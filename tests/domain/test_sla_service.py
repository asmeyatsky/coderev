"""
SLA Service Tests

Tests for SLA management, deadline tracking, and escalation logic.
"""

import pytest
from datetime import datetime, timedelta
from domain.entities.code_review import CodeReview, ReviewStatus, ReviewPriority
from domain.entities.user import User, UserRole
from domain.services.sla_service import SLAService


class TestSLAService:
    """Test cases for SLA Service"""

    @pytest.fixture
    def sla_service(self):
        """Create SLA service instance"""
        return SLAService()

    @pytest.fixture
    def sample_user(self):
        """Create a sample user"""
        return User(
            id="user-1",
            username="alice",
            email="alice@example.com",
            roles=[UserRole.DEVELOPER]
        )

    def test_sla_hours_by_priority(self, sla_service):
        """Test that SLA hours are correctly assigned by priority"""
        assert sla_service.calculate_sla_hours(
            CodeReview(
                id="review-1",
                title="Test",
                description="Test",
                source_branch="feature/test",
                target_branch="main",
                requester=User(id="user-1", username="test", email="test@example.com"),
                priority=ReviewPriority.CRITICAL
            )
        ) == 4

        assert sla_service.calculate_sla_hours(
            CodeReview(
                id="review-2",
                title="Test",
                description="Test",
                source_branch="feature/test",
                target_branch="main",
                requester=User(id="user-1", username="test", email="test@example.com"),
                priority=ReviewPriority.HIGH
            )
        ) == 24

        assert sla_service.calculate_sla_hours(
            CodeReview(
                id="review-3",
                title="Test",
                description="Test",
                source_branch="feature/test",
                target_branch="main",
                requester=User(id="user-1", username="test", email="test@example.com"),
                priority=ReviewPriority.MEDIUM
            )
        ) == 48

    def test_set_sla_deadline(self, sla_service, sample_user):
        """Test that SLA deadline is correctly set"""
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user,
            priority=ReviewPriority.HIGH
        )

        updated_review = sla_service.set_sla_deadline(review)

        assert updated_review.sla_deadline is not None
        assert updated_review.sla_hours_limit == 24
        # Deadline should be approximately 24 hours from now
        hours_diff = (updated_review.sla_deadline - datetime.now()).total_seconds() / 3600
        assert 23.9 < hours_diff < 24.1

    def test_is_overdue_false(self, sla_service, sample_user):
        """Test that review is not overdue when within deadline"""
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user,
            priority=ReviewPriority.MEDIUM
        )
        review_with_deadline = sla_service.set_sla_deadline(review)

        assert not review_with_deadline.is_overdue()

    def test_is_overdue_true(self, sla_service, sample_user):
        """Test that review is overdue when past deadline"""
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user,
            priority=ReviewPriority.MEDIUM,
            sla_deadline=datetime.now() - timedelta(hours=1)
        )

        assert review.is_overdue()

    def test_hours_remaining_calculation(self, sla_service, sample_user):
        """Test that hours remaining is calculated correctly"""
        future_time = datetime.now() + timedelta(hours=10)
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user,
            sla_deadline=future_time
        )

        hours_remaining = review.get_hours_remaining()
        assert 9.9 < hours_remaining < 10.1

    def test_escalate_review(self, sla_service, sample_user):
        """Test that review can be escalated"""
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user
        )

        assert not review.is_escalated
        assert review.escalation_level == 0

        escalated = review.escalate()
        assert escalated.is_escalated
        assert escalated.escalation_level == 1

    def test_multiple_escalations(self, sla_service, sample_user):
        """Test that review can be escalated multiple times"""
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user
        )

        review1 = review.escalate()
        assert review1.escalation_level == 1

        review2 = review1.escalate()
        assert review2.escalation_level == 2

    def test_needs_escalation_true(self, sla_service, sample_user):
        """Test that escalation is needed when near deadline"""
        soon_deadline = datetime.now() + timedelta(hours=2)
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user,
            status=ReviewStatus.OPEN,
            sla_deadline=soon_deadline
        )

        assert review.needs_escalation(hours_threshold=4)

    def test_needs_escalation_false_completed(self, sla_service, sample_user):
        """Test that completed reviews don't need escalation"""
        deadline = datetime.now() - timedelta(hours=1)
        review = CodeReview(
            id="review-1",
            title="Test",
            description="Test",
            source_branch="feature/test",
            target_branch="main",
            requester=sample_user,
            status=ReviewStatus.MERGED,
            sla_deadline=deadline
        )

        assert not review.needs_escalation()

    def test_find_overdue_reviews(self, sla_service, sample_user):
        """Test finding overdue reviews"""
        old_deadline = datetime.now() - timedelta(hours=1)
        future_deadline = datetime.now() + timedelta(hours=10)

        overdue_review = CodeReview(
            id="overdue-1",
            title="Overdue",
            description="Test",
            source_branch="feature/overdue",
            target_branch="main",
            requester=sample_user,
            status=ReviewStatus.OPEN,
            sla_deadline=old_deadline
        )

        on_time_review = CodeReview(
            id="on-time-1",
            title="On Time",
            description="Test",
            source_branch="feature/on-time",
            target_branch="main",
            requester=sample_user,
            status=ReviewStatus.OPEN,
            sla_deadline=future_deadline
        )

        merged_review = CodeReview(
            id="merged-1",
            title="Merged",
            description="Test",
            source_branch="feature/merged",
            target_branch="main",
            requester=sample_user,
            status=ReviewStatus.MERGED,
            sla_deadline=old_deadline
        )

        reviews = [overdue_review, on_time_review, merged_review]
        overdue_results = sla_service.find_overdue_reviews(reviews)

        assert len(overdue_results) == 1
        assert overdue_results[0].id == "overdue-1"

    def test_sla_summary(self, sla_service, sample_user):
        """Test SLA summary generation"""
        future_deadline = datetime.now() + timedelta(hours=10)
        at_risk_deadline = datetime.now() + timedelta(hours=2)
        old_deadline = datetime.now() - timedelta(hours=1)

        reviews = [
            CodeReview(
                id=f"review-{i}",
                title=f"Review {i}",
                description="Test",
                source_branch=f"feature/{i}",
                target_branch="main",
                requester=sample_user,
                status=ReviewStatus.OPEN,
                sla_deadline=future_deadline
            )
            for i in range(5)
        ]

        # Add at-risk review
        reviews.append(CodeReview(
            id="at-risk",
            title="At Risk",
            description="Test",
            source_branch="feature/at-risk",
            target_branch="main",
            requester=sample_user,
            status=ReviewStatus.OPEN,
            sla_deadline=at_risk_deadline
        ))

        # Add overdue review
        reviews.append(CodeReview(
            id="overdue",
            title="Overdue",
            description="Test",
            source_branch="feature/overdue",
            target_branch="main",
            requester=sample_user,
            status=ReviewStatus.OPEN,
            sla_deadline=old_deadline
        ))

        summary = sla_service.get_sla_summary(reviews)

        assert summary["total_active"] == 7
        assert summary["on_time"] == 5
        assert summary["at_risk"] == 1
        assert summary["overdue"] == 1
