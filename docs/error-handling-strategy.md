# Error Handling Strategy for APGI Framework

## Overview

This document establishes error handling best practices for the APGI Framework, replacing broad `except Exception` patterns with specific, actionable error handling that improves debuggability and maintainability.

## Problem Statement

Current codebase has 1,145+ broad exception handlers across 164 files, which:

- Obscures failure modes
- Makes debugging difficult
- Catches exceptions that should propagate
- Reduces static analyzability
- Violates the principle of explicit error handling

## Core Principles

### 1. Catch Specific Exceptions

**Bad:**

```python
try:
    result = process_data(data)
except Exception as e:
    logger.error(f"Error: {e}")
    return None
```

**Good:**

```python
try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Invalid data format: {e}")
    raise DataValidationError(f"Data validation failed: {e}") from e
except KeyError as e:
    logger.error(f"Missing required field: {e}")
    raise DataValidationError(f"Missing field: {e}") from e
except (IOError, OSError) as e:
    logger.error(f"File system error: {e}")
    raise
```

### 2. Use Exception Chaining

**Bad:**

```python
try:
    result = complex_operation()
except Exception:
    raise CustomError("Operation failed")
```

**Good:**

```python
try:
    result = complex_operation()
except ValueError as e:
    raise CustomError(f"Operation failed: {e}") from e
```

### 3. Define Custom Exception Hierarchy

```python
# apgi_framework/exceptions.py

class APGIFrameworkError(Exception):
    """Base exception for all APGI framework errors."""
    pass

class DataValidationError(APGIFrameworkError):
    """Raised when data validation fails."""
    pass

class ConfigurationError(APGIFrameworkError):
    """Raised when configuration is invalid."""
    pass

class SimulationError(APGIFrameworkError):
    """Raised when simulation fails."""
    pass

class AnalysisError(APGIFrameworkError):
    """Raised when analysis fails."""
    pass
```

### 4. Log with Context

**Bad:**

```python
except Exception as e:
    logger.error(f"Error: {e}")
```

**Good:**

```python
except ValueError as e:
    logger.error(
        "Data validation failed",
        extra={
            "error_type": "ValueError",
            "error_message": str(e),
            "data_type": type(data).__name__,
            "context": {"field": field_name}
        }
    )
```

### 5. Never Swallow Exceptions Without Justification

**Bad:**

```python
try:
    risky_operation()
except:
    pass  # Silent failure
```

**Good:**

```python
try:
    risky_operation()
except SpecificExpectedError as e:
    # Document why we're catching this
    logger.warning(f"Expected non-critical error: {e}")
    # Provide fallback
    return fallback_value
```

## Exception Categories and Handling Patterns

### 1. Input Validation Errors

**Expected Exceptions:** `ValueError`, `TypeError`, `KeyError`

**Pattern:**

```python
def validate_input(data: Dict[str, Any]) -> None:
    """Validate input data structure."""
    if not isinstance(data, dict):
        raise TypeError(f"Expected dict, got {type(data).__name__}")
    
    required_fields = ["subject_id", "timestamp", "measurements"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise DataValidationError(f"Missing required fields: {missing}")
    
    if not isinstance(data["measurements"], (list, tuple)):
        raise TypeError("measurements must be a list or tuple")
```

### 2. File I/O Errors

**Expected Exceptions:** `FileNotFoundError`, `PermissionError`, `OSError`

**Pattern:**

```python
def load_data_file(file_path: Path) -> Dict:
    """Load data from file with proper error handling."""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        raise DataNotFoundError(f"Data file not found: {file_path}")
    except PermissionError:
        raise DataAccessError(f"Permission denied: {file_path}")
    except json.JSONDecodeError as e:
        raise DataValidationError(f"Invalid JSON in {file_path}: {e}")
```

### 3. Network Errors

**Expected Exceptions:** `ConnectionError`, `TimeoutError`, `HTTPError`

**Pattern:**

```python
def fetch_remote_data(url: str, timeout: int = 30) -> Dict:
    """Fetch data from remote endpoint."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        raise NetworkError(f"Request timeout after {timeout}s")
    except requests.ConnectionError:
        raise NetworkError(f"Failed to connect to {url}")
    except requests.HTTPError as e:
        raise NetworkError(f"HTTP error {e.response.status_code}")
```

### 4. Computational Errors

**Expected Exceptions:** `ZeroDivisionError`, `OverflowError`, `ValueError` (math domain errors)

**Pattern:**

```python
def calculate_ratio(numerator: float, denominator: float) -> float:
    """Calculate ratio with proper error handling."""
    try:
        return numerator / denominator
    except ZeroDivisionError:
        raise ComputationError("Cannot divide by zero")
    except OverflowError:
        raise ComputationError("Numerical overflow in ratio calculation")
    except TypeError as e:
        raise ComputationError(f"Invalid numeric types: {e}")
```

### 5. Configuration Errors

**Expected Exceptions:** `KeyError`, `ValueError`, `TypeError`

**Pattern:**

