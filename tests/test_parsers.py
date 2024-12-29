"""Tests for the parser module."""
import pytest
from bs4 import BeautifulSoup
from hunter.parsers import (
    ContentType,
    HeadingParser,
    CodeBlockParser,
    ListParser,
    LinkParser,
    ParagraphParser,
    ParserFactory,
    ContentExtractor
)

def create_element(html: str) -> BeautifulSoup:
    """Helper to create a BeautifulSoup element."""
    return BeautifulSoup(html, 'html.parser')

class TestHeadingParser:
    def test_can_parse(self):
        parser = HeadingParser()
        assert parser.can_parse(create_element('<h1>Test</h1>').h1)
        assert parser.can_parse(create_element('<h2>Test</h2>').h2)
        assert not parser.can_parse(create_element('<p>Test</p>').p)
    
    def test_parse(self):
        parser = HeadingParser()
        element = create_element('<h1>Test Heading</h1>').h1
        result = parser.parse(element)
        assert result.content_type == ContentType.HEADING
        assert result.content == 'Test Heading'
        assert result.metadata['level'] == 1

class TestCodeBlockParser:
    def test_can_parse(self):
        parser = CodeBlockParser()
        assert parser.can_parse(create_element('<pre><code>def test():</code></pre>').pre)
        assert parser.can_parse(create_element('<code>import os</code>').code)
        assert not parser.can_parse(create_element('<p>Test</p>').p)
    
    def test_parse_with_language(self):
        parser = CodeBlockParser()
        html = '''
        <pre><code class="language-python">
        def hello():
            print("Hello, World!")
        </code></pre>
        '''
        element = create_element(html).pre
        result = parser.parse(element)
        assert result.content_type == ContentType.CODE_BLOCK
        assert 'def hello():' in result.content
        assert 'print("Hello, World!")' in result.content
        assert result.metadata['language'] == 'python'

class TestListParser:
    def test_can_parse(self):
        parser = ListParser()
        assert parser.can_parse(create_element('<ul><li>Test</li></ul>').ul)
        assert parser.can_parse(create_element('<ol><li>Test</li></ol>').ol)
        assert not parser.can_parse(create_element('<p>Test</p>').p)
    
    def test_parse_unordered_list(self):
        parser = ListParser()
        html = '''
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
            <li>Item 3</li>
        </ul>
        '''
        element = create_element(html).ul
        result = parser.parse(element)
        assert result.content_type == ContentType.LIST
        assert '- Item 1' in result.content
        assert '- Item 2' in result.content
        assert result.metadata['list_type'] == 'ul'
    
    def test_parse_ordered_list(self):
        parser = ListParser()
        html = '''
        <ol>
            <li>First</li>
            <li>Second</li>
            <li>Third</li>
        </ol>
        '''
        element = create_element(html).ol
        result = parser.parse(element)
        assert result.content_type == ContentType.LIST
        assert '1. First' in result.content
        assert '2. Second' in result.content
        assert result.metadata['list_type'] == 'ol'
    
    def test_nested_list(self):
        parser = ListParser()
        html = '''
        <ul>
            <li>Item 1
                <ul>
                    <li>Nested 1</li>
                    <li>Nested 2</li>
                </ul>
            </li>
            <li>Item 2</li>
        </ul>
        '''
        element = create_element(html).ul
        result = parser.parse(element)
        assert result.content_type == ContentType.LIST
        assert '- Item 1' in result.content
        assert '  - Nested 1' in result.content
        assert '- Item 2' in result.content

class TestLinkParser:
    def test_can_parse(self):
        parser = LinkParser()
        assert parser.can_parse(create_element('<a href="#">Test</a>').a)
        assert parser.can_parse(create_element('<img src="test.jpg" />').img)
        assert not parser.can_parse(create_element('<p>Test</p>').p)
    
    def test_parse_link(self):
        parser = LinkParser()
        element = create_element('<a href="https://example.com">Example</a>').a
        result = parser.parse(element)
        assert result.content_type == ContentType.LINK
        assert 'Example' in result.content
        assert 'https://example.com' in result.content
        assert not result.metadata['is_image']
    
    def test_parse_image(self):
        parser = LinkParser()
        element = create_element('<img src="test.jpg" alt="Test Image" />').img
        result = parser.parse(element)
        assert result.content_type == ContentType.IMAGE
        assert 'Test Image' in result.content
        assert 'test.jpg' in result.content
        assert result.metadata['is_image']

class TestParagraphParser:
    def test_can_parse(self):
        parser = ParagraphParser()
        assert parser.can_parse(create_element('<p>Test</p>').p)
        assert not parser.can_parse(create_element('<div>Test</div>').div)
    
    def test_parse(self):
        parser = ParagraphParser()
        element = create_element('<p>Test paragraph content</p>').p
        result = parser.parse(element)
        assert result.content_type == ContentType.PARAGRAPH
        assert result.content == 'Test paragraph content'
    
    def test_parse_empty(self):
        parser = ParagraphParser()
        element = create_element('<p>  </p>').p
        result = parser.parse(element)
        assert result is None

class TestParserFactory:
    def test_get_parser(self):
        factory = ParserFactory()
        
        # Test each element type gets the correct parser
        heading = create_element('<h1>Test</h1>').h1
        code = create_element('<pre><code>Test</code></pre>').pre
        list_el = create_element('<ul><li>Test</li></ul>').ul
        link = create_element('<a href="#">Test</a>').a
        para = create_element('<p>Test</p>').p
        
        assert isinstance(factory.get_parser(heading), HeadingParser)
        assert isinstance(factory.get_parser(code), CodeBlockParser)
        assert isinstance(factory.get_parser(list_el), ListParser)
        assert isinstance(factory.get_parser(link), LinkParser)
        assert isinstance(factory.get_parser(para), ParagraphParser)
        
        # Test unknown element returns None
        div = create_element('<div>Test</div>').div
        assert factory.get_parser(div) is None

class TestContentExtractor:
    def test_extract_from_html_basic(self):
        html = '''
        <div>
            <h1>Title</h1>
            <p>Paragraph 1</p>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <pre><code>print("Hello")</code></pre>
            <a href="https://example.com">Link</a>
        </div>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        # Verify we got all expected elements
        content_types = [r.content_type for r in results]
        assert ContentType.HEADING in content_types
        assert ContentType.PARAGRAPH in content_types
        assert ContentType.LIST in content_types
        assert ContentType.CODE_BLOCK in content_types
        assert ContentType.LINK in content_types
    
    def test_extract_from_html_skip_elements(self):
        html = '''
        <div>
            <h1>Title</h1>
            <script>alert("skip")</script>
            <nav>Skip this</nav>
            <div class="sidebar">Skip this too</div>
            <p>Keep this</p>
        </div>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        # Verify skipped elements are not included
        texts = [r.content for r in results]
        assert 'Title' in ' '.join(texts)
        assert 'Keep this' in ' '.join(texts)
        assert 'Skip this' not in ' '.join(texts)
        assert 'alert' not in ' '.join(texts)
