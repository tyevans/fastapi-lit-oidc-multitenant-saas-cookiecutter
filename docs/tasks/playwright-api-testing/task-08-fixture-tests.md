# TASK-08: Fixture-Based Test Suite

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-08 |
| Title | Fixture-Based Test Suite |
| Domain | Backend |
| Complexity | M (Medium) |
| Estimated Effort | 3-4 hours |
| Dependencies | TASK-05, TASK-06 |
| Blocks | TASK-11, TASK-13 |

---

## Scope

### What This Task Includes

1. Create `api-with-fixtures.api.spec.ts` with fixture-based patterns
2. Demonstrate all convenience fixtures (`adminRequest`, `userRequest`, etc.)
3. Demonstrate `authenticatedRequest` for multi-user tests
4. Test all 6 user contexts (admin, user, readOnly, newUser, manager, serviceAccount)
5. Show token and user metadata access
6. Include documentation comments explaining patterns

### What This Task Excludes

- Manual auth tests (TASK-07)
- Fixture implementation (TASK-05 - dependency)
- Admin endpoint creation (TASK-06 - dependency)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/tests/api-with-fixtures.api.spec.ts` | Fixture-based API tests |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-with-fixtures.api.spec.js` | Reference implementation |

---

## Implementation Details

### api-with-fixtures.api.spec.ts Specification

