# P4-05: Create Production Docker Compose File

## Task Identifier
**ID:** P4-05
**Phase:** 4 - Kubernetes Deployment
**Domain:** DevOps
**Complexity:** S (Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P1-03 | Required | Documented | Production Dockerfiles must exist for image references |

## Scope

### In Scope
- Create `compose.production.yml` for production deployments without Kubernetes
- Configure backend and frontend services with production targets
- Configure external database and Redis connection support
- Remove development volumes and hot-reload configurations
- Add resource limits for container memory and CPU
- Include health checks with appropriate production timeouts
- Create `.env.production.example` template file
- Document usage and deployment patterns

### Out of Scope
- Kubernetes manifests (handled by P4-01 through P4-03)
- Observability stack configuration (separate compose profile)
- Docker Swarm mode configuration (future enhancement)
- Load balancer/reverse proxy configuration (external concern)
- Database and Redis service definitions (external services in production)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/
  compose.production.yml       # Production compose file
  .env.production.example      # Production environment template
```

### Reference Files
| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/compose.yml` | Development compose file (pattern reference) |
| `template/{{cookiecutter.project_slug}}/backend/Dockerfile` | Backend Dockerfile with production target |
| `template/{{cookiecutter.project_slug}}/frontend/Dockerfile` | Frontend Dockerfile with production target |
| `template/{{cookiecutter.project_slug}}/.env.example` | Development environment variables |

## Implementation Details

### 1. Production Compose File (`compose.production.yml`)

```yaml
# Production Docker Compose Configuration
#
# This file is designed for production deployments WITHOUT Kubernetes.
# For Kubernetes deployments, use the k8s/ manifests instead.
#
# Usage:
#   1. Copy .env.production.example to .env.production
#   2. Configure all required environment variables
#   3. Run: docker compose -f compose.production.yml up -d
#
# Prerequisites:
#   - External PostgreSQL database (managed service recommended)
#   - External Redis instance (managed service recommended)
#   - Reverse proxy/load balancer for TLS termination
#   - Container registry access (ghcr.io or custom)

services:
  # Backend API (FastAPI)
  backend:
    image: ${BACKEND_IMAGE:-ghcr.io/OWNER/{{ cookiecutter.project_slug }}-backend}:${IMAGE_TAG:-latest}
    container_name: {{ cookiecutter.project_slug }}-backend
    restart: always
    environment:
      # Application
      ENV: production
      DEBUG: "false"
      LOG_LEVEL: ${LOG_LEVEL:-info}

      # Database - Application Runtime (RLS enforced)
      DATABASE_URL: ${DATABASE_URL}

      # Database - Migrations (BYPASSRLS, run separately)
      MIGRATION_DATABASE_URL: ${MIGRATION_DATABASE_URL}

      # Redis
      REDIS_URL: ${REDIS_URL}

      # API Configuration
      API_V1_PREFIX: ${API_V1_PREFIX:-{{ cookiecutter.backend_api_prefix }}}

      # OAuth Configuration
      OAUTH_ISSUER_URL: ${OAUTH_ISSUER_URL}

      # Security
      ALLOWED_HOSTS: ${ALLOWED_HOSTS:-*}
      CORS_ORIGINS: ${CORS_ORIGINS:-}
{% if cookiecutter.include_sentry == "yes" %}

      # Sentry (optional)
      SENTRY_DSN: ${SENTRY_DSN:-}
      SENTRY_ENVIRONMENT: production
{% endif %}
{% if cookiecutter.include_observability == "yes" %}

      # OpenTelemetry (optional)
      OTEL_SERVICE_NAME: backend
      OTEL_EXPORTER_OTLP_ENDPOINT: ${OTEL_EXPORTER_OTLP_ENDPOINT:-}
{% endif %}
    ports:
      - "${BACKEND_PORT:-8000}:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000{{ cookiecutter.backend_api_prefix }}/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '${BACKEND_CPU_LIMIT:-1.0}'
          memory: ${BACKEND_MEMORY_LIMIT:-512M}
        reservations:
          cpus: '${BACKEND_CPU_RESERVATION:-0.25}'
          memory: ${BACKEND_MEMORY_RESERVATION:-256M}
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    networks:
      - {{ cookiecutter.project_slug }}-network
    # No volumes in production - read-only container

  # Frontend (Nginx serving static files)
  frontend:
    image: ${FRONTEND_IMAGE:-ghcr.io/OWNER/{{ cookiecutter.project_slug }}-frontend}:${IMAGE_TAG:-latest}
    container_name: {{ cookiecutter.project_slug }}-frontend
    restart: always
    environment:
      # Note: VITE_* variables are build-time only
      # Runtime configuration should use a config endpoint or env injection
      NODE_ENV: production
    ports:
      - "${FRONTEND_PORT:-80}:80"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: '${FRONTEND_CPU_LIMIT:-0.5}'
          memory: ${FRONTEND_MEMORY_LIMIT:-128M}
        reservations:
          cpus: '${FRONTEND_CPU_RESERVATION:-0.1}'
          memory: ${FRONTEND_MEMORY_RESERVATION:-64M}
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
    depends_on:
      backend:
        condition: service_healthy
    networks:
      - {{ cookiecutter.project_slug }}-network
    # No volumes in production - read-only container

networks:
  {{ cookiecutter.project_slug }}-network:
    name: {{ cookiecutter.project_slug }}-network
    driver: bridge
```

### 2. Production Environment Template (`.env.production.example`)

```bash
# {{ cookiecutter.project_name }} Production Environment Configuration
#
# Copy this file to .env.production and configure all required values.
# DO NOT commit .env.production to version control.
#
# Usage: docker compose -f compose.production.yml --env-file .env.production up -d

# =============================================================================
# REQUIRED CONFIGURATION
# =============================================================================

# Database Connection (PostgreSQL)
# Format: postgresql+asyncpg://user:password@host:port/database
# Use a managed database service (RDS, Cloud SQL, Azure Database) in production
DATABASE_URL=postgresql+asyncpg://app_user:CHANGE_ME@db.example.com:5432/{{ cookiecutter.project_slug }}

# Migration Database URL (with BYPASSRLS privileges)
# Used only for running migrations - can be same as DATABASE_URL for managed services
MIGRATION_DATABASE_URL=postgresql+asyncpg://migration_user:CHANGE_ME@db.example.com:5432/{{ cookiecutter.project_slug }}

# Redis Connection
# Format: redis://default:password@host:port/db
# Use a managed Redis service (ElastiCache, Memorystore) in production
REDIS_URL=redis://default:CHANGE_ME@redis.example.com:6379/0

# OAuth/OIDC Issuer URL
# Your Keycloak realm URL or other OIDC provider
OAUTH_ISSUER_URL=https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}

# =============================================================================
# OPTIONAL CONFIGURATION
# =============================================================================

# Container Images
# Override if using a custom registry
BACKEND_IMAGE=ghcr.io/your-org/{{ cookiecutter.project_slug }}-backend
FRONTEND_IMAGE=ghcr.io/your-org/{{ cookiecutter.project_slug }}-frontend
IMAGE_TAG=latest

# Service Ports
BACKEND_PORT=8000
FRONTEND_PORT=80

# API Configuration
API_V1_PREFIX={{ cookiecutter.backend_api_prefix }}
LOG_LEVEL=info

# Security Configuration
# Comma-separated list of allowed hosts
ALLOWED_HOSTS=api.example.com,app.example.com
# Comma-separated list of allowed CORS origins
CORS_ORIGINS=https://app.example.com
{% if cookiecutter.include_sentry == "yes" %}

# Sentry Error Tracking (optional)
SENTRY_DSN=
{% endif %}
{% if cookiecutter.include_observability == "yes" %}

# OpenTelemetry (optional)
OTEL_EXPORTER_OTLP_ENDPOINT=
{% endif %}

# =============================================================================
# RESOURCE LIMITS
# =============================================================================

# Backend Resources
BACKEND_CPU_LIMIT=1.0
BACKEND_MEMORY_LIMIT=512M
BACKEND_CPU_RESERVATION=0.25
BACKEND_MEMORY_RESERVATION=256M

# Frontend Resources
FRONTEND_CPU_LIMIT=0.5
FRONTEND_MEMORY_LIMIT=128M
FRONTEND_CPU_RESERVATION=0.1
FRONTEND_MEMORY_RESERVATION=64M
```

### 3. Usage Documentation

Add to existing project README or create deployment documentation:

```markdown
## Production Deployment (Docker Compose)

For production deployments without Kubernetes, use the production Docker Compose file.

### Prerequisites

1. **External PostgreSQL Database**
   - PostgreSQL 16+ (managed service recommended)
   - Create two users: app_user (RLS enforced) and migration_user (BYPASSRLS)
   - Run database migrations before first deployment

2. **External Redis Instance**
   - Redis 7+ (managed service recommended)
   - Configure password authentication

3. **OAuth Provider**
   - Keycloak or compatible OIDC provider
   - Configure realm and client credentials

4. **Container Images**
   - Build and push images to container registry
   - Or use CI/CD to publish to ghcr.io

### Deployment Steps

```bash
# 1. Configure environment
cp .env.production.example .env.production
# Edit .env.production with your values

# 2. Run database migrations (one-time or on updates)
docker run --rm \
  -e DATABASE_URL=$MIGRATION_DATABASE_URL \
  ghcr.io/your-org/{{ cookiecutter.project_slug }}-backend:latest \
  alembic upgrade head

# 3. Start services
docker compose -f compose.production.yml --env-file .env.production up -d

# 4. Verify health
docker compose -f compose.production.yml ps
curl http://localhost:8000{{ cookiecutter.backend_api_prefix }}/health
```

### Updating Deployments

```bash
# Pull new images
docker compose -f compose.production.yml pull

# Restart with zero downtime (one service at a time)
docker compose -f compose.production.yml up -d --no-deps backend
docker compose -f compose.production.yml up -d --no-deps frontend

# Or rolling restart
docker compose -f compose.production.yml up -d
```

### Rollback

```bash
# Specify previous image tag
IMAGE_TAG=1.0.0 docker compose -f compose.production.yml up -d
```
```

## Success Criteria

### Functional Requirements
- [ ] FR-DEP-013: Production compose file (compose.production.yml) shall be included
- [ ] FR-DEP-014: Production compose file shall use production Docker targets
- [ ] FR-DEP-015: Production compose file shall not mount development volumes
- [ ] FR-DEP-016: Production compose file shall support external database connection

### Non-Functional Requirements
- [ ] Containers run with resource limits
- [ ] Health checks configured with appropriate timeouts
- [ ] Logging configured with rotation
- [ ] No secrets in compose file (all via environment variables)
- [ ] Restart policies configured for resilience

### Verification Steps

1. **Syntax Validation:**
   ```bash
   docker compose -f compose.production.yml config
   ```

2. **Dry Run:**
   ```bash
   docker compose -f compose.production.yml --env-file .env.production.example up --dry-run
   ```

3. **Image Pull Test:**
   ```bash
   docker compose -f compose.production.yml pull
   ```

4. **Production Readiness Checklist:**
   - [ ] No volume mounts (stateless containers)
   - [ ] No build context (pre-built images only)
   - [ ] Resource limits defined
   - [ ] Health checks configured
   - [ ] Restart policies set
   - [ ] Logging configured

### Quality Gates
- [ ] Compose file validates without errors
- [ ] No hardcoded secrets or credentials
- [ ] All required environment variables documented
- [ ] Resource limits are reasonable for production
- [ ] Health check endpoints match actual application

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P1-03 | Production Dockerfile targets | Images must have `production` target |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-07 | Environment variables | Documentation references compose.production.yml |
| P6-02 | Migration guide | Migration guide includes Docker Compose deployment |

### Integration Contract
```yaml
# Contract: Production Docker Compose

# Services
- backend:
    image: configurable via BACKEND_IMAGE
    port: 8000 (configurable via BACKEND_PORT)
    health: {{ cookiecutter.backend_api_prefix }}/health
- frontend:
    image: configurable via FRONTEND_IMAGE
    port: 80 (configurable via FRONTEND_PORT)
    health: /

# Required Environment Variables
- DATABASE_URL: PostgreSQL async connection string
- MIGRATION_DATABASE_URL: PostgreSQL migration connection string
- REDIS_URL: Redis connection string
- OAUTH_ISSUER_URL: OIDC issuer URL

# Optional Environment Variables
- BACKEND_IMAGE, FRONTEND_IMAGE, IMAGE_TAG
- BACKEND_PORT, FRONTEND_PORT
- LOG_LEVEL, ALLOWED_HOSTS, CORS_ORIGINS
- Resource limits (CPU, memory)
```

## Monitoring and Observability

### Container Metrics
Monitor via Docker stats or external tools:
```bash
docker stats {{ cookiecutter.project_slug }}-backend {{ cookiecutter.project_slug }}-frontend
```

### Log Collection
Logs are written to stdout/stderr with JSON file driver:
- Location: `/var/lib/docker/containers/<container_id>/<container_id>-json.log`
- Rotation: 10MB per file, 5 files max
- Collection: Use Promtail, Fluentd, or cloud logging agent

### Health Endpoints
- Backend: `http://localhost:8000{{ cookiecutter.backend_api_prefix }}/health`
- Frontend: `http://localhost:80/`

## Infrastructure Needs

### Host Requirements
- Docker Engine 24.0+
- Docker Compose v2.20+
- 2+ CPU cores recommended
- 2GB+ RAM recommended
- Network access to external PostgreSQL and Redis

### External Services
- PostgreSQL 16+ (managed service recommended)
- Redis 7+ (managed service recommended)
- Keycloak or OIDC provider
- Container registry (ghcr.io, ECR, GCR, etc.)

### Reverse Proxy
Production deployments should use a reverse proxy for:
- TLS termination
- Load balancing
- Request routing
- Rate limiting

Example nginx configuration:
```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:80;
}

server {
    listen 443 ssl;
    server_name api.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name app.example.com;

    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Template structure mirrors existing compose.yml
- Main work is removing development configurations
- Environment variable documentation is straightforward
- Testing requires minimal infrastructure

## Notes

### Design Decisions

**1. No Database/Redis Services:**
- Production should use managed database services
- External services provide backup, HA, and scaling
- Reduces operational complexity

**2. Pre-built Images Only:**
- No `build` context in production compose
- Images must be built and pushed separately
- Enables version pinning and rollback

**3. Resource Limits:**
- Prevents runaway containers
- Configurable via environment variables
- Defaults are conservative for small deployments

**4. JSON File Logging:**
- Simple, works everywhere
- Rotation prevents disk exhaustion
- Can be collected by external log agents

**5. No Observability Stack:**
- Observability should be deployed separately
- Production observability often uses managed services
- Can add as separate compose profile if needed

### Differences from Development Compose

| Aspect | Development | Production |
|--------|-------------|------------|
| Image source | Build from Dockerfile | Pre-built from registry |
| Dockerfile target | `development` | `production` |
| Volumes | Mount source code | None (stateless) |
| Database | Local PostgreSQL container | External managed service |
| Redis | Local Redis container | External managed service |
| Restart policy | `unless-stopped` | `always` with retry limits |
| Resource limits | None | Defined |
| Logging | Default | JSON with rotation |

### Security Considerations
- All secrets via environment variables
- `.env.production` must not be committed
- Use secret management for production (Vault, AWS SM, etc.)
- Container images should be scanned before deployment
- Consider read-only root filesystem (requires volume for tmp)

### Future Enhancements
- Docker Swarm mode configuration
- Multiple replica support
- Traefik integration for automatic TLS
- Docker secrets for credential management
- Separate profiles for observability stack

### Related Requirements
- FR-DEP-013: Production compose file shall be included
- FR-DEP-014: Production compose file shall use production Docker targets
- FR-DEP-015: Production compose file shall not mount development volumes
- FR-DEP-016: Production compose file shall support external database connection
- US-4.3: Production Docker Compose
