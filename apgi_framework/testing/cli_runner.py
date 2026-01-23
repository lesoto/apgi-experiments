"""
CLI Test Runner for APGI Framework Test Enhancement

This module provides command-line interface for test execution, coverage analysis,
and reporting with full feature parity to the GUI interface.

Requirements: 9.6
"""

import sys
import os
import logging
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from datetime import datetime
import json
import subprocess
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from apgi_framework.testing.batch_runner import BatchTestRunner
from apgi_framework.testing.activity_logger import (
    get_activity_logger,
    ActivityType,
    ActivityLevel,
)


class CLITestRunner:
    """Command-line interface for test execution and management."""

    def __init__(self, container, config):
        """Initialize CLI test runner with dependency container and configuration."""
        self.container = container
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.activity_logger = get_activity_logger()

        # Get components from container
        self.batch_runner = container.get_batch_runner()
        self.ci_integrator = container.get_ci_integrator()
        self.notification_manager = container.get_notification_manager()

        self._start_time = None
        self._test_results = {}

    def run_all_tests(self) -> int:
        """Run all tests in the project."""
        self.logger.info("Running all tests...")
        self._start_time = datetime.now()

        try:
            self.activity_logger.log_activity(
                ActivityType.TEST_EXECUTION_START,
                ActivityLevel.INFO,
                "Starting full test suite execution",
                data={"mode": "cli", "test_type": "all"},
            )

            # Discover all test files
            test_files = self._discover_test_files()
            self.logger.info(f"Discovered {len(test_files)} test files")

            # Execute tests
            results = self.batch_runner.run_tests(
                test_files=test_files,
                parallel=self.config.parallel_execution,
                max_workers=self.config.max_workers,
            )

            # Generate reports
            self._generate_reports(results, "all_tests")

            # Log completion
            self.activity_logger.log_activity(
                ActivityType.TEST_EXECUTION_COMPLETE,
                ActivityLevel.INFO,
                "Full test suite execution completed",
                data={
                    "total_tests": results.get("total_tests", 0),
                    "passed": results.get("passed", 0),
                    "failed": results.get("failed", 0),
                    "duration": str(datetime.now() - self._start_time),
                },
            )

            return 0 if results.get("failed", 0) == 0 else 1

        except Exception as e:
            self.logger.error(f"Error running all tests: {e}")
            self.activity_logger.log_activity(
                ActivityType.TEST_EXECUTION_ERROR,
                ActivityLevel.ERROR,
                f"Test execution failed: {str(e)}",
                data={"error_type": type(e).__name__},
            )
            return 1

    def run_unit_tests(self) -> int:
        """Run unit tests only."""
        self.logger.info("Running unit tests...")
        self._start_time = datetime.now()

        try:
            self.activity_logger.log_activity(
                ActivityType.TEST_EXECUTION_START,
                ActivityLevel.INFO,
                "Starting unit test execution",
                data={"mode": "cli", "test_type": "unit"},
            )

            # Discover unit test files
            test_files = self._discover_test_files(
                pattern="**/test_*.py", exclude_integration=True
            )
            self.logger.info(f"Discovered {len(test_files)} unit test files")

            # Execute tests
            results = self.batch_runner.run_tests(
                test_files=test_files,
                parallel=self.config.parallel_execution,
                max_workers=self.config.max_workers,
            )

            # Generate reports
            self._generate_reports(results, "unit_tests")

            return 0 if results.get("failed", 0) == 0 else 1

        except Exception as e:
            self.logger.error(f"Error running unit tests: {e}")
            return 1

    def run_integration_tests(self) -> int:
        """Run integration tests only."""
        self.logger.info("Running integration tests...")
        self._start_time = datetime.now()

        try:
            self.activity_logger.log_activity(
                ActivityType.TEST_EXECUTION_START,
                ActivityLevel.INFO,
                "Starting integration test execution",
                data={"mode": "cli", "test_type": "integration"},
            )

            # Discover integration test files
            test_files = self._discover_test_files(pattern="**/test_integration_*.py")
            integration_dir = Path(self.config.project_root) / "tests" / "integration"
            if integration_dir.exists():
                integration_files = list(integration_dir.glob("test_*.py"))
                test_files.extend(integration_files)

            self.logger.info(f"Discovered {len(test_files)} integration test files")

            # Execute tests
            results = self.batch_runner.run_tests(
                test_files=test_files,
                parallel=self.config.parallel_execution,
                max_workers=self.config.max_workers,
            )

            # Generate reports
            self._generate_reports(results, "integration_tests")

            return 0 if results.get("failed", 0) == 0 else 1

        except Exception as e:
            self.logger.error(f"Error running integration tests: {e}")
            return 1

    def run_tests_by_pattern(self, pattern: str) -> int:
        """Run tests matching a specific pattern."""
        self.logger.info(f"Running tests matching pattern: {pattern}")
        self._start_time = datetime.now()

        try:
            self.activity_logger.log_activity(
                ActivityType.TEST_EXECUTION_START,
                ActivityLevel.INFO,
                f"Starting pattern-based test execution: {pattern}",
                data={"mode": "cli", "test_type": "pattern", "pattern": pattern},
            )

            # Discover test files matching pattern
            test_files = self._discover_test_files(pattern=pattern)
            self.logger.info(
                f"Discovered {len(test_files)} test files matching pattern"
            )

            if not test_files:
                self.logger.warning(f"No test files found matching pattern: {pattern}")
                return 0

            # Execute tests
            results = self.batch_runner.run_tests(
                test_files=test_files,
                parallel=self.config.parallel_execution,
                max_workers=self.config.max_workers,
            )

            # Generate reports
            self._generate_reports(results, f"pattern_{pattern.replace('*', 'star')}")

            return 0 if results.get("failed", 0) == 0 else 1

        except Exception as e:
            self.logger.error(f"Error running tests by pattern: {e}")
            return 1

    def generate_coverage_report(self) -> int:
        """Generate coverage report without running tests."""
        self.logger.info("Generating coverage report...")

        try:
            self.activity_logger.log_activity(
                ActivityType.COVERAGE_ANALYSIS_START,
                ActivityLevel.INFO,
                "Starting coverage report generation",
                data={"mode": "cli"},
            )

            # Use CI integrator to generate coverage report
            coverage_report = self.ci_integrator.generate_coverage_report()

            if coverage_report:
                # Save report to file
                report_file = (
                    Path(self.config.project_root)
                    / "coverage_reports"
                    / f"coverage_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                report_file.parent.mkdir(parents=True, exist_ok=True)

                with open(report_file, "w") as f:
                    json.dump(coverage_report, f, indent=2)

                self.logger.info(f"Coverage report saved to: {report_file}")

                # Print summary to console
                self._print_coverage_summary(coverage_report)

                return 0
            else:
                self.logger.error("Failed to generate coverage report")
                return 1

        except Exception as e:
            self.logger.error(f"Error generating coverage report: {e}")
            return 1

    def run_interactive(self) -> int:
        """Run interactive CLI mode."""
        self.logger.info("Starting interactive CLI mode...")

        print("\n" + "=" * 60)
        print("APGI Framework Test Enhancement - Interactive CLI")
        print("=" * 60)

        while True:
            try:
                print("\nAvailable commands:")
                print("1. Run all tests")
                print("2. Run unit tests")
                print("3. Run integration tests")
                print("4. Run tests by pattern")
                print("5. Generate coverage report")
                print("6. View test history")
                print("7. Exit")

                choice = input("\nEnter your choice (1-7): ").strip()

                if choice == "1":
                    result = self.run_all_tests()
                    print(f"\nTest execution completed with exit code: {result}")
                elif choice == "2":
                    result = self.run_unit_tests()
                    print(f"\nUnit test execution completed with exit code: {result}")
                elif choice == "3":
                    result = self.run_integration_tests()
                    print(
                        f"\nIntegration test execution completed with exit code: {result}"
                    )
                elif choice == "4":
                    pattern = input(
                        "Enter test pattern (e.g., 'test_core_*.py'): "
                    ).strip()
                    if pattern:
                        result = self.run_tests_by_pattern(pattern)
                        print(
                            f"\nPattern test execution completed with exit code: {result}"
                        )
                elif choice == "5":
                    result = self.generate_coverage_report()
                    print(
                        f"\nCoverage report generation completed with exit code: {result}"
                    )
                elif choice == "6":
                    self._show_test_history()
                elif choice == "7":
                    print("Exiting interactive mode...")
                    break
                else:
                    print("Invalid choice. Please enter a number between 1-7.")

            except KeyboardInterrupt:
                print("\n\nExiting interactive mode...")
                break
            except Exception as e:
                print(f"Error: {e}")

        return 0

    def _discover_test_files(
        self, pattern: str = "**/test_*.py", exclude_integration: bool = False
    ) -> List[Path]:
        """Discover test files matching the given pattern."""
        project_root = Path(self.config.project_root)
        test_files = []

        # Search in tests directory
        tests_dir = project_root / "tests"
        if tests_dir.exists():
            test_files.extend(tests_dir.glob(pattern))

        # Search in apgi_framework directory for embedded tests
        framework_dir = project_root / "apgi_framework"
        if framework_dir.exists():
            test_files.extend(framework_dir.glob(pattern))

        # Filter out integration tests if requested
        if exclude_integration:
            test_files = [
                f
                for f in test_files
                if "integration" not in str(f) and "test_integration" not in f.name
            ]

        return sorted(test_files)

    def _generate_reports(self, results: Dict[str, Any], report_name: str):
        """Generate test execution reports."""
        try:
            # Create reports directory
            reports_dir = Path(self.config.project_root) / "test_reports"
            reports_dir.mkdir(parents=True, exist_ok=True)

            # Generate JSON report
            json_report = {
                "execution_info": {
                    "timestamp": datetime.now().isoformat(),
                    "duration": (
                        str(datetime.now() - self._start_time)
                        if self._start_time
                        else "unknown"
                    ),
                    "mode": "cli",
                    "report_name": report_name,
                },
                "results": results,
                "configuration": {
                    "parallel_execution": self.config.parallel_execution,
                    "max_workers": self.config.max_workers,
                    "coverage_threshold": self.config.coverage_threshold,
                },
            }

            json_file = (
                reports_dir
                / f"{report_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            with open(json_file, "w") as f:
                json.dump(json_report, f, indent=2)

            self.logger.info(f"Test report saved to: {json_file}")

            # Print summary to console
            self._print_test_summary(results)

        except Exception as e:
            self.logger.error(f"Error generating reports: {e}")

    def _print_test_summary(self, results: Dict[str, Any]):
        """Print test execution summary to console."""
        print("\n" + "=" * 50)
        print("TEST EXECUTION SUMMARY")
        print("=" * 50)

        total = results.get("total_tests", 0)
        passed = results.get("passed", 0)
        failed = results.get("failed", 0)
        skipped = results.get("skipped", 0)

        print(f"Total Tests:  {total}")
        print(f"Passed:       {passed}")
        print(f"Failed:       {failed}")
        print(f"Skipped:      {skipped}")

        if total > 0:
            pass_rate = (passed / total) * 100
            print(f"Pass Rate:    {pass_rate:.1f}%")

        if self._start_time:
            duration = datetime.now() - self._start_time
            print(f"Duration:     {duration}")

        # Show coverage if available
        coverage = results.get("coverage", {})
        if coverage:
            line_coverage = coverage.get("line_coverage", 0)
            branch_coverage = coverage.get("branch_coverage", 0)
            print(f"\nCoverage:")
            print(f"Lines:        {line_coverage:.1f}%")
            print(f"Branches:     {branch_coverage:.1f}%")

        print("=" * 50)

        # Show failed tests if any
        failed_tests = results.get("failed_tests", [])
        if failed_tests:
            print(f"\nFAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests[:10]:  # Show first 10 failures
                print(
                    f"  - {test.get('name', 'Unknown')}: {test.get('error', 'No error message')}"
                )

            if len(failed_tests) > 10:
                print(f"  ... and {len(failed_tests) - 10} more failures")

    def _print_coverage_summary(self, coverage_report: Dict[str, Any]):
        """Print coverage summary to console."""
        print("\n" + "=" * 50)
        print("COVERAGE REPORT SUMMARY")
        print("=" * 50)

        overall = coverage_report.get("overall", {})
        line_coverage = overall.get("line_coverage", 0)
        branch_coverage = overall.get("branch_coverage", 0)
        function_coverage = overall.get("function_coverage", 0)

        print(f"Overall Coverage:")
        print(f"Lines:        {line_coverage:.1f}%")
        print(f"Branches:     {branch_coverage:.1f}%")
        print(f"Functions:    {function_coverage:.1f}%")

        # Show module breakdown
        modules = coverage_report.get("modules", {})
        if modules:
            print(f"\nModule Coverage:")
            for module, data in sorted(modules.items()):
                module_coverage = data.get("line_coverage", 0)
                status = (
                    "✓"
                    if module_coverage >= self.config.coverage_threshold * 100
                    else "✗"
                )
                print(f"  {status} {module:<30} {module_coverage:.1f}%")

        print("=" * 50)

    def _show_test_history(self):
        """Show recent test execution history."""
        try:
            reports_dir = Path(self.config.project_root) / "test_reports"
            if not reports_dir.exists():
                print("No test history available.")
                return

            # Get recent report files
            report_files = sorted(
                reports_dir.glob("*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            if not report_files:
                print("No test history available.")
                return

            print("\n" + "=" * 60)
            print("RECENT TEST EXECUTIONS")
            print("=" * 60)

            for i, report_file in enumerate(
                report_files[:10]
            ):  # Show last 10 executions
                try:
                    with open(report_file, "r") as f:
                        report = json.load(f)

                    exec_info = report.get("execution_info", {})
                    results = report.get("results", {})

                    timestamp = exec_info.get("timestamp", "Unknown")
                    duration = exec_info.get("duration", "Unknown")
                    report_name = exec_info.get("report_name", "Unknown")

                    total = results.get("total_tests", 0)
                    passed = results.get("passed", 0)
                    failed = results.get("failed", 0)

                    status = "PASS" if failed == 0 else "FAIL"

                    print(
                        f"{i+1:2d}. {timestamp[:19]} | {report_name:<15} | {status:<4} | {passed}/{total} | {duration}"
                    )

                except Exception as e:
                    print(f"{i+1:2d}. {report_file.name} - Error reading report: {e}")

            print("=" * 60)

        except Exception as e:
            print(f"Error showing test history: {e}")

    def cleanup(self):
        """Cleanup CLI runner resources."""
        try:
            self.logger.info("Cleaning up CLI runner...")

            # Log final activity
            self.activity_logger.log_activity(
                ActivityType.SYSTEM_SHUTDOWN,
                ActivityLevel.INFO,
                "CLI runner cleanup completed",
                data={"mode": "cli"},
            )

        except Exception as e:
            self.logger.warning(f"Error during CLI cleanup: {e}")
