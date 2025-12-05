# P3-02: Create Dashboard Provisioning Configuration

## Task Overview

| Field | Value |
|-------|-------|
| **Task ID** | P3-02 |
| **Title** | Create Dashboard Provisioning Configuration |
| **Domain** | DevOps |
| **Complexity** | XS (< 4 hours) |
| **Dependencies** | P3-01 |
| **Blocks** | P3-03 |

---

## Scope

### Included
- Create dashboards.yml for Grafana dashboard provisioning
- Configure dashboard folder and discovery settings
- Set update behavior for provisioned dashboards

### Excluded
- Dashboard JSON files (handled in P3-03)
- Custom folders beyond default
- Dashboard permissions configuration

---

## Relevant Code Areas

### Source File
- `/home/ty/workspace/project-starter/implementation-manager/observability/grafana/dashboards/dashboards.yml`

### Destination File
- `template/{{cookiecutter.project_slug}}/observability/grafana/dashboards/dashboards.yml`

---

## Implementation Details

### Dashboard Provisioning Configuration

```yaml
# Grafana dashboard provisioning for {{ cookiecutter.project_name }}
# Loads dashboards from the local filesystem on startup

apiVersion: 1

providers:
  # Default dashboard provider
  # Loads all JSON files from /etc/grafana/provisioning/dashboards
  - name: 'default'
    orgId: 1
    folder: ''                    # Root folder (empty = General)
    folderUid: ''                 # Auto-generate folder UID
    type: file
    disableDeletion: false        # Allow deleting provisioned dashboards
    editable: true                # Allow editing provisioned dashboards
    updateIntervalSeconds: 10     # Check for updates every 10 seconds
    allowUiUpdates: true          # Allow saving changes via UI
    options:
      path: /etc/grafana/provisioning/dashboards
      foldersFromFilesStructure: false  # Don't create folders from directories
```

### Configuration Options Explained

| Option | Value | Purpose |
|--------|-------|---------|
| `name` | 'default' | Provider identifier |
| `orgId` | 1 | Default organization ID |
| `folder` | '' | Store in General folder |
| `type` | file | Load from filesystem |
| `disableDeletion` | false | Allow dashboard removal |
| `editable` | true | Allow editing in UI |
| `updateIntervalSeconds` | 10 | Refresh interval for changes |
| `allowUiUpdates` | true | Save UI changes back to file |
| `path` | /etc/grafana/provisioning/dashboards | Dashboard JSON location |

### Development vs Production Settings

**Development (current):**
- `editable: true` - Developers can modify dashboards
- `allowUiUpdates: true` - Changes saved to volume
- `disableDeletion: false` - Can remove dashboards

**Production (documentation note):**
- `editable: false` - Prevent accidental changes
- `allowUiUpdates: false` - Read-only provisioning
- `disableDeletion: true` - Preserve dashboards

---

## Success Criteria

- [ ] dashboards.yml created in grafana/dashboards directory
- [ ] Provider configuration is valid YAML
- [ ] Dashboards are loaded from correct path
- [ ] Dashboards are editable in Grafana UI
- [ ] Dashboard changes persist to volume
- [ ] No errors in Grafana logs on startup

---

## Integration Points

### Upstream
- **P3-01**: Datasources must be configured for dashboard queries

### Downstream
- **P3-03**: Backend dashboard JSON will be loaded by this provider

### Contract: Dashboard Location

Dashboard JSON files must be placed in:
```
observability/grafana/dashboards/
```

This maps to the container path:
```
/etc/grafana/provisioning/dashboards
```

Via the volume mount in compose.yml:
```yaml
volumes:
  - ./observability/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
```

### Contract: Dashboard JSON Format

Grafana expects dashboard JSON with this structure:
```json
{
  "dashboard": {
    "uid": "unique-dashboard-id",
    "title": "Dashboard Title",
    "panels": [...],
    ...
  },
  "overwrite": true
}
```

Or simplified format (auto-wrapped by Grafana):
```json
{
  "uid": "unique-dashboard-id",
  "title": "Dashboard Title",
  "panels": [...],
  ...
}
```

---

## Monitoring/Observability

After implementation, verify:
- Grafana logs show "starting to provision dashboards"
- No provisioning errors in Grafana logs
- Dashboards appear in Grafana after startup

---

## Infrastructure Needs

**Grafana Volume Mount** (from P1-06):
```yaml
volumes:
  - ./observability/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
```

---

## Estimated Effort

**Time**: 30 minutes - 1 hour

This is a simple configuration file:
- Create YAML configuration
- Validate syntax
- Test dashboard loading
