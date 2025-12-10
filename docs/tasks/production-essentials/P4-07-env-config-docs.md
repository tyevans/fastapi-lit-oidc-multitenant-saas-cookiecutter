# P4-07: Document Environment Configuration

## Task Identifier
**ID:** P4-07
**Phase:** 4 - Kubernetes Deployment
**Domain:** Documentation
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P4-01 | Required | Documented | Base manifests define ConfigMap and Secret structure |

## Scope

### In Scope
- Create comprehensive environment configuration documentation
- Document all required environment variables (must be set before deployment)
- Document all optional environment variables with defaults
- Create environment variable reference table for backend and frontend
- Document configuration differences across environments (development, staging, production)
- Provide secrets management integration examples (Vault, AWS Secrets Manager, Kubernetes Secrets)
- Document configuration validation patterns
- Create environment-specific `.env` template examples

### Out of Scope
- Implementing secrets management integration (documentation only)
- Modifying existing configuration files
- Creating configuration validation code
- Helm values.yaml (project uses Kustomize)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/docs/
  configuration.md              # Main configuration reference
  secrets-management.md         # Secrets management patterns (optional)

template/{{cookiecutter.project_slug}}/
  .env.production.example       # Production environment template
  .env.staging.example          # Staging environment template
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/.env.example                    # Existing dev environment template
template/{{cookiecutter.project_slug}}/backend/app/core/config.py      # Backend settings source
template/{{cookiecutter.project_slug}}/k8s/base/configmap.yaml         # K8s ConfigMap variables
template/{{cookiecutter.project_slug}}/k8s/base/secret.yaml            # K8s Secret template
template/{{cookiecutter.project_slug}}/compose.yml                     # Docker Compose environment
```

## Implementation Details

### 1. Configuration Reference Documentation (`docs/configuration.md`)

```markdown
# Environment Configuration Reference

This document provides a comprehensive reference for all environment variables used by {{ cookiecutter.project_name }}.

## Quick Reference

| Category | Required Variables | Optional Variables |
|----------|-------------------|-------------------|
| Core | `DATABASE_URL`, `REDIS_URL`, `OAUTH_ISSUER_URL` | `ENV`, `DEBUG`, `LOG_LEVEL` |
| OAuth | `OAUTH_ISSUER_URL` | `OAUTH_CLIENT_ID`, `OAUTH_AUDIENCE` |
| Security | None | `CORS_ORIGINS`, Rate limit settings |
| Frontend | `VITE_API_URL`, `VITE_OIDC_AUTHORITY` | `VITE_API_PREFIX` |

## Backend Environment Variables

### Required Variables

These variables MUST be set before deployment. The application will fail to start without them.

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:pass@host:5432/db` | Must use `asyncpg` driver |
| `REDIS_URL` | Redis connection string | `redis://default:pass@host:6379/0` | Used for caching and rate limiting |
| `OAUTH_ISSUER_URL` | OAuth2/OIDC issuer URL | `https://auth.example.com/realms/myapp` | Must be accessible from backend |
| `MIGRATION_DATABASE_URL` | Database URL for migrations | `postgresql+asyncpg://migrator:pass@host:5432/db` | Uses migration user with DDL permissions |

### Optional Variables (with defaults)

| Variable | Description | Default | Valid Values |
|----------|-------------|---------|--------------|
| `ENV` | Environment identifier | `development` | `development`, `staging`, `production` |
| `DEBUG` | Enable debug mode | `true` | `true`, `false` |
| `LOG_LEVEL` | Logging verbosity | `debug` | `debug`, `info`, `warning`, `error` |
| `API_V1_PREFIX` | API version prefix | `/api/v1` | Any valid URL path |
| `CORS_ORIGINS` | Allowed CORS origins | `*` | Comma-separated URLs or `*` |
| `RATE_LIMIT_PER_MINUTE` | Rate limit threshold | `100` | Integer |
| `RATE_LIMIT_BURST` | Rate limit burst size | `20` | Integer |

