# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for the project-starter template. ADRs document significant architectural decisions, providing context and rationale for future maintainers and contributors.

## About ADRs

Architecture Decision Records capture important decisions made during the development of this project. They help:

- **New contributors** understand why things are built the way they are
- **Evaluators** assess the architectural soundness of the template
- **Future maintainers** make informed decisions when considering changes
- **Current team** maintain consistency across related decisions

## ADR Format

All ADRs in this project follow a standard format:

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

## File Naming Convention

ADR files follow this naming pattern:

```
NNN-short-title.md
```

Examples:
- `001-fastapi-backend-framework.md`
- `005-row-level-security-multitenancy.md`

## Priority Legend

- **P1**: Critical for understanding core architecture - should be written first
- **P2**: Important for advanced usage and contribution
- **P3**: Nice to have for completeness

---

## ADR Index by Category

### Technology Stack (ADR-001 to ADR-004)

| ID | Title | Status | Priority | Description |
|----|-------|--------|----------|-------------|
| ADR-001 | FastAPI as Backend Framework | Planned | P1 | Why FastAPI was chosen over Flask, Django, or other Python web frameworks. Factors: async support, automatic OpenAPI docs, Pydantic integration, performance. |
| ADR-002 | Lit as Frontend Framework | Planned | P1 | Why Lit was chosen over React, Vue, Svelte, or Angular. Factors: web components standard, small bundle size, no virtual DOM, native platform alignment. |
| ADR-003 | PostgreSQL as Primary Database | Planned | P2 | Why PostgreSQL was chosen over MySQL, MongoDB, or other databases. Factors: RLS support, JSONB, mature ecosystem, reliability. |
| ADR-004 | Keycloak as Identity Provider | Planned | P1 | Why Keycloak was chosen over Auth0, Okta, or custom implementation. Factors: open source, full-featured, self-hosted option, OIDC compliance. |

### Architecture Patterns (ADR-005 to ADR-009)

| ID | Title | Status | Priority | Description |
|----|-------|--------|----------|-------------|
| ADR-005 | Row-Level Security for Multi-Tenancy | Planned | P1 | Why PostgreSQL RLS was chosen for tenant isolation over application-level filtering, separate schemas, or separate databases. Factors: security, simplicity, performance. |
| ADR-006 | Dual Database Users Pattern | Planned | P2 | Why separate migration and application database users are used. Factors: RLS bypass for migrations, principle of least privilege, security. |
| ADR-007 | Redis Token Revocation Strategy | Planned | P2 | Why Redis blacklist was chosen for token revocation over short-lived tokens, token introspection, or database storage. Factors: performance, simplicity, TTL support. |
| ADR-008 | JWKS Caching Strategy | Planned | P3 | How JWT validation keys are cached and refreshed. Factors: performance, security, key rotation support. |
| ADR-009 | Cookie-Based Authentication Transport | Planned | P2 | Why HTTP-only cookies are used for token transport over Authorization headers. Factors: XSS protection, CSRF considerations, browser security model. |

### Operational Decisions (ADR-010 to ADR-012)

| ID | Title | Status | Priority | Description |
|----|-------|--------|----------|-------------|
| ADR-010 | Docker Compose for Development | Planned | P2 | Why Docker Compose is the primary development environment over local installation or Kubernetes. Factors: simplicity, reproducibility, service orchestration. |
| ADR-011 | Port Allocation Strategy | Planned | P3 | Why specific ports were chosen (5435 for PostgreSQL, 8080 for Keycloak, etc.). Factors: avoiding conflicts, convention, debugging convenience. |
| ADR-012 | uv as Python Package Manager | Planned | P2 | Why uv was chosen over pip, poetry, or pipenv for the generated backend. Factors: speed, reproducibility, modern tooling. |

### Security Decisions (ADR-013 to ADR-015)

