# TASK-13: Validation and End-to-End Testing

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-13 |
| Title | Validation and End-to-End Testing |
| Domain | QA/Integration |
| Complexity | M (Medium) |
| Estimated Effort | 3-4 hours |
| Dependencies | All prior tasks (TASK-01 through TASK-12) |
| Blocks | None (final task) |

---

## Scope

### What This Task Includes

1. Validate template generation produces correct structure
2. Verify all cookiecutter variables are resolved
3. Validate dependency installation succeeds
4. Run full test suite and verify all tests pass
5. Test CI mode configuration
6. Validate documentation accuracy
7. Verify no regressions in existing template functionality

### What This Task Excludes

- Implementation changes (completed in prior tasks)
- Documentation updates (TASK-11, TASK-12)
- New feature development

---

## Validation Checklist

### V-1: Template Generation Validation

**Objective:** Verify the cookiecutter template generates a valid project.

```bash
# Clean test environment
rm -rf /tmp/playwright-validation
mkdir -p /tmp/playwright-validation
cd /tmp/playwright-validation

# Generate project with default values
cookiecutter /home/ty/workspace/project-starter/template/ \
  --no-input \
  project_name="Playwright Validation Test" \
  project_slug="playwright-validation"

# Verify playwright directory exists
ls -la playwright-validation/playwright/
```

**Validation Points:**

| Check | Expected Result | Pass/Fail |
|-------|-----------------|-----------|
| playwright/ directory exists | Directory present | |
| playwright/tests/ directory exists | Directory present | |
| package.json present | File exists | |
| playwright.config.ts present | File exists | |
| tsconfig.json present | File exists | |
| .gitignore present | File exists | |
| auth-helper.ts present | File in tests/ | |
| test-users.ts present | File in tests/ | |
| fixtures.ts present | File in tests/ | |
| api-endpoints.api.spec.ts present | File in tests/ | |
| api-with-fixtures.api.spec.ts present | File in tests/ | |
| README.md present | File exists | |
| QUICK_START.md present | File exists | |
| Makefile present (root) | File exists | |

### V-2: Cookiecutter Variable Resolution

**Objective:** Verify no unresolved cookiecutter variables remain.

```bash
cd playwright-validation

# Search for unresolved variables
grep -r "{{ cookiecutter" . --include="*.ts" --include="*.json" --include="*.md" --include="Makefile"

# Expected: No output (all variables resolved)
```

**Validation Points:**

| File Type | Check | Pass/Fail |
|-----------|-------|-----------|
| TypeScript files | No `{{ cookiecutter.*` | |
| JSON files | No `{{ cookiecutter.*` | |
| Markdown files | No `{{ cookiecutter.*` | |
| Makefile | No `{{ cookiecutter.*` | |
| Shell scripts | No `{{ cookiecutter.*` | |

### V-3: Dependency Installation

**Objective:** Verify npm install succeeds.

```bash
cd playwright-validation/playwright

# Install dependencies
npm install

# Verify Playwright is installed
npx playwright --version

# Verify TypeScript is installed
npx tsc --version

# Check for peer dependency warnings
npm ls @playwright/test
```

**Validation Points:**

| Check | Expected Result | Pass/Fail |
|-------|-----------------|-----------|
| npm install exits 0 | No errors | |
| @playwright/test installed | Version shown | |
| typescript installed | Version shown | |
| No peer dependency errors | Clean output | |

### V-4: TypeScript Compilation

**Objective:** Verify TypeScript files compile without errors.

```bash
cd playwright-validation/playwright

# Run TypeScript check
npx tsc --noEmit

# Expected: No output (no errors)
```

**Validation Points:**

| File | Compiles Without Error | Pass/Fail |
|------|------------------------|-----------|
| playwright.config.ts | Yes | |
| tests/auth-helper.ts | Yes | |
| tests/test-users.ts | Yes | |
| tests/fixtures.ts | Yes | |
| tests/api-endpoints.api.spec.ts | Yes | |
| tests/api-with-fixtures.api.spec.ts | Yes | |

### V-5: Test Execution (Local Mode)

**Objective:** Verify all tests pass with services running.

```bash
cd playwright-validation

# Start services
make docker-up

# Wait for services
sleep 30  # Or use make keycloak-wait

# Setup Keycloak realm
make keycloak-setup

# Run all tests
make test-api

# Capture results
echo "Test execution completed"
```

**Validation Points:**

| Test File | Tests Passed | Tests Failed | Pass/Fail |
|-----------|--------------|--------------|-----------|
| api-endpoints.api.spec.ts | 16+ | 0 | |
| api-with-fixtures.api.spec.ts | 18+ | 0 | |
| **Total** | 34+ | 0 | |

### V-6: Test Execution (CI Mode)

**Objective:** Verify tests work in CI mode.

```bash
cd playwright-validation/playwright

# Run in CI mode
CI=true npm test

# Expected: Tests pass with CI settings
```

**Validation Points:**

| Check | Expected Result | Pass/Fail |
|-------|-----------------|-----------|
| Tests run with single worker | Yes | |
| Retries configured | 2 retries | |
| No webServer auto-start | Services pre-started | |
| Exit code 0 | Tests pass | |

### V-7: Documentation Validation

**Objective:** Verify documentation accuracy.

