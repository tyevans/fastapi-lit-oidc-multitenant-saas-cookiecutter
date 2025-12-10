# P1-04: Configure Dependabot

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P1-04 |
| **Task Title** | Configure Dependabot |
| **Domain** | DevOps |
| **Complexity** | XS (Extra Small) |
| **Estimated Effort** | 0.5 days |
| **Priority** | Should Have |
| **Dependencies** | None |
| **FRD Requirements** | Implicit (dependency management best practice) |

---

## Scope

### What This Task Includes

1. Create `.github/dependabot.yml` configuration file
2. Configure automated dependency updates for Python (pip/uv ecosystem)
3. Configure automated dependency updates for npm (frontend)
4. Configure automated updates for GitHub Actions
5. Set appropriate update schedules and limits
6. Configure grouping for related dependencies
7. Add cookiecutter conditional integration with `include_github_actions`
8. Document Dependabot configuration in project README or docs

### What This Task Excludes

- Security vulnerability scanning (covered by P2-03, P2-04)
- Automated merging of PRs (requires separate auto-merge workflow)
- Renovate or alternative dependency management tools
- Private registry configuration (out of scope for template)

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  dependabot.yml                # Dependabot configuration
{% raw %}{% endif %}{% endraw %}
```

### Files to Modify

None - this is an additive task. The `.github/` directory conditional is established in P1-01.

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/pyproject.toml` | Python dependencies to track |
| `template/{{cookiecutter.project_slug}}/frontend/package.json` | npm dependencies to track |
| `.github/workflows/ci.yml` | GitHub Actions to track (from P1-01) |
| `template/cookiecutter.json` | Existing cookiecutter variables |

---

## Technical Specification

### Dependabot Configuration

```yaml
# .github/dependabot.yml
version: 2
updates:
  # Python dependencies (backend)
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "06:00"
      timezone: "UTC"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "deps(backend)"
    labels:
      - "dependencies"
      - "backend"
    groups:
      # Group minor/patch updates for core frameworks
      fastapi-ecosystem:
        patterns:
          - "fastapi*"
          - "starlette*"
          - "pydantic*"
          - "uvicorn*"
      testing:
        patterns:
          - "pytest*"
          - "coverage*"
          - "httpx*"
      linting:
        patterns:
          - "ruff*"
          - "mypy*"

  # npm dependencies (frontend)
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "06:00"
      timezone: "UTC"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "deps(frontend)"
    labels:
      - "dependencies"
      - "frontend"
    groups:
      lit-ecosystem:
        patterns:
          - "lit*"
          - "@lit/*"
      testing:
        patterns:
          - "vitest*"
          - "@vitest/*"
          - "playwright*"
          - "@playwright/*"
      build-tools:
        patterns:
          - "vite*"
          - "typescript*"
          - "eslint*"
          - "@typescript-eslint/*"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "06:00"
      timezone: "UTC"
    open-pull-requests-limit: 3
    commit-message:
      prefix: "ci"
    labels:
      - "dependencies"
      - "ci"
    groups:
      github-actions:
        patterns:
          - "*"
```

### Configuration Rationale

| Setting | Value | Rationale |
|---------|-------|-----------|
| `interval` | weekly | Balance between staying updated and PR noise |
| `day` | monday | Start of work week for review |
| `time` | 06:00 UTC | PRs ready for morning review in most timezones |
| `open-pull-requests-limit` | 5 (pip/npm), 3 (actions) | Prevent overwhelming with too many PRs |
| `groups` | By ecosystem | Reduce PR count by grouping related updates |
| `commit-message.prefix` | deps(backend), deps(frontend), ci | Conventional commit format |
| `labels` | dependencies + component | Easy filtering and automation |

### Grouping Strategy

Dependency grouping reduces the number of PRs while maintaining logical separation:

1. **Framework Groups**: Core framework components updated together (e.g., FastAPI + Starlette + Pydantic)
2. **Testing Groups**: Test libraries updated together (pytest plugins, coverage tools)
3. **Build Tool Groups**: Dev tooling updated together (linters, formatters, bundlers)
4. **GitHub Actions**: All action updates grouped (typically non-breaking)

---

## Dependencies

