# Priority 1: Direct Threshold Estimation System

## Overview

This module implements the Priority 1 direct threshold estimation system for the IPI (Interoceptive Predictive Ignition) framework. It provides psychophysical threshold estimation protocols across visual, auditory, and interoceptive modalities with integrated neural validation.

## Requirements Fulfilled

### Requirement 2.1-2.5: Psychophysical Threshold Estimation
- **2.1**: Adaptive staircase procedures across visual, auditory, and interoceptive modalities
- **2.2**: Systematic stimulus intensity variation with 50-500ms delays before awareness probes
- **2.3**: 50% conscious detection threshold calculation normalized to sensory detection thresholds
- **2.4**: Test-retest reliability with ICC > 0.70 over 1-week intervals
- **2.5**: Cross-modal threshold consistency with r > 0.5 correlation across modalities

### Requirement 3.1, 3.3: Neural Validation
- **3.1**: P3b amplitude, latency, and gamma-band activity extraction
- **3.3**: Neural correlates validation (lower θₜ predicts higher P3b amplitude r > 0.5, gamma power r > 0.4)
- **2.5**: P3b stochastic appearance detection on threshold trials

## Components

### 1. Threshold Estimation System (`threshold_estimation_system.py`)

#### Key Classes

**`ThresholdEstimationProtocol`**
- Main protocol for running threshold estimation experiments
- Integrates with `MultiModalTaskManager` for stimulus presentation
- Supports multiple modalities and threshold types
- Implements cross-modal normalization

**`ModalityThresholdConfig`**
- Configuration for threshold estimation in specific modality
- Includes staircase parameters, stimulus parameters, and awareness probe settings
- Validates configuration before execution

**`ThresholdEstimationResult`**
- Results container with threshold estimates, reliability metrics, and quality scores
- Includes detection and conscious access thresholds
- Provides normalized thresholds for cross-modal comparison

#### Features

- **Adaptive Staircase Algorithms**: QUEST+, PEST, simple up-down
- **Cross-Modal Normalization**: Normalizes thresholds to detection thresholds
- **Awareness Probes**: 50-500ms delayed probes for conscious access assessment
- **Quality Metrics**: Data quality and timing quality scoring
- **Test-Retest Reliability**: ICC calculation across sessions
- **Cross-Modal Consistency**: Correlation analysis across modalities

### 2. Neural Validation Pipeline (`neural_threshold_validation.py`)

#### Key Classes

**`NeuralThresholdValidationPipeline`**
- Integrates EEG recording with threshold estimation
- Real-time neural data processing during threshold trials
- Validates neural signatures of ignition events

**`NeuralThresholdTrial`**
- Container for single trial with behavioral and neural data
- Includes ERP components, P3b metrics, and gamma activity
- Quality metrics and artifact detection

**`NeuralValidationResult`**
- Comprehensive validation results
- Neural-behavioral correspondence metrics
- P3b stochastic appearance detection
- Gamma-band activity correlation

#### Features

- **EEG Integration**: Real-time EEG recording synchronized with stimulus presentation
- **ERP Analysis**: P3b peak detection, early component extraction (P1, N1, N170)
- **Gamma Analysis**: Gamma-band power and frontal-posterior coherence
- **Stochastic Appearance**: Detection of P3b variability near threshold
- **Neural Prediction**: Correlation between neural signatures and detection
- **Quality Control**: Artifact detection and signal quality assessment

## Usage Examples

### Basic Threshold Estimation

```python
from threshold_estimation_system import (
    ThresholdEstimationProtocol,
    create_default_visual_config
)

# Initialize protocol
protocol = ThresholdEstimationProtocol(
    participant_id="P001",
    session_id="session_001"
)
protocol.initialize()

# Run visual threshold estimation
visual_config = create_default_visual_config()
result = protocol.run_threshold_estimation(visual_config)

print(f"Threshold: {result.conscious_threshold.threshold:.4f}")
print(f"Normalized: {result.normalized_threshold:.4f}")

# Save results
protocol.save_results("output_dir")
protocol.cleanup()
```

### Neural Validation

