#!/usr/bin/env python3
"""
Dependency Verification Script for APGI Framework

This script checks if all required dependencies are properly installed
and can be imported. It provides detailed feedback on missing packages.

Usage:
    python check_dependencies.py
"""

import sys
import importlib
from typing import List, Dict, Tuple

# Core dependencies that must be available
CORE_DEPENDENCIES = [
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "torch",
    "customtkinter",
    "numba",
    "h5py",
    "statsmodels",
    "flask",
    "flask_socketio",
    "pytest",
    "jupyter",
    "streamlit",
    "psutil",
    "requests",
]

# Optional dependencies with warnings
OPTIONAL_DEPENDENCIES = [
    "pyautogui",
    "pygetwindow",
    "PIL",  # Pillow
    "cv2",  # opencv-python
    "scikit-learn",
    "seaborn",
    "plotly",
    "mne",
    "nibabel",
    "torchvision",
    "torchaudio",
]


def check_import(package_name: str) -> Tuple[bool, str]:
    """Check if a package can be imported."""
    try:
        importlib.import_module(package_name)
        return True, "✓ Successfully imported"
    except ImportError as e:
        return False, f"✗ Import failed: {e}"
    except Exception as e:
        return False, f"✗ Error: {e}"


def check_dependencies() -> Dict[str, Dict[str, Tuple[bool, str]]]:
    """Check all dependencies and return results."""
    results = {"core": {}, "optional": {}}

    print("🔍 Checking APGI Framework Dependencies")
    print("=" * 50)

    # Check core dependencies
    print("\n📦 CORE DEPENDENCIES (Required)")
    print("-" * 30)

    core_failed = []
    for dep in CORE_DEPENDENCIES:
        success, message = check_import(dep)
        results["core"][dep] = (success, message)
        status = "✓" if success else "✗"
        print(f"  {status} {dep:<20} {message}")
        if not success:
            core_failed.append(dep)

    # Check optional dependencies
    print("\n📦 OPTIONAL DEPENDENCIES")
    print("-" * 30)

    optional_failed = []
    for dep in OPTIONAL_DEPENDENCIES:
        success, message = check_import(dep)
        results["optional"][dep] = (success, message)
        status = "✓" if success else "✗"
        print(f"  {status} {dep:<20} {message}")
        if not success:
            optional_failed.append(dep)

    # Check APGI framework itself
    print("\n🏗️  APGI FRAMEWORK")
    print("-" * 30)

    framework_success = True
    framework_tests = [
        ("config", "apgi_framework.config"),
        ("main_controller", "apgi_framework.main_controller"),
        ("cli", "apgi_framework.cli"),
    ]

    for name, module in framework_tests:
        success, message = check_import(module)
        status = "✓" if success else "✗"
        print(f"  {status} {name:<20} {message}")
        if not success:
            framework_success = False

    # Summary
    print("\n📊 SUMMARY")
    print("=" * 50)

    total_core = len(CORE_DEPENDENCIES)
    passed_core = total_core - len(core_failed)

    total_optional = len(OPTIONAL_DEPENDENCIES)
    passed_optional = total_optional - len(optional_failed)

    print(f"Core Dependencies:    {passed_core}/{total_core} passed")
    print(f"Optional Dependencies: {passed_optional}/{total_optional} passed")
    print(f"APGI Framework:       {'✓' if framework_success else '✗'}")

    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)

    if core_failed:
        print("❌ CRITICAL: Missing core dependencies!")
        print("   Run: pip install -r requirements.txt")
        print(f"   Missing: {', '.join(core_failed)}")
        return False

    if not framework_success:
        print("⚠️  WARNING: APGI Framework import issues")
        print("   Run: pip install -e .")
        return False

    if optional_failed:
        print(f"⚠️  WARNING: {len(optional_failed)} optional dependencies missing")
        print("   Some features may not work properly")
        print(f"   Missing: {', '.join(optional_failed)}")

    print("✅ All critical dependencies are installed!")
    print("🚀 APGI Framework is ready to use!")

    return True


def main():
    """Main entry point."""
    try:
        success = check_dependencies()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Dependency check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
