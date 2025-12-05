# P4-04: Add Conditionals to main.py

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P4-04 |
| **Title** | Add Conditionals to main.py |
| **Domain** | Backend |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P4-01 |
| **Blocks** | None |

---

## Scope

### Included
- Wrap observability import in Jinja2 conditional
- Wrap setup_observability() call in Jinja2 conditional
- Ensure Python syntax remains valid after rendering
- Test application startup with both configurations

### Excluded
- Conditional logic for other features
- Runtime feature flags

---

## Relevant Code Areas

### Destination File
- `template/{{cookiecutter.project_slug}}/backend/app/main.py`

---

## Implementation Details

### Conditional Import

Add conditional import at the top of main.py:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routers import health_router, auth_router, oauth_router
# ... other imports ...

{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}
```

### Conditional Setup Call

Add conditional setup after app creation:

```python
app = FastAPI(
    title="{{ cookiecutter.project_name }}",
    description="{{ cookiecutter.project_short_description }}",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

{% if cookiecutter.include_observability == "yes" %}
# Setup observability (tracing, metrics, /metrics endpoint)
# Must be called before other middleware for complete instrumentation
setup_observability(app)
{% endif %}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    # ... rest of CORS config ...
)
```

### Full Example

```python
"""
{{ cookiecutter.project_name }} Backend API

FastAPI application with OAuth 2.0 authentication and multi-tenancy support.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.routers import health_router, auth_router, oauth_router
from app.middleware.tenant import TenantMiddleware
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    await init_db()
    yield


app = FastAPI(
    title="{{ cookiecutter.project_name }}",
    description="{{ cookiecutter.project_short_description }}",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

{% if cookiecutter.include_observability == "yes" %}
# Setup observability (tracing, metrics, /metrics endpoint)
# Must be called before other middleware for complete request instrumentation
setup_observability(app)
{% endif %}

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tenant context middleware
app.add_middleware(TenantMiddleware)

# Include routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX, tags=["health"])
app.include_router(auth_router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(oauth_router, prefix=settings.API_V1_PREFIX, tags=["oauth"])
```

### Python Syntax Considerations

**Critical**: Jinja2 conditionals in Python files must result in valid Python.

**Valid:**
```python
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}
```

Renders to either:
- `from app.observability import setup_observability` (with observability)
- Empty (without observability, which is valid Python)

**Also valid:**
```python
{% if cookiecutter.include_observability == "yes" %}
# Setup observability
setup_observability(app)
{% endif %}
```

### Testing Application Startup

1. **With observability:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   # Should start with observability message
   # /metrics endpoint available
   ```

2. **Without observability:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   # Should start without errors
   # /metrics endpoint NOT available
   ```

---

## Success Criteria

- [ ] Import statement conditionally included
- [ ] setup_observability() call conditionally included
- [ ] Generated main.py is valid Python with "yes"
- [ ] Generated main.py is valid Python with "no"
- [ ] Application starts successfully with observability
- [ ] Application starts successfully without observability
- [ ] No import errors in either case
- [ ] /metrics endpoint exists only when observability enabled

---

## Integration Points

### Upstream
- **P4-01**: `include_observability` variable must be defined
- **P2-02**: observability.py must exist for import

### Contract: Module Path

Import path must match the observability module location:
```python
from app.observability import setup_observability
```

This requires the file at:
```
backend/app/observability.py
```

### Contract: Function Signature

The setup call must match the function signature:
```python
setup_observability(app)  # Takes FastAPI app, returns instrumented app
```

---

## Monitoring/Observability

After implementation, verify:
- Python syntax is valid (no syntax errors)
- Application starts without import errors
- Correct behavior based on configuration

---

## Infrastructure Needs

None - template changes only.

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Adding conditionals to main.py
- Testing Python syntax validity
- Verifying application startup
- Testing both generation paths
