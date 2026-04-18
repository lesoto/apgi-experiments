# Authentication Strategy for APGI Framework

## Overview

This document defines the authentication and authorization strategy for the APGI Framework, replacing the simplistic static API key model with a robust JWT-based authentication system with role-based access control (RBAC).

## Current State

**Issues:**

- Single static API key with no expiration
- No role-based access control
- No token rotation mechanism
- No audit boundary for authentication events
- No session management
- No multi-factor authentication support

## Target Architecture

### 1. JWT-Based Authentication

**Components:**

- Access tokens (short-lived, 15 minutes)
- Refresh tokens (long-lived, 7 days)
- Token signing with RS256 (asymmetric keys)
- Token validation middleware
- Token refresh endpoint

**Token Payload Structure:**

```json
{
  "sub": "user_id",
  "iat": 1234567890,
  "exp": 1234567890,
  "jti": "unique_token_id",
  "roles": ["researcher", "analyst"],
  "permissions": ["read:experiments", "write:results"],
  "scope": "api_access"
}
```

### 2. Role-Based Access Control (RBAC)

**Roles:**

- `admin`: Full system access
- `researcher`: Read/write access to experiments
- `analyst`: Read-only access to results
- `viewer`: Limited read access

**Permissions:**

- `read:experiments` - View experiment data
- `write:experiments` - Create/modify experiments
- `read:results` - View analysis results
- `write:results` - Create/modify analyses
- `admin:users` - Manage users
- `admin:config` - Modify system configuration

### 3. User Management

**User Model:**

```python
class User:
    id: str
    username: str
    email: str
    roles: List[str]
    permissions: List[str]
    created_at: datetime
    last_login: datetime
    is_active: bool
    mfa_enabled: bool
```

### 4. Authentication Flow

```text
1. User provides credentials (username/password or API key)
2. Server validates credentials
3. Server generates JWT access token + refresh token
4. Server stores refresh token (hashed) in database
5. Client stores tokens securely
6. Client includes access token in Authorization header
7. Server validates token on each request
8. When access token expires, client uses refresh token
9. Server issues new access token if refresh token valid
10. Refresh token rotation on each use
```

## Implementation Plan

### Phase 1: Core JWT Infrastructure

**Files to Create:**

1. `apgi_framework/auth/jwt_manager.py` - JWT token generation/validation
2. `apgi_framework/auth/user_manager.py` - User management
3. `apgi_framework/auth/middleware.py` - Authentication middleware
4. `apgi_framework/auth/exceptions.py` - Custom auth exceptions

**Dependencies:**

```text
pyjwt>=2.8.0
cryptography>=41.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
```

### Phase 2: API Key Migration

**Approach:**

- Keep existing API keys for backward compatibility
- Add deprecation warning for API key usage
- Provide migration path from API keys to JWT
- Phase out API keys after migration period

### Phase 3: RBAC Implementation

**Components:**

- Role definitions in configuration
- Permission checking decorators
- Endpoint-level authorization
- Admin interface for user management

### Phase 4: Security Enhancements

**Features:**

- Token rotation on refresh
- Token blacklist for revocation
- Rate limiting on auth endpoints
- Audit logging for auth events
- MFA support (optional)

## Configuration

### Environment Variables

```bash
# JWT Configuration
APGI_JWT_SECRET_KEY=<random-256-bit-key>
APGI_JWT_ALGORITHM=RS256
APGI_JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
APGI_JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Authentication
APGI_AUTH_ENABLED=true
APGI_AUTH_TYPE=jwt
APGI_API_KEY_DEPRECATION_DATE=2024-12-31

# User Management
APGI_DEFAULT_ADMIN_USERNAME=admin
APGI_DEFAULT_ADMIN_EMAIL=admin@example.com
```

## API Endpoints

### Authentication Endpoints

```python
POST /api/v1/auth/login
POST /api/v1/auth/logout
POST /api/v1/auth/refresh
POST /api/v1/auth/verify
GET /api/v1/auth/me
```

### User Management Endpoints (Admin)

```python
GET /api/v1/users
POST /api/v1/users
GET /api/v1/users/{user_id}
PUT /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}
POST /api/v1/users/{user_id}/roles
```

## Security Considerations

### Token Storage

**Server-side:**

- Store refresh tokens hashed (bcrypt)
- Implement token blacklist
- Set appropriate expiration times

**Client-side:**

- Store tokens in httpOnly cookies (web)
- Use secure storage for mobile/desktop
- Never store tokens in localStorage

### Key Management

**Development:**

- Use environment variables for keys
- Generate keys with `openssl rand -hex 32`

**Production:**

- Use key management service (AWS KMS, HashiCorp Vault)
- Implement key rotation
- Separate signing and verification keys

### Rate Limiting

**Endpoints to protect:**

- `/api/v1/auth/login` - 5 requests per minute
- `/api/v1/auth/refresh` - 10 requests per minute
- `/api/v1/auth/verify` - 20 requests per minute

## Migration Path

### For Existing API Key Users

1. Add JWT authentication alongside API keys
2. Provide migration endpoint: `POST /api/v1/auth/migrate-api-key`
3. Send deprecation notices to API key users
4. Disable API key creation after migration period
5. Remove API key support after deprecation date

### Example Migration Flow

```python
# Old way (deprecated)
headers = {"X-API-Key": "static-api-key"}

# New way (JWT)
# 1. Get tokens
response = requests.post("/api/v1/auth/login", json={
    "username": "user",
    "password": "pass"
})
tokens = response.json()

# 2. Use access token
headers = {"Authorization": f"Bearer {tokens['access_token']}"}

# 3. Refresh when needed
response = requests.post("/api/v1/auth/refresh", json={
    "refresh_token": tokens['refresh_token']
})
```

## Monitoring and Auditing

### Metrics to Track

- Failed login attempts
- Successful logins
- Token refresh frequency
- API key usage (for migration tracking)
- Permission denials

### Audit Events

```python
{
  "event_type": "auth_login",
  "user_id": "user_123",
  "timestamp": "2024-01-01T00:00:00Z",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "success": true,
  "method": "jwt"
}
```

## Testing Strategy

### Unit Tests

- JWT token generation/validation
- User CRUD operations
- Permission checking
- Token refresh flow
- API key migration

### Integration Tests

- End-to-end authentication flow
- Protected endpoint access
- Token expiration handling
- Concurrent token refresh
- Rate limiting

### Security Tests

- Token tampering detection
- Brute force protection
- Token blacklist enforcement
- SQL injection in auth queries
- XSS in auth responses

## Rollback Plan

If JWT implementation has issues:

1. Revert to API key authentication
2. Keep JWT code but disable via configuration
3. Monitor for security issues
4. Address bugs in next iteration

## References

- JWT Best Practices: <https://tools.ietf.org/html/rfc8725>
- OWASP Authentication Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html>
- OAuth 2.0 for Browser-Based Apps: <https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps>
