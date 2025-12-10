# P3-05: Create Database Backup Scripts

## Task Identifier
**ID:** P3-05
**Phase:** 3 - Operational Readiness
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| None | - | - | Independent task - can start immediately |

## Scope

### In Scope
- Create `backup.sh` script using `pg_dump` for logical backups
- Support both full and schema-only backup modes
- Implement configurable retention policy (daily, weekly, monthly)
- Add compression using gzip/pigz for storage efficiency
- Support local and S3-compatible storage destinations
- Include backup verification (checksum, test restore)
- Add logging and exit codes for monitoring integration
- Create `.env.example` entries for backup configuration

### Out of Scope
- Restore and recovery scripts (P3-06)
- Kubernetes CronJob scheduling (P3-07)
- WAL archiving and continuous archiving (PITR setup)
- Backup encryption (document as future enhancement)
- Multi-database backup coordination
- ADR documentation (P3-10)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/scripts/db-backup.sh
template/{{cookiecutter.project_slug}}/scripts/backup-config.env.example
```

### Files to Modify
```
template/{{cookiecutter.project_slug}}/.env.example  (add backup configuration)
template/{{cookiecutter.project_slug}}/compose.yml   (optional: add backup volume mount)
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/scripts/init-db.sql       (database structure reference)
template/{{cookiecutter.project_slug}}/scripts/docker-dev.sh     (script pattern reference)
template/{{cookiecutter.project_slug}}/compose.yml               (postgres service configuration)
```

## Implementation Details

### 1. Backup Script (`scripts/db-backup.sh`)

```bash
#!/bin/bash
# {{ cookiecutter.project_name }} Database Backup Script
#
# Creates PostgreSQL logical backups using pg_dump with configurable
# retention policy and storage options.
#
# Usage:
#   ./scripts/db-backup.sh                    # Full backup with defaults
#   ./scripts/db-backup.sh --type=daily       # Explicit daily backup
#   ./scripts/db-backup.sh --type=weekly      # Weekly backup (longer retention)
#   ./scripts/db-backup.sh --type=monthly     # Monthly backup (longest retention)
#   ./scripts/db-backup.sh --schema-only      # Schema-only backup
#   ./scripts/db-backup.sh --verify           # Verify backup integrity
#
# Environment Variables:
#   POSTGRES_HOST          - Database host (default: localhost)
#   POSTGRES_PORT          - Database port (default: 5432)
#   POSTGRES_DB            - Database name (default: {{ cookiecutter.postgres_db }})
#   POSTGRES_USER          - Database user (default: {{ cookiecutter.postgres_user }})
#   PGPASSWORD             - Database password (required)
#   BACKUP_DIR             - Local backup directory (default: ./backups)
#   BACKUP_RETENTION_DAILY - Days to keep daily backups (default: 7)
#   BACKUP_RETENTION_WEEKLY - Weeks to keep weekly backups (default: 4)
#   BACKUP_RETENTION_MONTHLY - Months to keep monthly backups (default: 12)
#   BACKUP_S3_BUCKET       - S3 bucket for remote storage (optional)
#   BACKUP_S3_PREFIX       - S3 prefix/folder (default: backups/)
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Configuration error
#   3 - Database connection error
#   4 - Backup creation error
#   5 - Verification error
#   6 - Upload error
#   7 - Cleanup error

set -euo pipefail

# Script metadata
readonly SCRIPT_NAME="db-backup"
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default configuration
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-{{ cookiecutter.postgres_db }}}"
POSTGRES_USER="${POSTGRES_USER:-{{ cookiecutter.postgres_user }}}"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
BACKUP_RETENTION_DAILY="${BACKUP_RETENTION_DAILY:-7}"
BACKUP_RETENTION_WEEKLY="${BACKUP_RETENTION_WEEKLY:-4}"
BACKUP_RETENTION_MONTHLY="${BACKUP_RETENTION_MONTHLY:-12}"
BACKUP_S3_BUCKET="${BACKUP_S3_BUCKET:-}"
BACKUP_S3_PREFIX="${BACKUP_S3_PREFIX:-backups/}"

# Runtime options
BACKUP_TYPE="daily"
SCHEMA_ONLY=false
VERIFY_BACKUP=false
VERBOSE=false

# Logging functions
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $*"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2
}

