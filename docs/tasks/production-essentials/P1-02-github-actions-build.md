# P1-02: Create GitHub Actions Build Workflow

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P1-02 |
| **Task Title** | Create GitHub Actions Build Workflow |
| **Domain** | DevOps |
| **Complexity** | M (Medium) |
| **Estimated Effort** | 2 days |
| **Priority** | Must Have |
| **Dependencies** | P1-01 (CI workflow must exist) |
| **FRD Requirements** | FR-CI-007, FR-CI-008, FR-CI-009, FR-CI-010, FR-CI-011 |

---

## Scope

### What This Task Includes

1. Create `.github/workflows/build.yml` workflow file
2. Configure Docker build for backend and frontend services
3. Configure multi-platform builds (linux/amd64, linux/arm64)
4. Configure image tagging (git SHA, version tag, latest)
5. Configure push to GitHub Container Registry (ghcr.io)
6. Set up Docker layer caching for faster builds
7. Generate SBOM using Trivy/Syft (basic setup)

### What This Task Excludes

- Production Dockerfile enhancements (P1-03)
- Trivy vulnerability scanning (P2-03) - separate security workflow
- Deployment to Kubernetes (P4-04)
- Sentry release tracking (P3-03)

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
{% raw %}{% if cookiecutter.include_github_actions == "yes" %}{% endraw %}
.github/
  workflows/
    build.yml                 # Container build workflow
{% raw %}{% endif %}{% endraw %}
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/Dockerfile` | Backend multi-stage build |
| `template/{{cookiecutter.project_slug}}/frontend/Dockerfile` | Frontend multi-stage build |
| `template/{{cookiecutter.project_slug}}/.github/workflows/ci.yml` | CI workflow (P1-01) |

---

## Technical Specification

### Workflow Structure

```yaml
name: Build

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:  # Allow manual triggers

concurrency:
  group: {% raw %}${{ github.workflow }}-${{ github.ref }}{% endraw %}
  cancel-in-progress: true

env:
  REGISTRY: ghcr.io
  BACKEND_IMAGE: {% raw %}${{ github.repository }}{% endraw %}/backend
  FRONTEND_IMAGE: {% raw %}${{ github.repository }}{% endraw %}/frontend

