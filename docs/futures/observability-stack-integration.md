# Observability Stack Integration for Cookiecutter Template

| Field | Value |
|-------|-------|
| **Title** | Observability Stack Integration |
| **Date Created** | 2025-12-03 |
| **Last Updated** | 2025-12-03 (Revised) |
| **Author/Agent** | FRD Builder Agent |
| **Status** | Revised and Ready for Implementation |

---

## Table of Contents

- [x] [Problem Statement](#problem-statement)
- [x] [Goals & Success Criteria](#goals--success-criteria)
- [x] [Scope & Boundaries](#scope--boundaries)
- [x] [User Stories / Use Cases](#user-stories--use-cases)
- [x] [Functional Requirements](#functional-requirements)
- [x] [Non-Functional Requirements](#non-functional-requirements)
- [x] [Technical Approach](#technical-approach)
- [x] [Architecture & Integration Considerations](#architecture--integration-considerations)
- [x] [Data Models & Schema Changes](#data-models--schema-changes)
- [x] [UI/UX Considerations](#uiux-considerations)
- [x] [Security & Privacy Considerations](#security--privacy-considerations)
- [x] [Testing Strategy](#testing-strategy)
- [x] [Implementation Phases](#implementation-phases)
- [x] [Dependencies & Risks](#dependencies--risks)
- [x] [Open Questions](#open-questions)
- [x] [Status](#status)

---

## Problem Statement

### Current State

The cookiecutter project template at `/home/ty/workspace/project-starter/template/` generates full-stack applications with FastAPI backend, Lit frontend, PostgreSQL database, Redis cache, and Keycloak authentication. While the template provides a solid foundation for building modern web applications with multi-tenancy and OAuth 2.0, **it lacks production-ready observability infrastructure**.

Currently generated projects have:
- Basic health check endpoints (`/api/v1/health`)
- Standard Python logging (no structured format)
- No metrics collection or visualization
- No log aggregation or centralized logging
- No distributed tracing capabilities
- No pre-configured dashboards for monitoring

### The Proven Solution

The `implementation-manager/` project contains a battle-tested observability stack that addresses all these gaps:

**Components in implementation-manager/observability/**:
1. **Grafana** (Port 3000) - Unified visualization platform with pre-configured datasources and dashboards
2. **Prometheus** (Port 9090) - Metrics collection and storage with scrape configurations for backend, Keycloak, and observability services
3. **Loki** (Port 3100) - Log aggregation and storage with efficient querying
4. **Promtail** - Log collection from Docker containers with automatic container discovery
5. **Tempo** (Ports 3200, 4317, 4318) - Distributed tracing backend with OTLP protocol support

**Backend Instrumentation** (`implementation-manager/backend/observability.py`):
- OpenTelemetry integration for distributed tracing
- Prometheus metrics (request count, duration histograms, active requests gauge)
- FastAPI automatic instrumentation via `FastAPIInstrumentor`
- Structured logging with trace context injection (trace_id, span_id)
- `/metrics` endpoint for Prometheus scraping

### Pain Points Without Observability

1. **Debugging Blind Spots**: Developers cannot trace requests across service boundaries, making it difficult to diagnose issues in distributed systems.

2. **Performance Opacity**: Without metrics, there is no visibility into request latency percentiles (p95, p99), error rates, or throughput.

3. **Operational Burden**: Log aggregation is manual - developers must SSH into containers or use `docker compose logs` to view logs, which is inefficient for production troubleshooting.

4. **Incident Response Delays**: Without centralized observability, Mean Time to Detection (MTTD) and Mean Time to Resolution (MTTR) are significantly higher.

5. **Compliance Gaps**: Many production environments require audit trails and monitoring capabilities that the current template does not provide.

### Business Impact

- **Development Velocity**: Teams spend more time debugging without proper observability tools
- **Production Readiness**: Generated projects require significant additional work to be production-ready
- **Template Competitiveness**: Modern project templates (e.g., enterprise boilerplates) include observability by default
- **Learning Curve**: Developers must learn and integrate observability tools independently for each project

### Evidence from Codebase

The implementation-manager project demonstrates the value of integrated observability:

```yaml
# implementation-manager/docker-compose.yml (lines 91-160)
# Full observability stack already integrated and working:
prometheus:
  image: prom/prometheus:latest
  # ...configured with prometheus.yml

loki:
  image: grafana/loki:latest
  # ...configured with loki-config.yml

promtail:
  image: grafana/promtail:latest
  # ...configured with promtail-config.yml

tempo:
  image: grafana/tempo:latest
  # ...configured with tempo.yml

grafana:
  image: grafana/grafana:latest
  # ...with pre-configured datasources and dashboards
```

The backend already has observability setup code:
```python
# implementation-manager/backend/observability.py
def setup_observability(app):
    """Setup observability instrumentation for FastAPI app."""
    FastAPIInstrumentor.instrument_app(app)
    # ... middleware for Prometheus metrics
    # ... /metrics endpoint
```

### Opportunity

Porting the observability stack from `implementation-manager/` to the cookiecutter template will:
1. Provide immediate value to all projects generated from the template
2. Eliminate repetitive observability setup work across projects
3. Establish consistent observability patterns across the organization
4. Reduce time-to-production for new applications
5. Enable developers to focus on business logic rather than infrastructure

---

## Goals & Success Criteria

### Primary Goals

#### G1: Production-Ready Observability Out of the Box

Every project generated from the cookiecutter template should include a fully functional observability stack that requires zero additional configuration to start using in development and minimal configuration for production deployment.

**Success Criteria:**
- Projects generated with observability enabled start with all services operational within 60 seconds of `docker compose up`
- Grafana dashboards display live metrics within 2 minutes of backend activity
- Distributed traces appear in Tempo within 30 seconds of request completion
- Logs from all containers are aggregated in Loki within 5 seconds of being written

#### G2: Enable Service Level Objective (SLO) Monitoring

Provide the infrastructure and baseline metrics necessary for teams to define and monitor SLOs from day one, supporting modern SRE practices.

**Success Criteria:**
- Pre-configured Service Level Indicators (SLIs) for the four golden signals:
  - **Latency**: Request duration histograms with p50, p95, p99 percentile visualization
  - **Traffic**: Request rate per endpoint (requests/second)
  - **Errors**: Error rate by status code (4xx, 5xx) and error budget tracking
  - **Saturation**: Active request gauges and resource utilization metrics
- SLO dashboard template with configurable targets (default: 99.5% availability, p95 latency < 500ms)
- Error budget burn rate visualization

#### G3: Reduce Mean Time to Detection (MTTD) and Mean Time to Resolution (MTTR)

Enable rapid identification and resolution of issues through correlated observability data (metrics, logs, traces).

**Success Criteria:**
- Trace-to-logs correlation: Click from a trace span to view related logs (within +/- 1 hour window)
- Logs-to-trace correlation: Link from log entries containing trace_id to full trace visualization
- Metrics-to-traces integration: Drill down from metric anomalies to exemplar traces
- Target MTTD benchmark for generated projects: < 15 minutes for detectable incidents
- Target MTTR benchmark: < 1 hour for standard application issues with proper observability

#### G4: Minimal Footprint with Optional Inclusion

The observability stack should be optional and configurable, respecting resource constraints and developer preferences.

**Success Criteria:**
- Cookiecutter prompt allows enabling/disabling observability stack (`include_observability: [yes/no]`)
- When disabled, no observability containers are included in `compose.yml`
- When enabled, additional memory footprint < 2GB for complete stack
- Clear documentation on production scaling considerations
- No performance impact on application when observability is disabled

#### G5: Developer Experience and Onboarding

Lower the barrier to entry for observability practices by providing comprehensive, pre-configured tooling.

**Success Criteria:**
- Zero-config development experience: `docker compose up` provides working observability
- README includes observability quick-start guide (< 5 minute read)
- Backend Service Dashboard provides essential monitoring (request rate, latency, errors, active requests)
- Grafana Explore view enables ad-hoc log and trace exploration
- Inline code comments in `observability.py` explaining each component

### Quantitative Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Stack Startup Time | < 90 seconds | Time from `docker compose up` to all services healthy |
| Dashboard Load Time | < 3 seconds | Time to render backend dashboard with 1 hour of data |
| Trace Ingestion Latency | < 30 seconds | Time from request completion to trace visibility in Tempo |
| Log Aggregation Latency | < 5 seconds | Time from log emission to visibility in Loki |
| Metric Scrape Interval | 5-15 seconds | Prometheus scrape configuration (configurable) |
| Memory Overhead (Dev) | < 2GB | Combined memory usage of observability containers |
| Memory Overhead (Prod) | Scalable | Documentation for production resource planning |
| Template Generation Time | < 10% increase | Impact on cookiecutter generation time |

### Qualitative Success Criteria

| Criterion | Definition |
|-----------|------------|
| Consistency | Observability patterns match `implementation-manager` reference implementation |
| Maintainability | Configuration files use industry-standard formats with clear comments |
| Extensibility | Easy to add custom metrics, dashboards, and alerting rules |
| Documentation | Complete setup, usage, and customization documentation |
| Security | Observability endpoints not exposed to public internet by default |
| Testability | Observability components have health checks and can be validated in CI |

### Timeline Expectations

| Milestone | Target |
|-----------|--------|
| FRD Complete | Week 1 |
| Infrastructure Integration (Phase 1) | Week 2-3 |
| Backend Instrumentation (Phase 2) | Week 3-4 |
| Dashboards and Documentation (Phase 3) | Week 4-5 |
| Testing and Refinement | Week 5-6 |
| Production Ready | Week 6 |

### Definition of Done

The observability stack integration is considered complete when:

1. **Functional Completeness**
   - All five observability services (Prometheus, Loki, Promtail, Tempo, Grafana) are integrated into the template
   - Backend instrumentation module (`observability.py`) is ported and adapted
   - Pre-configured datasources connect all services through Grafana
   - Backend Service Dashboard is included (ported from source implementation)

2. **Quality Assurance**
   - All existing template tests continue to pass
   - New tests validate observability stack startup and connectivity
   - Documentation reviewed and complete

3. **User Validation**
   - Generated project with observability enabled starts successfully
   - Metrics, logs, and traces flow correctly through the stack
   - Dashboards display meaningful data from backend activity

4. **Production Readiness**
   - Security considerations documented and addressed
   - Resource requirements and scaling guidance provided
   - Environment-specific configuration options available

---

## Scope & Boundaries

### In Scope

#### IS-1: Docker Compose Infrastructure Integration

The following observability services will be added to the cookiecutter template's `compose.yml`:

| Service | Image | Purpose | Ports |
|---------|-------|---------|-------|
| **Prometheus** | `prom/prometheus:latest` | Metrics collection and storage | 9090 |
| **Loki** | `grafana/loki:latest` | Log aggregation and storage | 3100 |
| **Promtail** | `grafana/promtail:latest` | Docker log collection and forwarding | N/A |
| **Tempo** | `grafana/tempo:latest` | Distributed tracing backend | 3200, 4317 (gRPC), 4318 (HTTP) |
| **Grafana** | `grafana/grafana:latest` | Unified visualization platform | 3000 |

**Configuration files to be ported:**
- `observability/prometheus/prometheus.yml` - Scrape configurations for backend, Keycloak, and observability services
- `observability/loki/loki-config.yml` - Log storage and retention settings
- `observability/promtail/promtail-config.yml` - Docker container log discovery
- `observability/tempo/tempo.yml` - Tracing backend configuration
- `observability/grafana/datasources/datasources.yml` - Pre-configured datasource connections
- `observability/grafana/dashboards/dashboards.yml` - Dashboard provisioning
- `observability/grafana/dashboards/backend-dashboard.json` - Backend service dashboard

#### IS-2: Backend Instrumentation Module

A new `backend/app/observability.py` module will be added containing:

- **OpenTelemetry Tracing Setup**: TracerProvider, OTLPSpanExporter, BatchSpanProcessor configured for Tempo
- **Prometheus Metrics**: Counter (`http_requests_total`), Histogram (`http_request_duration_seconds`), Gauge (`active_requests`)
- **FastAPI Instrumentation**: Automatic request tracing via `FastAPIInstrumentor`
- **Metrics Middleware**: HTTP middleware for collecting request metrics
- **`/metrics` Endpoint**: Prometheus-compatible metrics endpoint
- **Structured Logging**: Log format with trace context injection (`trace_id`, `span_id`)

**Python Dependencies to be added to `pyproject.toml` / `requirements.txt`:**
```
opentelemetry-api
opentelemetry-sdk
opentelemetry-exporter-otlp-proto-grpc
opentelemetry-instrumentation-fastapi
prometheus-client
```

#### IS-3: Cookiecutter Template Configuration

New template variables to be added to `cookiecutter.json`:

| Variable | Default | Description |
|----------|---------|-------------|
| `include_observability` | `"yes"` | Enable/disable observability stack |
| `grafana_port` | `"3000"` | Grafana dashboard port |
| `prometheus_port` | `"9090"` | Prometheus metrics port |
| `loki_port` | `"3100"` | Loki log aggregation port |
| `tempo_port` | `"3200"` | Tempo tracing port |
| `tempo_otlp_grpc_port` | `"4317"` | OTLP gRPC ingestion port |
| `tempo_otlp_http_port` | `"4318"` | OTLP HTTP ingestion port |

Conditional template rendering will be implemented using Jinja2 `{% if cookiecutter.include_observability == "yes" %}` blocks.

**Note: Template Precedent** - This will be the first use of `{% if %}` conditional patterns in the cookiecutter template. The implementation approach established here will serve as the precedent for future conditional features. Ensure clean, well-documented conditionals with clear indentation patterns.

#### IS-4: Pre-Built Grafana Dashboards

**Initial Release**: One pre-built dashboard ported from the source implementation:

1. **Backend Service Dashboard** - Request rate, latency percentiles, error rates, active requests (ported from `implementation-manager/observability/grafana/dashboards/backend-dashboard.json`)

**Future Work** (not in initial scope): The following dashboards may be added in subsequent iterations:
- SLO Overview Dashboard - Error budget, availability tracking, SLI visualization
- Log Explorer Dashboard - Quick access to common log queries with filters by service, severity
- Trace Explorer Dashboard - Service map, trace search, latency distribution

**Rationale**: The source implementation contains only the Backend Service Dashboard. Rather than creating new dashboards from scratch, we port what exists and is proven. Additional dashboards can be added incrementally based on user feedback.

#### IS-5: Documentation and Developer Experience

- **README Section**: Observability quick-start guide (service URLs, accessing dashboards, viewing logs/traces)
- **Inline Code Comments**: Explanatory comments in `observability.py`
- **Observability README**: Dedicated `observability/README.md` (ported from implementation-manager)
- **Environment Variables**: Documentation of all observability-related environment variables

#### IS-6: Data Correlation Configuration

- Tempo-to-Loki correlation via `tracesToLogsV2` configuration
- Tempo-to-Prometheus correlation via `tracesToMetrics` configuration
- Service map visualization via Tempo node graph

---

### Out of Scope

#### OOS-1: Frontend Observability Instrumentation

While the implementation-manager includes frontend (Lit/TypeScript) instrumentation with OpenTelemetry Web SDK, this feature is **explicitly out of scope** for the initial integration:

- Frontend tracing initialization
- Fetch/XHR automatic instrumentation
- User interaction tracking
- Document load performance metrics
- Console log enrichment with trace context

**Rationale**: Frontend observability adds significant complexity (bundle size, CORS configuration for OTLP exports, browser compatibility) and is better suited for a follow-up feature once backend observability is stable.

**Future Feature Candidate**: `frontend-observability-instrumentation`

#### OOS-2: Alerting and Alert Manager

The following alerting capabilities are not included in this scope:

- Prometheus Alertmanager integration
- Alert rules configuration
- PagerDuty, Slack, or email notification integrations
- On-call routing and escalation policies

**Rationale**: Alerting is highly organization-specific and requires operational maturity. The template should provide the metrics and dashboards that enable alerting, but the alerting configuration itself should be a separate concern.

**Future Feature Candidate**: `alerting-infrastructure`

#### OOS-3: Production Deployment Configurations

The following production-specific configurations are not included:

- Kubernetes/Helm chart configurations for observability services
- High-availability Prometheus (Thanos, Cortex)
- Loki clustering and replication
- Tempo distributed mode
- TLS/mTLS configuration between observability services
- Cloud-native observability alternatives (AWS CloudWatch, GCP Cloud Operations, Azure Monitor)

**Rationale**: Production deployment patterns vary significantly by organization and infrastructure. The template provides a development-ready stack that can inform production architecture decisions.

**Guidance Provided**: Documentation will include a "Production Considerations" section outlining scaling and security recommendations.

#### OOS-4: Application Performance Management (APM) Features

Advanced APM features are not in scope:

- Automatic error tracking and grouping (like Sentry)
- Performance profiling (CPU, memory analysis)
- Database query analysis and N+1 detection
- External service dependency mapping beyond basic tracing
- Real User Monitoring (RUM)

**Rationale**: These features typically require dedicated APM platforms or significant additional instrumentation beyond basic observability.

#### OOS-5: Custom Metrics Beyond HTTP

The initial integration will focus on HTTP request metrics. The following are not automatically instrumented:

- Database query metrics (query count, latency by table)
- Redis operation metrics
- Background job metrics (if Celery/RQ is added later)
- Custom business metrics

**Rationale**: Custom metrics are application-specific. The template provides the foundation (`prometheus_client` integration) for developers to add their own metrics.

**Documentation**: Examples of adding custom metrics will be included in `observability/README.md`.

#### OOS-6: Log Parsing and Structured Fields

Advanced log processing is not in scope:

- Custom Promtail pipelines for parsing application-specific log formats
- Log field extraction beyond default Docker log labels
- Log-based metrics generation

**Rationale**: Log parsing requirements are application-specific. The default configuration captures all container logs which is sufficient for most use cases.

#### OOS-7: Keycloak Metrics Scraping Modifications

While Prometheus will be configured to scrape Keycloak metrics (as in implementation-manager), the following are not in scope:

- Keycloak metrics SPI configuration
- Custom Keycloak dashboards
- Keycloak-specific alerting

**Rationale**: Keycloak in development mode exposes limited metrics. Production Keycloak observability requires additional Keycloak configuration that is better addressed separately.

---

### Phase Boundaries

This feature will be implemented in distinct phases with clear boundaries:

| Phase | Scope | Deliverables |
|-------|-------|--------------|
| **Phase 1** | Infrastructure | Docker Compose observability services, configuration files, volume mounts |
| **Phase 2** | Backend Integration | `observability.py` module, dependency additions, main.py integration |
| **Phase 3** | Dashboards & Datasources | Grafana provisioning, dashboard JSON, datasource configuration |
| **Phase 4** | Template Conditionals | `include_observability` toggle, conditional rendering, cookiecutter.json updates |
| **Phase 5** | Documentation & Testing | README updates, observability documentation, validation tests |

Each phase should be independently testable and mergeable.

---

### Related Features (Separate Concerns)

The following are related but distinct features that should not be conflated with this work:

| Feature | Relationship | Status |
|---------|-------------|--------|
| **Distributed Tracing Headers** | Prerequisite: W3C Trace Context propagation in HTTP clients | Already present in implementation-manager |
| **Health Check Enhancement** | Adjacent: Health endpoints could expose Prometheus metrics | Existing health endpoints sufficient |
| **Logging Standardization** | Prerequisite: Structured JSON logging for better Loki queries | Can be addressed in parallel |
| **API Rate Limit Metrics** | Extension: Expose rate limiting counters to Prometheus | Future enhancement |
| **Database Connection Pool Metrics** | Extension: SQLAlchemy connection pool observability | Future enhancement |

---

### Boundary Validation Checklist

Before implementation begins, confirm the following boundaries are understood:

- [ ] Observability stack is **opt-in** via `include_observability` template variable
- [ ] Only **backend** Python code is instrumented; no frontend changes
- [ ] **Development-focused** configuration; production guidance is documentation-only
- [ ] **Five core services** (Prometheus, Loki, Promtail, Tempo, Grafana); no Alertmanager
- [ ] **One dashboard** (Backend Service) included initially; additional dashboards are future work
- [ ] **HTTP metrics only**; database/cache/background job metrics are user responsibility
- [ ] **Grafana anonymous access** enabled for development; production auth is user responsibility

---

## User Stories / Use Cases

This section defines the key user personas and their interaction scenarios with the observability stack. Each user story includes acceptance criteria to ensure the implementation meets user needs.

### User Personas

#### P1: Application Developer

A developer working on the generated project who writes features, fixes bugs, and needs to understand system behavior during development. They are the primary user of observability during the development cycle.

**Characteristics:**
- Works primarily with IDE and terminal
- May not have deep observability experience
- Needs quick feedback during development iterations
- Values simplicity over advanced features

#### P2: DevOps/Platform Engineer

An engineer responsible for deploying, configuring, and maintaining the application infrastructure. They need to ensure the observability stack is properly configured and integrated into CI/CD pipelines.

**Characteristics:**
- Comfortable with infrastructure-as-code
- Responsible for production deployment
- Needs to customize configurations for different environments
- Values consistency and automation

#### P3: On-Call Engineer

An engineer responding to production incidents who needs to quickly identify, diagnose, and resolve issues. They rely heavily on observability data for incident response.

**Characteristics:**
- May be investigating unfamiliar code paths
- Under time pressure during incidents
- Needs correlated data (metrics, logs, traces)
- Values speed of diagnosis over comprehensive analysis

#### P4: Technical Lead / SRE

A senior engineer responsible for defining Service Level Objectives (SLOs) and ensuring the system meets reliability targets. They need to track long-term trends and identify systemic issues.

**Characteristics:**
- Focuses on reliability and performance trends
- Defines and monitors SLOs
- Reviews architectural decisions
- Values data-driven decision making

#### P5: Template Consumer (New Project Creator)

A developer using the cookiecutter template to generate a new project. They need observability to "just work" without extensive configuration.

**Characteristics:**
- Generating a new project from the template
- May be unfamiliar with the observability stack
- Expects sensible defaults
- Needs clear documentation for customization

---

### User Stories

#### US-001: Viewing Real-Time Application Metrics

**As a** Application Developer (P1)
**I want to** view real-time metrics about my application's request rate, latency, and error rate
**So that** I can understand how my code changes affect performance

**Acceptance Criteria:**
1. After running `docker compose up`, I can access Grafana at `localhost:3000` without authentication
2. A pre-built "Backend Service Dashboard" is available in the dashboards list
3. The dashboard shows request rate by endpoint within 2 minutes of application activity
4. The dashboard shows latency percentiles (p95, p99) updated in near real-time (< 15 second delay)
5. The dashboard shows error rates separated by 4xx and 5xx status codes
6. The dashboard auto-refreshes every 10 seconds

**Scenario:**
```gherkin
Given the observability stack is running
And the backend has received HTTP requests
When I open Grafana and navigate to the Backend Service Dashboard
Then I see current request rate, latency percentiles, and error rates
And the data updates automatically without manual refresh
```

---

#### US-002: Debugging a Slow API Endpoint

**As a** Application Developer (P1)
**I want to** trace a slow API request to understand where time is being spent
**So that** I can identify and fix performance bottlenecks

**Acceptance Criteria:**
1. I can access the Grafana Explore view with Tempo datasource
2. I can search for traces by service name, duration, or time range
3. Clicking on a trace shows a flame graph visualization
4. Each span in the trace shows duration, service name, and operation name
5. I can expand spans to see attributes (HTTP method, path, status code)
6. The trace includes automatic instrumentation spans from FastAPI

**Scenario:**
```gherkin
Given I have made a slow API request to /api/v1/todos
When I navigate to Grafana Explore and select Tempo datasource
And I search for traces with duration > 500ms
Then I find the trace for my slow request
And I can see which operations took the most time
And I can identify database queries, external calls, or processing delays
```

---

#### US-003: Investigating Application Errors

**As an** On-Call Engineer (P3)
**I want to** quickly find error logs and correlate them with the request trace
**So that** I can diagnose and resolve production issues faster

**Acceptance Criteria:**
1. Error logs are automatically aggregated in Loki
2. Logs include trace_id and span_id for correlation
3. I can filter logs by severity level (ERROR, WARNING)
4. I can filter logs by service name or container
5. From a trace in Tempo, I can jump directly to related logs
6. From a log entry with trace_id, I can navigate to the full trace

**Scenario:**
```gherkin
Given an application error has occurred with trace_id "abc123"
When I search in Grafana Loki for logs containing "abc123"
Then I find the error log entries with stack traces
And I can click a link to view the full distributed trace
And I can see what operations occurred before the error
```

---

#### US-004: Monitoring Service Level Indicators

**As a** Technical Lead / SRE (P4)
**I want to** view dashboards showing key SLIs (latency, error rate, availability)
**So that** I can track whether we are meeting our SLO targets

**Acceptance Criteria:**
1. A pre-built SLO Dashboard is available in Grafana
2. The dashboard shows availability percentage (successful requests / total requests)
3. The dashboard shows p95 and p99 latency against configurable targets
4. The dashboard shows error budget remaining and burn rate
5. Time ranges can be adjusted (1h, 24h, 7d, 30d)
6. The dashboard supports filtering by endpoint or operation

**Scenario:**
```gherkin
Given the application has been running for 24 hours
When I open the SLO Overview Dashboard in Grafana
Then I see current availability percentage
And I see whether p95 latency is within the 500ms target
And I see how much error budget remains for the month
And I can identify endpoints that are not meeting SLO targets
```

---

#### US-005: Generating a Project with Observability

**As a** Template Consumer (P5)
**I want to** generate a new project with observability included by default
**So that** I have monitoring capabilities from day one

**Acceptance Criteria:**
1. When running cookiecutter, I am prompted whether to include observability
2. If I answer "yes", all observability services are added to `compose.yml`
3. The backend includes the `observability.py` module with full instrumentation
4. `pyproject.toml` includes all required OpenTelemetry dependencies
5. Pre-configured Grafana datasources and dashboards are included
6. The generated README includes an "Observability" section

**Scenario:**
```gherkin
Given I am generating a new project from the template
When I run `cookiecutter project-starter`
And I answer "yes" to include_observability
Then the generated project includes:
  | observability/prometheus/prometheus.yml |
  | observability/loki/loki-config.yml |
  | observability/promtail/promtail-config.yml |
  | observability/tempo/tempo.yml |
  | observability/grafana/datasources/datasources.yml |
  | observability/grafana/dashboards/* |
  | backend/app/observability.py |
And compose.yml includes prometheus, loki, promtail, tempo, grafana services
And the backend depends on observability services
```

---

#### US-006: Generating a Project without Observability

**As a** Template Consumer (P5)
**I want to** generate a project without the observability stack
**So that** I can minimize resource usage when observability is not needed

**Acceptance Criteria:**
1. When I answer "no" to include_observability, no observability services are included
2. The `compose.yml` does not include prometheus, loki, promtail, tempo, or grafana
3. The backend does not include `observability.py`
4. No observability-related dependencies are added to `pyproject.toml`
5. The application starts and runs without observability errors
6. The README does not include the Observability section

**Scenario:**
```gherkin
Given I am generating a new project from the template
When I run `cookiecutter project-starter`
And I answer "no" to include_observability
Then the generated project does NOT include the observability/ directory
And compose.yml does NOT include observability services
And the backend starts without observability initialization
And docker compose up starts only core services (backend, frontend, postgres, redis, keycloak)
```

---

#### US-007: Viewing Logs Across All Services

**As a** Application Developer (P1)
**I want to** view aggregated logs from all Docker containers in one place
**So that** I do not need to run `docker compose logs` for each service

**Acceptance Criteria:**
1. Logs from all containers are automatically collected by Promtail
2. Logs are searchable in Grafana via Loki datasource
3. I can filter logs by container name (backend, frontend, keycloak, postgres, redis)
4. I can filter logs by log level when available
5. Logs appear in Loki within 5 seconds of being written
6. Log entries preserve original formatting and line structure

**Scenario:**
```gherkin
Given multiple services are running and generating logs
When I open Grafana Explore and select Loki datasource
And I run the query {container=~"backend|keycloak"}
Then I see interleaved logs from both services
And logs are sorted by timestamp
And I can see which container each log entry came from
```

---

#### US-008: Adding Custom Metrics to Application Code

**As a** Application Developer (P1)
**I want to** add custom metrics to my application code (e.g., business metrics)
**So that** I can monitor application-specific behaviors

**Acceptance Criteria:**
1. The `observability.py` module provides examples of Counter, Histogram, and Gauge usage
2. I can import `prometheus_client` and create new metrics
3. Custom metrics appear at the `/metrics` endpoint
4. Custom metrics are scraped by Prometheus within 15 seconds
5. I can query custom metrics in Grafana
6. Documentation includes examples of common custom metric patterns

**Scenario:**
```gherkin
Given I want to track the number of user registrations
When I add a Counter metric "user_registrations_total" to my code
And increment it when a user registers
Then the metric appears at localhost:8000/metrics
And I can query it in Grafana: user_registrations_total
And I can create a dashboard panel showing registration rate over time
```

---

#### US-009: Tracing Requests Across Service Boundaries

**As an** On-Call Engineer (P3)
**I want to** see a complete trace of a request that spans multiple services
**So that** I can understand cross-service interactions and identify where failures occur

**Acceptance Criteria:**
1. The W3C Trace Context (traceparent header) is propagated between services
2. Traces show spans from the frontend through the backend
3. External HTTP calls made by the backend include trace context
4. The trace visualizes the parent-child relationship between spans
5. Service boundaries are clearly visible in the trace view
6. Total request time and time per service are displayed

**Scenario:**
```gherkin
Given the frontend makes an API call to the backend
And the backend makes an external HTTP call
When I search for the trace by trace_id
Then I see spans from frontend, backend, and external call
And the trace shows the timeline of each span
And I can see which service took the most time
And parent-child relationships are correctly displayed
```

---

#### US-010: Configuring Observability for Different Environments

**As a** DevOps/Platform Engineer (P2)
**I want to** customize observability configuration for different environments (dev, staging, prod)
**So that** I can adjust retention, sampling, and security settings appropriately

**Acceptance Criteria:**
1. Environment variables can override key configuration values (endpoints, retention)
2. Prometheus scrape interval is configurable via environment variable
3. OTEL endpoint is configurable via `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable
4. Loki retention period can be adjusted in configuration
5. Grafana can be configured to require authentication via environment variable
6. Documentation explains production configuration recommendations

**Scenario:**
```gherkin
Given I am deploying to a staging environment
When I set environment variables:
  | OTEL_EXPORTER_OTLP_ENDPOINT | http://tempo-staging:4317 |
  | GRAFANA_ADMIN_PASSWORD | secure-password |
  | PROMETHEUS_RETENTION_TIME | 15d |
Then the backend exports traces to the staging Tempo instance
And Grafana requires authentication to access
And Prometheus retains metrics for 15 days
```

---

#### US-011: Accessing Metrics Endpoint Directly

**As a** DevOps/Platform Engineer (P2)
**I want to** access the Prometheus metrics endpoint directly
**So that** I can integrate with external monitoring systems or validate metrics

**Acceptance Criteria:**
1. The backend exposes a `/metrics` endpoint
2. The endpoint returns Prometheus text format
3. All instrumented metrics are present (http_requests_total, http_request_duration_seconds, active_requests)
4. The endpoint is accessible without authentication
5. The endpoint responds within 100ms
6. The endpoint includes metric help text and type annotations

**Scenario:**
```gherkin
Given the backend is running
When I make a GET request to localhost:8000/metrics
Then I receive a 200 response with Content-Type text/plain
And the response includes http_requests_total metric
And the response includes http_request_duration_seconds_bucket histogram buckets
And the response includes HELP and TYPE annotations
```

---

#### US-012: Identifying Active Requests During Load

**As an** On-Call Engineer (P3)
**I want to** see how many requests are currently being processed
**So that** I can understand system load and identify potential saturation

**Acceptance Criteria:**
1. The `active_requests` gauge tracks concurrent request count
2. The metric increments when a request starts
3. The metric decrements when a request completes (success or failure)
4. The Backend Dashboard shows current active requests
5. Historical active request data is available in Grafana
6. Unusual spikes in active requests are visually apparent

**Scenario:**
```gherkin
Given the application is under load
When I view the Backend Service Dashboard
Then I see a gauge showing current active request count
And the count increases when new requests arrive
And the count decreases when requests complete
And I can see historical patterns to identify unusual load
```

---

### Edge Cases and Error Conditions

#### EC-001: Observability Stack Partially Available

**Scenario:** One observability service (e.g., Tempo) fails to start, but others are healthy.

**Expected Behavior:**
- The backend should continue to function normally
- Metrics collection to Prometheus should continue
- Log aggregation to Loki should continue
- Traces will not be recorded, but no application errors occur
- OpenTelemetry exporter logs a warning about failed connection

---

#### EC-002: High Cardinality Metrics

**Scenario:** Application exposes metrics with high cardinality labels (e.g., user_id in every metric).

**Expected Behavior:**
- Default instrumentation uses bounded cardinality (method, endpoint, status)
- Documentation warns against high cardinality patterns
- Prometheus may slow down but does not crash
- Grafana queries may timeout for high-cardinality queries

---

#### EC-003: Large Log Volume

**Scenario:** Application generates excessive logs (DEBUG level enabled, high traffic).

**Expected Behavior:**
- Promtail continues collecting logs
- Loki applies configured retention limits
- Old logs are automatically deleted per retention policy
- No disk space exhaustion due to unbounded log growth
- Log queries remain responsive within configured limits

---

#### EC-004: Trace Context Missing

**Scenario:** A request arrives without trace context headers.

**Expected Behavior:**
- OpenTelemetry generates a new trace_id
- The request is still traced from the point of entry
- No errors or exceptions are raised
- Logs include the newly generated trace_id

---

#### EC-005: Network Partition Between Services

**Scenario:** Network connectivity between backend and Tempo is lost.

**Expected Behavior:**
- Backend continues to handle requests normally
- Spans are buffered in memory by BatchSpanProcessor
- When connectivity is restored, buffered spans are exported
- If buffer overflows, oldest spans are dropped (not application errors)
- Backend logs warning about export failures

---

### User Journey Flows

#### Journey 1: Developer Debugging a New Feature

```
1. Developer adds new API endpoint
2. Developer runs `docker compose up`
3. Developer tests endpoint via curl or frontend
4. Developer notices slow response time
5. Developer opens Grafana -> Backend Dashboard
6. Developer sees elevated p95 latency for new endpoint
7. Developer navigates to Explore -> Tempo
8. Developer searches for traces on the new endpoint path
9. Developer finds slow trace, identifies database query as bottleneck
10. Developer optimizes query, re-tests, sees improved latency
```

#### Journey 2: On-Call Engineer Responding to Alert

```
1. Engineer receives alert about elevated error rate
2. Engineer opens Grafana -> Backend Dashboard
3. Engineer sees spike in 5xx errors starting 10 minutes ago
4. Engineer filters error rate by endpoint, identifies /api/v1/oauth/token
5. Engineer navigates to Explore -> Loki
6. Engineer queries {container="backend"} |= "ERROR"
7. Engineer finds error logs with "connection refused" to Keycloak
8. Engineer checks Keycloak container, finds it crashed
9. Engineer restarts Keycloak, error rate returns to normal
10. Engineer documents incident with trace_id and timestamps
```

#### Journey 3: SRE Establishing SLOs

```
1. SRE reviews baseline metrics over past week
2. SRE opens Grafana -> SLO Dashboard
3. SRE identifies current p95 latency is 320ms
4. SRE sets initial SLO: 99.5% of requests < 500ms
5. SRE configures error budget visualization (0.5% error budget)
6. SRE creates custom dashboard panel for burn rate
7. SRE documents SLO definitions in project wiki
8. Team reviews and approves SLO targets
9. Future: SRE configures alerting based on burn rate (out of scope)
```

---

### Summary Table: User Stories by Persona

| User Story | P1: Developer | P2: DevOps | P3: On-Call | P4: SRE | P5: Consumer |
|------------|:-------------:|:----------:|:-----------:|:-------:|:------------:|
| US-001: View Metrics | Primary | - | Secondary | Secondary | - |
| US-002: Debug Slow Endpoint | Primary | - | Secondary | - | - |
| US-003: Investigate Errors | Secondary | - | Primary | - | - |
| US-004: Monitor SLIs | - | - | Secondary | Primary | - |
| US-005: Generate with Observability | Secondary | Primary | - | - | Primary |
| US-006: Generate without Observability | - | Secondary | - | - | Primary |
| US-007: View Aggregated Logs | Primary | Secondary | Primary | - | - |
| US-008: Add Custom Metrics | Primary | - | - | Secondary | - |
| US-009: Trace Across Services | Secondary | - | Primary | Secondary | - |
| US-010: Configure for Environments | - | Primary | - | Secondary | - |
| US-011: Access Metrics Endpoint | Secondary | Primary | - | - | - |
| US-012: Identify Active Requests | Secondary | - | Primary | Primary | - |

---

## Functional Requirements

This section defines the specific functional requirements for the observability stack integration. Requirements are organized by category and prioritized using the MoSCoW method (Must Have, Should Have, Could Have, Won't Have). Each requirement is atomic, testable, and traceable to the user stories defined above.

### Requirement Categories

| Category | Code Prefix | Description |
|----------|-------------|-------------|
| Template Configuration | FR-TC | Cookiecutter template configuration and generation |
| Infrastructure Services | FR-IS | Docker Compose observability services |
| Backend Instrumentation | FR-BI | Python/FastAPI observability code |
| Metrics Collection | FR-MC | Prometheus metrics and scraping |
| Logging Aggregation | FR-LA | Loki and Promtail log collection |
| Distributed Tracing | FR-DT | Tempo and OpenTelemetry tracing |
| Visualization | FR-VZ | Grafana dashboards and datasources |
| Data Correlation | FR-DC | Cross-signal correlation capabilities |

---

### Template Configuration Requirements

#### FR-TC-001: Observability Toggle Configuration Variable (Must Have)

**Description**: The cookiecutter template shall include an `include_observability` configuration variable that controls whether the observability stack is generated.

**Acceptance Criteria**:
1. `cookiecutter.json` includes `"include_observability": "yes"` as default
2. Valid values are `"yes"` and `"no"` (case-insensitive)
3. The variable is prompted during interactive template generation
4. The variable description is clear: "Include observability stack (Prometheus, Loki, Tempo, Grafana)? [yes/no]"

**Traceability**: US-005, US-006

---

#### FR-TC-002: Observability Port Configuration Variables (Should Have)

**Description**: The cookiecutter template shall include configuration variables for all observability service ports to avoid conflicts with existing services.

**Acceptance Criteria**:
1. Template includes the following port variables with defaults:
   - `grafana_port`: `"3000"`
   - `prometheus_port`: `"9090"`
   - `loki_port`: `"3100"`
   - `tempo_http_port`: `"3200"`
   - `tempo_otlp_grpc_port`: `"4317"`
   - `tempo_otlp_http_port`: `"4318"`
2. Port values are validated as numeric strings in the range 1024-65535
3. Port variables are only prompted when `include_observability` is `"yes"`

**Traceability**: US-005, US-010

---

#### FR-TC-003: Conditional Template Rendering (Must Have)

**Description**: All observability-related files and configurations shall be conditionally rendered based on the `include_observability` variable.

**Acceptance Criteria**:
1. When `include_observability` is `"no"`:
   - The `observability/` directory is not created
   - No observability services are included in `compose.yml`
   - `backend/app/observability.py` is not created
   - No observability dependencies are added to `pyproject.toml`
   - README does not include observability documentation
2. When `include_observability` is `"yes"`:
   - All observability files and services are generated
   - Backend includes observability initialization
   - README includes observability quick-start guide

**Traceability**: US-005, US-006

---

#### FR-TC-004: Observability Directory Structure (Must Have)

**Description**: When observability is enabled, the template shall generate a standardized directory structure for configuration files.

**Acceptance Criteria**:
1. The following directory structure is created:
   ```
   observability/
   +-- prometheus/
   |   +-- prometheus.yml
   +-- loki/
   |   +-- loki-config.yml
   +-- promtail/
   |   +-- promtail-config.yml
   +-- tempo/
   |   +-- tempo.yml
   +-- grafana/
       +-- datasources/
       |   +-- datasources.yml
       +-- dashboards/
           +-- dashboards.yml
           +-- backend-dashboard.json
           +-- slo-dashboard.json
           +-- log-explorer-dashboard.json
           +-- trace-explorer-dashboard.json
   ```
2. All configuration files are syntactically valid YAML/JSON
3. All files include inline comments explaining key configuration options

**Traceability**: US-005, IS-1

---

### Infrastructure Services Requirements

#### FR-IS-001: Prometheus Service Definition (Must Have)

**Description**: The generated `compose.yml` shall include a properly configured Prometheus service for metrics collection and storage.

**Acceptance Criteria**:
1. Service uses `prom/prometheus:latest` image
2. Container name follows project naming convention: `{{ cookiecutter.project_slug }}-prometheus`
3. Port `{{ cookiecutter.prometheus_port }}:9090` is exposed
4. Configuration file is mounted at `/etc/prometheus/prometheus.yml`
5. Persistent volume is mounted at `/prometheus` for data retention
6. Command includes standard Prometheus flags for web UI and storage
7. Service has `restart: unless-stopped` policy
8. Service is included only when `include_observability` is `"yes"`

**Traceability**: US-005, IS-1

---

#### FR-IS-002: Loki Service Definition (Must Have)

**Description**: The generated `compose.yml` shall include a properly configured Loki service for log aggregation and storage.

**Acceptance Criteria**:
1. Service uses `grafana/loki:latest` image
2. Container name follows project naming convention: `{{ cookiecutter.project_slug }}-loki`
3. Port `{{ cookiecutter.loki_port }}:3100` is exposed
4. Configuration file is mounted at `/etc/loki/local-config.yaml`
5. Persistent volume is mounted at `/loki` for log storage
6. Command includes config file flag: `-config.file=/etc/loki/local-config.yaml`
7. Service has `restart: unless-stopped` policy

**Traceability**: US-005, US-007, IS-1

---

#### FR-IS-003: Promtail Service Definition (Must Have)

**Description**: The generated `compose.yml` shall include a properly configured Promtail service for Docker container log collection.

**Acceptance Criteria**:
1. Service uses `grafana/promtail:latest` image
2. Container name follows project naming convention: `{{ cookiecutter.project_slug }}-promtail`
3. Configuration file is mounted at `/etc/promtail/promtail-config.yml`
4. Docker socket is mounted: `/var/run/docker.sock:/var/run/docker.sock`
5. Docker container logs are mounted: `/var/lib/docker/containers:/var/lib/docker/containers:ro`
6. Command includes config file flag: `-config.file=/etc/promtail/promtail-config.yml`
7. Service depends on `loki` service
8. Service has `restart: unless-stopped` policy

**Traceability**: US-007, IS-1

---

#### FR-IS-004: Tempo Service Definition (Must Have)

**Description**: The generated `compose.yml` shall include a properly configured Tempo service for distributed trace storage.

**Acceptance Criteria**:
1. Service uses `grafana/tempo:latest` image
2. Container name follows project naming convention: `{{ cookiecutter.project_slug }}-tempo`
3. The following ports are exposed:
   - `{{ cookiecutter.tempo_http_port }}:3200` (Tempo HTTP API)
   - `{{ cookiecutter.tempo_otlp_grpc_port }}:4317` (OTLP gRPC receiver)
   - `{{ cookiecutter.tempo_otlp_http_port }}:4318` (OTLP HTTP receiver)
4. Configuration file is mounted at `/etc/tempo.yaml`
5. Persistent volume is mounted at `/tmp/tempo` for trace storage
6. Command includes config file flag: `-config.file=/etc/tempo.yaml`
7. Service has `restart: unless-stopped` policy

**Traceability**: US-002, US-009, IS-1

---

#### FR-IS-005: Grafana Service Definition (Must Have)

**Description**: The generated `compose.yml` shall include a properly configured Grafana service for visualization.

**Acceptance Criteria**:
1. Service uses `grafana/grafana:latest` image
2. Container name follows project naming convention: `{{ cookiecutter.project_slug }}-grafana`
3. Port `{{ cookiecutter.grafana_port }}:3000` is exposed
4. Datasources provisioning directory is mounted at `/etc/grafana/provisioning/datasources`
5. Dashboards provisioning directory is mounted at `/etc/grafana/provisioning/dashboards`
6. Persistent volume is mounted at `/var/lib/grafana`
7. Environment variables enable anonymous access for development:
   - `GF_AUTH_ANONYMOUS_ENABLED=true`
   - `GF_AUTH_ANONYMOUS_ORG_ROLE=Admin`
   - `GF_AUTH_DISABLE_LOGIN_FORM=true`
8. Service depends on `prometheus`, `loki`, and `tempo` services
9. Service has `restart: unless-stopped` policy

**Traceability**: US-001, US-004, US-005, IS-1

---

#### FR-IS-006: Volume Definitions for Observability (Must Have)

**Description**: The generated `compose.yml` shall include named volumes for all observability services requiring persistent storage.

**Acceptance Criteria**:
1. The following volumes are defined:
   - `prometheus-data` or `{{ cookiecutter.project_slug }}-prometheus-data`
   - `loki-data` or `{{ cookiecutter.project_slug }}-loki-data`
   - `tempo-data` or `{{ cookiecutter.project_slug }}-tempo-data`
   - `grafana-data` or `{{ cookiecutter.project_slug }}-grafana-data`
2. Volume definitions are only included when `include_observability` is `"yes"`

**Traceability**: IS-1

---

#### FR-IS-007: Service Dependencies Configuration (Must Have)

**Description**: Observability service dependencies shall be configured to ensure proper startup order.

**Acceptance Criteria**:
1. `promtail` depends on `loki` (log sink must be available)
2. `grafana` depends on `prometheus`, `loki`, and `tempo` (datasources must be available)
3. Backend service includes `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable pointing to Tempo when observability is enabled

**Traceability**: IS-1

---

### Backend Instrumentation Requirements

#### FR-BI-001: Observability Module Creation (Must Have)

**Description**: The template shall generate a `backend/app/observability.py` module containing all observability initialization and instrumentation code.

**Acceptance Criteria**:
1. Module file is created at `backend/app/observability.py`
2. Module is only created when `include_observability` is `"yes"`
3. Module includes comprehensive inline documentation explaining each component
4. Module follows existing codebase patterns for imports and structure

**Traceability**: US-005, IS-2

---

#### FR-BI-002: OpenTelemetry Tracer Configuration (Must Have)

**Description**: The observability module shall configure OpenTelemetry tracing with OTLP export to Tempo.

**Acceptance Criteria**:
1. `TracerProvider` is created with service name from `OTEL_SERVICE_NAME` environment variable (default: `"backend"`)
2. `OTLPSpanExporter` is configured with endpoint from `OTEL_EXPORTER_OTLP_ENDPOINT` environment variable (default: `"http://tempo:4317"`)
3. `BatchSpanProcessor` is used for efficient span export
4. Exporter uses insecure connection for development (TLS disabled)
5. Resource attributes include `service.name` following OpenTelemetry semantic conventions

**Traceability**: US-002, US-009, IS-2

---

#### FR-BI-003: FastAPI Automatic Instrumentation (Must Have)

**Description**: The observability module shall automatically instrument FastAPI using OpenTelemetry's FastAPIInstrumentor.

**Acceptance Criteria**:
1. `FastAPIInstrumentor.instrument_app(app)` is called during observability setup
2. All HTTP requests automatically generate trace spans
3. Spans include HTTP method, URL path, status code, and other standard attributes
4. Instrumentation follows OpenTelemetry semantic conventions for HTTP

**Traceability**: US-002, IS-2

---

#### FR-BI-004: Prometheus Metrics Definitions (Must Have)

**Description**: The observability module shall define standard HTTP metrics using the prometheus-client library.

**Acceptance Criteria**:
1. `http_requests_total` Counter metric with labels: `method`, `endpoint`, `status`
2. `http_request_duration_seconds` Histogram metric with labels: `method`, `endpoint`
3. `active_requests` Gauge metric (no labels)
4. All metrics include descriptive HELP text
5. Histogram uses default buckets suitable for web request durations

**Traceability**: US-001, US-008, US-012, IS-2

---

#### FR-BI-005: Metrics Collection Middleware (Must Have)

**Description**: The observability module shall include HTTP middleware that collects metrics for every request.

**Acceptance Criteria**:
1. Middleware increments `active_requests` at request start
2. Middleware decrements `active_requests` at request completion (success or failure)
3. Middleware observes request duration in `http_request_duration_seconds` histogram
4. Middleware increments `http_requests_total` with method, endpoint, and status labels
5. Middleware does not modify request or response content
6. Middleware handles exceptions gracefully (still records metrics)

**Traceability**: US-001, US-012, IS-2

---

#### FR-BI-006: Prometheus Metrics Endpoint (Must Have)

**Description**: The backend shall expose a `/metrics` endpoint for Prometheus scraping.

**Acceptance Criteria**:
1. Endpoint is accessible at `GET /metrics`
2. Response Content-Type is `text/plain; version=0.0.4; charset=utf-8` (Prometheus exposition format)
3. Response includes all defined metrics with current values
4. Response includes HELP and TYPE annotations for each metric
5. Endpoint responds within 100ms under normal conditions
6. Endpoint does not require authentication

**Traceability**: US-011, IS-2

---

#### FR-BI-007: Structured Logging with Trace Context (Should Have)

**Description**: The observability module shall configure structured logging that includes trace context for log correlation.

**Acceptance Criteria**:
1. Log format includes `trace_id` and `span_id` fields when available
2. Log format is human-readable in development (not JSON)
3. Logs without active trace context omit trace fields (no empty values)
4. Test mode (TESTING=true environment variable) uses simplified format without trace context
5. Log level is configurable via environment variable (default: INFO)

**Traceability**: US-003, IS-2

---

#### FR-BI-008: Observability Setup Function (Must Have)

**Description**: The observability module shall provide a `setup_observability(app)` function that initializes all observability components.

**Acceptance Criteria**:
1. Function accepts a FastAPI application instance
2. Function instruments the application with OpenTelemetry
3. Function registers the metrics middleware
4. Function registers the `/metrics` endpoint
5. Function logs a confirmation message on successful setup
6. Function is idempotent (safe to call multiple times)
7. Function returns the instrumented application instance

**Traceability**: IS-2

---

#### FR-BI-009: Observability Python Dependencies (Must Have)

**Description**: The template shall include all required Python dependencies for observability in the generated `pyproject.toml`.

**Acceptance Criteria**:
1. The following dependencies are added when `include_observability` is `"yes"`:
   - `opentelemetry-api`
   - `opentelemetry-sdk`
   - `opentelemetry-exporter-otlp-proto-grpc`
   - `opentelemetry-instrumentation-fastapi`
   - `prometheus-client`
2. Dependencies use compatible version constraints (e.g., `>=1.0.0,<2.0.0`)
3. Dependencies are not added when `include_observability` is `"no"`

**Traceability**: IS-2

---

#### FR-BI-010: Main Application Integration (Must Have)

**Description**: The generated `main.py` shall conditionally import and initialize observability.

**Acceptance Criteria**:
1. Import statement for `observability` module is included when observability is enabled
2. `setup_observability(app)` is called after application initialization
3. Observability setup occurs before other middleware registration
4. No observability-related code is present when `include_observability` is `"no"`

**Traceability**: IS-2

---

### Metrics Collection Requirements

#### FR-MC-001: Prometheus Scrape Configuration (Must Have)

**Description**: The Prometheus configuration shall include scrape jobs for all relevant services.

**Acceptance Criteria**:
1. Prometheus configuration file (`prometheus.yml`) includes the following scrape jobs:
   - `prometheus` (self-monitoring at `localhost:9090`)
   - `backend` (application metrics at `backend:8000/metrics`)
   - `keycloak` (Keycloak metrics at `keycloak:8080/metrics`)
   - `tempo` (Tempo metrics at `tempo:3200/metrics`)
   - `loki` (Loki metrics at `loki:3100/metrics`)
2. Backend scrape job uses 5-second interval for responsive dashboards
3. Other jobs use 15-second default interval
4. All jobs use correct `metrics_path` for each service

**Traceability**: US-001, IS-1

---

#### FR-MC-002: Prometheus Global Configuration (Must Have)

**Description**: Prometheus shall be configured with appropriate global settings for development use.

**Acceptance Criteria**:
1. Global scrape interval is 15 seconds (configurable)
2. Global evaluation interval is 15 seconds
3. External labels include project/cluster identifier
4. Configuration uses YAML format with comments

**Traceability**: IS-1

---

#### FR-MC-003: Prometheus Data Retention (Should Have)

**Description**: Prometheus shall be configured with appropriate data retention for development use.

**Acceptance Criteria**:
1. Default retention time is appropriate for development (e.g., 15 days)
2. Retention is configurable via Docker Compose environment variable or command flag
3. Storage path uses persistent volume to survive container restarts

**Traceability**: IS-1

---

### Logging Aggregation Requirements

#### FR-LA-001: Loki Storage Configuration (Must Have)

**Description**: Loki shall be configured for local filesystem storage suitable for development.

**Acceptance Criteria**:
1. Storage uses filesystem backend (not S3 or GCS)
2. Chunks directory is configured at `/loki/chunks`
3. Rules directory is configured at `/loki/rules`
4. Schema uses latest stable version (v13 or newer)
5. Auth is disabled for development (`auth_enabled: false`)
6. Analytics reporting is disabled

**Traceability**: IS-1

---

#### FR-LA-002: Loki Query Configuration (Should Have)

**Description**: Loki shall be configured with query limits appropriate for development.

**Acceptance Criteria**:
1. Results cache is enabled with embedded cache
2. Cache size is appropriate for development (e.g., 100MB)
3. Query timeout is set to reasonable value (default acceptable)

**Traceability**: IS-1

---

#### FR-LA-003: Promtail Docker Service Discovery (Must Have)

**Description**: Promtail shall automatically discover and collect logs from all Docker containers.

**Acceptance Criteria**:
1. Promtail uses Docker service discovery (`docker_sd_configs`)
2. Docker socket is mounted for container discovery
3. Refresh interval is 5 seconds for responsive log collection
4. Container logs appear in Loki within 5 seconds of emission

**Traceability**: US-007, IS-1

---

#### FR-LA-004: Promtail Label Configuration (Must Have)

**Description**: Promtail shall apply appropriate labels to collected logs for filtering.

**Acceptance Criteria**:
1. `container` label is extracted from Docker container name
2. `stream` label is extracted from log stream (stdout/stderr)
3. `service` label is extracted from Docker Compose service label
4. Labels enable filtering by container, service, and stream in Grafana

**Traceability**: US-007, IS-1

---

#### FR-LA-005: Promtail Push Configuration (Must Have)

**Description**: Promtail shall be configured to push logs to Loki.

**Acceptance Criteria**:
1. Client URL is configured as `http://loki:3100/loki/api/v1/push`
2. Positions file is configured for resume capability
3. Connection errors are handled gracefully (retry with backoff)

**Traceability**: IS-1

---

### Distributed Tracing Requirements

#### FR-DT-001: Tempo OTLP Receiver Configuration (Must Have)

**Description**: Tempo shall be configured to receive traces via OTLP protocol.

**Acceptance Criteria**:
1. OTLP gRPC receiver is enabled on port 4317
2. OTLP HTTP receiver is enabled on port 4318
3. Both receivers bind to `0.0.0.0` for container accessibility
4. Receivers accept traces from any source (no authentication for development)

**Traceability**: US-002, US-009, IS-1

---

#### FR-DT-002: Tempo Storage Configuration (Must Have)

**Description**: Tempo shall be configured for local trace storage suitable for development.

**Acceptance Criteria**:
1. Storage backend is `local` (filesystem)
2. Blocks storage path is `/tmp/tempo/blocks`
3. WAL (Write-Ahead Log) path is `/tmp/tempo/wal`
4. Block retention is appropriate for development (e.g., 1 hour minimum)
5. Max block duration is configured (e.g., 5 minutes)

**Traceability**: IS-1

---

#### FR-DT-003: Tempo HTTP API Configuration (Must Have)

**Description**: Tempo shall expose an HTTP API for trace queries.

**Acceptance Criteria**:
1. HTTP API is available on port 3200
2. API supports trace query by trace ID
3. API supports trace search by service name and duration
4. API is accessible from Grafana for visualization

**Traceability**: US-002, IS-1

---

#### FR-DT-004: Trace Context Propagation (Must Have)

**Description**: The backend shall propagate W3C Trace Context headers for distributed tracing.

**Acceptance Criteria**:
1. Incoming requests with `traceparent` header continue existing trace
2. Requests without trace context start new traces
3. Outgoing HTTP requests include `traceparent` header
4. Trace context is available in application code via OpenTelemetry API

**Traceability**: US-009

---

#### FR-DT-005: Span Export Reliability (Should Have)

**Description**: The backend shall handle trace export failures gracefully.

**Acceptance Criteria**:
1. BatchSpanProcessor buffers spans in memory during export failures
2. Buffer overflow drops oldest spans (not application errors)
3. Export failures are logged as warnings, not errors
4. Application continues normal operation when Tempo is unavailable

**Traceability**: EC-001, EC-005

---

### Visualization Requirements

#### FR-VZ-001: Grafana Datasource Provisioning (Must Have)

**Description**: Grafana shall be provisioned with datasources for all observability services.

**Acceptance Criteria**:
1. Prometheus datasource is configured and set as default
2. Loki datasource is configured for log queries
3. Tempo datasource is configured for trace queries
4. All datasources use internal Docker network URLs
5. All datasources are marked as editable for development flexibility

**Traceability**: US-001, IS-1, IS-3

---

#### FR-VZ-002: Grafana Dashboard Provisioning (Must Have)

**Description**: Grafana shall be provisioned with pre-built dashboards for common use cases.

**Acceptance Criteria**:
1. Dashboard provisioning is configured via `dashboards.yml`
2. Dashboards are loaded from `/etc/grafana/provisioning/dashboards`
3. Dashboards are editable (not locked)
4. Dashboard changes persist to Grafana volume

**Traceability**: US-001, US-004, IS-4

---

#### FR-VZ-003: Backend Service Dashboard (Must Have)

**Description**: A pre-built dashboard shall visualize backend service health and performance.

**Acceptance Criteria**:
1. Dashboard title is "Backend Service Dashboard"
2. Dashboard includes the following panels:
   - Request Rate (requests per second by method and endpoint)
   - Request Duration (p95 and p99 latency)
   - Error Rate (4xx and 5xx errors per second)
   - Active Requests (current concurrent requests)
   - Recent Logs (last 100 log entries from backend)
3. Dashboard uses appropriate visualization types (graph, gauge, logs)
4. Dashboard auto-refreshes every 10 seconds
5. Default time range is last 1 hour

**Traceability**: US-001, IS-4

---

#### FR-VZ-004: SLO Overview Dashboard (Future Work - Not in Initial Scope)

**Description**: A pre-built dashboard shall visualize Service Level Objectives and error budgets.

**Status**: Deferred to future iteration. The source implementation does not include this dashboard. Will be created based on user feedback after initial release.

**Acceptance Criteria** (for future implementation):
1. Dashboard title is "SLO Overview Dashboard"
2. Dashboard includes the following panels:
   - Availability percentage (successful requests / total requests)
   - Latency SLO status (percentage of requests within target)
   - Error budget remaining (monthly view)
   - Error budget burn rate (rate of budget consumption)
3. Dashboard includes configurable SLO targets via variables:
   - Availability target (default: 99.5%)
   - Latency target (default: 500ms for p95)
4. Time range supports 1 hour, 24 hours, 7 days, 30 days presets

**Traceability**: US-004, IS-4

---

#### FR-VZ-005: Log Explorer Dashboard (Future Work - Not in Initial Scope)

**Description**: A pre-built dashboard shall provide quick access to common log queries.

**Status**: Deferred to future iteration. The source implementation does not include this dashboard. Users can explore logs directly through Grafana's Explore view with the Loki datasource.

**Acceptance Criteria** (for future implementation):
1. Dashboard title is "Log Explorer Dashboard"
2. Dashboard includes the following panels:
   - All Logs panel with live tail capability
   - Error Logs panel (filtered by ERROR level or status >= 500)
   - Log Volume graph (logs per minute by service)
3. Dashboard includes filter variables:
   - Service selector (backend, keycloak, etc.)
   - Log level selector (INFO, WARNING, ERROR)
   - Container selector
4. Dashboard supports search within log content

**Traceability**: US-003, US-007, IS-4

---

#### FR-VZ-006: Trace Explorer Dashboard (Future Work - Not in Initial Scope)

**Description**: A pre-built dashboard shall provide trace search and visualization.

**Status**: Deferred to future iteration. The source implementation does not include this dashboard. Users can explore traces directly through Grafana's Explore view with the Tempo datasource.

**Acceptance Criteria** (for future implementation):
1. Dashboard title is "Trace Explorer Dashboard"
2. Dashboard includes the following panels:
   - Trace search panel (by service, duration, time range)
   - Trace duration histogram
   - Service map visualization (node graph)
   - Recent traces table
3. Dashboard includes filter variables:
   - Service name selector
   - Minimum duration filter
   - Status filter (error/success)

**Traceability**: US-002, US-009, IS-4

---

#### FR-VZ-007: Grafana Anonymous Access (Must Have)

**Description**: Grafana shall allow anonymous access in development mode.

**Acceptance Criteria**:
1. Anonymous authentication is enabled via environment variable
2. Anonymous users have Admin role (full access in development)
3. Login form is disabled to streamline development experience
4. Configuration is clearly documented as development-only

**Traceability**: US-001, G5

---

### Data Correlation Requirements

#### FR-DC-001: Trace to Logs Correlation (Must Have)

**Description**: Users shall be able to navigate from a trace span to related log entries.

**Acceptance Criteria**:
1. Tempo datasource includes `tracesToLogsV2` configuration
2. Configuration links to Loki datasource by UID
3. Time window for log search is +/- 1 hour from span time
4. Filter by trace ID is enabled
5. Clicking "Logs for this span" in Tempo opens Loki with appropriate query

**Traceability**: US-003, G3, IS-6

---

#### FR-DC-002: Trace to Metrics Correlation (Should Have)

**Description**: Users shall be able to navigate from traces to related metrics.

**Acceptance Criteria**:
1. Tempo datasource includes `tracesToMetrics` configuration
2. Configuration links to Prometheus datasource by UID
3. Metric queries use appropriate labels from trace attributes

**Traceability**: G3, IS-6

---

#### FR-DC-003: Service Map Visualization (Should Have)

**Description**: Users shall be able to view a service map derived from trace data.

**Acceptance Criteria**:
1. Tempo datasource includes `serviceMap` configuration
2. Configuration links to Prometheus datasource for metrics
3. Node graph is enabled in Tempo datasource
4. Service map shows service dependencies based on traces

**Traceability**: US-009, IS-6

---

#### FR-DC-004: Log to Trace Correlation (Should Have)

**Description**: Users shall be able to navigate from a log entry to its associated trace.

**Acceptance Criteria**:
1. Backend logs include `trace_id` field when trace context is available
2. Loki derived fields configuration extracts `trace_id`
3. Clicking trace ID in log entry opens Tempo with trace details
4. (Note: Derived fields configuration may require manual Grafana setup)

**Traceability**: US-003, G3

---

### Documentation Requirements

#### FR-DOC-001: README Observability Section (Must Have)

**Description**: The generated project README shall include an observability quick-start guide.

**Acceptance Criteria**:
1. README includes "Observability" section when `include_observability` is `"yes"`
2. Section includes service URLs with configured ports:
   - Grafana: `http://localhost:{{ cookiecutter.grafana_port }}`
   - Prometheus: `http://localhost:{{ cookiecutter.prometheus_port }}`
   - Backend Metrics: `http://localhost:{{ cookiecutter.backend_port }}/metrics`
3. Section includes quick-start steps (under 5 minutes to read)
4. Section links to detailed observability documentation

**Traceability**: US-005, G5, IS-5

---

#### FR-DOC-002: Observability Directory README (Should Have)

**Description**: The observability directory shall include detailed documentation.

**Acceptance Criteria**:
1. `observability/README.md` file is generated
2. Documentation includes:
   - Architecture overview with service diagram
   - Configuration file descriptions
   - Customization instructions
   - Production considerations
   - Troubleshooting guide
3. Documentation includes examples for adding custom metrics

**Traceability**: US-008, US-010, G5, IS-5

---

#### FR-DOC-003: Inline Code Documentation (Should Have)

**Description**: The observability module shall include comprehensive inline documentation.

**Acceptance Criteria**:
1. Module docstring explains the overall purpose
2. Each function includes docstring with parameters and return values
3. Complex configuration includes inline comments
4. Examples are provided for extending metrics

**Traceability**: US-008, G5, IS-5

---

### Environment Configuration Requirements

#### FR-ENV-001: Backend Observability Environment Variables (Must Have)

**Description**: The backend service shall support configuration via environment variables.

**Acceptance Criteria**:
1. `OTEL_SERVICE_NAME`: Service name for traces (default: `"backend"`)
2. `OTEL_EXPORTER_OTLP_ENDPOINT`: Tempo endpoint (default: `"http://tempo:4317"`)
3. `TESTING`: Disables trace context in logs when `"true"`
4. Environment variables are documented in `compose.yml` and README

**Traceability**: US-010, IS-2

---

#### FR-ENV-002: Grafana Environment Variables (Should Have)

**Description**: Grafana shall support configuration via environment variables for production customization.

**Acceptance Criteria**:
1. `GF_AUTH_ANONYMOUS_ENABLED`: Enable/disable anonymous access
2. `GF_AUTH_ANONYMOUS_ORG_ROLE`: Role for anonymous users
3. `GF_AUTH_DISABLE_LOGIN_FORM`: Hide login form
4. Variables are documented with production recommendations

**Traceability**: US-010

---

### Priority Summary

| Priority | Count | Requirements |
|----------|-------|-------------|
| Must Have | 29 | FR-TC-001, FR-TC-003, FR-TC-004, FR-IS-001 through FR-IS-007, FR-BI-001 through FR-BI-006, FR-BI-008 through FR-BI-010, FR-MC-001, FR-MC-002, FR-LA-001, FR-LA-003 through FR-LA-005, FR-DT-001 through FR-DT-004, FR-VZ-001 through FR-VZ-003, FR-VZ-007, FR-DC-001, FR-DOC-001, FR-ENV-001 |
| Should Have | 13 | FR-TC-002, FR-BI-007, FR-MC-003, FR-LA-002, FR-DT-005, FR-VZ-004 through FR-VZ-006, FR-DC-002 through FR-DC-004, FR-DOC-002, FR-DOC-003, FR-ENV-002 |
| Could Have | 0 | None |
| Won't Have | 0 | None (covered in Out of Scope) |

---

### Requirements Traceability Matrix

| Requirement | User Stories | Goals | Scope Items |
|-------------|-------------|-------|-------------|
| FR-TC-001 | US-005, US-006 | G4 | IS-3 |
| FR-TC-002 | US-005, US-010 | G4 | IS-3 |
| FR-TC-003 | US-005, US-006 | G4 | IS-3 |
| FR-TC-004 | US-005 | G1 | IS-1 |
| FR-IS-001 through FR-IS-007 | US-005 | G1 | IS-1 |
| FR-BI-001 through FR-BI-010 | US-001, US-002, US-005, US-008, US-011, US-012 | G1, G2, G5 | IS-2 |
| FR-MC-001 through FR-MC-003 | US-001 | G2 | IS-1 |
| FR-LA-001 through FR-LA-005 | US-007 | G1, G3 | IS-1 |
| FR-DT-001 through FR-DT-005 | US-002, US-009 | G1, G3 | IS-1 |
| FR-VZ-001 through FR-VZ-007 | US-001, US-002, US-003, US-004, US-007, US-009 | G1, G2, G5 | IS-1, IS-4 |
| FR-DC-001 through FR-DC-004 | US-003, US-009 | G3 | IS-6 |
| FR-DOC-001 through FR-DOC-003 | US-005, US-008, US-010 | G5 | IS-5 |
| FR-ENV-001, FR-ENV-002 | US-010 | G4 | IS-2, IS-3 |

---

## Non-Functional Requirements

This section defines the non-functional requirements (NFRs) that govern the quality attributes of the observability stack integration. These requirements complement the functional requirements by specifying performance, reliability, scalability, maintainability, and other system qualities that must be achieved.

### NFR Categories

| Category | Code Prefix | Description |
|----------|-------------|-------------|
| Performance | NFR-PF | Response times, throughput, and resource efficiency |
| Reliability | NFR-RL | Availability, fault tolerance, and recovery |
| Scalability | NFR-SC | Capacity growth and elastic behavior |
| Maintainability | NFR-MT | Ease of configuration, updates, and troubleshooting |
| Operability | NFR-OP | Deployment, monitoring, and operational concerns |
| Resource Efficiency | NFR-RE | Memory, CPU, storage, and network usage |
| Compatibility | NFR-CP | Integration with existing systems and standards |

---

### Performance Requirements

#### NFR-PF-001: Observability Stack Startup Time (Must Have)

**Description**: The complete observability stack shall start and become operational within an acceptable time frame to support rapid development iterations.

**Acceptance Criteria**:
1. All observability services (Prometheus, Loki, Promtail, Tempo, Grafana) reach healthy state within 90 seconds of `docker compose up`
2. Grafana becomes accessible and serves dashboards within 60 seconds of container start
3. Prometheus begins scraping targets within 30 seconds of container start
4. Tempo accepts OTLP trace exports within 20 seconds of container start

**Measurement Method**: Automated startup test measuring time from `docker compose up` command to all services reporting healthy status.

**Traceability**: G1 (Production-Ready Observability)

---

#### NFR-PF-002: Metrics Scrape and Query Latency (Must Have)

**Description**: Prometheus metrics collection and querying shall be responsive enough for real-time monitoring and debugging.

**Acceptance Criteria**:
1. Backend `/metrics` endpoint responds within 100ms under normal conditions
2. Prometheus scrape operations complete within the scrape interval (5s for backend, 15s for others)
3. Simple PromQL queries (single metric, 1-hour range) execute in < 500ms
4. Complex PromQL queries (aggregations, 24-hour range) execute in < 3 seconds
5. Grafana dashboard panels render within 3 seconds with 1 hour of data

**Measurement Method**: Response time monitoring via Prometheus self-metrics and Grafana query timing.

**Traceability**: US-001, G2

---

#### NFR-PF-003: Log Ingestion and Query Latency (Must Have)

**Description**: Log aggregation via Loki shall provide near real-time visibility into application logs.

**Acceptance Criteria**:
1. Logs appear in Loki within 5 seconds of emission from containers
2. Promtail batch sends logs at least every 1 second
3. Simple LogQL queries (single container, last 5 minutes) execute in < 1 second
4. Complex LogQL queries (regex matching, 1-hour range) execute in < 5 seconds
5. Live tail queries update within 2 seconds of new log entries

**Measurement Method**: End-to-end latency test from log emission to query visibility.

**Traceability**: US-003, US-007, G3

---

#### NFR-PF-004: Trace Ingestion and Query Latency (Must Have)

**Description**: Distributed tracing via Tempo shall provide responsive trace ingestion and querying for debugging workflows.

**Acceptance Criteria**:
1. Traces are queryable in Tempo within 30 seconds of span completion
2. Trace lookup by trace_id completes in < 1 second
3. Trace search by service and duration completes in < 3 seconds
4. Trace visualization (flame graph) renders in < 2 seconds for traces with up to 100 spans
5. BatchSpanProcessor exports spans at least every 5 seconds

**Measurement Method**: End-to-end latency test from span creation to Tempo query visibility.

**Traceability**: US-002, US-009, G3

---

#### NFR-PF-005: Application Performance Overhead (Must Have)

**Description**: The observability instrumentation shall have minimal impact on application performance.

**Acceptance Criteria**:
1. Instrumentation adds < 5% latency overhead to HTTP request processing
2. Metrics middleware adds < 1ms per request
3. Trace context propagation adds < 0.5ms per request
4. `/metrics` endpoint generation completes in < 50ms with up to 1000 unique metric series
5. Memory overhead from instrumentation libraries < 50MB in backend process

**Measurement Method**: A/B performance testing with and without observability enabled; profiling of instrumentation code.

**Traceability**: G4, ADR-002

---

#### NFR-PF-006: Grafana Dashboard Performance (Should Have)

**Description**: Grafana dashboards shall load and refresh efficiently to support effective monitoring.

**Acceptance Criteria**:
1. Backend Service Dashboard loads completely within 3 seconds
2. Dashboard auto-refresh (10-second interval) does not cause visible lag
3. Switching between datasources (Prometheus, Loki, Tempo) completes in < 1 second
4. Panel queries execute in parallel where possible
5. Browser memory usage remains under 500MB during normal dashboard usage

**Measurement Method**: Grafana's built-in query inspector; browser performance profiling.

**Traceability**: US-001, US-004, G5

---

### Reliability Requirements

#### NFR-RL-001: Graceful Degradation on Observability Failure (Must Have)

**Description**: The application shall continue to function normally when observability services are unavailable or degraded.

**Acceptance Criteria**:
1. Backend continues serving requests when Tempo is unavailable
2. Backend continues serving requests when Prometheus fails to scrape
3. Application logs continue to stdout/stderr when Loki/Promtail are unavailable
4. OpenTelemetry exporters fail gracefully with warning logs (not exceptions)
5. BatchSpanProcessor drops oldest spans when buffer is full (no application errors)
6. No application crashes or hangs due to observability service failures

**Measurement Method**: Chaos testing by stopping observability services during load test; verify application health.

**Traceability**: EC-001, EC-005, G4

---

#### NFR-RL-002: Observability Service Restart Recovery (Must Have)

**Description**: Observability services shall recover state and resume operation after container restarts.

**Acceptance Criteria**:
1. Prometheus retains metrics data after container restart (via persistent volume)
2. Loki retains log data after container restart (via persistent volume)
3. Tempo retains trace data after container restart (via persistent volume)
4. Grafana retains dashboard customizations after restart (via persistent volume)
5. Service recovery completes within 60 seconds of restart
6. No data corruption from unclean shutdowns (e.g., `docker compose down`)

**Measurement Method**: Restart testing with data verification before and after.

**Traceability**: FR-IS-006

---

#### NFR-RL-003: Data Integrity During Export (Should Have)

**Description**: Telemetry data shall be reliably exported without corruption or loss under normal conditions.

**Acceptance Criteria**:
1. Prometheus scrapes succeed > 99% of the time under normal network conditions
2. Promtail delivers > 99% of logs to Loki under normal conditions
3. OpenTelemetry BatchSpanProcessor delivers > 95% of spans under normal conditions
4. Failed exports are retried with exponential backoff
5. Partial failures do not corrupt successfully transmitted data

**Measurement Method**: Compare emitted data counts with received data counts; monitor export success rates.

**Traceability**: EC-005

---

#### NFR-RL-004: Service Health Checks (Should Have)

**Description**: All observability services shall expose health check endpoints for orchestration and monitoring.

**Acceptance Criteria**:
1. Prometheus exposes health at `/-/healthy` and readiness at `/-/ready`
2. Loki exposes health at `/ready`
3. Tempo exposes health at `/ready`
4. Grafana exposes health at `/api/health`
5. Health checks return within 1 second
6. Docker Compose health checks configured for all observability services

**Measurement Method**: Health endpoint verification; Docker health status checks.

**Traceability**: G1

---

### Scalability Requirements

#### NFR-SC-001: Metrics Cardinality Limits (Must Have)

**Description**: The default metrics instrumentation shall use bounded cardinality to prevent Prometheus performance degradation.

**Acceptance Criteria**:
1. Default instrumentation uses fixed labels: `method`, `endpoint`, `status`
2. Maximum unique label combinations per metric < 1000 in typical usage
3. Documentation warns against high-cardinality labels (e.g., `user_id`, `request_id`)
4. No dynamic labels from request parameters in default instrumentation
5. Prometheus memory usage remains stable under sustained traffic

**Measurement Method**: Cardinality analysis via `prometheus_tsdb_head_series`; memory monitoring.

**Traceability**: EC-002

---

#### NFR-SC-002: Log Volume Handling (Must Have)

**Description**: The logging stack shall handle reasonable log volumes without performance degradation or disk exhaustion.

**Acceptance Criteria**:
1. Promtail handles up to 1000 log lines per second per container without backpressure
2. Loki ingests logs without rate limiting at development traffic levels
3. Disk usage for logs grows linearly and predictably
4. Log retention limits prevent unbounded disk growth
5. Query performance degrades gracefully with increased log volume

**Measurement Method**: Load testing with high log output; disk usage monitoring over time.

**Traceability**: EC-003

---

#### NFR-SC-003: Trace Volume Handling (Should Have)

**Description**: The tracing stack shall handle reasonable trace volumes without performance degradation.

**Acceptance Criteria**:
1. Tempo ingests traces without dropping at development traffic levels (< 100 spans/second)
2. Trace storage uses efficient compression
3. Block compaction runs without impacting ingestion performance
4. Retention policies automatically remove old traces

**Measurement Method**: Load testing with distributed trace generation; monitor Tempo metrics.

**Traceability**: FR-DT-002

---

#### NFR-SC-004: Horizontal Scaling Readiness (Could Have)

**Description**: The observability configuration shall be designed to support horizontal scaling for production deployment.

**Acceptance Criteria**:
1. Configuration files use environment variables for endpoints (not hardcoded)
2. Service discovery patterns documented for multi-instance deployments
3. Storage backends are configurable (local for dev, S3/GCS for prod)
4. Documentation includes production scaling recommendations
5. No assumptions of single-instance deployment in configuration

**Measurement Method**: Configuration review; documentation completeness check.

**Traceability**: OOS-3 (production readiness guidance)

---

### Maintainability Requirements

#### NFR-MT-001: Configuration File Organization (Must Have)

**Description**: Observability configuration files shall be organized logically and documented for easy maintenance.

**Acceptance Criteria**:
1. Each service has its own configuration file in dedicated subdirectory
2. Configuration files use YAML format with inline comments
3. Key configuration values are explained with comments
4. Sensitive values (if any) use environment variable substitution
5. Configuration follows the pattern established in `implementation-manager/observability/`

**Measurement Method**: Configuration file review; adherence to reference implementation.

**Traceability**: IS-1, FR-TC-004

---

#### NFR-MT-002: Instrumentation Code Clarity (Must Have)

**Description**: The observability module code shall be readable and maintainable by developers unfamiliar with OpenTelemetry.

**Acceptance Criteria**:
1. Module includes comprehensive docstrings explaining each function
2. Complex configurations include explanatory comments
3. Examples for extending metrics are included in code comments
4. Code follows existing backend coding conventions
5. No unnecessary abstraction layers (direct use of OpenTelemetry APIs)

**Measurement Method**: Code review; developer feedback.

**Traceability**: FR-BI-001, FR-DOC-003, G5

---

#### NFR-MT-003: Version Pinning Strategy (Should Have)

**Description**: Observability component versions shall be managed for stability and reproducibility.

**Acceptance Criteria**:
1. Python dependencies specify version ranges (e.g., `>=1.0.0,<2.0.0`)
2. Docker images use `latest` tag for development (ease of updates)
3. Documentation notes pinning strategy for production (recommend specific versions)
4. Breaking changes in OpenTelemetry APIs are noted in upgrade guide
5. Grafana dashboard JSON is version-controlled

**Measurement Method**: Dependency specification review; documentation completeness.

**Traceability**: FR-BI-009

---

#### NFR-MT-004: Troubleshooting Support (Should Have)

**Description**: The observability stack shall include documentation and tools for troubleshooting common issues.

**Acceptance Criteria**:
1. `observability/README.md` includes troubleshooting section
2. Common issues documented: logs not appearing, traces missing, metrics not scraped
3. Each service includes log output configuration for debugging
4. Prometheus targets page accessible for scrape debugging
5. Grafana includes query inspector for debugging slow queries

**Measurement Method**: Documentation review; test troubleshooting scenarios.

**Traceability**: FR-DOC-002

---

### Operability Requirements

#### NFR-OP-001: Zero-Configuration Development Experience (Must Have)

**Description**: The observability stack shall work immediately after `docker compose up` without manual configuration.

**Acceptance Criteria**:
1. All datasources are pre-provisioned in Grafana
2. All dashboards are pre-loaded in Grafana
3. Prometheus scrape targets are pre-configured
4. Backend instrumentation activates automatically
5. No manual steps required between `docker compose up` and viewing dashboards

**Measurement Method**: Fresh clone test; verify dashboard functionality without configuration.

**Traceability**: G1, G5, US-005

---

#### NFR-OP-002: Service URL Accessibility (Must Have)

**Description**: All observability services shall be accessible via predictable URLs for developer convenience.

**Acceptance Criteria**:
1. Grafana accessible at `http://localhost:{{ cookiecutter.grafana_port }}`
2. Prometheus accessible at `http://localhost:{{ cookiecutter.prometheus_port }}`
3. Backend metrics at `http://localhost:{{ cookiecutter.backend_port }}/metrics`
4. Service URLs documented in README with configured port values
5. URLs work immediately without authentication in development mode

**Measurement Method**: URL accessibility testing after stack startup.

**Traceability**: FR-DOC-001, FR-VZ-007

---

#### NFR-OP-003: Container Naming Conventions (Should Have)

**Description**: Observability containers shall follow consistent naming conventions for easy identification.

**Acceptance Criteria**:
1. Container names include project slug: `{{ cookiecutter.project_slug }}-prometheus`
2. Container names match service names in `docker compose`
3. Naming convention documented for operators
4. Log filtering by container name works reliably in Loki

**Measurement Method**: Container listing; Loki query by container name.

**Traceability**: FR-IS-001 through FR-IS-005

---

#### NFR-OP-004: Log Output Verbosity (Should Have)

**Description**: Observability service logs shall be appropriately verbose for debugging without overwhelming output.

**Acceptance Criteria**:
1. Default log level is INFO or equivalent
2. Debug logging available via environment variable
3. Startup logs confirm successful initialization
4. Error logs include actionable information
5. No excessive repetitive log entries under normal operation

**Measurement Method**: Log review during normal and error conditions.

**Traceability**: G5

---

### Resource Efficiency Requirements

#### NFR-RE-001: Memory Footprint (Must Have)

**Description**: The observability stack shall have a reasonable memory footprint for development environments.

**Acceptance Criteria**:
1. Combined memory usage of all observability containers < 2GB under normal operation
2. Individual container memory usage:
   - Prometheus: < 512MB
   - Loki: < 256MB
   - Promtail: < 128MB
   - Tempo: < 512MB
   - Grafana: < 512MB
3. Memory usage does not grow unboundedly over 24-hour period
4. Memory limits configurable via Docker Compose

**Measurement Method**: `docker stats` monitoring over 24-hour period.

**Traceability**: G4

---

#### NFR-RE-002: CPU Usage (Should Have)

**Description**: The observability stack shall have minimal CPU impact during idle and moderate load periods.

**Acceptance Criteria**:
1. Idle CPU usage (no application traffic): < 5% total across all containers
2. Active CPU usage (moderate traffic): < 20% total across all containers
3. No CPU spikes during scheduled operations (compaction, retention enforcement)
4. CPU usage proportional to telemetry volume

**Measurement Method**: `docker stats` monitoring during load testing.

**Traceability**: G4

---

#### NFR-RE-003: Storage Growth Rate (Must Have)

**Description**: Storage usage shall grow predictably and be bounded by retention policies.

**Acceptance Criteria**:
1. Prometheus storage growth: < 100MB per day at development traffic levels
2. Loki storage growth: < 50MB per day at development traffic levels
3. Tempo storage growth: < 50MB per day at development traffic levels
4. Retention policies prevent storage from exceeding configured limits
5. Storage growth rate documented for capacity planning

**Measurement Method**: Volume size monitoring over multi-day period.

**Traceability**: FR-MC-003, FR-LA-001, FR-DT-002

---

#### NFR-RE-004: Network Bandwidth (Should Have)

**Description**: Observability network traffic shall not significantly impact application performance.

**Acceptance Criteria**:
1. Metrics scraping: < 100KB per scrape interval
2. Log shipping: < 1MB per minute under normal conditions
3. Trace export: < 500KB per minute under normal conditions
4. All telemetry uses internal Docker network (no external bandwidth)
5. Batch processing reduces network call frequency

**Measurement Method**: Network monitoring on internal Docker network.

**Traceability**: ADR-002 (network overhead mitigation)

---

### Compatibility Requirements

#### NFR-CP-001: OpenTelemetry Standards Compliance (Must Have)

**Description**: The tracing implementation shall comply with OpenTelemetry specifications and semantic conventions.

**Acceptance Criteria**:
1. Traces use W3C Trace Context format for propagation (`traceparent` header)
2. Span attributes follow OpenTelemetry semantic conventions for HTTP
3. OTLP protocol used for trace export (gRPC and HTTP supported)
4. Service name follows `service.name` resource attribute convention
5. Compatibility with OpenTelemetry Collector if deployed as intermediate processor

**Measurement Method**: Specification compliance review; interoperability testing with OpenTelemetry Collector.

**Traceability**: FR-DT-004, ADR-002 (industry standard)

---

#### NFR-CP-002: Prometheus Exposition Format (Must Have)

**Description**: The metrics endpoint shall comply with Prometheus exposition format for scraping compatibility.

**Acceptance Criteria**:
1. `/metrics` endpoint returns `text/plain; version=0.0.4; charset=utf-8` content type
2. Metrics include HELP and TYPE annotations
3. Metric names follow Prometheus naming conventions (lowercase, underscores)
4. Histogram buckets follow standard conventions
5. Compatible with any Prometheus-compatible scraper (Prometheus, VictoriaMetrics, etc.)

**Measurement Method**: Prometheus scrape success; format validation.

**Traceability**: FR-BI-006, FR-MC-001

---

#### NFR-CP-003: Grafana Datasource Compatibility (Must Have)

**Description**: Grafana configurations shall be compatible with the provisioned Grafana version.

**Acceptance Criteria**:
1. Datasource provisioning uses stable API format
2. Dashboard JSON compatible with Grafana 9.x and 10.x
3. Datasource configurations work with service hostnames in Docker network
4. Correlation configurations (tracesToLogs, tracesToMetrics) compatible with current Grafana

**Measurement Method**: Grafana version upgrade testing; datasource connection verification.

**Traceability**: FR-VZ-001, FR-DC-001

---

#### NFR-CP-004: Docker Compose Compatibility (Must Have)

**Description**: The observability stack shall work with standard Docker Compose installations.

**Acceptance Criteria**:
1. Compatible with Docker Compose V2 (docker compose) and V1 (docker-compose)
2. Uses standard Docker Compose file format (version 3.x)
3. Works on Linux, macOS, and Windows (WSL2) development environments
4. No dependency on Docker Swarm features
5. Volumes use standard named volume syntax

**Measurement Method**: Testing on multiple platforms; Docker Compose version compatibility.

**Traceability**: IS-1

---

#### NFR-CP-005: Python Version Compatibility (Should Have)

**Description**: The observability Python dependencies shall be compatible with the supported Python versions.

**Acceptance Criteria**:
1. Compatible with Python 3.10, 3.11, and 3.12
2. No dependencies on deprecated Python features
3. Type hints compatible with target Python versions
4. Async instrumentation compatible with asyncio patterns used in FastAPI

**Measurement Method**: CI testing on multiple Python versions.

**Traceability**: FR-BI-009

---

### Priority Summary

| Priority | Count | Requirements |
|----------|-------|--------------|
| Must Have | 18 | NFR-PF-001 through NFR-PF-005, NFR-RL-001, NFR-RL-002, NFR-SC-001, NFR-SC-002, NFR-MT-001, NFR-MT-002, NFR-OP-001, NFR-OP-002, NFR-RE-001, NFR-RE-003, NFR-CP-001 through NFR-CP-004 |
| Should Have | 10 | NFR-PF-006, NFR-RL-003, NFR-RL-004, NFR-SC-003, NFR-MT-003, NFR-MT-004, NFR-OP-003, NFR-OP-004, NFR-RE-002, NFR-RE-004, NFR-CP-005 |
| Could Have | 1 | NFR-SC-004 |
| Won't Have | 0 | None (production-specific NFRs covered in Out of Scope) |

---

### NFR Traceability Matrix

| NFR | Functional Requirements | User Stories | Goals | Scope Items |
|-----|------------------------|--------------|-------|-------------|
| NFR-PF-001 | FR-IS-001 through FR-IS-007 | US-005 | G1 | IS-1 |
| NFR-PF-002 | FR-MC-001, FR-BI-006 | US-001 | G2 | IS-1, IS-2 |
| NFR-PF-003 | FR-LA-001 through FR-LA-005 | US-003, US-007 | G3 | IS-1 |
| NFR-PF-004 | FR-DT-001 through FR-DT-003 | US-002, US-009 | G3 | IS-1 |
| NFR-PF-005 | FR-BI-004, FR-BI-005 | - | G4 | IS-2 |
| NFR-PF-006 | FR-VZ-003, FR-VZ-004 | US-001, US-004 | G5 | IS-4 |
| NFR-RL-001 | FR-DT-005 | - | G4 | IS-2 |
| NFR-RL-002 | FR-IS-006 | - | G1 | IS-1 |
| NFR-RL-003 | FR-LA-005, FR-DT-005 | - | - | IS-1, IS-2 |
| NFR-RL-004 | FR-IS-001 through FR-IS-005 | - | G1 | IS-1 |
| NFR-SC-001 | FR-BI-004 | - | - | IS-2 |
| NFR-SC-002 | FR-LA-003, FR-LA-004 | - | - | IS-1 |
| NFR-SC-003 | FR-DT-002 | - | - | IS-1 |
| NFR-SC-004 | - | US-010 | - | OOS-3 |
| NFR-MT-001 | FR-TC-004 | - | - | IS-1 |
| NFR-MT-002 | FR-BI-001, FR-DOC-003 | US-008 | G5 | IS-2, IS-5 |
| NFR-MT-003 | FR-BI-009 | - | - | IS-2 |
| NFR-MT-004 | FR-DOC-002 | - | G5 | IS-5 |
| NFR-OP-001 | FR-VZ-001, FR-VZ-002 | US-005 | G1, G5 | IS-1, IS-4 |
| NFR-OP-002 | FR-DOC-001 | US-005 | G5 | IS-5 |
| NFR-OP-003 | FR-IS-001 through FR-IS-005 | - | - | IS-1 |
| NFR-OP-004 | - | - | G5 | - |
| NFR-RE-001 | FR-IS-001 through FR-IS-005 | - | G4 | IS-1 |
| NFR-RE-002 | - | - | G4 | - |
| NFR-RE-003 | FR-MC-003, FR-LA-001, FR-DT-002 | - | G4 | IS-1 |
| NFR-RE-004 | - | - | G4 | - |
| NFR-CP-001 | FR-DT-004, FR-BI-002 | US-009 | - | IS-2 |
| NFR-CP-002 | FR-BI-006 | US-011 | - | IS-2 |
| NFR-CP-003 | FR-VZ-001, FR-DC-001 | - | - | IS-4 |
| NFR-CP-004 | FR-IS-001 through FR-IS-007 | US-005 | - | IS-1 |
| NFR-CP-005 | FR-BI-009 | - | - | IS-2 |

---

### Verification and Validation

Each NFR category shall be validated through the following methods:

| Category | Validation Approach |
|----------|-------------------|
| Performance | Automated performance tests; profiling; load testing |
| Reliability | Chaos testing; restart scenarios; failure injection |
| Scalability | Load testing with increasing volume; cardinality analysis |
| Maintainability | Code review; documentation review; developer feedback |
| Operability | Fresh clone testing; user acceptance testing |
| Resource Efficiency | 24-hour monitoring; resource profiling |
| Compatibility | Multi-platform testing; version compatibility matrix |

---

## Technical Approach

This section defines the high-level technical strategy for implementing the observability stack integration. The approach is grounded in the battle-tested `implementation-manager` reference implementation and ADR-002 architectural decisions, adapted for the cookiecutter template's conditional generation requirements.

### Implementation Strategy Overview

The technical approach follows a **port-and-adapt** strategy, where the proven observability implementation from `implementation-manager/` is systematically integrated into the cookiecutter template with appropriate parameterization and conditional rendering.

```
implementation-manager/              cookiecutter template/
       (source)            ----->     (destination)

observability/                  -->  observability/
  prometheus/prometheus.yml            prometheus/prometheus.yml (templatized)
  loki/loki-config.yml                 loki/loki-config.yml
  promtail/promtail-config.yml         promtail/promtail-config.yml (templatized)
  tempo/tempo.yml                      tempo/tempo.yml
  grafana/datasources/                 grafana/datasources/ (templatized)
  grafana/dashboards/                  grafana/dashboards/ (templatized)

backend/observability.py       -->  backend/app/observability.py (templatized)

docker-compose.yml             -->  compose.yml (observability services added conditionally)
```

### Technology Stack Selection

The observability stack is based on the **Grafana LGTM stack** (Loki, Grafana, Tempo, Mimir/Prometheus), as validated by ADR-002. This stack was selected for:

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Metrics Collection | **Prometheus** | Industry standard, PromQL ecosystem, pull-based model |
| Metrics Instrumentation | **prometheus-client** | Native Python library, low overhead |
| Log Aggregation | **Loki** | Efficient log storage, LogQL queries, Grafana integration |
| Log Collection | **Promtail** | Native Docker integration, automatic service discovery |
| Distributed Tracing | **Tempo** | OTLP support, Grafana correlation, cost-effective storage |
| Tracing Instrumentation | **OpenTelemetry** | CNCF standard, vendor-neutral, comprehensive instrumentation |
| Visualization | **Grafana** | Unified platform, datasource correlation, pre-built dashboards |

### Backend Instrumentation Architecture

The backend instrumentation follows the pattern established in `implementation-manager/backend/observability.py`:

```python
# Technical architecture of observability.py module

class ObservabilityModule:
    """
    Conceptual structure (actual implementation is functional)
    """

    # 1. OpenTelemetry Configuration
    #    - TracerProvider with Resource (service.name)
    #    - OTLPSpanExporter (gRPC to Tempo)
    #    - BatchSpanProcessor (efficient export batching)

    # 2. Prometheus Metrics
    #    - Counter: http_requests_total (method, endpoint, status)
    #    - Histogram: http_request_duration_seconds (method, endpoint)
    #    - Gauge: active_requests (concurrent request count)

    # 3. FastAPI Integration
    #    - FastAPIInstrumentor for automatic tracing
    #    - HTTP middleware for metrics collection
    #    - /metrics endpoint for Prometheus scraping

    # 4. Logging Configuration
    #    - Structured format with trace context (trace_id, span_id)
    #    - Conditional format for test mode
```

#### Instrumentation Integration Points

```
FastAPI Application Lifecycle
    |
    v
[main.py]
    |
    +---> setup_observability(app)  # Called after app creation
            |
            +---> FastAPIInstrumentor.instrument_app(app)
            |     (Automatic request/response tracing)
            |
            +---> Register metrics_middleware
            |     (Request counting, duration, active requests)
            |
            +---> Register /metrics endpoint
                  (Prometheus scrape target)
```

### Docker Compose Integration Pattern

The observability services integrate with the existing compose.yml using **conditional Jinja2 blocks**:

```yaml
# compose.yml template structure

services:
  # ... existing services (postgres, keycloak, backend, frontend, redis) ...

{% if cookiecutter.include_observability == "yes" %}
  # Prometheus - Metrics Collection
  prometheus:
    image: prom/prometheus:latest
    container_name: {{ cookiecutter.project_slug }}-prometheus
    # ... configuration ...

  # Loki - Log Aggregation
  loki:
    image: grafana/loki:latest
    container_name: {{ cookiecutter.project_slug }}-loki
    # ... configuration ...

  # Promtail - Log Collection
  promtail:
    image: grafana/promtail:latest
    container_name: {{ cookiecutter.project_slug }}-promtail
    depends_on:
      - loki
    # ... configuration ...

  # Tempo - Distributed Tracing
  tempo:
    image: grafana/tempo:latest
    container_name: {{ cookiecutter.project_slug }}-tempo
    # ... configuration ...

  # Grafana - Visualization
  grafana:
    image: grafana/grafana:latest
    container_name: {{ cookiecutter.project_slug }}-grafana
    depends_on:
      - prometheus
      - loki
      - tempo
    # ... configuration ...
{% endif %}

volumes:
  # ... existing volumes ...
{% if cookiecutter.include_observability == "yes" %}
  prometheus-data:
    name: {{ cookiecutter.project_slug }}-prometheus-data
  loki-data:
    name: {{ cookiecutter.project_slug }}-loki-data
  tempo-data:
    name: {{ cookiecutter.project_slug }}-tempo-data
  grafana-data:
    name: {{ cookiecutter.project_slug }}-grafana-data
{% endif %}
```

### Configuration Templatization Strategy

#### Prometheus Configuration (prometheus.yml)

The Prometheus configuration requires templatization for:
- External labels (cluster name from project_slug)
- Target endpoints (backend service name)

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: '{{ cookiecutter.project_slug }}'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s  # More frequent for responsive dashboards

  - job_name: 'keycloak'
    static_configs:
      - targets: ['keycloak:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'tempo'
    static_configs:
      - targets: ['tempo:3200']
    metrics_path: '/metrics'

  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
    metrics_path: '/metrics'
```

#### Loki Configuration (loki-config.yml)

The Loki configuration is largely static and can be ported directly:
- Filesystem storage backend for development
- Schema v13 for efficient indexing
- Embedded cache for query performance
- Analytics reporting disabled

#### Promtail Configuration (promtail-config.yml)

The Promtail configuration uses Docker service discovery with templatized label extraction:

```yaml
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'stream'
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'
```

#### Tempo Configuration (tempo.yml)

The Tempo configuration defines OTLP receivers and local storage:
- HTTP receiver on port 4318 for frontend traces
- gRPC receiver on port 4317 for backend traces (more efficient)
- Local filesystem storage with 1-hour block retention
- 5-minute max block duration for timely trace availability

#### Grafana Datasources (datasources.yml)

Grafana datasources require templatization for UID references used in correlation:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    uid: prometheus  # Used by Tempo for tracesToMetrics
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true

  - name: Loki
    uid: loki  # Used by Tempo for tracesToLogsV2
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true

  - name: Tempo
    uid: tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    editable: true
    jsonData:
      tracesToLogsV2:
        datasourceUid: 'loki'
        spanStartTimeShift: '-1h'
        spanEndTimeShift: '1h'
        filterByTraceID: true
      tracesToMetrics:
        datasourceUid: 'prometheus'
      serviceMap:
        datasourceUid: 'prometheus'
      nodeGraph:
        enabled: true
```

### Backend Environment Variables

The backend service requires additional environment variables when observability is enabled:

```yaml
backend:
  environment:
    # ... existing variables ...
{% if cookiecutter.include_observability == "yes" %}
    # OpenTelemetry Configuration
    OTEL_SERVICE_NAME: backend
    OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317
{% endif %}
```

### Python Dependencies Strategy

The `pyproject.toml` template requires conditional dependency inclusion:

```toml
[project]
dependencies = [
    # ... existing dependencies ...
{% if cookiecutter.include_observability == "yes" %}
    # OpenTelemetry
    "opentelemetry-api>=1.27.0,<2.0.0",
    "opentelemetry-sdk>=1.27.0,<2.0.0",
    "opentelemetry-exporter-otlp-proto-grpc>=1.27.0,<2.0.0",
    "opentelemetry-instrumentation-fastapi>=0.48b0,<1.0.0",
    # Prometheus
    "prometheus-client>=0.20.0,<1.0.0",
{% endif %}
]
```

### main.py Integration

The main application module requires conditional import and initialization:

```python
# Conditional import at module level
{% if cookiecutter.include_observability == "yes" %}
from observability import setup_observability
{% endif %}

# After app creation
app = FastAPI(...)

{% if cookiecutter.include_observability == "yes" %}
# Setup observability (before other middleware)
setup_observability(app)
{% endif %}
```

### Grafana Dashboard Strategy

Dashboards are stored as JSON files and provisioned via `dashboards.yml`. The initial implementation includes one pre-built dashboard ported from the source:

1. **Backend Service Dashboard** (`backend-dashboard.json`) - INCLUDED
   - Request rate by endpoint (graph)
   - Latency percentiles p50/p95/p99 (graph)
   - Error rate by status code (graph)
   - Active requests gauge (stat)
   - Recent logs panel (logs)

**Future Work** (not in initial scope - dashboards to be added in subsequent iterations):

2. **SLO Overview Dashboard** (`slo-dashboard.json`) - FUTURE
   - Availability percentage (stat)
   - Latency SLO compliance (gauge)
   - Error budget remaining (stat)
   - Error budget burn rate (graph)
   - Variables for configurable targets

3. **Log Explorer Dashboard** (`log-explorer-dashboard.json`) - FUTURE
   - All logs panel with live tail
   - Error logs panel (filtered)
   - Log volume by service (graph)
   - Service and level filter variables

4. **Trace Explorer Dashboard** (`trace-explorer-dashboard.json`) - FUTURE
   - Trace search panel
   - Trace duration histogram
   - Service map (node graph)
   - Recent traces table

**Note**: Users can explore logs and traces directly through Grafana's Explore view with the Loki and Tempo datasources until dedicated dashboards are created.

### Service Startup Order and Dependencies

The observability services have specific startup dependencies:

```
                          +-----------+
                          |  Postgres |
                          +-----------+
                                |
                                v
+-----------+           +-----------+           +-----------+
|   Loki    | <-------- | Promtail  |           |   Redis   |
+-----------+           +-----------+           +-----------+
      |                                               |
      |      +-----------+                           |
      +----> |   Tempo   | <-------------------------+
      |      +-----------+
      |            |
      |            v
      |      +-----------+
      +----> | Prometheus|
      |      +-----------+
      |            |
      v            v
      +-----------+
      |  Grafana  |
      +-----------+
            |
            v
      +-----------+
      |  Backend  | (with observability enabled)
      +-----------+
```

Docker Compose dependency configuration:
- `promtail` depends on `loki`
- `grafana` depends on `prometheus`, `loki`, `tempo`
- `backend` includes `OTEL_EXPORTER_OTLP_ENDPOINT` when observability enabled

### Data Flow Architecture

```
[User Browser]
      |
      | HTTP Request
      v
[Frontend Container]
      |
      | API Call (with traceparent header if frontend tracing enabled)
      v
[Backend Container]
      |
      +---> [FastAPIInstrumentor] --> [BatchSpanProcessor] --> [OTLPSpanExporter] --> [Tempo]
      |                                                                                  |
      +---> [MetricsMiddleware] --> [prometheus_client] --> [/metrics endpoint] <-- [Prometheus]
      |                                                                                  |
      +---> [logging.info()] --> [stdout] --> [Docker Log Driver] --> [Promtail] --> [Loki]
      |                                                                                  |
      v                                                                                  v
[Response to User]                                                                 [Grafana]
                                                                                   (visualize)
```

### Network Configuration

All observability services share the existing project network:

```yaml
networks:
  {{ cookiecutter.project_slug }}-network:
    name: {{ cookiecutter.project_slug }}-network
    driver: bridge
```

Internal service communication uses Docker DNS:
- `backend:8000` for metrics scraping
- `tempo:4317` for trace export (gRPC)
- `tempo:4318` for trace export (HTTP)
- `loki:3100` for log push
- `prometheus:9090` for Grafana datasource
- `loki:3100` for Grafana datasource
- `tempo:3200` for Grafana datasource

### Error Handling Strategy

The observability implementation follows the **fail-open** pattern:

1. **Trace Export Failures**: BatchSpanProcessor buffers spans; dropped if buffer full
2. **Metrics Endpoint Failures**: Returns 500 but does not affect application
3. **Log Collection Failures**: Logs still written to stdout; Promtail retries
4. **Grafana Datasource Errors**: Displays error in panel; other panels unaffected

```python
# Example: Graceful degradation in trace export
trace_exporter = OTLPSpanExporter(
    endpoint=OTLP_ENDPOINT,
    insecure=True  # TLS disabled for development
)
trace_provider.add_span_processor(
    BatchSpanProcessor(trace_exporter)
    # BatchSpanProcessor handles export failures internally
    # Logs warning, drops oldest spans if buffer full
)
```

### Testing Considerations

The observability module includes test-mode configuration:

```python
# observability.py test mode detection
if os.getenv("TESTING", "false").lower() == "true":
    # Simplified logging format (no trace context)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
```

Test isolation strategies:
- Environment variable `TESTING=true` disables trace context in logs
- Tests can mock or disable observability setup
- Metrics endpoints remain testable (return Prometheus format)

### Technology Version Compatibility

| Component | Image/Version | Compatibility Notes |
|-----------|---------------|---------------------|
| Prometheus | `prom/prometheus:latest` | Stable API, recommend pinning for production |
| Loki | `grafana/loki:latest` | Schema v13, backward compatible |
| Promtail | `grafana/promtail:latest` | Matches Loki version |
| Tempo | `grafana/tempo:latest` | OTLP v1 support |
| Grafana | `grafana/grafana:latest` | 9.x/10.x compatible datasources |
| opentelemetry-api | `>=1.27.0,<2.0.0` | Stable API |
| opentelemetry-sdk | `>=1.27.0,<2.0.0` | Matches API version |
| prometheus-client | `>=0.20.0,<1.0.0` | Stable exposition format |

### Rationale and Trade-offs

**Decision: Grafana LGTM Stack over alternatives**

| Alternative | Why Not Selected |
|-------------|------------------|
| ELK Stack | Higher resource requirements, complex setup |
| Commercial SaaS (DataDog, New Relic) | Vendor lock-in, ongoing costs, data privacy |
| Jaeger + Prometheus + ELK | More components, no unified visualization |
| Minimal (logs only) | Insufficient for distributed debugging |
| Grafana Cloud | External connectivity required, cost |

**Decision: OpenTelemetry over vendor-specific instrumentation**

- CNCF standard ensures vendor neutrality
- Comprehensive Python ecosystem
- Future-proof (converging instrumentation standards)
- Automatic instrumentation reduces code changes

**Decision: BatchSpanProcessor over SimpleSpanProcessor**

- Batching reduces network overhead
- Async export does not block request processing
- Graceful degradation on export failures
- Configurable batch size and export interval

**Decision: Pull-based metrics (Prometheus) over push-based**

- Prometheus pull model proven at scale
- Scrape targets discoverable and monitorable
- No metric loss on application restart
- Compatible with existing Prometheus ecosystem

### References to Existing Codebase

The technical approach is grounded in these existing implementation files:

| File | Purpose | Location |
|------|---------|----------|
| ADR-002 | Architecture decision record | `/home/ty/workspace/project-starter/implementation-manager/docs/decisions/ADR-002-observability-stack.md` |
| observability.py | Reference backend implementation | `/home/ty/workspace/project-starter/implementation-manager/backend/observability.py` |
| main.py | Integration pattern | `/home/ty/workspace/project-starter/implementation-manager/backend/main.py` |
| prometheus.yml | Scrape configuration | `/home/ty/workspace/project-starter/implementation-manager/observability/prometheus/prometheus.yml` |
| loki-config.yml | Log storage configuration | `/home/ty/workspace/project-starter/implementation-manager/observability/loki/loki-config.yml` |
| promtail-config.yml | Log collection rules | `/home/ty/workspace/project-starter/implementation-manager/observability/promtail/promtail-config.yml` |
| tempo.yml | Tracing backend configuration | `/home/ty/workspace/project-starter/implementation-manager/observability/tempo/tempo.yml` |
| datasources.yml | Grafana datasource provisioning | `/home/ty/workspace/project-starter/implementation-manager/observability/grafana/datasources/datasources.yml` |
| compose.yml | Current template structure | `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/compose.yml` |
| cookiecutter.json | Template configuration | `/home/ty/workspace/project-starter/template/cookiecutter.json` |

---

## Architecture & Integration Considerations

This section defines the system architecture, integration patterns, API contracts, data flows, and deployment considerations for the observability stack integration. The architecture is designed to seamlessly integrate with the existing cookiecutter template structure while providing comprehensive observability capabilities.

### High-Level System Architecture

The observability stack integrates as a parallel infrastructure layer alongside the core application services. The architecture follows the **sidecar pattern** for log collection and the **pull model** for metrics, with **push-based** trace export.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Generated Project                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        Application Layer                                  │   │
│  │                                                                           │   │
│  │   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐  │   │
│  │   │  Frontend   │   │   Backend   │   │  Keycloak   │   │    Redis    │  │   │
│  │   │   (Lit)     │──▶│  (FastAPI)  │──▶│   (OIDC)    │   │   (Cache)   │  │   │
│  │   │   :5173     │   │    :8000    │   │    :8080    │   │    :6379    │  │   │
│  │   └─────────────┘   └──────┬──────┘   └─────────────┘   └─────────────┘  │   │
│  │                            │                                              │   │
│  │                            │ SQL                                          │   │
│  │                            ▼                                              │   │
│  │                     ┌─────────────┐                                       │   │
│  │                     │ PostgreSQL  │                                       │   │
│  │                     │    :5432    │                                       │   │
│  │                     └─────────────┘                                       │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                     Observability Layer (Conditional)                     │   │
│  │                                                                           │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │   │                      Data Collection                             │    │   │
│  │   │                                                                  │    │   │
│  │   │   Prometheus ◀──────── /metrics ◀──────── Backend, Keycloak     │    │   │
│  │   │      :9090            (pull)                                     │    │   │
│  │   │                                                                  │    │   │
│  │   │   Promtail ──────────▶ Loki ◀──────────── Docker Logs           │    │   │
│  │   │                        :3100                                     │    │   │
│  │   │                                                                  │    │   │
│  │   │   Tempo ◀──────────── OTLP ◀──────────── Backend                │    │   │
│  │   │   :3200, :4317               (push)                              │    │   │
│  │   └─────────────────────────────────────────────────────────────────┘    │   │
│  │                                                                           │   │
│  │   ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │   │                      Visualization                               │    │   │
│  │   │                                                                  │    │   │
│  │   │   Grafana ◀──────── Prometheus, Loki, Tempo                     │    │   │
│  │   │     :3000                (datasources)                           │    │   │
│  │   └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                          Shared Network                                   │   │
│  │                   {{ cookiecutter.project_slug }}-network                 │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Architecture

#### Container Topology

When observability is enabled, the generated project includes 10 services (5 application + 5 observability):

| Layer | Container | Image | Ports | Purpose |
|-------|-----------|-------|-------|---------|
| Application | `postgres` | `postgres:{{ cookiecutter.postgres_version }}-alpine` | 5432 | Primary database |
| Application | `keycloak` | `quay.io/keycloak/keycloak:{{ cookiecutter.keycloak_version }}` | 8080 | OAuth/OIDC provider |
| Application | `backend` | Custom FastAPI | 8000 | API server |
| Application | `frontend` | Custom Lit/Vite | 5173 | Web UI |
| Application | `redis` | `redis:{{ cookiecutter.redis_version }}-alpine` | 6379 | Cache layer |
| Observability | `prometheus` | `prom/prometheus:latest` | 9090 | Metrics TSDB |
| Observability | `loki` | `grafana/loki:latest` | 3100 | Log aggregation |
| Observability | `promtail` | `grafana/promtail:latest` | - | Log collector |
| Observability | `tempo` | `grafana/tempo:latest` | 3200, 4317, 4318 | Trace backend |
| Observability | `grafana` | `grafana/grafana:latest` | 3000 | Visualization |

#### Service Dependency Graph

```
                                postgres
                                   │
                                   ▼
                               keycloak ◀───────────────────┐
                                   │                        │
                                   ▼                        │
                    redis ─────▶ backend ◀──────────────────┤
                                   │                        │
                                   ▼                        │
                               frontend                     │
                                                            │
┌─────────────────── Observability Layer ───────────────────┤
│                                                           │
│   loki ◀────────── promtail                              │
│     │                                                     │
│     ├───────────────────┬───────────────────┐            │
│     │                   │                   │            │
│     ▼                   ▼                   ▼            │
│  grafana ◀────────── tempo ◀────────── prometheus ◀──────┘
│                                            │
│                                            │
│               (scrapes /metrics from backend, keycloak)
└──────────────────────────────────────────────────────────
```

**Startup Order Dependencies:**

1. **Independent Tier**: `postgres`, `redis`, `loki`, `tempo`, `prometheus`
2. **Depends on postgres**: `keycloak`
3. **Depends on loki**: `promtail`
4. **Depends on keycloak, postgres, redis**: `backend`
5. **Depends on prometheus, loki, tempo**: `grafana`
6. **Depends on backend**: `frontend`

### Data Flow Architecture

#### Metrics Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Metrics Pipeline                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Backend Process                                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   [HTTP Request] ──▶ [MetricsMiddleware] ──▶ [Route Handler]    │   │
│   │                             │                       │            │   │
│   │                             ▼                       │            │   │
│   │                    [prometheus_client]              │            │   │
│   │                    ┌───────────────────┐            │            │   │
│   │                    │ http_requests_total │           │            │   │
│   │                    │ http_request_duration_seconds │ │            │   │
│   │                    │ active_requests     │           │            │   │
│   │                    └───────────────────┘            │            │   │
│   │                             │                       │            │   │
│   │                             ▼                       │            │   │
│   │                       [/metrics endpoint]           │            │   │
│   │                                                     │            │   │
│   └─────────────────────────────────────────────────────┘            │   │
│                                 │                                     │   │
│                                 │ HTTP GET (every 5s)                │   │
│                                 ▼                                     │   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Prometheus                                                     │   │
│   │   ┌───────────────────────────────────────────────────────────┐ │   │
│   │   │ Scrape Manager │ ──▶ │ TSDB Storage │ ──▶ │ PromQL Engine │ │   │
│   │   └───────────────────────────────────────────────────────────┘ │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                     │   │
│                                 │ PromQL queries                      │   │
│                                 ▼                                     │   │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Grafana Dashboard                                              │   │
│   │   [Request Rate] [Latency p95/p99] [Error Rate] [Active Requests]│   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Metrics Collection Intervals:**

| Target | Scrape Interval | Metrics Path | Purpose |
|--------|-----------------|--------------|---------|
| `backend:8000` | 5 seconds | `/metrics` | Application metrics (responsive dashboards) |
| `keycloak:8080` | 30 seconds | `/metrics` | Auth service metrics |
| `prometheus:9090` | 15 seconds | `/metrics` | Self-monitoring |
| `tempo:3200` | 15 seconds | `/metrics` | Trace backend metrics |
| `loki:3100` | 15 seconds | `/metrics` | Log backend metrics |

#### Logging Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Logging Pipeline                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Application Containers                                                 │
│   ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│   │  backend   │ │  frontend  │ │  keycloak  │ │  postgres  │           │
│   │   stdout   │ │   stdout   │ │   stdout   │ │   stdout   │           │
│   └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────┬──────┘           │
│         │              │              │              │                   │
│         └──────────────┴──────────────┴──────────────┘                   │
│                                 │                                        │
│                                 ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Docker Log Driver (json-file)                                  │   │
│   │   /var/lib/docker/containers/<id>/<id>-json.log                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                        │
│                                 │ File tailing                           │
│                                 ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Promtail                                                       │   │
│   │   ┌─────────────────────────────────────────────────────────┐   │   │
│   │   │ Docker SD │ ──▶ │ Relabel │ ──▶ │ Client (push) │       │   │   │
│   │   │           │     │ (labels)│     │               │       │   │   │
│   │   └─────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                        │
│                                 │ POST /loki/api/v1/push                 │
│                                 ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Loki                                                           │   │
│   │   ┌─────────────────────────────────────────────────────────┐   │   │
│   │   │ Ingester │ ──▶ │ Chunk Store │ ──▶ │ Querier │          │   │   │
│   │   └─────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                        │
│                                 │ LogQL queries                          │
│                                 ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Grafana Explore / Log Explorer Dashboard                       │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**Log Labels Extracted:**

| Label | Source | Example Value |
|-------|--------|---------------|
| `container` | `__meta_docker_container_name` | `my-project-backend` |
| `service` | `__meta_docker_container_label_com_docker_compose_service` | `backend` |
| `stream` | `__meta_docker_container_log_stream` | `stdout`, `stderr` |

#### Tracing Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Tracing Pipeline                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Backend Process                                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                                                                  │   │
│   │   [HTTP Request] ──▶ [FastAPIInstrumentor] ──▶ [Route Handler]  │   │
│   │         │                    │                        │          │   │
│   │         │                    ▼                        │          │   │
│   │         │            [TracerProvider]                 │          │   │
│   │         │            ┌──────────────┐                 │          │   │
│   │         │            │  Span Start  │                 │          │   │
│   │         │            │  trace_id    │                 │          │   │
│   │         │            │  span_id     │                 │          │   │
│   │         │            │  attributes  │                 │          │   │
│   │         │            └──────┬───────┘                 │          │   │
│   │         │                   │                         │          │   │
│   │         │                   ▼                         │          │   │
│   │         │           [BatchSpanProcessor]              │          │   │
│   │         │           (buffer, async export)            │          │   │
│   │         │                   │                         │          │   │
│   │   ┌─────▼─────────────────────────────────────────────▼─────┐   │   │
│   │   │              [logging with trace context]                │   │   │
│   │   │   format: "... trace_id=%(otelTraceID)s span_id=..."    │   │   │
│   │   └──────────────────────────────────────────────────────────┘   │   │
│   │                             │                                     │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                        │
│                                 │ OTLP/gRPC (batched, async)            │
│                                 ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Tempo                                                          │   │
│   │   ┌─────────────────────────────────────────────────────────┐   │   │
│   │   │ OTLP Receiver │ ──▶ │ Ingester │ ──▶ │ Block Store │   │   │   │
│   │   │   :4317 gRPC  │     │          │     │             │   │   │   │
│   │   │   :4318 HTTP  │     │          │     │             │   │   │   │
│   │   └─────────────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                 │                                        │
│                                 │ TraceQL queries                        │
│                                 ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │   Grafana Explore / Trace Explorer Dashboard                     │   │
│   │   [Trace Search] [Flame Graph] [Service Map] [Trace-Log Link]   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Integration Patterns

#### Backend Instrumentation Integration

The observability module integrates at the FastAPI application initialization phase:

```python
# main.py (when observability is enabled)
from fastapi import FastAPI
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}

app = FastAPI(
    title="{{ cookiecutter.project_name }}",
    # ... other configuration
)

{% if cookiecutter.include_observability == "yes" %}
# Setup observability BEFORE other middleware
# This ensures all requests are instrumented
setup_observability(app)
{% endif %}

# Register other middleware and routers
# ...
```

**Integration Points in `observability.py`:**

| Component | Integration Point | Purpose |
|-----------|-------------------|---------|
| `TracerProvider` | Module initialization | Global tracing configuration |
| `FastAPIInstrumentor` | `setup_observability()` | Automatic request tracing |
| `MetricsMiddleware` | `@app.middleware("http")` | Request counting and timing |
| `/metrics` endpoint | `@app.get("/metrics")` | Prometheus scrape target |
| Logging | `logging.basicConfig()` | Trace context in logs |

#### Docker Compose Integration

The observability services integrate via conditional Jinja2 blocks:

```yaml
# compose.yml template structure

services:
  # === Core Application Services ===
  postgres:
    # ... (always present)

  keycloak:
    # ... (always present)

  backend:
    # ... (always present)
    environment:
      # ... existing environment variables
{% if cookiecutter.include_observability == "yes" %}
      # OpenTelemetry Configuration
      OTEL_SERVICE_NAME: backend
      OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317
{% endif %}

  frontend:
    # ... (always present)

  redis:
    # ... (always present)

{% if cookiecutter.include_observability == "yes" %}
  # === Observability Services ===
  prometheus:
    image: prom/prometheus:latest
    container_name: {{ cookiecutter.project_slug }}-prometheus
    # ... full configuration

  loki:
    image: grafana/loki:latest
    container_name: {{ cookiecutter.project_slug }}-loki
    # ... full configuration

  promtail:
    image: grafana/promtail:latest
    container_name: {{ cookiecutter.project_slug }}-promtail
    depends_on:
      - loki
    # ... full configuration

  tempo:
    image: grafana/tempo:latest
    container_name: {{ cookiecutter.project_slug }}-tempo
    # ... full configuration

  grafana:
    image: grafana/grafana:latest
    container_name: {{ cookiecutter.project_slug }}-grafana
    depends_on:
      - prometheus
      - loki
      - tempo
    # ... full configuration
{% endif %}

volumes:
  postgres_data:
    # ... (always present)
  # ... other core volumes

{% if cookiecutter.include_observability == "yes" %}
  prometheus-data:
    name: {{ cookiecutter.project_slug }}-prometheus-data
  loki-data:
    name: {{ cookiecutter.project_slug }}-loki-data
  tempo-data:
    name: {{ cookiecutter.project_slug }}-tempo-data
  grafana-data:
    name: {{ cookiecutter.project_slug }}-grafana-data
{% endif %}
```

### API Contracts and Interfaces

#### Prometheus Metrics Endpoint

**Endpoint:** `GET /metrics`

**Response Format:** Prometheus Exposition Format (text/plain)

```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/v1/health",status="200"} 42.0
http_requests_total{method="POST",endpoint="/api/v1/todos",status="201"} 15.0
http_requests_total{method="GET",endpoint="/api/v1/todos",status="200"} 128.0

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/health",le="0.005"} 40.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/health",le="0.01"} 42.0
http_request_duration_seconds_bucket{method="GET",endpoint="/api/v1/health",le="+Inf"} 42.0
http_request_duration_seconds_sum{method="GET",endpoint="/api/v1/health"} 0.125
http_request_duration_seconds_count{method="GET",endpoint="/api/v1/health"} 42.0

# HELP active_requests Number of active requests
# TYPE active_requests gauge
active_requests 3.0
```

#### OTLP Trace Export Interface

**Protocol:** gRPC (primary) / HTTP (fallback)
**Endpoint:** `tempo:4317` (gRPC) or `tempo:4318` (HTTP)

**Span Attributes (OpenTelemetry HTTP Semantic Conventions):**

| Attribute | Type | Example Value |
|-----------|------|---------------|
| `http.method` | string | `"GET"` |
| `http.url` | string | `"http://backend:8000/api/v1/todos"` |
| `http.route` | string | `"/api/v1/todos"` |
| `http.status_code` | int | `200` |
| `http.request_content_length` | int | `256` |
| `http.response_content_length` | int | `1024` |
| `service.name` | string | `"backend"` |

#### Grafana Datasource API

**Datasource UIDs (used for cross-datasource correlation):**

| Datasource | UID | Type | URL |
|------------|-----|------|-----|
| Prometheus | `prometheus` | `prometheus` | `http://prometheus:9090` |
| Loki | `loki` | `loki` | `http://loki:3100` |
| Tempo | `tempo` | `tempo` | `http://tempo:3200` |

**Correlation Configuration in Tempo Datasource:**

```yaml
jsonData:
  tracesToLogsV2:
    datasourceUid: 'loki'
    spanStartTimeShift: '-1h'
    spanEndTimeShift: '1h'
    filterByTraceID: true
  tracesToMetrics:
    datasourceUid: 'prometheus'
  serviceMap:
    datasourceUid: 'prometheus'
  nodeGraph:
    enabled: true
```

### Network Architecture

#### Internal Service Communication

All services communicate via the Docker bridge network `{{ cookiecutter.project_slug }}-network`:

| Source | Destination | Protocol | Port | Purpose |
|--------|-------------|----------|------|---------|
| `prometheus` | `backend` | HTTP | 8000 | Metrics scraping |
| `prometheus` | `keycloak` | HTTP | 8080 | Metrics scraping |
| `prometheus` | `tempo` | HTTP | 3200 | Metrics scraping |
| `prometheus` | `loki` | HTTP | 3100 | Metrics scraping |
| `promtail` | `loki` | HTTP | 3100 | Log push |
| `backend` | `tempo` | gRPC | 4317 | Trace export |
| `grafana` | `prometheus` | HTTP | 9090 | Datasource queries |
| `grafana` | `loki` | HTTP | 3100 | Datasource queries |
| `grafana` | `tempo` | HTTP | 3200 | Datasource queries |

#### External Port Exposure

| Service | Default Host Port | Container Port | Purpose |
|---------|-------------------|----------------|---------|
| `grafana` | 3000 | 3000 | Dashboard access |
| `prometheus` | 9090 | 9090 | Direct queries, targets UI |
| `tempo` | 3200 | 3200 | Trace API access |
| `tempo` | 4317 | 4317 | OTLP gRPC (for external clients) |
| `tempo` | 4318 | 4318 | OTLP HTTP (for browser traces) |
| `loki` | 3100 | 3100 | Log queries, push API |

### Performance Considerations

#### Resource Allocation Guidelines

**Development Environment (default configuration):**

| Service | Memory Limit | CPU Limit | Rationale |
|---------|-------------|-----------|-----------|
| `prometheus` | 512MB | 0.5 | Handles ~1000 metrics series |
| `loki` | 256MB | 0.3 | Low log volume in dev |
| `promtail` | 128MB | 0.1 | Lightweight log forwarding |
| `tempo` | 512MB | 0.5 | Handles ~100 traces/min |
| `grafana` | 512MB | 0.5 | Dashboard rendering |
| **Total** | **~2GB** | **~2 cores** | |

#### Batching and Buffering Configuration

| Component | Setting | Value | Impact |
|-----------|---------|-------|--------|
| Prometheus | Scrape interval (backend) | 5s | Near real-time metrics |
| Prometheus | Scrape interval (others) | 15s | Reduced load |
| Promtail | Batch wait | 1s | Log latency |
| Promtail | Batch size | 1MB | Network efficiency |
| OpenTelemetry | Batch export interval | 5s | Trace latency |
| OpenTelemetry | Max queue size | 2048 spans | Buffer for spikes |

### Scalability Architecture

#### Horizontal Scaling Considerations

The development configuration uses single-instance deployments. For production scaling:

| Component | Scaling Strategy | Configuration Change |
|-----------|------------------|---------------------|
| Prometheus | Federation / Thanos | External datasource URL |
| Loki | Microservices mode | Multiple targets, S3 storage |
| Tempo | Distributed mode | Multiple targets, S3 storage |
| Grafana | Stateless replicas | External database for sessions |

**Production Scaling Guidance (documentation only, not implemented):**

```yaml
# Example production Prometheus with remote write
# (not included in template, for documentation)
prometheus:
  environment:
    - REMOTE_WRITE_URL=https://cortex.example.com/api/v1/push
```

#### Data Retention Strategy

| Component | Development Retention | Production Recommendation |
|-----------|----------------------|--------------------------|
| Prometheus | 15 days (storage-based) | 30-90 days with remote storage |
| Loki | 24 hours | 30-90 days with S3 |
| Tempo | 1 hour blocks | 7-30 days with S3 |
| Grafana | N/A (stateless) | External PostgreSQL |

### Security Architecture

#### Development Mode Security Profile

The default configuration prioritizes developer convenience over security:

| Aspect | Development Setting | Security Implication |
|--------|---------------------|---------------------|
| Grafana auth | Anonymous admin | No authentication required |
| Metrics endpoint | Unauthenticated | Open access to `/metrics` |
| OTLP endpoint | Insecure (no TLS) | Unencrypted trace data |
| Log access | No ACL | All logs visible |

#### Production Security Recommendations (Documentation)

The generated documentation includes production security guidance:

1. **Grafana Authentication**: Disable anonymous access, enable SSO
2. **Metrics Endpoint**: Network isolation or authentication proxy
3. **OTLP Transport**: Enable TLS for trace export
4. **Log Access**: Role-based access via Grafana org roles
5. **Network Segmentation**: Separate observability network

### Failure Modes and Recovery

#### Graceful Degradation Behavior

| Failure Scenario | Application Impact | Observability Impact |
|-----------------|-------------------|---------------------|
| Tempo unavailable | None | Traces not recorded (spans dropped) |
| Prometheus unavailable | None | Metrics not collected |
| Loki unavailable | None | Logs not aggregated (still in Docker) |
| Promtail unavailable | None | Logs not aggregated |
| Grafana unavailable | None | Dashboards inaccessible |

**Implementation Details:**

```python
# BatchSpanProcessor handles Tempo failures gracefully
trace_provider.add_span_processor(
    BatchSpanProcessor(
        trace_exporter,
        max_queue_size=2048,  # Buffer during outages
        max_export_batch_size=512,
        schedule_delay_millis=5000
    )
)
# Drops oldest spans if buffer overflows; no exceptions raised
```

#### Recovery Procedures

| Component | Recovery Action | Data Recovery |
|-----------|-----------------|---------------|
| Prometheus restart | Automatic | TSDB recovers from disk |
| Loki restart | Automatic | Chunks recovered from disk |
| Tempo restart | Automatic | Blocks recovered from disk |
| Promtail restart | Automatic | Resumes from positions file |
| Grafana restart | Automatic | State in volume |

### Template File Mapping

#### Files Created When Observability is Enabled

```
{{ cookiecutter.project_slug }}/
├── observability/
│   ├── prometheus/
│   │   └── prometheus.yml           # Prometheus scrape configuration
│   ├── loki/
│   │   └── loki-config.yml          # Loki storage configuration
│   ├── promtail/
│   │   └── promtail-config.yml      # Docker log collection
│   ├── tempo/
│   │   └── tempo.yml                # Tracing backend configuration
│   └── grafana/
│       ├── datasources/
│       │   └── datasources.yml      # Pre-configured datasources
│       └── dashboards/
│           ├── dashboards.yml       # Dashboard provisioning config
│           ├── backend-dashboard.json
│           ├── slo-dashboard.json
│           ├── log-explorer-dashboard.json
│           └── trace-explorer-dashboard.json
├── backend/
│   └── app/
│       └── observability.py         # Backend instrumentation module
└── compose.yml                      # Updated with observability services
```

#### Template Source to Destination Mapping

| Source (implementation-manager/) | Destination (template/) |
|----------------------------------|-------------------------|
| `observability/prometheus/prometheus.yml` | `observability/prometheus/prometheus.yml` (templatized) |
| `observability/loki/loki-config.yml` | `observability/loki/loki-config.yml` |
| `observability/promtail/promtail-config.yml` | `observability/promtail/promtail-config.yml` (templatized) |
| `observability/tempo/tempo.yml` | `observability/tempo/tempo.yml` |
| `observability/grafana/datasources/datasources.yml` | `observability/grafana/datasources/datasources.yml` |
| `backend/observability.py` | `backend/app/observability.py` (templatized) |
| N/A | `observability/grafana/dashboards/*.json` (new) |

### Integration with Existing Template Components

#### Interaction with Health Check Endpoint

The existing `/api/v1/health` endpoint is automatically instrumented:

- Prometheus metrics track health check request count and latency
- Traces capture health check spans
- Health check logs include trace context

#### Interaction with Authentication (Keycloak)

- Keycloak metrics are scraped by Prometheus
- Authentication flow traces are captured (when frontend tracing is added later)
- Auth error logs are aggregated in Loki

#### Interaction with Redis Cache

- Redis is not directly instrumented in the initial scope
- Future enhancement: Redis instrumentation for cache hit/miss metrics
- Cache-related logs are captured via Docker log collection

#### Interaction with PostgreSQL

- Database query tracing is not included (out of scope)
- PostgreSQL logs are captured via Docker log collection
- Future enhancement: SQLAlchemy instrumentation for query tracing

### Architecture Decision Records Reference

This architecture is grounded in the following ADR:

| ADR | Title | Key Decisions |
|-----|-------|---------------|
| ADR-002 | Observability Stack Implementation | Grafana LGTM stack selection, OpenTelemetry for tracing, BatchSpanProcessor for reliability, pull-based metrics |

**Key Architectural Principles from ADR-002:**

1. **Unified Visualization**: All telemetry data accessible through Grafana
2. **Vendor Neutrality**: Open-source stack, CNCF standards (OpenTelemetry)
3. **Graceful Degradation**: Application continues when observability fails
4. **Minimal Overhead**: Batching, async export, efficient protocols
5. **Developer Experience**: Zero-config development, pre-built dashboards

---

## Data Models & Schema Changes

This section defines the data models and schema considerations for the observability stack integration. Unlike typical features that add database tables, the observability integration primarily uses **external storage backends** managed by observability services (Prometheus, Loki, Tempo) rather than the application PostgreSQL database.

### Overview: No Application Database Changes Required

The observability stack integration does **not** require any changes to the existing PostgreSQL database schema. All observability data is stored in dedicated storage backends:

| Data Type | Storage Backend | Storage Format | Persistence |
|-----------|----------------|----------------|-------------|
| Metrics | Prometheus TSDB | Time-series data | `prometheus-data` volume |
| Logs | Loki Chunks | TSDB with filesystem storage | `loki-data` volume |
| Traces | Tempo Blocks | Object storage (local filesystem) | `tempo-data` volume |
| Dashboards & Preferences | Grafana SQLite | SQLite database | `grafana-data` volume |

**Rationale**: Separating observability data from application data provides:
1. Independent scaling of observability storage
2. No impact on application database performance
3. Clear data ownership and lifecycle management
4. Ability to rebuild observability data from scratch without affecting application state

---

### Prometheus Metrics Data Model

Prometheus uses a dimensional time-series data model where each metric is identified by a metric name and a set of key-value labels.

#### Backend Application Metrics Schema

The observability module defines the following metrics with their label schemas:

##### FR-DM-001: HTTP Request Counter Schema

```
Metric Name: http_requests_total
Type: Counter
Description: Total count of HTTP requests processed by the backend

Labels:
  - method (string): HTTP method (GET, POST, PUT, DELETE, PATCH, OPTIONS)
  - endpoint (string): Request path (e.g., /api/v1/todos, /api/v1/health)
  - status (string): HTTP response status code (200, 201, 400, 401, 404, 500)

Example Series:
  http_requests_total{method="GET", endpoint="/api/v1/todos", status="200"} 1523
  http_requests_total{method="POST", endpoint="/api/v1/oauth/token", status="401"} 12
  http_requests_total{method="GET", endpoint="/api/v1/health", status="200"} 8640
```

**Cardinality Considerations**:
- Method: 7 distinct values (bounded)
- Status: ~20 distinct values (bounded by HTTP specification)
- Endpoint: Variable based on API routes (bounded by application design)
- Estimated unique series: < 500 for typical applications

##### FR-DM-002: HTTP Request Duration Histogram Schema

```
Metric Name: http_request_duration_seconds
Type: Histogram
Description: Duration of HTTP request processing in seconds

Labels:
  - method (string): HTTP method
  - endpoint (string): Request path

Default Buckets: [.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0]

Generated Series (per label combination):
  http_request_duration_seconds_bucket{method="GET", endpoint="/api/v1/todos", le="0.005"} 100
  http_request_duration_seconds_bucket{method="GET", endpoint="/api/v1/todos", le="0.01"} 250
  ... (one for each bucket)
  http_request_duration_seconds_bucket{method="GET", endpoint="/api/v1/todos", le="+Inf"} 1523
  http_request_duration_seconds_sum{method="GET", endpoint="/api/v1/todos"} 152.3
  http_request_duration_seconds_count{method="GET", endpoint="/api/v1/todos"} 1523
```

**Cardinality Note**: Histograms generate multiple series per label combination (default 14 buckets + sum + count = 16 series per unique method/endpoint pair).

##### FR-DM-003: Active Requests Gauge Schema

```
Metric Name: active_requests
Type: Gauge
Description: Current number of in-flight HTTP requests

Labels: None (global gauge)

Example Series:
  active_requests 5
```

**Cardinality**: Single series (cardinality = 1)

#### Prometheus Storage Schema

Prometheus stores metrics in its Time-Series Database (TSDB) with the following characteristics:

| Property | Value | Configuration Location |
|----------|-------|----------------------|
| Data Directory | `/prometheus` | Volume mount |
| Retention Time | 15 days (default) | `--storage.tsdb.retention.time=15d` |
| Block Duration | 2 hours | Default compaction |
| Chunk Encoding | XOR encoding | Built-in |
| Index Format | Label-based inverted index | Built-in |

**Storage Growth Estimation**:
- ~1-2 bytes per sample
- 5-second scrape interval = 12 samples/minute
- ~500 unique series = 6,000 samples/minute = ~10 KB/minute
- ~14 MB/day at development traffic levels

---

### OpenTelemetry Trace Data Model

Traces follow the OpenTelemetry Protocol (OTLP) specification and are stored in Tempo.

#### Span Attribute Schema

The backend instrumentation generates spans with the following attribute schema, conforming to [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/):

##### FR-DM-004: HTTP Server Span Attributes

```yaml
# Resource Attributes (attached to all spans from the service)
resource:
  service.name: "backend"  # From OTEL_SERVICE_NAME
  service.version: "1.0.0"  # Optional, from application
  deployment.environment: "development"  # Optional

# Span Attributes (attached to individual spans)
span_attributes:
  # HTTP Semantic Conventions
  http.request.method: "GET"  # HTTP method
  url.path: "/api/v1/todos"  # Request path
  url.scheme: "http"  # http or https
  server.address: "localhost"  # Server hostname
  server.port: 8000  # Server port
  http.response.status_code: 200  # Response status

  # Network Attributes
  client.address: "172.18.0.1"  # Client IP
  network.protocol.version: "1.1"  # HTTP version

  # Custom Attributes (application-specific)
  tenant.id: "tenant-uuid"  # Extracted from JWT
  user.id: "user-uuid"  # Extracted from JWT (if applicable)
```

##### FR-DM-005: Span Structure

```json
{
  "traceId": "32-character-hex-string",
  "spanId": "16-character-hex-string",
  "parentSpanId": "16-character-hex-string-or-empty",
  "name": "GET /api/v1/todos",
  "kind": "SPAN_KIND_SERVER",
  "startTimeUnixNano": 1701619200000000000,
  "endTimeUnixNano": 1701619200050000000,
  "attributes": [
    {"key": "http.request.method", "value": {"stringValue": "GET"}},
    {"key": "http.response.status_code", "value": {"intValue": 200}},
    {"key": "url.path", "value": {"stringValue": "/api/v1/todos"}}
  ],
  "status": {
    "code": "STATUS_CODE_OK"
  },
  "resource": {
    "attributes": [
      {"key": "service.name", "value": {"stringValue": "backend"}}
    ]
  }
}
```

#### Tempo Storage Schema

Tempo uses a block-based storage format optimized for trace data:

| Property | Value | Configuration Location |
|----------|-------|----------------------|
| Blocks Directory | `/tmp/tempo/blocks` | `tempo.yml` |
| WAL Directory | `/tmp/tempo/wal` | `tempo.yml` |
| Block Retention | 1 hour | `compactor.compaction.block_retention` |
| Max Block Duration | 5 minutes | `ingester.max_block_duration` |
| Backend | Local filesystem | `storage.trace.backend` |

**Storage Format**:
- Traces are batched into blocks
- Blocks are parquet-based columnar storage
- Compressed with Snappy or ZSTD
- Indexed by trace ID and service name

**Storage Growth Estimation**:
- ~1 KB per trace (with 5-10 spans)
- Development traffic: ~100 traces/hour = ~2.4 MB/day
- Block compaction reclaims space from deleted traces

---

### Log Data Model (Loki)

Loki uses a log aggregation model where logs are indexed by labels rather than full-text indexing.

#### Log Entry Schema

##### FR-DM-006: Log Stream Labels

```yaml
# Labels extracted by Promtail from Docker metadata
labels:
  container: "myproject-backend"  # Docker container name
  service: "backend"  # Docker Compose service name
  stream: "stdout"  # stdout or stderr

# Optional labels (if parsing is configured)
  level: "INFO"  # Log level (extracted from log content)
  trace_id: "32-character-hex"  # Trace correlation (extracted from log content)
```

##### FR-DM-007: Structured Log Format

When observability is enabled, the backend produces structured logs with trace context:

```
2024-12-03 10:30:45,123 - app.api.routers.todos - INFO - Todo created successfully - trace_id=abc123def456... span_id=1234567890abcdef
```

**Log Fields**:
| Field | Format | Description |
|-------|--------|-------------|
| Timestamp | ISO 8601 | Log emission time |
| Logger Name | Dotted path | Python module path |
| Level | String | INFO, WARNING, ERROR, DEBUG |
| Message | String | Log message content |
| trace_id | 32-char hex | OpenTelemetry trace ID |
| span_id | 16-char hex | OpenTelemetry span ID |

**Note**: The default log format is human-readable. JSON structured logging can be configured as a future enhancement (out of scope for initial integration).

#### Loki Storage Schema

Loki stores logs using a chunk-based storage format:

| Property | Value | Configuration Location |
|----------|-------|----------------------|
| Chunks Directory | `/loki/chunks` | `loki-config.yml` |
| Rules Directory | `/loki/rules` | `loki-config.yml` |
| Schema Version | v13 | `schema_config.configs[].schema` |
| Index Prefix | `index_` | `schema_config.configs[].index.prefix` |
| Index Period | 24 hours | `schema_config.configs[].index.period` |
| Object Store | Filesystem | `schema_config.configs[].object_store` |
| Store Type | TSDB | `schema_config.configs[].store` |

**Storage Growth Estimation**:
- Log compression ratio: ~10:1
- Development log volume: ~50 MB raw/day = ~5 MB stored/day
- Index overhead: ~5% of log volume

---

### Grafana Data Model

Grafana persists configuration and user preferences in an embedded SQLite database.

#### Grafana Persistence Schema

##### FR-DM-008: Grafana State Storage

| Data Type | Storage | Persistence |
|-----------|---------|-------------|
| Datasources | Provisioned YAML + SQLite | Read-only from YAML, user changes in SQLite |
| Dashboards | Provisioned JSON + SQLite | Read-only from JSON, user changes in SQLite |
| User Preferences | SQLite | Anonymous user settings |
| Annotations | SQLite | Dashboard annotations |
| Alerts (if configured) | SQLite | Alert states and history |

**Volume**: `grafana-data` mounted at `/var/lib/grafana`

**Database Location**: `/var/lib/grafana/grafana.db` (SQLite)

##### FR-DM-009: Dashboard JSON Schema

Grafana dashboards follow the Grafana Dashboard JSON Model:

```json
{
  "id": null,
  "uid": "backend-service-dashboard",
  "title": "Backend Service Dashboard",
  "tags": ["backend", "observability"],
  "timezone": "browser",
  "schemaVersion": 39,
  "version": 1,
  "refresh": "10s",
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "panels": [
    {
      "id": 1,
      "type": "timeseries",
      "title": "Request Rate",
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "targets": [
        {
          "expr": "rate(http_requests_total[5m])",
          "legendFormat": "{{method}} {{endpoint}}"
        }
      ],
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
    }
  ],
  "templating": {
    "list": []
  },
  "annotations": {
    "list": []
  }
}
```

**Compatibility**: Dashboards are compatible with Grafana 9.x and 10.x.

---

### Datasource Correlation Configuration

#### FR-DM-010: Tempo-to-Loki Correlation Schema

The Tempo datasource is configured with correlation links to Loki:

```yaml
# datasources.yml
- name: Tempo
  uid: tempo
  type: tempo
  jsonData:
    tracesToLogsV2:
      datasourceUid: 'loki'
      spanStartTimeShift: '-1h'  # Search logs from 1 hour before span
      spanEndTimeShift: '1h'     # Search logs up to 1 hour after span
      filterByTraceID: true      # Filter logs by trace_id field
      filterBySpanID: false      # Do not filter by span_id
      customQuery: true
      query: '{service="backend"} | trace_id=`${__trace.traceId}`'
```

**Correlation Requirements**:
1. Backend logs must include `trace_id` in log message
2. Loki must be able to parse trace_id (default: string matching)
3. Time window allows for clock skew between services

#### FR-DM-011: Tempo-to-Prometheus Correlation Schema

```yaml
# datasources.yml (continued)
    tracesToMetrics:
      datasourceUid: 'prometheus'
      spanStartTimeShift: '-5m'
      spanEndTimeShift: '5m'
      queries:
        - name: 'Request Rate'
          query: 'rate(http_requests_total{endpoint="${__span.tags.url.path}"}[5m])'
        - name: 'Duration'
          query: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{endpoint="${__span.tags.url.path}"}[5m]))'
```

---

### Configuration File Data Models

#### FR-DM-012: Prometheus Scrape Configuration Schema

```yaml
# prometheus.yml - Scrape configuration data model
global:
  scrape_interval: 15s      # Default interval between scrapes
  evaluation_interval: 15s  # How often to evaluate rules
  external_labels:
    cluster: '{{ cookiecutter.project_slug }}'  # Label added to all metrics

scrape_configs:
  - job_name: string            # Unique job identifier
    static_configs:
      - targets: [string]       # List of host:port endpoints
    metrics_path: string        # Path to metrics endpoint (default: /metrics)
    scrape_interval: duration   # Override global interval
    scrape_timeout: duration    # Timeout for scrape (default: 10s)
    scheme: string              # http or https (default: http)
```

#### FR-DM-013: Loki Index Schema Configuration

```yaml
# loki-config.yml - Schema configuration
schema_config:
  configs:
    - from: "2020-10-24"        # Date this schema becomes active
      store: tsdb               # Storage engine (tsdb, boltdb-shipper)
      object_store: filesystem  # Object storage backend
      schema: v13               # Schema version
      index:
        prefix: index_          # Index file prefix
        period: 24h             # Index rotation period
```

**Schema Version Notes**:
- v13 is the current stable schema
- Provides efficient label-based indexing
- Supports both single-tenant and multi-tenant modes

---

### Environment Variable Data Model

#### FR-DM-014: Backend Observability Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OTEL_SERVICE_NAME` | String | `backend` | Service name in traces and metrics |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | URL | `http://tempo:4317` | Tempo OTLP gRPC endpoint |
| `TESTING` | Boolean | `false` | Disable trace context in test mode |

#### FR-DM-015: Grafana Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `GF_AUTH_ANONYMOUS_ENABLED` | Boolean | `true` | Enable anonymous access |
| `GF_AUTH_ANONYMOUS_ORG_ROLE` | String | `Admin` | Role for anonymous users |
| `GF_AUTH_DISABLE_LOGIN_FORM` | Boolean | `true` | Hide login form |
| `GF_SECURITY_ADMIN_PASSWORD` | String | `admin` | Admin password (production) |

---

### Data Retention Policies

#### FR-DM-016: Retention Configuration

| Service | Data Type | Default Retention | Configuration |
|---------|-----------|-------------------|---------------|
| Prometheus | Metrics | 15 days | `--storage.tsdb.retention.time` |
| Loki | Logs | Unlimited (chunk-based) | `limits_config.retention_period` |
| Tempo | Traces | 1 hour (blocks) | `compactor.compaction.block_retention` |
| Grafana | Dashboards | Unlimited | N/A (configuration) |

**Production Recommendations**:
- Prometheus: 30-90 days based on compliance requirements
- Loki: 7-30 days for operational logs
- Tempo: 24-72 hours (traces are high-volume, low-retention)

---

### Data Migration Considerations

Since the observability stack uses **external storage backends** rather than the application database, there are no database migrations required. However, the following considerations apply:

#### FR-DM-017: Zero-Migration Design

| Aspect | Consideration |
|--------|---------------|
| Application Database | No changes to PostgreSQL schema |
| Existing Migrations | Unaffected; Alembic migrations continue to work |
| Data Isolation | Observability data is completely separate from application data |
| Rollback | Removing observability has no impact on application database |

#### FR-DM-018: Volume Initialization

When observability is first enabled on a generated project:

1. **Prometheus**: Starts with empty TSDB; begins collecting metrics immediately
2. **Loki**: Starts with empty chunks; logs begin flowing via Promtail
3. **Tempo**: Starts with empty blocks; traces begin flowing from backend
4. **Grafana**: Initializes SQLite DB; provisions datasources and dashboards from YAML/JSON

No manual initialization or seeding is required.

---

### Schema Compatibility and Evolution

#### FR-DM-019: Metric Schema Evolution Guidelines

Following [OpenTelemetry best practices for schema management](https://betterstack.com/community/guides/observability/opentelemetry-best-practices/):

| Change Type | Approach | Example |
|-------------|----------|---------|
| Add new metric | Add new metric name | `http_request_size_bytes` |
| Add label to existing metric | Version metric name | `http_requests_total_v2` |
| Remove label | Deprecated with suffix | `http_requests_total` (keep), document deprecation |
| Change metric type | New metric name | `request_duration_histogram` instead of `request_duration_gauge` |

**Semantic Convention Alignment**:
- Follow [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) for attribute naming
- Use standard attribute names where applicable (e.g., `http.request.method` not `method`)
- Document any custom attributes with clear naming rationale

#### FR-DM-020: Dashboard Schema Compatibility

- Dashboard JSON is versioned via `schemaVersion` field
- Grafana maintains backward compatibility for dashboard imports
- Template includes dashboards tested with Grafana 9.x and 10.x
- Panel plugins use built-in types (timeseries, gauge, logs, table, stat)

---

### Summary: Schema Impact Assessment

| Component | Schema Change Required | Migration Required | Storage Location |
|-----------|----------------------|-------------------|-----------------|
| PostgreSQL | No | No | N/A |
| Prometheus | N/A (new service) | N/A | `prometheus-data` volume |
| Loki | N/A (new service) | N/A | `loki-data` volume |
| Tempo | N/A (new service) | N/A | `tempo-data` volume |
| Grafana | N/A (new service) | N/A | `grafana-data` volume |
| Backend App | No DB changes | No | In-memory metrics/traces |

**Conclusion**: The observability stack integration is a **zero-migration feature** that adds observability capabilities without modifying the application database schema. All telemetry data is stored in purpose-built backends optimized for their respective data types.

---

## UI/UX Considerations

This section defines the user interface and user experience considerations for the observability stack integration. Since the observability stack centers on Grafana as the primary visualization platform, this section focuses on dashboard design, navigation patterns, and the developer experience of interacting with observability tooling.

### Design Philosophy

The observability UX follows three core principles aligned with [Grafana dashboard best practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/):

1. **Purpose-Driven Design**: Every dashboard tells a story or answers a specific question. Dashboards progress logically from general overview to specific details.

2. **Audience-Centered**: Different personas (Application Developer, On-Call Engineer, SRE) have distinct needs. Dashboards are designed for specific use cases rather than trying to serve all audiences.

3. **Zero-Friction Access**: Observability should "just work" in development without authentication barriers, complex navigation, or manual configuration.

---

### Grafana Dashboard Design Standards

#### UX-001: Dashboard Naming Convention

All pre-built dashboards shall follow a consistent naming pattern for discoverability:

| Dashboard | Name | Tags |
|-----------|------|------|
| Backend health and performance | Backend Service Dashboard | `backend`, `fastapi`, `service` |
| SLO monitoring | SLO Overview Dashboard | `slo`, `reliability`, `sre` |
| Log exploration | Log Explorer Dashboard | `logs`, `loki`, `debugging` |
| Trace exploration | Trace Explorer Dashboard | `traces`, `tempo`, `debugging` |

**Rationale**: Consistent naming enables developers to quickly find relevant dashboards. Tags enable filtering when dashboard count grows.

#### UX-002: Dashboard Layout Grid

Dashboards shall use a consistent 24-column grid layout following Grafana conventions:

| Zone | Width | Purpose | Typical Panels |
|------|-------|---------|----------------|
| Overview Row | 24 columns | High-level status at a glance | Stat panels (total requests, error rate, uptime) |
| Primary Metrics Row | 12 columns x 2 | Key performance indicators | Time series graphs (request rate, latency) |
| Detail Row | 12 columns x 2 | Deeper investigation | Error breakdowns, active requests |
| Logs/Traces Row | 24 columns | Related observability data | Logs panel, trace links |

**Standard Panel Heights:**
- Stat panels: 4 units
- Time series graphs: 8 units
- Logs panels: 8-12 units
- Tables: 8 units

#### UX-003: Visual Hierarchy

Dashboards shall implement a clear visual hierarchy:

1. **Top Row**: Summary statistics using Stat panels (large numbers, color-coded thresholds)
2. **Middle Rows**: Time-series visualizations showing trends
3. **Bottom Row**: Detail tables, logs, or drill-down panels

**Color Coding Standards:**

| Metric State | Color | Hex Value | Usage |
|--------------|-------|-----------|-------|
| Healthy/Normal | Green | `#73BF69` | SLO within target, low error rate |
| Warning | Yellow/Orange | `#FADE2A` / `#FF9830` | Approaching threshold, elevated latency |
| Critical/Error | Red | `#F2495C` | SLO breached, high error rate |
| Neutral/Info | Blue | `#5794F2` | Informational metrics, traffic volume |

#### UX-004: Dashboard Time Controls

All dashboards shall implement consistent time controls:

| Setting | Default Value | Purpose |
|---------|---------------|---------|
| Default time range | `now-1h` to `now` | Shows recent activity without overwhelming data |
| Auto-refresh | `10s` | Responsive real-time updates |
| Time zone | `browser` | Respects developer's local time |

**Time Range Quick-Select Presets:**
- Last 5 minutes (debugging active issues)
- Last 1 hour (default development view)
- Last 24 hours (daily review)
- Last 7 days (trend analysis)

---

### Dashboard-Specific UX Requirements

#### UX-005: Backend Service Dashboard Layout

The Backend Service Dashboard shall prioritize the [RED method](https://grafana.com/blog/2024/07/03/getting-started-with-grafana-best-practices-to-design-your-first-dashboard/) (Rate, Errors, Duration):

```
+------------------------------------------------------------------+
|  [Request Rate]      [Error Rate %]     [P95 Latency]    [Active]|
|     12.5 /s             0.2%              145ms            3     |
|  (stat panel)       (stat panel)      (stat panel)   (stat panel)|
+------------------------------------------------------------------+
|                        Request Rate                               |
|  +---------------------------------------------------------+     |
|  |   [Time series: rate(http_requests_total[5m])]          |     |
|  |   Legend: GET /api/v1/todos, POST /api/v1/todos, etc.   |     |
|  +---------------------------------------------------------+     |
|                                                                   |
|  Request Duration              |  Error Rate                     |
|  +---------------------------+ | +---------------------------+   |
|  | [Time series: p95, p99]   | | [Time series: 4xx, 5xx]    |   |
|  +---------------------------+ | +---------------------------+   |
+------------------------------------------------------------------+
|                        Recent Logs                                |
|  +---------------------------------------------------------+     |
|  | [Logs panel: {service="backend"} | line_format]         |     |
|  | 2024-12-03 10:30:45 INFO Todo created trace_id=abc...   |     |
|  | 2024-12-03 10:30:44 INFO GET /api/v1/todos 200 45ms     |     |
|  +---------------------------------------------------------+     |
+------------------------------------------------------------------+
```

**Panel Specifications:**

| Panel | Type | Query | Legend Format |
|-------|------|-------|---------------|
| Request Rate (stat) | `stat` | `sum(rate(http_requests_total[5m]))` | - |
| Error Rate % (stat) | `stat` | `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100` | - |
| P95 Latency (stat) | `stat` | `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))` | - |
| Active Requests (stat) | `stat` | `sum(active_requests)` | - |
| Request Rate (graph) | `timeseries` | `rate(http_requests_total[5m])` | `{{method}} {{endpoint}}` |
| Request Duration (graph) | `timeseries` | `histogram_quantile(0.95, ...)` and `histogram_quantile(0.99, ...)` | `p95`, `p99` |
| Error Rate (graph) | `timeseries` | `rate(http_requests_total{status=~"4.."}[5m])` and `rate(http_requests_total{status=~"5.."}[5m])` | `4xx`, `5xx` |
| Recent Logs | `logs` | `{service="backend"}` | - |

#### UX-006: SLO Overview Dashboard Layout

The SLO Overview Dashboard shall enable SRE-focused monitoring with configurable targets:

```
+------------------------------------------------------------------+
|  Template Variables:                                              |
|  [Availability Target: 99.5%]  [Latency Target: 500ms]           |
+------------------------------------------------------------------+
|  [Availability]     [Latency SLO]     [Error Budget]  [Burn Rate]|
|     99.87%           98.2%              72%              1.2x    |
|  (green stat)      (green stat)     (yellow stat)   (stat panel) |
+------------------------------------------------------------------+
|  Availability Over Time           |  Latency Distribution         |
|  +---------------------------+    | +---------------------------+ |
|  | [Time series: SLI]        |    | [Histogram: request duration]||
|  | Target line at 99.5%      |    |                             | |
|  +---------------------------+    | +---------------------------+ |
|                                                                   |
|  Error Budget Consumption        |  Endpoints Below SLO          |
|  +---------------------------+   | +---------------------------+ |
|  | [Time series: budget used]|   | [Table: slow/error endpoints]||
|  | Threshold at 100%         |   | endpoint | p95 | error_rate | |
|  +---------------------------+   | +---------------------------+ |
+------------------------------------------------------------------+
```

**Template Variables:**

| Variable | Label | Type | Default | Options |
|----------|-------|------|---------|---------|
| `$availability_target` | Availability Target | Custom | `0.995` | `0.99`, `0.995`, `0.999`, `0.9999` |
| `$latency_target` | Latency Target (ms) | Custom | `500` | `100`, `250`, `500`, `1000`, `2000` |
| `$time_window` | SLO Window | Custom | `30d` | `1d`, `7d`, `30d`, `90d` |

#### UX-007: Log Explorer Dashboard Layout

The Log Explorer Dashboard shall provide efficient log navigation and filtering:

```
+------------------------------------------------------------------+
|  Template Variables:                                              |
|  [Service: All v]  [Level: All v]  [Container: All v]  [Search:__]|
+------------------------------------------------------------------+
|  Log Volume by Service                                            |
|  +---------------------------------------------------------+     |
|  | [Time series: count_over_time grouped by service]       |     |
|  | Legend: backend, keycloak, postgres                     |     |
|  +---------------------------------------------------------+     |
+------------------------------------------------------------------+
|  Error Logs (last hour)          |  All Logs (live tail)         |
|  +---------------------------+   | +---------------------------+ |
|  | [Logs: level=~"ERROR|WARN"]   | [Logs: {service=~"$service"}| |
|  | 2024-12-03 10:30:45 ERROR  |   | 2024-12-03 10:30:46 INFO   | |
|  | Connection refused...      |   | Request received...        | |
|  +---------------------------+   | +---------------------------+ |
+------------------------------------------------------------------+
```

**Log Panel Configuration:**

| Panel | Query | Options |
|-------|-------|---------|
| Error Logs | `{service=~"$service"} \|= "ERROR" or \|= "WARN"` | `showTime: true`, `wrapLogMessage: true`, `sortOrder: Descending` |
| All Logs | `{service=~"$service", container=~"$container"}` | `showTime: true`, `enableLogDetails: true`, `dedupStrategy: none` |
| Log Volume | `sum(count_over_time({service=~".+"}[1m])) by (service)` | - |

#### UX-008: Trace Explorer Dashboard Layout

The Trace Explorer Dashboard shall enable efficient trace discovery and analysis:

```
+------------------------------------------------------------------+
|  Template Variables:                                              |
|  [Service: backend v]  [Min Duration: 0ms]  [Status: All v]       |
+------------------------------------------------------------------+
|  Trace Duration Distribution     |  Traces Per Minute            |
|  +---------------------------+   | +---------------------------+ |
|  | [Histogram: span duration]|   | [Time series: trace count] | |
|  +---------------------------+   | +---------------------------+ |
+------------------------------------------------------------------+
|  Service Map (Node Graph)                                         |
|  +---------------------------------------------------------+     |
|  | [Node graph: service dependencies]                      |     |
|  | backend --> postgres, backend --> redis                 |     |
|  +---------------------------------------------------------+     |
+------------------------------------------------------------------+
|  Recent Traces                                                    |
|  +---------------------------------------------------------+     |
|  | [Table: trace_id | service | duration | status | time]  |     |
|  | abc123... | backend | 245ms | OK | 10:30:45             |     |
|  | def456... | backend | 1.2s  | ERROR | 10:30:40          |     |
|  +---------------------------------------------------------+     |
+------------------------------------------------------------------+
```

**TraceQL Queries:**

| Panel | Query | Purpose |
|-------|-------|---------|
| Duration Distribution | `{ resource.service.name = "$service" }` | Histogram of span durations |
| Recent Traces | `{ resource.service.name = "$service" && duration > ${min_duration}ms }` | Filterable trace list |
| Service Map | Enabled via Tempo datasource `nodeGraph.enabled: true` | Visual service topology |

---

### Navigation and Information Architecture

#### UX-009: Dashboard Home Screen

Grafana shall be configured with a logical home screen experience:

| Element | Configuration | Purpose |
|---------|---------------|---------|
| Home dashboard | Backend Service Dashboard | Most common starting point for developers |
| Starred dashboards | Pre-starred: Backend, SLO, Logs | Quick access to key dashboards |
| Dashboard folders | Observability | Organized grouping of all observability dashboards |

**Dashboard Discovery:**
- All observability dashboards shall be placed in an "Observability" folder
- Dashboard tags enable filtering (e.g., show only `debugging` dashboards)
- Search supports dashboard name and tag matching

#### UX-010: Cross-Dashboard Navigation

Dashboards shall implement drill-down and cross-reference patterns:

| From Dashboard | To Dashboard | Trigger | Context Passed |
|----------------|--------------|---------|----------------|
| Backend Service | Log Explorer | Click on error stat | Pre-filtered to ERROR level |
| Backend Service | Trace Explorer | Click on latency outlier | Pre-filtered to slow traces |
| SLO Overview | Backend Service | Click on endpoint row | Time range preserved |
| Log Explorer | Trace Explorer | Click on trace_id in log | trace_id passed for lookup |
| Trace Explorer | Log Explorer | Trace-to-logs correlation | trace_id and time range |

**Implementation**: Use Grafana's [data links](https://grafana.com/docs/grafana/latest/administration/correlations/) feature to create contextual navigation.

---

### Data Correlation UX

#### UX-011: Trace-to-Logs Correlation

The Tempo datasource shall be configured with [traces-to-logs correlation](https://grafana.com/docs/grafana/latest/datasources/tempo/traces-in-grafana/trace-correlations/):

**User Experience:**
1. User views a trace in Grafana (Explore or Trace panel)
2. Each span displays a "Logs" button/link
3. Clicking "Logs" opens Loki query pre-filtered by:
   - `trace_id` matching the current trace
   - Time range: span start - 1 hour to span end + 1 hour

**Configuration Requirements:**
```yaml
# Tempo datasource configuration
tracesToLogsV2:
  datasourceUid: 'loki'
  spanStartTimeShift: '-1h'
  spanEndTimeShift: '1h'
  filterByTraceID: true
  customQuery: true
  query: '{service="backend"} | trace_id=`${__trace.traceId}`'
```

**Visual Indicator**: Logs button appears on each span when correlation is configured.

#### UX-012: Trace-to-Metrics Correlation

The Tempo datasource shall be configured with [traces-to-metrics correlation](https://grafana.com/blog/2022/08/18/new-in-grafana-9.1-trace-to-metrics-allows-users-to-navigate-from-a-trace-span-to-a-selected-data-source/):

**User Experience:**
1. User views a trace span with endpoint information
2. Span displays a "Metrics" button/link
3. Clicking "Metrics" opens Prometheus query showing:
   - Request rate for that endpoint
   - Latency percentiles for that endpoint
   - Time range centered on span timestamp

**Configuration Requirements:**
```yaml
# Tempo datasource configuration
tracesToMetrics:
  datasourceUid: 'prometheus'
  spanStartTimeShift: '-5m'
  spanEndTimeShift: '5m'
  queries:
    - name: 'Request Rate'
      query: 'rate(http_requests_total{endpoint="${__span.tags.url.path}"}[5m])'
    - name: 'P95 Latency'
      query: 'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{endpoint="${__span.tags.url.path}"}[5m]))'
```

#### UX-013: Logs-to-Traces Correlation

Logs containing trace_id shall provide clickable links to traces:

**User Experience:**
1. User views logs in Log Explorer or Explore
2. Logs containing `trace_id=...` display a trace link icon
3. Clicking the icon opens the full trace in Tempo

**Implementation Approaches:**
1. **Derived Fields**: Configure Loki datasource to recognize `trace_id` pattern
2. **Data Links**: Create data link from log panel to Tempo query

**Derived Field Configuration:**
```yaml
# Loki datasource configuration
derivedFields:
  - name: 'trace_id'
    matcherRegex: 'trace_id=([a-f0-9]+)'
    url: '/explore?left={"datasource":"tempo","queries":[{"refId":"A","queryType":"traceId","query":"${__value.raw}"}]}'
    datasourceUid: 'tempo'
```

---

### Developer Experience Considerations

#### UX-014: Zero-Configuration Access

The observability stack shall provide immediate value without configuration:

| Aspect | Requirement | Implementation |
|--------|-------------|----------------|
| Authentication | No login required in development | `GF_AUTH_ANONYMOUS_ENABLED=true` |
| Default role | Full access to all features | `GF_AUTH_ANONYMOUS_ORG_ROLE=Admin` |
| Home page | Useful dashboard immediately visible | Backend Service Dashboard as home |
| Datasources | Pre-connected, no manual setup | Provisioned via YAML |
| Dashboards | Pre-built, immediately useful | Provisioned via JSON |

#### UX-015: Dashboard Load Time

Dashboards shall provide responsive performance:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Initial dashboard load | < 3 seconds | Time from navigation to all panels rendered |
| Panel refresh | < 1 second | Time for individual panel to update |
| Search response | < 500ms | Time for Loki/Tempo query results |

**Performance Optimization Strategies:**
1. Use appropriate time ranges (1 hour default, not 30 days)
2. Limit log panel results (100-500 lines max)
3. Use recording rules for expensive aggregations (future enhancement)
4. Avoid high-cardinality label queries in real-time dashboards

#### UX-016: Error States and Feedback

Dashboards shall provide clear feedback for error conditions:

| Condition | Visual Feedback | User Action |
|-----------|-----------------|-------------|
| Datasource unavailable | "No data" with error message | Check Docker Compose status |
| Query timeout | "Query timed out" with retry button | Reduce time range, simplify query |
| No data in time range | "No data" (not error) | Expand time range |
| Backend not running | Empty metrics, logs | Start backend service |

**Error Message Standards:**
- Use plain language, not technical jargon
- Suggest corrective actions when possible
- Distinguish between "no data" and "error fetching data"

#### UX-017: Onboarding Experience

New users shall be guided to observability features:

**README Documentation Section:**
```markdown
## Observability

This project includes a pre-configured observability stack:

- **Grafana** (http://localhost:3000) - Dashboards and visualization
- **Prometheus** (http://localhost:9090) - Metrics collection
- **Loki** (via Grafana) - Log aggregation
- **Tempo** (via Grafana) - Distributed tracing

### Quick Start

1. Start the application: `docker compose up`
2. Open Grafana: http://localhost:3000
3. View the "Backend Service Dashboard" to see live metrics
4. Use "Explore" to search logs and traces

### Available Dashboards

| Dashboard | Purpose |
|-----------|---------|
| Backend Service Dashboard | Request rate, latency, errors, logs |
| SLO Overview Dashboard | Availability, latency SLOs, error budget |
| Log Explorer Dashboard | Search and filter logs across services |
| Trace Explorer Dashboard | Search and visualize distributed traces |
```

---

### Accessibility Considerations

#### UX-018: Color Accessibility

Dashboards shall consider color accessibility:

| Requirement | Implementation |
|-------------|----------------|
| Color-blind safe | Do not rely solely on red/green distinction; use patterns or icons |
| Sufficient contrast | Text contrast ratio > 4.5:1 against backgrounds |
| Theme support | Dashboards work in both light and dark Grafana themes |

**Color-Blind Friendly Alternatives:**
- Use shapes in addition to colors (e.g., circle for OK, triangle for warning)
- Use Grafana's built-in "Color blind safe" color palette option
- Include text labels on stat panels, not just colors

#### UX-019: Keyboard Navigation

Grafana dashboards shall support keyboard navigation:

| Action | Shortcut |
|--------|----------|
| Toggle fullscreen panel | `v` |
| Refresh dashboard | `r` |
| Open time range picker | `t` |
| Go to Explore | `x` |
| Search dashboards | `/` or `Ctrl+K` |

**Note**: Keyboard shortcuts are Grafana built-in features, no custom implementation required.

---

### Mobile and Responsive Considerations

#### UX-020: Responsive Dashboard Layout

While observability dashboards are primarily desktop-focused, basic mobile viewing shall be supported:

| Screen Width | Layout Adjustment |
|--------------|-------------------|
| > 1200px | Full 24-column layout as designed |
| 768px - 1200px | Panels stack vertically, maintain 12-column width |
| < 768px | Single-column layout, panels at full width |

**Grafana's Responsive Behavior:**
- Grafana automatically adjusts panel layout based on viewport
- No custom responsive CSS required
- Complex visualizations (node graphs) may be suboptimal on mobile

**Recommendation**: Document that observability dashboards are optimized for desktop use. Mobile access is for quick status checks only.

---

### Documentation and Help

#### UX-021: In-Dashboard Documentation

Dashboards shall include contextual help:

| Element | Implementation |
|---------|----------------|
| Dashboard description | Markdown text explaining dashboard purpose |
| Panel descriptions | Tooltip help on each panel header |
| Query explanations | Comments in saved queries |
| Variable help text | Description for each template variable |

**Dashboard Description Template:**
```markdown
## Backend Service Dashboard

This dashboard provides real-time visibility into the backend API performance using the RED method:
- **Rate**: Request throughput by endpoint
- **Errors**: 4xx and 5xx error rates
- **Duration**: Request latency percentiles (p95, p99)

### Usage
- Use the time picker (top right) to adjust the time range
- Click on any panel title for options like "Explore" to dive deeper
- Stat panels show current values; graphs show historical trends

### Metrics Source
All metrics are collected via Prometheus scraping the `/metrics` endpoint on the backend service.
```

#### UX-022: Observability Documentation Structure

The generated project shall include observability documentation:

| Document | Location | Content |
|----------|----------|---------|
| Observability section | `README.md` | Quick start, dashboard overview, service URLs |
| Architecture diagram | `docs/observability.md` (optional) | Data flow, component relationships |
| Custom metrics guide | `backend/app/observability.py` | Inline code comments with examples |

---

### Summary: UX Requirements Traceability

| Requirement | Priority | Related User Stories | Related Goals |
|-------------|----------|---------------------|---------------|
| UX-001: Dashboard Naming Convention | Must Have | US-001, US-005 | G5 |
| UX-002: Dashboard Layout Grid | Must Have | US-001 | G5 |
| UX-003: Visual Hierarchy | Must Have | US-001, US-004 | G3, G5 |
| UX-004: Dashboard Time Controls | Must Have | US-001 | G5 |
| UX-005: Backend Service Dashboard Layout | Must Have | US-001, US-012 | G2, G5 |
| UX-006: SLO Overview Dashboard Layout | Should Have | US-004 | G2 |
| UX-007: Log Explorer Dashboard Layout | Should Have | US-003, US-007 | G3, G5 |
| UX-008: Trace Explorer Dashboard Layout | Should Have | US-002, US-009 | G3, G5 |
| UX-009: Dashboard Home Screen | Must Have | US-005 | G5 |
| UX-010: Cross-Dashboard Navigation | Should Have | US-003 | G3 |
| UX-011: Trace-to-Logs Correlation | Must Have | US-003 | G3 |
| UX-012: Trace-to-Metrics Correlation | Should Have | US-002 | G3 |
| UX-013: Logs-to-Traces Correlation | Must Have | US-003 | G3 |
| UX-014: Zero-Configuration Access | Must Have | US-005 | G4, G5 |
| UX-015: Dashboard Load Time | Should Have | - | G5 |
| UX-016: Error States and Feedback | Should Have | EC-001, EC-005 | G5 |
| UX-017: Onboarding Experience | Must Have | US-005 | G5 |
| UX-018: Color Accessibility | Should Have | - | G5 |
| UX-019: Keyboard Navigation | Could Have | - | G5 |
| UX-020: Responsive Dashboard Layout | Could Have | - | G5 |
| UX-021: In-Dashboard Documentation | Should Have | US-005 | G5 |
| UX-022: Observability Documentation Structure | Must Have | US-005 | G5 |

**Priority Summary:**
- Must Have: 10 requirements
- Should Have: 10 requirements
- Could Have: 2 requirements

---

## Security & Privacy Considerations

This section defines the security and privacy requirements for the observability stack integration. Observability systems inherently collect, transport, and store data that may contain sensitive information. The design must balance developer convenience in development environments with robust security controls for production deployments.

### Security Design Principles

The security architecture follows these core principles:

1. **Defense in Depth**: Multiple layers of security controls (network isolation, authentication, authorization, encryption)
2. **Least Privilege**: Components operate with minimal required permissions
3. **Fail-Open for Observability**: Application functionality is not impacted by observability failures (graceful degradation)
4. **Secure by Default for Production**: Documentation and configuration templates encourage secure defaults
5. **Transparency**: Clear documentation of security posture and risks

### Threat Model

#### Assets to Protect

| Asset | Sensitivity | Threat Impact |
|-------|-------------|---------------|
| Application metrics | Medium | Performance/capacity information disclosure |
| Application logs | High | May contain user actions, errors with context, trace IDs |
| Distributed traces | High | Request paths, timing data, span attributes |
| Grafana configuration | Medium | Dashboard definitions, datasource URLs |
| Grafana credentials | High | Access to all observability data |
| Prometheus TSDB | Medium | Historical metrics data |
| Loki chunks | High | Historical log data |
| Tempo blocks | High | Historical trace data |

#### Threat Actors

| Actor | Capability | Motivation |
|-------|------------|------------|
| External attacker | Network access to exposed ports | Data exfiltration, reconnaissance |
| Malicious insider | Internal network access | Data theft, sabotage |
| Compromised service | Network access, may have credentials | Lateral movement, data collection |
| Automated scanner | Port scanning, vulnerability probing | Initial reconnaissance |

#### Attack Vectors

| Vector | Risk Level (Dev) | Risk Level (Prod) | Mitigation |
|--------|------------------|-------------------|------------|
| Unauthenticated Grafana access | Accepted | High | Enable authentication in production |
| Exposed /metrics endpoint | Low | Medium | Network isolation, authentication proxy |
| Unencrypted trace transport (OTLP) | Low | High | Enable TLS for production |
| Log injection attacks | Medium | Medium | Input validation, structured logging |
| Information disclosure in logs | High | High | PII filtering, log sanitization |
| Docker socket access (Promtail) | Medium | High | Read-only mount, rootless containers |
| Prometheus scrape endpoints | Low | Medium | Network policies, authentication |

---

### Development Environment Security Profile

The default configuration prioritizes developer convenience. This is explicitly documented as development-only:

#### SEC-DEV-001: Anonymous Grafana Access

**Default Setting**: Enabled
**Configuration**:
```yaml
environment:
  - GF_AUTH_ANONYMOUS_ENABLED=true
  - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
  - GF_AUTH_DISABLE_LOGIN_FORM=true
```

**Security Implication**: Any user with network access can view all dashboards, metrics, logs, and traces.

**Mitigation**: This configuration is only for development. Production documentation explicitly requires authentication.

#### SEC-DEV-002: Unauthenticated Metrics Endpoint

**Default Setting**: Enabled
**Configuration**: The `/metrics` endpoint on the backend is publicly accessible without authentication.

**Security Implication**: Anyone with network access can enumerate metrics names, labels, and values.

**Mitigation**: In development, the backend is bound to localhost. Production guidance recommends network isolation or authentication proxy.

#### SEC-DEV-003: Unencrypted OTLP Transport

**Default Setting**: No TLS
**Configuration**:
```python
# Backend observability.py
trace_exporter = OTLPSpanExporter(
    endpoint="http://tempo:4317",  # Unencrypted gRPC
    insecure=True
)
```

**Security Implication**: Trace data transmitted in cleartext on Docker network.

**Mitigation**: Docker internal network provides isolation. Production guidance recommends TLS configuration.

#### SEC-DEV-004: Loki Authentication Disabled

**Default Setting**: `auth_enabled: false`
**Configuration**: From `loki-config.yml`:
```yaml
auth_enabled: false
```

**Security Implication**: No tenant isolation or access control for log data.

**Mitigation**: Single-tenant development use case. Production guidance covers multi-tenant configuration.

---

### Production Security Requirements

The following security requirements apply to production deployments. These are documented as guidance and configuration examples, not enforced by the template (per scope boundaries).

#### SEC-001: Grafana Authentication (Must Have)

**Requirement**: Production deployments MUST disable anonymous access and enable authentication.

**Acceptance Criteria**:
1. Documentation includes production authentication configuration examples
2. Environment variable overrides for authentication settings are documented
3. SSO/OAuth integration patterns are referenced

**Configuration Example** (documented in README):
```yaml
# Production Grafana environment variables
environment:
  - GF_AUTH_ANONYMOUS_ENABLED=false
  - GF_AUTH_DISABLE_LOGIN_FORM=false
  # For OIDC/OAuth (e.g., Keycloak)
  - GF_AUTH_GENERIC_OAUTH_ENABLED=true
  - GF_AUTH_GENERIC_OAUTH_CLIENT_ID=${GRAFANA_OAUTH_CLIENT_ID}
  - GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET=${GRAFANA_OAUTH_CLIENT_SECRET}
  - GF_AUTH_GENERIC_OAUTH_SCOPES=openid profile email
  - GF_AUTH_GENERIC_OAUTH_AUTH_URL=${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/auth
  - GF_AUTH_GENERIC_OAUTH_TOKEN_URL=${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/token
  - GF_AUTH_GENERIC_OAUTH_API_URL=${KEYCLOAK_URL}/realms/${REALM}/protocol/openid-connect/userinfo
```

**Reference**: [Grafana Authentication Best Practices](https://grafana.com/blog/2022/02/22/how-secure-is-your-grafana-instance-what-you-need-to-know/)

#### SEC-002: Metrics Endpoint Protection (Should Have)

**Requirement**: Production deployments SHOULD protect the `/metrics` endpoint from unauthorized access.

**Acceptance Criteria**:
1. Documentation describes metrics endpoint security options
2. Network isolation recommendations are provided
3. Authentication proxy pattern is documented

**Implementation Options** (documented):

Option A - Network Isolation:
```yaml
# Prometheus scrapes only internal Docker network
# /metrics endpoint not exposed to host
backend:
  expose: []  # No host port binding
  # Only accessible via Docker network
```

Option B - Basic Authentication:
```python
# backend/app/observability.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_metrics_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    expected_username = os.getenv("METRICS_USERNAME", "prometheus")
    expected_password = os.getenv("METRICS_PASSWORD")
    if not expected_password:
        return  # No password set, allow access
    if not (secrets.compare_digest(credentials.username, expected_username) and
            secrets.compare_digest(credentials.password, expected_password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/metrics", dependencies=[Depends(verify_metrics_credentials)])
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

**Reference**: [Prometheus Security Model](https://prometheus.io/docs/operating/security/)

#### SEC-003: TLS for Trace Transport (Should Have)

**Requirement**: Production deployments SHOULD enable TLS for OTLP trace export.

**Acceptance Criteria**:
1. Documentation includes TLS configuration for Tempo
2. Certificate management guidance is provided
3. Environment variable for enabling TLS is documented

**Configuration Example** (documented):
```python
# Production trace exporter with TLS
import os
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

trace_exporter = OTLPSpanExporter(
    endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "tempo:4317"),
    insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true").lower() == "true",
    # When insecure=False, uses system CA certificates or:
    # credentials=ssl_channel_credentials(root_certificates=cert_data)
)
```

**Tempo TLS Configuration** (documented):
```yaml
# tempo.yml for production
distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
          tls:
            cert_file: /etc/tempo/server.crt
            key_file: /etc/tempo/server.key
```

#### SEC-004: Network Segmentation (Should Have)

**Requirement**: Production deployments SHOULD isolate observability services on a dedicated network.

**Acceptance Criteria**:
1. Documentation describes network segmentation patterns
2. Docker Compose network configuration examples are provided
3. Firewall rule recommendations are documented

**Configuration Example** (documented):
```yaml
# Production compose.yml network configuration
networks:
  frontend:
    # Public-facing services
  backend:
    # Application services
  observability:
    internal: true  # Not accessible from host
    # Only Grafana exposed to frontend network

services:
  grafana:
    networks:
      - frontend      # Accessible for users
      - observability # Access to backends
  prometheus:
    networks:
      - observability
      - backend       # Scrape application metrics
  loki:
    networks:
      - observability
  tempo:
    networks:
      - observability
      - backend       # Receive traces from application
```

#### SEC-005: Secret Management (Must Have)

**Requirement**: Sensitive configuration values MUST be managed via environment variables, not hardcoded.

**Acceptance Criteria**:
1. All passwords and tokens use environment variable substitution
2. `.env.example` file documents required secrets
3. No default passwords in production configurations
4. Documentation references external secret management solutions

**Sensitive Values Identified**:

| Value | Environment Variable | Default (Dev Only) |
|-------|---------------------|-------------------|
| Grafana admin password | `GF_SECURITY_ADMIN_PASSWORD` | Not set (anonymous) |
| Grafana OAuth client secret | `GRAFANA_OAUTH_CLIENT_SECRET` | Not set |
| Metrics endpoint password | `METRICS_PASSWORD` | Not set |
| Loki authentication | Loki-specific config | Disabled |

**Documentation Content**:
```markdown
## Production Secrets

For production deployments, configure secrets via environment variables:

```bash
# Required for production
export GF_SECURITY_ADMIN_PASSWORD=$(openssl rand -base64 32)
export GRAFANA_OAUTH_CLIENT_SECRET="<from-keycloak>"

# Optional: Metrics endpoint authentication
export METRICS_USERNAME="prometheus"
export METRICS_PASSWORD=$(openssl rand -base64 32)
```

Consider using a secrets manager (HashiCorp Vault, AWS Secrets Manager, Kubernetes Secrets) for production deployments.
```

---

### Privacy Requirements

The observability stack collects data that may contain personally identifiable information (PII) or sensitive business data. These requirements ensure appropriate handling.

#### SEC-006: PII in Logs (Must Have)

**Requirement**: Documentation MUST warn about PII in logs and provide mitigation guidance.

**Acceptance Criteria**:
1. README includes warning about sensitive data in logs
2. Code comments in `observability.py` document PII risks
3. Log sanitization patterns are documented

**PII Risk Categories**:

| Category | Example | Risk Level | Mitigation |
|----------|---------|------------|------------|
| User identifiers | `user_id=123` | Medium | Acceptable if not correlated to PII |
| Email addresses | `email=user@example.com` | High | Do not log in plain text |
| IP addresses | `client_ip=192.168.1.1` | Medium | Consider hashing or truncation |
| Request bodies | `{"password": "..."}` | Critical | Never log request bodies with credentials |
| Error messages | `User john.doe@... not found` | High | Sanitize error messages |
| Query parameters | `?token=abc123` | High | Filter sensitive query params |

**Implementation Guidance** (documented in observability.py comments):
```python
# WARNING: Logs may contain sensitive information
#
# DO NOT LOG:
# - Passwords, API keys, tokens
# - Full email addresses (use hashed or truncated)
# - Credit card numbers or financial data
# - Health information (HIPAA)
# - Government identifiers (SSN, passport numbers)
#
# CONSIDER SANITIZING:
# - IP addresses (hash or truncate last octet)
# - User-provided content (may contain PII)
# - Error messages (may echo user input)
#
# For GDPR compliance, implement:
# 1. Data retention policies (see Loki/Prometheus retention)
# 2. Right to erasure (consider log anonymization)
# 3. Access controls (who can query logs)
```

**Reference**: [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

#### SEC-007: PII in Traces (Should Have)

**Requirement**: Documentation SHOULD describe PII risks in trace attributes and mitigation.

**Acceptance Criteria**:
1. Trace attribute guidelines are documented
2. Sensitive attribute filtering is described

**Trace Attribute PII Risks**:

| Attribute | OpenTelemetry Semantic Convention | PII Risk | Recommendation |
|-----------|----------------------------------|----------|----------------|
| `http.url` | Standard | Medium | May contain query params with tokens |
| `http.target` | Standard | Medium | May contain query params |
| `db.statement` | Standard | High | May contain user data in queries |
| `http.request.body` | Custom | Critical | Never record full bodies |
| `user.id` | Standard | Low | Acceptable if pseudonymous |
| `user.email` | Custom | High | Avoid in traces |

**Mitigation Code Example** (documented):
```python
# Sanitize URL query parameters in traces
from urllib.parse import urlparse, parse_qs, urlencode

SENSITIVE_PARAMS = {'token', 'api_key', 'password', 'secret', 'auth'}

def sanitize_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.query:
        params = parse_qs(parsed.query)
        sanitized = {k: ['[REDACTED]' if k.lower() in SENSITIVE_PARAMS else v[0]]
                     for k, v in params.items()}
        return parsed._replace(query=urlencode(sanitized, doseq=True)).geturl()
    return url
```

#### SEC-008: Data Retention and Right to Erasure (Should Have)

**Requirement**: Documentation SHOULD address data retention policies and GDPR considerations.

**Acceptance Criteria**:
1. Default retention periods are documented
2. GDPR right to erasure implications are described
3. Retention configuration is adjustable

**Default Retention Periods**:

| Component | Default Retention | Configuration |
|-----------|-------------------|---------------|
| Prometheus | 15 days | `--storage.tsdb.retention.time=15d` |
| Loki | 7 days | `retention_period: 168h` |
| Tempo | 1 hour (dev) | `block_retention: 1h` |

**GDPR Considerations** (documented):
```markdown
## GDPR and Data Retention

The observability stack stores data that may be subject to GDPR:

### Right to Erasure (Article 17)
If logs or traces contain PII, you may need to:
1. **Prevent PII collection**: Best approach - don't log PII
2. **Implement anonymization**: Hash or pseudonymize identifiers
3. **Time-based deletion**: Configure retention periods

### Data Subject Access Requests (Article 15)
Logs and traces containing a user's data may need to be:
1. Searchable by user identifier
2. Exportable in a readable format
3. Deletable upon request

### Recommended Approach
1. Avoid logging direct PII (emails, names)
2. Use pseudonymous identifiers (user_id)
3. Set retention periods aligned with business needs
4. Document data flows for compliance audits
```

**Reference**: [OWASP Data Security Top 10](https://owasp.org/www-project-data-security-top-10/)

---

### Log Injection Prevention

#### SEC-009: Structured Logging (Must Have)

**Requirement**: Logging MUST use structured format to prevent log injection attacks.

**Acceptance Criteria**:
1. Structured JSON logging is the default format
2. User input is never directly interpolated into log messages
3. Log injection risks are documented

**Log Injection Vulnerability** (CWE-117):
```python
# VULNERABLE: User input directly in log message
logger.info(f"User login: {username}")  # username could contain newlines/control chars

# SAFE: Structured logging with separate fields
logger.info("User login", extra={"username": username})
```

**Implementation in observability.py**:
```python
import logging
import json

class StructuredLogFormatter(logging.Formatter):
    """JSON formatter that safely handles user input."""

    def format(self, record):
        log_data = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, 'trace_id', None),
            "span_id": getattr(record, 'span_id', None),
        }
        # Extra fields are JSON-encoded, preventing injection
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        return json.dumps(log_data)
```

**Reference**: [OWASP A09:2021 Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)

---

### Access Control Requirements

#### SEC-010: Grafana Role-Based Access (Could Have)

**Requirement**: Documentation COULD describe Grafana RBAC configuration for team environments.

**Acceptance Criteria**:
1. Basic RBAC concepts are documented
2. Organization and team configuration is described
3. Dashboard permissions are explained

**RBAC Model** (documented for production):

| Role | Capabilities | Use Case |
|------|--------------|----------|
| Viewer | View dashboards, explore data | Development team members |
| Editor | Create/edit dashboards, alerts | Senior developers, SREs |
| Admin | Full configuration access | Platform team |

**Configuration Example**:
```yaml
# Grafana environment for RBAC
environment:
  - GF_USERS_DEFAULT_THEME=dark
  - GF_USERS_VIEWERS_CAN_EDIT=false
  - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/etc/grafana/provisioning/dashboards/backend-dashboard.json
```

#### SEC-011: Audit Logging (Could Have)

**Requirement**: Documentation COULD describe audit logging capabilities for compliance.

**Acceptance Criteria**:
1. Grafana audit logging configuration is documented
2. Access logging patterns are described

**Audit Events to Capture** (for compliance environments):

| Event | Importance | Grafana Feature |
|-------|------------|-----------------|
| Dashboard access | High | Enterprise audit logs |
| Data source queries | High | Enterprise audit logs |
| Configuration changes | Critical | Enterprise audit logs |
| User authentication | High | Standard logs |

**Note**: Full audit logging requires Grafana Enterprise. Open source version has limited audit capabilities.

---

### Docker Security Considerations

#### SEC-012: Promtail Docker Socket Access (Should Have)

**Requirement**: Documentation SHOULD describe security implications of Docker socket access.

**Acceptance Criteria**:
1. Docker socket risk is documented
2. Read-only mount is enforced
3. Rootless container options are described

**Risk Description**:
Promtail requires access to the Docker socket (`/var/run/docker.sock`) to discover and collect container logs. This provides read access to Docker state, which could expose:
- Container names and IDs
- Environment variables (if not filtered)
- Container labels
- Log content from all containers

**Mitigation Applied**:
```yaml
# Read-only Docker socket mount
promtail:
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro  # Read-only
    - /var/lib/docker/containers:/var/lib/docker/containers:ro  # Read-only
```

**Additional Production Recommendations** (documented):
1. Use Docker socket proxy (e.g., Tecnativa/docker-socket-proxy) to limit API access
2. Consider log drivers that push to Loki directly (loki-docker-driver)
3. Run Promtail as non-root user where possible

#### SEC-013: Container Image Security (Should Have)

**Requirement**: Documentation SHOULD recommend image versioning and vulnerability scanning.

**Acceptance Criteria**:
1. Image pinning recommendations are documented
2. Vulnerability scanning guidance is provided

**Current Configuration** (development):
```yaml
prometheus:
  image: prom/prometheus:latest  # Unpinned for development
```

**Production Recommendation** (documented):
```yaml
# Pin to specific versions for reproducibility and security
prometheus:
  image: prom/prometheus:v2.48.0  # Pin to tested version
grafana:
  image: grafana/grafana:10.2.2
loki:
  image: grafana/loki:2.9.2
tempo:
  image: grafana/tempo:2.3.1
promtail:
  image: grafana/promtail:2.9.2
```

**Vulnerability Scanning**:
```markdown
## Container Security

For production deployments:

1. **Pin image versions** to specific tags, not `latest`
2. **Scan images** with tools like Trivy, Snyk, or Grype:
   ```bash
   trivy image grafana/grafana:10.2.2
   ```
3. **Update regularly** to patch security vulnerabilities
4. **Use official images** from verified publishers
```

---

### Security Testing Requirements

#### SEC-014: Security Documentation Verification (Must Have)

**Requirement**: Security documentation MUST be included and verified in generated projects.

**Acceptance Criteria**:
1. Security section exists in generated README
2. Production security checklist is included
3. Test validates documentation exists

**Security Documentation Template**:
```markdown
## Security Considerations

### Development Mode Warning

The default observability configuration is optimized for development:
- Grafana anonymous access is ENABLED
- Metrics endpoints are UNAUTHENTICATED
- Trace transport is UNENCRYPTED

**DO NOT deploy to production without reviewing the security configuration.**

### Production Security Checklist

- [ ] Disable Grafana anonymous access (`GF_AUTH_ANONYMOUS_ENABLED=false`)
- [ ] Configure Grafana authentication (OIDC, LDAP, or built-in)
- [ ] Enable TLS for OTLP trace export
- [ ] Isolate observability services on internal network
- [ ] Configure firewall rules for metrics endpoints
- [ ] Set appropriate data retention periods
- [ ] Review logs for PII before enabling log aggregation
- [ ] Pin container image versions
- [ ] Implement secret management for credentials
```

#### SEC-015: Security Configuration Tests (Should Have)

**Requirement**: Automated tests SHOULD verify security-related configuration.

**Acceptance Criteria**:
1. Test verifies Grafana anonymous access is disabled in production config
2. Test verifies no hardcoded passwords exist
3. Test verifies Docker socket is mounted read-only

**Test Examples**:
```python
# test_observability_security.py

def test_no_hardcoded_passwords():
    """Verify no passwords are hardcoded in configuration files."""
    config_files = [
        'observability/prometheus/prometheus.yml',
        'observability/grafana/datasources/datasources.yml',
    ]
    for config_file in config_files:
        content = Path(config_file).read_text()
        assert 'password:' not in content.lower() or 'password: ${' in content.lower()

def test_docker_socket_readonly():
    """Verify Docker socket is mounted read-only."""
    compose = yaml.safe_load(Path('compose.yml').read_text())
    promtail_volumes = compose['services']['promtail']['volumes']
    docker_sock_mount = [v for v in promtail_volumes if 'docker.sock' in v][0]
    assert ':ro' in docker_sock_mount or docker_sock_mount.endswith(':ro')

def test_security_documentation_exists():
    """Verify security documentation is present."""
    readme = Path('README.md').read_text()
    assert 'Security Considerations' in readme or 'Security' in readme
    assert 'production' in readme.lower()
```

---

### Summary: Security Requirements Traceability

| Requirement | Priority | Category | Related Goals | Verification |
|-------------|----------|----------|---------------|--------------|
| SEC-DEV-001: Anonymous Grafana Access | N/A | Dev Default | G4, G5 | Documentation |
| SEC-DEV-002: Unauthenticated Metrics | N/A | Dev Default | G4, G5 | Documentation |
| SEC-DEV-003: Unencrypted OTLP | N/A | Dev Default | G4, G5 | Documentation |
| SEC-DEV-004: Loki Auth Disabled | N/A | Dev Default | G4, G5 | Documentation |
| SEC-001: Grafana Authentication | Must Have | Production | G1 | Documentation review |
| SEC-002: Metrics Endpoint Protection | Should Have | Production | G1 | Documentation review |
| SEC-003: TLS for Trace Transport | Should Have | Production | G1 | Documentation review |
| SEC-004: Network Segmentation | Should Have | Production | G1 | Documentation review |
| SEC-005: Secret Management | Must Have | Credentials | G1 | Code review, tests |
| SEC-006: PII in Logs | Must Have | Privacy | G1 | Documentation review |
| SEC-007: PII in Traces | Should Have | Privacy | G1 | Documentation review |
| SEC-008: Data Retention | Should Have | Compliance | G1 | Documentation review |
| SEC-009: Structured Logging | Must Have | Injection Prevention | G1 | Code review |
| SEC-010: Grafana RBAC | Could Have | Access Control | G1 | Documentation review |
| SEC-011: Audit Logging | Could Have | Compliance | G1 | Documentation review |
| SEC-012: Docker Socket Access | Should Have | Container Security | G1 | Compose review |
| SEC-013: Container Image Security | Should Have | Container Security | G1 | Documentation review |
| SEC-014: Security Documentation | Must Have | Documentation | G5 | Test verification |
| SEC-015: Security Config Tests | Should Have | Testing | G1 | Test execution |

**Priority Summary:**
- Must Have: 5 requirements (SEC-001, SEC-005, SEC-006, SEC-009, SEC-014)
- Should Have: 9 requirements
- Could Have: 2 requirements
- Development Defaults: 4 items (documented, not changed)

---

## Testing Strategy

This section defines the comprehensive testing approach for the observability stack integration. Testing spans multiple layers: template generation testing, unit tests for instrumentation code, integration tests for service connectivity, and end-to-end tests for complete observability workflows.

### Testing Philosophy

The testing strategy follows these principles:

1. **Test-Driven Template Development**: Template files are tested via cookiecutter generation tests before manual validation
2. **Fail-Open Testing**: Tests verify that observability failures do not break application functionality (NFR-RL-001)
3. **Fast Feedback Loops**: Unit tests run in < 30 seconds; integration tests in < 5 minutes
4. **Realistic Scenarios**: E2E tests simulate actual developer workflows (viewing dashboards, querying traces)
5. **Isolation**: Tests disable OpenTelemetry exporters in unit tests to avoid external dependencies and performance overhead

### Test Categories

| Category | Code Prefix | Scope | Dependencies | Execution Time |
|----------|-------------|-------|--------------|----------------|
| Template Generation | TG-* | Cookiecutter template output | Python, cookiecutter | < 30s |
| Unit Tests | UT-* | Observability module functions | pytest, mocks | < 30s |
| Integration Tests | IT-* | Service connectivity | Docker Compose, pytest-docker | 2-5 min |
| End-to-End Tests | E2E-* | Full observability workflows | Full stack running | 5-15 min |
| Performance Tests | PT-* | Latency, throughput, resource usage | Full stack, load tools | 15-30 min |
| Security Tests | ST-* | Configuration security | Static analysis, config parsing | < 1 min |

---

### Template Generation Tests

These tests verify that the cookiecutter template generates correct observability files based on configuration options.

#### TG-001: Observability Enabled Generates All Files (Must Have)

**Description**: When `include_observability` is `"yes"`, all observability files are generated.

**Test Implementation**:
```python
# tests/test_template_generation.py
import pytest
from pathlib import Path
from cookiecutter.main import cookiecutter

@pytest.fixture
def generated_project_with_observability(tmp_path):
    """Generate a project with observability enabled."""
    project_dir = cookiecutter(
        str(Path(__file__).parent.parent / "template"),
        output_dir=str(tmp_path),
        no_input=True,
        extra_context={
            "project_slug": "test-project",
            "include_observability": "yes",
        }
    )
    return Path(project_dir)

def test_observability_directory_structure(generated_project_with_observability):
    """Verify observability directory structure is created."""
    project = generated_project_with_observability

    expected_files = [
        "observability/prometheus/prometheus.yml",
        "observability/loki/loki-config.yml",
        "observability/promtail/promtail-config.yml",
        "observability/tempo/tempo.yml",
        "observability/grafana/datasources/datasources.yml",
        "observability/grafana/dashboards/dashboards.yml",
        "observability/grafana/dashboards/backend-dashboard.json",
        "observability/grafana/dashboards/slo-dashboard.json",
        "backend/app/observability.py",
    ]

    for file_path in expected_files:
        assert (project / file_path).exists(), f"Missing: {file_path}"

def test_compose_includes_observability_services(generated_project_with_observability):
    """Verify compose.yml includes observability services."""
    import yaml

    project = generated_project_with_observability
    compose_file = project / "compose.yml"

    with open(compose_file) as f:
        compose = yaml.safe_load(f)

    expected_services = ["prometheus", "loki", "promtail", "tempo", "grafana"]
    for service in expected_services:
        assert service in compose["services"], f"Missing service: {service}"
```

**Traceability**: FR-TC-001, FR-TC-003, FR-TC-004

---

#### TG-002: Observability Disabled Excludes All Files (Must Have)

**Description**: When `include_observability` is `"no"`, no observability files are generated.

**Test Implementation**:
```python
@pytest.fixture
def generated_project_without_observability(tmp_path):
    """Generate a project with observability disabled."""
    project_dir = cookiecutter(
        str(Path(__file__).parent.parent / "template"),
        output_dir=str(tmp_path),
        no_input=True,
        extra_context={
            "project_slug": "test-project",
            "include_observability": "no",
        }
    )
    return Path(project_dir)

def test_no_observability_directory(generated_project_without_observability):
    """Verify observability directory is not created."""
    project = generated_project_without_observability
    assert not (project / "observability").exists()

def test_compose_excludes_observability_services(generated_project_without_observability):
    """Verify compose.yml excludes observability services."""
    import yaml

    project = generated_project_without_observability
    compose_file = project / "compose.yml"

    with open(compose_file) as f:
        compose = yaml.safe_load(f)

    observability_services = ["prometheus", "loki", "promtail", "tempo", "grafana"]
    for service in observability_services:
        assert service not in compose["services"], f"Should not have: {service}"

def test_no_observability_module(generated_project_without_observability):
    """Verify observability.py is not created."""
    project = generated_project_without_observability
    assert not (project / "backend" / "app" / "observability.py").exists()
```

**Traceability**: FR-TC-003, US-006

---

#### TG-003: Configuration Files Are Valid YAML/JSON (Must Have)

**Description**: All generated configuration files are syntactically valid.

**Test Implementation**:
```python
import json

def test_prometheus_config_valid_yaml(generated_project_with_observability):
    """Verify prometheus.yml is valid YAML."""
    import yaml

    project = generated_project_with_observability
    config_file = project / "observability" / "prometheus" / "prometheus.yml"

    with open(config_file) as f:
        config = yaml.safe_load(f)

    assert "global" in config
    assert "scrape_configs" in config

def test_grafana_dashboards_valid_json(generated_project_with_observability):
    """Verify dashboard JSON files are valid."""
    project = generated_project_with_observability
    dashboard_dir = project / "observability" / "grafana" / "dashboards"

    for json_file in dashboard_dir.glob("*.json"):
        with open(json_file) as f:
            dashboard = json.load(f)
        assert "title" in dashboard, f"Dashboard missing title: {json_file}"
        assert "panels" in dashboard, f"Dashboard missing panels: {json_file}"

def test_datasources_valid_yaml(generated_project_with_observability):
    """Verify datasources.yml is valid and has all datasources."""
    import yaml

    project = generated_project_with_observability
    config_file = project / "observability" / "grafana" / "datasources" / "datasources.yml"

    with open(config_file) as f:
        config = yaml.safe_load(f)

    datasource_names = [ds["name"] for ds in config["datasources"]]
    assert "Prometheus" in datasource_names
    assert "Loki" in datasource_names
    assert "Tempo" in datasource_names
```

**Traceability**: FR-TC-004

---

#### TG-004: Port Configuration Applied Correctly (Should Have)

**Description**: Custom port configurations are correctly applied to generated files.

**Test Implementation**:
```python
def test_custom_ports_in_compose(tmp_path):
    """Verify custom ports are applied to compose.yml."""
    import yaml

    project_dir = cookiecutter(
        str(Path(__file__).parent.parent / "template"),
        output_dir=str(tmp_path),
        no_input=True,
        extra_context={
            "project_slug": "test-project",
            "include_observability": "yes",
            "grafana_port": "3001",
            "prometheus_port": "9091",
        }
    )
    project = Path(project_dir)

    with open(project / "compose.yml") as f:
        compose = yaml.safe_load(f)

    grafana_ports = compose["services"]["grafana"]["ports"]
    assert any("3001:3000" in p for p in grafana_ports)

    prometheus_ports = compose["services"]["prometheus"]["ports"]
    assert any("9091:9090" in p for p in prometheus_ports)
```

**Traceability**: FR-TC-002

---

### Unit Tests

Unit tests verify the observability module functions in isolation, with external dependencies mocked.

#### UT-001: Metrics Middleware Records Request Count (Must Have)

**Description**: The Prometheus metrics middleware correctly increments request counters.

**Test Implementation**:
```python
# backend/tests/unit/test_observability.py
import pytest
from unittest.mock import patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Disable OpenTelemetry in tests for performance
@pytest.fixture(autouse=True)
def disable_opentelemetry():
    """Disable OpenTelemetry during unit tests."""
    import os
    os.environ["TESTING"] = "true"
    yield
    os.environ.pop("TESTING", None)

@pytest.fixture
def app_with_observability():
    """Create test app with observability middleware."""
    from app.observability import setup_observability
    from prometheus_client import REGISTRY, CollectorRegistry

    # Use isolated registry for testing
    test_registry = CollectorRegistry()

    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    setup_observability(app, registry=test_registry)
    return app, test_registry

def test_request_count_incremented(app_with_observability):
    """Verify http_requests_total is incremented."""
    app, registry = app_with_observability
    client = TestClient(app)

    # Get initial count
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

    client.get("/test")
    client.get("/test")

    # Check metrics
    metrics = generate_latest(registry).decode()
    assert 'http_requests_total{' in metrics
    assert 'method="GET"' in metrics
    assert 'endpoint="/test"' in metrics
    assert 'status="200"' in metrics
```

**Traceability**: FR-BI-002, US-001

---

#### UT-002: Request Duration Histogram Recorded (Must Have)

**Description**: The request duration histogram correctly records latency.

**Test Implementation**:
```python
def test_request_duration_recorded(app_with_observability):
    """Verify http_request_duration_seconds histogram is recorded."""
    app, registry = app_with_observability
    client = TestClient(app)

    client.get("/test")

    from prometheus_client import generate_latest
    metrics = generate_latest(registry).decode()

    # Histogram should have bucket, count, and sum
    assert 'http_request_duration_seconds_bucket{' in metrics
    assert 'http_request_duration_seconds_count{' in metrics
    assert 'http_request_duration_seconds_sum{' in metrics
```

**Traceability**: FR-BI-003, G2

---

#### UT-003: Active Requests Gauge Tracks Concurrent Requests (Must Have)

**Description**: The active requests gauge correctly tracks in-flight requests.

**Test Implementation**:
```python
import asyncio
from fastapi import FastAPI
from starlette.testclient import TestClient
import threading
import time

def test_active_requests_gauge(app_with_observability):
    """Verify active_requests gauge tracks concurrent requests."""
    app, registry = app_with_observability

    # Add a slow endpoint for testing
    @app.get("/slow")
    async def slow_endpoint():
        await asyncio.sleep(0.5)
        return {"status": "ok"}

    client = TestClient(app)

    # Start request in background
    results = []
    def make_request():
        response = client.get("/slow")
        results.append(response.status_code)

    thread = threading.Thread(target=make_request)
    thread.start()

    # Give time for request to start
    time.sleep(0.1)

    # During request, gauge should be > 0
    # (Note: Exact verification depends on implementation details)

    thread.join()
    assert results[0] == 200
```

**Traceability**: FR-BI-004, US-012

---

#### UT-004: Metrics Endpoint Returns Prometheus Format (Must Have)

**Description**: The `/metrics` endpoint returns valid Prometheus text format.

**Test Implementation**:
```python
def test_metrics_endpoint_format(app_with_observability):
    """Verify /metrics returns Prometheus text format."""
    app, registry = app_with_observability
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    content = response.text
    # Should contain HELP and TYPE annotations
    assert "# HELP" in content
    assert "# TYPE" in content
```

**Traceability**: FR-BI-006, US-011

---

#### UT-005: Trace Context Injected Into Logs (Should Have)

**Description**: When tracing is active, trace_id and span_id are included in log records.

**Test Implementation**:
```python
from unittest.mock import patch, MagicMock
import logging

def test_trace_context_in_logs():
    """Verify trace context is injected into log records."""
    from app.observability import TracingLogFilter

    # Create mock trace context
    mock_span_context = MagicMock()
    mock_span_context.trace_id = 0x1234567890abcdef
    mock_span_context.span_id = 0xfedcba0987654321
    mock_span_context.is_valid = True

    mock_span = MagicMock()
    mock_span.get_span_context.return_value = mock_span_context

    with patch('opentelemetry.trace.get_current_span', return_value=mock_span):
        filter = TracingLogFilter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="Test message", args=(), exc_info=None
        )

        filter.filter(record)

        assert hasattr(record, 'trace_id')
        assert hasattr(record, 'span_id')
        # Trace ID should be formatted as hex string
        assert record.trace_id == "1234567890abcdef"
```

**Traceability**: FR-BI-008, US-003

---

#### UT-006: Graceful Handling When Tempo Unavailable (Must Have)

**Description**: Application does not crash when trace export fails.

**Test Implementation**:
```python
def test_trace_export_failure_handled():
    """Verify application handles trace export failure gracefully."""
    from app.observability import setup_tracing
    from opentelemetry.sdk.trace.export import SpanExportResult
    from unittest.mock import patch, MagicMock

    # Mock exporter that always fails
    mock_exporter = MagicMock()
    mock_exporter.export.return_value = SpanExportResult.FAILURE

    with patch('app.observability.OTLPSpanExporter', return_value=mock_exporter):
        # Should not raise exception
        tracer = setup_tracing(service_name="test", endpoint="http://nonexistent:4317")
        assert tracer is not None
```

**Traceability**: NFR-RL-001, EC-001

---

### Integration Tests

Integration tests verify connectivity and data flow between services using Docker Compose.

#### IT-001: Prometheus Scrapes Backend Metrics (Must Have)

**Description**: Prometheus successfully scrapes metrics from the backend `/metrics` endpoint.

**Test Implementation**:
```python
# backend/tests/integration/test_observability_integration.py
import pytest
import requests
import time

pytestmark = pytest.mark.integration

@pytest.fixture(scope="module")
def observability_stack(docker_compose_project):
    """Start the observability stack via Docker Compose."""
    docker_compose_project.up()

    # Wait for services to be ready
    services = {
        "prometheus": ("http://localhost:9090/-/ready", 30),
        "loki": ("http://localhost:3100/ready", 30),
        "tempo": ("http://localhost:3200/ready", 30),
        "grafana": ("http://localhost:3000/api/health", 30),
        "backend": ("http://localhost:8000/api/v1/health", 30),
    }

    for service, (url, timeout) in services.items():
        wait_for_service(url, timeout)

    yield docker_compose_project

    docker_compose_project.down()

def wait_for_service(url: str, timeout: int):
    """Wait for a service to become available."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(1)
    raise TimeoutError(f"Service at {url} not ready after {timeout}s")

def test_prometheus_scrapes_backend(observability_stack):
    """Verify Prometheus scrapes backend metrics."""
    # Generate some traffic
    for _ in range(5):
        requests.get("http://localhost:8000/api/v1/health")

    # Wait for scrape interval
    time.sleep(20)

    # Query Prometheus for backend metrics
    response = requests.get(
        "http://localhost:9090/api/v1/query",
        params={"query": 'http_requests_total{job="backend"}'}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["data"]["result"]) > 0
```

**Traceability**: FR-MC-001, US-001

---

#### IT-002: Logs Appear in Loki (Must Have)

**Description**: Container logs are collected by Promtail and queryable in Loki.

**Test Implementation**:
```python
def test_logs_in_loki(observability_stack):
    """Verify logs appear in Loki within 10 seconds."""
    # Generate a distinctive log entry
    import uuid
    marker = str(uuid.uuid4())

    # Trigger a request that will be logged
    requests.get(f"http://localhost:8000/api/v1/health?marker={marker}")

    # Wait for log ingestion
    time.sleep(10)

    # Query Loki for backend logs
    response = requests.get(
        "http://localhost:3100/loki/api/v1/query_range",
        params={
            "query": '{container=~".*backend.*"}',
            "start": str(int(time.time()) - 300),
            "end": str(int(time.time())),
            "limit": 100,
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    # Should have some log entries
    assert len(data["data"]["result"]) > 0
```

**Traceability**: FR-LA-003, US-007, NFR-PF-003

---

#### IT-003: Traces Appear in Tempo (Must Have)

**Description**: Distributed traces are exported to Tempo and queryable.

**Test Implementation**:
```python
def test_traces_in_tempo(observability_stack):
    """Verify traces appear in Tempo."""
    # Make a traced request
    response = requests.get("http://localhost:8000/api/v1/health")

    # Wait for trace export (BatchSpanProcessor exports every 5s by default)
    time.sleep(35)

    # Query Tempo for traces (via Grafana API or Tempo API)
    # Note: Tempo search requires TraceQL or service-based search
    response = requests.get(
        "http://localhost:3200/api/search",
        params={
            "tags": "service.name=backend",
            "limit": 10,
        }
    )

    # Tempo search API might return 200 with empty results initially
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        data = response.json()
        # Traces should eventually appear
        # (May need retry logic in real tests)
```

**Traceability**: FR-DT-001, US-002, NFR-PF-004

---

#### IT-004: Grafana Datasources Are Provisioned (Must Have)

**Description**: Grafana has all datasources pre-configured and healthy.

**Test Implementation**:
```python
def test_grafana_datasources_provisioned(observability_stack):
    """Verify Grafana datasources are configured and healthy."""
    # Get datasources
    response = requests.get("http://localhost:3000/api/datasources")

    assert response.status_code == 200
    datasources = response.json()

    datasource_names = [ds["name"] for ds in datasources]
    assert "Prometheus" in datasource_names
    assert "Loki" in datasource_names
    assert "Tempo" in datasource_names

    # Test datasource connectivity
    for ds in datasources:
        health_response = requests.get(
            f"http://localhost:3000/api/datasources/{ds['id']}/health"
        )
        # Should be 200 OK (healthy) or have success status
        assert health_response.status_code == 200
```

**Traceability**: FR-VZ-001, G1

---

#### IT-005: Grafana Dashboards Are Loaded (Must Have)

**Description**: Pre-built dashboards are loaded and accessible in Grafana.

**Test Implementation**:
```python
def test_grafana_dashboards_loaded(observability_stack):
    """Verify dashboards are provisioned in Grafana."""
    # Search for dashboards
    response = requests.get(
        "http://localhost:3000/api/search",
        params={"type": "dash-db"}
    )

    assert response.status_code == 200
    dashboards = response.json()

    dashboard_titles = [d["title"] for d in dashboards]

    expected_dashboards = [
        "Backend Service Dashboard",
        "SLO Overview Dashboard",
        "Log Explorer Dashboard",
        "Trace Explorer Dashboard",
    ]

    for expected in expected_dashboards:
        assert expected in dashboard_titles, f"Missing dashboard: {expected}"
```

**Traceability**: FR-VZ-002, FR-VZ-003, FR-VZ-004, FR-VZ-005, FR-VZ-006

---

#### IT-006: Trace-to-Logs Correlation Works (Should Have)

**Description**: Clicking from a trace to logs returns related log entries.

**Test Implementation**:
```python
def test_trace_to_logs_correlation(observability_stack):
    """Verify trace-to-logs correlation is configured."""
    # Get Tempo datasource
    response = requests.get("http://localhost:3000/api/datasources")
    datasources = response.json()
    tempo_ds = next(ds for ds in datasources if ds["name"] == "Tempo")

    # Verify Tempo has tracesToLogsV2 configured
    ds_details = requests.get(
        f"http://localhost:3000/api/datasources/{tempo_ds['id']}"
    ).json()

    json_data = ds_details.get("jsonData", {})
    assert "tracesToLogsV2" in json_data or "tracesToLogs" in json_data
```

**Traceability**: FR-DC-001, G3

---

### End-to-End Tests

E2E tests validate complete observability workflows from a user's perspective.

#### E2E-001: Developer Views Backend Dashboard (Must Have)

**Description**: A developer can start the stack, generate traffic, and view metrics in the Backend Dashboard.

**Test Implementation** (Playwright):
```typescript
// e2e/observability/backend-dashboard.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Backend Service Dashboard', () => {
  test.beforeAll(async () => {
    // Ensure stack is running and generate some traffic
    for (let i = 0; i < 10; i++) {
      await fetch('http://localhost:8000/api/v1/health');
    }
    // Wait for Prometheus scrape
    await new Promise(resolve => setTimeout(resolve, 20000));
  });

  test('should display request rate panel', async ({ page }) => {
    await page.goto('http://localhost:3000');

    // Navigate to Backend Dashboard
    await page.click('text=Dashboards');
    await page.click('text=Backend Service Dashboard');

    // Verify panels are loaded
    await expect(page.locator('text=Request Rate')).toBeVisible();

    // Verify data is present (panel should have graph or value)
    const requestRatePanel = page.locator('[data-testid="panel-request-rate"]');
    await expect(requestRatePanel).toBeVisible();
  });

  test('should display latency histogram', async ({ page }) => {
    await page.goto('http://localhost:3000/d/backend-service');

    await expect(page.locator('text=Request Duration')).toBeVisible();
  });

  test('should display error rate panel', async ({ page }) => {
    await page.goto('http://localhost:3000/d/backend-service');

    await expect(page.locator('text=Error Rate')).toBeVisible();
  });
});
```

**Traceability**: US-001, Journey 1

---

#### E2E-002: Developer Traces Slow Request (Should Have)

**Description**: A developer can use Grafana Explore to find and view a trace.

**Test Implementation**:
```typescript
test.describe('Trace Exploration', () => {
  test('should find traces in Tempo explorer', async ({ page }) => {
    await page.goto('http://localhost:3000/explore');

    // Select Tempo datasource
    await page.click('[data-testid="datasource-picker"]');
    await page.click('text=Tempo');

    // Search for traces by service
    await page.fill('[data-testid="query-input"]', '{ resource.service.name="backend" }');
    await page.click('button:has-text("Run query")');

    // Wait for results
    await page.waitForSelector('[data-testid="trace-result"]', { timeout: 30000 });

    // Should have at least one trace
    const traces = page.locator('[data-testid="trace-result"]');
    await expect(traces).toHaveCount({ min: 1 });
  });

  test('should view trace details', async ({ page }) => {
    await page.goto('http://localhost:3000/explore');

    // Select Tempo and run query
    // ... (similar setup as above)

    // Click on a trace
    await page.click('[data-testid="trace-result"]:first-child');

    // Should see trace timeline/flame graph
    await expect(page.locator('[data-testid="trace-timeline"]')).toBeVisible();
  });
});
```

**Traceability**: US-002, Journey 1

---

#### E2E-003: Engineer Queries Error Logs (Should Have)

**Description**: An engineer can filter logs by error level and find specific error entries.

**Test Implementation**:
```typescript
test.describe('Log Exploration', () => {
  test('should query logs in Loki explorer', async ({ page }) => {
    await page.goto('http://localhost:3000/explore');

    // Select Loki datasource
    await page.click('[data-testid="datasource-picker"]');
    await page.click('text=Loki');

    // Query backend logs
    await page.fill('[data-testid="query-input"]', '{container=~".*backend.*"}');
    await page.click('button:has-text("Run query")');

    // Wait for results
    await page.waitForSelector('[data-testid="log-line"]', { timeout: 30000 });

    // Should have log entries
    const logs = page.locator('[data-testid="log-line"]');
    await expect(logs).toHaveCount({ min: 1 });
  });

  test('should filter logs by level', async ({ page }) => {
    await page.goto('http://localhost:3000/explore');

    // Query error logs
    await page.fill('[data-testid="query-input"]', '{container=~".*backend.*"} |= "ERROR"');
    await page.click('button:has-text("Run query")');

    // Results should only contain ERROR level
    // (May be empty if no errors occurred)
  });
});
```

**Traceability**: US-003, US-007, Journey 2

---

### Performance Tests

Performance tests verify latency, throughput, and resource efficiency requirements.

#### PT-001: Stack Startup Time (Must Have)

**Description**: All observability services start within 90 seconds.

**Test Implementation**:
```python
# backend/tests/performance/test_observability_performance.py
import pytest
import subprocess
import time
import requests

pytestmark = pytest.mark.performance

def test_observability_stack_startup_time(tmp_path):
    """Verify observability stack starts within 90 seconds."""
    start_time = time.time()

    # Start stack
    subprocess.run(
        ["docker", "compose", "up", "-d"],
        check=True,
        cwd=tmp_path,
    )

    services = {
        "prometheus": "http://localhost:9090/-/ready",
        "loki": "http://localhost:3100/ready",
        "tempo": "http://localhost:3200/ready",
        "grafana": "http://localhost:3000/api/health",
    }

    # Wait for all services
    for service, url in services.items():
        deadline = start_time + 90
        while time.time() < deadline:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        else:
            pytest.fail(f"{service} not ready within 90 seconds")

    total_time = time.time() - start_time
    assert total_time < 90, f"Stack took {total_time:.1f}s to start"
```

**Traceability**: NFR-PF-001

---

#### PT-002: Metrics Endpoint Latency (Must Have)

**Description**: The `/metrics` endpoint responds within 100ms.

**Test Implementation**:
```python
def test_metrics_endpoint_latency(observability_stack):
    """Verify /metrics responds within 100ms."""
    import statistics

    latencies = []
    for _ in range(50):
        start = time.time()
        response = requests.get("http://localhost:8000/metrics")
        latency = (time.time() - start) * 1000  # ms
        latencies.append(latency)
        assert response.status_code == 200

    p50 = statistics.median(latencies)
    p95 = sorted(latencies)[int(len(latencies) * 0.95)]
    p99 = sorted(latencies)[int(len(latencies) * 0.99)]

    print(f"Metrics endpoint latency: p50={p50:.1f}ms, p95={p95:.1f}ms, p99={p99:.1f}ms")

    assert p95 < 100, f"p95 latency {p95:.1f}ms exceeds 100ms"
```

**Traceability**: NFR-PF-002

---

#### PT-003: Application Performance Overhead (Must Have)

**Description**: Instrumentation adds less than 5% latency overhead.

**Test Implementation**:
```python
def test_instrumentation_overhead():
    """Verify instrumentation overhead is < 5%."""
    # This test requires running with and without observability
    # and comparing latencies

    # Run baseline (observability disabled)
    baseline_latencies = []
    for _ in range(100):
        start = time.time()
        response = requests.get("http://localhost:8000/api/v1/health")
        latencies.append((time.time() - start) * 1000)

    baseline_p95 = sorted(baseline_latencies)[95]

    # Enable observability and re-test
    # (Would need to restart with observability enabled)
    instrumented_latencies = []
    # ... similar test ...

    instrumented_p95 = sorted(instrumented_latencies)[95]

    overhead = ((instrumented_p95 - baseline_p95) / baseline_p95) * 100
    assert overhead < 5, f"Overhead {overhead:.1f}% exceeds 5%"
```

**Traceability**: NFR-PF-005

---

#### PT-004: Memory Footprint (Must Have)

**Description**: Combined observability memory usage is under 2GB.

**Test Implementation**:
```python
import docker

def test_memory_footprint(observability_stack):
    """Verify combined memory usage < 2GB."""
    client = docker.from_env()

    observability_containers = [
        "test-project-prometheus",
        "test-project-loki",
        "test-project-promtail",
        "test-project-tempo",
        "test-project-grafana",
    ]

    total_memory_mb = 0
    for container_name in observability_containers:
        container = client.containers.get(container_name)
        stats = container.stats(stream=False)
        memory_usage = stats["memory_stats"]["usage"]
        memory_mb = memory_usage / (1024 * 1024)
        total_memory_mb += memory_mb
        print(f"{container_name}: {memory_mb:.1f}MB")

    print(f"Total: {total_memory_mb:.1f}MB")
    assert total_memory_mb < 2048, f"Total memory {total_memory_mb:.1f}MB exceeds 2GB"
```

**Traceability**: NFR-RE-001

---

### Security Tests

Security tests verify configuration security as defined in SEC-014 and SEC-015.

#### ST-001: No Hardcoded Passwords (Must Have)

**Description**: Configuration files do not contain hardcoded passwords.

**Test Implementation**:
```python
# backend/tests/security/test_observability_security.py
import pytest
from pathlib import Path
import re

pytestmark = pytest.mark.security

def test_no_hardcoded_passwords(generated_project_with_observability):
    """Verify no passwords are hardcoded in configuration files."""
    project = generated_project_with_observability

    config_files = [
        "observability/prometheus/prometheus.yml",
        "observability/grafana/datasources/datasources.yml",
        "compose.yml",
    ]

    password_patterns = [
        r'password:\s*["\']?[a-zA-Z0-9]+["\']?',  # password: value
        r'secret:\s*["\']?[a-zA-Z0-9]+["\']?',    # secret: value
        r'api_key:\s*["\']?[a-zA-Z0-9]+["\']?',   # api_key: value
    ]

    for file_path in config_files:
        full_path = project / file_path
        if not full_path.exists():
            continue

        content = full_path.read_text()

        for pattern in password_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Filter out environment variable references
            for match in matches:
                if '${' not in match and '$(' not in match:
                    pytest.fail(f"Potential hardcoded secret in {file_path}: {match}")
```

**Traceability**: SEC-005, SEC-015

---

#### ST-002: Docker Socket Read-Only (Must Have)

**Description**: Docker socket is mounted read-only for Promtail.

**Test Implementation**:
```python
import yaml

def test_docker_socket_readonly(generated_project_with_observability):
    """Verify Docker socket is mounted read-only."""
    project = generated_project_with_observability

    with open(project / "compose.yml") as f:
        compose = yaml.safe_load(f)

    promtail_volumes = compose["services"]["promtail"]["volumes"]

    docker_sock_mounts = [v for v in promtail_volumes if "docker.sock" in v]
    assert len(docker_sock_mounts) > 0, "Docker socket not mounted"

    for mount in docker_sock_mounts:
        assert ":ro" in mount, f"Docker socket not read-only: {mount}"
```

**Traceability**: SEC-012, SEC-015

---

#### ST-003: Security Documentation Exists (Must Have)

**Description**: Generated project includes security documentation.

**Test Implementation**:
```python
def test_security_documentation_exists(generated_project_with_observability):
    """Verify security documentation is present."""
    project = generated_project_with_observability

    readme = (project / "README.md").read_text()

    # Check for security section
    assert "security" in readme.lower(), "README missing security section"

    # Check for production warnings
    assert "production" in readme.lower(), "README missing production guidance"

    # Check for specific warnings
    security_keywords = [
        "anonymous",
        "authentication",
        "GF_AUTH",
    ]

    for keyword in security_keywords:
        assert keyword.lower() in readme.lower(), f"Missing security topic: {keyword}"
```

**Traceability**: SEC-014

---

### Test Configuration and Fixtures

#### Pytest Configuration

```python
# conftest.py additions for observability testing

import pytest
import os

def pytest_configure(config):
    """Configure pytest markers for observability tests."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "security: marks tests as security tests")
    config.addinivalue_line("markers", "e2e: marks tests as end-to-end tests")

@pytest.fixture(autouse=True)
def disable_telemetry_in_tests():
    """Disable OpenTelemetry exporters during unit tests."""
    os.environ["TESTING"] = "true"
    os.environ["OTEL_SDK_DISABLED"] = "true"  # OpenTelemetry SDK disable
    yield
    os.environ.pop("TESTING", None)
    os.environ.pop("OTEL_SDK_DISABLED", None)

@pytest.fixture(scope="session")
def docker_compose_project():
    """Fixture for managing Docker Compose in integration tests."""
    from python_on_whales import DockerClient

    docker = DockerClient(compose_files=["compose.yml"])
    return docker
```

#### Playwright Configuration for E2E

```typescript
// playwright.config.ts additions for observability E2E tests

import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  projects: [
    {
      name: 'observability',
      testMatch: /observability\/.*.spec.ts/,
      use: {
        baseURL: 'http://localhost:3000', // Grafana
      },
      // Longer timeout for dashboard loading
      timeout: 60000,
    },
  ],
  // E2E tests require full stack
  webServer: {
    command: 'docker compose up',
    url: 'http://localhost:3000/api/health',
    timeout: 120000,
    reuseExistingServer: true,
  },
});
```

---

### Test Execution Strategy

#### CI/CD Pipeline Integration

```yaml
# .github/workflows/test-observability.yml (example structure)
name: Observability Tests

on:
  push:
    paths:
      - 'template/**/observability/**'
      - 'template/**/observability.py'

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest tests/unit -m "not integration" --tb=short
        timeout-minutes: 5

  integration-tests:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:dind
    steps:
      - uses: actions/checkout@v4
      - name: Start observability stack
        run: docker compose up -d
      - name: Wait for services
        run: ./scripts/wait-for-services.sh
      - name: Run integration tests
        run: pytest tests/integration -m integration --tb=short
        timeout-minutes: 10

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate test project
        run: cookiecutter template/ --no-input -o /tmp
      - name: Run security tests
        run: pytest tests/security -m security --tb=short
        timeout-minutes: 2
```

#### Local Development Testing

```bash
# Run all observability tests locally
pytest tests/ -m "unit or integration or security" -v

# Run only unit tests (fast feedback)
pytest tests/unit -v --tb=short

# Run integration tests (requires Docker)
docker compose up -d
pytest tests/integration -m integration -v

# Run E2E tests (requires full stack)
npm run test:e2e -- --grep "observability"
```

---

### Test Coverage Requirements

| Test Category | Minimum Coverage | Critical Paths |
|---------------|------------------|----------------|
| Template Generation | 100% of file generation logic | Conditional rendering, port substitution |
| Unit Tests (observability.py) | 80% line coverage | Metrics middleware, trace context injection |
| Integration Tests | All service connectivity | Prometheus scrape, Loki ingestion, Tempo export |
| E2E Tests | Core user journeys | Dashboard viewing, trace exploration, log querying |
| Security Tests | All SEC-014, SEC-015 requirements | Password scanning, socket permissions |

---

### Requirements Traceability Matrix

| Test ID | Requirement | Priority | Automated | CI Integration |
|---------|-------------|----------|-----------|----------------|
| TG-001 | FR-TC-001, FR-TC-003, FR-TC-004 | Must Have | Yes | Yes |
| TG-002 | FR-TC-003, US-006 | Must Have | Yes | Yes |
| TG-003 | FR-TC-004 | Must Have | Yes | Yes |
| TG-004 | FR-TC-002 | Should Have | Yes | Yes |
| UT-001 | FR-BI-002 | Must Have | Yes | Yes |
| UT-002 | FR-BI-003 | Must Have | Yes | Yes |
| UT-003 | FR-BI-004 | Must Have | Yes | Yes |
| UT-004 | FR-BI-006 | Must Have | Yes | Yes |
| UT-005 | FR-BI-008 | Should Have | Yes | Yes |
| UT-006 | NFR-RL-001 | Must Have | Yes | Yes |
| IT-001 | FR-MC-001 | Must Have | Yes | Yes |
| IT-002 | FR-LA-003 | Must Have | Yes | Yes |
| IT-003 | FR-DT-001 | Must Have | Yes | Yes |
| IT-004 | FR-VZ-001 | Must Have | Yes | Yes |
| IT-005 | FR-VZ-002 through FR-VZ-006 | Must Have | Yes | Yes |
| IT-006 | FR-DC-001 | Should Have | Yes | Yes |
| E2E-001 | US-001, Journey 1 | Must Have | Yes | Optional |
| E2E-002 | US-002 | Should Have | Yes | Optional |
| E2E-003 | US-003, US-007 | Should Have | Yes | Optional |
| PT-001 | NFR-PF-001 | Must Have | Yes | Nightly |
| PT-002 | NFR-PF-002 | Must Have | Yes | Nightly |
| PT-003 | NFR-PF-005 | Must Have | Manual | Quarterly |
| PT-004 | NFR-RE-001 | Must Have | Yes | Nightly |
| ST-001 | SEC-005, SEC-015 | Must Have | Yes | Yes |
| ST-002 | SEC-012 | Must Have | Yes | Yes |
| ST-003 | SEC-014 | Must Have | Yes | Yes |

---

### Summary

**Total Test Requirements**: 24 tests across 6 categories

| Category | Must Have | Should Have | Total |
|----------|-----------|-------------|-------|
| Template Generation | 3 | 1 | 4 |
| Unit Tests | 5 | 1 | 6 |
| Integration Tests | 5 | 1 | 6 |
| End-to-End Tests | 1 | 2 | 3 |
| Performance Tests | 4 | 0 | 4 |
| Security Tests | 3 | 0 | 3 |

**Key Testing Tools**:
- **pytest**: Unit and integration tests
- **pytest-docker**: Docker Compose integration
- **Playwright**: E2E browser tests for Grafana dashboards
- **cookiecutter**: Template generation testing
- **prometheus-client**: Metrics testing utilities

**References**:
- [pytest-opentelemetry](https://pypi.org/project/pytest-opentelemetry/) - For tracing test runs
- [opentelemetry-test-utils](https://pypi.org/project/opentelemetry-test-utils/) - OpenTelemetry testing utilities
- [prometheus-fastapi-instrumentator](https://github.com/trallnag/prometheus-fastapi-instrumentator) - Prometheus metrics for FastAPI
- [OpenTelemetry Python Testing Issue #3480](https://github.com/open-telemetry/opentelemetry-python/issues/3480) - Best practices for unit testing with OpenTelemetry

---

## Implementation Phases

This section defines the implementation phases for integrating the observability stack into the cookiecutter template. The phases are designed to be independently testable and mergeable, following the port-and-adapt strategy from `implementation-manager/` as the reference implementation.

### Phase Overview

| Phase | Name | Duration Estimate | Dependencies | Key Deliverables |
|-------|------|-------------------|--------------|------------------|
| **Phase 1** | Infrastructure Setup | 2-3 days | None | Observability directory structure, Docker Compose services, configuration files |
| **Phase 2** | Backend Instrumentation | 2-3 days | Phase 1 | `observability.py` module, Python dependencies, main.py integration |
| **Phase 3** | Visualization Layer | 1-2 days | Phase 1 | Grafana datasources, Backend Service dashboard (ported from source), dashboard provisioning |
| **Phase 4** | Template Conditionals | 1-2 days | Phases 1-3 | `include_observability` toggle, Jinja2 conditionals, cookiecutter.json |
| **Phase 5** | Documentation & Testing | 2-3 days | Phases 1-4 | README updates, observability docs, validation tests, CI integration |

**Total Estimated Duration**: 7-10 days (revised from 9-14 days due to simplified dashboard scope)

---

### Phase 1: Infrastructure Setup

**Objective**: Establish the observability infrastructure in the template, including all Docker Compose services and configuration files for Prometheus, Loki, Promtail, Tempo, and Grafana.

#### Phase 1.1: Create Observability Directory Structure

**Description**: Create the `observability/` directory hierarchy in the template with all required subdirectories.

**Tasks**:
1. Create directory structure:
   ```
   template/{{cookiecutter.project_slug}}/observability/
   ├── prometheus/
   │   └── prometheus.yml
   ├── loki/
   │   └── loki-config.yml
   ├── promtail/
   │   └── promtail-config.yml
   ├── tempo/
   │   └── tempo.yml
   ├── grafana/
   │   ├── datasources/
   │   │   └── datasources.yml
   │   └── dashboards/
   │       ├── dashboards.yml
   │       └── *.json (dashboard files)
   └── README.md
   ```

**Source Reference**: `implementation-manager/observability/` directory structure

**Acceptance Criteria**:
- [ ] All directories created in template path
- [ ] Directory structure matches implementation-manager reference
- [ ] Empty placeholder files created for subsequent phases

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/` directory tree

---

#### Phase 1.2: Port Prometheus Configuration

**Description**: Templatize and port the Prometheus configuration from implementation-manager.

**Tasks**:
1. Copy `implementation-manager/observability/prometheus/prometheus.yml`
2. Templatize with Jinja2 variables:
   - Replace hardcoded cluster name with `{{ cookiecutter.project_slug }}`
   - Ensure target service names match template conventions

**Configuration Template**:
```yaml
# template/{{cookiecutter.project_slug}}/observability/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: '{{ cookiecutter.project_slug }}'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'keycloak'
    static_configs:
      - targets: ['keycloak:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'tempo'
    static_configs:
      - targets: ['tempo:3200']
    metrics_path: '/metrics'

  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
    metrics_path: '/metrics'
```

**Source Reference**: `implementation-manager/observability/prometheus/prometheus.yml`

**Acceptance Criteria**:
- [ ] Configuration validates against Prometheus config schema
- [ ] Project slug is properly templatized
- [ ] All scrape targets use correct service names from compose.yml

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/prometheus/prometheus.yml`

---

#### Phase 1.3: Port Loki Configuration

**Description**: Port the Loki configuration for log aggregation.

**Tasks**:
1. Copy `implementation-manager/observability/loki/loki-config.yml`
2. Review for any hardcoded values requiring templatization
3. Ensure filesystem storage paths align with Docker volume mounts

**Source Reference**: `implementation-manager/observability/loki/loki-config.yml`

**Acceptance Criteria**:
- [ ] Configuration validates against Loki config schema
- [ ] Storage paths match volume mount paths in compose.yml
- [ ] Analytics reporting disabled for privacy

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/loki/loki-config.yml`

---

#### Phase 1.4: Port Promtail Configuration

**Description**: Templatize and port the Promtail configuration for Docker container log collection.

**Tasks**:
1. Copy `implementation-manager/observability/promtail/promtail-config.yml`
2. Templatize container name filters with `{{ cookiecutter.project_slug }}`
3. Ensure Docker socket path is correct for container discovery

**Key Configuration Points**:
- Docker socket mount for container discovery: `/var/run/docker.sock`
- Container log path: `/var/lib/docker/containers`
- Loki push endpoint: `http://loki:3100/loki/api/v1/push`

**Source Reference**: `implementation-manager/observability/promtail/promtail-config.yml`

**Acceptance Criteria**:
- [ ] Configuration validates against Promtail config schema
- [ ] Container filtering uses templatized project slug
- [ ] Docker socket and log paths are correct

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/promtail/promtail-config.yml`

---

#### Phase 1.5: Port Tempo Configuration

**Description**: Port the Tempo configuration for distributed tracing.

**Tasks**:
1. Copy `implementation-manager/observability/tempo/tempo.yml`
2. Review OTLP receiver configuration (gRPC port 4317, HTTP port 4318)
3. Ensure storage paths align with Docker volume mounts

**Key Configuration Points**:
- OTLP gRPC receiver: port 4317
- OTLP HTTP receiver: port 4318
- Tempo API: port 3200
- Local filesystem backend for development

**Source Reference**: `implementation-manager/observability/tempo/tempo.yml`

**Acceptance Criteria**:
- [ ] Configuration validates against Tempo config schema
- [ ] OTLP receivers enabled on correct ports
- [ ] Storage backend configured for filesystem (development mode)

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/tempo/tempo.yml`

---

#### Phase 1.6: Add Observability Services to Docker Compose

**Description**: Add the 5 observability services (Prometheus, Loki, Promtail, Tempo, Grafana) to the template's compose.yml with conditional Jinja2 blocks.

**Tasks**:
1. Add service definitions for all 5 services
2. Wrap in `{% if cookiecutter.include_observability == "yes" %}` conditionals
3. Configure health checks for each service
4. Add volume definitions for persistent storage
5. Configure service dependencies (Promtail -> Loki, Grafana -> all)

**Docker Compose Service Definitions**:
```yaml
{% if cookiecutter.include_observability == "yes" %}
  # Observability Stack
  prometheus:
    image: prom/prometheus:latest
    container_name: {{ cookiecutter.project_slug }}-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    volumes:
      - ./observability/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - default

  loki:
    image: grafana/loki:latest
    container_name: {{ cookiecutter.project_slug }}-loki
    command: -config.file=/etc/loki/local-config.yaml
    ports:
      - "3100:3100"
    volumes:
      - ./observability/loki/loki-config.yml:/etc/loki/local-config.yaml:ro
      - loki-data:/loki
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3100/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - default

  promtail:
    image: grafana/promtail:latest
    container_name: {{ cookiecutter.project_slug }}-promtail
    command: -config.file=/etc/promtail/promtail-config.yml
    volumes:
      - ./observability/promtail/promtail-config.yml:/etc/promtail/promtail-config.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      loki:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - default

  tempo:
    image: grafana/tempo:latest
    container_name: {{ cookiecutter.project_slug }}-tempo
    command: ["-config.file=/etc/tempo.yaml"]
    ports:
      - "3200:3200"   # Tempo API
      - "4317:4317"   # OTLP gRPC
      - "4318:4318"   # OTLP HTTP
    volumes:
      - ./observability/tempo/tempo.yml:/etc/tempo.yaml:ro
      - tempo-data:/tmp/tempo
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3200/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - default

  grafana:
    image: grafana/grafana:latest
    container_name: {{ cookiecutter.project_slug }}-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
      - GF_AUTH_DISABLE_LOGIN_FORM=true
    volumes:
      - ./observability/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - ./observability/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - grafana-data:/var/lib/grafana
    depends_on:
      prometheus:
        condition: service_healthy
      loki:
        condition: service_healthy
      tempo:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - default
{% endif %}
```

**Volume Definitions**:
```yaml
volumes:
  # ... existing volumes ...
{% if cookiecutter.include_observability == "yes" %}
  prometheus-data:
    name: {{ cookiecutter.project_slug }}-prometheus-data
  loki-data:
    name: {{ cookiecutter.project_slug }}-loki-data
  tempo-data:
    name: {{ cookiecutter.project_slug }}-tempo-data
  grafana-data:
    name: {{ cookiecutter.project_slug }}-grafana-data
{% endif %}
```

**Source Reference**: `implementation-manager/docker-compose.yml` lines 91-170

**Acceptance Criteria**:
- [ ] All 5 services defined with correct image tags
- [ ] Container names use project_slug prefix
- [ ] Health checks configured for Prometheus, Loki, Tempo, Grafana
- [ ] Service dependencies properly configured
- [ ] Volumes defined with project_slug prefix
- [ ] Jinja2 conditionals wrap all observability content
- [ ] Services start successfully with `docker compose up`

**Deliverables**:
- Updated `template/{{cookiecutter.project_slug}}/compose.yml`

---

#### Phase 1.7: Create Observability README

**Description**: Create initial README for the observability directory explaining the stack components.

**Tasks**:
1. Document each service and its purpose
2. List exposed ports and endpoints
3. Provide quick-start commands
4. Reference main project README for detailed usage

**Source Reference**: `implementation-manager/observability/README.md`

**Acceptance Criteria**:
- [ ] README documents all 5 services
- [ ] Ports and endpoints clearly listed
- [ ] Cross-references main documentation

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/README.md`

---

#### Phase 1 Completion Criteria

**Integration Test**:
1. Generate a project with `include_observability: yes`
2. Run `docker compose up -d`
3. Verify all 5 observability services reach healthy status
4. Access Grafana at `localhost:3000` (should display login-free interface)
5. Verify Prometheus at `localhost:9090` shows configured targets

**Rollback Plan**: If Phase 1 fails, remove observability directory and compose.yml changes. No impact on existing template functionality.

**Traceability**: FR-IS-001 through FR-IS-007, FR-TC-001, FR-TC-003, FR-TC-004, NFR-PF-001, NFR-RL-002, NFR-RE-001

---

### Phase 2: Backend Instrumentation

**Objective**: Add OpenTelemetry tracing and Prometheus metrics instrumentation to the backend service, enabling automatic request tracing and metrics collection.

#### Phase 2.1: Add Observability Python Dependencies

**Description**: Add the required Python packages for OpenTelemetry and Prometheus instrumentation to the backend's pyproject.toml.

**Tasks**:
1. Add dependencies conditionally based on `include_observability`
2. Include version constraints compatible with Python 3.10-3.12

**Required Dependencies**:
```toml
# Observability dependencies (when include_observability == "yes")
opentelemetry-api = "^1.21.0"
opentelemetry-sdk = "^1.21.0"
opentelemetry-exporter-otlp-proto-grpc = "^1.21.0"
opentelemetry-instrumentation-fastapi = "^0.42b0"
prometheus-client = "^0.19.0"
```

**Conditional Template Logic**:
```toml
[tool.poetry.dependencies]
# ... existing dependencies ...
{% if cookiecutter.include_observability == "yes" %}
opentelemetry-api = "^1.21.0"
opentelemetry-sdk = "^1.21.0"
opentelemetry-exporter-otlp-proto-grpc = "^1.21.0"
opentelemetry-instrumentation-fastapi = "^0.42b0"
prometheus-client = "^0.19.0"
{% endif %}
```

**Source Reference**: `implementation-manager/backend/pyproject.toml` (inferred from imports in observability.py)

**Acceptance Criteria**:
- [ ] Dependencies added with appropriate version constraints
- [ ] Jinja2 conditional wrapping for observability toggle
- [ ] `poetry lock` succeeds with new dependencies
- [ ] Dependencies compatible with Python 3.10, 3.11, 3.12

**Deliverables**:
- Updated `template/{{cookiecutter.project_slug}}/backend/pyproject.toml`

---

#### Phase 2.2: Create Observability Module

**Description**: Port and templatize the `observability.py` module from implementation-manager.

**Tasks**:
1. Copy `implementation-manager/backend/observability.py` to template
2. Templatize service name with `{{ cookiecutter.project_slug }}`
3. Add comprehensive docstrings and inline comments
4. Implement test mode detection for trace context

**Module Structure**:
```python
# template/{{cookiecutter.project_slug}}/backend/app/observability.py
"""
Observability instrumentation for {{ cookiecutter.project_name }}.

This module configures:
- OpenTelemetry distributed tracing (exports to Tempo)
- Prometheus metrics (exposed at /metrics endpoint)
- Structured logging with trace context correlation

Environment Variables:
- OTEL_SERVICE_NAME: Service name for traces (default: "backend")
- OTEL_EXPORTER_OTLP_ENDPOINT: Tempo endpoint (default: "http://tempo:4317")
- TESTING: Set to "true" to disable trace context in logs
"""

import logging
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

# ... implementation following implementation-manager/backend/observability.py
```

**Source Reference**: `implementation-manager/backend/observability.py` (lines 1-103)

**Acceptance Criteria**:
- [ ] Module contains all OpenTelemetry configuration
- [ ] Prometheus metrics defined (http_requests_total, http_request_duration_seconds, active_requests)
- [ ] `setup_observability(app)` function implemented
- [ ] `/metrics` endpoint registered
- [ ] Test mode disables trace context in logs
- [ ] Comprehensive docstrings and comments included

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/backend/app/observability.py`

---

#### Phase 2.3: Integrate Observability into main.py

**Description**: Modify the backend's main.py to conditionally initialize observability.

**Tasks**:
1. Add conditional import for observability module
2. Call `setup_observability(app)` after app creation
3. Ensure observability setup is skipped when disabled

**Integration Pattern** (using Jinja2 conditionals):
```python
# In main.py imports section
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}

# After app creation
app = FastAPI(
    title="{{ cookiecutter.project_name }} API",
    # ...
)

{% if cookiecutter.include_observability == "yes" %}
# Setup observability (metrics, tracing, logging)
setup_observability(app)
{% endif %}
```

**Source Reference**: `implementation-manager/backend/main.py` (lines 8, 56-57)

**Acceptance Criteria**:
- [ ] Conditional import with Jinja2
- [ ] `setup_observability(app)` called after FastAPI app creation
- [ ] Application starts successfully with observability enabled
- [ ] Application starts successfully with observability disabled
- [ ] `/metrics` endpoint accessible when enabled

**Deliverables**:
- Updated `template/{{cookiecutter.project_slug}}/backend/app/main.py`

---

#### Phase 2.4: Add Backend Environment Variables

**Description**: Add observability-related environment variables to the backend service in compose.yml.

**Tasks**:
1. Add `OTEL_SERVICE_NAME` environment variable
2. Add `OTEL_EXPORTER_OTLP_ENDPOINT` pointing to Tempo
3. Document environment variables in .env.example

**Environment Variables**:
```yaml
# In compose.yml backend service
environment:
  # ... existing variables ...
{% if cookiecutter.include_observability == "yes" %}
  OTEL_SERVICE_NAME: backend
  OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317
{% endif %}
```

**Source Reference**: `implementation-manager/docker-compose.yml` (lines 56-57)

**Acceptance Criteria**:
- [ ] Environment variables added to backend service
- [ ] Variables wrapped in Jinja2 conditional
- [ ] .env.example documents observability variables

**Deliverables**:
- Updated `template/{{cookiecutter.project_slug}}/compose.yml` (backend service section)
- Updated `template/{{cookiecutter.project_slug}}/.env.example`

---

#### Phase 2 Completion Criteria

**Integration Test**:
1. Generate a project with `include_observability: yes`
2. Run `docker compose up -d`
3. Make HTTP requests to the backend (e.g., `curl http://localhost:8000/api/v1/health`)
4. Verify `/metrics` endpoint returns Prometheus metrics format
5. Verify traces appear in Tempo (via Grafana Explore)
6. Verify metrics appear in Prometheus targets as "UP"

**Unit Test Requirements**:
- Test `setup_observability()` function can be called without errors
- Test metrics are incremented on request
- Test trace context is propagated

**Rollback Plan**: If Phase 2 fails, remove `observability.py`, revert main.py changes, and remove dependencies. Phase 1 infrastructure remains intact.

**Traceability**: FR-BI-001 through FR-BI-010, FR-MC-001, FR-MC-002, FR-DT-001 through FR-DT-004, FR-ENV-001, NFR-PF-002, NFR-PF-004, NFR-PF-005, NFR-RL-001

---

### Phase 3: Visualization Layer

**Objective**: Configure Grafana with datasources for Prometheus, Loki, and Tempo, and create 4 pre-built dashboards for immediate observability value.

#### Phase 3.1: Configure Grafana Datasources

**Description**: Create the Grafana datasource provisioning configuration for automatic datasource setup.

**Tasks**:
1. Create datasources.yml with Prometheus, Loki, and Tempo configurations
2. Configure datasource correlation (Tempo -> Loki, Tempo -> Prometheus)
3. Templatize service URLs with Docker Compose service names

**Datasource Configuration**:
```yaml
# template/{{cookiecutter.project_slug}}/observability/grafana/datasources/datasources.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: false
    jsonData:
      derivedFields:
        - datasourceUid: tempo
          matcherRegex: "trace_id=(\\w+)"
          name: TraceID
          url: "$${__value.raw}"

  - name: Tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    uid: tempo
    editable: false
    jsonData:
      tracesToLogs:
        datasourceUid: loki
        filterByTraceID: true
        filterBySpanID: false
        lokiSearch: true
      tracesToMetrics:
        datasourceUid: prometheus
        queries:
          - name: Request Rate
            query: 'sum(rate(http_requests_total{$$__tags}[5m]))'
          - name: Request Duration
            query: 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{$$__tags}[5m])) by (le))'
```

**Source Reference**: `implementation-manager/observability/grafana/datasources/datasources.yml`

**Acceptance Criteria**:
- [ ] All 3 datasources configured (Prometheus, Loki, Tempo)
- [ ] Prometheus set as default datasource
- [ ] Tempo-to-Loki correlation configured (tracesToLogs)
- [ ] Tempo-to-Prometheus correlation configured (tracesToMetrics)
- [ ] Loki-to-Tempo correlation configured (derivedFields)
- [ ] Grafana starts with datasources pre-configured

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/grafana/datasources/datasources.yml`

---

#### Phase 3.2: Configure Dashboard Provisioning

**Description**: Create the Grafana dashboard provisioning configuration to automatically load dashboards from the dashboards directory.

**Tasks**:
1. Create dashboards.yml provisioning file
2. Configure folder organization for dashboards

**Dashboard Provisioning Configuration**:
```yaml
# template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/dashboards.yml
apiVersion: 1

providers:
  - name: '{{ cookiecutter.project_slug }}'
    orgId: 1
    folder: '{{ cookiecutter.project_name }}'
    folderUid: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

**Source Reference**: `implementation-manager/observability/grafana/dashboards/dashboards.yml`

**Acceptance Criteria**:
- [ ] Dashboard provisioning enabled
- [ ] Folder uses project name
- [ ] Dashboard JSON files automatically loaded

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/dashboards.yml`

---

#### Phase 3.3: Create Backend Service Dashboard

**Description**: Create the primary dashboard for monitoring backend service health using the RED method (Rate, Errors, Duration).

**Dashboard Panels**:
1. **Request Rate** - `sum(rate(http_requests_total[5m]))` by endpoint
2. **Error Rate** - `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`
3. **Request Duration (p95)** - `histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
4. **Request Duration (p99)** - `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
5. **Active Requests** - `active_requests`
6. **Requests by Status Code** - `sum(rate(http_requests_total[5m])) by (status)`
7. **Top Endpoints by Request Rate** - Table panel
8. **Slowest Endpoints (p95)** - Table panel

**Dashboard Layout** (as defined in UI/UX Considerations):
- Row 1: Key metrics (Request Rate, Error Rate, p95 Latency, Active Requests)
- Row 2: Time series graphs (Request Rate over time, Latency distribution)
- Row 3: Tables (Top endpoints, Error breakdown)

**Source Reference**: `implementation-manager/observability/grafana/dashboards/backend-dashboard.json`

**Acceptance Criteria**:
- [ ] Dashboard loads without errors
- [ ] All 8 panels display data correctly
- [ ] Time range selector works (1h, 6h, 24h, 7d)
- [ ] Auto-refresh enabled (10s default)
- [ ] Variables for endpoint filtering (if applicable)

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/backend-service.json`

---

#### Phase 3.4: Create SLO Overview Dashboard

**Description**: Create a dashboard for monitoring Service Level Objectives with error budget tracking.

**Dashboard Panels**:
1. **Availability (%)** - Successful requests / Total requests
2. **SLO Status Indicator** - Green/Yellow/Red based on target
3. **Error Budget Remaining** - Based on configurable SLO target (default 99.5%)
4. **Error Budget Burn Rate** - Rate of error budget consumption
5. **p95 Latency vs Target** - Comparison to 500ms default target
6. **p99 Latency vs Target** - Comparison to 1000ms default target
7. **SLO Compliance Over Time** - Time series of availability

**Dashboard Variables**:
- `slo_target` - Configurable availability target (default: 0.995)
- `latency_target_p95` - P95 latency target in seconds (default: 0.5)
- `latency_target_p99` - P99 latency target in seconds (default: 1.0)
- `time_window` - SLO calculation window (default: 30d)

**Acceptance Criteria**:
- [ ] Dashboard loads without errors
- [ ] Error budget calculation is mathematically correct
- [ ] SLO targets are configurable via dashboard variables
- [ ] Visual indicators (colors) correctly reflect SLO status

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/slo-overview.json`

---

#### Phase 3.5: Create Log Explorer Dashboard

**Description**: Create a dashboard for exploring and searching application logs aggregated in Loki.

**Dashboard Panels**:
1. **Log Volume** - `sum(count_over_time({container=~".+"}[1m]))`
2. **Logs by Level** - Breakdown by severity (ERROR, WARN, INFO, DEBUG)
3. **Logs by Container** - Volume by container name
4. **Error Log Stream** - Live view of ERROR level logs
5. **Log Search** - Full text search with LogQL
6. **Recent Errors Table** - Last 100 ERROR entries

**Dashboard Variables**:
- `container` - Filter by container name
- `level` - Filter by log level
- `search` - Full text search term

**Acceptance Criteria**:
- [ ] Dashboard loads without errors
- [ ] Log queries execute within performance targets
- [ ] Container and level filters work correctly
- [ ] Links to traces work (via trace_id in logs)

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/log-explorer.json`

---

#### Phase 3.6: Create Trace Explorer Dashboard

**Description**: Create a dashboard for exploring distributed traces stored in Tempo.

**Dashboard Panels**:
1. **Trace Search** - Search by service, operation, duration, time range
2. **Trace Duration Distribution** - Histogram of trace durations
3. **Service Dependency Graph** - Visual representation of service calls (if multiple services)
4. **Recent Traces Table** - Last 50 traces with duration, status
5. **Slow Traces** - Traces exceeding p95 latency threshold
6. **Failed Traces** - Traces with error status

**Dashboard Variables**:
- `service` - Filter by service name
- `operation` - Filter by operation/endpoint
- `min_duration` - Minimum duration filter
- `status` - Success/Error filter

**Acceptance Criteria**:
- [ ] Dashboard loads without errors
- [ ] Trace search returns results
- [ ] Clicking trace ID opens trace detail view
- [ ] Links to related logs work

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/trace-explorer.json`

---

#### Phase 3 Completion Criteria

**Integration Test**:
1. Generate a project with `include_observability: yes`
2. Run `docker compose up -d`
3. Generate traffic to backend (`for i in {1..100}; do curl http://localhost:8000/api/v1/health; done`)
4. Access Grafana at `localhost:3000`
5. Verify all 4 dashboards appear in dashboard list
6. Verify Backend Service Dashboard shows live metrics
7. Verify trace-to-logs correlation works (click trace -> see logs)
8. Verify logs-to-trace correlation works (click trace_id in log -> see trace)

**Rollback Plan**: If Phase 3 fails, remove dashboard files. Phase 1 infrastructure and Phase 2 instrumentation remain functional; Grafana will simply have no pre-built dashboards.

**Traceability**: FR-VZ-001 through FR-VZ-007, FR-DC-001 through FR-DC-004, UX-001 through UX-022, NFR-PF-006, NFR-OP-001

---

### Phase 4: Template Conditionals

**Objective**: Implement the `include_observability` cookiecutter variable and ensure all observability components are conditionally generated based on user preference.

#### Phase 4.1: Update cookiecutter.json

**Description**: Add the `include_observability` variable to the cookiecutter configuration.

**Tasks**:
1. Add `include_observability` with default value "yes"
2. Add variable description for cookiecutter prompts
3. Ensure variable is positioned logically in the prompt sequence

**Configuration Addition**:
```json
{
  "project_name": "My Project",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-') }}",
  // ... existing variables ...
  "include_observability": ["yes", "no"],
  "_include_observability_help": "Include observability stack (Prometheus, Grafana, Loki, Tempo) for metrics, logging, and tracing?"
}
```

**Source Reference**: Existing `template/cookiecutter.json` (to be updated)

**Acceptance Criteria**:
- [ ] Variable added with correct default
- [ ] Prompt appears during `cookiecutter` execution
- [ ] Both "yes" and "no" options work correctly

**Deliverables**:
- Updated `template/cookiecutter.json`

---

#### Phase 4.2: Add Conditional Directory Generation

**Description**: Configure cookiecutter to skip the `observability/` directory when observability is disabled.

**Tasks**:
1. Update `hooks/post_gen_project.py` (or create if needed)
2. Remove `observability/` directory when `include_observability == "no"`
3. Ensure clean removal without errors

**Post-Generation Hook**:
```python
# hooks/post_gen_project.py
import os
import shutil

include_observability = "{{ cookiecutter.include_observability }}"

if include_observability.lower() == "no":
    # Remove observability directory
    observability_dir = os.path.join(os.getcwd(), "observability")
    if os.path.exists(observability_dir):
        shutil.rmtree(observability_dir)
    print("Observability stack disabled - removed observability/ directory")
```

**Acceptance Criteria**:
- [ ] `observability/` directory exists when `include_observability: yes`
- [ ] `observability/` directory absent when `include_observability: no`
- [ ] No errors during project generation in either case

**Deliverables**:
- `template/hooks/post_gen_project.py` (new or updated)

---

#### Phase 4.3: Verify All Jinja2 Conditionals

**Description**: Audit all template files to ensure Jinja2 conditionals are correctly placed.

**Tasks**:
1. Review `compose.yml` for proper conditional blocks
2. Review `pyproject.toml` for conditional dependencies
3. Review `main.py` for conditional imports and setup
4. Review `README.md` for conditional documentation sections
5. Review `.env.example` for conditional environment variables

**Conditional Checklist**:

| File | Conditional Content |
|------|---------------------|
| `compose.yml` | Observability services, volumes, backend environment variables |
| `pyproject.toml` | OpenTelemetry and prometheus-client dependencies |
| `backend/app/main.py` | Import and `setup_observability()` call |
| `README.md` | Observability section in documentation |
| `.env.example` | `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT` |

**Acceptance Criteria**:
- [ ] All conditionals use consistent syntax: `{% if cookiecutter.include_observability == "yes" %}`
- [ ] No orphaned conditional blocks
- [ ] Template renders without Jinja2 errors in both modes

**Deliverables**:
- Verified and corrected template files

---

#### Phase 4.4: Conditional Backend File Generation

**Description**: Ensure `observability.py` is only generated when observability is enabled.

**Tasks**:
1. Update post-generation hook to remove `observability.py` when disabled
2. Or, use conditional directory naming (advanced cookiecutter feature)

**Implementation Option 1** (Post-gen hook):
```python
# In hooks/post_gen_project.py
if include_observability.lower() == "no":
    # Remove observability.py
    obs_file = os.path.join(os.getcwd(), "backend", "app", "observability.py")
    if os.path.exists(obs_file):
        os.remove(obs_file)
```

**Implementation Option 2** (Jinja2 conditional file):
```
# Use cookiecutter extension for conditional files
# File: template/{{cookiecutter.project_slug}}/backend/app/{% if cookiecutter.include_observability == 'yes' %}observability.py{% endif %}
```

**Acceptance Criteria**:
- [ ] `observability.py` exists when `include_observability: yes`
- [ ] `observability.py` absent when `include_observability: no`
- [ ] No import errors in `main.py` when `observability.py` is absent

**Deliverables**:
- Updated post-generation hook or conditional file template

---

#### Phase 4 Completion Criteria

**Integration Test - Observability Enabled**:
1. Run `cookiecutter . --no-input include_observability=yes`
2. Verify `observability/` directory exists with all config files
3. Verify `compose.yml` contains observability services
4. Verify `backend/app/observability.py` exists
5. Verify `pyproject.toml` contains observability dependencies
6. Run `docker compose up -d` and verify all services start

**Integration Test - Observability Disabled**:
1. Run `cookiecutter . --no-input include_observability=no`
2. Verify `observability/` directory does NOT exist
3. Verify `compose.yml` does NOT contain observability services
4. Verify `backend/app/observability.py` does NOT exist
5. Verify `pyproject.toml` does NOT contain observability dependencies
6. Run `docker compose up -d` and verify core services start without errors

**Rollback Plan**: If conditionals cause issues, revert to always-included observability as fallback.

**Traceability**: FR-TC-001, FR-TC-002, FR-TC-003, G4

---

### Phase 5: Documentation & Testing

**Objective**: Complete the integration with comprehensive documentation and a robust test suite to ensure quality and maintainability.

#### Phase 5.1: Update Main README

**Description**: Add observability documentation to the main project README.

**Tasks**:
1. Add "Observability" section to README template
2. Document stack components and their purposes
3. Provide quick-start guide for accessing dashboards
4. Include port reference table
5. Add conditional rendering for observability content

**README Section Content**:
```markdown
{% if cookiecutter.include_observability == "yes" %}
## Observability

This project includes a complete observability stack for monitoring, logging, and tracing.

### Components

| Service | Port | Purpose | URL |
|---------|------|---------|-----|
| Grafana | 3000 | Visualization & Dashboards | http://localhost:3000 |
| Prometheus | 9090 | Metrics Collection | http://localhost:9090 |
| Loki | 3100 | Log Aggregation | (accessed via Grafana) |
| Tempo | 3200, 4317, 4318 | Distributed Tracing | (accessed via Grafana) |

### Quick Start

1. Start the stack: `docker compose up -d`
2. Open Grafana: http://localhost:3000 (no login required in development)
3. Navigate to Dashboards > {{ cookiecutter.project_name }}
4. View the Backend Service Dashboard for real-time metrics

### Pre-built Dashboards

- **Backend Service**: Request rate, latency, error rate (RED metrics)
- **SLO Overview**: Service level objectives and error budgets
- **Log Explorer**: Search and filter application logs
- **Trace Explorer**: View distributed traces and request flows

### Adding Custom Metrics

See `backend/app/observability.py` for examples of adding custom Prometheus metrics.

### Production Considerations

The default configuration is optimized for development. For production:
- Enable Grafana authentication (`GF_AUTH_ANONYMOUS_ENABLED=false`)
- Configure external storage for Prometheus, Loki, and Tempo
- Set up alerting with Alertmanager
- Review data retention policies
{% endif %}
```

**Acceptance Criteria**:
- [ ] README section renders correctly when observability enabled
- [ ] README section absent when observability disabled
- [ ] All URLs and ports are accurate
- [ ] Quick-start guide is followable in < 5 minutes

**Deliverables**:
- Updated `template/{{cookiecutter.project_slug}}/README.md`

---

#### Phase 5.2: Create Observability Directory README

**Description**: Create detailed documentation in the observability directory.

**Tasks**:
1. Document directory structure and purpose of each file
2. Explain configuration customization options
3. Provide troubleshooting guide
4. Include production hardening recommendations

**Content Outline**:
```markdown
# Observability Stack

## Directory Structure
## Configuration Files
## Customization Guide
## Troubleshooting
## Production Recommendations
## Additional Resources
```

**Acceptance Criteria**:
- [ ] All configuration files documented
- [ ] Customization options explained
- [ ] Troubleshooting covers common issues
- [ ] Production recommendations included

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/observability/README.md` (expanded)

---

#### Phase 5.3: Create Template Generation Tests

**Description**: Create pytest tests to verify template generation in both observability modes.

**Test Cases**:
```python
# tests/test_template_generation.py

def test_generate_with_observability_enabled():
    """Test project generation with observability enabled."""
    # Generate project with include_observability=yes
    # Assert observability/ directory exists
    # Assert compose.yml contains observability services
    # Assert backend/app/observability.py exists
    # Assert pyproject.toml contains observability dependencies

def test_generate_without_observability():
    """Test project generation with observability disabled."""
    # Generate project with include_observability=no
    # Assert observability/ directory does NOT exist
    # Assert compose.yml does NOT contain observability services
    # Assert backend/app/observability.py does NOT exist
    # Assert pyproject.toml does NOT contain observability dependencies

def test_compose_yml_syntax_with_observability():
    """Test that generated compose.yml is valid YAML."""
    # Generate project
    # Parse compose.yml with pyyaml
    # Assert no parsing errors

def test_observability_services_start():
    """Integration test: verify observability services start successfully."""
    # Generate project with observability
    # Run docker compose up -d
    # Wait for health checks
    # Assert all services healthy
    # Cleanup: docker compose down
```

**Source Reference**: Testing Strategy section (TG-001 through TG-004)

**Acceptance Criteria**:
- [ ] All test cases implemented
- [ ] Tests pass for both observability modes
- [ ] Tests can run in CI environment
- [ ] Test coverage meets 80% target for observability code

**Deliverables**:
- `tests/test_template_generation.py`
- `tests/test_observability_integration.py`

---

#### Phase 5.4: Create Observability Unit Tests

**Description**: Create unit tests for the observability.py module.

**Test Cases**:
```python
# Generated project: backend/tests/test_observability.py

def test_setup_observability_instruments_app():
    """Test that setup_observability properly instruments FastAPI."""

def test_metrics_endpoint_returns_prometheus_format():
    """Test /metrics endpoint returns valid Prometheus format."""

def test_http_requests_counter_increments():
    """Test http_requests_total counter increments on requests."""

def test_http_duration_histogram_records():
    """Test http_request_duration_seconds records request duration."""

def test_active_requests_gauge_tracks_concurrent():
    """Test active_requests gauge tracks concurrent requests."""

def test_observability_graceful_degradation():
    """Test app functions when observability services unavailable."""
```

**Source Reference**: Testing Strategy section (UT-001 through UT-006)

**Acceptance Criteria**:
- [ ] All test cases implemented
- [ ] Tests run without external dependencies (Tempo, Prometheus)
- [ ] Tests achieve 80% coverage of observability.py
- [ ] Tests documented with clear docstrings

**Deliverables**:
- `template/{{cookiecutter.project_slug}}/backend/tests/test_observability.py`

---

#### Phase 5.5: Create Integration Tests

**Description**: Create Docker-based integration tests for the observability stack.

**Test Cases**:
```python
# tests/test_observability_integration.py

@pytest.fixture
def observability_stack():
    """Fixture to start/stop observability stack with pytest-docker."""

def test_prometheus_scrapes_backend_metrics(observability_stack):
    """Verify Prometheus successfully scrapes backend /metrics."""

def test_loki_receives_container_logs(observability_stack):
    """Verify logs appear in Loki after container activity."""

def test_tempo_receives_traces(observability_stack):
    """Verify traces appear in Tempo after HTTP requests."""

def test_grafana_datasources_configured(observability_stack):
    """Verify Grafana has all datasources configured."""

def test_grafana_dashboards_load(observability_stack):
    """Verify all 4 dashboards load without errors."""

def test_trace_to_logs_correlation(observability_stack):
    """Verify clicking trace navigates to related logs."""
```

**Source Reference**: Testing Strategy section (IT-001 through IT-006)

**Acceptance Criteria**:
- [ ] Tests use pytest-docker for Docker Compose management
- [ ] Tests verify end-to-end data flow
- [ ] Tests clean up resources after execution
- [ ] Tests can run in CI with Docker-in-Docker

**Deliverables**:
- `tests/test_observability_integration.py`
- `tests/docker-compose.test.yml` (if needed for test isolation)

---

#### Phase 5.6: CI/CD Pipeline Integration

**Description**: Add observability tests to the CI/CD pipeline.

**Tasks**:
1. Add unit test job for observability code
2. Add integration test job with Docker-in-Docker
3. Add template generation test job
4. Configure test matrix for observability enabled/disabled

**GitHub Actions Workflow**:
```yaml
# .github/workflows/test-observability.yml
name: Test Observability Integration

on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install pytest pytest-cov
      - name: Run unit tests
        run: pytest tests/test_observability_unit.py -v --cov

  template-generation:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        include_observability: [yes, no]
    steps:
      - uses: actions/checkout@v4
      - name: Generate project
        run: |
          pip install cookiecutter
          cookiecutter . --no-input include_observability=${{ matrix.include_observability }}
      - name: Validate generated project
        run: |
          # Validation commands based on matrix parameter

  integration-tests:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:dind
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: pytest tests/test_observability_integration.py -v
```

**Source Reference**: Testing Strategy section (CI/CD Integration)

**Acceptance Criteria**:
- [ ] Unit tests run on every push
- [ ] Template generation tests run for both modes
- [ ] Integration tests run with Docker-in-Docker
- [ ] CI passes for all test types

**Deliverables**:
- `.github/workflows/test-observability.yml`

---

#### Phase 5.7: Update Contributing Guide

**Description**: Add observability development guidelines to CONTRIBUTING.md.

**Tasks**:
1. Document how to add new metrics
2. Document how to add new dashboards
3. Document testing requirements for observability changes
4. Document configuration customization patterns

**Acceptance Criteria**:
- [ ] Adding custom metrics documented
- [ ] Adding dashboards documented
- [ ] Testing requirements clear
- [ ] Configuration patterns explained

**Deliverables**:
- Updated `CONTRIBUTING.md` or `docs/development.md`

---

#### Phase 5 Completion Criteria

**Documentation Review**:
- [ ] README observability section reviewed for accuracy
- [ ] Observability README is comprehensive
- [ ] All code has docstrings and comments

**Test Suite Verification**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Template generation tests pass for both modes
- [ ] CI pipeline runs successfully

**Final Checklist**:
- [ ] Generate project with observability, verify full stack works
- [ ] Generate project without observability, verify no errors
- [ ] Review all documentation for accuracy
- [ ] Verify test coverage meets requirements

**Rollback Plan**: Documentation and tests are non-destructive. Can be incrementally improved without affecting core functionality.

**Traceability**: FR-DOC-001 through FR-DOC-003, TG-001 through TG-004, UT-001 through UT-006, IT-001 through IT-006, G5

---

### Rollout Strategy

#### Pre-Release Checklist

Before releasing the observability integration:

1. **Code Review**: All phases reviewed by at least one other developer
2. **Testing**: All automated tests passing in CI
3. **Documentation**: All documentation reviewed for accuracy
4. **Performance**: Verified memory footprint < 2GB
5. **Compatibility**: Tested on Linux, macOS, Windows (WSL2)

#### Release Approach

**Option A: Feature Branch Merge (Recommended)**

1. Develop all phases in a feature branch
2. Merge to main after all phases complete and tested
3. Tag release with version bump (minor version)

**Option B: Phased Merge**

1. Merge Phase 1 (Infrastructure) first
2. Allow early adopters to test
3. Merge subsequent phases incrementally
4. Each merge includes its own tests

#### Post-Release Monitoring

1. Monitor GitHub issues for bug reports
2. Track adoption via GitHub stars/forks
3. Collect feedback from early adopters
4. Plan follow-up improvements based on feedback

---

### Phase Dependencies Graph

```
Phase 1: Infrastructure Setup
    |
    ├── Phase 2: Backend Instrumentation
    |       |
    |       └──┐
    |          |
    └── Phase 3: Visualization Layer
            |
            └──┐
               |
               v
        Phase 4: Template Conditionals
               |
               v
        Phase 5: Documentation & Testing
```

**Critical Path**: Phase 1 -> Phase 2/3 (parallel) -> Phase 4 -> Phase 5

**Parallelization Opportunities**:
- Phases 2 and 3 can proceed in parallel after Phase 1 completes
- Phase 5.1 (README) can start during Phase 4
- Phase 5.3-5.5 (tests) can be written alongside Phases 2-4

---

### Resource Requirements

| Phase | Estimated Effort | Skills Required |
|-------|------------------|-----------------|
| Phase 1 | 2-3 days | Docker, YAML, Jinja2 |
| Phase 2 | 2-3 days | Python, OpenTelemetry, FastAPI |
| Phase 3 | 2-3 days | Grafana, PromQL, LogQL |
| Phase 4 | 1-2 days | Cookiecutter, Jinja2, Python |
| Phase 5 | 2-3 days | Technical writing, pytest |
| **Total** | **9-14 days** | |

**Recommended Team Composition**:
- 1 Developer for Phases 1, 2, 4
- 1 Developer for Phase 3 (Grafana expertise helpful)
- Technical writer support for Phase 5 (or developer with documentation skills)

---

## Dependencies & Risks

This section documents the external dependencies, internal dependencies, technical risks, operational risks, and mitigation strategies for the observability stack integration. Each risk is assessed with likelihood (Low/Medium/High), impact (Low/Medium/High), and includes concrete mitigation approaches.

---

### External Dependencies

External dependencies are third-party technologies, services, or libraries required by the observability stack that are outside the project's direct control.

#### EXT-DEP-001: OpenTelemetry Python SDK

| Attribute | Details |
|-----------|---------|
| **Dependency** | `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp` |
| **Version Range** | `>=1.30.0` (API/SDK), `>=0.51b0` (instrumentation) |
| **Purpose** | Distributed tracing instrumentation for FastAPI backend |
| **Source** | [OpenTelemetry Python SDK](https://github.com/open-telemetry/opentelemetry-python) |
| **Maintenance Status** | Active - CNCF graduated project, 45% YoY increase in GitHub commits (2024) |
| **License** | Apache 2.0 |

**Risks**:
- Instrumentation packages may have breaking changes between minor versions
- Beta version notation (`0.51b0`) indicates potential API instability
- Python version compatibility must be monitored (currently supports 3.9-3.13)

**Mitigation**: Pin specific versions in `pyproject.toml`; document upgrade testing procedures; monitor [OpenTelemetry Python releases](https://github.com/open-telemetry/opentelemetry-python/releases).

---

#### EXT-DEP-002: Prometheus Client Library

| Attribute | Details |
|-----------|---------|
| **Dependency** | `prometheus-client` |
| **Version Range** | `>=0.21.1` |
| **Purpose** | Prometheus metrics exposition for `/metrics` endpoint |
| **Source** | [prometheus-client PyPI](https://pypi.org/project/prometheus-client/) |
| **Maintenance Status** | Active - core Prometheus ecosystem component |
| **License** | Apache 2.0 |

**Risks**:
- Metric registry conflicts if multiple libraries use default registry
- Memory consumption grows with metric cardinality

**Mitigation**: Use custom CollectorRegistry if integration issues arise; document cardinality guidelines for generated projects.

---

#### EXT-DEP-003: Grafana Docker Image

| Attribute | Details |
|-----------|---------|
| **Dependency** | `grafana/grafana:latest` |
| **Version Range** | Latest (recommend pinning to major version in production) |
| **Purpose** | Visualization and dashboard platform |
| **Source** | [Docker Hub - Grafana](https://hub.docker.com/r/grafana/grafana) |
| **Maintenance Status** | Active - Grafana Labs commercial backing |
| **License** | AGPL 3.0 (OSS), Enterprise License available |

**Risks**:
- `latest` tag can introduce unexpected breaking changes
- Dashboard JSON schema changes between major versions
- Datasource configuration API changes

**Mitigation**: Document production best practice of pinning to specific version (e.g., `grafana/grafana:11.0`); test dashboards against target version; version control dashboard JSON files.

---

#### EXT-DEP-004: Prometheus Docker Image

| Attribute | Details |
|-----------|---------|
| **Dependency** | `prom/prometheus:latest` |
| **Version Range** | Latest (recommend pinning in production) |
| **Purpose** | Metrics collection and storage |
| **Source** | [Docker Hub - Prometheus](https://hub.docker.com/r/prom/prometheus) |
| **Maintenance Status** | Active - CNCF graduated project |
| **License** | Apache 2.0 |

**Risks**:
- Configuration schema changes between versions
- Memory consumption scales with time series count (see RISK-003)
- Storage format changes can require data migration

**Mitigation**: Pin to specific version; configure `sample_limit` for cardinality protection; document memory sizing guidelines.

---

#### EXT-DEP-005: Loki Docker Image

| Attribute | Details |
|-----------|---------|
| **Dependency** | `grafana/loki:latest` |
| **Version Range** | Latest (recommend pinning in production) |
| **Purpose** | Log aggregation and storage |
| **Source** | [Docker Hub - Loki](https://hub.docker.com/r/grafana/loki) |
| **Maintenance Status** | Active - Grafana Labs product |
| **License** | AGPL 3.0 |

**Risks**:
- Schema changes between major versions
- Storage backend configuration differs significantly between versions
- Query performance varies based on ingestion volume

**Mitigation**: Pin to specific version; use filesystem storage for development (as implemented); document production scaling considerations.

---

#### EXT-DEP-006: Promtail Docker Image

| Attribute | Details |
|-----------|---------|
| **Dependency** | `grafana/promtail:latest` |
| **Version Range** | Should match Loki version |
| **Purpose** | Log collection from Docker containers |
| **Source** | [Docker Hub - Promtail](https://hub.docker.com/r/grafana/promtail) |
| **Maintenance Status** | Active - Grafana Labs product |
| **License** | AGPL 3.0 |

**Risks**:
- Docker socket access required (security implications - see RISK-007)
- Container discovery may fail with non-standard Docker configurations
- Version mismatch with Loki can cause ingestion issues

**Mitigation**: Pin to same version as Loki; document Docker socket risks; provide read-only socket mount where possible.

---

#### EXT-DEP-007: Tempo Docker Image

| Attribute | Details |
|-----------|---------|
| **Dependency** | `grafana/tempo:latest` |
| **Version Range** | Latest (recommend pinning in production) |
| **Purpose** | Distributed tracing backend with OTLP ingestion |
| **Source** | [Docker Hub - Tempo](https://hub.docker.com/r/grafana/tempo) |
| **Maintenance Status** | Active - Grafana Labs product |
| **License** | AGPL 3.0 |

**Risks**:
- Storage backend changes between versions
- OTLP protocol version compatibility with OpenTelemetry SDK
- Trace data volume can grow quickly without retention policies

**Mitigation**: Pin to specific version; configure retention policies; validate OTLP version compatibility.

---

#### EXT-DEP-008: Cookiecutter Framework

| Attribute | Details |
|-----------|---------|
| **Dependency** | `cookiecutter` |
| **Version Range** | `>=2.6.0` |
| **Purpose** | Template generation and project scaffolding |
| **Source** | [Cookiecutter GitHub](https://github.com/cookiecutter/cookiecutter) |
| **Maintenance Status** | Active - audreyr maintained |
| **License** | BSD-3-Clause |

**Risks**:
- Jinja2 rendering behavior changes
- Post-generation hook execution environment differences (Windows vs. Unix)
- Template upgrade path not native to cookiecutter

**Mitigation**: Test template generation across platforms; document minimum cookiecutter version; recommend [cruft](https://github.com/cruft/cruft) for template update management.

---

### Internal Dependencies

Internal dependencies are components within the project ecosystem that the observability stack relies upon.

#### INT-DEP-001: Docker Compose Infrastructure

| Attribute | Details |
|-----------|---------|
| **Dependency** | Existing Docker Compose setup in template |
| **Files Affected** | `compose.yml`, `compose.override.yml` |
| **Integration Point** | Observability services added as conditional blocks |

**Risks**:
- Compose file structure changes may break observability conditionals
- Network configuration changes affect inter-service communication
- Volume naming conflicts

**Mitigation**: Ensure observability services use unique, project-prefixed container and volume names; test Compose file validity after generation.

---

#### INT-DEP-002: FastAPI Backend Application

| Attribute | Details |
|-----------|---------|
| **Dependency** | Backend application structure (`backend/app/main.py`) |
| **Files Affected** | `main.py`, new `observability.py` module |
| **Integration Point** | `setup_observability(app)` called during app initialization |

**Risks**:
- Application startup order affects observability initialization
- Middleware ordering conflicts (observability middleware should run early)
- Import conflicts if observability is disabled but referenced

**Mitigation**: Use conditional imports; ensure observability setup occurs after app creation but before route registration; document middleware ordering.

---

#### INT-DEP-003: Backend Dependencies (pyproject.toml)

| Attribute | Details |
|-----------|---------|
| **Dependency** | Python dependency management |
| **Files Affected** | `backend/pyproject.toml` |
| **Integration Point** | Observability packages added conditionally |

**Risks**:
- Dependency conflicts with existing packages
- OpenTelemetry packages have many transitive dependencies
- Version resolution conflicts with other instrumentation packages

**Mitigation**: Test dependency resolution in clean environment; document known conflicts; use `uv` for faster, more reliable dependency resolution.

---

#### INT-DEP-004: Backend Health Check Endpoint

| Attribute | Details |
|-----------|---------|
| **Dependency** | Existing `/api/v1/health` endpoint |
| **Files Affected** | Health check router |
| **Integration Point** | Prometheus scrapes health check; traces include health requests |

**Risks**:
- Health check endpoints generate high-frequency metrics/traces
- Potential noise in observability data from health checks

**Mitigation**: Configure Prometheus to use longer scrape interval for health endpoints; consider excluding health endpoints from trace sampling.

---

#### INT-DEP-005: Keycloak Authentication Service

| Attribute | Details |
|-----------|---------|
| **Dependency** | Keycloak service for metrics scraping |
| **Files Affected** | Prometheus configuration (`prometheus.yml`) |
| **Integration Point** | Prometheus scrapes Keycloak metrics endpoint |

**Risks**:
- Keycloak `/metrics` endpoint may require authentication in some configurations
- Keycloak version changes may alter metrics endpoint behavior

**Mitigation**: Document Keycloak metrics configuration; test metrics scraping as part of integration tests; provide conditional Keycloak metrics scraping based on configuration.

---

### Technical Risks

Technical risks are potential issues arising from the technology choices, implementation approach, or integration complexity.

#### RISK-001: OpenTelemetry SDK Breaking Changes

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | OpenTelemetry instrumentation packages use beta versioning (e.g., `0.51b0`), indicating potential API instability. Major/minor version updates may introduce breaking changes to instrumentation APIs. |
| **Likelihood** | Medium |
| **Impact** | Medium |
| **Affected Components** | `observability.py`, tracing integration |
| **Detection** | CI/CD test failures, missing traces in Tempo |

**Mitigation Strategies**:
1. Pin specific versions in `pyproject.toml` with exact version constraints
2. Include OpenTelemetry upgrade testing in CI/CD pipeline
3. Monitor [OpenTelemetry Python changelog](https://github.com/open-telemetry/opentelemetry-python/blob/main/CHANGELOG.md)
4. Document tested version combinations in observability README
5. Use `opentelemetry-api` for instrumentation code where possible (stable API)

**Contingency**: If breaking changes occur, provide migration guide and bump template version with documented upgrade path.

---

#### RISK-002: Grafana Dashboard Compatibility

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Grafana dashboard JSON schema changes between major versions can render pre-built dashboards non-functional or display incorrectly. |
| **Likelihood** | Low |
| **Impact** | Medium |
| **Affected Components** | Pre-built dashboard JSON files, dashboard provisioning |
| **Detection** | Grafana UI errors, missing panels, broken queries |

**Mitigation Strategies**:
1. Version dashboards with schema version indicator
2. Test dashboards against minimum supported Grafana version
3. Use PromQL and LogQL syntax compatible with multiple versions
4. Document supported Grafana version range
5. Include dashboard validation in CI/CD

**Contingency**: Maintain dashboard templates for multiple Grafana major versions if significant incompatibilities arise.

---

#### RISK-003: Prometheus Memory Exhaustion (Cardinality Explosion)

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | High cardinality metrics (many unique label combinations) can cause Prometheus memory usage to grow unbounded, leading to OOM crashes and loss of observability. |
| **Likelihood** | Medium |
| **Impact** | High |
| **Affected Components** | Prometheus container, metrics collection |
| **Detection** | Prometheus container restarts, OOMKilled events, slow queries |

**Mitigation Strategies**:
1. Document label cardinality best practices in generated project README
2. Use path patterns instead of full URLs in `endpoint` label (e.g., `/api/v1/users/{id}` not `/api/v1/users/12345`)
3. Configure `sample_limit` in Prometheus scrape configs
4. Set container memory limits with appropriate headroom
5. Include cardinality monitoring query in default dashboard:
   ```promql
   topk(10, count by (__name__)({__name__=~".+"}))
   ```
6. Default to conservative metric retention (15 days for development)

**Contingency**: If memory issues occur, provide documentation on horizontal scaling with federation or migration to remote write solutions (Mimir, Thanos).

**References**: [Grafana Labs - Managing High Cardinality Metrics](https://grafana.com/blog/2022/10/20/how-to-manage-high-cardinality-metrics-in-prometheus-and-kubernetes/), [Last9 - Troubleshooting Prometheus](https://last9.io/blog/troubleshooting-common-prometheus-pitfalls-cardinality-resource-utilization-and-storage-challenges/)

---

#### RISK-004: Trace Context Propagation Failures

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Distributed traces may fail to propagate context across service boundaries (frontend to backend, backend to external services), resulting in disconnected trace spans. |
| **Likelihood** | Medium |
| **Impact** | Low |
| **Affected Components** | OpenTelemetry instrumentation, HTTP headers |
| **Detection** | Missing parent spans, orphan trace fragments |

**Mitigation Strategies**:
1. Use W3C Trace Context headers (standard propagation format)
2. Document manual context propagation for custom HTTP clients
3. Include trace context verification in integration tests
4. Log trace_id and span_id in structured logs for manual correlation

**Contingency**: Provide fallback to log-based correlation if automatic trace propagation fails.

---

#### RISK-005: Log Volume Disk Exhaustion

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Without proper retention policies, Loki storage can grow unbounded, exhausting disk space and causing log ingestion failures. |
| **Likelihood** | Medium |
| **Impact** | Medium |
| **Affected Components** | Loki storage, Promtail ingestion |
| **Detection** | Loki ingestion errors, disk space alerts |

**Mitigation Strategies**:
1. Configure Loki retention limits (default: 7 days for development)
2. Use compaction to reduce storage footprint
3. Document log volume expectations based on application activity
4. Include disk usage monitoring in default dashboard
5. Set volume size limits in Docker Compose

**Contingency**: Provide log rotation and external storage backend documentation for production deployments.

---

#### RISK-006: Template Generation Conditional Complexity

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Complex Jinja2 conditionals for observability inclusion may result in malformed generated files (YAML syntax errors, missing dependencies, broken imports). |
| **Likelihood** | Medium |
| **Impact** | High |
| **Affected Components** | Cookiecutter template, generated project files |
| **Detection** | Template generation failures, Docker Compose parsing errors |

**Mitigation Strategies**:
1. Use post-generation hooks to copy/remove files rather than inline conditionals
2. Test both `include_observability=yes` and `include_observability=no` in CI
3. Validate generated YAML files with schema validators
4. Keep conditional blocks at the file level where possible
5. Use consistent indentation in Jinja2 template blocks

**Contingency**: Provide manual installation guide if template generation issues arise.

---

#### RISK-007: Docker Socket Security Exposure (Promtail)

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Promtail requires Docker socket access (`/var/run/docker.sock`) for container discovery. This grants Promtail (and any container with socket access) root-equivalent access to the Docker host. |
| **Likelihood** | Low (in development) |
| **Impact** | Critical (if exploited) |
| **Affected Components** | Promtail container, Docker host security |
| **Detection** | Security audits, container escape attempts |

**Mitigation Strategies**:
1. Mount Docker socket as read-only (`:ro`) where possible
2. Document the security implications in observability README
3. Recommend Docker socket proxy for production deployments
4. Use user namespaces for container isolation
5. Include security warning in template generation output
6. Mark as **development-only** configuration with production alternatives documented

**Production Alternatives**:
- Use Kubernetes with proper Pod Security Standards
- Deploy Promtail as DaemonSet with restricted RBAC
- Use [docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy) to limit API access
- Consider alternative log collection (journald, file-based)

**References**: [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html), [Docker Daemon Socket Protection](https://docs.docker.com/engine/security/protect-access/)

---

#### RISK-008: OTLP Endpoint Connectivity Failures

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | If the Tempo OTLP endpoint is unreachable (Tempo not started, network issues), span export failures may cause application errors or performance degradation. |
| **Likelihood** | Medium |
| **Impact** | Low |
| **Affected Components** | OpenTelemetry exporter, application startup |
| **Detection** | Application logs showing export failures, missing traces |

**Mitigation Strategies**:
1. Use BatchSpanProcessor with retry configuration
2. Implement fail-open pattern (application continues if tracing fails)
3. Configure `OTEL_EXPORTER_OTLP_TIMEOUT` with reasonable defaults
4. Add Tempo to `depends_on` in Docker Compose
5. Include error handling in observability setup:
   ```python
   try:
       setup_observability(app)
   except Exception as e:
       logger.warning(f"Observability setup failed: {e}")
   ```

**Contingency**: Document how to disable tracing at runtime via environment variable.

---

#### RISK-009: Python Dependency Conflicts

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | OpenTelemetry packages have many transitive dependencies that may conflict with existing project dependencies (e.g., `grpcio`, `protobuf`, `certifi`). |
| **Likelihood** | Low |
| **Impact** | Medium |
| **Affected Components** | Python dependency resolution, `pyproject.toml` |
| **Detection** | `uv install` or `pip install` failures, import errors |

**Mitigation Strategies**:
1. Test dependency resolution in clean environment during CI
2. Document known version constraints for transitive dependencies
3. Use `uv` for faster, more reliable dependency resolution
4. Keep OpenTelemetry packages at compatible versions
5. Avoid unnecessary instrumentation packages

**Contingency**: Provide alternative lightweight instrumentation (metrics-only) if full OpenTelemetry stack causes conflicts.

---

### Operational Risks

Operational risks are potential issues that may arise during deployment, operation, or maintenance of the observability stack.

#### RISK-010: Resource Consumption in Development Environments

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | The full observability stack (5 containers) adds significant memory and CPU overhead, potentially exceeding available resources on developer laptops or CI environments. |
| **Likelihood** | Medium |
| **Impact** | Medium |
| **Affected Components** | All observability containers, developer experience |
| **Detection** | Slow container startup, system resource exhaustion, OOM kills |

**Resource Baseline** (from NFR-RE-001):
| Component | Memory (Min) | Memory (Recommended) |
|-----------|--------------|----------------------|
| Prometheus | 256 MB | 512 MB |
| Loki | 256 MB | 512 MB |
| Promtail | 64 MB | 128 MB |
| Tempo | 256 MB | 512 MB |
| Grafana | 256 MB | 512 MB |
| **Total** | **1,088 MB** | **2,176 MB** |

**Mitigation Strategies**:
1. Document minimum system requirements (8 GB RAM recommended with observability)
2. Provide `include_observability=no` option for resource-constrained environments
3. Set conservative resource limits in Docker Compose
4. Document how to selectively start services
5. Provide lightweight development mode (Prometheus + Grafana only)

**Contingency**: Document manual observability setup for production environments where local development is not feasible.

---

#### RISK-011: Observability Data Persistence Across Restarts

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Without proper volume configuration, observability data (metrics, logs, traces, dashboards) may be lost when containers are recreated, impacting debugging of past issues. |
| **Likelihood** | Low |
| **Impact** | Medium |
| **Affected Components** | Docker volumes, data persistence |
| **Detection** | Missing historical data after `docker compose down/up` |

**Mitigation Strategies**:
1. Use named volumes for all data directories (implemented in design)
2. Document volume lifecycle and backup procedures
3. Configure appropriate retention periods
4. Include volume initialization verification in integration tests

**Contingency**: Document data export procedures for critical observability data.

---

#### RISK-012: Grafana Anonymous Access in Production

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Default development configuration enables anonymous Grafana access with Admin role. If deployed to production without modification, this exposes sensitive operational data. |
| **Likelihood** | Medium |
| **Impact** | High |
| **Affected Components** | Grafana container, security posture |
| **Detection** | Security audit, unauthorized dashboard access |

**Mitigation Strategies**:
1. Clearly document development-only nature of default config
2. Provide production configuration template with authentication enabled
3. Add security warning in generated README
4. Include security checklist in observability documentation
5. Mark configuration with `# DEVELOPMENT ONLY - DO NOT USE IN PRODUCTION` comments

**Contingency**: Provide Keycloak integration guide for Grafana authentication in production.

---

#### RISK-013: Template Maintenance Burden

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Adding observability significantly increases template complexity and maintenance burden. Version updates to any observability component require template updates and testing. |
| **Likelihood** | High |
| **Impact** | Low |
| **Affected Components** | Template maintenance, CI/CD pipeline |
| **Detection** | Increased time for template updates, version drift |

**Mitigation Strategies**:
1. Pin specific versions with documented update schedule
2. Include version compatibility matrix in documentation
3. Automate dependency update testing with Dependabot or Renovate
4. Design for modularity (observability as optional, isolated feature)
5. Document upgrade procedures for generated projects

**Contingency**: If maintenance becomes unsustainable, consider external observability module or reference implementation link instead of embedded template.

**References**: [Cortex - Cookiecutter Benefits and Limitations](https://www.cortex.io/post/an-overview-of-cookiecutter), [Cruft for Template Updates](https://github.com/cruft/cruft)

---

#### RISK-014: CI/CD Pipeline Performance Impact

| Attribute | Assessment |
|-----------|------------|
| **Risk Description** | Integration tests requiring full observability stack add significant time and resource cost to CI/CD pipelines, potentially increasing feedback loop time and CI costs. |
| **Likelihood** | Medium |
| **Impact** | Low |
| **Affected Components** | GitHub Actions workflows, test execution time |
| **Detection** | Slow CI runs, increased CI costs |

**Mitigation Strategies**:
1. Use Docker layer caching for observability images
2. Run observability integration tests in separate job (parallelizable)
3. Consider nightly-only full integration tests
4. Use pre-pulled base images in CI
5. Implement test result caching

**Contingency**: Provide mock observability services for unit testing without full stack.

---

### Risk Summary Matrix

| Risk ID | Risk Description | Likelihood | Impact | Priority | Owner |
|---------|------------------|------------|--------|----------|-------|
| RISK-001 | OpenTelemetry SDK Breaking Changes | Medium | Medium | P2 | Development |
| RISK-002 | Grafana Dashboard Compatibility | Low | Medium | P3 | Development |
| RISK-003 | Prometheus Memory Exhaustion | Medium | High | P1 | Development + Ops |
| RISK-004 | Trace Context Propagation | Medium | Low | P3 | Development |
| RISK-005 | Log Volume Disk Exhaustion | Medium | Medium | P2 | Ops |
| RISK-006 | Template Conditional Complexity | Medium | High | P1 | Development |
| RISK-007 | Docker Socket Security | Low | Critical | P1 | Security |
| RISK-008 | OTLP Connectivity Failures | Medium | Low | P3 | Development |
| RISK-009 | Python Dependency Conflicts | Low | Medium | P3 | Development |
| RISK-010 | Resource Consumption | Medium | Medium | P2 | Development |
| RISK-011 | Data Persistence | Low | Medium | P3 | Ops |
| RISK-012 | Grafana Anonymous Access | Medium | High | P1 | Security |
| RISK-013 | Template Maintenance | High | Low | P2 | Development |
| RISK-014 | CI/CD Performance | Medium | Low | P3 | DevOps |

**Priority Legend**:
- **P1 (Critical)**: Must address before initial release
- **P2 (High)**: Should address in initial release, blocking for production use
- **P3 (Medium)**: Can address in subsequent releases

---

### Dependency Diagram

```
                     ┌─────────────────────────────────────────────────────┐
                     │              EXTERNAL DEPENDENCIES                  │
                     └─────────────────────────────────────────────────────┘
                                              │
          ┌───────────────────────────────────┼───────────────────────────────────┐
          │                                   │                                   │
          ▼                                   ▼                                   ▼
┌───────────────────┐             ┌───────────────────┐             ┌───────────────────┐
│   Python Packages │             │   Docker Images   │             │   Cookiecutter    │
├───────────────────┤             ├───────────────────┤             ├───────────────────┤
│ opentelemetry-api │             │ grafana/grafana   │             │ cookiecutter>=2.6 │
│ opentelemetry-sdk │             │ prom/prometheus   │             │ Jinja2            │
│ otel-fastapi      │             │ grafana/loki      │             │ cruft (optional)  │
│ otel-exporter-otlp│             │ grafana/promtail  │             └───────────────────┘
│ prometheus-client │             │ grafana/tempo     │
└────────┬──────────┘             └────────┬──────────┘
         │                                  │
         │      ┌───────────────────────────┘
         │      │
         ▼      ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              INTERNAL DEPENDENCIES                                      │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │ Docker Compose      │◄───│ Backend Application │◄───│ Cookiecutter Template       │ │
│  │ (compose.yml)       │    │ (main.py)           │    │ ({{project_slug}}/...)      │ │
│  │                     │    │                     │    │                             │ │
│  │ Observability       │    │ observability.py    │    │ include_observability       │ │
│  │ service definitions │    │ module              │    │ conditional                 │ │
│  └─────────┬───────────┘    └──────────┬──────────┘    └─────────────────────────────┘ │
│            │                           │                                                │
│            │                           │                                                │
│            ▼                           ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           EXISTING TEMPLATE SERVICES                            │   │
│  ├─────────────────────────────────────────────────────────────────────────────────┤   │
│  │  postgres   │    keycloak    │    redis    │    frontend    │    backend       │   │
│  │  (db)       │    (auth)      │    (cache)  │    (UI)        │    (API)         │   │
│  └─────────────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Traceability to Requirements

| Dependency/Risk | Related FRs | Related NFRs | Related Security Reqs |
|----------------|-------------|--------------|----------------------|
| EXT-DEP-001 (OpenTelemetry) | FR-DT-001 through FR-DT-006 | NFR-PF-003 | - |
| EXT-DEP-002 (prometheus-client) | FR-MC-001 through FR-MC-005 | NFR-PF-002 | - |
| EXT-DEP-003 (Grafana) | FR-VZ-001 through FR-VZ-008 | NFR-MN-001 | SEC-001 |
| EXT-DEP-004 (Prometheus) | FR-MC-001, FR-MC-002 | NFR-RE-001, NFR-SC-001 | SEC-002 |
| EXT-DEP-005 (Loki) | FR-LA-001 through FR-LA-005 | NFR-SC-002 | SEC-006, SEC-007 |
| EXT-DEP-006 (Promtail) | FR-LA-001, FR-LA-002 | - | SEC-012 |
| EXT-DEP-007 (Tempo) | FR-DT-001 through FR-DT-004 | NFR-SC-003 | SEC-003 |
| RISK-003 (Cardinality) | FR-MC-001 | NFR-RE-001 | - |
| RISK-006 (Template) | FR-TC-001 through FR-TC-003 | NFR-MN-002 | - |
| RISK-007 (Docker Socket) | FR-LA-002 | - | SEC-012 |
| RISK-012 (Grafana Auth) | FR-VZ-001 | - | SEC-001 |

---

## Open Questions

This section documents unresolved decisions, areas requiring further research, and questions that need stakeholder input before or during implementation.

### Strategic Questions

#### OQ-001: Docker Image Version Pinning Strategy ✅ RESOLVED

**Question**: Should the template pin specific Docker image versions (e.g., `grafana/grafana:11.3.0`) or use `latest` tags with version documentation?

**Context**: The Dependencies & Risks section (EXT-DEP-003 through EXT-DEP-007) recommends version pinning for production stability, but `latest` tags reduce maintenance burden and ensure security patches are applied.

**Trade-offs**:
| Approach | Pros | Cons |
|----------|------|------|
| Pin specific versions | Reproducible builds, no surprise breaking changes | Requires regular updates, security lag |
| Use `latest` | Always current, automatic security updates | Potential breaking changes, non-reproducible |
| Pin major version (e.g., `grafana/grafana:11`) | Balance of stability and updates | May miss important patches between major versions |

**Resolution**: Pin to specific versions in template with documented version compatibility matrix. Add Dependabot or Renovate configuration to automate update PRs.

---

#### OQ-002: Default Observability Inclusion ✅ RESOLVED

**Question**: Should `include_observability` default to `yes` or `no` when generating new projects?

**Context**: The observability stack adds ~2 GB RAM overhead (NFR-RE-001, RISK-010) but provides significant development value (G1-G5). Default choice affects adoption and developer experience.

**Trade-offs**:
| Default | Pros | Cons |
|---------|------|------|
| `yes` | Immediate value, observability-first culture | Resource burden on constrained systems, longer startup |
| `no` | Minimal footprint, faster startup | Developers must opt-in, may forget observability |

**Resolution**: Default to `yes` with clear documentation on disabling for resource-constrained environments.

---

#### OQ-003: Lightweight Development Mode ✅ RESOLVED

**Question**: Should the template provide a "lightweight" observability mode with only Prometheus and Grafana (no Loki/Tempo)?

**Context**: RISK-010 mitigation strategies mention providing "lightweight development mode (Prometheus + Grafana only)". This would reduce memory footprint from ~2 GB to ~1 GB.

**Trade-offs**:
| Approach | Pros | Cons |
|----------|------|------|
| Full stack only | Simpler template, consistent experience | High resource consumption |
| Full + lightweight | Flexible resource usage | More template complexity (RISK-006) |
| Lightweight only | Minimal resources | Missing distributed tracing and log aggregation |

**Resolution**: Full stack only. Simpler template with consistent experience is preferred over additional complexity for resource savings.

---

### Technical Questions

#### OQ-004: OpenTelemetry Instrumentation Version Constraints ✅ RESOLVED

**Question**: What version constraint strategy should be used for OpenTelemetry instrumentation packages that use beta versioning (e.g., `opentelemetry-instrumentation-fastapi = "^0.51b0"`)?

**Context**: RISK-001 highlights that beta-versioned packages may have API instability. The caret constraint (`^0.51b0`) allows minor version updates but could introduce breaking changes.

**Options**:
1. Exact version pin (`== 0.51b0`) - Maximum stability, requires manual updates
2. Tilde constraint (`~= 0.51b0`) - Patch updates only
3. Caret constraint (`^0.51b0`) - Minor updates allowed (current approach)

**Resolution**: Use tilde constraint (`~= 0.51b0`) for instrumentation packages, caret constraint for stable API packages.

---

#### OQ-005: Health Check Endpoint Trace Exclusion ✅ RESOLVED

**Question**: Should the `/api/v1/health` endpoint be excluded from distributed tracing to reduce noise?

**Context**: INT-DEP-004 notes that health check endpoints generate high-frequency metrics and traces that may create noise in observability data. Prometheus scrapes health checks every 15-30 seconds.

**Options**:
1. Include all endpoints (current approach) - Complete tracing, noisy data
2. Exclude `/api/v1/health` from tracing - Cleaner traces, special case logic
3. Configurable via environment variable - Flexible, additional complexity

**Resolution**: Exclude `/api/v1/health` from tracing for cleaner traces, with special case logic.

**Technical Note**: Exclusion can be implemented via span filter in OpenTelemetry:
```python
from opentelemetry.sdk.trace import SpanProcessor

class HealthCheckSpanFilter(SpanProcessor):
    def on_start(self, span, parent_context):
        if span.attributes.get("http.route") == "/api/v1/health":
            span.set_attribute("sampling.priority", 0)
```

---

#### OQ-006: Grafana Dashboard Provisioning Source ✅ RESOLVED

**Question**: Should dashboards be provisioned as embedded JSON files or fetched from a dashboard repository (e.g., Grafana marketplace, GitHub)?

**Context**: FR-VZ-003 through FR-VZ-006 define 4 pre-built dashboards. RISK-002 notes Grafana dashboard schema compatibility concerns.

**Options**:
1. Embedded JSON files (current approach) - Self-contained, versioned with template
2. Dashboard repository URLs - Always current, external dependency
3. Hybrid: Core dashboards embedded, optional dashboards from repository

**Resolution**: Embedded JSON files for reliability and offline development support.

---

#### OQ-007: Trace Sampling Strategy for High-Volume Endpoints ✅ RESOLVED

**Question**: Should the template implement trace sampling for high-volume production environments, or leave all traces unsampled (100% sampling)?

**Context**: Full trace sampling (100%) provides complete visibility but generates significant storage in high-traffic applications. This is marked as out of scope (development focus) but affects production readiness.

**Options**:
1. 100% sampling (current approach) - Complete visibility for development
2. Configurable sampling rate via `OTEL_TRACES_SAMPLER_ARG` - Production-ready
3. Parent-based sampling with configurable root sampling - Balance of visibility and cost

**Resolution**: Configurable sampling rate via `OTEL_TRACES_SAMPLER_ARG` for production-readiness.

---

### Security Questions

#### OQ-008: Docker Socket Access Alternative for Promtail ✅ RESOLVED

**Question**: Should the template provide an alternative log collection method that does not require Docker socket access?

**Context**: RISK-007 identifies Docker socket access (`/var/run/docker.sock`) as a critical security concern with root-equivalent access implications. Mitigation strategies mention alternatives but do not define a preferred approach.

**Alternatives**:
1. Docker socket with read-only mount (current approach)
2. Docker socket proxy ([docker-socket-proxy](https://github.com/Tecnativa/docker-socket-proxy))
3. File-based log collection (mount `/var/lib/docker/containers` only)
4. Journald integration (for systemd-based hosts)

**Resolution**: Docker socket approach with security documentation. The Docker socket method is simpler, works out of the box, and the security implications are acceptable for a development-focused template. Security documentation per SEC-012 addresses production considerations. Since this is an unreleased project template, we prioritize clean, straightforward implementation over complex alternatives.

---

#### OQ-009: Production Security Configuration Documentation Scope ✅ RESOLVED

**Question**: How detailed should the production security documentation be, given that production deployment configurations are explicitly out of scope (OOS-3)?

**Context**: SEC-001 through SEC-005 define production security requirements but implementation is marked as "documentation only". Users need enough guidance to secure production deployments without the FRD becoming a production deployment guide.

**Options**:
1. High-level checklist only - Points to external resources
2. Detailed configuration examples (current approach in Security section)
3. Separate production hardening guide document

**Resolution**: High-level checklist only, pointing to external resources. Production deployments will look very different than development configurations.

---

### Operational Questions

#### OQ-010: Retention Policy Defaults ✅ RESOLVED

**Question**: What should the default data retention periods be for each observability component?

**Context**: Data retention policies are documented in Data Models section but default values need stakeholder validation.

**Proposed Defaults**:
| Component | Data Type | Proposed Default | Rationale |
|-----------|-----------|------------------|-----------|
| Prometheus | Metrics | 15 days | Balanced storage vs. development debugging needs |
| Loki | Logs | 7 days | Logs can be verbose; 1 week covers typical sprint |
| Tempo | Traces | 7 days | Traces are larger; align with Loki retention |
| Grafana | Dashboards | Persistent | Configuration, not ephemeral data |

**Resolution**: Proposed retention periods are approved as-is.

---

#### OQ-011: Resource Limit Enforcement in Docker Compose ✅ RESOLVED

**Question**: Should Docker Compose service definitions include explicit resource limits (`deploy.resources.limits`)?

**Context**: RISK-010 documents resource consumption concerns. Resource limits prevent runaway containers but may cause OOM kills if set too low.

**Options**:
1. No limits (current approach) - Containers use what they need, risk of host exhaustion
2. Hard limits based on NFR-RE-001 baselines - Prevents runaway, may cause OOM kills
3. Soft limits (reservations only) - Scheduling hints without enforcement
4. Documented but commented-out limits - User can enable if needed

**Resolution**: Documented but commented-out limits - users can enable if needed.

---

#### OQ-012: CI/CD Integration Test Frequency ✅ RESOLVED

**Question**: Should full observability stack integration tests run on every PR, or only on scheduled/nightly builds?

**Context**: RISK-014 notes CI/CD performance impact. Full stack tests require Docker-in-Docker and take 3-5 minutes per run.

**Options**:
1. Every PR - Maximum confidence, slower feedback
2. Nightly only - Fast PRs, delayed failure detection
3. Hybrid: Unit tests on PR, integration tests on merge to main
4. Hybrid: Quick smoke test on PR, full suite nightly

**Resolution**: Nightly builds only. CI/CD will not be addressed in this FRD.

---

### Future Scope Questions

#### OQ-013: Frontend Observability Timeline

**Question**: When should frontend observability instrumentation (OOS-1) be prioritized?

**Context**: Frontend observability is explicitly out of scope but identified as a future feature candidate (`frontend-observability-instrumentation`). Implementation-manager contains reference implementation.

**Dependencies**:
- Backend observability must be stable first
- Frontend OpenTelemetry SDK has different versioning/stability than Python SDK
- Requires additional template complexity for JavaScript bundling

**Stakeholder Input Needed**: Product owner, frontend development team

**Suggested Timeline**: 2-3 months after initial backend observability release, based on adoption feedback.

---

#### OQ-014: Alerting Infrastructure Priority ✅ RESOLVED

**Question**: Should alerting infrastructure (OOS-2) be added as a fast-follow to this FRD or developed as a separate feature?

**Context**: Alerting is fundamental to production observability but adds significant complexity (AlertManager configuration, notification routing, on-call integration).

**Options**:
1. Include basic AlertManager in Phase 2 of this FRD
2. Develop as separate FRD after initial release
3. Provide documentation/guidance only, no template integration

**Resolution**: Separate FRD - alerting will be developed as a standalone feature after this FRD is complete.

---

#### OQ-015: Cloud-Native Observability Alternatives

**Question**: Should future iterations of this template support cloud-native observability alternatives (AWS CloudWatch, GCP Cloud Operations, Azure Monitor)?

**Context**: OOS-3 explicitly excludes cloud-native alternatives. Many production deployments use cloud provider observability services for integration with other cloud resources.

**Options**:
1. Never - Keep template cloud-agnostic with LGTM stack only
2. Provide migration documentation - How to move from LGTM to cloud services
3. Provide alternative template variants - Separate templates for AWS/GCP/Azure

**Stakeholder Input Needed**: Product owner, enterprise users

**Note**: This decision significantly impacts template architecture and maintenance burden.

---

### Open Question Summary

| ID | Category | Question Summary | Priority | Status |
|----|----------|------------------|----------|--------|
| OQ-001 | Strategic | Docker image version pinning strategy | High | ✅ Resolved |
| OQ-002 | Strategic | Default observability inclusion | Medium | ✅ Resolved |
| OQ-003 | Strategic | Lightweight development mode | Low | ✅ Resolved |
| OQ-004 | Technical | OpenTelemetry version constraints | High | ✅ Resolved |
| OQ-005 | Technical | Health check trace exclusion | Low | ✅ Resolved |
| OQ-006 | Technical | Dashboard provisioning source | Low | ✅ Resolved |
| OQ-007 | Technical | Trace sampling strategy | Low | ✅ Resolved |
| OQ-008 | Security | Docker socket alternative | Medium | ✅ Resolved |
| OQ-009 | Security | Production security doc scope | Low | ✅ Resolved |
| OQ-010 | Operational | Retention policy defaults | Medium | ✅ Resolved |
| OQ-011 | Operational | Resource limit enforcement | Medium | ✅ Resolved |
| OQ-012 | Operational | CI/CD test frequency | Medium | ✅ Resolved |
| OQ-013 | Future | Frontend observability timeline | Low | Open (out of scope) |
| OQ-014 | Future | Alerting infrastructure priority | Low | ✅ Resolved |
| OQ-015 | Future | Cloud-native alternatives | Low | Open (out of scope) |

**All blocking questions resolved.** OQ-013 and OQ-015 remain open as future scope items that do not block implementation.

---

### Resolution Process

1. **High Priority / Blocking**: Schedule decision meeting with stakeholders within 1 week of FRD approval
2. **Medium Priority**: Include in implementation kick-off discussion
3. **Low Priority**: Document decision during relevant implementation phase

**Escalation Path**: Unresolved questions after 2 weeks should be escalated to Team Leader for decision or delegation.

---

## Status

| Date | Update |
|------|--------|
| 2025-12-03 | FRD created. Problem Statement section complete. |
| 2025-12-03 | Goals & Success Criteria section complete. Defined 5 primary goals (G1-G5), quantitative metrics, timeline, and definition of done. |
| 2025-12-03 | Scope & Boundaries section complete. Defined 6 in-scope items (IS-1 through IS-6), 7 out-of-scope items (OOS-1 through OOS-7), phase boundaries, and related features. |
| 2025-12-03 | User Stories / Use Cases section complete. Defined 5 user personas (P1-P5), 12 user stories (US-001 through US-012) with acceptance criteria and Gherkin scenarios, 5 edge cases (EC-001 through EC-005), 3 user journey flows, and persona-to-story mapping table. |
| 2025-12-03 | Functional Requirements section complete. Defined 42 requirements across 8 categories (FR-TC, FR-IS, FR-BI, FR-MC, FR-LA, FR-DT, FR-VZ, FR-DC, FR-DOC, FR-ENV). 29 Must Have requirements, 13 Should Have requirements. Includes traceability matrix linking requirements to user stories, goals, and scope items. |
| 2025-12-03 | Non-Functional Requirements section complete. Defined 29 NFRs across 7 categories: Performance (6), Reliability (4), Scalability (4), Maintainability (4), Operability (4), Resource Efficiency (4), and Compatibility (5). 18 Must Have, 10 Should Have, 1 Could Have. Includes comprehensive traceability matrix and verification approach table. NFRs grounded in ADR-002 observability stack decisions and implementation-manager reference configuration. |
| 2025-12-03 | Technical Approach section complete. Defined port-and-adapt strategy from implementation-manager reference. Documented: technology stack selection rationale (Grafana LGTM stack), backend instrumentation architecture (OpenTelemetry + prometheus-client), Docker Compose integration pattern with conditional Jinja2 blocks, configuration templatization strategy for all 5 observability services, Python dependencies strategy, main.py integration pattern, Grafana dashboard strategy (4 pre-built dashboards), service startup order and dependencies, data flow architecture diagram, network configuration, error handling (fail-open pattern), testing considerations, technology version compatibility matrix, and trade-off analysis. All technical decisions are grounded in ADR-002 and reference implementation files. |
| 2025-12-03 | Architecture & Integration Considerations section complete. Documented: high-level system architecture with ASCII diagrams, component architecture (10 containers across application and observability layers), service dependency graph with startup order, comprehensive data flow architecture for metrics/logging/tracing pipelines, integration patterns (backend instrumentation, Docker Compose conditional blocks), API contracts and interfaces (Prometheus metrics endpoint format, OTLP span attributes, Grafana datasource configuration), network architecture (internal communication matrix, external port exposure), performance considerations (resource allocation guidelines, batching/buffering configuration), scalability architecture (horizontal scaling strategies, data retention), security architecture (development profile, production recommendations), failure modes and recovery procedures, template file mapping, integration with existing template components (health checks, Keycloak, Redis, PostgreSQL), and ADR-002 reference alignment. |
| 2025-12-03 | Data Models & Schema Changes section complete. Documented: zero-migration design (no PostgreSQL changes required), Prometheus metrics data model (3 metrics with label schemas: http_requests_total, http_request_duration_seconds, active_requests), cardinality considerations, OpenTelemetry trace data model (span attributes following semantic conventions, OTLP span structure), Tempo storage schema, Loki log data model (stream labels, structured log format with trace context), Grafana data model (SQLite persistence, dashboard JSON schema), datasource correlation configuration (Tempo-to-Loki and Tempo-to-Prometheus), configuration file data models, environment variable schemas, data retention policies with production recommendations, volume initialization process, and schema evolution guidelines following OpenTelemetry best practices. Defined 20 data model requirements (FR-DM-001 through FR-DM-020). |
| 2025-12-03 | UI/UX Considerations section complete. Documented: design philosophy (purpose-driven, audience-centered, zero-friction access), Grafana dashboard design standards (naming conventions, 24-column grid layout, visual hierarchy, color coding, time controls), dashboard-specific layouts for Backend Service (RED method), SLO Overview, Log Explorer, and Trace Explorer dashboards with ASCII wireframes and panel specifications, navigation and information architecture (home screen, cross-dashboard navigation), data correlation UX (trace-to-logs, trace-to-metrics, logs-to-traces with configuration examples), developer experience considerations (zero-config access, load time targets, error states), accessibility (color-blind safe, keyboard navigation), mobile/responsive considerations, and documentation requirements. Defined 22 UX requirements (UX-001 through UX-022): 10 Must Have, 10 Should Have, 2 Could Have. Research grounded in Grafana best practices documentation and industry observability UX standards. |
| 2025-12-03 | Security & Privacy Considerations section complete. Documented: security design principles (defense in depth, least privilege, fail-open, secure by default), comprehensive threat model (8 assets, 4 threat actors, 7 attack vectors with risk levels), development environment security profile (4 SEC-DEV items: anonymous Grafana, unauthenticated metrics, unencrypted OTLP, Loki auth disabled), production security requirements (SEC-001 through SEC-005: Grafana authentication, metrics endpoint protection, TLS for traces, network segmentation, secret management), privacy requirements (SEC-006 through SEC-008: PII in logs with risk categories and mitigation, PII in traces with attribute guidelines, data retention and GDPR considerations), log injection prevention (SEC-009: structured logging with CWE-117 mitigation), access control requirements (SEC-010: Grafana RBAC, SEC-011: audit logging), Docker security considerations (SEC-012: Docker socket access, SEC-013: container image security), and security testing requirements (SEC-014: documentation verification, SEC-015: automated security tests). Defined 15 security requirements: 5 Must Have, 9 Should Have, 2 Could Have, plus 4 development defaults. Research grounded in OWASP Logging Cheat Sheet, OWASP Top 10 A09:2021, Prometheus security model, and Grafana security best practices. |
| 2025-12-03 | Testing Strategy section complete. Defined comprehensive testing approach across 6 categories: Template Generation (TG-001 through TG-004), Unit Tests (UT-001 through UT-006), Integration Tests (IT-001 through IT-006), End-to-End Tests (E2E-001 through E2E-003), Performance Tests (PT-001 through PT-004), and Security Tests (ST-001 through ST-003). Total of 24 test specifications with implementation examples. Key testing tools: pytest, pytest-docker, Playwright, cookiecutter. Established test coverage requirements (80% for observability.py, 100% for template generation). CI/CD pipeline integration defined with GitHub Actions example. All tests traceable to functional requirements, NFRs, and security requirements. Research grounded in pytest-opentelemetry, opentelemetry-test-utils, and prometheus-fastapi-instrumentator best practices. |
| 2025-12-03 | Implementation Phases section complete. Defined 5 phases with detailed task breakdowns: Phase 1 (Infrastructure Setup - 7 sub-tasks for directory structure, Prometheus/Loki/Promtail/Tempo configs, Docker Compose services, observability README), Phase 2 (Backend Instrumentation - 4 sub-tasks for Python dependencies, observability.py module, main.py integration, environment variables), Phase 3 (Visualization Layer - 6 sub-tasks for Grafana datasources, dashboard provisioning, 4 pre-built dashboards), Phase 4 (Template Conditionals - 4 sub-tasks for cookiecutter.json, post-generation hooks, Jinja2 conditional verification, conditional file generation), Phase 5 (Documentation & Testing - 7 sub-tasks for README updates, observability docs, template generation tests, unit tests, integration tests, CI/CD pipeline, contributing guide). Total estimated duration: 9-14 days. Includes phase dependency graph showing Phase 2/3 can run in parallel, rollout strategy with pre-release checklist and release approaches, resource requirements, and comprehensive acceptance criteria with integration tests for each phase. All phases traceable to functional requirements (FR-IS, FR-BI, FR-VZ, FR-TC, FR-DOC) and non-functional requirements. |
| 2025-12-03 | Dependencies & Risks section complete. Documented: 8 external dependencies (EXT-DEP-001 through EXT-DEP-008) covering OpenTelemetry Python SDK, prometheus-client, Grafana/Prometheus/Loki/Promtail/Tempo Docker images, and Cookiecutter framework with version ranges, maintenance status, licenses, and specific risks. 5 internal dependencies (INT-DEP-001 through INT-DEP-005) covering Docker Compose infrastructure, FastAPI backend, Python dependencies, health check endpoint, and Keycloak authentication. 14 risks (RISK-001 through RISK-014) across technical and operational categories: OpenTelemetry SDK breaking changes, Grafana dashboard compatibility, Prometheus memory exhaustion (cardinality explosion), trace context propagation, log volume disk exhaustion, template generation conditional complexity, Docker socket security exposure, OTLP connectivity failures, Python dependency conflicts, resource consumption in development, data persistence, Grafana anonymous access in production, template maintenance burden, and CI/CD pipeline performance. Each risk assessed with likelihood, impact, mitigation strategies, and contingency plans. Includes risk summary matrix with priority levels (4 P1 Critical, 5 P2 High, 5 P3 Medium), dependency diagram showing external/internal relationships, and traceability table linking dependencies/risks to functional requirements, NFRs, and security requirements. Research grounded in OpenTelemetry production readiness guides, Grafana LGTM deployment best practices, Prometheus cardinality management, OWASP Docker Security Cheat Sheet, and cookiecutter maintenance patterns. |
| 2025-12-03 | Open Questions section complete. Documented 15 open questions (OQ-001 through OQ-015) across 5 categories: Strategic (3), Technical (4), Security (2), Operational (3), and Future Scope (3). Key blocking questions requiring resolution before implementation: OQ-001 (Docker image version pinning strategy), OQ-004 (OpenTelemetry version constraints), OQ-010 (retention policy defaults), and OQ-012 (CI/CD test frequency). Each question includes context, trade-off analysis, options/alternatives, stakeholder input needed, and recommendations. Includes summary matrix with priority and blocking status, plus resolution process with escalation path. Questions derived from risk analysis (RISK-001 through RISK-014), out-of-scope items (OOS-1 through OOS-7), and gaps identified across all FRD sections. |
| 2025-12-03 | **All blocking questions resolved.** Resolved 13 of 15 open questions: OQ-001 (pin specific versions + Dependabot/Renovate), OQ-002 (default to yes), OQ-003 (full stack only), OQ-004 (tilde constraint for beta packages), OQ-005 (exclude health endpoint from tracing), OQ-006 (embedded JSON dashboards), OQ-007 (configurable sampling via OTEL_TRACES_SAMPLER_ARG), OQ-008 (file-based log collection, no Docker socket), OQ-009 (high-level security checklist only), OQ-010 (proposed retention periods approved), OQ-011 (commented-out resource limits), OQ-012 (nightly builds, CI/CD out of scope), OQ-014 (alerting as separate FRD). OQ-013 and OQ-015 remain open as future scope items. FRD is now ready for implementation. |
| 2025-12-03 | **FRD Revision based on refinement analysis.** Key changes: (1) OQ-008 resolution changed from file-based log collection to Docker socket approach - simpler implementation that works out of box with security documentation per SEC-012; (2) Dashboard scope simplified from 4 dashboards to 1 (Backend Service Dashboard) - port what exists in source, defer SLO/Log/Trace Explorer dashboards to future work; (3) Added template precedent note - first use of `{% if %}` patterns establishes patterns for future conditional features; (4) Removed backwards compatibility concerns - this is an unreleased project, clean code prioritized over cautious migration language. |

**Current Progress**: Revised and ready for implementation - 15/15 sections complete (100%), all blocking questions resolved

**Project Context**: This is an UNRELEASED project template. No backwards compatibility required. Breaking changes for better feature support are encouraged. Clean, straightforward implementation is the priority.

**Revision Summary**:
1. **OQ-008**: Docker socket approach (not file-based) - simpler, works out of box
2. **Dashboards**: 1 dashboard (Backend Service) in initial scope, others are future work
3. **Template Conditionals**: First `{% if %}` usage - establishes precedent for future features
4. **Compatibility**: Removed cautious language - unreleased project enables clean implementation

**Next Steps**:
1. Begin implementation (all decisions made, scope clarified)
2. Start with Phase 1: Infrastructure Setup

**Summary**: This FRD is complete and revised with simplified scope:
- 5 primary goals with quantitative success metrics
- 6 in-scope items (IS-4 simplified to 1 dashboard) and 7 out-of-scope items
- 5 user personas and 12 user stories with acceptance criteria
- 42 functional requirements (FR-VZ-004 through FR-VZ-006 deferred to future work)
- 29 non-functional requirements across 7 categories
- 22 UX requirements
- 15 security requirements plus 4 development defaults
- 24 test specifications
- 5 implementation phases with streamlined sub-tasks
- 8 external dependencies and 5 internal dependencies
- 14 identified risks with mitigation strategies (key risks addressed in revision)

**Estimated Implementation Effort**: 7-10 days (reduced from 9-14 days due to simplified dashboard scope)

**Critical Path Items**:
1. Phase 1: Infrastructure Setup (2-3 days)
2. Phase 2/3: Backend + Visualization (parallel, 2-3 days)
3. Phase 4: Template Conditionals (1-2 days)
4. Phase 5: Documentation & Testing (2-3 days)

---

## Implementation Analysis: Backend Support

*Added by FRD Refinement Agent - 2025-12-03*

### Current State

**Relevant Files:**
- `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/app/main.py` - FastAPI application entry point
- `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/pyproject.toml` - Python dependencies
- `/home/ty/workspace/project-starter/implementation-manager/backend/observability.py` - Reference implementation (104 lines)

**Existing Patterns:**
- FastAPI app structured with lifespan context manager for startup/shutdown
- Middleware registration pattern established (CORS first, then TenantResolutionMiddleware)
- Router registration uses `app.include_router()` pattern
- Exception handlers configured for HTTP, validation, and general exceptions
- Settings managed via `app.core.config.settings` (pydantic-settings)

**Current Capabilities:**
- Health check endpoint exists at `/api/v1/health`
- Standard Python logging (no structured format)
- No metrics collection
- No distributed tracing
- No observability module

### Needed Work

- [ ] Create `backend/app/observability.py` template file (Complexity: Low)
  - Port from implementation-manager reference (104 lines)
  - Module includes: OpenTelemetry tracing, Prometheus metrics, FastAPI instrumentation, /metrics endpoint
  - Add Jinja2 conditional wrapper: `{% if cookiecutter.include_observability == "yes" %}`
  - Dependencies: None (self-contained module)

- [ ] Update `backend/app/main.py` template (Complexity: Low)
  - Add conditional import: `{% if cookiecutter.include_observability == "yes" %}from app.observability import setup_observability{% endif %}`
  - Add setup call after app creation, before middleware: `{% if cookiecutter.include_observability == "yes" %}setup_observability(app){% endif %}`
  - Location: After FastAPI() instantiation (line ~45), before CORS middleware (line ~59)

- [ ] Update `backend/pyproject.toml` template (Complexity: Low)
  - Add conditional dependencies block for OpenTelemetry packages:
    - `opentelemetry-api>=1.27.0,<2.0.0`
    - `opentelemetry-sdk>=1.27.0,<2.0.0`
    - `opentelemetry-exporter-otlp-proto-grpc>=1.27.0,<2.0.0`
    - `opentelemetry-instrumentation-fastapi~=0.48b0`
    - `prometheus-client>=0.20.0,<1.0.0`

- [ ] Implement health check trace exclusion per OQ-005 resolution (Complexity: Medium)
  - Add SpanProcessor filter to exclude `/api/v1/health` from tracing
  - Reduces noise from frequent health check probes

### Recommended Approach

Port `observability.py` as-is with minimal templating. The source module is well-structured, follows best practices, and meets all FR-BI requirements. Key characteristics:
- Test mode detection via `TESTING` environment variable
- Fail-open pattern: application continues if Tempo unavailable
- Configurable via standard OTEL environment variables (`OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`)

---

## Implementation Analysis: Docker Compose Integration

*Added by FRD Refinement Agent - 2025-12-03*

### Current State

**Relevant Files:**
- `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/compose.yml` - Template Docker Compose (183 lines)
- `/home/ty/workspace/project-starter/implementation-manager/docker-compose.yml` - Reference with observability (170 lines)

**Existing Patterns:**
- Services use `{{ cookiecutter.project_slug }}-*` container naming
- All services on `{{ cookiecutter.project_slug }}-network` bridge network
- Volumes named `{{ cookiecutter.project_slug }}-*-data`
- Restart policy: `unless-stopped` consistently applied
- Health checks configured for postgres, keycloak, backend, redis

**Current Capabilities:**
- 5 services: postgres, keycloak, backend, frontend, redis
- 4 volumes: postgres_data, redis_data, backend_cache, keycloak_data
- Backend environment variables include DATABASE_URL, REDIS_URL, API_V1_PREFIX
- Backend does NOT have OTEL_* environment variables

### Needed Work

- [ ] Add 5 observability services to `compose.yml` (Complexity: Medium)
  - prometheus, loki, promtail, tempo, grafana
  - Wrap in `{% if cookiecutter.include_observability == "yes" %}` block
  - Use source docker-compose.yml lines 91-160 as reference
  - Apply template variables for container names and ports

- [ ] Add 4 observability volumes (Complexity: Low)
  - prometheus-data, loki-data, tempo-data, grafana-data
  - Conditional on include_observability

- [ ] Add OTEL environment variables to backend service (Complexity: Low)
  - `OTEL_SERVICE_NAME: backend`
  - `OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317`
  - Conditional block within backend service environment

- [ ] Add observability service port mappings (Complexity: Low)
  - Use cookiecutter variables: `{{ cookiecutter.grafana_port }}:3000`, etc.

### Key Integration Patterns

**Service Dependencies:**
```
promtail -> loki
grafana -> prometheus, loki, tempo
backend (NO dependency on observability - fail-open pattern)
```

**Network Communication:**
- Prometheus scrapes `backend:8000/metrics`
- Backend exports traces to `tempo:4317` (gRPC)
- Promtail pushes logs to `loki:3100`
- Grafana queries all three backends on internal network

---

## Implementation Analysis: Infrastructure and Template Conditionals

*Added by FRD Refinement Agent - 2025-12-03*

### Current State

**Relevant Files:**
- `/home/ty/workspace/project-starter/template/cookiecutter.json` - Template configuration (63 lines)
- `/home/ty/workspace/project-starter/hooks/post_gen_project.py` - Post-generation hook (200 lines)
- `/home/ty/workspace/project-starter/implementation-manager/observability/` - Source directory structure

**Existing Patterns:**
- cookiecutter.json uses standard JSON with Jinja2 expressions for derived values
- `_copy_without_render` excludes certain file patterns from Jinja2 processing
- Post-gen hook handles: script permissions, .env creation, uv.lock, git init
- Template uses `{{ cookiecutter.variable }}` substitution throughout

**Current Capabilities:**
- No `include_observability` variable
- No observability port variables
- No observability/ directory in template
- No conditional file/directory rendering implemented

### Needed Work

- [ ] Add variables to `cookiecutter.json` (Complexity: Low)
  ```json
  "include_observability": "yes",
  "grafana_port": "3000",
  "prometheus_port": "9090",
  "loki_port": "3100",
  "tempo_http_port": "3200",
  "tempo_otlp_grpc_port": "4317",
  "tempo_otlp_http_port": "4318"
  ```

- [ ] Create `observability/` directory structure in template (Complexity: Medium)
  - Copy from implementation-manager/observability/
  - Templatize `prometheus.yml` cluster label: `{{ cookiecutter.project_slug }}`
  - Include all config files and README.md

- [ ] Update `hooks/post_gen_project.py` for conditional removal (Complexity: Low)
  - Add section to remove `observability/` directory when `include_observability == "no"`
  - Add section to remove `backend/app/observability.py` when disabled
  - Update "Next Steps" output to include observability URLs when enabled

- [ ] Add conditional sections to documentation files (Complexity: Low)
  - `README.md`: Add Observability section with service URLs
  - `.env.example`: Add Observability configuration section
  - `CLAUDE.md`: Add observability to service ports table

### Recommended Approach

Use hybrid conditional rendering:
1. **Jinja2 conditionals** in `compose.yml`, `main.py`, `pyproject.toml` for inline content
2. **Post-generation hook** for observability/ directory and observability.py file removal

This approach is cleaner than having the entire observability directory wrapped in Jinja2 conditionals.

---

## Implementation Analysis: Complexity Assessment

*Added by FRD Refinement Agent - 2025-12-03*

### Overall Complexity: Medium

| Component | Complexity | Effort Estimate | Risk Level |
|-----------|------------|-----------------|------------|
| Backend observability.py | Low | 0.5 days | Low |
| Backend main.py integration | Low | 0.25 days | Low |
| Python dependencies | Low | 0.25 days | Low |
| Docker Compose services | Medium | 1 day | Medium |
| Configuration files | Medium | 1 day | Low |
| cookiecutter.json | Low | 0.25 days | Low |
| Post-generation hook | Low | 0.5 days | Low |
| Dashboard (1 - Backend Service, ported) | Low | 0.5 days | Low |
| Documentation updates | Low | 0.5 days | Low |
| Testing | Medium | 1-2 days | Low |

**Total Estimated Effort**: 6-8 days (reduced from original estimate due to simplified dashboard scope - porting 1 existing dashboard vs creating 4 new ones)

### Critical Path

1. Phase 1: cookiecutter.json + observability directory structure
2. Phase 2: Backend instrumentation (observability.py, main.py, pyproject.toml)
3. Phase 3: Docker Compose integration
4. Phase 4: Post-generation hook
5. Phase 5: Documentation and testing

Phases 2 and 3 can run in parallel after Phase 1 completes.

### Identified Risks (Addressed in Revision)

1. **Dashboard Scope** - RESOLVED: Simplified to 1 dashboard (Backend Service Dashboard) which exists in source. Additional dashboards (SLO, Log Explorer, Trace Explorer) deferred to future work.

2. **Log Collection Approach** - RESOLVED: Using Docker socket approach per OQ-008 revision. Simpler implementation that works out of the box with security documentation per SEC-012.

3. **Conditional Rendering Precedent** - ACKNOWLEDGED: This is the first use of `{% if %}` patterns in the template. Implementation will establish patterns for future conditional features. Documented in IS-3 with guidance for clean, well-documented conditionals.

---

## Codebase Alignment Status

*Added by FRD Refinement Agent - 2025-12-03*

**Status: Codebase Aligned and Ready for Task Breakdown**

The FRD has been validated against the current codebase. Key findings:

1. **Source Implementation Exists**: Complete observability stack in `implementation-manager/` serves as proven reference
2. **Target Structure Compatible**: Template structure supports all required integrations
3. **Clean Implementation Path**: This is an unreleased project - no backwards compatibility concerns, enabling straightforward clean code implementation
4. **Dependencies Identified**: All external dependencies (OTEL, prometheus-client) are stable and well-documented
5. **All Blocking Questions Resolved**: OQ-001 through OQ-012 and OQ-014 resolved; remaining questions (OQ-013, OQ-015) are future scope

**Revisions Applied:**
1. OQ-008 resolution: Changed to Docker socket approach (simpler, works out of box) with security documentation
2. Dashboard scope: Simplified to 1 dashboard (Backend Service) - port what exists, defer others to future work
3. Template conditionals: First use of `{% if %}` patterns - establishes precedent for future features

**Ready for Implementation**: This FRD is ready for task breakdown and implementation planning
