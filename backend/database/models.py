from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from backend.database.database import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(255), default="Not Provided")
    email = Column(String(255), default="Not Provided")
    phone = Column(String(100), default="Not Provided")
    location = Column(String(255), default="Not Provided")
    years_of_experience = Column(Float, default=0.0)
    
    cv_filename = Column(String(255), nullable=False)
    cv_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    
    status = Column(String(50), default="UPLOADED", index=True)  # UPLOADED, PROCESSING, PROCESSED, FAILED
    error_message = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    education = relationship("CandidateEducation", back_populates="candidate", cascade="all, delete-orphan")
    skills = relationship("CandidateSkill", back_populates="candidate", cascade="all, delete-orphan")
    experience = relationship("CandidateExperience", back_populates="candidate", cascade="all, delete-orphan")
    projects = relationship("CandidateProject", back_populates="candidate", cascade="all, delete-orphan")
    certifications = relationship("CandidateCertification", back_populates="candidate", cascade="all, delete-orphan")
    domain_classification = relationship("DomainClassification", back_populates="candidate", uselist=False, cascade="all, delete-orphan")
    screening_result = relationship("ScreeningResult", back_populates="candidate", uselist=False, cascade="all, delete-orphan")


class CandidateEducation(Base):
    __tablename__ = "candidate_education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id"), nullable=False)
    degree = Column(String(255), default="Not Provided")
    institution = Column(String(255), default="Not Provided")
    field_of_study = Column(String(255), default="Not Provided")
    year = Column(String(100), default="Not Provided")

    candidate = relationship("Candidate", back_populates="education")


class CandidateSkill(Base):
    __tablename__ = "candidate_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    category = Column(String(100), default="General")  # Skill, Language, Framework, Tool

    candidate = relationship("Candidate", back_populates="skills")


class CandidateExperience(Base):
    __tablename__ = "candidate_experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id"), nullable=False)
    company = Column(String(255), default="Not Provided")
    role = Column(String(255), default="Not Provided")
    duration = Column(String(100), default="Not Provided")
    description = Column(Text, default="Not Provided")
    is_internship = Column(Integer, default=0)

    candidate = relationship("Candidate", back_populates="experience")


class CandidateProject(Base):
    __tablename__ = "candidate_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id"), nullable=False)
    title = Column(String(255), default="Not Provided")
    description = Column(Text, default="Not Provided")
    technologies = Column(Text, default="Not Provided")

    candidate = relationship("Candidate", back_populates="projects")


class CandidateCertification(Base):
    __tablename__ = "candidate_certifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id"), nullable=False)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), default="Not Provided")

    candidate = relationship("Candidate", back_populates="certifications")


class DomainClassification(Base):
    __tablename__ = "domain_classification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id"), nullable=False, unique=True)
    primary_domain = Column(String(255), nullable=False, index=True)
    primary_confidence = Column(Float, nullable=False)
    secondary_domains = Column(JSON, nullable=False)  # List of {"domain": str, "confidence": float}
    evidence = Column(JSON, nullable=False)  # List of string evidence bullet points

    candidate = relationship("Candidate", back_populates="domain_classification")


class ScreeningResult(Base):
    __tablename__ = "screening_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    candidate_id = Column(String(50), ForeignKey("candidates.id"), nullable=False, unique=True)
    screening_score = Column(Integer, nullable=False)  # 0 to 100
    recommendation = Column(String(100), nullable=False, index=True)  # Strong Match, Potential Match, Needs HR Review, Low Match
    summary = Column(Text, nullable=False)
    score_breakdown = Column(JSON, nullable=True)  # Detailed breakdown per criteria
    created_at = Column(DateTime, default=datetime.utcnow)

    candidate = relationship("Candidate", back_populates="screening_result")
