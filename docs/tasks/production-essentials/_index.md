# Production Essentials - Task Breakdown

## Feature Overview

Implement production-ready CI/CD pipelines, security hardening, Kubernetes deployment manifests, operational tooling (Sentry, alerting, backups), and developer experience improvements (k6 load testing, API versioning) for the cookiecutter SaaS template.

**Key Context:**
- UNRELEASED project - clean code first, breaking changes encouraged
- Follows existing `include_observability` cookiecutter conditional pattern (ADR-017)
- CI/CD focuses on GitHub Actions (primary target platform)
- Kubernetes uses Kustomize (no Helm complexity for initial release)
- Security headers, Sentry, and K8s are optional features

**Source FRD:** [frd.md](./frd.md)
**Refinement Tracking:** [.refinement-tracking-production-essentials.md](../../futures/.refinement-tracking-production-essentials.md)

---

## Task List

### Phase 1: CI/CD Foundation (2-3 weeks)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P1-01 | [Create GitHub Actions CI workflow](./P1-01-github-actions-ci.md) | Documented | DevOps | M | None |
| P1-02 | [Create GitHub Actions build workflow](./P1-02-github-actions-build.md) | Documented | DevOps | M | P1-01 |
| P1-03 | [Enhance production Dockerfiles](./P1-03-production-dockerfiles.md) | Documented | DevOps | S | None |
| P1-04 | [Configure Dependabot](./P1-04-dependabot-config.md) | Documented | DevOps | XS | None |
| P1-05 | [Configure Codecov integration](./P1-05-codecov-integration.md) | Documented | DevOps | S | P1-01 |
| P1-06 | [Write ADR-019: GitHub Actions CI/CD](./P1-06-adr-cicd.md) | Documented | Architecture | S | P1-01, P1-02 |

### Phase 2: Security Hardening (2 weeks)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P2-01 | [Implement security headers middleware](./P2-01-security-headers-middleware.md) | Documented | Backend | M | None |
| P2-02 | [Add security configuration to config.py](./P2-02-security-config.md) | Documented | Backend | S | P2-01 |
| P2-03 | [Add Trivy container scanning to CI](./P2-03-trivy-scanning.md) | Documented | DevOps | S | P1-02 |
| P2-04 | [Add dependency vulnerability scanning](./P2-04-dependency-scanning.md) | Documented | DevOps | S | P1-01 |
| P2-05 | [Configure gitleaks pre-commit hook](./P2-05-gitleaks-precommit.md) | Documented | DevOps | S | None |
| P2-06 | [Create security audit checklist](./P2-06-security-checklist.md) | Documented | Documentation | M | P2-01, P2-03 |
| P2-07 | [Write ADR-020: Security Headers](./P2-07-adr-security-headers.md) | Documented | Architecture | S | P2-01 |
| P2-08 | [Write ADR-022: Container Security Scanning](./P2-08-adr-container-scanning.md) | Documented | Architecture | S | P2-03 |

### Phase 3: Operational Readiness (2-3 weeks)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P3-01 | [Create Prometheus alerting rules](./P3-01-prometheus-alerts.md) | Documented | DevOps | M | None |
| P3-02 | [Update prometheus.yml with rule_files](./P3-02-prometheus-config-update.md) | Documented | DevOps | XS | P3-01 |
| P3-03 | [Implement optional Sentry integration](./P3-03-sentry-integration.md) | Documented | Backend | L | None |
| P3-04 | [Add Sentry cookiecutter conditional](./P3-04-sentry-cookiecutter.md) | Documented | DevOps | M | P3-03 |
| P3-05 | [Create database backup scripts](./P3-05-backup-scripts.md) | Documented | DevOps | M | None |
| P3-06 | [Create restore and recovery scripts](./P3-06-restore-scripts.md) | Documented | DevOps | M | P3-05 |
| P3-07 | [Create Kubernetes backup CronJob](./P3-07-backup-cronjob.md) | Documented | DevOps | S | P3-05, P4-01 |
| P3-08 | [Create operational runbook templates](./P3-08-runbook-templates.md) | Documented | Documentation | M | P3-01 |
| P3-09 | [Write point-in-time recovery documentation](./P3-09-recovery-docs.md) | Documented | Documentation | M | P3-05, P3-06 |
| P3-10 | [Write ADR-023: Database Backup Strategy](./P3-10-adr-backup.md) | Documented | Architecture | S | P3-05 |
| P3-11 | [Write ADR-024: Sentry Integration](./P3-11-adr-sentry.md) | Documented | Architecture | S | P3-03 |

