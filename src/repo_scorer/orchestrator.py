"""Main orchestrator for repository assessment"""

import asyncio
from typing import Dict, Optional

from repo_scorer.services.ollama_service import OllamaService
from repo_scorer.config import (
    RepositoryTool,
    get_questions_for_tool,
    get_all_questions,
)


class AssessmentOrchestrator:
    """Orchestrates the assessment flow"""

    def __init__(self, tool: RepositoryTool, model: Optional[str] = None):
        self.tool = tool
        self.ollama = OllamaService(model=model)
        self.question_scores: Dict[str, float] = {}
        self.scored_questions: set = set()  # Track which questions have been scored
        
        # Load predefined questions for the selected tool
        self.pillars = get_questions_for_tool(tool)
        self.questions = get_all_questions(self.pillars)
    
    async def score_question_importance(self, question_id: str) -> float:
        """
        Score importance for a single question on-demand with detailed logging
        
        Args:
            question_id: ID of the question to score
            
        Returns:
            Importance score (1-10)
        """
        # Check if already scored
        if question_id in self.scored_questions:
            # Find the question to get its current importance
            for pillar_id, pillar in self.pillars.items():
                for question in pillar.questions:
                    if question.id == question_id:
                        print(f"   ℹ️  Using cached importance score: {question.importance}/10")
                        return question.importance
        
        # Find the question
        question_obj = None
        for pillar_id, pillar in self.pillars.items():
            for question in pillar.questions:
                if question.id == question_id:
                    question_obj = question
                    break
            if question_obj:
                break
        
        if not question_obj:
            print(f"   ⚠️  Question {question_id} not found")
            return 6.0
        
        print(f"\n🔍 Scoring Question Importance...")
        print(f"   Question: {question_obj.text[:80]}..." if len(question_obj.text) > 80 else f"   Question: {question_obj.text}")
        print(f"   Current max score: {question_obj.max_score} points")
        
        # Default score based on question position (varied distribution)
        default_scores = [7.0, 8.0, 6.0, 9.0, 5.0, 7.5, 6.5, 8.5, 4.0, 7.0, 6.0, 8.0, 5.5, 7.5, 6.5]
        question_index = len(self.scored_questions)
        default_score = default_scores[question_index] if question_index < len(default_scores) else 6.0
        
        # Score with LLM
        importance = await self.ollama.score_question_importance(
            question_obj.text, 
            default_score=default_score
        )
        
        # Update the question's importance
        question_obj.importance = importance
        
        # Mark as scored
        self.scored_questions.add(question_id)
        
        # IMMEDIATELY recalculate max_scores for all questions based on current importance values
        # This ensures the display always shows LLM-calculated weights, not hardcoded values
        self._recalculate_max_scores()
        
        print(f"   ✅ Importance Score: {importance}/10")
        print(f"   Updated max score: {question_obj.max_score:.2f} points\n")
        
        return importance
    
    def _recalculate_max_scores(self) -> None:
        """
        Recalculate max_scores for all questions based on their importance weights.
        This is called after each question importance is scored to keep distribution current.
        
        For questions not yet scored:
        - If no questions scored yet: use equal distribution (100/total)
        - If some scored: unscored questions get average importance of scored ones
        """
        all_questions = []
        scored_questions = []
        unscored_questions = []
        
        # Collect questions and categorize by scoring status
        for pillar_id, pillar in self.pillars.items():
            for question in pillar.questions:
                all_questions.append(question)
                if question.id in self.scored_questions:
                    scored_questions.append(question)
                else:
                    unscored_questions.append(question)
        
        if not scored_questions:
            # No questions scored yet - use equal distribution
            points_per_question = 100.0 / len(all_questions)
            for question in all_questions:
                question.max_score = points_per_question
        else:
            # Some questions are scored
            # For unscored questions, estimate importance as average of scored questions
            avg_importance = sum(q.importance for q in scored_questions) / len(scored_questions)
            for question in unscored_questions:
                question.importance = avg_importance
            
            # Now distribute 100 points proportionally based on all importance values
            total_importance = sum(q.importance for q in all_questions)
            
            if total_importance > 0:
                for question in all_questions:
                    question.max_score = (question.importance / total_importance) * 100.0
            else:
                # Fallback: equal distribution
                points_per_question = 100.0 / len(all_questions)
                for question in all_questions:
                    question.max_score = points_per_question
        
        # Refresh questions list
        self.questions = get_all_questions(self.pillars)
        
        print(f"   📊 Recalculated scores - {len(scored_questions)}/{len(all_questions)} questions scored")
    
    def normalize_question_scores(self) -> None:
        """
        Final normalization of question max_scores (called at assessment completion).
        By this point, all questions should have their importance scored.
        """
        # Just call the internal recalculation method
        self._recalculate_max_scores()
        
        # Collect all questions for summary
        all_questions = []
        total_importance = 0.0
        
        for pillar_id, pillar in self.pillars.items():
            for question in pillar.questions:
                all_questions.append(question)
                total_importance += question.importance
        
        print("\n📊 Final Score Normalization Complete")
        print(f"   Total importance: {total_importance:.2f}")
        print(f"   Points distributed: 100.0")
        print(f"   Questions: {len(all_questions)}\n")

    async def check_readiness(self) -> tuple[bool, str]:
        """
        Check if system is ready to run assessment

        Returns:
            (is_ready, message)
        """
        ollama_connected, model_available = await self.ollama.check_health()

        if not ollama_connected:
            return False, "Cannot connect to Ollama. Is it running?"

        if not model_available:
            return (
                False,
                f"Model '{self.ollama.model}' not found. Run: ollama pull {self.ollama.model}",
            )
        
        print("\n✅ System ready - questions will be scored as you progress through the assessment\n")
        return True, "System ready"
