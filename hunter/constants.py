"""
Configuration constants for the Codename Hunter application.
These can be overridden using environment variables or config file.

Configuration Priority:
1. Environment variables (highest priority)
2. User config file (~/.config/hunter/config.ini)
3. Local config file (./config/config.ini)
4. Default config file (./config/config.ini.template)
"""

from typing import Literal, Optional
from pathlib import Path
import configparser
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Configuration paths
CONFIG_DIR = Path.home() / '.config' / 'hunter'
USER_CONFIG_FILE = CONFIG_DIR / 'config.ini'
LOCAL_CONFIG_FILE = Path(__file__).parent.parent / 'config' / 'config.ini'
DEFAULT_CONFIG_FILE = Path(__file__).parent.parent / 'config' / 'config.ini.template'

def get_config_value(section: str, key: str, default: str = '') -> str:
    """Get configuration value from environment or config files.
    
    Priority order:
    1. Environment variables
    2. User config file (~/.config/hunter/config.ini)
    3. Local config file (./config/config.ini)
    4. Default config file (./config/config.ini.template)
    5. Default value
    """
    # 1. Check environment variable
    env_key = f"HUNTER_{section.upper()}_{key.upper()}"
    if section == 'api' and key == 'together_api_key':
        env_key = 'TOGETHER_API_KEY'
    
    if value := os.getenv(env_key):
        return value
    
    # 2. Check config files in priority order
    config = configparser.ConfigParser()
    
    for config_file in [USER_CONFIG_FILE, LOCAL_CONFIG_FILE, DEFAULT_CONFIG_FILE]:
        if config_file.exists():
            try:
                config.read(config_file)
                if value := config.get(section, key, fallback=None):
                    logger.debug(f"Using config from {config_file}")
                    return value
            except (configparser.Error, OSError) as e:
                logger.warning(f"Error reading {config_file}: {e}")
    
    return default

# Together.ai API Configuration
TOGETHER_API_KEY = get_config_value('api', 'together_api_key')
TOGETHER_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
TOGETHER_MAX_TOKENS = 4000
TOGETHER_TEMPERATURE = 0.1

# Pricing (USD per million tokens)
TOGETHER_PRICE_PER_MILLION_TOKENS = 0.2

# Output Configuration
OUTPUT_FORMAT: Literal['markdown'] = get_config_value('output', 'format', 'markdown')
CONSOLE_STYLE: Literal['dark', 'light'] = get_config_value('output', 'style', 'dark')

# Rate Limiting
MAX_CALLS_PER_MINUTE = 60  # Together.ai rate limit

# Content Processing
MAX_CODE_BLOCK_LENGTH = 250  # Maximum number of lines in a code block
DEFAULT_CODE_LANGUAGE = ''  # Default language for code blocks when none detected
