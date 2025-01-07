"""Content parsing and extraction utilities.

This module implements a flexible parsing system for converting HTML content into
structured markdown. It uses a combination of design patterns:

1. Factory Pattern: ParserFactory creates appropriate parsers for different elements
2. Strategy Pattern: Each parser implements a specific parsing strategy
3. Abstract Base Class: ContentParser defines the parsing interface
4. Data Class: ParseResult encapsulates parsed content

The parsing system handles:
- Headings (h1-h6)
- Code blocks with language detection
- Lists (ordered and unordered) with nesting
- Links and images
- Paragraphs and general content

Example:
    >>> extractor = ContentExtractor()
    >>> results = await extractor.extract_from_url("https://example.com")
    >>> for result in results:
    ...     print(f"{result.content_type}: {result.content}")
"""

from typing import Optional, List, Dict, Protocol, Any, Iterator
from bs4 import BeautifulSoup, Tag, NavigableString
import aiohttp
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
import re

from hunter import constants
from hunter.formatters import BaseFormatter, CodeFormatter, LinkFormatter
from hunter.utils.fetcher import fetch_url_async
from hunter.utils.errors import HunterError, async_error_handler

class ContentType(Enum):
    """Types of content that can be extracted."""
    HEADING = 'heading'
    PARAGRAPH = 'paragraph'
    CODE_BLOCK = 'code_block'
    LIST = 'list'  # For list containers
    LIST_ITEM = 'list_item'  # For individual list items
    LINK = 'link'
    IMAGE = 'image'

