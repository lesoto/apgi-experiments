"""
Robust error handling and recovery system.

Provides hardware failure handling, session state management, backup systems,
and user guidance for error recovery.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from datetime import datetime
import json
import logging
import traceback

from ..data.parameter_estimation_models import SessionData
from ..data.parameter_estimation_dao import ParameterEstimationDAO
from ..security.secure_pickle import safe_pickle_load, safe_pickle_dump, SecurePickleError

logger = logging.getLogger(__name__)


class HardwareFailureHandler:
    """
    Handles graceful degradation when hardware fails.
    
    Manages EEG, eye tracker, and cardiac sensor failures with fallback strategies.
    """
    
    def __init__(self):
        """Initialize hardware failure handler."""
        self.hardware_status = {
            'eeg': {'available': True, 'last_check': None, 'error': None},
            'eye_tracker': {'available': True, 'last_check': None, 'error': None},
            'cardiac': {'available': True, 'last_check': None, 'error': None}
        }
        
        self.failure_callbacks: Dict[str, List[Callable]] = {
            'eeg': [],
            'eye_tracker': [],
            'cardiac': []
        }
        
        logger.info("HardwareFailureHandler initialized")
    
    def register_failure_callback(self, hardware_type: str, callback: Callable) -> None:
        """
        Register callback for hardware failure.
        
        Args:
            hardware_type: Type of hardware ('eeg', 'eye_tracker', 'cardiac')
            callback: Function to call on failure
        """
        if hardware_type in self.failure_callbacks:
            self.failure_callbacks[hardware_type].append(callback)
    
    def report_hardware_failure(self, hardware_type: str, error: Exception) -> None:
        """
        Report hardware failure and trigger callbacks.
        
        Args:
            hardware_type: Type of hardware that failed
            error: Exception that occurred
        """
        if hardware_type not in self.hardware_status:
            logger.error(f"Unknown hardware type: {hardware_type}")
            return
        
        self.hardware_status[hardware_type]['available'] = False
        self.hardware_status[hardware_type]['last_check'] = datetime.now()
        self.hardware_status[hardware_type]['error'] = str(error)
        
        logger.error(f"{hardware_type} failure: {error}")
        
        # Trigger callbacks
        for callback in self.failure_callbacks.get(hardware_type, []):
            try:
                callback(hardware_type, error)
            except Exception as e:
                logger.error(f"Error in failure callback: {e}")
    
    def check_hardware_status(self, hardware_type: str) -> bool:
        """
        Check if hardware is available.
        
        Args:
            hardware_type: Type of hardware to check
            
        Returns:
            True if hardware is available
        """
        return self.hardware_status.get(hardware_type, {}).get('available', False)
    
    def get_degraded_mode_config(self) -> Dict[str, bool]:
        """
        Get configuration for degraded mode operation.
        
        Returns:
            Dictionary indicating which systems are available
        """
        return {
            'eeg_available': self.hardware_status['eeg']['available'],
            'eye_tracker_available': self.hardware_status['eye_tracker']['available'],
            'cardiac_available': self.hardware_status['cardiac']['available'],
            'behavioral_only': not any(
                self.hardware_status[hw]['available'] 
                for hw in ['eeg', 'eye_tracker', 'cardiac']
            )
        }
    
    def attempt_hardware_recovery(self, hardware_type: str) -> bool:
        """
        Attempt to recover failed hardware.
        
        Args:
            hardware_type: Type of hardware to recover
            
        Returns:
            True if recovery successful
        """
        logger.info(f"Attempting to recover {hardware_type}")
        
        # In a real implementation, this would attempt to reinitialize hardware
        # For now, just log the attempt
        
        return False
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """
        Get summary of hardware failures.
        
        Returns:
            Dictionary with failure information
        """
        failures = []
        
        for hw_type, status in self.hardware_status.items():
            if not status['available']:
                failures.append({
                    'hardware': hw_type,
                    'error': status['error'],
                    'time': status['last_check'].isoformat() if status['last_check'] else None
                })
        
        return {
            'n_failures': len(failures),
            'failures': failures,
            'degraded_mode': len(failures) > 0
        }


class SessionStateManager:
    """
    Manages session state for pause/resume functionality.
    
    Preserves complete session state for interruption recovery.
    """
    
    def __init__(self, state_dir: Path):
        """
        Initialize session state manager.
        
        Args:
            state_dir: Directory for storing state files
        """
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_state: Optional[Dict[str, Any]] = None
        
        logger.info(f"SessionStateManager initialized with state dir: {state_dir}")
    
    def save_state(self, session_id: str, state_data: Dict[str, Any]) -> Path:
        """
        Save session state to disk.
        
        Args:
            session_id: Session identifier
            state_data: State data to save
            
        Returns:
            Path to saved state file
        """
        state_file = self.state_dir / f"{session_id}_state.pkl"
        
        # Add metadata
        state_data['saved_at'] = datetime.now().isoformat()
        state_data['session_id'] = session_id
        
        # Save state
        with open(state_file, 'wb') as f:
            safe_pickle_dump(state_data, f)
        
        self.current_state = state_data
        
        logger.info(f"Saved session state to {state_file}")
        return state_file
    
    def load_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load session state from disk.
        
        Args:
            session_id: Session identifier
            
        Returns:
            State data or None if not found
        """
        state_file = self.state_dir / f"{session_id}_state.pkl"
        
        if not state_file.exists():
            logger.warning(f"State file not found: {state_file}")
            return None
        
        try:
            with open(state_file, 'rb') as f:
                state_data = safe_pickle_load(f)
            
            self.current_state = state_data
            logger.info(f"Loaded session state from {state_file}")
            return state_data
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
            return None
    
    def delete_state(self, session_id: str) -> None:
        """
        Delete saved session state.
        
        Args:
            session_id: Session identifier
        """
        state_file = self.state_dir / f"{session_id}_state.pkl"
        
        if state_file.exists():
            state_file.unlink()
            logger.info(f"Deleted session state: {state_file}")
    
    def list_saved_states(self) -> List[Dict[str, Any]]:
        """
        List all saved session states.
        
        Returns:
            List of state information dictionaries
        """
        states = []
        
        for state_file in self.state_dir.glob("*_state.pkl"):
            try:
                with open(state_file, 'rb') as f:
                    state_data = safe_pickle_load(f)
                
                states.append({
                    'session_id': state_data.get('session_id'),
                    'saved_at': state_data.get('saved_at'),
                    'file_path': str(state_file)
                })
            except Exception as e:
                logger.error(f"Failed to read state file {state_file}: {e}")
        
        return states


