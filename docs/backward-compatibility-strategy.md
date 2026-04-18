# APGI Framework Backward Compatibility Strategy

## Version Numbering Policy

The APGI framework follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 2.1.3)
- **MAJOR**: Breaking changes that require code modifications
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

## Compatibility Levels

### 1. Public API (SemVer Contract)

**Stability**: High - Breaking changes only in major versions

The following are considered public API and maintain backward compatibility within major versions:

- Module imports from `apgi_framework.*`
- Class constructors and public methods
- Function signatures in `__init__.py` files
- CLI commands and arguments
- Configuration file schemas
- Data file formats (HDF5, JSON)

**Deprecation Timeline:**

- Features deprecated in version N remain functional until N+1.0.0
- Deprecation warnings issued at least 2 minor versions before removal
- Migration guide provided for all breaking changes

### 2. Internal API (Framework Contract)

**Stability**: Medium - May change in minor versions

Internal modules marked with `_` prefix or documented as internal:

- Implementation details
- Private helper methods
- Testing utilities in `tests/`

### 3. Experimental API (No Contract)

**Stability**: Low - May change without notice

Explicitly marked experimental features:

- Modules in `apgi_framework/research/`
- Functions decorated with `@experimental`
- Features in documentation marked "Experimental"

## Deprecation Process

### Phase 1: Announcement (version N.x.x)

1. Add `@deprecated` decorator to function/class
2. Add deprecation warning with:
   - Feature name
   - Removal version (N+1.0.0)
   - Migration path
   - Alternative if available
3. Update documentation with migration guide

### Phase 2: Maintenance (versions N.x.x to N.y.y)

1. Maintain backward compatibility
2. Actively support migration questions
3. Add tests for both old and new paths

### Phase 3: Removal (version N+1.0.0)

1. Remove deprecated code
2. Update documentation
3. Include in release notes

## Breaking Change Categories

### Type 1: Required (Major Version Bump)

Examples:

- Removing public functions/classes
- Changing function signatures
- Modifying data file formats
- Changing default behavior

### Type 2: Recommended (Minor Version with Deprecation)

Examples:

- Adding new required parameters
- Changing return types
- Performance improvements that alter timing

### Type 3: Optional (Patch Version)

Examples:

- Bug fixes
- Security patches
- Performance optimizations without behavioral changes

## Migration Tools

### Version Compatibility Checker

```python
from apgi_framework.versioning import check_compatibility

check_compatibility(current_version="1.2.3", target_version="2.0.0")
```

### Automated Migration Script

```bash
python -m apgi_framework.migration --from 1.x --to 2.x --check
python -m apgi_framework.migration --from 1.x --to 2.x --apply
```

## API Versioning

### REST API

API version specified in URL path:

- `/api/v1/experiments`
- `/api/v2/experiments`

Headers for version negotiation:

```text
Accept: application/vnd.apgi.v2+json
```

### Python API

Version-specific imports:

```python
from apgi_framework.v1 import ExperimentRunner  # Old API
from apgi_framework.v2 import ExperimentRunner  # New API
from apgi_framework import ExperimentRunner     # Current stable API
```

## Configuration Compatibility

### Versioned Config Files

Configuration files include version identifier:

```yaml
# apgi_config.yaml
version: "2.1"
experimental:
  enabled: true
  parameters:
    theta_0: 0.5
```

### Automatic Migration

Framework automatically upgrades configs:

- Detects config version
- Applies migration transforms
- Backs up original
- Writes migrated version

## Data Format Compatibility

### HDF5 Files

- Version stored in file metadata
- Reader supports multiple versions
- Migration utilities provided

### JSON Files

- Schema version in `$schema` field
- Backward-compatible reading
- Forward-compatible writing

## Testing for Compatibility

### CI/CD Compatibility Tests

```yaml
# .github/workflows/compatibility.yml
strategy:
  matrix:
    version: ["1.0", "1.1", "current"]
```

### API Contract Tests

Tests verify:

- Function signatures unchanged
- Return types consistent
- Behavior consistent
- Performance not degraded

## Community Communication

### Release Notes

Every release includes:

- New features
- Bug fixes
- Deprecation notices
- Breaking changes
- Migration guide link

### Deprecation Notices

Published:

- GitHub Discussions
- Documentation site
- In-code warnings
- Release notes

### Support Timeline

| Version | Release Date | End of Support |
|---------|--------------|----------------|
| 1.x     | 2024-01-01   | 2025-01-01     |
| 2.x     | 2024-06-01   | 2025-06-01     |
| 3.x     | (current)    | TBD            |

## Migration Guides

### 1.x to 2.x

See: [Migration Guide 1to2.md](migration-guides/Migration-Guide-1to2.md)

Key changes:

- Parameter estimation API restructured
- Configuration format updated
- CLI commands renamed

### 2.x to 3.x

See: [Migration Guide 2to3.md](migration-guides/Migration-Guide-2to3.md)

Key changes:

- Async API introduction
- New data model
- Enhanced security defaults

## Exception Process

For critical security or bug fixes that require breaking changes:

1. Security team review
2. Community announcement
3. Expedited timeline
4. Extended support for affected versions

## Contact

For compatibility questions:

- GitHub Discussions: [Compatibility Q&A](<https://github.com/apgi/discussions>)
- Email: <compatibility@apgi.org>
- Slack: #compatibility channel

## Glossary

- **Breaking Change**: Change requiring code modification by users
- **Deprecation**: Announcement of future removal
- **End of Support**: No more patches/updates provided
- **LTS**: Long Term Support version
- **Migration**: Process of updating code for new version
- **Semantic Versioning**: Version scheme (MAJOR.MINOR.PATCH)
