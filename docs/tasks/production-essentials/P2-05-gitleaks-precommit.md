# P2-05: Configure Gitleaks Pre-commit Hook

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P2-05 |
| **Task Title** | Configure Gitleaks Pre-commit Hook |
| **Domain** | DevOps |
| **Complexity** | S (Small) |
| **Estimated Effort** | 1 day |
| **Priority** | Must Have |
| **Dependencies** | None |
| **FRD Requirements** | FR-SEC-011, FR-SEC-012 |

---

## Scope

### What This Task Includes

1. Create `.pre-commit-config.yaml` with gitleaks hook configuration
2. Create `.gitleaks.toml` configuration file for custom rules and allowlists
3. Add gitleaks CI job to security workflow for server-side validation
4. Create `.secrets.baseline` file structure for managing exceptions
5. Document false positive handling procedures
6. Add pre-commit to backend dev dependencies

### What This Task Excludes

- Other pre-commit hooks (formatting, linting) - can be added later
- Credential rotation procedures (operational documentation)
- Integration with secrets management (Vault, AWS SM) - deployment concern
- Audit logging of secret detection events

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
.pre-commit-config.yaml           # Pre-commit hook configuration
.gitleaks.toml                    # Gitleaks configuration and allowlists
docs/
  development/
    secrets-management.md         # Documentation for handling secrets

{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    security.yml                  # Add gitleaks CI job (extends P2-03/P2-04)
{% raw %}{% endif %}{% endraw %}
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/.env.example` | Understand existing env var patterns |
| `template/{{cookiecutter.project_slug}}/backend/pyproject.toml` | Add pre-commit as dev dependency |
| `template/{{cookiecutter.project_slug}}/.github/workflows/security.yml` | Extend with gitleaks job |

---

## Technical Specification

### Pre-commit Configuration

Create `.pre-commit-config.yaml`:

```yaml
# .pre-commit-config.yaml
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks

repos:
  # Gitleaks - Secret detection
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4  # Use latest stable version
    hooks:
      - id: gitleaks
        name: Detect secrets with gitleaks
        description: Detect hardcoded secrets in git repository
        entry: gitleaks protect --staged --verbose
        language: golang
        pass_filenames: false

  # Optional: Additional security hooks
  # - repo: https://github.com/pre-commit/pre-commit-hooks
  #   rev: v4.5.0
  #   hooks:
  #     - id: detect-private-key
  #       name: Detect private keys
  #     - id: detect-aws-credentials
  #       name: Detect AWS credentials

# CI configuration
ci:
  autofix_prs: false  # Don't auto-fix, secrets require manual review
  autoupdate_schedule: monthly
```

### Gitleaks Configuration

Create `.gitleaks.toml`:

```toml
# .gitleaks.toml
# Gitleaks configuration for secret detection
# See: https://github.com/gitleaks/gitleaks#configuration

title = "{{ cookiecutter.project_name }} Gitleaks Configuration"

# Extend the default ruleset
[extend]
useDefault = true

# Custom rules can be added here
# [[rules]]
# id = "custom-api-key"
# description = "Custom API key pattern"
# regex = '''(?i)custom[_-]?api[_-]?key['":\s]*[=:]\s*['"]?([a-z0-9]{32,})['"]?'''
# secretGroup = 1

# Allowlist - files and patterns that should be ignored
[allowlist]
description = "Allowlisted files and patterns"

# Files to ignore completely
paths = [
    # Test fixtures with example/dummy secrets
    '''.*test.*fixture.*''',
    '''.*tests.*mock.*''',
    # Lock files (contain hashes, not secrets)
    '''uv\.lock''',
    '''package-lock\.json''',
    '''poetry\.lock''',
    # Documentation examples
    '''.*\.md''',
    # Environment example files (contain placeholders, not real secrets)
    '''\.env\.example''',
    '''\.env\.sample''',
    '''\.env\.template''',
]

# Specific commits to ignore (historical commits with cleaned secrets)
commits = [
    # Add commit SHAs here after cleaning historical secrets
    # "abc123def456..."
]

# Regex patterns to ignore (false positives)
regexes = [
    # Example placeholder values
    '''your[_-]?(api[_-]?)?key[_-]?here''',
    '''<your[_-]?.*>''',
    '''CHANGE[_-]?ME''',
    '''xxx+''',
    # Base64 encoded example strings
    '''ZXhhbXBsZQ==''',  # "example" in base64
    # Common test/example values
    '''test[_-]?secret''',
    '''example[_-]?password''',
    '''dummy[_-]?token''',
]

# Stopwords - strings that indicate a value is not a secret
stopwords = [
    "example",
    "sample",
    "placeholder",
    "changeme",
    "your-",
    "xxx",
    "test",
    "dummy",
    "fake",
    "mock",
]
```

### CI Job for Server-Side Validation

Add to existing `security.yml` workflow:

```yaml
  gitleaks-scan:
    name: Secret Detection (Gitleaks)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for scanning all commits

      - name: Run gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}
          GITLEAKS_LICENSE: {% raw %}${{ secrets.GITLEAKS_LICENSE }}{% endraw %}  # Optional, for enterprise features

      # Alternative: Run gitleaks directly without action
      # - name: Install gitleaks
      #   run: |
      #     wget -O gitleaks.tar.gz https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_x64.tar.gz
      #     tar -xzf gitleaks.tar.gz
      #     chmod +x gitleaks
      #
      # - name: Run gitleaks
      #   run: ./gitleaks detect --source . --verbose --redact

      - name: Upload gitleaks report
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: gitleaks-report
          path: results.sarif
          retention-days: 30
