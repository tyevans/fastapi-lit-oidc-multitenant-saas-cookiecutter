# P5-03: Create k6 Authentication Flow Tests

## Task Identifier
**ID:** P5-03
**Phase:** 5 - Developer Experience
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P5-02 | Structural | Must complete first | Uses k6 structure, lib/, config from P5-02 |

## Scope

### In Scope
- Create authenticated API endpoint load tests
- Implement token acquisition helper for OAuth/OIDC flow
- Create tests for protected endpoints with valid tokens
- Test token refresh scenarios under load
- Implement multi-tenant load testing (different tenant_id values)
- Test rate limiting behavior under load
- Create `api-authenticated.js` script

### Out of Scope
- Full OIDC browser-based flow (k6 is headless)
- Keycloak admin API integration
- User provisioning during tests (pre-created test users assumed)
- OAuth client credentials flow (uses password grant for simplicity)
- Testing Keycloak itself (focus on application behavior)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/tests/load/
  scripts/
    api-authenticated.js          # Authenticated endpoint tests
  lib/
    auth.js                       # Authentication helpers
    tokens.js                     # Token management
```

### Files to Modify
```
template/{{cookiecutter.project_slug}}/tests/load/lib/config.js      # Add auth config
template/{{cookiecutter.project_slug}}/tests/load/scenarios/load.js  # Import auth tests
template/{{cookiecutter.project_slug}}/tests/load/README.md          # Document auth testing
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/backend/app/api/routers/auth.py     # Auth endpoints
template/{{cookiecutter.project_slug}}/backend/app/middleware/tenant.py    # Tenant context
template/{{cookiecutter.project_slug}}/frontend/src/auth/auth-service.ts   # Token flow reference
tests/load/lib/config.js                                                   # Existing config (P5-02)
```

## Implementation Details

### 1. Auth Configuration (`tests/load/lib/auth.js`)

```javascript
// Authentication utilities for k6 load tests
//
// Provides helpers for obtaining and managing OAuth tokens.
// Uses Resource Owner Password Credentials flow for simplicity in load tests.
//
// Prerequisites:
//   - Test users created in Keycloak
//   - Client configured to allow password grant (test client only)

import http from 'k6/http';
import { check } from 'k6';
import encoding from 'k6/encoding';

// Auth configuration from environment
export const authConfig = {
  // Keycloak/OAuth endpoints
  tokenUrl: __ENV.TOKEN_URL || 'http://localhost:8080/realms/{{ cookiecutter.project_slug }}/protocol/openid-connect/token',

  // OAuth client credentials
  clientId: __ENV.CLIENT_ID || '{{ cookiecutter.project_slug }}-test',
  clientSecret: __ENV.CLIENT_SECRET || '',  // Optional for public clients

  // Test user credentials (for password grant)
  testUsers: parseTestUsers(__ENV.TEST_USERS || 'testuser:testpass'),

  // Token refresh threshold (refresh when less than this many seconds remain)
  refreshThreshold: 60,
};

// Parse TEST_USERS environment variable
// Format: "user1:pass1,user2:pass2"
function parseTestUsers(usersStr) {
  return usersStr.split(',').map(pair => {
    const [username, password] = pair.split(':');
    return { username, password };
  });
}

// Token cache (per VU)
const tokenCache = {};

/**
 * Obtain an access token using password grant.
 *
 * @param {string} username - Username for authentication
 * @param {string} password - Password for authentication
 * @returns {Object} Token response with access_token, refresh_token, expires_in
 */
export function getToken(username, password) {
  const payload = {
    grant_type: 'password',
    client_id: authConfig.clientId,
    username: username,
    password: password,
  };

  if (authConfig.clientSecret) {
    payload.client_secret = authConfig.clientSecret;
  }

  const response = http.post(authConfig.tokenUrl, payload, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    tags: { name: 'token_request' },
  });

  const success = check(response, {
    'token request successful': (r) => r.status === 200,
    'token response has access_token': (r) => {
      const body = JSON.parse(r.body);
      return 'access_token' in body;
    },
  });

  if (!success) {
    console.error(`Token request failed: ${response.status} - ${response.body}`);
    return null;
  }

  const tokenData = JSON.parse(response.body);
  return {
    accessToken: tokenData.access_token,
    refreshToken: tokenData.refresh_token,
    expiresIn: tokenData.expires_in,
    expiresAt: Date.now() + (tokenData.expires_in * 1000),
    tokenType: tokenData.token_type,
  };
}

