"""
Create Code Review Use Case

Architectural Intent:
- Handles the creation of new code reviews
- Orchestrates domain entities and services for review creation
- Applies business rules for review creation
- Validates input and returns appropriate DTOs

Key Design Decisions:
1. Use case orchestrates the creation process
2. Only one use case per specific business operation
3. Follows dependency inversion by depending on ports rather than implementations
4. Returns DTOs rather than domain entities to maintain separation
"""

from abc import ABC, abstractmethod
from typing import Protocol
from datetime import datetime

from ..dtos.dtos import CodeReviewDTO, UserDTO
from ...domain.ports.repository_ports import CodeReviewRepositoryPort, UserRepositoryPort
from ...domain.ports.external_service_ports import (
    RiskAnalysisServicePort,
    EnvironmentProvisioningServicePort,
    GitProviderServicePort
)
from ...domain.entities.code_review import CodeReview, ReviewStatus, ReviewPriority
from ...domain.entities.user import User
from ...domain.services.review_service import ReviewDomainService


class CreateCodeReviewUseCase(Protocol):
    """Protocol for creating code reviews"""
    
    def execute(
        self,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        requester_id: str
    ) -> CodeReviewDTO:
        """Execute the use case to create a new code review"""
        pass


class CreateCodeReviewUseCaseImpl:
    """Implementation of the create code review use case"""
    
    def __init__(
        self,
        code_review_repository: CodeReviewRepositoryPort,
        user_repository: UserRepositoryPort,
        risk_analysis_service: RiskAnalysisServicePort,
        environment_service: EnvironmentProvisioningServicePort,
        git_provider_service: GitProviderServicePort,
        review_service: ReviewDomainService
    ):
        self.code_review_repository = code_review_repository
        self.user_repository = user_repository
        self.risk_analysis_service = risk_analysis_service
        self.environment_service = environment_service
        self.git_provider_service = git_provider_service
        self.review_service = review_service
    
    def execute(
        self,
        title: str,
        description: str,
        source_branch: str,
        target_branch: str,
        requester_id: str
    ) -> CodeReviewDTO:
        """Execute the use case to create a new code review"""
        
        # Validate requester exists
        requester = self.user_repository.find_by_id(requester_id)
        if not requester:
            raise ValueError(f"Requester with ID {requester_id} not found")
        
        # Create the initial code review entity
        code_review = CodeReview(
            id=self._generate_id(),  # In a real implementation, we'd have a proper ID generator
            title=title,
            description=description,
            source_branch=source_branch,
            target_branch=target_branch,
            requester=requester,
            status=ReviewStatus.OPEN,
            priority=ReviewPriority.MEDIUM
        )
        
        # Save the initial version to get a persistent ID
        code_review = self.code_review_repository.save(code_review)
        
        # Get the code diff from the Git provider
        code_diff = self.git_provider_service.get_pull_request_diff(code_review.id)
        
        # Calculate risk score using the risk analysis service
        risk_score = self.risk_analysis_service.calculate_risk_score(code_review.id, code_diff)
        
        # Update the code review with the risk score
        code_review = code_review.set_risk_score(risk_score.overall_score)
        
        # Determine if special approvals are needed based on risk
        if risk_score.needs_security_review():
            code_review = CodeReview(
                id=code_review.id,
                title=code_review.title,
                description=code_review.description,
                source_branch=code_review.source_branch,
                target_branch=code_review.target_branch,
                requester=code_review.requester,
                created_at=code_review.created_at,
                updated_at=datetime.now(),
                status=code_review.status,
                priority=code_review.priority,
                reviewers=code_review.reviewers,
                approvers=code_review.approvers,
                rejectors=code_review.rejectors,
                required_approvals=code_review.required_approvals,
                current_approvals=code_review.current_approvals,
                risk_score=code_review.risk_score,
                security_approval_required=True,
                qa_approval_required=code_review.qa_approval_required,
                labels=code_review.labels,
                comments_count=code_review.comments_count,
                files_changed=code_review.files_changed,
                additions=code_review.additions,
                deletions=code_review.deletions,
                ephemeral_environment_url=code_review.ephemeral_environment_url
            )
        
        if risk_score.needs_qa_review():
            code_review = CodeReview(
                id=code_review.id,
                title=code_review.title,
                description=code_review.description,
                source_branch=code_review.source_branch,
                target_branch=code_review.target_branch,
                requester=code_review.requester,
                created_at=code_review.created_at,
                updated_at=datetime.now(),
                status=code_review.status,
                priority=code_review.priority,
                reviewers=code_review.reviewers,
                approvers=code_review.approvers,
                rejectors=code_review.rejectors,
                required_approvals=code_review.required_approvals,
                current_approvals=code_review.current_approvals,
                risk_score=code_review.risk_score,
                security_approval_required=code_review.security_approval_required,
                qa_approval_required=True,
                labels=code_review.labels,
                comments_count=code_review.comments_count,
                files_changed=code_review.files_changed,
                additions=code_review.additions,
                deletions=code_review.deletions,
                ephemeral_environment_url=code_review.ephemeral_environment_url
            )
        
        # Determine required reviewers based on risk and other factors
        available_users = self.user_repository.find_all()
        required_reviewers = self.review_service.calculate_required_reviewers(
            code_review,
            risk_score,
            available_users
        )
        
        # Assign reviewers to the code review
        for reviewer_id in required_reviewers:
            code_review = code_review.assign_reviewer(reviewer_id)
        
        # Update the number of required approvals based on the number of assigned reviewers
        code_review = CodeReview(
            id=code_review.id,
            title=code_review.title,
            description=code_review.description,
            source_branch=code_review.source_branch,
            target_branch=code_review.target_branch,
            requester=code_review.requester,
            created_at=code_review.created_at,
            updated_at=datetime.now(),
            status=code_review.status,
            priority=code_review.priority,
            reviewers=code_review.reviewers,
            approvers=code_review.approvers,
            rejectors=code_review.rejectors,
            required_approvals=len(required_reviewers),
            current_approvals=code_review.current_approvals,
            risk_score=code_review.risk_score,
            security_approval_required=code_review.security_approval_required,
            qa_approval_required=code_review.qa_approval_required,
            labels=code_review.labels,
            comments_count=code_review.comments_count,
            files_changed=code_review.files_changed,
            additions=code_review.additions,
            deletions=code_review.deletions,
            ephemeral_environment_url=code_review.ephemeral_environment_url
        )
        
        # Create an ephemeral environment for the code review
        environment = self.environment_service.create_environment(
            code_review.id,
            source_branch,
            {}  # Configuration would come from the repository
        )
        
        # Update the code review with the environment URL
        code_review = code_review.set_ephemeral_environment_url(environment.url)
        
        # Save the updated code review
        code_review = self.code_review_repository.save(code_review)
        
        # Return the DTO representation
        return self._to_dto(code_review)
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the code review"""
        # In a real implementation, we'd use a proper ID generation strategy
        import uuid
        return str(uuid.uuid4())
    
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