```

### Backend Dev Dependency Update

Add to `backend/pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    # ... existing dev dependencies ...
    "pre-commit>=3.5.0",
]
```

### Documentation: Secrets Management

Create `docs/development/secrets-management.md`:

```markdown
# Secrets Management Guide

This document describes how to handle secrets and sensitive data in {{ cookiecutter.project_name }}.

## Pre-commit Hook

This project uses [gitleaks](https://github.com/gitleaks/gitleaks) to detect secrets before they are committed.

### Setup

1. Install pre-commit:
   ```bash
   pip install pre-commit
   # or
   uv add --dev pre-commit
   ```

2. Install the hooks:
   ```bash
   pre-commit install
   ```

3. Test the setup:
   ```bash
   pre-commit run --all-files
   ```

### What Gets Detected

Gitleaks detects:
- API keys (AWS, GCP, Azure, etc.)
- Private keys (RSA, DSA, EC, etc.)
- Database connection strings with passwords
- JWT tokens and secrets
- OAuth client secrets
- Generic high-entropy strings that look like secrets

### Handling False Positives

If gitleaks flags a legitimate non-secret (e.g., a test fixture):

1. **Verify it's not a real secret** - double-check the flagged content
2. **Add to allowlist** - edit `.gitleaks.toml`:
   ```toml
   [allowlist]
   paths = [
       '''path/to/file\.txt''',
   ]
   ```
3. **Use stopwords** - if the value contains indicator words
4. **Commit the allowlist change** - include justification in commit message

### If You Accidentally Commit a Secret

1. **Do NOT push** - if you haven't pushed yet, amend the commit
2. **Rotate the secret immediately** - assume it's compromised
3. **Remove from history** - use `git filter-branch` or BFG Repo-Cleaner
4. **Force push** - after cleaning history (coordinate with team)
5. **Document the incident** - follow security incident procedures

### Environment Variables

Use environment variables for all secrets:

```bash
# Never commit real values
DATABASE_URL=postgresql://user:password@localhost/db  # Bad!

# Use environment variables
DATABASE_URL=${DATABASE_URL}  # Good
```

See `.env.example` for the template of required environment variables.

## CI/CD Secrets

Store secrets in GitHub repository settings:
- Settings > Secrets and variables > Actions

Required secrets for deployment:
- `REGISTRY_TOKEN` - Container registry authentication
- `KUBECONFIG` - Kubernetes deployment credentials
- `SENTRY_DSN` - Error tracking (if using Sentry)

## Related Documentation

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [gitleaks Documentation](https://github.com/gitleaks/gitleaks)
```

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| None | - | This is an independent foundational task |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-06 | Reference | Security checklist references secret detection |
| P6-01 | Reference | CLAUDE.md update includes pre-commit setup |

---

## Success Criteria

### Functional Requirements

- [ ] `.pre-commit-config.yaml` created with gitleaks hook
- [ ] `.gitleaks.toml` created with project-specific configuration
- [ ] Pre-commit hook detects test secrets (validation test)
- [ ] Pre-commit hook allows commits without secrets
- [ ] CI job runs gitleaks on all commits
- [ ] CI job fails when secrets are detected
- [ ] False positive handling documented
- [ ] Allowlist mechanisms work correctly
- [ ] pre-commit added to backend dev dependencies

### Non-Functional Requirements

- [ ] Pre-commit hook runs in under 5 seconds for typical commits
- [ ] CI scan completes in under 2 minutes for full repository
- [ ] Documentation is clear and actionable
- [ ] Configuration follows gitleaks best practices

### Validation Steps

1. Test secret detection locally:
   ```bash
   # Install pre-commit
   pre-commit install

   # Create test file with fake secret
   echo 'aws_secret_access_key = "AKIAIOSFODNN7EXAMPLE"' > test-secret.txt
   git add test-secret.txt

   # Attempt commit (should fail)
   git commit -m "test"

   # Clean up
   rm test-secret.txt
   ```

2. Test allowlist functionality:
   - Add pattern to `.gitleaks.toml` allowlist
   - Verify previously-flagged content is now allowed

3. Test CI integration:
   - Push commit with secret to branch (not main)
   - Verify CI job fails
   - Verify report artifact is uploaded

4. Test clean repository:
   - Run `gitleaks detect --source . --verbose`
   - Verify no secrets found in existing codebase

---

## Integration Points

### Pre-commit Workflow

```
Developer commits code
        |
        v
Pre-commit runs gitleaks
        |
    +---+---+
    |       |
 Secrets  No secrets
 found    found
    |       |
    v       v
 BLOCKED  ALLOWED
 (fix     (commit
 required) proceeds)
```

### CI Workflow Integration

The gitleaks CI job complements the pre-commit hook:

| Layer | Tool | Purpose |
|-------|------|---------|
| Local | pre-commit + gitleaks | Prevent secrets before commit |
| CI | gitleaks-action | Catch bypassed hooks, scan history |
| Scheduled | gitleaks CI job | Detect secrets in old commits |

### Security Workflow Structure

Complete security.yml after P2-03, P2-04, and P2-05:

```yaml
name: Security

jobs:
  # P2-03: Container scanning
  trivy-image-scan: ...
  trivy-filesystem-scan: ...

  # P2-04: Dependency scanning
  python-dependency-scan: ...
  npm-dependency-scan: ...

  # P2-05: Secret detection
  gitleaks-scan: ...
```

---

## Monitoring and Observability

### Pre-commit Metrics

Track locally via:
- Pre-commit hook execution logs
- Developer feedback on false positives

### CI Metrics

| Metric | Source | Purpose |
|--------|--------|---------|
| Secrets detected | CI job output | Track security incidents |
| Scan duration | Workflow timing | Performance monitoring |
| False positive rate | Allowlist additions | Configuration tuning |

### Alerting

1. **CI job failure** - Immediate attention required
2. **Secret in main branch** - Security incident, rotate immediately
3. **Excessive allowlist entries** - Review configuration

---

## Infrastructure Needs

### Local Development

Requirements:
- Python 3.8+ (for pre-commit)
- Git 2.9+ (for pre-commit hooks)
- Network access to download gitleaks binary

### CI/CD

Requirements:
- GitHub Actions enabled
- Full git history access (`fetch-depth: 0`)
- Optional: GITLEAKS_LICENSE for enterprise features

### No Additional Secrets Required

Gitleaks works without authentication for open-source use.

---

## Implementation Notes

### Gitleaks vs detect-secrets

| Feature | gitleaks | detect-secrets |
|---------|----------|----------------|
| Language | Go (fast) | Python |
| Git integration | Native | Via hook |
| Custom rules | TOML config | Plugin-based |
| CI action | Official action | Manual setup |
| Maintenance | Active | Active |

Recommendation: **gitleaks** for speed and native Git integration.

### Pre-commit Installation Options

```bash
# Via pip
pip install pre-commit

# Via uv
uv add --dev pre-commit

# Via homebrew (macOS)
brew install pre-commit

# Via pipx (isolated)
pipx install pre-commit
```

### Scanning Modes

| Mode | Command | Use Case |
|------|---------|----------|
| protect | `gitleaks protect` | Pre-commit hook (staged files only) |
| detect | `gitleaks detect` | CI/full repository scan |

### Historical Secret Handling

If secrets exist in git history:

```bash
# Scan history for secrets
gitleaks detect --source . --verbose --report-path=leaks.json

# Use BFG to clean history (example)
bfg --delete-files '*.pem'
bfg --replace-text passwords.txt

# Force push cleaned history
git push --force
```

**Warning:** Force-pushing rewrites history. Coordinate with team.

### .gitattributes Integration

Consider adding for large repositories:

```
# .gitattributes
*.lock linguist-generated=true
*.lock -diff
```

This helps gitleaks skip lock files by default.

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-SEC-011 | Pre-commit shall include secret detection using gitleaks | `.pre-commit-config.yaml` with gitleaks hook |
| FR-SEC-012 | CI shall validate no secrets in codebase | `gitleaks-scan` job in security.yml |

### Related ADRs

- ADR-019: GitHub Actions CI/CD (workflow patterns)
- ADR-022: Container Security Scanning (related security workflow)

### External Resources

- [gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [gitleaks Configuration](https://github.com/gitleaks/gitleaks#configuration)
- [gitleaks GitHub Action](https://github.com/gitleaks/gitleaks-action)
- [pre-commit Documentation](https://pre-commit.com/)
- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
