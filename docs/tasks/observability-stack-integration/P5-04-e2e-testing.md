# P5-04: End-to-End Integration Testing

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P5-04 |
| **Title** | End-to-End Integration Testing |
| **Domain** | DevOps |
| **Complexity** | M (1-2 days) |
| **Dependencies** | P5-03 |
| **Blocks** | None (end of Phase 5) |

---

## Scope

### Included
- Full stack startup test with observability
- Verify service health and connectivity
- Test metrics endpoint functionality
- Test trace export to Tempo
- Test log aggregation in Loki
- Verify Grafana datasource connectivity
- Test graceful degradation scenarios

### Excluded
- Performance/load testing
- Security testing
- Production deployment testing

---

## Relevant Code Areas

### Test Location
- Integration tests requiring Docker
- Consider `tests/integration/` or similar

---

## Implementation Details

### Test Categories

1. **Stack Startup Tests**
   - All 10 services start successfully
   - Health checks pass for all services
   - Services are reachable on expected ports

2. **Metrics Pipeline Tests**
   - Backend exposes `/metrics` endpoint
   - Prometheus scrapes backend metrics
   - Metrics appear in Prometheus queries

3. **Logging Pipeline Tests**
   - Backend logs appear in Loki
   - Log labels are correctly applied
   - LogQL queries return expected results

4. **Tracing Pipeline Tests**
   - Traces are exported to Tempo
   - Trace queries return results
   - Service name appears in traces

5. **Grafana Integration Tests**
   - Datasources are healthy
   - Dashboard loads without errors
   - Dashboard panels show data

6. **Graceful Degradation Tests**
   - Backend continues when Tempo unavailable
   - Backend continues when Prometheus down
   - Application functions without observability

### Test Implementation