### Upstream Dependencies

None - this is an independent task.

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-04 | Related | Dependabot complements CI-based vulnerability scanning |

### Integration with P1-01

This task adds a file to the `.github/` directory structure established in P1-01. The cookiecutter conditional `include_github_actions` applies to the entire `.github/` directory, so no additional conditional logic is needed for `dependabot.yml`.

---

## Success Criteria

### Functional Requirements

- [ ] `dependabot.yml` file exists in `.github/` directory
- [ ] Python dependencies tracked with weekly schedule
- [ ] npm dependencies tracked with weekly schedule
- [ ] GitHub Actions tracked with weekly schedule
- [ ] PR limits configured to prevent overwhelming
- [ ] Dependency groups reduce number of PRs for common packages
- [ ] Commit messages follow conventional commit format
- [ ] Labels applied for filtering and automation

### Non-Functional Requirements

- [ ] Configuration follows Dependabot best practices
- [ ] Documentation explains how to customize the configuration
- [ ] Grouping patterns cover major dependencies in template

### Validation Steps

1. Generate project with `include_github_actions: yes`
   - Verify `.github/dependabot.yml` exists
   - Verify YAML syntax is valid
2. Generate project with `include_github_actions: no`
   - Verify `.github/` directory does not exist
3. Push generated project to GitHub
   - Verify Dependabot recognizes configuration
   - Verify initial security/dependency scan runs

---

## Integration Points

### GitHub Integration

Dependabot is a GitHub-native feature that:
- Automatically creates PRs for dependency updates
- Integrates with repository security advisories
- Respects branch protection rules
- Works with CI status checks

### CI Workflow Integration

Dependabot PRs trigger the CI workflow (P1-01):
- Tests run automatically on Dependabot PRs
- Failed tests block merge
- Coverage reports generated for review

### Label-Based Automation

The configured labels enable automation:
- `dependencies` - General dependency filter
- `backend`/`frontend`/`ci` - Component-specific filtering
- Can be used with auto-merge workflows (future enhancement)

---

## Monitoring and Observability

### Dependabot Alerts

GitHub provides Dependabot alerts for:
- Security vulnerabilities in dependencies
- New dependency updates available
- Configuration issues

### Metrics to Track

- Number of open Dependabot PRs
- Time to merge dependency updates
- Failed CI runs on Dependabot PRs

### Recommended Repository Settings

Enable in GitHub repository settings:
- Dependabot alerts: On
- Dependabot security updates: On
- Dependency graph: On

---

## Infrastructure Needs

### GitHub Requirements

- Repository hosted on GitHub
- GitHub Actions enabled
- Dependabot enabled in repository settings

### No Secrets Required

Dependabot uses GitHub's built-in authentication for public registries (PyPI, npm, GitHub Actions).

---

## Implementation Notes

### Python Ecosystem Note

Dependabot uses `pip` ecosystem for Python, which works with:
- `requirements.txt`
- `pyproject.toml`
- `setup.py`
- `uv.lock` (via pip ecosystem)

The template uses `uv` for package management, but Dependabot's `pip` ecosystem correctly parses `pyproject.toml` for dependency updates.

### Directory Paths

The `directory` field specifies where to find the dependency manifest:
- `/backend` for Python (`pyproject.toml`)
- `/frontend` for npm (`package.json`)
- `/` for GitHub Actions (`.github/workflows/`)

### Merge Conflict Handling

Dependabot automatically rebases PRs when:
- Target branch is updated
- Other Dependabot PRs are merged

---

## References

### FRD Requirements Mapping

This task implements implicit dependency management best practice. While not explicitly listed as a requirement, it supports:

| Requirement ID | Description | How This Task Supports |
|----------------|-------------|------------------------|
| NFR-003 | No HIGH/CRITICAL vulnerabilities | Keeps dependencies updated |
| NFR-005 | Follow existing patterns | Matches GitHub-first approach |

### Related ADRs

- ADR-017: Optional Observability Stack (pattern for cookiecutter conditionals)
- ADR-019: GitHub Actions CI/CD (to be written in P1-06, will reference this configuration)

### External Resources

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Dependabot Configuration Options](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [Dependency Grouping](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file#groups)