### OAuth Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `OAUTH_ISSUER_URL` | OIDC issuer URL | Required | Used for JWKS discovery |
| `OAUTH_CLIENT_ID` | OAuth client ID | `{{ cookiecutter.project_slug }}` | For token validation |
| `OAUTH_AUDIENCE` | Expected token audience | Same as client ID | For multi-audience tokens |
| `OAUTH_REQUIRED_SCOPES` | Required scopes | `openid,profile` | Comma-separated |

{% if cookiecutter.include_observability == "yes" %}
### Observability Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `OTEL_SERVICE_NAME` | Service name for tracing | `backend` | Identifies service in traces |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://tempo:4317` | Tempo/Jaeger endpoint |
| `OTEL_TRACES_SAMPLER` | Trace sampling strategy | `parentbased_traceidratio` | Sampling configuration |
| `OTEL_TRACES_SAMPLER_ARG` | Sampler argument | `0.1` | 10% sampling in production |
{% endif %}

{% if cookiecutter.include_sentry == "yes" %}
### Sentry Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `SENTRY_DSN` | Sentry project DSN | None | Required for Sentry integration |
| `SENTRY_ENVIRONMENT` | Environment tag | Same as `ENV` | Groups errors by environment |
| `SENTRY_TRACES_SAMPLE_RATE` | Performance sampling | `0.1` | 10% of transactions |
{% endif %}

## Frontend Environment Variables

Frontend variables are embedded at **build time** via Vite.

### Build-Time Variables

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:8000` | Must be accessible from browser |
| `VITE_API_PREFIX` | API path prefix | `/api/v1` | Should match backend `API_V1_PREFIX` |
| `VITE_OIDC_AUTHORITY` | OIDC provider URL | Same as `OAUTH_ISSUER_URL` | For OIDC client |
| `VITE_OIDC_CLIENT_ID` | OIDC client ID | `{{ cookiecutter.project_slug }}-frontend` | Public client ID |

### Important Notes

1. **Build-Time Only**: Frontend variables are embedded during `npm run build`. Changes require a rebuild.
2. **Public Variables**: All `VITE_*` variables are exposed in the browser. Never put secrets here.
3. **Runtime Configuration**: For runtime configuration, consider a `/config` endpoint pattern.

## Environment-Specific Configuration

### Development

```bash
# .env (development)
ENV=development
DEBUG=true
LOG_LEVEL=debug

DATABASE_URL=postgresql+asyncpg://appuser:apppassword@localhost:5432/appdb
REDIS_URL=redis://localhost:6379/0
OAUTH_ISSUER_URL=http://localhost:8080/realms/{{ cookiecutter.keycloak_realm_name }}
```

### Staging

```bash
# .env.staging
ENV=staging
DEBUG=false
LOG_LEVEL=debug

DATABASE_URL=postgresql+asyncpg://appuser:${DB_PASSWORD}@staging-db.internal:5432/appdb
REDIS_URL=redis://default:${REDIS_PASSWORD}@staging-redis.internal:6379/0
OAUTH_ISSUER_URL=https://auth-staging.example.com/realms/{{ cookiecutter.keycloak_realm_name }}
```

### Production

```bash
# .env.production
ENV=production
DEBUG=false
LOG_LEVEL=info

DATABASE_URL=postgresql+asyncpg://appuser:${DB_PASSWORD}@prod-db.internal:5432/appdb
REDIS_URL=redis://default:${REDIS_PASSWORD}@prod-redis.internal:6379/0
OAUTH_ISSUER_URL=https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}

# Stricter rate limiting
RATE_LIMIT_PER_MINUTE=60
```

## Kubernetes Configuration

When deploying to Kubernetes, environment variables are managed via ConfigMaps and Secrets.

### ConfigMap (Non-Sensitive)

```yaml
# k8s/base/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ cookiecutter.project_slug }}-config
data:
  ENV: "production"
  LOG_LEVEL: "info"
  API_V1_PREFIX: "{{ cookiecutter.backend_api_prefix }}"
  OAUTH_ISSUER_URL: "https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}"
