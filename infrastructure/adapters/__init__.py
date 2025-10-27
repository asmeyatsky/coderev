"""
ECRP Infrastructure Adapters

This module contains all external service adapters for the Enhanced Code Review Platform.
Following the Clean Architecture principles and architectural guidelines:
- Implements domain service ports with concrete external service integrations
- Handles communication with external services (Git providers, AI services, etc.)
- Maintains independence from application and domain layers
- Provides the "driving" and "driven" adapter implementations
"""