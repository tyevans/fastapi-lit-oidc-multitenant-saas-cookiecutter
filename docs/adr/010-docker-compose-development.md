# ADR-010: Docker Compose for Development

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template generates multi-service applications with significant infrastructure requirements:

1. **Multiple Services**: The generated stack includes 5-10+ services (PostgreSQL, Redis, Keycloak, backend, frontend, and optionally Prometheus, Grafana, Loki, Tempo, Promtail)
2. **Complex Service Dependencies**: Services have strict startup order requirements (PostgreSQL must be healthy before Keycloak, Keycloak before backend, etc.)
3. **Environment Consistency**: Developers across different operating systems (Linux, macOS, Windows) need identical environments
4. **Reproducibility**: New developers must be able to onboard quickly with minimal manual setup
5. **Configuration Management**: Services require coordinated environment variables, network configuration, and volume mounts

The development environment must balance ease of use with production parity while supporting hot-reload for rapid iteration.

## Decision

We chose **Docker Compose** as the primary development environment orchestration tool.

The implementation uses a single `compose.yml` file with the following characteristics:

**Service Orchestration** (`compose.yml`):
- Defines all services with health checks for dependency ordering
- Uses `depends_on` with `condition: service_healthy` for startup sequencing
- Implements network aliases (e.g., `keycloak.localtest.me`) for consistent service discovery
- Provides named volumes for data persistence across restarts

**Development-Optimized Configuration**:
- Volume mounts for hot-reload (`./backend:/app`, `./frontend:/app`)
- Multi-stage Dockerfiles with `development` target for faster builds
- Environment variable defaults with `${VAR:-default}` syntax for flexibility
- Port exposure for local debugging and tool integration

**Health Check Strategy**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U user -d db"]
  interval: 10s
  timeout: 5s
  retries: 5
  start_period: 10s
```

**Helper Scripts** (`scripts/docker-dev.sh`):
- Wraps common Docker Compose operations
- Provides `up`, `down`, `logs`, `shell`, and `reset` commands
- Handles service-specific operations consistently

## Consequences

### Positive

1. **Zero-Friction Onboarding**: New developers run `./scripts/docker-dev.sh up` and have a complete environment in minutes, regardless of host OS

2. **Service Orchestration**: Health checks ensure services start in correct order. Backend waits for PostgreSQL, Redis, and Keycloak to be healthy before starting

3. **Environment Parity**: All developers work with identical service versions (PostgreSQL 18, Redis 7, Keycloak 23.0) defined in `cookiecutter.json`

4. **Data Persistence**: Named volumes (`postgres_data`, `redis_data`, `keycloak_data`) preserve state across container restarts

5. **Hot Reload**: Volume mounts enable code changes to reflect immediately without container rebuilds:
   - Backend: FastAPI auto-reload via `--reload` flag
   - Frontend: Vite HMR via volume mount

6. **Network Isolation**: Project-specific bridge network prevents port conflicts between multiple project instances

7. **Conditional Services**: Jinja2 templating enables optional observability stack inclusion via `include_observability` variable

### Negative

1. **Resource Consumption**: Running 5-10 containers requires significant memory (4-8GB recommended). Development laptops may struggle with full stack plus IDE

2. **Docker Dependency**: Requires Docker installation and familiarity. Some corporate environments restrict Docker usage

3. **Startup Time**: Full stack initialization takes 60-90 seconds due to health check intervals and service startup (especially Keycloak)

4. **Platform Differences**: Docker Desktop on macOS has known volume mount performance issues. Workarounds (e.g., `:cached` flag) may be needed

5. **Debugging Complexity**: Debugging across containers requires additional setup (remote debugging, log aggregation)

### Neutral

1. **No Override Files**: We intentionally use a single `compose.yml` rather than splitting into `docker-compose.yml` + `docker-compose.override.yml`. This simplifies understanding but reduces configuration flexibility

2. **Development-Only Focus**: Production deployment uses different orchestration (Kubernetes, ECS). Compose skills don't directly transfer

## Alternatives Considered

### Local Installation (Native Services)

**Approach**: Install PostgreSQL, Redis, Keycloak, etc. directly on developer machines.

**Why Not Chosen**:
- Version inconsistencies across developers cause "works on my machine" issues
- Manual installation steps increase onboarding time from minutes to hours
- Service conflicts with other projects using same ports
- Keycloak installation and configuration is particularly complex
- No clean way to reset environment to known state

### Kubernetes (minikube/kind)

**Approach**: Use local Kubernetes cluster for development environment.

**Why Not Chosen**:
- Significant complexity overhead for development use case
- Slower iteration cycle (build, push, deploy vs. volume mount)
- Higher resource consumption than Docker Compose
- Overkill for single-developer scenarios
- Better suited for testing Kubernetes-specific deployments

### VS Code Dev Containers

**Approach**: Use VS Code Remote Containers for development environment.

**Why Not Chosen**:
- Ties development to specific IDE
- Still requires Docker (no reduction in dependencies)
- Volume mount performance issues persist
- Adds complexity layer without clear benefit for this use case
- Can be added later by developers who prefer this workflow

### Nix / Devbox

**Approach**: Use Nix for reproducible development environments.

**Why Not Chosen**:
- Steep learning curve for most developers
- Limited Windows support
- Still need containers for services like Keycloak
- Smaller ecosystem and community compared to Docker

---

## Related ADRs

- [ADR-003: PostgreSQL as Primary Database](./003-postgresql-primary-database.md) - Database service orchestrated via Compose
- [ADR-004: Keycloak as Identity Provider](./004-keycloak-identity-provider.md) - OAuth service orchestrated via Compose
- [ADR-007: Redis Token Revocation](./007-redis-token-revocation.md) - Cache service orchestrated via Compose

## Implementation References

- `template/{{cookiecutter.project_slug}}/compose.yml` - Main compose configuration
- `template/{{cookiecutter.project_slug}}/backend/Dockerfile` - Multi-stage backend image
- `template/{{cookiecutter.project_slug}}/frontend/Dockerfile` - Multi-stage frontend image
- `template/{{cookiecutter.project_slug}}/scripts/docker-dev.sh` - Development helper script
