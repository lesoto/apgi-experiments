# Behavioral Tasks for Parameter Estimation

This module implements the three core behavioral tasks for extracting APGI (Ignition, Precision, Interoception) framework parameters:

1. **Detection Task** - for θ₀ (baseline ignition threshold) estimation
2. **Heartbeat Detection Task** - for Πᵢ (interoceptive precision) estimation  
3. **Dual-Modality Oddball Task** - for β (somatic bias) estimation

## Overview

These tasks form the foundation of the APGI parameter estimation pipeline, enabling rapid (~45-60 minute) individualized quantification of key computational parameters through a combination of behavioral measurements, EEG analysis, and pupillometry.

## Task 1: Detection Task (θ₀ Estimation)

### Purpose
Measures baseline ignition threshold using an adaptive visual/auditory detection task.

### Implementation
- **Class**: `DetectionTask`
- **Duration**: ~10 minutes (200 trials)
- **Modalities**: Visual (Gabor patches) or Auditory (tones)
- **Method**: QUEST+ adaptive staircase for optimal stimulus selection

### Key Components
- `QuestPlusStaircase`: Adaptive algorithm for efficient threshold estimation
- `GaborPatchGenerator` / `ToneGenerator`: Stimulus presentation
- `BehavioralThresholdCalculator`: Computes 50% detection point
- `P3bCorrelationValidator`: Validates threshold against P3b amplitude (target r > 0.5)

### Usage Example
```python
from research.core_mechanisms.experiments.experimental import DetectionTask

task = DetectionTask(
    task_id="detection_001",
    modality="visual",  # or "auditory"
    n_trials=200,
    participant_id="P001",
    session_id="S001"
)

task.initialize()
task.run()
results = task.get_results()

# Validate with P3b data
validation = task.validate_with_p3b(p3b_amplitudes)
print(f"θ₀ estimate: {results['threshold_estimate']:.4f}")
```

### Output
- Behavioral threshold estimate (θ₀)
- Psychometric curve parameters
- P3b correlation validation results
- Trial-by-trial data with reaction times

## Task 2: Heartbeat Detection Task (Πᵢ Estimation)

### Purpose
Measures interoceptive precision through heartbeat detection with confidence ratings.

