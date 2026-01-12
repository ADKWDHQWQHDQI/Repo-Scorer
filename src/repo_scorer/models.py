"""Pydantic models for request/response validation"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class AnswerClassification(BaseModel):
    """Classification result from LLM"""

    classification: str = Field(..., pattern="^(yes|partial|no|unsure)$")
    confidence: Optional[str] = None


class QuestionResponse(BaseModel):
    """Response for a single question"""

    question_id: str
    question_text: str
    pillar_name: str
    max_score: float


class AnswerSubmission(BaseModel):
    """User's answer submission"""

    question_id: str
    answer: str


class QuestionResult(BaseModel):
    """Result after scoring a question"""

    question_id: str
    question_text: str
    user_answer: str
    classification: str
    score_earned: float
    max_score: float
    is_follow_up: bool = False
    base_question_id: Optional[str] = None


class AssessmentResult(BaseModel):
    """Final assessment result"""

    final_score: float
    breakdown: Dict[str, tuple[float, float]]  # pillar_name -> (earned, max)
    question_results: list[QuestionResult]
    summary: Optional[str] = None


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    ollama_connected: bool
    model_available: bool
    model_name: str
