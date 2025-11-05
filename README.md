# IPI Framework

This project implements the Integrated Predictive Ignition (IPI) framework for understanding consciousness through computational modeling and experimental validation.

## Project Structure

```text
ipi-consciousness/
├── core/                      # Core framework components
│   ├── models/                # Core computational models
│   ├── analysis/              # Data analysis utilities
│   └── utils/                 # Helper functions
├── experiments/               # Experimental implementations
│   ├── interoceptive_gating/  # Interoceptive gating paradigm
│   ├── somatic_marker_priming/# Somatic marker experiments
│   ├── metabolic_cost/        # Metabolic cost analysis
│   ├── ai_benchmarking/       # AI agent benchmarking
│   └── clinical_biomarkers/   # Clinical applications
├── data/                      # Data storage
│   ├── raw/                   # Raw data
│   └── processed/             # Processed data
├── docs/                      # Documentation
└── scripts/                   # Utility scripts
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

## Project Goals

1. Implement the Interoceptive Gating Paradigm
2. Develop Somatic Marker Priming experiments
3. Analyze Metabolic Cost of Ignition
4. Benchmark AI agents using the IPI framework
5. Develop Clinical Biomarkers for Disorders of Consciousness

## IPI Experiments

### 1. The Interoceptive Gating Paradigm

**Idea**: Manipulate interoceptive precision (Πⁱ) while holding exteroceptive stimuli constant to see if it gates conscious access.

**Method**:

- Use a cardiac discrimination task: Participants judge whether a visual stimulus (Gabor patch) appears synchronously or asynchronously with their heartbeat.
- Compare three conditions:
  1. Interoceptive Focus: Attend to your heartbeat.
  2. Exteroceptive Focus: Attend to the visual clarity of the stimulus.
  3. Control Focus: Attend to a neutral auditory stream.
- Present visual stimuli at individual perceptual thresholds (50% detection rate).

**IPI Prediction**: The Interoceptive Focus condition will increase interoceptive precision (Πⁱ), lowering the ignition threshold (θₜ). This will result in:

- Higher detection rates for identical near-threshold stimuli.
- Larger P3b amplitudes and increased Global Field Power (GFP) in EEG, specifically correlated with heartbeat-evoked potential (HEP) amplitude.
- Faster reaction times for detected stimuli.

**Falsification**: If interoceptive focus has no effect or suppresses visual detection, the core role of interoceptive precision in gating access is challenged.

## 2. Somatic Marker Priming and Decision Ignition

**Idea**: Test if unconscious somatic markers bias conscious decisions through interoceptive precision.

**Method**:

- Use backward masking to pair neutral decision cues (e.g., abstract symbols) with unconsciously presented affective images (positive/negative from IAPS database).
- Followed by a conscious perceptual decision task under uncertainty (e.g., random dot motion discrimination).
- Manipulate interoceptive awareness via heartbeat counting during the task.

**IPI Prediction**:

- Decisions on trials primed with negative somatic markers will show:
  1. Higher interoceptive precision (measured via skin conductance response, pupil dilation).
  2. Increased likelihood of conscious "ignition" (P3b) during the decision period.
  3. A behavioral bias toward more conservative or avoidant choices.
- This effect will be stronger in individuals with higher baseline interoceptive accuracy.

**Falsification**: If somatic markers don't bias perception or interact with interoceptive awareness, it challenges their proposed role in conscious access.

## 3. Metabolic Cost of Ignition

**Idea**: Directly measure the metabolic expenditure of conscious processing to validate its proposed "expensive" nature.

**Method**:

- Use calibrated fMRI or fNIRS to quantify the glucose/oxygen cost of neural processing.
- Compare brain metabolism during:
  1. Subliminal word processing (masked primes, no ignition)
  2. Supraliminal word recognition (ignition)
  3. Semantic decision-making (sustained ignition)
- Vary cognitive load and interoceptive demand (e.g., concurrent heartbeat counting).

**IPI Prediction**:

- A significant, non-linear increase in metabolic rate will be observed specifically in the frontoparietal "workspace" network during ignition trials (2 & 3).
- High interoceptive demand will amplify this effect in the PFC but reduce it in sensory regions.
- The metabolic cost will correlate with the amplitude of the global broadcast signal.

**Falsification**: If the metabolic cost of conscious ignition is minimal or linear with neural activity, the framework's evolutionary rationale (costly threshold) is weakened.

## 4. AI Benchmarking with IPI Agents

**Idea**: Build IPI-based AI agents and compare their performance against alternative architectures in complex environments.

**Task**: Survival in a 2D environment with:

- Energy sources (food)
- Threats (predators)
- Information sources (partial observability)

**Agents**:

1. Baseline: Standard RL (Model-Free)
2. IPI-Lite: RL + precision-weighted prediction errors
3. Full IPI: Hierarchical PE with interoceptive loop and ignition threshold

**Metrics**:

- Survival time
- Energy efficiency
- Generalization to novel, high-uncertainty scenarios

**Prediction**: The IPI agent will show:

1. More human-like exploration/exploitation tradeoffs
2. Better performance in environments requiring metabolic cost-benefit analysis
3. "Conscious" ignition events that correlate with strategic behavioral switches

## 5. Clinical Biomarkers for Disorders of Consciousness

**Idea**: Develop a diagnostic panel based on IPI components to distinguish between states of consciousness.

**Method**:

Multi-modal assessment in DoC patients:

- **fMRI/EEG**: Measure global workspace connectivity (ignition capacity)
- **Heartbeat Evoked Potentials (HEP)**: Measure interoceptive precision
- **Pupillometry/SCR**: Measure autonomic (somatic) reactivity to emotional stimuli
- **Behavioral scales**: CRS-R for clinical correlation

**IPI Prediction**: This multi-dimensional IPI Consciousness Index will:

1. Have higher prognostic accuracy than single-modality tools (e.g., PCI alone)
2. Show that patients with preserved interoceptive precision but disrupted ignition (e.g., severe TBI) have better recovery prospects
3. Reveal distinct neural signatures for different DoC states (VS, MCS, EMCS)

## 6. Phase Transitions in Consciousness

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

## 7. Cross-Species Validation

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

## 8. Computational Model

**Goal**: Formalize IPI as a neural process model.

**Components**:

1. Hierarchical predictive coding network
2. Precision weighting via neuromodulation
3. Energy-dependent gating mechanism
4. Realistic neural mass model

**Test**: Can it reproduce:

1. Neural signatures of consciousness?
2. Behavioral effects from experiments 1-3?
3. Breakdown patterns in clinical populations?

## 9. Philosophical Implications

**Questions**:

1. Does IPI bridge the explanatory gap?
2. How does it compare to IIT/GWT/REBUS?
3. What are the boundaries of "conscious" processing?

## 10. Future Directions

1. Development of non-invasive precision modulators (e.g., tACS at individual alpha frequency)
2. Applications in education (optimizing learning states)
3. Clinical interventions for disorders of consciousness
4. Cross-species comparisons of conscious processing
