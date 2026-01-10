"""
DEPRECATED: This file contains security vulnerabilities and is kept for reference only.
Use apgi_framework.security.code_sandbox.py instead.

This file demonstrates BROKEN security practices that should NOT be used:
- Unsafe exec() usage without proper sandboxing
- Insufficient input validation
- Missing resource limits

For secure code execution, use the working code_sandbox.py module.
"""

import logging

logger = logging.getLogger(__name__)


class BrokenSandboxError(Exception):
    """This sandbox is deprecated and insecure."""

    pass


def deprecated_sandbox_warning():
    """Log warning about deprecated sandbox usage."""
    logger.warning(
        "Using deprecated and insecure code_sandbox_broken.py. "
        "Please migrate to apgi_framework.security.code_sandbox.py"
    )


# This entire module is deprecated and should not be used
deprecated_sandbox_warning()

# All class definitions and methods have been removed to prevent accidental use
# of insecure code execution. Use code_sandbox.py for secure alternatives.
