"""
Logging Configuration Module

Architectural Intent:
- Provides centralized logging configuration for the entire ECRP platform
- Supports structured logging with correlation IDs for request tracing
- Implements different log levels for different components
- Maintains audit trails for security-sensitive operations

Key Design Decisions:
1. Centralized configuration for consistency across layers
2. Correlation IDs for distributed tracing across requests
3. Structured logging for easier analysis and searching
4. Different handlers for different log types (audit, application, error)
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps


class CorrelationIDFilter(logging.Filter):
    """Filter that adds correlation ID to all log records"""

    def __init__(self):
        super().__init__()
        self._correlation_id = None

    @property
    def correlation_id(self) -> str:
        if self._correlation_id is None:
            self._correlation_id = str(uuid.uuid4())
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, value: str):
        self._correlation_id = value

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = self.correlation_id
        return True


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured JSON logs"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", "N/A"),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add any extra fields
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        return json.dumps(log_data)


# Global correlation ID filter
_correlation_filter = CorrelationIDFilter()


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for a module"""
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(StructuredFormatter())
        console_handler.addFilter(_correlation_filter)

        logger.addHandler(console_handler)

    return logger


def set_correlation_id(correlation_id: str):
    """Set correlation ID for the current request context"""
    _correlation_filter.correlation_id = correlation_id


def get_correlation_id() -> str:
    """Get current correlation ID"""
    return _correlation_filter.correlation_id


def log_operation(operation_name: str):
    """Decorator to log operation execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.info(
                f"Starting operation: {operation_name}",
                extra={"extra_data": {"operation": operation_name, "args_count": len(args)}}
            )
            try:
                result = func(*args, **kwargs)
                logger.info(
                    f"Completed operation: {operation_name}",
                    extra={"extra_data": {"operation": operation_name, "status": "success"}}
                )
                return result
            except Exception as e:
                logger.error(
                    f"Failed operation: {operation_name}",
                    extra={"extra_data": {"operation": operation_name, "error": str(e)}},
                    exc_info=True
                )
                raise
        return wrapper
    return decorator


def log_authorization(user_id: str, resource: str, action: str, allowed: bool):
    """Log authorization decisions"""
    logger = get_logger("authorization")
    level = "INFO" if allowed else "WARNING"
    status = "ALLOWED" if allowed else "DENIED"
    logger.log(
        logging.INFO if allowed else logging.WARNING,
        f"Authorization {status}: User {user_id} attempting {action} on {resource}",
        extra={"extra_data": {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "allowed": allowed
        }}
    )


def log_state_change(entity_type: str, entity_id: str, old_state: str, new_state: str, changed_by: str):
    """Log important state changes for audit trail"""
    logger = get_logger("audit")
    logger.info(
        f"State change: {entity_type} {entity_id} transitioned from {old_state} to {new_state}",
        extra={"extra_data": {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "old_state": old_state,
            "new_state": new_state,
            "changed_by": changed_by,
            "timestamp": datetime.utcnow().isoformat()
        }}
    )


def log_error(error_type: str, message: str, context: Optional[Dict[str, Any]] = None):
    """Log errors with context"""
    logger = get_logger("error")
    extra_data = {"error_type": error_type}
    if context:
        extra_data.update(context)
    logger.error(
        message,
        extra={"extra_data": extra_data},
        exc_info=True
    )


def log_performance(operation: str, duration_ms: float, threshold_ms: float = 1000):
    """Log slow operations"""
    logger = get_logger("performance")
    level = logging.WARNING if duration_ms > threshold_ms else logging.DEBUG
    logger.log(
        level,
        f"Operation {operation} took {duration_ms:.2f}ms",
        extra={"extra_data": {
            "operation": operation,
            "duration_ms": duration_ms,
            "slow": duration_ms > threshold_ms
        }}
    )


def create_audit_log(
    entity_type: str,
    entity_id: str,
    action: str,
    actor_id: str,
    old_state: Optional[Dict[str, Any]] = None,
    new_state: Optional[Dict[str, Any]] = None,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create an audit log entry for recording domain events.

    Args:
        entity_type: Type of entity being audited (e.g., 'CodeReview', 'Comment')
        entity_id: ID of the entity being audited
        action: Action being performed (e.g., 'APPROVE', 'MERGE', 'CREATE')
        actor_id: ID of the user performing the action
        old_state: Previous state of the entity (for updates)
        new_state: New state of the entity
        description: Human-readable description of the action

    Returns:
        Dictionary with audit log data ready to be saved to repository
    """
    audit_logger = get_logger("audit")
    audit_entry = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "action": action,
        "actor_id": actor_id,
        "old_state": old_state,
        "new_state": new_state,
        "description": description or f"{action} on {entity_type} {entity_id}",
        "timestamp": datetime.now().isoformat()
    }

    audit_logger.info(
        f"Audit: {action} on {entity_type} {entity_id} by {actor_id}",
        extra={"extra_data": audit_entry}
    )

    return audit_entry
