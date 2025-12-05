# TASK-04: Test Users Module

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-04 |
| Title | Test Users Module |
| Domain | Backend |
| Complexity | S (Small) |
| Estimated Effort | 2-3 hours |
| Dependencies | TASK-01 |
| Blocks | TASK-05, TASK-09 |

---

## Scope

### What This Task Includes

1. Create `test-users.ts` with TestUser interface definition
2. Define 6 pre-configured test users with credentials and roles
3. Implement `getUserByRole()` helper function
4. Implement `getUsersByRole()` helper function
5. Implement `getAllUsers()` helper function
6. Export all types and functions

### What This Task Excludes

- Keycloak user creation (TASK-09)
- Fixture integration (TASK-05)
- Auth helper integration (TASK-03)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/tests/test-users.ts` | Test user definitions and helper functions |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/tests/test-users.js` | Reference implementation (JavaScript) |

---

## Implementation Details

### test-users.ts Specification

```typescript
/**
 * Test user definitions for Playwright API tests
 *
 * These users must be created in Keycloak by the setup-realm.sh script.
 * The credentials and roles defined here must match the Keycloak configuration.
 *
 * User Naming Convention:
 * - Keys are camelCase for JavaScript convention
 * - Usernames are lowercase or hyphenated for Keycloak compatibility
 *
 * Password Convention:
 * - Pattern: username + '123' for easy memorization
 * - Exception: 'testuser' uses 'test123' for brevity
 */

/**
 * Represents a test user configured in Keycloak
 */
export interface TestUser {
  /** Keycloak username for authentication */
  username: string;

  /** User password (plaintext - development only) */
  password: string;

  /** User email address */
  email: string;

  /** Array of realm roles assigned to this user */
  roles: string[];

  /** Human-readable description of the user's purpose */
  description: string;
}

/**
 * Collection of all test users
 * Keys are used as fixture names (e.g., authenticatedRequest.admin)
 */
export const TEST_USERS: Record<string, TestUser> = {
  /**
   * Admin user with full administrative access
   * Use for testing admin-only endpoints and privileged operations
   */
  admin: {
    username: 'admin',
    password: 'admin123',
    email: 'admin@example.com',
    roles: ['user', 'admin'],
    description: 'Full admin access for privileged operations',
  },

  /**
   * Standard user with basic permissions
   * Use for testing typical authenticated user flows
   */
  user: {
    username: 'testuser',
    password: 'test123',
    email: 'test@example.com',
    roles: ['user'],
    description: 'Standard user for typical authenticated flows',
  },

  /**
   * Read-only user for access control testing
   * Use for testing read-only permissions and denied write operations
   */
  readOnly: {
    username: 'readonly',
    password: 'readonly123',
    email: 'readonly@example.com',
    roles: ['user', 'readonly'],
    description: 'Read-only access for viewing without modification',
  },

  /**
   * Fresh user account for onboarding testing
   * Use for testing first-time user experiences and onboarding flows
   */
  newUser: {
    username: 'newuser',
    password: 'newuser123',
    email: 'newuser@example.com',
    roles: ['user'],
    description: 'Fresh account for onboarding flow tests',
  },

  /**
   * Manager user with elevated permissions
   * Use for testing manager-level operations without full admin access
   */
  manager: {
    username: 'manager',
    password: 'manager123',
    email: 'manager@example.com',
    roles: ['user', 'manager'],
    description: 'Elevated permissions for management operations',
  },

  /**
   * Service account for API-to-API testing
   * Use for testing service-to-service communication patterns
   * Note: Does NOT have 'user' role - only 'service' role
   */
  serviceAccount: {
    username: 'service-account',
    password: 'service123',
    email: 'service@example.com',
    roles: ['service'],
    description: 'Service account for API-to-API integration tests',
  },
};

/**
 * Find the first user that has a specific role
 *
 * @param role - Role name to search for
 * @returns TestUser object or undefined if no user has the role
 *
 * @example
 * const adminUser = getUserByRole('admin');
 * // Returns the 'admin' user
 *
 * @example
 * const serviceUser = getUserByRole('service');
 * // Returns the 'serviceAccount' user
 */
export function getUserByRole(role: string): TestUser | undefined {
  return Object.values(TEST_USERS).find((user) => user.roles.includes(role));
}

/**
 * Find all users that have a specific role
 *
 * @param role - Role name to search for
 * @returns Array of TestUser objects (empty if no users have the role)
 *
 * @example
 * const usersWithUserRole = getUsersByRole('user');
 * // Returns [admin, user, readOnly, newUser, manager] (5 users)
 *
 * @example
 * const admins = getUsersByRole('admin');
 * // Returns [admin] (1 user)
 */
export function getUsersByRole(role: string): TestUser[] {
  return Object.values(TEST_USERS).filter((user) => user.roles.includes(role));
}

/**
 * Get all test users as an array
 *
 * @returns Array of all TestUser objects
 *
 * @example
 * const allUsers = getAllUsers();
 * // Returns array of 6 users
 */
export function getAllUsers(): TestUser[] {
  return Object.values(TEST_USERS);
}

/**
 * Get a specific user by key
 *
 * @param key - User key (admin, user, readOnly, newUser, manager, serviceAccount)
 * @returns TestUser object or undefined if key doesn't exist
 *
 * @example
 * const admin = getUser('admin');
 */
export function getUser(key: keyof typeof TEST_USERS): TestUser {
  return TEST_USERS[key];
}
```

