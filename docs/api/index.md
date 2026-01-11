# APGI Framework API Documentation

This directory contains the API documentation for the APGI Framework.

## Structure

- **core/** - Core APGI equations and models
- **falsification/** - Falsification testing framework  
- **config/** - Configuration management
- **data/** - Data management and storage
- **analysis/** - Analysis and statistical tools
- **gui/** - GUI components and interfaces
- **cli/** - Command-line interface
- **utils/** - Utility functions

## Getting Started

For detailed API documentation, see the individual module documentation
or visit the main documentation at: ../README.md

## API Reference

### Core Modules

#### APGI Framework
```python
from apgi_framework import APGIFramework
```

#### Configuration
```python
from apgi_framework.config import ConfigManager, APGIParameters
```

### Data Management

#### Data Manager
```python
from apgi_framework.data.data_manager import IntegratedDataManager
```

### Analysis Tools

#### Bayesian Models
```python
from apgi_framework.analysis.bayesian_models import BayesianParameterEstimator
```

### GUI Components

#### Main GUI Controller
```python
from apgi_framework.gui.components.main_gui_controller import MainGUIController
```

## Examples

See the `examples/` directory for comprehensive usage examples.
