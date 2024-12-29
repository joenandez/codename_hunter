"""Tests for main functionality."""
import pytest
from src.main import main

def test_main_runs():
    """Test that main function runs without errors."""
    try:
        main()
    except Exception as e:
        pytest.fail(f"Main function raised an exception: {e}")
