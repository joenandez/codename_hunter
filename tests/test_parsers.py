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
        assert result.content == '# Test Heading'
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
        assert result.content == '\nTest paragraph content\n'
    
    def test_parse_empty(self):
        parser = ParagraphParser()
        element = create_element('<p>  </p>').p
        result = parser.parse(element)
        assert result is None
    
    def test_paragraph_spacing(self):
        parser = ParagraphParser()
        element = create_element('<p>Test paragraph content</p>').p
        result = parser.parse(element)
        assert result.content_type == ContentType.PARAGRAPH
        assert result.content.startswith('\n')
        assert result.content.endswith('\n')
        assert result.content == '\nTest paragraph content\n'

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
    
    def test_extract_from_html_heading_formatting(self):
        html = '''
        <div>
            <h1>Title 1</h1>
            <h2>Title 2</h2>
            <h3>Title 3</h3>
        </div>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        # Verify heading formatting
        headings = [r.content for r in results if r.content_type == ContentType.HEADING]
        assert '# Title 1' in headings
        assert '## Title 2' in headings
        assert '### Title 3' in headings

    def test_main_content_detection_semantic_main(self):
        """Test detection of content within semantic <main> tag."""
        html = '''
        <html>
            <body>
                <header>Skip this</header>
                <main>
                    <h1>Main Content</h1>
                    <p>Important paragraph</p>
                </main>
                <footer>Skip this too</footer>
            </body>
        </html>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        content = ' '.join(r.content for r in results)
        assert 'Main Content' in content
        assert 'Important paragraph' in content
        assert 'Skip this' not in content
        assert 'Skip this too' not in content

    def test_main_content_detection_by_id(self):
        """Test detection of content using ID-based strategy."""
        html = '''
        <html>
            <body>
                <div>Skip this outer content</div>
                <div id="main-wrap">
                    <h1>Main Section</h1>
                    <p>Content in main-wrap</p>
                </div>
                <div id="sidebar">Skip sidebar</div>
            </body>
        </html>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        content = ' '.join(r.content for r in results)
        assert 'Main Section' in content
        assert 'Content in main-wrap' in content
        assert 'Skip this outer content' not in content
        assert 'Skip sidebar' not in content

    def test_main_content_detection_by_class(self):
        """Test detection of content using class-based strategy."""
        html = '''
        <html>
            <body>
                <nav>Skip navigation</nav>
                <div class="article-content">
                    <h1>Article Title</h1>
                    <p>Article content here</p>
                </div>
                <aside>Skip aside</aside>
            </body>
        </html>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        content = ' '.join(r.content for r in results)
        assert 'Article Title' in content
        assert 'Article content here' in content
        assert 'Skip navigation' not in content
        assert 'Skip aside' not in content

    def test_main_content_detection_article_tag(self):
        """Test detection of content using article tag fallback."""
        html = '''
        <html>
            <body>
                <header>Skip header</header>
                <article>
                    <h1>Blog Post</h1>
                    <p>Blog content</p>
                </article>
                <footer>Skip footer</footer>
            </body>
        </html>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        content = ' '.join(r.content for r in results)
        assert 'Blog Post' in content
        assert 'Blog content' in content
        assert 'Skip header' not in content
        assert 'Skip footer' not in content

    def test_main_content_detection_body_fallback(self):
        """Test fallback to body when no main content area is found."""
        html = '''
        <html>
            <body>
                <h1>Page Title</h1>
                <p>Simple page with no main content markers</p>
            </body>
        </html>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        content = ' '.join(r.content for r in results)
        assert 'Page Title' in content
        assert 'Simple page with no main content markers' in content

    def test_main_content_detection_nested_structure(self):
        """Test handling of deeply nested content structures."""
        html = '''
        <html>
            <body>
                <div class="wrapper">
                    <div class="container">
                        <main id="content">
                            <article>
                                <h1>Deep Content</h1>
                                <p>Nested content here</p>
                            </article>
                        </main>
                    </div>
                </div>
            </body>
        </html>
        '''
        extractor = ContentExtractor()
        results = extractor.extract_from_html(html)
        
        content = ' '.join(r.content for r in results)
        assert 'Deep Content' in content
        assert 'Nested content here' in content
