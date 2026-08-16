from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.repositories import CandidateRepository
from backend.ai.fallback_engine import DOMAINS_TAXONOMY
from backend.schemas.candidate import DomainStatItem

router = APIRouter(prefix="/api/domains", tags=["Domains"])

@router.get("", response_model=List[DomainStatItem])
def get_supported_domains_with_stats(db: Session = Depends(get_db)):
    """
    Returns supported domain list along with candidate count and average confidence.
    """
    db_stats = CandidateRepository.get_domain_stats(db)
    stats_dict = {item["domain"]: item for item in db_stats}
    
    result = []
    for domain_name in DOMAINS_TAXONOMY:
        if domain_name in stats_dict:
            result.append(DomainStatItem(**stats_dict[domain_name]))
        else:
            result.append(DomainStatItem(domain=domain_name, count=0, avg_confidence=0.0))
            
    return result
