# TASK-03: Authentication Helper Module

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-03 |
| Title | Authentication Helper Module |
| Domain | Backend |
| Complexity | M (Medium) |
| Estimated Effort | 3-4 hours |
| Dependencies | TASK-01 |
| Blocks | TASK-05, TASK-07 |

---

## Scope

### What This Task Includes

1. Create `auth-helper.ts` with OAuth 2.0 password grant token retrieval
2. Implement `getAccessToken()` function for any user
3. Implement convenience functions `getAdminToken()` and `getTestUserToken()`
4. Implement `authHeader()` helper for constructing Authorization headers
5. Export configuration constants (KEYCLOAK_URL, KEYCLOAK_REALM)
6. Design abstraction layer for future Token Exchange migration

### What This Task Excludes

- Test user definitions (TASK-04)
- Fixture system integration (TASK-05)
- Actual tests (TASK-07, TASK-08)
- Token Exchange implementation (future feature)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/tests/auth-helper.ts` | Keycloak authentication utilities |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/auth-helper.js` | Reference implementation (JavaScript) |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/services/oauth_client.py` | Backend OAuth client patterns |

---

## Implementation Details

### auth-helper.ts Specification

```typescript
/**
 * Authentication helper for Playwright API tests
 * Provides functions to obtain JWT tokens from Keycloak using OAuth 2.0 password grant
 *
 * Future Migration Path:
 * This module uses the password grant for simplicity. When migrating to Token Exchange:
 * 1. Replace getAccessToken() implementation with token exchange logic
 * 2. The interface (function signatures) remains unchanged
 * 3. Test code does not need to be modified
 */

import { APIRequestContext } from '@playwright/test';

// Configuration with environment variable overrides
export const KEYCLOAK_URL = process.env.KEYCLOAK_URL || 'http://localhost:{{ cookiecutter.keycloak_port }}';
export const KEYCLOAK_REALM = process.env.KEYCLOAK_REALM || '{{ cookiecutter.keycloak_realm_name }}';
const CLIENT_ID = '{{ cookiecutter.keycloak_backend_client_id }}';
const CLIENT_SECRET = '{{ cookiecutter.keycloak_backend_client_id }}-secret';

/**
 * Token response from Keycloak
 */
interface TokenResponse {
  access_token: string;
  expires_in: number;
  refresh_token?: string;
  token_type: string;
}

/**
 * Error response from Keycloak
 */
interface ErrorResponse {
  error: string;
  error_description?: string;
}

/**
 * Authentication strategy interface for future Token Exchange migration
 */
export interface AuthStrategy {
  getToken(request: APIRequestContext, username: string, password: string): Promise<string>;
}

/**
 * Password Grant authentication strategy (current implementation)
 */
