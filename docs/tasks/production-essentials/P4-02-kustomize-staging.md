# P4-02: Create Kustomize Staging Overlay

## Task Identifier
**ID:** P4-02
**Phase:** 4 - Kubernetes Deployment
**Domain:** DevOps
**Complexity:** S (Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P4-01 | Required | Documented | Base manifests must exist for overlay to patch |

## Scope

### In Scope
- Create staging overlay directory structure (`k8s/overlays/staging/`)
- Create `kustomization.yaml` referencing base resources
- Create ConfigMap patch with staging-specific values
- Create replica patch (reduced replicas for cost savings)
- Create resource patch (reduced limits for staging)
- Create image tag patch for staging images
- Add staging-specific annotations (environment labels)
- Configure staging ingress hostnames

### Out of Scope
- Production overlay (P4-03)
- Base manifests modification (P4-01)
- GitHub Actions deployment (P4-04)
- Actual secret values (documentation only)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/k8s/overlays/staging/
  kustomization.yaml
  configmap-patch.yaml
  replicas-patch.yaml
  resources-patch.yaml
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/k8s/base/kustomization.yaml
template/{{cookiecutter.project_slug}}/k8s/base/configmap.yaml
template/{{cookiecutter.project_slug}}/k8s/base/backend-deployment.yaml
template/{{cookiecutter.project_slug}}/k8s/base/frontend-deployment.yaml
template/{{cookiecutter.project_slug}}/k8s/base/ingress.yaml
```

## Implementation Details

### 1. Staging Kustomization (`k8s/overlays/staging/kustomization.yaml`)

```yaml
# {{ cookiecutter.project_name }} Kubernetes Staging Overlay
#
# Staging environment configuration with reduced resources for cost efficiency.
# Inherits from base/ and applies staging-specific patches.
#
# Deploy: kubectl apply -k k8s/overlays/staging
# Review: kubectl kustomize k8s/overlays/staging

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# Reference the base configuration
resources:
  - ../../base

# Staging namespace suffix (optional - keeps resources in same namespace)
# nameSuffix: -staging

# Additional staging labels
commonLabels:
  app.kubernetes.io/environment: staging

# Common annotations for all resources
commonAnnotations:
  environment: staging
  managed-by: kustomize

# Image customization
images:
  - name: ghcr.io/OWNER/{{ cookiecutter.project_slug }}-backend
    newTag: staging
  - name: ghcr.io/OWNER/{{ cookiecutter.project_slug }}-frontend
    newTag: staging

# Patches to apply
patches:
  # ConfigMap values for staging
  - path: configmap-patch.yaml

  # Reduced replicas for staging
  - path: replicas-patch.yaml

  # Reduced resources for staging
  - path: resources-patch.yaml

  # Staging ingress hosts
  - target:
      kind: Ingress
      name: {{ cookiecutter.project_slug }}-ingress
    patch: |-
      - op: replace
        path: /spec/rules/0/host
        value: staging.example.com
      - op: replace
        path: /spec/rules/1/host
        value: api-staging.example.com
      - op: replace
        path: /spec/tls/0/hosts
        value:
          - staging.example.com
          - api-staging.example.com
      - op: replace
        path: /spec/tls/0/secretName
        value: {{ cookiecutter.project_slug }}-staging-tls
```

### 2. ConfigMap Patch (`k8s/overlays/staging/configmap-patch.yaml`)

```yaml
# Staging environment configuration overrides
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ cookiecutter.project_slug }}-config
data:
  # Environment identifier
  ENV: "staging"

  # More verbose logging for debugging
  LOG_LEVEL: "debug"
  DEBUG: "true"

  # Staging OAuth provider
  # Update with your staging Keycloak URL
  OAUTH_ISSUER_URL: "https://auth-staging.example.com/realms/{{ cookiecutter.keycloak_realm_name }}"

  # Staging frontend API URL
  VITE_API_URL: "https://api-staging.example.com"
```

### 3. Replicas Patch (`k8s/overlays/staging/replicas-patch.yaml`)

```yaml
# Reduced replicas for staging environment
# Cost optimization: staging doesn't need high availability
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 1
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 1
```

### 4. Resources Patch (`k8s/overlays/staging/resources-patch.yaml`)

```yaml
# Reduced resource limits for staging environment
# Staging workloads typically have less traffic than production
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
        - name: backend
          resources:
            requests:
              cpu: 50m
              memory: 128Mi
            limits:
              cpu: 250m
              memory: 256Mi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  template:
    spec:
      containers:
        - name: frontend
          resources:
            requests:
              cpu: 25m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 64Mi
