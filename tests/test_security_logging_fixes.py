#!/usr/bin/env python3
"""
Comprehensive tests for security and logging fixes.

Tests the implemented security measures and logging consistency across the APGI Framework.
"""

import pytest
import tempfile
import logging
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import ast

# Import security modules
from apgi_framework.security.security_validator import (
    SecurityValidator, SecurityError, validate_input, safe_eval_literal,
    validate_file_path, sanitize_for_logging
)
from apgi_framework.security.secure_pickle import (
    SecurePickleValidator, safe_pickle_load, safe_pickle_dump,
    validate_pickle_security, SecurePickleError
)
from apgi_framework.security.code_sandbox import (
    CodeSandbox, SecurityViolationError, safe_execute,
    validate_code_safety
)
from apgi_framework.logging.standardized_logging import (
    APGILogger, LoggingManager, get_logger, setup_logging
)


class TestSecurityValidator:
    """Test the centralized security validator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SecurityValidator(strict_mode=True)
        self.validator_lenient = SecurityValidator(strict_mode=False)
    
    def test_string_validation_blocks_dangerous_patterns(self):
        """Test that dangerous patterns are blocked."""
        dangerous_inputs = [
            "__import__('os').system('ls')",
            "eval('malicious code')",
            "exec('dangerous code')",
            "subprocess.call(['ls'])",
            "pickle.loads(data)",
            "open('/etc/passwd')",
            "socket.socket()"
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(SecurityError):
                self.validator.validate_string_input(dangerous_input)
    
    def test_string_validation_allows_safe_inputs(self):
        """Test that safe inputs are allowed."""
        safe_inputs = [
            "Hello world",
            "42",
            "3.14159",
            "True",
            "['a', 'b', 'c']",
            "{'key': 'value'}"
        ]
        
        for safe_input in safe_inputs:
            assert self.validator.validate_string_input(safe_input) is True
    
    def test_data_structure_validation_recursive(self):
        """Test recursive validation of data structures."""
        # Safe nested structure
        safe_data = {
            'numbers': [1, 2, 3],
            'nested': {
                'strings': ['hello', 'world'],
                'bool': True
            }
        }
        assert self.validator.validate_data_structure(safe_data) is True
        
        # Dangerous nested structure
        dangerous_data = {
            'safe': [1, 2, 3],
            'dangerous': "eval('malicious')"
        }
        with pytest.raises(SecurityError):
            self.validator.validate_data_structure(dangerous_data)
    
    def test_file_path_validation_prevents_traversal(self):
        """Test that file path validation prevents directory traversal."""
        dangerous_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "..\\..\\windows\\system32"
        ]
        
        for dangerous_path in dangerous_paths:
            with pytest.raises(SecurityError):
                self.validator.validate_file_path(dangerous_path)
    
    def test_safe_literal_eval(self):
        """Test safe literal evaluation."""
        # Safe literals
        assert self.validator.safe_literal_eval("42") == 42
        assert self.validator.safe_literal_eval("[1, 2, 3]") == [1, 2, 3]
        assert self.validator.safe_literal_eval("{'key': 'value'}") == {'key': 'value'}
        
        # Dangerous expressions
        with pytest.raises(SecurityError):
            self.validator.safe_literal_eval("__import__('os')")
        
        with pytest.raises(SecurityError):
            self.validator.safe_literal_eval("eval('1+1')")
    
    def test_lenient_mode_warnings(self):
        """Test lenient mode logs warnings instead of raising errors."""
        with patch('apgi_framework.security.security_validator.logger') as mock_logger:
            # Should not raise error, but should log warning
            result = self.validator_lenient.validate_string_input("eval('test')")
            assert result is False
            mock_logger.warning.assert_called()
    
    def test_log_sanitization(self):
        """Test log data sanitization."""
        # Sensitive data should be redacted
        sensitive_data = "password=secret123 token=abc123"
        sanitized = self.validator.sanitize_for_logging(sensitive_data)
        assert "password=[REDACTED]" in sanitized
        assert "token=[REDACTED]" in sanitized
        assert "secret123" not in sanitized
        assert "abc123" not in sanitized


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
        test_data = {
            'numbers': [1, 2, 3, 4, 5],
            'strings': ['hello', 'world'],
            'nested': {'key': 'value'}
        }
        
        file_path = self.temp_dir / "test.pkl"
        
        # Dump and load
        safe_pickle_dump(test_data, file_path)
        loaded_data = safe_pickle_load(file_path)
        
        assert loaded_data == test_data
    
    def test_pickle_validation_blocks_dangerous_content(self):
        """Test that dangerous pickle content is blocked."""
        # Create malicious pickle data (simulated)
        malicious_data = b"__import__\n"
        
        with pytest.raises(SecurePickleError):
            self.validator.validate_pickle_data(malicious_data)
    
    def test_pickle_security_validation(self):
        """Test comprehensive pickle security validation."""
        # Create safe pickle file
        safe_data = [1, 2, 3]
        safe_file = self.temp_dir / "safe.pkl"
        safe_pickle_dump(safe_data, safe_file)
        
        result = validate_pickle_security(safe_file)
        assert result['is_safe'] is True
        assert len(result['errors']) == 0
    
    def test_checksum_verification(self):
        """Test checksum verification for pickle files."""
        test_data = {'test': 'data'}
        file_path = self.temp_dir / "checksum_test.pkl"
        
        # Dump with checksum
        safe_pickle_dump(test_data, file_path, create_checksum=True)
        
        # Verify checksum file exists
        checksum_file = file_path.with_suffix('.checksum')
        assert checksum_file.exists()
        
        # Load should verify checksum
        loaded_data = safe_pickle_load(file_path, verify_checksum=True)
        assert loaded_data == test_data


class TestCodeSandbox:
    """Test code execution sandbox."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.sandbox = CodeSandbox()
    
    def test_safe_code_execution(self):
        """Test execution of safe code."""
        safe_code = """
result = 2 + 2
message = "Hello, world!"
"""
        result = self.sandbox.execute_code(safe_code)
        
        assert result['success'] is True
        assert result['context']['result'] == 4
        assert result['context']['message'] == "Hello, world!"
    
    def test_dangerous_code_blocked(self):
        """Test that dangerous code is blocked."""
        dangerous_codes = [
            "eval('2 + 2')",
            "exec('print(\"hello\")')",
            "__import__('os')"
        ]
        
        for dangerous_code in dangerous_codes:
            with pytest.raises(SecurityViolationError):
                self.sandbox.validate_code(dangerous_code)
    
    def test_input_validation(self):
        """Test input validation for sandbox."""
        # Safe inputs
        safe_inputs = [
            "2 + 2",
            "['a', 'b', 'c']",
            "{'key': 'value'}"
        ]
        
        for safe_input in safe_inputs:
            assert self.sandbox.validate_input(safe_input) is True
        
        # Dangerous inputs
        dangerous_inputs = [
            "__import__('os')",
            "eval('malicious')",
            "exec('dangerous')"
        ]
        
        for dangerous_input in dangerous_inputs:
            with pytest.raises(SecurityViolationError):
                self.sandbox.validate_input(dangerous_input)