class PasswordGrantStrategy implements AuthStrategy {
  async getToken(request: APIRequestContext, username: string, password: string): Promise<string> {
    const tokenUrl = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`;

    const response = await request.post(tokenUrl, {
      form: {
        username,
        password,
        grant_type: 'password',
        client_id: CLIENT_ID,
        client_secret: CLIENT_SECRET,
      },
    });

    if (!response.ok()) {
      const text = await response.text();
      let errorMessage = `Failed to get token for '${username}': ${response.status()}`;

      try {
        const errorData: ErrorResponse = JSON.parse(text);
        errorMessage += ` - ${errorData.error}: ${errorData.error_description || 'No description'}`;
      } catch {
        errorMessage += ` - ${text}`;
      }

      throw new Error(errorMessage);
    }

    const data: TokenResponse = await response.json();
    return data.access_token;
  }
}

// Default authentication strategy
const authStrategy: AuthStrategy = new PasswordGrantStrategy();

/**
 * Get an access token from Keycloak for a user
 *
 * @param request - Playwright APIRequestContext
 * @param username - Keycloak username
 * @param password - User password
 * @returns Promise resolving to JWT access token string
 * @throws Error if authentication fails
 *
 * @example
 * const token = await getAccessToken(request, 'admin', 'admin123');
 */
export async function getAccessToken(
  request: APIRequestContext,
  username: string,
  password: string
): Promise<string> {
  return authStrategy.getToken(request, username, password);
}

/**
 * Get token for admin user (convenience function)
 *
 * @param request - Playwright APIRequestContext
 * @returns Promise resolving to admin JWT access token
 */
export async function getAdminToken(request: APIRequestContext): Promise<string> {
  return getAccessToken(request, 'admin', 'admin123');
}

/**
 * Get token for standard test user (convenience function)
 *
 * @param request - Playwright APIRequestContext
 * @returns Promise resolving to test user JWT access token
 */
export async function getTestUserToken(request: APIRequestContext): Promise<string> {
  return getAccessToken(request, 'testuser', 'test123');
}

/**
 * Create Authorization header object with Bearer token
 *
 * @param token - JWT access token
 * @returns Object with Authorization header
 *
 * @example
 * const headers = authHeader(token);
 * await request.get('/protected', { headers });
 */
export function authHeader(token: string): { Authorization: string } {
  return {
    Authorization: `Bearer ${token}`,
  };
}
```

### Key Design Decisions

1. **Strategy Pattern**: The `AuthStrategy` interface allows swapping password grant for Token Exchange without changing the public API.

2. **Error Handling**: Comprehensive error messages include:
   - HTTP status code
   - Keycloak error code and description
   - Username for debugging

3. **TypeScript Types**: Full typing for:
   - Function parameters and return types
   - Keycloak response interfaces
   - Playwright's APIRequestContext

4. **Configuration Hierarchy**:
   - Environment variables override defaults
   - Cookiecutter variables provide defaults
   - Client credentials are hardcoded (match realm setup)

---

## Cookiecutter Variables Used

| Variable | Default | Usage |
|----------|---------|-------|
| `{{ cookiecutter.keycloak_port }}` | 8080 | Keycloak server port |
| `{{ cookiecutter.keycloak_realm_name }}` | project-dev | Realm name for token endpoint |
| `{{ cookiecutter.keycloak_backend_client_id }}` | backend-api | Client ID for OAuth |

---

## Success Criteria

1. **Token Retrieval**: `getAccessToken()` returns valid JWT from Keycloak
2. **Error Messages**: Authentication failures provide actionable error messages
3. **TypeScript Valid**: No TypeScript errors in the module
4. **Interface Compatibility**: Functions work with Playwright's APIRequestContext
5. **Environment Override**: Environment variables correctly override defaults

---

## Verification Steps

```bash
# After Keycloak is running with test users (TASK-09)

# Test token retrieval manually
cd test-project/playwright
npm install

# Create a simple test script
cat > tests/verify-auth.ts << 'EOF'
import { test, expect } from '@playwright/test';
import { getAccessToken, getAdminToken, authHeader } from './auth-helper';

test('can get admin token', async ({ request }) => {
  const token = await getAdminToken(request);
  expect(token).toBeTruthy();
  expect(typeof token).toBe('string');
  console.log('Token length:', token.length);
});

test('authHeader creates correct header', async ({ request }) => {
  const token = await getAdminToken(request);
  const header = authHeader(token);
  expect(header.Authorization).toMatch(/^Bearer .+/);
});
EOF

# Run verification
npx playwright test tests/verify-auth.ts
```

---

## Integration Points

### Upstream Dependencies

- **TASK-01**: Package.json and TypeScript setup must exist

### Downstream Dependencies

This task enables:
- **TASK-05**: Fixtures need auth helper for token retrieval
- **TASK-07**: Basic tests use auth helper directly

### Contracts

**Interface Contract (IC-1):**
```typescript
export async function getAccessToken(
  request: APIRequestContext,
  username: string,
  password: string
): Promise<string>;

export async function getAdminToken(request: APIRequestContext): Promise<string>;
export async function getTestUserToken(request: APIRequestContext): Promise<string>;
export function authHeader(token: string): { Authorization: string };

export const KEYCLOAK_URL: string;
export const KEYCLOAK_REALM: string;
```

**Error Contract:**
```typescript
// On authentication failure, throws Error with message format:
// "Failed to get token for '{username}': {status} - {error}: {error_description}"
```

---

## Monitoring and Observability

### Logging Recommendations

The module includes error messages that help diagnose:
- Invalid credentials (401 with `invalid_grant`)
- Client misconfiguration (401 with `unauthorized_client`)
- Connection issues (network errors)

### Metrics to Consider (Future)

- Token retrieval latency
- Authentication failure rate
- Token cache hit rate (if caching is added)

---

## Infrastructure Needs

None - this task only creates template files. However, verification requires:
- Running Keycloak instance
- Configured realm with test users (TASK-09)

---

## Notes

1. **Future Token Exchange Migration**: The `AuthStrategy` interface is designed to support Token Exchange without changing test code. A future `TokenExchangeStrategy` would implement the same interface.

2. **Password Grant Deprecation**: While password grant is deprecated for production, it's appropriate for testing where:
   - Test users have known credentials
   - Keycloak is under developer control
   - No browser interaction is desired

3. **No Token Caching**: Each call fetches a new token. For large test suites, consider adding token caching in the fixtures layer (TASK-05).

4. **Client Secret Security**: The client secret is hardcoded to match the realm setup script. This is acceptable for development/testing configurations.

---

## FRD References

- FR-2.1: Auth Helper File
- FR-2.2: getAccessToken Function
- FR-2.3: Convenience Token Functions
- FR-2.4: Authorization Header Builder
- FR-2.5: Module Exports
- FR-9.1: Authentication Error Messages
- IP-2: Phase 2 - Authentication Infrastructure
- TA-2: Authentication Strategy

---

*Task Created: 2025-12-04*
*Status: Not Started*
