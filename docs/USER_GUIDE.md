# APGI Framework User Guide

Welcome to the APGI (Active Passive Inference) Framework User Guide. This comprehensive guide will help you get started with the framework and make the most of its features.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [GUI Overview](#gui-overview)
5. [Analysis Workflow](#analysis-workflow)
6. [Data Management](#data-management)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

## Getting Started

### What is APGI Framework?

The APGI Framework is a comprehensive scientific computing platform designed for:

- **Active Inference Modeling**: Implement and test active inference theories
- **Multimodal Data Analysis**: Process EEG, pupillometry, cardiac, and behavioral data
- **Parameter Estimation**: Estimate model parameters using Bayesian methods
- **Falsification Testing**: Test scientific hypotheses through model comparison
- **Visualization**: Create publication-quality plots and figures

### System Requirements

- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: Version 3.8 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 2GB free disk space
- **Graphics**: OpenGL support for visualization

## Installation

### Automated Installation (Recommended)

1. **Download the Framework**

   ```bash
   git clone https://github.com/your-org/apgi-experiments.git
   cd apgi-experiments
   ```

2. **Run the Setup Script**

   ```bash
   bash setup.sh
   ```

   The setup script will:
   - Check Python installation
   - Create virtual environment
   - Install dependencies
   - Verify installation
   - Create desktop shortcuts

### Manual Installation

1. **Create Virtual Environment**

   ```bash
   python -m venv apgi_venv
   source apgi_venv/bin/activate  # On Windows: apgi_venv\Scripts\activate
   ```

2. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

3. **Verify Installation**

   ```bash
   python -c "import apgi_framework; print('Installation successful!')"
   ```

### Docker Installation

1. **Pull the Docker Image**

   ```bash
   docker pull apgi-framework/apgi:latest
   ```

2. **Run with Docker Compose**

   ```bash
   docker-compose up
   ```

## Quick Start

### Launching the Application

**Method 1: Desktop Shortcut**

- Double-click the APGI Framework shortcut on your desktop

**Method 2: Command Line**

   ```bash
   # Activate virtual environment
   source apgi_venv/bin/activate

   # Launch GUI
   python -m apgi_gui
   ```

**Method 3: Development Mode**

   ```bash
   python launch_gui.py
   ```

### First Steps

1. **Explore the Interface**: The main window consists of:

   - **Sidebar**: Navigation and project management
   - **Main Area**: Tabbed workspace for analysis
   - **Status Bar**: System status and zoom controls

2. **Load Example Data**:

   - Go to `File > Load Example Data`
   - Select a modality (EEG, Pupillometry, Cardiac, or Behavioral)
   - Choose a subject from the dropdown

3. **Run Your First Analysis**:

   - Navigate to the **Analysis** tab
   - Select analysis type (Descriptive, Comparative, etc.)
   - Configure parameters
   - Click **Run Analysis**

## GUI Overview

### Main Window Layout

```
┌─────────────────────────────────────────────────────────┐
│ Menu Bar: File | Edit | View | Analysis | Tools | Help │
├─────────────┬───────────────────────────────────────────┤
│             │                                           │
│   Sidebar   │            Main Area                      │
│             │                                           │
│ - Projects  │  ┌─────────────────────────────────────┐  │
│ - Data      │  │ Analysis | Visualization | Results │  │
│ - Models    │  └─────────────────────────────────────┘  │
│ - Tools     │                                           │
│             │                                           │
├─────────────┴───────────────────────────────────────────┤
│ Status Bar: Ready | 100% | 12:34:56 | No file loaded    │
└─────────────────────────────────────────────────────────┘
```

### Sidebar Components

#### Projects Panel

- **New Project**: Create a new analysis project
- **Open Project**: Load existing projects
- **Recent Projects**: Quick access to recent work
- **Project Settings**: Configure project parameters

#### Data Panel

- **Import Data**: Load CSV, JSON, or pickle files
- **Example Data**: Access built-in datasets
- **Data Preview**: Quick preview of loaded data
- **Data Info**: View metadata and statistics

#### Models Panel

- **Detection Tasks**: Access behavioral task models
- **Analysis Models**: Configure analysis parameters
- **Bayesian Models**: Set up hierarchical models
- **Custom Models**: Add your own models

#### Tools Panel

- **Log Viewer**: View application logs
- **Preferences**: Configure settings
- **Zoom Controls**: Adjust UI scale
- **Export Tools**: Save results and figures

### Main Area Tabs

#### Analysis Tab

The Analysis tab is where you'll spend most of your time conducting data analysis.

#### Features

- Data import and preprocessing
- Multiple analysis types (Descriptive, Comparative, Correlation, etc.)
- Parameter configuration
- Real-time analysis progress
- Results preview

#### Workflow

1. **Data Import**: Select data source and configure import settings
2. **Analysis Selection**: Choose analysis type from dropdown menu
3. **Parameter Setup**: Configure analysis-specific parameters
4. **Run Analysis**: Execute analysis with progress tracking
5. **Review Results**: View statistical outputs and visualizations

#### Visualization Tab

Create and customize plots for your data.

#### Plot Types

- **Time Series**: Line plots for temporal data
- **Spectral Analysis**: Frequency domain plots
- **Topographic Maps**: Spatial visualizations
- **Statistical Plots**: Box plots, histograms, scatter plots

#### Customization Options

- Color schemes and themes
- Axis labels and titles
- Legend positioning
- Export formats (PNG, PDF, SVG)

#### Results Tab

Manage and compare analysis results.

#### Results Tab Features

- Results browser with filtering and sorting
- Detailed result viewer
- Comparison tools for multiple analyses
- Export functionality for reports

#### Actions

- **View Details**: Examine full analysis results
- **Compare**: Side-by-side comparison of analyses
- **Export**: Save results in various formats
- **Delete**: Remove unwanted results

## Analysis Workflow

### Step 1: Data Preparation

#### Loading Data
```python
# Using the GUI
1. Go to Data Panel > Import Data
2. Select file type (CSV, JSON, pickle)
3. Choose file and configure import options
4. Click "Load Data"

# Using Python API

```python
from apgi_framework.data import load_data
data = load_data("path/to/your/data.csv")
```

#### Data Validation
The framework automatically validates loaded data:
- Checks for missing values
- Verifies data types
- Validates time series consistency
- Checks for required columns

### Step 2: Analysis Configuration

#### Choosing Analysis Type

**Descriptive Analysis**
- Basic statistics (mean, std, min, max)
- Data distribution analysis
- Missing value analysis

**Comparative Analysis**
- Group comparisons
- Statistical tests (t-test, ANOVA)
- Effect size calculations

**Correlation Analysis**
- Correlation matrices
- Partial correlations
- Network analysis

**Time Series Analysis**
- Trend analysis
- Seasonality detection
- Spectral analysis

**Bayesian Analysis**
- Parameter estimation
- Model comparison
- Posterior analysis

#### Parameter Configuration

Each analysis type has specific parameters:

```python
# Example: Comparative Analysis Parameters
params = {
    "group_column": "condition",
    "dependent_variables": ["reaction_time", "accuracy"],
    "test_type": "anova",
    "correction_method": "bonferroni",
    "effect_size": "cohen_d"
}
```

### Step 3: Running Analysis

#### GUI Execution
1. Configure analysis parameters
2. Click "Run Analysis" button
3. Monitor progress in status bar
4. Review results when complete

#### Programmatic Execution

```python
from apgi_framework.analysis import AnalysisEngine

# Initialize analysis engine
engine = AnalysisEngine()

# Run analysis
result = engine.analyze(
    data=data,
    analysis_type="comparative",
    parameters=params
)

# Access results
print(result.statistics)
print(result.p_values)
print(result.effect_sizes)
```

### Step 4: Results Interpretation

#### Statistical Output
- **Descriptive Statistics**: Central tendency and variability
- **Inferential Statistics**: Test statistics and p-values
- **Effect Sizes**: Practical significance measures
- **Confidence Intervals**: Uncertainty quantification

#### Visualizations
- **Automated Plots**: Generated based on analysis type
- **Interactive Features**: Zoom, pan, and explore
- **Export Options**: Save in multiple formats

## Data Management

### Supported Data Formats

#### CSV Files
- Standard comma-separated values
- Automatic type detection
- Missing value handling

#### JSON Files
- Structured data format
- Metadata preservation
- Nested data support

#### Pickle Files
- Python object serialization
- Fast loading for large datasets
- Preserves data types

### Data Organization

#### Project Structure

```
your_project/
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
├── results/
│   ├── analysis/
│   ├── figures/
│   └── reports/
├── models/
└── config/
```

#### Best Practices
1. **Keep Raw Data Intact**: Never modify original data files
2. **Use Consistent Naming**: Follow a clear naming convention
3. **Document Everything**: Include metadata and README files
4. **Version Control**: Track changes with Git
5. **Regular Backups**: Protect your work

### Data Preprocessing

#### Cleaning Operations
- **Missing Value Handling**: Imputation or removal
- **Outlier Detection**: Statistical identification
- **Data Normalization**: Standardization and scaling
- **Time Series Alignment**: Synchronization across modalities

#### Quality Checks
- **Data Integrity**: Consistency validation
- **Range Checking**: Physiological plausibility
- **Temporal Consistency**: Time series validation
- **Cross-modality Alignment**: Synchronization verification

## Advanced Features

### Custom Analysis Models

#### Creating Custom Models
```python
from apgi_framework.analysis import BaseModel

    def analyze(self, data, parameters):
        # Implement your analysis logic
        results = {
            "custom_metric": self.calculate_metric(data),
            "p_value": self.calculate_p_value(data)
        }
        return results
    
    def calculate_metric(self, data):
        # Your custom calculation
        pass
```

#### Registering Custom Models
```python
from apgi_framework.analysis import register_model

register_model("custom_analysis", CustomAnalysis)
```

### Batch Processing

#### Processing Multiple Files
```python
from apgi_framework.batch import BatchProcessor

processor = BatchProcessor()

# Configure batch processing
processor.add_files("data/*.csv")
processor.set_analysis_type("comparative")
processor.set_parameters(params)

# Run batch analysis
results = processor.run()
```

#### Parallel Processing
- Multi-threading support
- Automatic resource management
- Progress tracking
- Error handling

### Integration with External Tools

#### MATLAB Integration
```python
from apgi_framework.integrations import MATLABBridge

bridge = MATLABBridge()
result = bridge.run_analysis("matlab_script.m", data)
```

#### R Integration
```python
from apgi_framework.integrations import RBridge

r_bridge = RBridge()
r_result = r_bridge.run_analysis("r_script.R", data)
```

## Troubleshooting

### Common Issues

#### Installation Problems
**Problem**: "Python not found" error
**Solution**: 
1. Verify Python installation: `python --version`
2. Add Python to system PATH
3. Use full path to Python executable

**Problem**: "Module not found" error
**Solution**:
1. Activate virtual environment
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python path: `import sys; print(sys.path)`

#### Data Loading Issues
**Problem**: "File not found" error
**Solution**:
1. Verify file path and permissions
2. Check file format compatibility
3. Ensure file is not corrupted

**Problem**: "Data format error"
**Solution**:
1. Check CSV delimiter and encoding
2. Verify column names and data types
3. Remove special characters from headers

#### Analysis Errors
**Problem**: "Insufficient data" error
**Solution**:
1. Check data size requirements
2. Verify data completeness
3. Review parameter settings

**Problem**: "Memory error"
**Solution**:
1. Reduce data size or use sampling
2. Close other applications
3. Increase system RAM or use cloud processing

### Performance Optimization

#### Memory Management
- Use data chunking for large datasets
- Clear unused variables
- Optimize data types
- Use memory-efficient algorithms

#### Processing Speed
- Enable parallel processing
- Use optimized libraries
- Cache intermediate results
- Profile and optimize bottlenecks

## FAQ

### General Questions

**Q: Is APGI Framework free?**
A: Yes, it's open-source under the MIT license.

**Q: What programming languages are supported?**
A: The framework is primarily Python-based but supports integration with MATLAB and R.

**Q: Can I use APGI Framework for commercial research?**
A: Yes, the MIT license allows commercial use.

### Technical Questions

**Q: How do I update the framework?**
A: Run `git pull` and `pip install -e .` in your project directory.

**Q: Can I contribute to the framework?**
A: Yes! Contributions are welcome. See the developer documentation for guidelines.

**Q: How do I report bugs?**
A: Use the GitHub Issues page with detailed error information and reproduction steps.

### Data Questions

**Q: What data formats are supported?**
A: CSV, JSON, pickle, HDF5, and common neurophysiology formats (EEG, EDF, etc.).

**Q: Can I process real-time data?**
A: Yes, the framework supports streaming data processing with appropriate configuration.

**Q: How do I handle missing data?**
A: The framework provides multiple imputation methods. Configure in the data preprocessing settings.

### Analysis Questions

**Q: What statistical tests are available?**
A: t-tests, ANOVA, non-parametric tests, Bayesian tests, and custom implementations.

**Q: Can I add custom analysis methods?**
A: Yes, see the "Custom Analysis Models" section for implementation details.

**Q: How do I export results?**
A: Use the export functionality in the Results tab or programmatically with the export API.

## Getting Help

### Documentation Resources
- **API Reference**: Detailed function and class documentation
- **Developer Guide**: For contributors and advanced users
- **Tutorials**: Step-by-step guides for common tasks
- **Examples**: Code samples and use cases

### Community Support
- **GitHub Discussions**: Ask questions and share knowledge
- **Issue Tracker**: Report bugs and request features
- **Wiki**: Community-maintained documentation
- **Mailing List**: Announcements and discussions

### Professional Support
- **Consulting Services**: Custom implementation and training
- **Workshops**: Hands-on training sessions
- **Technical Support**: Priority assistance for organizations

---

## Next Steps

Now that you've completed this guide, you might want to:

1. **Try the Tutorials**: Work through step-by-step examples
2. **Explore Examples**: See real-world applications
3. **Join the Community**: Connect with other users
4. **Contribute**: Help improve the framework
5. **Advanced Topics**: Dive deeper into specific features

Thank you for using the APGI Framework!
