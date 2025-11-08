# Implementation Plan

- [x] 1. Set up project structure and core interfaces
  - Create directory structure for models, services, tasks, signal processing, and statistical components
  - Define base interfaces and abstract classes for extensibility
  - Set up configuration management for task parameters and system settings
  - _Requirements: 8.3, 8.4_

- [x] 2. Implement parameter estimation specific data models
  - [x] 2.1 Create parameter estimation data model classes
    - Write TrialData, BehavioralResponse, QualityMetrics dataclasses for parameter estimation tasks
    - Implement ParameterEstimates and ParameterDistribution models with credible intervals
    - Add HeartbeatTrialResult, DetectionTrialResult, OddballTrialResult models
    - Add data validation methods and type checking for parameter estimation workflows
    - _Requirements: 1.2, 2.2, 3.2, 4.4_

  - [x] 2.2 Extend database schema for parameter estimation
    - Create parameter estimation specific tables (sessions, trials, parameter_estimates)
    - Write database migration scripts for new parameter estimation schema
    - Extend existing data access layer with parameter estimation CRUD operations
    - _Requirements: 8.4, 8.5_

  - [x]* 2.3 Write unit tests for parameter estimation data models


    - Create unit tests for parameter estimation data validation and serialization
    - Test parameter estimation database operations and constraint enforcement
    - _Requirements: 2.2, 8.4_

- [x] 3. Implement adaptive staircase algorithms and stimulus control
  - [x] 3.1 Create QUEST+ adaptive staircase implementation
    - Implement QuestPlusStaircase class for optimal stimulus selection
    - Write adaptive threshold estimation algorithms for detection tasks
    - Add staircase state management and persistence across trials
    - Create staircase convergence monitoring and stopping criteria
    - _Requirements: 1.6, 2.7, 3.4_

  - [x] 3.2 Implement stimulus generators for parameter estimation tasks
    - Write GaborPatchGenerator for visual detection task with intensity control
    - Create ToneGenerator for auditory detection and heartbeat synchronization
    - Implement CO2PuffController for interoceptive oddball stimuli with safety interlocks
    - Add HeartbeatSynchronizer for cardiac-locked stimulus presentation
    - _Requirements: 1.1, 2.1, 3.2, 3.3_

  - [x] 3.3 Build task control and timing infrastructure
    - Create PrecisionTimer for microsecond-accurate stimulus timing
    - Implement TaskStateMachine for session flow control across all three tasks
    - Write ResponseCollector with confidence rating support and reaction time measurement
    - Add SessionManager for participant tracking and task sequencing
    - _Requirements: 1.1, 2.1, 3.1, 8.1, 8.4_

  - [x]* 3.4 Write unit tests for adaptive algorithms and stimulus systems

    - Test QUEST+ convergence properties with synthetic data
    - Validate stimulus timing accuracy and parameter control
    - Test adaptive algorithm performance under various conditions
    - _Requirements: 1.6, 2.7, 3.4_

- [x] 4. Implement multi-modal data acquisition interfaces
  - [x] 4.1 Create EEG data acquisition system
    - Write EEGInterface class with real-time streaming and buffering
    - Implement ArtifactDetector for amplitude, gradient, and flatline detection
    - Add channel management and reference scheme configuration
    - Create real-time data callbacks and quality monitoring
    - _Requirements: 7.1, 7.2, 7.5_

  - [x] 4.2 Implement high-speed pupillometry acquisition
    - Write PupillometryInterface for high-speed pupillometry (1000 Hz)
    - Add BlinkDetector with velocity and missing data detection methods
    - Implement ArtifactInterpolator with linear and cubic spline interpolation
    - Create BaselineCorrector and LuminanceCorrector for signal processing
    - _Requirements: 2.3, 7.4, 7.5_

  - [x] 4.3 Build cardiac signal acquisition and processing
    - Implement PhysiologicalMonitoring for ECG/PPG signal acquisition
    - Write HeartRateMonitor with R-peak detection and HRV analysis
    - Add multi-modal biosignal integration (ECG, SCR, respiration)
    - Create synchronized data streaming across physiological signals
    - _Requirements: 2.4, 7.5_

  - [x] 4.4 Create behavioral response collection system
    - Write ResponseCollector for keyboard/button responses with reaction time measurement
    - Implement confidence rating collection with customizable scales
    - Add response validation and timing accuracy monitoring
    - Create response queue management with threading support
    - _Requirements: 1.2, 2.2, 3.2_


  - [ ]* 4.5 Write integration tests for multi-modal data acquisition
    - Test synchronization accuracy between EEG, pupillometry, and cardiac signals
    - Validate data streaming performance and latency under high-throughput conditions
    - Test hardware failure recovery and graceful degradation
    - _Requirements: 7.5_

