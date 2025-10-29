"""
Code Review Input Validation

Architectural Intent:
- Centralized validation logic for code review inputs
- Enforces business rules at the application layer
- Provides detailed validation error messages
- Follows clean code principles with focused validators

Key Design Decisions:
1. Validation is separate from domain entities (prevents mixing concerns)
2. Validators return both success status and error messages
3. Supports multiple validation errors per request
4. Validation parameters are configurable constants
"""

from typing import Tuple, List, Dict
from domain.entities.code_review import ReviewStatus, ReviewPriority


class CodeReviewValidator:
    """Validator for code review inputs"""

    # Configuration constants
    MIN_TITLE_LENGTH = 5
    MAX_TITLE_LENGTH = 200
    MIN_DESCRIPTION_LENGTH = 10
    MAX_DESCRIPTION_LENGTH = 5000
    MIN_BRANCH_LENGTH = 1
    MAX_BRANCH_LENGTH = 255

    @staticmethod
    def validate_create_request(
        title: str,
        description: str,
        source_branch: str,
        target_branch: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate code review creation request

        Args:
            title: Review title
            description: Review description
            source_branch: Source branch name
            target_branch: Target branch name

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        # Validate title
        if not title:
            errors.append("Title is required")
        elif len(title) < CodeReviewValidator.MIN_TITLE_LENGTH:
            errors.append(f"Title must be at least {CodeReviewValidator.MIN_TITLE_LENGTH} characters")
        elif len(title) > CodeReviewValidator.MAX_TITLE_LENGTH:
            errors.append(f"Title must not exceed {CodeReviewValidator.MAX_TITLE_LENGTH} characters")

        # Validate description
        if not description:
            errors.append("Description is required")
        elif len(description) < CodeReviewValidator.MIN_DESCRIPTION_LENGTH:
            errors.append(f"Description must be at least {CodeReviewValidator.MIN_DESCRIPTION_LENGTH} characters")
        elif len(description) > CodeReviewValidator.MAX_DESCRIPTION_LENGTH:
            errors.append(f"Description must not exceed {CodeReviewValidator.MAX_DESCRIPTION_LENGTH} characters")

        # Validate source branch
        if not source_branch or not source_branch.strip():
            errors.append("Source branch is required")
        elif len(source_branch) > CodeReviewValidator.MAX_BRANCH_LENGTH:
            errors.append(f"Source branch name must not exceed {CodeReviewValidator.MAX_BRANCH_LENGTH} characters")

        # Validate target branch
        if not target_branch or not target_branch.strip():
            errors.append("Target branch is required")
        elif len(target_branch) > CodeReviewValidator.MAX_BRANCH_LENGTH:
            errors.append(f"Target branch name must not exceed {CodeReviewValidator.MAX_BRANCH_LENGTH} characters")

        # Validate branch uniqueness
        if source_branch and target_branch and source_branch.strip() == target_branch.strip():
            errors.append("Source and target branches must be different")

        return len(errors) == 0, errors

    @staticmethod
    def validate_comment_request(content: str) -> Tuple[bool, List[str]]:
        """
        Validate comment creation request

        Args:
            content: Comment content

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        if not content:
            errors.append("Comment content is required")
        elif len(content) < 1:
            errors.append("Comment must have at least 1 character")
        elif len(content) > 5000:
            errors.append("Comment must not exceed 5000 characters")

        return len(errors) == 0, errors


class CommentValidator:
    """Validator for comment inputs"""

    MIN_CONTENT_LENGTH = 1
    MAX_CONTENT_LENGTH = 5000

    @staticmethod
    def validate_create_request(content: str, code_review_id: str) -> Tuple[bool, List[str]]:
        """
        Validate comment creation request

        Args:
            content: Comment content
            code_review_id: Associated code review ID

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        if not content or not content.strip():
            errors.append("Comment content is required")
        elif len(content) < CommentValidator.MIN_CONTENT_LENGTH:
            errors.append(f"Comment must be at least {CommentValidator.MIN_CONTENT_LENGTH} character")
        elif len(content) > CommentValidator.MAX_CONTENT_LENGTH:
            errors.append(f"Comment must not exceed {CommentValidator.MAX_CONTENT_LENGTH} characters")

        if not code_review_id or not code_review_id.strip():
            errors.append("Code review ID is required")

        return len(errors) == 0, errors

    @staticmethod
    def validate_update_request(new_content: str) -> Tuple[bool, List[str]]:
        """
        Validate comment update request

        Args:
            new_content: Updated comment content

        Returns:
            Tuple of (is_valid, error_list)
        """
        errors = []

        if not new_content or not new_content.strip():
            errors.append("Comment content is required")
        elif len(new_content) > CommentValidator.MAX_CONTENT_LENGTH:
            errors.append(f"Comment must not exceed {CommentValidator.MAX_CONTENT_LENGTH} characters")

        return len(errors) == 0, errors


class FilterValidator:
    """Validator for filter parameters"""

    @staticmethod
    def validate_filters(
        status: str = None,
        priority: str = None
    ) -> Tuple[bool, Dict[str, str]]:
        """
        Validate filter parameters

        Args:
            status: Filter by review status
            priority: Filter by review priority

        Returns:
            Tuple of (is_valid, error_dict)
        """
        errors = {}

        if status:
            try:
                ReviewStatus[status.upper()]
            except KeyError:
                valid_statuses = ", ".join([s.name.lower() for s in ReviewStatus])
                errors["status"] = f"Invalid status. Must be one of: {valid_statuses}"

        if priority:
            try:
                ReviewPriority[priority.upper()]
            except KeyError:
                valid_priorities = ", ".join([p.name.lower() for p in ReviewPriority])
                errors["priority"] = f"Invalid priority. Must be one of: {valid_priorities}"

        return len(errors) == 0, errors
