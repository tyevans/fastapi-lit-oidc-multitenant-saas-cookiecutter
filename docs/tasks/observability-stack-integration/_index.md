# Observability Stack Integration - Task Breakdown

## Feature Overview

Port the battle-tested observability stack (Prometheus, Loki, Promtail, Tempo, Grafana) from `implementation-manager/` into the cookiecutter project template. This enables generated projects to have production-ready observability out of the box.

**Key Context:**
- UNRELEASED project - clean code first, breaking changes encouraged
- Simplified scope: 1 dashboard (Backend Service), others are future work
- Docker socket approach for Promtail (not file-based)
- First use of `{% if %}` conditionals in template - sets precedent

**Source FRD:** [frd.md](./frd.md)

---

## Task List

### Phase 1: Infrastructure Setup (2-3 days)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P1-01 | [Create observability directory structure](./P1-01-observability-directory-structure.md) | Not Started | DevOps | XS | None |
| P1-02 | [Port Prometheus configuration](./P1-02-prometheus-configuration.md) | Not Started | DevOps | S | P1-01 |
| P1-03 | [Port Loki configuration](./P1-03-loki-configuration.md) | Not Started | DevOps | S | P1-01 |
| P1-04 | [Port Promtail configuration](./P1-04-promtail-configuration.md) | Not Started | DevOps | S | P1-01 |
| P1-05 | [Port Tempo configuration](./P1-05-tempo-configuration.md) | Not Started | DevOps | S | P1-01 |
| P1-06 | [Add observability services to compose.yml](./P1-06-compose-services.md) | Not Started | DevOps | M | P1-02, P1-03, P1-04, P1-05 |
| P1-07 | [Create observability README](./P1-07-observability-readme.md) | Not Started | DevOps | XS | P1-06 |

### Phase 2: Backend Instrumentation (2-3 days)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P2-01 | [Add observability Python dependencies](./P2-01-python-dependencies.md) | Not Started | Backend | S | P1-06 |
| P2-02 | [Create observability.py module](./P2-02-observability-module.md) | Not Started | Backend | M | P2-01 |
| P2-03 | [Integrate observability into main.py](./P2-03-main-integration.md) | Not Started | Backend | S | P2-02 |
| P2-04 | [Add backend environment variables to compose.yml](./P2-04-backend-env-vars.md) | Not Started | Backend | XS | P2-02 |

### Phase 3: Visualization Layer (1-2 days)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P3-01 | [Create Grafana datasources configuration](./P3-01-grafana-datasources.md) | Not Started | DevOps | S | P1-06 |
| P3-02 | [Create dashboard provisioning configuration](./P3-02-dashboard-provisioning.md) | Not Started | DevOps | XS | P3-01 |
| P3-03 | [Port Backend Service dashboard](./P3-03-backend-dashboard.md) | Not Started | DevOps | M | P3-02, P2-02 |

### Phase 4: Template Conditionals (1-2 days)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P4-01 | [Add cookiecutter.json variables](./P4-01-cookiecutter-variables.md) | Not Started | DevOps | S | P1-06, P2-02 |
| P4-02 | [Add Jinja2 conditionals to compose.yml](./P4-02-compose-conditionals.md) | Not Started | DevOps | M | P4-01 |
| P4-03 | [Add conditionals to pyproject.toml](./P4-03-pyproject-conditionals.md) | Not Started | Backend | S | P4-01 |
| P4-04 | [Add conditionals to main.py](./P4-04-main-conditionals.md) | Not Started | Backend | S | P4-01 |
| P4-05 | [Conditional observability directory rendering](./P4-05-directory-conditionals.md) | Not Started | DevOps | S | P4-01 |

### Phase 5: Documentation and Testing (2-3 days)

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| P5-01 | [Update project README with observability section](./P5-01-readme-update.md) | Not Started | DevOps | S | P4-05 |
| P5-02 | [Update CLAUDE.md with observability info](./P5-02-claude-md-update.md) | Not Started | DevOps | XS | P5-01 |
| P5-03 | [Add observability validation tests](./P5-03-validation-tests.md) | Not Started | Backend | M | P4-05 |
| P5-04 | [End-to-end integration testing](./P5-04-e2e-testing.md) | Not Started | DevOps | M | P5-03 |

---

## Dependency Graph

```
Phase 1: Infrastructure
========================
P1-01 (Directory Structure)
   |
   +---> P1-02 (Prometheus) ---+
   |                           |
   +---> P1-03 (Loki) ---------+
   |                           |
   +---> P1-04 (Promtail) -----+---> P1-06 (Compose Services) ---> P1-07 (Obs README)
   |                           |
   +---> P1-05 (Tempo) --------+

Phase 2: Backend Instrumentation
=================================
P1-06 ---> P2-01 (Python Deps) ---> P2-02 (observability.py) ---> P2-03 (main.py)
                                         |
                                         +---> P2-04 (Backend Env Vars)

Phase 3: Visualization
=======================
P1-06 ---> P3-01 (Datasources) ---> P3-02 (Dashboard Provisioning) ---> P3-03 (Backend Dashboard)
                                                                              ^
P2-02 -----------------------------------------------------------------------+

Phase 4: Template Conditionals
===============================
P1-06 + P2-02 ---> P4-01 (cookiecutter.json)
                        |
                        +---> P4-02 (compose.yml conditionals)
                        |
                        +---> P4-03 (pyproject.toml conditionals)
                        |
                        +---> P4-04 (main.py conditionals)
                        |
                        +---> P4-05 (Directory conditionals)

Phase 5: Documentation & Testing
=================================
P4-05 ---> P5-01 (README) ---> P5-02 (CLAUDE.md)
       |
       +---> P5-03 (Validation Tests) ---> P5-04 (E2E Testing)
```

