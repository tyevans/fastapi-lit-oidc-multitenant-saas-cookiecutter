# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack multi-tenant {{ cookiecutter.project_name }} application with OAuth 2.0 authentication and Row-Level Security.

**Stack:**
- Backend: FastAPI (Python {{ cookiecutter.python_version }}) with async SQLAlchemy, PostgreSQL {{ cookiecutter.postgres_version }}, Redis {{ cookiecutter.redis_version }}
- Frontend: Lit 3.x web components with Vite 5.x, TypeScript, Tailwind CSS
- Auth: Keycloak {{ cookiecutter.keycloak_version }} (OAuth 2.0/OIDC with PKCE)
- Infrastructure: Docker Compose ({% if cookiecutter.include_observability == "yes" %}10{% else %}5{% endif %} services)
{% if cookiecutter.include_observability == "yes" %}- Observability: Grafana, Prometheus, Loki, Tempo{% endif %}

## Development Commands

### Docker (Recommended)
```bash
./scripts/docker-dev.sh up              # Start all services
./scripts/docker-dev.sh down            # Stop services
./scripts/docker-dev.sh logs [service]  # View logs (backend, frontend, postgres, redis, keycloak)
./scripts/docker-dev.sh shell backend   # Interactive shell in backend container
./scripts/docker-dev.sh reset           # Full clean restart
```

### Backend (cd backend/)
```bash
# Testing
pytest                                   # All tests
pytest tests/unit/test_file.py -v       # Single test file
pytest -m unit                          # Unit tests only
pytest -m integration                   # Integration tests only
pytest --cov=app --cov-report=html      # With coverage

# Linting & Formatting
ruff check .                            # Lint
ruff check --fix                        # Auto-fix
ruff format                             # Format

# Database Migrations (inside container)
alembic upgrade head                    # Apply all migrations
alembic downgrade -1                    # Rollback one version
alembic revision --autogenerate -m "description"  # Create migration
```

### Frontend (cd frontend/)
```bash
npm run dev                             # Dev server (localhost:{{ cookiecutter.frontend_port }})
npm test                                # Vitest watch mode
npm run test:e2e                        # Playwright E2E tests
npm run test:e2e:ui                     # Playwright interactive UI
npm run lint                            # ESLint
npm run format                          # Prettier
npm run build                           # Production build
```

## Architecture

### Backend Structure
```
backend/app/
├── main.py              # FastAPI app entry point
├── api/
│   ├── dependencies/    # DI: auth.py, database.py, tenant.py, scopes.py
│   └── routers/         # Endpoints: health, auth, oauth, todos, test_auth
├── core/                # config.py, database.py, cache.py, security.py
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic request/response schemas
├── services/            # Business logic (JWKS client, token revocation, tenant context)
└── middleware/          # Tenant context middleware
```

### Frontend Structure
```
frontend/src/
├── main.ts              # Entry point with routing
├── api/                 # Type-safe HTTP client (client.ts, types.ts)
├── auth/                # OIDC client (config.ts, service.ts, store.ts)
└── components/          # Lit web components
```

## Key Patterns

### Authentication Flow
1. Frontend uses `oidc-client-ts` for PKCE authorization code flow with Keycloak
2. Backend validates JWT tokens via JWKS (public keys cached from Keycloak)
3. Token revocation tracked in Redis blacklist
4. Rate limiting (Redis) protects auth endpoints

### Multi-Tenancy
- `tenant_id` claim extracted from JWT token
- PostgreSQL Row-Level Security (RLS) enforces data isolation
- Two database users: `{{ cookiecutter.postgres_migration_user }}` (BYPASSRLS) and `{{ cookiecutter.postgres_app_user }}` (RLS enforced)
- Tenant context set via middleware → database session variable → RLS policies

### Route Protection
```python
# Require authentication (CurrentUser dependency)
async def endpoint(user: CurrentUser):
    return {"user_id": user.user_id, "tenant_id": user.tenant_id}

# Require specific scopes
from app.api.dependencies.scopes import require_scopes, require_any_scope

@router.post("/data")
async def create_data(_: None = Depends(require_scopes("data/write"))):
    ...

@router.get("/data")
async def get_data(_: None = Depends(require_any_scope("data/read", "data/read/mine"))):
    ...
```

### API Client (Frontend)
```typescript
// Authenticated request (default)
const response = await apiClient.get<DataType>('{{ cookiecutter.backend_api_prefix }}/endpoint')

// Public endpoint (no auth header)
const response = await apiClient.get<DataType>('{{ cookiecutter.backend_api_prefix }}/public', { authenticated: false })

if (response.success) {
  // response.data is typed
} else {
  // response.error has status, message, timestamp
}
```

