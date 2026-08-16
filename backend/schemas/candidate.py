from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field

class EducationItem(BaseModel):
    degree: str = "Not Provided"
    institution: str = "Not Provided"
    field_of_study: str = "Not Provided"
    year: str = "Not Provided"

class SkillItem(BaseModel):
    skill_name: str
    category: str = "General"

class ExperienceItem(BaseModel):
    company: str = "Not Provided"
    role: str = "Not Provided"
    duration: str = "Not Provided"
    description: str = "Not Provided"
    is_internship: bool = False

class ProjectItem(BaseModel):
    title: str = "Not Provided"
    description: str = "Not Provided"
    technologies: str = "Not Provided"

class CertificationItem(BaseModel):
    title: str
    issuer: str = "Not Provided"

class SecondaryDomainItem(BaseModel):
    domain: str
    confidence: float

class DomainClassificationResponse(BaseModel):
    primary_domain: str
    primary_confidence: float
    secondary_domains: List[SecondaryDomainItem] = []
    evidence: List[str] = []

class ScreeningResultResponse(BaseModel):
    screening_score: int
    recommendation: str
    summary: str
    score_breakdown: Optional[Dict[str, Any]] = None

class CandidateSummaryResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    location: str
    years_of_experience: float
    cv_filename: str
    file_type: str
    file_size_bytes: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    primary_domain: Optional[str] = None
    primary_confidence: Optional[float] = None
    screening_score: Optional[int] = None
    recommendation: Optional[str] = None

class CandidateDetailResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    location: str
    years_of_experience: float
    cv_filename: str
    cv_path: str
    file_type: str
    file_size_bytes: int
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    education: List[EducationItem] = []
    skills: List[SkillItem] = []
    experience: List[ExperienceItem] = []
    projects: List[ProjectItem] = []
    certifications: List[CertificationItem] = []
    domain_classification: Optional[DomainClassificationResponse] = None
    screening_result: Optional[ScreeningResultResponse] = None

class DashboardStatsResponse(BaseModel):
    total_cvs: int
    processed: int
    pending: int
    failed: int
    strong_matches: int
    potential_matches: int
    needs_review: int
    low_matches: int

class DomainStatItem(BaseModel):
    domain: str
    count: int
    avg_confidence: float

class Agent1ExportResponse(BaseModel):
    candidate_id: str
    candidate_name: str
    email: str
    primary_domain: str
    domain_confidence: float
    skills: List[str]
    screening_score: int
    recommendation: str
