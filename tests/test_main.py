"""Tests for main module functionality."""
import pytest
from unittest.mock import patch
from hunter.main import main
import runpy

def test_main_runs():
    """Test that main function runs without errors."""
    with patch('sys.argv', ['hunter', 'https://example.com']):
        try:
            main()
        except SystemExit as e:
            assert e.code == 0

def test_module_execution():
    """Test that the module can be executed directly."""
    with patch('hunter.main.main') as mock_main:
        runpy.run_module('hunter.__main__', run_name='__main__')
        mock_main.assert_called_once()
