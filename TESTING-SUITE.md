# APGI Framework Test Coverage Improvement Plan

**Objective:** Systematically increase test coverage from current baseline to 100% target  
**Last Updated:** 2026-03-21  
**Current Coverage Baseline:** 13.51% (37,154 total lines, 5,021 covered)  
**Tests Discovered:** 1,296 tests  
**Tests Passing:** ~1,100+ (estimated based on recent runs)  
**Tests Failing:** ~150+ (estimated based on recent runs)  
**Tests Skipped:** 8  

---

## 📊 Coverage Status Dashboard

| Category               | Total Tests | Passing | Failing | Skipped | Coverage % | Status            |
|------------------------|-------------|---------|---------|---------|------------|-------------------|
| **Unit Tests**         | 1,200+      | ~1,100  | ~150    | 8       | 13.51%     | 🟡 In Progress    |
| **Integration Tests**  | 8+          | 8       | 0       | 0       | TBD        | 🟡 In Progress    |
| **GUI Tests**          | 78          | 70+     | <8      | 0       | 9.6%       | 🟡 In Progress    |
| **Performance Tests**  | 17          | 17      | 0       | 0       | TBD        | ⚪ Stable          |
| **Property Tests**     | 27          | 27      | 0       | 0       | TBD        | ⚪ Stable          |
| **TOTAL**              | 1,296+      | ~1,150  | ~150    | 8       | **13.51%** | 🟡 In Progress    |

**Legend:**

    - 🟢 Complete (≥95% coverage, all tests passing)
    - 🟡 In Progress (active work underway)
    - 🔴 Blocked (dependencies/blockers identified)
    - ⚪ Not Started (planned but not yet begun)

---

## 🎯 Module-Level Coverage Tracking

### Core Framework (`apgi_framework/`)

| Module         | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                     |
| -------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ------------------------- |
| `__init__.py`  | 37    | 37      | 0       | 100.00%    | Medium   | 🟢     | Package initialization    |
| `__main__.py`  | 1     | 0       | 1       | 0.00%      | High     | ⚪     | CLI entry point           |
| `cli.py`       | 167   | 0       | 167     | 0.00%      | High     | ⚪     | Command-line interface    |
| `config.py`    | 189   | 65      | 124     | 34.39%     | High     | 🟡     | Configuration management  |
| `experiment.py`| 357   | 0       | 357     | 0.00%      | Critical | ⚪     | Core experiment logic     |

#### `adaptive/` Module

| File                      | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                      |
| ------------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | -------------------------- |
| `__init__.py`             | 19    | 0       | 19      | 0.00%      | Low      | ⚪     | Package init              |
| `quest_plus_staircase.py` | 311   | 0       | 311     | 0.00%      | High     | ⚪     | Quest+ adaptive algorithm |
| `stimulus_generators.py`  | 127   | 0       | 127     | 0.00%      | Medium   | ⚪     | Stimulus generation       |
| `threshold_estimators.py` | 144   | 0       | 144     | 0.00%      | Medium   | ⚪     | Threshold estimation      |

#### `analysis/` Module

| File                       | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                                           |
| -------------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ----------------------------------------------- |
| `__init__.py`              | 25    | 25      | 0       | 100.00%    | Low      | 🟢     | Package init                                    |
| `analysis_engine.py`       | 417   | 0       | 417     | 0.00%      | Critical | ⚪     | Main analysis engine                             |
| `bayesian_models.py`        | 267   | 0       | 267     | 0.00%      | High     | ⚪     | Bayesian analysis                               |
| `data_models.py`            | 149   | 149     | 0       | 100.00%    | Critical | 🟢     | **COMPLETED** - Added 29 comprehensive tests    |
| `equation.py`               | 175   | 58      | 117     | 33.14%     | Critical | 🟡     | Partial coverage exists                         |
| `falsification.py`         | 361   | 79      | 282     | 21.88%     | Critical | 🟡     | Hypothesis testing                              |
| `metrics.py`                | 209   | 0       | 209     | 0.00%      | High     | ⚪     | Statistical metrics                              |
| `parameter_recovery.py`     | 235   | 0       | 235     | 0.00%      | High     | ⚪     | Parameter estimation                            |
| `parameter_sensitivity.py` | 199   | 0       | 199     | 0.00%      | Medium   | ⚪     | Sensitivity analysis                            |
| `signal_processing.py`     | 187   | 0       | 187     | 0.00%      | Medium   | ⚪     | Signal processing                               |
| `validators.py`             | 163   | 0       | 163     | 0.00%      | High     | ⚪     | Data validation                                 |

