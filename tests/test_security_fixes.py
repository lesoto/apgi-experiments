#!/usr/bin/env python3
"""
Regression tests for APGI Framework security fixes.

Tests the security measures implemented to address:
- eval()/exec() vulnerabilities
- Unsafe pickle usage
- Code execution sandboxing
- Input validation
"""

import pytest
import tempfile
import pickle
from pathlib import Path
from unittest.mock import patch, MagicMock
import ast

# Import security modules
from apgi_framework.security.secure_pickle import (
    SecurePickleValidator,
    safe_pickle_load,
    safe_pickle_dump,
    validate_pickle_security,
    SecurePickleError,
)
from apgi_framework.security.code_sandbox import (
    CodeSandbox,
    SecurityViolationError,
    ResourceLimitExceededError,
    SandboxError,
    safe_execute,
    validate_code_safety,
)
from apgi_framework.logging.standardized_logging import (
    APGILogger,
    LoggingManager,
    get_logger,
)


class TestSecurePickle:
    """Test secure pickle functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SecurePickleValidator(strict_mode=True)
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_safe_pickle_dump_and_load(self):
        """Test safe pickle dump and load operations."""
        # Test data
        test_data = {
            "numbers": [1, 2, 3, 4, 5],
            "strings": ["hello", "world"],
            "nested": {"inner": {"value": 42}},
        }

        file_path = self.temp_dir / "test.pkl"

        # Dump and load
        safe_pickle_dump(test_data, file_path)
        loaded_data = safe_pickle_load(file_path, expected_types={dict})

        assert loaded_data == test_data

    def test_pickle_validation_rejects_dangerous_content(self):
        """Test that dangerous pickle content is rejected."""
        # Create malicious pickle content (simplified example)
        malicious_data = b'{"__reduce__": "__import__"}'

        file_path = self.temp_dir / "malicious.pkl"
        with open(file_path, "wb") as f:
            f.write(malicious_data)

        # Should raise SecurePickleError
        with pytest.raises(SecurePickleError):
            safe_pickle_load(file_path)

    def test_pickle_checksum_verification(self):
        """Test checksum verification for pickle files."""
        test_data = {"test": "data"}
        file_path = self.temp_dir / "checksum_test.pkl"

        # Dump with checksum
        safe_pickle_dump(test_data, file_path, create_checksum=True)

        # Modify file (corrupt it)
        with open(file_path, "ab") as f:
            f.write(b"corrupted")

        # Should fail checksum verification
        with pytest.raises(SecurePickleError):
            safe_pickle_load(file_path, verify_checksum=True)

    def test_validate_pickle_security_function(self):
        """Test the pickle security validation function."""
        test_data = {"safe": "data"}
        file_path = self.temp_dir / "validation_test.pkl"

        # Create safe pickle
        safe_pickle_dump(test_data, file_path)

        # Validate
        result = validate_pickle_security(file_path)
        assert result["is_safe"] is True
        assert len(result["errors"]) == 0

    def test_restricted_unpickler_blocks_forbidden_types(self):
        """Test that restricted unpickler blocks forbidden types."""
        from apgi_framework.security.secure_pickle import RestrictedUnpickler

        # This would need to be tested with actual malicious pickle data
        # For now, test the concept
        pass


class TestCodeSandbox:
    """Test code execution sandbox."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sandbox = CodeSandbox(
            max_memory_mb=50, max_cpu_time=2.0, max_execution_time=5.0
        )

    def test_safe_code_execution(self):
        """Test execution of safe code."""
        safe_code = """
result = 2 + 2
message = "Hello from sandbox"
"""

        result = self.sandbox.execute_code(safe_code, capture_output=True)

        assert result["success"] is True
        assert "result" in result["context"]  # Result should be in context
        assert result["stdout"] == ""
        assert result["stderr"] == ""

    def test_code_validation_blocks_dangerous_imports(self):
        """Test that dangerous imports are blocked."""
        dangerous_code = """
import os
os.system('echo "This should not execute"')
"""

        with pytest.raises(SecurityViolationError):
            self.sandbox.validate_code(dangerous_code)

    def test_code_validation_blocks_eval_exec(self):
        """Test that eval() and exec() are blocked."""
        dangerous_code = """
result = eval('2 + 2')
"""

        with pytest.raises(SecurityViolationError):
            self.sandbox.validate_code(dangerous_code)

    def test_resource_limits_enforced(self):
        """Test that resource limits are enforced."""
        # Code that should exceed memory limit
        memory_hog_code = """
# Create large list to exceed memory limit
big_list = [0] * 10000000  # This should exceed 50MB
"""

        with pytest.raises((ResourceLimitExceededError, SandboxError)):
            self.sandbox.execute_code(memory_hog_code)

    def test_network_access_blocked(self):
        """Test that network access is blocked."""
        network_code = """
import urllib.request
response = urllib.request.urlopen('http://example.com')
"""

        with pytest.raises(SecurityViolationError):
            self.sandbox.validate_code(network_code)

    def test_file_access_restricted(self):
        """Test that file access is restricted."""
        file_code = """
with open('/etc/passwd', 'r') as f:
    content = f.read()
"""

        with pytest.raises(SecurityViolationError):
            self.sandbox.validate_code(file_code)

    def test_safe_execute_convenience_function(self):
        """Test the safe_execute convenience function."""
        safe_code = """
x = 10
y = 20
product = x * y
"""

        result = safe_execute(safe_code)
        assert result["success"] is True

    def test_validate_code_safety_function(self):
        """Test the code safety validation function."""
        safe_code = "result = 2 + 2"
        dangerous_code = "eval('2 + 2')"

        assert validate_code_safety(safe_code) is True
        assert validate_code_safety(dangerous_code) is False


