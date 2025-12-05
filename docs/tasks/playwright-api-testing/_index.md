# Task Breakdown: Playwright API Testing Support

## Feature Overview

Add Playwright API testing infrastructure to the cookiecutter template, enabling developers to test FastAPI backend endpoints with authenticated requests using Keycloak OAuth 2.0.

**Source FRD:** [frd.md](./frd.md)

**Key Decisions:**
- Use TypeScript for all test files (`*.api.spec.ts`)
- Start with password grant, design abstraction layer for future Token Exchange migration
- Template location: `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/`
- Reference implementation: `/home/ty/workspace/project-starter/implementation-manager/playwright/`

---

## Task List

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| TASK-01 | [Foundation Setup - Directory and Package Configuration](./task-01-foundation-setup.md) | Not Started | Backend/DevOps | S | None |
| TASK-02 | [Playwright Configuration](./task-02-playwright-config.md) | Not Started | Backend/DevOps | S | TASK-01 |
| TASK-03 | [Authentication Helper Module](./task-03-auth-helper.md) | Not Started | Backend | M | TASK-01 |
| TASK-04 | [Test Users Module](./task-04-test-users.md) | Not Started | Backend | S | TASK-01 |
| TASK-05 | [Fixture System Implementation](./task-05-fixtures.md) | Not Started | Backend | M | TASK-03, TASK-04 |
| TASK-06 | [Admin Endpoint Creation](./task-06-admin-endpoint.md) | Not Started | Backend | S | None |
| TASK-07 | [Basic API Test Suite (Manual Auth)](./task-07-basic-tests.md) | Not Started | Backend | M | TASK-03, TASK-06 |
| TASK-08 | [Fixture-Based Test Suite](./task-08-fixture-tests.md) | Not Started | Backend | M | TASK-05, TASK-06 |
| TASK-09 | [Keycloak Realm Script Updates](./task-09-keycloak-setup.md) | Not Started | DevOps | M | TASK-04 |
| TASK-10 | [Makefile Integration](./task-10-makefile.md) | Not Started | DevOps | S | TASK-01 |
| TASK-11 | [Documentation - README](./task-11-readme.md) | Not Started | Documentation | M | TASK-01 through TASK-10 |
| TASK-12 | [Documentation - Quick Start Guide](./task-12-quickstart.md) | Not Started | Documentation | S | TASK-11 |
| TASK-13 | [Validation and End-to-End Testing](./task-13-validation.md) | Not Started | QA/Integration | M | All prior tasks |

---

## Dependency Graph

```
                                    +------------------+
                                    |    TASK-01       |
                                    | Foundation Setup |
                                    +--------+---------+
                                             |
              +-------------+----------------+----------------+---------------+
              |             |                |                |               |
              v             v                v                v               v
      +-------+-----+ +-----+------+ +-------+------+ +-------+------+ +------+-----+
      |   TASK-02   | |  TASK-03   | |   TASK-04    | |   TASK-10    | |  TASK-06   |
      |  PW Config  | | Auth Helper| |  Test Users  | |   Makefile   | | Admin EP   |
      +------+------+ +-----+------+ +------+-------+ +--------------+ +-----+------+
             |              |               |                                |
             |              +-------+-------+                                |
             |                      |                                        |
             v                      v                                        |
      +------+------+        +------+------+                                 |
      |   (ready)   |        |   TASK-05   |                                 |
      +-------------+        |   Fixtures  |                                 |
                             +------+------+                                 |
                                    |                                        |
                     +--------------+--------------+                         |
                     |                             |                         |
                     v                             v                         |
              +------+------+               +------+------+                  |
              |   TASK-07   |               |   TASK-08   |<-----------------+
              | Basic Tests |               |Fixture Tests|
              +------+------+               +------+------+
                     |                             |
                     +-------------+---------------+
                                   |
                     +-------------+---------------+
                     |                             |
                     v                             v
              +------+------+               +------+------+
              |   TASK-09   |               |   TASK-11   |
              |  Keycloak   |               |   README    |
              +------+------+               +------+------+
                     |                             |
                     +-------------+---------------+
                                   |
                                   v
                            +------+------+
                            |   TASK-12   |
                            | Quick Start |
                            +------+------+
                                   |
                                   v
                            +------+------+
                            |   TASK-13   |
                            | Validation  |
                            +-------------+
```

---

## Domain Distribution

### Backend Agent
- TASK-03: Authentication Helper Module
- TASK-04: Test Users Module
- TASK-05: Fixture System Implementation
- TASK-06: Admin Endpoint Creation
- TASK-07: Basic API Test Suite
- TASK-08: Fixture-Based Test Suite

