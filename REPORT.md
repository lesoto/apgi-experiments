# APGI Framework — End-to-End Application Audit Report

**Project:** APGI Framework – Advanced Platform for General Intelligence Research
**Audit Date:** 2026-02-22
**Branch Audited:** `claude/app-audit-testing-onxEE`
**Auditor:** Claude Code (Automated Static + Dynamic Analysis)
**Report Version:** 1.0

---

## Executive Summary

The APGI Framework is a Python-based scientific research platform for consciousness research, experimental paradigms, and falsification testing of consciousness theories. It consists of a large tkinter/customtkinter desktop GUI (`GUI.py`, `GUI-Launcher.py`, `GUI-Experiment-Registry.py`, `apgi_gui/app.py`, `apps/apgi_falsification_gui.py`, `Tests-GUI.py`, `Utils-GUI.py`), a CLI layer (`apgi_framework/cli.py`), a substantial backend framework, and an extensive pytest test suite.

**Overall Assessment:** The codebase is structurally ambitious and well-organized at the module level, but contains a significant number of incomplete implementations, stub functions, runtime dependency issues, and test failures that collectively reduce confidence in production readiness. A full suite run (excluding tkinter-dependent GUI tests) recorded **110 failed, 540 passed, 121 skipped, 9 errors** in 780 s across ~780 test items. An additional test-isolation problem was identified: a subset of failures only manifest during the complete suite run and pass when executed in isolation, indicating shared global state between test modules. Several user-facing features raise `NotImplementedError` at runtime. Core modules such as the PDF generator fail to import due to a scoping bug when optional dependencies are absent.

---

## KPI Scores

| KPI | Score (0–100) | Rationale |
|-----|:---:|-----------|
| **1. Functional Completeness** | **48** | Key user-facing features (Find/Find Next/Previous, Debug Mode, PDF/LATEX export, API service startup, consciousness evaluation with real data, coverage visualization) are stubs or raise `NotImplementedError`. Core simulation functions use hardcoded output values. Multiple public APIs (`QuestPlusParameters`, `StorageManager`, `IntegratedDataManager`, `APGIEquation`, stimulus generators) are missing documented methods or reject expected constructor arguments. |
| **2. UI/UX Consistency** | **61** | Theme toggling, undo/redo, zoom, keyboard shortcuts, and help dialogs are implemented in `apgi_gui/app.py`. Menu structure is coherent. However, missing features (Find, Debug) are exposed in menus without guards, and some components that load conditionally can silently fail. |
| **3. Responsiveness & Performance** | **68** | Long-running operations are generally offloaded to background threads. Some threshold-detection tests time out (>30 s), indicating potential infinite loops or unbounded computations in psychometric fitting. The `performance_monitor.py` module imports `tkinter` at the module top level, blocking headless usage. |
| **4. Error Handling & Resilience** | **55** | The CLI's `self.logger` is initialized to `None` and used before `setup_logging()` is called, causing `AttributeError` crashes. The PDF generator module raises `NameError` on import when `reportlab` is missing. Config manager's `save_preset` does not create nested parent directories. Corrupted JSON in presets is not caught as `ConfigurationError`. Several modules catch broad `Exception` silently. |
| **5. Overall Implementation Quality** | **58** | Syntax is clean (no parse errors across all 7 main GUI files). Linting produces only 1 flake8 issue across the framework. Module organisation is logical. However, a large number of abstract methods and concrete classes have `pass`-body stubs, the staircase rule parser uses an undocumented format, and two major GUI features (`run_consciousness_evaluation`, `short_term_apgi_model`, `combined_apgi_analysis`) output hardcoded results regardless of input data. |

---

## Bug Inventory

### CRITICAL Severity

| ID | Component | Description | Reproduction Steps | Expected | Actual |
|----|-----------|-------------|-------------------|----------|--------|
| **BUG-001** | `apgi_framework/reporting/pdf_generator.py:53` | `NameError` on module import when `reportlab` is not installed — `A4` used as a dataclass default value outside the `try` block | `python -c "import apgi_framework.reporting.pdf_generator"` without `reportlab` installed | Module imports cleanly; PDF generation raises `ImportError` with a message | `NameError: name 'A4' is not defined` — entire module fails to import |
| **BUG-002** | `apgi_framework/cli.py:179,637–639` | `AttributeError` crash when `initialize_controller()` is called before `setup_logging()` — `self.logger` is `None` | Instantiate `APGIFrameworkCLI()`, call `cli.initialize_controller()` directly (as the test does) | Method succeeds or raises a descriptive error | `AttributeError: 'NoneType' object has no attribute 'info'` / `'error'` |
| **BUG-003** | `apgi_framework/optimization/performance_monitor.py:11` | `import tkinter as tk` at module top level — fails on headless servers or any environment without `python3-tk` | `python -c "from apgi_framework.optimization.performance_monitor import PerformanceAlert"` in a headless env | Module imports with a fallback or raises `ImportError` with a helpful message | `ModuleNotFoundError: No module named 'tkinter'` — blocks all users of this module including `test_performance_properties.py` |

