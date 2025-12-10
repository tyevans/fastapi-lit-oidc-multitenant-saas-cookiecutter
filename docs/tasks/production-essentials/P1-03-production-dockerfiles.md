# P1-03: Enhance Production Dockerfiles

## Task Identification

| Field | Value |
|-------|-------|
| **Task ID** | P1-03 |
| **Task Title** | Enhance Production Dockerfiles |
| **Domain** | DevOps |
| **Complexity** | S (Small) |
| **Estimated Effort** | 2 days |
| **Priority** | Must Have |
| **Dependencies** | None |
| **FRD Requirements** | FR-DEP-008, FR-DEP-009, NFR-003, NFR-005 |

---

## Scope

### What This Task Includes

1. Add HEALTHCHECK instructions to backend production Dockerfile
2. Add HEALTHCHECK instructions to frontend production Dockerfile
3. Verify non-root user configuration is correct
4. Add security-focused labels (OCI annotations)
5. Verify resource-efficient base image selection
6. Document Dockerfile patterns in comments

### What This Task Excludes

- CI/CD workflow changes (P1-01, P1-02)
- Kubernetes health probe configuration (P4-01)
- Security scanning (P2-03)

---

## Current State Analysis

### Backend Dockerfile (Existing)

The backend Dockerfile already has strong production foundations:

```dockerfile
# Stage 4: Production image
FROM dependencies AS production

# Create non-root user (GOOD)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code (GOOD)
COPY --chown=appuser:appuser . .

# Switch to non-root user (GOOD)
USER appuser

# Expose port
EXPOSE 8000

# Run with production settings (GOOD - 4 workers)
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Gaps:**
- Missing HEALTHCHECK instruction
- Missing OCI labels

### Frontend Dockerfile (Existing)

The frontend Dockerfile has a minimal production stage:

```dockerfile
# Stage 3: Production
FROM nginx:alpine AS production

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

**Gaps:**
- Missing HEALTHCHECK instruction
- Running as root (nginx default)
- Missing OCI labels

---

## Relevant Code Areas

### Files to Modify

| File | Changes |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/Dockerfile` | Add HEALTHCHECK, OCI labels |
| `template/{{cookiecutter.project_slug}}/frontend/Dockerfile` | Add HEALTHCHECK, non-root user, OCI labels |

### Reference Files

| File | Purpose |
|------|---------|
| `template/{{cookiecutter.project_slug}}/backend/app/api/routers/health.py` | Health endpoint implementation |
| `template/{{cookiecutter.project_slug}}/frontend/nginx.conf` | Nginx configuration |

---

## Technical Specification

### Backend Dockerfile Enhancements

Add after the `EXPOSE 8000` line in the production stage:

```dockerfile
# Stage 4: Production image
FROM dependencies AS production

# OCI Labels for container metadata
LABEL org.opencontainers.image.title="{{ cookiecutter.project_name }} Backend"
LABEL org.opencontainers.image.description="FastAPI backend service"
LABEL org.opencontainers.image.vendor="{{ cookiecutter.author_name }}"
LABEL org.opencontainers.image.licenses="MIT"

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check - verify application responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run with production settings
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**HEALTHCHECK parameters:**
- `--interval=30s`: Check every 30 seconds
- `--timeout=10s`: Fail if check takes longer than 10 seconds
- `--start-period=10s`: Grace period for container startup
- `--retries=3`: Mark unhealthy after 3 consecutive failures

**Note:** The backend Dockerfile needs `curl` for health checks. Add to base stage:

```dockerfile
# Stage 1: Base image with Python {{ cookiecutter.python_version }}
FROM python:{{ cookiecutter.python_version }}-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    postgresql-client \
    curl \                          # Already present - used for health check
    && rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Frontend Dockerfile Enhancements

Complete production stage rewrite:

```dockerfile
# Stage 3: Production
FROM nginx:alpine AS production

# OCI Labels for container metadata
LABEL org.opencontainers.image.title="{{ cookiecutter.project_name }} Frontend"
LABEL org.opencontainers.image.description="Lit web components frontend"
LABEL org.opencontainers.image.vendor="{{ cookiecutter.author_name }}"
LABEL org.opencontainers.image.licenses="MIT"

# Create non-root user and set up nginx directories
RUN addgroup -g 1000 -S appgroup && \
    adduser -u 1000 -S appuser -G appgroup && \
    mkdir -p /var/cache/nginx /var/run/nginx && \
    chown -R appuser:appgroup /var/cache/nginx /var/run/nginx /usr/share/nginx/html && \
    touch /var/run/nginx.pid && \
    chown appuser:appgroup /var/run/nginx.pid

# Copy custom nginx.conf that runs as non-root
COPY --chown=appuser:appgroup nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from build stage
COPY --from=build --chown=appuser:appgroup /app/dist /usr/share/nginx/html

# Switch to non-root user
USER appuser

# Expose port 80 (or 8080 for non-root)
EXPOSE 80

# Health check - verify nginx responds
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

**Non-Root Nginx Considerations:**

Running nginx as non-root on port 80 requires either:

1. **Option A (Recommended):** Use port 8080 instead of 80
2. **Option B:** Use capabilities (`setcap 'cap_net_bind_service=+ep'`)
3. **Option C:** Use `nginx-unprivileged` base image

For simplicity, recommend **Option A** with port 8080:

```dockerfile
# Expose non-privileged port
EXPOSE 8080

# Health check on non-privileged port
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:8080/ || exit 1
```

This requires updating `nginx.conf` to listen on 8080.