```

### Secrets (Sensitive)

```bash
# Create secrets via kubectl
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --from-literal=DATABASE_URL='postgresql+asyncpg://...' \
  --from-literal=REDIS_URL='redis://...' \
  --from-literal=MIGRATION_DATABASE_URL='postgresql+asyncpg://...'
```

See [Secrets Management](./secrets-management.md) for production-ready patterns.

## Configuration Validation

The application validates configuration at startup:

1. **Required Variables**: Checked on import of `config.py`
2. **URL Format**: Database and Redis URLs are validated
3. **Type Coercion**: Boolean and integer values are automatically converted

### Startup Validation Errors

If configuration is invalid, the application logs specific errors:

```
ValidationError: DATABASE_URL must be set
ValidationError: Invalid OAUTH_ISSUER_URL format
```

## Troubleshooting

### Common Issues

**Issue**: Application fails to connect to database
```bash
# Verify DATABASE_URL is set correctly
echo $DATABASE_URL
# Test connection
python -c "import asyncpg; asyncpg.connect('$DATABASE_URL')"
```

**Issue**: OAuth token validation fails
```bash
# Verify OIDC discovery endpoint
curl $OAUTH_ISSUER_URL/.well-known/openid-configuration
```

**Issue**: CORS errors in browser
```bash
# Verify CORS_ORIGINS includes frontend URL
# For development, can use CORS_ORIGINS=*
```

### Debugging Configuration

Enable configuration debugging:
```bash
DEBUG=true LOG_LEVEL=debug python -c "from app.core.config import settings; print(settings.model_dump())"
```
```

### 2. Secrets Management Documentation (`docs/secrets-management.md`)

```markdown
# Secrets Management

This guide covers secure secrets management patterns for {{ cookiecutter.project_name }}.

## Overview

Secrets include:
- Database credentials (`DATABASE_URL`)
- Redis credentials (`REDIS_URL`)
- OAuth client secrets (if using confidential clients)
- API keys for external services
- TLS certificates

**Golden Rule**: Never commit secrets to version control.

## Kubernetes Secrets

### Basic Usage

```bash
# Create secrets from command line
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --namespace {{ cookiecutter.project_slug }} \
  --from-literal=DATABASE_URL='postgresql+asyncpg://user:pass@host:5432/db' \
  --from-literal=REDIS_URL='redis://default:pass@host:6379/0'
```

### From File

```bash
# Create from environment file (more secure)
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --namespace {{ cookiecutter.project_slug }} \
  --from-env-file=.env.production.secrets
```

### View Secrets (Carefully)

```bash
# List secrets
kubectl get secrets -n {{ cookiecutter.project_slug }}

# View secret (base64 encoded)
kubectl get secret {{ cookiecutter.project_slug }}-secrets -o yaml

# Decode specific value
kubectl get secret {{ cookiecutter.project_slug }}-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

## HashiCorp Vault Integration

For production environments, consider HashiCorp Vault for centralized secrets management.

### Vault Agent Sidecar

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
        vault.hashicorp.com/role: "{{ cookiecutter.project_slug }}"
        vault.hashicorp.com/agent-inject-secret-database: "secret/data/{{ cookiecutter.project_slug }}/database"
        vault.hashicorp.com/agent-inject-template-database: |
          {{ "{{" }}- with secret "secret/data/{{ cookiecutter.project_slug }}/database" -{{ "}}" }}
          DATABASE_URL={{ "{{" }} .Data.data.url {{ "}}" }}
          {{ "{{" }}- end {{ "}}" }}
```

### Setup Steps

1. Install Vault Helm chart
2. Configure Kubernetes authentication
3. Create secrets in Vault
4. Configure deployment annotations

## AWS Secrets Manager

For AWS deployments, use AWS Secrets Manager with the External Secrets Operator.

### External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: {{ cookiecutter.project_slug }}
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {{ cookiecutter.project_slug }}-secrets
  namespace: {{ cookiecutter.project_slug }}
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: {{ cookiecutter.project_slug }}-secrets
    creationPolicy: Owner
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: {{ cookiecutter.project_slug }}/database
        property: url
    - secretKey: REDIS_URL
      remoteRef:
        key: {{ cookiecutter.project_slug }}/redis
        property: url
```

