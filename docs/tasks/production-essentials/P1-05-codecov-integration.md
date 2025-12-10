# P1-05: Configure Codecov Integration

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P1-05 |
| **Task Title** | Configure Codecov Integration |
| **Domain** | DevOps |
| **Complexity** | S (Small) |
| **Estimated Effort** | 1 day |
| **Priority** | Should Have |
| **Dependencies** | P1-01 (GitHub Actions CI workflow) |
| **FRD Requirements** | FR-CI-006 |

---

## Scope

### What This Task Includes

1. Create `codecov.yml` configuration file
2. Add Codecov upload step to CI workflow (P1-01)
3. Configure coverage thresholds and targets
4. Set up coverage status checks for PRs
5. Configure coverage badge generation
6. Set up path-based coverage reporting (backend vs frontend)
7. Add cookiecutter conditional integration
8. Document Codecov setup process for users

### What This Task Excludes

- Alternative coverage services (Coveralls, Code Climate)
- Self-hosted Codecov instance configuration
- Paid Codecov features (carryforward flags, etc.)
- Coverage enforcement in pre-commit hooks

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
codecov.yml                       # Codecov configuration (root level)
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    ci.yml                        # Modified to add Codecov upload
{% raw %}{% endif %}{% endraw %}
```

### Files to Modify

```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    ci.yml                        # Add Codecov upload steps
{% raw %}{% endif %}{% endraw %}
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/pyproject.toml` | Coverage configuration for pytest |
| `template/{{cookiecutter.project_slug}}/frontend/vitest.config.ts` | Coverage configuration for vitest |
| `.github/workflows/ci.yml` | Existing CI workflow (from P1-01) |

---

## Technical Specification

### Codecov Configuration File

```yaml
# codecov.yml
codecov:
  require_ci_to_pass: true
  notify:
    wait_for_ci: true

coverage:
  precision: 2
  round: down
  range: "60...100"
  status:
    project:
      default:
        target: auto
        threshold: 1%
        informational: false
      backend:
        paths:
          - "backend/"
        target: 80%
        threshold: 2%
      frontend:
        paths:
          - "frontend/"
        target: 70%
        threshold: 2%
    patch:
      default:
        target: 80%
        threshold: 5%
        informational: false

parsers:
  gcov:
    branch_detection:
      conditional: yes
      loop: yes
      method: no
      macro: no

comment:
  layout: "reach,diff,flags,files"
  behavior: default
  require_changes: true
  require_base: false
  require_head: true

flags:
  backend:
    paths:
      - backend/
    carryforward: false
  frontend:
    paths:
      - frontend/
    carryforward: false
```

### CI Workflow Updates

Add to `.github/workflows/ci.yml` (modifying P1-01 output):

```yaml
  # Add after backend-test job's pytest step
  backend-test:
    # ... existing configuration ...
    steps:
      # ... existing steps ...
      - name: Run pytest
        run: uv run pytest --cov=app --cov-report=xml --cov-report=term
        working-directory: backend

      # NEW: Codecov upload step
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          token: {% raw %}${{ secrets.CODECOV_TOKEN }}{% endraw %}
          files: backend/coverage.xml
          flags: backend
          name: backend-coverage
          fail_ci_if_error: false
          verbose: true

  # Add after frontend-test job's vitest step
  frontend-test:
    # ... existing configuration ...
    steps:
      # ... existing steps ...
      - name: Run vitest
        run: npm run test:coverage
        working-directory: frontend

      # NEW: Codecov upload step
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          token: {% raw %}${{ secrets.CODECOV_TOKEN }}{% endraw %}
          directory: frontend/coverage
          flags: frontend
          name: frontend-coverage
          fail_ci_if_error: false
          verbose: true
