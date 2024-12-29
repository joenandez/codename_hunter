"""Tests for asynchronous operations."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, PropertyMock, AsyncMock
from hunter.utils.fetcher import fetch_url_async
from hunter.utils.ai import AIEnhancer
from hunter.utils.errors import HunterError

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
    enhancer = AIEnhancer()
    
    # Mock the session context manager
    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    
    # Mock the response context manager
    response_mock = MagicMock()
    response_mock.__aenter__.return_value = response_mock
    response_mock.__aexit__.return_value = None
    response_mock.status = 200
    
    # Mock the json response
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
    response_mock.json = AsyncMock(return_value=response_data)
    
    # Set up the session to return our response
    session_mock.post.return_value = response_mock
    
    with patch('aiohttp.ClientSession', return_value=session_mock):
        content = "Original content"
        enhanced = await enhancer.enhance_content_async(content)
        assert enhanced == "Enhanced content"

@pytest.mark.asyncio
async def test_enhance_content_async_failure():
    """Test content enhancement failure."""
    enhancer = AIEnhancer()
    
    # Mock the session context manager
    session_mock = MagicMock()
    session_mock.__aenter__.return_value = session_mock
    session_mock.__aexit__.return_value = None
    
    # Mock the response context manager
    response_mock = MagicMock()
    response_mock.__aenter__.return_value = response_mock
    response_mock.__aexit__.return_value = None
    response_mock.status = 500
    response_mock.json = AsyncMock(return_value={"error": "Internal server error"})
    
    # Set up the session to return our response
    session_mock.post.return_value = response_mock
    
    with patch('aiohttp.ClientSession', return_value=session_mock):
        content = "Original content"
        result = await enhancer.enhance_content_async(content)
        assert result == content  # Should return original content on failure 