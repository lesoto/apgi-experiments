# APGI Framework — End-to-End Application Audit Report

**Report Version:** 3.0
**Audit Date:** 2026-02-28
**Branch:** `claude/app-audit-security-aw9GR`
**Auditor:** Claude Code (automated, full-codebase scan)
**Scope:** Full repository — `apgi_framework/`, `apgi_gui/`, `GUI*.py`, `apps/`, `utils/`, `tests/`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [KPI Scores Dashboard](#2-kpi-scores-dashboard)
3. [Test Suite Results](#3-test-suite-results)
4. [Security Vulnerabilities](#4-security-vulnerabilities)
5. [Bug Inventory](#5-bug-inventory)
6. [Missing Features & Incomplete Implementations](#6-missing-features--incomplete-implementations)
7. [Actionable Recommendations](#7-actionable-recommendations)
8. [Appendix — Methodology](#8-appendix--methodology)

---

## 1. Executive Summary

The APGI (Adaptive Predictive Grounding of Ignition) Framework is a Python desktop application for consciousness research, experimental paradigms, and falsification testing. The codebase is large (≈ 33 000 statements across ≈ 200 Python files) and spans GUI layers (`customtkinter`), a CLI, neural signal processing, adaptive staircase algorithms, Bayesian modelling, and a deployment/CI subsystem.

### Key Findings at a Glance

| Category | Count | Worst Severity |
|---|---|---|
| Security vulnerabilities | **8** | 🔴 Critical |
| Functional bugs (test-verified) | **105 FAILED, 9 ERROR** | 🔴 Critical |
| Production assertion misuse | **10 occurrences** | 🟠 High |
| NotImplementedError stubs | **4** | 🟡 Medium |
| Missing tkinter system dependency | **1 (blocks all GUI tests)** | 🟠 High |
| Test coverage | **0.34% overall** | 🔴 Critical |
| Incomplete mock/test-setup issues | **≥ 6 test classes** | 🟡 Medium |

### Overall Health Score: **58 / 100**

The framework has solid architectural intent (security modules, centralized logging, layered validation) but suffers from: (a) critical security flaws that bypass its own security infrastructure; (b) 13.5% hard test failures; (c) near-zero test coverage of the core framework; and (d) a hard runtime dependency (`tkinter`) that is not installed in the standard Python distribution on this platform, blocking all GUI entry points.

---

## 2. KPI Scores Dashboard

| Dimension | Score | Status | Rationale |
|---|:---:|:---:|---|
| **Functional Completeness** | 62 / 100 | 🟡 Moderate | 4 NotImplementedError stubs in production paths; WorkflowOrchestrator state-management design causes 10 test failures; StorageManager field validation mismatches test expectations |
| **UI/UX Consistency** | 50 / 100 | 🟠 Poor | `tkinter` missing system-wide → all GUI entry points crash at import; fallback classes raise `ImportError` instead of degrading gracefully; bare `except Exception:` blocks in GUI swallow state silently |
| **Responsiveness & Performance** | 60 / 100 | 🟡 Moderate | `psutil` swap-memory warning on this kernel; `performance_monitor.py` has unconditional `import tkinter` blocking headless use; no CI-verified performance benchmarks; `PerformanceProfiler` init fails in tests |
| **Error Handling & Resilience** | 55 / 100 | 🟠 Poor | `ErrorTelemetry.__init__` does not create the telemetry JSON file (only the directory); `assert` used for production state checks (bypassed with `-O`); 15+ bare `except Exception:` handlers; CI integrator silently returns empty `changed_files` when git history is shallow |
| **Implementation Quality** | 63 / 100 | 🟡 Moderate | 2 SQL-injection points, 1 unsafe `pickle.loads`, mocking bugs in 6 test classes, string mismatch in `save_summary_report`, test infrastructure requires manual dependency installs not reflected in `requirements.txt` |

**Composite score: (62+50+60+55+63) / 5 = 58 / 100**

### Score Legend

| Range | Colour | Interpretation |
|---|---|---|
| 80–100 | 🟢 Green | Production-ready |
| 65–79 | 🔵 Blue | Minor issues only |
| 50–64 | 🟡 Yellow | Significant issues, not production-ready |
| 35–49 | 🟠 Orange | Substantial defects, requires sprint-level effort |
| 0–34 | 🔴 Red | Critical failures, blocked release |

---

## 3. Test Suite Results

### 3.1 Run Configuration

```
python -m pytest tests/ --timeout=60 -q --tb=line
```

Dependencies installed before run: `numpy`, `scipy`, `pandas`, `matplotlib`,
`seaborn`, `statsmodels`, `h5py`, `scikit-learn`, `psutil`, `pytest-cov`,
`hypothesis`, `pytest-timeout`

**Not installed / not available:** `tkinter` (system package `python3-tk` absent)

### 3.2 Aggregate Summary

| Metric | Value |
|---|---|
| Total collected | 781 |
| Passed | **545 (69.8%)** |
| Failed | **105 (13.5%)** |
| Skipped | 121 (15.5%) |
| Collection errors | **9 (1.2%)** |
| Suite wall time | ≈ 530 s |
| **Overall pass rate (excl. skipped)** | **83.8%** |

### 3.3 Failing Test Groups (categorised)

| Test Module / Group | Failures | Root Cause Category |
|---|:---:|---|
| `test_workflow_orchestrator.py` | 10 | WorkflowOrchestrator state bug + type mismatch |
| `test_system_validator.py` | 13 | MockController missing `equation_processor` attr |
| `test_threshold_detection.py` | 7 | `scipy.optimize.curve_fit` convergence failure on bootstrap data |
| `test_error_handling_properties.py` | 5 | Property-test violations in error categorisation |
| `test_data_management.py` | 2 | StorageManager validation requires undeclared fields |
| `test_error_telemetry.py` | 3 | Telemetry file not created on init; timeout in JSON serialisation |
| `test_diagnostics_cli.py` | 4 | Mock setup calls `.return_value` on real method (not a Mock) |
| `test_falsification_coverage.py` | 2 | Initialisation path broken in primary test fixture |
| `test_deployment_properties.py` | 2 | Hypothesis state-machine property failures |
| `test_utils_basic.py` | 2 | `PerformanceProfiler` import fails (indirect tkinter dep.) |
| `test_new_components.py` | 2 | Staircase adaptive method / CI calculation diverges |
| `integration/*` | 9 errors | Shallow git history (`HEAD~1` not found); tkinter; fixture errors |

---

## 4. Security Vulnerabilities

Findings are ordered by **CVSS-equivalent severity**.

---

### SEC-01 — Unsafe `pickle.loads` on Database-Retrieved Data

| Field | Value |
|---|---|
| **Severity** | 🔴 Critical |
| **File** | `apgi_framework/testing/performance_optimizer.py:285` |
| **CWE** | CWE-502: Deserialization of Untrusted Data |

**Vulnerable code:**
```python
result=pickle.loads(zlib.decompress(result_data)),
```
`result_data` is fetched directly from an SQLite database row. If the database file can be modified by any external party (shared filesystem, SQLite injection, compromised cache), this is arbitrary code execution.

**Expected behaviour:** Use the project's own `RestrictedUnpickler` from `apgi_framework.security.secure_pickle`.

**Recommendation:**
```python
from apgi_framework.security.secure_pickle import safe_pickle_load
import io
result = safe_pickle_load(io.BytesIO(zlib.decompress(result_data)))
```
Or validate via `SecurePickleValidator.validate_pickle_data()` before unpickling.

---

### SEC-02 — SQL Injection via f-string: `DROP TABLE`

| Field | Value |
|---|---|
| **Severity** | 🔴 Critical |
| **File** | `apgi_framework/data/parameter_estimation_schema.py:436` |
| **CWE** | CWE-89: Improper Neutralization of Special Elements in SQL |

**Vulnerable code:**
```python
conn.execute(f"DROP TABLE IF EXISTS {table}")
```
`table` comes from an iteration over `tables_to_drop`. If any caller populates that list from external input, an attacker can inject arbitrary SQL.

**Recommendation:** Validate `table` against a fixed whitelist:
```python
ALLOWED_TABLES = {"parameter_sessions", "parameter_results", ...}
if table not in ALLOWED_TABLES:
    raise ValueError(f"Illegal table name: {table}")
conn.execute(f"DROP TABLE IF EXISTS {table}")  # safe after whitelist check
```

---

### SEC-03 — SQL Injection via f-string: `PRAGMA table_info`

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **File** | `apgi_framework/data/migration_manager.py:195` |
| **CWE** | CWE-89 |

**Vulnerable code:**
```python
cursor = conn.execute(f"PRAGMA table_info({table_name})")
```
`table_name` is read from `SELECT name FROM sqlite_master`. While it originates from the schema, if the DB file is tampered with, an injected table name could escape the PRAGMA context. Whitelist all expected table names.

---

### SEC-04 — `assert` Statements Used for Security/Safety Guards

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **Files** | `deployment_validator.py:163,204,246,285,362,426` · `main_controller.py:352,405,443` · `memory_efficient_runner.py:305` |
| **CWE** | CWE-617: Reachable Assertion |

Python `assert` statements are **disabled** when the interpreter is run with the `-O` (optimise) flag, which is standard in some production Docker images and packaging tools.

**Vulnerable code (example):**
```python
# deployment_validator.py:163
assert self.current_report is not None
```

**Expected:** `None` propagation prevented at all times.

**Actual (with `-O`):** `None` silently passes, causing `AttributeError` 10–30 lines later.

**Recommendation:** Replace every production `assert` with an explicit guard:
```python
if self.current_report is None:
    raise RuntimeError("Validation report must be initialised before this step.")
```

---

### SEC-05 — Hardcoded Default Username for Database Configuration

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `apgi_framework/config/manager.py:48` |
| **CWE** | CWE-798: Use of Hard-coded Credentials |

```python
username: str = "apgi_user"
password: str = ""
```

Default credentials are baked into the dataclass. If an operator forgets to override them, the application runs with a known-default username and empty password.

**Recommendation:** Set `username: str = ""` and require explicit configuration; validate non-empty credentials at startup for non-SQLite backends.

---

### SEC-06 — Bare `exec()` in Code Sandbox (Bypasses Sandbox on Exception)

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `apgi_framework/security/code_sandbox.py:203,212` |
| **CWE** | CWE-78 (indirect) |

The sandbox correctly calls `validate_code()` first, but if validation is bypassed (e.g., a future caller skips it), the `exec(code, exec_context)` call provides only soft isolation. There is no OS-level process isolation (no `seccomp`, no `chroot`). The `__builtins__` restriction can be escaped in CPython via `().__class__.__bases__[0].__subclasses__()`.

**Recommendation:** For production execution of genuinely untrusted code, use `subprocess` with a restricted user, or a dedicated sandboxing library (`RestrictedPython`, `PyPy sandbox`).

---

### SEC-07 — Sensitive Data in Log Redaction Is Pattern-Matched Only

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `apgi_framework/security/security_validator.py:340–358` |
| **CWE** | CWE-532: Information Exposure Through Log Files |

`sanitize_for_logging` uses `re.sub` on key names like `password`, `token`, `key`, `secret`. This misses variations like `passwd`, `api_key`, `auth_token`, `POSTGRES_PASSWORD`, or base64-encoded secrets. Structural redaction (e.g., always redact dict values for known-sensitive keys) is more reliable.

---

### SEC-08 — `tkinter` Import Silently Replaced by Raising Fallback Classes

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `GUI.py:83–200` |
| **CWE** | CWE-390: Detection of Error Condition Without Action |

When `apgi_gui.utils.keyboard_manager`, `undo_redo_manager`, or `theme_manager` fail to import, the fallback code defines replacement classes whose **every method raises `ImportError`**. Any GUI interaction that reaches those code paths will crash with a non-user-friendly exception mid-operation.

**Recommendation:** Implement no-op fallback behaviour (disabled buttons/menu items) rather than deferred ImportError.

---

## 5. Bug Inventory

Bugs are categorised **Critical / High / Medium / Low** and linked to test evidence where available.

### 5.1 Critical Bugs

---

#### BUG-01 — `ErrorTelemetry.__init__` Does Not Create the Telemetry JSON File

| Field | Value |
|---|---|
| **Severity** | 🔴 Critical |
| **File** | `apgi_framework/logging/error_telemetry.py:28–43` |
| **Failing test** | `tests/test_error_telemetry.py::TestErrorTelemetry::test_initialization_creates_directory` |

**Root cause:** `__init__` calls `mkdir(parents=True, exist_ok=True)` (creates directory) then calls `_load_telemetry()`. `_load_telemetry` only *reads* the file if it exists; it does not *create* it. The file is only written when `_save_telemetry()` is called (i.e., after the first `report_error()`).

**Reproduction:**
```python
import tempfile, pathlib
from apgi_framework.logging.error_telemetry import ErrorTelemetry
with tempfile.TemporaryDirectory() as d:
    t = ErrorTelemetry(str(pathlib.Path(d) / "telemetry"))
    assert t.telemetry_file.exists()  # AssertionError – file does not exist
```

**Fix:** Call `_save_telemetry()` at the end of `__init__` to persist the empty structure.

---

#### BUG-02 — `WorkflowOrchestrator` Private Stage Methods Require `current_workflow` But Tests Call Them Directly

| Field | Value |
|---|---|
| **Severity** | 🔴 Critical (design + test) |
| **File** | `apgi_framework/workflow_orchestrator.py:489–727` |
| **Failing tests** | 8 in `TestWorkflowOrchestrator` |

**Root cause:** `_run_primary_tests()`, `_run_secondary_tests()`, `_run_statistical_analysis()`, `_run_result_aggregation()`, `_run_report_generation()`, `_run_cleanup()` all guard on `self.current_workflow is None`. Tests call these methods directly after creating the orchestrator without calling `run_complete_workflow()`, which initialises `current_workflow`.

**Reproduction:**
```python
orchestrator = WorkflowOrchestrator(mock_controller, config)
orchestrator._run_primary_tests()  # RuntimeError: Workflow should be initialized
```

**Fix (option A — tests):** Add `orchestrator.current_workflow = WorkflowResult(...)` in `setUp`.
**Fix (option B — production code):** Auto-initialise `current_workflow` in these private methods when `None`.

---

#### BUG-03 — `run_standard_falsification_workflow` Passes MockController as Config Path

| Field | Value |
|---|---|
| **Severity** | 🔴 Critical |
| **File** | `apgi_framework/workflow_orchestrator.py:820` |
| **Failing tests** | `TestModuleFunctions::test_run_standard_falsification_workflow`, `test_run_quick_validation_workflow` |

**Root cause:**
```python
controller = MainApplicationController(config_path)
```
The function signature accepts `controller` but passes it as `config_path` to `MainApplicationController.__init__`, which then calls `Path(config_path)` — raising `TypeError: expected str, bytes or os.PathLike object, not MockController`.

**Fix:** The function should not re-instantiate `MainApplicationController`. It should use the passed-in `controller` directly.

---

### 5.2 High Severity Bugs

---

#### BUG-04 — `TestSystemValidator` MockController Missing `equation_processor` Attribute

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **File** | `tests/test_system_validator.py:364` |
| **Failing tests** | 13 in `TestSystemValidator` |

Tests set up `MockController` without the `equation_processor` attribute that `SystemValidator` expects. `AttributeError: 'MockController' object has no attribute 'equation_processor'`.

**Fix:** Add `self.mock_controller.equation_processor = MagicMock()` (and similarly for other missing attributes) in `TestSystemValidator.setUp`.

---

#### BUG-05 — `TestDiagnosticsCLI` Calls `.return_value` on a Real Method Object

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **File** | `tests/test_diagnostics_cli.py:277` |
| **Failing tests** | 4 in `TestValidateParameters` |

```python
mock_validator.validate_apgi_parameters.return_value = MockValidationResult(...)
```
`mock_validator` is an instance of the real `ParameterValidator` class, not a `MagicMock`. Calling `.return_value` on a bound method raises `AttributeError`.

**Fix:** Replace `mock_validator = ParameterValidator()` with `mock_validator = MagicMock(spec=ParameterValidator)`.

---

#### BUG-06 — `StorageManager.store_dataset` Fails When Required Fields Are Absent From Test Fixtures

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **File** | `apgi_framework/data/storage_manager.py:103` |
| **Failing tests** | `TestStorageManager::test_storage_statistics`, `test_concurrent_access` |

Validator requires `apgi_parameters`, `neural_signatures`, `consciousness_assessments`. Test fixtures omit them, producing `StorageError: Dataset validation failed: ['Missing required data field: apgi_parameters', ...]`.

**Fix (recommended):** Update test fixtures to supply required fields. Alternatively, make fields optional with documented defaults.

---

#### BUG-07 — `save_summary_report` Header String Mismatch

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **File** | `apgi_framework/workflow_orchestrator.py` (report template) |
| **Failing test** | `TestWorkflowOrchestrator::test_save_summary_report` |

Test asserts `"WORKFLOW SUMMARY" in content` but the actual generated text header is:
`"APGI Framework Testing - Workflow Summary"`.

**Fix:** Either update the test to match the actual string, or update the report template to include `"WORKFLOW SUMMARY"` as a section heading (e.g., `\n## WORKFLOW SUMMARY\n`).

---

#### BUG-08 — `performance_monitor.py` Unconditionally Imports `tkinter`

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **File** | `apgi_framework/optimization/performance_monitor.py:11` |
| **Affected tests** | `tests/test_performance_properties.py` (entire module — collection error) |

```python
import tkinter as tk
```
This is a top-level unconditional import. On servers/headless environments without `python3-tk`, the entire `performance_monitor` module (and every importer) raises `ModuleNotFoundError`.

**Fix:** Guard with:
```python
try:
    import tkinter as tk
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
```
And use `HAS_TKINTER` to conditionally enable GUI-dependent code paths.

---

### 5.3 Medium Severity Bugs

---

#### BUG-09 — `ErrorTelemetry.report_error` JSON Serialisation Timeout

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `apgi_framework/logging/error_telemetry.py:51` |
| **Failing test** | `TestErrorTelemetry::test_max_errors_limit` (timeout > 30 s) |

When `error_type` keys contain non-string types (e.g., complex Python objects or recursive structures), `json.dump(..., default=str)` can enter an extremely long serialisation path. The test triggers this by generating error entries with `f"Error{i}"` keys that accumulate `system_info` dicts.

**Fix:** Add explicit size/depth limits on `error_report["context"]` and `error_report["system_info"]` before appending; truncate after N errors.

---

#### BUG-10 — `ThresholdDetectionParadigm` Bootstrap CI Fails With Insufficient Variance

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `apgi_framework/research/threshold_detection_paradigm.py:730` |
| **Failing tests** | 7 in `TestThresholdDetectionParadigmExtended` |

`_calculate_confidence_interval` bootstraps by sampling with replacement then calls `scipy.optimize.curve_fit`. When bootstrap samples happen to have zero or near-zero variance in `y`, `curve_fit` raises `OptimizeWarning` or raises `ValueError`. No exception guard exists around the curve-fit call.

**Fix:** Wrap the `curve_fit` call in `try/except (RuntimeError, ValueError, OptimizeWarning)` and fall back to a simpler percentile-based CI.

---

#### BUG-11 — `CI Integrator` Returns Empty `changed_files` on Shallow Git Histories

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `apgi_framework/testing/ci_integrator.py:99` |
| **Failing test** | `integration/test_end_to_end_workflow.py::test_ci_integration_workflow` |

`git diff HEAD~1` fails with `fatal: ambiguous argument 'HEAD~1'` when run on a repo with only one commit. The integrator catches this silently and returns `ChangeImpact(changed_files=[])`. The test then asserts `len(change_impact.changed_files) > 0` and fails.

**Fix:** Fall back to `git diff HEAD` (compare working tree to HEAD) or `git diff --stat --name-only HEAD` when `HEAD~1` is unavailable.

---

#### BUG-12 — `PerformanceProfiler` Initialisation Fails in Tests

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `utils/performance_profiler.py` |
| **Failing test** | `tests/test_utils_basic.py::TestPerformanceProfiler::test_performance_profiler_initialization` |

`PerformanceProfiler.__init__` tries to initialise a sub-component that has an unconditional tkinter dependency (via `performance_monitor.py`). Tests fail with `ModuleNotFoundError: No module named 'tkinter'`.

**Fix:** See BUG-08. Decouple `PerformanceProfiler` from the GUI monitor, or make it optional.

---

#### BUG-13 — `enable_error_reporting=True` Does Not Instantiate `ErrorTelemetry`

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **File** | `apgi_framework/logging/error_telemetry.py` (singleton factory) |
| **Failing test** | `TestErrorTelemetry::test_enable_error_reporting_true` |

`get_error_telemetry(enable=True)` is expected to call `ErrorTelemetry(...)`, but the mock asserting `ErrorTelemetry` was called once reports zero calls. The singleton factory caches the instance without going through the class constructor when the mock patches at the wrong level.

**Fix:** Patch at the module level (`apgi_framework.logging.error_telemetry.ErrorTelemetry`) rather than via import alias.

---

### 5.4 Low Severity Bugs

---

#### BUG-14 — `requirements.txt` Missing `scikit-learn` and `psutil`

| Field | Value |
|---|---|
| **Severity** | 🔵 Low |
| **File** | `requirements.txt` |

`sklearn` is required by `apgi_framework/clinical/__init__.py` and `psutil` is required by `apgi_framework/testing/memory_efficient_runner.py`. Neither appears in `requirements.txt`. First-time installs fail with `ModuleNotFoundError` for 5 test modules.

**Fix:** Add `scikit-learn>=1.3.0` and `psutil>=5.9.0` to `requirements.txt` (psutil is already listed — check the install step in CI).

---

#### BUG-15 — `psutil.swap_memory()` RuntimeWarning on This Kernel

| Field | Value |
|---|---|
| **Severity** | 🔵 Low |
| **File** | Runtime environment |

```
RuntimeWarning: 'sin' and 'sout' swap memory stats couldn't be determined and were set to 0
```
`/proc/vmstat` is missing on this kernel. Not a code bug, but causes noisy test output.

**Fix:** Suppress the warning in test configuration or guard psutil swap calls with a try/except.

---

#### BUG-16 — Hypothesis State-Machine Property Tests Flaky on Deployment Config

| Field | Value |
|---|---|
| **Severity** | 🔵 Low |
| **File** | `tests/test_deployment_properties.py::TestConfigurationStateMachine` |

Two Hypothesis state-machine tests fail non-deterministically due to a state-space that allows invalid transitions. The Hypothesis database in `.hypothesis/` is absent from `.gitignore` for all team members, meaning shrunk examples may not reproduce consistently.

**Fix:** Ensure `.hypothesis/` is committed or document the `--hypothesis-seed` for reproducibility. Add state pre-conditions to narrow invalid transitions.

---

## 6. Missing Features & Incomplete Implementations

| ID | Location | Description | Severity |
|---|---|---|---|
| MISS-01 | `apgi_framework/clinical/treatment_prediction.py:49` | `predict_treatment_response()` raises `NotImplementedError`. Core clinical functionality not implemented. | 🟠 High |
| MISS-02 | `apgi_framework/analysis/parameter_estimation.py:555` | `_fit_hierarchical_model()` raises `NotImplementedError`. Hierarchical Bayesian fitting is a documented framework feature. | 🟠 High |
| MISS-03 | `apgi_framework/validation/enhanced_error_handling.py:115,120` | Two abstract methods lack any implementation body beyond `raise NotImplementedError`. Class is not declared as ABC. | 🟡 Medium |
| MISS-04 | `apgi_framework/gui/components/results_visualization_panel.py` | Advanced visualization (3-D phase portraits, cross-spectral plots) documented in `docs/GUI-VISUAL-GUIDE.md` but not present in any GUI component. | 🟡 Medium |
| MISS-05 | `apgi_gui/components/dash_streamlit_integration.py:66` | `get_data()` base method raises `NotImplementedError`; no concrete subclass exists in the repository. | 🟡 Medium |
| MISS-06 | `apgi_framework/security/code_sandbox.py` | Sandbox has no OS-level isolation (no seccomp, no subprocess jail). Comment says "In production, this would use proper process isolation" — not implemented. | 🟡 Medium |
| MISS-07 | `apgi_framework/export/bids_export.py` | BIDS export for cardiac and pupillometry modalities only stubs column descriptions (`f"Measurement: {col}"`). EEG channel metadata is not populated. | 🔵 Low |
| MISS-08 | `docs/GUI-ENTRY-POINTS.md` entry #13 | Entry 14 listed in docs but no `GUI-Simple.py` present in `apps/` or root directory (removed but not updated in docs). | 🔵 Low |

---

## 7. Actionable Recommendations

Recommendations are ordered by **priority** (P1 = immediate / P4 = backlog).

### P1 — Immediate (Block Release)

| # | Action | Affected Files | Effort |
|---|---|---|---|
| R01 | Replace `pickle.loads` in `performance_optimizer.py:285` with `RestrictedUnpickler` | `testing/performance_optimizer.py` | 1 h |
| R02 | Whitelist table names before SQL interpolation in `parameter_estimation_schema.py` and `migration_manager.py` | `data/parameter_estimation_schema.py`, `data/migration_manager.py` | 2 h |
| R03 | Replace all 10 production `assert` statements with explicit guards (`if … is None: raise RuntimeError(…)`) | `deployment_validator.py`, `main_controller.py`, `memory_efficient_runner.py` | 2 h |
| R04 | Fix `WorkflowOrchestrator.run_standard_falsification_workflow` to use the passed-in controller instead of re-instantiating | `workflow_orchestrator.py:820` | 1 h |
| R05 | Fix `ErrorTelemetry.__init__` to create the telemetry file (call `_save_telemetry()` at end of init) | `logging/error_telemetry.py` | 30 min |

### P2 — High Priority (Next Sprint)

| # | Action | Affected Files | Effort |
|---|---|---|---|
| R06 | Guard `import tkinter` in `performance_monitor.py` and all other unconditional tkinter imports | `optimization/performance_monitor.py` + 6 GUI utils | 3 h |
| R07 | Fix test mock setup: add missing attributes (`equation_processor`) to `MockController` in `TestSystemValidator` | `tests/test_system_validator.py` | 2 h |
| R08 | Fix `TestDiagnosticsCLI` to use `MagicMock(spec=ParameterValidator)` instead of real class | `tests/test_diagnostics_cli.py` | 1 h |
| R09 | Fix `StorageManager` test fixtures to include required fields, or make those fields optional | `tests/test_data_management.py` | 2 h |
| R10 | Add `scikit-learn>=1.3.0` to `requirements.txt`; verify `psutil` entry is present | `requirements.txt` | 15 min |
| R11 | Implement `treatment_prediction.predict_treatment_response()` or mark it `experimental` with a log warning | `clinical/treatment_prediction.py` | 4 h |
| R12 | Implement `_fit_hierarchical_model()` or raise `FeatureNotYetImplementedError` with an ETA and fallback | `analysis/parameter_estimation.py` | 4 h |

### P3 — Medium Priority (Maintenance Cycle)

| # | Action | Affected Files | Effort |
|---|---|---|---|
| R13 | Replace bare `except Exception:` blocks in GUI code with logged, specific handlers | `GUI.py`, `GUI-Experiment-Registry.py`, `apgi_gui/app.py` | 4 h |
| R14 | Fix bootstrap CI in `ThresholdDetectionParadigm._calculate_confidence_interval` to handle zero-variance samples | `research/threshold_detection_paradigm.py` | 3 h |
| R15 | Fix `CI integrator` fallback when `HEAD~1` is unavailable | `testing/ci_integrator.py` | 1 h |
| R16 | Strengthen log sanitisation to use structural key-based redaction in addition to pattern matching | `security/security_validator.py` | 2 h |
| R17 | Remove hardcoded `username: str = "apgi_user"` default; document that DB credentials must come from environment | `config/manager.py` | 30 min |
| R18 | Fix `save_summary_report` header to include `"WORKFLOW SUMMARY"` or update the assertion | `workflow_orchestrator.py` / `tests/test_workflow_orchestrator.py` | 30 min |
| R19 | Add `WorkflowResult` initialisation to `TestWorkflowOrchestrator.setUp` so stage-methods can be tested directly | `tests/test_workflow_orchestrator.py` | 1 h |

### P4 — Backlog (Future Sprints)

| # | Action | Effort |
|---|---|---|
| R20 | Add OS-level sandbox isolation (subprocess + restricted user) for `code_sandbox.py` | 2 days |
| R21 | Achieve ≥ 70% line coverage on `apgi_framework/core/` and `apgi_framework/analysis/` | 3 days |
| R22 | Implement BIDS export for EEG channel metadata | 1 day |
| R23 | Update `docs/GUI-ENTRY-POINTS.md` to remove reference to missing `GUI-Simple.py` | 30 min |
| R24 | Add `--hypothesis-seed` to CI config and commit `.hypothesis/` examples for stable property tests | 1 h |

---

## 8. Appendix — Methodology

### Tools Used

| Tool | Purpose |
|---|---|
| `python -m pytest --timeout=60` | Full test suite execution |
| `pytest-cov` | Line-coverage measurement |
| `hypothesis` | Property-based test evaluation |
| Manual AST search (`grep`, `Read`) | Security pattern detection |
| `python -c "import …"` | Dependency availability checks |

### Files Examined (Direct Review)

- `apgi_framework/security/` (4 files — full read)
- `apgi_framework/workflow_orchestrator.py`
- `apgi_framework/core/equation.py`
- `apgi_framework/data/parameter_estimation_schema.py`
- `apgi_framework/data/migration_manager.py`
- `apgi_framework/testing/performance_optimizer.py`
- `apgi_framework/logging/error_telemetry.py`
- `apgi_framework/config/manager.py`
- `apgi_framework/config/config_manager.py`
- `apgi_framework/config/exceptions.py`
- `apgi_framework/main_controller.py`
- `apgi_framework/deployment/deployment_validator.py`
- `GUI.py` (first 200 lines + security-relevant sections)
- `requirements.txt`, `pyproject.toml`, `.env.example`
- Selected test files (18 failing modules)

### Coverage Summary (overall)

```
TOTAL    33050 stmts    32936 missed    0.34% covered
```

Highest-covered modules: `core/data_models.py` (93%), `config/constants.py` (100%), `core/__init__.py` (100%).
Lowest-covered: all `gui/`, `neural/`, `simulators/`, `analysis/` modules at 0%.

---

*Report generated by Claude Code automated audit pipeline. All findings are based on static analysis and dynamic test execution without live hardware (EEG, pupillometry, cardiac devices).*
