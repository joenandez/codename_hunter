"""Formatting utilities for markdown content.

This module provides a set of formatter classes that handle the conversion of HTML
content to properly formatted markdown. It implements a chain of responsibility pattern
where each formatter specializes in a specific type of content (code, links, etc.).

The formatters handle:
- Code block detection and language inference
- Link and image formatting
- Content cleaning and normalization
- Proper spacing and structure preservation

Example:
    >>> formatter = CodeFormatter()
    >>> code_block = formatter.format_code_block("def hello(): pass", "python")
    >>> print(code_block)
    ```python
    def hello(): pass
    ```
"""

from typing import Optional, List, Union
from bs4 import BeautifulSoup, Tag, NavigableString
import re

from hunter.constants import (
    TEXT_CLEANUP_PATTERNS,
    LANGUAGE_MAP,
    LANGUAGE_HINTS,
    CODE_DETECTION_PATTERNS,
    CODE_BLOCK_CLASSES,
    CODE_PATTERNS,
)

class BaseFormatter:
    """Base class for content formatting with shared utilities.
    
    This class provides common text cleaning and formatting utilities used by all
    formatters. It implements the base functionality for the formatter chain pattern.
    
    Attributes:
        None
    """
    
    @staticmethod
    def clean_content(text: str, preserve_structure: bool = False) -> str:
        """Clean and normalize text content.
        
        This method provides unified content cleaning that handles both regular text
        and structured content (like code blocks). It removes unnecessary whitespace,
        normalizes spacing around special characters, and optionally preserves the
        line structure of the content.
        
        Args:
            text: The text content to clean
            preserve_structure: If True, maintains line breaks and indentation
                              (used for code blocks)
        
        Returns:
            str: The cleaned text content
            
        Example:
            >>> formatter = BaseFormatter()
            >>> formatter.clean_content("Hello   world_1", False)
            'Hello world'
            >>> formatter.clean_content("def hello():\\n    pass", True)
            'def hello():\\n    pass'
        """
        if preserve_structure:
            lines = text.splitlines()
            cleaned_lines = []
            for line in lines:
                # Remove numbered suffixes and trailing whitespace
                line = re.sub(TEXT_CLEANUP_PATTERNS['numbered_suffix'], '', line.rstrip())
                cleaned_lines.append(line)
            # Remove empty lines at start and end while preserving internal empty lines
            while cleaned_lines and not cleaned_lines[0].strip():
                cleaned_lines.pop(0)
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()
            return '\n'.join(cleaned_lines)
        else:
            # Remove numbered suffixes first
            text = re.sub(TEXT_CLEANUP_PATTERNS['numbered_suffix'], '', text)
            # Remove trailing hash marks
            text = re.sub(TEXT_CLEANUP_PATTERNS['trailing_hash'], '', text)
            # Normalize whitespace
            text = re.sub(TEXT_CLEANUP_PATTERNS['whitespace'], ' ', text)
            # Add space around backticks
            text = re.sub(TEXT_CLEANUP_PATTERNS['backtick_after'], '` \\1', text)
            text = re.sub(TEXT_CLEANUP_PATTERNS['backtick_before'], '\\1 `', text)
            return text.strip()

