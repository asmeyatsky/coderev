"""
External Service Ports

Architectural Intent:
- Define contracts for external service integrations
- Enable separation of domain logic from infrastructure concerns
- Allow for different implementations (different providers, etc.)
- Follow interface-first development approach

Key Design Decisions:
1. Service interfaces are defined in domain layer
2. Implementations are in infrastructure layer
3. Domain entities may be transformed to external representations in adapters
4. Domain remains independent of external service details
"""

from abc import ABC, abstractmethod
from typing import Optional
from ..entities.risk_score import RiskScore
from ..entities.environment import Environment, EnvironmentStatus
from ..value_objects.url import URL


class RiskAnalysisServicePort(ABC):
    """Port for external risk analysis services (AI, static analysis, etc.)"""
    
    @abstractmethod
    def calculate_risk_score(self, code_review_id: str, code_diff: str) -> RiskScore:
        """Calculate a risk score for a code review based on the code changes"""
        pass


class EnvironmentProvisioningServicePort(ABC):
    """Port for environment provisioning services (Kubernetes, Docker, etc.)"""
    
    @abstractmethod
    def create_environment(self, code_review_id: str, branch: str, config: dict) -> Environment:
        """Create a new ephemeral environment for a code review"""
        pass
    
    @abstractmethod
    def start_environment(self, environment_id: str) -> bool:
        """Start an existing environment"""
        pass
    
    @abstractmethod
    def stop_environment(self, environment_id: str) -> bool:
        """Stop a running environment"""
        pass
    
    @abstractmethod
    def destroy_environment(self, environment_id: str) -> bool:
        """Destroy an environment and its resources"""
        pass
    
    @abstractmethod
    def get_environment_status(self, environment_id: str) -> EnvironmentStatus:
        """Get the current status of an environment"""
        pass
    
    @abstractmethod
    def get_environment_url(self, environment_id: str) -> Optional[URL]:
        """Get the access URL for an environment"""
        pass


class NotificationServicePort(ABC):
    """Port for notification services (email, Slack, etc.)"""
    
    @abstractmethod
    def send_review_assigned_notification(self, reviewer_id: str, code_review_id: str) -> bool:
        """Send a notification that a review has been assigned to a user"""
        pass
    
    @abstractmethod
    def send_review_reminder_notification(self, reviewer_id: str, code_review_id: str) -> bool:
        """Send a reminder notification for an assigned review"""
        pass
    
    @abstractmethod
    def send_review_escalation_notification(self, reviewer_id: str, code_review_id: str) -> bool:
        """Send an escalation notification for a review"""
        pass
    
    @abstractmethod
    def send_review_completed_notification(self, requester_id: str, code_review_id: str) -> bool:
        """Send a notification that a review has been completed"""
        pass


class GitProviderServicePort(ABC):
    """Port for Git provider integrations (GitHub, GitLab, Bitbucket, etc.)"""
    
    @abstractmethod
    def create_pull_request(self, source_branch: str, target_branch: str, title: str, description: str) -> str:
        """Create a pull/merge request in the Git provider"""
        pass
    
    @abstractmethod
    def update_pull_request(self, pr_id: str, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update an existing pull/merge request"""
        pass
    
    @abstractmethod
    def get_pull_request_diff(self, pr_id: str) -> str:
        """Get the diff for a pull/merge request"""
        pass
    
    @abstractmethod
    def add_comment_to_pull_request(self, pr_id: str, comment: str, file_path: Optional[str] = None, line: Optional[int] = None) -> bool:
        """Add a comment to a pull/merge request"""
        pass
    
    @abstractmethod
    def set_pull_request_status(self, pr_id: str, status: str, description: str, url: Optional[str] = None) -> bool:
        """Set the status of a pull/merge request"""
        pass

    @abstractmethod
    def get_pull_request_status(self, pr_id: str) -> str:
        """Get the status of a pull/merge request"""
        pass