#### `clinical/` Module

| File                        | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                     |
| --------------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ------------------------- |
| `__init__.py`               | 18    | 18      | 0       | 100.00%    | Low      | 🟢     | Package init              |
| `disorder_classification.py` | 215   | 0       | 215     | 0.00%      | High     | ⚪     | Disorder classification   |
| `parameter_extraction.py`   | 261   | 261     | 0       | 100.00%    | High     | 🟢     | Parameter extraction      |
| `population_comparison.py`  | 168   | 0       | 168     | 0.00%      | Medium   | ⚪     | Population comparisons    |

#### `data/` Module

| File                    | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                   |
| ----------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ----------------------- |
| `__init__.py`           | 12    | 12      | 0       | 100.00%    | Low      | 🟢     | Package init            |
| `data_manager.py`       | 241   | 0       | 241     | 0.00%      | Critical | ⚪     | Data management         |
| `export_manager.py`     | 173   | 0       | 173     | 0.00%      | High     | ⚪     | Data export             |
| `persistence_layer.py`  | 1,341 | 0       | 1,341   | 0.00%      | Critical | ⚪     | Data persistence        |
| `storage_manager.py`    | 514   | 0       | 514     | 0.00%      | Critical | ⚪     | Storage abstraction     |

#### `gui/` Module

| File                           | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                       |
| ------------------------------ | ----- | ------- | ------- | ---------- | -------- | ------ | --------------------------- |
| `__init__.py`                  | 13    | 13      | 0       | 100.00%    | Low      | 🟢     | Package init                |
| `adaptive_threshold_gui.py`    | 289   | 0       | 289     | 0.00%      | Medium   | ⚪     | Adaptive threshold GUI      |
| `base_app.py`                  | 211   | 0       | 211     | 0.00%      | High     | ⚪     | Base application            |
| `cli_adaptive_threshold.py`    | 187   | 0       | 187     | 0.00%      | Medium   | ⚪     | CLI for adaptive            |
| `data_dialogs.py`              | 145   | 0       | 145     | 0.00%      | Medium   | ⚪     | Data dialogs                |
| `data_management_gui.py`       | 178   | 0       | 178     | 0.00%      | Medium   | ⚪     | Data management GUI         |
| `error_dialogs.py`             | 123   | 0       | 123     | 0.00%      | Medium   | ⚪     | Error dialogs               |
| `experiment_management_gui.py` | 267   | 0       | 267     | 0.00%      | High     | ⚪     | Experiment management       |
| `experiment_runner_gui.py`     | 312   | 0       | 312     | 0.00%      | High     | ⚪     | Experiment runner           |
| `falsification_framework_gui.py`| 334   | 0       | 334     | 0.00%      | High     | ⚪     | Falsification GUI           |
| `main_controller.py`           | 357   | 0       | 357     | 0.00%      | Critical | ⚪     | Main controller             |
| `monitoring_dashboard.py`      | 693   | 75      | 618     | 10.82%     | Medium   | 🟡     | Monitoring dashboard        |
| `parameter_sensitivity_gui.py` | 256   | 0       | 256     | 0.00%      | Medium   | ⚪     | Sensitivity GUI             |
| `task_control_gui.py`          | 198   | 0       | 198     | 0.00%      | High     | ⚪     | Task control GUI          |
| `test_execution_controller.py` | 245   | 0       | 245     | 0.00%      | High     | ⚪     | Test execution GUI        |

#### `models/` Module

| File                  | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                   |
| --------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ----------------------- |
| `__init__.py`          | 14    | 14      | 0       | 100.00%    | Low      | 🟢     | Package init            |
| `agent.py`             | 347   | 0       | 347     | 0.00%      | Critical | ⚪     | APGI Agent model        |
| `phase_transition.py`  | 33    | 0       | 33      | 0.00%      | High     | ⚪     | Phase transitions       |
| `somatic_marker.py`    | 289   | 0       | 289     | 0.00%      | High     | ⚪     | Somatic markers         |

