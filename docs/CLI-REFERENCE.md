# APGI Framework CLI Reference

This document provides comprehensive reference for the APGI Framework command-line interface.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Command Overview](#command-overview)
3. [Global Options](#global-options)
4. [Test Commands](#test-commands)
5. [Configuration Commands](#configuration-commands)
6. [Workflow Commands](#workflow-commands)
7. [Utility Commands](#utility-commands)
8. [Examples](#examples)
9. [Exit Codes](#exit-codes)

## Getting Started

The APGI Framework provides several command-line entry points:

```bash
# Main CLI interface
python -m apgi_framework.cli

# Test runner
apgi-test

# GUI launcher
apgi-gui

# Deployment tools
apgi-deploy
```

## Command Overview

### Main Commands

|  Command  | Description |
|  -------  | ----------- |

|  `test`  | Run test suites and validation |
|  `config`  | Manage configuration profiles |
|  `workflow`  | Execute end-to-end workflows |
|  `gui`  | Launch graphical interface |
|  `deploy`  | Deployment and packaging tools |
|  `validate`  | Data and system validation |
|  `report`  | Generate reports and documentation |

## Global Options

All commands support these global options:

|  Option  | Short |  Description  |
|  ------  | ----- |  -----------  |

|  `--help`  | `-h` |  Show help message  |
|  `--verbose`  | `-v` |  Enable verbose output  |
|  `--quiet`  | `-q` |  Suppress non-error output  |
|  `--config`  | `-c` |  Specify configuration file  |
|  `--log-level`  | `-l` |  Set logging level (DEBUG, INFO, WARNING, ERROR)  |
|  `--output-dir`  | `-o` |  Specify output directory  |
|  `--dry-run`  | |  Show what would be done without executing  |

## Test Commands

### Run Tests

```bash
# Run all tests
apgi-test run

# Run specific test categories
apgi-test run --category unit
apgi-test run --category integration
apgi-test run --category performance

# Run with coverage
apgi-test run --coverage --coverage-report html

# Run specific test files
apgi-test run tests/test_apgi_equations.py

# Run with timeout
apgi-test run --timeout 300

# Run in parallel
apgi-test run --parallel --workers 4
```

### Test Options

|  Option  | Description |
|  ------  | ----------- |

|  `--category`  | Test category (unit, integration, gui, performance, research) |
|  `--coverage`  | Enable coverage reporting |
|  `--coverage-report`  | Coverage report format (html, xml, term) |
|  `--timeout`  | Test timeout in seconds |
|  `--parallel`  | Run tests in parallel |
|  `--workers`  | Number of parallel workers |
|  `--fail-fast`  | Stop on first failure |
|  `--reruns`  | Number of times to retry failed tests |

### List Tests

```bash
# List all available tests
apgi-test list

# List tests by category
apgi-test list --category unit

# List test files
apgi-test list --files
```

### Test Validation

```bash
# Validate test configuration
apgi-test validate

# Check test dependencies
apgi-test check-deps
```

## Configuration Commands

### Manage Configurations

```bash
# List available configuration profiles
apgi config list

# Create new configuration profile
apgi config create my_profile --description "Custom profile"

# Load configuration profile
apgi config load my_profile

# Save current configuration
apgi config save my_profile

# Delete configuration profile
apgi config delete my_profile

# Export configuration
apgi config export config.yaml

# Import configuration
apgi config import config.yaml
```

### Configuration Validation

```bash
# Validate configuration file
apgi config validate config.yaml

# Check configuration compatibility
apgi config check-compat
```

### Environment Management

```bash
# Show current environment settings
apgi config env

# Set environment variable
apgi config env APGI_LOG_LEVEL DEBUG

# Reset to defaults
apgi config reset
```

## Workflow Commands

### Execute Workflows

```bash
# Run standard falsification workflow
apgi workflow run-standard

# Run quick validation workflow
apgi workflow run-quick

# Run custom workflow from config
apgi workflow run config/workflow.yaml

# Run parallel workflow
apgi workflow run-parallel

# Cancel running workflow
apgi workflow cancel
```

### Workflow Management

```bash
# List available workflows
apgi workflow list

# Show workflow status
apgi workflow status

# Get workflow history
apgi workflow history

# Clean workflow artifacts
apgi workflow clean
```

### Workflow Options

|  Option  | Description |
|  ------  | ----------- |

|  `--config`  | Workflow configuration file |
|  `--output-dir`  | Output directory for results |
|  `--parallel`  | Enable parallel execution |
|  `--timeout`  | Workflow timeout in minutes |
|  `--resume`  | Resume interrupted workflow |

## Utility Commands

### Data Management

```bash
# Validate dataset
apgi validate data dataset.json

# Check data integrity
apgi validate integrity data.h5

# Export data
apgi data export --format csv dataset.json

# Import data
apgi data import --format json data.csv
```

### System Validation

```bash
# Run system health check
apgi validate system

# Check dependencies
apgi validate deps

# Validate installation
apgi validate install
```

### Reporting

```bash
# Generate test report
apgi report test --format html

# Generate coverage report
apgi report coverage --format xml

# Generate system report
apgi report system

# Export documentation
apgi report docs --format pdf
```

### Deployment

```bash
# Build package
apgi deploy build

# Create distribution
apgi deploy dist

# Install locally
apgi deploy install

# Check deployment readiness
apgi deploy check
```

## Examples

### Basic Usage

```bash
# Run all tests with coverage
apgi-test run --coverage --coverage-report html

# Execute standard workflow
apgi workflow run-standard --output-dir results/

# Launch GUI
apgi gui

# Validate configuration
apgi config validate
```

### Advanced Usage

```bash
# Run performance tests in parallel
apgi-test run --category performance --parallel --workers 8 --timeout 600

# Create and run custom workflow
apgi config create custom_profile
apgi workflow run config/custom_workflow.yaml --config custom_profile

# Generate comprehensive report
apgi report test --format html --output-dir reports/
apgi report coverage --format xml
apgi report system
```

### CI/CD Integration

```bash
# CI test run with JUnit output
apgi-test run --junit-xml results.xml --coverage --coverage-xml

# Deployment validation
apgi validate system
apgi validate deps
apgi deploy check

# Artifact generation
apgi report test --format html
apgi report coverage --format xml
```

## Exit Codes

|  Code  | Meaning |  Description  |
| ------ |---------| ------------- |

|  0  | Success |  Command completed successfully  |
|  1  | General Error |  Unspecified error occurred  |
|  2  | Invalid Usage |  Invalid command-line arguments  |
|  3  | Configuration Error |  Configuration file or settings invalid  |
|  4  | Dependency Error |  Required dependencies missing  |
|  5  | Test Failure |  One or more tests failed  |
|  6  | Validation Error |  Data or system validation failed  |
|  7  | Timeout |  Operation timed out  |
|  8  | Interrupted |  Operation was interrupted  |
|  9  | Permission Denied |  Insufficient permissions  |

## Environment Variables

|  Variable  | Description |  Default  |
| ---------- |-------------| --------- |

|  `APGI_CONFIG`  | Configuration file path |  `config/default.yaml`  |
|  `APGI_LOG_LEVEL`  | Logging level |  `INFO`  |
|  `APGI_OUTPUT_DIR`  | Output directory |  `output/`  |
|  `APGI_DATA_DIR`  | Data directory |  `data/`  |
|  `APGI_TEST_TIMEOUT`  | Test timeout (seconds) |  `300`  |
|  `APGI_PARALLEL_WORKERS`  | Number of parallel workers |  `auto`  |

## Configuration Files

The CLI uses YAML configuration files with the following structure:

```yaml
# APGI CLI Configuration
cli:
  log_level: INFO
  output_dir: output/
  parallel_workers: 4
  timeout: 300

testing:
  coverage: true
  coverage_format: html
  fail_fast: false
  reruns: 0

workflow:
  default_config: config/workflow.yaml
  parallel_execution: true
  save_intermediate: true

deployment:
  build_dir: build/
  dist_dir: dist/
  package_name: apgi-framework
```

## Troubleshooting

### Common Issues

**Command not found**: Ensure APGI is properly installed and in PATH
**Import errors**: Check Python environment and dependencies
**Permission errors**: Run with appropriate permissions
**Timeout errors**: Increase timeout values or check system performance

### Getting Help

```bash
# Show general help
apgi --help

# Show command-specific help
apgi test --help
apgi workflow --help

# Enable debug logging
apgi --log-level DEBUG command
```

For more detailed documentation, see the [User Guide](USER-GUIDE.md) and [API Reference](api/index.md).
