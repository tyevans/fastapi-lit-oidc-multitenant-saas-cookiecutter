# P3-11: Write ADR-024: Sentry Integration

## Task Identifier

| Field | Value |
|-------|-------|
| **Task ID** | P3-11 |
| **Task Title** | Write ADR-024: Sentry Integration |
| **Domain** | Architecture |
| **Complexity** | S (Small) |
| **Estimated Effort** | 0.5-1 day |
| **Priority** | Should Have |
| **Dependencies** | P3-03 (Sentry Integration) |
| **FRD Requirements** | NFR-001 |

---

## Scope

### What This Task Includes

1. Create ADR-024 documenting Sentry integration decisions
2. Document the choice of Sentry as error tracking solution
3. Explain optional integration pattern (follows `include_observability`)
4. Document fail-open pattern for error tracking
5. Document PII filtering approach
6. Explain multi-tenant context attachment
7. List considered alternatives and why they were rejected
8. Include integration architecture diagram

### What This Task Excludes

- Implementation of Sentry integration (P3-03)
- Cookiecutter conditional implementation (P3-04)
- Frontend Sentry integration (out of scope for this FRD)
- Alertmanager/PagerDuty integration

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
docs/
  adr/
    024-sentry-integration.md
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `docs/adr/017-optional-observability-stack.md` | ADR format and optional feature pattern |
| `backend/app/sentry.py` | Sentry implementation (P3-03) |
| `backend/app/core/config.py` | Sentry configuration settings |

---

## Technical Specification

### ADR-024: Sentry Integration

```markdown
# docs/adr/024-sentry-integration.md
# ADR-024: Sentry Error Tracking Integration

## Status

Accepted

## Date

{{ cookiecutter._creation_date }}

## Context

{{ cookiecutter.project_name }} needs a production-grade error tracking solution to:

1. **Capture unhandled exceptions** with full stack traces and context
2. **Correlate errors** with user sessions and tenant IDs for multi-tenant support
3. **Track releases** to identify regressions introduced by deployments
4. **Filter sensitive data** (PII) before transmission
5. **Integrate seamlessly** with the existing FastAPI/SQLAlchemy stack

### Requirements

| Requirement | Description |
|-------------|-------------|
| Exception capture | Automatic capture of unhandled exceptions |
| Stack traces | Full Python stack traces with local variables |
| User context | Attach user_id and tenant_id to errors |
| Release tracking | Correlate errors with deployment versions |
| PII filtering | Remove passwords, tokens, and sensitive data |
| Performance tracing | Optional request performance monitoring |
| Fail-open | Application works if error tracking unavailable |

### Constraints

- Must be optional (not all deployments need error tracking)
- Must follow existing cookiecutter conditional pattern
- Must not impact application performance significantly
- Must handle multi-tenant context properly
- SaaS or self-hosted deployment options required

## Decision

We will implement **optional Sentry integration** as the error tracking solution,
following these principles:

### 1. Error Tracking Platform: Sentry

**Choice:** Sentry SDK with FastAPI and SQLAlchemy integrations

**Rationale:**
- Industry-standard error tracking platform
- Excellent Python SDK with automatic framework detection
- First-party FastAPI and SQLAlchemy integrations
- Supports both SaaS and self-hosted deployment
- Free tier suitable for development and small projects
- Comprehensive context capture (request, user, breadcrumbs)

### 2. Integration Pattern: Optional via Cookiecutter

**Choice:** Use `include_sentry` cookiecutter variable following ADR-017 pattern

**Implementation:**
```python
{% raw %}{% if cookiecutter.include_sentry == "yes" %}{% endraw %}
from app.sentry import init_sentry
init_sentry(settings)
{% raw %}{% endif %}{% endraw %}
```

**Rationale:**
- Consistent with existing observability stack optional pattern
- No runtime overhead when disabled
- Clean codebase without error tracking when not needed
- Easy to enable/disable at project generation time

### 3. Initialization Pattern: Fail-Open

**Choice:** Application starts normally if Sentry is misconfigured or unavailable

**Implementation:**
```python
def init_sentry(settings: Settings) -> bool:
    if not settings.SENTRY_DSN:
        logger.info("SENTRY_DSN not configured - error tracking disabled")
        return False
    try:
        sentry_sdk.init(...)
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False  # Continue without error tracking
```

**Rationale:**
- Error tracking should never block application startup
- Development environments work without Sentry configuration
- Graceful degradation on network issues or misconfiguration
- Clear logging indicates Sentry status

### 4. Multi-Tenant Context: User and Tenant Tags

**Choice:** Attach tenant_id as both user context and tag

**Implementation:**
```python
def set_user_context(user_id: str, tenant_id: str, email: str = None):
    sentry_sdk.set_user({
        "id": user_id,
        "tenant_id": tenant_id,
        "email": email,
    })
    sentry_sdk.set_tag("tenant_id", tenant_id)
