# P2-02: Create Observability Module

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P2-02 |
| **Title** | Create Observability Module |
| **Domain** | Backend |
| **Complexity** | M (1-2 days) |
| **Dependencies** | P2-01 |
| **Blocks** | P2-03, P2-04, P3-03 |

---

## Scope

### Included
- Port `observability.py` from implementation-manager to template
- Configure OpenTelemetry tracing with OTLP export
- Define Prometheus metrics (Counter, Histogram, Gauge)
- Implement `setup_observability(app)` function
- Create metrics middleware for request instrumentation
- Add `/metrics` endpoint
- Configure structured logging with trace context
- Add comprehensive docstrings and inline comments

### Excluded
- Database query tracing (out of scope)
- Redis instrumentation (out of scope)
- Custom business metrics (user responsibility)
- OpenTelemetry metrics export (using Prometheus directly)

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/backend/observability.py`

### Destination File
- `template/{{cookiecutter.project_slug}}/backend/app/observability.py`

### Reference Files
- `/home/ty/workspace/project-starter/implementation-manager/backend/main.py` (integration pattern)

---

## Implementation Details

### Module Structure

```python
"""
Observability instrumentation for {{ cookiecutter.project_name }}.

This module configures:
- OpenTelemetry distributed tracing (exports to Tempo via OTLP)
- Prometheus metrics (exposed at /metrics endpoint)
- Structured logging with trace context correlation

Environment Variables:
- OTEL_SERVICE_NAME: Service name for traces (default: "backend")
- OTEL_EXPORTER_OTLP_ENDPOINT: Tempo endpoint (default: "http://tempo:4317")
- TESTING: Set to "true" to disable trace context in logs

Usage:
    from app.observability import setup_observability

    app = FastAPI()
    setup_observability(app)
"""

import logging
import os
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
from fastapi import Response


# =============================================================================
# Configuration
# =============================================================================

SERVICE_NAME_VAL = os.getenv("OTEL_SERVICE_NAME", "backend")
OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317")


# =============================================================================
# Logging Configuration
# =============================================================================

# Use simplified format in test mode (no trace context)
if os.getenv("TESTING", "false").lower() == "true":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
else:
    # Production format with trace context for correlation
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - trace_id=%(otelTraceID)s span_id=%(otelSpanID)s'
    )


# =============================================================================
# OpenTelemetry Tracing Setup
# =============================================================================

# Resource identifies this service in traces
resource = Resource(attributes={
    SERVICE_NAME: SERVICE_NAME_VAL
})

# TracerProvider manages trace creation and export
trace_provider = TracerProvider(resource=resource)

# OTLP exporter sends traces to Tempo
trace_exporter = OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)

# BatchSpanProcessor efficiently batches and exports spans
# - Handles export failures gracefully (drops oldest spans if buffer full)
# - Async export doesn't block request processing
trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

# Set as global tracer provider
trace.set_tracer_provider(trace_provider)


# =============================================================================
# OpenTelemetry Metrics Setup (for Tempo service graph)
# =============================================================================

metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True),
    export_interval_millis=5000
)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)


# =============================================================================
# Prometheus Metrics Definitions
# =============================================================================

# Counter: Total HTTP requests
# Labels: method (GET, POST, etc.), endpoint (/api/v1/...), status (200, 404, etc.)
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

# Histogram: Request duration in seconds
# Labels: method, endpoint
# Default buckets optimized for web request latencies
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Gauge: Current number of in-flight requests
active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)


# =============================================================================
# Tracer and Meter for Custom Instrumentation
# =============================================================================

# Use these for adding custom spans/metrics in application code
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)


# =============================================================================
# Setup Function
# =============================================================================

