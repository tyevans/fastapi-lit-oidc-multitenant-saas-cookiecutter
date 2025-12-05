# P3-01: Create Grafana Datasources Configuration

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P3-01 |
| **Title** | Create Grafana Datasources Configuration |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P1-06 |
| **Blocks** | P3-02 |

---

## Scope

### Included
- Create datasources.yml for Grafana provisioning
- Configure Prometheus, Loki, and Tempo datasources
- Set up trace-to-logs correlation (Tempo -> Loki)
- Set up trace-to-metrics correlation (Tempo -> Prometheus)
- Configure service map visualization
- Add inline documentation

### Excluded
- Custom datasource configurations (user responsibility)
- Additional datasources (CloudWatch, etc.)
- Datasource authentication (development mode)

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/grafana/datasources/datasources.yml`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/grafana/datasources/datasources.yml`

---

## Implementation Details

### Datasource Configuration Structure

```yaml
# Grafana datasource provisioning for {{ cookiecutter.project_name }}
# Pre-configured connections to Prometheus, Loki, and Tempo

apiVersion: 1

datasources:
  # ==========================================================================
  # Prometheus - Metrics
  # ==========================================================================
  - name: Prometheus
    uid: prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      httpMethod: POST
      manageAlerts: false
      prometheusType: Prometheus

  # ==========================================================================
  # Loki - Logs
  # ==========================================================================
  - name: Loki
    uid: loki
    type: loki
    access: proxy
    url: http://loki:3100
    editable: true
    jsonData:
      maxLines: 1000

  # ==========================================================================
  # Tempo - Traces
  # ==========================================================================
  - name: Tempo
    uid: tempo
    type: tempo
    access: proxy
    url: http://tempo:3200
    editable: true
    jsonData:
      # Trace to Logs correlation
      # Click "Logs for this span" to jump to related logs in Loki
      tracesToLogsV2:
        datasourceUid: 'loki'
        spanStartTimeShift: '-1h'
        spanEndTimeShift: '1h'
        filterByTraceID: true
        filterBySpanID: false
        customQuery: false

      # Trace to Metrics correlation
      # Links traces to Prometheus metrics
      tracesToMetrics:
        datasourceUid: 'prometheus'
        spanStartTimeShift: '-1h'
        spanEndTimeShift: '1h'
        tags:
          - key: 'service.name'
            value: 'service'

      # Service Map (Node Graph)
      # Visual representation of service dependencies
      serviceMap:
        datasourceUid: 'prometheus'

      # Enable node graph visualization
      nodeGraph:
        enabled: true

      # Trace search configuration
      search:
        hide: false

      # Lokiのstream selector for trace-log correlation
      lokiSearch:
        datasourceUid: 'loki'
```

### Key Configuration Points

1. **Datasource UIDs**
   - Must be consistent for cross-datasource references
   - Used by Tempo for tracesToLogsV2 and tracesToMetrics

2. **Prometheus as Default**
   - `isDefault: true` makes Prometheus the default for new panels

3. **Trace Correlations**
   - `tracesToLogsV2`: Links from trace spans to Loki logs
   - `tracesToMetrics`: Links from traces to Prometheus metrics
   - Time shift of +/- 1 hour captures related data

4. **Service Map**
   - Uses Prometheus metrics for service graph data
   - Node graph visualization enabled

### Datasource UID Requirements

UIDs are referenced by:
- Dashboard JSON files (P3-03)
- Tempo correlation configuration
- Grafana Explore saved queries

| Datasource | UID | Referenced By |
|------------|-----|---------------|
| Prometheus | `prometheus` | Tempo (tracesToMetrics, serviceMap) |
| Loki | `loki` | Tempo (tracesToLogsV2, lokiSearch) |
| Tempo | `tempo` | Dashboard queries |

---

## Success Criteria

- [ ] datasources.yml created in grafana/datasources directory
- [ ] Prometheus datasource configured as default
- [ ] Loki datasource configured for log queries
- [ ] Tempo datasource configured with all correlation settings
- [ ] UIDs are consistent (`prometheus`, `loki`, `tempo`)
- [ ] trace-to-logs correlation works (click "Logs for this span" in Tempo)
- [ ] Service map visualization available in Tempo
- [ ] All datasources accessible in Grafana after startup
- [ ] Configuration includes inline documentation

---

## Integration Points

### Upstream
- **P1-06**: Grafana service must mount this directory

### Downstream
- **P3-02**: Dashboard provisioning references datasources
- **P3-03**: Backend dashboard uses these datasource UIDs

### Contract: Datasource UIDs

All dashboard JSON files must reference datasources by these UIDs:

| Datasource | UID | Usage in Dashboard |
|------------|-----|-------------------|
| Prometheus | `prometheus` | `"datasource": {"type": "prometheus", "uid": "prometheus"}` |
| Loki | `loki` | `"datasource": {"type": "loki", "uid": "loki"}` |
| Tempo | `tempo` | `"datasource": {"type": "tempo", "uid": "tempo"}` |

### Contract: Internal URLs

Datasources connect to services via Docker internal DNS:

| Service | URL | Port |
|---------|-----|------|
| Prometheus | http://prometheus:9090 | 9090 |
| Loki | http://loki:3100 | 3100 |
| Tempo | http://tempo:3200 | 3200 |

---

## Monitoring/Observability

After implementation, verify:
- Grafana shows all 3 datasources in Configuration > Data Sources
- Each datasource shows "Data source is working" on test
- Explore view can query all 3 datasources
- Trace-to-logs link works in Tempo Explore

---

## Infrastructure Needs

**Grafana Volume Mount** (from P1-06):
```yaml
volumes:
  - ./observability/grafana/datasources:/etc/grafana/provisioning/datasources:ro
```

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Creating datasource configuration
- Configuring trace correlations
- Testing datasource connectivity
- Verifying correlation features