### DevOps Agent
- TASK-01: Foundation Setup
- TASK-02: Playwright Configuration
- TASK-09: Keycloak Realm Script Updates
- TASK-10: Makefile Integration

### Documentation Agent
- TASK-11: Documentation - README
- TASK-12: Documentation - Quick Start Guide

### QA/Integration Agent
- TASK-13: Validation and End-to-End Testing

---

## Progress Tracking

**Current Status:** 0 of 13 tasks completed (0%)

**Next Task to Document:** TASK-01 (Foundation Setup)

**Blockers:** None

---

## Integration Contracts

### Contract IC-1: Auth Helper Interface

The `auth-helper.ts` module must export:
```typescript
export async function getAccessToken(request: APIRequestContext, username: string, password: string): Promise<string>;
export async function getAdminToken(request: APIRequestContext): Promise<string>;
export async function getTestUserToken(request: APIRequestContext): Promise<string>;
export function authHeader(token: string): { Authorization: string };
export const KEYCLOAK_URL: string;
export const KEYCLOAK_REALM: string;
```

### Contract IC-2: Test Users Interface

The `test-users.ts` module must export:
```typescript
export interface TestUser {
  username: string;
  password: string;
  email: string;
  roles: string[];
  description: string;
}

export const TEST_USERS: Record<string, TestUser>;
export function getUserByRole(role: string): TestUser | undefined;
export function getUsersByRole(role: string): TestUser[];
export function getAllUsers(): TestUser[];
```

### Contract IC-3: Fixtures Interface

The `fixtures.ts` module must export an extended `test` object:
```typescript
import { test as base } from '@playwright/test';

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
```

### Contract IC-4: Admin Endpoint Response

The `/api/v1/test/admin` endpoint must return:
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

---

## Notes and Refinements

1. **TypeScript Decision:** FRD originally specified JavaScript (CommonJS), but the decision was made to use TypeScript for consistency with the frontend. Files will be `*.api.spec.ts` instead of `*.api.spec.js`.

2. **Authentication Abstraction:** Design the auth-helper with an interface that can be swapped to Token Exchange in the future without changing test code.

3. **No Existing Makefile:** The template does not currently have a Makefile. TASK-10 will create one from scratch using the implementation-manager Makefile as a reference.

4. **Admin Endpoint Gap:** The FRD identifies that the template lacks an admin-only endpoint for RBAC testing. TASK-06 addresses this by adding the endpoint before tests are written.

5. **Parallel Execution:** TASK-01, TASK-02, TASK-06, and TASK-10 have no dependencies on each other and can be executed in parallel.

---

## File References

### Reference Implementation
- `/home/ty/workspace/project-starter/implementation-manager/playwright/playwright.config.js`
- `/home/ty/workspace/project-starter/implementation-manager/playwright/package.json`
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/auth-helper.js`
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/test-users.js`
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/fixtures.js`
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-endpoints.api.spec.js`
- `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/api-with-fixtures.api.spec.js`

### Template Files to Create
- `template/{{cookiecutter.project_slug}}/playwright/package.json`
- `template/{{cookiecutter.project_slug}}/playwright/playwright.config.ts`
- `template/{{cookiecutter.project_slug}}/playwright/tsconfig.json`
- `template/{{cookiecutter.project_slug}}/playwright/.gitignore`
- `template/{{cookiecutter.project_slug}}/playwright/tests/auth-helper.ts`
- `template/{{cookiecutter.project_slug}}/playwright/tests/test-users.ts`
- `template/{{cookiecutter.project_slug}}/playwright/tests/fixtures.ts`
- `template/{{cookiecutter.project_slug}}/playwright/tests/api-endpoints.api.spec.ts`
- `template/{{cookiecutter.project_slug}}/playwright/tests/api-with-fixtures.api.spec.ts`
- `template/{{cookiecutter.project_slug}}/playwright/README.md`
- `template/{{cookiecutter.project_slug}}/playwright/QUICK_START.md`
- `template/{{cookiecutter.project_slug}}/Makefile`

### Template Files to Modify
- `template/{{cookiecutter.project_slug}}/keycloak/setup-realm.sh`
- `template/{{cookiecutter.project_slug}}/backend/app/api/routers/test_auth.py`
- `template/{{cookiecutter.project_slug}}/CLAUDE.md`

---

## Estimated Total Effort

| Complexity | Count | Effort per Task | Total |
|------------|-------|-----------------|-------|
| S (Small)  | 5     | 2-3 hours       | 10-15 hours |
| M (Medium) | 8     | 3-5 hours       | 24-40 hours |

**Total Estimated Effort:** 34-55 hours (4-7 days)

---

*Last Updated: 2025-12-04*
*Breakdown Status: In Progress*
