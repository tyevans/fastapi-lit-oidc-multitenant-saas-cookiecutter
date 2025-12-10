# P4-04: Create GitHub Actions Deploy Workflow

## Task Identifier
**ID:** P4-04
**Phase:** 4 - Kubernetes Deployment
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P1-02 | Required | Documented | Build workflow must exist to produce container images |
| P4-01 | Required | Documented | Kubernetes base manifests must exist for deployment |
| P4-02 | Optional | Documented | Staging overlay for staging deployments |
| P4-03 | Optional | Documented | Production overlay for production deployments |

## Scope

### In Scope
- Create `.github/workflows/deploy.yml` workflow file
- Configure staging deployment on merge to main branch
- Configure production deployment on version tag or manual approval
- Implement kubectl/kustomize-based deployment to Kubernetes
- Set up GitHub Environments with protection rules
- Configure deployment status reporting to GitHub
- Add rollback documentation and quick rollback workflow
- Wrap workflow in `include_github_actions` cookiecutter conditional

### Out of Scope
- Helm chart deployments (using Kustomize per P4-01)
- Multi-cluster deployments (single cluster per environment)
- ArgoCD or Flux GitOps integration (future enhancement)
- Blue/green or canary deployment strategies (future enhancement)
- Kubernetes cluster provisioning (assumes cluster exists)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    deploy.yml                 # Deployment workflow
{% raw %}{% endif %}{% endraw %}
```

### Reference Files
| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/.github/workflows/build.yml` | Container build workflow (P1-02) |
| `template/{{cookiecutter.project_slug}}/k8s/base/kustomization.yaml` | Kustomize base configuration |
| `template/{{cookiecutter.project_slug}}/k8s/overlays/staging/kustomization.yaml` | Staging overlay |
| `template/{{cookiecutter.project_slug}}/k8s/overlays/production/kustomization.yaml` | Production overlay |

## Implementation Details

### 1. Workflow Structure

