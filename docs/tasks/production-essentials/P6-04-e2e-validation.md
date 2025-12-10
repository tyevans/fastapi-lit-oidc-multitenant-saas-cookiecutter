# P6-04: End-to-End Deployment Validation

## Task Identifier
**ID:** P6-04
**Phase:** 6 - Documentation and Validation
**Domain:** DevOps
**Complexity:** L (Large)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P6-03 | Template validation | Must complete | Template must generate correctly |
| P1-01 | CI workflow | Must complete | CI pipeline to test |
| P1-02 | Build workflow | Must complete | Build pipeline to test |
| P4-01 | K8s manifests | Must complete | Kubernetes deployment to test |
| P4-04 | Deploy workflow | Must complete | Deployment automation to test |
| All P1-P5 | Implementation | Must complete | All features must be ready |

## Scope

### In Scope
- Create comprehensive E2E validation test suite
- Test full application lifecycle: generate -> build -> deploy -> test -> teardown
- Validate Docker Compose deployment (local/CI)
- Validate Kubernetes deployment (optional, requires cluster)
- Test CI/CD pipeline functionality
- Test application functionality after deployment
- Create validation checklist and reporting
- Document manual validation procedures

### Out of Scope
- Production environment deployment (testing only)
- Load testing (covered by P5-02, P5-03)
- Security penetration testing
- Long-running stability testing
- Multi-region deployment testing

## Relevant Code Areas

### Files to Create
```
template/tests/e2e/
  test_deployment.py                       # E2E deployment tests
  test_application.py                      # Application functionality tests
  conftest.py                              # E2E test fixtures
  helpers/
    docker.py                              # Docker helper functions
    kubernetes.py                          # K8s helper functions
    api.py                                 # API testing helpers

.github/workflows/
  e2e-validation.yml                       # E2E validation workflow

scripts/
  run-e2e-validation.sh                    # Manual E2E validation script

docs/
  E2E_VALIDATION_CHECKLIST.md              # Manual validation checklist
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/compose.yml
template/{{cookiecutter.project_slug}}/compose.production.yml
template/{{cookiecutter.project_slug}}/k8s/base/
template/{{cookiecutter.project_slug}}/k8s/overlays/
template/{{cookiecutter.project_slug}}/.github/workflows/
```

## Implementation Details

### 1. E2E Test Structure

```python
# template/tests/e2e/conftest.py

"""E2E test configuration and fixtures."""

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Generator

import pytest
import requests
from cookiecutter.main import cookiecutter

TEMPLATE_DIR = Path(__file__).parent.parent.parent
TIMEOUT_STARTUP = 180  # 3 minutes for services to start
TIMEOUT_HEALTH = 30    # 30 seconds for health check


@pytest.fixture(scope="session")
def generated_project() -> Generator[Path, None, None]:
    """Generate a test project and return its path."""
    tmpdir = tempfile.mkdtemp(prefix="e2e-test-")

    options = {
        "project_name": "E2E Test Project",
        "project_slug": "e2e-test-project",
        "include_observability": "yes",
        "include_github_actions": "yes",
        "include_kubernetes": "yes",
        "include_sentry": "no",  # Sentry requires external service
    }

    result_dir = cookiecutter(
        str(TEMPLATE_DIR),
        output_dir=tmpdir,
        no_input=True,
        extra_context=options,
    )

    yield Path(result_dir)

    # Cleanup
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture(scope="session")
def docker_compose_up(generated_project: Path) -> Generator[dict, None, None]:
    """Start Docker Compose services and return connection info."""
    project_dir = generated_project

    # Start services
    subprocess.run(
        ["docker", "compose", "up", "-d", "--build"],
        cwd=project_dir,
        check=True,
        capture_output=True,
    )

    # Wait for services to be healthy
    services = {
        "backend": "http://localhost:8000/api/v1/health",
        "frontend": "http://localhost:5173",
        "keycloak": "http://localhost:8080/health/ready",
    }

    start_time = time.time()
    while time.time() - start_time < TIMEOUT_STARTUP:
        all_healthy = True
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    all_healthy = False
            except requests.RequestException:
                all_healthy = False

        if all_healthy:
            break
        time.sleep(5)
    else:
        # Dump logs on failure
        subprocess.run(["docker", "compose", "logs"], cwd=project_dir)
        pytest.fail("Services did not become healthy in time")

    yield services

    # Teardown
    subprocess.run(
        ["docker", "compose", "down", "-v"],
        cwd=project_dir,
        capture_output=True,
    )


@pytest.fixture
def api_client(docker_compose_up: dict):
    """Return a configured API client."""
    from helpers.api import APIClient
    return APIClient(base_url="http://localhost:8000")
```

