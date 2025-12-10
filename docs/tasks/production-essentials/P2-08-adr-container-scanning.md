# P2-08: Write ADR-022: Container Security Scanning

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P2-08 |
| **Task Title** | Write ADR-022: Container Security Scanning |
| **Domain** | Architecture |
| **Complexity** | S (Small) |
| **Estimated Effort** | 0.5 days |
| **Priority** | Should Have |
| **Dependencies** | P2-03 (Trivy scanning must be implemented to document) |
| **FRD Requirements** | NFR-001, FR-SEC-007, FR-SEC-010 |

---

## Scope

### What This Task Includes

1. Write ADR-022 documenting container security scanning decisions
2. Document why Trivy was selected over alternatives (Snyk, Grype, Clair)
3. Document the scanning workflow and integration points
4. Document severity thresholds and failure conditions
5. Document SARIF integration with GitHub Security tab
6. Document scheduled scanning strategy for CVE detection
7. Document alternatives considered and trade-offs
8. Follow existing ADR format from docs/adr/

### What This Task Excludes

- Security headers ADR (P2-07)
- Dependency scanning ADR (could be combined or separate)
- SBOM generation details (documented in P1-02)
- Trivy implementation (P2-03)
- Runtime container security monitoring

---

## Relevant Code Areas

### Files to Create

```
docs/adr/
  022-container-security-scanning.md      # New ADR document
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `docs/adr/017-optional-observability-stack.md` | Template for ADR format |
| `docs/adr/019-github-actions-cicd.md` | CI/CD context |
| `docs/adr/README.md` | ADR index and conventions |
| `docs/tasks/production-essentials/P2-03-trivy-scanning.md` | Implementation specification |
| `template/{{cookiecutter.project_slug}}/.github/workflows/security.yml` | Scanning workflow |

---

## Technical Specification

### ADR Document Structure

The ADR should follow the established format:

```markdown
# ADR-022: Container Security Scanning

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | YYYY-MM-DD |
| **Decision Makers** | Project Team |
| **Related ADRs** | ADR-019 (GitHub Actions CI/CD) |

## Context

Container images are a critical part of the deployment pipeline. They bundle
application code with operating system packages and runtime dependencies,
creating a large attack surface. Known vulnerabilities (CVEs) in these
components can expose applications to:

- Remote code execution
- Privilege escalation
- Data exfiltration
- Denial of service

The template needs automated vulnerability scanning to:
1. Prevent deployment of images with known critical vulnerabilities
2. Provide visibility into the security posture of deployed containers
3. Enable proactive remediation before vulnerabilities are exploited
4. Support compliance requirements (SOC2, PCI-DSS, etc.)

### Scanning Requirements

1. **Pre-merge Scanning**: Block PRs that introduce critical vulnerabilities
2. **Registry Scanning**: Scan images in the container registry
3. **Scheduled Scanning**: Detect newly disclosed CVEs in existing images
4. **SBOM Integration**: Support software bill of materials for supply chain security

## Decision

We adopt **Trivy** by Aqua Security as our container security scanner, integrated
into GitHub Actions via the official `aquasecurity/trivy-action`.

### Why Trivy

| Factor | Trivy | Snyk | Grype | Clair |
|--------|-------|------|-------|-------|
| Cost | Free/OSS | Freemium | Free/OSS | Free/OSS |
| GitHub Action | Official | Official | Community | None |
| Scan Speed | Fast | Medium | Fast | Slow |
| SARIF Output | Yes | Yes | Yes | No |
| SBOM Support | Yes | Limited | Yes | No |
| Offline Mode | Yes | No | Yes | Yes |
| DB Updates | Automatic | Managed | Automatic | Manual |

### Scanning Strategy

#### 1. Pull Request Scanning
- Build image locally (not pushed)
- Scan with Trivy before merge
- Fail on HIGH or CRITICAL severity
- Upload SARIF to GitHub Security tab

#### 2. Main Branch Scanning
- Scan after successful image build
- Results inform release decisions
- SARIF provides audit trail

#### 3. Scheduled Scanning (Weekly)
- Scan main branch images
- Detect newly disclosed CVEs
- Alert security team to new findings

