# P4-06: Add Kubernetes Cookiecutter Conditional

## Task Identifier
**ID:** P4-06
**Phase:** 4 - Kubernetes Deployment
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P4-01 | Required | Documented | Kubernetes base manifests must exist before adding conditionals |
| P4-02 | Required | Documented | Staging overlay must exist |
| P4-03 | Required | Documented | Production overlay must exist |

## Scope

### In Scope
- Add `include_kubernetes` variable to `cookiecutter.json` (default: "no")
- Conditionally include entire `k8s/` directory structure
- Update CLAUDE.md with Kubernetes documentation (conditional)
- Update README.md with Kubernetes deployment section (conditional)
- Add GitHub Actions deploy workflow conditional (if `include_github_actions == "yes"`)
- Add post-generation hook validation for Kubernetes configuration
- Test all option combinations in CI

### Out of Scope
- Kubernetes manifest implementation (P4-01, P4-02, P4-03)
- Deploy workflow implementation (P4-04)
- Environment configuration documentation (P4-07)
- ADR documentation (P4-08)

## Relevant Code Areas

### Files to Modify
```
template/cookiecutter.json
template/{{cookiecutter.project_slug}}/README.md
template/{{cookiecutter.project_slug}}/CLAUDE.md
template/{{cookiecutter.project_slug}}/.github/workflows/deploy.yml (if exists)
template/hooks/post_gen_project.py (if exists)
```

### Files to Conditionally Include
```
template/{{cookiecutter.project_slug}}/k8s/
  base/
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
    staging/
      kustomization.yaml
      configmap-patch.yaml
      replicas-patch.yaml
    production/
      kustomization.yaml
      configmap-patch.yaml
      replicas-patch.yaml
      pdb.yaml
  README.md
```

### Existing Pattern Reference
The `include_observability` pattern in cookiecutter.json:
```json
{
  "include_observability": "yes"
}
```

Used in templates like:
```python
{% if cookiecutter.include_observability == "yes" %}
from app.observability import setup_observability
{% endif %}
```

## Implementation Details

### 1. Update cookiecutter.json

Add Kubernetes configuration variable:

```json
{
  // ... existing variables ...

  "include_observability": "yes",
  "include_sentry": "no",

  // GitHub Actions (for CI/CD)
  "include_github_actions": "yes",

  // Kubernetes Deployment (new)
  "include_kubernetes": "no",

  // ... rest of variables ...
}
```

**Note:** Default is "no" because:
- Kubernetes requires cluster infrastructure
- Not all projects will deploy to Kubernetes
- Following opt-in pattern for infrastructure features
- Users should explicitly enable based on deployment target

### 2. Directory Conditional Pattern

Cookiecutter supports directory-level conditionals using special naming:

**Option A: Jinja2 Directory Name (Recommended)**
```
template/{{cookiecutter.project_slug}}/{% if cookiecutter.include_kubernetes == 'yes' %}k8s{% endif %}/
```

However, this creates issues with empty directories. Better approach:

**Option B: Post-Generation Hook (Preferred)**

Use a post-generation hook to remove the k8s directory when not enabled:

```python
# hooks/post_gen_project.py
import os
import shutil

# Remove k8s directory if not enabled
if "{{ cookiecutter.include_kubernetes }}" != "yes":
    k8s_dir = os.path.join(os.getcwd(), "k8s")
    if os.path.exists(k8s_dir):
        shutil.rmtree(k8s_dir)
        print("Removed k8s/ directory (Kubernetes not enabled)")
```

**Option C: Keep Files, Add Conditional README (Fallback)**

If directory removal is complex, keep files but clearly mark them:

```markdown
# k8s/README.md
{% if cookiecutter.include_kubernetes == "no" %}
# Kubernetes Manifests (Not Enabled)

Kubernetes deployment was not enabled for this project.

To enable Kubernetes deployment in a new project:
```bash
cookiecutter template/ include_kubernetes=yes
```

Or manually add the k8s/ manifests to your project.
{% else %}
# Kubernetes Deployment
...
{% endif %}
```

### 3. Post-Generation Hook

Create or update `hooks/post_gen_project.py`:

