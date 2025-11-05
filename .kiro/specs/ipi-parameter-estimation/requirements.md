# Requirements Document

## Introduction

The IPI Framework Parameter Estimation Pipeline is a comprehensive neuroscience research system that enables rapid, individualized quantification of key computational parameters within a standardized 45-60 minute protocol. The system combines behavioral tasks, high-density EEG analysis, and pupillometry to extract three core parameters: baseline ignition threshold (θ₀), interoceptive precision (Πᵢ), and somatic bias (β). The implementation must support adaptive, computerized tasks optimized for clinical feasibility, real-time data processing, and robust statistical modeling.

## Requirements

### Requirement 1: Baseline Ignition Threshold (θ₀) Estimation

**User Story:** As a researcher, I want to measure baseline ignition threshold using an adaptive visual/auditory detection task, so that I can quantify individual differences in conscious perception thresholds.

#### Acceptance Criteria

1. WHEN the system starts a detection task THEN it SHALL present Gabor patches or tones at varying intensities for 200 trials over approximately 10 minutes
2. WHEN a stimulus is presented THEN the system SHALL record participant button press responses and reaction times
3. WHEN analyzing behavioral data THEN the system SHALL calculate the stimulus intensity yielding 50% "seen" responses as the behavioral ignition threshold
4. WHEN processing EEG data THEN the system SHALL extract P3b amplitude (250-500 ms at Pz electrode) for each trial
5. WHEN validating results THEN the system SHALL correlate lower θ₀ with higher resting P3b amplitude to suprathreshold standards (target correlation r > 0.5)
6. IF the adaptive staircase algorithm is running THEN the system SHALL adjust stimulus intensity based on previous responses to maintain optimal difficulty

### Requirement 2: Interoceptive Precision (Πᵢ) Estimation

**User Story:** As a researcher, I want to measure interoceptive precision through heartbeat detection with confidence ratings, so that I can quantify individual sensitivity to internal bodily signals.

#### Acceptance Criteria

1. WHEN the heartbeat detection task starts THEN the system SHALL present 60 trials of auditory tones that are either synchronous or asynchronous with heartbeat over approximately 8 minutes
2. WHEN a tone is presented THEN the system SHALL record participant responses about synchronization and confidence ratings
3. WHEN collecting physiological data THEN the system SHALL record high-speed pupillometry at 1000 Hz during all trials
4. WHEN processing EEG data THEN the system SHALL extract heartbeat-evoked potential (HEP; 250-400 ms post-R-peak) and interoceptive P3b to synchronous tones
5. WHEN calculating Πᵢ THEN the system SHALL derive it from d′ in heartbeat detection using hierarchical Bayesian model inversion
6. WHEN modeling trial-level Πᵢ THEN the system SHALL use HEP amplitude and pupil dilation (200-500 ms post-stimulus) as neural priors
7. IF participant shows poor heartbeat perception (d′ < 0.5) THEN the system SHALL implement adaptive staircase procedure adjusting asynchrony window to maintain ~75% correct response rate

### Requirement 3: Somatic Bias (β) Estimation

**User Story:** As a researcher, I want to measure somatic bias through dual-modality oddball tasks, so that I can quantify the relative weighting of interoceptive versus exteroceptive information.

#### Acceptance Criteria

1. WHEN the dual-modality oddball task starts THEN the system SHALL present 120 trials over approximately 12 minutes with matched-precision stimuli
2. WHEN presenting interoceptive deviants THEN the system SHALL deliver brief CO₂ puffs (10% CO₂) or heartbeat-synchronized flashes
3. WHEN presenting exteroceptive deviants THEN the system SHALL show rare visual Gabor orientations
4. WHEN calibrating stimuli THEN the system SHALL ensure Πₑ ≈ Πᵢ through separate staircase procedures
5. WHEN processing EEG data THEN the system SHALL extract P3b amplitude to both interoceptive and exteroceptive deviants
6. WHEN calculating β THEN the system SHALL compute the ratio (P3b_interoceptive / P3b_exteroceptive) under neutral context
7. WHEN controlling for artifacts THEN the system SHALL use bite bar or chin rest, standardized puff durations (<500 ms), and robust artifact rejection pipeline

### Requirement 4: Hierarchical Bayesian Model Fitting

**User Story:** As a researcher, I want to jointly fit all behavioral and neural data using hierarchical Bayesian methods, so that I can obtain reliable parameter estimates with uncertainty quantification.

