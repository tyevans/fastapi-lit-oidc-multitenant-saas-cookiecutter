# P2-07: Write ADR-020: Security Headers

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P2-07 |
| **Task Title** | Write ADR-020: Security Headers |
| **Domain** | Architecture |
| **Complexity** | S (Small) |
| **Estimated Effort** | 0.5 days |
| **Priority** | Should Have |
| **Dependencies** | P2-01 (Security headers middleware must exist to document) |
| **FRD Requirements** | NFR-001, FR-SEC-001 through FR-SEC-006 |

---

## Scope

### What This Task Includes

1. Write ADR-020 documenting security headers middleware decisions
2. Document the security headers implemented (CSP, HSTS, X-Frame-Options, etc.)
3. Document the rationale for each header and its default value
4. Document Lit component compatibility considerations (unsafe-inline requirements)
5. Document environment variable configuration approach
6. Document alternatives considered (nginx-only headers, third-party libraries)
7. Document consequences and trade-offs
8. Follow existing ADR format from docs/adr/

### What This Task Excludes

- Container security scanning ADR (P2-08)
- Security headers implementation (P2-01)
- Security configuration integration (P2-02)
- Frontend nginx security headers documentation
- CSP reporting endpoint design (future enhancement)

---

## Relevant Code Areas

### Files to Create

```
docs/adr/
  020-security-headers.md      # New ADR document
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `docs/adr/017-optional-observability-stack.md` | Template for ADR format |
| `docs/adr/README.md` | ADR index and conventions |
| `docs/tasks/production-essentials/P2-01-security-headers-middleware.md` | Implementation specification |
| `template/{{cookiecutter.project_slug}}/backend/app/middleware/security.py` | Implementation to document |
| `template/{{cookiecutter.project_slug}}/frontend/nginx.conf` | Existing frontend headers |

---

## Technical Specification

### ADR Document Structure

The ADR should follow the established format from existing ADRs:

```markdown
# ADR-020: Security Headers Middleware

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | YYYY-MM-DD |
| **Decision Makers** | Project Team |
| **Related ADRs** | ADR-017 (Cookiecutter Conditionals) |

## Context

The project-starter template generates FastAPI applications that may be deployed
in production environments facing the public internet. Modern web applications
require security headers to mitigate common vulnerabilities including:

- Cross-Site Scripting (XSS)
- Clickjacking
- MIME type sniffing attacks
- Man-in-the-middle attacks (via insecure connections)
- Information leakage through referrer headers

While the frontend nginx.conf already includes some security headers (X-Frame-Options,
X-Content-Type-Options, X-XSS-Protection), the backend API needs equivalent protection
for direct API access and responses that bypass the frontend proxy.

### Constraints

1. **Lit Component Compatibility**: The frontend uses Lit web components that require
   `'unsafe-inline'` in CSP for both script-src and style-src directives
2. **Development vs Production**: HSTS should only be added for HTTPS connections to
   avoid breaking development environments
3. **Configurability**: Different deployments may have different security requirements
4. **Performance**: Headers should not add measurable latency

## Decision

We implement a `SecurityHeadersMiddleware` for FastAPI that adds the following
security headers to all responses:

### Headers Implemented

| Header | Default Value | Rationale |
|--------|--------------|-----------|
| Content-Security-Policy | `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'` | XSS mitigation with Lit compatibility |
| Strict-Transport-Security | `max-age=31536000; includeSubDomains` | HTTPS enforcement (conditional) |
| X-Frame-Options | `DENY` | Clickjacking protection |
| X-Content-Type-Options | `nosniff` | MIME sniffing prevention |
| Referrer-Policy | `strict-origin-when-cross-origin` | Privacy protection |
| X-XSS-Protection | `1; mode=block` | Legacy browser XSS filter |

### Implementation Approach

