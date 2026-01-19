"""Test Assessment Orchestrator"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from orchestrator import AssessmentOrchestrator
from config import RepositoryTool


class TestOrchestratorInitialization:
    """Test orchestrator initialization"""
    
    @patch('orchestrator.AzureOpenAIService')
    def test_init_github(self, mock_ai_service):
        """Test initializing orchestrator for GitHub"""
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        
        assert orchestrator.tool == RepositoryTool.GITHUB
        assert len(orchestrator.questions) > 0
        assert len(orchestrator.pillars) > 0
        assert orchestrator.question_scores == {}
    
    @patch('orchestrator.AzureOpenAIService')
    def test_init_gitlab(self, mock_ai_service):
        """Test initializing orchestrator for GitLab"""
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITLAB)
        
        assert orchestrator.tool == RepositoryTool.GITLAB
        assert len(orchestrator.questions) > 0
    
    @patch('orchestrator.AzureOpenAIService')
    def test_init_azure_devops(self, mock_ai_service):
        """Test initializing orchestrator for Azure DevOps"""
        orchestrator = AssessmentOrchestrator(RepositoryTool.AZURE_DEVOPS)
        
        assert orchestrator.tool == RepositoryTool.AZURE_DEVOPS
        assert len(orchestrator.questions) > 0
    
    @patch('orchestrator.AzureOpenAIService')
    def test_questions_have_importance(self, mock_ai_service):
        """Test that all questions have importance scores"""
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        
        # orchestrator.questions returns tuples: (pillar_id, question, pillar_name)
        for pillar_id, question, pillar_name in orchestrator.questions:
            assert hasattr(question, 'importance')
            assert 1 <= question.importance <= 10


class TestAnalyzeAnswer:
    """Test answer analysis"""
    
    @patch('orchestrator.AzureOpenAIService')
    @pytest.mark.asyncio
    async def test_analyze_answer_stores_analysis(self, mock_ai_service):
        """Test that answer analysis is stored"""
        mock_ai_service.return_value.analyze_answer = AsyncMock(return_value="yes")
        
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        question_id = "test_q1"
        
        result = await orchestrator.analyze_answer(
            question_id,
            "Is branch protection enabled?",
            "Yes, we have it enabled.",
            8.0
        )
        
        assert result == "yes"
        assert question_id in orchestrator.answer_analyses
    
    @patch('orchestrator.AzureOpenAIService')
    @pytest.mark.asyncio
    async def test_analyze_answer_calls_ai_service(self, mock_ai_service):
        """Test that AI service is called correctly"""
        mock_service_instance = MagicMock()
        mock_service_instance.analyze_answer = AsyncMock(return_value="yes")
        mock_ai_service.return_value = mock_service_instance
        
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        
        await orchestrator.analyze_answer(
            "q1",
            "Test question?",
            "Test answer",
            5.0
        )
        
        mock_service_instance.analyze_answer.assert_called_once()


class TestGenerateFinalSummary:
    """Test final summary generation"""
    
    @patch('orchestrator.AzureOpenAIService')
    @pytest.mark.asyncio
    async def test_generate_summary_with_answers(self, mock_ai_service):
        """Test generating summary with answers"""
        mock_service_instance = MagicMock()
        mock_service_instance.generate_comprehensive_summary = AsyncMock(
            return_value="Comprehensive assessment summary"
        )
        mock_ai_service.return_value = mock_service_instance
        
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        
        # Add some answer analyses
        orchestrator.answer_analyses["q1"] = "Good implementation"
        
        answers = {
            "q1": {
                "classification": "yes",
                "answer": "Yes, implemented",
                "score": 10.0
            }
        }
        
        summary = await orchestrator.generate_final_summary(answers)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    @patch('orchestrator.AzureOpenAIService')
    @pytest.mark.asyncio
    async def test_generate_summary_empty_answers(self, mock_ai_service):
        """Test generating summary with no answers"""
        mock_service_instance = MagicMock()
        mock_service_instance.generate_comprehensive_summary = AsyncMock(
            return_value="No answers provided"
        )
        mock_ai_service.return_value = mock_service_instance
        
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        
        summary = await orchestrator.generate_final_summary({})
        
        assert isinstance(summary, str)


class TestImportanceSummary:
    """Test importance distribution"""
    
    @patch('orchestrator.AzureOpenAIService')
    def test_importance_distribution(self, mock_ai_service):
        """Test that importance scores are distributed correctly"""
        orchestrator = AssessmentOrchestrator(RepositoryTool.GITHUB)
        
        # Count questions by importance tier
        critical = 0
        high = 0
        moderate = 0
        low = 0
        
        # orchestrator.questions returns tuples: (pillar_id, question, pillar_name)
        for pillar_id, question, pillar_name in orchestrator.questions:
            if question.importance >= 9:
                critical += 1
            elif question.importance >= 7:
                high += 1
            elif question.importance >= 4:
                moderate += 1
            else:
                low += 1
        
        # Should have questions in multiple tiers
        total = critical + high + moderate + low
        assert total == len(orchestrator.questions)
        assert critical > 0  # Should have some critical questions
