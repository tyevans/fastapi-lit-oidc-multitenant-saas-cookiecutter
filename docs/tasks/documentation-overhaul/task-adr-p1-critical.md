# ADR-P1-01: Write P1 Critical ADRs

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | ADR-P1-01 |
| Title | Write P1 Critical ADRs (5 documents) |
| Domain | Documentation |
| Complexity | L (Large) |
| Estimated Effort | 5-10 hours |
| Dependencies | None |
| Blocks | OPT-01 (CONTRIBUTING.md references ADRs) |

---

## Scope

### What This Task Includes

Write the 5 highest-priority Architecture Decision Records that document the core technology and architectural choices:

1. **ADR-001: FastAPI as Backend Framework**
2. **ADR-002: Lit as Frontend Framework**
3. **ADR-004: Keycloak as Identity Provider**
4. **ADR-005: Row-Level Security for Multi-Tenancy**
5. **ADR-013: PKCE Enforcement for Public Clients**

### What This Task Excludes

- P2 ADRs (ADR-003, 006, 007, 009, 010, 012, 014, 016, 018)
- P3 ADRs (ADR-008, 011, 015, 017)
- Updating ADR index status (done after writing)
- CONTRIBUTING.md creation (separate task)

---

## Relevant Code Areas

### ADR Output Location

| ADR | File to Create |
|-----|----------------|
| ADR-001 | `/home/ty/workspace/project-starter/docs/adr/001-fastapi-backend-framework.md` |
| ADR-002 | `/home/ty/workspace/project-starter/docs/adr/002-lit-frontend-framework.md` |
| ADR-004 | `/home/ty/workspace/project-starter/docs/adr/004-keycloak-identity-provider.md` |
| ADR-005 | `/home/ty/workspace/project-starter/docs/adr/005-row-level-security-multitenancy.md` |
| ADR-013 | `/home/ty/workspace/project-starter/docs/adr/013-pkce-enforcement.md` |

### Reference Materials

| ADR | Primary Code Areas to Research |
|-----|-------------------------------|
| ADR-001 | `template/{{cookiecutter.project_slug}}/backend/app/main.py`, `backend/pyproject.toml`, `backend/app/api/` |
| ADR-002 | `template/{{cookiecutter.project_slug}}/frontend/src/`, `frontend/package.json`, `frontend/README.md` |
| ADR-004 | `template/{{cookiecutter.project_slug}}/keycloak/`, `backend/app/auth/`, `docker-compose.yml` |
| ADR-005 | `template/{{cookiecutter.project_slug}}/backend/app/db/`, `backend/alembic/versions/`, SQL files |
| ADR-013 | `template/{{cookiecutter.project_slug}}/frontend/src/auth/`, `keycloak/` configuration |

---

## Implementation Details

### ADR-001: FastAPI as Backend Framework

**Context to Document:**
- Need for a modern Python web framework
- Requirements: async support, automatic API documentation, type safety
- Team familiarity and ecosystem considerations

**Decision Points:**
- FastAPI chosen over Flask, Django, Starlette
- Pydantic for data validation
- Automatic OpenAPI/Swagger documentation
- Native async/await support

**Consequences to Document:**
- Positive: High performance, automatic docs, Pydantic integration
- Negative: Smaller ecosystem than Django, learning curve for async patterns

**Alternatives to Document:**
- Flask: Mature but no native async, manual OpenAPI
- Django: Full-featured but heavier, DRF needed for APIs
- Starlette: Lower-level, more manual work

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── app/main.py          # FastAPI application setup
├── app/api/routers/     # API route definitions
├── app/models/          # Pydantic models
└── pyproject.toml       # FastAPI dependency
```

---

### ADR-002: Lit as Frontend Framework

**Context to Document:**
- Need for a lightweight, standards-based frontend framework
- Web components as the target architecture
- Bundle size and performance considerations

**Decision Points:**
- Lit chosen over React, Vue, Svelte, Angular
- Web Components standard alignment
- No virtual DOM overhead
- Small bundle size (~5KB)

**Consequences to Document:**
- Positive: Small bundle, native web standards, good TypeScript support
- Negative: Smaller community than React, fewer ready-made components

**Alternatives to Document:**
- React: Large ecosystem but larger bundle, virtual DOM
- Vue: Good balance but custom component model
- Svelte: Compile-time but less mature, non-standard syntax
- Angular: Full framework but heavy, steep learning curve

**Code References:**
```
template/{{cookiecutter.project_slug}}/frontend/
├── src/components/      # Lit components
├── src/auth/           # Auth integration
├── package.json        # Lit dependency
└── README.md           # Frontend documentation
```

---

### ADR-004: Keycloak as Identity Provider

**Context to Document:**
- Need for robust OAuth 2.0 / OIDC identity provider
- Self-hosted requirement vs. SaaS preference
- Feature requirements: multi-tenancy, social login, admin UI

**Decision Points:**
- Keycloak chosen over Auth0, Okta, custom implementation
- Self-hosted and open source
- Full OIDC compliance
- Built-in admin console

**Consequences to Document:**
- Positive: Full-featured, open source, self-hosted option, no vendor lock-in
- Negative: Resource heavy, complex configuration, learning curve

**Alternatives to Document:**
- Auth0: Easier setup but SaaS-only, costs at scale
- Okta: Enterprise-grade but expensive
- Custom OAuth: Maximum control but significant development effort

**Code References:**
```
template/{{cookiecutter.project_slug}}/keycloak/
├── setup-realm.sh       # Realm configuration script
├── realm-config.json    # Realm export (if present)
docker-compose.yml       # Keycloak service definition
backend/app/auth/        # Backend integration
```

---

### ADR-005: Row-Level Security for Multi-Tenancy

**Context to Document:**
- Multi-tenant application requirement
- Need for strong tenant data isolation
- Performance considerations with tenant filtering

**Decision Points:**
- PostgreSQL RLS over application-level filtering
- Separate schemas rejected (operational complexity)
- Separate databases rejected (resource overhead)
- tenant_id column approach

**Consequences to Document:**
- Positive: Database-enforced isolation, transparent to application, no bypass possible
- Negative: PostgreSQL-specific, requires careful policy management, debugging complexity

**Alternatives to Document:**
- Application-level filtering: Simpler but error-prone, bypass possible
- Separate schemas: Good isolation but migration complexity
- Separate databases: Maximum isolation but resource intensive

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── app/db/models.py       # Base model with tenant_id
├── app/db/session.py      # RLS context setting
├── alembic/versions/      # RLS policy migrations
└── app/deps.py            # Tenant context injection
```

