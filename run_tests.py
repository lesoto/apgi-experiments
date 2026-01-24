#!/usr/bin/env python3
"""
Comprehensive Test Runner for APGI Framework

This script provides a unified interface for running different types of tests
with proper organization, reporting, and GUI integration.
"""

import sys
import os
import argparse
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from apgi_framework.utils.test_utils import FrameworkTestUtilities
    from apgi_framework.cli import APGIFrameworkCLI

    UTILS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Test utilities not available: {e}")
    UTILS_AVAILABLE = False


class ComprehensiveTestRunner:
    """Comprehensive test runner with multiple execution modes."""

    def __init__(self):
        self.cli = APGIFrameworkCLI() if UTILS_AVAILABLE else None
        self.test_utils = FrameworkTestUtilities() if UTILS_AVAILABLE else None

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
        cmd = ["python", "-m", "pytest", "-v", "tests"]

        if verbose:
            cmd.append("-vv")

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

            # Set up environment with PYTHONPATH
            env = os.environ.copy()
            env["PYTHONPATH"] = str(project_root)

            # Run pytest
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=1800,  # 30 minutes timeout
                env=env,
            )

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

        except subprocess.TimeoutExpired:
            print("❌ Test execution timed out after 30 minutes")
            results["errors"] = 1
            results["timeout"] = True
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

        cmd = ["python", "-m", "pytest", "-v", f"-m", category]

        if kwargs.get("verbose", False):
            cmd.append("-vv")

        if kwargs.get("coverage", False):
            cmd.extend(["--cov=apgi_framework", "--cov-report=term-missing"])

        try:
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout
            )

            results = {
                "category": category,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

            print(f"✅ {category} tests completed with exit code: {result.returncode}")
            return results

        except subprocess.TimeoutExpired:
            print(f"❌ {category} tests timed out")
            return {"category": category, "timeout": True}
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

    def discover_tests(self) -> Dict[str, Any]:
        """Discover and organize all tests."""
        if not self.test_utils:
            print("❌ Test utilities not available")
            return {}

        print("🔍 Discovering Tests")
        print("=" * 20)

        try:
            test_suites = self.test_utils.discover_tests(project_root)

            summary = {
                "total_suites": len(test_suites),
                "total_tests": sum(len(suite.test_cases) for suite in test_suites),
                "categories": {},
                "modules": set(),
                "suite_details": [],
            }

            for suite in test_suites:
                suite_info = {
                    "name": suite.name,
                    "test_count": len(suite.test_cases),
                    "estimated_duration": suite.total_estimated_duration,
                }
                summary["suite_details"].append(suite_info)

                for test_case in suite.test_cases:
                    category = test_case.category.value
                    if category not in summary["categories"]:
                        summary["categories"][category] = 0
                    summary["categories"][category] += 1
                    summary["modules"].add(test_case.module)

            summary["modules"] = list(summary["modules"])

            print(
                f"📊 Discovered {summary['total_tests']} tests in {summary['total_suites']} suites"
            )
            print(f"📂 Modules: {', '.join(summary['modules'])}")
            print(f"🏷️  Categories: {dict(summary['categories'])}")

            return summary

        except Exception as e:
            print(f"❌ Error discovering tests: {e}")
            return {"error": str(e)}

    def generate_report(
        self, results: Dict[str, Any], output_file: Optional[str] = None
    ) -> str:
        """Generate a comprehensive test report."""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_report_{timestamp}.json"

        report_path = project_root / output_file

        try:
            with open(report_path, "w") as f:
                json.dump(results, f, indent=2)

            print(f"📄 Report saved to: {report_path}")
            return str(report_path)

        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return ""

    def _parse_pytest_output(self, output: str, results: Dict[str, Any]):
        """Parse pytest output to extract test statistics."""
        lines = output.split("\n")

        for line in lines:
            if " passed" in line and " failed" in line:
                # Parse summary line like "673 passed, 2 failed in 10.5s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        results["passed"] = int(parts[i - 1])
                    elif part == "failed":
                        results["failed"] = int(parts[i - 1])
                    elif part == "error":
                        results["errors"] = int(parts[i - 1])
                    elif part == "skipped":
                        results["skipped"] = int(parts[i - 1])
                    elif part == "in" and i + 1 < len(parts) and "s" in parts[i + 1]:
                        try:
                            results["duration"] = float(parts[i + 1].rstrip("s"))
                        except ValueError:
                            pass

        results["total_tests"] = (
            results["passed"]
            + results["failed"]
            + results["errors"]
            + results["skipped"]
        )

    def _print_summary(self, results: Dict[str, Any]):
        """Print a formatted test summary."""
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)

        total = results["total_tests"]
        passed = results["passed"]
        failed = results["failed"]
        errors = results["errors"]
        skipped = results["skipped"]
        duration = results["duration"]

        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"⏱️  Duration: {duration:.2f}s")

        if total > 0:
            pass_rate = (passed / total) * 100
            print(f"📈 Pass Rate: {pass_rate:.1f}%")

        print("=" * 50)


def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Test Runner for APGI Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all                    # Run all tests
  python run_tests.py --unit                   # Run unit tests only
  python run_tests.py --gui --coverage         # Run GUI tests with coverage
  python run_tests.py --discover               # Discover and list tests
  python run_tests.py --all --report report.json  # Run all tests and save report
        """,
    )

    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests"
    )
    parser.add_argument("--gui", action="store_true", help="Run GUI tests")
    parser.add_argument(
        "--performance", action="store_true", help="Run performance tests"
    )
    parser.add_argument(
        "--discover", action="store_true", help="Discover and list tests"
    )
    parser.add_argument(
        "--coverage", action="store_true", help="Generate coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--report", help="Save report to specified file")
    parser.add_argument(
        "--timeout", type=int, default=1800, help="Test timeout in seconds"
    )

    args = parser.parse_args()

    runner = ComprehensiveTestRunner()

    if args.discover:
        runner.discover_tests()
        return 0

    results = {}

    if args.all:
        results = runner.run_all_tests(verbose=args.verbose, coverage=args.coverage)
    elif args.unit:
        results = runner.run_unit_tests()
    elif args.integration:
        results = runner.run_integration_tests()
    elif args.gui:
        results = runner.run_gui_tests()
    elif args.performance:
        results = runner.run_performance_tests()
    else:
        parser.print_help()
        return 1

    # Generate report if requested
    if args.report or args.all:
        runner.generate_report(results, args.report)

    # Return appropriate exit code
    exit_code = results.get("exit_code", 0)
    if exit_code == 0 and results.get("failed", 0) > 0:
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
