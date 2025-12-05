# FRD: Playwright API Testing Support for Cookiecutter Template

| **Metadata** | **Value** |
|--------------|-----------|
| Title | Playwright API Testing Support for Cookiecutter Template |
| Date Created | 2025-12-04 |
| Last Updated | 2025-12-04 |
| Author/Agent | FRD Writer Agent |
| Status | Ready for FRD Refiner - All sections complete |

---

## Table of Contents

1. [Problem Statement](#problem-statement) - COMPLETE
2. [Goals & Success Criteria](#goals--success-criteria) - COMPLETE
3. [Scope & Boundaries](#scope--boundaries) - COMPLETE
4. [User Stories / Use Cases](#user-stories--use-cases) - COMPLETE
5. [Functional Requirements](#functional-requirements) - COMPLETE
6. [Technical Approach](#technical-approach) - COMPLETE
7. [Architecture & Integration Considerations](#architecture--integration-considerations) - COMPLETE
8. [Data Models & Schema Changes](#data-models--schema-changes) - COMPLETE
9. [UI/UX Considerations](#uiux-considerations) - COMPLETE
10. [Security & Privacy Considerations](#security--privacy-considerations) - COMPLETE
11. [Testing Strategy](#testing-strategy) - COMPLETE
12. [Implementation Phases](#implementation-phases) - COMPLETE
13. [Dependencies & Risks](#dependencies--risks) - COMPLETE
14. [Open Questions](#open-questions) - COMPLETE
15. [Status](#status)

---

## Problem Statement

### Current Situation

The cookiecutter template at `/home/ty/workspace/project-starter/template/` currently provides Playwright testing support, but it is limited to **frontend E2E testing only**. The existing setup includes:

1. **Frontend-focused Playwright configuration** (`frontend/playwright.config.ts`):
   - Tests located in `frontend/e2e/` directory
   - Configured for browser-based UI testing with Chromium
   - Base URL pointing to frontend (`http://localhost:3000`)
   - Only one example test (`health-check.spec.ts`) testing the health-check Lit web component

2. **No API testing infrastructure**:
   - No standalone Playwright project for backend API testing
   - No authenticated request fixtures for testing protected endpoints
   - No integration with Keycloak authentication flow for test users
   - No Makefile targets for running API tests

### Evidence from Codebase

The reference implementation at `implementation-manager/playwright/` demonstrates a mature API testing setup that is **missing from the template**:

**Implementation-manager has** (`/home/ty/workspace/project-starter/implementation-manager/playwright/`):
```
playwright/
├── playwright.config.js       # API-focused config with baseURL to backend
├── package.json               # Dedicated dependencies and npm scripts
├── README.md                  # Comprehensive documentation
├── QUICK_START.md             # Quick start guide for developers
├── .gitignore                 # Playwright-specific ignores
└── tests/
    ├── auth-helper.js         # Keycloak authentication utilities
    ├── test-users.js          # Test user fixtures with credentials
    ├── fixtures.js            # Extended Playwright fixtures with authenticated contexts
    ├── api-endpoints.api.spec.js      # Basic API tests
    └── api-with-fixtures.api.spec.js  # Example tests using fixture pattern
```

**Template currently has** (`/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/frontend/`):
```
frontend/
├── playwright.config.ts      # Browser-focused config only
└── e2e/
    └── health-check.spec.ts  # Single UI test
```

### User Pain Points

1. **Developers using the template cannot test API endpoints** out of the box without manually setting up authentication helpers and fixtures.

2. **No standardized pattern** for testing protected endpoints with different user roles (admin, user, manager, readonly, etc.).

3. **No integration with Keycloak** for obtaining valid JWT tokens during API tests.

4. **No Makefile targets** for running API tests, forcing developers to navigate to different directories and remember npm commands.

5. **Documentation gap**: No guidance on how to write API tests for the multi-tenant OAuth-protected backend.

### Business Driver

Projects generated from this template are **multi-tenant applications with OAuth 2.0 authentication via Keycloak**. Without proper API testing infrastructure:

- Developers skip API testing, leading to bugs in production
- Each team reinvents the authentication testing wheel
- Test coverage for protected endpoints is inconsistent or non-existent
- Role-based access control (RBAC) is not systematically tested

The implementation-manager project has already solved these problems with a well-structured Playwright API testing setup. Incorporating this into the template will:

- Provide a batteries-included testing experience
- Ensure consistent API testing patterns across all generated projects
- Enable proper testing of authentication, authorization, and multi-tenancy

---

## Goals & Success Criteria

### Primary Goals

#### G1: Provide Standalone Playwright API Testing Infrastructure

Add a dedicated `playwright/` directory at the project root level (parallel to `frontend/` and `backend/`) that contains all necessary infrastructure for testing the FastAPI backend API endpoints with authentication.

**Success Criteria:**
- A `playwright/` directory exists in generated projects with its own `package.json`, `playwright.config.js`, and test directory
- The API testing setup is independent of the frontend E2E testing setup
- Tests can be run without starting the frontend development server
- The configuration points to the backend API (`http://localhost:8000`) as the base URL

#### G2: Enable Authenticated API Testing with Keycloak Integration

Provide utilities and fixtures that allow developers to test protected endpoints using valid JWT tokens obtained from Keycloak during test execution.

**Success Criteria:**
- An `auth-helper.js` module provides functions to obtain access tokens from Keycloak via the OAuth 2.0 password grant
- Pre-configured test user fixtures are available for different roles (admin, standard user, readonly, manager, service account)
- Developers can write tests with a single line to access authenticated endpoints:
  ```javascript
  test('admin can access admin endpoint', async ({ adminRequest }) => {
    const response = await adminRequest.get('/admin');
    expect(response.ok()).toBeTruthy();
  });
  ```
- Authentication failures during test setup produce clear, actionable error messages

#### G3: Support Role-Based Access Control (RBAC) Testing

Enable systematic testing of role-based permissions where different test users have different access levels to endpoints.

**Success Criteria:**
- At least 6 pre-configured test users with distinct role combinations:
  - `admin` - Full admin access (roles: user, admin)
  - `testuser` - Standard user (roles: user)
  - `readonly` - Read-only access (roles: user, readonly)
  - `manager` - Elevated permissions (roles: user, manager)
  - `newuser` - Fresh account for onboarding flows (roles: user)
  - `service-account` - Service-to-service communication (roles: service)
- Tests can verify both positive cases (user has access) and negative cases (user is denied)
- Role verification assertions are demonstrated in example tests

#### G4: Integrate with Project Makefile

Provide Makefile targets that make running API tests simple and consistent with other project commands.

**Success Criteria:**
- `make test` or `make test-api` runs all API tests from the project root
- `make test-ui` runs tests in Playwright's interactive UI mode
- `make test-debug` runs tests in debug mode
- `make test-report` opens the HTML test report
- `make test-install` installs Playwright dependencies
- All targets work correctly from the project root directory

#### G5: Provide Comprehensive Documentation

Include documentation that enables developers to quickly understand and extend the API testing infrastructure.

**Success Criteria:**
- A `README.md` in the `playwright/` directory explains the test structure, available fixtures, and common patterns
- A `QUICK_START.md` provides a 5-minute guide to running first tests
- Example tests demonstrate both basic patterns (manual auth) and recommended patterns (fixtures)
- Test user credentials and roles are clearly documented

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Time to first API test | < 5 minutes | Developer can run `make test-install && make test-api` successfully |
| Test user coverage | 6 distinct roles | Count of pre-configured test users with unique role combinations |
| Documentation completeness | 100% | README covers all fixtures, auth helpers, and test patterns |
| Example test coverage | 4 categories | Public endpoints, protected endpoints, admin-only endpoints, token validation |
| Makefile integration | 5+ targets | Count of test-related Makefile targets |

### Non-Goals (Explicit Exclusions)

The following are explicitly NOT goals of this feature:

1. **Replacing frontend E2E tests**: The existing frontend Playwright setup in `frontend/e2e/` remains unchanged and serves a different purpose (browser-based UI testing)

2. **Database seeding or fixtures**: Test data setup is outside the scope; tests should work against the default Keycloak realm with pre-configured users

3. **Performance or load testing**: Playwright API tests are for functional correctness, not performance benchmarking

4. **Multi-tenant isolation testing**: While the template supports multi-tenancy, complex tenant isolation scenarios are left to project-specific test implementations

5. **CI/CD pipeline configuration**: While the setup should work in CI, specific GitHub Actions or other CI configurations are not included

### Timeline Expectations

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | 1-2 days | Core infrastructure (playwright.config.js, package.json, auth-helper.js) |
| Phase 2 | 1 day | Test user fixtures and authenticated request contexts |
| Phase 3 | 1 day | Example tests and documentation |
| Phase 4 | 0.5 days | Makefile integration |
| Phase 5 | 0.5 days | Template integration and testing |

**Total estimated effort**: 4-5 days

### Definition of Done

This feature is complete when:

1. A new project generated from the template includes a fully functional `playwright/` directory
2. Running `make test-install && make test-api` from the project root executes API tests successfully
3. All 6 test user fixtures are available and working
4. The `README.md` and `QUICK_START.md` documentation is complete
5. At least 10 example tests demonstrate the key patterns:
   - Public endpoint testing
   - Protected endpoint testing with authentication
   - Admin-only endpoint testing with role checking
   - Token validation and error handling
   - Multiple user contexts in a single test
6. The Keycloak realm setup script (`keycloak/setup-realm.sh`) creates all required test users

---

## Scope & Boundaries

### In Scope

#### IS-1: New Playwright Directory at Project Root

Create a new `playwright/` directory at the project root level, parallel to `frontend/` and `backend/`. This directory will be completely independent of the existing frontend E2E testing setup.

**Deliverables:**
- `playwright/` directory structure in template
- Standalone `package.json` with Playwright dependencies
- Dedicated `playwright.config.js` for API testing
- `.gitignore` for Playwright artifacts

**Rationale:** Separating API tests from frontend E2E tests provides clearer organization and allows developers to run API tests without the frontend development server.

#### IS-2: Keycloak Authentication Helpers

Implement authentication utilities that integrate with the project's Keycloak setup for obtaining JWT access tokens during test execution.

**Deliverables:**
- `tests/auth-helper.js` with functions:
  - `getAccessToken(request, username, password)` - Generic token retrieval
  - `getAdminToken(request)` - Convenience function for admin user
  - `getTestUserToken(request)` - Convenience function for standard user
  - `authHeader(token)` - Authorization header builder
- Environment variable configuration for:
  - `KEYCLOAK_URL` (default: `http://localhost:{{ cookiecutter.keycloak_port }}`)
  - `KEYCLOAK_REALM` (default: `{{ cookiecutter.keycloak_realm_name }}`)
  - `BASE_URL` (default: `http://localhost:{{ cookiecutter.backend_port }}`)

**Rationale:** These helpers abstract away the OAuth 2.0 password grant flow complexity, allowing developers to focus on writing tests rather than authentication plumbing.

#### IS-3: Test User Fixtures Module

Provide a centralized definition of test users with their credentials and roles that matches the Keycloak realm configuration.

**Deliverables:**
- `tests/test-users.js` with:
  - `TEST_USERS` object containing 6 user definitions
  - `getUserByRole(role)` - Find user by role
  - `getUsersByRole(role)` - Find all users with a role
  - `getAllUsers()` - Get all test users

**Test User Matrix:**

| Key | Username | Password | Roles | Tenant ID | Purpose |
|-----|----------|----------|-------|-----------|---------|
| `admin` | admin | admin123 | user, admin | tenant-1 | Full administrative access testing |
| `user` | testuser | test123 | user | tenant-1 | Standard user permission testing |
| `readOnly` | readonly | readonly123 | user, readonly | tenant-1 | Read-only access control testing |
| `newUser` | newuser | newuser123 | user | tenant-1 | Onboarding flow testing |
| `manager` | manager | manager123 | user, manager | tenant-1 | Elevated permission testing |
| `serviceAccount` | service-account | service123 | service | tenant-1 | API-to-API integration testing |

**Rationale:** Consistent test user definitions across all tests prevent credential duplication and make role-based testing systematic.

#### IS-4: Playwright Extended Fixtures

Implement custom Playwright fixtures that provide pre-authenticated request contexts for each test user role.

**Deliverables:**
- `tests/fixtures.js` with extended `test` object providing:
  - `authenticatedRequest` - Object with all user contexts (`.admin`, `.user`, `.readOnly`, `.manager`, `.newUser`, `.serviceAccount`)
  - `adminRequest` - Direct access to admin-authenticated context
  - `userRequest` - Direct access to standard user context
  - `readOnlyRequest` - Direct access to readonly user context
  - `managerRequest` - Direct access to manager user context

**Rationale:** Fixtures eliminate boilerplate authentication code from every test, enabling clean, readable test syntax.

#### IS-5: Example API Test Suites

Provide example tests that demonstrate recommended patterns for common API testing scenarios.

**Deliverables:**
- `tests/api-endpoints.api.spec.js` - Basic tests using manual authentication (for advanced scenarios)
- `tests/api-with-fixtures.api.spec.js` - Tests using fixture pattern (recommended)

**Test Categories to Cover:**
1. Public endpoint testing (health check, root)
2. Protected endpoint testing with valid authentication
3. Unauthorized access testing (401 responses)
4. Admin-only endpoint testing with role verification
5. Forbidden access testing (403 responses for insufficient roles)
6. Token validation and error handling
7. Multiple user contexts in a single test

**Rationale:** Example tests serve as documentation and provide copy-paste starting points for developers.

#### IS-6: Keycloak Realm Test User Setup

Update the `keycloak/setup-realm.sh` script to create all 6 test users with appropriate roles and tenant assignments.

**Deliverables:**
- Add user creation for: admin, testuser, readonly, newuser, manager, service-account
- Configure role assignments matching `test-users.js`
- Set `tenant_id` attribute for multi-tenancy testing
- Use consistent password pattern (username + "123")

**Rationale:** Tests require pre-configured users in Keycloak; the setup script ensures reproducible test environments.

#### IS-7: Documentation

Provide comprehensive documentation for the API testing infrastructure.

**Deliverables:**
- `playwright/README.md` - Full documentation covering:
  - Setup instructions
  - Test structure overview
  - Writing tests with fixtures (recommended pattern)
  - Writing tests with manual authentication (advanced)
  - Available fixtures reference
  - Test user reference table
  - Environment variables
  - CI/CD considerations
- `playwright/QUICK_START.md` - 5-minute guide to first test

**Rationale:** Documentation reduces onboarding time and ensures developers can effectively use the testing infrastructure.

#### IS-8: Makefile Integration (if applicable)

If the template includes or will include a Makefile, add targets for API testing.

**Deliverables (contingent on Makefile existence):**
- `test` or `test-api` - Run all API tests
- `test-ui` - Run tests in interactive UI mode
- `test-debug` - Run tests in debug mode
- `test-report` - Open HTML test report
- `test-install` - Install Playwright dependencies

**Rationale:** Makefile targets provide consistent, discoverable commands for common operations.

---

### Out of Scope

#### OS-1: Frontend E2E Testing Modifications

The existing frontend Playwright setup in `frontend/e2e/` and `frontend/playwright.config.ts` will **not** be modified. The two testing setups serve different purposes:

| Aspect | Frontend E2E (existing) | API Testing (new) |
|--------|------------------------|-------------------|
| Location | `frontend/e2e/` | `playwright/tests/` |
| Config | `frontend/playwright.config.ts` | `playwright/playwright.config.js` |
| Base URL | Frontend (`:3000`) | Backend (`:8000`) |
| Purpose | Browser UI testing | API endpoint testing |
| Dependencies | Frontend dev server | Backend + Keycloak |
| Test type | Visual, interaction | HTTP request/response |

**Rationale:** Mixing API and E2E tests in one configuration creates confusion and unnecessary dependencies. They are conceptually different testing layers.

#### OS-2: Database Seeding and Test Data

Setting up test data in the database is **not** in scope. Tests should:
- Work against the default Keycloak realm with pre-configured users
- Not require database pre-population beyond what migrations provide
- Not include database fixtures or factory patterns

**Rationale:** Database seeding adds complexity and couples tests to specific data states. API tests should focus on endpoint behavior, not data management.

#### OS-3: Performance and Load Testing

Playwright API tests are for **functional correctness**, not:
- Performance benchmarking
- Load testing
- Stress testing
- Response time SLAs

**Rationale:** Performance testing requires specialized tools (k6, Locust, etc.) and different test design patterns.

#### OS-4: Complex Multi-Tenant Isolation Testing

While the template supports multi-tenancy, comprehensive tenant isolation testing is **not** included:
- Cross-tenant data access verification
- Tenant switching scenarios
- Complex tenant hierarchies
- Tenant-specific rate limiting

**Rationale:** Multi-tenant isolation is security-critical and requires project-specific understanding of data models and access patterns.

#### OS-5: CI/CD Pipeline Configuration

Specific CI/CD configurations are **not** included:
- GitHub Actions workflows
- GitLab CI configuration
- CircleCI, Jenkins, or other CI systems
- Docker-based test execution in CI

**Rationale:** CI/CD configurations are highly project-specific and depend on infrastructure choices made after project generation.

#### OS-6: Browser-Based Authentication Flow Testing

Testing the Keycloak login UI or PKCE flow through a browser is **not** in scope:
- Login form interactions
- OAuth redirect handling
- Session management in browser
- Logout flows

**Rationale:** These are frontend concerns handled by the existing frontend E2E test infrastructure.

#### OS-7: Mocking or Stubbing External Services

The test infrastructure does **not** include:
- Mock servers for Keycloak
- Backend API mocking
- Network stubbing utilities

**Rationale:** Integration tests should run against real services in the development environment. Unit tests with mocking are handled by backend pytest and frontend Vitest suites.

---

### Phase Boundaries

This feature is scoped as a **single-phase implementation** with no planned follow-up phases. However, the design allows for future extensions:

#### Possible Future Extensions (Not In Current Scope)

1. **WebSocket Testing Support** - If the backend adds WebSocket endpoints
2. **GraphQL Testing Patterns** - If GraphQL is added to the API layer
3. **Contract Testing Integration** - Pact or similar consumer-driven contract testing
4. **Visual API Documentation Testing** - OpenAPI spec validation
5. **Cross-Service Testing** - For microservices architectures

These extensions would be separate features with their own FRDs.

---

### Related Features (Separate Concerns)

The following are related but distinct features:

1. **Backend pytest Integration Testing** - Uses `httpx` test client, runs in Python, tests with mocked JWT tokens. Located in `backend/tests/integration/`.

2. **Frontend Vitest Unit Testing** - Tests Lit components in isolation. Located in `frontend/src/**/*.test.ts`.

3. **Frontend Playwright E2E Testing** - Browser-based UI testing. Located in `frontend/e2e/`.

4. **Keycloak Realm Export/Import** - Automating realm configuration. Located in `keycloak/`.

These features complement but do not overlap with the Playwright API testing infrastructure.

---

## User Stories / Use Cases

This section defines concrete scenarios that illustrate how developers will interact with the Playwright API testing infrastructure. Each user story follows the format: **As a [role], I want [capability], so that [benefit]**.

---

### Primary Actor: Backend Developer

#### US-1: Running API Tests for the First Time

**As a** backend developer who just cloned a project generated from the template,
**I want to** run API tests with minimal setup,
**So that** I can verify the backend is functioning correctly before making changes.

**Acceptance Criteria:**
- Developer runs `make test-install` to install Playwright dependencies (one-time setup)
- Developer runs `make test-api` from project root to execute all API tests
- Tests complete within 60 seconds for the default test suite
- Test output clearly shows pass/fail status for each test
- Failed tests provide actionable error messages

**Example Workflow:**
```bash
# First time setup
make test-install

# Run API tests (requires Docker services running)
make docker-up
make test-api
```

**Pre-conditions:**
- Docker services (Keycloak, Backend) are running
- Keycloak realm is configured with test users

**Post-conditions:**
- Developer sees test results in terminal
- HTML report is generated in `playwright/playwright-report/`

---

#### US-2: Testing a Protected Endpoint with Authentication

**As a** backend developer implementing a new protected endpoint,
**I want to** write a test that authenticates as a specific user,
**So that** I can verify the endpoint correctly validates JWT tokens.

**Acceptance Criteria:**
- Developer can use pre-configured fixtures for authenticated requests
- No manual token management required in test code
- Test clearly demonstrates authenticated access patterns

**Example Test:**
```javascript
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test('authenticated user can access protected endpoint', async ({ userRequest }) => {
  const response = await userRequest.get('/protected');

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.user.username).toBe('testuser');
});
```

**Pre-conditions:**
- `testuser` exists in Keycloak with valid credentials
- Protected endpoint requires JWT authentication

**Post-conditions:**
- Test passes when endpoint correctly validates token
- Test fails with clear error if authentication is misconfigured

---

#### US-3: Testing Role-Based Access Control (Positive Case)

**As a** backend developer implementing an admin-only feature,
**I want to** verify that users with the admin role can access the endpoint,
**So that** I can confirm my role-based security is working correctly.

**Acceptance Criteria:**
- Admin user can successfully access admin-only endpoints
- Response includes user information confirming admin role
- Test demonstrates the expected success pattern

**Example Test:**
```javascript
test('admin can access admin endpoint', async ({ adminRequest }) => {
  const response = await adminRequest.get('/admin');

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.user.roles).toContain('admin');
});
```

**Pre-conditions:**
- `admin` user has `admin` role in Keycloak
- `/admin` endpoint requires `admin` role

**Post-conditions:**
- Test passes when role check is correctly implemented
- Test clearly shows role verification in assertions

---

#### US-4: Testing Role-Based Access Control (Negative Case)

**As a** backend developer implementing an admin-only feature,
**I want to** verify that non-admin users are denied access,
**So that** I can confirm unauthorized users cannot access restricted functionality.

**Acceptance Criteria:**
- Non-admin user receives 403 Forbidden response
- Error response includes clear message about missing role
- Test demonstrates the expected denial pattern

**Example Test:**
```javascript
test('regular user cannot access admin endpoint', async ({ userRequest }) => {
  const response = await userRequest.get('/admin');

  expect(response.status()).toBe(403);
  const data = await response.json();
  expect(data.detail).toContain("Role 'admin' required");
});
```

**Pre-conditions:**
- `testuser` does NOT have `admin` role
- `/admin` endpoint requires `admin` role

**Post-conditions:**
- Test passes when role denial is correctly implemented
- Test fails if non-admin users can access the endpoint

---

#### US-5: Testing Unauthenticated Access Denial

**As a** backend developer,
**I want to** verify that protected endpoints reject unauthenticated requests,
**So that** I can confirm the security layer is active.

**Acceptance Criteria:**
- Requests without Authorization header receive 401 or 403 response
- Error message indicates authentication is required
- Test uses raw `request` context (no authentication)

**Example Test:**
```javascript
const { test, expect } = require('@playwright/test');

test('protected endpoint rejects unauthenticated requests', async ({ request }) => {
  const response = await request.get('/protected');

  expect(response.status()).toBe(403);
});
```

**Pre-conditions:**
- `/protected` endpoint requires authentication

**Post-conditions:**
- Test confirms security is enforced for unauthenticated requests

---

#### US-6: Comparing Multiple User Roles in a Single Test

**As a** backend developer testing complex permission scenarios,
**I want to** test multiple user roles within a single test case,
**So that** I can verify permission boundaries in one coherent scenario.

**Acceptance Criteria:**
- Single test can access multiple authenticated contexts
- All user contexts are available via `authenticatedRequest` fixture
- Test clearly demonstrates permission differences between roles

**Example Test:**
```javascript
test('permission boundaries between admin and regular user', async ({ authenticatedRequest }) => {
  // Admin can access admin endpoint
  const adminResponse = await authenticatedRequest.admin.get('/admin');
  expect(adminResponse.ok()).toBeTruthy();

  // Regular user cannot access admin endpoint
  const userResponse = await authenticatedRequest.user.get('/admin');
  expect(userResponse.status()).toBe(403);

  // Both can access protected endpoint
  const adminProtected = await authenticatedRequest.admin.get('/protected');
  const userProtected = await authenticatedRequest.user.get('/protected');
  expect(adminProtected.ok()).toBeTruthy();
  expect(userProtected.ok()).toBeTruthy();
});
```

**Pre-conditions:**
- All test users are configured in Keycloak
- Endpoint permissions are correctly implemented

**Post-conditions:**
- Test verifies the complete permission matrix for the endpoints

---

### Secondary Actor: QA Engineer / Test Writer

#### US-7: Writing Tests with Manual Authentication (Advanced)

**As a** QA engineer writing custom authentication tests,
**I want to** manually control the authentication flow,
**So that** I can test edge cases like expired tokens or invalid credentials.

**Acceptance Criteria:**
- Auth helper functions are accessible for manual token retrieval
- Token can be used directly with `authHeader()` utility
- Developer has full control over authentication headers

**Example Test:**
```javascript
const { test, expect } = require('@playwright/test');
const { getAccessToken, authHeader } = require('./auth-helper');

test('test with manually retrieved token', async ({ request }) => {
  // Get token for any user
  const token = await getAccessToken(request, 'manager', 'manager123');

  const response = await request.get('/protected', {
    headers: authHeader(token),
  });

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.user.username).toBe('manager');
  expect(data.user.roles).toContain('manager');
});
```

**Pre-conditions:**
- User credentials are known
- Keycloak is accessible for token exchange

**Post-conditions:**
- Token is successfully retrieved and used
- Developer understands the underlying auth mechanism

---

#### US-8: Testing Invalid Token Handling

**As a** QA engineer testing security edge cases,
**I want to** verify the API correctly rejects malformed or invalid tokens,
**So that** I can confirm the security layer handles attack vectors properly.

**Acceptance Criteria:**
- Invalid token format results in 401 response
- Expired token results in 401 response
- Malformed JWT results in clear error response
- Tests cover common token manipulation scenarios

**Example Tests:**
```javascript
test('should reject invalid token format', async ({ request }) => {
  const response = await request.get('/protected', {
    headers: { 'Authorization': 'Bearer invalid.token.here' },
  });

  expect(response.status()).toBe(401);
});

test('should reject expired/malformed JWT', async ({ request }) => {
  // Fake JWT with invalid signature
  const fakeToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0In0.invalidsig';

  const response = await request.get('/protected', {
    headers: { 'Authorization': `Bearer ${fakeToken}` },
  });

  expect(response.status()).toBe(401);
});
```

**Pre-conditions:**
- Backend validates JWT tokens against Keycloak public keys

**Post-conditions:**
- Security edge cases are documented through tests

---

#### US-9: Testing Public Endpoints (No Authentication)

**As a** developer testing public API endpoints,
**I want to** verify endpoints that don't require authentication,
**So that** I can confirm public APIs are accessible to all clients.

**Acceptance Criteria:**
- Health check and root endpoints respond without authentication
- Response format matches API specification
- Tests use unauthenticated `request` context

**Example Tests:**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('Public API Endpoints', () => {
  test('GET / returns hello world', async ({ request }) => {
    const response = await request.get('/');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('message', 'Hello World');
  });

  test('GET /health returns healthy status', async ({ request }) => {
    const response = await request.get('/health');

    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data).toHaveProperty('status', 'healthy');
  });
});
```

**Pre-conditions:**
- Backend server is running
- Public endpoints are correctly configured

**Post-conditions:**
- Public API contract is verified

---

### Tertiary Actor: DevOps / New Team Member

#### US-10: Understanding Available Test Users

**As a** new team member unfamiliar with the test infrastructure,
**I want to** quickly understand what test users are available and their roles,
**So that** I can write tests with appropriate user contexts.

**Acceptance Criteria:**
- README documents all test users with credentials and roles
- Test user module exports user information programmatically
- Helper functions allow querying users by role

**Example Usage:**
```javascript
const { TEST_USERS, getUserByRole, getUsersByRole } = require('./test-users');

// Get specific user
console.log(TEST_USERS.admin);
// { username: 'admin', password: 'admin123', roles: ['user', 'admin'], ... }

// Find user by role
const serviceUser = getUserByRole('service');
// Returns service-account user

// Find all users with a role
const usersWithUserRole = getUsersByRole('user');
// Returns array of users that have 'user' role
```

**Reference: Available Test Users**

| Fixture Key | Username | Password | Roles | Purpose |
|-------------|----------|----------|-------|---------|
| `admin` | admin | admin123 | user, admin | Full administrative access testing |
| `user` | testuser | test123 | user | Standard user permission testing |
| `readOnly` | readonly | readonly123 | user, readonly | Read-only access control testing |
| `newUser` | newuser | newuser123 | user | Onboarding flow testing |
| `manager` | manager | manager123 | user, manager | Elevated permission testing |
| `serviceAccount` | service-account | service123 | service | API-to-API integration testing |

**Pre-conditions:**
- Test users are documented in README
- Test users exist in Keycloak realm

**Post-conditions:**
- New team members can write tests without asking for credentials

---

#### US-11: Running Tests in Interactive UI Mode

**As a** developer debugging a failing test,
**I want to** run tests in Playwright's interactive UI mode,
**So that** I can step through tests and inspect request/response details.

**Acceptance Criteria:**
- `make test-ui` launches Playwright's UI mode
- Developer can select and run individual tests
- Request/response details are visible in the UI
- Tests can be re-run without restarting

**Example Workflow:**
```bash
# Launch interactive UI mode
make test-ui

# In the UI:
# 1. Select test file from sidebar
# 2. Click play to run specific test
# 3. View request/response in trace viewer
# 4. Modify test code and re-run
```

**Pre-conditions:**
- Playwright UI is installed
- Docker services are running

**Post-conditions:**
- Developer can efficiently debug failing tests

---

#### US-12: Viewing Test Reports After CI Run

**As a** developer reviewing test results after a CI run,
**I want to** open the HTML test report,
**So that** I can see detailed results including any failures.

**Acceptance Criteria:**
- `make test-report` opens the HTML report in default browser
- Report shows all test results with pass/fail status
- Failed tests include error messages and stack traces
- Report includes request/response details for debugging

**Example Workflow:**
```bash
# Run tests (generates report)
make test-api

# Open report in browser
make test-report
```

**Pre-conditions:**
- Tests have been run at least once
- HTML reporter is configured in playwright.config.js

**Post-conditions:**
- Developer can review comprehensive test results

---

### Edge Case Scenarios

#### US-13: Testing Service-to-Service Communication

**As a** developer implementing service-to-service API calls,
**I want to** test with a service account that has only `service` role,
**So that** I can verify service-level authentication works correctly.

**Acceptance Criteria:**
- Service account has distinct role (`service`) without `user` role
- Tests can use `authenticatedRequest.serviceAccount` context
- Service account can access service-level endpoints

**Example Test:**
```javascript
test('service account can authenticate', async ({ authenticatedRequest }) => {
  const response = await authenticatedRequest.serviceAccount.get('/protected');

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.user.username).toBe('service-account');
  expect(data.user.roles).toContain('service');
  expect(data.user.roles).not.toContain('user');
});
```

**Pre-conditions:**
- Service account configured with only `service` role
- Backend accepts `service` role for service-level endpoints

**Post-conditions:**
- Service-to-service authentication is verified

---

#### US-14: Testing New User Onboarding Flow

**As a** developer testing first-time user experiences,
**I want to** use a test account specifically for onboarding scenarios,
**So that** tests don't conflict with established user data.

**Acceptance Criteria:**
- `newUser` fixture provides a fresh user context
- User has minimal role assignments (just `user`)
- Account is suitable for testing first-login flows

**Example Test:**
```javascript
test('new user sees onboarding state', async ({ authenticatedRequest }) => {
  const response = await authenticatedRequest.newUser.get('/user/profile');

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  // Verify onboarding flags or incomplete profile state
  expect(data.user.username).toBe('newuser');
});
```

**Pre-conditions:**
- `newuser` account exists with basic `user` role
- Onboarding logic is implemented in backend

**Post-conditions:**
- Onboarding flows can be tested without affecting other test users

---

#### US-15: Accessing Token and User Info from Fixtures

**As a** developer writing advanced tests,
**I want to** access the raw token and user information from fixtures,
**So that** I can use them in custom scenarios (e.g., WebSocket auth, custom headers).

**Acceptance Criteria:**
- Fixtures expose `.token` property with the JWT
- Fixtures expose `.user` property with user metadata
- Token can be used for non-HTTP authentication scenarios

**Example Test:**
```javascript
test('can access raw token for custom scenarios', async ({ adminRequest }) => {
  // Access user info
  expect(adminRequest.user.username).toBe('admin');
  expect(adminRequest.user.roles).toContain('admin');

  // Access raw token for custom use
  expect(adminRequest.token).toBeTruthy();
  expect(typeof adminRequest.token).toBe('string');

  // Use token in custom scenario (e.g., WebSocket)
  // const ws = new WebSocket(`wss://api.example.com?token=${adminRequest.token}`);
});
```

**Pre-conditions:**
- Fixtures are configured to expose token and user

**Post-conditions:**
- Developers can use tokens in non-standard scenarios

---

### Use Case Summary Matrix

| Use Case | Actor | Fixture Used | HTTP Methods | Key Assertions |
|----------|-------|--------------|--------------|----------------|
| US-1 | Backend Dev | N/A | N/A | CLI output verification |
| US-2 | Backend Dev | `userRequest` | GET | `response.ok()`, user data |
| US-3 | Backend Dev | `adminRequest` | GET | `response.ok()`, role verification |
| US-4 | Backend Dev | `userRequest` | GET | `response.status() === 403` |
| US-5 | Backend Dev | `request` (raw) | GET | `response.status() === 403` |
| US-6 | Backend Dev | `authenticatedRequest` | GET | Multiple role comparisons |
| US-7 | QA Engineer | Manual auth | GET | Custom token handling |
| US-8 | QA Engineer | `request` (raw) | GET | 401 status, error messages |
| US-9 | Developer | `request` (raw) | GET | Public endpoint verification |
| US-10 | New Member | N/A | N/A | Documentation reference |
| US-11 | Developer | Any | Any | Interactive debugging |
| US-12 | Developer | N/A | N/A | Report viewing |
| US-13 | Backend Dev | `authenticatedRequest.serviceAccount` | GET | Service role verification |
| US-14 | Backend Dev | `authenticatedRequest.newUser` | GET | Onboarding state |
| US-15 | Backend Dev | `adminRequest` | N/A | Token/user access |

---

## Functional Requirements

This section defines atomic, testable requirements for the Playwright API testing infrastructure. Requirements are organized by functional area and prioritized using MoSCoW notation (Must Have, Should Have, Nice to Have).

---

### FR-1: Directory Structure and Project Configuration

#### FR-1.1: Playwright Directory Location (Must Have)

The template SHALL create a `playwright/` directory at the project root level, parallel to `frontend/` and `backend/`.

**Acceptance Criteria:**
- Directory path: `{{ cookiecutter.project_slug }}/playwright/`
- Directory is created during `cookiecutter` project generation
- Directory is independent from `frontend/e2e/` (no shared configuration)

**Verification:** After project generation, `ls -la` shows `playwright/` directory at root.

---

#### FR-1.2: Package Configuration (Must Have)

The template SHALL create a `playwright/package.json` file with the following configuration:

| Field | Value |
|-------|-------|
| `name` | `"playwright"` |
| `type` | `"commonjs"` |
| `testDir` | `"tests"` |

**npm Scripts:**

| Script | Command | Description |
|--------|---------|-------------|
| `test` | `playwright test` | Run all tests |
| `test:api` | `playwright test --project='API Tests'` | Run API tests only |
| `test:headed` | `playwright test --headed` | Run with visible browser (for debugging) |
| `test:debug` | `playwright test --debug` | Run in debug mode |
| `test:ui` | `playwright test --ui` | Run in interactive UI mode |
| `report` | `playwright show-report` | Open HTML test report |

**Dependencies:**

| Package | Version | Type |
|---------|---------|------|
| `@playwright/test` | `^1.56.0` (or latest stable) | devDependency |

**Acceptance Criteria:**
- `npm install` in `playwright/` directory succeeds
- All npm scripts execute without errors when services are running
- `npm test` runs Playwright test suite

**Verification:** `cd playwright && npm install && npm test` completes successfully.

---

#### FR-1.3: Playwright Configuration (Must Have)

The template SHALL create a `playwright/playwright.config.js` file with the following settings:

**Core Settings:**

| Setting | Value | Rationale |
|---------|-------|-----------|
| `testDir` | `'./tests'` | Matches package.json scripts |
| `timeout` | `30000` | 30 seconds per test (sufficient for auth + request) |
| `fullyParallel` | `true` | Maximize test execution speed |
| `forbidOnly` | `!!process.env.CI` | Prevent `.only()` in CI |
| `retries` | `process.env.CI ? 2 : 0` | Retry flaky tests in CI only |
| `workers` | `process.env.CI ? 1 : undefined` | Single worker in CI for stability |
| `reporter` | `'html'` | Generate HTML reports |

**Use Settings:**

| Setting | Value | Rationale |
|---------|-------|-----------|
| `baseURL` | `process.env.BASE_URL \|\| 'http://localhost:{{ cookiecutter.backend_port }}'` | Point to backend API |
| `trace` | `'on-first-retry'` | Collect traces only on retry for debugging |
| `extraHTTPHeaders.Accept` | `'application/json'` | API testing default |

**Projects:**

| Project Name | Test Match Pattern | Purpose |
|--------------|-------------------|---------|
| `API Tests` | `/.*\.api\.spec\.js/` | Match API test files |

**Web Server (Development Only):**

| Setting | Value | Notes |
|---------|-------|-------|
| `command` | `'cd .. && make docker-up'` | Start services if not running |
| `url` | `'http://localhost:{{ cookiecutter.backend_port }}/health'` | Health check endpoint |
| `timeout` | `120 * 1000` | 2 minutes for Docker startup |
| `reuseExistingServer` | `!process.env.CI` | Don't restart if already running |

**Acceptance Criteria:**
- Configuration uses cookiecutter variables for ports
- `BASE_URL` environment variable overrides default
- Tests match `*.api.spec.js` pattern
- Web server configuration only applies in development

**Verification:** `npx playwright test --list` shows correct project configuration.

---

#### FR-1.4: Git Ignore Configuration (Must Have)

The template SHALL create a `playwright/.gitignore` file that excludes:

```gitignore
node_modules/
playwright-report/
test-results/
playwright/.cache/
*.log
```

**Acceptance Criteria:**
- Playwright artifacts are not committed to version control
- `node_modules` is ignored
- HTML reports and test results are ignored

**Verification:** `git status` does not show ignored files after test execution.

---

### FR-2: Authentication Helper Module

#### FR-2.1: Auth Helper File (Must Have)

The template SHALL create `playwright/tests/auth-helper.js` with the following exports:

**Constants (Configurable via Environment Variables):**

| Constant | Environment Variable | Default Value |
|----------|---------------------|---------------|
| `KEYCLOAK_URL` | `KEYCLOAK_URL` | `'http://localhost:{{ cookiecutter.keycloak_port }}'` |
| `KEYCLOAK_REALM` | `KEYCLOAK_REALM` | `'{{ cookiecutter.keycloak_realm_name }}'` |
| `CLIENT_ID` | (hardcoded) | `'{{ cookiecutter.keycloak_backend_client_id }}'` |
| `CLIENT_SECRET` | (hardcoded) | `'{{ cookiecutter.keycloak_backend_client_id }}-secret'` |

**Acceptance Criteria:**
- Default values use cookiecutter template variables
- Environment variables override defaults for CI/CD flexibility
- Client ID and secret match Keycloak realm setup script

---

#### FR-2.2: getAccessToken Function (Must Have)

The template SHALL implement an async function `getAccessToken(request, username, password)` that:

1. Constructs token endpoint URL: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`
2. Makes POST request with form data:
   - `grant_type`: `'password'`
   - `client_id`: `CLIENT_ID`
   - `client_secret`: `CLIENT_SECRET`
   - `username`: provided username
   - `password`: provided password
3. Returns `access_token` from response on success
4. Throws descriptive error on failure including HTTP status and response body

**Function Signature:**
```javascript
async function getAccessToken(request, username, password)
// @param {import('@playwright/test').APIRequestContext} request
// @param {string} username
// @param {string} password
// @returns {Promise<string>} Access token
// @throws {Error} If authentication fails
```

**Acceptance Criteria:**
- Returns valid JWT access token on successful authentication
- Error message includes HTTP status code and response text
- Works with Playwright's `request` context

**Verification:** Token can be used to access protected endpoints.

---

#### FR-2.3: Convenience Token Functions (Should Have)

The template SHALL implement convenience functions for common test users:

| Function | Username | Password | Purpose |
|----------|----------|----------|---------|
| `getAdminToken(request)` | `'admin'` | `'admin123'` | Quick admin access |
| `getTestUserToken(request)` | `'testuser'` | `'test123'` | Quick user access |

**Acceptance Criteria:**
- Functions call `getAccessToken` with hardcoded credentials
- No additional parameters required beyond `request`

---

#### FR-2.4: Authorization Header Builder (Must Have)

The template SHALL implement a function `authHeader(token)` that:

1. Takes a JWT token string as input
2. Returns an object: `{ 'Authorization': 'Bearer ${token}' }`

**Function Signature:**
```javascript
function authHeader(token)
// @param {string} token - JWT access token
// @returns {{ Authorization: string }} Header object
```

**Acceptance Criteria:**
- Returns object suitable for spreading into `headers` option
- Format matches expected Bearer token format

---

#### FR-2.5: Module Exports (Must Have)

The `auth-helper.js` module SHALL export:

```javascript
module.exports = {
  getAccessToken,
  getAdminToken,
  getTestUserToken,
  authHeader,
  KEYCLOAK_URL,
  KEYCLOAK_REALM,
};
```

**Acceptance Criteria:**
- All functions and constants are importable
- `require('./auth-helper')` works from test files

---

### FR-3: Test User Fixtures Module

#### FR-3.1: Test Users File (Must Have)

The template SHALL create `playwright/tests/test-users.js` with a `TEST_USERS` object containing 6 pre-configured users.

**User Definitions:**

| Key | Username | Password | Email | Roles | Description |
|-----|----------|----------|-------|-------|-------------|
| `admin` | `admin` | `admin123` | `admin@example.com` | `['user', 'admin']` | Full admin access |
| `user` | `testuser` | `test123` | `test@example.com` | `['user']` | Standard user |
| `readOnly` | `readonly` | `readonly123` | `readonly@example.com` | `['user', 'readonly']` | Read-only access |
| `newUser` | `newuser` | `newuser123` | `newuser@example.com` | `['user']` | Fresh account for onboarding |
| `manager` | `manager` | `manager123` | `manager@example.com` | `['user', 'manager']` | Elevated permissions |
| `serviceAccount` | `service-account` | `service123` | `service@example.com` | `['service']` | API-to-API integration |

**Acceptance Criteria:**
- All 6 users are defined with consistent structure
- Password pattern: `username + '123'` for easy memorization
- Roles array accurately reflects Keycloak configuration
- Description explains purpose for documentation

---

#### FR-3.2: User Query Functions (Should Have)

The template SHALL implement helper functions:

**getUserByRole(role):**
- Returns first user object that has the specified role
- Returns `undefined` if no user has the role

**getUsersByRole(role):**
- Returns array of all user objects that have the specified role
- Returns empty array if no users have the role

**getAllUsers():**
- Returns array of all user objects

**Acceptance Criteria:**
- Functions enable programmatic user selection in tests
- Role matching uses `Array.includes()`

---

#### FR-3.3: Module Exports (Must Have)

The `test-users.js` module SHALL export:

```javascript
module.exports = {
  TEST_USERS,
  getUserByRole,
  getUsersByRole,
  getAllUsers,
};
```

---

### FR-4: Playwright Extended Fixtures

#### FR-4.1: Fixtures File (Must Have)

The template SHALL create `playwright/tests/fixtures.js` that extends Playwright's base `test` fixture with authenticated request contexts.

**Import Requirements:**
```javascript
const { test as base } = require('@playwright/test');
const { getAccessToken, authHeader } = require('./auth-helper');
const { TEST_USERS } = require('./test-users');
```

---

#### FR-4.2: authenticatedRequest Fixture (Must Have)

The fixture SHALL provide an `authenticatedRequest` object with pre-authenticated contexts for all test users.

**Behavior:**
1. For each user in `TEST_USERS`, obtain access token during fixture setup
2. Create a wrapper object for each user with methods: `get`, `post`, `put`, `patch`, `delete`
3. Each method automatically includes `Authorization: Bearer <token>` header
4. Each method merges user-provided headers with auth header (user headers take precedence)
5. Expose `user` (user object) and `token` (raw JWT) properties for advanced scenarios

**Fixture Shape:**
```javascript
authenticatedRequest: {
  admin: { get, post, put, patch, delete, user, token },
  user: { get, post, put, patch, delete, user, token },
  readOnly: { get, post, put, patch, delete, user, token },
  newUser: { get, post, put, patch, delete, user, token },
  manager: { get, post, put, patch, delete, user, token },
  serviceAccount: { get, post, put, patch, delete, user, token },
}
```

**Acceptance Criteria:**
- All 6 user contexts are available
- HTTP methods match Playwright's `request` API signature
- Authentication is transparent to test code
- Custom headers can be added alongside auth header

---

#### FR-4.3: Convenience Request Fixtures (Should Have)

The template SHALL provide shorthand fixtures for frequently used contexts:

| Fixture Name | Delegates To |
|--------------|--------------|
| `adminRequest` | `authenticatedRequest.admin` |
| `userRequest` | `authenticatedRequest.user` |
| `readOnlyRequest` | `authenticatedRequest.readOnly` |
| `managerRequest` | `authenticatedRequest.manager` |

**Acceptance Criteria:**
- Fixtures use `authenticatedRequest` internally (no duplicate token fetching)
- Tests can destructure: `async ({ adminRequest }) => { ... }`

---

#### FR-4.4: Module Exports (Must Have)

The `fixtures.js` module SHALL export the extended test function:

```javascript
module.exports = { test };
```

**Acceptance Criteria:**
- Tests import: `const { test } = require('./fixtures');`
- Standard `expect` is imported from `@playwright/test`

---

### FR-5: Example Test Suites

#### FR-5.1: Basic API Tests (Must Have)

The template SHALL create `playwright/tests/api-endpoints.api.spec.js` demonstrating manual authentication patterns.

**Required Test Cases:**

| Test Suite | Test Name | Endpoint | Auth | Expected |
|------------|-----------|----------|------|----------|
| Public API Endpoints | GET / should return hello world | `/` | None | 200, `{ message: 'Hello World' }` |
| Public API Endpoints | GET /health should return healthy status | `/health` | None | 200, `{ status: 'healthy' }` |
| Protected API Endpoints | GET /protected should fail without token | `/protected` | None | 403 |
| Protected API Endpoints | GET /protected should succeed with valid admin token | `/protected` | Admin | 200, user info in response |
| Protected API Endpoints | GET /protected should succeed with valid user token | `/protected` | User | 200, user info in response |
| Admin-Only API Endpoints | GET /admin should fail without token | `/admin` | None | 403 |
| Admin-Only API Endpoints | GET /admin should succeed with admin token | `/admin` | Admin | 200, admin role verified |
| Admin-Only API Endpoints | GET /admin should fail with regular user token | `/admin` | User | 403, error includes role requirement |
| Token Validation | should reject invalid token format | `/protected` | Invalid | 401 |
| Token Validation | should reject expired or malformed tokens | `/protected` | Fake JWT | 401 |

**Acceptance Criteria:**
- Uses `getAdminToken`, `getTestUserToken`, `authHeader` from `auth-helper.js`
- Demonstrates manual token retrieval pattern
- Includes descriptive test suite names with `test.describe()`
- Asserts on both status codes and response body content

---

#### FR-5.2: Fixture-Based API Tests (Must Have)

The template SHALL create `playwright/tests/api-with-fixtures.api.spec.js` demonstrating the recommended fixture pattern.

**Required Test Cases:**

| Test Suite | Test Name | Fixture Used | Scenario |
|------------|-----------|--------------|----------|
| API Tests with Fixtures | admin can access admin endpoint using adminRequest fixture | `adminRequest` | Admin access success |
| API Tests with Fixtures | regular user can access protected endpoint using userRequest fixture | `userRequest` | User access success |
| API Tests with Fixtures | regular user cannot access admin endpoint | `userRequest` | Role denial |
| API Tests with Fixtures | can access multiple user contexts in same test | `authenticatedRequest` | Compare admin vs user |
| API Tests with Fixtures | readonly user has proper role assignment | `readOnlyRequest` | Role verification |
| API Tests with Fixtures | can access user info and token from fixture | `adminRequest` | Token/user metadata |
| API Tests with Fixtures | POST request with authenticated context | `userRequest` | Non-GET method demo |
| Test User Scenarios | newUser fixture for testing onboarding flows | `authenticatedRequest.newUser` | New user context |
| Test User Scenarios | serviceAccount fixture for API integration tests | `authenticatedRequest.serviceAccount` | Service account context |

**Acceptance Criteria:**
- Imports `test` from `./fixtures` (not `@playwright/test`)
- Imports `expect` from `@playwright/test`
- Uses fixture destructuring: `async ({ adminRequest }) => { ... }`
- Includes documentation comments explaining patterns
- Demonstrates accessing `user` and `token` properties

---

### FR-6: Keycloak Test User Setup

#### FR-6.1: Realm Setup Script Updates (Must Have)

The template SHALL update `keycloak/setup-realm.sh` to create all 6 test users required for Playwright tests.

**Users to Create:**

| Username | Email | First Name | Last Name | Tenant ID | Password |
|----------|-------|------------|-----------|-----------|----------|
| `admin` | `admin@example.com` | Admin | User | `tenant-1` | `admin123` |
| `testuser` | `test@example.com` | Test | User | `tenant-1` | `test123` |
| `readonly` | `readonly@example.com` | Readonly | User | `tenant-1` | `readonly123` |
| `newuser` | `newuser@example.com` | New | User | `tenant-1` | `newuser123` |
| `manager` | `manager@example.com` | Manager | User | `tenant-1` | `manager123` |
| `service-account` | `service@example.com` | Service | Account | `tenant-1` | `service123` |

**Role Assignments:**

| Username | Roles |
|----------|-------|
| `admin` | `user`, `admin` |
| `testuser` | `user` |
| `readonly` | `user`, `readonly` |
| `newuser` | `user` |
| `manager` | `user`, `manager` |
| `service-account` | `service` |

**Acceptance Criteria:**
- Script creates all 6 users when executed
- Role assignments match `test-users.js` definitions
- Passwords follow the `username + '123'` pattern
- Script is idempotent (can run multiple times without error)

---

#### FR-6.2: Realm Role Creation (Must Have)

The setup script SHALL create the following realm roles before assigning them to users:

| Role Name | Description |
|-----------|-------------|
| `user` | Standard user access |
| `admin` | Administrative access |
| `readonly` | Read-only access to resources |
| `manager` | Manager-level permissions |
| `service` | Service account for API integration |

**Acceptance Criteria:**
- All roles exist in Keycloak realm
- Roles can be assigned to users
- Backend can validate these roles from JWT tokens

---

### FR-7: Documentation

#### FR-7.1: README.md (Must Have)

The template SHALL create `playwright/README.md` with the following sections:

1. **Overview**: Purpose of the API testing infrastructure
2. **Prerequisites**: Required services (Docker, Keycloak, Backend)
3. **Setup**: Installation instructions (`npm install`)
4. **Running Tests**: Commands for different test modes
5. **Test Structure**: Directory layout explanation
6. **Writing Tests**:
   - Recommended pattern (fixtures)
   - Advanced pattern (manual auth)
7. **Available Fixtures**: Table of all fixtures with descriptions
8. **Test Users**: Table of all test users with credentials and roles
9. **Environment Variables**: Configuration options
10. **Troubleshooting**: Common issues and solutions

**Acceptance Criteria:**
- All sections contain substantive content
- Code examples are included and accurate
- References to cookiecutter variables are resolved
- Test user credentials are clearly documented

---

#### FR-7.2: QUICK_START.md (Should Have)

The template SHALL create `playwright/QUICK_START.md` with a concise 5-minute guide:

1. Prerequisites check
2. Install dependencies (`make test-install` or `npm install`)
3. Start services (`make docker-up`)
4. Run tests (`make test-api` or `npm test`)
5. View report (`make test-report`)

**Acceptance Criteria:**
- Can be followed in under 5 minutes
- Uses Makefile commands when available
- Includes expected output snippets

---

### FR-8: Makefile Integration

#### FR-8.1: Test Targets (Must Have)

The template's root `Makefile` SHALL include the following Playwright-related targets:

| Target | Command | Description |
|--------|---------|-------------|
| `test` | `cd playwright && npm test` | Run all Playwright tests |
| `test-api` | `cd playwright && npm run test:api` | Run API tests only |
| `test-ui` | `cd playwright && npm run test:ui` | Run tests in interactive UI mode |
| `test-debug` | `cd playwright && npm run test:debug` | Run tests in debug mode |
| `test-report` | `cd playwright && npm run report` | Open HTML test report |
| `test-install` | `cd playwright && npm install` | Install Playwright dependencies |

**Acceptance Criteria:**
- All targets work from project root directory
- Targets are included in `.PHONY` declaration
- Targets have help text (comment with `##`)

---

#### FR-8.2: Help Text Integration (Should Have)

The Makefile `help` target SHALL include a "Testing Commands" section that lists all test-related targets.

**Acceptance Criteria:**
- `make help` displays all test targets
- Targets are grouped under a "Testing Commands" heading
- Description text is clear and concise

---

### FR-9: Error Handling and Robustness

#### FR-9.1: Authentication Error Messages (Must Have)

When `getAccessToken()` fails, the error message SHALL include:
- HTTP status code
- Response body text (for debugging)
- Clear indication that authentication failed

**Example Error:**
```
Error: Failed to get token: 401 {"error":"invalid_grant","error_description":"Invalid user credentials"}
```

**Acceptance Criteria:**
- Error message aids debugging without exposing sensitive data
- Status code is clearly visible
- Response text is included for Keycloak error details

---

#### FR-9.2: Fixture Initialization Failure (Should Have)

If any user's token retrieval fails during fixture initialization, the fixture SHALL:
- Fail fast with descriptive error
- Indicate which user's authentication failed
- Suggest checking Keycloak configuration

**Acceptance Criteria:**
- Partial fixture initialization does not occur
- Error message identifies the problematic user
- Tests do not run with incomplete fixtures

---

### FR-10: Non-Functional Requirements

#### FR-10.1: Test Execution Speed (Should Have)

The default test suite (all example tests) SHALL complete within 60 seconds on a standard development machine with all services running.

**Acceptance Criteria:**
- Token caching within fixtures prevents redundant auth requests
- Parallel test execution is enabled by default
- No artificial delays in test code

---

#### FR-10.2: CI/CD Compatibility (Should Have)

The test configuration SHALL support CI/CD environments:
- `CI` environment variable detection
- Single-worker mode in CI for stability
- Retry logic (2 retries) in CI only
- Web server startup disabled in CI (assumes services pre-started)

**Acceptance Criteria:**
- Tests pass in GitHub Actions or similar CI systems
- `CI=true npm test` uses appropriate configuration
- No interactive prompts in CI mode

---

### Requirements Summary Matrix

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-1.1 | Playwright directory at project root | Must Have | Pending |
| FR-1.2 | Package.json configuration | Must Have | Pending |
| FR-1.3 | Playwright configuration | Must Have | Pending |
| FR-1.4 | Git ignore configuration | Must Have | Pending |
| FR-2.1 | Auth helper file with constants | Must Have | Pending |
| FR-2.2 | getAccessToken function | Must Have | Pending |
| FR-2.3 | Convenience token functions | Should Have | Pending |
| FR-2.4 | Authorization header builder | Must Have | Pending |
| FR-2.5 | Auth helper module exports | Must Have | Pending |
| FR-3.1 | Test users file with 6 users | Must Have | Pending |
| FR-3.2 | User query functions | Should Have | Pending |
| FR-3.3 | Test users module exports | Must Have | Pending |
| FR-4.1 | Fixtures file structure | Must Have | Pending |
| FR-4.2 | authenticatedRequest fixture | Must Have | Pending |
| FR-4.3 | Convenience request fixtures | Should Have | Pending |
| FR-4.4 | Fixtures module exports | Must Have | Pending |
| FR-5.1 | Basic API tests (manual auth) | Must Have | Pending |
| FR-5.2 | Fixture-based API tests | Must Have | Pending |
| FR-6.1 | Keycloak test user creation | Must Have | Pending |
| FR-6.2 | Keycloak realm role creation | Must Have | Pending |
| FR-7.1 | README.md documentation | Must Have | Pending |
| FR-7.2 | QUICK_START.md guide | Should Have | Pending |
| FR-8.1 | Makefile test targets | Must Have | Pending |
| FR-8.2 | Makefile help text integration | Should Have | Pending |
| FR-9.1 | Authentication error messages | Must Have | Pending |
| FR-9.2 | Fixture initialization failure | Should Have | Pending |
| FR-10.1 | Test execution speed | Should Have | Pending |
| FR-10.2 | CI/CD compatibility | Should Have | Pending |

**Totals:**
- Must Have: 19 requirements
- Should Have: 9 requirements
- Nice to Have: 0 requirements

---

## Technical Approach

This section describes the high-level technical strategy for implementing Playwright API testing support in the cookiecutter template. The approach is grounded in patterns proven in the implementation-manager reference project.

---

### TA-1: Technology Stack Selection

#### Primary Technologies

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Test Framework | Playwright Test | ^1.56.x | Official API testing support, built-in fixtures, excellent reporting |
| JavaScript Runtime | Node.js | 20.x | Matches template frontend requirements |
| Module System | CommonJS | N/A | Simpler for test files, broader compatibility |
| Package Manager | npm | 10.x | Consistent with template frontend |

#### Why Playwright for API Testing

1. **Unified Testing Experience**: Developers already use Playwright for frontend E2E tests; using it for API tests provides consistency.

2. **Built-in Fixture System**: Playwright's `test.extend()` pattern enables clean, reusable authenticated request contexts without boilerplate.

3. **Excellent Request API**: The `APIRequestContext` provides a clean interface for HTTP requests with automatic JSON handling, form data support, and cookie management.

4. **Native Parallel Execution**: Playwright runs tests in parallel by default, reducing test suite execution time.

5. **Rich Reporting**: HTML reports with request/response details, trace viewer for debugging, and CI-friendly output formats.

6. **Active Development**: Regular updates from Microsoft with strong TypeScript support and documentation.

---

### TA-2: Authentication Strategy

#### OAuth 2.0 Password Grant Flow

The API testing infrastructure uses the OAuth 2.0 Resource Owner Password Credentials (ROPC) grant to obtain access tokens. While ROPC is deprecated for production applications, it is appropriate for testing scenarios where:

- Test users are pre-configured with known credentials
- Tests need programmatic token retrieval without browser interaction
- The identity provider (Keycloak) is under developer control

**Token Retrieval Flow:**

```
Test Setup
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  auth-helper.js: getAccessToken(request, username, password) │
└─────────────────────────────────────────────────────────────┘
    │
    │  POST /realms/{realm}/protocol/openid-connect/token
    │  form: { grant_type: 'password', client_id, client_secret, username, password }
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Keycloak Token Endpoint                    │
└─────────────────────────────────────────────────────────────┘
    │
    │  Response: { access_token, refresh_token, expires_in, ... }
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│  Extract access_token → Return to test fixture               │
└─────────────────────────────────────────────────────────────┘
```

**Implementation Reference:** `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/auth-helper.js`

```javascript
// Core pattern from implementation-manager
async function getAccessToken(request, username, password) {
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
    throw new Error(`Failed to get token: ${response.status()} ${text}`);
  }

  const data = await response.json();
  return data.access_token;
}
```

#### Keycloak Client Configuration

The tests use the backend client credentials, which is configured for `directAccessGrantsEnabled: true` in the Keycloak realm setup. This allows the password grant flow.

**Client Settings Required:**

| Setting | Value | Purpose |
|---------|-------|---------|
| `publicClient` | `false` | Confidential client with secret |
| `directAccessGrantsEnabled` | `true` | Enables password grant |
| `clientId` | `{{ cookiecutter.keycloak_backend_client_id }}` | Matches backend client |
| `secret` | `{{ cookiecutter.keycloak_backend_client_id }}-secret` | Matches realm setup |

---

### TA-3: Fixture Architecture

#### Playwright Test Extension Pattern

The fixture system extends Playwright's base `test` object to provide pre-authenticated request contexts. This approach:

1. **Authenticates Once Per Test**: Each test gets fresh tokens, ensuring test isolation
2. **Provides Multiple User Contexts**: All 6 test users are available via a single fixture
3. **Wraps Playwright's Request API**: Maintains familiar API while adding authorization headers

**Fixture Dependency Graph:**

```
┌───────────────────────────────────────────────────────────────────────────┐
│                              fixtures.js                                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌────────────────┐                                                       │
│  │    request     │ ◄─── Playwright's built-in APIRequestContext         │
│  └────────────────┘                                                       │
│          │                                                                │
│          ▼                                                                │
│  ┌─────────────────────────┐     ┌──────────────┐   ┌───────────────┐    │
│  │ authenticatedRequest    │ ◄── │ auth-helper  │ + │  test-users   │    │
│  ├─────────────────────────┤     └──────────────┘   └───────────────┘    │
│  │ .admin                  │                                              │
│  │ .user                   │                                              │
│  │ .readOnly               │                                              │
│  │ .newUser                │                                              │
│  │ .manager                │                                              │
│  │ .serviceAccount         │                                              │
│  └─────────────────────────┘                                              │
│          │                                                                │
│          ▼                                                                │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────┐           │
│  │  adminRequest  │  │  userRequest   │  │  readOnlyRequest  │  ...      │
│  └────────────────┘  └────────────────┘  └───────────────────┘           │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

**Implementation Reference:** `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/fixtures.js`

```javascript
// Core pattern - extend base test with authenticated contexts
const test = base.extend({
  authenticatedRequest: async ({ request }, use) => {
    const contexts = {};

    for (const [key, user] of Object.entries(TEST_USERS)) {
      const token = await getAccessToken(request, user.username, user.password);

      // Wrapper that injects auth headers
      contexts[key] = {
        get: (url, options = {}) => {
          return request.get(url, {
            ...options,
            headers: { ...authHeader(token), ...options.headers },
          });
        },
        post: (url, options = {}) => {
          return request.post(url, {
            ...options,
            headers: { ...authHeader(token), ...options.headers },
          });
        },
        // ... put, patch, delete
        user,
        token,
      };
    }

    await use(contexts);
  },

  // Convenience fixtures
  adminRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.admin);
  },
  // ... other convenience fixtures
});
```

---

### TA-4: Template Integration Strategy

#### Directory Structure in Template

The Playwright API testing infrastructure will be added as a new top-level directory in the cookiecutter template:

```
template/{{cookiecutter.project_slug}}/
├── backend/                    # Existing
├── frontend/                   # Existing (contains frontend E2E tests)
├── keycloak/                   # Existing (realm setup)
├── playwright/                 # NEW - API testing
│   ├── package.json
│   ├── playwright.config.js
│   ├── .gitignore
│   ├── README.md
│   ├── QUICK_START.md
│   └── tests/
│       ├── auth-helper.js
│       ├── test-users.js
│       ├── fixtures.js
│       ├── api-endpoints.api.spec.js
│       └── api-with-fixtures.api.spec.js
├── compose.yml                 # Existing
└── Makefile                    # Updated with test targets
```

#### Cookiecutter Variable Usage

All configurable values will use cookiecutter template variables to ensure consistency with the rest of the generated project:

| Value | Variable | Example |
|-------|----------|---------|
| Keycloak URL | `{{ cookiecutter.keycloak_port }}` | `http://localhost:8080` |
| Keycloak Realm | `{{ cookiecutter.keycloak_realm_name }}` | `my-project-dev` |
| Backend Client ID | `{{ cookiecutter.keycloak_backend_client_id }}` | `my-project-backend` |
| Backend URL | `{{ cookiecutter.backend_port }}` | `http://localhost:8000` |
| API Prefix | `{{ cookiecutter.backend_api_prefix }}` | `/api/v1` |

**Example: auth-helper.js with template variables:**

```javascript
const KEYCLOAK_URL = process.env.KEYCLOAK_URL || 'http://localhost:{{ cookiecutter.keycloak_port }}';
const KEYCLOAK_REALM = process.env.KEYCLOAK_REALM || '{{ cookiecutter.keycloak_realm_name }}';
const CLIENT_ID = '{{ cookiecutter.keycloak_backend_client_id }}';
const CLIENT_SECRET = '{{ cookiecutter.keycloak_backend_client_id }}-secret';
```

---

### TA-5: Test User Management

#### Test User Source of Truth

Test users are defined in two places that must remain synchronized:

1. **Keycloak Realm Setup Script** (`keycloak/setup-realm.sh`): Creates users in Keycloak
2. **Playwright Test Users Module** (`playwright/tests/test-users.js`): Defines credentials for tests

#### Current Template Users vs. Required Test Users

The current template creates 4 users:
- alice@example.com (tenant-1)
- bob@example.com (tenant-1)
- charlie@demo.example (tenant-2)
- diana@demo.example (tenant-2)

The implementation-manager pattern uses 6 role-focused users:
- admin (user, admin roles)
- testuser (user role)
- readonly (user, readonly roles)
- newuser (user role)
- manager (user, manager roles)
- service-account (service role)

**Recommended Approach:** Update the Keycloak setup script to create both sets of users:

1. **Original tenant-based users**: For multi-tenancy testing (alice, bob, charlie, diana)
2. **Role-based test users**: For RBAC testing (admin, testuser, readonly, newuser, manager, service-account)

This provides flexibility for both role-based API testing and tenant isolation testing.

#### Role Creation in Keycloak

The setup script must create realm roles before assigning them to users:

```bash
# Create realm roles
for ROLE in user admin readonly manager service; do
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$ROLE\"}" \
    "$KEYCLOAK_URL/admin/realms/${REALM}/roles"
done
```

---

### TA-6: Configuration Management

#### Environment Variable Hierarchy

The test infrastructure supports configuration override through environment variables:

```
Default Values (in code)
    ↓ overridden by
Environment Variables
    ↓ used by
Auth Helper / Playwright Config
```

**Supported Environment Variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `BASE_URL` | `http://localhost:{{ cookiecutter.backend_port }}` | Backend API base URL |
| `KEYCLOAK_URL` | `http://localhost:{{ cookiecutter.keycloak_port }}` | Keycloak server URL |
| `KEYCLOAK_REALM` | `{{ cookiecutter.keycloak_realm_name }}` | Keycloak realm name |
| `CI` | (unset) | Triggers CI-specific behavior |

#### Playwright Configuration for API Testing

```javascript
// playwright.config.js pattern
module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',

  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:{{ cookiecutter.backend_port }}',
    trace: 'on-first-retry',
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },
  },

  projects: [
    {
      name: 'API Tests',
      testMatch: /.*\.api\.spec\.js/,
    },
  ],

  // Development only: auto-start services
  webServer: process.env.CI ? undefined : {
    command: 'cd .. && make docker-up',
    url: 'http://localhost:{{ cookiecutter.backend_port }}/health',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI,
  },
});
```

---

### TA-7: API Endpoint Compatibility

#### Template Backend Endpoints

The template's backend uses an API prefix pattern. Endpoints are mounted at `{{ cookiecutter.backend_api_prefix }}`:

| Endpoint | Full Path | Auth Required | Description |
|----------|-----------|---------------|-------------|
| `/` | `/` | No | Root endpoint (service info) |
| `/health` | `/api/v1/health` | No | Health check |
| `/health/ready` | `/api/v1/health/ready` | No | Readiness probe |
| `/health/live` | `/api/v1/health/live` | No | Liveness probe |
| `/auth/me` | `/api/v1/auth/me` | Yes | Current user info |
| `/test/protected` | `/api/v1/test/protected` | Yes | Protected test endpoint |
| `/test/admin` | `/api/v1/test/admin` | Yes (admin role) | Admin-only test endpoint |

**Reference:** `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py`

#### Test Endpoint Mapping

Example tests must target the correct endpoints with API prefix:

```javascript
// Public endpoints
await request.get('/');                              // Root
await request.get('{{ cookiecutter.backend_api_prefix }}/health');  // Health check

// Protected endpoints
await userRequest.get('{{ cookiecutter.backend_api_prefix }}/auth/me');       // User info
await userRequest.get('{{ cookiecutter.backend_api_prefix }}/test/protected'); // Protected

// Admin-only endpoints
await adminRequest.get('{{ cookiecutter.backend_api_prefix }}/test/admin');   // Admin route
```

---

### TA-8: Error Handling Strategy

#### Authentication Errors

When token retrieval fails, the error message must be actionable:

```javascript
if (!response.ok()) {
  const text = await response.text();
  throw new Error(`Failed to get token for user '${username}': ${response.status()} ${text}`);
}
```

**Common Failure Scenarios:**

| Error | Cause | Resolution |
|-------|-------|------------|
| 401 `invalid_grant` | Wrong username/password | Check test-users.js matches Keycloak |
| 401 `unauthorized_client` | Client secret mismatch | Verify realm setup script |
| 503 Connection refused | Keycloak not running | Run `make docker-up` |
| 404 Not Found | Wrong realm name | Check KEYCLOAK_REALM variable |

#### Fixture Initialization Errors

If any user's token cannot be retrieved during fixture setup, the test should fail with a clear message:

```javascript
try {
  const token = await getAccessToken(request, user.username, user.password);
  // ...
} catch (error) {
  throw new Error(
    `Failed to authenticate test user '${key}' (${user.username}): ${error.message}\n` +
    `Ensure Keycloak is running and realm is configured. Run: make docker-up && ./keycloak/setup-realm.sh`
  );
}
```

---

### TA-9: Makefile Integration

#### Target Design

Makefile targets follow the pattern established in implementation-manager:

```makefile
# Directory paths
PLAYWRIGHT_DIR := playwright

# Testing Commands
test: ## Run all Playwright tests
	cd $(PLAYWRIGHT_DIR) && npm test

test-api: ## Run API tests only
	cd $(PLAYWRIGHT_DIR) && npm run test:api

test-ui: ## Run tests in UI mode
	cd $(PLAYWRIGHT_DIR) && npm run test:ui

test-debug: ## Run tests in debug mode
	cd $(PLAYWRIGHT_DIR) && npm run test:debug

test-report: ## Show Playwright test report
	cd $(PLAYWRIGHT_DIR) && npm run report

test-install: ## Install Playwright dependencies
	cd $(PLAYWRIGHT_DIR) && npm install
```

**Integration with Existing Template Makefile:**

The template may not currently have a Makefile. If not, one will be created following the implementation-manager pattern. If one exists, the test targets will be added.

---

### TA-10: Documentation Approach

#### README Structure

The `playwright/README.md` will follow this structure:

1. **Overview**: What this testing infrastructure provides
2. **Prerequisites**: Docker services, Node.js, npm
3. **Quick Start**: 5 commands to run first test
4. **Project Structure**: File layout explanation
5. **Writing Tests**:
   - Using fixtures (recommended)
   - Manual authentication (advanced)
6. **Available Fixtures**: Table with all fixtures and their purpose
7. **Test Users**: Table with credentials and roles
8. **Configuration**: Environment variables
9. **CI/CD Integration**: Notes for pipeline setup
10. **Troubleshooting**: Common issues and solutions

#### QUICK_START Guide

A focused guide for immediate productivity:

```markdown
# Quick Start - API Testing

## Prerequisites
- Docker services running (`make docker-up`)
- Keycloak realm configured (`./keycloak/setup-realm.sh`)

## Steps

1. Install dependencies:
   ```bash
   make test-install
   ```

2. Run tests:
   ```bash
   make test-api
   ```

3. View report:
   ```bash
   make test-report
   ```

## Writing Your First Test

```javascript
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test('my first API test', async ({ userRequest }) => {
  const response = await userRequest.get('/api/v1/auth/me');
  expect(response.ok()).toBeTruthy();
});
```
```

---

### TA-11: Technology Decisions Summary

| Decision | Choice | Alternative Considered | Rationale |
|----------|--------|----------------------|-----------|
| Test Framework | Playwright | Jest + SuperTest | Unified with frontend E2E, better fixtures |
| Module System | CommonJS | ES Modules | Simpler for test files, no transpilation needed |
| Auth Approach | Password Grant | Service Account | Simpler test user management, matches implementation-manager |
| Fixture Pattern | Extended Test | Separate Helper | Built-in Playwright pattern, cleaner test code |
| Config Location | Standalone directory | Inside frontend | Separation of concerns, independent lifecycle |
| User Management | Dual (tenant + role) | Role-only | Supports both RBAC and multi-tenancy testing |

---

### TA-12: Implementation Dependencies

#### External Dependencies

| Dependency | Version | Source | Purpose |
|------------|---------|--------|---------|
| Node.js | 20.x | System | JavaScript runtime |
| npm | 10.x | System | Package manager |
| Docker | Any | System | Service containers |
| Docker Compose | Any | System | Service orchestration |

#### Internal Dependencies

| Dependency | Location | Purpose |
|------------|----------|---------|
| Keycloak | `compose.yml` | Identity provider |
| Backend API | `compose.yml` | Test target |
| Realm Setup | `keycloak/setup-realm.sh` | Test user creation |

#### Package Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `@playwright/test` | ^1.56.x | Test framework and runner |

---

### TA-13: Codebase References

The following files from the implementation-manager project serve as reference implementations:

| File | Purpose | Key Patterns |
|------|---------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/playwright.config.js` | Configuration | Projects, webServer, use settings |
| `/home/ty/workspace/project-starter/implementation-manager/playwright/package.json` | Package config | Scripts, dependencies |
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/auth-helper.js` | Auth utilities | Token retrieval, header builder |
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/test-users.js` | User fixtures | User definitions, role queries |
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/fixtures.js` | Test fixtures | Extended test, authenticated contexts |
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-endpoints.api.spec.js` | Basic tests | Manual auth pattern |
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-with-fixtures.api.spec.js` | Fixture tests | Recommended patterns |
| `/home/ty/workspace/project-starter/implementation-manager/Makefile` | Build targets | Test command patterns |

The template endpoints follow the pattern in:
- `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py`
- `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/routers/health.py`

---

## Architecture & Integration Considerations

This section details the architectural decisions, integration patterns, and system interactions for the Playwright API testing infrastructure within the cookiecutter template.

---

### AI-1: System Architecture Overview

#### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 GENERATED PROJECT                                         │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              TESTING LAYER                                           │ │
│  │  ┌───────────────────────────────┐    ┌───────────────────────────────────────────┐ │ │
│  │  │      playwright/              │    │          frontend/e2e/                    │ │ │
│  │  │   (API Testing - NEW)         │    │      (Browser E2E - Existing)             │ │ │
│  │  │                               │    │                                           │ │ │
│  │  │  ┌─────────────────────────┐  │    │  ┌─────────────────────────────────────┐  │ │ │
│  │  │  │ playwright.config.js    │  │    │  │ playwright.config.ts               │  │ │ │
│  │  │  │ baseURL: :{{ cookiecutter.backend_port }}      │  │    │  │ baseURL: :{{ cookiecutter.frontend_port }}                 │  │ │ │
│  │  │  └─────────────────────────┘  │    │  └─────────────────────────────────────┘  │ │ │
│  │  │                               │    │                                           │ │ │
│  │  │  ┌─────────────────────────┐  │    │  Tests: health-check.spec.ts             │ │ │
│  │  │  │ tests/                  │  │    │                                           │ │ │
│  │  │  │  ├── auth-helper.js     │──┼────┼──► Keycloak Token Endpoint               │ │ │
│  │  │  │  ├── test-users.js      │  │    │                                           │ │ │
│  │  │  │  ├── fixtures.js        │  │    │                                           │ │ │
│  │  │  │  └── *.api.spec.js      │──┼────┼──► Backend API Endpoints                 │ │ │
│  │  │  └─────────────────────────┘  │    │                                           │ │ │
│  │  └───────────────────────────────┘    └───────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                                │
│                                          ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                              APPLICATION LAYER                                       │ │
│  │  ┌───────────────────────────────┐    ┌───────────────────────────────────────────┐ │ │
│  │  │     backend/                  │    │         frontend/                         │ │ │
│  │  │   (FastAPI + OAuth)           │    │      (Lit + PKCE Flow)                    │ │ │
│  │  │                               │    │                                           │ │ │
│  │  │  Port: {{ cookiecutter.backend_port }}                  │    │  Port: {{ cookiecutter.frontend_port }}                           │ │ │
│  │  │  Endpoints:                   │    │                                           │ │ │
│  │  │  - /                          │    │                                           │ │ │
│  │  │  - /api/v1/health            │    │                                           │ │ │
│  │  │  - /api/v1/test/protected    │◄───┼───JWT Validation via JWKS                 │ │ │
│  │  │  - /api/v1/auth/me           │    │                                           │ │ │
│  │  │  - /api/v1/todos/*           │    │                                           │ │ │
│  │  └───────────────────────────────┘    └───────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                          │                                                │
│                                          ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐ │
│  │                           INFRASTRUCTURE LAYER                                       │ │
│  │  ┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐               │ │
│  │  │    Keycloak       │  │   PostgreSQL      │  │      Redis        │               │ │
│  │  │  Port: {{ cookiecutter.keycloak_port }}      │  │  Port: {{ cookiecutter.postgres_port }}      │  │  Port: {{ cookiecutter.redis_port }}       │               │ │
│  │  │                   │  │                   │  │                   │               │ │
│  │  │  Token Endpoint   │  │  App Database     │  │  Token Blacklist  │               │ │
│  │  │  JWKS Endpoint    │  │  RLS Policies     │  │  Rate Limiting    │               │ │
│  │  │  Test Users       │  │  Tenant Data      │  │  Session Cache    │               │ │
│  │  └───────────────────┘  └───────────────────┘  └───────────────────┘               │ │
│  └─────────────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Separation of Testing Concerns

The architecture maintains strict separation between API testing and browser E2E testing:

| Aspect | API Testing (playwright/) | Browser E2E (frontend/e2e/) |
|--------|--------------------------|----------------------------|
| Purpose | Test backend API contracts, authentication, authorization | Test frontend UI interactions, visual rendering |
| Base URL | `http://localhost:{{ cookiecutter.backend_port }}` | `http://localhost:{{ cookiecutter.frontend_port }}` |
| Authentication | OAuth 2.0 Password Grant (programmatic) | PKCE flow through browser (user-like) |
| Dependencies | Backend + Keycloak | Frontend + Backend + Keycloak |
| Test Files | `*.api.spec.js` | `*.spec.ts` |
| Config | `playwright/playwright.config.js` | `frontend/playwright.config.ts` |
| Language | JavaScript (CommonJS) | TypeScript |

---

### AI-2: Integration Points

#### 2.1: Playwright to Keycloak Integration

The API testing infrastructure integrates with Keycloak via the OAuth 2.0 token endpoint for authentication.

**Token Endpoint Integration:**

```
┌─────────────────────┐     POST /realms/{realm}/protocol/openid-connect/token
│  auth-helper.js     │─────────────────────────────────────────────────────────►
│                     │     form: { grant_type: password, client_id, client_secret,
│  getAccessToken()   │            username, password }
└─────────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────────────┐
                              │            Keycloak                    │
                              │  Port: {{ cookiecutter.keycloak_port }}                        │
                              │                                         │
                              │  Validates:                             │
                              │  - Client ID + Secret (backend client)  │
                              │  - Username + Password (test user)      │
                              │  - directAccessGrantsEnabled: true      │
                              └───────────────────────────────────────┘
                                              │
                                              │ Response: { access_token, refresh_token, ... }
                                              ▼
┌─────────────────────┐     JWT Access Token (RS256 signed)
│  auth-helper.js     │◄────────────────────────────────────────────────────────
│                     │
│  Returns token      │
└─────────────────────┘
```

**Keycloak Client Requirements:**

The backend client (`{{ cookiecutter.keycloak_backend_client_id }}`) must be configured with:

| Setting | Value | Purpose |
|---------|-------|---------|
| `publicClient` | `false` | Confidential client requiring secret |
| `directAccessGrantsEnabled` | `true` | Enables Resource Owner Password Credentials (ROPC) grant |
| `secret` | `{{ cookiecutter.keycloak_backend_client_id }}-secret` | Client authentication |
| `standardFlowEnabled` | `true` | Allows authorization code flow (for frontend) |

**Reference:** `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/keycloak/setup-realm.sh` lines 89-145.

#### 2.2: Playwright to Backend Integration

API tests send HTTP requests directly to the FastAPI backend with JWT tokens in the Authorization header.

**Request Flow:**

```
┌─────────────────────┐
│  Test File          │     GET /api/v1/test/protected
│  *.api.spec.js      │     Headers: { Authorization: Bearer <JWT> }
│                     │───────────────────────────────────────────────►
│  userRequest.get()  │
└─────────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────────────┐
                              │          FastAPI Backend               │
                              │  Port: {{ cookiecutter.backend_port }}                        │
                              │                                         │
                              │  1. Extract JWT from Authorization      │
                              │  2. Validate signature via JWKS         │
                              │  3. Extract tenant_id from claims       │
                              │  4. Set tenant context for RLS          │
                              │  5. Execute endpoint handler            │
                              └───────────────────────────────────────┘
                                              │
                                              │ JSON Response
                                              ▼
┌─────────────────────┐
│  Test File          │◄──────────────────────────────────────────────
│                     │     { message: "...", user: { username, roles, tenant_id } }
│  Assert response    │
└─────────────────────┘
```

**Backend Endpoint Mapping:**

| Test Scenario | Endpoint | Auth Required | Response Codes |
|--------------|----------|---------------|----------------|
| Public access | `GET /` | No | 200 |
| Health check | `GET /api/v1/health` | No | 200 |
| Protected access | `GET /api/v1/test/protected` | Yes (any role) | 200 (auth), 403 (no auth) |
| User info | `GET /api/v1/auth/me` | Yes | 200 (auth), 401/403 (no auth) |
| Admin access | TBD (add admin endpoint) | Yes (admin role) | 200 (admin), 403 (non-admin) |

**Note:** The template's current `/api/v1/test/protected` endpoint does not have an admin-only equivalent. The FRD recommends adding an admin-only endpoint for comprehensive RBAC testing.

**Reference:** `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py`

#### 2.3: Backend to Keycloak Integration (JWKS)

The backend validates JWT tokens by fetching public keys from Keycloak's JWKS endpoint.

```
┌───────────────────────────────────────┐
│          FastAPI Backend               │
│                                         │
│  app/services/jwks_client.py           │──────────────────────────►
│  - Fetches JWKS from Keycloak          │  GET /realms/{realm}/protocol/openid-connect/certs
│  - Caches public keys                  │
│  - Validates JWT signatures            │
└───────────────────────────────────────┘
                                              │
                                              ▼
                              ┌───────────────────────────────────────┐
                              │            Keycloak                    │
                              │                                         │
                              │  JWKS Endpoint returns:                │
                              │  { keys: [{ kty, alg, use, n, e }] }   │
                              └───────────────────────────────────────┘
```

This integration is transparent to API tests; they only need valid tokens.

---

### AI-3: Data Flow Architecture

#### Authentication Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            TEST EXECUTION DATA FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

Phase 1: Fixture Initialization (per test)
─────────────────────────────────────────────

    fixtures.js                  auth-helper.js              Keycloak
    ───────────                  ──────────────              ────────
         │                            │                          │
         │  for each TEST_USER        │                          │
         ├────────────────────────────►                          │
         │  getAccessToken(           │  POST token endpoint     │
         │    request,                ├─────────────────────────►│
         │    username,               │  form: {                 │
         │    password                │    grant_type: password  │
         │  )                         │    client_id, secret     │
         │                            │    username, password    │
         │                            │  }                       │
         │                            │◄─────────────────────────┤
         │                            │  { access_token: JWT }   │
         │◄───────────────────────────┤                          │
         │  token                     │                          │
         │                            │                          │
         │  Create wrapper:           │                          │
         │  contexts[key] = {         │                          │
         │    get, post, put,         │                          │
         │    patch, delete,          │                          │
         │    user, token             │                          │
         │  }                         │                          │
         │                            │                          │
    ─────┴────────────────────────────┴──────────────────────────┴─────


Phase 2: Test Execution
─────────────────────────

    test.api.spec.js            fixtures.js                 Backend API
    ────────────────            ───────────                 ───────────
         │                           │                           │
         │  async ({ userRequest })  │                           │
         │◄──────────────────────────┤                           │
         │  Pre-authenticated        │                           │
         │  request context          │                           │
         │                           │                           │
         │  userRequest.get(         │                           │
         │    '/api/v1/test/protected' ─────────────────────────►│
         │  )                        │  GET /api/v1/test/protected
         │                           │  Authorization: Bearer JWT│
         │                           │                           │
         │                           │◄──────────────────────────┤
         │◄──────────────────────────┤  { message, user: {...} } │
         │  Response object          │                           │
         │                           │                           │
         │  expect(response.ok())    │                           │
         │  .toBeTruthy()            │                           │
         │                           │                           │
    ─────┴───────────────────────────┴───────────────────────────┴─────
```

#### Token Lifecycle

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         TOKEN LIFECYCLE IN TESTS                            │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ Test Start  │───►│ Fixture     │───►│ Token Valid │───►│ Test End    │ │
│  │             │    │ Init        │    │ for Test    │    │             │ │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘ │
│                           │                   │                  │         │
│                           ▼                   ▼                  ▼         │
│                     Get tokens          Use tokens         Tokens          │
│                     for all 6           in requests        discarded       │
│                     test users                             (not revoked)   │
│                                                                             │
│  Token Lifespan:                                                            │
│  - Default: 900 seconds (15 min) per Keycloak client config                │
│  - Sufficient for typical test execution (<60 seconds)                     │
│  - No refresh needed within single test                                    │
│                                                                             │
│  Isolation:                                                                 │
│  - Each test gets fresh tokens (no state sharing)                          │
│  - Parallel tests get independent token sets                               │
│  - No cross-test token contamination                                       │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

### AI-4: Network Architecture

#### Service Communication Map

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                             DOCKER COMPOSE NETWORK                                        │
│                         {{ cookiecutter.project_slug }}-network                                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│   ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│   │  HOST MACHINE (Developer Workstation)                                            │   │
│   │                                                                                   │   │
│   │  ┌────────────────────┐                                                          │   │
│   │  │  Playwright Tests  │                                                          │   │
│   │  │  (npm test)        │                                                          │   │
│   │  └────────────────────┘                                                          │   │
│   │          │         │                                                              │   │
│   │          │         └──────────────────────────────────────┐                      │   │
│   │          │ HTTP (localhost:{{ cookiecutter.backend_port }})                 │ HTTP (localhost:{{ cookiecutter.keycloak_port }})    │   │
│   │          ▼                                                 ▼                      │   │
│   └──────────┼─────────────────────────────────────────────────┼──────────────────────┘   │
│              │                                                 │                          │
│   ┌──────────┼─────────────────────────────────────────────────┼──────────────────────┐   │
│   │  DOCKER  │                                                 │                      │   │
│   │          ▼                                                 ▼                      │   │
│   │  ┌───────────────────┐                             ┌───────────────────┐          │   │
│   │  │  backend          │                             │  keycloak         │          │   │
│   │  │  :{{ cookiecutter.backend_port }} → :8000       │──JWKS Fetch──────►│  :{{ cookiecutter.keycloak_port }} → :8080       │          │   │
│   │  │                   │                             │                   │          │   │
│   │  └───────────────────┘                             └───────────────────┘          │   │
│   │          │                                                 │                      │   │
│   │          │ postgres://                                     │ jdbc:postgresql://   │   │
│   │          ▼                                                 ▼                      │   │
│   │  ┌───────────────────────────────────────────────────────────────────────┐        │   │
│   │  │                           postgres                                     │        │   │
│   │  │                      :{{ cookiecutter.postgres_port }} → :5432                                  │        │   │
│   │  │                                                                        │        │   │
│   │  │  Databases: {{ cookiecutter.postgres_db }}, keycloak_db                                │        │   │
│   │  └───────────────────────────────────────────────────────────────────────┘        │   │
│   │                                                                                    │   │
│   │  ┌───────────────────┐                                                            │   │
│   │  │  redis            │◄──Token blacklist, rate limiting───┐                       │   │
│   │  │  :{{ cookiecutter.redis_port }} → :6379       │                                │                       │   │
│   │  └───────────────────┘                                │                           │   │
│   │          ▲                                            │                           │   │
│   │          └────────────────────────────────────────────┘                           │   │
│   │                              backend                                               │   │
│   └────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

#### Port Mapping (Cookiecutter Variables)

| Service | Container Port | Host Port (Variable) | Default |
|---------|---------------|---------------------|---------|
| Backend | 8000 | `{{ cookiecutter.backend_port }}` | 8000 |
| Keycloak | 8080 | `{{ cookiecutter.keycloak_port }}` | 8080 |
| PostgreSQL | 5432 | `{{ cookiecutter.postgres_port }}` | 5432 |
| Redis | 6379 | `{{ cookiecutter.redis_port }}` | 6379 |
| Frontend | 5173 | `{{ cookiecutter.frontend_port }}` | 5173 |

**Reference:** `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/compose.yml`

---

### AI-5: API Contract Alignment

#### Template Backend API Structure

The template backend uses the `API_V1_PREFIX` setting (default: `/api/v1`) for all authenticated endpoints.

**Endpoint Registry:**

| Router | Prefix | Endpoints | Auth |
|--------|--------|-----------|------|
| health | `/api/v1` | `/health`, `/ready` | No |
| auth | `/api/v1` | `/auth/me` | Yes |
| oauth | `/api/v1` | `/oauth/login`, `/oauth/callback`, `/oauth/logout`, `/oauth/token` | Varies |
| test_auth | `/api/v1` | `/test/protected` | Yes |
| todos | `/api/v1` | `/todos/*` | Yes |
| root | `/` | `/` | No |

**Reference:** `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/main.py` lines 160-164.

#### API Test Endpoint Coverage

Tests should cover these endpoint categories:

| Category | Endpoint | Test Assertion |
|----------|----------|----------------|
| Public | `GET /` | Returns service info |
| Public | `GET /api/v1/health` | Returns `{ status: "healthy" }` |
| Protected | `GET /api/v1/test/protected` | 200 with auth, 403 without |
| Protected | `GET /api/v1/auth/me` | Returns user info from token |
| Admin (TBD) | `GET /api/v1/admin/*` | 200 with admin role, 403 without |

**Gap Identified:** The template lacks a dedicated admin-only endpoint. Consider adding one for comprehensive RBAC testing:

```python
# Recommended addition to test_auth.py
@router.get(
    "/admin",
    response_model=TestAuthResponse,
    summary="Admin-only test endpoint",
)
async def admin_endpoint(user: CurrentUser = Depends(require_admin)):
    """Admin-only endpoint for testing role-based access."""
    return TestAuthResponse(...)
```

---

### AI-6: Fixture Architecture Deep Dive

#### Fixture Dependency Chain

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      PLAYWRIGHT FIXTURE DEPENDENCY CHAIN                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  @playwright/test (built-in)                                             ││
│  │  ┌────────────────────┐                                                  ││
│  │  │  request           │  Playwright's built-in APIRequestContext         ││
│  │  │  (base fixture)    │  - Handles HTTP requests                         ││
│  │  │                    │  - Manages cookies                                ││
│  │  │                    │  - JSON serialization                             ││
│  │  └────────────────────┘                                                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                            │                                                 │
│                            │ depends on                                      │
│                            ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  fixtures.js (custom)                                                    ││
│  │  ┌────────────────────────────────────────────────────────────────────┐ ││
│  │  │  authenticatedRequest                                               │ ││
│  │  │  (extended fixture)                                                 │ ││
│  │  │                                                                     │ ││
│  │  │  - Iterates TEST_USERS                                             │ ││
│  │  │  - Calls getAccessToken() for each                                 │ ││
│  │  │  - Creates wrapper objects with auth headers                       │ ││
│  │  │  - Provides: .admin, .user, .readOnly, .newUser, .manager,         │ ││
│  │  │              .serviceAccount                                       │ ││
│  │  └────────────────────────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                            │                                                 │
│                            │ depends on                                      │
│                            ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  fixtures.js (convenience fixtures)                                      ││
│  │  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐ ┌──────────────┐  ││
│  │  │ adminRequest │ │ userRequest  │ │ readOnlyRequest│ │managerRequest│  ││
│  │  │              │ │              │ │                │ │              │  ││
│  │  │ delegates to │ │ delegates to │ │ delegates to   │ │ delegates to │  ││
│  │  │ authenticated│ │ authenticated│ │ authenticated  │ │ authenticated│  ││
│  │  │ Request.admin│ │ Request.user │ │ Request.readO..│ │ Request.mngr │  ││
│  │  └──────────────┘ └──────────────┘ └────────────────┘ └──────────────┘  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Fixture Initialization Sequence

```
Test Start
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Playwright creates base `request` fixture                                │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. `authenticatedRequest` fixture initializes:                              │
│     for (const [key, user] of Object.entries(TEST_USERS)) {                  │
│       // This happens 6 times (admin, user, readOnly, newUser, manager,     │
│       // serviceAccount)                                                     │
│       const token = await getAccessToken(request, user.username,            │
│                                          user.password);                     │
│       contexts[key] = createAuthenticatedWrapper(request, token, user);     │
│     }                                                                        │
│     await use(contexts);  // Make available to test                         │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Convenience fixtures resolve (if requested):                             │
│     adminRequest ─► authenticatedRequest.admin                               │
│     userRequest  ─► authenticatedRequest.user                               │
│     etc.                                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Test function executes with injected fixtures                            │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
Test End
```

**Performance Consideration:** Each test fetches 6 tokens. For a test suite with 20 tests running in parallel with default workers, this results in ~120 token requests. Keycloak should handle this load without issue in development, but consider token caching strategies for large test suites.

---

### AI-7: Multi-Tenancy Considerations

#### Tenant Context in Tests

The template uses `tenant_id` claims in JWT tokens for multi-tenancy. Test users have assigned tenants:

| User | Tenant ID | Purpose |
|------|-----------|---------|
| admin, testuser, readonly, newuser, manager | `tenant-1` | Primary test tenant |
| service-account | `tenant-1` | Service-to-service within tenant |

**Template's Existing Users (for reference):**

| User | Tenant ID |
|------|-----------|
| alice@example.com | `11111111-1111-1111-1111-111111111111` |
| bob@example.com | `11111111-1111-1111-1111-111111111111` |
| charlie@demo.example | `22222222-2222-2222-2222-222222222222` |
| diana@demo.example | `22222222-2222-2222-2222-222222222222` |

**Integration Decision:** The Playwright test users (admin, testuser, etc.) should be added alongside the existing tenant-based users, allowing both RBAC testing and tenant isolation testing.

#### RLS Implications

Row-Level Security policies in PostgreSQL enforce data isolation based on `tenant_id`. When tests access data endpoints, RLS policies filter results to the user's tenant.

```
Test Request                    Backend                         PostgreSQL
───────────                     ───────                         ──────────
    │                              │                                 │
    │ GET /api/v1/todos           │                                 │
    │ Authorization: Bearer JWT    │                                 │
    ├─────────────────────────────►│                                 │
    │                              │ Extract tenant_id from JWT      │
    │                              │ SET app.current_tenant = '...'  │
    │                              ├────────────────────────────────►│
    │                              │                                 │
    │                              │ SELECT * FROM todos             │
    │                              │ -- RLS policy applies:          │
    │                              │ -- tenant_id = current_setting( │
    │                              │ --   'app.current_tenant')      │
    │                              ├────────────────────────────────►│
    │                              │                                 │
    │                              │◄────────────────────────────────┤
    │                              │ Filtered results                │
    │◄─────────────────────────────┤                                 │
    │ JSON response                │                                 │
```

**Test Implication:** Tests can only see data belonging to their authenticated user's tenant. Cross-tenant access testing requires users from different tenants.

---

### AI-8: Error Handling and Resilience

#### Authentication Error Scenarios

| Scenario | HTTP Status | Error Source | Test Strategy |
|----------|-------------|--------------|---------------|
| Invalid credentials | 401 | Keycloak | Test with wrong password |
| Invalid client | 401 | Keycloak | N/A (config error) |
| Keycloak unavailable | 503 | Network/Keycloak | Service health check |
| Invalid token format | 401 | Backend | Test with malformed token |
| Expired token | 401 | Backend | N/A (tokens live 15 min) |
| Missing token | 403 | Backend | Test with no auth header |
| Insufficient role | 403 | Backend | Test user without required role |

#### Fixture Failure Handling

When token retrieval fails during fixture initialization:

```javascript
// Recommended error handling pattern in fixtures.js
for (const [key, user] of Object.entries(TEST_USERS)) {
  try {
    const token = await getAccessToken(request, user.username, user.password);
    // ... create context
  } catch (error) {
    throw new Error(
      `Failed to authenticate test user '${key}' (${user.username}): ${error.message}\n` +
      `Ensure Keycloak is running with configured test users.\n` +
      `Quick fix: make docker-up && ./keycloak/setup-realm.sh`
    );
  }
}
```

---

### AI-9: CI/CD Integration Architecture

#### CI Environment Differences

| Setting | Development | CI |
|---------|-------------|-----|
| `process.env.CI` | undefined | `true` |
| Workers | Parallel (auto) | Single (`workers: 1`) |
| Retries | 0 | 2 |
| Web Server | Auto-start via Makefile | Pre-started (external) |
| `forbidOnly` | false | true |
| Trace collection | On first retry | On first retry |

#### CI Service Startup Sequence

```
CI Pipeline
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. Start Docker services (external to Playwright)                           │
│     docker compose up -d                                                     │
│     Wait for health checks                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Configure Keycloak realm (if not persistent)                             │
│     ./keycloak/setup-realm.sh                                               │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Run Playwright tests                                                     │
│     CI=true npm test                                                         │
│     - Single worker (stability)                                              │
│     - 2 retries (flakiness handling)                                        │
│     - No webServer auto-start                                               │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. Upload test artifacts                                                    │
│     - playwright-report/                                                     │
│     - test-results/ (on failure)                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Note:** Specific CI/CD configurations (GitHub Actions, GitLab CI, etc.) are out of scope per OS-5, but the architecture supports integration.

---

### AI-10: Template Integration Points

#### Files to Add to Template

```
template/{{cookiecutter.project_slug}}/
├── playwright/                          # NEW DIRECTORY
│   ├── package.json                     # Playwright dependencies
│   ├── playwright.config.js             # API test configuration
│   ├── .gitignore                       # Exclude artifacts
│   ├── README.md                        # Full documentation
│   ├── QUICK_START.md                   # 5-minute guide
│   └── tests/
│       ├── auth-helper.js               # Keycloak authentication
│       ├── test-users.js                # User fixtures
│       ├── fixtures.js                  # Extended Playwright fixtures
│       ├── api-endpoints.api.spec.js    # Basic API tests
│       └── api-with-fixtures.api.spec.js # Fixture-based tests
```

#### Files to Modify in Template

| File | Modification |
|------|--------------|
| `keycloak/setup-realm.sh` | Add 6 role-based test users with role assignments |
| `Makefile` (if exists) | Add test-related targets |
| `CLAUDE.md` | Update with API testing documentation |
| `.gitignore` (root) | Ensure playwright artifacts are ignored |

#### Cookiecutter Variables Used

| Variable | Used In | Purpose |
|----------|---------|---------|
| `{{ cookiecutter.backend_port }}` | playwright.config.js, auth-helper.js | Backend base URL |
| `{{ cookiecutter.keycloak_port }}` | auth-helper.js | Keycloak URL |
| `{{ cookiecutter.keycloak_realm_name }}` | auth-helper.js | Realm for authentication |
| `{{ cookiecutter.keycloak_backend_client_id }}` | auth-helper.js | Client ID for token requests |
| `{{ cookiecutter.backend_api_prefix }}` | Test files | API endpoint prefix |
| `{{ cookiecutter.project_slug }}` | package.json name | Project identification |

---

### AI-11: Scalability Considerations

#### Test Suite Scaling

| Test Count | Token Requests | Estimated Time | Recommendation |
|------------|----------------|----------------|----------------|
| 10-20 | 60-120 | 10-20 seconds | Default config |
| 50-100 | 300-600 | 30-60 seconds | Consider token caching |
| 100+ | 600+ | 60+ seconds | Implement shared auth state |

**Future Enhancement:** For large test suites, consider implementing `storageState` to share authentication across tests:

```javascript
// Advanced: Share auth state between tests (not in initial scope)
const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ request }) => {
  const token = await getAccessToken(request, 'testuser', 'test123');
  await request.storageState({ path: authFile });
});
```

#### Parallel Execution

Playwright's `fullyParallel: true` setting enables parallel test execution:

- **Development:** Uses all available CPU cores
- **CI:** Single worker (`workers: 1`) for stability

Each parallel worker initializes its own fixture instances, so there's no shared state between tests.

---

### AI-12: Security Architecture

#### Credential Management

| Credential Type | Storage | Security Level |
|-----------------|---------|----------------|
| Test user passwords | `test-users.js` (plaintext) | Development only |
| Client secret | `auth-helper.js` | Matches setup-realm.sh |
| Keycloak admin | Environment variables | Not used in tests |

**Security Note:** Test credentials are intentionally simple (`username123`) for development convenience. Production Keycloak configurations should use different credentials.

#### Token Handling

- Tokens are obtained programmatically via ROPC grant
- Tokens are held in memory during test execution
- Tokens are not persisted to disk (no `storageState` by default)
- Tokens expire after 15 minutes (Keycloak default)
- No token refresh logic (tests complete well within lifespan)

---

### Architecture Summary

The Playwright API testing infrastructure integrates cleanly into the existing template architecture by:

1. **Adding a standalone testing layer** (`playwright/`) that operates independently of the frontend E2E tests
2. **Leveraging existing Keycloak infrastructure** with ROPC grant for programmatic authentication
3. **Extending Playwright's fixture system** to provide pre-authenticated request contexts
4. **Aligning with template conventions** (cookiecutter variables, directory structure, Makefile patterns)
5. **Supporting both development and CI environments** with appropriate configuration switches

The architecture is designed for extensibility, allowing future enhancements like token caching, shared authentication state, or additional user fixtures without breaking existing tests

---

## Data Models & Schema Changes

This section defines the data models, configuration structures, and identity management schema changes required for the Playwright API testing infrastructure. Notably, this feature **does not require any application database schema changes** since it operates purely as a testing layer against existing backend APIs.

---

### DM-1: No Application Database Schema Changes

The Playwright API testing infrastructure operates entirely at the HTTP layer, testing existing API endpoints. It does not:

- Require new database tables
- Modify existing table structures
- Add database migrations
- Change PostgreSQL RLS policies
- Affect the SQLAlchemy ORM models

**Rationale:** API tests validate the behavior of endpoints from an external client perspective. Any data created during tests uses existing API endpoints and existing database schemas.

---

### DM-2: Test User Data Model

The test user data model defines the structure for pre-configured test users used in Playwright API tests. This model lives in `playwright/tests/test-users.js`.

#### 2.1: TestUser Interface

```javascript
/**
 * @typedef {Object} TestUser
 * @property {string} username - Keycloak username for authentication
 * @property {string} password - User password (plaintext, development only)
 * @property {string} email - User email address
 * @property {string[]} roles - Array of realm role names assigned to user
 * @property {string} description - Human-readable purpose description
 */
```

**TypeScript Equivalent (for reference):**

```typescript
interface TestUser {
  username: string;
  password: string;
  email: string;
  roles: string[];
  description: string;
}
```

#### 2.2: TEST_USERS Collection Schema

The `TEST_USERS` object maps fixture keys to TestUser objects:

```javascript
/**
 * @type {Record<string, TestUser>}
 */
const TEST_USERS = {
  admin: TestUser,      // Key matches fixture name: authenticatedRequest.admin
  user: TestUser,       // Key matches fixture name: authenticatedRequest.user
  readOnly: TestUser,   // camelCase keys for JavaScript convention
  newUser: TestUser,
  manager: TestUser,
  serviceAccount: TestUser,
};
```

#### 2.3: Test User Data Instances

| Key | username | password | email | roles | description |
|-----|----------|----------|-------|-------|-------------|
| `admin` | `admin` | `admin123` | `admin@example.com` | `['user', 'admin']` | Full admin access |
| `user` | `testuser` | `test123` | `test@example.com` | `['user']` | Standard user |
| `readOnly` | `readonly` | `readonly123` | `readonly@example.com` | `['user', 'readonly']` | Read-only access |
| `newUser` | `newuser` | `newuser123` | `newuser@example.com` | `['user']` | Fresh account for onboarding |
| `manager` | `manager` | `manager123` | `manager@example.com` | `['user', 'manager']` | Elevated permissions |
| `serviceAccount` | `service-account` | `service123` | `service@example.com` | `['service']` | API-to-API integration |

**Password Convention:** `username + '123'` for easy memorization during development.

**Implementation Reference:** `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/test-users.js`

---

### DM-3: Authenticated Request Context Model

The authenticated request context wraps Playwright's `APIRequestContext` with pre-injected authorization headers.

#### 3.1: AuthenticatedContext Interface

```javascript
/**
 * @typedef {Object} AuthenticatedContext
 * @property {Function} get - HTTP GET with auth header: (url, options?) => Promise<Response>
 * @property {Function} post - HTTP POST with auth header: (url, options?) => Promise<Response>
 * @property {Function} put - HTTP PUT with auth header: (url, options?) => Promise<Response>
 * @property {Function} patch - HTTP PATCH with auth header: (url, options?) => Promise<Response>
 * @property {Function} delete - HTTP DELETE with auth header: (url, options?) => Promise<Response>
 * @property {TestUser} user - The TestUser object for this context
 * @property {string} token - Raw JWT access token
 */
```

**TypeScript Equivalent:**

```typescript
interface AuthenticatedContext {
  get: (url: string, options?: RequestOptions) => Promise<APIResponse>;
  post: (url: string, options?: RequestOptions) => Promise<APIResponse>;
  put: (url: string, options?: RequestOptions) => Promise<APIResponse>;
  patch: (url: string, options?: RequestOptions) => Promise<APIResponse>;
  delete: (url: string, options?: RequestOptions) => Promise<APIResponse>;
  user: TestUser;
  token: string;
}
```

#### 3.2: AuthenticatedRequestCollection Interface

The `authenticatedRequest` fixture provides access to all user contexts:

```javascript
/**
 * @typedef {Object} AuthenticatedRequestCollection
 * @property {AuthenticatedContext} admin - Admin user context
 * @property {AuthenticatedContext} user - Standard user context
 * @property {AuthenticatedContext} readOnly - Read-only user context
 * @property {AuthenticatedContext} newUser - New user context
 * @property {AuthenticatedContext} manager - Manager user context
 * @property {AuthenticatedContext} serviceAccount - Service account context
 */
```

**Implementation Reference:** `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/fixtures.js`

---

### DM-4: Keycloak Realm Schema Changes

The Keycloak realm must be extended with new roles and test users. These changes are identity schema changes managed by the `keycloak/setup-realm.sh` script.

#### 4.1: Realm Roles to Add

The following realm-level roles must be created for RBAC testing:

| Role Name | Description | Created By |
|-----------|-------------|------------|
| `user` | Standard user access to protected endpoints | setup-realm.sh |
| `admin` | Administrative access to admin-only endpoints | setup-realm.sh |
| `readonly` | Read-only access to resources | setup-realm.sh |
| `manager` | Manager-level elevated permissions | setup-realm.sh |
| `service` | Service account for API-to-API integration | setup-realm.sh |

**Keycloak Admin API for Role Creation:**

```bash
# Create realm role
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "admin", "description": "Administrative access"}' \
  "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/roles"
```

#### 4.2: Test Users to Add to Keycloak

Six test users must be created in the Keycloak realm with the following structure:

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "emailVerified": true,
  "firstName": "Admin",
  "lastName": "User",
  "enabled": true,
  "attributes": {
    "tenant_id": ["tenant-1"]
  },
  "credentials": [
    {
      "type": "password",
      "value": "admin123",
      "temporary": false
    }
  ]
}
```

**User-to-Role Mapping:**

| Username | Roles to Assign | Tenant ID |
|----------|-----------------|-----------|
| `admin` | `user`, `admin` | `tenant-1` |
| `testuser` | `user` | `tenant-1` |
| `readonly` | `user`, `readonly` | `tenant-1` |
| `newuser` | `user` | `tenant-1` |
| `manager` | `user`, `manager` | `tenant-1` |
| `service-account` | `service` | `tenant-1` |

**Keycloak Admin API for User Creation and Role Assignment:**

```bash
# Create user
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$USER_JSON" \
  "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users"

# Get user UUID
USER_UUID=$(curl -s \
  -H "Authorization: Bearer $TOKEN" \
  "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users?username=admin&exact=true" | jq -r '.[0].id')

# Assign role to user
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '[{"name": "admin"}]' \
  "$KEYCLOAK_URL/admin/realms/{{ cookiecutter.keycloak_realm_name }}/users/$USER_UUID/role-mappings/realm"
```

#### 4.3: Relationship to Existing Keycloak Users

The current template creates 4 tenant-based users:

| Existing User | Tenant ID | Purpose |
|---------------|-----------|---------|
| `alice@example.com` | `11111111-1111-1111-1111-111111111111` | Multi-tenancy testing |
| `bob@example.com` | `11111111-1111-1111-1111-111111111111` | Multi-tenancy testing |
| `charlie@demo.example` | `22222222-2222-2222-2222-222222222222` | Cross-tenant testing |
| `diana@demo.example` | `22222222-2222-2222-2222-222222222222` | Cross-tenant testing |

**Integration Strategy:** The 6 new role-based test users (admin, testuser, etc.) will be **added alongside** the existing tenant-based users. This allows:

1. Role-based API testing (using new users)
2. Multi-tenancy isolation testing (using existing users)
3. Backward compatibility with any existing tests

---

### DM-5: Configuration Data Model

The test infrastructure uses environment-driven configuration for flexibility across environments.

#### 5.1: AuthConfig Interface

```javascript
/**
 * Authentication configuration constants
 * @typedef {Object} AuthConfig
 */
const AuthConfig = {
  /** @type {string} Keycloak server URL */
  KEYCLOAK_URL: process.env.KEYCLOAK_URL || 'http://localhost:{{ cookiecutter.keycloak_port }}',

  /** @type {string} Keycloak realm name */
  KEYCLOAK_REALM: process.env.KEYCLOAK_REALM || '{{ cookiecutter.keycloak_realm_name }}',

  /** @type {string} Backend client ID for token requests */
  CLIENT_ID: '{{ cookiecutter.keycloak_backend_client_id }}',

  /** @type {string} Backend client secret */
  CLIENT_SECRET: '{{ cookiecutter.keycloak_backend_client_id }}-secret',
};
```

#### 5.2: PlaywrightConfig Interface

```javascript
/**
 * Playwright test configuration
 * @typedef {Object} PlaywrightConfig
 */
const PlaywrightConfig = {
  /** @type {string} Test directory relative to config file */
  testDir: './tests',

  /** @type {number} Timeout per test in milliseconds */
  timeout: 30000,

  /** @type {boolean} Run tests in parallel */
  fullyParallel: true,

  /** @type {boolean} Fail if .only() is used in CI */
  forbidOnly: Boolean(process.env.CI),

  /** @type {number} Retry count (2 in CI, 0 otherwise) */
  retries: process.env.CI ? 2 : 0,

  /** @type {number|undefined} Worker count (1 in CI for stability) */
  workers: process.env.CI ? 1 : undefined,

  /** @type {Object} Use configuration for all tests */
  use: {
    /** @type {string} Backend API base URL */
    baseURL: process.env.BASE_URL || 'http://localhost:{{ cookiecutter.backend_port }}',

    /** @type {string} When to collect traces */
    trace: 'on-first-retry',

    /** @type {Object} Default HTTP headers */
    extraHTTPHeaders: {
      'Accept': 'application/json',
    },
  },
};
```

**Implementation Reference:** `/home/ty/workspace/project-starter/implementation-manager/playwright/playwright.config.js`

---

### DM-6: OAuth Token Response Model

The authentication helper processes Keycloak token responses. This is a read-only model (consumed, not stored).

#### 6.1: KeycloakTokenResponse Interface

```javascript
/**
 * @typedef {Object} KeycloakTokenResponse
 * @property {string} access_token - JWT access token for API requests
 * @property {number} expires_in - Token lifetime in seconds (typically 900)
 * @property {number} refresh_expires_in - Refresh token lifetime
 * @property {string} refresh_token - Token for obtaining new access tokens
 * @property {string} token_type - Always "Bearer"
 * @property {string} session_state - Keycloak session identifier
 * @property {string} scope - Granted OAuth scopes
 */
```

**Example Response from Keycloak:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwiキ...",
  "expires_in": 900,
  "refresh_expires_in": 1800,
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldU...",
  "token_type": "Bearer",
  "session_state": "abc123-def456-...",
  "scope": "openid email profile"
}
```

**Usage:** Only `access_token` is extracted and used; other fields are ignored.

---

### DM-7: JWT Token Claims Model

The JWT access tokens contain claims used by the backend for authorization and tenant context.

#### 7.1: JWTClaims Interface (Reference)

```typescript
// These claims are validated by the backend, not the test infrastructure
interface JWTClaims {
  // Standard OIDC claims
  sub: string;           // User UUID (Keycloak user ID)
  iss: string;           // Issuer URL (Keycloak realm)
  aud: string | string[]; // Audience (client ID)
  exp: number;           // Expiration timestamp
  iat: number;           // Issued at timestamp

  // User identity claims
  preferred_username: string;
  email: string;
  email_verified: boolean;
  name: string;
  given_name: string;
  family_name: string;

  // Custom claims (configured via protocol mappers)
  tenant_id: string;     // Multi-tenancy identifier

  // Realm roles (access path: realm_access.roles)
  realm_access: {
    roles: string[];     // e.g., ["user", "admin"]
  };
}
```

**Token Claim Flow:**

```
Keycloak                    Backend                     Test
────────                    ───────                     ────
    │                           │                         │
    │ Issues JWT with claims:   │                         │
    │ - sub (user UUID)         │                         │
    │ - tenant_id (custom)      │                         │
    │ - realm_access.roles      │                         │
    ├──────────────────────────►│                         │
    │                           │ Validates signature     │
    │                           │ Extracts tenant_id      │
    │                           │ Sets RLS context        │
    │                           │                         │
    │                           │◄────────────────────────┤
    │                           │ Request with JWT        │
    │                           │                         │
    │                           ├────────────────────────►│
    │                           │ Response with user info │
    │                           │                         │
```

---

### DM-8: Data Model Synchronization Requirements

The test user data model spans multiple systems that must remain synchronized:

#### 8.1: Synchronization Points

| Source of Truth | Consumers | Sync Mechanism |
|-----------------|-----------|----------------|
| `keycloak/setup-realm.sh` | Keycloak database | Script execution creates users/roles |
| Keycloak database | Backend API (via JWT) | JWT tokens carry user claims |
| `playwright/tests/test-users.js` | Playwright fixtures | Manual sync with setup-realm.sh |

#### 8.2: Synchronization Invariants

The following invariants must be maintained:

1. **Credentials Match:** Passwords in `test-users.js` must match those in `setup-realm.sh`
2. **Roles Match:** Roles in `test-users.js` must match role assignments in `setup-realm.sh`
3. **Usernames Match:** Usernames in `test-users.js` must match exactly with Keycloak users
4. **Tenant IDs Match:** Tenant IDs in Keycloak user attributes must align with test expectations

#### 8.3: Recommended Validation

Consider adding a startup validation in the test infrastructure:

```javascript
// Potential enhancement: Validate test users exist in Keycloak
async function validateTestUsers(request) {
  for (const [key, user] of Object.entries(TEST_USERS)) {
    try {
      await getAccessToken(request, user.username, user.password);
    } catch (error) {
      throw new Error(
        `Test user '${key}' (${user.username}) failed authentication.\n` +
        `Ensure Keycloak is configured with: ./keycloak/setup-realm.sh`
      );
    }
  }
}
```

---

### DM-9: File Artifacts and Storage

The test infrastructure creates temporary artifacts that are excluded from version control.

#### 9.1: Generated Artifacts

| Artifact | Location | Description | Lifecycle |
|----------|----------|-------------|-----------|
| HTML Report | `playwright/playwright-report/` | Test execution results | Generated per run, overwritten |
| Test Results | `playwright/test-results/` | Detailed test traces | Generated on failure/retry |
| Node Modules | `playwright/node_modules/` | NPM dependencies | Installed via `npm install` |
| Playwright Cache | `playwright/.cache/` | Browser binaries | Managed by Playwright |

#### 9.2: .gitignore Configuration

```gitignore
# playwright/.gitignore
node_modules/
playwright-report/
test-results/
.cache/
*.log
```

---

### Data Models Summary

| Model | Location | Purpose | Persistence |
|-------|----------|---------|-------------|
| TestUser | `test-users.js` | Define test user credentials and roles | Source code |
| AuthenticatedContext | `fixtures.js` | Wrap HTTP client with auth | Runtime (memory) |
| AuthConfig | `auth-helper.js` | Authentication configuration | Source code + env |
| PlaywrightConfig | `playwright.config.js` | Test runner configuration | Source code |
| KeycloakTokenResponse | N/A (external) | OAuth token response | Runtime (memory) |
| JWTClaims | N/A (in token) | User identity claims | Token payload |
| Keycloak Users | Keycloak database | Identity provider users | Keycloak H2/PostgreSQL |
| Keycloak Roles | Keycloak database | Realm role definitions | Keycloak H2/PostgreSQL |

**Key Insight:** This feature introduces no application database schema changes. All data models are either:
1. JavaScript runtime structures (fixtures, configs)
2. Keycloak identity management objects (users, roles)
3. Transient authentication artifacts (tokens, test results)

---

## UI/UX Considerations

This feature is a **developer-facing testing infrastructure**, not an end-user application. Therefore, UI/UX considerations focus on **developer experience (DX)** rather than traditional user interface design. This section covers the command-line interface, Playwright's built-in visual tools, test report interfaces, and developer ergonomics.

---

### UX-1: Developer Experience Philosophy

#### Target Audience

The primary users of this testing infrastructure are:

| User Type | Experience Level | Primary Needs |
|-----------|------------------|---------------|
| Backend Developers | Intermediate-Advanced | Quick API validation, auth testing, RBAC verification |
| QA Engineers | Intermediate | Comprehensive test coverage, edge case testing |
| New Team Members | Beginner-Intermediate | Easy onboarding, clear documentation, simple commands |
| DevOps Engineers | Intermediate | CI/CD integration, reliable test execution |

#### Core DX Principles

1. **Zero-to-Running in 5 Minutes**: A new developer should be able to install dependencies and run their first test within 5 minutes of cloning the project.

2. **Sensible Defaults**: The testing infrastructure should work out-of-the-box with minimal configuration for local development.

3. **Progressive Disclosure**: Simple patterns for simple tests; advanced patterns available when needed but not required.

4. **Clear Error Messages**: When tests fail, error messages should guide developers toward resolution.

5. **Consistent Terminology**: Use consistent naming across Makefile targets, npm scripts, fixture names, and documentation.

---

### UX-2: Command-Line Interface Design

The primary interaction model is through terminal commands. These must be intuitive, memorable, and consistent.

#### 2.1: Makefile Target Naming Convention

Makefile targets follow a consistent naming pattern:

```
make test              # Run all tests (simple, memorable)
make test-{mode}       # Run tests in specific mode
make test-{action}     # Perform test-related action
```

**Target Design:**

| Target | Purpose | Mnemonic | Expected Behavior |
|--------|---------|----------|-------------------|
| `make test` | Run all Playwright tests | Primary action | Runs full suite, outputs summary |
| `make test-api` | Run API tests only | Specific subset | Runs `*.api.spec.js` files |
| `make test-ui` | Open Playwright UI | Visual interface | Launches browser-based UI |
| `make test-debug` | Debug mode | Troubleshooting | Stops at first failure, verbose |
| `make test-report` | View HTML report | Post-run analysis | Opens browser with last report |
| `make test-install` | Install dependencies | Setup action | npm install in playwright/ |

**Discoverability:**

```bash
$ make help
...
## Testing Commands
  test            Run all Playwright tests
  test-api        Run API tests only
  test-ui         Run tests in Playwright UI mode
  test-debug      Run tests in debug mode
  test-report     Show Playwright test report
  test-install    Install Playwright dependencies
```

#### 2.2: npm Script Naming Convention

For developers working directly in the `playwright/` directory:

```bash
npm test           # Same as 'make test'
npm run test:api   # Same as 'make test-api'
npm run test:ui    # Same as 'make test-ui'
npm run test:debug # Same as 'make test-debug'
npm run report     # Same as 'make test-report'
```

**Consistency Principle:** npm script names mirror Makefile targets for mental model consistency.

#### 2.3: Terminal Output Design

Test execution should provide clear, scannable output:

```
$ make test-api

Running 12 tests using 4 workers

  ✓  api-endpoints.api.spec.js:12:7 › Public API Endpoints › GET / should return hello world (245ms)
  ✓  api-endpoints.api.spec.js:20:7 › Public API Endpoints › GET /health should return healthy status (89ms)
  ✓  api-with-fixtures.api.spec.js:8:7 › API Tests with Fixtures › admin can access admin endpoint (312ms)
  ✓  api-with-fixtures.api.spec.js:15:7 › API Tests with Fixtures › regular user can access protected endpoint (287ms)
  ...

  12 passed (4.2s)

To open last HTML report run:

  npx playwright show-report
```

**Output Principles:**

- Use checkmarks and X marks for quick visual scanning
- Show test file and name for context
- Display timing for performance awareness
- Provide next-step hints (e.g., how to open report)

---

### UX-3: Playwright Visual Interfaces

Playwright provides built-in visual tools that enhance the developer experience beyond the CLI.

#### 3.1: Playwright UI Mode (`make test-ui`)

Playwright's UI mode provides a visual interface for test exploration and debugging.

**Features Leveraged:**

| Feature | Purpose | Developer Benefit |
|---------|---------|-------------------|
| Test Explorer | Browse test files and suites | Navigate large test suites easily |
| Watch Mode | Re-run tests on file changes | Rapid iteration during development |
| Time Travel | Step through test execution | Debug request/response sequences |
| Trace Viewer | Inspect network requests | Debug authentication issues |
| Filter/Search | Find specific tests | Locate tests by name or file |

**Launch Command:**

```bash
make test-ui
# Opens browser at http://localhost:PORT
```

**Visual Layout (conceptual):**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Playwright Test UI                                            [Run All] ▶  │
├───────────────────────────┬─────────────────────────────────────────────────┤
│  TESTS                    │  TEST DETAILS                                   │
│  ─────────────────────    │  ───────────────────────────────────────────    │
│  ▼ api-endpoints.api.spec │                                                 │
│    ▼ Public API Endpoints │  Selected: admin can access admin endpoint     │
│      ✓ GET / returns...   │                                                 │
│      ✓ GET /health...     │  Status: Passed (312ms)                        │
│    ▼ Protected API...     │                                                 │
│      ✓ GET /protected...  │  Actions:                                       │
│  ▼ api-with-fixtures...   │    [▶ Run]  [👁 Watch]  [🔍 Debug]              │
│    ✓ admin can access...  │                                                 │
│    ✓ user can access...   │  Network:                                       │
│                           │  POST /realms/dev/protocol/openid.../token     │
│                           │  GET /api/v1/admin  → 200 OK                   │
│                           │                                                 │
└───────────────────────────┴─────────────────────────────────────────────────┘
```

#### 3.2: HTML Test Report (`make test-report`)

After test execution, an HTML report is generated for detailed analysis.

**Report Structure:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Playwright Report                                      12 passed   0 failed │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  api-endpoints.api.spec.js                                   6 passed  │ │
│  │  ├── Public API Endpoints                                              │ │
│  │  │   ├── GET / should return hello world                     245ms    │ │
│  │  │   └── GET /health should return healthy status            89ms     │ │
│  │  ├── Protected API Endpoints                                           │ │
│  │  │   ├── GET /protected should fail without token            56ms     │ │
│  │  │   └── GET /protected should succeed with token            312ms    │ │
│  │  └── ...                                                               │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Click any test to view:                                                    │
│  • Request/Response details                                                 │
│  • Error messages and stack traces                                          │
│  • Test duration breakdown                                                  │
│  • Retry attempts (if any)                                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Report Accessibility:**

- Opens in default browser automatically
- Searchable test names
- Expandable/collapsible test groups
- Color-coded pass/fail status (green/red)
- Timestamp and duration information

#### 3.3: Trace Viewer for API Debugging

When tests fail or are retried, Playwright captures traces that include network request details.

**Trace Contents for API Tests:**

| Trace Element | Information Shown | Debug Value |
|---------------|-------------------|-------------|
| Request | Method, URL, headers, body | Verify request format |
| Response | Status, headers, body | Check API response |
| Timing | Request duration | Performance insights |
| Headers | Authorization, Content-Type | Auth token verification |

**Accessing Traces:**

1. Tests with `trace: 'on-first-retry'` capture traces on retry
2. Open HTML report and click failed/retried test
3. Click "Trace" tab to view request timeline

---

### UX-4: Test File and Fixture Ergonomics

The testing infrastructure is designed for comfortable developer workflows.

#### 4.1: Test File Naming Convention

Test files follow a predictable naming pattern:

```
tests/
├── auth-helper.js              # Utility modules (no .spec)
├── test-users.js               # Data modules (no .spec)
├── fixtures.js                 # Fixture definitions (no .spec)
├── api-endpoints.api.spec.js   # Test files (.api.spec.js)
└── api-with-fixtures.api.spec.js
```

**Convention Benefits:**

- `.api.spec.js` suffix clearly identifies test files
- Non-test modules omit `.spec` to avoid accidental execution
- Pattern aligns with common JavaScript testing conventions

#### 4.2: Fixture Import Pattern

Tests use a consistent import pattern for fixtures:

```javascript
// Recommended pattern - clean and explicit
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test('my test', async ({ adminRequest }) => {
  // adminRequest is pre-authenticated
});
```

**Alternative Pattern (for advanced scenarios):**

```javascript
// Manual authentication - when fixtures don't fit
const { test, expect } = require('@playwright/test');
const { getAccessToken, authHeader } = require('./auth-helper');

test('custom auth test', async ({ request }) => {
  const token = await getAccessToken(request, 'custom-user', 'password');
  const response = await request.get('/endpoint', {
    headers: authHeader(token),
  });
});
```

#### 4.3: Fixture Naming and Discoverability

Fixture names are designed for IDE autocompletion and intuitive use:

| Fixture | Type | Pattern |
|---------|------|---------|
| `adminRequest` | Direct access | Single-user shorthand |
| `userRequest` | Direct access | Single-user shorthand |
| `readOnlyRequest` | Direct access | Single-user shorthand |
| `managerRequest` | Direct access | Single-user shorthand |
| `authenticatedRequest` | Multi-user access | `authenticatedRequest.{user}` |

**IDE Experience:**

```javascript
// TypeScript-style JSDoc enables IDE autocompletion
async ({ authenticatedRequest }) => {
  authenticatedRequest.  // IDE shows: admin, user, readOnly, newUser, manager, serviceAccount
  authenticatedRequest.admin.  // IDE shows: get, post, put, patch, delete, user, token
}
```

---

### UX-5: Error Message Design

Error messages should guide developers toward resolution, not just report failure.

#### 5.1: Authentication Failure Messages

**Poor Error Message:**
```
Error: Request failed with status 401
```

**Good Error Message (implemented in auth-helper.js):**
```
Error: Failed to get token for user 'admin': 401 {"error":"invalid_grant","error_description":"Invalid user credentials"}

Troubleshooting:
- Verify Keycloak is running: make docker-up
- Verify realm is configured: ./keycloak/setup-realm.sh
- Check username/password in playwright/tests/test-users.js matches Keycloak
```

#### 5.2: Fixture Initialization Failure

When fixtures fail to initialize:

```
Error: Failed to authenticate test user 'serviceAccount' (service-account): Connection refused

The Playwright API test fixtures require Keycloak to be running.

Quick fix:
1. Start services: make docker-up
2. Wait for Keycloak: curl http://localhost:8080/health
3. Configure realm: ./keycloak/setup-realm.sh
4. Retry tests: make test-api
```

#### 5.3: Test Assertion Failures

Use descriptive assertion messages:

```javascript
// Good: Descriptive message
expect(response.status()).toBe(403);
// Output: Expected: 403, Received: 401

// Better: With context
expect(response.status(), 'Admin endpoint should reject non-admin user').toBe(403);
// Output: Admin endpoint should reject non-admin user
//         Expected: 403, Received: 401
```

---

### UX-6: Documentation User Experience

Documentation is a critical component of developer experience.

#### 6.1: README.md Structure

The README follows a task-oriented structure:

```markdown
# Playwright API Tests

## Quick Start (5 minutes)
1. make test-install
2. make docker-up
3. make test-api

## Available Commands
| Command | Description |
| ------- | ----------- |
| make test | Run all tests |
| ... | ... |

## Writing Your First Test
[Code example with minimal boilerplate]

## Test Users
| Username | Password | Roles | Purpose |
| -------- | -------- | ----- | ------- |
| admin | admin123 | user, admin | Admin access testing |
| ... | ... | ... | ... |

## Fixtures Reference
[Table of available fixtures with descriptions]

## Troubleshooting
[Common issues and resolutions]
```

#### 6.2: QUICK_START.md for Immediate Productivity

A separate quick-start guide for developers who want to run tests immediately:

```markdown
# Quick Start - Playwright API Tests

## Prerequisites
- Docker running
- Node.js 20+

## Steps

### 1. Install (one-time)
make test-install

### 2. Start services
make docker-up

### 3. Run tests
make test-api

### 4. View results
make test-report

## Next: Write your first test
See README.md for examples.
```

---

### UX-7: IDE and Editor Integration

The testing infrastructure supports modern IDE workflows.

#### 7.1: VSCode Integration

**Recommended Extensions:**

| Extension | Purpose | Configuration |
|-----------|---------|---------------|
| Playwright Test for VSCode | Run/debug tests in editor | Auto-detected from playwright.config.js |
| ESLint | Code quality | Standard JavaScript rules |
| Prettier | Code formatting | Optional but recommended |

**VSCode Playwright Extension Features:**

- Run individual tests from code lens
- Debug tests with breakpoints
- View test results in sidebar
- Navigate to test source from failures

**launch.json Configuration (for debugging):**

```json
{
  "type": "node",
  "request": "launch",
  "name": "Debug Playwright Tests",
  "program": "${workspaceFolder}/playwright/node_modules/@playwright/test/cli.js",
  "args": ["test", "--debug"],
  "cwd": "${workspaceFolder}/playwright"
}
```

#### 7.2: JetBrains IDE Integration

For WebStorm/IntelliJ users:

- Playwright plugin provides similar test running capabilities
- Run configurations auto-detected from package.json
- Debug support with breakpoints in test files

---

### UX-8: Workflow Scenarios

Common developer workflows should be smooth and intuitive.

#### 8.1: New Developer Onboarding Workflow

```
Day 1: Join project
├── Clone repository
├── Read QUICK_START.md (2 min)
├── Run: make test-install (30 sec)
├── Run: make docker-up (1 min)
├── Run: make test-api (15 sec)
└── See all tests pass, feel confident

Day 2: Write first API test
├── Copy example from README
├── Modify for new endpoint
├── Run: make test-api
└── Iterate until passing
```

#### 8.2: Feature Development Workflow

```
Start feature implementation
│
├── Write/modify backend endpoint
│
├── Write API test for endpoint
│   └── make test-api (run full suite)
│       OR
│   └── make test-ui (run single test interactively)
│
├── Test fails (expected - TDD)
│
├── Implement endpoint logic
│
├── Re-run: make test-api
│
├── Test passes
│
└── Commit code + tests
```

#### 8.3: Debugging Workflow

```
Test failure
│
├── Read error message in terminal
│
├── If unclear:
│   ├── Run: make test-report
│   │   └── View detailed failure in HTML report
│   │
│   └── OR: make test-ui
│       └── Run specific test in UI mode
│           └── View trace with request/response details
│
├── Identify issue (auth, endpoint, assertion)
│
├── Fix code
│
└── Re-run: make test-api
```

---

### UX-9: Accessibility Considerations

While primarily a developer tool, accessibility matters for inclusive development teams.

#### 9.1: Terminal Output

- Use high-contrast symbols (checkmarks, X marks)
- Avoid color-only status indicators (always include text)
- Support for colorblind developers (green/red + symbols)

#### 9.2: HTML Report

- Keyboard navigable
- Screen reader compatible labels
- Sufficient color contrast for pass/fail indicators
- Text alternatives for status icons

---

### UX-10: Consistency with Project Conventions

The testing infrastructure aligns with existing project patterns.

#### 10.1: Naming Consistency

| Pattern | Source | Applied In Tests |
|---------|--------|-----------------|
| `make {action}` | Project Makefile | `make test`, `make test-api` |
| `snake_case` variables | Python backend | Environment variable names |
| `camelCase` properties | JavaScript | Test fixture properties |
| Descriptive test names | Testing best practices | `'admin can access admin endpoint'` |

#### 10.2: File Organization Consistency

```
project/
├── backend/           # Python FastAPI
├── frontend/          # Lit + TypeScript
│   └── e2e/           # Frontend E2E tests (browser-based)
├── keycloak/          # Identity setup
├── playwright/        # API tests (NEW - mirrors structure)
│   ├── tests/
│   ├── package.json
│   └── playwright.config.js
└── Makefile           # Unified command interface
```

---

### UI/UX Summary

This feature enhances developer experience through:

1. **Intuitive CLI**: Consistent Makefile targets and npm scripts with clear naming
2. **Visual Tools**: Playwright UI mode and HTML reports for debugging and exploration
3. **Ergonomic Fixtures**: Simple import patterns with IDE autocompletion support
4. **Helpful Errors**: Actionable error messages that guide toward resolution
5. **Task-Oriented Docs**: Quick-start guides and reference tables for different needs
6. **Smooth Workflows**: Optimized for common developer scenarios (onboarding, TDD, debugging)
7. **IDE Integration**: Support for VSCode Playwright extension and JetBrains IDEs
8. **Accessibility**: Color-blind friendly output, keyboard navigation, screen reader support

**Key Metric:** A new developer should go from zero to running their first API test in under 5 minutes.

---

## Security & Privacy Considerations

This section addresses security and privacy concerns related to the Playwright API testing infrastructure. While the testing infrastructure operates exclusively in development and CI environments, proper security practices prevent credential leakage, protect sensitive data, and establish good habits that extend to production systems.

---

### SP-1: Test Credential Security

#### SP-1.1: Credential Storage Principles

**Requirement:** Test credentials SHALL NOT be committed to version control in production-ready form.

**Current Implementation (Implementation-Manager Reference):**
The reference implementation stores test credentials in `test-users.js`:

```javascript
// tests/test-users.js
const TEST_USERS = {
  admin: {
    username: 'admin',
    password: 'admin123',
    // ...
  },
  // ...
};
```

**Security Considerations:**

| Aspect | Status | Rationale |
|--------|--------|-----------|
| Hardcoded passwords | ACCEPTABLE for template | These are well-known test credentials for development environments only |
| Password patterns | ACCEPTABLE | Follows predictable pattern (`username123`) for ease of use in development |
| Production credentials | NOT ALLOWED | Template explicitly documents these are development-only credentials |

**Mitigation Strategies:**

1. **Clear Documentation**: README and test files SHALL include prominent warnings that credentials are for development only:
   ```javascript
   /**
    * Test user fixtures for Playwright tests
    *
    * WARNING: These credentials are for DEVELOPMENT ONLY.
    * DO NOT use these passwords in production environments.
    * These users are pre-configured in the Keycloak development realm.
    */
   ```

2. **Environment Variable Override**: Support environment variables for CI/CD environments with different credential requirements:
   ```javascript
   const ADMIN_PASSWORD = process.env.TEST_ADMIN_PASSWORD || 'admin123';
   ```

3. **Gitignore Protection**: The `.gitignore` SHALL exclude any local environment files that might contain actual secrets:
   ```
   .env
   .env.local
   .env.*.local
   ```

---

#### SP-1.2: OAuth Client Secret Management

**Requirement:** OAuth client secrets used for the password grant flow SHALL be managed securely.

**Current Implementation (auth-helper.js):**
```javascript
const CLIENT_SECRET = 'backend-secret-change-in-production';
```

**Security Considerations:**

| Scenario | Approach |
|----------|----------|
| Local Development | Hardcoded default is acceptable since Keycloak is running locally in Docker |
| CI/CD Environment | Client secret should be injected via environment variable |
| Production | Password grant flow should NOT be used; use authorization code with PKCE |

**Template Implementation:**

```javascript
// auth-helper.js template
const KEYCLOAK_URL = process.env.KEYCLOAK_URL || 'http://localhost:{{ cookiecutter.keycloak_port }}';
const KEYCLOAK_REALM = process.env.KEYCLOAK_REALM || '{{ cookiecutter.keycloak_realm_name }}';
const CLIENT_ID = process.env.KEYCLOAK_CLIENT_ID || 'backend-api';
const CLIENT_SECRET = process.env.KEYCLOAK_CLIENT_SECRET || '{{ cookiecutter.backend_client_secret }}';
```

**Environment Variable Documentation:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `KEYCLOAK_URL` | `http://localhost:{{ cookiecutter.keycloak_port }}` | Keycloak server URL |
| `KEYCLOAK_REALM` | `{{ cookiecutter.keycloak_realm_name }}` | OAuth realm name |
| `KEYCLOAK_CLIENT_ID` | `backend-api` | OAuth client ID |
| `KEYCLOAK_CLIENT_SECRET` | Cookiecutter default | OAuth client secret |
| `TEST_ADMIN_PASSWORD` | `admin123` | Admin test user password |
| `TEST_USER_PASSWORD` | `test123` | Standard test user password |

---

### SP-2: Network Security Considerations

#### SP-2.1: Test Environment Isolation

**Requirement:** The API testing infrastructure SHALL operate within isolated development/CI environments.

**Network Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network (Internal)                 │
│                                                              │
│  ┌──────────┐     ┌──────────┐     ┌───────────────────┐    │
│  │Playwright│────▶│ Backend  │────▶│    PostgreSQL    │    │
│  │  Tests   │     │ :8000    │     │      :5432       │    │
│  └──────────┘     └──────────┘     └───────────────────┘    │
│       │                │                                     │
│       │                │                                     │
│       │                ▼                                     │
│       │          ┌──────────┐                               │
│       └─────────▶│ Keycloak │                               │
│                  │  :8080   │                               │
│                  └──────────┘                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
                    Host Machine
                   (localhost only)
```

**Security Controls:**

1. **No External Network Access**: Test services do not require internet access
2. **Docker Network Isolation**: Services communicate on internal Docker network
3. **Localhost Binding**: Host ports bind to localhost only in development
4. **No Production Data**: Test environment uses isolated database and Keycloak realm

---

#### SP-2.2: Transport Security

**Requirement:** Communication between test components SHALL be appropriately secured.

| Connection | Protocol | TLS Required | Rationale |
|------------|----------|--------------|-----------|
| Playwright -> Backend | HTTP | No (localhost) | Internal Docker network, no sensitive data in transit |
| Playwright -> Keycloak | HTTP | No (localhost) | Password grant over internal network |
| Backend -> Keycloak (JWKS) | HTTP | No (development) | Internal Docker network |
| CI Environment | HTTPS | Recommended | CI services may expose endpoints externally |

**CI/CD Security Recommendations:**

```javascript
// playwright.config.js - CI-aware configuration
const isCI = !!process.env.CI;
const baseURL = isCI
  ? process.env.API_URL  // CI provides the URL
  : 'http://localhost:8000';

module.exports = defineConfig({
  use: {
    baseURL,
    // Enable stricter TLS validation in CI
    ignoreHTTPSErrors: !isCI,
  },
});
```

---

### SP-3: Token Security

#### SP-3.1: JWT Token Handling

**Requirement:** Access tokens obtained during tests SHALL be handled securely.

**Token Lifecycle:**

```
┌──────────────────────────────────────────────────────────────────────┐
│                        Token Lifecycle in Tests                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  1. Token Request        2. Token Storage        3. Token Disposal   │
│     (per test)              (memory only)           (automatic)      │
│                                                                       │
│  getAccessToken() ──────▶ fixture context ──────▶ test completion    │
│                           (JavaScript heap)        (GC cleanup)      │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

**Security Controls:**

1. **No Persistent Token Storage**: Tokens are held in memory during test execution only
2. **Per-Test Token Lifecycle**: Each test gets fresh tokens via fixtures
3. **No Token Logging**: Token values SHALL NOT be logged in test output:
   ```javascript
   // auth-helper.js - Error handling without exposing tokens
   if (!response.ok()) {
     const text = await response.text();
     // DO NOT log: console.log(`Token: ${data.access_token}`);
     throw new Error(`Failed to get token: ${response.status()} ${text}`);
   }
   ```

4. **Short Token Lifetime**: Test tokens use Keycloak's default short-lived access tokens (typically 5 minutes)

---

#### SP-3.2: Invalid Token Testing Security

**Requirement:** Tests that verify token validation SHALL use intentionally invalid tokens, not leaked production tokens.

**Safe Test Patterns:**

```javascript
// SAFE: Using intentionally malformed tokens
test('should reject invalid token format', async ({ request }) => {
  const response = await request.get('/protected', {
    headers: { 'Authorization': 'Bearer invalid.token.here' },
  });
  expect(response.status()).toBe(401);
});

// SAFE: Using expired test tokens (generated, not captured)
test('should reject expired token', async ({ request }) => {
  // This is a well-known test JWT with exp in the past
  const expiredToken = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ.signature';

  const response = await request.get('/protected', {
    headers: { 'Authorization': `Bearer ${expiredToken}` },
  });
  expect(response.status()).toBe(401);
});
```

**Prohibited Patterns:**

```javascript
// PROHIBITED: Never capture and store real tokens from production
// const stolenToken = '<production-token>'; // NEVER DO THIS
```

---

### SP-4: Test Data Privacy

#### SP-4.1: Test User Data Isolation

**Requirement:** Test users SHALL NOT contain personally identifiable information (PII) that could be confused with real user data.

**Test User Data Standards:**

| Field | Pattern | Example | Rationale |
|-------|---------|---------|-----------|
| Username | Descriptive role | `admin`, `testuser`, `readonly` | Clearly identifies as test account |
| Email | @example.com domain | `admin@example.com` | RFC 2606 reserved domain for documentation |
| Password | Simple pattern | `admin123` | Indicates non-production credential |
| Names | Generic/obvious | `Test Admin`, `Test User` | Clearly fake names |

**Implementation:**
```javascript
// test-users.js - Privacy-safe test data
const TEST_USERS = {
  admin: {
    username: 'admin',
    password: 'admin123',
    email: 'admin@example.com',  // RFC 2606 reserved domain
    firstName: 'Test',
    lastName: 'Admin',
    roles: ['user', 'admin'],
  },
  // ...
};
```

---

#### SP-4.2: Test Artifact Security

**Requirement:** Test artifacts (reports, traces, screenshots) SHALL NOT be exposed publicly.

**Gitignore Configuration:**
```
# Playwright artifacts - may contain sensitive test data
playwright-report/
test-results/
blob-report/
playwright/.cache/

# Never commit trace files - may contain auth tokens in requests
*.zip  # Playwright trace archives
```

**Test Report Security:**

| Artifact Type | Content Risk | Handling |
|---------------|--------------|----------|
| HTML Report | API responses, headers | Gitignored, CI artifact with retention |
| Trace Files | Full request/response including auth headers | Gitignored, secure CI artifact storage |
| Screenshots | N/A (API tests have no UI) | Not applicable |
| Videos | N/A (API tests have no UI) | Not applicable |
| Console Logs | May contain test data | Review before sharing |

**CI/CD Artifact Handling:**
```yaml
# Example: Secure artifact handling in CI
- name: Upload Test Report
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright/playwright-report/
    retention-days: 7  # Limited retention
  if: always()
```

---

### SP-5: Authorization Testing Security

#### SP-5.1: Role-Based Access Control (RBAC) Testing

**Requirement:** Tests SHALL verify both positive and negative authorization cases.

**Test Coverage Matrix:**

| Endpoint | Admin | User | ReadOnly | Manager | Service | Unauthenticated |
|----------|-------|------|----------|---------|---------|-----------------|
| `GET /` | 200 | 200 | 200 | 200 | 200 | 200 |
| `GET /health` | 200 | 200 | 200 | 200 | 200 | 200 |
| `GET /protected` | 200 | 200 | 200 | 200 | 200 | 401/403 |
| `GET /admin` | 200 | 403 | 403 | 403 | 403 | 401/403 |

**Security Testing Patterns:**

```javascript
test.describe('Authorization Boundary Tests', () => {
  test('admin can access admin endpoint', async ({ adminRequest }) => {
    const response = await adminRequest.get('/admin');
    expect(response.ok()).toBeTruthy();
  });

  test('regular user cannot access admin endpoint', async ({ userRequest }) => {
    const response = await userRequest.get('/admin');
    expect(response.status()).toBe(403);
  });

  test('unauthenticated request is rejected', async ({ request }) => {
    const response = await request.get('/admin');
    expect([401, 403]).toContain(response.status());
  });
});
```

---

#### SP-5.2: Privilege Escalation Prevention Testing

**Requirement:** Tests SHALL verify that users cannot escalate their privileges.

**Test Scenarios:**

1. **Role Injection Prevention:**
   ```javascript
   test('cannot inject roles via API', async ({ userRequest }) => {
     const response = await userRequest.post('/change-role', {
       data: { role: 'admin' },  // Attempt to self-promote
     });
     expect(response.status()).toBe(403);
   });
   ```

2. **Tenant Boundary Testing:**
   ```javascript
   test('cannot access other tenant data', async ({ authenticatedRequest }) => {
     // tenant-1 user cannot access tenant-2 data
     const response = await authenticatedRequest.user.get('/data/tenant-2-id');
     expect(response.status()).toBe(404);  // RLS hides data
   });
   ```

---

### SP-6: Secret Rotation and Lifecycle

#### SP-6.1: Development Credential Lifecycle

**Requirement:** Template SHALL document credential rotation procedures.

**Credential Types and Rotation:**

| Credential | Location | Rotation Frequency | Procedure |
|------------|----------|-------------------|-----------|
| Test user passwords | `test-users.js` | On template update | Update Keycloak realm script |
| OAuth client secret | `auth-helper.js` / ENV | Per environment | Keycloak admin console |
| Keycloak admin | `compose.yml` / ENV | Per project | Environment variable |
| Database password | `.env` | Per project | Environment variable |

**Documentation Requirement:**
The template README SHALL include:
```markdown
## Credential Management

### Development Credentials
The following credentials are pre-configured for local development:

| Service | Username | Password | Notes |
|---------|----------|----------|-------|
| Keycloak Admin | admin | admin | Only in development |
| Test Users | See test-users.js | <username>123 | Development only |

### Production Considerations
Before deploying to production:
1. Change all default passwords
2. Use environment variables for all secrets
3. Enable Keycloak HTTPS
4. Rotate OAuth client secrets
```

---

### SP-7: Security in CI/CD Pipelines

#### SP-7.1: CI Environment Security

**Requirement:** CI/CD pipelines SHALL handle test credentials securely.

**GitHub Actions Best Practices:**

```yaml
# Example: Secure secrets handling
jobs:
  api-tests:
    runs-on: ubuntu-latest
    env:
      # Use GitHub Secrets for CI credentials
      KEYCLOAK_CLIENT_SECRET: ${{ secrets.KEYCLOAK_CLIENT_SECRET }}
      TEST_ADMIN_PASSWORD: ${{ secrets.TEST_ADMIN_PASSWORD }}
    steps:
      - uses: actions/checkout@v4
      - name: Run API Tests
        run: |
          cd playwright
          npm ci
          npx playwright test
```

**Secret Masking:**
```yaml
# Secrets are automatically masked in logs
# The value of KEYCLOAK_CLIENT_SECRET will appear as ***
```

---

#### SP-7.2: Trace and Report Security in CI

**Requirement:** Test artifacts containing sensitive data SHALL be protected.

**Recommendations:**

1. **Trace Collection**: Only enable tracing on failure to minimize data exposure:
   ```javascript
   module.exports = defineConfig({
     use: {
       trace: 'on-first-retry',  // Only collect on failure
     },
   });
   ```

2. **Artifact Retention**: Limit retention period for test artifacts:
   ```yaml
   - name: Upload Trace
     uses: actions/upload-artifact@v3
     with:
       retention-days: 3  # Short retention
   ```

3. **Access Control**: Ensure only authorized team members can access CI artifacts

---

### SP-8: Compliance Considerations

#### SP-8.1: GDPR and Data Protection

**Requirement:** Test infrastructure SHALL comply with data protection requirements.

**Compliance Controls:**

| Requirement | Implementation |
|-------------|----------------|
| No real user data | Test users use fake data with @example.com emails |
| Data minimization | Tests use minimum necessary data |
| Right to erasure | Test environments can be destroyed completely |
| Data isolation | Development environment is isolated from production |

---

#### SP-8.2: Audit Trail

**Requirement:** Test execution SHALL maintain appropriate audit logs.

**Logging Configuration:**

```javascript
// playwright.config.js
module.exports = defineConfig({
  reporter: [
    ['html'],
    ['list'],  // Console output for CI logs
  ],
  // Test execution is logged by CI system
});
```

**Audit Information Captured:**
- Test execution timestamp
- Test pass/fail status
- CI pipeline run ID
- Git commit SHA

---

### SP-9: Security Documentation Requirements

#### SP-9.1: README Security Section

**Requirement:** The playwright/README.md SHALL include a security section.

**Required Content:**

```markdown
## Security Considerations

### Development Credentials
- All credentials in this directory are for **DEVELOPMENT ONLY**
- Test users use predictable passwords (username + "123")
- These credentials must NEVER be used in production

### CI/CD Usage
- Use environment variables for credentials in CI
- Store secrets using your CI provider's secret management
- Never log token values

### Test Artifacts
- HTML reports and traces may contain sensitive request data
- These files are gitignored and should not be committed
- Use appropriate access controls for CI artifacts
```

---

### SP-10: Security Checklist

**Pre-Implementation Checklist:**

- [ ] Test credentials are clearly marked as development-only
- [ ] Environment variable overrides are implemented for all secrets
- [ ] .gitignore excludes all test artifacts
- [ ] README includes security documentation
- [ ] No PII in test user data (using @example.com domain)
- [ ] Token values are never logged
- [ ] CI secrets are properly masked

**Post-Implementation Verification:**

- [ ] `git status` shows no test artifacts
- [ ] `grep -r "password" .` shows only documented test passwords
- [ ] Environment variable overrides work correctly
- [ ] CI pipeline masks secret values in logs
- [ ] Test reports do not expose sensitive data inappropriately

---

**References:**
- [Playwright Environment Variables Management (BrowserStack)](https://www.browserstack.com/guide/playwright-env-variables)
- [Handling Authentication in Playwright Security Best Practices](https://netizensreport.com/handling-authentication-in-playwright-security-best-practices/)
- [Security Best Practices Standards for Playwright](https://www.codingrules.ai/rules/security-best-practices-standards-for-playwright)
- [Playwright MCP Security Best Practices (Awesome Testing)](https://www.awesome-testing.com/2025/11/playwright-mcp-security)
- RFC 2606 - Reserved Top Level DNS Names (example.com)

---

## Testing Strategy

This section defines the comprehensive testing strategy for validating the Playwright API testing infrastructure itself. Since this feature provides testing capabilities for projects generated from the cookiecutter template, we must ensure the testing infrastructure is reliable, maintainable, and correctly implemented before it is used to test other applications.

---

### TS-1: Testing Philosophy and Principles

#### 1.1: Meta-Testing Approach

This feature is unique in that it provides testing infrastructure for other projects. The testing strategy must address two distinct levels:

| Level | Description | Scope |
|-------|-------------|-------|
| **Level 1: Infrastructure Testing** | Verify that the Playwright API testing infrastructure works correctly | Testing the testing framework itself |
| **Level 2: Template Testing** | Verify that generated projects include working API tests | Testing the cookiecutter template output |

**Guiding Principles:**

1. **Test Independence**: Each test should be completely isolated from other tests, with its own local storage, session storage, data, cookies, and authentication context. This improves reproducibility and prevents cascading failures.

2. **Comprehensive Validation**: Beyond status codes, validate response bodies, headers, and data integrity to ensure thorough API coverage.

3. **Realistic Test Data**: Use realistic but safe test data following RFC 2606 (example.com domain) and faker-js patterns where dynamic data is needed.

4. **CI/CD Integration**: All tests must run reliably in CI environments with appropriate retry logic and trace collection for debugging.

5. **Clear Assertions**: Use descriptive assertion messages that clearly indicate what is being verified and why.

---

### TS-2: Unit Testing Approach

#### 2.1: Auth Helper Unit Tests

The `auth-helper.js` module contains critical authentication logic that must be unit tested.

**Test File:** `playwright/tests/__tests__/auth-helper.test.js` (optional, for template development)

**Test Cases:**

| ID | Test Case | Input | Expected Output | Priority |
|----|-----------|-------|-----------------|----------|
| AH-01 | `getAccessToken` returns valid token on success | Valid credentials | JWT string | Must Have |
| AH-02 | `getAccessToken` throws on invalid credentials | Invalid password | Error with message containing "401" | Must Have |
| AH-03 | `getAccessToken` throws on connection failure | Keycloak unavailable | Error with descriptive message | Must Have |
| AH-04 | `getAdminToken` returns token for admin user | Valid Keycloak | JWT string | Should Have |
| AH-05 | `getTestUserToken` returns token for test user | Valid Keycloak | JWT string | Should Have |
| AH-06 | `authHeader` formats token correctly | Token string | `{ Authorization: 'Bearer {token}' }` | Must Have |
| AH-07 | `authHeader` handles empty token | Empty string | `{ Authorization: 'Bearer ' }` | Should Have |

**Note:** Unit tests for auth-helper are optional in the template since the module is exercised through integration tests. However, during template development, these tests validate correctness before integration.

#### 2.2: Test Users Module Unit Tests

The `test-users.js` module provides user fixtures and query functions.

**Test Cases:**

| ID | Test Case | Input | Expected Output | Priority |
|----|-----------|-------|-----------------|----------|
| TU-01 | `TEST_USERS` contains 6 user definitions | N/A | Object with 6 keys | Must Have |
| TU-02 | Each user has required properties | N/A | username, password, email, roles, description | Must Have |
| TU-03 | `getUserByRole('admin')` returns admin user | `'admin'` | Admin user object | Should Have |
| TU-04 | `getUserByRole('nonexistent')` returns undefined | `'nonexistent'` | `undefined` | Should Have |
| TU-05 | `getUsersByRole('user')` returns users with user role | `'user'` | Array with 5 users | Should Have |
| TU-06 | `getAllUsers()` returns all 6 users | N/A | Array with 6 user objects | Should Have |

---

### TS-3: Integration Testing Approach

Integration tests verify that the Playwright API testing infrastructure correctly integrates with Keycloak and the backend API. These tests form the primary validation mechanism.

#### 3.1: Authentication Integration Tests

**Test File:** `playwright/tests/api-endpoints.api.spec.js`

**Test Suite: "Token Validation"**

| ID | Test Case | Scenario | Expected Behavior | Fixtures Used |
|----|-----------|----------|-------------------|---------------|
| IT-01 | Valid admin token succeeds | Get token for admin, use on protected endpoint | 200 OK, user info in response | Manual auth |
| IT-02 | Valid user token succeeds | Get token for testuser, use on protected endpoint | 200 OK, user info in response | Manual auth |
| IT-03 | Invalid token format rejected | Use malformed token string | 401 Unauthorized | `request` (raw) |
| IT-04 | Fake JWT rejected | Use JWT with invalid signature | 401 Unauthorized | `request` (raw) |
| IT-05 | Missing token rejected | No Authorization header | 403 Forbidden | `request` (raw) |

**Test Suite: "Keycloak Integration"**

| ID | Test Case | Scenario | Expected Behavior |
|----|-----------|----------|-------------------|
| KI-01 | Token endpoint accessible | POST to Keycloak token endpoint | 200 OK with access_token |
| KI-02 | Invalid credentials rejected | Wrong password in token request | 401 with invalid_grant error |
| KI-03 | All test users can authenticate | Loop through TEST_USERS, get token for each | All 6 users return valid tokens |

#### 3.2: Fixture Integration Tests

**Test File:** `playwright/tests/api-with-fixtures.api.spec.js`

**Test Suite: "API Tests with Fixtures"**

| ID | Test Case | Fixture | Endpoint | Expected |
|----|-----------|---------|----------|----------|
| FI-01 | Admin fixture accesses admin endpoint | `adminRequest` | `/admin` | 200 OK, admin role verified |
| FI-02 | User fixture accesses protected endpoint | `userRequest` | `/protected` | 200 OK, user role verified |
| FI-03 | User fixture denied admin endpoint | `userRequest` | `/admin` | 403 with role error |
| FI-04 | Multiple contexts in single test | `authenticatedRequest` | Multiple | Each user has correct access |
| FI-05 | ReadOnly fixture has correct roles | `readOnlyRequest` | `/protected` | 200 OK, readonly role present |
| FI-06 | Fixture exposes user info | `adminRequest` | N/A | `.user.username` equals 'admin' |
| FI-07 | Fixture exposes raw token | `adminRequest` | N/A | `.token` is non-empty string |

**Test Suite: "Test User Scenarios"**

| ID | Test Case | Fixture | Purpose |
|----|-----------|---------|---------|
| TUS-01 | newUser fixture for onboarding | `authenticatedRequest.newUser` | Verify newuser context works |
| TUS-02 | serviceAccount fixture for API integration | `authenticatedRequest.serviceAccount` | Verify service role present |

---

### TS-4: End-to-End Testing Approach

E2E tests verify the complete workflow from running `make test-api` to seeing test results.

#### 4.1: Template Generation E2E Tests

These tests run during template development to ensure generated projects have working API tests.

**Test Workflow:**

```
1. Generate project from template
   └── cookiecutter . --no-input

2. Start Docker services
   └── make docker-up

3. Setup Keycloak realm
   └── ./keycloak/setup-realm.sh

4. Install Playwright dependencies
   └── make test-install

5. Run API tests
   └── make test-api

6. Verify exit code and output
   └── All tests should pass
```

**E2E Test Cases:**

| ID | Test Case | Verification | Success Criteria |
|----|-----------|--------------|------------------|
| E2E-01 | Generated project structure | Check files exist | All playwright files created |
| E2E-02 | npm install succeeds | Run npm install | Exit code 0 |
| E2E-03 | Playwright config valid | Run `npx playwright test --list` | Lists test projects |
| E2E-04 | API tests pass with running services | Run full test suite | All tests pass |
| E2E-05 | HTML report generated | Check file exists | `playwright-report/index.html` exists |

#### 4.2: CI/CD E2E Verification

**CI Environment Validation:**

| ID | Scenario | Configuration | Expected Behavior |
|----|----------|---------------|-------------------|
| CI-01 | CI mode detection | `CI=true` | Workers set to 1 |
| CI-02 | Retry logic in CI | `CI=true` | 2 retries on failure |
| CI-03 | forbidOnly in CI | `CI=true` with `.only()` test | Fail with error |
| CI-04 | Trace collection | Test retry occurs | Trace available in report |
| CI-05 | HTML report upload | CI artifact upload | Report accessible |

---

### TS-5: Role-Based Access Control (RBAC) Test Matrix

The RBAC test matrix ensures comprehensive coverage of role-based permissions.

#### 5.1: Permission Matrix

| Endpoint | admin | user | readonly | manager | service | unauthenticated |
|----------|-------|------|----------|---------|---------|-----------------|
| `GET /` | 200 | 200 | 200 | 200 | 200 | 200 |
| `GET /health` | 200 | 200 | 200 | 200 | 200 | 200 |
| `GET /protected` | 200 | 200 | 200 | 200 | 200 | 403 |
| `GET /admin` | 200 | 403 | 403 | 403 | 403 | 403 |
| `GET /auth/me` | 200 | 200 | 200 | 200 | 200 | 403 |

**Test Coverage Requirement:** Each cell in the matrix must have at least one test case.

#### 5.2: RBAC Test Implementation

**Recommended Pattern:**

```javascript
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('RBAC: Admin Endpoint Access', () => {
  test('admin can access admin endpoint', async ({ adminRequest }) => {
    const response = await adminRequest.get('/admin');
    expect(response.ok()).toBeTruthy();
  });

  test('regular user cannot access admin endpoint', async ({ userRequest }) => {
    const response = await userRequest.get('/admin');
    expect(response.status()).toBe(403);
    const data = await response.json();
    expect(data.detail).toContain("Role 'admin' required");
  });

  test('readonly user cannot access admin endpoint', async ({ readOnlyRequest }) => {
    const response = await readOnlyRequest.get('/admin');
    expect(response.status()).toBe(403);
  });

  // ... additional role tests
});
```

---

### TS-6: Error Handling and Edge Case Testing

#### 6.1: Authentication Error Test Cases

| ID | Scenario | Input | Expected Error | Test Location |
|----|----------|-------|----------------|---------------|
| ERR-01 | Wrong password | `getAccessToken(req, 'admin', 'wrong')` | Error containing "401" | api-endpoints |
| ERR-02 | Wrong username | `getAccessToken(req, 'nobody', 'pass')` | Error containing "401" | api-endpoints |
| ERR-03 | Keycloak down | Token request when Keycloak stopped | Error with connection message | Manual test |
| ERR-04 | Wrong realm | Modified KEYCLOAK_REALM env var | Error containing "404" | Manual test |
| ERR-05 | Wrong client secret | Modified CLIENT_SECRET | Error containing "401" | Manual test |

#### 6.2: API Error Response Test Cases

| ID | Scenario | Request | Expected Response |
|----|----------|---------|-------------------|
| API-01 | Invalid JSON body | POST with malformed JSON | 422 Unprocessable Entity |
| API-02 | Missing required field | POST without required field | 422 with field error |
| API-03 | Resource not found | GET /nonexistent | 404 Not Found |
| API-04 | Method not allowed | POST to GET-only endpoint | 405 Method Not Allowed |

#### 6.3: Token Edge Cases

| ID | Scenario | Token Value | Expected Response |
|----|----------|-------------|-------------------|
| TOK-01 | Empty token | `''` | 401 or 403 |
| TOK-02 | Malformed JWT | `'not.a.jwt'` | 401 |
| TOK-03 | Valid structure, invalid signature | Fake JWT | 401 |
| TOK-04 | Expired token | Token after expiry (not easily testable) | N/A - out of scope |
| TOK-05 | Whitespace token | `'   '` | 401 or 403 |

---

### TS-7: Performance Testing Considerations

While comprehensive performance testing is out of scope (per OS-3), basic performance validation ensures the testing infrastructure does not introduce significant overhead.

#### 7.1: Performance Baseline Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Token retrieval time | < 500ms per token | Playwright timing |
| Protected endpoint response | < 200ms | Playwright timing |
| Full test suite (10 tests) | < 30 seconds | CI timing |
| Parallel execution overhead | < 10% vs sequential | Compare with `workers: 1` |

#### 7.2: Performance Test Cases

| ID | Scenario | Measurement |
|----|----------|-------------|
| PERF-01 | Single test execution time | Record start/end time |
| PERF-02 | Token caching effectiveness | Compare 1 token vs 6 token tests |
| PERF-03 | Parallel test speedup | Compare workers: auto vs workers: 1 |

**Note:** Performance tests are informational and should not block CI pipeline.

---

### TS-8: Test Data Management

#### 8.1: Test User Data

Test users are pre-configured in Keycloak and defined in `test-users.js`. Data synchronization is validated by:

1. **Keycloak User Existence Check**: Attempting authentication validates user exists
2. **Role Assignment Check**: Token claims include expected roles
3. **Credential Match Check**: Successful authentication validates password

**Test User Validation Test:**

```javascript
test('all test users exist in Keycloak', async ({ request }) => {
  const { getAllUsers } = require('./test-users');
  const { getAccessToken } = require('./auth-helper');

  for (const user of getAllUsers()) {
    const token = await getAccessToken(request, user.username, user.password);
    expect(token).toBeTruthy();
  }
});
```

#### 8.2: Test Data Cleanup

API tests should not require data cleanup since they:
- Use existing Keycloak test users (no user creation)
- Do not create persistent application data in basic tests
- Each test has isolated authentication context

For tests that create data (POST endpoints), follow the cleanup pattern:

```javascript
test('create and cleanup resource', async ({ userRequest }) => {
  // Create
  const createResponse = await userRequest.post('/resources', {
    data: { name: 'Test Resource' }
  });
  const resourceId = (await createResponse.json()).id;

  try {
    // Test assertions
    expect(createResponse.status()).toBe(201);
  } finally {
    // Cleanup
    await userRequest.delete(`/resources/${resourceId}`);
  }
});
```

---

### TS-9: Test Execution Modes

#### 9.1: Local Development Mode

**Command:** `make test-api` or `npm test`

**Behavior:**
- Uses default Playwright workers (parallel execution)
- No retries (immediate failure feedback)
- Traces collected on first retry only
- Web server auto-start if services not running
- HTML report generated after run

**Developer Workflow:**
1. Make code changes
2. Run `make test-api`
3. Review failures in terminal
4. For debugging: `make test-ui` or `make test-debug`

#### 9.2: Interactive UI Mode

**Command:** `make test-ui` or `npm run test:ui`

**Features:**
- Visual test explorer
- Watch mode for file changes
- Run individual tests by clicking
- View request/response details in trace viewer
- Time travel debugging

**Best For:**
- Debugging failing tests
- Exploring test coverage
- Writing new tests iteratively

#### 9.3: Debug Mode

**Command:** `make test-debug` or `npm run test:debug`

**Features:**
- Playwright Inspector opens
- Step through test execution
- Inspect network requests
- Pause on failures

**Best For:**
- Deep debugging of complex issues
- Understanding fixture behavior
- Troubleshooting authentication

#### 9.4: CI Mode

**Command:** `CI=true npm test`

**Behavior:**
- Single worker (`workers: 1`) for stability
- 2 retries on failure
- `forbidOnly: true` prevents `.only()` commits
- No web server auto-start (services pre-started)
- Traces collected on retry for debugging
- Exit code reflects test results

**CI Pipeline Integration:**

```yaml
# Example GitHub Actions step
- name: Run Playwright API Tests
  run: |
    cd playwright
    npm ci
    CI=true npm test
  env:
    BASE_URL: http://localhost:8000
    KEYCLOAK_URL: http://localhost:8080
```

---

### TS-10: Test Reporting and Debugging

#### 10.1: HTML Report Analysis

**Location:** `playwright/playwright-report/index.html`

**Report Contents:**
- Test results summary (passed, failed, skipped)
- Test duration breakdown
- Grouped by test file and describe blocks
- Expandable test details
- Request/response data for each API call
- Trace viewer for failed/retried tests

**Access Command:** `make test-report` or `npx playwright show-report`

#### 10.2: Trace Analysis for API Tests

Traces capture detailed information for debugging:

| Trace Element | Information | Debug Use |
|---------------|-------------|-----------|
| Network tab | Request method, URL, headers, body | Verify request format |
| Response details | Status, headers, JSON body | Check API response |
| Timing | Request duration | Identify slow endpoints |
| Headers | Authorization header value | Verify token presence |

**Trace Collection Settings:**

```javascript
// playwright.config.js
{
  use: {
    trace: 'on-first-retry',  // Collect trace only when test is retried
  }
}
```

#### 10.3: Debugging Checklist

When tests fail, follow this checklist:

1. **Read Error Message**: Check terminal output for specific failure reason
2. **Check Services Running**: `make docker-up` ensures services are available
3. **Verify Keycloak Users**: Ensure `./keycloak/setup-realm.sh` has been run
4. **View HTML Report**: `make test-report` for detailed failure info
5. **Use UI Mode**: `make test-ui` for interactive debugging
6. **Check Network Tab**: In trace viewer, verify request/response details
7. **Validate Token**: Decode JWT at jwt.io to check claims
8. **Check Endpoint**: Manually test endpoint with curl to isolate issue

---

### TS-11: Test Organization and Naming

#### 11.1: File Naming Convention

| Pattern | Purpose | Example |
|---------|---------|---------|
| `*.api.spec.js` | API test files (matched by config) | `api-endpoints.api.spec.js` |
| `*.js` (no .spec) | Utility modules | `auth-helper.js`, `fixtures.js` |
| `__tests__/*.test.js` | Optional unit tests | `auth-helper.test.js` |

#### 11.2: Test Naming Convention

**Format:** `{action} {subject} {condition/result}`

**Examples:**
- `admin can access admin endpoint`
- `regular user cannot access admin endpoint`
- `protected endpoint rejects unauthenticated requests`
- `should reject invalid token format`

**Test Suite Naming:**

```javascript
test.describe('Public API Endpoints', () => { ... });
test.describe('Protected API Endpoints', () => { ... });
test.describe('Admin-Only API Endpoints', () => { ... });
test.describe('Token Validation', () => { ... });
test.describe('RBAC: Endpoint Access', () => { ... });
```

#### 11.3: Test Organization by Category

| Category | Focus | Example Tests |
|----------|-------|---------------|
| Public Endpoints | Unauthenticated access | Health check, root endpoint |
| Protected Endpoints | Authenticated access | User info, protected routes |
| Admin Endpoints | Role-based access | Admin-only routes |
| Token Validation | Security edge cases | Invalid tokens, missing auth |
| Fixtures | Fixture correctness | User context, token exposure |
| Error Handling | Error responses | Invalid input, not found |

---

### TS-12: Test Coverage Requirements

#### 12.1: Minimum Coverage Criteria

Before this feature is considered complete, the following test coverage must be achieved:

| Area | Minimum Tests | Coverage Target |
|------|---------------|-----------------|
| Public endpoints | 2 | All public endpoints tested |
| Protected endpoints | 3 | Authenticated access verified |
| Admin endpoints | 3 | Role-based access verified |
| Token validation | 2 | Invalid token handling tested |
| Fixtures | 5 | All fixture types exercised |
| Error handling | 2 | Common error scenarios covered |

**Total Minimum Tests:** 17 tests across 6 categories

#### 12.2: Coverage Verification

**Verification Command:** `npx playwright test --list`

**Output Should Show:**
- At least 17 test cases
- Tests grouped by test file
- Tests distributed across test suites

#### 12.3: Coverage Gaps to Monitor

| Gap Area | Risk | Mitigation |
|----------|------|------------|
| Service account tests | May not exercise service role | Include serviceAccount fixture test |
| POST/PUT/PATCH tests | Only GET methods in examples | Document pattern for future tests |
| Multi-tenant isolation | Cross-tenant access not tested | Documented as out of scope (OS-4) |
| Token refresh | Long-running tests may expire | Tests complete within token lifetime |

---

### TS-13: Test Maintenance Strategy

#### 13.1: Keeping Tests Current

As the backend API evolves, tests must be updated to match. Follow these practices:

1. **Endpoint Changes**: Update tests when API endpoints are added, modified, or removed
2. **Role Changes**: Update RBAC matrix when new roles are introduced
3. **User Changes**: Update `test-users.js` and Keycloak setup when test users change
4. **Configuration Changes**: Update environment variable documentation when config changes

#### 13.2: Test Review Checklist

When reviewing API test changes:

- [ ] Test names clearly describe what is being tested
- [ ] Assertions validate both status code and response body
- [ ] Fixtures are used appropriately (not manual auth for simple cases)
- [ ] Error cases include expected error message validation
- [ ] No hardcoded credentials outside of test-users.js
- [ ] Tests are independent and can run in any order
- [ ] Cleanup is performed for tests that create data

#### 13.3: Deprecation Handling

When deprecating tests or fixtures:

1. Mark deprecated items with TODO comments
2. Add deprecation notices to documentation
3. Create migration path for dependent tests
4. Remove after one major version cycle

---

### Testing Strategy Summary

The testing strategy for the Playwright API testing infrastructure is comprehensive and multi-layered:

| Layer | Purpose | Approach |
|-------|---------|----------|
| Unit Testing | Validate individual modules | Optional during development, exercised through integration |
| Integration Testing | Verify Keycloak and API integration | Primary testing mechanism via api-endpoints and api-with-fixtures specs |
| E2E Testing | Validate complete workflow | Template generation and full test suite execution |
| RBAC Testing | Ensure permission boundaries | Matrix-based coverage of all role/endpoint combinations |
| Error Testing | Verify error handling | Authentication failures, invalid tokens, API errors |

**Key Metrics:**

| Metric | Target |
|--------|--------|
| Minimum test count | 17 tests |
| Test execution time | < 30 seconds |
| CI reliability | Zero false positives |
| RBAC coverage | 100% of matrix cells |

**Quality Gates:**

1. All tests must pass before merge
2. No `.only()` tests in committed code
3. Test coverage review for new endpoints
4. HTML report review for failures

This testing strategy ensures the Playwright API testing infrastructure is reliable, well-documented, and provides a solid foundation for testing projects generated from the cookiecutter template.

---

## Implementation Phases

This section defines the logical breakdown of work for implementing Playwright API testing support. The implementation follows a phased approach that allows for incremental delivery and validation at each stage.

---

### Phase Overview

| Phase | Name | Duration Estimate | Dependencies | Deliverables |
|-------|------|-------------------|--------------|--------------|
| 1 | Foundation Setup | 2-3 hours | None | Directory structure, package.json, playwright.config.js |
| 2 | Authentication Infrastructure | 3-4 hours | Phase 1 | auth-helper.js, test-users.js |
| 3 | Fixture System | 2-3 hours | Phase 2 | fixtures.js with authenticated request contexts |
| 4 | Example Test Suites | 2-3 hours | Phase 3 | api-endpoints.api.spec.js, api-with-fixtures.api.spec.js |
| 5 | Keycloak Integration | 2-3 hours | Phase 1 | Updated setup-realm.sh with test users and roles |
| 6 | Build System Integration | 1-2 hours | Phase 1 | Makefile targets, npm scripts |
| 7 | Documentation | 2-3 hours | Phases 1-6 | README.md, QUICK_START.md |
| 8 | Validation and Testing | 2-3 hours | Phases 1-7 | End-to-end validation, CI readiness |

**Total Estimated Effort:** 16-24 hours (2-3 days)

---

### IP-1: Phase 1 - Foundation Setup

**Objective:** Establish the basic Playwright project structure within the cookiecutter template.

**Entry Criteria:**
- Access to the cookiecutter template repository
- Understanding of cookiecutter template variable syntax

**Deliverables:**

#### 1.1: Create Playwright Directory Structure

Create the following structure within the template:

```
template/{{cookiecutter.project_slug}}/
└── playwright/
    ├── tests/           # Test files directory (empty initially)
    ├── package.json     # Node.js dependencies
    ├── playwright.config.js  # Playwright configuration
    └── .gitignore       # Playwright-specific ignores
```

**Files to Create:**

| File | Requirements | Reference |
|------|--------------|-----------|
| `playwright/package.json` | FR-1.2 | `/home/ty/workspace/project-starter/implementation-manager/playwright/package.json` |
| `playwright/playwright.config.js` | FR-1.3 | `/home/ty/workspace/project-starter/implementation-manager/playwright/playwright.config.js` |
| `playwright/.gitignore` | FR-1.4 | Standard Playwright ignores |

#### 1.2: Package.json Configuration

```json
{
  "name": "{{ cookiecutter.project_slug }}-playwright",
  "version": "1.0.0",
  "description": "API tests for {{ cookiecutter.project_name }}",
  "main": "index.js",
  "directories": {
    "test": "tests"
  },
  "scripts": {
    "test": "playwright test",
    "test:api": "playwright test --project='API Tests'",
    "test:headed": "playwright test --headed",
    "test:debug": "playwright test --debug",
    "test:ui": "playwright test --ui",
    "report": "playwright show-report"
  },
  "keywords": ["playwright", "api-testing", "{{ cookiecutter.project_slug }}"],
  "author": "",
  "license": "ISC",
  "type": "commonjs",
  "devDependencies": {
    "@playwright/test": "^1.56.1"
  }
}
```

#### 1.3: Playwright Configuration

Configure playwright.config.js with:
- `testDir`: `./tests`
- `timeout`: 30000ms
- `fullyParallel`: true
- `forbidOnly`: CI detection
- `retries`: 2 in CI, 0 locally
- `workers`: 1 in CI, parallel locally
- `reporter`: html
- `baseURL`: Backend URL using cookiecutter variable
- `trace`: on-first-retry
- `testMatch`: `*.api.spec.js` pattern
- `webServer`: Docker Compose auto-start for local development

#### 1.4: Git Ignore Configuration

```gitignore
# Playwright
/test-results/
/playwright-report/
/blob-report/
/playwright/.cache/
node_modules/
```

**Exit Criteria:**
- [ ] `playwright/` directory exists in template
- [ ] `package.json` contains correct npm scripts
- [ ] `playwright.config.js` uses cookiecutter variables for URLs
- [ ] `.gitignore` excludes test artifacts
- [ ] `npm install` succeeds when run in generated project

**Verification:**
```bash
# Generate project from template
cookiecutter template/
cd my-project/playwright
npm install
npx playwright --version  # Should output version
```

---

### IP-2: Phase 2 - Authentication Infrastructure

**Objective:** Implement the Keycloak authentication helper module that enables tests to obtain JWT tokens.

**Entry Criteria:**
- Phase 1 complete
- Understanding of Keycloak OAuth 2.0 token endpoint

**Deliverables:**

#### 2.1: Create auth-helper.js

Location: `template/{{cookiecutter.project_slug}}/playwright/tests/auth-helper.js`

**Implementation Requirements (FR-2.1 through FR-2.5):**

```javascript
/**
 * Authentication helper for Playwright API tests
 * Provides functions to obtain JWT tokens from Keycloak
 */

// Configuration with cookiecutter variables and environment overrides
const KEYCLOAK_URL = process.env.KEYCLOAK_URL || 'http://localhost:{{ cookiecutter.keycloak_port }}';
const KEYCLOAK_REALM = process.env.KEYCLOAK_REALM || '{{ cookiecutter.keycloak_realm_name }}';
const CLIENT_ID = '{{ cookiecutter.keycloak_backend_client_id }}';
const CLIENT_SECRET = '{{ cookiecutter.keycloak_backend_client_id }}-secret';

/**
 * Get OAuth access token using password grant
 * @param {import('@playwright/test').APIRequestContext} request
 * @param {string} username
 * @param {string} password
 * @returns {Promise<string>} Access token
 */
async function getAccessToken(request, username, password) {
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
    throw new Error(`Failed to get token for '${username}': ${response.status()} ${text}`);
  }

  const data = await response.json();
  return data.access_token;
}

// Convenience functions
async function getAdminToken(request) {
  return getAccessToken(request, 'admin', 'admin123');
}

async function getTestUserToken(request) {
  return getAccessToken(request, 'testuser', 'test123');
}

function authHeader(token) {
  return { 'Authorization': `Bearer ${token}` };
}

module.exports = {
  getAccessToken,
  getAdminToken,
  getTestUserToken,
  authHeader,
  KEYCLOAK_URL,
  KEYCLOAK_REALM,
};
```

#### 2.2: Create test-users.js

Location: `template/{{cookiecutter.project_slug}}/playwright/tests/test-users.js`

**Implementation Requirements (FR-3.1 through FR-3.3):**

```javascript
/**
 * Test user definitions for Playwright API tests
 * These users must exist in Keycloak (created by setup-realm.sh)
 */

const TEST_USERS = {
  admin: {
    username: 'admin',
    password: 'admin123',
    email: 'admin@example.com',
    roles: ['user', 'admin'],
    description: 'Full admin access for privileged operations',
  },
  user: {
    username: 'testuser',
    password: 'test123',
    email: 'test@example.com',
    roles: ['user'],
    description: 'Standard user for typical authenticated flows',
  },
  readOnly: {
    username: 'readonly',
    password: 'readonly123',
    email: 'readonly@example.com',
    roles: ['user', 'readonly'],
    description: 'Read-only access for viewing without modification',
  },
  newUser: {
    username: 'newuser',
    password: 'newuser123',
    email: 'newuser@example.com',
    roles: ['user'],
    description: 'Fresh account for onboarding flow tests',
  },
  manager: {
    username: 'manager',
    password: 'manager123',
    email: 'manager@example.com',
    roles: ['user', 'manager'],
    description: 'Elevated permissions for management operations',
  },
  serviceAccount: {
    username: 'service-account',
    password: 'service123',
    email: 'service@example.com',
    roles: ['service'],
    description: 'Service account for API-to-API integration tests',
  },
};

function getUserByRole(role) {
  return Object.values(TEST_USERS).find(user => user.roles.includes(role));
}

function getUsersByRole(role) {
  return Object.values(TEST_USERS).filter(user => user.roles.includes(role));
}

function getAllUsers() {
  return Object.values(TEST_USERS);
}

module.exports = {
  TEST_USERS,
  getUserByRole,
  getUsersByRole,
  getAllUsers,
};
```

**Exit Criteria:**
- [ ] `auth-helper.js` exports all required functions
- [ ] `test-users.js` contains all 6 test users
- [ ] Configuration uses cookiecutter template variables
- [ ] Error messages include HTTP status and response text

**Verification:**
```javascript
// Manual verification after Keycloak is running
const { getAdminToken, authHeader } = require('./auth-helper');
// Token retrieval should succeed with correct Keycloak setup
```

---

### IP-3: Phase 3 - Fixture System

**Objective:** Implement Playwright test fixtures that provide pre-authenticated request contexts.

**Entry Criteria:**
- Phase 2 complete
- auth-helper.js and test-users.js are functional

**Deliverables:**

#### 3.1: Create fixtures.js

Location: `template/{{cookiecutter.project_slug}}/playwright/tests/fixtures.js`

**Implementation Requirements (FR-4.1 through FR-4.4):**

```javascript
/**
 * Extended Playwright fixtures with authenticated request contexts
 *
 * Usage in tests:
 *   const { test } = require('./fixtures');
 *   const { expect } = require('@playwright/test');
 *
 *   test('admin access', async ({ adminRequest }) => {
 *     const response = await adminRequest.get('/admin');
 *     expect(response.ok()).toBeTruthy();
 *   });
 */

const { test as base } = require('@playwright/test');
const { getAccessToken, authHeader } = require('./auth-helper');
const { TEST_USERS } = require('./test-users');

/**
 * Create an authenticated request wrapper for a user
 */
function createAuthenticatedContext(request, token, user) {
  const makeRequest = (method) => (url, options = {}) => {
    return request[method](url, {
      ...options,
      headers: { ...authHeader(token), ...options.headers },
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

const test = base.extend({
  /**
   * Provides authenticated request contexts for all test users
   */
  authenticatedRequest: async ({ request }, use) => {
    const contexts = {};

    for (const [key, user] of Object.entries(TEST_USERS)) {
      try {
        const token = await getAccessToken(request, user.username, user.password);
        contexts[key] = createAuthenticatedContext(request, token, user);
      } catch (error) {
        throw new Error(
          `Failed to authenticate test user '${key}' (${user.username}): ${error.message}\n` +
          `Ensure Keycloak is running and realm is configured. Run: make docker-up && ./keycloak/setup-realm.sh`
        );
      }
    }

    await use(contexts);
  },

  // Convenience fixtures for common user types
  adminRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.admin);
  },

  userRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.user);
  },

  readOnlyRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.readOnly);
  },

  managerRequest: async ({ authenticatedRequest }, use) => {
    await use(authenticatedRequest.manager);
  },
});

module.exports = { test };
```

**Exit Criteria:**
- [ ] `fixtures.js` extends Playwright's base test
- [ ] All 6 user contexts available via `authenticatedRequest`
- [ ] Convenience fixtures work: `adminRequest`, `userRequest`, etc.
- [ ] Each context exposes `get`, `post`, `put`, `patch`, `delete`, `user`, `token`
- [ ] Authentication failures produce actionable error messages

**Verification:**
```javascript
// Test fixture availability
test('fixture provides admin context', async ({ adminRequest }) => {
  expect(adminRequest.user.username).toBe('admin');
  expect(adminRequest.token).toBeDefined();
});
```

---

### IP-4: Phase 4 - Example Test Suites

**Objective:** Create example test files that demonstrate both manual authentication and fixture-based patterns.

**Entry Criteria:**
- Phase 3 complete
- Fixture system is functional

**Deliverables:**

#### 4.1: Create api-endpoints.api.spec.js (Manual Auth Pattern)

Location: `template/{{cookiecutter.project_slug}}/playwright/tests/api-endpoints.api.spec.js`

**Implementation Requirements (FR-5.1):**

Test suites to include:
- **Public API Endpoints**: Root `/` and health `/{{ cookiecutter.backend_api_prefix }}/health` endpoints
- **Protected API Endpoints**: Authentication required, both success and failure cases
- **Admin-Only API Endpoints**: Role-based access with admin and non-admin users
- **Token Validation**: Invalid token formats, malformed JWTs

**Test Count Target:** 10 tests minimum

```javascript
/**
 * Basic API endpoint tests using manual authentication
 * Demonstrates the auth-helper pattern for custom authentication scenarios
 */
const { test, expect } = require('@playwright/test');
const { getAdminToken, getTestUserToken, authHeader } = require('./auth-helper');

test.describe('Public API Endpoints', () => {
  test('GET / should return service info', async ({ request }) => {
    const response = await request.get('/');
    expect(response.ok()).toBeTruthy();
    // Adjust assertion based on actual root endpoint response
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/health should return healthy status', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/health');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.status).toBe('healthy');
  });
});

test.describe('Protected API Endpoints', () => {
  test('GET /{{ cookiecutter.backend_api_prefix }}/auth/me should fail without token', async ({ request }) => {
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');
    expect(response.status()).toBe(403);
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/auth/me should succeed with admin token', async ({ request }) => {
    const token = await getAdminToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me', {
      headers: authHeader(token),
    });
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('admin');
  });

  test('GET /{{ cookiecutter.backend_api_prefix }}/auth/me should succeed with user token', async ({ request }) => {
    const token = await getTestUserToken(request);
    const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me', {
      headers: authHeader(token),
    });
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('testuser');
  });
});

// ... Additional test suites for Admin endpoints and Token validation
```

#### 4.2: Create api-with-fixtures.api.spec.js (Fixture Pattern)

Location: `template/{{cookiecutter.project_slug}}/playwright/tests/api-with-fixtures.api.spec.js`

**Implementation Requirements (FR-5.2):**

Test suites demonstrating:
- Single-user fixtures (`adminRequest`, `userRequest`)
- Multi-user fixtures (`authenticatedRequest`)
- Accessing user metadata and token
- POST requests with authenticated context
- New user and service account scenarios

**Test Count Target:** 9 tests minimum

```javascript
/**
 * API tests using the fixture pattern (recommended approach)
 * Import { test } from fixtures.js to get authenticated request contexts
 */
const { test } = require('./fixtures');
const { expect } = require('@playwright/test');

test.describe('API Tests with Fixtures', () => {
  test('admin can access admin endpoint using adminRequest fixture', async ({ adminRequest }) => {
    const response = await adminRequest.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.user.roles).toContain('admin');
  });

  test('regular user can access protected endpoint using userRequest fixture', async ({ userRequest }) => {
    const response = await userRequest.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('testuser');
  });

  test('regular user cannot access admin endpoint', async ({ userRequest }) => {
    const response = await userRequest.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');
    expect(response.status()).toBe(403);
  });

  test('can access multiple user contexts in same test', async ({ authenticatedRequest }) => {
    const adminResp = await authenticatedRequest.admin.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');
    const userResp = await authenticatedRequest.user.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

    expect(adminResp.ok()).toBeTruthy();
    expect(userResp.ok()).toBeTruthy();
  });

  test('can access user info and token from fixture', async ({ adminRequest }) => {
    expect(adminRequest.user.username).toBe('admin');
    expect(adminRequest.user.roles).toContain('admin');
    expect(adminRequest.token).toBeDefined();
    expect(typeof adminRequest.token).toBe('string');
  });
});

test.describe('Test User Scenarios', () => {
  test('newUser fixture for testing onboarding flows', async ({ authenticatedRequest }) => {
    const response = await authenticatedRequest.newUser.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('newuser');
  });

  test('serviceAccount fixture for API integration tests', async ({ authenticatedRequest }) => {
    const response = await authenticatedRequest.serviceAccount.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');
    expect(response.ok()).toBeTruthy();
    const data = await response.json();
    expect(data.username).toBe('service-account');
  });
});
```

**Exit Criteria:**
- [ ] `api-endpoints.api.spec.js` contains 10+ tests with manual auth
- [ ] `api-with-fixtures.api.spec.js` contains 9+ tests with fixtures
- [ ] All tests use cookiecutter variables for endpoint paths
- [ ] Tests cover public, protected, and admin endpoints
- [ ] Tests demonstrate positive and negative cases

**Verification:**
```bash
# Run tests (with services running)
cd playwright && npm test
# Expected: 17+ tests pass
```

---

### IP-5: Phase 5 - Keycloak Integration

**Objective:** Update the Keycloak realm setup script to create all test users and roles required for Playwright tests.

**Entry Criteria:**
- Understanding of current setup-realm.sh script
- Phase 2 complete (test-users.js defines required users)

**Deliverables:**

#### 5.1: Update setup-realm.sh

Location: `template/{{cookiecutter.project_slug}}/keycloak/setup-realm.sh`

**Implementation Requirements (FR-6.1, FR-6.2):**

**New Roles to Create:**

| Role | Description |
|------|-------------|
| `user` | Standard user access (base role) |
| `admin` | Administrative access |
| `readonly` | Read-only access |
| `manager` | Manager-level permissions |
| `service` | Service account role for API integration |

**New Users to Create:**

| Username | Password | Email | Roles |
|----------|----------|-------|-------|
| `admin` | `admin123` | `admin@example.com` | user, admin |
| `testuser` | `test123` | `test@example.com` | user |
| `readonly` | `readonly123` | `readonly@example.com` | user, readonly |
| `newuser` | `newuser123` | `newuser@example.com` | user |
| `manager` | `manager123` | `manager@example.com` | user, manager |
| `service-account` | `service123` | `service@example.com` | service |

**Script Updates:**

```bash
# Add after existing role creation

# Create Playwright test roles
echo "Creating Playwright test roles..."
for ROLE in user admin readonly manager service; do
  echo "  Creating role: $ROLE"
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$ROLE\"}" \
    "$KEYCLOAK_URL/admin/realms/${REALM}/roles" 2>/dev/null || true
done

# Create Playwright test users
echo "Creating Playwright test users..."

create_test_user() {
  local USERNAME=$1
  local PASSWORD=$2
  local EMAIL=$3
  local FIRSTNAME=$4
  local LASTNAME=$5
  shift 5
  local ROLES=("$@")

  echo "  Creating user: $USERNAME"

  # Create user
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"$USERNAME\",
      \"email\": \"$EMAIL\",
      \"firstName\": \"$FIRSTNAME\",
      \"lastName\": \"$LASTNAME\",
      \"enabled\": true,
      \"emailVerified\": true,
      \"credentials\": [{
        \"type\": \"password\",
        \"value\": \"$PASSWORD\",
        \"temporary\": false
      }],
      \"attributes\": {
        \"tenant_id\": [\"tenant-1\"]
      }
    }" \
    "$KEYCLOAK_URL/admin/realms/${REALM}/users" 2>/dev/null || true

  # Get user ID
  USER_ID=$(curl -s -X GET \
    -H "Authorization: Bearer $TOKEN" \
    "$KEYCLOAK_URL/admin/realms/${REALM}/users?username=$USERNAME" | \
    grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

  # Assign roles
  for ROLE in "${ROLES[@]}"; do
    ROLE_ID=$(curl -s -X GET \
      -H "Authorization: Bearer $TOKEN" \
      "$KEYCLOAK_URL/admin/realms/${REALM}/roles/$ROLE" | \
      grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

    curl -s -X POST \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "[{\"id\": \"$ROLE_ID\", \"name\": \"$ROLE\"}]" \
      "$KEYCLOAK_URL/admin/realms/${REALM}/users/$USER_ID/role-mappings/realm" 2>/dev/null || true
  done
}

# Create test users
create_test_user "admin" "admin123" "admin@example.com" "Admin" "User" "user" "admin"
create_test_user "testuser" "test123" "test@example.com" "Test" "User" "user"
create_test_user "readonly" "readonly123" "readonly@example.com" "Readonly" "User" "user" "readonly"
create_test_user "newuser" "newuser123" "newuser@example.com" "New" "User" "user"
create_test_user "manager" "manager123" "manager@example.com" "Manager" "User" "user" "manager"
create_test_user "service-account" "service123" "service@example.com" "Service" "Account" "service"

echo "Playwright test users created successfully!"
```

**Exit Criteria:**
- [ ] Script creates 5 new realm roles
- [ ] Script creates 6 test users with correct credentials
- [ ] Role assignments match test-users.js definitions
- [ ] Script is idempotent (can run multiple times)
- [ ] Existing tenant-based users are preserved

**Verification:**
```bash
# Run setup script
./keycloak/setup-realm.sh

# Verify users via Keycloak Admin API or UI
curl -X GET "http://localhost:8080/admin/realms/REALM/users" -H "Authorization: Bearer TOKEN"
```

---

### IP-6: Phase 6 - Build System Integration

**Objective:** Add Makefile targets and npm scripts for easy test execution.

**Entry Criteria:**
- Phase 1 complete (package.json exists)
- Understanding of template's Makefile (if exists)

**Deliverables:**

#### 6.1: Makefile Targets

Location: `template/{{cookiecutter.project_slug}}/Makefile`

**Implementation Requirements (FR-8.1, FR-8.2):**

```makefile
# Add to .PHONY declaration
.PHONY: test test-api test-ui test-debug test-report test-install

# Directory paths
PLAYWRIGHT_DIR := playwright

# Testing Commands
test: ## Run all Playwright tests
	cd $(PLAYWRIGHT_DIR) && npm test

test-api: ## Run API tests only
	cd $(PLAYWRIGHT_DIR) && npm run test:api

test-ui: ## Run tests in interactive UI mode
	cd $(PLAYWRIGHT_DIR) && npm run test:ui

test-debug: ## Run tests in debug mode
	cd $(PLAYWRIGHT_DIR) && npm run test:debug

test-report: ## Show Playwright test report
	cd $(PLAYWRIGHT_DIR) && npm run report

test-install: ## Install Playwright dependencies
	cd $(PLAYWRIGHT_DIR) && npm install
```

#### 6.2: Help Target Integration

If template has a `help` target (like implementation-manager), add Testing Commands section:

```makefile
help: ## Show this help message
	@echo 'Testing Commands:'
	@grep -E '^test.*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
```

#### 6.3: Package.json npm Scripts (Verification)

Ensure package.json contains all required scripts (from Phase 1):

| Script | Command | Purpose |
|--------|---------|---------|
| `test` | `playwright test` | Run all tests |
| `test:api` | `playwright test --project='API Tests'` | Run API tests only |
| `test:ui` | `playwright test --ui` | Interactive UI mode |
| `test:debug` | `playwright test --debug` | Debug mode |
| `report` | `playwright show-report` | Open HTML report |

**Exit Criteria:**
- [ ] All 6 Makefile targets work from project root
- [ ] Targets include help comments (`##`)
- [ ] `make help` displays test targets
- [ ] npm scripts match Makefile target commands

**Verification:**
```bash
# From project root
make test-install
make test-api
make test-ui  # Opens UI
make test-report  # Opens HTML report
```

---

### IP-7: Phase 7 - Documentation

**Objective:** Create comprehensive documentation for the Playwright API testing infrastructure.

**Entry Criteria:**
- Phases 1-6 complete
- All code patterns established

**Deliverables:**

#### 7.1: Create README.md

Location: `template/{{cookiecutter.project_slug}}/playwright/README.md`

**Implementation Requirements (FR-7.1):**

**Required Sections:**

1. **Header**: Title, brief description
2. **Prerequisites**: Node.js, Docker, running services
3. **Setup**: `make test-install` or `npm install`
4. **Running Tests**: Table of all test commands
5. **Test Structure**: Directory layout diagram
6. **Writing Tests**:
   - Recommended pattern (fixtures) with code example
   - Advanced pattern (manual auth) with code example
7. **Available Fixtures**: Table with fixture name, user, roles, description
8. **Test Users**: Table with username, password, email, roles
9. **Environment Variables**: Configuration options
10. **Troubleshooting**: Common issues and solutions
11. **CI/CD**: Notes on running in CI environments

**Content Length:** 150-200 lines

**Reference:** `/home/ty/workspace/project-starter/implementation-manager/playwright/README.md`

#### 7.2: Create QUICK_START.md

Location: `template/{{cookiecutter.project_slug}}/playwright/QUICK_START.md`

**Implementation Requirements (FR-7.2):**

**Format:** Step-by-step guide with numbered sections

```markdown
# Quick Start Guide - Playwright API Testing

## 1. Install Dependencies
\`\`\`bash
make test-install
\`\`\`

## 2. Start Services
\`\`\`bash
make docker-up
\`\`\`

## 3. Run Tests
\`\`\`bash
make test-api
\`\`\`

## 4. View Report
\`\`\`bash
make test-report
\`\`\`

## 5. Write Your First Test
[Example code]

## Available Test Users
[Quick reference table]

## Debugging Tips
[UI mode, debug mode instructions]
```

**Content Length:** 50-80 lines

**Reference:** `/home/ty/workspace/project-starter/implementation-manager/playwright/QUICK_START.md`

**Exit Criteria:**
- [ ] README.md contains all 11 required sections
- [ ] QUICK_START.md can be followed in under 5 minutes
- [ ] All code examples use correct cookiecutter variables
- [ ] Test user credentials are documented
- [ ] Troubleshooting covers common setup issues

**Verification:**
- [ ] New developer can follow QUICK_START.md successfully
- [ ] README.md provides sufficient detail for advanced usage
- [ ] No placeholder or TODO content remains

---

### IP-8: Phase 8 - Validation and Testing

**Objective:** Validate the complete implementation through end-to-end testing and ensure CI readiness.

**Entry Criteria:**
- Phases 1-7 complete
- All code and documentation in place

**Deliverables:**

#### 8.1: Template Generation Validation

Test that the cookiecutter template generates a valid project:

```bash
# Generate fresh project
cookiecutter template/ --no-input project_name="Test Project"
cd test-project/

# Verify directory structure
ls -la playwright/
ls -la playwright/tests/

# Check cookiecutter variable substitution
grep -r "{{ cookiecutter" playwright/  # Should return nothing
```

**Validation Checklist:**
- [ ] `playwright/` directory created
- [ ] All 7 files present (package.json, config, auth-helper, test-users, fixtures, 2 spec files)
- [ ] README.md and QUICK_START.md present
- [ ] No unresolved cookiecutter variables
- [ ] Package.json has correct project name

#### 8.2: Dependency Installation Validation

```bash
cd test-project/playwright
npm install
npx playwright --version
```

**Validation Checklist:**
- [ ] `npm install` succeeds without errors
- [ ] `@playwright/test` installed
- [ ] No peer dependency warnings

#### 8.3: Test Execution Validation

```bash
# Start services
make docker-up

# Wait for Keycloak to be ready
./keycloak/wait-for-keycloak.sh

# Setup realm with test users
./keycloak/setup-realm.sh

# Run tests
make test-api
```

**Validation Checklist:**
- [ ] All tests pass (17+ tests)
- [ ] Test execution time under 60 seconds
- [ ] HTML report generated
- [ ] No flaky tests

#### 8.4: CI Environment Validation

```bash
# Simulate CI environment
export CI=true
cd playwright && npm test
```

**Validation Checklist:**
- [ ] Tests run with single worker
- [ ] Retries configured (2)
- [ ] No webServer auto-start
- [ ] Exit code 0 on success

#### 8.5: Documentation Validation

- [ ] Follow QUICK_START.md with fresh environment
- [ ] Verify README.md fixture examples work
- [ ] Check test user credentials against Keycloak
- [ ] Validate troubleshooting steps

**Exit Criteria:**
- [ ] Template generates valid project
- [ ] All tests pass in local environment
- [ ] All tests pass in CI-simulated environment
- [ ] Documentation is accurate and complete
- [ ] No regressions in existing template functionality

---

### Implementation Sequence Diagram

```
Week 1: Foundation and Core Infrastructure
├── Day 1-2: Phase 1 (Foundation) + Phase 2 (Auth Infrastructure)
│   └── Deliverables: Directory structure, auth-helper.js, test-users.js
│
├── Day 2-3: Phase 3 (Fixtures) + Phase 4 (Example Tests)
│   └── Deliverables: fixtures.js, api-endpoints.api.spec.js, api-with-fixtures.api.spec.js
│
└── Day 3: Phase 5 (Keycloak Integration)
    └── Deliverables: Updated setup-realm.sh

Week 2: Integration and Documentation
├── Day 1: Phase 6 (Build System)
│   └── Deliverables: Makefile targets, npm scripts verified
│
├── Day 1-2: Phase 7 (Documentation)
│   └── Deliverables: README.md, QUICK_START.md
│
└── Day 2-3: Phase 8 (Validation)
    └── Deliverables: Validated implementation, CI ready
```

---

### Rollout Strategy

#### Approach: Feature Branch with Template Testing

1. **Development Branch**: Create `feature/playwright-api-testing` branch
2. **Incremental Commits**: One commit per phase for easy review
3. **Template Testing**: Generate test project after each phase
4. **Integration Testing**: Full validation in Phase 8
5. **Code Review**: PR review with focus on:
   - Cookiecutter variable usage
   - Code quality and documentation
   - Test coverage and reliability
6. **Merge**: Squash merge to main after approval

#### Rollback Plan

If issues are discovered post-merge:
1. Playwright directory can be removed without affecting other template functionality
2. Keycloak setup script changes are additive (new users/roles only)
3. Makefile targets can be commented out

---

### Complexity and Effort Summary

| Phase | Complexity | Effort (hours) | Risk Level |
|-------|------------|----------------|------------|
| 1. Foundation | Low | 2-3 | Low |
| 2. Authentication | Medium | 3-4 | Medium |
| 3. Fixtures | Medium | 2-3 | Low |
| 4. Example Tests | Medium | 2-3 | Low |
| 5. Keycloak | Medium | 2-3 | Medium |
| 6. Build System | Low | 1-2 | Low |
| 7. Documentation | Low | 2-3 | Low |
| 8. Validation | Medium | 2-3 | Low |

**Total Effort:** 16-24 hours

**Primary Risks:**
- Keycloak realm setup script complexity (Phase 5)
- Authentication token retrieval in different environments (Phase 2)
- Template variable escaping in JavaScript files (All phases)

**Mitigation:**
- Reference implementation-manager patterns throughout
- Test each phase immediately after completion
- Use CI-like environment for final validation

---

## Dependencies & Risks

This section identifies the external dependencies, internal dependencies, technical risks, and mitigation strategies for implementing Playwright API testing support in the cookiecutter template.

---

### DR-1: External Dependencies

#### DR-1.1: Playwright Test Framework

| Attribute | Value |
|-----------|-------|
| Package | `@playwright/test` |
| Version | `^1.56.1` (as used in implementation-manager) |
| Type | npm devDependency |
| Criticality | **High** - Core testing framework |
| License | Apache 2.0 |

**Dependency Risks:**
- **Version Compatibility**: Playwright releases frequently (monthly). Breaking changes in major versions could affect test fixtures and configuration.
- **Node.js Compatibility**: Playwright requires Node.js 18+ as of 2024. The template currently uses Node.js 20, which is compatible.
- **Browser Dependencies**: While API tests do not use browser binaries, the Playwright package still includes browser download logic that may affect CI environments.

**Mitigation:**
- Pin to a specific minor version range (`^1.56.1`) to avoid automatic major upgrades
- Document Node.js version requirements in README
- Use `--ignore-scripts` flag in CI if browser download causes issues (not needed for API tests)

**Reference:** [Playwright Best Practices](https://playwright.dev/docs/best-practices)

#### DR-1.2: Keycloak Authentication Server

| Attribute | Value |
|-----------|-------|
| Component | Keycloak Identity Provider |
| Version | `23.0` (template default) |
| Protocol | OAuth 2.0 / OpenID Connect |
| Criticality | **High** - Required for authenticated API tests |

**Dependency Risks:**
- **Service Availability**: Tests fail if Keycloak is not running or not accessible
- **Realm Configuration**: Test users and roles must be pre-configured in Keycloak realm
- **Token Endpoint Stability**: Token URLs follow standard OIDC patterns but could change in Keycloak updates
- **Password Grant Deprecation**: The OAuth 2.0 password grant used for test authentication is deprecated in OAuth 2.1 and may be removed in future Keycloak versions

**Mitigation:**
- Playwright's `webServer` configuration starts Docker Compose automatically in local development
- Health check URLs verify Keycloak readiness before tests run
- Document Keycloak version compatibility requirements
- Plan migration path to client credentials grant for service-to-service testing (see DR-5.1)

**Reference:** [OAuth 2.1 Changes](https://skycloak.io/blog/upcoming-changes-in-oauth-2-1-what-you-need-to-know/)

#### DR-1.3: FastAPI Backend Service

| Attribute | Value |
|-----------|-------|
| Component | FastAPI Application |
| Version | Python 3.13 with FastAPI |
| Endpoints | `/`, `/health`, `/protected`, `/admin`, and application-specific routes |
| Criticality | **High** - Primary test target |

**Dependency Risks:**
- **Service Availability**: Backend must be running for API tests to execute
- **Endpoint Stability**: API contract changes could break existing tests
- **Authentication Middleware**: Backend must correctly validate JWT tokens from Keycloak

**Mitigation:**
- `webServer` configuration ensures backend is started before tests
- Health endpoint polling confirms backend readiness
- Test examples demonstrate both positive and negative authorization scenarios
- Example tests cover core endpoints that are unlikely to change

#### DR-1.4: Docker and Docker Compose

| Attribute | Value |
|-----------|-------|
| Component | Docker Compose |
| Version | Docker Compose V2 |
| Services | keycloak, backend, postgres (minimum for API tests) |
| Criticality | **Medium** - Required for local development testing |

**Dependency Risks:**
- **Resource Requirements**: Running Keycloak, PostgreSQL, and backend requires significant memory (~2-4GB)
- **Startup Time**: Full Docker Compose stack takes 30-60 seconds to become healthy
- **Platform Compatibility**: Docker Desktop licensing and ARM64 compatibility considerations

**Mitigation:**
- Configure appropriate `webServer.timeout` (120 seconds) for service startup
- Use `reuseExistingServer: true` to avoid repeated restarts
- Document minimum system requirements in README
- CI environments manage services separately (no webServer configuration)

---

### DR-2: Internal Dependencies

#### DR-2.1: Cookiecutter Template System

| Attribute | Value |
|-----------|-------|
| Component | Cookiecutter templating |
| Variables Used | `project_slug`, `project_name`, `keycloak_port`, `keycloak_realm_name`, `keycloak_backend_client_id`, `backend_port` |
| Criticality | **High** - Template variable substitution |

**Dependency Risks:**
- **Variable Escaping**: JavaScript template literals (`${}`) and cookiecutter variables (`{{ }}`) can conflict
- **Missing Variables**: New variables added to cookiecutter.json may not be available in all template files
- **Template Syntax Errors**: Invalid cookiecutter syntax causes project generation failure

**Mitigation:**
- Use environment variable overrides with process.env fallbacks for runtime flexibility
- Test template generation as part of validation phase (Phase 8)
- Follow established patterns from existing template JavaScript files (frontend)
- Document all cookiecutter variables used in Playwright files

**Affected Files:**
- `playwright/tests/auth-helper.js` - Uses Keycloak URL and realm variables
- `playwright/tests/test-users.js` - Uses project name for user email domains
- `playwright/playwright.config.js` - Uses backend port for baseURL
- `playwright/package.json` - Uses project_slug for package name

#### DR-2.2: Keycloak Realm Setup Script

| Attribute | Value |
|-----------|-------|
| Component | `keycloak/setup-realm.sh` |
| Current State | Creates realm, clients, and basic test users |
| Required Changes | Add 5 new roles and 6 new test users with role assignments |
| Criticality | **High** - Test users must exist for API tests |

**Dependency Risks:**
- **Script Idempotency**: Script must handle re-runs gracefully (users may already exist)
- **Keycloak API Stability**: Admin REST API endpoints could change between Keycloak versions
- **Role Assignment Complexity**: Creating roles and assigning to users requires multiple API calls
- **Script Failure Modes**: Partial execution could leave realm in inconsistent state

**Mitigation:**
- Use HTTP status code checking (409 Conflict for existing resources)
- Implement graceful error handling with informative messages
- Test script against multiple Keycloak versions (23.0, 24.x)
- Document manual recovery steps in case of script failure

**Reference Implementation:**
- Current script location: `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/keycloak/setup-realm.sh`
- Pattern reference: `/home/ty/workspace/project-starter/implementation-manager/keycloak/` (realm configuration)

#### DR-2.3: Makefile Integration

| Attribute | Value |
|-----------|-------|
| Component | Project root Makefile |
| New Targets | `test`, `test-api`, `test-ui`, `test-debug`, `test-report`, `test-install` |
| Criticality | **Medium** - Developer convenience |

**Dependency Risks:**
- **Path Handling**: Makefile must correctly navigate to `playwright/` directory
- **npm Availability**: Targets assume `npm` is installed and in PATH
- **Target Conflicts**: Template Makefile must not conflict with existing targets

**Mitigation:**
- Use `cd playwright &&` prefix pattern (as in implementation-manager Makefile)
- Add `check-deps` target that validates npm installation
- Follow existing Makefile conventions from implementation-manager
- Test targets on both Linux and macOS

**Reference Implementation:** `/home/ty/workspace/project-starter/implementation-manager/Makefile` (lines 120-143)

---

### DR-3: Technical Risks

#### DR-3.1: OAuth 2.0 Password Grant Deprecation

| Risk Level | **Medium-High** |
|------------|-----------------|
| Probability | High (within 2-3 years) |
| Impact | Medium (requires migration to alternative flow) |

**Description:**
The OAuth 2.0 Resource Owner Password Credentials Grant (password grant) used for obtaining test tokens is deprecated in OAuth 2.0 Security Best Current Practice and removed from OAuth 2.1. While Keycloak continues to support this flow in version 23.0, future versions may disable it by default or remove it entirely.

**Current Implementation:**
```javascript
// auth-helper.js - Uses password grant
const response = await request.post(tokenUrl, {
  form: {
    username,
    password,
    grant_type: 'password',  // Deprecated in OAuth 2.1
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
  },
});
```

**Migration Path:**
1. **Client Credentials Grant** (for service accounts): Use service account credentials for API-to-API testing
2. **Pre-generated Long-lived Tokens**: Generate test tokens during CI setup with extended expiration
3. **Token Exchange**: Use Keycloak token exchange to obtain test tokens from a service account

**Mitigation:**
- Document deprecation warning in README and auth-helper.js comments
- Ensure Keycloak client has `directAccessGrantsEnabled: true` explicitly configured
- Plan Phase 2 enhancement to add client credentials grant support for service account tests
- Monitor Keycloak release notes for password grant deprecation timeline

**Reference:** [Keycloak OAuth 2.1 Compatibility](https://www.keycloak.org/docs/latest/release_notes/index.html)

#### DR-3.2: Test User Credential Exposure

| Risk Level | **Medium** |
|------------|------------|
| Probability | Low (with proper practices) |
| Impact | High (credential compromise) |

**Description:**
Test user credentials are stored in plain text in `test-users.js` and referenced in documentation. While these are development-only credentials, they could be misused if:
- Developers reuse credentials in production
- Test users are created in production Keycloak realms
- Credentials are accidentally committed to version control

**Mitigation:**
- Use clearly non-production passwords (e.g., `admin123`, `test123`)
- Use RFC 2606 reserved domain `example.com` for test user emails
- Add prominent warnings in documentation
- Ensure `.gitignore` excludes any environment files with production credentials
- Separate test realm from production realm in Keycloak

**Reference:** Implementation-manager follows these practices in `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/test-users.js`

#### DR-3.3: Token Expiration During Test Execution

| Risk Level | **Low** |
|------------|---------|
| Probability | Low (with default token lifespans) |
| Impact | Medium (test failures) |

**Description:**
Access tokens have limited lifespan (default 5-15 minutes in Keycloak). Long-running test suites or slow test execution could result in token expiration mid-test, causing authentication failures.

**Mitigation:**
- Configure Keycloak access token lifespan appropriately for tests (900 seconds in backend client)
- Fixture architecture obtains fresh tokens at test start
- Individual tests should complete within token lifetime
- Document token refresh patterns for long-running scenarios

**Current Configuration (setup-realm.sh):**
```json
"attributes": {
  "access.token.lifespan": "900"  // 15 minutes
}
```

#### DR-3.4: Network Isolation in CI Environments

| Risk Level | **Medium** |
|------------|------------|
| Probability | Medium (depends on CI configuration) |
| Impact | High (test suite failures) |

**Description:**
CI environments may have different network configurations than local development:
- Service discovery differs (localhost vs container names)
- Port mappings may vary
- Firewall rules may block inter-service communication
- Docker-in-Docker configurations add complexity

**Mitigation:**
- Use environment variable overrides (`KEYCLOAK_URL`, `BASE_URL`) for CI configuration
- Document CI-specific setup requirements
- Provide example GitHub Actions workflow configuration
- Test suite works in CI mode (no webServer auto-start)

**Playwright Configuration Pattern:**
```javascript
// playwright.config.js
webServer: process.env.CI ? undefined : {
  command: 'cd .. && make docker-up',
  url: 'http://localhost:8000/health',
  timeout: 120 * 1000,
  reuseExistingServer: !process.env.CI,
},
```

#### DR-3.5: Cookiecutter Template Variable Escaping

| Risk Level | **Medium** |
|------------|------------|
| Probability | Medium (JavaScript files are complex) |
| Impact | Medium (project generation failure) |

**Description:**
JavaScript files containing cookiecutter template variables require careful escaping to avoid:
- Syntax errors in generated files
- Incorrect variable substitution
- Conflicts between JavaScript template literals and cookiecutter syntax

**Examples of Potential Issues:**
```javascript
// PROBLEMATIC: JavaScript template literal conflicts with cookiecutter
const url = `http://localhost:{{ cookiecutter.keycloak_port }}`;

// SAFE: String concatenation
const url = 'http://localhost:' + '{{ cookiecutter.keycloak_port }}';

// SAFE: Environment variable with cookiecutter default
const url = process.env.KEYCLOAK_URL || 'http://localhost:{{ cookiecutter.keycloak_port }}';
```

**Mitigation:**
- Use string concatenation or environment variable patterns instead of template literals with cookiecutter variables
- Test template generation with various project names (including edge cases)
- Add template validation to CI pipeline
- Follow patterns established in existing template JavaScript files

---

### DR-4: Operational Risks

#### DR-4.1: Documentation Maintenance Burden

| Risk Level | **Low** |
|------------|---------|
| Probability | Medium (documentation drift) |
| Impact | Low (developer confusion) |

**Description:**
Multiple documentation files (README.md, QUICK_START.md, inline comments) need to stay synchronized with code changes. Documentation can become outdated as the codebase evolves.

**Mitigation:**
- Keep documentation minimal and focused
- Use code comments for implementation details
- Include documentation review in PR checklist
- Generate example outputs from actual test runs

#### DR-4.2: Cross-Platform Compatibility

| Risk Level | **Low** |
|------------|---------|
| Probability | Low (Node.js is cross-platform) |
| Impact | Medium (developer friction) |

**Description:**
Playwright and npm are cross-platform, but edge cases exist:
- Path separators differ (Windows vs Unix)
- Shell commands in package.json scripts may not work on all platforms
- Docker Desktop behavior differs across platforms

**Mitigation:**
- Use platform-agnostic npm scripts
- Avoid shell-specific syntax in package.json
- Test on Linux, macOS, and Windows (CI matrix)
- Document Windows-specific requirements if any

#### DR-4.3: Keycloak Version Compatibility

| Risk Level | **Medium** |
|------------|------------|
| Probability | Medium (Keycloak evolves rapidly) |
| Impact | Medium (setup script failures) |

**Description:**
Keycloak has frequent releases with occasional breaking changes to:
- Admin REST API endpoints
- Default security configurations
- Realm import/export format
- Token endpoint behavior

**Mitigation:**
- Document tested Keycloak versions (23.0, 24.x, 25.x)
- Use standard OIDC endpoints that are less likely to change
- Monitor Keycloak release notes for breaking changes
- Test setup script against new Keycloak versions before adoption

---

### DR-5: Risk Mitigation Summary

| Risk ID | Risk | Probability | Impact | Mitigation Strategy | Owner |
|---------|------|-------------|--------|---------------------|-------|
| DR-3.1 | Password Grant Deprecation | High | Medium | Document deprecation, plan migration to client credentials | Implementation Phase |
| DR-3.2 | Test Credential Exposure | Low | High | Use dev-only credentials, RFC 2606 domains, documentation warnings | Implementation Phase |
| DR-3.3 | Token Expiration | Low | Medium | Configure appropriate token lifespan, fresh tokens per test | Configuration |
| DR-3.4 | CI Network Isolation | Medium | High | Environment variable overrides, CI-specific documentation | Documentation Phase |
| DR-3.5 | Template Variable Escaping | Medium | Medium | Avoid template literals with cookiecutter, test generation | Validation Phase |
| DR-2.2 | Realm Script Idempotency | Medium | Medium | HTTP status checking, graceful error handling | Implementation Phase |
| DR-1.2 | Keycloak Availability | Low | High | webServer auto-start, health checks, timeout configuration | Configuration |

---

### DR-6: Dependency Version Matrix

| Dependency | Minimum Version | Recommended Version | Maximum Tested |
|------------|-----------------|---------------------|----------------|
| Node.js | 18.0.0 | 20.x LTS | 22.x |
| npm | 9.0.0 | 10.x | Latest |
| @playwright/test | 1.40.0 | 1.56.1 | 1.56.x |
| Keycloak | 22.0 | 23.0 | 25.x |
| Docker | 24.0 | 25.x | Latest |
| Docker Compose | 2.20.0 | 2.24.x | Latest |

---

### DR-7: Contingency Plans

#### If Password Grant Is Disabled in Keycloak

1. **Immediate**: Re-enable password grant via Keycloak admin console or realm configuration
2. **Short-term**: Create long-lived test tokens manually or via admin API
3. **Long-term**: Implement client credentials grant for service account testing

#### If Playwright Major Version Breaks Compatibility

1. **Immediate**: Pin to last working version
2. **Short-term**: Review migration guide and update fixtures
3. **Long-term**: Adopt new API patterns and update documentation

#### If Docker Resource Constraints Prevent Testing

1. **Immediate**: Increase Docker Desktop memory allocation
2. **Short-term**: Use remote Keycloak instance for testing
3. **Long-term**: Consider lightweight Keycloak alternatives for testing

---

## Open Questions

This section documents unresolved decisions, areas requiring further research, and items needing stakeholder input before or during implementation.

---

### OQ-1: Authentication Flow Evolution

#### OQ-1.1: OAuth 2.0 Password Grant Migration Timeline

**Question:** When should we plan to migrate from the OAuth 2.0 password grant to an alternative authentication flow for test users?

**Context:** As documented in DR-3.1, the password grant (ROPC) is deprecated in OAuth 2.0 Security Best Current Practice and removed from OAuth 2.1. Keycloak currently supports this flow but may disable it by default in future versions. As of Keycloak 24+, OAuth 2.1 client policies can be enabled which explicitly disallow the password grant.

---

##### Alternative Authentication Strategies Analyzed

**Option A: Client Credentials + Token Exchange (Most OAuth 2.1 Compliant)**

```
┌──────────────────┐    1. client_credentials    ┌───────────┐
│  Test Framework  │ ─────────────────────────▶ │  Keycloak │
│  (Service Acct)  │ ◀───────────────────────── │           │
└──────────────────┘    2. service token         └───────────┘
         │
         │ 3. token-exchange (impersonate user)
         ▼
┌──────────────────┐
│   User Token     │ ─────▶ API calls as that user
└──────────────────┘
```

| Aspect | Assessment |
|--------|------------|
| OAuth 2.1 Compliance | ✅ Fully compliant |
| Complexity | High - requires Keycloak preview features |
| User Impersonation | ✅ Full support for any test user |
| Keycloak Requirements | v24+ with `token_exchange` and `admin_fine_grained_authz` features enabled |
| Credential Security | ✅ No user passwords in test code |

**Implementation Pattern:**
```javascript
async function getTokenForUser(userId) {
  // 1. Get service account token via client_credentials
  const serviceToken = await getClientCredentialsToken();

  // 2. Exchange for user token via token-exchange grant
  const response = await fetch(`${KEYCLOAK_URL}/token`, {
    method: 'POST',
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:token-exchange',
      client_id: 'test-service',
      client_secret: process.env.TEST_CLIENT_SECRET,
      subject_token: serviceToken,
      requested_subject: userId,
      requested_token_type: 'urn:ietf:params:oauth:token-type:access_token'
    })
  });
  return response.json();
}
```

**Keycloak Configuration Required:**
- Enable preview features: `-Dkeycloak.profile.feature.token_exchange=enabled -Dkeycloak.profile.feature.admin_fine_grained_authz=enabled`
- Create service client with `Service Accounts Enabled`
- Assign `impersonation` role from `realm-management` to service account
- Configure fine-grained permissions on target client

---

**Option B: Pure Client Credentials (Simplest OAuth 2.1 Compliant)**

Use multiple service accounts with different roles instead of impersonating users:

```
┌─────────────────────┐
│  test-admin-client  │ ──▶ Has admin role
├─────────────────────┤
│  test-user-client   │ ──▶ Has user role
├─────────────────────┤
│  test-readonly-client│ ──▶ Has readonly role
└─────────────────────┘
```

| Aspect | Assessment |
|--------|------------|
| OAuth 2.1 Compliance | ✅ Fully compliant |
| Complexity | Low - standard Keycloak configuration |
| User Impersonation | ❌ Tests service accounts, not actual users |
| Keycloak Requirements | Any version |
| Credential Security | ✅ Only client secrets needed |

**Limitations:** Cannot test user-specific claims (e.g., `preferred_username`, `tenant_id`), user-centric endpoints (e.g., "my profile"), or user-to-user scenarios.

**Best For:** Service-to-service API testing, RBAC role testing where user identity is not relevant.

---

**Option C: Pre-Generated Long-Lived Tokens**

Generate tokens via Keycloak Admin API during test setup or CI pipeline:

```javascript
// In test setup or CI pipeline
async function generateTestTokens() {
  const adminToken = await getAdminToken();

  for (const user of TEST_USERS) {
    const token = await keycloakAdmin.users.impersonation(user.id, {
      clientId: 'test-client'
    });
    await fs.writeFile(`.auth/${user.username}.json`, JSON.stringify(token));
  }
}
```

| Aspect | Assessment |
|--------|------------|
| OAuth 2.1 Compliance | ✅ Compliant (admin API is separate from OAuth grants) |
| Complexity | Medium - requires admin API access |
| User Impersonation | ✅ Full user tokens available |
| Keycloak Requirements | Any version with Admin API access |
| Credential Security | ⚠️ Requires admin credentials for token generation |

**Trade-offs:** Must manage token expiration and refresh; tokens typically generated once per CI run.

---

**Option D: Keep Password Grant (Pragmatic)**

Continue using password grant with explicit acknowledgment and mitigation:

| Aspect | Assessment |
|--------|------------|
| OAuth 2.1 Compliance | ❌ Deprecated, not compliant |
| Complexity | Low - already implemented |
| User Impersonation | ✅ Full user context |
| Keycloak Requirements | Any version (for now) |
| Credential Security | ⚠️ User passwords in environment variables |

**Mitigation Strategy:**
- Create dedicated Keycloak client with password grant enabled only in development realm
- Keycloak allows exempting specific clients from OAuth 2.1 policies
- Document clear migration path for when Keycloak deprecates the flow

---

##### Decision Matrix

| Approach | Complexity | OAuth 2.1 | Keycloak Version | User Context | Best For |
|----------|------------|-----------|------------------|--------------|----------|
| **Token Exchange** | High | ✅ | 24+ (preview) | ✅ Full | User impersonation |
| **Client Credentials** | Low | ✅ | Any | ❌ Service only | Role testing |
| **Pre-Generated Tokens** | Medium | ✅ | Any | ✅ Full | CI/CD pipelines |
| **Password Grant** | Low | ❌ | Any (for now) | ✅ Full | Quick start |

---

##### Recommended Decision: Phased Migration

**Phase 1 (This Implementation):** Implement with password grant
- Pragmatic approach that works with current Keycloak versions
- Design `auth-helper.js` as an abstraction layer for future migration
- Document deprecation status clearly in README

**Phase 2 (Future - When Keycloak 25+ becomes standard):** Migrate to Token Exchange
- Token Exchange expected to be production-ready (non-preview) in Keycloak 25+
- Migration involves only updating `auth-helper.js` internals
- No test file changes required due to abstraction layer

**Future-Proof Implementation Pattern:**
```javascript
// auth-helper.js with migration-ready abstraction
const AUTH_STRATEGY = process.env.AUTH_STRATEGY || 'password';

async function getTokenForUser(user) {
  switch (AUTH_STRATEGY) {
    case 'token-exchange':
      return tokenExchangeFlow(user);
    case 'client-credentials':
      return clientCredentialsFlow(user.role);
    case 'password':
    default:
      return passwordGrantFlow(user);
  }
}

// Public API remains stable regardless of underlying strategy
module.exports = { getAccessToken, authHeader, getTokenForUser };
```

---

##### References

- [OAuth 2.1 Specification](https://oauth.net/2.1/)
- [Upcoming Changes in OAuth 2.1: What You Need to Know](https://skycloak.io/blog/upcoming-changes-in-oauth-2-1-what-you-need-to-know/)
- [Keycloak Token Exchange Documentation](https://www.keycloak.org/securing-apps/token-exchange)
- [Keycloak GitHub: Supporting OAuth 2.1 (#25141)](https://github.com/keycloak/keycloak/issues/25141)
- [Stack Overflow: Password Grant Alternatives](https://stackoverflow.com/questions/77912703/oauth2-what-to-use-now-that-password-grant-type-is-deprecated)
- [GitHub: PoC Keycloak Token Exchange](https://github.com/masalinas/poc-keycloak-token-exchange)

---

**Status:** RESOLVED

**Decision:** Option 2 (Phased Migration) - Start with password grant, design abstraction layer for future migration to Token Exchange when Keycloak 25+ is adopted. This balances practical implementation with future-proofing while maintaining OAuth 2.1 migration readiness.

---

#### OQ-1.2: Token Caching Strategy

**Question:** Should authenticated request fixtures cache tokens within a test file to reduce Keycloak token endpoint calls?

**Context:** Current implementation obtains a fresh token per test, which is safe but creates additional load on Keycloak. For large test suites, this could impact test execution time.

**Options:**
1. **No Caching**: Fresh token per test (current approach, maximum isolation)
2. **File-Level Caching**: Cache tokens per test file using Playwright's `test.beforeAll`
3. **Worker-Level Caching**: Cache tokens per Playwright worker process

**Trade-offs:**
- No Caching: Slower but guaranteed isolation
- File/Worker Caching: Faster but may mask token-related bugs

**Status:** OPEN - Recommend starting with no caching, measure performance, optimize if needed

---

### OQ-2: Test User Management

#### OQ-2.1: Test User Password Complexity

**Question:** Should test user passwords follow production password policies, or should development Keycloak realms have relaxed password requirements?

**Context:** The test users use simple passwords (`admin123`, `test123`) that would fail most production password policies. This is intentional for ease of use but could mislead developers about production requirements.

**Options:**
1. **Simple Passwords**: Keep current simple passwords for developer convenience
2. **Complex Passwords**: Use production-like passwords to match real-world requirements
3. **Environment Variable Override**: Default to simple passwords but allow override via environment variables

**Recommendation:** Option 3 - provides flexibility for different testing scenarios

**Status:** OPEN

---

#### OQ-2.2: Additional Test User Roles

**Question:** Are the 6 defined test users sufficient for all anticipated testing scenarios, or should additional role combinations be provided?

**Context:** Current users cover: admin, standard user, readonly, manager, newuser, service-account. Some applications may need additional role combinations (e.g., `auditor`, `billing-admin`, `support-agent`).

**Options:**
1. **Fixed Set**: Keep the 6 defined users as a standard baseline
2. **Extensible Pattern**: Document how to add custom test users
3. **Additional Roles**: Add more role combinations to the default set

**Recommendation:** Option 2 - provide a solid baseline plus clear documentation for extension

**Status:** RESOLVED - Current 6 users cover common scenarios; extension pattern documented in test-users.js

---

### OQ-3: Template Integration

#### OQ-3.1: TypeScript vs JavaScript for Test Files

**Question:** Should the Playwright API tests use TypeScript (like the frontend E2E tests) or JavaScript (like the implementation-manager reference)?

**Context:** The frontend E2E tests in `frontend/e2e/` use TypeScript (`*.spec.ts`), while the implementation-manager Playwright tests use JavaScript (`*.js`). Consistency vs. simplicity trade-off.

**Options:**
1. **JavaScript**: Match implementation-manager reference, simpler setup, no compilation step
2. **TypeScript**: Match frontend E2E tests, better IDE support, type safety
3. **Both**: Provide TypeScript config but use JavaScript for initial examples

**Trade-offs:**
- JavaScript: Simpler onboarding, no TypeScript compilation needed, matches reference implementation
- TypeScript: Better developer experience with IDE autocompletion, catches errors earlier

**Decision:** Option 2 (TypeScript) - Consistency with frontend E2E tests, better IDE support, and type safety outweigh the minor additional complexity. All test files will use `.api.spec.ts` extension.

**Implementation Notes:**
- Test files: `*.api.spec.ts` (e.g., `api-endpoints.api.spec.ts`)
- Fixtures: `fixtures.ts`, `auth-helper.ts`, `test-users.ts`
- Add `tsconfig.json` to `playwright/` directory
- Ensure `@playwright/test` types are available

**Status:** RESOLVED

---

#### OQ-3.2: Playwright Directory Location

**Question:** Is project root `playwright/` the optimal location, or should API tests be co-located with the backend?

**Context:** Implementation-manager places Playwright tests at project root. Alternative: `backend/tests/playwright/` to keep API tests near API code.

**Options:**
1. **Project Root**: `playwright/` at root (matches implementation-manager)
2. **Backend Co-location**: `backend/tests/playwright/` or `backend/e2e/`
3. **Dedicated Test Directory**: `tests/api/` or `tests/playwright-api/`

**Trade-offs:**
- Root: Clear separation, easy Makefile integration, matches reference
- Backend: Closer to API code, but mixes Node.js tests with Python backend
- Tests Directory: Cleaner organization, but deviates from reference pattern

**Recommendation:** Option 1 (Project Root) - proven pattern from implementation-manager

**Status:** RESOLVED - Project root location confirmed by scope definition (IS-1)

---

### OQ-4: CI/CD Integration

#### OQ-4.1: GitHub Actions Workflow Template

**Question:** Should the template include a GitHub Actions workflow file for running Playwright API tests?

**Context:** CI/CD configuration was listed as a non-goal (scope section), but the testing strategy (TS-9) describes CI mode. A basic workflow template could accelerate adoption.

**Options:**
1. **No CI Template**: Leave CI configuration to individual projects
2. **Example Workflow**: Include a `.github/workflows/playwright-api.yml.example` file
3. **Active Workflow**: Include an active workflow that runs on PR/push

**Trade-offs:**
- No Template: Maximum flexibility, no CI lock-in
- Example: Provides guidance without being prescriptive
- Active: Works out of box but may not fit all CI environments

**Recommendation:** Option 2 - provide example that teams can customize

**Stakeholder Input Needed:** Should CI configuration be added to scope?

**Status:** OPEN

---

#### OQ-4.2: Parallel Test Execution in CI

**Question:** What should be the default `workers` configuration for CI environments?

**Context:** Playwright defaults to parallel execution, but CI runners have varying resource constraints. The implementation-manager uses `workers: 1` for reliability.

**Options:**
1. **Single Worker**: `workers: 1` in CI (reliable, predictable)
2. **Auto Detection**: Let Playwright auto-detect based on CPU cores
3. **Configurable**: Environment variable `PW_WORKERS` with sensible default

**Recommendation:** Option 3 - provides flexibility while maintaining CI stability

**Status:** OPEN - Defer to implementation phase

---

### OQ-5: Documentation Scope

#### OQ-5.1: Video Tutorial Content

**Question:** Should documentation include video recordings of test runs or just text/image documentation?

**Context:** Playwright's trace viewer and HTML reports include visual elements. Video walkthroughs could accelerate developer onboarding but require maintenance.

**Options:**
1. **Text Only**: Written documentation with code examples
2. **Screenshots**: Include screenshots of UI mode, reports, trace viewer
3. **Video**: Include screen recordings or animated GIFs

**Recommendation:** Option 2 - screenshots provide visual guidance without video maintenance burden

**Status:** RESOLVED - UX-5 documentation structure confirmed

---

#### OQ-5.2: Troubleshooting Guide Depth

**Question:** How comprehensive should the troubleshooting section be?

**Context:** The QUICK_START.md includes a troubleshooting section. Unknown: What common issues will developers encounter?

**Options:**
1. **Minimal**: Cover only known issues from implementation-manager
2. **Comprehensive**: Anticipate common issues based on architecture
3. **Living Document**: Start minimal, expand based on user feedback

**Recommendation:** Option 3 - practical approach that improves over time

**Status:** OPEN - Initial implementation covers common issues; expand post-launch

---

### OQ-6: Performance and Scalability

#### OQ-6.1: Large Test Suite Performance

**Question:** What is the expected performance impact when test suites grow beyond 100 tests?

**Context:** The baseline testing strategy (TS-7) defines metrics for small suites. Large projects may have hundreds of API tests.

**Research Needed:**
- Token acquisition time per test (currently ~50-100ms per Keycloak call)
- Parallel worker scaling behavior
- Memory usage with many authenticated contexts

**Recommendation:** Document performance characteristics in README; consider token caching if performance degrades

**Status:** OPEN - Requires performance testing during implementation

---

#### OQ-6.2: Keycloak Load During Test Runs

**Question:** Will rapid test execution overwhelm the development Keycloak instance?

**Context:** If 100+ tests each obtain tokens, Keycloak receives 600+ token requests (6 users x 100 tests) in a short period.

**Mitigation Options:**
1. **Accept Current Load**: Development Keycloak should handle this
2. **Connection Pooling**: Reuse HTTP connections to Keycloak
3. **Rate Limiting**: Add delays between token requests if needed
4. **Token Caching**: Cache tokens at worker level (see OQ-1.2)

**Status:** OPEN - Monitor during implementation; Keycloak typically handles this load

---

### OQ-7: Security Considerations

#### OQ-7.1: Client Secret Storage in Template

**Question:** How should the Keycloak client secret be stored in template files?

**Context:** The current approach uses a predictable pattern (`{{cookiecutter.keycloak_backend_client_id}}-secret`). This is acceptable for development but should be clearly documented as non-production.

**Options:**
1. **Predictable Pattern**: Current approach with clear documentation
2. **Generated Secret**: Generate random secret during `cookiecutter` execution
3. **Environment Variable**: Require secret to be set via environment variable

**Trade-offs:**
- Predictable: Simple setup, works out of box, security risk if used in production
- Generated: More secure, but complicates setup-realm.sh synchronization
- Environment: Most secure, but adds friction to getting started

**Recommendation:** Option 1 with prominent documentation warning

**Status:** RESOLVED - SP-1.2 documents current approach with security warnings

---

#### OQ-7.2: Test Artifacts in Version Control

**Question:** Should `.gitignore` patterns for Playwright artifacts be more aggressive?

**Context:** Test reports and traces may contain sensitive information (tokens in request headers, response bodies). Current `.gitignore` excludes standard Playwright directories.

**Files to Consider:**
- `playwright-report/` - HTML reports with request/response details
- `test-results/` - Test artifacts including traces
- `*.trace.zip` - Trace files containing full request/response data

**Recommendation:** Keep current `.gitignore` patterns; document that traces may contain tokens

**Status:** RESOLVED - Current patterns are sufficient per SP-4.2

---

### OQ-8: Future Enhancements

#### OQ-8.1: GraphQL Testing Support

**Question:** Should the template include patterns for testing GraphQL APIs if projects use GraphQL?

**Context:** The template currently supports REST APIs. Some projects may add GraphQL endpoints alongside REST.

**Options:**
1. **REST Only**: Keep focus on REST API testing
2. **GraphQL Patterns**: Add example tests for GraphQL queries/mutations
3. **Future Phase**: Document as potential Phase 2 enhancement

**Recommendation:** Option 3 - REST covers majority of use cases; GraphQL can be added later

**Status:** OPEN - Out of initial scope; may address in future iteration

---

#### OQ-8.2: Contract Testing Integration

**Question:** Should API tests validate responses against OpenAPI schemas?

**Context:** The template generates OpenAPI documentation. Tests could validate that responses match schema definitions.

**Options:**
1. **No Schema Validation**: Tests check business logic only
2. **Manual Assertions**: Include example tests with explicit schema checks
3. **Automated Validation**: Integrate OpenAPI schema validation library

**Recommendation:** Option 1 for initial implementation; schema validation is orthogonal concern

**Status:** OPEN - Considered out of scope per OS-6

---

### OQ-9: Unresolved From Previous Sections

#### OQ-9.1: Windows Development Environment Support

**Question (from DR-4.2):** Are there Windows-specific issues with the Playwright API testing setup?

**Context:** Operational risks identified potential cross-platform compatibility issues. Node.js and Playwright are cross-platform, but shell scripts and Docker behavior may differ.

**Research Needed:**
- Test setup-realm.sh execution on Windows (Git Bash, WSL)
- Verify Makefile targets work on Windows
- Document any Windows-specific requirements

**Status:** OPEN - Requires testing on Windows during implementation

---

#### OQ-9.2: Keycloak Version Upgrade Path

**Question (from DR-4.3):** What is the testing and validation process when upgrading Keycloak versions?

**Context:** The template defaults to Keycloak 23.0. Projects may upgrade to newer versions (24.x, 25.x).

**Documentation Needed:**
- List of tested Keycloak versions
- Known compatibility issues
- Upgrade testing procedure

**Status:** OPEN - Document during Phase 8 validation

---

### Open Questions Summary

| ID | Question | Priority | Status | Owner |
|----|----------|----------|--------|-------|
| OQ-1.1 | Password grant migration timeline | Medium | OPEN | Architecture Team |
| OQ-1.2 | Token caching strategy | Low | OPEN | Implementation Phase |
| OQ-2.1 | Test user password complexity | Low | OPEN | Implementation Phase |
| OQ-2.2 | Additional test user roles | Low | RESOLVED | - |
| OQ-3.1 | TypeScript vs JavaScript | Medium | OPEN | Team Decision |
| OQ-3.2 | Playwright directory location | Medium | RESOLVED | - |
| OQ-4.1 | GitHub Actions workflow template | Low | OPEN | Scope Decision |
| OQ-4.2 | Parallel test execution in CI | Low | OPEN | Implementation Phase |
| OQ-5.1 | Video tutorial content | Low | RESOLVED | - |
| OQ-5.2 | Troubleshooting guide depth | Low | OPEN | Post-Launch |
| OQ-6.1 | Large test suite performance | Medium | OPEN | Implementation Phase |
| OQ-6.2 | Keycloak load during tests | Low | OPEN | Implementation Phase |
| OQ-7.1 | Client secret storage | Medium | RESOLVED | - |
| OQ-7.2 | Test artifacts in VCS | Low | RESOLVED | - |
| OQ-8.1 | GraphQL testing support | Low | OPEN | Future Phase |
| OQ-8.2 | Contract testing integration | Low | OPEN | Future Phase |
| OQ-9.1 | Windows environment support | Medium | OPEN | Implementation Phase |
| OQ-9.2 | Keycloak version upgrade path | Low | OPEN | Phase 8 |

**Summary:**
- **6 RESOLVED**: Questions answered by existing FRD sections or design decisions
- **12 OPEN**: Questions to be addressed during implementation or requiring stakeholder input
- **3 High Priority**: OQ-1.1, OQ-3.1, OQ-9.1 should be resolved before implementation begins

---

## Status

| Date | Section Completed | Notes |
|------|-------------------|-------|
| 2025-12-04 | Problem Statement | Initial FRD created. Analyzed implementation-manager Playwright setup and compared with current template. |
| 2025-12-04 | Goals & Success Criteria | Defined 5 primary goals (G1-G5), success metrics, non-goals, timeline, and definition of done. Referenced implementation-manager patterns. |
| 2025-12-04 | Scope & Boundaries | Defined 8 in-scope items (IS-1 through IS-8), 7 out-of-scope exclusions (OS-1 through OS-7), phase boundaries, and related features. |
| 2025-12-04 | User Stories / Use Cases | Defined 15 user stories (US-1 through US-15) covering 3 actor categories: Backend Developer, QA Engineer, and DevOps/New Team Member. Includes concrete code examples from implementation-manager reference. |
| 2025-12-04 | Functional Requirements | Defined 28 requirements (FR-1.1 through FR-10.2) across 10 functional areas. 19 Must Have, 9 Should Have. Includes acceptance criteria, verification steps, function signatures, and configuration tables. All requirements reference implementation-manager patterns and use cookiecutter template variables. |
| 2025-12-04 | Technical Approach | Defined 13 technical approach sections (TA-1 through TA-13) covering technology stack, authentication strategy (OAuth 2.0 password grant), fixture architecture, template integration, test user management, configuration, API endpoints, error handling, Makefile integration, documentation, and codebase references. Includes ASCII diagrams, code examples, and decision rationale. |
| 2025-12-04 | Architecture & Integration Considerations | Defined 12 architecture sections (AI-1 through AI-12) covering system architecture overview with component diagrams, integration points (Playwright-Keycloak, Playwright-Backend, Backend-Keycloak JWKS), data flow architecture with authentication sequence diagrams, network architecture with Docker Compose topology, API contract alignment, fixture architecture deep dive, multi-tenancy considerations with RLS implications, error handling and resilience patterns, CI/CD integration architecture, template integration points, scalability considerations, and security architecture. Includes extensive ASCII diagrams showing data flow and service communication. |
| 2025-12-04 | Data Models & Schema Changes | Defined 9 data model sections (DM-1 through DM-9) covering: no application database changes needed, TestUser data model with JSDoc interfaces, AuthenticatedContext model for fixtures, Keycloak realm schema changes (5 new roles, 6 new test users), configuration data models, OAuth token response model, JWT claims reference, data synchronization requirements across systems, and file artifact storage. Explicitly documents that this feature requires no PostgreSQL/SQLAlchemy changes. |
| 2025-12-04 | UI/UX Considerations | Defined 10 UI/UX sections (UX-1 through UX-10) covering developer experience philosophy (DX), command-line interface design with Makefile and npm script conventions, Playwright visual interfaces (UI mode, HTML reports, trace viewer), test file and fixture ergonomics, error message design patterns, documentation UX (README and QUICK_START structure), IDE integration (VSCode and JetBrains), common workflow scenarios (onboarding, feature development, debugging), accessibility considerations for terminal and HTML output, and consistency with project conventions. This feature focuses on DX rather than traditional UI since it is a developer-facing testing infrastructure. |
| 2025-12-04 | Security & Privacy Considerations | Defined 10 security sections (SP-1 through SP-10) covering test credential security (storage principles, OAuth client secret management), network security considerations (environment isolation, transport security with diagrams), token security (JWT handling, invalid token testing patterns), test data privacy (user data isolation using RFC 2606 example.com domain, artifact security with gitignore configuration), authorization testing security (RBAC test coverage matrix, privilege escalation prevention), secret rotation and lifecycle documentation, CI/CD pipeline security (GitHub Actions secrets, trace security), GDPR compliance considerations, security documentation requirements, and implementation checklists. References industry best practices from BrowserStack, Awesome Testing, and other sources. |
| 2025-12-04 | Testing Strategy | Defined 13 testing strategy sections (TS-1 through TS-13) covering: meta-testing philosophy for testing infrastructure, unit testing approach for auth-helper and test-users modules, integration testing approach with authentication and fixture tests, E2E testing approach for template generation validation, RBAC test matrix with role/endpoint permission grid, error handling and edge case testing (authentication errors, API errors, token edge cases), performance testing considerations with baseline metrics, test data management including user validation and cleanup patterns, test execution modes (local, interactive UI, debug, CI), test reporting and debugging with HTML reports and trace analysis, test organization and naming conventions, test coverage requirements (minimum 17 tests across 6 categories), and test maintenance strategy with review checklists. References Playwright best practices and implementation-manager patterns. |
| 2025-12-04 | Implementation Phases | Defined 8 implementation phases (IP-1 through IP-8) with comprehensive breakdown: Phase 1 (Foundation Setup) establishes directory structure, package.json, playwright.config.js; Phase 2 (Authentication Infrastructure) implements auth-helper.js and test-users.js; Phase 3 (Fixture System) creates fixtures.js with authenticated request contexts; Phase 4 (Example Test Suites) delivers api-endpoints.api.spec.js and api-with-fixtures.api.spec.js; Phase 5 (Keycloak Integration) updates setup-realm.sh with 5 new roles and 6 test users; Phase 6 (Build System Integration) adds Makefile targets; Phase 7 (Documentation) creates README.md and QUICK_START.md; Phase 8 (Validation and Testing) ensures CI readiness. Total estimated effort: 16-24 hours (2-3 days). Includes implementation sequence diagram, rollout strategy, rollback plan, and complexity/effort summary table. All phases reference implementation-manager patterns and include entry/exit criteria, deliverables, and verification steps. |
| 2025-12-04 | Dependencies & Risks | Defined 7 dependency and risk sections (DR-1 through DR-7) covering: external dependencies (Playwright @1.56.1, Keycloak 23.0, FastAPI backend, Docker Compose), internal dependencies (cookiecutter template system, Keycloak realm setup script, Makefile integration), technical risks (OAuth 2.0 password grant deprecation with migration path, test credential exposure, token expiration, CI network isolation, template variable escaping), operational risks (documentation maintenance, cross-platform compatibility, Keycloak version compatibility), risk mitigation summary table with probability/impact ratings, dependency version matrix with minimum/recommended/maximum versions, and contingency plans for password grant removal, Playwright breaking changes, and Docker resource constraints. References OAuth 2.1 deprecation guidance and Playwright best practices. |
| 2025-12-04 | Open Questions | Defined 18 open questions (OQ-1.1 through OQ-9.2) across 9 categories: Authentication Flow Evolution (password grant migration, token caching), Test User Management (password complexity, additional roles), Template Integration (TypeScript vs JavaScript, directory location), CI/CD Integration (GitHub Actions workflow, parallel execution), Documentation Scope (video tutorials, troubleshooting depth), Performance and Scalability (large suite performance, Keycloak load), Security Considerations (client secret storage, artifact handling), Future Enhancements (GraphQL support, contract testing), and Unresolved From Previous Sections (Windows support, Keycloak upgrade path). 6 questions resolved by existing FRD sections, 12 open questions requiring implementation-phase decisions or stakeholder input. Summary table with priority and owner assignments included. |

**Current Progress**: 14/14 sections complete (100%)

**FRD Status**: Ready for FRD Refiner - All sections complete as of 2025-12-04

**Blockers**: None

**Required Reviews**:
- ~~Architecture Team: Review OQ-1.1 (OAuth password grant migration timeline) before implementation~~ **RESOLVED** - Phased migration approach documented with abstraction layer for future Token Exchange migration
- ~~Team Decision: Review OQ-3.1 (TypeScript vs JavaScript for test files) to confirm recommendation~~ **RESOLVED** - TypeScript selected for consistency with frontend E2E tests

**Key References Used**:
- `/home/ty/workspace/project-starter/implementation-manager/playwright/` - Reference API testing implementation
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/fixtures.js` - Authenticated request context pattern
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/test-users.js` - Test user fixture definitions
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/auth-helper.js` - Keycloak authentication helper pattern
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-endpoints.api.spec.js` - Basic API test patterns
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-with-fixtures.api.spec.js` - Fixture-based test patterns
- `/home/ty/workspace/project-starter/implementation-manager/playwright/README.md` - Documentation structure and test user reference
- `/home/ty/workspace/project-starter/implementation-manager/Makefile` - Makefile target patterns for Playwright
- `/home/ty/workspace/project-starter/implementation-manager/backend/main.py` - API endpoints structure (/, /health, /protected, /admin)
- `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/frontend/playwright.config.ts` - Current template frontend E2E config
- `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/keycloak/setup-realm.sh` - Current Keycloak realm setup script

