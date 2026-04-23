# APGI Framework — Comprehensive Codebase Architecture Audit

## 3.2.1 Improved Coverage (Progress Made)

Coverage has improved from 11.3% to approximately 29% overall. Significant progress has been made in test coverage:

- 200+ tests now passing (up from much lower baseline)
- Fixed CLI module tests completely
- Fixed core model integration tests
- Fixed adaptive module tests
- Fixed clinical module tests (with proper skipping for missing dependencies)
- Test collection now works properly

However, many modules still need additional coverage, particularly `deployment`, `security`, `export`, and many `gui` components.

### 3.2.2 Oversized Modules

- `gui/` at 16,629 lines with 24 files is the largest module and likely has high internal coupling
- `data/` (16 files), `testing/` (14 files), and `analysis/` (13 files) are also large
- Consider splitting `gui/` into `gui/components/`, `gui/dashboards/`, and `gui/utils/` (partially done)

### 3.2.3 Test Collection Issues Resolved

Previous test collection issues (import errors, pytest.skip usage, test class constructors) have been fixed. The aspirational tests that were causing 60 errors have been addressed. Test failures reduced from ~98 to ~50, with proper skipping for missing dependencies.

### 3.2.4 Test-to-Source Ratio

- Source: 105,388 lines
- Tests: 31,311 lines
- Ratio: 0.30:1

A healthy ratio is typically 1:1 to 2:1 (tests:source). The current 0.3:1 ratio, combined with 29% coverage, indicates continued need for test expansion, though significant progress has been made.

### 3.3 Dependency Flow

The framework follows a layered architecture:

```text
Entry Points (CLI, GUIs, scripts)
  └── main_controller / workflow_orchestrator
        ├── core (models, data structures)
        ├── engines (analysis, falsification)
        ├── adaptive (QUEST+, task control)
        ├── neural / clinical / simulators
        ├── data (persistence, formats)
        ├── validation / security
        └── gui / visualization / reporting
```

The `engines` module is nearly empty (11 lines), suggesting the analysis engine code may be scattered across `analysis/` and `falsification/` rather than properly centralized.

---

## 4. Risk Areas

| Risk | Impact | Recommendation |
| --- | --- | --- |
| 29% code coverage | Some bugs still undetected, refactoring still risky | Continue prioritizing coverage for `core/`, `data/`, `analysis/` |
| ~50 failing tests | Some real failures remain | Fix remaining test failures in adaptive, falsification, storage |
| No integration test for full workflow | End-to-end behavior unverified | Add smoke test for CLI + core pipeline |
| `gui/` module size (16K lines) | Hard to maintain and test | Split into focused sub-modules |
| `engines/` is a stub (11 lines) | Architectural gap | Consolidate engine code or remove the module |
| Multiple GUI entry points | User confusion | Consolidate into single launcher |
| Test duration (~23 min) | Slows CI feedback | Parallelize or mark slow tests |
| 8 skipped tests | May hide regressions | Review skip reasons periodically |

---

## 5. Recommendations

### Immediate Actions (Priority 1)

1. **Fix remaining ~50 failures**: Focus on adaptive, falsification, and storage manager test failures
2. **Increase coverage to 40%+**: Continue focusing on `core/`, `data/`, `analysis/`, and `falsification/` — the most critical modules
3. **Add CLI smoke test**: A single end-to-end test that runs the main workflow through the CLI
4. **Target 70%+ coverage**: Systematically add tests for `neural/`, `clinical/`, `simulators/`, and `gui/` modules
5. **Refactor `gui/`**: Split the 24-file, 16K-line module into focused sub-packages
6. **Implement or remove `engines/`**: The 11-line stub should either become the central engine registry or be removed
7. **Add architecture decision records (ADRs)**: Document key design decisions for future contributors
8. **Implement missing TODO items**: Database integration, ML classification tools, deployment automation
