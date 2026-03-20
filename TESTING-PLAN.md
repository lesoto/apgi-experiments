# APGI Framework Test Coverage Improvement Plan

## Coverage Status Summary

> **Overall Coverage**: **26.99%** (33,688 statements, 9,091 covered)
> **Test Suite**: 70+ test files, 445+ tests in `tests/`
> **Status**: In Progress - Coverage increasing, 6 new test files added.
> **Latest Improvement**: Coverage increased from 24.00% → 26.99% by adding tests for neural, adaptive, validation modules.

- [x] Create tests for `apgi_framework/neural/physiological_monitoring.py` (440 stmts — was 0%)
- [x] Create tests for `apgi_framework/neural/cardiac_processor.py` (360 stmts — was 0%)
- [x] Create tests for `apgi_framework/adaptive/task_control.py` (412 stmts — was 0%)
- [x] Create tests for `apgi_framework/adaptive/stimulus_generators.py` (396 stmts — was 0%)
- [x] Create tests for `apgi_framework/validation/system_health.py` (322 stmts — 0% → 83%)
- [x] Create tests for `apgi_framework/main_controller.py` (500 stmts — ~10%)
- [ ] Create tests for high-statement modules with 0% coverage:
  - `apgi_framework/gui/coverage_visualization.py` (504 statements - 0%)
  - `apgi_framework/gui/results_viewer.py` (470 statements - 0%)
  - `apgi_framework/gui/enhanced_dash.py` (444 statements - 0%)
  - `apgi_framework/gui/error_handling.py` (381 statements - 0%)
- [ ] Improve coverage for partial modules in `apgi_framework/core/`
- [ ] Achieve 100% coverage across all functional submodules

## Known Test Suite Issues

1. **System Initialization**: (Fixed) Core components and tests now initialize correctly.
2. **Missing Dependencies**: Optional dependencies (like `h5py`, `pystan`) require careful mocking.
3. **GUI Display**: GUI-heavy modules require headless `PySide6` testing (currently 0%).
4. **Segfault**: Full test suite can segfault — running targeted test subsets avoids this.

### Coverage Gaps (Top Modules)

| Module | Statements | Status | Coverage | Priority |
| :--- | :---: | :--- | :---: | :--- |
| `apgi_framework/experimental_control.py` | 1142 | ✅ Added core logic tests | 🟩 87.5% | Critical |
| `apgi_framework/cli.py` | 1064 | ✅ Added validation logic tests | 🟩 ~90% | Critical |
| `apgi_framework/system_validator.py` | 543 | ✅ Added validation suite tests | 🟩 61.9% | High |
| `apgi_framework/main_controller.py` | 500 | ✅ Added controller tests | ⚠️ ~15% | High |
| `apgi_framework/data/persistence_layer.py` | 468 | ✅ Bug fixed, new tests added | ⚠️ 18.6% | High |
| `apgi_framework/analysis/analysis_engine.py` | 339 | ✅ Added analysis tests | 🟩 ~100% | High |
| `apgi_framework/workflow_orchestrator.py` | 358 | ✅ Added workflow tests | 🟩 79.05% | High |
| `apgi_framework/validation/system_health.py` | 322 | ✅ Comprehensive tests added | 🟩 83.2% | Medium |
| `apgi_framework/neural/physiological_monitoring.py` | 440 | ✅ Comprehensive tests added | 🟩 ~85% | High |
| `apgi_framework/neural/cardiac_processor.py` | 360 | ✅ Comprehensive tests added | 🟩 ~70% | High |
| `apgi_framework/adaptive/task_control.py` | 412 | ✅ Comprehensive tests added | 🟩 ~75% | Medium |
| `apgi_framework/adaptive/stimulus_generators.py` | 396 | ✅ Comprehensive tests added | 🟩 ~70% | Medium |
| `apgi_framework/gui/coverage_visualization.py` | 504 | 🔄 Needs GUI tests | ❌ 0% | High |
| `apgi_framework/gui/results_viewer.py` | 470 | 🔄 Needs GUI tests | ❌ 0% | High |
| `apgi_framework/clinical/parameter_extraction.py` | 451 | ✅ Added extraction tests | 🟩 ~100% | High |
| `apgi_framework/gui/enhanced_dash.py` | 444 | 🔄 Needs GUI tests | ❌ 0% | Medium |
| `apgi_framework/gui/error_handling.py` | 381 | 🔄 Needs GUI tests | ❌ 0% | Low |
| `apgi_framework/testing/performance_opt.py` | 366 | 🔄 Needs benchmark tests | ❌ 0% | Low |
| `apgi_framework/testing/ci_integrator.py` | 320 | 🔄 Needs CI tests | ❌ 0% | Low |
| `apgi_framework/data/storage_manager.py` | 330 | ✅ Added storage tests | 🟩 ~100% | High |


## Progress Summary (2026-03-19)

| Module | Statements | Status | Coverage |
| :--- | :---: | :--- | :---: |
| `apgi_framework/cli.py` | 1064 | Added validation logic tests | ~90% |
| `apgi_framework/data/persistence_layer.py` | 468 | FIXED BUG + New tests | 18.6% |
| `apgi_framework/system_validator.py` | 543 | New tests | 61.9% |
| `apgi_framework/main_controller.py` | 500 | Added controller tests | ~15% |
| `apgi_framework/experimental_control.py` | 1142 | Implemented comprehensive tests | 87.5% |
| `apgi_framework/workflow_orchestrator.py` | 358 | Fixed errors, implemented tests | 79.1% |
| `apgi_framework/data/storage_manager.py` | 330 | Implemented comprehensive tests | ~100% |
| `apgi_framework/clinical/parameter_extraction.py` | 451 | Implemented comprehensive tests | ~100% |
| `apgi_framework/analysis/analysis_engine.py` | 339 | Implemented comprehensive tests | ~100% |
| `apgi_framework/analysis/ml_classification.py` | 273 | Added ML classification tests | ~100% |
| `apgi_framework/neural/physiological_monitoring.py` | 440 | **NEW** Comprehensive tests added | ~85% |
| `apgi_framework/neural/cardiac_processor.py` | 360 | **NEW** Comprehensive tests added | ~70% |
| `apgi_framework/adaptive/task_control.py` | 412 | **NEW** Comprehensive tests added | ~75% |
| `apgi_framework/adaptive/stimulus_generators.py` | 396 | **NEW** Comprehensive tests added | ~70% |
| `apgi_framework/validation/system_health.py` | 322 | **NEW** Comprehensive tests added | 83.2% |

### New Test Files Added

| Test File | Tests | Target Module |
| :--- | :---: | :--- |
| `tests/test_neural_physmon_coverage.py` | 45+ | `neural/physiological_monitoring.py` |
| `tests/test_cardiac_processor_coverage.py` | 30+ | `neural/cardiac_processor.py` |
| `tests/test_task_control_coverage.py` | 60+ | `adaptive/task_control.py` |
| `tests/test_stimulus_generators_coverage.py` | 50+ | `adaptive/stimulus_generators.py` |
| `tests/test_system_health_coverage.py` | 35+ | `validation/system_health.py` |
| `tests/test_main_controller_coverage.py` | 7 | `main_controller.py` |

### Remaining Work

- `apgi_framework/gui/main_window.py` (0% coverage — requires GUI/display)
- `apgi_framework/testing/` submodules (many at 0%)
- `apgi_framework/reporting/` submodules (0%)
- `apgi_framework/security/` submodules (0%)
- `apgi_framework/utils/` submodules with 0% (font_manager, thread_manager, etc.)
