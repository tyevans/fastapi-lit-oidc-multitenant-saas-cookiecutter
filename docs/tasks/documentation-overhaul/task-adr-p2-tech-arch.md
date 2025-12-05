# ADR-P2-01: Write P2 Important ADRs - Technology & Architecture

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | ADR-P2-01 |
| Title | Write P2 Important ADRs - Technology & Architecture (5 documents) |
| Domain | Documentation |
| Complexity | L (Large) |
| Estimated Effort | 5-10 hours |
| Dependencies | None |
| Blocks | None |

---

## Scope

### What This Task Includes

Write 5 Architecture Decision Records covering technology choices and architectural patterns:

1. **ADR-003: PostgreSQL as Primary Database**
2. **ADR-006: Dual Database Users Pattern**
3. **ADR-007: Redis Token Revocation Strategy**
4. **ADR-009: Cookie-Based Authentication Transport**
5. **ADR-014: Rate Limiting Strategy**

### What This Task Excludes

- P1 ADRs (separate task ADR-P1-01)
- P2 Operations/Template ADRs (separate task ADR-P2-02)
- P3 ADRs (separate task ADR-P3-01)

---

## Relevant Code Areas

### ADR Output Location

| ADR | File to Create |
|-----|----------------|
| ADR-003 | `/home/ty/workspace/project-starter/docs/adr/003-postgresql-primary-database.md` |
| ADR-006 | `/home/ty/workspace/project-starter/docs/adr/006-dual-database-users.md` |
| ADR-007 | `/home/ty/workspace/project-starter/docs/adr/007-redis-token-revocation.md` |
| ADR-009 | `/home/ty/workspace/project-starter/docs/adr/009-cookie-based-auth-transport.md` |
| ADR-014 | `/home/ty/workspace/project-starter/docs/adr/014-rate-limiting-strategy.md` |

### Reference Materials

| ADR | Primary Code Areas to Research |
|-----|-------------------------------|
| ADR-003 | `template/{{cookiecutter.project_slug}}/backend/app/db/`, `docker-compose.yml`, `alembic.ini` |
| ADR-006 | `template/{{cookiecutter.project_slug}}/backend/alembic/env.py`, database initialization scripts |
| ADR-007 | `template/{{cookiecutter.project_slug}}/backend/app/auth/`, Redis configuration |
| ADR-009 | `template/{{cookiecutter.project_slug}}/backend/app/auth/`, cookie settings, CORS config |
| ADR-014 | `template/{{cookiecutter.project_slug}}/backend/app/api/`, rate limiting middleware |

---

## Implementation Details

### ADR-003: PostgreSQL as Primary Database

**Context to Document:**
- Need for a robust, feature-rich relational database
- Requirements: Row-Level Security support, JSON capabilities, mature ecosystem
- Considerations: Cloud provider support, tooling

**Decision Points:**
- PostgreSQL chosen over MySQL, MongoDB, SQLite
- Version 16+ for modern features
- RLS capability critical for multi-tenancy

**Consequences to Document:**
- Positive: RLS support, JSONB, excellent tooling, reliability
- Negative: Slightly more resource-intensive than MySQL, less familiar to some developers

**Alternatives to Document:**
- MySQL: Popular but no native RLS, less JSON support
- MongoDB: Document store but no relational integrity, different paradigm
- SQLite: Lightweight but no multi-connection, limited features

**Code References:**
```
template/{{cookiecutter.project_slug}}/
├── docker-compose.yml      # PostgreSQL service definition
├── backend/app/db/
│   ├── session.py         # Database session management
│   └── models.py          # SQLAlchemy models
└── backend/alembic/        # Migration framework
```

---

### ADR-006: Dual Database Users Pattern

**Context to Document:**
- RLS policies apply to all queries including migrations
- Migrations need to bypass RLS to modify schema
- Principle of least privilege for application user

**Decision Points:**
- Two PostgreSQL users: migration user and application user
- Migration user: bypasses RLS, used only for schema changes
- Application user: RLS enforced, used at runtime
- Separate connection strings in configuration

**Consequences to Document:**
- Positive: Migrations work correctly, least privilege, defense in depth
- Negative: Two connection strings to manage, additional complexity

**Alternatives to Document:**
- Single user with RLS disable/enable: Risk of forgetting to re-enable
- Application-level bypass: Defeats purpose of RLS
- Schema-only user: Similar but less granular

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── alembic/env.py           # Migration database URL
├── app/db/session.py        # Application database URL
├── .env.example             # Both DATABASE_URL variables
└── docker-compose.yml       # PostgreSQL user creation
```

---

### ADR-007: Redis Token Revocation Strategy

**Context to Document:**
- JWTs are stateless and cannot be invalidated after issuance
- Need for logout and token revocation capability
- Performance requirements for token validation

**Decision Points:**
- Redis blacklist for revoked tokens
- Store revoked token IDs with TTL matching token expiry
- Check blacklist on each authenticated request

**Consequences to Document:**
- Positive: Fast lookups, automatic cleanup via TTL, simple implementation
- Negative: Network hop for each request, Redis dependency, memory usage

**Alternatives to Document:**
- Short-lived tokens only: Simple but poor UX (frequent re-auth)
- Token introspection: Standards-based but network overhead to IdP
- Database storage: Reliable but slower, no automatic cleanup

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── app/auth/token_blacklist.py    # Blacklist implementation
├── app/auth/deps.py               # Token validation with blacklist check
├── app/api/routers/auth.py        # Logout endpoint
└── docker-compose.yml             # Redis service
```