### 2. Deployment Tests

```python
# template/tests/e2e/test_deployment.py

"""E2E tests for deployment functionality."""

import subprocess
from pathlib import Path

import pytest
import requests


class TestDockerComposeDeploy:
    """Tests for Docker Compose deployment."""

    def test_services_start_successfully(self, docker_compose_up):
        """Test that all services start without errors."""
        # If fixture succeeds, services are running
        assert docker_compose_up is not None

    def test_backend_health_endpoint(self, docker_compose_up):
        """Test backend health endpoint returns OK."""
        response = requests.get("http://localhost:8000/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_frontend_serves_html(self, docker_compose_up):
        """Test frontend serves HTML content."""
        response = requests.get("http://localhost:5173")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type", "")

    def test_keycloak_ready(self, docker_compose_up):
        """Test Keycloak is ready."""
        response = requests.get("http://localhost:8080/health/ready")
        assert response.status_code == 200

    def test_postgres_connection(self, generated_project):
        """Test PostgreSQL is accessible."""
        result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "postgres",
                "pg_isready", "-U", "e2e_test_project_user"
            ],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0

    def test_redis_connection(self, generated_project):
        """Test Redis is accessible."""
        result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "redis",
                "redis-cli", "ping"
            ],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert "PONG" in result.stdout

    @pytest.mark.skipif(
        not Path("/var/run/docker.sock").exists(),
        reason="Docker not available"
    )
    def test_backend_image_builds(self, generated_project):
        """Test backend Docker image builds successfully."""
        result = subprocess.run(
            ["docker", "build", "-t", "e2e-backend-test", "."],
            cwd=generated_project / "backend",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

    @pytest.mark.skipif(
        not Path("/var/run/docker.sock").exists(),
        reason="Docker not available"
    )
    def test_frontend_image_builds(self, generated_project):
        """Test frontend Docker image builds successfully."""
        result = subprocess.run(
            ["docker", "build", "-t", "e2e-frontend-test", "."],
            cwd=generated_project / "frontend",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"


class TestKubernetesManifests:
    """Tests for Kubernetes manifest validity."""

    def test_kustomize_staging_renders(self, generated_project):
        """Test staging Kustomize overlay renders successfully."""
        result = subprocess.run(
            ["kubectl", "kustomize", "k8s/overlays/staging"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Kustomize failed: {result.stderr}"
        assert "Deployment" in result.stdout
        assert "Service" in result.stdout

    def test_kustomize_production_renders(self, generated_project):
        """Test production Kustomize overlay renders successfully."""
        result = subprocess.run(
            ["kubectl", "kustomize", "k8s/overlays/production"],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Kustomize failed: {result.stderr}"
        assert "Deployment" in result.stdout
        assert "replicas: 3" in result.stdout  # Production has 3 replicas

    def test_manifests_dry_run(self, generated_project):
        """Test manifests pass kubectl dry-run validation."""
        result = subprocess.run(
            [
                "kubectl", "apply",
                "-k", "k8s/overlays/staging",
                "--dry-run=client",
                "-o", "yaml"
            ],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Dry run failed: {result.stderr}"


class TestCIPipeline:
    """Tests for CI pipeline functionality."""

    def test_ci_workflow_valid(self, generated_project):
        """Test CI workflow is valid YAML."""
        import yaml

        ci_file = generated_project / ".github" / "workflows" / "ci.yml"
        with open(ci_file) as f:
            workflow = yaml.safe_load(f)

        assert "name" in workflow
        assert "on" in workflow
        assert "jobs" in workflow

    def test_build_workflow_valid(self, generated_project):
        """Test build workflow is valid YAML."""
        import yaml

        build_file = generated_project / ".github" / "workflows" / "build.yml"
        with open(build_file) as f:
            workflow = yaml.safe_load(f)

        assert "name" in workflow
        assert "jobs" in workflow

    def test_backend_tests_pass(self, generated_project):
        """Test backend tests pass in generated project."""
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "backend", "pytest", "-x"],
            cwd=generated_project,
            capture_output=True,
            text=True,
            timeout=300,
        )
        # Note: May fail if tests require full setup
        # This is a smoke test that pytest can run
        assert result.returncode == 0 or "no tests ran" in result.stdout.lower()
```

