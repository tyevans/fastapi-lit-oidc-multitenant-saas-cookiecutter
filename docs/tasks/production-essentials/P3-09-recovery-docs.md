# P3-09: Write Point-in-Time Recovery Documentation

## Task Identifier

| Field | Value |
|-------|-------|
| **Task ID** | P3-09 |
| **Task Title** | Write Point-in-Time Recovery Documentation |
| **Domain** | Documentation |
| **Complexity** | M (Medium) |
| **Estimated Effort** | 1-2 days |
| **Priority** | Should Have |
| **Dependencies** | P3-05 (Backup Scripts), P3-06 (Restore Scripts) |
| **FRD Requirements** | FR-OPS-013, FR-OPS-014 |

---

## Scope

### What This Task Includes

1. Create `docs/operations/database-recovery.md` comprehensive recovery guide
2. Document logical backup recovery (pg_dump/pg_restore)
3. Document point-in-time recovery (PITR) concepts and setup
4. Document disaster recovery procedures
5. Create recovery testing procedures and checklists
6. Document data verification after restore
7. Include common recovery scenarios with step-by-step instructions
8. Add troubleshooting guide for common restore issues
9. Document backup verification procedures
10. Add timing/duration estimates for recovery operations

### What This Task Excludes

- Backup script implementation (P3-05)
- Restore script implementation (P3-06)
- Kubernetes backup CronJob (P3-07)
- ADR documentation (P3-10)
- Multi-region disaster recovery
- Third-party backup tools (Barman, pgBackRest)

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
docs/
  operations/
    database-recovery.md            # Main recovery documentation
    recovery-testing-checklist.md   # Recovery drill checklist
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `scripts/db-backup.sh` | Backup script (P3-05) |
| `scripts/db-restore.sh` | Restore script (P3-06) |
| `compose.yml` | PostgreSQL configuration |
| `scripts/init-db.sql` | Database initialization |

---

## Technical Specification

### Database Recovery Guide Structure

```markdown
# docs/operations/database-recovery.md
# {{ cookiecutter.project_name }} Database Recovery Guide

## Overview

This guide covers database backup and recovery procedures for {{ cookiecutter.project_name }}.
It includes logical backup recovery, point-in-time recovery concepts, and disaster
recovery procedures.

**Important:** Always test recovery procedures in a non-production environment before
applying to production. Recovery operations may result in data loss if performed
incorrectly.

---

## Table of Contents

1. [Backup Overview](#backup-overview)
2. [Recovery Scenarios](#recovery-scenarios)
3. [Logical Backup Recovery](#logical-backup-recovery)
4. [Point-in-Time Recovery (PITR)](#point-in-time-recovery-pitr)
5. [Disaster Recovery](#disaster-recovery)
6. [Recovery Testing](#recovery-testing)
7. [Troubleshooting](#troubleshooting)
8. [Reference](#reference)

---

## Backup Overview

### Backup Types

| Type | Tool | Use Case | RPO | Storage |
|------|------|----------|-----|---------|
| Logical (Full) | pg_dump | Full database restore, migrations | Last backup | ~1x DB size |
| Logical (Schema) | pg_dump --schema-only | Structure restore, dev environments | N/A | ~1MB |
| Physical | pg_basebackup | Large databases, PITR base | Continuous | ~1x DB size |
| WAL Archives | archive_command | Point-in-time recovery | Seconds | Variable |

### Backup Locations

```
./backups/                          # Local backups
  {{ cookiecutter.postgres_db }}_daily_YYYYMMDD_HHMMSS.sql.gz
  {{ cookiecutter.postgres_db }}_weekly_YYYYMMDD_HHMMSS.sql.gz
  {{ cookiecutter.postgres_db }}_monthly_YYYYMMDD_HHMMSS.sql.gz

s3://bucket/backups/                # Remote backups (if configured)
  daily/
  weekly/
  monthly/
