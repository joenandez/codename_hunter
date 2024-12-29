"""Constants used throughout the hunter application."""
from enum import Enum
from typing import Dict, List, Set

# Regular Expression Patterns
TEXT_CLEANUP_PATTERNS = {
    'numbered_suffix': r'_\d+',
    'trailing_hash': r'#$',
    'whitespace': r'\s+',
    'backtick_after': r'`(\S)',
    'backtick_before': r'(\S)`',
}

LINK_FORMATTING_PATTERNS = {
    'space_before_link': r'(?<!\s)\[',
    'space_after_text': r'\](?!\(|\s)',
    'space_after_link': r'\)(?!\s|$|\.|,|\?|!|:)',
}

# HTML Content Extraction
SKIP_CLASSES: Set[str] = {
    'sidebar',
    'nav',
    'menu',
    'footer',
    'header',
    'search'
}

SKIP_IDS: Set[str] = {
    'nav',
    'sidebar',
    'menu',
    'footer',
    'header',
    'search'
}

SKIP_TAGS: Set[str] = {
    'nav',
    'header',
    'footer'
}

MAIN_CONTENT_CLASSES: List[str] = [
    'docs-content',
    'article-content',
    'main-content'
]

# Language Detection
LANGUAGE_HINTS: Dict[str, str] = {
    'import': 'typescript',
    'function': 'typescript',
    'const': 'typescript',
    'export': 'typescript',
    'interface': 'typescript',
    'type': 'typescript',
    'npm': 'bash',
    'yarn': 'bash',
    'apt-get': 'bash',
    '<template>': 'vue',
    'useState': 'jsx',
    'NextResponse': 'typescript',
    'supabase.auth': 'typescript'
}

# Language Mapping
LANGUAGE_MAP: Dict[str, str] = {
    'js': 'javascript',
    'ts': 'typescript',
    'jsx': 'javascript',
    'tsx': 'typescript',
    'shell': 'bash',
    'sh': 'bash',
    'json': 'json',
    'py': 'python',
}

# Code Block Detection
CODE_BLOCK_CLASSES: Set[str] = {
    'block',
    'language-',
    'hljs',
    'syntax',
    'code-block'
}

CODE_PATTERNS: List[str] = [
    'function',
    'import',
    'class',
    'const',
    'return',
    'async',
    'await',
    '{',
    '};',
    '=>',
    'interface',
    'type',
    'export'
]

# Content Types
class ContentType(Enum):
    CODE_BLOCK = 'code_block'
    HEADING = 'heading'
    LIST_ITEM = 'list_item'
    CONTENT = 'content'

# Formatting
MAX_CONSECUTIVE_NEWLINES = 4
INDENT_SIZE = 2

# API Configuration
TOGETHER_API_CONFIG = {
    'model': 'mistralai/Mistral-7B-Instruct-v0.2',
    'max_tokens': 4000,
    'temperature': 0.1,
    'cost_per_1k_tokens': 0.0002,  # $0.0002 per 1K tokens
    'chars_per_token': 4,  # Rough approximation: 1 token ≈ 4 characters
    'base_url': 'https://api.together.xyz/v1/chat/completions',
}

# System Messages
MARKDOWN_ENHANCEMENT_PROMPT = """You are a markdown formatting expert. Your task is to improve the formatting while preserving all information and links. Focus on:
1. Consistent spacing between sections
2. Beautiful list formatting
3. Proper code block presentation
4. Clear section hierarchy
5. Clean link and inline code formatting

Important!!!: Return ONLY the raw markdown content. Do not add any explanations. The users is saving this output directly to a markdown file."""
