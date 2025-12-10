# P4-03: Create Kustomize Production Overlay

## Task Identifier
**ID:** P4-03
**Phase:** 4 - Kubernetes Deployment
**Domain:** DevOps
**Complexity:** S (Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P4-01 | Required | Documented | Base manifests must exist for overlay to patch |

## Scope

### In Scope
- Create production overlay directory structure (`k8s/overlays/production/`)
- Create `kustomization.yaml` referencing base resources
- Create ConfigMap patch with production-specific values
- Create replica patch (increased replicas for high availability)
- Create resource patch (production-appropriate limits)
- Create image tag patch for production images (semantic versions)
- Add production-specific annotations
- Configure production ingress hostnames
- Add pod anti-affinity for high availability
- Add pod disruption budget recommendation (documented, not enforced)

### Out of Scope
- Staging overlay (P4-02)
- Base manifests modification (P4-01)
- GitHub Actions deployment (P4-04)
- HPA implementation (documented as future enhancement)
- Actual secret values (documentation only)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/k8s/overlays/production/
  kustomization.yaml
  configmap-patch.yaml
  replicas-patch.yaml
  resources-patch.yaml
  pdb.yaml (optional, documented)
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/k8s/base/kustomization.yaml
template/{{cookiecutter.project_slug}}/k8s/base/configmap.yaml
template/{{cookiecutter.project_slug}}/k8s/base/backend-deployment.yaml
template/{{cookiecutter.project_slug}}/k8s/base/frontend-deployment.yaml
template/{{cookiecutter.project_slug}}/k8s/base/ingress.yaml
template/{{cookiecutter.project_slug}}/k8s/overlays/staging/  (pattern reference)
```

## Implementation Details

### 1. Production Kustomization (`k8s/overlays/production/kustomization.yaml`)

```yaml
# {{ cookiecutter.project_name }} Kubernetes Production Overlay
#
# Production environment configuration with high availability settings.
# Inherits from base/ and applies production-specific patches.
#
# IMPORTANT: Review all settings before deploying to production.
#
# Deploy: kubectl apply -k k8s/overlays/production
# Review: kubectl kustomize k8s/overlays/production

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

# Reference the base configuration
resources:
  - ../../base
  # Uncomment to enable Pod Disruption Budget
  # - pdb.yaml

# Production labels
commonLabels:
  app.kubernetes.io/environment: production

# Production annotations
commonAnnotations:
  environment: production
  managed-by: kustomize

# Image customization - use semantic versions in production
images:
  - name: ghcr.io/OWNER/{{ cookiecutter.project_slug }}-backend
    newTag: v1.0.0
  - name: ghcr.io/OWNER/{{ cookiecutter.project_slug }}-frontend
    newTag: v1.0.0

# Patches to apply
patches:
  # ConfigMap values for production
  - path: configmap-patch.yaml

  # Increased replicas for high availability
  - path: replicas-patch.yaml

  # Production resource limits
  - path: resources-patch.yaml

  # Production ingress hosts
  - target:
      kind: Ingress
      name: {{ cookiecutter.project_slug }}-ingress
    patch: |-
      - op: replace
        path: /spec/rules/0/host
        value: app.example.com
      - op: replace
        path: /spec/rules/1/host
        value: api.example.com
      - op: replace
        path: /spec/tls/0/hosts
        value:
          - app.example.com
          - api.example.com
      - op: replace
        path: /spec/tls/0/secretName
        value: {{ cookiecutter.project_slug }}-production-tls
      - op: add
        path: /metadata/annotations/cert-manager.io~1cluster-issuer
        value: letsencrypt-prod

  # Add production-specific security annotations
  - target:
      kind: Deployment
      name: backend
    patch: |-
      - op: add
        path: /metadata/annotations/kubectl.kubernetes.io~1default-container
        value: backend
      - op: add
        path: /spec/template/metadata/annotations
        value:
          prometheus.io/scrape: "true"
          prometheus.io/port: "8000"
          prometheus.io/path: "/metrics"

  # Frontend Prometheus annotations (if metrics exposed)
  - target:
      kind: Deployment
      name: frontend
    patch: |-
      - op: add
        path: /metadata/annotations/kubectl.kubernetes.io~1default-container
        value: frontend
```

### 2. ConfigMap Patch (`k8s/overlays/production/configmap-patch.yaml`)

```yaml
# Production environment configuration overrides
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ cookiecutter.project_slug }}-config
data:
  # Environment identifier
  ENV: "production"

  # Production logging - info level to reduce log volume
  LOG_LEVEL: "info"
  DEBUG: "false"

  # Production OAuth provider
  # Update with your production Keycloak URL
  OAUTH_ISSUER_URL: "https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}"

  # Production frontend API URL
  VITE_API_URL: "https://api.example.com"

  # Production-specific settings
  # Stricter rate limiting in production
  RATE_LIMIT_PER_MINUTE: "60"

  # Cache settings
  CACHE_TTL_SECONDS: "300"
