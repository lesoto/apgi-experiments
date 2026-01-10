"""
Testing module for APGI Framework

This module provides comprehensive testing capabilities including:
- Batch test execution
- Test result persistence
- Performance monitoring
- Test utilities and fixtures
"""

from .batch_runner import (
    BatchTestRunner,
    TestResult,
    BatchExecutionSummary,
    run_all_tests,
    run_unit_tests,
    run_integration_tests,
    run_research_tests,
    run_failed_tests,
)
from .persistence import (
    TestResultPersistence,
    TestExecutionRecord,
    BatchExecutionRecord,
    get_persistence_manager,
    store_test_results,
    get_test_performance_report,
)

__all__ = [
    "BatchTestRunner",
    "TestResult",
    "BatchExecutionSummary",
    "run_all_tests",
    "run_unit_tests",
    "run_integration_tests",
    "run_research_tests",
    "run_failed_tests",
    "TestResultPersistence",
    "TestExecutionRecord",
    "BatchExecutionRecord",
    "get_persistence_manager",
    "store_test_results",
    "get_test_performance_report",
]