```yaml
name: Deploy

on:
  # Automatic staging deployment after successful build
  workflow_run:
    workflows: ["Build"]
    types:
      - completed
    branches: [main]

  # Manual deployment trigger
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        type: choice
        options:
          - staging
          - production
        default: staging
      image_tag:
        description: 'Image tag to deploy (default: latest)'
        required: false
        default: 'latest'

  # Production deployment on version tags
  push:
    tags:
      - 'v*'

concurrency:
  group: deploy-{% raw %}${{ github.event.inputs.environment || (github.ref_type == 'tag' && 'production' || 'staging') }}{% endraw %}
  cancel-in-progress: false  # Don't cancel in-progress deployments

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE: {% raw %}${{ github.repository }}{% endraw %}/backend
  FRONTEND_IMAGE: {% raw %}${{ github.repository }}{% endraw %}/frontend

jobs:
  # Determine deployment parameters
  prepare:
    runs-on: ubuntu-latest
    outputs:
      environment: {% raw %}${{ steps.config.outputs.environment }}{% endraw %}
      image_tag: {% raw %}${{ steps.config.outputs.image_tag }}{% endraw %}
      should_deploy: {% raw %}${{ steps.config.outputs.should_deploy }}{% endraw %}
    steps:
      - name: Determine deployment configuration
        id: config
        run: |
          # Determine environment and image tag based on trigger
          if [[ "${{ github.event_name }}" == "workflow_dispatch" ]]; then
            echo "environment=${{ github.event.inputs.environment }}" >> $GITHUB_OUTPUT
            echo "image_tag=${{ github.event.inputs.image_tag }}" >> $GITHUB_OUTPUT
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref_type }}" == "tag" ]]; then
            echo "environment=production" >> $GITHUB_OUTPUT
            # Extract version from tag (v1.2.3 -> 1.2.3)
            echo "image_tag=${GITHUB_REF_NAME#v}" >> $GITHUB_OUTPUT
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          elif [[ "${{ github.event.workflow_run.conclusion }}" == "success" ]]; then
            echo "environment=staging" >> $GITHUB_OUTPUT
            echo "image_tag=latest" >> $GITHUB_OUTPUT
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          else
            echo "should_deploy=false" >> $GITHUB_OUTPUT
          fi

  # Deploy to staging environment
  deploy-staging:
    needs: prepare
    if: needs.prepare.outputs.should_deploy == 'true' && needs.prepare.outputs.environment == 'staging'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    permissions:
      contents: read
      id-token: write  # For OIDC authentication to cloud providers
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v4
        with:
          version: 'v1.29.0'

      - name: Configure Kubernetes credentials
        # Option 1: Kubeconfig from secret
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > ~/.kube/config
          chmod 600 ~/.kube/config
        # Option 2: Cloud provider OIDC (uncomment for AWS EKS, GKE, or AKS)
        # - uses: aws-actions/configure-aws-credentials@v4
        #   with:
        #     role-to-assume: arn:aws:iam::123456789:role/github-actions
        #     aws-region: us-east-1
        # - run: aws eks update-kubeconfig --name my-cluster --region us-east-1

      - name: Update image tags
        run: |
          cd k8s/overlays/staging
          kustomize edit set image \
            ghcr.io/OWNER/{{ cookiecutter.project_slug }}-backend:${{ needs.prepare.outputs.image_tag }} \
            ghcr.io/OWNER/{{ cookiecutter.project_slug }}-frontend:${{ needs.prepare.outputs.image_tag }}

      - name: Deploy to staging
        run: |
          kubectl apply -k k8s/overlays/staging
          kubectl rollout status deployment/backend -n {{ cookiecutter.project_slug }} --timeout=5m
          kubectl rollout status deployment/frontend -n {{ cookiecutter.project_slug }} --timeout=5m

      - name: Verify deployment
        run: |
          # Wait for pods to be ready
          kubectl wait --for=condition=ready pod -l app.kubernetes.io/name={{ cookiecutter.project_slug }} -n {{ cookiecutter.project_slug }} --timeout=120s

          # Check health endpoints
          BACKEND_POD=$(kubectl get pod -n {{ cookiecutter.project_slug }} -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
          kubectl exec -n {{ cookiecutter.project_slug }} $BACKEND_POD -- curl -f http://localhost:8000{{ cookiecutter.backend_api_prefix }}/health

      - name: Report deployment status
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const status = '${{ job.status }}' === 'success' ? 'success' : 'failure';
            await github.rest.repos.createDeploymentStatus({
              owner: context.repo.owner,
              repo: context.repo.repo,
              deployment_id: context.payload.deployment?.id || 0,
              state: status,
              environment: 'staging',
              description: `Deployed ${context.sha.substring(0, 7)} to staging`
            });

  # Deploy to production environment
  deploy-production:
    needs: prepare
    if: needs.prepare.outputs.should_deploy == 'true' && needs.prepare.outputs.environment == 'production'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.example.com
    permissions:
      contents: read
      id-token: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up kubectl
        uses: azure/setup-kubectl@v4
        with:
          version: 'v1.29.0'

      - name: Configure Kubernetes credentials
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG_PRODUCTION }}" | base64 -d > ~/.kube/config
          chmod 600 ~/.kube/config

      - name: Update image tags
        run: |
          cd k8s/overlays/production
          kustomize edit set image \
            ghcr.io/OWNER/{{ cookiecutter.project_slug }}-backend:${{ needs.prepare.outputs.image_tag }} \
            ghcr.io/OWNER/{{ cookiecutter.project_slug }}-frontend:${{ needs.prepare.outputs.image_tag }}

      - name: Deploy to production
        run: |
          kubectl apply -k k8s/overlays/production
          kubectl rollout status deployment/backend -n {{ cookiecutter.project_slug }} --timeout=5m
          kubectl rollout status deployment/frontend -n {{ cookiecutter.project_slug }} --timeout=5m

      - name: Verify deployment
        run: |
          kubectl wait --for=condition=ready pod -l app.kubernetes.io/name={{ cookiecutter.project_slug }} -n {{ cookiecutter.project_slug }} --timeout=120s

          BACKEND_POD=$(kubectl get pod -n {{ cookiecutter.project_slug }} -l app.kubernetes.io/component=backend -o jsonpath='{.items[0].metadata.name}')
          kubectl exec -n {{ cookiecutter.project_slug }} $BACKEND_POD -- curl -f http://localhost:8000{{ cookiecutter.backend_api_prefix }}/health

      - name: Create GitHub Release
        if: github.ref_type == 'tag'
        uses: actions/github-script@v7
        with:
          script: |
            const tag = context.ref.replace('refs/tags/', '');
            await github.rest.repos.createRelease({
              owner: context.repo.owner,
              repo: context.repo.repo,
              tag_name: tag,
              name: `Release ${tag}`,
              generate_release_notes: true
            });

  # Rollback job (manual trigger only)
  rollback:
    if: github.event_name == 'workflow_dispatch' && github.event.inputs.environment != ''
    runs-on: ubuntu-latest
    environment:
      name: {% raw %}${{ github.event.inputs.environment }}{% endraw %}
    steps:
      - name: Rollback deployment
        run: |
          echo "To rollback, run:"
          echo "  kubectl rollout undo deployment/backend -n {{ cookiecutter.project_slug }}"
          echo "  kubectl rollout undo deployment/frontend -n {{ cookiecutter.project_slug }}"
          echo ""
          echo "Or deploy a specific version using workflow_dispatch with image_tag parameter"
```

