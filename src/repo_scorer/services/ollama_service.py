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

# Deprecated: QUESTION_IMPORTANCE_PROMPT is no longer used
# Importance scores are now manually defined in config.py
QUESTION_IMPORTANCE_PROMPT = """Deprecated - importance scores are now in config"""

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
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b-instruct")
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.timeout = timeout or int(os.getenv("OLLAMA_TIMEOUT", "60"))
        # Don't create client here - create fresh for each operation to avoid event loop issues
        self._client = None
    
    def _get_client(self):
        """Get or create a fresh AsyncClient for the current event loop"""
        # Always create a fresh client to avoid event loop binding issues
        return ollama.AsyncClient(host=self.host)

    async def check_health(self) -> tuple[bool, bool]:
        """
        Check if Ollama is running and model is available

        Returns:
            (ollama_connected, model_available)
        """
        try:
            # Try to list models with fresh client
            client = self._get_client()
            models = await client.list()
            
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
    
    async def analyze_answer(self, question: str, answer: str, importance: float) -> str:
        """
        Analyze a single question-answer pair and provide brief insight
        
        Args:
            question: The governance question
            answer: User's answer (yes/no with optional details)
            importance: Importance score of the question (1-10)
            
        Returns:
            Brief analysis/insight (2-3 sentences)
        """
        prompt = f"""Question: {question}
Answer: {answer}

Provide 1-2 sentence insight (max 40 words):
If YES: Impact and benefit
If NO: Why it matters"""
        
        print(f"🤖 Analyzing Q{importance:.0f}... ", end="", flush=True)
        
        try:
            client = self._get_client()
            response = await asyncio.wait_for(
                client.generate(
                    model=self.model,
                    prompt=prompt,
                    system="Repository governance expert. Be concise.",
                    stream=False,
                    options={
                        "temperature": 0.6,
                        "num_predict": 50,  # Shorter for speed
                    },
                ),
                timeout=20,  # Fast timeout
            )
            analysis = response["response"].strip()
            print(f"✅ Done")
            return analysis
        except asyncio.TimeoutError:
            print(f"⚠️ Timeout")
            return "Analysis unavailable (timeout)."
        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                print(f"⚠️ Model not found")
            else:
                print(f"⚠️ Failed")
            return "Analysis unavailable for this response."
    
    async def generate_final_summary(self, 
                                     tool_name: str,
                                     yes_answers: list[tuple[str, str, float, str]], 
                                     no_answers: list[tuple[str, str, float, str]],
                                     final_score: float) -> str:
        """
        Generate comprehensive final summary with strengths and improvement recommendations
        
        Args:
            tool_name: Name of the repository tool (GitHub/GitLab/Azure DevOps)
            yes_answers: List of (question, answer, importance, analysis) for YES responses
            no_answers: List of (question, answer, importance, analysis) for NO responses
            final_score: Final assessment score (0-100)
            
        Returns:
            Comprehensive professional summary
        """
        # Build context efficiently
        strengths_context = "\n".join([
            f"- {q} (Importance: {imp}/10)"
            for q, _, imp, _ in yes_answers[:10]  # Limit to avoid token overflow
        ])
        
        gaps_context = "\n".join([
            f"- {q} (Importance: {imp}/10)"
            for q, _, imp, _ in no_answers[:10]  # Limit to avoid token overflow
        ])
        
        prompt = f"""Assessment: {tool_name} | Score: {final_score}/100 | Implemented: {len(yes_answers)}/{len(yes_answers) + len(no_answers)}

STRENGTHS:
{strengths_context[:500] if strengths_context else "None"}

GAPS:
{gaps_context[:500] if gaps_context else "None"}

Provide concise summary (max 300 words):
1. Executive Summary (2 sentences)
2. Top 3 Strengths
3. Top 3 Critical Improvements (why + how)
4. Quick Roadmap: Immediate/Short/Long-term priorities

Be specific and actionable."""
        
        print(f"\n📊 Generating summary... ", end="", flush=True)
        
        try:
            client = self._get_client()
            response = await asyncio.wait_for(
                client.generate(
                    model=self.model,
                    prompt=prompt,
                    system="DevOps expert. Concise, actionable guidance.",
                    stream=False,
                    options={
                        "temperature": 0.6,
                        "num_predict": 350,  # Reduced for speed
                    },
                ),
                timeout=40,  # Fast timeout
            )
            summary = response["response"].strip()
            print(f"✅ Done ({len(summary)} chars)")
            return summary
        except asyncio.TimeoutError:
            print(f"⚠️ Timeout (>40s)")
            return "Summary generation timed out. Review individual question insights below."
        except Exception as e:
            error_msg = str(e)
            if "model" in error_msg.lower() and "not found" in error_msg.lower():
                print(f"⚠️ Model not found")
                return f"Model '{self.model}' not available. Install: ollama pull {self.model}"
            else:
                print(f"⚠️ Failed: {e}")
                return "Unable to generate summary. Review individual question insights below."

    async def score_question_importance(self, question_text: str, default_score: float = 5.0) -> float:
        """
        Score the importance of a question using LLM
        
        The LLM evaluates how critical this governance practice is for
        repository health, security, and team productivity.
        
        Args:
            question_text: The question to evaluate
            default_score: Fallback score if LLM fails (default: 5.0)
            
        Returns:
            Importance score from 1.0 to 10.0
        """
        prompt = QUESTION_IMPORTANCE_PROMPT.format(question=question_text)
        
        print(f"   🤖 Sending request to LLM ({self.model})...")
        print(f"   ⏱️  Timeout: 15 seconds")
        
        # Retry only once for faster processing
        for attempt in range(1):
            try:
                client = self._get_client()
                response = await asyncio.wait_for(
                    client.generate(
                        model=self.model,
                        prompt=prompt,
                        system="You are an expert in software engineering governance and best practices. Differentiate carefully between practices.",
                        stream=False,
                        options={
                            "temperature": 0.3,  # Slightly higher to get more varied responses
                            "num_predict": 10,   # Allow a bit more tokens for number + reasoning
                        },
                    ),
                    timeout=15,  # Reduced timeout for faster processing
                )
                
                # Extract the number from response
                importance_text = response["response"].strip()
                print(f"   📥 LLM Response: '{importance_text}'")
                
                # Try to extract first number found
                import re
                numbers = re.findall(r'\b([1-9]|10)\b', importance_text)
                if numbers:
                    importance = float(numbers[0])
                    # Ensure it's in valid range
                    importance = max(1.0, min(10.0, importance))
                    print(f"   ✨ Parsed Score: {importance}/10")
                    return importance
                
                # If no number found, try parsing decimal numbers as well
                decimal_numbers = re.findall(r'\b(10|[1-9](?:\.\d+)?)\b', importance_text)
                if decimal_numbers:
                    importance = float(decimal_numbers[0])
                    importance = max(1.0, min(10.0, importance))
                    print(f"   ✨ Parsed Score: {importance}/10")
                    return importance
                
                # If no number found, use default
                print(f"   ⚠️  Could not parse LLM response, using default: {default_score}")
                return default_score
                    
            except asyncio.TimeoutError:
                print(f"   ⏱️  Timeout (15s exceeded)")
                print(f"   ⚠️  Using default score: {default_score}/10")
                return default_score
            except KeyError as e:
                print(f"   ❌ Invalid response structure: {e}")
                print(f"   ⚠️  Using default score: {default_score}/10")
                return default_score
            except Exception as e:
                print(f"   ❌ Error: {e}")
                print(f"   ⚠️  Using default score: {default_score}/10")
                return default_score
        
        # Fallback if all attempts failed
        return default_score
