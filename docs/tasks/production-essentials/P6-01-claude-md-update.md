# P6-01: Update CLAUDE.md with New Features

## Task Identifier
**ID:** P6-01
**Phase:** 6 - Documentation and Validation
**Domain:** Documentation
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| All P1-P5 tasks | Informational | Pending | Must know all features to document them |
| P1-01 | GitHub Actions CI | Must complete | CI commands to document |
| P1-02 | GitHub Actions build | Must complete | Build commands to document |
| P2-01 | Security headers | Must complete | Security configuration to document |
| P3-03 | Sentry integration | Must complete | Sentry setup to document |
| P4-01 | Kubernetes manifests | Must complete | K8s commands to document |
| P5-02 | k6 load testing | Must complete | Load testing commands to document |

## Scope

### In Scope
- Add CI/CD commands and workflow documentation to CLAUDE.md
- Add security headers configuration section
- Add Kubernetes deployment commands (conditional on `include_kubernetes`)
- Add Sentry configuration section (conditional on `include_sentry`)
- Add load testing commands (k6)
- Add API client generation commands
- Add backup/restore script commands
- Update service ports table with any new ports
- Add troubleshooting section for common issues
- Maintain existing cookiecutter conditional patterns

### Out of Scope
- Creating separate documentation files (handled by other tasks)
- Modifying the root project CLAUDE.md (this is template-level)
- Writing ADRs (separate tasks)
- Tutorial-style documentation (CLAUDE.md is reference only)

## Relevant Code Areas

### Files to Modify
```
template/{{cookiecutter.project_slug}}/CLAUDE.md    # Main update target
```

### Reference Files (to document)
```
template/{{cookiecutter.project_slug}}/.github/workflows/ci.yml
template/{{cookiecutter.project_slug}}/.github/workflows/build.yml
template/{{cookiecutter.project_slug}}/.github/workflows/deploy.yml
template/{{cookiecutter.project_slug}}/backend/app/middleware/security_headers.py
template/{{cookiecutter.project_slug}}/backend/app/services/sentry.py
template/{{cookiecutter.project_slug}}/k8s/base/
template/{{cookiecutter.project_slug}}/k8s/overlays/
template/{{cookiecutter.project_slug}}/scripts/backup-db.sh
template/{{cookiecutter.project_slug}}/scripts/restore-db.sh
template/{{cookiecutter.project_slug}}/scripts/generate-api-client.sh
template/{{cookiecutter.project_slug}}/tests/load/
```

## Implementation Details

### 1. New Sections to Add

The following sections should be added to CLAUDE.md, following the existing structure and conditional patterns:

#### CI/CD Section (conditional on `include_github_actions`)

```markdown
{% if cookiecutter.include_github_actions == "yes" %}
## CI/CD Pipeline

GitHub Actions workflows are configured for automated testing, building, and deployment.

### Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | PR, push to main | Lint, test, coverage |
| `build.yml` | Push to main | Build and push Docker images |
| `deploy.yml` | Manual, tag | Deploy to staging/production |

### Common Commands

```bash
# View workflow runs
gh run list

# View specific workflow run
gh run view <run-id>

# Re-run failed workflow
gh run rerun <run-id>

# Trigger deployment manually
gh workflow run deploy.yml -f environment=staging
```

### Container Registry

Images are pushed to GitHub Container Registry:
```bash
# Pull backend image
docker pull ghcr.io/{{ cookiecutter.author_name | lower | replace(' ', '-') }}/{{ cookiecutter.project_slug }}-backend:latest

# Pull frontend image
docker pull ghcr.io/{{ cookiecutter.author_name | lower | replace(' ', '-') }}/{{ cookiecutter.project_slug }}-frontend:latest
```
{% endif %}
```

#### Security Configuration Section

```markdown
## Security Configuration

### Security Headers

Security headers are added via middleware. Configure in environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `X_FRAME_OPTIONS` | `DENY` | Clickjacking protection |
| `CSP_POLICY` | `default-src 'self'...` | Content Security Policy |
| `FORCE_HSTS` | `false` | Force HSTS in non-HTTPS |
| `HSTS_MAX_AGE` | `31536000` | HSTS max-age (1 year) |

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install

# Run all hooks manually
pre-commit run --all-files

# Run specific hook
pre-commit run gitleaks --all-files
```
```

#### Sentry Section (conditional)

```markdown
{% if cookiecutter.include_sentry == "yes" %}
## Error Tracking (Sentry)

Sentry is configured for error tracking with automatic exception capture.

### Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `SENTRY_DSN` | Yes | Sentry project DSN |
| `SENTRY_ENVIRONMENT` | No | Environment name (default: ENV) |
| `SENTRY_SAMPLE_RATE` | No | Transaction sample rate (default: 0.1) |

### Testing Sentry

```bash
# Trigger test error (development only)
curl -X POST http://localhost:{{ cookiecutter.backend_port }}{{ cookiecutter.backend_api_prefix }}/debug/sentry-test
```