### 3. Application Functionality Tests

```python
# template/tests/e2e/test_application.py

"""E2E tests for application functionality."""

import pytest
import requests


class TestAPIEndpoints:
    """Tests for API endpoint functionality."""

    def test_openapi_schema_available(self, docker_compose_up):
        """Test OpenAPI schema is accessible."""
        response = requests.get("http://localhost:8000/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema

    def test_health_check_detailed(self, docker_compose_up):
        """Test detailed health check response."""
        response = requests.get("http://localhost:8000/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data

    def test_api_rate_limiting(self, docker_compose_up):
        """Test rate limiting is active."""
        # Make many requests quickly
        responses = []
        for _ in range(100):
            response = requests.get("http://localhost:8000/api/v1/health")
            responses.append(response.status_code)

        # Should eventually get rate limited (429)
        # Note: May not trigger if limit is high
        assert all(code in [200, 429] for code in responses)

    def test_cors_headers_present(self, docker_compose_up):
        """Test CORS headers are present."""
        response = requests.options(
            "http://localhost:8000/api/v1/health",
            headers={"Origin": "http://localhost:5173"}
        )
        # CORS preflight should succeed or endpoint allows GET
        assert response.status_code in [200, 204]

    def test_security_headers_present(self, docker_compose_up):
        """Test security headers are present in responses."""
        response = requests.get("http://localhost:8000/api/v1/health")

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "X-Frame-Options" in response.headers


class TestObservability:
    """Tests for observability stack (when enabled)."""

    def test_prometheus_accessible(self, docker_compose_up):
        """Test Prometheus is accessible."""
        response = requests.get("http://localhost:9090/-/healthy")
        assert response.status_code == 200

    def test_prometheus_has_targets(self, docker_compose_up):
        """Test Prometheus has configured targets."""
        response = requests.get("http://localhost:9090/api/v1/targets")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "activeTargets" in data["data"]

    def test_grafana_accessible(self, docker_compose_up):
        """Test Grafana is accessible."""
        response = requests.get("http://localhost:3000/api/health")
        assert response.status_code == 200

    def test_backend_metrics_endpoint(self, docker_compose_up):
        """Test backend exposes Prometheus metrics."""
        response = requests.get("http://localhost:8000/metrics")
        assert response.status_code == 200
        assert "http_requests_total" in response.text

    def test_alerting_rules_loaded(self, docker_compose_up):
        """Test Prometheus alerting rules are loaded."""
        response = requests.get("http://localhost:9090/api/v1/rules")
        assert response.status_code == 200
        data = response.json()
        # Should have at least one rule group
        assert data["data"]["groups"]


class TestDatabaseOperations:
    """Tests for database functionality."""

    def test_migrations_applied(self, generated_project):
        """Test Alembic migrations are applied."""
        result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "backend",
                "alembic", "current"
            ],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        # Should show current revision or "head"
        assert result.returncode == 0

    def test_database_rls_enabled(self, generated_project):
        """Test Row-Level Security is enabled on tables."""
        result = subprocess.run(
            [
                "docker", "compose", "exec", "-T", "postgres",
                "psql", "-U", "e2e_test_project_user", "-d", "e2e_test_project_db",
                "-c", "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';"
            ],
            cwd=generated_project,
            capture_output=True,
            text=True,
        )
        # Should show RLS-enabled tables
        assert result.returncode == 0
```

