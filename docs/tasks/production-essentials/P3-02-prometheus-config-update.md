# P3-02: Update prometheus.yml with rule_files

## Task Identifier
**ID:** P3-02
**Phase:** 3 - Operational Readiness
**Domain:** DevOps
**Complexity:** XS (Extra Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P3-01 | Hard | Documented | Alerting rules file must exist before referencing |

## Scope

### In Scope
- Add `rule_files` configuration section to prometheus.yml
- Reference the alerts.yml file created in P3-01
- Add `alerting` section placeholder for Alertmanager (optional)
- Update prometheus.yml documentation header comments

### Out of Scope
- Creating alerting rules (P3-01)
- Alertmanager deployment or configuration
- Grafana alert channel configuration (P3-10)
- Notification routing or receiver setup

## Relevant Code Areas

### Files to Modify
```
template/{{cookiecutter.project_slug}}/observability/prometheus/prometheus.yml
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/observability/prometheus/alerts.yml  (created by P3-01)
```

### Existing Prometheus Configuration
The current prometheus.yml contains:
- `global` section with scrape/evaluation intervals
- `scrape_configs` for prometheus, backend, keycloak, tempo, loki
- No `rule_files` or `alerting` sections

## Implementation Details

### Configuration Changes

Add `rule_files` section after `global` configuration:

```yaml
# Prometheus Configuration for {{ cookiecutter.project_name }}
# ...existing header comments...

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: '{{ cookiecutter.project_slug }}'

# -----------------------------------------------------------------------------
# Alerting Rules Configuration
# -----------------------------------------------------------------------------
# Rule files specify groups of alerting and recording rules.
# Rules are evaluated at the evaluation_interval defined above.
rule_files:
  - 'alerts.yml'

# -----------------------------------------------------------------------------
# Alertmanager Configuration (Optional)
# -----------------------------------------------------------------------------
# Configure Alertmanager for sending alert notifications.
# Uncomment and configure when Alertmanager is deployed.
#
# alerting:
#   alertmanagers:
#     - static_configs:
#         - targets:
#             - 'alertmanager:9093'

# Scrape configuration for each monitored service
scrape_configs:
  # ... existing scrape configs ...
```

### File Structure After Change
```
observability/prometheus/
  prometheus.yml       # Updated with rule_files reference
  alerts.yml           # Created by P3-01
```

## Success Criteria

### Functional Requirements
- [ ] `rule_files` section added to prometheus.yml
- [ ] alerts.yml is correctly referenced in rule_files
- [ ] Prometheus loads alerting rules on startup
- [ ] Alerting section commented placeholder is included

### Verification Steps
1. Start observability stack: `./scripts/docker-dev.sh up`
2. Check Prometheus rules are loaded:
   ```bash
   curl http://localhost:9090/api/v1/rules
   ```
3. Verify rules appear in Prometheus UI at `http://localhost:9090/rules`
4. Confirm no configuration errors in Prometheus logs:
   ```bash
   docker compose logs prometheus | grep -i "error\|warn"
   ```

### Quality Gates
- [ ] prometheus.yml passes YAML syntax validation
- [ ] Prometheus container starts successfully
- [ ] Rules endpoint returns the alert groups from P3-01
- [ ] No configuration warnings in Prometheus logs

## Integration Points

### Upstream Dependencies
| Task | Contract | Status |
|------|----------|--------|
| P3-01 | alerts.yml file exists in observability/prometheus/ | Must be complete |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P3-08 | Runbook templates reference alerting rules | Can proceed independently |

### Integration Contract
```yaml
# prometheus.yml exposes rules via API
# Expected API response after implementation:
GET /api/v1/rules
{
  "status": "success",
  "data": {
    "groups": [
      {
        "name": "backend_alerts",
        "file": "/etc/prometheus/alerts.yml",
        "rules": [...]
      },
      {
        "name": "infrastructure_alerts",
        "file": "/etc/prometheus/alerts.yml",
        "rules": [...]
      }
    ]
  }
}
```

## Monitoring and Observability

### Verification Metrics
- `prometheus_rule_group_rules` - Count of rules per group
- `prometheus_rule_evaluation_failures_total` - Rule evaluation errors
- `prometheus_rule_group_last_duration_seconds` - Rule evaluation performance

### Health Checks
- Prometheus `/rules` endpoint returns populated rule groups
- No rule evaluation errors in Prometheus metrics

## Infrastructure Needs

### Docker Compose Changes
None - prometheus.yml is already mounted as a volume.

### Volume Mounts
Existing mount handles both prometheus.yml and alerts.yml:
```yaml
# In compose.yml (observability section)
prometheus:
  volumes:
    - ./observability/prometheus:/etc/prometheus:ro
```

## Estimated Effort

**Size:** XS (Extra Small)
**Time:** 30 minutes - 1 hour
**Justification:** Single file modification, minimal code changes, straightforward YAML configuration

## Notes

### Why rule_files Instead of Inline Rules
- Separation of concerns: configuration vs. alerting logic
- Easier to manage and update alerting rules independently
- Supports multiple rule files for organization
- Standard Prometheus best practice

### Alertmanager Section
The alerting section is included as a commented placeholder because:
- Alertmanager deployment is out of scope for initial release
- Provides documentation for users who want to add alerting
- Easy to uncomment when Alertmanager is deployed
- FR-OPS-010 (Grafana alerting notification channels) covers basic alerting

### Related Requirements
- FR-OPS-005: Prometheus alerting rules file shall be included (P3-01)
- This task enables the rules to be loaded and evaluated
