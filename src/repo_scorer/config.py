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
    """Individual question with manually assigned importance weight"""
    id: str
    text: str
    max_score: float
    importance: float  # Manual importance score (1-10 scale) - higher means more critical


@dataclass
class Pillar:
    """Scoring pillar with questions"""
    name: str
    total_weight: float
    questions: List[Question]


# GitHub Questions with Manual Importance Scores
# Each tuple is (question_text, importance_score)
# Importance scale: 1-10 (1=low, 10=critical)
GITHUB_QUESTIONS = [
    ("Are repositories organized using organizations and teams, with role-based access instead of individual permissions?", 8.0),
    ("Is branch protection enforced (mandatory PRs, minimum reviewers, status checks)?", 10.0),
    ("Are CODEOWNERS files used to automatically assign reviewers for critical paths?", 7.0),
    ("Are Pull Request templates standardized across repositories?", 5.0),
    ("Is signed commits or commit verification enforced?", 6.0),
    ("Are secrets prevented from being committed using GitHub secret scanning?", 10.0),
    ("Are repository visibility policies (public/internal/private) clearly defined and enforced?", 9.0),
    ("Is repository naming and structure standardized across the organization?", 4.0),
    ("Are GitHub Actions status checks mandatory before merge?", 8.0),
    ("Are stale branches automatically cleaned up after merge?", 3.0),
    ("Is monorepo vs multirepo strategy clearly defined and documented?", 6.0),
    ("Are forking policies clearly defined for internal and external contributors?", 5.0),
    ("Is repository archival managed for inactive or deprecated projects?", 3.0),
    ("Are security alerts (Dependabot, CodeQL) actively monitored and acted upon?", 9.0),
    ("Is repository activity (PR cycle time, merge frequency) measured and reviewed periodically?", 4.0),
]

# GitLab Questions with Manual Importance Scores
# Each tuple is (question_text, importance_score)
# Importance scale: 1-10 (1=low, 10=critical)
GITLAB_QUESTIONS = [
    ("Are repositories structured using groups and subgroups aligned to teams or products?", 7.0),
    ("Is merge request approval rules enforced based on branch and code area?", 9.0),
    ("Are protected branches configured with restricted push and merge permissions?", 10.0),
    ("Are merge request templates standardized and mandatory?", 5.0),
    ("Is commit signing or verification enabled?", 6.0),
    ("Are push rules configured to prevent secrets, large files, or invalid commits?", 10.0),
    ("Are code owners defined using CODEOWNERS for approval routing?", 7.0),
    ("Are repository access levels (Guest, Reporter, Developer, Maintainer) clearly governed?", 8.0),
    ("Are merge strategies (merge commit, squash, fast-forward) standardized?", 4.0),
    ("Are inactive branches and repositories automatically identified and cleaned up?", 3.0),
    ("Is monorepo vs multirepo guidance documented and followed?", 6.0),
    ("Are fork workflows governed for internal and external contributions?", 5.0),
    ("Are repository compliance checks enforced before merge?", 8.0),
    ("Are security scanning results reviewed before code promotion?", 9.0),
    ("Are repository KPIs (MR aging, review time, merge rate) tracked and improved?", 4.0),
]

# Azure DevOps Questions with Manual Importance Scores
# Each tuple is (question_text, importance_score)
# Importance scale: 1-10 (1=low, 10=critical)
AZURE_DEVOPS_QUESTIONS = [
    ("Are repositories organized using projects and teams aligned to delivery units?", 7.0),
    ("Are branch policies enforced (minimum reviewers, build validation, comment resolution)?", 10.0),
    ("Are path-based policies used for critical code areas?", 8.0),
    ("Are pull request templates standardized?", 5.0),
    ("Is commit history hygiene maintained (squash/rebase strategies)?", 4.0),
    ("Are service hooks or policies used to prevent secret leakage?", 10.0),
    ("Are repository permissions managed using Azure AD groups?", 8.0),
    ("Are naming conventions enforced for repos and branches?", 3.0),
    ("Are build validations mandatory before PR completion?", 9.0),
    ("Are stale branches periodically cleaned up?", 3.0),
    ("Is there a defined repo strategy for microservices vs monoliths?", 6.0),
    ("Are fork-based workflows governed for partners or vendors?", 5.0),
    ("Are repo policies audited regularly for compliance?", 7.0),
    ("Are security issues in repos tracked and remediated systematically?", 9.0),
    ("Are repository metrics (PR throughput, reviewer load) used for process improvement?", 4.0),
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
    
    # Create tool-specific pillar with importance-based scoring
    # Calculate total importance to distribute 100 points proportionally
    total_importance = sum(importance for _, importance in tool_questions)
    
    tool_pillar_questions = [
        Question(
            id=f"{tool.value}_{i+1}",
            text=question_text,
            max_score=round((importance / total_importance) * 100.0, 2),
            importance=importance
        )
        for i, (question_text, importance) in enumerate(tool_questions)
    ]
    
    # Adjust last question to ensure total is exactly 100 points
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

