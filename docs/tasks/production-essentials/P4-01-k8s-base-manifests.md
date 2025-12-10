# P4-01: Create Kubernetes Base Manifests

## Task Identifier
**ID:** P4-01
**Phase:** 4 - Kubernetes Deployment
**Domain:** DevOps
**Complexity:** L (Large)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P1-03 | Required | Documented | Production Dockerfiles must exist for image references |

## Scope

### In Scope
- Create Kustomize base directory structure (`k8s/base/`)
- Create `kustomization.yaml` with all base resources
- Create backend Deployment manifest with health probes, resource limits
- Create backend Service manifest exposing port 8000
- Create frontend Deployment manifest with nginx configuration
- Create frontend Service manifest exposing port 80
- Create ConfigMap for non-sensitive environment variables
- Create Secret template (references only, not values)
- Create Ingress manifest with TLS configuration template
- Add RBAC manifests if needed for service accounts
- Ensure all manifests follow Kubernetes best practices

### Out of Scope
- Staging overlay customization (P4-02)
- Production overlay customization (P4-03)
- GitHub Actions deployment workflow (P4-04)
- Cookiecutter conditional integration (P4-06)
- HPA (Horizontal Pod Autoscaler) - documented as future enhancement
- PDB (Pod Disruption Budget) - documented as future enhancement
- Network Policies - documented as future enhancement

## Relevant Code Areas

### Files to Create
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
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/backend/Dockerfile      (production target reference)
template/{{cookiecutter.project_slug}}/frontend/Dockerfile     (production target reference)
template/{{cookiecutter.project_slug}}/compose.yml             (environment variable reference)
template/{{cookiecutter.project_slug}}/.env.example            (configuration variables)
template/{{cookiecutter.project_slug}}/backend/app/core/config.py  (backend settings)
```

## Implementation Details

### 1. Directory Structure

```
k8s/
  base/
    kustomization.yaml       # Kustomize configuration
    namespace.yaml           # Namespace definition
    backend-deployment.yaml  # Backend pods specification
    backend-service.yaml     # Backend service
    frontend-deployment.yaml # Frontend pods specification
    frontend-service.yaml    # Frontend service
    configmap.yaml          # Non-sensitive configuration
    secret.yaml             # Secret references (not values)
    ingress.yaml            # Ingress with TLS
  overlays/
    staging/                 # (P4-02)
    production/              # (P4-03)
  README.md                  # Deployment documentation
```

### 2. Kustomization Base (`k8s/base/kustomization.yaml`)

```yaml
# {{ cookiecutter.project_name }} Kubernetes Base Configuration
#
# This base configuration defines the common resources for all environments.
# Use overlays (staging, production) for environment-specific customizations.
#
# Apply with: kubectl apply -k k8s/overlays/staging
# Or directly: kubectl apply -k k8s/base (not recommended for production)

apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

metadata:
  name: {{ cookiecutter.project_slug }}-base

# Namespace for all resources
namespace: {{ cookiecutter.project_slug }}

# Common labels applied to all resources
commonLabels:
  app.kubernetes.io/name: {{ cookiecutter.project_slug }}
  app.kubernetes.io/managed-by: kustomize

# Resources to include
resources:
  - namespace.yaml
  - configmap.yaml
  - secret.yaml
  - backend-deployment.yaml
  - backend-service.yaml
  - frontend-deployment.yaml
  - frontend-service.yaml
  - ingress.yaml

# ConfigMap generator (alternative approach)
# configMapGenerator:
#   - name: {{ cookiecutter.project_slug }}-config
#     envs:
#       - config.env
```

### 3. Namespace (`k8s/base/namespace.yaml`)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: {{ cookiecutter.project_slug }}
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: namespace
```

### 4. Backend Deployment (`k8s/base/backend-deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ cookiecutter.project_slug }}
      app.kubernetes.io/component: backend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ cookiecutter.project_slug }}
        app.kubernetes.io/component: backend
    spec:
      serviceAccountName: default
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: backend
          image: ghcr.io/OWNER/{{ cookiecutter.project_slug }}-backend:latest
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 8000
              protocol: TCP
          env:
            - name: ENV
              valueFrom:
                configMapKeyRef:
                  name: {{ cookiecutter.project_slug }}-config
                  key: ENV
            - name: LOG_LEVEL
              valueFrom:
                configMapKeyRef:
                  name: {{ cookiecutter.project_slug }}-config
                  key: LOG_LEVEL
            - name: API_V1_PREFIX
              valueFrom:
                configMapKeyRef:
                  name: {{ cookiecutter.project_slug }}-config
                  key: API_V1_PREFIX
            - name: OAUTH_ISSUER_URL
              valueFrom:
                configMapKeyRef:
                  name: {{ cookiecutter.project_slug }}-config
                  key: OAUTH_ISSUER_URL
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ cookiecutter.project_slug }}-secrets
                  key: DATABASE_URL
            - name: REDIS_URL
              valueFrom:
                secretKeyRef:
                  name: {{ cookiecutter.project_slug }}-secrets
                  key: REDIS_URL
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: {{ cookiecutter.backend_api_prefix }}/health
              port: http
            initialDelaySeconds: 30
            periodSeconds: 30
            timeoutSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: {{ cookiecutter.backend_api_prefix }}/health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
            - name: cache
              mountPath: /app/.cache
      volumes:
        - name: tmp
          emptyDir: {}
        - name: cache
          emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
                    app.kubernetes.io/component: backend
                topologyKey: kubernetes.io/hostname
