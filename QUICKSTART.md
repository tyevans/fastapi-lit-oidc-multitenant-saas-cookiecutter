# Quick Start Guide

Get a running project in under 5 minutes.

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- cookiecutter (`pip install cookiecutter`)
- jq (`brew install jq` on macOS or `apt install jq` on Ubuntu)

## Step 1: Generate Your Project

```bash
cookiecutter /path/to/project-starter/template
```

Answer the prompts (or press Enter to accept defaults):
- **project_name**: Your project name
- **project_slug**: Auto-generated from project name
- **author_name**: Your name
- **author_email**: Your email

**Verification**: You should see a new directory created with your project slug name.

```bash
ls -la your-project-slug/
```

## Step 2: Configure Environment

```bash
cd your-project-slug
cp .env.example .env
```

Review the `.env` file and update any values if needed. The defaults work for local development.

**Verification**: You should see a `.env` file with database, Redis, and Keycloak configuration.

```bash
cat .env | head -20
```

## Step 3: Start Services

```bash
./scripts/docker-dev.sh up
```

Wait 1-2 minutes for all services to initialize. Keycloak takes the longest.

**Verification**: You should see all services running and healthy.

```bash
docker compose ps
```

Expected output shows `postgres`, `redis`, `keycloak`, `backend`, and `frontend` all in "running" state.

## Step 4: Set Up OAuth

```bash
./keycloak/setup-realm.sh
```

This creates the OAuth realm, clients, and test users.

**Verification**: You should see "Realm setup complete" and can access Keycloak.

```bash
curl -s http://localhost:8080/realms/your-project-slug-dev/.well-known/openid-configuration | jq .issuer
```

Test users created:
- `alice@example.com` / `password123`
- `bob@example.com` / `password123`

## Step 5: Access Your Application

Open in your browser:

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Keycloak Admin | http://localhost:8080/admin (admin/admin) |

**Verification**: You should see the frontend load and be able to click through to login.

```bash
curl http://localhost:8000/api/v1/health
```

Expected output: `{"status": "healthy"}`

---

## Next Steps

- **Full documentation**: See [README.md](./README.md) for complete feature documentation
- **Generated project docs**: See `your-project-slug/README.md` for project-specific guidance
- **Backend development**: The generated backend uses `uv` as the recommended Python package manager for fast, reproducible dependency management
- **Run database migrations**: `./scripts/docker-dev.sh shell backend` then `alembic upgrade head`

## Troubleshooting

For common issues, see the [Troubleshooting section in README.md](./README.md#troubleshooting).

**Quick checks:**
```bash
# View all logs
./scripts/docker-dev.sh logs

# Check service health
docker compose ps

# Restart everything
./scripts/docker-dev.sh restart
```