#### Acceptance Criteria

1. WHEN fitting the model THEN the system SHALL use Stan or PyMC3 for hierarchical Bayesian framework implementation
2. WHEN modeling surprise accumulation THEN the system SHALL implement dSₜ/dt = –Sₜ/τ + f(Πₑ·|εₑ|, β·Πᵢ·|εᵢ|)
3. WHEN calculating ignition probability THEN the system SHALL use Bₜ = σ(α(Sₜ – θₜ))
4. WHEN generating output THEN the system SHALL provide individualized θ₀, Πᵢ, and β estimates with 95% credible intervals
5. WHEN validating reliability THEN the system SHALL achieve test-retest ICC > 0.75 over 1 week period
6. WHEN handling individual differences THEN the system SHALL model response criterion variations within the Bayesian fitting procedure

### Requirement 5: Parameter Recovery Validation

**User Story:** As a researcher, I want to validate the computational pipeline through parameter recovery studies, so that I can ensure the system can accurately recover known ground-truth parameters.

#### Acceptance Criteria

1. WHEN conducting parameter recovery THEN the system SHALL simulate 100 synthetic datasets with known ground-truth parameters
2. WHEN simulating data THEN the system SHALL incorporate realistic trial-by-trial noise and physiological artifacts matching EEG and pupillometry characteristics
3. WHEN validating recovery accuracy THEN the system SHALL achieve Pearson correlations r > 0.85 for θ₀ and β, and r > 0.75 for Πᵢ
4. WHEN comparing recovered vs true parameters THEN the system SHALL generate comprehensive validation reports with correlation matrices and error distributions
5. IF parameter recovery fails validation criteria THEN the system SHALL flag the pipeline as requiring refinement before empirical data collection

### Requirement 6: Predictive Validity Testing

**User Story:** As a researcher, I want to test predictive validity on independent tasks, so that I can demonstrate clinical utility of the extracted parameters.

#### Acceptance Criteria

1. WHEN testing Πᵢ validity THEN the system SHALL predict performance disruption on emotional interference tasks (emotional Stroop/flanker)
2. WHEN testing θ₀ validity THEN the system SHALL predict attentional lapses and reaction time variability on Continuous Performance Task
3. WHEN testing β validity THEN the system SHALL correlate with validated somatic symptom questionnaires (Body Vigilance Scale)
4. WHEN comparing predictive power THEN the system SHALL outperform traditional measures (trait anxiety, EEG theta/beta ratio, raw heartbeat accuracy)
5. WHEN generating validity reports THEN the system SHALL provide statistical comparisons and effect size calculations

### Requirement 7: Real-time Data Processing and Quality Control

**User Story:** As a researcher, I want real-time data processing with quality control, so that I can ensure data integrity during collection and provide immediate feedback.

#### Acceptance Criteria

1. WHEN collecting EEG data THEN the system SHALL process signals in real-time with artifact detection and rejection
2. WHEN monitoring data quality THEN the system SHALL provide live feedback on electrode impedances and signal quality
3. WHEN detecting artifacts THEN the system SHALL apply FASTER algorithm for automated artifact rejection
4. WHEN processing pupillometry THEN the system SHALL handle blink artifacts and provide real-time pupil diameter measurements
5. WHEN synchronizing data streams THEN the system SHALL maintain precise timing alignment between EEG, pupillometry, and behavioral responses
6. IF data quality falls below threshold THEN the system SHALL alert the operator and suggest corrective actions

### Requirement 8: User Interface and Experiment Control

**User Story:** As a researcher, I want an intuitive interface for experiment control and monitoring, so that I can efficiently run sessions and monitor participant progress.

#### Acceptance Criteria

1. WHEN starting a session THEN the system SHALL provide a unified interface for all three parameter estimation tasks
2. WHEN monitoring progress THEN the system SHALL display real-time task completion, data quality metrics, and estimated parameters
3. WHEN configuring experiments THEN the system SHALL allow customization of task parameters, stimulus intensities, and timing
4. WHEN managing participants THEN the system SHALL handle participant IDs, session scheduling, and data organization
5. WHEN generating reports THEN the system SHALL create comprehensive session summaries with parameter estimates and quality metrics
6. IF technical issues occur THEN the system SHALL provide clear error messages and recovery options