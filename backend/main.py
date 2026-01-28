"""
FastAPI Backend for DevSecOps Maturity Assessment
Exposes Python orchestrator as REST API for React frontend
Serves React static files at root path
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from typing import Dict, Optional
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timedelta
from threading import Lock
import base64
import urllib.parse
import os
from pathlib import Path

# Import modules (now in backend root)
from orchestrator import AssessmentOrchestrator
from config import RepositoryTool, CICDPlatform, DeploymentPlatform, get_questions_for_tool
from models import QuestionResult, AssessmentResult
from database import get_db, UserEmail, AssessmentRecord, init_db
from email_service import get_email_service
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db_background():
    """Initialize database in background - non-blocking"""
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("⚠️  App will continue running, but database features may not work")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup - run DB init in background to avoid blocking probes
    asyncio.create_task(asyncio.to_thread(init_db_background))
    
    # Start background cleanup task
    asyncio.create_task(periodic_cleanup_task())
    logger.info("✅ Application startup complete - background init running")
    
    yield
    
    # Shutdown
    global cleanup_task_running
    cleanup_task_running = False
    logger.info("Application shutting down")


app = FastAPI(
    title="DevSecOps Maturity Assessment API",
    description="DevSecOps Repository Assessment API powered by Azure OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:8000",  # Backend serving frontend
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for assessment sessions (use Redis in production)
# Structure: {session_id: {"orchestrator": AssessmentOrchestrator, "created_at": datetime, "last_accessed": datetime}}
assessment_sessions: Dict[str, dict] = {}
session_lock = Lock()

# In-memory cache for shared results (expires after 48 hours)
# Structure: {share_token: {"results": dict, "expires_at": datetime, "email": str, "platform": str}}
shared_results_cache: Dict[str, dict] = {}
cache_lock = Lock()

# Cache and session cleanup intervals
CACHE_EXPIRY_HOURS = 48
SESSION_EXPIRY_HOURS = 2
CLEANUP_INTERVAL_MINUTES = 30

# Background cleanup task flag
cleanup_task_running = False

# Personal email domains to block
PERSONAL_EMAIL_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'aol.com', 'icloud.com', 'mail.com', 'protonmail.com',
    'zoho.com', 'yandex.com', 'gmx.com', 'live.com',
    'msn.com', 'rediffmail.com', 'inbox.com','test.com','test123.com',
    'example.com','example.org','example.net','testxyz.com', 'myemail.com',
    'email.com','xyz.com','abc.com','demo.com','sample.com', 'tempmail.com',
    'disposablemail.com','fakeemail.com','mailinator.com','throwawaymail.com',
    '10minutemail.com','guerrillamail.com','maildrop.cc','getnada.com',
    'trashmail.com','yopmail.com'
]


# Request/Response Models
class StartAssessmentRequest(BaseModel):
    tool: str  # "github", "gitlab", "azure_devops", "bitbucket"
    cicd_platform: Optional[str] = None  # "github_actions", "azure_pipelines", "gitlab_ci", "jenkins", "circleci"
    deployment_platform: Optional[str] = None  # "azure", "aws", "gcp", "on_premise", "kubernetes"


class StartAssessmentResponse(BaseModel):
    session_id: str
    questions: list
    pillars: dict
    message: str


class SaveEmailRequest(BaseModel):
    email: EmailStr
    repository_platform: Optional[str] = None
    cicd_platform: Optional[str] = None
    deployment_platform: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_work_email(cls, v: str) -> str:
        """Validate that email is not from personal domains"""
        domain = v.split('@')[1].lower()
        if domain in PERSONAL_EMAIL_DOMAINS:
            raise ValueError(
                f'Personal email domains are not allowed. Please use your work email address.'
            )
        return v


class SaveEmailResponse(BaseModel):
    success: bool
    message: str
    email: str


class SubmitAnswerRequest(BaseModel):
    session_id: str
    question_id: str
    question_text: str
    answer: str
    importance: float


class SubmitAnswerResponse(BaseModel):
    classification: str
    score: float
    analysis: str


class CompleteAssessmentRequest(BaseModel):
    session_id: str
    tool: str
    answers: Dict[str, dict]
    email: str


class HealthCheckResponse(BaseModel):
    status: str
    service_connected: bool
    deployment_available: bool
    message: str


# Helper function to cleanup expired cache entries
def _cleanup_expired_cache():
    """Remove expired entries from shared results cache"""
    now = datetime.utcnow()
    expired_tokens = [
        token for token, data in shared_results_cache.items()
        if data["expires_at"] < now
    ]
    for token in expired_tokens:
        shared_results_cache.pop(token, None)
    
    if expired_tokens:
        logger.info(f"Cleaned up {len(expired_tokens)} expired cache entries")

def _cleanup_expired_sessions():
    """Remove expired assessment sessions"""
    now = datetime.utcnow()
    expiry_threshold = now - timedelta(hours=SESSION_EXPIRY_HOURS)
    
    with session_lock:
        expired_sessions = [
            session_id for session_id, data in assessment_sessions.items()
            if data["last_accessed"] < expiry_threshold
        ]
        for session_id in expired_sessions:
            assessment_sessions.pop(session_id, None)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired assessment sessions")

async def periodic_cleanup_task():
    """Background task to periodically clean up expired sessions and cache"""
    global cleanup_task_running
    cleanup_task_running = True
    
    logger.info("Background cleanup task started")
    
    try:
        while cleanup_task_running:
            await asyncio.sleep(CLEANUP_INTERVAL_MINUTES * 60)  # Convert minutes to seconds
            
            try:
                _cleanup_expired_sessions()
                _cleanup_expired_cache()
                logger.info("Periodic cleanup completed successfully")
            except Exception as e:
                logger.error(f"Error during periodic cleanup: {e}")
    except asyncio.CancelledError:
        logger.info("Background cleanup task cancelled")
    finally:
        cleanup_task_running = False


@app.get("/healthz")
async def healthz():
    """Fast health check for Azure App Service probes - no dependencies"""
    return {"status": "ok"}


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Detailed health check - checks Azure OpenAI service accessibility"""
    try:
        # Create a temporary orchestrator to check health
        temp_orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        is_ready, message = await temp_orchestrator.check_readiness()
        
        return HealthCheckResponse(
            status="healthy" if is_ready else "unhealthy",
            service_connected=is_ready,
            deployment_available=is_ready,
            message=message
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            service_connected=False,
            deployment_available=False,
            message=f"Error: {str(e)}"
        )


