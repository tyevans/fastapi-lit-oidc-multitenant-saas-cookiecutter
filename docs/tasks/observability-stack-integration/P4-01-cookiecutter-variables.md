# P4-01: Add cookiecutter.json Variables

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P4-01 |
| **Title** | Add cookiecutter.json Variables |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P1-06, P2-02 |
| **Blocks** | P4-02, P4-03, P4-04, P4-05 |

---

## Scope

### Included
- Add `include_observability` variable to cookiecutter.json
- Add optional port configuration variables
- Document variable prompts and descriptions
- Set sensible defaults

### Excluded
- Conditional rendering logic (handled in P4-02 through P4-05)
- Advanced configuration options (retention, scaling)
- Production-specific settings

---

## Relevant Code Areas

### Destination File
- `/home/ty/workspace/project-starter/template/cookiecutter.json`

---

## Implementation Details

### Variables to Add

```json
{
  // ... existing variables ...

  "include_observability": "yes",
  "grafana_port": "3000",
  "prometheus_port": "9090",
  "tempo_http_port": "3200",
  "tempo_otlp_grpc_port": "4317",
  "tempo_otlp_http_port": "4318",
  "loki_port": "3100"
}
```

### Variable Definitions

| Variable | Default | Type | Description |
|----------|---------|------|-------------|
| `include_observability` | "yes" | Choice | Enable/disable observability stack |
| `grafana_port` | "3000" | String | Grafana dashboard port |
| `prometheus_port` | "9090" | String | Prometheus metrics UI port |
| `tempo_http_port` | "3200" | String | Tempo HTTP API port |
| `tempo_otlp_grpc_port` | "4317" | String | Tempo OTLP gRPC receiver port |
| `tempo_otlp_http_port` | "4318" | String | Tempo OTLP HTTP receiver port |
| `loki_port` | "3100" | String | Loki log aggregation port |

### Variable Placement

Add variables after existing service ports (keycloak_port, backend_port, frontend_port):

```json
{
  "_template": "template/",

  "project_name": "My Awesome Project",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '-').replace('_', '-') }}",
  // ... existing variables ...

  "backend_port": "8000",
  "backend_api_prefix": "/api/v1",
  "python_version": "3.13",

  "frontend_port": "5173",
  "node_version": "20",

  "include_observability": "yes",
  "grafana_port": "3000",
  "prometheus_port": "9090",
  "tempo_http_port": "3200",
  "tempo_otlp_grpc_port": "4317",
  "tempo_otlp_http_port": "4318",
  "loki_port": "3100",

  "license": ["MIT", "BSD-3-Clause", "Apache-2.0", "GPL-3.0", "Proprietary"]
}
```

### Conditional Port Prompting

Currently, cookiecutter does not natively support conditional prompts. Options:

**Option A: Always prompt for all variables (Recommended for simplicity)**
- All port variables shown during generation
- Observability ports unused if `include_observability` is "no"
- Simpler implementation

**Option B: Post-generation hook**
- Use hooks to remove unused variables
- More complex, requires Python hook

**Recommendation**: Use Option A for initial implementation. Port variables are harmless when observability is disabled.

### First Conditional Feature Precedent

This is the first use of conditional template variables in the cookiecutter project. The approach established here will set the precedent for future conditional features.

**Established Pattern:**
1. Use string values for boolean-like choices: `"yes"` / `"no"`
2. Check with string comparison: `{% if cookiecutter.include_observability == "yes" %}`
3. Use lowercase, snake_case for variable names
4. Group related variables together
5. Document the conditional behavior

---

## Success Criteria

- [ ] `include_observability` variable added with default "yes"
- [ ] All port variables added with sensible defaults
- [ ] Variables placed logically in cookiecutter.json (after other ports)
- [ ] Variable names follow existing naming conventions
- [ ] Cookiecutter prompts for new variables during generation
- [ ] Generated project uses variable values correctly
- [ ] Variables work with both "yes" and "no" values for include_observability

---

## Integration Points

### Upstream
- **P1-06**: compose.yml ready for conditional logic
- **P2-02**: observability.py ready for conditional inclusion

### Downstream
- **P4-02**: compose.yml uses these variables
- **P4-03**: pyproject.toml uses `include_observability`
- **P4-04**: main.py uses `include_observability`
- **P4-05**: Directory rendering uses `include_observability`

### Contract: Variable Access

Templates access these variables via:
```jinja2
{{ cookiecutter.include_observability }}
{{ cookiecutter.grafana_port }}
{{ cookiecutter.prometheus_port }}
// etc.
```

Conditional blocks use:
```jinja2
{% if cookiecutter.include_observability == "yes" %}
...
{% endif %}
```

---

## Monitoring/Observability

After implementation, verify:
- `cookiecutter template/` prompts for observability variables
- Generated project with "yes" has all observability files
- Generated project with "no" has no observability files
- Port values correctly substituted in compose.yml

---

## Infrastructure Needs

None - configuration file changes only.

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Adding variables to cookiecutter.json
- Testing with both "yes" and "no" values
- Documenting the conditional pattern
- Verifying variable access in templates
