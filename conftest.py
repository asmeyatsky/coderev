"""
Pytest configuration and fixtures for ECRP project

This file helps pytest discover and import modules correctly.
"""

import sys
import os

# Add the project root to the Python path so tests can import from ecrp
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Create an __init__.py in the project root if it doesn't exist
init_file = os.path.join(project_root, '__init__.py')
if not os.path.exists(init_file):
    open(init_file, 'a').close()

import pytest
from datetime import datetime


@pytest.fixture
def sample_user():
    """Fixture providing a sample user for tests"""
    from domain.entities.user import User, UserRole
    return User(
        id="user-123",
        username="testuser",
        email="test@example.com",
        roles=[UserRole.REVIEWER]
    )


@pytest.fixture
def sample_code_review(sample_user):
    """Fixture providing a sample code review for tests"""
    from domain.entities.code_review import CodeReview, ReviewStatus, ReviewPriority
    return CodeReview(
        id="review-123",
        title="Test Review",
        description="This is a test code review",
        source_branch="feature/test",
        target_branch="main",
        requester=sample_user,
        status=ReviewStatus.OPEN,
        priority=ReviewPriority.MEDIUM,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )


@pytest.fixture
def sample_comment(sample_user):
    """Fixture providing a sample comment for tests"""
    from domain.entities.comment import Comment, CommentType
    return Comment(
        id="comment-123",
        content="This is a test comment",
        author_id=sample_user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        comment_type=CommentType.GENERAL
    )


@pytest.fixture
def sample_risk_score():
    """Fixture providing a sample risk score for tests"""
    from domain.entities.risk_score import RiskScore
    return RiskScore(
        id="risk-123",
        code_review_id="review-123",
        calculated_at=datetime.now(),
        code_complexity_score=0.7,
        security_impact_score=0.5,
        critical_files_score=0.3,
        dataflow_confidence_score=0.8,
        test_coverage_delta_score=0.6,
        code_complexity_weight=0.2,
        security_impact_weight=0.3,
        critical_files_weight=0.2,
        dataflow_confidence_weight=0.15,
        test_coverage_delta_weight=0.15,
        overall_score=60.0,
        risk_level="medium"
    )


@pytest.fixture
def setup_repositories():
    """Fixture providing in-memory repositories for integration tests"""
    from infrastructure.repositories.in_memory_repositories import (
        InMemoryUserRepository,
        InMemoryCodeReviewRepository,
        InMemoryCommentRepository,
        InMemoryRiskScoreRepository,
        InMemoryEnvironmentRepository
    )

    return {
        "user_repository": InMemoryUserRepository(),
        "code_review_repository": InMemoryCodeReviewRepository(),
        "comment_repository": InMemoryCommentRepository(),
        "risk_score_repository": InMemoryRiskScoreRepository(),
        "environment_repository": InMemoryEnvironmentRepository()
    }
