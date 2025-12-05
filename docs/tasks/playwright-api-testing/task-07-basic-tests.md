# TASK-07: Basic API Test Suite (Manual Auth)

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-07 |
| Title | Basic API Test Suite (Manual Auth) |
| Domain | Backend |
| Complexity | M (Medium) |
| Estimated Effort | 3-4 hours |
| Dependencies | TASK-03, TASK-06 |
| Blocks | TASK-11, TASK-13 |

---

## Scope

### What This Task Includes

1. Create `api-endpoints.api.spec.ts` with manual authentication patterns
2. Implement tests for public endpoints (root, health)
3. Implement tests for protected endpoints with and without auth
4. Implement tests for admin-only endpoints with role checking
5. Implement tests for token validation (invalid tokens, malformed JWTs)
6. Demonstrate manual token retrieval pattern

### What This Task Excludes

- Fixture-based tests (TASK-08)
- Auth helper implementation (TASK-03 - dependency)
- Admin endpoint creation (TASK-06 - dependency)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/tests/api-endpoints.api.spec.ts` | Basic API tests with manual authentication |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-endpoints.api.spec.js` | Reference implementation |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/routers/health.py` | Health endpoint response format |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py` | Protected/admin endpoint responses |

---

## Implementation Details

### api-endpoints.api.spec.ts Specification

```typescript
/**
 * Basic API endpoint tests using manual authentication
 *
 * This file demonstrates the manual authentication pattern where tokens
 * are retrieved explicitly using auth-helper functions. This pattern is
 * useful for:
 * - Custom authentication scenarios
 * - Testing invalid tokens
 * - Understanding the authentication flow
 *
 * For most tests, prefer the fixture pattern in api-with-fixtures.api.spec.ts
 */

import { test, expect } from '@playwright/test';
import { getAdminToken, getTestUserToken, authHeader } from './auth-helper';

/**
 * Public API Endpoints
 * These endpoints do not require authentication
 */
test.describe('Public API Endpoints', () => {
  test('GET / should return service info', async ({ request }) => {
    const response = await request.get('/');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('message');
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/health should return healthy status', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/health');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/health/ready should return ready status', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/health/ready');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('status');
  });
});

/**
 * Protected API Endpoints
 * These endpoints require a valid JWT token but no specific role
 */
test.describe('Protected API Endpoints', () => {
  test('GET /{{ cookiecutter.backend_api_prefix }}/auth/me should fail without token', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

    // Backend returns 401 or 403 for unauthenticated requests
    expect([401, 403]).toContain(response.status());
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/auth/me should succeed with admin token', async ({ request }) => {
    const token = await getAdminToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me', {
      headers: authHeader(token),
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('username', 'admin');
    expect(data.roles).toContain('admin');
    expect(data.roles).toContain('user');
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/auth/me should succeed with user token', async ({ request }) => {
    const token = await getTestUserToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me', {
      headers: authHeader(token),
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('username', 'testuser');
    expect(data.roles).toContain('user');
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/test/protected should fail without token', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/protected');

    expect([401, 403]).toContain(response.status());
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/test/protected should succeed with valid token', async ({ request }) => {
    const token = await getTestUserToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/protected', {
      headers: authHeader(token),
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('message', 'This is a protected route');
    expect(data.user).toHaveProperty('username', 'testuser');
  });
});

/**
 * Admin-Only API Endpoints
 * These endpoints require the 'admin' role
 */
test.describe('Admin-Only API Endpoints', () => {
  test('GET /{{ cookiecutter.backend_api_prefix }}/test/admin should fail without token', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');

    expect([401, 403]).toContain(response.status());
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/test/admin should succeed with admin token', async ({ request }) => {
    const token = await getAdminToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/admin', {
      headers: authHeader(token),
    });

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('message', 'This is an admin route');
    expect(data.user).toHaveProperty('username', 'admin');
    expect(data.user.roles).toContain('admin');
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/test/admin should fail with regular user token', async ({ request }) => {
    const token = await getTestUserToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/admin', {
      headers: authHeader(token),
    });

    expect(response.status()).toBe(403);
    const data = await response.json();
    expect(data).toHaveProperty('detail');
    expect(data.detail).toContain("Role 'admin' required");
  });
});

/**
 * Token Validation
 * Tests for invalid, malformed, and expired tokens
 */
test.describe('Token Validation', () => {
  test('should reject request with invalid token format', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/protected', {
      headers: authHeader('invalid.token.here'),
    });

    expect(response.status()).toBe(401);
    const data = await response.json();
    expect(data).toHaveProperty('detail');
  });

  test('should reject request with malformed JWT', async ({ request }) => {
    // This is a structurally valid JWT but with invalid signature
    const fakeToken =
      'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.' +
      'eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.' +
      'POstGetfAytaZS82wHcjoTyoqhMyxXiWdR7Nn7A28cN';

    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/protected', {
      headers: authHeader(fakeToken),
    });

    expect(response.status()).toBe(401);
  });

  test('should reject request with empty Authorization header', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/protected', {
      headers: { Authorization: '' },
    });

    expect([401, 403]).toContain(response.status());
  });

  test('should reject request with invalid Authorization scheme', async ({ request }) => {
    const token = await getAdminToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/test/protected', {
      headers: { Authorization: `Basic ${token}` }, // Wrong scheme
    });

    expect([401, 403]).toContain(response.status());
  });
});

/**
 * HTTP Methods
 * Verify different HTTP methods work with authentication
 */
test.describe('HTTP Methods with Authentication', () => {
  test('POST request with authentication should work', async ({ request }) => {
    const token = await getTestUserToken(request);
    // POST to a hypothetical endpoint - will likely 404 but tests auth works
    const response = await request.post('/{{ cookiecutter.backend_api_prefix }}/test/echo', {
      headers: authHeader(token),
      data: { test: 'data' },
    });

    // We expect 404 (endpoint doesn't exist) or 405 (method not allowed)
    // but NOT 401/403 (auth should pass)
    if (response.status() === 401 || response.status() === 403) {
      // If we get auth error, something is wrong
      expect(response.status()).not.toBe(401);
      expect(response.status()).not.toBe(403);
    }
  });
});
```

