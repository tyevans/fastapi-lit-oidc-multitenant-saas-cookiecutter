# P1-05: Port Tempo Configuration

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P1-05 |
| **Title** | Port Tempo Configuration |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P1-01 |
| **Blocks** | P1-06 |

---

## Scope

### Included
- Port `tempo.yml` from implementation-manager to template
- Configure OTLP receivers (gRPC and HTTP)
- Set up local filesystem storage for development
- Configure block retention and compaction
- Add inline documentation comments

### Excluded
- S3/GCS storage backend (production concern)
- Tempo distributed mode configuration
- Search/traceQL advanced configuration

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/tempo/tempo.yml`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/tempo/tempo.yml`

---

## Implementation Details

### Configuration Structure

```yaml
# Tempo configuration for {{ cookiecutter.project_name }}
# Distributed tracing backend with OTLP receivers

server:
  http_listen_port: 3200

query_frontend:
  search:
    duration_slo: 5s
    throughput_bytes_slo: 1.073741824e+09

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
        http:
          endpoint: 0.0.0.0:4318

ingester:
  max_block_duration: 5m

compactor:
  compaction:
    block_retention: 1h

storage:
  trace:
    backend: local
    local:
      path: /tmp/tempo/blocks
    wal:
      path: /tmp/tempo/wal
    block:
      bloom_filter_false_positive: .05
      v2_index_downsample_bytes: 1000
      v2_encoding: zstd

metrics_generator:
  registry:
    external_labels:
      source: tempo
      cluster: docker-compose
  storage:
    path: /tmp/tempo/generator/wal
    remote_write: []
```

### Key Configuration Points

1. **OTLP Receivers**
   - gRPC on port 4317 (primary for backend)
   - HTTP on port 4318 (for frontend/browser traces)
   - Both bind to 0.0.0.0 for container accessibility

2. **Storage Configuration**
   - Backend: local filesystem
   - Blocks path: `/tmp/tempo/blocks`
   - WAL path: `/tmp/tempo/wal`
   - ZSTD encoding for compression

3. **Retention Configuration**
   - Block retention: 1 hour (development)
   - Max block duration: 5 minutes (fast trace availability)

4. **HTTP API**
   - Port 3200 for Tempo API
   - Used by Grafana for trace queries

### Port Mapping

| Port | Protocol | Purpose |
|------|----------|---------|
| 3200 | HTTP | Tempo API (queries, health) |
| 4317 | gRPC | OTLP trace ingestion (backend) |
| 4318 | HTTP | OTLP trace ingestion (frontend) |

---

## Success Criteria

- [ ] Configuration validates against Tempo config schema
- [ ] OTLP gRPC receiver enabled on port 4317
- [ ] OTLP HTTP receiver enabled on port 4318
- [ ] Storage backend configured for filesystem
- [ ] Block retention set to 1 hour (development appropriate)
- [ ] Receivers bind to 0.0.0.0 for container access
- [ ] Configuration includes inline comments

---

## Integration Points

### Upstream
- **P1-01**: Directory structure must exist

### Downstream
- **P1-06**: Tempo service in compose.yml will mount this configuration
- **P2-02**: Backend observability module will export traces to Tempo
- **P3-01**: Grafana datasource will connect to Tempo

### Contract: OTLP Ingestion

Tempo accepts traces via OTLP protocol:

| Protocol | Endpoint | Client |
|----------|----------|--------|
| gRPC | `tempo:4317` | Backend (P2-02) |
| HTTP | `tempo:4318` | Future frontend tracing |

**Backend Environment Variable:**
```
OTEL_EXPORTER_OTLP_ENDPOINT=http://tempo:4317
```

### Contract: Tempo API

| Endpoint | Purpose | Consumer |
|----------|---------|----------|
| GET /ready | Health check | Docker healthcheck |
| GET /metrics | Prometheus metrics | Prometheus (P1-02) |
| GET /api/traces/{traceID} | Trace query | Grafana (P3-01) |
| GET /api/search | Trace search | Grafana (P3-01) |

---

## Monitoring/Observability

After implementation, verify:
- Tempo reaches ready state within 30 seconds
- `/ready` endpoint returns 200
- OTLP receivers are listening (check logs)
- Test trace can be submitted and queried

---

## Infrastructure Needs

**Docker Volume**: `tempo-data` mounted at `/tmp/tempo`

This volume stores:
- Trace blocks
- Write-Ahead Log (WAL)
- Metrics generator data

**Note:** Using `/tmp/tempo` as the base path (matching implementation-manager).

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Reviewing source configuration
- Validating OTLP receiver settings
- Testing trace ingestion
- Validating storage paths