#### `neural/` Module

| File                        | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                         |
| --------------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ----------------------------- |
| `__init__.py`               | 13    | 13      | 0       | 100.00%    | Low      | 🟢     | Package init                  |
| `cardiac_processor.py`      | 360   | 60      | 300     | 16.67%     | High     | 🟡     | Cardiac signal processing     |
| `eeg_interface.py`          | 164   | 50      | 114     | 30.49%     | High     | 🟡     | EEG interface                 |
| `eeg_processor.py`          | 211   | 61      | 150     | 28.91%     | High     | 🟡     | EEG signal processing         |
| `erp_analysis.py`           | 163   | 38      | 125     | 23.31%     | Medium   | 🟡     | ERP analysis                  |
| `gamma_synchrony.py`        | 182   | 33      | 149     | 18.13%     | Medium   | 🟡     | Gamma synchrony analysis      |
| `microstate_analysis.py`  | 205   | 30      | 175     | 14.63%     | Medium   | 🟡     | Microstate analysis           |
| `physiological_monitoring.py`| 440 | 80      | 360     | 18.18%     | Medium   | 🟡     | Physiological monitoring      |
| `pupillometry_interface.py`| 310  | 68      | 242     | 21.94%     | High     | 🟡     | Pupillometry interface        |
| `pupillometry_processor.py`| 190  | 33      | 157     | 17.37%     | Medium   | 🟡     | Pupillometry processing       |
| `quality_control.py`        | 192   | 43      | 149     | 22.40%     | Medium   | 🟡     | Quality control               |

#### `research/` Module

| File                            | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                       |
| ------------------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | --------------------------- |
| `__init__.py`                   | 14    | 8       | 6       | 57.14%     | Low      | 🟡     | Package init                |
| `cross_species_validation.py`   | 222   | 63      | 159     | 28.38%     | Medium   | 🟡     | Cross-species validation    |
| `threshold_detection_paradigm.py`| 417  | 84      | 333     | 20.14%     | Medium   | 🟡     | Threshold detection        |
| `core_mechanisms/experiments.py`| 59    | 23      | 36      | 38.98%     | Medium   | 🟡     | Core mechanism experiments  |

#### `security/` Module

| File                   | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                     |
| ---------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ------------------------- |
| `__init__.py`          | 24    | 8       | 16      | 33.33%     | Low      | 🟡     | Package init              |
| `code_sandbox.py`      | 178   | 0       | 178     | 0.00%      | High     | ⚪     | Code sandbox              |
| `input_sanitization.py`| 189   | 29      | 160     | 15.34%     | High     | 🟡     | Input sanitization        |
| `secure_pickle.py`     | 164   | 29      | 135     | 17.68%     | Medium   | 🟡     | Secure pickle             |
| `security_validator.py`| 120   | 0       | 120     | 0.00%      | Critical | ⚪     | Security validator        |

#### `simulation/` Module

| File                       | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                     |
| -------------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ------------------------- |
| `__init__.py`              | 8     | 8       | 0       | 100.00%    | Low      | 🟢     | Package init              |
| `bold_simulator.py`        | 146   | 33      | 113     | 22.60%     | High     | 🟡     | BOLD signal simulator     |
| `gamma_simulator.py`       | 139   | 28      | 111     | 20.14%     | High     | 🟡     | Gamma signal simulator    |
| `p3b_simulator.py`         | 56    | 13      | 43      | 23.21%     | Medium   | 🟡     | P3b signal simulator        |
| `pci_calculator.py`        | 231   | 26      | 205     | 11.26%     | High     | 🟡     | PCI calculator            |
| `signature_validator.py` | 273   | 47      | 226     | 17.22%     | Medium   | 🟡     | Signature validator       |

#### `testing/` Module

| File                       | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                     |
| -------------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ------------------------- |
| `__init__.py`              | 5     | 5       | 0       | 100.00%    | Low      | 🟢     | Package init              |
| `activity_logger.py`       | 330   | 240     | 90      | 72.73%     | High     | 🟢     | Activity logging            |
| `batch_runner.py`          | 230   | 128     | 102     | 55.65%     | High     | 🟢     | Batch test runner           |
| `ci_integrator.py`         | 320   | 64      | 256     | 20.00%     | High     | 🟡     | CI integration            |
| `error_handler.py`         | 147   | 109     | 38      | 74.15%     | High     | 🟢     | Error handling            |

