# APGI Framework — End-to-End Application Audit Report

**Version:** 4.0
**Date:** 2026-03-13
**Auditor:** Claude (Automated Security & Quality Audit)
**Branch:** `claude/app-audit-security-Phx6T`
**Scope:** Full codebase — `apgi_framework/`, `apgi_gui/`, `GUI*.py`, `apps/`, `utils/`, `tests/`, infrastructure files

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [KPI Scores Table](#kpi-scores-table)
3. [Audit Methodology](#audit-methodology)
4. [Dimension 1 — Functional Completeness](#dimension-1--functional-completeness)
5. [Dimension 2 — UI/UX Consistency](#dimension-2--uiux-consistency)
6. [Dimension 3 — Responsiveness & Performance](#dimension-3--responsiveness--performance)
7. [Dimension 4 — Error Handling & Resilience](#dimension-4--error-handling--resilience)
8. [Dimension 5 — Implementation Quality](#dimension-5--implementation-quality)
9. [Security Audit](#security-audit)
10. [Bug Inventory](#bug-inventory)
11. [Missing Features Log](#missing-features-log)
12. [Actionable Recommendations](#actionable-recommendations)
13. [Appendix — Test Run Results](#appendix--test-run-results)

---

## Executive Summary

The APGI Framework is a research-grade desktop application platform for consciousness studies, falsification testing, and neural signal simulation. The codebase is large (~85,000+ lines of Python across the framework, ~7,000 lines in the main GUI alone) and architecturally ambitious, encompassing a GUI layer, REST/WebSocket API, CLI, data persistence, ML integration, and a secure sandboxed execution environment.

### Overall Health

The application demonstrates **above-average maturity** for a research-tooling project. Security infrastructure (secure pickle handling, input sanitization, path traversal protection, CSRF, production validators) is genuinely well-considered. However, the audit uncovered **fifteen confirmed test failures**, **three security vulnerabilities of varying severity**, several **stub implementations** shipped as functional features, and a **dangerously low test coverage** of ~9% for the overall framework codebase.

### Key Findings Summary

| Category | Finding |
|---|---|
| Test Suite | 15 failures / 135 passing / 6 skipped (out of ~156 collectible tests, ~38 files uncollectable due to missing deps) |
| Code Coverage | ~9.07% overall framework coverage — critically low |
| Critical Bugs | 1 (unsafe `pickle.load` in ML module) |
| High Bugs | 5 (stub functions shipped as real features, race condition in test state, CORS missing HTTP-security headers, config manager throws on corrupt JSON instead of falling back) |
| Medium Bugs | 6 (non-reproducible simulation, preferences path-traversal, test_name casing mismatch, print() pollution, missing authentication in web API, unseeded RNG in pharmacological simulator) |
| Low Bugs | 4 (minor UX gaps, missing SMTP credential masking in logs, docker-compose exposes services on all interfaces, Jupyter token not required) |
| Missing Features | 4 major (consciousness evaluation stub, short-term APGI model stub, combined APGI analysis stub, no web API authentication) |

---

## KPI Scores Table

| Dimension | Score | Status | Threshold |
|---|---|---|---|
| Functional Completeness | **62 / 100** | ⚠️ NEEDS WORK | ≥ 75 |
| UI/UX Consistency | **71 / 100** | ⚠️ NEEDS WORK | ≥ 75 |
| Responsiveness & Performance | **74 / 100** | ⚠️ NEEDS WORK | ≥ 75 |
| Error Handling & Resilience | **78 / 100** | ✅ ACCEPTABLE | ≥ 75 |
| Implementation Quality | **61 / 100** | ❌ BELOW THRESHOLD | ≥ 75 |
| **OVERALL** | **69 / 100** | ⚠️ NEEDS WORK | ≥ 75 |

**Color legend:**
✅ Green (≥ 75) — Acceptable
⚠️ Yellow (60–74) — Needs Work
❌ Red (< 60) — Below Threshold

---

## Audit Methodology

### Scope

All source files were examined statically. Dynamic analysis was performed by installing available dependencies and running the pytest suite:

```
pytest tests/ --ignore=tests/framework --ignore=tests/integration -q
```

`tests/framework/` and `tests/integration/` were excluded at collection time due to missing optional dependencies (`numpy`, `hypothesis`, `h5py`, `statsmodels`, `psycopg2`) that are not listed in `requirements.txt`. This itself is noted as a bug (see BUG-013).

### Tools Used

- Static code analysis (manual grep, AST review)
- `pytest` with `pytest-cov`
- Docker / compose configuration review
- Security pattern review (OWASP Top-10, CWE checklist)

---

## Dimension 1 — Functional Completeness

**Score: 62 / 100**

### What Works

- Core mathematical engine: `APGIEquation`, `PrecisionCalculator`, `PredictionErrorProcessor`, `SomaticMarkerEngine`, `ThresholdManager` — all implemented with good numerical stability.
- Falsification tests: `PrimaryFalsificationTest`, `ConsciousnessWithoutIgnitionTest`, `ThresholdInsensitivityTest`, `SomaBiasTest` — all wired to GUI.
- Neural simulators: `P3bSimulator`, `GammaSimulator`, `BOLDSimulator`, `PCICalculator` — seeded RNGs, reproducible outputs.
- CLI (`apgi_framework/cli.py`): fully-functional argument parser with range-validated inputs; runs experiments, generates reports, manages configurations.
- Data import/export: CSV, JSON, Excel, pickle (via `safe_pickle_load`).
- Preferences dialog: theme switching, folder selection, thread pool size, console line limit.
- Config management: load/save JSON, presets, env-var overrides.
- Logging: centralized structured logging with telemetry capture.

### What is Incomplete / Stubbed

| Feature | Location | Severity |
|---|---|---|
| `run_consciousness_evaluation()` | `GUI.py:6511` | High — returns hardcoded fake metrics (0.78, 0.65, 0.82) |
| `short_term_apgi_model()` | `GUI.py:6530` | High — prints placeholder strings only |
| `combined_apgi_analysis()` | `GUI.py:6538` | High — prints placeholder strings only |
| Web API Authentication | `apgi_gui/components/web_interface.py` | Critical — all REST endpoints are unauthenticated |

The three GUI analysis methods log messages that simulate real processing ("Step 1: Processing neural data…") but produce no actual computation. Users see a success dialog with no data. This is a functional regression that misrepresents the application's capabilities.

---

## Dimension 2 — UI/UX Consistency

**Score: 71 / 100**

### Positive Findings

- Consistent use of `customtkinter` (`ctk`) throughout the main GUI.
- `GUIConstants` dataclass centralizes all sizing, colors, and defaults — no magic numbers scattered in widget code.
- Toolbar and menu bar follow a logical grouping: File → Edit → View → Tests → Analysis → Data → Tools → Help.
- Status bar provides real-time feedback for long-running operations.
- Tooltips, keyboard shortcuts, undo/redo managed by dedicated utility managers with graceful no-op fallbacks when `apgi_gui` package is not installed.
- Preferences dialog exposes theme switching, folder paths, and performance settings.

### Issues Found

- **Theme persistence is not implemented.** The preferences `save_preferences()` function calls `ctk.set_appearance_mode()` in memory but does not write the theme choice to disk or to the config file. On next launch, the theme reverts to the system default. (See BUG-006.)
- **Preferences auto-save checkbox has no effect.** The `autosave_var` BooleanVar is read but never acted upon — there is no auto-save logic wired to it. (See BUG-007.)
- **The `test_running` flag has a race condition.** Because `test_running` is a plain `bool` (not a threading lock), two rapid button clicks before the first thread increments the flag can bypass the guard and run concurrent tests. (See BUG-003.)
- **No visual disabled-state feedback for running operations.** When a test is running, the sidebar buttons are not disabled — only a console log message indicates another test is in progress. This is inconsistent with standard desktop UX.
- **Result display for `_on_test_completion_callback` dumps all `__dict__` attributes unfiltered**, including internal `_`-prefixed fields if present. (See BUG-008.)

---

## Dimension 3 — Responsiveness & Performance

**Score: 74 / 100**

### Positive Findings

- All long-running operations (simulations, data import/export, validation, cleaning, plotting) are dispatched via `run_in_thread()` through a managed `ThreadPoolManager` (singleton, max 8 workers).
- GUI updates from worker threads are always routed through `self.after(0, callback)` — correct Tk thread-safety pattern.
- `MatplotlibManager` caps active figures at 50, runs `gc.collect()` on close, and proactively cleans up via `_cleanup_old_figures()`.
- `matplotlib.use("Agg")` prevents threading-related crashes with the interactive matplotlib backend.
- Subprocess execution in `execute_script()` uses a 5-minute timeout and kills the process on expiry.

### Issues Found

- **Thread pool size is hardcoded to 8** in `ThreadPoolManager.__init__` regardless of the `APGI_MAX_WORKERS` / `APGI_THREAD_POOL_SIZE` environment variables. The preference dialog exposes this setting but it is never applied to the actual pool (the pool is a singleton initialized once). (See BUG-009.)
- **Pharmacological simulator uses global `np.random` instead of a seeded RNG instance.** All other simulators use `self.rng = np.random.RandomState(random_seed)`. This makes `PharmacologicalSimulator` non-reproducible. (See BUG-010.)
- **Memory tracking for undo stack is initialized but `_undo_memory_usage` is never incremented.** The `apgi_gui/app.py` declares `_undo_memory_limit` and `_undo_memory_usage` but contains no code to update `_undo_memory_usage` when items are pushed onto the undo stack, making the memory limit enforcement dead code.
- **`plt.get_fignums()` inside `close_all_figures()` re-opens closed figures.** Calling `plt.figure(num)` with an existing number returns that figure, but with a non-existent number creates a new one, causing potential figure leaks if `id` values don't match stored IDs.

---

## Dimension 4 — Error Handling & Resilience

**Score: 78 / 100**

### Positive Findings

- `GUIErrorHandler` categorises errors by severity (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) and limits repeated dialogs for the same error class.
- `ErrorRecoveryManager` with `RetryConfig` and `@with_retry` decorator covers transient failures.
- `APGIFrameworkError` exception hierarchy is well-structured with contextual fields.
- All database operations (`_store_metadata_sqlite`, `_store_metadata_postgresql`) use parameterised queries — no SQL injection surface.
- `safe_pickle_load` / `safe_pickle_dump` guard all pickle I/O in `persistence_layer.py`, `experiment_tracker.py`, `error_handling.py`.
- `FileNotFoundError` and `json.JSONDecodeError` are caught separately in `load_config` with meaningful messages.
- Thread timeout enforcement in subprocess execution (`communicate(timeout=300)`).

### Issues Found

- **`ConfigManager.__init__` raises `ConfigurationError` on corrupt JSON.** The test `test_load_config_invalid_json` documents the expected behaviour: silently fall back to defaults. Currently, construction of `ConfigManager(path)` with a malformed file raises an exception, crashing the application before the GUI is shown. (BUG-001.)
- **`ConfigManager` does not catch `ConfigurationError` raised by `load_config`.** The `__init__` method at `config_manager.py:225` calls `self.load_config(config_path)` without a `try/except`, so the exception propagates to the caller. (BUG-001, same root cause.)
- **`_on_test_error` callback exposes raw exception strings to end-users.** `messagebox.showerror(…, f"Test failed: {error_msg}")` may leak internal module paths, class names, or stack traces. User-facing messages should be sanitised. (BUG-011.)
- **No graceful degradation when PostgreSQL is unavailable.** `PersistenceLayer.__init__` attempts `psycopg2.connect` immediately when `backend="postgresql"` is set; failure raises `PersistenceError` with no fallback to SQLite. (BUG-012.)

---

## Dimension 5 — Implementation Quality

**Score: 61 / 100**

### Positive Findings

- Security module is production-quality: `InputSanitizer`, `SecureFileHandler`, `SecurePickleValidator`, `CodeSandbox`, `SecurityValidator` — well-structured with clear threat models.
- `ProductionValidator` enforces `SECRET_KEY` length, debug-mode prohibition, CORS wildcard detection at startup.
- Type annotations throughout (`py.typed` marker, dataclasses, TypedDict).
- Centralized constants (`GUIConstants`, `TimingConstants`, `DataConstants`) eliminate magic numbers.
- CI/CD pipeline (`ci_pipeline.yml`) runs lint, mypy, black, and tests on 5 Python versions × 3 OS.

### Issues Found

- **Overall test coverage is 9.07%.** The vast majority of framework modules (`workflow_orchestrator.py`, `validation/`, `gui/`, `optimization/`, `adaptive/`, `analysis/`) have 0% coverage. This means regressions in core business logic will go undetected. (BUG-013.)
- **System validator produces human-readable `test_name` values with spaces/title-case, but tests assert snake_case.** `system_validator.py` sets `test_name="APGI Equation Accuracy"` while `test_system_validator.py:373` asserts `== "apgi_equation_accuracy"`. This is a test/implementation contract mismatch causing 15 failures. (BUG-002.)
- **379 `print()` calls in `apgi_framework/` (excluding CLI).** Production code should use the logging framework for all output. Direct `print()` bypasses log level controls, rotation, and filtering. (BUG-014.)
- **`psycopg2` is a hard import in `persistence_layer.py`** even when using SQLite or HDF5 backends. This forces all users to install PostgreSQL bindings even when they never use that backend. Should be a conditional/lazy import. (BUG-015.)
- **`apgi_framework/core/models.py:169` uses `np.random.randn` without seeding.** `PredictiveIgnitionNetwork` weights are randomly initialised on each run, making results non-reproducible without manual seeding. (BUG-010 companion.)

---

## Security Audit

### Vulnerability Summary

| ID | Title | Severity | CWE | File |
|---|---|---|---|---|
| SEC-001 | Unsafe `pickle.load()` in ML module | **Critical** | CWE-502 | `apgi_framework/ml/ml_integration.py:480` |
| SEC-002 | No HTTP security headers in Flask app | **High** | CWE-693 | `apgi_gui/components/web_interface.py` |
| SEC-003 | Unauthenticated REST API endpoints | **High** | CWE-306 | `apgi_gui/components/web_interface.py` |
| SEC-004 | Preference folder paths not sanitised | **Medium** | CWE-22 | `GUI.py:5091` |
| SEC-005 | Docker Redis/Grafana/Jupyter exposed on all interfaces | **Medium** | CWE-284 | `docker-compose.yml` |
| SEC-006 | Jupyter token empty-string allowed | **Medium** | CWE-287 | `docker-compose.yml` |
| SEC-007 | SMTP credentials in config dict (no masking in logs) | **Low** | CWE-312 | `apgi_framework/testing/notification_manager.py:605` |

---

### SEC-001 — Unsafe `pickle.load()` in ML Module (CRITICAL)

**File:** `apgi_framework/ml/ml_integration.py:480`
**CWE:** CWE-502 — Deserialization of Untrusted Data

```python
# VULNERABLE CODE (ml_integration.py:473-480)
import pickle
with open(filepath, "rb") as f:
    model = pickle.load(f)   # <-- unsafe: no type validation
```

**Issue:** `ml_integration.py::MLIntegration.load_model()` uses a bare `pickle.load()` on an arbitrary file path. All other persistence paths in this codebase correctly use `apgi_framework.security.secure_pickle.safe_pickle_load()`, which validates the pickled type against a whitelist before unpickling. An attacker who can write a crafted `.pkl` file to the model directory (or trick the user into loading one via the file dialog) can achieve arbitrary code execution.

**Reproduction:**
1. Create `malicious_model.pkl` containing a `__reduce__` exploit.
2. Place it in the model directory or pass via `load_model("consciousness", path)`.
3. On load, arbitrary shell commands execute.

**Fix:**
```python
from ..security.secure_pickle import safe_pickle_load
# ...
model = safe_pickle_load(filepath, expected_types={your_model_class})
```

---

### SEC-002 — Missing HTTP Security Headers (HIGH)

**File:** `apgi_gui/components/web_interface.py`
**CWE:** CWE-693 — Protection Mechanism Failure

The Flask application does not set any HTTP security headers. An attacker operating in the same network can conduct clickjacking, MIME-sniffing, or XSS attacks.

**Missing headers:**
- `Content-Security-Policy`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` (when TLS is used)

**Fix (add after `_create_flask_app`):**
```python
@self.app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response
```

---

### SEC-003 — Unauthenticated REST API Endpoints (HIGH)

**File:** `apgi_gui/components/web_interface.py:263–360`
**CWE:** CWE-306 — Missing Authentication for Critical Function

All API routes (`/api/experiments`, `/api/config`, `/api/upload`, `/api/realtime`) are accessible to any client with network access. There is no token, session, or API-key check. The `/api/upload` endpoint accepts files and saves them to the `uploads/` directory. The `/api/config` `PUT` endpoint allows unauthenticated modification of application configuration.

**Fix:** Add token-based authentication decorator:
```python
from functools import wraps
from flask import request, jsonify

def require_api_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-API-Token")
        if token != self.app.config["API_TOKEN"]:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
```

---

### SEC-004 — Preference Folder Paths Not Sanitised (MEDIUM)

**File:** `GUI.py:5091–5112`
**CWE:** CWE-22 — Path Traversal

```python
def save_preferences():
    self.data_folder = data_folder_entry.get()        # raw user input
    self.results_folder = results_folder_entry.get()   # raw user input
    for folder in [self.data_folder, self.results_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)                         # creates arbitrary dirs
```

A user (or an automated input) can set the data folder to `/etc/malicious` or `../../sensitive`. `os.makedirs()` will create the directory and subsequent file writes will target it.

**Fix:** Resolve and validate paths against an allowed base:
```python
from apgi_framework.security import sanitize_path
safe_folder = sanitize_path(data_folder_entry.get(), base_dir=Path.home())
self.data_folder = str(safe_folder)
```

---

### SEC-005 — Docker Services Exposed on All Interfaces (MEDIUM)

**File:** `docker-compose.yml`

`redis`, `postgres`, `prometheus`, and `grafana` all publish ports as `"PORT:PORT"` (e.g., `"6379:6379"`, `"5432:5432"`, `"9090:9090"`, `"3000:3000"`). On a multi-homed host, this binds to `0.0.0.0`, making these services accessible from external networks.

**Fix:**
```yaml
ports:
  - "127.0.0.1:6379:6379"   # bind only to localhost
  - "127.0.0.1:5432:5432"
```

---

### SEC-006 — Jupyter Token Not Required (MEDIUM)

**File:** `docker-compose.yml`

```yaml
environment:
  - JUPYTER_TOKEN=${JUPYTER_TOKEN}
```

If `JUPYTER_TOKEN` is not set in the environment, Docker substitutes an empty string, allowing unauthenticated access to the Jupyter notebook server (which provides a full Python REPL and file browser).

**Fix:** Use the `${VARIABLE:?error_message}` syntax:
```yaml
- JUPYTER_TOKEN=${JUPYTER_TOKEN:?JUPYTER_TOKEN must be set}
```

---

### SEC-007 — SMTP Credentials Not Masked in Logs (LOW)

**File:** `apgi_framework/testing/notification_manager.py:597–607`

SMTP credentials are passed as plain-text values in the `config` dict. If the `config` dict is logged (e.g., during debug output of a `NotificationChannel`), the password appears in log files.

**Fix:** Use a `SecureString` wrapper or mask the password field in `__repr__`/`__str__` of the config object.

---

## Bug Inventory

Severity key: 🔴 Critical | 🟠 High | 🟡 Medium | 🟢 Low

### BUG-001 — ConfigManager Raises on Corrupt JSON Instead of Falling Back

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **Component** | `apgi_framework/config/config_manager.py:225` |
| **Test** | `tests/test_config_manager.py::test_load_config_invalid_json` (FAILING) |

**Description:** `ConfigManager.__init__` calls `self.load_config(config_path)` which propagates `ConfigurationError` when the JSON is malformed. The test documents the requirement to silently fall back to defaults.

**Reproduction:**
```python
import tempfile, pathlib
from apgi_framework.config.config_manager import ConfigManager

with tempfile.TemporaryDirectory() as d:
    p = pathlib.Path(d) / "bad.json"
    p.write_text("{invalid json")
    mgr = ConfigManager(str(p))  # raises ConfigurationError
```

**Expected:** `ConfigManager` falls back to defaults and logs a warning.
**Actual:** `ConfigurationError: Invalid configuration file: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)`.

**Fix:**
```python
# In __init__, wrap load_config:
if config_path:
    config_file = self.path_manager.resolve_path(config_path)
    if config_file.exists():
        try:
            self.load_config(config_path)
        except ConfigurationError as e:
            logger.warning(f"Failed to load config '{config_path}': {e}. Using defaults.")
```

---

### BUG-002 — SystemValidator `test_name` Values Are Title-Case, Tests Expect snake_case

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **Component** | `apgi_framework/system_validator.py:417` + `tests/test_system_validator.py:373` |
| **Tests Failing** | 15 tests in `TestSystemValidator` |

**Description:** `ValidationTestResult.test_name` is set to human-readable strings like `"APGI Equation Accuracy"`, but test assertions compare against programmatic identifiers like `"apgi_equation_accuracy"`.

**Reproduction:** `pytest tests/test_system_validator.py -k "test_test_apgi_equation_accuracy"`

**Expected:** `result.test_name == "apgi_equation_accuracy"`
**Actual:** `result.test_name == "APGI Equation Accuracy"`

**Fix options:**
1. Change `system_validator.py` to use snake_case identifiers: `test_name="apgi_equation_accuracy"`.
2. Add a `test_id` field to `ValidationTestResult` for programmatic use and keep `test_name` for display.

---

### BUG-003 — Race Condition in `test_running` Guard

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **Component** | `GUI.py:1148–1165` |

**Description:** The `test_running: bool` flag is checked and set non-atomically. Between the `if self.test_running:` check and the `self.test_running = True` assignment, a second click on a different test button on the same CPU tick can bypass the guard.

**Fix:** Replace with a `threading.Lock`:
```python
self._test_lock = threading.Lock()

def _run_test_safely(self, test_type, test_function):
    if not self._test_lock.acquire(blocking=False):
        self.log_to_console(f"Test already running, skipping {test_type}")
        return
    try:
        test_function()
    except Exception as e:
        self._test_lock.release()
        raise
```

---

### BUG-004 — `run_consciousness_evaluation` / `short_term_apgi_model` / `combined_apgi_analysis` Are Stubs

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **Component** | `GUI.py:6511`, `GUI.py:6530`, `GUI.py:6538` |

**Description:** Three menu actions appear functional (show success dialog, log "completed") but perform no real computation. `run_consciousness_evaluation()` hardcodes result values (0.78, 0.65, 0.82) with no calculation.

**Reproduction:** Click "Run Consciousness Evaluation" from the menu. No data is required, and always the same canned result is displayed.

**Fix:** Implement using existing `MainApplicationController` and `APGIEquation` engine, or raise `NotImplementedError` until implemented and disable the menu item.

---

### BUG-005 — `ConfigManager.save_preset` Can Fail With Directory Not Found

| Field | Value |
|---|---|
| **Severity** | 🟠 High |
| **Component** | `apgi_framework/config/config_manager.py:336` |
| **Test** | `tests/test_config_manager.py::test_save_preset_creates_directory` (FAILING) |

**Description:** The `save_preset` method writes to `self.presets_dir / f"{name}.json"` without ensuring the directory exists. In some test environments where the presets dir uses a tempdir fallback, the parent may be missing.

**Fix:**
```python
self.presets_dir.mkdir(parents=True, exist_ok=True)
```

---

### BUG-006 — Theme Preference Not Persisted to Disk

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `GUI.py:5091–5112` |

**Description:** The `save_preferences()` function applies the theme in memory but writes only `self.data_folder` and `self.results_folder`. On restart, theme reverts to system default.

**Fix:** Save selected theme to the config file or a local preferences JSON file and reload on startup.

---

### BUG-007 — Auto-Save Checkbox Has No Effect

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `GUI.py:4985–4993` |

**Description:** `autosave_var = tk.BooleanVar(value=True)` is created and displayed but never read in `save_preferences()` and no auto-save timer is registered anywhere.

---

### BUG-008 — `_on_test_completion_callback` Dumps Raw `__dict__`

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `GUI.py:2352–2356` |

**Description:** The callback iterates `results.__dict__.items()` and logs every field, including any `_private` fields that happen to exist. This can expose internal state or sensitive computed values.

---

### BUG-009 — Thread Pool Size Preference Not Applied

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `GUI.py:5070`, `apgi_framework/utils/thread_manager.py:29` |

**Description:** The preferences dialog allows changing the thread pool size, and `self.thread_pool_size` is updated, but the `ThreadPoolManager` singleton is initialised once at import time with a hardcoded `max_workers=8` and is never reconfigured. The preference setting is effectively ignored.

---

### BUG-010 — `PharmacologicalSimulator` Uses Unseeded Global RNG

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `apgi_framework/simulators/pharmacological_simulator.py:244,246,358,390,418,440` |

**Description:** All other simulators (`P3bSimulator`, `GammaSimulator`, `BOLDSimulator`, `PCICalculator`) accept a `random_seed` and use `self.rng = np.random.RandomState(seed)`. `PharmacologicalSimulator` calls `np.random.uniform`, `np.random.normal` directly from the global state, making its outputs non-reproducible across runs even when `config.json` specifies `"random_seed": 42`.

---

### BUG-011 — Raw Exception Messages Shown to End Users

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `GUI.py:2367`, multiple `messagebox.showerror` calls |

**Description:** Error dialogs show `f"Test failed: {error_msg}"` where `error_msg` is `str(e)` from the exception. Internal Python errors containing module paths, type names, and stack fragments are exposed to end users.

---

### BUG-012 — PostgreSQL Backend Has No SQLite Fallback

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `apgi_framework/data/persistence_layer.py:167–191` |

**Description:** When `backend="postgresql"` and the database server is unavailable, `PersistenceLayer.__init__` raises `PersistenceError` with no fallback. A graceful degradation to SQLite would prevent loss of experiment data on temporary connectivity issues.

---

### BUG-013 — Test Collection Fails for 38 Test Files Due to Missing Dependencies

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `requirements.txt`, `tests/` |

**Description:** 38 test files fail to collect because `numpy`, `hypothesis`, `h5py`, `statsmodels`, and `psycopg2` are not in `requirements.txt`. The `requirements.txt` lists them as optional (`pip install -e .[all]`) but the test suite requires them. This means CI will silently skip most tests unless `pip install -e .[all]` is run.

**Fix:** Add required test dependencies to `requirements.txt` or create a `requirements-test.txt` and update `.github/workflows/*.yml` accordingly.

---

### BUG-014 — 379 `print()` Calls in Framework Code

| Field | Value |
|---|---|
| **Severity** | 🟡 Medium |
| **Component** | `apgi_framework/` (all modules) |

**Description:** Direct `print()` calls bypass the logging system. This prevents log level control, file rotation, and structured output. Particularly notable in `apgi_framework/installation_validator.py`, `apgi_framework/system_validator.py`, and various GUI modules.

---

### BUG-015 — `psycopg2` Imported Unconditionally in `persistence_layer.py`

| Field | Value |
|---|---|
| **Severity** | 🟢 Low |
| **Component** | `apgi_framework/data/persistence_layer.py:20-21` |

**Description:** `import psycopg2` at the top of the file forces installation of PostgreSQL bindings even for users who only use SQLite or HDF5 backends. This inflates the install footprint and creates a hard dependency on a C extension that requires `libpq-dev` headers.

**Fix:** Move `import psycopg2` inside `_init_postgresql()`.

---

### BUG-016 — `close_all_figures()` May Create New Matplotlib Figures

| Field | Value |
|---|---|
| **Severity** | 🟢 Low |
| **Component** | `GUI.py:990–1005` |

**Description:** `plt.figure(fig_num)` where `fig_num` is not in `plt.get_fignums()` creates a new figure. The comparison between stored `id()` values and figure objects is fragile because Python can reuse memory addresses.

---

### BUG-017 — Docker Compose `JUPYTER_TOKEN` Not Validated

| Field | Value |
|---|---|
| **Severity** | 🟢 Low (Infrastructure) |
| **Component** | `docker-compose.yml` |

See SEC-006 above.

---

### BUG-018 — `_undo_memory_usage` Never Updated

| Field | Value |
|---|---|
| **Severity** | 🟢 Low |
| **Component** | `apgi_gui/app.py:109–113` |

**Description:** `_undo_memory_usage` and `_undo_memory_limit` are declared but `_undo_memory_usage` is never incremented or decremented, making the memory limit enforcement completely inert.

---

## Missing Features Log

| # | Feature | Location | Priority | Notes |
|---|---|---|---|---|
| MF-001 | Consciousness Evaluation implementation | `GUI.py:6511` | P0 | Currently a stub with fake hardcoded results |
| MF-002 | Short-Term APGI Model | `GUI.py:6530` | P0 | Stub — no computation |
| MF-003 | Combined APGI Analysis | `GUI.py:6538` | P0 | Stub — no computation |
| MF-004 | Web API Authentication | `web_interface.py` | P0 — Security | All endpoints are open |
| MF-005 | HTTP Security Headers (Flask) | `web_interface.py` | P1 — Security | No CSP, X-Frame-Options, etc. |
| MF-006 | Theme persistence across restarts | `GUI.py:5091` | P1 | Theme saved in memory only |
| MF-007 | Auto-save functionality | `GUI.py:4988` | P2 | Checkbox exists, no implementation |
| MF-008 | Button disabled-state during test execution | `GUI.py` | P2 | UX — prevents duplicate runs |
| MF-009 | Thread pool reconfiguration | `thread_manager.py` | P2 | Preference is read but not applied |
| MF-010 | PostgreSQL to SQLite fallback | `persistence_layer.py` | P2 | No resilience to DB outages |

---

## Actionable Recommendations

### Priority 0 — Fix Immediately (Security / Data Loss)

| # | Action | File(s) | Effort | Team |
|---|---|---|---|---|
| R-01 | Replace `pickle.load()` with `safe_pickle_load()` in `MLIntegration.load_model()` | `ml/ml_integration.py:473` | 30 min | Backend |
| R-02 | Wrap `ConfigManager.load_config()` call in `__init__` with try/except; fall back to defaults | `config/config_manager.py:225` | 1 h | Backend |
| R-03 | Add API token authentication to all Flask REST endpoints | `web_interface.py` | 2–4 h | Backend |
| R-04 | Add HTTP security headers via Flask `after_request` hook | `web_interface.py` | 1 h | Backend |

### Priority 1 — Fix Before Next Release (High Impact)

| # | Action | File(s) | Effort | Team |
|---|---|---|---|---|
| R-05 | Fix `test_name` values in `system_validator.py` to match test expectations (15 test failures) | `system_validator.py` | 1 h | Backend |
| R-06 | Replace `test_running: bool` with `threading.Lock` to eliminate race condition | `GUI.py:1135` | 1 h | GUI |
| R-07 | Implement or disable stub menu items (`run_consciousness_evaluation`, etc.) | `GUI.py:6511–6548` | 2–8 h | Research/GUI |
| R-08 | Bind Docker service ports to `127.0.0.1` in `docker-compose.yml` | `docker-compose.yml` | 30 min | DevOps |
| R-09 | Require `JUPYTER_TOKEN` with `${JUPYTER_TOKEN:?err}` syntax | `docker-compose.yml` | 15 min | DevOps |
| R-10 | Sanitise preference folder paths against allowed base directory | `GUI.py:5091` | 1 h | GUI |

### Priority 2 — Address in Near Term (Quality / UX)

| # | Action | File(s) | Effort | Team |
|---|---|---|---|---|
| R-11 | Add `random_seed` parameter and `self.rng` to `PharmacologicalSimulator` | `simulators/pharmacological_simulator.py` | 2 h | Backend |
| R-12 | Persist theme to config file on save; reload on startup | `GUI.py:5091`, `config/manager.py` | 2 h | GUI |
| R-13 | Implement auto-save timer using `self.after(interval, save_fn)` | `GUI.py` | 3 h | GUI |
| R-14 | Disable sidebar buttons while test is running; re-enable in `_on_test_complete` | `GUI.py` | 2 h | GUI |
| R-15 | Move `import psycopg2` inside `_init_postgresql()` | `persistence_layer.py:20` | 15 min | Backend |
| R-16 | Add PostgreSQL-to-SQLite fallback on connection failure | `persistence_layer.py:167` | 3 h | Backend |
| R-17 | Sanitise error messages before showing to end users | `GUI.py:2367` | 2 h | GUI |
| R-18 | Mask SMTP password in log output | `notification_manager.py:605` | 30 min | Backend |

### Priority 3 — Technical Debt (Code Health)

| # | Action | File(s) | Effort | Team |
|---|---|---|---|---|
| R-19 | Replace 379 `print()` calls with `logger.*()` | `apgi_framework/` | 4–8 h | Backend |
| R-20 | Add `numpy`, `hypothesis`, `h5py`, `statsmodels` to `requirements.txt` so full test suite runs in CI | `requirements.txt`, CI YAML | 1 h | DevOps |
| R-21 | Increase overall test coverage from 9% to at least 60% for critical paths | `tests/` | 2–4 weeks | Backend |
| R-22 | Fix `_undo_memory_usage` tracking in `apgi_gui/app.py` | `apgi_gui/app.py:109` | 1 h | GUI |
| R-23 | Refactor `close_all_figures()` to use figure object references instead of `id()` | `GUI.py:990` | 1 h | GUI |

---

## Appendix — Test Run Results

### Collectible Tests (partial, missing optional deps)

```
Ran: tests/ (excluding tests/framework, tests/integration)
Results: 15 failed, 135 passed, 6 skipped
Duration: ~17 s
```

### Failing Tests

| Test | File | Cause |
|---|---|---|
| `test_load_config_invalid_json` | `test_config_manager.py` | BUG-001: exception propagated instead of fallback |
| `test_load_preset_corrupted_json` | `test_config_manager.py` | BUG-001: related |
| `test_save_preset_creates_directory` | `test_config_manager.py` | BUG-005: directory not created |
| `test_test_apgi_equation_accuracy` | `test_system_validator.py` | BUG-002: `"APGI Equation Accuracy"` ≠ `"apgi_equation_accuracy"` |
| `test_test_precision_calculations` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_prediction_error_processing` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_somatic_marker_calculations` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_threshold_management` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_sigmoid_function` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_numerical_stability` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_p3b_simulation` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_gamma_simulation` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_bold_simulation` | `test_system_validator.py` | BUG-002 (same) |
| `test_test_consciousness_assessment` | `test_system_validator.py` | BUG-002 (same) |
| `test_run_stress_tests` | `test_system_validator.py` | BUG-002 (same) |

### Uncollectable Test Files (missing deps)

38 test files fail to collect. Key dependencies missing from `requirements.txt`:
- `numpy` (required by 25+ test files)
- `hypothesis` (required by property-based test files)
- `h5py` (required by data management tests)
- `statsmodels` (required by statistical analysis tests)
- `psycopg2` (required by persistence layer tests)

### Code Coverage (Selected Modules)

| Module | Coverage |
|---|---|
| `apgi_framework/validation/input_validation.py` | 89.52% |
| `apgi_framework/validation/error_recovery.py` | 28.47% |
| `apgi_framework/config/config_manager.py` | ~35% |
| `apgi_framework/utils/framework_test_utils.py` | 42.32% |
| `apgi_framework/workflow_orchestrator.py` | 0% |
| `apgi_framework/validation/system_health.py` | 10.40% |
| `apgi_framework/utils/thread_manager.py` | 0% |
| **TOTAL (framework)** | **~9.07%** |

---

*Report generated: 2026-03-13 by automated audit tooling on branch `claude/app-audit-security-Phx6T`.*
