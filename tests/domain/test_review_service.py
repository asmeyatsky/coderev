"""
ReviewDomainService Tests

Test cases for the ReviewDomainService domain service.
Validating business logic and coordination between entities.
"""

import pytest
from domain.entities.user import User, UserRole
from domain.entities.code_review import CodeReview, ReviewStatus, ReviewPriority
from domain.entities.risk_score import RiskScore
from domain.services.review_service import ReviewDomainService


class TestReviewDomainService:
    """Test cases for the ReviewDomainService"""
    
    def test_calculate_required_reviewers_with_security_risk(self):
        """Test calculating required reviewers when security risk is present"""
        # Arrange
        service = ReviewDomainService()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester
        )
        
        risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=50.0,
            security_impact_score=80.0,  # High security impact
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=10.0
        )
        
        security_engineer = User(
            id="sec-456",
            username="security-eng",
            email="sec@example.com",
            roles={UserRole.SECURITY_ENGINEER}
        )
        
        regular_reviewer = User(
            id="rev-789",
            username="regular-reviewer",
            email="reviewer@example.com",
            roles={UserRole.REVIEWER}
        )
        
        available_users = [security_engineer, regular_reviewer]
        
        # Act
        required_reviewers = service.calculate_required_reviewers(
            code_review,
            risk_score,
            available_users
        )
        
        # Assert
        assert "sec-456" in required_reviewers  # Security engineer should be required
    
    def test_calculate_required_reviewers_with_qa_risk(self):
        """Test calculating required reviewers when QA risk is present"""
        # Arrange
        service = ReviewDomainService()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester
        )
        
        risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=50.0,
            security_impact_score=20.0,
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=80.0  # High test coverage delta
        )
        
        qa_engineer = User(
            id="qa-456",
            username="qa-eng",
            email="qa@example.com",
            roles={UserRole.QA_ENGINEER}
        )
        
        regular_reviewer = User(
            id="rev-789",
            username="regular-reviewer",
            email="reviewer@example.com",
            roles={UserRole.REVIEWER}
        )
        
        available_users = [qa_engineer, regular_reviewer]
        
        # Act
        required_reviewers = service.calculate_required_reviewers(
            code_review,
            risk_score,
            available_users
        )
        
        # Assert
        assert "qa-456" in required_reviewers  # QA engineer should be required
    
    def test_can_user_approve_review_returns_true_for_valid_approver(self):
        """Test that can_user_approve_review returns True for valid approver"""
        # Arrange
        service = ReviewDomainService()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        reviewer = User(
            id="user-456",
            username="reviewer",
            email="reviewer@example.com",
            roles={UserRole.REVIEWER}
        )
        
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester,
            reviewers={"user-456"}
        )
        
        # Act
        can_approve = service.can_user_approve_review(reviewer, code_review)
        
        # Assert
        assert can_approve is True
    
    def test_can_user_approve_review_returns_false_for_non_assigned_reviewer(self):
        """Test that can_user_approve_review returns False for non-assigned reviewer"""
        # Arrange
        service = ReviewDomainService()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        reviewer = User(
            id="user-456",
            username="reviewer",
            email="reviewer@example.com",
            roles={UserRole.REVIEWER}
        )
        
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester,
            reviewers={"user-789"}  # Different reviewer assigned
        )
        
        # Act
        can_approve = service.can_user_approve_review(reviewer, code_review)
        
        # Assert
        assert can_approve is False
    
    def test_can_user_approve_review_returns_false_for_requester(self):
        """Test that can_user_approve_review returns False for the requester"""
        # Arrange
        service = ReviewDomainService()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com",
            roles={UserRole.REVIEWER}
        )
        
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester,
            reviewers={"user-123"}  # Requester is assigned as reviewer
        )
        
        # Act
        can_approve = service.can_user_approve_review(requester, code_review)
        
        # Assert
        assert can_approve is False  # Requester cannot approve their own review
    
    def test_calculate_review_time_estimate_for_large_changes(self):
        """Test that calculate_review_time_estimate increases for large changes"""
        # Arrange
        service = ReviewDomainService()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        code_review_small = CodeReview(
            id="review-123",
            title="Small Review",
            description="This is a small review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester,
            files_changed=1,
            additions=20,
            deletions=10
        )
        
        code_review_large = CodeReview(
            id="review-456",
            title="Large Review",
            description="This is a large review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester,
            files_changed=20,
            additions=600,
            deletions=100
        )
        
        # Act
        small_estimate = service.calculate_review_time_estimate(code_review_small)
        large_estimate = service.calculate_review_time_estimate(code_review_large)
        
        # Assert
        assert large_estimate > small_estimate  # Large changes should take more time
    
    def test_should_escalate_review_returns_true_for_aged_high_risk_review(self):
        """Test that should_escalate_review returns True for aged high-risk reviews"""
        # Arrange
        service = ReviewDomainService()
        
        from datetime import datetime, timedelta
        past_time = datetime.now() - timedelta(days=2)  # 2 days ago
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        code_review = CodeReview(
            id="review-123",
            title="High Risk Review",
            description="This is a high risk review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester,
            created_at=past_time,
            status=ReviewStatus.UNDER_REVIEW,  # Not yet approved
            risk_score=85.0  # High risk score
        )
        
        # Act
        should_escalate = service.should_escalate_review(code_review)
        
        # Assert
        assert should_escalate is True  # High risk and aged review should be escalated
    
    def test_should_escalate_review_returns_false_for_new_review(self):
        """Test that should_escalate_review returns False for new reviews"""
        # Arrange
        service = ReviewDomainService()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        code_review = CodeReview(
            id="review-123",
            title="New Review",
            description="This is a new review",
            source_branch="feature/test",
            target_branch="main",
            requester=requester,
            status=ReviewStatus.UNDER_REVIEW
        )
        
        # Act
        should_escalate = service.should_escalate_review(code_review)
        
        # Assert
        assert should_escalate is False  # New review should not be escalated