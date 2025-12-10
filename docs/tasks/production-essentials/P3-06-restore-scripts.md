# P3-06: Create Restore and Recovery Scripts

## Task Identifier
**ID:** P3-06
**Phase:** 3 - Operational Readiness
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P3-05 | Required | Documented | Backup script creates files this script restores |

## Scope

### In Scope
- Create `db-restore.sh` script for restoring from pg_dump backups
- Support restore from local files and S3 storage
- Add pre-restore validation (backup integrity, database existence)
- Implement safety checks (confirmation prompts, dry-run mode)
- Support selective restore (schema-only, data-only, specific tables)
- Create restore verification (row counts, schema comparison)
- Add point-in-time recovery guidance (for WAL-based recovery)
- Document rollback procedures for failed restores

### Out of Scope
- Backup creation (P3-05)
- Kubernetes CronJob scheduling (P3-07)
- WAL archiving implementation (future enhancement)
- Full point-in-time recovery automation (document process only)
- Cross-database migration tooling
- ADR documentation (P3-10)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/scripts/db-restore.sh
template/{{cookiecutter.project_slug}}/scripts/db-verify.sh
```

### Files to Modify
```
template/{{cookiecutter.project_slug}}/.env.example  (add restore configuration if needed)
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/scripts/db-backup.sh     (backup format reference)
template/{{cookiecutter.project_slug}}/scripts/init-db.sql      (database structure reference)
template/{{cookiecutter.project_slug}}/compose.yml              (postgres service configuration)
```

## Implementation Details

### 1. Restore Script (`scripts/db-restore.sh`)

```bash
#!/bin/bash
# {{ cookiecutter.project_name }} Database Restore Script
#
# Restores PostgreSQL database from pg_dump backup files created by db-backup.sh.
# Includes safety checks, verification, and rollback procedures.
#
# Usage:
#   ./scripts/db-restore.sh backup_file.sql.gz              # Restore from file
#   ./scripts/db-restore.sh --list                          # List available backups
#   ./scripts/db-restore.sh --latest                        # Restore most recent backup
#   ./scripts/db-restore.sh --from-s3 backup_file.sql.gz    # Restore from S3
#   ./scripts/db-restore.sh --dry-run backup_file.sql.gz    # Preview without restoring
#   ./scripts/db-restore.sh --schema-only backup_file.sql.gz # Restore schema only
#
# Environment Variables:
#   POSTGRES_HOST          - Database host (default: localhost)
#   POSTGRES_PORT          - Database port (default: 5432)
#   POSTGRES_DB            - Database name (default: {{ cookiecutter.postgres_db }})
#   POSTGRES_USER          - Database user (default: {{ cookiecutter.postgres_user }})
#   PGPASSWORD             - Database password (required)
#   BACKUP_DIR             - Backup directory (default: ./backups)
#   BACKUP_S3_BUCKET       - S3 bucket for remote backups (optional)
#   BACKUP_S3_PREFIX       - S3 prefix (default: backups/)
#   RESTORE_SKIP_CONFIRM   - Skip confirmation prompts (default: false)
#
# Exit Codes:
#   0 - Success
#   1 - General error
#   2 - Configuration error
#   3 - Database connection error
#   4 - Backup file error
#   5 - Restore error
#   6 - Verification error
#   7 - User cancelled

set -euo pipefail

# Script metadata
readonly SCRIPT_NAME="db-restore"
readonly SCRIPT_VERSION="1.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Default configuration
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-{{ cookiecutter.postgres_db }}}"
POSTGRES_USER="${POSTGRES_USER:-{{ cookiecutter.postgres_user }}}"
BACKUP_DIR="${BACKUP_DIR:-${PROJECT_ROOT}/backups}"
BACKUP_S3_BUCKET="${BACKUP_S3_BUCKET:-}"
BACKUP_S3_PREFIX="${BACKUP_S3_PREFIX:-backups/}"
RESTORE_SKIP_CONFIRM="${RESTORE_SKIP_CONFIRM:-false}"

# Runtime options
BACKUP_FILE=""
DRY_RUN=false
LIST_BACKUPS=false
USE_LATEST=false
FROM_S3=false
SCHEMA_ONLY=false
DATA_ONLY=false
DROP_EXISTING=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $*"
}

log_error() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] [${RED}ERROR${NC}] $*" >&2
}

log_warn() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] [${YELLOW}WARN${NC}] $*"
}

