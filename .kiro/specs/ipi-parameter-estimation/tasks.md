# Implementation Plan

- [x] 1. Set up project structure and core interfaces
  - Create directory structure for models, services, tasks, signal processing, and statistical components
  - Define base interfaces and abstract classes for extensibility
  - Set up configuration management for task parameters and system settings
  - _Requirements: 8.3, 8.4_

- [ ] 2. Implement parameter estimation specific data models
  - [ ] 2.1 Create parameter estimation data model classes
    - Write TrialData, BehavioralResponse, QualityMetrics dataclasses for parameter estimation tasks
    - Implement ParameterEstimates and ParameterDistribution models with credible intervals
    - Add HeartbeatTrialResult, DetectionTrialResult, OddballTrialResult models
    - Add data validation methods and type checking for parameter estimation workflows
    - _Requirements: 1.2, 2.2, 3.2, 4.4_

  - [ ] 2.2 Extend database schema for parameter estimation
    - Create parameter estimation specific tables (sessions, trials, parameter_estimates)
    - Write database migration scripts for new parameter estimation schema
    - Extend existing data access layer with parameter estimation CRUD operations
    - _Requirements: 8.4, 8.5_

  - [ ]* 2.3 Write unit tests for parameter estimation data models
    - Create unit tests for parameter estimation data validation and serialization
    - Test parameter estimation database operations and constraint enforcement
    - _Requirements: 2.2, 8.4_

- [ ] 3. Implement adaptive staircase algorithms and stimulus control
  - [ ] 3.1 Create QUEST+ adaptive staircase implementation
    - Implement QuestPlusStaircase class for optimal stimulus selection
    - Write adaptive threshold estimation algorithms for detection tasks
    - Add staircase state management and persistence across trials
    - Create staircase convergence monitoring and stopping criteria
    - _Requirements: 1.6, 2.7, 3.4_

  - [ ] 3.2 Implement stimulus generators for parameter estimation tasks
    - Write GaborPatchGenerator for visual detection task with intensity control
    - Create ToneGenerator for auditory detection and heartbeat synchronization
    - Implement CO2PuffController for interoceptive oddball stimuli with safety interlocks
    - Add HeartbeatSynchronizer for cardiac-locked stimulus presentation
    - _Requirements: 1.1, 2.1, 3.2, 3.3_

  - [ ] 3.3 Build task control and timing infrastructure
    - Create PrecisionTimer for microsecond-accurate stimulus timing
    - Implement TaskStateMachine for session flow control across all three tasks
    - Write ResponseCollector with confidence rating support and reaction time measurement
    - Add SessionManager for participant tracking and task sequencing
    - _Requirements: 1.1, 2.1, 3.1, 8.1, 8.4_

  - [ ]* 3.4 Write unit tests for adaptive algorithms and stimulus systems
    - Test QUEST+ convergence properties with synthetic data
    - Validate stimulus timing accuracy and parameter control
    - Test adaptive algorithm performance under various conditions
    - _Requirements: 1.6, 2.7, 3.4_

- [ ] 4. Implement multi-modal data acquisition interfaces
  - [ ] 4.1 Create EEG data acquisition system
    - Write EEGAcquisition class with LSL (Lab Streaming Layer) integration for real-time EEG
    - Implement manufacturer-specific API connections (BrainVision, EGI, Biosemi)
    - Add ElectrodeImpedanceMonitor for real-time impedance checking and quality assessment
    - Create EEGDataBuffer for real-time data buffering and streaming with configurable window sizes
    - _Requirements: 7.1, 7.2, 7.5_

  - [ ] 4.2 Implement high-speed pupillometry acquisition
    - Write EyeTrackerInterface for high-speed pupillometry (1000 Hz) with multiple tracker support
    - Add real-time BlinkDetector and PupilQualityMonitor for data quality assessment
    - Implement CalibrationManager for eye tracker calibration and drift correction procedures
    - Create PupilDataExtractor for real-time pupil diameter extraction and preprocessing
    - _Requirements: 2.3, 7.4, 7.5_

  - [ ] 4.3 Build cardiac signal acquisition and processing
    - Implement CardiacAcquisition for ECG/PPG signal acquisition with multiple sensor support
    - Write RPeakDetector using Pan-Tompkins algorithm and backup detection methods
    - Add HeartRateVariabilityAnalyzer for real-time HRV analysis and cardiac timing
    - Create CardiacSynchronizer for heartbeat-locked stimulus presentation with backup manual marking
    - _Requirements: 2.4, 7.5_

  - [ ] 4.4 Create behavioral response collection system
    - Write ResponseHandler for keyboard/button responses with microsecond timing precision
    - Implement ConfidenceRatingCollector with customizable rating scales and interfaces
    - Add ResponseValidator for response quality checking and outlier detection
    - Create TrialFeedbackSystem for real-time participant feedback and performance monitoring
    - _Requirements: 1.2, 2.2, 3.2_

  - [ ]* 4.5 Write integration tests for multi-modal data acquisition
    - Test synchronization accuracy between EEG, pupillometry, and cardiac signals
    - Validate data streaming performance and latency under high-throughput conditions
    - Test hardware failure recovery and graceful degradation
    - _Requirements: 7.5_

