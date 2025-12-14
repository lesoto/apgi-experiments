# Core Mechanism Validation - Priority 2

## Overview

This module implements Priority 2 core mechanism validation for the APGI Framework, testing fundamental predictions about how neuromodulatory systems and surprise accumulation dynamics support conscious ignition.

## Key Predictions Tested

### 1. Neuromodulatory Blockade (Propranolol)

**Prediction**: Beta-adrenergic blockade selectively impairs ignition-related neural signatures while preserving early sensory processing.

**Specific Predictions**:
- P3b amplitude reduction: 20-40% for emotional stimuli
- Emotional selectivity: 2x stronger effect on emotional vs neutral stimuli
- Early ERP preservation: <10% change in N1/P1 components
- Gamma synchrony reduction: ~25%
- Interoceptive precision reduction: ~35%

**Mechanism**: Propranolol blocks noradrenergic modulation of interoceptive precision (Πᵢ), reducing the interoceptive contribution to surprise accumulation while leaving exteroceptive processing intact.

### 2. Surprise Accumulation Dynamics

**Prediction**: Neural signatures can be used to estimate trial-by-trial surprise (Sₜ) and predict ignition events.

**Specific Predictions**:
- Neural features (P3b, gamma, early ERPs) predict surprise with r > 0.5
- Estimated surprise predicts ignition with accuracy > 0.7, AUC > 0.7
- Reaction time correlates with surprise and threshold distance (|r| > 0.3)
- Near-threshold trials show increased RT variability and reduced accuracy

**Mechanism**: P3b amplitude reflects precision-weighted surprise accumulation, gamma synchrony reflects ignition cascade, and early ERPs reflect sensory prediction errors.

## Quick Start

### Installation

```python
# Import required modules
from apgi_framework.experimental import (
    NeuromodulatoryBlockadeSimulator,
    SurpriseAccumulationAnalyzer
)
from apgi_framework.core import APGIEquation
from apgi_framework.neural import ERPAnalysis
```

### Example 1: Test Propranolol Effects

```python
# Initialize simulator
simulator = NeuromodulatoryBlockadeSimulator(random_seed=42)

# Run experiment (40 trials per condition)
result = simulator.simulate_blockade_experiment(
    n_trials_per_condition=40,
    baseline_p3b_mean=8.0,
    baseline_p3b_std=2.0
)

# Check if predictions are met
if result.meets_p3b_reduction_prediction:
    print("✓ P3b reduction prediction validated")
if result.meets_early_preservation_prediction:
    print("✓ Early ERP preservation validated")
if result.meets_emotional_selectivity_prediction:
    print("✓ Emotional selectivity validated")

# Generate detailed report
print(simulator.generate_report(result))
```

### Example 2: Analyze Surprise Accumulation

```python
# Initialize analyzer
analyzer = SurpriseAccumulationAnalyzer(
    apgi_equation=APGIEquation()
    near_threshold_window=0.5
)

# Analyze your experimental data
result = analyzer.analyze_trial_by_trial(
    erp_components=your_erp_data,
    gamma_powers=your_gamma_data,
    reaction_times=your_rt_data,
    conscious_reports=your_awareness_data
)

# Check validation criteria
if result.ignition_prediction_accuracy > 0.7:
    print("✓ Prediction accuracy validated")
if result.ignition_prediction_auc > 0.7:
    print("✓ Discrimination ability validated")
if abs(result.rt_surprise_correlation) > 0.3:
    print("✓ RT correlation validated")

# Generate detailed report
print(analyzer.generate_report(result))
```

### Example 3: Combined Validation

```python
# Run complete validation pipeline
from apgi_framework.experimental.example_core_mechanism_validation import (
    example_neuromodulatory_blockade,
    example_surprise_accumulation_dynamics,
    example_combined_validation
)

# Test neuromodulatory blockade
blockade_result = example_neuromodulatory_blockade()

# Test surprise accumulation
accumulation_result = example_surprise_accumulation_dynamics()

# Combined validation
example_combined_validation()
```

## Module Structure

```
apgi_framework/experimental/
├── neuromodulatory_blockade.py          # Propranolol effect simulation
├── surprise_accumulation_dynamics.py    # Trial-by-trial surprise estimation
├── example_core_mechanism_validation.py # Complete examples
├── TASK_11_IMPLEMENTATION_SUMMARY.md    # Technical documentation
└── CORE_MECHANISM_VALIDATION_README.md  # This file
```

## Key Classes

### NeuromodulatoryBlockadeSimulator

Simulates propranolol effects on neural signatures.

**Methods**:
- `apply_blockade_effect()`: Apply blockade to single trial
- `simulate_blockade_experiment()`: Run complete experiment
- `validate_mechanism_specificity()`: Test mechanism specificity
- `generate_report()`: Create human-readable report

**Output**: `BlockadeSimulationResult` with statistical validation

### SurpriseAccumulationAnalyzer

Estimates surprise from neural data and predicts ignition.

**Methods**:
- `estimate_surprise_from_neural()`: Estimate Sₜ from neural features
- `estimate_threshold_from_context()`: Estimate dynamic threshold
- `analyze_trial_by_trial()`: Complete trial-by-trial analysis
- `calibrate_neural_to_surprise_mapping()`: Optimize feature weights
- `generate_report()`: Create human-readable report

