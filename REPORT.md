# APGI Framework — End-to-End Application Audit Report (Security Edition)

**Project:** APGI Framework – Advanced Platform for General Intelligence Research
**Audit Date:** 2026-02-27
**Branch Audited:** `claude/app-audit-security-h2cMm`
**Auditor:** Claude Code (Static Analysis · Dynamic Pattern Scan · Dependency Graph Review)
**Report Version:** 2.0 (supersedes v1.0 dated 2026-02-22)

---

## Executive Summary

The APGI Framework is a Python-based scientific research platform for consciousness research,
experimental paradigms, and falsification testing. It exposes a large tkinter/customtkinter
desktop GUI (`GUI.py`, `GUI-Launcher.py`, `GUI-Experiment-Registry.py`, `apgi_gui/app.py`,
`apps/apgi_falsification_gui.py`, `Tests-GUI.py`, `Utils-GUI.py`), an optional Flask web
interface (`apgi_gui/components/web_interface.py`), a CLI layer (`apgi_framework/cli.py`),
~340 Python source files, and an extensive pytest test suite.

**This edition focuses on the five mandated audit dimensions with a particular emphasis on
security.** The most pressing finding is a cluster of independent CRITICAL vulnerabilities —
hardcoded credentials committed to source control, a path-traversal file-upload endpoint with no
filename sanitisation, unsafe `pickle.load` from both database and disk, and f-string code
injection in the experiment runner — that together enable unauthenticated remote code execution
in the web interface and arbitrary command execution in the desktop GUI. These must be resolved
before any internet-facing or multi-user deployment.

**Key Metrics (this audit):**

| Metric | Value |
|--------|-------|
| Total Python files analysed | 343 |
| Syntax errors found | 0 |
| Security vulnerabilities (total) | 27 (7 Critical, 10 High, 7 Medium, 3 Low) |
| Functional bugs (total) | 24 (6 High, 10 Medium, 8 Low) |
| Statistical formula bugs | 6 |
| `NotImplementedError` stubs in production paths | 9 |
| Missing features vs README / public API | 6 |
| Unsafe `pickle` call sites (bypassing secure wrapper) | 4 |
| Hardcoded credentials / secrets | 6 |

---

## KPI Scores

| Dimension | Score | RAG | Rationale |
|-----------|:-----:|:---:|-----------|
| **Functional Completeness** | 52 / 100 | 🔴 | Core APGI math engine solid; 9 `NotImplementedError` stubs in user-facing paths; `TreatmentPredictor.predict()` always returns a hardcoded SSRI stub; `DisorderClassification.evaluate()` always returns `CONTROL`; EEG `.set` export silently writes `.csv`/`.npy` instead; batch re-fit not implemented |
| **UI / UX Consistency** | 60 / 100 | 🟡 | Consistent customtkinter styling; Find / Debug menu items crash on click; experiment description parser inverted (always shows "No description"); help dialogs incomplete; status-bar feedback inconsistent |
| **Responsiveness & Performance** | 70 / 100 | 🟡 | ThreadPoolExecutor used throughout; long-running ops off main thread; no progress cancellation in several GUI dialogs; 100 % CPU busy-wait in `PrecisionTimer.wait_until`; SQLite cache bloats with large pickled objects |
| **Error Handling & Resilience** | 50 / 100 | 🔴 | Bare `pass` in ≥14 except blocks; `assert` as runtime guard (disabled with `-O`); `ErrorRecoveryStrategy` subclass never overrides abstract methods; `data` variable potentially unbound in `load_dataset`; swallowed exceptions mask failures throughout |
| **Security** | 34 / 100 | 🔴 | 7 CRITICAL issues including hardcoded Flask secret, path-traversal upload, unsafe pickle.load, committed credentials (DB / Jupyter / Grafana), f-string code injection, and unvalidated CWD script execution |

> **RAG key:** 🟢 ≥ 80 · 🟡 60–79 · 🔴 < 60

**Overall Health Score: 53 / 100** 🔴

The framework is suitable for offline research prototyping on a trusted machine. It **must not** be deployed as a web service until the CRITICAL security issues are resolved.

---

## Section 1 — Security Vulnerability Inventory

### 1.1 Critical Vulnerabilities

---

#### SEC-01 · Hardcoded Flask Session Secret Key

| Field | Detail |
|-------|--------|
| **File** | `apgi_gui/components/web_interface.py:180` |
| **Severity** | 🔴 CRITICAL |
| **CWE** | CWE-798 Use of Hard-coded Credentials |
| **OWASP** | A07:2021 – Identification and Authentication Failures |

**Evidence:**
```python
self.app.config["SECRET_KEY"] = "apgi-framework-secret-key"
```

The static string `"apgi-framework-secret-key"` is the seed for Flask's session cookie signing. Any attacker who knows this string (it is committed to the repository) can forge arbitrary session cookies, bypass authentication, and hijack sessions.

**Contrast** with `apgi_framework/gui/interactive_dashboard.py:79-80`, which correctly uses:
```python
self.app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", os.urandom(24).hex())
```

**Fix:**
```python
import secrets
self.app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
```

---

#### SEC-02 · Path Traversal in File Upload Handler

| Field | Detail |
|-------|--------|
| **File** | `apgi_gui/components/web_interface.py:619-625` |
| **Severity** | 🔴 CRITICAL |
| **CWE** | CWE-22 Improper Limitation of a Pathname to a Restricted Directory |
| **OWASP** | A01:2021 – Broken Access Control |

**Evidence:**
```python
upload_dir = Path("uploads")
upload_dir.mkdir(exist_ok=True)
if filename:
    file_path = upload_dir / filename   # filename is raw user input
    file.save(str(file_path))
```

Only a file-extension check is applied. `filename` comes directly from `request.files["file"].filename` and is never sanitised with Werkzeug's `secure_filename()` or the project's own `InputSanitizer.sanitize_filename()` (which exists but is not called).

**Reproduction:**
```bash
curl -F "file=@evil.json;filename=../../apgi_framework/__init__.py" http://localhost:5000/api/upload
```

**Fix:**
```python
from werkzeug.utils import secure_filename
filename = secure_filename(file.filename)
if not filename:
    raise ValueError("Invalid filename")
file_path = upload_dir / filename
```

