# APGI Framework Tutorials

## Tutorial 1: Getting Started with Your First Experiment

### Objective
Learn to set up and run a basic detection task experiment from start to finish.

### Prerequisites
- APGI Framework installed
- Basic understanding of experimental psychology concepts
- 15 minutes of time

### Step 1: Launch the Application

1. **Start the APGI Framework**
   ```bash
   python launch_gui.py
   ```

2. **Choose Your Experience Level**
   - Beginner: Recommended for first-time users
   - Intermediate: Some familiarity with similar software
   - Advanced: Skip basic tutorials

3. **Complete the Welcome Wizard**
   - Set your preferred data directory
   - Choose default experiment settings
   - Enable auto-save (recommended)

### Step 2: Create a New Experiment

1. **File → New Experiment**
2. **Select Experiment Type**: Detection Task
3. **Basic Configuration**:
   ```
   Participant ID: P001
   Session ID: S001
   Number of Trials: 50
   Modality: Visual
   ```

4. **Advanced Settings** (for now, keep defaults):
   - Stimulus intensity range: 0.01 - 1.0
   - Trial duration: 500ms
   - Response window: 2000ms

### Step 3: Run the Experiment

1. **Click "Start Experiment"**
2. **Read Instructions** carefully
3. **Practice Trial** (optional but recommended)
4. **Main Experiment**:
   - Focus on the center of the screen
   - Press SPACEBAR when you see a stimulus
   - Try to be as accurate as possible
   - Don't worry about speed

5. **Complete All Trials** (approximately 5-10 minutes)

### Step 4: Review Results

1. **Automatic Analysis**: Results appear immediately
2. **Key Metrics to Understand**:
   - **Threshold**: ~0.25 (stimulus intensity at 50% detection)
   - **Confidence**: ±0.05 (statistical uncertainty)
   - **Hit Rate**: ~50% (expected for threshold task)
   - **Mean RT**: ~600ms (typical response time)

3. **Save Results**: File → Save As → "P001_Detection_001.json"

### What You Learned
- How to create and configure an experiment
- How to run a detection task
- How to interpret basic results
- How to save and organize data

---

## Tutorial 2: Data Analysis and Visualization

### Objective
Learn to analyze experimental data and create meaningful visualizations.

### Prerequisites
- Completed Tutorial 1
- Have experimental data available
- 20 minutes of time

### Step 1: Import Your Data

1. **File → Open** → Select your experiment file
2. **Switch to Analysis Tab**
3. **Data Import Options**:
   - Auto-detect columns (recommended)
   - Preview data before import
   - Handle missing values

### Step 2: Basic Statistical Analysis

1. **Descriptive Statistics**:
   - Click "Analyze → Descriptive Statistics"
   - Select variables: Response Time, Accuracy
   - View results: Mean, SD, Min, Max

2. **Response Time Analysis**:
   - **Analyze → Response Times**
   - **Distribution**: Histogram with normal curve overlay
   - **Outliers**: Box plot with outlier detection
   - **Summary**: Mean, median, IQR

3. **Accuracy Analysis**:
   - **Analyze → Accuracy**
   - **Hit Rate**: Percentage of correct detections
   - **Signal Detection**: d' and criterion calculations
   - **Confidence**: Metacognitive awareness

### Step 3: Create Visualizations

1. **Psychometric Curve**:
   - **Visualization → Psychometric Function**
   - X-axis: Stimulus intensity
   - Y-axis: Detection probability
   - **Fit**: Logistic function with confidence intervals

2. **Response Time Distribution**:
   - **Visualization → Response Times**
   - **Plot Type**: Histogram + density curve
   - **Color**: Blue for correct, red for incorrect
   - **Labels**: Add mean and median lines

3. **Learning Curve**:
   - **Visualization → Learning**
   - **X-axis**: Trial number
   - **Y-axis**: Response time or accuracy
   - **Smoothing**: Moving average (window=10)

### Step 4: Export Your Results

1. **Figures**:
   - Right-click any plot → Export
   - **Format**: PNG (600 DPI) for publications
   - **Naming**: Auto-generated with timestamp

2. **Data Tables**:
   - **File → Export Results**
   - **Format**: CSV for Excel/SPSS
   - **Content**: All analysis results

### What You Learned
- How to import and validate experimental data
- How to perform basic statistical analyses
- How to create publication-ready visualizations
- How to export results for further analysis

---

## Tutorial 3: Heartbeat Detection Task

### Objective
Learn to set up and run an interoceptive awareness experiment.