```

### 3. Replicas Patch (`k8s/overlays/production/replicas-patch.yaml`)

```yaml
# Production replicas for high availability
# Minimum 2 replicas for zero-downtime deployments
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  # Production deployment strategy
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### 4. Resources Patch (`k8s/overlays/production/resources-patch.yaml`)

```yaml
# Production resource limits
# These should be tuned based on actual usage metrics
#
# Guidelines:
# - Requests: Average resource usage
# - Limits: Peak resource usage + buffer
# - Monitor and adjust based on metrics
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
              cpu: 200m
              memory: 512Mi
            limits:
              cpu: 1000m
              memory: 1Gi
          # Production-tuned probes
          livenessProbe:
            initialDelaySeconds: 30
            periodSeconds: 30
            timeoutSeconds: 10
            failureThreshold: 3
          readinessProbe:
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
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
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 256Mi
```

### 5. Pod Disruption Budget (Optional) (`k8s/overlays/production/pdb.yaml`)

```yaml
# Pod Disruption Budget - ensures minimum availability during maintenance
#
# Enable by uncommenting in kustomization.yaml:
#   resources:
#     - ../../base
#     - pdb.yaml
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: backend-pdb
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backend
spec:
  # At least 1 pod must be available during disruptions
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ cookiecutter.project_slug }}
      app.kubernetes.io/component: backend
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: frontend-pdb
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: frontend
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ cookiecutter.project_slug }}
      app.kubernetes.io/component: frontend
```

## Success Criteria

### Functional Requirements
- [ ] Production overlay inherits all base resources
- [ ] ConfigMap is patched with production-specific values
- [ ] Replicas are increased for high availability (backend: 3, frontend: 2)
- [ ] Resources are appropriately sized for production workloads
- [ ] Image tags use semantic versions (not `latest`)
- [ ] Ingress hosts are production domains
- [ ] Rolling update strategy ensures zero-downtime deployments

### Verification Steps
1. **Kustomize Build:**
   ```bash
   # Build and review rendered manifests
   kubectl kustomize k8s/overlays/production

   # Verify production values in output
   kubectl kustomize k8s/overlays/production | grep -A5 "ENV:"
   ```

2. **Diff from Staging:**
   ```bash
   # Compare production to staging
   diff <(kubectl kustomize k8s/overlays/staging) <(kubectl kustomize k8s/overlays/production)
   ```

3. **Validate Manifests:**
   ```bash
   # Dry-run apply
   kubectl apply -k k8s/overlays/production --dry-run=client

   # Server-side validation
   kubectl apply -k k8s/overlays/production --dry-run=server
   ```

4. **Verify Replicas:**
   ```bash
   # Check replicas are increased
   kubectl kustomize k8s/overlays/production | grep "replicas:"
   # Expected: replicas: 3 (backend), replicas: 2 (frontend)
   ```

5. **Verify Resources:**
   ```bash
   # Check production resource limits
   kubectl kustomize k8s/overlays/production | grep -A10 "resources:"
   ```

6. **Verify Rolling Update:**
   ```bash
   # Check deployment strategy
   kubectl kustomize k8s/overlays/production | grep -A5 "strategy:"
   ```

### Quality Gates
- [ ] `kubectl kustomize` succeeds without errors
- [ ] All base resources are included
- [ ] Production-specific values are correctly applied
- [ ] No hardcoded secrets in overlay files
- [ ] Labels include environment: production
- [ ] Image tags are semantic versions, not `latest`
- [ ] Rolling update maxUnavailable: 0 for zero-downtime

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-01 | Base manifest structure | Overlay patches base resources |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-04 | Overlay path `k8s/overlays/production` | Deploy workflow applies this overlay |

