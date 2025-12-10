# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2024-XX-XX

### Added

#### CI/CD Pipeline (Phase 1)

- **GitHub Actions CI Workflow** (`ci.yml`)
  - Automated testing on pull requests and pushes to main
  - Backend linting with ruff and testing with pytest
  - Frontend linting with eslint and testing with vitest
  - Coverage reporting with Codecov integration
  - Parallel job execution for faster feedback

- **GitHub Actions Build Workflow** (`build.yml`)
  - Multi-platform Docker image builds (linux/amd64, linux/arm64)
  - Automatic image tagging with git SHA, semantic version, and `latest`
  - Push to GitHub Container Registry (ghcr.io)
  - SBOM generation for security compliance
  - Build caching for faster subsequent builds

- **Dependabot Configuration**
  - Automated dependency updates for Python (pip)
  - Automated dependency updates for Node.js (npm)
  - Automated updates for GitHub Actions
  - Weekly update schedule with reasonable PR limits

- **Production Dockerfiles**
  - Multi-stage builds for smaller images
  - HEALTHCHECK instructions for container orchestration
  - Non-root user execution for security
  - Optimized layer caching

#### Security Hardening (Phase 2)

- **Security Headers Middleware**
  - Content-Security-Policy (CSP) with configurable directives
  - Strict-Transport-Security (HSTS) for HTTPS enforcement
  - X-Frame-Options to prevent clickjacking
  - X-Content-Type-Options to prevent MIME sniffing
  - Referrer-Policy for privacy protection
  - All headers configurable via environment variables

- **Vulnerability Scanning**
  - Trivy container image scanning in CI pipeline
  - pip-audit for Python dependency vulnerability scanning
  - npm audit for Node.js dependency scanning
  - Build fails on HIGH or CRITICAL vulnerabilities

- **Secret Detection**
  - gitleaks pre-commit hook for detecting leaked credentials
  - Patterns for API keys, passwords, private keys, and tokens
  - Blocks commits containing potential secrets

- **Security Documentation**
  - Security audit checklist for deployments
  - Security configuration guide
  - Incident response guidelines

#### Operational Readiness (Phase 3)

- **Prometheus Alerting Rules**
  - High error rate alerts (5xx responses > 1% for 5 minutes)
  - High latency alerts (p95 > 2 seconds for 5 minutes)
  - Database connection pool exhaustion warnings
  - Redis connection failure alerts
  - Service availability monitoring

- **Sentry Integration** (Optional)
  - Automatic exception capture and reporting
  - User context enrichment (tenant_id, user_id)
  - Release tracking for deployment correlation
  - PII filtering via configurable before_send hook
  - Performance monitoring with transaction sampling

- **Database Backup and Recovery**
  - `backup-db.sh` script for automated PostgreSQL backups
  - `restore-db.sh` script for point-in-time recovery
  - Configurable retention policies
  - Compression and verification
  - Kubernetes CronJob for scheduled backups

- **Operational Runbooks**
  - Incident response procedures
  - Database recovery procedures
  - Service scaling guides
  - Post-incident review templates

#### Kubernetes Deployment (Phase 4)

- **Kustomize-Based Manifests**
  - Base manifests for shared configuration
  - Staging overlay with development-appropriate settings
  - Production overlay with high-availability configuration
  - Proper resource limits and requests

- **Kubernetes Resources**
  - Backend and frontend Deployments with health probes
  - Services with proper port mapping
  - ConfigMaps for environment configuration
  - Secret references for sensitive data
  - Ingress with TLS termination support

- **GitHub Actions Deploy Workflow** (`deploy.yml`)
  - Manual trigger with environment selection
  - Automatic staging deployment on main merge
  - Production deployment with approval gates
  - Rollback support

- **Production Docker Compose**
  - `compose.production.yml` for non-Kubernetes deployments
  - Production Docker targets with optimizations
  - External database/Redis configuration support
  - Proper resource limits

#### Developer Experience (Phase 5)

- **OpenAPI Client Generation**
  - TypeScript API client generation from OpenAPI spec
  - `generate-api-client.sh` script for easy regeneration
  - Type-safe API calls in frontend
  - Automatic validation option

- **k6 Load Testing**
  - Smoke tests for quick validation
  - Load tests for sustained traffic simulation
  - Stress tests for finding breaking points
  - Authentication flow tests
  - Configurable thresholds and scenarios

- **API Versioning Documentation**
  - URL path versioning strategy (`/api/v1`, `/api/v2`)
  - Deprecation policy guidelines
  - Breaking change criteria
  - Client migration guidance

