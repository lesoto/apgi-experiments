# APGI Experiments Guide

This guide provides comprehensive instructions for running experiments in the APGI (Active Precision and Gating Integration) framework.

## Table of Contents

1. [Overview](#overview)
2. [Experiment Registry](#experiment-registry)
3. [Running Experiments](#running-experiments)
   - [Using the GUI](#using-the-gui)
   - [Using Command Line](#using-command-line)
   - [Using Python API](#using-python-api)
4. [Available Experiments](#available-experiments)
5. [Configuration Parameters](#configuration-parameters)
6. [Output and Results](#output-and-results)
7. [Troubleshooting](#troubleshooting)

## Overview

The APGI framework includes 24 cognitive experiments that test various aspects of consciousness, attention, memory, decision-making, and perception. Each experiment integrates APGI parameters (θₜ threshold, π precision, ε prediction error, β inverse temperature) to model cognitive processes.

## Experiment Registry

All experiments are registered in `/tools/run_experiments.py` with the following structure:

```python
EXPERIMENTS = {
    "experiment_name": "module.path.to.experiment",
    # ... 24 total experiments
}
```

## Running Experiments

### Using the GUI

The easiest way to run experiments is through the graphical interface:

#### Launching the GUI

```bash
# From the project root directory
python experiment_registry_gui.py
```

#### GUI Features

- **Experiment List**: Browse all 24 available experiments
- **Experiment Details**: View documentation and module information
- **Parameter Configuration**: Set participants, trials, and output file
- **Individual Execution**: Run selected experiments
- **Batch Execution**: Run all experiments sequentially
- **Real-time Output**: Monitor progress and results
- **Status Tracking**: Track success/failure status of each experiment

#### GUI Usage Steps

1. **Launch the GUI**: Run `python experiment_registry_gui.py`
2. **Select Experiment**: Click on an experiment from the list
3. **Configure Parameters**: Set number of participants and trials
4. **Choose Output**: (Optional) Select output file for results
5. **Run Experiment**: Click "Run Selected Experiment" or "Run All Experiments"
6. **Monitor Progress**: View real-time output in the console

### Using Command Line

You can run experiments directly from the command line:

#### Basic Usage

```bash
# Run a specific experiment
python tools/run_experiments.py experiment_name

# With parameters
python tools/run_experiments.py experiment_name --n_participants 10 --n_trials 50

# With output file
python tools/run_experiments.py experiment_name --n_participants 10 --n_trials 50 --output results.csv
```

#### Available Experiments (Command Line)

```bash
# Decision Making
python tools/run_experiments.py iowa_gambling_task
python tools/run_experiments.py probabilistic_category_learning

# Attention
python tools/run_experiments.py attentional_blink
python tools/run_experiments.py change_blindness
python tools/run_experiments.py visual_search
python tools/run_experiments.py posner_cueing

# Conflict Monitoring
python tools/run_experiments.py stroop_effect
python tools/run_experiments.py simon_effect
python tools/run_experiments.py eriksen_flanker

# Consciousness
python tools/run_experiments.py masking
python tools/run_experiments.py binocular_rivalry
python tools/run_experiments.py inattentional_blindness

# Memory
python tools/run_experiments.py dual_n_back
python tools/run_experiments.py sternberg_memory
python tools/run_experiments.py working_memory_span
python tools/run_experiments.py drm_false_memory

# Executive Control
python tools/run_experiments.py go_no_go
python tools/run_experiments.py stop_signal

# Perception
python tools/run_experiments.py navon_task
python tools/run_experiments.py multisensory_integration

# Learning
python tools/run_experiments.py serial_reaction_time
python tools/run_experiments.py artificial_grammar_learning

# Timing and Navigation
python tools/run_experiments.py time_estimation
python tools/run_experiments.py virtual_navigation
```

#### Command Line Parameters

- `--n_participants`: Number of participants to simulate (default: 10)
- `--n_trials`: Number of trials per condition (default: 50)
- `--output`: Output file path for results (CSV format)

### Using Python API

You can also run experiments programmatically:

#### Basic API Usage

```python
from tools.run_experiments import run_experiment

# Run a single experiment
result = run_experiment('iowa_gambling_task', n_participants=20, n_trials=100)

# Run with output file
result = run_experiment('stroop_effect', 
                       n_participants=15, 
                       n_trials=60,
                       output_file='stroop_results.csv')

# Access results
print(f"Experiment type: {type(result)}")
print(f"Participant data: {result.participant_data}")
```

#### Advanced API Usage

```python
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tools.run_experiments import run_experiment, EXPERIMENTS

# Run multiple experiments
experiments_to_run = ['iowa_gambling_task', 'stroop_effect', 'dual_n_back']
results = {}

for exp_name in experiments_to_run:
    try:
        result = run_experiment(exp_name, n_participants=10, n_trials=30)
        results[exp_name] = result
        print(f"✓ {exp_name} completed successfully")
    except Exception as e:
        print(f"✗ {exp_name} failed: {e}")
        results[exp_name] = None

# Process results
for exp_name, result in results.items():
    if result:
        print(f"\n{exp_name} Summary:")
        print(f"  Participants: {len(result.participant_data)}")
        # Access specific experiment data
        if exp_name == 'iowa_gambling_task':
            print(f"  Average reward: {result.participant_data[0]['average_reward']}")
        elif exp_name == 'stroop_effect':
            print(f"  Average reaction time: {result.participant_data[0]['average_reaction_time']}")
        elif exp_name == 'dual_n_back':
            print(f"  Average accuracy: {result.participant_data[0]['average_accuracy']}")
```

## Available Experiments

### Decision Making (2 experiments)

1. **Iowa Gambling Task** (`iowa_gambling_task`) - Decision making under uncertainty
2. **Probabilistic Category Learning** (`probabilistic_category_learning`) - Category learning with feedback

### Attention (4 experiments)

3. **Attentional Blink** (`attentional_blink`) - Temporal attention limitations
4. **Change Blindness** (`change_blindness`) - Visual change detection
5. **Visual Search** (`visual_search`) - Feature and conjunction search
6. **Posner Cueing** (`posner_cueing`) - Spatial attention orienting

### Conflict Monitoring (3 experiments)

7. **Stroop Effect** (`stroop_effect`) - Interference in word-color processing
8. **Simon Effect** (`simon_effect`) - Spatial stimulus-response conflict
9. **Eriksen Flanker** (`eriksen_flanker`) - Response inhibition and conflict

### Consciousness (3 experiments)

10. **Masking** (`masking`) - Visual masking and consciousness thresholds
11. **Binocular Rivalry** (`binocular_rivalry`) - Competing visual perceptions
12. **Inattentional Blindness** (`inattentional_blindness`) - Failure to see unexpected stimuli

### Memory (4 experiments)

13. **Dual N-Back** (`dual_n_back`) - Working memory updating
14. **Sternberg Memory** (`sternberg_memory`) - Memory scanning and retrieval
15. **Working Memory Span** (`working_memory_span`) - Working memory capacity
16. **DRM False Memory** (`drm_false_memory`) - False memory creation

### Executive Control (2 experiments)

17. **Go/No-Go** (`go_no_go`) - Response inhibition
18. **Stop Signal** (`stop_signal`) - Reactive inhibition

### Perception (2 experiments)
19. **Navon Task** (`navon_task`) - Global vs. local processing
20. **Multisensory Integration** (`multisensory_integration`) - Cross-modal processing

### Learning (2 experiments)
21. **Serial Reaction Time** (`serial_reaction_time`) - Implicit sequence learning
22. **Artificial Grammar Learning** (`artificial_grammar_learning`) - Implicit pattern learning

### Timing and Navigation (2 experiments)
23. **Time Estimation** (`time_estimation`) - Temporal perception
24. **Virtual Navigation** (`virtual_navigation`) - Spatial navigation and memory

## Configuration Parameters

### Common Parameters

All experiments support these common parameters:

- **n_participants** (int, default: 10): Number of simulated participants
- **n_trials** (int, default: 50): Number of trials per condition
- **output_file** (str, optional): Path to save results CSV file

### APGI Parameters

Experiments can be configured with APGI-specific parameters:

- **theta_base** (float, default: 5.0): Base ignition threshold
- **sigma_pe** (float, default: 1.0): Prediction error precision
- **sigma_pi** (float, default: 1.0): Interoceptive precision
- **beta** (float, default: 1.0): Inverse temperature parameter

### Experiment-Specific Parameters

Each experiment may have additional parameters:

```python
# Example: Iowa Gambling Task specific parameters
result = run_experiment('iowa_gambling_task',
                       n_participants=20,
                       n_trials=100,
                       deck_rewards={'A': 100, 'B': 100, 'C': 50, 'D': 50},
                       penalty_probabilities={'A': 0.5, 'B': 0.1, 'C': 0.5, 'D': 0.1})

# Example: DRM False Memory specific parameters
result = run_experiment('drm_false_memory',
                       n_participants=15,
                       n_trials=8,  # Number of word lists
                       words_per_list=12,
                       lure_probability=0.25)
```

## Output and Results

### Data Structure

Experiments return structured data with the following components:

```python
result = run_experiment('experiment_name')

# Access participant data
for participant_id, data in result.participant_data.items():
    trials = data['trials']  # List of trial dictionaries
    summary = data['summary']  # Participant summary statistics
    
# Access overall results
results_df = result.results  # Pandas DataFrame with all trial data
```

### Trial Data Structure

Each trial contains:

```python
{
    'participant_id': int,
    'trial_number': int,
    'condition': str,
    'response': any,
    'accuracy': int,  # 0 or 1
    'reaction_time_ms': int,
    'confidence': float,
    'timestamp': float,
    'surprise': float,  # APGI parameter
    'ignition_probability': float,  # APGI parameter
    'somatic_marker': float,  # APGI parameter
    'precision': float  # APGI parameter
}
```

### Summary Statistics

Participant summaries include:

```python
{
    'total_trials': int,
    'accuracy': float,
    'mean_reaction_time': float,
    'mean_confidence': float,
    'mean_surprise': float,
    'mean_ignition_probability': float,
    'condition_performance': {...}  # Condition-specific metrics
}
```

### Saving Results

Results can be saved to CSV files:

```python
# Via parameter
result = run_experiment('experiment_name', output_file='results.csv')

# Via method
result.save_data('results.csv')

# Access DataFrame directly
df = result.results
df.to_csv('custom_results.csv', index=False)
```

## Troubleshooting

### Common Issues

#### 1. Import Errors

```
ModuleNotFoundError: No module named 'research.cognitive_tasks.experiments...'
```

**Solution**: Ensure you're running from the project root directory and the project structure is intact.

#### 2. Runtime Errors

Some experiments may have runtime issues:

- **attentional_blink**: String to numeric conversion error
- **change_blindness**: Missing 'alternations_used' attribute
- **masking**: Uninitialized 'base_confidence' variable
- **serial_reaction_time**: Missing 'current_response_data' attribute
- **artificial_grammar_learning**: Missing 'length' attribute

**Solution**: These are known issues. Use the GUI to identify which experiments fail and check the error messages.

#### 3. GUI Not Starting

```
_tkinter.TclError: no display name and no $DISPLAY environment variable
```

**Solution**: This occurs in headless environments. Use command-line or API methods instead.

#### 4. Memory Issues

Large experiments with many participants may consume significant memory.

**Solution**: Reduce participant count or run experiments individually.

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run experiment
result = run_experiment('experiment_name', n_participants=1, n_trials=5)
```

### Performance Tips

1. **Start Small**: Test with 1-2 participants and few trials first
2. **Use GUI for Testing**: The GUI provides real-time feedback
3. **Batch Process**: Run multiple experiments sequentially rather than in parallel
4. **Monitor Memory**: Watch system memory usage with large experiments

### Getting Help

1. **Check GUI Output**: The GUI console shows detailed error messages
2. **Review Experiment Code**: Each experiment has detailed documentation
3. **Check Parameters**: Ensure all required parameters are provided
4. **Test Individually**: Run problematic experiments in isolation

## Quick Start Examples

### Example 1: First Experiment

```bash
# Launch GUI
python experiment_registry_gui.py

# Or command line
python tools/run_experiments.py iowa_gambling_task --n_participants 5 --n_trials 20
```

### Example 2: Batch Testing

```python
from tools.run_experiments import run_experiment

# Test multiple experiments with small parameters
test_experiments = ['stroop_effect', 'go_no_go', 'dual_n_back']
for exp in test_experiments:
    try:
        result = run_experiment(exp, n_participants=2, n_trials=10)
        print(f"✓ {exp} works")
    except Exception as e:
        print(f"✗ {exp} failed: {e}")
```

### Example 3: Research Study

```python
# Full study with multiple conditions
result = run_experiment('iowa_gambling_task',
                       n_participants=30,
                       n_trials=100,
                       output_file='gambling_study_results.csv')

# Access specific metrics
for participant_id, data in result.participant_data.items():
    summary = data['summary']
    print(f"Participant {participant_id}:")
    print(f"  Final Score: {summary.get('final_score', 0)}")
    print(f"  Advantageous Selections: {summary.get('advantageous_deck_percentage', 0):.1f}%")
```

This guide provides everything needed to effectively run and analyze experiments in the APGI framework. For specific experiment details, refer to the individual experiment documentation in their respective modules.
