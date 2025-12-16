"""
Secure pickle utilities for APGI Framework.

Provides safe alternatives to direct pickle usage with input validation,
type checking, and sandboxing to prevent code execution vulnerabilities.
"""

import pickle
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Set
import logging
from dataclasses import is_dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


class SecurePickleError(Exception):
    """Security-related pickle errors."""
    pass


class SecurePickleValidator:
    """
    Validates and secures pickle operations to prevent code execution attacks.
    
    Only allows specific whitelisted types and validates data integrity.
    """
    
    # Whitelisted safe types that can be unpickled
    ALLOWED_TYPES = {
        # Basic types
        str, int, float, bool, type(None),
        # Collections
        list, tuple, dict, set, frozenset,
        # Data structures
        bytes, bytearray,
        # Scientific computing (common in research)
        'numpy.ndarray', 'numpy.float64', 'numpy.float32', 'numpy.int64', 'numpy.int32',
        # Framework types (dataclasses)
        'ExperimentalDataset', 'ExperimentMetadata', 'ExperimentSession',
        'DataVersion', 'BackupInfo', 'QueryFilter', 'StorageStats',
        # Standard library types
        datetime, 'datetime.datetime',
        # Paths
        'pathlib.Path',
    }
    
    # Forbidden modules that could indicate malicious code
    FORBIDDEN_MODULES = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'http', 'ftplib',
        'smtplib', 'telnetlib', 'pickle', 'shelve', 'dbm', 'sqlite3',
        'eval', 'exec', 'compile', '__import__', 'open', 'file',
    }
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator.
        
        Args:
            strict_mode: If True, rejects any unknown types. If False, logs warnings.
        """
        self.strict_mode = strict_mode
        self.validation_cache = {}
        
    def validate_pickle_data(self, data: bytes, expected_types: Optional[Set[type]] = None) -> bool:
        """
        Validate pickle data before unpickling.
        
        Args:
            data: Raw pickle bytes to validate
            expected_types: Set of expected types for additional validation
            
        Returns:
            bool: True if data appears safe
            
        Raises:
            SecurePickleError: If data appears malicious
        """
        try:
            # Check file signature
            if not self._is_valid_pickle_format(data):
                raise SecurePickleError("Invalid pickle format detected")
            
            # Try to analyze pickle opcode stream for dangerous patterns
            if self._contains_dangerous_opcodes(data):
                raise SecurePickleError("Dangerous pickle opcodes detected")
                
            return True
            
        except Exception as e:
            logger.error(f"Pickle validation failed: {e}")
            if self.strict_mode:
                raise SecurePickleError(f"Pickle validation failed: {e}")
            return False
    
    def _is_valid_pickle_format(self, data: bytes) -> bool:
        """Check if data has valid pickle format."""
        if len(data) < 2:
            return False
            
        # Check for valid pickle protocol markers
        valid_protocols = {b'\x80', b'}', b')', b'.', b'0', b'1', b'2'}
        return data[:1] in valid_protocols
    
    def _contains_dangerous_opcodes(self, data: bytes) -> bool:
        """
        Scan pickle data for dangerous opcodes that could execute code.
        
        This is a simplified check - production use would need more comprehensive analysis.
        """
        dangerous_patterns = [
            b'__reduce__',
            b'__reduce_ex__',
            b'__getstate__',
            b'__setstate__',
            b'eval',
            b'exec',
            b'compile',
            b'open',
            b'file',
            b'os.',
            b'sys.',
            b'subprocess',
        ]
        
        for pattern in dangerous_patterns:
            if pattern in data:
                logger.warning(f"Dangerous pattern detected in pickle: {pattern}")
                return True
                
        return False
    
    def safe_load(self, file_path: Union[str, Path], 
                  expected_types: Optional[Set[type]] = None,
                  verify_checksum: bool = True) -> Any:
        """
        Safely load pickled data with validation.
        
        Args:
            file_path: Path to pickle file
            expected_types: Set of expected types for validation
            verify_checksum: Whether to verify file integrity
            
        Returns:
            Unpickled data
            
        Raises:
            SecurePickleError: If data is unsafe or corrupted
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise SecurePickleError(f"Pickle file not found: {file_path}")
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Validate pickle data
            self.validate_pickle_data(data, expected_types)
            
            # Verify checksum if requested and available
            if verify_checksum:
                checksum_file = file_path.with_suffix('.checksum')
                if checksum_file.exists():
                    with open(checksum_file, 'r') as f:
                        expected_checksum = f.read().strip()
                    
                    actual_checksum = hashlib.sha256(data).hexdigest()
                    if actual_checksum != expected_checksum:
                        raise SecurePickleError(f"Checksum mismatch for {file_path}")
            
            # Unpickle with restricted unpickler
            import io
            with io.BytesIO(data) as data_stream:
                unpickler = RestrictedUnpickler(data_stream, allowed_types=expected_types or self.ALLOWED_TYPES)
                result = unpickler.load()
            
            # Validate result type
            if expected_types:
                result_type = type(result)
                if result_type not in expected_types and not any(
                    isinstance(result, t) for t in expected_types
                ):
                    raise SecurePickleError(f"Unexpected type: {result_type}")
            
            logger.info(f"Safely loaded pickle from {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to safely load pickle {file_path}: {e}")
            raise SecurePickleError(f"Failed to safely load pickle: {e}")
    
    def safe_dump(self, obj: Any, file_path: Union[str, Path],
                  create_checksum: bool = True,
                  protocol: int = pickle.HIGHEST_PROTOCOL) -> None:
        """
        Safely dump object to pickle file.
        
        Args:
            obj: Object to pickle
            file_path: Output file path
            create_checksum: Whether to create checksum file
            protocol: Pickle protocol version
            
        Raises:
            SecurePickleError: If object contains unsafe data
        """
        file_path = Path(file_path)
        
        try:
            # Validate object type
            obj_type = type(obj)
            if obj_type not in self.ALLOWED_TYPES and not is_dataclass(obj):
                logger.warning(f"Pickling object of potentially unsafe type: {obj_type}")
                if self.strict_mode:
                    raise SecurePickleError(f"Unsafe type for pickling: {obj_type}")
            
            # Create parent directory
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Pickle the object
            with open(file_path, 'wb') as f:
                pickle.dump(obj, f, protocol=protocol)
            
            # Create checksum if requested
            if create_checksum:
                with open(file_path, 'rb') as f:
                    data = f.read()
                checksum = hashlib.sha256(data).hexdigest()
                checksum_file = file_path.with_suffix('.checksum')
                with open(checksum_file, 'w') as f:
                    f.write(checksum)
            
            logger.info(f"Safely dumped object to {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to safely dump pickle {file_path}: {e}")
            raise SecurePickleError(f"Failed to safely dump pickle: {e}")