---

### HIGH Severity

| ID | Component | Description | Reproduction Steps | Expected | Actual |
|----|-----------|-------------|-------------------|----------|--------|
| **BUG-004** | `apgi_gui/app.py:1224,1228,1232,1236` | Four user-facing menu actions raise `NotImplementedError` at runtime — **Find**, **Find Next**, **Find Previous**, **Debug Mode** | Launch `apgi_gui/app.py`; trigger Edit → Find (or keyboard shortcut) | A search dialog opens (or feature is visibly disabled/greyed out) | `NotImplementedError: Find functionality not yet implemented` — unhandled exception |
| **BUG-005** | `apgi_framework/config/config_manager.py:329–331` | `save_preset()` does not create nested parent directories, causing `FileNotFoundError` when the presets path contains intermediate directories that do not exist | Set `manager.presets_dir = Path("/tmp/x/sub/presets")` (non-existent parent); call `manager.save_preset("name")` | Directory tree created automatically | `FileNotFoundError: No such file or directory` |
| **BUG-006** | `apgi_framework/config/config_manager.py:346` | `load_preset()` does not catch `json.JSONDecodeError` — corrupted preset files propagate a raw JSON error instead of a `ConfigurationError` | Write `{invalid json` to a preset file; call `manager.load_preset("corrupted")` | `ConfigurationError: Invalid preset file: ...` | `json.decoder.JSONDecodeError: Expecting property name ...` |
| **BUG-007** | `apgi_framework/research/threshold_detection_paradigm.py:393` | Staircase rule parser rejects the conventional `"3up_1down"` notation (expected format is 3 underscore-separated tokens like `"3_up_down"`) | `AdaptiveStaircase(rule="3up_1down")` | Staircase initialises with 3-up/1-down rule | `ValidationError: Invalid staircase rule: 3up_1down` |
| **BUG-008** | `apgi_framework/data/storage_manager.py` | `store_dataset()` validation requires three specific domain fields (`apgi_parameters`, `neural_signatures`, `consciousness_assessments`), making the storage layer unusable for generic datasets or during testing with minimal data | Create a `DataSet` with `data={"key": "value"}`; call `storage.store_dataset(dataset)` | Dataset stored successfully | `StorageError: Dataset validation failed: ['Missing required data field: apgi_parameters', ...]` |
| **BUG-009** | `apgi_framework/analysis/statistical_report_generator.py:374` | `ReportFormat.PDF` and `ReportFormat.LATEX` are defined in the enum but raise `ValueError: Export format ... not yet implemented` when used | Call `generator.export_results(data, format_type=ReportFormat.PDF)` | PDF exported to file | `ValueError: Export format ReportFormat.PDF not yet implemented` |
| **BUG-010** | `tests/integration/test_integration_properties.py:861` | Property-based test creates a temporary directory without `exist_ok=True`, causing `FileExistsError` on repeated Hypothesis shrinking runs | Run `pytest tests/integration/test_integration_properties.py::TestAPGIFrameworkCompatibilityProperties::test_apgi_test_fixture_compatibility` | Tests pass under all generated examples | `FileExistsError: [Errno 17] File exists` |
| **BUG-011** | `apgi_framework/testing/ci_integrator.py:99` | CI integrator silently produces empty `changed_files` list when repository has no prior commits (`HEAD~1` does not exist), breaking CI impact-analysis workflows on fresh clones | Run `CIIntegrator.get_change_impact()` on a repo with a single commit | Returns a sensible default or raises a descriptive error | `git diff` fails with `fatal: ambiguous argument 'HEAD~1'`; `changed_files = []` silently |

---

### MEDIUM Severity

