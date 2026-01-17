# APGI Framework CLI Reference

Complete command-line interface reference for the APGI Framework Falsification Testing System.

## Table of Contents

1. [Overview](#overview)
2. [Global Options](#global-options)
3. [Commands](#commands)
4. [Parameter Reference](#parameter-reference)
5. [Configuration Files](#configuration-files)
6. [Examples](#examples)
7. [Exit Codes](#exit-codes)

## Overview

The APGI Framework CLI provides comprehensive command-line access to all falsification testing capabilities.

### Basic Usage

```bash
python -m apgi_framework.cli [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Getting Help

```bash

# General help

python -m apgi_framework.cli --help

# Command-specific help

python -m apgi_framework.cli run-test --help
python -m apgi_framework.cli run-batch --help
```

## Global Options

Options that apply to all commands.

### --config, -c

Specify configuration file path.

```bash
python -m apgi_framework.cli --config config.json run-test primary
```

- **Type**: String (file path)
- **Default**: None
- **Required**: No

### --log-level, -l

Set logging verbosity level.

```bash
python -m apgi_framework.cli --log-level DEBUG run-test primary
```

- **Type**: Choice (DEBUG, INFO, WARNING, ERROR)
- **Default**: INFO
- **Required**: No

**Level Descriptions**:

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages only

### --output-dir, -o

Specify output directory for results.

```bash
python -m apgi_framework.cli --output-dir results/my_experiment run-test primary
```

**Type**: String (directory path)  
**Default**: "results"  
**Required**: No

## Commands

### run-test

Run an individual falsification test.

#### Syntax

```bash
python -m apgi_framework.cli run-test TEST_TYPE [OPTIONS]
```

#### Arguments

**TEST_TYPE** (required)

Type of falsification test to run.

**Choices**:

- `primary`: Primary falsification test (full ignition without consciousness)
- `consciousness-without-ignition`: Consciousness without ignition signatures
- `threshold-insensitivity`: Neuromodulatory threshold dynamics
- `soma-bias`: Interoceptive vs exteroceptive bias

#### Options

### --trials, -n

Number of trials to simulate.

```bash
python -m apgi_framework.cli run-test primary --trials 2000
```

**Type**: Integer  
**Range**: 100-10000  
**Default**: 1000  
**Required**: No

#### --participants, -p

Number of participants to simulate (for multi-participant tests).

```bash
python -m apgi_framework.cli run-test soma-bias --participants 200
```

**Type**: Integer  
**Range**: 10-1000  
**Default**: 100  
**Required**: No  
**Applicable to**: soma-bias test

#### --seed

Random seed for reproducibility.

```bash
python -m apgi_framework.cli run-test primary --seed 42
```

**Type**: Integer  
**Default**: None (random)  
**Required**: No

#### Examples

```bash

# Basic primary test

python -m apgi_framework.cli run-test primary

# High-power test with reproducibility

python -m apgi_framework.cli run-test primary --trials 5000 --seed 42

# Soma-bias test with many participants

python -m apgi_framework.cli run-test soma-bias --participants 500

# With custom output directory

python -m apgi_framework.cli run-test primary \
    --trials 2000 \
    --output-dir results/experiment_001
```

### run-batch

Run multiple falsification tests in batch mode.

#### Syntax

```bash
python -m apgi_framework.cli run-batch [OPTIONS]
```

#### Options

**--all-tests**

Run all available falsification tests.

```bash
python -m apgi_framework.cli run-batch --all-tests
```

**Type**: Flag  
**Default**: False  
**Required**: No (but either --all-tests or --tests must be specified)

**--tests**

Specify which tests to run.

```bash
python -m apgi_framework.cli run-batch --tests primary soma-bias
```

**Type**: List of choices  
**Choices**: primary, consciousness-without-ignition, threshold-insensitivity, soma-bias  
**Default**: None  
**Required**: No (but either --all-tests or --tests must be specified)

**--parallel**

Run tests in parallel (experimental feature).

```bash
python -m apgi_framework.cli run-batch --all-tests --parallel
```

**Type**: Flag  
**Default**: False  
**Required**: No  
**Note**: Experimental feature, may have stability issues

#### Examples

```bash

# Run all tests

python -m apgi_framework.cli run-batch --all-tests

# Run specific tests

python -m apgi_framework.cli run-batch --tests primary consciousness-without-ignition

# Run all tests with custom config

python -m apgi_framework.cli --config my_config.json run-batch --all-tests

# Parallel execution (experimental)

python -m apgi_framework.cli run-batch --all-tests --parallel
```

### generate-config

Generate a configuration file template.

#### Syntax

```bash
python -m apgi_framework.cli generate-config [OPTIONS]
```

#### Options

**--output**

Output file path for configuration.

```bash
python -m apgi_framework.cli generate-config --output my_config.json
```

**Type**: String (file path)  
**Default**: "apgi_config.json"  
**Required**: No

**--template**

Configuration template type.

```bash
python -m apgi_framework.cli generate-config --template comprehensive
```

**Type**: Choice  
**Choices**: default, minimal, comprehensive  
**Default**: default  
**Required**: No

**Template Descriptions**:

- **default**: Standard configuration with commonly used parameters
- **minimal**: Minimal configuration with only essential parameters
- **comprehensive**: Full configuration with all available options

#### Examples

```bash

# Generate default configuration

python -m apgi_framework.cli generate-config

# Generate minimal configuration

python -m apgi_framework.cli generate-config \
    --template minimal \
    --output minimal_config.json

# Generate comprehensive configuration

python -m apgi_framework.cli generate-config \
    --template comprehensive \
    --output full_config.json
```json

### validate-system

Validate system components and configuration.

#### Syntax

```bash
python -m apgi_framework.cli validate-system [OPTIONS]
```

#### Options

**--detailed**

Show detailed validation results for each component.

```bash
python -m apgi_framework.cli validate-system --detailed
```

**Type**: Flag  
**Default**: False  
**Required**: No

#### Examples

```bash

# Basic validation

python -m apgi_framework.cli validate-system

# Detailed validation

python -m apgi_framework.cli validate-system --detailed

# Validate with specific configuration

python -m apgi_framework.cli --config my_config.json validate-system --detailed
```

#### Output

**Simple Output**:
```
System Validation: PASS
```

**Detailed Output**:
```
============================================================
System Validation Results (Detailed)
============================================================
Mathematical Engine: PASS
Neural Simulators: PASS
Falsification Tests: PASS
Data Manager: PASS

Overall Status: PASS
============================================================
```

### status

Show current system status and configuration.

#### Syntax

```bash
python -m apgi_framework.cli status
```

#### Examples

```bash

# Show system status
python -m apgi_framework.cli status

# Show status with specific configuration
python -m apgi_framework.cli --config my_config.json status
```

#### Output

```
==================================================
APGI Framework System Status
==================================================
Initialized: YES
Components Registered: YES
Config Loaded: YES
Mathematical Engine Ready: YES
Neural Simulators Ready: YES
Falsification Tests Ready: YES
Data Manager Ready: YES
Last Updated: 2025-01-07T10:30:45
==================================================
```

### set-params

Set APGI parameter values.

#### Syntax

```bash
python -m apgi_framework.cli set-params [OPTIONS]
```

#### Options

**--extero-precision**

Set exteroceptive precision value.

```bash
python -m apgi_framework.cli set-params --extero-precision 2.5
```

**Type**: Float  
**Range**: 0.1-10.0  
**Default**: 2.0  
**Required**: No

**--intero-precision**

Set interoceptive precision value.

```bash
python -m apgi_framework.cli set-params --intero-precision 2.0
```

**Type**: Float  
**Range**: 0.1-10.0  
**Default**: 1.5  
**Required**: No

**--threshold**

Set ignition threshold value.

```bash
python -m apgi_framework.cli set-params --threshold 3.0
```

**Type**: Float  
**Range**: 0.5-10.0  
**Default**: 3.5  
**Required**: No

**--steepness**

Set sigmoid steepness value.

```bash
python -m apgi_framework.cli set-params --steepness 2.5
```

**Type**: Float  
**Range**: 0.1-5.0  
**Default**: 2.0  
**Required**: No

**--somatic-gain**

Set somatic marker gain value.

```bash
python -m apgi_framework.cli set-params --somatic-gain 1.5
```

**Type**: Float  
**Range**: 0.1-5.0  
**Default**: 1.3  
**Required**: No

#### Examples

```bash

# Set single parameter

python -m apgi_framework.cli set-params --threshold 3.0

# Set multiple parameters

python -m apgi_framework.cli set-params \
    --extero-precision 2.5 \
    --intero-precision 2.0 \
    --threshold 3.0

# Set all parameters

python -m apgi_framework.cli set-params \
    --extero-precision 2.5 \
    --intero-precision 2.0 \
    --threshold 3.0 \
    --steepness 2.5 \
    --somatic-gain 1.5
```

## Parameter Reference

### APGI Parameters

#### extero_precision

Precision (inverse variance) of exteroceptive (external sensory) prediction errors.

**Range**: 0.1 - 10.0  
**Default**: 2.0  
**Units**: Dimensionless (inverse variance)

**Interpretation**:

- Higher values = more reliable external sensory signals
- Lower values = noisier external signals
- Affects weighting in surprise calculation

#### intero_precision

Precision (inverse variance) of interoceptive (internal bodily) prediction errors.

**Range**: 0.1 - 10.0  
**Default**: 1.5  
**Units**: Dimensionless (inverse variance)

**Interpretation**:

- Higher values = more reliable internal bodily signals
- Lower values = noisier internal signals
- Affects weighting in surprise calculation

#### threshold

Ignition threshold for conscious access.

**Range**: 0.5 - 10.0  
**Default**: 3.5  
**Units**: Dimensionless (surprise units)

**Interpretation**:

- Higher values = harder to trigger ignition (more conservative)
- Lower values = easier to trigger ignition (more liberal)
- Critical parameter for conscious access

#### steepness

Steepness of sigmoid function for ignition probability.

**Range**: 0.1 - 5.0  
**Default**: 2.0  
**Units**: Dimensionless

**Interpretation**:

- Higher values = sharper threshold (more all-or-none)
- Lower values = gradual threshold (more graded)
- Affects transition from unconscious to conscious

#### somatic_gain

Gain factor for somatic marker modulation of interoceptive precision.

**Range**: 0.1 - 5.0  
**Default**: 1.3  
**Units**: Dimensionless (multiplicative factor)

**Interpretation**:

- Higher values = stronger emotional/motivational modulation
- Lower values = weaker modulation
- Affects context-dependent precision weighting

### Experimental Configuration Parameters

#### n_trials

Number of trials to simulate in a test.

**Range**: 100 - 10000  
**Default**: 1000  
**Units**: Count

**Recommendations**:

- 1000: Standard testing
- 2000+: High-power analyses
- 5000+: Publication-quality results

#### n_participants

Number of participants to simulate (for multi-participant tests).

**Range**: 10 - 1000  
**Default**: 100  
**Units**: Count

**Recommendations**:

- 100: Standard testing
- 200+: High-power analyses
- 500+: Publication-quality results

#### random_seed

Random seed for reproducible results.

**Range**: Any integer  
**Default**: None (random)  
**Units**: Integer

**Usage**:

- Set to specific value (e.g., 42) for reproducibility
- Leave unset for different results each run
- Document seed value in publications

#### output_directory

Directory path for saving results.

**Type**: String (directory path)  
**Default**: "results"

**Usage**:

- Use descriptive names (e.g., "results/experiment_001")
- Organize by experiment or date
- Ensure write permissions

#### log_level

Logging verbosity level.

**Type**: Choice  
**Choices**: DEBUG, INFO, WARNING, ERROR  
**Default**: INFO

**Usage**:

- DEBUG: Troubleshooting and development
- INFO: Normal operation
- WARNING: Important warnings only
- ERROR: Errors only

## Configuration Files

### File Format

Configuration files use JSON format.

### Structure

```json
{
  "apgi_parameters": {
    "extero_precision": 2.0,
    "intero_precision": 1.5,
    "extero_error": 1.2,
    "intero_error": 0.8,
    "somatic_gain": 1.3,
    "threshold": 3.5,
    "steepness": 2.0
  },
  "experimental_config": {
    "n_trials": 1000,
    "n_participants": 100,
    "random_seed": 42,
    "output_directory": "results",
    "log_level": "INFO",
    "save_intermediate": true,
    "p3b_threshold": 5.0,
    "gamma_plv_threshold": 0.3,
    "bold_z_threshold": 3.1,
    "pci_threshold": 0.4,
    "alpha_level": 0.05,
    "effect_size_threshold": 0.5,
    "power_threshold": 0.8
  }
}
```

### Using Configuration Files

```bash

# Run test with configuration

python -m apgi_framework.cli --config config.json run-test primary

# Generate configuration template

python -m apgi_framework.cli generate-config --output config.json

# Validate configuration

python -m apgi_framework.cli --config config.json validate-system
```

## Examples

### Example 1: Basic Workflow

```bash

# 1. Generate configuration

python -m apgi_framework.cli generate-config --output my_config.json

# 2. Validate system

python -m apgi_framework.cli --config my_config.json validate-system

# 3. Run primary test

python -m apgi_framework.cli --config my_config.json run-test primary --trials 1000

# 4. Check status

python -m apgi_framework.cli status
```

### Example 2: Batch Processing

```bash

# Run all tests with custom configuration

python -m apgi_framework.cli \
    --config my_config.json \
    --output-dir results/batch_001 \
    run-batch --all-tests
```

### Example 3: Parameter Exploration

```bash

# Test different threshold values

for threshold in 2.0 2.5 3.0 3.5 4.0; do
    python -m apgi_framework.cli set-params --threshold $threshold
    python -m apgi_framework.cli run-test primary \
        --trials 1000 \
        --output-dir results/threshold_$threshold
done
```

### Example 4: Reproducible Research

```bash

# Set up reproducible experiment

python -m apgi_framework.cli generate-config \
    --template comprehensive \
    --output experiment_config.json

# Edit config to set random_seed: 42

# Run with fixed seed

python -m apgi_framework.cli \
    --config experiment_config.json \
    run-test primary \
    --seed 42 \
    --trials 2000
```

### Example 5: High-Power Analysis

```bash

# Run high-power test with detailed logging

python -m apgi_framework.cli \
    --log-level DEBUG \
    --output-dir results/high_power \
    run-test primary \
    --trials 5000 \
    --seed 42
```

## Exit Codes

The CLI uses standard exit codes:

| Code | Meaning | Description |
|------|---------|-------------|
| 0 | Success | Command completed successfully |
| 1 | Error | General error occurred |
| 2 | Usage Error | Invalid command or arguments |
| 130 | Interrupted | User interrupted with Ctrl+C |

### Checking Exit Codes

```bash

# Bash

python -m apgi_framework.cli run-test primary
echo $?  # Prints exit code

# PowerShell

python -m apgi_framework.cli run-test primary
echo $LASTEXITCODE  # Prints exit code
```

### Using Exit Codes in Scripts

```bash
#!/bin/bash

# Run test and check result

if python -m apgi_framework.cli run-test primary --trials 1000; then
    echo "Test completed successfully"
else
    echo "Test failed with exit code $?"
    exit 1
fi
```

## Tips and Best Practices

### 1. Use Configuration Files

Store parameters in configuration files rather than command-line arguments for:

- Reproducibility
- Documentation
- Version control
- Sharing with collaborators

### 2. Set Random Seeds

Always set random seeds for:

- Published results
- Reproducible research
- Debugging
- Comparison across runs

### 3. Start with Validation

Always validate the system before important experiments:

```bash
python -m apgi_framework.cli validate-system --detailed
```

### 4. Use Descriptive Output Directories

Organize results with descriptive names:

```bash
python -m apgi_framework.cli run-test primary \
    --output-dir results/2025-01-07_primary_threshold_exploration
```

### 5. Enable Debug Logging for Troubleshooting

When encountering issues:

```bash
python -m apgi_framework.cli --log-level DEBUG run-test primary
```

### 6. Save Configurations with Results

Keep configuration files with results for documentation:

```bash

# Generate config

python -m apgi_framework.cli generate-config --output results/experiment_001/config.json

# Run with that config

python -m apgi_framework.cli \
    --config results/experiment_001/config.json \
    --output-dir results/experiment_001 \
    run-test primary
```

---

**Version**: 1.0  
**Last Updated**: 2025-01-07  
**See Also**: USER_GUIDE.md, examples/
