# P3-03: Implement Optional Sentry Integration

## Task Identifier
**ID:** P3-03
**Phase:** 3 - Operational Readiness
**Domain:** Backend
**Complexity:** L (Large)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| None | - | - | Independent task - can start immediately |

## Scope

### In Scope
- Create `sentry.py` module in `backend/app/` directory
- Add Sentry configuration settings to `config.py`
- Add `init_sentry()` function with FastAPI and SQLAlchemy integrations
- Implement `before_send` hook for PII filtering
- Add tenant and user context attachment to Sentry events
- Update `main.py` to conditionally initialize Sentry
- Add `sentry-sdk[fastapi]` to backend requirements
- Create tests for Sentry initialization logic

### Out of Scope
- Cookiecutter conditionals (P3-04)
- Frontend Sentry integration
- Sentry release tracking in CI/CD (P3-04, P1-02)
- ADR documentation (P3-11)
- Alertmanager or PagerDuty notification integration

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/backend/app/sentry.py
template/{{cookiecutter.project_slug}}/backend/tests/unit/test_sentry.py
```

### Files to Modify
```
template/{{cookiecutter.project_slug}}/backend/app/core/config.py
template/{{cookiecutter.project_slug}}/backend/app/main.py
template/{{cookiecutter.project_slug}}/backend/requirements.txt
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/backend/app/observability.py  (pattern reference)
template/{{cookiecutter.project_slug}}/backend/app/middleware/tenant.py  (tenant context)
```

## Implementation Details

### 1. Sentry Module (`backend/app/sentry.py`)

```python
"""
Sentry error tracking integration for {{ cookiecutter.project_name }}.

This module provides optional Sentry SDK integration for production
error tracking. It follows a fail-open pattern where the application
continues functioning normally if Sentry is misconfigured or unavailable.

Features:
- Automatic exception capture with stack traces
- Tenant and user context attachment (multi-tenancy aware)
- PII filtering via before_send hook
- Release tracking for deployment correlation
- FastAPI and SQLAlchemy integrations

Environment Variables:
    SENTRY_DSN: Sentry Data Source Name (required to enable)
    SENTRY_ENVIRONMENT: Environment tag (default: "development")
    SENTRY_TRACES_SAMPLE_RATE: Trace sampling rate (default: 0.1)
    SENTRY_RELEASE: Release version (default: APP_VERSION from settings)

Usage:
    from app.sentry import init_sentry
    from app.core.config import settings

    init_sentry(settings)

Architecture Notes:
    - Follows fail-open pattern: If Sentry DSN is not configured or invalid,
      the application starts normally without error tracking
    - Integrates with existing tenant context middleware for multi-tenant
      error correlation
    - PII filtering removes sensitive data before transmission
"""

import logging
from typing import Any, Optional

from app.core.config import Settings

logger = logging.getLogger(__name__)

# Sentry SDK imports wrapped in try-except for graceful degradation
# when sentry-sdk is not installed
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.asyncio import AsyncioIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    logger.warning("sentry-sdk not installed - error tracking disabled")


# PII fields to filter from Sentry events
PII_FIELDS = frozenset({
    "password",
    "passwd",
    "secret",
    "api_key",
    "apikey",
    "access_token",
    "auth_token",
    "credentials",
    "credit_card",
    "card_number",
    "ssn",
    "social_security",
})


def _before_send(event: dict[str, Any], hint: dict[str, Any]) -> Optional[dict[str, Any]]:
    """
    Sentry before_send hook for PII filtering and event enrichment.

    This function runs before every event is sent to Sentry, allowing:
    - Filtering of sensitive data (passwords, tokens, etc.)
    - Event modification or enrichment
    - Conditional event dropping (return None)

    Args:
        event: The Sentry event dictionary
        hint: Additional context (exception info, etc.)

    Returns:
        Modified event dict, or None to drop the event
    """
    # Filter request body data for PII
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            for key in list(data.keys()):
                if key.lower() in PII_FIELDS:
                    data[key] = "[Filtered]"

    # Filter headers for sensitive tokens
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        if isinstance(headers, dict):
            for key in list(headers.keys()):
                if key.lower() in {"authorization", "x-api-key", "cookie"}:
                    headers[key] = "[Filtered]"

    # Filter breadcrumb data
    if "breadcrumbs" in event:
        for breadcrumb in event.get("breadcrumbs", {}).get("values", []):
            if "data" in breadcrumb and isinstance(breadcrumb["data"], dict):
                for key in list(breadcrumb["data"].keys()):
                    if key.lower() in PII_FIELDS:
                        breadcrumb["data"][key] = "[Filtered]"

    return event


