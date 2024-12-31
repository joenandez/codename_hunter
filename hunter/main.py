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
from datetime import datetime

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
        console.print("\nTo unset the API key if needed:")
        console.print("1. Unix/macOS: unset TOGETHER_API_KEY")
        console.print("2. Windows: set TOGETHER_API_KEY=")
        console.print("3. Or delete the TOGETHER_API_KEY line from your .env file\n")
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
        description="""
██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
                                                    
🎯 Hunter - Converts web pages to clean, well-formatted Markdown to make it easier to work with AI Code Editors.

📝 Description:
  This tool extracts content from web pages and converts it to markdown format.
  It can optionally enhance the output using AI (requires Together.ai API key).

🔑 API Key Configuration:
  To enable AI enhancement, set your Together.ai API key using one of these methods:

  1. Environment variable (recommended, case-insensitive):
     export TOGETHER_API_KEY='your_api_key_here'
     # On Windows: set TOGETHER_API_KEY=your_api_key_here

  2. Create a .env file in your working directory (case-insensitive):
     TOGETHER_API_KEY=your_api_key_here

  🌐 Get your API key at: https://api.together.xyz/settings/api-keys

📋 Common Use Cases:
  1. Basic usage (copies to clipboard):
     hunter https://example.com

  2. Save to default folder (hunter_docs):
     hunter https://example.com -d

  3. Save to custom folder:
     hunter https://example.com -d my_docs

  4. Save to custom folder without prompts:
     hunter https://example.com -d my_docs --force-dir

  5. Extract without AI or clipboard:
     hunter https://example.com --no-enhance --no-copy
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="🎉 Happy hunting! For more information, visit: https://github.com/joenandez/codename_hunter"
    )
    
    # URL argument
    parser.add_argument(
        "url",
        help="🌐 URL of the web page to process"
    )
    
    # Output options group
    output_group = parser.add_argument_group('📥 Output Options')
    output_group.add_argument(
        "-d", "--save-to-disk",
        nargs="?",
        const="hunter_docs",
        metavar="folder",
        help="💾 Save markdown to disk in the specified folder (default: hunter_docs)"
    )
    
    output_group.add_argument(
        "--force-dir",
        action="store_true",
        help="📁 Create output directory without prompting if it doesn't exist"
    )
    
    # Processing options group
    processing_group = parser.add_argument_group('⚙️ Processing Options')
    processing_group.add_argument(
        "--no-enhance",
        action="store_true",
        help="🚫 Disable AI enhancement (faster, but may result in less clean formatting)"
    )
    
    processing_group.add_argument(
        "--no-copy",
        action="store_true",
        help="📋 Disable automatic copying to clipboard"
    )
    
    return parser.parse_args()

async def process_url(url: str, no_enhance: bool, no_copy: bool, console: Console, 
                save_to_disk: Optional[str] = None, force_dir: bool = False) -> None:
    """Process a URL asynchronously.
    
    Args:
        url: URL to process
        no_enhance: Whether to skip AI enhancement
        no_copy: Whether to skip clipboard copy
        console: Rich console for output
        save_to_disk: Optional folder path to save markdown file (None = don't save)
        force_dir: Whether to create directory without prompting
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
                original_content = content  # Store original content
                enhancer = AIEnhancer()
                enhanced_content = await enhancer.enhance_content_async(content)
                
                # Validate enhanced content length
                if len(enhanced_content) < 0.9 * len(original_content):
                    logger.warning("AI enhancement removed too much content, falling back to original")
                    console.print("\n[yellow]⚠️  AI enhancement removed too much content, using original instead[/yellow]")
                    content = original_content
                else:
                    content = enhanced_content
            else:
                logger.warning("Skipping enhancement: No API key available")
        
        # Display the result
        console.print(Markdown(content))
        
        # Handle saving to disk if requested
        if save_to_disk:
            folder_path = Path(save_to_disk)
            if not folder_path.exists():
                if force_dir:
                    logger.info(f"Creating directory: {folder_path}")
                    folder_path.mkdir(parents=True, exist_ok=True)
                else:
                    # Prompt user for folder creation
                    response = input(f"Folder '{save_to_disk}' does not exist. Create now? (Y/n): ").strip().lower()
                    if response in ('', 'y', 'yes'):
                        logger.info(f"Creating directory: {folder_path}")
                        folder_path.mkdir(parents=True, exist_ok=True)
                    else:
                        logger.info("Skipping file save, copying to clipboard only")
                        if not no_copy:
                            pyperclip.copy(content)
                            console.print("\n[green]✓[/green] Content has been copied to clipboard!")
                        return

            # Generate filename from URL
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            base_name = parsed_url.netloc + parsed_url.path.replace('/', '-')
            if base_name.endswith('-'):
                base_name = base_name[:-1]
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"{base_name}-{timestamp}.md"
            file_path = folder_path / filename

            # Add source link at the top
            content_with_source = f"[Source: {url}]({url})\n\n{content}"
            
            # Save the file
            logger.info(f"Saving content to: {file_path}")
            file_path.write_text(content_with_source)
            console.print(f"\n[green]✓[/green] Content saved to: {file_path}")
        
        # Copy to clipboard by default unless disabled
        if not no_copy and not save_to_disk:
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
        
        await process_url(
            args.url, 
            args.no_enhance, 
            args.no_copy, 
            console,
            args.save_to_disk,
            args.force_dir
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        console = Console()
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)

def main() -> None:
    """Main entry point for the application."""
    asyncio.run(main_async())
