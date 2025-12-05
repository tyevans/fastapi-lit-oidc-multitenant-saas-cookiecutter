# P1-04: Port Promtail Configuration

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P1-04 |
| **Title** | Port Promtail Configuration |
| **Domain** | DevOps |
| **Complexity** | S (4-8 hours) |
| **Dependencies** | P1-01 |
| **Blocks** | P1-06 |

---

## Scope

### Included
- Port `promtail-config.yml` from implementation-manager to template
- Configure Docker service discovery for container log collection
- Set up label extraction from Docker metadata
- Configure Loki push endpoint
- Add inline documentation comments

### Excluded
- Custom log parsing pipelines (application-specific)
- File-based log collection (using Docker socket approach)
- Log level extraction from log content (future enhancement)

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/promtail/promtail-config.yml`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/promtail/promtail-config.yml`

---

## Implementation Details

### Configuration Structure

```yaml
# Promtail configuration for {{ cookiecutter.project_name }}
# Collects logs from Docker containers via Docker socket

server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 5s
    relabel_configs:
      # Extract container name (remove leading slash)
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'

      # Extract log stream (stdout/stderr)
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'stream'

      # Extract Docker Compose service name
      - source_labels: ['__meta_docker_container_label_com_docker_compose_service']
        target_label: 'service'

      # Extract Docker Compose project name
      - source_labels: ['__meta_docker_container_label_com_docker_compose_project']
        target_label: 'project'
```

### Key Configuration Points

1. **Docker Service Discovery**
   - Uses Docker socket (`/var/run/docker.sock`)
   - 5-second refresh interval for container discovery
   - Automatically discovers new containers

2. **Label Extraction**
   - `container`: Full container name (without leading slash)
   - `stream`: stdout or stderr
   - `service`: Docker Compose service name
   - `project`: Docker Compose project name

3. **Loki Client**
   - Push URL: `http://loki:3100/loki/api/v1/push`
   - Uses internal Docker network for communication

4. **Positions File**
   - Tracks log read positions for resume capability
   - Stored at `/tmp/positions.yaml`

### Docker Socket Approach

This configuration uses the Docker socket approach rather than file-based log collection:

**Advantages:**
- Automatic container discovery
- No need to map log file paths
- Works with any logging driver
- Simpler configuration

**Requirements:**
- Docker socket must be mounted: `/var/run/docker.sock:/var/run/docker.sock:ro`
- Container log access: `/var/lib/docker/containers:/var/lib/docker/containers:ro`

---

## Success Criteria

- [ ] Configuration validates against Promtail config schema
- [ ] Docker service discovery is properly configured
- [ ] Label extraction correctly maps container metadata
- [ ] Loki push URL uses correct internal hostname
- [ ] Positions file path is writable
- [ ] Configuration includes inline comments
- [ ] Logs from all project containers appear in Loki within 5 seconds

---

## Integration Points

### Upstream
- **P1-01**: Directory structure must exist
- **P1-03**: Loki must be running to receive logs

### Downstream
- **P1-06**: Promtail service in compose.yml will:
  - Mount this configuration
  - Mount Docker socket
  - Mount container logs directory
  - Depend on Loki service

### Contract: Log Labels

Promtail extracts and applies the following labels to all logs:

| Label | Source | Example Value |
|-------|--------|---------------|
| `container` | `__meta_docker_container_name` | `my-project-backend` |
| `service` | `__meta_docker_container_label_com_docker_compose_service` | `backend` |
| `stream` | `__meta_docker_container_log_stream` | `stdout`, `stderr` |
| `project` | `__meta_docker_container_label_com_docker_compose_project` | `my-project` |

These labels enable LogQL queries like:
```logql
{service="backend"}
{container="my-project-keycloak"}
{stream="stderr"}
```

---

## Monitoring/Observability

After implementation, verify:
- Promtail logs show successful connection to Docker socket
- Container discovery logs appear
- No "push" errors in Promtail logs
- Logs appear in Loki within 5 seconds of emission

---

## Infrastructure Needs

**Docker Mounts Required:**
- `/var/run/docker.sock:/var/run/docker.sock:ro` (container discovery)
- `/var/lib/docker/containers:/var/lib/docker/containers:ro` (log access)

**Note:** These mounts require appropriate permissions on the host system. The `:ro` flag ensures read-only access.

---

## Estimated Effort

**Time**: 2-4 hours

Includes:
- Reviewing source configuration
- Testing Docker socket access
- Validating label extraction
- Testing log flow to Loki
