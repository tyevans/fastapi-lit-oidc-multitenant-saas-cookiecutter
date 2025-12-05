# P1-07: Create Observability README

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P1-07 |
| **Title** | Create Observability README |
| **Domain** | DevOps |
| **Complexity** | XS (< 4 hours) |
| **Dependencies** | P1-06 |
| **Blocks** | None (end of Phase 1) |

---

## Scope

### Included
- Document all observability stack components
- List service URLs and ports
- Provide quick-start usage instructions
- Document configuration files
- Add troubleshooting section
- Include security notes for production

### Excluded
- Detailed Prometheus query examples (covered in dashboard docs)
- Custom metrics documentation (P5-01)
- Full production deployment guide (out of scope)

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/README.md`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/README.md`

---

## Implementation Details

### README Structure

```markdown
# Observability Stack

This directory contains the configuration for the complete observability stack including metrics, logs, and distributed tracing.

## Components

### 1. Grafana (Port 3000)
- **URL**: http://localhost:3000
- **Features**:
  - Unified visualization platform
  - Pre-configured datasources (Prometheus, Loki, Tempo)
  - Backend Service Dashboard
  - Anonymous access enabled for development

### 2. Prometheus (Port 9090)
- **URL**: http://localhost:9090
- **Features**:
  - Metrics collection and storage
  - Scrapes metrics from backend, Keycloak, and observability services
  - 15-second scrape interval (5s for backend)

### 3. Loki (Port 3100)
- **URL**: http://localhost:3100
- **Features**:
  - Log aggregation and storage
  - Efficient log querying with LogQL
  - Integrated with Grafana for log visualization

### 4. Promtail
- **Features**:
  - Log collection from Docker containers
  - Automatic container discovery via Docker socket
  - Ships logs to Loki

### 5. Tempo (Ports 3200, 4317, 4318)
- **URL**: http://localhost:3200
- **OTLP gRPC**: Port 4317
- **OTLP HTTP**: Port 4318
- **Features**:
  - Distributed tracing backend
  - OTLP protocol support
  - Trace correlation with logs and metrics

## Backend Instrumentation

The backend (FastAPI) is instrumented with:

### Metrics
- HTTP request count by method, endpoint, and status
- Request duration histograms (p50, p95, p99)
- Active request gauge
- Available at: http://localhost:8000/metrics

### Tracing
- Automatic FastAPI request tracing via OpenTelemetry
- Custom span creation support
- Trace propagation to downstream services
- Exports to Tempo via OTLP gRPC

### Logging
- Structured logging with trace context
- Automatic trace_id and span_id injection
- Log levels: DEBUG, INFO, WARNING, ERROR

## Usage

### Starting the Stack

```bash
docker compose up -d
```

### Accessing Services

1. **Grafana Dashboard**: http://localhost:3000
   - Navigate to dashboards to see backend metrics
   - Use "Explore" to query logs from Loki
   - Use "Explore" with Tempo to view traces

2. **Prometheus**: http://localhost:9090
   - Query metrics directly
   - View scrape targets status

3. **Backend Metrics**: http://localhost:8000/metrics
   - Prometheus format metrics endpoint

### Viewing Logs

In Grafana:
1. Go to Explore
2. Select "Loki" datasource
3. Use LogQL queries:
   ```
   {service="backend"}
   {container="{{ cookiecutter.project_slug }}-keycloak"}
   {stream="stderr"}
   ```

### Viewing Traces

In Grafana:
1. Go to Explore
2. Select "Tempo" datasource
3. Search by trace ID or use trace search
4. Click on a trace to see the flame graph
5. Jump to logs from traces using the "Logs for this span" button

### Viewing Metrics

In Grafana:
1. Go to Dashboards
2. Open "Backend Service Dashboard"
3. Or create custom queries in Explore with Prometheus datasource

Example Prometheus queries:
```promql
# Request rate
rate(http_requests_total{job="backend"}[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="backend"}[5m]))

# Error rate
rate(http_requests_total{job="backend",status=~"5.."}[5m])
```

## Configuration Files

| File | Purpose |
|------|---------|
| `prometheus/prometheus.yml` | Prometheus scrape configuration |
| `loki/loki-config.yml` | Loki storage and retention settings |
| `promtail/promtail-config.yml` | Docker log collection configuration |
| `tempo/tempo.yml` | Tracing backend configuration |
| `grafana/datasources/` | Pre-configured datasource connections |
| `grafana/dashboards/` | Pre-built dashboard definitions |

## Data Retention

Current configuration (development):
- **Prometheus**: Data retained based on storage capacity
- **Loki**: Retention based on schema configuration
- **Tempo**: 1-hour block retention

For production, adjust retention policies in the respective configuration files.

## Troubleshooting

### Logs not appearing in Loki
- Check Promtail is running: `docker compose ps promtail`
- Check Promtail logs: `docker compose logs promtail`
- Verify Docker socket is accessible

### Traces not appearing in Tempo
- Verify OTEL_EXPORTER_OTLP_ENDPOINT is set correctly
- Check network connectivity between services
- Review Tempo logs: `docker compose logs tempo`

### Metrics not being scraped
- Check Prometheus targets: http://localhost:9090/targets
- Verify service is exposing /metrics endpoint
- Review Prometheus logs: `docker compose logs prometheus`

## Security Notes

**Development Configuration**: The current setup has authentication disabled for ease of development. For production:

1. Enable Grafana authentication
2. Add authentication to Prometheus
3. Secure Loki and Tempo with proper authentication
4. Use TLS for all communications
5. Implement proper network segmentation
```

---

## Success Criteria

- [ ] README documents all 5 observability services
- [ ] Ports and URLs clearly listed
- [ ] Quick-start instructions provided
- [ ] Configuration files section included
- [ ] Troubleshooting section covers common issues
- [ ] Security notes warn about production requirements
- [ ] Project slug is templatized where appropriate
- [ ] Cross-references main project documentation

---

## Integration Points

### Upstream
- **P1-06**: compose.yml defines the service ports to document

### Related Documentation
- **P5-01**: Main project README will link to this document
- **P5-02**: CLAUDE.md will reference observability commands

---

## Monitoring/Observability

Not applicable for this task (documentation).

---

## Infrastructure Needs

None - documentation only.

---

## Estimated Effort

**Time**: 2-3 hours

Includes:
- Adapting source README
- Templatizing project-specific values
- Reviewing for completeness
- Adding troubleshooting scenarios
