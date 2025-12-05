# P2-01: Add Observability Python Dependencies

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P2-01 |
| **Title** | Add Observability Python Dependencies |
| **Domain** | Backend |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P1-06 |
| **Blocks** | P2-02 |

---

## Scope

### Included
- Add OpenTelemetry packages to pyproject.toml
- Add prometheus-client package
- Configure version constraints for Python 3.10-3.13 compatibility
- Initial conditional structure (refined in P4-03)

### Excluded
- OpenTelemetry instrumentation for other libraries (SQLAlchemy, Redis)
- Custom metric exporters
- Development/test dependencies for observability

---

## Relevant Code Areas

### Source File (Dependencies Inferred)
- `/home/ty/workspace/project-starter/implementation-manager/backend/observability.py` (import statements)

### Destination File
- `template/{{cookiecutter.project_slug}}/backend/pyproject.toml`

---

## Implementation Details

### Required Dependencies

Based on the `observability.py` source file imports:

```python
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
```

### Dependencies to Add

```toml
# Observability dependencies
opentelemetry-api = ">=1.27.0,<2.0.0"
opentelemetry-sdk = ">=1.27.0,<2.0.0"
opentelemetry-exporter-otlp-proto-grpc = ">=1.27.0,<2.0.0"
opentelemetry-instrumentation-fastapi = ">=0.48b0,<1.0.0"
prometheus-client = ">=0.20.0,<1.0.0"
```

### Dependency Explanation

| Package | Version | Purpose |
|---------|---------|---------|
| `opentelemetry-api` | >=1.27.0,<2.0.0 | Core OTel API (trace, metrics) |
| `opentelemetry-sdk` | >=1.27.0,<2.0.0 | OTel SDK (TracerProvider, MeterProvider) |
| `opentelemetry-exporter-otlp-proto-grpc` | >=1.27.0,<2.0.0 | OTLP/gRPC export to Tempo |
| `opentelemetry-instrumentation-fastapi` | >=0.48b0,<1.0.0 | Automatic FastAPI instrumentation |
| `prometheus-client` | >=0.20.0,<1.0.0 | Prometheus metrics and /metrics endpoint |

### Version Constraint Rationale

- **OpenTelemetry packages**: Version 1.27.0+ provides stable APIs and improved performance. The <2.0.0 constraint protects against breaking changes.
- **FastAPI instrumentation**: Beta versioning (0.48b0) is standard for OpenTelemetry instrumentation packages. They follow a different versioning scheme than the core SDK.
- **prometheus-client**: Version 0.20.0+ includes modern exposition formats and typing support.

### pyproject.toml Structure

Add dependencies with conditional comment (to be refined in P4-03):

```toml
[project]
dependencies = [
    # ... existing dependencies ...

    # Observability (when include_observability == "yes")
    "opentelemetry-api>=1.27.0,<2.0.0",
    "opentelemetry-sdk>=1.27.0,<2.0.0",
    "opentelemetry-exporter-otlp-proto-grpc>=1.27.0,<2.0.0",
    "opentelemetry-instrumentation-fastapi>=0.48b0,<1.0.0",
    "prometheus-client>=0.20.0,<1.0.0",
]
```

**Note**: Full Jinja2 conditional wrapping is handled in P4-03.

---

## Success Criteria

- [ ] All 5 observability dependencies added to pyproject.toml
- [ ] Version constraints are appropriate (not too restrictive, not too loose)
- [ ] Dependencies are compatible with Python 3.10, 3.11, 3.12, 3.13
- [ ] `pip install` / `uv sync` succeeds without conflicts
- [ ] Dependencies don't conflict with existing FastAPI dependencies
- [ ] Import statements in observability.py can resolve successfully

---

## Integration Points

### Upstream
- **P1-06**: compose.yml must exist for Docker-based testing

### Downstream
- **P2-02**: observability.py imports these dependencies
- **P4-03**: Conditional dependency logic

### Dependency Conflict Check

Verify no conflicts with existing dependencies in template:
- `fastapi`: OpenTelemetry FastAPI instrumentation must be compatible
- `uvicorn`: No known conflicts
- `pydantic`: No known conflicts
- `sqlalchemy`: Future instrumentation (not in scope)

---

## Monitoring/Observability

After implementation, verify:
- No deprecation warnings during import
- All packages resolve to expected versions
- `pip list` shows correct installed versions

---

## Infrastructure Needs

None - configuration file changes only.

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Researching compatible versions
- Testing dependency resolution
- Verifying Python version compatibility
- Checking for conflicts