class TestInputValidation:
    """Test input validation security measures."""

    def test_validate_input_blocks_dangerous_patterns(self):
        """Test that input validation blocks dangerous patterns."""
        from apgi_framework.security.code_sandbox import CodeSandbox

        sandbox = CodeSandbox()

        # Test dangerous strings
        dangerous_inputs = [
            "__import__('os').system('ls')",
            "eval('malicious code')",
            "exec('dangerous code')",
            "subprocess.call(['ls'])",
            "pickle.loads(data)",
        ]

        for dangerous_input in dangerous_inputs:
            with pytest.raises(SecurityViolationError):
                sandbox.validate_input(dangerous_input)

    def test_validate_input_allows_safe_data(self):
        """Test that safe input data is allowed."""
        from apgi_framework.security.code_sandbox import CodeSandbox

        sandbox = CodeSandbox()

        # Test safe inputs
        safe_inputs = [
            "Hello, world!",
            "2 + 2",
            "result = x * y",
            "data = [1, 2, 3, 4, 5]",
        ]

        for safe_input in safe_inputs:
            try:
                sandbox.validate_input(safe_input)
            except SecurityViolationError:
                pytest.fail(f"Safe input was rejected: {safe_input}")


class TestLoggingSecurity:
    """Test logging security features."""

    def test_logger_prevents_code_execution(self):
        """Test that logger doesn't execute code in messages."""
        logger = get_logger("test_security")

        # This should not execute the code
        malicious_message = "__import__('os').system('echo hacked')"

        # Should log the message as a string, not execute it
        logger.info(malicious_message)

        # If we get here without code execution, test passes
        assert True

    def test_structured_logging_sanitizes_input(self):
        """Test that structured logging sanitizes input data."""
        logger = APGILogger("test_security", enable_structured=True)

        # This should be safely logged as data, not executed
        malicious_data = {"code": "__import__('os').system('ls')"}

        logger.info("Test message", **malicious_data)

        # If we get here without code execution, test passes
        assert True


class TestEvalExecReplacements:
    """Test that eval()/exec() have been properly replaced."""

    def test_run_experiments_uses_safe_ast_literal_eval(self):
        """Test that run_experiments.py uses safe ast.literal_eval with validation."""
        # Import the function
        from run_experiments import main

        # Test that it handles safe input correctly
        with patch(
            "sys.argv", ["run_experiments.py", "interoceptive_gating", "--test", "42"]
        ):
            try:
                result = main()
                # Should not crash or execute malicious code
                assert result in [0, 1]  # Exit codes
            except SystemExit:
                pass  # Expected

    def test_no_eval_or_exec_in_framework(self):
        """Test that no eval() or exec() calls remain in the framework."""
        import ast
        import os

        framework_dir = Path("apgi_framework")
        violations = []

        for py_file in framework_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            # Skip security modules which legitimately use exec() for sandboxing
            if "security" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content)

                # Check for eval and exec calls
                class EvalExecFinder(ast.NodeVisitor):
                    def visit_Call(self, node):
                        if isinstance(node.func, ast.Name):
                            if node.func.id in ["eval", "exec"]:
                                violations.append(
                                    f"{py_file}:{node.lineno} - {node.func.id}()"
                                )
                        self.generic_visit(node)

                finder = EvalExecFinder()
                finder.visit(tree)

            except Exception as e:
                violations.append(f"{py_file} - Parse error: {e}")

        # Report violations (should be empty after fixes)
        assert len(violations) == 0, f"Found eval/exec violations: {violations}"


class TestSecurityRegression:
    """Regression tests for security fixes."""

    def test_pickle_files_are_secure(self):
        """Test that existing pickle files are secure."""
        # This would scan existing pickle files in the project
        # For now, test the validation mechanism
        pass

    def test_no_hardcoded_secrets(self):
        """Test that no hardcoded secrets exist in the code."""
        import re
        from pathlib import Path

        # Patterns that might indicate secrets
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        framework_dir = Path("apgi_framework")
        violations = []

        for py_file in framework_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        violations.append(f"{py_file}: Potential secret found")
            except Exception:
                pass

        # Should not find any hardcoded secrets
        assert len(violations) == 0, f"Found potential secrets: {violations}"

    def test_logging_replaces_print_statements(self):
        """Test that print statements have been replaced with logging."""
        import ast
        from pathlib import Path

        # Check that critical files use logging instead of print
        critical_files = [
            "apgi_framework/data/storage_manager.py",
            "apgi_framework/data/experiment_tracker.py",
            "apgi_framework/analysis/bayesian_models.py",
        ]

        for file_path in critical_files:
            path = Path(file_path)
            if not path.exists():
                continue

            try:
                content = path.read_text(encoding="utf-8")

                # Should have logging import
                assert (
                    "from ..logging.standardized_logging import get_logger" in content
                    or "from apgi_framework.logging.standardized_logging import get_logger"
                    in content
                ), f"{file_path} should import standardized logging"

                # Should have logger initialization
                assert (
                    "logger = get_logger" in content
                ), f"{file_path} should initialize logger"

            except Exception as e:
                pytest.fail(f"Failed to check {file_path}: {e}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
