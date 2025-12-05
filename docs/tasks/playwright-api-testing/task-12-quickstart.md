# TASK-12: Documentation - Quick Start Guide

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-12 |
| Title | Documentation - Quick Start Guide |
| Domain | Documentation |
| Complexity | S (Small) |
| Estimated Effort | 1-2 hours |
| Dependencies | TASK-11 |
| Blocks | TASK-13 |

---

## Scope

### What This Task Includes

1. Create focused `playwright/QUICK_START.md` guide
2. Provide 5-minute setup-to-first-test flow
3. Include minimal code example for first test
4. Quick reference for test users
5. Links to full README for more details

### What This Task Excludes

- Comprehensive documentation (TASK-11 README)
- Troubleshooting (covered in README)
- Configuration details (covered in README)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/QUICK_START.md` | 5-minute getting started guide |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| TASK-11 README | Full documentation to reference |

---

## Implementation Details

### QUICK_START.md Specification

```markdown
# Quick Start - Playwright API Testing

Get your first API test running in under 5 minutes.

## Prerequisites

- Docker running
- Node.js 18+ installed

## Step 1: Install Dependencies

```bash
make test-install
```

Or without Make:
```bash
cd playwright && npm install
```

## Step 2: Start Services

```bash
make docker-up
```

Wait for services to be ready (about 30 seconds).

## Step 3: Setup Keycloak

```bash
make keycloak-setup
```

This creates test users in Keycloak.

## Step 4: Run Tests

```bash
make test-api
```

Expected output: All tests pass!

## Step 5: View Report

```bash
make test-report
```

Opens an HTML report in your browser.

---

## Write Your First Test

Create a new file `tests/my-first.api.spec.ts`:

```typescript
import { test, expect } from './fixtures';

test('my first API test', async ({ userRequest }) => {
  // Make an authenticated request
  const response = await userRequest.get('/{{ cookiecutter.backend_api_prefix }}/auth/me');

  // Verify the response
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  expect(data.username).toBe('testuser');
});
```

Run your test:
```bash
cd playwright && npx playwright test tests/my-first.api.spec.ts
```

---

## Quick Reference: Available Fixtures

| Fixture | User | Quick Description |
|---------|------|-------------------|
| `adminRequest` | admin | Full admin access |
| `userRequest` | testuser | Standard user |
| `readOnlyRequest` | readonly | Read-only access |
| `managerRequest` | manager | Elevated access |
| `authenticatedRequest` | All | Access all users |

## Quick Reference: Test Users

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| testuser | test123 | User |
| readonly | readonly123 | Read-only |
| manager | manager123 | Manager |

---

## Common Commands

| Command | Description |
|---------|-------------|
| `make test` | Run all tests |
| `make test-api` | Run API tests |
| `make test-ui` | Interactive mode |
| `make test-debug` | Debug mode |
| `make test-report` | View report |

---

## Debugging Tips

### Interactive UI Mode
```bash
make test-ui
```
Opens Playwright's interactive test runner.

### Debug a Failing Test
```bash
make test-debug
```
Pauses execution on failure for inspection.

### Run a Single Test
```bash
cd playwright && npx playwright test tests/my-test.api.spec.ts
```

---

## Next Steps

- Read the full [README](./README.md) for advanced patterns
- Explore example tests in `tests/api-with-fixtures.api.spec.ts`
- Learn about multi-user testing with `authenticatedRequest`

---

*Need help? Check the [Troubleshooting section](./README.md#troubleshooting) in the README.*
```

---

## Success Criteria

1. **Concise**: 50-80 lines, focused content
2. **5-Minute Flow**: Steps 1-5 can be completed in under 5 minutes
3. **Working Example**: First test example is valid TypeScript
4. **Quick References**: User and command tables are scannable
5. **Links to README**: References full documentation for details

---

## Verification Steps

```bash
# Generate project
cookiecutter template/ --no-input project_name="Test Project"
cd test-project/playwright

# Verify QUICK_START exists
cat QUICK_START.md

# Time yourself following the guide
# Should complete in under 5 minutes with services already running

# Verify first test example works
cat > tests/my-first.api.spec.ts << 'EOF'
import { test, expect } from './fixtures';

test('my first API test', async ({ userRequest }) => {
  const response = await userRequest.get('/api/v1/auth/me');
  expect(response.ok()).toBeTruthy();
});
EOF

npx playwright test tests/my-first.api.spec.ts
```

---

## Integration Points

### Upstream Dependencies

- **TASK-11**: README must exist for reference links

### Downstream Dependencies

This task enables:
- **TASK-13**: Validation follows QUICK_START to verify setup

---

## Notes

1. **Focus on Speed**: The guide prioritizes getting started quickly over comprehensive coverage.

2. **Make Commands**: Uses Make commands as primary, with raw commands as fallback.

3. **No Troubleshooting**: Refers to README for troubleshooting to keep the guide short.

4. **First Test Example**: The example uses `userRequest` (simpler than admin) for a gentle introduction.

---

## FRD References

- FR-7.2: QUICK_START Guide
- IP-7: Phase 7 - Documentation
- TA-10: Documentation Approach

---

*Task Created: 2025-12-04*
*Status: Not Started*
