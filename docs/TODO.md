# APGI Framework - TODO List

## Current Status Overview (Updated December 31, 2024)

### ✅ Recently Completed
- **Workspace Cleanup**: Removed all Python cache files, temporary logs, and empty directories
- **Test Coverage Improvement**: Achieved 23% overall test coverage (up from near-zero)
- **Fixed 204 Tests**: CLI and clinical modules now have passing tests
- **Reduced Failing Tests**: Only 16 failing tests remain (excluding problematic files)

### 🔄 Current State
- **GUI System**: Modern customtkinter interface implemented but monolithic (1,394 lines in single file)
- **Adaptive Testing**: Framework exists, 16 failing tests need fixes (significant improvement from 93)
- **Falsification Testing**: Core logic implemented, integration issues remain
- **Pharmacological Simulators**: Implementation exists, signature mismatches need fixing
- **Neural Simulators**: Multiple simulators implemented, some integration issues

- **Real-time Monitoring Dashboard**: Basic structure only
- **Advanced Visualization**: Limited plotting capabilities
- **Deployment Automation**: No automation system
- **Performance Optimization**: No optimization implemented

MISSING-001: Advanced Experimental Paradigms
Status: Partially implemented or missing

❌ Phase Transitions in Consciousness: NOT IMPLEMENTED
❌ Cross-Species Validation: NOT IMPLEMENTED
⚠️ Clinical Biomarkers: STUB ONLY (25% complete)
⚠️ Threshold Detection Paradigm: Directory exists, no code
MISSING-002: Real-time Monitoring Dashboard
Location: apgi_framework/gui/monitoring_dashboard.py
Status: Basic structure only, not functional
Impact: Cannot monitor experiments in real-time
Priority: Medium - nice-to-have feature

MISSING-003: Advanced Visualization
Status: Limited plotting capabilities

❌ No interactive dashboards
⚠️ Basic matplotlib plots only
❌ No real-time visualization updates
Impact: Limited data exploration capabilities
MISSING-004: Database Integration
Status: No large dataset database system
Impact: Cannot handle large-scale multi-participant studies efficiently
Priority: Medium - needed for scaling

MISSING-005: Machine Learning Classification Tools
Status: Not implemented
Impact: Cannot use ML for disorder classification
Priority: Low - research feature

MISSING-006: Deployment Automation
Status: No automation system
Impact: Manual deployment process, error-prone
Priority: Medium - DevOps improvement

Inconsistent Logging
Impact: Some modules use different logging formats
Priority: Low - cosmetic issue

ISSUE-002: Hard-coded Parameters
Impact: Some thresholds hard-coded instead of configurable
Priority: Low - technical debt

ISSUE-003: Mixed Example/Production Code
Location: apgi_framework/neural/
Files: example_signal_processing.py, example_usage.py
Impact: Confusion about production vs. example code
Priority: Low - organizational issue


#### Critical Issues
1. **Insufficient Test Coverage** 
   - Overall coverage: 23% (improved from near-zero)
   - No integration tests for GUI workflows
   - No UI automation testing
   - 16 failing tests remain (mostly in adaptive, falsification, storage modules)

2. **Monolithic Architecture**
   - `apgi_falsification_gui.py` contains 1,394 lines in a single file
   - Multiple responsibilities mixed: UI, validation, test execution, results visualization
   - Tight coupling between components

3. **Complex State Management**
   - Global state scattered across classes
   - No clear separation of concerns
   - Difficult to test individual components

#### Performance Issues
1. **UI Thread Blocking**
   - Long-running operations on main thread
   - No proper async handling for computationally intensive tasks
   - Potential UI freezing during test execution

2. **Memory Management**
   - Large objects held in memory without cleanup
   - No resource management for matplotlib figures
   - Potential memory leaks in long-running sessions

### Recommendations

#### Immediate Actions (High Priority)
1. **Extract Components**
   ```python
   # Split monolithic GUI into focused components:
   - ParameterConfigPanel (already exists)
   - TestExecutionPanel  
   - ResultsVisualizationPanel
   - LoggingPanel
   ```

2. **Add Basic Test Coverage**
   ```python
   # Create test files:
   - tests/test_gui_components.py
   - tests/test_parameter_validation.py
   - tests/test_test_execution.py
   ```

3. **Implement MVC Pattern**
   ```python
   # Separate concerns:
   - Models: TestConfiguration, TestResults
   - Views: GUI components
   - Controllers: TestRunnerController, ValidationController
   ```

#### Medium-term Improvements
1. **Async Operations**
   - Move test execution to background threads
   - Implement progress callbacks
   - Add cancellation support

2. **Configuration Management**
   - External GUI state management
   - Session persistence
   - Settings management

---

## 2. Falsification Tests Analysis

