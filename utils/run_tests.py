#!/usr/bin/env python3
"""
Test Runner for APGI Framework

This script provides a unified interface for running tests with proper
environment setup and multiple execution modes.
"""

import sys
import os
import subprocess
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(project_root))

try:
    from apgi_framework.utils.test_utils import FrameworkTestUtilities
    from apgi_framework.cli import APGIFrameworkCLI

    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Test utilities not available: {e}")
    UTILS_AVAILABLE = False


def setup_python_path():
    """Set up the Python path to include the project root."""
    # Get the project root directory (go up one level from utils/)
    project_root = Path(__file__).parent.parent.absolute()

    # Add project root to Python path if not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Set PYTHONPATH environment variable
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{project_root}:{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = str(project_root)

    return env


def run_pytest(args=None, capture_output=False):
    """Run pytest with proper environment setup.

    Args:
        args: List of pytest arguments (optional).
        capture_output: Whether to capture stdout/stderr.
    """
    env = setup_python_path()

    # Default pytest arguments
    if args is None:
        args = ["tests/", "-v", "--tb=short", "--color=yes"]

    # Construct pytest command
    cmd = [sys.executable, "-m", "pytest"] + args

    print(f"Running: {' '.join(cmd)}")
    print(f"PYTHONPATH: {env['PYTHONPATH']}")
    print("-" * 60)

    # Run pytest
    try:
        if capture_output:
            result = subprocess.run(
                cmd, env=env, cwd=project_root, capture_output=True, text=True
            )
            return result
        else:
            result = subprocess.run(cmd, env=env, cwd=project_root)
            return result
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        if capture_output:

            class MockResult:
                def __init__(
                    self, test_dir: str = "tests", output_file: Optional[str] = None
                ):
                    self.test_dir = Path(test_dir)
                    self.output_file = (
                        output_file or f"test_results_{int(time.time())}.json"
                    )
                    self.results = {}
                    self.start_time = None
                    self.end_time = None
                    self.parallel_workers = multiprocessing.cpu_count()
                    self.use_parallel = True

            return MockResult()
        return 130
    except Exception as e:
        print(f"Error running pytest: {e}")
        if capture_output:

            class MockResult:
                def __init__(self):
                    self.returncode = 1
                    self.stdout = ""
                    self.stderr = str(e)

            return MockResult()
        return 1


class ComprehensiveTestRunner:
    """Comprehensive test runner with multiple execution modes."""

    def __init__(self):
        self.cli = APGIFrameworkCLI() if UTILS_AVAILABLE else None
        self.test_utils = FrameworkTestUtilities() if UTILS_AVAILABLE else None

    def run_pytest(self, args=None, capture_output=False, timeout=1800):
        """Run pytest with proper environment setup.

        Args:
            args: List of pytest arguments (optional).
            capture_output: Whether to capture stdout/stderr.
            timeout: Timeout in seconds.
        """
        env = setup_python_path()

        # Default pytest arguments
        if args is None:
            args = ["tests/", "-v", "--tb=short", "--color=yes"]

        # Construct pytest command
        cmd = [sys.executable, "-m", "pytest"] + args

        print(f"Running: {' '.join(cmd)}")
        print(f"PYTHONPATH: {env['PYTHONPATH']}")
        print("-" * 60)

        # Run pytest
        try:
            if capture_output:
                result = subprocess.run(
                    cmd,
                    env=env,
                    cwd=Path(__file__).parent.parent,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                return result
            else:
                result = subprocess.run(cmd, env=env, cwd=Path(__file__).parent.parent)
                return result
        except KeyboardInterrupt:
            print("\nTest execution interrupted by user")
            if capture_output:

                class MockResult:
                    def __init__(self):
                        self.returncode = 130
                        self.stdout = ""
                        self.stderr = "Test execution interrupted by user"

                return MockResult()
            return 130
        except subprocess.TimeoutExpired:
            print(f"\nTest execution timed out after {timeout} seconds")
            if capture_output:

                class MockResult:
                    def __init__(self):
                        self.returncode = 124
                        self.stdout = ""
                        self.stderr = (
                            f"Test execution timed out after {timeout} seconds"
                        )

                return MockResult()
            return 124
        except Exception as e:
            print(f"Error running pytest: {e}")
            if capture_output:

                class MockResult:
                    def __init__(self):
                        self.returncode = 1
                        self.stdout = ""
                        self.stderr = str(e)

                return MockResult()
            return 1

    def run_all_tests(
        self, verbose: bool = False, coverage: bool = False
    ) -> Dict[str, Any]:
        """Run all tests with comprehensive reporting."""
        print("🧪 Running Comprehensive Test Suite")
        print("=" * 50)

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "duration": 0,
            "categories": {},
            "details": {},
        }

        # Build pytest command
        cmd = ["tests"]

        if verbose:
            cmd.append("-vv")
        else:
            cmd.append("-v")

        if coverage:
            cmd.extend(
                [
                    "--cov=apgi_framework",
                    "--cov=research",
                    "--cov-report=html",
                    "--cov-report=term-missing",
                    "--cov-report=json",
                ]
            )

        # Add test markers and categories
        cmd.extend(["--tb=short", "--strict-markers", "--color=yes"])

        try:
            start_time = datetime.now()

            # Run pytest with captured output
            result = self.run_pytest(cmd, capture_output=True)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            results["duration"] = duration
            results["exit_code"] = result.returncode
            results["stdout"] = result.stdout
            results["stderr"] = result.stderr

            # Parse results from output
            self._parse_pytest_output(result.stdout, results)

            # Print summary
            self._print_summary(results)

            return results

        except Exception as e:
            print(f"❌ Error running tests: {e}")
            results["errors"] = 1
            results["exception"] = str(e)
            return results

    def run_category_tests(self, category: str, **kwargs) -> Dict[str, Any]:
        """Run tests for a specific category."""
        print(f"🧪 Running {category} Tests")
        print("=" * 30)

        cmd = ["-m", category]

        if kwargs.get("verbose", False):
            cmd.append("-vv")
        else:
            cmd.append("-v")

        if kwargs.get("coverage", False):
            cmd.extend(["--cov=apgi_framework", "--cov-report=term-missing"])

        try:
            result = self.run_pytest(cmd, capture_output=True, timeout=600)

            results = {
                "category": category,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

            print(f"✅ {category} tests completed with exit code: {result.returncode}")
            return results

        except Exception as e:
            print(f"❌ Error running {category} tests: {e}")
            return {"category": category, "error": str(e)}

    def run_gui_tests(self) -> Dict[str, Any]:
        """Run GUI-specific tests."""
        return self.run_category_tests("gui")

    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests."""
        return self.run_category_tests("unit")

    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        return self.run_category_tests("integration")

    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        return self.run_category_tests("performance")

    def run_specific_test(self, test_path: str, **kwargs) -> Dict[str, Any]:
        """Run a specific test file or test function."""
        print(f"🧪 Running Specific Test: {test_path}")
        print("=" * 40)

        cmd = [test_path]

        if kwargs.get("verbose", False):
            cmd.append("-vv")
        else:
            cmd.append("-v")

        if kwargs.get("coverage", False):
            cmd.extend(["--cov=apgi_framework", "--cov-report=term-missing"])

        try:
            result = self.run_pytest(cmd, capture_output=True, timeout=300)

            results = {
                "test_path": test_path,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

            print(f"✅ Test {test_path} completed with exit code: {result.returncode}")
            return results

        except Exception as e:
            print(f"❌ Error running test {test_path}: {e}")
            return {"test_path": test_path, "error": str(e)}

    def _parse_pytest_output(self, output: str, results: Dict[str, Any]):
        """Parse pytest output to extract test statistics."""
        try:
            lines = output.split("\n")
            for line in lines:
                if (
                    " passed" in line
                    or " failed" in line
                    or " skipped" in line
                    or " error" in line
                ):
                    # Parse the summary line
                    parts = line.split()
                    for part in parts:
                        if part.isdigit():
                            results["total_tests"] += int(part)
                        elif "passed" in part:
                            results["passed"] = int(part.split()[0])
                        elif "failed" in part:
                            results["failed"] = int(part.split()[0])
                        elif "skipped" in part:
                            results["skipped"] = int(part.split()[0])
                        elif "error" in part:
                            results["errors"] = int(part.split()[0])
        except Exception:
            # If parsing fails, continue with default values
            pass

    def _print_summary(self, results: Dict[str, Any]):
        """Print a formatted summary of test results."""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {results['total_tests']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⏭️  Skipped: {results['skipped']}")
        print(f"🚨 Errors: {results['errors']}")
        print(f"⏱️  Duration: {results['duration']:.2f}s")
        print(f"📅 Timestamp: {results['timestamp']}")

        if results["exit_code"] == 0:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed or had errors")

        print("=" * 50)


class TestRunner:
    def __init__(self, test_dir: str, output_file: Optional[str] = None):
        self.test_dir = Path(test_dir)
        self.output_file = output_file or f"test_results_{int(time.time())}.json"
        self.results = {}
        self.start_time = None
        self.end_time = None
        self.parallel_workers = multiprocessing.cpu_count()
        self.use_parallel = True

    def run_tests(
        self,
        verbose: bool = False,
        coverage: bool = False,
        category: Optional[str] = None,
        specific_file: Optional[str] = None,
        parallel: Optional[bool] = None,
        max_workers: Optional[int] = None,
    ) -> Dict[str, any]:
        """Run tests with specified options."""
        self.start_time = time.time()

        # Determine parallel execution settings
        if parallel is not None:
            self.use_parallel = parallel
        if max_workers is not None:
            self.parallel_workers = max_workers

        # Build pytest command
        cmd = ["python", "-m", "pytest"]

        # Add parallel execution if enabled
        if self.use_parallel and self.parallel_workers > 1:
            cmd.extend(["-n", str(self.parallel_workers)])
            print(f"Running tests in parallel with {self.parallel_workers} workers")

        # Add verbosity
        if verbose:
            cmd.append("-v")

        # Add coverage
        if coverage:
            cmd.extend(
                ["--cov=apgi_framework", "--cov-report=html", "--cov-report=term"]
            )

        # Add category filter
        if category:
            cmd.extend(["-m", category])

        # Add specific file or directory
        if specific_file:
            test_path = self.test_dir / specific_file
            cmd.append(str(test_path))
        else:
            cmd.append(str(self.test_dir))

        # Add JSON output for parsing
        cmd.extend(["--json-report", "--json-report-file=.pytest_results.json"])

        print(f"Running command: {' '.join(cmd)}")

        try:
            # Run tests
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.test_dir.parent
            )

            self.end_time = time.time()

            # Parse results
            self._parse_results(result)

            return self.results

        except Exception as e:
            self.end_time = time.time()
            return {
                "error": str(e),
                "execution_time": self.end_time - self.start_time,
                "parallel_used": self.use_parallel,
                "workers": self.parallel_workers if self.use_parallel else 1,
            }

    def _parse_results(self, result: subprocess.CompletedProcess):
        """Parse test results from pytest output."""
        execution_time = self.end_time - self.start_time

        # Try to parse JSON report
        json_file = self.test_dir.parent / ".pytest_results.json"
        if json_file.exists():
            try:
                with open(json_file, "r") as f:
                    json_data = json.load(f)

                self.results = {
                    "summary": json_data.get("summary", {}),
                    "tests": json_data.get("tests", []),
                    "execution_time": execution_time,
                    "return_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "parallel_used": self.use_parallel,
                    "workers": self.parallel_workers if self.use_parallel else 1,
                }

                # Clean up JSON file
                json_file.unlink()
                return

            except Exception as e:
                print(f"Warning: Could not parse JSON results: {e}")

        # Fallback to parsing stdout
        self.results = {
            "execution_time": execution_time,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "parallel_used": self.use_parallel,
            "workers": self.parallel_workers if self.use_parallel else 1,
        }

        # Try to extract basic summary from stdout
        stdout_lines = result.stdout.split("\n")
        for line in stdout_lines:
            if "passed" in line and "failed" in line:
                # Extract numbers like "5 passed, 2 failed"
                import re

                matches = re.findall(r"(\d+) (passed|failed|skipped|error)", line)
                summary = {}
                for count, status in matches:
                    summary[status] = int(count)
                self.results["summary"] = summary
                break

    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST EXECUTION SUMMARY")
        print("=" * 60)

        if "error" in self.results:
            print(f"❌ Error: {self.results['error']}")
            print(f"Execution time: {self.results['execution_time']:.2f}s")
            return

        execution_time = self.results.get("execution_time", 0)
        return_code = self.results.get("return_code", 1)
        parallel_used = self.results.get("parallel_used", False)
        workers = self.results.get("workers", 1)

        print(f"Execution time: {execution_time:.2f}s")
        print(f"Parallel execution: {'✅' if parallel_used else '❌'}")
        if parallel_used:
            print(f"Workers used: {workers}")
        print(f"Return code: {return_code}")

        summary = self.results.get("summary", {})
        if summary:
            print("\nTest Results:")
            for status, count in summary.items():
                icon = (
                    "✅"
                    if status == "passed"
                    else (
                        "❌"
                        if status == "failed"
                        else "⏭️" if status == "skipped" else "💥"
                    )
                )
                print(f"  {icon} {status.capitalize()}: {count}")

        if return_code == 0:
            print("\n🎉 All tests completed successfully!")
        else:
            print("\n⚠️ Some tests failed or encountered errors.")

        # Show performance comparison if parallel was used
        if parallel_used and workers > 1:
            estimated_sequential_time = execution_time * workers
            print(
                f"\n📊 Performance: Estimated sequential time would be {estimated_sequential_time:.2f}s"
            )
            print(f"   Speedup: ~{workers}x with parallel execution")


def main():
    """Main entry point with comprehensive CLI interface."""
    parser = argparse.ArgumentParser(
        description="Comprehensive APGI Framework Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Run all tests
  %(prog)s --coverage                # Run all tests with coverage
  %(prog)s --category unit           # Run unit tests only
  %(prog)s --specific tests/test_cli.py  # Run specific test file
  %(prog)s --verbose --coverage      # Run with verbose output and coverage
  %(prog)s --save-results            # Save results to JSON file
""",
    )

    # Test selection options
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument(
        "--category",
        choices=["unit", "integration", "gui", "performance"],
        help="Run tests for a specific category",
    )
    test_group.add_argument(
        "--specific", help="Run specific test file or test function"
    )
    test_group.add_argument(
        "--all",
        action="store_true",
        help="Run all tests with comprehensive reporting (default)",
    )

    # Output options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--coverage",
        "-c",
        action="store_true",
        help="Run tests with coverage reporting",
    )
    parser.add_argument(
        "--save-results", action="store_true", help="Save test results to JSON file"
    )

    # Parallel execution options
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument(
        "--no-parallel", action="store_true", help="Disable parallel execution"
    )
    parser.add_argument(
        "--workers", type=int, help="Number of workers for parallel execution"
    )

    # Additional pytest arguments
    parser.add_argument(
        "pytest_args", nargs="*", help="Additional arguments to pass to pytest"
    )

    args = parser.parse_args()

    # Determine parallel settings
    parallel = args.parallel and not args.no_parallel
    max_workers = args.workers

    # Create test runner
    runner = TestRunner("tests")

    # Run tests
    results = runner.run_tests(
        verbose=args.verbose,
        coverage=args.coverage,
        category=args.category,
        specific_file=args.specific,
        parallel=parallel,
        max_workers=max_workers,
    )

    # Print summary
    runner.print_summary()

    # Save results if requested
    if args.save_results:
        output_path = project_root / "test_results" / runner.output_file
        output_path.parent.mkdir(exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(results, f, indent=2)
        print(f"📄 Results saved to: {output_path}")

    # Exit with appropriate code
    exit_code = results.get("return_code", 1)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
