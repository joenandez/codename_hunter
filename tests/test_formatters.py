import pytest
from bs4 import BeautifulSoup
from hunter.formatters import BaseFormatter, CodeFormatter, LinkFormatter

def test_base_formatter_clean_content():
    formatter = BaseFormatter()
    
    # Test text cleaning
    text = "This  is _123 some text  with #  extra spaces"
    assert formatter.clean_content(text) == "This is some text with extra spaces"
    
    # Test more complex cases
    text2 = "Multiple_1 numbers_2 in_3 text"
    assert formatter.clean_content(text2) == "Multiple numbers in text"
    
    # Test with backticks
    text3 = "Code`like`this"
    assert formatter.clean_content(text3) == "Code ` like ` this"

def test_code_formatter_is_code_block():
    formatter = CodeFormatter()
    
    # Test with pre tag
    element = BeautifulSoup('<pre><code>test</code></pre>', 'html.parser').find('code')
    assert formatter.is_code_block("test", element) is True
    
    # Test with code class
    element = BeautifulSoup('<code class="language-python">test</code>', 'html.parser').find('code')
    assert formatter.is_code_block("test", element) is True
    
    # Test with code patterns
    assert formatter.is_code_block("def test():\n    return True") is True
    assert formatter.is_code_block("This is normal text") is False

def test_code_formatter_detect_language():
    formatter = CodeFormatter()
    
    # Test class-based detection
    element = BeautifulSoup('<code class="language-python">test</code>', 'html.parser').find('code')
    assert formatter.detect_language(element) == "python"
    
    # Test content-based detection
    element = BeautifulSoup('<code>def test():\n    pass</code>', 'html.parser').find('code')
    assert formatter.detect_language(element) == "python"

def test_code_formatter_format_code_block():
    formatter = CodeFormatter()
    
    code = """
    function test() {
        return true;
    }
    """
    expected = '\n```javascript\nfunction test() {\n    return true;\n}\n```\n'
    assert formatter.format_code_block(code, "javascript") == expected

def test_link_formatter():
    formatter = LinkFormatter()
    
    # Test link formatting
    element = BeautifulSoup('<a href="https://example.com">Test Link</a>', 'html.parser').find('a')
    assert formatter.format_link(element) == " [Test Link](https://example.com) "
    
    # Test link without href
    element = BeautifulSoup('<a>Test Link</a>', 'html.parser').find('a')
    assert formatter.format_link(element) == "Test Link"

def test_image_formatter():
    formatter = LinkFormatter()
    
    # Test image with title
    element = BeautifulSoup('<img src="test.jpg" alt="Test" title="Title">', 'html.parser').find('img')
    assert formatter.format_image(element) == '\n![Test](test.jpg "Title")\n'
    
    # Test image without title
    element = BeautifulSoup('<img src="test.jpg" alt="Test">', 'html.parser').find('img')
    assert formatter.format_image(element) == '\n![Test](test.jpg)\n'
    
    # Test image without src
    element = BeautifulSoup('<img alt="Test">', 'html.parser').find('img')
    assert formatter.format_image(element) == ''