### Phase 4: Kubernetes Deployment (2 weeks)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P4-01 | [Create Kubernetes base manifests](./P4-01-k8s-base-manifests.md) | Documented | DevOps | L | P1-03 |
| P4-02 | [Create Kustomize staging overlay](./P4-02-kustomize-staging.md) | Documented | DevOps | S | P4-01 |
| P4-03 | [Create Kustomize production overlay](./P4-03-kustomize-production.md) | Documented | DevOps | S | P4-01 |
| P4-04 | [Create GitHub Actions deploy workflow](./P4-04-deploy-workflow.md) | Documented | DevOps | M | P4-01, P1-02 |
| P4-05 | [Create production Docker Compose file](./P4-05-compose-production.md) | Documented | DevOps | S | P1-03 |
| P4-06 | [Add Kubernetes cookiecutter conditional](./P4-06-k8s-cookiecutter.md) | Documented | DevOps | M | P4-01 |
| P4-07 | [Document environment configuration](./P4-07-env-config-docs.md) | Documented | Documentation | M | P4-01 |
| P4-08 | [Write ADR-021: Kubernetes Deployment](./P4-08-adr-kubernetes.md) | Documented | Architecture | S | P4-01 |

### Phase 5: Developer Experience (2 weeks)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P5-01 | [Configure OpenAPI Generator for TypeScript](./P5-01-openapi-generator.md) | Documented | Frontend | M | None |
| P5-02 | [Create k6 load testing scripts](./P5-02-k6-load-tests.md) | Documented | DevOps | M | None |
| P5-03 | [Create k6 authentication flow tests](./P5-03-k6-auth-tests.md) | Documented | DevOps | M | P5-02 |
| P5-04 | [Document API versioning strategy](./P5-04-api-versioning-docs.md) | Documented | Documentation | S | None |
| P5-05 | [Document performance baselines](./P5-05-performance-baselines.md) | Documented | Documentation | S | P5-02 |

### Phase 6: Documentation and Validation (1-2 weeks)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P6-01 | [Update CLAUDE.md with new features](./P6-01-claude-md-update.md) | Documented | Documentation | M | All P1-P5 |
| P6-02 | [Create migration guide for existing projects](./P6-02-migration-guide.md) | Documented | Documentation | M | All P1-P5 |
| P6-03 | [Validate cookiecutter option combinations](./P6-03-cookiecutter-validation.md) | Documented | DevOps | M | All P1-P5 |
| P6-04 | [End-to-end deployment validation](./P6-04-e2e-validation.md) | Documented | DevOps | L | P6-03 |
| P6-05 | [Write release notes](./P6-05-release-notes.md) | Documented | Documentation | S | P6-04 |

---

## Dependency Graph

