# P2-02: Add Security Configuration to config.py

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P2-02 |
| **Task Title** | Add Security Configuration to config.py |
| **Domain** | Backend |
| **Complexity** | S (Small) |
| **Estimated Effort** | 0.5 days |
| **Priority** | Should Have |
| **Dependencies** | P2-01 (Security headers middleware must exist) |
| **FRD Requirements** | FR-SEC-006 |

---

## Scope

### What This Task Includes

1. Add security header settings to `config.py` (Settings class)
2. Add environment variables for all configurable security options
3. Update `.env.example` with security header configuration
4. Integrate `SecurityHeadersMiddleware` into `main.py` with cookiecutter conditional
5. Add cookiecutter variable `include_security_headers` to `cookiecutter.json`
6. Update post-generation hooks if needed

### What This Task Excludes

- The middleware implementation itself (P2-01)
- Frontend nginx security headers (already exist)
- ADR documentation (P2-07)
- Security audit checklist (P2-06)

---

## Relevant Code Areas

### Files to Modify

```
template/{{cookiecutter.project_slug}}/
backend/
  app/
    core/
      config.py             # Add security settings
    main.py                 # Add middleware registration with conditional
.env.example                # Add security environment variables
cookiecutter.json           # Add include_security_headers variable
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/app/middleware/security.py` | Middleware from P2-01 |
| `template/{{cookiecutter.project_slug}}/backend/app/core/config.py` | Existing patterns |
| `template/{{cookiecutter.project_slug}}/backend/app/main.py` | Existing middleware registration |

---

## Technical Specification

### Configuration Settings (config.py)

Add the following settings to the `Settings` class:

```python
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ... existing settings ...

    # Security Headers Configuration
    # These settings control the SecurityHeadersMiddleware behavior
    # Reference: OWASP Secure Headers Project

    # Master toggle for security headers
    SECURITY_HEADERS_ENABLED: bool = True

    # Content-Security-Policy (CSP)
    # Default allows Lit components (requires unsafe-inline for script/style)
    CSP_ENABLED: bool = True
    CSP_DEFAULT_SRC: str = "'self'"
    CSP_SCRIPT_SRC: str = "'self' 'unsafe-inline'"
    CSP_STYLE_SRC: str = "'self' 'unsafe-inline'"
    CSP_IMG_SRC: str = "'self' data: https:"
    CSP_FONT_SRC: str = "'self'"
    CSP_CONNECT_SRC: str = "'self'"  # Will be extended with FRONTEND_URL
    CSP_FRAME_ANCESTORS: str = "'none'"
    CSP_REPORT_URI: str = ""  # Empty = disabled, set to CSP reporting endpoint

    # Strict-Transport-Security (HSTS)
    # Only applied for HTTPS requests
    HSTS_ENABLED: bool = True
    HSTS_MAX_AGE: int = 31536000  # 1 year in seconds
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = False  # Requires careful consideration before enabling

    # Other Security Headers
    X_FRAME_OPTIONS: str = "DENY"  # DENY, SAMEORIGIN, or empty to disable
    X_CONTENT_TYPE_OPTIONS: str = "nosniff"
    REFERRER_POLICY: str = "strict-origin-when-cross-origin"
    X_XSS_PROTECTION: str = "1; mode=block"  # Legacy but still useful

    # ... model_config ...
```

### Environment Variables (.env.example)

Add the following to `.env.example`:

```bash
# =============================================================================
# Security Headers Configuration
# =============================================================================
# Master toggle - set to false to disable all security headers
SECURITY_HEADERS_ENABLED=true

# Content-Security-Policy (CSP)
# Note: 'unsafe-inline' is required for Lit web components
CSP_ENABLED=true
CSP_DEFAULT_SRC='self'
CSP_SCRIPT_SRC='self' 'unsafe-inline'
CSP_STYLE_SRC='self' 'unsafe-inline'
CSP_IMG_SRC='self' data: https:
CSP_FONT_SRC='self'
CSP_CONNECT_SRC='self'
CSP_FRAME_ANCESTORS='none'
# CSP_REPORT_URI=https://your-domain.report-uri.com/csp-report

# Strict-Transport-Security (HSTS)
# Only applied for HTTPS connections
HSTS_ENABLED=true
HSTS_MAX_AGE=31536000
HSTS_INCLUDE_SUBDOMAINS=true
HSTS_PRELOAD=false

# Other Security Headers
X_FRAME_OPTIONS=DENY
X_CONTENT_TYPE_OPTIONS=nosniff
REFERRER_POLICY=strict-origin-when-cross-origin
X_XSS_PROTECTION=1; mode=block
```