```

### 5. Backend Service (`k8s/base/backend-service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backend
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backend
  ports:
    - name: http
      port: 8000
      targetPort: http
      protocol: TCP
```

### 6. Frontend Deployment (`k8s/base/frontend-deployment.yaml`)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ cookiecutter.project_slug }}
      app.kubernetes.io/component: frontend
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {{ cookiecutter.project_slug }}
        app.kubernetes.io/component: frontend
    spec:
      serviceAccountName: default
      securityContext:
        runAsNonRoot: true
        runAsUser: 101  # nginx user
        fsGroup: 101
      containers:
        - name: frontend
          image: ghcr.io/OWNER/{{ cookiecutter.project_slug }}-frontend:latest
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          livenessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 10
            periodSeconds: 30
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            timeoutSeconds: 3
            failureThreshold: 3
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
              add:
                - NET_BIND_SERVICE
          volumeMounts:
            - name: nginx-cache
              mountPath: /var/cache/nginx
            - name: nginx-run
              mountPath: /var/run
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: nginx-cache
          emptyDir: {}
        - name: nginx-run
          emptyDir: {}
        - name: tmp
          emptyDir: {}
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
                    app.kubernetes.io/component: frontend
                topologyKey: kubernetes.io/hostname
```

### 7. Frontend Service (`k8s/base/frontend-service.yaml`)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: frontend
spec:
  type: ClusterIP
  selector:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: frontend
  ports:
    - name: http
      port: 80
      targetPort: http
      protocol: TCP
```

### 8. ConfigMap (`k8s/base/configmap.yaml`)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ cookiecutter.project_slug }}-config
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: config
data:
  # Environment
  ENV: "production"
  LOG_LEVEL: "info"
  DEBUG: "false"

  # API Configuration
  API_V1_PREFIX: "{{ cookiecutter.backend_api_prefix }}"

  # OAuth Configuration
  # Update OAUTH_ISSUER_URL based on your Keycloak deployment
  OAUTH_ISSUER_URL: "https://auth.example.com/realms/{{ cookiecutter.keycloak_realm_name }}"

  # Frontend Configuration
  # VITE_* variables are build-time, not runtime
  # Consider using a config endpoint or environment injection for runtime config
  VITE_API_URL: "https://api.example.com"
  VITE_API_PREFIX: "{{ cookiecutter.backend_api_prefix }}"
```

### 9. Secret Template (`k8s/base/secret.yaml`)

```yaml
# Secret template - DO NOT commit actual secrets to version control
#
# Create secrets manually or use external secret management:
#   kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
#     --from-literal=DATABASE_URL='postgresql+asyncpg://...' \
#     --from-literal=REDIS_URL='redis://...'
#
# Or use sealed-secrets, external-secrets-operator, or Vault
#
apiVersion: v1
kind: Secret
metadata:
  name: {{ cookiecutter.project_slug }}-secrets
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: secrets
type: Opaque
stringData:
  # PLACEHOLDER VALUES - Replace before deployment
  # These are intentionally invalid to prevent accidental use

  # Database connection string
  # Format: postgresql+asyncpg://user:password@host:port/database
  DATABASE_URL: "REPLACE_WITH_ACTUAL_DATABASE_URL"

  # Redis connection string
  # Format: redis://default:password@host:port/0
  REDIS_URL: "REPLACE_WITH_ACTUAL_REDIS_URL"

  # Migration database URL (if different from app user)
  MIGRATION_DATABASE_URL: "REPLACE_WITH_MIGRATION_DATABASE_URL"
```

### 10. Ingress (`k8s/base/ingress.yaml`)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ cookiecutter.project_slug }}-ingress
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: ingress
  annotations:
    # Common annotations - adjust based on your ingress controller
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "60"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "60"
    # Enable CORS if needed
    # nginx.ingress.kubernetes.io/enable-cors: "true"
    # Rate limiting
    # nginx.ingress.kubernetes.io/limit-rps: "100"
    # TLS with cert-manager
    # cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - app.example.com
        - api.example.com
      secretName: {{ cookiecutter.project_slug }}-tls
  rules:
    # Frontend - main application
    - host: app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
    # Backend API
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
```

### 11. README (`k8s/README.md`)

```markdown
# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying {{ cookiecutter.project_name }}.

