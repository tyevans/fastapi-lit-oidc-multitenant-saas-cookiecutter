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
