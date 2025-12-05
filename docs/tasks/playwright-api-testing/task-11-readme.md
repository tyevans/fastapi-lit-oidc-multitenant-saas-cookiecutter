# TASK-11: Documentation - README

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-11 |
| Title | Documentation - README |
| Domain | Documentation |
| Complexity | M (Medium) |
| Estimated Effort | 3-4 hours |
| Dependencies | TASK-01 through TASK-10 |
| Blocks | TASK-12, TASK-13 |

---

## Scope

### What This Task Includes

1. Create comprehensive `playwright/README.md`
2. Document all available fixtures and their usage
3. Document test user credentials and roles
4. Provide code examples for both patterns (fixture and manual)
5. Document environment variables and configuration
6. Include troubleshooting guide for common issues
7. Add CI/CD integration notes

### What This Task Excludes

- Quick Start guide (TASK-12)
- Actual test files (TASK-07, TASK-08)
- Implementation details

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/README.md` | Comprehensive documentation |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/README.md` | Reference documentation (if exists) |
| Completed tasks TASK-01 through TASK-10 | Source of truth for features |

---

## Implementation Details

### README.md Specification

```markdown
# Playwright API Testing

This directory contains the API testing infrastructure for {{ cookiecutter.project_name }}, built on [Playwright](https://playwright.dev/docs/api-testing).

## Overview

The API testing framework provides:
- **Pre-authenticated request contexts** for all test users
- **TypeScript support** for type-safe test development
- **Fixture-based patterns** for clean, maintainable tests
- **Role-based testing** for RBAC validation
- **Integration with Keycloak** for OAuth 2.0 authentication

## Prerequisites

Before running tests, ensure you have:

1. **Node.js 18+** installed
2. **Docker** and **Docker Compose** running
3. **Backend services** started (`make docker-up`)
4. **Keycloak realm** configured (`make keycloak-setup`)

## Quick Start

```bash
# 1. Install dependencies
make test-install

# 2. Start services (if not already running)
make docker-up

# 3. Setup Keycloak (if first time)
make keycloak-setup

# 4. Run tests
make test-api

# 5. View report
make test-report
```

## Project Structure

```
playwright/
├── playwright.config.ts    # Playwright configuration
├── package.json            # Dependencies and npm scripts
├── tsconfig.json           # TypeScript configuration
├── README.md               # This file
├── QUICK_START.md          # 5-minute getting started guide
└── tests/
    ├── auth-helper.ts      # Keycloak authentication utilities
    ├── test-users.ts       # Test user definitions
    ├── fixtures.ts         # Extended Playwright fixtures
    ├── api-endpoints.api.spec.ts      # Basic tests (manual auth)
    └── api-with-fixtures.api.spec.ts  # Fixture-based tests (recommended)
```

## Writing Tests

### Recommended Pattern: Using Fixtures

The fixture pattern is the **recommended approach** for writing API tests. Fixtures automatically handle authentication, providing pre-configured request contexts for each test user.

```typescript
import { test, expect } from './fixtures';

test('admin can access admin endpoint', async ({ adminRequest }) => {
  const response = await adminRequest.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');

  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.user.username).toBe('admin');
  expect(data.user.roles).toContain('admin');
});

test('regular user cannot access admin endpoint', async ({ userRequest }) => {
  const response = await userRequest.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');

  expect(response.status()).toBe(403);
});
```

### Multi-User Testing

For tests that need to compare access levels between users:

```typescript
test('compare admin and user access', async ({ authenticatedRequest }) => {
  // Admin can access
  const adminResp = await authenticatedRequest.admin.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');
  expect(adminResp.ok()).toBeTruthy();

  // User cannot access
  const userResp = await authenticatedRequest.user.get('/{{ cookiecutter.backend_api_prefix }}/test/admin');
  expect(userResp.status()).toBe(403);
});
```

### Accessing User Metadata

Fixtures provide access to user information and tokens:

```typescript
test('can access user info', async ({ adminRequest }) => {
  // User metadata
  console.log(adminRequest.user.username);  // 'admin'
  console.log(adminRequest.user.roles);     // ['user', 'admin']
  console.log(adminRequest.user.email);     // 'admin@example.com'

  // Raw JWT token (for custom scenarios)
  const token = adminRequest.token;
});
```

### Advanced Pattern: Manual Authentication

For custom authentication scenarios or testing invalid tokens:

```typescript
import { test, expect } from '@playwright/test';
import { getAccessToken, authHeader } from './auth-helper';

