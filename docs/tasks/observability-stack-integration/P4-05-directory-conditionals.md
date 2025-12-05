# P4-05: Conditional Observability Directory Rendering

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P4-05 |
| **Title** | Conditional Observability Directory Rendering |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P4-01 |
| **Blocks** | P5-01, P5-03 |

---

## Scope

### Included
- Configure cookiecutter to conditionally render the observability directory
- Conditionally render the observability.py module
- Set up post-generation hooks if needed
- Ensure clean generation with and without observability

### Excluded
- Conditional rendering of other directories
- Runtime configuration changes

---

## Relevant Code Areas

### Files Affected
- `template/hooks/post_gen_project.py` (may need creation or modification)
- `template/{{cookiecutter.project_slug}}/observability/` (entire directory)
- `template/{{cookiecutter.project_slug}}/backend/app/observability.py`

---

## Implementation Details

### Approach Options

Cookiecutter doesn't natively support conditional directories. Two approaches:

**Option A: Post-Generation Hook (Recommended)**

Create/modify `template/hooks/post_gen_project.py`:

```python
#!/usr/bin/env python
"""Post-generation hook to clean up conditional files."""

import os
import shutil

# Read cookiecutter context
include_observability = "{{ cookiecutter.include_observability }}"

# Current directory is the generated project
project_dir = os.getcwd()

if include_observability.lower() != "yes":
    # Remove observability directory
    observability_dir = os.path.join(project_dir, "observability")
    if os.path.exists(observability_dir):
        shutil.rmtree(observability_dir)
        print("Removed observability/ directory")

    # Remove observability module
    observability_module = os.path.join(project_dir, "backend", "app", "observability.py")
    if os.path.exists(observability_module):
        os.remove(observability_module)
        print("Removed backend/app/observability.py")

    print("Observability stack disabled - related files removed")
else:
    print("Observability stack enabled")
```

**Option B: Jinja2 Extensions (Complex)**

Use cookiecutter-jinja2-extension for conditional directories.
Not recommended due to complexity and additional dependencies.

### Hook Implementation Steps

1. **Check for existing hooks directory:**
   ```
   template/hooks/
   ```

2. **Create or modify post_gen_project.py:**
   - Add observability cleanup logic
   - Preserve any existing hook functionality

3. **Test hook execution:**
   - Generate with `include_observability: yes`
   - Generate with `include_observability: no`
   - Verify correct files present/absent

### Full Hook Example

If a hook already exists, integrate with it:

```python
#!/usr/bin/env python
"""Post-generation project hook.

Handles:
- Conditional observability directory removal
- [Other existing functionality...]
"""

import os
import shutil


def remove_observability_files():
    """Remove observability-related files when disabled."""
    include_observability = "{{ cookiecutter.include_observability }}"

    if include_observability.lower() != "yes":
        project_dir = os.getcwd()

        # Remove observability directory tree
        observability_dir = os.path.join(project_dir, "observability")
        if os.path.exists(observability_dir):
            shutil.rmtree(observability_dir)
            print("  - Removed observability/ directory")

        # Remove backend observability module
        observability_module = os.path.join(
            project_dir, "backend", "app", "observability.py"
        )
        if os.path.exists(observability_module):
            os.remove(observability_module)
            print("  - Removed backend/app/observability.py")


def main():
    """Execute post-generation hooks."""
    print("Running post-generation hooks...")

    # Handle observability
    remove_observability_files()

    # [Other existing hook functions...]

    print("Post-generation complete!")


if __name__ == "__main__":
    main()
```

### Files to Remove When Disabled

| File/Directory | Path |
|----------------|------|
| Observability config directory | `observability/` |
| Prometheus config | `observability/prometheus/prometheus.yml` |
| Loki config | `observability/loki/loki-config.yml` |
| Promtail config | `observability/promtail/promtail-config.yml` |
| Tempo config | `observability/tempo/tempo.yml` |
| Grafana datasources | `observability/grafana/datasources/` |
| Grafana dashboards | `observability/grafana/dashboards/` |
| Observability README | `observability/README.md` |
| Backend observability module | `backend/app/observability.py` |

### Testing Checklist

**With observability enabled (`include_observability: yes`):**
- [ ] `observability/` directory exists
- [ ] All config files present
- [ ] `backend/app/observability.py` exists
- [ ] `docker compose up` starts all 10 services

**With observability disabled (`include_observability: no`):**
- [ ] `observability/` directory does NOT exist
- [ ] `backend/app/observability.py` does NOT exist
- [ ] No orphaned observability files
- [ ] `docker compose up` starts only 5 core services
- [ ] No errors about missing files or imports

---

## Success Criteria

- [ ] Post-generation hook properly removes observability files when disabled
- [ ] Hook preserves existing functionality (if any)
- [ ] Generated project with "yes" has all observability files
- [ ] Generated project with "no" has NO observability files
- [ ] No residual files or empty directories
- [ ] Hook runs without errors on Linux/macOS/Windows
- [ ] Clear output messages during generation

---

## Integration Points

### Upstream
- **P4-01**: `include_observability` variable must be defined

### Downstream
- **P5-01**: README describes observability as optional
- **P5-03**: Validation tests check for correct file presence/absence

### Contract: File Locations

The hook must know exact file locations:

```
observability/                    # Directory tree
backend/app/observability.py      # Python module
```

These paths are relative to the generated project root.

---

## Monitoring/Observability

After implementation, verify:
- Hook execution message appears during generation
- Correct files present/absent based on choice
- No errors during hook execution

---

## Infrastructure Needs

**Hook Requirements:**
- Python standard library only (os, shutil)
- No additional dependencies
- Works with Python 3.8+ (cookiecutter compatibility)

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Creating/modifying post-generation hook
- Testing on multiple platforms
- Verifying file cleanup
- Integration with existing hooks (if any)
