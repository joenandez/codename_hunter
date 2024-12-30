"""Utility modules for the Hunter application.

This package contains various utility modules:
- errors: Error handling and custom exceptions
- fetcher: Async HTTP request handling
- progress: Progress tracking with rich output
- ai: AI enhancement utilities
"""

from typing import Dict, Any
from .errors import HunterError, error_handler, async_error_handler
from .progress import ProgressManager
from .fetcher import fetch_url_async
from .ai import AIEnhancer, TokenInfo

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration dictionary.
    
    Args:
        config: Dictionary containing configuration values
        
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    required_fields = {'api_key', 'output_format'}
    return all(field in config for field in required_fields)

__all__ = [
    'HunterError',
    'error_handler',
    'async_error_handler',
    'ProgressManager',
    'fetch_url_async',
    'AIEnhancer',
    'TokenInfo',
    'validate_config',
] 