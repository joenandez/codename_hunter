"""Tests for asynchronous operations."""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, PropertyMock
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
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = PropertyMock(return_value=asyncio.Future())
        mock_response.json.return_value.set_result({
            "choices": [{
                "message": {"content": "Enhanced content"}
            }],
            "usage": {
                "total_tokens": 100,
                "prompt_tokens": 50,
                "completion_tokens": 50
            }
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        content = "Original content"
        enhanced = await enhancer.enhance_content_async(content)
        assert enhanced == "Enhanced content"

@pytest.mark.asyncio
async def test_enhance_content_async_failure():
    """Test content enhancement failure."""
    enhancer = AIEnhancer()
    with patch('aiohttp.ClientSession.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.json = PropertyMock(return_value=asyncio.Future())
        mock_response.json.return_value.set_result({
            "error": "Internal server error"
        })
        mock_post.return_value.__aenter__.return_value = mock_response

        content = "Original content"
        result = await enhancer.enhance_content_async(content)
        assert result == content  # Should return original content on failure 