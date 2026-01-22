"""
FastAPI Backend for DevSecOps Assessment
Exposes Python orchestrator as REST API for React frontend
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, field_validator
from typing import Dict, Optional
from contextlib import asynccontextmanager
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timedelta
from threading import Lock

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    try:
        init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.warning("⚠️  App will continue running, but database features may not work")
    
    # Start background cleanup task
    asyncio.create_task(periodic_cleanup_task())
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    global cleanup_task_running
    cleanup_task_running = False
    logger.info("Application shutting down")


app = FastAPI(
    title="DevSecOps Assessment API",
    description="DevSecOps Repository Assessment API powered by Azure OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://green-wave-03cc57a0f.1.azurestaticapps.net",
        "https://green-wave-03cc57a0f-preview.eastus2.1.azurestaticapps.net",
        "https://red-pebble-019922c00.6.azurestaticapps.net",
        "http://localhost:5173",  # Local development
        "http://localhost:3000"   # Alternative local port
    ],
    allow_credentials=False,
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


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "DevSecOps Assessment API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/health", response_model=HealthCheckResponse)
async def health_check():
    """Check if Azure OpenAI service is accessible"""
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
async def get_shared_results(share_token: str):
    """Retrieve assessment results by share token (public endpoint)"""
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
            
            return SaveEmailResponse(
                success=True,
                message="Email updated successfully",
                email=request.email
            )
        
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
        
        return SaveEmailResponse(
            success=True,
            message="Email saved successfully",
            email=request.email
        )
        
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
                    "pillar_name": question_pillar_name
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


# For local development only - Azure App Service will use uvicorn directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