```python
from neural_threshold_validation import (
    NeuralThresholdValidationPipeline,
    validate_neural_predictions
)

# Initialize pipeline
pipeline = NeuralThresholdValidationPipeline(
    participant_id="P002",
    session_id="session_001"
)
pipeline.initialize()

# Run with neural recording
visual_config = create_default_visual_config()
validation_result = pipeline.run_neural_threshold_estimation(visual_config)

print(f"P3b correlation: {validation_result.p3b_amplitude_threshold_correlation:.3f}")
print(f"Gamma correlation: {validation_result.gamma_power_threshold_correlation:.3f}")
print(f"Stochastic appearance: {validation_result.p3b_stochastic_appearance_detected}")

# Validate predictions
validations = validate_neural_predictions(validation_result)
print(f"Overall validation: {validations['overall_validation']}")

pipeline.save_results("output_dir")
pipeline.cleanup()
```

### Cross-Modal Consistency

```python
# Run threshold estimation for multiple modalities
protocol = ThresholdEstimationProtocol("P003", "session_001")
protocol.initialize()

# Visual
visual_result = protocol.run_threshold_estimation(create_default_visual_config())

# Auditory
auditory_result = protocol.run_threshold_estimation(create_default_auditory_config())

# Interoceptive
intero_result = protocol.run_threshold_estimation(create_default_interoceptive_config())

# Calculate cross-modal consistency
consistency = protocol.calculate_cross_modal_consistency()
print(f"Cross-modal consistency: {consistency:.3f}")
print(f"Requirement (r > 0.5): {'PASS' if consistency > 0.5 else 'FAIL'}")

protocol.cleanup()
```

### Test-Retest Reliability

```python
# Session 1
protocol_s1 = ThresholdEstimationProtocol("P004", "session_001")
protocol_s1.initialize()
result_s1 = protocol_s1.run_threshold_estimation(create_default_visual_config())
protocol_s1.cleanup()

# Session 2 (1 week later)
protocol_s2 = ThresholdEstimationProtocol("P004", "session_002")
protocol_s2.initialize()
result_s2 = protocol_s2.run_threshold_estimation(create_default_visual_config())

# Calculate ICC
icc = protocol_s2.calculate_test_retest_reliability(result_s1, result_s2)
print(f"Test-retest ICC: {icc:.3f}")
print(f"Requirement (ICC > 0.70): {'PASS' if icc > 0.70 else 'FAIL'}")

protocol_s2.cleanup()
```

## Configuration

### Staircase Parameters

```python
from experimental.adaptive_staircase import StaircaseParameters, StaircaseType

staircase_params = StaircaseParameters(
    staircase_type=StaircaseType.QUEST_PLUS,
    min_intensity=0.01,
    max_intensity=1.0,
    initial_intensity=0.3,
    min_trials=30,
    max_trials=80,
    min_reversals=6,
    normalize_to_detection_threshold=True
)
```

### Modality Configuration

```python
from experimental.threshold_estimation_system import ModalityThresholdConfig
from adaptive.stimulus_generators import GaborParameters

visual_config = ModalityThresholdConfig(
    modality=ModalityType.VISUAL,
    threshold_type=ThresholdType.CONSCIOUS_ACCESS,
    staircase_params=staircase_params,
    base_visual_params=GaborParameters(
        contrast=0.5,
        spatial_frequency=2.0,
        orientation=0.0,
        size_degrees=2.0,
        duration_ms=100.0
    ),
    awareness_probe_delay_ms=500.0,
    use_awareness_probe=True,
    n_trials_per_block=40,
    n_blocks=2
)
```

### EEG Configuration

```python
from neural.eeg_interface import EEGConfig, ChannelInfo, ChannelType

eeg_config = EEGConfig(
    sampling_rate=1000.0,
    buffer_size=10000,
    channels=[
        ChannelInfo("Fz", ChannelType.EEG),
        ChannelInfo("Cz", ChannelType.EEG),
        ChannelInfo("Pz", ChannelType.EEG),
        # ... more channels
    ],
    reference_type="average",
    highpass_freq=0.1,
    lowpass_freq=100.0,
    artifact_threshold=100.0
)
```

