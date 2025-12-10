# P2-04: Add Dependency Vulnerability Scanning

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P2-04 |
| **Task Title** | Add Dependency Vulnerability Scanning |
| **Domain** | DevOps |
| **Complexity** | S (Small) |
| **Estimated Effort** | 1 day |
| **Priority** | Must Have |
| **Dependencies** | P1-01 (CI workflow exists) |
| **FRD Requirements** | FR-SEC-008, FR-SEC-009, FR-SEC-010 |

---

## Scope

### What This Task Includes

1. Add pip-audit job to security workflow for Python dependency scanning
2. Add npm audit job to security workflow for Node.js dependency scanning
3. Configure severity thresholds (fail on HIGH/CRITICAL vulnerabilities)
4. Generate machine-readable output for tracking and reporting
5. Upload scan results as workflow artifacts
6. Configure SARIF output for GitHub Security tab integration (where supported)

### What This Task Excludes

- Container image scanning (P2-03) - already documented
- Filesystem/IaC scanning (handled by Trivy in P2-03)
- SBOM generation (P1-02 build workflow)
- Pre-commit secret detection (P2-05)
- Automatic dependency updates (P1-04 Dependabot)

---

## Relevant Code Areas

### Files to Modify

```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    security.yml              # Add dependency scanning jobs (extends P2-03)
{% raw %}{% endif %}{% endraw %}
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/.github/workflows/security.yml` | Security workflow created in P2-03 |
| `template/{{cookiecutter.project_slug}}/backend/pyproject.toml` | Python dependencies to scan |
| `template/{{cookiecutter.project_slug}}/backend/uv.lock` | Locked Python dependencies |
| `template/{{cookiecutter.project_slug}}/frontend/package.json` | Node.js dependencies to scan |
| `template/{{cookiecutter.project_slug}}/frontend/package-lock.json` | Locked Node.js dependencies |

---

## Technical Specification

### Security Workflow Extension

Add these jobs to the existing `security.yml` workflow (created in P2-03):

```yaml
# Add to existing security.yml from P2-03

  python-dependency-scan:
    name: Python Dependency Audit
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '{{ cookiecutter.python_version }}'

      - name: Install pip-audit
        run: pip install pip-audit

      - name: Run pip-audit
        id: pip-audit
        run: |
          # Audit production dependencies from pyproject.toml
          pip-audit \
            --requirement <(uv pip compile pyproject.toml -o -) \
            --format json \
            --output pip-audit-results.json \
            --desc on \
            --progress-spinner off \
            || true

          # Check for HIGH/CRITICAL vulnerabilities
          pip-audit \
            --requirement <(uv pip compile pyproject.toml -o -) \
            --strict \
            --desc on \
            --progress-spinner off

      - name: Upload pip-audit results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: pip-audit-results
          path: backend/pip-audit-results.json
          retention-days: 30

      - name: Generate human-readable report
        if: always()
        run: |
          pip-audit \
            --requirement <(uv pip compile pyproject.toml -o -) \
            --desc on \
            --progress-spinner off \
            > pip-audit-report.txt 2>&1 || true

      - name: Upload human-readable report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: pip-audit-report
          path: backend/pip-audit-report.txt
          retention-days: 30

  npm-dependency-scan:
    name: NPM Dependency Audit
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: npm ci

      - name: Run npm audit (JSON output)
        id: npm-audit-json
        run: |
          npm audit --json > npm-audit-results.json 2>&1 || true

      - name: Upload npm audit JSON results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: npm-audit-results
          path: frontend/npm-audit-results.json
          retention-days: 30

      - name: Run npm audit (fail on high/critical)
        run: |
          # npm audit returns exit code based on vulnerabilities found
          # --audit-level=high will fail on high and critical
          npm audit --audit-level=high

      - name: Generate human-readable report
        if: always()
        run: |
          npm audit > npm-audit-report.txt 2>&1 || true

      - name: Upload human-readable report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: npm-audit-report
          path: frontend/npm-audit-report.txt
          retention-days: 30
```