```

### Retention Policy

| Backup Type | Retention | Typical Count |
|-------------|-----------|---------------|
| Daily | 7 days | ~7 files |
| Weekly | 4 weeks | ~4 files |
| Monthly | 12 months | ~12 files |

---

## Recovery Scenarios

### Scenario Matrix

| Scenario | Recovery Method | Data Loss | Downtime |
|----------|-----------------|-----------|----------|
| Accidental table drop | Logical restore (table) | Since last backup | Minutes |
| Accidental data deletion | PITR or logical restore | Varies | 10-30 min |
| Database corruption | Full logical restore | Since last backup | 30-60 min |
| Complete server failure | DR restore | Since last backup/WAL | 1-2 hours |
| Schema rollback | Schema restore + data | None (careful) | 10-30 min |

### Decision Flowchart

```
Is the database accessible?
├─ No → Go to "Disaster Recovery"
└─ Yes → What was lost?
          ├─ Specific table/rows → "Selective Recovery"
          ├─ Entire database → "Full Database Recovery"
          └─ Recent transactions → "Point-in-Time Recovery"
```

---

## Logical Backup Recovery

### Prerequisites

- Access to backup files
- PostgreSQL client tools (psql, pg_restore)
- Sufficient disk space (2x backup size recommended)
- Application stopped (to prevent writes during restore)

### Full Database Recovery

**Estimated time:** 10-60 minutes depending on database size

#### Step 1: Stop Application Services

```bash
# Docker Compose
docker compose stop backend