- [x] 5. Implement real-time signal processing pipeline





  - [x] 5.1 Build EEG signal processing components


    - Implement EEGProcessor with real-time filtering (0.1-30 Hz bandpass) using scipy filters
    - Write FASTERArtifactDetector for automated artifact detection and rejection
    - Create ERPExtractor for P3b (250-500ms at Pz) and HEP (250-400ms post R-peak) extraction
    - Add EpochExtractor and BaselineCorrector for trial-based ERP analysis
    - _Requirements: 1.4, 2.4, 3.5, 7.1, 7.3_


  - [x] 5.2 Create pupillometry signal processing pipeline

    - Implement PupillometryProcessor integrating existing blink detection and interpolation
    - Write PupilFeatureExtractor for post-stimulus windows (200-500ms) with peak, mean, time-to-peak metrics
    - Add PupilMetricsCalculator for dilation metrics and area under curve computation
    - Create PupilQualityScorer for comprehensive data quality assessment
    - _Requirements: 2.3, 2.6, 7.4_

  - [x] 5.3 Build cardiac signal processing pipeline


    - Implement CardiacProcessor integrating existing R-peak detection with additional algorithms
    - Write HRVAnalyzer extending existing HRV metrics with frequency domain analysis
    - Add HEPExtractor for heartbeat-evoked potential epoch extraction around R-peaks
    - Create CardiacQualityAssessor for signal quality assessment and beat validation
    - _Requirements: 2.4, 2.6_

  - [x] 5.4 Implement real-time quality control system


    - Write SignalQualityMonitor integrating EEG, pupil, and cardiac quality metrics
    - Create unified ArtifactDetector coordinating across all modalities
    - Implement AdaptiveProtocolManager for quality-based protocol adjustments
    - Add OperatorNotificationSystem for real-time alerts and recovery suggestions
    - _Requirements: 7.1, 7.2, 7.6_


  - [ ]* 5.5 Write unit tests for signal processing pipeline
    - Test filtering algorithms and artifact rejection with synthetic EEG data
    - Validate feature extraction accuracy with known P3b and HEP signatures
    - Test pupil processing with simulated blink artifacts and quality degradation
    - _Requirements: 1.4, 2.4, 3.5_
-

- [x] 6. Implement the three core behavioral task classes




  - [x] 6.1 Create detection task for θ₀ estimation


    - Write DetectionTask class integrating QuestPlusStaircase and stimulus generators
    - Implement visual (Gabor) and auditory (tone) stimulus presentation with PrecisionTimer
    - Add BehavioralThresholdCalculator for 50% detection point estimation from staircase data
    - Create P3bCorrelationValidator for threshold-P3b amplitude correlation validation
    - Integrate with SessionManager and ParameterEstimationDAO for data persistence
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 6.2 Build heartbeat detection task for Πᵢ estimation

    - Write HeartbeatDetectionTask integrating HeartbeatSynchronizer and ToneGenerator
    - Implement synchronous/asynchronous tone presentation relative to R-peaks
    - Add DPrimeCalculator for heartbeat detection accuracy (d′) calculation
    - Create ConfidenceAnalyzer for confidence rating collection and metacognitive analysis
    - Implement AdaptiveAsynchronyAdjuster for poor performers (d′ < 0.5)
    - Integrate pupillometry and HEP extraction for neural priors
    - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7_

  - [x] 6.3 Create dual-modality oddball task for β estimation

    - Write DualModalityOddballTask with precision-matched stimulus calibration
    - Implement InteroceptiveDeviantGenerator using CO2PuffController and heartbeat flashes
    - Add ExteroceptiveDeviantGenerator using GaborPatchGenerator and ToneGenerator
    - Create StimulusCalibrator to ensure Πₑ ≈ Πᵢ through separate staircase procedures
    - Implement P3bRatioCalculator for interoceptive/exteroceptive P3b ratio computation
    - Integrate with EEG processing for P3b extraction

    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ]* 6.4 Write integration tests for behavioral task implementations
    - Test task timing accuracy and stimulus presentation synchronization
    - Validate adaptive algorithm convergence and performance across tasks
    - Test task switching and session management functionality
    - _Requirements: 1.6, 2.7, 3.4_