---

#### SEC-03 · Unsafe `pickle.loads` / `pickle.load` Without Validation

| Field | Detail |
|-------|--------|
| **Files** | `apgi_framework/testing/performance_optimizer.py:284` · `apgi_framework/testing/memory_efficient_runner.py:430` |
| **Severity** | 🔴 CRITICAL |
| **CWE** | CWE-502 Deserialization of Untrusted Data |
| **OWASP** | A08:2021 – Software and Data Integrity Failures |

**Evidence:**
```python
# performance_optimizer.py:284
result=pickle.loads(result_data),   # result_data is a raw BLOB from SQLite

# memory_efficient_runner.py:430
with open(checkpoint_path, "rb") as f:
    checkpoint = pickle.load(f)     # reads from disk unconditionally
```

If an attacker can write to the SQLite database or replace a checkpoint file, they can inject a malicious pickle payload that executes arbitrary code on load. The project ships a fully-functional `RestrictedUnpickler` in `apgi_framework/security/secure_pickle.py` that is **never used** at these sites.

**Fix:** Replace with `safe_pickle_load` from `apgi_framework.security.secure_pickle`.

---

#### SEC-04 · Hardcoded Credentials in `docker-compose.yml`

| Field | Detail |
|-------|--------|
| **File** | `docker-compose.yml:58, 78, 128` |
| **Severity** | 🔴 CRITICAL |
| **CWE** | CWE-798 Use of Hard-coded Credentials |

**Evidence:**
```yaml
POSTGRES_PASSWORD=apgi_password       # line 58
JUPYTER_TOKEN=apgi-dev-token          # line 78
GF_SECURITY_ADMIN_PASSWORD=admin      # line 128
```

Three separate sets of credentials are committed in plaintext. The Grafana password `admin` gives full dashboard admin access to anyone who can reach port 3000.

**Fix:** Replace with env-var references and load from a `.env` file that is never committed:
```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?err}
GF_SECURITY_ADMIN_PASSWORD: ${GF_ADMIN_PASSWORD:?err}
```

---

#### SEC-05 · Hardcoded Database Credentials in `pyproject.toml`

| Field | Detail |
|-------|--------|
| **File** | `pyproject.toml:380` |
| **Severity** | 🔴 CRITICAL |
| **CWE** | CWE-798 Use of Hard-coded Credentials |

**Evidence:**
```toml
database_url = "postgresql://test:test@localhost/test_db"
```

Even "test" credentials committed to source control normalise the practice and are typically reused or leaked through CI logs.

**Fix:** `database_url = "${DATABASE_URL}"`.

---

#### SEC-06 · Code Injection via f-string Script Generation

| Field | Detail |
|-------|--------|
| **File** | `GUI-Experiment-Registry.py:618-635, 743-761` |
| **Severity** | 🔴 CRITICAL |
| **CWE** | CWE-94 Code Injection |
| **OWASP** | A03:2021 – Injection |

**Evidence:**
```python
script_content = f"""
...
project_root = Path("{project_root}")    # path may contain " characters
result = run_experiment("{exp_name}", n_participants={params["n_participants"]}, ...)
"""
with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
    f.write(script_content)
subprocess.run([sys.executable, script_path], ...)
```

`project_root` is never sanitised. A working-directory path containing `"` would break out of the string literal. `exp_name` comes from the GUI listbox selection, and any future developer who populates the listbox from user input would introduce a trivially exploitable injection.

**Fix:** Use `json.dumps()` for all interpolated values:
```python
script_content = (
    f"project_root = Path({json.dumps(str(project_root))})\n"
    f"result = run_experiment({json.dumps(exp_name)}, ...)\n"
)
```

---

#### SEC-07 · Unvalidated `.py` Files in CWD Executed via Subprocess

| Field | Detail |
|-------|--------|
| **File** | `GUI.py:6644-6714` |
| **Severity** | 🔴 CRITICAL |
| **CWE** | CWE-426 Untrusted Search Path |

`get_python_files()` uses `os.listdir(".")` to enumerate Python files without anchoring to the project root. `execute_script()` then validates only with `os.path.exists()`, not by checking membership in a strict allowlist. Any `.py` file in the process CWD (e.g., dropped there by a malicious package or uploaded via the web interface) can be selected and executed.

**Fix:** Anchor `get_python_files()` to `Path(__file__).parent`; resolve every script path and verify it is still inside `ALLOWED_BASE_DIR` before passing to `subprocess`.

---

### 1.2 High Vulnerabilities

---

#### SEC-08 · `shell=True` with Composite String (Command Injection)

| Field | Detail |
|-------|--------|
| **File** | `utils/install_dependencies.py:62` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-78 OS Command Injection |

**Evidence:**
```python
subprocess.run(command, shell=True, ...)
# command is an f-string: f"{sys.executable} -m pip install -r {requirements_path} ..."
```

If `requirements_path` contains shell metacharacters (space, semicolon, backtick), arbitrary shell commands are executed. Flagged by Bandit B602.

**Fix:** `subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)], check=True)`

---

#### SEC-09 · Wildcard CORS — Any Origin Accepted

| Field | Detail |
|-------|--------|
| **File** | `apgi_gui/components/web_interface.py:184, 189` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-942 Permissive Cross-domain Policy |

```python
CORS(self.app)                                  # allows all origins
cors_allowed_origins="*"                        # SocketIO wildcard too
```

Combined with the hardcoded secret key (SEC-01), any malicious website the user visits can make authenticated requests to the locally-running Flask server.

**Fix:** `CORS(self.app, resources={r"/api/*": {"origins": ["http://localhost:5000"]}})`

---

#### SEC-10 · Path Traversal via Unsanitised `experiment_id` in HDF5 and Filesystem Paths

| Field | Detail |
|-------|--------|
| **File** | `apgi_framework/data/persistence_layer.py:304-311, 370-374, 423, 438, 528, 636` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-22 Path Traversal |

**Evidence:**
```python
exp_group = f.create_group(experiment_id)   # HDF5 traversal via "/" in ID
data_file = self.data_path / f"{experiment_id}.pkl"  # filesystem traversal
```