### Prerequisites
- Completed Tutorials 1-2
- Heart rate sensor (optional, can use simulation)
- 25 minutes of time

### Step 1: Equipment Setup

1. **Heartbeat Sensor** (if available):
   - Connect sensor to USB port
   - Test signal quality
   - Verify R-peak detection

2. **Simulation Mode** (if no sensor):
   - **Settings → Simulation Mode**
   - **Heart Rate**: 70 BPM (default)
   - **Variability**: 10% (realistic)

### Step 2: Configure Heartbeat Detection

1. **File → New Experiment**
2. **Select**: Heartbeat Detection Task
3. **Basic Settings**:
   ```
   Participant ID: P001
   Number of Trials: 60
   Asynchrony Window: 300ms
   Confidence Rating: 1-5 scale
   ```

4. **Advanced Settings**:
   - **Synchronous Trials**: 50%
   - **Asynchronous Range**: 200-400ms
   - **Tone Parameters**: 1000Hz, 50ms duration
   - **Response Window**: 3000ms

### Step 3: Calibration

1. **Run Calibration** (automatic):
   - Detect resting heart rate
   - Test tone synchronization
   - Adjust volume levels

2. **Practice Trials**:
   - 5 synchronous trials
   - 5 asynchronous trials
   - Get familiar with the task

### Step 4: Main Experiment

1. **Task Instructions**:
   - "Listen for tones and judge if they occur with your heartbeat"
   - "Rate your confidence in each judgment"
   - "Respond as quickly and accurately as possible"

2. **Trial Structure**:
   ```
   1. Wait for tone (2-5 seconds)
   2. Hear tone (synchronous or asynchronous)
   3. Make judgment (Sync/Async)
   4. Rate confidence (1-5)
   5. Inter-trial interval (1-2 seconds)
   ```

3. **Monitoring**:
   - Real-time heartbeat display
   - Response accuracy tracking
   - Confidence rating distribution

### Step 5: Analyze Results

1. **Signal Detection Analysis**:
   - **d' (d-prime)**: Sensitivity to heartbeat synchrony
   - **Criterion**: Response bias
   - **Hit Rate**: Correct synchronous detection
   - **False Alarm Rate**: Incorrect synchronous responses

2. **Metacognitive Analysis**:
   - **Confidence-Accuracy Correlation**: Metacognitive awareness
   - **Type 2 ROC**: Metacognitive sensitivity
   - **Calibration**: Confidence accuracy

3. **Physiological Correlates**:
   - **Heart Rate Variability**: During task performance
   - **Pupil Dilation**: Cognitive load indicators
   - **Response Times**: Decision processes

### Expected Results

- **d' Range**: 0.5 - 2.0 (individual differences)
- **Criterion**: Slightly conservative (negative values)
- **Confidence-Accuracy Correlation**: 0.2 - 0.6
- **Mean Response Time**: 800-1200ms

### What You Learned
- How to set up physiological monitoring
- How to design interoceptive awareness experiments
- How to analyze signal detection data
- How to assess metacognitive awareness

---

## Tutorial 4: Advanced Analysis with Bayesian Methods

### Objective
Learn to use Bayesian parameter estimation for more sophisticated analysis.

### Prerequisites
- Completed Tutorials 1-3
- Basic understanding of Bayesian statistics
- 30 minutes of time

### Step 1: Bayesian Parameter Estimation

1. **Load Multiple Sessions**:
   - **File → Import Multiple**
   - Select 3-5 sessions from same participant
   - **Merge**: Combine data for hierarchical analysis

2. **Configure Bayesian Analysis**:
   - **Analysis → Bayesian Methods**
   - **Model**: Hierarchical psychometric function
   - **Priors**: Weakly informative (default)
   - **Sampling**: MCMC with 10,000 samples

3. **Run Analysis**:
   - **Convergence Check**: Gelman-Rubin statistic
   - **Effective Sample Size**: >1000 per parameter
   - **Trace Plots**: Visual inspection

### Step 2: Model Comparison

1. **Alternative Models**:
   - **Model 1**: Standard psychometric function
   - **Model 2**: Lapse rate included
   - **Model 3**: Individual differences

2. **Model Evidence**:
   - **WAIC**: Watanabe-Akaike Information Criterion
   - **LOO**: Leave-one-out cross-validation
   - **Bayes Factors**: Model comparison

3. **Model Averaging**:
   - **Weighted Average**: Based on model evidence
   - **Parameter Estimates**: Model-averaged posteriors
   - **Uncertainty**: Incorporates model uncertainty