class CodeFormatter(BaseFormatter):
    """Handles code-specific formatting and language detection.
    
    This formatter is responsible for identifying code blocks, detecting their
    programming language, and formatting them with proper markdown syntax.
    
    The class uses multiple strategies to identify code blocks:
    1. HTML structure analysis (pre/code tags)
    2. CSS class analysis
    3. Content pattern matching
    """

    @classmethod
    def is_code_block(cls, text: str, element: Optional[Union[Tag, NavigableString]] = None) -> bool:
        """Determine if content should be treated as a code block.
        
        Uses multiple heuristics:
        1. HTML structure (pre/code tags)
        2. CSS classes indicating code
        3. Content patterns matching code
        
        Args:
            text: Content to analyze
            element: Optional BeautifulSoup element for additional context
            
        Returns:
            bool: True if content appears to be code
        """
        if element is None:
            # Use general code detection patterns when no element context
            text = text.strip()
            # Check general patterns first
            if any(pattern.search(text) for pattern in CODE_DETECTION_PATTERNS):
                return True
            # Then check language-specific patterns
            for patterns in CODE_PATTERNS.values():
                if any(pattern.search(text) for pattern in patterns):
                    return True
            return False
            
        # Check element structure
        if element.name == 'pre' and element.find('code'):
            return True
        if element.name == 'code' and element.parent and element.parent.name == 'pre':
            return True
            
        # Check classes
        classes = element.get('class', [])
        if any(cls in ' '.join(classes) for cls in CODE_BLOCK_CLASSES):
            return True
            
        # Check content patterns
        text = text.strip()
        # Check general patterns first
        if any(pattern.search(text) for pattern in CODE_DETECTION_PATTERNS):
            return True
            
        # Then check language-specific patterns
        for patterns in CODE_PATTERNS.values():
            if any(pattern.search(text) for pattern in patterns):
                return True
                
        return False

    @classmethod
    def detect_language(cls, element: Optional[Union[Tag, NavigableString]]) -> str:
        """Detect programming language of code block.
        
        Uses multiple strategies:
        1. Class-based detection (e.g., 'language-python')
        2. Content-based hints
        
        Args:
            element: BeautifulSoup element containing code
            
        Returns:
            str: Detected language or empty string
        """
        if not element or isinstance(element, NavigableString):
            return ''
            
        # Check class-based hints
        classes = element.get('class', [])
        if classes:
            class_str = ' '.join(classes)
            for lang, hints in LANGUAGE_HINTS.items():
                if any(hint in class_str.lower() for hint in hints):
                    return LANGUAGE_MAP.get(lang, lang)
                    
        # Check content-based hints
        content = element.get_text()
        for lang, patterns in CODE_PATTERNS.items():
            if any(pattern.search(content) for pattern in patterns):
                return LANGUAGE_MAP.get(lang, lang)
                
        return ''

    def format_code_block(self, code: str, language: str = '') -> str:
        """Format code block with proper markdown syntax.
        
        Args:
            code: The code content to format
            language: Optional language identifier
            
        Returns:
            str: Formatted code block with markdown fence
        """
        # Clean the code while preserving structure
        lines = code.splitlines()
        
        # Find the minimum indentation level (ignoring empty lines)
        min_indent = float('inf')
        for line in lines:
            if line.strip():  # Only consider non-empty lines
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        
        # Remove the common indentation from all lines
        if min_indent < float('inf'):
            cleaned_lines = []
            for line in lines:
                if line.strip():  # Only dedent non-empty lines
                    cleaned_lines.append(line[min_indent:])
                else:
                    cleaned_lines.append('')
            cleaned_code = '\n'.join(cleaned_lines)
        else:
            cleaned_code = code
        
        # Clean the code further while preserving structure
        cleaned_code = self.clean_content(cleaned_code, preserve_structure=True)
        
        # Count backticks in code to determine fence length
        max_backticks = 0
        for line in cleaned_code.splitlines():
            backtick_count = line.count('`')
            max_backticks = max(max_backticks, backtick_count)
            
        # Use a fence with more backticks than any line in the code
        fence = '`' * (max_backticks + 1) if max_backticks > 2 else '```'
        
        # Add code fence with language
        return f"\n{fence}{language}\n{cleaned_code}\n{fence}\n"

class LinkFormatter(BaseFormatter):
    """Handles link and image formatting in markdown.
    
    This formatter is responsible for converting HTML links and images to proper
    markdown syntax, handling attributes like href, src, alt text, and titles.
    """
    
    def format_link(self, element: Tag) -> str:
        """Format links with proper markdown syntax and spacing.
        
        Args:
            element: BeautifulSoup link element
        
        Returns:
            str: Formatted markdown link
            
        Example:
            >>> formatter = LinkFormatter()
            >>> print(formatter.format_link(link_element))
            [Link Text](https://example.com)
        """
        href = element.get('href', '')
        text = self.clean_content(element.get_text(strip=True))
        
        # Skip empty or anchor-only links
        if not href or href.startswith('#'):
            return text
            
        # Handle section references (common in documentation)
        if href.startswith('/') and '#' in href:
            base_url = element.get('data-base-url', '')  # Some docs include base URL
            href = base_url + href if base_url else href
            
        # Escape any backticks in link text
        text = text.replace('`', '\\`')
        
        # Return with spaces for backward compatibility
        return f" [{text}]({href}) "

    def format_image(self, element: Tag) -> str:
        """Format images with proper markdown syntax and attributes.
        
        Handles:
        1. Source URL
        2. Alt text
        3. Optional title
        4. Proper spacing
        
        Args:
            element: BeautifulSoup image element
        
        Returns:
            str: Formatted markdown image
            
        Example:
            >>> formatter = LinkFormatter()
            >>> print(formatter.format_image(img_element))
            ![Alt Text](https://example.com/image.png "Title")
        """
        src = element.get('src', '')
        alt = self.clean_content(element.get('alt', ''))
        title = self.clean_content(element.get('title', ''))
        if title:
            return f"\n![{alt}]({src} \"{title}\")\n"
        return f"\n![{alt}]({src})\n" if src else ''
