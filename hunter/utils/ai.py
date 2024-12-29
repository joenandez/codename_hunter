"""AI enhancement utilities.

This module provides asynchronous AI-based content enhancement using the Together API.
It includes token tracking, cost estimation, and proper error handling.
"""

import logging
import aiohttp
import asyncio
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from hunter.utils.errors import HunterError, async_error_handler
from hunter.utils.progress import ProgressManager
from hunter.constants import (
    TOGETHER_API_KEY,
    TOGETHER_MODEL,
    TOGETHER_MAX_TOKENS,
    TOGETHER_TEMPERATURE,
    TOGETHER_PRICE_PER_MILLION_TOKENS
)

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TokenInfo:
    """Information about token usage and limits.
    
    This class tracks token usage for AI operations, helping to manage
    rate limits and costs.
    
    Attributes:
        total_tokens (int): Total number of tokens used
        content_tokens (int): Tokens used for content (excluding system tokens)
        remaining_tokens (int): Tokens remaining in the current quota
    """
    total_tokens: int
    content_tokens: int
    remaining_tokens: int

class AIEnhancer:
    """Handles AI-based content enhancement operations using Together API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional API key.
        
        Args:
            api_key: Together API key (defaults to TOGETHER_API_KEY from constants)
        """
        self.api_key = api_key or TOGETHER_API_KEY
        self.default_return_value = None  # Will be set to the original content in enhance_content_async
    
    @async_error_handler
    async def enhance_content_async(self, content: str) -> str:
        """Enhance content using Together AI asynchronously.
        
        Args:
            content: The content to enhance
            
        Returns:
            str: Enhanced content or original if enhancement fails
        """
        # Set the default return value to the original content
        self.default_return_value = content
        
        if not self.api_key:
            logger.warning("No API key available for AI enhancement")
            return content
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        messages = [{
            "role": "system",
            "content": """You are a markdown formatting expert. Improve the formatting while preserving all information and links. Focus on:
1. Consistent spacing between sections
2. Beautiful list formatting
3. Proper code block presentation
4. Clear section hierarchy
5. Clean link and inline code formatting

Return ONLY the raw markdown content."""
        }, {
            "role": "user",
            "content": f"Here is the markdown content to improve:\n\n{content}"
        }]

        async with ProgressManager() as progress_mgr:
            task_id = progress_mgr.add_task("Enhancing content with Together AI...")
            spinner_task = None
            
            try:
                # Create a background task to update the spinner
                async def update_spinner():
                    while True:
                        progress_mgr.advance(task_id)
                        await asyncio.sleep(0.1)  # Update every 100ms
                
                spinner_task = asyncio.create_task(update_spinner())
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.together.xyz/v1/chat/completions",
                        headers=headers,
                        json={
                            "model": TOGETHER_MODEL,
                            "messages": messages,
                            "max_tokens": TOGETHER_MAX_TOKENS,
                            "temperature": TOGETHER_TEMPERATURE
                        },
                        timeout=30
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            if "choices" in result and result["choices"]:
                                # Log token usage and cost information
                                if "usage" in result:
                                    usage = result["usage"]
                                    total_tokens = usage.get("total_tokens", 0)
                                    cost = (total_tokens / 1_000_000) * TOGETHER_PRICE_PER_MILLION_TOKENS
                                    logger.info(
                                        f"Token usage - Prompt: {usage.get('prompt_tokens', 0)}, "
                                        f"Completion: {usage.get('completion_tokens', 0)}, "
                                        f"Total: {total_tokens} "
                                        f"(Cost: ${cost:.4f})"
                                    )
                                return result["choices"][0]["message"]["content"].strip()
                        
                        logger.error(f"AI enhancement failed: {response.status}")
                        return content
            finally:
                if spinner_task:
                    spinner_task.cancel()
                    try:
                        await spinner_task
                    except asyncio.CancelledError:
                        pass
                progress_mgr.remove_task(task_id)
    
    def get_token_usage(self, response_json: Dict[str, Any]) -> TokenInfo:
        """Extract token usage information from API response.
        
        Args:
            response_json: The JSON response from Together API
            
        Returns:
            TokenInfo: Token usage information
        """
        usage = response_json.get("usage", {})
        return TokenInfo(
            total_tokens=usage.get("total_tokens", 0),
            content_tokens=usage.get("completion_tokens", 0),
            remaining_tokens=TOGETHER_MAX_TOKENS - usage.get("total_tokens", 0)
        ) 