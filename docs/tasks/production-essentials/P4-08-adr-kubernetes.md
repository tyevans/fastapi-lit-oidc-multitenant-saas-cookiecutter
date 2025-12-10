# P4-08: Write ADR-021: Kubernetes Deployment

## Task Identifier
**ID:** P4-08
**Phase:** 4 - Kubernetes Deployment
**Domain:** Architecture
**Complexity:** S (Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P4-01 | Required | Documented | Base manifests must exist to document decisions |

## Scope

### In Scope
- Create ADR-021 documenting Kubernetes deployment approach
- Document the decision to use Kustomize over Helm
- Document the decision to use plain manifests as base
- Explain the overlay structure (base, staging, production)
- Document resource management patterns
- Document health probe configuration rationale
- List alternatives considered (Helm, raw YAML, GitOps tools)

### Out of Scope
- Implementation of Kubernetes manifests (P4-01 through P4-06)
- Advanced Kubernetes features (HPA, Network Policies)
- Specific cloud provider documentation
- GitOps tool integration (Argo CD, Flux)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/docs/adr/
  021-kubernetes-deployment.md
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/k8s/base/kustomization.yaml
template/{{cookiecutter.project_slug}}/k8s/base/*.yaml
template/{{cookiecutter.project_slug}}/k8s/overlays/staging/kustomization.yaml
template/{{cookiecutter.project_slug}}/k8s/overlays/production/kustomization.yaml
docs/adr/017-optional-observability-stack.md  # Pattern reference
docs/adr/010-docker-compose-development.md     # Related decision
```

## Implementation Details

### ADR-021: Kubernetes Deployment (`docs/adr/021-kubernetes-deployment.md`)

```markdown
# ADR-021: Kubernetes Deployment Strategy

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | {{ cookiecutter.creation_date }} |
| **Decision Makers** | Project Team |

## Context

{{ cookiecutter.project_name }} needs a Kubernetes deployment strategy for staging and production environments. Key challenges include:

1. **Deployment Complexity**: Kubernetes has a steep learning curve; we need to balance power with accessibility
2. **Environment Variability**: Staging and production require different configurations (replicas, resources, domains)
3. **Template Compatibility**: Deployment manifests must work with cookiecutter templating
4. **Tooling Choices**: Multiple tools exist (Helm, Kustomize, raw YAML, Jsonnet, cdk8s)
5. **Operational Needs**: Must support rolling updates, health checks, and resource limits
6. **Optional Feature**: Not all projects need Kubernetes; it should be opt-in

The template already uses Docker Compose for development (ADR-010). Kubernetes is the target for production deployments where container orchestration, scaling, and high availability are required.

## Decision

We adopt **Kustomize with plain YAML manifests** for Kubernetes deployment, structured as:

```
k8s/
  base/                         # Common configuration
    kustomization.yaml
    namespace.yaml
    backend-deployment.yaml
    backend-service.yaml
    frontend-deployment.yaml
    frontend-service.yaml
    configmap.yaml
    secret.yaml
    ingress.yaml
  overlays/
    staging/                    # Staging overrides
      kustomization.yaml
      configmap-patch.yaml
      replicas-patch.yaml
    production/                 # Production overrides
      kustomization.yaml
      configmap-patch.yaml
      replicas-patch.yaml
      resources-patch.yaml
      pdb.yaml
```

**Deployment Command:**
```bash
# Staging
kubectl apply -k k8s/overlays/staging

# Production
kubectl apply -k k8s/overlays/production
```

**Key Design Principles:**

1. **Plain YAML Base**: Human-readable, IDE-supported, easy to understand
2. **Kustomize Overlays**: Environment-specific patches without duplication
3. **No Templating in Manifests**: Cookiecutter handles project-level templating; Kustomize handles environment-level
4. **Security by Default**: Non-root containers, read-only filesystems, dropped capabilities
5. **Resource Limits**: All containers have requests and limits defined
6. **Health Probes**: Liveness and readiness probes for all services

**Optional Feature Pattern:**
```json
// cookiecutter.json
{
  "include_kubernetes": "no"  // Default: no (opt-in)
}
```

The entire `k8s/` directory is included only when `include_kubernetes == "yes"`, following the pattern established by `include_observability` (ADR-017).

## Consequences

### Positive

1. **No Additional Tooling**: Kustomize is built into `kubectl` since v1.14
   ```bash
   # No installation needed
   kubectl apply -k k8s/overlays/production
   ```

2. **Simple Mental Model**: Base + Overlays is intuitive
   - Base: What's common to all environments
   - Overlay: What's different per environment

3. **GitOps Ready**: Plain YAML works with any GitOps tool (Argo CD, Flux)
   ```yaml
   # Argo CD Application
   source:
     path: k8s/overlays/production
     kustomize:
       images: [...]
   ```

4. **IDE Support**: YAML files are well-supported by editors
   - Kubernetes YAML schema validation
   - Auto-completion for resource fields
   - No custom plugin required (unlike Helm)

5. **Debuggable**: Can preview exactly what will be applied
   ```bash
   kubectl kustomize k8s/overlays/production > rendered.yaml
   ```

6. **Security Best Practices Built-In**:
   - Non-root containers (runAsNonRoot: true)
   - Read-only root filesystem
   - Dropped capabilities
   - Resource limits preventing noisy neighbor issues

7. **Production-Ready Defaults**:
   - Rolling update strategy with maxUnavailable: 0
   - Pod anti-affinity for availability
   - Health probes with appropriate timeouts

### Negative

1. **Limited Templating**: Kustomize patches are less flexible than Helm templates
   - Cannot conditionally include resources based on values
   - Complex transformations require multiple patches

2. **Overlay Duplication**: Similar patches may be repeated across overlays
   - Staging and production may have similar structure
   - Could extract common patterns to intermediate overlays

3. **No Package Management**: Unlike Helm, cannot version or share as packages
   - No chart repository concept
   - Harder to consume third-party applications

4. **Learning Curve**: Strategic merge patches and JSON patches require understanding
   - Patch semantics differ from simple value replacement
   - Debugging patch failures can be challenging

### Neutral

1. **Cookiecutter Compatibility**: Jinja2 templating in YAML works but requires care
   - Double-brace syntax: `{{ "{{" }} cookiecutter.project_slug {{ "}}" }}`
   - YAML indentation must be preserved

2. **Upgrade Path**: Can migrate to Helm if needed
   - Extract manifests as Helm templates
   - Convert values to values.yaml

## Alternatives Considered

### Helm Charts

**Approach**: Use Helm for templating and packaging.

```yaml
# values.yaml
replicaCount: 3
image:
  repository: ghcr.io/owner/app
  tag: v1.0.0
```

**Why Not Chosen**:
- Requires Helm CLI installation
- Template syntax adds complexity ({{ .Values.x }})
- Conflicts with cookiecutter Jinja2 syntax
- Overkill for single-application deployment
- Debugging rendered templates is harder

**When to Reconsider**:
- Multiple applications sharing configuration
- Need to publish as reusable chart
- Complex conditional logic required

### Raw YAML (No Kustomize)

**Approach**: Separate YAML files per environment without tooling.

```
k8s/
  staging/
    deployment.yaml
    service.yaml
  production/
    deployment.yaml
    service.yaml
```

**Why Not Chosen**:
- Massive duplication across environments
- Easy to miss updating one environment
- No DRY (Don't Repeat Yourself) principle

### Jsonnet / cdk8s

**Approach**: Use a programming language for manifest generation.

```jsonnet
// deployment.jsonnet
local k = import 'k.libsonnet';
k.deployment.new('backend', 3, ...)
```

**Why Not Chosen**:
- Requires learning new language/framework
- Additional build step
- IDE support less mature than YAML
- Overkill for template scope

### Terraform Kubernetes Provider

**Approach**: Manage Kubernetes resources via Terraform.

```hcl
resource "kubernetes_deployment" "backend" {
  metadata { name = "backend" }
  spec { ... }
}
```

**Why Not Chosen**:
- Mixes infrastructure and application concerns
- State management complexity
- Slower feedback loop for app changes
- Not standard Kubernetes workflow

---

## Configuration Details

### Resource Defaults

| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|----------------|-----------|--------------|
| Backend (staging) | 50m | 128Mi | 250m | 256Mi |
| Backend (production) | 200m | 512Mi | 1000m | 1Gi |
| Frontend (staging) | 25m | 32Mi | 100m | 64Mi |
| Frontend (production) | 100m | 128Mi | 500m | 256Mi |

### Health Probe Configuration

| Probe | Backend | Frontend |
|-------|---------|----------|
| Liveness Path | /api/v1/health | / |
| Readiness Path | /api/v1/health | / |
| Initial Delay | 30s | 10s |
| Period | 30s | 30s |
| Timeout | 10s | 5s |
| Failure Threshold | 3 | 3 |

### Deployment Strategy

| Environment | Strategy | Max Surge | Max Unavailable |
|-------------|----------|-----------|-----------------|
| Staging | RollingUpdate | 1 | 1 |
| Production | RollingUpdate | 1 | 0 |

**Production Zero-Downtime**: With `maxUnavailable: 0`, at least the current number of pods are always available during updates.

### Security Context

All containers run with:
```yaml
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

---

## Related ADRs

- [ADR-010: Docker Compose Development](./010-docker-compose-development.md) - Local development environment
- [ADR-016: Cookiecutter Template Engine](./016-cookiecutter-template-engine.md) - Template conditionals
- [ADR-017: Optional Observability Stack](./017-optional-observability-stack.md) - Optional feature pattern

## Implementation References

- `k8s/base/` - Base manifests
- `k8s/overlays/staging/` - Staging overlay
- `k8s/overlays/production/` - Production overlay
- `k8s/README.md` - Deployment documentation
- `cookiecutter.json` - `include_kubernetes` variable
```

## Success Criteria

### Functional Requirements
- [ ] NFR-001: ADR documentation for Kubernetes deployment exists
- [ ] ADR follows established ADR format (Status, Date, Context, Decision, Consequences)
- [ ] Kustomize decision is clearly justified
- [ ] Alternatives are documented with reasons for rejection
- [ ] Security decisions are documented
- [ ] Resource management approach is documented

### Verification Steps
1. **Format Validation:**
   ```bash
   # Check ADR exists
   test -f docs/adr/021-kubernetes-deployment.md

   # Verify required sections
   grep -q "## Context" docs/adr/021-kubernetes-deployment.md
   grep -q "## Decision" docs/adr/021-kubernetes-deployment.md
   grep -q "## Consequences" docs/adr/021-kubernetes-deployment.md
   grep -q "## Alternatives Considered" docs/adr/021-kubernetes-deployment.md
   ```

2. **Cross-Reference Check:**
   - Verify ADR references correct file paths
   - Verify related ADRs exist and are linked
   - Check consistency with actual manifest structure

3. **README Update:**
   ```bash
   # ADR should be listed in docs/adr/README.md
   grep -q "021-kubernetes-deployment" docs/adr/README.md
   ```

### Quality Gates
- [ ] ADR number is unique (021)
- [ ] Status is "Accepted"
- [ ] Date is set
- [ ] All required sections present
- [ ] At least 3 alternatives considered
- [ ] Positive and negative consequences documented
- [ ] Related ADRs linked
- [ ] Implementation references provided

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-01 | Manifest structure and security patterns | ADR documents these decisions |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-01 | ADR-021 exists | CLAUDE.md update references ADRs |
| P6-02 | Kubernetes approach | Migration guide references ADR |

### Integration Contract
```yaml
# Contract: ADR-021 structure

# File location
docs/adr/021-kubernetes-deployment.md

# Required sections
- Context (problem statement)
- Decision (Kustomize with overlays)
- Consequences (positive, negative, neutral)
- Alternatives Considered (Helm, raw YAML, Jsonnet)
- Configuration Details (resources, probes, security)
- Related ADRs
- Implementation References

# ADR README update
docs/adr/README.md must include link to ADR-021
```

## Monitoring and Observability

Not applicable - this is a documentation task.

## Infrastructure Needs

No infrastructure required - documentation only.

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5 days
**Justification:**
- ADR template is well-established
- Decisions are already made in P4-01
- Mainly documenting existing choices
- Related ADRs provide pattern to follow

## Notes

### Design Decisions

**1. ADR-021 Numbering:**
- Follows sequential ADR numbering
- ADR-019 (CI/CD) and ADR-020 (Security Headers) precede this
- ADR-022 onwards for Phase 3+ decisions

**2. Focus on "Why Kustomize":**
- Most important decision to document
- Alternatives section helps future maintainers
- Provides upgrade path to Helm if needed

**3. Include Configuration Tables:**
- Resource defaults documented in ADR
- Health probe configuration documented
- Serves as quick reference

**4. Reference Implementation Files:**
- Links to actual k8s/ directory
- Helps readers navigate codebase
- Keeps ADR and implementation in sync

### ADR Best Practices

From Michael Nygard's ADR format:
- **Context**: Forces articulation of the problem
- **Decision**: Clear statement of what we decided
- **Consequences**: Honest assessment of tradeoffs
- **Alternatives**: Shows due diligence in research

### Style Guidelines

- Use tables for configuration details
- Include code examples for key concepts
- Link to related ADRs
- Keep neutral/factual tone
- Avoid implementation details (that's for task docs)

### Related Requirements
- NFR-001: All new features shall have corresponding ADR documentation
- US-4.1: Production Kubernetes Manifests
