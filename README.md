# APGI Framework

Active Precision Gating and Interoception (APGI) Framework for consciousness research and falsification testing.

## Overview

The APGI Framework provides a comprehensive computational framework for testing theories of consciousness through precision gating mechanisms and interoceptive processing. It implements mathematical models, experimental paradigms, and analysis tools for consciousness research.

## Features

- **Mathematical Core**: Implementation of APGI equations and precision gating mechanisms
- **Experimental Paradigms**: Falsification tests, threshold detection, and cross-species validation
- **Neural Interfaces**: Real-time EEG, pupillometry, and physiological monitoring
- **Interactive Dashboard**: Web-based monitoring and visualization
- **Analysis Tools**: Bayesian parameter estimation, statistical analysis, and reporting
- **Deployment Automation**: Automated deployment and environment management

## Installation

### Prerequisites

- Python 3.8 or higher

- Git

### Quick Setup (Recommended)

1. **Clone the repository:**

```bash
git clone <repository-url>
cd apgi-experiments
```

2. **Create and activate virtual environment:**

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Install the framework:**

```bash
pip install -e .
```

### Alternative Installation Methods

#### Development Installation

```bash
# After setting up virtual environment
pip install -e .[dev,gui,ml]
```

#### Direct Installation (Not Recommended)

```bash
pip install -e .
```

### Verify Installation

Test that all dependencies are installed:

```bash
python -c "import numpy, scipy, pandas, matplotlib, torch, customtkinter; print('✓ All core dependencies installed')"
```

Test the framework:

```bash
python -c "from apgi_framework.config import ConfigManager; print('✓ APGI Framework installed successfully')"
```

Run comprehensive dependency check:

```bash
python check_dependencies.py
```

## Quick Start

### Basic Usage

```python
from apgi_framework import APGIFramework

# Initialize framework
framework = APGIFramework()

# Run falsification test
results = framework.run_falsification_test(
    n_trials=100,
    n_participants=20
)

print(f"Falsification rate: {results.falsification_rate}")
```

### Launch GUI

```bash
python launch_gui.py
```

### Start Interactive Dashboard

```bash
apgi-dashboard --port 8050
```

## Documentation

- [Developer Guide](docs/developer/)
- [Experimental Paradigms](docs/experimental/)
- [API Reference](docs/api/)

## Examples

See the [examples](examples/) directory for comprehensive usage examples:

- [Framework Examples](examples/framework_examples/)
- [Experimental Scripts](examples/)
- [Validation Examples](examples/validation_and_error_handling_example.py)

## Testing

Run the test suite:

```bash
pytest tests/
```
