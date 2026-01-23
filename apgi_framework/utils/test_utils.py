"""
Test-specific utilities for the APGI Framework test enhancement system.

This module provides test discovery, metadata extraction, test execution utilities,
and test result processing functions for comprehensive test management.
"""

import subprocess
import sys
import json
import re
import os
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import importlib.util

from .file_utils import FileUtils
from .ast_analyzer import ASTAnalyzer, TestMetrics


class FrameworkTestRunStatus(Enum):
    """Test execution status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    UNKNOWN = "unknown"


class FrameworkFailureCategory(Enum):
    """Test failure categories."""

    ASSERTION_ERROR = "assertion_error"
    FRAMEWORK_ERROR = "framework_error"
    IMPORT_ERROR = "import_error"
    TIMEOUT_ERROR = "timeout_error"
    SETUP_ERROR = "setup_error"
    TEARDOWN_ERROR = "teardown_error"


class FrameworkTestRunCategory(Enum):
    """Test categories."""

    UNIT = "unit"
    INTEGRATION = "integration"
    PROPERTY = "property"
    GUI = "gui"
    PERFORMANCE = "performance"
    SMOKE = "smoke"
    MODULE_SPECIFIC = "module_specific"


@dataclass
class FrameworkTestConfiguration:
    """Test execution configuration."""

    categories: List[FrameworkTestRunCategory] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    parallel: bool = False
    max_workers: int = 4
    timeout: Optional[float] = None
    retries: int = 0
    verbose: bool = False
    coverage: bool = False


@dataclass
class FrameworkTestDefinition:
    """Represents a single test case."""

    name: str
    file_path: Path
    module: str  # Added module attribute
    class_name: Optional[str]
    method_name: str
    category: FrameworkTestRunCategory
    line_number: int
    docstring: Optional[str]
    parameters: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    estimated_duration: float = 0.0
    tags: Set[str] = field(default_factory=set)


@dataclass
class FrameworkTestRunResult:
    """Represents test execution result."""

    test_case: FrameworkTestDefinition
    status: FrameworkTestRunStatus
    duration: float
    output: str
    error_message: Optional[str] = None
    traceback: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FrameworkTestCollection:
    """Represents a collection of test cases."""

    name: str
    test_cases: List[FrameworkTestDefinition]
    setup_methods: List[str] = field(default_factory=list)
    teardown_methods: List[str] = field(default_factory=list)
    fixtures: List[str] = field(default_factory=list)
    total_estimated_duration: float = 0.0


@dataclass
class FrameworkTestFailure:
    """Represents a test failure with detailed information."""

    test_name: str
    failure_category: FrameworkFailureCategory
    error_message: str
    stack_trace: str
    failure_context: Dict[str, Any]
    file_path: Path
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FrameworkTestResults:
    """Test execution results summary."""

    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    error_tests: int
    execution_time: float
    failures: List[FrameworkTestFailure] = field(default_factory=list)
    timestamp: Optional[datetime] = None
    results: List[FrameworkTestRunResult] = field(default_factory=list)

    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        return (
            (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        )


@dataclass
class FrameworkTestRunExecution:
    """Represents a test execution session."""

    execution_id: str
    test_suites: List[FrameworkTestCollection]
    results: List[FrameworkTestRunResult] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    configuration: Dict[str, Any] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)


class FrameworkTestUtilities:
    """
    Comprehensive test utilities for discovery, execution, and result processing.

    Provides functionality for test discovery, metadata extraction, test execution
    coordination, and result analysis for the test enhancement system.
    """

    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize TestUtilities.

        Args:
            base_path: Base directory for test operations
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
        self.logger = logging.getLogger(__name__)

        # Initialize AST analyzer
        self.ast_analyzer = ASTAnalyzer()

        # Initialize file utils
        self.file_utils = FileUtils()

        # Test file patterns
        self.test_file_patterns = ["test_*.py", "*_test.py", "tests.py"]

        # Test method patterns
        self.test_method_patterns = ["test_*", "*_test"]

    def discover_tests(
        self,
        root_dir: Union[str, Path],
        patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> List[FrameworkTestCollection]:
        """
        Discover all test files and extract test cases.

        Args:
            root_dir: Root directory to search for tests
            patterns: File patterns to include (optional)
            exclude_patterns: File patterns to exclude (optional)

        Returns:
            List of test suites
        """
        if patterns is None:
            patterns = self.test_file_patterns

        if exclude_patterns is None:
            exclude_patterns = ["__pycache__", "*.pyc", ".git"]

        test_files = []

        # Find test files
        for pattern in patterns:
            found_files = self.file_utils.find_files(pattern, root_dir, recursive=True)
            test_files.extend(found_files)

        # Remove duplicates and filter exclusions
        test_files = list(set(test_files))

        if exclude_patterns:
            filtered_files = []
            for file_path in test_files:
                should_exclude = False
                for exclude_pattern in exclude_patterns:
                    if exclude_pattern in str(file_path):
                        should_exclude = True
                        break
                if not should_exclude:
                    filtered_files.append(file_path)
            test_files = filtered_files

        # Extract test cases from files
        test_suites = []
        for test_file in test_files:
            try:
                suite = self._extract_test_suite(test_file)
                if suite.test_cases:  # Only add suites with test cases
                    test_suites.append(suite)
            except Exception as e:
                self.logger.warning(f"Failed to extract tests from {test_file}: {e}")

        self.logger.info(
            f"Discovered {len(test_suites)} test suites with {sum(len(s.test_cases) for s in test_suites)} test cases"
        )
        return test_suites

    def _extract_test_suite(self, file_path: Path) -> FrameworkTestCollection:
        """Extract test suite from a single test file."""
        elements = self.ast_analyzer.extract_code_elements(file_path)
        test_metrics = self.ast_analyzer.analyze_test_code(file_path)

        test_cases = []
        setup_methods = []
        teardown_methods = []
        fixtures = []

        # Process code elements
        for element in elements:
            if element.is_test and element.node_type.value in ["function", "method"]:
                # Determine category
                category = self._determine_test_category(
                    file_path, element.name, element.decorators
                )

                # Create test case
                test_case = FrameworkTestDefinition(
                    name=(
                        f"{element.parent_class}.{element.name}"
                        if element.parent_class
                        else element.name
                    ),
                    file_path=file_path,
                    module=file_path.stem,  # Use file name as module
                    class_name=element.parent_class,
                    method_name=element.name,
                    category=category,
                    line_number=element.line_start,
                    docstring=element.docstring,
                    parameters=element.parameters,
                    decorators=element.decorators,
                    dependencies=self._extract_test_dependencies(element),
                    estimated_duration=self._estimate_test_duration(element),
                    tags=self._extract_test_tags(element),
                )
                test_cases.append(test_case)

        # Extract setup/teardown methods
        setup_methods = test_metrics.setup_methods
        teardown_methods = test_metrics.teardown_methods
        fixtures = test_metrics.fixture_usage

        # Calculate total estimated duration
        total_duration = sum(tc.estimated_duration for tc in test_cases)

        suite_name = file_path.stem
        return FrameworkTestCollection(
            name=suite_name,
            test_cases=test_cases,
            setup_methods=setup_methods,
            teardown_methods=teardown_methods,
            fixtures=fixtures,
            total_estimated_duration=total_duration,
        )

    def _determine_test_category(
        self, file_path: Path, test_name: str, decorators: List[str]
    ) -> FrameworkTestRunCategory:
        """Determine test category based on file path, name, and decorators."""
        file_name = file_path.name.lower()
        test_name_lower = test_name.lower()

        # Check decorators first
        for decorator in decorators:
            if "property" in decorator.lower() or "given" in decorator.lower():
                return FrameworkTestRunCategory.PROPERTY
            if "gui" in decorator.lower() or "ui" in decorator.lower():
                return FrameworkTestRunCategory.GUI
            if "performance" in decorator.lower() or "benchmark" in decorator.lower():
                return FrameworkTestRunCategory.PERFORMANCE

        # Check file path
        if "integration" in str(file_path).lower():
            return FrameworkTestRunCategory.INTEGRATION
        if "property" in file_name or "pbt" in file_name:
            return FrameworkTestRunCategory.PROPERTY
        if "gui" in file_name or "ui" in file_name:
            return FrameworkTestRunCategory.GUI
        if "performance" in file_name or "benchmark" in file_name:
            return FrameworkTestRunCategory.PERFORMANCE
        if "smoke" in file_name:
            return FrameworkTestRunCategory.SMOKE

        # Check test name
        if "integration" in test_name_lower:
            return FrameworkTestRunCategory.INTEGRATION
        if "property" in test_name_lower:
            return FrameworkTestRunCategory.PROPERTY
        if "gui" in test_name_lower or "ui" in test_name_lower:
            return FrameworkTestRunCategory.GUI
        if "performance" in test_name_lower or "benchmark" in test_name_lower:
            return FrameworkTestRunCategory.PERFORMANCE
        if "smoke" in test_name_lower:
            return FrameworkTestRunCategory.SMOKE

        # Default to unit test
        return FrameworkTestRunCategory.UNIT

    def _extract_test_dependencies(self, element) -> Set[str]:
        """Extract test dependencies from code element."""
        dependencies = set()

        # Add dependencies based on decorators
        for decorator in element.decorators:
            if "mock" in decorator.lower():
                dependencies.add("mock")
            if "fixture" in decorator.lower():
                dependencies.add("pytest")
            if "hypothesis" in decorator.lower() or "given" in decorator.lower():
                dependencies.add("hypothesis")

        return dependencies

    def _estimate_test_duration(self, element) -> float:
        """Estimate test execution duration based on complexity."""
        base_duration = 0.1  # Base 100ms

        # Adjust based on complexity
        complexity_factor = min(element.complexity / 10.0, 2.0)

        # Adjust based on test type
        type_factors = {
            "integration": 2.0,
            "property": 3.0,
            "gui": 5.0,
            "performance": 10.0,
        }

        type_factor = 1.0
        for test_type, factor in type_factors.items():
            if test_type in element.name.lower():
                type_factor = factor
                break

        return base_duration * complexity_factor * type_factor

    def _extract_test_tags(self, element) -> Set[str]:
        """Extract test tags from decorators and docstring."""
        tags = set()

        # Extract from decorators
        for decorator in element.decorators:
            if "mark" in decorator.lower():
                # Extract pytest marks
                if "." in decorator:
                    mark_name = decorator.split(".")[-1]
                    tags.add(mark_name)

        # Extract from docstring
        if element.docstring:
            # Look for tags in format @tag or #tag
            tag_pattern = r"[@#](\w+)"
            found_tags = re.findall(tag_pattern, element.docstring)
            tags.update(found_tags)

        return tags

    def filter_tests(
        self,
        test_suites: List[FrameworkTestCollection],
        categories: Optional[List[FrameworkTestRunCategory]] = None,
        tags: Optional[List[str]] = None,
        name_pattern: Optional[str] = None,
        max_duration: Optional[float] = None,
    ) -> List[FrameworkTestCollection]:
        """
        Filter test suites based on criteria.

        Args:
            test_suites: List of test suites to filter
            categories: Test categories to include
            tags: Test tags to include
            name_pattern: Name pattern to match
            max_duration: Maximum test duration

        Returns:
            Filtered test suites
        """
        filtered_suites = []

        for suite in test_suites:
            filtered_cases = []

            for test_case in suite.test_cases:
                # Check category filter
                if categories and test_case.category not in categories:
                    continue

                # Check tag filter
                if tags and not any(tag in test_case.tags for tag in tags):
                    continue

                # Check name pattern
                if name_pattern and name_pattern not in test_case.name:
                    continue

                # Check duration filter
                if max_duration and test_case.estimated_duration > max_duration:
                    continue

                filtered_cases.append(test_case)

            # Create filtered suite if it has test cases
            if filtered_cases:
                filtered_suite = FrameworkTestCollection(
                    name=suite.name,
                    test_cases=filtered_cases,
                    setup_methods=suite.setup_methods,
                    teardown_methods=suite.teardown_methods,
                    fixtures=suite.fixtures,
                    total_estimated_duration=sum(
                        tc.estimated_duration for tc in filtered_cases
                    ),
                )
                filtered_suites.append(filtered_suite)

        return filtered_suites

    def execute_tests(
        self,
        test_suites: List[FrameworkTestCollection],
        config: Optional[Dict[str, Any]] = None,
    ) -> FrameworkTestRunExecution:
        """
        Execute test suites using pytest.

        Args:
            test_suites: Test suites to execute
            config: Execution configuration

        Returns:
            Test execution results
        """
        if config is None:
            config = {}

        execution_id = f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create test execution
        execution = FrameworkTestRunExecution(
            execution_id=execution_id,
            test_suites=test_suites,
            start_time=datetime.now(),
            configuration=config,
            environment=dict(os.environ) if "os" in sys.modules else {},
        )

        # Collect all test files
        test_files = set()
        for suite in test_suites:
            for test_case in suite.test_cases:
                test_files.add(str(test_case.file_path))

        # Build pytest command
        cmd = ["python", "-m", "pytest", "-v"]

        # Add configuration options
        if config.get("verbose", False):
            cmd.append("-vv")

        if config.get("coverage", False):
            cmd.extend(
                ["--cov=apgi_framework", "--cov=research", "--cov-report=term-missing"]
            )

        # Add test files
        cmd.extend(sorted(test_files))

        try:
            # Run pytest
            result = subprocess.run(
                cmd,
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=config.get("timeout", 1800),
            )

            # Parse results
            execution.end_time = datetime.now()
            execution.results = self._parse_pytest_output(result.stdout, result.stderr)

            return execution

        except subprocess.TimeoutExpired:
            execution.end_time = datetime.now()
            execution.configuration["timeout"] = True
            return execution
        except Exception as e:
            execution.end_time = datetime.now()
            execution.configuration["error"] = str(e)
            return execution

    def _parse_pytest_output(
        self, stdout: str, stderr: str
    ) -> List[FrameworkTestRunResult]:
        """Parse pytest output to extract test results."""
        results = []

        # Simple parsing - in a real implementation, this would be more sophisticated
        lines = stdout.split("\n")
        for line in lines:
            if "::" in line and (
                "PASSED" in line
                or "FAILED" in line
                or "SKIPPED" in line
                or "ERROR" in line
            ):
                # Extract test name and status
                parts = line.split()
                if len(parts) >= 2:
                    test_name = parts[0]
                    status_str = parts[1]

                    # Map status
                    status_map = {
                        "PASSED": FrameworkTestRunStatus.PASSED,
                        "FAILED": FrameworkTestRunStatus.FAILED,
                        "SKIPPED": FrameworkTestRunStatus.SKIPPED,
                        "ERROR": FrameworkTestRunStatus.ERROR,
                    }

                    status = status_map.get(status_str, FrameworkTestRunStatus.UNKNOWN)

                    # Create a basic test result
                    # In a real implementation, we'd match this to the actual test definition
                    result = FrameworkTestRunResult(
                        test_case=None,  # Would be filled in with actual test case
                        status=status,
                        duration=0.1,
                        output=line,
                        timestamp=datetime.now(),
                    )
                    results.append(result)

        return results


# Backward compatibility aliases
TestUtilities = FrameworkTestUtilities
TestDefinition = FrameworkTestDefinition
TestConfiguration = FrameworkTestConfiguration
TestCollection = FrameworkTestCollection
TestRunResult = FrameworkTestRunResult
TestResults = FrameworkTestResults
TestRunExecution = FrameworkTestRunExecution
TestFailure = FrameworkTestFailure
TestRunStatus = FrameworkTestRunStatus
TestRunCategory = FrameworkTestRunCategory
FailureCategory = FrameworkFailureCategory
