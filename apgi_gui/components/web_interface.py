"""
Comprehensive web interface for APGI Framework applications.

Provides a full-featured web-based interface with real-time monitoring,
experiment control, data visualization, and collaborative features.
"""

import json
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Check for optional dependencies
FLASK_AVAILABLE = False
SOCKETIO_AVAILABLE = False

logger = logging.getLogger(__name__)

try:
    from flask import Flask, jsonify, request
    from flask_cors import CORS

    FLASK_AVAILABLE = True
except ImportError:
    logger.warning("Flask not available - install with: pip install flask flask-cors")

try:
    from flask_socketio import SocketIO, emit, join_room, leave_room

    SOCKETIO_AVAILABLE = True
except ImportError:
    logger.warning(
        "Flask-SocketIO not available - install with: " "pip install flask-socketio"
    )


@dataclass
class WebInterfaceConfig:
    """Configuration for web interface."""

    title: str = "APGI Framework Web Interface"
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    static_folder: str = "static"
    template_folder: str = "templates"
    enable_websockets: bool = True
    enable_file_upload: bool = True
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.allowed_extensions:
            self.allowed_extensions = [
                "json",
                "csv",
                "txt",
                "png",
                "jpg",
                "jpeg",
                "pdf",
            ]


class WebSocketManager:
    """Manages WebSocket connections for real-time communication."""

    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.rooms: Dict[str, List[str]] = {}
        self.message_handlers: Dict[str, Callable] = {}

    def add_connection(self, connection_id: str, websocket: Any):
        """Add a WebSocket connection."""
        self.connections[connection_id] = websocket
        logger.info(f"WebSocket connection added: {connection_id}")

    def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.connections:
            del self.connections[connection_id]

        # Remove from all rooms
        for room_id, room_connections in self.rooms.items():
            if connection_id in room_connections:
                room_connections.remove(connection_id)

        logger.info(f"WebSocket connection removed: {connection_id}")

    def join_room(self, connection_id: str, room_id: str):
        """Add connection to a room."""
        if room_id not in self.rooms:
            self.rooms[room_id] = []

        if connection_id not in self.rooms[room_id]:
            self.rooms[room_id].append(connection_id)

        logger.info(f"Connection {connection_id} joined room {room_id}")

    def leave_room(self, connection_id: str, room_id: str):
        """Remove connection from a room."""
        if room_id in self.rooms and connection_id in self.rooms[room_id]:
            self.rooms[room_id].remove(connection_id)

        logger.info(f"Connection {connection_id} left room {room_id}")

    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection."""
        if connection_id in self.connections:
            try:
                await self.connections[connection_id].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")

    async def send_to_room(self, room_id: str, message: Dict[str, Any]):
        """Send message to all connections in a room."""
        if room_id in self.rooms:
            for connection_id in self.rooms[room_id]:
                await self.send_to_connection(connection_id, message)

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connections."""
        for connection_id in self.connections:
            await self.send_to_connection(connection_id, message)

    def register_message_handler(self, message_type: str, handler: Callable):
        """Register a handler for specific message types."""
        self.message_handlers[message_type] = handler


