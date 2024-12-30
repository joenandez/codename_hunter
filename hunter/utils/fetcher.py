"""Asynchronous URL fetching utilities.

This module provides asynchronous functions for fetching content from URLs.
It uses aiohttp for efficient async HTTP requests and includes proper error
handling and logging.
"""

import logging
import aiohttp
from typing import Optional
from hunter.utils.errors import HunterError

# Configure logging
logger = logging.getLogger(__name__)

async def fetch_url_async(url: str, timeout: int = 10) -> str:
    """Fetch content from URL asynchronously.
    
    Makes an asynchronous HTTP GET request to the specified URL and returns
    the response content. Includes error handling and logging.
    
    Args:
        url: The URL to fetch content from
        timeout: Request timeout in seconds (default: 10)
        
    Returns:
        str: The response content
        
    Raises:
        HunterError: If the request fails
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=timeout) as response:
                response.raise_for_status()
                return await response.text()
                
    except aiohttp.ClientError as e:
        logger.error(f"Network error fetching {url}: {str(e)}")
        raise HunterError(f"Network error: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching {url}: {str(e)}")
        raise HunterError(f"Failed to fetch URL: {str(e)}") 