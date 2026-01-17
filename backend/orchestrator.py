"""Main orchestrator for repository assessment"""

import asyncio
from typing import Dict, Optional

from azure_openai_service import AzureOpenAIService
from config import (
    RepositoryTool,
    get_questions_for_tool,
    get_all_questions,
)


class AssessmentOrchestrator:
    """Orchestrates the assessment flow"""

    def __init__(self, tool: RepositoryTool, api_key: Optional[str] = None):
        self.tool = tool
        self.ai_service = AzureOpenAIService(api_key=api_key)
        self.question_scores: Dict[str, float] = {}
        self.answer_analyses: Dict[str, str] = {}  # Store LLM analysis for each answer
        
        # Load predefined questions for the selected tool
        # Questions now have manual importance scores from config
        self.pillars = get_questions_for_tool(tool)
        self.questions = get_all_questions(self.pillars)
        
        print(f"\n📋 Loaded {len(self.questions)} questions with manual importance scores")
        self._display_importance_summary()
    
    def _display_importance_summary(self) -> None:
        """Display summary of importance scores distribution"""
        all_questions = []
        for pillar_id, pillar in self.pillars.items():
            for question in pillar.questions:
                all_questions.append(question)
        
        if not all_questions:
            return
        
        # Count by importance tier
        critical = sum(1 for q in all_questions if q.importance >= 9)
        high = sum(1 for q in all_questions if 7 <= q.importance < 9)
        moderate = sum(1 for q in all_questions if 4 <= q.importance < 7)
        low = sum(1 for q in all_questions if q.importance < 4)
        
        print(f"   Critical (9-10): {critical} questions")
        print(f"   High (7-8): {high} questions")
        print(f"   Moderate (4-6): {moderate} questions")
        print(f"   Low (1-3): {low} questions")
        print()
    
    async def analyze_answer(self, question_id: str, question_text: str, 
                           answer: str, importance: float) -> str:
        """
        Analyze an individual answer using LLM and store the analysis
        
        Args:
            question_id: Question identifier
            question_text: The question text
            answer: User's answer
            importance: Importance score of the question
            
        Returns:
            LLM analysis of the answer
        """
        analysis = await self.ai_service.analyze_answer(question_text, answer, importance)
        self.answer_analyses[question_id] = analysis
        return analysis
    
    async def generate_final_summary(self, answers: Dict[str, Dict]) -> str:
        """
        Generate comprehensive final summary based on all answers
        
        Args:
            answers: Dictionary of question_id -> {classification, answer, score, ...}
            
        Returns:
            Professional summary with strengths and recommendations
        """
        # Separate YES and NO answers with their analyses
        yes_answers = []
        no_answers = []
        
        for pillar_id, pillar in self.pillars.items():
            for question in pillar.questions:
                if question.id in answers:
                    answer_data = answers[question.id]
                    analysis = self.answer_analyses.get(question.id, "No analysis available")
                    
                    answer_tuple = (
                        question.text,
                        answer_data.get("answer", ""),
                        question.importance,
                        analysis
                    )
                    
                    if answer_data["classification"] == "yes":
                        yes_answers.append(answer_tuple)
                    else:
                        no_answers.append(answer_tuple)
        
        # Sort by importance (highest first)
        yes_answers.sort(key=lambda x: x[2], reverse=True)
        no_answers.sort(key=lambda x: x[2], reverse=True)
        
        # Calculate final score
        final_score = sum(self.question_scores.values())
        
        # Generate summary using Azure OpenAI
        summary = await self.ai_service.generate_comprehensive_summary(
            yes_answers=yes_answers,
            no_answers=no_answers,
            total_score=final_score
        )
        
        return summary

    async def check_readiness(self) -> tuple[bool, str]:
        """
        Check if system is ready to run assessment

        Returns:
            (is_ready, message)
        """
        service_connected, deployment_available = await self.ai_service.check_health()

        if not service_connected:
            return False, "Cannot connect to Azure OpenAI service."

        if not deployment_available:
            return (
                False,
                f"Azure OpenAI deployment '{self.ai_service.deployment}' not accessible.",
            )
        
        print("\n✅ System ready - Azure OpenAI connected\n")
        return True, "Azure OpenAI service ready"