## Service Ports
| Service    | Port |
|------------|------|
| Frontend   | {{ cookiecutter.frontend_port }} |
| Backend    | {{ cookiecutter.backend_port }} |
| PostgreSQL | {{ cookiecutter.postgres_port }} |
| Redis      | {{ cookiecutter.redis_port }} |
| Keycloak   | {{ cookiecutter.keycloak_port }} |
{% if cookiecutter.include_observability == "yes" %}| Grafana    | {{ cookiecutter.grafana_port }} |
| Prometheus | {{ cookiecutter.prometheus_port }} |
| Loki       | {{ cookiecutter.loki_port }} |
| Tempo      | {{ cookiecutter.tempo_http_port }} |
{% endif %}

## Initial Setup
```bash
cp .env.example .env
./scripts/docker-dev.sh up
./keycloak/setup-realm.sh              # Creates OAuth realm and test users
./scripts/docker-dev.sh shell backend
alembic upgrade head                   # Apply migrations
```

Test users: `alice@example.com`, `bob@example.com` (password: `password123`)

## Key Configuration Files
- Backend config: `backend/app/core/config.py` (pydantic-settings)
- Environment: `.env` (copy from `.env.example`)
- Docker: `compose.yml`
- Frontend env: `VITE_API_URL` for backend API URL

For comprehensive configuration documentation, see:
- `docs/operations/environment-configuration.md` - Complete environment variable reference
- `docs/operations/secrets-management.md` - Production secrets patterns
- `docs/operations/configuration-validation.md` - Troubleshooting guide
{% if cookiecutter.include_github_actions == "yes" %}
## CI/CD Pipeline

GitHub Actions workflows are configured for automated testing, building, and deployment.

### Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR, push to main | Lint, test, coverage |
| `build.yml` | Push to main | Build and push Docker images |
| `deploy.yml` | Manual, tag | Deploy to staging/production |
| `security.yml` | Schedule, PR | Security scanning (Trivy, CodeQL) |

### Common Commands

```bash
# View workflow runs
gh run list

# View specific workflow run
gh run view <run-id>

# View run logs
gh run view <run-id> --log

# Re-run failed workflow
gh run rerun <run-id>

# Trigger deployment manually
gh workflow run deploy.yml -f environment=staging -f image_tag=latest

# View workflow status
gh workflow view ci.yml
```

### Container Registry

Images are pushed to GitHub Container Registry:
```bash
# Pull backend image
docker pull ghcr.io/{{ cookiecutter.github_username | lower }}/{{ cookiecutter.project_slug }}-backend:latest

# Pull frontend image
docker pull ghcr.io/{{ cookiecutter.github_username | lower }}/{{ cookiecutter.project_slug }}-frontend:latest

# List available tags
gh api /user/packages/container/{{ cookiecutter.project_slug }}-backend/versions --jq '.[].metadata.container.tags[]'
```

### Dependabot

Automated dependency updates are configured in `.github/dependabot.yml`:
- Python dependencies (weekly)
- npm dependencies (weekly)
- Docker base images (weekly)
- GitHub Actions (weekly)
{% endif %}
## Security Configuration

### Security Headers

Security headers are added via middleware (`backend/app/middleware/security.py`). Configure via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECURITY_HEADERS_ENABLED` | `true` | Enable/disable security headers |
| `X_FRAME_OPTIONS` | `DENY` | Clickjacking protection |
| `CONTENT_TYPE_OPTIONS` | `nosniff` | Prevent MIME sniffing |
| `XSS_PROTECTION` | `1; mode=block` | XSS filter |
| `CSP_ENABLED` | `true` | Enable Content Security Policy |
| `HSTS_ENABLED` | `true` | HTTP Strict Transport Security |
| `HSTS_MAX_AGE` | `31536000` | HSTS max-age (1 year) |

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run gitleaks --all-files

# Skip hooks temporarily (not recommended)
git commit --no-verify -m "message"
```

### Secret Detection

Gitleaks is configured for secret detection (`.gitleaks.toml`):
```bash
# Scan for secrets
gitleaks detect --source . --verbose

# Scan specific commit range
gitleaks detect --source . --log-opts="HEAD~10..HEAD"

# Generate baseline (for existing secrets to ignore)
gitleaks detect --source . --report-path=.gitleaks-baseline.json
```

