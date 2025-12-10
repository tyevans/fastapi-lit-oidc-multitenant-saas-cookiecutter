# P6-02: Create Migration Guide for Existing Projects

## Task Identifier
**ID:** P6-02
**Phase:** 6 - Documentation and Validation
**Domain:** Documentation
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| All P1-P5 tasks | Informational | Pending | Must know all features to create migration steps |
| P1-01 through P1-06 | CI/CD features | Must complete | CI/CD migration steps |
| P2-01 through P2-08 | Security features | Must complete | Security migration steps |
| P3-01 through P3-11 | Operational features | Must complete | Operational migration steps |
| P4-01 through P4-08 | Kubernetes features | Must complete | K8s migration steps |
| P5-01 through P5-05 | DX features | Must complete | DX migration steps |

## Scope

### In Scope
- Create comprehensive migration guide for projects generated from older template versions
- Document step-by-step procedures for each major feature area
- Provide file-by-file migration instructions with diffs where helpful
- Include compatibility notes and breaking changes
- Create checklist for migration verification
- Document rollback procedures if migration causes issues
- Provide version compatibility matrix

### Out of Scope
- Automated migration scripts (documented as future enhancement)
- Database schema migrations (handled separately by Alembic)
- Support for projects not generated from this template
- Migration from other frameworks (e.g., Django to FastAPI)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/docs/
  MIGRATION.md                              # Main migration guide
  migrations/
    v1.x-to-v2.0.md                        # Version-specific migration (if needed)
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/.github/workflows/ci.yml
template/{{cookiecutter.project_slug}}/.github/workflows/build.yml
template/{{cookiecutter.project_slug}}/backend/app/middleware/security_headers.py
template/{{cookiecutter.project_slug}}/backend/app/core/config.py
template/{{cookiecutter.project_slug}}/observability/prometheus/alerts.yml
template/{{cookiecutter.project_slug}}/k8s/base/
template/{{cookiecutter.project_slug}}/scripts/backup-db.sh
```

## Implementation Details

### 1. Migration Guide Structure (`docs/MIGRATION.md`)

```markdown
# Migration Guide

This guide helps you upgrade existing projects generated from earlier versions of the {{ cookiecutter.project_name }} template to include Production Essentials features.

## Table of Contents

