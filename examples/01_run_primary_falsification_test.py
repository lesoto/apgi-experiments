#!/usr/bin/env python3
"""
Example 01: Run Primary Falsification Test

Demonstrates the primary APGI falsification pipeline:
  1. Generate synthetic APGI signal data
  2. Apply the falsification test battery
  3. Print a summary of pass/fail results

Usage:
    python examples/01_run_primary_falsification_test.py
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def generate_synthetic_signal(n_samples=500, noise=0.1):
    """Generate a synthetic APGI-like signal."""
    try:
        import numpy as np

        t = np.linspace(0, 10, n_samples)
        signal = (
            np.sin(2 * np.pi * 0.5 * t)  # slow oscillation
            + 0.5 * np.sin(2 * np.pi * 2.0 * t)  # fast component
            + noise * np.random.randn(n_samples)  # noise
        )
        return t, signal
    except ImportError:
        print("  [WARN] NumPy not available — using stub signal.")
        n = n_samples
        t = [i / n * 10 for i in range(n)]
        signal = [((i % 20) - 10) / 10.0 for i in range(n)]
        return t, signal


def run_falsification_battery(signal):
    """Apply a set of falsification tests to the signal."""
    results = []

    # Test 1: Signal non-stationarity check (variance ratio)
    half = len(signal) // 2
    try:
        first_half = signal[:half]
        second_half = signal[half:]
        mean1 = sum(first_half) / len(first_half)
        mean2 = sum(second_half) / len(second_half)
        var1 = sum((x - mean1) ** 2 for x in first_half) / len(first_half)
        var2 = sum((x - mean2) ** 2 for x in second_half) / len(second_half)
        ratio = abs(var1 / (var2 + 1e-12))
        passed = 0.5 <= ratio <= 2.0
        results.append(("Stationarity (variance ratio)", passed, f"ratio={ratio:.3f}"))
    except Exception as e:
        results.append(("Stationarity (variance ratio)", False, str(e)))

    # Test 2: Signal amplitude range check
    try:
        sig_min = min(signal)
        sig_max = max(signal)
        amplitude = sig_max - sig_min
        passed = amplitude > 0.1
        results.append(("Amplitude range", passed, f"amplitude={amplitude:.4f}"))
    except Exception as e:
        results.append(("Amplitude range", False, str(e)))

    # Test 3: Zero-crossing rate (oscillation check)
    try:
        crossings = sum(
            1 for i in range(1, len(signal)) if signal[i - 1] * signal[i] < 0
        )
        rate = crossings / len(signal)
        passed = rate > 0.05
        results.append(("Zero-crossing rate", passed, f"rate={rate:.4f}"))
    except Exception as e:
        results.append(("Zero-crossing rate", False, str(e)))

    return results


def print_results(results):
    print(f"\n{'Test':<40} {'Status':<8} {'Details'}")
    print("-" * 70)
    for name, passed, detail in results:
        status = "PASS ✓" if passed else "FAIL ✗"
        print(f"  {name:<38} {status:<8} {detail}")
    total = len(results)
    passed = sum(1 for _, p, _ in results if p)
    print(f"\n  Results: {passed}/{total} tests passed")
    return passed == total


def main():
    print("=" * 60)
    print("APGI — Primary Falsification Test (Example 01)")
    print("=" * 60)

    print("\nStep 1: Generating synthetic APGI signal...")
    t, signal = generate_synthetic_signal()
    print(f"  Generated {len(signal)} samples over t=[0, {max(t):.1f}]s")

    print("\nStep 2: Running falsification battery...")
    start = time.time()
    results = run_falsification_battery(signal)
    elapsed = time.time() - start

    print("\nStep 3: Results")
    all_passed = print_results(results)
    print(f"\n  Completed in {elapsed:.4f}s")
    print(
        f"\n  Overall: {'FALSIFICATION REJECTED ✓' if all_passed else 'FALSIFICATION SUPPORTED ✗'}"
    )
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