class RestrictedUnpickler(pickle.Unpickler):
    """
    Restricted unpickler that only allows safe types.
    """
    
    def __init__(self, file, allowed_types: Set[type]):
        super().__init__(file)
        self.allowed_types = allowed_types
    
    def find_class(self, module, name):
        """
        Override find_class to only allow whitelisted types.
        """
        # Check for forbidden modules
        if any(forbidden in module for forbidden in SecurePickleValidator.FORBIDDEN_MODULES):
            raise SecurePickleError(f"Forbidden module in pickle: {module}")
        
        # Check if type is allowed
        full_name = f"{module}.{name}"
        if full_name in self.allowed_types or name in self.allowed_types:
            return super().find_class(module, name)
        
        raise SecurePickleError(f"Type not allowed: {full_name}")


# Global validator instance
_default_validator = SecurePickleValidator()


def safe_pickle_load(file_path: Union[str, Path], 
                   expected_types: Optional[Set[type]] = None,
                   verify_checksum: bool = True) -> Any:
    """
    Convenience function for safe pickle loading.
    
    Args:
        file_path: Path to pickle file
        expected_types: Set of expected types for validation
        verify_checksum: Whether to verify file integrity
        
    Returns:
        Unpickled data
    """
    return _default_validator.safe_load(file_path, expected_types, verify_checksum)


def safe_pickle_dump(obj: Any, file_path: Union[str, Path], 
                   create_checksum: bool = True,
                   protocol: int = pickle.HIGHEST_PROTOCOL) -> None:
    """
    Convenience function for safe pickle dumping.
    
    Args:
        obj: Object to pickle
        file_path: Output file path
    """
    return _default_validator.safe_dump(obj, file_path, create_checksum=create_checksum, protocol=protocol)


def validate_pickle_security(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate a pickle file for security issues.
    
    Args:
        file_path: Path to pickle file
        
    Returns:
        Dictionary with validation results
    """
    file_path = Path(file_path)
    
    result = {
        'file_path': str(file_path),
        'is_safe': False,
        'warnings': [],
        'errors': [],
        'file_size': 0,
        'checksum': None
    }
    
    try:
        if not file_path.exists():
            result['errors'].append("File does not exist")
            return result
        
        # Get file info
        result['file_size'] = file_path.stat().st_size
        
        # Read and validate
        with open(file_path, 'rb') as f:
            data = f.read()
        
        result['checksum'] = hashlib.sha256(data).hexdigest()
        
        # Validate format
        if not _default_validator._is_valid_pickle_format(data):
            result['errors'].append("Invalid pickle format")
            return result
        
        # Check for dangerous patterns
        if _default_validator._contains_dangerous_opcodes(data):
            result['errors'].append("Dangerous opcodes detected")
            return result
        
        # Try to load with restricted unpickler
        try:
            import io
            with io.BytesIO(data) as data_stream:
                unpickler = RestrictedUnpickler(data_stream, allowed_types=_default_validator.ALLOWED_TYPES)
                obj = unpickler.load()
            result['is_safe'] = True
            result['object_type'] = type(obj).__name__
        except Exception as e:
            result['errors'].append(f"Failed to load safely: {e}")
        
    except Exception as e:
        result['errors'].append(f"Validation error: {e}")
    
    return result
