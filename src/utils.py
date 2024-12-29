"""Utility functions for the application."""
from typing import Optional, Dict, Any
import logging
import os
import requests
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
console = Console()

@dataclass
class TokenInfo:
    """Information about token usage."""
    total_tokens: int
    content_tokens: int
    remaining_tokens: int

class AIEnhancer:
    """Handles AI-based content enhancement operations."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('TOGETHER_API_KEY')
        if not self.api_key:
            logger.warning("No API key provided for AI enhancement")
    
    def enhance_content(self, content: str) -> str:
        """Enhance content using AI if API key is available."""
        if not self.api_key:
            return content
            
        try:
            # AI enhancement logic will go here
            return content
        except Exception as e:
            logger.error(f"AI enhancement failed: {str(e)}")
            return content
    
    def calculate_tokens(self, text: str) -> TokenInfo:
        """Calculate token usage for the given text."""
        # Simplified token calculation (can be replaced with more accurate method)
        total = len(text.split())
        return TokenInfo(
            total_tokens=total,
            content_tokens=total,
            remaining_tokens=10000 - total  # Example limit
        )

def error_handler(func):
    """Decorator for consistent error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"Network error in {func.__name__}: {str(e)}")
            raise HunterError(f"Network error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise HunterError(f"Operation failed: {str(e)}")
    return wrapper

class HunterError(Exception):
    """Custom exception class for Hunter-specific errors."""
    pass

class ProgressManager:
    """Manages progress indicators for long-running operations."""
    
    def __init__(self):
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        )
    
    def __enter__(self):
        return self.progress
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()

@error_handler
def fetch_url(url: str) -> str:
    """Fetch content from URL with error handling."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration settings."""
    required_fields = ['api_key', 'output_format']
    return all(field in config for field in required_fields)
