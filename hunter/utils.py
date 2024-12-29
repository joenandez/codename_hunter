"""Utility functions for the application.

This module provides utility functions and classes for:
1. AI content enhancement
2. Progress tracking
3. Error handling
4. Token management
5. Configuration validation

The utilities are designed to be reusable across the application and provide
consistent behavior for common operations.

Example:
    >>> with ProgressManager() as progress:
    ...     progress.update("Processing...")
    ...     result = process_content()
    
    >>> enhancer = AIEnhancer()
    >>> enhanced = enhancer.enhance_content("Some content")
"""

from typing import Optional, Dict, Any, Callable, TypeVar, cast
import logging
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from functools import wraps
try:
    # When installed via pip
    from hunter.constants import (
        TOGETHER_API_KEY,
        TOGETHER_MODEL,
        TOGETHER_MAX_TOKENS,
        TOGETHER_TEMPERATURE
    )
except ImportError:
    # When run directly from source
    from .constants import (
        TOGETHER_API_KEY,
        TOGETHER_MODEL,
        TOGETHER_MAX_TOKENS,
        TOGETHER_TEMPERATURE
    )

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
console = Console()

@dataclass
class TokenInfo:
    """Information about token usage and limits.
    
    This class tracks token usage for AI operations, helping to manage
    rate limits and costs.
    
    Attributes:
        total_tokens (int): Total number of tokens used
        content_tokens (int): Tokens used for content (excluding system tokens)
        remaining_tokens (int): Tokens remaining in the current quota
    """
    total_tokens: int
    content_tokens: int
    remaining_tokens: int

class AIEnhancer:
    """Handles AI-based content enhancement operations using Together API."""
    
    def enhance_content(self, content: str) -> str:
        """Enhance content using Together AI if API key is available.
        
        Args:
            content: The content to enhance
            
        Returns:
            str: Enhanced content or original if enhancement fails
        """
        if not TOGETHER_API_KEY:
            logger.warning("No API key available for AI enhancement")
            return content
            
        try:
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            messages = [{
                "role": "system",
                "content": """You are a markdown formatting expert. Improve the formatting while preserving all information and links. Focus on:
1. Consistent spacing between sections
2. Beautiful list formatting
3. Proper code block presentation
4. Clear section hierarchy
5. Clean link and inline code formatting

Return ONLY the raw markdown content."""
            }, {
                "role": "user",
                "content": f"Here is the markdown content to improve:\n\n{content}"
            }]

            response = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json={
                    "model": TOGETHER_MODEL,
                    "messages": messages,
                    "max_tokens": TOGETHER_MAX_TOKENS,
                    "temperature": TOGETHER_TEMPERATURE
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"].strip()
            
            logger.error(f"AI enhancement failed: {response.status_code}")
            return content
            
        except Exception as e:
            logger.error(f"AI enhancement failed: {str(e)}")
            return content
    
    def calculate_tokens(self, text: str) -> TokenInfo:
        """Calculate token usage for the given text.
        
        Uses a simplified token calculation method based on word count.
        For production use, this should be replaced with a more accurate
        tokenizer matching the AI model being used.
        
        Args:
            text: The text to calculate tokens for
            
        Returns:
            TokenInfo: Token usage information
        """
        # Simplified token calculation (approximately 4 chars per token)
        total = len(text) // 4
        return TokenInfo(
            total_tokens=total,
            content_tokens=total,
            remaining_tokens=TOGETHER_MAX_TOKENS - total
        )

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
        except requests.RequestException as e:
            logger.error(f"Network error in {func.__name__}: {str(e)}")
            raise HunterError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise HunterError(f"Operation failed: {str(e)}")
    return cast(F, wrapper)

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

class ProgressManager:
    """Manages progress indicators for long-running operations.
    
    This class provides a context manager for showing progress indicators
    during long-running operations. It uses Rich for beautiful console output.
    
    Example:
        >>> with ProgressManager() as progress:
        ...     progress.update("Step 1...")
        ...     do_step_1()
        ...     progress.update("Step 2...")
        ...     do_step_2()
    """
    
    def __init__(self):
        """Initialize the progress manager with a Rich progress bar."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )
    
    def __enter__(self) -> Progress:
        """Start the progress display.
        
        Returns:
            Progress: The progress object for updating status
        """
        return self.progress
    
    def __exit__(self, exc_type: Optional[type], 
                 exc_val: Optional[Exception], 
                 exc_tb: Optional[Any]) -> None:
        """Clean up the progress display.
        
        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.progress.stop()

@error_handler
def fetch_url(url: str) -> str:
    """Fetch content from URL with error handling.
    
    Makes an HTTP GET request to the specified URL and returns the response
    content. Includes error handling via the error_handler decorator.
    
    Args:
        url: The URL to fetch content from
        
    Returns:
        str: The response content
        
    Raises:
        HunterError: If the request fails
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration settings.
    
    Checks that all required configuration fields are present in the
    provided configuration dictionary.
    
    Args:
        config: Configuration dictionary to validate
        
    Returns:
        bool: True if configuration is valid, False otherwise
        
    Example:
        >>> config = {'api_key': 'abc123', 'output_format': 'markdown'}
        >>> is_valid = validate_config(config)
    """
    required_fields = ['api_key', 'output_format']
    return all(field in config for field in required_fields)

def enhance_markdown_formatting(content: str, api_key: str) -> str:
    """Enhance markdown formatting using AI.
    
    Args:
        content: The markdown content to enhance
        api_key: The Together API key to use
        
    Returns:
        Enhanced markdown content
    """
    enhancer = AIEnhancer()
    return enhancer.enhance_content(content)

@error_handler
def extract_content(url: str) -> str:
    """Extract and format content from a URL.
    
    Args:
        url: The URL to extract content from
        
    Returns:
        Formatted markdown content
    """
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove unwanted elements
    for element in soup.find_all(['script', 'style', 'nav', 'footer', 'iframe']):
        element.decompose()
    
    # Extract main content
    content = []
    for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'code', 'ul', 'ol', 'li']):
        if element.name.startswith('h'):
            level = int(element.name[1])
            content.append(f"{'#' * level} {element.get_text().strip()}\n")
        elif element.name == 'pre' or element.name == 'code':
            code = element.get_text().strip()
            lang = element.get('class', [''])[0].replace('language-', '') if element.get('class') else ''
            content.append(f"```{lang}\n{code}\n```\n")
        elif element.name in ['ul', 'ol']:
            for li in element.find_all('li', recursive=False):
                content.append(f"- {li.get_text().strip()}\n")
        elif element.name != 'li':  # Skip li elements as they're handled in ul/ol
            content.append(f"{element.get_text().strip()}\n")
    
    return '\n'.join(content)