### Implementation
- **Class**: `HeartbeatDetectionTask`
- **Duration**: ~8 minutes (60 trials)
- **Method**: Synchronous/asynchronous tone presentation relative to R-peaks
- **Adaptive**: Adjusts asynchrony window for poor performers (d' < 0.5)

### Key Components
- `HeartbeatSynchronizer`: Real-time R-peak detection and timing
- `ToneGenerator`: Cardiac-locked tone presentation
- `DPrimeCalculator`: Computes sensitivity (d') from hits and false alarms
- `ConfidenceAnalyzer`: Metacognitive assessment
- `AdaptiveAsynchronyAdjuster`: Maintains ~75% accuracy for poor performers

### Usage Example
```python
from research.core_mechanisms.experiments.experimental import HeartbeatDetectionTask

task = HeartbeatDetectionTask(
    task_id="heartbeat_001",
    n_trials=60,
    participant_id="P001",
    session_id="S001"
)

task.initialize()
task.run()
results = task.get_results()

# Integrate neural priors
task.integrate_pupillometry(pupil_data)
task.integrate_hep(hep_amplitudes)

print(f"Πᵢ (d'): {results['d_prime']:.3f}")
```

### Output
- d' (sensitivity measure)
- Confidence-accuracy correlation
- Metacognitive sensitivity
- Pupil dilation features (200-500ms post-stimulus)
- HEP amplitudes (250-400ms post R-peak)

## Task 3: Dual-Modality Oddball Task (β Estimation)

### Purpose
Measures somatic bias through precision-matched interoceptive and exteroceptive oddball detection.

### Implementation
- **Class**: `DualModalityOddballTask`
- **Duration**: ~12 minutes (120 trials)
- **Method**: Rare deviants in both modalities with matched detection precision
- **Calibration**: Ensures Πₑ ≈ Πᵢ through separate staircase procedures

### Key Components
- `StimulusCalibrator`: Matches precision across modalities
- `InteroceptiveDeviantGenerator`: CO2 puffs or heartbeat-synchronized flashes
- `ExteroceptiveDeviantGenerator`: Rare Gabor orientations or tones
- `P3bRatioCalculator`: Computes β from P3b amplitude ratio

### Usage Example
```python
from research.core_mechanisms.experiments.experimental import DualModalityOddballTask

task = DualModalityOddballTask(
    task_id="oddball_001",
    n_trials=120,
    deviant_probability=0.2,
    participant_id="P001",
    session_id="S001"
)

# Initialize (includes automatic calibration)
task.initialize()
task.run()

# Integrate EEG data
task.integrate_eeg_p3b(p3b_data)
results = task.get_results()

print(f"β (P3b ratio): {results['p3b_ratio']:.3f}")
```

### Output
- P3b ratio (interoceptive/exteroceptive)
- Calibrated thresholds for both modalities
- Detection rates per modality
- Trial-by-trial P3b amplitudes

## Complete Session Workflow

A typical parameter estimation session runs all three tasks sequentially:

```python
from apgi_framework.experimental import (
    DetectionTask,
    HeartbeatDetectionTask,
    DualModalityOddballTask
)

# Task 1: θ₀ estimation (~10 min)
detection = DetectionTask(...)
detection.initialize()
detection.run()
theta0 = detection.get_results()['threshold_estimate']

# Inter-task interval (60s)

# Task 2: Πᵢ estimation (~8 min)
heartbeat = HeartbeatDetectionTask(...)
heartbeat.initialize()
heartbeat.run()
pi_i = heartbeat.get_results()['d_prime']

# Inter-task interval (60s)

# Task 3: β estimation (~12 min)
oddball = DualModalityOddballTask(...)
oddball.initialize()
oddball.run()
oddball.integrate_eeg_p3b(p3b_data)
beta = oddball.get_results()['p3b_ratio']

print(f"Parameters: θ₀={theta0:.4f}, Πᵢ={pi_i:.3f}, β={beta:.3f}")
```

## Data Integration

### EEG Integration
All tasks support integration with EEG data for neural validation:

- **Detection Task**: P3b amplitude (250-500ms at Pz)
- **Heartbeat Task**: HEP amplitude (250-400ms post R-peak)
- **Oddball Task**: P3b amplitudes to both deviant types

### Pupillometry Integration
Heartbeat detection task integrates high-speed pupillometry (1000 Hz):

- Baseline pupil diameter
- Peak dilation (200-500ms post-stimulus)
- Time to peak
- Blink detection and interpolation

### Database Persistence
All tasks support automatic data persistence via `ParameterEstimationDAO`:

```python
from pathlib import Path
from apgi_framework.data import ParameterEstimationDAO

dao = ParameterEstimationDAO(Path("data/parameter_estimation.db"))

task = DetectionTask(
    ...,
    dao=dao  # Automatic trial-by-trial saving
)
```

## Quality Control

### Real-time Monitoring
- Timing accuracy tracking (sub-millisecond precision)
- Response validation
- Signal quality assessment
- Adaptive parameter adjustment

### Data Quality Metrics
Each trial includes comprehensive quality metrics:
- EEG artifact ratio
- Pupil data loss percentage
- Cardiac signal quality
- Overall quality score

### Validation Criteria
- **Detection Task**: P3b correlation r > 0.5
- **Heartbeat Task**: d' > 0.5 (adaptive adjustment if lower)
- **Oddball Task**: Precision matching Πₑ ≈ Πᵢ

## Advanced Features

### Adaptive Algorithms
- QUEST+ for optimal stimulus selection
- Adaptive asynchrony adjustment for heartbeat task
- Precision-matched calibration for oddball task

### Timing Control
- `PrecisionTimer`: Sub-millisecond accuracy
- Cardiac-locked stimulus presentation
- Synchronized multi-modal data acquisition

### State Management
- Task state machine for robust error handling
- Pause/resume functionality
- Session state preservation

## Testing and Validation

Run the example file to test all tasks:

```bash
python -m apgi_framework.experimental.example_behavioral_tasks
```

This will run:
1. Individual task examples
2. Complete session workflow
3. Simulated data integration
4. Results summary

## Requirements

### Hardware
- EEG system (128+ channels recommended)
- High-speed eye tracker (1000 Hz for pupillometry)
- ECG/PPG for cardiac monitoring
- Response device (keyboard/button box)

### Software Dependencies
- numpy
- scipy (for psychometric functions and statistics)
- Lab Streaming Layer (LSL) for data synchronization

### Optional
- CO2 delivery system for interoceptive oddball
- Chin rest/bite bar for artifact control

## Clinical Feasibility

The complete protocol is designed for clinical feasibility:
- **Total duration**: 45-60 minutes (including setup)
- **Automated**: Minimal experimenter intervention
- **Adaptive**: Adjusts to individual performance
- **Robust**: Comprehensive error handling and quality control
- **Validated**: Neural markers confirm behavioral estimates

## References

See the main APGI framework documentation for theoretical background and validation studies.

## Support

For questions or issues:
1. Check `example_behavioral_tasks.py` for usage examples
2. Review task-specific docstrings
3. Consult the main APGI framework documentation