### Viewing Errors

Visit your Sentry dashboard: https://sentry.io/organizations/YOUR_ORG/issues/
{% endif %}
```

#### Kubernetes Section (conditional)

```markdown
{% if cookiecutter.include_kubernetes == "yes" %}
## Kubernetes Deployment

Kubernetes manifests use Kustomize for environment management.

### Directory Structure

```
k8s/
  base/           # Base manifests (shared)
  overlays/
    staging/      # Staging environment
    production/   # Production environment
```

### Common Commands

```bash
# Preview staging manifests
kubectl kustomize k8s/overlays/staging

# Apply to staging
kubectl apply -k k8s/overlays/staging

# Apply to production
kubectl apply -k k8s/overlays/production

# View deployments
kubectl get deployments -n {{ cookiecutter.project_slug }}

# View pods
kubectl get pods -n {{ cookiecutter.project_slug }}

# View logs
kubectl logs -f deployment/backend -n {{ cookiecutter.project_slug }}

# Port forward for local access
kubectl port-forward svc/backend 8000:8000 -n {{ cookiecutter.project_slug }}
```

### Secrets Management

```bash
# Create secrets (example)
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --from-literal=database-url='postgresql://...' \
  --from-literal=redis-url='redis://...' \
  -n {{ cookiecutter.project_slug }}
```
{% endif %}
```

#### Load Testing Section

```markdown
## Load Testing (k6)

k6 scripts are available for performance testing.

### Running Tests

```bash
# Smoke test (quick validation)
./scripts/run-load-test.sh smoke

# Load test (sustained traffic)
./scripts/run-load-test.sh load

# Stress test (find breaking point)
./scripts/run-load-test.sh stress

# Run specific test file
k6 run tests/load/auth-flow.js --vus 10 --duration 30s
```

### Test Configuration