/**
 * Refresh an access token using refresh token.
 *
 * @param {string} refreshToken - The refresh token
 * @returns {Object} New token response
 */
export function refreshToken(refreshToken) {
  const payload = {
    grant_type: 'refresh_token',
    client_id: authConfig.clientId,
    refresh_token: refreshToken,
  };

  if (authConfig.clientSecret) {
    payload.client_secret = authConfig.clientSecret;
  }

  const response = http.post(authConfig.tokenUrl, payload, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    tags: { name: 'token_refresh' },
  });

  if (response.status !== 200) {
    console.error(`Token refresh failed: ${response.status}`);
    return null;
  }

  const tokenData = JSON.parse(response.body);
  return {
    accessToken: tokenData.access_token,
    refreshToken: tokenData.refresh_token,
    expiresIn: tokenData.expires_in,
    expiresAt: Date.now() + (tokenData.expires_in * 1000),
    tokenType: tokenData.token_type,
  };
}

/**
 * Get a valid access token, refreshing if necessary.
 * Manages token lifecycle per VU.
 *
 * @param {number} userIndex - Index into test users array (for multi-user tests)
 * @returns {string} Valid access token
 */
export function getValidToken(userIndex = 0) {
  const cacheKey = `user_${userIndex}`;
  const cached = tokenCache[cacheKey];

  // Check if we have a valid cached token
  if (cached) {
    const remainingSeconds = (cached.expiresAt - Date.now()) / 1000;

    // Token still valid and not near expiry
    if (remainingSeconds > authConfig.refreshThreshold) {
      return cached.accessToken;
    }

    // Try to refresh
    if (cached.refreshToken) {
      const refreshed = refreshToken(cached.refreshToken);
      if (refreshed) {
        tokenCache[cacheKey] = refreshed;
        return refreshed.accessToken;
      }
    }
  }

  // Need to get a new token
  const user = authConfig.testUsers[userIndex % authConfig.testUsers.length];
  const token = getToken(user.username, user.password);

  if (token) {
    tokenCache[cacheKey] = token;
    return token.accessToken;
  }

  throw new Error(`Failed to obtain token for user index ${userIndex}`);
}

/**
 * Create authorization header with Bearer token.
 *
 * @param {number} userIndex - Index into test users array
 * @returns {Object} Headers object with Authorization
 */
export function authHeaders(userIndex = 0) {
  const token = getValidToken(userIndex);
  return {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
}

/**
 * Decode JWT token to inspect claims (for debugging/validation).
 *
 * @param {string} token - JWT token string
 * @returns {Object} Decoded token payload
 */
export function decodeToken(token) {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid JWT format');
    }
    const payload = encoding.b64decode(parts[1], 'rawurl', 's');
    return JSON.parse(payload);
  } catch (e) {
    console.error(`Failed to decode token: ${e.message}`);
    return null;
  }
}

/**
 * Extract tenant_id from token claims.
 *
 * @param {string} token - JWT token string
 * @returns {string} Tenant ID or null
 */
export function getTenantId(token) {
  const decoded = decodeToken(token);
  return decoded ? decoded.tenant_id || decoded.tid : null;
}
```

### 2. Token Management (`tests/load/lib/tokens.js`)

```javascript
// Token management utilities for multi-user load testing
//
// Provides pooling and distribution of tokens across VUs.

import { SharedArray } from 'k6/data';
import { getToken, authConfig } from './auth.js';

// Pre-populate tokens for all test users during setup
// This avoids token acquisition overhead during the test
let tokenPool = null;

/**
 * Initialize token pool during test setup.
 * Call this from setup() function.
 *
 * @returns {Array} Array of token objects
 */
export function initializeTokenPool() {
  const tokens = [];

  for (const user of authConfig.testUsers) {
    const token = getToken(user.username, user.password);
    if (token) {
      tokens.push({
        username: user.username,
        ...token,
      });
    } else {
      console.warn(`Failed to get token for ${user.username}`);
    }
  }

  console.log(`Initialized token pool with ${tokens.length} tokens`);
  return tokens;
}

