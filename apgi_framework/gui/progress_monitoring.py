"""
Real-time progress monitoring for parameter estimation tasks.

Provides classes for tracking task completion and data quality during experiments.
"""

from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RealTimeProgressMonitor:
    """
    Monitors task progress and data quality in real-time.
    
    Tracks trial completion, timing, and provides progress updates.
    """
    
    def __init__(self):
        """Initialize progress monitor."""
        self.current_task: Optional[str] = None
        self.total_trials: int = 0
        self.completed_trials: int = 0
        self.start_time: Optional[datetime] = None
        self.estimated_completion: Optional[datetime] = None
        
        # Callbacks for progress updates
        self.progress_callbacks: list[Callable[[Dict[str, Any]], None]] = []
        
        logger.info("RealTimeProgressMonitor initialized")
    
    def start_task(self, task_name: str, total_trials: int) -> None:
        """
        Start monitoring a new task.
        
        Args:
            task_name: Name of the task
            total_trials: Total number of trials
        """
        self.current_task = task_name
        self.total_trials = total_trials
        self.completed_trials = 0
        self.start_time = datetime.now()
        self.estimated_completion = None
        
        logger.info(f"Started monitoring task: {task_name} ({total_trials} trials)")
        self._notify_progress()
    
    def update_progress(self, completed_trials: int) -> None:
        """
        Update progress with number of completed trials.
        
        Args:
            completed_trials: Number of completed trials
        """
        self.completed_trials = completed_trials
        
        # Estimate completion time
        if self.start_time and completed_trials > 0:
            elapsed = datetime.now() - self.start_time
            trials_per_second = completed_trials / elapsed.total_seconds()
            remaining_trials = self.total_trials - completed_trials
            
            if trials_per_second > 0:
                remaining_seconds = remaining_trials / trials_per_second
                self.estimated_completion = datetime.now() + timedelta(seconds=remaining_seconds)
        
        self._notify_progress()
    
    def complete_task(self) -> None:
        """Mark current task as completed."""
        self.completed_trials = self.total_trials
        self._notify_progress()
        
        logger.info(f"Task completed: {self.current_task}")
        self.current_task = None
    
    def add_progress_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add callback for progress updates.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callbacks.append(callback)
    
    def _notify_progress(self) -> None:
        """Notify all registered callbacks of progress update."""
        progress_data = self.get_progress_data()
        
        for callback in self.progress_callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
    
    def get_progress_data(self) -> Dict[str, Any]:
        """
        Get current progress data.
        
        Returns:
            Dictionary with progress information
        """
        progress_percent = 0.0
        if self.total_trials > 0:
            progress_percent = (self.completed_trials / self.total_trials) * 100
        
        elapsed_time = None
        if self.start_time:
            elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        return {
            'task_name': self.current_task,
            'total_trials': self.total_trials,
            'completed_trials': self.completed_trials,
            'progress_percent': progress_percent,
            'elapsed_seconds': elapsed_time,
            'estimated_completion': self.estimated_completion.isoformat() if self.estimated_completion else None
        }
    
    def get_progress_string(self) -> str:
        """
        Get formatted progress string.
        
        Returns:
            Human-readable progress string
        """
        if not self.current_task:
            return "No task running"
        
        progress_data = self.get_progress_data()
        
        progress_str = f"{self.current_task}: {self.completed_trials}/{self.total_trials} trials "
        progress_str += f"({progress_data['progress_percent']:.1f}%)"
        
        if self.estimated_completion:
            progress_str += f" - ETA: {self.estimated_completion.strftime('%H:%M:%S')}"
        
        return progress_str
    
    def reset(self) -> None:
        """Reset progress monitor."""
        self.current_task = None
        self.total_trials = 0
        self.completed_trials = 0
        self.start_time = None
        self.estimated_completion = None
        
        logger.info("Progress monitor reset")