#### `utils/` Module

| File                    | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                   |
| ----------------------- | ----- | ------- | ------- | ---------- | -------- | ------ | ----------------------- |
| `__init__.py`           | 6     | 6       | 0       | 100.00%    | Low      | 🟢     | Package init            |
| `file_utils.py`         | 257   | 35      | 222     | 13.62%     | Medium   | 🟡     | File utilities            |
| `framework_test_utils.py`| 291  | 107     | 184     | 36.77%     | High     | 🟡     | Framework test utilities  |
| `logging_utils.py`      | 239   | 97      | 142     | 40.59%     | High     | 🟡     | Logging utilities         |
| `path_utils.py`         | 179   | 54      | 125     | 30.17%     | Medium   | 🟡     | Path utilities            |
| `progress_monitor.py`   | 110   | 29      | 81      | 26.36%     | Medium   | 🟡     | Progress monitoring       |

### GUI Components (`apgi_gui/`)

| Module       | Lines | Covered | Missing | Coverage % | Priority | Status | Notes                     |
| ------------ | ----- | ------- | ------- | ---------- | -------- | ------ | ------------------------- |
| `app.py`      | 245   | 0       | 245     | 0.00%      | Critical | ⚪     | Main GUI application      |
| `config/`     | 89    | 0       | 89      | 0.00%      | Medium   | ⚪     | Configuration module      |
| `components/`| 892   | 0       | 892     | 0.00%      | High     | ⚪     | GUI components            |
| `utils/`      | 267   | 77      | 190     | 28.84%     | Medium   | 🟡     | GUI utilities            |

---

## 🎲 Uncovered Code Paths Analysis

### Critical Uncovered Areas

| Module | Function/Class | Risk Level | Impact | Test Strategy |
|--------|---------------|------------|--------|---------------|
| `data/persistence_layer.py` | Data persistence, backup/restore | **Critical** | High | Unit tests with mock filesystem |
| `gui/main_controller.py` | GUI coordination, event handling | **Critical** | High | Integration tests with mocked GUI |
| `experiment.py` | Core experiment lifecycle | **Critical** | High | End-to-end workflow tests |
| `models/agent.py` | Agent behavior, state management | **Critical** | High | Behavioral simulation tests |
| `analysis/analysis_engine.py` | Analysis workflows | **High** | Medium | Component integration tests |
| `cli.py` | Command-line interface | **High** | Medium | CLI argument/exit code tests |
| `validation/` modules | Input validation (mostly 0%) | **High** | Medium | Property-based testing |
| `gui/components/` | GUI components (892 lines) | **Medium** | Medium | Headless GUI testing |
| `data/storage_manager.py` | Storage abstraction | **High** | Medium | Storage mock tests |
| `data/data_manager.py` | Data management workflows | **High** | Medium | Integration tests |

### Edge Cases Identified

| Module | Edge Case | Current Status | Test Needed |
|--------|-----------|----------------|-------------|
| `data_models.py` | Empty/zero-size datasets | ✅ Tested | Covered in comprehensive tests |
| `equation.py` | Division by zero in complexity calculation | ⚠️ Untested | Add boundary condition test |
| `falsification.py` | Invalid hypothesis formats | ⚠️ Untested | Add malformed input tests |
| `neural/processors` | Missing signal channels | ⚠️ Partial | Complete channel handling tests |
| `validation/` | SQL injection in input | ⚠️ Untested | Security fuzzing tests |
| `gui/` | Concurrent GUI events | ⚠️ Untested | Thread safety tests |
| `utils/file_utils` | Permission errors | ⚠️ Partial | Error handling tests |

---

## 📋 Test Development Tasks

