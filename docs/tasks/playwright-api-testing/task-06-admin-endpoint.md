# TASK-06: Admin Endpoint Creation

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-06 |
| Title | Admin Endpoint Creation |
| Domain | Backend |
| Complexity | S (Small) |
| Estimated Effort | 2-3 hours |
| Dependencies | None |
| Blocks | TASK-07, TASK-08 |

---

## Scope

### What This Task Includes

1. Add admin-only test endpoint `/api/v1/test/admin` to the template backend
2. Implement role-based access control requiring `admin` role
3. Return user information in response (username, roles, tenant_id)
4. Add appropriate error response for non-admin users (403 Forbidden)

### What This Task Excludes

- Playwright test files (TASK-07, TASK-08)
- Keycloak role creation (already exists via TASK-09)
- Frontend changes

---

## Relevant Code Areas

### Files to Modify

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py` | Add admin endpoint to existing test auth router |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py` | Existing protected endpoint pattern |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/dependencies/auth.py` | CurrentUser dependency pattern |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/dependencies/scopes.py` | Scope/role checking patterns |

---

## Implementation Details

### Current test_auth.py Structure

The existing file has a `/test/protected` endpoint. We need to add an admin-only endpoint.

### Admin Endpoint Implementation

Add to `template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from app.api.dependencies.auth import CurrentUser


router = APIRouter(prefix="/test", tags=["test"])


class TestUserInfo(BaseModel):
    """User information returned in test responses"""
    username: str
    roles: List[str]
    tenant_id: str


class TestAuthResponse(BaseModel):
    """Response model for test auth endpoints"""
    message: str
    user: TestUserInfo


def require_admin(user: CurrentUser) -> CurrentUser:
    """
    Dependency that requires the user to have the 'admin' role.
    Raises 403 Forbidden if the user lacks the admin role.
    """
    if "admin" not in user.roles:
        raise HTTPException(
            status_code=403,
            detail="Role 'admin' required. User roles: " + ", ".join(user.roles)
        )
    return user


@router.get(
    "/protected",
    response_model=TestAuthResponse,
    summary="Protected test endpoint",
    description="Requires any authenticated user. Used for testing authentication.",
)
async def protected_endpoint(user: CurrentUser) -> TestAuthResponse:
    """Protected endpoint accessible to any authenticated user."""
    return TestAuthResponse(
        message="This is a protected route",
        user=TestUserInfo(
            username=user.username,
            roles=user.roles,
            tenant_id=user.tenant_id,
        ),
    )


@router.get(
    "/admin",
    response_model=TestAuthResponse,
    summary="Admin-only test endpoint",
    description="Requires 'admin' role. Used for testing role-based access control.",
)
async def admin_endpoint(user: CurrentUser = Depends(require_admin)) -> TestAuthResponse:
    """
    Admin-only endpoint for testing RBAC.

    Returns 403 Forbidden if the authenticated user does not have the 'admin' role.
    """
    return TestAuthResponse(
        message="This is an admin route",
        user=TestUserInfo(
            username=user.username,
            roles=user.roles,
            tenant_id=user.tenant_id,
        ),
    )
```

### Response Examples

**Success Response (200 OK):**
```json
{
  "message": "This is an admin route",
  "user": {
    "username": "admin",
    "roles": ["user", "admin"],
    "tenant_id": "tenant-1"
  }
}
```

**Forbidden Response (403):**
```json
{
  "detail": "Role 'admin' required. User roles: user"
}
```

**Unauthorized Response (401/403):**
```json
{
  "detail": "Not authenticated"
}
```

---

## Success Criteria

1. **Endpoint Available**: GET `/api/v1/test/admin` is accessible
2. **Admin Access**: Users with `admin` role receive 200 response
3. **Non-Admin Denied**: Users without `admin` role receive 403 response
4. **Unauthenticated Denied**: Requests without token receive 401/403 response
5. **Response Format**: Response includes message and user info with roles

---

## Verification Steps

```bash
# After Keycloak and backend are running

# 1. Get admin token
ADMIN_TOKEN=$(curl -s -X POST \
  "http://localhost:8080/realms/PROJECT_REALM/protocol/openid-connect/token" \
  -d "client_id=backend-api" \
  -d "client_secret=backend-api-secret" \
  -d "username=admin" \
  -d "password=admin123" \
  -d "grant_type=password" | jq -r '.access_token')

# 2. Test admin access (should return 200)
curl -s -X GET "http://localhost:8000/api/v1/test/admin" \
  -H "Authorization: Bearer $ADMIN_TOKEN" | jq

# 3. Get user token
USER_TOKEN=$(curl -s -X POST \
  "http://localhost:8080/realms/PROJECT_REALM/protocol/openid-connect/token" \
  -d "client_id=backend-api" \
  -d "client_secret=backend-api-secret" \
  -d "username=testuser" \
  -d "password=test123" \
  -d "grant_type=password" | jq -r '.access_token')

# 4. Test non-admin access (should return 403)
curl -s -X GET "http://localhost:8000/api/v1/test/admin" \
  -H "Authorization: Bearer $USER_TOKEN" | jq

# 5. Test unauthenticated access (should return 401 or 403)
curl -s -X GET "http://localhost:8000/api/v1/test/admin" | jq
```

---

## Integration Points

### Upstream Dependencies

None - this task can be executed independently.

### Downstream Dependencies

This task enables:
- **TASK-07**: Basic tests need admin endpoint for RBAC testing
- **TASK-08**: Fixture tests need admin endpoint for RBAC testing

### Contracts

**Interface Contract (IC-4):**

Request:
```
GET /api/v1/test/admin
Authorization: Bearer <JWT with admin role>
```

Response (200 OK):
```json
{
  "message": "This is an admin route",
  "user": {
    "username": "string",
    "roles": ["user", "admin"],
    "tenant_id": "string"
  }
}
```

Response (403 Forbidden):
```json
{
  "detail": "Role 'admin' required. User roles: <user_roles>"
}
```

---

## Monitoring and Observability

The endpoint integrates with existing backend observability:
- Request logging via FastAPI middleware
- Prometheus metrics for request count/latency
- OpenTelemetry tracing (if enabled)

---

## Infrastructure Needs

None - uses existing backend infrastructure.

---

## Notes

1. **Gap Identification**: The FRD identified that the template lacks an admin-only endpoint. This task addresses that gap to enable comprehensive RBAC testing.

2. **Error Message Format**: The 403 error message includes the user's actual roles to help with debugging.

3. **Dependency Injection**: Uses FastAPI's `Depends()` pattern for the `require_admin` check, which is consistent with the existing codebase.

4. **Response Model Reuse**: Uses the same `TestAuthResponse` model as the existing `/protected` endpoint for consistency.

5. **Alternative Approach**: Could use the existing `require_scopes` dependency, but a custom `require_admin` is clearer for role-based checks.

---

## FRD References

- AI-5: API Contract Alignment (Gap Identified section)
- FR-5.1: Basic API Tests (Admin-Only API Endpoints tests)
- FR-5.2: Fixture-Based API Tests (admin access tests)
- TA-7: API Endpoint Compatibility

---

*Task Created: 2025-12-04*
*Status: Not Started*
