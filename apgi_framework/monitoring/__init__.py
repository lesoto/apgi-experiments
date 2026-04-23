"""
Monitoring module for APGI Framework.

This module provides real-time monitoring capabilities for:
- EEG signals
- Pupillometry
- Cardiac signals
- Experimental progress
"""

from typing import Any, Dict, List, Optional


# Mock classes for testing
class RealTimeMonitor:
    """Mock real-time monitor for testing purposes."""

    def __init__(self) -> None:
        self.monitoring_active: bool = False
        self.data_buffer: List[Any] = []

    def start_monitoring(self) -> Dict[str, str]:
        """Start real-time monitoring."""
        self.monitoring_active = True
        return {"status": "started", "timestamp": "2024-01-01T00:00:00Z"}

    def stop_monitoring(self) -> Dict[str, str]:
        """Stop real-time monitoring."""
        self.monitoring_active = False
        return {"status": "stopped", "timestamp": "2024-01-01T00:00:00Z"}

    def add_data_point(self, data: Any) -> None:
        """Add a data point to the monitoring buffer."""
        if self.monitoring_active:
            self.data_buffer.append(data)
            if len(self.data_buffer) > 1000:  # Keep buffer size manageable
                self.data_buffer.pop(0)

    def get_latest_data(self, n_points: int = 10) -> List[Any]:
        """Get the latest n data points."""
        return self.data_buffer[-n_points:] if self.data_buffer else []


class PerformanceMonitor:
    """Mock performance monitor for testing purposes."""

    def __init__(self) -> None:
        self.performance_metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.monitoring_active: bool = False

    def start_monitoring(self) -> Dict[str, str]:
        """Start performance monitoring."""
        self.monitoring_active = True
        return {"status": "started", "timestamp": "2024-01-01T00:00:00Z"}

    def stop_monitoring(self) -> Dict[str, str]:
        """Stop performance monitoring."""
        self.monitoring_active = False
        return {"status": "stopped", "timestamp": "2024-01-01T00:00:00Z"}

    def record_metric(self, metric_name: str, value: float) -> None:
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

    def get_metrics(self, metric_name: Optional[str] = None) -> Any:
        """Get performance metrics."""
        if metric_name:
            return self.performance_metrics.get(metric_name, [])
        return self.performance_metrics


__all__ = [
    "RealTimeMonitor",
    "PerformanceMonitor",
]
