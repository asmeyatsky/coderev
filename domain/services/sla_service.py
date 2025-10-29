"""
SLA Management Service

Architectural Intent:
- Manages Service Level Agreement (SLA) tracking for code reviews
- Monitors review deadlines and triggers escalations
- Enforces time-based review requirements
- Supports compliance and performance tracking

Key Design Decisions:
1. SLA service is stateless and focused on SLA operations
2. Escalation levels allow for progressive notification
3. SLA configuration is flexible (different hours for different priorities)
4. Service integrates with review service for domain logic
"""

from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from ..entities.code_review import CodeReview, ReviewStatus, ReviewPriority
from ..entities.user import User


class SLAService:
    """
    SLAService contains business logic for SLA management and escalation
    """

    # SLA hours by priority (adjustable for different organizations)
    SLA_HOURS_BY_PRIORITY = {
        ReviewPriority.CRITICAL: 4,      # 4 hours for critical
        ReviewPriority.HIGH: 24,         # 24 hours for high priority
        ReviewPriority.MEDIUM: 48,       # 48 hours for medium
        ReviewPriority.LOW: 72           # 72 hours for low priority
    }

    # Escalation thresholds (hours before deadline)
    FIRST_ESCALATION_THRESHOLD = 4   # Escalate if < 4 hours remaining
    SECOND_ESCALATION_THRESHOLD = 1  # Re-escalate if < 1 hour remaining

    def calculate_sla_hours(self, code_review: CodeReview) -> int:
        """Calculate SLA hours based on review priority"""
        return self.SLA_HOURS_BY_PRIORITY.get(code_review.priority, 48)

    def set_sla_deadline(self, code_review: CodeReview) -> CodeReview:
        """Set the SLA deadline for a code review"""
        sla_hours = self.calculate_sla_hours(code_review)
        return code_review.set_sla_deadline(sla_hours)

    def check_sla_status(self, code_review: CodeReview) -> dict:
        """
        Check the current SLA status of a review

        Returns dict with:
        - is_overdue: bool - whether deadline has passed
        - hours_remaining: float - hours until deadline
        - needs_escalation: bool - whether escalation is needed
        - escalation_level: int - current escalation level
        """
        return {
            "is_overdue": code_review.is_overdue(),
            "hours_remaining": code_review.get_hours_remaining(),
            "needs_escalation": code_review.needs_escalation(
                self.FIRST_ESCALATION_THRESHOLD
            ),
            "escalation_level": code_review.escalation_level,
            "review_id": code_review.id
        }

    def find_reviews_needing_escalation(
        self,
        reviews: List[CodeReview],
        escalation_level: int = 0
    ) -> List[CodeReview]:
        """Find all reviews that need escalation at the specified level"""
        needing_escalation = []

        for review in reviews:
            # Skip completed reviews
            if review.status in [ReviewStatus.MERGED, ReviewStatus.CLOSED, ReviewStatus.REJECTED]:
                continue

            # Check if needs escalation
            if review.needs_escalation(self.FIRST_ESCALATION_THRESHOLD):
                # For next escalation level
                if review.escalation_level == escalation_level:
                    needing_escalation.append(review)

        return needing_escalation

    def find_overdue_reviews(self, reviews: List[CodeReview]) -> List[CodeReview]:
        """Find all reviews that have exceeded their SLA deadline"""
        overdue = []

        for review in reviews:
            # Skip completed reviews
            if review.status in [ReviewStatus.MERGED, ReviewStatus.CLOSED, ReviewStatus.REJECTED]:
                continue

            if review.is_overdue():
                overdue.append(review)

        return sorted(overdue, key=lambda r: r.sla_deadline or datetime.now())

    def get_sla_summary(self, reviews: List[CodeReview]) -> dict:
        """Get a summary of SLA status across all reviews"""
        on_time = 0
        at_risk = 0
        overdue = 0
        escalated = 0

        for review in reviews:
            # Skip completed reviews
            if review.status in [ReviewStatus.MERGED, ReviewStatus.CLOSED, ReviewStatus.REJECTED]:
                continue

            if review.is_overdue():
                overdue += 1
            elif review.needs_escalation(self.FIRST_ESCALATION_THRESHOLD):
                at_risk += 1
            else:
                on_time += 1

            if review.is_escalated:
                escalated += 1

        return {
            "total_active": on_time + at_risk + overdue,
            "on_time": on_time,
            "at_risk": at_risk,
            "overdue": overdue,
            "escalated": escalated,
            "escalation_percentage": (
                escalated / (on_time + at_risk + overdue) * 100
                if (on_time + at_risk + overdue) > 0 else 0
            )
        }

    def should_send_escalation_notification(self, code_review: CodeReview) -> bool:
        """Determine if escalation notification should be sent"""
        if not code_review.needs_escalation(self.FIRST_ESCALATION_THRESHOLD):
            return False

        # Don't notify if already notified recently (within 1 hour)
        if code_review.escalation_notified_at:
            since_last_notification = datetime.now() - code_review.escalation_notified_at
            if since_last_notification < timedelta(hours=1):
                return False

        return True

    def mark_escalation_notified(self, code_review: CodeReview) -> CodeReview:
        """Mark that escalation notification was sent"""
        from dataclasses import replace
        return replace(
            code_review,
            escalation_notified_at=datetime.now(),
            updated_at=datetime.now()
        )