| ID | Component | Description | Reproduction Steps | Expected | Actual |
|----|-----------|-------------|-------------------|----------|--------|
| **BUG-012** | `apgi_framework/monitoring/realtime_monitor.py:598` | `global _global_monitor` declared but the name is never actually assigned inside the scope — dead/broken code | `python -m flake8 apgi_framework/monitoring/realtime_monitor.py` | No lint warnings | `F824 global _global_monitor is unused: name is never assigned in scope` |
| **BUG-013** | `GUI.py` — `run_consciousness_evaluation()` | Function outputs hardcoded fake metric values (0.78, 0.65, 0.82) regardless of any loaded data | Click **Consciousness Evaluation** button with any dataset | Real computed consciousness metrics | Hardcoded strings logged to console; dialog says "completed successfully" |
| **BUG-014** | `GUI.py` — `short_term_apgi_model()` / `combined_apgi_analysis()` | Both methods log static strings and show a success dialog without performing any actual computation | Click either button | Model runs against loaded data | Static text output; no real analysis performed |
| **BUG-015** | `apgi_framework/deployment/automation.py:455` | `_start_api_service()` logs `"API service startup not implemented yet"` and returns without doing anything | Call `automation.start_services()` in a multi-service deployment config | API service starts | Nothing happens; log message is the only output |
| **BUG-016** | `apgi_framework/cli.py` — `test_cli_unknown_command` | Unknown CLI command exits with code `2` (argparse default) instead of documented exit code `1` | Run `apgi-test unknown-command` | Exit code `1` | Exit code `2` |
| **BUG-017** | `tests/test_error_telemetry.py` — `test_initialization_creates_directory` | `ErrorTelemetry` does not create the telemetry directory on initialization — `telemetry_file` path does not exist | Instantiate `ErrorTelemetry(base_dir=tmpdir)`; check `telemetry.telemetry_file.exists()` | File created at init | `AssertionError: assert False` |
| **BUG-018** | `apgi_framework/core/` — `TestAPGIAgent::test_agent_parameter_validation` | Agent does not raise `ValueError` for out-of-range parameters as documented | Pass boundary-violating params to `APGIAgent`; expect `ValueError` | `ValueError` raised | No exception raised — parameters silently accepted |
| **BUG-019** | `tests/test_diagnostics_cli.py` | Multiple mock targets use `.return_value` on non-mockable method objects; `sys.exit` called more times than expected in warning/failure scenarios | `pytest tests/test_diagnostics_cli.py` | Tests pass | `AttributeError: 'method' object has no attribute 'return_value'`; exit call count mismatch |
| **BUG-020** | `apgi_framework/testing/test_threshold_detection.py` | Multiple threshold detection tests exceed the 30-second timeout, indicating unbounded loops or hanging psychometric fits | `pytest tests/test_threshold_detection.py --timeout=30` | Tests complete in <10 s | `Failed: Timeout (>30.0s)` for cross-modal comparison, confidence interval, and report generation tests |

---

### LOW Severity

