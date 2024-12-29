"""Error handling utilities.

This module provides custom exception classes and error handling decorators
for consistent error management across the application.
"""

from typing import TypeVar, Callable, Any, cast
from functools import wraps
import logging

# Configure logging
logger = logging.getLogger(__name__)

class HunterError(Exception):
    """Custom exception class for Hunter-specific errors.
    
    This exception class is used to wrap various errors that can occur
    during content processing, providing a consistent error interface.
    
    Example:
        >>> try:
        ...     process_content()
        ... except HunterError as e:
        ...     print(f"Processing failed: {str(e)}")
    """
    pass

# Type variable for the error handler decorator
F = TypeVar('F', bound=Callable[..., Any])

def error_handler(func: F) -> F:
    """Decorator for consistent error handling.
    
    This decorator provides consistent error handling across the application,
    converting various exceptions into HunterError instances and ensuring
    proper logging.
    
    Args:
        func: The function to wrap with error handling
        
    Returns:
        Callable: Wrapped function with error handling
        
    Example:
        >>> @error_handler
        ... def risky_operation():
        ...     response = requests.get("https://example.com")
        ...     response.raise_for_status()
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise HunterError(f"Operation failed: {str(e)}")
    return cast(F, wrapper)

def async_error_handler(func: F) -> F:
    """Decorator for consistent async error handling.
    
    Similar to error_handler but designed for async functions.
    
    Args:
        func: The async function to wrap with error handling
        
    Returns:
        Callable: Wrapped async function with error handling
        
    Example:
        >>> @async_error_handler
        ... async def risky_async_operation():
        ...     async with aiohttp.ClientSession() as session:
        ...         async with session.get("https://example.com") as response:
        ...             return await response.text()
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in async {func.__name__}: {str(e)}")
            raise HunterError(f"Operation failed: {str(e)}")
    return cast(F, wrapper) 