```
Phase 1: CI/CD Foundation
=========================
                    P1-03 (Dockerfiles) ----+
                                            |
P1-01 (CI Workflow) ----+---> P1-05 (Codecov)
        |               |
        |               +---> P1-06 (ADR-019)
        |               |
        +---> P1-02 (Build Workflow) ---+
                                        |
P1-04 (Dependabot) [independent]        |
                                        v
                              Feeds into Phase 2, 4

Phase 2: Security Hardening
============================
P2-01 (Middleware) ---> P2-02 (Config) ---> P2-06 (Checklist)
        |                                         ^
        +---> P2-07 (ADR-020)                    |
                                                  |
P1-02 ---> P2-03 (Trivy) ---> P2-06 (Checklist) -+
                |
                +---> P2-08 (ADR-022)

P1-01 ---> P2-04 (Dependency Scanning)

P2-05 (Gitleaks) [independent]

Phase 3: Operational Readiness
==============================
P3-01 (Prometheus Alerts) ---> P3-02 (Config Update) ---> P3-08 (Runbooks)
                                                              ^
P3-03 (Sentry) ---> P3-04 (Cookiecutter) ---> P3-11 (ADR)    |
                                                              |
P3-05 (Backup) ---> P3-06 (Restore) ---> P3-09 (Recovery Docs)
        |                |
        +---> P3-10 (ADR-023)
        |
        +---> P3-07 (CronJob) [needs P4-01]

Phase 4: Kubernetes Deployment
==============================
P1-03 ---> P4-01 (Base Manifests) ---> P4-02 (Staging)
                   |                         |
                   +---> P4-03 (Production) -+
                   |                         |
                   +---> P4-04 (Deploy Workflow) <--- P1-02
                   |
                   +---> P4-05 (Compose Prod)
                   |
                   +---> P4-06 (Cookiecutter)
                   |
                   +---> P4-07 (Env Docs)
                   |
                   +---> P4-08 (ADR-021)

Phase 5: Developer Experience
=============================
P5-01 (OpenAPI Generator) [independent]

P5-02 (k6 Load Tests) ---> P5-03 (Auth Tests) ---> P5-05 (Baselines)

P5-04 (API Versioning Docs) [independent]

Phase 6: Documentation & Validation
====================================
All P1-P5 ---> P6-01 (CLAUDE.md)
           |
           +---> P6-02 (Migration Guide)
           |
           +---> P6-03 (Validation) ---> P6-04 (E2E) ---> P6-05 (Release Notes)
```

---

## Domain Distribution

### DevOps Agent (26 tasks)
- **Phase 1:** P1-01, P1-02, P1-03, P1-04, P1-05
- **Phase 2:** P2-03, P2-04, P2-05
- **Phase 3:** P3-01, P3-02, P3-04, P3-05, P3-06, P3-07
- **Phase 4:** P4-01, P4-02, P4-03, P4-04, P4-05, P4-06
- **Phase 5:** P5-02, P5-03
- **Phase 6:** P6-03, P6-04

### Backend Agent (4 tasks)
- **Phase 2:** P2-01, P2-02
- **Phase 3:** P3-03

### Frontend Agent (1 task)
- **Phase 5:** P5-01

### Architecture Agent (7 tasks)
- **Phase 1:** P1-06
- **Phase 2:** P2-07, P2-08
- **Phase 3:** P3-10, P3-11
- **Phase 4:** P4-08

### Documentation Agent (8 tasks)
- **Phase 2:** P2-06
- **Phase 3:** P3-08, P3-09
- **Phase 4:** P4-07
- **Phase 5:** P5-04, P5-05
- **Phase 6:** P6-01, P6-02, P6-05

---

## Integration Contracts

### Contract 1: Security Headers Middleware API
**Provider:** Backend Agent (P2-01)
**Consumer:** main.py integration (P2-02)

```python
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to all HTTP responses.

    Headers added:
    - Content-Security-Policy
    - Strict-Transport-Security (HTTPS only)
    - X-Frame-Options
    - X-Content-Type-Options
    - Referrer-Policy
    """
```

### Contract 2: Sentry Integration Module
**Provider:** Backend Agent (P3-03)
**Consumer:** main.py, cookiecutter conditionals (P3-04)

```python
def init_sentry(settings: Settings) -> None:
    """
    Initialize Sentry SDK with FastAPI integration.

    Features:
    - Automatic exception capture
    - User context (tenant_id, user_id)
    - Release tracking
    - PII filtering via before_send hook
    """
```

### Contract 3: Prometheus Alerting Rules
**Provider:** DevOps Agent (P3-01)
**Consumer:** Prometheus configuration (P3-02)

```yaml
# observability/prometheus/alerts.yml
groups:
  - name: backend_alerts
    rules:
      - alert: HighErrorRate
      - alert: HighLatency
      - alert: DatabaseConnectionPoolExhausted
      - alert: RedisConnectionFailure
```

### Contract 4: Kubernetes Manifests Structure
**Provider:** DevOps Agent (P4-01)
**Consumer:** Overlays (P4-02, P4-03), deploy workflow (P4-04)