HDF5 group names containing `/` act as path separators inside the HDF5 virtual filesystem. Filesystem paths built from unsanitised `experiment_id` can escape `self.data_path`. Both read and delete operations are affected.

**Fix:** Validate `experiment_id` against `^[a-zA-Z0-9_\-]+$`; for filesystem paths additionally resolve and verify containment within `self.data_path`.

---

#### SEC-11 · Path Traversal in BIDS Export via Unsanitised `subject_id`

| Field | Detail |
|-------|--------|
| **File** | `apgi_framework/export/bids_export.py:136-141` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-22 Path Traversal |

```python
output_dir = self.bids_root / f"sub-{subject_id}"
```

`_sanitize_string` is called for BIDS *filenames* but not for directory construction. `subject_id = "../../../etc"` escapes `bids_root`.

**Fix:** Apply `_sanitize_string` to `subject_id` and verify `output_dir.resolve().is_relative_to(self.bids_root.resolve())`.

---

#### SEC-12 · Global NumPy RNG Mutation (Thread-Unsafe, Reproducibility Violation)

| Field | Detail |
|-------|--------|
| **Files** | `apgi_framework/analysis/effect_size_calculator.py:83-85` · `apgi_framework/analysis/statistical_tester.py:91` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-362 Concurrent Execution Using Shared Resource |

```python
np.random.seed(random_state)  # Mutates global RNG state for entire process
```

Destroys reproducibility for all concurrent numpy random operations (other threads, test runs). Registered as a security concern because it can corrupt statistical outputs in ways that are hard to detect.

**Fix:** `self.rng = np.random.default_rng(random_state)` and use `self.rng` exclusively.

---

#### SEC-13 · Hardcoded Python Binary (`"python"`) Instead of `sys.executable`

| Field | Detail |
|-------|--------|
| **File** | `GUI.py:6704` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-426 Untrusted Search Path |

```python
subprocess.Popen(["python", script_path], ...)
```

Resolves `python` via `PATH`, allowing PATH-based injection attacks and failing silently on systems where only `python3` is in PATH.

**Fix:** `subprocess.Popen([sys.executable, script_path], ...)`

---

#### SEC-14 · Fallback Stubs Raise `ImportError` on Instantiation in GUI-Experiment-Registry

| Field | Detail |
|-------|--------|
| **File** | `GUI-Experiment-Registry.py:63-80, 208-237` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-755 Improper Handling of Exceptional Conditions |

The fallback class definitions for `_KeyboardManager`, `_UndoRedoManager`, `_WidgetTracker`, and `_ThemeManager` raise `ImportError` in `__init__`. The guard `if "_KeyboardManager" in locals()` is always `True` (the names are module-level), so the application always attempts to instantiate the broken fallbacks, crashing `__init__` when dependencies are absent.

**Fix:** Initialize all four manager attributes to `None` in the `except ImportError` blocks.

---

#### SEC-15 · Inverted Docstring Parser — Experiment Descriptions Never Shown

| Field | Detail |
|-------|--------|
| **File** | `GUI-Experiment-Registry.py:469-485` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-670 Always-Incorrect Control Flow |

```python
in_docstring = False
in_docstring = not in_docstring   # immediately set to True before any processing
```

`in_docstring` is toggled to `True` before the loop, so the first `"""` causes an immediate break. No docstring content is ever extracted — users always see "No description available."

**Fix:** Remove the premature toggle at line 471.

---

#### SEC-16 · CI/CD Security Scans Never Fail the Pipeline

| Field | Detail |
|-------|--------|
| **File** | `utils/cicd_pipeline.py:330-348` |
| **Severity** | 🟠 HIGH |
| **CWE** | CWE-693 Protection Mechanism Failure |

```python
if result.returncode != 0:
    logger.warning("Security vulnerabilities found")
    # Don't fail pipeline for security warnings
```

Both `safety` and `bandit` scans log warnings but `_run_security_scan()` unconditionally returns `True`, meaning security scan failures **never** block deployment.

**Fix:** Return `False` on `bandit` HIGH-severity findings; configure `safety` to fail on known CVEs.

---

### 1.3 Medium Vulnerabilities

---

#### SEC-17 · Unsafe `pickle.dump` Without Checksum in `batch_processor.py`

| Field | Detail |
|-------|--------|
| **File** | `utils/batch_processor.py:350` · `apgi_framework/processing/results_processor.py:612-614` |
| **Severity** | 🟡 MEDIUM |
| **CWE** | CWE-502 Deserialization of Untrusted Data |

Raw `pickle.dump` without checksums or `safe_pickle_dump`. Files can be replaced between write and read. **Fix:** Use `safe_pickle_dump`.

---

#### SEC-18 · `assert` Used as Runtime Guard (Disabled Under `-O`)

| Field | Detail |
|-------|--------|
| **Files** | `apgi_framework/workflow_orchestrator.py:412,433,440,503,530,540` · `apgi_framework/deployment/automation.py:155` · `apgi_framework/analysis/bayesian_models.py:607` |
| **Severity** | 🟡 MEDIUM |
| **CWE** | CWE-617 Reachable Assertion |

Python's `-O` optimisation flag removes all `assert` statements. These guards protect against silent `NoneType` `AttributeError` crashes. **Fix:** Replace with `if x is None: raise RuntimeError(...)`.

---

#### SEC-19 · SMTP Without Explicit TLS Certificate Context

| Field | Detail |
|-------|--------|
| **File** | `apgi_framework/testing/notification_manager.py:596-601` |
| **Severity** | 🟡 MEDIUM |
| **CWE** | CWE-297 Improper Validation of Certificate with Host Mismatch |

`server.starttls()` without `ssl.create_default_context()` may not enforce certificate validation on all Python builds. **Fix:** `server.starttls(context=ssl.create_default_context())`.

---

#### SEC-20 · `_update_config_from_dict` Uses `setattr` Without Type Validation

| Field | Detail |
|-------|--------|
| **File** | `apgi_framework/config/manager.py:261-266` |
| **Severity** | 🟡 MEDIUM |

Config values from YAML/JSON are applied via `setattr` without type coercion. A string in a field typed as `bool` or `int` silently stores the wrong type, producing downstream errors. **Fix:** Validate and coerce types at assignment.

