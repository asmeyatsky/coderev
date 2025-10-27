"""
Review Domain Service

Architectural Intent:
- Contains complex business logic related to code reviews that doesn't fit in the CodeReview entity
- Coordinates operations that span multiple entities
- Implements business rules that require domain knowledge
- Follows DDD principles with rich domain model

Key Design Decisions:
1. Service is stateless and focused on specific business operations
2. Encapsulates complex review coordination logic
3. Coordinates between CodeReview, Comment, and other entities
4. Validates business rules across multiple entities
"""

from typing import List, Optional, Set
from datetime import datetime
from ..entities.user import User, UserRole
from ..entities.code_review import CodeReview, ReviewStatus
from ..entities.comment import Comment
from ..entities.risk_score import RiskScore


class ReviewDomainService:
    """
    ReviewDomainService contains business logic for code review operations
    """
    
    def calculate_required_reviewers(
        self,
        code_review: CodeReview,
        risk_score: Optional[RiskScore] = None,
        available_users: List[User] = None
    ) -> Set[str]:
        """
        Calculate the required reviewers for a code review based on various factors
        """
        required_reviewers = set()
        
        # Add the author's team members as potential reviewers (avoid self-review)
        # This is a simplified logic - in real implementation, we'd have team structures
        
        # If security changes are detected, require a security engineer
        if risk_score and risk_score.needs_security_review():
            security_engineers = [user for user in available_users or [] if UserRole.SECURITY_ENGINEER in user.roles]
            if security_engineers:
                # For now, add the first available security engineer
                required_reviewers.add(security_engineers[0].id)
        
        # If QA review is needed, require a QA engineer
        if risk_score and risk_score.needs_qa_review():
            qa_engineers = [user for user in available_users or [] if UserRole.QA_ENGINEER in user.roles]
            if qa_engineers:
                # For now, add the first available QA engineer
                required_reviewers.add(qa_engineers[0].id)
        
        # If no specific requirements, add regular reviewers
        if not required_reviewers and available_users:
            # Find non-security, non-QA reviewers
            regular_reviewers = [
                user for user in available_users
                if UserRole.REVIEWER in user.roles
                and user.id != code_review.requester.id  # Don't add the requester as reviewer
            ]
            
            # Add at least one regular reviewer if available
            if regular_reviewers:
                required_reviewers.add(regular_reviewers[0].id)
        
        return required_reviewers
    
    def can_user_approve_review(self, user: User, code_review: CodeReview) -> bool:
        """
        Check if a user has permission to approve a specific code review
        """
        # Basic check: user must be assigned as a reviewer
        if user.id not in code_review.reviewers:
            return False
        
        # If the review is security-sensitive, only security engineers can approve
        if code_review.security_approval_required and UserRole.SECURITY_ENGINEER not in user.roles:
            return False
        
        # If the review is QA-sensitive, only QA engineers can approve
        if code_review.qa_approval_required and UserRole.QA_ENGINEER not in user.roles:
            return False
        
        # User cannot approve their own review
        if user.id == code_review.requester.id:
            return False
        
        return True
    
    def can_user_view_review(self, user: User, code_review: CodeReview) -> bool:
        """
        Check if a user has permission to view a specific code review
        """
        # Requester can always view their own review
        if user.id == code_review.requester.id:
            return True
        
        # Reviewers assigned to the review can view it
        if user.id in code_review.reviewers:
            return True
        
        # Admins can view any review
        if UserRole.ADMIN in user.roles:
            return True
        
        # Users with relevant roles might have access based on other criteria
        # In a full implementation, we'd check team memberships, etc.
        return False
    
    def calculate_review_time_estimate(self, code_review: CodeReview) -> int:
        """
        Estimate the time needed to complete this review in minutes
        """
        # Base time estimate
        time_estimate = 15  # 15 minutes base
        
        # Add time based on the number of files changed
        time_estimate += code_review.files_changed * 5
        
        # Add time based on additions/deletions
        lines_changed = code_review.additions + code_review.deletions
        if lines_changed > 500:  # More than 500 lines
            time_estimate += 60  # Extra hour
        elif lines_changed > 200:  # More than 200 lines
            time_estimate += 30  # Extra 30 minutes
        elif lines_changed > 50:  # More than 50 lines
            time_estimate += 15  # Extra 15 minutes
        
        # Add time if risk score is high
        if code_review.risk_score and code_review.risk_score > 70:
            time_estimate *= 2  # Double the time for high-risk reviews
        
        # Adjust for priority
        if code_review.priority == "high":
            time_estimate = int(time_estimate * 0.75)  # 25% less time for high priority (faster review)
        elif code_review.priority == "critical":
            time_estimate = int(time_estimate * 0.5)   # 50% less time for critical (urgent review)
        
        return time_estimate
    
    def should_escalate_review(self, code_review: CodeReview) -> bool:
        """
        Determine if a review should be escalated based on aging and other factors
        """
        # Calculate time since creation
        time_since_creation = datetime.now() - code_review.created_at
        
        # Escalate if:
        # 1. Review is older than estimated time * 2
        # 2. Review is high risk
        # 3. Review is high or critical priority
        estimated_time_minutes = self.calculate_review_time_estimate(code_review)
        estimated_time_threshold = estimated_time_minutes * 2  # 2x the estimated time
        
        is_aged = time_since_creation.total_seconds() / 60 > estimated_time_threshold
        is_high_risk = code_review.risk_score and code_review.risk_score > 70
        is_urgent_priority = code_review.priority in ["high", "critical"]
        is_not_approved = code_review.status not in [ReviewStatus.APPROVED, ReviewStatus.MERGED]
        
        return is_aged and (is_high_risk or is_urgent_priority) and is_not_approved
    
    def get_review_sla_deadline(self, code_review: CodeReview) -> datetime:
        """
        Calculate the SLA deadline for this review
        """
        # Base SLA is 4 hours for normal reviews
        base_sla_hours = 4
        
        # Adjust based on priority
        if code_review.priority == "high":
            base_sla_hours = 2
        elif code_review.priority == "critical":
            base_sla_hours = 1
        
        # Adjust based on risk
        if code_review.risk_score and code_review.risk_score > 80:
            base_sla_hours *= 2  # High-risk reviews get more time
        
        return code_review.created_at + datetime.timedelta(hours=base_sla_hours)
    
    def is_review_overdue(self, code_review: CodeReview) -> bool:
        """
        Check if a review has passed its SLA deadline
        """
        deadline = self.get_review_sla_deadline(code_review)
        return datetime.now() > deadline