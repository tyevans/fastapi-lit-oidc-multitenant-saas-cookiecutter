# P2-03: Add Trivy Container Scanning to CI

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P2-03 |
| **Task Title** | Add Trivy Container Scanning to CI |
| **Domain** | DevOps |
| **Complexity** | S (Small) |
| **Estimated Effort** | 1 day |
| **Priority** | Must Have |
| **Dependencies** | P1-02 (Build workflow must exist to produce images) |
| **FRD Requirements** | FR-SEC-007, FR-SEC-010 |

---

## Scope

### What This Task Includes

1. Create `.github/workflows/security.yml` workflow file
2. Configure Trivy to scan built container images for vulnerabilities
3. Configure severity thresholds (fail on HIGH/CRITICAL)
4. Upload scan results as workflow artifacts
5. Configure SARIF output for GitHub Security tab integration
6. Add cookiecutter conditional (part of `include_github_actions`)

### What This Task Excludes

- Dependency vulnerability scanning (P2-04) - separate job in same workflow
- Dockerfile security best practices scanning (can be added later)
- SBOM generation (handled in P1-02 build workflow)
- Production Dockerfile hardening (P1-03)

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    security.yml              # Security scanning workflow
{% raw %}{% endif %}{% endraw %}
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/.github/workflows/build.yml` | Build workflow that produces images (P1-02) |
| `template/{{cookiecutter.project_slug}}/.github/workflows/ci.yml` | CI workflow patterns (P1-01) |
| `template/{{cookiecutter.project_slug}}/backend/Dockerfile` | Backend image to scan |
| `template/{{cookiecutter.project_slug}}/frontend/Dockerfile` | Frontend image to scan |

---

## Technical Specification

### Workflow Structure

```yaml
name: Security

on:
  push:
    branches: [main]
  pull_request:
    branches: [main, develop]
  schedule:
    # Run weekly to catch new CVEs
    - cron: '0 6 * * 1'  # Monday at 6 AM UTC
  workflow_dispatch:  # Allow manual triggers

concurrency:
  group: {% raw %}${{ github.workflow }}-${{ github.ref }}{% endraw %}
  cancel-in-progress: true

permissions:
  contents: read
  security-events: write  # Required for SARIF upload

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE: {% raw %}${{ github.repository }}{% endraw %}/backend
  FRONTEND_IMAGE: {% raw %}${{ github.repository }}{% endraw %}/frontend

jobs:
  trivy-image-scan:
    name: Container Image Scan
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false  # Continue scanning all images even if one fails
      matrix:
        include:
          - service: backend
            dockerfile: backend/Dockerfile
            context: backend
          - service: frontend
            dockerfile: frontend/Dockerfile
            context: frontend

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build image for scanning
        uses: docker/build-push-action@v6
        with:
          context: {% raw %}${{ matrix.context }}{% endraw %}
          file: {% raw %}${{ matrix.dockerfile }}{% endraw %}
          target: production
          load: true  # Load into local Docker for scanning
          tags: {% raw %}${{ matrix.service }}:scan{% endraw %}
          cache-from: type=gha,scope={% raw %}${{ matrix.service }}{% endraw %}
          cache-to: type=gha,mode=max,scope={% raw %}${{ matrix.service }}{% endraw %}

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: {% raw %}${{ matrix.service }}:scan{% endraw %}
          format: 'sarif'
          output: 'trivy-{% raw %}${{ matrix.service }}{% endraw %}.sarif'
          severity: 'CRITICAL,HIGH,MEDIUM'
          # Fail on HIGH or CRITICAL vulnerabilities
          exit-code: '1'
          ignore-unfixed: true  # Ignore vulnerabilities without fixes
          vuln-type: 'os,library'

      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v3
        if: always()  # Upload even if scan fails
        with:
          sarif_file: 'trivy-{% raw %}${{ matrix.service }}{% endraw %}.sarif'
          category: 'trivy-{% raw %}${{ matrix.service }}{% endraw %}'

      - name: Generate human-readable report
        uses: aquasecurity/trivy-action@master
        if: always()
        with:
          image-ref: {% raw %}${{ matrix.service }}:scan{% endraw %}
          format: 'table'
          output: 'trivy-{% raw %}${{ matrix.service }}{% endraw %}-report.txt'
          severity: 'CRITICAL,HIGH,MEDIUM,LOW'
          vuln-type: 'os,library'

      - name: Upload scan report artifact
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: trivy-{% raw %}${{ matrix.service }}{% endraw %}-report
          path: trivy-{% raw %}${{ matrix.service }}{% endraw %}-report.txt
          retention-days: 30

  trivy-filesystem-scan:
    name: Filesystem Scan
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Run Trivy filesystem scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-filesystem.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
          ignore-unfixed: true

      - name: Upload filesystem scan results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: 'trivy-filesystem.sarif'
          category: 'trivy-filesystem'