---

#### SEC-21 · `APGI_SECRET_KEY` Not Validated at Startup

| Field | Detail |
|-------|--------|
| **File** | `apgi_framework/config/manager.py:201-235` |
| **Severity** | 🟡 MEDIUM |

`APGI_SECRET_KEY` is not read by `_load_environment_config()`. No minimum-length check exists; the key may be empty or absent in non-development environments with no diagnostic.

---

#### SEC-22 · MD5 Used for Model Cache Key

| Field | Detail |
|-------|--------|
| **File** | `apgi_framework/analysis/bayesian_models.py:303` |
| **Severity** | 🟡 MEDIUM |
| **CWE** | CWE-327 Use of Broken Cryptographic Algorithm |

`hashlib.md5(model_code.encode()).hexdigest()` — MD5 is cryptographically broken. **Fix:** Use `hashlib.sha256`.

---

#### SEC-23 · `secure_pickle._is_valid_pickle_format` Checks Incorrect Byte Set

| Field | Detail |
|-------|--------|
| **File** | `apgi_framework/security/secure_pickle.py:153-155` |
| **Severity** | 🟡 MEDIUM |

```python
valid_protocols = {b"\x80", b"}", b")", b".", b"0", b"1", b"2"}
```

`b"}"`, `b")"`, `b"."` are individual pickle opcodes that appear mid-stream, not at the start of a valid pickle. This produces unreliable validation results. **Fix:** Use `pickletools` opcode parsing.

---

### 1.4 Low Vulnerabilities

---

#### SEC-24 · Division by Zero in `eta_squared` (Analysis Engine)

**File:** `apgi_framework/analysis/analysis_engine.py:313` — `eta_squared = between_var / total_var` when all observations are constant. **Fix:** Guard `if total_var == 0: eta_squared = 0.0`.

#### SEC-25 · Division by Zero in Cohen's d / Hedges' g

**File:** `apgi_framework/analysis/effect_size_calculator.py:112,115` — When `n1 == n2 == 1` or both groups have zero variance. **Fix:** Validate minimum group sizes and guard `pooled_std == 0`.

#### SEC-26 · Full Deserialization During Pickle Validation (DoS)

**File:** `apgi_framework/security/secure_pickle.py:423-438` — `validate_pickle_security()` fully deserializes the object during validation. A large payload consumes unbounded memory. **Fix:** Add file size cap before loading.

---

## Section 2 — Functional Bug Inventory

### Priority: High

---

#### BUG-01 · `TreatmentPredictor.predict()` Is a Stub — Always Returns Hardcoded SSRI

| File | `apgi_framework/clinical/treatment_prediction.py:47-54` |
|------|---|
| **Severity** | 🟠 HIGH |

```python
def predict(self, params: BaselineParameters) -> TreatmentPrediction:
    # Placeholder implementation
    return TreatmentPrediction(
        recommended_treatment=TreatmentType.SSRI,
        predicted_response=0.7,
        confidence=0.8,
    )
```

Every patient receives the same SSRI recommendation with a fixed 70 % response rate regardless of input parameters. No warning or error is raised.

**Fix:** Raise `NotImplementedError` with a clear message, or implement the actual treatment-matching logic.

---

#### BUG-02 · Double-Application of Variability Adjustment in `ThresholdManager`

| File | `apgi_framework/core/threshold.py:278-281` |
|------|---|
| **Severity** | 🟠 HIGH |

```python
scaled_adjustment = total_adjustment * stability_factor   # includes variability_adjustment
threshold += scaled_adjustment
# Fallback to simple variability adjustment
variability_adjustment = 0.1 * recent_variability
threshold += float(variability_adjustment)   # BUG: applied a second time
```

The variability component is added twice — once inside `total_adjustment * stability_factor` and once as a raw addition. This corrupts the threshold value on every adaptive update.

**Fix:** Remove lines 279–281.

---

#### BUG-03 · `DisorderClassification.evaluate()` Always Returns `DisorderType.CONTROL`

| File | `apgi_framework/clinical/disorder_classification.py:629` |
|------|---|
| **Severity** | 🟠 HIGH |

```python
return ClassificationResult(
    predicted_disorder=DisorderType.CONTROL,  # Placeholder
    ...
)
```

The field is hardcoded. The function correctly computes accuracy and confusion matrices but returns a wrong prediction type. **Fix:** Set `predicted_disorder` to the most common predicted class, or use a batch-evaluation result type.

---

#### BUG-04 · `NotImplementedError` in Production GUI Menu Items

| File | `apgi_gui/app.py:1224-1236` |
|------|---|
| **Severity** | 🟠 HIGH |

`find()`, `find_next()`, `find_previous()`, `toggle_debug_mode()` all raise `NotImplementedError` — visible, enabled menu items that crash on click.

**Fix:** Replace with graceful "not yet implemented" dialogs.

---

#### BUG-05 · EEG Export Writes `.csv`/`.npy` Instead of Promised `.set`

| File | `apgi_framework/export/bids_export.py:170-177` |
|------|---|
| **Severity** | 🟠 HIGH |

```python
csv_path = output_path.with_suffix(".csv")
df.to_csv(csv_path, index=False)
np.save(output_path.with_suffix(".npy"), data)
# output_path (.set) is NEVER written
```

`export_eeg_data` records the `.set` path as the canonical output, which does not exist. All subsequent reads of the returned path fail.

**Fix:** Either write a proper `.set` file using MNE-Python, or change the export format and update the path consistently.

---

#### BUG-06 · BIDS Behavioral Export Fails for Any Subject Beyond `sub-01`

| File | `apgi_framework/export/bids_export.py:280-296` |
|------|---|
| **Severity** | 🟠 HIGH |

`output_dir.mkdir()` is never called before writing behavioral data. `_create_bids_structure` only creates `sub-01/ses-01/…` directories. Writing to any other subject or session raises `FileNotFoundError`.

**Fix:** Add `output_dir.mkdir(parents=True, exist_ok=True)` before each write.

---

### Priority: Medium

---

#### BUG-07 · `ErrorRecoveryStrategy` Subclass Never Overrides Abstract Methods

