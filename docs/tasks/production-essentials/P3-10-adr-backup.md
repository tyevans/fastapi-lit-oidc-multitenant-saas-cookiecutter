# P3-10: Write ADR-023: Database Backup Strategy

## Task Identifier

| Field | Value |
|-------|-------|
| **Task ID** | P3-10 |
| **Task Title** | Write ADR-023: Database Backup Strategy |
| **Domain** | Architecture |
| **Complexity** | S (Small) |
| **Estimated Effort** | 0.5-1 day |
| **Priority** | Should Have |
| **Dependencies** | P3-05 (Backup Scripts) |
| **FRD Requirements** | NFR-001 |

---

## Scope

### What This Task Includes

1. Create ADR-023 documenting database backup strategy decisions
2. Document the choice of pg_dump over pg_basebackup
3. Explain retention policy rationale (7 daily, 4 weekly, 12 monthly)
4. Document plain-text SQL format decision
5. Explain S3 integration approach
6. Document fail-open pattern for backup operations
7. List considered alternatives and why they were rejected
8. Include future enhancement roadmap

### What This Task Excludes

- Implementation of backup scripts (P3-05)
- Implementation of restore scripts (P3-06)
- Recovery documentation (P3-09)
- Actual backup testing or validation

---

## Relevant Code Areas

### Files to Create

```
template/{{cookiecutter.project_slug}}/
docs/
  adr/
    023-database-backup-strategy.md
```

### Reference Files (Read-Only)

| File | Purpose |
|------|---------|
| `docs/adr/017-optional-observability-stack.md` | ADR format reference |
| `scripts/db-backup.sh` | Backup implementation (P3-05) |
| `scripts/db-restore.sh` | Restore implementation (P3-06) |

---

## Technical Specification

### ADR-023: Database Backup Strategy

