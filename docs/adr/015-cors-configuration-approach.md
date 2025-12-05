# ADR-015: CORS Configuration Approach

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2025-12-05 |
| **Decision Makers** | Project Team |

## Context

The project-starter template implements a separated frontend/backend architecture where the frontend (Vite on port 5173) makes API requests to the backend (FastAPI on port 8000). This cross-origin setup requires CORS (Cross-Origin Resource Sharing) configuration. Key challenges include:

1. **Development Convenience**: Developers need unrestricted CORS during local development
2. **Security**: Production environments must restrict origins to prevent CSRF and data exfiltration
3. **Cookie Authentication**: The template uses HttpOnly cookies requiring `credentials: true` in CORS
4. **OAuth Flows**: Browser-based OAuth callbacks may originate from different domains
5. **Flexibility**: Different deployment environments have different allowed origins

The CORS configuration must balance security with developer experience while supporting cookie-based authentication.

## Decision

We implement a **configurable CORS policy** via environment variables with sensible development defaults.

**FastAPI CORS Middleware** (`backend/app/main.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)
```

**Configuration** (`backend/app/core/config.py`):
```python
class Settings(BaseSettings):
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
```

**Environment Variable Format**:
```bash
# Development (default)
CORS_ORIGINS=http://localhost:5173,http://localhost:5173

# Production (set explicitly)
CORS_ORIGINS=https://myapp.example.com,https://admin.example.com
```

**Middleware Order** (`backend/app/main.py`):
```python
# 1. Observability middleware (if enabled) - instruments all requests
setup_observability(app)

# 2. CORS middleware - handles preflight and response headers
app.add_middleware(CORSMiddleware, ...)

# 3. Tenant Resolution middleware - extracts tenant from JWT
app.add_middleware(TenantResolutionMiddleware)
```

## Consequences

### Positive

1. **Development Works Out of Box**: Default configuration allows frontend (localhost:5173) to call backend (localhost:8000) without any setup.

2. **Credential Support**: `allow_credentials=True` enables cookie-based authentication:
   ```python
   # Frontend can send cookies with requests
   fetch('http://localhost:8000/api/v1/protected', {
       credentials: 'include'  # Sends HttpOnly auth cookies
   })
   ```

3. **Environment-Based Configuration**: Production CORS origins set via environment variables without code changes:
   ```bash
   # docker-compose.prod.yml
   environment:
     CORS_ORIGINS: https://myapp.com
   ```

4. **Comma-Separated Parsing**: Multiple origins supported in single environment variable:
   ```bash
   CORS_ORIGINS=https://app.example.com,https://staging.example.com
   ```

5. **Permissive Methods/Headers in Development**: `["*"]` for methods and headers simplifies development; production can restrict if needed.

### Negative

1. **Wildcard Not Supported with Credentials**: Cannot use `allow_origins=["*"]` with `allow_credentials=True` (CORS spec restriction). Must explicitly list origins.

2. **Manual Production Configuration**: Operators must configure `CORS_ORIGINS` for each deployment environment.

3. **No Origin Validation**: CORS origins are trusted as-is; typos could create security gaps or broken configurations.

4. **Permissive Default Headers**: `allow_headers=["*"]` may be overly permissive for some security policies.

### Neutral

1. **Preflight Caching**: FastAPI's CORS middleware handles OPTIONS preflight requests; caching controlled by browser defaults.

2. **Middleware Order Matters**: CORS must run early to handle preflight before authentication middleware rejects unauthenticated OPTIONS requests.

## Alternatives Considered

### Wildcard Origins (`allow_origins=["*"]`)

**Approach**: Allow any origin during development.

**Why Not Chosen**:
- Incompatible with `allow_credentials=True` per CORS spec
- Browser rejects credentials with wildcard origin
- Would break cookie-based authentication flow

### Origin Reflection (Dynamic Allow-Origin)

**Approach**: Reflect the request's Origin header in Access-Control-Allow-Origin.

**Why Not Chosen**:
- Security risk: any origin becomes allowed
- FastAPI's CORSMiddleware doesn't support this pattern easily
- Explicit allowlist is more secure and auditable

### Proxy-Based CORS Avoidance

**Approach**: Proxy API requests through frontend dev server (Vite proxy) to avoid CORS.

**Why Not Chosen**:
- Masks real production behavior during development
- Adds complexity to frontend configuration
- OAuth callbacks may still require CORS handling
- Production still needs CORS configuration

### Separate Development/Production Config Files

**Approach**: Maintain separate config.py files for each environment.

**Why Not Chosen**:
- Environment variables are standard pattern for 12-factor apps
- Single config file with env var overrides is cleaner
- Reduces risk of deploying wrong configuration

---

## Security Considerations

**Production Checklist**:
1. [ ] Set `CORS_ORIGINS` to explicit production domain(s) only
2. [ ] Consider restricting `CORS_ALLOW_METHODS` to actual methods used
3. [ ] Review `CORS_ALLOW_HEADERS` for unnecessary headers
4. [ ] Ensure HTTPS for all production origins
5. [ ] Never use `*` for origins in production with credentials

**Cookie Authentication + CORS**:
- HttpOnly cookies require `credentials: include` on fetch requests
- `allow_credentials=True` must be set in CORS config
- SameSite=Lax cookies work cross-origin only with top-level navigation
- Consider SameSite=None; Secure for cross-site cookie scenarios

---

## Related ADRs

- [ADR-001: FastAPI Backend Framework](./001-fastapi-backend-framework.md) - CORS middleware host
- [ADR-009: Cookie-Based Authentication](./009-cookie-authentication.md) - Requires credentials CORS

## Implementation References

- `backend/app/main.py` - CORSMiddleware configuration
- `backend/app/core/config.py` - CORS settings with validator
- `template/{{cookiecutter.project_slug}}/.env.example` - Environment variable documentation