| ID | Title | Status | Priority | Description |
|----|-------|--------|----------|-------------|
| ADR-013 | PKCE Enforcement for Public Clients | Planned | P1 | Why PKCE is enforced for frontend OAuth clients. Factors: security best practices, OAuth 2.1 compliance, authorization code interception protection. |
| ADR-014 | Rate Limiting Strategy | Planned | P2 | Why Redis-based rate limiting was implemented and the default limits chosen. Factors: DDoS protection, API abuse prevention, user experience. |
| ADR-015 | CORS Configuration Approach | Planned | P3 | How CORS origins are configured and why. Factors: security, development convenience, production deployment. |

### Template Design (ADR-016 to ADR-018)

| ID | Title | Status | Priority | Description |
|----|-------|--------|----------|-------------|
| ADR-016 | Cookiecutter as Template Engine | Planned | P2 | Why Cookiecutter was chosen over Copier, Yeoman, or custom generation. Factors: Python ecosystem, maturity, simplicity, Jinja2 templating. |
| ADR-017 | Optional Observability Stack | Planned | P3 | Why observability is an optional feature rather than always-on or never-included. Factors: resource usage, complexity, developer preference. |
| ADR-018 | Always-On Multi-Tenancy | Planned | P2 | Why multi-tenancy and rate limiting are always enabled rather than optional. Factors: architectural complexity of removal, security defaults, production readiness. |

---

## Summary by Priority

### P1 - Critical (Write First)

| ID | Title | Category |
|----|-------|----------|
| ADR-001 | FastAPI as Backend Framework | Technology Stack |
| ADR-002 | Lit as Frontend Framework | Technology Stack |
| ADR-004 | Keycloak as Identity Provider | Technology Stack |
| ADR-005 | Row-Level Security for Multi-Tenancy | Architecture Patterns |
| ADR-013 | PKCE Enforcement for Public Clients | Security Decisions |

### P2 - Important

| ID | Title | Category |
|----|-------|----------|
| ADR-003 | PostgreSQL as Primary Database | Technology Stack |
| ADR-006 | Dual Database Users Pattern | Architecture Patterns |
| ADR-007 | Redis Token Revocation Strategy | Architecture Patterns |
| ADR-009 | Cookie-Based Authentication Transport | Architecture Patterns |
| ADR-010 | Docker Compose for Development | Operational Decisions |
| ADR-012 | uv as Python Package Manager | Operational Decisions |
| ADR-014 | Rate Limiting Strategy | Security Decisions |
| ADR-016 | Cookiecutter as Template Engine | Template Design |
| ADR-018 | Always-On Multi-Tenancy | Template Design |

### P3 - Nice to Have

| ID | Title | Category |
|----|-------|----------|
| ADR-008 | JWKS Caching Strategy | Architecture Patterns |
| ADR-011 | Port Allocation Strategy | Operational Decisions |
| ADR-015 | CORS Configuration Approach | Security Decisions |
| ADR-017 | Optional Observability Stack | Template Design |

---

## Contributing New ADRs

When making a significant architectural decision:

1. Copy the format template above
2. Use the next available ADR number
3. Fill in all sections (Alternatives Considered is optional but recommended)
4. Set Status to "Proposed"
5. Submit for review
6. Update Status to "Accepted" after approval

### What Warrants an ADR?

Write an ADR when:

- Choosing between multiple viable technologies
- Establishing patterns that will be used project-wide
- Making decisions with significant trade-offs
- Changing a previous architectural decision

Do not write an ADR for:

- Minor implementation details
- Obvious or industry-standard choices without trade-offs
- Temporary solutions marked as technical debt

---

## Related Documentation

- [Main README](../../README.md) - Project overview and quick start
- [QUICKSTART.md](../../QUICKSTART.md) - Getting started guide
- [FRD: Documentation Overhaul](../futures/documentation-overhaul.md) - Feature request document that defined this ADR structure

---

## Document History

| Date | Change |
|------|--------|
| 2025-12-05 | Initial ADR index created with 18 planned ADRs |
