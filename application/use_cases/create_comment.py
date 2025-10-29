"""
Create Comment Use Case

Architectural Intent:
- Handles the creation of comments on code reviews
- Orchestrates domain entities and services for comment creation
- Applies business rules for comment creation
- Validates input and returns appropriate DTOs

Key Design Decisions:
1. Use case orchestrates the comment creation process
2. Only one use case per specific business operation
3. Follows dependency inversion by depending on ports rather than implementations
4. Returns DTOs rather than domain entities to maintain separation
"""

from abc import ABC, abstractmethod
from typing import Protocol, Optional
from datetime import datetime

# Using absolute imports since the sys.path is modified in the presentation layer
from domain.ports.repository_ports import CommentRepositoryPort, CodeReviewRepositoryPort, UserRepositoryPort
from domain.entities.comment import Comment, CommentType
from domain.entities.user import User
from domain.entities.code_review import CodeReview
from application.dtos.dtos import CommentDTO


class CreateCommentUseCase(Protocol):
    """Protocol for creating comments"""
    
    def execute(
        self,
        content: str,
        author_id: str,
        code_review_id: str,
        parent_id: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None
    ) -> CommentDTO:
        """Execute the use case to create a new comment"""
        pass


class CreateCommentUseCaseImpl:
    """Implementation of the create comment use case"""
    
    def __init__(
        self,
        comment_repository: CommentRepositoryPort,
        code_review_repository: CodeReviewRepositoryPort,
        user_repository: UserRepositoryPort
    ):
        self.comment_repository = comment_repository
        self.code_review_repository = code_review_repository
        self.user_repository = user_repository
    
    def execute(
        self,
        content: str,
        author_id: str,
        code_review_id: str,
        parent_id: Optional[str] = None,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None
    ) -> CommentDTO:
        """Execute the use case to create a new comment"""
        
        # Validate author exists
        author = self.user_repository.find_by_id(author_id)
        if not author:
            raise ValueError(f"Author with ID {author_id} not found")
        
        # Validate code review exists
        code_review = self.code_review_repository.find_by_id(code_review_id)
        if not code_review:
            raise ValueError(f"Code review with ID {code_review_id} not found")
        
        # Determine comment type based on provided parameters
        comment_type = CommentType.GENERAL
        if file_path and line_number is not None:
            comment_type = CommentType.LINE
        elif file_path:
            comment_type = CommentType.FILE
        elif parent_id:
            comment_type = CommentType.DISCUSSION
        
        # Create the comment entity
        comment = Comment(
            id=self._generate_id(),
            content=content,
            author_id=author_id,
            code_review_id=code_review_id,
            parent_id=parent_id,
            file_path=file_path,
            line_number=line_number,
            comment_type=comment_type
        )
        
        # Save the comment
        saved_comment = self.comment_repository.save(comment)
        
        # Update the code review with incremented comment count
        updated_code_review = code_review.add_comment()
        self.code_review_repository.save(updated_code_review)
        
        # Return the DTO representation
        return self._to_dto(saved_comment)
    
    def _generate_id(self) -> str:
        """Generate a unique ID for the comment"""
        # In a real implementation, we'd use a proper ID generation strategy
        import uuid
        return str(uuid.uuid4())
    
    def _to_dto(self, comment: Comment) -> CommentDTO:
        """Convert a Comment entity to a DTO"""
        return CommentDTO(
            id=comment.id,
            content=comment.content,
            author_id=comment.author_id,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            code_review_id=comment.code_review_id,
            parent_id=comment.parent_id,
            file_path=comment.file_path,
            line_number=comment.line_number,
            is_resolved=comment.is_resolved,
            is_deleted=comment.is_deleted
        )