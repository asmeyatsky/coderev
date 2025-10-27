"""
Repository Ports

Architectural Intent:
- Define contracts for data persistence operations
- Enable separation of domain logic from infrastructure concerns
- Allow for different implementations (database, cache, etc.)
- Follow interface-first development approach

Key Design Decisions:
1. Repository interfaces are defined in domain layer
2. Implementations are in infrastructure layer
3. Methods follow CRUD patterns where appropriate
4. Domain entities are used as return types to maintain domain independence
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User
from ..entities.code_review import CodeReview
from ..entities.comment import Comment
from ..entities.risk_score import RiskScore
from ..entities.environment import Environment


class UserRepositoryPort(ABC):
    """Port for user-related data operations"""
    
    @abstractmethod
    def save(self, user: User) -> User:
        """Save a user to the repository"""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Find a user by ID"""
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        """Find a user by username"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[User]:
        """Find all users"""
        pass
    
    @abstractmethod
    def find_by_role(self, role: str) -> List[User]:
        """Find users by role"""
        pass


class CodeReviewRepositoryPort(ABC):
    """Port for code review-related data operations"""
    
    @abstractmethod
    def save(self, code_review: CodeReview) -> CodeReview:
        """Save a code review to the repository"""
        pass
    
    @abstractmethod
    def find_by_id(self, review_id: str) -> Optional[CodeReview]:
        """Find a code review by ID"""
        pass
    
    @abstractmethod
    def find_by_requester(self, requester_id: str) -> List[CodeReview]:
        """Find code reviews by requester ID"""
        pass
    
    @abstractmethod
    def find_by_reviewer(self, reviewer_id: str) -> List[CodeReview]:
        """Find code reviews assigned to a reviewer"""
        pass
    
    @abstractmethod
    def find_all_open_reviews(self) -> List[CodeReview]:
        """Find all open code reviews"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[CodeReview]:
        """Find all code reviews"""
        pass


class CommentRepositoryPort(ABC):
    """Port for comment-related data operations"""
    
    @abstractmethod
    def save(self, comment: Comment) -> Comment:
        """Save a comment to the repository"""
        pass
    
    @abstractmethod
    def find_by_id(self, comment_id: str) -> Optional[Comment]:
        """Find a comment by ID"""
        pass
    
    @abstractmethod
    def find_by_code_review(self, code_review_id: str) -> List[Comment]:
        """Find all comments for a code review"""
        pass
    
    @abstractmethod
    def find_by_author(self, author_id: str) -> List[Comment]:
        """Find comments by author"""
        pass
    
    @abstractmethod
    def find_by_parent(self, parent_id: str) -> List[Comment]:
        """Find comments that are replies to a parent comment"""
        pass


class RiskScoreRepositoryPort(ABC):
    """Port for risk score-related data operations"""
    
    @abstractmethod
    def save(self, risk_score: RiskScore) -> RiskScore:
        """Save a risk score to the repository"""
        pass
    
    @abstractmethod
    def find_by_code_review_id(self, code_review_id: str) -> Optional[RiskScore]:
        """Find a risk score by code review ID"""
        pass
    
    @abstractmethod
    def find_by_id(self, risk_score_id: str) -> Optional[RiskScore]:
        """Find a risk score by ID"""
        pass
    
    @abstractmethod
    def find_all_for_review(self, code_review_id: str) -> List[RiskScore]:
        """Find all risk scores for a code review (history)"""
        pass


class EnvironmentRepositoryPort(ABC):
    """Port for environment-related data operations"""
    
    @abstractmethod
    def save(self, environment: Environment) -> Environment:
        """Save an environment to the repository"""
        pass
    
    @abstractmethod
    def find_by_id(self, environment_id: str) -> Optional[Environment]:
        """Find an environment by ID"""
        pass
    
    @abstractmethod
    def find_by_code_review_id(self, code_review_id: str) -> Optional[Environment]:
        """Find an environment by code review ID"""
        pass
    
    @abstractmethod
    def find_all_running(self) -> List[Environment]:
        """Find all running environments"""
        pass
    
    @abstractmethod
    def find_expired(self) -> List[Environment]:
        """Find all expired environments"""
        pass