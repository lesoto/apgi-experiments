#!/usr/bin/env python3
"""
Validation script for all 28 experiments in the APGI Experiment Registry.
Tests each experiment for basic execution and error handling.
"""

import sys
import traceback
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.run_experiments import EXPERIMENTS, run_experiment
from apgi_framework.logging.standardized_logging import get_logger
from apgi_framework.config.constants import ValidationConstants

logger = get_logger("experiment_validation")


class ExperimentValidator:
    """Validates all experiments in the registry."""

    def __init__(self):
        self.results = {}
        self.errors = {}

    def validate_single_experiment(
        self, experiment_name: str
    ) -> Tuple[bool, str, float]:
        """
        Validate a single experiment.

        Returns:
            Tuple of (success, message, execution_time)
        """
        logger.info(f"Validating experiment: {experiment_name}")
        start_time = time.time()

        try:
            # Try to run experiment with minimal parameters
            result = run_experiment(
                experiment_name,
                n_participants=ValidationConstants.MIN_TEST_PARTICIPANTS,  # Minimal for testing
                n_trials=ValidationConstants.MIN_TEST_TRIALS,  # Minimal for testing
                output_file=None,  # No output file for testing
            )

            execution_time = time.time() - start_time
            success = True
            message = f"Success: Completed in {execution_time:.2f}s"

        except ImportError as e:
            execution_time = time.time() - start_time
            success = False
            message = f"Import Error: {str(e)}"

        except AttributeError as e:
            execution_time = time.time() - start_time
            success = False
            message = f"Function Missing: {str(e)}"

        except Exception as e:
            execution_time = time.time() - start_time
            success = False
            message = f"Runtime Error: {str(e)}"
            # Store full traceback for debugging
            self.errors[experiment_name] = {
                "error": str(e),
                "traceback": traceback.format_exc(),
            }

        return success, message, execution_time

    def validate_all_experiments(self) -> Dict[str, Dict]:
        """Validate all experiments and return results."""
        logger.info(f"Starting validation of {len(EXPERIMENTS)} experiments")

        for experiment_name in sorted(EXPERIMENTS.keys()):
            success, message, execution_time = self.validate_single_experiment(
                experiment_name
            )

            self.results[experiment_name] = {
                "success": success,
                "message": message,
                "execution_time": execution_time,
            }

            logger.info(f"  {experiment_name}: {'✓' if success else '✗'} - {message}")

        return self.results

    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        total_experiments = len(self.results)
        successful_experiments = sum(1 for r in self.results.values() if r["success"])
        failed_experiments = total_experiments - successful_experiments

        report = []
        report.append("=" * 80)
        report.append("APGI EXPERIMENT VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Total Experiments: {total_experiments}")
        report.append(f"Successful: {successful_experiments}")
        report.append(f"Failed: {failed_experiments}")
        report.append(
            f"Success Rate: {(successful_experiments/total_experiments)*100:.1f}%"
        )
        report.append("")

        # Successful experiments
        if successful_experiments > 0:
            report.append("SUCCESSFUL EXPERIMENTS:")
            report.append("-" * 40)
            for name, result in self.results.items():
                if result["success"]:
                    report.append(f"  ✓ {name:<30} ({result['execution_time']:.2f}s)")
            report.append("")

        # Failed experiments
        if failed_experiments > 0:
            report.append("FAILED EXPERIMENTS:")
            report.append("-" * 40)
            for name, result in self.results.items():
                if not result["success"]:
                    report.append(f"  ✗ {name:<30} - {result['message']}")
            report.append("")

            # Detailed error information
            report.append("DETAILED ERROR INFORMATION:")
            report.append("-" * 40)
            for name, error_info in self.errors.items():
                report.append(f"\n{name}:")
                report.append(f"  Error: {error_info['error']}")
                report.append("  Traceback:")
                for line in error_info["traceback"].split("\n"):
                    if line.strip():
                        report.append(f"    {line}")

        # Performance summary
        report.append("\nPERFORMANCE SUMMARY:")
        report.append("-" * 40)
        execution_times = [
            r["execution_time"] for r in self.results.values() if r["success"]
        ]
        if execution_times:
            report.append(
                f"  Average execution time: {sum(execution_times)/len(execution_times):.2f}s"
            )
            report.append(f"  Fastest experiment: {min(execution_times):.2f}s")
            report.append(f"  Slowest experiment: {max(execution_times):.2f}s")

        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main validation function."""
    validator = ExperimentValidator()

    print("Starting APGI Experiment Validation...")
    print(f"Testing {len(EXPERIMENTS)} experiments...")
    print()

    # Validate all experiments
    results = validator.validate_all_experiments()

    # Generate and display report
    report = validator.generate_report()
    print(report)

    # Save report to file
    report_file = project_root / "experiment_validation_report.txt"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\nDetailed report saved to: {report_file}")

    # Return exit code based on success rate
    successful_count = sum(1 for r in results.values() if r["success"])
    total_count = len(results)

    if successful_count == total_count:
        print("\n🎉 All experiments validated successfully!")
        return 0
    elif successful_count > total_count * 0.8:  # 80% success rate
        print(f"\n⚠️  Most experiments successful ({successful_count}/{total_count})")
        return 1
    else:
        print(f"\n❌ Many experiments failed ({successful_count}/{total_count})")
        return 2


if __name__ == "__main__":
    sys.exit(main())
