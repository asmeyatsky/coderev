"""
In-Memory Repository Implementations

Architectural Intent:
- Provide in-memory implementations of repository ports for development and testing
- Demonstrate repository interface implementation patterns
- Enable rapid development without external dependencies
- Serve as a baseline for more sophisticated implementations

Key Design Decisions:
1. In-memory storage is suitable for MVP and testing
2. Thread-safe access using locks for concurrent operations
3. Follows the repository pattern with clean separation of concerns
4. Maintains domain entity integrity
"""

from typing import List, Optional, Dict
from threading import Lock
from domain.ports.repository_ports import (
    UserRepositoryPort,
    CodeReviewRepositoryPort,
    CommentRepositoryPort,
    RiskScoreRepositoryPort,
    EnvironmentRepositoryPort,
    AuditLogRepositoryPort
)
from domain.entities.user import User
from domain.entities.code_review import CodeReview, ReviewPriority
from domain.entities.comment import Comment
from domain.entities.risk_score import RiskScore
from domain.entities.environment import Environment, EnvironmentStatus
from domain.entities.audit_log import AuditLog


class InMemoryUserRepository(UserRepositoryPort):
    """In-memory implementation of UserRepositoryPort"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._lock = Lock()
    
    def save(self, user: User) -> User:
        with self._lock:
            self._users[user.id] = user
            return user
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._users.get(user_id)
    
    def find_by_username(self, username: str) -> Optional[User]:
        with self._lock:
            for user in self._users.values():
                if user.username == username:
                    return user
            return None
    
    def find_all(self) -> List[User]:
        with self._lock:
            return list(self._users.values())
    
    def find_by_role(self, role: str) -> List[User]:
        with self._lock:
            result = []
            for user in self._users.values():
                if any(user_role.value == role for user_role in user.roles):
                    result.append(user)
            return result


class InMemoryCodeReviewRepository(CodeReviewRepositoryPort):
    """In-memory implementation of CodeReviewRepositoryPort"""
    
    def __init__(self):
        self._code_reviews: Dict[str, CodeReview] = {}
        self._lock = Lock()
    
    def save(self, code_review: CodeReview) -> CodeReview:
        with self._lock:
            self._code_reviews[code_review.id] = code_review
            return code_review
    
    def find_by_id(self, review_id: str) -> Optional[CodeReview]:
        with self._lock:
            return self._code_reviews.get(review_id)
    
    def find_by_requester(self, requester_id: str) -> List[CodeReview]:
        with self._lock:
            result = []
            for review in self._code_reviews.values():
                if review.requester.id == requester_id:
                    result.append(review)
            return result
    
    def find_by_reviewer(self, reviewer_id: str) -> List[CodeReview]:
        with self._lock:
            result = []
            for review in self._code_reviews.values():
                if reviewer_id in review.reviewers:
                    result.append(review)
            return result
    
    def find_all_open_reviews(self) -> List[CodeReview]:
        with self._lock:
            from ...domain.entities.code_review import ReviewStatus
            result = []
            for review in self._code_reviews.values():
                if review.status in [ReviewStatus.OPEN, ReviewStatus.UNDER_REVIEW]:
                    result.append(review)
            return result
    
    def find_all(self) -> List[CodeReview]:
        with self._lock:
            return list(self._code_reviews.values())

    def find_with_filters(
        self,
        status = None,
        priority = None,
        requester_id: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> tuple:
        """
        Find reviews with filtering, sorting, and pagination

        Args:
            status: Filter by ReviewStatus enum
            priority: Filter by ReviewPriority enum
            requester_id: Filter by requester ID
            reviewer_id: Filter by reviewer ID
            skip: Number of items to skip (offset)
            limit: Number of items to return
            sort_by: Field to sort by (created_at, risk_score, priority)
            sort_order: Sort order (asc, desc)

        Returns:
            Tuple of (filtered_reviews, total_count)
        """
        with self._lock:
            results = list(self._code_reviews.values())

            # Apply filters
            if status:
                results = [r for r in results if r.status == status]
            if priority:
                results = [r for r in results if r.priority == priority]
            if requester_id:
                results = [r for r in results if r.requester.id == requester_id]
            if reviewer_id:
                results = [r for r in results if reviewer_id in r.reviewers]

            # Sort
            reverse = sort_order.lower() == "desc"
            if sort_by == "created_at":
                results.sort(key=lambda r: r.created_at, reverse=reverse)
            elif sort_by == "risk_score":
                results.sort(key=lambda r: r.risk_score or 0, reverse=reverse)
            elif sort_by == "priority":
                priority_order = {
                    ReviewPriority.LOW: 0,
                    ReviewPriority.MEDIUM: 1,
                    ReviewPriority.HIGH: 2,
                    ReviewPriority.CRITICAL: 3
                }
                results.sort(
                    key=lambda r: priority_order.get(r.priority, 0),
                    reverse=reverse
                )

            total = len(results)

            # Paginate
            paginated = results[skip:skip + limit]
            return paginated, total

    def search_by_text(self, query: str) -> List[CodeReview]:
        """
        Search reviews by title, description, or branch names

        Args:
            query: Search query string

        Returns:
            List of matching code reviews
        """
        with self._lock:
            query_lower = query.lower()
            results = []
            for review in self._code_reviews.values():
                if (query_lower in review.title.lower() or
                    query_lower in review.description.lower() or
                    query_lower in review.source_branch.lower() or
                    query_lower in review.target_branch.lower()):
                    results.append(review)
            return results


class InMemoryCommentRepository(CommentRepositoryPort):
    """In-memory implementation of CommentRepositoryPort"""
    
    def __init__(self):
        self._comments: Dict[str, Comment] = {}
        self._lock = Lock()
    
    def save(self, comment: Comment) -> Comment:
        with self._lock:
            self._comments[comment.id] = comment
            return comment
    
    def find_by_id(self, comment_id: str) -> Optional[Comment]:
        with self._lock:
            return self._comments.get(comment_id)
    
    def find_by_code_review(self, code_review_id: str) -> List[Comment]:
        with self._lock:
            result = []
            for comment in self._comments.values():
                if comment.code_review_id == code_review_id:
                    result.append(comment)
            return result
    
    def find_by_author(self, author_id: str) -> List[Comment]:
        with self._lock:
            result = []
            for comment in self._comments.values():
                if comment.author_id == author_id:
                    result.append(comment)
            return result
    
    def find_by_parent(self, parent_id: str) -> List[Comment]:
        with self._lock:
            result = []
            for comment in self._comments.values():
                if comment.parent_id == parent_id:
                    result.append(comment)
            return result


class InMemoryRiskScoreRepository(RiskScoreRepositoryPort):
    """In-memory implementation of RiskScoreRepositoryPort"""
    
    def __init__(self):
        self._risk_scores: Dict[str, RiskScore] = {}
        self._lock = Lock()
    
    def save(self, risk_score: RiskScore) -> RiskScore:
        with self._lock:
            self._risk_scores[risk_score.id] = risk_score
            return risk_score
    
    def find_by_code_review_id(self, code_review_id: str) -> Optional[RiskScore]:
        with self._lock:
            for risk_score in self._risk_scores.values():
                if risk_score.code_review_id == code_review_id:
                    return risk_score
            return None
    
    def find_by_id(self, risk_score_id: str) -> Optional[RiskScore]:
        with self._lock:
            return self._risk_scores.get(risk_score_id)
    
    def find_all_for_review(self, code_review_id: str) -> List[RiskScore]:
        with self._lock:
            result = []
            for risk_score in self._risk_scores.values():
                if risk_score.code_review_id == code_review_id:
                    result.append(risk_score)
            return result


class InMemoryEnvironmentRepository(EnvironmentRepositoryPort):
    """In-memory implementation of EnvironmentRepositoryPort"""
    
    def __init__(self):
        self._environments: Dict[str, Environment] = {}
        self._lock = Lock()
    
    def save(self, environment: Environment) -> Environment:
        with self._lock:
            self._environments[environment.id] = environment
            return environment
    
    def find_by_id(self, environment_id: str) -> Optional[Environment]:
        with self._lock:
            return self._environments.get(environment_id)
    
    def find_by_code_review_id(self, code_review_id: str) -> Optional[Environment]:
        with self._lock:
            for environment in self._environments.values():
                if environment.code_review_id == code_review_id:
                    return environment
            return None
    
    def find_all_running(self) -> List[Environment]:
        with self._lock:
            result = []
            for environment in self._environments.values():
                if environment.status == EnvironmentStatus.RUNNING:
                    result.append(environment)
            return result
    
    def find_expired(self) -> List[Environment]:
        with self._lock:
            result = []
            for environment in self._environments.values():
                if environment.is_expired():
                    result.append(environment)
            return result


class InMemoryAuditLogRepository(AuditLogRepositoryPort):
    """In-memory implementation of AuditLogRepositoryPort"""

    def __init__(self):
        self._audit_logs: Dict[str, AuditLog] = {}
        self._lock = Lock()

    def save(self, audit_log: AuditLog) -> AuditLog:
        """Save an audit log to the repository"""
        with self._lock:
            self._audit_logs[audit_log.id] = audit_log
            return audit_log

    def find_by_id(self, audit_log_id: str) -> Optional[AuditLog]:
        """Find an audit log by ID"""
        with self._lock:
            return self._audit_logs.get(audit_log_id)

    def find_by_entity(self, entity_type: str, entity_id: str) -> List[AuditLog]:
        """Find all audit logs for a specific entity"""
        with self._lock:
            result = []
            for log in self._audit_logs.values():
                if log.entity_type == entity_type and log.entity_id == entity_id:
                    result.append(log)
            return sorted(result, key=lambda x: x.created_at, reverse=True)

    def find_by_actor(self, actor_id: str) -> List[AuditLog]:
        """Find all audit logs by a specific actor"""
        with self._lock:
            result = []
            for log in self._audit_logs.values():
                if log.actor_id == actor_id:
                    result.append(log)
            return sorted(result, key=lambda x: x.created_at, reverse=True)

    def find_all(self) -> List[AuditLog]:
        """Find all audit logs"""
        with self._lock:
            return sorted(self._audit_logs.values(), key=lambda x: x.created_at, reverse=True)

    def find_by_code_review(self, code_review_id: str) -> List[AuditLog]:
        """Find all audit logs related to a code review"""
        with self._lock:
            result = []
            for log in self._audit_logs.values():
                if log.entity_type == "CodeReview" and log.entity_id == code_review_id:
                    result.append(log)
            return sorted(result, key=lambda x: x.created_at, reverse=True)