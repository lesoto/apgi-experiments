# Documentation Organization Summary

## 📁 Files Moved to docs/ Folder

### ✅ Successfully Organized

All stray `.md` files have been moved from throughout the project into the centralized `docs/` folder with proper organization:

## 🗂️ New Documentation Structure

```text
docs/
├── index.md                           # Main documentation index
├── README.md                          # General documentation readme
├── DOCUMENTATION.md                    # Documentation guidelines
├── EXPERIMENTS_GUIDE.md               # Experiments guide
├── TUTORIALS.md                       # Tutorials overview
├── USER_GUIDE.md                      # User guide
│
├── api/                               # API documentation
│   └── index.md
│
├── benchmarks/                        # Performance benchmarks
│   └── README.md                      # Moved from benchmarks/
│
├── developer/                         # Developer documentation
│   ├── error-handling.md
│   ├── gui-integration.md
│   ├── index.md
│   ├── logging-configuration.md
│   └── validation-guide.md
│
├── examples/                          # Code examples
│   ├── index.md                       # Moved from examples/
│   ├── data/README.md                 # Moved from examples/data/
│   └── framework_examples/README.md   # Moved from examples/framework_examples/
│
├── experimental/                      # Experimental features
│   ├── index.md
│   ├── parameter-validation-features.md
│   ├── parameter-validation-guide.md
│   └── validation-summary.md
│
├── project/                           # Project management
│   ├── TODO.md                        # Moved from root
│   └── TODO-old.md                     # Moved from root
│
├── research/                          # Research documentation
│   ├── ai_benchmarking/README.md      # Moved from research/ai_benchmarking/
│   ├── clinical_biomarkers/README.md  # Moved from research/clinical_biomarkers/
│   ├── cognitive_tasks/README.md      # Moved from research/cognitive_tasks/
│   └── core_mechanisms/README.md      # Moved from research/core_mechanisms/
│
├── researcher/                        # Researcher guides
│   ├── bayesian-modeling.md
│   ├── clinical-parameter-extraction.md
│   ├── falsification-methodology.md
│   ├── framework-falsification-testing.md
│   ├── parameter-estimation.md
│   └── testable-predictions.md
│
├── technical/                         # Technical documentation
│   ├── apgi-equation.md
│   ├── neural-signatures.md
│   ├── pupillometry.md
│   └── signal-processing.md
│
└── user/                              # User documentation
    ├── cli-reference.md
    ├── deployment_guide.md
    ├── examples.md
    ├── falsification-gui.md
    ├── gui-guide.md
    ├── gui-readme.md
    ├── quick-start.md
    ├── quick_start_guide.md
    ├── results-interpretation.md
    ├── step_by_step_tutorials.md
    ├── troubleshooting.md
    └── user-guide.md
```

## 📋 Files Moved

| Original Location                              | New Location                              | Purpose                                 |
|-----------------------------------------------|-------------------------------------------|-----------------------------------------|
| `TODO.md`                                     | `docs/project/TODO.md`                     | Project tasks and roadmap                |
| `TODO-old.md`                                 | `docs/project/TODO-old.md`                 | Previous TODO backup                     |
| `benchmarks/README.md`                        | `docs/benchmarks/README.md`                | Benchmark documentation                  |
| `examples/data/README.md`                     | `docs/examples/data/README.md`             | Sample data documentation                |
| `examples/framework_examples/README.md`       | `docs/examples/framework_examples/README.md` | Framework examples                      |
| `examples/index.md`                           | `docs/examples/index.md`                   | Examples index                          |
| `research/ai_benchmarking/README.md`          | `docs/research/ai_benchmarking/README.md`   | AI benchmarking research                 |
| `research/clinical_biomarkers/README.md`      | `docs/research/clinical_biomarkers/README.md` | Clinical biomarkers research            |
| `research/cognitive_tasks/README.md`          | `docs/research/cognitive_tasks/README.md`   | Cognitive tasks research                  |
| `research/core_mechanisms/README.md`           | `docs/research/core_mechanisms/README.md`    | Core mechanisms research                  |

## 🧹 Cleanup Actions

- ✅ Removed `.pytest_cache/` directory (cache files)
- ✅ Created organized directory structure
- ✅ Moved all stray `.md` files to appropriate locations
- ✅ Created comprehensive main index (`docs/index.md`)

## 🎯 Benefits

1. **Centralized Documentation**: All documentation now in one location
2. **Logical Organization**: Files grouped by purpose and audience
3. **Easy Navigation**: Clear hierarchy and main index
4. **Better Maintenance**: Easier to update and manage documentation
5. **Improved Discoverability**: Users can easily find relevant documentation

## 📝 Next Steps

1. Update any internal links that reference the old file locations
2. Update build scripts or documentation generators
3. Verify all links work correctly in the new structure
4. Consider adding a documentation search mechanism

---

**Status**: ✅ Complete 
**Files Moved**: 10  
**Directories Created**: 8  
**Main Index**: docs/index.md