```
k8s/
  base/
    kustomization.yaml
    backend-deployment.yaml
    backend-service.yaml
    frontend-deployment.yaml
    frontend-service.yaml
    configmap.yaml
    ingress.yaml
  overlays/
    staging/
      kustomization.yaml
      configmap-patch.yaml
    production/
      kustomization.yaml
      configmap-patch.yaml
      replicas-patch.yaml
```

### Contract 5: Cookiecutter Conditional Variables
**Provider:** DevOps Agent (P1-01, P3-04, P4-06)
**Consumer:** Template files

```json
{
  "include_github_actions": "yes",  // Default: yes
  "include_kubernetes": "no",       // Default: no (opt-in)
  "include_sentry": "no",           // Default: no (opt-in)
  "sentry_dsn": ""                  // Only used if include_sentry == "yes"
}
```

---

## Progress Tracking

| Phase | Tasks | Documented | Completed | Progress |
|-------|-------|------------|-----------|----------|
| Phase 1 | 6 | 6 | 0 | 100% documented |
| Phase 2 | 8 | 8 | 0 | 100% documented |
| Phase 3 | 11 | 11 | 0 | 100% documented |
| Phase 4 | 8 | 8 | 0 | 100% documented |
| Phase 5 | 5 | 5 | 0 | 100% documented |
| Phase 6 | 5 | 5 | 0 | 100% documented |
| **Total** | **43** | **43** | **0** | **100% documented**|

---

## Notes and Refinements

### Initial Breakdown Notes (2025-12-05)

**Scope Refinements from FRD Analysis:**
1. Production Dockerfile targets already exist (per refinement tracking) - P1-03 focuses on enhancements (HEALTHCHECK)
2. Frontend nginx.conf already has X-Frame-Options, X-Content-Type-Options, X-XSS-Protection - Backend middleware is primary focus
3. Observability stack exists - alerting rules (P3-01, P3-02) extend existing prometheus.yml

