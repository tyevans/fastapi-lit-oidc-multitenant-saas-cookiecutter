# P2-01: Implement Security Headers Middleware

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P2-01 |
| **Task Title** | Implement Security Headers Middleware |
| **Domain** | Backend |
| **Complexity** | M (Medium) |
| **Estimated Effort** | 2 days |
| **Priority** | Must Have |
| **Dependencies** | None |
| **FRD Requirements** | FR-SEC-001, FR-SEC-002, FR-SEC-003, FR-SEC-004, FR-SEC-005, FR-SEC-006 |

---

## Scope

### What This Task Includes

1. Create `SecurityHeadersMiddleware` class following the existing `TenantResolutionMiddleware` pattern
2. Implement Content-Security-Policy (CSP) header with configurable directives
3. Implement Strict-Transport-Security (HSTS) header (conditional on HTTPS)
4. Implement X-Frame-Options header (DENY or configurable)
5. Implement X-Content-Type-Options header (nosniff)
6. Implement Referrer-Policy header
7. Add cookiecutter conditional for optional security headers feature
8. Write unit tests for the middleware

### What This Task Excludes

- Security configuration in config.py (P2-02)
- Frontend nginx security headers (already exist partially)
- CSP reporting endpoint implementation (future enhancement)
- Permissions-Policy header (future enhancement)
- Integration with main.py (handled by config.py, P2-02)

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
backend/
  app/
    middleware/
      security.py           # SecurityHeadersMiddleware implementation
  tests/
    unit/
      middleware/
        test_security.py    # Unit tests for security middleware
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/app/middleware/tenant.py` | Pattern reference for middleware implementation |
| `template/{{cookiecutter.project_slug}}/backend/app/core/config.py` | Configuration patterns to follow |
| `template/{{cookiecutter.project_slug}}/backend/app/main.py` | Middleware registration pattern |
| `template/{{cookiecutter.project_slug}}/frontend/nginx.conf` | Existing frontend headers (X-Frame-Options, X-Content-Type-Options) |

---

## Technical Specification

### Middleware Architecture

```python
"""
Security Headers Middleware for FastAPI.

Adds security-related HTTP headers to all responses to mitigate common
web vulnerabilities. Headers are configurable via environment variables.

Key Features:
- Content-Security-Policy (CSP) for XSS mitigation
- Strict-Transport-Security (HSTS) for transport security
- X-Frame-Options for clickjacking protection
- X-Content-Type-Options for MIME sniffing prevention
- Referrer-Policy for privacy protection

References:
- OWASP Secure Headers: https://owasp.org/www-project-secure-headers/
- MDN Security Headers: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers
"""

import logging
from dataclasses import dataclass
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


