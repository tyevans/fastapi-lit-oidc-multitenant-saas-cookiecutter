# P1-01: Create GitHub Actions CI Workflow

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P1-01 |
| **Task Title** | Create GitHub Actions CI Workflow |
| **Domain** | DevOps |
| **Complexity** | M (Medium) |
| **Estimated Effort** | 3 days |
| **Priority** | Must Have |
| **Dependencies** | None |
| **FRD Requirements** | FR-CI-001, FR-CI-002, FR-CI-003, FR-CI-004, FR-CI-005 |

---

## Scope

### What This Task Includes

1. Create `.github/workflows/ci.yml` workflow file
2. Implement backend lint job (ruff check)
3. Implement backend test job (pytest with coverage)
4. Implement frontend lint job (eslint)
5. Implement frontend test job (vitest)
6. Configure GitHub Actions service containers (PostgreSQL, Redis)
7. Configure dependency caching (uv for Python, npm for Node.js)
8. Add cookiecutter conditional for `include_github_actions`
9. Configure matrix testing for cookiecutter option combinations

### What This Task Excludes

- Container build workflow (P1-02)
- Deployment workflows (P4-04)
- Security scanning jobs (P2-03, P2-04)
- Coverage reporting integration with Codecov (P1-05)

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    ci.yml                    # Primary CI workflow
{% raw %}{% endif %}{% endraw %}
```

### Files to Modify

```
template/cookiecutter.json    # Add include_github_actions variable
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/pyproject.toml` | Python version, test/lint commands, dependencies |
| `template/{{cookiecutter.project_slug}}/frontend/package.json` | Node version, test/lint scripts |
| `template/{{cookiecutter.project_slug}}/.env.example` | Required environment variables |
| `template/{{cookiecutter.project_slug}}/compose.yml` | Service configuration patterns |
| `template/cookiecutter.json` | Existing cookiecutter variables |

---

## Technical Specification

### Workflow Structure

```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

concurrency:
  group: {% raw %}${{ github.workflow }}-${{ github.ref }}{% endraw %}
  cancel-in-progress: true

jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - name: Install dependencies
        run: uv sync --dev
        working-directory: backend
      - name: Run ruff check
        run: uv run ruff check .
        working-directory: backend
      - name: Run ruff format check
        run: uv run ruff format --check .
        working-directory: backend

  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:{{ cookiecutter.postgres_version }}-alpine
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:{{ cookiecutter.redis_version }}-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    env:
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
      REDIS_URL: redis://localhost:6379/0
      JWT_ALGORITHM: RS256
      JWKS_URL: http://localhost:8080/realms/test/protocol/openid-connect/certs
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"
      - name: Install dependencies
        run: uv sync --dev
        working-directory: backend
      - name: Run pytest
        run: uv run pytest --cov=app --cov-report=xml --cov-report=term
        working-directory: backend
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-backend
          path: backend/coverage.xml

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: Install dependencies
        run: npm ci
        working-directory: frontend
      - name: Run eslint
        run: npm run lint
        working-directory: frontend

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: Install dependencies
        run: npm ci
        working-directory: frontend
      - name: Run vitest
        run: npm run test:coverage
        working-directory: frontend
      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-frontend
          path: frontend/coverage/
```

### Cookiecutter Variable Addition

Add to `template/cookiecutter.json`:

```json
{
  "include_github_actions": ["yes", "no"]
}
```

Default should be `"yes"` (first item in list).

### Jinja2 Directory Conditional

The `.github/` directory should be conditionally rendered. This requires special handling in cookiecutter post-generation hooks.

**Option 1: Post-generation hook (recommended)**

Create `hooks/post_gen_project.py`:

```python
import os
import shutil

if "{{ cookiecutter.include_github_actions }}" != "yes":
    shutil.rmtree(".github", ignore_errors=True)
```

**Option 2: Inline conditional in workflow file**

If directory-level conditionals are not feasible, add workflow-level check:

```yaml
name: CI
on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

