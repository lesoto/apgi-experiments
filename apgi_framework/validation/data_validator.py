"""
Enhanced Data Validator for APGI Framework

Provides comprehensive data validation, integrity checks, and sanitization
for experimental data, parameters, and user inputs.
"""

import re
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import warnings

from ..logging.standardized_logging import get_logger

logger = get_logger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""

    field_name: str
    severity: ValidationSeverity
    message: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None
    suggestion: Optional[str] = None
