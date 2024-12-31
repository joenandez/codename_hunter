"""Tests for main module functionality."""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path
from hunter.main import main, process_url, parse_args
from rich.console import Console
import runpy

def test_parse_args_defaults():
    """Test argument parsing with default values."""
    with patch('sys.argv', ['hunter', 'https://example.com']):
        args = parse_args()
        assert args.url == 'https://example.com'
        assert not args.no_enhance
        assert not args.no_copy
        assert args.save_to_disk is None
        assert not args.force_dir

def test_parse_args_save_to_disk_default():
    """Test -d argument with default folder name."""
    with patch('sys.argv', ['hunter', 'https://example.com', '-d']):
        args = parse_args()
        assert args.save_to_disk == 'hunter_docs'
        assert not args.force_dir

def test_parse_args_save_to_disk_custom():
    """Test -d argument with custom folder name."""
    with patch('sys.argv', ['hunter', 'https://example.com', '-d', 'custom_docs']):
        args = parse_args()
        assert args.save_to_disk == 'custom_docs'
        assert not args.force_dir

def test_parse_args_force_dir():
    """Test --force-dir argument."""
    with patch('sys.argv', ['hunter', 'https://example.com', '-d', '--force-dir']):
        args = parse_args()
        assert args.save_to_disk == 'hunter_docs'
        assert args.force_dir

def test_parse_args_all_options():
    """Test all CLI arguments together."""
    with patch('sys.argv', [
        'hunter',
        'https://example.com',
        '--no-enhance',
        '--no-copy',
        '-d', 'custom_docs',
        '--force-dir'
    ]):
        args = parse_args()
        assert args.url == 'https://example.com'
        assert args.no_enhance
        assert args.no_copy
        assert args.save_to_disk == 'custom_docs'
        assert args.force_dir

def test_main_runs():
    """Test that main function runs without errors."""
    with patch('sys.argv', ['hunter', 'https://example.com']), \
         patch('hunter.main.process_url', new_callable=AsyncMock) as mock_process:
        mock_process.return_value = None
        
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

def test_module_execution():
    """Test that the module can be executed directly."""
    with patch('hunter.main.main') as mock_main:
        runpy.run_module('hunter.__main__', run_name='__main__')
        mock_main.assert_called_once()

@pytest.mark.asyncio
async def test_process_url_save_to_disk_force():
    """Test saving to disk with force_dir=True."""
    mock_console = MagicMock(spec=Console)
    mock_path = MagicMock(spec=Path)
    mock_file_path = MagicMock(spec=Path)
    mock_path.exists.return_value = False
    mock_path.__truediv__.return_value = mock_file_path
    
    with patch('hunter.main.Path', return_value=mock_path), \
         patch('hunter.main.ContentExtractor') as MockExtractor, \
         patch('hunter.parsers.fetch_url_async') as mock_fetch:
        
        # Setup mocks
        mock_extractor = MockExtractor.return_value
        mock_extractor.extract_from_url = AsyncMock(return_value=[MagicMock(content="Test content")])
        mock_fetch.return_value = "<html>Test content</html>"
        
        # Test with force_dir=True
        await process_url(
            url="https://example.com",
            no_enhance=True,
            no_copy=True,
            console=mock_console,
            save_to_disk="test_dir",
            force_dir=True
        )
        
        # Verify directory was created without prompt
        mock_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file_path.write_text.assert_called_once()
        assert "[Source: https://example.com]" in mock_file_path.write_text.call_args[0][0]

@pytest.mark.asyncio
async def test_process_url_save_to_disk_prompt_yes():
    """Test saving to disk with user prompt (answering yes)."""
    mock_console = MagicMock(spec=Console)
    mock_path = MagicMock(spec=Path)
    mock_file_path = MagicMock(spec=Path)
    mock_path.exists.return_value = False
    mock_path.__truediv__.return_value = mock_file_path
    
    with patch('hunter.main.Path', return_value=mock_path), \
         patch('hunter.main.ContentExtractor') as MockExtractor, \
         patch('hunter.parsers.fetch_url_async') as mock_fetch, \
         patch('builtins.input', return_value='y'):
        
        # Setup mocks
        mock_extractor = MockExtractor.return_value
        mock_extractor.extract_from_url = AsyncMock(return_value=[MagicMock(content="Test content")])
        mock_fetch.return_value = "<html>Test content</html>"
        
        # Test with force_dir=False
        await process_url(
            url="https://example.com",
            no_enhance=True,
            no_copy=True,
            console=mock_console,
            save_to_disk="test_dir",
            force_dir=False
        )
        
        # Verify directory was created after prompt
        mock_path.mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file_path.write_text.assert_called_once()

@pytest.mark.asyncio
async def test_process_url_save_to_disk_prompt_no():
    """Test saving to disk with user prompt (answering no)."""
    mock_console = MagicMock(spec=Console)
    mock_path = MagicMock(spec=Path)
    mock_file_path = MagicMock(spec=Path)
    mock_path.exists.return_value = False
    mock_path.__truediv__.return_value = mock_file_path
    
    with patch('hunter.main.Path', return_value=mock_path), \
         patch('hunter.main.ContentExtractor') as MockExtractor, \
         patch('hunter.parsers.fetch_url_async') as mock_fetch, \
         patch('builtins.input', return_value='n'), \
         patch('pyperclip.copy') as mock_copy:
        
        # Setup mocks
        mock_extractor = MockExtractor.return_value
        mock_extractor.extract_from_url = AsyncMock(return_value=[MagicMock(content="Test content")])
        mock_fetch.return_value = "<html>Test content</html>"
        
        # Test with force_dir=False
        await process_url(
            url="https://example.com",
            no_enhance=True,
            no_copy=False,  # Allow clipboard copy
            console=mock_console,
            save_to_disk="test_dir",
            force_dir=False
        )
        
        # Verify directory was not created and content was copied to clipboard
        mock_path.mkdir.assert_not_called()
        mock_file_path.write_text.assert_not_called()
        mock_copy.assert_called_once_with("Test content")

@pytest.mark.asyncio
async def test_process_url_save_to_disk_existing_dir():
    """Test saving to disk with existing directory."""
    mock_console = MagicMock(spec=Console)
    mock_path = MagicMock(spec=Path)
    mock_file_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.__truediv__.return_value = mock_file_path
    
    with patch('hunter.main.Path', return_value=mock_path), \
         patch('hunter.main.ContentExtractor') as MockExtractor, \
         patch('hunter.parsers.fetch_url_async') as mock_fetch:
        
        # Setup mocks
        mock_extractor = MockExtractor.return_value
        mock_extractor.extract_from_url = AsyncMock(return_value=[MagicMock(content="Test content")])
        mock_fetch.return_value = "<html>Test content</html>"
        
        # Test with existing directory
        await process_url(
            url="https://example.com",
            no_enhance=True,
            no_copy=True,
            console=mock_console,
            save_to_disk="test_dir",
            force_dir=False
        )
        
        # Verify no directory creation was attempted
        mock_path.mkdir.assert_not_called()
        mock_file_path.write_text.assert_called_once()
        assert "[Source: https://example.com]" in mock_file_path.write_text.call_args[0][0]
