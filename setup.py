"""
Comprehensive Setup Script for APGI Framework Test Enhancement

This setup script provides complete installation and configuration for the
APGI Framework with comprehensive test enhancement capabilities.

Requirements: System deployment
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        self.execute(self._post_install, [], msg="Running post-install tasks")

    def _post_install(self):
        """Execute post-installation tasks."""
        print("Running APGI Framework post-installation setup...")

        # Create necessary directories
        self._create_directories()

        # Install optional dependencies based on user choice
        self._install_optional_dependencies()

        # Validate installation
        self._validate_installation()

        print("APGI Framework installation completed successfully!")

    def _create_directories(self):
        """Create necessary directories for the framework."""
        directories = [
            "logs",
            "test_reports",
            "coverage_reports",
            "session_data",
            "apgi_outputs",
            "data/examples",
            "config",
        ]

        for directory in directories:
            dir_path = Path.cwd() / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")

    def _install_optional_dependencies(self):
        """Install optional dependencies based on user requirements."""
        try:
            # Check if GUI dependencies should be installed
            install_gui = (
                input("Install GUI dependencies (PySide6)? [y/N]: ")
                .lower()
                .startswith("y")
            )
            if install_gui:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "PySide6>=6.0"]
                )
                print("GUI dependencies installed successfully")

            # Check if development dependencies should be installed
            install_dev = (
                input("Install development dependencies? [y/N]: ")
                .lower()
                .startswith("y")
            )
            if install_dev:
                dev_packages = [
                    "pytest>=7.0",
                    "pytest-cov>=4.0",
                    "pytest-xdist>=3.0",
                    "hypothesis>=6.0",
                    "black>=22.0",
                    "flake8>=5.0",
                    "mypy>=1.0",
                ]
                for package in dev_packages:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", package]
                    )
                print("Development dependencies installed successfully")

        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install optional dependencies: {e}")
        except KeyboardInterrupt:
            print("Installation of optional dependencies skipped by user")

    def _validate_installation(self):
        """Validate the installation."""
        try:
            # Test import of main modules
            import apgi_framework

            print("✓ Core framework import successful")

            # Test test enhancement modules
            from apgi_framework.testing import main

            print("✓ Test enhancement modules import successful")

            # Check Python version
            if sys.version_info >= (3, 8):
                print(
                    f"✓ Python version {sys.version_info.major}.{sys.version_info.minor} is supported"
                )
            else:
                print(
                    f"⚠ Python version {sys.version_info.major}.{sys.version_info.minor} may not be fully supported"
                )

            print("Installation validation completed successfully!")

        except ImportError as e:
            print(f"⚠ Warning: Some modules failed to import: {e}")


class PostDevelopCommand(develop):
    """Post-installation for development mode."""

    def run(self):
        develop.run(self)
        self.execute(self._post_develop, [], msg="Running post-develop tasks")

    def _post_develop(self):
        """Execute post-development installation tasks."""
        print("Setting up APGI Framework for development...")

        # Create development directories
        dev_directories = [
            "logs",
            "test_reports",
            "coverage_reports",
            "session_data",
            "apgi_outputs",
            "data/examples",
            "config",
            ".pytest_cache",
            "benchmark_results",
        ]

        for directory in dev_directories:
            dir_path = Path.cwd() / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        # Install development dependencies
        try:
            dev_packages = [
                "pytest>=7.0",
                "pytest-cov>=4.0",
                "pytest-xdist>=3.0",
                "hypothesis>=6.0",
                "black>=22.0",
                "flake8>=5.0",
                "mypy>=1.0",
                "pre-commit>=2.0",
            ]

            for package in dev_packages:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])

            print("Development environment setup completed!")

        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to install development dependencies: {e}")


def get_version():
    """Get version from version file or default."""
    version_file = Path(__file__).parent / "apgi_framework" / "__version__.py"
    if version_file.exists():
        with open(version_file, "r") as f:
            exec(f.read())
            return locals().get("__version__", "1.0.0")
    return "1.0.0"


def get_long_description():
    """Get long description from README."""
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return """
APGI Framework Test Enhancement