---

### ADR-013: PKCE Enforcement for Public Clients

**Context to Document:**
- Frontend is a public OAuth client (no client secret)
- Authorization code flow security concerns
- OAuth 2.1 and security best practices

**Decision Points:**
- PKCE (Proof Key for Code Exchange) mandatory
- code_verifier and code_challenge parameters
- S256 challenge method (SHA-256)

**Consequences to Document:**
- Positive: Prevents authorization code interception, OAuth 2.1 compliant
- Negative: Additional complexity in auth flow, requires PKCE-capable IdP

**Alternatives to Document:**
- Implicit flow: Simpler but deprecated, tokens in URL
- No PKCE: Vulnerable to code interception attacks
- BFF pattern: More secure but additional backend complexity

**Code References:**
```
template/{{cookiecutter.project_slug}}/frontend/
├── src/auth/             # PKCE implementation in auth flow
├── src/auth/pkce.ts      # PKCE utility functions (if separate)
keycloak/
├── setup-realm.sh        # PKCE enforcement in client config
```

---

## Success Criteria

1. **File Existence:** All 5 ADR files exist at the specified paths
2. **Format Compliance:** Each ADR follows the format specified in `docs/adr/README.md`
3. **Complete Sections:** Each ADR includes Status, Context, Decision, Consequences, and Alternatives Considered
4. **Accurate Content:** ADRs accurately reflect the actual implementation in the codebase
5. **Code References:** Each ADR references specific code files that implement the decision
6. **Status Update:** After writing, update ADR index status from "Planned" to "Accepted"

---

## Verification Steps

```bash
# Verify all P1 ADR files exist
ls -la /home/ty/workspace/project-starter/docs/adr/001-*.md
ls -la /home/ty/workspace/project-starter/docs/adr/002-*.md
ls -la /home/ty/workspace/project-starter/docs/adr/004-*.md
ls -la /home/ty/workspace/project-starter/docs/adr/005-*.md
ls -la /home/ty/workspace/project-starter/docs/adr/013-*.md

# Verify each ADR contains required sections
for adr in 001 002 004 005 013; do
  echo "=== ADR-$adr ==="
  grep -E "^## (Status|Context|Decision|Consequences|Alternatives)" \
    /home/ty/workspace/project-starter/docs/adr/${adr}-*.md
done

# Verify Status is Accepted
for adr in 001 002 004 005 013; do
  echo "=== ADR-$adr Status ==="
  head -10 /home/ty/workspace/project-starter/docs/adr/${adr}-*.md | grep -A1 "## Status"
done

# Verify ADR index has been updated
grep "Accepted" /home/ty/workspace/project-starter/docs/adr/README.md
```

---

## Integration Points

### Upstream Dependencies

- ADR format and naming convention established in `docs/adr/README.md` (completed)

### Downstream Dependencies

- **OPT-01 (CONTRIBUTING.md):** Will reference P1 ADRs for architectural guidance
- **Future contributors:** Will use ADRs to understand core decisions

### Contracts

**ADR Format Contract:**
Each ADR must include these sections:
- Title with ADR-NNN identifier
- Status (set to "Accepted" after writing)
- Context (problem/motivation)
- Decision (what was chosen)
- Consequences (positive and negative)
- Alternatives Considered (what was rejected and why)

---

## Monitoring and Observability

Not applicable for documentation tasks.

---

## Infrastructure Needs

None - this task creates documentation files only.

---

## Notes

1. **Research Depth:** Each ADR requires examining the codebase to accurately document the implementation. Do not rely solely on FRD descriptions.

2. **Alternatives Quality:** The "Alternatives Considered" section is crucial for P1 ADRs. Include concrete reasons why alternatives were rejected.

3. **Code References:** Include specific file paths that readers can examine to see the decision implemented.

4. **Writing Style:** Use clear, technical language. Avoid marketing speak. Be honest about trade-offs.

5. **Cross-References:** Where appropriate, reference related ADRs (e.g., ADR-001 FastAPI relates to ADR-005 RLS due to database integration).

6. **Keycloak Specifics:** ADR-004 and ADR-013 are closely related - consider documenting together or cross-referencing.

---

## FRD References

- FR-A01: ADR Directory (completed)
- FR-A02: ADR Index File (completed)
- FR-A03: ADR Format
- FR-A04: Minimum ADR Count (18 planned)
- FR-A05: ADR Categories
- FR-A06: ADR Descriptions

---

*Task Created: 2025-12-05*
*Status: Not Started*
