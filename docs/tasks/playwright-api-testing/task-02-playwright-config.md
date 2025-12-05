# TASK-02: Playwright Configuration

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-02 |
| Title | Playwright Configuration |
| Domain | Backend/DevOps |
| Complexity | S (Small) |
| Estimated Effort | 2-3 hours |
| Dependencies | TASK-01 |
| Blocks | TASK-07, TASK-08 |

---

## Scope

### What This Task Includes

1. Create `playwright.config.ts` with API testing configuration
2. Configure baseURL using cookiecutter variables
3. Set up projects for API tests
4. Configure CI-specific settings (retries, workers)
5. Configure webServer for local development auto-start
6. Set up HTML reporter

### What This Task Excludes

- Test files (TASK-07, TASK-08)
- Helper modules (TASK-03, TASK-04, TASK-05)
- Browser-based testing configuration (frontend already has this)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/playwright.config.ts` | Playwright test configuration |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/playwright.config.js` | Reference for API testing config structure |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/frontend/playwright.config.ts` | Reference for TypeScript Playwright config in template |

---

## Implementation Details

### playwright.config.ts Specification

```typescript
import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright configuration for API testing
 * @see https://playwright.dev/docs/api-testing
 */
export default defineConfig({
  // Test directory
  testDir: './tests',

  // Test file pattern - only API spec files
  testMatch: '**/*.api.spec.ts',

  // Timeout per test (30 seconds)
  timeout: 30000,

  // Run tests in parallel
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Limit workers on CI for stability
  workers: process.env.CI ? 1 : undefined,

  // Reporter configuration
  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],

  // Shared settings for all projects
  use: {
    // Base URL for API requests
    baseURL: process.env.BASE_URL || 'http://localhost:{{ cookiecutter.backend_port }}',

    // Collect trace on first retry
    trace: 'on-first-retry',

    // Default headers for API requests
    extraHTTPHeaders: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  },

  // Configure projects
  projects: [
    {
      name: 'API Tests',
      testMatch: '**/*.api.spec.ts',
    },
  ],

  // Run local dev server before starting the tests (development only)
  webServer: process.env.CI
    ? undefined
    : {
        command: 'cd .. && docker compose up -d backend keycloak postgres redis',
        url: 'http://localhost:{{ cookiecutter.backend_port }}/{{ cookiecutter.backend_api_prefix }}/health',
        timeout: 120 * 1000,
        reuseExistingServer: true,
      },
});
```

### Key Configuration Decisions

1. **testMatch Pattern**: `**/*.api.spec.ts` ensures only API test files are matched, avoiding conflicts with frontend E2E tests.

2. **CI Detection**: Uses `process.env.CI` to adjust behavior:
   - `forbidOnly`: Prevents accidental `.only()` commits
   - `retries`: 2 retries in CI, 0 locally
   - `workers`: Single worker in CI for stability
   - `webServer`: Disabled in CI (services pre-started)

3. **baseURL**: Uses cookiecutter variable `{{ cookiecutter.backend_port }}` with environment override via `BASE_URL`.

4. **webServer**: Auto-starts Docker services in development for convenience.

5. **Reporters**:
   - `html`: Generates detailed HTML report
   - `list`: Shows test progress in terminal

---

## Cookiecutter Variables Used

| Variable | Default | Usage |
|----------|---------|-------|
| `{{ cookiecutter.backend_port }}` | 8000 | Base URL for API requests |
| `{{ cookiecutter.backend_api_prefix }}` | /api/v1 | Health check URL path |

---

## Success Criteria

1. **Config Valid**: `npx playwright test --list` shows "API Tests" project
2. **Base URL Correct**: Configuration uses correct backend port from cookiecutter
3. **CI Mode Works**: `CI=true npx playwright test --list` works without webServer
4. **TypeScript Valid**: No TypeScript errors in config file

---

## Verification Steps

```bash
# Generate test project
cookiecutter template/ --no-input project_name="Test Project"
cd test-project/playwright

# Install dependencies
npm install

# Verify configuration is valid
npx playwright test --list

# Check TypeScript compilation
npx tsc --noEmit playwright.config.ts

# Verify CI mode
CI=true npx playwright test --list

# Clean up
cd ../..
rm -rf test-project
```

---

## Integration Points

### Upstream Dependencies

- **TASK-01**: Package.json must exist with Playwright installed

### Downstream Dependencies

This task enables:
- **TASK-07**: Tests need valid Playwright configuration
- **TASK-08**: Tests need valid Playwright configuration

### Contracts

**Configuration Contract:**
```typescript
// These settings must be present:
{
  testDir: './tests',
  testMatch: '**/*.api.spec.ts',
  use: {
    baseURL: 'http://localhost:{{ cookiecutter.backend_port }}',
    extraHTTPHeaders: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    },
  },
  projects: [
    { name: 'API Tests' }
  ]
}
```

**Environment Variable Contract:**
```bash
# These environment variables should override defaults:
BASE_URL=http://custom-host:8080  # Override baseURL
CI=true                            # Enable CI mode
```

---

## Monitoring and Observability

Not directly applicable, but the configuration enables:
- HTML reports for test results visualization
- Trace collection on retries for debugging

---

## Infrastructure Needs

None - this task only creates template files.

---

## Notes

1. **TypeScript Config**: Unlike the JavaScript reference implementation, this uses TypeScript with ES module syntax (`import`/`export`).

2. **webServer Command**: Uses `docker compose` (not `make docker-up`) because there's no Makefile yet. TASK-10 will create the Makefile.

3. **Health Check Path**: The webServer URL uses the health endpoint to verify the backend is ready. The path combines the backend port and API prefix.

4. **No Browser Downloads**: API tests don't need browser binaries. Playwright handles this gracefully.

---

## FRD References

- FR-1.3: Playwright Configuration
- IP-1: Phase 1 - Foundation Setup (Configuration section)
- TA-6: Configuration Management

---

*Task Created: 2025-12-04*
*Status: Not Started*