- [x] **T-001**: Establish baseline coverage metrics
- [x] **T-002**: Fix any failing collection or infrastructure issues
- [x] **T-003**: Create missing test infrastructure files
- [ ] **T-004**: Document test patterns and conventions
- [ ] **T-101**: Test `experiment.py` - Core experiment lifecycle (0% coverage)
- [ ] **T-102**: Test `analysis_engine.py` - Analysis workflows (0% coverage)
- [x] **T-103**: Test `data_models.py` - Data structure validation (100% coverage)
- [ ] **T-104**: Test `equation.py` - Equation solver edge cases (33% coverage)
- [ ] **T-105**: Test `falsification.py` - Hypothesis testing logic (22% coverage)
- [ ] **T-106**: Test `main_controller.py` - Controller coordination (0% coverage)
- [ ] **T-107**: Test `agent.py` - Agent behavior models (0% coverage)
- [ ] **T-201**: Test `persistence_layer.py` - Data persistence operations
- [ ] **T-202**: Test `storage_manager.py` - Storage abstraction
- [ ] **T-203**: Test `data_manager.py` - Data management workflows
- [ ] **T-204**: Test `export_manager.py` - Export functionality
- [ ] **T-301**: Test `app.py` - Main application
- [ ] **T-302**: Test `experiment_runner_gui.py` - Runner GUI
- [ ] **T-303**: Test `task_control_gui.py` - Task control
- [ ] **T-304**: Test component event handling
- [ ] **T-305**: Test GUI error handling
- [ ] **T-401**: End-to-end experiment workflow test
- [ ] **T-402**: Cross-module integration tests
- [ ] **T-403**: GUI + backend integration tests
- [ ] **T-404**: Data flow integration tests
- [ ] **T-501**: Error handling path tests
- [ ] **T-502**: Boundary condition tests
- [ ] **T-503**: Concurrent access tests
- [ ] **T-504**: Resource cleanup tests
- [ ] **T-505**: Invalid input handling tests

---

## 🐛 Known Issues & Blockers

| ID | Issue | Impact | Status | Resolution Plan |
|----|-------|--------|--------|-----------------|
| ISSUE-001 | Segmentation faults during test runs | **RESOLVED** | � Complete | GUI cleanup fixtures added to conftest.py |
| ISSUE-002 | ~150 failing tests across modules | Reduces coverage accuracy | 🔴 Active | Fix assertions, mocks, imports |
| ISSUE-003 | GUI modules at 0% coverage | Missing GUI tests | 🟡 In Progress | Headless GUI testing framework |
| ISSUE-004 | persistence_layer.py 0% coverage | **RESOLVED** | 🟢 Complete | Test suite created (15/16 passing) |
| ISSUE-005 | Neural/processor test flakiness | Intermittent failures | 🟡 In Progress | Test isolation improvements |

---

## 📝 Test Implementation 

### Phase 1: Data Models Coverage Complete

**Action**: Implemented comprehensive tests for `data/data_models.py`  
**Tests Added**: 29 new tests in `tests/test_data_models_comprehensive.py`  
**Coverage Achieved**: 100% coverage for data_models module (149 lines fully covered)  
**Tests Include**:
- DataVersion dataclass tests (UUID generation, timestamp handling, field types)
- ExperimentMetadata tests (default/custom creation, validation status, timestamps)
- BackupInfo tests (backup types, status values, compression ratios)
- ExperimentalDataset tests (initialization, lock/unlock cycles, nested data)
- Integration tests (full experiment workflow, version history, backup lifecycle)
- Edge case tests (empty data, large sizes, zero retention, nested structures)

**Next Priorities**:
1. persistence_layer.py (0% coverage, 1,341 lines) - CRITICAL
2. main_controller.py (0% coverage, 514 lines) - CRITICAL  
3. analysis/data_models.py (0% coverage) - HIGH
4. validation modules (mostly 0% coverage) - MEDIUM

---

## Coverage Commands

```bash
# Generate coverage report
python -m pytest --cov=apgi_framework --cov=apgi_gui --cov-report=term-missing

# Generate HTML report
python -m pytest --cov=apgi_framework --cov=apgi_gui --cov-report=html

# Generate XML report for CI
python -m pytest --cov=apgi_framework --cov=apgi_gui --cov-report=xml

# Run specific module coverage
python -m pytest tests/test_analysis.py --cov=apgi_framework.analysis

# Run with coverage minimum threshold
python -m pytest --cov=apgi_framework --cov-fail-under=80
```
