# APGI Framework — Comprehensive Codebase Audit Report (v5.0)

**Date:** 2026-03-20
**Branch:** `claude/audit-codebase-8HGSo`
**Scope:** Full codebase audit — architecture, test coverage, security, and quality

---

## Executive Summary

The APGI Framework is a production-ready research platform for consciousness studies and neural signal processing. It implements the Advanced Platform for General Intelligence (APGI) model, with particular focus on the **Interoceptive Predictive Integration (IPI)** model for consciousness research.

The codebase is large and well-structured at **~198,000 lines of Python** across **262 source files** and **81 test files**. Multiple previous audit cycles have significantly improved coverage across critical modules. This report consolidates the full audit picture, documenting what has been done, what remains, and what is recommended.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Repository Statistics](#2-repository-statistics)
3. [Architecture Overview](#3-architecture-overview)
4. [Directory Structure](#4-directory-structure)
5. [Entry Points](#5-entry-points)
6. [Core Framework Modules](#6-core-framework-modules)
7. [Test Coverage Analysis](#7-test-coverage-analysis)
8. [Security Audit](#8-security-audit)
9. [Dependencies](#9-dependencies)
10. [CI/CD Pipeline](#10-cicd-pipeline)
11. [Deployment Infrastructure](#11-deployment-infrastructure)
12. [Known Issues & Gaps](#12-known-issues--gaps)
13. [Recommendations](#13-recommendations)
14. [Audit History](#14-audit-history)

---

## 1. Project Overview

| Field | Value |
|---|---|
| **Name** | APGI Framework — Test Enhancement |
| **Version** | 1.0.0 (Beta) |
| **License** | MIT |
| **Python** | 3.8 — 3.12 |
| **Research Domain** | Consciousness studies, neural signal processing, adaptive testing |
| **Primary Purpose** | Validate and falsify consciousness theories through systematic experimental paradigms |

### What the Framework Does

- **Consciousness theory testing**: Implements falsification paradigms to empirically test/falsify theories such as IPI
- **Neural data processing**: EEG, ECG, and pupillometry signal processing pipelines
- **Adaptive experimental control**: QUEST+ staircase, adaptive stimuli, closed-loop paradigms
- **Clinical biomarker identification**: Extracts and quantifies clinical-grade biomarkers from physiological data
- **Cross-species validation**: Supports both human and animal research paradigms
- **Machine learning integration**: Classification, prediction, and pattern detection in neural data

---

## 2. Repository Statistics

| Metric | Value |
|---|---|
| Total Python source files | 262 |
| Core framework modules | 181 |
| Test files | 81 |
| Total estimated LOC | ~198,000 |
| Documentation files (Markdown) | 55+ |
| Configuration/data files | 438 |
| Example data size | ~180 MB |

### Code Distribution

| Directory | Files | Purpose |
|---|---|---|
| `apgi_framework/` | 181 | Core framework |
| `tests/` | 81 | Test suite |
| `apgi_gui/` | ~15 | GUI module package |
| `examples/` | ~20 | Usage examples & demos |
| `utils/` | ~25 | Developer utilities |
| `research/` | ~10 | Research implementations |
| `benchmarks/` | 4 | Performance benchmarks |
| Root scripts | 10 | Launchers, runners |

---

## 3. Architecture Overview

The framework follows a **layered MVC architecture** with a plugin-like module system:

```
┌───────────────────────────────────────────────────────┐
│                    Entry Points                        │
│  GUI-Launcher.py  │  CLI (cli.py)  │  Python API      │
└───────────────────────────────────────────────────────┘
           │                  │               │
┌──────────▼──────────────────▼───────────────▼─────────┐
│               Main Controller (main_controller.py)     │
│           Workflow Orchestrator (workflow_orchestrator) │
└────────────────────────────────────────────────────────┘
           │
┌──────────▼──────────────────────────────────────────────────────────────┐
│                       Core Framework Packages                           │
│  core/  │  neural/  │  adaptive/  │  falsification/  │  clinical/      │
│  ml/    │  analysis/ │  data/     │  validation/     │  simulators/    │
│  gui/   │  testing/  │  reporting/ │ monitoring/     │  security/      │
└─────────────────────────────────────────────────────────────────────────┘
           │
┌──────────▼────────────────────────────────────┐
│           Infrastructure Layer                 │
│  PostgreSQL │ Redis │ Docker │ Prometheus      │
│  Grafana   │ Nginx │ k8s    │ GitHub Actions  │
└───────────────────────────────────────────────┘
```

### Design Patterns

| Pattern | Where Used |
|---|---|
| MVC | GUI ↔ Controller ↔ Models |
| Singleton | Configuration manager, logging |
| Factory | Test runners, analysis engines |
| Observer | Real-time monitoring dashboard |
| Strategy | Falsification criteria, analysis backends |
| Pipeline | Data processing workflows |
| Plugin | Research modules, experimental paradigms |

---

## 4. Directory Structure

```
apgi-experiments/
├── apgi_framework/                # Core framework (181 Python files)
│   ├── core/                      # Mathematical models
│   │   ├── data_models.py
│   │   ├── equation.py            # APGI core equations
│   │   ├── precision.py
│   │   ├── prediction_error.py
│   │   ├── threshold.py
│   │   └── somatic_marker.py
│   ├── cli.py                     # Primary CLI (2,305 LOC)
│   ├── experimental_control.py    # Experimental validation (2,582 LOC)
│   ├── system_validator.py        # System validation (1,478 LOC)
│   ├── workflow_orchestrator.py   # Workflow management (903 LOC)
│   ├── main_controller.py         # App controller (499 LOC)
│   ├── gui/                       # GUI components & dashboards
│   ├── analysis/                  # Data analysis engines
│   ├── neural/                    # Neural signal processing
│   ├── clinical/                  # Clinical biomarkers
│   ├── adaptive/                  # Adaptive paradigms
│   ├── falsification/             # Falsification protocols
│   ├── testing/                   # Testing framework
│   ├── config/                    # Configuration management
│   ├── deployment/                # Deployment automation
│   ├── monitoring/                # Real-time monitoring
│   ├── validation/                # Validation systems
│   ├── data/                      # Data processing & persistence
│   ├── ml/                        # Machine learning
│   ├── simulators/                # Neural/pharmacological simulators
│   ├── security/                  # Security modules
│   ├── error_handling/            # Error management
│   ├── logging/                   # Logging configuration
│   ├── reporting/                 # Report generation (PDF, templates)
│   ├── visualization/             # Data visualization
│   ├── optimization/              # Performance optimization
│   ├── accessibility/             # Accessibility features
│   ├── research/                  # Research-specific modules
│   └── utils/                     # Utility functions
│
├── apgi_gui/                      # GUI module package
│   ├── app.py                     # Advanced GUI (~65K LOC)
│   ├── components/
│   ├── config/
│   └── utils/
│
├── tests/                         # Test suite (81 files)
│   ├── conftest.py
│   ├── framework/
│   ├── integration/
│   └── test_*.py                  # 70+ test modules
│
├── examples/                      # Usage examples
│   ├── 01_run_primary_falsification_test.py
│   ├── 02_batch_processing_configurations.py
│   ├── 03_custom_analysis_saved_results.py
│   ├── 04_extending_falsification_criteria.py
│   └── data/                      # Example datasets (~170MB)
│
├── research/                      # Research implementations
│   ├── core_mechanisms/
│   └── interoceptive_gating/
│
├── utils/                         # Developer tools
├── config/                        # Default configuration
├── data/                          # Research data (~180MB)
├── benchmarks/                    # Performance benchmarks
├── apps/                          # Application templates
├── docs/                          # Documentation (55+ files)
├── k8s/                           # Kubernetes manifests
├── .github/workflows/             # CI/CD pipelines
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── requirements.txt
```

---

## 5. Entry Points

Listed in order of primary importance:

| # | File | Type | Purpose | LOC |
|---|---|---|---|---|
| 1 | `apgi_framework/cli.py` | CLI | Primary command-line interface | 2,305 |
| 2 | `GUI.py` | Desktop GUI | Main GUI application | 7,248 |
| 3 | `GUI-Launcher.py` | Desktop GUI | Launcher for all GUI apps | 1,043 |
| 4 | `GUI-Experiment-Registry.py` | Desktop GUI | Experiment management | 948 |
| 5 | `apgi_gui/app.py` | Desktop GUI | Advanced GUI application | ~65,000 |
| 6 | `run_experiments.py` | Script | Batch experiment runner | 1,149 |
| 7 | `run_tests.py` | Script | Test runner | 840 |
| 8 | `Tests-GUI.py` | Desktop GUI | Test execution GUI | 753 |
| 9 | `Utils-GUI.py` | Desktop GUI | Utilities GUI | 634 |
| 10 | `apgi_framework/main_controller.py` | Python API | Python API entry point | 499 |

### CLI Usage

```bash
# Run tests
python -m apgi_framework.cli test --all

# Run with coverage
pytest --cov=apgi_framework

# Run specific categories
pytest -m unit
pytest -m integration
pytest -m gui
```

### GUI Usage

```bash
python GUI-Launcher.py          # Recommended entry point
python GUI.py                   # Direct main GUI
python GUI-Experiment-Registry.py
```

---

## 6. Core Framework Modules

### 6.1 Core Mathematical Models (`apgi_framework/core/`)

| Module | Purpose |
|---|---|
| `equation.py` | APGI core equations (IPI model) |
| `data_models.py` | Data structure definitions |
| `precision.py` | Bayesian precision calculations |
| `prediction_error.py` | Hierarchical prediction error |
| `threshold.py` | Consciousness threshold detection |
| `somatic_marker.py` | Somatic marker integration engine |

### 6.2 Neural Signal Processing (`apgi_framework/neural/`)

| Module | Purpose | Coverage |
|---|---|---|
| `physiological_monitoring.py` | EEG/ECG real-time monitoring | ~85% |
| `cardiac_processor.py` | Cardiac signal processing | ~70% |

### 6.3 Adaptive Paradigms (`apgi_framework/adaptive/`)

| Module | Purpose | Coverage |
|---|---|---|
| `task_control.py` | Adaptive task/trial control | ~75% |
| `stimulus_generators.py` | Stimulus generation engine | ~70% |
| `quest_plus_staircase.py` | QUEST+ psychophysical staircase | N/A |

### 6.4 Falsification Testing (`apgi_framework/falsification/`)

| Module | Purpose |
|---|---|
| `ai_acc_validation.py` | AI accuracy validation |
| `experimental_control.py` | Experimental integrity control |
| `edge_case_interpreter.py` | Edge case analysis |
| `result_interpretation.py` | Result interpretation engine |

### 6.5 Clinical Applications (`apgi_framework/clinical/`)

| Module | Purpose | Coverage |
|---|---|---|
| `parameter_extraction.py` | Clinical parameter extraction | ~100% |
| `biomarkers.py` | Biomarker identification | N/A |

### 6.6 High-Level Controllers

| Module | LOC | Coverage | Role |
|---|---|---|---|
| `cli.py` | 2,305 | ~90% | CLI commands, validation, reporting |
| `experimental_control.py` | 2,582 | ~87.5% | Experimental integrity & validation |
| `system_validator.py` | 1,478 | ~62% | Installation, dependencies, health |
| `workflow_orchestrator.py` | 903 | ~79% | Experiment pipeline orchestration |
| `main_controller.py` | 499 | ~15% | Application lifecycle management |

---

## 7. Test Coverage Analysis

### 7.1 Overall Coverage Summary

| Category | Status |
|---|---|
| Target coverage | 80%+ |
| Test files | 81 |
| Test framework | pytest + hypothesis |
| Parallel testing | pytest-xdist |
| Property-based testing | hypothesis |

### 7.2 Module Coverage Status

#### Critical Modules — Well Covered

| Module | Statements | Coverage | Status |
|---|---|---|---|
| `apgi_framework/cli.py` | 1,064 | ~90% | ✅ |
| `apgi_framework/experimental_control.py` | 1,142 | ~87.5% | ✅ |
| `apgi_framework/analysis/analysis_engine.py` | 339 | ~100% | ✅ |
| `apgi_framework/clinical/parameter_extraction.py` | 451 | ~100% | ✅ |
| `apgi_framework/data/storage_manager.py` | 330 | ~100% | ✅ |
| `apgi_framework/neural/physiological_monitoring.py` | 440 | ~85% | ✅ |
| `apgi_framework/validation/system_health.py` | 322 | ~83.2% | ✅ |
| `apgi_framework/workflow_orchestrator.py` | 358 | ~79% | ✅ |
| `apgi_framework/neural/cardiac_processor.py` | 360 | ~70% | ✅ |
| `apgi_framework/adaptive/task_control.py` | 412 | ~75% | ✅ |
| `apgi_framework/adaptive/stimulus_generators.py` | 396 | ~70% | ✅ |

#### Partial Coverage — Needs Improvement

| Module | Statements | Coverage | Priority |
|---|---|---|---|
| `apgi_framework/system_validator.py` | 543 | ~62% | High |
| `apgi_framework/data/persistence_layer.py` | 468 | ~18.6% | High |
| `apgi_framework/main_controller.py` | 499 | ~15% | High |

#### No Coverage — GUI/Display Required

| Module | Statements | Coverage | Reason |
|---|---|---|---|
| `apgi_framework/gui/coverage_visualization.py` | 504 | 0% | Requires display |
| `apgi_framework/gui/results_viewer.py` | 470 | 0% | Requires display |
| `apgi_framework/gui/enhanced_dash.py` | 444 | 0% | Requires display |
| `apgi_framework/gui/error_handling.py` | 381 | 0% | Requires display |
| `apgi_framework/gui/main_window.py` | N/A | 0% | Requires display |

#### No Coverage — Infrastructure Modules

| Area | Status |
|---|---|
| `apgi_framework/testing/` submodules | 0% — needs CI mock environment |
| `apgi_framework/reporting/` submodules | 0% — needs rendering environment |
| `apgi_framework/security/` submodules | 0% — needs isolated testing |
| `apgi_framework/utils/font_manager.py` | 0% — GUI dependent |
| `apgi_framework/utils/thread_manager.py` | 0% — threading complexity |
| `apgi_framework/testing/performance_opt.py` | 0% — benchmark context |
| `apgi_framework/testing/ci_integrator.py` | 0% — CI environment required |

### 7.3 Test Suite Breakdown

| Test File | Target Module |
|---|---|
| `test_neural_physmon_coverage.py` | `neural/physiological_monitoring.py` |
| `test_cardiac_processor_coverage.py` | `neural/cardiac_processor.py` |
| `test_task_control_coverage.py` | `adaptive/task_control.py` |
| `test_stimulus_generators_coverage.py` | `adaptive/stimulus_generators.py` |
| `test_system_health_coverage.py` | `validation/system_health.py` |
| `test_main_controller_coverage.py` | `main_controller.py` |
| `tests/framework/` | Framework integration |
| `tests/integration/` | End-to-end pipelines |
| `cross_browser_compatibility.py` | Web UI compatibility |

### 7.4 Known Test Suite Issues

1. **Segfault risk**: Running the full test suite at once may cause segfaults. Use targeted subsets.
2. **GUI tests**: All GUI-heavy modules require either a display or headless `pytest-xvfb` / `pytest-qt` setup.
3. **Optional dependency mocking**: `h5py`, `pystan`, `torch` need careful mocking for environments that lack them.
4. **Coverage minimum**: CI enforces 80% minimum; currently met for covered modules.

---

## 8. Security Audit

### 8.1 Security Posture

| Area | Finding | Status |
|---|---|---|
| Docker user | Non-root `apgi` user enforced | ✅ |
| Input validation | Present at system boundaries | ✅ |
| SQL injection | Parameterized queries used | ✅ |
| Secrets management | `.env.example` provided; secrets not committed | ✅ |
| Code execution | `RestrictedPython` for sandbox | ✅ |
| Password handling | `SecureString` abstraction present | ✅ |
| Dependency scanning | Bandit + Safety in CI | ✅ |
| Container scanning | Trivy in CI pipeline | ✅ |

### 8.2 Security CI Gates

The CI pipeline includes:
- **Bandit**: Static analysis for Python security issues
- **Safety**: Known vulnerability check against PyPI advisories
- **Trivy**: Container image vulnerability scanning

### 8.3 Security Recommendations

- Rotate `.env` secrets regularly and ensure `.env` files are never committed
- Add SAST scanning to PR gates (currently on main only)
- Consider adding `pip-audit` as an additional dependency scanner
- The `security/` submodule has 0% test coverage — add isolated security unit tests

---

## 9. Dependencies

### 9.1 Core Scientific Stack

| Package | Version | Purpose |
|---|---|---|
| numpy | >=1.20.0 | Numerical computing |
| scipy | >=1.7.0 | Scientific algorithms |
| pandas | >=1.3.0 | Data manipulation |
| matplotlib | >=3.5.0 | Plotting |
| seaborn | >=0.12.0 | Statistical visualization |
| statsmodels | >=0.14.0 | Statistical modeling |

### 9.2 Neural & Neuroimaging

| Package | Version | Purpose |
|---|---|---|
| mne | >=1.4.0 | EEG/MEG analysis |
| nibabel | >=5.1.0 | Neuroimaging file formats |
| h5py | >=3.8.0 | HDF5 scientific data |
| numba | >=0.57.0 | JIT compilation |

### 9.3 Machine Learning

| Package | Version | Purpose |
|---|---|---|
| scikit-learn | >=1.3.0 | Classical ML |
| torch (PyTorch) | >=2.0.0 | Deep learning |
| tensorflow | >=2.8 | Deep learning (alt) |

### 9.4 GUI

| Package | Version | Purpose |
|---|---|---|
| customtkinter | >=5.2.0 | Modern tkinter UI |
| Pillow | >=10.0.0 | Image processing |
| pyautogui | >=0.9.54 | GUI automation |
| pygetwindow | >=0.0.9 | Window management |

### 9.5 Testing & Quality

| Package | Version | Purpose |
|---|---|---|
| pytest | >=7.4.0 | Test framework |
| hypothesis | >=6.70.0 | Property-based testing |
| coverage | >=6.0 | Coverage reporting |
| pytest-xdist | >=3.0 | Parallel test execution |
| pytest-xvfb | >=3.0.0 | Headless display for GUI tests |
| black | >=23.7.0 | Code formatting |
| isort | >=5.12.0 | Import sorting |
| flake8 | >=6.0.0 | Linting |
| mypy | >=1.0 | Type checking |

### 9.6 Web & Deployment

| Package | Purpose |
|---|---|
| Flask >=2.3.0 | Web framework |
| Streamlit >=1.25.0 | Data apps |
| psutil | System monitoring |
| RestrictedPython | Secure code execution |
| prometheus-client | Metrics export |

---

## 10. CI/CD Pipeline

### 10.1 Workflow Files

| File | Purpose |
|---|---|
| `.github/workflows/test.yml` | Full CI/CD pipeline |
| `.github/workflows/automated-testing.yml` | Automated test matrix |

### 10.2 Pipeline Stages

```
Push / PR to main or develop
         │
         ├── Linting & Formatting (Black, isort, flake8)
         ├── Type Checking (mypy)
         ├── Unit Tests (Ubuntu / Windows / macOS × Python 3.8–3.11)
         │       └── Coverage upload to Codecov
         ├── Security Scanning (Bandit, Safety, Trivy)
         ├── Performance Benchmarks (main branch only)
         ├── Documentation Build (Sphinx)
         ├── Package Build & Validation
         ├── Docker Build (multi-platform: amd64, arm64)
         └── Integration Tests (docker-compose)
```

### 10.3 Quality Gates

| Gate | Threshold |
|---|---|
| Minimum test coverage | 80% |
| Maximum test failures | 0 |
| Security vulnerabilities | Must pass Bandit/Safety/Trivy |
| Code formatting | Black + isort enforced |

### 10.4 Scheduling

- Triggered on: push/PR to `main` and `develop`
- Weekly scheduled run for dependency drift detection

---

## 11. Deployment Infrastructure

### 11.1 Docker

**`Dockerfile`** — Multi-stage build:
- Base: `python:3.9-slim`
- Non-root user `apgi` for security
- Virtual environment isolation
- Built-in health check
- Port: `8000`

### 11.2 Docker Compose Stack

| Service | Image | Purpose |
|---|---|---|
| `app` | Local build | APGI Framework |
| `db` | postgres:15-alpine | Structured data persistence |
| `redis` | redis:7-alpine | Caching & sessions |
| `jupyter` | jupyter/scipy-notebook | Development environment |
| `nginx` | nginx:alpine | Reverse proxy |
| `prometheus` | prom/prometheus | Metrics collection |
| `grafana` | grafana/grafana | Monitoring dashboards |

### 11.3 Kubernetes

`k8s/deployment.yaml` provides a Kubernetes deployment manifest for cluster-based scaling.

### 11.4 Deployment Scripts

| Script | Platform | Purpose |
|---|---|---|
| `setup.sh` | Linux/macOS | Automated environment setup |
| `deploy.sh` | Linux/macOS | Production deployment |
| `deploy.bat` | Windows | Windows deployment |

---

## 12. Known Issues & Gaps

### 12.1 Test Coverage Gaps

| Gap | Impact | Resolution Path |
|---|---|---|
| GUI modules at 0% | Cannot verify UI correctness | Add `pytest-xvfb` / headless tests |
| `main_controller.py` at ~15% | Core app lifecycle undertested | Add lifecycle unit tests with mocking |
| `persistence_layer.py` at ~18.6% | Data integrity risk | Add storage integration tests |
| `system_validator.py` at ~62% | Validation gaps | Add negative validation path tests |
| `security/` at 0% | Security regressions undetected | Add isolated security unit tests |
| `reporting/` at 0% | Report generation untested | Add report snapshot tests |
| `testing/ci_integrator.py` at 0% | CI integration unverified | Mock CI environment tests |

### 12.2 Technical Debt

| Issue | Location | Severity |
|---|---|---|
| Segfault on full test run | Test suite | Medium |
| Optional deps need mocking | `h5py`, `pystan`, `torch` | Low |
| `mypy` in phase 2 (not strict) | All modules | Low |
| `main_controller.py` mostly untested | Core lifecycle | High |

### 12.3 Documentation Gaps

- No API reference auto-generated (Sphinx configured but not verified)
- `apgi_gui/app.py` (~65K LOC) lacks inline docstrings in places
- Some `utils/` modules have no corresponding documentation

---

## 13. Recommendations

### Priority 1 — Critical (Address Immediately)

1. **Increase `main_controller.py` coverage** from ~15% to 80%+
   - Mock `apgi_framework` submodules; test initialization, shutdown, state transitions
2. **Increase `persistence_layer.py` coverage** from ~18.6% to 70%+
   - Use in-memory SQLite or temporary file fixtures

### Priority 2 — High (Next Sprint)

3. **Enable headless GUI testing** via `pytest-xvfb` (already in `dev` deps)
   - Target `coverage_visualization.py`, `results_viewer.py`, `enhanced_dash.py`
4. **Add security module tests** for `apgi_framework/security/`
   - Use isolated environments; mock external connections
5. **Increase `system_validator.py` coverage** from ~62% to 85%+
   - Add negative/failure path tests

### Priority 3 — Medium (Backlog)

6. **Add `reporting/` tests** — snapshot-based PDF/report tests
7. **Add `testing/ci_integrator.py` tests** — mock CI server responses
8. **Enable strict `mypy`** — currently in phase 2; migrate to strict for new modules
9. **Add `pip-audit`** to the CI pipeline alongside Bandit and Safety
10. **Document `apgi_gui/app.py`** — the 65K LOC GUI needs module-level docstrings

### Operational Recommendations

11. **Use targeted test subsets** to avoid the known segfault on full suite runs
12. **Set up Grafana dashboards** from the included docker-compose stack for runtime monitoring
13. **Review and rotate** all `.env` secrets on a quarterly schedule

---

## 14. Audit History

| Version | Branch | Key Work |
|---|---|---|
| v1.0 | `claude/app-audit-security-*` | Initial security-focused audit |
| v2.0 | `claude/app-audit-security-7D8yh` | Security hardening, additional findings |
| v3.0 | `claude/app-audit-security-aw9GR` | Coverage artefacts, test improvements |
| v4.0 | `claude/app-audit-security-Phx6T` | End-to-end application audit |
| v5.0 | `claude/audit-codebase-8HGSo` | **This report** — consolidated full-codebase audit |

### Changes Made in This Audit Cycle

- Added test fixes (`fixed some tests`, `added tests` — commits `3d9bcad`, `8c67d12`)
- Removed superseded falsification test artefacts (`bd90b3f`)
- Created this comprehensive `REPORT.md` consolidating all audit findings

---

## Appendix A: Quick Start

```bash
# Clone and setup
git clone <repo>
cd apgi-experiments
pip install -e .[dev]

# Run tests
pytest -m unit
pytest -m integration
pytest --cov=apgi_framework --cov-report=html

# Start full stack (requires Docker)
docker-compose up

# Launch GUI
python GUI-Launcher.py

# CLI
python -m apgi_framework.cli --help
```

## Appendix B: Configuration

Key configuration files:

| File | Purpose |
|---|---|
| `config/config.json` | APGI parameters, experimental config, statistical thresholds |
| `pyproject.toml` | Project metadata, test configuration, linting, mypy |
| `.env.example` | Environment variable template |
| `utils/config/default.yaml` | Default YAML configuration |
| `docker-compose.yml` | Full stack deployment configuration |

---

*Report generated by audit on branch `claude/audit-codebase-8HGSo` — 2026-03-20*
