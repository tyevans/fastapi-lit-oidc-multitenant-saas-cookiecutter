# P3-01: Create Prometheus Alerting Rules

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P3-01 |
| **Task Title** | Create Prometheus Alerting Rules |
| **Domain** | DevOps |
| **Complexity** | M (Medium) |
| **Estimated Effort** | 2 days |
| **Priority** | Must Have |
| **Dependencies** | None (observability stack already exists) |
| **FRD Requirements** | FR-OPS-005, FR-OPS-006, FR-OPS-007, FR-OPS-008, FR-OPS-009, FR-OPS-010 |

---

## Scope

### What This Task Includes

1. Create `observability/prometheus/alerts.yml` alerting rules file
2. Implement HighErrorRate alert (5xx > 1% for 5 minutes)
3. Implement HighLatency alert (p95 > 2s for 5 minutes)
4. Implement DatabaseConnectionPoolExhausted alert
5. Implement RedisConnectionFailure alert
6. Implement ServiceDown alerts for critical services
7. Add Grafana notification channel template (webhook)
8. Document alert thresholds and escalation procedures
9. Add cookiecutter conditional (part of `include_observability`)

### What This Task Excludes

- Prometheus configuration update (P3-02) - separate task for rule_files
- PagerDuty/OpsGenie direct integration (documented patterns only)
- Custom application-specific alerts (template provides foundation)
- Alert silencing/inhibition rules (advanced configuration)
- Alertmanager deployment (Grafana alerting used instead)

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_observability == "yes" %}{% endraw %}
observability/
  prometheus/
    alerts.yml                          # Prometheus alerting rules
  grafana/
    provisioning/
      notifiers/
        webhook.yml                     # Notification channel template
{% raw %}{% endif %}{% endraw %}
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/observability/prometheus/prometheus.yml` | Existing Prometheus configuration |
| `template/{{cookiecutter.project_slug}}/observability/grafana/datasources/datasources.yml` | Grafana datasource configuration |
| `template/{{cookiecutter.project_slug}}/backend/app/main.py` | FastAPI metrics endpoint |
| `docs/adr/017-optional-observability-stack.md` | Observability stack architecture |

---

## Technical Specification

### Alerting Rules File Structure

```yaml
# observability/prometheus/alerts.yml
#
# Prometheus Alerting Rules for {{ cookiecutter.project_name }}
#
# These rules define conditions that trigger alerts when service health
# or performance degrades. Alerts are evaluated every 15 seconds
# (per prometheus.yml evaluation_interval).
#
# Alert severity levels:
#   critical - Immediate response required, service degradation
#   warning  - Investigation needed, potential issues
#   info     - Informational, no immediate action
#
# For more information:
# https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/

