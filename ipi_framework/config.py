"""
Configuration management system for experimental parameters.

This module provides centralized configuration management for the IPI Framework,
including parameter validation, default values, and experimental settings.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

from .exceptions import ConfigurationError


@dataclass
class IPIParameters:
    """Core IPI equation parameters."""
    extero_precision: float = 2.0
    intero_precision: float = 1.5
    extero_error: float = 1.2
    intero_error: float = 0.8
    somatic_gain: float = 1.3
    threshold: float = 3.5
    steepness: float = 2.0
    
    def __post_init__(self):
        """Validate parameter ranges."""
        if self.extero_precision <= 0:
            raise ConfigurationError("Exteroceptive precision must be positive")
        if self.intero_precision <= 0:
            raise ConfigurationError("Interoceptive precision must be positive")
        if self.somatic_gain <= 0:
            raise ConfigurationError("Somatic gain must be positive")
        if self.steepness <= 0:
            raise ConfigurationError("Steepness parameter must be positive")


@dataclass
class ExperimentalConfig:
    """Configuration for experimental parameters and settings."""
    n_trials: int = 1000
    n_participants: int = 100
    random_seed: Optional[int] = None
    output_directory: str = "results"
    log_level: str = "INFO"
    save_intermediate: bool = True
    
    # Neural signature thresholds
    p3b_threshold: float = 5.0  # μV
    gamma_plv_threshold: float = 0.3
    bold_z_threshold: float = 3.1
    pci_threshold: float = 0.4
    
    # Statistical parameters
    alpha_level: float = 0.05
    effect_size_threshold: float = 0.5
    power_threshold: float = 0.8
    
    def __post_init__(self):
        """Validate experimental configuration."""
        if self.n_trials <= 0:
            raise ConfigurationError("Number of trials must be positive")
        if self.n_participants <= 0:
            raise ConfigurationError("Number of participants must be positive")
        if not 0 < self.alpha_level < 1:
            raise ConfigurationError("Alpha level must be between 0 and 1")


class ConfigManager:
    """Manages configuration loading, validation, and access."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file. If None, uses defaults.
        """
        self.config_path = config_path
        self.ipi_params = IPIParameters()
        self.experimental_config = ExperimentalConfig()
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to JSON configuration file.
            
        Raises:
            ConfigurationError: If configuration file is invalid.
        """
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Load IPI parameters
            if 'ipi_parameters' in config_data:
                ipi_data = config_data['ipi_parameters']
                self.ipi_params = IPIParameters(**ipi_data)
            
            # Load experimental configuration
            if 'experimental_config' in config_data:
                exp_data = config_data['experimental_config']
                self.experimental_config = ExperimentalConfig(**exp_data)
                
        except (json.JSONDecodeError, TypeError, ValueError) as e:
            raise ConfigurationError(f"Invalid configuration file: {e}")
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {config_path}")
    
    def save_config(self, config_path: str) -> None:
        """Save current configuration to JSON file.
        
        Args:
            config_path: Path where to save configuration file.
        """
        config_data = {
            'ipi_parameters': self.ipi_params.__dict__,
            'experimental_config': self.experimental_config.__dict__
        }
        
        # Create directory if it doesn't exist
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_ipi_parameters(self) -> IPIParameters:
        """Get current IPI parameters."""
        return self.ipi_params
    
    def get_experimental_config(self) -> ExperimentalConfig:
        """Get current experimental configuration."""
        return self.experimental_config
    
    def update_ipi_parameters(self, **kwargs) -> None:
        """Update IPI parameters.
        
        Args:
            **kwargs: Parameter names and values to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.ipi_params, key):
                setattr(self.ipi_params, key, value)
            else:
                raise ConfigurationError(f"Unknown IPI parameter: {key}")
        
        # Re-validate parameters
        self.ipi_params.__post_init__()
    
    def update_experimental_config(self, **kwargs) -> None:
        """Update experimental configuration.
        
        Args:
            **kwargs: Configuration names and values to update.
        """
        for key, value in kwargs.items():
            if hasattr(self.experimental_config, key):
                setattr(self.experimental_config, key, value)
            else:
                raise ConfigurationError(f"Unknown experimental parameter: {key}")
        
        # Re-validate configuration
        self.experimental_config.__post_init__()


# Global configuration instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def initialize_config(config_path: Optional[str] = None) -> ConfigManager:
    """Initialize global configuration manager.
    
    Args:
        config_path: Path to configuration file.
        
    Returns:
        Initialized configuration manager.
    """
    global _config_manager
    _config_manager = ConfigManager(config_path)
    return _config_manager