@dataclass
class ParseResult:
    """Container for parsed content and metadata.
    
    This class encapsulates the result of parsing an HTML element, including its
    content type, formatted content, and any additional metadata.
    
    Attributes:
        content_type (ContentType): The type of content that was parsed
        content (str): The formatted markdown content
        metadata (Dict[str, Any]): Additional information about the content
            (e.g., heading level, language for code blocks)
    """
    content_type: ContentType
    content: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize metadata dict if none provided."""
        if self.metadata is None:
            self.metadata = {}

class ContentParser(ABC):
    """Base class for all content parsers.
    
    This abstract base class defines the interface that all content parsers must
    implement. It provides the basic structure for the parsing strategy pattern.
    
    Attributes:
        formatter (BaseFormatter): Base formatter for content cleaning
    """
    
    def __init__(self):
        """Initialize the parser with a base formatter."""
        self.formatter = BaseFormatter()
    
    @abstractmethod
    def can_parse(self, element: Tag) -> bool:
        """Determine if this parser can handle the given element.
        
        Args:
            element: BeautifulSoup Tag to check
            
        Returns:
            bool: True if this parser can handle the element
        """
        pass
    
    @abstractmethod
    def parse(self, element: Tag) -> ParseResult:
        """Parse the element and return structured content.
        
        Args:
            element: BeautifulSoup Tag to parse
            
        Returns:
            ParseResult: Structured content with metadata
            
        Raises:
            ValueError: If the element cannot be parsed
        """
        pass

class HeadingParser(ContentParser):
    """Parser for heading elements (h1-h6).
    
    This parser handles HTML heading elements and converts them to markdown
    headings with the appropriate level.
    """
    
    def can_parse(self, element: Tag) -> bool:
        """Check if element is a heading (h1-h6).
        
        Args:
            element: BeautifulSoup Tag to check
            
        Returns:
            bool: True if element is a heading
        """
        return element.name and element.name.startswith('h') and len(element.name) == 2
    
    def parse(self, element: Tag) -> ParseResult:
        """Parse a heading element.
        
        Extracts the heading level and text, formatting it as a markdown heading.
        
        Args:
            element: BeautifulSoup heading element
            
        Returns:
            ParseResult: Parsed heading with level in metadata
        """
        level = int(element.name[1])
        content = self.formatter.clean_content(element.get_text())
        markdown_heading = '#' * level + ' ' + content
        return ParseResult(
            content_type=ContentType.HEADING,
            content=markdown_heading,
            metadata={'level': level}
        )

class CodeBlockParser(ContentParser):
    """Parser for code block elements.
    
    This parser handles code blocks, including:
    - Language detection
    - Proper markdown code fence formatting
    - Structure preservation
    """
    
    def __init__(self):
        """Initialize with both base and code-specific formatters."""
        super().__init__()
        self.code_formatter = CodeFormatter()
    
    def can_parse(self, element: Tag) -> bool:
        """Determine if element contains code.
        
        Uses multiple heuristics including:
        - HTML structure (pre/code tags)
        - CSS classes
        - Content patterns
        
        Args:
            element: BeautifulSoup Tag to check
            
        Returns:
            bool: True if element contains code
        """
        return self.code_formatter.is_code_block(element.get_text(), element)
    
    def parse(self, element: Tag) -> ParseResult:
        """Parse a code block element.
        
        Handles:
        1. Code extraction
        2. Language detection
        3. Proper fence formatting
        
        Args:
            element: BeautifulSoup code element
            
        Returns:
            ParseResult: Formatted code block with language metadata
        """
        code_element = element.find('code') if element.name == 'pre' else element
        language = self.code_formatter.detect_language(code_element or element)
        code_text = code_element.get_text() if code_element else element.get_text()
        formatted_code = self.code_formatter.format_code_block(code_text, language)
        
        return ParseResult(
            content_type=ContentType.CODE_BLOCK,
            content=formatted_code,
            metadata={'language': language}
        )

class LinkParser(ContentParser):
    """Parser for link and image elements.
    
    This parser handles both hyperlinks and images, preserving:
    - URLs
    - Alt text
    - Titles
    - Proper markdown syntax
    """
    
    def __init__(self):
        """Initialize with both base and link-specific formatters."""
        super().__init__()
        self.link_formatter = LinkFormatter()
    
    def can_parse(self, element: Tag) -> bool:
        """Check if element is a link or image.
        
        Args:
            element: BeautifulSoup Tag to check
            
        Returns:
            bool: True if element is a link or image
        """
        return element.name == 'a' or element.name == 'img'
    
    def parse(self, element: Tag) -> ParseResult:
        """Parse a link or image element.
        
        Handles both regular links and images with their respective attributes.
        
        Args:
            element: BeautifulSoup link or image element
            
        Returns:
            ParseResult: Formatted link/image with URL and text metadata
        """
        is_image = element.name == 'img'
        
        if is_image:
            content = self.link_formatter.format_image(element)
            content_type = ContentType.IMAGE
        else:
            content = self.link_formatter.format_link(element)
            content_type = ContentType.LINK
        
        return ParseResult(
            content_type=content_type,
            content=content,
            metadata={
                'url': element.get('href' if not is_image else 'src', ''),
                'text': element.get('alt' if is_image else 'text', ''),
                'is_image': is_image
            }
        )

class ListParser(ContentParser):
    """Parser for ordered and unordered lists.
    
    This parser handles both types of lists and supports nested list structures.
    It maintains proper indentation and numbering based on list type and depth.
    """
    
    def __init__(self):
        """Initialize list parser with formatter."""
        super().__init__()
        self.formatter = BaseFormatter()
        self._factory = None  # Lazy initialization
    
    @property
    def factory(self):
        """Lazy initialization of parser factory.
        
        Returns:
            ParserFactory: Instance for parsing nested content
        """
        if self._factory is None:
            self._factory = ParserFactory()
        return self._factory

    def can_parse(self, element: Tag) -> bool:
        """Check if element is a list (ol/ul).
        
        Args:
            element: HTML element to check
            
        Returns:
            bool: True if element is a list, False otherwise
        """
        return element.name in ['ul', 'ol']
    
    def get_list_depth(self, element: Tag) -> int:
        """Calculate nesting depth of list element.
        
        Args:
            element: List element to check
            
        Returns:
            int: Nesting depth (1-based)
        """
        depth = 1
        parent = element.parent
        while parent:
            if parent.name in ['ul', 'ol']:
                depth += 1
            parent = parent.parent
        return depth
    
    def format_list_item(self, element: Tag, depth: int = 0, index: int = 1) -> str:
        """Format a single list item with proper indentation.
        
        Args:
            element: List item element to format
            depth: Current nesting depth
            index: Current item index (for ordered lists)
            
        Returns:
            str: Formatted list item
        """
        indent = '    ' * depth
        marker = f"{index}. " if element.parent.name == 'ol' else '- '
        
        # Get the direct text content
        content = self.formatter.clean_content(element.get_text(strip=True))
        
        # Handle nested lists
        nested_content = []
        for child in element.children:
            if isinstance(child, Tag) and child.name in ['ul', 'ol']:
                nested_parser = self.factory.get_parser(child)
                if nested_parser:
                    result = nested_parser.parse(child)
                    nested_content.append(result.content)
        
        # Combine content
        formatted = f"{indent}{marker}{content}"
        if nested_content:
            formatted += '\n' + '\n'.join(nested_content)
        
        return formatted
    
    def parse(self, element: Tag) -> ParseResult:
        """Parse a list element and its items.
        
        Handles:
        1. List type detection (ordered/unordered)
        2. Proper indentation
        3. Nested content
        
        Args:
            element: List element to parse
            
        Returns:
            ParseResult: Formatted list with type and depth metadata
        """
        depth = self.get_list_depth(element)
        items = []
        
        for i, item in enumerate(element.find_all('li', recursive=False), start=1):
            items.append(self.format_list_item(item, depth, i))
        
        content = '\n'.join(items)
        return ParseResult(
            content_type=ContentType.LIST,
            content=content,
            metadata={'depth': depth, 'list_type': element.name}
        )

class ParagraphParser(ContentParser):
    """Parser for paragraph elements.
    
    This parser handles standard paragraph content, cleaning and formatting
    the text appropriately.
    """
    
    def can_parse(self, element: Tag) -> bool:
        """Check if element is a paragraph.
        
        Args:
            element: BeautifulSoup Tag to check
            
        Returns:
            bool: True if element is a paragraph
        """
        return element.name == 'p'
    
    def parse(self, element: Tag) -> Optional[ParseResult]:
        """Parse a paragraph element.
        
        Extracts and cleans the text content. Returns None for empty paragraphs.
        Adds newlines around paragraph content for proper markdown spacing.
        
        Args:
            element: BeautifulSoup paragraph element
            
        Returns:
            ParseResult: Parsed paragraph content or None if empty
        """
        content = self.formatter.clean_content(element.get_text())
        if not content.strip():
            return None
            
        # Add newlines for proper markdown paragraph spacing
        formatted_content = f"\n{content.strip()}\n"
            
        return ParseResult(
            content_type=ContentType.PARAGRAPH,
            content=formatted_content
        )

class ParserFactory:
    """Factory for creating appropriate content parsers.
    
    This class implements the Factory pattern to create parser instances based on
    the type of content being parsed. It maintains a registry of parsers and
    selects the appropriate one based on the element being parsed.
    """
    
    def __init__(self):
        """Initialize parser registry."""
        self.parsers = [
            HeadingParser(),
            CodeBlockParser(),
            ListParser(),
            LinkParser(),
            ParagraphParser()
        ]
    
    def get_parser(self, element: Tag) -> Optional[ContentParser]:
        """Get appropriate parser for element.
        
        Tries each registered parser in order until one accepts the element.
        
        Args:
            element: HTML element to parse
            
        Returns:
            ContentParser: Appropriate parser instance or None if no parser accepts
        """
        if not isinstance(element, Tag):
            return None
            
        for parser in self.parsers:
            if parser.can_parse(element):
                return parser
                
        return None

class ContentExtractor:
    """Main class for extracting and parsing content from HTML.
    
    This class coordinates the entire content extraction and parsing process:
    1. Fetching content from URLs
    2. Finding appropriate parsers
    3. Extracting structured content
    4. Error handling
    
    Attributes:
        parser_factory (ParserFactory): Factory for creating parsers
    """
    
    def __init__(self):
        """Initialize with parser factory."""
        self.parser_factory = ParserFactory()
        self._seen_content = set()
        self._last_heading_level = 0
        self._section_stack = []
        self.formatter = BaseFormatter()
    
    def _is_duplicate(self, content: str) -> bool:
        """Check if content has been seen before, with smart normalization.
        
        Args:
            content: Content to check for duplication
            
        Returns:
            bool: True if content is a duplicate
        """
        # Normalize content for comparison
        normalized = ' '.join(content.lower().split())
        
        # Skip very short content
        if len(normalized) < 5:
            return False
            
        # Check if normalized content is a duplicate
        if normalized in self._seen_content:
            return True
            
        self._seen_content.add(normalized)
        return False
        
    def _process_heading(self, element: Tag) -> Optional[ParseResult]:
        """Process a heading element with proper section tracking.
        
        Args:
            element: Heading element to process
            
        Returns:
            Optional[ParseResult]: Parsed heading or None if duplicate
        """
        level = int(element.name[1])
        text = self.formatter.clean_content(element.get_text(strip=True))
        
        if not text or self._is_duplicate(text):
            return None
            
        # Handle section hierarchy
        while self._section_stack and self._section_stack[-1] >= level:
            self._section_stack.pop()
        self._section_stack.append(level)
        
        # Get link if heading is wrapped in one
        parent_link = element.find_parent('a')
        if parent_link and parent_link.get('href'):
            content = f"[{text}]({parent_link['href']})"
        else:
            content = f"{'#' * level} {text}"
            
        return ParseResult(
            content_type=ContentType.HEADING,
            content=content,
            metadata={'level': level}
        )
        
    def extract_from_html(self, html: str) -> List[ParseResult]:
        """Extract and parse content from HTML string using direct HTML to Markdown mapping."""
        soup = BeautifulSoup(html, 'html.parser')
        results: List[ParseResult] = []
        self._seen_content = set()
        self._section_stack = []
        
        # Remove script, style, and navigation elements
        for element in soup.find_all(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
            
        # Remove elements with skip classes/ids
        for element in soup.find_all(class_=list(constants.SKIP_CLASSES)):
            element.decompose()
        for element in soup.find_all(id=list(constants.SKIP_IDS)):
            element.decompose()
            
        # Try to find main content area
        main_content = None
        
        # 1. Try article with prose class first (common in documentation sites)
        main_content = soup.find('article', class_=lambda x: x and 'prose' in x)
        
        # 2. Try HTML5 semantic main tag
        if not main_content:
            main_content = soup.find('main')
            
        # 3. Try by ID containing 'main' or 'content'
        if not main_content:
            for element in soup.find_all(id=True):
                if any(term in element.get('id', '').lower() for term in ['main', 'content', 'article']):
                    main_content = element
                    break
                    
        # Use main content if found, otherwise use body
        content_root = main_content if main_content else soup.find('body') or soup
        
        def process_element(element):
            """Process a single element and its children."""
            if isinstance(element, NavigableString):
                if element.strip():
                    text = self.formatter.clean_content(str(element))
                    if not self._is_duplicate(text):
                        return [ParseResult(
                            content_type=ContentType.PARAGRAPH,
                            content=text
                        )]
                return []
                
            if not isinstance(element, Tag):
                return []
                
            # Skip navigation and sidebar elements
            if (element.get('role') == 'navigation' or 
                element.get('aria-label') == 'Breadcrumb' or
                any(cls in str(element.get('class', [])) for cls in ['sidebar', 'nav', 'navigation']) or
                any(term in str(element.get('id', '')).lower() for term in ['sidebar', 'nav', 'navigation'])):
                return []
                
            results = []
            
            # Handle headings with section tracking
            if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                heading_result = self._process_heading(element)
                if heading_result:
                    results.append(heading_result)
                    
            # Handle code blocks
            elif element.name == 'pre' or (element.name == 'code' and element.parent.name != 'pre'):
                code_text = element.get_text(strip=True)
                if code_text and not self._is_duplicate(code_text):
                    language = ''
                    if element.get('class'):
                        for cls in element.get('class'):
                            if cls.startswith('language-'):
                                language = cls.replace('language-', '')
                                break
                    results.append(ParseResult(
                        content_type=ContentType.CODE_BLOCK,
                        content=f"\n```{language}\n{code_text}\n```\n",
                        metadata={'language': language}
                    ))
                    
            # Handle links
            elif element.name == 'a':
                href = element.get('href', '')
                text = element.get_text(strip=True)
                if href and text and not href.startswith('#'):
                    link_content = f"[{text}]({href})"
                    if not self._is_duplicate(link_content):
                        results.append(ParseResult(
                            content_type=ContentType.LINK,
                            content=link_content,
                            metadata={'url': href, 'text': text}
                        ))
                        
            # Handle lists
            elif element.name in ['ul', 'ol']:
                items = []
                for i, item in enumerate(element.find_all('li', recursive=False), 1):
                    prefix = '- ' if element.name == 'ul' else f"{i}. "
                    text = item.get_text(strip=True)
                    if text and not self._is_duplicate(text):
                        items.append(f"{prefix}{text}")
                if items:
                    list_content = '\n'.join(items) + '\n'
                    results.append(ParseResult(
                        content_type=ContentType.LIST,
                        content=list_content,
                        metadata={'ordered': element.name == 'ol'}
                    ))
                        
            # Handle paragraphs and other text containers
            elif element.name in ['p', 'div', 'section', 'article']:
                direct_text = ''.join(
                    str(c) for c in element.children 
                    if isinstance(c, NavigableString) and c.strip()
                )
                if direct_text.strip() and not self._is_duplicate(direct_text):
                    results.append(ParseResult(
                        content_type=ContentType.PARAGRAPH,
                        content=f"\n{self.formatter.clean_content(direct_text)}\n"
                    ))
                    
            # Process children for container elements
            if element.name not in ['pre', 'code']:
                for child in element.children:
                    results.extend(process_element(child))
                    
            return results
            
        # Process only the main content area
        results = process_element(content_root)
        
        # Post-process to handle inline code
        for result in results:
            if result.content_type == ContentType.PARAGRAPH:
                # Convert `text` patterns to proper inline code
                result.content = re.sub(r'`([^`]+)`', r'\\`\1\\`', result.content)
                
        return results

    @async_error_handler
    async def extract_from_url(self, url: str) -> List[ParseResult]:
        """Extract and parse content from a URL asynchronously.
        
        Args:
            url: URL to fetch content from
            
        Returns:
            List[ParseResult]: List of parsed content results
            
        Raises:
            HunterError: If URL fetch or parsing fails
        """
        html = await fetch_url_async(url)
        return self.extract_from_html(html)
