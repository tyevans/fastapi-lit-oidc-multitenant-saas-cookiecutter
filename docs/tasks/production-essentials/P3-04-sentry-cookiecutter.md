# P3-04: Add Sentry Cookiecutter Conditional

## Task Identifier
**ID:** P3-04
**Phase:** 3 - Operational Readiness
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P3-03 | Hard | Documented | Sentry module must exist before adding conditionals |

## Scope

### In Scope
- Add `include_sentry` variable to `cookiecutter.json` (default: "no")
- Add Jinja2 conditionals around Sentry-related code in backend
- Conditionally include `sentry-sdk[fastapi]` in `requirements.txt`
- Update `.env.example` with Sentry configuration (conditional)
- Add Sentry release tracking to GitHub Actions build workflow (optional)
- Update CLAUDE.md with Sentry documentation (conditional)
- Add post-generation hook validation for Sentry configuration

### Out of Scope
- Sentry SDK implementation (P3-03)
- Frontend Sentry integration
- ADR documentation (P3-11)
- Alertmanager notification integration

## Relevant Code Areas

### Files to Modify
```
template/cookiecutter.json
template/{{cookiecutter.project_slug}}/backend/app/main.py
template/{{cookiecutter.project_slug}}/backend/app/api/dependencies/auth.py
template/{{cookiecutter.project_slug}}/backend/requirements.txt
template/{{cookiecutter.project_slug}}/.env.example
template/{{cookiecutter.project_slug}}/CLAUDE.md
template/hooks/post_gen_project.py  (if exists)
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/backend/app/sentry.py  (created by P3-03)
template/{{cookiecutter.project_slug}}/backend/app/observability.py  (pattern reference)
```

### Existing Pattern Reference
The `include_observability` pattern in cookiecutter.json:
```json
{
  "include_observability": "yes"
}
```

Used in templates like:
```python
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}
```

## Implementation Details

### 1. Update cookiecutter.json

Add Sentry configuration variables:

```json
{
  // ... existing variables ...

  "include_observability": "yes",

  // Sentry Configuration (after observability)
  "include_sentry": "no",
  "sentry_dsn": "",

  // ... rest of variables ...
}
```

**Note:** Default is "no" because:
- Sentry requires a DSN (account-specific)
- Following principle of minimal footprint
- Users should explicitly opt-in to external services

### 2. Backend main.py Conditionals

```python
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
{% if cookiecutter.include_sentry == "yes" %}
from app.sentry import init_sentry
{% endif %}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"API prefix: {settings.API_V1_PREFIX}")
    {% if cookiecutter.include_sentry == "yes" %}
    # Initialize Sentry error tracking
    sentry_enabled = init_sentry(settings)
    print(f"Sentry error tracking: {'enabled' if sentry_enabled else 'disabled'}")
    {% endif %}

    yield

    # Shutdown
    print(f"Shutting down {settings.APP_NAME}")

# ... rest of main.py ...
```

### 3. Backend config.py Conditionals

```python
class Settings(BaseSettings):
    # ... existing settings ...

    {% if cookiecutter.include_sentry == "yes" %}
    # Sentry Configuration
    SENTRY_DSN: str = "{{ cookiecutter.sentry_dsn }}"
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_RELEASE: str = ""  # Defaults to APP_VERSION if empty
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of requests traced
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1  # 10% of traces profiled
    {% endif %}
```

### 4. Auth Dependency Conditionals

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

### 5. Requirements.txt Conditionals

```
# Error Tracking
{% if cookiecutter.include_sentry == "yes" %}
sentry-sdk[fastapi]>=2.0.0,<3.0.0
{% endif %}
```

### 6. .env.example Conditionals

```bash
# =============================================================================
# Application
# =============================================================================
APP_NAME={{ cookiecutter.project_name }}
APP_VERSION=0.1.0
DEBUG=true

# ... existing env vars ...

{% if cookiecutter.include_sentry == "yes" %}
# =============================================================================
# Sentry Error Tracking
# =============================================================================
# Get your DSN from https://sentry.io/settings/{org}/projects/{project}/keys/
SENTRY_DSN={{ cookiecutter.sentry_dsn }}
SENTRY_ENVIRONMENT=development
# SENTRY_RELEASE is auto-set from APP_VERSION if empty

{% endif %}
```

### 7. CLAUDE.md Conditionals

Add to the CLAUDE.md template:

