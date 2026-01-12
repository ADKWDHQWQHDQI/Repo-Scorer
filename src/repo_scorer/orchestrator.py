"""Main orchestrator for repository assessment"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from repo_scorer.services.ollama_service import OllamaService
from repo_scorer.config import (
    RepositoryTool,
    get_questions_for_tool,
    get_all_questions,
    get_follow_up_questions,
    ANSWER_MAPPING,
)
from repo_scorer.scoring import score_question, calculate_final_score, generate_breakdown
from repo_scorer.models import QuestionResult, AssessmentResult


class AssessmentOrchestrator:
    """Orchestrates the assessment flow"""

    def __init__(self, tool: RepositoryTool, model: Optional[str] = None):
        self.tool = tool
        self.ollama = OllamaService(model=model)
        self.question_scores: Dict[str, float] = {}
        self.question_results: List[QuestionResult] = []
        self.current_question_index = 0
        self.pending_follow_ups: List[tuple] = []  # Queue of follow-up questions
        self.importance_weights_assigned = False
        
        # Load predefined questions for the selected tool
        self.pillars = get_questions_for_tool(tool)
        self.questions = get_all_questions(self.pillars)

    async def assign_importance_weights(self) -> None:
        """
        Use LLM to assign importance weights to all questions
        
        This evaluates each question and assigns a weight (1-10) based on
        how critical that governance practice is for repository health.
        Then redistributes the 100 points proportionally based on importance.
        """
        if self.importance_weights_assigned:
            return
        
        print("\n🤖 AI is evaluating question importance...")
        
        # Score all questions in parallel for efficiency
        all_questions_flat = []
        for pillar_id, pillar in self.pillars.items():
            for question in pillar.questions:
                all_questions_flat.append((pillar_id, question))
        
        # Score questions (with some batching to avoid overwhelming the LLM)
        importance_tasks = [
            self.ollama.score_question_importance(q.text)
            for _, q in all_questions_flat
        ]
        
        importances = await asyncio.gather(*importance_tasks)
        
        # Assign importance scores to questions
        for (pillar_id, question), importance in zip(all_questions_flat, importances):
            question.importance = importance
        
        # Recalculate max_scores based on importance weights
        for pillar_id, pillar in self.pillars.items():
            total_importance = sum(q.importance for q in pillar.questions)
            
            # Redistribute pillar's total weight (100 points) based on importance
            for question in pillar.questions:
                # Weight proportional to importance
                question.max_score = round(
                    (question.importance / total_importance) * pillar.total_weight, 2
                )
            
            # Adjust last question to ensure total is exactly pillar.total_weight
            actual_total = sum(q.max_score for q in pillar.questions)
            if abs(actual_total - pillar.total_weight) > 0.01:
                pillar.questions[-1].max_score = round(
                    pillar.questions[-1].max_score + (pillar.total_weight - actual_total), 2
                )
        
        # Refresh questions list
        self.questions = get_all_questions(self.pillars)
        self.importance_weights_assigned = True
        
        print("✓ Question importance weights assigned\n")
    
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
        
        # Assign importance weights to questions using LLM
        if not self.importance_weights_assigned:
            await self.assign_importance_weights()

        return True, "System ready"

    async def process_answer(
        self, question_id: str, user_answer: str
    ) -> QuestionResult:
        """
        Process a single answer

        Args:
            question_id: ID of the question
            user_answer: User's natural language answer

        Returns:
            QuestionResult with classification and score
        """
        # Find the question
        question_data = None
        pillar_id = None
        pillar_name = None
        is_follow_up = "_followup_" in question_id

        # First check in base questions
        for pid, q, pname in self.questions:
            if q.id == question_id:
                question_data = q
                pillar_id = pid
                pillar_name = pname
                break

        # If not found and it's a follow-up, check pending follow-ups
        if not question_data and is_follow_up:
            for pid, fq, pname in self.pending_follow_ups:
                if fq.id == question_id:
                    # Convert FollowUpQuestion to Question for processing
                    from repo_scorer.config import Question
                    question_data = Question(
                        id=fq.id,
                        text=fq.text,
                        max_score=fq.max_score
                    )
                    pillar_id = pid
                    pillar_name = pname
                    break
        
        # Also check if it's a follow-up that was already processed (in pending but being processed now)
        if not question_data and is_follow_up:
            # Check all possible follow-up questions from config
            base_question_id = question_id.split("_followup_")[0]
            classification = None  # We don't know the classification yet
            
            # Get all potential follow-ups for the base question
            all_follow_ups = get_follow_up_questions(base_question_id, "partial")  # Check partial
            all_follow_ups.extend(get_follow_up_questions(base_question_id, "no"))  # Check no
            
            for fq in all_follow_ups:
                if fq.id == question_id:
                    from repo_scorer.config import Question
                    question_data = Question(
                        id=fq.id,
                        text=fq.text,
                        max_score=fq.max_score
                    )
                    # Find the pillar from the base question
                    base_question_id = fq.base_question_id
                    for pid, q, pname in self.questions:
                        if q.id == base_question_id:
                            pillar_id = pid
                            pillar_name = pname
                            break
                    break

        if not question_data:
            raise ValueError(f"Question {question_id} not found")

        # Classify answer using LLM
        classification = await self.ollama.classify_answer(
            question_data.text, user_answer
        )

        # Calculate score deterministically
        earned_score = score_question(question_data.max_score, classification)

        # Store score
        self.question_scores[question_id] = earned_score

        # Create result
        result = QuestionResult(
            question_id=question_id,
            question_text=question_data.text,
            user_answer=user_answer,
            classification=classification,
            score_earned=round(earned_score, 2),
            max_score=question_data.max_score,
            is_follow_up=is_follow_up,
            base_question_id=question_id.split("_followup_")[0] if is_follow_up else None,
        )

        self.question_results.append(result)
        
        # AI-driven adaptive questioning: Check if follow-up questions should be triggered
        if not is_follow_up:  # Only trigger follow-ups for base questions
            follow_ups = get_follow_up_questions(question_id, classification)
            
            for follow_up in follow_ups:
                # AI decides if this follow-up is relevant
                should_ask = await self.ollama.decide_follow_up(
                    question_data.text,
                    user_answer,
                    classification,
                    follow_up.text
                )
                
                if should_ask:
                    # Add to pending follow-ups queue
                    self.pending_follow_ups.append((pillar_id, follow_up, pillar_name))
        
        return result

    async def run_full_assessment(
        self, answers: Dict[str, str]
    ) -> AssessmentResult:
        """
        Run full assessment with all answers at once

        Args:
            answers: Dictionary of question_id -> user_answer

        Returns:
            Complete assessment result
        """
        # Process all answers
        for question_id, user_answer in answers.items():
            await self.process_answer(question_id, user_answer)

        return await self.finalize_assessment()

    async def finalize_assessment(self) -> AssessmentResult:
        """
        Finalize assessment and generate results

        Returns:
            Complete assessment result with summary
        """
        # Calculate final score
        final_score = calculate_final_score(self.question_scores)

        # Generate pillar breakdown with pillar names and max scores
        pillar_questions = {
            pillar.name: [(q.id, q.max_score) for q in pillar.questions]
            for pillar in self.pillars.values()
        }
        breakdown = generate_breakdown(self.question_scores, pillar_questions)

        # Generate AI summary
        summary = await self.ollama.generate_summary(
            final_score, breakdown, self.question_results
        )

        return AssessmentResult(
            final_score=round(final_score, 2),
            breakdown=breakdown,
            question_results=self.question_results,
            summary=summary,
        )

    def get_next_question(self) -> Optional[tuple]:
        """
        Get next question in sequence (adaptive: prioritizes follow-ups)

        Returns:
            (pillar_id, question, pillar_name) or None if complete
        """
        # Prioritize pending follow-ups (adaptive questioning)
        if self.pending_follow_ups:
            return self.pending_follow_ups.pop(0)
        
        # Otherwise, continue with base questions
        if self.current_question_index >= len(self.questions):
            return None

        question_tuple = self.questions[self.current_question_index]
        self.current_question_index += 1
        return question_tuple

    def reset(self):
        """Reset orchestrator for new assessment"""
        self.question_scores = {}
        self.question_results = []
        self.current_question_index = 0
        self.pending_follow_ups = []
        # Note: We keep importance_weights_assigned=True to avoid re-scoring on reset