### 2. GitHub Environments Configuration

The workflow uses GitHub Environments for deployment protection:

**Staging Environment:**
- No required reviewers (auto-deploy on merge to main)
- Deployment branches: `main` only
- Secrets: `KUBECONFIG_STAGING`

**Production Environment:**
- Required reviewers: 1-6 team members
- Wait timer: optional (e.g., 5 minutes for review)
- Deployment branches: `main` and version tags
- Secrets: `KUBECONFIG_PRODUCTION`

### 3. Secrets Required

| Secret | Environment | Description |
|--------|-------------|-------------|
| `KUBECONFIG_STAGING` | staging | Base64-encoded kubeconfig for staging cluster |
| `KUBECONFIG_PRODUCTION` | production | Base64-encoded kubeconfig for production cluster |

**Creating kubeconfig secret:**
```bash
# Get kubeconfig from cluster
kubectl config view --minify --flatten > kubeconfig.yaml

# Base64 encode
base64 -w 0 kubeconfig.yaml > kubeconfig.b64

# Add to GitHub Secrets (Settings > Secrets > Actions)
```

### 4. Rollback Procedures

**Quick Rollback (previous version):**
```bash
kubectl rollout undo deployment/backend -n {{ cookiecutter.project_slug }}
kubectl rollout undo deployment/frontend -n {{ cookiecutter.project_slug }}
```

**Rollback to specific revision:**
```bash
# List revision history
kubectl rollout history deployment/backend -n {{ cookiecutter.project_slug }}

# Rollback to specific revision
kubectl rollout undo deployment/backend -n {{ cookiecutter.project_slug }} --to-revision=2
```

**Rollback via workflow:**
1. Go to Actions > Deploy workflow
2. Click "Run workflow"
3. Select environment (staging/production)
4. Enter specific image_tag (e.g., `1.0.0` for previous version)
5. Click "Run workflow"

## Success Criteria

### Functional Requirements
- [ ] Deploy workflow triggers on successful build workflow (staging)
- [ ] Deploy workflow triggers on version tags (production)
- [ ] Deploy workflow supports manual trigger with environment selection
- [ ] Staging deployment completes without manual approval
- [ ] Production deployment requires environment approval
- [ ] Image tags are correctly updated in Kustomize overlays
- [ ] Deployment status is reported to GitHub
- [ ] Health checks verify successful deployment
- [ ] Rollback procedure is documented and tested

### Non-Functional Requirements
- [ ] Deployment completes in under 5 minutes
- [ ] Failed deployments do not leave cluster in inconsistent state
- [ ] Concurrent deployments to same environment are prevented
- [ ] Secrets are not exposed in logs

### Verification Steps

1. **Staging Deployment Test:**
   ```bash
   # Merge PR to main
   # Verify build workflow completes
   # Verify deploy workflow triggers automatically
   # Verify pods are running with correct image tag
   kubectl get pods -n {{ cookiecutter.project_slug }} -o jsonpath='{.items[*].spec.containers[*].image}'
   ```

2. **Production Deployment Test:**
   ```bash
   # Create and push version tag
   git tag v1.0.0
   git push origin v1.0.0

   # Approve deployment in GitHub UI
   # Verify production pods are running
   ```

3. **Manual Rollback Test:**
   ```bash
   # Run workflow_dispatch with previous version
   # Verify rollback completes successfully
   ```

### Quality Gates
- [ ] Workflow syntax validated (`actionlint`)
- [ ] All secrets documented
- [ ] Environment protection rules configured
- [ ] Rollback procedure tested
- [ ] Deployment status visible in GitHub UI

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P1-02 | Build workflow completion event | Deploy triggers on `workflow_run.completed` |
| P4-01 | Kustomize base manifests | Deployment applies overlays to base |
| P4-02 | Staging overlay | Staging deployment uses `k8s/overlays/staging` |
| P4-03 | Production overlay | Production deployment uses `k8s/overlays/production` |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-06 | Workflow conditional | Deploy workflow wrapped in `include_github_actions` |
| P6-04 | E2E validation | E2E tests verify deployment workflow |

