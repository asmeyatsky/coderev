"""
Data Transfer Objects

Architectural Intent:
- Transfer data between application layer and presentation/infrastructure layers
- Represent data structures optimized for specific use cases
- Maintain separation between domain entities and external representations
- Follow clean architecture principles

Key Design Decisions:
1. DTOs are separate from domain entities
2. DTOs can include serialization/deserialization logic
3. DTOs are optimized for specific operations or external interfaces
4. DTOs maintain a clear contract between layers
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Set
from enum import Enum


class ReviewStatusDTO(Enum):
    """DTO for review status"""
    DRAFT = "draft"
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    NEEDS_WORK = "needs_work"
    APPROVED = "approved"
    REJECTED = "rejected"
    MERGED = "merged"
    CLOSED = "closed"


class ReviewPriorityDTO(Enum):
    """DTO for review priority"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class UserDTO:
    """DTO for user data"""
    id: str
    username: str
    email: str
    roles: List[str]
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class CodeReviewDTO:
    """DTO for code review data"""
    id: str
    title: str
    description: str
    source_branch: str
    target_branch: str
    requester_id: str
    created_at: datetime
    updated_at: datetime
    
    # Status and metadata
    status: ReviewStatusDTO
    priority: ReviewPriorityDTO
    
    # Review tracking
    reviewers: List[str]  # IDs of assigned reviewers
    approvers: List[str]  # IDs of users who approved
    rejectors: List[str]  # IDs of users who rejected
    required_approvals: int
    current_approvals: int
    
    # Risk scoring
    risk_score: Optional[float] = None
    security_approval_required: bool = False
    qa_approval_required: bool = False
    
    # Additional metadata
    labels: List[str] = None
    comments_count: int = 0
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0
    
    # Ephemeral environment
    ephemeral_environment_url: Optional[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []


@dataclass
class CommentDTO:
    """DTO for comment data"""
    id: str
    content: str
    author_id: str
    created_at: datetime
    updated_at: datetime
    
    # Relationships
    code_review_id: Optional[str] = None
    parent_id: Optional[str] = None  # For nested/reply comments
    file_path: Optional[str] = None  # File being commented on
    line_number: Optional[int] = None  # Line number in the file
    
    # Status
    is_resolved: bool = False
    is_deleted: bool = False


@dataclass
class RiskScoreDTO:
    """DTO for risk score data"""
    id: str
    code_review_id: str
    calculated_at: datetime
    
    # Risk factors as defined in PRD section 2.4
    code_complexity_score: float  # W_1: Cyclomatic complexity, etc.
    security_impact_score: float  # W_2: Security vulnerabilities
    critical_files_score: float   # W_3: Changes to high-risk files
    dataflow_confidence_score: float  # W_4: Confidence in analysis
    test_coverage_delta_score: float  # W_5: Changes in test coverage
    
    # Weights for each factor (should sum to 1.0)
    code_complexity_weight: float
    security_impact_weight: float
    critical_files_weight: float
    dataflow_confidence_weight: float
    test_coverage_delta_weight: float
    
    # Calculated values
    overall_score: float
    risk_level: str  # Low, Medium, High, Critical


@dataclass
class EnvironmentDTO:
    """DTO for environment data"""
    id: str
    code_review_id: str
    created_at: datetime
    updated_at: datetime
    
    # Environment properties
    name: Optional[str] = None
    description: Optional[str] = None
    status: str = "pending"  # Using string as it will be serialized
    ttl_minutes: int = 120  # Default 2-hour TTL
    
    # Access information
    url: Optional[str] = None
    ssh_access_url: Optional[str] = None
    
    # Environment configuration
    branch: Optional[str] = None
    commit_hash: Optional[str] = None
    services: List[str] = None  # List of services in the environment
    resources: dict = None  # Resource allocation specs
    
    # Lifecycle management
    expires_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.services is None:
            self.services = []
        if self.resources is None:
            self.resources = {}