1. [Version Compatibility](#version-compatibility)
2. [Pre-Migration Checklist](#pre-migration-checklist)
3. [Feature Migration Guides](#feature-migration-guides)
   - [CI/CD Pipeline](#cicd-pipeline)
   - [Security Hardening](#security-hardening)
   - [Operational Readiness](#operational-readiness)
   - [Kubernetes Deployment](#kubernetes-deployment)
   - [Developer Experience](#developer-experience)
4. [Post-Migration Verification](#post-migration-verification)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)

---

## Version Compatibility

| Feature | Minimum Template Version | Dependencies |
|---------|-------------------------|--------------|
| CI/CD Pipeline | 2.0.0 | None |
| Security Headers | 2.0.0 | None |
| Sentry Integration | 2.0.0 | `include_sentry=yes` |
| Kubernetes Manifests | 2.0.0 | `include_kubernetes=yes` |
| k6 Load Testing | 2.0.0 | None |
| API Client Generation | 2.0.0 | None |

### Breaking Changes in 2.0.0

1. **New cookiecutter variables**: `include_github_actions`, `include_kubernetes`, `include_sentry`
2. **Config.py additions**: Security header settings added
3. **New middleware**: `security_headers.py` added to middleware stack
4. **Prometheus config**: `alerts.yml` referenced in `prometheus.yml`

---

## Pre-Migration Checklist

Before starting migration, ensure:

- [ ] Current project is in a clean git state (no uncommitted changes)
- [ ] All tests pass in current state
- [ ] Database backup is available
- [ ] You have reviewed the breaking changes above
- [ ] Required environment variables are documented for your deployment

### Backup Your Project

```bash
# Create a backup branch
git checkout -b pre-migration-backup
git push origin pre-migration-backup

# Return to main branch
git checkout main
```

---

## Feature Migration Guides

### CI/CD Pipeline

**Files to add:**
```
.github/
  workflows/
    ci.yml
    build.yml
    deploy.yml
  dependabot.yml
```

**Steps:**

1. **Create workflow directory:**
   ```bash
   mkdir -p .github/workflows
   ```

2. **Copy CI workflow:**
   Copy `.github/workflows/ci.yml` from a fresh template generation or from the template repository.

3. **Update workflow with your project specifics:**
   ```yaml
   # In ci.yml, update:
   env:
     PYTHON_VERSION: "{{ cookiecutter.python_version }}"  # Your Python version
     NODE_VERSION: "20"  # Your Node.js version
   ```

4. **Copy build workflow:**
   Copy `.github/workflows/build.yml` and update:
   ```yaml
   # Update registry and image names
   env:
     REGISTRY: ghcr.io
     IMAGE_NAME_BACKEND: ${{ github.repository }}-backend
     IMAGE_NAME_FRONTEND: ${{ github.repository }}-frontend
   ```

5. **Copy Dependabot config:**
   Copy `.github/dependabot.yml` as-is.

6. **Test locally:**
   ```bash
   # Verify workflows are valid
   gh workflow list
   ```

**Verification:**
- [ ] CI workflow runs on PR
- [ ] Build workflow runs on merge to main
- [ ] Dependabot creates dependency PRs

---

### Security Hardening

**Files to add/modify:**

| File | Action |
|------|--------|
| `backend/app/middleware/security_headers.py` | Add |
| `backend/app/core/config.py` | Modify |
| `backend/app/main.py` | Modify |
| `.pre-commit-config.yaml` | Modify |

**Steps:**

1. **Add security headers middleware:**
   Create `backend/app/middleware/security_headers.py`:
   ```python
   """Security headers middleware for FastAPI."""
   from starlette.middleware.base import BaseHTTPMiddleware
   from starlette.requests import Request
   from starlette.responses import Response

   from app.core.config import settings


   class SecurityHeadersMiddleware(BaseHTTPMiddleware):
       """Add security headers to all responses."""

       async def dispatch(self, request: Request, call_next) -> Response:
           response = await call_next(request)

           response.headers["X-Content-Type-Options"] = "nosniff"
           response.headers["X-Frame-Options"] = settings.X_FRAME_OPTIONS
           response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

           if settings.CSP_POLICY:
               response.headers["Content-Security-Policy"] = settings.CSP_POLICY

           if request.url.scheme == "https" or settings.FORCE_HSTS:
               response.headers["Strict-Transport-Security"] = (
                   f"max-age={settings.HSTS_MAX_AGE}; includeSubDomains"
               )

           return response
   ```

2. **Add settings to config.py:**
   ```python
   # Add to Settings class in backend/app/core/config.py

   # Security Headers
   X_FRAME_OPTIONS: str = "DENY"
   CSP_POLICY: str = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'"
   FORCE_HSTS: bool = False
   HSTS_MAX_AGE: int = 31536000  # 1 year
   ```

3. **Add middleware to main.py:**
   ```python
   # In backend/app/main.py, after CORS middleware

   from app.middleware.security_headers import SecurityHeadersMiddleware

   # Add after CORSMiddleware
   app.add_middleware(SecurityHeadersMiddleware)
   ```

4. **Update pre-commit config:**
   Add to `.pre-commit-config.yaml`:
   ```yaml
   - repo: https://github.com/gitleaks/gitleaks
     rev: v8.18.0
     hooks:
       - id: gitleaks
   ```

5. **Install updated hooks:**
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

**Verification:**
- [ ] Security headers appear in API responses
- [ ] Pre-commit hooks run gitleaks
- [ ] No secrets detected in codebase

---

### Operational Readiness

**Files to add:**

| File | Action |
|------|--------|
| `observability/prometheus/alerts.yml` | Add |
| `observability/prometheus/prometheus.yml` | Modify |
| `scripts/backup-db.sh` | Add |
| `scripts/restore-db.sh` | Add |
| `docs/runbooks/` | Add directory |

**Steps:**

1. **Add Prometheus alerting rules:**
   Create `observability/prometheus/alerts.yml`:
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
   ```

2. **Update prometheus.yml:**
   Add to `observability/prometheus/prometheus.yml`:
   ```yaml
   rule_files:
     - /etc/prometheus/alerts.yml
   ```

3. **Update Docker Compose (observability):**
   Add volume mount for alerts:
   ```yaml
   prometheus:
     volumes:
       - ./observability/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
       - ./observability/prometheus/alerts.yml:/etc/prometheus/alerts.yml:ro
   ```

4. **Add backup scripts:**
   Copy `scripts/backup-db.sh` and `scripts/restore-db.sh` from template.

5. **Make scripts executable:**
   ```bash
   chmod +x scripts/backup-db.sh scripts/restore-db.sh
   ```

**Verification:**
- [ ] Prometheus loads alerting rules
- [ ] Backup script creates valid backups
- [ ] Restore script can restore from backup

---

### Kubernetes Deployment

**Files to add:**
```
k8s/
  base/
    kustomization.yaml
    backend-deployment.yaml
    backend-service.yaml
    frontend-deployment.yaml
    frontend-service.yaml
    configmap.yaml
    secrets.yaml
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

**Steps:**

1. **Create directory structure:**
   ```bash
   mkdir -p k8s/base k8s/overlays/staging k8s/overlays/production
   ```

2. **Copy base manifests:**
   Copy all files from `k8s/base/` in a fresh template generation.

3. **Copy overlay manifests:**
   Copy files from `k8s/overlays/staging/` and `k8s/overlays/production/`.

4. **Customize for your project:**
   - Update image names in deployments
   - Update ConfigMap values
   - Update Ingress hosts
   - Update resource requests/limits

5. **Test manifests:**
   ```bash
   # Validate syntax
   kubectl kustomize k8s/overlays/staging

   # Dry run
   kubectl apply -k k8s/overlays/staging --dry-run=client
   ```

**Verification:**
- [ ] Kustomize renders manifests without errors
- [ ] Manifests apply to a test cluster
- [ ] Services are reachable after deployment

---

### Developer Experience

**Files to add:**

| File | Action |
|------|--------|
| `frontend/openapitools.json` | Add |
| `frontend/.openapi-generator-ignore` | Add |
| `scripts/generate-api-client.sh` | Add |
| `tests/load/smoke.js` | Add |
| `tests/load/load.js` | Add |
| `docs/API_VERSIONING.md` | Add |

**Steps:**

1. **Add OpenAPI Generator config:**
   Copy `frontend/openapitools.json` from template.

2. **Add generator ignore file:**
   Copy `frontend/.openapi-generator-ignore` from template.

3. **Add generation script:**
   Copy `scripts/generate-api-client.sh` and make executable:
   ```bash
   chmod +x scripts/generate-api-client.sh
   ```

4. **Add k6 load tests:**
   ```bash
   mkdir -p tests/load
   ```
   Copy test files from template.

5. **Install frontend dependencies:**
   ```bash
   cd frontend
   npm install --save-dev @openapitools/openapi-generator-cli
   ```

6. **Test generation:**
   ```bash
   ./scripts/generate-api-client.sh --validate
   ```

**Verification:**
- [ ] API client generates without errors
- [ ] k6 tests run successfully
- [ ] Generated client compiles with TypeScript

---

## Post-Migration Verification

Run this checklist after completing migration:

### Core Functionality
- [ ] All existing tests pass
- [ ] Application starts without errors
- [ ] Authentication flow works
- [ ] Database operations work

### New Features
- [ ] CI pipeline runs on PR (if GitHub Actions added)
- [ ] Security headers present in responses
- [ ] Prometheus loads alerting rules (if observability enabled)
- [ ] Backup script creates valid backup
- [ ] API client generates successfully

### Integration
- [ ] Pre-commit hooks run without errors
- [ ] Docker build completes
- [ ] Kubernetes manifests validate (if added)

---

## Troubleshooting

### CI Pipeline Issues

**Problem:** Workflow fails with "permission denied"
```bash
# Ensure GITHUB_TOKEN has correct permissions
# Check repository Settings > Actions > General > Workflow permissions
```

**Problem:** Tests fail in CI but pass locally
```bash
# Check for environment differences
# Ensure CI uses same Python/Node versions
# Check for hardcoded paths or ports
```

### Security Headers Issues

**Problem:** CSP blocks legitimate resources
```bash
# Update CSP_POLICY in .env to allow required sources
CSP_POLICY="default-src 'self'; script-src 'self' 'unsafe-inline' https://trusted-cdn.com"
```

**Problem:** HSTS breaks local development
```bash
# Ensure FORCE_HSTS=false for development
# Only enable in production with HTTPS
```

### Kubernetes Issues

**Problem:** ImagePullBackOff error
```bash
# Check image name and tag
kubectl describe pod <pod-name>

# Verify registry credentials
kubectl get secret regcred -o yaml
```

**Problem:** ConfigMap not updating
```bash
# Trigger rollout restart
kubectl rollout restart deployment/backend
```

---

## Rollback Procedures

### Quick Rollback (Git)

```bash
# Revert to pre-migration state
git checkout pre-migration-backup
git checkout -b main-rollback
git push origin main-rollback

# If confident, reset main
git checkout main
git reset --hard pre-migration-backup
git push --force-with-lease origin main
```

### Partial Rollback

To remove specific features:

**Remove CI/CD:**
```bash
rm -rf .github/workflows
git add -A && git commit -m "Remove CI/CD workflows"
```

**Remove Security Headers:**
```bash
rm backend/app/middleware/security_headers.py
# Revert config.py and main.py changes
git checkout HEAD~1 -- backend/app/core/config.py backend/app/main.py
```

**Remove Kubernetes:**
```bash
rm -rf k8s/
git add -A && git commit -m "Remove Kubernetes manifests"
```

---

## Getting Help

If you encounter issues during migration:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review the [ADR documentation](../decisions/) for design rationale
3. Open an issue in the template repository
4. Reach out to the maintainers

---

*Last updated: {{ cookiecutter.project_name }} Template v2.0.0*
```

### 2. Version-Specific Migration (Optional)

If semantic versioning is implemented, create version-specific guides:

```markdown
# docs/migrations/v1.x-to-v2.0.md

# Migration from v1.x to v2.0

This guide covers specific changes when upgrading from template version 1.x to 2.0.

## Breaking Changes

1. **cookiecutter.json additions**
   - `include_github_actions` (default: "yes")
   - `include_kubernetes` (default: "no")
   - `include_sentry` (default: "no")

2. **Config.py schema changes**
   - Added security header settings
   - Added optional Sentry settings

3. **New middleware**
   - SecurityHeadersMiddleware added to stack
   - Order: CORS -> Security Headers -> Tenant -> ...

## Detailed Changes

[... specific diffs and migration steps ...]
```

## Success Criteria

### Functional Requirements
- [ ] Migration guide covers all Phase 1-5 features
- [ ] Step-by-step instructions are clear and complete
- [ ] File paths and code snippets are accurate
- [ ] Verification steps are included for each section
- [ ] Rollback procedures are documented
- [ ] Troubleshooting covers common issues

### Verification Steps
1. **Walkthrough Test:**
   ```bash
   # Generate old-style project (simulate pre-migration)
   cookiecutter . --no-input \
     include_github_actions=no \
     include_kubernetes=no \
     include_sentry=no

   # Follow migration guide step by step
   # Verify each section's verification steps pass
   ```

2. **Documentation Review:**
   - All code snippets are syntactically correct
   - All file paths are valid
   - All commands are functional

3. **User Testing:**
   - Have someone unfamiliar with the project follow the guide
   - Document any unclear steps or missing information

### Quality Gates
- [ ] Guide is comprehensive (covers all features)
- [ ] Instructions are sequential and logical
- [ ] Code examples are tested and working
- [ ] Links to related documentation are valid
- [ ] Rollback procedures are safe and tested

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| All P1-P5 tasks | Implementations | Must match actual implementations |
| P6-01 | CLAUDE.md | Reference for command examples |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-05 | Release notes | Migration guide linked in release |

### Integration Contract
```yaml
# Contract: Migration guide structure

# Required sections
- Version Compatibility
- Pre-Migration Checklist
- Feature Migration Guides (one per feature area)
- Post-Migration Verification
- Troubleshooting
- Rollback Procedures

# Each feature migration includes
- Files to add/modify
- Step-by-step instructions
- Code snippets
- Verification checklist
```

## Monitoring and Observability

### Documentation Metrics
- Migration success rate (users who complete without issues)
- Common failure points (which steps cause problems)
- Time to migrate (typical duration)

### Feedback Collection
- Issue templates for migration problems
- Link to feedback form in guide

## Infrastructure Needs

### None Required
This is a documentation-only task. No infrastructure changes needed.

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Significant documentation to write
- Must accurately reflect all Phase 1-5 implementations
- Code snippets must be tested
- Troubleshooting section requires anticipating issues
- Coordination with all previous tasks

## Notes

### Design Decisions

**1. Single Comprehensive Guide:**
- One main MIGRATION.md file
- Optional version-specific guides as needed
- Easier to maintain than multiple scattered docs

**2. Feature-Based Organization:**
- Grouped by feature area (CI/CD, Security, etc.)
- Allows partial migration
- Users can skip features they don't need

**3. Copy-Based Migration:**
- Recommend copying files from fresh generation
- Safer than patching existing files
- Easier to maintain consistency

**4. Verification at Each Step:**
- Checklist after each section
- Catches issues early
- Builds confidence

### Related Requirements
- FRD mentions "Migration path for existing projects" in Technical Approach section
- Users with existing projects need clear upgrade path
- Documentation completeness is a success criterion

### Coordination Notes
- Must wait for Phase 1-5 implementations to finalize
- May need updates if implementations differ from specs
- Review migration steps against actual file structures
