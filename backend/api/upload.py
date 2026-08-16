from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.services.candidate_service import CandidateService

router = APIRouter(prefix="/api/candidates", tags=["Upload"])

@router.post("/upload", status_code=202)
async def upload_cvs(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts single or multiple CV file uploads (PDF, DOCX, TXT).
    Validates file formats, stores files, and triggers background AI analysis.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded.")
        
    response_items = []
    
    for file in files:
        try:
            candidate_id = CandidateService.save_and_initiate_cv(db, file)
            # Schedule asynchronous background processing task
            background_tasks.add_task(CandidateService.process_candidate_cv, db, candidate_id)
            
            response_items.append({
                "candidate_id": candidate_id,
                "filename": file.filename,
                "status": "PROCESSING",
                "message": "File accepted and processing initiated."
            })
        except HTTPException as he:
            response_items.append({
                "filename": file.filename,
                "status": "REJECTED",
                "error": he.detail
            })
        except Exception as e:
            response_items.append({
                "filename": file.filename,
                "status": "FAILED",
                "error": str(e)
            })
            
    return {
        "total_uploaded": len(files),
        "results": response_items
    }
