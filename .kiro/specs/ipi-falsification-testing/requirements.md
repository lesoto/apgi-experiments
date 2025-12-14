# Requirements Document

## Introduction

This specification defines the requirements for implementing a comprehensive testing framework to validate or falsify the APGI (Interoceptive Predictive Integration) Framework. The system will implement the mathematical ignition threshold equation, simulate neural signatures, and provide automated testing capabilities to evaluate the four primary falsification criteria outlined in the APGI Framework Falsification document.

The framework tests conscious access through precision-gated threshold mechanisms, requiring implementation of complex neurophysiological simulations, statistical analysis tools, and automated validation systems to determine if the APGI Framework can be falsified under controlled experimental conditions.

## Requirements

### Requirement 1: Core Mathematical Framework Implementation

**User Story:** As a neuroscience researcher, I want to implement the APGI ignition threshold equation so that I can simulate conscious access mechanisms and test falsification criteria.

#### Acceptance Criteria

1. WHEN the system calculates total precision-weighted surprise THEN it SHALL compute Sₜ = Πₑ·|εₑ| + Πᵢ(M_{c,a})·|εᵢ| with dimensionless output in range 0-10
2. WHEN the system evaluates ignition probability THEN it SHALL compute Bₜ = σ(α(Sₜ - θₜ)) using logistic sigmoid function
3. WHEN prediction errors are provided THEN the system SHALL standardize them as z-scores before processing
4. WHEN somatic marker gain is calculated THEN it SHALL modulate Πᵢ precision values, not εᵢ prediction errors directly
5. WHEN threshold θₜ is evaluated THEN it SHALL support dynamic adjustment based on context (high-stakes vs routine tasks)

### Requirement 2: Neural Signature Simulation

**User Story:** As a researcher testing falsification criteria, I want to simulate neural signatures (P3b ERP, gamma synchrony, BOLD activation, PCI) so that I can test dissociation scenarios between neural activity and consciousness.

#### Acceptance Criteria

1. WHEN simulating P3b ERP THEN the system SHALL generate amplitude values >5 μV at Pz electrode with latency 250-500 ms
2. WHEN simulating gamma-band synchrony THEN it SHALL calculate phase-locking values (PLV) >0.3 between frontoparietal and temporal regions, sustained >200 ms (30-80 Hz)
3. WHEN simulating BOLD activation THEN it SHALL generate Z > 3.1 values for bilateral dorsolateral prefrontal cortex, intraparietal sulcus, and anterior insula/ACC
4. WHEN calculating Perturbational Complexity Index THEN it SHALL compute PCI > 0.4 for conscious states
5. WHEN generating control signatures THEN it SHALL produce subthreshold values (P3b < 2 μV, PLV < 0.15, PCI < 0.3) for unconscious conditions

### Requirement 3: Primary Falsification Testing

**User Story:** As a researcher, I want to test the primary falsification criterion (full ignition signatures without consciousness) so that I can determine if the APGI Framework can be decisively falsified.

#### Acceptance Criteria

1. WHEN testing primary falsification THEN the system SHALL verify ALL required signatures are present simultaneously (P3b, gamma synchrony, BOLD, PCI)
2. WHEN evaluating consciousness absence THEN it SHALL confirm both subjective report negativity and objective forced-choice at chance level
3. WHEN checking AI/ACC engagement THEN it SHALL verify no significant BOLD response and PLV ≤ 0.25 for gamma coherence
4. WHEN running control requirements THEN it SHALL validate intact motor/verbal systems and metacognitive sensitivity
5. WHEN interpreting results THEN it SHALL distinguish between complete patterns (falsification) and partial signatures (subthreshold ignitions)

### Requirement 4: Secondary Falsification Criteria Testing

**User Story:** As a researcher, I want to test secondary falsification criteria (consciousness without ignition, threshold insensitivity, soma-bias absence) so that I can comprehensively evaluate framework boundaries.