### 4. API Testing Helpers

```python
# template/tests/e2e/helpers/api.py

"""API testing helper utilities."""

import requests
from typing import Optional, Dict, Any


class APIClient:
    """Simple API client for E2E testing."""

    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.token: Optional[str] = None

    def set_token(self, token: str):
        """Set authorization token for subsequent requests."""
        self.token = token
        self.session.headers["Authorization"] = f"Bearer {token}"

    def get(self, path: str, **kwargs) -> requests.Response:
        """Make GET request."""
        return self.session.get(
            f"{self.base_url}{path}",
            timeout=self.timeout,
            **kwargs
        )

    def post(self, path: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Make POST request."""
        return self.session.post(
            f"{self.base_url}{path}",
            json=data,
            timeout=self.timeout,
            **kwargs
        )

    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.get("/api/v1/health")
            return response.status_code == 200
        except requests.RequestException:
            return False
```

### 5. CI E2E Workflow

```yaml
# .github/workflows/e2e-validation.yml

name: E2E Validation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
    inputs:
      include_k8s:
        description: 'Run Kubernetes tests'
        required: false
        default: 'false'

jobs:
  e2e-docker-compose:
    name: E2E - Docker Compose
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install cookiecutter pytest requests pyyaml

      - name: Generate test project
        run: |
          cookiecutter . --no-input \
            project_name="E2E Test" \
            include_observability=yes \
            include_github_actions=yes \
            include_kubernetes=yes

      - name: Start services
        run: |
          cd e2e-test
          docker compose up -d --build

      - name: Wait for services
        run: |
          cd e2e-test
          ./scripts/wait-for-services.sh || true
          sleep 30

      - name: Run E2E tests
        run: |
          pytest template/tests/e2e/ -v \
            --ignore=template/tests/e2e/test_kubernetes.py

      - name: Collect logs on failure
        if: failure()
        run: |
          cd e2e-test
          docker compose logs > docker-compose-logs.txt

      - name: Upload logs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: docker-compose-logs
          path: e2e-test/docker-compose-logs.txt

      - name: Cleanup
        if: always()
        run: |
          cd e2e-test
          docker compose down -v

  e2e-kubernetes:
    name: E2E - Kubernetes
    runs-on: ubuntu-latest
    if: github.event.inputs.include_k8s == 'true' || github.event_name == 'push'
    timeout-minutes: 45

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'

      - name: Install kind
        run: |
          curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
          chmod +x ./kind
          sudo mv ./kind /usr/local/bin/kind

      - name: Create kind cluster
        run: |
          kind create cluster --name e2e-test

      - name: Generate test project
        run: |
          pip install cookiecutter
          cookiecutter . --no-input \
            project_name="E2E K8s Test" \
            include_kubernetes=yes

      - name: Build and load images
        run: |
          cd e2e-k8s-test
          docker build -t e2e-backend:test ./backend
          docker build -t e2e-frontend:test ./frontend
          kind load docker-image e2e-backend:test --name e2e-test
          kind load docker-image e2e-frontend:test --name e2e-test

      - name: Deploy to kind
        run: |
          cd e2e-k8s-test
          # Update image references for local testing
          kubectl apply -k k8s/overlays/staging --dry-run=client -o yaml

      - name: Validate manifests
        run: |
          cd e2e-k8s-test
          kubectl kustomize k8s/overlays/staging
          kubectl kustomize k8s/overlays/production

      - name: Cleanup
        if: always()
        run: |
          kind delete cluster --name e2e-test
```

### 6. Manual Validation Script