# Kubernetes
kubectl scale deployment backend --replicas=0
```

#### Step 2: Identify Backup to Restore

```bash
# List available backups
ls -la backups/*.sql.gz

# Check backup integrity
./scripts/db-restore.sh --verify-only --backup=backups/{{ cookiecutter.postgres_db }}_daily_20240115_020000.sql.gz
```

#### Step 3: Restore Database

```bash
# Full restore (drops and recreates database)
./scripts/db-restore.sh \
  --backup=backups/{{ cookiecutter.postgres_db }}_daily_20240115_020000.sql.gz \
  --drop-existing

# Or restore to new database for verification
./scripts/db-restore.sh \
  --backup=backups/{{ cookiecutter.postgres_db }}_daily_20240115_020000.sql.gz \
  --target-db={{ cookiecutter.postgres_db }}_restored
```

#### Step 4: Verify Restore

```bash
# Check row counts
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} -c "
SELECT schemaname, relname, n_tup_ins as rows
FROM pg_stat_user_tables
ORDER BY n_tup_ins DESC
LIMIT 10;
"

# Run application health checks
docker compose start backend
curl -s http://localhost:8000/health | jq .
```

#### Step 5: Restart Services

```bash
# Docker Compose
docker compose start backend

# Kubernetes
kubectl scale deployment backend --replicas=2
```

### Selective Table Recovery

**Use case:** Accidentally dropped or corrupted a specific table

#### Step 1: Extract Table from Backup

```bash
# Create temporary restore database
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -c "CREATE DATABASE temp_restore;"

# Restore full backup to temp database
zcat backups/{{ cookiecutter.postgres_db }}_daily_20240115_020000.sql.gz | \
  docker compose exec -T postgres psql -U {{ cookiecutter.postgres_user }} -d temp_restore
```

#### Step 2: Copy Table to Production

```bash
# Dump specific table from temp
docker compose exec postgres pg_dump -U {{ cookiecutter.postgres_user }} -d temp_restore \
  --table=public.your_table \
  --data-only \
  > /tmp/table_data.sql

# Restore to production (append mode)
docker compose exec -T postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} \
  < /tmp/table_data.sql
```

#### Step 3: Cleanup

```bash
# Drop temporary database
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -c "DROP DATABASE temp_restore;"
```

### Selective Row Recovery

**Use case:** Accidentally deleted specific rows

```bash
# 1. Identify what was lost
# 2. Restore to temp database (as above)
# 3. Export specific rows
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d temp_restore -c "
COPY (
  SELECT * FROM your_table
  WHERE id IN (1, 2, 3)  -- IDs to recover
) TO '/tmp/recovered_rows.csv' WITH CSV HEADER;
"

# 4. Import to production
docker compose exec postgres psql -U {{ cookiecutter.postgres_user }} -d {{ cookiecutter.postgres_db }} -c "
COPY your_table FROM '/tmp/recovered_rows.csv' WITH CSV HEADER;
"
```

---

## Point-in-Time Recovery (PITR)

### Overview

PITR allows recovery to any point in time, not just the last backup. This requires:
1. A base backup (pg_basebackup)
2. Archived WAL files
3. PostgreSQL configured for archiving

**Note:** This template uses logical backups by default. PITR requires additional
PostgreSQL configuration.

### Enabling PITR (Production Setup)

#### Step 1: Configure WAL Archiving

Add to `postgresql.conf`:

```ini
# WAL Archiving
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
archive_timeout = 60  # Archive every 60 seconds if no activity
```

#### Step 2: Create Base Backup

```bash
# Create base backup with pg_basebackup
pg_basebackup -h localhost -U {{ cookiecutter.postgres_user }} \
  -D /backups/base_$(date +%Y%m%d_%H%M%S) \
  -Ft -z -P
```

#### Step 3: Recovery to Specific Time

Create `recovery.signal` and set target time:

```bash
# postgresql.auto.conf
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_time = '2024-01-15 14:30:00 UTC'
recovery_target_action = 'pause'
```

#### Step 4: Start Recovery

```bash
# Start PostgreSQL - it will recover to target time
pg_ctl start

# Once recovered, promote if satisfied
psql -c "SELECT pg_wal_replay_resume();"
```

### PITR Considerations

| Factor | Recommendation |
|--------|----------------|
| RPO | Seconds (limited by archive_timeout) |
| RTO | Minutes to hours (depends on WAL volume) |
| Storage | 10-100x WAL per day (depends on write volume) |
| Complexity | High - requires careful configuration |

---

## Disaster Recovery

### Complete Environment Recovery

**Use case:** Full infrastructure failure, need to recover everything

#### Prerequisites

- Access to backup storage (local or S3)
- Fresh PostgreSQL installation
- Application deployment ready

#### Step 1: Set Up New Database

```bash
# Start fresh PostgreSQL
docker compose up -d postgres

# Wait for initialization
sleep 10
```

#### Step 2: Download Latest Backup

```bash
# From S3
aws s3 cp s3://bucket/backups/daily/latest.sql.gz ./backups/

# Or locate local backup
ls -lt backups/*.sql.gz | head -1
```

#### Step 3: Restore Database

```bash
# Initialize with init-db.sql (creates roles, extensions)
docker compose exec -T postgres psql -U postgres < scripts/init-db.sql

# Restore data
./scripts/db-restore.sh --backup=backups/latest.sql.gz
```

#### Step 4: Verify and Start Services

```bash
# Verify data integrity
./scripts/db-restore.sh --verify-restored

# Start application
docker compose up -d
```

### Cross-Region Recovery

For cross-region disaster recovery:

1. **Configure S3 Cross-Region Replication** on backup bucket
2. **Document recovery region** infrastructure setup
3. **Maintain runbook** with region-specific commands
4. **Test quarterly** with full DR drill

---

## Recovery Testing

### Monthly Recovery Drill

Perform this drill monthly to ensure recovery procedures work:

#### Checklist

```markdown
## Recovery Drill Checklist - {{ cookiecutter.project_name }}

Date: _______________
Performed by: _______________

### Preparation
- [ ] Identified test environment
- [ ] Located latest backup
- [ ] Verified backup integrity (checksum)
- [ ] Documented expected row counts

### Recovery Steps
- [ ] Stopped application services
- [ ] Executed restore script
- [ ] Restore completed without errors
- [ ] Verified row counts match expected

### Verification
- [ ] Application health check passes
- [ ] Sample data queries return expected results
- [ ] Authentication works
- [ ] All services communicate properly

### Timing
- Backup download time: ___ minutes
- Restore time: ___ minutes
- Verification time: ___ minutes
- Total recovery time: ___ minutes

### Issues Encountered
_________________________________________________________________
_________________________________________________________________

### Action Items
_________________________________________________________________
_________________________________________________________________

### Sign-off
Performed by: _________________ Date: _______________
Verified by: _________________ Date: _______________
```

### Automated Recovery Testing

Add to CI/CD pipeline:

```yaml
# .github/workflows/recovery-test.yml
name: Recovery Test

on:
  schedule:
    - cron: '0 3 1 * *'  # Monthly on 1st at 3 AM

jobs:
  recovery-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start test database
        run: docker compose up -d postgres

      - name: Download latest backup
        run: |
          aws s3 cp s3://bucket/backups/daily/$(date -d yesterday +%Y%m%d)*.sql.gz ./test-backup.sql.gz

      - name: Restore backup
        run: |
          ./scripts/db-restore.sh --backup=test-backup.sql.gz --target-db=test_restore

      - name: Verify restore
        run: |
          ./scripts/db-restore.sh --verify-restored --target-db=test_restore

      - name: Report results
        if: always()
        run: |
          # Send notification with results
          echo "Recovery test completed"
```

---

## Troubleshooting

### Common Issues

#### Issue: "Role does not exist"

**Symptom:**
```
ERROR: role "app_user" does not exist
```

**Solution:**
Run init-db.sql before restore to create roles:
```bash
docker compose exec -T postgres psql -U postgres < scripts/init-db.sql
```

#### Issue: "Database already exists"

**Symptom:**
```
ERROR: database "{{ cookiecutter.postgres_db }}" already exists
```

**Solution:**
Use `--drop-existing` flag or manually drop:
```bash
./scripts/db-restore.sh --backup=backup.sql.gz --drop-existing

# Or manually
docker compose exec postgres psql -U postgres -c "DROP DATABASE {{ cookiecutter.postgres_db }};"
```

#### Issue: "Checksum mismatch"

**Symptom:**
```
ERROR: Checksum verification failed
```

**Solution:**
Backup may be corrupted. Try:
1. Re-download from S3
2. Use a different backup
3. Check disk for errors

#### Issue: "Out of disk space"

**Symptom:**
```
ERROR: could not extend file: No space left on device
```

**Solution:**
```bash
# Check disk space
df -h

# Clean up old backups
find backups/ -name "*.sql.gz" -mtime +30 -delete

# Or expand storage
```

#### Issue: "Lock timeout"

**Symptom:**
```
ERROR: canceling statement due to lock timeout
```

**Solution:**
Ensure all connections are closed:
```bash
docker compose exec postgres psql -U postgres -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '{{ cookiecutter.postgres_db }}'
AND pid <> pg_backend_pid();
"
```

### Recovery Metrics

Track these metrics for recovery procedures:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Backup success rate | 100% | Monitor backup cron |
| Backup size growth | <10%/month | Compare monthly |
| Restore test success | 100% | Monthly drill |
| Recovery time | <1 hour | Time drill |

---

## Reference

### Quick Commands

```bash
# List backups
ls -la backups/*.sql.gz

# Check backup size
du -h backups/

# Verify backup integrity
sha256sum -c backups/backup.sql.gz.sha256

# Quick restore (development)
./scripts/db-restore.sh --backup=backups/latest.sql.gz

# Restore with verification
./scripts/db-restore.sh --backup=backups/latest.sql.gz --verify

# Restore to new database
./scripts/db-restore.sh --backup=backups/latest.sql.gz --target-db=test_restore
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| POSTGRES_HOST | localhost | Database host |
| POSTGRES_PORT | 5432 | Database port |
| POSTGRES_DB | {{ cookiecutter.postgres_db }} | Database name |
| POSTGRES_USER | {{ cookiecutter.postgres_user }} | Database user |
| PGPASSWORD | (required) | Database password |
| BACKUP_DIR | ./backups | Backup directory |

### Related Documentation

- [Backup Scripts](../../scripts/db-backup.sh)
- [Restore Scripts](../../scripts/db-restore.sh)
- [ADR-023: Database Backup Strategy](../adr/023-database-backup-strategy.md)
- [Runbook: Database Recovery](../runbooks/db-connections.md)
```

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P3-05 | Required | References backup script interface |
| P3-06 | Required | References restore script interface |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P3-10 | Reference | ADR references recovery documentation |

---

## Success Criteria

### Functional Requirements

- [ ] FR-OPS-013: Point-in-time recovery documentation shall be included
- [ ] FR-OPS-014: Database restoration procedure shall be documented and tested
- [ ] Full database recovery documented with step-by-step instructions
- [ ] Selective table/row recovery documented
- [ ] PITR concepts and setup documented
- [ ] Disaster recovery procedures documented
- [ ] Recovery testing checklist included
- [ ] Troubleshooting guide for common issues
- [ ] Timing estimates for recovery operations
- [ ] Quick reference commands included

### Non-Functional Requirements

- [ ] Documentation is clear and actionable
- [ ] Commands are copy-paste ready
- [ ] All placeholders use cookiecutter variables
- [ ] Procedures tested in development environment
- [ ] Consistent formatting with other docs

### Validation Steps

1. Documentation review
   - Verify all recovery scenarios covered
   - Verify commands match script interfaces
   - Check for missing steps

2. Procedure testing
   - Execute full recovery in dev environment
   - Execute selective recovery
   - Verify troubleshooting steps

3. Timing validation
   - Measure actual recovery times
   - Update estimates if needed

---

## Integration Points

### Script Interface Reference

Recovery documentation references these script interfaces:

```bash
# Backup script (P3-05)
./scripts/db-backup.sh [--type=daily|weekly|monthly] [--verify] [--schema-only]

# Restore script (P3-06)
./scripts/db-restore.sh --backup=FILE [--drop-existing] [--verify] [--target-db=NAME]
```

### Environment Configuration

Documentation uses these environment variables:
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`
- `PGPASSWORD` (required for restore operations)
- `BACKUP_DIR` (backup file location)

---

## Monitoring and Observability

### Recovery Metrics to Track

| Metric | Source | Purpose |
|--------|--------|---------|
| backup_last_success_timestamp | Prometheus | Detect backup failures |
| restore_test_success | CI/CD | Track recovery health |
| recovery_time_seconds | Manual drill | Validate RTO |

### Alerting Recommendations

```yaml
# Add to alerts.yml
- alert: BackupAgeExceedsThreshold
  expr: time() - backup_last_success_timestamp > 86400 * 2  # 2 days
  labels:
    severity: critical
  annotations:
    summary: "Database backup is stale"
    description: "No successful backup in 48 hours"
```

---

## Infrastructure Needs

### No Infrastructure Changes Required

This task creates documentation only.

### Recommended Testing Environment

- Isolated PostgreSQL instance for recovery testing
- Sufficient storage for backup files (2x database size)
- Network access to backup storage (S3 if applicable)

---

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Comprehensive documentation with multiple scenarios
- Must align with backup/restore script interfaces
- Testing procedures require execution and validation
- Troubleshooting section requires real-world issue coverage

---

## Implementation Notes

### Documentation Structure

The recovery guide follows a scenario-based approach:
1. **What happened?** - Identify the scenario
2. **What do I need?** - Prerequisites
3. **How do I fix it?** - Step-by-step instructions
4. **How do I verify?** - Confirmation steps
5. **What if it fails?** - Troubleshooting

### Timing Estimates

Provide realistic timing estimates based on:
- Database size (use 1GB as baseline)
- Network speed (for S3 downloads)
- Compression ratio (~10x typical)

### Cross-Referencing

Link to related documents:
- Backup scripts (P3-05)
- Restore scripts (P3-06)
- ADR-023 (P3-10)
- Runbooks (P3-08)

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| FR-OPS-013 | Point-in-time recovery documentation | PITR section |
| FR-OPS-014 | Database restoration procedure documented and tested | Full recovery guide |

### Related Tasks

- P3-05: Database Backup Scripts
- P3-06: Restore and Recovery Scripts
- P3-07: Kubernetes Backup CronJob
- P3-08: Operational Runbook Templates
- P3-10: ADR-023 Database Backup Strategy

### External Resources

- [PostgreSQL Backup and Restore](https://www.postgresql.org/docs/current/backup.html)
- [PostgreSQL PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)
- [pg_dump Documentation](https://www.postgresql.org/docs/current/app-pgdump.html)
- [pg_restore Documentation](https://www.postgresql.org/docs/current/app-pgrestore.html)
