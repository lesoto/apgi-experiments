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
- NumPy, SciPy, Matplotlib
- Optional: Flask, Plotly (for dashboard)

### Install from Source

```bash
git clone <repository-url>
cd apgi-experiments
pip install -e .
```

### Development Installation

```bash
pip install -e .[dev,gui]
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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this framework in your research, please cite:

```
APGI Framework for Consciousness Research
(2026) https://github.com/apgi-research/apgi-framework
```

## Support

For questions and support:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [examples](examples/)