### Step 3: Predictive Analysis

1. **Posterior Predictive Checks**:
   - **Simulate Data**: From posterior distributions
   - **Compare**: Simulated vs. observed data
   - **Assess**: Model fit and adequacy

2. **Cross-Validation**:
   - **Leave-One-Out**: Predict held-out sessions
   - **Performance Metrics**: Predictive accuracy
   - **Generalization**: To new conditions

### Step 4: Advanced Visualizations

1. **Posterior Distributions**:
   - **Density Plots**: Parameter posteriors
   - **Credible Intervals**: 95% highest density
   - **Trace Plots**: MCMC convergence

2. **Model Comparison Plots**:
   - **WAIC Comparison**: Model ranking
   - **Bayes Factors**: Evidence strength
   - **Posterior Predictives**: Model fits

3. **Hierarchical Results**:
   - **Individual Parameters**: Participant-level
   - **Group Parameters**: Population-level
   - **Shrinkage**: Individual to group

### What You Learned
- How to implement Bayesian parameter estimation
- How to compare competing models
- How to assess model fit and predictive validity
- How to visualize Bayesian analysis results

---

## Tutorial 5: Real-time Monitoring and Live Experiments

### Objective
Learn to set up real-time monitoring for live experiment tracking.

### Prerequisites
- Completed previous tutorials
- Multiple monitors (recommended)
- 20 minutes of time

### Step 1: Set Up Monitoring Dashboard

1. **Tools → Real-time Monitoring**
2. **Configure Dashboard Layout**:
   - **Panel 1**: Live EEG signal
   - **Panel 2**: Response times
   - **Panel 3**: Accuracy tracking
   - **Panel 4**: System resources

3. **Update Settings**:
   - **Refresh Rate**: 10 Hz (default)
   - **Buffer Size**: 1000 samples
   - **Alerts**: Enable threshold alerts

### Step 2: Configure Live Data Streams

1. **EEG Monitoring**:
   - **Device Selection**: Choose EEG device
   - **Channel Configuration**: 8-channel setup
   - **Filter Settings**: 1-40 Hz bandpass
   - **Artifact Detection**: Automatic rejection

2. **Behavioral Tracking**:
   - **Response Collection**: Real-time logging
   - **Performance Metrics**: Online calculation
   - **Adaptive Parameters**: Dynamic adjustment

3. **System Monitoring**:
   - **CPU Usage**: Resource tracking
   - **Memory Usage**: RAM monitoring
   - **Disk Space**: Storage availability
   - **Network Status**: Connection health

### Step 3: Run Live Experiment

1. **Start Monitoring**:
   - **Begin Recording**: All data streams
   - **Check Signals**: Verify data quality
   - **Test Alerts**: Confirm notification system

2. **Launch Experiment**:
   - **File → New Experiment**
   - **Enable Live Mode**: Real-time analysis
   - **Start Task**: Begin data collection

3. **Monitor Progress**:
   - **Signal Quality**: EEG amplitude and noise
   - **Performance**: Online accuracy and RT
   - **System Health**: Resource utilization
   - **Alerts**: Automatic notifications

### Step 4: Real-time Analysis

1. **Online Processing**:
   - **Feature Extraction**: Real-time EEG features
   - **Classification**: Online pattern detection
   - **Adaptive Staircase**: Dynamic parameter adjustment

2. **Quality Control**:
   - **Artifact Detection**: Automatic bad trial detection
   - **Signal Quality**: Online quality metrics
   - **Data Integrity**: Continuous validation

3. **Intervention Rules**:
   - **Threshold Alerts**: Performance degradation
   - **System Alerts**: Resource exhaustion
   - **Data Alerts**: Quality issues

### Step 5: Export and Analysis

1. **Live Data Export**:
   - **Continuous Export**: Real-time data saving
   - **Backup System**: Automatic redundancy
   - **Compression**: Efficient storage

2. **Post-Experiment Analysis**:
   - **Quality Metrics**: Data quality assessment
   - **Performance Summary**: Live vs. offline analysis
   - **System Optimization**: Resource usage analysis

### What You Learned
- How to set up real-time monitoring
- How to configure live data streams
- How to run experiments with live feedback
- How to implement quality control systems

---

## Tutorial 6: Batch Processing and Automation

### Objective
Learn to automate experiment processing for large datasets.

### Prerequisites
- Completed previous tutorials
- Multiple experiment files
- 25 minutes of time

### Step 1: Set Up Batch Processing

