# TASK-05: Fixture System Implementation

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-05 |
| Title | Fixture System Implementation |
| Domain | Backend |
| Complexity | M (Medium) |
| Estimated Effort | 3-4 hours |
| Dependencies | TASK-03, TASK-04 |
| Blocks | TASK-08 |

---

## Scope

### What This Task Includes

1. Create `fixtures.ts` extending Playwright's base test
2. Implement `authenticatedRequest` fixture with all 6 user contexts
3. Implement convenience fixtures (`adminRequest`, `userRequest`, etc.)
4. Create type-safe wrapper for authenticated HTTP methods
5. Expose `user` and `token` properties on each context
6. Implement proper error handling for fixture initialization

### What This Task Excludes

- Auth helper implementation (TASK-03)
- Test user definitions (TASK-04)
- Actual test files (TASK-08)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/tests/fixtures.ts` | Extended Playwright test fixtures |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/fixtures.js` | Reference implementation (JavaScript) |
| `@playwright/test` type definitions | TypeScript type guidance |

---

## Implementation Details

### fixtures.ts Specification

```typescript
/**
 * Extended Playwright fixtures with authenticated request contexts
 *
 * This module provides pre-authenticated request contexts for all test users,
 * eliminating the need for manual token management in test files.
 *
 * Usage:
 *   import { test, expect } from './fixtures';
 *
 *   test('admin can access admin endpoint', async ({ adminRequest }) => {
 *     const response = await adminRequest.get('/admin');
 *     expect(response.ok()).toBeTruthy();
 *   });
 *
 *   test('compare user access levels', async ({ authenticatedRequest }) => {
 *     const adminResp = await authenticatedRequest.admin.get('/admin');
 *     const userResp = await authenticatedRequest.user.get('/admin');
 *     expect(adminResp.ok()).toBeTruthy();
 *     expect(userResp.status()).toBe(403);
 *   });
 */

import { test as base, expect, APIRequestContext, APIResponse } from '@playwright/test';
import { getAccessToken, authHeader } from './auth-helper';
import { TEST_USERS, TestUser } from './test-users';

/**
 * Authenticated HTTP request context for a specific user
 */
export interface AuthenticatedContext {
  /** HTTP GET with automatic auth header */
  get(url: string, options?: RequestOptions): Promise<APIResponse>;

  /** HTTP POST with automatic auth header */
  post(url: string, options?: RequestOptions): Promise<APIResponse>;

  /** HTTP PUT with automatic auth header */
  put(url: string, options?: RequestOptions): Promise<APIResponse>;

  /** HTTP PATCH with automatic auth header */
  patch(url: string, options?: RequestOptions): Promise<APIResponse>;

  /** HTTP DELETE with automatic auth header */
  delete(url: string, options?: RequestOptions): Promise<APIResponse>;

  /** The TestUser object for this context */
  user: TestUser;

  /** Raw JWT access token */
  token: string;
}

/**
 * Request options that can be passed to HTTP methods
 */
interface RequestOptions {
  headers?: Record<string, string>;
  data?: unknown;
  form?: Record<string, string>;
  params?: Record<string, string>;
  timeout?: number;
  failOnStatusCode?: boolean;
}

/**
 * Collection of authenticated contexts for all test users
 */
export type AuthenticatedRequestCollection = {
  [K in keyof typeof TEST_USERS]: AuthenticatedContext;
};

/**
 * Create an authenticated request wrapper for a user
 *
 * @param request - Playwright's raw request context
 * @param token - JWT access token
 * @param user - TestUser object
 * @returns AuthenticatedContext with all HTTP methods
 */
function createAuthenticatedContext(
  request: APIRequestContext,
  token: string,
  user: TestUser
): AuthenticatedContext {
  const makeRequest =
    (method: 'get' | 'post' | 'put' | 'patch' | 'delete') =>
    (url: string, options: RequestOptions = {}): Promise<APIResponse> => {
      return request[method](url, {
        ...options,
        headers: {
          ...authHeader(token),
          ...options.headers,
        },
      });
    };

  return {
    get: makeRequest('get'),
    post: makeRequest('post'),
    put: makeRequest('put'),
    patch: makeRequest('patch'),
    delete: makeRequest('delete'),
    user,
    token,
  };
}

/**
 * Extended test fixtures with authenticated request contexts
 */
export const test = base.extend<{
  /** All authenticated request contexts */
  authenticatedRequest: AuthenticatedRequestCollection;

  /** Admin user request context */
  adminRequest: AuthenticatedContext;

  /** Standard user request context */
  userRequest: AuthenticatedContext;

  /** Read-only user request context */
  readOnlyRequest: AuthenticatedContext;

  /** Manager user request context */
  managerRequest: AuthenticatedContext;
}>({
  /**
   * Provides authenticated request contexts for all test users
   *
   * Each context includes get, post, put, patch, delete methods
   * that automatically include the Authorization header.
   */
  authenticatedRequest: async ({ request }, use) => {
    const contexts: Record<string, AuthenticatedContext> = {};

    // Authenticate all users in parallel for better performance
    const entries = Object.entries(TEST_USERS);
    const results = await Promise.allSettled(
      entries.map(async ([key, user]) => {
        const token = await getAccessToken(request, user.username, user.password);
        return { key, token, user };
      })
    );

    // Process results and handle any failures
    const failures: string[] = [];
    for (const result of results) {
      if (result.status === 'fulfilled') {
        const { key, token, user } = result.value;
        contexts[key] = createAuthenticatedContext(request, token, user);
      } else {
        failures.push(result.reason.message);
      }
    }

    // If any authentication failed, provide actionable error
    if (failures.length > 0) {
      throw new Error(
        `Failed to authenticate test users:\n${failures.join('\n')}\n\n` +
          `Ensure Keycloak is running and the realm is configured:\n` +
          `  1. Start services: docker compose up -d\n` +
          `  2. Setup realm: ./keycloak/setup-realm.sh\n` +
          `  3. Retry tests: npm test`
      );
    }

    await use(contexts as AuthenticatedRequestCollection);
  },

  /**
   * Quick access to admin-authenticated request context
   */
  adminRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.admin);
  },

  /**
   * Quick access to standard user-authenticated request context
   */
  userRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.user);
  },

  /**
   * Quick access to read-only user-authenticated request context
   */
  readOnlyRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.readOnly);
  },

  /**
   * Quick access to manager-authenticated request context
   */
  managerRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.manager);
  },
});

// Re-export expect for convenience
export { expect };
```