```

### Trivy Configuration Options

| Option | Value | Rationale |
|--------|-------|-----------|
| `severity` | `CRITICAL,HIGH,MEDIUM` | Report all significant vulnerabilities |
| `exit-code` | `1` | Fail build on HIGH/CRITICAL (per FR-SEC-010) |
| `ignore-unfixed` | `true` | Don't fail on vulnerabilities without patches |
| `vuln-type` | `os,library` | Scan both OS packages and language libraries |
| `format` | `sarif` | GitHub Security tab integration |

### Trivy Ignore File (.trivyignore)

Create a `.trivyignore` file for managing false positives:

```
# .trivyignore
# List CVE IDs to ignore (one per line)
# Only ignore vulnerabilities after careful review

# Example: CVE-2023-12345 - False positive for our use case
# CVE-2023-12345

# See: https://aquasecurity.github.io/trivy/latest/docs/configuration/filtering/
```

### Severity Levels and Actions

| Severity | Exit Code | Action |
|----------|-----------|--------|
| CRITICAL | 1 (fail) | Block merge, immediate attention required |
| HIGH | 1 (fail) | Block merge, fix before release |
| MEDIUM | 0 (pass) | Report only, fix in next sprint |
| LOW | 0 (pass) | Report only, track for future |

### Scheduled Scans

Weekly scheduled scans (`cron: '0 6 * * 1'`) ensure:
- New CVEs are detected even without code changes
- Main branch is continuously monitored
- Security team gets regular updates

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P1-02 | Prerequisite | Uses same Dockerfile targets and build patterns |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-06 | Reference | Security checklist references container scanning |
| P2-08 | Reference | ADR-022 documents container scanning strategy |
| P6-03 | Validation | Cookiecutter validation includes security workflow |

---

## Success Criteria

### Functional Requirements

- [ ] Security workflow triggers on push to main
- [ ] Security workflow triggers on pull requests
- [ ] Security workflow runs weekly on schedule
- [ ] Backend container image scanned with Trivy
- [ ] Frontend container image scanned with Trivy
- [ ] Workflow fails on HIGH or CRITICAL vulnerabilities
- [ ] Unfixed vulnerabilities do not fail the build
- [ ] SARIF results uploaded to GitHub Security tab
- [ ] Human-readable reports uploaded as artifacts
- [ ] Filesystem scan runs for dependency vulnerabilities
- [ ] Matrix strategy scans both images in parallel

### Non-Functional Requirements

- [ ] Scan completes in under 5 minutes per image
- [ ] Docker layer caching reduces rebuild time
- [ ] Minimal permissions (contents: read, security-events: write)
- [ ] Artifacts retained for 30 days for audit purposes

### Validation Steps

1. Create PR with vulnerable dependency
   - Add known vulnerable package to requirements.txt
   - Verify workflow fails with vulnerability details
   - Verify SARIF results appear in Security tab

2. Create PR with no vulnerabilities
   - Verify workflow passes
   - Verify reports generated and uploaded

3. Test scheduled scan
   - Manually trigger workflow
   - Verify both images scanned successfully

4. Test ignore functionality
   - Add CVE to .trivyignore
   - Verify vulnerability is skipped

---

## Integration Points

### GitHub Security Tab

SARIF (Static Analysis Results Interchange Format) enables:
- Vulnerabilities visible in GitHub Security tab
- Per-PR security annotations
- Trend tracking over time
- Export for compliance reporting

### Build Workflow Relationship

The security workflow builds images locally for scanning rather than pulling from registry:

```yaml
# Build locally for scanning (not pushed)
uses: docker/build-push-action@v6
with:
  load: true  # Load into local Docker
  push: false # Don't push to registry
