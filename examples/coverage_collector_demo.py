#!/usr/bin/env python3
"""
Demonstration of CoverageCollector with coverage.py integration.

This script shows how to use the CoverageCollector to measure coverage
during test execution with persistence and retrieval capabilities.
"""

import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from apgi_framework.test_enhancement.coverage.coverage_collector import (
    CoverageCollector,
)
from apgi_framework.test_enhancement.models import TestConfiguration, TestExecution


def create_sample_module():
    """Create a sample Python module for coverage demonstration."""
    temp_dir = tempfile.mkdtemp()
    sample_file = os.path.join(temp_dir, "sample_module.py")

    with open(sample_file, "w") as f:
        f.write(
            """
def calculate_area(length, width):
    '''Calculate the area of a rectangle.'''
    if length <= 0 or width <= 0:
        raise ValueError("Length and width must be positive")
    return length * width

def calculate_perimeter(length, width):
    '''Calculate the perimeter of a rectangle.'''
    return 2 * (length + width)

def unused_function():
    '''This function will not be called, showing uncovered code.'''
    return "This line is never executed"

class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width
    
    def area(self):
        return calculate_area(self.length, self.width)
    
    def perimeter(self):
        return calculate_perimeter(self.length, self.width)
"""
        )

    return temp_dir, sample_file


def demonstrate_coverage_collection():
    """Demonstrate coverage collection with the CoverageCollector."""
    print("=== CoverageCollector Demonstration ===\n")

    # Create sample module
    temp_dir, sample_file = create_sample_module()
    print(f"Created sample module at: {sample_file}")

    try:
        # Initialize CoverageCollector
        collector = CoverageCollector(
            source_paths=[temp_dir],
            omit_patterns=[],  # Don't omit anything for this demo
            branch_coverage=True,
        )
        print("CoverageCollector initialized")

        # Create test execution context
        test_execution = TestExecution(
            execution_id="demo_execution",
            selected_tests=[],
            configuration=TestConfiguration(),
            start_time=datetime.now(),
        )
        print(f"Test execution context created: {test_execution.execution_id}")

        # Use CoverageCollector as context manager
        with collector:
            print("Coverage measurement started")

            # Import and execute the sample module
            sys.path.insert(0, temp_dir)
            import importlib.util

            spec = importlib.util.spec_from_file_location("sample_module", sample_file)
            sample_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sample_module)

            # Execute some functions (but not all)
            print("Executing sample code...")
            area = sample_module.calculate_area(5, 3)
            print(f"Area calculated: {area}")

            rect = sample_module.Rectangle(4, 6)
            rect_area = rect.area()
            print(f"Rectangle area: {rect_area}")

            # Note: We're not calling calculate_perimeter or unused_function
            # This will show up in coverage gaps

        print("Coverage measurement stopped")

        # Collect coverage data
        coverage_data = collector.collect_coverage(test_execution)
        print(f"Coverage data collected for execution: {coverage_data.execution_id}")

        # Display coverage results
        print("\n=== Coverage Results ===")
        print(f"Overall coverage: {coverage_data.overall_coverage:.2f}%")
        print(f"Timestamp: {coverage_data.timestamp}")

        if coverage_data.line_coverage:
            print("\nLine Coverage by File:")
            for file_path, coverage in coverage_data.line_coverage.items():
                filename = os.path.basename(file_path)
                print(f"  {filename}: {coverage:.2f}%")

        if coverage_data.module_coverage:
            print("\nModule Coverage Details:")
            for module_name, module_cov in coverage_data.module_coverage.items():
                print(f"  Module: {module_cov.module_name}")
                print(
                    f"    Lines: {module_cov.covered_lines}/"
                    f"{module_cov.total_lines} ({module_cov.line_coverage:.2f}%)"
                )
                print(
                    f"    Branches: {module_cov.covered_branches}/"
                    f"{module_cov.total_branches} ({module_cov.branch_coverage:.2f}%)"
                )
                if module_cov.uncovered_lines:
                    print(f"    Uncovered lines: {module_cov.uncovered_lines}")

        # Demonstrate persistence
        coverage_file = os.path.join(temp_dir, "coverage_data.json")
        collector.save_coverage_data(coverage_data, coverage_file)
        print(f"\nCoverage data saved to: {coverage_file}")

        # Demonstrate retrieval
        loaded_data = collector.load_coverage_data(coverage_file)
        if loaded_data:
            print("Coverage data loaded successfully")
            print(f"Loaded execution ID: {loaded_data.execution_id}")
            print(f"Loaded overall coverage: {loaded_data.overall_coverage:.2f}%")

        # Demonstrate caching
        cached_data = collector.get_cached_coverage_data("demo_execution")
        if cached_data:
            print(f"Coverage data retrieved from cache: {cached_data.execution_id}")

        print("\n=== Demonstration Complete ===")

    finally:
        # Cleanup
        if temp_dir in sys.path:
            sys.path.remove(temp_dir)

        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
        print("Temporary files cleaned up")


if __name__ == "__main__":
    demonstrate_coverage_collection()