/**
 * Get a token from the pool based on VU number.
 * Distributes load across available tokens.
 *
 * @param {Array} pool - Token pool from setup
 * @param {number} vuId - Virtual user ID (__VU)
 * @returns {Object} Token object
 */
export function getPooledToken(pool, vuId) {
  if (!pool || pool.length === 0) {
    throw new Error('Token pool is empty');
  }

  const index = (vuId - 1) % pool.length;
  return pool[index];
}

/**
 * Create test user data for multi-tenant testing.
 * Returns SharedArray for efficient memory usage.
 */
export function createTestUsers() {
  return new SharedArray('test_users', function() {
    // In a real scenario, this might load from a file
    return authConfig.testUsers.map((user, index) => ({
      username: user.username,
      password: user.password,
      tenantId: `tenant_${index + 1}`,  // Simulated tenant IDs
    }));
  });
}
```

### 3. Authenticated API Tests (`tests/load/scripts/api-authenticated.js`)

```javascript
// Authenticated API Endpoint Load Tests
//
// Tests protected API endpoints with valid OAuth tokens.
// Includes token acquisition, refresh, and multi-user scenarios.
//
// Prerequisites:
//   - Test users created in Keycloak
//   - Backend running with auth enabled
//
// Usage:
//   k6 run tests/load/scripts/api-authenticated.js
//   k6 run --env TEST_USERS=user1:pass1,user2:pass2 tests/load/scripts/api-authenticated.js
//
// Environment Variables:
//   TOKEN_URL    - OAuth token endpoint
//   CLIENT_ID    - OAuth client ID
//   TEST_USERS   - Comma-separated user:pass pairs

import http from 'k6/http';
import { check, sleep, group, fail } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { BASE_URL, API_PREFIX, defaultOptions } from '../lib/config.js';
import { authHeaders, getValidToken, decodeToken, authConfig } from '../lib/auth.js';
import { initializeTokenPool, getPooledToken } from '../lib/tokens.js';
import { thinkTime } from '../lib/helpers.js';

// Custom metrics
const authErrors = new Rate('auth_errors');
const tokenRefreshCount = new Counter('token_refresh_count');
const authenticatedRequests = new Counter('authenticated_requests');
const authLatency = new Trend('auth_latency', true);

// Test configuration
export const options = {
  scenarios: {
    authenticated_api: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 10 },   // Warm up
        { duration: '3m', target: 30 },   // Normal load
        { duration: '1m', target: 0 },    // Cool down
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.05'],  // Allow slightly higher for auth issues
    auth_errors: ['rate<0.05'],
    'http_req_duration{name:me}': ['p(95)<300'],
    'http_req_duration{name:todos}': ['p(95)<500'],
    checks: ['rate>0.90'],
  },
  tags: {
    test_type: 'authenticated',
  },
};

// Setup: Initialize token pool
export function setup() {
  console.log(`\n=== Authenticated API Load Test ===`);
  console.log(`Base URL: ${BASE_URL}${API_PREFIX}`);
  console.log(`Token URL: ${authConfig.tokenUrl}`);
  console.log(`Test Users: ${authConfig.testUsers.length}`);
  console.log('');

  // Get tokens for all test users upfront
  const tokenPool = initializeTokenPool();

  if (tokenPool.length === 0) {
    fail('No valid tokens obtained - check TEST_USERS and Keycloak configuration');
  }

  return {
    tokenPool: tokenPool,
    startTime: new Date().toISOString(),
  };
}