```

**Rationale:**
- Enables filtering errors by tenant in Sentry UI
- Supports multi-tenant debugging and impact analysis
- User context provides authentication correlation
- Tags enable dashboards and alerts by tenant

### 5. PII Filtering: Before-Send Hook

**Choice:** Filter sensitive data using before_send hook

**Implementation:**
```python
PII_FIELDS = {"password", "secret", "api_key", "access_token", ...}

def _before_send(event, hint):
    # Filter request body
    if "request" in event and "data" in event["request"]:
        for key in event["request"]["data"]:
            if key.lower() in PII_FIELDS:
                event["request"]["data"][key] = "[Filtered]"
    # Filter headers
    if "request" in event and "headers" in event["request"]:
        for key in ["Authorization", "Cookie", "X-API-Key"]:
            if key in event["request"]["headers"]:
                event["request"]["headers"][key] = "[Filtered]"
    return event
```

**Rationale:**
- GDPR and privacy compliance
- Prevents credential exposure in error reports
- Consistent filtering across all events
- Extensible for application-specific fields

### 6. Configuration: Environment Variables

**Choice:** All Sentry configuration via environment variables

**Variables:**
| Variable | Default | Description |
|----------|---------|-------------|
| SENTRY_DSN | "" | Sentry project DSN (empty = disabled) |
| SENTRY_ENVIRONMENT | development | Environment tag |
| SENTRY_RELEASE | APP_VERSION | Release version for tracking |
| SENTRY_TRACES_SAMPLE_RATE | 0.1 | Performance trace sampling (10%) |

**Rationale:**
- Follows 12-factor app configuration
- Easy to configure per environment
- DSN as secret - not committed to repository
- Sensible defaults for development

## Alternatives Considered

### Alternative 1: Rollbar

**Pros:**
- Good Python support
- Simpler pricing model
- Decent feature set

**Cons:**
- Smaller community and ecosystem
- Fewer integrations
- No self-hosted option

**Decision:** Rejected. Sentry has broader adoption, better FastAPI integration,
and self-hosted option for sensitive deployments.

### Alternative 2: Bugsnag

**Pros:**
- Good stability monitoring
- Release health tracking
- Solid Python SDK

**Cons:**
- Less comprehensive than Sentry
- Fewer framework integrations
- Higher pricing for comparable features

**Decision:** Rejected. Sentry provides more features at the free tier and better
matches our FastAPI/SQLAlchemy stack.

### Alternative 3: Application Insights (Azure)

**Pros:**
- Deep Azure integration
- Comprehensive APM features
- Log correlation

**Cons:**
- Azure-specific
- More complex setup
- Python SDK less mature than Sentry

**Decision:** Rejected. Template aims for cloud-agnostic deployment. Teams using
Azure can substitute Application Insights if preferred.

### Alternative 4: Self-Built Error Tracking

**Pros:**
- Full control
- No external dependencies
- No cost

**Cons:**
- Significant development effort
- Maintenance burden
- Missing advanced features (deduplication, trends, etc.)

**Decision:** Rejected. Building error tracking is not a differentiating feature
for most applications. Sentry provides proven functionality.

### Alternative 5: No Error Tracking (Logs Only)

**Pros:**
- No additional dependencies
- Existing Loki stack captures logs
- Simpler architecture

**Cons:**
- No aggregation or deduplication
- Harder to identify trends
- No user impact analysis
- Missing stack trace correlation

**Decision:** Rejected for production. Logs are valuable but insufficient for
effective error management. Sentry complements logging, not replaces it.

## Consequences

### Positive

1. **Proactive Error Detection:** Errors captured before users report them
2. **Context-Rich Debugging:** Full stack traces with request and user context
3. **Multi-Tenant Visibility:** Filter and analyze errors by tenant
4. **Release Correlation:** Identify regressions from deployments
5. **Minimal Code Impact:** Single initialization point, automatic capture
6. **Privacy Compliant:** PII filtered before transmission

### Negative

1. **External Dependency:** Requires Sentry account or self-hosted instance
2. **Network Overhead:** Events sent to external service (async, minimal impact)
3. **Learning Curve:** Team needs familiarity with Sentry UI
4. **Cost at Scale:** High error volumes may require paid tier

### Trade-offs

| Aspect | Choice | Trade-off |
|--------|--------|-----------|
| SaaS vs Self-Hosted | SaaS default | Convenience vs data control |
| Sampling | 10% traces | Cost vs visibility |
| PII Filtering | Aggressive | Privacy vs debugging detail |
| Optional | Yes | Simplicity vs always-on |

## Architecture

### Integration Points

```
                                    ┌─────────────────────┐
                                    │   Sentry Cloud      │
                                    │   (or self-hosted)  │
                                    └──────────▲──────────┘
                                               │
                                               │ HTTPS
                                               │