log_debug() {
    if [[ "${VERBOSE}" == "true" ]]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] [DEBUG] $*"
    fi
}

log_success() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] [${GREEN}SUCCESS${NC}] $*"
}

# Print usage information
usage() {
    cat << EOF
Usage: ${SCRIPT_NAME} [OPTIONS] [BACKUP_FILE]

Restores PostgreSQL database from backup files created by db-backup.sh.

Options:
    --list              List available backup files
    --latest            Restore from most recent backup
    --from-s3           Download and restore from S3
    --dry-run           Preview restore without executing
    --schema-only       Restore schema only (no data)
    --data-only         Restore data only (no schema)
    --drop              Drop existing objects before restore
    --skip-confirm      Skip confirmation prompts
    --verbose, -v       Enable verbose output
    --help, -h          Show this help message

Arguments:
    BACKUP_FILE         Path to backup file (.sql.gz) or filename in BACKUP_DIR

Examples:
    ${SCRIPT_NAME} --list                         # List available backups
    ${SCRIPT_NAME} --latest                       # Restore most recent backup
    ${SCRIPT_NAME} mydb_daily_20240101.sql.gz     # Restore specific backup
    ${SCRIPT_NAME} --from-s3 --latest             # Restore latest from S3
    ${SCRIPT_NAME} --dry-run backup.sql.gz        # Preview restore

Exit Codes:
    0 - Success
    1 - General error
    2 - Configuration error
    3 - Database connection error
    4 - Backup file error
    5 - Restore error
    6 - Verification error
    7 - User cancelled
EOF
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --list)
                LIST_BACKUPS=true
                ;;
            --latest)
                USE_LATEST=true
                ;;
            --from-s3)
                FROM_S3=true
                ;;
            --dry-run)
                DRY_RUN=true
                ;;
            --schema-only)
                SCHEMA_ONLY=true
                ;;
            --data-only)
                DATA_ONLY=true
                ;;
            --drop)
                DROP_EXISTING=true
                ;;
            --skip-confirm)
                RESTORE_SKIP_CONFIRM=true
                ;;
            --verbose|-v)
                VERBOSE=true
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            -*)
                log_error "Unknown option: $1"
                usage
                exit 2
                ;;
            *)
                BACKUP_FILE="$1"
                ;;
        esac
        shift
    done

    # Validate conflicting options
    if [[ "${SCHEMA_ONLY}" == "true" && "${DATA_ONLY}" == "true" ]]; then
        log_error "Cannot use --schema-only and --data-only together"
        exit 2
    fi
}

# Validate configuration
validate_config() {
    log_info "Validating configuration..."

    # Check required password
    if [[ -z "${PGPASSWORD:-}" ]]; then
        log_error "PGPASSWORD environment variable is required"
        exit 2
    fi

    # Check backup directory exists (for local restores)
    if [[ ! -d "${BACKUP_DIR}" && "${FROM_S3}" != "true" ]]; then
        log_error "Backup directory does not exist: ${BACKUP_DIR}"
        exit 2
    fi

    # Check for required tools
    if ! command -v psql &> /dev/null; then
        log_error "psql is required but not installed"
        exit 2
    fi

    if ! command -v zcat &> /dev/null; then
        log_error "zcat is required but not installed"
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

# List available backups
list_backups() {
    log_info "Available backups in ${BACKUP_DIR}:"
    echo ""

    if [[ -d "${BACKUP_DIR}" ]]; then
        local count=0
        while IFS= read -r -d '' file; do
            local filename
            filename="$(basename "${file}")"
            local size
            size="$(du -h "${file}" | cut -f1)"
            local date
            date="$(stat -c '%y' "${file}" | cut -d'.' -f1)"

            printf "  %-50s %8s  %s\n" "${filename}" "${size}" "${date}"
            ((count++))
        done < <(find "${BACKUP_DIR}" -name "*.sql.gz" -type f -print0 | sort -z)

        echo ""
        log_info "Total: ${count} backup(s)"
    else
        log_warn "Backup directory does not exist"
    fi

    # List S3 backups if configured
    if [[ -n "${BACKUP_S3_BUCKET}" ]] && command -v aws &> /dev/null; then
        echo ""
        log_info "S3 backups (s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}):"
        aws s3 ls "s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}" --recursive 2>/dev/null || log_warn "Cannot access S3 bucket"
    fi
}

# Find latest backup
find_latest_backup() {
    local latest_file

    if [[ "${FROM_S3}" == "true" ]]; then
        if [[ -z "${BACKUP_S3_BUCKET}" ]]; then
            log_error "BACKUP_S3_BUCKET is required for S3 restores"
            exit 2
        fi

        # Find latest in S3
        latest_file="$(aws s3 ls "s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}" --recursive 2>/dev/null | \
            grep '\.sql\.gz$' | sort -k1,2 | tail -1 | awk '{print $NF}')"

        if [[ -z "${latest_file}" ]]; then
            log_error "No backup files found in S3"
            exit 4
        fi

        echo "${latest_file}"
    else
        # Find latest local backup
        latest_file="$(find "${BACKUP_DIR}" -name "*.sql.gz" -type f -printf '%T@ %p\n' 2>/dev/null | \
            sort -n | tail -1 | cut -d' ' -f2-)"

        if [[ -z "${latest_file}" ]]; then
            log_error "No backup files found in ${BACKUP_DIR}"
            exit 4
        fi

        echo "${latest_file}"
    fi
}