| File | `apgi_framework/validation/enhanced_error_handling.py:111-117` |
|------|---|
| **Severity** | 🟡 MEDIUM |

`DataValidationRecovery(ErrorRecoveryStrategy)` inherits `can_handle()` and `recover()` which raise `NotImplementedError`. The subclass is `pass`. Any invocation of the recovery subsystem raises `NotImplementedError`.

**Fix:** Implement both methods in `DataValidationRecovery` or use `abc.ABC` / `@abstractmethod`.

---

#### BUG-08 · `ParameterEstimator.refit()` Raises After Deprecation Warning

| File | `apgi_framework/analysis/parameter_estimation.py:558-565` |
|------|---|
| **Severity** | 🟡 MEDIUM |

Issues a deprecation warning *and then* unconditionally raises `NotImplementedError`. The warning misleads callers into thinking an alternative exists. **Fix:** Remove the deprecation warning or implement the method.

---

#### BUG-09 · Thread-Unsafe Global Singletons

| Files | `apgi_framework/config/manager.py:449-451` and three others |
|-------|---|
| **Severity** | 🟡 MEDIUM |

All four global singleton factories (`ConfigurationManager`, `ActivityLogger`, `LoggingUtils`, `PathManager`) use an unprotected read-check-write pattern, enabling race conditions that create duplicate instances with divergent state.

**Fix:** Wrap with `threading.Lock()`.

---

#### BUG-10 · Incorrect Eta-squared Confidence Interval (Central vs Non-Central F)

| File | `apgi_framework/analysis/effect_size_calculator.py:449-468` |
|------|---|
| **Severity** | 🟡 MEDIUM |

`_eta_squared_ci` uses `scipy.stats.f.ppf` (central F quantiles) instead of the non-central F inversion required by the Smithson/Steiger method. Produces meaningless confidence intervals. The `omega_squared` method inherits the same wrong CI. **Fix:** Use `scipy.stats.ncf` for proper non-central F inversion.

---

#### BUG-11 · `consistency_score` Unbounded Below Zero in `ExperimentalControl`

| File | `apgi_framework/experimental_control.py:149` |
|------|---|
| **Severity** | 🟡 MEDIUM |

`consistency_score = 1.0 - (rt_std / rt_mean)` can be negative for high-variability participants, corrupting subsequent `control_score` arithmetic. **Fix:** `max(0.0, 1.0 - (rt_std / rt_mean))`.

---

#### BUG-12 · QUEST+ Expected Entropy Normalization is Mathematically Incorrect

| File | `apgi_framework/adaptive/quest_plus_staircase.py:281-285` |
|------|---|
| **Severity** | 🟡 MEDIUM |

Accumulated entropy before normalization is divided by the sum (`-entropy / p_detected_total`). Shannon entropy requires normalising the posterior distribution first, then computing `−Σ p_norm log p_norm`. The current formula is algebraically different, producing incorrect information gain estimates and therefore suboptimal stimulus selection.

---

#### BUG-13 · Welch's Degrees of Freedom Truncated to `int`

| File | `apgi_framework/analysis/statistical_tester.py:128` |
|------|---|
| **Severity** | 🟡 MEDIUM |

`degrees_of_freedom=int(df)` truncates the Welch-Satterthwaite continuous df, producing inconsistent results vs. scipy's internal calculation. **Fix:** Store as `float(df)`.

---

#### BUG-14 · `_calculate_icc` Always Returns `0.0` for Single-Value Pairs

| File | `apgi_framework/clinical/parameter_extraction.py:660-668` |
|------|---|
| **Severity** | 🟡 MEDIUM |

`self._calculate_icc([val1], [val2])` passes single-element lists; the early-exit check fires immediately, returning 0.0 for every ICC. All test-retest reliability metrics are meaningless.

---

#### BUG-15 · `AnalysisEngine.__init__` Crashes When seaborn Is Not Installed

| File | `apgi_framework/analysis/analysis_engine.py:78-79` |
|------|---|
| **Severity** | 🟡 MEDIUM |

```python
sns.set_palette("husl")   # sns is None when seaborn is absent
```

`HAS_SEABORN` is declared but never checked here. Every `AnalysisEngine` instantiation fails with `AttributeError` when seaborn is absent.

**Fix:** `if HAS_SEABORN and sns is not None: sns.set_palette("husl")`

---

#### BUG-16 · `data` Variable Potentially Unbound in `PersistenceLayer.load_dataset`

| File | `apgi_framework/data/persistence_layer.py:209-220` |
|------|---|
| **Severity** | 🟡 MEDIUM |

If `self.backend` is mutated after `__init__`, neither branch runs and `data` is referenced unbound, raising `UnboundLocalError` instead of a meaningful exception.

**Fix:** Initialize `data: Dict[str, Any] = {}` before the conditional.

---

### Priority: Low

---

#### BUG-17 · `update_config` Does Not Persist to File

`apgi_framework/config/manager.py:415-423` — In-memory only; settings lost on restart. **Fix:** Call `save_config()` or document explicitly.

#### BUG-18 · Division by Zero in `data_quality_assessment.py` for Empty DataFrame

`utils/data_quality_assessment.py:79` — `total_cells == 0`. **Fix:** Guard `if total_cells == 0`.

#### BUG-19 · Division by Zero in `data_processor.py` for Empty DataFrame

`utils/data_processor.py:400` — `len(data) == 0`. **Fix:** Guard with `len(data) or 1`.

#### BUG-20 · Subprocess Process Leak on Timeout in Experiment Registry

`GUI-Experiment-Registry.py:645-650` — `TimeoutExpired` is not caught; the child process is never killed. **Fix:** Catch `subprocess.TimeoutExpired` and call `process.kill()`.

#### BUG-21 · 100% CPU Busy-Wait in `PrecisionTimer.wait_until`

`apgi_framework/adaptive/task_control.py:185` — `while time.perf_counter() < target: pass` pegs CPU. **Fix:** Hybrid sleep + busy-wait for the final millisecond.

#### BUG-22 · Two-Group Bootstrap Uses Identical Indices for Independent Samples