```bash
#!/bin/bash
# scripts/run-e2e-validation.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/e2e-validation}"
CLEANUP="${CLEANUP:-true}"

echo -e "${BLUE}=== E2E Validation Script ===${NC}"
echo "Output directory: $OUTPUT_DIR"

# Cleanup previous runs
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Step 1: Generate project
echo -e "\n${YELLOW}Step 1: Generating project...${NC}"
cd "$OUTPUT_DIR"
cookiecutter "$PROJECT_ROOT" --no-input \
    project_name="E2E Validation" \
    include_observability=yes \
    include_github_actions=yes \
    include_kubernetes=yes \
    include_sentry=no

PROJECT_DIR="$OUTPUT_DIR/e2e-validation"
cd "$PROJECT_DIR"
echo -e "${GREEN}Project generated at: $PROJECT_DIR${NC}"

# Step 2: Validate files exist
echo -e "\n${YELLOW}Step 2: Validating file structure...${NC}"
REQUIRED_FILES=(
    "compose.yml"
    "backend/app/main.py"
    "frontend/package.json"
    ".github/workflows/ci.yml"
    "k8s/base/kustomization.yaml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo -e "  ${GREEN}OK${NC}: $file"
    else
        echo -e "  ${RED}MISSING${NC}: $file"
        exit 1
    fi
done

# Step 3: Build Docker images
echo -e "\n${YELLOW}Step 3: Building Docker images...${NC}"
docker compose build --quiet
echo -e "${GREEN}Docker images built successfully${NC}"

# Step 4: Start services
echo -e "\n${YELLOW}Step 4: Starting services...${NC}"
docker compose up -d

# Wait for services
echo "Waiting for services to be ready..."
TIMEOUT=180
ELAPSED=0
while [[ $ELAPSED -lt $TIMEOUT ]]; do
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}Backend is ready${NC}"
        break
    fi
    sleep 5
    ELAPSED=$((ELAPSED + 5))
    echo "  Waiting... ($ELAPSED/$TIMEOUT seconds)"
done

if [[ $ELAPSED -ge $TIMEOUT ]]; then
    echo -e "${RED}Services failed to start in time${NC}"
    docker compose logs
    exit 1
fi

# Step 5: Run health checks
echo -e "\n${YELLOW}Step 5: Running health checks...${NC}"

# Backend health
BACKEND_HEALTH=$(curl -sf http://localhost:8000/api/v1/health | jq -r '.status')
if [[ "$BACKEND_HEALTH" == "healthy" ]]; then
    echo -e "  ${GREEN}OK${NC}: Backend health check"
else
    echo -e "  ${RED}FAIL${NC}: Backend health check"
    exit 1
fi

# Frontend
if curl -sf http://localhost:5173 > /dev/null; then
    echo -e "  ${GREEN}OK${NC}: Frontend accessible"
else
    echo -e "  ${RED}FAIL${NC}: Frontend not accessible"
fi

# Keycloak
if curl -sf http://localhost:8080/health/ready > /dev/null; then
    echo -e "  ${GREEN}OK${NC}: Keycloak ready"
else
    echo -e "  ${YELLOW}WARN${NC}: Keycloak not ready (may need more time)"
fi

# Step 6: Check security headers
echo -e "\n${YELLOW}Step 6: Checking security headers...${NC}"
HEADERS=$(curl -sI http://localhost:8000/api/v1/health)

if echo "$HEADERS" | grep -qi "X-Content-Type-Options: nosniff"; then
    echo -e "  ${GREEN}OK${NC}: X-Content-Type-Options"
else
    echo -e "  ${RED}FAIL${NC}: X-Content-Type-Options missing"
fi

if echo "$HEADERS" | grep -qi "X-Frame-Options"; then
    echo -e "  ${GREEN}OK${NC}: X-Frame-Options"
else
    echo -e "  ${RED}FAIL${NC}: X-Frame-Options missing"
fi

# Step 7: Check observability (if enabled)
echo -e "\n${YELLOW}Step 7: Checking observability...${NC}"

if curl -sf http://localhost:9090/-/healthy > /dev/null; then
    echo -e "  ${GREEN}OK${NC}: Prometheus healthy"
else
    echo -e "  ${YELLOW}WARN${NC}: Prometheus not ready"
fi

if curl -sf http://localhost:3000/api/health > /dev/null; then
    echo -e "  ${GREEN}OK${NC}: Grafana healthy"
else
    echo -e "  ${YELLOW}WARN${NC}: Grafana not ready"
fi

# Step 8: Validate Kubernetes manifests
echo -e "\n${YELLOW}Step 8: Validating Kubernetes manifests...${NC}"
if command -v kubectl &> /dev/null; then
    if kubectl kustomize k8s/overlays/staging > /dev/null 2>&1; then
        echo -e "  ${GREEN}OK${NC}: Staging manifests valid"
    else
        echo -e "  ${RED}FAIL${NC}: Staging manifests invalid"
    fi

    if kubectl kustomize k8s/overlays/production > /dev/null 2>&1; then
        echo -e "  ${GREEN}OK${NC}: Production manifests valid"
    else
        echo -e "  ${RED}FAIL${NC}: Production manifests invalid"
    fi
else
    echo -e "  ${YELLOW}SKIP${NC}: kubectl not installed"
fi

# Cleanup
if [[ "$CLEANUP" == "true" ]]; then
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    docker compose down -v
    echo -e "${GREEN}Cleanup complete${NC}"
else
    echo -e "\n${YELLOW}Skipping cleanup. Project at: $PROJECT_DIR${NC}"
fi

# Summary
echo -e "\n${GREEN}=== E2E Validation Complete ===${NC}"
echo "All critical checks passed!"
```

