# IPI Framework - TODO List

This document contains all the experimental paradigms and features that are planned but not yet fully implemented.

## Experimental Paradigms (Not Yet Implemented)

### 1. Somatic Marker Priming and Decision Ignition

**Status**: Partial implementation (basic structure exists)

**Idea**: Test if unconscious somatic markers bias conscious decisions through interoceptive precision.

**Method**:

- Use backward masking to pair neutral decision cues (e.g., abstract symbols) with unconsciously presented affective images (positive/negative from IAPS database)
- Followed by a conscious perceptual decision task under uncertainty (e.g., random dot motion discrimination)
- Manipulate interoceptive awareness via heartbeat counting during the task

**IPI Prediction**:

- Decisions on trials primed with negative somatic markers will show:
  1. Higher interoceptive precision (measured via skin conductance response, pupil dilation)
  2. Increased likelihood of conscious "ignition" (P3b) during the decision period
  3. A behavioral bias toward more conservative or avoidant choices
- This effect will be stronger in individuals with higher baseline interoceptive accuracy

**Falsification**: If somatic markers don't bias perception or interact with interoceptive awareness, it challenges their proposed role in conscious access.

### 2. Metabolic Cost of Ignition

**Status**: Partial implementation (basic structure exists)

**Idea**: Directly measure the metabolic expenditure of conscious processing to validate its proposed "expensive" nature.

**Method**:

- Use calibrated fMRI or fNIRS to quantify the glucose/oxygen cost of neural processing
- Compare brain metabolism during:
  1. Subliminal word processing (masked primes, no ignition)
  2. Supraliminal word recognition (ignition)
  3. Semantic decision-making (sustained ignition)
- Vary cognitive load and interoceptive demand (e.g., concurrent heartbeat counting)

**IPI Prediction**:

- A significant, non-linear increase in metabolic rate will be observed specifically in the frontoparietal "workspace" network during ignition trials (2 & 3)
- High interoceptive demand will amplify this effect in the PFC but reduce it in sensory regions
- The metabolic cost will correlate with the amplitude of the global broadcast signal

**Falsification**: If the metabolic cost of conscious ignition is minimal or linear with neural activity, the framework's evolutionary rationale (costly threshold) is weakened.

### 3. Clinical Biomarkers for Disorders of Consciousness

**Status**: Stub implementation only

**Idea**: Develop a diagnostic panel based on IPI components to distinguish between states of consciousness.

**Method**:

Multi-modal assessment in DoC patients:

- **fMRI/EEG**: Measure global workspace connectivity (ignition capacity)
- **Heartbeat Evoked Potentials (HEP)**: Measure interoceptive precision
- **Pupillometry/SCR**: Measure autonomic (somatic) reactivity to emotional stimuli
- **Behavioral scales**: CRS-R for clinical correlation

**IPI Prediction**:

This multi-dimensional IPI Consciousness Index will:

1. Have higher prognostic accuracy than single-modality tools (e.g., PCI alone)
2. Show that patients with preserved interoceptive precision but disrupted ignition (e.g., severe TBI) have better recovery prospects
3. Reveal distinct neural signatures for different DoC states (VS, MCS, EMCS)

### 4. Phase Transitions in Consciousness

**Status**: Not implemented

**Idea**: Test if anesthetic transitions follow critical slowing dynamics predicted by IPI.

**Method**:

- High-temporal EEG during propofol induction/recovery
- Measure:
  1. Critical slowing (autocorrelation, variance)
  2. Functional connectivity (wPLI)
  3. Perturbation complexity index

**Prediction**:

- Loss of consciousness will show hallmarks of critical slowing
- Recovery will be more variable, reflecting multi-stable attractors
- Individual differences in transition dynamics will correlate with baseline precision

### 5. Cross-Species Validation

**Status**: Not implemented

**Test**: Whether IPI generalizes to non-human consciousness.

**Approach**:

- Train macaques in a confidence-based visual task
- Simultaneous recordings:
  1. Prefrontal LFPs (ignition)
  2. Pupillometry (LC activity)
  3. Autonomic measures (heart rate, skin conductance)

**Prediction**:
- Confidence reports will correlate with PFC ignition signatures
- These will be modulated by interoceptive signals
- Pharmacological disruption of NE will decouple the relationship

### 6. Threshold Detection Paradigm

**Status**: Directory exists but no implementation

**Idea**: Systematic investigation of the ignition threshold mechanism.

**Method**:

- Parametric manipulation of stimulus intensity around perceptual threshold
- EEG/MEG recording to capture ignition signatures
- Manipulation of interoceptive precision through various means

### 7. Advanced Computational Models

**Status**: Partial implementation

**Needed Implementations**:

- Full hierarchical predictive coding network
- Realistic neural mass models
- Energy-dependent gating mechanisms
- Integration with existing neuroscience simulation frameworks (e.g., Brian, NEST)

## Technical Improvements Needed

### Core Framework Enhancements

1. **Better Neural Simulation**

   - Implement realistic neural dynamics
   - Add noise models for different brain regions
   - Include neuromodulatory effects (dopamine, norepinephrine, acetylcholine)

2. **Advanced Analysis Tools**

   - EEG/MEG analysis pipelines
   - Connectivity analysis methods
   - Statistical testing frameworks
   - Machine learning classification tools

3. **Data Management**

   - Database integration for large datasets
   - Standardized data formats (BIDS compliance)
   - Version control for experimental protocols

### Experimental Infrastructure

1. **Real-time Capabilities**

   - Integration with psychophysics toolboxes (PsychoPy, Psychtoolbox)
   - Real-time physiological monitoring
   - Closed-loop experimental control

2. **Hardware Integration**

   - EEG/MEG acquisition systems
   - Eye tracking integration
   - Physiological monitoring (ECG, GSR, pupillometry)

3. **Stimulus Generation**

   - Advanced visual stimulus generation
   - Auditory stimulus synthesis
   - Haptic/tactile stimulus control