```python
"""
End-to-end integration tests for observability stack.

These tests require Docker and may take several minutes to complete.
Run with: pytest tests/integration/test_observability_e2e.py -v
"""

import os
import subprocess
import time
from pathlib import Path

import pytest
import requests


# Increase timeout for CI environments
STARTUP_TIMEOUT = 120  # seconds
HEALTH_CHECK_INTERVAL = 5  # seconds


@pytest.fixture(scope="module")
def generated_project(tmp_path_factory):
    """Generate a test project with observability enabled."""
    output_dir = tmp_path_factory.mktemp("project")
    template_dir = Path(__file__).parent.parent.parent / "template"

    result = subprocess.run(
        [
            "cookiecutter",
            str(template_dir),
            "--no-input",
            "-o", str(output_dir),
            "project_name=E2E Test Project",
            "include_observability=yes",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Generation failed: {result.stderr}"

    return output_dir / "e2e-test-project"


@pytest.fixture(scope="module")
def docker_compose_up(generated_project):
    """Start Docker Compose stack and wait for services."""
    # Start all services
    result = subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=generated_project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"docker compose up failed: {result.stderr}"

    # Wait for all services to be healthy
    start_time = time.time()
    services_healthy = False

    while time.time() - start_time < STARTUP_TIMEOUT:
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )

        # Check if all services are healthy
        # (Implementation depends on output format)
        if _all_services_healthy(result.stdout):
            services_healthy = True
            break

        time.sleep(HEALTH_CHECK_INTERVAL)

    if not services_healthy:
        # Print logs for debugging
        subprocess.run(
            ["docker", "compose", "logs"],
            cwd=generated_project,
        )
        pytest.fail("Services did not become healthy within timeout")

    yield

    # Cleanup
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        cwd=generated_project,
        capture_output=True,
    )


def _all_services_healthy(compose_ps_output):
    """Check if all services are healthy from docker compose ps output."""
    # Simple check - may need adjustment based on output format
    return "unhealthy" not in compose_ps_output and "starting" not in compose_ps_output


class TestStackStartup:
    """Tests for observability stack startup."""

    def test_backend_is_healthy(self, docker_compose_up):
        """Backend service should be healthy."""
        response = requests.get("http://localhost:8000/api/v1/health")
        assert response.status_code == 200

    def test_grafana_is_healthy(self, docker_compose_up):
        """Grafana should be healthy."""
        response = requests.get("http://localhost:3000/api/health")
        assert response.status_code == 200

    def test_prometheus_is_healthy(self, docker_compose_up):
        """Prometheus should be healthy."""
        response = requests.get("http://localhost:9090/-/healthy")
        assert response.status_code == 200

    def test_loki_is_healthy(self, docker_compose_up):
        """Loki should be ready."""
        response = requests.get("http://localhost:3100/ready")
        assert response.status_code == 200

    def test_tempo_is_healthy(self, docker_compose_up):
        """Tempo should be ready."""
        response = requests.get("http://localhost:3200/ready")
        assert response.status_code == 200


class TestMetricsPipeline:
    """Tests for metrics collection pipeline."""

    def test_backend_exposes_metrics(self, docker_compose_up):
        """Backend should expose Prometheus metrics."""
        response = requests.get("http://localhost:8000/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text
        assert "http_request_duration_seconds" in response.text

    def test_prometheus_scrapes_backend(self, docker_compose_up):
        """Prometheus should successfully scrape backend."""
        # Wait a bit for scrape to occur
        time.sleep(10)

        response = requests.get(
            "http://localhost:9090/api/v1/targets",
        )
        assert response.status_code == 200
        data = response.json()

        # Find backend target
        backend_target = None
        for target in data.get("data", {}).get("activeTargets", []):
            if target.get("labels", {}).get("job") == "backend":
                backend_target = target
                break

        assert backend_target is not None, "Backend target not found"
        assert backend_target["health"] == "up", "Backend target not healthy"

    def test_metrics_queryable(self, docker_compose_up):
        """Should be able to query backend metrics from Prometheus."""
        # Make some requests to generate metrics
        for _ in range(5):
            requests.get("http://localhost:8000/api/v1/health")

        time.sleep(10)  # Wait for scrape

        response = requests.get(
            "http://localhost:9090/api/v1/query",
            params={"query": 'http_requests_total{job="backend"}'},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["data"]["result"]) > 0


class TestLoggingPipeline:
    """Tests for log aggregation pipeline."""

    def test_backend_logs_in_loki(self, docker_compose_up):
        """Backend logs should appear in Loki."""
        # Generate some log entries
        for _ in range(5):
            requests.get("http://localhost:8000/api/v1/health")

        time.sleep(10)  # Wait for log propagation

        response = requests.get(
            "http://localhost:3100/loki/api/v1/query_range",
            params={
                "query": '{service="backend"}',
                "limit": "10",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Should have some log entries
        assert len(data["data"]["result"]) > 0


class TestTracingPipeline:
    """Tests for distributed tracing pipeline."""

    def test_traces_in_tempo(self, docker_compose_up):
        """Traces should appear in Tempo."""
        # Generate some traces
        for _ in range(5):
            requests.get("http://localhost:8000/api/v1/health")

        time.sleep(15)  # Wait for trace export and processing

        # Search for traces from backend service
        response = requests.get(
            "http://localhost:3200/api/search",
            params={"tags": "service.name=backend"},
        )
        assert response.status_code == 200
        data = response.json()
        # Should have some traces
        assert len(data.get("traces", [])) > 0


class TestGrafanaIntegration:
    """Tests for Grafana datasource and dashboard integration."""

    def test_prometheus_datasource_healthy(self, docker_compose_up):
        """Prometheus datasource should be healthy in Grafana."""
        response = requests.get(
            "http://localhost:3000/api/datasources/uid/prometheus",
        )
        assert response.status_code == 200

    def test_loki_datasource_healthy(self, docker_compose_up):
        """Loki datasource should be healthy in Grafana."""
        response = requests.get(
            "http://localhost:3000/api/datasources/uid/loki",
        )
        assert response.status_code == 200

    def test_tempo_datasource_healthy(self, docker_compose_up):
        """Tempo datasource should be healthy in Grafana."""
        response = requests.get(
            "http://localhost:3000/api/datasources/uid/tempo",
        )
        assert response.status_code == 200

    def test_backend_dashboard_exists(self, docker_compose_up):
        """Backend service dashboard should be provisioned."""
        response = requests.get(
            "http://localhost:3000/api/dashboards/uid/backend-service",
        )
        assert response.status_code == 200


class TestGracefulDegradation:
    """Tests for graceful degradation when observability services fail."""

    def test_backend_works_without_tempo(self, docker_compose_up, generated_project):
        """Backend should continue working when Tempo is stopped."""
        # Stop Tempo
        subprocess.run(
            ["docker", "compose", "stop", "tempo"],
            cwd=generated_project,
            capture_output=True,
        )

        time.sleep(5)

        # Backend should still respond
        response = requests.get("http://localhost:8000/api/v1/health")
        assert response.status_code == 200

        # Restart Tempo
        subprocess.run(
            ["docker", "compose", "start", "tempo"],
            cwd=generated_project,
            capture_output=True,
        )

    def test_backend_works_without_prometheus(self, docker_compose_up, generated_project):
        """Backend should continue working when Prometheus is stopped."""
        # Stop Prometheus
        subprocess.run(
            ["docker", "compose", "stop", "prometheus"],
            cwd=generated_project,
            capture_output=True,
        )

        time.sleep(5)

        # Backend should still respond
        response = requests.get("http://localhost:8000/api/v1/health")
        assert response.status_code == 200

        # Metrics endpoint should still work
        response = requests.get("http://localhost:8000/metrics")
        assert response.status_code == 200

        # Restart Prometheus
        subprocess.run(
            ["docker", "compose", "start", "prometheus"],
            cwd=generated_project,
            capture_output=True,
        )
```

---

## Success Criteria

- [ ] All 10 services start and pass health checks
- [ ] Backend /metrics endpoint returns valid Prometheus format
- [ ] Prometheus successfully scrapes backend metrics
- [ ] Backend logs appear in Loki via Promtail
- [ ] Traces from backend appear in Tempo
- [ ] All Grafana datasources are healthy
- [ ] Backend dashboard is provisioned and loads
- [ ] Backend continues functioning when observability services fail
- [ ] Tests are reproducible in CI environment

---

## Integration Points

### Upstream
- **P5-03**: Validation tests should pass first

### Contract: Health Endpoints

| Service | Health Endpoint | Expected Status |
|---------|----------------|-----------------|
| Backend | /api/v1/health | 200 |
| Grafana | /api/health | 200 |
| Prometheus | /-/healthy | 200 |
| Loki | /ready | 200 |
| Tempo | /ready | 200 |

---

## Monitoring/Observability

Tests themselves validate observability functionality:
- Metrics collection works
- Log aggregation works
- Trace collection works
- Grafana integration works

---

## Infrastructure Needs

**Docker Requirements:**
- Docker Compose V2
- Sufficient memory (4GB+ recommended)
- Available ports: 3000, 3100, 3200, 4317, 4318, 5173, 5432, 6379, 8000, 8080, 9090

**CI Requirements:**
- Docker-in-Docker or Docker socket access
- Extended timeout (5+ minutes)
- Network isolation for port conflicts

---

## Estimated Effort

**Time**: 4-8 hours

Includes:
- Writing E2E test cases
- Setting up Docker fixtures
- Running and debugging tests
- CI integration
- Handling timing/flakiness issues
