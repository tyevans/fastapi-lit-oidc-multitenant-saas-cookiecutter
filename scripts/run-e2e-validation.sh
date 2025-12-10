#!/bin/bash
# E2E Deployment Validation Script
# Validates the full deployment lifecycle: generate -> build -> deploy -> test -> teardown
#
# Usage:
#   ./scripts/run-e2e-validation.sh                      # Run full validation
#   CLEANUP=false ./scripts/run-e2e-validation.sh        # Keep output for debugging
#   SKIP_DOCKER=true ./scripts/run-e2e-validation.sh     # Skip Docker builds (faster)
#   SKIP_K8S=true ./scripts/run-e2e-validation.sh        # Skip Kubernetes validation
#
# Requirements:
#   - cookiecutter (pip install cookiecutter)
#   - Docker and Docker Compose
#   - kubectl (optional, for K8s validation)
#   - curl, jq

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TEMPLATE_DIR="$PROJECT_ROOT/template"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/e2e-validation}"
CLEANUP="${CLEANUP:-true}"
SKIP_DOCKER="${SKIP_DOCKER:-false}"
SKIP_K8S="${SKIP_K8S:-false}"
TIMEOUT_STARTUP="${TIMEOUT_STARTUP:-180}"
VERBOSE="${VERBOSE:-false}"

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

# Logging functions
log_header() {
    echo -e "\n${CYAN}============================================${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}============================================${NC}"
}

log_step() {
    echo -e "\n${YELLOW}>>> Step $1: $2${NC}"
}

log_pass() {
    echo -e "  ${GREEN}[PASS]${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "  ${RED}[FAIL]${NC} $1"
    ((TESTS_FAILED++))
}

log_skip() {
    echo -e "  ${MAGENTA}[SKIP]${NC} $1"
    ((TESTS_SKIPPED++))
}

log_info() {
    echo -e "  ${BLUE}[INFO]${NC} $1"
}

log_warn() {
    echo -e "  ${YELLOW}[WARN]${NC} $1"
}

# Check requirements
check_requirements() {
    log_header "Checking Requirements"

    local missing=()

    if ! command -v cookiecutter &> /dev/null; then
        missing+=("cookiecutter")
    else
        log_pass "cookiecutter installed"
    fi

    if ! command -v docker &> /dev/null; then
        missing+=("docker")
    else
        log_pass "docker installed"
    fi

    if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
        missing+=("docker-compose")
    else
        log_pass "docker compose installed"
    fi

    if ! command -v curl &> /dev/null; then
        missing+=("curl")
    else
        log_pass "curl installed"
    fi

    if ! command -v jq &> /dev/null; then
        log_warn "jq not installed (optional, some checks may be limited)"
    else
        log_pass "jq installed"
    fi

    if command -v kubectl &> /dev/null; then
        log_pass "kubectl installed"
    else
        log_info "kubectl not installed (Kubernetes validation will be skipped)"
        SKIP_K8S=true
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "\n${RED}Missing required tools: ${missing[*]}${NC}"
        echo "Install with:"
        echo "  pip install cookiecutter"
        echo "  Install Docker from https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Check Docker daemon
    if ! docker info &> /dev/null; then
        echo -e "${RED}Docker daemon is not running${NC}"
        exit 1
    fi
    log_pass "Docker daemon is running"
}

# Clean up function
cleanup() {
    if [ "$CLEANUP" = "true" ]; then
        log_info "Cleaning up..."
        if [ -d "$PROJECT_DIR" ]; then
            cd "$PROJECT_DIR" 2>/dev/null && docker compose down -v 2>/dev/null || true
        fi
        rm -rf "$OUTPUT_DIR"
        log_info "Cleanup complete"
    else
        log_info "Skipping cleanup. Project at: $PROJECT_DIR"
    fi
}

# Set up trap for cleanup on exit
trap cleanup EXIT

# Step 1: Generate project
generate_project() {
    log_step "1" "Generating Project"

    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"

    cd "$OUTPUT_DIR"

    if cookiecutter "$TEMPLATE_DIR" --no-input \
        project_name="E2E Validation" \
        project_slug="e2e-validation" \
        author_name="E2E Test" \
        author_email="e2e@example.com" \
        github_username="e2e-test" \
        include_observability=yes \
        include_github_actions=yes \
        include_kubernetes=yes \
        include_sentry=no 2>&1; then
        log_pass "Project generated successfully"
    else
        log_fail "Project generation failed"
        exit 1
    fi

    PROJECT_DIR="$OUTPUT_DIR/e2e-validation"

    if [ ! -d "$PROJECT_DIR" ]; then
        log_fail "Project directory not created"
        exit 1
    fi

    log_info "Project location: $PROJECT_DIR"
}