@app.get("/api/results/shared/{share_token}")
async def get_shared_results(
    share_token: str,
    email: Optional[str] = Query(None, description="Encoded email for click tracking"),
    db: Session = Depends(get_db)
):
    """Retrieve assessment results by share token (public endpoint) and track email clicks"""
    try:
        # Clean up expired entries first
        _cleanup_expired_cache()
        
        # Check if token exists in cache
        if share_token not in shared_results_cache:
            raise HTTPException(
                status_code=404, 
                detail="Results not found or have expired. Shared links are valid for 48 hours."
            )
        
        cached_data = shared_results_cache[share_token]
        
        # Check if expired
        if cached_data["expires_at"] < datetime.utcnow():
            # Remove expired entry
            shared_results_cache.pop(share_token, None)
            raise HTTPException(
                status_code=404,
                detail="Results have expired. Shared links are valid for 48 hours."
            )
        
        # Track email click if email parameter is provided
        if email:
            try:
                # Decode the email
                decoded_email = base64.urlsafe_b64decode(urllib.parse.unquote(email)).decode()
                logger.info(f"Tracking report view for email: {decoded_email}")
                
                # Update user_emails record to mark report as viewed
                user_email = db.query(UserEmail).filter(UserEmail.email == decoded_email).first()
                if user_email and not user_email.report_viewed:
                    user_email.report_viewed = True
                    user_email.viewed_at = datetime.utcnow()
                    db.commit()
                    logger.info(f"✅ Marked report as viewed for: {decoded_email}")
                elif user_email and user_email.report_viewed:
                    logger.info(f"ℹ️ Report already marked as viewed for: {decoded_email}")
            except Exception as e:
                logger.warning(f"Failed to track email click: {e}")
                # Don't fail the request if tracking fails
        
        # Return results with metadata
        return {
            "results": cached_data["results"],
            "platform": cached_data["platform"],
            "email": cached_data["email"],
            "expires_at": cached_data["expires_at"].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving results: {str(e)}")


@app.options("/api/results/shared/{share_token}")
async def options_shared_results(share_token: str):
    """Handle CORS preflight for shared results endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
        }
    )


# Add OPTIONS handler for CORS preflight
@app.options("/api/email/save")
async def options_email_save():
    """Handle CORS preflight for email save endpoint"""
    print("OPTIONS /api/email/save called")  # Debug log
    return JSONResponse(
        status_code=200,
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
        }
    )


@app.post("/api/email/save", response_model=SaveEmailResponse)
async def save_email(request: SaveEmailRequest, db: Session = Depends(get_db)):
    """Save user email to database with platform selections"""
    try:
        print(f"Received email save request: {request.email}")  # Debug log
        # Check if email already exists
        existing_email = db.query(UserEmail).filter(UserEmail.email == request.email).first()
        
        if existing_email:
            # Update platform selections if provided
            if request.repository_platform:
                setattr(existing_email, 'repository_platform', request.repository_platform)
            if request.cicd_platform:
                setattr(existing_email, 'cicd_platform', request.cicd_platform)
            if request.deployment_platform:
                setattr(existing_email, 'deployment_platform', request.deployment_platform)
            
            db.commit()
            
            response = SaveEmailResponse(
                success=True,
                message="Email updated successfully",
                email=request.email
            )
            print(f"Returning response: {response.model_dump()}")  # Debug log
            return response
        
        # Create new email record
        new_email = UserEmail(
            email=request.email,
            repository_platform=request.repository_platform,
            cicd_platform=request.cicd_platform,
            deployment_platform=request.deployment_platform
        )
        
        db.add(new_email)
        db.commit()
        db.refresh(new_email)
        
        response = SaveEmailResponse(
            success=True,
            message="Email saved successfully",
            email=request.email
        )
        print(f"Returning response: {response.model_dump()}")  # Debug log
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.options("/api/assessment/start")
async def options_assessment_start():
    """Handle CORS preflight for assessment start endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
        }
    )