```markdown
{% if cookiecutter.include_sentry == "yes" %}
## Error Tracking (Sentry)

The project includes optional Sentry integration for error tracking.

### Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| SENTRY_DSN | Sentry project DSN | (from cookiecutter) |
| SENTRY_ENVIRONMENT | Environment tag | development |
| SENTRY_RELEASE | Release version | APP_VERSION |
| SENTRY_TRACES_SAMPLE_RATE | Trace sampling rate | 0.1 |

### Features

- Automatic exception capture with stack traces
- Multi-tenant context (tenant_id, user_id)
- PII filtering via before_send hook
- Integration with FastAPI and SQLAlchemy

### Usage

Sentry is automatically initialized on application startup if SENTRY_DSN is configured.
User context is automatically set after successful authentication.

```python
# Manual message capture (optional)
from app.sentry import capture_message

capture_message("Custom event", level="info", custom_data="value")
```
{% endif %}
```

### 8. Sentry Module Conditional Include

The entire `sentry.py` file should be conditionally included:

```
template/{{cookiecutter.project_slug}}/backend/app/{% if cookiecutter.include_sentry == 'yes' %}sentry.py{% endif %}
```

However, this is complex with cookiecutter. Alternative approach - keep the file but make it a no-op when not configured:

```python
# backend/app/sentry.py
"""
Sentry error tracking integration.
{% if cookiecutter.include_sentry == "no" %}

NOTE: Sentry is not enabled for this project.
This file is included as a stub for potential future enablement.
{% endif %}
"""

{% if cookiecutter.include_sentry == "yes" %}
# Full Sentry implementation from P3-03
import logging
# ... rest of implementation ...
{% else %}
# Stub implementation when Sentry is disabled
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

SENTRY_AVAILABLE = False

def init_sentry(settings: Any) -> bool:
    """Stub: Sentry is not enabled for this project."""
    return False

def set_user_context(user_id: str, tenant_id: str, email: Optional[str] = None) -> None:
    """Stub: Sentry is not enabled for this project."""
    pass

def clear_user_context() -> None:
    """Stub: Sentry is not enabled for this project."""
    pass

def capture_message(message: str, level: str = "info", **extra: Any) -> Optional[str]:
    """Stub: Sentry is not enabled for this project."""
    return None
{% endif %}
```

### 9. GitHub Actions Integration (FR-OPS-004)

Update build workflow to set SENTRY_RELEASE:

```yaml
# .github/workflows/build.yml
{% if cookiecutter.include_sentry == "yes" %}
- name: Set Sentry Release
  run: echo "SENTRY_RELEASE=${{ github.sha }}" >> $GITHUB_ENV

- name: Build with Sentry Release
  run: |
    docker build \
      --build-arg SENTRY_RELEASE=${{ env.SENTRY_RELEASE }} \
      -t ${{ env.IMAGE_NAME }}:${{ github.sha }} \
      ./backend
{% endif %}
```

## Success Criteria

### Functional Requirements
- [ ] `include_sentry` variable in cookiecutter.json
- [ ] Default value is "no" (opt-in pattern)
- [ ] When "yes": Sentry SDK included, configuration added
- [ ] When "no": Clean project without Sentry dependencies
- [ ] GitHub Actions sets SENTRY_RELEASE when enabled (FR-OPS-004)

### Verification Steps
1. **Generate with Sentry enabled:**
   ```bash
   cookiecutter template/ --no-input include_sentry=yes sentry_dsn=https://xxx@sentry.io/123
   # Verify: sentry-sdk in requirements.txt
   # Verify: SENTRY_DSN in .env.example
   # Verify: Sentry imports in main.py
   ```

2. **Generate with Sentry disabled:**
   ```bash
   cookiecutter template/ --no-input include_sentry=no
   # Verify: No sentry-sdk in requirements.txt
   # Verify: No SENTRY_* in .env.example
   # Verify: No Sentry imports in main.py
   ```

3. **Matrix test all combinations:**
   ```bash
   # Test: observability=yes, sentry=yes
   # Test: observability=yes, sentry=no
   # Test: observability=no, sentry=yes
   # Test: observability=no, sentry=no
   ```

### Quality Gates
- [ ] All option combinations generate valid projects
- [ ] Generated project starts successfully (both yes and no)
- [ ] No Jinja2 syntax errors in templates
- [ ] ruff format passes on generated code
- [ ] pytest passes on generated project

## Integration Points

### Upstream Dependencies
| Task | Contract | Status |
|------|----------|--------|
| P3-03 | sentry.py module implementation | Must be complete |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P3-11 | ADR-024 references include_sentry pattern | Documents the conditional |
| P6-03 | Template validation tests all combinations | Tests this implementation |