`apgi_framework/analysis/effect_size_calculator.py:364-377` — Both arrays resampled with the same index set, preserving phantom paired structure. **Fix:** Use independent `np.random.choice` calls per array.

#### BUG-23 · `validate_against_criterion` Returns Fake Correlations

`apgi_framework/clinical/parameter_extraction.py:826-845` — Ignores `criterion_measures` input; returns a fixed linear transform of parameter values presented as empirical Pearson correlations.

#### BUG-24 · `Optional[str]` Annotation Missing Across All 13 Exception Classes

`apgi_framework/exceptions.py:34+` — `operation: str = None` is a type error; should be `Optional[str] = None`. Affects `MathematicalError` and 12 sibling classes.

---

## Section 3 — Missing Features Log

| ID | Feature | Specification Reference | Status | Severity |
|----|---------|------------------------|--------|----------|
| MF-01 | **Find / Find Next / Find Previous** | README §2 "GUI Applications"; `apgi_gui/app.py` menu structure | `NotImplementedError` at runtime | 🟠 HIGH |
| MF-02 | **Debug Mode** toggle | `apgi_gui/app.py:1236` | `NotImplementedError` at runtime | 🟠 HIGH |
| MF-03 | **`ParameterEstimator.refit()`** | Public API docstring; documented workflow | Not implemented; raises | 🟠 HIGH |
| MF-04 | **`TreatmentPredictor` real predictions** | `clinical/treatment_prediction.py` public API | Hardcoded stub returns SSRI always | 🟠 HIGH |
| MF-05 | **EEG BIDS `.set` export** | BIDS EEG specification; `export/bids_export.py` signature | `.csv`/`.npy` written, `.set` never created | 🟠 HIGH |
| MF-06 | **Error Recovery strategy implementations** | `enhanced_error_handling.py` architecture | Stub — `DataValidationRecovery` never overrides base | 🟡 MEDIUM |

---

## Section 4 — UI/UX Consistency Findings

| ID | Location | Issue | Severity |
|----|----------|-------|----------|
| UI-01 | `apgi_gui/app.py` Edit/Debug menu | Menu items visible and enabled but crash on click with `NotImplementedError` | 🟠 HIGH |
| UI-02 | `GUI-Experiment-Registry.py:469-485` | Docstring parser inverted; all experiments show "No description available" | 🟠 HIGH |
| UI-03 | `GUI.py:6704` | Hardcoded `"python"` binary silently fails on Linux where `python3` is the only interpreter | 🟠 HIGH |
| UI-04 | `GUI-Experiment-Registry.py` | No progress indicator during 5-minute experiment timeout; user sees frozen UI | 🟡 MEDIUM |
| UI-05 | Multiple `except Exception: pass` | Errors swallowed silently; no user feedback on failure | 🟡 MEDIUM |
| UI-06 | `apgi_gui/components/web_interface.py` | File upload JSON response includes full server-side `path` — information disclosure | 🟡 MEDIUM |
| UI-07 | `apgi_framework/core/equation.py:124-133` | Surprise clamped silently to [0,10] at DEBUG log level; misleads callers with large prediction errors | 🟢 LOW |

---

## Section 5 — Performance & Responsiveness Findings

| ID | Location | Issue | Severity |
|----|----------|-------|----------|
| PERF-01 | `GUI-Experiment-Registry.py` | No cancellation mechanism for running experiments; hung subprocess blocks until 300 s timeout | 🟡 MEDIUM |
| PERF-02 | `apgi_framework/testing/performance_optimizer.py` | SQLite cache stores full `pickle.dumps()` blob per result entry; large objects bloat the DB | 🟡 MEDIUM |
| PERF-03 | `apgi_framework/adaptive/task_control.py:185` | 100% CPU busy-wait for entire timing wait; causes thermal throttling in long sessions | 🟡 MEDIUM |
| PERF-04 | `apgi_framework/analysis/analysis_engine.py:329` | ANOVA loop spawns `min(group_cols, 4)` threads; GIL contention for DataFrames with many columns | 🟢 LOW |
| PERF-05 | `docker-compose.yml` | Full source tree mounted as volume (`.:/app`); all container writes hit host filesystem | 🟢 LOW |

---

## Section 6 — Error Handling & Resilience Findings

| ID | Location | Issue | Severity |
|----|----------|-------|----------|
| EH-01 | `apgi_framework/validation/enhanced_error_handling.py` | Recovery strategy base raises `NotImplementedError`; subclass never overrides → recovery always fails | 🟠 HIGH |
| EH-02 | `apgi_framework/data/persistence_layer.py:209-220` | `data` variable unbound if backend attribute mutated after init | 🟡 MEDIUM |
| EH-03 | `apgi_framework/workflow_orchestrator.py` et al. | `assert` guards disabled under `-O` → silent `AttributeError` in production | 🟡 MEDIUM |
| EH-04 | `utils/gui-simple-experiment-runner.py` | 14+ bare `pass` exception blocks hide all errors | 🟡 MEDIUM |
| EH-05 | `run_tests.py:349,669` | `except Exception: pass` swallows test-runner errors; output appears empty | 🟡 MEDIUM |
| EH-06 | `GUI.py:996-998, 1012-1014` | Bare `except Exception: pass` in two critical GUI init paths | 🟡 MEDIUM |
| EH-07 | `apgi_framework/config/manager.py` | `update_config()` broad `except Exception` re-raises but does not restore previous state | 🟢 LOW |

---

## Section 7 — Prioritised Remediation Roadmap

### Sprint 1 — Immediate (Before Any Web Deployment)

| # | Issue | File | Effort |
|---|-------|------|--------|
| 1 | SEC-04 — Rotate & move docker-compose credentials to `.env` | `docker-compose.yml` | S |
| 2 | SEC-05 — Remove hardcoded DB URL from pyproject.toml | `pyproject.toml` | XS |
| 3 | SEC-01 — Randomise Flask SECRET_KEY from env var | `web_interface.py:180` | XS |
| 4 | SEC-02 — Sanitise upload filename with `secure_filename()` | `web_interface.py:624` | XS |
| 5 | SEC-03 — Replace unsafe `pickle.load` with `safe_pickle_load` | 2 call sites | S |
| 6 | SEC-09 — Restrict CORS to `localhost` | `web_interface.py:184` | XS |
| 7 | SEC-08 — Replace `shell=True` with list-form subprocess | `install_dependencies.py:62` | XS |
| 8 | SEC-06 — Fix f-string code injection (use `json.dumps`) | `GUI-Experiment-Registry.py` | S |
| 9 | SEC-07 — Anchor script execution to project root allowlist | `GUI.py:6644` | S |

