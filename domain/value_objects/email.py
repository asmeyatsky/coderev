"""
Email Value Object

Architectural Intent:
- Represents an email address in the ECRP system
- Ensures email addresses are well-formed and valid
- Provides type safety and validation for email addresses
- Immutable value object following DDD principles

Key Design Decisions:
1. Email format is validated at construction using regex
2. Value object is immutable after creation
3. Provides utility methods for email manipulation
"""

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class Email:
    """
    Email Value Object
    
    Invariants:
    - Email must be a valid format
    - Email must not be empty
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the email format"""
        if not self.value:
            raise ValueError("Email cannot be empty")
        
        # Basic email validation using regex
        email_pattern = re.compile(
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        if not email_pattern.match(self.value):
            raise ValueError(f"Invalid email format: {self.value}")
    
    def get_domain(self) -> Optional[str]:
        """Extract the domain from the email"""
        try:
            return self.value.split('@')[1]
        except IndexError:
            return None
    
    def get_local_part(self) -> Optional[str]:
        """Extract the local part (before @) from the email"""
        try:
            return self.value.split('@')[0]
        except IndexError:
            return None
    
    def __str__(self) -> str:
        """String representation"""
        return self.value