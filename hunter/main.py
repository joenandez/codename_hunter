"""Main entry point for the application.

This module provides the main entry point and CLI interface for the Hunter application.
It coordinates the content extraction, formatting, and enhancement pipeline.

Example:
    Basic usage:
        $ python -m hunter url https://example.com
        $ hunter url https://example.com

    With enhancement and clipboard:
        $ hunter url https://example.com --no-enhance --no-copy
        
    Configure API key:
        $ hunter config --set-api-key
        $ hunter config --show
"""

from pathlib import Path
import configparser
from getpass import getpass
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

CONFIG_DIR = Path.home() / '.config' / 'hunter'
CONFIG_FILE = CONFIG_DIR / 'config.ini'

def ensure_config_dir() -> None:
    """Ensure configuration directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Secure the directory permissions
    CONFIG_DIR.chmod(0o700)

def load_config() -> configparser.ConfigParser:
    """Load configuration from file."""
    config = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        config.read(CONFIG_FILE)
    return config

def save_config(config: configparser.ConfigParser) -> None:
    """Save configuration to file."""
    ensure_config_dir()
    with CONFIG_FILE.open('w') as f:
        config.write(f)
    # Secure the file permissions
    CONFIG_FILE.chmod(0o600)

def get_api_key() -> Optional[str]:
    """Get API key from environment or config file."""
    # Environment variable takes precedence
    if key := os.getenv('TOGETHER_API_KEY'):
        return key
    
    # Try config file
    config = load_config()
    return config.get('api', 'together_api_key', fallback=None)

def set_api_key(key: Optional[str] = None) -> None:
    """Set API key in configuration file."""
    if not key:
        key = getpass("Enter your Together API key: ")
    
    config = load_config()
    if 'api' not in config:
        config['api'] = {}
    config['api']['together_api_key'] = key
    save_config(config)
    print("[green]✓[/green] API key saved successfully!")

def show_config(console: Console) -> None:
    """Display current configuration."""
    config = load_config()
    console.print("\n[bold blue]Configuration:[/bold blue]")
    
    # Show API key status
    key = get_api_key()
    if key:
        masked_key = f"{key[:4]}...{key[-4:]}"
        console.print(f"[green]✓ API key configured: {masked_key}[/green]")
    else:
        console.print("[yellow]⚠️  No API key configured[/yellow]")
        console.print("[yellow]Tip: Set it using 'hunter config --set-api-key'[/yellow]")

def check_api_status(console: Console) -> None:
    """Check and display Together API status."""
    console.print("\n[bold blue]API Status:[/bold blue]")
    if key := get_api_key():
        masked_key = f"{key[:4]}...{key[-4:]}"
        console.print(f"[green]✓ Found API key: {masked_key}[/green]")
    else:
        console.print("[yellow]⚠️  No API key found[/yellow]")
        console.print("[yellow]Tip: Set it using 'hunter config --set-api-key'[/yellow]")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract and enhance markdown content from web pages.",
        epilog="Example: hunter https://example.com -e -c"
    )
    
    # Create subparsers for different modes
    subparsers = parser.add_subparsers(dest='command')
    
    # URL processing mode (default)
    url_parser = subparsers.add_parser('url', help='Process a URL (default mode)')
    url_parser.add_argument("url", help="URL to process")
    url_parser.add_argument("--no-enhance", action="store_true",
                           help="Disable AI enhancement")
    url_parser.add_argument("--no-copy", action="store_true",
                           help="Disable clipboard copy")
    
    # Config mode
    config_parser = subparsers.add_parser('config', help='Configure settings')
    config_parser.add_argument("--set-api-key", action="store_true",
                              help="Set Together API key")
    config_parser.add_argument("--show", action="store_true",
                              help="Show current configuration")
    
    args = parser.parse_args()
    
    # If no command is specified but a URL-like argument is present, treat it as URL mode
    if not args.command and len(sys.argv) > 1 and '://' in sys.argv[1]:
        return parser.parse_args(['url'] + sys.argv[1:])
    
    # Validate arguments
    if not args.command:
        parser.error("Please provide a URL to process or use 'config' command")
    
    return args

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
    
    if args.command == 'config':
        if args.set_api_key:
            set_api_key()
        if args.show:
            show_config(console)
        return
    
    # URL processing (default command)
    try:
        # Extract content
        content = extract_content(args.url)
        
        # Check API status and enhance by default unless disabled
        if not args.no_enhance:
            check_api_status(console)
            if key := get_api_key():
                content = enhance_markdown_formatting(content, key)
            else:
                console.print("[yellow]⚠️  AI enhancement skipped - no API key configured[/yellow]")
        
        # Copy to clipboard by default unless disabled
        if not args.no_copy:
            pyperclip.copy(content)
            console.print("\n[green]✓[/green] Content has been copied to clipboard!")
        
        # Display the result
        console.print(Markdown(content))
        
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error fetching URL:[/red] {str(e)}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