test('custom auth scenario', async ({ request }) => {
  const token = await getAccessToken(request, 'admin', 'admin123');
  const response = await request.get('/{{ cookiecutter.backend_api_prefix }}/auth/me', {
    headers: {
      ...authHeader(token),
      'X-Custom-Header': 'custom-value',
    },
  });

  expect(response.ok()).toBeTruthy();
});
```

## Available Fixtures

| Fixture | User | Roles | Description |
|---------|------|-------|-------------|
| `adminRequest` | admin | user, admin | Full administrative access |
| `userRequest` | testuser | user | Standard authenticated user |
| `readOnlyRequest` | readonly | user, readonly | Read-only access |
| `managerRequest` | manager | user, manager | Elevated permissions |
| `authenticatedRequest` | All users | Various | Access to all user contexts |

### authenticatedRequest Properties

The `authenticatedRequest` fixture provides access to all users:

| Property | User | Roles |
|----------|------|-------|
| `.admin` | admin | user, admin |
| `.user` | testuser | user |
| `.readOnly` | readonly | user, readonly |
| `.newUser` | newuser | user |
| `.manager` | manager | user, manager |
| `.serviceAccount` | service-account | service |

## Test Users

All test users are created in Keycloak by the `setup-realm.sh` script.

| Username | Password | Email | Roles | Use Case |
|----------|----------|-------|-------|----------|
| admin | admin123 | admin@example.com | user, admin | Admin-only endpoints |
| testuser | test123 | test@example.com | user | Standard user flows |
| readonly | readonly123 | readonly@example.com | user, readonly | Read-only access testing |
| newuser | newuser123 | newuser@example.com | user | Onboarding flows |
| manager | manager123 | manager@example.com | user, manager | Elevated access testing |
| service-account | service123 | service@example.com | service | API-to-API integration |

## Running Tests

### npm Scripts

```bash
npm test              # Run all tests
npm run test:api      # Run API tests only
npm run test:ui       # Interactive UI mode
npm run test:debug    # Debug mode
npm run report        # Open HTML report
```

### Makefile Targets

```bash
make test             # Run all tests
make test-api         # Run API tests only
make test-ui          # Interactive UI mode
make test-debug       # Debug mode
make test-report      # Open HTML report
make test-install     # Install dependencies
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_URL` | `http://localhost:{{ cookiecutter.backend_port }}` | Backend API base URL |
| `KEYCLOAK_URL` | `http://localhost:{{ cookiecutter.keycloak_port }}` | Keycloak server URL |
| `KEYCLOAK_REALM` | `{{ cookiecutter.keycloak_realm_name }}` | Keycloak realm name |
| `CI` | undefined | Set to `true` in CI environments |

### CI/CD Behavior

When `CI=true`:
- Single worker for test stability
- 2 retries on failure
- No webServer auto-start (services must be pre-started)
- `.only()` tests cause failure

## Troubleshooting

### Common Issues

#### "Failed to get token for 'admin': 401"

**Cause:** Keycloak not configured or user doesn't exist.

**Solution:**
```bash
make keycloak-setup
```

#### "Connection refused"

**Cause:** Backend or Keycloak not running.

**Solution:**
```bash
make docker-up
make keycloak-wait
```

#### "Role 'admin' required"

**Cause:** Using wrong user for admin-only endpoint.

**Solution:** Use `adminRequest` fixture instead of `userRequest`.

#### Tests pass locally but fail in CI

**Cause:** Services not ready when tests start.

**Solution:** Add health check wait before running tests:
```bash
make keycloak-wait
```

### Debug Mode

For debugging failing tests:

```bash
# Run in debug mode (pause on failure)
make test-debug

# Run in UI mode (interactive)
make test-ui

# Run single test file
cd playwright && npx playwright test tests/api-endpoints.api.spec.ts
```

### View Test Report

After running tests, view the HTML report:

```bash
make test-report
```

## API Endpoints

Tests target these backend endpoints:

| Endpoint | Method | Auth Required | Role Required |
|----------|--------|---------------|---------------|
| `/` | GET | No | - |
| `/{{ cookiecutter.backend_api_prefix }}/health` | GET | No | - |
| `/{{ cookiecutter.backend_api_prefix }}/auth/me` | GET | Yes | Any |
| `/{{ cookiecutter.backend_api_prefix }}/test/protected` | GET | Yes | Any |
| `/{{ cookiecutter.backend_api_prefix }}/test/admin` | GET | Yes | admin |

## Contributing

When adding new tests:

1. Use the fixture pattern (`import { test } from './fixtures'`)
2. Name files with `.api.spec.ts` extension
3. Group related tests in `test.describe()` blocks
4. Include both positive and negative test cases
5. Add JSDoc comments for complex scenarios

## Further Reading

- [Playwright API Testing Guide](https://playwright.dev/docs/api-testing)
- [Playwright Fixtures](https://playwright.dev/docs/test-fixtures)
- [Project CLAUDE.md](../CLAUDE.md) for backend patterns
```

---

## Success Criteria

1. **Complete Sections**: All 11 required sections present
2. **Code Examples Work**: Examples are syntactically correct TypeScript
3. **Accurate Information**: User credentials match TASK-04
4. **Formatted Tables**: All tables render correctly in Markdown
5. **Troubleshooting Covers Common Issues**: At least 4 issues documented

---

## Verification Steps

```bash
# Generate project
cookiecutter template/ --no-input project_name="Test Project"
cd test-project/playwright

# Verify README exists
cat README.md

# Verify Markdown renders correctly
# (Use VS Code preview or online Markdown viewer)

# Verify code examples have correct syntax
grep -A 5 "import { test" README.md

# Verify user credentials match test-users.ts
grep "admin123" README.md
```

---

## Integration Points

### Upstream Dependencies

- **TASK-01 through TASK-10**: All features must be complete for accurate documentation

### Downstream Dependencies

This task enables:
- **TASK-12**: Quick Start references README for details
- **TASK-13**: Validation uses documentation for testing

---

## Notes

1. **Cookiecutter Variables**: The README uses cookiecutter variables that will be replaced during project generation.

2. **Code Example Accuracy**: All code examples should be syntactically valid and match the actual implementations.

3. **Section Order**: The order follows the FRD specification (FR-7.1).

4. **Troubleshooting**: Focus on issues that new developers commonly encounter.

---

## FRD References

- FR-7.1: README Structure
- IP-7: Phase 7 - Documentation
- TA-10: Documentation Approach

---

*Task Created: 2025-12-04*
*Status: Not Started*