log_debug() {
    if [[ "${VERBOSE}" == "true" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [DEBUG] $*"
    fi
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $*"
}

# Print usage information
usage() {
    cat << EOF
Usage: ${SCRIPT_NAME} [OPTIONS]

Creates PostgreSQL database backups with configurable retention policy.

Options:
    --type=TYPE       Backup type: daily, weekly, monthly (default: daily)
    --schema-only     Create schema-only backup (no data)
    --verify          Verify backup integrity after creation
    --verbose, -v     Enable verbose output
    --help, -h        Show this help message

Environment Variables:
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, PGPASSWORD
    BACKUP_DIR, BACKUP_RETENTION_DAILY, BACKUP_RETENTION_WEEKLY, BACKUP_RETENTION_MONTHLY
    BACKUP_S3_BUCKET, BACKUP_S3_PREFIX

Examples:
    ${SCRIPT_NAME}                    # Daily backup with defaults
    ${SCRIPT_NAME} --type=weekly      # Weekly backup
    ${SCRIPT_NAME} --verify           # Backup with verification
    BACKUP_DIR=/mnt/backups ${SCRIPT_NAME}  # Custom backup directory

Exit Codes:
    0 - Success
    1 - General error
    2 - Configuration error
    3 - Database connection error
    4 - Backup creation error
    5 - Verification error
    6 - Upload error
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --type=*)
                BACKUP_TYPE="${1#*=}"
                if [[ ! "${BACKUP_TYPE}" =~ ^(daily|weekly|monthly)$ ]]; then
                    log_error "Invalid backup type: ${BACKUP_TYPE}"
                    exit 2
                fi
                ;;
            --schema-only)
                SCHEMA_ONLY=true
                ;;
            --verify)
                VERIFY_BACKUP=true
                ;;
            --verbose|-v)
                VERBOSE=true
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                exit 2
                ;;
        esac
        shift
    done
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."

    # Check required password
    if [[ -z "${PGPASSWORD:-}" ]]; then
        log_error "PGPASSWORD environment variable is required"
        exit 2
    fi

    # Create backup directory if it doesn't exist
    if [[ ! -d "${BACKUP_DIR}" ]]; then
        log_info "Creating backup directory: ${BACKUP_DIR}"
        mkdir -p "${BACKUP_DIR}"
    fi

    # Check for required tools
    if ! command -v pg_dump &> /dev/null; then
        log_error "pg_dump is required but not installed"
        exit 2
    fi

    if ! command -v gzip &> /dev/null && ! command -v pigz &> /dev/null; then
        log_error "gzip or pigz is required for compression"
        exit 2
    fi

    log_debug "Configuration validated successfully"
}

# Test database connection
test_connection() {
    log_info "Testing database connection..."

    if ! pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" &> /dev/null; then
        log_error "Cannot connect to database at ${POSTGRES_HOST}:${POSTGRES_PORT}"
        exit 3
    fi

    log_debug "Database connection successful"
}

# Generate backup filename
generate_filename() {
    local timestamp
    timestamp="$(date '+%Y%m%d_%H%M%S')"

    local suffix=""
    if [[ "${SCHEMA_ONLY}" == "true" ]]; then
        suffix="_schema"
    fi

    echo "${POSTGRES_DB}_${BACKUP_TYPE}_${timestamp}${suffix}.sql.gz"
}