# Step 2: Validate file structure
validate_file_structure() {
    log_step "2" "Validating File Structure"

    cd "$PROJECT_DIR"

    local required_files=(
        "compose.yml"
        "backend/app/main.py"
        "backend/app/core/config.py"
        "backend/pyproject.toml"
        "frontend/package.json"
        "frontend/src/main.ts"
        ".github/workflows/ci.yml"
        ".github/workflows/build.yml"
        "k8s/base/kustomization.yaml"
        "observability/prometheus/prometheus.yml"
    )

    for file in "${required_files[@]}"; do
        if [ -f "$file" ] || [ -d "$file" ]; then
            log_pass "Found: $file"
        else
            log_fail "Missing: $file"
        fi
    done
}

# Step 3: Validate Python syntax
validate_python_syntax() {
    log_step "3" "Validating Python Syntax"

    cd "$PROJECT_DIR"

    local errors=0
    while IFS= read -r -d '' pyfile; do
        if python -m py_compile "$pyfile" 2>/dev/null; then
            [ "$VERBOSE" = "true" ] && log_info "OK: $pyfile"
        else
            log_fail "Syntax error: $pyfile"
            ((errors++))
        fi
    done < <(find backend -name "*.py" -type f -print0)

    if [ $errors -eq 0 ]; then
        log_pass "All Python files have valid syntax"
    fi
}

# Step 4: Validate YAML syntax
validate_yaml_syntax() {
    log_step "4" "Validating YAML Syntax"

    cd "$PROJECT_DIR"

    local errors=0
    while IFS= read -r -d '' yamlfile; do
        if python -c "import yaml; yaml.safe_load(open('$yamlfile'))" 2>/dev/null; then
            [ "$VERBOSE" = "true" ] && log_info "OK: $yamlfile"
        else
            log_fail "YAML error: $yamlfile"
            ((errors++))
        fi
    done < <(find . -name "*.yml" -o -name "*.yaml" -type f 2>/dev/null | grep -v node_modules | tr '\n' '\0')

    if [ $errors -eq 0 ]; then
        log_pass "All YAML files have valid syntax"
    fi
}

# Step 5: Validate JSON syntax
validate_json_syntax() {
    log_step "5" "Validating JSON Syntax"

    cd "$PROJECT_DIR"

    local errors=0
    while IFS= read -r -d '' jsonfile; do
        if python -c "import json; json.load(open('$jsonfile'))" 2>/dev/null; then
            [ "$VERBOSE" = "true" ] && log_info "OK: $jsonfile"
        else
            log_fail "JSON error: $jsonfile"
            ((errors++))
        fi
    done < <(find . -name "*.json" -type f 2>/dev/null | grep -v node_modules | tr '\n' '\0')

    if [ $errors -eq 0 ]; then
        log_pass "All JSON files have valid syntax"
    fi
}

# Step 6: Build Docker images
build_docker_images() {
    log_step "6" "Building Docker Images"

    if [ "$SKIP_DOCKER" = "true" ]; then
        log_skip "Docker build skipped (SKIP_DOCKER=true)"
        return
    fi

    cd "$PROJECT_DIR"

    # Build with compose
    if docker compose build --quiet 2>&1; then
        log_pass "Docker images built successfully"
    else
        log_fail "Docker image build failed"
        return 1
    fi
}

# Step 7: Start services
start_services() {
    log_step "7" "Starting Docker Compose Services"

    if [ "$SKIP_DOCKER" = "true" ]; then
        log_skip "Docker services skipped (SKIP_DOCKER=true)"
        return
    fi

    cd "$PROJECT_DIR"

    docker compose up -d

    log_info "Waiting for services to be ready (timeout: ${TIMEOUT_STARTUP}s)..."

    local elapsed=0
    while [ $elapsed -lt $TIMEOUT_STARTUP ]; do
        if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
            log_pass "Backend service is ready"
            break
        fi
        sleep 5
        elapsed=$((elapsed + 5))
        log_info "Waiting... ($elapsed/$TIMEOUT_STARTUP seconds)"
    done

    if [ $elapsed -ge $TIMEOUT_STARTUP ]; then
        log_fail "Services failed to start within timeout"
        docker compose logs --tail=50
        return 1
    fi
}