- [ ] 5. Implement real-time signal processing pipeline
  - [ ] 5.1 Build EEG signal processing components
    - Implement EEGProcessor with real-time filtering (0.1-30 Hz bandpass) using scipy filters
    - Write FASTERArtifactDetector for automated artifact detection and rejection
    - Create ERPExtractor for P3b (250-500ms at Pz) and HEP (250-400ms post R-peak) extraction
    - Add EpochExtractor and BaselineCorrector for trial-based analysis
    - _Requirements: 1.4, 2.4, 3.5, 7.1, 7.3_

  - [ ] 5.2 Create pupillometry signal processing pipeline
    - Implement PupillometryProcessor with blink detection and cubic spline interpolation
    - Write PupilBaselineCorrector and PupilFeatureExtractor (200-500ms post-stimulus windows)
    - Add PupilMetricsCalculator for dilation metrics (peak, mean, time-to-peak, area under curve)
    - Create PupilQualityScorer for data quality assessment and artifact flagging
    - _Requirements: 2.3, 2.6, 7.4_

  - [ ] 5.3 Build cardiac signal processing pipeline
    - Implement CardiacProcessor with multiple R-peak detection algorithms (Pan-Tompkins, Hamilton, Christov)
    - Write HRVAnalyzer for heart rate variability analysis and cardiac timing extraction
    - Add HEPExtractor for heartbeat-evoked potential epoch extraction around R-peaks
    - Create CardiacQualityAssessor for signal quality assessment and beat validation
    - _Requirements: 2.4, 2.6_

  - [ ] 5.4 Implement real-time quality control system
    - Write SignalQualityMonitor for real-time quality assessment with configurable thresholds
    - Create ArtifactDetector for automated artifact detection across EEG, pupil, and cardiac modalities
    - Implement AdaptiveProtocolManager for quality-based data collection protocol adjustments
    - Add OperatorNotificationSystem for real-time quality alerts and recovery suggestions
    - _Requirements: 7.1, 7.2, 7.6_

  - [ ]* 5.5 Write unit tests for signal processing pipeline
    - Test filtering algorithms and artifact rejection with synthetic EEG data
    - Validate feature extraction accuracy with known P3b and HEP signatures
    - Test pupil processing with simulated blink artifacts and quality degradation
    - _Requirements: 1.4, 2.4, 3.5_

- [ ] 6. Implement the three core behavioral task classes
  - [ ] 6.1 Create detection task for θ₀ estimation
    - Write DetectionTask class with QUEST+ adaptive staircase integration
    - Implement visual (Gabor patches) and auditory (tones) stimulus presentation with precise timing
    - Add BehavioralThresholdCalculator for 50% detection point estimation
    - Create P3bCorrelationValidator for threshold-P3b amplitude correlation validation
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ] 6.2 Build heartbeat detection task for Πᵢ estimation
    - Write HeartbeatDetectionTask with real-time cardiac synchronization
    - Implement synchronous/asynchronous tone presentation relative to R-peaks
    - Add DPrimeCalculator for heartbeat detection accuracy (d′) calculation
    - Create ConfidenceAnalyzer for confidence rating collection and metacognitive analysis
    - Implement AdaptiveAsynchronyAdjuster for poor performers (d′ < 0.5)
    - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7_

  - [ ] 6.3 Create dual-modality oddball task for β estimation
    - Write DualModalityOddballTask with precision-matched stimulus calibration
    - Implement InteroceptiveDeviantGenerator (CO₂ puffs, heartbeat-synchronized flashes)
    - Add ExteroceptiveDeviantGenerator (rare Gabor orientations, auditory deviants)
    - Create StimulusCalibrator to ensure Πₑ ≈ Πᵢ through separate staircase procedures
    - Implement P3bRatioCalculator for interoceptive/exteroceptive P3b ratio computation
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ]* 6.4 Write integration tests for behavioral task implementations
    - Test task timing accuracy and stimulus presentation synchronization
    - Validate adaptive algorithm convergence and performance across tasks
    - Test task switching and session management functionality
    - _Requirements: 1.6, 2.7, 3.4_