jobs:
  build-backend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: {% raw %}${{ env.REGISTRY }}{% endraw %}
          username: {% raw %}${{ github.actor }}{% endraw %}
          password: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: {% raw %}${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}{% endraw %}
          tags: |
            type=ref,event=branch
            type=sha,prefix=
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: backend
          file: backend/Dockerfile
          target: production
          platforms: linux/amd64,linux/arm64
          push: true
          tags: {% raw %}${{ steps.meta.outputs.tags }}{% endraw %}
          labels: {% raw %}${{ steps.meta.outputs.labels }}{% endraw %}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: {% raw %}${{ env.REGISTRY }}/${{ env.BACKEND_IMAGE }}:${{ github.sha }}{% endraw %}
          artifact-name: sbom-backend.spdx.json

  build-frontend:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up QEMU
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: {% raw %}${{ env.REGISTRY }}{% endraw %}
          username: {% raw %}${{ github.actor }}{% endraw %}
          password: {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: {% raw %}${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}{% endraw %}
          tags: |
            type=ref,event=branch
            type=sha,prefix=
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: frontend
          file: frontend/Dockerfile
          target: production
          platforms: linux/amd64,linux/arm64
          push: true
          tags: {% raw %}${{ steps.meta.outputs.tags }}{% endraw %}
          labels: {% raw %}${{ steps.meta.outputs.labels }}{% endraw %}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Generate SBOM
        uses: anchore/sbom-action@v0
        with:
          image: {% raw %}${{ env.REGISTRY }}/${{ env.FRONTEND_IMAGE }}:${{ github.sha }}{% endraw %}
          artifact-name: sbom-frontend.spdx.json
```

### Image Tagging Strategy

| Trigger | Tags Generated |
|---------|----------------|
| Push to `main` | `main`, `<sha>`, `latest` |
| Tag `v1.2.3` | `1.2.3`, `1.2`, `<sha>` |
| Tag `v1.2.3-beta.1` | `1.2.3-beta.1`, `<sha>` |

The `docker/metadata-action` handles tag generation automatically based on:
- `type=ref,event=branch` - Branch name for branch pushes
- `type=sha,prefix=` - Short SHA (e.g., `abc1234`)
- `type=semver,pattern={{version}}` - Full semver for tags
- `type=semver,pattern={{major}}.{{minor}}` - Major.minor for semver tags
- `type=raw,value=latest` - `latest` for default branch only

### Multi-Platform Build Configuration

```yaml
platforms: linux/amd64,linux/arm64
```

This builds images for:
- **linux/amd64**: Standard x86_64 servers, most cloud VMs
- **linux/arm64**: ARM-based servers (AWS Graviton, Apple Silicon, Raspberry Pi)

**Performance Note:** ARM64 builds are emulated via QEMU and take 2-3x longer. Consider using a matrix strategy with native ARM runners if available.

### Docker Layer Caching

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

GitHub Actions cache (`type=gha`) stores layer cache in GitHub's cache storage:
- 10 GB limit per repository
- Automatically managed by GitHub
- Shared across workflow runs

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P1-01 | Prerequisite | Uses same cookiecutter conditional pattern |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P1-03 | Enhancement | Uses production Dockerfile targets |
| P2-03 | Extension | Trivy scanning uses built images |
| P4-04 | Sequential | Deploy workflow deploys built images |

---

## Success Criteria

### Functional Requirements

- [ ] Build workflow triggers on push to main branch
- [ ] Build workflow triggers on version tags (v*)
- [ ] Build workflow supports manual trigger (workflow_dispatch)
- [ ] Backend image builds with production target
- [ ] Frontend image builds with production target
- [ ] Images tagged with git SHA
- [ ] Images tagged with semver when pushing version tags
- [ ] Images tagged with `latest` on main branch
- [ ] Images pushed to ghcr.io
- [ ] Multi-platform images available (amd64, arm64)
- [ ] SBOM artifacts generated and uploaded

### Non-Functional Requirements

- [ ] Build completes in under 10 minutes for single platform
- [ ] Docker layer caching reduces rebuild time by 50%+
- [ ] Workflow uses minimal permissions (contents: read, packages: write)
- [ ] Images use production Dockerfile targets (non-root user)

### Validation Steps

1. Push to main branch
   - Verify workflow triggers
   - Verify both images pushed to ghcr.io
   - Verify tags: `main`, `<sha>`, `latest`
   - Verify multi-platform manifests exist
2. Push version tag `v1.0.0`
   - Verify tags: `1.0.0`, `1.0`, `<sha>`
3. Pull and run images locally
   - `docker pull ghcr.io/<repo>/backend:latest`
   - `docker run --rm ghcr.io/<repo>/backend:latest`
   - Verify container starts as non-root user

---

## Integration Points

### GitHub Container Registry

**Registry URL:** `ghcr.io`

**Image Names:**
- Backend: `ghcr.io/<owner>/<repo>/backend`
- Frontend: `ghcr.io/<owner>/<repo>/frontend`

**Authentication:**
- Uses `GITHUB_TOKEN` (automatically provided)
- Requires `packages: write` permission

### Dockerfile Targets

Both Dockerfiles must have a `production` target:

```dockerfile
# Backend: production target exists (line 51)
FROM dependencies AS production

# Frontend: production target should exist
FROM nginx:alpine AS production
```

### SBOM Format

SBOM is generated in SPDX format using `anchore/sbom-action`:
- Artifact name: `sbom-backend.spdx.json`, `sbom-frontend.spdx.json`
- Contains package inventory for vulnerability scanning

---

## Monitoring and Observability

### Build Metrics

Track via GitHub Actions UI:
- Build duration per job
- Cache hit/miss ratio
- Multi-platform build time breakdown

### Recommended Monitoring

1. Set up GitHub Actions workflow status badge in README
2. Configure GitHub repository webhook for build notifications
3. Monitor ghcr.io storage usage (free tier limits apply)

---

## Infrastructure Needs

### GitHub Actions Requirements

- Repository must be on GitHub
- Actions must be enabled
- Packages (ghcr.io) must be enabled

### Secrets Required

| Secret | Source | Purpose |
|--------|--------|---------|
| `GITHUB_TOKEN` | Automatic | Registry authentication |

No additional secrets required - `GITHUB_TOKEN` is automatically provided.

### Resource Limits

- GitHub-hosted runners: 7 GB RAM, 2 CPU
- Multi-platform builds require QEMU emulation
- ARM64 builds may timeout on complex builds (consider native runners)

---

## Implementation Notes

### Parallel Builds

Backend and frontend builds run in parallel:

```yaml
jobs:
  build-backend:
    # ...
  build-frontend:
    # No 'needs' - runs in parallel
```

This reduces total build time compared to sequential builds.

### Build Context

Each build uses only its service directory as context:

```yaml
context: backend
file: backend/Dockerfile
```

This prevents unnecessary cache invalidation when only one service changes.

### Metadata Labels

The `docker/metadata-action` adds OCI labels:
- `org.opencontainers.image.source` - Repository URL
- `org.opencontainers.image.revision` - Git SHA
- `org.opencontainers.image.created` - Build timestamp

These labels enable traceability from running container to source code.

### ARM64 Build Performance

If ARM64 builds are too slow:

1. **Option A:** Use matrix with native runners (requires self-hosted or ARM runners)
2. **Option B:** Build ARM64 only on tags/releases
3. **Option C:** Disable ARM64 initially, add later

```yaml
# Option B: ARM64 only on tags
platforms: {% raw %}${{ github.event_name == 'push' && startsWith(github.ref, 'refs/tags/') && 'linux/amd64,linux/arm64' || 'linux/amd64' }}{% endraw %}
```

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-CI-007 | Docker images built on merge to main | `on.push.branches: [main]` |
| FR-CI-008 | Images tagged with git SHA, version, latest | `docker/metadata-action` |
| FR-CI-009 | Images pushed to ghcr.io | `docker/login-action` + `build-push-action` |
| FR-CI-010 | Multi-platform builds (amd64, arm64) | `platforms: linux/amd64,linux/arm64` |
| FR-CI-011 | SBOM generated for images | `anchore/sbom-action` |

### Related ADRs

- ADR-017: Optional Observability Stack (pattern reference)
- ADR-019: GitHub Actions CI/CD (to be written in P1-06)

### External Resources

- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [Docker Metadata Action](https://github.com/docker/metadata-action)
- [GitHub Container Registry Docs](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Anchore SBOM Action](https://github.com/anchore/sbom-action)
