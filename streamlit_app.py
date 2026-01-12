"""
Professional Streamlit Frontend for Repository Scorer
Modern, responsive UI with real-time scoring and visualization
"""

import streamlit as st
import asyncio
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Optional
import pandas as pd

# Add src directory to path
src_path = Path(__file__).resolve().parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from repo_scorer.orchestrator import AssessmentOrchestrator
from repo_scorer.config import RepositoryTool


# Page configuration
st.set_page_config(
    page_title="Repository Quality Scorer | AI-Powered Assessment Platform",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Repository Quality Scorer - Professional assessment tool powered by local AI (Ollama). No data leaves your machine."
    }
)

# Custom CSS for professional look
st.markdown("""
<style>
    /* Main background and colors */
    .main {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e293b 100%);
        background-attachment: fixed;
    }
    
    .stApp {
        background: transparent;
    }
    
    /* Content container */
    .block-container {
        padding: 3rem 4rem;
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        margin: 2rem auto;
        max-width: 1400px;
    }
    
    /* Headers */
    h1 {
        color: #1e293b;
        font-weight: 700;
        font-size: 2.8rem !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
        letter-spacing: -0.02em;
    }
    
    h2 {
        color: #334155;
        font-weight: 700;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 0.75rem;
        margin-top: 2.5rem !important;
        font-size: 1.8rem !important;
    }
    
    h3 {
        color: #475569;
        font-weight: 600;
        font-size: 1.3rem !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: #1e40af;
        color: white;
        border: none;
        padding: 0.875rem 2.5rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(30, 64, 175, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .stButton > button:hover {
        background: #1e3a8a;
        box-shadow: 0 4px 12px rgba(30, 64, 175, 0.4);
        transform: translateY(-1px);
    }
    
    /* Radio buttons */
    .stRadio > label {
        font-weight: 600;
        color: #1e293b;
        font-size: 1.1rem;
        margin-bottom: 1rem;
    }
    
    .stRadio [role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 2rem;
        justify-content: center;
        margin-top: 1rem;
    }
    
    .stRadio [role="radio"] {
        background: #f8fafc;
        border: 3px solid #cbd5e1;
        border-radius: 8px;
        padding: 1.25rem 4rem;
        font-size: 1.3rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        min-width: 150px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stRadio [role="radio"]:hover {
        background: #e0e7ff;
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    .stRadio [role="radio"][aria-checked="true"] {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        border-color: #1e40af;
        color: white;
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(30, 64, 175, 0.4);
    }
    
    .stRadio [role="radio"] > div:first-child {
        display: none;
    }
    
    .stRadio label[data-baseweb="radio"] {
        background: #f8fafc;
        border: 3px solid #cbd5e1;
        border-radius: 8px;
        padding: 1.25rem 4rem;
        font-size: 1.3rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        min-width: 150px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stRadio label[data-baseweb="radio"]:hover {
        background: #e0e7ff;
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    /* Selected state for radio button label */
    .stRadio input[type="radio"]:checked + div {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%) !important;
        border-color: #1e40af !important;
        color: white !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(30, 64, 175, 0.4) !important;
    }
    
    .stRadio input[type="radio"]:checked ~ label {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%) !important;
        border-color: #1e40af !important;
        color: white !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(30, 64, 175, 0.4) !important;
    }
    
    .stRadio div[data-baseweb="radio"] input:checked ~ div {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%) !important;
        border-color: #1e40af !important;
        color: white !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(30, 64, 175, 0.4) !important;
    }
    
    .stRadio label[data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    
    /* Additional targeting for Streamlit's radio button structure */
    .stRadio [data-testid="stMarkdownContainer"] + div > div > div {
        display: flex;
        justify-content: center;
        gap: 2rem;
    }
    
    .stRadio [data-testid="stMarkdownContainer"] + div > div > div > label {
        background: #f8fafc;
        border: 3px solid #cbd5e1;
        border-radius: 8px;
        padding: 1.25rem 4rem;
        font-size: 1.3rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        min-width: 150px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stRadio [data-testid="stMarkdownContainer"] + div > div > div > label:has(input:checked) {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        border-color: #059669 !important;
        color: white !important;
        transform: scale(1.08) !important;
        box-shadow: 0 8px 20px rgba(5, 150, 105, 0.5) !important;
    }
    
    .stRadio [data-testid="stMarkdownContainer"] + div > div > div > label:hover {
        background: #e0e7ff;
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
        display: none !important;
    }
    
    /* Text input */
    .stTextArea textarea {
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        font-size: 1rem;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e40af;
    }
    
    /* Info boxes */
    .stAlert {
        border-radius: 6px;
        border-left: 4px solid #1e40af;
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #0f172a;
    }
    
    .css-1d391kg p, [data-testid="stSidebar"] p {
        color: #e2e8f0;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #f1f5f9;
    }
    
    /* Score badge */
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        border-radius: 50px;
        font-weight: 700;
        font-size: 1.2rem;
        margin: 0.5rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    
    .score-excellent {
        background: #059669;
        color: white;
    }
    
    .score-good {
        background: #0284c7;
        color: white;
    }
    
    .score-fair {
        background: #ea580c;
        color: white;
    }
    
    .score-poor {
        background: #dc2626;
        color: white;
    }
    
    /* Question card */
    .question-card {
        background: #f8fafc;
        border-radius: 8px;
        padding: 2rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin: 1.5rem 0;
        border-left: 4px solid #1e40af;
        border: 1px solid #e2e8f0;
    }
    
    /* Importance indicator */
    .importance-indicator {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 500;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    if "stage" not in st.session_state:
        st.session_state.stage = "welcome"  # welcome, assessment, results
    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None
    if "current_question_idx" not in st.session_state:
        st.session_state.current_question_idx = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "results" not in st.session_state:
        st.session_state.results = None
    if "system_ready" not in st.session_state:
        st.session_state.system_ready = False


def get_score_class(score: float) -> str:
    """Get CSS class based on score"""
    if score >= 80:
        return "score-excellent"
    elif score >= 60:
        return "score-good"
    elif score >= 40:
        return "score-fair"
    else:
        return "score-poor"


def get_score_label(score: float) -> str:
    """Get text label based on score"""
    if score >= 80:
        return "EXCELLENT"
    elif score >= 60:
        return "GOOD"
    elif score >= 40:
        return "FAIR"
    else:
        return "NEEDS IMPROVEMENT"


def render_welcome_page():
    """Render welcome page with tool selection"""
    st.markdown("# Repository Quality Scorer")
    st.markdown("### Intelligent Assessment Platform for Development Excellence")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style='background: #f8fafc; padding: 2.5rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #e2e8f0;'>
            <h3 style='margin-top: 0; color: #1e293b; font-weight: 700;'>Overview</h3>
            <p style='font-size: 1.05rem; line-height: 1.8; color: #475569;'>
                Our AI-powered platform conducts comprehensive assessments of repository 
                governance practices. Receive a detailed score out of <strong>100</strong> 
                based on industry-leading best practices and standards.
            </p>
            <h3 style='color: #1e293b; font-weight: 700; margin-top: 1.5rem;'>Key Capabilities</h3>
            <ul style='font-size: 1.05rem; line-height: 1.8; color: #475569; margin-bottom: 0;'>
                <li><strong>AI-Driven Analysis:</strong> Advanced natural language processing</li>
                <li><strong>Intelligent Weighting:</strong> Critical practices prioritized appropriately</li>
                <li><strong>Multi-Platform Support:</strong> GitHub, GitLab, Azure DevOps</li>
                <li><strong>Actionable Insights:</strong> Comprehensive governance pillar breakdown</li>
                <li><strong>Privacy-First:</strong> All processing performed locally</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #f8fafc; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;'>
            <h4 style='color: #1e293b; text-align: center; font-weight: 700; font-size: 1.3rem; margin-bottom: 1.5rem;'>Assessment Features</h4>
            <ul style='font-size: 1.05rem; line-height: 1.8; color: #475569; list-style-type: none; padding-left: 0;'>
                <li style='margin-bottom: 0.75rem;'>✓ <strong>Comprehensive Evaluation</strong> across 5 key pillars</li>
                <li style='margin-bottom: 0.75rem;'>✓ <strong>Binary Assessment</strong> for clear pass/fail criteria</li>
                <li style='margin-bottom: 0.75rem;'>✓ <strong>Intelligent Scoring</strong> with importance weighting</li>
                <li style='margin-bottom: 0.75rem;'>✓ <strong>Visual Reports</strong> with actionable insights</li>
                <li style='margin-bottom: 0.75rem;'>✓ <strong>Real-time Feedback</strong> throughout assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("## Select Your Repository Platform")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("GitHub", width="stretch", key="github_btn"):
            start_assessment(RepositoryTool.GITHUB)
    
    with col2:
        if st.button("GitLab", width="stretch", key="gitlab_btn"):
            start_assessment(RepositoryTool.GITLAB)
    
    with col3:
        if st.button("Azure DevOps", width="stretch", key="azure_btn"):
            start_assessment(RepositoryTool.AZURE_DEVOPS)
    
    st.markdown("---")
    
    # Footer with additional information
    st.markdown("""
    <div style='background: #f8fafc; padding: 2rem; border-radius: 8px; margin-top: 2rem; border: 1px solid #e2e8f0;'>
        <h3 style='color: #1e293b; margin-top: 0;'>Quick Start Guide</h3>
        <ol style='color: #475569; line-height: 1.8;'>
            <li>Ensure <strong>Ollama is running</strong> on your machine</li>
            <li>Select your repository platform above</li>
            <li>Answer questions with simple <strong>YES/NO</strong> responses</li>
            <li>Receive comprehensive assessment with detailed breakdown</li>
            <li>Export results as JSON for record-keeping</li>
        </ol>
        <p style='margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 0.9rem;'>
            🔒 <strong>100% Local Processing</strong> - All AI processing happens on your machine. No data is sent to external servers.
        </p>
    </div>
    """, unsafe_allow_html=True)


def start_assessment(tool: RepositoryTool):
    """Initialize assessment with selected tool"""
    st.session_state.stage = "initializing"
    st.session_state.selected_tool = tool
    st.rerun()


def check_system_readiness():
    """Check if Ollama is ready and initialize orchestrator"""
    if st.session_state.orchestrator is None:
        st.session_state.orchestrator = AssessmentOrchestrator(
            tool=st.session_state.selected_tool
        )
    
    # Run async check with proper event loop management
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    is_ready, message = loop.run_until_complete(
        st.session_state.orchestrator.check_readiness()
    )
    # Don't close the loop
    
    return is_ready, message


def render_assessment_page():
    """Render the assessment question page"""
    orchestrator = st.session_state.orchestrator
    questions = orchestrator.questions
    current_idx = st.session_state.current_question_idx
    
    if current_idx >= len(questions):
        # Assessment complete
        finalize_assessment()
        return
    
    pillar_id, question, pillar_name = questions[current_idx]
    
    # Score importance on-demand before displaying question
    if question.id not in orchestrator.scored_questions:
        with st.spinner(f"🤖 AI is evaluating this question's importance..."):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(orchestrator.score_question_importance(question.id))
    
    # Progress bar
    progress = (current_idx + 1) / len(questions)
    st.progress(progress)
    st.markdown(f"""<div style='text-align: center; color: #64748b; font-weight: 600; margin: 0.5rem 0 2rem 0;'>
        Question {current_idx + 1} of {len(questions)}
    </div>""", unsafe_allow_html=True)
    
    # Pillar badge
    st.markdown(f"""
    <div style='text-align: center; margin: 1.5rem 0;'>
        <span style='background: #1e40af; 
                     color: white; padding: 0.6rem 2rem; border-radius: 6px; 
                     font-weight: 600; font-size: 1.05rem; text-transform: uppercase;
                     letter-spacing: 0.05em;'>
            {pillar_name}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Question card - with priority, impact, and score displayed
    importance_level = "CRITICAL" if question.importance >= 8 else "HIGH" if question.importance >= 6 else "MEDIUM" if question.importance >= 4 else "STANDARD"
    importance_color = "#dc2626" if question.importance >= 8 else "#ea580c" if question.importance >= 6 else "#0284c7" if question.importance >= 4 else "#64748b"
    
    st.markdown(f"""
    <div class='question-card'>
        <h3 style='margin-top: 0; color: #1e293b; line-height: 1.4;'>{question.text}</h3>
        <div style='display: flex; justify-content: space-between; align-items: center; 
                    margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;'>
            <div class='importance-indicator'>
                <span style='background: {importance_color}; color: white; padding: 0.25rem 0.75rem; 
                             border-radius: 4px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>
                    {importance_level} PRIORITY
                </span>
            </div>
            <div style='color: #1e40af; font-weight: 700; font-size: 1.2rem;'>
                {question.max_score:.1f} pts
            </div>
        </div>
        <div style='margin: 1rem 0 0 0; padding: 0.75rem 1rem; background: #f1f5f9; border-radius: 6px; border-left: 3px solid #1e40af;'>
            <p style='margin: 0; color: #475569; font-size: 0.9rem;'>
                 <strong>Tip:</strong> Answer based on your current repository practices.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Answer input - Clean Yes/No selection
    st.markdown("### Response")
    st.markdown("<div style='text-align: center; margin: 2rem 0;'>", unsafe_allow_html=True)
    
    # Create a clean radio button selection
    answer = st.radio(
        "Select your answer:",
        options=["YES", "NO"],
        key=f"answer_{current_idx}",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection, forces user to choose
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_idx > 0:
            if st.button("← Previous", width="stretch"):
                st.session_state.current_question_idx -= 1
                st.rerun()
    
    with col3:
        if st.button("Next →" if current_idx < len(questions) - 1 else "Complete Assessment", 
                    width="stretch", type="primary"):
            if answer is not None:
                # Process answer
                process_answer(question.id, answer)
                st.session_state.current_question_idx += 1
                st.rerun()
            else:
                st.error("Please select YES or NO before proceeding.")
    
    # Sidebar with progress
    with st.sidebar:
        st.markdown("### Assessment Progress")
        st.metric("Questions Answered", f"{current_idx}/{len(questions)}")
        st.metric("Completion", f"{int(progress * 100)}%")
        
        if st.session_state.answers:
            st.markdown("---")
            st.markdown("### Recent Responses")
            recent = list(st.session_state.answers.items())[-3:]
            for q_id, result in recent:
                status = "Pass" if result["classification"] == "yes" else "Fail" if result["classification"] == "no" else "Partial"
                st.markdown(f"**{status}**: {result['score']:.1f} pts")


def process_answer(question_id: str, answer: str):
    """Process user answer and get score - simplified without LLM classification"""
    orchestrator = st.session_state.orchestrator
    
    # Convert user's YES/NO directly to classification
    classification = "yes" if answer.upper() == "YES" else "no"
    
    # Find the question to get max score
    question_data = None
    for pid, q, pname in orchestrator.questions:
        if q.id == question_id:
            question_data = q
            break
    
    if not question_data:
        raise ValueError(f"Question {question_id} not found")
    
    # Calculate score directly: YES = full score, NO = 0
    score_earned = question_data.max_score if classification == "yes" else 0.0
    
    # Store score
    orchestrator.question_scores[question_id] = score_earned
    
    # Store result
    st.session_state.answers[question_id] = {
        "answer": answer,
        "classification": classification,
        "score": score_earned
    }


def finalize_assessment():
    """Calculate final results and show results page - simplified without LLM processing"""
    orchestrator = st.session_state.orchestrator
    
    # Normalize scores to sum to 100 points based on importance weights
    orchestrator.normalize_question_scores()
    
    # Recalculate earned scores based on the normalized max_scores
    # (Since max_scores changed after normalization, we need to recalculate earned points)
    for question_id, answer_data in st.session_state.answers.items():
        # Find the question to get the NEW normalized max_score
        for pid, q, pname in orchestrator.questions:
            if q.id == question_id:
                # Recalculate score: YES = full normalized score, NO = 0
                classification = answer_data["classification"]
                score_earned = q.max_score if classification == "yes" else 0.0
                # Update stored scores with normalized values
                orchestrator.question_scores[question_id] = score_earned
                answer_data["score"] = score_earned
                break
    
    # Calculate pillar breakdown from updated scores
    pillar_questions = {
        pillar.name: [(q.id, q.max_score) for q in pillar.questions]
        for pillar in orchestrator.pillars.values()
    }
    
    breakdown = {}
    for pillar_name, questions in pillar_questions.items():
        earned = sum(orchestrator.question_scores.get(q_id, 0.0) for q_id, _ in questions)
        max_score = sum(max_s for _, max_s in questions)
        breakdown[pillar_name] = (earned, max_score)
    
    # Calculate final score (sum of earned points, which should now properly reflect the 100-point scale)
    total_earned = sum(orchestrator.question_scores.values())
    final_score = total_earned  # Already out of 100 after normalization
    
    # Create question results from stored answers
    question_results = []
    for question_id, answer_data in st.session_state.answers.items():
        # Find question details
        for pid, q, pname in orchestrator.questions:
            if q.id == question_id:
                from repo_scorer.models import QuestionResult
                result = QuestionResult(
                    question_id=question_id,
                    question_text=q.text,
                    user_answer=answer_data["answer"],
                    classification=answer_data["classification"],
                    score_earned=answer_data["score"],
                    max_score=q.max_score
                )
                question_results.append(result)
                break
    
    # Create assessment result
    from repo_scorer.models import AssessmentResult
    results = AssessmentResult(
        final_score=round(final_score, 2),
        breakdown=breakdown,
        question_results=question_results,
        summary=f"Assessment complete with a score of {final_score:.1f}/100. Review detailed breakdown below."
    )
    
    st.session_state.results = results
    st.session_state.stage = "results"
    st.rerun()


def render_results_page():
    """Render comprehensive results page"""
    results = st.session_state.results
    
    st.markdown("# Assessment Complete")
    st.markdown("---")
    
    # Overall score
    score = results.final_score
    score_class = get_score_class(score)
    score_label = get_score_label(score)
    
    st.markdown(f"""
    <div style='text-align: center; padding: 4rem 2rem; background: #f8fafc; 
                border-radius: 8px; margin: 2rem 0; border: 1px solid #e2e8f0;'>
        <h2 style='margin: 0; color: #1e293b; border: none; font-size: 1.8rem; text-transform: uppercase; letter-spacing: 0.05em;'>Repository Quality Score</h2>
        <div class='score-badge {score_class}' style='font-size: 4rem; margin: 2rem auto; padding: 2rem 3rem; border-radius: 8px; display: inline-block; font-weight: 700;'>
            {score:.1f} <span style='font-size: 2rem; opacity: 0.8;'>/ 100</span>
        </div>
        <div style='background: white; padding: 1rem 2rem; border-radius: 6px; display: inline-block; margin-top: 1rem; border: 1px solid #e2e8f0;'>
            <span style='font-size: 1.3rem; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;'>{score_label}</span>
        </div>
        <p style='font-size: 1.1rem; color: #64748b; margin-top: 1.5rem; max-width: 600px; margin-left: auto; margin-right: auto;'>
            {get_score_description(score)}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Pillar breakdown
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("## Pillar Breakdown")
        render_pillar_chart(results.breakdown)
    
    with col2:
        st.markdown("## Overall Performance")
        render_gauge_chart(score)
    
    # Detailed breakdown
    st.markdown("---")
    st.markdown("## Detailed Analysis by Pillar")
    
    render_detailed_breakdown(results)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("New Assessment", width="stretch"):
            reset_assessment()
            st.rerun()
    
    with col2:
        if st.button("Export Results (JSON)", width="stretch"):
            export_results_json()
    
    with col3:
        if st.button("View Summary", width="stretch"):
            show_summary()


def get_score_description(score: float) -> str:
    """Get description based on score"""
    if score >= 80:
        return "Excellent performance. Your repository demonstrates strong adherence to industry best practices."
    elif score >= 60:
        return "Good foundation established. Continue refining practices for optimal governance."
    elif score >= 40:
        return "Moderate implementation. Consider prioritizing critical governance practices."
    else:
        return "Significant improvement needed. Focus on establishing fundamental practices."


def render_pillar_chart(breakdown: Dict):
    """Render horizontal bar chart for pillar breakdown"""
    pillars = list(breakdown.keys())
    earned = [breakdown[p][0] for p in pillars]
    max_scores = [breakdown[p][1] for p in pillars]
    percentages = [(e/m)*100 if m > 0 else 0 for e, m in zip(earned, max_scores)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=pillars,
        x=earned,
        name='Earned',
        orientation='h',
        marker=dict(
            color='#1e40af',
            line=dict(color='#1e3a8a', width=2)
        ),
        text=[f"{e:.1f}/{m:.1f}" for e, m in zip(earned, max_scores)],
        textposition='inside',
        textfont=dict(color='white', size=12, family='Arial', weight='bold'),
        hovertemplate='<b>%{y}</b><br>Earned: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12, color='#2d3748', family='Arial'),
        xaxis=dict(
            title="Points",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            range=[0, max(max_scores) * 1.1]
        ),
        yaxis=dict(
            title="",
            showgrid=False
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig, width="stretch")


def render_gauge_chart(score: float):
    """Render gauge chart for overall score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Quality Score", 'font': {'size': 20, 'color': '#1e293b', 'family': 'Arial'}},
        delta={'reference': 70, 'increasing': {'color': "#059669"}, 'decreasing': {'color': "#dc2626"}},
        gauge={
            'axis': {'range': [None, 100], 'tickwidth': 2, 'tickcolor': "#1e293b"},
            'bar': {'color': "#1e40af", 'thickness': 0.75},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#cbd5e1",
            'steps': [
                {'range': [0, 40], 'color': '#fee2e2'},
                {'range': [40, 60], 'color': '#fed7aa'},
                {'range': [60, 80], 'color': '#dbeafe'},
                {'range': [80, 100], 'color': '#d1fae5'}
            ],
            'threshold': {
                'line': {'color': "#1e293b", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': "#2d3748", 'family': "Arial"}
    )
    
    st.plotly_chart(fig, width="stretch")


def render_detailed_breakdown(results):
    """Render detailed question-by-question breakdown"""
    # Group by pillar and deduplicate questions by ID (keep only the latest)
    pillar_results = {}
    seen_questions = {}  # Track latest result for each question_id
    
    # First pass: deduplicate by keeping only the last occurrence of each question
    for qr in results.question_results:
        seen_questions[qr.question_id] = qr
    
    # Second pass: group by pillar using deduplicated results
    for qr in seen_questions.values():
        # Find pillar name from orchestrator
        pillar_name = None
        for pid, q, pname in st.session_state.orchestrator.questions:
            if q.id == qr.question_id:
                pillar_name = pname
                break
        
        if pillar_name:
            if pillar_name not in pillar_results:
                pillar_results[pillar_name] = []
            pillar_results[pillar_name].append(qr)
    
    # Render each pillar
    for pillar_name, questions in pillar_results.items():
        with st.expander(f"{pillar_name}", expanded=False):
            for qr in questions:
                # Get question details for importance/priority display
                question_obj = None
                for pid, q, pname in st.session_state.orchestrator.questions:
                    if q.id == qr.question_id:
                        question_obj = q
                        break
                
                classification_status = {
                    "yes": ("Pass", "#059669"),
                    "no": ("Fail", "#dc2626"),
                    "unsure": ("Partial", "#ea580c")
                }
                
                status, color = classification_status.get(qr.classification, ("Unknown", "#64748b"))
                percentage = (qr.score_earned / qr.max_score * 100) if qr.max_score > 0 else 0
                
                # Importance display
                importance_level = "Critical" if question_obj and question_obj.importance >= 8 else "High" if question_obj and question_obj.importance >= 6 else "Medium" if question_obj and question_obj.importance >= 4 else "Standard"
                importance_color = "#dc2626" if question_obj and question_obj.importance >= 8 else "#ea580c" if question_obj and question_obj.importance >= 6 else "#0284c7" if question_obj and question_obj.importance >= 4 else "#64748b"
                
                st.markdown(f"""
                <div style='background: #f8fafc; padding: 1.5rem; border-radius: 8px; 
                            margin: 1rem 0; border-left: 4px solid {color}; border: 1px solid #e2e8f0;'>
                    <div style='display: flex; justify-content: space-between; align-items: flex-start; gap: 1.5rem;'>
                        <div style='flex: 1; max-width: calc(100% - 140px);'>
                            <div style='margin-bottom: 0.75rem; display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center;'>
                                <span style='background: {color}; color: white; padding: 0.25rem 0.75rem; 
                                             border-radius: 4px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; white-space: nowrap;'>
                                    {status}
                                </span>
                                <span style='background: {importance_color}; color: white; padding: 0.25rem 0.75rem; 
                                             border-radius: 4px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; white-space: nowrap;'>
                                    {importance_level} Priority
                                </span>
                            </div>
                            <strong style='color: #1e293b; font-size: 1.05rem; display: block; margin-bottom: 0.5rem;'>{qr.question_text}</strong>
                            <p style='margin: 0.5rem 0 0 0; color: #64748b; font-size: 0.95rem;'>
                                Response: "{qr.user_answer}"
                            </p>
                        </div>
                        <div style='text-align: right; min-width: 100px; flex-shrink: 0;'>
                            <div style='font-size: 1.8rem; font-weight: 700; color: #1e40af;'>
                                {qr.score_earned:.1f}
                            </div>
                            <div style='font-size: 0.9rem; color: #64748b;'>
                                of {qr.max_score:.1f}
                            </div>
                            <div style='font-size: 0.9rem; color: #475569; font-weight: 600; margin-top: 0.25rem;'>
                                {percentage:.0f}%
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)


def export_results_json():
    """Export results as JSON"""
    import json
    results = st.session_state.results
    
    export_data = {
        "final_score": results.final_score,
        "breakdown": {k: {"earned": v[0], "max": v[1]} for k, v in results.breakdown.items()},
        "questions": [
            {
                "question": qr.question_text,
                "answer": qr.user_answer,
                "classification": qr.classification,
                "score_earned": qr.score_earned,
                "max_score": qr.max_score
            }
            for qr in results.question_results
        ]
    }
    
    json_str = json.dumps(export_data, indent=2)
    st.download_button(
        label="Download JSON Report",
        data=json_str,
        file_name=f"repo_assessment_{st.session_state.selected_tool.value}.json",
        mime="application/json"
    )


def show_summary():
    """Show AI-generated summary"""
    results = st.session_state.results
    if results.summary:
        st.markdown("### Executive Summary")
        st.info(results.summary)
    else:
        st.warning("Summary not available")


def reset_assessment():
    """Reset all session state"""
    st.session_state.clear()
    init_session_state()


def main():
    """Main application entry point"""
    init_session_state()
    
    # Sidebar always visible
    with st.sidebar:
        st.markdown("""<div style='text-align: center; padding: 1rem 0;'>
            <h1 style='color: #1e40af; margin: 0; font-size: 3rem;'>✔️</h1>
            <h2 style='margin: 0.5rem 0 0 0; font-size: 1.5rem;'>Repository Scorer</h2>
            <p style='color: #64748b; font-size: 0.9rem; margin: 0.25rem 0 0 0;'>AI-Powered Assessment</p>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")
        
        if st.session_state.stage != "welcome":
            st.markdown(f"**Platform:** {st.session_state.selected_tool.value.replace('_', ' ').title()}")
            st.markdown("---")
        
        st.markdown("### System Status")
        st.markdown("✅ Streamlit Active")
        
        if st.session_state.orchestrator:
            st.markdown("✅ Orchestrator Ready")
        
        st.markdown("---")
        st.markdown("### System Requirements")
        
        # Display actual model being used
        model_name = "Not loaded"
        if st.session_state.orchestrator:
            model_name = st.session_state.orchestrator.ollama.model
        
        st.markdown(f"""
        <div style='color: white;'>
        <p style='margin: 0.25rem 0;'><strong>Ollama:</strong> Running locally</p>
        <p style='margin: 0.25rem 0;'><strong>Model:</strong> {model_name}</p>
        <p style='margin: 0.25rem 0;'><strong>Port:</strong> 11434</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        Professional tool for evaluating 
        repository governance, CI/CD, 
        testing, and code quality.
        
        🔒 **Privacy First**  
        All processing happens locally.
        """)
        
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.8rem;'>v1.0.0</p>", unsafe_allow_html=True)
    
    # Main content routing
    if st.session_state.stage == "welcome":
        render_welcome_page()
    
    elif st.session_state.stage == "initializing":
        st.markdown("# Initializing Assessment")
        st.markdown("---")
        
        with st.spinner("Checking system readiness..."):
            is_ready, message = check_system_readiness()
        
        if is_ready:
            st.success("✓ " + message)
            with st.spinner("AI is analyzing question importance... This may take a few minutes."):
                # The importance weighting is done in check_readiness
                pass
            st.success("✓ Question importance weights assigned")
            st.session_state.stage = "assessment"
            st.session_state.system_ready = True
            st.rerun()
        else:
            st.error("✗ " + message)
            st.info("Please ensure Ollama is running and the required model is available.")
            if st.button("Retry"):
                st.rerun()
            if st.button("Back to Home"):
                reset_assessment()
                st.rerun()
    
    elif st.session_state.stage == "assessment":
        render_assessment_page()
    
    elif st.session_state.stage == "results":
        render_results_page()


if __name__ == "__main__":
    main()
