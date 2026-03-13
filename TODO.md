# TODO

### BUG-014 — 379 `print()` Calls in Framework Code
| **Component** | `apgi_framework/` (all modules) |
| **Status** | ⚠️ **PARTIALLY ADDRESSED** |
**Description:** Direct `print()` calls bypass the logging system. This prevents log level control, file rotation, and structured output. Particularly notable in `apgi_framework/installation_validator.py`, `apgi_framework/system_validator.py`, and various GUI modules.
**Fix Applied:** CLI tools (cli.py, installation_validator.py, etc.) appropriately use print() for user-facing output. Help system fallback methods use print() appropriately. Non-CLI modules should use logger calls for debugging/error logging. 420 total print() calls found, but many are intentional in CLI/help contexts.

| **No visual disabled-state feedback for running operations.** When a test is running, the sidebar buttons are not disabled — only a console log message indicates another test is in progress. This is inconsistent with standard desktop UX. | `GUI.py` | Medium | Not Fixed |
| **379 `print()` calls in `apgi_framework/` (excluding CLI).** Production code should use the logging framework for all output. Direct `print()` bypasses log level controls, rotation, and filtering. (BUG-014.) | `apgi_framework/` | Low | Not Fixed |
| MF-006 | Theme persistence across restarts | `GUI.py:5091` | P1 | Theme saved in memory only |
| MF-007 | Auto-save functionality | `GUI.py:4988` | P2 | Checkbox exists, no implementation |
| MF-009 | Thread pool reconfiguration | `thread_manager.py` | P2 | Preference is read but not applied |
| R-01 | Replace `pickle.load()` with `safe_pickle_load()` in `MLIntegration.load_model()` | `ml/ml_integration.py:473` | 30 min | Backend |
| R-03 | Add API token authentication to all Flask REST endpoints | `web_interface.py` | 2–4 h | Backend | Not Fixed |
| R-13 | Implement auto-save timer using `self.after(interval, save_fn)` | `GUI.py` | 3 h | GUI |
| R-19 | Replace 379 `print()` calls with `logger.*()` | `apgi_framework/` | 4–8 h | Backend |
| R-21 | Increase overall test coverage from 9% to at least 60% for critical paths | `tests/` | 2–4 weeks |
| `test_load_config_invalid_json` | `test_config_manager.py` | BUG-001: exception propagated instead of fallback |
| `test_load_preset_corrupted_json` | `test_config_manager.py` | BUG-001: related |
| `test_save_preset_creates_directory` | `test_config_manager.py` | BUG-005: directory not created |