### Sprint 2 — High Priority (Before Beta Release)

| # | Issue | File | Effort |
|---|-------|------|--------|
| 10 | BUG-01 — Add real logic to `TreatmentPredictor.predict()` | `treatment_prediction.py:47` | L |
| 11 | BUG-02 — Remove duplicate variability adjustment | `threshold.py:278-281` | XS |
| 12 | BUG-03 — Fix `DisorderClassification.evaluate()` return field | `disorder_classification.py:629` | S |
| 13 | BUG-04 — Replace `NotImplementedError` menu raises with dialogs | `apgi_gui/app.py:1224-1236` | S |
| 14 | BUG-05 — Fix EEG `.set` export (write file or change format) | `bids_export.py:170-177` | M |
| 15 | BUG-06 — Add `mkdir(parents=True)` to BIDS behavioral export | `bids_export.py:280-296` | XS |
| 16 | SEC-13 — Replace `"python"` with `sys.executable` | `GUI.py:6704` | XS |
| 17 | SEC-15 — Fix inverted docstring parser | `GUI-Experiment-Registry.py:471` | XS |
| 18 | SEC-16 — Fail CI pipeline on security scan findings | `cicd_pipeline.py:330-348` | S |
| 19 | SEC-14 — Fix broken fallback stubs in Registry GUI | `GUI-Experiment-Registry.py:208-237` | S |
| 20 | BUG-09 — Add `threading.Lock()` to global singleton factories | 4 modules | S |
| 21 | SEC-18 — Convert `assert` guards to `if`/`raise RuntimeError` | `workflow_orchestrator.py` et al. | S |

### Sprint 3 — Medium Priority

| # | Issue | File | Effort |
|---|-------|------|--------|
| 22 | SEC-10/11 — Validate `experiment_id`/`subject_id` for path traversal | `persistence_layer.py` · `bids_export.py` | S |
| 23 | BUG-10 — Fix eta-squared CI (use non-central F) | `effect_size_calculator.py:449` | M |
| 24 | BUG-12 — Fix QUEST+ entropy normalization | `quest_plus_staircase.py:281` | S |
| 25 | BUG-15 — Guard `sns.set_palette` behind `HAS_SEABORN` | `analysis_engine.py:79` | XS |
| 26 | BUG-11 — Clamp `consistency_score` to [0,1] | `experimental_control.py:149` | XS |
| 27 | SEC-17 — Replace raw pickle.dump with `safe_pickle_dump` | `batch_processor.py`, `results_processor.py` | S |
| 28 | SEC-19 — Add explicit SSL context to SMTP | `notification_manager.py:596` | XS |
| 29 | SEC-22 — Replace MD5 cache key with SHA-256 | `bayesian_models.py:303` | XS |
| 30 | BUG-07 — Implement `DataValidationRecovery` methods | `enhanced_error_handling.py` | M |
| 31 | UI-06 — Remove server path from upload JSON response | `web_interface.py:633` | XS |
| 32 | EH-04/05/06 — Add logging to bare-pass exception handlers | multiple files | S |

### Sprint 4 — Hardening

| # | Issue | Effort |
|---|-------|--------|
| 33 | BUG-17 — Auto-persist config on `update_config()` | XS |
| 34 | BUG-18/19 — Division-by-zero guards in data utils | XS |
| 35 | BUG-20 — Kill subprocess on timeout | XS |
| 36 | BUG-21 — Hybrid sleep + busy-wait in `PrecisionTimer` | S |
| 37 | BUG-22 — Independent bootstrap resampling per group | XS |
| 38 | BUG-24 — Fix `str = None` type annotation in all 13 exception classes | XS |
| 39 | LOW-07 — Enable mypy strict mode incrementally in `pyproject.toml` | M |

> **Effort key:** XS < 1 h · S < 1 day · M < 1 week · L > 1 week

---

## Appendix A — All Security Findings (Summary Table)