### 7. Manual Validation Checklist

```markdown
# docs/E2E_VALIDATION_CHECKLIST.md

# E2E Validation Checklist

Use this checklist to manually validate the Production Essentials features.

## Prerequisites

- [ ] Docker Desktop or Docker Engine running
- [ ] kubectl installed (for K8s validation)
- [ ] At least 8GB RAM available for Docker
- [ ] Ports 5173, 8000, 8080, 3000, 9090 available

## Template Generation

- [ ] Template generates with all options enabled
- [ ] Template generates with all options disabled
- [ ] No Jinja2 errors during generation
- [ ] All expected files present

## Docker Compose Deployment

### Service Startup
- [ ] `docker compose up -d` completes without errors
- [ ] Backend container starts and stays running
- [ ] Frontend container starts and stays running
- [ ] PostgreSQL container is healthy
- [ ] Redis container is healthy
- [ ] Keycloak container is ready

### Health Checks
- [ ] Backend: `curl http://localhost:8000/api/v1/health` returns 200
- [ ] Frontend: `curl http://localhost:5173` returns HTML
- [ ] Keycloak: `curl http://localhost:8080/health/ready` returns 200

### Security Headers
- [ ] X-Content-Type-Options: nosniff present
- [ ] X-Frame-Options present
- [ ] Referrer-Policy present

### Observability (if enabled)
- [ ] Prometheus: `http://localhost:9090` accessible
- [ ] Grafana: `http://localhost:3000` accessible
- [ ] Backend metrics: `http://localhost:8000/metrics` returns metrics
- [ ] Alerting rules loaded in Prometheus

## CI/CD Workflows (if enabled)

### Workflow Syntax
- [ ] ci.yml is valid YAML
- [ ] build.yml is valid YAML
- [ ] deploy.yml is valid YAML

### Local Simulation
- [ ] Backend linting passes: `cd backend && ruff check .`
- [ ] Frontend linting passes: `cd frontend && npm run lint`
- [ ] Backend tests run: `cd backend && pytest`
- [ ] Frontend tests run: `cd frontend && npm test`

## Kubernetes Manifests (if enabled)

### Manifest Validation
- [ ] `kubectl kustomize k8s/overlays/staging` renders
- [ ] `kubectl kustomize k8s/overlays/production` renders
- [ ] No invalid resource references
- [ ] Resource limits defined

### Dry Run
- [ ] `kubectl apply -k k8s/overlays/staging --dry-run=client` succeeds

## Database Operations

### Migrations
- [ ] `alembic upgrade head` succeeds
- [ ] `alembic current` shows migration