- **Performance Baseline Documentation**
  - Response time expectations
  - Throughput targets
  - Resource utilization guidelines

#### Documentation (Phase 6)

- **Updated CLAUDE.md**
  - Complete feature reference
  - Configuration options
  - Architecture decisions

- **Migration Guide**
  - Step-by-step upgrade instructions
  - Breaking change documentation
  - Feature adoption guidance

- **Template Validation**
  - Automated validation test suite
  - All 16 option combinations tested
  - Python, YAML, JSON syntax validation
  - Conditional file verification

- **E2E Deployment Validation**
  - `run-e2e-validation.sh` script for full lifecycle testing
  - GitHub Actions E2E workflow
  - Manual validation checklist
  - Docker and Kubernetes validation

- **This Changelog**
  - Following Keep a Changelog format
  - Semantic versioning compliance
  - Detailed release notes

### Changed

- **Dockerfile Improvements**
  - Production targets now use multi-stage builds
  - Added HEALTHCHECK instructions
  - Runs as non-root user by default

- **Pre-commit Configuration**
  - Extended with security hooks (gitleaks)
  - Added ruff for Python linting
  - Added type checking hooks

- **Prometheus Configuration**
  - Now references external alerting rules file
  - Updated scrape configurations
  - Added backend metrics target

### New Cookiecutter Options

| Option | Default | Description |
|--------|---------|-------------|
| `include_github_actions` | `yes` | Include GitHub Actions CI/CD workflows |
| `include_kubernetes` | `no` | Include Kubernetes deployment manifests |
| `include_sentry` | `no` | Include Sentry error tracking integration |

### Breaking Changes

1. **New Environment Variables Required**

   When security headers are enabled (default), the following environment variables are used:
   ```env
   X_FRAME_OPTIONS=DENY
   CSP_POLICY=default-src 'self'; script-src 'self' 'unsafe-inline'
   FORCE_HSTS=false
   HSTS_MAX_AGE=31536000
   ```

2. **Middleware Stack Order Changed**

   Security headers middleware is now added after CORS middleware:
   ```python
   app.add_middleware(CORSMiddleware, ...)
   app.add_middleware(SecurityHeadersMiddleware)  # NEW
   app.add_middleware(TenantMiddleware)
   ```

3. **Config Schema Expanded**

   `backend/app/core/config.py` has new fields for security headers and Sentry.
   Existing projects need to add these settings.

### Deprecated

- None

### Removed

- None

### Fixed

- None (new features only in this release)

### Security

- Container images are now scanned with Trivy (fails on HIGH/CRITICAL)
- Python dependencies scanned with pip-audit
- Node.js dependencies scanned with npm audit
- Secret detection with gitleaks prevents credential commits
- Security headers middleware mitigates common web vulnerabilities
- HSTS enforcement for HTTPS-only deployments

## [1.0.0] - 2024-XX-XX

### Added

- Initial release with full-stack template
- **FastAPI Backend**
  - Python 3.13+ with async support
  - Pydantic v2 for data validation
  - SQLAlchemy 2.0 with async sessions
  - Alembic for database migrations

- **Lit Frontend**
  - TypeScript-first development
  - Vite for fast development builds
  - Tailwind CSS for styling
  - Vitest for unit testing
  - Playwright for E2E testing

- **Keycloak Authentication**
  - OAuth 2.0 / OIDC integration
  - PKCE enforcement for security
  - Multi-tenant realm configuration
  - Token validation and refresh

- **Multi-Tenant Architecture**
  - Row-Level Security (RLS) in PostgreSQL
  - Automatic tenant isolation
  - Tenant context middleware
  - Dual database users (admin/app)

- **Optional Observability Stack**
  - Prometheus for metrics collection
  - Grafana for visualization
  - Loki for log aggregation
  - Tempo for distributed tracing
  - Pre-configured dashboards

- **Docker Compose Development**
  - Complete local development environment
  - Hot-reload for backend and frontend
  - Service orchestration
  - Volume persistence

- **Comprehensive Testing**
  - pytest for backend unit/integration tests
  - vitest for frontend unit tests
  - Playwright for E2E browser tests
  - Test fixtures and factories

- **Cookiecutter Template**
  - Customizable project generation
  - Optional feature toggles
  - Post-generation hooks
  - Template validation tests

---

[Unreleased]: https://github.com/your-org/project-starter/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/your-org/project-starter/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/your-org/project-starter/releases/tag/v1.0.0
