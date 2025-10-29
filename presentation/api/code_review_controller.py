"""
Code Review API Controller

Architectural Intent:
- Handle HTTP requests related to code reviews
- Validate incoming requests
- Orchestrate appropriate use cases
- Format responses according to API specifications
- Maintain separation between presentation and application layers

Key Design Decisions:
1. API endpoints follow REST conventions where appropriate
2. Request/response validation happens at the API layer
3. DTOs are used for data transfer between layers
4. Error handling returns appropriate HTTP status codes
"""

import sys
import os
import uuid
from typing import Dict, Any, List
from flask import Flask, request, jsonify

# Add the project root to the Python path to enable imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from application.use_cases.create_code_review import CreateCodeReviewUseCaseImpl
from application.use_cases.approve_code_review import ApproveCodeReviewUseCaseImpl
from application.use_cases.request_changes import RequestChangesUseCaseImpl
from application.use_cases.merge_code_review import MergeCodeReviewUseCaseImpl
from application.use_cases.create_comment import CreateCommentUseCaseImpl
from application.validation.code_review_validator import CodeReviewValidator, FilterValidator
from domain.entities.user import UserRole
from domain.entities.code_review import ReviewStatus, ReviewPriority
from infrastructure.config.dependency_injection import container
from infrastructure.logging_config import get_logger, set_correlation_id, log_error
from presentation.api.response_envelope import (
    create_success_response,
    create_error_response,
    create_paginated_response,
    ErrorDetail,
    validate_pagination_params,
    validate_enum_param
)

logger = get_logger(__name__)