### Key Design Decisions

1. **Parallel Token Retrieval**: Uses `Promise.allSettled` to fetch all tokens in parallel, improving fixture initialization time.

2. **Type Safety**: Full TypeScript types for:
   - `AuthenticatedContext` interface
   - Request options
   - Fixture type definitions

3. **Error Aggregation**: Collects all authentication failures and reports them together with actionable instructions.

4. **Header Merging**: User-provided headers override auth headers when needed.

5. **Convenience Fixtures**: Top-level fixtures (`adminRequest`, etc.) depend on `authenticatedRequest` to avoid duplicate token fetching.

---

## Success Criteria

1. **All Fixtures Available**: `adminRequest`, `userRequest`, `readOnlyRequest`, `managerRequest`, `authenticatedRequest`
2. **HTTP Methods Work**: `get`, `post`, `put`, `patch`, `delete` all include auth headers
3. **User/Token Exposed**: `context.user` and `context.token` are accessible
4. **Parallel Execution**: Token retrieval happens in parallel
5. **Error Messages Actionable**: Authentication failures provide clear instructions
6. **TypeScript Valid**: No TypeScript errors

---

## Verification Steps

```typescript
// tests/verify-fixtures.ts
import { test, expect } from './fixtures';

test('adminRequest fixture is available', async ({ adminRequest }) => {
  expect(adminRequest.user.username).toBe('admin');
  expect(adminRequest.token).toBeTruthy();
});

test('userRequest fixture is available', async ({ userRequest }) => {
  expect(userRequest.user.username).toBe('testuser');
});

test('authenticatedRequest has all users', async ({ authenticatedRequest }) => {
  expect(authenticatedRequest.admin).toBeDefined();
  expect(authenticatedRequest.user).toBeDefined();
  expect(authenticatedRequest.readOnly).toBeDefined();
  expect(authenticatedRequest.newUser).toBeDefined();
  expect(authenticatedRequest.manager).toBeDefined();
  expect(authenticatedRequest.serviceAccount).toBeDefined();
});

test('can make authenticated GET request', async ({ adminRequest }) => {
  // This will fail until backend is running, but validates fixture works
  const response = await adminRequest.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');
  // Just checking the fixture created the request correctly
  expect(response).toBeDefined();
});

test('can access token for custom scenarios', async ({ adminRequest }) => {
  const token = adminRequest.token;
  expect(token).toMatch(/^eyJ/); // JWT starts with eyJ
});
```

