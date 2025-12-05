# Task Breakdown: Documentation Overhaul - ADR Writing Phase

## Feature Overview

Complete the documentation overhaul by writing the 18 Architecture Decision Records (ADRs) identified in the refined FRD. The main documentation work (Phases 1-5) has been completed:

- ADR index created at `docs/adr/README.md` (18 ADRs indexed)
- QUICKSTART.md reworked (121 lines, 5 steps)
- README.md reworked (217 lines)
- TEMPLATE_SUMMARY.md deprecated
- Validation passed

**Source FRD:** [frd.md](./frd.md)

**Remaining Work:** Write the 18 ADR documents following the format established in the ADR index.

---

## Task List

| ID | Task | Status | Domain | Complexity | Dependencies |
|----|------|--------|--------|------------|--------------|
| ADR-P1-01 | [Write P1 Critical ADRs (5 documents)](./task-adr-p1-critical.md) | Not Started | Documentation | L | None |
| ADR-P2-01 | [Write P2 Important ADRs - Technology & Architecture (5 documents)](./task-adr-p2-tech-arch.md) | Not Started | Documentation | L | None |
| ADR-P2-02 | [Write P2 Important ADRs - Operations & Template Design (4 documents)](./task-adr-p2-ops-template.md) | Not Started | Documentation | M | None |
| ADR-P3-01 | [Write P3 Nice-to-Have ADRs (4 documents)](./task-adr-p3-nice-to-have.md) | Not Started | Documentation | M | None |
| MAINT-01 | [Remove TEMPLATE_SUMMARY.md (Post-Release)](./task-template-summary-removal.md) | Not Started | Documentation | XS | Release cycle completion |
| OPT-01 | [Create CONTRIBUTING.md (Optional)](./task-contributing-md.md) | Not Started | Documentation | S | ADR-P1-01 |

---

## Dependency Graph

```
                    +------------------+
                    |  ADR Index Ready |
                    |  (Completed P1)  |
                    +--------+---------+
                             |
         +-------------------+-------------------+
         |                   |                   |
         v                   v                   v
  +------+------+     +------+------+     +------+------+
  |  ADR-P1-01  |     |  ADR-P2-01  |     |  ADR-P2-02  |
  |  P1 Critical|     |  P2 Tech/Arch|    |  P2 Ops/Tmpl|
  +------+------+     +------+------+     +------+------+
         |                   |                   |
         |                   v                   v
         |            +------+------+     +------+------+
         |            |  ADR-P3-01  |     |  (parallel) |
         |            |  P3 Nice2Have|    +-------------+
         |            +-------------+
         |
         v
  +------+------+
  |   OPT-01    |
  | CONTRIBUTING|
  +-------------+

                        (Separate Track)
                    +------------------+
                    |    MAINT-01      |
                    | Template Summary |
                    |  (After Release) |
                    +------------------+
```

**Note:** ADR tasks can be worked in parallel. The only dependency is that OPT-01 (CONTRIBUTING.md) benefits from having P1 ADRs completed first to reference architectural guidance.

---

## Domain Distribution

### Documentation Agent
All tasks in this breakdown are documentation tasks:
- ADR-P1-01: Write 5 critical ADRs
- ADR-P2-01: Write 5 technology/architecture ADRs
- ADR-P2-02: Write 4 operations/template ADRs
- ADR-P3-01: Write 4 nice-to-have ADRs
- MAINT-01: Remove deprecated file
- OPT-01: Create CONTRIBUTING.md

---

## Progress Tracking

**Current Status:** 0 of 6 tasks completed (0%)

**Next Task:** ADR-P1-01 (P1 Critical ADRs - highest priority)

**Blockers:** None

---

## ADR Distribution by Priority

### P1 - Critical (Write First) - ADR-P1-01

| ADR ID | Title | Category | File Name |
|--------|-------|----------|-----------|
| ADR-001 | FastAPI as Backend Framework | Technology Stack | `001-fastapi-backend-framework.md` |
| ADR-002 | Lit as Frontend Framework | Technology Stack | `002-lit-frontend-framework.md` |
| ADR-004 | Keycloak as Identity Provider | Technology Stack | `004-keycloak-identity-provider.md` |
| ADR-005 | Row-Level Security for Multi-Tenancy | Architecture Patterns | `005-row-level-security-multitenancy.md` |
| ADR-013 | PKCE Enforcement for Public Clients | Security Decisions | `013-pkce-enforcement.md` |

### P2 - Important - ADR-P2-01 (Technology & Architecture)

| ADR ID | Title | Category | File Name |
|--------|-------|----------|-----------|
| ADR-003 | PostgreSQL as Primary Database | Technology Stack | `003-postgresql-primary-database.md` |
| ADR-006 | Dual Database Users Pattern | Architecture Patterns | `006-dual-database-users.md` |
| ADR-007 | Redis Token Revocation Strategy | Architecture Patterns | `007-redis-token-revocation.md` |
| ADR-009 | Cookie-Based Authentication Transport | Architecture Patterns | `009-cookie-based-auth-transport.md` |
| ADR-014 | Rate Limiting Strategy | Security Decisions | `014-rate-limiting-strategy.md` |

### P2 - Important - ADR-P2-02 (Operations & Template Design)

| ADR ID | Title | Category | File Name |
|--------|-------|----------|-----------|
| ADR-010 | Docker Compose for Development | Operational Decisions | `010-docker-compose-development.md` |
| ADR-012 | uv as Python Package Manager | Operational Decisions | `012-uv-package-manager.md` |
| ADR-016 | Cookiecutter as Template Engine | Template Design | `016-cookiecutter-template-engine.md` |
| ADR-018 | Always-On Multi-Tenancy | Template Design | `018-always-on-multitenancy.md` |