#### Acceptance Criteria

1. WHEN testing consciousness without ignition THEN the system SHALL verify conscious reports occur with P3b < 2 μV, gamma PLV < 0.15, PCI < 0.3, and no frontoparietal BOLD elevation in >20% of trials
2. WHEN testing threshold insensitivity THEN it SHALL simulate pharmacological challenges (propranolol, L-DOPA, SSRIs, physostigmine) and verify θₜ modulation or lack thereof
3. WHEN testing soma-bias absence THEN it SHALL compare interoceptive vs exteroceptive prediction errors with matched precision and calculate β values
4. WHEN β approaches 1.0 (0.95-1.05) THEN the system SHALL flag soma-bias falsification
5. WHEN evaluating edge cases THEN it SHALL properly interpret anesthesia awareness, blindsight, dreams, and locked-in syndrome within framework boundaries

### Requirement 5: Neuromodulatory Threshold Dynamics

**User Story:** As a researcher studying threshold modulation, I want to simulate neuromodulatory effects on ignition threshold so that I can test the framework's predictions about dynamic threshold adjustment.

#### Acceptance Criteria

1. WHEN simulating norepinephrine effects THEN the system SHALL modulate θₜ based on propranolol blockade scenarios
2. WHEN simulating dopamine effects THEN it SHALL adjust θₜ according to L-DOPA elevation conditions
3. WHEN simulating serotonin effects THEN it SHALL modify θₜ based on SSRI elevation parameters
4. WHEN simulating acetylcholine effects THEN it SHALL alter θₜ according to physostigmine elevation
5. WHEN threshold remains unchanged despite pharmacological manipulation THEN the system SHALL flag neuromodulatory implementation falsification

### Requirement 6: Statistical Analysis and Validation

**User Story:** As a researcher, I want comprehensive statistical analysis tools so that I can validate experimental results and determine statistical significance of falsification tests.

#### Acceptance Criteria

1. WHEN analyzing experimental data THEN the system SHALL perform cluster-corrected statistical tests with p < 0.05 threshold
2. WHEN calculating effect sizes THEN it SHALL provide Cohen's d values and confidence intervals for all comparisons
3. WHEN evaluating replication requirements THEN it SHALL track results across multiple independent simulated "labs"
4. WHEN assessing sample sizes THEN it SHALL require n > 100 for soma-bias testing and appropriate power analysis
5. WHEN generating reports THEN it SHALL provide detailed statistical summaries with falsification probability assessments

### Requirement 7: Experimental Control and Validation

**User Story:** As a researcher, I want robust experimental controls so that I can ensure valid testing conditions and rule out confounding factors.

#### Acceptance Criteria

1. WHEN running experiments THEN the system SHALL validate intact motor/verbal response systems in simulated participants
2. WHEN testing task comprehension THEN it SHALL verify participants understand well-trained tasks
3. WHEN using stimuli THEN it SHALL ensure supraliminal presentation in control conditions
4. WHEN measuring consciousness THEN it SHALL employ multiple converging measures beyond verbal report
5. WHEN assessing metacognition THEN it SHALL verify intact confidence-accuracy correspondence to rule out executive dysfunction

### Requirement 8: Data Management and Reporting

**User Story:** As a researcher, I want comprehensive data management and reporting capabilities so that I can track experimental progress and generate publication-ready results.

#### Acceptance Criteria

1. WHEN storing experimental data THEN the system SHALL maintain structured datasets with proper metadata and versioning
2. WHEN generating reports THEN it SHALL produce detailed falsification test results with statistical summaries
3. WHEN tracking experiments THEN it SHALL log all parameter settings, random seeds, and experimental conditions
4. WHEN exporting results THEN it SHALL support multiple formats (CSV, JSON, HDF5) for further analysis
5. WHEN visualizing data THEN it SHALL generate publication-quality plots and figures showing key findings