---

## Integration Points

### Upstream Dependencies

- **TASK-03**: `getAccessToken()` and `authHeader()` must be implemented
- **TASK-04**: `TEST_USERS` and `TestUser` must be defined

### Downstream Dependencies

This task enables:
- **TASK-08**: Fixture-based test suite

### Contracts

**Interface Contract (IC-3):**
```typescript
export interface AuthenticatedContext {
  get(url: string, options?: object): Promise<APIResponse>;
  post(url: string, options?: object): Promise<APIResponse>;
  put(url: string, options?: object): Promise<APIResponse>;
  patch(url: string, options?: object): Promise<APIResponse>;
  delete(url: string, options?: object): Promise<APIResponse>;
  user: TestUser;
  token: string;
}

export const test: typeof base & {
  authenticatedRequest: Record<string, AuthenticatedContext>;
  adminRequest: AuthenticatedContext;
  userRequest: AuthenticatedContext;
  readOnlyRequest: AuthenticatedContext;
  managerRequest: AuthenticatedContext;
};

export { expect };
```

**Fixture Availability Contract:**
Tests using these fixtures:
```typescript
test('example', async ({ adminRequest }) => { ... });
test('example', async ({ userRequest }) => { ... });
test('example', async ({ readOnlyRequest }) => { ... });
test('example', async ({ managerRequest }) => { ... });
test('example', async ({ authenticatedRequest }) => {
  // authenticatedRequest.admin
  // authenticatedRequest.user
  // authenticatedRequest.readOnly
  // authenticatedRequest.newUser
  // authenticatedRequest.manager
  // authenticatedRequest.serviceAccount
});
```

---

## Monitoring and Observability

### Logging

The fixture provides error messages that include:
- Which users failed to authenticate
- Step-by-step instructions for resolution

### Performance Considerations

- Parallel token retrieval reduces initialization time
- Each test still gets fresh tokens (no caching across tests)
- For large test suites, consider adding token caching

---

## Infrastructure Needs

None - this task only creates template files. However, verification requires:
- Running Keycloak instance
- Configured realm with test users (TASK-09)
- Running backend (for actual endpoint tests)

---

## Notes

1. **Re-export of expect**: The module re-exports `expect` from Playwright for convenience, so tests only need one import.

2. **No newUserRequest or serviceAccountRequest**: Only the most commonly used fixtures have convenience shortcuts. Access `newUser` and `serviceAccount` via `authenticatedRequest`.

3. **Type Assertion**: The `contexts as AuthenticatedRequestCollection` assertion is safe because we've verified all users authenticated successfully.

4. **Token Lifetime**: Tokens are valid for ~15 minutes (Keycloak default). Tests complete well within this window.

---

## FRD References

- FR-4.1: Fixtures File
- FR-4.2: authenticatedRequest Fixture
- FR-4.3: Convenience Request Fixtures
- FR-4.4: Module Exports
- FR-9.2: Fixture Initialization Failure
- IP-3: Phase 3 - Fixture System
- TA-3: Fixture Architecture
- AI-6: Fixture Architecture Deep Dive

---

*Task Created: 2025-12-04*
*Status: Not Started*
