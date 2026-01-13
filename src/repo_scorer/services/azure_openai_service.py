"""Azure OpenAI service for LLM interactions"""

import os
from typing import Optional
from dotenv import load_dotenv

try:
    from openai import AzureOpenAI
except ImportError:
    raise ImportError(
        "openai package not found. Please install: pip install openai"
    )

# Load environment variables
load_dotenv()


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "https://reposcorer.cognitiveservices.azure.com/")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        
        if not self.api_key:
            raise ValueError("Azure OpenAI API key is required. Set AZURE_OPENAI_API_KEY environment variable.")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.endpoint,
            api_version=self.api_version
        )

    async def check_health(self) -> tuple[bool, bool]:
        """
        Check if Azure OpenAI is accessible and deployment is available

        Returns:
            (service_connected, deployment_available)
        """
        try:
            # Try a simple completion to verify connectivity
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True, True
        except Exception as e:
            print(f"Azure OpenAI health check failed: {e}")
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
If NO: Risk and recommendation"""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a repository governance expert. Provide concise, actionable insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "Analysis unavailable."
        except Exception as e:
            print(f"Error analyzing answer: {e}")
            return "Analysis unavailable."
    
    async def generate_comprehensive_summary(
        self, yes_answers: list, no_answers: list, total_score: float
    ) -> str:
        """
        Generate comprehensive assessment summary with strengths and recommendations
        
        Args:
            yes_answers: List of (question, answer, importance, analysis) for YES responses
            no_answers: List of (question, answer, importance, analysis) for NO responses
            total_score: Final assessment score
            
        Returns:
            Formatted professional summary
        """
        # Prepare strengths (YES answers, highest importance first)
        yes_sorted = sorted(yes_answers, key=lambda x: x[2], reverse=True)
        strengths_text = "\n".join([
            f"- {q} (Priority: {imp:.0f}/10)"
            for q, _, imp, _ in yes_sorted[:5]  # Top 5 strengths
        ])
        
        # Prepare gaps (NO answers, highest importance first)
        no_sorted = sorted(no_answers, key=lambda x: x[2], reverse=True)
        gaps_text = "\n".join([
            f"- {q} (Priority: {imp:.0f}/10)"
            for q, _, imp, _ in no_sorted[:5]  # Top 5 gaps
        ])
        
        prompt = f"""Generate a professional repository governance assessment summary.

OVERALL SCORE: {total_score:.1f}/100

IMPLEMENTED STRENGTHS ({len(yes_answers)} practices):
{strengths_text if strengths_text else "None identified"}

CRITICAL GAPS ({len(no_answers)} missing practices):
{gaps_text if gaps_text else "None identified"}

Provide:
1. Executive Overview (2-3 sentences)
2. Key Strengths (bullet points)
3. Critical Gaps & Risks (bullet points)
4. Prioritized Recommendations (3-5 actionable items, prioritize by importance score)

Keep it professional, concise, and actionable. Maximum 300 words."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a senior repository governance consultant. Provide executive-level insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else f"Assessment completed with score {total_score:.1f}/100. Review individual question insights for detailed analysis."
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Assessment completed with score {total_score:.1f}/100. Review individual question insights for detailed analysis."