{% raw %}{% if cookiecutter.include_github_actions != "yes" %}{% endraw %}
# GitHub Actions disabled via cookiecutter
{% raw %}{% else %}{% endraw %}
jobs:
  # ... workflow content
{% raw %}{% endif %}{% endraw %}
```

---

## Dependencies

### Upstream Dependencies

None - this is a foundational task.

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P1-02 | Sequential | Build workflow triggers after CI passes |
| P1-05 | Parallel | Codecov integration adds to coverage step |
| P1-06 | Documentation | ADR references this workflow |
| P2-03 | Extension | Trivy job added to this workflow |
| P2-04 | Extension | pip-audit/npm audit jobs added |

---

## Success Criteria

### Functional Requirements

- [ ] CI workflow triggers on PR to main/develop branches
- [ ] CI workflow triggers on push to main branch
- [ ] Backend lint job (ruff check) executes and fails on violations
- [ ] Backend format check (ruff format --check) executes and fails on violations
- [ ] Backend test job (pytest) executes with coverage reporting
- [ ] Frontend lint job (eslint) executes and fails on violations
- [ ] Frontend test job (vitest) executes with coverage reporting
- [ ] PostgreSQL service container available for backend tests
- [ ] Redis service container available for backend tests
- [ ] All jobs complete in under 10 minutes total

### Non-Functional Requirements

- [ ] Workflow uses concurrency groups to cancel redundant runs
- [ ] Dependencies are cached (uv for Python, npm for Node.js)
- [ ] Coverage artifacts are uploaded for downstream processing
- [ ] Workflow file follows GitHub Actions best practices
- [ ] Cookiecutter conditional properly excludes `.github/` when disabled

### Validation Steps

1. Generate project with `include_github_actions: yes`
   - Verify `.github/workflows/ci.yml` exists
   - Verify workflow syntax is valid: `act -n` or GitHub Actions linter
2. Generate project with `include_github_actions: no`
   - Verify `.github/` directory does not exist
3. Push test PR to generated project
   - Verify all jobs trigger and pass
   - Verify coverage artifacts are uploaded

---

## Integration Points

### Service Container Configuration

The workflow requires service containers matching the development environment:

| Service | Image | Health Check |
|---------|-------|--------------|
| PostgreSQL | `postgres:{{ cookiecutter.postgres_version }}-alpine` | `pg_isready` |
| Redis | `redis:{{ cookiecutter.redis_version }}-alpine` | `redis-cli ping` |

### Environment Variables

Backend tests require:

```yaml
DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
REDIS_URL: redis://localhost:6379/0
JWT_ALGORITHM: RS256
JWKS_URL: http://localhost:8080/realms/test/protocol/openid-connect/certs
```

**Note:** JWKS_URL points to a non-existent Keycloak instance. Tests should mock JWT validation or this URL should be configurable.

### Caching Strategy

| Cache Type | Key | Restore Keys |
|------------|-----|--------------|
| uv | `uv-${{ runner.os }}-${{ hashFiles('backend/uv.lock') }}` | `uv-${{ runner.os }}-` |
| npm | Built-in via `actions/setup-node` cache option | - |

---

## Monitoring and Observability

### Workflow Metrics

GitHub Actions provides built-in metrics:

- Workflow run duration
- Job success/failure rate
- Billable minutes consumed

### Recommended Alerts

Configure GitHub repository settings:

- Require status checks to pass before merging
- Enable branch protection on main/develop

---

## Infrastructure Needs

### GitHub Actions Requirements

- Repository must be on GitHub
- Actions must be enabled in repository settings
- Service containers require Linux runners (ubuntu-latest)

### Secrets (None Required for CI)

This workflow does not require secrets. Build workflow (P1-02) will add registry authentication.

---

## Implementation Notes

### Python Version

The workflow uses Python {{ cookiecutter.python_version }}. Ensure `setup-uv` action supports this version.

### Node.js Version

The workflow uses Node.js 20 (LTS). This aligns with frontend development dependencies.

### Parallelization

All four jobs (backend-lint, backend-test, frontend-lint, frontend-test) can run in parallel, reducing total CI time.

### Test Isolation

Backend tests run with a fresh PostgreSQL instance per workflow run, ensuring test isolation.

### Coverage Output

- Backend: `coverage.xml` (Cobertura format)
- Frontend: `coverage/` directory (Vitest format)

These are uploaded as artifacts for P1-05 (Codecov integration).

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-CI-001 | CI triggers on PR to main/develop | `on.pull_request.branches` |
| FR-CI-002 | Backend pytest suite runs | `backend-test` job |
| FR-CI-003 | Frontend vitest suite runs | `frontend-test` job |
| FR-CI-004 | Ruff linter runs on backend | `backend-lint` job |
| FR-CI-005 | ESLint runs on frontend | `frontend-lint` job |

### Related ADRs

- ADR-017: Optional Observability Stack (pattern for cookiecutter conditionals)
- ADR-019: GitHub Actions CI/CD (to be written in P1-06)

### External Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [astral-sh/setup-uv Action](https://github.com/astral-sh/setup-uv)
- [actions/setup-node Action](https://github.com/actions/setup-node)