# Create backup
create_backup() {
    local backup_file="$1"
    local backup_path="${BACKUP_DIR}/${backup_file}"

    log_info "Creating ${BACKUP_TYPE} backup: ${backup_file}"

    # Build pg_dump options
    local pg_dump_opts=(
        -h "${POSTGRES_HOST}"
        -p "${POSTGRES_PORT}"
        -U "${POSTGRES_USER}"
        -d "${POSTGRES_DB}"
        --no-password
        --verbose
        --format=plain
        --no-owner
        --no-privileges
    )

    if [[ "${SCHEMA_ONLY}" == "true" ]]; then
        pg_dump_opts+=(--schema-only)
    fi

    # Use pigz for parallel compression if available, otherwise gzip
    local compress_cmd="gzip"
    if command -v pigz &> /dev/null; then
        compress_cmd="pigz -p 4"
    fi

    # Execute backup with compression
    if pg_dump "${pg_dump_opts[@]}" | ${compress_cmd} > "${backup_path}"; then
        local backup_size
        backup_size="$(du -h "${backup_path}" | cut -f1)"
        log_success "Backup created: ${backup_path} (${backup_size})"

        # Generate checksum
        local checksum_file="${backup_path}.sha256"
        sha256sum "${backup_path}" > "${checksum_file}"
        log_debug "Checksum saved: ${checksum_file}"
    else
        log_error "Failed to create backup"
        rm -f "${backup_path}"
        exit 4
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_file="$1"
    local backup_path="${BACKUP_DIR}/${backup_file}"
    local checksum_file="${backup_path}.sha256"

    log_info "Verifying backup integrity..."

    # Verify checksum
    if [[ -f "${checksum_file}" ]]; then
        if sha256sum -c "${checksum_file}" &> /dev/null; then
            log_debug "Checksum verification passed"
        else
            log_error "Checksum verification failed"
            exit 5
        fi
    fi

    # Test decompression (read first 1000 lines)
    if ! zcat "${backup_path}" | head -1000 > /dev/null 2>&1; then
        log_error "Backup file appears to be corrupted"
        exit 5
    fi

    # Verify SQL structure
    local first_line
    first_line="$(zcat "${backup_path}" | head -1)"
    if [[ ! "${first_line}" =~ ^--.*PostgreSQL ]]; then
        log_error "Backup does not appear to be valid PostgreSQL dump"
        exit 5
    fi

    log_success "Backup verification passed"
}

# Upload to S3 (optional)
upload_to_s3() {
    local backup_file="$1"
    local backup_path="${BACKUP_DIR}/${backup_file}"

    if [[ -z "${BACKUP_S3_BUCKET}" ]]; then
        log_debug "S3 upload skipped (BACKUP_S3_BUCKET not configured)"
        return 0
    fi

    log_info "Uploading backup to S3..."

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is required for S3 upload but not installed"
        exit 6
    fi

    local s3_path="s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}${BACKUP_TYPE}/${backup_file}"
    local checksum_file="${backup_path}.sha256"

    if aws s3 cp "${backup_path}" "${s3_path}" --quiet; then
        log_success "Uploaded to ${s3_path}"

        # Also upload checksum
        if [[ -f "${checksum_file}" ]]; then
            aws s3 cp "${checksum_file}" "${s3_path}.sha256" --quiet
        fi
    else
        log_error "Failed to upload backup to S3"
        exit 6
    fi
}

# Cleanup old backups based on retention policy
cleanup_old_backups() {
    log_info "Cleaning up old backups..."

    local retention_days
    case "${BACKUP_TYPE}" in
        daily)
            retention_days="${BACKUP_RETENTION_DAILY}"
            ;;
        weekly)
            retention_days=$((BACKUP_RETENTION_WEEKLY * 7))
            ;;
        monthly)
            retention_days=$((BACKUP_RETENTION_MONTHLY * 30))
            ;;
    esac

    local pattern="${POSTGRES_DB}_${BACKUP_TYPE}_*.sql.gz"
    local count=0

    # Find and remove old backups
    while IFS= read -r -d '' file; do
        if [[ -f "${file}" ]]; then
            rm -f "${file}" "${file}.sha256"
            ((count++))
            log_debug "Removed: ${file}"
        fi
    done < <(find "${BACKUP_DIR}" -name "${pattern}" -type f -mtime "+${retention_days}" -print0 2>/dev/null)

    if [[ ${count} -gt 0 ]]; then
        log_info "Removed ${count} old backup(s) older than ${retention_days} days"
    else
        log_debug "No old backups to remove"
    fi

    # Cleanup S3 old backups (if configured)
    if [[ -n "${BACKUP_S3_BUCKET}" ]] && command -v aws &> /dev/null; then
        local s3_prefix="s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}${BACKUP_TYPE}/"
        local cutoff_date
        cutoff_date="$(date -d "-${retention_days} days" '+%Y-%m-%d')"

        log_debug "S3 cleanup: removing files older than ${cutoff_date}"
        # Note: S3 lifecycle policies are recommended for production
    fi
}

# Main execution
main() {
    parse_args "$@"

    log_info "Starting {{ cookiecutter.project_name }} database backup"
    log_info "Database: ${POSTGRES_DB}@${POSTGRES_HOST}:${POSTGRES_PORT}"
    log_info "Backup type: ${BACKUP_TYPE}"

    validate_config
    test_connection

    local backup_file
    backup_file="$(generate_filename)"

    create_backup "${backup_file}"

    if [[ "${VERIFY_BACKUP}" == "true" ]]; then
        verify_backup "${backup_file}"
    fi

    upload_to_s3 "${backup_file}"
    cleanup_old_backups

    log_success "Backup completed successfully: ${backup_file}"
    exit 0
}

