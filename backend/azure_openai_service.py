"""Azure OpenAI service for LLM interactions"""

import os
import time
import logging
from typing import Optional
from dotenv import load_dotenv

try:
    from openai import AzureOpenAI, APIError, RateLimitError, APITimeoutError
except ImportError:
    raise ImportError(
        "openai package not found. Please install: pip install openai"
    )

# Load environment variables
load_dotenv()

# Setup logging
logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Service for interacting with Azure OpenAI"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "https://reposcorer.cognitiveservices.azure.com/")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        self.max_retries = max_retries
        self.timeout = timeout
        
        if not self.api_key:
            error_msg = (
                "Azure OpenAI API key is required but not found.\n"
                "Please set AZURE_OPENAI_API_KEY in your .env file.\n"
                "For local development:\n"
                "  1. Copy backend/.env.example to backend/.env\n"
                "  2. Get your API key from Azure Portal > Azure OpenAI Service > Keys and Endpoint\n"
                "  3. Set AZURE_OPENAI_API_KEY=your-key-here in .env file"
            )
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.endpoint,
            api_version=self.api_version,
            timeout=self.timeout,
            max_retries=0  # We handle retries manually with exponential backoff
        )
    
    def _retry_with_exponential_backoff(self, func, *args, **kwargs):
        """
        Retry a function with exponential backoff
        
        Args:
            func: Function to retry
            *args, **kwargs: Arguments to pass to the function
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except (RateLimitError, APITimeoutError, APIError) as e:
                last_exception = e
                error_type = type(e).__name__
                
                if attempt < self.max_retries - 1:
                    # Calculate backoff time: 1s, 2s, 4s, 8s
                    backoff_time = 2 ** attempt
                    logger.warning(
                        f"Azure OpenAI API {error_type} (attempt {attempt + 1}/{self.max_retries}). "
                        f"Retrying in {backoff_time}s..."
                    )
                    time.sleep(backoff_time)
                else:
                    logger.error(
                        f"Azure OpenAI API {error_type} after {self.max_retries} attempts: {str(e)}"
                    )
            except Exception as e:
                # For unexpected errors, don't retry
                logger.error(f"Unexpected error calling Azure OpenAI: {str(e)}")
                raise
        
        if last_exception:
            raise last_exception
        raise RuntimeError("All retry attempts failed without catching an exception")

    async def check_health(self) -> tuple[bool, bool]:
        """
        Check if Azure OpenAI is accessible and deployment is available

        Returns:
            (service_connected, deployment_available)
        """
        try:
            # Try a simple completion to verify connectivity
            response = self._retry_with_exponential_backoff(
                self.client.chat.completions.create,
                model=self.deployment,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True, True
        except Exception as e:
            logger.error(f"Azure OpenAI health check failed: {e}")
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
        priority_level = "CRITICAL" if importance >= 9 else "HIGH" if importance >= 7 else "MODERATE" if importance >= 5 else "STANDARD"
        
        prompt = f"""Analyze this repository governance practice:

Question: {question}
Answer: {answer}
Priority Level: {priority_level} (Importance: {importance}/10)

Provide a focused, actionable insight (35-45 words):

If YES:
- State the specific positive impact on repository quality/security/efficiency
- Mention 1 key benefit this practice provides
- Briefly note how it protects or enhances the development workflow

If NO:
- Clearly state the primary risk or vulnerability this creates
- Provide 1 specific, actionable recommendation to implement this practice
- Mention the expected improvement once implemented

Focus on business value and technical impact. Be direct and specific."""

        try:
            response = self._retry_with_exponential_backoff(
                self.client.chat.completions.create,
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a senior DevOps and repository governance expert with deep knowledge of CI/CD, security best practices, and software quality standards. Provide insights that are technically accurate, actionable, and business-focused. Avoid generic advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=120,
                temperature=0.6
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "Analysis unavailable."
        except Exception as e:
            logger.error(f"Error analyzing answer for question: {e}")
            return f"Analysis temporarily unavailable due to service error."
    
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
            f"  • {q} [Priority: {imp:.0f}/10]"
            for q, _, imp, _ in yes_sorted[:7]  # Top 7 strengths
        ])
        
        # Prepare gaps (NO answers, highest importance first)
        no_sorted = sorted(no_answers, key=lambda x: x[2], reverse=True)
        gaps_text = "\n".join([
            f"  • {q} [Priority: {imp:.0f}/10]"
            for q, _, imp, _ in no_sorted[:7]  # Top 7 gaps
        ])
        
        # Calculate score tier
        score_tier = "EXCELLENT" if total_score >= 80 else "GOOD" if total_score >= 60 else "MODERATE" if total_score >= 40 else "NEEDS IMPROVEMENT"
        
        prompt = f"""You are a senior DevOps and repository governance consultant preparing an executive-level assessment report.

=== ASSESSMENT OVERVIEW ===
Overall Score: {total_score:.1f}/100 ({score_tier})
Implemented Practices: {len(yes_answers)}
Missing Critical Practices: {len(no_answers)}

=== TOP IMPLEMENTED STRENGTHS ===
{strengths_text if strengths_text else "  • No practices currently implemented"}

=== CRITICAL GAPS & MISSING PRACTICES ===
{gaps_text if gaps_text else "  • All practices implemented"}

=== YOUR TASK ===
Create a professional, executive-level assessment summary with these sections:

**1. EXECUTIVE SUMMARY** (3-4 sentences)
- Open with the overall governance maturity level and score context
- Highlight the most critical finding (strength OR gap)
- State business impact: security posture, development velocity, code quality
- Provide forward-looking statement about potential improvements

**2. KEY STRENGTHS & COMPETITIVE ADVANTAGES** (3-5 bullet points)
- Focus on practices with highest priority scores
- Explain specific business value: reduced risks, faster deployments, better quality
- Mention how these create competitive advantages or prevent common issues
- Be specific about the protection or efficiency gained

**3. CRITICAL GAPS & RISK EXPOSURE** (3-5 bullet points)
- Prioritize by importance score and actual risk
- Clearly state the security, quality, or operational risk each gap creates
- Quantify impact where possible: "increases vulnerability to X", "slows release cycle by Y"
- Connect each gap to real-world consequences teams face

**4. STRATEGIC IMPLEMENTATION ROADMAP** (4-6 prioritized recommendations)
- Order by: Critical security gaps → High-impact quality improvements → Efficiency gains
- Format each as: "[PRIORITY LEVEL] Action Item: Specific implementation step"
- Provide concrete next steps, not generic advice
- Include quick wins (can be done in days) and strategic initiatives (weeks/months)
- Mention tools, features, or workflows to adopt

**GUIDELINES:**
- Write in professional business tone suitable for technical leaders
- Use specific terminology: branch protection, CODEOWNERS, secret scanning, etc.
- Avoid generic phrases like "improve security" - be specific about WHAT and HOW
- Focus on actionable insights, not philosophical statements
- Maximum 400 words total
- Use clear formatting with bold section headers

Generate the comprehensive assessment report now:"""

        try:
            response = self._retry_with_exponential_backoff(
                self.client.chat.completions.create,
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a principal DevOps consultant and repository governance expert who has assessed hundreds of enterprise development teams. You understand the business impact of technical practices. Your reports are known for being actionable, specific, and immediately valuable to engineering leadership. You never provide generic advice - every recommendation is concrete and implementation-focused."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else f"Assessment completed with score {total_score:.1f}/100. Review individual question insights for detailed analysis."
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Assessment completed with score {total_score:.1f}/100. Detailed summary temporarily unavailable due to service error. Review individual question insights for analysis."
