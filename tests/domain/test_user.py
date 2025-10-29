"""
User Entity Tests

Test cases for the User domain entity.
Validating business rules, invariants, and behavior of the User entity.
"""

import pytest
from datetime import datetime
from domain.entities.user import User, UserRole


class TestUser:
    """Test cases for the User entity"""
    
    def test_user_creation_with_valid_data(self):
        """Test creating a user with valid data"""
        # Arrange
        user_id = "user-123"
        username = "testuser"
        email = "test@example.com"
        
        # Act
        user = User(
            id=user_id,
            username=username,
            email=email
        )
        
        # Assert
        assert user.id == user_id
        assert user.username == username
        assert user.email == email
        assert user.roles == set()
        assert isinstance(user.created_at, datetime)
    
    def test_user_creation_fails_with_empty_id(self):
        """Test that user creation fails with empty ID"""
        # Act & Assert
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            User(
                id="",
                username="testuser",
                email="test@example.com"
            )
    
    def test_user_creation_fails_with_empty_username(self):
        """Test that user creation fails with empty username"""
        # Act & Assert
        with pytest.raises(ValueError, match="Username cannot be empty"):
            User(
                id="user-123",
                username="",
                email="test@example.com"
            )
    
    def test_user_creation_fails_with_invalid_email(self):
        """Test that user creation fails with invalid email"""
        # Act & Assert
        with pytest.raises(ValueError, match="Email must be valid"):
            User(
                id="user-123",
                username="testuser",
                email="invalid-email"
            )
    
    def test_has_role_returns_false_for_non_assigned_role(self):
        """Test that has_role returns False for non-assigned role"""
        # Arrange
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        
        # Act
        has_role = user.has_role(UserRole.DEVELOPER)
        
        # Assert
        assert has_role is False
    
    def test_has_role_returns_true_for_assigned_role(self):
        """Test that has_role returns True for assigned role"""
        # Arrange
        user = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            roles={UserRole.DEVELOPER}
        )
        
        # Act
        has_role = user.has_role(UserRole.DEVELOPER)
        
        # Assert
        assert has_role is True
    
    def test_add_role_creates_new_instance_with_role(self):
        """Test that adding a role creates a new instance with the role"""
        # Arrange
        original_user = User(
            id="user-123",
            username="testuser",
            email="test@example.com"
        )
        
        # Act
        updated_user = original_user.add_role(UserRole.REVIEWER)
        
        # Assert
        assert original_user.roles == set()  # Original unchanged
        assert updated_user.roles == {UserRole.REVIEWER}  # New instance has role
        assert original_user is not updated_user  # Different instances
    
    def test_remove_role_creates_new_instance_without_role(self):
        """Test that removing a role creates a new instance without the role"""
        # Arrange
        original_user = User(
            id="user-123",
            username="testuser",
            email="test@example.com",
            roles={UserRole.REVIEWER}
        )
        
        # Act
        updated_user = original_user.remove_role(UserRole.REVIEWER)
        
        # Assert
        assert original_user.roles == {UserRole.REVIEWER}  # Original unchanged
        assert updated_user.roles == set()  # New instance has no roles
        assert original_user is not updated_user  # Different instances