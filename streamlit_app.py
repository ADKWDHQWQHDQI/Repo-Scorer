"""
Professional Streamlit Frontend for Repository Scorer
Modern, responsive UI with real-time scoring and visualization
"""

import streamlit as st
import asyncio
import sys
import html
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
        'About': "Repository Quality Scorer - Professional assessment tool powered by Azure OpenAI. Secure cloud-based AI analysis."
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
    
    /* Radio buttons - Professional YES/NO styling */
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
        border: 2px solid #cbd5e1;
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
    
    .stRadio [role="radio"] > div:first-child {
        display: none !important;
    }
    
    .stRadio [role="radio"]:hover {
        background: #dbeafe;
        border-color: #3b82f6;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
    }
    
    .stRadio [role="radio"][aria-checked="true"] {
        background: #dbeafe !important;
        border-color: #3b82f6 !important;
        color: #1e40af !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4) !important;
        font-weight: 800 !important;
    }
    
    .stRadio [role="radio"][aria-checked="true"] > div {
        background: transparent !important;
        border: none !important;
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


def get_or_create_event_loop():
    """Get or create event loop for async operations"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


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
    st.markdown("### AI-Powered Assessment Platform with Progressive Intelligence")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style='background: #f8fafc; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;'>
            <h4 style='color: #1e293b; text-align: center; font-weight: 700; font-size: 1.3rem; margin-bottom: 1.5rem;'>Platform Overview</h4>
            <p style='font-size: 1.05rem; line-height: 1.8; color: #475569;'>
                Our advanced AI platform conducts comprehensive assessments of repository 
                governance practices with <strong>real-time intelligent analysis</strong>. 
                Receive a detailed score out of <strong>100</strong> based on manually curated importance 
                weights for industry-leading best practices.
            </p>
            <h3 style='color: #1e293b; font-weight: 700; margin-top: 1.5rem;'>Advanced AI-Powered Features</h3>
            <ul style='font-size: 1.05rem; line-height: 1.8; color: #475569; margin-bottom: 0;'>
                <li><strong>Progressive AI Analysis:</strong> Real-time insights delivered as you answer each question</li>
                <li><strong>Intelligent Importance Weighting:</strong> Critical security and quality practices receive higher priority</li>
                <li><strong>Comprehensive Executive Summary:</strong> Professional report with strategic implementation roadmap</li>
                <li><strong>Strengths and Gaps Analysis:</strong> Clear identification of implemented practices and improvement opportunities</li>
                <li><strong>Secure Cloud AI:</strong> All AI processing via Azure OpenAI with enterprise-grade security</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #f8fafc; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;'>
            <h4 style='color: #1e293b; text-align: center; font-weight: 700; font-size: 1.3rem; margin-bottom: 1.5rem;'>Assessment Deliverables</h4>
            <ul style='font-size: 1.05rem; line-height: 1.8; color: #475569; list-style-type: none; padding-left: 0;'>
                <li style='margin-bottom: 0.75rem;'><strong>15 Questions</strong> tailored to your platform</li>
                <li style='margin-bottom: 0.75rem;'><strong>Real-time AI Insights</strong> for each response</li>
                <li style='margin-bottom: 0.75rem;'><strong>Intelligent Scoring</strong> based on importance weights</li>
                <li style='margin-bottom: 0.75rem;'><strong>Executive Summary</strong> with implementation roadmap</li>
                <li style='margin-bottom: 0.75rem;'><strong>Prioritized Recommendations</strong> by business impact</li>
                <li style='margin-bottom: 0.75rem;'><strong>Exportable Results</strong> in JSON format</li>
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
    
    # Scoring methodology explanation
    st.markdown("---")
    st.markdown("""
    <div style='background: #f8fafc; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0;'>
        <h4 style='color: #1e293b; text-align: center; font-weight: 700; font-size: 1.3rem; margin-bottom: 1.5rem;'>Intelligent Scoring Methodology</h4>
        <p style='color: #475569; font-size: 1.05rem; line-height: 1.8;'>
            Questions are <strong>manually weighted by importance</strong> to reflect their real-world impact on repository quality:
        </p>
        <ul style='color: #475569; font-size: 1rem; line-height: 1.8;'>
            <li><strong>Critical (9-10):</strong> Security vulnerabilities, branch protection, secret scanning (approximately 40% of total score)</li>
            <li><strong>High (7-8):</strong> Access control, code ownership, approval workflows (approximately 30% of total score)</li>
            <li><strong>Moderate (4-6):</strong> Templates, commit conventions, repository strategy (approximately 20% of total score)</li>
            <li><strong>Standard (1-3):</strong> Naming conventions, cleanup automation, metrics (approximately 10% of total score)</li>
        </ul>
        <p style='color: #475569; font-size: 0.95rem; font-style: italic; margin-bottom: 0;'>
            This weighting ensures that implementing critical security and quality practices has the most significant impact on your overall assessment score.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Footer with additional information
    st.markdown("""
    <div style='background: #f8fafc; padding: 2rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-top: 2rem;'>
        <h4 style='color: #1e293b; text-align: center; font-weight: 700; font-size: 1.3rem; margin-bottom: 1.5rem;'>Assessment Workflow</h4>
        <ol style='color: #475569; line-height: 2; font-size: 1.05rem;'>
            <li>Select your repository platform (GitHub, GitLab, or Azure DevOps)</li>
            <li>Answer <strong>15 curated questions</strong> with simple YES or NO responses</li>
            <li><strong>Azure OpenAI analyzes each answer</strong> in real-time</li>
            <li>Complete assessment to receive <strong>comprehensive AI-generated summary</strong></li>
            <li>Review <strong>strengths, gaps, and prioritized roadmap</strong> for improvement</li>
            <li>Export detailed results as JSON for documentation and tracking</li>
        </ol>
        <div style='background: white; padding: 1rem; border-radius: 6px; margin-top: 1rem; border-left: 4px solid #f59e0b;'>
            <p style='margin: 0; color: #1e293b; font-weight: 600;'>Important: Questions are weighted by importance. Critical security and governance practices have significantly higher impact on your final score.</p>
        </div>
    </div>
        <p style='margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 0.9rem;'>
            <strong>Security Notice:</strong> Azure OpenAI provides enterprise-grade security and compliance. Your data is processed securely in Microsoft's cloud infrastructure.
        </p>
    </div>
    """, unsafe_allow_html=True)


def start_assessment(tool: RepositoryTool):
    """Initialize assessment with selected tool"""
    st.session_state.stage = "initializing"
    st.session_state.selected_tool = tool
    st.rerun()


def check_system_readiness():
    """Check if Azure OpenAI is ready and initialize orchestrator"""
    if st.session_state.orchestrator is None:
        st.session_state.orchestrator = AssessmentOrchestrator(
            tool=st.session_state.selected_tool
        )
    
    loop = get_or_create_event_loop()
    is_ready, message = loop.run_until_complete(
        st.session_state.orchestrator.check_readiness()
    )
    return is_ready, message


def render_assessment_page():
    """Render the assessment question page"""
    orchestrator = st.session_state.orchestrator
    questions = orchestrator.questions
    current_idx = st.session_state.current_question_idx
    
    if current_idx >= len(questions):
        finalize_assessment()
        return
    
    if current_idx == 0 and not st.session_state.answers:
        st.info("**AI-Powered Assessment:** After each answer, our AI will analyze your response and provide professional insights. At the end, you'll receive a comprehensive executive summary with actionable recommendations.", icon="ℹ️")
    
    pillar_id, question, pillar_name = questions[current_idx]
    
    # Progress bar - based on actual answered questions
    answered_count = len(st.session_state.answers)
    total_questions = len(questions)
    progress = answered_count / total_questions if total_questions > 0 else 0
    
    st.progress(progress)
    st.markdown(f"""<div style='text-align: center; color: #64748b; font-weight: 600; margin: 0.5rem 0 2rem 0;'>
        Question {current_idx + 1} of {total_questions} | Answered: {answered_count}/{total_questions} ({int(progress * 100)}%)
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
    
    importance_level = "CRITICAL" if question.importance >= 8 else "HIGH" if question.importance >= 6 else "MEDIUM" if question.importance >= 4 else "STANDARD"
    importance_color = "#dc2626" if question.importance >= 8 else "#ea580c" if question.importance >= 6 else "#0284c7" if question.importance >= 4 else "#64748b"
    
    has_analysis = question.id in st.session_state.answers and 'analysis' in st.session_state.answers[question.id]
    analysis_badge = '<span style="background: #059669; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-left: 0.5rem;">AI ANALYZED</span>' if has_analysis else ""
    
    escaped_question_text = html.escape(question.text)
    
    # Question card - priority, impact, and score displayed (NO leading whitespace to avoid markdown code block)
    st.markdown(f"""<div class='question-card'>
<h3 style='margin-top: 0; color: #1e293b; line-height: 1.4;'>{escaped_question_text}</h3>
<div style='display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid #e2e8f0;'>
<div class='importance-indicator'>
<span style='background: {importance_color}; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600; text-transform: uppercase;'>{importance_level} PRIORITY</span>
{analysis_badge}
</div>
<div style='color: #1e40af; font-weight: 700; font-size: 1.2rem;'>{question.max_score:.1f} pts</div>
</div>
<div style='margin: 1rem 0 0 0; padding: 0.75rem 1rem; background: #f1f5f9; border-radius: 6px; border-left: 3px solid #1e40af;'>
<p style='margin: 0; color: #475569; font-size: 0.9rem;'><strong>Tip:</strong> Answer based on your current repository practices.</p>
</div>
</div>""", unsafe_allow_html=True)
    st.markdown("### Response")
    
    answer = st.radio(
        "Select your answer:",
        options=["YES", "NO"],
        key=f"answer_{current_idx}",
        horizontal=True,
        label_visibility="collapsed",
        index=None  # No default selection, forces user to choose
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_idx > 0:
            if st.button("Previous", width="stretch"):
                st.session_state.current_question_idx -= 1
                st.rerun()
    
    with col3:
        button_text = "Next" if current_idx < len(questions) - 1 else "Generate AI Summary"
        if st.button(button_text, width="stretch", type="primary"):
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
        st.metric("Questions Answered", f"{answered_count}/{total_questions}")
        st.metric("Completion", f"{int(progress * 100)}%")
        st.metric("Current Question", f"#{current_idx + 1}")
        
        # Show AI analysis status
        if st.session_state.answers:
            analyzed_count = sum(1 for ans in st.session_state.answers.values() if 'analysis' in ans)
            st.metric("AI Insights Generated", f"{analyzed_count}")
        
        if st.session_state.answers:
            st.markdown("---")
            st.markdown("### Recent Responses")
            recent = list(st.session_state.answers.items())[-3:]
            for q_id, result in recent:
                status = "Pass" if result["classification"] == "yes" else "Fail"
                has_analysis = " [AI]" if result.get('analysis') else ""
                st.markdown(f"**{status}**{has_analysis}: {result['score']:.1f} pts")


def process_answer(question_id: str, answer: str):
    """Process user answer, get score, and analyze with LLM"""
    orchestrator = st.session_state.orchestrator
    classification = "yes" if answer.upper() == "YES" else "no"
    
    question_data = None
    for pid, q, pname in orchestrator.questions:
        if q.id == question_id:
            question_data = q
            break
    
    if not question_data:
        raise ValueError(f"Question {question_id} not found")
    
    score_earned = question_data.max_score if classification == "yes" else 0.0
    orchestrator.question_scores[question_id] = score_earned
    
    with st.spinner("Analyzing your response..."):
        loop = get_or_create_event_loop()
        analysis = loop.run_until_complete(
            orchestrator.analyze_answer(
                question_id,
                question_data.text,
                answer,
                question_data.importance
            )
        )
    
    st.session_state.answers[question_id] = {
        "answer": answer,
        "classification": classification,
        "score": score_earned,
        "analysis": analysis  # Store LLM analysis
    }


def recompute_scores():
    """Recompute all scores from answers - single source of truth"""
    orchestrator = st.session_state.orchestrator
    orchestrator.question_scores.clear()
    
    for q_id, ans in st.session_state.answers.items():
        for _, q, _ in orchestrator.questions:
            if q.id == q_id:
                orchestrator.question_scores[q_id] = q.max_score if ans["classification"] == "yes" else 0.0
                break


def finalize_assessment():
    """Calculate final results, generate LLM summary, and show results page"""
    orchestrator = st.session_state.orchestrator
    recompute_scores()
    
    with st.spinner("Generating comprehensive assessment summary..."):
        loop = get_or_create_event_loop()
        llm_summary = loop.run_until_complete(
            orchestrator.generate_final_summary(st.session_state.answers)
        )
        st.session_state.llm_summary = llm_summary
    
    # Calculate pillar breakdown from scores
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
    """Render comprehensive results page with LLM-generated summary"""
    results = st.session_state.results
    
    st.markdown("# Assessment Complete")
    st.markdown("---")
    
    # Display LLM-generated comprehensive summary first
    if hasattr(st.session_state, 'llm_summary') and st.session_state.llm_summary:
        st.markdown("## AI-Powered Professional Assessment Summary")
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f0f9ff 0%, #f8fafc 100%); 
                    padding: 2rem; border-radius: 12px; margin: 2rem 0; 
                    border: 2px solid #3b82f6; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);'>
            <div style='color: #1e293b; font-size: 1.05rem; line-height: 1.8;'>
                {st.session_state.llm_summary.replace(chr(10), '<br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)
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
    
    # Show individual question insights with AI analysis
    st.markdown("---")
    st.markdown("## Individual Question Insights")
    
    render_question_insights()
    
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
    """Render horizontal bar chart for pillar breakdown - shows contribution to final 100-point score"""
    pillars = list(breakdown.keys())
    earned = [breakdown[p][0] for p in pillars]
    max_scores = [breakdown[p][1] for p in pillars]
    percentages = [(e/m)*100 if m > 0 else 0 for e, m in zip(earned, max_scores)]
    
    fig = go.Figure()
    
    # Add potential (max) bars first
    fig.add_trace(go.Bar(
        y=pillars,
        x=max_scores,
        name='Potential Impact',
        orientation='h',
        marker=dict(
            color='#e2e8f0',
            line=dict(color='#cbd5e1', width=1)
        ),
        text=[f"{m:.1f}" for m in max_scores],
        textposition='inside',
        textfont=dict(color='#64748b', size=11, family='Arial'),
        hovertemplate='<b>%{y}</b><br>Max Possible: %{x:.1f} pts<extra></extra>'
    ))
    
    # Add earned bars on top
    fig.add_trace(go.Bar(
        y=pillars,
        x=earned,
        name='Earned',
        orientation='h',
        marker=dict(
            color='#1e40af',
            line=dict(color='#1e3a8a', width=2)
        ),
        text=[f"{e:.1f}" for e in earned],
        textposition='inside',
        textfont=dict(color='white', size=12, family='Arial', weight='bold'),
        hovertemplate='<b>%{y}</b><br>Earned: %{x:.1f} pts<br>Percentage: %{customdata:.0f}%<extra></extra>',
        customdata=percentages
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12, color='#2d3748', family='Arial'),
        xaxis=dict(
            title="Contribution to Final Score (out of 100)",
            showgrid=True,
            gridcolor='rgba(0,0,0,0.05)',
            range=[0, max(max_scores) * 1.1]
        ),
        yaxis=dict(
            title="",
            showgrid=False
        ),
        barmode='overlay',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='center',
            x=0.5
        )
    )
    
    st.plotly_chart(fig, width="stretch")


def render_gauge_chart(score: float):
    """Render gauge chart for overall score"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall Quality Score", 'font': {'size': 20, 'color': '#1e293b', 'family': 'Arial'}},
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


def render_question_insights():
    """Render AI insights for each question grouped by YES/NO"""
    orchestrator = st.session_state.orchestrator
    answers = st.session_state.answers
    
    # Separate YES and NO answers
    yes_answers = []
    no_answers = []
    
    for question_id, answer_data in answers.items():
        # Find question
        for pid, q, pname in orchestrator.questions:
            if q.id == question_id:
                item = {
                    'question': q.text,
                    'answer': answer_data['answer'],
                    'importance': q.importance,
                    'analysis': answer_data.get('analysis', 'No analysis available')
                }
                if answer_data['classification'] == 'yes':
                    yes_answers.append(item)
                else:
                    no_answers.append(item)
                break
    
    # Sort by importance (highest first)
    yes_answers.sort(key=lambda x: x['importance'], reverse=True)
    no_answers.sort(key=lambda x: x['importance'], reverse=True)
    
    # Display YES answers (What you did well)
    if yes_answers:
        st.markdown("### What You're Doing Right")
        st.markdown("<p style='color: #64748b; margin-bottom: 1rem;'>These practices demonstrate your commitment to repository quality and governance.</p>", unsafe_allow_html=True)
        
        with st.expander(f"View {len(yes_answers)} Implemented Practices", expanded=False):
            for item in yes_answers:
                importance_badge = "Critical" if item['importance'] >= 9 else "High" if item['importance'] >= 7 else "Moderate" if item['importance'] >= 5 else "Standard"
                badge_color = "#dc2626" if item['importance'] >= 9 else "#ea580c" if item['importance'] >= 7 else "#0284c7" if item['importance'] >= 5 else "#64748b"
                st.markdown(f"""
                <div style='background: #f0fdf4; padding: 1.25rem; border-radius: 8px; 
                            margin: 1rem 0; border-left: 4px solid #059669; border: 1px solid #bbf7d0;'>
                    <div style='font-size: 0.85rem; color: {badge_color}; font-weight: 600; margin-bottom: 0.5rem;'>
                        {importance_badge} Priority
                    </div>
                    <strong style='color: #1e293b; font-size: 1rem; display: block; margin-bottom: 0.75rem;'>{item['question']}</strong>
                    <p style='margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6; font-style: italic;'>
                        {item['analysis']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # Display NO answers (Areas for improvement)
    if no_answers:
        st.markdown("### Areas for Improvement")
        st.markdown("<p style='color: #64748b; margin-bottom: 1rem;'>Implementing these practices will significantly enhance your repository governance.</p>", unsafe_allow_html=True)
        
        with st.expander(f"View {len(no_answers)} Improvement Opportunities", expanded=True):
            for item in no_answers:
                importance_badge = "Critical" if item['importance'] >= 9 else "High" if item['importance'] >= 7 else "Moderate" if item['importance'] >= 5 else "Standard"
                badge_color = "#dc2626" if item['importance'] >= 9 else "#ea580c" if item['importance'] >= 7 else "#0284c7" if item['importance'] >= 5 else "#64748b"
                st.markdown(f"""
                <div style='background: #fef2f2; padding: 1.25rem; border-radius: 8px; 
                            margin: 1rem 0; border-left: 4px solid #dc2626; border: 1px solid #fecaca;'>
                    <div style='font-size: 0.85rem; color: {badge_color}; font-weight: 600; margin-bottom: 0.5rem;'>
                        {importance_badge} Priority - Action Needed
                    </div>
                    <strong style='color: #1e293b; font-size: 1rem; display: block; margin-bottom: 0.75rem;'>{item['question']}</strong>
                    <p style='margin: 0; color: #475569; font-size: 0.95rem; line-height: 1.6; font-style: italic;'>
                        {item['analysis']}
                    </p>
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
        st.markdown("Streamlit Active")
        
        if st.session_state.orchestrator:
            st.markdown("Orchestrator Ready")
        
        st.markdown("---")
        st.markdown("### System Requirements")
        
        # Display AI service info
        deployment_name = "Not loaded"
        if st.session_state.orchestrator:
            deployment_name = st.session_state.orchestrator.ai_service.deployment
        
        st.markdown(f"""
        <div style='color: white;'>
        <p style='margin: 0.25rem 0;'><strong>AI Service:</strong> Azure OpenAI</p>
        <p style='margin: 0.25rem 0;'><strong>Model:</strong> {deployment_name}</p>
        <p style='margin: 0.25rem 0;'><strong>Status:</strong> Cloud-based</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        Professional tool for evaluating 
        repository governance, CI/CD, 
        testing, and code quality.
        
        **Privacy First**  
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
            st.success("✓ Azure OpenAI ready for analysis")
            st.session_state.stage = "assessment"
            st.session_state.system_ready = True
            st.rerun()
        else:
            st.error("✗ " + message)
            st.info("Please check your Azure OpenAI service configuration and connectivity.")
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
