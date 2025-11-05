# Implementation Plan

- [ ] 1. Set up project structure and core interfaces
  - Create directory structure for models, services, tasks, signal processing, and statistical components
  - Define base interfaces and abstract classes for extensibility
  - Set up configuration management for task parameters and system settings
  - _Requirements: 8.3, 8.4_

- [ ] 2. Implement core data models and validation
  - [ ] 2.1 Create data model classes for trials, sessions, and parameter estimates
    - Write TrialData, BehavioralResponse, QualityMetrics dataclasses
    - Implement ParameterEstimates and ParameterDistribution models
    - Add data validation methods and type checking
    - _Requirements: 1.2, 2.2, 3.2, 4.4_

  - [ ] 2.2 Implement database schema and ORM integration
    - Create SQLAlchemy models for sessions, trials, and parameter estimates tables
    - Write database migration scripts and connection management
    - Implement data access layer with CRUD operations
    - _Requirements: 8.4, 8.5_

  - [ ]* 2.3 Write unit tests for data models
    - Create unit tests for data validation and serialization
    - Test database operations and constraint enforcement
    - _Requirements: 2.2, 8.4_

- [ ] 3. Implement stimulus generation and task control
  - [ ] 3.1 Create adaptive staircase algorithms
    - Implement QUEST+ algorithm for optimal stimulus selection
    - Write adaptive threshold estimation for detection tasks
    - Add staircase state management and persistence
    - _Requirements: 1.6, 2.7, 3.4_

  - [ ] 3.2 Implement stimulus generators for all modalities
    - Write visual stimulus generator for Gabor patches with intensity control
    - Create auditory tone generator with precise timing
    - Implement CO₂ puff controller with safety interlocks
    - Add heartbeat-synchronized stimulus presentation
    - _Requirements: 1.1, 2.1, 3.2, 3.3_

  - [ ] 3.3 Build task control and timing systems
    - Create precise timing controller with microsecond accuracy
    - Implement task state machine for session flow control
    - Write response collection system with confidence ratings
    - Add session management and participant tracking
    - _Requirements: 1.1, 2.1, 3.1, 8.1, 8.4_

  - [ ]* 3.4 Write unit tests for stimulus and timing systems
    - Test stimulus parameter accuracy and timing precision
    - Validate adaptive algorithm convergence properties
    - _Requirements: 1.6, 2.7, 3.4_

- [ ] 4. Implement data acquisition interfaces
  - [ ] 4.1 Create EEG data acquisition interface
    - Write LSL (Lab Streaming Layer) integration for real-time EEG
    - Implement manufacturer-specific API connections (BrainVision, EGI, etc.)
    - Add electrode impedance monitoring and quality assessment
    - Create real-time data buffering and streaming
    - _Requirements: 7.1, 7.2, 7.5_

  - [ ] 4.2 Implement pupillometry data acquisition
    - Write eye tracker interface for high-speed pupillometry (1000 Hz)
    - Add real-time blink detection and data quality monitoring
    - Implement calibration procedures and drift correction
    - Create pupil diameter extraction and preprocessing
    - _Requirements: 2.3, 7.4, 7.5_

  - [ ] 4.3 Build cardiac signal processing
    - Implement ECG/PPG signal acquisition and R-peak detection
    - Write real-time heart rate variability analysis
    - Add cardiac timing synchronization for stimulus presentation
    - Create backup sensor switching and manual peak marking
    - _Requirements: 2.4, 7.5_

  - [ ] 4.4 Create behavioral response collection
    - Write keyboard/button response handler with precise timing
    - Implement confidence rating collection interface
    - Add response validation and quality checking
    - Create trial-by-trial feedback system
    - _Requirements: 1.2, 2.2, 3.2_

  - [ ]* 4.5 Write integration tests for data acquisition
    - Test multi-modal synchronization accuracy
    - Validate data streaming performance under load
    - _Requirements: 7.5_

- [ ] 5. Implement signal processing pipeline
  - [ ] 5.1 Build EEG signal processing components
    - Implement real-time filtering (0.1-30 Hz bandpass)
    - Write FASTER artifact detection and rejection algorithm
    - Create ERP extraction for P3b (250-500ms at Pz) and HEP (250-400ms post R-peak)
    - Add epoch extraction and baseline correction
    - _Requirements: 1.4, 2.4, 3.5, 7.1, 7.3_

  - [ ] 5.2 Create pupillometry signal processing
    - Implement blink detection and cubic spline interpolation
    - Write baseline correction and feature extraction (200-500ms post-stimulus)
    - Add pupil dilation metrics calculation (peak, mean, time-to-peak)
    - Create data quality scoring and artifact flagging
    - _Requirements: 2.3, 2.6, 7.4_

  - [ ] 5.3 Build cardiac signal processing
    - Implement R-peak detection algorithms (Pan-Tompkins, etc.)
    - Write HRV analysis and cardiac timing extraction
    - Add heartbeat-evoked potential epoch extraction
    - Create cardiac data quality assessment
    - _Requirements: 2.4, 2.6_

  - [ ] 5.4 Implement real-time quality control
    - Write real-time signal quality monitoring with threshold alerts
    - Create automated artifact detection across all modalities
    - Implement adaptive data collection protocols based on quality
    - Add operator notification system for quality issues
    - _Requirements: 7.1, 7.2, 7.6_

  - [ ]* 5.5 Write unit tests for signal processing
    - Test filtering and artifact rejection with synthetic data
    - Validate feature extraction accuracy with known signals
    - _Requirements: 1.4, 2.4, 3.5_

