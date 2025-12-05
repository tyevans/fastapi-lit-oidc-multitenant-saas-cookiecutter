# ADR-P3-01: Write P3 Nice-to-Have ADRs

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | ADR-P3-01 |
| Title | Write P3 Nice-to-Have ADRs (4 documents) |
| Domain | Documentation |
| Complexity | M (Medium) |
| Estimated Effort | 4-6 hours |
| Dependencies | None |
| Blocks | None |

---

## Scope

### What This Task Includes

Write 4 Architecture Decision Records that provide additional context but are not critical for understanding core architecture:

1. **ADR-008: JWKS Caching Strategy**
2. **ADR-011: Port Allocation Strategy**
3. **ADR-015: CORS Configuration Approach**
4. **ADR-017: Optional Observability Stack**

### What This Task Excludes

- P1 ADRs (separate task ADR-P1-01)
- P2 ADRs (separate tasks ADR-P2-01, ADR-P2-02)
- Non-ADR documentation tasks

---

## Relevant Code Areas

### ADR Output Location

| ADR | File to Create |
|-----|----------------|
| ADR-008 | `/home/ty/workspace/project-starter/docs/adr/008-jwks-caching-strategy.md` |
| ADR-011 | `/home/ty/workspace/project-starter/docs/adr/011-port-allocation-strategy.md` |
| ADR-015 | `/home/ty/workspace/project-starter/docs/adr/015-cors-configuration.md` |
| ADR-017 | `/home/ty/workspace/project-starter/docs/adr/017-optional-observability.md` |

### Reference Materials

| ADR | Primary Code Areas to Research |
|-----|-------------------------------|
| ADR-008 | `template/{{cookiecutter.project_slug}}/backend/app/auth/jwks.py` or JWT validation code |
| ADR-011 | `template/{{cookiecutter.project_slug}}/docker-compose.yml`, `.env.example` |
| ADR-015 | `template/{{cookiecutter.project_slug}}/backend/app/main.py`, CORS middleware |
| ADR-017 | `template/{{cookiecutter.project_slug}}/observability/`, `cookiecutter.json` |

---

## Implementation Details

### ADR-008: JWKS Caching Strategy

**Context to Document:**
- JWT validation requires public keys from identity provider
- JWKS (JSON Web Key Set) endpoint provides these keys
- Network latency and availability concerns
- Key rotation requirements

**Decision Points:**
- Cache JWKS locally with TTL
- Refresh on cache miss or key rotation
- Fallback behavior on JWKS endpoint unavailability
- Cache duration trade-offs

**Consequences to Document:**
- Positive: Reduced latency, resilience to brief IdP outages
- Negative: Stale key risk during rotation, cache invalidation complexity

**Alternatives to Document:**
- No caching: Simple but poor performance, IdP dependency
- Long-lived cache: Better performance but key rotation delays
- Pre-configured keys: No network calls but no rotation support

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── app/auth/jwks.py           # JWKS fetching and caching (if separate)
├── app/auth/jwt.py            # JWT validation with cached keys
├── app/core/config.py         # JWKS cache TTL configuration
└── .env.example               # JWKS-related environment variables
```

---

### ADR-011: Port Allocation Strategy

**Context to Document:**
- Multiple services require network ports
- Conflict avoidance with common local services
- Developer convenience for debugging
- Convention over configuration

**Decision Points:**
- PostgreSQL: 5435 (not default 5432 to avoid conflicts)
- Keycloak: 8080 (standard)
- Backend: 8000 (FastAPI default)
- Frontend: 3000 (standard dev server)
- Redis: 6379 (default, less conflict risk)

**Consequences to Document:**
- Positive: Avoids common conflicts, predictable ports
- Negative: Non-standard PostgreSQL port may confuse some tools

**Alternatives to Document:**
- Default ports: Simpler but conflict-prone
- Randomized ports: No conflicts but discovery complexity
- Environment-variable only: Flexible but no sensible defaults

**Code References:**
```
template/{{cookiecutter.project_slug}}/
├── docker-compose.yml         # Port mappings
├── .env.example              # Port environment variables
├── backend/app/core/config.py # Port configuration
└── frontend/vite.config.ts    # Frontend dev server port (if applicable)
```

---

### ADR-015: CORS Configuration Approach

**Context to Document:**
- Frontend and backend on different origins during development
- Security implications of permissive CORS
- Production vs. development requirements
- Credential handling with CORS

**Decision Points:**
- Environment-based origin configuration
- Permissive in development, restrictive in production
- Credentials allowed (for cookies)
- Specific methods and headers allowed

**Consequences to Document:**
- Positive: Flexible configuration, secure defaults
- Negative: Configuration complexity, potential misconfiguration in production

**Alternatives to Document:**
- Wildcard origins: Simple but insecure
- Same-origin only: Secure but requires reverse proxy
- BFF pattern: Avoids CORS but additional complexity

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── app/main.py                 # CORS middleware configuration
├── app/core/config.py          # CORS settings
├── .env.example               # CORS origin environment variable
└── docker-compose.yml         # Service origins
```

