# P4-02: Add Jinja2 Conditionals to compose.yml

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P4-02 |
| **Title** | Add Jinja2 Conditionals to compose.yml |
| **Domain** | DevOps |
| **Complexity** | M (1-2 days) |
| **Dependencies** | P4-01 |
| **Blocks** | None |

---

## Scope

### Included
- Wrap observability services in Jinja2 conditional blocks
- Make backend environment variables conditional
- Make volume definitions conditional
- Use port variables in service definitions
- Ensure proper YAML formatting with conditionals

### Excluded
- Network configuration changes (uses existing network)
- Backend service dependency on observability (not needed)

---

## Relevant Code Areas

### Destination File
- `template/{{cookiecutter.project_slug}}/compose.yml`

---

## Implementation Details

### Conditional Structure Overview

```yaml
services:
  # Core services (always present)
  postgres:
    # ...
  keycloak:
    # ...
  backend:
    # ...
    environment:
      # ... existing vars ...
{% if cookiecutter.include_observability == "yes" %}
      # OpenTelemetry Configuration
      OTEL_SERVICE_NAME: backend
      OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317
{% endif %}
  frontend:
    # ...
  redis:
    # ...

{% if cookiecutter.include_observability == "yes" %}
  # ============================================
  # OBSERVABILITY STACK
  # ============================================
  prometheus:
    # ...
  loki:
    # ...
  promtail:
    # ...
  tempo:
    # ...
  grafana:
    # ...
{% endif %}

volumes:
  # Core volumes (always present)
  postgres_data:
    # ...
{% if cookiecutter.include_observability == "yes" %}
  prometheus-data:
    # ...
  loki-data:
    # ...
  tempo-data:
    # ...
  grafana-data:
    # ...
{% endif %}
```

### Key Conditional Locations

1. **Backend Environment Variables** (inline conditional)
```yaml
  backend:
    environment:
      ENV: ${ENV:-development}
      # ... other vars ...
{% if cookiecutter.include_observability == "yes" %}
      OTEL_SERVICE_NAME: backend
      OTEL_EXPORTER_OTLP_ENDPOINT: http://tempo:4317
{% endif %}
```

2. **Observability Services Block** (section conditional)
```yaml
{% if cookiecutter.include_observability == "yes" %}
  # ============================================
  # OBSERVABILITY STACK
  # ============================================

  prometheus:
    image: prom/prometheus:latest
    container_name: {{ cookiecutter.project_slug }}-prometheus
    ports:
      - "${PROMETHEUS_PORT:-{{ cookiecutter.prometheus_port }}}:9090"
    # ... rest of service ...
{% endif %}
```

3. **Volumes Block** (section conditional)
```yaml
volumes:
  postgres_data:
    name: {{ cookiecutter.project_slug }}-postgres-data
  # ... other core volumes ...
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

### Port Variable Usage

Replace hardcoded ports with cookiecutter variables:

```yaml
  prometheus:
    ports:
      - "${PROMETHEUS_PORT:-{{ cookiecutter.prometheus_port }}}:9090"

  loki:
    ports:
      - "${LOKI_PORT:-{{ cookiecutter.loki_port }}}:3100"

  tempo:
    ports:
      - "${TEMPO_HTTP_PORT:-{{ cookiecutter.tempo_http_port }}}:3200"
      - "${TEMPO_OTLP_GRPC_PORT:-{{ cookiecutter.tempo_otlp_grpc_port }}}:4317"
      - "${TEMPO_OTLP_HTTP_PORT:-{{ cookiecutter.tempo_otlp_http_port }}}:4318"

  grafana:
    ports:
      - "${GRAFANA_PORT:-{{ cookiecutter.grafana_port }}}:3000"
```

### YAML Formatting Considerations

**Critical**: Jinja2 conditionals must maintain valid YAML indentation.

**Correct:**
```yaml
services:
  backend:
    environment:
      DEBUG: true
{% if cookiecutter.include_observability == "yes" %}
      OTEL_SERVICE_NAME: backend
{% endif %}
```

**Incorrect (will break YAML):**
```yaml
services:
  backend:
    environment:
      DEBUG: true
      {% if cookiecutter.include_observability == "yes" %}
      OTEL_SERVICE_NAME: backend
      {% endif %}
```

The Jinja2 tags must be at the start of the line (column 0) or you must use Jinja2 whitespace control.

### Testing Both Paths

Generate projects with both settings and verify:

1. **With observability (`include_observability: yes`):**
   - All 10 services present (5 core + 5 observability)
   - Backend has OTEL environment variables
   - All observability volumes defined
   - `docker compose up` starts all services

2. **Without observability (`include_observability: no`):**
   - Only 5 core services present
   - No OTEL environment variables on backend
   - No observability volumes defined
   - `docker compose up` starts only core services
   - No errors or warnings about missing observability

---

## Success Criteria

- [ ] Observability services conditionally included based on `include_observability`
- [ ] Backend environment variables conditionally added
- [ ] Volumes conditionally defined
- [ ] Port variables correctly substituted
- [ ] Generated YAML is valid with both "yes" and "no"
- [ ] `docker compose config` validates successfully
- [ ] `docker compose up` works with observability enabled
- [ ] `docker compose up` works with observability disabled
- [ ] No Jinja2 artifacts in generated files

---

## Integration Points

### Upstream
- **P4-01**: Variables must be defined in cookiecutter.json

### Contract: Conditional Pattern

This task establishes the conditional pattern for the template:

```jinja2
{% if cookiecutter.include_observability == "yes" %}
  # Observability-specific content
{% endif %}
```

**Key conventions:**
- Use string comparison (`== "yes"`) not boolean
- Place conditional tags at line start for YAML
- Group related conditional content together
- Add clear section headers within conditionals

---

## Monitoring/Observability

After implementation, verify:
- Generated compose.yml is valid YAML
- No Jinja2 syntax in generated files
- Service counts match expected (5 vs 10)
- Environment variables present/absent as expected

---

## Infrastructure Needs

None - template changes only.

---

## Estimated Effort

**Time**: 4-8 hours

Includes:
- Adding conditional blocks to compose.yml
- Testing YAML validity
- Verifying both generation paths
- Fixing indentation issues
- Testing service startup