```bash
cd playwright-validation

# Follow QUICK_START guide
cat playwright/QUICK_START.md

# Verify each step works as documented
```

**Validation Points:**

| Documentation Element | Accurate | Pass/Fail |
|-----------------------|----------|-----------|
| QUICK_START steps work | Yes | |
| README code examples valid | Yes | |
| User credentials correct | Yes | |
| Environment variables documented | Yes | |
| Troubleshooting issues covered | Yes | |

### V-8: Makefile Validation

**Objective:** Verify all Makefile targets work.

```bash
cd playwright-validation

# Test help target
make help

# Test each target
make test-install
make test-api
make test-report
```

**Validation Points:**

| Target | Works | Pass/Fail |
|--------|-------|-----------|
| help | Yes | |
| docker-up | Yes | |
| docker-down | Yes | |
| keycloak-setup | Yes | |
| test | Yes | |
| test-api | Yes | |
| test-ui | Yes | |
| test-debug | Yes | |
| test-report | Yes | |
| test-install | Yes | |

### V-9: Keycloak User Validation

**Objective:** Verify all test users authenticate correctly.

```bash
cd playwright-validation

# Get admin token and verify each user
KEYCLOAK_URL="http://localhost:8080"
REALM="playwright-validation-dev"  # Default realm name
CLIENT_ID="backend-api"
CLIENT_SECRET="backend-api-secret"

for USER_COMBO in "admin:admin123" "testuser:test123" "readonly:readonly123" "newuser:newuser123" "manager:manager123" "service-account:service123"; do
  USER=$(echo $USER_COMBO | cut -d: -f1)
  PASS=$(echo $USER_COMBO | cut -d: -f2)

  TOKEN=$(curl -s -X POST \
    "$KEYCLOAK_URL/realms/$REALM/protocol/openid-connect/token" \
    -d "client_id=$CLIENT_ID" \
    -d "client_secret=$CLIENT_SECRET" \
    -d "username=$USER" \
    -d "password=$PASS" \
    -d "grant_type=password" | jq -r '.access_token')

  if [ "$TOKEN" != "null" ] && [ -n "$TOKEN" ]; then
    echo "PASS: $USER authenticated"
  else
    echo "FAIL: $USER failed"
  fi
done
```

**Validation Points:**

| User | Authenticates | Pass/Fail |
|------|---------------|-----------|
| admin | Yes | |
| testuser | Yes | |
| readonly | Yes | |
| newuser | Yes | |
| manager | Yes | |
| service-account | Yes | |

### V-10: Regression Testing

**Objective:** Verify existing template functionality still works.

```bash
cd playwright-validation

# Backend tests still pass
docker compose exec backend pytest tests/ --tb=short

# Frontend E2E tests still work (if they exist)
cd frontend
npm run test:e2e
```

**Validation Points:**

| Existing Feature | Still Works | Pass/Fail |
|------------------|-------------|-----------|
| Backend unit tests pass | Yes | |
| Backend API endpoints work | Yes | |
| Frontend E2E tests pass | Yes | |
| Docker Compose services start | Yes | |
| Keycloak existing users (alice, bob) work | Yes | |

---

## Validation Report Template

```markdown
# Playwright API Testing - Validation Report

**Date:** YYYY-MM-DD
**Validator:** [Name]
**Template Version:** [Git commit/tag]

## Summary

| Category | Pass | Fail | Total |
|----------|------|------|-------|
| V-1: Template Generation | | | 14 |
| V-2: Variable Resolution | | | 5 |
| V-3: Dependencies | | | 4 |
| V-4: TypeScript | | | 6 |
| V-5: Local Tests | | | 2 |
| V-6: CI Tests | | | 4 |
| V-7: Documentation | | | 5 |
| V-8: Makefile | | | 10 |
| V-9: Keycloak Users | | | 6 |
| V-10: Regression | | | 5 |
| **TOTAL** | | | 61 |

## Issues Found

1. [Issue description]
   - Severity: High/Medium/Low
   - Task to fix: TASK-XX
   - Resolution: [Description]

## Conclusion

[ ] PASS - Ready for merge
[ ] FAIL - Issues must be resolved
```

---

## Success Criteria

1. **All Checks Pass**: 100% of validation points pass
2. **No Regressions**: Existing template features still work
3. **Documentation Accurate**: QUICK_START guide works as written
4. **CI Ready**: Tests pass in CI mode

---

## Verification Steps

Run the complete validation suite:

```bash
# Execute all validation steps in sequence
cd /tmp
./run-playwright-validation.sh

# Review report
cat /tmp/playwright-validation/VALIDATION_REPORT.md
```

---

## Integration Points

### Upstream Dependencies

- All prior tasks (TASK-01 through TASK-12) must be complete

### Downstream Dependencies

None - this is the final task.

---

## Notes

1. **Clean Environment**: Validation should be run in a clean directory to simulate a fresh project generation.

2. **Service Dependencies**: Some validation steps require Docker services to be running.

3. **Timing**: Allow sufficient time for services to start (Keycloak takes ~30 seconds).

4. **Issue Resolution**: If validation fails, create follow-up tasks or return to relevant prior tasks for fixes.

---

## FRD References

- IP-8: Phase 8 - Validation and Testing
- All acceptance criteria from prior phases

---

*Task Created: 2025-12-04*
*Status: Not Started*