┌──────────────────────────────────────────────┴───────────────┐
│                        Backend Service                        │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │   FastAPI   │────▶│   sentry.py │────▶│  Sentry SDK │    │
│  │  Middleware │     │  init/hooks │     │  (async)    │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│         │                   │                               │
│         │            ┌──────┴──────┐                        │
│         │            │ before_send │                        │
│         │            │ (PII filter)│                        │
│         │            └─────────────┘                        │
│         │                                                    │
│  ┌──────▼──────┐     ┌─────────────┐                        │
│  │    Auth     │────▶│set_user_ctx │                        │
│  │ Dependency  │     │(tenant_id)  │                        │
│  └─────────────┘     └─────────────┘                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Exception Occurs:** Unhandled exception in request handler
2. **SDK Captures:** Sentry SDK intercepts and enriches with context
3. **PII Filtering:** before_send hook removes sensitive data
4. **Async Transmission:** Event queued and sent asynchronously
5. **Sentry Processing:** Deduplication, grouping, alerting
6. **Developer Review:** Error appears in Sentry dashboard

## Implementation

### File Structure

```
backend/
  app/
    sentry.py           # Sentry initialization and helpers
    core/
      config.py         # Sentry configuration settings
    api/
      dependencies/
        auth.py         # User context attachment

.env.example            # SENTRY_DSN placeholder
```

### Configuration

```python
# config.py
class Settings(BaseSettings):
    # Sentry Configuration
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_RELEASE: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
```

### Initialization

```python
# main.py
{% raw %}{% if cookiecutter.include_sentry == "yes" %}{% endraw %}
from app.sentry import init_sentry
sentry_enabled = init_sentry(settings)
{% raw %}{% endif %}{% endraw %}
```

### Cookiecutter Variable

```json
// cookiecutter.json
{
  "include_sentry": ["no", "yes"]
}
```

## Complementary Stack

Sentry complements existing observability:

| Tool | Purpose | Overlap |
|------|---------|---------|
| Prometheus | Metrics | None - different data |
| Loki | Logs | Breadcrumbs also capture logs |
| Tempo | Traces | Sentry traces are separate |
| Grafana | Visualization | Sentry has own dashboard |
| Sentry | Error Tracking | Primary error management |

## Related Decisions

