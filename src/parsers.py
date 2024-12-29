"""Content parsing and extraction utilities."""
from typing import Optional, List, Dict, Protocol
from bs4 import BeautifulSoup, Tag
import requests
from abc import ABC, abstractmethod
from dataclasses import dataclass
from . import constants
from .formatters import BaseFormatter, CodeFormatter, LinkFormatter
from enum import Enum, auto

class ContentType(Enum):
    """Types of content that can be parsed."""
    HEADING = constants.ContentType.HEADING.value
    CODE_BLOCK = constants.ContentType.CODE_BLOCK.value
    LIST = 'list'
    PARAGRAPH = constants.ContentType.CONTENT.value
    LINK = 'link'
    IMAGE = 'image'

@dataclass
class ParseResult:
    """Container for parsed content."""
    content_type: ContentType
    content: str
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ContentParser(ABC):
    """Base class for all content parsers."""
    
    def __init__(self):
        self.formatter = BaseFormatter()
    
    @abstractmethod
    def can_parse(self, element: Tag) -> bool:
        """Determine if this parser can handle the given element."""
        pass
    
    @abstractmethod
    def parse(self, element: Tag) -> ParseResult:
        """Parse the element and return structured content."""
        pass

class HeadingParser(ContentParser):
    """Parser for heading elements (h1-h6)."""
    
    def can_parse(self, element: Tag) -> bool:
        return element.name and element.name.startswith('h') and len(element.name) == 2
    
    def parse(self, element: Tag) -> ParseResult:
        level = int(element.name[1])
        content = self.formatter.clean_content(element.get_text())
        return ParseResult(
            content_type=ContentType.HEADING,
            content=content,
            metadata={'level': level}
        )

class CodeBlockParser(ContentParser):
    """Parser for code block elements."""
    
    def __init__(self):
        super().__init__()
        self.code_formatter = CodeFormatter()
    
    def can_parse(self, element: Tag) -> bool:
        """Determine if this element is a code block."""
        return self.code_formatter.is_code_block(element.get_text(), element)
    
    def parse(self, element: Tag) -> ParseResult:
        """Parse a code block element."""
        # Get the actual code element if we're on a pre tag
        code_element = element.find('code') if element.name == 'pre' else element
        
        # Detect language and format code
        language = self.code_formatter.detect_language(code_element or element)
        code_text = code_element.get_text() if code_element else element.get_text()
        formatted_code = self.code_formatter.format_code_block(code_text, language)
        
        return ParseResult(
            content_type=ContentType.CODE_BLOCK,
            content=formatted_code,
            metadata={'language': language}
        )

class LinkParser(ContentParser):
    """Parser for link and image elements."""
    
    def __init__(self):
        super().__init__()
        self.link_formatter = LinkFormatter()
    
    def can_parse(self, element: Tag) -> bool:
        return element.name == 'a' or element.name == 'img'
    
    def parse(self, element: Tag) -> ParseResult:
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
    """Parser for list elements (ul/ol)."""
    
    def can_parse(self, element: Tag) -> bool:
        return element.name in ('ul', 'ol')
    
    def get_list_depth(self, element: Tag) -> int:
        """Calculate the nesting depth of a list item."""
        depth = 0
        parent = element.parent
        while parent:
            if parent.name in ('ul', 'ol'):
                depth += 1
            parent = parent.parent
        return depth
    
    def format_list_item(self, element: Tag, parser_factory) -> str:
        """Format a single list item with proper indentation and markers."""
        depth = self.get_list_depth(element.parent)
        indent = ' ' * (constants.INDENT_SIZE * (depth - 1))
        
        # Process the content of the list item
        content_parts = []
        for child in element.children:
            if isinstance(child, Tag):
                parser = parser_factory.get_parser(child)
                if parser:
                    result = parser.parse(child)
                    content_parts.append(result.content)
                else:
                    content_parts.append(self.formatter.clean_content(child.get_text()))
            else:
                text = child.strip()
                if text:
                    content_parts.append(self.formatter.clean_content(text))
        
        content = ' '.join(content_parts).strip()
        
        # Determine list marker
        is_ordered = element.parent.name == 'ol'
        if is_ordered:
            position = sum(1 for sibling in element.previous_siblings if sibling.name == 'li') + 1
            marker = f"{position}."
        else:
            marker = '-'
            
        return f"{indent}{marker} {content}"
    
    def parse(self, element: Tag) -> ParseResult:
        """Parse a list element and its items."""
        from . import parser_factory
        
        formatted_items = []
        for item in element.find_all('li', recursive=False):
            formatted_items.append(self.format_list_item(item, parser_factory))
        
        content = '\n'.join(formatted_items)
        
        return ParseResult(
            content_type=ContentType.LIST,
            content=content,
            metadata={
                'list_type': element.name,
                'depth': self.get_list_depth(element)
            }
        )

