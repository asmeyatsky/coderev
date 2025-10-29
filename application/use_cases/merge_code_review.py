"""
Merge Code Review Use Case

Architectural Intent:
- Handles the merging of approved code reviews
- Orchestrates domain entities and services for review merging
- Applies business rules for review merging
- Validates that all requirements are met before merging
- Returns appropriate DTOs

Key Design Decisions:
1. Use case orchestrates the merge process
2. Only one use case per specific business operation
3. Follows dependency inversion by depending on ports rather than implementations
4. Enforces all business rules before allowing merge
5. Returns DTOs rather than domain entities to maintain separation
"""

from abc import ABC, abstractmethod
from typing import Protocol
from datetime import datetime

# Using absolute imports since the sys.path is modified in the presentation layer
from domain.ports.repository_ports import CodeReviewRepositoryPort, UserRepositoryPort
from domain.ports.external_service_ports import GitProviderServicePort
from domain.entities.code_review import CodeReview, ReviewStatus
from domain.entities.user import User, UserRole
from domain.services.review_service import ReviewDomainService
from application.dtos.dtos import CodeReviewDTO, ReviewStatusDTO, ReviewPriorityDTO


class MergeCodeReviewUseCase(Protocol):
    """Protocol for merging code reviews"""
    
    def execute(self, code_review_id: str, merger_id: str) -> CodeReviewDTO:
        """Execute the use case to merge a code review"""
        pass


class MergeCodeReviewUseCaseImpl:
    """Implementation of the merge code review use case"""
    
    def __init__(
        self,
        code_review_repository: CodeReviewRepositoryPort,
        user_repository: UserRepositoryPort,
        git_provider_service: GitProviderServicePort,
        review_service: ReviewDomainService
    ):
        self.code_review_repository = code_review_repository
        self.user_repository = user_repository
        self.git_provider_service = git_provider_service
        self.review_service = review_service
    
    def execute(self, code_review_id: str, merger_id: str) -> CodeReviewDTO:
        """Execute the use case to merge a code review"""
        
        # Retrieve the code review
        code_review = self.code_review_repository.find_by_id(code_review_id)
        if not code_review:
            raise ValueError(f"Code review with ID {code_review_id} not found")
        
        # Retrieve the user performing the merge
        merger = self.user_repository.find_by_id(merger_id)
        if not merger:
            raise ValueError(f"Merger with ID {merger_id} not found")
        
        # Check if the code review can be merged according to business rules
        if not code_review.can_merge():
            raise ValueError(f"Code review {code_review_id} does not meet requirements for merging")

        # Check if the merger has permission to merge
        # Typically only the requester, admins, or merge maintainers can merge
        if merger.id != code_review.requester.id and UserRole.ADMIN not in merger.roles:
            raise PermissionError(f"User {merger_id} does not have permission to merge this review")

        # If security approval was required, verify it was obtained
        if code_review.security_approval_required:
            has_security_approval = any(
                self.user_repository.find_by_id(approver_id) and
                UserRole.SECURITY_ENGINEER in self.user_repository.find_by_id(approver_id).roles
                for approver_id in code_review.approvers
            )
            if not has_security_approval:
                raise ValueError("Security approval is required but was not obtained")

        # If QA approval was required, verify it was obtained
        if code_review.qa_approval_required:
            has_qa_approval = any(
                self.user_repository.find_by_id(approver_id) and
                UserRole.QA_ENGINEER in self.user_repository.find_by_id(approver_id).roles
                for approver_id in code_review.approvers
            )
            if not has_qa_approval:
                raise ValueError("QA approval is required but was not obtained")
        
        # Update the code review status to merged
        merged_code_review = code_review.merge()
        
        # Attempt to merge the pull request in the Git provider
        # This would be the actual merge operation in the Git provider (GitHub, GitLab, etc.)
        pr_merged = self.git_provider_service.set_pull_request_status(
            code_review_id,
            "success",
            "Successfully merged by ECRP",
            merged_code_review.ephemeral_environment_url
        )
        
        if not pr_merged:
            # If the Git provider merge failed, we might want to handle this differently
            # For now, we'll proceed with updating our internal state
            pass
        
        # Save the updated code review
        saved_code_review = self.code_review_repository.save(merged_code_review)
        
        # Return the DTO representation
        return self._to_dto(saved_code_review)
    
    def _to_dto(self, code_review: CodeReview) -> CodeReviewDTO:
        """Convert a CodeReview entity to a DTO"""
        return CodeReviewDTO(
            id=code_review.id,
            title=code_review.title,
            description=code_review.description,
            source_branch=code_review.source_branch,
            target_branch=code_review.target_branch,
            requester_id=code_review.requester.id,
            created_at=code_review.created_at,
            updated_at=code_review.updated_at,
            status=ReviewStatusDTO[code_review.status.name],
            priority=ReviewPriorityDTO[code_review.priority.name],
            reviewers=list(code_review.reviewers),
            approvers=list(code_review.approvers),
            rejectors=list(code_review.rejectors),
            required_approvals=code_review.required_approvals,
            current_approvals=code_review.current_approvals,
            risk_score=code_review.risk_score,
            security_approval_required=code_review.security_approval_required,
            qa_approval_required=code_review.qa_approval_required,
            labels=list(code_review.labels),
            comments_count=code_review.comments_count,
            files_changed=code_review.files_changed,
            additions=code_review.additions,
            deletions=code_review.deletions,
            ephemeral_environment_url=code_review.ephemeral_environment_url
        )