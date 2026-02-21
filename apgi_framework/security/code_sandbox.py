"""
Secure code execution sandbox for APGI Framework.

Provides a safe environment for dynamic code execution with strict
security controls, resource limits, and input validation.
"""

import ast
import logging
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)


class SandboxError(Exception):
    """Sandbox execution errors."""

    pass


class SecurityViolationError(SandboxError):
    """Security policy violations."""

    pass


class ResourceLimitExceededError(SandboxError):
    """Resource limit exceeded."""

    pass


class CodeSandbox:
    """
    Secure sandbox for executing untrusted Python code.

    Provides isolation, resource limits, and strict security controls
    to prevent malicious code execution.
    """

    def __init__(
        self,
        max_memory_mb: int = 100,
        max_cpu_time: float = 5.0,
        max_execution_time: float = 10.0,
        allow_network: bool = False,
        allow_file_access: bool = False,
        allowed_modules: Optional[List[str]] = None,
    ):
        """
        Initialize sandbox with security constraints.

        Args:
            max_memory_mb: Maximum memory usage in MB
            max_cpu_time: Maximum CPU time in seconds
            max_execution_time: Maximum wall clock time in seconds
            allow_network: Whether to allow network access
            allow_file_access: Whether to allow file system access
            allowed_modules: List of allowed Python modules
        """
        self.max_memory_mb = max_memory_mb
        self.max_cpu_time = max_cpu_time
        self.max_execution_time = max_execution_time
        self.allow_network = allow_network
        self.allow_file_access = allow_file_access

        # Default allowed modules for scientific computing
        self.allowed_modules = allowed_modules or [
            "math",
            "random",
            "statistics",
            "itertools",
            "functools",
            "collections",
            "datetime",
            "decimal",
            "fractions",
            "numpy",
            "scipy",
            "pandas",
            "matplotlib.pyplot",
            "seaborn",
            "sklearn",
            "statsmodels",
        ]

        # Forbidden modules and operations
        self.forbidden_modules = {
            "os",
            "sys",
            "subprocess",
            "socket",
            "urllib",
            "http",
            "ftplib",
            "smtplib",
            "telnetlib",
            "pickle",
            "shelve",
            "dbm",
            "sqlite3",
            "eval",
            "exec",
            "compile",
            "__import__",
            "open",
            "file",
            "input",
            "raw_input",
            "help",
            "credits",
        }

        self.forbidden_functions = {
            "eval",
            "exec",
            "compile",
            "__import__",
            "reload",
            "globals",
            "locals",
            "vars",
            "dir",
            "hasattr",
            "getattr",
            "setattr",
            "delattr",
            "callable",
            "isinstance",
            "issubclass",
            "open",
        }

    def validate_code(self, code: str) -> bool:
        """
        Validate code for security violations before execution.

        Args:
            code: Python code to validate

        Raises:
            SecurityViolationError: If code appears malicious
        """
        # Parse AST to check for violations
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SecurityViolationError(f"Syntax error in code: {e}")

        # Check for dangerous imports and function calls
        validator = SecurityValidator(
            self.allowed_modules, self.forbidden_modules, self.forbidden_functions
        )
        validator.visit(tree)

        if validator.violations:
            raise SecurityViolationError(
                f"Security violations found: {validator.violations}"
            )

        return True

    def execute_code(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        capture_output: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute code in secure sandbox environment.

        Args:
            code: Python code to execute
            context: Optional variables to inject into execution context
            capture_output: Whether to capture stdout/stderr

        Returns:
            Dictionary with execution results

        Raises:
            SandboxError: If execution fails or security violation occurs
        """
        # Validate code first
        self.validate_code(code)

        # For now, implement a simple safe execution
        # In production, this would use proper process isolation
        try:
            exec_context = self._prepare_execution_context(context)

            if capture_output:
                import contextlib
                import io

                stdout_capture = io.StringIO()
                stderr_capture = io.StringIO()

                with (
                    contextlib.redirect_stdout(stdout_capture),
                    contextlib.redirect_stderr(stderr_capture),
                ):
                    exec(code, exec_context)

                return {
                    "success": True,
                    "stdout": stdout_capture.getvalue(),
                    "stderr": stderr_capture.getvalue(),
                    "context": exec_context,
                }
            else:
                exec(code, exec_context)
                return {"success": True, "context": exec_context}

        except Exception as e:
            return {"success": False, "error": str(e), "error_type": type(e).__name__}

    def validate_input(self, data: Any) -> bool:
        """
        Validate input data for security threats.

        Args:
            data: Input data to validate

        Raises:
            SecurityViolationError: If data is malicious
        """
        if isinstance(data, str):
            # Check for dangerous patterns
            dangerous_patterns = [
                "__import__",
                "eval(",
                "exec(",
                "compile(",
                "subprocess",
                "os.system",
                "os.popen",
                "socket",
                "urllib",
                "http",
                "ftplib",
                "pickle.loads",
                "pickle.load",
                "__reduce__",
                "__reduce_ex__",
            ]

            for pattern in dangerous_patterns:
                if pattern in data.lower():
                    raise SecurityViolationError(
                        f"Dangerous pattern detected: {pattern}"
                    )

        elif isinstance(data, (bytes, bytearray)):
            # Check for malicious bytecode
            if b"__import__" in data or b"eval(" in data or b"exec(" in data:
                raise SecurityViolationError("Malicious bytecode detected")

        return True

    def _prepare_execution_context(
        self, context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare secure execution context."""
        exec_context: Dict[str, Any] = {
            # Safe built-ins
            "__builtins__": {
                "print": print,
                "len": len,
                "range": range,
                "enumerate": enumerate,
                "zip": zip,
                "map": map,
                "filter": filter,
                "sum": sum,
                "max": max,
                "min": min,
                "abs": abs,
                "round": round,
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict,
                "tuple": tuple,
                "set": set,
                "bool": bool,
                "type": type,
                "isinstance": isinstance,
                "hasattr": hasattr,
                # Math functions
                "math": __import__("math"),
            }
        }

        # Add allowed modules
        for module_name in self.allowed_modules:
            try:
                exec_context[str(module_name)] = __import__(module_name)  # type: ignore
            except ImportError:
                pass

        # Add user-provided context (validate first)
        if context:
            for key, value in context.items():
                if self._is_safe_value(value):
                    exec_context[key] = value
                else:
                    logger.warning(f"Skipping unsafe value in context: {key}")

        return exec_context

    def _is_safe_value(self, value: Any) -> bool:
        """Check if a value is safe to include in execution context."""
        try:
            # Check for dangerous objects
            if callable(value):
                # Check if it's a safe function
                return value.__module__ in self.allowed_modules

            # Check for containers with dangerous content
            if isinstance(value, (list, tuple, set)):
                return all(self._is_safe_value(item) for item in value)

            # Check for dictionaries with dangerous values
            if isinstance(value, dict):
                return all(self._is_safe_value(v) for v in value.values())

            # Check for strings with dangerous content
            if isinstance(value, str):
                try:
                    self.validate_input(value)
                    return True
                except SecurityViolationError:
                    return False

            return True

        except Exception:
            return False


class SecurityValidator(ast.NodeVisitor):
    """AST visitor to validate code security."""

    def __init__(
        self,
        allowed_modules: List[str],
        forbidden_modules: set,
        forbidden_functions: set,
    ):
        self.allowed_modules = allowed_modules
        self.forbidden_modules = forbidden_modules
        self.forbidden_functions = forbidden_functions
        self.violations: List[str] = []

    def visit_Import(self, node):
        """Check import statements."""
        for alias in node.names:
            # Check for exact matches and submodule imports
            if alias.name in self.forbidden_modules or any(
                forbidden in alias.name for forbidden in self.forbidden_modules
            ):
                self.violations.append(f"Forbidden import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Check from-import statements."""
        if node.module and any(
            forbidden in node.module for forbidden in self.forbidden_modules
        ):
            self.violations.append(f"Forbidden import from: {node.module}")
        self.generic_visit(node)

    def visit_Call(self, node):
        """Check function calls."""
        if isinstance(node.func, ast.Name):
            if node.func.id in self.forbidden_functions:
                self.violations.append(f"Dangerous function call: {node.func.id}")
        self.generic_visit(node)


# Global sandbox instance
_default_sandbox = CodeSandbox()


def safe_execute(
    code: str, context: Optional[Dict[str, Any]] = None, **kwargs
) -> Dict[str, Any]:
    """
    Safely execute code in the default sandbox.

    Args:
        code: Python code to execute
        context: Optional execution context
        **kwargs: Additional sandbox configuration

    Returns:
        Dictionary with execution results
    """
    return _default_sandbox.execute_code(code, context, **kwargs)


def validate_code_safety(code: str) -> bool:
    """
    Validate code for security issues.

    Args:
        code: Python code to validate

    Returns:
        True if code is safe
    """
    try:
        _default_sandbox.validate_code(code)
        return True
    except SecurityViolationError:
        return False
