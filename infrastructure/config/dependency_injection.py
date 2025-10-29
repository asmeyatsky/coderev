"""
Dependency Injection Configuration

Architectural Intent:
- Configure and provide all necessary dependencies for the application
- Implement the dependency inversion principle
- Centralize the creation and wiring of components
- Enable easy testing with different implementations

Key Design Decisions:
1. Use a factory pattern for creating service instances
2. Maintain separation between configuration and business logic
3. Enable easy switching between implementations (in-memory, database, etc.)
4. Follow the dependency inversion principle
"""

# Using absolute imports since the sys.path is modified in the presentation layer
from infrastructure.repositories.in_memory_repositories import (
    InMemoryUserRepository,
    InMemoryCodeReviewRepository,
    InMemoryCommentRepository,
    InMemoryRiskScoreRepository,
    InMemoryEnvironmentRepository,
    InMemoryAuditLogRepository
)
from infrastructure.adapters.external_service_adapters import (
    MockRiskAnalysisServiceAdapter,
    MockEnvironmentProvisioningServiceAdapter,
    MockNotificationServiceAdapter,
    MockGitProviderServiceAdapter
)
from domain.services.review_service import ReviewDomainService
from domain.services.sla_service import SLAService
from application.use_cases.create_code_review import CreateCodeReviewUseCaseImpl
from application.use_cases.approve_code_review import ApproveCodeReviewUseCaseImpl
from application.use_cases.create_comment import CreateCommentUseCaseImpl
from application.use_cases.request_changes import RequestChangesUseCaseImpl
from application.use_cases.merge_code_review import MergeCodeReviewUseCaseImpl


class DependencyContainer:
    """Container for all dependencies in the application"""
    
    def __init__(self):
        # Repositories
        self.user_repository = InMemoryUserRepository()
        self.code_review_repository = InMemoryCodeReviewRepository()
        self.comment_repository = InMemoryCommentRepository()
        self.risk_score_repository = InMemoryRiskScoreRepository()
        self.environment_repository = InMemoryEnvironmentRepository()
        self.audit_log_repository = InMemoryAuditLogRepository()
        
        # External service adapters
        self.risk_analysis_service = MockRiskAnalysisServiceAdapter()
        self.environment_service = MockEnvironmentProvisioningServiceAdapter()
        self.notification_service = MockNotificationServiceAdapter()
        self.git_provider_service = MockGitProviderServiceAdapter()
        
        # Domain services
        self.review_service = ReviewDomainService()
        self.sla_service = SLAService()
        
        # Use cases
        self.create_code_review_use_case = CreateCodeReviewUseCaseImpl(
            self.code_review_repository,
            self.user_repository,
            self.risk_analysis_service,
            self.environment_service,
            self.git_provider_service,
            self.review_service
        )
        
        self.approve_code_review_use_case = ApproveCodeReviewUseCaseImpl(
            self.code_review_repository,
            self.user_repository,
            self.review_service
        )
        
        self.create_comment_use_case = CreateCommentUseCaseImpl(
            self.comment_repository,
            self.code_review_repository,
            self.user_repository
        )
        
        self.request_changes_use_case = RequestChangesUseCaseImpl(
            self.code_review_repository,
            self.user_repository,
            self.review_service
        )
        
        self.merge_code_review_use_case = MergeCodeReviewUseCaseImpl(
            self.code_review_repository,
            self.user_repository,
            self.git_provider_service,
            self.review_service
        )


# Global dependency container instance
container = DependencyContainer()