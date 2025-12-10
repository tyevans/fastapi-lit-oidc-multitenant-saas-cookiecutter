# Environment Configuration Reference

This document provides a comprehensive reference for all environment variables used by {{ cookiecutter.project_name }}.

## Quick Reference

| Category | Required Variables | Optional Variables |
|----------|-------------------|-------------------|
| Core | `DATABASE_URL`, `REDIS_URL` | `ENV`, `DEBUG`, `LOG_LEVEL` |
| OAuth | `OAUTH_ISSUER_URL` | `OAUTH_AUDIENCE`, `OAUTH_CLIENT_ID` |
| API | None | `API_V1_PREFIX`, `CORS_ORIGINS` |
| Rate Limiting | None | `RATE_LIMIT_*` settings |
| Session | None | `SESSION_COOKIE_*` settings |
| Multi-Tenancy | None | `TENANT_CLAIM_NAME`, `REQUIRE_TENANT_CLAIM` |
| Frontend | `VITE_API_URL`, `VITE_OIDC_AUTHORITY` | `VITE_API_PREFIX` |
{%- if cookiecutter.include_observability == "yes" %}
| Observability | None | `OTEL_*` settings |
{%- endif %}
{%- if cookiecutter.include_sentry == "yes" %}
| Error Tracking | None | `SENTRY_*` settings |
{%- endif %}

---

## Backend Environment Variables

### Required Variables

These variables MUST be set before deployment. The application will fail to start or function incorrectly without them.

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `DATABASE_URL` | PostgreSQL connection string for application runtime | `postgresql+asyncpg://appuser:pass@host:5432/db` | Must use `asyncpg` driver. Uses app_user with RLS enforced. |
| `MIGRATION_DATABASE_URL` | PostgreSQL connection string for migrations | `postgresql+asyncpg://migrator:pass@host:5432/db` | Uses migration_user with BYPASSRLS for schema changes. |
| `REDIS_URL` | Redis connection string | `redis://default:pass@host:6379/0` | Used for caching, rate limiting, and session storage. |
| `OAUTH_ISSUER_URL` | OAuth2/OIDC issuer URL | `https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}` | Must be accessible from backend for JWKS discovery. |

### Optional Variables (with defaults)

#### Application Settings

| Variable | Description | Default | Valid Values |
|----------|-------------|---------|--------------|
| `ENV` | Environment identifier | `development` | `development`, `staging`, `production` |
| `DEBUG` | Enable debug mode | `true` | `true`, `false` |
| `LOG_LEVEL` | Logging verbosity | `info` | `debug`, `info`, `warning`, `error` |
| `APP_NAME` | Application display name | `{{ cookiecutter.project_name }}` | Any string |
| `APP_VERSION` | Application version | `0.1.0` | Semantic version string |

#### Server Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `HOST` | Server bind address | `0.0.0.0` | Use `127.0.0.1` for local-only access |
| `PORT` | Server port | `{{ cookiecutter.backend_port }}` | Must match container port in Docker/K8s |
| `RELOAD` | Enable hot reload | `true` | Disable in production |

#### API Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `API_V1_PREFIX` | API version prefix | `{{ cookiecutter.backend_api_prefix }}` | All API routes are prefixed with this |

#### CORS Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:{{ cookiecutter.frontend_port }},http://localhost:5173` | Comma-separated URLs or `*` for development |
| `CORS_ALLOW_CREDENTIALS` | Allow credentials | `true` | Required for cookie-based auth |
| `CORS_ALLOW_METHODS` | Allowed HTTP methods | `*` | Comma-separated or `*` |
| `CORS_ALLOW_HEADERS` | Allowed headers | `*` | Comma-separated or `*` |

#### OAuth Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `OAUTH_ISSUER_URL` | OIDC issuer URL | Required | Used for JWKS discovery and token validation |
| `OAUTH_AUDIENCE` | Expected token audience | `{{ cookiecutter.keycloak_backend_client_id }}` | For audience claim validation |
| `OAUTH_ALGORITHMS` | Supported JWT algorithms | `RS256` | Comma-separated (e.g., `RS256,RS384`) |
| `OAUTH_CLIENT_ID` | OAuth client ID | `{{ cookiecutter.keycloak_backend_client_id }}` | Backend client identifier |
| `OAUTH_CLIENT_SECRET` | OAuth client secret | `your-client-secret` | Set via environment in production |
| `OAUTH_REDIRECT_URI` | OAuth redirect URI | `http://localhost:{{ cookiecutter.backend_port }}{{ cookiecutter.backend_api_prefix }}/auth/callback` | Must match Keycloak client config |
| `OAUTH_SCOPES` | Requested OAuth scopes | `openid,profile,email` | Comma-separated |
| `OAUTH_USE_PKCE` | Enable PKCE | `true` | Recommended for enhanced security |

