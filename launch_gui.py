#!/usr/bin/env python3
"""
Launcher script for APGI Framework Falsification Testing System GUI.

This script provides a simple way to launch the GUI application with
proper error handling and dependency checking.
"""

import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are available."""
    required_modules = [
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Error: Missing required modules: {', '.join(missing_modules)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Main launcher function."""
    print("APGI Framework Falsification Testing System")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("apgi_framework").exists():
        print("Error: apgi_framework directory not found.")
        print("Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Add current directory to Python path
    current_dir = Path(__file__).parent.absolute()
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    try:
        print("Starting GUI application...")
        from apgi_falsification_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        print("Please ensure all APGI Framework components are properly installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting GUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()