# P5-03: Add Observability Validation Tests

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P5-03 |
| **Title** | Add Observability Validation Tests |
| **Domain** | Backend |
| **Complexity** | M (1-2 days) |
| **Dependencies** | P4-05 |
| **Blocks** | P5-04 |

---

## Scope

### Included
- Test template generation with observability enabled
- Test template generation with observability disabled
- Validate correct file presence/absence
- Test compose.yml validity
- Test pyproject.toml validity
- Test Python syntax validity

### Excluded
- Runtime integration tests (P5-04)
- Performance tests
- Load testing

---

## Relevant Code Areas

### Test Location
- Create tests in existing test structure or new location for template tests
- Consider `tests/template/` or `template/tests/`

---

## Implementation Details

### Test Categories

1. **Template Generation Tests**
   - Generate project with `include_observability: yes`
   - Generate project with `include_observability: no`
   - Verify correct files present/absent

2. **Configuration Validity Tests**
   - YAML validity for compose.yml
   - TOML validity for pyproject.toml
   - Python syntax validity for main.py and observability.py

3. **Content Validation Tests**
   - Correct port values substituted
   - No Jinja2 artifacts in generated files
   - All variables resolved

### Test Implementation

```python
"""
Template validation tests for observability feature.

Tests generation with and without observability to ensure
correct file presence/absence and configuration validity.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml
import tomllib  # Python 3.11+ or tomli for earlier versions


@pytest.fixture
def template_dir():
    """Path to the cookiecutter template."""
    return Path(__file__).parent.parent.parent / "template"


@pytest.fixture
def temp_output_dir():
    """Temporary directory for generated projects."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestObservabilityEnabled:
    """Tests for template generation with observability enabled."""

    @pytest.fixture
    def project_dir(self, template_dir, temp_output_dir):
        """Generate project with observability enabled."""
        result = subprocess.run(
            [
                "cookiecutter",
                str(template_dir),
                "--no-input",
                "-o", str(temp_output_dir),
                "project_name=Test Project",
                "include_observability=yes",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Generation failed: {result.stderr}"
        return temp_output_dir / "test-project"

    def test_observability_directory_exists(self, project_dir):
        """Observability directory should exist when enabled."""
        assert (project_dir / "observability").is_dir()

    def test_prometheus_config_exists(self, project_dir):
        """Prometheus configuration should exist."""
        prometheus_config = project_dir / "observability/prometheus/prometheus.yml"
        assert prometheus_config.exists()

        # Validate YAML
        with open(prometheus_config) as f:
            config = yaml.safe_load(f)
        assert "scrape_configs" in config

    def test_loki_config_exists(self, project_dir):
        """Loki configuration should exist."""
        loki_config = project_dir / "observability/loki/loki-config.yml"
        assert loki_config.exists()

    def test_promtail_config_exists(self, project_dir):
        """Promtail configuration should exist."""
        promtail_config = project_dir / "observability/promtail/promtail-config.yml"
        assert promtail_config.exists()

    def test_tempo_config_exists(self, project_dir):
        """Tempo configuration should exist."""
        tempo_config = project_dir / "observability/tempo/tempo.yml"
        assert tempo_config.exists()

    def test_grafana_datasources_exist(self, project_dir):
        """Grafana datasources configuration should exist."""
        datasources = project_dir / "observability/grafana/datasources/datasources.yml"
        assert datasources.exists()

    def test_grafana_dashboards_exist(self, project_dir):
        """Grafana dashboards should exist."""
        dashboards_dir = project_dir / "observability/grafana/dashboards"
        assert dashboards_dir.is_dir()
        assert (dashboards_dir / "dashboards.yml").exists()
        assert (dashboards_dir / "backend-dashboard.json").exists()

    def test_observability_module_exists(self, project_dir):
        """Backend observability module should exist."""
        module = project_dir / "backend/app/observability.py"
        assert module.exists()

        # Validate Python syntax
        result = subprocess.run(
            ["python", "-m", "py_compile", str(module)],
            capture_output=True,
        )
        assert result.returncode == 0, f"Invalid Python: {result.stderr}"

    def test_compose_has_observability_services(self, project_dir):
        """compose.yml should include observability services."""
        compose_file = project_dir / "compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        services = compose.get("services", {})
        assert "prometheus" in services
        assert "loki" in services
        assert "promtail" in services
        assert "tempo" in services
        assert "grafana" in services

    def test_compose_has_observability_volumes(self, project_dir):
        """compose.yml should include observability volumes."""
        compose_file = project_dir / "compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        volumes = compose.get("volumes", {})
        assert "prometheus-data" in volumes
        assert "loki-data" in volumes
        assert "tempo-data" in volumes
        assert "grafana-data" in volumes

    def test_backend_has_otel_env_vars(self, project_dir):
        """Backend service should have OTEL environment variables."""
        compose_file = project_dir / "compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        backend_env = compose["services"]["backend"].get("environment", {})
        assert "OTEL_SERVICE_NAME" in backend_env
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" in backend_env

    def test_pyproject_has_observability_deps(self, project_dir):
        """pyproject.toml should include observability dependencies."""
        pyproject_file = project_dir / "backend/pyproject.toml"
        with open(pyproject_file, "rb") as f:
            pyproject = tomllib.load(f)

        deps = pyproject.get("project", {}).get("dependencies", [])
        dep_names = [d.split(">")[0].split("<")[0].split("=")[0] for d in deps]

        assert "opentelemetry-api" in dep_names
        assert "opentelemetry-sdk" in dep_names
        assert "prometheus-client" in dep_names


class TestObservabilityDisabled:
    """Tests for template generation with observability disabled."""

    @pytest.fixture
    def project_dir(self, template_dir, temp_output_dir):
        """Generate project with observability disabled."""
        result = subprocess.run(
            [
                "cookiecutter",
                str(template_dir),
                "--no-input",
                "-o", str(temp_output_dir),
                "project_name=Test Project",
                "include_observability=no",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Generation failed: {result.stderr}"
        return temp_output_dir / "test-project"

    def test_observability_directory_not_exists(self, project_dir):
        """Observability directory should NOT exist when disabled."""
        assert not (project_dir / "observability").exists()

    def test_observability_module_not_exists(self, project_dir):
        """Backend observability module should NOT exist."""
        module = project_dir / "backend/app/observability.py"
        assert not module.exists()

    def test_compose_no_observability_services(self, project_dir):
        """compose.yml should NOT include observability services."""
        compose_file = project_dir / "compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        services = compose.get("services", {})
        assert "prometheus" not in services
        assert "loki" not in services
        assert "promtail" not in services
        assert "tempo" not in services
        assert "grafana" not in services

    def test_compose_no_observability_volumes(self, project_dir):
        """compose.yml should NOT include observability volumes."""
        compose_file = project_dir / "compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        volumes = compose.get("volumes", {})
        assert "prometheus-data" not in volumes
        assert "loki-data" not in volumes
        assert "tempo-data" not in volumes
        assert "grafana-data" not in volumes

    def test_backend_no_otel_env_vars(self, project_dir):
        """Backend service should NOT have OTEL environment variables."""
        compose_file = project_dir / "compose.yml"
        with open(compose_file) as f:
            compose = yaml.safe_load(f)

        backend_env = compose["services"]["backend"].get("environment", {})
        assert "OTEL_SERVICE_NAME" not in backend_env
        assert "OTEL_EXPORTER_OTLP_ENDPOINT" not in backend_env

    def test_pyproject_no_observability_deps(self, project_dir):
        """pyproject.toml should NOT include observability dependencies."""
        pyproject_file = project_dir / "backend/pyproject.toml"
        with open(pyproject_file, "rb") as f:
            pyproject = tomllib.load(f)

        deps = pyproject.get("project", {}).get("dependencies", [])
        dep_names = [d.split(">")[0].split("<")[0].split("=")[0] for d in deps]

        assert "opentelemetry-api" not in dep_names
        assert "opentelemetry-sdk" not in dep_names
        assert "prometheus-client" not in dep_names

    def test_main_py_valid_syntax(self, project_dir):
        """main.py should have valid Python syntax without observability."""
        main_file = project_dir / "backend/app/main.py"
        result = subprocess.run(
            ["python", "-m", "py_compile", str(main_file)],
            capture_output=True,
        )
        assert result.returncode == 0, f"Invalid Python: {result.stderr}"


class TestNoJinja2Artifacts:
    """Tests to ensure no Jinja2 artifacts in generated files."""

    @pytest.fixture(params=["yes", "no"])
    def project_dir(self, request, template_dir, temp_output_dir):
        """Generate project with both settings."""
        result = subprocess.run(
            [
                "cookiecutter",
                str(template_dir),
                "--no-input",
                "-o", str(temp_output_dir / request.param),
                "project_name=Test Project",
                f"include_observability={request.param}",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        return temp_output_dir / request.param / "test-project"

    def test_no_jinja2_in_compose(self, project_dir):
        """compose.yml should not contain Jinja2 artifacts."""
        compose_file = project_dir / "compose.yml"
        content = compose_file.read_text()
        assert "{{" not in content
        assert "{%" not in content
        assert "cookiecutter" not in content

    def test_no_jinja2_in_pyproject(self, project_dir):
        """pyproject.toml should not contain Jinja2 artifacts."""
        pyproject_file = project_dir / "backend/pyproject.toml"
        content = pyproject_file.read_text()
        assert "{{" not in content
        assert "{%" not in content
        assert "cookiecutter" not in content
```

---

## Success Criteria

- [ ] Tests pass for observability enabled configuration
- [ ] Tests pass for observability disabled configuration
- [ ] All file presence/absence tests pass
- [ ] All configuration validity tests pass
- [ ] No Jinja2 artifacts in generated files
- [ ] Python syntax valid in all generated Python files
- [ ] YAML valid in all generated YAML files
- [ ] TOML valid in generated pyproject.toml

---

## Integration Points

### Upstream
- **P4-05**: Conditional rendering must be complete

### Downstream
- **P5-04**: E2E tests build on validation tests

### Test Dependencies

Tests require:
- `pytest`
- `pyyaml`
- `tomllib` (Python 3.11+) or `tomli`
- `cookiecutter`

---

## Monitoring/Observability

Tests are the monitoring for this feature:
- CI runs tests on every PR
- Test failures indicate generation issues
- Coverage reports show tested paths

---

## Infrastructure Needs

**CI Integration:**
- Tests should run in CI pipeline
- Requires Docker for runtime tests (P5-04)
- May need matrix testing for Python versions

---

## Estimated Effort

**Time**: 4-8 hours

Includes:
- Writing test cases
- Setting up test fixtures
- Running tests for both configurations
- Fixing any issues found
- CI integration
