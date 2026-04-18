# API Versioning Strategy for APGI Framework

## Overview

This document defines the API versioning and integration contract strategy for the APGI Framework, ensuring backward compatibility, clear deprecation policies, and structured evolution of public APIs.

## Current State

**Issues:**

- No OpenAPI/JSON Schema versioning found
- k8s deployment.yaml exists but no API versioning
- No backward compatibility strategy codified
- No formal integration contracts
- Optional dependency behavior creates variant runtime paths

## Target Architecture

### 1. Semantic Versioning

**Version Format:** `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (incompatible API changes)
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**Example:** `1.2.0` → Major version 1, Minor version 2, Patch 0

### 2. API Versioning Strategy

**Approach:** URL-based versioning

```text
/api/v1/experiments
/api/v2/experiments
/api/v3/experiments
```

**Version Support Policy:**

- Current version (N): Fully supported, active development
- Previous version (N-1): Maintenance mode, bug fixes only
- Older versions (N-2 and below): Deprecated, no support

**Deprecation Timeline:**

- Announce deprecation: 6 months before removal
- Warning in API responses: 3 months before removal
- Remove deprecated version: After 6-month grace period

### 3. OpenAPI Specification

**Location:** `docs/api/openapi.yaml`

**Structure:**

```yaml
openapi: 3.0.3
info:
  title: APGI Framework API
  version: 1.2.0
  description: API for APGI Framework experiments and analysis
servers:
  - url: http://localhost:8000/api/v1
    description: Development server
  - url: https://api.apgi-framework.com/api/v1
    description: Production server
paths:
  /experiments:
    get:
      summary: List experiments
      operationId: listExperiments
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ExperimentList'
```

### 4. Schema Versioning

**JSON Schema Versioning:**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://apgi-framework.com/schemas/experiment/v1.json",
  "title": "Experiment Schema v1",
  "type": "object",
  "properties": {
    "version": {
      "type": "string",
      "const": "1.0.0"
    }
  }
}
```

**Backward Compatibility Rules:**

- Add optional fields: OK
- Rename required fields: BREAKING
- Change field type: BREAKING
- Remove required fields: BREAKING
- Remove optional fields: OK (with deprecation)

## Implementation Plan

### Phase 1: OpenAPI Specification

**Tasks:**

1. Create `docs/api/openapi.yaml` with current API endpoints
2. Document all request/response schemas
3. Add authentication requirements
4. Include examples for each endpoint
5. Generate client SDKs from spec

**Tools:**

```text
openapi-spec-validator>=0.5.0
prance>=23.6.23.0
```

### Phase 2: API Versioning Implementation

**Tasks:**

1. Add version prefix to all API routes
2. Implement version negotiation
3. Add version deprecation warnings
4. Create version migration guide
5. Update documentation

**Implementation:**

```python
from fastapi import APIRouter

# Version 1 router
v1_router = APIRouter(prefix="/v1", tags=["experiments"])

@v1_router.get("/experiments")
async def list_experiments_v1():
    """List experiments (v1)."""
    return experiments

# Version 2 router
v2_router = APIRouter(prefix="/v2", tags=["experiments"])

@v2_router.get("/experiments")
async def list_experiments_v2():
    """List experiments (v2) with enhanced filtering."""
    return experiments_enhanced
```

### Phase 3: Backward Compatibility Tests

**Tasks:**

1. Create test suite for API compatibility
2. Test v1 clients against v2 API
3. Test data migration between versions
4. Add integration tests for version transitions

**Test Structure:**

```python
def test_v1_api_compatibility():
    """Test v1 API still works with v2 backend."""
    response = client.get("/api/v1/experiments")
    assert response.status_code == 200
    assert "deprecated" in response.headers

def test_v2_enhancements():
    """Test v2 API enhancements."""
    response = client.get("/api/v2/experiments")
    assert response.status_code == 200
    assert "pagination" in response.json()
```

### Phase 4: Configuration Versioning

**Tasks:**

1. Version configuration schemas
2. Add config migration utilities
3. Document config breaking changes
4. Provide config upgrade scripts

**Implementation:**

```python
class ConfigVersionManager:
    """Manage configuration versioning and migration."""
    
    CURRENT_VERSION = "1.2.0"
    
    def migrate_config(self, config: Dict, from_version: str) -> Dict:
        """Migrate config from old version to current."""
        if from_version == self.CURRENT_VERSION:
            return config
        
        # Apply migrations
        for version in self._get_migration_path(from_version):
            config = self._apply_migration(config, version)
        
        return config
```

## API Endpoint Design

### Versioned Endpoints

**Pattern:** `/api/{version}/{resource}`

**Examples:**

```text
GET  /api/v1/experiments
POST /api/v1/experiments
GET  /api/v1/experiments/{id}
PUT  /api/v1/experiments/{id}

GET  /api/v2/experiments
POST /api/v2/experiments
GET  /api/v2/experiments/{id}
PUT  /api/v2/experiments/{id}
```

