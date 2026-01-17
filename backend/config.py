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
    pillar: str  # Pillar category this question belongs to


@dataclass
class Pillar:
    """Scoring pillar with questions"""
    name: str
    total_weight: float
    questions: List[Question]


# GitHub Questions with Manual Importance Scores and Pillar Categories
# Each tuple is (question_text, importance_score, pillar_category)
# Importance scale: 1-10 (1=low, 10=critical)
# Pillars: security, governance, code_review, repository_management, process_metrics
GITHUB_QUESTIONS = [
    ("Are repositories organized using organizations and teams, with role-based access instead of individual permissions?", 8.0, "governance"),
    ("Is branch protection enforced (mandatory PRs, minimum reviewers, status checks)?", 10.0, "code_review"),
    ("Are CODEOWNERS files used to automatically assign reviewers for critical paths?", 7.0, "code_review"),
    ("Are Pull Request templates standardized across repositories?", 5.0, "code_review"),
    ("Is signed commits or commit verification enforced?", 6.0, "security"),
    ("Are secrets prevented from being committed using GitHub secret scanning?", 10.0, "security"),
    ("Are repository visibility policies (public/internal/private) clearly defined and enforced?", 9.0, "governance"),
    ("Is repository naming and structure standardized across the organization?", 4.0, "repository_management"),
    ("Are GitHub Actions status checks mandatory before merge?", 8.0, "code_review"),
    ("Are stale branches automatically cleaned up after merge?", 3.0, "repository_management"),
    ("Is monorepo vs multirepo strategy clearly defined and documented?", 6.0, "repository_management"),
    ("Are forking policies clearly defined for internal and external contributors?", 5.0, "governance"),
    ("Is repository archival managed for inactive or deprecated projects?", 3.0, "repository_management"),
    ("Are security alerts (Dependabot, CodeQL) actively monitored and acted upon?", 9.0, "security"),
    ("Is repository activity (PR cycle time, merge frequency) measured and reviewed periodically?", 4.0, "process_metrics"),
]

# GitLab Questions with Manual Importance Scores and Pillar Categories
# Each tuple is (question_text, importance_score, pillar_category)
# Importance scale: 1-10 (1=low, 10=critical)
# Pillars: security, governance, code_review, repository_management, process_metrics
GITLAB_QUESTIONS = [
    ("Are repositories structured using groups and subgroups aligned to teams or products?", 7.0, "governance"),
    ("Is merge request approval rules enforced based on branch and code area?", 9.0, "code_review"),
    ("Are protected branches configured with restricted push and merge permissions?", 10.0, "code_review"),
    ("Are merge request templates standardized and mandatory?", 5.0, "code_review"),
    ("Is commit signing or verification enabled?", 6.0, "security"),
    ("Are push rules configured to prevent secrets, large files, or invalid commits?", 10.0, "security"),
    ("Are code owners defined using CODEOWNERS for approval routing?", 7.0, "code_review"),
    ("Are repository access levels (Guest, Reporter, Developer, Maintainer) clearly governed?", 8.0, "governance"),
    ("Are merge strategies (merge commit, squash, fast-forward) standardized?", 4.0, "repository_management"),
    ("Are inactive branches and repositories automatically identified and cleaned up?", 3.0, "repository_management"),
    ("Is monorepo vs multirepo guidance documented and followed?", 6.0, "repository_management"),
    ("Are fork workflows governed for internal and external contributions?", 5.0, "governance"),
    ("Are repository compliance checks enforced before merge?", 8.0, "security"),
    ("Are security scanning results reviewed before code promotion?", 9.0, "security"),
    ("Are repository KPIs (MR aging, review time, merge rate) tracked and improved?", 4.0, "process_metrics"),
]