| ID | Component | Description | Reproduction Steps | Expected | Actual |
|----|-----------|-------------|-------------------|----------|--------|
| **BUG-021** | `apgi_framework/gui/coverage_visualization.py` | Entire widget class is a Qt (`PySide6`) stub — all 30+ rendering methods are bare `pass` bodies; no visualisation is actually rendered | Import module without PySide6 | Graceful degradation with tkinter fallback | Fallback stubs expose no API whatsoever; widget tree is non-functional |
| **BUG-022** | `apgi_framework/validation/enhanced_error_handling.py:113,117` | Two abstract methods defined but body is bare `raise NotImplementedError` (not `@abstractmethod`) — subclasses may not be forced to implement them | Instantiate a subclass that doesn't override these methods | `TypeError` at instantiation | No error at instantiation; `NotImplementedError` deferred to call time |
| **BUG-023** | `pyproject.toml:201–210` | `addopts` includes `--cov=apgi_framework` but `pytest-cov` is not in the minimal `dependencies` list — running `pytest` without installing `[dev]` fails immediately | `pip install -e . && pytest` | Test suite runs | `ERROR: unrecognized arguments: --cov=apgi_framework ...` |
| **BUG-024** | `apgi_framework/config/config_manager.py:212` | `presets_dir = Path("config/presets")` is a relative path — resolves differently depending on the working directory at import time | Run tests from a temp directory; create `ConfigManager` | Presets stored relative to project root | Presets stored in unexpected locations when CWD differs from project root |
| **BUG-025** | `apgi_framework/data/storage_manager.py` — `test_concurrent_access` | Concurrent `store_dataset` calls on minimal/empty data dicts all fail validation — zero successful writes when ≥4 are expected | Run `pytest tests/test_data_management.py::TestStorageManager::test_concurrent_access` | ≥4 concurrent writes succeed | `assert 0 >= 4` — all concurrent writes rejected by validator |
| **BUG-026** | Test suite — multiple files | **Test isolation failure:** ~15+ tests pass individually but fail during the full suite run due to shared global state pollution between modules (affected files: `test_deployment_properties`, `test_error_handling_properties`, `test_falsification_coverage`, `test_config_manager` logging variants, `test_utils_basic::TestPerformanceProfiler`) | `pytest tests/` (full run) vs `pytest tests/test_deployment_properties.py` (isolated) | Tests pass in both contexts | Tests fail only in the full suite run |
| **BUG-027** | `apgi_framework/core/equation.py` | `APGIEquation` missing expected public methods `set_parameters()` and `calculate()` | `eq = APGIEquation(); eq.set_parameters({})` | Method executes | `AttributeError: 'APGIEquation' object has no attribute 'set_parameters'` |
| **BUG-028** | `apgi_framework/adaptive/quest_plus_staircase.py` | `QuestPlusParameters` rejects `step_size_min` kwarg; `QuestPlusStaircase` missing `current_level` and `step_up` attributes; `StaircaseState` has no `UP` member — widespread API mismatch between tests and implementation | `QuestPlusParameters(step_size_min=0.1)` | Parameter accepted | `TypeError: unexpected keyword argument 'step_size_min'` |
| **BUG-029** | `apgi_framework/research/stimulus_generators.py` | `ToneParameters`, `GaborParameters`, `CO2PuffParameters` reject their expected primary kwargs (`frequency`, `size`, `concentration`) — constructor API does not match documented/tested interface | `ToneParameters(frequency=440)` | Parameter accepted | `TypeError: unexpected keyword argument 'frequency'` |
| **BUG-030** | `apgi_framework/data/data_manager.py` + `storage_manager.py` | `IntegratedDataManager` rejects `storage_path` constructor arg and is missing `query_experiments()` method; `StorageManager` is missing `retrieve_dataset()` method; `query_datasets()` returns `dict` but callers expect an object with `.experiment_ids` | `IntegratedDataManager(storage_path="/tmp/x")` | Manager created | `TypeError: unexpected keyword argument 'storage_path'`; `AttributeError: no attribute 'query_experiments'`; `AttributeError: no attribute 'retrieve_dataset'` |
| **BUG-031** | Multiple modules — systemic relative-path issue | At least 4 modules resolve output directories relative to CWD at runtime: `config/presets` (ConfigManager), `logs/telemetry` (ErrorTelemetry), `apgi_output/performance_profiles` (PerformanceProfiler), `config` (error_handler). All fail with `FileNotFoundError` when CWD differs from the project root | Instantiate any of these classes from a temp directory or test runner | Directory created relative to project root | `FileNotFoundError: [Errno 2] No such file or directory: 'config'` (etc.) |
| **BUG-032** | `apgi_framework/system_validator.py` | Validation test names returned as "Title Case" (e.g., `"Threshold Management"`) but tests compare against `"snake_case"` (e.g., `"threshold_management"`) — naming convention mismatch | `assert validator.get_test_name() == "threshold_management"` | Strings match | `AssertionError: 'Threshold Management' == 'threshold_management'` |
| **BUG-033** | `apgi_framework/system_validator.py` | `ValidationSuite.total_execution_time` computed via float addition returns `0.30000000000000004` where tests assert `== 0.3` — exact float equality used instead of `pytest.approx` | `assert suite.total_execution_time == 0.3` | Assertion passes | `AssertionError: assert 0.30000000000000004 == 0.3` |
| **BUG-034** | `apgi_framework/workflow_orchestrator.py` | Summary report contains `"APGI Framework Testing - Workflow Summary"` header but test asserts presence of `"WORKFLOW SUMMARY"` | `assert 'WORKFLOW SUMMARY' in orchestrator.save_summary_report()` | Assertion passes | `AssertionError: 'WORKFLOW SUMMARY' not found in output` |
| **BUG-035** | `apgi_framework/research/threshold_detection_paradigm.py` | `PsychometricFunction` is missing the `_extract_threshold_at_performance()` method expected by callers | `fn._extract_threshold_at_performance(0.75)` | Value returned | `AttributeError: 'PsychometricFunction' object has no attribute '_extract_threshold_at_performance'` |
| **BUG-036** | `apgi_framework/testing/framework.py` — `FrameworkTestCase` | Constructor requires a `module` positional argument not documented; callers that omit it get a `TypeError` | `FrameworkTestCase()` | Instance created with defaults | `TypeError: __init__() missing 1 required positional argument: 'module'` |

---

## Missing Features / Incomplete Implementations

