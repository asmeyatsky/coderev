"""
Code Review Entity

Architectural Intent:
- Represents a code review request (Pull/Merge Request) in the ECRP system
- Encapsulates business rules for review lifecycle, status transitions, and approval requirements
- Maintains invariants related to the review process
- Follows DDD principles with rich domain model

Key Design Decisions:
1. CodeReview is immutable to prevent accidental state corruption during review process
2. Status transitions are controlled through domain methods to ensure valid state changes
3. Approval requirements are validated when attempting to merge
4. All state changes happen through domain methods that maintain invariants
"""

from dataclasses import dataclass, field, replace
from typing import List, Optional, Set
from datetime import datetime
from enum import Enum
from .user import User


class ReviewStatus(Enum):
    """Enum for possible review statuses"""
    DRAFT = "draft"
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    NEEDS_WORK = "needs_work"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    CLOSED = "closed"


class ReviewPriority(Enum):
    """Enum for review priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class CodeReview:
    """
    CodeReview Domain Entity
    
    Invariants:
    - Review must have a unique ID
    - Review must have a source branch and target branch
    - Status transitions must follow defined rules
    - Cannot approve a review that is not open or under review
    """
    
    id: str
    title: str
    description: str
    source_branch: str
    target_branch: str
    requester: User
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Status and metadata
    status: ReviewStatus = ReviewStatus.OPEN
    priority: ReviewPriority = ReviewPriority.MEDIUM
    
    # Review tracking
    reviewers: Set[str] = field(default_factory=set)  # IDs of assigned reviewers
    approvers: Set[str] = field(default_factory=set)  # IDs of users who approved
    rejectors: Set[str] = field(default_factory=set)  # IDs of users who rejected
    required_approvals: int = 1
    current_approvals: int = 0
    
    # Risk scoring
    risk_score: Optional[float] = None  # Calculated by AI
    security_approval_required: bool = False
    qa_approval_required: bool = False
    
    # Additional metadata
    labels: Set[str] = field(default_factory=set)
    comments_count: int = 0
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0

    # SLA tracking
    sla_hours_limit: int = 48  # Default: 48 hours for standard reviews
    sla_deadline: Optional[datetime] = None  # Calculated deadline for completion
    is_escalated: bool = False
    escalation_level: int = 0  # 0 = none, 1+ = escalation count
    escalation_notified_at: Optional[datetime] = None  # When escalation was last notified

    # Ephemeral environment
    ephemeral_environment_url: Optional[str] = None
    
    def __post_init__(self):
        """Validate invariants after initialization"""
        if not self.id:
            raise ValueError("CodeReview ID cannot be empty")
        if not self.source_branch:
            raise ValueError("Source branch cannot be empty")
        if not self.target_branch:
            raise ValueError("Target branch cannot be empty")
        if self.required_approvals < 1:
            raise ValueError("Required approvals must be at least 1")
        if self.current_approvals < 0:
            raise ValueError("Current approvals cannot be negative")
    
    def assign_reviewer(self, reviewer_id: str) -> 'CodeReview':
        """Assign a reviewer to this code review"""
        new_reviewers = set(self.reviewers)
        new_reviewers.add(reviewer_id)
        return self._update_reviewers(new_reviewers)
    
    def request_changes(self, reviewer_id: str) -> 'CodeReview':
        """Mark review as needing changes"""
        # Add to rejectors and remove from approvers
        new_rejectors = set(self.rejectors)
        new_rejectors.add(reviewer_id)
        
        new_approvers = set(self.approvers)
        new_approvers.discard(reviewer_id)
        
        current_approvals = len(new_approvers)
        
        return self._update_approvals(
            approvers=new_approvers,
            rejectors=new_rejectors,
            current_approvals=current_approvals,
            status=ReviewStatus.NEEDS_WORK
        )
    
    def approve(self, reviewer_id: str) -> 'CodeReview':
        """Approve the code review by a reviewer"""
        if self.status not in [ReviewStatus.OPEN, ReviewStatus.UNDER_REVIEW]:
            raise ValueError(f"Cannot approve review with status {self.status.value}")
        
        # Add to approvers and remove from rejectors
        new_approvers = set(self.approvers)
        new_approvers.add(reviewer_id)
        
        new_rejectors = set(self.rejectors)
        new_rejectors.discard(reviewer_id)
        
        current_approvals = len(new_approvers)
        
        # Determine new status based on current approvals
        new_status = self.status
        if current_approvals >= self.required_approvals:
            new_status = ReviewStatus.APPROVED
        
        return self._update_approvals(
            approvers=new_approvers,
            rejectors=new_rejectors,
            current_approvals=current_approvals,
            status=new_status
        )
    
    def reject(self, reviewer_id: str) -> 'CodeReview':
        """Reject the code review by a reviewer"""
        if self.status not in [ReviewStatus.OPEN, ReviewStatus.UNDER_REVIEW]:
            raise ValueError(f"Cannot reject review with status {self.status.value}")
        
        # Add to rejectors and remove from approvers
        new_rejectors = set(self.rejectors)
        new_rejectors.add(reviewer_id)
        
        new_approvers = set(self.approvers)
        new_approvers.discard(reviewer_id)
        
        current_approvals = len(new_approvers)
        
        return self._update_approvals(
            approvers=new_approvers,
            rejectors=new_rejectors,
            current_approvals=current_approvals,
            status=ReviewStatus.REJECTED
        )
    
    def can_merge(self) -> bool:
        """Determine if the review can be merged"""
        # Basic conditions
        if self.status != ReviewStatus.APPROVED:
            return False

        # Check if we have enough approvals
        if self.current_approvals < self.required_approvals:
            return False

        # Note: Security and QA approval requirements should be checked at the use case layer
        # where we have access to the approver user objects and can verify their roles
        return True
    
    def merge(self) -> 'CodeReview':
        """Mark the review as merged if all requirements are met"""
        if not self.can_merge():
            raise ValueError("Cannot merge review that doesn't meet all requirements")
        
        # Update status to merged
        return self._update_status(ReviewStatus.MERGED)
    
    def close(self) -> 'CodeReview':
        """Close the review"""
        return self._update_status(ReviewStatus.CLOSED)
    
    def add_comment(self) -> 'CodeReview':
        """Increment comment count"""
        return self._update_comments_count(self.comments_count + 1)
    
    def update_stats(self, files_changed: int, additions: int, deletions: int) -> 'CodeReview':
        """Update statistics about the changes"""
        return replace(
            self,
            files_changed=files_changed,
            additions=additions,
            deletions=deletions,
            updated_at=datetime.now()
        )
    
    def set_risk_score(self, score: float) -> 'CodeReview':
        """Set the AI-calculated risk score"""
        return replace(self, risk_score=score, updated_at=datetime.now())
    
    def set_ephemeral_environment_url(self, url: str) -> 'CodeReview':
        """Set the URL for the ephemeral review environment"""
        return replace(self, ephemeral_environment_url=url, updated_at=datetime.now())
    
    def _update_reviewers(self, reviewers: Set[str]) -> 'CodeReview':
        """Helper method to update reviewers and return new instance"""
        return replace(self, reviewers=reviewers, updated_at=datetime.now())
    
    def _update_approvals(
        self,
        approvers: Set[str],
        rejectors: Set[str],
        current_approvals: int,
        status: ReviewStatus
    ) -> 'CodeReview':
        """Helper method to update approval information and return new instance"""
        return replace(
            self,
            approvers=approvers,
            rejectors=rejectors,
            current_approvals=current_approvals,
            status=status,
            updated_at=datetime.now()
        )
    
    def _update_status(self, status: ReviewStatus) -> 'CodeReview':
        """Helper method to update status and return new instance"""
        return replace(self, status=status, updated_at=datetime.now())
    
    def _update_comments_count(self, comments_count: int) -> 'CodeReview':
        """Helper method to update comment count and return new instance"""
        return replace(self, comments_count=comments_count, updated_at=datetime.now())

    def set_sla_deadline(self, hours_limit: int) -> 'CodeReview':
        """Set the SLA deadline based on hours from now"""
        from datetime import timedelta
        deadline = datetime.now() + timedelta(hours=hours_limit)
        return replace(
            self,
            sla_hours_limit=hours_limit,
            sla_deadline=deadline,
            updated_at=datetime.now()
        )

    def is_overdue(self) -> bool:
        """Check if the review is past its SLA deadline"""
        if self.sla_deadline is None:
            return False
        return datetime.now() > self.sla_deadline

    def escalate(self, escalation_level: int = None) -> 'CodeReview':
        """Escalate the review due to SLA breach or other concerns"""
        new_level = (escalation_level or self.escalation_level) + 1
        return replace(
            self,
            is_escalated=True,
            escalation_level=new_level,
            escalation_notified_at=datetime.now(),
            updated_at=datetime.now()
        )

    def get_hours_remaining(self) -> float:
        """Get hours remaining until SLA deadline"""
        if self.sla_deadline is None:
            return float('inf')
        from datetime import timedelta
        remaining = self.sla_deadline - datetime.now()
        return remaining.total_seconds() / 3600

    def needs_escalation(self, hours_threshold: int = 4) -> bool:
        """Check if review needs escalation based on remaining time"""
        if self.status in [ReviewStatus.MERGED, ReviewStatus.CLOSED, ReviewStatus.REJECTED]:
            return False  # Already completed
        return self.get_hours_remaining() <= hours_threshold