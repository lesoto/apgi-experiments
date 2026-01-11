"""
Command-Line Interface for APGI Framework Falsification Testing System.

This module provides a comprehensive CLI for running individual falsification tests,
batch experiment execution, and configuration management.
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .main_controller import MainApplicationController
from .config import ConfigManager, APGIParameters, ExperimentalConfig
from .exceptions import APGIFrameworkError, ConfigurationError
from .testing.batch_runner import BatchTestRunner, run_failed_tests
from .testing.persistence import TestResultPersistence, store_test_results
from .testing.test_generator import (
    TestSuiteGenerator,
    analyze_test_coverage,
    generate_missing_tests,
    create_coverage_report,
)


class APGIFrameworkCLI:
    """Command-line interface for the APGI Framework Falsification Testing System."""

    def __init__(self):
        """Initialize the CLI."""
        self.controller = None
        self.logger = None

    def setup_logging(self, log_level: str = "INFO") -> None:
        """Setup logging for CLI operations."""
        from ..logging.centralized_logging import APGILogManager

        APGILogManager.setup_logging(level=log_level)
        self.logger = logging.getLogger(__name__)

    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="APGI Framework Falsification Testing System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run primary falsification test
  python -m apgi_framework.cli run-test primary --trials 1000
  
  # Run all tests in batch mode
  python -m apgi_framework.cli run-batch --config config.json
  
  # Generate default configuration
  python -m apgi_framework.cli generate-config --output config.json
  
  # Validate system components
  python -m apgi_framework.cli validate-system
            """,
        )

        # Global options
        parser.add_argument(
            "--config", "-c", type=str, help="Path to configuration file"
        )

        parser.add_argument(
            "--log-level",
            "-l",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Set logging level (default: INFO)",
        )

        parser.add_argument(
            "--output-dir", "-o", type=str, help="Output directory for results"
        )

        # Subcommands
        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Run individual test command
        test_parser = subparsers.add_parser(
            "run-test", help="Run individual falsification test"
        )
        test_parser.add_argument(
            "test_type",
            choices=[
                "primary",
                "consciousness-without-ignition",
                "threshold-insensitivity",
                "soma-bias",
            ],
            help="Type of falsification test to run",
        )
        test_parser.add_argument(
            "--trials",
            "-n",
            type=int,
            default=1000,
            help="Number of trials to run (default: 1000)",
        )
        test_parser.add_argument(
            "--participants",
            "-p",
            type=int,
            default=100,
            help="Number of participants to simulate (default: 100)",
        )
        test_parser.add_argument(
            "--seed", type=int, help="Random seed for reproducibility"
        )

        # Run batch experiments command
        batch_parser = subparsers.add_parser("run-batch", help="Run batch experiments")
        batch_parser.add_argument(
            "--all-tests", action="store_true", help="Run all falsification tests"
        )
        batch_parser.add_argument(
            "--tests",
            nargs="+",
            choices=[
                "primary",
                "consciousness-without-ignition",
                "threshold-insensitivity",
                "soma-bias",
            ],
            help="Specific tests to run in batch",
        )
        batch_parser.add_argument(
            "--parallel",
            action="store_true",
            help="Run tests in parallel (experimental)",
        )

        # Advanced batch testing commands
        batch_test_parser = subparsers.add_parser(
            "batch-test", help="Advanced batch test execution"
        )
        batch_test_parser.add_argument(
            "--test-paths", nargs="+", help="Specific test paths to run"
        )
        batch_test_parser.add_argument(
            "--markers",
            nargs="+",
            choices=[
                "unit",
                "integration",
                "research",
                "core",
                "slow",
                "neural",
                "behavioral",
            ],
            help="Run tests with specific markers",
        )
        batch_test_parser.add_argument(
            "--keywords", type=str, help="Run tests matching keywords"
        )
        batch_test_parser.add_argument(
            "--parallel",
            action="store_true",
            default=True,
            help="Run tests in parallel (default: True)",
        )
        batch_test_parser.add_argument(
            "--sequential", action="store_true", help="Run tests sequentially"
        )
        batch_test_parser.add_argument(
            "--max-workers", type=int, help="Maximum number of parallel workers"
        )
        batch_test_parser.add_argument(
            "--timeout",
            type=int,
            default=300,
            help="Timeout per test in seconds (default: 300)",
        )
        batch_test_parser.add_argument(
            "--failfast", action="store_true", help="Stop on first failure"
        )
        batch_test_parser.add_argument(
            "--report", type=str, help="Output path for HTML report"
        )

        # Test result management commands
        result_parser = subparsers.add_parser(
            "test-results", help="Manage test results"
        )
        result_parser.add_argument(
            "--list", action="store_true", help="List recent test results"
        )
        result_parser.add_argument(
            "--show", type=str, help="Show specific test result file"
        )
        result_parser.add_argument(
            "--rerun-failed", type=str, help="Re-run failed tests from result file"
        )
        result_parser.add_argument(
            "--clean", action="store_true", help="Clean old test results"
        )

        # Test analysis and reporting commands
        analysis_parser = subparsers.add_parser(
            "test-analysis", help="Analyze test results and performance"
        )
        analysis_parser.add_argument(
            "--performance-report",
            action="store_true",
            help="Generate performance report",
        )
        analysis_parser.add_argument(
            "--days",
            type=int,
            default=30,
            help="Number of days to analyze (default: 30)",
        )
        analysis_parser.add_argument(
            "--trends", action="store_true", help="Show performance trends"
        )
        analysis_parser.add_argument(
            "--failures", action="store_true", help="Analyze failure patterns"
        )
        analysis_parser.add_argument(
            "--test-name", type=str, help="Analyze specific test"
        )
        analysis_parser.add_argument(
            "--export", type=str, help="Export results to file"
        )
        analysis_parser.add_argument(
            "--format",
            choices=["json", "csv"],
            default="json",
            help="Export format (default: json)",
        )

        # Test generation and coverage commands
        coverage_parser = subparsers.add_parser(
            "test-coverage", help="Analyze and generate test coverage"
        )
        coverage_parser.add_argument(
            "--analyze", action="store_true", help="Analyze test coverage gaps"
        )
        coverage_parser.add_argument(
            "--generate", action="store_true", help="Generate missing tests"
        )
        coverage_parser.add_argument(
            "--report", action="store_true", help="Generate coverage report"
        )
        coverage_parser.add_argument(
            "--output-dir",
            type=str,
            default="generated_tests",
            help="Output directory for generated tests (default: generated_tests)",
        )
        coverage_parser.add_argument(
            "--report-file",
            type=str,
            default="coverage_report.md",
            help="Output file for coverage report (default: coverage_report.md)",
        )
        coverage_parser.add_argument(
            "--root-path",
            type=str,
            help="Root path to analyze (default: current directory)",
        )

        # Configuration management commands
        config_parser = subparsers.add_parser(
            "generate-config", help="Generate configuration file"
        )
        config_parser.add_argument(
            "--output",
            type=str,
            default="apgi_config.json",
            help="Output path for configuration file (default: apgi_config.json)",
        )
        config_parser.add_argument(
            "--template",
            choices=["default", "minimal", "comprehensive"],
            default="default",
            help="Configuration template to use (default: default)",
        )

        # System validation command
        validate_parser = subparsers.add_parser(
            "validate-system", help="Validate system components"
        )
        validate_parser.add_argument(
            "--detailed", action="store_true", help="Show detailed validation results"
        )

        # Status command
        status_parser = subparsers.add_parser("status", help="Show system status")

        # Parameter override commands
        param_parser = subparsers.add_parser("set-params", help="Set APGI parameters")
        param_parser.add_argument(
            "--extero-precision", type=float, help="Exteroceptive precision"
        )
        param_parser.add_argument(
            "--intero-precision", type=float, help="Interoceptive precision"
        )
        param_parser.add_argument("--threshold", type=float, help="Ignition threshold")
        param_parser.add_argument("--steepness", type=float, help="Sigmoid steepness")
        param_parser.add_argument(
            "--somatic-gain", type=float, help="Somatic marker gain"
        )

        return parser

    def initialize_controller(self, config_path: Optional[str] = None) -> None:
        """Initialize the main application controller."""
        try:
            self.controller = MainApplicationController(config_path)
            self.controller.initialize_system()
            self.logger.info("System initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            sys.exit(1)

    def run_individual_test(self, args: argparse.Namespace) -> None:
        """Run an individual falsification test."""
        self.logger.info(f"Running {args.test_type} test with {args.trials} trials")

        try:
            # Update configuration if parameters provided
            if args.trials:
                self.controller.config_manager.update_experimental_config(
                    n_trials=args.trials
                )
            if args.participants:
                self.controller.config_manager.update_experimental_config(
                    n_participants=args.participants
                )
            if args.seed:
                self.controller.config_manager.update_experimental_config(
                    random_seed=args.seed
                )

            # Get falsification tests
            tests = self.controller.get_falsification_tests()

            # Run the specified test
            if args.test_type == "primary":
                result = tests["primary"].run_falsification_test(n_trials=args.trials)
            elif args.test_type == "consciousness-without-ignition":
                result = tests[
                    "consciousness_without_ignition"
                ].run_consciousness_without_ignition_test(n_trials=args.trials)
            elif args.test_type == "threshold-insensitivity":
                result = tests[
                    "threshold_insensitivity"
                ].run_threshold_insensitivity_test()
            elif args.test_type == "soma-bias":
                result = tests["soma_bias"].run_soma_bias_test(
                    n_participants=args.participants
                )

            # Display results
            self._display_test_result(result, args.test_type)

            # Save results
            self._save_test_result(result, args.test_type)

        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            sys.exit(1)

    def run_batch_experiments(self, args: argparse.Namespace) -> None:
        """Run batch experiments."""
        self.logger.info("Running batch experiments")

        try:
            # Determine which tests to run
            if args.all_tests:
                test_types = [
                    "primary",
                    "consciousness-without-ignition",
                    "threshold-insensitivity",
                    "soma-bias",
                ]
            elif args.tests:
                test_types = args.tests
            else:
                self.logger.error("Must specify either --all-tests or --tests")
                sys.exit(1)

            results = {}
            tests = self.controller.get_falsification_tests()

            for test_type in test_types:
                self.logger.info(f"Running {test_type} test...")

                try:
                    if test_type == "primary":
                        result = tests["primary"].run_test()
                    elif test_type == "consciousness-without-ignition":
                        result = tests["consciousness_without_ignition"].run_test()
                    elif test_type == "threshold-insensitivity":
                        result = tests["threshold_insensitivity"].run_test()
                    elif test_type == "soma-bias":
                        result = tests["soma_bias"].run_test()

                    results[test_type] = result
                    self.logger.info(f"Completed {test_type} test")

                except Exception as e:
                    self.logger.error(f"Failed to run {test_type} test: {e}")
                    results[test_type] = {"error": str(e)}

            # Display batch results
            self._display_batch_results(results)

            # Save batch results
            self._save_batch_results(results)

        except Exception as e:
            self.logger.error(f"Batch execution failed: {e}")
            sys.exit(1)

    def generate_configuration(self, args: argparse.Namespace) -> None:
        """Generate a configuration file."""
        self.logger.info(
            f"Generating {args.template} configuration file: {args.output}"
        )

        try:
            if args.template == "minimal":
                config_data = self._create_minimal_config()
            elif args.template == "comprehensive":
                config_data = self._create_comprehensive_config()
            else:  # default
                config_data = self._create_default_config()

            # Create output directory if needed
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)

            # Save configuration
            with open(args.output, "w") as f:
                json.dump(config_data, f, indent=2)

            self.logger.info(f"Configuration saved to {args.output}")

        except Exception as e:
            self.logger.error(f"Failed to generate configuration: {e}")
            sys.exit(1)

    def validate_system(self, args: argparse.Namespace) -> None:
        """Validate system components."""
        self.logger.info("Validating system components...")

        try:
            validation_results = self.controller.run_system_validation()

            if args.detailed:
                self._display_detailed_validation(validation_results)
            else:
                self._display_simple_validation(validation_results)

            if not validation_results.get("overall", False):
                sys.exit(1)

        except Exception as e:
            self.logger.error(f"System validation failed: {e}")
            sys.exit(1)

    def show_status(self, args: argparse.Namespace) -> None:
        """Show system status."""
        try:
            status = self.controller.get_system_status()
            self._display_system_status(status)
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            sys.exit(1)

    def set_parameters(self, args: argparse.Namespace) -> None:
        """Set APGI parameters."""
        try:
            updates = {}
            if args.extero_precision is not None:
                updates["extero_precision"] = args.extero_precision
            if args.intero_precision is not None:
                updates["intero_precision"] = args.intero_precision
            if args.threshold is not None:
                updates["threshold"] = args.threshold
            if args.steepness is not None:
                updates["steepness"] = args.steepness
            if args.somatic_gain is not None:
                updates["somatic_gain"] = args.somatic_gain

            if updates:
                self.controller.config_manager.update_apgi_parameters(**updates)
                self.logger.info(f"Updated parameters: {updates}")
            else:
                self.logger.warning("No parameters specified to update")

        except Exception as e:
            self.logger.error(f"Failed to set parameters: {e}")
            sys.exit(1)

    def run_advanced_batch_tests(self, args: argparse.Namespace) -> None:
        """Run advanced batch tests using the new batch test runner."""
        self.logger.info("Running advanced batch tests")

        try:
            # Initialize batch runner
            batch_runner = BatchTestRunner(
                self.controller.config_manager if self.controller else None
            )

            # Set progress callback
            def progress_callback(progress: float, result: Any):
                self.logger.info(
                    f"Progress: {progress:.1%} - {result.test_name}: {result.status}"
                )

            batch_runner.set_progress_callback(progress_callback)

            # Determine execution mode
            parallel = args.parallel and not args.sequential

            # Run batch tests
            summary = batch_runner.run_batch_tests(
                test_selection=args.test_paths,
                markers=args.markers,
                keywords=args.keywords,
                parallel=parallel,
                max_workers=args.max_workers,
                timeout=args.timeout,
                failfast=args.failfast,
            )

            # Store results in persistence database
            try:
                batch_id = store_test_results(summary)
                self.logger.info(
                    f"Test results stored in database with batch_id: {batch_id}"
                )
            except Exception as e:
                self.logger.warning(f"Failed to store results in database: {e}")

            # Display results
            self._display_batch_test_summary(summary)

            # Generate report if requested
            if args.report:
                report_path = batch_runner.generate_report(summary, args.report)
                self.logger.info(f"Test report generated: {report_path}")

            # Save results for potential re-run
            self._save_batch_test_summary(summary)

        except Exception as e:
            self.logger.error(f"Advanced batch test execution failed: {e}")
            sys.exit(1)

    def manage_test_results(self, args: argparse.Namespace) -> None:
        """Manage test results."""
        try:
            if args.list:
                self._list_test_results()
            elif args.show:
                self._show_test_result(args.show)
            elif args.rerun_failed:
                self._rerun_failed_tests(args.rerun_failed)
            elif args.clean:
                self._clean_test_results()
            else:
                self.logger.error(
                    "Must specify one of: --list, --show, --rerun-failed, --clean"
                )
                sys.exit(1)

        except Exception as e:
            self.logger.error(f"Test results management failed: {e}")
            sys.exit(1)

    def analyze_test_results(self, args: argparse.Namespace) -> None:
        """Analyze test results and generate reports."""
        try:
            persistence = TestResultPersistence()

            if args.performance_report:
                self.logger.info(
                    f"Generating performance report for last {args.days} days"
                )
                report = persistence.generate_performance_report(args.days)
                print(report)

                # Save report to file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_file = f"performance_report_{timestamp}.md"
                with open(report_file, "w") as f:
                    f.write(report)
                print(f"\nReport saved to: {report_file}")

            elif args.trends:
                self.logger.info(
                    f"Showing performance trends for last {args.days} days"
                )
                trends = persistence.get_performance_trends(args.test_name)

                if not trends:
                    print("No performance trend data found")
                    return

                print(f"\nPerformance Trends (Last {args.days} days):")
                print(f"{'='*80}")
                for trend in trends:
                    print(f"\nTest: {trend['test_name']}")
                    print(f"  Success Rate: {trend['success_rate']:.1%}")
                    print(f"  Avg Duration: {trend['avg_duration']:.3f}s")
                    print(
                        f"  Min/Max Duration: {trend['min_duration']:.3f}s / {trend['max_duration']:.3f}s"
                    )
                    print(f"  Total Executions: {trend['total_executions']}")
                    print(f"  Last Execution: {trend['last_execution']}")

            elif args.failures:
                self.logger.info(
                    f"Analyzing failure patterns for last {args.days} days"
                )
                patterns = persistence.analyze_failure_patterns(args.days)

                if not patterns:
                    print("No failure pattern data found")
                    return

                print(f"\nFailure Pattern Analysis (Last {args.days} days):")
                print(f"{'='*80}")

                if patterns.get("failed_tests"):
                    print("\nMost Frequently Failing Tests:")
                    for test in patterns["failed_tests"][:10]:
                        print(
                            f"  - {test['test_name']}: {test['failure_count']} failures"
                        )
                        if test["error_patterns"]:
                            print(
                                f"    Common errors: {test['error_patterns'][:150]}..."
                            )

                if patterns.get("common_errors"):
                    print("\nMost Common Error Messages:")
                    for error in patterns["common_errors"][:5]:
                        print(
                            f"  - {error['count']} occurrences: {error['error_sample']}"
                        )

            elif args.export:
                self.logger.info(f"Exporting test results to {args.export}")
                persistence.export_results(args.export, args.format, args.days)
                print(f"Results exported to: {args.export}")

            else:
                self.logger.error(
                    "Must specify one of: --performance-report, --trends, --failures, --export"
                )
                sys.exit(1)

        except Exception as e:
            self.logger.error(f"Test analysis failed: {e}")
            sys.exit(1)

    def manage_test_coverage(self, args: argparse.Namespace) -> None:
        """Manage test coverage analysis and generation."""
        try:
            generator = TestSuiteGenerator()

            if args.analyze:
                self.logger.info("Analyzing test coverage gaps")
                analysis = generator.analyze_codebase(args.root_path)

                # Display summary
                metrics = analysis["metrics"]
                print(f"\n{'='*60}")
                print("Test Coverage Analysis Results")
                print(f"{'='*60}")
                print(f"Total Modules: {metrics.total_modules}")
                print(f"Tested Modules: {metrics.tested_modules}")
                print(f"Total Functions/Methods: {metrics.total_functions}")
                print(f"Tested Functions/Methods: {metrics.tested_functions}")
                print(f"Coverage Percentage: {metrics.coverage_percentage:.1f}%")
                print(f"Test Quality Score: {metrics.test_quality_score:.1f}/100")
                print(f"Total Coverage Gaps: {len(analysis['coverage_gaps'])}")

                # Show priority breakdown
                gaps = analysis["coverage_gaps"]
                high_priority = len([g for g in gaps if g.test_priority == "high"])
                medium_priority = len([g for g in gaps if g.test_priority == "medium"])
                low_priority = len([g for g in gaps if g.test_priority == "low"])

                print(f"\nCoverage Gaps by Priority:")
                print(f"  High Priority: {high_priority}")
                print(f"  Medium Priority: {medium_priority}")
                print(f"  Low Priority: {low_priority}")

                # Show top gaps
                if gaps:
                    print(f"\nTop 10 Coverage Gaps:")
                    sorted_gaps = sorted(
                        gaps, key=lambda g: g.complexity_score, reverse=True
                    )
                    for i, gap in enumerate(sorted_gaps[:10], 1):
                        print(
                            f"  {i:2d}. {gap.module_name}.{gap.function_name} "
                            f"(Complexity: {gap.complexity_score}, Priority: {gap.test_priority})"
                        )

                print(f"\n{'='*60}")

            elif args.generate:
                self.logger.info(f"Generating missing tests to {args.output_dir}")
                analysis = generator.analyze_codebase(args.root_path)
                generated_files = generator.generate_missing_tests(
                    analysis, args.output_dir
                )

                print(f"\nGenerated {len(generated_files)} test files:")
                for module_name, file_path in generated_files.items():
                    print(f"  - {module_name}: {file_path}")

                print(f"\nTo run the generated tests:")
                print(
                    f"  python -m apgi_framework.cli batch-test --test-paths {args.output_dir}/"
                )

            elif args.report:
                self.logger.info(f"Generating coverage report: {args.report_file}")
                analysis = generator.analyze_codebase(args.root_path)
                report_path = generator.generate_coverage_report(
                    analysis, args.report_file
                )
                print(f"Coverage report generated: {report_path}")

            else:
                self.logger.error(
                    "Must specify one of: --analyze, --generate, --report"
                )
                sys.exit(1)

        except Exception as e:
            self.logger.error(f"Test coverage management failed: {e}")
            sys.exit(1)

    def _display_batch_test_summary(self, summary: Any) -> None:
        """Display batch test execution summary."""
        print(f"\n{'='*80}")
        print("APGI Framework Advanced Batch Test Results")
        print(f"{'='*80}")

        print(f"Total Tests: {summary.total_tests}")
        print(f"Passed: {summary.passed}")
        print(f"Failed: {summary.failed}")
        print(f"Skipped: {summary.skipped}")
        print(f"Errors: {summary.errors}")
        print(f"Success Rate: {(summary.passed/summary.total_tests*100):.1f}%")
        print(f"Total Duration: {summary.total_duration:.2f} seconds")
        print(f"Start Time: {summary.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {summary.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Show failed tests if any
        failed_tests = [
            r for r in summary.test_results if r.status in ["failed", "error"]
        ]
        if failed_tests:
            print(f"\nFailed Tests ({len(failed_tests)}):")
            for result in failed_tests[:10]:  # Show first 10
                print(
                    f"  - {result.test_name}: {result.error_message or 'No error message'}"
                )
            if len(failed_tests) > 10:
                print(f"  ... and {len(failed_tests) - 10} more")

        print(f"\n{'='*80}\n")

    def _save_batch_test_summary(self, summary: Any) -> None:
        """Save batch test summary to file."""
        try:
            output_dir = Path("test_results")
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"batch_test_summary_{timestamp}.json"

            # Convert summary to dictionary for JSON serialization
            summary_dict = {
                "total_tests": summary.total_tests,
                "passed": summary.passed,
                "failed": summary.failed,
                "skipped": summary.skipped,
                "errors": summary.errors,
                "total_duration": summary.total_duration,
                "start_time": (
                    summary.start_time.isoformat()
                    if hasattr(summary.start_time, "isoformat")
                    else str(summary.start_time)
                ),
                "end_time": (
                    summary.end_time.isoformat()
                    if hasattr(summary.end_time, "isoformat")
                    else str(summary.end_time)
                ),
                "test_results": [
                    {
                        "test_name": result.test_name,
                        "test_file": result.test_file,
                        "status": result.status,
                        "duration": result.duration,
                        "output": result.output,
                        "error_message": result.error_message,
                        "traceback": result.traceback,
                        "start_time": (
                            result.start_time.isoformat()
                            if result.start_time
                            and hasattr(result.start_time, "isoformat")
                            else str(result.start_time)
                        ),
                        "end_time": (
                            result.end_time.isoformat()
                            if result.end_time and hasattr(result.end_time, "isoformat")
                            else str(result.end_time)
                        ),
                    }
                    for result in summary.test_results
                ],
                "execution_metadata": summary.execution_metadata,
            }

            with open(filename, "w") as f:
                json.dump(summary_dict, f, indent=2, default=str)

            self.logger.info(f"Batch test summary saved to {filename}")

        except Exception as e:
            self.logger.warning(f"Failed to save batch test summary: {e}")

    def _list_test_results(self) -> None:
        """List recent test result files."""
        results_dir = Path("test_results")
        if not results_dir.exists():
            print("No test results directory found")
            return

        result_files = sorted(
            results_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True
        )

        if not result_files:
            print("No test result files found")
            return

        print(f"\nRecent Test Results:")
        print(f"{'='*60}")
        for i, result_file in enumerate(result_files[:20], 1):  # Show last 20
            mtime = datetime.fromtimestamp(result_file.stat().st_mtime)
            size = result_file.stat().st_size
            print(
                f"{i:2d}. {result_file.name} ({mtime.strftime('%Y-%m-%d %H:%M:%S')}, {size} bytes)"
            )

    def _show_test_result(self, result_file: str) -> None:
        """Show details of a specific test result file."""
        results_dir = Path("test_results")
        file_path = (
            results_dir / result_file
            if not Path(result_file).is_absolute()
            else Path(result_file)
        )

        if not file_path.exists():
            self.logger.error(f"Test result file not found: {file_path}")
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            print(f"\nTest Result Details: {result_file}")
            print(f"{'='*60}")

            if "summary" in data:
                summary = data["summary"]
                print(f"Total Tests: {summary.get('total_tests', 'N/A')}")
                print(f"Passed: {summary.get('passed', 'N/A')}")
                print(f"Failed: {summary.get('failed', 'N/A')}")
                print(f"Skipped: {summary.get('skipped', 'N/A')}")
                print(f"Errors: {summary.get('errors', 'N/A')}")
                print(f"Duration: {summary.get('total_duration', 'N/A')} seconds")
                print(f"Start Time: {summary.get('start_time', 'N/A')}")
                print(f"End Time: {summary.get('end_time', 'N/A')}")

            if "test_results" in data:
                print(f"\nTest Results:")
                for result in data["test_results"][:10]:  # Show first 10
                    print(
                        f"  - {result.get('test_name', 'Unknown')}: {result.get('status', 'Unknown')}"
                    )
                    if result.get("error_message"):
                        print(f"    Error: {result['error_message'][:100]}...")

                if len(data["test_results"]) > 10:
                    print(f"  ... and {len(data['test_results']) - 10} more tests")

            print(f"\n{'='*60}\n")

        except Exception as e:
            self.logger.error(f"Failed to read test result file: {e}")

    def _rerun_failed_tests(self, result_file: str) -> None:
        """Re-run failed tests from a previous result file."""
        try:
            self.logger.info(f"Re-running failed tests from {result_file}")

            summary = run_failed_tests(result_file, parallel=True)

            # Display results
            self._display_batch_test_summary(summary)

            # Save new results
            self._save_batch_test_summary(summary)

        except Exception as e:
            self.logger.error(f"Failed to re-run failed tests: {e}")
            sys.exit(1)

    def _clean_test_results(self) -> None:
        """Clean old test result files."""
        results_dir = Path("test_results")
        if not results_dir.exists():
            print("No test results directory to clean")
            return

        # Remove files older than 7 days
        import time

        current_time = time.time()
        cutoff_time = current_time - (7 * 24 * 60 * 60)  # 7 days ago

        removed_count = 0
        for result_file in results_dir.glob("*.json"):
            if result_file.stat().st_mtime < cutoff_time:
                result_file.unlink()
                removed_count += 1

        print(f"Cleaned {removed_count} old test result files")

    def _display_test_result(self, result: Any, test_type: str) -> None:
        """Display individual test result."""
        print(f"\n{'='*60}")
        print(f"APGI Framework Falsification Test Results: {test_type.upper()}")
        print(f"{'='*60}")

        if hasattr(result, "is_falsified"):
            print(
                f"Falsification Status: {'FALSIFIED' if result.is_falsified else 'NOT FALSIFIED'}"
            )
            print(f"Confidence Level: {result.confidence_level:.3f}")
            print(f"Effect Size: {result.effect_size:.3f}")
            print(f"P-value: {result.p_value:.6f}")
            print(f"Statistical Power: {result.statistical_power:.3f}")
        else:
            print(f"Result: {result}")

        print(f"{'='*60}\n")

    def _display_batch_results(self, results: Dict[str, Any]) -> None:
        """Display batch experiment results."""
        print(f"\n{'='*80}")
        print("APGI Framework Batch Falsification Test Results")
        print(f"{'='*80}")

        for test_type, result in results.items():
            print(f"\n{test_type.upper()}:")
            if "error" in result:
                print(f"  ERROR: {result['error']}")
            elif hasattr(result, "is_falsified"):
                print(f"  Falsified: {'YES' if result.is_falsified else 'NO'}")
                print(f"  Confidence: {result.confidence_level:.3f}")
                print(f"  Effect Size: {result.effect_size:.3f}")
                print(f"  P-value: {result.p_value:.6f}")
            else:
                print(f"  Result: {result}")

        print(f"\n{'='*80}\n")

    def _display_detailed_validation(self, results: Dict[str, Any]) -> None:
        """Display detailed validation results."""
        print(f"\n{'='*60}")
        print("System Validation Results (Detailed)")
        print(f"{'='*60}")

        for component, status in results.items():
            if component != "overall":
                status_str = "PASS" if status else "FAIL"
                print(f"{component.replace('_', ' ').title()}: {status_str}")

        overall_status = "PASS" if results.get("overall", False) else "FAIL"
        print(f"\nOverall Status: {overall_status}")
        print(f"{'='*60}\n")

    def _display_simple_validation(self, results: Dict[str, Any]) -> None:
        """Display simple validation results."""
        overall_status = "PASS" if results.get("overall", False) else "FAIL"
        print(f"System Validation: {overall_status}")

    def _display_system_status(self, status: Dict[str, Any]) -> None:
        """Display system status."""
        print(f"\n{'='*50}")
        print("APGI Framework System Status")
        print(f"{'='*50}")

        for key, value in status.items():
            if key != "timestamp":
                display_key = key.replace("_", " ").title()
                display_value = (
                    "YES" if value else "NO" if isinstance(value, bool) else str(value)
                )
                print(f"{display_key}: {display_value}")

        print(f"Last Updated: {status.get('timestamp', 'Unknown')}")
        print(f"{'='*50}\n")

    def _save_test_result(self, result: Any, test_type: str) -> None:
        """Save individual test result to file."""
        try:
            output_dir = Path(
                self.controller.config_manager.get_experimental_config().output_directory
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"{test_type}_result_{timestamp}.json"

            # Convert result to dictionary for JSON serialization
            if hasattr(result, "__dict__"):
                result_dict = result.__dict__
            else:
                result_dict = {"result": str(result)}

            with open(filename, "w") as f:
                json.dump(result_dict, f, indent=2, default=str)

            self.logger.info(f"Results saved to {filename}")

        except Exception as e:
            self.logger.warning(f"Failed to save results: {e}")

    def _save_batch_results(self, results: Dict[str, Any]) -> None:
        """Save batch experiment results to file."""
        try:
            output_dir = Path(
                self.controller.config_manager.get_experimental_config().output_directory
            )
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"batch_results_{timestamp}.json"

            # Convert results to dictionary for JSON serialization
            results_dict = {}
            for test_type, result in results.items():
                if hasattr(result, "__dict__"):
                    results_dict[test_type] = result.__dict__
                else:
                    results_dict[test_type] = {"result": str(result)}

            with open(filename, "w") as f:
                json.dump(results_dict, f, indent=2, default=str)

            self.logger.info(f"Batch results saved to {filename}")

        except Exception as e:
            self.logger.warning(f"Failed to save batch results: {e}")

    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            "apgi_parameters": {
                "extero_precision": 2.0,
                "intero_precision": 1.5,
                "extero_error": 1.2,
                "intero_error": 0.8,
                "somatic_gain": 1.3,
                "threshold": 3.5,
                "steepness": 2.0,
            },
            "experimental_config": {
                "n_trials": 1000,
                "n_participants": 100,
                "random_seed": None,
                "output_directory": "results",
                "log_level": "INFO",
                "save_intermediate": True,
                "p3b_threshold": 5.0,
                "gamma_plv_threshold": 0.3,
                "bold_z_threshold": 3.1,
                "pci_threshold": 0.4,
                "alpha_level": 0.05,
                "effect_size_threshold": 0.5,
                "power_threshold": 0.8,
            },
        }

    def _create_minimal_config(self) -> Dict[str, Any]:
        """Create minimal configuration."""
        return {
            "apgi_parameters": {"threshold": 3.5, "steepness": 2.0},
            "experimental_config": {"n_trials": 100, "output_directory": "results"},
        }

    def _create_comprehensive_config(self) -> Dict[str, Any]:
        """Create comprehensive configuration with all options."""
        config = self._create_default_config()

        # Add additional comprehensive options
        config["experimental_config"].update(
            {
                "detailed_logging": True,
                "save_raw_data": True,
                "generate_plots": True,
                "statistical_corrections": ["fdr", "bonferroni"],
                "bootstrap_iterations": 10000,
                "confidence_interval": 0.95,
            }
        )

        return config

    def run(self, args: List[str] = None) -> None:
        """Main entry point for the CLI."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)

        # Setup logging
        self.setup_logging(parsed_args.log_level)

        # Handle case where no command is provided
        if not parsed_args.command:
            parser.print_help()
            return

        # Initialize controller for commands that need it
        if parsed_args.command not in [
            "generate-config",
            "batch-test",
            "test-results",
            "test-analysis",
            "test-coverage",
        ]:
            self.initialize_controller(parsed_args.config)

        # Override output directory if provided
        if parsed_args.output_dir and self.controller:
            self.controller.config_manager.update_experimental_config(
                output_directory=parsed_args.output_dir
            )

        # Execute the requested command
        try:
            if parsed_args.command == "run-test":
                self.run_individual_test(parsed_args)
            elif parsed_args.command == "run-batch":
                self.run_batch_experiments(parsed_args)
            elif parsed_args.command == "batch-test":
                self.run_advanced_batch_tests(parsed_args)
            elif parsed_args.command == "test-results":
                self.manage_test_results(parsed_args)
            elif parsed_args.command == "test-analysis":
                self.analyze_test_results(parsed_args)
            elif parsed_args.command == "test-coverage":
                self.manage_test_coverage(parsed_args)
            elif parsed_args.command == "generate-config":
                self.generate_configuration(parsed_args)
            elif parsed_args.command == "validate-system":
                self.validate_system(parsed_args)
            elif parsed_args.command == "status":
                self.show_status(parsed_args)
            elif parsed_args.command == "set-params":
                self.set_parameters(parsed_args)
            else:
                self.logger.error(f"Unknown command: {parsed_args.command}")
                sys.exit(1)

        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            sys.exit(1)
        finally:
            # Cleanup
            if self.controller:
                try:
                    self.controller.shutdown_system()
                except Exception as e:
                    self.logger.warning(f"Error during cleanup: {e}")


def main():
    """Entry point for the CLI when run as a module."""
    cli = APGIFrameworkCLI()
    cli.run()


if __name__ == "__main__":
    main()