### Setup Steps

1. Install External Secrets Operator
2. Create IAM role for service account (IRSA)
3. Configure SecretStore
4. Create ExternalSecret resources

## Sealed Secrets

For GitOps workflows, Bitnami Sealed Secrets allows encrypting secrets that can be safely committed.

### Installation

```bash
# Install kubeseal CLI
brew install kubeseal

# Install controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
```

### Usage

```bash
# Create sealed secret
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --dry-run=client \
  --from-literal=DATABASE_URL='...' \
  -o yaml | kubeseal -o yaml > sealed-secrets.yaml

# Apply sealed secret (can be committed to git)
kubectl apply -f sealed-secrets.yaml
```

## Best Practices

### Do

- Use a secrets manager in production (Vault, AWS SM, GCP Secret Manager)
- Rotate secrets regularly (automate with Vault)
- Use separate secrets per environment
- Audit secret access
- Use least-privilege access

### Do Not

- Commit secrets to git (even in private repos)
- Log secrets or include in error messages
- Share secrets across environments
- Use default/example passwords in production
- Store secrets in ConfigMaps

## Secret Rotation

### Database Password Rotation

1. Create new password in secrets manager
2. Update database user password
3. Update Kubernetes secret
4. Restart pods to pick up new secret

```bash
# Rolling restart to pick up new secrets
kubectl rollout restart deployment/backend -n {{ cookiecutter.project_slug }}
```

### Automatic Rotation

Consider using:
- Vault dynamic secrets (auto-rotating database credentials)
- AWS RDS IAM authentication (no password needed)
- External Secrets Operator refresh intervals

## Troubleshooting

### Secret Not Found

```bash
# Check secret exists
kubectl get secret {{ cookiecutter.project_slug }}-secrets -n {{ cookiecutter.project_slug }}

# Check secret is mounted in pod
kubectl exec -n {{ cookiecutter.project_slug }} <pod-name> -- env | grep DATABASE
```

### Permission Denied

```bash
# Check RBAC
kubectl auth can-i get secrets --as=system:serviceaccount:{{ cookiecutter.project_slug }}:default

# Check External Secrets Operator logs
kubectl logs -n external-secrets deployment/external-secrets
```
```

### 3. Production Environment Template (`.env.production.example`)

```bash
# {{ cookiecutter.project_name }} - Production Environment Configuration
#
# Copy this file to .env.production and fill in actual values.
# NEVER commit .env.production to version control.
#
# For Kubernetes deployments, use ConfigMaps and Secrets instead.
# See docs/configuration.md for details.

# =============================================================================
# ENVIRONMENT
# =============================================================================

# Environment identifier (development, staging, production)
ENV=production

# Disable debug mode in production
DEBUG=false

# Production logging level (info recommended for production)
LOG_LEVEL=info

# =============================================================================
# DATABASE (REQUIRED)
# =============================================================================

# PostgreSQL connection string for application user
# Format: postgresql+asyncpg://user:password@host:port/database
# The appuser has limited permissions (no DDL)
DATABASE_URL=postgresql+asyncpg://appuser:CHANGE_ME@db-host:5432/{{ cookiecutter.project_slug }}

# PostgreSQL connection string for migrations
# Format: postgresql+asyncpg://user:password@host:port/database
# The migrator user has DDL permissions for schema changes
MIGRATION_DATABASE_URL=postgresql+asyncpg://migrator:CHANGE_ME@db-host:5432/{{ cookiecutter.project_slug }}

# =============================================================================
# REDIS (REQUIRED)
# =============================================================================

# Redis connection string
# Format: redis://default:password@host:port/database
REDIS_URL=redis://default:CHANGE_ME@redis-host:6379/0

# =============================================================================
# OAUTH / AUTHENTICATION (REQUIRED)
# =============================================================================

# OAuth2/OIDC issuer URL (Keycloak realm URL)
OAUTH_ISSUER_URL=https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}

# OAuth client ID for backend token validation
OAUTH_CLIENT_ID={{ cookiecutter.project_slug }}