@dataclass
class SecurityHeadersConfig:
    """
    Configuration for security headers.

    All values are optional and can be disabled by setting to None.
    """
    # Content-Security-Policy
    csp_enabled: bool = True
    csp_default_src: str = "'self'"
    csp_script_src: str = "'self' 'unsafe-inline'"  # Required for Lit components
    csp_style_src: str = "'self' 'unsafe-inline'"   # Required for Lit components
    csp_img_src: str = "'self' data: https:"
    csp_font_src: str = "'self'"
    csp_connect_src: str = "'self'"
    csp_frame_ancestors: str = "'none'"
    csp_report_uri: Optional[str] = None

    # Strict-Transport-Security (HSTS)
    hsts_enabled: bool = True
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False

    # X-Frame-Options
    x_frame_options: str = "DENY"  # DENY, SAMEORIGIN, or None to disable

    # X-Content-Type-Options
    x_content_type_options: str = "nosniff"

    # Referrer-Policy
    referrer_policy: str = "strict-origin-when-cross-origin"

    # X-XSS-Protection (legacy, but still useful for older browsers)
    x_xss_protection: str = "1; mode=block"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all HTTP responses.

    This middleware adds a comprehensive set of security headers designed to
    mitigate common web vulnerabilities including XSS, clickjacking, and
    MIME sniffing attacks.

    Example:
        >>> from app.middleware.security import SecurityHeadersMiddleware, SecurityHeadersConfig
        >>>
        >>> config = SecurityHeadersConfig(
        ...     csp_script_src="'self' 'unsafe-inline' https://cdn.example.com",
        ...     x_frame_options="SAMEORIGIN",
        ... )
        >>> app.add_middleware(SecurityHeadersMiddleware, config=config)

    Note:
        HSTS header is only added for HTTPS requests to avoid browser issues
        when accessing the site over HTTP during development.
    """

    def __init__(self, app, config: Optional[SecurityHeadersConfig] = None):
        """
        Initialize the security headers middleware.

        Args:
            app: The ASGI application
            config: Security headers configuration. If None, uses defaults.
        """
        super().__init__(app)
        self.config = config or SecurityHeadersConfig()
        self._csp_header = self._build_csp_header()
        self._hsts_header = self._build_hsts_header()
        logger.info("SecurityHeadersMiddleware initialized")

    def _build_csp_header(self) -> Optional[str]:
        """Build the Content-Security-Policy header value."""
        if not self.config.csp_enabled:
            return None

        directives = []

        if self.config.csp_default_src:
            directives.append(f"default-src {self.config.csp_default_src}")
        if self.config.csp_script_src:
            directives.append(f"script-src {self.config.csp_script_src}")
        if self.config.csp_style_src:
            directives.append(f"style-src {self.config.csp_style_src}")
        if self.config.csp_img_src:
            directives.append(f"img-src {self.config.csp_img_src}")
        if self.config.csp_font_src:
            directives.append(f"font-src {self.config.csp_font_src}")
        if self.config.csp_connect_src:
            directives.append(f"connect-src {self.config.csp_connect_src}")
        if self.config.csp_frame_ancestors:
            directives.append(f"frame-ancestors {self.config.csp_frame_ancestors}")
        if self.config.csp_report_uri:
            directives.append(f"report-uri {self.config.csp_report_uri}")

        return "; ".join(directives)

    def _build_hsts_header(self) -> Optional[str]:
        """Build the Strict-Transport-Security header value."""
        if not self.config.hsts_enabled:
            return None

        parts = [f"max-age={self.config.hsts_max_age}"]

        if self.config.hsts_include_subdomains:
            parts.append("includeSubDomains")
        if self.config.hsts_preload:
            parts.append("preload")

        return "; ".join(parts)

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or handler in chain

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # Content-Security-Policy
        if self._csp_header:
            response.headers["Content-Security-Policy"] = self._csp_header

        # Strict-Transport-Security (only for HTTPS)
        if self._hsts_header and self._is_https_request(request):
            response.headers["Strict-Transport-Security"] = self._hsts_header

        # X-Frame-Options
        if self.config.x_frame_options:
            response.headers["X-Frame-Options"] = self.config.x_frame_options

        # X-Content-Type-Options
        if self.config.x_content_type_options:
            response.headers["X-Content-Type-Options"] = self.config.x_content_type_options

        # Referrer-Policy
        if self.config.referrer_policy:
            response.headers["Referrer-Policy"] = self.config.referrer_policy

        # X-XSS-Protection (legacy)
        if self.config.x_xss_protection:
            response.headers["X-XSS-Protection"] = self.config.x_xss_protection

        return response

    def _is_https_request(self, request: Request) -> bool:
        """
        Determine if request was made over HTTPS.

        Checks both the URL scheme and common proxy headers.

        Args:
            request: HTTP request

        Returns:
            True if request is HTTPS, False otherwise
        """
        # Check URL scheme
        if request.url.scheme == "https":
            return True

        # Check X-Forwarded-Proto header (set by reverse proxy)
        forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
        if forwarded_proto.lower() == "https":
            return True

        return False
```

### CSP Configuration for Lit Components

The default CSP configuration accounts for Lit component requirements:

| Directive | Value | Reason |
|-----------|-------|--------|
| `script-src` | `'self' 'unsafe-inline'` | Lit uses inline scripts for component rendering |
| `style-src` | `'self' 'unsafe-inline'` | Lit uses inline styles for shadow DOM styling |

**Security Note:** `'unsafe-inline'` is required for Lit components. Consider using CSP nonces in future iterations for stricter security.

### Test Specification

```python
"""Unit tests for SecurityHeadersMiddleware."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from app.middleware.security import SecurityHeadersMiddleware, SecurityHeadersConfig


