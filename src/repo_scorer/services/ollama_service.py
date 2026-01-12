"""Ollama service for LLM interactions"""

import asyncio
import os
from typing import Optional
from dotenv import load_dotenv

try:
    import ollama
except ImportError:
    raise ImportError(
        "ollama package not found. Please install: pip install ollama"
    )

from repo_scorer.config import SYSTEM_PROMPT, CLASSIFICATION_PROMPT, FOLLOW_UP_DECISION_PROMPT, QUESTION_IMPORTANCE_PROMPT

# Load environment variables
load_dotenv()


class OllamaService:
    """Service for interacting with local Ollama LLM"""

    def __init__(
        self,
        model: Optional[str] = None,
        host: Optional[str] = None,
        timeout: int = 60,
    ):
        self.model = model or os.getenv("OLLAMA_MODEL", "phi-3:mini")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.timeout = timeout or int(os.getenv("OLLAMA_TIMEOUT", "60"))
        self.client = ollama.AsyncClient(host=self.host)

    async def check_health(self) -> tuple[bool, bool]:
        """
        Check if Ollama is running and model is available

        Returns:
            (ollama_connected, model_available)
        """
        try:
            # Try to list models
            models = await self.client.list()
            
            # Handle both dict response and object response
            if hasattr(models, 'models'):
                model_list = models.models
            elif isinstance(models, dict):
                model_list = models.get("models", [])
            else:
                model_list = []
            
            # Extract model names
            model_names = []
            for m in model_list:
                if hasattr(m, 'model'):
                    model_names.append(m.model)
                elif isinstance(m, dict):
                    model_names.append(m.get("name", m.get("model", "")))
                else:
                    model_names.append(str(m))

            # Check if our model is available
            model_available = any(
                self.model in name or name.startswith(self.model.split(":")[0])
                for name in model_names
            )

            return True, model_available
        except Exception as e:
            print(f"Ollama health check failed: {e}")
            return False, False

    async def classify_answer(
        self, question_text: str, user_answer: str
    ) -> str:
        """
        Classify user's answer using LLM

        Args:
            question_text: The question that was asked
            user_answer: User's natural language answer

        Returns:
            Classification: "yes", "partial", "no", or "unsure"
        """
        prompt = CLASSIFICATION_PROMPT.format(
            question=question_text, answer=user_answer
        )

        try:
            response = await asyncio.wait_for(
                self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    system=SYSTEM_PROMPT,
                    stream=False,
                    options={
                        "temperature": 0.1,  # Low temperature for consistent classification
                        "num_predict": 10,    # Only need one word
                    },
                ),
                timeout=self.timeout,
            )

            # Extract and clean the classification
            classification = response["response"].strip().lower()
            
            # Remove any extra text, punctuation, or explanations
            classification = classification.split()[0] if classification else ""
            classification = classification.strip('.,;:!?')

            # Validate classification
            valid_classifications = ["yes", "partial", "no", "unsure"]
            if classification in valid_classifications:
                return classification

            # Enhanced fallback logic with user answer analysis
            user_answer_lower = user_answer.lower()
            
            # Check for clear yes patterns
            if any(word in user_answer_lower for word in [
                "yes", "yep", "yeah", "yup", "definitely", "absolutely", 
                "correct", "true", "indeed", "certainly", "confirmed"
            ]):
                return "yes"
            
            # Check for clear no patterns
            if any(word in user_answer_lower for word in [
                "no", "nope", "nah", "never", "not implemented", "don't have",
                "haven't", "not yet", "removed", "doesn't exist"
            ]):
                return "no"
            
            # Check for partial patterns
            if any(word in user_answer_lower for word in [
                "partial", "somewhat", "kinda", "kind of", "sort of", "sorta",
                "sometimes", "maybe", "mostly", "working on", "in progress",
                "some", "depends", "varies", "mixed", "trying"
            ]):
                return "partial"
            
            # Check for unsure patterns
            if any(word in user_answer_lower for word in [
                "idk", "dunno", "don't know", "not sure", "unsure", 
                "unclear", "unknown", "can't say"
            ]) or len(user_answer.strip()) < 3:  # Very short responses like "...", "hmm"
                return "unsure"
            
            # If LLM gave a classification word but not exact, try to match
            if "yes" in classification:
                return "yes"
            elif "no" in classification:
                return "no"
            elif "partial" in classification:
                return "partial"
            
            # Default to unsure for ambiguous cases
            return "unsure"

        except asyncio.TimeoutError:
            print(f"Timeout classifying answer after {self.timeout}s")
            return "unsure"
        except Exception as e:
            print(f"Error classifying answer: {e}")
            return "unsure"

    async def decide_follow_up(
        self, 
        original_question: str, 
        user_answer: str, 
        classification: str,
        follow_up_question: str
    ) -> bool:
        """
        AI decides whether to ask a follow-up question based on context
        
        This is the core of adaptive questioning - AI analyzes the user's
        answer and determines if the follow-up would provide valuable clarification.
        
        Args:
            original_question: The original question asked
            user_answer: User's response to original question
            classification: How the answer was classified
            follow_up_question: The proposed follow-up question
            
        Returns:
            True if follow-up should be asked, False otherwise
        """
        prompt = FOLLOW_UP_DECISION_PROMPT.format(
            original_question=original_question,
            user_answer=user_answer,
            classification=classification,
            follow_up_question=follow_up_question
        )
        
        try:
            response = await asyncio.wait_for(
                self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    system=SYSTEM_PROMPT,
                    stream=False,
                    options={
                        "temperature": 0.2,  # Low temperature for consistent decisions
                        "num_predict": 5,    # Just need "yes" or "no"
                    },
                ),
                timeout=10,  # Shorter timeout for decision
            )
            
            decision = response["response"].strip().lower()
            decision = decision.split()[0] if decision else ""
            decision = decision.strip('.,;:!?')
            
            # Parse decision
            if "yes" in decision:
                return True
            elif "no" in decision:
                return False
            
            # Default behavior: ask follow-up for partial/no classifications
            return classification in ["partial", "no"]
            
        except Exception as e:
            print(f"Error deciding follow-up: {e}")
            # Fallback: ask follow-up for partial/no classifications
            return classification in ["partial", "no"]

    async def score_question_importance(self, question_text: str) -> float:
        """
        Score the importance of a question using LLM
        
        The LLM evaluates how critical this governance practice is for
        repository health, security, and team productivity.
        
        Args:
            question_text: The question to evaluate
            
        Returns:
            Importance score from 1.0 to 10.0
        """
        prompt = QUESTION_IMPORTANCE_PROMPT.format(question=question_text)
        
        try:
            response = await asyncio.wait_for(
                self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    system="You are an expert in software engineering governance and best practices.",
                    stream=False,
                    options={
                        "temperature": 0.3,  # Some variation but generally consistent
                        "num_predict": 5,    # Just need a number
                    },
                ),
                timeout=10,
            )
            
            # Extract the number from response
            importance_text = response["response"].strip()
            
            # Try to extract first number found
            import re
            numbers = re.findall(r'\b([1-9]|10)\b', importance_text)
            if numbers:
                importance = float(numbers[0])
                # Ensure it's in valid range
                return max(1.0, min(10.0, importance))
            
            # Fallback: default to medium importance
            return 5.0
            
        except Exception as e:
            print(f"Error scoring question importance: {e}")
            # Fallback: default to medium importance
            return 5.0
    
    async def generate_summary(
        self, final_score: float, breakdown: dict, question_results: list
    ) -> str:
        """
        Generate a fact-based summary of the assessment

        Args:
            final_score: Total score out of 100
            breakdown: Pillar-wise scores (pillar_name -> (earned, max))
            question_results: List of question results

        Returns:
            AI-generated summary based on actual results
        """
        # Build detailed context from actual results
        context = f"Repository Assessment Score: {final_score}/100\n\n"
        context += "Pillar Performance:\n"
        for pillar_name, (earned, max_score) in breakdown.items():
            percentage = (earned / max_score * 100) if max_score > 0 else 0
            context += f"  - {pillar_name}: {earned}/{max_score} ({percentage:.1f}%)\n"
        
        # Add key findings
        context += "\nKey Findings:\n"
        strong_areas = []
        weak_areas = []
        
        for result in question_results:
            if result.classification == "yes":
                strong_areas.append(result.question_text)
            elif result.classification == "no":
                weak_areas.append(result.question_text)
        
        if strong_areas:
            context += f"Strengths ({len(strong_areas)} items)\n"
        if weak_areas:
            context += f"Improvements needed ({len(weak_areas)} items)\n"

        prompt = f"""Based on this actual assessment data:

{context}

Write a factual 2-3 sentence summary:
1. Mention the overall score
2. Identify the strongest pillar by name and percentage
3. Identify the weakest area that needs improvement

Use ONLY the data provided. Do not make up statistics or details."""

        try:
            response = await asyncio.wait_for(
                self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    stream=False,
                    options={
                        "temperature": 0.3,  # Lower temperature for factual output
                        "num_predict": 200,
                    },
                ),
                timeout=self.timeout,
            )

            return response["response"].strip()

        except asyncio.TimeoutError:
            # Generate simple factual summary
            best_pillar = max(breakdown.items(), key=lambda x: x[1][0] / x[1][1] if x[1][1] > 0 else 0)
            worst_pillar = min(breakdown.items(), key=lambda x: x[1][0] / x[1][1] if x[1][1] > 0 else 0)
            return (
                f"Assessment complete with score of {final_score}/100. "
                f"Strongest area: {best_pillar[0]} ({best_pillar[1][0]}/{best_pillar[1][1]}). "
                f"Needs improvement: {worst_pillar[0]} ({worst_pillar[1][0]}/{worst_pillar[1][1]})."
            )
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Assessment complete. Final score: {final_score}/100. Review breakdown for details."