### Test Count Summary

| Category | Test Count |
|----------|------------|
| Public API Endpoints | 3 |
| Protected API Endpoints | 5 |
| Admin-Only API Endpoints | 3 |
| Token Validation | 4 |
| HTTP Methods | 1 |
| **Total** | **16** |

---

## Cookiecutter Variables Used

| Variable | Default | Usage |
|----------|---------|-------|
| `{{ cookiecutter.backend_api_prefix }}` | /api/v1 | API endpoint paths |

---

## Success Criteria

1. **All Tests Pass**: 16+ tests pass with services running
2. **Public Endpoints**: Health and root endpoints work without auth
3. **Protected Endpoints**: Auth required, any role accepted
4. **Admin Endpoints**: Only admin role accepted, 403 for others
5. **Token Validation**: Invalid tokens properly rejected
6. **TypeScript Valid**: No TypeScript errors

---

## Verification Steps

```bash
# Start services
docker compose up -d

# Wait for Keycloak
./keycloak/wait-for-keycloak.sh

# Setup realm with test users
./keycloak/setup-realm.sh

# Run tests
cd playwright
npm install
npx playwright test tests/api-endpoints.api.spec.ts

# Expected output: 16 tests passed
```

---

## Integration Points

### Upstream Dependencies

- **TASK-03**: Auth helper functions must be implemented
- **TASK-06**: Admin endpoint must exist for RBAC tests

### Downstream Dependencies

This task enables:
- **TASK-11**: Documentation references these test patterns
- **TASK-13**: Validation runs these tests

### Contracts

This test suite validates contracts:
- IC-1: Auth Helper Interface (uses `getAdminToken`, `getTestUserToken`, `authHeader`)
- IC-4: Admin Endpoint Response (validates response format)

---

## Monitoring and Observability

Test execution produces:
- HTML report in `playwright-report/`
- Console output with test results
- Trace files on failure (for debugging)

---

## Infrastructure Needs

For test execution:
- Running Keycloak with configured realm
- Running backend API
- Test users created in Keycloak (TASK-09)

---

## Notes

1. **Manual Auth Pattern**: This file demonstrates explicit token management. It's more verbose than fixtures but useful for understanding the auth flow.

2. **Flexible Status Codes**: Tests use `[401, 403].toContain()` because backends may return either for unauthenticated requests.

3. **Cookie Variable Syntax**: The `{{ cookiecutter.backend_api_prefix }}` syntax will be replaced during project generation.

4. **HTTP Methods Test**: The POST test intentionally hits a non-existent endpoint to verify auth passes before the 404.

5. **Parallel Execution**: Tests can run in parallel since each fetches its own token.

---

## FRD References

- FR-5.1: Basic API Tests
- IP-4: Phase 4 - Example Test Suites (section 4.1)
- TA-7: API Endpoint Compatibility

---

*Task Created: 2025-12-04*
*Status: Not Started*
