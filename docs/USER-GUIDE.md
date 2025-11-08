# IPI Framework Falsification Testing System - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [GUI User Guide](#gui-user-guide)
4. [CLI User Guide](#cli-user-guide)
5. [Understanding Results](#understanding-results)
6. [Common Workflows](#common-workflows)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

## Introduction

The IPI (Interoceptive Predictive Integration) Framework Falsification Testing System is a comprehensive platform for testing the predictions of the IPI Framework through systematic falsification testing. This guide will help you:

- Run falsification tests using the GUI or CLI
- Configure experimental parameters
- Interpret test results
- Troubleshoot common issues
- Follow best practices for rigorous testing

### Quick Navigation

**New to the system?** Start with the [Quick Start Guide](QUICK_START_GUIDE.md) to get running in 5 minutes.

**Using the GUI?** See the [GUI Visual Guide](GUI_VISUAL_GUIDE.md) for a visual walkthrough with diagrams.

**Need help?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues and solutions.


### What is Falsification Testing?

Falsification testing is a scientific methodology where we attempt to disprove a theory by identifying conditions under which its predictions fail. For the IPI Framework, we test four primary falsification criteria:

1. **Primary Falsification**: Full ignition signatures without consciousness

2. **Consciousness Without Ignition**: Conscious reports without ignition signatures

3. **Threshold Insensitivity**: Ignition threshold unaffected by neuromodulation

4. **Soma-Bias Absence**: No preferential weighting of interoceptive signals

## Getting Started

### Installation

Ensure you have Python 3.8+ installed, then install dependencies:

```bash
pip install -r requirements.txt
```

### Quick Start

#### Using Python API

```python
from ipi_framework.main_controller import MainApplicationController

# Initialize system
controller = MainApplicationController()
controller.initialize_system()

# Run primary falsification test
tests = controller.get_falsification_tests()
result = tests['primary'].run_test(n_trials=1000)

# View results
print(f"Falsified: {result.is_falsified}")
print(f"Confidence: {result.confidence_level:.3f}")

# Cleanup
controller.shutdown_system()
```

#### Using CLI

```bash
# Run primary falsification test
python -m ipi_framework.cli run-test primary --trials 1000

# View system status
python -m ipi_framework.cli status

# Validate system
python -m ipi_framework.cli validate-system
```

#### Using GUI

```bash
# Launch GUI application
python launch_gui.py
```

## GUI User Guide

### Main Window Overview

The GUI provides an intuitive interface for running falsification tests and viewing results.

#### Components

1. **Test Selection Panel** (Left): Choose which falsification test to run
2. **Parameter Configuration Panel** (Center): Set IPI parameters and experimental settings
3. **Results Display Panel** (Right): View test results and visualizations
4. **Progress Panel** (Bottom): Monitor test execution progress
5. **Menu Bar** (Top): Access file operations, settings, and help

### Running a Test

#### Step 1: Select Test Type

Click on one of the test buttons in the left panel:
- **Primary Falsification Test**: Tests for full ignition without consciousness
- **Consciousness Without Ignition**: Tests for consciousness without ignition signatures
- **Threshold Insensitivity**: Tests neuromodulatory effects on threshold
- **Soma-Bias Test**: Tests interoceptive vs exteroceptive weighting

#### Step 2: Configure Parameters

In the Parameter Configuration Panel, set:

**IPI Parameters:**
- **Exteroceptive Precision** (0.1-10.0): Precision of external sensory signals
  - Default: 2.0
  - Higher values = more reliable external signals
  
- **Interoceptive Precision** (0.1-10.0): Precision of internal bodily signals
  - Default: 1.5
  - Higher values = more reliable internal signals
  
- **Threshold** (0.5-10.0): Ignition threshold for conscious access
  - Default: 3.5
  - Lower values = easier ignition
  
- **Steepness** (0.1-5.0): Sigmoid steepness for ignition probability
  - Default: 2.0
  - Higher values = sharper threshold
  
- **Somatic Gain** (0.1-5.0): Gain for somatic marker modulation
  - Default: 1.3
  - Higher values = stronger emotional modulation

**Experimental Settings:**
- **Number of Trials**: How many trials to simulate (100-10000)
  - Recommended: 1000 for standard tests
  - Use 2000+ for high-power analyses
  
- **Number of Participants**: For multi-participant tests (10-1000)
  - Recommended: 100 for soma-bias test
  
- **Random Seed**: For reproducible results (optional)
  - Leave empty for random seed
  - Use specific value (e.g., 42) for reproducibility

#### Step 3: Run Test

1. Click the **"Run Test"** button
2. Monitor progress in the Progress Panel

3. Wait for test completion (may take 30 seconds to several minutes)

#### Step 4: View Results

Results appear in the Results Display Panel:

**Summary Section:**
- Falsification status (FALSIFIED / NOT FALSIFIED)
- Confidence level (0-1)
- Statistical significance (p-value)
- Effect size (Cohen's d)
- Statistical power

**Detailed Metrics:**
- Trial-by-trial breakdown
- Neural signature statistics
- Consciousness assessment metrics

**Visualizations:**
- Distribution plots
- Time series (if applicable)
- Statistical summaries

### Saving and Loading Results

#### Saving Results

1. After test completion, click **File → Save Results**
2. Choose location and filename
3. Results saved in JSON format with metadata

#### Loading Previous Results

1. Click **File → Load Results**
2. Select result file (.json)
3. Results displayed in Results Panel

### Exporting Data

#### Export Options

1. Click **File → Export**
2. Choose format:
   - **JSON**: Full data with metadata
   - **CSV**: Tabular data for spreadsheet analysis
   - **HDF5**: Large datasets with compression
   - **PDF Report**: Publication-ready report

### Batch Processing

For running multiple configurations:

1. Click **Tools → Batch Processing**
2. Define parameter ranges:
   - Select parameters to vary
   - Set min, max, and step values
3. Click **"Start Batch"**
4. Monitor progress for all configurations
5. View comparative results when complete

## CLI User Guide

### Basic Commands

#### Run Individual Test

```bash
# Primary falsification test
python -m ipi_framework.cli run-test primary --trials 1000

# With custom parameters
python -m ipi_framework.cli run-test primary \
    --trials 2000 \
    --seed 42 \
    --output-dir results/my_test
```

#### Run Batch Tests

```bash
# Run all tests
python -m ipi_framework.cli run-batch --all-tests

# Run specific tests
python -m ipi_framework.cli run-batch \
    --tests primary consciousness-without-ignition

# Parallel execution (experimental)
python -m ipi_framework.cli run-batch --all-tests --parallel
```

#### Configuration Management

```bash
# Generate default configuration
python -m ipi_framework.cli generate-config --output config.json

# Generate minimal configuration
python -m ipi_framework.cli generate-config \
    --template minimal \
    --output minimal_config.json

# Generate comprehensive configuration
python -m ipi_framework.cli generate-config \
    --template comprehensive \
    --output full_config.json
```

#### System Management

```bash
# Check system status
python -m ipi_framework.cli status

# Validate system components
python -m ipi_framework.cli validate-system

# Detailed validation
python -m ipi_framework.cli validate-system --detailed
```

#### Parameter Configuration

```bash
# Set IPI parameters
python -m ipi_framework.cli set-params \
    --extero-precision 2.5 \
    --intero-precision 2.0 \
    --threshold 3.0 \
    --steepness 2.5
```

### Using Configuration Files

#### Create Configuration File

```json
{
  "ipi_parameters": {
    "extero_precision": 2.0,
    "intero_precision": 1.5,
    "threshold": 3.5,
    "steepness": 2.0,
    "somatic_gain": 1.3
  },
  "experimental_config": {
    "n_trials": 1000,
    "n_participants": 100,
    "random_seed": 42,
    "output_directory": "results",
    "log_level": "INFO"
  }
}
```

#### Use Configuration File

```bash
# Run test with configuration
python -m ipi_framework.cli run-test primary --config config.json

# Run batch with configuration
python -m ipi_framework.cli run-batch --all-tests --config config.json
```

### Advanced CLI Usage

#### Logging Control

```bash
# Set log level
python -m ipi_framework.cli run-test primary \
    --log-level DEBUG \
    --trials 1000

# Available levels: DEBUG, INFO, WARNING, ERROR
```

#### Output Directory Management

```bash
# Specify output directory
python -m ipi_framework.cli run-test primary \
    --output-dir results/experiment_001 \
    --trials 1000
```

## Understanding Results

### Falsification Result Structure

Every test returns a `FalsificationResult` with:

```python
FalsificationResult(
    test_type: str,              # Type of test run
    is_falsified: bool,          # Whether framework was falsified
    confidence_level: float,     # Confidence in result (0-1)
    effect_size: float,          # Cohen's d effect size
    p_value: float,              # Statistical significance
    statistical_power: float,    # Power of the test (0-1)
    replication_count: int,      # Number of replications
    detailed_results: dict       # Additional metrics
)
```

### Interpreting Falsification Status

#### NOT FALSIFIED (is_falsified = False)

**Meaning**: The test did not find evidence contradicting the IPI Framework.

**Interpretation**:
- Framework predictions held under test conditions
- No instances of the falsification criterion were observed
- Framework remains viable under these parameters

**Example**: Primary test shows no cases of full ignition signatures without consciousness.

#### FALSIFIED (is_falsified = True)

**Meaning**: The test found evidence contradicting the IPI Framework.

**Interpretation**:
- Framework predictions violated under test conditions
- Falsification criterion was met
- Framework may need revision or has boundary conditions

**Example**: Primary test shows multiple cases of full ignition without consciousness.

### Statistical Metrics

#### Confidence Level

- **Range**: 0.0 to 1.0
- **Interpretation**:
  - < 0.5: Low confidence in result
  - 0.5-0.7: Moderate confidence
  - 0.7-0.9: High confidence
  - > 0.9: Very high confidence

#### P-value

- **Range**: 0.0 to 1.0
- **Interpretation**:
  - < 0.001: Extremely significant
  - < 0.01: Highly significant
  - < 0.05: Significant (standard threshold)
  - ≥ 0.05: Not significant

#### Effect Size (Cohen's d)

- **Range**: -∞ to +∞ (typically -3 to +3)
- **Interpretation**:
  - |d| < 0.2: Small effect
  - 0.2 ≤ |d| < 0.5: Small to medium effect
  - 0.5 ≤ |d| < 0.8: Medium to large effect
  - |d| ≥ 0.8: Large effect

#### Statistical Power

- **Range**: 0.0 to 1.0
- **Interpretation**:
  - < 0.5: Underpowered (increase sample size)
  - 0.5-0.8: Adequate power
  - ≥ 0.8: Well-powered (standard target)
  - ≥ 0.95: Very well-powered

### Test-Specific Interpretations

#### Primary Falsification Test

**What it tests**: Can full ignition signatures occur without consciousness?

**Falsified if**: Observe P3b > 5μV, gamma PLV > 0.3, BOLD Z > 3.1, PCI > 0.4, but no subjective report and chance-level forced choice.

**Implications**:
- **Not Falsified**: Ignition signatures reliably predict consciousness
- **Falsified**: Ignition can occur without consciousness (decisive falsification)

#### Consciousness Without Ignition Test

**What it tests**: Can consciousness occur without ignition signatures?

**Falsified if**: >20% of conscious reports occur with subthreshold signatures (P3b < 2μV, gamma PLV < 0.15, PCI < 0.3).

**Implications**:
- **Not Falsified**: Consciousness requires ignition
- **Falsified**: Consciousness can occur via alternative mechanisms

#### Threshold Insensitivity Test

**What it tests**: Does neuromodulation affect ignition threshold?

**Falsified if**: Pharmacological manipulation (propranolol, L-DOPA, SSRIs, physostigmine) fails to modulate threshold.

**Implications**:
- **Not Falsified**: Threshold is neuromodulatory-sensitive as predicted
- **Falsified**: Threshold is fixed, contradicting dynamic threshold theory

#### Soma-Bias Test

**What it tests**: Are interoceptive signals preferentially weighted?

**Falsified if**: β (interoceptive/exteroceptive weighting ratio) approaches 1.0 (0.95-1.05), indicating no bias.

**Implications**:
- **Not Falsified**: Interoceptive signals have special status
- **Falsified**: No preferential interoceptive weighting

## Common Workflows

### Workflow 1: Basic Falsification Testing

**Goal**: Run a single falsification test with default parameters.

**Steps**:
1. Launch GUI or use CLI
2. Select primary falsification test
3. Use default parameters
4. Run test with 1000 trials
5. Review results
6. Save results for records

**CLI Commands**:
```bash
python -m ipi_framework.cli run-test primary --trials 1000
```

### Workflow 2: Parameter Sensitivity Analysis

**Goal**: Explore how different parameter values affect falsification.

**Steps**:
1. Identify parameter of interest (e.g., threshold)
2. Define range of values to test
3. Run batch processing across range
4. Compare results
5. Identify critical parameter values

**Example Script**: See `examples/02_batch_processing_configurations.py`

### Workflow 3: Comprehensive Framework Evaluation

**Goal**: Test all falsification criteria systematically.

**Steps**:
1. Run all four falsification tests
2. Use consistent parameters across tests
3. Ensure adequate statistical power (n ≥ 1000)
4. Document all results
5. Generate comprehensive report

**CLI Commands**:
```bash
python -m ipi_framework.cli run-batch --all-tests --config config.json
```

### Workflow 4: Reproducible Research

**Goal**: Ensure results can be replicated exactly.

**Steps**:
1. Create configuration file with all parameters
2. Set random seed for reproducibility
3. Document software versions
4. Run tests with configuration
5. Save configuration with results
6. Share configuration for replication

**Configuration Example**:
```json
{
  "ipi_parameters": {
    "extero_precision": 2.0,
    "intero_precision": 1.5,
    "threshold": 3.5,
    "steepness": 2.0,
    "somatic_gain": 1.3
  },
  "experimental_config": {
    "n_trials": 2000,
    "random_seed": 42,
    "output_directory": "results/replication_study"
  }
}
```

### Workflow 5: Custom Analysis

**Goal**: Perform custom analysis on saved results.

**Steps**:
1. Run experiments and save results

2. Load results using Python API

3. Perform custom statistical analyses

4. Generate custom visualizations

5. Export analysis report

**Example Script**: See `examples/03_custom_analysis_saved_results.py`

## Troubleshooting

### Common Issues and Solutions

#### Issue: "System not initialized" Error

**Symptoms**: Error message when trying to run tests.

**Cause**: System components not properly initialized.

**Solution**:
```python
controller = MainApplicationController()
controller.initialize_system()  # Don't forget this!
```

#### Issue: Low Statistical Power Warning

**Symptoms**: Warning about statistical power < 0.8.

**Cause**: Insufficient sample size (too few trials).

**Solution**:
- Increase number of trials (try 2000+)
- Check power analysis recommendations
- Consider effect size when determining sample size

#### Issue: Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError`.

**Cause**: Python path not configured or dependencies missing.

**Solution**:
```bash
# Install dependencies
pip install -r requirements.txt

# Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/ipi_framework"
```

#### Issue: GUI Not Launching

**Symptoms**: GUI window doesn't appear or crashes.

**Cause**: Missing GUI dependencies or display issues.

**Solution**:
```bash
# Install GUI dependencies
pip install PyQt5

# Check display
echo $DISPLAY  # Should show :0 or similar

# Try launching with verbose output
python launch_gui.py --verbose
```

#### Issue: Results Not Saving

**Symptoms**: Results don't appear in output directory.

**Cause**: Permission issues or invalid output path.

**Solution**:
```bash
# Check permissions
ls -la results/

# Create directory if needed
mkdir -p results

# Specify absolute path
python -m ipi_framework.cli run-test primary \
    --output-dir /absolute/path/to/results
```

#### Issue: Inconsistent Results

**Symptoms**: Different results on repeated runs.

**Cause**: Random seed not set.

**Solution**:
```python
# Set random seed for reproducibility
controller.config_manager.update_experimental_config(random_seed=42)
```

#### Issue: Test Takes Too Long

**Symptoms**: Test execution exceeds expected time.

**Cause**: Too many trials or complex simulations.

**Solution**:
- Reduce number of trials for initial testing
- Use batch processing for multiple configurations
- Check system resources (CPU, memory)
- Consider parallel processing (experimental)

### Getting Help

#### Check System Status

```bash
python -m ipi_framework.cli status
python -m ipi_framework.cli validate-system --detailed
```

#### Enable Debug Logging

```bash
python -m ipi_framework.cli run-test primary \
    --log-level DEBUG \
    --trials 100
```

#### Review Log Files

```bash
# Check application logs
cat results/ipi_framework.log

# Check recent errors
tail -n 50 results/ipi_framework.log | grep ERROR
```

## Best Practices

### Experimental Design

1. **Use Adequate Sample Sizes**
   - Minimum 1000 trials for standard tests
   - 2000+ trials for high-power analyses
   - 100+ participants for multi-participant tests

2. **Set Random Seeds for Reproducibility**
   - Always set random seed for published results
   - Document seed value in methods section
   - Use different seeds for independent replications

3. **Run System Validation First**
   - Validate system before important experiments
   - Check all components are functioning
   - Verify parameter ranges are valid

4. **Save Complete Configuration**
   - Save configuration file with results
   - Document all parameter values
   - Include software version information

### Statistical Analysis

1. **Check Statistical Power**
   - Ensure power ≥ 0.8 for conclusive results
   - Increase sample size if underpowered
   - Report power in results

2. **Report Effect Sizes**
   - Always report effect sizes, not just p-values
   - Use Cohen's d for standardized comparison
   - Interpret practical significance

3. **Apply Multiple Comparisons Corrections**
   - Use appropriate corrections for multiple tests
   - Document correction method used
   - Report both corrected and uncorrected values

4. **Consider Replication**
   - Run multiple independent replications
   - Report consistency across replications
   - Use meta-analytic approaches for synthesis

### Data Management

1. **Organize Results Systematically**
   ```
   results/
   ├── experiment_001/
   │   ├── config.json
   │   ├── primary_result_20250107.json
   │   └── analysis_report.json
   ├── experiment_002/
   │   └── ...
   └── batch_processing/
       └── ...
   ```

2. **Use Descriptive Filenames**
   - Include date, test type, and key parameters
   - Example: `primary_test_threshold3.5_20250107.json`

3. **Backup Important Results**

   - Regularly backup results directory
   - Use version control for configurations
   - Archive completed experiments

4. **Document Experiments**
   - Keep lab notebook or README
   - Document rationale for parameter choices
   - Note any anomalies or issues

### Reporting Results

1. **Include All Relevant Metrics**
   - Falsification status
   - Confidence level
   - P-value and effect size
   - Statistical power
   - Sample size

2. **Provide Context**
   - Explain parameter choices
   - Describe experimental conditions
   - Relate to theoretical predictions

3. **Be Transparent**
   - Report all tests run, not just significant ones
   - Disclose any data exclusions
   - Share data and code when possible

4. **Interpret Cautiously**
   - Distinguish statistical from practical significance
   - Consider alternative explanations
   - Acknowledge limitations

---

## Additional Resources

- **Examples**: See `examples/` directory for working code examples
- **API Documentation**: Check module docstrings in `ipi_framework/`
- **Theoretical Background**: See `IPI-Falsification.md`
- **CLI Reference**: Run `python -m ipi_framework.cli --help`
- **Error Handling**: See `docs/ERROR_HANDLING_QUICK_REFERENCE.md`

## Support

For issues, questions, or contributions:
- Check existing documentation first
- Review examples for similar use cases
- Run system validation to diagnose issues
- Enable debug logging for detailed information

---

**Version**: 1.0  
**Last Updated**: 2025-01-07  
**Maintainer**: IPI Framework Development Team
