#!/usr/bin/env python3
"""
One-Click Deployment Script for APGI Framework
Designed for non-technical users - minimal configuration required
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from apgi_framework.deployment.automation_manager import DeploymentAutomationManager
    from apgi_framework.logging.standardized_logging import get_logger
    from apgi_framework.config.constants import TimingConstants
except ImportError:
    print(
        "[ERROR] APGI Framework not found. Please ensure you're in the correct directory."
    )
    sys.exit(1)

logger = get_logger(__name__)


class QuickDeploy:
    """Simplified deployment interface for non-technical users."""

    def __init__(self):
        self.manager = DeploymentAutomationManager()

    def check_prerequisites(self) -> bool:
        """Check if Docker is available."""
        print("Checking prerequisites...")

        try:
            # Check Docker
            result = subprocess.run(
                ["docker", "--version"], capture_output=True, text=True, check=True
            )
            print(f"[OK] Docker found: {result.stdout.strip()}")

            # Check Docker Compose
            result = subprocess.run(
                ["docker-compose", "--version"],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"[OK] Docker Compose found: {result.stdout.strip()}")

            return True

        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ERROR] Docker or Docker Compose not found")
            print(
                "Please install Docker Desktop from https://www.docker.com/products/docker-desktop"
            )
            return False

    def interactive_setup(self) -> bool:
        """Interactive setup for basic configuration."""
        print("\nSetup: Quick Setup")
        print("=" * 50)

        # Environment selection
        print("Select environment:")
        print("1. Development (for testing)")
        print("2. Production (for real use)")

        while True:
            choice = input("Enter choice [1-2]: ").strip()
            if choice == "1":
                self.manager.config.environment = "development"
                self.manager.config.monitoring_enabled = True
                break
            elif choice == "2":
                self.manager.config.environment = "production"
                self.manager.config.monitoring_enabled = True
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")

        # Port configuration
        default_port = "8000"
        port = input(f"Enter web port [{default_port}]: ").strip()
        if port:
            try:
                port_num = int(port)
                self.manager.config.ports = {"8000": port_num}
            except ValueError:
                print("Invalid port, using default 8000")

        # Data directory
        default_data = "./data"
        data_dir = input(f"Data directory [{default_data}]: ").strip()
        if data_dir:
            self.manager.config.volumes = {data_dir: "/app/data"}

        # Backup preference
        backup_choice = input("Enable automatic backups? [Y/n]: ").strip().lower()
        self.manager.config.backup_enabled = backup_choice != "n"

        print("\n[OK] Configuration complete!")
        return True

    def deploy(self) -> bool:
        """Perform the deployment."""
        print("\nStarting Deployment...")
        print("=" * 50)

        # Show progress spinner
        import threading
        import time

        stop_spinner = threading.Event()

        def spinner():
            chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            while not stop_spinner.is_set():
                for char in chars:
                    if stop_spinner.is_set():
                        break
                    print(f"\r{char} Deploying...", end="", flush=True)
                    time.sleep(TimingConstants.SHORT_DELAY)

        spinner_thread = threading.Thread(target=spinner, daemon=True)
        spinner_thread.start()

        try:
            success = self.manager.deploy()
            stop_spinner.set()
            print("\r" + " " * 30 + "\r", end="")  # Clear spinner line

            if success:
                print("[OK] Deployment successful!")
                self.show_success_info()
                return True
            else:
                print("[ERROR] Deployment failed!")
                self.show_troubleshooting()
                return False

        except Exception as e:
            stop_spinner.set()
            print(f"\n[ERROR] Deployment error: {e}")
            self.show_troubleshooting()
            return False

    def show_success_info(self):
        """Show success information and next steps."""
        print("\n[SUCCESS] APGI Framework is now running!")
        print("=" * 50)

        status = self.manager.get_status()

        print(f"Container ID: {status['container_id']}")
        print(
            f"Web Interface: http://localhost:{list(self.manager.config.ports.values())[0]}"
        )
        print(f"Health Status: {status['health_status']}")

        if status["monitoring_active"]:
            print("Auto-monitoring is enabled")

        print("\nUseful Commands:")
        print("  python quick_deploy.py status    - Check deployment status")
        print("  python quick_deploy.py stop      - Stop the application")
        print("  python quick_deploy.py logs      - View logs")
        print("  python quick_deploy.py help      - Show more options")

        print("\n📁 Data Locations:")
        print("  Application Data: ./data")
        print("  Outputs: ./apgi_outputs")
        print("  Session State: ./session_state")
        print("  Logs: ./logs")

        if self.manager.config.backup_enabled:
            print("💾 Automatic backups are enabled in ./backups/")

    def show_troubleshooting(self):
        """Show troubleshooting information."""
        print("\nTroubleshooting")
        print("=" * 50)

        print("Common issues and solutions:")
        print("1. Docker not running - Start Docker Desktop")
        print("2. Port already in use - Try a different port")
        print("3. Permission denied - Run with administrator privileges")
        print("4. Out of memory - Close other applications")

        print("\nFor detailed logs, run:")
        print("  python quick_deploy.py logs")

        print("\nFor support, check:")
        print("  📖 docs/user/troubleshooting.md")

    def show_status(self):
        """Show current status."""
        status = self.manager.get_status()

        print("Deployment Status")
        print("=" * 50)

        if status["is_running"]:
            print(f"[OK] Running: Yes")
            print(
                f"Web Interface: http://localhost:{list(self.manager.config.ports.values())[0]}"
            )
            print(f"Health: {status['health_status']}")
            print(f"CPU: {status['cpu_usage']:.1f}%")
            print(f"Memory: {status['memory_usage']:.1f}%")

            if status["error_count"] > 0:
                print(f"[WARN] Errors: {status['error_count']}")
        else:
            print("[ERROR] Running: No")
            print("Run 'python quick_deploy.py deploy' to start")

    def stop_deployment(self):
        """Stop the deployment."""
        print("Stopping APGI Framework...")
        self.manager.cleanup()
        print("[OK] Stopped successfully")

    def show_logs(self):
        """Show logs."""
        if not self.manager._is_container_running():
            print("[ERROR] Container is not running")
            return

        print("📄 Showing logs (Ctrl+C to stop)...")
        try:
            subprocess.run(["docker", "logs", "-f", self.manager.config.container_name])
        except KeyboardInterrupt:
            print("\n📄 Logs display stopped")


def main():
    """Main entry point."""
    if len(sys.argv) < 2 or sys.argv[1] == "deploy":
        # Default deployment flow
        deployer = QuickDeploy()

        print("APGI Framework Quick Deploy")
        print("=" * 50)
        print(
            "This script will help you deploy APGI Framework with minimal configuration."
        )
        print()

        # Check prerequisites
        if not deployer.check_prerequisites():
            input("Press Enter to exit...")
            sys.exit(1)

        # Interactive setup
        if not deployer.interactive_setup():
            input("Press Enter to exit...")
            sys.exit(1)

        # Deploy
        if deployer.deploy():
            input("\nPress Enter to exit...")
            sys.exit(0)
        else:
            input("\nPress Enter to exit...")
            sys.exit(1)

    else:
        # Handle other commands
        deployer = QuickDeploy()
        command = sys.argv[1]

        if command == "status":
            deployer.show_status()
        elif command == "stop":
            deployer.stop_deployment()
        elif command == "logs":
            deployer.show_logs()
        elif command == "help":
            print("APGI Framework Quick Deploy")
            print("=" * 50)
            print("Commands:")
            print("  python quick_deploy.py deploy   - Deploy the application")
            print("  python quick_deploy.py status   - Show deployment status")
            print("  python quick_deploy.py stop     - Stop the application")
            print("  python quick_deploy.py logs     - View logs")
            print("  python quick_deploy.py help     - Show this help")
        else:
            print(f"[ERROR] Unknown command: {command}")
            print("Run 'python quick_deploy.py help' for available commands")


if __name__ == "__main__":
    main()
