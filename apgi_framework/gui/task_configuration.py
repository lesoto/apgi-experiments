"""
Task parameter configuration for parameter estimation experiments.

Provides classes for configuring adaptive algorithms and stimulus parameters.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DetectionTaskConfig:
    """Configuration for detection task."""
    modality: str = "visual"  # 'visual' or 'auditory'
    n_trials: int = 200
    duration_minutes: float = 10.0
    
    # Staircase parameters
    stimulus_min: float = 0.01
    stimulus_max: float = 1.0
    stimulus_steps: int = 50
    
    # Stimulus parameters
    gabor_spatial_frequency: float = 2.0
    gabor_size_degrees: float = 2.0
    tone_frequency_hz: float = 1000.0
    stimulus_duration_ms: float = 500.0


@dataclass
class HeartbeatTaskConfig:
    """Configuration for heartbeat detection task."""
    n_trials: int = 60
    duration_minutes: float = 8.0
    
    # Adaptive parameters
    initial_asynchrony_ms: float = 300.0
    min_asynchrony_ms: float = 200.0
    max_asynchrony_ms: float = 600.0
    adjustment_step_ms: float = 50.0
    
    # Stimulus parameters
    tone_frequency_hz: float = 1000.0
    tone_duration_ms: float = 50.0
    tone_amplitude: float = 0.7


@dataclass
class OddballTaskConfig:
    """Configuration for dual-modality oddball task."""
    n_trials: int = 120
    duration_minutes: float = 12.0
    deviant_probability: float = 0.2
    
    # Calibration parameters
    calibration_trials_per_modality: int = 30
    
    # Interoceptive stimulus parameters
    co2_concentration: float = 10.0
    co2_duration_ms: float = 300.0
    
    # Exteroceptive stimulus parameters
    gabor_standard_orientation: float = 0.0
    gabor_deviant_orientation: float = 45.0
    tone_standard_frequency: float = 1000.0
    tone_deviant_frequency: float = 1200.0


class TaskParameterConfigurator:
    """
    Manages task parameter configuration.
    
    Provides interface for adjusting adaptive algorithm and stimulus parameters.
    """
    
    def __init__(self):
        """Initialize task parameter configurator."""
        self.detection_config = DetectionTaskConfig()
        self.heartbeat_config = HeartbeatTaskConfig()
        self.oddball_config = OddballTaskConfig()
        
        logger.info("TaskParameterConfigurator initialized")
    
    def get_detection_config(self) -> DetectionTaskConfig:
        """Get detection task configuration."""
        return self.detection_config
    
    def update_detection_config(self, **kwargs) -> None:
        """
        Update detection task configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.detection_config, key):
                setattr(self.detection_config, key, value)
                logger.info(f"Updated detection config: {key}={value}")
            else:
                logger.warning(f"Unknown detection config parameter: {key}")
    
    def get_heartbeat_config(self) -> HeartbeatTaskConfig:
        """Get heartbeat task configuration."""
        return self.heartbeat_config
    
    def update_heartbeat_config(self, **kwargs) -> None:
        """
        Update heartbeat task configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.heartbeat_config, key):
                setattr(self.heartbeat_config, key, value)
                logger.info(f"Updated heartbeat config: {key}={value}")
            else:
                logger.warning(f"Unknown heartbeat config parameter: {key}")
    
    def get_oddball_config(self) -> OddballTaskConfig:
        """Get oddball task configuration."""
        return self.oddball_config
    
    def update_oddball_config(self, **kwargs) -> None:
        """
        Update oddball task configuration.
        
        Args:
            **kwargs: Configuration parameters to update
        """
        for key, value in kwargs.items():
            if hasattr(self.oddball_config, key):
                setattr(self.oddball_config, key, value)
                logger.info(f"Updated oddball config: {key}={value}")
            else:
                logger.warning(f"Unknown oddball config parameter: {key}")
    
    def get_all_configs(self) -> Dict[str, Any]:
        """
        Get all task configurations.
        
        Returns:
            Dictionary with all configurations
        """
        return {
            'detection': self.detection_config.__dict__,
            'heartbeat': self.heartbeat_config.__dict__,
            'oddball': self.oddball_config.__dict__
        }
    
    def reset_to_defaults(self) -> None:
        """Reset all configurations to defaults."""
        self.detection_config = DetectionTaskConfig()
        self.heartbeat_config = HeartbeatTaskConfig()
        self.oddball_config = OddballTaskConfig()
        
        logger.info("Reset all task configurations to defaults")
    
    def validate_config(self, task_type: str) -> bool:
        """
        Validate configuration for a task type.
        
        Args:
            task_type: Type of task ('detection', 'heartbeat', or 'oddball')
            
        Returns:
            True if configuration is valid
        """
        if task_type == 'detection':
            config = self.detection_config
            return (config.n_trials > 0 and 
                   config.stimulus_min < config.stimulus_max and
                   config.stimulus_steps > 0)
        
        elif task_type == 'heartbeat':
            config = self.heartbeat_config
            return (config.n_trials > 0 and
                   config.min_asynchrony_ms < config.max_asynchrony_ms)
        
        elif task_type == 'oddball':
            config = self.oddball_config
            return (config.n_trials > 0 and
                   0 < config.deviant_probability < 1)
        
        return False
