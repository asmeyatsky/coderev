"""
Review Priority Value Object

Architectural Intent:
- Represents the priority level of a code review
- Ensures only valid priority levels are used
- Provides type safety and validation for review priorities
- Immutable value object following DDD principles

Key Design Decisions:
1. Priority levels are predefined and validated at construction
2. Value object is immutable after creation
3. Provides utility methods for priority comparison
"""

from dataclasses import dataclass
from enum import Enum
from typing import Union


class PriorityLevel(Enum):
    """Enum for priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ReviewPriority:
    """
    ReviewPriority Value Object
    
    Invariants:
    - Priority level must be one of the predefined values
    """
    
    level: PriorityLevel
    
    def __post_init__(self):
        """Validate the priority level"""
        if not isinstance(self.level, PriorityLevel):
            try:
                # Try to convert string to PriorityLevel
                object.__setattr__(self, 'level', PriorityLevel(self.level))
            except ValueError:
                raise ValueError(f"Priority level must be a valid PriorityLevel, got {self.level}")
    
    def is_higher_priority_than(self, other: 'ReviewPriority') -> bool:
        """Check if this priority is higher than another"""
        priority_order = {
            PriorityLevel.LOW: 0,
            PriorityLevel.MEDIUM: 1,
            PriorityLevel.HIGH: 2,
            PriorityLevel.CRITICAL: 3
        }
        return priority_order[self.level] > priority_order[other.level]
    
    def is_urgent(self) -> bool:
        """Check if this priority is urgent (HIGH or CRITICAL)"""
        return self.level in [PriorityLevel.HIGH, PriorityLevel.CRITICAL]
    
    def to_string(self) -> str:
        """Get the string representation of the priority"""
        return self.level.value
    
    @staticmethod
    def from_string(level_str: str) -> 'ReviewPriority':
        """Create a ReviewPriority from a string value"""
        level_enum = PriorityLevel(level_str.lower())
        return ReviewPriority(level_enum)
    
    def __str__(self) -> str:
        """String representation"""
        return self.level.value