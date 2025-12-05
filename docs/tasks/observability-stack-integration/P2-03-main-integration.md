# P2-03: Integrate Observability into main.py

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P2-03 |
| **Title** | Integrate Observability into main.py |
| **Domain** | Backend |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P2-02 |
| **Blocks** | None |

---

## Scope

### Included
- Add import statement for observability module
- Call `setup_observability(app)` after app creation
- Ensure observability setup occurs before other middleware
- Initial integration (conditional logic refined in P4-04)

### Excluded
- Conditional import logic (handled in P4-04)
- Custom span creation examples
- Additional instrumentation

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/backend/main.py` (integration pattern)

### Destination File
- `template/{{cookiecutter.project_slug}}/backend/app/main.py`

---

## Implementation Details

### Integration Location

The observability setup must be called:
1. **After** FastAPI app creation
2. **Before** other middleware registration
3. **Before** router registration

This ensures all requests are instrumented from the start.

### Integration Code

```python
# At the top of main.py, add import
from app.observability import setup_observability

# After app creation, before middleware
app = FastAPI(
    title="{{ cookiecutter.project_name }}",
    description="{{ cookiecutter.project_short_description }}",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
)

# Setup observability FIRST (before other middleware)
# This ensures all requests are traced and metriced
setup_observability(app)

# Then add other middleware
app.add_middleware(
    CORSMiddleware,
    # ... CORS configuration
)

# Then include routers
app.include_router(health_router, prefix=settings.API_V1_PREFIX)
# ... other routers
```

### Why Order Matters

```
Request Flow with Observability:
================================

[HTTP Request]
     |
     v
[Observability Metrics Middleware]  <-- Captures timing START
     |
     v
[CORS Middleware]
     |
     v
[Other Middleware]
     |
     v
[FastAPIInstrumentor Span]  <-- Creates trace span
     |
     v
[Route Handler]
     |
     v
[Response]
     |
     v
[Observability Metrics Middleware]  <-- Captures timing END, records metrics
     |
     v
[HTTP Response]
```

If observability is registered after CORS middleware, CORS-rejected requests won't be tracked.

### Current main.py Structure Reference

Review the existing main.py structure in the template to identify the correct insertion point:

```python
# Typical structure:
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
# ... other imports

app = FastAPI(...)

# CORS middleware
app.add_middleware(CORSMiddleware, ...)

# Routers
app.include_router(...)
```

### Modified Structure

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.observability import setup_observability  # ADD THIS
# ... other imports

app = FastAPI(...)

# Setup observability (before other middleware)
setup_observability(app)  # ADD THIS

# CORS middleware
app.add_middleware(CORSMiddleware, ...)

# Routers
app.include_router(...)
```

---

## Success Criteria

- [ ] Import statement added for observability module
- [ ] `setup_observability(app)` called after app creation
- [ ] Observability setup occurs BEFORE CORS middleware
- [ ] Observability setup occurs BEFORE router registration
- [ ] Application starts without import errors
- [ ] `/metrics` endpoint is accessible
- [ ] Traces are exported to Tempo
- [ ] All HTTP requests are instrumented

---

## Integration Points

### Upstream
- **P2-02**: observability.py must exist and be importable

### Downstream
- **P4-04**: Conditional import and setup

### Contract: Application Lifecycle

The observability module expects to be called with a FastAPI app instance:

```python
# Expected call pattern
app = FastAPI(...)
setup_observability(app)  # Returns instrumented app
```

The function:
1. Calls `FastAPIInstrumentor.instrument_app(app)`
2. Registers metrics middleware via `@app.middleware("http")`
3. Registers `/metrics` endpoint via `@app.get("/metrics")`

---

## Monitoring/Observability

After implementation, verify:
- Application starts without errors
- `http://localhost:8000/metrics` returns Prometheus format
- Traces appear in Tempo for HTTP requests
- Backend logs show "Observability configured for backend"

---

## Infrastructure Needs

None - code changes only.

---

## Estimated Effort

**Time**: 1-2 hours

This is a straightforward integration task:
- Identify correct location in main.py
- Add import and function call
- Verify order of middleware registration
- Test the integration