## Structure

```
k8s/
  base/                 # Base configuration (common to all environments)
  overlays/
    staging/            # Staging environment overrides
    production/         # Production environment overrides
```

## Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Container images pushed to registry
- External services configured:
  - PostgreSQL database
  - Redis instance
  - Keycloak/OAuth provider

## Quick Start

### 1. Create Secrets

```bash
# Create namespace first
kubectl create namespace {{ cookiecutter.project_slug }}

# Create secrets (replace with actual values)
kubectl create secret generic {{ cookiecutter.project_slug }}-secrets \
  --namespace {{ cookiecutter.project_slug }} \
  --from-literal=DATABASE_URL='postgresql+asyncpg://user:pass@host:5432/db' \
  --from-literal=REDIS_URL='redis://default:pass@host:6379/0' \
  --from-literal=MIGRATION_DATABASE_URL='postgresql+asyncpg://migrator:pass@host:5432/db'
```

### 2. Deploy to Staging

```bash
# Review what will be applied
kubectl apply -k k8s/overlays/staging --dry-run=client

# Apply to cluster
kubectl apply -k k8s/overlays/staging
```

### 3. Deploy to Production

```bash
# Apply production overlay
kubectl apply -k k8s/overlays/production
```

## Customization

### Environment-Specific Configuration

Edit the overlay's `kustomization.yaml` to:
- Change replica counts
- Update resource limits
- Modify ConfigMap values
- Add environment-specific annotations

### Image Updates

Update image tags in overlay patches or use:

```bash
kubectl set image deployment/backend backend=ghcr.io/OWNER/{{ cookiecutter.project_slug }}-backend:v1.2.3
```

### Secrets Management

