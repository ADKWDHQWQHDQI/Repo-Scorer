"""Configuration for repository assessment questions and scoring"""

from enum import Enum
from typing import Dict, List
from dataclasses import dataclass


class RepositoryTool(str, Enum):
    """Supported repository tools"""
    GITHUB = "github"
    GITLAB = "gitlab"
    AZURE_DEVOPS = "azure_devops"


@dataclass
class Question:
    """Individual question with weight"""
    id: str
    text: str
    max_score: float
    importance: float = 5.0  # Default importance, will be set by LLM (1-10 scale)


@dataclass
class Pillar:
    """Scoring pillar with questions"""
    name: str
    total_weight: float
    questions: List[Question]


# Question importance scoring prompt
QUESTION_IMPORTANCE_PROMPT = """You are evaluating the importance of repository governance practices. Your task is to DIFFERENTIATE between practices - not all practices are equally important.

Question:
"{question}"

Rate the importance of this practice for a well-governed repository on a scale of 1-10:

CRITICAL FOUNDATION (9-10):
- Security vulnerabilities that could lead to breaches
- Practices that prevent production incidents
- Access control and authentication fundamentals
- Example: Branch protection, code review requirements

HIGH IMPACT (7-8):
- Significantly improves code quality or team velocity
- Prevents common mistakes and rework
- Example: Automated testing, CODEOWNERS

MODERATE IMPACT (4-6):
- Good practices that help but aren't critical
- Process improvements with measurable benefits
- Example: PR templates, commit conventions

NICE TO HAVE (1-3):
- Minor conveniences or optimizations
- Practices with limited impact on outcomes
- Example: Aesthetic preferences, optional tooling

IMPORTANT: Be critical and specific. Most practices should NOT be 9-10. Reserve high scores for truly critical items.

Respond with ONLY a single number from 1 to 10."""


# GitHub Questions (15 questions, ~6.67 points each)
GITHUB_QUESTIONS = [
    "Are repositories organized using organizations and teams, with role-based access instead of individual permissions?",
    "Is branch protection enforced (mandatory PRs, minimum reviewers, status checks)?",
    "Are CODEOWNERS files used to automatically assign reviewers for critical paths?",
    "Are Pull Request templates standardized across repositories?",
    "Is signed commits or commit verification enforced?",
    "Are secrets prevented from being committed using GitHub secret scanning?",
    "Are repository visibility policies (public/internal/private) clearly defined and enforced?",
    "Is repository naming and structure standardized across the organization?",
    "Are GitHub Actions status checks mandatory before merge?",
    "Are stale branches automatically cleaned up after merge?",
    "Is monorepo vs multirepo strategy clearly defined and documented?",
    "Are forking policies clearly defined for internal and external contributors?",
    "Is repository archival managed for inactive or deprecated projects?",
    "Are security alerts (Dependabot, CodeQL) actively monitored and acted upon?",
    "Is repository activity (PR cycle time, merge frequency) measured and reviewed periodically?",
]

# GitLab Questions (15 questions, ~6.67 points each)
GITLAB_QUESTIONS = [
    "Are repositories structured using groups and subgroups aligned to teams or products?",
    "Is merge request approval rules enforced based on branch and code area?",
    "Are protected branches configured with restricted push and merge permissions?",
    "Are merge request templates standardized and mandatory?",
    "Is commit signing or verification enabled?",
    "Are push rules configured to prevent secrets, large files, or invalid commits?",
    "Are code owners defined using CODEOWNERS for approval routing?",
    "Are repository access levels (Guest, Reporter, Developer, Maintainer) clearly governed?",
    "Are merge strategies (merge commit, squash, fast-forward) standardized?",
    "Are inactive branches and repositories automatically identified and cleaned up?",
    "Is monorepo vs multirepo guidance documented and followed?",
    "Are fork workflows governed for internal and external contributions?",
    "Are repository compliance checks enforced before merge?",
    "Are security scanning results reviewed before code promotion?",
    "Are repository KPIs (MR aging, review time, merge rate) tracked and improved?",
]

# Azure DevOps Questions (15 questions, ~6.67 points each)
AZURE_DEVOPS_QUESTIONS = [
    "Are repositories organized using projects and teams aligned to delivery units?",
    "Are branch policies enforced (minimum reviewers, build validation, comment resolution)?",
    "Are path-based policies used for critical code areas?",
    "Are pull request templates standardized?",
    "Is commit history hygiene maintained (squash/rebase strategies)?",
    "Are service hooks or policies used to prevent secret leakage?",
    "Are repository permissions managed using Azure AD groups?",
    "Are naming conventions enforced for repos and branches?",
    "Are build validations mandatory before PR completion?",
    "Are stale branches periodically cleaned up?",
    "Is there a defined repo strategy for microservices vs monoliths?",
    "Are fork-based workflows governed for partners or vendors?",
    "Are repo policies audited regularly for compliance?",
    "Are security issues in repos tracked and remediated systematically?",
    "Are repository metrics (PR throughput, reviewer load) used for process improvement?",
]


def get_questions_for_tool(tool: RepositoryTool) -> Dict[str, Pillar]:
    """
    Get predefined questions for a specific repository tool
    
    Args:
        tool: The repository tool (GitHub, GitLab, or Azure DevOps)
        
    Returns:
        Dictionary of pillar_id -> Pillar with questions
    """
    # Tool-specific questions (100 points total: 15 questions × ~6.67 points each)
    tool_questions_map = {
        RepositoryTool.GITHUB: GITHUB_QUESTIONS,
        RepositoryTool.GITLAB: GITLAB_QUESTIONS,
        RepositoryTool.AZURE_DEVOPS: AZURE_DEVOPS_QUESTIONS,
    }
    
    tool_questions = tool_questions_map[tool]
    tool_name = tool.value.replace("_", " ").title()
    
    # Create tool-specific pillar (100 points)
    tool_pillar_questions = [
        Question(
            id=f"{tool.value}_{i+1}",
            text=q,
            max_score=round(100.0 / len(tool_questions), 2),
        )
        for i, q in enumerate(tool_questions)
    ]
    
    # Adjust last question to ensure total is exactly 100
    total = sum(q.max_score for q in tool_pillar_questions)
    if abs(total - 100.0) > 0.01:
        tool_pillar_questions[-1].max_score = round(
            tool_pillar_questions[-1].max_score + (100.0 - total), 2
        )
    
    pillars = {
        f"{tool.value}_specific": Pillar(
            name=f"{tool_name} - Repository & Code Management",
            total_weight=100.0,
            questions=tool_pillar_questions,
        )
    }
    
    return pillars


def get_all_questions(pillars: Dict[str, Pillar]) -> List[tuple[str, Question, str]]:
    """Get all questions with their pillar context"""
    questions = []
    for pillar_id, pillar in pillars.items():
        for question in pillar.questions:
            questions.append((pillar_id, question, pillar.name))
    return questions

