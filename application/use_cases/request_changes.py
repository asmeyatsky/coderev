"""
Request Changes Use Case

Architectural Intent:
- Handles the process of requesting changes on a code review
- Orchestrates domain entities and services for change requests
- Applies business rules for requesting changes
- Validates input and returns appropriate DTOs

Key Design Decisions:
1. Use case orchestrates the change request process
2. Only one use case per specific business operation
3. Follows dependency inversion by depending on ports rather than implementations
4. Enforces business rules for who can request changes
5. Returns DTOs rather than domain entities to maintain separation
"""

from abc import ABC, abstractmethod
from typing import Protocol
from datetime import datetime

# Using absolute imports since the sys.path is modified in the presentation layer
from domain.ports.repository_ports import CodeReviewRepositoryPort, UserRepositoryPort
from domain.entities.code_review import CodeReview, ReviewStatus
from domain.entities.user import User
from domain.services.review_service import ReviewDomainService
from application.dtos.dtos import CodeReviewDTO


class RequestChangesUseCase(Protocol):
    """Protocol for requesting changes on code reviews"""
    
    def execute(self, code_review_id: str, reviewer_id: str) -> CodeReviewDTO:
        """Execute the use case to request changes on a code review"""
        pass


class RequestChangesUseCaseImpl:
    """Implementation of the request changes use case"""
    
    def __init__(
        self,
        code_review_repository: CodeReviewRepositoryPort,
        user_repository: UserRepositoryPort,
        review_service: ReviewDomainService
    ):
        self.code_review_repository = code_review_repository
        self.user_repository = user_repository
        self.review_service = review_service
    
    def execute(self, code_review_id: str, reviewer_id: str) -> CodeReviewDTO:
        """Execute the use case to request changes on a code review"""
        
        # Retrieve the code review
        code_review = self.code_review_repository.find_by_id(code_review_id)
        if not code_review:
            raise ValueError(f"Code review with ID {code_review_id} not found")
        
        # Retrieve the reviewer
        reviewer = self.user_repository.find_by_id(reviewer_id)
        if not reviewer:
            raise ValueError(f"Reviewer with ID {reviewer_id} not found")
        
        # Check if the user has permission to request changes for this review
        if not self.review_service.can_user_approve_review(reviewer, code_review):
            raise PermissionError(f"User {reviewer_id} is not authorized to request changes for review {code_review_id}")
        
        # Update the code review with the change request
        updated_code_review = code_review.request_changes(reviewer_id)
        
        # Save the updated code review
        saved_code_review = self.code_review_repository.save(updated_code_review)
        
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
            status=ReviewStatusDTO(code_review.status.value),
            priority=ReviewPriorityDTO(code_review.priority.value),
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