```

## Success Criteria

### Functional Requirements
- [ ] Staging overlay inherits all base resources
- [ ] ConfigMap is patched with staging-specific values
- [ ] Replicas are reduced for cost optimization
- [ ] Resources are reduced for staging workloads
- [ ] Image tags point to staging images
- [ ] Ingress hosts are staging-specific

### Verification Steps
1. **Kustomize Build:**
   ```bash
   # Build and review rendered manifests
   kubectl kustomize k8s/overlays/staging

   # Verify staging values in output
   kubectl kustomize k8s/overlays/staging | grep -A5 "ENV:"
   ```

2. **Diff from Base:**
   ```bash
   # Compare staging to base
   diff <(kubectl kustomize k8s/base) <(kubectl kustomize k8s/overlays/staging)
   ```

3. **Validate Manifests:**
   ```bash
   # Dry-run apply
   kubectl apply -k k8s/overlays/staging --dry-run=client

   # Server-side validation
   kubectl apply -k k8s/overlays/staging --dry-run=server
   ```

4. **Verify Replicas:**
   ```bash
   # Check replicas are reduced
   kubectl kustomize k8s/overlays/staging | grep "replicas:"
   # Expected: replicas: 1 (not 2)
   ```

5. **Verify Resources:**
   ```bash
   # Check reduced resource limits
   kubectl kustomize k8s/overlays/staging | grep -A5 "resources:"
   ```

### Quality Gates
- [ ] `kubectl kustomize` succeeds without errors
- [ ] All base resources are included
- [ ] Staging-specific values are correctly applied
- [ ] No hardcoded secrets in overlay files
- [ ] Labels include environment: staging

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-01 | Base manifest structure | Overlay patches base resources |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-04 | Overlay path `k8s/overlays/staging` | Deploy workflow applies this overlay |

### Integration Contract
```yaml
# Contract: Staging overlay structure

# Directory
k8s/overlays/staging/
  kustomization.yaml    # References ../../base
  configmap-patch.yaml
  replicas-patch.yaml
  resources-patch.yaml

# Kustomize command
kubectl apply -k k8s/overlays/staging

# Labels added
app.kubernetes.io/environment: staging

# Image tags
backend: staging
frontend: staging

# Replicas
backend: 1
frontend: 1

# Resource limits (reduced from base)
backend:  250m CPU, 256Mi memory
frontend: 100m CPU, 64Mi memory
```

## Monitoring and Observability

### Staging-Specific Metrics
Consider enabling more verbose logging in staging:
```yaml
LOG_LEVEL: "debug"
```

### Cost Monitoring
With reduced replicas and resources, staging cluster costs should be approximately:
- 50% of production CPU allocation
- 50% of production memory allocation

## Infrastructure Needs

### Staging Cluster Requirements
- Kubernetes cluster (can be shared with other staging environments)
- Reduced node count compared to production
- Staging secrets configured

### DNS Configuration
- `staging.example.com` -> Staging Ingress
- `api-staging.example.com` -> Staging Ingress

### TLS Certificates
- Staging TLS secret: `{{ cookiecutter.project_slug }}-staging-tls`
- Can use cert-manager with staging issuer

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Straightforward Kustomize overlay creation
- Patterns established in base manifests
- Mostly configuration value changes
- Limited testing required

## Notes

### Design Decisions

**1. Single Replica:**
Staging uses single replicas because:
- Reduces costs
- Sufficient for testing and validation
- Production HA is tested in production overlay

**2. Debug Logging:**
Enabled in staging for:
- Easier troubleshooting
- Development team visibility
- Not performance-critical

**3. Reduced Resources:**
Staging resources are halved because:
- Lower traffic expectations
- Cost optimization
- Production sizing validated separately

**4. Strategic Merge Patches:**
Using multiple small patch files because:
- Easier to understand and maintain
- Can selectively apply patches
- Clear separation of concerns

### Staging vs Production Differences
| Aspect | Staging | Production |
|--------|---------|------------|
| Replicas | 1 | 2+ |
| Log Level | debug | info |
| Resources | Reduced | Full |
| TLS | Staging certs | Production certs |
| Domains | *-staging.* | Production domains |

### Security Considerations
- Staging should use separate secrets from production
- Staging database should be isolated
- Consider data masking for staging test data
- Restrict staging access to development team

### Related Requirements
- US-4.2: Environment Configuration Management
- FR-DEP-010: Environment configuration documentation shall list required variables
