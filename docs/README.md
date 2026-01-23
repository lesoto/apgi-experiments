# APGI Framework

APGI Framework Entry Points Analysis
🖥️ GUI Applications
Main GUI Applications
GUI.py - Main comprehensive GUI application (244KB)
GUI-Simple.py - Simplified GUI template version
GUI-Experiment-Registry.py - Experiment registry GUI for running 24 experiments
launch_gui.py - Centralized GUI launcher for all applications
apgi_gui/app.py - Modern GUI application using customtkinter
Apps Directory GUIs
apps/apgi_falsification_gui.py - Falsification testing GUI (74KB)
apps/apgi_falsification_gui_refactored.py - Refactored falsification GUI
apps/experiment_runner_gui.py - Experiment runner interface
apps/gui_template.py - GUI template (241KB)
apps/gui_template_background.py - Background GUI template
Framework GUI Components
apgi_framework/gui/coverage_visualization.py - Test coverage visualization
apgi_framework/gui/enhanced_monitoring_dashboard.py - Enhanced monitoring dashboard
apgi_framework/gui/interactive_dashboard.py - Interactive dashboard
apgi_framework/gui/monitoring_dashboard.py - Basic monitoring dashboard
apgi_framework/gui/parameter_estimation_gui.py - Parameter estimation GUI
apgi_framework/gui/progress_monitoring.py - Progress monitoring GUI
apgi_framework/gui/reporting_visualization.py - Reporting visualization
apgi_framework/gui/results_viewer.py - Results viewer GUI
apgi_framework/gui/session_management.py - Session management GUI
apgi_framework/gui/task_configuration.py - Task configuration GUI
⌨️ CLI Interfaces
Primary CLI Entry Points
apgi_framework/cli.py - Main command-line interface
apgi_framework/main.py - Module entry point (python -m apgi_framework)
apgi_framework/deployment/cli.py - Deployment CLI
apgi_framework/validation/diagnostics_cli.py - Diagnostics CLI
CLI Tools
tools/run_tests.py - Test runner CLI
tools/run_experiments.py - Experiment runner CLI
🔧 Standalone Tools & Scripts
Setup & Deployment
setup.py - Installation and setup script
setup.sh - Unix/Linux setup script
deploy.bat - Windows deployment script
deploy.sh - Unix/Linux deployment script
quick_deploy.py - Quick deployment tool
delete_pycache.py - Cache cleanup utility
Analysis & Processing
tools/run_experiments.py - Experiment execution tool
examples/data_loader.py - Data loading utility
examples/coverage_collector_demo.py - Coverage collection demo
🧪 Testing Suites
Main Test Runner
run_tests.py - Comprehensive test runner with GUI integration
Test Categories
Unit Tests - Fast, isolated component tests
Integration Tests - Cross-component integration tests
Framework Tests - Core framework functionality tests
Falsification Tests - Falsification testing validation
GUI Tests - GUI component testing
Performance Tests - Benchmark and performance tests
Research Tests - Domain-specific experiment tests
Test Configuration
pytest.ini - Pytest configuration (61 lines)
pyproject.toml - Modern testing configuration (225 lines)
Key Test Files
tests/test_gui_components.py - GUI component tests
tests/test_cli_module.py - CLI module tests
tests/test_falsification_coverage.py - Falsification coverage tests
tests/framework/ - Framework-specific tests (9 files)
tests/falsification/ - Falsification tests (7 files)
tests/integration/ - Integration tests (4 files)
🚀 Module Entry Points
Framework Module
python -m apgi_framework - Main framework module execution
Package Entry Points
apgi_framework/init.
py - Package initialization
apgi_gui/__init__.py - GUI package initialization

## Quick Start (5 minutes)

__New to the system?__ See the [Quick Start Guide](docs/QUICK_START_GUIDE.md) for a 5-minute introduction.

__Using GUI?__ Check out the [GUI Visual Guide](docs/GUI_VISUAL_GUIDE.md) for a visual walkthrough.

__Using Web Interface?__ Visit [APGI-Experiments.html](../../apgi-web/APGI-Experiments.html) for interactive web-based experiments and visualizations.

__Need help?__ See the [Documentation Index](docs/DOCUMENTATION_INDEX.md) for complete documentation.

### Installation