---

### ADR-009: Cookie-Based Authentication Transport

**Context to Document:**
- Need to transport access tokens from frontend to backend
- Security considerations: XSS, CSRF, token theft
- Browser security model alignment

**Decision Points:**
- HTTP-only cookies over Authorization header
- Secure flag for HTTPS
- SameSite=Lax for CSRF protection
- CSRF token for state-changing requests

**Consequences to Document:**
- Positive: XSS-resistant (JavaScript cannot access), automatic sending
- Negative: CSRF considerations, cookie size limits, CORS complexity

**Alternatives to Document:**
- Authorization header: Simple but XSS-vulnerable (stored in JavaScript memory)
- localStorage/sessionStorage: Convenient but XSS-vulnerable
- BFF pattern: Most secure but requires additional backend

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── app/auth/cookies.py          # Cookie configuration
├── app/api/routers/auth.py      # Cookie setting on login
├── app/main.py                  # CORS configuration
└── frontend/src/auth/           # Frontend auth handling
```

---

### ADR-014: Rate Limiting Strategy

**Context to Document:**
- Need to protect API from abuse and DDoS
- Fair resource allocation among users/tenants
- Balance between security and user experience

**Decision Points:**
- Redis-based rate limiting (sliding window)
- Per-user and per-IP limits
- Default limits with configurability
- 429 Too Many Requests response

**Consequences to Document:**
- Positive: DDoS protection, fair usage, Redis efficiency
- Negative: Redis dependency, potential legitimate user impact, configuration complexity

**Alternatives to Document:**
- In-memory rate limiting: No shared state across instances
- Database-based: Persistent but slower
- API Gateway: External but adds infrastructure

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── app/api/middleware/rate_limit.py    # Rate limiting implementation
├── app/api/deps.py                     # Rate limit dependency
├── app/core/config.py                  # Rate limit configuration
└── .env.example                        # Rate limit environment variables
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
# Verify all ADR files exist
for adr in 003 006 007 009 014; do
  ls -la /home/ty/workspace/project-starter/docs/adr/${adr}-*.md
done

# Verify each ADR contains required sections
for adr in 003 006 007 009 014; do
  echo "=== ADR-$adr ==="
  grep -E "^## (Status|Context|Decision|Consequences|Alternatives)" \
    /home/ty/workspace/project-starter/docs/adr/${adr}-*.md
done

# Count total words per ADR (should be substantial, 200+ words minimum)
for adr in 003 006 007 009 014; do
  echo -n "ADR-$adr: "
  wc -w /home/ty/workspace/project-starter/docs/adr/${adr}-*.md | tail -1
done
```

---

## Integration Points

### Upstream Dependencies

- ADR format and naming convention established in `docs/adr/README.md`
- Can reference P1 ADRs if completed (ADR-003 relates to ADR-005 RLS)

### Downstream Dependencies

- None directly, but contributes to complete ADR documentation

### Cross-References

- ADR-003 (PostgreSQL) relates to ADR-005 (RLS) and ADR-006 (Dual Users)
- ADR-007 (Redis Token) relates to ADR-009 (Cookie Auth)
- ADR-014 (Rate Limiting) relates to ADR-018 (Always-On Multi-Tenancy)

---

## Monitoring and Observability

Not applicable for documentation tasks.

---

## Infrastructure Needs

None - this task creates documentation files only.

---

## Notes

1. **Technical Depth:** P2 ADRs often involve more technical implementation details. Include code snippets where helpful.

2. **Security Focus:** ADR-007, ADR-009, and ADR-014 have security implications. Document threat models where relevant.

3. **Cross-Reference P1:** Where these ADRs relate to P1 decisions, include cross-references (e.g., ADR-003 relates to ADR-005).

4. **Redis Common Theme:** ADR-007 and ADR-014 both use Redis. Consider noting this shared dependency.

5. **Performance Considerations:** Include performance rationale where relevant (Redis choice for speed, etc.).

---

## FRD References

- FR-A03: ADR Format
- FR-A04: Minimum ADR Count (18 planned)
- FR-A05: ADR Categories (Architecture Patterns, Security Decisions)
- ADR Index entries for ADR-003, 006, 007, 009, 014

---

*Task Created: 2025-12-05*
*Status: Not Started*
