"""
Example 3: Custom Analysis of Saved Results

This example demonstrates how to load saved experimental results
and perform custom analyses, including:
- Loading and parsing result files
- Statistical re-analysis
- Comparative analysis across experiments
- Generating custom visualizations
- Extracting specific metrics
"""

import sys
from pathlib import Path
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from apgi_framework.data import StorageManager
from apgi_framework.core import FalsificationResult
import logging

# Setup logging with standardized system
try:
    from apgi_framework.logging.standardized_logging import get_logger

    logger = get_logger("custom_analysis_example")
except ImportError:
    # Fallback to basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger: Any = logging.getLogger(__name__)


def load_saved_results(results_directory: str = "results") -> List[Dict[str, Any]]:
    """
    Load all saved result files from a directory.

    Args:
        results_directory: Path to directory containing result files

    Returns:
        List of result dictionaries
    """
    results_path = Path(results_directory)

    if not results_path.exists():
        logger.warning(f"Results directory not found: {results_directory}")
        return []

    # Find all JSON result files
    result_files = list(results_path.glob("**/*_result_*.json"))

    logger.info(f"Found {len(result_files)} result files")

    results = []
    for file_path in result_files:
        try:
            with open(file_path, "r") as f:
                result_data = json.load(f)
                result_data["_file_path"] = str(file_path)
                result_data["_file_name"] = file_path.name
                results.append(result_data)
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")

    logger.info(f"Successfully loaded {len(results)} results")
    return results


def analyze_falsification_rates(results: List[Dict[str, Any]]):
    """
    Example 3A: Analyze falsification rates across experiments.
    """
    logger.info("=" * 60)
    logger.info("Example 3A: Falsification Rate Analysis")
    logger.info("=" * 60)

    if not results:
        logger.warning("No results to analyze")
        return

    # Calculate overall falsification rate
    falsified_count = sum(1 for r in results if r.get("is_falsified", False))
    total_count = len(results)
    falsification_rate = falsified_count / total_count if total_count > 0 else 0

    logger.info("\nOverall Statistics:")
    logger.info(f"  Total experiments: {total_count}")
    logger.info(f"  Falsified: {falsified_count}")
    logger.info(f"  Not falsified: {total_count - falsified_count}")
    logger.info(f"  Falsification rate: {falsification_rate:.1%}")

    # Analyze by test type if available
    test_types = {}
    for r in results:
        test_type = r.get("test_type", "unknown")
        if test_type not in test_types:
            test_types[test_type] = {"total": 0, "falsified": 0}
        test_types[test_type]["total"] += 1
        if r.get("is_falsified", False):
            test_types[test_type]["falsified"] += 1

    if len(test_types) > 1:
        logger.info("\nFalsification Rates by Test Type:")
        for test_type, counts in test_types.items():
            rate = counts["falsified"] / counts["total"] if counts["total"] > 0 else 0
            logger.info(
                f"  {test_type}: {counts['falsified']}/{counts['total']} ({rate:.1%})"
            )

    # Confidence level distribution
    confidence_levels = [r.get("confidence_level", 0) for r in results]
    if confidence_levels:
        logger.info(f"\nConfidence Level Statistics:")
        logger.info(f"  Mean: {np.mean(confidence_levels):.3f}")
        logger.info(f"  Median: {np.median(confidence_levels):.3f}")
        logger.info(f"  Std Dev: {np.std(confidence_levels):.3f}")
        logger.info(f"  Min: {np.min(confidence_levels):.3f}")
        logger.info(f"  Max: {np.max(confidence_levels):.3f}")

    logger.info("=" * 60 + "\n")


