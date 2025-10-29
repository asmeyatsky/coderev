"""
API Response Envelope

Architectural Intent:
- Provides a standardized response format for all API endpoints
- Ensures consistent error handling and response structure
- Makes it easier for clients to parse responses
- Includes correlation IDs for request tracing

Key Design Decisions:
1. All responses follow the same envelope structure
2. Correlation IDs are included for distributed tracing
3. Error responses include detailed error information
4. HTTP status codes align with standard conventions
"""

from typing import Optional, Any, List, Dict
from dataclasses import asdict
from datetime import datetime
from infrastructure.logging_config import get_correlation_id


class ErrorDetail:
    """Details about a specific error in the response"""

    def __init__(self, code: str, message: str, field: Optional[str] = None):
        self.code = code
        self.message = message
        self.field = field

    def to_dict(self) -> Dict[str, Any]:
        result = {"code": self.code, "message": self.message}
        if self.field:
            result["field"] = self.field
        return result


def create_success_response(
    data: Any,
    status_code: int = 200,
    message: str = "Success"
) -> tuple:
    """
    Create a successful API response

    Args:
        data: The response data/payload
        status_code: HTTP status code (default: 200)
        message: Optional success message

    Returns:
        Tuple of (response_dict, status_code)
    """
    return {
        "success": True,
        "data": data,
        "message": message,
        "correlation_id": get_correlation_id(),
        "timestamp": datetime.utcnow().isoformat()
    }, status_code


def create_error_response(
    error: str,
    status_code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[List[ErrorDetail]] = None,
    context: Optional[Dict[str, Any]] = None
) -> tuple:
    """
    Create an error API response

    Args:
        error: Error message
        status_code: HTTP status code (default: 400)
        error_code: Machine-readable error code
        details: List of detailed errors (e.g., validation errors)
        context: Additional context about the error

    Returns:
        Tuple of (response_dict, status_code)
    """
    response = {
        "success": False,
        "error": error,
        "error_code": error_code or f"ERR_{status_code}",
        "correlation_id": get_correlation_id(),
        "timestamp": datetime.utcnow().isoformat()
    }

    if details:
        response["error_details"] = [d.to_dict() for d in details]

    if context:
        response["context"] = context

    return response, status_code


def create_paginated_response(
    items: List[Any],
    total: int,
    skip: int,
    limit: int,
    status_code: int = 200
) -> tuple:
    """
    Create a paginated API response

    Args:
        items: List of items for current page
        total: Total number of items across all pages
        skip: Number of items skipped (offset)
        limit: Number of items per page
        status_code: HTTP status code (default: 200)

    Returns:
        Tuple of (response_dict, status_code)
    """
    return {
        "success": True,
        "data": items,
        "pagination": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "pages": (total + limit - 1) // limit,  # Ceiling division
            "current_page": (skip // limit) + 1
        },
        "correlation_id": get_correlation_id(),
        "timestamp": datetime.utcnow().isoformat()
    }, status_code


def validate_pagination_params(skip: int, limit: int) -> tuple[bool, Optional[str]]:
    """
    Validate pagination parameters

    Args:
        skip: Offset parameter
        limit: Limit parameter

    Returns:
        Tuple of (is_valid, error_message)
    """
    if skip < 0:
        return False, "Parameter 'skip' must be >= 0"
    if limit < 1:
        return False, "Parameter 'limit' must be >= 1"
    if limit > 100:
        return False, "Parameter 'limit' must be <= 100"
    return True, None


def validate_enum_param(value: str, enum_class, param_name: str) -> tuple[bool, Optional[Any], Optional[str]]:
    """
    Validate that a string parameter is a valid enum value

    Args:
        value: String value to validate
        enum_class: Enum class to validate against
        param_name: Name of the parameter (for error messages)

    Returns:
        Tuple of (is_valid, enum_value, error_message)
    """
    if not value:
        return True, None, None

    try:
        enum_value = enum_class[value.upper()]
        return True, enum_value, None
    except KeyError:
        valid_values = ", ".join([e.name.lower() for e in enum_class])
        return False, None, f"Parameter '{param_name}' must be one of: {valid_values}"
