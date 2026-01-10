"""
Setup script for APGI Framework
"""

import os
from setuptools import setup, find_packages

# Read README.md if it exists, otherwise use basic description
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "Active Precision Gating and Interoception (APGI) Framework for consciousness research and falsification testing."

# Read requirements.txt if it exists
requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
if os.path.exists(requirements_path):
    with open(requirements_path, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "numpy>=1.20.0",
        "scipy>=1.7.0",
        "matplotlib>=3.5.0",
        "pandas>=1.3.0",
    ]

setup(
    name="apgi-framework",
    version="1.0.0",
    author="APGI Research Team",
    author_email="research@apgi.org",
    description="Active Precision Gating and Interoception Framework for Consciousness Research",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/apgi-research/apgi-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "gui": [
            "flask>=2.0",
            "flask-socketio>=5.0",
            "plotly>=5.0",
            "bootstrap-flask>=2.0",
        ],
        "ml": [
            "scikit-learn>=1.0",
            "tensorflow>=2.8",
            "torch>=1.10",
        ],
    },
    entry_points={
        "console_scripts": [
            "apgi-gui=apgi_framework.cli:main",
            "apgi-deploy=apgi_framework.deployment.automation:main",
            "apgi-dashboard=apgi_framework.gui.interactive_dashboard:main",
        ],
    },
    include_package_data=True,
    package_data={
        "apgi_framework": [
            "gui/templates/*.html",
            "gui/static/*",
            "config/*.json",
            "data/*.json",
        ],
    },
    zip_safe=False,
)