### Main.py Integration

Update `main.py` to conditionally register the security headers middleware:

```python
"""
Main FastAPI application.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.api.routers import health, test_auth, auth, oauth, todos
from app.middleware.tenant import TenantResolutionMiddleware
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}
{% if cookiecutter.include_security_headers == "yes" %}
from app.middleware.security import SecurityHeadersMiddleware, SecurityHeadersConfig
{% endif %}


# ... lifespan context manager ...


# Initialize FastAPI application
app = FastAPI(
    # ... existing configuration ...
)

{% if cookiecutter.include_observability == "yes" %}
# Setup observability (tracing, metrics, logging)
setup_observability(app)
{% endif %}

{% if cookiecutter.include_security_headers == "yes" %}
# Security Headers Middleware
# Adds security-related HTTP headers to all responses
# Must be added before CORS middleware to ensure headers are present on all responses
if settings.SECURITY_HEADERS_ENABLED:
    # Build connect-src with frontend URL
    connect_src = settings.CSP_CONNECT_SRC
    if settings.FRONTEND_URL and settings.FRONTEND_URL not in connect_src:
        connect_src = f"{connect_src} {settings.FRONTEND_URL}"

    security_config = SecurityHeadersConfig(
        # CSP Configuration
        csp_enabled=settings.CSP_ENABLED,
        csp_default_src=settings.CSP_DEFAULT_SRC,
        csp_script_src=settings.CSP_SCRIPT_SRC,
        csp_style_src=settings.CSP_STYLE_SRC,
        csp_img_src=settings.CSP_IMG_SRC,
        csp_font_src=settings.CSP_FONT_SRC,
        csp_connect_src=connect_src,
        csp_frame_ancestors=settings.CSP_FRAME_ANCESTORS,
        csp_report_uri=settings.CSP_REPORT_URI or None,

        # HSTS Configuration
        hsts_enabled=settings.HSTS_ENABLED,
        hsts_max_age=settings.HSTS_MAX_AGE,
        hsts_include_subdomains=settings.HSTS_INCLUDE_SUBDOMAINS,
        hsts_preload=settings.HSTS_PRELOAD,

        # Other Headers
        x_frame_options=settings.X_FRAME_OPTIONS or None,
        x_content_type_options=settings.X_CONTENT_TYPE_OPTIONS or None,
        referrer_policy=settings.REFERRER_POLICY or None,
        x_xss_protection=settings.X_XSS_PROTECTION or None,
    )
    app.add_middleware(SecurityHeadersMiddleware, config=security_config)
{% endif %}

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # ... existing CORS config ...
)

# Tenant Resolution Middleware
app.add_middleware(TenantResolutionMiddleware)

# ... rest of main.py ...
```

### Cookiecutter Variable (cookiecutter.json)

Add the new variable to `cookiecutter.json`:

```json
{
    "project_name": "My SaaS Project",
    "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
    "project_short_description": "A production-ready SaaS application",

    "...existing variables...": "...",

    "include_observability": ["yes", "no"],
    "include_security_headers": ["yes", "no"],

    "...remaining variables...": "..."
}
```

**Note:** Default is "yes" because security headers are important for production deployments.

### Middleware Order

The middleware registration order is important:

```
1. Observability (if enabled) - instruments all requests
2. Security Headers (if enabled) - adds headers before CORS processing
3. CORS - handles cross-origin requests
4. Tenant Resolution - extracts tenant context
```

Security headers should be added before CORS to ensure headers are present even on CORS preflight responses.

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-01 | Required | Uses `SecurityHeadersMiddleware` and `SecurityHeadersConfig` |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-06 | Reference | Security checklist references configuration options |
| P2-07 | Reference | ADR documents configuration architecture |
| P6-01 | Reference | CLAUDE.md update includes security headers section |

---

## Success Criteria

### Functional Requirements

- [ ] All security header settings added to `Settings` class in config.py
- [ ] Settings use appropriate defaults (secure by default)
- [ ] All settings can be overridden via environment variables
- [ ] `.env.example` updated with all security settings and comments
- [ ] `main.py` conditionally registers middleware based on cookiecutter variable
- [ ] `main.py` respects `SECURITY_HEADERS_ENABLED` runtime toggle
- [ ] Cookiecutter variable `include_security_headers` added to cookiecutter.json
- [ ] CSP `connect-src` automatically includes `FRONTEND_URL`