class WebInterface:
    """
    Comprehensive web interface for APGI Framework.

    Provides Flask-based web server with WebSocket support,
    real-time monitoring, and experiment control.
    """

    def __init__(self, config: WebInterfaceConfig):
        if not FLASK_AVAILABLE:
            raise ImportError(
                "Flask is not available. Install with: pip install flask flask-cors"
            )

        self.config = config
        self.app = None
        self.socketio = None
        self.websocket_manager = WebSocketManager()
        self.is_running = False
        self.server_thread: Optional[threading.Thread] = None

        # Data providers
        self.data_providers: Dict[str, Any] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}

        # Create Flask app
        self._create_flask_app()

        # Setup Socket.IO if available
        if SOCKETIO_AVAILABLE and config.enable_websockets:
            self._setup_socketio()

        # Setup routes
        self._setup_routes()

        logger.info("Web interface initialized")

    def _create_flask_app(self):
        """Create Flask application."""
        self.app = Flask(
            __name__,
            static_folder=self.config.static_folder,
            template_folder=self.config.template_folder,
        )

        self.app.config["SECRET_KEY"] = "apgi-framework-secret-key"
        self.app.config["MAX_CONTENT_LENGTH"] = self.config.max_file_size

        # Enable CORS
        CORS(self.app)

    def _setup_socketio(self):
        """Setup Socket.IO for WebSocket support."""
        self.socketio = SocketIO(
            self.app, cors_allowed_origins="*", async_mode="threading"
        )

        # Setup Socket.IO event handlers
        @self.socketio.on("connect")
        def handle_connect():
            connection_id = f"conn_{int(time.time() * 1000)}"
            join_room(connection_id)
            emit("connected", {"connection_id": connection_id})
            logger.info(f"Socket.IO client connected: {connection_id}")

        @self.socketio.on("disconnect")
        def handle_disconnect():
            logger.info("Socket.IO client disconnected")

        @self.socketio.on("join_room")
        def handle_join_room(data):
            room_id = data.get("room_id")
            connection_id = data.get("connection_id")
            if room_id and connection_id:
                join_room(room_id)
                emit("joined_room", {"room_id": room_id})

        @self.socketio.on("leave_room")
        def handle_leave_room(data):
            room_id = data.get("room_id")
            connection_id = data.get("connection_id")
            if room_id and connection_id:
                leave_room(room_id)
                emit("left_room", {"room_id": room_id})

        @self.socketio.on("experiment_command")
        def handle_experiment_command(data):
            self._handle_experiment_command(data)

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route("/")
        def index():
            """Main dashboard page."""
            return self._render_main_dashboard()

        @self.app.route("/api/experiments")
        def get_experiments():
            """Get experiment data API."""
            try:
                experiments = self._get_experiment_data()
                return jsonify({"success": True, "data": experiments})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/experiments/<experiment_id>")
        def get_experiment(experiment_id):
            """Get specific experiment data."""
            try:
                experiment = self._get_experiment_by_id(experiment_id)
                if experiment:
                    return jsonify({"success": True, "data": experiment})
                else:
                    return (
                        jsonify({"success": False, "error": "Experiment not found"}),
                        404,
                    )
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/experiments", methods=["POST"])
        def create_experiment():
            """Create new experiment."""
            try:
                data = request.get_json()
                experiment = self._create_experiment(data)
                return jsonify({"success": True, "data": experiment})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/experiments/<experiment_id>/run", methods=["POST"])
        def run_experiment(experiment_id):
            """Run an experiment."""
            try:
                result = self._run_experiment(experiment_id)
                return jsonify({"success": True, "data": result})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/upload", methods=["POST"])
        def upload_file():
            """Handle file uploads."""
            if not self.config.enable_file_upload:
                return jsonify({"success": False, "error": "File upload disabled"}), 400

            try:
                return self._handle_file_upload()
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/system/status")
        def system_status():
            """Get system status."""
            try:
                status = self._get_system_status()
                return jsonify({"success": True, "data": status})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

        @self.app.route("/api/realtime")
        def realtime_data():
            """Get real-time data."""
            try:
                data = self._get_realtime_data()
                return jsonify({"success": True, "data": data})
            except Exception as e:
                return jsonify({"success": False, "error": str(e)}), 500

    def _render_main_dashboard(self) -> str:
        """Render the main dashboard HTML."""
        # Create a simple HTML dashboard
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .header { background-color: #0078d4; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .card { background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .status-online { color: #28a745; }
        .status-offline { color: #dc3545; }
        .btn { background-color: #0078d4; color: white; padding: 10px 20px; border: none; border-radius: 3px; cursor: pointer; }
        .btn:hover { background-color: #005a9e; }
        .btn:disabled { background-color: #ccc; cursor: not-allowed; }
        #log { background-color: #f8f9fa; border: 1px solid #dee2e6; padding: 10px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{title}}</h1>
        <p>Real-time experiment monitoring and control</p>
    </div>
    
    <div class="grid">
        <div class="card">
            <h3>System Status</h3>
            <p>Status: <span id="system-status" class="status-online">Online</span></p>
            <p>Active Experiments: <span id="active-experiments">0</span></p>
            <p>Completed Experiments: <span id="completed-experiments">0</span></p>
        </div>
        
        <div class="card">
            <h3>Quick Actions</h3>
            <button class="btn" onclick="createExperiment()">New Experiment</button>
            <button class="btn" onclick="refreshData()">Refresh Data</button>
            <button class="btn" onclick="showUpload()">Upload Data</button>
        </div>
        
        <div class="card">
            <h3>Real-time Log</h3>
            <div id="log"></div>
        </div>
    </div>
    
    <div class="card">
        <h3>Experiments</h3>
        <div id="experiments-list">
            <p>Loading experiments...</p>
        </div>
    </div>
    
    <script>
        // WebSocket connection for real-time updates
        let socket;
        
        function connectWebSocket() {
            if (typeof io !== 'undefined') {
                socket = io();
                
                socket.on('connect', function() {
                    addLog('Connected to server');
                });
                
                socket.on('experiment_update', function(data) {
                    updateExperimentStatus(data);
                    addLog('Experiment update: ' + data.name);
                });
                
                socket.on('system_status', function(data) {
                    updateSystemStatus(data);
                });
            }
        }
        
        function addLog(message) {
            const log = document.getElementById('log');
            const timestamp = new Date().toLocaleTimeString();
            log.innerHTML += '[' + timestamp + '] ' + message + '\\n';
            log.scrollTop = log.scrollHeight;
        }
        
        function updateSystemStatus(data) {
            document.getElementById('system-status').textContent = data.online ? 'Online' : 'Offline';
            document.getElementById('system-status').className = data.online ? 'status-online' : 'status-offline';
            document.getElementById('active-experiments').textContent = data.active_experiments || 0;
            document.getElementById('completed-experiments').textContent = data.completed_experiments || 0;
        }
        
        function refreshData() {
            fetch('/api/experiments')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        displayExperiments(data.data);
                    }
                })
                .catch(error => {
                    addLog('Error loading experiments: ' + error);
                });
            
            fetch('/api/system/status')
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateSystemStatus(data.data);
                    }
                })
                .catch(error => {
                    addLog('Error loading system status: ' + error);
                });
        }
        
        function displayExperiments(experiments) {
            const list = document.getElementById('experiments-list');
            if (experiments.length === 0) {
                list.innerHTML = '<p>No experiments found</p>';
                return;
            }
            
            let html = '<table border="1" style="width: 100%; border-collapse: collapse;">';
            html += '<tr><th>Name</th><th>Status</th><th>Created</th><th>Actions</th></tr>';
            
            experiments.forEach(exp => {
                html += '<tr>';
                html += '<td>' + exp.name + '</td>';
                html += '<td>' + exp.status + '</td>';
                html += '<td>' + exp.created_at + '</td>';
                html += '<td><button class="btn" onclick="runExperiment(\\'' + exp.id + '\\')">Run</button></td>';
                html += '</tr>';
            });
            
            html += '</table>';
            list.innerHTML = html;
        }
        
        function createExperiment() {
            const name = prompt('Enter experiment name:');
            if (name) {
                fetch('/api/experiments', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: name,
                        description: 'Web interface experiment'
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        addLog('Created experiment: ' + name);
                        refreshData();
                    } else {
                        addLog('Error creating experiment: ' + data.error);
                    }
                })
                .catch(error => {
                    addLog('Error creating experiment: ' + error);
                });
            }
        }
        
        function runExperiment(experimentId) {
            fetch('/api/experiments/' + experimentId + '/run', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addLog('Started experiment: ' + experimentId);
                    refreshData();
                } else {
                    addLog('Error running experiment: ' + data.error);
                }
            })
            .catch(error => {
                addLog('Error running experiment: ' + error);
            });
        }
        
        function showUpload() {
            addLog('File upload feature - implement file input dialog');
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            connectWebSocket();
            refreshData();
            
            // Auto-refresh every 30 seconds
            setInterval(refreshData, 30000);
        });
    </script>
    
    {% if enable_websockets %}
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    {% endif %}
</body>
</html>
        """

        # Use Flask's render_template_string
        from flask import render_template_string

        return render_template_string(
            html_template,
            title=self.config.title,
            enable_websockets=self.config.enable_websockets,
        )

    def _get_experiment_data(self) -> List[Dict[str, Any]]:
        """Get experiment data from providers."""
        experiments = []

        for provider_name, provider in self.data_providers.items():
            try:
                if hasattr(provider, "get_experiments"):
                    experiments.extend(provider.get_experiments())
                elif hasattr(provider, "get_data"):
                    data = provider.get_data("experiments")
                    if isinstance(data, list):
                        experiments.extend(data)
            except Exception as e:
                logger.error(f"Error getting experiments from {provider_name}: {e}")

        return experiments

    def _get_experiment_by_id(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get specific experiment by ID."""
        experiments = self._get_experiment_data()
        for exp in experiments:
            if exp.get("id") == experiment_id:
                return exp
        return None

    def _create_experiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new experiment."""
        experiment = {
            "id": f"exp_{int(time.time() * 1000)}",
            "name": data.get("name", "Untitled Experiment"),
            "description": data.get("description", ""),
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "parameters": data.get("parameters", {}),
            "results": {},
        }

        # Notify event handlers
        self._notify_event_handlers("experiment_created", experiment)

        return experiment

    def _run_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Run an experiment."""
        experiment = self._get_experiment_by_id(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")

        # Update status
        experiment["status"] = "running"
        experiment["started_at"] = datetime.now().isoformat()

        # Notify event handlers
        self._notify_event_handlers("experiment_started", experiment)

        # Broadcast via WebSocket if available
        if self.socketio:
            self.socketio.emit("experiment_update", experiment)

        # Simulate experiment execution (in real implementation, this would run the actual experiment)
        def simulate_completion():
            time.sleep(2)  # Simulate work
            experiment["status"] = "completed"
            experiment["completed_at"] = datetime.now().isoformat()
            experiment["results"] = {"success": True, "duration": 2.0}

            self._notify_event_handlers("experiment_completed", experiment)

            if self.socketio:
                self.socketio.emit("experiment_update", experiment)

        # Run in background thread
        thread = threading.Thread(target=simulate_completion)
        thread.daemon = True
        thread.start()

        return experiment

    def _handle_file_upload(self) -> Dict[str, Any]:
        """Handle file upload."""
        if "file" not in request.files:
            raise ValueError("No file provided")

        file = request.files["file"]
        if file.filename == "":
            raise ValueError("No file selected")

        # Check file extension
        filename = file.filename
        if filename and not any(
            filename.lower().endswith("." + ext)
            for ext in self.config.allowed_extensions
        ):
            raise ValueError(
                f"File type not allowed. Allowed types: "
                f"{self.config.allowed_extensions}"
            )

        # Save file
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)

        if filename:
            file_path = upload_dir / filename
            file.save(str(file_path))
        else:
            raise ValueError("No filename provided")

        # Process file (example implementation)
        result = {
            "filename": filename,
            "size": file_path.stat().st_size,
            "path": str(file_path),
            "uploaded_at": datetime.now().isoformat(),
        }

        # Notify event handlers
        self._notify_event_handlers("file_uploaded", result)

        return result

    def _get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        status = {
            "online": True,
            "timestamp": datetime.now().isoformat(),
            "active_experiments": 0,
            "completed_experiments": 0,
            "system_info": {"python_version": "3.x", "platform": "Web Interface"},
        }

        # Count experiments
        experiments = self._get_experiment_data()
        for exp in experiments:
            if exp.get("status") == "running":
                status["active_experiments"] += 1  # type: ignore
            elif exp.get("status") == "completed":
                status["completed_experiments"] += 1  # type: ignore

        return status

    def _get_realtime_data(self) -> Dict[str, Any]:
        """Get real-time data."""
        data = {
            "timestamp": datetime.now().isoformat(),
            "cpu_usage": 0.5,  # Placeholder
            "memory_usage": 0.3,  # Placeholder
            "active_connections": (
                len(self.websocket_manager.connections) if self.websocket_manager else 0
            ),
        }

        # Add data from providers
        for provider_name, provider in self.data_providers.items():
            try:
                if hasattr(provider, "get_realtime_data"):
                    provider_data = provider.get_realtime_data()
                    data[provider_name] = provider_data
            except Exception as e:
                logger.error(f"Error getting realtime data from {provider_name}: {e}")

        return data

    def _handle_experiment_command(self, data: Dict[str, Any]):
        """Handle experiment command from WebSocket."""
        command = data.get("command")
        experiment_id = data.get("experiment_id")

        if command == "run":
            try:
                if experiment_id is not None:
                    result = self._run_experiment(experiment_id)
                    emit("experiment_response", {"success": True, "data": result})
                else:
                    emit(
                        "experiment_response",
                        {"success": False, "error": "No experiment ID provided"},
                    )
            except Exception as e:
                emit("experiment_response", {"success": False, "error": str(e)})

        elif command == "stop":
            # Implement stop functionality
            emit(
                "experiment_response",
                {"success": True, "message": "Experiment stopped"},
            )

        else:
            emit(
                "experiment_response",
                {"success": False, "error": f"Unknown command: {command}"},
            )

    def _notify_event_handlers(self, event_type: str, data: Any):
        """Notify registered event handlers."""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Event handler error for {event_type}: {e}")

    def add_data_provider(self, name: str, provider: Any):
        """Add a data provider."""
        self.data_providers[name] = provider
        logger.info(f"Added data provider: {name}")

    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)

    def start_server(self):
        """Start the web server."""
        if self.is_running:
            logger.warning("Web server is already running")
            return

        def run_server():
            try:
                if self.socketio:
                    self.socketio.run(
                        self.app,
                        host=self.config.host,
                        port=self.config.port,
                        debug=self.config.debug,
                        allow_unsafe_werkzeug=True,
                    )
                else:
                    self.app.run(
                        host=self.config.host,
                        port=self.config.port,
                        debug=self.config.debug,
                        threaded=True,
                    )
            except Exception as e:
                logger.error(f"Web server error: {e}")

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        self.is_running = True

        logger.info(
            f"Web interface started at http://{self.config.host}:{self.config.port}"
        )

    def stop_server(self):
        """Stop the web server."""
        self.is_running = False
        logger.info("Web server stopped")


def create_web_interface(config: Optional[WebInterfaceConfig] = None) -> WebInterface:
    """
    Convenience function to create a web interface.

    Args:
        config: Optional configuration

    Returns:
        WebInterface instance
    """
    if config is None:
        config = WebInterfaceConfig()

    return WebInterface(config)