@app.post("/api/assessment/start", response_model=StartAssessmentResponse)
async def start_assessment(request: StartAssessmentRequest):
    """Initialize a new assessment session"""
    try:
        # Validate tool
        tool = RepositoryTool(request.tool)
        
        # Validate optional platforms
        cicd_platform = CICDPlatform(request.cicd_platform) if request.cicd_platform else None
        deployment_platform = DeploymentPlatform(request.deployment_platform) if request.deployment_platform else None
        
        # Create orchestrator with platform selections
        orchestrator = AssessmentOrchestrator(
            tool=tool,
            cicd_platform=cicd_platform,
            deployment_platform=deployment_platform
        )
        
        # Check readiness
        is_ready, message = await orchestrator.check_readiness()
        if not is_ready:
            raise HTTPException(status_code=503, detail=message)
        
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Store session with timestamps
        with session_lock:
            assessment_sessions[session_id] = {
                "orchestrator": orchestrator,
                "created_at": now,
                "last_accessed": now
            }
        
        # Prepare questions
        questions = []
        for pillar_id, question_obj, pillar_name in orchestrator.questions:
            questions.append({
                "id": question_obj.id,
                "text": question_obj.text,
                "max_score": question_obj.max_score,
                "importance": question_obj.importance,
                "pillar": pillar_name,
                "pillar_id": pillar_id,
                "description": question_obj.description,
                "doc_url": question_obj.doc_url
            })
        
        # Prepare pillars
        pillars = {}
        for pillar_id, pillar in orchestrator.pillars.items():
            pillars[pillar_id] = {
                "id": pillar_id,
                "name": pillar.name,
                "total_weight": pillar.total_weight,
                "question_count": len(pillar.questions)
            }
        
        # Cleanup expired sessions periodically
        _cleanup_expired_sessions()
        
        return StartAssessmentResponse(
            session_id=session_id,
            questions=questions,
            pillars=pillars,
            message="Assessment started successfully"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid tool: {request.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.options("/api/assessment/answer")
async def options_assessment_answer():
    """Handle CORS preflight for assessment answer endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
        }
    )


@app.post("/api/assessment/answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """Analyze a single answer using AI"""
    try:
        # Get session and update last accessed time
        with session_lock:
            session_data = assessment_sessions.get(request.session_id)
            if not session_data:
                raise HTTPException(status_code=404, detail="Assessment session not found or expired")
            
            session_data["last_accessed"] = datetime.utcnow()
            orchestrator = session_data["orchestrator"]
        
        # Find the question object to get its max_score (properly weighted)
        question_obj = None
        for pillar_id, q, pillar_name in orchestrator.questions:
            if q.id == request.question_id:
                question_obj = q
                break
        
        if not question_obj:
            raise HTTPException(status_code=404, detail="Question not found in assessment")
        
        # Analyze answer
        analysis = await orchestrator.analyze_answer(
            request.question_id,
            request.question_text,
            request.answer,
            request.importance
        )
        
        # Determine classification and score using the question's max_score (not importance!)
        classification = "yes" if request.answer.lower().strip() in ["yes", "y"] else "no"
        score = question_obj.max_score if classification == "yes" else 0.0
        
        # Store score
        orchestrator.question_scores[request.question_id] = score
        
        return SubmitAnswerResponse(
            classification=classification,
            score=score,
            analysis=analysis
        )
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.options("/api/assessment/complete")
async def options_assessment_complete():
    """Handle CORS preflight for assessment complete endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept, Origin, X-Requested-With",
        }
    )