main "$@"
```

### 2. Backup Configuration Example (`scripts/backup-config.env.example`)

```bash
# {{ cookiecutter.project_name }} Backup Configuration
# Copy to backup-config.env and customize

# Database Connection
# These are typically inherited from .env but can be overridden
POSTGRES_HOST=localhost
POSTGRES_PORT={{ cookiecutter.postgres_port }}
POSTGRES_DB={{ cookiecutter.postgres_db }}
POSTGRES_USER={{ cookiecutter.postgres_user }}
# PGPASSWORD should be set securely (not in this file for production)

# Backup Storage
BACKUP_DIR=./backups

# Retention Policy
# Daily backups kept for 7 days
BACKUP_RETENTION_DAILY=7
# Weekly backups kept for 4 weeks
BACKUP_RETENTION_WEEKLY=4
# Monthly backups kept for 12 months
BACKUP_RETENTION_MONTHLY=12

# S3 Remote Storage (optional)
# Uncomment and configure for cloud backup storage
# BACKUP_S3_BUCKET=your-bucket-name
# BACKUP_S3_PREFIX=backups/{{ cookiecutter.project_slug }}/
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-access-key
# AWS_SECRET_ACCESS_KEY=your-secret-key
```

### 3. Environment File Updates (`.env.example`)

Add to existing `.env.example`:

```bash
# ===========================================
# Database Backup Configuration
# ===========================================

# Local backup directory (relative to project root)
BACKUP_DIR=./backups

# Retention policy (number of backups to keep)
BACKUP_RETENTION_DAILY=7
BACKUP_RETENTION_WEEKLY=4
BACKUP_RETENTION_MONTHLY=12

# S3 remote storage (optional - for production)
# BACKUP_S3_BUCKET=
# BACKUP_S3_PREFIX=backups/
```

### 4. Docker Integration (compose.yml)

Add backup volume mount to postgres service (optional, for container-based backups):

```yaml
services:
  postgres:
    # ... existing configuration ...
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql:ro
      - ./backups:/backups  # Add for container-based backup access
