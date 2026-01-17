# APGI Cognitive Tasks Framework

This directory contains a comprehensive collection of cognitive experiments integrated with the APGI (Active Inference and Precision Gating Integration) framework. Each experiment is designed to test specific aspects of cognition while measuring APGI parameters (θₜ, π, ε, β).

## Directory Structure

```text
research/cognitive_tasks/experiments/
├── __init__.py                           # Base classes and utilities
├── decision_making/                      # Decision-making paradigms
│   ├── __init__.py
│   ├── iowa_gambling_task.py            # Risk-based decision making
│   └── probabilistic_category_learning.py # Statistical learning
├── attention/                           # Attention and perception
│   ├── __init__.py
│   ├── attentional_blink.py             # Temporal attention limits
│   ├── change_blindness.py              # Change detection
│   ├── visual_search.py                 # Spatial attention
│   └── posner_cueing.py                # Spatial orienting
├── conflict_monitoring/                 # Cognitive control and conflict
│   ├── __init__.py
│   ├── stroop_effect.py                 # Semantic interference
│   ├── simon_effect.py                 # Spatial interference
│   └── eriksen_flanker.py              # Flanker interference
├── consciousness/                       # Consciousness and awareness
│   ├── __init__.py
│   ├── masking.py                       # Visual masking
│   ├── binocular_rivalry.py            # Binocular rivalry
│   └── inattentional_blindness.py     # Inattentional blindness
├── memory/                             # Memory processes
│   ├── __init__.py
│   ├── dual_n_back.py                   # Working memory
│   ├── sternberg_memory.py             # Recognition memory
│   ├── working_memory_span.py          # Memory capacity
│   └── drm_false_memory.py             # False memory
├── executive_control/                   # Executive functions
│   ├── __init__.py
│   ├── go_no_go.py                     # Response inhibition
│   └── stop_signal.py                  # Action cancellation
├── perception/                         # Perceptual processes
│   ├── __init__.py
│   ├── navon_task.py                   # Global/local processing
│   └── multisensory_integration.py     # Cross-modal perception
├── learning/                           # Learning and plasticity
│   ├── __init__.py
│   ├── serial_reaction_time.py          # Implicit learning
│   └── artificial_grammar_learning.py  # Rule learning
└── timing_navigation/                  # Temporal and spatial cognition
    ├── __init__.py
    ├── time_estimation.py              # Time perception
    └── virtual_navigation.py          # Spatial navigation
```

## Base Classes

### CognitiveTaskExperiment

The foundational base class for all cognitive experiments, providing:
- APGI model integration
- Trial data management
- Response simulation for testing
- Comprehensive summary statistics

### Specialized Base Classes

- **TrialBasedTask**: For experiments with discrete trials
- **BlockBasedTask**: For experiments with block structures
- **AdaptiveTask**: For experiments with difficulty adjustment

## APGI Integration

Each experiment maps cognitive processes to APGI parameters:

| Parameter                | Cognitive Interpretation                 | Measurement                      |
|--------------------------|------------------------------------------|----------------------------------|
| **θₜ** (threshold)       | Decision/attention threshold             | Response criteria                 |
| **π** (precision)         | Confidence/certainty                      | Response confidence               |
| **ε** (prediction error)  | Unexpected events                         | Conflict/surprise                 |
| **β** (inverse temperature) | Response consistency                     | Choice variability                |

## Implemented Experiments

### Decision Making (2/2 complete)

#### Iowa Gambling Task

- **Purpose**: Assess risk-based decision making
- **APGI Focus**: θₜ (risk threshold), ε (outcome prediction error)
- **Features**: Learning from feedback, deck selection strategies
- **File**: `decision_making/iowa_gambling_task.py`

#### Probabilistic Category Learning

- **Purpose**: Statistical learning under uncertainty
- **APGI Focus**: π (precision), ε (prediction error)
- **Features**: Category learning, belief updating
- **File**: `decision_making/probabilistic_category_learning.py`

### Attention (4/4 complete)

#### Attentional Blink

- **Purpose**: Temporal attention limitations
- **APGI Focus**: θₜ (temporal threshold), π (temporal precision)
- **Features**: RSVP streams, dual-target detection
- **File**: `attention/attentional_blink.py`

#### Change Blindness

- **Purpose**: Visual change detection
- **APGI Focus**: θₜ (change detection threshold)
- **Features**: Flicker paradigm, scene changes
- **File**: `attention/change_blindness.py`

#### Visual Search

- **Purpose**: Spatial attention efficiency
- **APGI Focus**: π (spatial precision), θₜ (search termination)
- **Features**: Feature vs. conjunction searches, set size effects
- **File**: `attention/visual_search.py`

#### Posner Cueing

- **Purpose**: Spatial attention orienting
- **APGI Focus**: ε (invalid cue prediction error)
- **Features**: Valid/invalid cues, SOA manipulation
- **File**: `attention/posner_cueing.py`

### Conflict Monitoring (3/3 complete)

#### Stroop Effect

- **Purpose**: Cognitive control and interference
- **APGI Focus**: θₜ (control threshold), ε (conflict prediction error)
- **Features**: Congruent/incongruent trials, conflict adaptation
- **File**: `conflict_monitoring/stroop_effect.py`

#### Simon Effect