A comprehensive testing solution for the Active Precision Gating and Interoception (APGI) 
Framework, providing advanced test execution, coverage analysis, and reporting capabilities.

Features:
- Comprehensive test suite analysis and validation
- Advanced coverage measurement and gap identification  
- Property-based testing with Hypothesis integration
- GUI and CLI interfaces for test execution
- Automated CI/CD integration
- Performance optimization and resource management
- Detailed reporting and visualization
"""


def get_requirements():
    """Get requirements from requirements.txt."""
    requirements_path = Path(__file__).parent / "requirements.txt"
    if requirements_path.exists():
        with open(requirements_path, "r", encoding="utf-8") as fh:
            return [
                line.strip() for line in fh if line.strip() and not line.startswith("#")
            ]

    # Fallback core requirements
    return [
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
        "coverage>=6.0",
        "pytest>=7.0",
        "hypothesis>=6.0",
    ]


def check_system_requirements():
    """Check system requirements before installation."""
    print("Checking system requirements...")

    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)

    # Check platform
    supported_platforms = ["Windows", "Linux", "Darwin"]  # Darwin = macOS
    current_platform = platform.system()
    if current_platform not in supported_platforms:
        print(f"Warning: Platform {current_platform} may not be fully supported")

    # Check available disk space (basic check)
    try:
        import shutil

        free_space = shutil.disk_usage(".").free / (1024**3)  # GB
        if free_space < 1.0:  # Less than 1GB
            print("Warning: Low disk space available")
    except:
        pass

    print("✓ System requirements check completed")


# Run system requirements check
check_system_requirements()

setup(
    name="apgi-framework-test-enhancement",
    version=get_version(),
    author="APGI Research Team",
    author_email="research@apgi.org",
    description="Comprehensive Test Enhancement for APGI Framework",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/apgi-research/apgi-framework",
    project_urls={
        "Bug Reports": "https://github.com/apgi-research/apgi-framework/issues",
        "Source": "https://github.com/apgi-research/apgi-framework",
        "Documentation": "https://apgi-framework.readthedocs.io/",
    },
    packages=find_packages(exclude=["tests*", "benchmarks*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
    ],
    keywords="testing, coverage, property-based-testing, consciousness-research, apgi",
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "gui": [
            "PySide6>=6.0",
        ],
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-xdist>=3.0",
            "hypothesis>=6.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "pre-commit>=2.0",
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
        "performance": [
            "memory-profiler>=0.60",
            "psutil>=5.8",
            "line-profiler>=3.0",
        ],
        "ml": [
            "scikit-learn>=1.0",
            "tensorflow>=2.8",
            "torch>=1.10",
        ],
        "neural": [
            "mne>=1.0",
            "scipy>=1.7.0",
            "scikit-learn>=1.0",
        ],
        "all": [
            "PySide6>=6.0",
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-xdist>=3.0",
            "hypothesis>=6.0",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
            "memory-profiler>=0.60",
            "psutil>=5.8",
            "mne>=1.0",
            "scikit-learn>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "apgi-test=apgi_framework.testing.main:main",
            "apgi-test-gui=apgi_framework.testing.main:main",
            "apgi-coverage=apgi_framework.testing.main:main",
            "apgi-deploy=apgi_framework.deployment.automation:main",
            "apgi-dashboard=apgi_framework.gui.interactive_dashboard:main",
        ],
    },
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
    include_package_data=True,
    package_data={
        "apgi_framework": [
            "gui/templates/*.html",
            "gui/static/*",
            "config/*.json",
            "config/*.yaml",
            "data/*.json",
            "testing/templates/*",
        ],
    },
    data_files=[
        ("config", ["config/test_config_template.json"]),
        ("docs", ["docs/README.md"]),
    ],
    zip_safe=False,
    test_suite="tests",
    tests_require=[
        "pytest>=7.0",
        "pytest-cov>=4.0",
        "hypothesis>=6.0",
    ],
)
