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


@dataclass
class Pillar:
    """Scoring pillar with questions"""
    name: str
    total_weight: float
    questions: List[Question]


@dataclass
class FollowUpQuestion:
    """Follow-up question triggered conditionally"""
    id: str
    text: str
    max_score: float
    trigger_classifications: List[str]  # e.g., ["partial", "no"]
    base_question_id: str  # ID of the question that triggers this


# Answer classification mappings
ANSWER_MAPPING = {
    "yes": 1.0,
    "partial": 0.5,
    "no": 0.0,
    "unsure": 0.25,
}

# System prompt for Ollama
SYSTEM_PROMPT = """You are a software governance assessor.
Interpret user answers as: yes, partial, no, or unsure.
Do not calculate scores.
Do not explain scoring unless asked.
Be concise."""

# Classification prompt template
CLASSIFICATION_PROMPT = """Question:
"{question}"

User answer:
"{answer}"

Classify the answer into ONE category:

YES - Affirmative responses:
  Examples: yes, yeah, yep, definitely, absolutely, correct, true, implemented, we have it

PARTIAL - Partially implemented or conditional:
  Examples: partially, somewhat, kinda, sort of, maybe, sometimes, mostly, "yes but...", "working on it", "depends", "some teams do"

NO - Negative responses or not implemented:
  Examples: no, nope, not yet, haven't, don't have, not implemented, removed, "used to but not anymore"

UNSURE - Uncertain or don't know:
  Examples: idk, don't know, not sure, unsure, dunno, unclear, "...", "hmm", no clear answer

Return ONLY one word: yes, partial, no, or unsure"""

# Follow-up decision prompt for adaptive questioning
FOLLOW_UP_DECISION_PROMPT = """Based on the user's answer to the previous question, decide if a follow-up question would provide valuable clarification.

Original Question:
"{original_question}"

User's Answer:
"{user_answer}"

Classification: {classification}

Proposed Follow-up Question:
"{follow_up_question}"

Should this follow-up be asked? Consider:
- If answer was clear and complete, skip follow-up
- If answer was vague or partial, follow-up adds value
- If user already addressed the follow-up topic, skip it

Respond with ONLY: yes or no"""


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


# Follow-up questions configuration (GitHub example - expand for other tools)
# Maps base question ID -> list of follow-up questions
FOLLOW_UP_QUESTIONS = {
    # CI/CD related follow-up
    "github_9": [
        FollowUpQuestion(
            id="github_9_followup_1",
            text="Does the pipeline run automatically on all pull requests before merge?",
            max_score=2.0,
            trigger_classifications=["partial"],
            base_question_id="github_9"
        )
    ],
    # Branch protection follow-up
    "github_2": [
        FollowUpQuestion(
            id="github_2_followup_1",
            text="Are these protections enforced consistently across all critical branches (main, develop, release)?",
            max_score=2.0,
            trigger_classifications=["partial"],
            base_question_id="github_2"
        )
    ],
    # Secret scanning follow-up
    "github_6": [
        FollowUpQuestion(
            id="github_6_followup_1",
            text="Are developers notified immediately when secrets are detected, and is remediation tracked?",
            max_score=2.0,
            trigger_classifications=["partial", "no"],
            base_question_id="github_6"
        )
    ],
    # Repository structure follow-up
    "github_8": [
        FollowUpQuestion(
            id="github_8_followup_1",
            text="Is the naming convention documented and enforced through automation or policies?",
            max_score=2.0,
            trigger_classifications=["partial"],
            base_question_id="github_8"
        )
    ],
    # Security alerts follow-up
    "github_14": [
        FollowUpQuestion(
            id="github_14_followup_1",
            text="What is the average time to remediate critical security alerts in your repositories?",
            max_score=2.0,
            trigger_classifications=["partial"],
            base_question_id="github_14"
        )
    ],
}


def get_all_questions(pillars: Dict[str, Pillar]) -> List[tuple[str, Question, str]]:
    """Get all questions with their pillar context"""
    questions = []
    for pillar_id, pillar in pillars.items():
        for question in pillar.questions:
            questions.append((pillar_id, question, pillar.name))
    return questions


def get_follow_up_questions(base_question_id: str, classification: str) -> List[FollowUpQuestion]:
    """Get applicable follow-up questions based on classification"""
    follow_ups = FOLLOW_UP_QUESTIONS.get(base_question_id, [])
    return [
        fq for fq in follow_ups
        if classification in fq.trigger_classifications
    ]