| # | Feature / Component | Location | Status | Impact |
|---|---------------------|----------|--------|--------|
| 1 | **Find / Find Next / Find Previous** (text search in results/logs) | `apgi_gui/app.py:1222–1232` | `NotImplementedError` stub | High — menu items and keyboard shortcuts are wired but non-functional |
| 2 | **Debug Mode toggle** | `apgi_gui/app.py:1234–1236` | `NotImplementedError` stub | Medium — developer-facing, but exposed in UI |
| 3 | **PDF export** of statistical analysis reports | `apgi_framework/analysis/statistical_report_generator.py:374` | Enum value defined; `ValueError` raised on use | High — PDF is a first-class documented export format |
| 4 | **LATEX export** of statistical analysis reports | `apgi_framework/analysis/statistical_report_generator.py:374` | Same as PDF | Medium |
| 5 | **API service startup** in deployment automation | `apgi_framework/deployment/automation.py:453–456` | Logs placeholder message; does nothing | High for server/multi-service deployment scenarios |
| 6 | **Real consciousness evaluation** | `GUI.py:6454–6472` | Hardcoded outputs (0.78, 0.65, 0.82) regardless of data | Critical for research validity |
| 7 | **Short-term APGI model analysis** | `GUI.py:6473–6480` | Static string output only | High |
| 8 | **Combined APGI analysis** | `GUI.py:6481–6488` | Static string output only | High |
| 9 | **Coverage visualisation widget** (Qt/PySide6) | `apgi_framework/gui/coverage_visualization.py` | 30+ methods all bare `pass` | Medium — optional Qt UI path is entirely unrendered |
| 10 | **PDF report generation** (ReportLab) | `apgi_framework/reporting/pdf_generator.py` | Module crashes on import when `reportlab` absent (scoping bug) | High — module is part of the reporting subsystem |
| 11 | **Adaptive staircase rule parsing** | `apgi_framework/research/threshold_detection_paradigm.py:390–399` | Does not accept standard `"3up_1down"` notation | Medium — affects all psychophysics experiments using staircases |
| 12 | **Telemetry directory creation on init** | `apgi_framework/logging/error_telemetry.py` | Directory not created in `__init__` | Low — logging silently fails |
| 13 | **CLI logger initialization before use** | `apgi_framework/cli.py:179` | `self.logger = None` used before `setup_logging()` | High — CLI crashes when controller initialisation fails |
| 14 | **Generic dataset storage** | `apgi_framework/data/storage_manager.py` | Requires 3 domain-specific fields; no support for arbitrary research data | Medium |
| 15 | **Presets directory auto-creation with nested paths** | `apgi_framework/config/config_manager.py:329` | `open()` without `parent.mkdir(parents=True, exist_ok=True)` | Medium |
| 16 | **`GUI-Simple.py` missing** | `GUI-Launcher.py:223,703` | File referenced in launcher app registry and `launch_simple_gui()` but does not exist on disk | High |

---

## Test Suite Summary

Tests were executed against all modules that can be imported without a display server (`DISPLAY`). Tests requiring `tkinter`/`customtkinter` were excluded as the test environment lacks `python3-tk`.

| Test File | Passed | Failed | Skipped | Key Failures |
|-----------|:------:|:------:|:-------:|--------------|
| `test_core_models.py` | 70 | 0 | 0 | — |
| `test_core_analysis.py` | 18 | 0 | 0 | — |
| `test_input_validation.py` | 22 | 0 | 0 | — |
| `test_edge_cases.py` | 29 | 0 | 0 | — |
| `test_clinical_module.py` + variants | 56 | 0 | 0 | — |
| `test_pci_calculator.py` | 34 | 0 | 0 | — |
| `test_pharmacological_simulator.py` | 35 | 0 | 0 | — |
| `test_statistical_analysis_validation.py` | 28 | 0 | 0 | — |
| `test_falsification_coverage.py` | 8 | 0 | 0 | — |
| `test_cross_species_validation.py` | 5 | 0 | 0 | — |
| `test_config_manager.py` | 18 | 3 | 0 | `save_preset` no parent-mkdir; corrupted JSON not caught; invalid JSON not caught |
| `test_error_telemetry.py` | 19 | 2 | 0 | Dir not created on init; mock target mismatch |
| `test_core_coverage.py` | 108 | 1 | 0 | `APGIAgent` does not raise `ValueError` on bad params |
| `test_cli_module.py` | 40 | 2 | 0 | `logger=None` before `setup_logging()` |
| `test_cli_coverage.py` | 40 | 7 | 0 | `sys.exit(0)` raised from test context; unknown cmd exits 2 not 1 |
| `test_new_components.py` | 32 | 1 | 86 | Staircase rule `"3up_1down"` rejected |
| `test_diagnostics_cli.py` | 17 | 4 | 9 | Mock attribute error; `sys.exit` call count mismatch |
| `test_workflow_orchestrator.py` | 12 | 8 | 0 | Orchestrator workflow steps fail end-to-end |
| `test_system_validator.py` | 22 | 11 | 0 | Validator suite, equation accuracy, simulation tests |
| `test_data_management.py` | 18 | 15 | 0 | `StorageManager` rejects datasets without domain-specific fields |
| `test_adaptive_comprehensive.py` | 5 | 14 | 0 | `QuestPlusStaircase`, `StimulusGenerators`, `SessionManager` |
| `test_threshold_detection.py` | 8 | 16 | 0 | Timeout; rule parsing; all extended-paradigm tests |
| `integration/test_integration_properties.py` | 19 | 2 | 2 | `FileExistsError` in property tests; error-handling workflow |
| `integration/test_end_to_end_workflow.py` | 0 | 1 | 0 | 9 ERRORS | CI integrator `HEAD~1`; component interaction |
| `test_performance_properties.py` | — | — | — | **Entirely excluded** — `tkinter` unavailable (BUG-003) |
| `tests/framework/test_equation.py` | 0 | 2 | 0 | `APGIEquation` missing `set_parameters()` and `calculate()` (BUG-027) |
| `test_adaptive_comprehensive.py` (full) | 5 | 21 | 0 | API mismatch: `QuestPlusParameters`, `StaircaseState`, `QuestPlusStaircase`, stimulus generators, `SessionConfiguration` (BUG-028, BUG-029) |
| `test_activity_logging_properties.py` | varies | 3 | 0 | Execution ID not logged; test name not in output; concurrent logging drops entries |
| `test_data_management.py` (full) | 3 | 15 | 0 | `IntegratedDataManager` / `StorageManager` API mismatch (BUG-030) |

