import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.config import settings
from backend.database.database import init_db
from backend.utils.logging import setup_logging
from backend.api import upload, candidates, dashboard, domains

# Setup Logging
setup_logging()
logger = logging.getLogger("main")

# Initialize Database tables
init_db()

app = FastAPI(
    title=settings.APP_NAME,
    description="Agent 1 — AI CV Screening & Domain Classification Module API",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(upload.router)
app.include_router(candidates.router)
app.include_router(dashboard.router)
app.include_router(domains.router)

# Mount static frontend assets
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_index():
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend index.html not found"}

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "ai_provider": settings.AI_PROVIDER,
        "agent": "Agent 1 — CV Screening & Domain Classification"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