class ParagraphParser(ContentParser):
    """Parser for paragraph elements."""
    
    def can_parse(self, element: Tag) -> bool:
        return element.name == 'p'
    
    def parse(self, element: Tag) -> ParseResult:
        text = self.formatter.clean_content(element.get_text())
        if not text:
            return None
            
        return ParseResult(
            content_type=ContentType.PARAGRAPH,
            content=text
        )

class ParserFactory:
    """Factory for creating appropriate parsers for different content types."""
    
    def __init__(self):
        self.parsers: List[ContentParser] = [
            HeadingParser(),
            CodeBlockParser(),
            ListParser(),
            LinkParser(),
            ParagraphParser(),
        ]
    
    def get_parser(self, element: Tag) -> Optional[ContentParser]:
        """Get the appropriate parser for the given element."""
        for parser in self.parsers:
            if parser.can_parse(element):
                return parser
        return None

class ContentExtractor:
    """Main class for extracting and parsing content from HTML."""
    
    def __init__(self):
        self.parser_factory = ParserFactory()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _fetch_url(self, url: str) -> str:
        """Fetch HTML content from a URL."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ValueError(f"Failed to fetch URL {url}: {str(e)}")
    
    def _parse_element(self, element: Tag) -> Optional[ParseResult]:
        """Parse a single element using the appropriate parser."""
        parser = self.parser_factory.get_parser(element)
        if parser:
            try:
                return parser.parse(element)
            except Exception as e:
                print(f"Warning: Failed to parse element {element.name}: {str(e)}")
        return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text content while preserving important formatting."""
        base_parser = BaseParser()
        return base_parser.clean_text(text)
    
    def extract_from_url(self, url: str) -> List[ParseResult]:
        """Extract and parse content from a URL."""
        html = self._fetch_url(url)
        return self.extract_from_html(html)
    
    def extract_from_html(self, html: str) -> List[ParseResult]:
        """Extract and parse content from HTML string."""
        soup = BeautifulSoup(html, 'html.parser')
        results: List[ParseResult] = []
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'noscript', 'iframe']):
            element.decompose()
            
        # Remove elements with skip classes/ids
        for element in soup.find_all(class_=list(constants.SKIP_CLASSES)):
            element.decompose()
        for element in soup.find_all(id=list(constants.SKIP_IDS)):
            element.decompose()
        for element in soup.find_all(constants.SKIP_TAGS):
            element.decompose()
        
        # Try to find main content area first
        main_content = None
        for class_name in constants.MAIN_CONTENT_CLASSES:
            main_content = soup.find(class_=class_name)
            if main_content:
                break
        
        # Use main content if found, otherwise use whole body
        content_root = main_content if main_content else soup
        
        # Process main content elements
        for element in content_root.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'pre', 'code', 'ul', 'ol', 'a', 'img']):
            # Skip if element is empty or only contains whitespace
            if not element.get_text(strip=True) and element.name not in ['img']:
                continue
                
            # Skip if element is nested within a parent that will handle it
            if element.parent and element.parent.name in ['pre', 'code'] and element.name in ['pre', 'code']:
                continue
            
            result = self._parse_element(element)
            if result:
                results.append(result)
        
        return results