1. **Tools → Batch Processing**
2. **Select Files**:
   - **Directory**: Choose experiment folder
   - **File Pattern**: *.json (experiment files)
   - **Recursive**: Include subdirectories

3. **Configure Pipeline**:
   - **Step 1**: Data validation
   - **Step 2**: Preprocessing
   - **Step 3**: Analysis
   - **Step 4**: Visualization
   - **Step 5**: Export

### Step 2: Define Processing Rules

1. **Data Validation**:
   - **Required Fields**: Participant ID, session, responses
   - **Data Types**: Numeric, categorical, temporal
   - **Quality Checks**: Missing values, outliers

2. **Preprocessing Rules**:
   - **Response Time Filtering**: 200-3000ms
   - **Accuracy Thresholds**: Minimum performance
   - **Artifact Rejection**: EEG quality criteria

3. **Analysis Parameters**:
   - **Statistical Tests**: Pre-specified analyses
   - **Model Selection**: Automatic model comparison
   - **Correction Methods**: Multiple comparison correction

### Step 3: Execute Batch Processing

1. **Start Processing**:
   - **Parallel Processing**: Use multiple cores
   - **Progress Tracking**: Real-time updates
   - **Error Handling**: Continue on errors

2. **Monitor Progress**:
   - **Current File**: Processing status
   - **Completion Rate**: Percentage done
   - **Time Estimate**: Remaining time
   - **Error Log**: Processing issues

### Step 4: Review Batch Results

1. **Summary Report**:
   - **Files Processed**: Total and successful
   - **Error Summary**: Types and frequencies
   - **Quality Metrics**: Data quality assessment

2. **Aggregate Analysis**:
   - **Group Statistics**: Across all participants
   - **Individual Results**: Participant-level summaries
   - **Comparative Analysis**: Between-group comparisons

3. **Export Options**:
   - **CSV Files**: Spreadsheet format
   - **JSON Data**: Structured format
   - **PDF Reports**: Summary documents
   - **Database**: Direct database import

### Step 5: Automation Scripting

1. **Create Script**:
   ```python
   # Example batch processing script
   from apgi_framework import BatchProcessor
   
   processor = BatchProcessor()
   processor.add_directory('experiments/')
   processor.set_analysis_pipeline(['validation', 'analysis', 'export'])
   processor.run_parallel(cores=4)
   ```

2. **Schedule Automation**:
   - **Daily Processing**: Automatic data processing
   - **Weekly Reports**: Summary generation
   - **Monthly Backup**: Data archiving

### What You Learned
- How to set up batch processing pipelines
- How to define processing rules and validation
- How to monitor and manage large-scale processing
- How to automate repetitive analysis tasks

---

## Quick Reference Cheat Sheet

### Keyboard Shortcuts
- **Ctrl+N**: New experiment
- **Ctrl+O**: Open file
- **Ctrl+S**: Save
- **Ctrl+Shift+S**: Save As
- **Ctrl+Z**: Undo
- **Ctrl+Y**: Redo
- **Ctrl+F**: Find
- **Ctrl+H**: Replace
- **F5**: Run experiment
- **F1**: Help
- **Esc**: Stop current operation

### Common Workflows

#### Quick Experiment Setup
1. File → New → Detection Task
2. Enter Participant ID
3. Set Trials = 50
4. Click Start

#### Data Analysis
1. File → Open → Select data
2. Analysis Tab → Descriptive Statistics
3. Visualization → Psychometric Curve
4. File → Export Results

#### Batch Processing
1. Tools → Batch Processing
2. Select directory
3. Configure pipeline
4. Click Run

### Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| GUI not responding | Check memory usage, close other apps |
| Can't import data | Verify file format and permissions |
| Experiment crashes | Reduce trial count, check sensors |
| Slow analysis | Enable parallel processing |

### Default Settings

| Parameter | Default | Recommended Range |
|-----------|---------|------------------|
| Trials | 100 | 50-200 |
| Response Window | 2000ms | 1000-3000ms |
| Stimulus Duration | 500ms | 100-1000ms |
| Inter-trial Interval | 1000ms | 500-2000ms |

---

**Congratulations!** You've completed the APGI Framework tutorial series. You now have the skills to:

- Design and run sophisticated experiments
- Analyze data using advanced statistical methods
- Create professional visualizations
- Automate large-scale data processing
- Monitor experiments in real-time

For additional help and resources:
- **Documentation**: `docs/` directory
- **Community Forum**: https://forum.apgi-framework.org
- **Video Tutorials**: https://youtube.com/apgi-framework
- **Support**: support@apgi-framework.org
