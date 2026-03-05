# APGI Framework — End-to-End Application Audit Report

> **Version:** 1.0
> **Date:** 2026-03-05
> **Branch audited:** `claude/app-audit-security-7D8yh`
> **Auditor:** Claude Code (automated security & quality audit)
> **Scope:** Full codebase — `apgi_framework/`, `apgi_gui/`, `GUI*.py`, `tests/`, `utils/`

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [KPI Scores](#2-kpi-scores)
3. [Application Overview](#3-application-overview)
4. [Bug Inventory](#4-bug-inventory)
   - [Critical](#41-critical-bugs)
   - [High](#42-high-severity-bugs)
   - [Medium](#43-medium-severity-bugs)
   - [Low](#44-low-severity-bugs)
5. [Security Vulnerability Assessment](#5-security-vulnerability-assessment)
6. [Missing Features & Incomplete Implementations](#6-missing-features--incomplete-implementations)
7. [Dimensional Audit Results](#7-dimensional-audit-results)
8. [Actionable Recommendations](#8-actionable-recommendations)
9. [Appendix — File Reference Map](#9-appendix--file-reference-map)

---

## 1. Executive Summary

The APGI Framework (Adaptive Predictive Gating Index) is a Python-based scientific research platform for consciousness research, neurophysiological signal processing, and falsification testing of consciousness theories. The application ships with a desktop GUI (`GUI.py` using tkinter/customtkinter), a web monitoring dashboard (Flask + Socket.IO), a CLI, and a rich suite of analysis modules.

### Overall Health: ⚠️ MODERATE RISK

The core scientific computation engine is well-structured and mathematically sound. The security subsystem (`apgi_framework/security/`) is among the project's strongest areas, featuring RestrictedPython sandboxing, a restricted unpickler, and robust input sanitization. However, the audit identified **2 critical**, **6 high**, **11 medium**, and **9 low** severity issues concentrated in the web interface layer, configuration management, and UI/UX consistency.

### Key Findings at a Glance

| Area | Finding |
|------|---------|
| 🔴 Security | XSS via unsanitized `innerHTML` injection in web_interface.py |
| 🔴 Security | Unsafe code injection in `_execute_with_subprocess` via f-string code embedding |
| 🟠 Functional | Dashboard HTML references API endpoints (`/api/experiments`, `/api/experiment/{id}`, `/api/config`) that are not implemented in the web server |
| 🟠 Config | `GUIConstants` defines `MIN_WINDOW_WIDTH` twice with conflicting values (800 vs 1600) |
| 🟠 Config | `APGIConfig.secret_key` defaults to an empty string — no secret enforced on startup |
| 🟡 UX | Optional GUI modules (tooltips, keyboard shortcuts, undo/redo, themes) silently degrade to no-ops without user notification |
| 🟡 UX | CORS wildcard (`*`) on SocketIO endpoint in `web_monitoring_dashboard.py` |
| 🟢 Strong | Security sandbox, restricted pickle loader, and input sanitization are well-implemented |
| 🟢 Strong | Comprehensive test infrastructure with hypothesis-based property testing |

---

## 2. KPI Scores

| Dimension | Score | Rating | Threshold |
|-----------|-------|--------|-----------|
| **Functional Completeness** | 62 / 100 | 🟡 Moderate | ≥80 = Pass |
| **UI/UX Consistency** | 58 / 100 | 🟡 Moderate | ≥75 = Pass |
| **Responsiveness & Performance** | 71 / 100 | 🟡 Moderate | ≥80 = Pass |
| **Error Handling & Resilience** | 68 / 100 | 🟡 Moderate | ≥80 = Pass |
| **Implementation Quality** | 70 / 100 | 🟡 Moderate | ≥80 = Pass |
| **Security Posture** | 60 / 100 | 🟠 At Risk | ≥85 = Pass |
| **Overall** | **65 / 100** | 🟠 **Needs Work** | ≥80 = Pass |

### Color Key
- 🟢 ≥80 — Passing
- 🟡 60–79 — Moderate / Needs improvement
- 🟠 40–59 — At risk / Significant gaps
- 🔴 <40 — Critical / Failing

---

## 3. Application Overview

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.8–3.12 |
| Desktop GUI | tkinter / customtkinter 5.x |
| Web Dashboard | Flask 2.3+, Flask-SocketIO 5.x |
| Scientific Computing | NumPy, SciPy, pandas, scikit-learn, statsmodels |
| Signal Processing | MNE (optional), h5py |
| Visualization | matplotlib, Plotly |
| Sandboxing | RestrictedPython |
| Build | setuptools / pyproject.toml |
| Testing | pytest, hypothesis (property-based), coverage |
| CI | GitHub Actions |
| Deployment | Docker, Kubernetes (k8s/deployment.yaml) |

### Entry Points

| Entry Point | Type | Location |
|-------------|------|----------|
| Main GUI | Desktop | `GUI.py` |
| GUI Launcher | Desktop | `GUI-Launcher.py` |
| Experiment Registry GUI | Desktop | `GUI-Experiment-Registry.py` |
| Falsification GUI | Desktop | `apps/apgi_falsification_gui.py` |
| Tests GUI | Desktop | `Tests-GUI.py` |
| Utils GUI | Desktop | `Utils-GUI.py` |
| CLI | Terminal | `apgi_framework/cli.py` |
| Batch Experiment Runner | Script | `run_experiments.py` |
| Web Dashboard | Browser | `apgi_framework/gui/web_monitoring_dashboard.py` |
| Interactive Dashboard | Browser | `apgi_framework/gui/interactive_dashboard.py` |
| Full Web Interface | Browser | `apgi_gui/components/web_interface.py` |

---

## 4. Bug Inventory

### 4.1 Critical Bugs

---

#### BUG-001 · XSS via Unsanitized `innerHTML` Injection

| Field | Detail |
|-------|--------|
| **Severity** | 🔴 Critical |
| **Category** | Security — Cross-Site Scripting (XSS) |
| **Affected File** | `apgi_gui/components/web_interface.py:399, 444–454` |
| **CWE** | CWE-79 Improper Neutralization of Input During Web Page Generation |

**Description:**
The `addLog` function at line 399 appends user-visible log messages directly into the DOM using `innerHTML` without any HTML escaping:

```javascript
// Line 399
log.innerHTML += '[' + timestamp + '] ' + message + '\\n';
```

The `message` parameter is populated from Socket.IO server-sent events (`experiment_update`, `system_status`) whose payload ultimately originates from experiment metadata provided by users. An attacker who can influence experiment names or descriptions could inject arbitrary HTML/JavaScript.

Additionally, the `displayExperiments` function at lines 444–454 constructs an HTML table by concatenating raw server-supplied `exp.name`, `exp.status`, and `exp.created_at` into `innerHTML`:

```javascript
html += '<td>' + exp.name + '</td>';   // unescaped
html += '<td>' + exp.status + '</td>'; // unescaped
```

**Reproduction Steps:**
1. Create an experiment with name: `<img src=x onerror="alert(1)">`
2. Navigate to the web interface (`/`).
3. The injected payload executes in the victim's browser.

**Expected:** Experiment names are HTML-escaped before rendering.
**Actual:** Raw strings are inserted verbatim into innerHTML.

**Remediation:**
Replace all `innerHTML` concatenation with DOM methods (`textContent`, `createElement`, `appendChild`) or use a sanitization library such as DOMPurify. At minimum, use a helper:
```javascript
function escapeHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
            .replace(/"/g,'&quot;').replace(/'/g,'&#x27;');
}
```

---

#### BUG-002 · Code Injection via Unsafe f-String Code Embedding in Subprocess Sandbox

| Field | Detail |
|-------|--------|
| **Severity** | 🔴 Critical |
| **Category** | Security — Code Injection |
| **Affected File** | `apgi_framework/security/code_sandbox.py:232–258` |
| **CWE** | CWE-94 Improper Control of Generation of Code (Code Injection) |

**Description:**
The `_execute_with_subprocess` method constructs an execution script by embedding the untrusted `code` variable directly into an f-string using triple-quote delimiters:

```python
exec_script = f"""
...
exec('''{code}''', exec_locals)
...
"""
```

An attacker can break out of the triple-quote string by supplying code that contains `'''`. For example, the following payload:

```python
code = "'''); import os; os.system('id') #"
```

This terminates the triple-quote string early, allowing arbitrary Python to execute **outside** the `exec()` call and therefore outside any sandboxing restrictions. Although the preceding AST-based `validate_code` check provides a layer of defense, the f-string embedding itself is architecturally unsafe and the AST validation operates on the **original** code string, not the constructed subprocess script.

**Reproduction Steps:**
1. Call `CodeSandbox(use_subprocess_isolation=True).execute_code("'''); import os; os.system('whoami')\n#")`
2. The `exec_script` f-string is malformed and the attacker-controlled Python runs with subprocess-level privileges.

**Expected:** User code is passed as an argument to the subprocess via a safe serialization channel (e.g., base64-encoded or written to a temp file), never embedded as a string literal.
**Actual:** User code is embedded verbatim into the subprocess script using triple-quote delimiters.

**Remediation:**
Pass the code to the subprocess via `stdin` or write it to a temporary file and pass the file path. Never embed user code as a string literal in generated code:
```python
import base64, tempfile
# Write code to temp file
with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as tf:
    tf.write(code)
# Pass temp file path as argument, not embedded code
```

---

### 4.2 High-Severity Bugs

---

#### BUG-003 · Dashboard API Endpoints Missing — Frontend/Backend Mismatch

| Field | Detail |
|-------|--------|
| **Severity** | 🟠 High |
| **Category** | Functional Completeness |
| **Affected Files** | `apgi_framework/gui/templates/dashboard.html:324–370`, `apgi_framework/gui/web_monitoring_dashboard.py:83–95` |

**Description:**
The `dashboard.html` template (used by `interactive_dashboard.py`) makes `fetch()` calls to three REST API endpoints:
- `GET /api/experiments`
- `GET /api/experiment/{experimentId}`
- `GET /api/config`

However, the `web_monitoring_dashboard.py` Flask application only registers one route: `GET /api/data`. None of the three endpoints called by the frontend are implemented. Every page load results in `404 Not Found` errors for all three API calls, rendering the dashboard non-functional.

**Expected:** Dashboard loads and displays experiment list and configuration.
**Actual:** Dashboard shows persistent loading spinners; browser console shows 404 errors for all three API calls.

**Remediation:** Implement the missing Flask routes in `web_monitoring_dashboard.py` (or the corresponding `interactive_dashboard.py`) to serve experiment data, individual experiment details, and current configuration.

---

#### BUG-004 · Conflicting `MIN_WINDOW_WIDTH` / `MIN_WINDOW_HEIGHT` Constants

| Field | Detail |
|-------|--------|
| **Severity** | 🟠 High |
| **Category** | Configuration / Functional Bug |
| **Affected File** | `apgi_framework/config/constants.py:14–52` |

**Description:**
`GUIConstants` defines `MIN_WINDOW_WIDTH` and `MIN_WINDOW_HEIGHT` twice within the same class body:

```python
# Line 14-16
MIN_WINDOW_WIDTH = 800
MIN_WINDOW_HEIGHT = 600

# Lines 51-52 (override — these take effect)
MIN_WINDOW_WIDTH = 1600
MIN_WINDOW_HEIGHT = 1000
```

Python class bodies execute sequentially, so the second definitions at lines 51–52 silently override the first. The effective values are 1600×1000, which means the GUI refuses to open on any display smaller than 1600×1000. This makes the application completely unusable on the majority of laptops (e.g., 1366×768, 1280×800).

**Expected:** Minimum window size is sensible for the target hardware (≤1280×720 recommended for research workstations).
**Actual:** GUI enforces a minimum of 1600×1000, blocking usage on common laptop screens.

**Remediation:** Remove the duplicate definitions at lines 51–52 or set `MIN_WINDOW_WIDTH = 800` / `MIN_WINDOW_HEIGHT = 600` as the final authoritative values.

---

#### BUG-005 · Flask `SECRET_KEY` Defaults to Empty String — Sessions Unsigned

| Field | Detail |
|-------|--------|
| **Severity** | 🟠 High |
| **Category** | Security — Insecure Configuration |
| **Affected File** | `apgi_framework/config/manager.py:115` |
| **CWE** | CWE-321 Use of Hard-coded Cryptographic Key |

**Description:**
`APGIConfig.secret_key` defaults to an empty string (`""`). The `ConfigurationManager._load_environment_config` reads `APGI_SECRET_KEY` from the environment but there is no enforcement that ensures the key is set before the web components start. Flask uses `SECRET_KEY` to cryptographically sign session cookies; an empty or absent key means all cookies are unsigned and can be trivially forged.

**Expected:** Application refuses to start if `APGI_SECRET_KEY` is not set in production, or auto-generates a strong ephemeral key.
**Actual:** Application starts with an empty secret key, making sessions insecure.

**Remediation:** In the config validator, add:
```python
if self.config.environment == "production" and not self.config.secret_key:
    raise ConfigurationError("APGI_SECRET_KEY must be set in production")
```
For development, auto-generate: `self.config.secret_key = secrets.token_hex(32)`.

---

#### BUG-006 · SocketIO `cors_allowed_origins="*"` — Wildcard CORS on WebSocket

| Field | Detail |
|-------|--------|
| **Severity** | 🟠 High |
| **Category** | Security — CORS Misconfiguration |
| **Affected Files** | `apgi_framework/gui/web_monitoring_dashboard.py:63`, `apgi_gui/components/web_interface.py:201` |
| **CWE** | CWE-942 Overly Permissive Cross-domain Whitelist |

**Description:**
Two separate Socket.IO servers are initialized with `cors_allowed_origins="*"`:

```python
# web_monitoring_dashboard.py:63
self.socketio = SocketIO(self.app, cors_allowed_origins="*")

# web_interface.py:201
self.socketio = SocketIO(self.app, cors_allowed_origins="*", async_mode="threading")
```

Wildcard CORS allows **any** website to establish a WebSocket connection to the server and receive real-time experiment data or send control commands. While `web_interface.py` does restrict REST CORS to the configured host, the SocketIO wildcard bypasses this restriction.

Note: `interactive_dashboard.py:86` correctly restricts to `["http://localhost:5000", "http://127.0.0.1:5000"]`.

**Expected:** SocketIO CORS restricted to known origins.
**Actual:** Any origin can connect to the WebSocket server.

**Remediation:** Change both instances to:
```python
SocketIO(self.app, cors_allowed_origins=["http://localhost:5000", "http://127.0.0.1:5000"])
```

---

#### BUG-007 · Missing CSRF Protection on State-Mutating API Endpoints

| Field | Detail |
|-------|--------|
| **Severity** | 🟠 High |
| **Category** | Security — CSRF |
| **Affected Files** | `apgi_gui/components/web_interface.py` (all POST/DELETE routes) |
| **CWE** | CWE-352 Cross-Site Request Forgery |

**Description:**
The web interface exposes state-mutating endpoints (e.g., `POST /api/experiments`, `POST /api/experiments/{id}/run`) with no CSRF token validation. There is no `flask-wtf` or equivalent CSRF protection middleware in use. Any page on the internet can trigger these endpoints via a cross-origin form submission or AJAX request.

**Expected:** All state-mutating endpoints validate a CSRF token.
**Actual:** No CSRF protection is present.

**Remediation:** Install `flask-wtf` and enable `CSRFProtect(app)`, or implement the `SameSite=Strict` cookie flag combined with a custom `X-Requested-With` header check.

---

#### BUG-008 · `apgi_gui` Package Silently Degrades — Key GUI Features Non-Functional

| Field | Detail |
|-------|--------|
| **Severity** | 🟠 High |
| **Category** | Functional Completeness |
| **Affected File** | `GUI.py:83–205` |

**Description:**
The main GUI file attempts to import four feature packages from `apgi_gui.utils`:
- `tooltip_manager` (parameter tooltips)
- `keyboard_manager` (keyboard shortcuts)
- `undo_redo_manager` (undo/redo)
- `theme_manager` (dark/light themes)

All four imports are wrapped in `try/except ImportError` blocks that silently fall back to no-op stub classes. The README lists `apgi_gui/app.py` as a valid entry point but the `apgi_gui` package is not included in the `pyproject.toml` `packages` list (`packages = ["apgi_framework", "tests"]`), making it impossible to install these modules properly.

As a result, the GUI always runs in degraded mode — tooltips never appear, keyboard shortcuts don't work, undo/redo is disabled, and theme switching silently does nothing — with **no user notification**.

**Expected:** Missing optional modules show a one-time warning; the README accurately documents what is optional vs required.
**Actual:** Features silently degrade to no-ops; `pyproject.toml` omits `apgi_gui` from installable packages.

**Remediation:** Add `apgi_gui` to `[tool.setuptools]` `packages` list in `pyproject.toml`. Display a status-bar warning when optional features are unavailable.

---

### 4.3 Medium-Severity Bugs

---

#### BUG-009 · Two Incompatible Dashboard HTML Templates

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Functional Completeness / UI Consistency |
| **Affected Files** | `apgi_framework/gui/templates/dashboard.html`, `apgi_framework/gui/web_monitoring_dashboard.py:119–340` |

**Description:**
Two completely different HTML dashboards exist for monitoring. The standalone template file (`dashboard.html`) is feature-rich (Bootstrap, SocketIO, Plotly, experiment detail modal, export, loading states), while the embedded string in `_get_dashboard_html()` is minimal (plain CSS, no Bootstrap, no Plotly charts initialized). They have different event schemas (`initial_data` vs `data_update`), different element IDs, and different functionality. Users receive different UIs depending on which class is instantiated, with no documented distinction.

**Remediation:** Consolidate to a single template. Serve it from the `templates/` directory rather than embedding HTML as a Python string.

---

#### BUG-010 · Non-Existent `configuration-display` Element ID in Dashboard JS

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Functional Bug — UI Broken |
| **Affected File** | `apgi_framework/gui/templates/dashboard.html:281–283` |

**Description:**
The dashboard JavaScript calls `showLoading('configuration-display', ...)` during initialization, but no element with ID `configuration-display` exists in the HTML. The actual configuration elements are `apgi-config` and `exp-config`. The `hideLoading` fallback also writes to `configuration-display`, which is silently ignored.

**Expected:** Loading spinner appears in the configuration section while data loads.
**Actual:** `document.getElementById('configuration-display')` returns `null`; the loading spinner is never displayed.

**Remediation:** Change line 282 to `showLoading('apgi-config', ...)` and `showLoading('exp-config', ...)`, or add an element with ID `configuration-display` as a wrapper.

---

#### BUG-011 · Overly Broad Exception Swallowing in Core Analysis Modules

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Error Handling |
| **Affected Files** | `apgi_framework/core/*.py`, `apgi_framework/analysis/*.py` |

**Description:**
Multiple locations throughout the core and analysis modules use `except Exception as e: logger.error(...); return False/None` patterns. Examples:

- `code_sandbox.py:489–516`: `_is_safe_value` returns `False` on any exception including `AttributeError` and `TypeError`, which could silently mask real errors.
- `apgi_framework/data/data_manager.py:79–82`: `start_system()` re-raises as `DataManagementError`, losing the original exception chain.
- Configuration file loading in `manager.py:197–199` re-raises but the original `Exception` is too broad.

Excessive exception swallowing prevents proper debugging and can hide security-relevant errors.

**Remediation:** Catch specific exceptions (e.g., `ValueError`, `AttributeError`) rather than bare `Exception`. Use `raise ... from e` for chained exceptions to preserve context.

---

#### BUG-012 · Ephemeral Flask `SECRET_KEY` — Sessions Break on Every Restart

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Functional Bug — Session Management |
| **Affected Files** | `apgi_framework/gui/interactive_dashboard.py:79–81`, `apgi_gui/components/web_interface.py:183–185` |

**Description:**
Both Flask servers generate a random secret key at startup:

```python
# interactive_dashboard.py:80
self.app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())

# web_interface.py:184
self.app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
```

If `FLASK_SECRET_KEY` is not set in the environment, a new random key is generated each time the server starts. Any active sessions are immediately invalidated after a server restart or process recycle.

**Expected:** Stable secret key persisted across restarts (configurable via environment variable).
**Actual:** Sessions are lost on every restart unless `FLASK_SECRET_KEY` is explicitly configured.

**Remediation:** Document `FLASK_SECRET_KEY` as required in `.env.example`. Add a startup warning if the fallback random key is being used.

---

#### BUG-013 · Incomplete Test Stubs — `TODO` Placeholders in Core Test Suite

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Test Quality |
| **Affected File** | `tests/framework/test_equation.py:16, 24, 31` |

**Description:**
Three test methods in `test_equation.py` contain only `# TODO: Add comprehensive...` comments and `assert True` — providing no actual test coverage of the `APGIEquation` core class:

```python
def test_equation_creation(self):
    assert APGIEquation is not None
    # TODO: Add comprehensive test cases for APGIEquation

def test_equation_parameters(self):
    assert hasattr(equation, "calculate_ignition_probability")
    # TODO: Add comprehensive parameter validation tests

def test_equation_calculation(self):
    assert hasattr(equation, "calculate_full_equation")
    # TODO: Add comprehensive calculation tests
```

The core equation (`APGIEquation`) is the mathematical heart of the framework, yet it has only placeholder tests.

**Remediation:** Replace stub tests with actual parameterized test cases covering happy paths, boundary conditions, and expected numerical outputs.

---

#### BUG-014 · `apgi_gui` Package Missing from `pyproject.toml` Packages List

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Build / Packaging |
| **Affected File** | `pyproject.toml:179` |

**Description:**
`[tool.setuptools]` specifies `packages = ["apgi_framework", "tests"]` but the `apgi_gui` package (which contains web interface, tooltip manager, keyboard manager, etc.) is not listed. This means `pip install -e .` will not install `apgi_gui`, and all imports from it will fail unless the repository is in `PYTHONPATH` directly. The README lists `apgi_gui/app.py` as a supported entry point.

**Remediation:** Add `"apgi_gui"` to the `packages` list, or switch to `find:` / `find_packages()` auto-discovery.

---

#### BUG-015 · `_contains_dangerous_opcodes` Uses Byte-Pattern Matching — Bypassable

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Security — Defense Bypass |
| **Affected File** | `apgi_framework/security/secure_pickle.py:161–187` |
| **CWE** | CWE-184 Incomplete List of Disallowed Inputs |

**Description:**
`SecurePickleValidator._contains_dangerous_opcodes` uses raw byte-pattern string matching to detect dangerous pickle payloads:

```python
dangerous_patterns = [b"__reduce__", b"os.", b"subprocess", ...]
for pattern in dangerous_patterns:
    if pattern in data:
```

This approach is bypassable through obfuscation. For example, pickle payloads can use global references resolved at load time rather than literal byte strings, e.g., splitting `"__reduce__"` across multiple opcodes. The docstring itself acknowledges: *"This is a simplified check - production use would need more comprehensive analysis."*

**Expected:** Pickle safety enforced exclusively through `RestrictedUnpickler.find_class()` allowlist, not byte patterns.
**Actual:** Byte-pattern scan provides a false sense of security; the `RestrictedUnpickler` is the actual gate.

**Remediation:** Remove or clearly label the byte-pattern check as `defense-in-depth only`. Ensure `RestrictedUnpickler` is always used and is the primary gate. Add a `strict_mode` check that rejects any pickle that triggers an unknown type in `find_class`.

---

#### BUG-016 · `DEBUG=true` Default in `.env.example` Could Enable Debug Mode in Production

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Security — Misconfiguration |
| **Affected File** | `.env.example:6` |
| **CWE** | CWE-215 Insertion of Sensitive Information Into Log File |

**Description:**
The provided `.env.example` contains:

```ini
APGI_DEBUG=true
APGI_LOG_LEVEL=DEBUG
```

Users who copy `.env.example` to `.env` as-is (a common quick-start pattern) will run with debug mode enabled, exposing detailed stack traces, internal state, and potentially configuration details in error responses.

**Remediation:** Change `.env.example` defaults to `APGI_DEBUG=false` and `APGI_LOG_LEVEL=INFO`. Add a comment: `# Set to true for local development only — never in production`.

---

#### BUG-017 · `loadInitialData()` References Non-Existent `configuration-display` and Missing Error Recovery

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Error Handling / UI |
| **Affected File** | `apgi_framework/gui/templates/dashboard.html:281` |

This bug compounds BUG-010. The `loadingStates.config` flag is set but `hideLoading('configuration-display', ...)` is called on the failure path with an element ID that does not exist. Users see no loading state and no error message in the configuration panel.

---

#### BUG-018 · `mypy` Strict Mode Disabled — Type Safety Not Enforced

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Implementation Quality |
| **Affected File** | `pyproject.toml:390–436` |

**Description:**
`pyproject.toml` explicitly disables mypy strict mode and incremental strictness checks:

```toml
strict = false
disallow_untyped_defs = false
check_untyped_defs = false
```

The comment acknowledges these will be "enabled in phase 2" but no milestone is documented. The result is that type errors go undetected. Several observed issues:
- `UndoRedoManager` is referenced at `GUI.py:174` using the class name from the try block but is only defined in the except block as `_UndoRedoManager`, creating a potential `NameError`.
- `_create_undo_redo_menu` at `GUI.py:174` references `UndoRedoManager` (from the try block's import) while inside the except block where it may not be defined.

**Remediation:** Enable `check_untyped_defs = true` as an intermediate step. Fix discovered type errors. Set a milestone date for Phase 2 strict mode.

---

#### BUG-019 · `BUG-019` — `utils/logging_config.py` Sets All File Handlers to `DEBUG` Level by Default

| Field | Detail |
|-------|--------|
| **Severity** | 🟡 Medium |
| **Category** | Security / Information Disclosure |
| **Affected File** | `utils/logging_config.py:287, 325` |

**Description:**
Log file handlers are configured at `DEBUG` level:

```python
level="DEBUG",
rotation="10 MB",
```

In research environments this can log sensitive parameter values, session identifiers, and internal state to disk. The `security_validator.py` provides a `sanitize_for_logging` function but it is not consistently applied before DEBUG-level log entries.

**Remediation:** Set file handler default to `INFO`. Provide an opt-in `--log-level DEBUG` flag for troubleshooting sessions only. Ensure `sanitize_for_logging` is used for all structured log entries.

---

### 4.4 Low-Severity Bugs

---

#### BUG-020 · README Documents Missing Entry Points

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `README.md:95, 135` |

README references `apgi_gui/app.py` and `apps/apgi_falsification_gui.py` as primary entry points (items 5 and 14 in the entry-point list). `apgi_gui/app.py` does not exist in the repository. `apps/apgi_falsification_gui.py` does exist. The README should be updated.

---

#### BUG-021 · `deploy.sh` Referenced in README But Not Present

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `README.md:130` |

The README documents a `deploy.sh` script (#12 in the entry-point list) but no such file exists in the repository root (only `setup.sh` is present).

---

#### BUG-022 · `APGI_SECRET_KEY` Placeholder Value in `.env.example`

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `.env.example:20` |

The placeholder `your-secret-key-here-replace-with-random-64-char-hex` is not prefixed with a `CHANGE_THIS_` marker. Users who do not read comments carefully may use the placeholder value verbatim.

---

#### BUG-023 · `apgi-test-gui` and `apgi-coverage` Scripts Map to Same Entry Point

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `pyproject.toml:172–174` |

All three CLI scripts `apgi-test`, `apgi-test-gui`, and `apgi-coverage` map to `apgi_framework.testing.main:main`. This creates confusion — users expect distinct behavior from these commands.

---

#### BUG-024 · `Dockerfile` Not Reviewed for Security Hardening

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `Dockerfile` |

The Dockerfile was not reviewed in depth. Standard checks should verify: non-root user, minimal base image, no secrets baked in, layer cache optimization, and `.dockerignore` completeness.

---

#### BUG-025 · `MAX_WINDOW_WIDTH` / `MAX_WINDOW_HEIGHT` Defined but Never Applied a Second Time

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `apgi_framework/config/constants.py:49–50` |

`MAX_WINDOW_WIDTH = 2000` and `MAX_WINDOW_HEIGHT = 1200` appear only once (lines 49–50). The duplicate MIN values at lines 51–52 (see BUG-004) suggest a copy-paste error that accidentally overrode the MIN constants instead of setting additional MAX constants.

---

#### BUG-026 · `test_generator.py` Emits `assert True` Placeholder Tests

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `apgi_framework/testing/test_generator.py:121–122` |

Auto-generated tests contain `# TODO: Add actual test cases` + `assert True`. These pass trivially and inflate test count metrics without providing coverage.

---

#### BUG-027 · Inconsistent Use of `logging` vs Custom Logger Across Modules

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Category** | Implementation Quality |

Some modules use `logging.getLogger(__name__)` directly; others use `apgi_framework.logging.centralized_logging.get_logger()` or `apgi_framework.logging.standardized_logging.get_logger()`. This fragmentation makes centralized log level control and structured logging inconsistent.

---

#### BUG-028 · `apgi_framework/testing/test_generator.py` `TODO` at Line 121

| Field | Detail |
|-------|--------|
| **Severity** | 🟢 Low |
| **Affected File** | `apgi_framework/testing/test_generator.py:121` |

Duplicate of BUG-026. The auto-generator writes `# TODO: Add actual test cases based on module functionality` followed by `assert True` into every generated test. This is both a documentation problem and a quality gap.

---

## 5. Security Vulnerability Assessment

### Summary Table

| ID | Vulnerability | Severity | OWASP / CWE | File |
|----|--------------|----------|-------------|------|
| SEC-001 | XSS via innerHTML injection | 🔴 Critical | A03:2021, CWE-79 | `web_interface.py:399,454` |
| SEC-002 | Code injection via f-string code embedding in sandbox | 🔴 Critical | A03:2021, CWE-94 | `code_sandbox.py:232` |
| SEC-003 | SocketIO CORS wildcard (`*`) | 🟠 High | A05:2021, CWE-942 | `web_monitoring_dashboard.py:63` |
| SEC-004 | No CSRF protection on POST endpoints | 🟠 High | A01:2021, CWE-352 | `web_interface.py` |
| SEC-005 | Empty default `SECRET_KEY` | 🟠 High | A02:2021, CWE-321 | `config/manager.py:115` |
| SEC-006 | Ephemeral Flask session key on restart | 🟡 Medium | A07:2021 | `interactive_dashboard.py:80` |
| SEC-007 | Bypassable pickle opcode scanning | 🟡 Medium | A08:2021, CWE-184 | `secure_pickle.py:161` |
| SEC-008 | DEBUG defaults in `.env.example` | 🟡 Medium | A05:2021, CWE-215 | `.env.example:6` |
| SEC-009 | DEBUG log files capture sensitive data | 🟡 Medium | A09:2021 | `logging_config.py:287` |

### Positive Security Controls

The following security controls are correctly implemented and represent good practices:

- ✅ **RestrictedPython sandbox** (`code_sandbox.py`) — AST validation + restricted builtins
- ✅ **RestrictedUnpickler** (`secure_pickle.py`) — allowlist-based `find_class` override
- ✅ **Input sanitization** (`input_sanitization.py`) — path traversal, filename, text, URL, JSON
- ✅ **Path traversal prevention** (`security_validator.py`) — `..` detection + allowed-dirs enforcement
- ✅ **Log sanitization** (`security_validator.py:sanitize_for_logging`) — redacts passwords, tokens, keys
- ✅ **Restricted CORS on REST API** (`web_interface.py:188–196`) — limited to configured host
- ✅ **Checksum validation for pickle files** (`secure_pickle.py:222–231`) — SHA-256 integrity check

---

## 6. Missing Features & Incomplete Implementations

| ID | Feature | Expected | Status | Effort |
|----|---------|---------|--------|--------|
| MF-001 | Web dashboard REST API (`/api/experiments`, `/api/experiment/{id}`, `/api/config`) | Functional endpoints returning JSON | ❌ Not implemented | Medium |
| MF-002 | `apgi_gui` package installation | Package installable via `pip install -e .` | ❌ Missing from `pyproject.toml` | Low |
| MF-003 | `APGIEquation` unit tests | Comprehensive test suite for core math | ❌ Placeholder stubs only | Medium |
| MF-004 | Keyboard shortcuts (GUI) | Ctrl+S, Ctrl+Z, Ctrl+Y, etc. | ⚠️ Silently disabled (module not installed) | Medium |
| MF-005 | Undo/redo (GUI) | Parameter change undo history | ⚠️ Silently disabled | Medium |
| MF-006 | Tooltip system (GUI) | Parameter hover tooltips | ⚠️ Silently disabled | Low |
| MF-007 | Theme switching (GUI) | Dark/light mode toggle | ⚠️ Silently disabled | Low |
| MF-008 | CSRF protection | All POST/DELETE endpoints protected | ❌ Not implemented | Medium |
| MF-009 | `deploy.sh` script | Documented deployment automation | ❌ File does not exist | Low |
| MF-010 | `apgi_gui/app.py` | Documented alternative GUI entry point | ❌ File does not exist | Unknown |
| MF-011 | Mypy strict mode (Phase 2) | Type-safe codebase | ⚠️ Explicitly deferred, no milestone | High |
| MF-012 | Consolidated dashboard template | Single dashboard implementation | ⚠️ Two incompatible implementations | Medium |
| MF-013 | Production startup validation | Refuse to start with unsafe config | ❌ Not enforced | Low |

---

## 7. Dimensional Audit Results

### 7.1 Functional Completeness — 62/100

**Criteria evaluated:** All documented entry points work; API contracts match frontend calls; settings persist correctly; all configuration options are honored.

**Findings:**
- The dashboard frontend makes 3 API calls; 0 of 3 are implemented (BUG-003) → **-20 points**
- `apgi_gui` package not installable → **-8 points**
- Core `APGIEquation` has no meaningful tests → **-5 points**
- 4 documented GUI features silently degrade to no-ops → **-5 points**

**Strengths:** CLI is well-implemented with proper argument validation. Batch experiment runner is functional. Scientific modules (EEG, pupillometry, cardiac) are well-structured.

---

### 7.2 UI/UX Consistency — 58/100

**Criteria evaluated:** Consistent visual design across all views; loading states managed correctly; error messages shown to users; settings inputs validated before use.

**Findings:**
- Two incompatible dashboard UIs (BUG-009) → **-12 points**
- Minimum window size 1600×1000 makes GUI unusable on most laptops (BUG-004) → **-10 points**
- Non-existent `configuration-display` element ID (BUG-010) → **-8 points**
- No user-visible warning when optional features are disabled (BUG-008) → **-7 points**
- `displayExperiments` in web_interface.py uses deprecated HTML table with inline styles → **-5 points**

**Strengths:** The `dashboard.html` template has well-implemented loading states (spinner + fallback text), a connection status badge, auto-dismissing alerts, and responsive Plotly charts.

---

### 7.3 Responsiveness & Performance — 71/100

**Criteria evaluated:** Thread safety; UI does not block on background operations; resource limits enforced; memory leak risks.

**Findings:**
- GUI operations are run in background threads via `run_in_thread` — correctly implemented
- `ExperimentMonitor` uses `threading.Lock()` for thread-safe state → correctly implemented
- `CodeSandbox` enforces CPU and memory limits via `resource.setrlimit` → correctly implemented
- No obvious memory leaks found in monitoring code (daemon threads clean up on exit)
- `apgi_framework/gui/web_monitoring_dashboard.py` uses `cors_allowed_origins="*"` which could allow unauthorized WebSocket flooding → **-10 points**
- Dashboard plot updates re-initialize full Plotly charts on every `updatePlots` call rather than using `Plotly.react` for incremental updates → **-5 points**
- `CONSOLE_MAX_LINES = 1000` cap on the log panel prevents unbounded memory growth → ✅ correctly implemented
- `GuiConstants.THREAD_POOL_SIZE = 4` is appropriately bounded → ✅

**Strengths:** Daemon thread pattern prevents process hang. Lock-protected shared state. Resource limits in sandbox. GUI uses matplotlib Agg backend to prevent threading issues.

---

### 7.4 Error Handling & Resilience — 68/100

**Criteria evaluated:** Errors communicated to users; no silent failures on critical paths; exceptions are specific; fallback behavior is documented.

**Findings:**
- Broad `except Exception` swallowing in multiple locations (BUG-011) → **-12 points**
- Dashboard JS `loadInitialData` has good try/catch with user-facing `showAlert` → ✅
- 4 optional GUI modules fail silently with no user notification → **-8 points**
- `DataManagementError` wrapping loses original exception cause in some paths → **-5 points**
- `safe_read_file` checks file existence and size before reading → ✅
- `validate_pickle_data` returns `False` rather than raising in non-strict mode → ✅ (configurable)
- `CodeSandbox.validate_code` always raises on violations → ✅

**Strengths:** Security-critical code paths (sandbox, pickle) raise on any violation. Web dashboard JS errors are surfaced to the user via alert toasts. CLI has typed argument validation with range checking.

---

### 7.5 Implementation Quality — 70/100

**Criteria evaluated:** Code organization; type annotations; test coverage; linting; documentation accuracy.

**Findings:**
- `pyproject.toml` disables mypy strict mode with no target date (BUG-018) → **-8 points**
- Three test stubs with `assert True` placeholders on core equation (BUG-013) → **-7 points**
- `apgi_gui` not in `packages` (BUG-014) → **-5 points**
- Inconsistent logger usage (standard vs custom) → **-5 points**
- README documents non-existent files → **-3 points**
- Duplicate constant definitions with conflicting values (BUG-004) → **-2 points**

**Strengths:** Scientific modules have clear docstrings and type annotations. Security modules are well-documented with rationale. `hypothesis`-based property testing provides strong coverage for data validation. `pyproject.toml` has a comprehensive optional-dependency structure.

---

## 8. Actionable Recommendations

### Priority 1 — Fix Immediately (Critical / Security)

| # | Action | Owner | Effort | Issue |
|---|--------|-------|--------|-------|
| R-01 | Replace all `innerHTML` string concatenation with DOM methods or DOMPurify; escape all user-supplied data before rendering | Frontend / Security | S (2–4h) | BUG-001 |
| R-02 | Refactor `_execute_with_subprocess` to pass code via `stdin` or temp file instead of f-string embedding | Security | M (4–8h) | BUG-002 |
| R-03 | Add CSRF protection (`flask-wtf` or SameSite cookie + header check) to all POST endpoints | Backend | M (4–8h) | BUG-007 |
| R-04 | Restrict SocketIO `cors_allowed_origins` to specific known origins in both servers | Backend | S (1h) | BUG-006 |
| R-05 | Enforce non-empty `APGI_SECRET_KEY` at startup in production; fail fast with clear error | Backend / DevOps | S (2h) | BUG-005 |

### Priority 2 — Fix Before Next Release (High)

| # | Action | Owner | Effort | Issue |
|---|--------|-------|--------|-------|
| R-06 | Remove duplicate `MIN_WINDOW_WIDTH`/`MIN_WINDOW_HEIGHT` constants; set to 1024×768 | Frontend | S (30min) | BUG-004 |
| R-07 | Implement missing REST API endpoints (`/api/experiments`, `/api/experiment/{id}`, `/api/config`) | Backend | L (1–2 days) | BUG-003 |
| R-08 | Add `apgi_gui` to `pyproject.toml` packages list; verify installable | Build | S (1h) | BUG-014 |
| R-09 | Display user-facing warning in status bar when optional GUI modules are unavailable | Frontend | S (2h) | BUG-008 |
| R-10 | Change `.env.example` debug defaults to `false`/`INFO` | DevOps | S (15min) | BUG-016 |

### Priority 3 — Improve Before Stable Release (Medium)

| # | Action | Owner | Effort | Issue |
|---|--------|-------|--------|-------|
| R-11 | Consolidate two dashboard HTML implementations into one (use `templates/dashboard.html`) | Frontend | M (1 day) | BUG-009 |
| R-12 | Fix `configuration-display` element ID mismatch in dashboard JS | Frontend | S (30min) | BUG-010 |
| R-13 | Replace `except Exception` broad handlers with specific exception types throughout | All | M (1 day) | BUG-011 |
| R-14 | Write comprehensive unit tests for `APGIEquation` (numerical correctness, boundary conditions) | QA | M (4–8h) | BUG-013 |
| R-15 | Remove byte-pattern scanning from `_contains_dangerous_opcodes` or clearly document its limited scope | Security | S (2h) | BUG-015 |
| R-16 | Enable `check_untyped_defs = true` in mypy; fix discovered errors; set Phase 2 deadline | Core | L (2–3 days) | BUG-018 |
| R-17 | Standardize logger usage (`get_logger` from `centralized_logging`) across all modules | All | M (4h) | BUG-027 |
| R-18 | Use `Plotly.react` instead of `Plotly.newPlot` for incremental dashboard chart updates | Frontend | S (2h) | §7.3 |

### Priority 4 — Nice to Have (Low)

| # | Action | Owner | Effort | Issue |
|---|--------|-------|--------|-------|
| R-19 | Update README to remove references to `apgi_gui/app.py` and `deploy.sh` | Docs | S (30min) | BUG-020, BUG-021 |
| R-20 | Create `deploy.sh` or remove the reference | DevOps | M (4h) | BUG-021 |
| R-21 | Rename `apgi-test-gui` and `apgi-coverage` CLI scripts to have distinct entry points | Build | S (1h) | BUG-023 |
| R-22 | Audit Dockerfile for non-root user, minimal base image, no secrets baked in | DevOps | M (4h) | BUG-024 |
| R-23 | Remove auto-generated `assert True` placeholder tests from test generator | QA | S (1h) | BUG-026 |
| R-24 | Add `CHANGE_THIS_` prefix to all placeholder values in `.env.example` | DevOps | S (15min) | BUG-022 |

---

## 9. Appendix — File Reference Map

| File | Role | Critical Issues |
|------|------|-----------------|
| `GUI.py` | Main desktop GUI (278KB) | BUG-008 (silent feature degradation) |
| `apgi_framework/security/code_sandbox.py` | Code sandboxing | BUG-002 (critical injection) |
| `apgi_framework/security/secure_pickle.py` | Pickle safety | BUG-015 (bypassable scan) |
| `apgi_framework/security/input_sanitization.py` | Input sanitization | ✅ Well implemented |
| `apgi_framework/security/security_validator.py` | Centralized security | ✅ Well implemented |
| `apgi_framework/gui/web_monitoring_dashboard.py` | Web monitoring UI | BUG-006 (CORS wildcard) |
| `apgi_framework/gui/interactive_dashboard.py` | Interactive web UI | BUG-012 (ephemeral key) |
| `apgi_framework/gui/templates/dashboard.html` | Dashboard HTML | BUG-003, BUG-010 |
| `apgi_gui/components/web_interface.py` | Full web interface | BUG-001 (XSS), BUG-006, BUG-007 |
| `apgi_framework/config/constants.py` | Configuration constants | BUG-004 (duplicate conflicting constants) |
| `apgi_framework/config/manager.py` | Config management | BUG-005 (empty secret key) |
| `apgi_framework/data/dashboard.py` | Experiment monitoring | ✅ Thread-safe, well implemented |
| `apgi_framework/data/data_manager.py` | Data management | BUG-011 (broad exception handling) |
| `pyproject.toml` | Build configuration | BUG-014, BUG-018, BUG-023 |
| `.env.example` | Environment template | BUG-016, BUG-022 |
| `tests/framework/test_equation.py` | Core math tests | BUG-013 (placeholder stubs) |
| `README.md` | Project documentation | BUG-020, BUG-021 |

---

*Report generated by automated audit — 2026-03-05*
*Codebase: APGI Framework (apgi-experiments) — Development Status: Beta*