```

## Success Criteria

### Functional Requirements
- [ ] FR-OPS-011: Database backup script using pg_dump shall be included
- [ ] FR-OPS-012: Backup script shall support configurable retention policy
- [ ] Backup script exits with appropriate codes for monitoring integration
- [ ] Backup verification validates file integrity and SQL structure

### Verification Steps
1. **Basic Backup:**
   ```bash
   # Set password and run backup
   export PGPASSWORD=your_password
   ./scripts/db-backup.sh

   # Verify backup was created
   ls -la backups/
   # Expected: {{ cookiecutter.postgres_db }}_daily_YYYYMMDD_HHMMSS.sql.gz
   ```

2. **Different Backup Types:**
   ```bash
   ./scripts/db-backup.sh --type=weekly
   ./scripts/db-backup.sh --type=monthly

   # Verify files created with correct naming
   ls backups/*weekly* backups/*monthly*
   ```

3. **Schema-Only Backup:**
   ```bash
   ./scripts/db-backup.sh --schema-only --verify

   # Verify schema backup is smaller than full backup
   ls -la backups/*schema*
   ```

4. **Retention Cleanup:**
   ```bash
   # Create old test files
   touch -d "10 days ago" backups/test_daily_old.sql.gz

   # Run cleanup
   BACKUP_RETENTION_DAILY=7 ./scripts/db-backup.sh

   # Verify old file was removed
   ls backups/test_daily_old.sql.gz 2>/dev/null || echo "Old backup cleaned up"
   ```

5. **Exit Code Verification:**
   ```bash
   # Test connection failure
   POSTGRES_HOST=invalid-host ./scripts/db-backup.sh
   echo "Exit code: $?"  # Expected: 3

   # Test missing password
   unset PGPASSWORD && ./scripts/db-backup.sh
   echo "Exit code: $?"  # Expected: 2
   ```

### Quality Gates
- [ ] Script runs successfully in Docker container
- [ ] Script runs successfully from host machine
- [ ] All exit codes properly indicate failure types
- [ ] Backup file can be restored (verified by P3-06)
- [ ] Compression reduces backup size by >50%

## Integration Points

### Upstream Dependencies
None - this task is independent.

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P3-06 | Backup file format and location | Restore script reads backups created by this script |
| P3-07 | Script interface and exit codes | Kubernetes CronJob executes this script |
| P3-09 | Script usage documentation | Recovery docs reference backup procedures |
| P3-10 | ADR-023 documents backup strategy | References this implementation |

### Integration Contract
```bash
# Contract: db-backup.sh interface

# Input: Environment variables
# - PGPASSWORD (required)
# - POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER
# - BACKUP_DIR, BACKUP_RETENTION_*, BACKUP_S3_*

# Output: Backup files
# - Location: ${BACKUP_DIR}/${POSTGRES_DB}_${type}_${timestamp}.sql.gz
# - Checksum: ${backup_file}.sha256
# - Format: gzip-compressed pg_dump plain-text SQL

# Exit codes:
# 0=success, 2=config error, 3=connection error, 4=backup error, 5=verify error, 6=upload error
```

## Monitoring and Observability

### Prometheus Metrics (via textfile collector)
The backup script can optionally write metrics for Prometheus:

```bash
# At end of backup script, write metrics
cat > /var/lib/prometheus/textfile/backup.prom << EOF
# HELP backup_last_success_timestamp Unix timestamp of last successful backup
# TYPE backup_last_success_timestamp gauge
backup_last_success_timestamp{database="${POSTGRES_DB}",type="${BACKUP_TYPE}"} $(date +%s)

# HELP backup_size_bytes Size of last backup in bytes
# TYPE backup_size_bytes gauge
backup_size_bytes{database="${POSTGRES_DB}",type="${BACKUP_TYPE}"} $(stat -c%s "${backup_path}")

# HELP backup_duration_seconds Duration of backup operation in seconds
# TYPE backup_duration_seconds gauge
backup_duration_seconds{database="${POSTGRES_DB}",type="${BACKUP_TYPE}"} ${SECONDS}
EOF
```

### Alerting Integration
Backup failures should trigger alerts. The exit codes enable:
- Monitoring tools (Datadog, New Relic) to detect non-zero exits
- Prometheus Alertmanager rules based on backup metrics
- Simple cron-based email notifications

### Logging
All output is timestamped and prefixed with log level:
- `[INFO]` - Normal operations
- `[ERROR]` - Failures (written to stderr)
- `[DEBUG]` - Verbose mode details
- `[SUCCESS]` - Successful completions

## Infrastructure Needs

### Local Requirements
- `pg_dump` (PostgreSQL client tools)
- `gzip` or `pigz` (compression)
- `sha256sum` (verification)
- Sufficient disk space in BACKUP_DIR

### Container Requirements
For running backup from within Docker:
```bash
docker compose exec postgres pg_dump -U {{ cookiecutter.postgres_user }} {{ cookiecutter.postgres_db }} | gzip > backup.sql.gz
```

### S3 Requirements (Optional)
- AWS CLI configured
- IAM credentials with s3:PutObject permission
- S3 bucket created with appropriate lifecycle policies

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Bash scripting with multiple features (retention, S3, verification)
- Integration with existing Docker setup
- Comprehensive error handling and exit codes
- Testing across different scenarios

## Notes

### Design Decisions

**1. pg_dump over pg_basebackup:**
Logical backups (pg_dump) are chosen for:
- Cross-version compatibility
- Selective restore capability
- Human-readable SQL format
- Smaller size for typical application databases

**2. Plain-text SQL format:**
Custom format could be used for parallel restore, but plain SQL:
- Works without psql custom format support
- Easier to inspect and debug
- Can be grepped for specific objects

**3. Retention by backup type:**
Different retention periods allow efficient storage:
- Daily: Short-term recovery (7 days)
- Weekly: Point-in-time recovery (4 weeks)
- Monthly: Compliance and long-term (12 months)

### Future Enhancements
- WAL archiving for true point-in-time recovery
- Backup encryption at rest
- Parallel backup using pg_dump --jobs
- Incremental backup support
- Backup to multiple destinations

### Related Requirements
- FR-OPS-011: Database backup script using pg_dump shall be included
- FR-OPS-012: Backup script shall support configurable retention policy
- US-3.3: Automated database backups for data loss recovery

### Security Considerations
- PGPASSWORD should be passed via environment, not command line
- Backup files may contain sensitive data - secure storage location
- S3 credentials should use IAM roles in production, not access keys
- Consider encryption for backups containing PII