## Load Testing (k6)

k6 scripts are available in `tests/load/` for performance testing.

### Running Tests

```bash
# Using the load test script
./scripts/load-test.sh smoke         # Quick validation (1 min)
./scripts/load-test.sh load          # Sustained load (5 min)
./scripts/load-test.sh stress        # Find breaking point (10 min)
./scripts/load-test.sh spike         # Traffic spike simulation
./scripts/load-test.sh soak          # Extended duration test

# Run specific scenario
k6 run tests/load/scenarios/health-check.js

# Run with custom options
k6 run tests/load/scenarios/api-crud.js --vus 50 --duration 2m

# Run with environment variables
K6_BASE_URL=https://staging.example.com k6 run tests/load/scenarios/auth-flow.js
```

### Test Configuration

Configure via environment variables:
- `K6_BASE_URL`: Target URL (default: `http://localhost:{{ cookiecutter.backend_port }}`)
- `K6_VUS`: Virtual users (varies by test type)
- `K6_DURATION`: Test duration (varies by test type)
- `K6_ITERATIONS`: Fixed iteration count (optional)

### Viewing Results

```bash
# Console output (default)
k6 run tests/load/scenarios/smoke.js

# JSON output
k6 run tests/load/scenarios/smoke.js --out json=results.json

# For InfluxDB + Grafana integration
k6 run --out influxdb=http://localhost:8086/k6 tests/load/scenarios/smoke.js
```

See `tests/load/README.md` for detailed documentation and performance baselines.

## API Client Generation

TypeScript API clients can be generated from the OpenAPI spec.

### Generation

```bash
# Generate client (requires backend running)
./scripts/generate-api-client.sh

# Validate OpenAPI spec only
./scripts/generate-api-client.sh --validate

# Generate with custom output directory
./scripts/generate-api-client.sh --output frontend/src/api/generated

# From frontend directory
cd frontend && npm run generate:api
```

### Generated Client Usage

```typescript
import { DefaultApi, Configuration } from './api/generated';

const config = new Configuration({
  basePath: import.meta.env.VITE_API_URL,
  accessToken: async () => await authService.getAccessToken()
});

const api = new DefaultApi(config);

// Type-safe API calls
const health = await api.healthCheck();
const todos = await api.listTodos({ limit: 10, offset: 0 });
```

### OpenAPI Configuration

Configuration in `frontend/openapitools.json`:
```json
{
  "generator-cli": {
    "version": "7.0.0",
    "generators": {
      "typescript-fetch": {
        "inputSpec": "http://localhost:{{ cookiecutter.backend_port }}/openapi.json",
        "output": "src/api/generated"
      }
    }
  }
}
```

## Database Operations

### Backup

```bash
# Create backup (uses Docker by default)
./scripts/db-backup.sh

# Backup with custom retention (days)
BACKUP_RETENTION_DAYS=30 ./scripts/db-backup.sh

# Backup to S3
BACKUP_S3_ENABLED=true \
BACKUP_S3_BUCKET=my-backup-bucket \
BACKUP_S3_REGION=us-east-1 \
./scripts/db-backup.sh

# Backup with encryption
BACKUP_ENCRYPTION_ENABLED=true \
BACKUP_ENCRYPTION_KEY="your-32-byte-key" \
./scripts/db-backup.sh
```

### Restore

```bash
# Restore from latest backup
./scripts/db-restore.sh --latest

# Restore from specific file
./scripts/db-restore.sh --file backups/backup_20240101_120000.sql.gz

# Restore with verification
./scripts/db-restore.sh --file backup.sql.gz --verify

# Dry run (show what would be restored)
./scripts/db-restore.sh --latest --dry-run
```

### Verification

```bash
# Verify backup integrity
./scripts/db-verify.sh backups/backup_20240101_120000.sql.gz

# Verify and test restore to temporary database
./scripts/db-verify.sh backups/backup.sql.gz --test-restore
```

### Migrations

```bash
# Apply all pending migrations
./scripts/docker-dev.sh shell backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "add_user_preferences_table"

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# View migration history
alembic history --verbose

# Show current revision
alembic current
```

## Troubleshooting

### CI Pipeline Issues

**Problem:** Workflow fails with "permission denied"
```bash
# Check repository permissions
# Settings > Actions > General > Workflow permissions
# Ensure "Read and write permissions" is selected

# For GHCR push issues, verify package permissions
gh api /user/packages/container/{{ cookiecutter.project_slug }}-backend
```

