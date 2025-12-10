# E2E Validation Checklist

Use this checklist to manually validate the Production Essentials features before a release.

## Prerequisites

Before starting validation, ensure you have:

- [ ] Docker Desktop or Docker Engine running (with at least 8GB RAM allocated)
- [ ] `kubectl` installed (for Kubernetes validation)
- [ ] `cookiecutter` installed (`pip install cookiecutter`)
- [ ] `jq` installed (for JSON parsing in scripts)
- [ ] Ports 3000, 5173, 8000, 8080, 9090 available

## Automated Validation

Run the automated E2E validation script:

```bash
./scripts/run-e2e-validation.sh
```

Options:
- `CLEANUP=false` - Keep generated project for inspection
- `SKIP_DOCKER=true` - Skip Docker builds (faster, syntax validation only)
- `SKIP_K8S=true` - Skip Kubernetes validation
- `VERBOSE=true` - Show detailed output

## Manual Validation Steps

### 1. Template Generation

#### All Features Enabled
- [ ] Generate with all options enabled:
  ```bash
  cookiecutter template/ --no-input \
    project_name="Full Test" \
    include_observability=yes \
    include_github_actions=yes \
    include_kubernetes=yes \
    include_sentry=yes
  ```
- [ ] No Jinja2 errors during generation
- [ ] Project directory created with expected name

#### Minimal Configuration
- [ ] Generate with all options disabled:
  ```bash
  cookiecutter template/ --no-input \
    project_name="Minimal Test" \
    include_observability=no \
    include_github_actions=no \
    include_kubernetes=no \
    include_sentry=no
  ```
- [ ] No errors during generation
- [ ] No observability, .github, k8s, or sentry files present

### 2. File Structure Validation

#### Core Files Present
- [ ] `compose.yml` exists and is valid YAML
- [ ] `backend/app/main.py` exists
- [ ] `backend/pyproject.toml` exists
- [ ] `frontend/package.json` exists
- [ ] `frontend/src/main.ts` exists
- [ ] `.env.example` exists with all required variables

#### Conditional Files (when enabled)
- [ ] `.github/workflows/ci.yml` present (if include_github_actions=yes)
- [ ] `.github/workflows/build.yml` present (if include_github_actions=yes)
- [ ] `k8s/base/kustomization.yaml` present (if include_kubernetes=yes)
- [ ] `k8s/overlays/staging/` present (if include_kubernetes=yes)
- [ ] `k8s/overlays/production/` present (if include_kubernetes=yes)
- [ ] `observability/` directory present (if include_observability=yes)
- [ ] `backend/app/sentry.py` present (if include_sentry=yes)

### 3. Docker Compose Deployment

#### Service Startup
- [ ] Run `docker compose up -d --build`
- [ ] All containers start without immediate crashes
- [ ] Backend container stays running
- [ ] Frontend container stays running
- [ ] PostgreSQL container shows as healthy
- [ ] Redis container shows as healthy

#### Health Endpoints
- [ ] Backend health: `curl http://localhost:8000/api/v1/health` returns 200
- [ ] Frontend accessible: `curl http://localhost:5173` returns HTML
- [ ] OpenAPI docs: `curl http://localhost:8000/docs` returns HTML

#### Database Connectivity
- [ ] PostgreSQL accessible:
  ```bash
  docker compose exec postgres pg_isready -U <project>_user
  ```
- [ ] Migrations applied:
  ```bash
  docker compose exec backend alembic current
  ```

#### Redis Connectivity
- [ ] Redis responds:
  ```bash
  docker compose exec redis redis-cli ping
  ```
  Should return: PONG

#### Keycloak (if applicable)
- [ ] Keycloak ready: `curl http://localhost:8080/health/ready`
- [ ] Admin console accessible: http://localhost:8080/admin

### 4. Security Headers

Check response headers from backend:

```bash
curl -sI http://localhost:8000/api/v1/health
```

- [ ] `X-Content-Type-Options: nosniff` present
- [ ] `X-Frame-Options` present (DENY or SAMEORIGIN)
- [ ] `Referrer-Policy` present
- [ ] `Content-Security-Policy` present (if configured)

### 5. Observability Stack (if enabled)

#### Prometheus
- [ ] Prometheus accessible: http://localhost:9090
- [ ] Health check: `curl http://localhost:9090/-/healthy`
- [ ] Targets configured: Check http://localhost:9090/targets

