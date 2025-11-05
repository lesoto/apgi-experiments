# IPI Framework

This project implements the Integrated Predictive Ignition (IPI) framework for understanding consciousness through computational modeling and experimental validation.

## Project Structure

```text
ipi-consciousness/
├── core/                      # Core framework components
│   ├── models/                # Core computational models
│   │   ├── ipi_agent.py       # Main IPI agent implementation
│   │   ├── phase_transition.py # Somatic marker agent
│   │   ├── active_inference.py # Active inference models
│   │   └── hierarchical_predictive.py # Hierarchical predictive coding
│   ├── analysis/              # Data analysis utilities
│   └── utils/                 # Helper functions
├── experiments/               # Experimental implementations
│   ├── interoceptive_gating/  # Interoceptive gating paradigm (IMPLEMENTED)
│   ├── ai_benchmarking/       # AI agent benchmarking (IMPLEMENTED)
│   ├── somatic_marker_priming/# Somatic marker experiments (PARTIAL)
│   ├── metabolic_cost/        # Metabolic cost analysis (PARTIAL)
│   └── clinical_biomarkers/   # Clinical applications (STUB)
├── data/                      # Data storage
│   ├── raw/                   # Raw data
│   └── processed/             # Processed data
├── docs/                      # Documentation
└── tests/                     # Unit tests
```

## Getting Started

1. **Set up the environment**

   ```bash
   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix/macOS
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Run the IPI Agent example**

   ```bash
   python -m core.models.ipi_agent
   ```

3. **Run the Somatic Agent example**

   ```bash
   python -m core.models.phase_transition
   ```

4. **Run experiments via GUI**

   ```bash
   python gui.py
   ```

5. **Run experiments via command line**

   ```bash
   # Run interoceptive gating experiment
   python run_experiments.py interoceptive_gating --n_participants 10 --n_trials 50
   
   # Run AI benchmarking experiment
   python run_experiments.py ai_benchmarking --n_episodes 100 --n_agents_per_type 3
   ```

## Currently Implemented

### Core Models

1. **IPI Agent** (`core/models/ipi_agent.py`)
   - Implements the core IPI framework with interoceptive and exteroceptive processing
   - Dynamic threshold mechanism for conscious access
   - Precision-weighted prediction errors
   - Somatic marker integration

2. **Phase Transition Model** (`core/models/phase_transition.py`)
   - Somatic marker-based decision making
   - Conscious vs unconscious processing modes
   - Expected free energy calculations

3. **Base Experiment Framework** (`core/experiment.py`)
   - Abstract base class for all experiments
   - Standardized data collection and analysis

### Implemented Experiments

1. **Interoceptive Gating Paradigm** (`experiments/interoceptive_gating/`)
   - Tests how interoceptive precision gates conscious access
   - Cardiac discrimination task simulation
   - Three conditions: interoceptive focus, exteroceptive focus, control
   - Threshold tracking and detection rate analysis

2. **AI Benchmarking** (`experiments/ai_benchmarking/`)
   - Compares different agent architectures in survival environments
   - Includes Random, Reactive, DQN, and IPI agents
   - Grid world environment with food, obstacles, and predators
   - Performance metrics: survival time, energy efficiency, food consumption

### Demonstration Scripts

1. **IPI Model Demonstrations** (`run_experiments.py`)
   - Threshold effects on ignition probability
   - Somatic marker influence on decision making
   - Precision parameter effects
   - Dynamic threshold adaptation

2. **GUI Interface** (`gui.py`)
   - Tkinter-based interface for running experiments
   - Parameter configuration and real-time logging
   - Supports all implemented experiments

## Key Features

- **Modular Architecture**: Clean separation between models, experiments, and utilities
- **Standardized Experiments**: All experiments inherit from `BaseExperiment` for consistency
- **Multiple Interfaces**: Command-line, GUI, and programmatic access
- **Data Management**: Automatic data saving and visualization
- **Extensible Design**: Easy to add new models and experiments

## Example Usage

### Running the IPI Agent

```python
from core.models.ipi_agent import IPIAgent

# Create and run agent with default parameters
agent = IPIAgent()
agent.run_example()  # Runs simulation and shows plots
```

### Running an Experiment

```python
from experiments.interoceptive_gating.experiment import run_interoceptive_gating_experiment

# Run experiment with custom parameters
experiment = run_interoceptive_gating_experiment(
    n_participants=20,
    n_trials_per_condition=100
)
```