**Problem:** Tests fail in CI but pass locally
```bash
# Check for environment differences
# Ensure CI uses same Python/Node versions as local
python --version  # Should match ci.yml PYTHON_VERSION
node --version    # Should match ci.yml NODE_VERSION

# Check for hardcoded paths or ports
grep -r "localhost:8000" tests/
```

**Problem:** Docker build fails in CI
```bash
# Clean Docker cache locally
docker builder prune -f

# Rebuild without cache
docker compose build --no-cache backend

# Check for layer caching issues
docker compose build --progress=plain backend 2>&1 | tee build.log
```

### Security Headers Issues

**Problem:** CSP blocks legitimate resources
```bash
# Check current CSP header
curl -I http://localhost:{{ cookiecutter.backend_port }}/health | grep -i content-security

# Update CSP in .env
CSP_DIRECTIVES="default-src 'self'; script-src 'self' 'unsafe-inline' https://trusted-cdn.com"
```

**Problem:** CORS errors with security headers
```bash
# Verify CORS and security header order
# Security headers should come after CORS middleware
# Check backend/app/main.py for middleware order
```

### Database Issues

**Problem:** Connection pool exhausted
```bash
# Check active connections
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} \
  -c "SELECT count(*) FROM pg_stat_activity WHERE datname = '{{ cookiecutter.postgres_db }}';"

# View connection details
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} \
  -c "SELECT pid, usename, application_name, state, query_start FROM pg_stat_activity WHERE datname = '{{ cookiecutter.postgres_db }}';"

# Terminate idle connections
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} \
  -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{{ cookiecutter.postgres_db }}' AND state = 'idle' AND query_start < now() - interval '10 minutes';"
```

**Problem:** Backup script fails
```bash
# Check Docker socket permissions
ls -la /var/run/docker.sock

# Verify backup directory exists and is writable
ls -la backups/

# Run backup with debug output
BACKUP_DEBUG=true ./scripts/db-backup.sh
```

### Load Testing Issues

**Problem:** k6 connection errors
```bash
# Verify target is accessible
curl -v http://localhost:{{ cookiecutter.backend_port }}/health

# Check for rate limiting
# Reduce VUs or add think time
k6 run --vus 5 --duration 30s tests/load/scenarios/smoke.js
```

**Problem:** High error rate in load tests
```bash
# Check backend logs during test
./scripts/docker-dev.sh logs backend

# Monitor resource usage
docker stats

# Check for connection pool issues
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -c "SHOW max_connections;"
```
{% if cookiecutter.include_kubernetes == "yes" %}
### Kubernetes Issues

**Problem:** Pods stuck in ImagePullBackOff
```bash
# Check pod status
kubectl describe pod -n {{ cookiecutter.project_slug }} -l app.kubernetes.io/component=backend

# Verify image exists
docker pull ghcr.io/{{ cookiecutter.github_username | lower }}/{{ cookiecutter.project_slug }}-backend:latest

# Check image pull secrets
kubectl get secret -n {{ cookiecutter.project_slug }} regcred -o yaml
```

**Problem:** ConfigMap changes not reflected
```bash
# Trigger rollout restart
kubectl rollout restart deployment/backend -n {{ cookiecutter.project_slug }}

# Watch rollout status
kubectl rollout status deployment/backend -n {{ cookiecutter.project_slug }}
```

**Problem:** Service not accessible
```bash
# Check service endpoints
kubectl get endpoints -n {{ cookiecutter.project_slug }}

# Check ingress status
kubectl describe ingress -n {{ cookiecutter.project_slug }}

# Port forward for debugging
kubectl port-forward svc/backend 8000:8000 -n {{ cookiecutter.project_slug }}
```
{% endif %}
For more detailed troubleshooting, see:
- `docs/runbooks/` - Operational runbooks for common issues
- `docs/operations/configuration-validation.md` - Configuration troubleshooting
{% if cookiecutter.include_observability == "yes" %}
## Observability Stack

The project includes a complete observability stack for monitoring, logging, and tracing.

### Service URLs

| Service | Port | URL |
|---------|------|-----|
| Grafana | {{ cookiecutter.grafana_port }} | http://localhost:{{ cookiecutter.grafana_port }} |
| Prometheus | {{ cookiecutter.prometheus_port }} | http://localhost:{{ cookiecutter.prometheus_port }} |
| Loki | {{ cookiecutter.loki_port }} | http://localhost:{{ cookiecutter.loki_port }} |
| Tempo | {{ cookiecutter.tempo_http_port }} | http://localhost:{{ cookiecutter.tempo_http_port }} |