class CodeReviewController:
    """Controller for handling code review related HTTP requests"""
    
    def __init__(self):
        self.create_code_review_use_case = container.create_code_review_use_case
        self.approve_code_review_use_case = container.approve_code_review_use_case
        self.request_changes_use_case = container.request_changes_use_case
        self.merge_code_review_use_case = container.merge_code_review_use_case
        self.create_comment_use_case = container.create_comment_use_case
    
    def register_routes(self, app: Flask):
        """Register all code review routes with the Flask app"""
        
        @app.route('/api/code-reviews', methods=['POST'])
        def create_code_review():
            """Create a new code review"""
            try:
                # Set correlation ID
                correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
                set_correlation_id(correlation_id)

                data = request.get_json()

                # Extract required fields
                title = data.get('title')
                description = data.get('description')
                source_branch = data.get('source_branch')
                target_branch = data.get('target_branch')
                requester_id = data.get('requester_id')

                # Validate required fields
                is_valid, errors = CodeReviewValidator.validate_create_request(
                    title, description, source_branch, target_branch
                )
                if not is_valid:
                    error_details = [ErrorDetail("VALIDATION_ERROR", e) for e in errors]
                    return create_error_response(
                        "Validation failed",
                        400,
                        "VALIDATION_FAILED",
                        error_details
                    )

                if not requester_id:
                    return create_error_response(
                        "Missing required field: requester_id",
                        400,
                        "MISSING_FIELD"
                    )

                logger.info(f"Creating code review: {title}")

                # Execute the use case
                result = self.create_code_review_use_case.execute(
                    title=title,
                    description=description,
                    source_branch=source_branch,
                    target_branch=target_branch,
                    requester_id=requester_id
                )

                return create_success_response(result.__dict__, 201, "Code review created successfully")
            except ValueError as e:
                log_error("CREATE_REVIEW_VALIDATION_ERROR", str(e))
                return create_error_response(str(e), 400, "VALIDATION_ERROR")
            except Exception as e:
                log_error("CREATE_REVIEW_FAILED", str(e))
                return create_error_response("Internal server error", 500, "INTERNAL_ERROR")
        
        @app.route('/api/code-reviews/<review_id>/approve', methods=['POST'])
        def approve_code_review(review_id):
            """Approve a code review"""
            try:
                # Set correlation ID
                correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
                set_correlation_id(correlation_id)

                data = request.get_json()
                reviewer_id = data.get('reviewer_id')

                if not reviewer_id:
                    return create_error_response(
                        "Missing required field: reviewer_id",
                        400,
                        "MISSING_FIELD"
                    )

                logger.info(f"Approving code review: {review_id} by {reviewer_id}")

                # Execute the use case
                result = self.approve_code_review_use_case.execute(
                    code_review_id=review_id,
                    reviewer_id=reviewer_id
                )

                return create_success_response(result.__dict__, 200, "Code review approved successfully")
            except ValueError as e:
                log_error("APPROVE_REVIEW_FAILED", str(e), {"review_id": review_id})
                return create_error_response(str(e), 400, "VALIDATION_ERROR")
            except PermissionError as e:
                log_error("APPROVE_REVIEW_PERMISSION_DENIED", str(e), {"review_id": review_id})
                return create_error_response(str(e), 403, "PERMISSION_DENIED")
            except Exception as e:
                log_error("APPROVE_REVIEW_FAILED", str(e), {"review_id": review_id})
                return create_error_response("Internal server error", 500, "INTERNAL_ERROR")
        
        @app.route('/api/code-reviews/<review_id>/request-changes', methods=['POST'])
        def request_changes(review_id):
            """Request changes for a code review"""
            try:
                # Set correlation ID
                correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
                set_correlation_id(correlation_id)

                data = request.get_json()
                reviewer_id = data.get('reviewer_id')

                if not reviewer_id:
                    return create_error_response(
                        "Missing required field: reviewer_id",
                        400,
                        "MISSING_FIELD"
                    )

                logger.info(f"Requesting changes on code review: {review_id} by {reviewer_id}")

                # Execute the use case
                result = self.request_changes_use_case.execute(
                    code_review_id=review_id,
                    reviewer_id=reviewer_id
                )

                return create_success_response(result.__dict__, 200, "Changes requested successfully")
            except ValueError as e:
                log_error("REQUEST_CHANGES_FAILED", str(e), {"review_id": review_id})
                return create_error_response(str(e), 400, "VALIDATION_ERROR")
            except PermissionError as e:
                log_error("REQUEST_CHANGES_PERMISSION_DENIED", str(e), {"review_id": review_id})
                return create_error_response(str(e), 403, "PERMISSION_DENIED")
            except Exception as e:
                log_error("REQUEST_CHANGES_FAILED", str(e), {"review_id": review_id})
                return create_error_response("Internal server error", 500, "INTERNAL_ERROR")
        
        @app.route('/api/code-reviews/<review_id>/merge', methods=['POST'])
        def merge_code_review(review_id):
            """Merge an approved code review"""
            try:
                # Set correlation ID
                correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
                set_correlation_id(correlation_id)

                data = request.get_json()
                merger_id = data.get('merger_id')

                if not merger_id:
                    return create_error_response(
                        "Missing required field: merger_id",
                        400,
                        "MISSING_FIELD"
                    )

                logger.info(f"Merging code review: {review_id} by {merger_id}")

                # Execute the use case
                result = self.merge_code_review_use_case.execute(
                    code_review_id=review_id,
                    merger_id=merger_id
                )

                return create_success_response(result.__dict__, 200, "Code review merged successfully")
            except ValueError as e:
                log_error("MERGE_REVIEW_FAILED", str(e), {"review_id": review_id})
                return create_error_response(str(e), 400, "VALIDATION_ERROR")
            except PermissionError as e:
                log_error("MERGE_REVIEW_PERMISSION_DENIED", str(e), {"review_id": review_id})
                return create_error_response(str(e), 403, "PERMISSION_DENIED")
            except Exception as e:
                log_error("MERGE_REVIEW_FAILED", str(e), {"review_id": review_id})
                return create_error_response("Internal server error", 500, "INTERNAL_ERROR")
        
        @app.route('/api/code-reviews', methods=['GET'])
        def get_all_code_reviews():
            """Get all code reviews with optional filtering, sorting, and pagination"""
            try:
                # Set correlation ID for request tracking
                correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
                set_correlation_id(correlation_id)

                # Get query parameters
                status = request.args.get('status')
                priority = request.args.get('priority')
                requester_id = request.args.get('requester_id')
                query = request.args.get('q')  # Full-text search

                try:
                    skip = int(request.args.get('skip', 0))
                    limit = int(request.args.get('limit', 20))
                except ValueError:
                    return create_error_response(
                        "Invalid pagination parameters",
                        400,
                        "INVALID_PAGINATION"
                    )

                sort_by = request.args.get('sort_by', 'created_at')
                sort_order = request.args.get('sort_order', 'desc')

                # Validate pagination
                is_valid, error = validate_pagination_params(skip, limit)
                if not is_valid:
                    return create_error_response(error, 400, "INVALID_PAGINATION")

                # Validate filters
                is_valid, errors = FilterValidator.validate_filters(status, priority)
                if not is_valid:
                    error_details = [ErrorDetail(k, v) for k, v in errors.items()]
                    return create_error_response(
                        "Invalid filter parameters",
                        400,
                        "INVALID_FILTERS",
                        error_details
                    )

                # Get repository
                code_review_repository = container.code_review_repository

                # Execute search or filter
                if query:
                    logger.info(f"Full-text search: {query}")
                    reviews = code_review_repository.search_by_text(query)
                    total = len(reviews)
                    paginated_reviews = reviews[skip:skip + limit]
                else:
                    # Convert string enums to actual enums
                    status_enum = ReviewStatus[status.upper()] if status else None
                    priority_enum = ReviewPriority[priority.upper()] if priority else None

                    logger.info(f"Filtering reviews: status={status}, priority={priority}")
                    paginated_reviews, total = code_review_repository.find_with_filters(
                        status=status_enum,
                        priority=priority_enum,
                        requester_id=requester_id,
                        skip=skip,
                        limit=limit,
                        sort_by=sort_by,
                        sort_order=sort_order
                    )

                # Convert to DTOs
                from application.use_cases.create_code_review import CreateCodeReviewUseCaseImpl
                use_case = CreateCodeReviewUseCaseImpl(
                    container.code_review_repository,
                    container.user_repository,
                    container.risk_analysis_service,
                    container.environment_service,
                    container.git_provider_service,
                    container.review_service
                )
                dtos = [use_case._to_dto(r) for r in paginated_reviews]

                return create_paginated_response(dtos, total, skip, limit, 200)
            except Exception as e:
                log_error("LIST_REVIEWS_FAILED", str(e))
                return create_error_response(
                    "Internal server error",
                    500,
                    "INTERNAL_ERROR"
                )

        @app.route('/api/code-reviews/<review_id>', methods=['GET'])
        def get_code_review(review_id):
            """Get a specific code review by ID"""
            try:
                # Set correlation ID
                correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
                set_correlation_id(correlation_id)

                logger.info(f"Fetching code review: {review_id}")

                # Get repository
                code_review_repository = container.code_review_repository
                code_review = code_review_repository.find_by_id(review_id)

                if not code_review:
                    logger.warning(f"Code review not found: {review_id}")
                    return create_error_response(
                        f"Code review with ID {review_id} not found",
                        404,
                        "NOT_FOUND"
                    )

                # Convert to DTO
                from application.use_cases.create_code_review import CreateCodeReviewUseCaseImpl
                use_case = CreateCodeReviewUseCaseImpl(
                    container.code_review_repository,
                    container.user_repository,
                    container.risk_analysis_service,
                    container.environment_service,
                    container.git_provider_service,
                    container.review_service
                )
                dto = use_case._to_dto(code_review)

                return create_success_response(dto, 200)
            except Exception as e:
                log_error("GET_REVIEW_FAILED", str(e), {"review_id": review_id})
                return create_error_response(
                    "Internal server error",
                    500,
                    "INTERNAL_ERROR"
                )
        
        @app.route('/api/code-reviews/<review_id>/comments', methods=['POST'])
        def add_comment(review_id):
            """Add a comment to a code review"""
            try:
                # Set correlation ID
                correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
                set_correlation_id(correlation_id)

                data = request.get_json()

                # Extract required fields
                content = data.get('content')
                author_id = data.get('author_id')

                if not content or not author_id:
                    missing = []
                    if not content:
                        missing.append("content")
                    if not author_id:
                        missing.append("author_id")
                    error_details = [ErrorDetail("MISSING_FIELD", f"Missing required field: {field}") for field in missing]
                    return create_error_response(
                        "Missing required fields",
                        400,
                        "MISSING_FIELDS",
                        error_details
                    )

                # Extract optional fields
                parent_id = data.get('parent_id')
                file_path = data.get('file_path')
                line_number = data.get('line_number')

                logger.info(f"Adding comment to code review: {review_id} by {author_id}")

                # Execute the use case
                result = self.create_comment_use_case.execute(
                    content=content,
                    author_id=author_id,
                    code_review_id=review_id,
                    parent_id=parent_id,
                    file_path=file_path,
                    line_number=line_number
                )

                return create_success_response(result.__dict__, 201, "Comment added successfully")
            except ValueError as e:
                log_error("ADD_COMMENT_FAILED", str(e), {"review_id": review_id})
                return create_error_response(str(e), 400, "VALIDATION_ERROR")
            except Exception as e:
                log_error("ADD_COMMENT_FAILED", str(e), {"review_id": review_id})
                return create_error_response("Internal server error", 500, "INTERNAL_ERROR")


# Initialize the controller and setup function for easy registration
controller = CodeReviewController()


def setup_routes(app: Flask):
    """Setup function to register all routes with the Flask app"""
    controller.register_routes(app)