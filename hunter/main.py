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
from rich.theme import Theme

try:
    # When installed via pip
    from hunter.constants import (
        TOGETHER_API_KEY,
        TOGETHER_MODEL,
        TOGETHER_MAX_TOKENS,
        TOGETHER_TEMPERATURE,
        OUTPUT_FORMAT,
        CONSOLE_STYLE
    )
    from hunter.utils import extract_content, enhance_markdown_formatting
except ImportError:
    # When run directly from source
    from .constants import (
        TOGETHER_API_KEY,
        TOGETHER_MODEL,
        TOGETHER_MAX_TOKENS,
        TOGETHER_TEMPERATURE,
        OUTPUT_FORMAT,
        CONSOLE_STYLE
    )
    from .utils import extract_content, enhance_markdown_formatting

def check_api_status(console: Console) -> None:
    """Check and display Together API status."""
    console.print("\n[bold blue]API Status:[/bold blue]")
    if TOGETHER_API_KEY:
        masked_key = f"{TOGETHER_API_KEY[:4]}...{TOGETHER_API_KEY[-4:]}"
        console.print(f"[green]✓ Found API key: {masked_key}[/green]")
    else:
        console.print("[yellow]⚠️  No API key found[/yellow]")
        console.print("[yellow]Tip: Set TOGETHER_API_KEY environment variable or configure in ~/.config/hunter/config.ini[/yellow]")

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
    args = parse_args()
    theme = Theme({}) if CONSOLE_STYLE == 'light' else Theme({
        "info": "cyan",
        "warning": "yellow",
        "error": "red bold",
        "success": "green"
    })
    console = Console(theme=theme)
    
    try:
        # Extract content
        content = extract_content(args.url)
        
        # Check API status and enhance by default unless disabled
        if not args.no_enhance:
            check_api_status(console)
            if TOGETHER_API_KEY:
                content = enhance_markdown_formatting(content, TOGETHER_API_KEY)
            else:
                console.print("[yellow]⚠️  AI enhancement skipped - no API key configured[/yellow]")
        
        # Display the result
        console.print(Markdown(content))
        
        # Copy to clipboard by default unless disabled
        if not args.no_copy:
            pyperclip.copy(content)
            console.print("\n[green]✓[/green] Content has been copied to clipboard!")
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching URL:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
