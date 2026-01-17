"""Scoring engine - deterministic score calculation"""

from typing import Dict


def score_question(max_score: float, classification: str) -> float:
    """
    Calculate score for a question based on classification

    Args:
        max_score: Maximum possible score for the question
        classification: Answer classification (yes/no)

    Returns:
        Calculated score (full points for yes, 0 for no)
    """
    return max_score if classification == "yes" else 0.0


def calculate_final_score(question_scores: Dict[str, float]) -> float:
    """
    Calculate total score from all question scores

    Args:
        question_scores: Dictionary of question_id -> earned_score

    Returns:
        Total score out of 100
    """
    return sum(question_scores.values())


def generate_breakdown(
    question_scores: Dict[str, float], pillar_questions: Dict[str, list]
) -> Dict[str, tuple[float, float]]:
    """
    Generate pillar-wise breakdown with earned and max scores

    Args:
        question_scores: Dictionary of question_id -> earned_score
        pillar_questions: Dictionary of pillar_id -> list of (question_id, max_score) tuples

    Returns:
        Dictionary of pillar_name -> (earned_score, max_score)
    """
    breakdown = {}
    for pillar_name, question_data in pillar_questions.items():
        earned = sum(question_scores.get(qid, 0.0) for qid, _ in question_data)
        max_total = sum(max_score for _, max_score in question_data)
        breakdown[pillar_name] = (round(earned, 2), round(max_total, 2))
    return breakdown

