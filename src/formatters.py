"""Formatting utilities for markdown content."""
from typing import Optional
from bs4 import BeautifulSoup
import re
from .constants import (
    TEXT_CLEANUP_PATTERNS,
    LANGUAGE_MAP,
    LANGUAGE_HINTS,
    CODE_PATTERNS,
    CODE_BLOCK_CLASSES,
)

class BaseFormatter:
    """Base class for content formatting with shared utilities."""
    
    @staticmethod
    def clean_content(text: str, preserve_structure: bool = False) -> str:
        """Unified content cleaning method that handles both text and code.
        
        Args:
            text: The text to clean
            preserve_structure: If True, preserves line structure (for code)
        """
        if preserve_structure:
            lines = text.splitlines()
            cleaned_lines = [re.sub(TEXT_CLEANUP_PATTERNS['numbered_suffix'], '', line.rstrip()) for line in lines]
            # Remove empty lines at start and end while preserving internal empty lines
            while cleaned_lines and not cleaned_lines[0].strip():
                cleaned_lines.pop(0)
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()
            return '\n'.join(cleaned_lines)
        else:
            text = re.sub(TEXT_CLEANUP_PATTERNS['numbered_suffix'], '', text)
            text = re.sub(TEXT_CLEANUP_PATTERNS['trailing_hash'], '', text.strip())
            text = re.sub(TEXT_CLEANUP_PATTERNS['whitespace'], ' ', text)
            text = re.sub(TEXT_CLEANUP_PATTERNS['backtick_after'], '` \\1', text)
            text = re.sub(TEXT_CLEANUP_PATTERNS['backtick_before'], '\\1 `', text)
            return text.strip()

class CodeFormatter(BaseFormatter):
    """Handles code-specific formatting."""

    @classmethod
    def is_code_block(cls, text: str, element: Optional[BeautifulSoup] = None) -> bool:
        """Determine if content should be treated as a code block."""
        if element and element.parent and element.parent.name == 'pre':
            return True
            
        if element and element.get('class'):
            classes = element.get('class')
            if any(c in str(classes) for c in CODE_BLOCK_CLASSES):
                return True
        
        has_newlines = '\n' in text.strip()
        word_count = len(text.split())
        
        return (has_newlines or 
                word_count > 10 or 
                any(pattern in text for pattern in CODE_PATTERNS))

    @classmethod
    def detect_language(cls, element: Optional[BeautifulSoup]) -> str:
        """Detect programming language from element or content."""
        if not element:
            return ''
            
        # Check class names
        classes = element.get('class', [])
        for cls_name in classes:
            if cls_name.startswith(('language-', 'lang-')):
                return cls_name.replace('language-', '').replace('lang-', '')
                
        # Check data attributes
        for attr in element.attrs:
            if attr.startswith('data-lang'):
                return element[attr]
                
        # Detect from content
        code_text = element.get_text()
        for hint, lang in LANGUAGE_HINTS.items():
            if hint in code_text:
                return lang
                
        return ''

    def format_code_block(self, code: str, language: str = '') -> str:
        """Format code block with proper language and spacing."""
        code = self.clean_content(code, preserve_structure=True)
        if not code.strip():
            return ''
        
        lang_spec = LANGUAGE_MAP.get(language, language) if language else ''
        return f"\n```{lang_spec}\n{code.strip()}\n```\n"

class LinkFormatter(BaseFormatter):
    """Handles link and image formatting."""
    
    def format_link(self, element: BeautifulSoup) -> str:
        """Format links with proper spacing."""
        href = element.get('href', '')
        text = self.clean_content(element.get_text(strip=True))
        return f" [{text}]({href}) " if href and text else text

    def format_image(self, element: BeautifulSoup) -> str:
        """Format images with proper attributes and spacing."""
        src = element.get('src', '')
        alt = self.clean_content(element.get('alt', ''))
        title = self.clean_content(element.get('title', ''))
        if title:
            return f"\n![{alt}]({src} \"{title}\")\n"
        return f"\n![{alt}]({src})\n" if src else ''