### Integration Contract
```json
// cookiecutter.json contract
{
  "include_sentry": "yes|no",  // Default: "no"
  "sentry_dsn": "string"       // Only used if include_sentry == "yes"
}
```

## Monitoring and Observability

Not applicable - this is a cookiecutter template modification task.

## Infrastructure Needs

### Template Testing
- CI matrix should test Sentry option combinations
- Add to existing template validation tests

### Documentation
- Update README with Sentry option documentation
- Add to feature matrix in project documentation

## Testing Strategy

### Cookiecutter Template Tests

```python
# tests/test_cookiecutter.py

import pytest
import subprocess
from pathlib import Path


@pytest.mark.parametrize("include_sentry,sentry_dsn", [
    ("yes", "https://test@sentry.io/123"),
    ("no", ""),
])
def test_sentry_conditional(tmp_path, include_sentry, sentry_dsn):
    """Test Sentry cookiecutter conditional generates valid project."""
    result = subprocess.run([
        "cookiecutter", "template/",
        "--no-input",
        "--output-dir", str(tmp_path),
        f"include_sentry={include_sentry}",
        f"sentry_dsn={sentry_dsn}",
    ], capture_output=True, text=True)

    assert result.returncode == 0

    project_dir = tmp_path / "my-awesome-project"
    requirements = (project_dir / "backend" / "requirements.txt").read_text()

    if include_sentry == "yes":
        assert "sentry-sdk" in requirements
        env_example = (project_dir / ".env.example").read_text()
        assert "SENTRY_DSN" in env_example
    else:
        assert "sentry-sdk" not in requirements


def test_sentry_no_breaks_observability(tmp_path):
    """Test that Sentry=no doesn't affect observability=yes."""
    subprocess.run([
        "cookiecutter", "template/",
        "--no-input",
        "--output-dir", str(tmp_path),
        "include_observability=yes",
        "include_sentry=no",
    ], check=True)

    project_dir = tmp_path / "my-awesome-project"
    main_py = (project_dir / "backend" / "app" / "main.py").read_text()

    assert "from app.observability import setup_observability" in main_py
    assert "from app.sentry import" not in main_py
```

### Generated Project Tests

```python
# Run in generated project context
def test_app_starts_without_sentry():
    """Test application starts when Sentry is disabled."""
    # Start app, verify no errors
    pass

def test_app_starts_with_invalid_sentry_dsn():
    """Test fail-open pattern with invalid DSN."""
    # Set invalid SENTRY_DSN, verify app starts
    pass
```

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Multiple files need Jinja2 conditionals
- Matrix testing required for option combinations
- Integration with existing cookiecutter patterns
- GitHub Actions workflow modifications (optional FR-OPS-004)

## Notes

### Design Decisions

**1. Default Value "no":**
Unlike `include_observability` (default "yes"), Sentry defaults to "no" because:
- Requires external service account
- DSN is project-specific (cannot have a generic default)
- Following minimal footprint principle

**2. Stub vs. Exclude Pattern:**
Using a stub implementation when Sentry is disabled (instead of excluding the file entirely) because:
- Simpler cookiecutter template structure
- Allows future enablement without adding files
- Consistent import statements (no need to check before importing)

**3. sentry_dsn Variable:**
Included in cookiecutter.json even though it could be set via environment variable because:
- Allows baking DSN into generated project
- Simplifies initial setup for teams with known DSN
- Can be overridden via environment variable

### Jinja2 Best Practices

1. **Whitespace Control:**
   Use `{%- ... -%}` for conditionals that should not add blank lines
   ```python
   {%- if cookiecutter.include_sentry == "yes" %}
   from app.sentry import init_sentry
   {%- endif %}
   ```

2. **Consistent Quoting:**
   Always use double quotes for string comparison
   ```python
   {% if cookiecutter.include_sentry == "yes" %}
   ```

3. **Block Organization:**
   Group related conditionals together, don't scatter throughout file

### Related Requirements
- FR-OPS-001: Template shall include optional Sentry SDK integration (implemented via this conditional)
- FR-OPS-004: Sentry release tracking shall be configured in CI/CD pipeline
- NFR-006: Optional features shall follow the observability pattern

### Risk Mitigation

**Risk: Template Syntax Errors**
- Mitigation: Comprehensive matrix testing in CI
- Mitigation: Use cookiecutter's built-in template validation

**Risk: Combination Conflicts**
- Mitigation: Test all combinations: observability x sentry
- Mitigation: Independent feature flags (no cross-dependencies)
