# P3-03: Port Backend Service Dashboard

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P3-03 |
| **Title** | Port Backend Service Dashboard |
| **Domain** | DevOps |
| **Complexity** | M (1-2 days) |
| **Dependencies** | P3-02, P2-02 |
| **Blocks** | None (end of Phase 3) |

---

## Scope

### Included
- Port `backend-dashboard.json` from implementation-manager
- Update datasource references to use correct UIDs
- Configure panels for backend metrics visualization
- Set appropriate refresh interval and time range
- Add recent logs panel from Loki

### Excluded
- SLO dashboard (future work per FRD)
- Log Explorer dashboard (future work per FRD)
- Trace Explorer dashboard (future work per FRD)
- Custom business metrics panels

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/grafana/dashboards/backend-dashboard.json`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/backend-dashboard.json`

---

## Implementation Details

### Dashboard Panels

The Backend Service Dashboard should include:

1. **Request Rate (Graph)**
   - Metric: `rate(http_requests_total{job="backend"}[5m])`
   - Labels: by method, endpoint
   - Type: Time series graph

2. **Latency Percentiles (Graph)**
   - Metric: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="backend"}[5m]))`
   - Show: p50, p95, p99
   - Type: Time series graph

3. **Error Rate (Graph)**
   - Metric: `rate(http_requests_total{job="backend",status=~"5.."}[5m])`
   - Also show: 4xx errors
   - Type: Time series graph

4. **Active Requests (Stat)**
   - Metric: `active_requests`
   - Type: Stat panel (gauge)
   - Thresholds: Green < 10, Yellow < 50, Red >= 50

5. **Recent Logs (Logs)**
   - Query: `{service="backend"}`
   - Limit: Last 100 entries
   - Type: Logs panel

### Dashboard JSON Structure

```json
{
  "uid": "backend-service",
  "title": "Backend Service Dashboard",
  "description": "Request rate, latency, errors, and logs for the backend service",
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
      "title": "Request Rate",
      "type": "timeseries",
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 0 },
      "targets": [
        {
          "expr": "rate(http_requests_total{job=\"backend\"}[5m])",
          "legendFormat": "{{method}} {{endpoint}}"
        }
      ]
    },
    {
      "title": "Latency Percentiles",
      "type": "timeseries",
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 0 },
      "targets": [
        {
          "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket{job=\"backend\"}[5m]))",
          "legendFormat": "p50"
        },
        {
          "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"backend\"}[5m]))",
          "legendFormat": "p95"
        },
        {
          "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket{job=\"backend\"}[5m]))",
          "legendFormat": "p99"
        }
      ]
    },
    {
      "title": "Error Rate",
      "type": "timeseries",
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "gridPos": { "h": 8, "w": 12, "x": 0, "y": 8 },
      "targets": [
        {
          "expr": "rate(http_requests_total{job=\"backend\",status=~\"5..\"}[5m])",
          "legendFormat": "5xx errors"
        },
        {
          "expr": "rate(http_requests_total{job=\"backend\",status=~\"4..\"}[5m])",
          "legendFormat": "4xx errors"
        }
      ]
    },
    {
      "title": "Active Requests",
      "type": "stat",
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "gridPos": { "h": 8, "w": 12, "x": 12, "y": 8 },
      "targets": [
        {
          "expr": "active_requests",
          "legendFormat": "Active"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": null },
              { "color": "yellow", "value": 10 },
              { "color": "red", "value": 50 }
            ]
          }
        }
      }
    },
    {
      "title": "Recent Logs",
      "type": "logs",
      "datasource": {
        "type": "loki",
        "uid": "loki"
      },
      "gridPos": { "h": 10, "w": 24, "x": 0, "y": 16 },
      "targets": [
        {
          "expr": "{service=\"backend\"}",
          "maxLines": 100
        }
      ]
    }
  ]
}
```

### Key Configuration Points

1. **Datasource UIDs**
   - Must match UIDs in datasources.yml (P3-01)
   - Prometheus panels: `"uid": "prometheus"`
   - Loki panels: `"uid": "loki"`

2. **Refresh Interval**
   - 10 seconds for near real-time updates
   - Matches Prometheus scrape interval

3. **Time Range**
   - Default: Last 1 hour
   - Appropriate for development debugging

4. **Grid Layout**
   - 24-column grid system
   - Panels arranged logically (metrics above, logs below)

### Porting Steps

1. Copy source JSON from implementation-manager
2. Update datasource UIDs to match template UIDs
3. Verify PromQL queries use correct job label (`job="backend"`)
4. Update Loki query to use correct label (`service="backend"`)
5. Test all panels show data

---

## Success Criteria

- [ ] Dashboard JSON is valid and loads without errors
- [ ] All datasource UIDs match those in P3-01
- [ ] Request Rate panel shows data when backend receives requests
- [ ] Latency Percentiles show p50, p95, p99
- [ ] Error Rate panel shows 4xx and 5xx separately
- [ ] Active Requests gauge displays current count
- [ ] Recent Logs panel shows backend logs from Loki
- [ ] Dashboard auto-refreshes every 10 seconds
- [ ] Dashboard appears in Grafana after stack startup

---

## Integration Points

### Upstream
- **P3-02**: Dashboard provisioning must be configured
- **P2-02**: Backend must expose metrics for these queries

### Contract: Metric Names

Dashboard queries depend on these metric names from P2-02:

| Metric | Type | Labels | Dashboard Panel |
|--------|------|--------|-----------------|
| `http_requests_total` | Counter | method, endpoint, status | Request Rate, Error Rate |
| `http_request_duration_seconds` | Histogram | method, endpoint | Latency Percentiles |
| `active_requests` | Gauge | (none) | Active Requests |

### Contract: Job Label

Prometheus queries use `job="backend"` which matches the scrape job name in prometheus.yml (P1-02):

```yaml
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
```

### Contract: Loki Label

Logs panel uses `service="backend"` which is extracted by Promtail (P1-04) from Docker Compose service label.

---

## Monitoring/Observability

After implementation, verify:
- Dashboard loads without errors
- All panels show "No data" or actual data (no query errors)
- Refresh works automatically
- Drilling down to Explore works from panels

---

## Infrastructure Needs

**Dashboard File Location**:
```
observability/grafana/dashboards/backend-dashboard.json
```

This is automatically loaded by the dashboard provider (P3-02).

---

## Estimated Effort

**Time**: 4-8 hours

Includes:
- Porting and adapting dashboard JSON
- Updating datasource references
- Testing all panels
- Adjusting layout and thresholds
- Verifying data flow
