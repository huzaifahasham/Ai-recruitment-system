import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.repositories import CandidateRepository
from backend.schemas.candidate import (
    CandidateSummaryResponse,
    CandidateDetailResponse,
    Agent1ExportResponse,
    ScreeningResultResponse
)

router = APIRouter(prefix="/api/candidates", tags=["Candidates"])

@router.get("", response_model=List[CandidateSummaryResponse])
def get_candidates(
    search: Optional[str] = Query(None, description="Search by name, email, or filename"),
    domain: Optional[str] = Query(None, description="Filter by primary domain"),
    recommendation: Optional[str] = Query(None, description="Filter by HR recommendation"),
    status: Optional[str] = Query(None, description="Filter by status (UPLOADED, PROCESSING, PROCESSED, FAILED)"),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    max_score: Optional[int] = Query(None, ge=0, le=100),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    candidates = CandidateRepository.get_candidates(
        db=db,
        search=search,
        domain=domain,
        recommendation=recommendation,
        status=status,
        min_score=min_score,
        max_score=max_score,
        skip=skip,
        limit=limit
    )
    
    response = []
    for c in candidates:
        domain_name = c.domain_classification.primary_domain if c.domain_classification else None
        confidence = c.domain_classification.primary_confidence if c.domain_classification else None
        score = c.screening_result.screening_score if c.screening_result else None
        rec = c.screening_result.recommendation if c.screening_result else None
        
        response.append(CandidateSummaryResponse(
            id=c.id,
            name=c.name,
            email=c.email,
            phone=c.phone,
            location=c.location,
            years_of_experience=c.years_of_experience,
            cv_filename=c.cv_filename,
            file_type=c.file_type,
            file_size_bytes=c.file_size_bytes,
            status=c.status,
            error_message=c.error_message,
            created_at=c.created_at,
            primary_domain=domain_name,
            primary_confidence=confidence,
            screening_score=score,
            recommendation=rec
        ))
        
    return response


@router.get("/{candidate_id}", response_model=CandidateDetailResponse)
def get_candidate_detail(candidate_id: str, db: Session = Depends(get_db)):
    candidate = CandidateRepository.get_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    return CandidateDetailResponse(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        location=candidate.location,
        years_of_experience=candidate.years_of_experience,
        cv_filename=candidate.cv_filename,
        cv_path=candidate.cv_path,
        file_type=candidate.file_type,
        file_size_bytes=candidate.file_size_bytes,
        status=candidate.status,
        error_message=candidate.error_message,
        created_at=candidate.created_at,
        education=[
            {
                "degree": e.degree,
                "institution": e.institution,
                "field_of_study": e.field_of_study,
                "year": e.year
            } for e in candidate.education
        ],
        skills=[
            {
                "skill_name": s.skill_name,
                "category": s.category
            } for s in candidate.skills
        ],
        experience=[
            {
                "company": ex.company,
                "role": ex.role,
                "duration": ex.duration,
                "description": ex.description,
                "is_internship": bool(ex.is_internship)
            } for ex in candidate.experience
        ],
        projects=[
            {
                "title": p.title,
                "description": p.description,
                "technologies": p.technologies
            } for p in candidate.projects
        ],
        certifications=[
            {
                "title": cert.title,
                "issuer": cert.issuer
            } for cert in candidate.certifications
        ],
        domain_classification={
            "primary_domain": candidate.domain_classification.primary_domain,
            "primary_confidence": candidate.domain_classification.primary_confidence,
            "secondary_domains": candidate.domain_classification.secondary_domains,
            "evidence": candidate.domain_classification.evidence
        } if candidate.domain_classification else None,
        screening_result={
            "screening_score": candidate.screening_result.screening_score,
            "recommendation": candidate.screening_result.recommendation,
            "summary": candidate.screening_result.summary,
            "score_breakdown": candidate.screening_result.score_breakdown
        } if candidate.screening_result else None
    )


@router.get("/{candidate_id}/screening", response_model=ScreeningResultResponse)
def get_candidate_screening(candidate_id: str, db: Session = Depends(get_db)):
    candidate = CandidateRepository.get_by_id(db, candidate_id)
    if not candidate or not candidate.screening_result:
        raise HTTPException(status_code=404, detail="Screening result not available for this candidate.")
    
    return ScreeningResultResponse(
        screening_score=candidate.screening_result.screening_score,
        recommendation=candidate.screening_result.recommendation,
        summary=candidate.screening_result.summary,
        score_breakdown=candidate.screening_result.score_breakdown
    )


@router.get("/{candidate_id}/agent1-export", response_model=Agent1ExportResponse)
def export_candidate_for_agent2(candidate_id: str, db: Session = Depends(get_db)):
    """
    Exposes clean candidate profile export for downstream Agent 2 integration.
    """
    candidate = CandidateRepository.get_by_id(db, candidate_id)
    if not candidate or candidate.status != "PROCESSED":
        raise HTTPException(status_code=400, detail="Candidate not processed or ready for Agent 2 consumption.")
        
    skills_list = [s.skill_name for s in candidate.skills]
    
    return Agent1ExportResponse(
        candidate_id=candidate.id,
        candidate_name=candidate.name,
        email=candidate.email,
        primary_domain=candidate.domain_classification.primary_domain if candidate.domain_classification else "Other",
        domain_confidence=candidate.domain_classification.primary_confidence if candidate.domain_classification else 0.0,
        skills=skills_list,
        screening_score=candidate.screening_result.screening_score if candidate.screening_result else 0,
        recommendation=candidate.screening_result.recommendation if candidate.screening_result else "Needs HR Review"
    )


@router.get("/{candidate_id}/cv")
def download_candidate_cv(candidate_id: str, db: Session = Depends(get_db)):
    candidate = CandidateRepository.get_by_id(db, candidate_id)
    if not candidate or not os.path.exists(candidate.cv_path):
        raise HTTPException(status_code=404, detail="Original CV file not found.")
        
    return FileResponse(
        path=candidate.cv_path,
        filename=candidate.cv_filename,
        media_type="application/octet-stream"
    )
