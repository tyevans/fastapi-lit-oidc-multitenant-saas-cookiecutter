# P1-02: Port Prometheus Configuration

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P1-02 |
| **Title** | Port Prometheus Configuration |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P1-01 |
| **Blocks** | P1-06 |

---

## Scope

### Included
- Port `prometheus.yml` from implementation-manager to template
- Templatize with cookiecutter variables (project_slug)
- Configure scrape targets for backend, keycloak, and observability services
- Add inline documentation comments

### Excluded
- Alert rules configuration (out of scope per FRD)
- Remote write configuration (production concern)
- Custom recording rules

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/prometheus/prometheus.yml`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/prometheus/prometheus.yml`

---

## Implementation Details

### Configuration Structure

```yaml
# Prometheus configuration for {{ cookiecutter.project_name }}
# Scrapes metrics from backend, keycloak, and observability services

global:
  scrape_interval: 15s     # Default scrape interval
  evaluation_interval: 15s # Rule evaluation interval
  external_labels:
    cluster: '{{ cookiecutter.project_slug }}'

scrape_configs:
  # Self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Backend API metrics (more frequent for responsive dashboards)
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  # Keycloak metrics (less frequent, lower priority)
  - job_name: 'keycloak'
    static_configs:
      - targets: ['keycloak:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Tempo metrics
  - job_name: 'tempo'
    static_configs:
      - targets: ['tempo:3200']
    metrics_path: '/metrics'

  # Loki metrics
  - job_name: 'loki'
    static_configs:
      - targets: ['loki:3100']
    metrics_path: '/metrics'
```

### Key Configuration Points

1. **Global Settings**
   - 15-second default scrape interval
   - External label with project slug for identification

2. **Backend Scrape Job**
   - 5-second interval for responsive dashboards
   - Targets `/metrics` endpoint

3. **Keycloak Scrape Job**
   - 30-second interval (lower priority)
   - Note: Keycloak in dev mode exposes limited metrics

4. **Observability Service Monitoring**
   - Prometheus, Loki, and Tempo self-monitoring

---

## Success Criteria

- [ ] Configuration file validates against Prometheus config schema
- [ ] Project slug is properly templatized in `external_labels.cluster`
- [ ] All scrape targets use correct Docker service names
- [ ] Backend scrape interval is 5 seconds (per FRD requirement)
- [ ] Configuration includes inline comments explaining each section
- [ ] File renders correctly when cookiecutter generates project

---

## Integration Points

### Upstream
- **P1-01**: Directory structure must exist

### Downstream
- **P1-06**: Prometheus service in compose.yml will mount this configuration
- **P3-01**: Grafana datasource will connect to Prometheus

### Contract: Prometheus Scrape Targets
The following endpoints must be available for Prometheus to scrape:

| Target | Port | Path | Provider Task |
|--------|------|------|---------------|
| backend:8000 | 8000 | /metrics | P2-02 |
| keycloak:8080 | 8080 | /metrics | Existing |
| tempo:3200 | 3200 | /metrics | P1-05 |
| loki:3100 | 3100 | /metrics | P1-03 |

---

## Monitoring/Observability

After implementation, verify:
- Prometheus targets page shows all configured targets
- Scrape success rate is > 99%
- No configuration errors in Prometheus logs

---

## Infrastructure Needs

None - configuration file only.

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Reviewing source configuration
- Templatizing variables
- Adding documentation
- Validating YAML syntax
