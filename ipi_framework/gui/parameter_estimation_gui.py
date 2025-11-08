"""
Main parameter estimation experiment control interface.

Provides unified GUI for all three parameter estimation tasks (detection,
heartbeat detection, and dual-modality oddball).
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import logging
import threading

from ..experimental.behavioral_tasks import DetectionTask, HeartbeatDetectionTask, DualModalityOddballTask
from ..data.parameter_estimation_dao import ParameterEstimationDAO
from ..data.parameter_estimation_models import SessionData, TaskType
from .session_management import SessionSetupManager, ParticipantManager
from .progress_monitoring import RealTimeProgressMonitor
from .task_configuration import TaskParameterConfigurator

logger = logging.getLogger(__name__)


class ParameterEstimationGUI:
    """
    Main GUI for parameter estimation experiments.
    
    Provides unified interface for running all three tasks with real-time
    monitoring, session management, and task configuration.
    """
    
    def __init__(self, db_path: Path, title: str = "IPI Parameter Estimation System"):
        """
        Initialize parameter estimation GUI.
        
        Args:
            db_path: Path to database for data storage
            title: Window title
        """
        self.db_path = db_path
        self.dao = ParameterEstimationDAO(db_path)
        
        # Create main window
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("1400x900")
        
        # Session management
        self.session_manager = SessionSetupManager(self.dao)
        self.participant_manager = ParticipantManager(self.dao)
        
        # Task configuration
        self.task_configurator = TaskParameterConfigurator()
        
        # Progress monitoring
        self.progress_monitor = RealTimeProgressMonitor()
        
        # Current session and tasks
        self.current_session: Optional[SessionData] = None
        self.detection_task: Optional[DetectionTask] = None
        self.heartbeat_task: Optional[HeartbeatDetectionTask] = None
        self.oddball_task: Optional[DualModalityOddballTask] = None
        
        # Task execution state
        self.task_running = False
        self.task_thread: Optional[threading.Thread] = None
        
        # Build UI
        self._build_ui()
        
        logger.info("ParameterEstimationGUI initialized")
    
    def _build_ui(self) -> None:
        """Build the main user interface."""
        # Create menu bar
        self._create_menu_bar()
        
        # Create main layout with notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_session_tab()
        self._create_detection_task_tab()
        self._create_heartbeat_task_tab()
        self._create_oddball_task_tab()
        self._create_monitoring_tab()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_menu_bar(self) -> None:
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Session", command=self._new_session)
        file_menu.add_command(label="Load Session", command=self._load_session)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        # Tasks menu
        tasks_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tasks", menu=tasks_menu)
        tasks_menu.add_command(label="Run Detection Task", command=self._run_detection_task)
        tasks_menu.add_command(label="Run Heartbeat Task", command=self._run_heartbeat_task)
        tasks_menu.add_command(label="Run Oddball Task", command=self._run_oddball_task)
        tasks_menu.add_separator()
        tasks_menu.add_command(label="Run All Tasks", command=self._run_all_tasks)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_session_tab(self) -> None:
        """Create session setup and management tab."""
        session_frame = ttk.Frame(self.notebook)
        self.notebook.add(session_frame, text="Session Setup")
        
        # Participant information
        participant_frame = ttk.LabelFrame(session_frame, text="Participant Information", padding=10)
        participant_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(participant_frame, text="Participant ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.participant_id_var = tk.StringVar()
        ttk.Entry(participant_frame, textvariable=self.participant_id_var, width=30).grid(row=0, column=1, pady=2)
        
        ttk.Label(participant_frame, text="Researcher:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.researcher_var = tk.StringVar()
        ttk.Entry(participant_frame, textvariable=self.researcher_var, width=30).grid(row=1, column=1, pady=2)
        
        # Session configuration
        config_frame = ttk.LabelFrame(session_frame, text="Session Configuration", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(config_frame, text="Protocol Version:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.protocol_version_var = tk.StringVar(value="1.0.0")
        ttk.Entry(config_frame, textvariable=self.protocol_version_var, width=20).grid(row=0, column=1, pady=2)
        
        # Session controls
        control_frame = ttk.Frame(session_frame, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Start New Session", command=self._start_new_session).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="End Session", command=self._end_session).pack(side=tk.LEFT, padx=5)
        
        # Session status
        status_frame = ttk.LabelFrame(session_frame, text="Session Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.session_status_text = scrolledtext.ScrolledText(status_frame, height=15, state=tk.DISABLED)
        self.session_status_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_detection_task_tab(self) -> None:
        """Create detection task configuration tab."""
        task_frame = ttk.Frame(self.notebook)
        self.notebook.add(task_frame, text="Detection Task")
        
        # Task parameters
        params_frame = ttk.LabelFrame(task_frame, text="Task Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Modality:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.detection_modality_var = tk.StringVar(value="visual")
        ttk.Combobox(params_frame, textvariable=self.detection_modality_var, 
                    values=["visual", "auditory"], state="readonly", width=20).grid(row=0, column=1, pady=2)
        
        ttk.Label(params_frame, text="Number of Trials:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.detection_trials_var = tk.IntVar(value=200)
        ttk.Spinbox(params_frame, from_=50, to=500, textvariable=self.detection_trials_var, width=20).grid(row=1, column=1, pady=2)
        
        # Task controls
        control_frame = ttk.Frame(task_frame, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Run Task", command=self._run_detection_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop Task", command=self._stop_current_task).pack(side=tk.LEFT, padx=5)
    
    def _create_heartbeat_task_tab(self) -> None:
        """Create heartbeat detection task configuration tab."""
        task_frame = ttk.Frame(self.notebook)
        self.notebook.add(task_frame, text="Heartbeat Task")
        
        # Task parameters
        params_frame = ttk.LabelFrame(task_frame, text="Task Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Number of Trials:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.heartbeat_trials_var = tk.IntVar(value=60)
        ttk.Spinbox(params_frame, from_=30, to=120, textvariable=self.heartbeat_trials_var, width=20).grid(row=0, column=1, pady=2)
        
        # Task controls
        control_frame = ttk.Frame(task_frame, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Run Task", command=self._run_heartbeat_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop Task", command=self._stop_current_task).pack(side=tk.LEFT, padx=5)
    
    def _create_oddball_task_tab(self) -> None:
        """Create oddball task configuration tab."""
        task_frame = ttk.Frame(self.notebook)
        self.notebook.add(task_frame, text="Oddball Task")
        
        # Task parameters
        params_frame = ttk.LabelFrame(task_frame, text="Task Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Number of Trials:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.oddball_trials_var = tk.IntVar(value=120)
        ttk.Spinbox(params_frame, from_=60, to=240, textvariable=self.oddball_trials_var, width=20).grid(row=0, column=1, pady=2)
        
        ttk.Label(params_frame, text="Deviant Probability:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.oddball_deviant_prob_var = tk.DoubleVar(value=0.2)
        ttk.Spinbox(params_frame, from_=0.1, to=0.5, increment=0.05, 
                   textvariable=self.oddball_deviant_prob_var, width=20).grid(row=1, column=1, pady=2)
        
        # Task controls
        control_frame = ttk.Frame(task_frame, padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Run Task", command=self._run_oddball_task).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Stop Task", command=self._stop_current_task).pack(side=tk.LEFT, padx=5)
    
    def _create_monitoring_tab(self) -> None:
        """Create real-time monitoring tab."""
        monitor_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitor_frame, text="Monitoring")
        
        # Progress display
        progress_frame = ttk.LabelFrame(monitor_frame, text="Task Progress", padding=10)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="No task running")
        self.progress_label.pack(pady=5)
        
        # Data quality display
        quality_frame = ttk.LabelFrame(monitor_frame, text="Data Quality", padding=10)
        quality_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.quality_text = scrolledtext.ScrolledText(quality_frame, height=20, state=tk.DISABLED)
        self.quality_text.pack(fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self) -> None:
        """Create status bar at bottom of window."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.time_label = ttk.Label(status_frame, text="", relief=tk.SUNKEN)
        self.time_label.pack(side=tk.RIGHT)
        
        self._update_time()
    
    def _update_time(self) -> None:
        """Update time display in status bar."""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)
    
    def _new_session(self) -> None:
        """Create new session."""
        self._start_new_session()
    
    def _load_session(self) -> None:
        """Load existing session."""
        # TODO: Implement session loading dialog
        messagebox.showinfo("Load Session", "Session loading not yet implemented")
    
    def _start_new_session(self) -> None:
        """Start a new parameter estimation session."""
        participant_id = self.participant_id_var.get().strip()
        researcher = self.researcher_var.get().strip()
        
        if not participant_id:
            messagebox.showerror("Error", "Please enter a participant ID")
            return
        
        try:
            # Create new session
            self.current_session = self.session_manager.create_session(
                participant_id=participant_id,
                researcher=researcher,
                protocol_version=self.protocol_version_var.get()
            )
            
            self._update_session_status(f"Session started: {self.current_session.session_id}")
            self._update_status(f"Session active for participant {participant_id}")
            
            logger.info(f"Started new session: {self.current_session.session_id}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start session: {str(e)}")
            logger.error(f"Failed to start session: {e}")
    
    def _end_session(self) -> None:
        """End current session."""
        if not self.current_session:
            messagebox.showwarning("Warning", "No active session")
            return
        
        if self.task_running:
            messagebox.showwarning("Warning", "Cannot end session while task is running")
            return
        
        try:
            # Update session status
            self.current_session.completion_status = "completed"
            self.current_session.total_duration_minutes = (
                (datetime.now() - self.current_session.session_date).total_seconds() / 60
            )
            
            # Save session
            self.dao.update_session(self.current_session)
            
            self._update_session_status(f"Session ended: {self.current_session.session_id}")
            self._update_status("Session ended")
            
            self.current_session = None
            
            logger.info("Session ended")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to end session: {str(e)}")
            logger.error(f"Failed to end session: {e}")
    
    def _run_detection_task(self) -> None:
        """Run detection task."""
        if not self.current_session:
            messagebox.showerror("Error", "Please start a session first")
            return
        
        if self.task_running:
            messagebox.showwarning("Warning", "A task is already running")
            return
        
        try:
            # Create detection task
            self.detection_task = DetectionTask(
                task_id=f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                modality=self.detection_modality_var.get(),
                n_trials=self.detection_trials_var.get(),
                participant_id=self.current_session.participant_id,
                session_id=self.current_session.session_id,
                dao=self.dao
            )
            
            # Initialize task
            if not self.detection_task.initialize():
                messagebox.showerror("Error", "Failed to initialize detection task")
                return
            
            # Run task in separate thread
            self.task_running = True
            self.task_thread = threading.Thread(target=self._execute_detection_task)
            self.task_thread.start()
            
            self._update_status("Running detection task...")
            self.notebook.select(4)  # Switch to monitoring tab
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start detection task: {str(e)}")
            logger.error(f"Failed to start detection task: {e}")
    
    def _execute_detection_task(self) -> None:
        """Execute detection task (runs in separate thread)."""
        try:
            success = self.detection_task.run()
            
            if success:
                self.root.after(0, lambda: self._task_completed("Detection task completed successfully"))
            else:
                self.root.after(0, lambda: self._task_failed("Detection task failed"))
                
        except Exception as e:
            self.root.after(0, lambda: self._task_failed(f"Detection task error: {str(e)}"))
            logger.error(f"Detection task error: {e}")
        finally:
            self.task_running = False
    
    def _run_heartbeat_task(self) -> None:
        """Run heartbeat detection task."""
        if not self.current_session:
            messagebox.showerror("Error", "Please start a session first")
            return
        
        if self.task_running:
            messagebox.showwarning("Warning", "A task is already running")
            return
        
        try:
            # Create heartbeat task
            self.heartbeat_task = HeartbeatDetectionTask(
                task_id=f"heartbeat_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                n_trials=self.heartbeat_trials_var.get(),
                participant_id=self.current_session.participant_id,
                session_id=self.current_session.session_id,
                dao=self.dao
            )
            
            # Initialize task
            if not self.heartbeat_task.initialize():
                messagebox.showerror("Error", "Failed to initialize heartbeat task")
                return
            
            # Run task in separate thread
            self.task_running = True
            self.task_thread = threading.Thread(target=self._execute_heartbeat_task)
            self.task_thread.start()
            
            self._update_status("Running heartbeat detection task...")
            self.notebook.select(4)  # Switch to monitoring tab
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start heartbeat task: {str(e)}")
            logger.error(f"Failed to start heartbeat task: {e}")
    
    def _execute_heartbeat_task(self) -> None:
        """Execute heartbeat task (runs in separate thread)."""
        try:
            success = self.heartbeat_task.run()
            
            if success:
                self.root.after(0, lambda: self._task_completed("Heartbeat task completed successfully"))
            else:
                self.root.after(0, lambda: self._task_failed("Heartbeat task failed"))
                
        except Exception as e:
            self.root.after(0, lambda: self._task_failed(f"Heartbeat task error: {str(e)}"))
            logger.error(f"Heartbeat task error: {e}")
        finally:
            self.task_running = False
    
    def _run_oddball_task(self) -> None:
        """Run oddball task."""
        if not self.current_session:
            messagebox.showerror("Error", "Please start a session first")
            return
        
        if self.task_running:
            messagebox.showwarning("Warning", "A task is already running")
            return
        
        try:
            # Create oddball task
            self.oddball_task = DualModalityOddballTask(
                task_id=f"oddball_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                n_trials=self.oddball_trials_var.get(),
                deviant_probability=self.oddball_deviant_prob_var.get(),
                participant_id=self.current_session.participant_id,
                session_id=self.current_session.session_id,
                dao=self.dao
            )
            
            # Initialize task
            if not self.oddball_task.initialize():
                messagebox.showerror("Error", "Failed to initialize oddball task")
                return
            
            # Run task in separate thread
            self.task_running = True
            self.task_thread = threading.Thread(target=self._execute_oddball_task)
            self.task_thread.start()
            
            self._update_status("Running oddball task...")
            self.notebook.select(4)  # Switch to monitoring tab
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start oddball task: {str(e)}")
            logger.error(f"Failed to start oddball task: {e}")
    
    def _execute_oddball_task(self) -> None:
        """Execute oddball task (runs in separate thread)."""
        try:
            success = self.oddball_task.run()
            
            if success:
                self.root.after(0, lambda: self._task_completed("Oddball task completed successfully"))
            else:
                self.root.after(0, lambda: self._task_failed("Oddball task failed"))
                
        except Exception as e:
            self.root.after(0, lambda: self._task_failed(f"Oddball task error: {str(e)}"))
            logger.error(f"Oddball task error: {e}")
        finally:
            self.task_running = False
    
    def _run_all_tasks(self) -> None:
        """Run all three tasks sequentially."""
        if not self.current_session:
            messagebox.showerror("Error", "Please start a session first")
            return
        
        if self.task_running:
            messagebox.showwarning("Warning", "A task is already running")
            return
        
        # TODO: Implement sequential task execution
        messagebox.showinfo("Run All Tasks", "Sequential task execution not yet implemented")
    
    def _stop_current_task(self) -> None:
        """Stop currently running task."""
        if not self.task_running:
            messagebox.showinfo("Info", "No task is currently running")
            return
        
        # TODO: Implement graceful task stopping
        messagebox.showinfo("Stop Task", "Task stopping not yet implemented")
    
    def _task_completed(self, message: str) -> None:
        """Handle task completion."""
        self._update_status(message)
        self._update_quality_display(message)
        messagebox.showinfo("Task Complete", message)
    
    def _task_failed(self, message: str) -> None:
        """Handle task failure."""
        self._update_status(message)
        self._update_quality_display(message)
        messagebox.showerror("Task Failed", message)
    
    def _update_session_status(self, message: str) -> None:
        """Update session status display."""
        self.session_status_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.session_status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.session_status_text.see(tk.END)
        self.session_status_text.config(state=tk.DISABLED)
    
    def _update_status(self, message: str) -> None:
        """Update status bar."""
        self.status_label.config(text=message)
        logger.info(message)
    
    def _update_quality_display(self, message: str) -> None:
        """Update data quality display."""
        self.quality_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.quality_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.quality_text.see(tk.END)
        self.quality_text.config(state=tk.DISABLED)
    
    def _show_about(self) -> None:
        """Show about dialog."""
        about_text = """IPI Parameter Estimation System
        
Version 1.0.0

A comprehensive system for estimating IPI framework parameters
through behavioral tasks and neural measurements.

© 2024 IPI Research Team"""
        
        messagebox.showinfo("About", about_text)
    
    def _on_closing(self) -> None:
        """Handle window closing."""
        if self.task_running:
            if not messagebox.askokcancel("Quit", "A task is running. Are you sure you want to quit?"):
                return
        
        if self.current_session and self.current_session.completion_status == "in_progress":
            if messagebox.askyesno("End Session", "End current session before closing?"):
                self._end_session()
        
        self.root.destroy()
    
    def run(self) -> None:
        """Run the GUI application."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()


def launch_gui(db_path: Path) -> None:
    """
    Launch the parameter estimation GUI.
    
    Args:
        db_path: Path to database file
    """
    gui = ParameterEstimationGUI(db_path)
    gui.run()