def analyze_statistical_power(results: List[Dict[str, Any]]):
    """
    Example 3B: Analyze statistical power across experiments.
    """
    logger.info("=" * 60)
    logger.info("Example 3B: Statistical Power Analysis")
    logger.info("=" * 60)

    if not results:
        logger.warning("No results to analyze")
        return

    # Extract power values
    power_values = [
        r.get("statistical_power", 0) for r in results if "statistical_power" in r
    ]

    if not power_values:
        logger.warning("No statistical power data available")
        return

    logger.info(f"\nStatistical Power Summary:")
    logger.info(f"  Number of experiments: {len(power_values)}")
    logger.info(f"  Mean power: {np.mean(power_values):.3f}")
    logger.info(f"  Median power: {np.median(power_values):.3f}")
    logger.info(f"  Std Dev: {np.std(power_values):.3f}")

    # Categorize by power level
    high_power = sum(1 for p in power_values if p >= 0.8)
    medium_power = sum(1 for p in power_values if 0.5 <= p < 0.8)
    low_power = sum(1 for p in power_values if p < 0.5)

    logger.info("\nPower Distribution:")
    logger.info(
        f"  High power (≥0.8): {high_power} ({high_power / len(power_values):.1%})"
    )
    logger.info(
        f"  Medium power (0.5-0.8): {medium_power} ({medium_power / len(power_values):.1%})"
    )
    logger.info(
        f"  Low power (<0.5): {low_power} ({low_power / len(power_values):.1%})"
    )

    # Identify underpowered experiments
    if low_power > 0:
        logger.info(
            f"\n[WARN] Warning: {low_power} experiments had low statistical power"
        )
        logger.info("  Consider increasing sample size for future experiments")

    logger.info("=" * 60 + "\n")


def analyze_effect_sizes(results: List[Dict[str, Any]]):
    """
    Example 3C: Analyze effect sizes and their relationship to falsification.
    """
    logger.info("=" * 60)
    logger.info("Example 3C: Effect Size Analysis")
    logger.info("=" * 60)

    if not results:
        logger.warning("No results to analyze")
        return

    # Extract effect sizes
    effect_sizes = [r.get("effect_size", 0) for r in results if "effect_size" in r]

    if not effect_sizes:
        logger.warning("No effect size data available")
        return

    logger.info(f"\nEffect Size Summary (Cohen's d):")
    logger.info(f"  Number of experiments: {len(effect_sizes)}")
    logger.info(f"  Mean: {np.mean(effect_sizes):.3f}")
    logger.info(f"  Median: {np.median(effect_sizes):.3f}")
    logger.info(f"  Std Dev: {np.std(effect_sizes):.3f}")
    logger.info(f"  Range: [{np.min(effect_sizes):.3f}, {np.max(effect_sizes):.3f}]")

    # Categorize by effect size magnitude
    small = sum(1 for d in effect_sizes if abs(d) < 0.5)
    medium = sum(1 for d in effect_sizes if 0.5 <= abs(d) < 0.8)
    large = sum(1 for d in effect_sizes if abs(d) >= 0.8)

    logger.info(f"\nEffect Size Distribution:")
    logger.info(f"  Small (|d| < 0.5): {small} ({small / len(effect_sizes):.1%})")
    logger.info(
        f"  Medium (0.5 ≤ |d| < 0.8): {medium} ({medium / len(effect_sizes):.1%})"
    )
    logger.info(f"  Large (|d| ≥ 0.8): {large} ({large / len(effect_sizes):.1%})")

    # Relationship between effect size and falsification
    falsified_results = [
        r for r in results if r.get("is_falsified", False) and "effect_size" in r
    ]
    not_falsified_results = [
        r for r in results if not r.get("is_falsified", False) and "effect_size" in r
    ]

    if falsified_results and not_falsified_results:
        falsified_effects = [r["effect_size"] for r in falsified_results]
        not_falsified_effects = [r["effect_size"] for r in not_falsified_results]

        logger.info("\nEffect Size by Falsification Status:")
        logger.info(f"  Falsified experiments:")
        logger.info(f"    Mean: {np.mean(falsified_effects):.3f}")
        logger.info(f"    Median: {np.median(falsified_effects):.3f}")
        logger.info(f"  Not falsified experiments:")
        logger.info(f"    Mean: {np.mean(not_falsified_effects):.3f}")
        logger.info(f"    Median: {np.median(not_falsified_effects):.3f}")

    logger.info("=" * 60 + "\n")


