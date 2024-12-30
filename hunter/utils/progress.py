"""Progress tracking utilities.

This module provides utilities for tracking progress of long-running operations
using Rich for beautiful console output.
"""

from typing import Optional, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# Moon phase emojis for the spinner
MOON_PHASES = ["🌑", "🌘", "🌗", "🌖", "🌕", "🌔", "🌓", "🌒", "🌑"]

console = Console()

class ProgressManager:
    """Manages progress indicators for long-running operations.
    
    This class provides a context manager for showing progress indicators
    during long-running operations. It uses Rich for beautiful console output
    with a custom moon phase spinner.
    
    Example:
        >>> with ProgressManager() as progress:
        ...     progress.update("Step 1...")
        ...     do_step_1()
        ...     progress.update("Step 2...")
        ...     do_step_2()
    """
    
    def __init__(self):
        """Initialize the progress manager with a Rich progress bar."""
        self.progress = Progress(
            TextColumn("{task.fields[spinner]}", justify="right"),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        )
        self._frame = 0
    
    def __enter__(self) -> Progress:
        """Start the progress display.
        
        Returns:
            Progress: The progress object for updating status
        """
        self.progress.start()
        return self
    
    def __exit__(self, exc_type: Optional[type], 
                 exc_val: Optional[Exception], 
                 exc_tb: Optional[Any]) -> None:
        """Clean up the progress display.
        
        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.progress.stop()
        
    async def __aenter__(self) -> Progress:
        """Start the progress display asynchronously.
        
        Returns:
            Progress: The progress object for updating status
        """
        self.progress.start()
        return self
    
    async def __aexit__(self, exc_type: Optional[type], 
                      exc_val: Optional[Exception], 
                      exc_tb: Optional[Any]) -> None:
        """Clean up the progress display asynchronously.
        
        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.progress.stop()
    
    def add_task(self, description: str, total: Optional[float] = None) -> int:
        """Add a new task with the moon phase spinner.
        
        Args:
            description: Task description to display
            total: Optional total steps (None for indefinite)
            
        Returns:
            int: Task ID
        """
        return self.progress.add_task(description, total=total, spinner=MOON_PHASES[0])
    
    def advance(self, task_id: int) -> None:
        """Advance the moon phase spinner.
        
        Args:
            task_id: The ID of the task to update
        """
        self._frame = (self._frame + 1) % len(MOON_PHASES)
        self.progress.update(task_id, spinner=MOON_PHASES[self._frame])
    
    def remove_task(self, task_id: int) -> None:
        """Remove a task from the progress display.
        
        Args:
            task_id: The ID of the task to remove
        """
        self.progress.remove_task(task_id) 