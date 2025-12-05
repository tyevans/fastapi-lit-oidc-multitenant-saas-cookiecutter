# P5-01: Update Project README with Observability Section

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P5-01 |
| **Title** | Update Project README with Observability Section |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P4-05 |
| **Blocks** | P5-02 |

---

## Scope

### Included
- Add observability section to project README template
- Document service URLs and ports
- Provide quick-start instructions
- Conditionally render observability content
- Update architecture diagrams (if present)

### Excluded
- Full observability documentation (see observability/README.md)
- Detailed troubleshooting (covered in observability docs)
- Production deployment guide

---

## Relevant Code Areas

### Destination File
- `template/{{cookiecutter.project_slug}}/README.md`

---

## Implementation Details

### README Section to Add

Add a new section after "Quick Start" or "Development" section:

```markdown
{% if cookiecutter.include_observability == "yes" %}
## Observability Stack

This project includes a pre-configured observability stack for metrics, logs, and distributed tracing.

### Services

| Service | URL | Purpose |
|---------|-----|---------|
| Grafana | http://localhost:{{ cookiecutter.grafana_port }} | Dashboards and visualization |
| Prometheus | http://localhost:{{ cookiecutter.prometheus_port }} | Metrics collection |
| Loki | http://localhost:{{ cookiecutter.loki_port }} | Log aggregation |
| Tempo | http://localhost:{{ cookiecutter.tempo_http_port }} | Distributed tracing |

### Quick Start

1. Access Grafana at http://localhost:{{ cookiecutter.grafana_port }} (no login required)
2. Navigate to **Dashboards** > **Backend Service Dashboard**
3. Use **Explore** to query logs (Loki) and traces (Tempo)

### Key Endpoints

- **Backend Metrics**: http://localhost:{{ cookiecutter.backend_port }}/metrics
- **Prometheus UI**: http://localhost:{{ cookiecutter.prometheus_port }}

### Learn More

See [observability/README.md](./observability/README.md) for detailed documentation.
{% endif %}
```

### Update Service Ports Table

If the README has a service ports table, update it conditionally:

```markdown
## Service Ports

| Service | Port |
|---------|------|
| Frontend | {{ cookiecutter.frontend_port }} |
| Backend | {{ cookiecutter.backend_port }} |
| PostgreSQL | {{ cookiecutter.postgres_port }} |
| Redis | {{ cookiecutter.redis_port }} |
| Keycloak | {{ cookiecutter.keycloak_port }} |
{% if cookiecutter.include_observability == "yes" %}
| Grafana | {{ cookiecutter.grafana_port }} |
| Prometheus | {{ cookiecutter.prometheus_port }} |
| Loki | {{ cookiecutter.loki_port }} |
| Tempo | {{ cookiecutter.tempo_http_port }} |
{% endif %}
```

### Update Stack Description

If there's a "Tech Stack" or "Architecture" section:

```markdown
## Tech Stack

- **Backend**: FastAPI (Python {{ cookiecutter.python_version }})
- **Frontend**: Lit 3.x / Vite 5.x
- **Database**: PostgreSQL {{ cookiecutter.postgres_version }}
- **Cache**: Redis {{ cookiecutter.redis_version }}
- **Auth**: Keycloak {{ cookiecutter.keycloak_version }}
{% if cookiecutter.include_observability == "yes" %}
- **Observability**: Grafana, Prometheus, Loki, Tempo
{% endif %}
```

### Conditional Rendering Pattern

Use Jinja2 conditionals that don't break Markdown:

```markdown
{% if cookiecutter.include_observability == "yes" %}
## Observability

Content here...
{% endif %}
```

This renders cleanly because:
- Markdown ignores blank lines
- Jinja2 tags at line start don't interfere with Markdown

---

## Success Criteria

- [ ] Observability section added to README template
- [ ] Service URLs use correct port variables
- [ ] Content conditionally rendered based on include_observability
- [ ] README is valid Markdown with "yes"
- [ ] README is valid Markdown with "no" (no empty sections)
- [ ] Links to observability/README.md work
- [ ] Generated README renders correctly in GitHub/GitLab

---

## Integration Points

### Upstream
- **P4-05**: Conditional rendering must be working

### Downstream
- **P5-02**: CLAUDE.md will reference observability commands

### Contract: Port Variables

README uses these variables from cookiecutter.json:

| Variable | Default | Usage |
|----------|---------|-------|
| `grafana_port` | 3000 | Grafana URL |
| `prometheus_port` | 9090 | Prometheus URL |
| `loki_port` | 3100 | Loki URL |
| `tempo_http_port` | 3200 | Tempo URL |
| `backend_port` | 8000 | Metrics endpoint URL |

---

## Monitoring/Observability

After implementation, verify:
- README renders correctly in Markdown preview
- All URLs use correct ports
- Conditional sections appear/disappear correctly

---

## Infrastructure Needs

None - documentation only.

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Adding observability section to README
- Updating other relevant sections
- Testing conditional rendering
- Verifying Markdown validity
