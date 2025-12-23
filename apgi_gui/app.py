"""Main application module for APGI Framework GUI."""

import os
import json
import logging
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional, List
import customtkinter as ctk
from datetime import datetime

# Import custom components
from .components.sidebar import Sidebar
from .components.main_area import MainArea
from .components.status_bar import StatusBar
from .utils.logger import setup_logging
from .utils.config import AppConfig

class APGIFrameworkApp(ctk.CTk):
    """Main application class for APGI Framework GUI."""
    
    def __init__(self):
        """Initialize the application."""
        super().__init__()
        
        # Initialize application state
        self.title("APGI Framework GUI")
        self.geometry("1800x1000+50+50")
        self.minsize(1200, 800)
        
        # Initialize configuration
        self.config = AppConfig()
        
        # Set appearance
        ctk.set_appearance_mode(self.config.theme)
        ctk.set_default_color_theme("blue")
        
        # Initialize application data
        self.current_file: Optional[Path] = None
        self.undo_stack: List[Dict[str, Any]] = []
        self.redo_stack: List[Dict[str, Any]] = []
        self.recent_files: List[Path] = []
        
        # Setup logging
        self.logger = setup_logging("apgi_gui", self.config.log_dir)
        self.logger.info("APGI Framework GUI started")
        
        # Setup UI
        self._setup_ui()
        self._setup_keyboard_shortcuts()
        
        # Load recent files
        self._load_recent_files()
        
        # Center window on screen
        self._center_window()
    
    def _setup_ui(self) -> None:
        """Set up the main user interface."""
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create main containers
        self.sidebar = Sidebar(self, self)
        self.main_area = MainArea(self, self)
        self.status_bar = StatusBar(self, self)
        
        # Layout
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.status_bar.grid(row=1, column=1, sticky="ew")
    
    def _setup_keyboard_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        self.bind("<Control-n>", lambda e: self.new_file())
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-S>", lambda e: self.save_file_as())
        self.bind("<Control-q>", lambda e: self.quit())
        self.bind("<Control-z>", lambda e: self.undo())
        self.bind("<Control-y>", lambda e: self.redo())
        self.bind("<F1>", lambda e: self.show_help())
        self.bind("<Control-h>", lambda e: self.show_help())
        self.bind("<Control-t>", lambda e: self.toggle_theme())
    
    def _center_window(self) -> None:
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _load_recent_files(self) -> None:
        """Load the list of recently opened files."""
        try:
            if self.config.recent_files_path.exists():
                with open(self.config.recent_files_path, 'r') as f:
                    recent_files = json.load(f)
                    self.recent_files = [Path(f) for f in recent_files if Path(f).exists()]
        except Exception as e:
            self.logger.error(f"Error loading recent files: {e}")
    
    def _save_recent_files(self) -> None:
        """Save the list of recently opened files."""
        try:
            with open(self.config.recent_files_path, 'w') as f:
                json.dump([str(f) for f in self.recent_files], f)
        except Exception as e:
            self.logger.error(f"Error saving recent files: {e}")
    
    def update_status(self, message: str, level: str = "info") -> None:
        """Update the status bar with a message.
        
        Args:
            message: The message to display
            level: The message level (info, warning, error)
        """
        self.status_bar.set_status(message, level)
        
        # Log the message
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(message)
    
    def new_file(self) -> None:
        """Create a new file."""
        self.current_file = None
        self.main_area.clear()
        self.update_status("New file created")
    
    def open_file(self, file_path: Optional[Path] = None) -> None:
        """Open a file.
        
        Args:
            file_path: Path to the file to open. If None, shows a file dialog.
        """
        if file_path is None:
            file_path = tk.filedialog.askopenfilename(
                title="Open APGI Configuration",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                initialdir=self.config.data_dir
            )
            if not file_path:
                return
            file_path = Path(file_path)
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.current_file = file_path
            self.main_area.load_data(data)
            
            # Add to recent files
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:10]  # Keep only 10 most recent
            self._save_recent_files()
            
            self.update_status(f"Opened {file_path.name}")
            
        except Exception as e:
            self.update_status(f"Error opening file: {e}", "error")
    
    def save_file(self) -> None:
        """Save the current file."""
        if self.current_file is None:
            self.save_file_as()
        else:
            self._save_to_file(self.current_file)
    
    def save_file_as(self) -> None:
        """Save the current file with a new name."""
        file_path = tk.filedialog.asksaveasfilename(
            title="Save APGI Configuration",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir=self.config.data_dir
        )
        
        if not file_path:
            return
        
        file_path = Path(file_path)
        self._save_to_file(file_path)
        self.current_file = file_path
    
    def _save_to_file(self, file_path: Path) -> None:
        """Save data to a file.
        
        Args:
            file_path: Path to save the file to
        """
        try:
            data = self.main_area.get_data()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            self.update_status(f"Saved to {file_path.name}")
            
            # Add to recent files if not already there
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
            self.recent_files.insert(0, file_path)
            self.recent_files = self.recent_files[:10]  # Keep only 10 most recent
            self._save_recent_files()
            
        except Exception as e:
            self.update_status(f"Error saving file: {e}", "error")
    
    def undo(self) -> None:
        """Undo the last action."""
        if self.undo_stack:
            self.redo_stack.append(self.main_area.get_data())
            self.main_area.load_data(self.undo_stack.pop())
            self.update_status("Undo successful")
        else:
            self.update_status("Nothing to undo", "warning")
    
    def redo(self) -> None:
        """Redo the last undone action."""
        if self.redo_stack:
            self.undo_stack.append(self.main_area.get_data())
            self.main_area.load_data(self.redo_stack.pop())
            self.update_status("Redo successful")
        else:
            self.update_status("Nothing to redo", "warning")
    
    def toggle_theme(self) -> None:
        """Toggle between light and dark themes."""
        if self.config.theme == "dark":
            self.config.theme = "light"
            ctk.set_appearance_mode("light")
            self.update_status("Switched to light theme")
        else:
            self.config.theme = "dark"
            ctk.set_appearance_mode("dark")
            self.update_status("Switched to dark theme")
        
        # Save the theme preference
        self.config.save()
    
    def show_help(self) -> None:
        """Show the help dialog."""
        help_text = """APGI Framework GUI Help

Keyboard Shortcuts:
  Ctrl+N       - New file
  Ctrl+O       - Open file
  Ctrl+S       - Save file
  Ctrl+Shift+S - Save file as
  Ctrl+Z       - Undo
  Ctrl+Y       - Redo
  Ctrl+T       - Toggle theme
  F1 or Ctrl+H - Show this help

For more information, please refer to the documentation.
"""
        tk.messagebox.showinfo("APGI Framework Help", help_text)
    
    def run(self) -> None:
        """Run the application."""
        self.mainloop()


def main():
    """Main entry point for the application."""
    try:
        app = APGIFrameworkApp()
        app.run()
    except Exception as e:
        logging.error("Fatal error in application", exc_info=True)
        tk.messagebox.showerror("Fatal Error", f"A fatal error occurred: {e}\n\nCheck the logs for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