```python
#!/usr/bin/env python
"""
Post-generation hook for cookiecutter template.

Cleans up files and directories based on selected options.
"""
import os
import shutil


def remove_directory(path: str) -> None:
    """Remove a directory if it exists."""
    full_path = os.path.join(os.getcwd(), path)
    if os.path.exists(full_path):
        shutil.rmtree(full_path)
        print(f"  Removed: {path}/")


def remove_file(path: str) -> None:
    """Remove a file if it exists."""
    full_path = os.path.join(os.getcwd(), path)
    if os.path.exists(full_path):
        os.remove(full_path)
        print(f"  Removed: {path}")


def main() -> None:
    """Main post-generation cleanup."""
    print("Running post-generation cleanup...")

    # Kubernetes conditional
    if "{{ cookiecutter.include_kubernetes }}" != "yes":
        remove_directory("k8s")

    # GitHub Actions conditional
    if "{{ cookiecutter.include_github_actions }}" != "yes":
        remove_directory(".github")

    # Observability conditional (if not already handled)
    if "{{ cookiecutter.include_observability }}" != "yes":
        remove_directory("observability")

    # Sentry conditional (handled inline, but ensure clean)
    # Sentry uses stub pattern, no directory to remove

    print("Post-generation cleanup complete!")


if __name__ == "__main__":
    main()
```

### 4. README.md Conditionals

Add Kubernetes section to project README:

```markdown
{% if cookiecutter.include_kubernetes == "yes" %}
## Kubernetes Deployment

This project includes Kubernetes manifests for deployment using Kustomize.

### Quick Start

```bash
# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to production
kubectl apply -k k8s/overlays/production
```

### Structure

```
k8s/
  base/                 # Base manifests (shared)
  overlays/
    staging/            # Staging environment
    production/         # Production environment
```

### Prerequisites

- Kubernetes cluster (1.25+)
- kubectl with cluster access
- External PostgreSQL and Redis
- OAuth provider (Keycloak)

See [k8s/README.md](k8s/README.md) for detailed deployment instructions.

{% endif %}
```

### 5. CLAUDE.md Conditionals

Add Kubernetes section to CLAUDE.md:

```markdown
{% if cookiecutter.include_kubernetes == "yes" %}
## Kubernetes Deployment

The project includes Kustomize-based Kubernetes manifests.

### Deployment Commands

```bash
# Deploy to staging
kubectl apply -k k8s/overlays/staging

# Deploy to production
kubectl apply -k k8s/overlays/production

# Check deployment status
kubectl get all -n {{ cookiecutter.project_slug }}

# View logs
kubectl logs -n {{ cookiecutter.project_slug }} -l app.kubernetes.io/component=backend

# Port forward for local access
kubectl port-forward -n {{ cookiecutter.project_slug }} svc/backend 8000:8000
```

### Structure

| Directory | Purpose |
|-----------|---------|
| k8s/base/ | Shared manifests (deployments, services, ingress) |
| k8s/overlays/staging/ | Staging overrides (reduced replicas) |
| k8s/overlays/production/ | Production overrides (HA, PDB) |

### Key Resources

| Resource | File | Description |
|----------|------|-------------|
| Namespace | namespace.yaml | Isolated namespace for the project |
| Backend | backend-deployment.yaml | FastAPI backend pods |
| Frontend | frontend-deployment.yaml | Nginx frontend pods |
| ConfigMap | configmap.yaml | Non-sensitive configuration |
| Secret | secret.yaml | Secret template (create manually) |
| Ingress | ingress.yaml | TLS ingress configuration |

### Secrets Management

Secrets should not be committed to version control. Create them manually:

```bash
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --namespace {{ cookiecutter.project_slug }} \
  --from-literal=DATABASE_URL='postgresql+asyncpg://...' \
  --from-literal=REDIS_URL='redis://...'
```

Or use external secret management (Sealed Secrets, External Secrets Operator, Vault).

{% endif %}
```

### 6. Deploy Workflow Conditional

Update deploy.yml to use both conditionals:

```yaml
{% raw %}{% if cookiecutter.include_github_actions == "yes" and cookiecutter.include_kubernetes == "yes" %}{% endraw %}
name: Deploy

on:
  workflow_run:
    workflows: ["Build"]
    types: [completed]
    branches: [main]

  # ... rest of deploy workflow from P4-04 ...
{% raw %}{% endif %}{% endraw %}
```

### 7. Combination Matrix

The Kubernetes conditional should work with other feature flags:

| include_github_actions | include_kubernetes | Result |
|------------------------|-------------------|--------|
| yes | yes | Full CI/CD with K8s deploy |
| yes | no | CI/CD without K8s deploy |
| no | yes | K8s manifests only, manual deploy |
| no | no | No CI/CD, no K8s |