### Alternative: Using safety for Python (if pip-audit unavailable)

```yaml
  python-dependency-scan-safety:
    name: Python Dependency Scan (Safety)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '{{ cookiecutter.python_version }}'

      - name: Install safety
        run: pip install safety

      - name: Export requirements
        working-directory: backend
        run: |
          pip install uv
          uv pip compile pyproject.toml -o requirements.txt

      - name: Run safety check
        working-directory: backend
        run: |
          safety check \
            --file requirements.txt \
            --full-report \
            --output json \
            > safety-results.json 2>&1 || true

          # Fail on vulnerabilities
          safety check --file requirements.txt
```

### Tool Comparison

| Tool | Pros | Cons | Recommendation |
|------|------|------|----------------|
| **pip-audit** | OSV database, actively maintained, PyPA project | Requires Python 3.7+ | Primary choice |
| **safety** | Well-known, JSON output | Requires API key for full database | Alternative |
| **npm audit** | Built-in, no installation | Only npm packages | Required for frontend |
| **Trivy fs scan** | Scans multiple formats | Less granular for deps | Already in P2-03 |

### Severity Mapping

| Tool | High Threshold | Critical Threshold |
|------|----------------|-------------------|
| pip-audit | `--strict` fails on any vulnerability | Same |
| npm audit | `--audit-level=high` | `--audit-level=critical` |
| safety | Exit code 64+ on vulnerabilities | Same |

### Vulnerability Database Sources

| Tool | Database | Update Frequency |
|------|----------|------------------|
| pip-audit | OSV (Open Source Vulnerabilities) | Real-time |
| safety | PyUp Safety DB | Daily |
| npm audit | GitHub Advisory Database | Real-time |

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P1-01 | Prerequisite | CI workflow must exist |
| P2-03 | Sibling | Extends security.yml workflow |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-06 | Reference | Security checklist references dependency scanning |
| P6-03 | Validation | Cookiecutter validation includes security workflow |

---

## Success Criteria

### Functional Requirements

- [ ] Python dependency scan runs in security workflow
- [ ] pip-audit scans backend dependencies from pyproject.toml
- [ ] npm audit scans frontend dependencies from package.json
- [ ] Workflow fails on HIGH or CRITICAL vulnerabilities (per FR-SEC-010)
- [ ] JSON results uploaded as workflow artifacts
- [ ] Human-readable reports uploaded as workflow artifacts
- [ ] Both scans complete even if one fails (fail-fast: false)

### Non-Functional Requirements

- [ ] Python scan completes in under 2 minutes
- [ ] npm scan completes in under 2 minutes
- [ ] Artifacts retained for 30 days for audit purposes
- [ ] Minimal additional permissions required

### Validation Steps

1. Add known vulnerable Python package
   - Add `requests==2.19.0` (known CVEs) to test
   - Verify pip-audit fails with vulnerability details
   - Verify JSON output contains CVE information

2. Add known vulnerable npm package
   - Add vulnerable version of a package
   - Verify npm audit fails with vulnerability details
   - Verify JSON output contains advisory information

3. Test clean dependencies
   - Use current locked dependencies
   - Verify both scans pass
   - Verify artifacts are generated

4. Test artifact retention
   - Download artifacts from completed workflow
   - Verify JSON format is valid and parseable

---

## Integration Points

### Security Workflow Structure

The complete security.yml after P2-03 and P2-04:

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main, develop]
  schedule:
    - cron: '0 6 * * 1'
  workflow_dispatch:

jobs:
  # From P2-03
  trivy-image-scan:
    # ... container scanning ...

  trivy-filesystem-scan:
    # ... filesystem scanning ...

  # From P2-04
  python-dependency-scan:
    # ... pip-audit ...

  npm-dependency-scan:
    # ... npm audit ...
