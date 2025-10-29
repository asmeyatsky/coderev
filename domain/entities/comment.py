"""
Comment Entity

Architectural Intent:
- Represents a comment in the code review process
- Encapsulates business rules for comment creation, modification, and threading
- Maintains invariants related to comment content and relationships
- Follows DDD principles with rich domain model

Key Design Decisions:
1. Comments are immutable after creation to maintain the integrity of the review history
2. Nested comments are supported through optional parent_id
3. Comments can be for specific files/lines in the code diff
4. Content validation happens at construction time
"""

from dataclasses import dataclass, field, replace
from typing import Optional
from datetime import datetime
from enum import Enum


class CommentType(Enum):
    """Enum for different types of comments"""
    GENERAL = "general"      # General comment about the PR
    LINE = "line"            # Comment on a specific line in the code
    FILE = "file"            # Comment on a specific file
    DISCUSSION = "discussion" # Reply to another comment


@dataclass(frozen=True)
class Comment:
    """
    Comment Domain Entity
    
    Invariants:
    - Comment must have a unique ID
    - Comment must have content
    - Comment must have an author
    - File and line information must be valid if provided
    """
    
    id: str
    content: str
    author_id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Relationships
    code_review_id: Optional[str] = None
    parent_id: Optional[str] = None  # For nested/reply comments
    file_path: Optional[str] = None  # File being commented on
    line_number: Optional[int] = None  # Line number in the file
    comment_type: CommentType = CommentType.GENERAL
    
    # Status
    is_resolved: bool = False
    is_deleted: bool = False
    
    def __post_init__(self):
        """Validate invariants after initialization"""
        if not self.id:
            raise ValueError("Comment ID cannot be empty")
        if not self.content:
            raise ValueError("Comment content cannot be empty")
        if not self.author_id:
            raise ValueError("Comment author ID cannot be empty")
        if self.line_number is not None and self.line_number < 0:
            raise ValueError("Line number must be non-negative")
    
    def update_content(self, new_content: str) -> 'Comment':
        """Update comment content, returning a new instance"""
        if not new_content:
            raise ValueError("Comment content cannot be empty")

        return replace(self, content=new_content, updated_at=datetime.now())
    
    def mark_resolved(self) -> 'Comment':
        """Mark the comment as resolved, returning a new instance"""
        return replace(self, is_resolved=True, updated_at=datetime.now())

    def mark_unresolved(self) -> 'Comment':
        """Mark the comment as unresolved, returning a new instance"""
        return replace(self, is_resolved=False, updated_at=datetime.now())

    def delete(self) -> 'Comment':
        """Mark the comment as deleted, returning a new instance"""
        return replace(self, is_deleted=True, updated_at=datetime.now())
    
    def is_reply(self) -> bool:
        """Check if this comment is a reply to another comment"""
        return self.parent_id is not None