### Severity Handling

| Severity | Exit Code | Action |
|----------|-----------|--------|
| CRITICAL | 1 (fail) | Block merge, immediate attention |
| HIGH | 1 (fail) | Block merge, fix before release |
| MEDIUM | 0 (pass) | Report only, track in backlog |
| LOW | 0 (pass) | Report only, informational |

### Unfixed Vulnerabilities

```yaml
ignore-unfixed: true
```

Vulnerabilities without available patches do not fail the build:
- Prevents blocking on issues developers cannot fix
- Still reported for visibility and tracking
- Can be overridden per-repository if stricter policy needed

### Output Formats

1. **SARIF**: GitHub Security tab integration, code scanning alerts
2. **Table**: Human-readable artifact for review
3. **JSON**: Machine-readable for automation (optional)

### Ignore File (.trivyignore)

False positives and accepted risks are managed via `.trivyignore`:

```
# .trivyignore
# CVE-YYYY-NNNNN - Reason for ignoring
# Only ignore after security team review
```

## Consequences

### Positive

1. **Shift-Left Security**: Vulnerabilities caught before deployment
2. **Automated Enforcement**: No manual security review for common CVEs
3. **Visibility**: GitHub Security tab provides centralized view
4. **Compliance Support**: SARIF reports support audit requirements
5. **Free Tooling**: No additional cost for open source projects
6. **Fast Feedback**: Scans complete in under 5 minutes

### Negative

1. **False Positives**: Some reported vulnerabilities may not be exploitable
2. **Database Lag**: New CVEs take 24-48 hours to appear in Trivy DB
3. **Build Time**: Adds 2-5 minutes to CI pipeline
4. **Ignore Management**: `.trivyignore` requires ongoing maintenance

### Neutral

1. Trivy database updates are automatic but require internet access
2. Multi-platform images require scanning each architecture separately
3. Runtime security (admission controllers, etc.) not addressed by this decision

## Alternatives Considered

### 1. Snyk Container
- **Pros**: Excellent UI, remediation advice, enterprise features
- **Cons**: Freemium model, limited scans on free tier, slower
- **Why Rejected**: Cost for full features, Trivy sufficient for template needs

### 2. Grype (Anchore)
- **Pros**: Fast, good accuracy, SBOM-first approach
- **Cons**: Less mature GitHub Action, smaller community
- **Why Rejected**: Trivy has better GitHub integration and broader adoption

### 3. Clair (Quay)
- **Pros**: Mature, used by Quay registry
- **Cons**: Complex setup, no official GitHub Action, no SARIF
- **Why Rejected**: Integration complexity too high for template

### 4. GitHub Native (Dependabot/CodeQL)
- **Pros**: No additional tooling, native integration
- **Cons**: Limited container scanning, primarily for dependencies
- **Why Rejected**: Does not provide comprehensive container image scanning

## Implementation References

- Workflow: `template/{{cookiecutter.project_slug}}/.github/workflows/security.yml`
- Ignore file: `template/{{cookiecutter.project_slug}}/.trivyignore`
- Task specification: `docs/tasks/production-essentials/P2-03-trivy-scanning.md`

