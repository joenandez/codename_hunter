"""Common test fixtures."""
import pytest
from hunter.parsers import ContentExtractor
from hunter.utils.ai import AIEnhancer
from hunter.formatters import BaseFormatter, CodeFormatter, LinkFormatter
import os

@pytest.fixture(autouse=True)
def mock_together_api_key(monkeypatch):
    """Mock Together API key for tests."""
    monkeypatch.setenv('TOGETHER_API_KEY', 'test_key')

@pytest.fixture
def extractor():
    """Fixture for ContentExtractor."""
    return ContentExtractor()

@pytest.fixture
def enhancer():
    """Fixture for AIEnhancer."""
    return AIEnhancer()

@pytest.fixture
def base_formatter():
    """Fixture for BaseFormatter."""
    return BaseFormatter()

@pytest.fixture
def code_formatter():
    """Fixture for CodeFormatter."""
    return CodeFormatter()

@pytest.fixture
def link_formatter():
    """Fixture for LinkFormatter."""
    return LinkFormatter()

@pytest.fixture
def sample_html():
    """Fixture for sample HTML content."""
    return """
    <html>
        <body>
            <h1>Test Heading</h1>
            <p>Test paragraph</p>
            <pre><code class="language-python">def test():
    pass</code></pre>
            <ul>
                <li>Item 1</li>
                <li>Item 2</li>
            </ul>
            <a href="https://example.com">Test Link</a>
        </body>
    </html>
    """ 