"""
CreateCodeReviewUseCase Tests

Test cases for the CreateCodeReviewUseCase application use case.
Validating orchestration between domain entities, services, and infrastructure.
"""

import pytest
from unittest.mock import Mock, MagicMock
from application.use_cases.create_code_review import CreateCodeReviewUseCaseImpl
from domain.entities.user import User, UserRole
from domain.entities.code_review import CodeReview, ReviewStatus
from domain.entities.risk_score import RiskScore


class TestCreateCodeReviewUseCase:
    """Test cases for the CreateCodeReviewUseCase"""
    
    def test_execute_creates_code_review_successfully(self):
        """Test that execute successfully creates a code review"""
        # Arrange
        mock_code_review_repository = Mock()
        mock_user_repository = Mock()
        mock_risk_analysis_service = Mock()
        mock_environment_service = Mock()
        mock_git_provider_service = Mock()
        mock_review_service = Mock()
        
        # Mock the requester user
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        mock_user_repository.find_by_id.return_value = requester
        
        # Mock the risk score
        risk_score = RiskScore(
            id="risk-123",
            code_review_id="review-123",
            code_complexity_score=50.0,
            security_impact_score=30.0,
            critical_files_score=20.0,
            dataflow_confidence_score=40.0,
            test_coverage_delta_score=10.0
        )
        mock_risk_analysis_service.calculate_risk_score.return_value = risk_score
        
        # Mock the Git provider service to return a diff
        mock_git_provider_service.get_pull_request_diff.return_value = "sample diff content"

        # Mock the environment service to return an environment
        mock_environment = Mock()
        mock_environment.url = "https://example.com/env"
        mock_environment_service.create_environment.return_value = mock_environment

        # Mock all users for review service
        mock_user_repository.find_all.return_value = [requester]

        # Mock the review service to return empty required reviewers list
        mock_review_service.calculate_required_reviewers.return_value = []

        # Mock the repository save method to return the code review passed to it
        mock_code_review_repository.save.side_effect = lambda code_review: code_review
        
        use_case = CreateCodeReviewUseCaseImpl(
            code_review_repository=mock_code_review_repository,
            user_repository=mock_user_repository,
            risk_analysis_service=mock_risk_analysis_service,
            environment_service=mock_environment_service,
            git_provider_service=mock_git_provider_service,
            review_service=mock_review_service
        )
        
        # Act
        result = use_case.execute(
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester_id="user-123"
        )
        
        # Assert - Verify the repository save was called
        assert mock_code_review_repository.save.called
        saved_review = mock_code_review_repository.save.call_args[0][0]
        assert saved_review.title == "Test Review"
        assert saved_review.requester.id == "user-123"
    
    def test_execute_fails_when_requester_not_found(self):
        """Test that execute fails when requester is not found"""
        # Arrange
        mock_code_review_repository = Mock()
        mock_user_repository = Mock()
        mock_risk_analysis_service = Mock()
        mock_environment_service = Mock()
        mock_git_provider_service = Mock()
        mock_review_service = Mock()
        
        # Mock the requester user to return None (not found)
        mock_user_repository.find_by_id.return_value = None
        
        use_case = CreateCodeReviewUseCaseImpl(
            code_review_repository=mock_code_review_repository,
            user_repository=mock_user_repository,
            risk_analysis_service=mock_risk_analysis_service,
            environment_service=mock_environment_service,
            git_provider_service=mock_git_provider_service,
            review_service=mock_review_service
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Requester with ID user-123 not found"):
            use_case.execute(
                title="Test Review",
                description="This is a test review",
                source_branch="feature/test",
                target_branch="main",
                requester_id="user-123"
            )