| ID | File | Line | Severity | Category | Title |
|----|------|------|----------|----------|-------|
| SEC-01 | `apgi_gui/components/web_interface.py` | 180 | 🔴 CRITICAL | Auth | Hardcoded Flask secret key |
| SEC-02 | `apgi_gui/components/web_interface.py` | 619-625 | 🔴 CRITICAL | Injection | Path traversal in file upload |
| SEC-03 | `performance_optimizer.py` / `memory_efficient_runner.py` | 284 / 430 | 🔴 CRITICAL | Deserialisation | Unsafe `pickle.load` |
| SEC-04 | `docker-compose.yml` | 58, 78, 128 | 🔴 CRITICAL | Auth | Hardcoded infra credentials |
| SEC-05 | `pyproject.toml` | 380 | 🔴 CRITICAL | Auth | Hardcoded DB URL with credentials |
| SEC-06 | `GUI-Experiment-Registry.py` | 618-635 | 🔴 CRITICAL | Injection | f-string code injection |
| SEC-07 | `GUI.py` | 6644-6714 | 🔴 CRITICAL | Execution | Unvalidated CWD scripts executed |
| SEC-08 | `utils/install_dependencies.py` | 62 | 🟠 HIGH | Injection | `shell=True` command injection |
| SEC-09 | `apgi_gui/components/web_interface.py` | 184, 189 | 🟠 HIGH | Config | Wildcard CORS |
| SEC-10 | `apgi_framework/data/persistence_layer.py` | 304, 423 | 🟠 HIGH | Injection | Path traversal via `experiment_id` |
| SEC-11 | `apgi_framework/export/bids_export.py` | 136-141 | 🟠 HIGH | Injection | Path traversal via `subject_id` |
| SEC-12 | `effect_size_calculator.py` / `statistical_tester.py` | 85 / 91 | 🟠 HIGH | Concurrency | Global NumPy RNG mutation |
| SEC-13 | `GUI.py` | 6704 | 🟠 HIGH | Path | Hardcoded `"python"` binary |
| SEC-14 | `GUI-Experiment-Registry.py` | 208-237 | 🟠 HIGH | Logic | Broken fallback stubs crash `__init__` |
| SEC-15 | `GUI-Experiment-Registry.py` | 471 | 🟠 HIGH | Logic | Inverted docstring parser |
| SEC-16 | `utils/cicd_pipeline.py` | 330-348 | 🟠 HIGH | Config | Security scans never fail pipeline |
| SEC-17 | `batch_processor.py` / `results_processor.py` | 350 / 613 | 🟡 MEDIUM | Deserialisation | Unsafe `pickle.dump` (no checksum) |
| SEC-18 | `workflow_orchestrator.py` et al. | Various | 🟡 MEDIUM | Logic | `assert` as runtime guard |
| SEC-19 | `notification_manager.py` | 596-601 | 🟡 MEDIUM | Crypto | SMTP without explicit TLS context |
| SEC-20 | `apgi_framework/config/manager.py` | 261-266 | 🟡 MEDIUM | Validation | `setattr` without type validation |
| SEC-21 | `apgi_framework/config/manager.py` | 201-235 | 🟡 MEDIUM | Auth | `APGI_SECRET_KEY` not validated |
| SEC-22 | `apgi_framework/analysis/bayesian_models.py` | 303 | 🟡 MEDIUM | Crypto | MD5 for cache key |
| SEC-23 | `apgi_framework/security/secure_pickle.py` | 153-155 | 🟡 MEDIUM | Validation | Incorrect pickle format byte check |
| SEC-24 | `apgi_framework/analysis/analysis_engine.py` | 313 | 🟢 LOW | Math | `eta_squared` division by zero |
| SEC-25 | `apgi_framework/analysis/effect_size_calculator.py` | 112, 115 | 🟢 LOW | Math | Cohen's d / Hedges' g division by zero |
| SEC-26 | `apgi_framework/security/secure_pickle.py` | 423-438 | 🟢 LOW | DoS | Full deserialisation during validation |

---

## Appendix B — All Bugs (Summary Table)

| ID | File | Line | Severity | Category | Title |
|----|------|------|----------|----------|-------|
| BUG-01 | `clinical/treatment_prediction.py` | 47 | 🟠 HIGH | Incomplete | `predict()` always returns hardcoded SSRI |
| BUG-02 | `core/threshold.py` | 278 | 🟠 HIGH | Logic | Variability adjustment applied twice |
| BUG-03 | `clinical/disorder_classification.py` | 629 | 🟠 HIGH | Incomplete | `evaluate()` always returns `CONTROL` |
| BUG-04 | `apgi_gui/app.py` | 1224-1236 | 🟠 HIGH | Incomplete | 4 menu items raise `NotImplementedError` |
| BUG-05 | `export/bids_export.py` | 170-177 | 🟠 HIGH | Logic | `.set` file never written |
| BUG-06 | `export/bids_export.py` | 280-296 | 🟠 HIGH | Bug | Missing `mkdir` for new subjects |
| BUG-07 | `validation/enhanced_error_handling.py` | 111-117 | 🟡 MEDIUM | Incomplete | Recovery subclass never overrides methods |
| BUG-08 | `analysis/parameter_estimation.py` | 558-565 | 🟡 MEDIUM | Incomplete | `refit()` raises after deprecation warning |
| BUG-09 | `config/manager.py` et al. | 449 | 🟡 MEDIUM | Concurrency | Thread-unsafe global singletons |
| BUG-10 | `analysis/effect_size_calculator.py` | 449-468 | 🟡 MEDIUM | Statistics | Central F used for eta-squared CI |
| BUG-11 | `experimental_control.py` | 149 | 🟡 MEDIUM | Math | `consistency_score` unbounded below 0 |
| BUG-12 | `adaptive/quest_plus_staircase.py` | 281-285 | 🟡 MEDIUM | Statistics | Incorrect entropy normalization |
| BUG-13 | `analysis/statistical_tester.py` | 128 | 🟡 MEDIUM | Statistics | Welch's df truncated to `int` |
| BUG-14 | `clinical/parameter_extraction.py` | 660 | 🟡 MEDIUM | Statistics | ICC always returns 0.0 |
| BUG-15 | `analysis/analysis_engine.py` | 78-79 | 🟡 MEDIUM | Crash | `sns.set_palette()` when seaborn absent |
| BUG-16 | `data/persistence_layer.py` | 209-220 | 🟡 MEDIUM | Logic | `data` potentially unbound |
| BUG-17 | `config/manager.py` | 415-423 | 🟢 LOW | UX | Config not persisted after update |
| BUG-18 | `utils/data_quality_assessment.py` | 79 | 🟢 LOW | Math | Division by zero on empty DataFrame |
| BUG-19 | `utils/data_processor.py` | 400 | 🟢 LOW | Math | Division by zero on empty DataFrame |
| BUG-20 | `GUI-Experiment-Registry.py` | 645-650 | 🟢 LOW | Resource | Process not killed on timeout |
| BUG-21 | `adaptive/task_control.py` | 185 | 🟢 LOW | Performance | 100% CPU busy-wait loop |
| BUG-22 | `analysis/effect_size_calculator.py` | 364-377 | 🟢 LOW | Statistics | Shared indices for independent bootstrap |
| BUG-23 | `clinical/parameter_extraction.py` | 826-845 | 🟢 LOW | Statistics | `validate_against_criterion` ignores input data |
| BUG-24 | `apgi_framework/exceptions.py` | 34+ | 🟢 LOW | Types | `str = None` annotation error (13 classes) |

---

## Appendix C — Files Audited in This Cycle

Core framework, security modules, GUI files, analysis engine, clinical modules, adaptive modules,
export layer, deployment utilities, configuration, docker/CI configuration. 343 Python files
checked for syntax errors (0 found). All files listed in the README "Entry Points" section and
"Utils Scripts" section reviewed.

---

*Report generated by Claude Code automated static analysis — 2026-02-27*
*Supersedes previous audit report v1.0 (2026-02-22, branch `claude/app-audit-testing-onxEE`)*