def compare_experiments(results: List[Dict[str, Any]]):
    """
    Example 3D: Compare multiple experiments side-by-side.
    """
    logger.info("=" * 60)
    logger.info("Example 3D: Experiment Comparison")
    logger.info("=" * 60)

    if len(results) < 2:
        logger.warning("Need at least 2 experiments for comparison")
        return

    # Sort by confidence level
    sorted_results = sorted(
        results, key=lambda x: x.get("confidence_level", 0), reverse=True
    )

    # Display top experiments
    logger.info(f"\nTop 5 Experiments by Confidence Level:")
    logger.info(
        f"{'Rank':<6} {'File':<30} {'Falsified':<12} {'Confidence':<12} {'P-value':<12}"
    )
    logger.info("-" * 80)

    for idx, result in enumerate(sorted_results[:5], 1):
        file_name = result.get("_file_name", "unknown")[:28]
        falsified = "YES" if result.get("is_falsified", False) else "NO"
        confidence = result.get("confidence_level", 0)
        p_value = result.get("p_value", 1.0)

        logger.info(
            f"{idx:<6} {file_name:<30} {falsified:<12} {confidence:<12.3f} {p_value:<12.6f}"
        )

    # Compare falsified vs not falsified
    falsified = [r for r in results if r.get("is_falsified", False)]
    not_falsified = [r for r in results if not r.get("is_falsified", False)]

    if falsified and not_falsified:
        logger.info("\nComparative Statistics:")
        logger.info(f"\nFalsified Experiments (n={len(falsified)}):")
        logger.info(
            f"  Mean confidence: {np.mean([r.get('confidence_level', 0) for r in falsified]):.3f}"
        )
        logger.info(
            f"  Mean effect size: {np.mean([r.get('effect_size', 0) for r in falsified]):.3f}"
        )
        logger.info(
            f"  Mean p-value: {np.mean([r.get('p_value', 1.0) for r in falsified]):.6f}"
        )

        logger.info(f"\nNot Falsified Experiments (n={len(not_falsified)}):")
        logger.info(
            f"  Mean confidence: {np.mean([r.get('confidence_level', 0) for r in not_falsified]):.3f}"
        )
        logger.info(
            f"  Mean effect size: {np.mean([r.get('effect_size', 0) for r in not_falsified]):.3f}"
        )
        logger.info(
            f"  Mean p-value: {np.mean([r.get('p_value', 1.0) for r in not_falsified]):.6f}"
        )

    logger.info("=" * 60 + "\n")


def extract_custom_metrics(results: List[Dict[str, Any]]):
    """
    Example 3E: Extract and analyze custom metrics.
    """
    logger.info("=" * 60)
    logger.info("Example 3E: Custom Metrics Extraction")
    logger.info("=" * 60)

    if not results:
        logger.warning("No results to analyze")
        return

    # Extract all available metrics
    all_keys = set()
    for r in results:
        all_keys.update(r.keys())

    # Remove metadata keys
    metadata_keys = {"_file_path", "_file_name"}
    metric_keys = all_keys - metadata_keys

    logger.info(f"\nAvailable Metrics ({len(metric_keys)}):")
    for key in sorted(metric_keys):
        # Count how many results have this metric
        count = sum(1 for r in results if key in r)
        coverage = count / len(results) * 100
        logger.info(f"  {key}: {count}/{len(results)} ({coverage:.0f}%)")

    # Create summary statistics for numeric metrics
    logger.info(f"\nNumeric Metric Summary:")
    for key in sorted(metric_keys):
        values = []
        for r in results:
            if key in r:
                val = r[key]
                if isinstance(val, (int, float)) and not isinstance(val, bool):
                    values.append(val)

        if values:
            logger.info(f"\n  {key}:")
            logger.info(f"    Count: {len(values)}")
            logger.info(f"    Mean: {np.mean(values):.4f}")
            logger.info(f"    Std: {np.std(values):.4f}")
            logger.info(f"    Min: {np.min(values):.4f}")
            logger.info(f"    Max: {np.max(values):.4f}")

    logger.info("\n" + "=" * 60 + "\n")


