# {{ cookiecutter.project_name }}

{% if cookiecutter.include_github_actions == "yes" %}[![CI](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/ci.yml/badge.svg)](https://github.com/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }}/graph/badge.svg)](https://codecov.io/gh/{{ cookiecutter.github_username }}/{{ cookiecutter.project_slug }})
{% endif %}
{{ cookiecutter.project_short_description }}

## Architecture

This project is a full-stack web application with:

- **Backend**: FastAPI (Python {{ cookiecutter.python_version }}) with async SQLAlchemy ORM
- **Frontend**: Lit web components with Vite bundler
- **Database**: PostgreSQL {{ cookiecutter.postgres_version }} with Row-Level Security
- **OAuth**: Keycloak {{ cookiecutter.keycloak_version }} (OIDC/OAuth 2.0)
- **Cache**: Redis {{ cookiecutter.redis_version }} for distributed caching
- **Orchestration**: Docker Compose for local development
{% if cookiecutter.include_observability == "yes" %}- **Observability**: Grafana, Prometheus, Loki, Tempo (metrics, logs, traces){% endif %}

## Features

- ✅ Multi-tenant architecture with tenant isolation
- ✅ OAuth 2.0 Authorization Code flow with PKCE
- ✅ JWT validation with JWKS caching
- ✅ Distributed rate limiting with Redis
- ✅ Token revocation and logout
- ✅ Database migrations with Alembic
- ✅ Comprehensive testing (pytest, Playwright)
- ✅ Hot reload for development
- ✅ API documentation with OpenAPI/Swagger
- ✅ Health check endpoints

## Quick Start

### Prerequisites

- Docker & Docker Compose
- `jq` (for Keycloak setup scripts)

### 1. Start Services

```bash
# Copy environment template (if not already done)
cp .env.example .env

# Review and update .env as needed
nano .env

# Start all services
./scripts/docker-dev.sh up
```

This starts:
- PostgreSQL on port {{ cookiecutter.postgres_port }}
- Redis on port {{ cookiecutter.redis_port }}
- Keycloak on port {{ cookiecutter.keycloak_port }}
- Backend on port {{ cookiecutter.backend_port }}
- Frontend on port {{ cookiecutter.frontend_port }}
{% if cookiecutter.include_observability == "yes" %}- Grafana on port {{ cookiecutter.grafana_port }}
- Prometheus on port {{ cookiecutter.prometheus_port }}
- Loki on port {{ cookiecutter.loki_port }}
- Tempo on port {{ cookiecutter.tempo_http_port }}{% endif %}

### 2. Set Up Keycloak

```bash
# Wait for Keycloak to be ready (1-2 minutes)
# Then create the OAuth realm and test users
./keycloak/setup-realm.sh
```

This creates:
- Realm: `{{ cookiecutter.keycloak_realm_name }}`
- Backend client: `{{ cookiecutter.keycloak_backend_client_id }}` (confidential)
- Frontend client: `{{ cookiecutter.keycloak_frontend_client_id }}` (public with PKCE)
- Test users (password: `password123`):
  - alice@example.com (Tenant: 11111111-1111-1111-1111-111111111111)
  - bob@example.com (Tenant: 11111111-1111-1111-1111-111111111111)
  - charlie@demo.example (Tenant: 22222222-2222-2222-2222-222222222222)
  - diana@demo.example (Tenant: 22222222-2222-2222-2222-222222222222)

### 3. Run Database Migrations

```bash
# Open backend shell
./scripts/docker-dev.sh shell backend

# Inside container:
alembic upgrade head
exit
```

### 4. Access Your Application

- **Frontend**: http://localhost:{{ cookiecutter.frontend_port }}
- **Backend API**: http://localhost:{{ cookiecutter.backend_port }}
- **API Documentation**: http://localhost:{{ cookiecutter.backend_port }}/docs
- **Keycloak Admin**: http://localhost:{{ cookiecutter.keycloak_port }}/admin
  - Username: `{{ cookiecutter.keycloak_admin }}`
  - Password: `{{ cookiecutter.keycloak_admin_password }}`
{% if cookiecutter.include_observability == "yes" %}- **Grafana**: http://localhost:{{ cookiecutter.grafana_port }} (no login required)
- **Prometheus**: http://localhost:{{ cookiecutter.prometheus_port }}{% endif %}

{% if cookiecutter.include_observability == "yes" %}
## Observability Stack

This project includes a pre-configured observability stack for metrics, logs, and distributed tracing.

### Services

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | http://localhost:{{ cookiecutter.grafana_port }} | Dashboards and visualization |
| Prometheus | http://localhost:{{ cookiecutter.prometheus_port }} | Metrics collection |
| Loki | http://localhost:{{ cookiecutter.loki_port }} | Log aggregation |
| Tempo | http://localhost:{{ cookiecutter.tempo_http_port }} | Distributed tracing |

### Quick Start

1. Access Grafana at http://localhost:{{ cookiecutter.grafana_port }} (no login required)
2. Navigate to **Dashboards** > **Backend Service Dashboard**
3. Use **Explore** to query logs (Loki) and traces (Tempo)

### Key Endpoints

- **Backend Metrics**: http://localhost:{{ cookiecutter.backend_port }}/metrics
- **Prometheus UI**: http://localhost:{{ cookiecutter.prometheus_port }}

### Learn More

See [observability/README.md](./observability/README.md) for detailed documentation on:
- Viewing logs with LogQL queries
- Exploring traces with TraceQL
- Querying metrics with PromQL
- Creating custom dashboards
- Troubleshooting common issues

{% endif %}
## Development

### Docker Helper Script

```bash
./scripts/docker-dev.sh [command]

Commands:
  up              Start all services
  down            Stop all services
  restart         Restart all services
  build           Build service images
  rebuild         Rebuild without cache
  logs [service]  Show logs (optional service filter)
  ps              Show running containers
  shell [service] Open shell (default: backend)
  clean           Remove containers and volumes
  reset           Full reset (clean + rebuild + start)
```

### Backend Development

#### Local Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

#### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test file
pytest tests/unit/test_oauth_client.py

# Integration tests only
pytest tests/integration/
```

#### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "add users table"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1

# View migration history
alembic history
```

#### Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── api/
│   │   ├── dependencies/    # Dependency injection
│   │   │   ├── auth.py      # JWT validation
│   │   │   ├── database.py  # DB session
│   │   │   └── tenant.py    # Tenant context
│   │   └── routers/         # API endpoints
│   │       ├── health.py    # Health checks
│   │       ├── oauth.py     # OAuth flow
│   │       └── auth.py      # Token management
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── cache.py         # Redis cache
│   │   └── security.py      # JWT utilities
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── middleware/          # Custom middleware
├── alembic/                 # Database migrations
├── tests/                   # Test suite
└── requirements.txt         # Dependencies
```

### Frontend Development

#### Local Setup

```bash
cd frontend
npm install
```

#### Running Development Server

```bash
# With Docker (hot reload enabled)
./scripts/docker-dev.sh up

# Or locally
npm run dev
```

#### Running Tests

```bash
# Unit tests
npm test

# E2E tests
npm run test:e2e

# E2E with UI
npm run test:e2e -- --ui
```

#### Project Structure

```
frontend/
├── src/
│   ├── main.ts              # Entry point
│   ├── api/
│   │   ├── client.ts        # HTTP client
│   │   ├── types.ts         # TypeScript types
│   │   └── health.ts        # API methods
│   ├── components/          # Lit web components
│   │   └── health-check.ts  # Example component
│   └── style.css            # Global styles
├── e2e/                     # Playwright E2E tests
├── package.json             # Dependencies
└── vite.config.ts           # Vite configuration
```

## OAuth Integration

### Backend: Token Validation

```python
from fastapi import Depends
from app.api.dependencies.auth import get_current_user
from app.schemas.auth import AuthenticatedUser

@router.get("/protected")
async def protected_endpoint(
    current_user: AuthenticatedUser = Depends(get_current_user)
):
    # JWT automatically validated
    # User info available
    return {
        "user_id": current_user.sub,
        "email": current_user.email,
        "tenant_id": current_user.tenant_id
    }
```

### Frontend: Login Flow

```typescript
// Redirect to OAuth login
const loginResponse = await fetch('{{ cookiecutter.backend_api_prefix }}/oauth/login');
const { auth_url } = await loginResponse.json();
window.location.href = auth_url;

// Handle OAuth callback
const params = new URLSearchParams(window.location.search);
await fetch(`{{ cookiecutter.backend_api_prefix }}/oauth/callback?code=${params.get('code')}&state=${params.get('state')}`);

// Make authenticated requests
const response = await fetch('{{ cookiecutter.backend_api_prefix }}/protected', {
  credentials: 'include'  // Send HTTP-only auth cookie
});
```

## Multi-Tenancy

This application uses multi-tenant architecture with:

- **Tenant ID in JWT**: Custom claim in Keycloak tokens
- **Row-Level Security (RLS)**: PostgreSQL policies enforce data isolation
- **Tenant Context**: Middleware automatically sets tenant context from JWT

### Database Roles

- **{{ cookiecutter.postgres_migration_user }}**: For migrations (has BYPASSRLS)
- **{{ cookiecutter.postgres_app_user }}**: For application runtime (RLS enforced)

### Usage

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.context import get_tenant_context

async def get_users(db: AsyncSession):
    # Tenant context automatically set by middleware
    tenant_id = get_tenant_context()

    # RLS policies automatically filter by tenant
    result = await db.execute(select(User))
    return result.scalars().all()
```

## Rate Limiting

Distributed rate limiting using Redis:

```python
from app.core.rate_limit import RateLimiter

@router.post("/api/expensive-operation")
async def expensive_operation(request: Request):
    # Check rate limit
    await rate_limiter.check_rate_limit(
        key=f"operation:{request.client.host}",
        max_requests=10,
        window_seconds=60
    )
    # Operation logic...
```

Configuration in `.env`:
```bash
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_WINDOW_SECONDS=60
```

## Token Revocation

Logout with token blacklisting:

```python
from app.services.token_revocation import revoke_token

@router.post("/logout")
async def logout(
    current_user: AuthenticatedUser = Depends(get_current_user),
    token: str = Depends(get_bearer_token)
):
    await revoke_token(token, current_user.exp)
    response = JSONResponse({"message": "Logged out"})
    response.delete_cookie("access_token")
    return response
```

Tokens are stored in Redis blacklist until expiration.

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# General
ENV=development
DEBUG=true

# Database
POSTGRES_DB={{ cookiecutter.postgres_db }}
POSTGRES_USER={{ cookiecutter.postgres_user }}
POSTGRES_PASSWORD={{ cookiecutter.postgres_password }}

# Redis
REDIS_PASSWORD={{ cookiecutter.redis_password }}

# API
API_V1_PREFIX={{ cookiecutter.backend_api_prefix }}

# Keycloak
KEYCLOAK_ADMIN={{ cookiecutter.keycloak_admin }}
KEYCLOAK_ADMIN_PASSWORD={{ cookiecutter.keycloak_admin_password }}
```

See `.env.example` for complete list.

## Keycloak Configuration

### Access Admin Console

http://localhost:{{ cookiecutter.keycloak_port }}/admin

- Username: `{{ cookiecutter.keycloak_admin }}`
- Password: `{{ cookiecutter.keycloak_admin_password }}`

### OIDC Discovery

http://localhost:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}/.well-known/openid-configuration

### Export Realm Configuration

```bash
./keycloak/export-realm.sh
```

## Troubleshooting

### Services not healthy

```bash
# Check status
docker compose ps

# View logs
./scripts/docker-dev.sh logs [service]

# Restart service
docker compose restart [service]
```

### Keycloak realm setup fails

```bash
# Ensure Keycloak is healthy
curl http://localhost:{{ cookiecutter.keycloak_port }}/health

# Check admin credentials in .env
echo $KEYCLOAK_ADMIN
echo $KEYCLOAK_ADMIN_PASSWORD

# Try setup again
./keycloak/setup-realm.sh
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker compose ps postgres

# Test connection
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }}

