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
import re
from enum import Enum, auto
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class ContentType(Enum):
    """Types of content that can be processed.
    
    This enum defines the base content types that can be processed by the application.
    It is extended by parsers for more specific content types.
    
    Attributes:
        HEADING: Section headings (h1-h6)
        CODE_BLOCK: Programming code blocks
        CONTENT: General content (paragraphs, etc.)
    """
    HEADING = 'heading'
    CODE_BLOCK = 'code_block'
    CONTENT = 'content'

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

# Content Filtering
SKIP_CLASSES = {
    'advertisement',
    'ads',
    'banner',
    'breadcrumb',
    'comment',
    'cookie',
    'footer',
    'header',
    'menu',
    'nav',
    'navbar',
    'popup',
    'sidebar',
    'social',
    'tracking',
    'widget'
}

SKIP_IDS = {
    'ad',
    'banner',
    'comment',
    'footer',
    'header',
    'menu',
    'nav',
    'popup',
    'sidebar',
    'social'
}

SKIP_TAGS = {
    'script',
    'style',
    'noscript',
    'iframe',
    'nav',
    'footer',
    'header'
}

# Main Content Detection
MAIN_CONTENT_CLASSES = [
    'article',
    'content',
    'main',
    'post',
    'entry',
    'blog-post',
    'article-content',
    'post-content',
    'entry-content'
]

# Text Cleanup Patterns
TEXT_CLEANUP_PATTERNS = {
    'numbered_suffix': re.compile(r'_\d+'),   # Remove numbered suffixes like _1, _2
    'trailing_hash': re.compile(r'#'),        # Remove hash marks
    'whitespace': re.compile(r'\s+'),         # Normalize whitespace
    'backtick_after': re.compile(r'`(\w)'),   # Add space after backtick
    'backtick_before': re.compile(r'(\w)`')   # Add space before backtick
}

# Language Detection
LANGUAGE_MAP = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'rb': 'ruby',
    'rs': 'rust',
    'go': 'go',
    'java': 'java',
    'cpp': 'cpp',
    'cs': 'csharp',
    'php': 'php',
    'sh': 'bash',
    'md': 'markdown',
    'html': 'html',
    'css': 'css',
    'sql': 'sql',
    'json': 'json',
    'yaml': 'yaml',
    'toml': 'toml',
    'xml': 'xml'
}

# Language Detection Hints
LANGUAGE_HINTS = {
    'python': ['python', 'py', 'ipython'],
    'javascript': ['javascript', 'js', 'node'],
    'typescript': ['typescript', 'ts'],
    'ruby': ['ruby', 'rb'],
    'rust': ['rust', 'rs'],
    'go': ['golang', 'go'],
    'java': ['java'],
    'cpp': ['cpp', 'c++', 'cxx'],
    'csharp': ['csharp', 'c#', 'cs'],
    'php': ['php'],
    'bash': ['bash', 'shell', 'sh'],
    'markdown': ['markdown', 'md'],
    'html': ['html', 'htm'],
    'css': ['css', 'scss', 'sass'],
    'sql': ['sql', 'mysql', 'postgresql'],
    'json': ['json'],
    'yaml': ['yaml', 'yml'],
    'toml': ['toml'],
    'xml': ['xml']
}

# Code Block Detection
CODE_BLOCK_CLASSES = [
    'code',
    'highlight',
    'syntax',
    'prettyprint',
    'sourceCode',
    'language-',
    'hljs'
]

# General code detection patterns
CODE_DETECTION_PATTERNS = [
    re.compile(r'^\s*[a-zA-Z_]\w*\s*\([^)]*\)\s*[{:]'),  # Function/method definitions
    re.compile(r'^\s*(?:var|let|const)\s+[a-zA-Z_]\w*\s*='),  # Variable declarations
    re.compile(r'^\s*import\s+[\w\s,{}*]+\s+from'),  # Import statements
    re.compile(r'^\s*class\s+[a-zA-Z_]\w*'),  # Class definitions
    re.compile(r'^\s*[a-zA-Z_]\w*\s*=\s*(?:function|class|=>)'),  # Function/class assignments
    re.compile(r'^\s*(?:public|private|protected)\s+\w+'),  # Access modifiers
    re.compile(r'^\s*@\w+'),  # Decorators
    re.compile(r'^\s*#include\s+[<"].*[>"]'),  # C/C++ includes
    re.compile(r'^\s*package\s+[\w.]+;'),  # Java/Kotlin packages
    re.compile(r'^\s*using\s+[\w.]+;')  # C# using statements
]

# Language-specific code patterns
CODE_PATTERNS = {
    lang: [re.compile(pattern) for pattern in patterns]
    for lang, patterns in {
        'python': [
            r'^\s*def\s+\w+\s*\(',
            r'^\s*class\s+\w+[:\(]',
            r'^\s*import\s+\w+',
            r'^\s*from\s+[\w.]+\s+import'
        ],
        'javascript': [
            r'^\s*function\s+\w+\s*\(',
            r'^\s*const\s+\w+\s*=',
            r'^\s*let\s+\w+\s*=',
            r'^\s*var\s+\w+\s*=',
            r'^\s*import\s+.*from'
        ],
        'html': [
            r'^\s*<[a-zA-Z][^>]*>',
            r'^\s*</[a-zA-Z][^>]*>'
        ],
        'css': [
            r'^\s*\.[a-zA-Z][\w-]*\s*{',
            r'^\s*#[a-zA-Z][\w-]*\s*{',
            r'^\s*@media\s',
            r'^\s*@import\s'
        ],
        'sql': [
            r'^\s*SELECT\s+.*FROM',
            r'^\s*INSERT\s+INTO',
            r'^\s*UPDATE\s+.*SET',
            r'^\s*DELETE\s+FROM'
        ]
    }.items()
}