#### Grafana
- [ ] Grafana accessible: http://localhost:3000
- [ ] Health check: `curl http://localhost:3000/api/health`
- [ ] Default credentials work (admin/admin)
- [ ] Prometheus data source configured

#### Backend Metrics
- [ ] Metrics endpoint: `curl http://localhost:8000/metrics`
- [ ] `http_requests_total` metric present
- [ ] `http_request_duration_seconds` metric present

#### Alerting Rules
- [ ] Rules loaded: Check http://localhost:9090/api/v1/rules
- [ ] At least one rule group present

### 6. CI/CD Workflows (if enabled)

#### Workflow Syntax
- [ ] `ci.yml` is valid YAML with name, on, jobs keys
- [ ] `build.yml` is valid YAML with name, on, jobs keys
- [ ] No syntax errors when parsed

#### Local Simulation
- [ ] Backend linting passes:
  ```bash
  cd backend && uv run ruff check app/
  ```
- [ ] Backend tests run:
  ```bash
  cd backend && uv run pytest
  ```
- [ ] Frontend linting passes:
  ```bash
  cd frontend && npm run lint
  ```
- [ ] Frontend tests run:
  ```bash
  cd frontend && npm test
  ```

### 7. Kubernetes Manifests (if enabled)

#### Kustomize Rendering
- [ ] Staging renders:
  ```bash
  kubectl kustomize k8s/overlays/staging
  ```
- [ ] Production renders:
  ```bash
  kubectl kustomize k8s/overlays/production
  ```

#### Manifest Validation
- [ ] Dry-run succeeds:
  ```bash
  kubectl apply -k k8s/overlays/staging --dry-run=client
  ```
- [ ] Deployments defined
- [ ] Services defined
- [ ] ConfigMaps defined
- [ ] Resource limits specified

#### Production Differences
- [ ] Production has higher replica counts
- [ ] Production has production-specific configurations

### 8. Database Operations

#### Migrations
- [ ] Alembic upgrade works:
  ```bash
  docker compose exec backend alembic upgrade head
  ```
- [ ] Current revision shows:
  ```bash
  docker compose exec backend alembic current
  ```

#### Backup Scripts (if present)
- [ ] Backup script exists: `scripts/backup-db.sh`
- [ ] Backup creates file:
  ```bash
  ./scripts/backup-db.sh
  ```
- [ ] Backup file is valid gzip

#### Restore Scripts (if present)
- [ ] Restore script exists: `scripts/restore-db.sh`
- [ ] Restore from latest works:
  ```bash
  ./scripts/restore-db.sh --latest
  ```

### 9. API Client Generation (if enabled)

- [ ] Generate script exists: `scripts/generate-api-client.sh`
- [ ] Validation passes:
  ```bash
  ./scripts/generate-api-client.sh --validate
  ```
- [ ] Client generates successfully

### 10. Load Testing (if present)

- [ ] k6 scripts exist in `tests/load/`
- [ ] Smoke test runs:
  ```bash
  k6 run tests/load/smoke.js
  ```

### 11. Security Checks

#### Secret Detection
- [ ] No hardcoded passwords in Python files
- [ ] No API keys committed
- [ ] `.env.example` has placeholder values only

#### Configuration Security
- [ ] DEBUG mode configurable via environment
- [ ] Secret key configurable via environment
- [ ] Database password configurable via environment

### 12. Cleanup

- [ ] Services stop cleanly:
  ```bash
  docker compose down -v
  ```
- [ ] No orphaned containers
- [ ] No orphaned volumes
- [ ] No orphaned networks

## Sign-Off

### Test Environment

| Item | Value |
|------|-------|
| Docker Version | |
| Python Version | |
| Node Version | |
| OS | |
| Date | |

### Results Summary

| Category | Passed | Failed | Skipped |
|----------|--------|--------|---------|
| Template Generation | | | |
| File Structure | | | |
| Docker Compose | | | |
| Security Headers | | | |
| Observability | | | |
| CI/CD | | | |
| Kubernetes | | | |
| Database | | | |
| Security | | | |
| **Total** | | | |

### Validator Information

- **Name:** ________________________
- **Date:** ________________________
- **Version:** ________________________

### Notes and Issues Found

```
(Document any issues, warnings, or observations here)




```

### Approval

- [ ] All critical tests passed
- [ ] No blocking issues found
- [ ] Ready for release

**Signed:** ________________________ **Date:** ________________________