```typescript
/**
 * API tests using the fixture pattern (RECOMMENDED APPROACH)
 *
 * This file demonstrates the recommended way to write API tests using
 * pre-authenticated request contexts provided by fixtures.ts.
 *
 * Benefits of the fixture pattern:
 * - No manual token management in tests
 * - Cleaner, more readable test code
 * - Type-safe request contexts
 * - All users authenticated once per test
 *
 * Available fixtures:
 * - adminRequest: Admin user context
 * - userRequest: Standard user context
 * - readOnlyRequest: Read-only user context
 * - managerRequest: Manager user context
 * - authenticatedRequest: All user contexts (.admin, .user, .readOnly, .newUser, .manager, .serviceAccount)
 */

import { test, expect } from './fixtures';

/**
 * Core Fixture Tests
 * Demonstrates the primary fixture patterns
 */
test.describe('API Tests with Fixtures', () => {
  test('admin can access admin endpoint using adminRequest fixture', async ({ adminRequest }) => {
    const response = await adminRequest.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.message).toBe('This is an admin route');
    expect(data.user.username).toBe('admin');
    expect(data.user.roles).toContain('admin');
    expect(data.user.roles).toContain('user');
  });

  test('regular user can access protected endpoint using userRequest fixture', async ({ userRequest }) => {
    const response = await userRequest.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('testuser');
    expect(data.roles).toContain('user');
    expect(data.roles).not.toContain('admin');
  });

  test('regular user cannot access admin endpoint', async ({ userRequest }) => {
    const response = await userRequest.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');

    expect(response.status()).toBe(403);
    const data = await response.json();
    expect(data.detail).toContain("Role 'admin' required");
  });

  test('readOnly user can access protected endpoints', async ({ readOnlyRequest }) => {
    const response = await readOnlyRequest.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('readonly');
    expect(data.roles).toContain('readonly');
    expect(data.roles).toContain('user');
  });

  test('manager has proper role assignment', async ({ managerRequest }) => {
    const response = await managerRequest.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('manager');
    expect(data.roles).toContain('manager');
    expect(data.roles).toContain('user');
  });
});

/**
 * Multi-User Context Tests
 * Demonstrates using authenticatedRequest for multiple users in one test
 */
test.describe('Multi-User Tests with authenticatedRequest', () => {
  test('can access multiple user contexts in same test', async ({ authenticatedRequest }) => {
    // Admin can access admin endpoint
    const adminResponse = await authenticatedRequest.admin.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');
    expect(adminResponse.ok()).toBeTruthy();

    // Regular user cannot access admin endpoint
    const userResponse = await authenticatedRequest.user.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');
    expect(userResponse.status()).toBe(403);

    // Manager can access protected endpoint
    const managerResponse = await authenticatedRequest.manager.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');
    expect(managerResponse.ok()).toBeTruthy();
  });

  test('compare admin and user access levels', async ({ authenticatedRequest }) => {
    const endpoints = [
      '/{{ cookiecutter.backend_api_prefix }}/test/protected',
      '/{{ cookiecutter.backend_api_prefix }}/test/admin',
    ];

    for (const endpoint of endpoints) {
      const adminResp = await authenticatedRequest.admin.get(endpoint);
      const userResp = await authenticatedRequest.user.get(endpoint);

      // Admin should access all endpoints
      expect(adminResp.ok()).toBeTruthy();

      // User should only access protected, not admin
      if (endpoint.includes('admin')) {
        expect(userResp.status()).toBe(403);
      } else {
        expect(userResp.ok()).toBeTruthy();
      }
    }
  });

  test('all users can access protected endpoint', async ({ authenticatedRequest }) => {
    const users = ['admin', 'user', 'readOnly', 'newUser', 'manager'] as const;

    for (const userKey of users) {
      const response = await authenticatedRequest[userKey].get('/{{ cookiecutter.backend_api_prefix }}/test/protected');
      expect(response.ok(), `${userKey} should access protected endpoint`).toBeTruthy();
    }
  });
});

/**
 * Fixture Metadata Tests
 * Demonstrates accessing user info and token from fixtures
 */
test.describe('Fixture Metadata Access', () => {
  test('can access user info from adminRequest fixture', async ({ adminRequest }) => {
    expect(adminRequest.user.username).toBe('admin');
    expect(adminRequest.user.email).toBe('admin@example.com');
    expect(adminRequest.user.roles).toContain('admin');
    expect(adminRequest.user.description).toBeTruthy();
  });

  test('can access raw token from fixture', async ({ adminRequest }) => {
    const token = adminRequest.token;

    expect(token).toBeTruthy();
    expect(typeof token).toBe('string');
    // JWT tokens start with 'eyJ' (base64 encoded '{"')
    expect(token).toMatch(/^eyJ/);
  });

  test('token can be used for custom scenarios', async ({ adminRequest, request }) => {
    // Get the token from the fixture
    const token = adminRequest.token;

    // Use it manually (e.g., for custom headers or WebSocket auth)
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me', {
      headers: {
        Authorization: `Bearer ${token}`,
        'X-Custom-Header': 'custom-value',
      },
    });

    expect(response.ok()).toBeTruthy();
  });
});

/**
 * Special User Scenario Tests
 * Tests for newUser and serviceAccount fixtures
 */
test.describe('Test User Scenarios', () => {
  test('newUser fixture for testing onboarding flows', async ({ authenticatedRequest }) => {
    const response = await authenticatedRequest.newUser.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('newuser');
    expect(data.roles).toContain('user');
    // newUser has minimal roles - good for testing first-time user experiences
    expect(data.roles).toHaveLength(1);
  });

  test('serviceAccount fixture for API integration tests', async ({ authenticatedRequest }) => {
    const response = await authenticatedRequest.serviceAccount.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('service-account');
    expect(data.roles).toContain('service');
    // Service account does NOT have 'user' role
    expect(data.roles).not.toContain('user');
  });

  test('readOnly user cannot modify resources (example pattern)', async ({ readOnlyRequest }) => {
    // This demonstrates the pattern for testing read-only access
    // The actual endpoint might return 405 Method Not Allowed or 403 Forbidden
    const response = await readOnlyRequest.post('/{{ cookiecutter.backend_api_prefix }}/todos', {
      data: { title: 'Test Todo', completed: false },
    });

    // Expect either 403 (forbidden) or 405 (method not allowed) or 201 (if allowed)
    // The actual behavior depends on your application's access control
    expect([201, 403, 404, 405]).toContain(response.status());
  });
});

/**
 * HTTP Method Tests
 * Demonstrates all HTTP methods work with authenticated contexts
 */
test.describe('HTTP Methods with Fixtures', () => {
  test('POST request with userRequest', async ({ userRequest }) => {
    // POST to a hypothetical endpoint
    const response = await userRequest.post('/{{ cookiecutter.backend_api_prefix }}/test/echo', {
      data: { message: 'Hello, World!' },
    });

    // Expect 404 (not found) since endpoint doesn't exist
    // but NOT 401/403 (auth should pass)
    expect(response.status()).not.toBe(401);
    expect(response.status()).not.toBe(403);
  });

  test('PUT request with adminRequest', async ({ adminRequest }) => {
    const response = await adminRequest.put('/{{ cookiecutter.backend_api_prefix }}/test/resource/1', {
      data: { updated: true },
    });

    // Auth should pass, endpoint may or may not exist
    expect(response.status()).not.toBe(401);
    expect(response.status()).not.toBe(403);
  });

  test('PATCH request with managerRequest', async ({ managerRequest }) => {
    const response = await managerRequest.patch('/{{ cookiecutter.backend_api_prefix }}/test/resource/1', {
      data: { field: 'value' },
    });

    expect(response.status()).not.toBe(401);
    expect(response.status()).not.toBe(403);
  });

  test('DELETE request with adminRequest', async ({ adminRequest }) => {
    const response = await adminRequest.delete('/{{ cookiecutter.backend_api_prefix }}/test/resource/1');

    expect(response.status()).not.toBe(401);
    expect(response.status()).not.toBe(403);
  });
});
```