def init_sentry(settings: Settings) -> bool:
    """
    Initialize Sentry SDK with FastAPI integration.

    This function configures the Sentry SDK for error tracking in production.
    It follows a fail-open pattern - if Sentry DSN is not configured or
    initialization fails, the application continues without error tracking.

    Args:
        settings: Application settings instance with Sentry configuration

    Returns:
        True if Sentry was successfully initialized, False otherwise

    Configuration:
        The following settings control Sentry behavior:
        - SENTRY_DSN: Required - Sentry project DSN
        - SENTRY_ENVIRONMENT: Environment tag (staging, production)
        - SENTRY_TRACES_SAMPLE_RATE: Performance monitoring sample rate
        - APP_VERSION: Used as release version for error correlation

    Example:
        from app.sentry import init_sentry
        from app.core.config import settings

        if init_sentry(settings):
            print("Sentry error tracking enabled")
    """
    # Check if sentry-sdk is available
    if not SENTRY_AVAILABLE:
        logger.info("Sentry SDK not installed - skipping initialization")
        return False

    # Check if Sentry is configured
    if not settings.SENTRY_DSN:
        logger.info("SENTRY_DSN not configured - error tracking disabled")
        return False

    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.SENTRY_ENVIRONMENT,
            release=settings.SENTRY_RELEASE or settings.APP_VERSION,

            # Enable performance monitoring (traces)
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,

            # Profile configuration (if available in plan)
            profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,

            # Integrations
            integrations=[
                # FastAPI integration with URL-based transaction naming
                # Groups errors by endpoint pattern rather than full URL
                FastApiIntegration(transaction_style="url"),

                # SQLAlchemy integration for database query tracking
                SqlalchemyIntegration(),

                # Asyncio integration for proper async context tracking
                AsyncioIntegration(),

                # Logging integration - captures log messages as breadcrumbs
                LoggingIntegration(
                    level=logging.INFO,      # Capture INFO and above as breadcrumbs
                    event_level=logging.ERROR  # Create events for ERROR and above
                ),
            ],

            # PII filtering hook
            before_send=_before_send,

            # Send default PII (filtered by before_send)
            send_default_pii=False,

            # Attach stack traces to captured messages
            attach_stacktrace=True,

            # Max breadcrumbs to capture
            max_breadcrumbs=50,
        )

        logger.info(
            f"Sentry initialized - DSN: {settings.SENTRY_DSN[:20]}..., "
            f"environment: {settings.SENTRY_ENVIRONMENT}, "
            f"release: {settings.SENTRY_RELEASE or settings.APP_VERSION}"
        )
        return True

    except Exception as e:
        # Fail-open: Log error but don't crash the application
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def set_user_context(user_id: str, tenant_id: str, email: Optional[str] = None) -> None:
    """
    Set Sentry user context for error correlation.

    This function should be called after successful authentication to
    attach user information to all subsequent Sentry events. It enables
    filtering and searching errors by user or tenant in the Sentry UI.

    Args:
        user_id: Unique user identifier (from JWT sub claim)
        tenant_id: Tenant identifier (from JWT tenant_id claim)
        email: Optional user email (will be hashed in Sentry)

    Example:
        from app.sentry import set_user_context

        # In authentication dependency or middleware
        set_user_context(
            user_id=token_data.sub,
            tenant_id=token_data.tenant_id,
            email=token_data.email
        )
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.set_user({
            "id": user_id,
            "tenant_id": tenant_id,
            "email": email,
        })

        # Also set tenant as a tag for easier filtering
        sentry_sdk.set_tag("tenant_id", tenant_id)

    except Exception as e:
        logger.debug(f"Failed to set Sentry user context: {e}")


def clear_user_context() -> None:
    """
    Clear Sentry user context (typically on logout or request completion).
    """
    if not SENTRY_AVAILABLE:
        return

    try:
        sentry_sdk.set_user(None)
    except Exception:
        pass


def capture_message(message: str, level: str = "info", **extra: Any) -> Optional[str]:
    """
    Manually capture a message to Sentry.

    Args:
        message: The message to capture
        level: Severity level (debug, info, warning, error, fatal)
        **extra: Additional context data

    Returns:
        Sentry event ID if captured, None otherwise
    """
    if not SENTRY_AVAILABLE:
        return None

    try:
        with sentry_sdk.push_scope() as scope:
            for key, value in extra.items():
                scope.set_extra(key, value)
            return sentry_sdk.capture_message(message, level=level)
    except Exception:
        return None
```

### 2. Configuration Updates (`backend/app/core/config.py`)

Add Sentry configuration settings:

```python
class Settings(BaseSettings):
    # ... existing settings ...

    # Sentry Configuration (Optional)
    SENTRY_DSN: str = ""  # Empty string disables Sentry
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_RELEASE: str = ""  # Defaults to APP_VERSION if empty
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of requests traced
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1  # 10% of traces profiled
```

### 3. Main.py Integration

```python
# Add after observability setup in main.py
{% if cookiecutter.include_sentry == "yes" %}
from app.sentry import init_sentry

# Initialize Sentry error tracking (fail-open pattern)
sentry_enabled = init_sentry(settings)
if sentry_enabled:
    print("Sentry error tracking: enabled")
{% endif %}
```

### 4. Requirements Update

Add to `backend/requirements.txt`:

```
# Error Tracking (optional)
sentry-sdk[fastapi]>=2.0.0,<3.0.0
```

### 5. Authentication Integration

Update auth dependency to set Sentry user context:

```python
# In backend/app/api/dependencies/auth.py

{% if cookiecutter.include_sentry == "yes" %}
from app.sentry import set_user_context
{% endif %}

async def get_current_user(...) -> TokenPayload:
    # ... existing validation logic ...

    {% if cookiecutter.include_sentry == "yes" %}
    # Set Sentry user context for error correlation
    set_user_context(
        user_id=payload.sub,
        tenant_id=payload.tenant_id,
        email=getattr(payload, 'email', None)
    )
    {% endif %}

    return payload
```

## Success Criteria

### Functional Requirements
- [ ] FR-OPS-001: Sentry SDK integration in backend (optional via DSN)
- [ ] FR-OPS-002: Unhandled exceptions captured with stack traces
- [ ] FR-OPS-003: tenant_id and user_id attached to error context
- [ ] Fail-open pattern: Application starts without Sentry DSN configured

### Verification Steps
1. **Without Sentry DSN:**
   ```bash
   # Start backend without SENTRY_DSN
   docker compose up backend
   # Verify: Application starts normally
   # Verify: Logs show "SENTRY_DSN not configured"
   ```

2. **With Sentry DSN:**
   ```bash
   # Set SENTRY_DSN in .env
   SENTRY_DSN=https://xxx@sentry.io/xxx
   docker compose up backend
   # Verify: Logs show "Sentry initialized"
   ```

3. **Error Capture:**
   ```bash
   # Trigger an error
   curl http://localhost:8000/api/v1/test-error
   # Verify: Error appears in Sentry dashboard
   # Verify: tenant_id and user_id are attached
   ```

4. **PII Filtering:**
   ```python
   # Verify password fields are filtered
   # Check Sentry event does not contain raw credentials
   ```

### Quality Gates
- [ ] Unit tests pass for sentry.py module
- [ ] Integration test verifies init_sentry() returns correct status
- [ ] No application crash when SENTRY_DSN is invalid
- [ ] No PII leakage in captured events (verified via test)

## Integration Points

### Upstream Dependencies
None - this task is independent.

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P3-04 | `include_sentry` cookiecutter variable | Wraps sentry.py in conditional |
| P3-11 | ADR-024 documents Sentry integration | References this implementation |
| P1-02 | CI/CD sets SENTRY_RELEASE | Build workflow sets release version |

### Integration Contract
```python
# Contract: sentry.py module interface

def init_sentry(settings: Settings) -> bool:
    """
    Initialize Sentry SDK.

    Args:
        settings: Application settings with SENTRY_* configuration

    Returns:
        True if Sentry was initialized, False otherwise
    """

def set_user_context(user_id: str, tenant_id: str, email: Optional[str] = None) -> None:
    """
    Set user context for error correlation.

    Called from auth dependencies after successful authentication.
    """

def clear_user_context() -> None:
    """Clear user context (logout/request end)."""

def capture_message(message: str, level: str = "info", **extra) -> Optional[str]:
    """Manually capture a message to Sentry."""
```

## Monitoring and Observability

### Sentry Dashboard Metrics
- Error rate trends
- Error grouping by tenant_id
- Release correlation
- User impact analysis

### Logging
- INFO: "Sentry initialized" on successful init
- INFO: "SENTRY_DSN not configured" when disabled
- ERROR: "Failed to initialize Sentry: {error}" on init failure

### Health Monitoring
The Sentry integration follows the fail-open pattern:
- No health checks depend on Sentry availability
- Application continues operating if Sentry is unavailable
- Silent degradation (no user-facing errors)

## Infrastructure Needs

### Environment Variables
Add to `.env.example`:
```bash
# Sentry Configuration (optional)
# Get your DSN from https://sentry.io/settings/{org}/projects/{project}/keys/
SENTRY_DSN=
SENTRY_ENVIRONMENT=development
# SENTRY_RELEASE is auto-set from APP_VERSION if empty
```

### Docker Compose Changes
None required - Sentry is a SaaS service.

### Network Requirements
- Outbound HTTPS to sentry.io (or self-hosted Sentry instance)
- No inbound connections required

## Testing Strategy

### Unit Tests (`backend/tests/unit/test_sentry.py`)
```python
import pytest
from unittest.mock import patch, MagicMock

from app.sentry import init_sentry, set_user_context, _before_send
from app.core.config import Settings


class TestBeforeSend:
    """Tests for PII filtering hook."""

    def test_filters_password_from_request_data(self):
        event = {
            "request": {
                "data": {"username": "alice", "password": "secret123"}
            }
        }
        result = _before_send(event, {})
        assert result["request"]["data"]["password"] == "[Filtered]"
        assert result["request"]["data"]["username"] == "alice"

    def test_filters_authorization_header(self):
        event = {
            "request": {
                "headers": {"Authorization": "Bearer token123", "Content-Type": "application/json"}
            }
        }
        result = _before_send(event, {})
        assert result["request"]["headers"]["Authorization"] == "[Filtered]"
        assert result["request"]["headers"]["Content-Type"] == "application/json"


class TestInitSentry:
    """Tests for Sentry initialization."""

    def test_returns_false_when_dsn_empty(self):
        settings = MagicMock(spec=Settings)
        settings.SENTRY_DSN = ""

        result = init_sentry(settings)
        assert result is False

    @patch("app.sentry.sentry_sdk")
    def test_returns_true_on_successful_init(self, mock_sentry):
        settings = MagicMock(spec=Settings)
        settings.SENTRY_DSN = "https://xxx@sentry.io/123"
        settings.SENTRY_ENVIRONMENT = "test"
        settings.SENTRY_RELEASE = "1.0.0"
        settings.SENTRY_TRACES_SAMPLE_RATE = 0.1
        settings.SENTRY_PROFILES_SAMPLE_RATE = 0.1
        settings.APP_VERSION = "1.0.0"

        result = init_sentry(settings)

        assert result is True
        mock_sentry.init.assert_called_once()


class TestSetUserContext:
    """Tests for user context setting."""

    @patch("app.sentry.sentry_sdk")
    def test_sets_user_and_tenant_tag(self, mock_sentry):
        set_user_context(
            user_id="user-123",
            tenant_id="tenant-456",
            email="user@example.com"
        )

        mock_sentry.set_user.assert_called_once_with({
            "id": "user-123",
            "tenant_id": "tenant-456",
            "email": "user@example.com",
        })
        mock_sentry.set_tag.assert_called_once_with("tenant_id", "tenant-456")
```

## Estimated Effort

**Size:** L (Large)
**Time:** 2-3 days
**Justification:**
- New module creation with comprehensive functionality
- Integration with multiple existing components (config, main, auth)
- PII filtering requires careful implementation and testing
- Multi-tenant context integration needs thorough testing
- Documentation and test coverage requirements

## Notes

### Design Decisions

**1. Fail-Open Pattern:**
Sentry integration follows the same fail-open pattern as the observability module. If Sentry is unavailable or misconfigured, the application continues operating normally.

**2. Optional Dependency:**
When `include_sentry == "no"`, the sentry-sdk package should not be included in requirements.txt. This is handled by P3-04 (cookiecutter conditionals).

**3. PII Filtering:**
The before_send hook filters common PII fields. Additional fields can be added based on application-specific requirements.

**4. Integration with Existing Observability:**
Sentry complements (not replaces) the existing observability stack:
- Prometheus: Metrics and alerting
- Loki: Log aggregation
- Tempo: Distributed tracing
- Sentry: Error tracking and user impact analysis

### Related Requirements
- FR-OPS-001: Template shall include optional Sentry SDK integration in backend
- FR-OPS-002: Sentry integration shall capture unhandled exceptions with stack traces
- FR-OPS-003: Sentry integration shall attach tenant_id and user_id context to errors
- FR-OPS-004: Sentry release tracking shall be configured in CI/CD pipeline (P3-04)

### Security Considerations
- SENTRY_DSN should be treated as a secret (contains auth token)
- PII filtering is critical for compliance (GDPR, etc.)
- Consider self-hosted Sentry for sensitive data environments
