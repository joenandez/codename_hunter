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

from pathlib import Path
import configparser
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
import pyperclip
import requests
from bs4 import BeautifulSoup
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
from hunter.utils import (
    extract_content,
    enhance_markdown_formatting,
    print_api_status,
    HunterError,
    logger
)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract and enhance markdown content from web pages.",
        epilog="Example: hunter https://example.com"
    )
    
    # First, check if the first argument is a URL
    if len(sys.argv) > 1 and '://' in sys.argv[1]:
        # Add main arguments
        parser.add_argument("url", help="URL to process")
        parser.add_argument("--no-enhance", action="store_true",
                           help="Disable AI enhancement")
        parser.add_argument("--no-copy", action="store_true",
                           help="Disable clipboard copy")
        args = parser.parse_args()
        # Explicitly set command for direct URL usage
        args.command = 'url'
        return args
    
    # If not a URL, use subcommands
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # URL processing mode (allow both 'url' and 'uri' commands)
    for cmd in ['url', 'uri']:
        url_parser = subparsers.add_parser(cmd, help='Process a URL')
        url_parser.add_argument("url", help="URL to process")
        url_parser.add_argument("--no-enhance", action="store_true",
                               help="Disable AI enhancement")
        url_parser.add_argument("--no-copy", action="store_true",
                               help="Disable clipboard copy")
    
    return parser.parse_args()

def main() -> None:
    """Main entry point for the application."""
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
        
        try:
            # Extract content
            logger.info(f"Processing URL: {args.url}")
            content = extract_content(args.url)
            
            # Enhance by default unless disabled
            if not args.no_enhance:
                logger.debug("Checking API status before enhancement")
                print_api_status(console)
                if TOGETHER_API_KEY:
                    logger.info("Enhancing content with AI")
                    content = enhance_markdown_formatting(content, TOGETHER_API_KEY)
                else:
                    logger.warning("Skipping enhancement: No API key available")
            
            # Display the result
            console.print(Markdown(content))
            
            # Copy to clipboard by default unless disabled
            if not args.no_copy:
                logger.debug("Copying content to clipboard")
                pyperclip.copy(content)
                console.print("\n[green]✓[/green] Content has been copied to clipboard!")
                
            logger.info("URL processing completed successfully")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching URL: {str(e)}")
            console.print(f"[red]Error fetching URL:[/red] {str(e)}")
            sys.exit(1)
        except HunterError as e:
            logger.error(f"Hunter-specific error: {str(e)}")
            console.print(f"[red]Error:[/red] {str(e)}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        console = Console()
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        sys.exit(1)
    finally:
        logger.info("Hunter application shutting down")

if __name__ == "__main__":
    main()