# =============================================================================
# API CONFIGURATION
# =============================================================================

# API version prefix
API_V1_PREFIX={{ cookiecutter.backend_api_prefix }}

# CORS allowed origins (comma-separated)
# In production, specify exact origins
CORS_ORIGINS=https://app.example.com,https://www.example.com

# =============================================================================
# RATE LIMITING
# =============================================================================

# Requests per minute per client
RATE_LIMIT_PER_MINUTE=60

# Burst allowance
RATE_LIMIT_BURST=10

# =============================================================================
# FRONTEND (BUILD-TIME)
# =============================================================================

# These are embedded during frontend build, not runtime
VITE_API_URL=https://api.example.com
VITE_API_PREFIX={{ cookiecutter.backend_api_prefix }}
VITE_OIDC_AUTHORITY=https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}
VITE_OIDC_CLIENT_ID={{ cookiecutter.project_slug }}-frontend

{% if cookiecutter.include_observability == "yes" %}
# =============================================================================
# OBSERVABILITY (OPTIONAL)
# =============================================================================

# OpenTelemetry service name
OTEL_SERVICE_NAME=backend

# OTLP collector endpoint (Tempo, Jaeger, etc.)
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317

# Trace sampling rate (0.0 to 1.0)
# 0.1 = 10% of requests traced (recommended for production)
OTEL_TRACES_SAMPLER_ARG=0.1
{% endif %}

{% if cookiecutter.include_sentry == "yes" %}
# =============================================================================
# SENTRY (OPTIONAL)
# =============================================================================

# Sentry DSN for error tracking
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0

# Sentry environment tag
SENTRY_ENVIRONMENT=production

# Performance monitoring sample rate (0.0 to 1.0)
SENTRY_TRACES_SAMPLE_RATE=0.1
{% endif %}
```

### 4. Staging Environment Template (`.env.staging.example`)

```bash
# {{ cookiecutter.project_name }} - Staging Environment Configuration
#
# Copy this file to .env.staging and fill in actual values.
# NEVER commit .env.staging to version control.

# =============================================================================
# ENVIRONMENT
# =============================================================================

ENV=staging
DEBUG=false
LOG_LEVEL=debug

# =============================================================================
# DATABASE (REQUIRED)
# =============================================================================

DATABASE_URL=postgresql+asyncpg://appuser:CHANGE_ME@staging-db:5432/{{ cookiecutter.project_slug }}
MIGRATION_DATABASE_URL=postgresql+asyncpg://migrator:CHANGE_ME@staging-db:5432/{{ cookiecutter.project_slug }}

# =============================================================================
# REDIS (REQUIRED)
# =============================================================================

REDIS_URL=redis://default:CHANGE_ME@staging-redis:6379/0

# =============================================================================
# OAUTH (REQUIRED)
# =============================================================================

OAUTH_ISSUER_URL=https://auth-staging.example.com/realms/{{ cookiecutter.keycloak_realm_name }}
OAUTH_CLIENT_ID={{ cookiecutter.project_slug }}

# =============================================================================
# API CONFIGURATION
# =============================================================================

API_V1_PREFIX={{ cookiecutter.backend_api_prefix }}
CORS_ORIGINS=https://staging.example.com

# =============================================================================
# RATE LIMITING (Relaxed for testing)
# =============================================================================

RATE_LIMIT_PER_MINUTE=200
RATE_LIMIT_BURST=50

# =============================================================================
# FRONTEND (BUILD-TIME)
# =============================================================================

VITE_API_URL=https://api-staging.example.com
VITE_API_PREFIX={{ cookiecutter.backend_api_prefix }}
VITE_OIDC_AUTHORITY=https://auth-staging.example.com/realms/{{ cookiecutter.keycloak_realm_name }}
VITE_OIDC_CLIENT_ID={{ cookiecutter.project_slug }}-frontend

{% if cookiecutter.include_sentry == "yes" %}
# =============================================================================
# SENTRY (Higher sampling for staging)
# =============================================================================

SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=staging
SENTRY_TRACES_SAMPLE_RATE=0.5
{% endif %}
```

## Success Criteria

### Functional Requirements
- [ ] FR-DEP-010: Environment configuration documentation lists required variables
- [ ] FR-DEP-011: Environment configuration documentation lists optional variables with defaults
- [ ] FR-DEP-012: Secrets management examples documented for Vault and AWS SM
- [ ] All backend configuration variables are documented with descriptions
- [ ] All frontend configuration variables are documented with build-time notes
- [ ] Environment-specific templates exist for staging and production

### Verification Steps
1. **Documentation Review:**
   ```bash
   # Check documentation exists
   ls docs/configuration.md docs/secrets-management.md

   # Verify all config.py settings are documented
   grep -E "^[A-Z_]+:" backend/app/core/config.py | wc -l
   # Compare with documented variables
   ```

2. **Template Validation:**
   ```bash
   # Verify environment templates are valid shell syntax
   bash -n .env.production.example
   bash -n .env.staging.example
   ```

3. **Cross-Reference Check:**
   - Compare documented variables with `config.py`
   - Compare documented variables with `k8s/base/configmap.yaml`
   - Verify all ConfigMap keys are documented

### Quality Gates
- [ ] All required variables are clearly marked
- [ ] All defaults are accurate
- [ ] Examples use realistic placeholder values (not actual secrets)
- [ ] Kubernetes configuration patterns are documented
- [ ] At least two secrets management patterns are documented
- [ ] Documentation follows project style

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-01 | ConfigMap/Secret variable names | Documentation references K8s configuration |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-01 | Configuration documentation location | CLAUDE.md update references docs/ |
| P6-02 | Configuration migration patterns | Migration guide references this documentation |

### Integration Contract
```yaml
# Contract: Configuration documentation structure

# Files created
docs/
  configuration.md              # Main reference (all variables)
  secrets-management.md         # Secrets patterns (Vault, AWS SM, Sealed Secrets)

.env.production.example         # Production template (no secrets)
.env.staging.example            # Staging template (no secrets)

# Variable documentation format
| Variable | Description | Default | Notes |

# Environment sections
- Backend Required
- Backend Optional
- OAuth Configuration
- Observability (conditional)
- Sentry (conditional)
- Frontend Build-Time

# Secrets management patterns
- Kubernetes Secrets (basic)
- HashiCorp Vault (production)
- AWS Secrets Manager (cloud)
- Sealed Secrets (GitOps)
```

## Monitoring and Observability

### Documentation Metrics
- Number of variables documented
- Percentage of config.py settings covered
- Last documentation update date

### User Experience
- Clear distinction between required and optional
- Environment-specific examples
- Troubleshooting section for common issues

## Infrastructure Needs

### Documentation Platform
- Markdown format for GitHub/GitLab rendering
- Compatible with static site generators (MkDocs, Docusaurus)

### No Additional Infrastructure Required
This task is documentation-only.

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Comprehensive variable audit required
- Multiple documentation files to create
- Secrets management patterns research
- Environment templates with conditionals
- Cross-referencing with existing configuration

## Notes

### Design Decisions

**1. Separate Secrets Management Document:**
- Keeps main configuration.md focused
- Allows detailed coverage of each pattern
- Easier to update as patterns evolve

**2. Environment-Specific Templates:**
- Provides starting point for each environment
- Shows different default values per environment
- Includes conditionals for optional features

**3. Kubernetes-First Approach:**
- Kubernetes deployment is the target
- ConfigMap/Secret patterns emphasized
- Docker Compose patterns secondary

**4. External Secrets Manager Focus:**
- Basic K8s secrets for development
- Vault/AWS SM for production
- Sealed Secrets for GitOps

### Style Guidelines

- Use tables for variable references
- Include example values (not real secrets)
- Provide troubleshooting for common issues
- Link to relevant ADRs and tasks

### Related Requirements
- US-4.2: Environment Configuration Management
- FR-DEP-010: Required variables documented
- FR-DEP-011: Optional variables with defaults
- FR-DEP-012: Secrets management examples
