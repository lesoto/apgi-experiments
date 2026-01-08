#!/usr/bin/env python3
"""
Test runner script for APGI Framework experiments.

This script sets up the proper Python path and runs pytest with the correct
configuration to avoid ModuleNotFoundError issues.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_python_path():
    """Set up the Python path to include the project root."""
    # Get the project root directory (go up one level from tools/)
    project_root = Path(__file__).parent.parent.absolute()
    
    # Add project root to Python path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Set PYTHONPATH environment variable
    env = os.environ.copy()
    if 'PYTHONPATH' in env:
        env['PYTHONPATH'] = f"{project_root}:{env['PYTHONPATH']}"
    else:
        env['PYTHONPATH'] = str(project_root)
    
    return env

def run_pytest(args=None):
    """Run pytest with proper environment setup.
    
    Args:
        args: List of pytest arguments (optional)
    """
    env = setup_python_path()
    
    # Default pytest arguments
    if args is None:
        args = [
            'tests/',
            '-v',
            '--tb=short',
            '--color=yes'
        ]
    
    # Construct pytest command
    cmd = [sys.executable, '-m', 'pytest'] + args
    
    print(f"Running: {' '.join(cmd)}")
    print(f"PYTHONPATH: {env['PYTHONPATH']}")
    print("-" * 60)
    
    # Run pytest
    try:
        result = subprocess.run(cmd, env=env, cwd=Path(__file__).parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running pytest: {e}")
        return 1

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run APGI Framework tests')
    parser.add_argument('pytest_args', nargs='*', help='Arguments to pass to pytest')
    parser.add_argument('--coverage', action='store_true', help='Run with coverage')
    parser.add_argument('--specific', help='Run specific test file')
    
    args = parser.parse_args()
    
    # Build pytest arguments
    pytest_args = []
    
    if args.specific:
        pytest_args.append(args.specific)
    else:
        pytest_args.append('tests/')
    
    # Add verbosity and traceback options
    pytest_args.extend(['-v', '--tb=short', '--color=yes'])
    
    # Add coverage if requested
    if args.coverage:
        pytest_args.extend([
            '--cov=apgi_framework',
            '--cov=research', 
            '--cov-report=html',
            '--cov-report=term-missing'
        ])
    
    # Add any additional pytest arguments
    if args.pytest_args:
        pytest_args.extend(args.pytest_args)
    
    # Run tests
    exit_code = run_pytest(pytest_args)
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