### 8. Validation Tests

```python
# tests/test_cookiecutter_k8s.py
import pytest
import subprocess
from pathlib import Path


@pytest.mark.parametrize("include_kubernetes", ["yes", "no"])
def test_kubernetes_conditional(tmp_path, include_kubernetes):
    """Test Kubernetes cookiecutter conditional generates valid project."""
    result = subprocess.run([
        "cookiecutter", "template/",
        "--no-input",
        "--output-dir", str(tmp_path),
        f"include_kubernetes={include_kubernetes}",
    ], capture_output=True, text=True)

    assert result.returncode == 0

    project_dir = tmp_path / "my-awesome-project"
    k8s_dir = project_dir / "k8s"

    if include_kubernetes == "yes":
        assert k8s_dir.exists()
        assert (k8s_dir / "base" / "kustomization.yaml").exists()
        assert (k8s_dir / "overlays" / "staging" / "kustomization.yaml").exists()
        assert (k8s_dir / "overlays" / "production" / "kustomization.yaml").exists()
    else:
        assert not k8s_dir.exists()


@pytest.mark.parametrize("include_github_actions,include_kubernetes", [
    ("yes", "yes"),
    ("yes", "no"),
    ("no", "yes"),
    ("no", "no"),
])
def test_github_actions_kubernetes_combinations(tmp_path, include_github_actions, include_kubernetes):
    """Test all GitHub Actions + Kubernetes combinations."""
    subprocess.run([
        "cookiecutter", "template/",
        "--no-input",
        "--output-dir", str(tmp_path),
        f"include_github_actions={include_github_actions}",
        f"include_kubernetes={include_kubernetes}",
    ], check=True)

    project_dir = tmp_path / "my-awesome-project"
    github_dir = project_dir / ".github"
    k8s_dir = project_dir / "k8s"

    # Verify directories match expectations
    assert github_dir.exists() == (include_github_actions == "yes")
    assert k8s_dir.exists() == (include_kubernetes == "yes")

    # If both enabled, deploy workflow should exist
    if include_github_actions == "yes" and include_kubernetes == "yes":
        deploy_workflow = github_dir / "workflows" / "deploy.yml"
        assert deploy_workflow.exists()


def test_kubernetes_manifests_valid(tmp_path):
    """Test generated Kubernetes manifests are valid."""
    subprocess.run([
        "cookiecutter", "template/",
        "--no-input",
        "--output-dir", str(tmp_path),
        "include_kubernetes=yes",
    ], check=True)

    project_dir = tmp_path / "my-awesome-project"

    # Validate with kubectl (requires kubectl installed)
    result = subprocess.run([
        "kubectl", "kustomize", str(project_dir / "k8s" / "base"),
    ], capture_output=True, text=True)

    assert result.returncode == 0
```

## Success Criteria

### Functional Requirements
- [ ] `include_kubernetes` variable in cookiecutter.json
- [ ] Default value is "no" (opt-in pattern)
- [ ] When "yes": k8s/ directory included with all manifests
- [ ] When "no": k8s/ directory removed or not generated
- [ ] README.md includes Kubernetes section when enabled
- [ ] CLAUDE.md includes Kubernetes commands when enabled
- [ ] Deploy workflow conditionally included (requires both flags)

### Verification Steps
1. **Generate with Kubernetes enabled:**
   ```bash
   cookiecutter template/ --no-input include_kubernetes=yes
   # Verify: k8s/ directory exists
   # Verify: All base and overlay files present
   # Verify: Kubernetes section in README.md
   ```

2. **Generate with Kubernetes disabled:**
   ```bash
   cookiecutter template/ --no-input include_kubernetes=no
   # Verify: k8s/ directory does not exist
   # Verify: No Kubernetes references in README.md
   ```

3. **Matrix test all combinations:**
   ```bash
   # Test: github_actions=yes, kubernetes=yes
   # Test: github_actions=yes, kubernetes=no
   # Test: github_actions=no, kubernetes=yes
   # Test: github_actions=no, kubernetes=no
   # Also cross with observability and sentry flags
   ```