```python
def get_config_value(config: Dict, key: str, required: bool = True) -> Any:
    """Get configuration value with validation."""
    if key not in config:
        if required:
            raise ConfigurationError(f"Required configuration key missing: {key}")
        return None
    
    value = config[key]
    if value is None and required:
        raise ConfigurationError(f"Configuration key {key} cannot be None")
    
    return value
```

## Migration Strategy

### Phase 1: Critical Path Files (High Priority)

Target files that:

- Are in the main execution path
- Handle user data
- Perform security-sensitive operations

**Files to prioritize:**

1. `apgi_framework/main_controller.py`
2. `apgi_framework/config/manager.py`
3. `apgi_framework/data/storage_manager.py`
4. `apgi_framework/core/experiment.py`

### Phase 2: Core Module Files (Medium Priority)

Target files in:

- `apgi_framework/core/`
- `apgi_framework/data/`
- `apgi_framework/analysis/`

### Phase 3: Supporting Modules (Low Priority)

Target files in:

- `apgi_framework/gui/`
- `apgi_framework/utils/`
- `apgi_framework/simulators/

## Refactoring Guidelines

### When to Keep Broad Exception Handling

Only keep `except Exception` when:

1. Top-level error boundary where all exceptions must be caught
2. Cleanup operations in `finally` blocks
3. Plugin/module loading where third-party code may raise unexpected exceptions

**Example of acceptable use:**

```python
def main():
    """Top-level entry point."""
    try:
        controller = MainApplicationController()
        controller.initialize_system()
        controller.run_workflow()
    except APGIFrameworkError as e:
        logger.critical(f"Framework error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
```

### When to Replace Broad Exception Handling

Replace `except Exception` when:

1. Catching specific, expected exceptions
2. The exception type is known from the operation
3. Different error types require different handling
4. The exception should be re-raised with context

**Example of refactoring:**

```python
# Before
def process_file(file_path: str):
    try:
        data = load_file(file_path)
        result = analyze(data)
        return result
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return None

# After
def process_file(file_path: str):
    try:
        data = load_file(file_path)
        result = analyze(data)
        return result
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise DataNotFoundError(f"Cannot process missing file: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        raise DataAccessError(f"Cannot access file: {file_path}")
    except DataValidationError as e:
        logger.error(f"Invalid data in {file_path}: {e}")
        raise
    except AnalysisError as e:
        logger.error(f"Analysis failed for {file_path}: {e}")
        raise
```

## Code Review Checklist

For each exception handler, verify:

- [ ] Catches specific exception types, not bare `except` or `except Exception`
- [ ] Uses exception chaining with `from e` when re-raising
- [ ] Logs with sufficient context (error type, message, relevant data)
- [ ] Has clear justification for catching the exception
- [ ] Provides meaningful fallback or re-raises with context
- [ ] Documents why the exception is expected here
- [ ] Differentiates between expected and unexpected errors

## Static Analysis Integration

### Flake8 Plugin

Add to `.flake8`:

```ini
[flake8]
# Enable broad-exception check
select = E9, F63, F7, F82
ignore = 
# Add custom check for except exception
```

### Custom Linter Rule

Create `linting/check_exceptions.py`:

```python
import ast
from typing import List

class BroadExceptionChecker(ast.NodeVisitor):
    def __init__(self):
        self.violations: List[tuple] = []
    
    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.violations.append(
                (node.lineno, node.col_offset, "Bare except clause")
            )
        elif isinstance(node.type, ast.Name) and node.type.id == "Exception":
            # Check if this is a top-level handler (acceptable)
            if not self._is_top_level_handler(node):
                self.violations.append(
                    (node.lineno, node.col_offset, "Broad except Exception")
                )
        self.generic_visit(node)
    
    def _is_top_level_handler(self, node) -> bool:
        # Check if this is in a main() or top-level function
        return False  # Implementation depends on AST analysis
```

## Testing Guidelines

### Test Exception Paths

```python
def test_specific_exception_handling():
    """Test that specific exceptions are handled correctly."""
    with pytest.raises(DataValidationError) as exc_info:
        validate_input({"invalid": "data"})
    
    assert "Missing required fields" in str(exc_info.value)

def test_exception_chaining():
    """Test that exception chaining preserves context."""
    try:
        process_invalid_data()
    except DataValidationError as e:
        assert e.__cause__ is not None
        assert isinstance(e.__cause__, ValueError)
```

## Monitoring and Metrics

### Track Exception Types

```python
from collections import defaultdict

class ExceptionTracker:
    def __init__(self):
        self.exception_counts = defaultdict(int)
    
    def record_exception(self, exception: Exception):
        exception_type = type(exception).__name__
        self.exception_counts[exception_type] += 1
        logger.info(
            f"Exception recorded: {exception_type}",
            extra={"exception_type": exception_type}
        )
```

## References

- Python Exception Handling: <https://docs.python.org/3/tutorial/errors.html>
- Exception Chaining: <https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement>
- Logging Best Practices: <https://docs.python.org/3/howto/logging.html>
