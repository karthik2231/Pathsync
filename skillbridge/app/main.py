from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db, engine, Base
from app.routers import auth, candidates, employers, jobs, matching, recommendations

# Initializes the FastAPI app instance
app = FastAPI(
    title="SkillBridge API",
    description="AI-powered Skill Gap Analyzer and Talent Matching Platform",
    version="1.0.0"
)

# JWT Auth Middleware & CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include structured routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(candidates.router, prefix="/candidates", tags=["Candidates"])
app.include_router(employers.router, prefix="/employers", tags=["Employers"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(matching.router, prefix="/match", tags=["Matching"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])

@app.get("/health", tags=["System"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint. Confirms API and Database connectivity.
    """
    try:
        # Check DB connection using mapped execution
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db_connected": True}
    except Exception as e:
        return {"status": "error", "db_connected": False, "details": str(e)}

@app.get("/")
def read_root():
    return {"message": "SkillBridge API is running. Access /docs for Swagger documentation."}
