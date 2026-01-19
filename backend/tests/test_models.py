"""Test Pydantic models"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import QuestionResult, AssessmentResult
from pydantic import ValidationError


class TestQuestionResult:
    """Test QuestionResult model"""
    
    def test_question_result_valid(self):
        """Test creating valid QuestionResult"""
        result = QuestionResult(
            question_id="q1",
            question_text="Is branch protection enabled?",
            user_answer="Yes, it is enabled",
            classification="yes",
            score_earned=10.0,
            max_score=10.0
        )
        
        assert result.question_id == "q1"
        assert result.classification == "yes"
        assert result.score_earned == 10.0
    
    def test_question_result_missing_field(self):
        """Test that missing required field raises error"""
        with pytest.raises(ValidationError):
            QuestionResult(
                question_id="q1",
                question_text="Test?",
                # Missing user_answer
                classification="yes",
                score_earned=10.0,
                max_score=10.0
            )
    
    def test_question_result_wrong_type(self):
        """Test that wrong type raises error"""
        with pytest.raises(ValidationError):
            QuestionResult(
                question_id="q1",
                question_text="Test?",
                user_answer="Yes",
                classification="yes",
                score_earned="ten",  # Should be float
                max_score=10.0
            )


class TestAssessmentResult:
    """Test AssessmentResult model"""
    
    def test_assessment_result_valid(self):
        """Test creating valid AssessmentResult"""
        question_results = [
            QuestionResult(
                question_id="q1",
                question_text="Test?",
                user_answer="Yes",
                classification="yes",
                score_earned=10.0,
                max_score=10.0
            )
        ]
        
        result = AssessmentResult(
            final_score=85.5,
            breakdown={
                "security": (20.0, 30.0)
            },
            question_results=question_results,
            summary="Good performance"
        )
        
        assert result.final_score == 85.5
        assert "security" in result.breakdown
        assert len(result.question_results) == 1
    
    def test_assessment_result_empty_breakdown(self):
        """Test AssessmentResult with empty breakdown"""
        result = AssessmentResult(
            final_score=0.0,
            breakdown={},
            question_results=[],
            summary="No answers"
        )
        
        assert result.final_score == 0.0
        assert len(result.breakdown) == 0
    
    def test_assessment_result_missing_summary(self):
        """Test that missing summary raises error"""
        with pytest.raises(ValidationError):
            AssessmentResult(
                final_score=85.5,
                breakdown={},
                question_results=[]
                # Missing summary
            )
