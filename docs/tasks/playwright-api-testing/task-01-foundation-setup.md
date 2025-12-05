# TASK-01: Foundation Setup - Directory and Package Configuration

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-01 |
| Title | Foundation Setup - Directory and Package Configuration |
| Domain | Backend/DevOps |
| Complexity | S (Small) |
| Estimated Effort | 2-3 hours |
| Dependencies | None |
| Blocks | TASK-02, TASK-03, TASK-04, TASK-05, TASK-10 |

---

## Scope

### What This Task Includes

1. Create the `playwright/` directory structure in the cookiecutter template
2. Create `package.json` with Playwright dependencies and npm scripts
3. Create `tsconfig.json` for TypeScript support
4. Create `.gitignore` for Playwright artifacts
5. Create empty `tests/` subdirectory

### What This Task Excludes

- Playwright configuration file (TASK-02)
- Test files and helper modules (TASK-03 through TASK-08)
- Makefile integration (TASK-10)
- Documentation (TASK-11, TASK-12)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/playwright/package.json` | Node.js package configuration |
| `template/{{cookiecutter.project_slug}}/playwright/tsconfig.json` | TypeScript configuration |
| `template/{{cookiecutter.project_slug}}/playwright/.gitignore` | Git ignore for Playwright artifacts |
| `template/{{cookiecutter.project_slug}}/playwright/tests/.gitkeep` | Placeholder for tests directory |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/playwright/package.json` | Reference for package.json structure (needs TypeScript adaptation) |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/frontend/package.json` | Reference for cookiecutter variable patterns |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/frontend/tsconfig.json` | Reference for TypeScript configuration in template |

---

## Implementation Details

### 1. Directory Structure

Create the following structure:

```
template/{{cookiecutter.project_slug}}/
└── playwright/
    ├── package.json
    ├── tsconfig.json
    ├── .gitignore
    └── tests/
        └── .gitkeep
```

### 2. package.json Specification

```json
{
  "name": "{{ cookiecutter.project_slug }}-playwright",
  "version": "1.0.0",
  "description": "API tests for {{ cookiecutter.project_name }}",
  "type": "module",
  "scripts": {
    "test": "playwright test",
    "test:api": "playwright test --project='API Tests'",
    "test:headed": "playwright test --headed",
    "test:debug": "playwright test --debug",
    "test:ui": "playwright test --ui",
    "report": "playwright show-report"
  },
  "keywords": [
    "playwright",
    "api-testing",
    "{{ cookiecutter.project_slug }}"
  ],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "@playwright/test": "^1.40.0",
    "typescript": "^5.3.0"
  }
}
```

**Key Decisions:**
- `"type": "module"` - Use ES modules for TypeScript compatibility
- TypeScript added as devDependency for `.ts` file support
- Playwright version pinned to ^1.40.0 (supports TypeScript natively)

### 3. tsconfig.json Specification

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "types": ["node"]
  },
  "include": ["tests/**/*.ts", "playwright.config.ts"]
}
```

**Key Decisions:**
- `noEmit: true` - Playwright runs TypeScript directly, no compilation needed
- `moduleResolution: "bundler"` - Modern resolution for ES modules
- Strict mode enabled for type safety

### 4. .gitignore Specification

```gitignore
# Dependencies
node_modules/

# Playwright
/test-results/
/playwright-report/
/blob-report/
/playwright/.cache/

# IDE
.vscode/
.idea/

# Logs
*.log
npm-debug.log*
```

---

## Success Criteria

1. **Directory Structure**: `playwright/` directory exists with correct subdirectories
2. **Package.json Valid**: `npm install` succeeds in the playwright directory of a generated project
3. **TypeScript Support**: `npx tsc --noEmit` passes without errors (after test files are added)
4. **Cookiecutter Variables**: All `{{ cookiecutter.* }}` variables resolve correctly during project generation
5. **Git Ignore**: Playwright artifacts are properly ignored after test execution

---

## Verification Steps

```bash
# Generate a test project
cd /home/ty/workspace/project-starter
cookiecutter template/ --no-input project_name="Test Project" project_slug="test-project"

# Navigate to playwright directory
cd test-project/playwright

# Verify directory structure
ls -la
ls -la tests/

# Verify package.json is valid JSON
cat package.json | python3 -m json.tool

# Install dependencies
npm install

# Verify Playwright is installed
npx playwright --version

# Verify TypeScript is installed
npx tsc --version

# Clean up test project
cd ../..
rm -rf test-project
```

---

## Integration Points

### Downstream Dependencies

This task enables:
- **TASK-02**: Requires package.json to exist for playwright.config.ts
- **TASK-03**: Requires tests/ directory for auth-helper.ts
- **TASK-04**: Requires tests/ directory for test-users.ts
- **TASK-05**: Requires tests/ directory and TypeScript setup for fixtures.ts
- **TASK-10**: Requires playwright/ directory for Makefile targets

### Contracts

This task establishes the following contracts:

**Directory Contract:**
- `playwright/` directory exists at project root
- `playwright/tests/` directory exists for test files
- `playwright/package.json` contains npm scripts for test execution

**Script Contract:**
```bash
# These npm scripts must work after dependencies are installed:
npm test              # Run all tests
npm run test:api      # Run API tests only
npm run test:ui       # Interactive UI mode
npm run test:debug    # Debug mode
npm run report        # Open HTML report
```

---

## Monitoring and Observability

Not applicable for this task (foundation setup).

---

## Infrastructure Needs

None - this task only creates template files.

---

## Notes

1. **TypeScript vs JavaScript**: The reference implementation uses JavaScript (CommonJS), but this implementation uses TypeScript for consistency with the frontend. The key differences:
   - File extension: `.ts` instead of `.js`
   - Module system: ES modules instead of CommonJS
   - Added `tsconfig.json` for TypeScript configuration

2. **Package.json Cookiecutter Variables**: The `{{ cookiecutter.project_slug }}` and `{{ cookiecutter.project_name }}` variables should be used for the package name and description.

3. **Playwright Version**: Using `^1.40.0` which has native TypeScript support. This is newer than the reference implementation's version but more appropriate for TypeScript projects.

---

## FRD References

- FR-1.1: Playwright Directory Location
- FR-1.2: Package Configuration
- FR-1.4: Git Ignore Configuration
- IP-1: Phase 1 - Foundation Setup

---

*Task Created: 2025-12-04*
*Status: Not Started*