### Version Negotiation

**Headers:**

```text
Accept: application/vnd.apgi.v1+json
API-Version: 1
```

**Fallback:**

- If no version specified, use current version
- Return version in response header

```text
API-Version: 1.2.0
```

## Breaking Change Guidelines

### When to Increment MAJOR Version

**Breaking Changes:**

- Remove or rename required fields
- Change field types (incompatible)
- Remove endpoints
- Change authentication requirements
- Change response format significantly

**Example:**

```python
# v1
{
  "subject_id": "123",
  "data": [...]
}

# v2 (breaking - renamed field)
{
  "participant_id": "123",  # Was subject_id
  "measurements": [...]  # Was data
}
```

### When to Increment MINOR Version

**Non-Breaking Changes:**

- Add new optional fields
- Add new endpoints
- Add new query parameters
- Add new response headers

**Example:**

```python
# v1.0
{
  "subject_id": "123",
  "data": [...]
}

# v1.1 (non-breaking - added optional field)
{
  "subject_id": "123",
  "data": [...],
  "metadata": {...}  # New optional field
}
```

### When to Increment PATCH Version

**Bug Fixes:**

- Fix validation bugs
- Fix error handling
- Fix performance issues
- Fix documentation

## Deprecation Process

### 1. Announce Deprecation

**Timeline:** 6 months before removal

**Actions:**

- Add deprecation notice to documentation
- Add deprecation header to API responses
- Send notices to registered API users
- Update changelog

**Response Header:**

```text
Deprecation: true
Sunset: 2024-12-31
Link: </api/v2/experiments>; rel="successor-version"
```

### 2. Warning Period

**Timeline:** 3 months before removal

**Actions:**

- Log warnings for deprecated endpoint usage
- Return warnings in API responses
- Provide migration guide
- Offer support for migration

### 3. Removal

**Timeline:** After 6-month grace period

**Actions:**

- Remove deprecated endpoints
- Update documentation
- Archive old API specs
- Communicate removal completion

## Documentation Requirements

### API Documentation

**Sections:**

1. Quick start guide
2. Authentication
3. Versioning policy
4. Endpoint reference
5. Schema definitions
6. Error codes
7. Rate limiting
8. Changelog

### Changelog Format

```markdown
## [1.2.0] - 2024-01-15

### Added
- New filtering options for experiments endpoint
- Pagination support for list endpoints

### Changed
- Enhanced error responses with detailed context

### Deprecated
- `/api/v1/legacy` endpoint (use `/api/v2/experiments`)

### Removed
- None

### Fixed
- Fixed timezone handling in timestamp fields
```

## Integration Contracts

### Public API Contract

**Stability Guarantee:**

- v1.x: Stable within major version
- Breaking changes only in major versions
- 6-month deprecation notice required

**Testing Requirements:**

- All public APIs must have integration tests
- Version compatibility tests required
- Contract tests for external integrations

### Internal API Contract

**Stability:** No stability guarantee

**Documentation:**

- Internal APIs documented for developers
- May change without notice
- Use at own risk

## Optional Dependencies

### Strategy

**Principle:** Optional dependencies should not create variant runtime paths that reduce robustness.

**Implementation:**

```python
try:
    import optional_library
    HAS_OPTIONAL = True
except ImportError:
    HAS_OPTIONAL = False

def process_data(data):
    if not HAS_OPTIONAL:
        raise NotImplementedError(
            "This feature requires optional_library. "
            "Install with: pip install apgi-framework[optional]"
        )
    return optional_library.process(data)
```

**Documentation:**

- Clearly document optional features
- Provide installation instructions
- Add runtime checks with helpful error messages
- Test both with and without optional dependencies

## Configuration Versioning

### Config Schema Versioning

**Format:**

```yaml
config:
  version: "1.2.0"
  experiments:
    # config fields
```

**Migration:**

```python
def migrate_config(config: Dict) -> Dict:
    """Migrate config to latest version."""
    config_version = config.get("config", {}).get("version", "1.0.0")
    
    if config_version != CURRENT_CONFIG_VERSION:
        # Apply migrations
        for migration in MIGRATIONS[config_version:]:
            config = migration(config)
        
        config["config"]["version"] = CURRENT_CONFIG_VERSION
    
    return config
```

## Monitoring

### Metrics to Track

- API version usage distribution
- Deprecated endpoint call rates
- Response times by version
- Error rates by version
- Client SDK versions

### Alerts

- High usage of deprecated versions
- Breaking changes approaching deprecation
- Version compatibility issues

## Rollback Plan

If API versioning causes issues:

1. Revert to previous API version
2. Keep new version in maintenance mode
3. Investigate and fix issues
4. Re-release with fixes

## References

- Semantic Versioning: <https://semver.org/>
- OpenAPI Specification: <https://swagger.io/specification/>
- API Versioning Best Practices: <https://restfulapi.net/versioning/>