@app.post("/api/assessment/complete", response_model=dict)
async def complete_assessment(request: CompleteAssessmentRequest, db: Session = Depends(get_db)):
    """Complete assessment and generate final results"""
    try:
        # Get session
        with session_lock:
            session_data = assessment_sessions.get(request.session_id)
            if not session_data:
                raise HTTPException(status_code=404, detail="Assessment session not found or expired")
            
            orchestrator = session_data["orchestrator"]
        
        tool = RepositoryTool(request.tool)
        
        # Generate final summary
        summary = await orchestrator.generate_final_summary(request.answers)
        
        # Calculate breakdown by pillar
        breakdown = {}
        for pillar_id, pillar in orchestrator.pillars.items():
            earned = sum(
                orchestrator.question_scores.get(q.id, 0.0)
                for q in pillar.questions
            )
            max_score = sum(q.max_score for q in pillar.questions)
            percentage = (earned / max_score * 100) if max_score > 0 else 0
            
            breakdown[pillar_id] = {
                "id": pillar_id,
                "name": pillar.name,
                "earned": round(earned, 2),
                "max": round(max_score, 2),
                "percentage": round(percentage, 2)
            }
        
        # Prepare question results with pillar information
        question_results = []
        for question_id, answer_data in request.answers.items():
            # Find question details
            question_obj = None
            question_pillar_id = None
            question_pillar_name = None
            for pillar_id, q, pillar_name in orchestrator.questions:
                if q.id == question_id:
                    question_obj = q
                    question_pillar_id = pillar_id
                    question_pillar_name = pillar_name
                    break
            
            if question_obj:
                question_results.append({
                    "question_id": question_id,
                    "question_text": question_obj.text,
                    "user_answer": answer_data.get("answer", ""),
                    "classification": answer_data.get("classification", "no"),
                    "score_earned": answer_data.get("score", 0.0),
                    "max_score": question_obj.max_score,
                    "analysis": answer_data.get("analysis", ""),
                    "pillar_id": question_pillar_id,
                    "pillar_name": question_pillar_name,
                    "description": question_obj.description,
                    "doc_url": question_obj.doc_url
                })
        
        # Calculate final score
        final_score = sum(orchestrator.question_scores.values())
        
        results = {
            "final_score": round(final_score, 2),
            "breakdown": breakdown,
            "question_results": question_results,
            "summary": summary
        }
        
        # Generate unique share token
        share_token = str(uuid.uuid4())
        
        # Store results in memory cache with expiration
        with cache_lock:
            shared_results_cache[share_token] = {
                "results": results,
                "expires_at": datetime.utcnow() + timedelta(hours=CACHE_EXPIRY_HOURS),
                "email": request.email,
                "platform": request.tool
            }
        
        # Clean up expired entries
        _cleanup_expired_cache()
        
        # Send email with results
        email_service = get_email_service()
        email_success, email_message = await email_service.send_assessment_email(
            recipient_email=request.email,
            platform=request.tool,
            score=final_score,
            ai_summary=summary,
            share_token=share_token
        )
        
        if not email_success:
            logger.warning(f"Failed to send email: {email_message}")
            # Continue anyway - user can still access results if they saved the token
        else:
            logger.info(f"Email sent successfully to {request.email}")
        
        # Don't save full assessment results to database - only email already stored
        # We're keeping results in memory cache only
        
        # Clean up session and expired sessions
        with session_lock:
            assessment_sessions.pop(request.session_id, None)
        _cleanup_expired_sessions()
        
        return {
            "results": results,
            "share_token": share_token,
            "email_sent": email_success,
            "email_message": email_message if not email_success else "Email sent successfully"
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid tool: {request.tool}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files for React frontend from wwwroot folder
# Try multiple paths for compatibility
wwwroot_dir = Path(__file__).parent / "wwwroot"
if not wwwroot_dir.exists():
    # Fallback for Azure App Service
    wwwroot_dir = Path("/home/site/wwwroot")
if not wwwroot_dir.exists():
    # Fallback for current working directory
    wwwroot_dir = Path(os.getcwd()) / "backend" / "wwwroot"

logger.info(f"WWWRoot directory: {wwwroot_dir}, exists: {wwwroot_dir.exists()}")

# Serve frontend static files from wwwroot
if wwwroot_dir.exists():
    # Mount assets folder for JS/CSS files with proper caching headers
    assets_dir = wwwroot_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
        logger.info(f"Mounted /assets from {assets_dir}")
    
    # Serve index.html at root
    @app.get("/")
    async def serve_root():
        """Serve the React app's index.html at root path"""
        index_file = wwwroot_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
        raise HTTPException(status_code=404, detail="Frontend not found - please build the React app first")
    
    # Serve index.html for all non-API routes (SPA routing)
    # This must be the LAST route defined
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Catch-all route to serve React app for client-side routing"""
        # Don't intercept API routes
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Don't intercept assets
        if full_path.startswith("assets/"):
            raise HTTPException(status_code=404, detail="Asset not found")
        
        # Don't intercept docs
        if full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Serve index.html for all other routes (React Router handles client-side routing)
        index_file = wwwroot_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")
        raise HTTPException(status_code=404, detail="Frontend not found - please build the React app first")
else:
    logger.warning(f"WWWRoot directory not found at {wwwroot_dir}. Static files will not be served. Run 'npm run build:prod' in frontend folder.")