- [ ] 7. Implement hierarchical Bayesian modeling and parameter estimation
  - [ ] 7.1 Create hierarchical Bayesian model framework
    - Write HierarchicalBayesianModel class with Stan model definition for joint parameter estimation
    - Implement SurpriseAccumulator with equation: dSₜ/dt = –Sₜ/τ + f(Πₑ·|εₑ|, β·Πᵢ·|εᵢ|)
    - Add IgnitionProbabilityCalculator with: Bₜ = σ(α(Sₜ – θₜ))
    - Create StanModelCompiler for PyMC3/Stan integration with model compilation and caching
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 7.2 Build joint parameter estimation pipeline
    - Implement JointParameterFitter for simultaneous behavioral and neural data fitting
    - Write ParameterExtractor for θ₀, Πᵢ, and β extraction with 95% credible intervals
    - Add ConvergenceDiagnostics for R-hat, effective sample size, and chain mixing assessment
    - Create IndividualParameterEstimator for personalized parameter output with uncertainty quantification
    - _Requirements: 4.4, 4.6_

  - [ ] 7.3 Implement parameter recovery validation system
    - Write SyntheticDataGenerator with known ground-truth parameters and realistic noise models
    - Create ParameterRecoveryValidator for 100 synthetic dataset simulation and analysis
    - Implement RecoveryAnalyzer with correlation metrics and bias assessment
    - Add ValidationReportGenerator with pass/fail criteria and detailed recovery statistics
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 7.4 Build predictive validity testing framework
    - Implement EmotionalInterferenceTask (Stroop/flanker) for Πᵢ validation testing
    - Create ContinuousPerformanceTask for θ₀ validation and attentional lapse prediction
    - Add BodyVigilanceScaleAnalyzer for β validation through somatic symptom correlation
    - Write PredictivePowerComparator for comparison against traditional measures (trait anxiety, EEG ratios)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 7.5 Write unit tests for statistical modeling components
    - Test parameter recovery accuracy with known synthetic datasets
    - Validate Bayesian model convergence and numerical stability under various conditions
    - Test edge cases and boundary conditions for parameter estimation
    - _Requirements: 4.5, 5.3_

- [ ] 8. Implement user interface and experiment control system
  - [ ] 8.1 Create main parameter estimation experiment control interface
    - Write ParameterEstimationGUI with unified interface for all three tasks (detection, heartbeat, oddball)
    - Implement SessionSetupManager and ParticipantManager for session configuration and tracking
    - Add RealTimeProgressMonitor for task completion and data quality display
    - Create TaskParameterConfigurator for adaptive algorithm and stimulus parameter adjustment
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ] 8.2 Build real-time multi-modal monitoring dashboard
    - Implement LiveEEGMonitor for real-time EEG signal quality and P3b/HEP display
    - Add PupillometryMonitor and CardiacMonitor for live physiological signal monitoring
    - Create RealTimeParameterEstimateUpdater for ongoing Bayesian parameter updates
    - Write QualityAlertSystem for automated data quality issue detection and notifications
    - _Requirements: 8.2, 7.2, 7.6_

  - [ ] 8.3 Create comprehensive reporting and visualization system
    - Write SessionReportGenerator for detailed session summaries with all three parameter estimates
    - Implement ParameterVisualizationEngine with credible interval plots and posterior distributions
    - Add DataQualitySummarizer for artifact statistics and signal quality metrics across modalities
    - Create DataExporter for analysis-ready output (CSV, HDF5, BIDS format)
    - _Requirements: 8.5, 4.4_

  - [ ] 8.4 Implement robust error handling and recovery system
    - Write HardwareFailureHandler for graceful degradation when EEG/eye tracker/cardiac sensors fail
    - Add SessionStateManager for pause/resume functionality with complete state preservation
    - Implement AutomaticBackupSystem for real-time data backup and recovery
    - Create UserGuidanceSystem with clear error messages and step-by-step recovery instructions
    - _Requirements: 8.6, 7.6_

  - [ ]* 8.5 Write integration tests for complete user interface system
    - Test end-to-end parameter estimation workflow with simulated participants and data
    - Validate error handling, recovery procedures, and graceful degradation scenarios
    - Test multi-modal data synchronization and real-time processing under various conditions
    - _Requirements: 8.1, 8.6_

- [ ] 9. Implement system integration, validation, and deployment
  - [ ] 9.1 Create system configuration and deployment infrastructure
    - Write InstallationManager with automated dependency installation (LSL, Stan, eye tracker SDKs)
    - Create HardwareConfigurationManager for different EEG systems, eye trackers, and cardiac sensors
    - Add SystemRequirementsValidator for compatibility checking and performance assessment
    - Implement DeploymentValidator with automated testing pipeline for new installations
    - _Requirements: 8.3, 8.4_

  - [ ] 9.2 Build comprehensive parameter estimation validation pipeline
    - Integrate ParameterRecoveryValidator into deployment workflow with automated pass/fail criteria
    - Create ReliabilityTester for automated test-retest reliability assessment (ICC > 0.75 target)
    - Implement PredictiveValidityPipeline for systematic validation against independent measures
    - Add PerformanceBenchmarker for real-time processing optimization and bottleneck identification
    - _Requirements: 4.5, 5.5, 6.5_

  - [ ] 9.3 Create comprehensive documentation and training system
    - Write ParameterEstimationUserManual with detailed protocols for all three tasks
    - Create TroubleshootingGuide with hardware-specific solutions and FAQ
    - Add VideoTutorialGenerator for system operation and data interpretation training
    - Implement InSystemHelpSystem with context-sensitive guidance and tooltips
    - _Requirements: 8.1, 8.6_

  - [ ]* 9.4 Write comprehensive end-to-end system validation tests
    - Test complete parameter estimation pipeline with synthetic participants across all three tasks
    - Validate system performance under various hardware configurations and failure conditions
    - Test parameter recovery, reliability, and predictive validity under realistic conditions
    - _Requirements: 4.5, 5.5, 6.5_