## External References

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Action](https://github.com/aquasecurity/trivy-action)
- [SARIF Specification](https://sarifweb.azurewebsites.net/)
- [GitHub Code Scanning](https://docs.github.com/en/code-security/code-scanning)
- [CVE Database](https://cve.mitre.org/)
```

### Key Content Requirements

#### Context Section Must Cover

1. Why container scanning is necessary (attack surface, CVEs)
2. Types of vulnerabilities found in containers (OS packages, libraries)
3. Compliance and audit requirements
4. Shift-left security principles

#### Decision Section Must Cover

1. Why Trivy was selected (comparison table with alternatives)
2. Scanning strategy (PR, main branch, scheduled)
3. Severity thresholds and failure conditions
4. Unfixed vulnerability handling rationale
5. Output formats and their purposes
6. Ignore file management approach

#### Consequences Section Must Cover

1. **Positive**: Shift-left, automation, visibility, compliance, speed
2. **Negative**: False positives, DB lag, build time, ignore maintenance
3. **Neutral**: DB updates, multi-arch considerations, runtime security gap

#### Alternatives Section Must Cover

1. Snyk Container (rejected: cost for full features)
2. Grype/Anchore (rejected: less mature GitHub integration)
3. Clair/Quay (rejected: integration complexity)
4. GitHub Native (rejected: limited container scanning)

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-03 | Required | Trivy scanning must be implemented to document |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-06 | Reference | Security checklist references ADR-022 |
| P6-01 | Reference | CLAUDE.md update references ADR-022 |

---

## Success Criteria

### Functional Requirements

- [ ] ADR-022 created in docs/adr/ directory
- [ ] ADR follows established format from existing ADRs
- [ ] Context section explains container security risks and requirements
- [ ] Decision section documents Trivy selection with comparison table
- [ ] Scanning strategy documented (PR, main, scheduled)
- [ ] Severity thresholds and failure conditions documented
- [ ] Unfixed vulnerability handling explained
- [ ] Output formats (SARIF, table) documented
- [ ] Ignore file approach documented
- [ ] Alternatives section covers Snyk, Grype, Clair, GitHub native
- [ ] Consequences section covers positive, negative, and neutral outcomes
- [ ] Implementation references point to correct file paths

### Non-Functional Requirements

- [ ] ADR is clear and understandable to developers unfamiliar with container security
- [ ] Technical accuracy verified against implementation (P2-03)
- [ ] Comparison table provides objective criteria for tool selection
- [ ] External references to Trivy docs and CVE resources included
- [ ] ADR index (docs/adr/README.md) updated with new entry

### Validation Steps

1. Review ADR-022 against ADR template from existing ADRs
2. Verify scanning configuration matches P2-03 implementation
3. Verify comparison table is accurate and fair
4. Verify alternatives considered are relevant industry options
5. Verify file paths in implementation references are correct
6. Verify ADR index updated

---

## Integration Points

### ADR Index Update

Update `docs/adr/README.md` to include:

```markdown
| ADR-022 | Container Security Scanning | Accepted | Security |
```

### Cross-References

The ADR should reference:
- ADR-019 (GitHub Actions CI/CD) for workflow context
- P2-03 task document for implementation details

### Related Documentation

After this ADR is written:
- P2-06 security checklist should reference ADR-022
- P6-01 CLAUDE.md update should mention ADR-022

---

## Monitoring and Observability

### Not Applicable

This is a documentation task with no runtime monitoring requirements.

---

## Infrastructure Needs

### No Additional Infrastructure Required

This task creates documentation only.

### Development Requirements

- Access to docs/adr/ directory
- Familiarity with existing ADR format
- Understanding of P2-03 implementation
- Basic knowledge of container security concepts

---

## Implementation Notes

### ADR Numbering

ADR-022 follows ADR-021 (Kubernetes Deployment). Note the gap from ADR-020 (Security Headers) - ADR-021 is reserved for Kubernetes deployment architecture.

### Tool Comparison Objectivity

The comparison table should be:
- Factual and verifiable
- Based on current tool capabilities (as of implementation date)
- Fair to all alternatives
- Focused on criteria relevant to the template use case

### Trivy vs Snyk Context

While Snyk is more feature-rich for enterprise use, the ADR should clearly explain why Trivy is preferred for an open-source template:
- Free for all uses
- No account required
- Simpler integration
- Sufficient accuracy for template needs

### Future Considerations

The ADR should note potential future enhancements:
- Runtime security scanning (admission controllers)
- SBOM-based vulnerability tracking
- Vulnerability management workflow integration

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| NFR-001 | All features shall have ADR documentation | This task |
| FR-SEC-007 | CI shall scan container images using Trivy | Documented in ADR |
| FR-SEC-010 | CI shall fail if HIGH or CRITICAL found | Documented in ADR |

### Related ADRs

- ADR-019: GitHub Actions CI/CD (workflow context)
- ADR-020: Security Headers (related security decision)
- ADR-021: Kubernetes Deployment (deployment context)

### External Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Action](https://github.com/aquasecurity/trivy-action)
- [OWASP Container Security](https://owasp.org/www-project-docker-security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Container Security Guide](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-190.pdf)