Configure via environment variables:
- `BASE_URL`: Target URL (default: http://localhost:{{ cookiecutter.backend_port }})
- `VUS`: Virtual users (default varies by test)
- `DURATION`: Test duration (default varies by test)

### Viewing Results

Results are output to console. For Grafana integration:
```bash
k6 run --out influxdb=http://localhost:8086/k6 tests/load/smoke.js
```
```

#### API Client Generation Section

```markdown
## API Client Generation

TypeScript API clients can be generated from the OpenAPI spec.

### Generation

```bash
# From project root (requires backend running)
./scripts/generate-api-client.sh

# Validate spec only
./scripts/generate-api-client.sh --validate

# From frontend directory
cd frontend && npm run generate:api:fetch
```

### Usage

```typescript
import { DefaultApi, Configuration } from './api/generated'

const config = new Configuration({
  basePath: import.meta.env.VITE_API_URL,
  accessToken: async () => await authService.getAccessToken()
})

const api = new DefaultApi(config)
const health = await api.healthCheck()
```
```

#### Database Operations Section

```markdown
## Database Operations

### Backup

```bash
# Manual backup
./scripts/backup-db.sh

# With custom retention (days)
RETENTION_DAYS=30 ./scripts/backup-db.sh

# Backup to S3
BACKUP_S3_BUCKET=my-bucket ./scripts/backup-db.sh
```

### Restore

```bash
# Restore from latest backup
./scripts/restore-db.sh --latest

# Restore from specific file
./scripts/restore-db.sh --file /backups/backup_20240101_120000.sql.gz

# Restore to specific point in time (if WAL archiving enabled)
./scripts/restore-db.sh --pitr "2024-01-01 12:00:00"
```

### Migrations

```bash
# Apply all pending migrations
./scripts/docker-dev.sh shell backend
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```
```

### 2. Update Service Ports Table

Add any new ports introduced by Phase 1-5 features:

```markdown
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
```

### 3. Add Troubleshooting Section

```markdown
## Troubleshooting

### Common Issues

**CI Pipeline Fails on PR**
```bash
# Run linting locally
cd backend && ruff check .
cd frontend && npm run lint

# Run tests locally
cd backend && pytest
cd frontend && npm test
```

**Docker Build Fails**
```bash
# Clean Docker cache
docker builder prune -f

# Rebuild without cache
docker compose build --no-cache backend
```

**Kubernetes Deployment Issues**
```bash
# Check pod status
kubectl describe pod <pod-name> -n {{ cookiecutter.project_slug }}

# Check events
kubectl get events -n {{ cookiecutter.project_slug }} --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n {{ cookiecutter.project_slug }} --previous
```

**Database Connection Issues**
```bash
# Test connection
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} -c '\conninfo'

# Check active connections
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} -c 'SELECT * FROM pg_stat_activity'
```
```

### 4. Cookiecutter Conditionals Pattern

Ensure all new sections follow the established conditional pattern:

```jinja2
{% if cookiecutter.include_github_actions == "yes" %}
## CI/CD Pipeline
...
{% endif %}

{% if cookiecutter.include_kubernetes == "yes" %}
## Kubernetes Deployment
...
{% endif %}

{% if cookiecutter.include_sentry == "yes" %}
## Error Tracking (Sentry)
...
{% endif %}
```

## Success Criteria

### Functional Requirements
- [ ] All Phase 1-5 features are documented in CLAUDE.md
- [ ] CI/CD commands are documented (conditional on `include_github_actions`)
- [ ] Security configuration is documented
- [ ] Kubernetes commands are documented (conditional on `include_kubernetes`)
- [ ] Sentry configuration is documented (conditional on `include_sentry`)
- [ ] Load testing commands are documented
- [ ] API client generation is documented
- [ ] Backup/restore commands are documented
- [ ] Troubleshooting section is comprehensive

### Verification Steps
1. **Template Generation Test:**
   ```bash
   # Generate with all options
   cookiecutter . --no-input \
     include_github_actions=yes \
     include_kubernetes=yes \
     include_sentry=yes \
     include_observability=yes

   # Verify CLAUDE.md contains all sections
   grep -q "CI/CD Pipeline" my-awesome-project/CLAUDE.md
   grep -q "Kubernetes Deployment" my-awesome-project/CLAUDE.md
   grep -q "Error Tracking" my-awesome-project/CLAUDE.md
   ```

2. **Conditional Generation Test:**
   ```bash
   # Generate with minimal options
   cookiecutter . --no-input \
     include_github_actions=no \
     include_kubernetes=no \
     include_sentry=no

   # Verify CLAUDE.md does NOT contain conditional sections
   ! grep -q "CI/CD Pipeline" my-awesome-project/CLAUDE.md
   ! grep -q "Kubernetes Deployment" my-awesome-project/CLAUDE.md
   ! grep -q "Error Tracking" my-awesome-project/CLAUDE.md
   ```

3. **Command Validation:**
   ```bash
   # Verify documented commands work
   ./scripts/docker-dev.sh up
   ./scripts/backup-db.sh
   ./scripts/generate-api-client.sh --validate
   ```

### Quality Gates
- [ ] All code blocks are syntactically correct
- [ ] All commands are tested and functional
- [ ] Cookiecutter conditionals render correctly
- [ ] No hardcoded values (all use cookiecutter variables)
- [ ] Documentation follows existing CLAUDE.md style
- [ ] Service ports table is accurate

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P1-01 through P5-05 | Feature implementations | All features must exist to be documented |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-03 | CLAUDE.md included in validation | Template validation includes doc files |
| P6-04 | E2E uses CLAUDE.md commands | Validation tests documented commands |

### Integration Contract
```yaml
# Contract: CLAUDE.md structure

# Required sections (always present)
- Project Overview
- Development Commands
- Architecture
- Key Patterns
- Service Ports
- Initial Setup
- Key Configuration Files
- Troubleshooting (NEW)

# Conditional sections
- CI/CD Pipeline (include_github_actions == "yes")
- Kubernetes Deployment (include_kubernetes == "yes")
- Error Tracking (include_sentry == "yes")
- Observability Stack (include_observability == "yes")

# All commands documented must:
- Be functional in generated project
- Use cookiecutter variables for ports/names
- Include example output where helpful
```

## Monitoring and Observability

### Documentation Quality Metrics
- Command success rate (all documented commands work)
- Template generation success with all option combinations
- User feedback on documentation clarity

### Validation
- Automated tests verify documented commands
- Template generation tests include CLAUDE.md validation
- Pre-commit hooks validate Jinja2 syntax

## Infrastructure Needs

### None Required
This is a documentation-only task. No infrastructure changes needed.

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Significant content to add (multiple sections)
- Must coordinate with all Phase 1-5 task outputs
- Cookiecutter conditionals require careful testing
- All commands must be validated
- Must maintain consistency with existing style

## Notes

### Design Decisions

**1. Reference Documentation Style:**
- CLAUDE.md is a quick reference, not a tutorial
- Commands with brief explanations, not step-by-step guides
- Links to detailed docs where needed

**2. Cookiecutter Conditional Pattern:**
- Follow existing `include_observability` pattern exactly
- Section appears/disappears based on option value
- No partial sections or fallbacks

**3. Command Examples:**
- Show most common usage first
- Include environment variable options
- Keep examples concise and practical

**4. Troubleshooting Section:**
- Added as new permanent section
- Covers common issues across all features
- Provides diagnostic commands and solutions

### Related Requirements
- NFR-005: All additions shall follow existing codebase patterns and conventions
- All documentation tasks depend on accurate CLAUDE.md as reference
- Template users rely on CLAUDE.md for onboarding

### Coordination Notes
- Wait for all Phase 1-5 tasks to complete before finalizing
- May need updates if task implementations differ from spec
- Review with domain agents for accuracy