// Main test function
export default function(data) {
  // Get token for this VU
  let token;
  try {
    const pooledToken = getPooledToken(data.tokenPool, __VU);
    token = pooledToken.accessToken;
  } catch (e) {
    // Fallback to dynamic token acquisition
    token = getValidToken(__VU % authConfig.testUsers.length);
  }

  if (!token) {
    authErrors.add(1);
    console.error(`VU ${__VU}: Failed to obtain token`);
    sleep(5);  // Back off on auth failure
    return;
  }

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Test 1: Get current user (/me endpoint)
  group('user_profile', function() {
    const startTime = Date.now();
    const response = http.get(`${BASE_URL}${API_PREFIX}/auth/me`, {
      headers: headers,
      tags: { name: 'me', authenticated: 'true' },
    });
    authLatency.add(Date.now() - startTime);

    authenticatedRequests.add(1);
    authErrors.add(response.status === 401 || response.status === 403);

    const success = check(response, {
      'me: status 200': (r) => r.status === 200,
      'me: has user data': (r) => {
        if (r.status !== 200) return false;
        try {
          const body = JSON.parse(r.body);
          return 'sub' in body || 'email' in body || 'user_id' in body;
        } catch {
          return false;
        }
      },
      'me: response time < 300ms': (r) => r.timings.duration < 300,
    });

    if (!success && response.status === 401) {
      console.log(`VU ${__VU}: Token expired or invalid`);
    }
  });

  thinkTime(1, 2);

  // Test 2: List todos (protected, tenant-scoped)
  group('list_todos', function() {
    const response = http.get(`${BASE_URL}${API_PREFIX}/todos`, {
      headers: headers,
      tags: { name: 'todos', authenticated: 'true' },
    });

    authenticatedRequests.add(1);
    authErrors.add(response.status === 401 || response.status === 403);

    check(response, {
      'todos: status 200': (r) => r.status === 200,
      'todos: returns array': (r) => {
        if (r.status !== 200) return false;
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body) || ('items' in body && Array.isArray(body.items));
        } catch {
          return false;
        }
      },
    });
  });

  thinkTime(2, 4);

  // Test 3: Create and delete todo (write operations)
  group('crud_todo', function() {
    // Create
    const createPayload = JSON.stringify({
      title: `Load test todo ${Date.now()}`,
      description: `Created by VU ${__VU} at iteration ${__ITER}`,
    });

    const createResponse = http.post(`${BASE_URL}${API_PREFIX}/todos`, createPayload, {
      headers: headers,
      tags: { name: 'create_todo', authenticated: 'true' },
    });

    authenticatedRequests.add(1);

    const created = check(createResponse, {
      'create: status 201 or 200': (r) => r.status === 201 || r.status === 200,
    });

    // Delete if created successfully
    if (created && (createResponse.status === 201 || createResponse.status === 200)) {
      try {
        const todoData = JSON.parse(createResponse.body);
        const todoId = todoData.id;

        if (todoId) {
          sleep(0.5);  // Brief pause before delete

          const deleteResponse = http.del(`${BASE_URL}${API_PREFIX}/todos/${todoId}`, null, {
            headers: headers,
            tags: { name: 'delete_todo', authenticated: 'true' },
          });

          authenticatedRequests.add(1);

          check(deleteResponse, {
            'delete: status 204 or 200': (r) => r.status === 204 || r.status === 200,
          });
        }
      } catch (e) {
        console.log(`VU ${__VU}: Failed to parse create response`);
      }
    }
  });

  thinkTime(2, 4);
}

// Teardown
export function teardown(data) {
  console.log(`\n=== Test Complete ===`);
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
  console.log(`Token pool size: ${data.tokenPool.length}`);
}

// Summary handler
export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    scenario: 'authenticated',
    metrics: {
      requests: data.metrics.authenticated_requests?.values?.count || 0,
      authErrors: (data.metrics.auth_errors?.values?.rate || 0) * 100,
      duration: {
        avg: data.metrics.http_req_duration?.values?.avg || 0,
        p95: data.metrics.http_req_duration?.values?.['p(95)'] || 0,
      },
      authLatency: {
        avg: data.metrics.auth_latency?.values?.avg || 0,
        p95: data.metrics.auth_latency?.values?.['p(95)'] || 0,
      },
    },
  };

  return {
    'results/auth-test-summary.json': JSON.stringify(summary, null, 2),
  };
}
```

### 4. Token Refresh Under Load Test

```javascript
// Token Refresh Load Test (add to api-authenticated.js or create separate file)
//
// Tests token refresh behavior under sustained load.
// Ensures the system handles token expiry gracefully.

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter, Rate } from 'k6/metrics';
import { BASE_URL, API_PREFIX } from '../lib/config.js';
import { getToken, refreshToken, authConfig } from '../lib/auth.js';