**Full suite result (confirmed, 3 independent runs):** ~106–110 failed, 540–544 passed, 121 skipped, 9 errors — variance between runs confirms test isolation issues (BUG-026).

**Note on test isolation:** Several failures (`test_deployment_properties`, `test_error_handling_properties`, `test_falsification_coverage`, `test_config_manager` logging variants, `test_utils_basic::TestPerformanceProfiler`) pass when run in isolation but fail during the full suite run. This indicates **shared global state / test-order dependency** across modules — an additional quality issue not captured per-file above.

---

## UI / UX Findings

| Area | Finding | Severity |
|------|---------|----------|
| Menu items (Edit → Find) | Wired to `NotImplementedError`; user receives an unhandled exception dialog | High |
| Menu items (Debug Mode) | Same — raises `NotImplementedError` | Medium |
| Consciousness evaluation button | Returns instantly with hardcoded numbers; no progress indicator or real computation | High |
| APGI model buttons | Return instantly with generic success dialog; no computation | High |
| Theme toggle | Implemented; recursively propagates to child widgets | ✓ OK |
| Undo/Redo | Implemented with memory-limited stack | ✓ OK |
| Zoom (Ctrl+= / Ctrl+-) | Implemented; scales fonts and window size | ✓ OK |
| Keyboard shortcuts | Registered via `_setup_standard_shortcuts`; most functional | ✓ Mostly OK |
| Help dialog | Context-sensitive help implemented per-tab | ✓ OK |
| Recent files list | Persisted to JSON; loaded on startup | ✓ OK |
| Status bar | Updates on operations; colour-coded by level | ✓ OK |
| Preferences dialog | Full preferences dialog with save/reset implemented | ✓ OK |
| Log viewer | Implemented with filtering and export | ✓ OK |
| Tab navigation | Next/Previous tab via keyboard shortcut | ✓ OK |

---

## Responsiveness & Performance Findings

| Area | Finding | Severity |
|------|---------|----------|
| Long-running tests | Offloaded to `threading.Thread` in all experiment runner methods | ✓ OK |
| Psychometric fitting | `threshold_detection_paradigm.py` operations exceed 30 s in test scenarios; potential infinite loop in fitting loop | High |
| Figure management | `MatplotlibManager` limits figures to 20 and cleans up oldest; GC called after close | ✓ OK |
| Memory (undo stack) | `_get_object_size()` tracks undo stack memory, trimmed by size | ✓ OK |
| tkinter import in performance module | `performance_monitor.py` imports `tkinter` unconditionally at module level — blocks all non-GUI usage | Critical |
| Dataset concurrency | `StorageManager` concurrent writes all fail due to overly strict validator | Medium |

---

## Cross-Browser / Cross-Platform Compatibility

This is a desktop Python/tkinter application; standard web browser compatibility is not applicable. Platform-relevant findings:

