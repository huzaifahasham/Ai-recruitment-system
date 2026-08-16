from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.repositories import CandidateRepository
from backend.schemas.candidate import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    """
    Returns aggregate stats: Total CVs, Processed, Pending, Failed,
    Strong Matches, Potential Matches, Needs Review, Low Matches.
    """
    stats = CandidateRepository.get_dashboard_stats(db)
    return DashboardStatsResponse(**stats)
