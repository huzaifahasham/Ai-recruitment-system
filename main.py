"""
main.py — FastAPI Application for Basic AI Recruitment System (3 AI Agents).
"""

import os
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import (
    init_db,
    get_all_candidates,
    get_candidate_by_id,
    get_interview_by_token,
    get_interview_by_candidate_id,
    get_all_email_logs
)
from agents.cv_agent import CVScreeningAgent
from agents.interview_agent import AIInterviewAgent
from agents.selection_agent import CandidateSelectionAgent
from email_service import send_interview_link_email

# Initialize database
init_db()

# Instantiate the 3 logical AI Agents
agent1_cv = CVScreeningAgent()
agent2_interview = AIInterviewAgent()
agent3_selection = CandidateSelectionAgent()

app = FastAPI(
    title="Basic AI Recruitment System",
    description="Student project demonstrating a 3-Agent AI recruitment workflow.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Upload directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
os.makedirs(frontend_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


# Pydantic Schemas
class InterviewSubmission(BaseModel):
    answers: list[str]


class SMTPConfigRequest(BaseModel):
    server: str
    port: int = 587
    user: str
    password: str


# Page Routes
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return "<h1>HR Dashboard HTML not found</h1>"


@app.get("/interview/{token}", response_class=HTMLResponse)
def serve_candidate_interview(token: str):
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return "<h1>Interview Portal HTML not found</h1>"


# SMTP Settings API
@app.get("/api/smtp-config")
def get_smtp_settings():
    from email_service import get_smtp_config
    return get_smtp_config()


@app.post("/api/smtp-config")
def set_smtp_settings(config: SMTPConfigRequest):
    from email_service import update_smtp_config
    update_smtp_config(config.server, config.port, config.user, config.password)
    return {"message": "SMTP Configuration updated successfully.", "server": config.server, "user": config.user}


# API Routes

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    candidates = get_all_candidates()
    total = len(candidates)
    pending = sum(1 for c in candidates if c["status"] in ["Pending", "Interview Generated", "Interview Sent"])
    passed = sum(1 for c in candidates if "Passed" in c["status"])
    failed = sum(1 for c in candidates if "Failed" in c["status"])

    return {
        "total": total,
        "pending": pending,
        "passed": passed,
        "failed": failed
    }


@app.get("/api/candidates")
def list_candidates():
    return get_all_candidates()


@app.get("/api/candidates/{candidate_id}")
def get_candidate_details(candidate_id: int):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    interview = get_interview_by_candidate_id(candidate_id)
    return {
        "candidate": candidate,
        "interview": interview
    }


# AGENT 1: CV Upload & Extraction
@app.post("/api/upload-cv")
async def upload_cv(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Trigger Agent 1
        candidate_info = agent1_cv.process_cv(file_path)
        return {
            "message": "CV uploaded and processed successfully by Agent 1",
            "candidate": candidate_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 1 CV screening error: {str(e)}")


# AGENT 2: Generate 10 Questions
@app.post("/api/candidates/{candidate_id}/generate-interview")
def generate_interview(candidate_id: int):
    try:
        result = agent2_interview.generate_interview(candidate_id)
        return {
            "message": "Interview generated successfully by Agent 2",
            "interview": result
        }
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 2 question generation error: {str(e)}")


# EMAIL 1: Send Interview Link to Candidate
@app.post("/api/candidates/{candidate_id}/send-interview-email")
def send_interview_link(candidate_id: int, request: Request):
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    interview = get_interview_by_candidate_id(candidate_id)
    if not interview:
        raise HTTPException(status_code=400, detail="Interview not generated yet. Please generate interview first.")

    host_url = str(request.base_url).rstrip("/")
    interview_link = f"{host_url}/#interview/{interview['token']}"

    email_res = send_interview_link_email(candidate_id, candidate["name"], candidate["email"], interview_link)
    
    # Update candidate status
    from database import update_candidate_status
    update_candidate_status(candidate_id, "Interview Sent")

    return {
        "message": "Interview link email dispatched successfully",
        "interview_link": interview_link,
        "email_details": email_res
    }


# AGENT 2 & 3: Candidate Submit Answers & AI Scoring Evaluation & Outcome
@app.get("/api/interview-data/{token}")
def get_interview_data(token: str):
    interview = get_interview_by_token(token)
    if not interview:
        raise HTTPException(status_code=404, detail="Invalid or expired interview link")
    return interview


@app.post("/api/interview/{token}/submit")
def submit_interview(token: str, payload: InterviewSubmission):
    if not payload.answers or len(payload.answers) == 0:
        raise HTTPException(status_code=400, detail="Please answer the interview questions.")

    try:
        # Step 1: Agent 2 evaluates answers and scores out of 100
        eval_result = agent2_interview.evaluate_answers(token, payload.answers)
        candidate_id = eval_result["candidate_id"]
        score = eval_result["score"]
        is_pass = (eval_result["status"] == "PASS")

        # Step 2: Agent 3 receives result, determines PASS/FAIL final status
        selection_result = agent3_selection.process_selection(candidate_id, score, is_pass)

        return {
            "message": "Interview submitted and evaluated successfully",
            "evaluation": eval_result,
            "selection": selection_result
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")


# AGENT 3: Send Final Email (for PASS candidates)
@app.post("/api/candidates/{candidate_id}/send-final-email")
def send_final_email(candidate_id: int):
    try:
        agent3_selection.dispatch_final_email(candidate_id)
        return {"message": "Final interview invitation email sent successfully."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email error: {str(e)}")


@app.get("/api/emails")
def list_email_logs():
    return get_all_email_logs()


# Demo Data Seeder for testing
@app.post("/api/demo/seed")
def seed_demo_data():
    from generate_sample_cvs import create_sample_pdf
    
    # Sample 1: Ali Khan
    p1 = create_sample_pdf(
        "ali_khan_cv.pdf", "Ali Khan", "ali@gmail.com", "0300-1234567",
        "BS Computer Science", "Python, SQL, Java", "1 Year", "AWS"
    )
    c1 = agent1_cv.process_cv(p1)

    # Sample 2: Sara Ahmed
    p2 = create_sample_pdf(
        "sara_ahmed_cv.pdf", "Sara Ahmed", "sara@gmail.com", "0312-9876543",
        "MS Data Science", "Python, Machine Learning, SQL", "2 Years", "TensorFlow Certified"
    )
    c2 = agent1_cv.process_cv(p2)

    return {
        "message": "Demo candidate CVs seeded and processed by Agent 1 successfully",
        "candidates": [c1, c2]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