```markdown
# docs/adr/023-database-backup-strategy.md
# ADR-023: Database Backup Strategy

## Status

Accepted

## Date

{{ cookiecutter._creation_date }}

## Context

{{ cookiecutter.project_name }} requires a reliable database backup strategy to protect
against data loss, enable disaster recovery, and support operational procedures such
as database migrations and environment cloning.

### Requirements

The backup strategy must support:

1. **Recovery Point Objective (RPO):** Maximum acceptable data loss
   - Development: 24 hours (daily backups sufficient)
   - Production: Should support near-zero with PITR option

2. **Recovery Time Objective (RTO):** Maximum acceptable downtime
   - Target: < 1 hour for full database restore
   - < 10 minutes for selective data recovery

3. **Operational Needs:**
   - Regular automated backups
   - Multiple retention tiers (daily, weekly, monthly)
   - Remote storage for disaster recovery
   - Ability to restore to specific point in time (future enhancement)

### Constraints

- PostgreSQL as the database (version {{ cookiecutter.postgres_version }})
- Template must work across various deployment environments (Docker, Kubernetes, VMs)
- Minimal external dependencies for core backup functionality
- Optional cloud storage integration (S3-compatible)

## Decision

We will implement a **logical backup strategy using pg_dump** with the following
characteristics:

### 1. Backup Method: pg_dump (Logical Backups)

**Choice:** Use `pg_dump` for all regular backups

**Rationale:**
- Cross-version compatibility (can restore to different PostgreSQL versions)
- Selective restore capability (individual tables/rows)
- Human-readable SQL output for debugging and auditing
- Smaller backup size for typical application databases
- No need for PostgreSQL superuser privileges
- Works identically across all deployment environments

### 2. Backup Format: Plain-Text SQL with Compression

**Choice:** Generate plain-text SQL dumps compressed with gzip

**Format:** `{database}_{type}_{timestamp}.sql.gz`

**Rationale:**
- Can be inspected and modified if needed
- Works with standard Unix tools (zcat, grep, etc.)
- No special restore tools required beyond psql
- Good compression ratio (~10:1 typical)
- Can be piped directly for streaming operations

### 3. Retention Policy: Tiered Retention

**Choice:** Implement three retention tiers

| Tier | Retention | Purpose |
|------|-----------|---------|
| Daily | 7 days | Recent recovery, development |
| Weekly | 4 weeks | Point-in-time recovery window |
| Monthly | 12 months | Compliance, long-term archive |

**Rationale:**
- Balances storage costs with recovery options
- Provides multiple recovery points at different granularities
- Meets common compliance requirements (1-year retention)
- Configurable via environment variables for different needs

### 4. Storage: Local with Optional S3

**Choice:** Primary storage local, optional sync to S3-compatible storage

**Rationale:**
- Local storage ensures fast backup/restore operations
- S3 integration provides off-site disaster recovery
- S3 lifecycle policies can manage long-term retention
- Works with any S3-compatible storage (AWS, MinIO, etc.)
- Optional dependency - core functionality works without cloud access

### 5. Verification: Checksum and Structure Validation

**Choice:** Generate SHA256 checksums and validate SQL structure on restore

**Rationale:**
- Detects corruption before attempting restore
- Quick validation without full restore
- Standard checksum format compatible with verification tools
- Structure validation catches truncated or incomplete dumps

### 6. Scheduling: External Scheduler

**Choice:** Provide scripts, rely on external scheduling (cron, Kubernetes CronJob)

**Rationale:**
- Flexibility to use platform-native scheduling
- No additional daemon required
- Works with existing monitoring and alerting
- Clear separation of concerns

## Alternatives Considered

### Alternative 1: pg_basebackup (Physical Backups)

**Pros:**
- Fastest backup and restore for large databases
- Required for true point-in-time recovery (PITR)
- Captures entire cluster state

**Cons:**
- Requires same PostgreSQL major version for restore
- Larger backup size (entire data directory)
- More complex setup (WAL archiving configuration)
- Requires superuser or replication privileges

**Decision:** Rejected for default implementation. Physical backups are better suited
for large production databases (>100GB) and are documented as a future enhancement
for teams that need PITR.

### Alternative 2: pg_dump Custom Format

**Pros:**
- Supports parallel restore
- Selective restore built-in
- Slightly smaller than SQL

**Cons:**
- Requires pg_restore tool
- Not human-readable
- Version-specific format

**Decision:** Rejected. Plain SQL provides better portability and debuggability for
the typical template use case. Custom format can be used for large databases.

### Alternative 3: Third-Party Backup Tools (Barman, pgBackRest)

**Pros:**
- Full-featured backup management
- Built-in PITR support
- Incremental backups
- Better for enterprise scale

**Cons:**
- Additional infrastructure (Barman server)
- More complex setup
- Larger dependency footprint
- Overkill for template scope

**Decision:** Rejected for template inclusion. These tools are recommended for
production deployments but add too much complexity for a starter template.

### Alternative 4: Database-as-a-Service Managed Backups

**Pros:**
- Zero configuration
- Automatic PITR
- Managed by provider

**Cons:**
- Not portable across providers
- Not available for self-hosted
- Cost implications

**Decision:** Out of scope. Template focuses on self-hosted deployments. Teams using
managed databases should use provider backup features.

## Consequences

### Positive

1. **Simple to understand:** Shell scripts with clear logic
2. **Portable:** Works across Docker, Kubernetes, VMs, bare metal
3. **Low dependencies:** Only requires PostgreSQL client tools
4. **Debuggable:** Plain SQL backups can be inspected
5. **Flexible:** Environment variables for all configuration
6. **Testable:** Easy to validate in CI/CD pipelines

### Negative

1. **No built-in PITR:** Requires additional configuration for point-in-time recovery
2. **Full backups only:** No incremental backup support
3. **Scaling limits:** pg_dump may be slow for very large databases (>100GB)
4. **Manual scheduling:** Requires external cron/scheduler setup

### Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Backup job failure | Exit codes enable monitoring; recommend alerting |
| Storage exhaustion | Retention policy auto-cleans; monitor disk space |
| Restore takes too long | Document RTO expectations; scale resources |
| Backup corruption | Checksum verification; S3 versioning |

## Implementation

### File Structure

```
scripts/
  db-backup.sh        # Main backup script
  db-restore.sh       # Main restore script
  backup-config.env.example  # Configuration template

backups/              # Default backup location
  .gitkeep

docs/
  operations/
    database-recovery.md  # Recovery procedures
```

### Interface

```bash
# Backup
./scripts/db-backup.sh                    # Daily backup
./scripts/db-backup.sh --type=weekly      # Weekly backup
./scripts/db-backup.sh --verify           # With verification
./scripts/db-backup.sh --schema-only      # Schema only

# Restore
./scripts/db-restore.sh --backup=FILE     # Restore from file
./scripts/db-restore.sh --verify-only     # Verify without restore
./scripts/db-restore.sh --drop-existing   # Replace existing database
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| BACKUP_DIR | ./backups | Backup storage directory |
| BACKUP_RETENTION_DAILY | 7 | Days to keep daily backups |
| BACKUP_RETENTION_WEEKLY | 4 | Weeks to keep weekly backups |
| BACKUP_RETENTION_MONTHLY | 12 | Months to keep monthly backups |
| BACKUP_S3_BUCKET | (none) | S3 bucket for remote storage |
| BACKUP_S3_PREFIX | backups/ | S3 prefix for backups |

## Future Enhancements

The following are documented as potential future improvements:

