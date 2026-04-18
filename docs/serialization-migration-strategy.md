# Serialization Migration Strategy for APGI Framework

## Overview

This document defines the strategy for migrating from pickle-based serialization to safer alternatives (JSON/msgpack) across the APGI Framework, reducing security risks and improving maintainability.

## Current State

**Issues:**

- 235+ pickle references across 30 files
- Pickle allows arbitrary code execution
- Security vulnerabilities if untrusted data is deserialized
- Limited interoperability with other systems
- Difficult to debug serialized data

**Existing Mitigations:**

- `secure_pickle.py` (510 lines) with validation
- Whitelist types
- Dangerous opcode detection
- Forbidden module blocking
- Checksums for data integrity

## Target Architecture

### 1. Serialization Format Hierarchy

**Priority Order:**

1. **JSON** - For simple, serializable data (dicts, lists, primitives)
2. **Msgpack** - For binary-efficient serialization of complex data
3. **Secure Pickle** - Only for objects that cannot be serialized otherwise

**Decision Tree:**

```text
Can serialize as JSON?
├─ Yes → Use JSON (faster, human-readable)
└─ No → Can serialize as msgpack?
    ├─ Yes → Use msgpack (binary, efficient)
    └─ No → Use secure pickle with trusted mode
```

### 2. Data Classification

**Safe for JSON:**

- Configuration data
- Experiment parameters
- Metadata
- Results that are JSON-serializable

**Safe for Msgpack:**

- Numerical arrays
- Binary data
- Large datasets
- Time-series data

**Requires Secure Pickle:**

- Custom class instances
- Complex object graphs
- Lambda functions
- Objects with external dependencies

## Implementation Strategy

### Phase 1: Audit and Classification

**Tasks:**

1. Scan all pickle usage across codebase
2. Classify each usage by data type
3. Identify critical vs non-critical paths
4. Create migration priority list

**Tool:**

```python
# scripts/audit_pickle_usage.py
import ast
import os
from pathlib import Path

def find_pickle_usage():
    """Find all pickle usage in codebase."""
    pickle_refs = []
    for py_file in Path('.').rglob('*.py'):
        content = py_file.read_text()
        if 'pickle' in content or 'joblib' in content:
            pickle_refs.append(py_file)
    return pickle_refs
```

### Phase 2: JSON Migration (High Priority)

**Target Files:**

- Configuration files
- Experiment metadata
- API responses
- Data validation results

**Implementation:**

```python
import json
from typing import Any

def serialize_json(data: Any) -> str:
    """Serialize data to JSON with custom encoder."""
    return json.dumps(data, cls=APGIJSONEncoder, indent=2)

def deserialize_json(json_str: str) -> Any:
    """Deserialize JSON string with custom decoder."""
    return json.loads(json_str, cls=APGIJSONDecoder)

class APGIJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for APGI data types."""
    def default(self, obj):
        if hasattr(obj, 'to_json'):
            return obj.to_json()
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        return super().default(obj)
```

### Phase 3: Msgpack Migration (Medium Priority)

**Target Files:**

- Neural simulation results
- Large datasets
- Time-series data
- Binary data

**Implementation:**

```python
import msgpack

def serialize_msgpack(data: Any) -> bytes:
    """Serialize data to msgpack format."""
    return msgpack.packb(data, use_bin_type=True)

def deserialize_msgpack(data: bytes) -> Any:
    """Deserialize msgpack data."""
    return msgpack.unpackb(data, raw=False)
```

### Phase 4: Secure Pickle Isolation (Low Priority)

**Approach:**

- Keep `secure_pickle.py` for legacy data
- Add deprecation warnings
- Require explicit `trusted_mode=True` flag
- Document why pickle is necessary for each use case

**Implementation:**

```python
def load_pickle_trusted(file_path: Path, trusted: bool = False):
    """Load pickle file with explicit trust flag."""
    if not trusted:
        raise SecurityError(
            "Pickle loading requires explicit trusted=True. "
            "Consider migrating to JSON/msgpack."
        )
    return SecurePickleValidator.load(file_path)
```

## Migration Guidelines

### When to Use JSON

**Use JSON when:**

- Data is configuration or metadata
- Data needs to be human-readable
- Interoperability with web APIs is required
- Data size is small (< 1MB)

**Example:**

```python
# Before
with open('config.pkl', 'wb') as f:
    pickle.dump(config, f)

# After
with open('config.json', 'w') as f:
    json.dump(config, f, cls=APGIJSONEncoder)
```

### When to Use Msgpack

**Use msgpack when:**

- Data is numerical or binary
- Performance is critical
- Data size is medium (1MB - 100MB)
- Binary efficiency is needed

**Example:**

```python
# Before
with open('results.pkl', 'wb') as f:
    pickle.dump(results, f)

# After
with open('results.msgpack', 'wb') as f:
    f.write(msgpack.packb(results, use_bin_type=True))
```