### Common Commands

```bash
# View observability logs
docker compose logs grafana
docker compose logs prometheus
docker compose logs loki
docker compose logs tempo
docker compose logs promtail

# Restart observability stack
docker compose restart grafana prometheus loki tempo promtail

# Check Prometheus targets
curl http://localhost:{{ cookiecutter.prometheus_port }}/api/v1/targets

# Query backend metrics
curl http://localhost:{{ cookiecutter.backend_port }}/metrics
```

### Useful PromQL Queries

```promql
# Request rate
rate(http_requests_total{job="backend"}[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="backend"}[5m]))

# Error rate
rate(http_requests_total{job="backend",status=~"5.."}[5m])

# Active requests
active_requests
```

### Useful LogQL Queries

```logql
# Backend logs
{service="backend"}

# Error logs only
{service="backend"} |= "ERROR"

# Logs with trace ID
{service="backend"} | json | trace_id != ""
```
{% endif %}
{%- if cookiecutter.include_kubernetes == "yes" %}

## Kubernetes Deployment

The project includes Kustomize-based Kubernetes manifests for production deployment.

### Deployment Commands

```bash
# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to production
kubectl apply -k k8s/overlays/production

# Check deployment status
kubectl get all -n {{ cookiecutter.project_slug }}

# View logs
kubectl logs -n {{ cookiecutter.project_slug }} -l app.kubernetes.io/component=backend

# Port forward for local access
kubectl port-forward -n {{ cookiecutter.project_slug }} svc/backend 8000:8000
```

### Structure

| Directory | Purpose |
|-----------|---------|
| k8s/base/ | Shared manifests (deployments, services, ingress) |
| k8s/overlays/staging/ | Staging overrides (reduced replicas) |
| k8s/overlays/production/ | Production overrides (HA, PDB) |

### Key Resources

| Resource | File | Description |
|----------|------|-------------|
| Namespace | namespace.yaml | Isolated namespace for the project |
| Backend | backend-deployment.yaml | FastAPI backend pods |
| Frontend | frontend-deployment.yaml | Nginx frontend pods |
| ConfigMap | configmap.yaml | Non-sensitive configuration |
| Secret | secret.yaml | Secret template (create manually) |
| Ingress | ingress.yaml | TLS ingress configuration |

### Secrets Management

Secrets should not be committed to version control. Create them manually:

```bash
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --namespace {{ cookiecutter.project_slug }} \
  --from-literal=DATABASE_URL='postgresql+asyncpg://...' \
  --from-literal=REDIS_URL='redis://...'
```

Or use external secret management (Sealed Secrets, External Secrets Operator, Vault).
{%- endif %}
{%- if cookiecutter.include_sentry == "yes" %}

## Error Tracking (Sentry)

The project includes optional Sentry integration for production error tracking.

### Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `SENTRY_DSN` | Sentry project DSN | `{{ cookiecutter.sentry_dsn }}` |
| `SENTRY_ENVIRONMENT` | Environment tag | `development` |
| `SENTRY_RELEASE` | Release version | `APP_VERSION` |
| `SENTRY_TRACES_SAMPLE_RATE` | Trace sampling rate | `0.1` |
| `SENTRY_PROFILES_SAMPLE_RATE` | Profile sampling rate | `0.1` |

### Features

- Automatic exception capture with stack traces
- Multi-tenant context (tenant_id, user_id attached to errors)
- PII filtering via before_send hook (passwords, tokens filtered)
- FastAPI and SQLAlchemy integrations
- Fail-open pattern (app runs normally if Sentry is unavailable)

### Usage

Sentry is automatically initialized on application startup if `SENTRY_DSN` is configured.
User context is automatically set after successful authentication.

```python
# Manual message capture (optional)
from app.sentry import capture_message, capture_exception

# Capture custom event
capture_message("Important event", level="info", custom_data="value")

# Capture handled exception
try:
    risky_operation()
except Exception as e:
    capture_exception(e, operation="risky_operation")
    # Handle gracefully
```

### Breadcrumbs and Tags

```python
from app.sentry import add_breadcrumb, set_tag, set_context

# Add breadcrumb for debugging trail
add_breadcrumb("User clicked checkout", category="ui", level="info")

# Set searchable tag
set_tag("feature", "checkout")

# Set structured context
set_context("order", {"order_id": "123", "total": 99.99})
```
{% endif %}
