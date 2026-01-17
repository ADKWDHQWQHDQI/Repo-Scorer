"""Pydantic models for request/response validation"""

from typing import Dict
from pydantic import BaseModel


class QuestionResult(BaseModel):
    """Result after scoring a question"""

    question_id: str
    question_text: str
    user_answer: str
    classification: str
    score_earned: float
    max_score: float


class AssessmentResult(BaseModel):
    """Final assessment result"""

    final_score: float
    breakdown: Dict[str, tuple[float, float]]  # pillar_name -> (earned, max)
    question_results: list[QuestionResult]
    summary: str