### When to Keep Secure Pickle

**Keep pickle only when:**

- Data contains custom class instances
- Object graphs are complex
- Migration would break existing functionality
- Explicit `trusted=True` flag is provided

**Example:**

```python
# Only for legacy data with explicit trust
with open('legacy_object.pkl', 'rb') as f:
    obj = SecurePickleValidator.load(f, trusted=True)
```

## File Format Migration

### File Extension Convention

| Format | Extension | Use Case |
| --- | --- | --- |
| JSON | `.json` | Config, metadata, API data |
| Msgpack | `.msgpack` or `.mp` | Binary data, arrays |
| Secure Pickle | `.pkl.secure` | Legacy objects only |

### Backward Compatibility

**Strategy:**

1. Support reading both old and new formats
2. Write new format by default
3. Provide migration tool for old files
4. Deprecate old format after migration period

**Implementation:**

```python
def load_data(file_path: Path):
    """Load data with format auto-detection."""
    if file_path.suffix == '.json':
        return load_json(file_path)
    elif file_path.suffix in ('.msgpack', '.mp'):
        return load_msgpack(file_path)
    elif file_path.suffix == '.pkl':
        logger.warning("Loading legacy pickle file")
        return load_secure_pickle(file_path, trusted=True)
    else:
        raise ValueError(f"Unknown file format: {file_path.suffix}")
```

## Performance Considerations

### Benchmarks

**Expected performance:**

- JSON: Fast for small data, slower for large
- Msgpack: 2-5x faster than JSON for binary data
- Secure Pickle: Slowest due to validation overhead

**Recommendation:**

- Use JSON for < 1MB data
- Use msgpack for 1MB - 100MB data
- Consider memory-mapped files for > 100MB

### Memory Usage

**JSON:**

- Pros: Human-readable, debuggable
- Cons: Higher memory usage for binary data

**Msgpack:**

- Pros: Compact, efficient for binary data
- Cons: Not human-readable

**Secure Pickle:**

- Pros: Can serialize anything
- Cons: Highest memory usage, security risk

## Security Considerations

### JSON Security

**Risks:**

- None for simple JSON
- Potential for XXE in XML (not applicable)

**Mitigations:**

- Use `json.loads` with object_hook for validation
- Validate schema after deserialization
- Limit maximum document size

### Msgpack Security

**Risks:**

- Binary format can hide malicious data
- Potential for memory exhaustion with large payloads

**Mitigations:**

- Limit maximum message size
- Validate structure after unpacking
- Use `max_buffer_size` parameter

### Secure Pickle Security

**Risks:**

- Arbitrary code execution
- Deserialization attacks

**Mitigations:**

- Require explicit `trusted=True` flag
- Validate all deserialized objects
- Maintain whitelist of allowed types
- Add checksums for integrity

## Testing Strategy

### Unit Tests

**Test cases:**

- JSON serialization/deserialization
- Msgpack serialization/deserialization
- Custom encoder/decoder functionality
- Format auto-detection
- Backward compatibility

### Integration Tests

**Test scenarios:**

- Load old pickle files, save as new format
- Migrate existing data files
- Verify data integrity after migration
- Performance benchmarks

### Security Tests

**Test scenarios:**

- Attempt to load malicious pickle without trusted flag
- Test oversized message rejection
- Validate schema enforcement
- Test checksum verification

## Rollback Plan

If migration causes issues:

1. Revert to pickle for affected components
2. Keep new serialization code for future use
3. Investigate and fix migration bugs
4. Re-attempt migration with fixes

## Monitoring

### Metrics to Track

- Number of pickle references remaining
- Migration progress by module
- Performance impact (serialization time)
- Data integrity validation results
- Security incidents related to serialization

## Dependencies

```txt
# Add to requirements.txt
msgpack>=1.0.5
orjson>=3.9.0  # Faster JSON alternative
```

## Migration Checklist

For each file using pickle:

- [ ] Classify data type (JSON/msgpack/pickle)
- [ ] Implement new serialization method
- [ ] Add backward compatibility for reading old files
- [ ] Update file extension
- [ ] Add tests for new serialization
- [ ] Update documentation
- [ ] Remove pickle code after migration period
- [ ] Verify data integrity

## Timeline

**Phase 1 (Week 1):** Audit and classification
**Phase 2 (Week 2-3):** JSON migration for config/metadata
**Phase 3 (Week 4-5):** Msgpack migration for simulation results
**Phase 4 (Week 6):** Secure pickle isolation and deprecation
**Phase 5 (Week 7):** Testing and validation
**Phase 6 (Week 8):** Documentation and cleanup

## References

- Python pickle security: <https://docs.python.org/3/library/pickle.html#restricting-globals>
- Msgpack specification: <https://msgpack.org/>
- OWASP Deserialization: <https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html>