1. **Middleware Pattern**: Following existing `TenantResolutionMiddleware` pattern
2. **Dataclass Configuration**: `SecurityHeadersConfig` dataclass for type-safe config
3. **Header Pre-computation**: CSP and HSTS headers built once at initialization
4. **HTTPS Detection**: Checks both URL scheme and X-Forwarded-Proto header
5. **Individual Disabling**: Any header can be disabled by setting to None/False

### Configuration via Environment Variables

All headers are configurable via environment variables in config.py:

```python
SECURITY_HEADERS_ENABLED: bool = True
CSP_DEFAULT_SRC: str = "'self'"
CSP_SCRIPT_SRC: str = "'self' 'unsafe-inline'"
CSP_STYLE_SRC: str = "'self' 'unsafe-inline'"
HSTS_MAX_AGE: int = 31536000
X_FRAME_OPTIONS: str = "DENY"
REFERRER_POLICY: str = "strict-origin-when-cross-origin"
```

### Cookiecutter Conditional

Security headers are opt-in via `include_security_headers` cookiecutter variable,
following the pattern established in ADR-017 for optional features.

## Consequences

### Positive

1. **Defense in Depth**: Backend adds headers regardless of frontend proxy configuration
2. **OWASP Compliance**: Addresses security header recommendations from OWASP
3. **Flexibility**: All headers configurable for different deployment requirements
4. **Developer Experience**: Sensible defaults work out of the box
5. **Lit Compatible**: CSP configuration tested with Lit web components

### Negative

1. **CSP Limitations**: `'unsafe-inline'` required for Lit reduces XSS protection
2. **Configuration Complexity**: Many environment variables to manage
3. **Header Duplication**: Some headers may be set by both nginx and backend

### Neutral

1. Future enhancement could implement CSP nonces for stricter security
2. CSP reporting endpoint could be added for violation monitoring
3. Permissions-Policy header could be added in future iteration

## Alternatives Considered

### 1. Nginx-Only Headers
- **Pros**: Single configuration location, simpler backend
- **Cons**: Doesn't protect direct API access, less flexible per-route
- **Why Rejected**: Backend middleware provides defense in depth

### 2. Third-Party Library (secure)
- **Pros**: Mature, well-tested, comprehensive
- **Cons**: Additional dependency, less control, may include unnecessary features
- **Why Rejected**: Custom middleware is simpler and more aligned with project patterns

### 3. FastAPI Dependency Injection
- **Pros**: Per-route control, explicit
- **Cons**: Must be added to every route, easy to forget
- **Why Rejected**: Middleware ensures all responses are protected

## Implementation References

- Middleware: `template/{{cookiecutter.project_slug}}/backend/app/middleware/security.py`
- Configuration: `template/{{cookiecutter.project_slug}}/backend/app/core/config.py`
- Tests: `template/{{cookiecutter.project_slug}}/backend/tests/unit/middleware/test_security.py`

