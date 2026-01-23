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
from .ci_integrator import (
    CIIntegrator,
    CIConfiguration,
    ChangeImpact,
    ChangeAnalyzer,
    PreCommitHookManager,
    TestExecutionResult,
)
from .notification_manager import (
    NotificationManager,
    NotificationChannel,
    TestFailureNotification,
    TestHistoryTracker,
    create_email_channel,
    create_slack_channel,
    create_teams_channel,
    create_file_channel,
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
    "CIIntegrator",
    "CIConfiguration",
    "ChangeImpact",
    "ChangeAnalyzer",
    "PreCommitHookManager",
    "TestExecutionResult",
    "NotificationManager",
    "NotificationChannel",
    "TestFailureNotification",
    "TestHistoryTracker",
    "create_email_channel",
    "create_slack_channel",
    "create_teams_channel",
    "create_file_channel",
]