### Non-Functional Requirements

- [ ] Settings follow existing config.py patterns (naming, typing, defaults)
- [ ] Environment variables use consistent naming convention (UPPER_SNAKE_CASE)
- [ ] Comments explain purpose and valid values for each setting
- [ ] No breaking changes to existing configuration

### Validation Steps

1. Generate project with `include_security_headers=yes`
   - Verify security middleware registered in main.py
   - Verify config.py has all security settings
   - Start backend and verify headers present

2. Generate project with `include_security_headers=no`
   - Verify security middleware code not present
   - Backend should start without security headers

3. Test runtime toggle
   - Set `SECURITY_HEADERS_ENABLED=false`
   - Verify headers not added to responses

4. Test configuration override
   - Set `X_FRAME_OPTIONS=SAMEORIGIN`
   - Verify response uses SAMEORIGIN instead of DENY

---

## Integration Points

### Configuration Flow

```
Environment Variables
        |
        v
    Settings (config.py)
        |
        v
SecurityHeadersConfig (built in main.py)
        |
        v
SecurityHeadersMiddleware (applied to app)
        |
        v
    HTTP Responses (with headers)
```

### CSP and Frontend URL

The `connect-src` directive must include the frontend URL for API calls:

```python
# Automatic FRONTEND_URL inclusion
connect_src = settings.CSP_CONNECT_SRC
if settings.FRONTEND_URL and settings.FRONTEND_URL not in connect_src:
    connect_src = f"{connect_src} {settings.FRONTEND_URL}"
```

This ensures the frontend can make API requests without CSP violations.

### Cookiecutter Conditional Pattern

Following the established pattern from ADR-017 (observability):

```jinja2
{% if cookiecutter.include_security_headers == "yes" %}
# Security headers code here
{% endif %}
```

This pattern is used in:
- `main.py` for middleware registration
- Template structure for middleware file inclusion

---

## Monitoring and Observability

### Logging

Configuration loading is logged at startup:

```python
# In lifespan or startup
if settings.SECURITY_HEADERS_ENABLED:
    print(f"Security headers enabled: CSP={settings.CSP_ENABLED}, HSTS={settings.HSTS_ENABLED}")
else:
    print("Security headers disabled via SECURITY_HEADERS_ENABLED=false")
```

### Configuration Validation

Consider adding startup validation:

```python
@field_validator("X_FRAME_OPTIONS")
@classmethod
def validate_x_frame_options(cls, v: str) -> str:
    """Validate X-Frame-Options value."""
    valid = ["DENY", "SAMEORIGIN", ""]
    if v and v not in valid:
        raise ValueError(f"X_FRAME_OPTIONS must be one of: {valid}")
    return v
```

---

## Infrastructure Needs

### No Additional Infrastructure Required

This task modifies existing configuration files only.

### Environment Considerations

| Environment | Recommended Settings |
|-------------|---------------------|
| Development | `SECURITY_HEADERS_ENABLED=true`, `HSTS_ENABLED=false` |
| Staging | `SECURITY_HEADERS_ENABLED=true`, `HSTS_ENABLED=true`, `HSTS_MAX_AGE=86400` |
| Production | `SECURITY_HEADERS_ENABLED=true`, `HSTS_ENABLED=true`, `HSTS_MAX_AGE=31536000` |

---

## Implementation Notes

### Setting Naming Convention

All security settings use the pattern:
- `SECURITY_*` for master toggles
- `CSP_*` for Content-Security-Policy directives
- `HSTS_*` for Strict-Transport-Security options
- `X_*` for X-prefixed headers

### Empty String Handling

Empty strings disable individual headers:

```python
X_FRAME_OPTIONS: str = "DENY"  # Set to "" to disable
```

In main.py:
```python
x_frame_options=settings.X_FRAME_OPTIONS or None,  # Converts "" to None
```

### CSP Directive Quoting

CSP directive values include their quotes:

```bash
CSP_DEFAULT_SRC='self'          # Includes the single quotes
CSP_SCRIPT_SRC='self' 'unsafe-inline'  # Multiple values, each quoted
```

This matches the CSP specification where keyword values must be quoted.

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-SEC-006 | Security headers configurable via environment | All settings in config.py |

### Related Tasks

- P2-01: SecurityHeadersMiddleware implementation
- P2-07: ADR-020 Security Headers documentation

### External Resources

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [FastAPI Configuration Best Practices](https://fastapi.tiangolo.com/advanced/settings/)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)