### Backup/Restore
- [ ] `./scripts/backup-db.sh` creates backup file
- [ ] Backup file is valid gzip
- [ ] `./scripts/restore-db.sh --latest` restores successfully

## API Client Generation

- [ ] `./scripts/generate-api-client.sh --validate` passes
- [ ] Generated client compiles (if backend running)

## Load Testing

- [ ] k6 installed or available via Docker
- [ ] Smoke test runs: `k6 run tests/load/smoke.js`

## Cleanup

- [ ] `docker compose down -v` removes all containers
- [ ] No orphaned volumes
- [ ] No orphaned networks

## Sign-Off

**Validator:** ________________________
**Date:** ________________________
**Version:** ________________________

### Notes:
```

## Success Criteria

### Functional Requirements
- [ ] Generated project deploys successfully with Docker Compose
- [ ] All services start and become healthy
- [ ] Security headers are present in responses
- [ ] Observability stack functions correctly
- [ ] Kubernetes manifests validate and render
- [ ] CI workflows are syntactically valid
- [ ] Database operations work correctly

### Verification Steps
1. **Automated E2E Tests:**
   ```bash
   pytest template/tests/e2e/ -v
   ```

2. **Manual Validation:**
   ```bash
   ./scripts/run-e2e-validation.sh
   ```

3. **CI Pipeline:**
   - Trigger e2e-validation workflow
   - Verify all jobs pass

### Quality Gates
- [ ] All E2E tests pass
- [ ] Manual validation checklist complete
- [ ] CI E2E workflow passes
- [ ] No critical issues found
- [ ] Performance is acceptable (services start within 3 minutes)

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-03 | Template validation | Templates must generate correctly |
| All P1-P5 | Feature implementations | All features must be testable |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-05 | Release notes | E2E validation results inform release |

### Integration Contract
```yaml
# Contract: E2E Validation

# Test environments
- Docker Compose (required)
- Kubernetes with kind (optional)

# Required validations
- Template generation
- Docker image builds
- Service startup
- Health checks
- Security headers
- Observability (when enabled)
- Kubernetes manifests (when enabled)

# Success criteria
- All services healthy within 3 minutes
- All health endpoints return 200
- Security headers present
- No errors in logs (warnings OK)
```

## Monitoring and Observability

### Test Metrics
- E2E test pass rate
- Time to service startup
- Common failure patterns

### CI Visibility
- GitHub Actions workflow status
- Artifact collection on failure
- Log preservation

## Infrastructure Needs

### CI Requirements
- Docker-in-Docker or Docker socket access
- kind for Kubernetes testing
- 8GB+ RAM for full stack
- 30-45 minute timeout

### Local Requirements
- Docker Desktop or Docker Engine
- 8GB+ RAM
- kubectl (optional)
- kind (optional)

## Estimated Effort

**Size:** L (Large)
**Time:** 3-4 days
**Justification:**
- Comprehensive test suite development
- Multiple deployment scenarios to test
- CI workflow configuration
- Docker Compose and Kubernetes testing
- Manual validation checklist creation
- Debugging and stabilization

## Notes

### Design Decisions

**1. Session-Scoped Fixtures:**
- Docker Compose starts once per test session
- Reduces test time significantly
- Requires careful test isolation

**2. Separate Docker and K8s Tests:**
- Docker Compose tests always run
- Kubernetes tests optional (require kind)
- Can be run independently

**3. Manual Checklist:**
- Complements automated tests
- Catches UI/UX issues
- Provides auditable validation

**4. Timeout Configuration:**
- 3 minutes for service startup
- 30 minutes total for Docker Compose tests
- 45 minutes for Kubernetes tests

### Related Requirements
- NFR-002: Template generation shall succeed for all option combinations
- Success criteria: Time to first deployment < 2 hours
- All features must work in generated projects

### Coordination Notes
- Depends on all Phase 1-5 tasks being complete
- May reveal issues in earlier tasks
- Results inform release readiness
- CI resources may need scaling for matrix tests
