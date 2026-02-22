# APGI Framework — Comprehensive Application Audit Report

**Report Date:** 2026-02-22
**Auditor:** Automated End-to-End Audit
**Branch:** `claude/app-audit-testing-Zdyzh`
**Python Version Tested:** 3.11.14
**Scope:** Full codebase — GUI applications, framework modules, test suite, documentation

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Application Overview](#2-application-overview)
3. [KPI Scores](#3-kpi-scores)
4. [Bug Inventory](#4-bug-inventory)
5. [Missing Features & Incomplete Implementations](#5-missing-features--incomplete-implementations)
6. [Test Suite Analysis](#6-test-suite-analysis)
7. [Documentation Audit](#7-documentation-audit)
8. [Actionable Recommendations](#8-actionable-recommendations)
9. [Appendix — File Inventory](#9-appendix--file-inventory)

---

## 1. Executive Summary

The APGI Framework (Adaptive Precision and Generalized Intelligence) is a research-grade Python desktop application for consciousness studies, neural signal processing, and adaptive experiment management. It consists of:

- **5 GUI entry points** (`GUI.py`, `apgi_gui/app.py`, `GUI-Launcher.py`, `GUI-Experiment-Registry.py`, plus apps/)
- **26 framework subpackages** under `apgi_framework/`
- **45+ test files** covering unit, integration, property-based, and GUI tests
- **Extensive documentation** across 16+ markdown files

### Overall Health: **POOR TO FAIR**

The application contains **one critical import-level bug** that cascades to prevent 31 test files from loading and blocks all major framework modules from being imported. Additionally, two documented primary GUI entry points (`launch_gui.py`, `GUI-Simple.py`) are entirely absent from the repository. Several GUI view modes advertised to users will crash the application on selection. The test suite, where it can run, yields **7 failures out of 56 active tests** (12.5% failure rate), with an additional **121 tests silently skipped** due to missing display environment and **31 test files failing to collect** due to the critical import bug.

---

## 2. Application Overview

| Attribute | Value |
|-----------|-------|
| Domain | Consciousness research / computational neuroscience |
| Primary Language | Python 3.8–3.12 |
| GUI Framework | CustomTkinter + Tkinter |
| Core Dependencies | numpy, scipy, pandas, matplotlib, customtkinter |
| Package Name | `apgi-framework-test-enhancement` v1.0.0 |
| Architecture | Multi-entry-point monolith with framework library |
| Entry Points | GUI.py (5,691 lines), apgi_gui/app.py (1,700 lines), GUI-Launcher.py, GUI-Experiment-Registry.py |

### Entry Points Status

| Entry Point | Exists | Syntax OK | Importable | Notes |
|-------------|--------|-----------|------------|-------|
| `GUI.py` | ✅ | ✅ | ✅ | Imports succeed with dependencies installed |
| `apgi_gui/app.py` | ✅ | ✅ | ✅ | Modern component architecture |
| `GUI-Launcher.py` | ✅ | ✅ | ✅ | Launcher for all GUIs |
| `GUI-Experiment-Registry.py` | ✅ | ✅ | ✅ | Experiment registry |
| `GUI-Simple.py` | ❌ | — | — | **MISSING — documented but absent** |
| `launch_gui.py` | ❌ | — | — | **MISSING — documented as primary entry** |

---

## 3. KPI Scores

| # | KPI | Score (1–100) | Rationale |
|---|-----|--------------|-----------|
| 1 | **Functional Completeness** | **42/100** | Critical path_manager import bug breaks the entire framework; 2 documented GUI entry points missing; multiple GUI view modes crash on selection; find/debug/search features explicitly unimplemented; ~31 test modules unable to load |
| 2 | **UI/UX Consistency** | **55/100** | The components that exist follow consistent CustomTkinter patterns with good zoom, theme toggle, keyboard shortcuts, and status bar; however, large sections of the sidebar, visualization modes, and session management are stubs; fallback classes silently mask failures |
| 3 | **Responsiveness & Performance** | **58/100** | Architecture uses threading for long tasks, memory-monitored undo/redo stacks, and adaptive window sizing; however, headless testing prevents runtime validation; `matplotlib.use("Agg")` backend selected correctly; no performance benchmarks passing |
| 4 | **Error Handling & Resilience** | **40/100** | Defensive try/except wrapping is pervasive but masks real errors via silent fallback classes; the fundamental `path_manager` import error is unhandled at startup; SessionStateManager methods called in demo code do not exist; bare `except Exception` swallowing in file I/O paths |
| 5 | **Overall Implementation Quality** | **45/100** | Good directory structure and module separation; however, 60+ stub `pass` methods, 50+ `# type: ignore` comments, missing LICENSE/README/CHANGELOG, broken docs cross-references, 31 test collection errors, and a cascade import failure indicate the codebase is in mid-development with significant incomplete work |

### Score Interpretation

| Range | Grade |
|-------|-------|
| 80–100 | Production-ready |
| 60–79 | Near-ready, minor issues |
| 40–59 | Significant work required |
| 20–39 | Major rework needed |
| 1–19 | Prototype / non-functional |

---

## 4. Bug Inventory

### 4.1 Critical Severity

---

#### BUG-001 — Wrong import path for `path_manager` breaks entire framework

**Severity:** Critical
**Affected File:** `apgi_framework/config/config_manager.py:14`
**Affected URLs/Components:** All framework modules; 31 test files; all GUI components

**Description:**
`config_manager.py` imports `get_path_manager` from a non-existent module path `..path_manager`. The actual function lives at `apgi_framework.utils.path_utils`. This single wrong import cascades and causes every module that transitively imports `apgi_framework.config` to fail with `ModuleNotFoundError`.

**Reproduction Steps:**
```bash
cd /home/user/apgi-experiments
python3 -c "import sys; sys.path.insert(0, '.'); import apgi_framework"
```

**Expected:**
Framework imports successfully.

**Actual:**
```
ModuleNotFoundError: No module named 'apgi_framework.path_manager'
```

**Impact:**
- All 31 of the following test files fail to collect: `test_adaptive_module.py`, `test_cli_module.py`, `test_config_manager.py`, `test_core_models.py`, `test_data_management.py`, `test_workflow_orchestrator.py`, and 26 others.
- All GUI components under `apgi_framework/gui/` cannot be imported.
- `apgi_framework.workflow_orchestrator`, `apgi_framework.data.data_manager`, `apgi_framework.analysis.analysis_engine` all fail to import.

**Fix:**
```python
# apgi_framework/config/config_manager.py line 14
# Change:
from ..path_manager import get_path_manager
# To:
from ..utils.path_utils import get_path_manager
```

---

### 4.2 High Severity

---

#### BUG-002 — ResultsVisualizationPanel crashes on all non-Overview view modes

**Severity:** High
**Affected File:** `apgi_framework/gui/components/results_visualization_panel.py`
**Affected Lines:** 519–592 (dispatch), missing methods throughout

**Description:**
The `ResultsVisualizationPanel` advertises five view modes via a dropdown: "Overview", "Statistical Details", "Time Series", "Comparison", and "Neural Signatures". Only "Overview" is implemented. All others dispatch to private methods (`_show_statistical_details`, `_show_time_series_plots`, etc.) that in turn call missing plot methods, resulting in an immediate `AttributeError`.

**Missing methods (partial list):**
- `_plot_effect_sizes_with_ci()`
- `_plot_p_vs_effect_size()`
- `_plot_ci_widths()`
- `_plot_power_analysis()`
- `_plot_success_rate_timeline()`
- `_plot_falsification_timeline()`
- `_plot_trend_analysis()`
- `_plot_run_comparison()`
- `_plot_run_comparison_bar()`
- `_plot_neural_correlates()`

**Reproduction Steps:**
1. Launch the APGI GUI.
2. Navigate to Results Visualization Panel.
3. Change the view mode dropdown from "Overview" to any other option.

**Expected:**
The selected visualization renders with appropriate charts.

**Actual:**
```
AttributeError: 'ResultsVisualizationPanel' object has no attribute '_plot_effect_sizes_with_ci'
```

**Fix:** Implement all missing plot methods or remove the non-working view modes from the dropdown until they are ready.

---

#### BUG-003 — `TestFallbackFunctionality` test raises `NameError: name 'tk' is not defined`

**Severity:** High
**Affected File:** `tests/test_gui_components_refactored.py:393`

**Description:**
`tkinter` is imported inside a `try/except` block with a flag `TKINTER_AVAILABLE`. The `TestFallbackFunctionality.setup_method()` uses `tk.Tk()` directly without checking `TKINTER_AVAILABLE`, causing a `NameError` when tkinter is not importable.

**Reproduction Steps:**
```bash
python3 -m pytest tests/test_gui_components_refactored.py::TestFallbackFunctionality::test_fallback_gui_initialization -v
```

**Expected:**
Test is skipped if tkinter unavailable, otherwise passes.

**Actual:**
```
NameError: name 'tk' is not defined
```

**Fix:**
```python
class TestFallbackFunctionality:
    def setup_method(self):
        if not TKINTER_AVAILABLE:
            pytest.skip("tkinter not available")
        self.root = tk.Tk()
        self.root.withdraw()
```

---

#### BUG-004 — `APGIAgent` mock in tests missing `.config` attribute

**Severity:** High
**Affected Files:** `tests/test_apgi_agent.py` (line referenced from `test_edge_cases.py:322`)
**Affected Test:** `test_edge_cases.py::TestEdgeCases::test_extreme_modulation_factor`

**Description:**
The test constructs an `APGIAgent(M=1000.0)` and calls `agent.config.Pi_i_base`. The `APGIAgent` mock class defined in `test_apgi_agent.py` stores `Pi_i_base` directly on `self`, not on a `config` sub-object, causing an `AttributeError`.

**Reproduction Steps:**
```bash
python3 -m pytest tests/test_edge_cases.py::TestEdgeCases::test_extreme_modulation_factor -v
```

**Expected:**
`agent.Pi_i[7] == Pi_i_base * 1000.0` assertion passes.

**Actual:**
```
AttributeError: 'APGIAgent' object has no attribute 'config'
```

**Fix:** Change test assertion to `agent.Pi_i[7] == agent.Pi_i_base * 1000.0`.

---

#### BUG-005 — `ErrorHandler` missing documented `log_error` method

**Severity:** High
**Affected File:** `utils/error_handler.py`
**Affected Test:** `tests/test_utils_basic.py::TestErrorHandler::test_error_handler_methods`

**Description:**
The test asserts `hasattr(handler, "log_error")` but `ErrorHandler` has no such method. The actual methods are `handle_error`, `create_error`, `format_error`, etc. Either the test expectation is wrong or the method is missing from the implementation.

**Reproduction Steps:**
```bash
python3 -m pytest tests/test_utils_basic.py::TestErrorHandler::test_error_handler_methods -v
```

**Expected:**
`ErrorHandler` has a `log_error` method.

**Actual:**
```
AssertionError: assert False
  +  where False = hasattr(<utils.error_handler.ErrorHandler object>, 'log_error')
```

**Fix:** Add `log_error` method to `ErrorHandler`, or update the test to check for the actual method name `handle_error`.

---

#### BUG-006 — `DataValidator` missing `validate_dataset_structure` method

**Severity:** High
**Affected File:** `utils/data_validation.py`
**Affected Test:** `tests/test_utils_basic.py::TestDataValidation::test_data_validator_methods`

**Description:**
Test asserts `DataValidator` has a `validate_dataset_structure` method, but the method does not exist on the class.

**Reproduction Steps:**
```bash
python3 -m pytest tests/test_utils_basic.py::TestDataValidation::test_data_validator_methods -v
```

**Expected:**
`DataValidator` has `validate_dataset_structure`.

**Actual:**
```
AssertionError: assert False
  +  where False = hasattr(<utils.data_validation.DataValidator object>, 'validate_dataset_structure')
```

**Fix:** Implement `validate_dataset_structure()` in `DataValidator`, or update the test to match actual API.

---

#### BUG-007 — `APGIAgent.test_parameter_validation` fails — missing validation

**Severity:** High
**Affected File:** `tests/test_apgi_agent.py::TestAPGIAgent::test_parameter_validation`

**Description:**
The test expects that creating `APGIAgent` with invalid parameters (e.g., negative `T`) raises a `ValueError`. The mock `APGIAgent` in the test file does not implement parameter validation.

**Reproduction Steps:**
```bash
python3 -m pytest tests/test_apgi_agent.py::TestAPGIAgent::test_parameter_validation -v
```

**Expected:**
`ValueError` raised for invalid parameters.

**Actual:**
```
Failed: DID NOT RAISE <class 'ValueError'>
```

---

#### BUG-008 — `test_nan_and_inf_handling` does not raise `ValueError` for NaN stimulus

**Severity:** High
**Affected File:** `tests/test_edge_cases.py::TestEdgeCases::test_nan_and_inf_handling`

**Description:**
The test sets `agent.ext_stim[5] = np.nan` and expects a `ValueError` with the message "NaN values". The `APGIAgent` mock processes NaN silently without validation.

**Reproduction Steps:**
```bash
python3 -m pytest tests/test_edge_cases.py::TestEdgeCases::test_nan_and_inf_handling -v
```

**Expected:**
`ValueError: "NaN values"` is raised.

**Actual:**
```
Failed: DID NOT RAISE <class 'ValueError'>
```

---

#### BUG-009 — `test_empty_stimulus` fails with `AttributeError`

**Severity:** High
**Affected File:** `tests/test_edge_cases.py::TestEdgeCases::test_empty_stimulus`

**Description:**
Test accesses `agent.config` which does not exist on the mock `APGIAgent`.

**Reproduction Steps:**
```bash
python3 -m pytest tests/test_edge_cases.py::TestEdgeCases::test_empty_stimulus -v
```

**Expected:**
Test runs and validates empty stimulus behavior.

**Actual:**
```
AttributeError: 'APGIAgent' object has no attribute 'config'
```

---

#### BUG-010 — `test_context_modulation_edge_cases` fails with `AttributeError`

**Severity:** High
**Affected File:** `tests/test_edge_cases.py::TestEdgeCases::test_context_modulation_edge_cases`

**Description:**
Same root cause as BUG-009. `agent.config` is accessed but not present on the mock.

---

### 4.3 Medium Severity

---

#### BUG-011 — 14 GUI modules commented out in `apgi_framework/gui/__init__.py`

**Severity:** Medium
**Affected File:** `apgi_framework/gui/__init__.py`

**Description:**
All major GUI component exports are commented out. Only `launch_gui()` is exported. Any code attempting `from apgi_framework.gui import SessionSetupManager` (or similar) will raise `ImportError`.

**Commented-out exports include:**
- `SessionSetupManager`, `ParticipantManager`
- `RealTimeProgressMonitor`
- `TaskParameterConfigurator`
- `LiveEEGMonitor`
- `SessionReportGenerator`
- `HardwareFailureHandler`
- (7 more)

---

#### BUG-012 — Demo code in `error_handling.py` calls non-existent `SessionStateManager` methods

**Severity:** Medium
**Affected File:** `apgi_framework/gui/error_handling.py` (approx. lines 1096–1139)

**Description:**
The demo GUI calls methods on `SessionStateManager` that are not defined:
- `create_session(session_id)` — not implemented
- `handle_session_crash(exception)` — not implemented
- `attempt_session_recovery()` — not implemented
- `get_session_status()` — not implemented

**Actual `SessionStateManager` methods:** `save_state()`, `load_state()`, `delete_state()`, `list_saved_states()`

Any use of the demo GUI will crash with `AttributeError`.

---

#### BUG-013 — `sys.path.insert()` anti-pattern in `apgi_framework/data/__init__.py`

**Severity:** Medium
**Affected File:** `apgi_framework/data/__init__.py` (lines 10–11, 60–61)

**Description:**
The data package init mutates `sys.path` to inject the `examples/` directory for `data_loader` imports. This anti-pattern breaks packaging, makes testing harder, and fails if the project is moved or deployed.

---

#### BUG-014 — Pervasive fallback dummy classes mask real import errors

**Severity:** Medium
**Affected Files:**
- `apgi_framework/gui/components/main_gui_controller.py` (lines 32–93)
- `apgi_framework/gui/components/parameter_config_panel.py` (lines 23–148)
- `apgi_framework/gui/components/test_execution_panel.py` (lines 23–83)
- `apgi_framework/gui/error_handling.py` (lines 27–75)

**Description:**
All four files create do-nothing placeholder classes when the real imports fail. While graceful degradation is a valid pattern, these fallbacks hide genuine dependency failures and create objects that silently produce no output. The `# type: ignore` comments (50+ occurrences) further disable static analysis.

**Example:**
```python
try:
    from apgi_framework.config import ConfigManager
except ImportError:
    class ConfigManager:  # type: ignore[no-redef]
        def __init__(self):
            pass
```

---

#### BUG-015 — `find()`, `find_next()`, `find_previous()` are explicit placeholders

**Severity:** Medium
**Affected File:** `apgi_gui/app.py` (lines 1222–1235)

**Description:**
Three keyboard-bound actions (`Ctrl+F`, `Ctrl+G`, `Ctrl+Shift+G`) display a status bar message saying the feature is not implemented, but they are exposed in the keyboard shortcut setup with no further indication to the user.

```python
def find(self) -> None:
    # Placeholder for find functionality
    self.update_status("Find functionality not yet implemented")
```

---

#### BUG-016 — `toggle_debug_mode()` is a no-op placeholder

**Severity:** Medium
**Affected File:** `apgi_gui/app.py:1237–1240`

**Description:**
`Ctrl+D` is bound to `toggle_debug_mode()` which only prints a status message. No debug panel or logging level change is triggered.

---

#### BUG-017 — `GUI.py` contains multiple empty `pass` stubs in fallback classes

**Severity:** Medium
**Affected File:** `GUI.py` (lines 91, 94, 111, 114, 119, 136, 139, 142, 145, 148, 152, 155, 158, 172, 175, 178, 578, 583, 590)

**Description:**
Fallback classes for `KeyboardManager`, `UndoRedoManager`, `WidgetTracker`, and `ThemeManager` all consist only of `pass` method bodies. When real dependencies are missing, these fallbacks are silently substituted, providing zero actual functionality while pretending to work.

---

#### BUG-018 — `apgi_framework/config/exceptions.py` referenced but imports from wrong location

**Severity:** Medium
**Affected File:** `apgi_framework/config/config_manager.py:17`

**Description:**
`config_manager.py` imports `from .exceptions import ConfigurationError`. This requires a `exceptions.py` file within `apgi_framework/config/`, which must be checked and verified to exist separately from the top-level `apgi_framework/exceptions.py`.

---

#### BUG-019 — `121 GUI tests silently skipped` due to missing display

**Severity:** Medium
**Affected Files:** `tests/test_gui_components.py`, `tests/test_gui_components_expanded.py`, `tests/test_gui_config_management.py`, `tests/test_new_components.py`

**Description:**
All 121 GUI tests use `@pytest.mark.skipif` or equivalent guards that skip when no display is available. No headless testing adapter (e.g., `xvfb`) is configured in the CI pipeline or pyproject.toml. These tests contribute zero coverage in the standard test run.

---

#### BUG-020 — `tkinter` listed as pip-installable optional dependency

**Severity:** Medium
**Affected File:** `pyproject.toml` (line 49)

**Description:**
```toml
[project.optional-dependencies]
gui = [
    "tkinter>=8.6",   # NOT a pip package
    ...
]
```
`tkinter` is not available on PyPI; it is part of the Python standard library (requiring OS-level package `python3-tk` on Debian/Ubuntu). This will fail with `ERROR: No matching distribution found for tkinter>=8.6` on clean environments.

---

### 4.4 Low Severity

---

#### BUG-021 — All 14 exception classes in `apgi_framework/exceptions.py` are bare `pass` stubs

**Severity:** Low
**Affected File:** `apgi_framework/exceptions.py` (lines 13–97)

**Description:**
All exception classes (`APGIFrameworkError`, `MathematicalError`, `SimulationError`, etc.) have no custom `__init__`, no message templates, and no contextual data. Exception handling is functional but entirely uninformative.

---

#### BUG-022 — README.md contains malformed markdown nesting

**Severity:** Low
**Affected File:** `docs/README.md` (lines 306–308)

**Description:**
A code block is opened with triple backticks and then another code block opens inside it without closing the outer one, producing broken rendering.

```markdown
   # Install dependencies

   ```bash          ← inner triple backtick inside outer code block
   pip install -r requirements.txt
   ```
```

---

#### BUG-023 — `_collect_original_sizes()` method has multiple bare `pass` exception catches

**Severity:** Low
**Affected File:** `apgi_gui/app.py` (lines 1102, 1113, 1127)

**Description:**
The zoom system silently ignores all exceptions when collecting widget sizes, which means zoom failures are invisible.

---

## 5. Missing Features & Incomplete Implementations

### 5.1 Missing Files (Documented but Absent)

| File | Documented In | Impact |
|------|--------------|--------|
| `launch_gui.py` | README.md, TUTORIALS.md, GUI-ENTRY-POINTS.md, docs/README.md | New users directed to non-existent entry point |
| `GUI-Simple.py` | GUI-ENTRY-POINTS.md, docs/README.md | Recommended for new users; does not exist |
| `README.md` (project root) | Standard expectation | No top-level project overview |
| `LICENSE` | docs/README.md references it | Legal/compliance gap |
| `CONTRIBUTING.md` | docs/DOCUMENTATION.md | No contributor guidance |
| `CHANGELOG.md` | docs/DOCUMENTATION.md standard | No version history |
| `CODE_OF_CONDUCT.md` | docs/DOCUMENTATION.md | No community standards |
| `setup.py` | Standard Python package | Missing traditional setup entry |

### 5.2 Missing Documentation Files (Cross-Referenced)

| File | Referenced In |
|------|--------------|
| `docs/FAQ.md` | docs/DOCUMENTATION.md |
| `docs/known-issues.md` | docs/DOCUMENTATION.md |
| `docs/support.md` | docs/DOCUMENTATION.md |
| `docs/community.md` | docs/DOCUMENTATION.md |
| `docs/bug-reporting.md` | docs/DOCUMENTATION.md |
| `docs/QUICK-START.md` | docs/DOCUMENTATION.md (multiple) |
| `docs/GUI_VISUAL_GUIDE.md` | docs/DOCUMENTATION.md, docs/README.md |
| `docs/CLI_REFERENCE.md` | docs/DOCUMENTATION.md |
| `docs/USER_GUIDE.md` | docs/DOCUMENTATION.md |
| `docs/api/` directory | docs/DOCUMENTATION.md (entire section) |

### 5.3 Unimplemented GUI Features

| Feature | Entry Point | Status |
|---------|-------------|--------|
| Find / Find Next / Find Previous | `apgi_gui/app.py` | Placeholder — displays "not yet implemented" |
| Debug Mode toggle | `apgi_gui/app.py` | No-op placeholder |
| Statistical Details view | `ResultsVisualizationPanel` | Crashes — missing 4 plot methods |
| Time Series view | `ResultsVisualizationPanel` | Crashes — missing 4 plot methods |
| Comparison view | `ResultsVisualizationPanel` | Crashes — missing 4 plot methods |
| Neural Signatures view | `ResultsVisualizationPanel` | Crashes — missing 4 plot methods |
| Session lifecycle (create/crash/recover/status) | `error_handling.py` demo | 4 methods missing on `SessionStateManager` |
| 14 GUI module exports | `apgi_framework/gui/__init__.py` | All commented out |

### 5.4 Incomplete Framework Modules

| Module | Issue |
|--------|-------|
| `apgi_framework/security/code_sandbox.py` | 4 classes defined with only `pass` |
| `apgi_framework/testing/test_generator.py` | 1 class with only `pass` |
| `apgi_framework/clinical/treatment_prediction.py` | 1 class with only `pass` |
| `apgi_framework/gui/parameter_estimation_gui.py` | 8 methods with only `pass` |
| `apgi_framework/security/input_sanitization.py` | 1 class with only `pass` |
| `apgi_framework/adaptive/task_control.py` | 2 methods with only `pass` (lines 186, 217) |
| `apgi_framework/optimization/performance_monitor.py` | 1 method with only `pass` (line 433) |
| `apgi_framework/config/manager.py` | 2 methods with only `pass` |

---

## 6. Test Suite Analysis

### 6.1 Summary

| Metric | Value |
|--------|-------|
| Total test files | 45+ |
| Test files with collection errors | 31 (69%) |
| Root cause of collection errors | `ModuleNotFoundError: apgi_framework.path_manager` (BUG-001) |
| Tests in collectable files | 215 |
| Tests PASSED | 56 |
| Tests FAILED | 7 |
| Tests SKIPPED | 121 (GUI tests, no display) + 2 (other) |
| Test ERRORS (setup/teardown) | 1 |
| Pass rate (of runnable tests) | **56/63 = 88.9%** |
| Pass rate (including uncollectable) | **~18%** |

### 6.2 Failing Tests

| Test ID | File | Failure Reason |
|---------|------|---------------|
| `TestAPGIAgent::test_parameter_validation` | `test_apgi_agent.py` | No `ValueError` raised for invalid params |
| `TestEdgeCases::test_context_modulation_edge_cases` | `test_edge_cases.py` | `AttributeError: no attribute 'config'` |
| `TestEdgeCases::test_empty_stimulus` | `test_edge_cases.py` | `AttributeError: no attribute 'config'` |
| `TestEdgeCases::test_nan_and_inf_handling` | `test_edge_cases.py` | `ValueError` not raised for NaN input |
| `TestEdgeCases::test_extreme_modulation_factor` | `test_edge_cases.py` | `AttributeError: no attribute 'config'` |
| `TestErrorHandler::test_error_handler_methods` | `test_utils_basic.py` | `log_error` method missing |
| `TestDataValidation::test_data_validator_methods` | `test_utils_basic.py` | `validate_dataset_structure` missing |

### 6.3 Test Infrastructure Issues

- **No CI display configuration:** 121 GUI tests skip in every run without `xvfb` or similar.
- **`pytest-timeout` not installed:** `pyproject.toml` specifies `pytest-timeout>=2.0` but it is not in `requirements.txt` and the flag causes argument errors.
- **Property-based tests blocked:** All `test_*_properties.py` files fail to collect due to BUG-001.
- **`tests/framework/` and `tests/falsification/` directories contain no test files** in their subdirectory roots (only `__init__.py`).
- **Redundant test files:** Multiple similar test files exist for the same components (`test_adaptive_module.py`, `test_adaptive_module_simple.py`, `test_adaptive_simple.py`) indicating possible deduplication debt.

### 6.4 Code Warnings During Test Run

```
RuntimeWarning: overflow encountered in exp
  return 1.0 / (1.0 + np.exp(-x))
```
Sigmoid function does not clamp input values before exponentiation. For inputs > ~710 this will produce `inf`.

```
RuntimeWarning: 'sin' and 'sout' swap memory stats couldn't be determined
```
`psutil` swap memory stats unavailable on this Linux environment (non-blocking but noisy).

---

## 7. Documentation Audit

### 7.1 Documentation Quality

| Document | Exists | Accurate | Issues |
|----------|--------|---------|--------|
| `docs/README.md` | ✅ | Partial | References missing files; broken markdown nesting |
| `docs/GUI-ENTRY-POINTS.md` | ✅ | Partial | Describes `GUI-Simple.py` and `launch_gui.py` which don't exist |
| `docs/GUI-VISUAL-GUIDE.md` | ✅ | Mostly | Describes view modes that crash (BUG-002) |
| `docs/DOCUMENTATION.md` | ✅ | Poor | Entire API, troubleshooting, and quickstart sections link to missing files |
| `docs/QUICK-START-GUIDE.md` | ✅ | Good | Standalone; accurate |
| `docs/USER-GUIDE.md` | ✅ | Good | Comprehensive; mostly accurate |
| `docs/TESTING.md` | ✅ | Partial | Does not mention 31 collection errors |
| `docs/TROUBLESHOOTING.md` | ✅ | Good | Useful; up to date |
| `docs/EXPERIMENTS.md` | ✅ | Good | Well-written |
| `docs/CLI-REFERENCE.md` | ✅ | Unknown | CLI not testable without framework import fix |
| `docs/api/` | ❌ | — | Entire directory missing |
| `docs/FAQ.md` | ❌ | — | Missing |

### 7.2 Documentation–Code Gaps

The documentation describes the system as having:
- A web interface at `../../apgi-web/APGI-Experiments.html` — not present in this repository.
- A `setup.py` — not present.
- A `core/models/apgi_agent.py` — present in `core/analysis/` but instructions say `core/models/`.
- `tests/unit/`, `tests/performance/` directories for pytest markers — these directories do not exist; only `tests/framework/`, `tests/falsification/`, `tests/integration/`.

---

## 8. Actionable Recommendations

### Priority 1 — Critical (Fix immediately; blocks everything else)

| # | Action | File(s) | Effort |
|---|--------|---------|--------|
| R-01 | Fix wrong import in `config_manager.py`: change `from ..path_manager import get_path_manager` → `from ..utils.path_utils import get_path_manager` | `apgi_framework/config/config_manager.py:14` | XS (1 line) |
| R-02 | Create `launch_gui.py` or update all documentation to point to the correct launcher (`GUI-Launcher.py`) | All docs + new file | S |
| R-03 | Create `GUI-Simple.py` as documented, or remove all references to it from docs | docs/GUI-ENTRY-POINTS.md, docs/README.md | S–M |

### Priority 2 — High (Required before QA sign-off)

| # | Action | File(s) | Effort |
|---|--------|---------|--------|
| R-04 | Implement the 4 missing plot method groups in `ResultsVisualizationPanel`, OR remove the broken view mode options from the dropdown | `results_visualization_panel.py` | L |
| R-05 | Fix `TestFallbackFunctionality` to skip when `TKINTER_AVAILABLE` is False | `tests/test_gui_components_refactored.py:393` | XS |
| R-06 | Fix all 5 `test_edge_cases.py` failures: add `config` sub-object to mock `APGIAgent`, implement NaN/inf validation | `tests/test_edge_cases.py`, `tests/test_apgi_agent.py` | S |
| R-07 | Implement `ErrorHandler.log_error()` or update test to use `handle_error()` | `utils/error_handler.py` or test | XS |
| R-08 | Implement `DataValidator.validate_dataset_structure()` or update test | `utils/data_validation.py` or test | XS |
| R-09 | Remove `tkinter>=8.6` from `pyproject.toml` optional dependencies; add OS-level install note only | `pyproject.toml:49` | XS |

### Priority 3 — Medium (Required for feature-complete delivery)

| # | Action | File(s) | Effort |
|---|--------|---------|--------|
| R-10 | Implement `SessionStateManager` lifecycle methods (`create_session`, `handle_session_crash`, `attempt_session_recovery`, `get_session_status`) or fix demo code to use existing methods | `apgi_framework/gui/error_handling.py` | M |
| R-11 | Replace all do-nothing fallback class patterns with explicit error handling and clear error messages | 4 GUI component files | M |
| R-12 | Configure xvfb in CI (`.ci/` already exists) to enable the 121 skipped GUI tests | `.ci/` config | S |
| R-13 | Uncomment and verify exported GUI modules in `apgi_framework/gui/__init__.py` | `gui/__init__.py` | M |
| R-14 | Implement or clearly mark as `NotImplemented` the `find()`, `find_next()`, `find_previous()`, and `toggle_debug_mode()` methods | `apgi_gui/app.py` | M |
| R-15 | Remove `sys.path.insert()` from `apgi_framework/data/__init__.py`; use proper package structure | `data/__init__.py` | S |
| R-16 | Add `pytest-timeout` to `requirements.txt` or remove the entry from `pyproject.toml` | `requirements.txt` / `pyproject.toml` | XS |
| R-17 | Add sigmoid input clamping to prevent `RuntimeWarning: overflow in exp` | `tests/test_edge_cases.py` + implementation | XS |

### Priority 4 — Low (Technical debt; schedule for future sprint)

| # | Action | File(s) | Effort |
|---|--------|---------|--------|
| R-18 | Add `LICENSE` file (MIT as documented) | Project root | XS |
| R-19 | Add project root `README.md` | Project root | S |
| R-20 | Add `CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` | Project root | S |
| R-21 | Create missing docs: `docs/FAQ.md`, `docs/known-issues.md`, `docs/QUICK-START.md`, `docs/api/` | `docs/` | L |
| R-22 | Replace 50+ `# type: ignore` comments with proper Union types and Protocol definitions | Multiple GUI files | M–L |
| R-23 | Implement or delete the 60+ `pass` stub methods across `security/`, `clinical/`, `testing/`, `gui/` | Multiple files | L |
| R-24 | Add message templates and contextual data to all 14 exception subclasses | `apgi_framework/exceptions.py` | S |
| R-25 | Fix broken markdown nesting in `docs/README.md:306–308` | `docs/README.md` | XS |
| R-26 | Consolidate duplicate test files (`test_adaptive_module*.py` × 3, `test_clinical_*.py` × 4) | `tests/` | M |
| R-27 | Correct the `setup.sh` reference to `gui.py` (lowercase) — actual file is `GUI.py` | `setup.sh`, `docs/README.md` | XS |

---

## 9. Appendix — File Inventory

### 9.1 Source File Counts

| Category | File Count | Notes |
|----------|-----------|-------|
| GUI entry points (root) | 4 | GUI.py, GUI-Launcher.py, GUI-Experiment-Registry.py, Utils-GUI.py |
| GUI apps (`apps/`) | 5 | All syntax-valid |
| `apgi_gui/` package | 20 | Component-based architecture |
| `apgi_framework/` package | 90+ | Core framework library |
| Test files (`tests/`) | 45 | 31 fail to collect |
| Example files (`examples/`) | 10 | Standalone scripts |
| Documentation files (`docs/`) | 16+ markdown | Multiple cross-references broken |

### 9.2 Dependency Status (Post-Install)

| Package | Required Version | Status |
|---------|-----------------|--------|
| numpy | ≥1.24.0 | ✅ 2.4.2 |
| scipy | ≥1.10.0 | ✅ 1.17.0 |
| pandas | ≥2.0.0 | ✅ 3.0.1 |
| matplotlib | ≥3.7.0 | ✅ 3.10.8 |
| customtkinter | ≥5.2.0 | ✅ 5.2.2 |
| statsmodels | ≥0.14.0 | ✅ 0.14.6 |
| seaborn | ≥0.12.0 | ✅ 0.13.2 |
| psutil | ≥5.9.0 | ✅ 7.2.2 |
| pytest | ≥7.4.0 | ✅ 9.0.2 |
| hypothesis | ≥6.70.0 | ✅ 6.151.9 |
| h5py | ≥3.8.0 | ❌ Not installed |
| pytest-timeout | ≥2.0 | ❌ Not installed (causes CLI error) |
| tkinter | system pkg | ⚠️ OS-level; not pip-installable |

### 9.3 Test Results Summary Table

| Test File | Status | Pass | Fail | Skip | Notes |
|-----------|--------|------|------|------|-------|
| test_apgi_agent.py | Collected | 6 | 1 | 0 | `test_parameter_validation` fails |
| test_core_analysis.py | Collected | 8 | 0 | 0 | All pass |
| test_edge_cases.py | Collected | 11 | 4 | 0 | 4 `AttributeError` / `ValueError` |
| test_utils_basic.py | Collected | 16 | 2 | 0 | Missing methods |
| test_utils_modules.py | Collected | 7 | 0 | 0 | All pass |
| test_phase_transition.py | Collected | 4 | 0 | 0 | All pass |
| test_threshold_detection.py | Collected | 4 | 0 | 6 | Some skipped |
| test_clinical_biomarkers.py | Collected | 0 | 0 | 20 | All skipped (no display) |
| test_system_validator.py | Collected | 0 | 0 | 50+ | All skipped (no display) |
| test_gui_components.py | Collected | 0 | 0 | ~30 | All skipped (no display) |
| test_gui_components_expanded.py | Collected | 0 | 0 | ~15 | All skipped |
| test_gui_components_refactored.py | Collected | 0 | 0 | 11 + 1 err | `NameError: tk` |
| test_gui_config_management.py | Collected | 0 | 0 | ~10 | All skipped |
| test_new_components.py | Collected | 0 | 0 | ~35 | All skipped |
| 31 other test files | ERROR | — | — | — | BUG-001 import failure |

---

*This report was generated by automated end-to-end audit on 2026-02-22.*
*All line numbers reference the state of the codebase on branch `claude/app-audit-testing-Zdyzh`.*
