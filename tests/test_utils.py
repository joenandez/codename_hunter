"""Tests for utility functions."""
import pytest
from unittest.mock import patch, MagicMock
from src.utils import (
    AIEnhancer,
    TokenInfo,
    HunterError,
    fetch_url,
    validate_config,
    ProgressManager
)

def test_token_info():
    """Test TokenInfo dataclass."""
    info = TokenInfo(total_tokens=100, content_tokens=80, remaining_tokens=900)
    assert info.total_tokens == 100
    assert info.content_tokens == 80
    assert info.remaining_tokens == 900

class TestAIEnhancer:
    """Test AIEnhancer class functionality."""
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        enhancer = AIEnhancer()
        assert enhancer.api_key is None
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        enhancer = AIEnhancer(api_key="test_key")
        assert enhancer.api_key == "test_key"
    
    def test_enhance_content_without_api_key(self):
        """Test content enhancement without API key."""
        enhancer = AIEnhancer()
        content = "Test content"
        assert enhancer.enhance_content(content) == content
    
    def test_calculate_tokens(self):
        """Test token calculation."""
        enhancer = AIEnhancer()
        text = "This is a test text"
        token_info = enhancer.calculate_tokens(text)
        assert token_info.total_tokens == 5
        assert token_info.content_tokens == 5
        assert token_info.remaining_tokens == 9995

@pytest.mark.asyncio
async def test_fetch_url():
    """Test URL fetching with mocked response."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = "Test content"
        mock_get.return_value = mock_response
        
        result = fetch_url("http://test.com")
        assert result == "Test content"
        mock_get.assert_called_once_with("http://test.com")

def test_fetch_url_error():
    """Test URL fetching with error."""
    with patch('requests.get', side_effect=Exception("Network error")):
        with pytest.raises(HunterError):
            fetch_url("http://test.com")

def test_validate_config():
    """Test configuration validation."""
    valid_config = {
        'api_key': 'test_key',
        'output_format': 'markdown'
    }
    assert validate_config(valid_config) is True
    
    invalid_config = {
        'api_key': 'test_key'
    }
    assert validate_config(invalid_config) is False

@pytest.mark.asyncio
async def test_progress_manager():
    """Test progress manager context."""
    with ProgressManager() as progress:
        assert progress is not None
        # Add a task and ensure it works
        task_id = progress.add_task("Testing...", total=None)
        assert task_id is not None