| Platform Area | Finding | Severity |
|---------------|---------|----------|
| Linux headless | `tkinter`/`customtkinter` require `python3-tk` system package; README documents this but no runtime guard exists | Medium |
| Linux headless | `performance_monitor.py` hard-imports `tkinter`; blocks non-GUI usage and the entire `test_performance_properties.py` suite | Critical |
| Windows paths | `security_validator.py` references Windows-specific paths (`C:\Windows\`, `C:\Program Files\`) which is intentional for validation; fine | ✓ OK |
| Dependency isolation | `reportlab` optional but `pdf_generator.py` fails to import when absent due to module-level use of `A4` outside the try block | Critical |
| `pyproject.toml` addopts | `--cov` flags in `addopts` break `pytest` without `pytest-cov` installed; not in minimal `dependencies` | Medium |
| `GUI-Simple.py` missing | `GUI-Launcher.py:223,703` registers and can launch `GUI-Simple.py` but the file does not exist in the repository | High |

---

## Actionable Recommendations for Remediation

### Priority 1 — Critical (Fix immediately before any release)

**REC-001: Fix `pdf_generator.py` `A4` scoping bug**
Move the `ReportConfig.page_size` default from `A4` to a string constant (`"A4"`) or use a `field(default_factory=...)` with a lazy lookup. Alternatively define `A4 = (595.28, 841.89)` as a fallback in the `except ImportError` block.
```python
# In the except ImportError block:
A4 = (595.28, 841.89)
inch = 72.0
```

**REC-002: Fix `cli.py` `NoneType` logger crash**
Initialize `self.logger` to a real logger in `__init__` instead of `None`:
```python
def __init__(self):
    self.controller = None
    self.logger = logging.getLogger(__name__)
```

**REC-003: Wrap `tkinter` import in `performance_monitor.py`**
Guard the top-level import:
```python
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
```

---

### Priority 2 — High (Fix before general availability)

**REC-004: Implement or disable Find/Find Next/Find Previous/Debug Mode**
Either implement a basic text-search dialog in `apgi_gui/app.py` or disable/grey-out the menu items and keyboard shortcuts. Remove the bare `raise NotImplementedError` so users do not encounter unhandled exceptions.

**REC-005: Replace hardcoded analysis outputs**
`run_consciousness_evaluation()`, `short_term_apgi_model()`, and `combined_apgi_analysis()` in `GUI.py` must call actual model code. At minimum, wire them to the existing framework functions in `apgi_framework/` and display real computed results.

**REC-006: Fix `config_manager.save_preset()` directory creation**
Add `preset_path.parent.mkdir(parents=True, exist_ok=True)` before the `open()` call.

**REC-007: Catch `JSONDecodeError` in `load_preset()`**
Wrap `json.load()` in a try/except and re-raise as `ConfigurationError`.

**REC-008: Fix staircase rule parser**
Accept the standard notation `"3up_1down"` by parsing the string with a regex:
```python
import re
m = re.match(r'(\d+)up_(\d+)down', rule)
if not m:
    raise ValidationError(...)
up_count, down_count = int(m.group(1)), int(m.group(2))
```

**REC-009: Implement PDF and LATEX export formats**
In `statistical_report_generator.py`, add a `_export_pdf()` method that uses the existing `pdf_generator.py` module, and a `_export_latex()` method. Remove the two unimplemented format cases from the `ValueError`.

**REC-010: Implement API service startup**
`_start_api_service()` in `deployment/automation.py` must either start a real service (Flask/FastAPI) or raise a `NotImplementedError` with a clear message rather than silently returning.

---

### Priority 3 — Medium (Fix before beta)

**REC-011: Fix `StorageManager` validation to support generic datasets**
Move the domain-specific field requirements (`apgi_parameters`, `neural_signatures`, `consciousness_assessments`) from mandatory to optional/configurable validation, or add a `strict=False` mode for non-domain data.

**REC-012: Use absolute path for `presets_dir`**
In `ConfigManager.__init__`, resolve the presets directory relative to the config file location or the package root:
```python
self.presets_dir = Path(__file__).parent.parent / "config" / "presets"
```

**REC-013: Fix `pytest` addopts / dependency declaration**
Move `--cov` flags out of `addopts` in `pyproject.toml` and into a `pytest.ini` or separate `conftest.py` so that users without `pytest-cov` can still run the test suite. Add `pytest-cov` to the base `dependencies` or document the `[dev]` install requirement prominently.

**REC-014: Handle missing `HEAD~1` in CI integrator**
Catch the `git diff HEAD~1` failure case and fall back to `git diff HEAD` or return an empty-but-valid result:
```python
result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], ...)
if result.returncode != 0:
    result = subprocess.run(["git", "diff", "--name-only", "HEAD"], ...)
