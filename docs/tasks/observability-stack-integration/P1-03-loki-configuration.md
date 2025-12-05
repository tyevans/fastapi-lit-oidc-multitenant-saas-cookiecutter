# P1-03: Port Loki Configuration

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P1-03 |
| **Title** | Port Loki Configuration |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P1-01 |
| **Blocks** | P1-06 |

---

## Scope

### Included
- Port `loki-config.yml` from implementation-manager to template
- Configure filesystem storage backend for development
- Set appropriate retention and schema settings
- Disable analytics reporting
- Add inline documentation comments

### Excluded
- S3/GCS storage backend configuration (production concern)
- Loki clustering configuration
- Custom log parsing pipelines

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/loki/loki-config.yml`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/loki/loki-config.yml`

---

## Implementation Details

### Configuration Structure

The Loki configuration should include:

1. **Auth Configuration**
   - `auth_enabled: false` (development mode)

2. **Server Configuration**
   - HTTP listen port: 3100
   - gRPC listen port: 9096

3. **Common Configuration**
   - Instance address for replication
   - Path prefix for storage
   - Storage backend: filesystem
   - Replication factor: 1 (single instance)

4. **Schema Configuration**
   - Schema version: v13 (latest stable)
   - Index type: tsdb
   - Object store: filesystem
   - 24-hour index period

5. **Storage Configuration**
   - Filesystem backend
   - Chunks directory: `/loki/chunks`
   - Rules directory: `/loki/rules`

6. **Compactor Configuration**
   - Working directory for compaction
   - Shared store: filesystem

7. **Analytics Configuration**
   - `reporting_enabled: false` (privacy)

### Key Configuration Points

```yaml
# Loki configuration for {{ cookiecutter.project_name }}
# Log aggregation with filesystem storage (development mode)

auth_enabled: false

server:
  http_listen_port: 3100
  grpc_listen_port: 9096

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

ruler:
  alertmanager_url: http://localhost:9093

analytics:
  reporting_enabled: false
```

---

## Success Criteria

- [ ] Configuration file validates against Loki config schema
- [ ] Storage paths match volume mount paths in compose.yml (`/loki`)
- [ ] Auth is disabled for development simplicity
- [ ] Analytics reporting is disabled
- [ ] Schema uses v13 (latest stable)
- [ ] Embedded cache is enabled for query performance
- [ ] Configuration includes inline comments

---

## Integration Points

### Upstream
- **P1-01**: Directory structure must exist

### Downstream
- **P1-04**: Promtail will push logs to Loki at `http://loki:3100`
- **P1-06**: Loki service in compose.yml will mount this configuration
- **P3-01**: Grafana datasource will connect to Loki

### Contract: Loki API
Loki exposes the following endpoints:

| Endpoint | Purpose | Consumer |
|----------|---------|----------|
| POST /loki/api/v1/push | Log ingestion | Promtail (P1-04) |
| GET /ready | Health check | Docker healthcheck |
| GET /metrics | Prometheus metrics | Prometheus (P1-02) |
| GET /loki/api/v1/query | Log queries | Grafana (P3-01) |

---

## Monitoring/Observability

After implementation, verify:
- Loki reaches ready state within 30 seconds
- `/ready` endpoint returns 200
- No configuration errors in Loki logs

---

## Infrastructure Needs

**Docker Volume**: `loki-data` mounted at `/loki`

This volume stores:
- Log chunks
- TSDB index files
- Rule configurations

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Reviewing source configuration
- Validating schema version compatibility
- Adding documentation
- Testing with Docker volume mounts
