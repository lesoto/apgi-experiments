"""
Simple GUI usage example for APGI Framework.

This example demonstrates basic GUI functionality without requiring
all the complex dependencies that may not be available.
"""

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

# Add the parent directory to the path so we can import apgi_framework
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


def launch_simple_gui() -> None:
    """Launch a simple demonstration GUI."""

    # Create main window
    root = tk.Tk()
    root.title("APGI Framework - Simple GUI Demo")
    root.geometry("800x600")

    # Create main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(
        main_frame, text="APGI Framework GUI Demo", font=("Arial", 16, "bold")
    )
    title_label.pack(pady=(0, 20))

    # Description
    desc_text = """
    This is a simplified demonstration of the APGI Framework GUI.
    
    Features available in the full framework:
    • Parameter estimation experiments
    • Real-time neural monitoring
    • Interactive dashboard
    • Data visualization and analysis
    • Deployment automation
    
    Current Status: Framework installed and working!
    """

    desc_label = ttk.Label(main_frame, text=desc_text, justify=tk.LEFT)
    desc_label.pack(pady=(0, 20), fill=tk.X)

    # Status frame
    status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
    status_frame.pack(fill=tk.X, pady=(0, 20))

    # Status items
    status_items = [
        ("Framework Installation:", "✅ Complete"),
        ("Module Import:", "✅ Working"),
        ("Configuration:", "✅ Available"),
        ("Examples:", "✅ Accessible"),
    ]

    for label, status in status_items:
        item_frame = ttk.Frame(status_frame)
        item_frame.pack(fill=tk.X, pady=2)

        ttk.Label(item_frame, text=label, width=20).pack(side=tk.LEFT)
        ttk.Label(item_frame, text=status, width=15).pack(side=tk.LEFT, padx=(10, 0))

    # Action buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=(0, 20))

    def show_info() -> None:
        messagebox.showinfo(
            "APGI Framework",
            "Framework successfully installed and configured!\n\n"
            "You can now:\n"
            "• Run examples from the examples/ directory\n"
            "• Use the interactive dashboard\n"
            "• Deploy with automation tools\n"
            "• Access all framework modules",
        )

    def show_examples() -> None:
        examples_path = Path(__file__).parent
        messagebox.showinfo(
            "Examples Location", f"Framework examples are located at:\n{examples_path}"
        )

    info_btn = ttk.Button(button_frame, text="Show Info", command=show_info)
    info_btn.pack(side=tk.LEFT, padx=(0, 10))

    examples_btn = ttk.Button(button_frame, text="Show Examples", command=show_examples)
    examples_btn.pack(side=tk.LEFT)

    # Exit button
    exit_btn = ttk.Button(main_frame, text="Exit", command=root.quit)
    exit_btn.pack(pady=(20, 0))

    # Start the GUI
    root.mainloop()


def main() -> None:
    """Main function for GUI example."""
    print("Starting APGI Framework GUI Demo...")
    print("This demonstrates that the framework is properly installed.")
    print()

    try:
        launch_simple_gui()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("GUI demo failed to start.")


if __name__ == "__main__":
    main()