- **Purpose**: Spatial stimulus-response compatibility
- **APGI Focus**: θₜ (response selection), π (spatial mapping)
- **Features**: Spatial interference, compatibility effects
- **File**: `conflict_monitoring/simon_effect.py`

#### Eriksen Flanker

- **Purpose**: Attentional filtering and response selection
- **APGI Focus**: θₜ (filtering threshold), ε (flanker conflict)
- **Features**: Flanker compatibility, conflict adaptation
- **File**: `conflict_monitoring/eriksen_flanker.py`

### Consciousness (1/3 complete)

#### Visual Masking

- **Purpose**: Conscious perception thresholds
- **APGI Focus**: θₜ (consciousness threshold), π (perceptual precision)
- **Features**: SOA manipulation, mask types, visibility estimation
- **File**: `consciousness/masking.py`

#### Binocular Rivalry (pending)

- **Purpose**: Perceptual competition and awareness
- **APGI Focus**: θₜ (perceptual switching), π (competition precision)

#### Inattentional Blindness (pending)

- **Purpose**: Attention and awareness
- **APGI Focus**: θₜ (attentional gating), π (awareness precision)

## Usage Examples

### Running Individual Experiments

```python
from research.cognitive_tasks.experiments.decision_making.iowa_gambling_task import run_iowa_gambling_task_experiment

# Run with default parameters
results = run_iowa_gambling_task_experiment()

# Access results
summary = results['summary']
participant_data = results['participant_data']

# Get specific participant summary
summary = experiment.participant_data[1]['summary']
```

### Using the Experiment Registry

```python
from tools.run_experiments import run_experiment

# Run any registered experiment
results = run_experiment(
    'stroop_effect',
    n_participants=20,
    congruent_ratio=0.7,
    apgi_params={'theta_t': 0.5, 'pi': 1.0}
)
```

### Creating Custom Experiments

```python
from research.cognitive_tasks.experiments import TrialBasedTask, TrialBasedTaskConfig

@dataclass
class CustomExperimentConfig(TrialBasedTaskConfig):
    stimulus_duration: float = 0.5
    response_window: float = 2.0

class CustomExperiment(TrialBasedTask):
    def generate_trial(self, config: CustomExperimentConfig):
        # Implement trial generation
        return {}
```

## Configuration System

Each experiment uses a dataclass-based configuration system:

```python
@dataclass
class ExperimentConfig:
    n_participants: int = 20
    n_trials: int = 100
    stimulus_duration_ms: int = 1000
    response_window_ms: int = 2000
    
    # APGI parameters
    theta_base: float = 5.0
    sigma_pe: float = 1.0
    sigma_pi: float = 1.0
    beta: float = 1.0
```

## Data Structure

### Trial Data

Each trial includes:
- Basic trial information (ID, participant, condition)
- Stimulus parameters
- Response data (accuracy, RT, confidence)
- APGI parameters (surprise, ignition probability, somatic marker)

### Summary Statistics

Comprehensive summaries include:
- Overall performance metrics
- Condition-specific effects
- Learning curves and adaptation effects
- APGI parameter distributions

## Running Experiments from Command Line

```bash
# Run specific experiment
python tools/run_experiments.py iowa_gambling_task --n_participants 20 --n_trials 100 --output results.csv

# Run with custom parameters
python tools/run_experiments.py stroop_effect --n_participants 10 --congruent_ratio 0.5
```

## Experiment Registry

All experiments are registered in `tools/run_experiments.py`:

```python
EXPERIMENTS = {
    "iowa_gambling_task": "research.cognitive_tasks.experiments.decision_making.iowa_gambling_task",
    "probabilistic_category_learning": "research.cognitive_tasks.experiments.decision_making.probabilistic_category_learning",
    # ... other experiments
}
```

## Key Design Principles

1. **Modular Design**: Each experiment is self-contained with standardized interfaces
2. **APGI Integration**: Explicit mapping to APGI parameters with theoretical justification
3. **Configuration-Driven**: Flexible parameter system via dataclasses
4. **Comprehensive Analysis**: Built-in summary statistics and effect calculations
5. **Simulation Support**: Response simulation for testing and development
6. **Extensible**: Easy to add new experiments following established patterns

## Future Development

### Remaining Experiments (13/24 complete)

- **Memory**: N-back, Sternberg, Working Memory Span, DRM
- **Executive Control**: Go/No-Go, Stop Signal  
- **Perception**: Navon Task, Multisensory Integration
- **Learning**: Serial Reaction Time, Artificial Grammar Learning
- **Consciousness**: Binocular Rivalry, Inattentional Blindness
- **Timing/Navigation**: Time Estimation, Virtual Navigation

### Planned Enhancements

- Real-time APGI parameter visualization
- Cross-experiment parameter comparison
- Machine learning-based parameter optimization
- Integration with neuroimaging data formats
- Web-based experiment interfaces

## Contributing

When adding new experiments:

1. Follow the established directory structure
2. Inherit from appropriate base class
3. Include comprehensive APGI integration
4. Add to experiment registry
5. Update this documentation
6. Include example usage and parameter descriptions

## References

Each experiment includes theoretical background and references to seminal papers in cognitive psychology and neuroscience, with specific attention to how the paradigm relates to active inference and precision gating theories.