### P3 - Nice to Have - ADR-P3-01

| ADR ID | Title | Category | File Name |
|--------|-------|----------|-----------|
| ADR-008 | JWKS Caching Strategy | Architecture Patterns | `008-jwks-caching-strategy.md` |
| ADR-011 | Port Allocation Strategy | Operational Decisions | `011-port-allocation-strategy.md` |
| ADR-015 | CORS Configuration Approach | Security Decisions | `015-cors-configuration.md` |
| ADR-017 | Optional Observability Stack | Template Design | `017-optional-observability.md` |

---

## Integration Contracts

### Contract IC-1: ADR Format

All ADRs must follow the format specified in `docs/adr/README.md`:

```markdown
# ADR-NNN: [Title]

## Status

[Proposed | Accepted | Deprecated | Superseded by ADR-XXX]

## Context

What is the issue that we're seeing that is motivating this decision or change?
Include relevant background, constraints, and forces at play.

## Decision

What is the change that we're proposing and/or doing?
State the decision clearly and concisely.

## Consequences

What becomes easier or more difficult to do because of this change?
Include both positive and negative consequences.

## Alternatives Considered

What other options were evaluated? Why were they not chosen?
This section is optional but recommended.
```

### Contract IC-2: File Naming

ADR files must follow the naming pattern: `NNN-short-title.md`

Examples:
- `001-fastapi-backend-framework.md`
- `005-row-level-security-multitenancy.md`

### Contract IC-3: ADR Index Update

After each ADR is written, the status in `docs/adr/README.md` should be updated from "Planned" to "Accepted".

---

## Notes and Refinements

1. **Parallel Work Encouraged:** All ADR writing tasks (ADR-P1-01 through ADR-P3-01) have no inter-dependencies and can be worked in parallel by multiple documentation agents.

2. **Research Required:** Each ADR will require research into the codebase to understand the actual implementation and document the rationale accurately.

3. **Alternatives Section:** While marked as optional in the format, all ADRs should include an "Alternatives Considered" section where possible to provide full context.

4. **TEMPLATE_SUMMARY.md Timeline:** The FRD recommends keeping the deprecation notice for one release cycle before full removal. MAINT-01 should be scheduled accordingly.

5. **CONTRIBUTING.md Scope:** If OPT-01 is pursued, it should focus on contribution guidelines that reference ADRs for architectural guidance and include documentation contribution guidance.

---

## Estimated Total Effort

| Task | Complexity | Count | Effort per ADR | Total Effort |
|------|------------|-------|----------------|--------------|
| ADR-P1-01 | L | 5 ADRs | 1-2 hours | 5-10 hours |
| ADR-P2-01 | L | 5 ADRs | 1-2 hours | 5-10 hours |
| ADR-P2-02 | M | 4 ADRs | 1-1.5 hours | 4-6 hours |
| ADR-P3-01 | M | 4 ADRs | 1-1.5 hours | 4-6 hours |
| MAINT-01 | XS | 1 | 15 min | 0.25 hours |
| OPT-01 | S | 1 | 2-3 hours | 2-3 hours |

**Total Estimated Effort:** 20-35 hours (3-5 days)

---

## File References

### ADR Directory
- `/home/ty/workspace/project-starter/docs/adr/README.md` - ADR index and format guide

### Codebase Areas to Reference for ADR Writing

| ADR | Primary Code Areas |
|-----|-------------------|
| ADR-001 (FastAPI) | `template/{{cookiecutter.project_slug}}/backend/` |
| ADR-002 (Lit) | `template/{{cookiecutter.project_slug}}/frontend/` |
| ADR-003 (PostgreSQL) | `template/{{cookiecutter.project_slug}}/backend/app/db/` |
| ADR-004 (Keycloak) | `template/{{cookiecutter.project_slug}}/keycloak/` |
| ADR-005 (RLS) | `template/{{cookiecutter.project_slug}}/backend/app/db/` |
| ADR-006 (Dual Users) | `template/{{cookiecutter.project_slug}}/backend/alembic/` |
| ADR-007 (Redis) | `template/{{cookiecutter.project_slug}}/backend/app/auth/` |
| ADR-008 (JWKS) | `template/{{cookiecutter.project_slug}}/backend/app/auth/` |
| ADR-009 (Cookies) | `template/{{cookiecutter.project_slug}}/backend/app/auth/` |
| ADR-010 (Docker) | `template/{{cookiecutter.project_slug}}/docker-compose*.yml` |
| ADR-011 (Ports) | `template/{{cookiecutter.project_slug}}/docker-compose*.yml` |
| ADR-012 (uv) | `template/{{cookiecutter.project_slug}}/backend/pyproject.toml` |
| ADR-013 (PKCE) | `template/{{cookiecutter.project_slug}}/frontend/`, Keycloak config |
| ADR-014 (Rate Limiting) | `template/{{cookiecutter.project_slug}}/backend/app/api/` |
| ADR-015 (CORS) | `template/{{cookiecutter.project_slug}}/backend/app/main.py` |
| ADR-016 (Cookiecutter) | `template/cookiecutter.json`, `hooks/` |
| ADR-017 (Observability) | `template/{{cookiecutter.project_slug}}/observability/` |
| ADR-018 (Multi-Tenancy) | `template/{{cookiecutter.project_slug}}/backend/app/db/` |

---

*Last Updated: 2025-12-05*
*Breakdown Status: Complete*
