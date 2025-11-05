import os
import shutil
from pathlib import Path

def create_directories():
    """Create the necessary directory structure."""
    base_dir = Path(__file__).parent
    
    # Main directories
    dirs = [
        "experiments/interoceptive_gating",
        "experiments/somatic_marker_priming",
        "experiments/metabolic_cost",
        "experiments/ai_benchmarking",
        "experiments/clinical_biomarkers",
        "core/models",
        "core/analysis",
        "core/utils",
        "data/raw",
        "data/processed",
        "docs"
    ]
    
    for dir_path in dirs:
        full_path = base_dir / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        (full_path / "__init__.py").touch()
    
    # Create empty __init__.py in main directories
    for dir_name in ["experiments", "core", "data"]:
        (base_dir / dir_name / "__init__.py").touch()

def organize_existing_files():
    """Move existing Python files to their appropriate locations."""
    base_dir = Path(__file__).parent
    
    # Map of files to their target locations
    file_mapping = {
        "ipi_agent.py": "core/models/ipi_agent.py",
        "phase-transition.py": "core/models/phase_transition.py",
        "grid-agent.py": "experiments/ai_benchmarking/grid_agent.py",
        "hierarchical-predictive.py": "core/models/hierarchical_predictive.py",
        "active-inference.py": "core/models/active_inference.py",
        "threshold-phenomenon.py": "core/analysis/threshold_phenomenon.py",
        "surprise-dynamics.py": "core/analysis/surprise_dynamics.py"
    }
    
    for src, dst in file_mapping.items():
        src_path = base_dir / src
        dst_path = base_dir / dst
        if src_path.exists() and not dst_path.exists():
            shutil.move(str(src_path), str(dst_path))

def main():
    print("Creating directory structure...")
    create_directories()
    
    print("Organizing existing files...")
    organize_existing_files()
    
    print("\nProject structure created successfully!")
    print("Next steps:")
    print("1. Create a virtual environment: python -m venv venv")
    print("2. Activate the virtual environment")
    print("3. Install dependencies: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
