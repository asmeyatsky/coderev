"""
External Service Adapters

Architectural Intent:
- Provide concrete implementations of external service ports
- Handle communication with external systems (Git providers, AI services, etc.)
- Adapt external service interfaces to domain service interfaces
- Maintain clean separation between domain and infrastructure

Key Design Decisions:
1. Adapters follow the ports and adapters pattern
2. Adapters handle error cases and external service specifics
3. Domain entities are converted to appropriate formats for external services
4. External service responses are converted back to domain entities
"""

import random
from typing import Optional, List
from datetime import datetime, timedelta
from ...domain.ports.external_service_ports import (
    RiskAnalysisServicePort,
    EnvironmentProvisioningServicePort,
    NotificationServicePort,
    GitProviderServicePort
)
from ...domain.entities.risk_score import RiskScore
from ...domain.entities.environment import Environment, EnvironmentStatus
from ...domain.value_objects.url import URL


class MockRiskAnalysisServiceAdapter(RiskAnalysisServicePort):
    """Mock implementation of RiskAnalysisServicePort for development"""
    
    def calculate_risk_score(self, code_review_id: str, code_diff: str) -> RiskScore:
        # In a real implementation, this would call an AI service or static analysis tool
        # For the mock, we'll generate a score based on some simple heuristics
        
        # Calculate various risk factors based on the code diff
        lines_changed = len(code_diff.split('\n')) if code_diff else 0
        complexity_score = min(100, max(0, lines_changed / 10))  # Higher for more changes
        
        # Security impact - assume 20% chance of security issues
        security_score = random.randint(0, 20)
        
        # Critical files score - check if critical files are changed
        critical_files = ['authentication', 'security', 'config', 'database']
        critical_score = 0
        for file in critical_files:
            if file in code_diff.lower():
                critical_score = random.randint(60, 80)
                break
        
        # Dataflow confidence - for simplicity, use a random value in mock
        dataflow_score = random.randint(0, 30)
        
        # Test coverage delta - assume negative for mock
        test_coverage_score = random.randint(0, 40)
        
        # Generate a unique ID for the risk score
        import uuid
        risk_score = RiskScore(
            id=str(uuid.uuid4()),
            code_review_id=code_review_id,
            code_complexity_score=complexity_score,
            security_impact_score=security_score,
            critical_files_score=critical_score,
            dataflow_confidence_score=dataflow_score,
            test_coverage_delta_score=test_coverage_score
        )
        
        return risk_score


class MockEnvironmentProvisioningServiceAdapter(EnvironmentProvisioningServicePort):
    """Mock implementation of EnvironmentProvisioningServicePort for development"""
    
    def create_environment(self, code_review_id: str, branch: str, config: dict) -> Environment:
        import uuid
        env_id = str(uuid.uuid4())
        
        # In a real implementation, this would provision actual infrastructure
        # For the mock, we'll generate a fake URL and environment
        url = f"https://review-{code_review_id[:8]}.ecrp-demo.com"
        
        environment = Environment(
            id=env_id,
            code_review_id=code_review_id,
            name=f"Review-{code_review_id[:8]}",
            description=f"Ephemeral environment for code review {code_review_id}",
            url=url,
            branch=branch,
            commit_hash=branch.split('/')[-1][:8] if branch else "unknown",  # Simplified
            services=["web", "api", "db"],  # Default services
            resources={"cpu": "2", "memory": "4Gi"},  # Default resources
            ttl_minutes=120  # 2-hour TTL
        )
        
        return environment
    
    def start_environment(self, environment_id: str) -> bool:
        # In a real implementation, this would start the actual environment
        # For mock, we'll just return True
        return True
    
    def stop_environment(self, environment_id: str) -> bool:
        # In a real implementation, this would stop the actual environment
        # For mock, we'll just return True
        return True
    
    def destroy_environment(self, environment_id: str) -> bool:
        # In a real implementation, this would destroy the actual environment
        # For mock, we'll just return True
        return True
    
    def get_environment_status(self, environment_id: str) -> EnvironmentStatus:
        # For mock, randomly return a status
        import random
        statuses = [EnvironmentStatus.RUNNING, EnvironmentStatus.PENDING, EnvironmentStatus.CREATING]
        return random.choice(statuses)
    
    def get_environment_url(self, environment_id: str) -> Optional[URL]:
        # For mock, return a sample URL
        return URL(f"https://env-{environment_id[:8]}.ecrp-demo.com")