def export_analysis_report(
    results: List[Dict[str, Any]], output_file: str = "analysis_report.json"
):
    """
    Export comprehensive analysis report.
    """
    logger.info("=" * 60)
    logger.info("Exporting Analysis Report")
    logger.info("=" * 60)

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_experiments": len(results),
        "summary": {
            "falsified_count": sum(1 for r in results if r.get("is_falsified", False)),
            "falsification_rate": (
                sum(1 for r in results if r.get("is_falsified", False)) / len(results)
                if results
                else 0
            ),
        },
        "statistics": {},
        "experiments": results,
    }

    # Add statistical summaries
    if results:
        confidence_levels = [r.get("confidence_level", 0) for r in results]
        effect_sizes = [r.get("effect_size", 0) for r in results if "effect_size" in r]
        p_values = [r.get("p_value", 1.0) for r in results if "p_value" in r]

        report["statistics"] = {
            "confidence_level": {
                "mean": float(np.mean(confidence_levels)),
                "median": float(np.median(confidence_levels)),
                "std": float(np.std(confidence_levels)),
            },
            "effect_size": {
                "mean": float(np.mean(effect_sizes)) if effect_sizes else None,
                "median": float(np.median(effect_sizes)) if effect_sizes else None,
                "std": float(np.std(effect_sizes)) if effect_sizes else None,
            },
            "p_value": {
                "mean": float(np.mean(p_values)) if p_values else None,
                "median": float(np.median(p_values)) if p_values else None,
            },
        }

    # Save report
    output_path = Path("results/analysis") / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    logger.info(f"\nAnalysis report saved to: {output_path}")
    logger.info("=" * 60 + "\n")


def run_metabolic_cost_experiment(**kwargs):
    """
    Wrapper function for metabolic_cost experiment.
    Maps to falsification rate analysis.
    """
    results = load_saved_results("results")
    analyze_falsification_rates(results)
    return results


def run_attentional_blink_experiment(**kwargs):
    """Wrapper for attentional_blink experiment."""
    results = load_saved_results("results")
    analyze_falsification_rates(results)
    return results


def run_stroop_effect_experiment(**kwargs):
    """Wrapper for stroop_effect experiment."""
    results = load_saved_results("results")
    analyze_falsification_rates(results)
    return results


def run_binocular_rivalry_experiment(**kwargs):
    """Wrapper for binocular_rivalry experiment."""
    results = load_saved_results("results")
    analyze_falsification_rates(results)
    return results


def run_working_memory_span_experiment(**kwargs):
    """Wrapper for working_memory_span experiment."""
    results = load_saved_results("results")
    analyze_falsification_rates(results)
    return results


def run_navon_task_experiment(**kwargs):
    """Wrapper for navon_task experiment."""
    results = load_saved_results("results")
    analyze_falsification_rates(results)
    return results


def run_time_estimation_experiment(**kwargs):
    """Wrapper for time_estimation experiment."""
    results = load_saved_results("results")
    analyze_falsification_rates(results)
    return results


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("APGI Framework - Custom Analysis Examples")
    print("=" * 70 + "\n")

    # Load saved results
    print("Loading saved results...")
    results = load_saved_results("results")

    if not results:
        print("\n[WARN] No saved results found. Run some experiments first!")
        print("Try running: python examples/01_run_primary_falsification_test.py")
        sys.exit(0)

    print(f"Loaded {len(results)} results\n")
    print("-" * 70 + "\n")

    # Run analyses
    analyze_falsification_rates(results)
    analyze_statistical_power(results)
    analyze_effect_sizes(results)
    compare_experiments(results)
    extract_custom_metrics(results)

    # Export comprehensive report
    export_analysis_report(results)

    print("=" * 70)
    print("All custom analyses completed successfully!")
    print("=" * 70 + "\n")