```

### Alternative: Separate Coverage Job

For cleaner separation, a dedicated coverage job can be added:

```yaml
  coverage:
    needs: [backend-test, frontend-test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Download backend coverage
        uses: actions/download-artifact@v4
        with:
          name: coverage-backend
          path: backend/

      - name: Download frontend coverage
        uses: actions/download-artifact@v4
        with:
          name: coverage-frontend
          path: frontend/coverage/

      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          token: {% raw %}${{ secrets.CODECOV_TOKEN }}{% endraw %}
          files: backend/coverage.xml
          directory: frontend/coverage
          flags: backend,frontend
          fail_ci_if_error: false
          verbose: true
```

### README Badge

Add to project README.md:

```markdown
[![codecov](https://codecov.io/gh/{{ cookiecutter.github_owner }}/{{ cookiecutter.project_slug }}/graph/badge.svg)](https://codecov.io/gh/{{ cookiecutter.github_owner }}/{{ cookiecutter.project_slug }})
```

Note: This requires adding `github_owner` to cookiecutter.json or using a placeholder.

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Required Artifact |
|---------|-----------------|-------------------|
| P1-01 | Sequential | CI workflow with coverage artifacts |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P1-06 | Documentation | ADR references coverage integration |

### Integration with P1-01

This task modifies the CI workflow created in P1-01:
- Adds Codecov upload steps to backend-test and frontend-test jobs
- Uses coverage artifacts already being generated
- Requires `CODECOV_TOKEN` secret to be documented

---

## Success Criteria

### Functional Requirements

- [ ] `codecov.yml` file exists at project root
- [ ] CI workflow uploads backend coverage to Codecov
- [ ] CI workflow uploads frontend coverage to Codecov
- [ ] Coverage status checks appear on PRs
- [ ] Coverage badge can be generated
- [ ] Backend coverage target: 80%
- [ ] Frontend coverage target: 70%
- [ ] Patch coverage target: 80%
- [ ] Coverage flags separate backend/frontend

### Non-Functional Requirements

- [ ] Codecov action uses v4 (latest stable)
- [ ] Token passed via secrets (not hardcoded)
- [ ] Configuration follows Codecov best practices
- [ ] Documentation explains setup process
- [ ] Upload failure does not fail CI (`fail_ci_if_error: false`)

### Validation Steps

1. Generate project with `include_github_actions: yes`
   - Verify `codecov.yml` exists
   - Verify CI workflow has Codecov upload steps
2. Push to GitHub with Codecov integration enabled
   - Verify coverage uploads successfully
   - Verify PR status checks appear
   - Verify coverage badge works
3. Generate project with `include_github_actions: no`
   - Verify `codecov.yml` still exists (can be used with other CI)
   - Verify no GitHub-specific configurations fail

---

## Integration Points

### Coverage Report Formats

| Component | Tool | Output Format | Location |
|-----------|------|---------------|----------|
| Backend | pytest-cov | Cobertura XML | `backend/coverage.xml` |
| Frontend | vitest | lcov/cobertura | `frontend/coverage/` |

### GitHub Integration

Codecov provides:
- PR comments with coverage diff
- Status checks for coverage thresholds
- Coverage graphs in repository
- Badge generation

### Required Secrets

```yaml
secrets:
  CODECOV_TOKEN:
    description: "Codecov upload token from codecov.io"
    required: true  # For private repos
    note: "Optional for public repos, but recommended"
```

Documentation should explain:
1. How to get Codecov token from codecov.io
2. How to add token to GitHub repository secrets
3. That public repos can work without token (but rate-limited)

---

## Monitoring and Observability

### Codecov Dashboard

Codecov provides:
- Coverage trends over time
- Component-level coverage breakdown
- Commit-by-commit coverage changes
- Pull request coverage impact

### Alerts

Configure in Codecov UI:
- Coverage drop notifications
- Uncovered critical paths
- Long-running coverage decreases

---

## Infrastructure Needs

### External Services

| Service | Account Type | Cost |
|---------|--------------|------|
| Codecov | Free (OSS) / Team | Free for public repos |

### Secrets Configuration

| Secret Name | Source | Required |
|-------------|--------|----------|
| `CODECOV_TOKEN` | Codecov dashboard | Yes (recommended) |

### Repository Settings

- Codecov GitHub App installed (recommended)
- Repository enabled in Codecov dashboard

---

## Implementation Notes

### Token Requirement

As of 2024, Codecov requires tokens for:
- Private repositories (always)
- Public repositories (recommended, prevents rate limiting)

The template assumes users will:
1. Sign up for Codecov (free for public repos)
2. Add repository to Codecov
3. Copy upload token
4. Add as GitHub secret

### Coverage Threshold Strategy

| Component | Target | Rationale |
|-----------|--------|-----------|
| Backend | 80% | Backend code is more critical and testable |
| Frontend | 70% | UI components harder to unit test |
| Patch | 80% | New code should be well-tested |
| Threshold | 2% | Allow minor fluctuations |

### Fail Behavior

`fail_ci_if_error: false` because:
- Codecov outages should not block deployments
- Coverage is informational, not blocking
- Branch protection rules can enforce coverage separately

If stricter enforcement is desired, users can:
1. Set `fail_ci_if_error: true`
2. Use GitHub branch protection with Codecov status checks

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-CI-006 | Generate and upload test coverage reports | Codecov integration |

### Related Tasks

- P1-01: CI workflow provides coverage artifacts
- P1-06: ADR documents coverage integration decisions

### Related ADRs

- ADR-017: Optional Observability Stack (pattern reference)
- ADR-019: GitHub Actions CI/CD (to be written, will include coverage section)

### External Resources

- [Codecov Documentation](https://docs.codecov.com/)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)
- [Codecov YAML Reference](https://docs.codecov.com/docs/codecov-yaml)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Vitest Coverage](https://vitest.dev/guide/coverage.html)
