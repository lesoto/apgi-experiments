"""
Monitoring module for APGI Framework.

This module provides real-time monitoring capabilities for:
- EEG signals
- Pupillometry
- Cardiac signals
- Experimental progress
"""

# Mock classes for testing
class RealTimeMonitor:
    """Mock real-time monitor for testing purposes."""

    def __init__(self):
        self.monitoring_active = False
        self.data_buffer = []

    def start_monitoring(self):
        """Start real-time monitoring."""
        self.monitoring_active = True
        return {"status": "started", "timestamp": "2024-01-01T00:00:00Z"}

    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.monitoring_active = False
        return {"status": "stopped", "timestamp": "2024-01-01T00:00:00Z"}

    def add_data_point(self, data):
        """Add a data point to the monitoring buffer."""
        if self.monitoring_active:
            self.data_buffer.append(data)
            if len(self.data_buffer) > 1000:  # Keep buffer size manageable
                self.data_buffer.pop(0)

    def get_latest_data(self, n_points=10):
        """Get the latest n data points."""

        return self.data_buffer[-n_points:] if self.data_buffer else []


class PerformanceMonitor:
    """Mock performance monitor for testing purposes."""

    def __init__(self):
        self.performance_metrics = {}
        self.monitoring_active = False

    def start_monitoring(self):
        """Start performance monitoring."""
        self.monitoring_active = True
        return {"status": "started", "timestamp": "2024-01-01T00:00:00Z"}

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        return {"status": "stopped", "timestamp": "2024-01-01T00:00:00Z"}

    def record_metric(self, metric_name, value):
        """Record a performance metric."""
        if self.monitoring_active:
            if metric_name not in self.performance_metrics:
                self.performance_metrics[metric_name] = []
            self.performance_metrics[metric_name].append(
                {
                    "value": value,
                    "timestamp": "2024-01-01T00:00:00Z",
                }
            )

    def get_metrics(self, metric_name=None):
        """Get performance metrics."""
        if metric_name:
            return self.performance_metrics.get(metric_name, [])
        return self.performance_metrics


__all__ = [
    "RealTimeMonitor",
    "PerformanceMonitor",
]
