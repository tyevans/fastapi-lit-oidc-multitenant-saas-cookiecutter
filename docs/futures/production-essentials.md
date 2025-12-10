# Production Essentials for Project Starter Template

**Date Created:** 2025-12-05
**Last Updated:** 2025-12-05
**Author/Agent:** FRD Builder Agent
**Status:** Ready for FRD Refiner - All Sections Complete

---

## Table of Contents

- [Problem Statement](#problem-statement) - COMPLETE
- [Goals & Success Criteria](#goals--success-criteria) - COMPLETE
- [Scope & Boundaries](#scope--boundaries) - COMPLETE
- [User Stories / Use Cases](#user-stories--use-cases) - COMPLETE
- [Functional Requirements](#functional-requirements) - COMPLETE
- [Technical Approach](#technical-approach) - COMPLETE
- [Architecture & Integration Considerations](#architecture--integration-considerations) - COMPLETE
- [Data Models & Schema Changes](#data-models--schema-changes) - COMPLETE
- [UI/UX Considerations](#uiux-considerations) - COMPLETE
- [Security & Privacy Considerations](#security--privacy-considerations) - COMPLETE
- [Testing Strategy](#testing-strategy) - COMPLETE
- [Implementation Phases](#implementation-phases) - COMPLETE
- [Dependencies & Risks](#dependencies--risks) - COMPLETE
- [Open Questions](#open-questions)
- [Status](#status)

---

## Problem Statement

### Current State Analysis

The project-starter template provides a robust foundation for building multi-tenant SaaS applications with OAuth 2.0 authentication. It includes:

**What Exists:**
- **Backend (FastAPI):** API routers for health, auth, OAuth, todos; JWT validation with JWKS caching; multi-tenant middleware; Row-Level Security enforcement; rate limiting via Redis; comprehensive configuration management
- **Frontend (Lit):** Web components for auth-callback, login-button, user-profile, todo-list, health-check; OIDC client integration with PKCE; API client with typed responses
- **Infrastructure:** Docker Compose orchestration for 10+ services; PostgreSQL with dual-user security model; Redis for caching and rate limiting; Keycloak for OAuth/OIDC
- **Observability (Optional):** Prometheus, Grafana, Loki, Tempo for metrics, logs, and traces
- **Testing:** Pytest for backend unit/integration tests; Vitest for frontend; Playwright for E2E/API testing
- **Documentation:** ADR records (18 documented decisions); component READMEs; CLAUDE.md for AI assistance

### Identified Gaps

Despite the comprehensive foundation, several production-essential features are missing or incomplete:

#### 1. **CI/CD Pipeline Configuration**
- No GitHub Actions, GitLab CI, or other CI/CD workflow definitions
- No automated testing on pull requests
- No deployment automation or staging/production environment configuration
- No container registry configuration for image publishing

#### 2. **Environment-Specific Configuration Management**
- Only `.env.example` exists with development defaults
- No production-ready configuration patterns
- No secrets management integration (e.g., Vault, AWS Secrets Manager, Doppler)
- No environment validation or configuration schema for production

#### 3. **Production Dockerfiles and Deployment Manifests**
- Dockerfiles exist but only with development targets
- No production-optimized multi-stage builds
- No Kubernetes manifests (Helm charts, Kustomize, raw YAML)
- No production compose file or Swarm configuration

#### 4. **Error Tracking and Alerting**
- Basic exception handlers exist but no integration with error tracking services
- No Sentry, Rollbar, or similar integration in template
- No alerting rules for Prometheus/Grafana
- No PagerDuty, OpsGenie, or notification channel setup

#### 5. **Database Backup and Recovery**
- No backup scripts or automation
- No point-in-time recovery configuration
- No database migration rollback documentation
- No disaster recovery procedures

#### 6. **API Versioning and Documentation Strategy**
- Single API version prefix exists (`/api/v1`)
- No API versioning strategy documentation
- No automated API changelog generation
- No API client SDK generation tooling

#### 7. **Performance and Load Testing**
- No load testing scripts (k6, Locust, Artillery)
- No performance benchmarks or baselines
- No capacity planning documentation

#### 8. **Security Hardening**
- No security headers middleware (CSP, HSTS, etc.)
- No dependency vulnerability scanning in template
- No SBOM (Software Bill of Materials) generation
- No security audit checklist or compliance documentation

#### 9. **User Management and Admin Features**
- Todos router is demo/example only (in-memory storage)
- No actual user management endpoints
- No admin dashboard or user administration UI
- No role/permission management beyond basic scopes

#### 10. **Background Jobs and Task Queue**
- No Celery, RQ, or async task queue integration
- No scheduled job configuration
- No email sending infrastructure
- No webhook handling patterns

### Business Impact

Without these essentials, teams using this template will need to:
1. Spend significant time implementing CI/CD from scratch
2. Risk security vulnerabilities due to missing hardening
3. Face production incidents without proper error tracking
4. Struggle with deployments lacking Kubernetes manifests
5. Encounter data loss risks without backup procedures

### User Pain Points

- **DevOps Engineers:** Cannot deploy the template to production without significant additional work
- **Security Teams:** Cannot approve production deployment without security hardening
- **Developers:** Must build common patterns (background jobs, emails) from scratch
- **Operations:** No runbooks or operational procedures for incident response

### Evidence from Codebase

From `template/{{cookiecutter.project_slug}}/backend/app/api/routers/todos.py`:
```python
# In-memory storage for demo purposes
# In a real app, this would use a database
_demo_todos: dict[str, dict] = { ... }
```

This comment explicitly acknowledges the example nature of the todos implementation, suggesting that production-ready entity management patterns are needed.

From `template/{{cookiecutter.project_slug}}/backend/Dockerfile` (target: development):
The Dockerfile only includes a development target, confirming the absence of production-ready container builds.

---

## Goals & Success Criteria

### Primary Goals

1. **Accelerate Time-to-Production**
   - Reduce the time from project generation to production deployment from weeks to days
   - Provide ready-to-use CI/CD pipelines that work out of the box
   - Include production-ready Dockerfile targets and deployment manifests

2. **Ensure Production-Grade Security**
   - Implement security headers and hardening best practices
   - Integrate dependency vulnerability scanning into the template
   - Provide security audit checklists and compliance documentation

3. **Enable Operational Excellence**
   - Include error tracking integration (configurable)
   - Provide database backup and recovery patterns
   - Create alerting rules and runbook templates

4. **Maintain Template Simplicity**
   - Keep additions optional where possible (following the observability pattern)
   - Ensure generated projects remain understandable and maintainable
   - Document all additions with ADRs

### Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Time to first deployment | < 2 hours from generation | Timed deployment exercise |
| CI/CD pipeline working | 100% on generation | Automated template tests |
| Security scan pass rate | 0 high/critical vulnerabilities | Trivy/Snyk scan on generated project |
| Documentation completeness | All features documented | Documentation review checklist |
| Template generation success | 100% with all option combinations | Matrix testing in CI |

### Success Indicators

**Short-term (1-2 months):**
- CI/CD workflows successfully run on first commit
- Production Dockerfiles build and pass security scans
- All new features have corresponding ADRs

**Medium-term (3-6 months):**
- At least 3 production deployments using the template
- Community feedback incorporated into improvements
- Load testing baselines established

**Long-term (6-12 months):**
- Template used as reference for security best practices
- Zero production incidents attributable to template gaps
- Kubernetes deployment patterns validated in production

### Non-Goals

- Creating a one-size-fits-all solution (options are preferred)
- Supporting every CI/CD platform (focus on GitHub Actions initially)
- Building a full admin dashboard (provide patterns, not complete implementation)
- Implementing every security framework compliance (provide foundation, not certification)

---

## Scope & Boundaries

### In Scope

**Phase 1 - CI/CD and Deployment Essentials:**
- GitHub Actions workflows (lint, test, build, deploy)
- Production-optimized multi-stage Dockerfiles
- Basic Kubernetes manifests (Deployment, Service, Ingress, ConfigMap, Secret)
- Container registry configuration (GitHub Container Registry)

**Phase 2 - Security Hardening:**
- Security headers middleware (CSP, HSTS, X-Frame-Options, etc.)
- Dependency vulnerability scanning (Trivy/Snyk integration in CI)
- Pre-commit hooks for secrets detection
- Security audit checklist document

**Phase 3 - Operational Readiness:**
- Error tracking integration (Sentry as optional dependency)
- Prometheus alerting rules and Grafana alert channels
- Database backup scripts and recovery documentation
- Operational runbook templates

**Phase 4 - Developer Experience:**
- API client SDK generation (OpenAPI Generator)
- Load testing scripts (k6)
- Performance benchmarking documentation
- API versioning strategy documentation

### Out of Scope

**Explicitly Excluded:**
- Full Helm chart with all configuration options (provide basic manifests)
- Multi-cloud deployment scripts (focus on Kubernetes-agnostic patterns)
- Complete admin dashboard implementation (provide API endpoints only)
- Celery/background job queue (large enough for separate FRD)
- Email sending infrastructure (large enough for separate FRD)
- Webhook handling patterns (can be added to separate FRD)
- Specific compliance certifications (SOC2, HIPAA, etc.)
- Auto-scaling configuration (document patterns only)

### Related Features (Separate FRDs)

The following should be addressed in dedicated FRDs:
- Background Jobs and Task Queue System
- Email/Notification Infrastructure
- Webhook Processing Patterns
- Complete Admin Dashboard
- Advanced Kubernetes Configuration (HPA, PDB, etc.)

---

## User Stories / Use Cases

### Personas

| Persona | Description | Primary Goals |
|---------|-------------|---------------|
| **Template User** | Developer adopting the template for a new project | Get to production quickly with confidence |
| **DevOps Engineer** | Engineer responsible for deployment and operations | Reliable, automated deployments with observability |
| **Security Engineer** | Engineer responsible for security posture | Confidence in security hardening and compliance |
| **Backend Developer** | Developer building features on the template | Clear patterns and working CI/CD |
| **Frontend Developer** | Developer building UI features | Fast iteration with automated quality checks |
| **SRE/Operator** | Engineer responsible for production reliability | Alerting, runbooks, and recovery procedures |

### Epic 1: CI/CD Pipeline Setup

**US-1.1: Automated Testing on Pull Requests**
> As a **Backend Developer**, I want my pull requests to automatically run tests so that I can catch regressions before merging.

**Acceptance Criteria:**
- GitHub Actions workflow triggers on PR to main/develop branches
- Backend pytest suite runs with coverage reporting
- Frontend vitest suite runs
- Linting (ruff, eslint) runs and fails on violations
- Test results visible in PR checks
- Coverage badge updates automatically

**US-1.2: Automated Container Builds**
> As a **DevOps Engineer**, I want container images to be built and pushed automatically so that I have versioned, deployable artifacts.

**Acceptance Criteria:**
- Docker images build on merge to main
- Images tagged with git SHA, semantic version, and `latest`
- Images pushed to GitHub Container Registry (ghcr.io)
- Multi-platform builds (linux/amd64, linux/arm64)
- Build artifacts include SBOM for security scanning

**US-1.3: Deployment Automation**
> As a **DevOps Engineer**, I want deployments to staging and production to be automated so that releases are consistent and auditable.

**Acceptance Criteria:**
- Staging deploys automatically on merge to main
- Production deploys via manual approval or tag
- Kubernetes manifests applied via GitHub Actions
- Deployment status reported back to GitHub
- Rollback procedure documented and testable

### Epic 2: Security Hardening

**US-2.1: Security Headers Configuration**
> As a **Security Engineer**, I want the application to serve proper security headers so that common web vulnerabilities are mitigated.

**Acceptance Criteria:**
- Content-Security-Policy (CSP) header configured
- Strict-Transport-Security (HSTS) header enabled
- X-Frame-Options set to DENY or SAMEORIGIN
- X-Content-Type-Options set to nosniff
- Referrer-Policy configured appropriately
- Headers are configurable via environment variables

**US-2.2: Dependency Vulnerability Scanning**
> As a **Security Engineer**, I want dependencies scanned for known vulnerabilities so that I can address security issues proactively.

**Acceptance Criteria:**
- Trivy or Snyk runs in CI on every PR
- Container images scanned for OS and library vulnerabilities
- Python dependencies scanned via safety or pip-audit
- npm dependencies scanned via npm audit
- High/critical vulnerabilities fail the build
- SBOM generated and stored with each release

**US-2.3: Secrets Detection**
> As a **Security Engineer**, I want secrets detected before they reach the repository so that credentials are not accidentally exposed.

**Acceptance Criteria:**
- Pre-commit hook with detect-secrets or gitleaks
- CI job validates no secrets in codebase
- Documentation on handling false positives
- .secrets.baseline file for managing exceptions

**US-2.4: Security Audit Checklist**
> As a **Security Engineer**, I want a security audit checklist so that I can verify the application meets security requirements before production.

**Acceptance Criteria:**
- Comprehensive checklist covering OWASP Top 10
- Sections for authentication, authorization, data protection
- Environment-specific considerations
- Links to relevant documentation and ADRs

### Epic 3: Operational Readiness

**US-3.1: Error Tracking Integration**
> As an **SRE/Operator**, I want unhandled exceptions reported to an error tracking service so that I can respond to production issues quickly.

**Acceptance Criteria:**
- Sentry integration as optional dependency
- Automatic exception capture with stack traces
- User context (tenant_id, user_id) attached to errors
- Release tracking for regression detection
- Environment separation (staging/production)

**US-3.2: Alerting Rules Configuration**
> As an **SRE/Operator**, I want preconfigured alerting rules so that I am notified of issues before users report them.

**Acceptance Criteria:**
- Prometheus alerting rules for key metrics
- High error rate alerts (5xx > 1% for 5 minutes)
- High latency alerts (p95 > 2s for 5 minutes)
- Database connection pool exhaustion alerts
- Redis connection failure alerts
- Grafana notification channels configured (webhook template)

**US-3.3: Database Backup and Recovery**
> As an **SRE/Operator**, I want automated database backups so that I can recover from data loss incidents.

**Acceptance Criteria:**
- Backup script using pg_dump or pg_basebackup
- Cron job configuration for scheduled backups
- Backup retention policy (7 daily, 4 weekly, 12 monthly)
- Point-in-time recovery documentation
- Restoration testing procedure
- Backup monitoring and alerting

**US-3.4: Operational Runbooks**
> As an **SRE/Operator**, I want operational runbooks so that I can respond to incidents consistently and effectively.

**Acceptance Criteria:**
- Runbook template with standard sections
- Common incident runbooks (database recovery, scaling, restarts)
- Escalation procedures documented
- Contact information and on-call procedures
- Post-incident review template

### Epic 4: Deployment Configuration

**US-4.1: Production Kubernetes Manifests**
> As a **DevOps Engineer**, I want Kubernetes manifests so that I can deploy the application to any Kubernetes cluster.

**Acceptance Criteria:**
- Deployment manifests for backend and frontend
- Service definitions with proper port mapping
- Ingress configuration with TLS termination
- ConfigMap for environment-specific configuration
- Secret references (not values) for sensitive data
- Resource requests and limits defined
- Health check probes (liveness, readiness) configured

**US-4.2: Environment Configuration Management**
> As a **DevOps Engineer**, I want clear environment configuration patterns so that I can manage staging and production safely.

**Acceptance Criteria:**
- Environment-specific configuration files/patterns
- Documentation on required vs optional variables
- Configuration schema validation
- Secrets management integration examples (Vault, AWS SM)
- Environment variable injection for Kubernetes

**US-4.3: Production Docker Compose**
> As a **Template User**, I want a production-ready Docker Compose file so that I can deploy without Kubernetes initially.

**Acceptance Criteria:**
- Separate `compose.production.yml` file
- Production targets used for images
- External database/Redis connection support
- Proper resource limits defined
- No development volumes mounted
- Environment file template for production

### Epic 5: Developer Experience

**US-5.1: API Client SDK Generation**
> As a **Frontend Developer**, I want auto-generated TypeScript API clients so that I can integrate with the backend type-safely.

**Acceptance Criteria:**
- OpenAPI Generator configured in CI
- TypeScript client generated from openapi.json
- Client published to npm or included in frontend
- Generation runs on API changes
- Breaking change detection in CI

**US-5.2: Load Testing Scripts**
> As a **DevOps Engineer**, I want load testing scripts so that I can validate performance before production releases.

**Acceptance Criteria:**
- k6 test scripts for key API endpoints
- Authentication flow testing
- Configurable virtual users and duration
- Performance baseline documented
- CI integration for regression testing

**US-5.3: API Versioning Documentation**
> As a **Backend Developer**, I want clear API versioning guidelines so that I can evolve the API without breaking clients.

**Acceptance Criteria:**
- Versioning strategy documented (URL path vs header)
- Deprecation policy defined
- Breaking change criteria documented
- Client migration guide template
- Changelog generation from commits/PRs

### Edge Cases and Error Scenarios

**EC-1: CI/CD Failure Recovery**
- Pipeline fails mid-deployment: Manual rollback documented, partial state handled
- Container registry unavailable: Retry logic, fallback to previous image
- Test flakiness: Retry policy, flaky test quarantine

**EC-2: Security Incident Response**
- Credential exposure detected: Rotation procedure, audit trail
- Vulnerability discovered in production: Hotfix deployment path
- DDoS or abuse: Rate limiting escalation, IP blocking

**EC-3: Operational Failures**
- Database connection exhaustion: Alert triggers, connection pool tuning guide
- Redis failure: Graceful degradation, cache bypass
- Certificate expiration: Monitoring, renewal automation

**EC-4: Data Recovery Scenarios**
- Accidental data deletion: Point-in-time recovery procedure
- Corrupted migration: Rollback procedure, data verification
- Cross-tenant data leak (RLS failure): Detection, containment, audit

---

## Functional Requirements

Requirements are organized by category and prioritized using MoSCoW method:
- **M** = Must Have (critical for production readiness)
- **S** = Should Have (important but not blocking)
- **C** = Could Have (nice to have, can defer)

### CI/CD Pipeline Requirements

| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-CI-001 | GitHub Actions workflow shall trigger on pull requests to main and develop branches | M | US-1.1 |
| FR-CI-002 | CI pipeline shall execute backend pytest suite and report results | M | US-1.1 |
| FR-CI-003 | CI pipeline shall execute frontend vitest suite and report results | M | US-1.1 |
| FR-CI-004 | CI pipeline shall run ruff linter on backend code and fail on violations | M | US-1.1 |
| FR-CI-005 | CI pipeline shall run eslint on frontend code and fail on violations | M | US-1.1 |
| FR-CI-006 | CI pipeline shall generate and upload test coverage reports | S | US-1.1 |
| FR-CI-007 | Docker images shall be built on merge to main branch | M | US-1.2 |
| FR-CI-008 | Docker images shall be tagged with git SHA, version tag if present, and `latest` | M | US-1.2 |
| FR-CI-009 | Docker images shall be pushed to GitHub Container Registry (ghcr.io) | M | US-1.2 |
| FR-CI-010 | Docker builds shall support multi-platform (linux/amd64, linux/arm64) | S | US-1.2 |
| FR-CI-011 | CI pipeline shall generate SBOM for container images using Syft or Trivy | S | US-1.2, US-2.2 |
| FR-CI-012 | Staging environment shall deploy automatically on merge to main | S | US-1.3 |
| FR-CI-013 | Production deployment shall require manual approval or semantic version tag | M | US-1.3 |
| FR-CI-014 | Deployment workflow shall apply Kubernetes manifests via kubectl or kustomize | S | US-1.3 |
| FR-CI-015 | Deployment status shall be reported back to GitHub as deployment status | S | US-1.3 |

### Security Requirements

| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-SEC-001 | Backend shall add Content-Security-Policy header to all responses | M | US-2.1 |
| FR-SEC-002 | Backend shall add Strict-Transport-Security header when HTTPS is detected | M | US-2.1 |
| FR-SEC-003 | Backend shall add X-Frame-Options header set to DENY | M | US-2.1 |
| FR-SEC-004 | Backend shall add X-Content-Type-Options header set to nosniff | M | US-2.1 |
| FR-SEC-005 | Backend shall add Referrer-Policy header set to strict-origin-when-cross-origin | S | US-2.1 |
| FR-SEC-006 | Security headers shall be configurable via environment variables | S | US-2.1 |
| FR-SEC-007 | CI pipeline shall scan container images for vulnerabilities using Trivy | M | US-2.2 |
| FR-SEC-008 | CI pipeline shall scan Python dependencies using pip-audit or safety | M | US-2.2 |
| FR-SEC-009 | CI pipeline shall scan npm dependencies using npm audit | M | US-2.2 |
| FR-SEC-010 | CI pipeline shall fail if HIGH or CRITICAL vulnerabilities are found | M | US-2.2 |
| FR-SEC-011 | Pre-commit configuration shall include secret detection using gitleaks | M | US-2.3 |
| FR-SEC-012 | CI pipeline shall validate no secrets are present in codebase | S | US-2.3 |
| FR-SEC-013 | Template shall include security audit checklist document covering OWASP Top 10 | S | US-2.4 |
| FR-SEC-014 | Security checklist shall reference relevant ADRs and documentation | C | US-2.4 |

### Operational Requirements

| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-OPS-001 | Template shall include optional Sentry SDK integration in backend | S | US-3.1 |
| FR-OPS-002 | Sentry integration shall capture unhandled exceptions with stack traces | S | US-3.1 |
| FR-OPS-003 | Sentry integration shall attach tenant_id and user_id context to errors | S | US-3.1 |
| FR-OPS-004 | Sentry release tracking shall be configured in CI/CD pipeline | C | US-3.1 |
| FR-OPS-005 | Prometheus alerting rules file shall be included in observability stack | M | US-3.2 |
| FR-OPS-006 | Alert rule shall trigger on HTTP 5xx error rate > 1% for 5 minutes | M | US-3.2 |
| FR-OPS-007 | Alert rule shall trigger on p95 latency > 2 seconds for 5 minutes | M | US-3.2 |
| FR-OPS-008 | Alert rule shall trigger on database connection pool exhaustion | S | US-3.2 |
| FR-OPS-009 | Alert rule shall trigger on Redis connection failures | S | US-3.2 |
| FR-OPS-010 | Grafana alerting notification channel template shall be included | S | US-3.2 |
| FR-OPS-011 | Database backup script using pg_dump shall be included | M | US-3.3 |
| FR-OPS-012 | Backup script shall support configurable retention policy | S | US-3.3 |
| FR-OPS-013 | Point-in-time recovery documentation shall be included | S | US-3.3 |
| FR-OPS-014 | Database restoration procedure shall be documented and tested | M | US-3.3 |
| FR-OPS-015 | Operational runbook template shall be included | S | US-3.4 |
| FR-OPS-016 | Runbooks shall include: database recovery, scaling, restart procedures | S | US-3.4 |
| FR-OPS-017 | Post-incident review template shall be included | C | US-3.4 |

### Deployment Configuration Requirements

| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-DEP-001 | Kubernetes Deployment manifest shall be included for backend service | M | US-4.1 |
| FR-DEP-002 | Kubernetes Deployment manifest shall be included for frontend service | M | US-4.1 |
| FR-DEP-003 | Kubernetes Service manifests shall expose backend on port 8000 | M | US-4.1 |
| FR-DEP-004 | Kubernetes Service manifests shall expose frontend on port 80 | M | US-4.1 |
| FR-DEP-005 | Kubernetes Ingress manifest shall include TLS configuration template | S | US-4.1 |
| FR-DEP-006 | Kubernetes ConfigMap shall externalize non-sensitive configuration | M | US-4.1 |
| FR-DEP-007 | Kubernetes manifests shall reference Secrets for sensitive values | M | US-4.1 |
| FR-DEP-008 | Deployment manifests shall define resource requests and limits | M | US-4.1 |
| FR-DEP-009 | Deployment manifests shall configure liveness and readiness probes | M | US-4.1 |
| FR-DEP-010 | Environment configuration documentation shall list required variables | M | US-4.2 |
| FR-DEP-011 | Environment configuration documentation shall list optional variables with defaults | S | US-4.2 |
| FR-DEP-012 | Secrets management examples shall be documented for Vault and AWS SM | C | US-4.2 |
| FR-DEP-013 | Production compose file (compose.production.yml) shall be included | S | US-4.3 |
| FR-DEP-014 | Production compose file shall use production Docker targets | M | US-4.3 |
| FR-DEP-015 | Production compose file shall not mount development volumes | M | US-4.3 |
| FR-DEP-016 | Production compose file shall support external database connection | S | US-4.3 |

### Developer Experience Requirements

| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| FR-DX-001 | OpenAPI Generator configuration shall be included for TypeScript client | S | US-5.1 |
| FR-DX-002 | TypeScript client generation shall run in CI on API changes | C | US-5.1 |
| FR-DX-003 | Breaking API change detection shall be implemented in CI | C | US-5.1 |
| FR-DX-004 | k6 load testing scripts shall be included for key endpoints | S | US-5.2 |
| FR-DX-005 | Load testing scripts shall test authentication flow | S | US-5.2 |
| FR-DX-006 | Load testing scripts shall be configurable for virtual users and duration | S | US-5.2 |
| FR-DX-007 | Performance baseline documentation shall be included | C | US-5.2 |
| FR-DX-008 | API versioning strategy shall be documented | S | US-5.3 |
| FR-DX-009 | API deprecation policy shall be documented | S | US-5.3 |
| FR-DX-010 | Breaking change criteria shall be documented | S | US-5.3 |

### Non-Functional Requirements

| ID | Requirement | Priority | Traceability |
|----|-------------|----------|--------------|
| NFR-001 | All new features shall have corresponding ADR documentation | M | Goals |
| NFR-002 | Template generation shall succeed for all option combinations | M | Goals |
| NFR-003 | Production Dockerfiles shall pass Trivy security scan with no HIGH/CRITICAL | M | Goals |
| NFR-004 | CI pipeline shall complete in under 10 minutes for typical PR | S | Goals |
| NFR-005 | All additions shall follow existing codebase patterns and conventions | M | Goals |
| NFR-006 | Optional features shall follow the observability pattern (include_X cookiecutter variable) | S | Goals |

### Requirements Summary

| Category | Must Have | Should Have | Could Have | Total |
|----------|-----------|-------------|------------|-------|
| CI/CD Pipeline | 8 | 7 | 0 | 15 |
| Security | 7 | 5 | 2 | 14 |
| Operational | 5 | 9 | 3 | 17 |
| Deployment | 9 | 5 | 2 | 16 |
| Developer Experience | 0 | 7 | 3 | 10 |
| Non-Functional | 3 | 2 | 1 | 6 |
| **Total** | **32** | **35** | **11** | **78** |

---

## Technical Approach

### Guiding Principles

1. **Follow Existing Patterns**: All additions must follow established template patterns, particularly the cookiecutter conditional pattern used for observability (ADR-017)
2. **Minimal Footprint**: Production essentials should be lightweight and not add excessive complexity
3. **Fail-Open Design**: Production services should not block core application functionality
4. **Configuration over Code**: Prefer configuration files and environment variables over hardcoded values
5. **Documentation First**: Every feature must have corresponding ADR and usage documentation

### Technology Stack

#### CI/CD Platform: GitHub Actions

**Rationale:**
- Native integration with GitHub repositories (primary target)
- Free for open source, generous free tier for private repos
- Extensive marketplace of reusable actions
- Matrix builds for template option combinations
- Built-in secrets management
- Deployment environments with protection rules

**Key Actions to Leverage:**
- `actions/checkout@v4` - Repository checkout
- `actions/setup-python@v5` - Python environment
- `actions/setup-node@v4` - Node.js environment
- `docker/setup-buildx-action@v3` - Multi-platform Docker builds
- `docker/login-action@v3` - Container registry authentication
- `docker/build-push-action@v6` - Build and push images
- `aquasecurity/trivy-action@master` - Container vulnerability scanning
- `azure/k8s-deploy@v5` - Kubernetes deployment (optional)

#### Container Registry: GitHub Container Registry (ghcr.io)

**Rationale:**
- Free for public packages
- Native GitHub integration (no additional authentication)
- Supports multi-platform images
- Visibility tied to repository permissions
- Already used by many open-source projects

#### Security Scanning Tools

| Tool | Purpose | Integration |
|------|---------|-------------|
| **Trivy** | Container image and filesystem scanning | CI action, pre-commit |
| **pip-audit** | Python dependency vulnerabilities | CI action |
| **npm audit** | Node.js dependency vulnerabilities | CI action (built-in) |
| **gitleaks** | Secret detection | Pre-commit hook, CI action |
| **Syft** | SBOM generation | CI action (with Trivy) |

#### Kubernetes: Plain Manifests with Kustomize

**Rationale:**
- No Helm complexity for simple deployments
- Kustomize is built into kubectl
- Environment overlays (base, staging, production)
- Easier to understand for teams new to Kubernetes
- Can be upgraded to Helm later if needed

**Structure:**
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

#### Error Tracking: Sentry (Optional)

**Rationale:**
- Industry standard for error tracking
- Excellent Python SDK (sentry-sdk)
- Free tier suitable for development and small projects
- Self-hosted option available
- Integrates with existing observability stack

**Integration Pattern:**
```python
{% if cookiecutter.include_sentry == "yes" %}
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENV,
    release=settings.APP_VERSION,
    integrations=[
        FastApiIntegration(transaction_style="url"),
        SqlalchemyIntegration(),
    ],
    traces_sample_rate=0.1,
)
{% endif %}
```

#### Load Testing: k6

**Rationale:**
- Modern, JavaScript-based scripting
- Low resource consumption
- Built-in thresholds and checks
- Good integration with Grafana (optional)
- Can run in CI without special infrastructure
- Supports WebSocket and gRPC

### Implementation Strategies

#### Strategy 1: CI/CD Workflow Files

**Approach:** Add GitHub Actions workflow files to the template

**Files to Create:**
```
.github/
  workflows/
    ci.yml           # PR checks (lint, test)
    build.yml        # Container builds on main
    deploy.yml       # Deployment workflows
    security.yml     # Security scanning
    release.yml      # Semantic release handling
  dependabot.yml     # Automated dependency updates
```

**CI Workflow Structure (ci.yml):**
```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '{{ cookiecutter.python_version }}'
      - run: pip install ruff
      - run: ruff check backend/

  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:{{ cookiecutter.postgres_version }}-alpine
        # ... service configuration
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install uv && uv sync
      - run: pytest --cov=app
      - uses: codecov/codecov-action@v4

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm test
```

#### Strategy 2: Security Headers Middleware

**Approach:** Create a configurable security headers middleware

**File:** `backend/app/middleware/security_headers.py`

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = settings.X_FRAME_OPTIONS
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # CSP (configurable)
        if settings.CSP_POLICY:
            response.headers["Content-Security-Policy"] = settings.CSP_POLICY

        # HSTS (only for HTTPS)
        if request.url.scheme == "https" or settings.FORCE_HSTS:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.HSTS_MAX_AGE}; includeSubDomains"
            )

        return response
```

**Configuration additions to `config.py`:**
```python
# Security Headers
X_FRAME_OPTIONS: str = "DENY"
CSP_POLICY: str = "default-src 'self'; script-src 'self' 'unsafe-inline'"
FORCE_HSTS: bool = False
HSTS_MAX_AGE: int = 31536000  # 1 year
```

#### Strategy 3: Prometheus Alerting Rules

**Approach:** Add alerting rules configuration to observability stack

**File:** `observability/prometheus/alerts.yml`

```yaml
groups:
  - name: backend_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          (sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m]))) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 1% for 5 minutes"

      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "95th percentile latency is above 2 seconds"

      - alert: DatabaseConnectionPoolExhausted
        expr: pg_stat_activity_count >= pg_settings_max_connections * 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool near exhaustion"
```

#### Strategy 4: Database Backup Scripts

**Approach:** Shell scripts with configurable retention

**File:** `scripts/backup-db.sh`

```bash
#!/bin/bash
set -euo pipefail

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"

# Create backup
pg_dump -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" | gzip > "$BACKUP_FILE"

# Cleanup old backups
find "$BACKUP_DIR" -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_FILE"
```

**Kubernetes CronJob:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: backup
              image: postgres:{{ cookiecutter.postgres_version }}-alpine
              command: ["/scripts/backup-db.sh"]
              volumeMounts:
                - name: backup-storage
                  mountPath: /backups
              envFrom:
                - secretRef:
                    name: database-credentials
```

#### Strategy 5: Pre-commit Configuration

**Approach:** Extend existing pre-commit configuration

**File:** `.pre-commit-config.yaml` (additions)

```yaml
repos:
  # Existing repos...

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

### Cookiecutter Integration

Following the observability pattern (ADR-017), new optional features use cookiecutter conditionals:

**New cookiecutter.json variables:**
```json
{
  "include_sentry": "no",
  "include_github_actions": "yes",
  "include_kubernetes": "no",
  "sentry_dsn": ""
}
```

**Conditional file inclusion:**
```
{% if cookiecutter.include_github_actions == "yes" %}
.github/
  workflows/
    ci.yml
    build.yml
    ...
{% endif %}

{% if cookiecutter.include_kubernetes == "yes" %}
k8s/
  base/
  overlays/
{% endif %}
```

### Integration Points with Existing Codebase

| Component | Integration Point | Changes Required |
|-----------|-------------------|------------------|
| Security Headers | `main.py` | Add middleware after CORS |
| Sentry | `main.py`, `config.py` | Conditional init, new settings |
| Alerting Rules | `prometheus.yml` | Add rule_files reference |
| Backup Scripts | `scripts/` | New script, CronJob manifest |
| Pre-commit | `.pre-commit-config.yaml` | Add gitleaks hook |
| CI/CD | `.github/workflows/` | New workflow files |
| K8s Manifests | `k8s/` | New directory structure |

### Migration Path for Existing Projects

For projects already generated from the template:

1. **CI/CD Workflows**: Copy `.github/workflows/` from a fresh template generation
2. **Security Headers**: Add middleware file and update `main.py`
3. **Kubernetes**: Copy `k8s/` directory and customize
4. **Sentry**: Add dependency and integration code

**Documentation to provide:**
- Migration checklist for each feature
- Diff examples showing required changes
- Version compatibility matrix

---

## Architecture & Integration Considerations

### System Architecture Overview

```
                                    ┌─────────────────────────────────────────────────────────────────┐
                                    │                     GitHub Actions CI/CD                        │
                                    │  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌─────────────────┐    │
                                    │  │  Lint   │  │  Test   │  │  Build   │  │ Security Scan   │    │
                                    │  └────┬────┘  └────┬────┘  └────┬─────┘  └────────┬────────┘    │
                                    │       └────────────┴───────────┬┴─────────────────┘             │
                                    └────────────────────────────────┼─────────────────────────────────┘
                                                                     │
                                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                        Container Registry (ghcr.io)                                     │
│                              ┌─────────────────────┐  ┌─────────────────────┐                           │
│                              │ backend:sha-xxx     │  │ frontend:sha-xxx    │                           │
│                              │ backend:v1.0.0      │  │ frontend:v1.0.0     │                           │
│                              └─────────────────────┘  └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                                     │
                              ┌──────────────────────────────────────┼───────────────────────────────┐
                              │                        Kubernetes Cluster                            │
                              │   ┌─────────────────────────────────┐│                               │
                              │   │           Ingress               ││                               │
                              │   │    (TLS Termination, Routing)   ││                               │
                              │   └──────────────┬──────────────────┘│                               │
                              │                  │                   │                               │
                              │      ┌───────────┴───────────┐       │                               │
                              │      ▼                       ▼       │                               │
                              │ ┌──────────┐           ┌──────────┐  │                               │
                              │ │ Frontend │           │ Backend  │  │                               │
                              │ │ Service  │           │ Service  │  │                               │
                              │ └────┬─────┘           └────┬─────┘  │                               │
                              │      │                      │        │                               │
                              │ ┌────┴─────┐           ┌────┴─────┐  │                               │
                              │ │ Frontend │           │ Backend  │  │   ┌────────────────────────┐  │
                              │ │ Pods     │           │ Pods     │◄─┼──►│    ConfigMap/Secrets   │  │
                              │ │ (nginx)  │           │ (uvicorn)│  │   └────────────────────────┘  │
                              │ └──────────┘           └────┬─────┘  │                               │
                              │                             │        │                               │
                              └─────────────────────────────┼────────┴───────────────────────────────┘
                                                            │
                              ┌──────────────────────────────────────────────────────────────────────┐
                              │                       External Services                              │
                              │   ┌────────────┐   ┌────────────┐   ┌────────────┐  ┌────────────┐   │
                              │   │ PostgreSQL │   │   Redis    │   │  Keycloak  │  │   Sentry   │   │
                              │   │ (Managed)  │   │ (Managed)  │   │ (Self/SaaS)│  │ (Optional) │   │
                              │   └────────────┘   └────────────┘   └────────────┘  └────────────┘   │
                              └──────────────────────────────────────────────────────────────────────┘
```

### Component Interactions

#### 1. CI/CD Pipeline Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   PR Open    │────►│   CI Jobs    │────►│ Security     │────►│ Merge Ready  │
│              │     │ (lint, test) │     │ Scan         │     │              │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                       │
                                                                       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Production   │◄────│  Manual      │◄────│ Staging      │◄────│ Merge to     │
│ Deploy       │     │  Approval    │     │ Deploy       │     │ Main         │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

#### 2. Security Headers Middleware Chain

```
Request ──► CORS Middleware ──► Tenant Middleware ──► Security Headers ──► Route Handler
                                                              │
                                                              ▼
                                                     Response Headers:
                                                     - Content-Security-Policy
                                                     - Strict-Transport-Security
                                                     - X-Frame-Options
                                                     - X-Content-Type-Options
                                                     - Referrer-Policy
```

#### 3. Error Tracking Flow (with Sentry)

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────┐
│ Unhandled   │────►│ Exception       │────►│ Sentry SDK  │
│ Exception   │     │ Handler         │     │ Capture     │
└─────────────┘     └─────────────────┘     └──────┬──────┘
                                                   │
                           ┌───────────────────────┴───────────────────────┐
                           │                   Sentry                       │
                           │  ┌─────────────┐  ┌─────────────┐  ┌────────┐  │
                           │  │ Stack Trace │  │ User Context│  │ Tags   │  │
                           │  │ - tenant_id │  │ - user_id   │  │ - env  │  │
                           │  │ - request   │  │ - email     │  │ - ver  │  │
                           │  └─────────────┘  └─────────────┘  └────────┘  │
                           └───────────────────────────────────────────────┘
```

#### 4. Alerting Pipeline (Observability Stack)

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Backend       │────►│ Prometheus    │────►│ Alert         │────►│ Alert Manager │
│ /metrics      │     │ Scrape        │     │ Rules         │     │ (Optional)    │
└───────────────┘     └───────────────┘     └───────────────┘     └───────┬───────┘
                                                                          │
                      ┌───────────────────────────────────────────────────┴─────┐
                      │                     Notification Channels               │
                      │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
                      │  │  Slack   │  │  Email   │  │ PagerDuty│  │ Webhook  │  │
                      │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
                      └─────────────────────────────────────────────────────────┘
```

### API Contract Specifications

#### Security Headers Response

All API responses will include these headers (when SecurityHeadersMiddleware is enabled):

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
Strict-Transport-Security: max-age=31536000; includeSubDomains  # HTTPS only
```

#### Health Check Endpoints

**Kubernetes Probes:**

```yaml
# Liveness probe - is the process alive?
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 30

# Readiness probe - is the service ready to accept traffic?
readinessProbe:
  httpGet:
    path: /api/v1/health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
```

**Required Health Endpoints:**

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `GET /api/v1/health` | Basic liveness | `{"status": "healthy"}` |
| `GET /api/v1/health/ready` | Readiness (DB, Redis) | `{"status": "ready", "database": "ok", "redis": "ok"}` |
| `GET /metrics` | Prometheus metrics | Prometheus text format |

### Integration with Existing Services

#### Database (PostgreSQL)

**No schema changes required.** Production essentials integrate at the application layer.

**Backup Integration:**
- Backup scripts use existing `POSTGRES_*` environment variables
- Compatible with RLS model (backups use migration user with BYPASSRLS)
- Point-in-time recovery requires WAL archiving (infrastructure concern)

#### Redis

**No configuration changes required.** Existing connection patterns work.

**Rate Limiting Enhancements:**
- Security scanning endpoints may need separate rate limits
- Consider dedicated Redis DB for production metrics (optional)

#### Keycloak

**No changes required.** Existing OAuth flow remains unchanged.

**Production Considerations:**
- Document external Keycloak setup for production
- Include ingress configuration for Keycloak if self-hosted in K8s

#### Observability Stack

**Alerting Rules Integration:**

Modify `observability/prometheus/prometheus.yml`:
```yaml
rule_files:
  - /etc/prometheus/alerts.yml  # Add this line

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093  # Optional external alertmanager
```

### Data Flow Diagrams

#### Deployment Data Flow

```
                    ┌──────────────────────────────────────────────────────────────┐
                    │                    GitHub Repository                         │
                    │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐   │
                    │  │ Source Code │  │ Dockerfile  │  │ K8s Manifests       │   │
                    │  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘   │
                    └─────────┼────────────────┼────────────────────┼──────────────┘
                              │                │                    │
                              ▼                ▼                    │
                    ┌─────────────────────────────────────┐         │
                    │        GitHub Actions Runner         │         │
                    │  ┌─────────┐ ┌─────────┐ ┌────────┐ │         │
                    │  │ Test    │ │ Build   │ │ Push   │ │         │
                    │  └────┬────┘ └────┬────┘ └───┬────┘ │         │
                    └───────┼───────────┼──────────┼──────┘         │
                            │           │          │                 │
                            ▼           ▼          ▼                 ▼
                    ┌────────────┐ ┌────────────────┐ ┌────────────────────┐
                    │ Test       │ │ Container      │ │ kubectl apply      │
                    │ Results    │ │ Registry       │ │ -k overlays/prod   │
                    └────────────┘ └────────────────┘ └────────────────────┘
```

### Performance Considerations

#### CI/CD Pipeline Performance

| Stage | Target Duration | Optimization Strategy |
|-------|-----------------|----------------------|
| Checkout | < 30s | Shallow clone, sparse checkout |
| Dependencies | < 2min | Dependency caching, uv/npm ci |
| Lint | < 1min | Ruff (fast), parallel jobs |
| Backend Tests | < 5min | Parallel test execution |
| Frontend Tests | < 3min | Vitest (fast) |
| Docker Build | < 5min | Layer caching, BuildKit |
| Security Scan | < 2min | Trivy with cache |
| **Total** | **< 10min** | Parallel job execution |

#### Runtime Performance Impact

| Component | Overhead | Mitigation |
|-----------|----------|------------|
| Security Headers Middleware | < 1ms/request | No external calls, header-only |
| Sentry SDK | 1-5ms/error | Async capture, sampling |
| Prometheus Metrics | < 1ms/request | In-memory, async scrape |

#### Resource Requirements (Kubernetes)

**Backend Pod:**
```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

**Frontend Pod:**
```yaml
resources:
  requests:
    cpu: 50m
    memory: 64Mi
  limits:
    cpu: 200m
    memory: 128Mi
```

### Scalability Requirements

#### Horizontal Scaling

**Backend:**
- Stateless design (no session affinity required)
- Scale via Kubernetes HPA on CPU/memory
- Database connection pool limits must scale with replicas

**Frontend:**
- Static assets, easily scalable
- CDN recommended for production

#### Vertical Scaling Points

- **Database connections**: Monitor pool exhaustion
- **Redis connections**: Monitor connection limits
- **Sentry rate limits**: Monitor quota usage

### Cross-Component Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            Dependency Matrix                                     │
├─────────────────────┬──────────┬───────┬──────────┬───────┬─────────┬──────────┤
│ Component           │ Postgres │ Redis │ Keycloak │ Sentry│ Prometheus│ Grafana │
├─────────────────────┼──────────┼───────┼──────────┼───────┼─────────┼──────────┤
│ Backend             │ Required │ Req   │ Required │ Opt   │ Opt     │ N/A      │
│ Frontend            │ N/A      │ N/A   │ N/A      │ Opt   │ N/A     │ N/A      │
│ CI Pipeline         │ N/A      │ N/A   │ N/A      │ N/A   │ N/A     │ N/A      │
│ Alerting            │ N/A      │ N/A   │ N/A      │ N/A   │ Req     │ Opt      │
│ Backup CronJob      │ Required │ N/A   │ N/A      │ N/A   │ N/A     │ N/A      │
└─────────────────────┴──────────┴───────┴──────────┴───────┴─────────┴──────────┘

Legend: Req = Required, Opt = Optional, N/A = Not Applicable
```

### Failure Mode Analysis

| Failure | Impact | Mitigation | Recovery |
|---------|--------|------------|----------|
| CI runner unavailable | Builds blocked | GitHub-hosted runners as fallback | Auto-retry |
| Container registry down | Deployments blocked | Cache last good image locally | Manual cache |
| Sentry unavailable | No error tracking | Fail-open (no app impact) | Auto-reconnect |
| Alerting rules misconfigured | Missed alerts | CI validation of rules | Config rollback |
| Backup job fails | Potential data loss | Alert on failure, retry | Manual backup |

### ADR Requirements

The following ADRs should be created during implementation:

| ADR | Topic | Key Decisions |
|-----|-------|--------------|
| ADR-019 | GitHub Actions CI/CD | Workflow structure, caching strategy, secrets handling |
| ADR-020 | Security Headers | Header selection, CSP policy defaults |
| ADR-021 | Kubernetes Deployment | Manifest structure, Kustomize vs Helm decision |
| ADR-022 | Container Security Scanning | Tool selection (Trivy), threshold policies |
| ADR-023 | Database Backup Strategy | Backup frequency, retention, recovery procedures |
| ADR-024 | Optional Sentry Integration | Integration pattern, sampling rates |

---

## Data Models & Schema Changes

### Overview

The Production Essentials feature is primarily focused on CI/CD pipelines, deployment configurations, security hardening, and operational tooling. As such, **no database schema changes are required** for the core functionality.

The existing schema (tenants, users, oauth_providers with RLS policies) remains unchanged and fully supports all proposed production enhancements.

### Existing Schema Summary

The current database schema includes:

| Table | Purpose | RLS Enabled |
|-------|---------|-------------|
| `tenants` | Multi-tenant organization records | No (needed for subdomain resolution) |
| `users` | User accounts linked to OAuth subjects | Yes |
| `oauth_providers` | OAuth/OIDC provider configurations per tenant | Yes |
| `schema_version` | Database initialization tracking | No |

### Configuration Storage Considerations

While no schema changes are required, some production features may benefit from configuration storage:

#### 1. Application Settings (Environment Variables - Recommended)

Production essentials configurations should be stored as environment variables, following the existing pattern in `backend/app/core/config.py`:

```python
# Proposed additions to Settings class (pydantic-settings)

# Security Headers
X_FRAME_OPTIONS: str = "DENY"
CSP_POLICY: str = "default-src 'self'"
FORCE_HSTS: bool = False
HSTS_MAX_AGE: int = 31536000

# Sentry Integration (Optional)
SENTRY_DSN: str | None = None
SENTRY_ENVIRONMENT: str = "development"
SENTRY_TRACES_SAMPLE_RATE: float = 0.1

# Backup Configuration
BACKUP_RETENTION_DAYS: int = 7
BACKUP_S3_BUCKET: str | None = None
```

**Rationale:** Environment variables are the standard approach for configuration that varies between environments (development, staging, production). This aligns with 12-factor app principles and Kubernetes ConfigMap/Secret patterns.

#### 2. Alert Rule Configuration (File-Based)

Prometheus alerting rules are stored in YAML files within the observability stack:

```
observability/prometheus/
  prometheus.yml          # Main Prometheus config
  alerts.yml              # NEW: Alerting rules (proposed)
```

**Rationale:** Prometheus natively uses YAML configuration files. Storing alert rules in the repository enables version control and review processes.

#### 3. Kubernetes Manifests (File-Based)

Deployment configurations are stored as Kustomize manifests:

```
k8s/
  base/                   # Base manifests
  overlays/
    staging/              # Staging-specific patches
    production/           # Production-specific patches
```

**Rationale:** Kubernetes manifests should be version-controlled and deployed via CI/CD, not stored in the application database.

### Future Schema Considerations

If future enhancements require database persistence, the following patterns should be followed:

#### Pattern: Feature Flags Table (Out of Scope)

If per-tenant feature flags are needed in the future:

```sql
CREATE TABLE feature_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    flag_name VARCHAR(100) NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(tenant_id, flag_name)
);

-- Enable RLS
ALTER TABLE feature_flags ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON feature_flags
    USING (tenant_id = COALESCE(
        NULLIF(current_setting('app.current_tenant_id', TRUE), '')::UUID,
        '00000000-0000-0000-0000-000000000000'::UUID
    ));
```

**Note:** This is documented for future reference but is explicitly out of scope for Production Essentials.

#### Pattern: Audit Log Table (Out of Scope)

If security audit logging to database is needed:

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    user_id UUID,
    action VARCHAR(50) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant_created ON audit_logs(tenant_id, created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
```

**Note:** Security audit logging is better handled through structured logging (Loki) rather than database storage. This pattern is documented for teams that require database-backed audit trails for compliance.

### Migration Strategy

Since no schema changes are required:

1. **No Alembic migrations needed** for Production Essentials core features
2. **Backward compatible** with existing generated projects
3. **Configuration-driven** approach ensures easy adoption

### Data Retention and Lifecycle

#### Backup Data Retention

| Backup Type | Retention Period | Storage |
|-------------|-----------------|---------|
| Daily backups | 7 days | Local or S3 |
| Weekly backups | 4 weeks | S3 (recommended) |
| Monthly backups | 12 months | S3 cold storage |

#### Log Retention (Loki)

| Log Type | Retention Period | Rationale |
|----------|-----------------|-----------|
| Application logs | 30 days | Operational troubleshooting |
| Security logs | 90 days | Security incident investigation |
| Audit logs | 1 year | Compliance requirements |

**Note:** Actual retention policies should be configured based on organizational requirements and compliance needs.

### Compatibility Matrix

| Existing Schema Version | Compatible | Notes |
|------------------------|------------|-------|
| e10757622a70 (Initial) | Yes | Full compatibility |
| 5ba5077f1546 (RLS update) | Yes | Full compatibility |
| Future versions | Yes | No schema dependencies |

### Summary

Production Essentials maintains full backward compatibility by:

1. **Using environment variables** for runtime configuration
2. **Using file-based configuration** for CI/CD and infrastructure
3. **Avoiding database schema changes** in the core feature set
4. **Documenting patterns** for future features requiring persistence

---

## UI/UX Considerations

### Overview

Production Essentials is primarily a backend, infrastructure, and DevOps-focused feature set. However, there are several UI/UX touchpoints that enhance the developer and operator experience.

### User Interface Scope

| Category | UI Required | Description |
|----------|-------------|-------------|
| CI/CD Pipelines | No | GitHub Actions UI provides all necessary feedback |
| Security Headers | No | Invisible to end users, detectable via browser DevTools |
| Alerting | Minimal | Grafana dashboards (already exists in observability stack) |
| Error Tracking | No | Sentry provides its own dashboard |
| Kubernetes | No | kubectl and cloud provider UIs |
| Load Testing | No | k6 CLI and optional Grafana dashboards |

### Developer Experience Enhancements

#### 1. CI/CD Feedback in Pull Requests

**GitHub Actions Status Checks:**

```
PR #123: Add user profile feature
-----------------------------------------
[x] ci / backend-lint (passed)
[x] ci / backend-test (passed)
[x] ci / frontend-lint (passed)
[x] ci / frontend-test (passed)
[x] security / trivy-scan (passed)
[x] security / gitleaks (passed)
-----------------------------------------
All checks have passed
```

**Design Principles:**
- Clear pass/fail indicators
- Detailed logs available on click
- Test coverage reports linked in PR comments
- Security scan results summarized (no manual log parsing)

**PR Comment Template (Automated):**

```markdown
## CI/CD Summary

### Test Results
- Backend: 142 tests passed, 0 failed (98.2% coverage)
- Frontend: 67 tests passed, 0 failed (94.1% coverage)

### Security Scan
- Container vulnerabilities: 0 critical, 0 high
- Dependency vulnerabilities: 0 critical, 0 high
- Secrets detected: 0

### Build Artifacts
- Backend image: `ghcr.io/org/backend:sha-abc1234`
- Frontend image: `ghcr.io/org/frontend:sha-abc1234`
```

#### 2. Deployment Status Notifications

**Slack/Discord Notification Template:**

```
:rocket: Deployment to staging completed

Service: backend
Version: v1.2.3 (sha-abc1234)
Environment: staging
Time: 2025-12-05 10:30:00 UTC
Duration: 2m 15s

View deployment: [GitHub Actions](link)
View application: [Staging URL](link)
```

**Design Principles:**
- Actionable links to dashboards and logs
- Clear environment identification
- Version and commit reference for traceability
- Duration for performance awareness

#### 3. Error Alert Notifications

**Alert Notification Template (Slack/Email):**

```
:warning: Alert: High Error Rate

Severity: Critical
Service: backend
Alert: HTTP 5xx error rate > 1% for 5 minutes
Current Value: 3.2%

Dashboard: [Grafana Link](link)
Runbook: [Error Rate Runbook](link)
```

**Design Principles:**
- Clear severity indicators
- Current metric value for context
- Direct links to dashboards and runbooks
- Consistent format across all alert types

### Grafana Dashboard Enhancements

#### Production Readiness Dashboard

A new Grafana dashboard should be added to the observability stack:

**Dashboard Sections:**

1. **Service Health**
   - Uptime percentage (last 24h, 7d, 30d)
   - Current error rate
   - Request latency (p50, p95, p99)

2. **Security Status**
   - Last security scan timestamp
   - Vulnerability count by severity
   - Certificate expiration countdown

3. **Deployment History**
   - Recent deployments with version
   - Deployment frequency
   - Rollback events

4. **Resource Utilization**
   - CPU and memory usage
   - Database connection pool status
   - Redis connection status

**Dashboard Variables:**
```yaml
variables:
  - name: environment
    type: custom
    options: [staging, production]
  - name: service
    type: custom
    options: [backend, frontend]
  - name: time_range
    type: interval
    options: [5m, 15m, 1h, 24h, 7d]
```

#### Alert Dashboard

A dedicated dashboard for alert visualization:

**Panels:**
- Active alerts table
- Alert history timeline
- Alert frequency heatmap
- Mean Time to Recovery (MTTR) tracking

### CLI/Terminal User Experience

#### k6 Load Test Output

**Formatted Output Example:**

```
          /\      |‾‾| /‾‾/   /‾‾/
     /\  /  \     |  |/  /   /  /
    /  \/    \    |     (   /   ‾‾\
   /          \   |  |\  \ |  (‾)  |
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: load-test.js
     output: -

  scenarios: (100.00%) 1 scenario, 50 max VUs, 5m30s max duration
           * default: 50 looping VUs for 5m0s (gracefulStop: 30s)

running (5m00.0s), 00/50 VUs, 15000 complete iterations
default [======================================] 50 VUs  5m0s

     ✓ status is 200
     ✓ response time < 200ms

     checks.........................: 100.00% ✓ 30000      ✗ 0
     http_req_duration..............: avg=45.2ms  min=12ms  med=42ms  max=198ms  p(90)=78ms  p(95)=95ms
     http_reqs......................: 15000   50/s
     vus............................: 50      min=50       max=50
     vus_max........................: 50      min=50       max=50
```

**Design Principles:**
- Clear visual progress indicator
- Pass/fail checks prominently displayed
- Performance metrics with percentiles
- Summary statistics for quick assessment

#### Backup Script Output

**Formatted Output Example:**

```
[2025-12-05 02:00:00] Starting database backup...
[2025-12-05 02:00:00] Database: myapp_production
[2025-12-05 02:00:15] Backup size: 1.2 GB
[2025-12-05 02:00:30] Compressing backup...
[2025-12-05 02:00:45] Compressed size: 245 MB
[2025-12-05 02:00:50] Uploading to S3: s3://backups/myapp/2025-12-05_020000.sql.gz
[2025-12-05 02:01:15] Upload complete (checksum verified)
[2025-12-05 02:01:16] Cleaning old backups (retention: 7 days)
[2025-12-05 02:01:17] Removed 1 expired backup
[2025-12-05 02:01:17] Backup completed successfully

Summary:
  Duration: 1m 17s
  Backup file: 2025-12-05_020000.sql.gz
  Size: 245 MB (1.2 GB uncompressed)
  Location: s3://backups/myapp/
```

**Design Principles:**
- Timestamped progress updates
- Size and duration information
- Clear success/failure indication
- Actionable summary at completion

### Accessibility Considerations

Although Production Essentials has minimal end-user UI, accessibility should be maintained:

#### Grafana Dashboards
- Ensure color-blind friendly palettes for status indicators
- Provide text labels alongside color indicators
- Maintain sufficient contrast ratios

#### Notification Messages
- Use clear, descriptive language
- Include severity levels in text (not just emoji)
- Provide context without requiring visual parsing

### Documentation UI Patterns

#### Security Audit Checklist Format

**Interactive Checklist Design:**

```markdown
## Pre-Production Security Checklist

### Authentication & Authorization
- [ ] JWT validation is enabled and configured
- [ ] Token expiration is set appropriately (< 1 hour recommended)
- [ ] Token revocation is implemented via Redis blacklist
- [ ] OAuth scopes are properly defined and enforced

### Data Protection
- [ ] RLS policies are enabled on all tenant-scoped tables
- [ ] Database passwords are not in source control
- [ ] API rate limiting is configured
- [ ] Input validation is implemented on all endpoints

### Infrastructure Security
- [ ] HTTPS is enforced in production
- [ ] Security headers are configured
- [ ] Container images pass vulnerability scans
- [ ] Secrets are managed via external secrets manager

Progress: 8/12 items complete
```

**Design Principles:**
- Clear grouping by category
- Progress indicator
- Actionable items with yes/no answers
- Links to relevant documentation for each item

### Runbook UI Pattern

**Runbook Structure:**

```markdown
# Runbook: Database Connection Exhaustion

## Severity: Critical
## Service: Backend
## On-Call: DevOps Team

---

## Symptoms
- Alert: "Database connection pool near exhaustion"
- API requests returning 500 errors
- Slow query responses

## Immediate Actions
1. [ ] Check current connection count: `SELECT count(*) FROM pg_stat_activity;`
2. [ ] Identify long-running queries: `SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active';`
3. [ ] If necessary, terminate long-running queries: `SELECT pg_terminate_backend(pid);`

## Root Cause Investigation
1. Review recent deployments
2. Check for query performance regression
3. Analyze connection pool settings

## Prevention
- Implement query timeout limits
- Add connection pool monitoring
- Review database indexing
```

**Design Principles:**
- Clear severity and ownership
- Step-by-step actionable instructions
- Copy-pastable commands
- Prevention guidance for future incidents

### Design System Alignment

All UI additions should follow the existing template design patterns:

| Element | Pattern | Reference |
|---------|---------|-----------|
| Colors | Tailwind CSS palette | `frontend/tailwind.config.js` |
| Components | Lit web components | `frontend/src/components/` |
| Typography | System UI fonts | Existing component styles |
| Spacing | 4px base unit (0.25rem) | Consistent with existing |
| Status Indicators | Circular dots with color | `health-check.ts` pattern |

### Summary

Production Essentials UI/UX focuses on:

1. **Developer Experience** - Clear CI/CD feedback, actionable notifications
2. **Operator Experience** - Informative dashboards, consistent runbook format
3. **Automation-First** - Most interactions via CLI and APIs
4. **Consistency** - Following existing template patterns and design system

---

## Security & Privacy Considerations

### Overview

Production Essentials includes significant security enhancements designed to harden the application for production deployment. This section details the security model, threat mitigations, and privacy considerations.

### Existing Security Foundation

The template already provides a strong security foundation:

| Security Feature | Current Implementation | Reference |
|-----------------|----------------------|-----------|
| Authentication | OAuth 2.0/OIDC with PKCE | ADR-004 |
| Authorization | Scope-based access control | `auth.py` |
| Multi-tenancy | PostgreSQL Row-Level Security | ADR-005 |
| Token Revocation | Redis blacklist | ADR-007 |
| JWKS Caching | Secure key rotation handling | ADR-008 |
| Rate Limiting | Redis-based throttling | ADR-014 |
| CORS | Configurable origin policies | ADR-015 |

### Security Headers Implementation

#### HTTP Security Headers

The following security headers will be added via middleware:

| Header | Value | Purpose | OWASP Reference |
|--------|-------|---------|-----------------|
| `Content-Security-Policy` | Configurable | Prevent XSS, injection attacks | A03:2021 |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforce HTTPS | A05:2021 |
| `X-Frame-Options` | `DENY` | Prevent clickjacking | A05:2021 |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME-type sniffing | A05:2021 |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Control referrer information | Privacy |
| `Permissions-Policy` | Configurable | Control browser features | A05:2021 |

#### Content Security Policy (CSP)

**Default CSP Policy:**

```
default-src 'self';
script-src 'self' 'unsafe-inline';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self';
connect-src 'self' {keycloak_url};
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

**CSP Configuration Approach:**
- `'unsafe-inline'` for scripts is required for Lit component hydration
- Connect-src must include Keycloak URL for OAuth flows
- Frame-ancestors blocks embedding in iframes (defense-in-depth for clickjacking)

**Customization via Environment Variables:**

```python
# config.py additions
CSP_DEFAULT_SRC: str = "'self'"
CSP_SCRIPT_SRC: str = "'self' 'unsafe-inline'"
CSP_STYLE_SRC: str = "'self' 'unsafe-inline'"
CSP_IMG_SRC: str = "'self' data: https:"
CSP_CONNECT_SRC: str = "'self'"  # Keycloak URL added automatically
CSP_REPORT_URI: str | None = None  # Optional CSP violation reporting
```

### Vulnerability Scanning

#### Container Image Scanning

**Trivy Integration:**

```yaml
# .github/workflows/security.yml
jobs:
  container-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Build image
        run: docker build -t app:${{ github.sha }} .

      - name: Run Trivy scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      - name: Upload results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

**Vulnerability Thresholds:**

| Severity | CI Behavior | Response Time |
|----------|-------------|---------------|
| Critical | Fail build | Must fix before merge |
| High | Fail build | Must fix before merge |
| Medium | Warning only | Fix within 30 days |
| Low | Log only | Best effort |

#### Dependency Scanning

**Python Dependencies (pip-audit):**

```yaml
- name: Scan Python dependencies
  run: |
    pip install pip-audit
    pip-audit --requirement requirements.txt --format json --output pip-audit.json
    pip-audit --requirement requirements.txt --fail-on-vuln --severity high
```

**Node.js Dependencies (npm audit):**

```yaml
- name: Scan npm dependencies
  run: |
    npm audit --audit-level=high
    npm audit --json > npm-audit.json
```

### Secret Detection

#### Pre-commit Hook Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
        args: ['--config', '.gitleaks.toml']
```

**Gitleaks Configuration:**

```toml
# .gitleaks.toml
[extend]
useDefault = true

[allowlist]
paths = [
  '''\.env\.example$''',
  '''docs/.*\.md$''',
]

[[rules]]
id = "custom-api-key"
description = "Custom API Key Pattern"
regex = '''(?i)api[_-]?key[_-]?[=:]["']?[a-zA-Z0-9]{32,}["']?'''
```

#### CI Secret Scanning

```yaml
- name: Scan for secrets
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Authentication Security

#### Token Security Best Practices

| Aspect | Implementation | Rationale |
|--------|----------------|-----------|
| Access Token Lifetime | 15 minutes (configurable) | Minimize exposure window |
| Refresh Token Lifetime | 8 hours (configurable) | Balance security and UX |
| Token Storage | Browser memory (not localStorage) | XSS protection |
| Token Revocation | Redis blacklist with TTL | Immediate invalidation |
| PKCE | Required for all flows | Prevent authorization code interception |

#### Session Security

**Recommendations for Production:**

```python
# Session configuration recommendations
SESSION_COOKIE_SECURE = True       # HTTPS only
SESSION_COOKIE_HTTPONLY = True     # No JavaScript access
SESSION_COOKIE_SAMESITE = "Lax"    # CSRF protection
SESSION_LIFETIME_SECONDS = 3600    # 1 hour max
```

### Authorization Security

#### Scope Enforcement

The existing scope system should be reviewed for production:

```python
# Existing scopes (schemas/auth.py)
SCOPE_STATEMENTS_READ = "statements/read"
SCOPE_STATEMENTS_WRITE = "statements/write"
SCOPE_STATEMENTS_READ_MINE = "statements/read/mine"
SCOPE_STATE_READ = "state/read"
SCOPE_STATE_WRITE = "state/write"
SCOPE_ADMIN = "admin"
SCOPE_TENANT_ADMIN = "tenant/admin"
```

**Production Checklist:**
- [ ] All endpoints have explicit scope requirements
- [ ] Admin scopes are restricted to authorized users in Keycloak
- [ ] Scope hierarchy is documented and enforced
- [ ] Scope validation fails closed (deny by default)

### Data Protection

#### Sensitive Data Handling

| Data Type | Protection Measure | Storage |
|-----------|-------------------|---------|
| Passwords | Not stored (OAuth delegated) | N/A |
| API Keys | Hashed with bcrypt | Database |
| OAuth Tokens | Short-lived, revocable | Memory/Redis |
| PII (email, name) | Encrypted at rest | Database |
| Secrets | External secrets manager | Vault/AWS SM |

#### Encryption Requirements

**At Rest:**
- PostgreSQL: Enable TDE (Transparent Data Encryption) in production
- Backups: Encrypted with AES-256-GCM
- S3 Backups: Server-side encryption (SSE-S3 or SSE-KMS)

**In Transit:**
- All external communication over TLS 1.2+
- Internal service mesh communication over mTLS (optional)
- Database connections over TLS

### Privacy Considerations

#### Data Minimization

Production Essentials does not introduce new PII collection. However, the following data is logged and should be reviewed:

| Log Data | Contains PII | Retention | Justification |
|----------|-------------|-----------|---------------|
| Request logs | IP address | 30 days | Troubleshooting |
| Error logs | User ID (UUID) | 90 days | Incident investigation |
| Audit logs | User actions | 1 year | Compliance |
| Metrics | Tenant ID | 90 days | Performance monitoring |

#### GDPR Considerations

If operating in EU/EEA:

1. **Data Subject Requests:** Ensure ability to export/delete user data
2. **Consent:** OAuth consent screen managed by Keycloak
3. **Data Processing Agreements:** Required for Sentry, cloud providers
4. **Cross-border Transfers:** Verify data residency requirements

#### Log Sanitization

**Recommended Log Filtering:**

```python
# Sensitive fields to redact from logs
SENSITIVE_FIELDS = [
    "password",
    "token",
    "secret",
    "api_key",
    "authorization",
    "cookie",
    "credit_card",
    "ssn",
]

def sanitize_log_data(data: dict) -> dict:
    """Redact sensitive fields from log data."""
    sanitized = data.copy()
    for field in SENSITIVE_FIELDS:
        if field in sanitized:
            sanitized[field] = "[REDACTED]"
    return sanitized
```

### Error Tracking Privacy

#### Sentry Data Handling

**Before Sending to Sentry:**

```python
import sentry_sdk
from sentry_sdk import configure_scope

def before_send(event, hint):
    """Sanitize data before sending to Sentry."""
    # Remove sensitive headers
    if "request" in event:
        if "headers" in event["request"]:
            for header in ["Authorization", "Cookie", "X-API-Key"]:
                event["request"]["headers"].pop(header, None)

    # Remove sensitive query parameters
    if "request" in event:
        if "query_string" in event["request"]:
            event["request"]["query_string"] = "[REDACTED]"

    return event

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    before_send=before_send,
    send_default_pii=False,  # Disable automatic PII collection
)
```

**Sentry Data Retention:**
- Configure retention period in Sentry project settings
- Recommend 90 days for error data
- Use data scrubbing rules for additional PII protection

### Infrastructure Security

#### Kubernetes Security

**Pod Security Standards:**

```yaml
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 1000
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: backend
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

**Network Policies:**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: ingress
      ports:
        - protocol: TCP
          port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
    - to:
        - podSelector:
            matchLabels:
              app: redis
      ports:
        - protocol: TCP
          port: 6379
```

#### Container Security

**Dockerfile Best Practices:**

```dockerfile
# Use specific version tags, not latest
FROM python:3.12-slim-bookworm AS base

# Run as non-root user
RUN useradd --create-home --shell /bin/bash appuser
USER appuser

# No secrets in build args
# No sensitive files copied

# Health check defined
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1
```

### Security Audit Checklist

A comprehensive security checklist will be provided in `docs/SECURITY_CHECKLIST.md`:

```markdown
# Pre-Production Security Checklist

## Authentication & Authorization
- [ ] HTTPS enforced for all endpoints
- [ ] OAuth 2.0 PKCE flow configured
- [ ] Token expiration times are appropriate
- [ ] Token revocation is working
- [ ] All endpoints have scope requirements defined
- [ ] Admin endpoints restricted appropriately

## Infrastructure Security
- [ ] Security headers configured and verified
- [ ] Container images pass vulnerability scans
- [ ] Secrets stored in external secrets manager
- [ ] Database connections use TLS
- [ ] Network policies restrict pod communication

## Data Protection
- [ ] RLS policies enabled on all tenant tables
- [ ] Backup encryption configured
- [ ] PII logging minimized and documented
- [ ] Data retention policies defined

## Monitoring & Response
- [ ] Error tracking (Sentry) configured
- [ ] Security alerts configured in Prometheus
- [ ] Incident response runbooks documented
- [ ] On-call rotation established

## Compliance (if applicable)
- [ ] Privacy policy updated
- [ ] Cookie consent implemented
- [ ] Data processing agreements in place
- [ ] GDPR data subject request procedures documented
```

### Threat Model Summary

| Threat | Mitigation | Status |
|--------|------------|--------|
| XSS | CSP headers, input validation | Planned |
| CSRF | SameSite cookies, CORS | Existing |
| SQL Injection | SQLAlchemy ORM, RLS | Existing |
| Clickjacking | X-Frame-Options, CSP frame-ancestors | Planned |
| Credential Stuffing | Rate limiting, OAuth delegation | Existing |
| Token Theft | Short-lived tokens, revocation | Existing |
| Dependency Vulns | Automated scanning in CI | Planned |
| Secret Exposure | Pre-commit hooks, CI scanning | Planned |
| Container Vulns | Trivy scanning in CI | Planned |
| Data Breach | Encryption at rest, RLS | Existing/Planned |

### Compliance Considerations

#### SOC 2 Alignment

Production Essentials supports SOC 2 compliance through:

- **Security:** Vulnerability scanning, access controls, encryption
- **Availability:** Health checks, alerting, backup procedures
- **Confidentiality:** RLS, encryption, log sanitization
- **Processing Integrity:** Input validation, audit logging
- **Privacy:** Data minimization, retention policies

**Note:** Full SOC 2 certification requires organizational controls beyond technical implementation.

#### OWASP Top 10 (2021) Coverage

| OWASP Category | Coverage |
|----------------|----------|
| A01: Broken Access Control | RLS, scopes, CORS |
| A02: Cryptographic Failures | TLS, encryption at rest |
| A03: Injection | ORM, CSP, input validation |
| A04: Insecure Design | Threat model, ADRs |
| A05: Security Misconfiguration | Security headers, scanning |
| A06: Vulnerable Components | Dependency scanning |
| A07: Auth Failures | OAuth 2.0, PKCE, revocation |
| A08: Software/Data Integrity | CI/CD, SBOM |
| A09: Security Logging | Structured logging, alerting |
| A10: SSRF | Network policies (K8s) |

---

## Testing Strategy

### Overview

Production Essentials extends the existing test suite with additional tests for security, CI/CD, and operational features. The testing approach maintains the established patterns while ensuring comprehensive coverage of new functionality.

### Existing Test Infrastructure

| Layer | Framework | Location | Current Coverage |
|-------|-----------|----------|------------------|
| Backend Unit | pytest | `backend/tests/unit/` | Auth, OAuth, tenant, scopes |
| Backend Integration | pytest | `backend/tests/integration/` | OAuth flow, tenant isolation |
| Frontend Unit | Vitest | `frontend/src/**/*.test.ts` | Components, API client |
| E2E/API | Playwright | `playwright/tests/` | API endpoints, auth flow |

### Testing Levels for Production Essentials

#### Level 1: Unit Tests

**Security Headers Middleware Tests:**

```python
# tests/unit/test_security_headers.py

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch

from app.middleware.security_headers import SecurityHeadersMiddleware


class TestSecurityHeadersMiddleware:
    """Tests for security headers middleware."""

    def test_adds_x_content_type_options(self, test_client):
        """Verify X-Content-Type-Options header is set."""
        response = test_client.get("/api/v1/health")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_adds_x_frame_options(self, test_client):
        """Verify X-Frame-Options header is set."""
        response = test_client.get("/api/v1/health")
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_adds_referrer_policy(self, test_client):
        """Verify Referrer-Policy header is set."""
        response = test_client.get("/api/v1/health")
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_adds_csp_header(self, test_client):
        """Verify Content-Security-Policy header is set."""
        response = test_client.get("/api/v1/health")
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    def test_hsts_not_set_for_http(self, test_client):
        """Verify HSTS is not set for HTTP requests."""
        response = test_client.get("/api/v1/health")
        # HSTS should only be set for HTTPS
        assert "Strict-Transport-Security" not in response.headers

    @patch("app.core.config.settings.FORCE_HSTS", True)
    def test_hsts_set_when_forced(self, test_client):
        """Verify HSTS is set when FORCE_HSTS is enabled."""
        response = test_client.get("/api/v1/health")
        assert "Strict-Transport-Security" in response.headers

    def test_csp_configurable(self, test_client):
        """Verify CSP policy is configurable via settings."""
        # Test with custom CSP configuration
        pass


class TestCSPPolicy:
    """Tests for Content Security Policy configuration."""

    def test_default_csp_policy(self):
        """Verify default CSP policy is secure."""
        from app.core.config import settings
        # Default should include self and not allow unsafe-eval
        assert "'self'" in settings.CSP_DEFAULT_SRC
        assert "unsafe-eval" not in settings.CSP_SCRIPT_SRC

    def test_keycloak_url_in_connect_src(self):
        """Verify Keycloak URL is included in connect-src."""
        # OAuth flows require connection to Keycloak
        pass
```

**Sentry Integration Tests:**

```python
# tests/unit/test_sentry_integration.py

import pytest
from unittest.mock import patch, MagicMock


class TestSentryIntegration:
    """Tests for Sentry error tracking integration."""

    @patch("sentry_sdk.init")
    def test_sentry_initialization(self, mock_init):
        """Verify Sentry initializes with correct configuration."""
        from app.observability.sentry import setup_sentry

        setup_sentry()

        mock_init.assert_called_once()
        call_kwargs = mock_init.call_args[1]
        assert call_kwargs["send_default_pii"] is False

    def test_before_send_removes_sensitive_headers(self):
        """Verify sensitive headers are removed before sending to Sentry."""
        from app.observability.sentry import before_send

        event = {
            "request": {
                "headers": {
                    "Authorization": "Bearer token123",
                    "Cookie": "session=abc",
                    "Content-Type": "application/json",
                }
            }
        }

        sanitized = before_send(event, {})

        assert "Authorization" not in sanitized["request"]["headers"]
        assert "Cookie" not in sanitized["request"]["headers"]
        assert sanitized["request"]["headers"]["Content-Type"] == "application/json"

    def test_tenant_context_attached_to_errors(self):
        """Verify tenant_id is attached to Sentry error context."""
        # Test that tenant context is properly set in Sentry scope
        pass

    def test_sentry_disabled_when_no_dsn(self):
        """Verify Sentry does not initialize when DSN is not configured."""
        pass
```

**Alerting Rules Unit Tests:**

```python
# tests/unit/test_alerting_rules.py

import pytest
import yaml
from pathlib import Path


class TestAlertingRules:
    """Tests for Prometheus alerting rules."""

    @pytest.fixture
    def alert_rules(self):
        """Load alerting rules from YAML file."""
        rules_path = Path("observability/prometheus/alerts.yml")
        with open(rules_path) as f:
            return yaml.safe_load(f)

    def test_high_error_rate_alert_exists(self, alert_rules):
        """Verify high error rate alert is defined."""
        rules = alert_rules["groups"][0]["rules"]
        alert_names = [r["alert"] for r in rules]
        assert "HighErrorRate" in alert_names

    def test_high_latency_alert_exists(self, alert_rules):
        """Verify high latency alert is defined."""
        rules = alert_rules["groups"][0]["rules"]
        alert_names = [r["alert"] for r in rules]
        assert "HighLatency" in alert_names

    def test_alert_has_severity_label(self, alert_rules):
        """Verify all alerts have severity labels."""
        rules = alert_rules["groups"][0]["rules"]
        for rule in rules:
            assert "severity" in rule.get("labels", {})

    def test_alert_has_annotations(self, alert_rules):
        """Verify all alerts have summary and description annotations."""
        rules = alert_rules["groups"][0]["rules"]
        for rule in rules:
            annotations = rule.get("annotations", {})
            assert "summary" in annotations
            assert "description" in annotations
```

#### Level 2: Integration Tests

**CI/CD Workflow Validation:**

```python
# tests/integration/test_ci_workflows.py

import pytest
import yaml
from pathlib import Path


class TestCIWorkflows:
    """Integration tests for CI/CD workflow files."""

    @pytest.fixture
    def ci_workflow(self):
        """Load CI workflow YAML."""
        workflow_path = Path(".github/workflows/ci.yml")
        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def test_ci_workflow_triggers_on_pr(self, ci_workflow):
        """Verify CI triggers on pull requests."""
        triggers = ci_workflow.get("on", {})
        assert "pull_request" in triggers

    def test_ci_workflow_has_backend_tests(self, ci_workflow):
        """Verify CI includes backend test job."""
        jobs = ci_workflow.get("jobs", {})
        assert "backend-test" in jobs or any(
            "pytest" in str(job) for job in jobs.values()
        )

    def test_ci_workflow_has_frontend_tests(self, ci_workflow):
        """Verify CI includes frontend test job."""
        jobs = ci_workflow.get("jobs", {})
        assert "frontend-test" in jobs or any(
            "vitest" in str(job) or "npm test" in str(job)
            for job in jobs.values()
        )

    def test_ci_workflow_has_security_scan(self, ci_workflow):
        """Verify CI includes security scanning."""
        workflow_str = str(ci_workflow)
        assert "trivy" in workflow_str.lower() or "security" in workflow_str.lower()
```

**Kubernetes Manifest Validation:**

```python
# tests/integration/test_kubernetes_manifests.py

import pytest
import yaml
from pathlib import Path


class TestKubernetesManifests:
    """Integration tests for Kubernetes manifests."""

    @pytest.fixture
    def backend_deployment(self):
        """Load backend deployment manifest."""
        manifest_path = Path("k8s/base/backend-deployment.yaml")
        with open(manifest_path) as f:
            return yaml.safe_load(f)

    def test_deployment_has_resource_limits(self, backend_deployment):
        """Verify deployment has resource limits defined."""
        containers = backend_deployment["spec"]["template"]["spec"]["containers"]
        for container in containers:
            resources = container.get("resources", {})
            assert "limits" in resources
            assert "requests" in resources

    def test_deployment_has_health_probes(self, backend_deployment):
        """Verify deployment has liveness and readiness probes."""
        containers = backend_deployment["spec"]["template"]["spec"]["containers"]
        for container in containers:
            assert "livenessProbe" in container
            assert "readinessProbe" in container

    def test_deployment_runs_as_non_root(self, backend_deployment):
        """Verify deployment runs as non-root user."""
        security_context = backend_deployment["spec"]["template"]["spec"].get(
            "securityContext", {}
        )
        assert security_context.get("runAsNonRoot") is True

    def test_deployment_uses_secrets_for_sensitive_config(self, backend_deployment):
        """Verify sensitive config comes from secrets, not configmaps."""
        containers = backend_deployment["spec"]["template"]["spec"]["containers"]
        for container in containers:
            env_from = container.get("envFrom", [])
            # Check that secretRef is used for database credentials, etc.
            has_secret_ref = any("secretRef" in ef for ef in env_from)
            assert has_secret_ref or len(env_from) == 0
```

**Backup Script Tests:**

```python
# tests/integration/test_backup_scripts.py

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch


class TestBackupScripts:
    """Integration tests for database backup scripts."""

    def test_backup_script_exists(self):
        """Verify backup script exists and is executable."""
        script_path = Path("scripts/backup-db.sh")
        assert script_path.exists()

    def test_backup_script_syntax(self):
        """Verify backup script has valid shell syntax."""
        result = subprocess.run(
            ["bash", "-n", "scripts/backup-db.sh"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_restore_script_exists(self):
        """Verify restore script exists."""
        script_path = Path("scripts/restore-db.sh")
        assert script_path.exists()

    @pytest.mark.skipif(
        not Path("/usr/bin/pg_dump").exists(),
        reason="pg_dump not available"
    )
    def test_backup_script_dry_run(self):
        """Test backup script in dry-run mode."""
        # Use test database for validation
        pass
```

#### Level 3: E2E/API Tests

**Security Headers E2E Tests:**

```typescript
// playwright/tests/security-headers.api.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Security Headers', () => {
  test('API responses include security headers', async ({ request }) => {
    const response = await request.get('/api/v1/health');

    // Verify security headers
    expect(response.headers()['x-content-type-options']).toBe('nosniff');
    expect(response.headers()['x-frame-options']).toBe('DENY');
    expect(response.headers()['referrer-policy']).toBe('strict-origin-when-cross-origin');
    expect(response.headers()['content-security-policy']).toContain("default-src 'self'");
  });

  test('CORS headers are correct for allowed origins', async ({ request }) => {
    const response = await request.get('/api/v1/health', {
      headers: {
        Origin: 'http://localhost:3000',
      },
    });

    expect(response.headers()['access-control-allow-origin']).toBeDefined();
  });

  test('CORS rejects disallowed origins', async ({ request }) => {
    const response = await request.get('/api/v1/health', {
      headers: {
        Origin: 'http://malicious-site.com',
      },
    });

    // Should not have CORS headers for disallowed origin
    expect(response.headers()['access-control-allow-origin']).toBeUndefined();
  });
});
```

**Load Testing with k6:**

```javascript
// k6/load-test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const healthCheckDuration = new Trend('health_check_duration');

// Test configuration
export const options = {
  stages: [
    { duration: '1m', target: 10 },   // Ramp up to 10 users
    { duration: '3m', target: 50 },   // Stay at 50 users
    { duration: '1m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% of requests under 500ms
    errors: ['rate<0.01'],              // Error rate under 1%
  },
};

export default function () {
  // Health check endpoint
  const healthResponse = http.get(`${__ENV.BASE_URL}/api/v1/health`);
  healthCheckDuration.add(healthResponse.timings.duration);

  check(healthResponse, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  }) || errorRate.add(1);

  sleep(1);
}

// Authenticated endpoint test
export function authenticatedTest() {
  const token = __ENV.AUTH_TOKEN;

  const response = http.get(`${__ENV.BASE_URL}/api/v1/auth/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  check(response, {
    'auth endpoint status is 200': (r) => r.status === 200,
    'auth endpoint response time < 500ms': (r) => r.timings.duration < 500,
  }) || errorRate.add(1);
}
```

**k6 CI Integration:**

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday at 6 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install k6
        run: |
          sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6

      - name: Run load tests
        env:
          BASE_URL: ${{ secrets.STAGING_URL }}
          AUTH_TOKEN: ${{ secrets.LOAD_TEST_TOKEN }}
        run: k6 run k6/load-test.js --out json=results.json

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: results.json
```

#### Level 4: Security Testing

**Security Scan Tests:**

```python
# tests/security/test_vulnerability_scan.py

import pytest
import subprocess
import json


class TestSecurityScans:
    """Security scanning tests."""

    @pytest.mark.slow
    def test_trivy_container_scan(self):
        """Run Trivy container scan and verify no critical vulnerabilities."""
        result = subprocess.run(
            [
                "trivy", "image",
                "--severity", "CRITICAL,HIGH",
                "--format", "json",
                "--exit-code", "0",
                "backend:test"
            ],
            capture_output=True,
            text=True
        )

        if result.stdout:
            findings = json.loads(result.stdout)
            critical_vulns = sum(
                1 for result in findings.get("Results", [])
                for vuln in result.get("Vulnerabilities", [])
                if vuln["Severity"] in ["CRITICAL", "HIGH"]
            )
            assert critical_vulns == 0, f"Found {critical_vulns} critical/high vulnerabilities"

    @pytest.mark.slow
    def test_pip_audit(self):
        """Run pip-audit and verify no known vulnerabilities."""
        result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True,
            cwd="backend"
        )

        if result.stdout:
            vulns = json.loads(result.stdout)
            assert len(vulns) == 0, f"Found {len(vulns)} vulnerable packages"

    @pytest.mark.slow
    def test_gitleaks_scan(self):
        """Run gitleaks and verify no secrets in codebase."""
        result = subprocess.run(
            ["gitleaks", "detect", "--source", ".", "--no-git", "--exit-code", "0"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Secrets detected in codebase"
```

### Test Coverage Requirements

| Component | Minimum Coverage | Target Coverage |
|-----------|-----------------|-----------------|
| Security Headers Middleware | 90% | 95% |
| Sentry Integration | 80% | 90% |
| Alerting Rules | 100% (validation) | 100% |
| Kubernetes Manifests | 100% (validation) | 100% |
| Backup Scripts | 80% | 90% |
| CI Workflows | 100% (syntax) | 100% |

### Test Execution Matrix

| Test Type | Runs On | Frequency | Blocking |
|-----------|---------|-----------|----------|
| Unit Tests | PR, Main | Every commit | Yes |
| Integration Tests | PR, Main | Every commit | Yes |
| E2E Tests | Main | Every commit | Yes |
| Security Scans | PR, Main | Every commit | Yes |
| Load Tests | Staging | Weekly | No |
| Penetration Tests | Production | Quarterly | N/A |

### CI Test Configuration

```yaml
# .github/workflows/ci.yml (test job excerpt)
jobs:
  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml --cov-report=html

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test -- --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

### Test Data Management

**Test Fixtures:**

```python
# tests/conftest.py additions

@pytest.fixture
def security_headers_settings():
    """Override security header settings for testing."""
    from app.core.config import settings
    original = {
        "X_FRAME_OPTIONS": settings.X_FRAME_OPTIONS,
        "CSP_POLICY": settings.CSP_POLICY,
    }
    yield original
    # Restore original settings after test


@pytest.fixture
def mock_sentry():
    """Mock Sentry SDK for testing."""
    with patch("sentry_sdk.capture_exception") as mock:
        yield mock
```

### Performance Baseline Documentation

| Endpoint | Expected P50 | Expected P95 | Expected P99 |
|----------|-------------|-------------|-------------|
| GET /health | < 10ms | < 50ms | < 100ms |
| GET /api/v1/auth/me | < 50ms | < 150ms | < 300ms |
| POST /api/v1/todos | < 100ms | < 300ms | < 500ms |
| GET /api/v1/todos | < 100ms | < 250ms | < 400ms |

### Test Environment Requirements

| Environment | Purpose | Data |
|-------------|---------|------|
| Unit Tests | Isolated testing | Mocked |
| Integration Tests | Component interaction | Test database |
| E2E Tests | Full stack validation | Seeded test data |
| Load Tests | Performance validation | Synthetic data |
| Staging | Pre-production | Production-like |

---

## Implementation Phases

### Overview

Implementation follows a phased approach, with each phase building on the previous one. This ensures stable foundations before adding complex features, and allows for incremental validation and feedback.

### Phase Summary

| Phase | Focus Area | Duration | Dependencies |
|-------|-----------|----------|--------------|
| Phase 1 | CI/CD Foundation | 2-3 weeks | None |
| Phase 2 | Security Hardening | 2 weeks | Phase 1 |
| Phase 3 | Operational Readiness | 2-3 weeks | Phase 1 |
| Phase 4 | Deployment Configuration | 2 weeks | Phase 2, Phase 3 |
| Phase 5 | Developer Experience | 2 weeks | Phase 1, Phase 4 |
| Phase 6 | Documentation & Validation | 1-2 weeks | All phases |

**Total Estimated Duration:** 10-14 weeks

---

### Phase 1: CI/CD Foundation

**Objective:** Establish automated testing and build pipelines as the foundation for all subsequent phases.

**Duration:** 2-3 weeks

**Prerequisites:** None

#### Deliverables

| ID | Deliverable | Priority | Effort |
|----|-------------|----------|--------|
| P1-D1 | GitHub Actions CI workflow (`ci.yml`) | Must Have | 3 days |
| P1-D2 | GitHub Actions build workflow (`build.yml`) | Must Have | 2 days |
| P1-D3 | Production Dockerfile targets (backend, frontend) | Must Have | 2 days |
| P1-D4 | Dependabot configuration | Should Have | 0.5 days |
| P1-D5 | Test coverage reporting (Codecov) | Should Have | 1 day |
| P1-D6 | ADR-019: GitHub Actions CI/CD | Must Have | 1 day |

#### Tasks

**Week 1:**
1. Create `.github/workflows/ci.yml` with lint and test jobs
2. Configure GitHub Actions caching for dependencies
3. Add PostgreSQL and Redis service containers to CI
4. Set up matrix testing for cookiecutter options

**Week 2:**
1. Create production Dockerfile targets with multi-stage builds
2. Implement `.github/workflows/build.yml` for container builds
3. Configure GitHub Container Registry authentication
4. Add multi-platform build support (amd64, arm64)

**Week 3:**
1. Set up Codecov integration
2. Configure Dependabot for automated dependency updates
3. Write ADR-019 documenting CI/CD decisions
4. Validate with template generation tests

#### Acceptance Criteria

- [ ] CI workflow runs on every PR and blocks merge on failure
- [ ] Tests execute in < 10 minutes
- [ ] Container images build and push to ghcr.io on main
- [ ] Multi-platform images available
- [ ] Coverage reports visible in PRs
- [ ] ADR-019 approved and merged

#### Risk Mitigation

- **Risk:** CI flakiness from external services
  - **Mitigation:** Use GitHub-hosted service containers, implement retry logic

- **Risk:** Long build times
  - **Mitigation:** Aggressive caching, parallel job execution

---

### Phase 2: Security Hardening

**Objective:** Implement security scanning, secret detection, and security headers.

**Duration:** 2 weeks

**Prerequisites:** Phase 1 complete

#### Deliverables

| ID | Deliverable | Priority | Effort |
|----|-------------|----------|--------|
| P2-D1 | Security headers middleware | Must Have | 2 days |
| P2-D2 | Trivy container scanning in CI | Must Have | 1 day |
| P2-D3 | pip-audit and npm audit integration | Must Have | 1 day |
| P2-D4 | Gitleaks pre-commit hook | Must Have | 0.5 days |
| P2-D5 | Gitleaks CI scanning | Should Have | 0.5 days |
| P2-D6 | Security configuration settings | Must Have | 1 day |
| P2-D7 | Security audit checklist document | Should Have | 1 day |
| P2-D8 | ADR-020: Security Headers | Must Have | 0.5 days |
| P2-D9 | ADR-022: Container Security Scanning | Must Have | 0.5 days |

#### Tasks

**Week 1:**
1. Implement `SecurityHeadersMiddleware` in `backend/app/middleware/`
2. Add security header configuration to `config.py`
3. Register middleware in `main.py`
4. Write unit tests for security headers
5. Add E2E tests for header verification

**Week 2:**
1. Add Trivy scanning to CI workflow
2. Configure vulnerability thresholds (fail on HIGH/CRITICAL)
3. Add pip-audit to backend CI
4. Add npm audit to frontend CI
5. Configure gitleaks in pre-commit
6. Create security audit checklist document
7. Write ADR-020 and ADR-022

#### Acceptance Criteria

- [ ] All API responses include security headers
- [ ] Security headers are configurable via environment
- [ ] Container scans fail build on HIGH/CRITICAL vulnerabilities
- [ ] Dependency scans fail build on known vulnerabilities
- [ ] Pre-commit hook catches secrets before commit
- [ ] Security checklist is comprehensive and usable
- [ ] ADR-020 and ADR-022 approved

#### Risk Mitigation

- **Risk:** CSP too restrictive, breaks functionality
  - **Mitigation:** Extensive testing, configurable policy, staged rollout

- **Risk:** False positives in secret detection
  - **Mitigation:** Baseline file, allowlist configuration

---

### Phase 3: Operational Readiness

**Objective:** Implement error tracking, alerting, and backup procedures.

**Duration:** 2-3 weeks

**Prerequisites:** Phase 1 complete

#### Deliverables

| ID | Deliverable | Priority | Effort |
|----|-------------|----------|--------|
| P3-D1 | Prometheus alerting rules | Must Have | 2 days |
| P3-D2 | Optional Sentry integration | Should Have | 3 days |
| P3-D3 | Database backup scripts | Must Have | 2 days |
| P3-D4 | Backup Kubernetes CronJob | Should Have | 1 day |
| P3-D5 | Recovery documentation | Must Have | 2 days |
| P3-D6 | Operational runbook templates | Should Have | 2 days |
| P3-D7 | ADR-023: Database Backup Strategy | Must Have | 0.5 days |
| P3-D8 | ADR-024: Sentry Integration | Should Have | 0.5 days |

#### Tasks

**Week 1:**
1. Create `observability/prometheus/alerts.yml`
2. Configure Prometheus to load alert rules
3. Define alerting rules for error rate, latency, resource usage
4. Test alerts with Grafana notification channels

**Week 2:**
1. Implement optional Sentry SDK integration
2. Add Sentry cookiecutter conditional
3. Configure Sentry context injection (tenant_id, user_id)
4. Implement before_send hooks for PII filtering
5. Write Sentry integration tests

**Week 3:**
1. Create `scripts/backup-db.sh` and `scripts/restore-db.sh`
2. Create backup Kubernetes CronJob manifest
3. Write point-in-time recovery documentation
4. Create runbook templates
5. Write ADR-023 and ADR-024

#### Acceptance Criteria

- [ ] Alerts fire correctly for defined conditions
- [ ] Sentry captures errors with appropriate context
- [ ] Sentry filters sensitive data before sending
- [ ] Backup scripts work with configurable retention
- [ ] Recovery procedures are documented and tested
- [ ] Runbook templates are usable
- [ ] ADR-023 and ADR-024 approved

#### Risk Mitigation

- **Risk:** Alert fatigue from noisy rules
  - **Mitigation:** Tuned thresholds, severity levels, documentation

- **Risk:** Sentry sending PII
  - **Mitigation:** before_send hook, send_default_pii=False, testing

---

### Phase 4: Deployment Configuration

**Objective:** Create production-ready Kubernetes manifests and deployment workflows.

**Duration:** 2 weeks

**Prerequisites:** Phase 2 and Phase 3 complete

#### Deliverables

| ID | Deliverable | Priority | Effort |
|----|-------------|----------|--------|
| P4-D1 | Kubernetes base manifests | Must Have | 3 days |
| P4-D2 | Kustomize staging overlay | Should Have | 1 day |
| P4-D3 | Kustomize production overlay | Should Have | 1 day |
| P4-D4 | Deployment workflow (`deploy.yml`) | Should Have | 2 days |
| P4-D5 | Production Docker Compose | Should Have | 1 day |
| P4-D6 | Environment configuration docs | Must Have | 1 day |
| P4-D7 | ADR-021: Kubernetes Deployment | Must Have | 0.5 days |

#### Tasks

**Week 1:**
1. Create `k8s/base/` directory structure
2. Write backend Deployment, Service manifests
3. Write frontend Deployment, Service manifests
4. Create ConfigMap for configuration
5. Create Secret references for sensitive values
6. Write Ingress manifest with TLS

**Week 2:**
1. Create staging overlay with environment patches
2. Create production overlay with replicas, resources
3. Implement deployment workflow with staging/production
4. Add manual approval for production deployments
5. Create `compose.production.yml`
6. Document environment configuration requirements
7. Write ADR-021

#### Acceptance Criteria

- [ ] `kubectl apply -k k8s/overlays/staging` works
- [ ] `kubectl apply -k k8s/overlays/production` works
- [ ] Deployments have resource limits and health probes
- [ ] Pods run as non-root with security context
- [ ] Deployment workflow successfully deploys to staging
- [ ] Production deployment requires manual approval
- [ ] ADR-021 approved

#### Risk Mitigation

- **Risk:** Kubernetes manifest errors discovered in production
  - **Mitigation:** Manifest validation in CI, staging deployment first

- **Risk:** Secrets leaked in manifests
  - **Mitigation:** Use secretRef, not inline values; CI validation

---

### Phase 5: Developer Experience

**Objective:** Add SDK generation, load testing, and API documentation.

**Duration:** 2 weeks

**Prerequisites:** Phase 1 and Phase 4 complete

#### Deliverables

| ID | Deliverable | Priority | Effort |
|----|-------------|----------|--------|
| P5-D1 | OpenAPI Generator configuration | Should Have | 2 days |
| P5-D2 | TypeScript client generation workflow | Could Have | 1 day |
| P5-D3 | k6 load testing scripts | Should Have | 2 days |
| P5-D4 | Load testing CI workflow | Could Have | 1 day |
| P5-D5 | API versioning documentation | Should Have | 1 day |
| P5-D6 | Performance baseline documentation | Should Have | 1 day |

#### Tasks

**Week 1:**
1. Configure OpenAPI Generator for TypeScript
2. Create npm script for client generation
3. (Optional) Add generation to CI on API changes
4. Document API versioning strategy

**Week 2:**
1. Create k6 load test scripts for key endpoints
2. Configure k6 thresholds and checks
3. (Optional) Add load testing workflow
4. Document performance baselines
5. Test complete developer workflow

#### Acceptance Criteria

- [ ] TypeScript client can be generated from openapi.json
- [ ] k6 tests execute and report results
- [ ] Load tests have defined thresholds
- [ ] API versioning strategy is documented
- [ ] Performance baselines are documented

#### Risk Mitigation

- **Risk:** Generated client has compatibility issues
  - **Mitigation:** Version pinning, integration tests

- **Risk:** Load tests affect shared environments
  - **Mitigation:** Dedicated test environment, controlled execution

---

### Phase 6: Documentation & Validation

**Objective:** Complete documentation, validate all features, prepare for release.

**Duration:** 1-2 weeks

**Prerequisites:** All phases complete

#### Deliverables

| ID | Deliverable | Priority | Effort |
|----|-------------|----------|--------|
| P6-D1 | Updated CLAUDE.md with new features | Must Have | 1 day |
| P6-D2 | Migration guide for existing projects | Must Have | 2 days |
| P6-D3 | Cookiecutter template validation | Must Have | 2 days |
| P6-D4 | End-to-end deployment validation | Must Have | 2 days |
| P6-D5 | Release notes | Must Have | 0.5 days |

#### Tasks

**Week 1:**
1. Update CLAUDE.md with all new features and commands
2. Write migration guide for existing projects
3. Test all cookiecutter option combinations
4. Fix any template generation issues

**Week 2:**
1. Perform end-to-end deployment to staging
2. Validate all features work as documented
3. Address any issues found in validation
4. Write release notes
5. Final review and approval

#### Acceptance Criteria

- [ ] CLAUDE.md is comprehensive and accurate
- [ ] Migration guide enables existing project upgrades
- [ ] All cookiecutter combinations generate valid projects
- [ ] E2E deployment succeeds with all features
- [ ] Release notes document all changes

---

### Implementation Timeline

```
Week 1-3:   Phase 1 - CI/CD Foundation
Week 3-5:   Phase 2 - Security Hardening (overlaps Week 3)
Week 3-6:   Phase 3 - Operational Readiness (parallel with Phase 2)
Week 6-8:   Phase 4 - Deployment Configuration
Week 8-10:  Phase 5 - Developer Experience
Week 10-12: Phase 6 - Documentation & Validation
```

**Gantt Chart:**

```
         W1   W2   W3   W4   W5   W6   W7   W8   W9   W10  W11  W12
Phase 1  ████████████
Phase 2           ████████
Phase 3           ████████████
Phase 4                     ████████
Phase 5                               ████████
Phase 6                                        ████████
```

### Rollout Strategy

#### Feature Flags

New features use cookiecutter conditionals:

```json
{
  "include_github_actions": "yes",
  "include_kubernetes": "no",
  "include_sentry": "no"
}
```

**Default Values:**
- `include_github_actions`: "yes" (enabled by default)
- `include_kubernetes`: "no" (opt-in)
- `include_sentry`: "no" (opt-in)

#### Staged Rollout

1. **Alpha:** Feature complete, tested internally
2. **Beta:** Selected users test in their projects
3. **GA:** Documentation complete, stable release

### ADR Summary

| ADR | Title | Phase |
|-----|-------|-------|
| ADR-019 | GitHub Actions CI/CD | Phase 1 |
| ADR-020 | Security Headers | Phase 2 |
| ADR-021 | Kubernetes Deployment | Phase 4 |
| ADR-022 | Container Security Scanning | Phase 2 |
| ADR-023 | Database Backup Strategy | Phase 3 |
| ADR-024 | Optional Sentry Integration | Phase 3 |

### Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| CI pipeline success rate | > 95% | GitHub Actions metrics |
| Time to first deployment | < 2 hours | Timed test |
| Security scan pass rate | 100% | CI results |
| Documentation coverage | 100% | Checklist review |
| User satisfaction | > 4/5 | Feedback survey |

---

## Dependencies & Risks

### External Dependencies

#### Platform Dependencies

| Dependency | Type | Required For | Mitigation if Unavailable |
|------------|------|--------------|---------------------------|
| GitHub Actions | CI/CD Platform | All CI/CD workflows | Manual testing, alternative CI (GitLab CI, CircleCI) |
| GitHub Container Registry (ghcr.io) | Container Registry | Image storage | Docker Hub, AWS ECR, private registry |
| Codecov | Coverage Reporting | PR coverage comments | Local coverage reports, alternative (Coveralls) |
| Sentry (Optional) | Error Tracking | Production error monitoring | Structured logging, self-hosted Sentry |
| Trivy | Security Scanning | Vulnerability detection | Snyk, Grype, manual audits |

#### Infrastructure Dependencies

| Dependency | Version | Purpose | Criticality |
|------------|---------|---------|-------------|
| Kubernetes | 1.25+ | Container orchestration | High (for K8s deployment) |
| PostgreSQL | 15+ | Primary database | Critical |
| Redis | 7+ | Caching, rate limiting | High |
| Keycloak | 22+ | OAuth/OIDC provider | Critical |
| Prometheus | 2.45+ | Metrics collection | Medium |
| Grafana | 10+ | Dashboard visualization | Medium |

#### Library Dependencies

**Backend (Python):**

| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| sentry-sdk | ^2.0 | Error tracking (optional) | MIT |
| pip-audit | ^2.6 | Dependency scanning | Apache 2.0 |

**Frontend (Node.js):**

| Library | Version | Purpose | License |
|---------|---------|---------|---------|
| @sentry/browser | ^8.0 | Error tracking (optional) | MIT |

**DevOps Tools:**

| Tool | Version | Purpose | License |
|------|---------|---------|---------|
| Trivy | Latest | Container/dependency scanning | Apache 2.0 |
| gitleaks | v8.18+ | Secret detection | MIT |
| k6 | Latest | Load testing | AGPL-3.0 |
| Kustomize | v5+ | K8s configuration | Apache 2.0 |

### Internal Dependencies

#### Codebase Dependencies

| Component | Depends On | Nature |
|-----------|-----------|--------|
| Security Headers Middleware | FastAPI, Starlette | Runtime |
| Sentry Integration | FastAPI, Pydantic, Redis | Runtime |
| Alerting Rules | Prometheus, Grafana | Configuration |
| Kubernetes Manifests | Docker Images | Deployment |
| CI Workflows | Test Suite, Dockerfiles | Build |
| Backup Scripts | PostgreSQL client tools | Operations |

#### Feature Dependencies

```
Phase 1: CI/CD Foundation
    └── Phase 2: Security Hardening
    └── Phase 3: Operational Readiness
            └── Phase 4: Deployment Configuration
                    └── Phase 5: Developer Experience
                            └── Phase 6: Documentation & Validation
```

### Team Dependencies

| Team/Role | Involvement | Phase |
|-----------|-------------|-------|
| DevOps/Platform | Kubernetes setup, CI/CD configuration | Phase 1, 4 |
| Security | Security review, audit checklist validation | Phase 2 |
| Backend | Security headers, Sentry integration | Phase 2, 3 |
| Frontend | Security headers compliance, Sentry integration | Phase 2, 3 |
| Documentation | CLAUDE.md, migration guides | Phase 6 |
| QA | E2E validation, load testing | Phase 5, 6 |

### Risk Register

#### High Priority Risks

| ID | Risk | Likelihood | Impact | Mitigation Strategy | Owner |
|----|------|------------|--------|---------------------|-------|
| R1 | CI/CD pipeline flakiness delays releases | Medium | High | Implement retry logic, use service containers, monitor flaky tests | DevOps |
| R2 | Security headers break existing functionality | Medium | High | Extensive testing, configurable headers, staged rollout, CSP report-only mode | Backend |
| R3 | Kubernetes manifests incorrect for production | Low | Critical | Manifest validation in CI, staging deployment first, infrastructure-as-code review | DevOps |
| R4 | Secret exposure through CI/CD logs | Low | Critical | Secret masking, audit logging, minimal secret scope | Security |
| R5 | Backup scripts fail silently | Medium | Critical | Alert on backup failure, test restoration monthly, backup verification | DevOps |

#### Medium Priority Risks

| ID | Risk | Likelihood | Impact | Mitigation Strategy | Owner |
|----|------|------------|--------|---------------------|-------|
| R6 | Trivy false positives block valid PRs | Medium | Medium | Baseline file, severity thresholds, exception process | Security |
| R7 | Sentry rate limits exceeded | Low | Medium | Sampling configuration, quota monitoring, fallback to logging | Backend |
| R8 | k6 load tests affect production | Low | Medium | Dedicated test environment, controlled execution windows | QA |
| R9 | Alerting rules too noisy | Medium | Medium | Threshold tuning, severity levels, alert aggregation | DevOps |
| R10 | Multi-platform builds increase CI time | High | Medium | Build caching, parallel builds, schedule non-blocking builds | DevOps |

#### Low Priority Risks

| ID | Risk | Likelihood | Impact | Mitigation Strategy | Owner |
|----|------|------------|--------|---------------------|-------|
| R11 | OpenAPI client generation has breaking changes | Low | Low | Version pinning, integration tests, manual review | Frontend |
| R12 | Dependabot creates too many PRs | Medium | Low | Configuration tuning, batch updates, auto-merge for patches | DevOps |
| R13 | Documentation becomes outdated | Medium | Low | Documentation tests, review checklist, versioned docs | Documentation |

### Risk Mitigation Details

#### R1: CI/CD Pipeline Flakiness

**Detection:**
- Monitor CI job failure rates
- Track retry frequency
- Identify flaky tests

**Prevention:**
- Use deterministic tests (no random data, fixed timestamps)
- Mock external services
- Use GitHub service containers for databases
- Implement test isolation

**Response:**
- Quarantine flaky tests
- Add retry logic for transient failures
- Document known flaky scenarios

#### R2: Security Headers Breaking Functionality

**Detection:**
- CSP violation reports (if CSP_REPORT_URI configured)
- Browser console errors in testing
- User-reported functionality issues

**Prevention:**
- Start with CSP in report-only mode
- Extensive E2E testing across browsers
- Document header configuration options
- Gradual rollout with monitoring

**Response:**
- Immediate header configuration adjustment
- Rollback capability via environment variables
- Post-incident header policy review

#### R3: Kubernetes Manifest Errors

**Detection:**
- CI manifest validation (`kubectl apply --dry-run`)
- Staging deployment failures
- Pod crash loops in production

**Prevention:**
- Kubeval/kubeconform validation in CI
- Required staging deployment before production
- Infrastructure-as-code review process
- Resource limit validation

**Response:**
- Documented rollback procedure
- Previous deployment preserved
- Incident review and manifest update

#### R4: Secret Exposure

**Detection:**
- gitleaks alerts
- GitHub secret scanning alerts
- Audit log review

**Prevention:**
- Pre-commit hooks for secret detection
- CI secret scanning
- Minimal secret scope in workflows
- Secret masking in logs

**Response:**
- Immediate secret rotation
- Audit affected systems
- Incident report and root cause analysis

#### R5: Backup Script Failures

**Detection:**
- Backup job exit code monitoring
- Prometheus alert on backup age
- Missing backup file alerts

**Prevention:**
- Exit code validation
- Backup verification (checksum, restore test)
- Monitoring and alerting
- Monthly restore drills

**Response:**
- Immediate manual backup
- Root cause investigation
- Script fix and validation

### Dependency Version Management

#### Version Pinning Strategy

| Dependency Type | Strategy | Update Frequency |
|-----------------|----------|------------------|
| Runtime Libraries | Pin major.minor | Monthly review |
| Dev Dependencies | Pin major.minor | Monthly review |
| GitHub Actions | Pin to version tag | Quarterly review |
| Base Images | Pin to specific tag | Security updates immediately |
| Kubernetes API | Target latest stable | Annual review |

#### Breaking Change Management

1. **Monitor** release notes for pinned dependencies
2. **Test** updates in isolated branch
3. **Stage** updates in staging environment
4. **Deploy** with rollback capability
5. **Document** required migration steps

### Contingency Plans

#### CI/CD Platform Unavailable

**Scenario:** GitHub Actions outage prevents CI/CD execution

**Contingency:**
1. Local test execution with documented commands
2. Manual security scanning with Trivy CLI
3. Manual image build and push
4. Manual deployment via kubectl

**Recovery:**
1. Re-run failed workflows when service restored
2. Verify deployment state matches expected
3. Review incident impact

#### Container Registry Unavailable

**Scenario:** ghcr.io outage prevents image pull/push

**Contingency:**
1. Use locally cached images for deployment
2. Push to backup registry (Docker Hub)
3. Update deployment manifests with backup registry

**Recovery:**
1. Re-push images to primary registry
2. Update deployments to use primary registry
3. Verify image consistency

#### Sentry Unavailable

**Scenario:** Sentry service outage

**Impact:** Error tracking disabled (application continues to function)

**Contingency:**
1. Errors continue to be logged via structured logging
2. Loki/Grafana provides backup error visibility
3. Manual log review for critical errors

**Recovery:**
1. Sentry SDK automatically reconnects
2. Backlog of errors may be lost (acceptable)
3. Verify error reporting resumes

### Success Criteria for Risk Mitigation

| Metric | Target | Measurement |
|--------|--------|-------------|
| CI failure rate (non-test) | < 2% | GitHub Actions metrics |
| Security scan false positive rate | < 5% | Manual review of blocked PRs |
| Backup success rate | 100% | Backup monitoring alerts |
| Secret exposure incidents | 0 | Security incident count |
| MTTR for deployment issues | < 30 minutes | Incident tracking |

### Risk Review Schedule

| Review Type | Frequency | Participants |
|-------------|-----------|--------------|
| Risk register update | Monthly | DevOps, Security |
| Incident retrospective | Per incident | All affected teams |
| Dependency audit | Quarterly | DevOps, Backend, Frontend |
| Security review | Quarterly | Security, Backend |
| Disaster recovery drill | Bi-annually | DevOps, Backend |

---

## Open Questions

- Should CI/CD be template-agnostic or provide specific GitHub Actions/GitLab CI examples?
- What level of Kubernetes support is needed (Helm, Kustomize, or plain manifests)?
- Should the template include optional Celery/background job support similar to observability?
- What secrets management providers should be prioritized?
- Should this be a single large FRD or broken into multiple focused FRDs?

---

## Status

**Ready for FRD Refiner - All Sections Complete**

**Last Updated:** 2025-12-05

**Completed Sections:**
1. Problem Statement - Comprehensive analysis of current state and 10 identified gaps
2. Goals & Success Criteria - Defined metrics, success indicators, and non-goals
3. Scope & Boundaries - Clear 4-phase approach with explicit exclusions
4. User Stories / Use Cases - 5 epics with 15 user stories, personas, and edge cases
5. Functional Requirements - 78 requirements across 6 categories with MoSCoW prioritization
6. Technical Approach - Technology stack, implementation strategies, cookiecutter integration
7. Architecture & Integration Considerations - System diagrams, API contracts, performance requirements
8. Data Models & Schema Changes - No schema changes required; configuration patterns documented
9. UI/UX Considerations - Developer and operator experience enhancements
10. Security & Privacy Considerations - Security headers, vulnerability scanning, OWASP coverage
11. Testing Strategy - 4-level test approach with unit, integration, E2E, and security tests
12. Implementation Phases - 6 phases over 10-14 weeks with detailed deliverables
13. Dependencies & Risks - 13 risks identified with mitigation strategies

**Progress:** 100% (13/13 sections complete)

**Summary Statistics:**
- Total Functional Requirements: 78
- Must Have Requirements: 32
- Should Have Requirements: 35
- Could Have Requirements: 11
- ADRs to Create: 6 (ADR-019 through ADR-024)
- Estimated Implementation Duration: 10-14 weeks
- High Priority Risks: 5
- Medium Priority Risks: 5
- Low Priority Risks: 3

**Key Decisions Made:**
- GitHub Actions for CI/CD (primary platform)
- Kustomize over Helm for Kubernetes configuration
- Trivy for container and dependency scanning
- Sentry as optional error tracking (cookiecutter conditional)
- No database schema changes required

**Related Future FRDs:**
- Background Jobs and Task Queue System
- Email/Notification Infrastructure
- Webhook Processing Patterns
- Complete Admin Dashboard
- Advanced Kubernetes Configuration (HPA, PDB, etc.)

**Next Steps:**
1. FRD Refiner review for coherence and completeness
2. Stakeholder review and approval
3. ADR drafting for Phase 1
4. Implementation kickoff
