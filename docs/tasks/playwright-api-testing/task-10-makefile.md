# TASK-10: Makefile Integration

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | TASK-10 |
| Title | Makefile Integration |
| Domain | DevOps |
| Complexity | S (Small) |
| Estimated Effort | 2-3 hours |
| Dependencies | TASK-01 |
| Blocks | TASK-11 |

---

## Scope

### What This Task Includes

1. Create project root Makefile (does not currently exist)
2. Add test-related targets (test, test-api, test-ui, test-debug, test-report, test-install)
3. Add Docker-related targets (docker-up, docker-down, docker-logs)
4. Add help target with command descriptions
5. Integrate with existing docker-dev.sh script where appropriate

### What This Task Excludes

- Playwright directory creation (TASK-01)
- Test files (TASK-07, TASK-08)
- Documentation (TASK-11)

---

## Relevant Code Areas

### Files to Create

| File Path | Purpose |
|-----------|---------|
| `template/{{cookiecutter.project_slug}}/Makefile` | Project automation commands |

### Reference Files

| File Path | How It Helps |
|-----------|--------------|
| `/home/ty/workspace/project-starter/implementation-manager/Makefile` | Reference Makefile patterns |
| `/home/ty/workspace/project-starter/template/{{cookiecutter.project_slug}}/scripts/docker-dev.sh` | Existing Docker commands to wrap |

---

## Implementation Details

### Makefile Specification

```makefile
# {{ cookiecutter.project_name }} Makefile
# Provides common development and testing commands

.PHONY: help docker-up docker-down docker-logs docker-reset \
        test test-api test-ui test-debug test-report test-install \
        backend-shell frontend-shell keycloak-setup

# Default target
.DEFAULT_GOAL := help

# Directory paths
PLAYWRIGHT_DIR := playwright
SCRIPTS_DIR := scripts

# ============================================
# Help
# ============================================

help: ## Show this help message
	@echo ''
	@echo '{{ cookiecutter.project_name }} - Development Commands'
	@echo ''
	@echo 'Docker Commands:'
	@grep -E '^docker-[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo 'Testing Commands:'
	@grep -E '^test[a-zA-Z_-]*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''
	@echo 'Other Commands:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -v -E '^(docker-|test)' | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ''

# ============================================
# Docker Commands
# ============================================

docker-up: ## Start all Docker services
	./$(SCRIPTS_DIR)/docker-dev.sh up

docker-down: ## Stop all Docker services
	./$(SCRIPTS_DIR)/docker-dev.sh down

docker-logs: ## View Docker logs (use: make docker-logs SERVICE=backend)
	@if [ -n "$(SERVICE)" ]; then \
		./$(SCRIPTS_DIR)/docker-dev.sh logs $(SERVICE); \
	else \
		./$(SCRIPTS_DIR)/docker-dev.sh logs; \
	fi

docker-reset: ## Full clean restart of Docker services
	./$(SCRIPTS_DIR)/docker-dev.sh reset

# ============================================
# Shell Access
# ============================================

backend-shell: ## Open shell in backend container
	./$(SCRIPTS_DIR)/docker-dev.sh shell backend

frontend-shell: ## Open shell in frontend container
	./$(SCRIPTS_DIR)/docker-dev.sh shell frontend

# ============================================
# Keycloak
# ============================================

keycloak-setup: ## Run Keycloak realm setup script
	./keycloak/setup-realm.sh

keycloak-wait: ## Wait for Keycloak to be ready
	@echo "Waiting for Keycloak to be ready..."
	@until curl -sf http://localhost:{{ cookiecutter.keycloak_port }}/health/ready > /dev/null 2>&1; do \
		echo "  Keycloak not ready, waiting..."; \
		sleep 5; \
	done
	@echo "Keycloak is ready!"

# ============================================
# Playwright Testing Commands
# ============================================

test: ## Run all Playwright tests
	cd $(PLAYWRIGHT_DIR) && npm test

test-api: ## Run API tests only
	cd $(PLAYWRIGHT_DIR) && npm run test:api

test-ui: ## Run tests in interactive UI mode
	cd $(PLAYWRIGHT_DIR) && npm run test:ui

test-debug: ## Run tests in debug mode
	cd $(PLAYWRIGHT_DIR) && npm run test:debug

test-report: ## Show Playwright test report
	cd $(PLAYWRIGHT_DIR) && npm run report

test-install: ## Install Playwright dependencies
	cd $(PLAYWRIGHT_DIR) && npm install

# ============================================
# Full Setup Commands
# ============================================

setup: ## Initial project setup (install deps, start services, setup keycloak)
	@echo "Installing Playwright dependencies..."
	$(MAKE) test-install
	@echo ""
	@echo "Starting Docker services..."
	$(MAKE) docker-up
	@echo ""
	@echo "Waiting for services..."
	$(MAKE) keycloak-wait
	@echo ""
	@echo "Setting up Keycloak realm..."
	$(MAKE) keycloak-setup
	@echo ""
	@echo "Setup complete! Run 'make test-api' to verify."

# ============================================
# CI Commands
# ============================================

ci-test: ## Run tests in CI mode
	cd $(PLAYWRIGHT_DIR) && CI=true npm test
```

