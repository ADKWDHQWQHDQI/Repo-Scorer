"""FastAPI application for repository scorer API"""

import sys
from pathlib import Path

# Add src directory to path so repo_scorer can be imported
src_path = Path(__file__).resolve().parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from fastapi import FastAPI, HTTPException
from typing import Dict, Optional

from repo_scorer.orchestrator import AssessmentOrchestrator
from repo_scorer.models import (
    QuestionResponse,
    AnswerSubmission,
    QuestionResult,
    AssessmentResult,
    HealthCheck,
)
from repo_scorer.config import RepositoryTool, get_questions_for_tool, get_all_questions

app = FastAPI(
    title="Repository Scorer API",
    description="Intelligent repository quality assessment powered by local LLM",
    version="0.1.0",
)

# Store orchestrators per session (in-memory, for demo)
sessions: Dict[str, AssessmentOrchestrator] = {}


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Repository Scorer API",
        "version": "0.1.0",
        "endpoints": {
            "health": "/health",
            "questions": "/questions",
            "start": "/start-assessment",
            "submit": "/submit-answer",
            "finalize": "/finalize-assessment/{session_id}",
        },
    }


@app.get("/health", response_model=HealthCheck, tags=["System"])
async def health_check():
    """Check system health and Ollama connectivity"""
    orchestrator = AssessmentOrchestrator(tool=RepositoryTool.GITHUB)

    ollama_connected, model_available = await orchestrator.ollama.check_health()

    return HealthCheck(
        status="healthy" if ollama_connected and model_available else "degraded",
        ollama_connected=ollama_connected,
        model_available=model_available,
        model_name=orchestrator.ollama.model,
    )


@app.get("/questions", response_model=list[QuestionResponse], tags=["Assessment"])
async def list_questions(tool: str = "github"):
    """Get all assessment questions for a specific tool"""
    try:
        repo_tool = RepositoryTool(tool.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tool. Must be one of: {', '.join([t.value for t in RepositoryTool])}"
        )
    
    pillars = get_questions_for_tool(repo_tool)
    questions = get_all_questions(pillars)
    return [
        QuestionResponse(
            question_id=q.id,
            question_text=q.text,
            pillar_name=pillar_name,
            max_score=q.max_score,
        )
        for _, q, pillar_name in questions
    ]


@app.post("/start-assessment", tags=["Assessment"])
async def start_assessment(tool: str, model: Optional[str] = None) -> dict:
    """Start a new assessment session"""
    import uuid
    
    # Validate tool
    try:
        repo_tool = RepositoryTool(tool.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tool. Must be one of: {', '.join([t.value for t in RepositoryTool])}"
        )

    session_id = str(uuid.uuid4())
    orchestrator = AssessmentOrchestrator(tool=repo_tool, model=model)

    # Check readiness
    is_ready, message = await orchestrator.check_readiness()
    if not is_ready:
        raise HTTPException(status_code=503, detail=message)

    sessions[session_id] = orchestrator

    return {
        "session_id": session_id,
        "tool": repo_tool.value,
        "model": orchestrator.ollama.model,
        "total_questions": len(orchestrator.questions),
        "message": "Assessment started. Submit answers to /submit-answer",
    }


@app.post(
    "/submit-answer",
    response_model=QuestionResult,
    tags=["Assessment"],
)
async def submit_answer(
    session_id: str, submission: AnswerSubmission
) -> QuestionResult:
    """Submit an answer for a question"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    orchestrator = sessions[session_id]

    try:
        result = await orchestrator.process_answer(
            submission.question_id, submission.answer
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {e}")


@app.post(
    "/finalize-assessment/{session_id}",
    response_model=AssessmentResult,
    tags=["Assessment"],
)
async def finalize_assessment(session_id: str) -> AssessmentResult:
    """Finalize assessment and get results"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    orchestrator = sessions[session_id]

    try:
        result = await orchestrator.finalize_assessment()

        # Clean up session
        del sessions[session_id]

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error finalizing assessment: {e}"
        )


@app.get("/pillars", tags=["Info"])
async def get_pillars():
    """Get information about scoring pillars"""
    # Get pillar information through the orchestrator
    orchestrator = AssessmentOrchestrator(tool=RepositoryTool.GITHUB)
    pillars = orchestrator.pillars
    return {
        pillar_id: {
            "name": pillar.name,
            "weight": pillar.total_weight,
            "num_questions": len(pillar.questions),
        }
        for pillar_id, pillar in pillars.items()
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
