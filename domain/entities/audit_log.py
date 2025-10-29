"""
Audit Log Entity

Architectural Intent:
- Track all changes and actions in the system for compliance and debugging
- Maintain immutable record of who did what and when
- Enable reconstruction of entity state at any point in time
- Support forensic analysis and compliance audits

Key Design Decisions:
1. Audit logs are immutable (frozen dataclass)
2. Each log entry includes actor, action, timestamp, and state changes
3. Logs are stored separately from domain entities
4. Both old and new states are captured for updates
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class AuditAction(Enum):
    """Enum for audit log actions"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_CHANGES = "request_changes"
    MERGE = "merge"
    CLOSE = "close"
    COMMENT = "comment"
    RESOLVE_COMMENT = "resolve_comment"
    ENVIRONMENT_CREATE = "environment_create"
    ENVIRONMENT_DESTROY = "environment_destroy"


@dataclass(frozen=True)
class AuditLog:
    """
    Audit Log Domain Entity

    Invariants:
    - ID must not be empty
    - Entity type must not be empty
    - Entity ID must not be empty
    - Action must be valid AuditAction enum
    - Actor ID must not be empty
    - Timestamp must be valid datetime
    """

    id: str
    entity_type: str  # "CodeReview", "Comment", "Environment", etc.
    entity_id: str
    action: AuditAction
    actor_id: str
    created_at: datetime = field(default_factory=datetime.now)

    # Optional state tracking
    old_state: Optional[Dict[str, Any]] = None  # Previous state (for updates)
    new_state: Optional[Dict[str, Any]] = None  # Current state (for creates/updates)
    changes: Optional[Dict[str, Any]] = None    # Summary of what changed
    description: Optional[str] = None  # Human-readable description

    def __post_init__(self):
        """Validate invariants after initialization"""
        if not self.id:
            raise ValueError("Audit log ID cannot be empty")
        if not self.entity_type:
            raise ValueError("Entity type cannot be empty")
        if not self.entity_id:
            raise ValueError("Entity ID cannot be empty")
        if not self.actor_id:
            raise ValueError("Actor ID cannot be empty")
        if not isinstance(self.action, AuditAction):
            raise ValueError("Action must be a valid AuditAction")

    @property
    def is_state_change(self) -> bool:
        """Check if this audit log represents a state change"""
        return self.action in [AuditAction.UPDATE, AuditAction.APPROVE, AuditAction.REJECT]

    def get_summary(self) -> str:
        """Get a human-readable summary of the action"""
        if self.description:
            return self.description
        return f"{self.actor_id} {self.action.value} {self.entity_type} {self.entity_id}"