```

### Dependabot Integration (P1-04)

Dependency scanning complements Dependabot:

| Tool | Purpose |
|------|---------|
| Dependabot | Automatic PRs for updates |
| pip-audit/npm audit | Fail CI on vulnerabilities |

Together they provide:
1. Proactive updates (Dependabot)
2. Gated security enforcement (audit tools)

### Lock File Handling

Both tools work with lock files for reproducible scans:

| Language | Lock File | Tool Handling |
|----------|-----------|---------------|
| Python | uv.lock | Compile to requirements, then audit |
| Node.js | package-lock.json | npm audit reads directly |

---

## Monitoring and Observability

### Workflow Status

Monitor via:
- GitHub Actions workflow status badge
- Artifact downloads for vulnerability reports
- PR check status for dependency scans

### Recommended Alerts

1. **Dependency scan failure** - Notify security team
2. **New vulnerability detected** - Block merge until addressed
3. **Weekly scan failures** - Track trending vulnerabilities

### Metrics to Track

| Metric | Source | Purpose |
|--------|--------|---------|
| Vulnerability count | JSON artifacts | Track security posture |
| Time to remediate | PR history | Measure response time |
| False positive rate | Skipped packages | Tune scanning |

---

## Infrastructure Needs

### GitHub Actions Requirements

- Repository must be on GitHub
- GitHub Actions must be enabled
- No additional secrets required for public vulnerability databases

### Tool Installation

Tools installed at runtime:

```yaml
# pip-audit
pip install pip-audit

# npm audit - built into npm, no installation
```

### Resource Requirements

| Resource | Requirement |
|----------|-------------|
| Runner | ubuntu-latest |
| Python | {{ cookiecutter.python_version }} |
| Node.js | 20 |
| Memory | Standard runner sufficient |

---

## Implementation Notes

### pip-audit with uv

Since the template uses uv for dependency management, compile dependencies before auditing:

```bash
# Compile pyproject.toml to requirements format
uv pip compile pyproject.toml -o - | pip-audit -r /dev/stdin
```

This ensures:
- All dependencies (including transitive) are audited
- Locked versions from uv.lock are respected
- No need to install dependencies in workflow

### npm audit Specifics

npm audit behavior:

```bash
# Exit codes:
# 0 - No vulnerabilities
# 1+ - Vulnerabilities found (count varies)

# Audit level options:
npm audit --audit-level=low      # Fail on any
npm audit --audit-level=moderate # Fail on moderate+
npm audit --audit-level=high     # Fail on high+ (recommended)
npm audit --audit-level=critical # Fail on critical only
```

### Handling False Positives

For Python (pip-audit):
```bash
# Ignore specific vulnerabilities
pip-audit --ignore-vuln PYSEC-2023-1234
```

For Node.js (npm):
```json
// .npmrc or package.json
{
  "overrides": {
    "vulnerable-package": "^2.0.0"
  }
}
```

### Production vs Development Dependencies

Consider scanning only production dependencies:

```bash
# Python - production only
uv pip compile pyproject.toml --no-dev -o -

# Node.js - production only
npm audit --omit=dev
```

For this task, scan all dependencies (including dev) since vulnerabilities in dev tools can still be exploited in CI/CD.

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-SEC-008 | CI shall scan Python deps using pip-audit or safety | `pip-audit` job |
| FR-SEC-009 | CI shall scan npm deps using npm audit | `npm-audit` job |
| FR-SEC-010 | CI shall fail if HIGH or CRITICAL found | `--strict` and `--audit-level=high` |

### Related ADRs

- ADR-019: GitHub Actions CI/CD (workflow patterns)
- ADR-022: Container Security Scanning (related security workflow)

### External Resources

- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [npm audit Documentation](https://docs.npmjs.com/cli/v10/commands/npm-audit)
- [OSV Database](https://osv.dev/)
- [GitHub Advisory Database](https://github.com/advisories)
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/)
