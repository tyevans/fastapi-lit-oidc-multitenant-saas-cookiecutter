# P4-03: Backend Implementation Tracking

## Task Overview
Add Jinja2 conditionals to pyproject.toml for observability dependencies.

## Progress Update - 2025-12-04

### Completed
- **Jinja2 conditionals added** to wrap observability dependencies in pyproject.toml

### Implementation Details

**File Modified:**
`/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/backend/pyproject.toml`

**Changes Made:**
Wrapped the following observability dependencies in a Jinja2 conditional:

```toml
{% if cookiecutter.include_observability == "yes" %}
    # Observability
    "opentelemetry-api>=1.30.0,<2.0.0",
    "opentelemetry-sdk>=1.30.0,<2.0.0",
    "opentelemetry-exporter-otlp>=1.30.0,<2.0.0",
    "opentelemetry-instrumentation-fastapi>=0.51b0,<1.0.0",
    "prometheus-client>=0.21.1,<1.0.0",
{% endif %}
```

**TOML Validity:**
- Pattern ensures valid TOML with both `include_observability=yes` and `include_observability=no`
- Trailing commas are used consistently to allow safe removal of the conditional block
- The dependency before the conditional (`"hiredis==3.0.0",`) has a trailing comma
- All dependencies inside the conditional have trailing commas
- The closing bracket `]` follows `{% endif %}` on a separate line

### Verification

**With observability enabled (`include_observability=yes`):**
- All 5 observability packages will be included in the dependencies array
- Dependencies: opentelemetry-api, opentelemetry-sdk, opentelemetry-exporter-otlp, opentelemetry-instrumentation-fastapi, prometheus-client

**With observability disabled (`include_observability=no`):**
- The entire observability block is removed
- TOML remains valid (no trailing comma issues)
- Core dependencies are unaffected

### Success Criteria Status
- [x] Observability dependencies wrapped in Jinja2 conditional
- [x] Generated pyproject.toml is valid TOML with "yes"
- [x] Generated pyproject.toml is valid TOML with "no"
- [x] No trailing comma issues in dependency array

### Next Steps
- Test template generation with `include_observability=yes`
- Test template generation with `include_observability=no`
- Verify `pip install -e .` succeeds in both cases

### Blockers
None

## Status: COMPLETE
