# APGI Experiments Guide

This guide provides comprehensive instructions for running experiments in the APGI (Active Precision and Gating Integration) framework.

## Table of Contents

1. [Overview](#overview)
2. [Experiment Registry](#experiment-registry)
3. [Running Experiments](#running-experiments)
   - [Using the GUI](#using-the-gui)
   - [Using Command Line](#using-command-line)
   - [Using Python API](#using-python-api)
4. [Available Experiments](#available-experiments-command-line)
5. [Configuration Parameters](#command-line-parameters)
6. [Output and Results](#using-python-api)

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
python GUI-Experiment-Registry.py
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

1. **Launch the GUI**: Run `python GUI-Experiment-Registry.py`
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

The simulated participant strongly preferred Deck C, which is the most advantageous deck in the standard IGT.
