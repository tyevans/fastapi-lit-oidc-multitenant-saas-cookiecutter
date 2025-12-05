# P2-04: Add Backend Environment Variables to compose.yml

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P2-04 |
| **Title** | Add Backend Environment Variables to compose.yml |
| **Domain** | Backend |
| **Complexity** | XS (< 4 hours) |
| **Dependencies** | P2-02 |
| **Blocks** | None |

---

## Scope

### Included
- Add OpenTelemetry environment variables to backend service
- Configure OTLP endpoint for Tempo
- Set service name for tracing
- Initial configuration (conditional logic refined in P4-02)

### Excluded
- Conditional Jinja2 logic (handled in P4-02)
- Frontend environment variables (out of scope)
- Production configuration options

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/docker-compose.yml` (backend service section)

### Destination File
- `template/{{cookiecutter.project_slug}}/compose.yml` (backend service section)

---

## Implementation Details

### Environment Variables to Add

Add to the `backend` service `environment` section:

```yaml
backend:
  # ... existing configuration ...
  environment:
    # ... existing environment variables ...

    # OpenTelemetry Configuration (for observability)
    OTEL_SERVICE_NAME: backend
    OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317
```

### Environment Variable Details

| Variable | Value | Purpose |
|----------|-------|---------|
| `OTEL_SERVICE_NAME` | `backend` | Identifies service in traces and metrics |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `http://tempo:4317` | OTLP gRPC endpoint for trace export |

### Full Backend Service Section (Partial)

```yaml
  # Backend API (FastAPI)
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      target: development
    container_name: {{ cookiecutter.project_slug }}-backend
    restart: unless-stopped
    environment:
      # Application
      ENV: ${ENV:-development}
      DEBUG: ${DEBUG:-true}
      LOG_LEVEL: ${LOG_LEVEL:-info}

      # Database configuration
      DATABASE_URL: postgresql+asyncpg://...
      # ... other existing environment variables ...

      # OpenTelemetry Configuration
      OTEL_SERVICE_NAME: backend
      OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317

    ports:
      - "${BACKEND_PORT:-{{ cookiecutter.backend_port }}}:8000"
    # ... rest of configuration ...
```

### Dependency Consideration

The backend does NOT need to depend on Tempo because:
1. OpenTelemetry's BatchSpanProcessor handles export failures gracefully
2. Traces are buffered if Tempo is unavailable
3. No application errors occur when Tempo is down

This allows the backend to start independently of observability services.

---

## Success Criteria

- [ ] `OTEL_SERVICE_NAME` environment variable added to backend service
- [ ] `OTEL_EXPORTER_OTLP_ENDPOINT` points to `http://tempo:4317`
- [ ] Environment variables are placed logically (grouped with comments)
- [ ] Backend service starts successfully with these variables
- [ ] Traces are exported to Tempo when Tempo is running
- [ ] Backend starts without errors when Tempo is not running (graceful degradation)

---

## Integration Points

### Upstream
- **P2-02**: observability.py reads these environment variables

### Downstream
- **P4-02**: Conditional environment variable inclusion

### Contract: Environment Variables

The observability module expects these environment variables:

| Variable | Default in Code | compose.yml Value | Notes |
|----------|----------------|-------------------|-------|
| `OTEL_SERVICE_NAME` | "backend" | "backend" | Could be templatized to `{{ cookiecutter.project_slug }}-backend` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | "http://tempo:4317" | "http://tempo:4317" | Uses Docker network hostname |

**Note**: The defaults in the observability.py code match these values, so even if the environment variables are missing, the module will work correctly.

---

## Monitoring/Observability

After implementation, verify:
- `docker compose config` shows environment variables on backend service
- Backend logs show "Observability configured for backend"
- Traces in Tempo have `service.name: backend`

---

## Infrastructure Needs

None - configuration changes only.

---

## Estimated Effort

**Time**: 30 minutes - 1 hour

This is a simple configuration addition:
- Add two environment variables to compose.yml
- Add comment for grouping
- Test that backend starts correctly
