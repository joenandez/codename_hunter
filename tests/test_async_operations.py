"""Tests for asynchronous operations."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, PropertyMock, AsyncMock
from aiohttp import ClientSession, ClientResponse, web
from hunter.utils.fetcher import fetch_url_async
from hunter.utils.ai import AIEnhancer
from hunter.utils.errors import HunterError
from hunter.utils.progress import ProgressManager

@pytest.mark.asyncio
async def test_fetch_url_async_success():
    """Test successful URL fetching."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.text = PropertyMock(return_value=asyncio.Future())
        mock_response.text.return_value.set_result("Test content")
        mock_get.return_value.__aenter__.return_value = mock_response

        content = await fetch_url_async("https://example.com")
        assert content == "Test content"

@pytest.mark.asyncio
async def test_fetch_url_async_failure():
    """Test URL fetching failure."""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 500
        mock_get.return_value.__aenter__.return_value = mock_response

        with pytest.raises(HunterError):
            await fetch_url_async("https://example.com")

@pytest.mark.asyncio
async def test_enhance_content_async_success():
    """Test successful content enhancement."""
    enhancer = AIEnhancer(api_key="test_key")
    
    # Create response data
    response_data = {
        "choices": [{
            "message": {"content": "Enhanced content"}
        }],
        "usage": {
            "total_tokens": 100,
            "prompt_tokens": 50,
            "completion_tokens": 50
        }
    }
    
    # Mock the progress manager
    mock_progress = AsyncMock()
    mock_progress.add_task = MagicMock(return_value=1)
    mock_progress.advance = MagicMock()
    mock_progress.remove_task = MagicMock()
    mock_progress.__aenter__.return_value = mock_progress
    
    # Mock the response using the same pattern as test_fetch_url_async_success
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = PropertyMock(return_value=asyncio.Future())
        mock_response.json.return_value.set_result(response_data)
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch('hunter.utils.ai.ProgressManager', return_value=mock_progress), \
             patch('hunter.utils.ai.TOGETHER_MODEL', 'test-model'), \
             patch('hunter.utils.ai.TOGETHER_MAX_TOKENS', 1000), \
             patch('hunter.utils.ai.TOGETHER_TEMPERATURE', 0.5):
            content = "Original content"
            enhanced = await enhancer.enhance_content_async(content)
            assert enhanced == "Enhanced content"

@pytest.mark.asyncio
async def test_enhance_content_async_failure():
    """Test content enhancement failure."""
    enhancer = AIEnhancer(api_key="test_key")
    
    # Mock the progress manager
    mock_progress = AsyncMock()
    mock_progress.add_task = MagicMock(return_value=1)
    mock_progress.advance = MagicMock()
    mock_progress.remove_task = MagicMock()
    mock_progress.__aenter__.return_value = mock_progress
    
    # Mock the response using the same pattern as test_fetch_url_async_success
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.json = PropertyMock(return_value=asyncio.Future())
        mock_response.json.return_value.set_result({"error": "Internal server error"})
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch('hunter.utils.ai.ProgressManager', return_value=mock_progress), \
             patch('hunter.utils.ai.TOGETHER_MODEL', 'test-model'), \
             patch('hunter.utils.ai.TOGETHER_MAX_TOKENS', 1000), \
             patch('hunter.utils.ai.TOGETHER_TEMPERATURE', 0.5):
            content = "Original content"
            result = await enhancer.enhance_content_async(content)
            assert result == content  # Should return original content on failure