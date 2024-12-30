"""Main entry point for the application.

This module provides the main entry point and CLI interface for the Hunter application.
It coordinates the content extraction, formatting, and enhancement pipeline.

Example:
    Basic usage:
        $ python -m hunter url https://example.com
        $ hunter url https://example.com

    With enhancement and clipboard:
        $ hunter url https://example.com --no-enhance --no-copy
"""

import asyncio
from pathlib import Path
import configparser
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
import pyperclip
import argparse
import sys
import os
import logging
from rich.theme import Theme

from hunter.constants import (
    TOGETHER_API_KEY,
    TOGETHER_MODEL,
    TOGETHER_MAX_TOKENS,
    TOGETHER_TEMPERATURE,
    OUTPUT_FORMAT,
    CONSOLE_STYLE
)
from hunter.utils.errors import HunterError
from hunter.utils.ai import AIEnhancer
from hunter.parsers import ContentExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_api_status(console: Console) -> None:
    """Print the API configuration status with appropriate decoration.
    
    Args:
        console: Rich console instance for status display
    """
    if TOGETHER_API_KEY:
        console.print("[green]✓ Together AI API key configured[/green]")
    else:
        console.print("[yellow]⚠️  Together AI API key not configured[/yellow]")
        console.print("\nTo configure the API key, either:")
        console.print("1. Add TOGETHER_API_KEY to your environment variables")
        console.print("2. Create a .env file with TOGETHER_API_KEY=your_key")
        console.print("\nGet your API key at: https://api.together.xyz/settings/api-keys\n")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Extract and enhance markdown content from web pages."
    )
    parser.add_argument("url", help="URL to process")
    parser.add_argument("--no-enhance", action="store_true", help="Disable AI enhancement")
    parser.add_argument("--no-copy", action="store_true", help="Disable clipboard copy")
    
    return parser.parse_args()

async def process_url(url: str, no_enhance: bool, no_copy: bool, console: Console) -> None:
    """Process a URL asynchronously.
    
    Args:
        url: URL to process
        no_enhance: Whether to skip AI enhancement
        no_copy: Whether to skip clipboard copy
        console: Rich console for output
    """
    try:
        # Extract content
        logger.info(f"Processing URL: {url}")
        extractor = ContentExtractor()
        content_list = await extractor.extract_from_url(url)
        
        # Join content into a single string
        content = '\n'.join(item.content for item in content_list)
        
        # Enhance by default unless disabled
        if not no_enhance:
            logger.debug("Checking API status before enhancement")
            print_api_status(console)
            if TOGETHER_API_KEY:
                logger.info("Enhancing content with AI")
                enhancer = AIEnhancer()
                content = await enhancer.enhance_content_async(content)
            else:
                logger.warning("Skipping enhancement: No API key available")
        
        # Display the result
        console.print(Markdown(content))
        
        # Copy to clipboard by default unless disabled
        if not no_copy:
            logger.debug("Copying content to clipboard")
            pyperclip.copy(content)
            console.print("\n[green]✓[/green] Content has been copied to clipboard!")
            
        logger.info("URL processing completed successfully")
            
    except HunterError as e:
        logger.error(f"Hunter-specific error: {str(e)}")
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

async def main_async() -> None:
    """Async main entry point for the application."""
    logger.info("Starting Hunter application")
    
    try:
        args = parse_args()
        logger.debug(f"Parsed arguments: {vars(args)}")
        
        theme = Theme({}) if CONSOLE_STYLE == 'light' else Theme({
            "info": "cyan",
            "warning": "yellow",
            "error": "red bold",
            "success": "green"
        })
        console = Console(theme=theme)
        
        await process_url(args.url, args.no_enhance, args.no_copy, console)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        console = Console()
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

def main() -> None:
    """Main entry point for the application."""
    asyncio.run(main_async())