1. **Point-in-Time Recovery (PITR)**
   - Configure WAL archiving
   - Add pg_basebackup for base snapshots
   - Document recovery_target_time usage

2. **Incremental Backups**
   - Investigate pgBackRest for incremental support
   - Reduce storage requirements for large databases

3. **Backup Encryption**
   - Add GPG encryption for backups at rest
   - Key management documentation

4. **Parallel Backup/Restore**
   - Use pg_dump --jobs for parallel dump
   - Use custom format with pg_restore --jobs

5. **Monitoring Integration**
   - Prometheus metrics for backup status
   - Grafana dashboard for backup health

## Related Decisions

- [ADR-017: Optional Observability Stack](./017-optional-observability-stack.md) - Follows optional feature pattern
- [ADR-021: Kubernetes Deployment](./021-kubernetes-deployment.md) - CronJob scheduling

## References

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [pg_dump Manual](https://www.postgresql.org/docs/current/app-pgdump.html)
- [Continuous Archiving and PITR](https://www.postgresql.org/docs/current/continuous-archiving.html)
```

---

## Dependencies

### Upstream Dependencies

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| P3-05 | Required | Documents decisions implemented in backup scripts |

### Downstream Dependents

| Task ID | Dependency Type | Integration Point |
|---------|-----------------|-------------------|
| None | - | ADR is standalone documentation |

---

## Success Criteria

### Functional Requirements

- [ ] NFR-001: All new features shall have corresponding ADR documentation
- [ ] ADR follows established format (Status, Date, Context, Decision, etc.)
- [ ] Documents pg_dump vs pg_basebackup decision
- [ ] Documents retention policy rationale
- [ ] Documents plain-text SQL format decision
- [ ] Documents S3 integration approach
- [ ] Lists considered alternatives with pros/cons
- [ ] Includes future enhancement roadmap
- [ ] References related ADRs

### Non-Functional Requirements

- [ ] ADR is concise and well-structured
- [ ] Technical accuracy in PostgreSQL details
- [ ] Consistent with existing ADR style
- [ ] Proper markdown formatting

### Validation Steps

1. Format validation
   - Verify all ADR sections present
   - Check markdown rendering
   - Verify internal links work

2. Technical review
   - Verify PostgreSQL recommendations are accurate
   - Confirm rationale aligns with implementation

3. Cross-reference validation
   - Verify consistency with P3-05, P3-06 implementations
   - Check related ADR references

---

## Integration Points

### ADR Numbering

- Follows sequential numbering: ADR-023
- Previous: ADR-022 (Container Security Scanning)
- Next: ADR-024 (Sentry Integration)

### Related ADRs

| ADR | Relationship |
|-----|--------------|
| ADR-017 | Follows optional feature pattern |
| ADR-021 | Kubernetes deployment for CronJob scheduling |
| ADR-022 | Security scanning context |

---

## Monitoring and Observability

### No Runtime Impact

This task creates documentation only; no runtime monitoring required.

### Documentation Health

Consider periodic review of ADRs to ensure they remain accurate as implementations evolve.

---

## Infrastructure Needs

### No Infrastructure Changes Required

This task creates an ADR document only.

---

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Single document creation
- Decisions already made in P3-05
- Template structure exists from other ADRs
- Primarily documentation synthesis

---

## Implementation Notes

### ADR Writing Guidelines

1. **Context First:** Explain the problem before the solution
2. **Be Specific:** Include concrete examples and metrics
3. **Document Alternatives:** Show thoughtful consideration
4. **Acknowledge Trade-offs:** Be honest about consequences
5. **Link Related Work:** Cross-reference other ADRs and documentation

### Key Decisions to Document

| Decision | Rationale |
|----------|-----------|
| pg_dump over pg_basebackup | Cross-version compatibility, simplicity |
| Plain SQL over custom format | Portability, debuggability |
| Tiered retention | Balance storage vs recovery options |
| Local + S3 | Fast access + disaster recovery |
| External scheduler | Flexibility, separation of concerns |

### Alternatives to Cover

- pg_basebackup (physical backups)
- pg_dump custom format
- Third-party tools (Barman, pgBackRest)
- Managed database backups

---

## References

### FRD Requirements Mapping

| Requirement ID | Description | Implementation |
|----------------|-------------|----------------|
| NFR-001 | All new features shall have corresponding ADR documentation | ADR-023 |

### Related Tasks

- P3-05: Create Database Backup Scripts
- P3-06: Create Restore and Recovery Scripts
- P3-07: Create Kubernetes Backup CronJob
- P3-09: Write Point-in-Time Recovery Documentation

### External Resources

- [PostgreSQL Backup Documentation](https://www.postgresql.org/docs/current/backup.html)
- [Architecture Decision Records](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