#### JWKS Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `JWKS_CACHE_TTL` | JWKS cache duration (seconds) | `3600` | How long to cache public keys |
| `JWKS_HTTP_TIMEOUT` | JWKS HTTP timeout (seconds) | `10` | Timeout for JWKS/OIDC requests |

#### Rate Limiting Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` | Disable only for testing |
| `RATE_LIMIT_REQUESTS_PER_MINUTE` | General request limit | `100` | Per client IP |
| `RATE_LIMIT_FAILED_AUTH_PER_MINUTE` | Failed auth limit | `10` | Prevents brute force attacks |
| `RATE_LIMIT_WINDOW_SECONDS` | Time window | `60` | Window for rate limit counting |

#### Session Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `SESSION_COOKIE_SECURE` | Set Secure cookie flag | `false` | Set `true` for HTTPS in production |
| `SESSION_COOKIE_MAX_AGE` | Cookie max age (seconds) | `604800` | 7 days default |
| `FRONTEND_URL` | Frontend URL for redirects | `http://localhost:{{ cookiecutter.frontend_port }}` | Used for post-auth redirects |

#### Multi-Tenancy Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `TENANT_CLAIM_NAME` | JWT claim for tenant ID | `tenant_id` | Must match Keycloak mapper config |
| `REQUIRE_TENANT_CLAIM` | Require tenant in tokens | `true` | Set `false` for single-tenant mode |
| `TENANT_CACHE_TTL` | Tenant cache duration | `3600` | Seconds to cache tenant info |

{%- if cookiecutter.include_sentry == "yes" %}

#### Sentry Error Tracking

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `SENTRY_DSN` | Sentry project DSN | Empty (disabled) | Get from Sentry project settings |
| `SENTRY_ENVIRONMENT` | Environment tag | `development` | Groups errors by environment |
| `SENTRY_RELEASE` | Release version | Same as `APP_VERSION` | Track errors by deployment |
| `SENTRY_TRACES_SAMPLE_RATE` | Performance sampling | `0.1` | 10% of transactions traced |
| `SENTRY_PROFILES_SAMPLE_RATE` | Profile sampling | `0.1` | 10% of traces profiled |
{%- endif %}

#### Security Headers Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `SECURITY_HEADERS_ENABLED` | Enable security headers | `true` | Master toggle |
| `CSP_ENABLED` | Enable Content-Security-Policy | `true` | Prevents XSS attacks |
| `CSP_DEFAULT_SRC` | CSP default-src | `'self'` | Default content source |
| `CSP_SCRIPT_SRC` | CSP script-src | `'self' 'unsafe-inline'` | Required for Lit components |
| `CSP_STYLE_SRC` | CSP style-src | `'self' 'unsafe-inline'` | Required for Lit components |
| `CSP_IMG_SRC` | CSP img-src | `'self' data: https:` | Allowed image sources |
| `CSP_FONT_SRC` | CSP font-src | `'self'` | Allowed font sources |
| `CSP_CONNECT_SRC` | CSP connect-src | `'self'` | Extended with FRONTEND_URL |
| `CSP_FRAME_ANCESTORS` | CSP frame-ancestors | `'none'` | Prevents clickjacking |
| `CSP_BASE_URI` | CSP base-uri | `'self'` | Allowed base URIs |
| `CSP_FORM_ACTION` | CSP form-action | `'self'` | Allowed form targets |
| `CSP_REPORT_URI` | CSP report-uri | Empty | CSP violation reporting endpoint |
| `HSTS_ENABLED` | Enable HSTS header | `true` | Only for HTTPS |
| `HSTS_MAX_AGE` | HSTS max-age (seconds) | `31536000` | 1 year |
| `HSTS_INCLUDE_SUBDOMAINS` | Include subdomains in HSTS | `true` | Apply to all subdomains |
| `HSTS_PRELOAD` | Enable HSTS preload | `false` | Requires careful consideration |
| `X_FRAME_OPTIONS` | X-Frame-Options header | `DENY` | `DENY`, `SAMEORIGIN`, or empty |
| `X_CONTENT_TYPE_OPTIONS` | X-Content-Type-Options | `nosniff` | Prevents MIME sniffing |
| `REFERRER_POLICY` | Referrer-Policy header | `strict-origin-when-cross-origin` | Controls referrer info |
| `PERMISSIONS_POLICY` | Permissions-Policy header | See config.py | Feature permissions |
| `X_XSS_PROTECTION` | X-XSS-Protection header | `1; mode=block` | Legacy XSS protection |

