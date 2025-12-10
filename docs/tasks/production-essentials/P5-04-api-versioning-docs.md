# P5-04: Document API Versioning Strategy

## Task Identifier
**ID:** P5-04
**Phase:** 5 - Developer Experience
**Domain:** Documentation
**Complexity:** S (Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| None | - | - | Can be developed independently |

## Scope

### In Scope
- Document the API versioning strategy (URL path-based)
- Define breaking change criteria
- Create deprecation policy and timeline
- Document client migration patterns
- Create API changelog template
- Document version negotiation behavior
- Provide examples of version evolution

### Out of Scope
- Implementing multiple API versions (only v1 exists)
- Automated changelog generation from commits
- API breaking change detection in CI
- Header-based versioning implementation
- GraphQL versioning (REST only)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/docs/
  api-versioning.md               # Main versioning strategy document
  api-changelog.md                # Changelog template
  api-migration-guide-template.md # Migration guide template
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/backend/app/main.py              # API prefix configuration
template/{{cookiecutter.project_slug}}/backend/app/api/routers/*.py    # Existing API structure
template/{{cookiecutter.project_slug}}/backend/app/core/config.py      # API_V1_PREFIX setting
```

## Implementation Details

### 1. API Versioning Strategy (`docs/api-versioning.md`)

```markdown
# API Versioning Strategy

This document defines the API versioning strategy for {{ cookiecutter.project_name }}.

## Overview

{{ cookiecutter.project_name }} uses **URL path-based versioning** for its REST API. All API endpoints include a version prefix in the URL path.

**Current Version:** v1
**Base URL:** `{{ cookiecutter.backend_api_prefix }}`
**Full Example:** `https://api.example.com{{ cookiecutter.backend_api_prefix }}/health`

## Versioning Approach

### Why URL Path Versioning?

We chose URL path versioning over alternatives for these reasons:

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| **URL Path** (`/api/v1/`) | Simple, visible, cacheable | URL changes between versions | **Selected** |
| Header (`Accept-Version`) | Clean URLs | Hidden, harder to test | Not selected |
| Query param (`?version=1`) | Flexible | Easy to forget, caching issues | Not selected |
| Content negotiation | RESTful | Complex, tooling issues | Not selected |

**Key benefits of URL path versioning:**
- Immediately visible in logs, documentation, and debugging
- Easy to route at load balancer level
- Simple to test with curl/browser
- Clear separation of version-specific code
- CDN/cache friendly (different URLs = different cache entries)

### Version Format

Versions follow this format:

```
/api/v{MAJOR}/
```

- **MAJOR**: Incremented for breaking changes only
- Minor and patch changes do not create new versions

Examples:
- `/api/v1/users` - Version 1
- `/api/v2/users` - Version 2 (breaking changes)

## Versioning Policy

### Supported Versions

| Version | Status | End of Support |
|---------|--------|----------------|
| v1 | **Current** | - |

### Support Timeline

- **Current version**: Fully supported with new features and bug fixes
- **Previous version (N-1)**: Bug fixes and security patches only, deprecated
- **Older versions (N-2+)**: Unsupported, may be removed

**Minimum support period**: Each version is supported for at least **12 months** after the next major version is released.

### Deprecation Process

1. **Announcement** (Month 0): New version released, previous version marked deprecated
2. **Migration Period** (Months 1-6): Both versions fully functional, migration encouraged
3. **Reduced Support** (Months 7-12): Bug fixes only for deprecated version
4. **End of Life** (Month 12+): Deprecated version may be removed

## Breaking Changes

### What Constitutes a Breaking Change

The following changes **require a new major version**:

#### Request Breaking Changes
- Removing an endpoint
- Renaming an endpoint path
- Removing a required request field
- Making an optional request field required
- Changing a field's data type
- Changing request validation to be more restrictive
- Removing support for a request format (e.g., query params to body only)

#### Response Breaking Changes
- Removing a response field
- Renaming a response field
- Changing a field's data type
- Changing the structure of nested objects
- Changing enum values (removal or rename)
- Changing error response format

#### Behavioral Breaking Changes
- Changing authentication requirements
- Changing authorization/permission requirements
- Changing rate limit behavior significantly
- Changing the semantics of an operation

### What Is NOT a Breaking Change

The following changes are **backward compatible** and do not require a new version:

- Adding new endpoints
- Adding optional request fields
- Adding new response fields
- Adding new enum values (addition only)
- Relaxing validation (e.g., increasing a limit)
- Adding new error codes (while keeping existing ones)
- Performance improvements
- Bug fixes (unless clients depend on buggy behavior)

### Example: Breaking vs Non-Breaking

**Non-breaking (v1 remains v1):**
```python
# Before: GET /api/v1/users returns
{ "id": 1, "name": "John" }

# After: Adding a new field is non-breaking
{ "id": 1, "name": "John", "email": "john@example.com" }
```

**Breaking (requires v2):**
```python
# Before: GET /api/v1/users returns
{ "id": 1, "name": "John" }

# After: Renaming a field is breaking
{ "id": 1, "full_name": "John" }  # 'name' -> 'full_name' breaks clients
```

## Version Negotiation

### Default Behavior

- Requests to `/api/v1/*` always use v1 behavior
- Requests to `/api/v2/*` always use v2 behavior (when available)
- No automatic version negotiation or fallback

### Explicit Version Required

Clients must explicitly specify the API version in the URL. There is no "latest" alias to prevent accidental breaking changes.

**Correct:**
```bash
curl https://api.example.com/api/v1/users
```

**Incorrect (no version):**
```bash
curl https://api.example.com/api/users  # 404 Not Found
```

## Client Migration

### Migration Guide Template

When releasing a new major version, provide:

1. **Migration Guide**: Step-by-step instructions
2. **Changelog**: Complete list of changes
3. **Compatibility Matrix**: What works, what doesn't
4. **Timeline**: Deprecation and EOL dates

See [API Migration Guide Template](./api-migration-guide-template.md) for the full template.

### Recommended Migration Process

1. **Review changes**: Read the migration guide and changelog
2. **Update API client**: Use the new version's SDK or update URLs
3. **Test thoroughly**: Verify all integrations in staging
4. **Monitor**: Watch for errors after deployment
5. **Complete migration**: Remove old version references

### Handling Multiple Versions

During migration periods, clients may need to support multiple versions:

```typescript
// API client configuration
const API_VERSION = process.env.API_VERSION || 'v1';
const BASE_URL = `https://api.example.com/api/${API_VERSION}`;

// Feature flags for version-specific behavior
if (API_VERSION === 'v2') {
  // Use new field names
  user.fullName = response.full_name;
} else {
  // Use old field names
  user.fullName = response.name;
}
```

## Implementation Guidelines

### Backend: Version-Specific Routers

```python
# app/api/v1/router.py
from fastapi import APIRouter
v1_router = APIRouter(prefix="/api/v1")

# app/api/v2/router.py
from fastapi import APIRouter
v2_router = APIRouter(prefix="/api/v2")

# app/main.py
app.include_router(v1_router)
app.include_router(v2_router)  # When v2 is released
```

### Shared vs Version-Specific Logic

- **Shared**: Business logic, database models, utilities
- **Version-specific**: Request/response models, serialization, routers

```
app/
  core/           # Shared business logic
  models/         # Shared database models
  api/
    v1/           # Version 1 specific
      routers/
      schemas/    # v1 request/response models
    v2/           # Version 2 specific
      routers/
      schemas/    # v2 request/response models
```

### Testing Multiple Versions

```python
# tests/api/test_users_v1.py
def test_get_user_v1(client):
    response = client.get("/api/v1/users/1")
    assert "name" in response.json()  # v1 field

# tests/api/test_users_v2.py
def test_get_user_v2(client):
    response = client.get("/api/v2/users/1")
    assert "full_name" in response.json()  # v2 field
```

## Documentation

### OpenAPI Specification

Each version has its own OpenAPI spec:

- `/openapi.json` - Current version (v1)
- `/api/v1/openapi.json` - Version 1 spec
- `/api/v2/openapi.json` - Version 2 spec (when available)

### Swagger UI

Interactive documentation available at:

- `/docs` - Current version
- `/api/v1/docs` - Version 1 docs
- `/api/v2/docs` - Version 2 docs (when available)

## Changelog

See [API Changelog](./api-changelog.md) for the complete history of API changes.

## Related Documentation

- [ADR-XXX: API Versioning Strategy](../adr/)
- [API Changelog](./api-changelog.md)
- [Migration Guide Template](./api-migration-guide-template.md)
```

### 2. API Changelog Template (`docs/api-changelog.md`)

```markdown
# API Changelog

All notable changes to the {{ cookiecutter.project_name }} API are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for API versions.

## [Unreleased]

### Added
- (List new endpoints, fields, or features)

### Changed
- (List modifications to existing functionality)

### Deprecated
- (List features that will be removed in future versions)

### Removed
- (List removed features - only in major versions)

### Fixed
- (List bug fixes)

### Security
- (List security-related changes)

---

## [v1] - {{ cookiecutter.project_slug }} Initial Release

### Added

#### Authentication Endpoints
- `POST /api/v1/auth/token` - Exchange authorization code for tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/auth/me` - Get current user information
- `POST /api/v1/auth/logout` - Revoke tokens

#### Health Endpoints
- `GET /api/v1/health` - Application health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

#### Todo Endpoints (Demo)
- `GET /api/v1/todos` - List todos for current tenant
- `POST /api/v1/todos` - Create a new todo
- `GET /api/v1/todos/{id}` - Get todo by ID
- `PUT /api/v1/todos/{id}` - Update a todo
- `DELETE /api/v1/todos/{id}` - Delete a todo

### Notes
- Initial release with OAuth 2.0 / OIDC authentication
- Multi-tenant architecture with Row-Level Security
- Rate limiting via Redis

---

## Changelog Entry Template

When adding new entries, use this template:

```markdown
## [vX] - YYYY-MM-DD

### Added
- `METHOD /api/vX/endpoint` - Description of new endpoint
- New field `field_name` added to `EndpointResponse`

### Changed
- `METHOD /api/vX/endpoint` - Description of change
- Field `old_name` renamed to `new_name` in `SchemaName`

### Deprecated
- `METHOD /api/vX/endpoint` - Will be removed in vY. Use `/api/vX/new-endpoint` instead.
- Field `field_name` in `SchemaName` - Will be removed in vY.

### Removed
- `METHOD /api/vX-1/endpoint` - Removed, use vX equivalent
- Field `field_name` removed from `SchemaName`

### Fixed
- Fixed issue where `endpoint` returned incorrect data when...

### Security
- Fixed authentication bypass in `endpoint`
```

---

## Version Comparison

| Feature | v1 |
|---------|-----|
| Authentication | OAuth 2.0 / OIDC |
| Multi-tenancy | Yes (RLS) |
| Rate Limiting | Yes (Redis) |
| Pagination | Offset-based |

---

## Migration Guides

- [Migrating from v0 to v1](./migrations/v0-to-v1.md) (if applicable)
```

### 3. Migration Guide Template (`docs/api-migration-guide-template.md`)

```markdown
# API Migration Guide: v{OLD} to v{NEW}

This guide helps you migrate from API v{OLD} to v{NEW}.

**Migration Timeline:**
- v{NEW} Released: YYYY-MM-DD
- v{OLD} Deprecated: YYYY-MM-DD
- v{OLD} End of Life: YYYY-MM-DD

## Quick Start

1. Update your base URL:
   ```diff
   - https://api.example.com/api/v{OLD}/
   + https://api.example.com/api/v{NEW}/
   ```

2. Update affected endpoints (see below)

3. Test in staging environment

4. Deploy to production

## Breaking Changes Summary

| Change | v{OLD} | v{NEW} | Action Required |
|--------|--------|--------|-----------------|
| Example | `name` field | `full_name` field | Update field reference |

## Detailed Changes

### Endpoint: `/users`

#### GET /users/{id}

**Response Change:**

```diff
{
  "id": 1,
- "name": "John Doe",
+ "full_name": "John Doe",
+ "display_name": "John",
  "email": "john@example.com"
}
```

**Migration Steps:**
1. Update response parsing to use `full_name` instead of `name`
2. Optionally use new `display_name` field

**Code Example:**

```typescript
// Before (v{OLD})
const userName = response.name;

// After (v{NEW})
const userName = response.full_name;
const displayName = response.display_name;
```

### Endpoint: `/resources`

#### POST /resources

**Request Change:**

```diff
{
  "title": "My Resource",
- "type": "blog_post",
+ "resource_type": "blog_post",
+ "visibility": "public"  // New required field
}
```

**Migration Steps:**
1. Rename `type` to `resource_type` in request body
2. Add required `visibility` field (values: "public", "private", "team")

## New Features in v{NEW}

### New Endpoints

- `GET /api/v{NEW}/analytics` - Usage analytics
- `POST /api/v{NEW}/bulk-operations` - Batch processing

### New Fields

| Endpoint | New Field | Type | Description |
|----------|-----------|------|-------------|
| GET /users | `display_name` | string | Short display name |
| GET /resources | `visibility` | enum | Resource visibility |

## Compatibility Matrix

| Client SDK | v{OLD} Support | v{NEW} Support |
|------------|----------------|----------------|
| JavaScript | Yes | Yes (>= 2.0.0) |
| Python | Yes | Yes (>= 2.0.0) |
| Generated | Yes | Regenerate required |

## Testing Checklist

- [ ] All API calls updated to v{NEW} URLs
- [ ] Request bodies updated with new field names
- [ ] Response parsing updated for changed fields
- [ ] New required fields added to requests
- [ ] Error handling updated for new error codes
- [ ] Integration tests passing
- [ ] Staging deployment verified
- [ ] Production deployment completed
- [ ] Monitoring configured for new endpoints

## Rollback Plan

If issues occur after migration:

1. Revert API base URL to v{OLD}
2. Revert related code changes
3. v{OLD} remains functional until EOL date

## Support

- **Documentation**: https://docs.example.com/api/v{NEW}
- **Issues**: https://github.com/example/project/issues
- **Migration Help**: support@example.com

## FAQ

**Q: Can I use both versions simultaneously?**
A: Yes, during the migration period both versions are available. However, we recommend completing migration as soon as possible.

**Q: Will my API keys work with v{NEW}?**
A: Yes, authentication is version-independent.

**Q: What happens after the EOL date?**
A: v{OLD} endpoints will return 410 Gone status with a message directing to v{NEW}.
```

## Success Criteria

### Functional Requirements
- [ ] FR-DX-008: API versioning strategy documented
- [ ] FR-DX-009: API deprecation policy documented
- [ ] FR-DX-010: Breaking change criteria documented
- [ ] Versioning strategy document is comprehensive
- [ ] Changelog template is usable
- [ ] Migration guide template covers common scenarios

### Verification Steps
1. **Document Review:**
   - Versioning strategy clearly explains URL path approach
   - Breaking change criteria has concrete examples
   - Deprecation timeline is defined

2. **Template Validation:**
   - Changelog template follows Keep a Changelog format
   - Migration guide template is actionable
   - Examples are clear and correct

3. **Code Alignment:**
   ```bash
   # Verify API prefix in config matches documentation
   grep "API_V1_PREFIX" backend/app/core/config.py
   # Should match documented prefix
   ```

### Quality Gates
- [ ] Documents use clear, professional language
- [ ] Breaking change criteria is unambiguous
- [ ] Deprecation policy has concrete timelines
- [ ] Templates are ready for immediate use
- [ ] Examples match actual API structure
- [ ] Links to related docs are correct

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| None | - | Independent documentation task |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-01 | CLAUDE.md | References versioning docs |
| P6-02 | Migration guide | Uses migration template |

### Integration Contract
```yaml
# Contract: API Versioning Documentation

# Documentation files
docs/api-versioning.md        # Main strategy document
docs/api-changelog.md         # Version history
docs/api-migration-guide-template.md  # Migration template

# Key definitions
versioning_approach: url_path  # /api/v{N}/
version_format: "v{MAJOR}"     # v1, v2, etc.
support_period: 12_months      # After next major version
deprecation_notice: 6_months   # Before EOL

# Breaking change criteria
breaking_changes:
  - endpoint_removal
  - field_removal
  - field_rename
  - type_change
  - validation_tightening

non_breaking_changes:
  - endpoint_addition
  - optional_field_addition
  - field_addition_response
  - enum_value_addition
```

## Monitoring and Observability

### Documentation Metrics
- Track page views on versioning docs
- Monitor for outdated references
- Alert when changelog is stale

### API Version Usage
- Log API version in requests
- Track version adoption rates
- Alert on deprecated version usage

## Infrastructure Needs

No infrastructure requirements - pure documentation task.

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Documentation-only task
- Templates can be adapted from standards
- No code implementation required
- Clear requirements from FRD

## Notes

### Design Decisions

**1. URL Path Versioning:**
- Most visible and debuggable
- Aligns with industry practice (Stripe, GitHub)
- Easy to implement in FastAPI

**2. Major-Only Versioning:**
- Simpler than full SemVer in URLs
- Matches breaking change focus
- `/api/v1/` not `/api/v1.2.3/`

**3. 12-Month Support Window:**
- Reasonable for B2B SaaS
- Balances maintenance burden
- Industry standard timeframe

### Future Considerations

**Automated Changelog:**
- Could parse conventional commits
- Generate changelog from PR labels
- Tools: release-drafter, semantic-release

**Breaking Change Detection:**
- OpenAPI diff in CI
- Alert on breaking changes
- Tools: openapi-diff, oasdiff

### Related Requirements
- FR-DX-008: API versioning strategy documented
- FR-DX-009: API deprecation policy documented
- FR-DX-010: Breaking change criteria documented
- US-5.3: Clear API versioning guidelines