groups:
  # ===========================================================================
  # Backend API Alerts
  # ===========================================================================
  - name: backend_alerts
    rules:
      # -----------------------------------------------------------------------
      # High Error Rate Alert
      # -----------------------------------------------------------------------
      # Triggers when HTTP 5xx error rate exceeds 1% of total requests
      # for 5 consecutive minutes.
      #
      # Rationale: 1% error rate indicates systemic issues beyond occasional
      # timeouts. 5 minute duration avoids false positives from brief spikes.
      - alert: HighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{job="backend",status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{job="backend"}[5m]))
          ) > 0.01
        for: 5m
        labels:
          severity: critical
          service: backend
        annotations:
          summary: "High error rate detected on backend API"
          description: |
            Error rate is {{ printf "%.2f" $value }}% (threshold: 1%).
            HTTP 5xx responses have exceeded 1% of total traffic for 5 minutes.
            Check backend logs for exception details.
          runbook_url: "{{ '{{' }} .ExternalURL {{ '}}' }}/runbooks/high-error-rate.md"

      # -----------------------------------------------------------------------
      # High Latency Alert
      # -----------------------------------------------------------------------
      # Triggers when 95th percentile response time exceeds 2 seconds
      # for 5 consecutive minutes.
      #
      # Rationale: p95 > 2s indicates degraded user experience. 5 minute
      # duration accounts for legitimate traffic spikes.
      - alert: HighLatency
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket{job="backend"}[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning
          service: backend
        annotations:
          summary: "High latency detected on backend API"
          description: |
            95th percentile latency is {{ printf "%.2f" $value }}s (threshold: 2s).
            Most requests are completing slowly. Check for:
            - Database query performance
            - External service latency
            - Resource exhaustion (CPU, memory)
          runbook_url: "{{ '{{' }} .ExternalURL {{ '}}' }}/runbooks/high-latency.md"

      # -----------------------------------------------------------------------
      # Backend Service Down
      # -----------------------------------------------------------------------
      # Triggers when backend is unreachable for 1 minute.
      - alert: BackendDown
        expr: up{job="backend"} == 0
        for: 1m
        labels:
          severity: critical
          service: backend
        annotations:
          summary: "Backend API is down"
          description: |
            Backend service has been unreachable for 1 minute.
            Prometheus cannot scrape metrics from the backend.
            Check container status and logs.
          runbook_url: "{{ '{{' }} .ExternalURL {{ '}}' }}/runbooks/service-down.md"

  # ===========================================================================
  # Database Alerts
  # ===========================================================================
  - name: database_alerts
    rules:
      # -----------------------------------------------------------------------
      # Database Connection Pool Exhausted
      # -----------------------------------------------------------------------
      # Triggers when PostgreSQL connections approach the maximum limit.
      # Uses 90% threshold to allow time for remediation.
      #
      # Note: This requires PostgreSQL metrics exposed via pg_exporter or
      # application-level connection pool metrics. Adjust expr based on
      # available metrics.
      - alert: DatabaseConnectionPoolExhausted
        expr: |
          (
            pg_stat_activity_count{state!="idle"}
            /
            pg_settings_max_connections
          ) > 0.9
        for: 2m
        labels:
          severity: critical
          service: postgres
        annotations:
          summary: "Database connection pool near exhaustion"
          description: |
            Active database connections are at {{ printf "%.0f" $value }}% of max_connections.
            New connections may be rejected. Consider:
            - Increasing max_connections
            - Optimizing slow queries
            - Checking for connection leaks
          runbook_url: "{{ '{{' }} .ExternalURL {{ '}}' }}/runbooks/db-connections.md"

      # -----------------------------------------------------------------------
      # Database Connection Pool (Application Level)
      # -----------------------------------------------------------------------
      # Alternative alert using SQLAlchemy pool metrics if pg_exporter
      # is not deployed. Adjust based on actual metric names.
      - alert: SQLAlchemyPoolExhausted
        expr: |
          sqlalchemy_pool_checked_out{job="backend"}
          /
          sqlalchemy_pool_size{job="backend"}
          > 0.9
        for: 2m
        labels:
          severity: warning
          service: backend
        annotations:
          summary: "SQLAlchemy connection pool near exhaustion"
          description: |
            Application connection pool is {{ printf "%.0f" $value }}% utilized.
            Backend may experience connection wait times.

  # ===========================================================================
  # Redis Alerts
  # ===========================================================================
  - name: redis_alerts
    rules:
      # -----------------------------------------------------------------------
      # Redis Connection Failure
      # -----------------------------------------------------------------------
      # Triggers when Redis becomes unreachable.
      - alert: RedisConnectionFailure
        expr: redis_up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
          service: redis
        annotations:
          summary: "Redis is unreachable"
          description: |
            Redis has been unreachable for 1 minute.
            This affects:
            - Rate limiting (may fail open)
            - Token revocation checks
            - Caching (performance degradation)
          runbook_url: "{{ '{{' }} .ExternalURL {{ '}}' }}/runbooks/redis-down.md"

      # -----------------------------------------------------------------------
      # Redis Memory Usage
      # -----------------------------------------------------------------------
      # Triggers when Redis memory usage exceeds 80% of maxmemory.
      - alert: RedisHighMemory
        expr: |
          redis_memory_used_bytes{job="redis"}
          /
          redis_memory_max_bytes{job="redis"}
          > 0.8
        for: 5m
        labels:
          severity: warning
          service: redis
        annotations:
          summary: "Redis memory usage high"
          description: |
            Redis memory usage is {{ printf "%.0f" $value }}% of maxmemory.
            Eviction policy may start removing keys.

  # ===========================================================================
  # Authentication Service Alerts
  # ===========================================================================
  - name: keycloak_alerts
    rules:
      # -----------------------------------------------------------------------
      # Keycloak Down
      # -----------------------------------------------------------------------
      - alert: KeycloakDown
        expr: up{job="keycloak"} == 0
        for: 2m
        labels:
          severity: critical
          service: keycloak
        annotations:
          summary: "Keycloak authentication service is down"
          description: |
            Keycloak has been unreachable for 2 minutes.
            This affects:
            - New user logins (blocked)
            - Token refresh (may fail)
            - JWKS retrieval (may use cached keys)
          runbook_url: "{{ '{{' }} .ExternalURL {{ '}}' }}/runbooks/keycloak-down.md"

  # ===========================================================================
  # Infrastructure Alerts
  # ===========================================================================
  - name: infrastructure_alerts
    rules:
      # -----------------------------------------------------------------------
      # High CPU Usage (Container Level)
      # -----------------------------------------------------------------------
      - alert: HighCPUUsage
        expr: |
          sum(rate(container_cpu_usage_seconds_total{name=~".+"}[5m])) by (name)
          /
          sum(container_spec_cpu_quota{name=~".+"}
              /
              container_spec_cpu_period{name=~".+"}
          ) by (name)
          > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on container {{ '{{' }} $labels.name {{ '}}' }}"
          description: |
            Container {{ '{{' }} $labels.name {{ '}}' }} is using {{ printf "%.0f" $value }}% of CPU quota.

      # -----------------------------------------------------------------------
      # High Memory Usage (Container Level)
      # -----------------------------------------------------------------------
      - alert: HighMemoryUsage
        expr: |
          container_memory_working_set_bytes{name=~".+"}
          /
          container_spec_memory_limit_bytes{name=~".+"}
          > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on container {{ '{{' }} $labels.name {{ '}}' }}"
          description: |
            Container {{ '{{' }} $labels.name {{ '}}' }} is using {{ printf "%.0f" $value }}% of memory limit.
```

### Grafana Notification Channel Template

```yaml
# observability/grafana/provisioning/notifiers/webhook.yml
#
# Grafana Notification Channel Configuration
#
# This template configures a webhook notification channel for alerting.
# Replace the URL with your actual alerting endpoint (Slack, PagerDuty, etc.)
#
# For Slack integration:
#   url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
#
# For PagerDuty integration:
#   url: https://events.pagerduty.com/v2/enqueue
#
# For more information:
# https://grafana.com/docs/grafana/latest/alerting/notifications/

notifiers:
  - name: webhook-alerts
    type: webhook
    uid: webhook-alerts
    org_id: 1
    is_default: true
    send_reminder: true
    frequency: 1h
    disable_resolve_message: false
    settings:
      url: "${ALERT_WEBHOOK_URL:-http://localhost:9999/alerts}"
      httpMethod: POST
      username: ""
      password: ""
      autoResolve: true
      uploadImage: false
```

### Alert Threshold Justification

| Alert | Threshold | Duration | Rationale |
|-------|-----------|----------|-----------|
| HighErrorRate | > 1% | 5m | 1% is significant error rate; 5m prevents false positives |
| HighLatency | p95 > 2s | 5m | 2s is poor UX threshold; 5m accounts for traffic spikes |
| BackendDown | up == 0 | 1m | Service outage requires quick response |
| DatabaseConnectionPoolExhausted | > 90% | 2m | Near exhaustion needs immediate attention |
| RedisConnectionFailure | up == 0 | 1m | Critical for rate limiting and caching |
| KeycloakDown | up == 0 | 2m | Auth service critical but may have brief restarts |

### Alert Severity Levels

| Severity | Description | Response Time | Notification |
|----------|-------------|---------------|--------------|
| critical | Service outage or degradation | < 15 minutes | Page on-call |
| warning | Potential issues, investigation needed | < 1 hour | Team channel |
| info | Informational, no immediate action | Next business day | Dashboard |

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| None | - | Observability stack exists per ADR-017 |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P3-02 | Required | prometheus.yml needs rule_files configuration |
| P3-08 | Reference | Runbook templates reference alert conditions |

---

## Success Criteria

### Functional Requirements

- [ ] `alerts.yml` file created in observability/prometheus/ directory
- [ ] HighErrorRate alert triggers on 5xx > 1% for 5 minutes
- [ ] HighLatency alert triggers on p95 > 2s for 5 minutes
- [ ] DatabaseConnectionPoolExhausted alert triggers at 90% capacity
- [ ] RedisConnectionFailure alert triggers when Redis unreachable
- [ ] BackendDown alert triggers when backend unreachable
- [ ] KeycloakDown alert triggers when Keycloak unreachable
- [ ] All alerts have severity labels (critical, warning, info)
- [ ] All alerts have service labels for filtering
- [ ] All alerts have description and runbook_url annotations
- [ ] Grafana webhook notification channel template created
- [ ] File wrapped in cookiecutter `include_observability` conditional

### Non-Functional Requirements

- [ ] Alert expressions are syntactically valid PromQL
- [ ] Alert thresholds are documented with rationale
- [ ] Severity levels follow documented escalation policy
- [ ] Annotations provide actionable information
- [ ] Comments explain each alert's purpose
- [ ] Alert names follow consistent naming convention (PascalCase)

### Validation Steps

1. Syntax validation
   - Load alerts.yml in Prometheus UI (Status > Rules)
   - Verify no syntax errors reported
   - Confirm all rules appear in expected state

2. Alert triggering test (manual)
   - Simulate high error rate by returning 5xx from backend
   - Verify HighErrorRate alert enters PENDING then FIRING state
   - Verify alert annotations render correctly

3. Grafana integration
   - Verify alerts visible in Grafana Alerting dashboard
   - Test notification channel with test message
   - Verify alert state syncs from Prometheus

4. Documentation review
   - Verify each alert has meaningful description
   - Verify runbook URLs point to existing (or planned) documents
   - Verify severity levels are consistent

---

## Integration Points

### Prometheus Configuration Integration

P3-02 will update prometheus.yml to load these rules:

```yaml
# prometheus.yml (addition for P3-02)
rule_files:
  - "alerts.yml"
```

### Grafana Alert Integration

Grafana uses Prometheus as alerting datasource:
- Alerts visible in Alerting > Alert Rules
- Can create Grafana-native alerts alongside Prometheus rules
- Notification channels route alerts to external systems

### Metric Dependencies

Alerts depend on these metrics being available:

| Metric | Source | Required For |
|--------|--------|--------------|
| `http_requests_total` | FastAPI prometheus_client | HighErrorRate |
| `http_request_duration_seconds_bucket` | FastAPI prometheus_client | HighLatency |
| `up` | Prometheus scrape | ServiceDown alerts |
| `pg_stat_activity_count` | pg_exporter (optional) | DatabaseConnectionPoolExhausted |
| `redis_up` | redis_exporter (optional) | RedisConnectionFailure |

### Cookiecutter Conditional

Alerts are only included when `include_observability == "yes"`:

```
{% raw %}{% if cookiecutter.include_observability == "yes" %}{% endraw %}
observability/prometheus/alerts.yml
{% raw %}{% endif %}{% endraw %}
```

---

## Monitoring and Observability

### Alert on Alerts

Consider adding meta-alerts:

```yaml
- alert: PrometheusAlertingFailure
  expr: prometheus_notifications_dropped_total > 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Prometheus is failing to send alerts"
```

### Dashboard Integration

Alerts should be visible in:
- Prometheus UI: Status > Rules
- Grafana: Alerting > Alert Rules
- Grafana Dashboard: Alert list panel

---

## Infrastructure Needs

### Optional Exporters

For full alert coverage, consider adding:

| Exporter | Purpose | Port |
|----------|---------|------|
| postgres_exporter | Database metrics | 9187 |
| redis_exporter | Redis metrics | 9121 |
| node_exporter | Host metrics | 9100 |
| cadvisor | Container metrics | 8080 |

These are optional enhancements; core alerts work with existing scrape targets.

### Resource Requirements

- No additional resources for alerting rules
- Alert evaluation adds minimal CPU overhead
- Notification channels may require external connectivity

---

## Implementation Notes

### PromQL Syntax

Alert expressions must be valid PromQL. Key patterns:

```promql
# Rate calculation over time window
rate(metric[5m])

# Ratio calculation
sum(rate(metric_a[5m])) / sum(rate(metric_b[5m]))

# Histogram percentile
histogram_quantile(0.95, sum(rate(histogram_bucket[5m])) by (le))

# Boolean check
up{job="backend"} == 0
```

### Alert Duration (for:)

The `for` clause prevents flapping:
- Too short: False positives from brief spikes
- Too long: Delayed response to real issues
- Generally: 1-5 minutes for critical, 5-15 minutes for warning

### Template Variables

Annotations support Go template syntax:
- `{{ $value }}` - Current value that triggered alert
- `{{ $labels.name }}` - Label value from metric
- `{{ .ExternalURL }}` - Prometheus URL

### Recording Rules (Future Enhancement)

For complex queries, consider recording rules:

```yaml
groups:
  - name: recording_rules
    rules:
      - record: job:http_requests:rate5m
        expr: sum(rate(http_requests_total[5m])) by (job)
```

Recording rules pre-compute expensive queries for faster alerting.

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-OPS-005 | Prometheus alerting rules file included | `alerts.yml` file |
| FR-OPS-006 | Alert on HTTP 5xx > 1% for 5 minutes | HighErrorRate alert |
| FR-OPS-007 | Alert on p95 latency > 2s for 5 minutes | HighLatency alert |
| FR-OPS-008 | Alert on database connection pool exhaustion | DatabaseConnectionPoolExhausted alert |
| FR-OPS-009 | Alert on Redis connection failures | RedisConnectionFailure alert |
| FR-OPS-010 | Grafana notification channel template | `webhook.yml` provisioning |

### Related ADRs

- ADR-017: Optional Observability Stack (existing observability architecture)
- ADR-019: GitHub Actions CI/CD (deployment context)

### External Resources

- [Prometheus Alerting Rules](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
- [Prometheus Recording Rules](https://prometheus.io/docs/prometheus/latest/configuration/recording_rules/)
- [PromQL Documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Alerting](https://grafana.com/docs/grafana/latest/alerting/)
- [SRE Book - Monitoring](https://sre.google/sre-book/monitoring-distributed-systems/)