---

### ADR-017: Optional Observability Stack

**Context to Document:**
- Observability is valuable but resource-intensive
- Not all projects need full monitoring stack in development
- Trade-off between completeness and simplicity

**Decision Points:**
- Observability stack as optional cookiecutter variable
- Includes: Prometheus, Grafana, Loki (if applicable)
- Opt-in at project generation time
- Self-contained when enabled

**Consequences to Document:**
- Positive: Resource savings when not needed, simpler default setup
- Negative: Conditional complexity in template, two configurations to maintain

**Alternatives to Document:**
- Always included: Consistent but resource-heavy
- Never included: Simple but missing production tooling
- External tooling: Flexible but integration complexity

**Code References:**
```
template/
├── cookiecutter.json                           # observability variable
├── {{cookiecutter.project_slug}}/
│   ├── observability/                          # Conditional directory
│   │   ├── docker-compose.observability.yml
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   └── loki/
│   └── docker-compose.yml                      # Conditional service includes
```

---

## Success Criteria

1. **File Existence:** All 4 ADR files exist at the specified paths
2. **Format Compliance:** Each ADR follows the format specified in `docs/adr/README.md`
3. **Complete Sections:** Each ADR includes Status, Context, Decision, Consequences, and Alternatives Considered
4. **Accurate Content:** ADRs accurately reflect the actual implementation in the codebase
5. **Code References:** Each ADR references specific code files that implement the decision
6. **Status Update:** After writing, update ADR index status from "Planned" to "Accepted"

---

## Verification Steps

```bash
# Verify all ADR files exist
for adr in 008 011 015 017; do
  ls -la /home/ty/workspace/project-starter/docs/adr/${adr}-*.md
done

# Verify each ADR contains required sections
for adr in 008 011 015 017; do
  echo "=== ADR-$adr ==="
  grep -E "^## (Status|Context|Decision|Consequences|Alternatives)" \
    /home/ty/workspace/project-starter/docs/adr/${adr}-*.md
done

# Verify reasonable content length
for adr in 008 011 015 017; do
  echo -n "ADR-$adr: "
  wc -w /home/ty/workspace/project-starter/docs/adr/${adr}-*.md | tail -1
done
```

---

## Integration Points

### Upstream Dependencies

- ADR format and naming convention established in `docs/adr/README.md`

### Downstream Dependencies

- None directly, contributes to complete ADR documentation

### Cross-References

- ADR-008 (JWKS) relates to ADR-004 (Keycloak) and ADR-013 (PKCE)
- ADR-011 (Ports) relates to ADR-010 (Docker Compose)
- ADR-015 (CORS) relates to ADR-009 (Cookie Auth)
- ADR-017 (Observability) relates to ADR-016 (Cookiecutter)

---

## Monitoring and Observability

Not applicable for documentation tasks.

---

## Infrastructure Needs

None - this task creates documentation files only.

---

## Notes

1. **Lower Priority:** These ADRs are "nice to have" - they complete the documentation but are not critical for understanding core architecture.

2. **Shorter Documents:** P3 ADRs may be shorter than P1/P2 as they cover more tactical decisions.

3. **Cross-Reference Higher Priority:** Link to related P1/P2 ADRs where appropriate.

4. **Implementation Verification:** Some implementations (like JWKS caching) may need code investigation to document accurately.

5. **Observability Specifics:** ADR-017 should document what's included in the observability stack and how it's conditionally included.

---

## FRD References

- FR-A03: ADR Format
- FR-A04: Minimum ADR Count (18 planned)
- FR-A05: ADR Categories (Architecture Patterns, Operational Decisions, Security Decisions, Template Design)
- ADR Index entries for ADR-008, 011, 015, 017

---

*Task Created: 2025-12-05*
*Status: Not Started*