### Nginx Configuration Update

If switching to port 8080 for non-root operation, update `nginx.conf`:

```nginx
server {
    listen 8080;  # Changed from 80
    server_name localhost;
    # ... rest of config
}
```

---

## Dependencies

### Upstream Dependencies

None - this is a foundational task.

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P1-02 | Enhancement | Build workflow uses production targets |
| P4-01 | Contract | K8s probes should align with HEALTHCHECK |
| P2-03 | Extension | Trivy scans these Dockerfiles |

---

## Success Criteria

### Functional Requirements

- [ ] Backend production image has HEALTHCHECK instruction
- [ ] Frontend production image has HEALTHCHECK instruction
- [ ] Backend runs as non-root user (appuser:1000)
- [ ] Frontend runs as non-root user (appuser:1000)
- [ ] Health checks use appropriate endpoints (/api/v1/health, /)
- [ ] OCI labels present on built images

### Non-Functional Requirements

- [ ] Health check intervals are reasonable (30s)
- [ ] Start period allows for application warmup
- [ ] No security warnings from Trivy (user namespace)
- [ ] Base images are minimal (slim/alpine variants)

### Validation Steps

1. Build backend production image:
   ```bash
   docker build --target production -t backend-test ./backend
   ```

2. Verify backend runs as non-root:
   ```bash
   docker run --rm backend-test id
   # Expected: uid=1000(appuser) gid=1000(appuser)
   ```

3. Verify backend health check:
   ```bash
   docker inspect backend-test --format='{{.Config.Healthcheck}}'
   # Should show HEALTHCHECK configuration
   ```

4. Build frontend production image:
   ```bash
   docker build --target production -t frontend-test ./frontend
   ```

5. Verify frontend runs as non-root:
   ```bash
   docker run --rm frontend-test id
   # Expected: uid=1000(appuser) gid=1000(appgroup)
   ```

6. Run Trivy scan for user namespace issues:
   ```bash
   trivy image --severity HIGH,CRITICAL backend-test
   trivy image --severity HIGH,CRITICAL frontend-test
   ```

---

## Integration Points

### Health Endpoints

| Service | Health Endpoint | Expected Response |
|---------|-----------------|-------------------|
| Backend | `/api/v1/health` | `{"status": "healthy"}` |
| Frontend | `/` | HTTP 200 (static HTML) |

### Kubernetes Probe Alignment

The HEALTHCHECK configuration should align with Kubernetes probes in P4-01:

| Docker HEALTHCHECK | Kubernetes Equivalent |
|-------------------|----------------------|
| `--interval=30s` | `periodSeconds: 30` |
| `--timeout=10s` | `timeoutSeconds: 10` |
| `--start-period=10s` | `initialDelaySeconds: 10` |
| `--retries=3` | `failureThreshold: 3` |

---

## Monitoring and Observability

### Container Health Status

Docker reports health status:
- `starting` - Within start-period
- `healthy` - Last 3 checks passed
- `unhealthy` - Last 3 checks failed

Query with:
```bash
docker inspect --format='{{.State.Health.Status}}' <container>
```

### Metrics

No additional metrics from this task. Container health is surfaced via:
- Docker daemon health status
- Kubernetes pod conditions (when deployed)

---

## Infrastructure Needs

### Base Image Selection

| Service | Base Image | Rationale |
|---------|------------|-----------|
| Backend | `python:{{ cookiecutter.python_version }}-slim` | Minimal Python, no extra packages |
| Frontend | `nginx:alpine` | Minimal nginx, ~5MB overhead |

### Security Considerations

1. **Non-root user**: Prevents privilege escalation
2. **Read-only filesystem**: Consider adding `--read-only` in orchestration
3. **No shell**: Alpine images have shell; consider distroless for higher security

---

## Implementation Notes

### HEALTHCHECK vs Orchestration Probes

Docker HEALTHCHECK is useful for:
- Local development (`docker run`)
- Docker Compose deployments
- Docker Swarm

Kubernetes ignores Docker HEALTHCHECK and uses its own probes. However, having consistent configuration is valuable for:
- Documentation
- Parity between local and production
- Fallback for non-K8s deployments

### curl vs wget

- Backend uses `curl` (already installed for other purposes)
- Frontend uses `wget` (smaller than curl on Alpine, pre-installed)

### Port Considerations

For true non-root operation in frontend:
- Use port 8080 instead of 80
- Update nginx.conf to `listen 8080;`
- Update EXPOSE and HEALTHCHECK accordingly
- Update Kubernetes service/ingress (P4-01)

Alternatively, keep port 80 and run nginx as root (simpler, less secure).

**Recommendation:** Use port 8080 for consistency with non-root security model.

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-DEP-008 | Resource requests and limits defined | Dockerfile sets up minimal images |
| FR-DEP-009 | Liveness/readiness probes configured | HEALTHCHECK provides baseline |
| NFR-003 | Pass Trivy scan (no HIGH/CRITICAL) | Non-root user, minimal base |
| NFR-005 | Follow existing patterns | Matches observability Dockerfile patterns |

### Related ADRs

- ADR-017: Optional Observability Stack (Dockerfile patterns)

### External Resources

- [Docker HEALTHCHECK Reference](https://docs.docker.com/engine/reference/builder/#healthcheck)
- [OCI Image Spec (Labels)](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
- [Running nginx as non-root](https://nginx.org/en/docs/switch_to_non_root.html)
- [Trivy Container Scanning](https://aquasecurity.github.io/trivy/latest/docs/target/container_image/)