### Target Summary

| Target | Description | Dependencies |
|--------|-------------|--------------|
| `help` | Show all available commands | None |
| `docker-up` | Start Docker services | docker-dev.sh |
| `docker-down` | Stop Docker services | docker-dev.sh |
| `docker-logs` | View service logs | docker-dev.sh |
| `docker-reset` | Clean restart | docker-dev.sh |
| `backend-shell` | Shell access | docker-dev.sh |
| `frontend-shell` | Shell access | docker-dev.sh |
| `keycloak-setup` | Setup realm | setup-realm.sh |
| `keycloak-wait` | Wait for Keycloak | curl |
| `test` | Run all tests | npm |
| `test-api` | Run API tests | npm |
| `test-ui` | Interactive mode | npm |
| `test-debug` | Debug mode | npm |
| `test-report` | Show report | npm |
| `test-install` | Install deps | npm |
| `setup` | Full setup | Multiple |
| `ci-test` | CI mode tests | npm |

---

## Cookiecutter Variables Used

| Variable | Default | Usage |
|----------|---------|-------|
| `{{ cookiecutter.project_name }}` | Project Name | Help text |
| `{{ cookiecutter.keycloak_port }}` | 8080 | Keycloak health check URL |

---

## Success Criteria

1. **Makefile Created**: File exists at project root
2. **All Targets Work**: Each target executes correctly
3. **Help Output**: `make help` shows formatted command list
4. **Docker Integration**: docker-* targets work with existing script
5. **Test Integration**: test-* targets work with Playwright

---

## Verification Steps

```bash
# Generate project
cookiecutter template/ --no-input project_name="Test Project"
cd test-project

# Verify Makefile exists
ls -la Makefile

# Test help target
make help

# Test Docker targets (will fail without Docker, but should not have syntax errors)
make docker-up 2>&1 || echo "Docker not running (expected)"

# Test install target
make test-install

# Test Playwright targets
make test-api 2>&1 || echo "Services not running (expected)"
```

---

## Integration Points

### Upstream Dependencies

- **TASK-01**: Playwright directory must exist for test targets

### Downstream Dependencies

This task enables:
- **TASK-11**: Documentation references Makefile commands

### Contracts

**Command Contract:**
The following make commands MUST work:
```bash
make help           # Show help
make docker-up      # Start services
make docker-down    # Stop services
make test           # Run all tests
make test-api       # Run API tests
make test-ui        # Interactive mode
make test-install   # Install dependencies
make setup          # Full setup
```

---

## Monitoring and Observability

Not directly applicable, but the Makefile provides:
- Consistent command interface
- Colored output via help target
- Service health checking via keycloak-wait

---

## Infrastructure Needs

None - this task only creates template files.

---

## Notes

1. **No Existing Makefile**: The template does not currently have a Makefile. This task creates one from scratch.

2. **docker-dev.sh Integration**: The Makefile wraps the existing `docker-dev.sh` script for Docker commands, maintaining consistency.

3. **SERVICE Variable**: The `docker-logs` target accepts an optional SERVICE parameter for targeted log viewing.

4. **Setup Target**: The `setup` target provides a one-command project initialization, useful for new developers.

5. **CI Target**: The `ci-test` target sets CI=true for consistent CI behavior.

---

## FRD References

- FR-8.1: Makefile Targets
- FR-8.2: npm Script Integration
- IP-6: Phase 6 - Build System Integration
- TA-9: Makefile Integration

---

*Task Created: 2025-12-04*
*Status: Not Started*
