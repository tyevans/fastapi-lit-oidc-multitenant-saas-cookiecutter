# ADR-P2-02: Write P2 Important ADRs - Operations & Template Design

## Task Metadata

| Field | Value |
|-------|-------|
| Task ID | ADR-P2-02 |
| Title | Write P2 Important ADRs - Operations & Template Design (4 documents) |
| Domain | Documentation |
| Complexity | M (Medium) |
| Estimated Effort | 4-6 hours |
| Dependencies | None |
| Blocks | None |

---

## Scope

### What This Task Includes

Write 4 Architecture Decision Records covering operational and template design decisions:

1. **ADR-010: Docker Compose for Development**
2. **ADR-012: uv as Python Package Manager**
3. **ADR-016: Cookiecutter as Template Engine**
4. **ADR-018: Always-On Multi-Tenancy**

### What This Task Excludes

- P1 ADRs (separate task ADR-P1-01)
- P2 Technology/Architecture ADRs (separate task ADR-P2-01)
- P3 ADRs (separate task ADR-P3-01)

---

## Relevant Code Areas

### ADR Output Location

| ADR | File to Create |
|-----|----------------|
| ADR-010 | `/home/ty/workspace/project-starter/docs/adr/010-docker-compose-development.md` |
| ADR-012 | `/home/ty/workspace/project-starter/docs/adr/012-uv-package-manager.md` |
| ADR-016 | `/home/ty/workspace/project-starter/docs/adr/016-cookiecutter-template-engine.md` |
| ADR-018 | `/home/ty/workspace/project-starter/docs/adr/018-always-on-multitenancy.md` |

### Reference Materials

| ADR | Primary Code Areas to Research |
|-----|-------------------------------|
| ADR-010 | `template/{{cookiecutter.project_slug}}/docker-compose*.yml`, Dockerfile files |
| ADR-012 | `template/{{cookiecutter.project_slug}}/backend/pyproject.toml`, `uv.lock` |
| ADR-016 | `template/cookiecutter.json`, `hooks/`, project structure |
| ADR-018 | `template/{{cookiecutter.project_slug}}/backend/app/db/`, `cookiecutter.json` |

---

## Implementation Details

### ADR-010: Docker Compose for Development

**Context to Document:**
- Need for consistent development environment across team members
- Multiple services to orchestrate (backend, frontend, database, Keycloak, Redis)
- Balance between simplicity and production parity

**Decision Points:**
- Docker Compose as primary development environment
- Single `docker-compose.yml` with optional overrides
- Health checks for service readiness
- Volume mounts for hot reload

**Consequences to Document:**
- Positive: Reproducible environment, easy onboarding, service orchestration
- Negative: Docker overhead, resource usage, potential platform differences

**Alternatives to Document:**
- Local installation: Faster but environment inconsistency
- Kubernetes (minikube/kind): Production parity but complex for development
- devcontainers: Good IDE integration but Docker dependency remains

**Code References:**
```
template/{{cookiecutter.project_slug}}/
├── docker-compose.yml           # Main compose file
├── docker-compose.override.yml  # Development overrides (if present)
├── backend/Dockerfile           # Backend container
├── frontend/Dockerfile          # Frontend container (if present)
└── scripts/docker-dev.sh        # Development scripts
```

---

### ADR-012: uv as Python Package Manager

**Context to Document:**
- Need for fast, reliable Python dependency management
- Modern Python packaging standards (PEP 517, 621)
- Developer experience (speed, reproducibility)

**Decision Points:**
- uv chosen over pip, poetry, pipenv
- pyproject.toml as single configuration file
- uv.lock for reproducible builds
- Virtual environment management via uv

**Consequences to Document:**
- Positive: 10-100x faster than pip, reproducible, modern standards
- Negative: Newer tool (less proven), team learning curve

**Alternatives to Document:**
- pip + requirements.txt: Universal but slow, no lock file
- poetry: Popular but slower, custom lock format
- pipenv: Feature-rich but performance issues, less maintained
- pip-tools: Good but more manual setup

**Code References:**
```
template/{{cookiecutter.project_slug}}/backend/
├── pyproject.toml     # Project configuration and dependencies
├── uv.lock           # Locked dependencies (if present)
└── README.md         # uv usage instructions
```

---

### ADR-016: Cookiecutter as Template Engine