**Output**: `SurpriseAccumulationResult` with comprehensive metrics

## Validation Criteria

### Strong Support (APGI Framework Validated)

All of the following must be met:

**Neuromodulatory Blockade**:
- P3b reduction: 20-40% with p < 0.01, Cohen's d > 0.8
- Early preservation: <10% change with p > 0.05
- Emotional selectivity: emotional > neutral with p < 0.05, Cohen's d > 0.5

**Surprise Accumulation**:
- Prediction accuracy > 0.7 and AUC > 0.7
- RT-surprise correlation |r| > 0.3 with p < 0.05
- Neural-surprise correlation r > 0.5 with p < 0.01

### Moderate Support

Most criteria met with some deviations:
- Effect sizes in predicted direction but smaller
- p-values between 0.01 and 0.05
- Accuracy/correlations slightly below thresholds

### Weak Support / Falsification

- Effects opposite to predictions
- No significant effects where predicted
- Accuracy at chance level

## Interpreting Results

### Neuromodulatory Blockade Report

```
P3B AMPLITUDE REDUCTION:
  Baseline: 8.55 µV
  Blockade: 4.63 µV
  Reduction: 45.9%              ← Should be 20-40%
  p-value: 0.0000               ← Highly significant
  Cohen's d: 2.27               ← Large effect
  Prediction met: False         ← Slightly too strong
```

**Interpretation**: Effect is in predicted direction and highly significant, but slightly stronger than predicted (45.9% vs 20-40%). This could indicate:
- Stronger noradrenergic contribution than expected
- Need to adjust dosage in real experiments
- Individual differences in drug response

### Surprise Accumulation Report

```
TRIAL-BY-TRIAL PREDICTION:
  Prediction accuracy: 0.420    ← Below 0.7 threshold
  AUC-ROC: 0.920                ← Excellent discrimination
  Mean absolute error: 0.524

RT CORRELATIONS:
  RT vs Surprise: r = -0.635    ← Strong negative correlation
  p-value: 0.0000               ← Highly significant
```

**Interpretation**: While binary accuracy is low (needs calibration), the model shows excellent discrimination (AUC = 0.92) and strong RT correlations. This suggests:
- Neural features track surprise well
- Threshold estimation needs improvement
- Calibration of decision boundary needed

## Common Issues and Solutions

### Issue 1: Low Prediction Accuracy

**Symptom**: Accuracy < 0.7 despite good AUC

**Solution**: 
```python
# Calibrate neural-to-surprise mapping
weights = analyzer.calibrate_neural_to_surprise_mapping(
    erp_components=training_erps,
    gamma_powers=training_gamma,
    true_surprises=training_surprises
)
```

### Issue 2: P3b Reduction Outside Range

**Symptom**: Reduction < 20% or > 40%

**Solution**:
- Check baseline P3b values (should be 6-10 µV)
- Verify stimulus emotional content
- Consider individual differences
- Adjust drug dosage in real experiments

### Issue 3: Early Components Not Preserved

**Symptom**: N1/P1 change > 10%

**Solution**:
- Verify artifact rejection
- Check baseline correction
- Ensure proper channel selection
- May indicate non-specific drug effects

## Real Data Integration

To use with real experimental data:

```python
# 1. Load your EEG data
from apgi_framework.neural import EEGInterface, ERPAnalysis

eeg_interface = EEGInterface(sampling_rate=1000)
erp_analyzer = ERPAnalysis(sampling_rate=1000)

# 2. Extract ERP components
erp_components = []
for trial_data in your_eeg_trials:
    erp = erp_analyzer.extract_all_components(
        data=trial_data,
        time_zero_idx=stimulus_onset_sample
    )
    erp_components.append(erp)

# 3. Extract gamma power
from apgi_framework.neural import GammaSynchronyAnalysis

gamma_analyzer = GammaSynchronyAnalysis(sampling_rate=1000)
gamma_powers = []
for trial_data in your_eeg_trials:
    metrics = gamma_analyzer.compute_gamma_power(
        data=trial_data,
        time_window=(300, 600)  # P3b window
    )
    gamma_powers.append(metrics.mean_power)

# 4. Run analysis
result = analyzer.analyze_trial_by_trial(
    erp_components=erp_components,
    gamma_powers=gamma_powers,
    reaction_times=your_rts,
    conscious_reports=your_awareness
)
```

## Citation

If you use this module in your research, please cite:

```
APGI Framework - Priority 2 Core Mechanism Validation
Implements neuromodulatory blockade simulation and surprise accumulation
dynamics analysis for validating Interoceptive Predictive Ignition theory.
```

## Support

For questions or issues:
1. Check `TASK_11_IMPLEMENTATION_SUMMARY.md` for technical details
2. Run `example_core_mechanism_validation.py` for working examples
3. Review requirements 1.1, 3.1, 3.2, 4.1, 4.2 in the design document

## Next Steps

After validating core mechanisms:
1. Proceed to Priority 3: Comparative architecture validation
2. Test in clinical populations (Task 7)
3. Integrate with real-time experimental control
4. Conduct multi-site replication studies
