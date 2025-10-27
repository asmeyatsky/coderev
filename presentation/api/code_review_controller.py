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

from typing import Dict, Any, List
from flask import Flask, request, jsonify
import sys
import os
# Add the project root to the Python path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from application.use_cases.create_code_review import CreateCodeReviewUseCaseImpl
from application.use_cases.approve_code_review import ApproveCodeReviewUseCaseImpl
from application.use_cases.request_changes import RequestChangesUseCaseImpl
from application.use_cases.merge_code_review import MergeCodeReviewUseCaseImpl
from application.use_cases.create_comment import CreateCommentUseCaseImpl
from domain.entities.user import UserRole
from infrastructure.config.dependency_injection import container


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
                data = request.get_json()
                
                # Extract required fields
                title = data.get('title')
                description = data.get('description')
                source_branch = data.get('source_branch')
                target_branch = data.get('target_branch')
                requester_id = data.get('requester_id')
                
                # Validate required fields
                if not all([title, description, source_branch, target_branch, requester_id]):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                # Execute the use case
                result = self.create_code_review_use_case.execute(
                    title=title,
                    description=description,
                    source_branch=source_branch,
                    target_branch=target_branch,
                    requester_id=requester_id
                )
                
                return jsonify(result.__dict__), 201
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                return jsonify({'error': 'Internal server error'}), 500
        
        @app.route('/api/code-reviews/<review_id>/approve', methods=['POST'])
        def approve_code_review(review_id):
            """Approve a code review"""
            try:
                data = request.get_json()
                reviewer_id = data.get('reviewer_id')
                
                if not reviewer_id:
                    return jsonify({'error': 'Missing reviewer_id'}), 400
                
                # Execute the use case
                result = self.approve_code_review_use_case.execute(
                    code_review_id=review_id,
                    reviewer_id=reviewer_id
                )
                
                return jsonify(result.__dict__), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except PermissionError as e:
                return jsonify({'error': str(e)}), 403
            except Exception as e:
                return jsonify({'error': 'Internal server error'}), 500
        
        @app.route('/api/code-reviews/<review_id>/request-changes', methods=['POST'])
        def request_changes(review_id):
            """Request changes for a code review"""
            try:
                data = request.get_json()
                reviewer_id = data.get('reviewer_id')
                
                if not reviewer_id:
                    return jsonify({'error': 'Missing reviewer_id'}), 400
                
                # Execute the use case
                result = self.request_changes_use_case.execute(
                    code_review_id=review_id,
                    reviewer_id=reviewer_id
                )
                
                return jsonify(result.__dict__), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except PermissionError as e:
                return jsonify({'error': str(e)}), 403
            except Exception as e:
                return jsonify({'error': 'Internal server error'}), 500
        
        @app.route('/api/code-reviews/<review_id>/merge', methods=['POST'])
        def merge_code_review(review_id):
            """Merge an approved code review"""
            try:
                data = request.get_json()
                merger_id = data.get('merger_id')
                
                if not merger_id:
                    return jsonify({'error': 'Missing merger_id'}), 400
                
                # Execute the use case
                result = self.merge_code_review_use_case.execute(
                    code_review_id=review_id,
                    merger_id=merger_id
                )
                
                return jsonify(result.__dict__), 200
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                return jsonify({'error': 'Internal server error'}), 500
        
        @app.route('/api/code-reviews', methods=['GET'])
        def get_all_code_reviews():
            """Get all code reviews"""
            # This would require a new use case to fetch all reviews
            # For now, this is a placeholder
            return jsonify({'message': 'Not implemented'}), 501
        
        @app.route('/api/code-reviews/<review_id>', methods=['GET'])
        def get_code_review(review_id):
            """Get a specific code review"""
            # This would require a new use case to fetch a single review
            # For now, this is a placeholder
            return jsonify({'message': f'Not implemented for review {review_id}'}), 501
        
        @app.route('/api/code-reviews/<review_id>/comments', methods=['POST'])
        def add_comment(review_id):
            """Add a comment to a code review"""
            try:
                data = request.get_json()
                
                # Extract required fields
                content = data.get('content')
                author_id = data.get('author_id')
                
                if not all([content, author_id]):
                    return jsonify({'error': 'Missing required fields'}), 400
                
                # Extract optional fields
                parent_id = data.get('parent_id')
                file_path = data.get('file_path')
                line_number = data.get('line_number')
                
                # Execute the use case
                result = self.create_comment_use_case.execute(
                    content=content,
                    author_id=author_id,
                    code_review_id=review_id,
                    parent_id=parent_id,
                    file_path=file_path,
                    line_number=line_number
                )
                
                return jsonify(result.__dict__), 201
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            except Exception as e:
                return jsonify({'error': 'Internal server error'}), 500


# Initialize the controller and setup function for easy registration
controller = CodeReviewController()


def setup_routes(app: Flask):
    """Setup function to register all routes with the Flask app"""
    controller.register_routes(app)