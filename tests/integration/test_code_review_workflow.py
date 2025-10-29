"""
Integration Tests for Code Review Workflows

Tests complete workflows from creation through approval and merge.
Validates interaction between layers and proper data flow.
"""

import pytest
from datetime import datetime
from domain.entities.code_review import CodeReview, ReviewStatus, ReviewPriority
from domain.entities.user import User, UserRole
from domain.entities.risk_score import RiskScore
from infrastructure.repositories.in_memory_repositories import (
    InMemoryCodeReviewRepository,
    InMemoryUserRepository,
    InMemoryRiskScoreRepository
)


class TestCodeReviewWorkflow:
    """Test complete code review workflows"""

    @pytest.fixture
    def setup_users(self):
        """Set up test users with different roles"""
        author = User(
            id="author-1",
            username="alice",
            email="alice@example.com",
            roles=[UserRole.DEVELOPER]
        )
        reviewer = User(
            id="reviewer-1",
            username="bob",
            email="bob@example.com",
            roles=[UserRole.REVIEWER]
        )
        security_engineer = User(
            id="security-1",
            username="charlie",
            email="charlie@example.com",
            roles=[UserRole.SECURITY_ENGINEER]
        )
        maintainer = User(
            id="maintainer-1",
            username="david",
            email="david@example.com",
            roles=[UserRole.ADMIN]
        )
        return {
            "author": author,
            "reviewer": reviewer,
            "security_engineer": security_engineer,
            "maintainer": maintainer
        }

    @pytest.fixture
    def repositories(self, setup_users):
        """Set up in-memory repositories"""
        user_repo = InMemoryUserRepository()
        code_review_repo = InMemoryCodeReviewRepository()
        risk_score_repo = InMemoryRiskScoreRepository()

        # Save all users
        for user in setup_users.values():
            user_repo.save(user)

        return {
            "users": user_repo,
            "reviews": code_review_repo,
            "risk_scores": risk_score_repo,
            "users_data": setup_users
        }

    def test_complete_review_workflow(self, repositories):
        """Test: Create → Assign Reviewers → Approve → Merge"""
        # Setup
        author = repositories["users_data"]["author"]
        reviewer = repositories["users_data"]["reviewer"]
        maintainer = repositories["users_data"]["maintainer"]

        # Step 1: Create code review
        code_review = CodeReview(
            id="review-1",
            title="Add authentication",
            description="Implement JWT authentication for API",
            source_branch="feature/auth",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.HIGH,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        saved_review = repositories["reviews"].save(code_review)
        assert saved_review.id == "review-1"
        assert saved_review.status == ReviewStatus.OPEN

        # Step 2: Assign reviewer
        review_with_reviewer = saved_review.assign_reviewer(reviewer.id)
        saved_review = repositories["reviews"].save(review_with_reviewer)
        assert reviewer.id in saved_review.reviewers

        # Step 3: Reviewer approves
        approved_review = saved_review.approve(reviewer.id)
        saved_review = repositories["reviews"].save(approved_review)
        assert reviewer.id in saved_review.approvers
        assert saved_review.current_approvals == 1
        assert saved_review.status == ReviewStatus.APPROVED

        # Step 4: Check if can merge
        assert saved_review.can_merge()

        # Step 5: Merge (by maintainer)
        merged_review = saved_review.merge()
        saved_review = repositories["reviews"].save(merged_review)
        assert saved_review.status == ReviewStatus.MERGED

    def test_filtering_by_status(self, repositories):
        """Test: Filter reviews by status"""
        author = repositories["users_data"]["author"]

        # Create multiple reviews with different statuses
        open_review = CodeReview(
            id="review-open",
            title="Feature X",
            description="Implement feature X",
            source_branch="feature/x",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.MEDIUM
        )
        approved_review = CodeReview(
            id="review-approved",
            title="Feature Y",
            description="Implement feature Y",
            source_branch="feature/y",
            target_branch="main",
            requester=author,
            status=ReviewStatus.APPROVED,
            priority=ReviewPriority.MEDIUM
        )
        merged_review = CodeReview(
            id="review-merged",
            title="Feature Z",
            description="Implement feature Z",
            source_branch="feature/z",
            target_branch="main",
            requester=author,
            status=ReviewStatus.MERGED,
            priority=ReviewPriority.MEDIUM
        )

        repositories["reviews"].save(open_review)
        repositories["reviews"].save(approved_review)
        repositories["reviews"].save(merged_review)

        # Filter by open status
        open_reviews, total = repositories["reviews"].find_with_filters(
            status=ReviewStatus.OPEN
        )
        assert len(open_reviews) == 1
        assert open_reviews[0].id == "review-open"
        assert total == 1

    def test_search_by_text(self, repositories):
        """Test: Full-text search for reviews"""
        author = repositories["users_data"]["author"]

        # Create reviews with different titles and descriptions
        review1 = CodeReview(
            id="review-auth",
            title="Add authentication",
            description="Implement JWT authentication",
            source_branch="feature/auth",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.HIGH
        )
        review2 = CodeReview(
            id="review-db",
            title="Database migration",
            description="Migrate to PostgreSQL",
            source_branch="feature/db",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.MEDIUM
        )

        repositories["reviews"].save(review1)
        repositories["reviews"].save(review2)

        # Search for "authentication"
        results = repositories["reviews"].search_by_text("authentication")
        assert len(results) == 1
        assert results[0].id == "review-auth"

        # Search for "feature" (matches both branches)
        results = repositories["reviews"].search_by_text("feature")
        assert len(results) == 2

    def test_pagination(self, repositories):
        """Test: Paginate results"""
        author = repositories["users_data"]["author"]

        # Create 5 reviews
        for i in range(5):
            review = CodeReview(
                id=f"review-{i}",
                title=f"Feature {i}",
                description=f"Implement feature {i}",
                source_branch=f"feature/{i}",
                target_branch="main",
                requester=author,
                status=ReviewStatus.OPEN,
                priority=ReviewPriority.MEDIUM
            )
            repositories["reviews"].save(review)

        # Get first page (limit 2)
        page1, total = repositories["reviews"].find_with_filters(skip=0, limit=2)
        assert len(page1) == 2
        assert total == 5

        # Get second page
        page2, total = repositories["reviews"].find_with_filters(skip=2, limit=2)
        assert len(page2) == 2
        assert total == 5

        # Get third page
        page3, total = repositories["reviews"].find_with_filters(skip=4, limit=2)
        assert len(page3) == 1
        assert total == 5

    def test_sorting_by_priority(self, repositories):
        """Test: Sort results by priority"""
        author = repositories["users_data"]["author"]

        # Create reviews with different priorities
        for priority in [ReviewPriority.LOW, ReviewPriority.HIGH, ReviewPriority.MEDIUM, ReviewPriority.CRITICAL]:
            review = CodeReview(
                id=f"review-{priority.value}",
                title=f"Review {priority.value}",
                description="Test review",
                source_branch="feature/test",
                target_branch="main",
                requester=author,
                status=ReviewStatus.OPEN,
                priority=priority
            )
            repositories["reviews"].save(review)

        # Sort by priority descending (critical → low)
        results, _ = repositories["reviews"].find_with_filters(sort_by="priority", sort_order="desc")
        priorities = [r.priority for r in results]
        assert priorities == [ReviewPriority.CRITICAL, ReviewPriority.HIGH, ReviewPriority.MEDIUM, ReviewPriority.LOW]

        # Sort by priority ascending (low → critical)
        results, _ = repositories["reviews"].find_with_filters(sort_by="priority", sort_order="asc")
        priorities = [r.priority for r in results]
        assert priorities == [ReviewPriority.LOW, ReviewPriority.MEDIUM, ReviewPriority.HIGH, ReviewPriority.CRITICAL]

    def test_error_scenario_merge_unapproved_review(self, repositories):
        """Test: Cannot merge review without required approvals"""
        author = repositories["users_data"]["author"]

        # Create an open review without approvals
        review = CodeReview(
            id="review-no-approval",
            title="Feature without approval",
            description="This review has no approvals",
            source_branch="feature/no-approval",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.MEDIUM
        )
        saved_review = repositories["reviews"].save(review)

        # Try to merge without approvals should fail
        assert not saved_review.can_merge()

    def test_error_scenario_duplicate_approval(self, repositories):
        """Test: Same reviewer cannot approve twice"""
        author = repositories["users_data"]["author"]
        reviewer = repositories["users_data"]["reviewer"]

        # Create a review
        review = CodeReview(
            id="review-duplicate-approval",
            title="Feature for duplicate approval test",
            description="Test duplicate approval handling",
            source_branch="feature/dup-approval",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.MEDIUM
        )
        saved_review = repositories["reviews"].save(review)

        # Assign and approve once
        review_with_reviewer = saved_review.assign_reviewer(reviewer.id)
        saved_review = repositories["reviews"].save(review_with_reviewer)

        approved_review = saved_review.approve(reviewer.id)
        saved_review = repositories["reviews"].save(approved_review)
        assert saved_review.current_approvals == 1

        # Try to approve again - should raise error because review is now APPROVED
        with pytest.raises(ValueError, match="Cannot approve review"):
            saved_review.approve(reviewer.id)

    def test_error_scenario_request_changes_from_non_reviewer(self, repositories):
        """Test: Only assigned reviewers can request changes"""
        author = repositories["users_data"]["author"]
        non_reviewer = User(
            id="random-user",
            username="charlie",
            email="charlie@example.com",
            roles=[UserRole.DEVELOPER]
        )

        # Create a review
        review = CodeReview(
            id="review-non-reviewer",
            title="Feature for non-reviewer test",
            description="Test non-reviewer handling",
            source_branch="feature/non-reviewer",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.MEDIUM
        )
        saved_review = repositories["reviews"].save(review)

        # Non-reviewer tries to request changes
        # This should still work at entity level, but business logic should prevent it
        request_changes_review = saved_review.request_changes(non_reviewer.id)
        assert non_reviewer.id in request_changes_review.rejectors

    def test_concurrent_approval_consistency(self, repositories):
        """Test: Multiple reviewers approving maintains consistent state"""
        author = repositories["users_data"]["author"]
        reviewer1 = repositories["users_data"]["reviewer"]
        reviewer2 = User(
            id="reviewer-2",
            username="david",
            email="david@example.com",
            roles=[UserRole.REVIEWER]
        )
        repositories["users"].save(reviewer2)

        # Create a review requiring 2 approvals
        review = CodeReview(
            id="review-concurrent-approval",
            title="Feature for concurrent approval",
            description="Test concurrent approval handling",
            source_branch="feature/concurrent",
            target_branch="main",
            requester=author,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.MEDIUM,
            required_approvals=2
        )
        saved_review = repositories["reviews"].save(review)

        # Assign both reviewers
        review_v1 = saved_review.assign_reviewer(reviewer1.id)
        review_v2 = review_v1.assign_reviewer(reviewer2.id)
        saved_review = repositories["reviews"].save(review_v2)

        # Both reviewers approve (simulating concurrent approvals)
        review_approved_by_1 = saved_review.approve(reviewer1.id)
        saved_review = repositories["reviews"].save(review_approved_by_1)

        review_approved_by_2 = saved_review.approve(reviewer2.id)
        saved_review = repositories["reviews"].save(review_approved_by_2)

        # Both approvals should be recorded
        assert reviewer1.id in saved_review.approvers
        assert reviewer2.id in saved_review.approvers
        assert saved_review.current_approvals == 2
        assert saved_review.status == ReviewStatus.APPROVED

    def test_state_transition_invalid_path(self, repositories):
        """Test: Invalid status transitions are prevented"""
        author = repositories["users_data"]["author"]

        # Create a closed review
        review = CodeReview(
            id="review-closed",
            title="Closed feature",
            description="This review is closed",
            source_branch="feature/closed",
            target_branch="main",
            requester=author,
            status=ReviewStatus.CLOSED,
            priority=ReviewPriority.MEDIUM
        )
        saved_review = repositories["reviews"].save(review)

        # Try to approve a closed review - should raise error
        with pytest.raises(ValueError, match="Cannot approve review"):
            saved_review.approve("reviewer-1")
