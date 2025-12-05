# P4-03: Add Conditionals to pyproject.toml

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P4-03 |
| **Title** | Add Conditionals to pyproject.toml |
| **Domain** | Backend |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P4-01 |
| **Blocks** | None |

---

## Scope

### Included
- Wrap observability Python dependencies in Jinja2 conditionals
- Ensure TOML remains valid after template rendering
- Test dependency resolution with both configurations

### Excluded
- Development/test dependencies for observability
- Optional dependency groups (extras)

---

## Relevant Code Areas

### Destination File
- `template/{{cookiecutter.project_slug}}/backend/pyproject.toml`

---

## Implementation Details

### Conditional Dependencies

Wrap observability dependencies in Jinja2 conditional:

```toml
[project]
name = "{{ cookiecutter.project_slug }}-backend"
version = "0.1.0"
description = "{{ cookiecutter.project_short_description }}"
requires-python = ">={{ cookiecutter.python_version }}"

dependencies = [
    # Core dependencies
    "fastapi>=0.109.0,<1.0.0",
    "uvicorn[standard]>=0.27.0,<1.0.0",
    "pydantic>=2.5.0,<3.0.0",
    "pydantic-settings>=2.1.0,<3.0.0",
    "sqlalchemy[asyncio]>=2.0.0,<3.0.0",
    "asyncpg>=0.29.0,<1.0.0",
    "alembic>=1.13.0,<2.0.0",
    "redis>=5.0.0,<6.0.0",
    "httpx>=0.26.0,<1.0.0",
    "python-jose[cryptography]>=3.3.0,<4.0.0",
    "passlib[bcrypt]>=1.7.0,<2.0.0",
{% if cookiecutter.include_observability == "yes" %}
    # Observability
    "opentelemetry-api>=1.27.0,<2.0.0",
    "opentelemetry-sdk>=1.27.0,<2.0.0",
    "opentelemetry-exporter-otlp-proto-grpc>=1.27.0,<2.0.0",
    "opentelemetry-instrumentation-fastapi>=0.48b0,<1.0.0",
    "prometheus-client>=0.20.0,<1.0.0",
{% endif %}
]
```

### TOML Formatting Considerations

**Critical**: The Jinja2 conditional must not break TOML array syntax.

**Valid pattern:**
```toml
dependencies = [
    "package-a>=1.0.0",
{% if cookiecutter.include_observability == "yes" %}
    "package-b>=1.0.0",
{% endif %}
]
```

This works because:
- Trailing commas are allowed in TOML arrays
- The conditional is on its own line
- The closing bracket remains on a separate line

**Invalid pattern (would break with observability=no):**
```toml
dependencies = [
    "package-a>=1.0.0"{% if cookiecutter.include_observability == "yes" %},
    "package-b>=1.0.0"{% endif %}
]
```

### Testing Dependency Resolution

After generation, verify:

1. **With observability:**
   ```bash
   cd backend
   pip install -e .
   python -c "from app.observability import setup_observability; print('OK')"
   ```

2. **Without observability:**
   ```bash
   cd backend
   pip install -e .
   # No observability module present, no import test needed
   ```

### Optional: Using pyproject.toml Optional Dependencies

Alternative approach using extras (not recommended for this case):

```toml
[project.optional-dependencies]
observability = [
    "opentelemetry-api>=1.27.0,<2.0.0",
    # ... other deps
]
```

This would require `pip install -e ".[observability]"` which is more complex for users.

**Recommendation**: Use conditional rendering for simpler user experience.

---

## Success Criteria

- [ ] Observability dependencies wrapped in Jinja2 conditional
- [ ] Generated pyproject.toml is valid TOML with "yes"
- [ ] Generated pyproject.toml is valid TOML with "no"
- [ ] No trailing comma issues in dependency array
- [ ] `pip install -e .` succeeds with observability enabled
- [ ] `pip install -e .` succeeds with observability disabled
- [ ] No import errors for core application without observability

---

## Integration Points

### Upstream
- **P4-01**: `include_observability` variable must be defined

### Contract: Dependency Versions

Match the versions specified in P2-01:

| Package | Version Constraint |
|---------|-------------------|
| opentelemetry-api | >=1.27.0,<2.0.0 |
| opentelemetry-sdk | >=1.27.0,<2.0.0 |
| opentelemetry-exporter-otlp-proto-grpc | >=1.27.0,<2.0.0 |
| opentelemetry-instrumentation-fastapi | >=0.48b0,<1.0.0 |
| prometheus-client | >=0.20.0,<1.0.0 |

---

## Monitoring/Observability

After implementation, verify:
- TOML syntax validation passes
- Dependency resolution succeeds
- No conflicts with existing dependencies

---

## Infrastructure Needs

None - template changes only.

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Adding conditional to pyproject.toml
- Testing TOML validity
- Verifying dependency installation
- Testing both generation paths