const refreshSuccessRate = new Rate('refresh_success_rate');
const refreshCount = new Counter('refresh_count');

export const options = {
  scenarios: {
    token_refresh: {
      executor: 'constant-vus',
      vus: 5,
      duration: '10m',  // Long duration to force token refresh
    },
  },
  thresholds: {
    refresh_success_rate: ['rate>0.95'],
    http_req_failed: ['rate<0.05'],
  },
};

export function setup() {
  // Get initial token with short expiry (if configurable)
  const user = authConfig.testUsers[0];
  const token = getToken(user.username, user.password);
  return { initialToken: token };
}

export default function(data) {
  let currentToken = data.initialToken;

  // Make authenticated request
  const response = http.get(`${BASE_URL}${API_PREFIX}/auth/me`, {
    headers: {
      'Authorization': `Bearer ${currentToken.accessToken}`,
    },
  });

  // If token expired, refresh it
  if (response.status === 401) {
    group('token_refresh', function() {
      const newToken = refreshToken(currentToken.refreshToken);
      refreshCount.add(1);

      if (newToken) {
        refreshSuccessRate.add(1);
        currentToken = newToken;
      } else {
        refreshSuccessRate.add(0);
        // Get new token via password grant
        const user = authConfig.testUsers[__VU % authConfig.testUsers.length];
        currentToken = getToken(user.username, user.password);
      }
    });
  }

  check(response, {
    'status is 200 or handled 401': (r) => r.status === 200 || r.status === 401,
  });

  sleep(5);  // Wait between requests to allow tokens to expire
}
```

### 5. Rate Limiting Test

```javascript
// Rate Limiting Behavior Test
//
// Tests that rate limiting is enforced and returns proper responses.
// Located at: tests/load/scripts/rate-limiting.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Counter } from 'k6/metrics';
import { BASE_URL, API_PREFIX } from '../lib/config.js';
import { authHeaders } from '../lib/auth.js';

const rateLimitHits = new Counter('rate_limit_hits');
const rateLimitRate = new Rate('rate_limit_rate');

export const options = {
  scenarios: {
    rate_limit_test: {
      executor: 'constant-arrival-rate',
      rate: 100,           // 100 requests per second
      timeUnit: '1s',
      duration: '1m',
      preAllocatedVUs: 50,
      maxVUs: 100,
    },
  },
  thresholds: {
    // We expect some rate limiting
    http_req_failed: ['rate<0.30'],  // Up to 30% may be rate limited
  },
};

export function setup() {
  console.log('Testing rate limiting behavior...');
  console.log('Sending high request volume to trigger rate limits.');
  return {};
}

export default function() {
  const response = http.get(`${BASE_URL}${API_PREFIX}/health`, {
    tags: { name: 'rate_limit_test' },
  });

  if (response.status === 429) {
    rateLimitHits.add(1);
    rateLimitRate.add(1);

    check(response, {
      'rate limit: has Retry-After header': (r) => 'retry-after' in r.headers,
      'rate limit: proper 429 response': (r) => r.status === 429,
    });

    // Respect Retry-After if present
    const retryAfter = response.headers['retry-after'];
    if (retryAfter) {
      sleep(parseInt(retryAfter) || 1);
    }
  } else {
    rateLimitRate.add(0);
    check(response, {
      'request: status 200': (r) => r.status === 200,
    });
  }
}

export function handleSummary(data) {
  const totalRequests = data.metrics.http_reqs?.values?.count || 0;
  const rateLimited = data.metrics.rate_limit_hits?.values?.count || 0;

  console.log(`\n=== Rate Limiting Summary ===`);
  console.log(`Total Requests: ${totalRequests}`);
  console.log(`Rate Limited (429): ${rateLimited}`);
  console.log(`Rate Limit %: ${((rateLimited / totalRequests) * 100).toFixed(2)}%`);

  return {};
}
```

### 6. Multi-Tenant Load Test

```javascript
// Multi-Tenant Load Test
//
// Tests that tenant isolation is maintained under load.
// Each VU operates as a different tenant.
//
// Located at: tests/load/scripts/multi-tenant.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Counter } from 'k6/metrics';
import { BASE_URL, API_PREFIX } from '../lib/config.js';
import { authHeaders, getTenantId, getValidToken } from '../lib/auth.js';

