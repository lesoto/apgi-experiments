"""
Modern Setup Script for APGI Framework

This setup script provides modern Python packaging with pyproject.toml support.
Uses current best practices and avoids deprecated setuptools parameters.
"""

import sys
from pathlib import Path

from setuptools import find_packages, setup  # type: ignore

# Handle --auto flag for compatibility with automated scripts
if "--auto" in sys.argv:
    sys.argv.remove("--auto")

# Modern packaging - check for pyproject.toml first
PYPROJECT_TOML = Path(__file__).parent / "pyproject.toml"


def read_requirements():
    """Read requirements from requirements.txt."""
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, "r", encoding="utf-8") as f:
            return [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]
    return []


def get_version():
    """Get version from pyproject.toml or VERSION file."""
    if PYPROJECT_TOML.exists():
        try:
            import toml  # type: ignore

            config = toml.load(PYPROJECT_TOML)
            return config.get("project", {}).get("version", "0.1.0")
        except ImportError:
            pass

    version_file = Path(__file__).parent / "VERSION"
    if version_file.exists():
        return version_file.read_text().strip()

    return "0.1.0"


def get_long_description():
    """Get long description from README."""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return "APGI Framework - Adaptive Precision and Generalized Intelligence"


# Modern setup configuration
setup_config = {
    "name": "apgi-framework",
    "version": get_version(),
    "description": "Adaptive Precision and Generalized Intelligence Framework",
    "long_description": get_long_description(),
    "long_description_content_type": "text/markdown",
    "author": "APGI Framework Team",
    "author_email": "contact@apgi-framework.org",
    "url": "https://github.com/apgi-framework/apgi-experiments",
    "packages": find_packages(exclude=["tests*", "examples*", "docs*"]),
    "python_requires": ">=3.8",
    "install_requires": read_requirements(),
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    "keywords": [
        "machine-learning",
        "neuroscience",
        "consciousness",
        "active-inference",
    ],
    "project_urls": {
        "Bug Reports": "https://github.com/apgi-framework/apgi-experiments/issues",
        "Source": "https://github.com/apgi-framework/apgi-experiments",
        "Documentation": "https://apgi-framework.readthedocs.io/",
    },
    "include_package_data": True,
    "package_data": {
        "apgi_framework": ["config/*.yaml", "config/*.json", "data/*.csv"],
    },
}

# Only run setup if not using pyproject.toml
if not PYPROJECT_TOML.exists():
    setup(**setup_config)
else:
    # For pyproject.toml, just provide minimal setup for compatibility
    setup(
        name=setup_config["name"],
        version=setup_config["version"],
        packages=setup_config["packages"],
    )