### Quality Gates
- [ ] All option combinations generate valid projects
- [ ] Post-generation hook runs without errors
- [ ] No orphaned files when kubernetes=no
- [ ] kubectl kustomize validates base manifests
- [ ] Generated project starts successfully

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-01 | k8s/base/ manifests | Must exist before conditional |
| P4-02 | k8s/overlays/staging/ | Must exist before conditional |
| P4-03 | k8s/overlays/production/ | Must exist before conditional |
| P4-04 | deploy.yml workflow | Conditionally included with kubernetes |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-08 | ADR-021 references include_kubernetes | Documents the conditional |
| P6-03 | Template validation tests combinations | Tests this implementation |

### Integration Contract
```json
// cookiecutter.json contract
{
  "include_kubernetes": "yes|no",    // Default: "no"
  "include_github_actions": "yes|no" // Deploy workflow needs both
}
```

## Monitoring and Observability

Not applicable - this is a cookiecutter template modification task.

## Infrastructure Needs

### Template Testing
- CI matrix should test Kubernetes option combinations
- Add to existing template validation tests
- Requires kubectl for manifest validation

### Documentation
- Update template README with Kubernetes option documentation
- Add to feature matrix in project documentation

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Post-generation hook implementation
- Multiple files need Jinja2 conditionals
- Matrix testing required for option combinations
- Validation testing requires kubectl

## Notes

### Design Decisions

**1. Default Value "no":**
Unlike `include_observability` (default "yes") and `include_github_actions` (default "yes"), Kubernetes defaults to "no" because:
- Requires external cluster infrastructure
- Not all projects will deploy to Kubernetes
- Many projects use Docker Compose or serverless
- Following minimal footprint principle

**2. Post-Generation Hook vs. Directory Naming:**
Using post-generation hook instead of Jinja2 directory naming because:
- Cleaner directory structure
- More reliable file removal
- Easier to maintain and test
- Avoids empty directory issues

**3. Deploy Workflow Double Conditional:**
The deploy workflow requires both `include_github_actions` and `include_kubernetes` because:
- No point having deploy workflow without K8s manifests
- No point having K8s deploy without CI/CD pipeline
- Clean separation of concerns

**4. Keep Manifests Separate from App Code:**
Kubernetes manifests in dedicated `k8s/` directory because:
- Clear separation of concerns
- Standard convention in industry
- Easier to manage with GitOps tools
- Does not clutter application code

### Jinja2 Best Practices

1. **Whitespace Control:**
   Use `{%- ... -%}` for conditionals that should not add blank lines
   ```markdown
   {%- if cookiecutter.include_kubernetes == "yes" %}
   ## Kubernetes Deployment
   ...
   {%- endif %}
   ```

2. **Consistent Quoting:**
   Always use double quotes for string comparison
   ```
   {% if cookiecutter.include_kubernetes == "yes" %}
   ```

3. **Combined Conditionals:**
   Use `and` for multiple conditions
   ```
   {% if cookiecutter.include_github_actions == "yes" and cookiecutter.include_kubernetes == "yes" %}
   ```

### Related Requirements
- FR-DEP-001 through FR-DEP-009: Kubernetes deployment requirements
- NFR-006: Optional features shall follow the observability pattern (include_X variable)
- US-4.1: Production Kubernetes Manifests

### Risk Mitigation

**Risk: Post-Generation Hook Failure**
- Mitigation: Comprehensive error handling in hook
- Mitigation: Test hook in CI with all combinations
- Mitigation: Hook should be idempotent

**Risk: Template Syntax Errors**
- Mitigation: Comprehensive matrix testing in CI
- Mitigation: Use cookiecutter's built-in template validation
- Mitigation: Test with real kubectl validation

**Risk: Combination Conflicts**
- Mitigation: Test all combinations: observability x sentry x github_actions x kubernetes
- Mitigation: Independent feature flags where possible
- Mitigation: Document known dependencies (e.g., deploy needs both flags)

### Feature Flag Matrix

Full matrix of feature flags to test:

| observability | sentry | github_actions | kubernetes | Valid |
|---------------|--------|----------------|------------|-------|
| yes | yes | yes | yes | yes |
| yes | yes | yes | no | yes |
| yes | yes | no | yes | yes |
| yes | yes | no | no | yes |
| yes | no | yes | yes | yes |
| yes | no | yes | no | yes |
| yes | no | no | yes | yes |
| yes | no | no | no | yes |
| no | yes | yes | yes | yes |
| no | yes | yes | no | yes |
| no | yes | no | yes | yes |
| no | yes | no | no | yes |
| no | no | yes | yes | yes |
| no | no | yes | no | yes |
| no | no | no | yes | yes |
| no | no | no | no | yes |

All 16 combinations should produce valid, buildable projects.