@pytest.fixture
def app_with_security_headers():
    """Create a FastAPI app with security headers middleware."""
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    return app


@pytest.fixture
def client(app_with_security_headers):
    """Create test client."""
    return TestClient(app_with_security_headers)


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware."""

    def test_adds_csp_header(self, client):
        """CSP header should be present in response."""
        response = client.get("/test")
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    def test_adds_x_frame_options_header(self, client):
        """X-Frame-Options header should be DENY by default."""
        response = client.get("/test")
        assert response.headers["X-Frame-Options"] == "DENY"

    def test_adds_x_content_type_options_header(self, client):
        """X-Content-Type-Options header should be nosniff."""
        response = client.get("/test")
        assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_adds_referrer_policy_header(self, client):
        """Referrer-Policy header should be present."""
        response = client.get("/test")
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"

    def test_hsts_not_added_for_http(self, client):
        """HSTS should not be added for HTTP requests."""
        response = client.get("/test")
        # TestClient uses HTTP by default
        assert "Strict-Transport-Security" not in response.headers

    def test_hsts_added_for_https_forwarded_proto(self, client):
        """HSTS should be added when X-Forwarded-Proto is https."""
        response = client.get("/test", headers={"X-Forwarded-Proto": "https"})
        assert "Strict-Transport-Security" in response.headers
        assert "max-age=31536000" in response.headers["Strict-Transport-Security"]

    def test_custom_config(self):
        """Custom configuration should override defaults."""
        app = FastAPI()
        config = SecurityHeadersConfig(
            x_frame_options="SAMEORIGIN",
            hsts_max_age=86400,
        )
        app.add_middleware(SecurityHeadersMiddleware, config=config)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")
        assert response.headers["X-Frame-Options"] == "SAMEORIGIN"

    def test_csp_can_be_disabled(self):
        """CSP can be disabled via configuration."""
        app = FastAPI()
        config = SecurityHeadersConfig(csp_enabled=False)
        app.add_middleware(SecurityHeadersMiddleware, config=config)

        @app.get("/test")
        async def test_endpoint():
            return {"status": "ok"}

        client = TestClient(app)
        response = client.get("/test")
        assert "Content-Security-Policy" not in response.headers
```

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| None | - | This is a foundational task |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-02 | Required | Configuration integration in config.py and main.py |
| P2-06 | Reference | Security checklist references middleware implementation |
| P2-07 | Reference | ADR-020 documents security headers architecture |

---

## Success Criteria

### Functional Requirements

- [ ] `SecurityHeadersMiddleware` class created following existing middleware patterns
- [ ] Content-Security-Policy header added to all responses
- [ ] CSP directives compatible with Lit components (unsafe-inline for script/style)
- [ ] Strict-Transport-Security header added only for HTTPS requests
- [ ] HSTS detects HTTPS via URL scheme and X-Forwarded-Proto header
- [ ] X-Frame-Options header set to DENY by default
- [ ] X-Content-Type-Options header set to nosniff
- [ ] Referrer-Policy header set to strict-origin-when-cross-origin
- [ ] All headers configurable via `SecurityHeadersConfig` dataclass
- [ ] Headers can be individually disabled by setting to None/False

### Non-Functional Requirements

- [ ] Middleware adds less than 1ms latency to request processing
- [ ] Headers pre-computed at middleware initialization (not per-request)
- [ ] Comprehensive logging for debugging and auditing
- [ ] Unit test coverage > 90% for middleware module
- [ ] Code follows existing project patterns and conventions

### Validation Steps

1. Run backend with middleware enabled
   - Make request to any endpoint
   - Verify all expected headers present in response
   - Verify CSP allows Lit components to function

2. Test HTTPS detection
   - Request without X-Forwarded-Proto: No HSTS header
   - Request with X-Forwarded-Proto: https: HSTS header present

3. Test configuration
   - Override individual settings
   - Disable specific headers
   - Verify changes reflected in responses

4. Security validation
   - Use browser DevTools to verify headers
   - Test CSP doesn't break frontend rendering
   - Verify X-Frame-Options prevents framing

---

## Integration Points

### Middleware Registration Order

The security headers middleware should be added early in the middleware chain:

```python
# main.py (handled by P2-02)
{% if cookiecutter.include_security_headers == "yes" %}
from app.middleware.security import SecurityHeadersMiddleware, SecurityHeadersConfig
from app.core.config import settings

# Security Headers Middleware
# Runs early to ensure all responses have security headers
security_config = SecurityHeadersConfig(
    csp_connect_src=f"'self' {settings.FRONTEND_URL}",
    # Additional configuration from settings...
)
app.add_middleware(SecurityHeadersMiddleware, config=security_config)
{% endif %}

# CORS middleware (existing)
app.add_middleware(CORSMiddleware, ...)

# Tenant middleware (existing)
app.add_middleware(TenantResolutionMiddleware)
```

### Configuration from Environment

P2-02 will add these settings to `config.py`:

```python
# Security Headers Configuration
SECURITY_HEADERS_ENABLED: bool = True
CSP_DEFAULT_SRC: str = "'self'"
CSP_SCRIPT_SRC: str = "'self' 'unsafe-inline'"
CSP_STYLE_SRC: str = "'self' 'unsafe-inline'"
HSTS_MAX_AGE: int = 31536000
X_FRAME_OPTIONS: str = "DENY"
```

### Cookiecutter Conditional

Add new cookiecutter variable (follows ADR-017 pattern):

```json
{
  "include_security_headers": ["yes", "no"]
}
```

Default: "yes" (security headers are important for production)

---

## Monitoring and Observability

### Logging

The middleware logs at INFO level during initialization and DEBUG level for per-request processing:

```python
logger.info("SecurityHeadersMiddleware initialized")
logger.debug(f"Security headers added to response for {request.url.path}")
```

### Metrics (Future Enhancement)

Consider adding prometheus metrics in future:
- `security_headers_applied_total` - Counter of responses with headers
- `csp_violations_total` - Counter of CSP violation reports (requires reporting endpoint)

---

## Infrastructure Needs

### No Additional Infrastructure Required

This task is purely application-level code with no infrastructure dependencies.

### Development Requirements

- Python 3.11+ (existing requirement)
- pytest for testing (existing)
- FastAPI/Starlette (existing)

---

## Implementation Notes

### Header Caching

CSP and HSTS headers are built once during middleware initialization:

```python
def __init__(self, app, config=None):
    super().__init__(app)
    self.config = config or SecurityHeadersConfig()
    self._csp_header = self._build_csp_header()  # Built once
    self._hsts_header = self._build_hsts_header()  # Built once
```

This ensures minimal per-request overhead.

### Lit Component Compatibility

The default CSP must allow Lit components to work:

1. **Inline scripts:** Lit renders components using inline JavaScript
2. **Inline styles:** Shadow DOM styling requires inline styles
3. **Connection to API:** `connect-src` must include backend API URL

Testing with frontend is critical before finalizing CSP policy.

### HSTS Preload Considerations

HSTS preload (`preload` directive) is disabled by default because:
1. Requires HTTPS to be available on all subdomains
2. Cannot be easily undone once submitted to preload list
3. Should be explicitly enabled after thorough testing

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-SEC-001 | Backend shall add Content-Security-Policy header | `_build_csp_header()` method |
| FR-SEC-002 | Backend shall add HSTS when HTTPS detected | `_is_https_request()` check |
| FR-SEC-003 | Backend shall add X-Frame-Options set to DENY | `config.x_frame_options` |
| FR-SEC-004 | Backend shall add X-Content-Type-Options nosniff | `config.x_content_type_options` |
| FR-SEC-005 | Backend shall add Referrer-Policy | `config.referrer_policy` |
| FR-SEC-006 | Security headers configurable via environment | `SecurityHeadersConfig` dataclass |

### Related ADRs

- ADR-017: Optional Observability Stack (cookiecutter conditional pattern)
- ADR-020: Security Headers (to be written in P2-07)

### External Resources

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
- [Lit and CSP](https://lit.dev/docs/security/trusted-types/)