### User Matrix

| Key | Username | Password | Email | Roles | Purpose |
|-----|----------|----------|-------|-------|---------|
| `admin` | admin | admin123 | admin@example.com | user, admin | Full administrative access |
| `user` | testuser | test123 | test@example.com | user | Standard user flows |
| `readOnly` | readonly | readonly123 | readonly@example.com | user, readonly | Read-only access control |
| `newUser` | newuser | newuser123 | newuser@example.com | user | Onboarding testing |
| `manager` | manager | manager123 | manager@example.com | user, manager | Elevated permissions |
| `serviceAccount` | service-account | service123 | service@example.com | service | API-to-API integration |

---

## Success Criteria

1. **All Users Defined**: 6 users with correct credentials and roles
2. **TypeScript Valid**: No TypeScript errors
3. **Query Functions Work**: `getUserByRole()`, `getUsersByRole()`, `getAllUsers()` return correct results
4. **Interface Exported**: `TestUser` interface is importable
5. **Keys Match Fixture Names**: Keys work with fixture destructuring

---

## Verification Steps

```typescript
// tests/verify-users.ts
import { TEST_USERS, getUserByRole, getUsersByRole, getAllUsers, TestUser } from './test-users';

// Verify all 6 users exist
console.assert(Object.keys(TEST_USERS).length === 6, 'Should have 6 users');

// Verify getUserByRole
const adminUser = getUserByRole('admin');
console.assert(adminUser?.username === 'admin', 'Should find admin user');

const serviceUser = getUserByRole('service');
console.assert(serviceUser?.username === 'service-account', 'Should find service account');

// Verify getUsersByRole
const usersWithUserRole = getUsersByRole('user');
console.assert(usersWithUserRole.length === 5, 'Should have 5 users with user role');

// Verify getAllUsers
const allUsers = getAllUsers();
console.assert(allUsers.length === 6, 'Should return all 6 users');

// Verify TypeScript types
const typedUser: TestUser = TEST_USERS.admin;
console.assert(typedUser.roles.includes('admin'), 'Admin should have admin role');

console.log('All verification tests passed!');
```

---

## Integration Points

### Upstream Dependencies

- **TASK-01**: Package.json and TypeScript setup must exist

### Downstream Dependencies

This task enables:
- **TASK-05**: Fixtures iterate over TEST_USERS to create authenticated contexts
- **TASK-09**: Keycloak setup script must create matching users

### Contracts

**Interface Contract (IC-2):**
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

**Data Contract:**
The following users MUST exist with these exact credentials:

| Username | Password | Roles |
|----------|----------|-------|
| admin | admin123 | user, admin |
| testuser | test123 | user |
| readonly | readonly123 | user, readonly |
| newuser | newuser123 | user |
| manager | manager123 | user, manager |
| service-account | service123 | service |

---

## Monitoring and Observability

Not applicable for this task (data definitions only).

---

## Infrastructure Needs

None - this task only creates template files.

---

## Notes

1. **Password Security**: Passwords are stored in plaintext. This is acceptable for development/testing but should be clearly documented.

2. **Role Hierarchy**: The `user` role is a base role for most users. Only `serviceAccount` lacks the `user` role, which is intentional for testing service-level authentication.

3. **Sync with Keycloak**: TASK-09 must create these exact users in Keycloak. Any mismatch will cause authentication failures.

4. **Key Naming**: Keys use camelCase (`readOnly`, `newUser`, `serviceAccount`) for JavaScript convention, while usernames use lowercase/hyphenated (`readonly`, `newuser`, `service-account`) for Keycloak compatibility.

---

## FRD References

- FR-3.1: Test Users File
- FR-3.2: User Query Functions
- FR-3.3: Module Exports
- DM-2: Test User Data Model
- IP-2: Phase 2 - Authentication Infrastructure

---

*Task Created: 2025-12-04*
*Status: Not Started*