For production, consider:
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets)
- [External Secrets Operator](https://external-secrets.io/)
- [HashiCorp Vault](https://www.vaultproject.io/)

## Verification

```bash
# Check deployment status
kubectl get all -n {{ cookiecutter.project_slug }}

# Check pod logs
kubectl logs -n {{ cookiecutter.project_slug }} -l app.kubernetes.io/component=backend

# Check ingress
kubectl get ingress -n {{ cookiecutter.project_slug }}

# Port forward for local testing
kubectl port-forward -n {{ cookiecutter.project_slug }} svc/backend 8000:8000
```

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod -n {{ cookiecutter.project_slug }} <pod-name>

# Check container logs
kubectl logs -n {{ cookiecutter.project_slug }} <pod-name> -c backend
```

### Ingress not working

```bash
# Verify ingress controller is running
kubectl get pods -n ingress-nginx

# Check ingress status
kubectl describe ingress -n {{ cookiecutter.project_slug }}
```

### Database connection issues

```bash
# Verify secret is mounted
kubectl exec -n {{ cookiecutter.project_slug }} <pod-name> -- env | grep DATABASE

# Test connectivity from pod
kubectl exec -n {{ cookiecutter.project_slug }} <pod-name> -- nc -zv <db-host> 5432
```
```

## Success Criteria

### Functional Requirements
- [ ] FR-DEP-001: Kubernetes Deployment manifest shall be included for backend service
- [ ] FR-DEP-002: Kubernetes Deployment manifest shall be included for frontend service
- [ ] FR-DEP-003: Kubernetes Service manifests shall expose backend on port 8000
- [ ] FR-DEP-004: Kubernetes Service manifests shall expose frontend on port 80
- [ ] FR-DEP-005: Kubernetes Ingress manifest shall include TLS configuration template
- [ ] FR-DEP-006: Kubernetes ConfigMap shall externalize non-sensitive configuration
- [ ] FR-DEP-007: Kubernetes manifests shall reference Secrets for sensitive values
- [ ] FR-DEP-008: Deployment manifests shall define resource requests and limits
- [ ] FR-DEP-009: Deployment manifests shall configure liveness and readiness probes

### Verification Steps
1. **Manifest Validation:**
   ```bash
   # Validate all manifests
   kubectl apply -k k8s/base --dry-run=client

   # Check for deprecated APIs
   kubectl apply -k k8s/base --dry-run=server
   ```

2. **Kustomize Build:**
   ```bash
   # Build and review rendered manifests
   kubectl kustomize k8s/base
   ```

3. **Security Context Verification:**
   ```bash
   # Verify no privileged containers
   kubectl kustomize k8s/base | grep -A5 "securityContext"
   ```

4. **Resource Limits:**
   ```bash
   # Verify resource limits are set
   kubectl kustomize k8s/base | grep -A10 "resources:"
   ```

### Quality Gates
- [ ] All manifests pass `kubectl apply --dry-run=client`
- [ ] No deprecated API versions used
- [ ] Security contexts enforce non-root, read-only root filesystem
- [ ] Resource requests and limits defined for all containers
- [ ] Health probes configured with appropriate timeouts
- [ ] Ingress TLS configured

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P1-03 | Production Dockerfile targets | Images referenced must use production targets |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-02 | Base manifest structure | Staging overlay patches base resources |
| P4-03 | Base manifest structure | Production overlay patches base resources |
| P4-04 | Kustomize directory structure | Deploy workflow applies overlays |
| P4-06 | k8s/ directory structure | Cookiecutter conditional wraps entire k8s/ |
| P4-07 | ConfigMap/Secret variable names | Documentation references configuration |
| P4-08 | Manifest design decisions | ADR documents Kustomize choice |
| P3-07 | Namespace and RBAC | Backup CronJob deploys to same namespace |

### Integration Contract
```yaml
# Contract: Kubernetes base manifests structure

# Directory structure
k8s/
  base/
    kustomization.yaml    # Must include all base resources
    namespace.yaml        # Namespace: {{ cookiecutter.project_slug }}
    backend-deployment.yaml
    backend-service.yaml
    frontend-deployment.yaml
    frontend-service.yaml
    configmap.yaml        # Name: {{ cookiecutter.project_slug }}-config
    secret.yaml           # Name: {{ cookiecutter.project_slug }}-secrets
    ingress.yaml

# Labels (all resources)
app.kubernetes.io/name: {{ cookiecutter.project_slug }}
app.kubernetes.io/component: <component>

# Ports
backend:  8000 (ClusterIP)
frontend: 80 (ClusterIP)

# Health endpoints
backend:  {{ cookiecutter.backend_api_prefix }}/health
frontend: /
```

## Monitoring and Observability

### Prometheus Annotations
Add to deployment pod templates for automatic scraping:
```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Logging
Containers log to stdout/stderr. Use cluster log aggregation (Loki, Elasticsearch) to collect.

### Tracing
If observability is enabled, configure OTEL environment variables in ConfigMap:
```yaml
OTEL_SERVICE_NAME: "backend"
OTEL_EXPORTER_OTLP_ENDPOINT: "http://tempo.observability:4317"
```

## Infrastructure Needs

### Cluster Requirements
- Kubernetes 1.25+
- Ingress controller (nginx-ingress recommended)
- Cert-manager (optional, for automatic TLS)
- Metrics server (for HPA, future enhancement)

### External Services
- PostgreSQL 16+ (managed recommended: RDS, Cloud SQL, Azure Database)
- Redis 7+ (managed recommended: ElastiCache, Memorystore)
- Keycloak or OAuth provider

### Resource Estimates
| Component | CPU Request | Memory Request | CPU Limit | Memory Limit | Replicas |
|-----------|-------------|----------------|-----------|--------------|----------|
| Backend   | 100m        | 256Mi          | 500m      | 512Mi        | 2        |
| Frontend  | 50m         | 64Mi           | 200m      | 128Mi        | 2        |
| **Total** | **300m**    | **640Mi**      | **1400m** | **1280Mi**   | 4        |

## Estimated Effort

**Size:** L (Large)
**Time:** 2-3 days
**Justification:**
- Multiple manifest files with detailed configuration
- Security contexts and best practices implementation
- Resource limits and health probes tuning
- Documentation and README creation
- Testing across different Kubernetes versions

## Notes

### Design Decisions

**1. Kustomize over Helm:**
- Built into kubectl (no additional tooling)
- Simpler for basic deployments
- Easier to understand for Kubernetes beginners
- Can be upgraded to Helm later if needed

**2. ClusterIP Services:**
- Ingress handles external traffic
- Services are internal only
- Reduces attack surface

**3. Security Contexts:**
- runAsNonRoot enforced
- Read-only root filesystem
- Dropped capabilities
- Follows Kubernetes hardening guidelines

**4. Anti-Affinity:**
- Preferred (not required) pod spreading
- Improves availability across nodes
- Doesn't block scheduling on single-node clusters

**5. Resource Limits:**
- Conservative defaults for development clusters
- Should be tuned based on actual usage
- Memory limits prevent OOM kills

### Future Enhancements
- Horizontal Pod Autoscaler (HPA)
- Pod Disruption Budget (PDB)
- Network Policies
- Service Mesh integration (Istio, Linkerd)
- GitOps with Argo CD or Flux

### Security Considerations
- Secrets should not be committed to git
- Use external secret management in production
- Container images should be scanned (Trivy, P2-03)
- Network policies should restrict pod-to-pod traffic
- RBAC should limit service account permissions

### Related Requirements
- FR-DEP-001 through FR-DEP-009: Kubernetes deployment requirements
- US-4.1: Production Kubernetes Manifests
- NFR-005: All additions shall follow existing codebase patterns
