"""
Configuration constants for the Codename Hunter application.
These can be overridden using environment variables or config file.
"""

from typing import Literal
from pathlib import Path
import configparser
import os

# Configuration paths
CONFIG_DIR = Path.home() / '.config' / 'hunter'
CONFIG_FILE = CONFIG_DIR / 'config.ini'

def get_config_value(section: str, key: str, default: str = '') -> str:
    """Get configuration value from environment or config file."""
    # Environment variables take precedence
    env_key = f"HUNTER_{section.upper()}_{key.upper()}"
    if value := os.getenv(env_key):
        return value
    
    # Try config file
    if CONFIG_FILE.exists():
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
        return config.get(section, key, fallback=default)
    
    return default

# Together.ai API Configuration
TOGETHER_API_KEY = get_config_value('api', 'together_api_key')
TOGETHER_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
TOGETHER_MAX_TOKENS = 4000
TOGETHER_TEMPERATURE = 0.1

# Output Configuration
OUTPUT_FORMAT: Literal['markdown'] = get_config_value('output', 'format', 'markdown')
CONSOLE_STYLE: Literal['dark', 'light'] = get_config_value('output', 'style', 'dark')

# Rate Limiting
MAX_CALLS_PER_MINUTE = 60  # Together.ai rate limit

# Content Processing
MAX_CODE_BLOCK_LENGTH = 250  # Maximum number of lines in a code block
DEFAULT_CODE_LANGUAGE = ''  # Default language for code blocks when none detected