class MockNotificationServiceAdapter(NotificationServicePort):
    """Mock implementation of NotificationServicePort for development"""
    
    def send_review_assigned_notification(self, reviewer_id: str, code_review_id: str) -> bool:
        # In a real implementation, this would send an actual notification
        # For mock, we'll just return True
        print(f"MOCK: Notification sent to reviewer {reviewer_id} for review {code_review_id}")
        return True
    
    def send_review_reminder_notification(self, reviewer_id: str, code_review_id: str) -> bool:
        # In a real implementation, this would send an actual notification
        # For mock, we'll just return True
        print(f"MOCK: Reminder notification sent to reviewer {reviewer_id} for review {code_review_id}")
        return True
    
    def send_review_escalation_notification(self, reviewer_id: str, code_review_id: str) -> bool:
        # In a real implementation, this would send an actual notification
        # For mock, we'll just return True
        print(f"MOCK: Escalation notification sent to reviewer {reviewer_id} for review {code_review_id}")
        return True
    
    def send_review_completed_notification(self, requester_id: str, code_review_id: str) -> bool:
        # In a real implementation, this would send an actual notification
        # For mock, we'll just return True
        print(f"MOCK: Completion notification sent to requester {requester_id} for review {code_review_id}")
        return True


class MockGitProviderServiceAdapter(GitProviderServicePort):
    """Mock implementation of GitProviderServicePort for development"""
    
    def create_pull_request(self, source_branch: str, target_branch: str, title: str, description: str) -> str:
        # In a real implementation, this would communicate with a Git provider API
        # For mock, we'll generate a fake PR ID
        import uuid
        pr_id = f"PR-{str(uuid.uuid4())[:8]}"
        print(f"MOCK: Created pull request {pr_id} from {source_branch} to {target_branch}")
        return pr_id
    
    def update_pull_request(self, pr_id: str, title: Optional[str] = None, description: Optional[str] = None) -> bool:
        # In a real implementation, this would update the PR via Git provider API
        # For mock, we'll just return True
        print(f"MOCK: Updated pull request {pr_id}")
        return True
    
    def get_pull_request_diff(self, pr_id: str) -> str:
        # In a real implementation, this would fetch the diff from Git provider
        # For mock, we'll return a sample diff
        return f"""
diff --git a/file.py b/file.py
index 1234567..89abcde 100644
--- a/file.py
+++ b/file.py
@@ -1,5 +1,5 @@
 def hello():
-    print("Hello")
+    print("Hello, World!")
     return "greeting"
        """
    
    def add_comment_to_pull_request(self, pr_id: str, comment: str, file_path: Optional[str] = None, line: Optional[int] = None) -> bool:
        # In a real implementation, this would add a comment via Git provider API
        # For mock, we'll just return True
        location = f" at {file_path}:{line}" if file_path and line else ""
        print(f"MOCK: Added comment to PR {pr_id}{location}: {comment}")
        return True
    
    def set_pull_request_status(self, pr_id: str, status: str, description: str, url: Optional[str] = None) -> bool:
        # In a real implementation, this would set the status via Git provider API
        # For mock, we'll just return True
        print(f"MOCK: Set PR {pr_id} status to {status}: {description}")
        return True

    def get_pull_request_status(self, pr_id: str) -> str:
        # In a real implementation, this would fetch the status from Git provider
        # For mock, we'll return a random status
        import random
        statuses = ["open", "closed", "merged", "draft"]
        return random.choice(statuses)