def setup_observability(app):
    """
    Setup observability instrumentation for FastAPI app.

    This function:
    1. Instruments FastAPI with OpenTelemetry for automatic request tracing
    2. Adds HTTP middleware for Prometheus metrics collection
    3. Registers the /metrics endpoint for Prometheus scraping

    Args:
        app: FastAPI application instance

    Returns:
        The instrumented FastAPI application

    Example:
        app = FastAPI()
        setup_observability(app)
    """
    # Instrument FastAPI with OpenTelemetry
    # This automatically creates spans for all HTTP requests
    FastAPIInstrumentor.instrument_app(app)

    # Add middleware for Prometheus metrics
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        """
        Middleware that collects HTTP metrics for every request.

        Metrics collected:
        - active_requests: Incremented at start, decremented at end
        - http_request_duration_seconds: Request processing time
        - http_requests_total: Request count with method, endpoint, status
        """
        active_requests.inc()
        method = request.method
        path = request.url.path

        # Time the request and record duration
        with http_request_duration_seconds.labels(method=method, endpoint=path).time():
            response = await call_next(request)

        active_requests.dec()
        http_requests_total.labels(
            method=method,
            endpoint=path,
            status=response.status_code
        ).inc()

        return response

    # Add metrics endpoint for Prometheus scraping
    @app.get("/metrics", include_in_schema=False)
    async def get_metrics():
        """
        Prometheus metrics endpoint.

        Returns metrics in Prometheus exposition format.
        This endpoint is excluded from API documentation.
        """
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

    logging.info(f"Observability configured for {SERVICE_NAME_VAL}")
    return app
```

### Key Implementation Points

1. **Test Mode Detection**
   - `TESTING=true` disables trace context in logs
   - Prevents log format errors during pytest

2. **Graceful Degradation**
   - BatchSpanProcessor handles export failures
   - Drops oldest spans if buffer full (no exceptions)
   - `insecure=True` for development (no TLS)

3. **Metrics Middleware**
   - Uses context manager for accurate duration timing
   - Tracks active requests with gauge
   - Labels for filtering (method, endpoint, status)

4. **/metrics Endpoint**
   - Excluded from OpenAPI schema (`include_in_schema=False`)
   - Returns Prometheus exposition format

---

## Success Criteria

- [ ] Module contains all OpenTelemetry configuration
- [ ] TracerProvider configured with correct service name
- [ ] OTLPSpanExporter points to Tempo endpoint
- [ ] BatchSpanProcessor used for efficient export
- [ ] Prometheus metrics defined (http_requests_total, http_request_duration_seconds, active_requests)
- [ ] `setup_observability(app)` function implemented
- [ ] FastAPIInstrumentor instruments the app
- [ ] Metrics middleware collects request data
- [ ] `/metrics` endpoint registered and returns valid Prometheus format
- [ ] Test mode disables trace context in logs
- [ ] Comprehensive docstrings and inline comments included
- [ ] Module imports successfully without errors

---

## Integration Points

### Upstream
- **P2-01**: Python dependencies must be installed

### Downstream
- **P2-03**: main.py imports and calls setup_observability()
- **P2-04**: compose.yml adds OTEL environment variables
- **P3-03**: Backend dashboard queries these metrics

### Contract: Observability Module API

```python
def setup_observability(app: FastAPI) -> FastAPI:
    """
    Initialize observability instrumentation.

    - Instruments app with OpenTelemetry tracing
    - Registers metrics middleware
    - Adds /metrics endpoint

    Returns: The instrumented FastAPI application
    """
```

### Contract: Metrics Endpoint

```
Endpoint: GET /metrics
Content-Type: text/plain; version=0.0.4; charset=utf-8

Metrics:
- http_requests_total{method="GET",endpoint="/api/v1/health",status="200"}
- http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/health",le="0.005"}
- http_request_duration_seconds_sum{method="GET",endpoint="/api/v1/health"}
- http_request_duration_seconds_count{method="GET",endpoint="/api/v1/health"}
- active_requests
```

### Contract: Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| OTEL_SERVICE_NAME | "backend" | Service name in traces |
| OTEL_EXPORTER_OTLP_ENDPOINT | "http://tempo:4317" | Tempo OTLP endpoint |
| TESTING | "false" | Disable trace context in logs when "true" |

---

## Monitoring/Observability

After implementation, verify:
- Traces appear in Tempo within 30 seconds
- Metrics appear at /metrics endpoint
- Logs include trace_id and span_id (when not in test mode)
- No errors in backend logs related to observability

---

## Infrastructure Needs

**Environment Variables** (set in compose.yml - P2-04):
- `OTEL_SERVICE_NAME=backend`
- `OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317`

**Network Access**:
- Backend must be able to reach `tempo:4317` (gRPC)

---

## Estimated Effort

**Time**: 4-8 hours

Includes:
- Porting and adapting source code
- Adding comprehensive documentation
- Testing trace export
- Testing metrics endpoint
- Verifying log format