---

## Frontend Environment Variables

Frontend variables are embedded at **build time** via Vite. They are prefixed with `VITE_` to be exposed to the client.

### Build-Time Variables

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:{{ cookiecutter.backend_port }}` | Must be accessible from browser |
| `VITE_API_PREFIX` | API path prefix | `{{ cookiecutter.backend_api_prefix }}` | Should match backend `API_V1_PREFIX` |
| `VITE_OIDC_AUTHORITY` | OIDC provider URL | Same as `OAUTH_ISSUER_URL` | For OIDC client initialization |
| `VITE_OIDC_CLIENT_ID` | OIDC client ID | `{{ cookiecutter.keycloak_frontend_client_id }}` | Public client ID (no secret) |

### Important Notes

1. **Build-Time Only**: Frontend variables are embedded during `npm run build`. Changes require a rebuild and redeployment.

2. **Public Variables**: All `VITE_*` variables are exposed in the browser bundle. **Never put secrets in VITE_ variables.**

3. **Runtime Configuration**: For runtime configuration without rebuilds, consider:
   - A `/config` endpoint pattern that serves configuration JSON
   - Environment injection at container startup via nginx substitution

---

## Infrastructure Variables

### PostgreSQL (Docker Compose)

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `POSTGRES_HOST` | Database hostname | `postgres` | Container service name |
| `POSTGRES_PORT` | Database port | `{{ cookiecutter.postgres_port }}` | Host-mapped port |
| `POSTGRES_DB` | Database name | `{{ cookiecutter.postgres_db }}` | Application database |
| `POSTGRES_USER` | Admin username | `{{ cookiecutter.postgres_user }}` | Used by Keycloak |
| `POSTGRES_PASSWORD` | Admin password | `change_me_in_production` | **Change in production!** |

### Redis (Docker Compose)

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `REDIS_HOST` | Redis hostname | `redis` | Container service name |
| `REDIS_PORT` | Redis port | `{{ cookiecutter.redis_port }}` | Host-mapped port |
| `REDIS_PASSWORD` | Redis password | `{{ cookiecutter.redis_password }}` | Required for auth |

### Keycloak (Docker Compose)

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `KEYCLOAK_PORT` | Keycloak port | `{{ cookiecutter.keycloak_port }}` | Admin console and OIDC |
| `KEYCLOAK_ADMIN` | Admin username | `{{ cookiecutter.keycloak_admin }}` | Initial admin user |
| `KEYCLOAK_ADMIN_PASSWORD` | Admin password | `{{ cookiecutter.keycloak_admin_password }}` | **Change in production!** |

{%- if cookiecutter.include_observability == "yes" %}

### OpenTelemetry Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `OTEL_SERVICE_NAME` | Service name for tracing | `backend` | Identifies service in Tempo/Grafana |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector endpoint | `http://tempo:4317` | gRPC endpoint for Tempo |
| `OTEL_TRACES_SAMPLER` | Trace sampling strategy | `parentbased_traceidratio` | Sampling configuration |
| `OTEL_TRACES_SAMPLER_ARG` | Sampler argument | `0.1` | 10% sampling rate |

### Observability Service Ports

| Service | Variable | Default | Notes |
|---------|----------|---------|-------|
| Grafana | `GRAFANA_PORT` | `{{ cookiecutter.grafana_port }}` | Dashboard UI |
| Prometheus | `PROMETHEUS_PORT` | `{{ cookiecutter.prometheus_port }}` | Metrics server |
| Loki | `LOKI_PORT` | `{{ cookiecutter.loki_port }}` | Log aggregation |
| Tempo | `TEMPO_HTTP_PORT` | `{{ cookiecutter.tempo_http_port }}` | Trace HTTP API |
| Tempo OTLP gRPC | `TEMPO_OTLP_GRPC_PORT` | `{{ cookiecutter.tempo_otlp_grpc_port }}` | OTLP gRPC ingestion |
| Tempo OTLP HTTP | `TEMPO_OTLP_HTTP_PORT` | `{{ cookiecutter.tempo_otlp_http_port }}` | OTLP HTTP ingestion |
{%- endif %}

---

## Environment-Specific Configuration

### Development