```

This ensures:
- PRs are scanned before merge
- No need to wait for build workflow
- No registry credentials required for scanning

### Caching Strategy

Uses GitHub Actions cache scoped per service:

```yaml
cache-from: type=gha,scope={% raw %}${{ matrix.service }}{% endraw %}
cache-to: type=gha,mode=max,scope={% raw %}${{ matrix.service }}{% endraw %}
```

This provides:
- Fast rebuilds for security scans
- Separate cache per service (backend/frontend)
- Shared with build workflow if scopes match

---

## Monitoring and Observability

### Workflow Status

Monitor via:
- GitHub Actions workflow status badge
- Repository Security tab for vulnerability trends
- Email notifications for failed scheduled scans

### Recommended Alerts

1. **Security scan failure** - Immediate notification to security team
2. **New CRITICAL vulnerability** - Page on-call engineer
3. **Weekly scan completed** - Summary report to stakeholders

### Metrics to Track

| Metric | Source | Purpose |
|--------|--------|---------|
| Vulnerability count by severity | Security tab | Track security posture |
| Time to remediate | PR history | Measure response time |
| False positive rate | .trivyignore entries | Tune scanning |

---

## Infrastructure Needs

### GitHub Actions Requirements

- Repository must be on GitHub
- GitHub Actions must be enabled
- Advanced Security (for private repos) or public repository

### Permissions Required

```yaml
permissions:
  contents: read          # Read repository
  security-events: write  # Upload SARIF
```

### Resource Limits

- GitHub-hosted runners: 7 GB RAM, 2 CPU
- Trivy downloads vulnerability database (~500 MB)
- Consider caching Trivy DB for faster scans

---

## Implementation Notes

### Trivy Database Caching

For faster scans, consider caching the Trivy database:

```yaml
- name: Cache Trivy DB
  uses: actions/cache@v4
  with:
    path: ~/.cache/trivy
    key: trivy-db-{% raw %}${{ github.run_id }}{% endraw %}
    restore-keys: |
      trivy-db-
```

### Matrix Strategy Benefits

Using matrix for multiple images:
- Parallel scanning (faster overall)
- Consistent configuration
- Easy to add new services

```yaml
strategy:
  matrix:
    include:
      - service: backend
      - service: frontend
      # Add more services as needed
```

### Fail-Fast Disabled

```yaml
fail-fast: false
```

This ensures all images are scanned even if one fails, providing complete visibility.

### Production Target Only

Scans use the `production` Dockerfile target:

```yaml
target: production
```

This matches what gets deployed, not development dependencies.

---

## Trivy Output Formats

### SARIF Format (Primary)

Used for GitHub Security integration:

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [{
    "tool": { "driver": { "name": "Trivy" } },
    "results": [...]
  }]
}
```

### Table Format (Human-Readable)

Uploaded as artifact for review:

```
┌──────────────┬────────────────┬──────────┬────────────────────────────────────────────────────────────┐
│   Library    │ Vulnerability  │ Severity │                           Title                            │
├──────────────┼────────────────┼──────────┼────────────────────────────────────────────────────────────┤
│ libexpat    │ CVE-2024-12345 │ HIGH     │ Heap buffer overflow in XML parsing                        │
└──────────────┴────────────────┴──────────┴────────────────────────────────────────────────────────────┘
```

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-SEC-007 | CI shall scan container images using Trivy | `aquasecurity/trivy-action` |
| FR-SEC-010 | CI shall fail if HIGH or CRITICAL found | `exit-code: '1'` with severity filter |

### Related ADRs

- ADR-019: GitHub Actions CI/CD (workflow patterns)
- ADR-022: Container Security Scanning (to be written in P2-08)

### External Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Action](https://github.com/aquasecurity/trivy-action)
- [GitHub SARIF Upload](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github)
- [GitHub Security Tab](https://docs.github.com/en/code-security/security-overview/about-the-security-overview)
