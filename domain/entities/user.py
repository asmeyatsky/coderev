"""
User Entity

Architectural Intent:
- Represents a user in the ECRP system (requester, reviewer, QA engineer, etc.)
- Maintains business rules related to user identification and roles
- Follows DDD principles with rich domain model

Key Design Decisions:
1. User entity is immutable after creation to prevent accidental state corruption
2. Roles are stored as a set for efficient lookups and to prevent duplicates
3. Domain invariants ensure required fields are always present
4. Validation happens at construction time
"""

from dataclasses import dataclass, field
from typing import Set, Optional
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """
    Enum for different roles a user can have in the ECRP system
    """
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    QA_ENGINEER = "qa_engineer"
    SECURITY_ENGINEER = "security_engineer"
    COMPLIANCE_OFFICER = "compliance_officer"
    ADMIN = "admin"


@dataclass(frozen=True)
class User:
    """
    User Domain Entity
    
    Invariants:
    - User must have a unique ID
    - User must have a username
    - Username must be non-empty
    - Email must be valid if provided
    """
    
    id: str
    username: str
    email: str
    roles: Set[UserRole] = field(default_factory=set)
    full_name: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate invariants after initialization"""
        if not self.id:
            raise ValueError("User ID cannot be empty")
        if not self.username:
            raise ValueError("Username cannot be empty")
        if not self.email or "@" not in self.email:
            raise ValueError("Email must be valid")
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role"""
        return role in self.roles
    
    def add_role(self, role: UserRole) -> 'User':
        """Add a role to the user, returning a new instance"""
        current_roles = set(self.roles)
        current_roles.add(role)
        return self._update_roles(current_roles)
    
    def remove_role(self, role: UserRole) -> 'User':
        """Remove a role from the user, returning a new instance"""
        current_roles = set(self.roles)
        current_roles.discard(role)
        return self._update_roles(current_roles)
    
    def _update_roles(self, roles: Set[UserRole]) -> 'User':
        """Helper method to update roles and return new instance"""
        return User(
            id=self.id,
            username=self.username,
            email=self.email,
            roles=roles,
            full_name=self.full_name,
            created_at=self.created_at
        )