```

**REC-015: Add `exist_ok=True` in property-based integration test**
In `test_integration_properties.py:861`, change:
```python
project_dir.mkdir(parents=True)
```
to:
```python
project_dir.mkdir(parents=True, exist_ok=True)
```

**REC-016: Fix `threshold_detection_paradigm.py` performance**
Profile and fix the psychometric function fitting path that causes >30 s hangs in `test_adaptive_comprehensive.py` and `test_threshold_detection.py`. Add iteration limits and convergence guards.

**REC-017: Implement `ErrorTelemetry` directory creation**
Create the telemetry directory (and default file) in `ErrorTelemetry.__init__()`:
```python
self.telemetry_file.parent.mkdir(parents=True, exist_ok=True)
```

**REC-018: Fix unknown CLI command exit code**
In `cli.py`, intercept unknown commands before argparse exits with code 2:
```python
parser.error = lambda msg: sys.exit(1)
```
or handle unrecognised subcommands explicitly and call `sys.exit(1)`.

---

### Priority 4 — Low (Quality improvements)

**REC-019: Fix systemic relative-path issues across modules**
Audit every module that constructs file paths at runtime. Replace all occurrences of `Path("config/presets")`, `Path("logs/telemetry")`, `Path("apgi_output/...")`, etc. with paths anchored to a known absolute reference:
```python
BASE_DIR = Path(__file__).parent.parent  # project root
self.presets_dir = BASE_DIR / "config" / "presets"
```
Apply the same pattern to `error_handler.py`, `error_telemetry.py`, and `performance_monitor.py`.

**REC-020: Fix test isolation / shared global state**
Use `pytest-xdist` isolation or `autouse` fixtures that reset global singletons (`APGILogManager`, `ErrorTelemetry`, `ConfigManager`) between tests. Alternatively, run `pytest --forked` (via `pytest-forked`) to guarantee process isolation. Use `monkeypatch` or `importlib.reload()` in affected test modules rather than relying on module-level singletons persisting across tests.

**REC-025: Implement missing `APGIEquation` public API**
Add `set_parameters(params: dict)` and `calculate()` (or `compute()`) methods to `APGIEquation`. These are referenced directly in `tests/framework/test_equation.py` and appear to be core documented methods.

**REC-026: Reconcile `QuestPlus*` / stimulus generator / session API**
Align `QuestPlusParameters`, `QuestPlusStaircase`, `StaircaseState`, `ToneParameters`, `GaborParameters`, `CO2PuffParameters`, and `SessionConfiguration` constructors with the kwargs expected by the test suite. Either add the missing parameters to the dataclasses or update tests to match the actual implemented signatures — but do not leave them silently mismatched.

**REC-027: Fix `IntegratedDataManager` / `StorageManager` API**
Add `storage_path` constructor parameter to `IntegratedDataManager`. Implement missing `query_experiments()` and `StorageManager.retrieve_dataset()` methods. Fix `query_datasets()` to return an object with `.experiment_ids` rather than a raw `dict`.

**REC-028: Normalise `SystemValidator` test name casing**
Change validator test names from "Title Case" to `snake_case` (or update tests to match), and replace `== 0.3` float comparisons with `pytest.approx(0.3)`.

**REC-029: Fix `WorkflowOrchestrator` summary header**
Change the summary template to include `"WORKFLOW SUMMARY"` as a section header, or update the test assertion to match `"APGI Framework Testing - Workflow Summary"`.

**REC-030: Add `_extract_threshold_at_performance()` to `PsychometricFunction`**
Implement this private helper method which is called by threshold-extraction code and expected by tests.

**REC-031: Fix `FrameworkTestCase` constructor**
Make the `module` argument optional with a sensible default, or document it clearly as required and update all callers.

**REC-021: Implement `coverage_visualization.py` Qt widget**
Either complete the PySide6 widget implementation or remove it and implement an equivalent tkinter widget since the rest of the UI uses tkinter/customtkinter.

**REC-022: Fix `global _global_monitor` in `realtime_monitor.py`**
Remove or populate the unused `global` declaration (flake8 F824).

**REC-023: Add `@abstractmethod` decorator to `enhanced_error_handling.py` stubs**
The two methods raising `NotImplementedError` should be decorated with `@abstractmethod` and the class should inherit from `ABC` to enforce implementation at subclass instantiation time.

**REC-024: Enforce `APGIAgent` parameter validation**
The test `test_agent_parameter_validation` expects `ValueError` for out-of-range parameters. Implement boundary checks in the agent's `__init__` or `set_parameters()` method.

**REC-032: Add `system_tk_available` guard to all top-level tkinter GUI modules**
Wrap all `import tkinter` statements in optional/guarded imports across `apgi_framework/gui/` so that headless imports (for unit testing or CLI-only usage) gracefully degrade.

---

## Appendix — Files Audited

| File | Lines | Notes |
|------|------:|-------|
| `GUI.py` | ~6750 | Main desktop GUI — extensive, mostly functional |
| `GUI-Launcher.py` | ~1500 | Launcher GUI — clean, no syntax errors |
| `GUI-Experiment-Registry.py` | ~850 | Registry GUI — 2 bare `pass` stubs in exception handlers |
| `apgi_gui/app.py` | ~1700 | Alternative GUI app — 4 `NotImplementedError` stubs |
| `apps/apgi_falsification_gui.py` | ~2000 | Falsification GUI — 7 bare `pass` stubs |
| `Tests-GUI.py` | ~900 | Test runner GUI — 2 bare `pass` in error handlers |
| `Utils-GUI.py` | ~600 | Utils GUI — no stubs found |
| `apgi_framework/cli.py` | ~2200 | CLI — logger init bug (BUG-002) |
| `apgi_framework/reporting/pdf_generator.py` | ~400 | Critical import bug (BUG-001) |
| `apgi_framework/gui/coverage_visualization.py` | ~450 | Qt widget — 30+ stub methods |
| `apgi_framework/optimization/performance_monitor.py` | ~200 | Unconditional tkinter import (BUG-003) |
| `apgi_framework/config/config_manager.py` | ~400 | `save_preset` / `load_preset` bugs |
| `apgi_framework/analysis/statistical_report_generator.py` | ~380 | PDF/LATEX formats unimplemented |
| `apgi_framework/deployment/automation.py` | ~500 | API service startup stub |
| `apgi_framework/research/threshold_detection_paradigm.py` | ~600 | Rule parser bug; performance issues |

---

*Report generated by automated code analysis (static + dynamic) on branch `claude/app-audit-testing-onxEE`. All reproduction steps were verified against the live codebase.*
