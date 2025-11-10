# IPI Framework Examples

This directory contains example scripts demonstrating various features of the IPI Framework, including falsification testing, batch processing, custom analysis, and framework extension.

## Falsification Testing Examples

### 01_run_primary_falsification_test.py

Demonstrates how to run the primary falsification test from Python code:

1. **Basic Test**: Run primary falsification test with default parameters
2. **Custom Parameters**: Configure IPI parameters and experimental settings
3. **With Validation**: Run system validation before executing tests

**Run the example:**

```bash
python examples/01_run_primary_falsification_test.py
```

**Key Features:**

- System initialization and configuration
- Running falsification tests programmatically
- Interpreting test results
- System validation and health checks

### 02_batch_processing_configurations.py

Demonstrates batch processing across multiple parameter configurations:

1. **Threshold Variations**: Test multiple threshold values systematically
2. **Precision Combinations**: Explore exteroceptive/interoceptive precision space
3. **Comprehensive Sweep**: Multi-dimensional parameter exploration

**Run the example:**

```bash
python examples/02_batch_processing_configurations.py
```

**Key Features:**
- Systematic parameter exploration
- Sensitivity analysis
- Batch result aggregation
- Automated report generation

### 03_custom_analysis_saved_results.py

Demonstrates custom analysis of saved experimental results:

1. **Falsification Rate Analysis**: Calculate overall and per-test falsification rates
2. **Statistical Power Analysis**: Evaluate statistical power across experiments
3. **Effect Size Analysis**: Analyze effect sizes and their distributions
4. **Experiment Comparison**: Compare multiple experiments side-by-side
5. **Custom Metrics Extraction**: Extract and analyze specific metrics

**Run the example:**

```bash
python examples/03_custom_analysis_saved_results.py
```

**Key Features:**
- Loading saved results from disk
- Statistical re-analysis
- Comparative analysis
- Custom metric extraction
- Report generation

### 04_extending_falsification_criteria.py

Demonstrates how to extend the framework with custom falsification tests:

1. **Temporal Dynamics Test**: Test temporal constraints of ignition signatures
2. **Cross-Modal Integration Test**: Test cross-modal integration requirements
3. **Metacognitive Calibration Test**: Test metacognitive calibration requirements

**Run the example:**

```bash
python examples/04_extending_falsification_criteria.py
```

**Key Features:**
- Creating custom falsification tests
- Implementing novel test criteria
- Custom result structures
- Test interpretation patterns

## Validation and Error Handling Examples

### validation_and_error_handling_example.py

Demonstrates the validation and error handling features:

1. **Parameter Validation**: How to validate parameters before use
2. **System Health Check**: Running system health checks
3. **Safe Configuration**: Creating configurations with automatic validation
4. **Safe Test Execution**: Running tests with error handling
5. **Parameter Information**: Getting information about parameters
6. **Error Recovery**: Error logging and recovery mechanisms

**Run the example:**

```bash
python examples/validation_and_error_handling_example.py
```

### parameter_validation_example.py

Focused examples of parameter validation capabilities.

**Run the example:**

```bash
python examples/parameter_validation_example.py
```

## Quick Start Guide

### Running Your First Falsification Test

```python
from ipi_framework.main_controller import MainApplicationController

# Initialize the system
controller = MainApplicationController()
controller.initialize_system()

# Get falsification tests
tests = controller.get_falsification_tests()

# Run primary falsification test
result = tests['primary'].run_test(n_trials=1000)

# Display results
print(f"Falsified: {result.is_falsified}")
print(f"Confidence: {result.confidence_level:.3f}")
print(f"P-value: {result.p_value:.6f}")

# Cleanup
controller.shutdown_system()
```

### Batch Processing Multiple Configurations

```python
from ipi_framework.main_controller import MainApplicationController

threshold_values = [2.0, 3.0, 4.0, 5.0]
results = []

for threshold in threshold_values:
    controller = MainApplicationController()
    controller.initialize_system()
    
    # Configure parameters
    controller.config_manager.update_ipi_parameters(threshold=threshold)
    
    # Run test
    tests = controller.get_falsification_tests()
    result = tests['primary'].run_test(n_trials=500)
    results.append(result)
    
    controller.shutdown_system()
```

### Loading and Analyzing Saved Results

```python
import json
from pathlib import Path

# Load results
result_files = Path("results").glob("**/*_result_*.json")
results = []

for file_path in result_files:
    with open(file_path, 'r') as f:
        results.append(json.load(f))

# Analyze falsification rate
falsified_count = sum(1 for r in results if r.get('is_falsified', False))
falsification_rate = falsified_count / len(results)

print(f"Falsification rate: {falsification_rate:.1%}")
```

## CLI Usage Examples

The framework also provides a comprehensive CLI for running tests:

### Run Individual Test

```bash
# Run primary falsification test
python -m ipi_framework.cli run-test primary --trials 1000

# Run with custom parameters
python -m ipi_framework.cli run-test primary --trials 2000 --seed 42
```

### Run Batch Tests

```bash
# Run all tests
python -m ipi_framework.cli run-batch --all-tests

# Run specific tests
python -m ipi_framework.cli run-batch --tests primary soma-bias
```

### Generate Configuration
```bash
# Generate default configuration
python -m ipi_framework.cli generate-config --output config.json

# Generate minimal configuration
python -m ipi_framework.cli generate-config --template minimal --output minimal_config.json
```

### System Validation
```bash
# Run system validation
python -m ipi_framework.cli validate-system

# Detailed validation
python -m ipi_framework.cli validate-system --detailed
```

## Requirements

All examples require the IPI Framework to be properly installed with all dependencies:

```bash
pip install -r requirements.txt
```

## Additional Resources

- **Falsification Documentation**: See `IPI-Falsification.md` for theoretical background
- **Validation Documentation**: See `VALIDATION_AND_ERROR_HANDLING_SUMMARY.md`
- **Error Handling Guide**: See `docs/ERROR_HANDLING_QUICK_REFERENCE.md`
- **CLI Reference**: Run `python -m ipi_framework.cli --help`
- **API Documentation**: Check module docstrings in `ipi_framework/`

## Troubleshooting

### Common Issues

**Import Errors**: Ensure the parent directory is in your Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

**No Results Found**: Run some experiments first before trying analysis examples:
```bash
python examples/01_run_primary_falsification_test.py
```

**System Validation Fails**: Check that all components are properly initialized:
```bash
python -m ipi_framework.cli validate-system --detailed
```

## Contributing

To add new examples:
1. Follow the existing naming convention (`##_descriptive_name.py`)
2. Include comprehensive docstrings
3. Add logging for progress tracking
4. Update this README with example description
5. Test the example thoroughly before committing