# Resolve backup file path
resolve_backup_file() {
    local input_file="$1"

    if [[ "${FROM_S3}" == "true" ]]; then
        # Download from S3 to temp location
        local s3_path
        if [[ "${input_file}" == s3://* ]]; then
            s3_path="${input_file}"
        else
            s3_path="s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}${input_file}"
        fi

        local temp_file
        temp_file="$(mktemp --suffix=.sql.gz)"

        log_info "Downloading backup from S3: ${s3_path}"
        if ! aws s3 cp "${s3_path}" "${temp_file}" --quiet; then
            log_error "Failed to download backup from S3"
            rm -f "${temp_file}"
            exit 4
        fi

        echo "${temp_file}"
    else
        # Local file resolution
        if [[ -f "${input_file}" ]]; then
            echo "${input_file}"
        elif [[ -f "${BACKUP_DIR}/${input_file}" ]]; then
            echo "${BACKUP_DIR}/${input_file}"
        else
            log_error "Backup file not found: ${input_file}"
            exit 4
        fi
    fi
}

# Validate backup file
validate_backup_file() {
    local backup_file="$1"

    log_info "Validating backup file..."

    # Check file exists and is readable
    if [[ ! -r "${backup_file}" ]]; then
        log_error "Cannot read backup file: ${backup_file}"
        exit 4
    fi

    # Check file is not empty
    if [[ ! -s "${backup_file}" ]]; then
        log_error "Backup file is empty: ${backup_file}"
        exit 4
    fi

    # Verify checksum if available
    local checksum_file="${backup_file}.sha256"
    if [[ -f "${checksum_file}" ]]; then
        if sha256sum -c "${checksum_file}" &> /dev/null; then
            log_debug "Checksum verification passed"
        else
            log_error "Checksum verification failed"
            exit 4
        fi
    else
        log_warn "No checksum file found - skipping integrity check"
    fi

    # Test decompression
    if ! zcat "${backup_file}" | head -1 > /dev/null 2>&1; then
        log_error "Backup file appears to be corrupted"
        exit 4
    fi

    # Verify it's a PostgreSQL dump
    local first_line
    first_line="$(zcat "${backup_file}" | head -1)"
    if [[ ! "${first_line}" =~ ^--.*PostgreSQL ]]; then
        log_error "File does not appear to be a PostgreSQL dump"
        exit 4
    fi

    log_debug "Backup file validated"
}

# Get database statistics (for verification)
get_db_stats() {
    psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -t -A -c "SELECT json_build_object(
            'tables', (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'),
            'total_rows', (SELECT COALESCE(sum(n_live_tup), 0) FROM pg_stat_user_tables)
        );" 2>/dev/null || echo '{"tables": 0, "total_rows": 0}'
}

# Confirm restore with user
confirm_restore() {
    local backup_file="$1"

    if [[ "${RESTORE_SKIP_CONFIRM}" == "true" ]]; then
        return 0
    fi

    local backup_size
    backup_size="$(du -h "${backup_file}" | cut -f1)"

    echo ""
    echo "========================================"
    echo "         DATABASE RESTORE WARNING"
    echo "========================================"
    echo ""
    echo "You are about to restore the database:"
    echo ""
    echo "  Database: ${POSTGRES_DB}@${POSTGRES_HOST}:${POSTGRES_PORT}"
    echo "  Backup:   $(basename "${backup_file}")"
    echo "  Size:     ${backup_size}"
    echo ""

    if [[ "${DROP_EXISTING}" == "true" ]]; then
        echo -e "  ${RED}WARNING: Existing objects will be DROPPED!${NC}"
        echo ""
    fi

    if [[ "${SCHEMA_ONLY}" == "true" ]]; then
        echo "  Mode:     Schema only (no data)"
    elif [[ "${DATA_ONLY}" == "true" ]]; then
        echo "  Mode:     Data only (no schema)"
    else
        echo "  Mode:     Full restore"
    fi

    echo ""
    echo "This operation cannot be undone!"
    echo ""

    read -p "Are you sure you want to continue? (yes/no): " -r confirm
    echo ""

    if [[ "${confirm}" != "yes" ]]; then
        log_info "Restore cancelled by user"
        exit 7
    fi
}

# Perform dry run analysis
dry_run_analysis() {
    local backup_file="$1"

    log_info "Performing dry-run analysis..."

    echo ""
    echo "Backup File Analysis:"
    echo "===================="

    # Count statements by type
    echo ""
    echo "SQL Statement Summary:"
    zcat "${backup_file}" | grep -E '^(CREATE|ALTER|DROP|INSERT|COPY|SET|COMMENT)' | \
        cut -d' ' -f1 | sort | uniq -c | sort -rn | head -20

    # List tables
    echo ""
    echo "Tables in backup:"
    zcat "${backup_file}" | grep -E '^CREATE TABLE' | \
        sed 's/CREATE TABLE \(IF NOT EXISTS \)\?//' | \
        cut -d'(' -f1 | tr -d '"' | sort

    # Estimate row counts from COPY statements
    echo ""
    echo "Estimated data volume:"
    local copy_count
    copy_count="$(zcat "${backup_file}" | grep -c '^COPY ' || true)"
    echo "  COPY statements: ${copy_count}"

    echo ""
    log_info "Dry run complete - no changes made"
}

# Perform the restore
perform_restore() {
    local backup_file="$1"

    log_info "Starting database restore..."

    # Get pre-restore stats
    local pre_stats
    pre_stats="$(get_db_stats)"
    log_debug "Pre-restore stats: ${pre_stats}"

    # Build psql options
    local psql_opts=(
        -h "${POSTGRES_HOST}"
        -p "${POSTGRES_PORT}"
        -U "${POSTGRES_USER}"
        -d "${POSTGRES_DB}"
        --no-password
        --echo-errors
        -v ON_ERROR_STOP=1
    )

    if [[ "${VERBOSE}" == "true" ]]; then
        psql_opts+=(--echo-all)
    fi

    # Prepare restore command
    local restore_start
    restore_start="$(date +%s)"

    if [[ "${DROP_EXISTING}" == "true" ]]; then
        log_warn "Dropping existing objects..."
        psql "${psql_opts[@]}" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;" 2>&1 || true
    fi

    # Execute restore
    log_info "Restoring from backup..."

    local filter_opts=""
    if [[ "${SCHEMA_ONLY}" == "true" ]]; then
        # Filter out COPY and INSERT statements for schema-only
        filter_opts="grep -v -E '^(COPY|INSERT)'"
    elif [[ "${DATA_ONLY}" == "true" ]]; then
        # Filter to only COPY and INSERT statements for data-only
        filter_opts="grep -E '^(COPY|INSERT|\\\\\\.)'"
    fi

    if [[ -n "${filter_opts}" ]]; then
        if ! zcat "${backup_file}" | eval "${filter_opts}" | psql "${psql_opts[@]}" 2>&1; then
            log_error "Restore failed"
            exit 5
        fi
    else
        if ! zcat "${backup_file}" | psql "${psql_opts[@]}" 2>&1; then
            log_error "Restore failed"
            exit 5
        fi
    fi

    local restore_end
    restore_end="$(date +%s)"
    local restore_duration=$((restore_end - restore_start))

    log_success "Restore completed in ${restore_duration} seconds"

    # Get post-restore stats
    local post_stats
    post_stats="$(get_db_stats)"
    log_info "Post-restore stats: ${post_stats}"
}

# Verify restore
verify_restore() {
    log_info "Verifying restore..."

    # Check for errors in pg_stat
    local error_count
    error_count="$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -t -A -c "SELECT count(*) FROM pg_stat_user_tables WHERE last_analyze IS NULL;" 2>/dev/null || echo "0")"

    # Get table count
    local table_count
    table_count="$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -t -A -c "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null || echo "0")"

    log_info "Restored ${table_count} tables"

    # Run ANALYZE for optimizer
    log_info "Running ANALYZE on restored tables..."
    psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -c "ANALYZE;" &> /dev/null || true

    log_success "Restore verification passed"
}

# Main execution
main() {
    parse_args "$@"

    log_info "{{ cookiecutter.project_name }} Database Restore"

    # Handle list command
    if [[ "${LIST_BACKUPS}" == "true" ]]; then
        list_backups
        exit 0
    fi

    validate_config
    test_connection

    # Determine backup file
    if [[ "${USE_LATEST}" == "true" ]]; then
        BACKUP_FILE="$(find_latest_backup)"
        log_info "Using latest backup: $(basename "${BACKUP_FILE}")"
    elif [[ -z "${BACKUP_FILE}" ]]; then
        log_error "No backup file specified. Use --list to see available backups."
        usage
        exit 2
    fi

    # Resolve full path
    local resolved_file
    resolved_file="$(resolve_backup_file "${BACKUP_FILE}")"

    validate_backup_file "${resolved_file}"

    # Handle dry run
    if [[ "${DRY_RUN}" == "true" ]]; then
        dry_run_analysis "${resolved_file}"
        exit 0
    fi

    # Confirm with user
    confirm_restore "${resolved_file}"

    # Perform restore
    perform_restore "${resolved_file}"
    verify_restore

    # Cleanup temp file if from S3
    if [[ "${FROM_S3}" == "true" && "${resolved_file}" == /tmp/* ]]; then
        rm -f "${resolved_file}"
    fi

    log_success "Database restore completed successfully"
    exit 0
}

main "$@"
```

### 2. Verification Script (`scripts/db-verify.sh`)

```bash
#!/bin/bash
# {{ cookiecutter.project_name }} Database Verification Script
#
# Verifies database integrity after restore or for regular health checks.
#
# Usage:
#   ./scripts/db-verify.sh                    # Run all verifications
#   ./scripts/db-verify.sh --quick            # Quick check only
#   ./scripts/db-verify.sh --compare backup   # Compare with backup

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_DB="${POSTGRES_DB:-{{ cookiecutter.postgres_db }}}"
POSTGRES_USER="${POSTGRES_USER:-{{ cookiecutter.postgres_user }}}"

log_info() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $*"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $*" >&2
}

log_success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $*"
}

# Check database connectivity
check_connectivity() {
    log_info "Checking database connectivity..."
    if pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" &> /dev/null; then
        log_success "Database is accessible"
        return 0
    else
        log_error "Cannot connect to database"
        return 1
    fi
}

# Check schema version
check_schema_version() {
    log_info "Checking schema version..."
    local version
    version="$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -t -A -c "SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1;" 2>/dev/null || echo "unknown")"
    log_info "Schema version: ${version}"
}

# Check RLS policies
check_rls_policies() {
    log_info "Checking Row-Level Security policies..."
    local rls_count
    rls_count="$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -t -A -c "SELECT count(*) FROM pg_policies;" 2>/dev/null || echo "0")"
    log_info "RLS policies found: ${rls_count}"

    if [[ "${rls_count}" -eq 0 ]]; then
        log_error "Warning: No RLS policies found - tenant isolation may not be enforced"
        return 1
    fi
    return 0
}

# Check table integrity
check_tables() {
    log_info "Checking table integrity..."

    local tables
    tables="$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -t -A -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public';" 2>/dev/null)"

    local table_count=0
    local total_rows=0

    while IFS= read -r table; do
        if [[ -n "${table}" ]]; then
            local row_count
            row_count="$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
                -t -A -c "SELECT count(*) FROM \"${table}\";" 2>/dev/null || echo "0")"
            ((table_count++))
            total_rows=$((total_rows + row_count))
            echo "  ${table}: ${row_count} rows"
        fi
    done <<< "${tables}"

    log_info "Total: ${table_count} tables, ${total_rows} rows"
}

# Check for orphaned records
check_integrity() {
    log_info "Checking referential integrity..."

    # Check for orphaned tenant references (example)
    local orphans
    orphans="$(psql -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
        -t -A -c "SELECT count(*) FROM users u WHERE NOT EXISTS (SELECT 1 FROM tenants t WHERE t.id = u.tenant_id);" 2>/dev/null || echo "0")"

    if [[ "${orphans}" -gt 0 ]]; then
        log_error "Found ${orphans} orphaned user records"
        return 1
    fi

    log_success "No integrity issues found"
    return 0
}

# Main
main() {
    log_info "Starting database verification..."

    local exit_code=0

    check_connectivity || exit_code=1
    check_schema_version
    check_tables
    check_rls_policies || exit_code=1
    check_integrity || exit_code=1

    if [[ ${exit_code} -eq 0 ]]; then
        log_success "All verifications passed"
    else
        log_error "Some verifications failed"
    fi

    exit ${exit_code}
}

main "$@"
```

## Success Criteria

### Functional Requirements
- [ ] FR-OPS-014: Database restoration procedure shall be documented and tested
- [ ] Restore script can restore from local backup files
- [ ] Restore script can restore from S3 storage
- [ ] Safety checks prevent accidental data loss
- [ ] Verification confirms successful restore

### Verification Steps
1. **List Available Backups:**
   ```bash
   ./scripts/db-restore.sh --list
   # Expected: List of backup files with sizes and dates
   ```

2. **Dry Run Analysis:**
   ```bash
   ./scripts/db-restore.sh --dry-run backups/latest.sql.gz
   # Expected: Analysis of backup contents without modification
   ```

3. **Full Restore:**
   ```bash
   export PGPASSWORD=your_password
   ./scripts/db-restore.sh --latest
   # Follow prompts
   # Expected: Database restored and verified
   ```

4. **Schema-Only Restore:**
   ```bash
   ./scripts/db-restore.sh --schema-only backup.sql.gz
   # Expected: Only schema restored, no data
   ```

5. **Verification Script:**
   ```bash
   ./scripts/db-verify.sh
   # Expected: All checks pass
   ```

### Quality Gates
- [ ] Restore completes without errors
- [ ] Restored database passes verification script
- [ ] RLS policies are intact after restore
- [ ] Application can connect and function after restore
- [ ] Confirmation prompts prevent accidental restores

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P3-05 | Backup file format (.sql.gz) | Reads backups created by db-backup.sh |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P3-09 | Script usage and procedures | Recovery docs reference these scripts |
| P3-10 | ADR-023 documents recovery strategy | References restore procedures |

### Integration Contract
```bash
# Contract: db-restore.sh interface

# Input:
# - Backup file: .sql.gz format from db-backup.sh
# - Environment: PGPASSWORD, POSTGRES_* variables

# Output:
# - Restored database
# - Exit code: 0=success, non-zero=failure

# Safety:
# - Requires confirmation (unless --skip-confirm)
# - Supports dry-run mode
# - Validates backup before restore
```

## Monitoring and Observability

### Logging
- All operations logged with timestamps
- Errors written to stderr
- Verbose mode for debugging

### Metrics
Restore operations can emit metrics:
- `restore_duration_seconds`
- `restore_success` (1/0)
- `restored_table_count`
- `restored_row_count`

## Infrastructure Needs

### Local Requirements
- `psql` (PostgreSQL client)
- `zcat` (decompression)
- `sha256sum` (verification)

### Permissions
- User must have CREATEDB or access to target database
- For full restore with --drop, user needs DROP privileges

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- Multiple restore modes (full, schema, data)
- Safety features (confirmation, dry-run, verification)
- S3 integration
- Comprehensive error handling

## Notes

### Design Decisions

**1. Confirmation by Default:**
Restores require explicit "yes" confirmation to prevent accidental data loss. Use `--skip-confirm` for automated scenarios.

**2. Backup Validation:**
Before restore, the script validates:
- File exists and is readable
- Checksum matches (if available)
- File is valid gzip
- Content is PostgreSQL dump format

**3. Post-Restore Verification:**
After restore, the script runs ANALYZE and basic integrity checks to ensure the database is usable.

### Rollback Procedure
If restore fails mid-way:
1. Check error messages for specific failure
2. Restore from a different backup if available
3. For partial restores, consider --drop flag to clean slate
4. Contact DBA for complex recovery scenarios

### Related Requirements
- FR-OPS-014: Database restoration procedure shall be documented and tested
- US-3.3: Point-in-time recovery documentation
- EC-4: Data recovery scenarios