const tenantRequests = new Counter('tenant_requests');
const crossTenantErrors = new Counter('cross_tenant_errors');

export const options = {
  scenarios: {
    multi_tenant: {
      executor: 'per-vu-iterations',
      vus: 10,
      iterations: 50,
    },
  },
  thresholds: {
    cross_tenant_errors: ['count==0'],  // No cross-tenant access
    checks: ['rate>0.99'],
  },
};

export function setup() {
  console.log('Testing multi-tenant isolation under load...');
  return {};
}

export default function() {
  // Each VU gets a different user (and potentially different tenant)
  const userIndex = (__VU - 1) % 10;  // Assuming up to 10 test users
  const token = getValidToken(userIndex);
  const expectedTenantId = getTenantId(token);

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  group('tenant_isolation', function() {
    // Create a resource
    const createPayload = JSON.stringify({
      title: `Tenant ${expectedTenantId} todo`,
      tenant_marker: expectedTenantId,
    });

    const createResponse = http.post(`${BASE_URL}${API_PREFIX}/todos`, createPayload, {
      headers: headers,
    });

    tenantRequests.add(1);

    if (createResponse.status === 201 || createResponse.status === 200) {
      const created = JSON.parse(createResponse.body);

      // Verify tenant_id matches
      const resourceTenantId = created.tenant_id;
      if (resourceTenantId && resourceTenantId !== expectedTenantId) {
        crossTenantErrors.add(1);
        console.error(`TENANT VIOLATION: Expected ${expectedTenantId}, got ${resourceTenantId}`);
      }

      check(createResponse, {
        'created: correct tenant': (r) => {
          const body = JSON.parse(r.body);
          return !body.tenant_id || body.tenant_id === expectedTenantId;
        },
      });

      // Clean up
      if (created.id) {
        http.del(`${BASE_URL}${API_PREFIX}/todos/${created.id}`, null, { headers });
      }
    }
  });

  sleep(1);
}

export function teardown(data) {
  console.log('Multi-tenant test complete');
}
```

### 7. Update Config for Auth (`tests/load/lib/config.js` addition)

```javascript
// Add to existing config.js from P5-02

// Authentication configuration
export const authConfig = {
  enabled: __ENV.AUTH_ENABLED !== 'false',
  tokenUrl: __ENV.TOKEN_URL || 'http://localhost:8080/realms/{{ cookiecutter.project_slug }}/protocol/openid-connect/token',
  clientId: __ENV.CLIENT_ID || '{{ cookiecutter.project_slug }}-test',
};

// Authenticated request helper
export function withAuth(token) {
  return {
    ...defaultOptions,
    headers: {
      ...defaultOptions.headers,
      'Authorization': `Bearer ${token}`,
    },
  };
}
```

### 8. Update README (`tests/load/README.md` addition)

```markdown
## Authenticated Testing

### Prerequisites

1. **Create Test Users in Keycloak:**
   ```bash
   # Access Keycloak admin console
   open http://localhost:8080/admin
   # Login: admin / admin

   # Create test realm users or use existing
   ```

2. **Configure Test Client:**
   - Enable "Direct Access Grants" (password grant)
   - Set client as "public" or configure secret

3. **Set Environment Variables:**
   ```bash
   export TEST_USERS="testuser1:password1,testuser2:password2"
   export TOKEN_URL="http://localhost:8080/realms/myapp/protocol/openid-connect/token"
   export CLIENT_ID="myapp-test"
   ```

### Running Authenticated Tests

```bash
# Run with default test user
./scripts/load-test.sh auth

# Run with custom users
k6 run --env TEST_USERS=user:pass tests/load/scripts/api-authenticated.js

# Test token refresh
k6 run tests/load/scripts/token-refresh.js
```

### Test Scenarios

| Script | Description |
|--------|-------------|
| `api-authenticated.js` | Protected endpoint tests |
| `rate-limiting.js` | Rate limit behavior |
| `multi-tenant.js` | Tenant isolation verification |

### Troubleshooting Authentication