- [ ] 6. Implement behavioral task classes
  - [ ] 6.1 Create detection task for θ₀ estimation
    - Write DetectionTask class with adaptive staircase integration
    - Implement visual/auditory stimulus presentation with precise timing
    - Add behavioral threshold calculation (50% detection point)
    - Create P3b amplitude correlation validation
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ] 6.2 Build heartbeat detection task for Πᵢ estimation
    - Write HeartbeatDetectionTask with cardiac synchronization
    - Implement synchronous/asynchronous tone presentation
    - Add d′ calculation for heartbeat detection accuracy
    - Create confidence rating collection and analysis
    - Implement adaptive asynchrony adjustment for poor performers
    - _Requirements: 2.1, 2.2, 2.5, 2.6, 2.7_

  - [ ] 6.3 Create dual-modality oddball task for β estimation
    - Write DualModalityOddballTask with stimulus calibration
    - Implement interoceptive deviants (CO₂ puffs, heartbeat-synchronized flashes)
    - Add exteroceptive deviants (rare Gabor orientations)
    - Create stimulus intensity calibration to ensure Πₑ ≈ Πᵢ
    - Implement P3b ratio calculation (interoceptive/exteroceptive)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [ ]* 6.4 Write integration tests for behavioral tasks
    - Test task timing accuracy and stimulus presentation
    - Validate adaptive algorithm performance
    - _Requirements: 1.6, 2.7, 3.4_

- [ ] 7. Implement statistical modeling and parameter estimation
  - [ ] 7.1 Create hierarchical Bayesian model framework
    - Write Stan model definition for joint parameter estimation
    - Implement surprise accumulation equation: dSₜ/dt = –Sₜ/τ + f(Πₑ·|εₑ|, β·Πᵢ·|εᵢ|)
    - Add ignition probability calculation: Bₜ = σ(α(Sₜ – θₜ))
    - Create PyMC3/Stan integration with model compilation
    - _Requirements: 4.1, 4.2, 4.3_

  - [ ] 7.2 Build parameter estimation pipeline
    - Implement joint fitting of behavioral and neural data
    - Write parameter extraction with 95% credible intervals
    - Add convergence diagnostics (R-hat, effective sample size)
    - Create individual parameter estimate output with uncertainty
    - _Requirements: 4.4, 4.6_

  - [ ] 7.3 Implement parameter recovery validation
    - Write synthetic data generator with known ground-truth parameters
    - Create 100 synthetic dataset simulation with realistic noise
    - Implement parameter recovery analysis with correlation metrics
    - Add validation report generation with pass/fail criteria
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ] 7.4 Build predictive validity testing framework
    - Implement emotional interference task (Stroop/flanker) for Πᵢ validation
    - Create Continuous Performance Task for θ₀ validation
    - Add Body Vigilance Scale correlation analysis for β validation
    - Write predictive power comparison against traditional measures
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 7.5 Write unit tests for statistical models
    - Test parameter recovery with known synthetic data
    - Validate model convergence and numerical stability
    - _Requirements: 4.5, 5.3_

- [ ] 8. Implement user interface and experiment control
  - [ ] 8.1 Create main experiment control interface
    - Write unified GUI for all three parameter estimation tasks
    - Implement session setup and participant management
    - Add real-time progress monitoring and data quality display
    - Create task parameter configuration interface
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ] 8.2 Build real-time monitoring dashboard
    - Implement live EEG signal quality display
    - Add pupillometry and cardiac signal monitoring
    - Create real-time parameter estimate updates
    - Write alert system for data quality issues
    - _Requirements: 8.2, 7.2, 7.6_

  - [ ] 8.3 Create reporting and visualization system
    - Write comprehensive session report generation
    - Implement parameter estimate visualization with credible intervals
    - Add data quality summary and artifact statistics
    - Create export functionality for further analysis
    - _Requirements: 8.5, 4.4_

  - [ ] 8.4 Implement error handling and recovery
    - Write graceful error handling for hardware failures
    - Add session pause/resume functionality with state preservation
    - Implement automatic backup and data recovery
    - Create clear error messages and recovery guidance
    - _Requirements: 8.6, 7.6_

  - [ ]* 8.5 Write integration tests for user interface
    - Test end-to-end workflow with simulated participants
    - Validate error handling and recovery procedures
    - _Requirements: 8.1, 8.6_

- [ ] 9. Implement system integration and deployment
  - [ ] 9.1 Create system configuration and deployment scripts
    - Write installation scripts for all dependencies
    - Create configuration management for different hardware setups
    - Add system requirements validation and compatibility checking
    - Implement automated testing pipeline for deployment validation
    - _Requirements: 8.3, 8.4_

  - [ ] 9.2 Build comprehensive validation pipeline
    - Integrate parameter recovery validation into deployment
    - Create automated reliability testing (test-retest ICC > 0.75)
    - Implement predictive validity testing pipeline
    - Add performance benchmarking and optimization
    - _Requirements: 4.5, 5.5, 6.5_

  - [ ] 9.3 Create documentation and training materials
    - Write comprehensive user manual and protocol documentation
    - Create troubleshooting guides and FAQ
    - Add video tutorials for system operation
    - Implement in-system help and guidance
    - _Requirements: 8.1, 8.6_

  - [ ]* 9.4 Write end-to-end system tests
    - Test complete pipeline with synthetic participants
    - Validate system performance under various conditions
    - _Requirements: 4.5, 5.5, 6.5_