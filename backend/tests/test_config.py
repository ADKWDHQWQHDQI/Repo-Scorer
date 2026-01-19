"""Test configuration and questions"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    RepositoryTool,
    Question,
    Pillar,
    get_questions_for_tool,
    get_all_questions,
    GITHUB_QUESTIONS,
    GITLAB_QUESTIONS,
    AZURE_DEVOPS_QUESTIONS,
    PILLAR_METADATA
)


class TestRepositoryTool:
    """Test repository tool enum"""
    
    def test_repository_tool_values(self):
        """Test that repository tools have correct values"""
        assert RepositoryTool.GITHUB == "github"
        assert RepositoryTool.GITLAB == "gitlab"
        assert RepositoryTool.AZURE_DEVOPS == "azure_devops"


class TestQuestions:
    """Test question structure"""
    
    def test_github_questions_structure(self):
        """Test GitHub questions have correct structure"""
        assert len(GITHUB_QUESTIONS) > 0
        for question in GITHUB_QUESTIONS:
            assert len(question) == 3  # (text, importance, pillar)
            text, importance, pillar = question
            assert isinstance(text, str)
            assert isinstance(importance, float)
            assert isinstance(pillar, str)
            assert 1 <= importance <= 10
    
    def test_gitlab_questions_structure(self):
        """Test GitLab questions have correct structure"""
        assert len(GITLAB_QUESTIONS) > 0
        for question in GITLAB_QUESTIONS:
            assert len(question) == 3
    
    def test_azure_devops_questions_structure(self):
        """Test Azure DevOps questions have correct structure"""
        assert len(AZURE_DEVOPS_QUESTIONS) > 0
        for question in AZURE_DEVOPS_QUESTIONS:
            assert len(question) == 3
    
    def test_questions_have_valid_pillars(self):
        """Test all questions reference valid pillars"""
        valid_pillars = set(PILLAR_METADATA.keys())
        
        for questions in [GITHUB_QUESTIONS, GITLAB_QUESTIONS, AZURE_DEVOPS_QUESTIONS]:
            for text, importance, pillar in questions:
                assert pillar in valid_pillars, f"Invalid pillar: {pillar}"


class TestGetQuestionsForTool:
    """Test getting questions for specific tool"""
    
    def test_get_github_questions(self):
        """Test getting GitHub questions"""
        pillars = get_questions_for_tool(RepositoryTool.GITHUB)
        assert isinstance(pillars, dict)
        assert len(pillars) > 0
        
        # Check pillar structure
        for pillar_id, pillar in pillars.items():
            assert isinstance(pillar, Pillar)
            assert len(pillar.questions) > 0
    
    def test_get_gitlab_questions(self):
        """Test getting GitLab questions"""
        pillars = get_questions_for_tool(RepositoryTool.GITLAB)
        assert isinstance(pillars, dict)
        assert len(pillars) > 0
    
    def test_get_azure_devops_questions(self):
        """Test getting Azure DevOps questions"""
        pillars = get_questions_for_tool(RepositoryTool.AZURE_DEVOPS)
        assert isinstance(pillars, dict)
        assert len(pillars) > 0
    
    def test_questions_assigned_to_pillars(self):
        """Test that questions are correctly assigned to pillars"""
        pillars = get_questions_for_tool(RepositoryTool.GITHUB)
        
        total_questions = 0
        for pillar in pillars.values():
            for question in pillar.questions:
                assert isinstance(question, Question)
                assert question.pillar in pillars  # Pillar ID should be in pillars dict
                total_questions += 1
        
        assert total_questions == len(GITHUB_QUESTIONS)


class TestGetAllQuestions:
    """Test getting all questions from pillars"""
    
    def test_get_all_questions_github(self):
        """Test getting all GitHub questions"""
        pillars = get_questions_for_tool(RepositoryTool.GITHUB)
        all_questions = get_all_questions(pillars)
        
        assert len(all_questions) == len(GITHUB_QUESTIONS)
        # get_all_questions returns tuples: (pillar_id, question, pillar_name)
        for pillar_id, question, pillar_name in all_questions:
            assert isinstance(question, Question)
            assert isinstance(pillar_id, str)
            assert isinstance(pillar_name, str)
    
    def test_get_all_questions_gitlab(self):
        """Test getting all GitLab questions"""
        pillars = get_questions_for_tool(RepositoryTool.GITLAB)
        all_questions = get_all_questions(pillars)
        
        assert len(all_questions) == len(GITLAB_QUESTIONS)
    
    def test_get_all_questions_azure_devops(self):
        """Test getting all Azure DevOps questions"""
        pillars = get_questions_for_tool(RepositoryTool.AZURE_DEVOPS)
        all_questions = get_all_questions(pillars)
        
        assert len(all_questions) == len(AZURE_DEVOPS_QUESTIONS)


class TestPillarMetadata:
    """Test pillar metadata"""
    
    def test_pillar_metadata_structure(self):
        """Test pillar metadata has correct structure"""
        assert len(PILLAR_METADATA) > 0
        
        for pillar_id, metadata in PILLAR_METADATA.items():
            assert "name" in metadata
            assert "description" in metadata
            assert isinstance(metadata["name"], str)
            assert isinstance(metadata["description"], str)
    
    def test_required_pillars_exist(self):
        """Test that required pillars exist"""
        required_pillars = ["security", "governance", "code_review", 
                          "repository_management", "process_metrics"]
        
        for pillar in required_pillars:
            assert pillar in PILLAR_METADATA


class TestQuestionClass:
    """Test Question dataclass"""
    
    def test_question_creation(self):
        """Test creating a Question instance"""
        question = Question(
            id="q1",
            text="Is this a test?",
            max_score=10.0,
            importance=8.0,
            pillar="security"
        )
        
        assert question.id == "q1"
        assert question.text == "Is this a test?"
        assert question.max_score == 10.0
        assert question.importance == 8.0
        assert question.pillar == "security"


class TestPillarClass:
    """Test Pillar dataclass"""
    
    def test_pillar_creation(self):
        """Test creating a Pillar instance"""
        questions = [
            Question("q1", "Test?", 10.0, 8.0, "Security")
        ]
        
        pillar = Pillar(
            name="Security",
            total_weight=10.0,
            questions=questions
        )
        
        assert pillar.name == "Security"
        assert pillar.total_weight == 10.0
        assert len(pillar.questions) == 1


class TestImportanceScores:
    """Test importance score distribution"""
    
    def test_importance_range(self):
        """Test that all importance scores are in valid range"""
        all_questions = GITHUB_QUESTIONS + GITLAB_QUESTIONS + AZURE_DEVOPS_QUESTIONS
        
        for text, importance, pillar in all_questions:
            assert 1 <= importance <= 10, f"Invalid importance {importance} for: {text}"
    
    def test_has_critical_questions(self):
        """Test that each tool has critical questions (importance >= 9)"""
        for tool_questions in [GITHUB_QUESTIONS, GITLAB_QUESTIONS, AZURE_DEVOPS_QUESTIONS]:
            critical_count = sum(1 for _, imp, _ in tool_questions if imp >= 9)
            assert critical_count > 0, "Should have at least one critical question"
    
    def test_importance_distribution(self):
        """Test that importance scores are well distributed"""
        for tool_questions in [GITHUB_QUESTIONS, GITLAB_QUESTIONS, AZURE_DEVOPS_QUESTIONS]:
            importance_scores = [imp for _, imp, _ in tool_questions]
            
            # Should have variety in importance
            unique_scores = set(importance_scores)
            assert len(unique_scores) >= 5, "Should have diverse importance scores"
