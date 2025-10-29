"""
Environment Entity

Architectural Intent:
- Represents an ephemeral review environment (sandbox) for a code review
- Encapsulates business rules for environment lifecycle management
- Maintains invariants related to resource management and access
- Follows DDD principles with rich domain model

Key Design Decisions:
1. Environments are immutable in terms of core properties after creation
2. Status transitions are controlled through domain methods
3. Automatic cleanup is enforced through TTL (Time To Live)
4. Environment resources are properly isolated per PR
"""

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class EnvironmentStatus(Enum):
    """Enum for environment lifecycle statuses"""
    PENDING = "pending"
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    FAILED = "failed"
    DESTROYED = "destroyed"


@dataclass(frozen=True)
class Environment:
    """
    Environment Domain Entity
    
    Invariants:
    - Environment must have a unique ID
    - Environment must have a code review ID
    - TTL must be positive
    - Created and updated timestamps must be valid
    - URL must be valid when status is RUNNING
    """
    
    id: str
    code_review_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Environment properties
    name: Optional[str] = None
    description: Optional[str] = None
    status: EnvironmentStatus = EnvironmentStatus.PENDING
    ttl_minutes: int = 120  # Default 2-hour TTL
    
    # Access information
    url: Optional[str] = None
    ssh_access_url: Optional[str] = None
    api_access_token: Optional[str] = None
    
    # Environment configuration
    branch: Optional[str] = None
    commit_hash: Optional[str] = None
    services: list = None  # List of services in the environment
    resources: dict = None  # Resource allocation specs
    
    # Lifecycle management
    expires_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate invariants after initialization"""
        if not self.id:
            raise ValueError("Environment ID cannot be empty")
        if not self.code_review_id:
            raise ValueError("Code review ID cannot be empty")
        if self.ttl_minutes <= 0:
            raise ValueError("TTL must be positive")
        if self.status == EnvironmentStatus.RUNNING and not self.url:
            raise ValueError("URL must be provided when environment is running")
        
        # Calculate expiration time if not set
        if self.expires_at is None:
            object.__setattr__(self, 'expires_at', self.created_at + timedelta(minutes=self.ttl_minutes))
    
    def start(self) -> 'Environment':
        """Transition environment to running state"""
        if self.status not in [EnvironmentStatus.PENDING, EnvironmentStatus.CREATING]:
            raise ValueError(f"Cannot start environment in status {self.status.value}")

        return replace(
            self,
            status=EnvironmentStatus.RUNNING,
            updated_at=datetime.now(),
            last_accessed_at=datetime.now()
        )
    
    def stop(self) -> 'Environment':
        """Transition environment to stopped state"""
        if self.status != EnvironmentStatus.RUNNING:
            raise ValueError(f"Cannot stop environment in status {self.status.value}")

        return replace(self, status=EnvironmentStatus.STOPPED, updated_at=datetime.now())
    
    def destroy(self) -> 'Environment':
        """Transition environment to destroyed state"""
        if self.status == EnvironmentStatus.DESTROYED:
            raise ValueError("Environment is already destroyed")

        return replace(self, status=EnvironmentStatus.DESTROYED, updated_at=datetime.now())
    
    def mark_accessed(self) -> 'Environment':
        """Update the last accessed time"""
        return replace(self, last_accessed_at=datetime.now(), updated_at=datetime.now())
    
    def is_expired(self) -> bool:
        """Check if the environment has expired"""
        return datetime.now() > self.expires_at
    
    def time_remaining(self) -> timedelta:
        """Get the time remaining before expiration"""
        remaining = self.expires_at - datetime.now()
        return max(remaining, timedelta(seconds=0))
    
    def is_accessible(self) -> bool:
        """Check if the environment is currently accessible"""
        return (
            self.status == EnvironmentStatus.RUNNING and
            not self.is_expired()
        )