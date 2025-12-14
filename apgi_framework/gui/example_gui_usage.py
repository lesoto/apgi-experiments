"""
Example usage of the parameter estimation GUI.

Demonstrates how to launch and use the GUI for running parameter estimation experiments.
"""

from pathlib import Path
from apgi_framework.gui import launch_gui


def main():
    """Launch the parameter estimation GUI."""
    # Set up database path
    db_path = Path("data/parameter_estimation.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Launch GUI
    print("Launching APGI Parameter Estimation GUI...")
    print(f"Database: {db_path}")
    print("\nGUI Features:")
    print("- Session management for participants")
    print("- Three behavioral tasks: Detection, Heartbeat, Oddball")
    print("- Real-time monitoring of EEG, pupillometry, and cardiac signals")
    print("- Automatic data quality assessment")
    print("- Parameter estimation with Bayesian modeling")
    print("- Comprehensive reporting and data export")
    print("\nStarting GUI...")
    
    launch_gui(db_path)


if __name__ == "__main__":
    main()