1. __Set up the environment__

   ```bash
   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/macOS
   
   # Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

2. __Validate installation__

   ```bash
   python -m apgi_framework.cli validate-system
   ```

3. __Run the APGI Agent example__

   ```bash
   python -m core.models.apgi_agent
   ```

4. __Run the Somatic Agent example__

   ```bash
   python -m core.models.phase_transition
   ```

5. __Run experiments via GUI__

   ```bash
   python gui.py
   ```

6. __Run experiments via command line__

   ```bash
   # Run interoceptive gating experiment
   python run_experiments.py interoceptive_gating --n_participants 10 --n_trials 50
   
   # Run AI benchmarking experiment
   python run_experiments.py ai_benchmarking --n_episodes 100 --n_agents_per_type 3
   ```

## Currently Implemented

### Core Models

1. __APGI Agent__ (`core/models/apgi_agent.py`)
   - Implements the core APGI framework with interoceptive and exteroceptive processing
   - Dynamic threshold mechanism for conscious access
   - Precision-weighted prediction errors
   - Somatic marker integration

2. __Phase Transition Model__ (`core/models/phase_transition.py`)
   - Somatic marker-based decision making
   - Conscious vs unconscious processing modes
   - Expected free energy calculations

3. __Base Experiment Framework__ (`core/experiment.py`)
   - Abstract base class for all experiments
   - Standardized data collection and analysis

### Implemented Experiments

1. __Interoceptive Gating Paradigm__ (`experiments/interoceptive_gating/`)
   - Tests how interoceptive precision gates conscious access
   - Cardiac discrimination task simulation
   - Three conditions: interoceptive focus, exteroceptive focus, control
   - Threshold tracking and detection rate analysis

2. __AI Benchmarking__ (`experiments/ai_benchmarking/`)
   - Compares different agent architectures in survival environments
   - Includes Random, Reactive, DQN, and APGI agents
   - Grid world environment with food, obstacles, and predators
   - Performance metrics: survival time, energy efficiency, food consumption

### Demonstration Scripts

1. __APGI Model Demonstrations__ (`run_experiments.py`)
   - Threshold effects on ignition probability
   - Somatic marker influence on decision making
   - Precision parameter effects
   - Dynamic threshold adaptation

2. __GUI Interface__ (`gui.py`)
   - Tkinter-based interface for running experiments
   - Parameter configuration and real-time logging
   - Supports all implemented experiments

3. __Web Interface__ (`../../apgi-web/APGI-Experiments.html`)
   - Interactive web-based experiments and visualizations
   - Modern responsive design with real-time particle animations
   - Neural network visualizations and interactive parameter controls
   - Cross-platform accessibility through web browser

## Key Features

- __Modular Architecture__: Clean separation between models, experiments, and utilities
- __Standardized Experiments__: All experiments inherit from `BaseExperiment` for consistency
- __Multiple Interfaces__: Command-line, GUI, web interface, and programmatic access
- __Data Management__: Automatic data saving and visualization
- __Extensible Design__: Easy to add new models and experiments
- __Web-Based Visualization__: Interactive experiments with real-time neural animations

## Example Usage

### Running Falsification Tests

__Using the GUI:__

```bash
python launch_gui.py
```python

__Using the CLI:__

```bash

# Run primary falsification test

python -m apgi_framework.cli run-test primary --trials 1000

# Run all tests

python -m apgi_framework.cli run-batch --all-tests
```python

__Using Python API:__

```python
from apgi_framework.main_controller import MainApplicationController

# Initialize system

controller = MainApplicationController()
controller.initialize_system()

# Run test

tests = controller.get_falsification_tests()
result = tests['primary'].run_test(n_trials=1000)
print(f"Falsified: {result.is_falsified}")
print(f"Confidence: {result.confidence_level:.2f}")

# Cleanup

controller.shutdown_system()
```python

## Running the APGI Agent

```python
from core.models.apgi_agent import APGIAgent

# Create and run agent with default parameters

agent = APGIAgent()
agent.run_example()  # Runs simulation and shows plots
```python

### Running an Experiment

```python
from research.interoceptive_gating.experiments.experiment import run_interoceptive_gating_experiment

# Run experiment with custom parameters

experiment = run_interoceptive_gating_experiment(
    n_participants=20,
    n_trials_per_condition=100
)
```python

## Documentation

Complete documentation is available in the `docs/` directory and web interface:

- __[APGI-Experiments.html](../../apgi-web/APGI-Experiments.html)__ - Interactive web-based experiments and visualizations
- __[Quick Start Guide](docs/QUICK_START_GUIDE.md)__ - Get started in 5 minutes
- __[GUI Visual Guide](docs/GUI_VISUAL_GUIDE.md)__ - Visual walkthrough of GUI
- __[User Guide](docs/USER_GUIDE.md)__ - Complete user manual
- __[CLI Reference](docs/CLI_REFERENCE.md)__ - Command-line interface documentation
- __[Results Interpretation Guide](docs/RESULTS_INTERPRETATION_GUIDE.md)__ - Understanding test results
- __[Troubleshooting](docs/TROUBLESHOOTING.md)__ - Common issues and solutions
- __[Documentation Index](docs/DOCUMENTATION_INDEX.md)__ - Complete documentation index

See [docs/README.md](docs/README.md) for a complete documentation overview.