- [x] 7. Implement hierarchical Bayesian modeling and parameter estimation




  - [x] 7.1 Create hierarchical Bayesian model framework

    - Write HierarchicalBayesianModel class with Stan model definition for joint parameter estimation
    - Implement SurpriseAccumulator with equation: dSₜ/dt = –Sₜ/τ + f(Πₑ·|εₑ|, β·Πᵢ·|εᵢ|)
    - Add IgnitionProbabilityCalculator with: Bₜ = σ(α(Sₜ – θₜ))
    - Create StanModelCompiler for PyMC3/Stan integration with model compilation and caching
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 7.2 Build joint parameter estimation pipeline


    - Implement JointParameterFitter for simultaneous behavioral and neural data fitting
    - Write ParameterExtractor for θ₀, Πᵢ, and β extraction with 95% credible intervals
    - Add ConvergenceDiagnostics for R-hat, effective sample size, and chain mixing assessment
    - Create IndividualParameterEstimator for personalized parameter output with uncertainty quantification
    - _Requirements: 4.4, 4.6_

  - [x] 7.3 Implement parameter recovery validation system


    - Write SyntheticDataGenerator with known ground-truth parameters and realistic noise models
    - Create ParameterRecoveryValidator for 100 synthetic dataset simulation and analysis
    - Implement RecoveryAnalyzer with correlation metrics and bias assessment
    - Add ValidationReportGenerator with pass/fail criteria and detailed recovery statistics
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 7.4 Build predictive validity testing framework


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
- [x] 8. Implement user interface and experiment control system




- [ ] 8. Implement user interface and experiment control system

  - [x] 8.1 Create main parameter estimation experiment control interface


    - Write ParameterEstimationGUI with unified interface for all three tasks (detection, heartbeat, oddball)
    - Implement SessionSetupManager and ParticipantManager for session configuration and tracking
    - Add RealTimeProgressMonitor for task completion and data quality display
    - Create TaskParameterConfigurator for adaptive algorithm and stimulus parameter adjustment
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 8.2 Build real-time multi-modal monitoring dashboard


    - Implement LiveEEGMonitor for real-time EEG signal quality and P3b/HEP display
    - Add PupillometryMonitor and CardiacMonitor for live physiological signal monitoring
    - Create RealTimeParameterEstimateUpdater for ongoing Bayesian parameter updates
    - Write QualityAlertSystem for automated data quality issue detection and notifications
    - _Requirements: 8.2, 7.2, 7.6_

  - [x] 8.3 Create comprehensive reporting and visualization system


    - Write SessionReportGenerator for detailed session summaries with all three parameter estimates
    - Implement ParameterVisualizationEngine with credible interval plots and posterior distributions
    - Add DataQualitySummarizer for artifact statistics and signal quality metrics across modalities
    - Create DataExporter for analysis-ready output (CSV, HDF5, BIDS format)
    - _Requirements: 8.5, 4.4_

  - [x] 8.4 Implement robust error handling and recovery system


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
-

- [x] 9. Implement system integration, validation, and deployment




  - [x] 9.1 Create system configuration and deployment infrastructure

    - Write InstallationManager with automated dependency installation (LSL, Stan, eye tracker SDKs)
    - Create HardwareConfigurationManager for different EEG systems, eye trackers, and cardiac sensors
    - Add SystemRequirementsValidator for compatibility checking and performance assessment
    - Implement DeploymentValidator with automated testing pipeline for new installations
    - _Requirements: 8.3, 8.4_


  - [x] 9.2 Build comprehensive parameter estimation validation pipeline

    - Integrate ParameterRecoveryValidator into deployment workflow with automated pass/fail criteria
    - Create ReliabilityTester for automated test-retest reliability assessment (ICC > 0.75 target)
    - Implement PredictiveValidityPipeline for systematic validation against independent measures
    - Add PerformanceBenchmarker for real-time processing optimization and bottleneck identification
    - _Requirements: 4.5, 5.5, 6.5_


  - [x] 9.3 Create comprehensive documentation and training system

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