- [ADR-017: Optional Observability Stack](./017-optional-observability-stack.md) - Follows optional pattern
- [ADR-019: GitHub Actions CI/CD](./019-github-actions-cicd.md) - Release tracking integration
- [ADR-023: Database Backup Strategy](./023-database-backup-strategy.md) - Follows documentation pattern

## References

- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Sentry FastAPI Integration](https://docs.sentry.io/platforms/python/integrations/fastapi/)
- [Sentry Self-Hosted](https://develop.sentry.dev/self-hosted/)
- [GDPR and Sentry](https://sentry.io/security/#gdpr)
```

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P3-03 | Required | Documents decisions implemented in Sentry module |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| None | - | ADR is standalone documentation |

---

## Success Criteria

### Functional Requirements

- [ ] NFR-001: All new features shall have corresponding ADR documentation
- [ ] ADR follows established format (Status, Date, Context, Decision, etc.)
- [ ] Documents Sentry as chosen error tracking platform
- [ ] Documents optional integration pattern
- [ ] Documents fail-open initialization pattern
- [ ] Documents PII filtering approach
- [ ] Documents multi-tenant context attachment
- [ ] Lists considered alternatives with pros/cons
- [ ] Includes integration architecture diagram
- [ ] References related ADRs

### Non-Functional Requirements

- [ ] ADR is concise and well-structured
- [ ] Technical accuracy in Sentry SDK details
- [ ] Consistent with existing ADR style
- [ ] Proper markdown formatting
- [ ] Diagram renders correctly

### Validation Steps

1. Format validation
   - Verify all ADR sections present
   - Check markdown rendering
   - Verify diagram displays correctly
   - Verify internal links work

2. Technical review
   - Verify Sentry recommendations are accurate
   - Confirm rationale aligns with implementation
   - Check alternatives are fairly presented

3. Cross-reference validation
   - Verify consistency with P3-03 implementation
   - Check related ADR references

---

## Integration Points

### ADR Numbering

- Follows sequential numbering: ADR-024
- Previous: ADR-023 (Database Backup Strategy)
- Next: ADR-025 (reserved for future)

### Related ADRs

| ADR | Relationship |
|-----|--------------|
| ADR-017 | Follows optional feature pattern |
| ADR-019 | CI/CD integration for release tracking |
| ADR-023 | Follows documentation pattern |

---

## Monitoring and Observability

### No Runtime Impact

This task creates documentation only; no runtime monitoring required.

### Documentation Health

Consider periodic review of ADRs to ensure they remain accurate as Sentry SDK evolves.

---

## Infrastructure Needs

### No Infrastructure Changes Required

This task creates an ADR document only.

---

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Single document creation
- Decisions already made in P3-03
- Template structure exists from other ADRs
- Primarily documentation synthesis
- Includes architecture diagram

---

## Implementation Notes

### ADR Writing Guidelines

1. **Context First:** Explain the problem before the solution
2. **Be Specific:** Include concrete examples and code snippets
3. **Document Alternatives:** Show thoughtful consideration
4. **Acknowledge Trade-offs:** Be honest about consequences
5. **Link Related Work:** Cross-reference other ADRs

### Key Decisions to Document

| Decision | Rationale |
|----------|-----------|
| Sentry over alternatives | Industry standard, best FastAPI support |
| Optional via cookiecutter | Follows ADR-017 pattern |
| Fail-open pattern | Error tracking shouldn't block startup |
| PII filtering | Privacy compliance |
| Multi-tenant context | Supports SaaS debugging |
| Environment config | 12-factor app principles |

### Alternatives to Cover

- Rollbar
- Bugsnag
- Application Insights
- Self-built error tracking
- Logs only (no error tracking)

### Diagram Requirements

Include architecture diagram showing:
- Backend service
- Sentry SDK integration
- before_send hook
- User context attachment
- Data flow to Sentry

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| NFR-001 | All new features shall have corresponding ADR documentation | ADR-024 |

### Related Tasks

- P3-03: Implement Optional Sentry Integration
- P3-04: Add Sentry Cookiecutter Conditional

### External Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)
- [Architecture Decision Records](https://adr.github.io/)
