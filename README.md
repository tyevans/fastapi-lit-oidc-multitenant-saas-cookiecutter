# OAuth-Enabled Full-Stack Application Template

A production-ready cookiecutter template for building modern web applications with FastAPI, Lit, PostgreSQL, Keycloak OAuth, and Docker Compose.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Template Variables](#template-variables)
- [Generated Project Structure](#generated-project-structure)
- [Development Workflow](#development-workflow)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This template generates a complete full-stack application with enterprise-grade authentication, multi-tenant data isolation, and production-ready infrastructure. It is designed for teams building SaaS applications or internal tools that require OAuth integration and tenant separation.

**Target Audience:**
- Developers building new SaaS applications
- Teams needing OAuth/OIDC authentication from day one
- Projects requiring multi-tenant data isolation

For a quick 5-minute setup, see [QUICKSTART.md](./QUICKSTART.md).

## Features

### Core Stack

- **Backend**: FastAPI (Python 3.13) with async SQLAlchemy
- **Frontend**: Lit web components with Vite
- **Database**: PostgreSQL 18 with Row-Level Security
- **OAuth**: Keycloak 23.0 with OIDC/OAuth 2.0
- **Cache**: Redis 7 for distributed caching
- **Orchestration**: Docker Compose for local development

### Security Features

- OAuth 2.0 Authorization Code flow with PKCE
- JWT validation with JWKS caching
- Multi-tenant architecture with Row-Level Security
- Distributed rate limiting with Redis
- Token revocation and logout support
- Separate database roles (migration vs application)

### Developer Experience

- Hot reload for both backend and frontend
- Database migrations with Alembic
- Comprehensive testing setup (pytest, Playwright)
- API documentation with Swagger/OpenAPI
- Health check endpoints
- Development helper scripts

### Optional Features

- **Observability Stack**: Prometheus, Grafana, Loki, Tempo for metrics, logs, and traces

## Prerequisites

- Python 3.13+
- Node.js 20+
- Docker & Docker Compose
- cookiecutter (`pip install cookiecutter`)
- jq (for Keycloak setup scripts)

## Quick Start

For the complete 5-step walkthrough with verification steps, see **[QUICKSTART.md](./QUICKSTART.md)**.

**Summary:**

```bash
cookiecutter /path/to/project-starter/template
cd your-project-slug
./scripts/docker-dev.sh up
./keycloak/setup-realm.sh
```

Access your application at http://localhost:5173.

## Template Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `project_name` | My Awesome Project | Human-readable project name |
| `project_slug` | (auto-generated) | URL-safe identifier derived from project name |
| `project_short_description` | A FastAPI + Lit web application... | Brief project description |
| `author_name` | Your Name | Author name for package metadata |
| `author_email` | your.email@example.com | Author email |
| `postgres_version` | 18 | PostgreSQL version |
| `postgres_port` | 5435 | Host port for PostgreSQL |
| `postgres_password` | change_me_in_production | Database password |
| `redis_version` | 7 | Redis version |
| `redis_port` | 6379 | Host port for Redis |
| `keycloak_version` | 23.0 | Keycloak version |
| `keycloak_port` | 8080 | Host port for Keycloak |
| `backend_port` | 8000 | Host port for backend API |
| `backend_api_prefix` | /api/v1 | API path prefix |
| `frontend_port` | 5173 | Host port for frontend |
| `python_version` | 3.13 | Python version for backend |
| `node_version` | 20 | Node.js version for frontend |
| `include_observability` | yes | Include Prometheus, Grafana, Loki, Tempo |
| `license` | MIT | Project license (MIT, BSD-3-Clause, Apache-2.0, GPL-3.0, Proprietary) |

**Note:** Multi-tenancy, rate limiting, and token revocation are always enabled as core architectural features.

## Generated Project Structure

```
your-project/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/          # Routes and dependencies
│   │   ├── core/         # Config, database, security
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── middleware/   # Custom middleware
│   ├── alembic/          # Database migrations
│   └── tests/            # Test suite
├── frontend/             # Lit web application
│   ├── src/
│   │   ├── api/         # HTTP client
│   │   └── components/  # Lit components
│   └── e2e/             # Playwright tests
├── keycloak/            # OAuth configuration
│   ├── setup-realm.sh   # Realm setup script
│   └── realm-export.json
├── scripts/             # Helper scripts
│   └── docker-dev.sh    # Docker Compose wrapper
├── observability/       # (if included) Monitoring stack
├── compose.yml          # Docker Compose services
└── README.md            # Generated project documentation
```

For detailed documentation of each component, see the generated project's README.md and component-specific READMEs.

## Development Workflow

### Essential Commands

```bash
./scripts/docker-dev.sh up        # Start all services
./scripts/docker-dev.sh down      # Stop all services
./scripts/docker-dev.sh logs      # View all logs
./scripts/docker-dev.sh logs backend  # View specific service logs
./scripts/docker-dev.sh shell backend # Open shell in container
./scripts/docker-dev.sh restart   # Restart services
./scripts/docker-dev.sh rebuild   # Rebuild containers
./scripts/docker-dev.sh clean     # Remove all data
```

### Database Migrations

```bash
./scripts/docker-dev.sh shell backend
alembic upgrade head                    # Apply migrations
alembic revision --autogenerate -m "description"  # Create migration
```

For backend and frontend development details, see the component READMEs in the generated project.

## Troubleshooting

### Services Not Starting

```bash
./scripts/docker-dev.sh logs      # Check logs for errors
docker compose ps                 # Verify service status
./scripts/docker-dev.sh restart   # Restart all services
```

### Keycloak Setup Fails

Ensure Keycloak is healthy before running setup:

```bash
curl http://localhost:8080/health
./keycloak/setup-realm.sh
```

### Database Connection Errors

```bash
docker compose ps postgres        # Check PostgreSQL status
docker compose exec postgres psql -U your_user -d your_db
```

### OAuth Token Validation Fails

```bash
curl http://localhost:8080/realms/your-realm/.well-known/openid-configuration
./scripts/docker-dev.sh logs backend
```

For additional troubleshooting, see the generated project documentation.

## Contributing

This template is designed to be forked and customized. When making architectural decisions, please document them using our ADR process.

- **Architecture Decision Records**: See [docs/adr/README.md](./docs/adr/README.md) for documented decisions and the ADR format
- **Add new services** to `compose.yml`
- **Extend the backend** with new routers in `backend/app/api/routers/`
- **Add frontend components** in `frontend/src/components/`

## License

MIT

---

Generated with Cookiecutter