### Integration Contract
```yaml
# Contract: Deployment workflow

# Triggers
- workflow_run: Build workflow completion (staging)
- push.tags: v* (production)
- workflow_dispatch: Manual trigger

# Environments
- staging:
    url: https://staging.example.com
    secrets: [KUBECONFIG_STAGING]
    protection: none
- production:
    url: https://app.example.com
    secrets: [KUBECONFIG_PRODUCTION]
    protection: required_reviewers

# Outputs
- Kubernetes deployment applied via kustomize
- Deployment status reported to GitHub
- GitHub Release created on version tags
```

## Monitoring and Observability

### Deployment Metrics
- Track deployment frequency in GitHub Actions
- Monitor deployment duration
- Alert on deployment failures

### Kubernetes Monitoring
After deployment, verify via Prometheus/Grafana:
```promql
# Pod restart count (should be 0 after healthy deployment)
increase(kube_pod_container_status_restarts_total{namespace="{{ cookiecutter.project_slug }}"}[1h])

# Deployment replica availability
kube_deployment_status_replicas_available{namespace="{{ cookiecutter.project_slug }}"}
```

### Alerting
Consider creating alerts for:
- Deployment failures (GitHub webhook to Slack/PagerDuty)
- Pod restarts after deployment
- Health check failures post-deployment

## Infrastructure Needs

### GitHub Configuration
- Repository Settings > Environments > Create "staging" and "production"
- Environment protection rules (reviewers, wait timer)
- Environment secrets (kubeconfig)

### Kubernetes Requirements
- Kubernetes 1.25+ cluster per environment
- RBAC permissions for deployment service account
- Ingress controller configured
- TLS certificates provisioned

### Cloud Provider Authentication (Optional)
For cloud-managed Kubernetes (EKS, GKE, AKS), consider OIDC authentication:

**AWS EKS:**
```yaml
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
    aws-region: us-east-1
- run: aws eks update-kubeconfig --name cluster-name
```

**Google GKE:**
```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY }}
    service_account: ${{ secrets.GCP_SERVICE_ACCOUNT }}
- uses: google-github-actions/get-gke-credentials@v2
  with:
    cluster_name: cluster-name
    location: us-central1
```

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Workflow structure is straightforward but requires careful configuration
- Environment protection rules need repository settings
- Kubeconfig secret management requires documentation
- Testing requires actual Kubernetes clusters or mocking
- Rollback procedures need documentation and testing

## Notes

### Design Decisions

**1. workflow_run vs. workflow_call:**
- Using `workflow_run` allows deploy to trigger after build completion
- Alternative: `workflow_call` for reusable workflow (more complex)

**2. Kustomize Edit vs. Patch Files:**
- Using `kustomize edit set image` for dynamic image updates
- Alternative: Template patch files (more complex, less flexible)

**3. Environment Protection:**
- Production requires manual approval via GitHub Environments
- Staging auto-deploys for fast iteration
- Can add wait timer for production if needed

**4. Kubeconfig vs. Cloud OIDC:**
- Template uses kubeconfig secret for simplicity
- Cloud OIDC is more secure (no long-lived credentials)
- Document both approaches for user choice

### Security Considerations

**Kubeconfig Protection:**
- Store as encrypted GitHub secret
- Use minimal RBAC permissions
- Rotate credentials regularly
- Consider cloud provider OIDC for production

**Least Privilege:**
```yaml
# Example Kubernetes RBAC for deployment
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: github-actions-deploy
  namespace: {{ cookiecutter.project_slug }}
rules:
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "patch", "update"]
  - apiGroups: [""]
    resources: ["pods", "pods/exec"]
    verbs: ["get", "list"]
```

### Future Enhancements
- Blue/green deployment strategy
- Canary deployments with traffic splitting
- ArgoCD GitOps integration
- Slack/Teams deployment notifications
- Automatic rollback on health check failure
- Multi-cluster deployments

### Related Requirements
- FR-CI-012: Staging environment shall deploy automatically on merge to main
- FR-CI-013: Production deployment shall require manual approval or semantic version tag
- FR-CI-014: Deployment workflow shall apply Kubernetes manifests via kubectl or kustomize
- FR-CI-015: Deployment status shall be reported back to GitHub as deployment status
- US-1.3: Deployment Automation