# Azure DevOps Questions with Manual Importance Scores and Pillar Categories
# Each tuple is (question_text, importance_score, pillar_category)
# Importance scale: 1-10 (1=low, 10=critical)
# Pillars: security, governance, code_review, repository_management, process_metrics
AZURE_DEVOPS_QUESTIONS = [
    ("Are repositories organized using projects and teams aligned to delivery units?", 7.0, "governance"),
    ("Are branch policies enforced (minimum reviewers, build validation, comment resolution)?", 10.0, "code_review"),
    ("Are path-based policies used for critical code areas?", 8.0, "code_review"),
    ("Are pull request templates standardized?", 5.0, "code_review"),
    ("Is commit history hygiene maintained (squash/rebase strategies)?", 4.0, "repository_management"),
    ("Are service hooks or policies used to prevent secret leakage?", 10.0, "security"),
    ("Are repository permissions managed using Azure AD groups?", 8.0, "governance"),
    ("Are naming conventions enforced for repos and branches?", 3.0, "repository_management"),
    ("Are build validations mandatory before PR completion?", 9.0, "code_review"),
    ("Are stale branches periodically cleaned up?", 3.0, "repository_management"),
    ("Is there a defined repo strategy for microservices vs monoliths?", 6.0, "repository_management"),
    ("Are fork-based workflows governed for partners or vendors?", 5.0, "governance"),
    ("Are repo policies audited regularly for compliance?", 7.0, "security"),
    ("Are security issues in repos tracked and remediated systematically?", 9.0, "security"),
    ("Are repository metrics (PR throughput, reviewer load) used for process improvement?", 4.0, "process_metrics"),
]


# Pillar metadata
PILLAR_METADATA = {
    "security": {
        "name": "Security & Compliance",
        "description": "Security scanning, secrets management, and compliance checks"
    },
    "governance": {
        "name": "Governance & Access Control",
        "description": "Organizations, teams, permissions, and access policies"
    },
    "code_review": {
        "name": "Code Review & Quality",
        "description": "Pull requests, branch protection, and review processes"
    },
    "repository_management": {
        "name": "Repository Management",
        "description": "Repository structure, naming, cleanup, and organization"
    },
    "process_metrics": {
        "name": "Process & Metrics",
        "description": "KPIs, monitoring, and continuous improvement"
    }
}


def get_questions_for_tool(tool: RepositoryTool) -> Dict[str, Pillar]:
    """
    Get predefined questions for a specific repository tool, organized by pillars
    
    Args:
        tool: The repository tool (GitHub, GitLab, or Azure DevOps)
        
    Returns:
        Dictionary of pillar_id -> Pillar with questions
    """
    # Tool-specific questions
    tool_questions_map = {
        RepositoryTool.GITHUB: GITHUB_QUESTIONS,
        RepositoryTool.GITLAB: GITLAB_QUESTIONS,
        RepositoryTool.AZURE_DEVOPS: AZURE_DEVOPS_QUESTIONS,
    }
    
    tool_questions = tool_questions_map[tool]
    
    # Group questions by pillar
    pillar_groups = {}
    for i, (question_text, importance, pillar_category) in enumerate(tool_questions):
        if pillar_category not in pillar_groups:
            pillar_groups[pillar_category] = []
        pillar_groups[pillar_category].append((i, question_text, importance, pillar_category))
    
    # Calculate total importance to distribute 100 points proportionally
    total_importance = sum(importance for _, importance, _ in tool_questions)
    
    # Create pillars with questions
    pillars = {}
    for pillar_id, questions in pillar_groups.items():
        pillar_metadata = PILLAR_METADATA[pillar_id]
        
        pillar_questions = [
            Question(
                id=f"{tool.value}_{i+1}",
                text=question_text,
                max_score=round((importance / total_importance) * 100.0, 2),
                importance=importance,
                pillar=pillar_id
            )
            for i, question_text, importance, _ in questions
        ]
        
        # Calculate total weight for this pillar
        pillar_weight = sum(q.max_score for q in pillar_questions)
        
        pillars[pillar_id] = Pillar(
            name=pillar_metadata["name"],
            total_weight=round(pillar_weight, 2),
            questions=pillar_questions
        )
    
    # Adjust to ensure total is exactly 100 points
    total = sum(pillar.total_weight for pillar in pillars.values())
    if abs(total - 100.0) > 0.01:
        # Adjust the last question of the last pillar
        last_pillar = list(pillars.values())[-1]
        last_question = last_pillar.questions[-1]
        adjustment = 100.0 - total
        last_question.max_score = round(last_question.max_score + adjustment, 2)
        last_pillar.total_weight = round(last_pillar.total_weight + adjustment, 2)
    
    return pillars


def get_all_questions(pillars: Dict[str, Pillar]) -> List[tuple[str, Question, str]]:
    """Get all questions with their pillar context"""
    questions = []
    for pillar_id, pillar in pillars.items():
        for question in pillar.questions:
            questions.append((pillar_id, question, pillar.name))
    return questions

