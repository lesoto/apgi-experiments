# IPI Framework Documentation Index

Complete documentation for the IPI Framework Falsification Testing System.

## Quick Start

**New Users Start Here:**
1. [Quick Start Guide](QUICK_START_GUIDE.md) - Get running in 5 minutes
2. [GUI Visual Guide](GUI_VISUAL_GUIDE.md) - Visual walkthrough with diagrams
3. [User Guide](USER_GUIDE.md) - Complete guide to using the system
4. [Examples](../examples/README.md) - Working code examples

## Core Documentation

### User Guides

| Document | Description | Audience |
|----------|-------------|----------|
| [Quick Start Guide](QUICK_START_GUIDE.md) | Get started in 5 minutes | New users |
| [User Guide](USER_GUIDE.md) | Complete user guide covering GUI, CLI, and API usage | All users |
| [GUI Visual Guide](GUI_VISUAL_GUIDE.md) | Visual walkthrough of GUI with diagrams | GUI users |
| [CLI Reference](CLI_REFERENCE.md) | Comprehensive command-line interface reference | CLI users |
| [Results Interpretation Guide](RESULTS_INTERPRETATION_GUIDE.md) | How to interpret falsification test results | Researchers |
| [Troubleshooting](TROUBLESHOOTING.md) | Common issues and solutions | All users |

### Technical Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| [Error Handling Quick Reference](ERROR_HANDLING_QUICK_REFERENCE.md) | Error handling patterns and best practices | Developers |
| [Validation Quick Reference](../VALIDATION_QUICK_REFERENCE.md) | Parameter validation reference | Developers |
| [Parameter Validation Guide](parameter_validation_guide.md) | Detailed validation documentation | Developers |

### Theoretical Background

| Document | Description | Audience |
|----------|-------------|----------|
| [IPI Falsification](../IPI-Falsification.md) | Theoretical basis for falsification testing | Researchers |
| [IPI Ignition Equation](../IPI-Ignition-Equation.md) | Mathematical framework documentation | Researchers |
| [IPI Testable Predictions](../IPI-Testable-Predictions.md) | Framework predictions and tests | Researchers |

## Examples and Tutorials

### Example Scripts

Located in `examples/` directory:

| Example | Description | Difficulty |
|---------|-------------|------------|
| [01_run_primary_falsification_test.py](../examples/01_run_primary_falsification_test.py) | Running primary falsification test | Beginner |
| [02_batch_processing_configurations.py](../examples/02_batch_processing_configurations.py) | Batch processing multiple configurations | Intermediate |
| [03_custom_analysis_saved_results.py](../examples/03_custom_analysis_saved_results.py) | Custom analysis of saved results | Intermediate |
| [04_extending_falsification_criteria.py](../examples/04_extending_falsification_criteria.py) | Extending with new falsification tests | Advanced |
| [validation_and_error_handling_example.py](../examples/validation_and_error_handling_example.py) | Validation and error handling | Beginner |

See [Examples README](../examples/README.md) for detailed descriptions and usage.

## Documentation by Task

### Getting Started

**I want to run my first falsification test:**
1. Read [Quick Start Guide](QUICK_START_GUIDE.md) - 5 minute setup
2. Try [Example 01](../examples/01_run_primary_falsification_test.py)
3. Review [Results Interpretation Guide](RESULTS_INTERPRETATION_GUIDE.md)

