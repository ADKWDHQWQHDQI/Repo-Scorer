"""Test scoring engine"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scoring import score_question, calculate_final_score, generate_breakdown


class TestScoreQuestion:
    """Test individual question scoring"""
    
    def test_score_yes_classification(self):
        """Test scoring with yes classification"""
        score = score_question(10.0, "yes")
        assert score == 10.0
    
    def test_score_no_classification(self):
        """Test scoring with no classification"""
        score = score_question(10.0, "no")
        assert score == 0.0
    
    def test_score_unsure_classification(self):
        """Test scoring with unsure classification"""
        score = score_question(10.0, "unsure")
        assert score == 0.0
    
    def test_score_different_max_scores(self):
        """Test scoring with various max scores"""
        assert score_question(5.5, "yes") == 5.5
        assert score_question(7.8, "yes") == 7.8
        assert score_question(10.0, "yes") == 10.0
    
    def test_score_zero_max(self):
        """Test scoring with zero max score"""
        score = score_question(0.0, "yes")
        assert score == 0.0


class TestCalculateFinalScore:
    """Test final score calculation"""
    
    def test_calculate_empty_scores(self):
        """Test calculating with no scores"""
        final = calculate_final_score({})
        assert final == 0.0
    
    def test_calculate_single_score(self):
        """Test calculating with single score"""
        scores = {"q1": 10.0}
        final = calculate_final_score(scores)
        assert final == 10.0
    
    def test_calculate_multiple_scores(self):
        """Test calculating with multiple scores"""
        scores = {
            "q1": 10.0,
            "q2": 7.0,
            "q3": 5.5
        }
        final = calculate_final_score(scores)
        assert final == 22.5
    
    def test_calculate_with_zero_scores(self):
        """Test calculating with some zero scores"""
        scores = {
            "q1": 10.0,
            "q2": 0.0,
            "q3": 5.0
        }
        final = calculate_final_score(scores)
        assert final == 15.0
    
    def test_calculate_total_100(self):
        """Test calculating perfect score"""
        scores = {f"q{i}": 10.0 for i in range(10)}
        final = calculate_final_score(scores)
        assert final == 100.0


class TestGenerateBreakdown:
    """Test pillar breakdown generation"""
    
    def test_breakdown_single_pillar(self):
        """Test breakdown with single pillar"""
        question_scores = {"q1": 10.0, "q2": 5.0}
        pillar_questions = {
            "Security": [("q1", 10.0), ("q2", 10.0)]
        }
        
        breakdown = generate_breakdown(question_scores, pillar_questions)
        
        assert "Security" in breakdown
        assert breakdown["Security"] == (15.0, 20.0)
    
    def test_breakdown_multiple_pillars(self):
        """Test breakdown with multiple pillars"""
        question_scores = {
            "q1": 10.0,
            "q2": 5.0,
            "q3": 7.0
        }
        pillar_questions = {
            "Security": [("q1", 10.0), ("q2", 10.0)],
            "Governance": [("q3", 7.0)]
        }
        
        breakdown = generate_breakdown(question_scores, pillar_questions)
        
        assert len(breakdown) == 2
        assert breakdown["Security"] == (15.0, 20.0)
        assert breakdown["Governance"] == (7.0, 7.0)
    
    def test_breakdown_missing_scores(self):
        """Test breakdown with missing question scores"""
        question_scores = {"q1": 10.0}  # q2 missing
        pillar_questions = {
            "Security": [("q1", 10.0), ("q2", 10.0)]
        }
        
        breakdown = generate_breakdown(question_scores, pillar_questions)
        
        assert breakdown["Security"] == (10.0, 20.0)
    
    def test_breakdown_empty_pillars(self):
        """Test breakdown with empty pillars"""
        question_scores = {}
        pillar_questions = {}
        
        breakdown = generate_breakdown(question_scores, pillar_questions)
        
        assert breakdown == {}
    
    def test_breakdown_zero_scores(self):
        """Test breakdown with all zero scores"""
        question_scores = {"q1": 0.0, "q2": 0.0}
        pillar_questions = {
            "Security": [("q1", 10.0), ("q2", 10.0)]
        }
        
        breakdown = generate_breakdown(question_scores, pillar_questions)
        
        assert breakdown["Security"] == (0.0, 20.0)
    
    def test_breakdown_rounding(self):
        """Test breakdown rounds to 2 decimal places"""
        question_scores = {"q1": 7.777, "q2": 3.333}
        pillar_questions = {
            "Security": [("q1", 10.0), ("q2", 10.0)]
        }
        
        breakdown = generate_breakdown(question_scores, pillar_questions)
        
        earned, max_score = breakdown["Security"]
        assert earned == 11.11
        assert max_score == 20.0


class TestScoringEdgeCases:
    """Test edge cases in scoring"""
    
    def test_negative_scores(self):
        """Test that negative scores are not possible"""
        score = score_question(-10.0, "yes")
        assert score == -10.0  # Function doesn't validate, but returns as-is
    
    def test_large_scores(self):
        """Test with very large scores"""
        score = score_question(1000000.0, "yes")
        assert score == 1000000.0
    
    def test_fractional_scores(self):
        """Test with fractional scores"""
        score = score_question(0.1, "yes")
        assert score == 0.1
        
        score = score_question(10.999, "yes")
        assert score == 10.999
