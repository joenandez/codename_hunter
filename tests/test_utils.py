"""Tests for utility functions."""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from hunter.utils import (
    AIEnhancer,
    TokenInfo,
    HunterError,
    validate_config,
    ProgressManager,
    error_handler,
    async_error_handler
)
from hunter.utils.fetcher import fetch_url_async
import asyncio

def test_token_info():
    """Test TokenInfo dataclass."""
    info = TokenInfo(total_tokens=100, content_tokens=80, remaining_tokens=900)
    assert info.total_tokens == 100
    assert info.content_tokens == 80
    assert info.remaining_tokens == 900

class TestErrorHandling:
    """Test error handling utilities."""
    
    def test_hunter_error(self):
        """Test HunterError exception."""
        with pytest.raises(HunterError) as exc_info:
            raise HunterError("Test error")
        assert str(exc_info.value) == "Test error"
    
    def test_error_handler_success(self):
        """Test error_handler with successful function."""
        @error_handler
        def successful_function():
            return "success"
        
        assert successful_function() == "success"
    
    def test_error_handler_failure(self):
        """Test error_handler with failing function."""
        @error_handler
        def failing_function():
            raise ValueError("Test failure")
        
        with pytest.raises(HunterError) as exc_info:
            failing_function()
        assert "Test failure" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_error_handler_success(self):
        """Test async_error_handler with successful function."""
        @async_error_handler
        async def successful_async_function():
            return "success"
        
        result = await successful_async_function()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_async_error_handler_failure(self):
        """Test async_error_handler with failing function."""
        @async_error_handler
        async def failing_async_function():
            raise ValueError("Test failure")
        
        with pytest.raises(HunterError) as exc_info:
            await failing_async_function()
        assert "Test failure" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_async_error_handler_cancellation(self):
        """Test async_error_handler with cancellation."""
        class TestClass:
            def __init__(self):
                self.default_return_value = "default"
        
        @async_error_handler
        async def cancellable_function(self):
            raise asyncio.CancelledError()
        
        test_instance = TestClass()
        result = await cancellable_function(test_instance)
        assert result == "default"
    
    @pytest.mark.asyncio
    async def test_async_error_handler_keyboard_interrupt(self):
        """Test async_error_handler with keyboard interrupt."""
        @async_error_handler
        async def interruptible_function():
            raise KeyboardInterrupt()
        
        result = await interruptible_function()
        assert result is None

class TestAIEnhancer:
    """Test AIEnhancer class functionality."""
    
    def test_init_without_api_key(self):
        """Test initialization without API key."""
        with patch('hunter.utils.ai.TOGETHER_API_KEY', None):
            enhancer = AIEnhancer()
            assert enhancer.api_key is None
    
    def test_init_with_api_key(self):
        """Test initialization with API key."""
        enhancer = AIEnhancer(api_key="test_key")
        assert enhancer.api_key == "test_key"
    
    @pytest.mark.asyncio
    async def test_enhance_content_without_api_key(self):
        """Test content enhancement without API key."""
        with patch('hunter.utils.ai.TOGETHER_API_KEY', None):
            enhancer = AIEnhancer()
            content = "Test content"
            enhanced = await enhancer.enhance_content_async(content)
            assert enhanced == content
    
    def test_get_token_usage(self):
        """Test token usage calculation."""
        enhancer = AIEnhancer()
        response = {
            "usage": {
                "total_tokens": 100,
                "completion_tokens": 80,
            }
        }
        token_info = enhancer.get_token_usage(response)
        assert token_info.total_tokens == 100
        assert token_info.content_tokens == 80

@pytest.mark.asyncio
async def test_fetch_url():
    """Test URL fetching with mocked response."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.text = PropertyMock(return_value=asyncio.Future())
        mock_response.text.return_value.set_result("Test content")
        mock_get.return_value.__aenter__.return_value = mock_response
        
        result = await fetch_url_async("http://test.com")
        assert result == "Test content"

@pytest.mark.asyncio
async def test_fetch_url_error():
    """Test URL fetching with error."""
    with patch('aiohttp.ClientSession.get', side_effect=Exception("Network error")):
        with pytest.raises(HunterError):
            await fetch_url_async("http://test.com")

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