**Codebase Alignment (from refinement tracking):**
- Total FRD requirements: 78 (32 Must Have, 35 Should Have, 11 Could Have)
- Refined estimate: 10-11 weeks (vs FRD's 10-14 weeks)
- Strong existing foundations: Docker production targets, observability stack, testing infrastructure

### Risks Identified

1. **Jinja2 Template Complexity**: Multiple new cookiecutter conditionals (github_actions, kubernetes, sentry) - needs careful testing
2. **CSP Policy Tuning**: Lit components use inline styles - CSP must allow 'unsafe-inline' for script-src
3. **Alert Fatigue**: Prometheus alerting rules need careful threshold tuning
4. **Cross-Platform Docker Builds**: ARM64 builds may be slower - needs CI optimization

### Key Decisions

1. GitHub Actions is the only CI/CD platform for initial release (GitLab CI out of scope)
2. Kubernetes uses Kustomize, not Helm (simpler, built into kubectl)
3. Sentry is optional (follows include_observability pattern)
4. k6 for load testing (JavaScript-based, low resource consumption)
5. Security headers configurable via environment variables

---

## Breakdown Status

**Status**: COMPLETE - 43 of 43 tasks documented (100%)

**Breakdown Date**: 2025-12-05
**Completion Date**: 2025-12-05

---

### Phase 6 - Documentation and Validation (FINAL PHASE - COMPLETE)

**Tasks Documented (Final Session)**:
- P6-01: Update CLAUDE.md with new features (Documentation, M) - Comprehensive CLAUDE.md updates covering CI/CD, security, K8s, Sentry, load testing, API generation, backup/restore commands, and troubleshooting
- P6-02: Create migration guide for existing projects (Documentation, M) - Full migration guide with step-by-step procedures for each feature area, verification checklists, rollback procedures
- P6-03: Validate cookiecutter option combinations (DevOps, M) - Pytest test suite for all 16 option combinations, CI workflow for matrix testing, manual validation script
- P6-04: End-to-end deployment validation (DevOps, L) - Comprehensive E2E test suite for Docker Compose and Kubernetes, CI workflow, manual validation checklist
- P6-05: Write release notes (Documentation, S) - CHANGELOG.md in Keep a Changelog format, detailed release notes, GitHub release template

---

### Complete Task Summary by Phase

**Phase 1: CI/CD Foundation (6 tasks)**
- P1-01: Create GitHub Actions CI workflow (DevOps, M)
- P1-02: Create GitHub Actions build workflow (DevOps, M)
- P1-03: Enhance production Dockerfiles (DevOps, S)
- P1-04: Configure Dependabot (DevOps, XS)
- P1-05: Configure Codecov integration (DevOps, S)
- P1-06: Write ADR-019: GitHub Actions CI/CD (Architecture, S)

**Phase 2: Security Hardening (8 tasks)**
- P2-01: Implement security headers middleware (Backend, M)
- P2-02: Add security configuration to config.py (Backend, S)
- P2-03: Add Trivy container scanning to CI (DevOps, S)
- P2-04: Add dependency vulnerability scanning (DevOps, S)
- P2-05: Configure gitleaks pre-commit hook (DevOps, S)
- P2-06: Create security audit checklist (Documentation, M)
- P2-07: Write ADR-020: Security Headers (Architecture, S)
- P2-08: Write ADR-022: Container Security Scanning (Architecture, S)

**Phase 3: Operational Readiness (11 tasks)**
- P3-01: Create Prometheus alerting rules (DevOps, M)
- P3-02: Update prometheus.yml with rule_files (DevOps, XS)
- P3-03: Implement optional Sentry integration (Backend, L)
- P3-04: Add Sentry cookiecutter conditional (DevOps, M)
- P3-05: Create database backup scripts (DevOps, M)
- P3-06: Create restore and recovery scripts (DevOps, M)
- P3-07: Create Kubernetes backup CronJob (DevOps, S)
- P3-08: Create operational runbook templates (Documentation, M)
- P3-09: Write point-in-time recovery documentation (Documentation, M)
- P3-10: Write ADR-023: Database Backup Strategy (Architecture, S)
- P3-11: Write ADR-024: Sentry Integration (Architecture, S)

**Phase 4: Kubernetes Deployment (8 tasks)**
- P4-01: Create Kubernetes base manifests (DevOps, L)
- P4-02: Create Kustomize staging overlay (DevOps, S)
- P4-03: Create Kustomize production overlay (DevOps, S)
- P4-04: Create GitHub Actions deploy workflow (DevOps, M)
- P4-05: Create production Docker Compose file (DevOps, S)
- P4-06: Add Kubernetes cookiecutter conditional (DevOps, M)
- P4-07: Document environment configuration (Documentation, M)
- P4-08: Write ADR-021: Kubernetes Deployment (Architecture, S)

**Phase 5: Developer Experience (5 tasks)**
- P5-01: Configure OpenAPI Generator for TypeScript (Frontend, M)
- P5-02: Create k6 load testing scripts (DevOps, M)
- P5-03: Create k6 authentication flow tests (DevOps, M)
- P5-04: Document API versioning strategy (Documentation, S)
- P5-05: Document performance baselines (Documentation, S)

**Phase 6: Documentation and Validation (5 tasks)**
- P6-01: Update CLAUDE.md with new features (Documentation, M)
- P6-02: Create migration guide for existing projects (Documentation, M)
- P6-03: Validate cookiecutter option combinations (DevOps, M)
- P6-04: End-to-end deployment validation (DevOps, L)
- P6-05: Write release notes (Documentation, S)

---

### Estimated Total Effort

**Total**: 10-11 weeks (43 tasks across 6 phases)

| Complexity | Count | Typical Duration |
|------------|-------|------------------|
| XS | 2 | 0.5 days each |
| S | 17 | 1 day each |
| M | 20 | 1-2 days each |
| L | 4 | 2-3 days each |

---

### Ready for Implementation

All 43 tasks are now fully documented and ready for domain agents to claim:

- **DevOps Agent**: 24 tasks ready
- **Backend Agent**: 3 tasks ready
- **Frontend Agent**: 1 task ready
- **Architecture Agent**: 7 tasks ready
- **Documentation Agent**: 8 tasks ready

Each task document includes:
- Clear scope and boundaries
- Dependencies and integration points
- Implementation details with code examples
- Success criteria and verification steps
- Quality gates
- Estimated effort

**The Production Essentials feature breakdown is COMPLETE.**