class AutomaticBackupSystem:
    """
    Real-time data backup and recovery.
    
    Automatically backs up session data at regular intervals.
    """
    
    def __init__(self, backup_dir: Path, dao: ParameterEstimationDAO):
        """
        Initialize automatic backup system.
        
        Args:
            backup_dir: Directory for storing backups
            dao: Data access object for retrieving data
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.dao = dao
        self.backup_interval_seconds = 300  # 5 minutes
        self.last_backup: Optional[datetime] = None
        
        logger.info(f"AutomaticBackupSystem initialized with backup dir: {backup_dir}")
    
    def create_backup(self, session_id: str) -> Optional[Path]:
        """
        Create backup of session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            session = self.dao.get_session(session_id)
            
            if not session:
                logger.error(f"Session {session_id} not found for backup")
                return None
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"{session_id}_backup_{timestamp}.json"
            
            # Convert session to dictionary
            session_dict = session.to_dict()
            
            # Add backup metadata
            session_dict['backup_metadata'] = {
                'backup_time': datetime.now().isoformat(),
                'backup_version': '1.0'
            }
            
            # Write backup
            with open(backup_file, 'w') as f:
                json.dump(session_dict, f, indent=2)
            
            self.last_backup = datetime.now()
            
            logger.info(f"Created backup: {backup_file}")
            return backup_file
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def restore_from_backup(self, backup_file: Path) -> Optional[SessionData]:
        """
        Restore session from backup file.
        
        Args:
            backup_file: Path to backup file
            
        Returns:
            Restored SessionData or None if failed
        """
        try:
            with open(backup_file, 'r') as f:
                session_dict = json.load(f)
            
            # TODO: Convert dictionary back to SessionData
            session_data = self._dict_to_session_data(session_dict)
            
            logger.info(f"Restored session from backup: {backup_file}")
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return None
    
    def _dict_to_session_data(self, session_dict: Dict[str, Any]) -> SessionData:
        """Convert dictionary back to SessionData object."""
        try:
            # Handle datetime conversion
            session_date = session_dict.get('session_date')
            if isinstance(session_date, str):
                session_date = datetime.fromisoformat(session_date.replace('Z', '+00:00'))
            
            # Convert trial data lists
            detection_trials = []
            for trial_dict in session_dict.get('detection_trials', []):
                # Convert nested datetime objects
                if 'timestamp' in trial_dict and isinstance(trial_dict['timestamp'], str):
                    trial_dict['timestamp'] = datetime.fromisoformat(trial_dict['timestamp'].replace('Z', '+00:00'))
                detection_trials.append(trial_dict)
            
            heartbeat_trials = []
            for trial_dict in session_dict.get('heartbeat_trials', []):
                if 'timestamp' in trial_dict and isinstance(trial_dict['timestamp'], str):
                    trial_dict['timestamp'] = datetime.fromisoformat(trial_dict['timestamp'].replace('Z', '+00:00'))
                heartbeat_trials.append(trial_dict)
            
            oddball_trials = []
            for trial_dict in session_dict.get('oddball_trials', []):
                if 'timestamp' in trial_dict and isinstance(trial_dict['timestamp'], str):
                    trial_dict['timestamp'] = datetime.fromisoformat(trial_dict['timestamp'].replace('Z', '+00:00'))
                oddball_trials.append(trial_dict)
            
            # Create SessionData object
            session_data = SessionData(
                session_id=session_dict.get('session_id', ''),
                participant_id=session_dict.get('participant_id', ''),
                session_date=session_date,
                protocol_version=session_dict.get('protocol_version', '1.0.0'),
                completion_status=session_dict.get('completion_status', 'in_progress'),
                total_duration_minutes=session_dict.get('total_duration_minutes'),
                detection_trials=detection_trials,
                heartbeat_trials=heartbeat_trials,
                oddball_trials=oddball_trials,
                parameter_estimates=session_dict.get('parameter_estimates'),
                session_quality_score=session_dict.get('session_quality_score', 1.0),
                technical_issues=session_dict.get('technical_issues', []),
                researcher=session_dict.get('researcher', ''),
                notes=session_dict.get('notes', '')
            )
            
            return session_data
            
        except Exception as e:
            logger.error(f"Failed to convert dict to SessionData: {e}")
            raise
    
    def list_backups(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List available backups.
        
        Args:
            session_id: Optional session ID to filter by
            
        Returns:
            List of backup information dictionaries
        """
        backups = []
        
        pattern = f"{session_id}_backup_*.json" if session_id else "*_backup_*.json"
        
        for backup_file in self.backup_dir.glob(pattern):
            try:
                backups.append({
                    'file_path': str(backup_file),
                    'file_name': backup_file.name,
                    'created': datetime.fromtimestamp(backup_file.stat().st_mtime),
                    'size_bytes': backup_file.stat().st_size
                })
            except Exception as e:
                logger.error(f"Failed to read backup file {backup_file}: {e}")
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, max_age_days: int = 30, max_backups_per_session: int = 10) -> int:
        """
        Clean up old backup files.
        
        Args:
            max_age_days: Maximum age of backups to keep
            max_backups_per_session: Maximum number of backups per session
            
        Returns:
            Number of backups deleted
        """
        deleted_count = 0
        cutoff_date = datetime.now().timestamp() - (max_age_days * 24 * 3600)
        
        # Group backups by session
        session_backups: Dict[str, List[Path]] = {}
        
        for backup_file in self.backup_dir.glob("*_backup_*.json"):
            # Extract session ID from filename
            session_id = backup_file.name.split('_backup_')[0]
            
            if session_id not in session_backups:
                session_backups[session_id] = []
            
            session_backups[session_id].append(backup_file)
        
        # Clean up old backups
        for session_id, backups in session_backups.items():
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            for i, backup_file in enumerate(backups):
                # Delete if too old or exceeds max count
                if (backup_file.stat().st_mtime < cutoff_date or 
                    i >= max_backups_per_session):
                    try:
                        backup_file.unlink()
                        deleted_count += 1
                        logger.info(f"Deleted old backup: {backup_file}")
                    except Exception as e:
                        logger.error(f"Failed to delete backup {backup_file}: {e}")
        
        return deleted_count


class UserGuidanceSystem:
    """
    Provides clear error messages and recovery instructions.
    
    Displays user-friendly error messages with step-by-step recovery guidance.
    """
    
    def __init__(self, parent_window: Optional[tk.Tk] = None):
        """
        Initialize user guidance system.
        
        Args:
            parent_window: Parent tkinter window for dialogs
        """
        self.parent_window = parent_window
        
        # Error message templates
        self.error_templates = {
            'eeg_failure': {
                'title': 'EEG System Failure',
                'message': 'The EEG system has encountered an error.',
                'steps': [
                    'Check that the EEG amplifier is powered on',
                    'Verify all electrode connections',
                    'Check impedances are below 10 kΩ',
                    'Restart the EEG acquisition software',
                    'If problem persists, continue in behavioral-only mode'
                ]
            },
            'eye_tracker_failure': {
                'title': 'Eye Tracker Failure',
                'message': 'The eye tracking system has encountered an error.',
                'steps': [
                    'Check that the eye tracker is connected via USB',
                    'Verify the participant is positioned correctly',
                    'Run eye tracker calibration',
                    'Check lighting conditions in the room',
                    'If problem persists, continue without pupillometry'
                ]
            },
            'cardiac_failure': {
                'title': 'Cardiac Sensor Failure',
                'message': 'The cardiac monitoring system has encountered an error.',
                'steps': [
                    'Check ECG/PPG sensor connections',
                    'Verify sensor placement on participant',
                    'Check for loose cables',
                    'Try repositioning the sensor',
                    'If problem persists, continue without cardiac monitoring'
                ]
            }
        }
        
        logger.info("UserGuidanceSystem initialized")
    
    def show_error_guidance(self, error_type: str, additional_info: str = "") -> None:
        """
        Show error guidance dialog.
        
        Args:
            error_type: Type of error (key in error_templates)
            additional_info: Additional error information
        """
        if error_type not in self.error_templates:
            self._show_generic_error(error_type, additional_info)
            return
        
        template = self.error_templates[error_type]
        
        # Build message
        message = template['message']
        if additional_info:
            message += f"\n\nDetails: {additional_info}"
        
        message += "\n\nRecovery Steps:"
        for i, step in enumerate(template['steps'], 1):
            message += f"\n{i}. {step}"
        
        # Show dialog
        if self.parent_window:
            messagebox.showerror(template['title'], message, parent=self.parent_window)
        else:
            logger.error(f"{template['title']}: {message}")
    
    def _show_generic_error(self, error_type: str, error_info: str) -> None:
        """Show generic error message."""
        message = f"An error has occurred: {error_type}"
        if error_info:
            message += f"\n\nDetails: {error_info}"
        
        message += "\n\nPlease contact technical support if the problem persists."
        
        if self.parent_window:
            messagebox.showerror("Error", message, parent=self.parent_window)
        else:
            logger.error(message)
    
    def show_recovery_success(self, component: str) -> None:
        """
        Show recovery success message.
        
        Args:
            component: Component that was recovered
        """
        message = f"Successfully recovered {component}.\n\nYou may continue with the experiment."
        
        if self.parent_window:
            messagebox.showinfo("Recovery Successful", message, parent=self.parent_window)
        else:
            logger.info(message)
    
    def show_degraded_mode_warning(self, unavailable_systems: List[str]) -> bool:
        """
        Show warning about degraded mode operation.
        
        Args:
            unavailable_systems: List of unavailable systems
            
        Returns:
            True if user wants to continue in degraded mode
        """
        message = "The following systems are unavailable:\n\n"
        for system in unavailable_systems:
            message += f"• {system}\n"
        
        message += "\nYou can continue in degraded mode with reduced functionality.\n\n"
        message += "Do you want to continue?"
        
        if self.parent_window:
            return messagebox.askyesno("Degraded Mode", message, parent=self.parent_window)
        else:
            logger.warning(message)
            return False
    
    def log_error_with_context(self, error: Exception, context: Dict[str, Any]) -> None:
        """
        Log error with full context information.
        
        Args:
            error: Exception that occurred
            context: Context information dictionary
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.error(f"Error with context: {json.dumps(error_info, indent=2)}")
        
        # Optionally save to error log file
        error_log_dir = Path("error_logs")
        error_log_dir.mkdir(exist_ok=True)
        
        error_log_file = error_log_dir / f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(error_log_file, 'w') as f:
                json.dump(error_info, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")
