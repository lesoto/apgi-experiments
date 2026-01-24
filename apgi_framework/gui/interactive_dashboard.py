"""
Interactive Web Dashboard for APGI Framework

Provides real-time monitoring, interactive visualizations, and experiment management
through a modern web interface using Flask and WebSocket for real-time updates.
"""

try:
    from flask import Flask, render_template, jsonify, request
    from flask_socketio import SocketIO, emit
except ImportError:
    print("Warning: flask_socketio not available. Running in limited mode.")
    Flask = None
    SocketIO = None
    emit = None
import sys
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from ..logging.standardized_logging import get_logger
    from ..data.dashboard import ExperimentMonitor, ExperimentComparator
    from ..data.visualizer import InteractiveVisualizer
    from ..config import get_config_manager
except ImportError:
    # Handle relative import when run directly
    from apgi_framework.logging.standardized_logging import get_logger
    from apgi_framework.data.dashboard import ExperimentMonitor, ExperimentComparator
    from apgi_framework.data.visualizer import InteractiveVisualizer
    from apgi_framework.config import get_config_manager


class InteractiveWebDashboard:
    """
    Interactive web-based dashboard for real-time experiment monitoring.

    Features:
    - Real-time data streaming via WebSocket
    - Interactive plots with Plotly
    - Experiment management and comparison
    - Live parameter monitoring
    - Export capabilities
    """

    def __init__(self, port: int = 8050, host: str = "localhost"):
        """
        Initialize interactive dashboard.

        Args:
            port: Web server port
            host: Server host
        """
        self.port = port
        self.host = host

        # Flask app setup
        template_dir = Path(__file__).parent / "templates"
        static_dir = Path(__file__).parent / "static"
        self.app = Flask(
            __name__,
            template_folder=str(template_dir),
            static_folder=str(static_dir) if static_dir.exists() else None,
        )
        self.app.config["SECRET_KEY"] = os.getenv(
            "FLASK_SECRET_KEY", os.urandom(24).hex()
        )

        # WebSocket setup
        self.socketio = SocketIO(
            self.app,
            cors_allowed_origins=["http://localhost:5000", "http://127.0.0.1:5000"],
        )

        # Core components
        self.experiment_monitor = ExperimentMonitor()
        self.comparator = ExperimentComparator()
        self.visualizer = InteractiveVisualizer()
        self.config_manager = get_config_manager()

        # Dashboard state
        self.is_running = False
        self.connected_clients = set()
        self.update_thread = None
        self.stop_event = threading.Event()

        # Data cache
        self.dashboard_cache = {}
        self.last_update = datetime.now()

        # Setup routes and WebSocket events
        self._setup_routes()
        self._setup_socketio_events()

        self.logger = get_logger(__name__)
        self.logger.info(f"InteractiveWebDashboard initialized for {host}:{port}")

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """Main dashboard page."""
            return render_template("dashboard.html")

        @self.app.route("/api/experiments")
        def get_experiments():
            """Get all experiments data."""
            try:
                experiments = self.experiment_monitor.get_all_experiments()

                # Validate experiments data structure
                if experiments:
                    for exp in experiments:
                        if not isinstance(exp, dict):
                            self.logger.warning(
                                f"Invalid experiment data type: {type(exp)}"
                            )
                            continue
                        required_fields = ["id", "name", "status", "timestamp"]
                        missing_fields = [
                            field for field in required_fields if field not in exp
                        ]
                        if missing_fields:
                            self.logger.warning(
                                f"Experiment {exp.get('id', 'unknown')} missing fields: {missing_fields}"
                            )

                # If no experiments, provide sample data for demonstration
                if not experiments:
                    self.logger.info("No experiments found, providing sample data")
                    experiments = self._get_sample_experiments()

                return jsonify(
                    {
                        "success": True,
                        "data": experiments,
                        "timestamp": datetime.now().isoformat(),
                        "count": len(experiments),
                        "message": (
                            "Sample data"
                            if not self.experiment_monitor.get_all_experiments()
                            else "Real data"
                        ),
                    }
                )
            except Exception as e:
                self.logger.error(f"Error getting experiments: {e}")
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/experiment/<experiment_id>")
        def get_experiment(experiment_id):
            """Get specific experiment data."""
            try:
                experiment = self.experiment_monitor.get_experiment_status(
                    experiment_id
                )
                if not experiment:
                    return (
                        jsonify({"success": False, "error": "Experiment not found"}),
                        404,
                    )

                # Add visualization data
                viz_data = self.visualizer.create_interactive_dashboard_data(
                    experiment.get("results", []), experiment.get("trials", [])
                )

                return jsonify(
                    {
                        "success": True,
                        "data": experiment,
                        "visualizations": viz_data,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/compare", methods=["POST"])
        def compare_experiments():
            """Compare multiple experiments."""
            try:
                data = request.get_json()
                experiment_ids = data.get("experiments", [])

                if len(experiment_ids) < 2:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "At least 2 experiments required for comparison",
                            }
                        ),
                        400,
                    )

                # Get experiment data
                experiments = {}
                for exp_id in experiment_ids:
                    exp_data = self.experiment_monitor.get_experiment_status(exp_id)
                    if exp_data:
                        experiments[exp_id] = exp_data

                if len(experiments) < 2:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": "Not enough valid experiments found",
                            }
                        ),
                        400,
                    )

                # Generate comparison
                comparison = self.comparator.compare_experiments(experiments)

                return jsonify(
                    {
                        "success": True,
                        "data": comparison,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/config")
        def get_config():
            """Get current configuration."""
            try:
                config_data = {
                    "apgi_parameters": self.config_manager.get_apgi_parameters().__dict__,
                    "experimental_config": self.config_manager.get_experimental_config().__dict__,
                    "performance_thresholds": self.config_manager.get_performance_thresholds().__dict__,
                    "stimulus_parameters": self.config_manager.get_stimulus_parameters().__dict__,
                }

                return jsonify(
                    {
                        "success": True,
                        "data": config_data,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/export/<experiment_id>")
        def export_experiment(experiment_id):
            """Export experiment data."""
            try:
                format_type = request.args.get("format", "json")
                experiment = self.experiment_monitor.get_experiment_status(
                    experiment_id
                )

                if not experiment:
                    return (
                        jsonify({"success": False, "error": "Experiment not found"}),
                        404,
                    )

                # Export logic here
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

                if format_type == "json":
                    filename = f"experiment_{experiment_id}_{timestamp}.json"
                    filepath = Path("exports") / filename
                    filepath.parent.mkdir(exist_ok=True)

                    with open(filepath, "w") as f:
                        json.dump(experiment, f, indent=2, default=str)

                    return jsonify(
                        {
                            "success": True,
                            "filename": filename,
                            "filepath": str(filepath),
                        }
                    )
                else:
                    return (
                        jsonify(
                            {
                                "success": False,
                                "error": f"Unsupported format: {format_type}",
                            }
                        ),
                        400,
                    )

            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

    def _setup_socketio_events(self):
        """Setup WebSocket events for real-time updates."""

        @self.socketio.on("connect")
        def handle_connect():
            """Handle client connection."""
            self.connected_clients.add(request.sid)
            self.logger.info(f"Client connected: {request.sid}")

            # Send initial data
            try:
                experiments = self.experiment_monitor.get_all_experiments()
                if not experiments:
                    self.logger.info(
                        "No experiments found, providing sample data for WebSocket"
                    )
                    experiments = self._get_sample_experiments()

                emit(
                    "initial_data",
                    {
                        "experiments": experiments,
                        "config": self._get_config_summary(),
                        "timestamp": datetime.now().isoformat(),
                        "message": (
                            "Sample data"
                            if not self.experiment_monitor.get_all_experiments()
                            else "Real data"
                        ),
                    },
                )
            except Exception as e:
                self.logger.error(f"Error sending initial data: {e}")
                emit("error", {"message": f"Failed to load initial data: {e}"})

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Handle client disconnection."""
            try:
                self.connected_clients.discard(request.sid)
                self.logger.info(f"Client disconnected: {request.sid}")
            except Exception as e:
                self.logger.error(f"Error handling client disconnection: {e}")

        @self.socketio.on("request_update")
        def handle_update_request():
            """Handle manual update request."""
            try:
                experiments = self.experiment_monitor.get_all_experiments()
                if not experiments:
                    self.logger.info(
                        "No experiments found, providing sample data for update"
                    )
                    experiments = self._get_sample_experiments()

                update_data = {
                    "experiments": experiments,
                    "timestamp": datetime.now().isoformat(),
                    "message": (
                        "Sample data"
                        if not self.experiment_monitor.get_all_experiments()
                        else "Real data"
                    ),
                }
                emit("update", update_data)
            except Exception as e:
                self.logger.error(f"Error handling update request: {e}")
                emit("error", {"message": f"Failed to update data: {e}"})

    def start_dashboard(self):
        """Start the interactive dashboard."""
        if self.is_running:
            self.logger.warning("Dashboard is already running")
            return

        try:
            self.is_running = True
            self.stop_event.clear()

            # Start experiment monitoring
            self.experiment_monitor.start_monitoring()

            # Start real-time update thread
            self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
            self.update_thread.start()

            # Start Flask server
            self.logger.info(
                f"Starting interactive dashboard at http://{self.host}:{self.port}"
            )
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=False,
                allow_unsafe_werkzeug=True,
            )

        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {e}")
            self.stop_dashboard()
            raise

    def stop_dashboard(self):
        """Stop the interactive dashboard."""
        if not self.is_running:
            return

        self.is_running = False
        self.stop_event.set()

        # Stop experiment monitoring
        self.experiment_monitor.stop_monitoring()

        # Wait for update thread
        if self.update_thread:
            self.update_thread.join(timeout=2.0)

        self.logger.info("Interactive dashboard stopped")

    def _update_loop(self):
        """Background thread for real-time updates."""
        while self.is_running and not self.stop_event.is_set():
            try:
                # Only check for updates if there are connected clients
                if self.connected_clients:
                    # Check for updates
                    current_experiments = self.experiment_monitor.get_all_experiments()

                    # Compare with cached data
                    if current_experiments != self.dashboard_cache.get("experiments"):
                        self.dashboard_cache["experiments"] = current_experiments
                        self.last_update = datetime.now()

                        # Broadcast update to all connected clients
                        update_data = {
                            "experiments": current_experiments,
                            "timestamp": self.last_update.isoformat(),
                        }
                        self.socketio.emit("update", update_data)

                    # Sleep for 1 second when clients are connected
                    time.sleep(1.0)
                else:
                    # Sleep longer when no clients are connected to reduce CPU usage
                    time.sleep(5.0)

            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                time.sleep(5.0)  # Wait longer on error

    def _get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for dashboard."""
        try:
            return {
                "apgi": self.config_manager.get_apgi_parameters().__dict__,
                "experimental": self.config_manager.get_experimental_config().__dict__,
            }
        except Exception as e:
            self.logger.error(f"Error getting config summary: {e}")
            return {}

    def _get_sample_experiments(self) -> Dict[str, Dict[str, Any]]:
        """Get sample experiment data for demonstration purposes."""
        return {
            "sample_primary": {
                "id": "sample_primary",
                "metadata": {
                    "name": "Primary Falsification Test",
                    "description": "Sample primary falsification test",
                    "total_trials": 1000,
                    "test_type": "primary",
                },
                "start_time": datetime.now() - timedelta(hours=2),
                "status": "completed",
                "progress": 100.0,
                "current_trial": 1000,
                "total_trials": 1000,
                "results": [
                    {
                        "trial": 1,
                        "falsified": True,
                        "confidence": 0.95,
                        "response_time": 1.23,
                    },
                    {
                        "trial": 2,
                        "falsified": False,
                        "confidence": 0.12,
                        "response_time": 0.87,
                    },
                ],
                "trials": [],
                "last_update": datetime.now() - timedelta(hours=1),
                "statistics": {
                    "trials_per_second": 2.5,
                    "estimated_completion": None,
                    "falsifications_detected": 234,
                    "success_rate": 76.6,
                },
            },
            "sample_consciousness": {
                "id": "sample_consciousness",
                "metadata": {
                    "name": "Consciousness Without Ignition Test",
                    "description": "Sample consciousness test",
                    "total_trials": 500,
                    "test_type": "consciousness-without-ignition",
                },
                "start_time": datetime.now() - timedelta(minutes=30),
                "status": "running",
                "progress": 65.0,
                "current_trial": 325,
                "total_trials": 500,
                "results": [],
                "trials": [],
                "last_update": datetime.now() - timedelta(minutes=5),
                "statistics": {
                    "trials_per_second": 1.8,
                    "estimated_completion": datetime.now() + timedelta(minutes=97),
                    "falsifications_detected": 87,
                    "success_rate": 73.2,
                },
            },
        }

    def get_dashboard_url(self) -> str:
        """Get dashboard URL."""
        return f"http://{self.host}:{self.port}"


def create_interactive_dashboard(
    port: int = 8050, host: str = "localhost"
) -> InteractiveWebDashboard:
    """
    Create and configure an interactive dashboard.

    Args:
        port: Web server port
        host: Server host

    Returns:
        Configured interactive dashboard
    """
    if Flask is None:
        print(
            "Error: Flask and flask_socketio are required for the interactive dashboard."
        )
        print("Please install them with: pip install flask flask-socketio")
        return None

    return InteractiveWebDashboard(port=port, host=host)


if __name__ == "__main__":
    if Flask is None:
        print(
            "Error: Flask and flask_socketio are required for the interactive dashboard."
        )
        print("Please install them with: pip install flask flask-socketio")
        exit(1)

    dashboard = create_interactive_dashboard()
    if dashboard:
        print(f"Starting interactive dashboard at {dashboard.get_dashboard_url()}")
        dashboard.start_dashboard()