class TestLoggingConsistency:
    """Test logging consistency and functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        setup_logging(log_dir=self.temp_dir, log_level="DEBUG")
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_creation_and_usage(self):
        """Test logger creation and basic usage."""
        logger = get_logger("test_module")
        
        assert isinstance(logger, APGILogger)
        assert logger.name == "test_module"
        
        # Test different log levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
    
    def test_structured_logging(self):
        """Test structured logging functionality."""
        logger = get_logger("structured_test", enable_structured=True)
        
        # Test logging with extra data
        logger.info("Test message", 
                   experiment_id="test123",
                   user_id="user456",
                   event_type="test")
    
    def test_performance_logging(self):
        """Test performance metric logging."""
        logger = get_logger("performance_test")
        
        logger.performance_metric("response_time", 0.123, "seconds")
        logger.performance_metric("memory_usage", 1024, "MB")
    
    def test_security_event_logging(self):
        """Test security event logging."""
        logger = get_logger("security_test")
        
        logger.security_event("invalid_input", {
            'input_type': 'string',
            'length': 1000,
            'user_agent': 'test_agent'
        })
    
    def test_experiment_logging(self):
        """Test experiment-specific logging."""
        logger = get_logger("experiment_test")
        
        logger.experiment_start("test_experiment", {'param1': 'value1'})
        logger.experiment_end("test_experiment", "completed", 123.45)
    
    def test_log_execution_context_manager(self):
        """Test the log execution context manager."""
        logger = get_logger("context_test")
        
        with logger.log_execution("test_operation"):
            # Simulate some work
            result = 2 + 2
            assert result == 4


class TestIntegrationSecurity:
    """Integration tests for security measures."""
    
    def test_run_experiments_security(self):
        """Test that run_experiments.py uses secure evaluation."""
        # Import the function we fixed
        from run_experiments import _is_safe_data_structure
        
        # Test safe data structures
        safe_data = {'key': 'value', 'numbers': [1, 2, 3]}
        assert _is_safe_data_structure(safe_data) is True
        
        # Test dangerous data structures
        dangerous_data = {'safe': 'value', 'dangerous': "eval('test')"}
        assert _is_safe_data_structure(dangerous_data) is False
    
    def test_no_unsafe_pickle_in_framework(self):
        """Test that no unsafe pickle usage remains in framework."""
        import os
        
        framework_dir = Path("apgi_framework")
        if not framework_dir.exists():
            pytest.skip("Framework directory not found")
        
        # Find all Python files in framework
        python_files = list(framework_dir.rglob("*.py"))
        
        for py_file in python_files:
            content = py_file.read_text()
            
            # Check for unsafe pickle usage, but allow pattern lists in security modules
            if "pickle.load" in content or "pickle.dump" in content:
                # Skip security validator files which contain pattern lists
                if "security_validator.py" in str(py_file):
                    continue
                    
                # Should be using secure_pickle instead
                assert "secure_pickle" in content or "safe_pickle" in content, \
                    f"Unsafe pickle usage found in {py_file}"
    
    def test_logging_consistency_across_modules(self):
        """Test that modules use consistent logging."""
        framework_dir = Path("apgi_framework")
        if not framework_dir.exists():
            pytest.skip("Framework directory not found")
        
        # Check that files with print statements also have logging imports
        python_files = list(framework_dir.rglob("*.py"))
        
        for py_file in python_files:
            content = py_file.read_text()
            
            # Skip example files and test files which may legitimately use print
            if "example" in str(py_file).lower() or "test" in str(py_file).lower():
                continue
                
            if "print(" in content:
                # Should have logging import and usage
                assert "logging" in content or "get_logger" in content, \
                    f"File with print() statements missing logging: {py_file}"


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])
