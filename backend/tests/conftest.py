"""Pytest fixtures and configuration for testing"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
import os
from unittest.mock import MagicMock, AsyncMock

# Import application components
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db, assessment_sessions, shared_results_cache
from database import Base
from orchestrator import AssessmentOrchestrator
from azure_openai_service import AzureOpenAIService


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def override_get_db(db_session):
    """Override the get_db dependency"""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    return _override_get_db


@pytest.fixture(scope="function")
def client(override_get_db):
    """Create a test client"""
    app.dependency_overrides[get_db] = override_get_db
    
    # Clear in-memory storage before each test
    assessment_sessions.clear()
    shared_results_cache.clear()
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_azure_openai():
    """Mock Azure OpenAI service"""
    mock_service = MagicMock(spec=AzureOpenAIService)
    mock_service.analyze_answer = AsyncMock(return_value="yes")
    mock_service.generate_summary = AsyncMock(return_value="This is a comprehensive summary of the assessment results.")
    return mock_service


@pytest.fixture
def sample_session_id():
    """Return a sample session ID"""
    return "test-session-123"


@pytest.fixture
def sample_questions():
    """Return sample questions data"""
    return [
        {
            "id": "q1",
            "text": "Is branch protection enforced?",
            "max_score": 10.0,
            "importance": 10,
            "pillar": "code_review"
        },
        {
            "id": "q2",
            "text": "Are CODEOWNERS files used?",
            "max_score": 7.0,
            "importance": 7,
            "pillar": "code_review"
        }
    ]


@pytest.fixture
def sample_answers():
    """Return sample answers data"""
    return {
        "q1": {
            "answer": "Yes, we have branch protection enabled on all main branches.",
            "classification": "yes",
            "score": 10.0,
            "analysis": "Good implementation of branch protection"
        },
        "q2": {
            "answer": "No, we don't use CODEOWNERS files.",
            "classification": "no",
            "score": 0.0,
            "analysis": "Consider implementing CODEOWNERS"
        }
    }


@pytest.fixture
def sample_assessment_result():
    """Return sample assessment result"""
    return {
        "final_score": 58.5,
        "breakdown": {
            "code_review": {"earned": 10.0, "max": 17.0, "percentage": 58.8},
            "security": {"earned": 20.0, "max": 30.0, "percentage": 66.7}
        },
        "question_results": [
            {
                "question_id": "q1",
                "question_text": "Is branch protection enforced?",
                "user_answer": "Yes",
                "classification": "yes",
                "score_earned": 10.0,
                "max_score": 10.0
            }
        ],
        "summary": "Good overall implementation with room for improvement"
    }


@pytest.fixture
def valid_corporate_email():
    """Return a valid corporate email"""
    return "test.user@company.com"


@pytest.fixture
def invalid_personal_email():
    """Return an invalid personal email"""
    return "test@gmail.com"


@pytest.fixture(autouse=True)
def reset_caches():
    """Reset in-memory caches before each test"""
    assessment_sessions.clear()
    shared_results_cache.clear()
    yield
    assessment_sessions.clear()
    shared_results_cache.clear()
