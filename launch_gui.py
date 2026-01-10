#!/usr/bin/env python3
"""
GUI Launcher for APGI Framework

This script provides a simple launcher to choose between GUI.py and GUI-Simple.py
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import importlib.util


class GUILauncher:
    """Simple launcher to choose between GUI options."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("APGI Framework - GUI Launcher")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        # Center the window
        self.center_window()

        self.create_widgets()

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Create the launcher widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, text="APGI Framework", font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 10))

        subtitle_label = ttk.Label(
            main_frame, text="Choose GUI Interface", font=("Arial", 12)
        )
        subtitle_label.pack(pady=(0, 30))

        # GUI options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.BOTH, expand=True)

        # Full-featured GUI option
        full_gui_frame = ttk.LabelFrame(
            options_frame, text="Full-Featured GUI", padding="15"
        )
        full_gui_frame.pack(fill=tk.X, pady=10)

        ttk.Label(full_gui_frame, text="GUI.py", font=("Arial", 11, "bold")).pack(
            anchor=tk.W
        )
        ttk.Label(full_gui_frame, text="• Complete APGI Framework interface").pack(
            anchor=tk.W, pady=(5, 0)
        )

        # Buttons for full GUI
        button_frame = ttk.Frame(full_gui_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        select_full_button = ttk.Button(
            button_frame, text="Select", command=self.select_full_gui
        )
        select_full_button.pack(side=tk.LEFT)

        # Simple GUI option
        simple_gui_frame = ttk.LabelFrame(
            options_frame, text="Simple GUI", padding="15"
        )
        simple_gui_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            simple_gui_frame, text="GUI-Simple.py", font=("Arial", 11, "bold")
        ).pack(anchor=tk.W)
        ttk.Label(simple_gui_frame, text="• Streamlined interface").pack(
            anchor=tk.W, pady=(5, 0)
        )

        # Buttons for simple GUI
        button_frame = ttk.Frame(simple_gui_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        select_simple_button = ttk.Button(
            button_frame, text="Select", command=self.select_simple_gui
        )
        select_simple_button.pack(side=tk.LEFT)

        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        cancel_button = ttk.Button(bottom_frame, text="Cancel", command=self.root.quit)
        cancel_button.pack(side=tk.RIGHT)

    def launch_full_gui(self):
        """Launch the full-featured GUI."""
        try:
            print("Launching full-featured GUI (GUI.py)")
            self.root.destroy()

            # Import and run the full GUI
            current_dir = Path(__file__).parent.absolute()

            spec = importlib.util.spec_from_file_location(
                "gui_template", current_dir / "GUI.py"
            )
            gui_template = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gui_template)
            app = gui_template.APGIFrameworkGUI()
            app.mainloop()

        except Exception as e:
            print(f"Error launching full GUI: {e}")
            messagebox.showerror("Error", f"Failed to launch full GUI: {e}")

    def launch_simple_gui(self):
        """Launch the simple GUI."""
        try:
            print("Launching simple GUI (GUI-Simple.py)")
            self.root.destroy()

            # Import and run the simple GUI
            current_dir = Path(__file__).parent.absolute()

            spec = importlib.util.spec_from_file_location(
                "template_gui", current_dir / "GUI-Simple.py"
            )
            template_gui = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_gui)
            app = template_gui.TemplateGUI()
            app.run()

        except Exception as e:
            print(f"Error launching simple GUI: {e}")
            messagebox.showerror("Error", f"Failed to launch simple GUI: {e}")

    def select_full_gui(self):
        """Select and launch the full-featured GUI."""
        self.launch_full_gui()

    def select_simple_gui(self):
        """Select and launch the simple GUI."""
        self.launch_simple_gui()

    def run(self):
        """Start the launcher."""
        print("Starting GUI launcher...")
        self.root.mainloop()


def main():
    """Main entry point."""
    try:
        app = GUILauncher()
        app.run()
    except Exception as e:
        print(f"Error starting GUI launcher: {e}")
        messagebox.showerror("Error", f"Failed to start GUI launcher: {e}")


if __name__ == "__main__":
    main()