## External References

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [Lit and Content Security Policy](https://lit.dev/docs/security/trusted-types/)
```

### Key Content Requirements

#### Context Section Must Cover

1. Why backend needs security headers (not just nginx)
2. Lit component compatibility constraints
3. Development vs production HTTPS considerations
4. Links to OWASP security header guidelines

#### Decision Section Must Cover

1. Each header implemented with rationale
2. Default values and why they were chosen
3. CSP `'unsafe-inline'` requirement for Lit
4. HSTS conditional behavior (HTTPS-only)
5. Configuration approach via environment variables
6. Cookiecutter conditional pattern

#### Consequences Section Must Cover

1. **Positive**: Defense in depth, OWASP compliance, flexibility
2. **Negative**: CSP limitations due to Lit, configuration complexity
3. **Neutral**: Future enhancement opportunities (CSP nonces, Permissions-Policy)

#### Alternatives Section Must Cover

1. Nginx-only headers (rejected: no direct API protection)
2. Third-party library like `secure` (rejected: additional dependency)
3. Dependency injection approach (rejected: must be added to every route)

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-01 | Required | Middleware implementation must exist to document |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P2-06 | Reference | Security checklist references ADR-020 |
| P6-01 | Reference | CLAUDE.md update references ADR-020 |

---

## Success Criteria

### Functional Requirements

- [ ] ADR-020 created in docs/adr/ directory
- [ ] ADR follows established format from existing ADRs
- [ ] Context section explains why security headers are needed
- [ ] Decision section documents all implemented headers
- [ ] Each header has documented rationale and default value
- [ ] Lit component compatibility documented and explained
- [ ] Environment variable configuration approach documented
- [ ] Cookiecutter conditional pattern documented
- [ ] Alternatives section covers nginx-only, third-party, and DI approaches
- [ ] Consequences section covers positive, negative, and neutral outcomes
- [ ] Implementation references point to correct file paths

### Non-Functional Requirements

- [ ] ADR is clear and understandable to developers unfamiliar with the project
- [ ] Technical accuracy verified against implementation (P2-01)
- [ ] External references to OWASP and MDN included
- [ ] ADR index (docs/adr/README.md) updated with new entry

### Validation Steps

1. Review ADR-020 against ADR template from existing ADRs
2. Verify all headers from P2-01 are documented
3. Verify CSP configuration matches Lit component requirements
4. Verify alternatives considered are relevant and accurately described
5. Verify file paths in implementation references are correct
6. Verify ADR index updated

---

## Integration Points

### ADR Index Update

Update `docs/adr/README.md` to include:

```markdown
| ADR-020 | Security Headers Middleware | Accepted | Security |
```

### Cross-References

The ADR should reference:
- ADR-017 (Cookiecutter Conditionals) for the optional feature pattern
- P2-01 task document for implementation details

### Related Documentation

After this ADR is written:
- P2-06 security checklist should reference ADR-020
- P6-01 CLAUDE.md update should mention ADR-020

---

## Monitoring and Observability

### Not Applicable

This is a documentation task with no runtime monitoring requirements.

---

## Infrastructure Needs

### No Additional Infrastructure Required

This task creates documentation only.

### Development Requirements

- Access to docs/adr/ directory
- Familiarity with existing ADR format
- Understanding of P2-01 implementation

---

## Implementation Notes

### ADR Numbering

ADR-020 follows ADR-019 (GitHub Actions CI/CD). Verify no gaps in numbering and that ADR-019 doesn't already exist with different content.

### OWASP Alignment

The ADR should reference OWASP Secure Headers Project recommendations:
- https://owasp.org/www-project-secure-headers/
- Specifically the HTTP Response Headers section

### CSP Complexity

The Content-Security-Policy section deserves special attention:
1. Explain why each directive is needed
2. Explain why `'unsafe-inline'` is required for Lit
3. Note that nonces would be more secure but require more complexity
4. Provide guidance on customizing CSP for specific deployments

### Header Overlap Documentation

Note that some headers (X-Frame-Options, X-Content-Type-Options) may be set by both nginx and backend. Document that this is intentional for defense in depth, and browsers use the most restrictive value.

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| NFR-001 | All features shall have ADR documentation | This task |
| FR-SEC-001 | CSP header | Documented in ADR |
| FR-SEC-002 | HSTS header | Documented in ADR |
| FR-SEC-003 | X-Frame-Options header | Documented in ADR |
| FR-SEC-004 | X-Content-Type-Options header | Documented in ADR |
| FR-SEC-005 | Referrer-Policy header | Documented in ADR |
| FR-SEC-006 | Headers configurable via environment | Documented in ADR |

### Related ADRs

- ADR-017: Optional Observability Stack (cookiecutter conditional pattern)
- ADR-019: GitHub Actions CI/CD (workflow patterns)

### External Resources

- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN HTTP Security Headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers#security)
- [Lit Security - Trusted Types](https://lit.dev/docs/security/trusted-types/)
- [Content-Security-Policy.com](https://content-security-policy.com/)