# Check logs
./scripts/docker-dev.sh logs postgres
```

### OAuth token validation fails

```bash
# Check JWKS endpoint
curl http://localhost:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}/.well-known/openid-configuration | jq .jwks_uri

# Check backend can reach Keycloak
docker compose exec backend curl http://keycloak:8080/health

# Review backend logs
./scripts/docker-dev.sh logs backend
```

## Production Deployment
{%- if cookiecutter.include_kubernetes == "yes" %}

### Kubernetes Deployment

This project includes Kubernetes manifests for deployment using Kustomize.

#### Quick Start

```bash
# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to production
kubectl apply -k k8s/overlays/production
```

#### Structure

```
k8s/
  base/                 # Base manifests (shared)
  overlays/
    staging/            # Staging environment
    production/         # Production environment
```

#### Prerequisites

- Kubernetes cluster (1.25+)
- kubectl with cluster access
- External PostgreSQL and Redis
- OAuth provider (Keycloak)

See [k8s/README.md](k8s/README.md) for detailed deployment instructions.

{%- endif %}

### Build for Production

```bash
# Build production images
docker compose build --target production

# Push to registry
docker compose push
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong OAuth client secrets
- [ ] Enable HTTPS for all services
- [ ] Use secret management (not .env files)
- [ ] Review and restrict CORS origins
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Review rate limiting settings
- [ ] Enable Keycloak security features
- [ ] Use managed PostgreSQL service
- [ ] Set up SSL/TLS for database connections

## License

{{ cookiecutter.license }}

## Author

{{ cookiecutter.author_name }} <{{ cookiecutter.author_email }}>

---

Built with FastAPI, Lit, PostgreSQL, Keycloak, and Docker Compose