### Integration Contract
```yaml
# Contract: Production overlay structure

# Directory
k8s/overlays/production/
  kustomization.yaml    # References ../../base
  configmap-patch.yaml
  replicas-patch.yaml
  resources-patch.yaml
  pdb.yaml              # Optional PDB

# Kustomize command
kubectl apply -k k8s/overlays/production

# Labels added
app.kubernetes.io/environment: production

# Image tags (semantic versioning)
backend: v1.0.0
frontend: v1.0.0

# Replicas (high availability)
backend: 3
frontend: 2

# Resource limits (production-sized)
backend:  1000m CPU, 1Gi memory
frontend: 500m CPU, 256Mi memory

# Deployment strategy
maxSurge: 1
maxUnavailable: 0
```

## Monitoring and Observability

### Production Metrics
Prometheus annotations are added for automatic scraping:
```yaml
prometheus.io/scrape: "true"
prometheus.io/port: "8000"
prometheus.io/path: "/metrics"
```

### Alerting Thresholds
Production should have alerts configured for:
- High error rate (>1% 5xx for 5 minutes)
- High latency (p95 > 2s for 5 minutes)
- Pod restarts
- Resource exhaustion (CPU/memory > 80%)

### SLA Monitoring
With 3 backend replicas and rolling updates:
- Expected uptime: 99.9%
- Zero-downtime deployments
- Automatic recovery from single pod failures

## Infrastructure Needs

### Production Cluster Requirements
- Kubernetes cluster with multi-node setup
- Minimum 3 nodes for pod anti-affinity to be effective
- Production-grade node types (e.g., n2-standard-4 on GKE)
- Cluster autoscaler enabled (recommended)

### DNS Configuration
- `app.example.com` -> Production Ingress
- `api.example.com` -> Production Ingress

### TLS Certificates
- Production TLS secret: `{{ cookiecutter.project_slug }}-production-tls`
- Use cert-manager with `letsencrypt-prod` issuer
- Certificate renewal automation required

### Resource Estimates (Production)
| Component | CPU Request | Memory Request | CPU Limit | Memory Limit | Replicas | Total CPU | Total Memory |
|-----------|-------------|----------------|-----------|--------------|----------|-----------|--------------|
| Backend   | 200m        | 512Mi          | 1000m     | 1Gi          | 3        | 600m      | 1.5Gi        |
| Frontend  | 100m        | 128Mi          | 500m      | 256Mi        | 2        | 200m      | 256Mi        |
| **Total** | -           | -              | -         | -            | 5        | **800m**  | **1.75Gi**   |

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Similar structure to staging overlay (P4-02)
- Mostly configuration value adjustments
- PDB is optional enhancement
- Well-established patterns

## Notes

### Design Decisions

**1. Three Backend Replicas:**
- Allows one pod failure + one pod updating
- Maintains quorum for availability
- Cost-effective for medium traffic

**2. Two Frontend Replicas:**
- Static assets are cacheable
- CDN typically handles most traffic
- Lower resource requirements

**3. Semantic Version Tags:**
Production uses explicit version tags (not `latest`) because:
- Reproducible deployments
- Easy rollback to specific version
- Clear audit trail

**4. Zero-Downtime Rolling Updates:**
- `maxUnavailable: 0` ensures always at capacity
- `maxSurge: 1` allows one extra pod during update
- Readiness probes prevent traffic to unready pods

**5. Pod Disruption Budget (Optional):**
- Protects against accidental disruption
- Ensures minimum availability during node maintenance
- Enable when cluster has node auto-upgrade

### Staging vs Production Differences
| Aspect | Staging | Production |
|--------|---------|------------|
| Replicas (backend) | 1 | 3 |
| Replicas (frontend) | 1 | 2 |
| Log Level | debug | info |
| CPU Request (backend) | 50m | 200m |
| Memory Request (backend) | 128Mi | 512Mi |
| Image Tags | staging | v1.0.0 |
| Domains | *-staging.* | Production |
| TLS Issuer | staging | letsencrypt-prod |
| PDB | No | Optional |

### Security Considerations
- Production secrets must be managed via external secrets operator or Vault
- Use separate service accounts with minimal permissions
- Enable Network Policies (future enhancement)
- Regular security scanning of deployed images
- Audit logging enabled on cluster

### Scaling Considerations
For future HPA implementation:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Related Requirements
- US-4.2: Environment Configuration Management
- FR-DEP-008: Deployment manifests shall define resource requests and limits
- FR-DEP-009: Deployment manifests shall configure liveness and readiness probes