---

## Domain Distribution

### DevOps Agent (14 tasks)
- P1-01 through P1-07 (Infrastructure)
- P3-01, P3-02, P3-03 (Visualization)
- P4-01, P4-02, P4-05 (Template Conditionals)
- P5-01, P5-02, P5-04 (Documentation)

### Backend Agent (7 tasks)
- P2-01 through P2-04 (Instrumentation)
- P4-03, P4-04 (Backend Conditionals)
- P5-03 (Validation Tests)

---

## Integration Contracts

### Contract 1: Observability Module API
**Provider:** Backend Agent (P2-02)
**Consumer:** main.py integration (P2-03, P4-04)

```python
def setup_observability(app: FastAPI) -> FastAPI:
    """
    Initialize observability instrumentation for FastAPI application.

    - Instruments app with OpenTelemetry tracing
    - Registers metrics middleware
    - Adds /metrics endpoint

    Returns: The instrumented FastAPI application
    """
```

### Contract 2: Metrics Endpoint
**Provider:** Backend Agent (P2-02)
**Consumer:** Prometheus scrape configuration (P1-02)

```
Endpoint: GET /metrics
Response: Prometheus exposition format (text/plain)
Metrics:
  - http_requests_total{method, endpoint, status}
  - http_request_duration_seconds{method, endpoint}
  - active_requests
```

### Contract 3: Trace Export
**Provider:** Backend Agent (P2-02)
**Consumer:** Tempo service (P1-05)

```
Protocol: OTLP/gRPC
Endpoint: tempo:4317
Configuration: OTEL_EXPORTER_OTLP_ENDPOINT environment variable
```

### Contract 4: Conditional Template Variable
**Provider:** DevOps Agent (P4-01)
**Consumer:** All conditional tasks (P4-02 through P4-05)

```json
{
  "include_observability": "yes"  // or "no"
}
```

### Contract 5: Docker Network Communication
**Provider:** compose.yml (P1-06, P4-02)
**Consumer:** All observability services

```
Network: {{ cookiecutter.project_slug }}-network
Service Names: prometheus, loki, promtail, tempo, grafana, backend
```

---

## Progress Tracking

| Phase | Tasks | Completed | Progress |
|-------|-------|-----------|----------|
| Phase 1 | 7 | 0 | 0% |
| Phase 2 | 4 | 0 | 0% |
| Phase 3 | 3 | 0 | 0% |
| Phase 4 | 5 | 0 | 0% |
| Phase 5 | 4 | 0 | 0% |
| **Total** | **23** | **0** | **0%** |

---

## Notes and Refinements

### Initial Breakdown Notes (2025-12-03)
- Scope simplified from FRD: Only Backend Service Dashboard in initial release
- SLO, Log Explorer, and Trace Explorer dashboards marked as future work
- Docker socket approach confirmed for Promtail (matches implementation-manager)
- First conditional template feature - approach will set precedent for future features

### Risks Identified
1. **Jinja2 Conditional Complexity**: First use of conditionals in the template may require careful testing to ensure proper YAML formatting
2. **Docker Socket Permissions**: Promtail Docker socket access may require elevated permissions on some systems
3. **OpenTelemetry Versioning**: Beta instrumentation packages (opentelemetry-instrumentation-fastapi) may have breaking changes

### Key Decisions
- Use `{% if cookiecutter.include_observability == "yes" %}` pattern consistently
- Observability services use project network, not default network
- All configuration files use YAML with inline comments
- Anonymous Grafana access enabled by default for development convenience

---

## Breakdown Status

**Status**: COMPLETE - All 23 tasks documented and ready for domain agents

**Breakdown Date**: 2025-12-03

**Task Documents Created**:
- Phase 1: 7 tasks (P1-01 through P1-07)
- Phase 2: 4 tasks (P2-01 through P2-04)
- Phase 3: 3 tasks (P3-01 through P3-03)
- Phase 4: 5 tasks (P4-01 through P4-05)
- Phase 5: 4 tasks (P5-01 through P5-04)

**Estimated Total Effort**: 7-10 days

**Next Steps**:
1. Domain agents can claim tasks starting with Phase 1
2. Begin with P1-01 (directory structure) as it has no dependencies
3. Multiple tasks can be worked in parallel within phases
4. Cross-phase dependencies must be respected (see Dependency Graph above)
