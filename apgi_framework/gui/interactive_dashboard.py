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
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

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
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'apgi-dashboard-secret-key'
        
        # WebSocket setup
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
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
        
        @self.app.route('/')
        def index():
            """Main dashboard page."""
            return render_template('dashboard.html')
        
        @self.app.route('/api/experiments')
        def get_experiments():
            """Get all experiments data."""
            try:
                experiments = self.experiment_monitor.get_all_experiments()
                return jsonify({
                    'success': True,
                    'data': experiments,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/experiment/<experiment_id>')
        def get_experiment(experiment_id):
            """Get specific experiment data."""
            try:
                experiment = self.experiment_monitor.get_experiment_status(experiment_id)
                if not experiment:
                    return jsonify({
                        'success': False,
                        'error': 'Experiment not found'
                    }), 404
                
                # Add visualization data
                viz_data = self.visualizer.create_interactive_dashboard_data(
                    experiment.get('results', []),
                    experiment.get('trials', [])
                )
                
                return jsonify({
                    'success': True,
                    'data': experiment,
                    'visualizations': viz_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/compare', methods=['POST'])
        def compare_experiments():
            """Compare multiple experiments."""
            try:
                data = request.get_json()
                experiment_ids = data.get('experiments', [])
                
                if len(experiment_ids) < 2:
                    return jsonify({
                        'success': False,
                        'error': 'At least 2 experiments required for comparison'
                    }), 400
                
                # Get experiment data
                experiments = {}
                for exp_id in experiment_ids:
                    exp_data = self.experiment_monitor.get_experiment_status(exp_id)
                    if exp_data:
                        experiments[exp_id] = exp_data
                
                if len(experiments) < 2:
                    return jsonify({
                        'success': False,
                        'error': 'Not enough valid experiments found'
                    }), 400
                
                # Generate comparison
                comparison = self.comparator.compare_experiments(experiments)
                
                return jsonify({
                    'success': True,
                    'data': comparison,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/config')
        def get_config():
            """Get current configuration."""
            try:
                config_data = {
                    'apgi_parameters': self.config_manager.get_apgi_parameters().__dict__,
                    'experimental_config': self.config_manager.get_experimental_config().__dict__,
                    'performance_thresholds': self.config_manager.get_performance_thresholds().__dict__,
                    'stimulus_parameters': self.config_manager.get_stimulus_parameters().__dict__
                }
                
                return jsonify({
                    'success': True,
                    'data': config_data,
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/export/<experiment_id>')
        def export_experiment(experiment_id):
            """Export experiment data."""
            try:
                format_type = request.args.get('format', 'json')
                experiment = self.experiment_monitor.get_experiment_status(experiment_id)
                
                if not experiment:
                    return jsonify({
                        'success': False,
                        'error': 'Experiment not found'
                    }), 404
                
                # Export logic here
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if format_type == 'json':
                    filename = f"experiment_{experiment_id}_{timestamp}.json"
                    filepath = Path("exports") / filename
                    filepath.parent.mkdir(exist_ok=True)
                    
                    with open(filepath, 'w') as f:
                        json.dump(experiment, f, indent=2, default=str)
                    
                    return jsonify({
                        'success': True,
                        'filename': filename,
                        'filepath': str(filepath)
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Unsupported format: {format_type}'
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
    
    def _setup_socketio_events(self):
        """Setup WebSocket events for real-time updates."""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection."""
            self.connected_clients.add(request.sid)
            self.logger.info(f"Client connected: {request.sid}")
            
            # Send initial data
            emit('initial_data', {
                'experiments': self.experiment_monitor.get_all_experiments(),
                'config': self._get_config_summary(),
                'timestamp': datetime.now().isoformat()
            })
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection."""
            self.connected_clients.discard(request.sid)
            self.logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle manual update request."""
            try:
                update_data = {
                    'experiments': self.experiment_monitor.get_all_experiments(),
                    'timestamp': datetime.now().isoformat()
                }
                emit('update', update_data)
            except Exception as e:
                emit('error', {'message': str(e)})
    
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
            self.update_thread = threading.Thread(
                target=self._update_loop, 
                daemon=True
            )
            self.update_thread.start()
            
            # Start Flask server
            self.logger.info(f"Starting interactive dashboard at http://{self.host}:{self.port}")
            self.socketio.run(
                self.app, 
                host=self.host, 
                port=self.port, 
                debug=False,
                allow_unsafe_werkzeug=True
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
                # Check for updates
                current_experiments = self.experiment_monitor.get_all_experiments()
                
                # Compare with cached data
                if current_experiments != self.dashboard_cache.get('experiments'):
                    self.dashboard_cache['experiments'] = current_experiments
                    self.last_update = datetime.now()
                    
                    # Broadcast update to all connected clients
                    if self.connected_clients:
                        update_data = {
                            'experiments': current_experiments,
                            'timestamp': self.last_update.isoformat()
                        }
                        self.socketio.emit('update', update_data)
                
                # Sleep for 1 second before next update
                time.sleep(1.0)
                
            except Exception as e:
                self.logger.error(f"Error in update loop: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary for dashboard."""
        try:
            return {
                'apgi': self.config_manager.get_apgi_parameters().__dict__,
                'experimental': self.config_manager.get_experimental_config().__dict__
            }
        except Exception as e:
            self.logger.error(f"Error getting config summary: {e}")
            return {}
    
    def get_dashboard_url(self) -> str:
        """Get dashboard URL."""
        return f"http://{self.host}:{self.port}"


def create_interactive_dashboard(port: int = 8050, host: str = "localhost") -> InteractiveWebDashboard:
    """
    Create and configure an interactive dashboard.
    
    Args:
        port: Web server port
        host: Server host
        
    Returns:
        Configured interactive dashboard
    """
    if Flask is None:
        print("Error: Flask and flask_socketio are required for the interactive dashboard.")
        print("Please install them with: pip install flask flask-socketio")
        return None
    
    return InteractiveWebDashboard(port=port, host=host)


if __name__ == "__main__":
    if Flask is None:
        print("Error: Flask and flask_socketio are required for the interactive dashboard.")
        print("Please install them with: pip install flask flask-socketio")
        exit(1)
    
    dashboard = create_interactive_dashboard()
    if dashboard:
        print(f"Starting interactive dashboard at {dashboard.get_dashboard_url()}")
        dashboard.start_dashboard()
