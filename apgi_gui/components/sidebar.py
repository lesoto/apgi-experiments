"""Sidebar component for the APGI Framework GUI."""

import customtkinter as ctk
import tkinter as tk
from pathlib import Path
from typing import Optional, Callable, Any
import json


class Sidebar(ctk.CTkFrame):
    """Sidebar component containing navigation and tools."""
    
    def __init__(self, parent, app):
        """Initialize the sidebar.
        
        Args:
            parent: Parent widget
            app: Main application instance
        """
        super().__init__(parent)
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the sidebar UI components."""
        # Configure frame
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(
            self, 
            text="APGI Framework",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation Section
        nav_frame = ctk.CTkFrame(self)
        nav_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        nav_frame.grid_columnconfigure(0, weight=1)
        
        nav_label = ctk.CTkLabel(
            nav_frame,
            text="Navigation",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        nav_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Navigation buttons
        self.new_btn = ctk.CTkButton(
            nav_frame,
            text="New Configuration",
            command=self.app.new_file,
            height=40
        )
        self.new_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.open_btn = ctk.CTkButton(
            nav_frame,
            text="Open File",
            command=self.app.open_file,
            height=40
        )
        self.open_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.save_btn = ctk.CTkButton(
            nav_frame,
            text="Save File",
            command=self.app.save_file,
            height=40
        )
        self.save_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Tools Section
        tools_frame = ctk.CTkFrame(self)
        tools_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        tools_frame.grid_columnconfigure(0, weight=1)
        
        tools_label = ctk.CTkLabel(
            tools_frame,
            text="Tools",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        tools_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Tool buttons
        self.undo_btn = ctk.CTkButton(
            tools_frame,
            text="Undo",
            command=self.app.undo,
            height=40
        )
        self.undo_btn.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.redo_btn = ctk.CTkButton(
            tools_frame,
            text="Redo",
            command=self.app.redo,
            height=40
        )
        self.redo_btn.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.theme_btn = ctk.CTkButton(
            tools_frame,
            text="Toggle Theme",
            command=self.app.toggle_theme,
            height=40
        )
        self.theme_btn.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        
        # Recent Files Section
        recent_frame = ctk.CTkFrame(self)
        recent_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(1, weight=1)
        
        recent_label = ctk.CTkLabel(
            recent_frame,
            text="Recent Files",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        recent_label.grid(row=0, column=0, padx=10, pady=(10, 5))
        
        # Recent files listbox with scrollbar
        self.recent_listbox = tk.Listbox(recent_frame, height=8)
        self.recent_listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.recent_listbox.bind('<<ListboxSelect>>', self.on_recent_select)
        
        # Configure scrollbar
        scrollbar = tk.Scrollbar(recent_frame, orient="vertical")
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.recent_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.recent_listbox.yview)
        
        # Help Section
        help_frame = ctk.CTkFrame(self)
        help_frame.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        help_frame.grid_columnconfigure(0, weight=1)
        
        self.help_btn = ctk.CTkButton(
            help_frame,
            text="Help (F1)",
            command=self.app.show_help,
            height=40
        )
        self.help_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        # Configure grid weights for expansion
        self.grid_rowconfigure(3, weight=1)  # Recent files section expands
        
        # Load recent files
        self.update_recent_files()
    
    def update_recent_files(self):
        """Update the recent files list."""
        self.recent_listbox.delete(0, tk.END)
        
        for file_path in self.app.recent_files:
            self.recent_listbox.insert(tk.END, file_path.name)
    
    def on_recent_select(self, event):
        """Handle recent file selection.
        
        Args:
            event: Listbox selection event
        """
        selection = self.recent_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.app.recent_files):
                file_path = self.app.recent_files[index]
                self.app.open_file(file_path)
    
    def refresh(self):
        """Refresh the sidebar content."""
        self.update_recent_files()
