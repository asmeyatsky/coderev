"""
CodeReview Entity Tests

Test cases for the CodeReview domain entity.
Validating business rules, invariants, and behavior of the CodeReview entity.
"""

import pytest
from datetime import datetime
from ecrp.domain.entities.code_review import CodeReview, ReviewStatus, ReviewPriority
from ecrp.domain.entities.user import User, UserRole


class TestCodeReview:
    """Test cases for the CodeReview entity"""
    
    def test_code_review_creation_with_valid_data(self):
        """Test creating a code review with valid data"""
        # Arrange
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        
        # Act
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=user
        )
        
        # Assert
        assert code_review.id == "review-123"
        assert code_review.title == "Test Review"
        assert code_review.description == "This is a test review"
        assert code_review.source_branch == "feature/test"
        assert code_review.target_branch == "main"
        assert code_review.requester == user
        assert code_review.status == ReviewStatus.OPEN
        assert code_review.priority == ReviewPriority.MEDIUM
        assert code_review.required_approvals == 1
    
    def test_code_review_creation_fails_with_empty_id(self):
        """Test that code review creation fails with empty ID"""
        # Arrange
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="CodeReview ID cannot be empty"):
            CodeReview(
                id="",
                title="Test Review",
                description="This is a test review",
                source_branch="feature/test",
                target_branch="main",
                requester=user
            )
    
    def test_code_review_creation_fails_with_empty_source_branch(self):
        """Test that code review creation fails with empty source branch"""
        # Arrange
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Source branch cannot be empty"):
            CodeReview(
                id="review-123",
                title="Test Review",
                description="This is a test review",
                source_branch="",
                target_branch="main",
                requester=user
            )
    
    def test_code_review_creation_fails_with_empty_target_branch(self):
        """Test that code review creation fails with empty target branch"""
        # Arrange
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Target branch cannot be empty"):
            CodeReview(
                id="review-123",
                title="Test Review",
                description="This is a test review",
                source_branch="feature/test",
                target_branch="",
                requester=user
            )
    
    def test_approve_method_updates_approvals_and_status(self):
        """Test that approve method updates approvals and status correctly"""
        # Arrange
        user = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        reviewer = User(
            id="user-456",
            username="reviewer",
            email="reviewer@example.com"
        )
        
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=user,
            reviewers={"user-456"}
        )
        
        # Act
        updated_review = code_review.approve("user-456")
        
        # Assert
        assert "user-456" in updated_review.approvers
        assert updated_review.current_approvals == 1
        assert updated_review.status == ReviewStatus.APPROVED
    
    def test_request_changes_method_updates_status(self):
        """Test that request_changes method updates status correctly"""
        # Arrange
        user = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        reviewer = User(
            id="user-456",
            username="reviewer",
            email="reviewer@example.com"
        )
        
        code_review = CodeReview(
            id="review-123",
            title="Test Review",
            description="This is a test review",
            source_branch="feature/test",
            target_branch="main",
            requester=user,
            reviewers={"user-456"}
        )
        
        # Act
        updated_review = code_review.request_changes("user-456")
        
        # Assert
        assert "user-456" in updated_review.rejectors
        assert updated_review.status == ReviewStatus.NEEDS_WORK
    
    def test_can_merge_returns_true_when_all_conditions_met(self):
        """Test that can_merge returns True when all conditions are met"""
        # Arrange
        user = User(
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
            requester=user,
            status=ReviewStatus.APPROVED,
            current_approvals=1,
            required_approvals=1
        )
        
        # Act
        can_merge = code_review.can_merge()
        
        # Assert
        assert can_merge is True
    
    def test_can_merge_returns_false_when_not_approved(self):
        """Test that can_merge returns False when not approved"""
        # Arrange
        user = User(
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
            requester=user,
            status=ReviewStatus.OPEN,
            current_approvals=1,
            required_approvals=1
        )
        
        # Act
        can_merge = code_review.can_merge()
        
        # Assert
        assert can_merge is False
    
    def test_merge_method_changes_status_to_merged(self):
        """Test that merge method changes status to merged when conditions are met"""
        # Arrange
        user = User(
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
            requester=user,
            status=ReviewStatus.APPROVED,
            current_approvals=1,
            required_approvals=1
        )
        
        # Act
        merged_review = code_review.merge()
        
        # Assert
        assert merged_review.status == ReviewStatus.MERGED
    
    def test_merge_method_fails_when_conditions_not_met(self):
        """Test that merge method fails when conditions are not met"""
        # Arrange
        user = User(
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
            requester=user,
            status=ReviewStatus.OPEN,  # Not approved
            current_approvals=1,
            required_approvals=1
        )
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot merge review that doesn't meet all requirements"):
            code_review.merge()