**Context to Document:**
- Need for project scaffolding tool
- Requirements: Python ecosystem, Jinja2 templating, hooks
- Adoption and community considerations

**Decision Points:**
- Cookiecutter over Copier, Yeoman, custom solution
- Jinja2 templating for flexibility
- Pre/post generation hooks for customization
- Conditional file inclusion

**Consequences to Document:**
- Positive: Mature ecosystem, well-documented, Python native
- Negative: Limited update mechanism, no interactive prompts during generation

**Alternatives to Document:**
- Copier: Better update support but smaller community
- Yeoman: JavaScript ecosystem, more generators available
- Custom solution: Maximum control but maintenance burden
- GitHub template repositories: Simple but no variable substitution

**Code References:**
```
template/
├── cookiecutter.json                    # Template variables and defaults
├── {{cookiecutter.project_slug}}/       # Template directory
└── hooks/
    ├── pre_gen_project.py               # Pre-generation validation
    └── post_gen_project.py              # Post-generation cleanup
```

---

### ADR-018: Always-On Multi-Tenancy

**Context to Document:**
- Original template had optional multi-tenancy
- Complexity of maintaining two code paths
- Production readiness considerations

**Decision Points:**
- Multi-tenancy always enabled (not optional)
- Rate limiting always enabled (not optional)
- Simplifies template maintenance
- Provides secure-by-default configuration

**Consequences to Document:**
- Positive: Single code path, simpler maintenance, secure defaults
- Negative: Cannot generate single-tenant projects, slight overhead

**Alternatives to Document:**
- Optional via cookiecutter variable: More flexibility but complex maintenance
- Separate template: Clear separation but duplication
- Feature flags at runtime: Maximum flexibility but complex

**Code References:**
```
template/cookiecutter.json                    # Removed multi-tenancy toggle
template/{{cookiecutter.project_slug}}/
├── backend/app/db/models.py                 # tenant_id on all models
├── backend/app/db/rls_policies.py           # RLS always applied
└── backend/app/api/middleware/rate_limit.py # Rate limiting always enabled
```

**Related Documentation:**
- `docs/todo.txt`: "we removed the ability to generate projects without multitenancy or rate limiting"

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
for adr in 010 012 016 018; do
  ls -la /home/ty/workspace/project-starter/docs/adr/${adr}-*.md
done

# Verify each ADR contains required sections
for adr in 010 012 016 018; do
  echo "=== ADR-$adr ==="
  grep -E "^## (Status|Context|Decision|Consequences|Alternatives)" \
    /home/ty/workspace/project-starter/docs/adr/${adr}-*.md
done

# Verify reasonable content length
for adr in 010 012 016 018; do
  echo -n "ADR-$adr: "
  wc -w /home/ty/workspace/project-starter/docs/adr/${adr}-*.md | tail -1
done
```

---

## Integration Points

### Upstream Dependencies

- ADR format and naming convention established in `docs/adr/README.md`

### Downstream Dependencies

- None directly, but contributes to complete ADR documentation

### Cross-References

- ADR-010 (Docker Compose) relates to ADR-011 (Port Allocation, P3)
- ADR-016 (Cookiecutter) relates to ADR-017 (Optional Observability, P3)
- ADR-018 (Always-On Multi-Tenancy) relates to ADR-005 (RLS) and ADR-014 (Rate Limiting)

---

## Monitoring and Observability

Not applicable for documentation tasks.

---

## Infrastructure Needs

None - this task creates documentation files only.

---

## Notes

1. **Template-Level Decisions:** ADR-016 and ADR-018 are about the template itself, not generated projects. Frame context accordingly.

2. **Recent Change Context:** ADR-018 documents a recent decision (removing optional multi-tenancy). Reference the docs/todo.txt item.

3. **Tool Evaluation:** ADR-012 (uv) documents a relatively new tool choice. Include version considerations and maturity assessment.

4. **Practical Examples:** For ADR-010, include practical benefits like "new developer onboarding time reduced from X to Y".

5. **Cross-Reference P1:** ADR-018 heavily relates to ADR-005 (RLS). Ensure cross-referencing.

---

## FRD References

- FR-A03: ADR Format
- FR-A04: Minimum ADR Count (18 planned)
- FR-A05: ADR Categories (Operational Decisions, Template Design)
- ADR Index entries for ADR-010, 012, 016, 018

---

*Task Created: 2025-12-05*
*Status: Not Started*