**Token request fails:**
- Verify Keycloak is running: `curl http://localhost:8080`
- Check client configuration in Keycloak admin
- Verify test user credentials

**401 errors during test:**
- Token may have expired (check `expires_in`)
- Verify token is being refreshed correctly
- Check clock sync between systems

**Cross-tenant errors:**
- Verify tenant_id claim in token
- Check RLS policies in database
- Review multi-tenant middleware logs
```

## Success Criteria

### Functional Requirements
- [ ] FR-DX-005: Load testing scripts test authentication flow
- [ ] Authentication helpers obtain valid tokens
- [ ] Token refresh works under load
- [ ] Multi-tenant isolation is maintained
- [ ] Rate limiting behavior is tested

### Verification Steps
1. **Token Acquisition:**
   ```bash
   # Verify token can be obtained
   k6 run --iterations 1 tests/load/scripts/api-authenticated.js
   # Should show successful token acquisition in logs
   ```

2. **Authenticated Requests:**
   ```bash
   # Run short authenticated test
   k6 run --vus 5 --duration 30s tests/load/scripts/api-authenticated.js
   # Should show 0% auth_errors
   ```

3. **Multi-Tenant Test:**
   ```bash
   k6 run tests/load/scripts/multi-tenant.js
   # Should show cross_tenant_errors: count==0
   ```

4. **Rate Limiting:**
   ```bash
   k6 run tests/load/scripts/rate-limiting.js
   # Should show rate_limit_hits and proper 429 handling
   ```

### Quality Gates
- [ ] Token acquisition succeeds for all test users
- [ ] Token refresh handles expiry gracefully
- [ ] No cross-tenant data access under load
- [ ] Rate limiting returns proper 429 responses
- [ ] Error handling for auth failures is robust
- [ ] Documentation covers auth test setup

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P5-02 | k6 structure | Uses lib/, config, helpers from P5-02 |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P5-05 | Auth metrics | Baselines include auth latency |
| P6-01 | Auth test docs | CLAUDE.md documents auth testing |

### Integration Contract
```yaml
# Contract: Authentication Load Testing

# Auth helper module
tests/load/lib/auth.js
  - getToken(username, password) -> token object
  - refreshToken(refreshToken) -> token object
  - getValidToken(userIndex) -> access token string
  - authHeaders(userIndex) -> headers object

# Token pool management
tests/load/lib/tokens.js
  - initializeTokenPool() -> Array<token>
  - getPooledToken(pool, vuId) -> token

# Environment variables
TEST_USERS: "user1:pass1,user2:pass2"
TOKEN_URL: OAuth token endpoint
CLIENT_ID: OAuth client ID
CLIENT_SECRET: Optional client secret

# Test scripts
api-authenticated.js: Protected endpoint tests
rate-limiting.js: Rate limit behavior
multi-tenant.js: Tenant isolation
```

## Monitoring and Observability

### Authentication Metrics
- Token acquisition latency
- Token refresh success rate
- Authentication error rate
- Per-tenant request distribution

### Alerts During Testing
- High auth error rate (>5%)
- Token refresh failures
- Cross-tenant access attempts

## Infrastructure Needs

### Development Requirements
- Keycloak running with test realm
- Test users configured
- Client with password grant enabled

### CI Requirements (Future)
- Keycloak service in CI
- Test user provisioning
- Secret management for credentials

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Builds on P5-02 foundation
- OAuth integration requires testing
- Multiple auth scenarios to cover
- Token lifecycle management
- Multi-tenant considerations

## Notes

### Design Decisions

**1. Password Grant for Load Tests:**
- Simplest flow for headless testing
- Keycloak test client only
- Not used in production clients

**2. Token Pooling:**
- Pre-acquire tokens in setup()
- Avoids token request overhead per VU
- Distributes load across users

**3. Per-VU Token Cache:**
- Each VU manages its own token
- Handles refresh independently
- Prevents token sharing issues

### Security Considerations

**Test Credentials:**
- Use dedicated test users only
- Never use production credentials
- Test users have limited permissions

**Token Handling:**
- Tokens are ephemeral (test duration)
- No persistent token storage
- Credentials via environment only

### Related Requirements
- FR-DX-005: Load testing scripts test authentication flow
- US-5.2: Authentication flow testing
