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

from repo_scorer.config import QUESTION_IMPORTANCE_PROMPT

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