### Current State
- **Files**: `primary_falsification_test.py` (508 lines), `threshold_insensitivity_test.py` (619 lines)
- **Test Coverage**: 23% overall (improved from 16-28% baseline)
- **Complexity**: High - multiple nested validation layers
- **Status**: Core logic implemented, integration issues remain

### Issues Identified

#### Critical Issues
1. **Complex Logic Chains**
   - Deep nesting of validation steps
   - Multiple decision points with insufficient testing
   - Hard to trace execution paths

2. **Insufficient Test Coverage**
   - Edge cases not covered
   - Error handling paths untested
   - Statistical analysis methods unvalidated

3. **Simulation vs Real Data**
   - Heavy reliance on simulated data
   - No validation with real experimental data
   - Potential bias in simulation parameters

#### Performance Issues
1. **Computational Complexity**
   - O(n²) operations in statistical analysis
   - Inefficient array operations
   - No caching of expensive computations

2. **Memory Usage**
   - Large result objects held in memory
   - No streaming for large datasets
   - Potential memory issues with many trials

### Code Analysis

#### Primary Falsification Test Issues
```python
# Lines 368-385: Complex falsification determination
def _determine_falsification(self, signature_validation, consciousness_assessment, 
                           ai_acc_validation, controls_valid):
    return (signature_validation['all_present'] and
            consciousness_assessment['consciousness_absent'] and
            ai_acc_validation['activation_absent'] and
            ai_acc_validation['coherence_low'] and
            controls_valid)
```
- **Issue**: Multiple boolean conditions without individual testing
- **Impact**: Difficult to debug falsification logic failures

#### Threshold Insensitivity Test Issues
```python
# Lines 441-464: Complex drug effect validation
def _determine_falsification(self, drug_type, threshold_change, 
                           physiological_controls_valid, drug_effect_confirmed):
    # Complex logic with multiple conditions
    threshold_insensitive = abs(threshold_change) < self.sensitivity_threshold
    return (threshold_insensitive and 
            physiological_controls_valid and 
            drug_effect_confirmed and
            abs(expected_change) > self.sensitivity_threshold)
```
- **Issue**: Drug-specific logic mixed with general validation
- **Impact**: Hard to extend to new drug types

### Recommendations

#### Immediate Actions (High Priority)
1. **Extract Validation Logic**
   ```python
   # Create focused validators:
   - SignatureValidator
   - ConsciousnessAssessor  
   - DrugEffectValidator
   - ExperimentalControlValidator
   ```

2. **Add Comprehensive Tests**
   ```python
   # Test coverage targets:
   - Edge cases: 90%
   - Error paths: 85%
   - Statistical methods: 95%
   ```

3. **Implement Strategy Pattern**
   ```python
   # Replace conditional logic with strategies:
   class FalsificationStrategy:
       def is_falsifying(self, trial_data) -> bool
   
   class PrimaryFalsificationStrategy(FalsificationStrategy):
       # Primary test logic
   
   class ThresholdInsensitivityStrategy(FalsificationStrategy):
       # Threshold test logic
   ```

#### Medium-term Improvements
1. **Performance Optimization**
   - Vectorize operations where possible
   - Implement result streaming
   - Add computation caching

2. **Data Validation Framework**
   - Real data integration
   - Simulation parameter validation
   - Statistical method verification

---

## 3. Neural Processing Analysis

### Current State
- **Files**: `cardiac_processor.py` (720 lines), `disorder_classification.py` (445 lines)
- **Test Coverage**: Insufficient (estimated <20%, part of overall 23%)
- **Performance**: Critical for real-time processing
- **Status**: Algorithms implemented, performance optimization needed

### Issues Identified

#### Critical Issues
1. **Performance Bottlenecks**
   - R-peak detection algorithms not optimized
   - HRV analysis uses inefficient computations
   - No parallel processing for multi-channel data

2. **Algorithm Selection**
   - Multiple R-peak detection algorithms without performance comparison
   - No adaptive algorithm selection based on signal quality
   - Fixed parameters regardless of signal characteristics

3. **Insufficient Testing**
   - No performance benchmarks
   - Limited edge case testing
   - No real data validation

#### Code Analysis

#### Cardiac Processor Issues
```python
# Lines 100-156: Pan-Tompkins implementation
def detect_r_peaks_pan_tompkins(self, ecg_signal, timestamps):
    # Inefficient derivative computation
    derivative = np.diff(ecg_signal)
    derivative = np.pad(derivative, (0, 1), mode='edge')
    
    # Squaring operation creates large arrays
    squared = derivative ** 2
    
    # Moving average without optimization
    integrated = np.convolve(squared, np.ones(window_size) / window_size, mode='same')
```
- **Issue**: Inefficient array operations
- **Impact**: Poor performance with long recordings