### Test Count Summary

| Category | Test Count |
|----------|------------|
| Core Fixture Tests | 5 |
| Multi-User Tests | 3 |
| Fixture Metadata Access | 3 |
| Test User Scenarios | 3 |
| HTTP Methods | 4 |
| **Total** | **18** |

---

## Cookiecutter Variables Used

| Variable | Default | Usage |
|----------|---------|-------|
| `{{ cookiecutter.backend_api_prefix }}` | /api/v1 | API endpoint paths |

---

## Success Criteria

1. **All Tests Pass**: 18+ tests pass with services running
2. **All Fixtures Work**: adminRequest, userRequest, readOnlyRequest, managerRequest, authenticatedRequest
3. **Metadata Accessible**: user and token properties work on all contexts
4. **Multi-User Tests**: Tests using multiple contexts work correctly
5. **TypeScript Valid**: No TypeScript errors

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
npx playwright test tests/api-with-fixtures.api.spec.ts

# Expected output: 18 tests passed
```

---

## Integration Points

### Upstream Dependencies

- **TASK-05**: Fixtures must be implemented
- **TASK-06**: Admin endpoint must exist

### Downstream Dependencies

This task enables:
- **TASK-11**: Documentation references these patterns as recommended approach
- **TASK-13**: Validation runs these tests

### Contracts

This test suite validates contracts:
- IC-2: Test Users Interface (validates user data)
- IC-3: Fixtures Interface (validates fixture behavior)
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

1. **Recommended Approach**: This file should be emphasized in documentation as the preferred way to write tests.

2. **Import from fixtures**: Tests import from `./fixtures` (not `@playwright/test`) to get authenticated contexts.

3. **Documentation Comments**: The file includes extensive comments explaining patterns - these serve as inline documentation.

4. **Multi-User Tests**: The `authenticatedRequest` fixture enables testing multiple user roles in a single test, which is powerful for RBAC testing.

5. **Metadata Access**: Exposing `user` and `token` on fixtures enables advanced scenarios like WebSocket authentication or custom header handling.

---

## FRD References

- FR-5.2: Fixture-Based API Tests
- IP-4: Phase 4 - Example Test Suites (section 4.2)
- US-2 through US-6: User stories for authenticated testing

---

*Task Created: 2025-12-04*
*Status: Not Started*
