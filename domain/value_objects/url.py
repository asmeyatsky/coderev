"""
URL Value Object

Architectural Intent:
- Represents a URL in the ECRP system
- Ensures URLs are well-formed and valid
- Provides type safety and validation for URLs
- Immutable value object following DDD principles

Key Design Decisions:
1. URL format is validated at construction using regex
2. Value object is immutable after creation
3. Provides utility methods for URL manipulation
"""

from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class URL:
    """
    URL Value Object
    
    Invariants:
    - URL must be a valid format
    - URL must not be empty
    """
    
    value: str
    
    def __post_init__(self):
        """Validate the URL format"""
        if not self.value:
            raise ValueError("URL cannot be empty")
        
        # Basic URL validation using regex
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(self.value):
            raise ValueError(f"Invalid URL format: {self.value}")
    
    def is_https(self) -> bool:
        """Check if the URL uses HTTPS protocol"""
        return self.value.lower().startswith('https://')
    
    def get_domain(self) -> Optional[str]:
        """Extract the domain from the URL"""
        # Extract domain using regex
        domain_pattern = re.compile(r'https?://([^/]+)')
        match = domain_pattern.match(self.value)
        return match.group(1) if match else None
    
    def __str__(self) -> str:
        """String representation"""
        return self.value