**I want to use the CLI:**
1. Read [Quick Start Guide - CLI Section](QUICK_START_GUIDE.md#option-b-using-the-cli-recommended-for-automation)
2. Read [CLI Reference](CLI_REFERENCE.md) for complete documentation
3. Try basic commands:
   ```bash
   python -m ipi_framework.cli validate-system
   python -m ipi_framework.cli run-test primary --trials 1000
   ```

**I want to use the GUI:**
1. Read [Quick Start Guide - GUI Section](QUICK_START_GUIDE.md#option-a-using-the-gui-recommended-for-beginners)
2. Read [GUI Visual Guide](GUI_VISUAL_GUIDE.md) for visual walkthrough
3. Launch GUI: `python launch_gui.py`
4. Follow step-by-step instructions in guides

### Running Tests

**I want to run a single test:**
- [User Guide - Running Tests](USER_GUIDE.md#running-a-test)
- [Example 01](../examples/01_run_primary_falsification_test.py)
- [CLI Reference - run-test](CLI_REFERENCE.md#run-test)

**I want to run multiple tests:**
- [User Guide - Batch Processing](USER_GUIDE.md#batch-processing)
- [Example 02](../examples/02_batch_processing_configurations.py)
- [CLI Reference - run-batch](CLI_REFERENCE.md#run-batch)

**I want to customize parameters:**
- [CLI Reference - Parameter Reference](CLI_REFERENCE.md#parameter-reference)
- [User Guide - Parameter Configuration](USER_GUIDE.md#step-2-configure-parameters)
- [Example 02](../examples/02_batch_processing_configurations.py)

### Analyzing Results

**I want to understand my results:**
1. [Results Interpretation Guide](RESULTS_INTERPRETATION_GUIDE.md)
2. [User Guide - Understanding Results](USER_GUIDE.md#understanding-results)
3. Check [Common Scenarios](RESULTS_INTERPRETATION_GUIDE.md#common-scenarios)

**I want to analyze saved results:**
- [Example 03](../examples/03_custom_analysis_saved_results.py)
- [User Guide - Loading Results](USER_GUIDE.md#loading-previous-results)

**I want to export results:**
- [User Guide - Exporting Data](USER_GUIDE.md#exporting-data)
- [CLI Reference - Output Options](CLI_REFERENCE.md#--output-dir--o)

### Troubleshooting

**Something isn't working:**
1. Check [Troubleshooting Guide](TROUBLESHOOTING.md)
2. Run system validation: `python -m ipi_framework.cli validate-system --detailed`
3. Enable debug logging: `--log-level DEBUG`
4. Review [Common Issues](TROUBLESHOOTING.md#common-issues-and-solutions)

**I'm getting errors:**
- [Troubleshooting - Error Categories](TROUBLESHOOTING.md)
- [Error Handling Quick Reference](ERROR_HANDLING_QUICK_REFERENCE.md)
- Check logs: `cat results/ipi_framework.log`

### Advanced Usage

**I want to extend the framework:**
- [Example 04](../examples/04_extending_falsification_criteria.py)
- Review existing test implementations in `ipi_framework/falsification/`

**I want to understand the theory:**
- [IPI Falsification](../IPI-Falsification.md)
- [IPI Ignition Equation](../IPI-Ignition-Equation.md)
- [IPI Testable Predictions](../IPI-Testable-Predictions.md)

**I want to contribute:**
- Review code in `ipi_framework/`
- Check [Error Handling Quick Reference](ERROR_HANDLING_QUICK_REFERENCE.md)
- Follow patterns in existing examples

## Documentation by User Type

### Researchers

**Primary Documents:**
1. [User Guide](USER_GUIDE.md)
2. [Results Interpretation Guide](RESULTS_INTERPRETATION_GUIDE.md)
3. [IPI Falsification](../IPI-Falsification.md)
4. [Examples](../examples/README.md)

**Workflow:**
1. Understand theoretical background
2. Run falsification tests
3. Interpret results correctly
4. Report findings appropriately

### Developers

**Primary Documents:**
1. [Error Handling Quick Reference](ERROR_HANDLING_QUICK_REFERENCE.md)
2. [Validation Quick Reference](../VALIDATION_QUICK_REFERENCE.md)
3. [Example 04 - Extending Framework](../examples/04_extending_falsification_criteria.py)
4. Code in `ipi_framework/`

**Workflow:**
1. Understand system architecture
2. Review existing implementations
3. Follow error handling patterns
4. Extend with new features

### System Administrators

**Primary Documents:**
1. [Troubleshooting Guide](TROUBLESHOOTING.md)
2. [CLI Reference](CLI_REFERENCE.md)
3. [User Guide - Installation](USER_GUIDE.md#installation)

**Workflow:**
1. Install and configure system
2. Validate installation
3. Troubleshoot issues
4. Maintain system health

### Students/Learners

**Primary Documents:**
1. [Quick Start Guide](QUICK_START_GUIDE.md)
2. [GUI Visual Guide](GUI_VISUAL_GUIDE.md)
3. [User Guide](USER_GUIDE.md)
4. [Examples](../examples/README.md)
5. [IPI Falsification](../IPI-Falsification.md)

**Workflow:**
1. Start with Quick Start Guide
2. Follow GUI Visual Guide for hands-on learning
3. Run basic examples
4. Understand theoretical concepts
5. Progress to advanced topics

## Quick Reference Cards

### Common Commands

```bash
# System validation
python -m ipi_framework.cli validate-system

# Run primary test
python -m ipi_framework.cli run-test primary --trials 1000

# Run all tests
python -m ipi_framework.cli run-batch --all-tests

# Generate configuration
python -m ipi_framework.cli generate-config --output config.json

# Check status
python -m ipi_framework.cli status
```

### Common Python Patterns

```python
# Initialize system
from ipi_framework.main_controller import MainApplicationController

controller = MainApplicationController()
controller.initialize_system()

# Run test
tests = controller.get_falsification_tests()
result = tests['primary'].run_test(n_trials=1000)

# Cleanup
controller.shutdown_system()
```

### Parameter Ranges

| Parameter | Range | Default | Units |
|-----------|-------|---------|-------|
| extero_precision | 0.1-10.0 | 2.0 | dimensionless |
| intero_precision | 0.1-10.0 | 1.5 | dimensionless |
| threshold | 0.5-10.0 | 3.5 | dimensionless |
| steepness | 0.1-5.0 | 2.0 | dimensionless |
| somatic_gain | 0.1-5.0 | 1.3 | dimensionless |

### Statistical Thresholds

| Metric | Threshold | Interpretation |
|--------|-----------|----------------|
| Confidence | ≥ 0.8 | High confidence |
| P-value | < 0.05 | Significant |
| Effect Size | ≥ 0.5 | Medium effect |
| Power | ≥ 0.8 | Well-powered |

## Documentation Maintenance

### Version Information

- **Current Version**: 1.0
- **Last Updated**: 2025-01-07
- **Maintainer**: IPI Framework Development Team

### Contributing to Documentation

To improve documentation:
1. Identify gaps or unclear sections
2. Follow existing documentation style
3. Include examples where appropriate
4. Test all code examples
5. Update this index if adding new documents

### Documentation Standards

- Use Markdown format
- Include table of contents for long documents
- Provide working code examples
- Use consistent terminology
- Include version and date information
- Cross-reference related documents

## Additional Resources

### External Resources

- **Python Documentation**: https://docs.python.org/3/
- **NumPy Documentation**: https://numpy.org/doc/
- **SciPy Documentation**: https://docs.scipy.org/doc/
- **Matplotlib Documentation**: https://matplotlib.org/stable/contents.html

### Related Projects

- IPI Framework Core Implementation
- Neural Signature Simulators
- Statistical Analysis Tools

### Support Channels

1. **Documentation**: Start here
2. **Examples**: Working code samples
3. **Validation**: System diagnostics
4. **Logs**: Debug information

---

**Need Help?**
1. Check relevant documentation section above
2. Try examples for your use case
3. Run system validation
4. Review troubleshooting guide
5. Enable debug logging for detailed information

**Quick Links:**
- [Quick Start Guide](QUICK_START_GUIDE.md) - Get started fast
- [GUI Visual Guide](GUI_VISUAL_GUIDE.md) - Visual walkthrough
- [User Guide](USER_GUIDE.md) - Complete documentation
- [Examples](../examples/README.md) - Working code
- [CLI Reference](CLI_REFERENCE.md) - Command reference
- [Troubleshooting](TROUBLESHOOTING.md) - Problem solving