# Step 8: Run health checks
run_health_checks() {
    log_step "8" "Running Health Checks"

    if [ "$SKIP_DOCKER" = "true" ]; then
        log_skip "Health checks skipped (SKIP_DOCKER=true)"
        return
    fi

    cd "$PROJECT_DIR"

    # Backend health
    if curl -sf http://localhost:8000/api/v1/health > /dev/null; then
        local status=$(curl -sf http://localhost:8000/api/v1/health | jq -r '.status' 2>/dev/null || echo "ok")
        if [ "$status" = "healthy" ] || [ "$status" = "ok" ]; then
            log_pass "Backend health check: $status"
        else
            log_warn "Backend health check returned: $status"
        fi
    else
        log_fail "Backend health endpoint not responding"
    fi

    # Frontend
    if curl -sf http://localhost:5173 > /dev/null; then
        log_pass "Frontend is accessible"
    else
        log_warn "Frontend not accessible (may still be starting)"
    fi

    # PostgreSQL via compose exec
    if docker compose exec -T postgres pg_isready -U e2e_validation_user 2>/dev/null; then
        log_pass "PostgreSQL is ready"
    else
        log_warn "PostgreSQL check failed"
    fi

    # Redis
    if docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG; then
        log_pass "Redis is responding"
    else
        log_warn "Redis check failed"
    fi

    # Keycloak
    if curl -sf http://localhost:8080/health/ready > /dev/null 2>&1; then
        log_pass "Keycloak is ready"
    else
        log_warn "Keycloak not ready (may need more time)"
    fi
}

# Step 9: Check security headers
check_security_headers() {
    log_step "9" "Checking Security Headers"

    if [ "$SKIP_DOCKER" = "true" ]; then
        log_skip "Security header checks skipped (SKIP_DOCKER=true)"
        return
    fi

    local headers
    headers=$(curl -sI http://localhost:8000/api/v1/health 2>/dev/null || echo "")

    if echo "$headers" | grep -qi "X-Content-Type-Options"; then
        log_pass "X-Content-Type-Options header present"
    else
        log_warn "X-Content-Type-Options header missing"
    fi

    if echo "$headers" | grep -qi "X-Frame-Options"; then
        log_pass "X-Frame-Options header present"
    else
        log_warn "X-Frame-Options header missing"
    fi

    if echo "$headers" | grep -qi "Referrer-Policy"; then
        log_pass "Referrer-Policy header present"
    else
        log_warn "Referrer-Policy header missing"
    fi
}

# Step 10: Check observability stack
check_observability() {
    log_step "10" "Checking Observability Stack"

    if [ "$SKIP_DOCKER" = "true" ]; then
        log_skip "Observability checks skipped (SKIP_DOCKER=true)"
        return
    fi

    # Prometheus
    if curl -sf http://localhost:9090/-/healthy > /dev/null 2>&1; then
        log_pass "Prometheus is healthy"
    else
        log_warn "Prometheus not ready"
    fi

    # Grafana
    if curl -sf http://localhost:3000/api/health > /dev/null 2>&1; then
        log_pass "Grafana is healthy"
    else
        log_warn "Grafana not ready"
    fi

    # Backend metrics endpoint
    if curl -sf http://localhost:8000/metrics > /dev/null 2>&1; then
        log_pass "Backend metrics endpoint available"
    else
        log_warn "Backend metrics endpoint not available"
    fi
}

# Step 11: Validate Kubernetes manifests
validate_kubernetes() {
    log_step "11" "Validating Kubernetes Manifests"

    if [ "$SKIP_K8S" = "true" ]; then
        log_skip "Kubernetes validation skipped"
        return
    fi

    cd "$PROJECT_DIR"

    # Check if k8s directory exists
    if [ ! -d "k8s" ]; then
        log_skip "No k8s directory found"
        return
    fi

    # Validate staging overlay
    if kubectl kustomize k8s/overlays/staging > /dev/null 2>&1; then
        log_pass "Staging Kustomize overlay renders successfully"
    else
        log_fail "Staging Kustomize overlay failed to render"
    fi

    # Validate production overlay
    if kubectl kustomize k8s/overlays/production > /dev/null 2>&1; then
        log_pass "Production Kustomize overlay renders successfully"
    else
        log_fail "Production Kustomize overlay failed to render"
    fi

    # Dry-run validation
    if kubectl apply -k k8s/overlays/staging --dry-run=client -o yaml > /dev/null 2>&1; then
        log_pass "Kubernetes dry-run validation passed"
    else
        log_warn "Kubernetes dry-run validation had issues"
    fi
}

# Step 12: Validate CI workflows
validate_ci_workflows() {
    log_step "12" "Validating CI Workflow Files"

    cd "$PROJECT_DIR"

    local workflows=(".github/workflows/ci.yml" ".github/workflows/build.yml")

    for workflow in "${workflows[@]}"; do
        if [ -f "$workflow" ]; then
            if python -c "import yaml; yaml.safe_load(open('$workflow'))" 2>/dev/null; then
                # Check for required keys
                if python -c "
import yaml
with open('$workflow') as f:
    w = yaml.safe_load(f)
    assert 'name' in w, 'Missing name'
    assert 'on' in w, 'Missing on trigger'
    assert 'jobs' in w, 'Missing jobs'
" 2>/dev/null; then
                    log_pass "$workflow is valid"
                else
                    log_fail "$workflow missing required keys"
                fi
            else
                log_fail "$workflow has invalid YAML"
            fi
        else
            log_warn "$workflow not found"
        fi
    done
}

# Step 13: Run security scan simulation
run_security_checks() {
    log_step "13" "Running Security Checks"

    cd "$PROJECT_DIR"

    # Check for common security issues in code
    local security_issues=0

    # Check for hardcoded secrets patterns (simplified)
    if grep -r "password\s*=\s*['\"][^'\"]*['\"]" backend/app --include="*.py" 2>/dev/null | grep -v "example\|test\|mock" > /dev/null; then
        log_warn "Potential hardcoded password found"
        ((security_issues++))
    fi

    # Check for debug mode in production configs
    if grep -q "DEBUG\s*=\s*True" backend/app/core/config.py 2>/dev/null; then
        log_warn "DEBUG mode may be enabled"
    fi

    # Verify .gitignore excludes sensitive files
    if [ -f ".gitignore" ]; then
        if grep -q ".env" .gitignore && grep -q "__pycache__" .gitignore; then
            log_pass ".gitignore includes security-sensitive patterns"
        else
            log_warn ".gitignore may be missing important patterns"
        fi
    fi

    if [ $security_issues -eq 0 ]; then
        log_pass "No obvious security issues detected"
    fi
}

# Stop services
stop_services() {
    log_step "14" "Stopping Services"

    if [ "$SKIP_DOCKER" = "true" ]; then
        log_skip "Service teardown skipped (SKIP_DOCKER=true)"
        return
    fi

    cd "$PROJECT_DIR"

    if docker compose down -v 2>&1; then
        log_pass "Services stopped and volumes removed"
    else
        log_warn "Some issues during service teardown"
    fi
}

# Print summary
print_summary() {
    log_header "E2E Validation Summary"

    local total=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))

    echo ""
    echo -e "Total Tests:   $total"
    echo -e "${GREEN}Passed:        $TESTS_PASSED${NC}"
    echo -e "${RED}Failed:        $TESTS_FAILED${NC}"
    echo -e "${MAGENTA}Skipped:       $TESTS_SKIPPED${NC}"
    echo ""

    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}  E2E VALIDATION PASSED${NC}"
        echo -e "${GREEN}========================================${NC}"
        return 0
    else
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}  E2E VALIDATION FAILED${NC}"
        echo -e "${RED}  $TESTS_FAILED test(s) failed${NC}"
        echo -e "${RED}========================================${NC}"
        return 1
    fi
}

# Main execution
main() {
    log_header "E2E Deployment Validation"
    echo ""
    echo -e "${BLUE}Template:${NC}    $TEMPLATE_DIR"
    echo -e "${BLUE}Output:${NC}      $OUTPUT_DIR"
    echo -e "${BLUE}Cleanup:${NC}     $CLEANUP"
    echo -e "${BLUE}Skip Docker:${NC} $SKIP_DOCKER"
    echo -e "${BLUE}Skip K8s:${NC}    $SKIP_K8S"

    check_requirements
    generate_project
    validate_file_structure
    validate_python_syntax
    validate_yaml_syntax
    validate_json_syntax
    build_docker_images
    start_services
    run_health_checks
    check_security_headers
    check_observability
    validate_kubernetes
    validate_ci_workflows
    run_security_checks
    stop_services

    print_summary
}

# Run main function
main "$@"
