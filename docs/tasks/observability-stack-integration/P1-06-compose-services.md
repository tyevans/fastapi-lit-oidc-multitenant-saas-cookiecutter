# P1-06: Add Observability Services to compose.yml

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P1-06 |
| **Title** | Add Observability Services to compose.yml |
| **Domain** | DevOps |
| **Complexity** | M (1-2 days) |
| **Dependencies** | P1-02, P1-03, P1-04, P1-05 |
| **Blocks** | P1-07, P2-01, P3-01, P4-01 |

---

## Scope

### Included
- Add 5 observability service definitions to compose.yml
- Configure health checks for all services
- Set up service dependencies (startup order)
- Define named volumes for persistent storage
- Configure network membership
- Use Jinja2 conditionals for observability toggle (initial pass)

### Excluded
- Full conditional logic (refined in P4-02)
- Backend environment variables (P2-04)
- Resource limits (documentation-only per FRD)

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/docker-compose.yml` (observability services section)

### Destination File
- `template/{{cookiecutter.project_slug}}/compose.yml`

### Existing compose.yml Structure
The current compose.yml includes:
- postgres, keycloak, backend, frontend, redis services
- Volumes: postgres_data, redis_data, backend_cache, keycloak_data
- Network: {{ cookiecutter.project_slug }}-network

---

## Implementation Details

### Service Definitions

Add the following services after the existing services (redis), wrapped in conditional:

```yaml
{% if cookiecutter.include_observability == "yes" %}
  # ============================================
  # OBSERVABILITY STACK
  # ============================================

  # Prometheus - Metrics Collection and Storage
  prometheus:
    image: prom/prometheus:latest
    container_name: {{ cookiecutter.project_slug }}-prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--web.enable-lifecycle'
    ports:
      - "${PROMETHEUS_PORT:-9090}:9090"
    volumes:
      - ./observability/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:9090/-/healthy"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - {{ cookiecutter.project_slug }}-network

  # Loki - Log Aggregation and Storage
  loki:
    image: grafana/loki:latest
    container_name: {{ cookiecutter.project_slug }}-loki
    command: -config.file=/etc/loki/local-config.yaml
    ports:
      - "${LOKI_PORT:-3100}:3100"
    volumes:
      - ./observability/loki/loki-config.yml:/etc/loki/local-config.yaml:ro
      - loki-data:/loki
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3100/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - {{ cookiecutter.project_slug }}-network

  # Promtail - Docker Container Log Collection
  promtail:
    image: grafana/promtail:latest
    container_name: {{ cookiecutter.project_slug }}-promtail
    command: -config.file=/etc/promtail/promtail-config.yml
    volumes:
      - ./observability/promtail/promtail-config.yml:/etc/promtail/promtail-config.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      loki:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - {{ cookiecutter.project_slug }}-network

  # Tempo - Distributed Tracing Backend
  tempo:
    image: grafana/tempo:latest
    container_name: {{ cookiecutter.project_slug }}-tempo
    command: ["-config.file=/etc/tempo.yaml"]
    ports:
      - "${TEMPO_HTTP_PORT:-3200}:3200"     # Tempo API
      - "${TEMPO_OTLP_GRPC_PORT:-4317}:4317" # OTLP gRPC
      - "${TEMPO_OTLP_HTTP_PORT:-4318}:4318" # OTLP HTTP
    volumes:
      - ./observability/tempo/tempo.yml:/etc/tempo.yaml:ro
      - tempo-data:/tmp/tempo
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3200/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - {{ cookiecutter.project_slug }}-network

  # Grafana - Unified Visualization Platform
  grafana:
    image: grafana/grafana:latest
    container_name: {{ cookiecutter.project_slug }}-grafana
    ports:
      - "${GRAFANA_PORT:-3000}:3000"
    environment:
      # Anonymous access enabled for development convenience
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
      - GF_AUTH_DISABLE_LOGIN_FORM=true
      # Feature toggles for correlation
      - GF_FEATURE_TOGGLES_ENABLE=traceqlEditor
    volumes:
      - ./observability/grafana/datasources:/etc/grafana/provisioning/datasources:ro
      - ./observability/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - grafana-data:/var/lib/grafana
    depends_on:
      prometheus:
        condition: service_healthy
      loki:
        condition: service_healthy
      tempo:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    networks:
      - {{ cookiecutter.project_slug }}-network
{% endif %}
```

### Volume Definitions

Add to the volumes section:

```yaml
volumes:
  # ... existing volumes ...
{% if cookiecutter.include_observability == "yes" %}
  prometheus-data:
    name: {{ cookiecutter.project_slug }}-prometheus-data
  loki-data:
    name: {{ cookiecutter.project_slug }}-loki-data
  tempo-data:
    name: {{ cookiecutter.project_slug }}-tempo-data
  grafana-data:
    name: {{ cookiecutter.project_slug }}-grafana-data
{% endif %}
```

### Service Dependency Graph

```
                    postgres
                       |
                       v
                   keycloak
                       |
   redis ------->  backend  <------- tempo (traces)
                       |
                       v
                   frontend

   loki <-------- promtail

   prometheus + loki + tempo -----> grafana
```

---

## Success Criteria

- [ ] All 5 observability services defined correctly
- [ ] Container names use `{{ cookiecutter.project_slug }}` prefix
- [ ] Health checks configured for Prometheus, Loki, Tempo, Grafana
- [ ] Promtail depends on Loki (service_healthy)
- [ ] Grafana depends on Prometheus, Loki, Tempo (service_healthy)
- [ ] Docker socket mounts configured for Promtail
- [ ] Named volumes defined with project_slug prefix
- [ ] All services use project network
- [ ] Initial Jinja2 conditionals wrap observability content
- [ ] `docker compose config` validates successfully
- [ ] `docker compose up` starts all services successfully

---

## Integration Points

### Upstream
- **P1-02**: Prometheus configuration must exist
- **P1-03**: Loki configuration must exist
- **P1-04**: Promtail configuration must exist
- **P1-05**: Tempo configuration must exist

### Downstream
- **P1-07**: Observability README references service ports
- **P2-01**: Backend dependencies
- **P2-04**: Backend environment variables
- **P3-01**: Grafana datasource provisioning
- **P4-02**: Refined conditional logic

### Contract: Service Ports

Default ports exposed by observability services:

| Service | Default Port | Environment Variable |
|---------|-------------|---------------------|
| Grafana | 3000 | GRAFANA_PORT |
| Prometheus | 9090 | PROMETHEUS_PORT |
| Loki | 3100 | LOKI_PORT |
| Tempo HTTP | 3200 | TEMPO_HTTP_PORT |
| Tempo OTLP gRPC | 4317 | TEMPO_OTLP_GRPC_PORT |
| Tempo OTLP HTTP | 4318 | TEMPO_OTLP_HTTP_PORT |

---

## Monitoring/Observability

After implementation, verify:
- All 5 services start within 90 seconds
- All health checks pass
- Grafana accessible at http://localhost:3000
- Prometheus targets page shows all configured targets
- No error logs from observability services

---

## Infrastructure Needs

**Docker Volumes (4 new):**
- prometheus-data: Metrics TSDB storage
- loki-data: Log chunks and index
- tempo-data: Trace blocks and WAL
- grafana-data: Dashboard state and preferences

**Host Mounts (Promtail):**
- `/var/run/docker.sock` (read-only)
- `/var/lib/docker/containers` (read-only)

---

## Estimated Effort

**Time**: 4-8 hours

Includes:
- Adding all service definitions
- Configuring health checks
- Setting up dependencies
- Testing service startup
- Validating network connectivity