## Output Files

### Threshold Results
- `threshold_{participant}_{session}_{modality}.json`: Individual modality results
- `threshold_summary_{participant}_{session}.json`: Cross-modal summary

### Neural Validation Results
- `neural_validation_{participant}_{session}_{modality}.json`: Validation results
- `neural_trials_{participant}_{session}.json`: Trial-level neural data

### Result Structure

```json
{
  "participant_id": "P001",
  "session_id": "session_001",
  "modality": "visual",
  "threshold_type": "conscious_access",
  "conscious_threshold": {
    "threshold": 0.3245,
    "std_error": 0.0123,
    "confidence_interval": [0.3004, 0.3486],
    "n_trials": 45,
    "n_reversals": 8,
    "converged": true
  },
  "normalized_threshold": 1.23,
  "n_trials_completed": 45,
  "data_quality_score": 0.95,
  "timing_quality_score": 0.98
}
```

## Validation Criteria

### IPI Framework Requirements

1. **P3b-Threshold Correlation**: r > 0.5 (Requirement 3.3)
2. **Gamma-Threshold Correlation**: r > 0.4 (Requirement 3.3)
3. **P3b Stochastic Appearance**: Detected on threshold trials (Requirement 2.5)
4. **Test-Retest Reliability**: ICC > 0.70 (Requirement 2.4)
5. **Cross-Modal Consistency**: r > 0.5 (Requirement 2.5)

### Quality Metrics

- **Data Quality Score**: Based on convergence, reversals, and trial count
- **Timing Quality Score**: Based on stimulus presentation timing accuracy
- **Signal Quality Score**: Based on EEG artifact rate and impedances
- **Validation Confidence**: Overall confidence in neural validation results

## Integration with Existing Components

### Dependencies

- `experimental/adaptive_staircase.py`: Adaptive staircase algorithms
- `experimental/multi_modal_task_manager.py`: Stimulus presentation
- `adaptive/quest_plus_staircase.py`: QUEST+ implementation
- `adaptive/stimulus_generators.py`: Stimulus generation
- `neural/eeg_interface.py`: EEG data acquisition
- `neural/erp_analysis.py`: ERP component extraction
- `neural/gamma_synchrony.py`: Gamma-band analysis

### Data Flow

```
ThresholdEstimationProtocol
    ↓
MultiModalTaskManager → Stimulus Presentation
    ↓
AdaptiveStaircase → Intensity Selection
    ↓
TrialResult → Behavioral Response
    ↓
NeuralThresholdValidationPipeline
    ↓
EEGInterface → Neural Recording
    ↓
ERPAnalysis + GammaSynchronyAnalysis
    ↓
NeuralValidationResult
```

## Testing

Run the example script to test the implementation:

```bash
python ipi_framework/experimental/example_threshold_estimation.py
```

This will run four examples:
1. Basic threshold estimation
2. Neural validation pipeline
3. Test-retest reliability
4. Complete validation battery

## Notes

- Current implementation uses simulated data for demonstration
- Real implementation requires hardware integration:
  - Stimulus presentation system (PsychoPy, Presentation, etc.)
  - EEG/MEG recording system (BrainVision, Neuroscan, etc.)
  - Response collection device (keyboard, button box, etc.)
- Timing precision is critical for neural synchronization
- Artifact rejection is essential for clean neural data
- Cross-modal normalization requires careful calibration

## Future Enhancements

- [ ] Hardware trigger integration for precise EEG synchronization
- [ ] Real-time adaptive threshold adjustment based on neural data
- [ ] Machine learning models for threshold prediction from neural signatures
- [ ] Multi-site data aggregation and meta-analysis
- [ ] Automated quality control and data validation
- [ ] Integration with clinical assessment tools

## References

- IPI Framework Requirements Document
- IPI Framework Design Document
- IPI Testable Predictions Document
- QUEST+ Algorithm (Watson & Pelli, 1983)
- P3b Component Analysis (Polich, 2007)
- Gamma-Band Synchrony (Fries, 2009)