```bash
# .env (development)
ENV=development
DEBUG=true
LOG_LEVEL=debug
RELOAD=true

# Database - Local Docker
DATABASE_URL=postgresql+asyncpg://{{ cookiecutter.postgres_app_user }}:{{ cookiecutter.postgres_app_password }}@postgres:5432/{{ cookiecutter.postgres_db }}
MIGRATION_DATABASE_URL=postgresql+asyncpg://{{ cookiecutter.postgres_migration_user }}:{{ cookiecutter.postgres_migration_password }}@postgres:5432/{{ cookiecutter.postgres_db }}

# Redis - Local Docker
REDIS_URL=redis://default:{{ cookiecutter.redis_password }}@redis:6379/0

# OAuth - Local Keycloak
OAUTH_ISSUER_URL=http://keycloak.localtest.me:{{ cookiecutter.keycloak_port }}/realms/{{ cookiecutter.keycloak_realm_name }}

# CORS - Permissive for development
CORS_ORIGINS=*
```

### Staging

```bash
# .env.staging
ENV=staging
DEBUG=false
LOG_LEVEL=debug

# Database - Managed PostgreSQL
DATABASE_URL=postgresql+asyncpg://appuser:${DB_APP_PASSWORD}@staging-db.internal:5432/{{ cookiecutter.postgres_db }}
MIGRATION_DATABASE_URL=postgresql+asyncpg://migrator:${DB_MIGRATION_PASSWORD}@staging-db.internal:5432/{{ cookiecutter.postgres_db }}

# Redis - Managed Redis
REDIS_URL=redis://default:${REDIS_PASSWORD}@staging-redis.internal:6379/0

# OAuth - Staging Keycloak
OAUTH_ISSUER_URL=https://auth-staging.example.com/realms/{{ cookiecutter.keycloak_realm_name }}

# CORS - Staging domains only
CORS_ORIGINS=https://staging.example.com,https://app-staging.example.com

# Session security
SESSION_COOKIE_SECURE=true
```

### Production

```bash
# .env.production
ENV=production
DEBUG=false
LOG_LEVEL=info
RELOAD=false

# Database - Production PostgreSQL with connection pooling
DATABASE_URL=postgresql+asyncpg://appuser:${DB_APP_PASSWORD}@prod-db.internal:5432/{{ cookiecutter.postgres_db }}
MIGRATION_DATABASE_URL=postgresql+asyncpg://migrator:${DB_MIGRATION_PASSWORD}@prod-db.internal:5432/{{ cookiecutter.postgres_db }}

# Redis - Production Redis cluster
REDIS_URL=redis://default:${REDIS_PASSWORD}@prod-redis.internal:6379/0

# OAuth - Production Keycloak
OAUTH_ISSUER_URL=https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}

# CORS - Production domains only
CORS_ORIGINS=https://example.com,https://app.example.com

# Session security
SESSION_COOKIE_SECURE=true

# Stricter rate limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=60
RATE_LIMIT_BURST=10

# Security headers
HSTS_PRELOAD=true
```

---

## Kubernetes Configuration

When deploying to Kubernetes, environment variables are managed via ConfigMaps and Secrets.

### ConfigMap (Non-Sensitive)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ cookiecutter.project_slug }}-config
data:
  ENV: "production"
  LOG_LEVEL: "info"
  DEBUG: "false"
  API_V1_PREFIX: "{{ cookiecutter.backend_api_prefix }}"
  OAUTH_ISSUER_URL: "https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}"
  TENANT_CLAIM_NAME: "tenant_id"
  REQUIRE_TENANT_CLAIM: "true"
```

### Secrets (Sensitive)

```bash
# Create secrets via kubectl
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --namespace {{ cookiecutter.project_slug }} \
  --from-literal=DATABASE_URL='postgresql+asyncpg://...' \
  --from-literal=MIGRATION_DATABASE_URL='postgresql+asyncpg://...' \
  --from-literal=REDIS_URL='redis://...'
```

See [Secrets Management](./secrets-management.md) for production-ready patterns including Vault, AWS Secrets Manager, and Sealed Secrets.

---

## Configuration Loading

Configuration is loaded via `pydantic-settings` in `backend/app/core/config.py`.

### Loading Priority (highest to lowest)

1. Environment variables
2. `.env` file
3. Default values in `Settings` class

### Type Coercion

Pydantic automatically converts string environment variables to proper types:

- `"true"` / `"false"` -> `bool`
- `"100"` -> `int`
- `"0.5"` -> `float`
- Comma-separated strings -> `List[str]` (via custom validator)

### Accessing Configuration

```python
from app.core.config import settings

# Use settings anywhere in the application
print(settings.DATABASE_URL)
print(settings.CORS_ORIGINS)  # Returns List[str]
```

---

## Related Documentation

- [Secrets Management](./secrets-management.md) - Production secrets patterns
- [Configuration Validation](./configuration-validation.md) - Troubleshooting guide
- [../DEPLOYMENT.md](../DEPLOYMENT.md) - Deployment procedures
- [../runbooks/](../runbooks/) - Operational runbooks
