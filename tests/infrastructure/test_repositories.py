"""
In-Memory Repository Tests

Test cases for the in-memory repository implementations.
Validating that repositories correctly implement the repository port interfaces.
"""

import pytest
from infrastructure.repositories.in_memory_repositories import (
    InMemoryUserRepository,
    InMemoryCodeReviewRepository
)
from domain.entities.user import User
from domain.entities.code_review import CodeReview


class TestInMemoryUserRepository:
    """Test cases for the InMemoryUserRepository"""
    
    def test_save_and_find_by_id(self):
        """Test saving and finding a user by ID"""
        # Arrange
        repository = InMemoryUserRepository()
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        
        # Act
        saved_user = repository.save(user)
        found_user = repository.find_by_id("user-123")
        
        # Assert
        assert found_user is not None
        assert found_user.id == "user-123"
        assert found_user.username == "testuser"
        assert found_user == saved_user  # Should be the same instance
    
    def test_find_by_username(self):
        """Test finding a user by username"""
        # Arrange
        repository = InMemoryUserRepository()
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        repository.save(user)
        
        # Act
        found_user = repository.find_by_username("testuser")
        
        # Assert
        assert found_user is not None
        assert found_user.id == "user-123"
    
    def test_find_by_username_returns_none_when_not_found(self):
        """Test that find_by_username returns None when user is not found"""
        # Arrange
        repository = InMemoryUserRepository()
        
        # Act
        found_user = repository.find_by_username("nonexistent")
        
        # Assert
        assert found_user is None


class TestInMemoryCodeReviewRepository:
    """Test cases for the InMemoryCodeReviewRepository"""
    
    def test_save_and_find_by_id(self):
        """Test saving and finding a code review by ID"""
        # Arrange
        repository = InMemoryCodeReviewRepository()
        
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
        
        # Act
        saved_review = repository.save(code_review)
        found_review = repository.find_by_id("review-123")
        
        # Assert
        assert found_review is not None
        assert found_review.id == "review-123"
        assert found_review.title == "Test Review"
        assert found_review == saved_review  # Should be the same instance
    
    def test_find_by_requester(self):
        """Test finding code reviews by requester"""
        # Arrange
        repository = InMemoryCodeReviewRepository()
        
        requester = User(
            id="user-123",
            username="requester",
            email="requester@example.com"
        )
        
        code_review1 = CodeReview(
            id="review-123",
            title="Test Review 1",
            description="This is a test review",
            source_branch="feature/test1",
            target_branch="main",
            requester=requester
        )
        
        code_review2 = CodeReview(
            id="review-456",
            title="Test Review 2",
            description="This is another test review",
            source_branch="feature/test2",
            target_branch="main",
            requester=requester
        )
        
        other_requester = User(
            id="user-789",
            username="other",
            email="other@example.com"
        )
        
        other_review = CodeReview(
            id="review-789",
            title="Other Review",
            description="This is a different review",
            source_branch="feature/test3",
            target_branch="main",
            requester=other_requester
        )
        
        repository.save(code_review1)
        repository.save(code_review2)
        repository.save(other_review)
        
        # Act
        reviews_by_requester = repository.find_by_requester("user-123")
        
        # Assert
        assert len(reviews_by_requester) == 2
        review_ids = {review.id for review in reviews_by_requester}
        assert "review-123" in review_ids
        assert "review-456" in review_ids
        assert "review-789" not in review_ids