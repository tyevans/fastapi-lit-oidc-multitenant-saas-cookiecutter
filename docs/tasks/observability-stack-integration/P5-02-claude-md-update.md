# P5-02: Update CLAUDE.md with Observability Info

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P5-02 |
| **Title** | Update CLAUDE.md with Observability Info |
| **Domain** | DevOps |
| **Complexity** | XS (< 4 hours) |
| **Dependencies** | P5-01 |
| **Blocks** | None |

---

## Scope

### Included
- Add observability section to CLAUDE.md
- Document common observability commands
- List service ports (conditionally)
- Provide usage examples for AI assistants

### Excluded
- Detailed configuration documentation
- Production deployment information

---

## Relevant Code Areas

### Destination File
- `template/{{cookiecutter.project_slug}}/CLAUDE.md`

---

## Implementation Details

### Section to Add

Add after the existing "Service Ports" section or as a new section:

```markdown
{% if cookiecutter.include_observability == "yes" %}
## Observability Stack

The project includes a complete observability stack for monitoring, logging, and tracing.

### Service URLs

| Service | Port | URL |
|---------|------|-----|
| Grafana | {{ cookiecutter.grafana_port }} | http://localhost:{{ cookiecutter.grafana_port }} |
| Prometheus | {{ cookiecutter.prometheus_port }} | http://localhost:{{ cookiecutter.prometheus_port }} |
| Loki | {{ cookiecutter.loki_port }} | http://localhost:{{ cookiecutter.loki_port }} |
| Tempo | {{ cookiecutter.tempo_http_port }} | http://localhost:{{ cookiecutter.tempo_http_port }} |

### Common Commands

```bash
# View observability logs
docker compose logs grafana
docker compose logs prometheus
docker compose logs loki
docker compose logs tempo
docker compose logs promtail

# Restart observability stack
docker compose restart grafana prometheus loki tempo promtail

# Check Prometheus targets
curl http://localhost:{{ cookiecutter.prometheus_port }}/api/v1/targets

# Query backend metrics
curl http://localhost:{{ cookiecutter.backend_port }}/metrics
```

### Useful PromQL Queries

```promql
# Request rate
rate(http_requests_total{job="backend"}[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="backend"}[5m]))

# Error rate
rate(http_requests_total{job="backend",status=~"5.."}[5m])

# Active requests
active_requests
```

### Useful LogQL Queries

```logql
# Backend logs
{service="backend"}

# Error logs only
{service="backend"} |= "ERROR"

# Logs with trace ID
{service="backend"} | json | trace_id != ""
```
{% endif %}
```

### Update Service Ports Table

Modify the existing ports table to include observability:

```markdown
## Service Ports

| Service    | Port |
|------------|------|
| Frontend   | {{ cookiecutter.frontend_port }} |
| Backend    | {{ cookiecutter.backend_port }} |
| PostgreSQL | {{ cookiecutter.postgres_port }} |
| Redis      | {{ cookiecutter.redis_port }} |
| Keycloak   | {{ cookiecutter.keycloak_port }} |
{% if cookiecutter.include_observability == "yes" %}
| Grafana    | {{ cookiecutter.grafana_port }} |
| Prometheus | {{ cookiecutter.prometheus_port }} |
| Loki       | {{ cookiecutter.loki_port }} |
| Tempo      | {{ cookiecutter.tempo_http_port }} |
{% endif %}
```

### Update Project Overview

If CLAUDE.md has a project overview, add observability to the stack:

```markdown
## Project Overview

Full-stack multi-tenant {{ cookiecutter.project_name }} application with OAuth 2.0 authentication and Row-Level Security.

**Stack:**
- Backend: FastAPI (Python {{ cookiecutter.python_version }}) with async SQLAlchemy, PostgreSQL {{ cookiecutter.postgres_version }}, Redis {{ cookiecutter.redis_version }}
- Frontend: Lit 3.x web components with Vite 5.x, TypeScript, Tailwind CSS
- Auth: Keycloak {{ cookiecutter.keycloak_version }} (OAuth 2.0/OIDC with PKCE)
- Infrastructure: Docker Compose ({% if cookiecutter.include_observability == "yes" %}10{% else %}5{% endif %} services)
{% if cookiecutter.include_observability == "yes" %}
- Observability: Grafana, Prometheus, Loki, Tempo
{% endif %}
```

---

## Success Criteria

- [ ] Observability section added to CLAUDE.md template
- [ ] Service URLs use correct port variables
- [ ] Common commands documented
- [ ] PromQL and LogQL examples included
- [ ] Content conditionally rendered based on include_observability
- [ ] Service count in overview reflects observability choice
- [ ] Generated CLAUDE.md is helpful for AI assistants

---

## Integration Points

### Upstream
- **P5-01**: README update establishes documentation pattern

### Contract: Purpose of CLAUDE.md

CLAUDE.md provides context for AI assistants (like Claude) working with the codebase. Content should:
- Be actionable (commands, queries)
- Be correct (verified ports, endpoints)
- Be concise (reference other docs for details)
- Provide quick wins (copy-paste commands)

---

## Monitoring/Observability

After implementation, verify:
- Commands work as documented
- Port numbers are correct
- Queries return expected results

---

## Infrastructure Needs

None - documentation only.

---

## Estimated Effort

**Time**: 1-2 hours

Includes:
- Adding observability section
- Updating existing sections
- Testing commands
- Verifying conditional rendering