#### Disorder Classification Issues
```python
# Lines 176-217: Feature extraction without validation
def extract_neural_signature(self, p3b_data, gamma_data, microstate_data, 
                           pupil_data, apgi_params, behavioral_data):
    # No input validation
    # No error handling for missing data
    # Assumes all data is present and valid
```
- **Issue**: No input validation or error handling
- **Impact**: Runtime errors with incomplete data

### Recommendations

#### Immediate Actions (High Priority)
1. **Performance Optimization**
   ```python
   # Optimize critical paths:
   - Use numba for R-peak detection
   - Implement vectorized HRV calculations
   - Add parallel processing for multi-channel EEG
   ```

2. **Add Input Validation**
   ```python
   # Validate all inputs:
   def extract_neural_signature(self, **kwargs):
       # Validate required fields
       # Handle missing data gracefully
       # Provide meaningful error messages
   ```

3. **Benchmark Suite**
   ```python
   # Performance benchmarks:
   - R-peak detection speed/accuracy
   - HRV computation time
   - Memory usage profiling
   ```

#### Medium-term Improvements
1. **Adaptive Algorithms**
   - Signal quality assessment
   - Algorithm selection based on signal characteristics
   - Dynamic parameter tuning

2. **Real-time Processing**
   - Streaming data support
   - Low-latency processing
   - Buffer management

---

## 4. Cross-Cutting Concerns

### Logging and Monitoring
- **Issue**: Inconsistent logging across components
- **Impact**: Difficult to debug production issues
- **Solution**: Implement structured logging with correlation IDs

### Error Handling
- **Issue**: Inconsistent error handling patterns
- **Impact**: Poor user experience and debugging
- **Solution**: Standardize exception hierarchy and handling

### Configuration Management
- **Issue**: Hard-coded parameters scattered throughout code
- **Impact**: Difficult to tune and maintain
- **Solution**: Centralized configuration with validation

### Experimental Paradigms

- **Somatic Marker Priming and Decision Ignition**: Status: Partial implementation (basic structure exists)
- **Metabolic Cost of Ignition**: Status: Partial implementation (basic structure exists)
- **Clinical Biomarkers for Disorders of Consciousness**: Status: Stub implementation only
- **Phase Transitions in Consciousness**: Status: Not implemented
- **Cross-Species Validation**: Status: Not implemented
- **Threshold Detection Paradigm**: Status: Directory exists but no implementation
- **Advanced Computational Models**: Status: Partial implementation

### Better Neural Simulation

- Realistic neural dynamics
- Noise models for different brain regions
- Neuromodulatory effects

### Advanced Analysis Tools

- EEG/MEG analysis pipelines
- Connectivity analysis methods
- Statistical testing frameworks
- Machine learning classification tools

### Data Management

- Database integration for large datasets

### Priority Tasks (Updated)

1. ✅ **Workspace Cleanup**: Completed - removed all temporary files and cache
2. ✅ **Test Coverage Improvement**: Achieved 23% coverage, fixed 204 tests
3. **Fix Remaining 16 Failing Tests**: Focus on adaptive, falsification, and storage modules
4. **GUI Refactoring**: Split monolithic 1,394-line file into components
5. **Performance Optimization**: Neural processing and falsification test algorithms
6. **Add Missing Experimental Paradigm Logic**: Complete implementation stubs

### Implementation Status

- **Somatic Marker Priming**: Basic structure exists, needs experimental logic
- **Metabolic Cost of Ignition**: Basic structure exists, needs fMRI/fNIRS integration
- **AI Benchmarking**: Agent and environment systems implemented, needs validation
- **Interoceptive Gating**: Basic framework exists, needs detailed implementation

- **Clinical Biomarkers for Disorders of Consciousness**: Directory exists, minimal implementation
- **Phase Transitions in Consciousness**: Not implemented
- **Cross-Species Validation**: Not implemented
- **Threshold Detection Paradigm**: Directory exists but no implementation

### Technical Components (Updated Status)

- **Neural Simulation**: Multiple simulators (P3b, Gamma, BOLD) implemented, integration issues remain
- **Analysis Tools**: Bayesian models, effect size calculators, statistical tools exist with 23% test coverage
- **Hardware Integration**: Basic structure, needs EEG/MEG acquisition system integration
- **Real-time Capabilities**: Framework exists, needs psychophysics toolbox integration
- **Stimulus Generation**: Basic generators, needs advanced visual/auditory synthesis
- **Test Infrastructure**: 23% coverage achieved, 204 tests fixed, 16 failing tests remain

### Data Infrastructure

- **Database Integration**: No large dataset database system
- **Version Control for Protocols**: No experimental protocol versioning
- **Machine Learning Classification**: No ML tools implemented
- **Connectivity Analysis**: Limited connectivity analysis methods
- **EEG/MEG Analysis Pipelines**: No complete analysis pipelines

### Stimulus Generation

- **Advanced visual stimulus generation**
- **Auditory stimulus synthesis**
- **Haptic/tactile stimulus control**
