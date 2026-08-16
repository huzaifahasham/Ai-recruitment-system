from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, desc
from backend.database.models import (
    Candidate, CandidateEducation, CandidateSkill, CandidateExperience,
    CandidateProject, CandidateCertification, DomainClassification, ScreeningResult
)

class CandidateRepository:
    @staticmethod
    def create_candidate(db: Session, candidate_data: dict) -> Candidate:
        candidate = Candidate(**candidate_data)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return candidate

    @staticmethod
    def get_by_id(db: Session, candidate_id: str) -> Optional[Candidate]:
        return db.query(Candidate).filter(Candidate.id == candidate_id).first()

    @staticmethod
    def update_status(db: Session, candidate_id: str, status: str, error_message: Optional[str] = None):
        candidate = CandidateRepository.get_by_id(db, candidate_id)
        if candidate:
            candidate.status = status
            if error_message:
                candidate.error_message = error_message
            db.commit()
            db.refresh(candidate)
        return candidate

    @staticmethod
    def save_analysis_results(
        db: Session,
        candidate_id: str,
        extracted_info: dict,
        domain_info: dict,
        screening_info: dict
    ) -> Candidate:
        candidate = CandidateRepository.get_by_id(db, candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        # Update candidate base details
        candidate.name = extracted_info.get("candidate_name", "Not Provided")
        candidate.email = extracted_info.get("email", "Not Provided")
        candidate.phone = extracted_info.get("phone", "Not Provided")
        candidate.location = extracted_info.get("location", "Not Provided")
        candidate.years_of_experience = float(extracted_info.get("years_of_experience", 0.0))
        candidate.status = "PROCESSED"
        candidate.error_message = None

        # Clean existing nested collections
        db.query(CandidateEducation).filter(CandidateEducation.candidate_id == candidate_id).delete()
        db.query(CandidateSkill).filter(CandidateSkill.candidate_id == candidate_id).delete()
        db.query(CandidateExperience).filter(CandidateExperience.candidate_id == candidate_id).delete()
        db.query(CandidateProject).filter(CandidateProject.candidate_id == candidate_id).delete()
        db.query(CandidateCertification).filter(CandidateCertification.candidate_id == candidate_id).delete()
        db.query(DomainClassification).filter(DomainClassification.candidate_id == candidate_id).delete()
        db.query(ScreeningResult).filter(ScreeningResult.candidate_id == candidate_id).delete()

        # Save Education
        for edu in extracted_info.get("education", []):
            if isinstance(edu, dict):
                db.add(CandidateEducation(
                    candidate_id=candidate_id,
                    degree=edu.get("degree", "Not Provided"),
                    institution=edu.get("institution", "Not Provided"),
                    field_of_study=edu.get("field_of_study", "Not Provided"),
                    year=edu.get("year", "Not Provided")
                ))
            elif isinstance(edu, str):
                db.add(CandidateEducation(
                    candidate_id=candidate_id,
                    degree=edu,
                    institution="Not Provided",
                    field_of_study="Not Provided",
                    year="Not Provided"
                ))

        # Save Skills
        for skill in extracted_info.get("skills", []):
            db.add(CandidateSkill(candidate_id=candidate_id, skill_name=skill, category="Skill"))
        for lang in extracted_info.get("programming_languages", []):
            db.add(CandidateSkill(candidate_id=candidate_id, skill_name=lang, category="Language"))
        for tool in extracted_info.get("frameworks_tools", []):
            db.add(CandidateSkill(candidate_id=candidate_id, skill_name=tool, category="Tool"))

        # Save Experience
        for exp in extracted_info.get("work_experience", []):
            if isinstance(exp, dict):
                db.add(CandidateExperience(
                    candidate_id=candidate_id,
                    company=exp.get("company", "Not Provided"),
                    role=exp.get("role", "Not Provided"),
                    duration=exp.get("duration", "Not Provided"),
                    description=exp.get("description", "Not Provided"),
                    is_internship=0
                ))
        for exp in extracted_info.get("internships", []):
            if isinstance(exp, dict):
                db.add(CandidateExperience(
                    candidate_id=candidate_id,
                    company=exp.get("company", "Not Provided"),
                    role=exp.get("role", "Not Provided"),
                    duration=exp.get("duration", "Not Provided"),
                    description=exp.get("description", "Not Provided"),
                    is_internship=1
                ))

        # Save Projects
        for proj in extracted_info.get("projects", []):
            if isinstance(proj, dict):
                db.add(CandidateProject(
                    candidate_id=candidate_id,
                    title=proj.get("title", proj.get("name", "Not Provided")),
                    description=proj.get("description", "Not Provided"),
                    technologies=proj.get("technologies", "Not Provided")
                ))
            elif isinstance(proj, str):
                db.add(CandidateProject(
                    candidate_id=candidate_id,
                    title=proj,
                    description="Not Provided",
                    technologies="Not Provided"
                ))

        # Save Certifications
        for cert in extracted_info.get("certifications", []):
            if isinstance(cert, dict):
                db.add(CandidateCertification(
                    candidate_id=candidate_id,
                    title=cert.get("title", cert.get("name", "Not Provided")),
                    issuer=cert.get("issuer", "Not Provided")
                ))
            elif isinstance(cert, str):
                db.add(CandidateCertification(
                    candidate_id=candidate_id,
                    title=cert,
                    issuer="Not Provided"
                ))

        # Save Domain Classification
        db.add(DomainClassification(
            candidate_id=candidate_id,
            primary_domain=domain_info.get("primary_domain", "Other"),
            primary_confidence=float(domain_info.get("confidence", 0.0)),
            secondary_domains=domain_info.get("secondary_domains", []),
            evidence=domain_info.get("evidence", [])
        ))

        # Save Screening Result
        db.add(ScreeningResult(
            candidate_id=candidate_id,
            screening_score=int(screening_info.get("score", 0)),
            recommendation=screening_info.get("recommendation", "Needs HR Review"),
            summary=screening_info.get("summary", ""),
            score_breakdown=screening_info.get("score_breakdown", {})
        ))

        db.commit()
        db.refresh(candidate)
        return candidate

    @staticmethod
    def get_candidates(
        db: Session,
        search: Optional[str] = None,
        domain: Optional[str] = None,
        recommendation: Optional[str] = None,
        status: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Candidate]:
        query = db.query(Candidate).outerjoin(DomainClassification).outerjoin(ScreeningResult)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Candidate.name.ilike(search_pattern),
                    Candidate.email.ilike(search_pattern),
                    Candidate.cv_filename.ilike(search_pattern)
                )
            )

        if domain:
            query = query.filter(DomainClassification.primary_domain == domain)

        if recommendation:
            query = query.filter(ScreeningResult.recommendation == recommendation)

        if status:
            query = query.filter(Candidate.status == status)

        if min_score is not None:
            query = query.filter(ScreeningResult.screening_score >= min_score)

        if max_score is not None:
            query = query.filter(ScreeningResult.screening_score <= max_score)

        return query.order_by(desc(Candidate.created_at)).offset(skip).limit(limit).all()

    @staticmethod
    def get_dashboard_stats(db: Session) -> Dict[str, Any]:
        total_cvs = db.query(Candidate).count()
        processed = db.query(Candidate).filter(Candidate.status == "PROCESSED").count()
        pending = db.query(Candidate).filter(Candidate.status.in_(["UPLOADED", "PROCESSING"])).count()
        failed = db.query(Candidate).filter(Candidate.status == "FAILED").count()

        strong_matches = db.query(ScreeningResult).filter(ScreeningResult.recommendation == "Strong Match").count()
        potential_matches = db.query(ScreeningResult).filter(ScreeningResult.recommendation == "Potential Match").count()
        needs_review = db.query(ScreeningResult).filter(ScreeningResult.recommendation == "Needs HR Review").count()
        low_matches = db.query(ScreeningResult).filter(ScreeningResult.recommendation == "Low Match").count()

        return {
            "total_cvs": total_cvs,
            "processed": processed,
            "pending": pending,
            "failed": failed,
            "strong_matches": strong_matches,
            "potential_matches": potential_matches,
            "needs_review": needs_review,
            "low_matches": low_matches
        }

    @staticmethod
    def get_domain_stats(db: Session) -> List[Dict[str, Any]]:
        results = db.query(
            DomainClassification.primary_domain,
            func.count(DomainClassification.candidate_id).label("count"),
            func.avg(DomainClassification.primary_confidence).label("avg_confidence")
        ).group_by(DomainClassification.primary_domain).all()

        return [
            {
                "domain": row.primary_domain,
                "count": row.count,
                "avg_confidence": round(float(row.avg_confidence), 1) if row.avg_confidence else 0.0
            }
            for row in results
        ]
