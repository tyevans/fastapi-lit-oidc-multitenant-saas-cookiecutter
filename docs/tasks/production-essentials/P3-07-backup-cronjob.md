# P3-07: Create Kubernetes Backup CronJob

## Task Identifier
**ID:** P3-07
**Phase:** 3 - Operational Readiness
**Domain:** DevOps
**Complexity:** S (Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P3-05 | Required | Documented | Backup script that CronJob executes |
| P4-01 | Required | Not Started | Kubernetes base manifests (provides structure and patterns) |

## Scope

### In Scope
- Create Kubernetes CronJob manifest for scheduled database backups
- Configure daily, weekly, and monthly backup schedules
- Set up PersistentVolumeClaim for backup storage
- Add Secret references for database credentials
- Configure job history limits and concurrency policy
- Add resource requests/limits for backup jobs
- Create ServiceAccount with minimal required permissions
- Add ConfigMap for backup script configuration

### Out of Scope
- Backup script implementation (P3-05)
- Restore CronJob (manual restore is preferred)
- Backup to S3 (documented in script, not K8s-specific)
- Monitoring/alerting integration (separate concern)
- Velero or other K8s backup solutions

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/k8s/base/backup-cronjob.yaml
template/{{cookiecutter.project_slug}}/k8s/base/backup-pvc.yaml
template/{{cookiecutter.project_slug}}/k8s/base/backup-configmap.yaml
template/{{cookiecutter.project_slug}}/k8s/base/backup-serviceaccount.yaml
```

### Files to Modify
```
template/{{cookiecutter.project_slug}}/k8s/base/kustomization.yaml  (add backup resources)
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/scripts/db-backup.sh         (script to execute)
template/{{cookiecutter.project_slug}}/k8s/base/backend-deployment.yaml (pattern reference)
template/{{cookiecutter.project_slug}}/k8s/base/configmap.yaml      (config pattern reference)
```

## Implementation Details

### 1. Backup CronJob Manifest (`k8s/base/backup-cronjob.yaml`)

```yaml
# {{ cookiecutter.project_name }} Database Backup CronJobs
# Schedules: Daily (2 AM), Weekly (Sunday 3 AM), Monthly (1st of month 4 AM)
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ cookiecutter.project_slug }}-backup-daily
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backup
    app.kubernetes.io/part-of: {{ cookiecutter.project_slug }}
    backup-type: daily
spec:
  schedule: "0 2 * * *"  # Daily at 2:00 AM
  timeZone: "UTC"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  startingDeadlineSeconds: 600  # 10 minutes to start
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600  # 1 hour max
      template:
        metadata:
          labels:
            app.kubernetes.io/name: {{ cookiecutter.project_slug }}
            app.kubernetes.io/component: backup
            backup-type: daily
        spec:
          serviceAccountName: {{ cookiecutter.project_slug }}-backup
          restartPolicy: OnFailure
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            fsGroup: 1000
          containers:
            - name: backup
              image: postgres:{{ cookiecutter.postgres_version }}-alpine
              imagePullPolicy: IfNotPresent
              command:
                - /bin/sh
                - -c
                - |
                  set -e

                  # Configuration
                  BACKUP_TYPE="daily"
                  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                  BACKUP_FILE="${POSTGRES_DB}_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"
                  BACKUP_PATH="/backups/${BACKUP_FILE}"

                  echo "[$(date)] Starting ${BACKUP_TYPE} backup..."

                  # Test connection
                  pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

                  # Create backup with compression
                  pg_dump \
                    -h "${POSTGRES_HOST}" \
                    -p "${POSTGRES_PORT}" \
                    -U "${POSTGRES_USER}" \
                    -d "${POSTGRES_DB}" \
                    --no-password \
                    --format=plain \
                    --no-owner \
                    --no-privileges \
                    | gzip > "${BACKUP_PATH}"

                  # Generate checksum
                  sha256sum "${BACKUP_PATH}" > "${BACKUP_PATH}.sha256"

                  # Report success
                  BACKUP_SIZE=$(du -h "${BACKUP_PATH}" | cut -f1)
                  echo "[$(date)] Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

                  # Cleanup old daily backups (keep last 7)
                  cd /backups
                  ls -t ${POSTGRES_DB}_daily_*.sql.gz 2>/dev/null | tail -n +8 | xargs -r rm -f
                  ls -t ${POSTGRES_DB}_daily_*.sql.gz.sha256 2>/dev/null | tail -n +8 | xargs -r rm -f

                  echo "[$(date)] Cleanup completed"
              env:
                - name: POSTGRES_HOST
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_HOST
                - name: POSTGRES_PORT
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_PORT
                - name: POSTGRES_DB
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_DB
                - name: POSTGRES_USER
                  valueFrom:
                    secretKeyRef:
                      name: {{ cookiecutter.project_slug }}-db-credentials
                      key: username
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: {{ cookiecutter.project_slug }}-db-credentials
                      key: password
              resources:
                requests:
                  cpu: 100m
                  memory: 256Mi
                limits:
                  cpu: 500m
                  memory: 512Mi
              volumeMounts:
                - name: backup-storage
                  mountPath: /backups
          volumes:
            - name: backup-storage
              persistentVolumeClaim:
                claimName: {{ cookiecutter.project_slug }}-backup-pvc

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ cookiecutter.project_slug }}-backup-weekly
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backup
    app.kubernetes.io/part-of: {{ cookiecutter.project_slug }}
    backup-type: weekly
spec:
  schedule: "0 3 * * 0"  # Weekly on Sunday at 3:00 AM
  timeZone: "UTC"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 2
  failedJobsHistoryLimit: 2
  startingDeadlineSeconds: 600
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600
      template:
        metadata:
          labels:
            app.kubernetes.io/name: {{ cookiecutter.project_slug }}
            app.kubernetes.io/component: backup
            backup-type: weekly
        spec:
          serviceAccountName: {{ cookiecutter.project_slug }}-backup
          restartPolicy: OnFailure
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            fsGroup: 1000
          containers:
            - name: backup
              image: postgres:{{ cookiecutter.postgres_version }}-alpine
              imagePullPolicy: IfNotPresent
              command:
                - /bin/sh
                - -c
                - |
                  set -e

                  BACKUP_TYPE="weekly"
                  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                  BACKUP_FILE="${POSTGRES_DB}_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"
                  BACKUP_PATH="/backups/${BACKUP_FILE}"

                  echo "[$(date)] Starting ${BACKUP_TYPE} backup..."

                  pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

                  pg_dump \
                    -h "${POSTGRES_HOST}" \
                    -p "${POSTGRES_PORT}" \
                    -U "${POSTGRES_USER}" \
                    -d "${POSTGRES_DB}" \
                    --no-password \
                    --format=plain \
                    --no-owner \
                    --no-privileges \
                    | gzip > "${BACKUP_PATH}"

                  sha256sum "${BACKUP_PATH}" > "${BACKUP_PATH}.sha256"

                  BACKUP_SIZE=$(du -h "${BACKUP_PATH}" | cut -f1)
                  echo "[$(date)] Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

                  # Cleanup old weekly backups (keep last 4)
                  cd /backups
                  ls -t ${POSTGRES_DB}_weekly_*.sql.gz 2>/dev/null | tail -n +5 | xargs -r rm -f
                  ls -t ${POSTGRES_DB}_weekly_*.sql.gz.sha256 2>/dev/null | tail -n +5 | xargs -r rm -f

                  echo "[$(date)] Cleanup completed"
              env:
                - name: POSTGRES_HOST
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_HOST
                - name: POSTGRES_PORT
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_PORT
                - name: POSTGRES_DB
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_DB
                - name: POSTGRES_USER
                  valueFrom:
                    secretKeyRef:
                      name: {{ cookiecutter.project_slug }}-db-credentials
                      key: username
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: {{ cookiecutter.project_slug }}-db-credentials
                      key: password
              resources:
                requests:
                  cpu: 100m
                  memory: 256Mi
                limits:
                  cpu: 500m
                  memory: 512Mi
              volumeMounts:
                - name: backup-storage
                  mountPath: /backups
          volumes:
            - name: backup-storage
              persistentVolumeClaim:
                claimName: {{ cookiecutter.project_slug }}-backup-pvc

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: {{ cookiecutter.project_slug }}-backup-monthly
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backup
    app.kubernetes.io/part-of: {{ cookiecutter.project_slug }}
    backup-type: monthly
spec:
  schedule: "0 4 1 * *"  # Monthly on 1st at 4:00 AM
  timeZone: "UTC"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 2
  failedJobsHistoryLimit: 2
  startingDeadlineSeconds: 600
  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 7200  # 2 hours for monthly
      template:
        metadata:
          labels:
            app.kubernetes.io/name: {{ cookiecutter.project_slug }}
            app.kubernetes.io/component: backup
            backup-type: monthly
        spec:
          serviceAccountName: {{ cookiecutter.project_slug }}-backup
          restartPolicy: OnFailure
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            fsGroup: 1000
          containers:
            - name: backup
              image: postgres:{{ cookiecutter.postgres_version }}-alpine
              imagePullPolicy: IfNotPresent
              command:
                - /bin/sh
                - -c
                - |
                  set -e

                  BACKUP_TYPE="monthly"
                  TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                  BACKUP_FILE="${POSTGRES_DB}_${BACKUP_TYPE}_${TIMESTAMP}.sql.gz"
                  BACKUP_PATH="/backups/${BACKUP_FILE}"

                  echo "[$(date)] Starting ${BACKUP_TYPE} backup..."

                  pg_isready -h "${POSTGRES_HOST}" -p "${POSTGRES_PORT}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}"

                  pg_dump \
                    -h "${POSTGRES_HOST}" \
                    -p "${POSTGRES_PORT}" \
                    -U "${POSTGRES_USER}" \
                    -d "${POSTGRES_DB}" \
                    --no-password \
                    --format=plain \
                    --no-owner \
                    --no-privileges \
                    | gzip > "${BACKUP_PATH}"

                  sha256sum "${BACKUP_PATH}" > "${BACKUP_PATH}.sha256"

                  BACKUP_SIZE=$(du -h "${BACKUP_PATH}" | cut -f1)
                  echo "[$(date)] Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"

                  # Cleanup old monthly backups (keep last 12)
                  cd /backups
                  ls -t ${POSTGRES_DB}_monthly_*.sql.gz 2>/dev/null | tail -n +13 | xargs -r rm -f
                  ls -t ${POSTGRES_DB}_monthly_*.sql.gz.sha256 2>/dev/null | tail -n +13 | xargs -r rm -f

                  echo "[$(date)] Cleanup completed"
              env:
                - name: POSTGRES_HOST
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_HOST
                - name: POSTGRES_PORT
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_PORT
                - name: POSTGRES_DB
                  valueFrom:
                    configMapKeyRef:
                      name: {{ cookiecutter.project_slug }}-backup-config
                      key: POSTGRES_DB
                - name: POSTGRES_USER
                  valueFrom:
                    secretKeyRef:
                      name: {{ cookiecutter.project_slug }}-db-credentials
                      key: username
                - name: PGPASSWORD
                  valueFrom:
                    secretKeyRef:
                      name: {{ cookiecutter.project_slug }}-db-credentials
                      key: password
              resources:
                requests:
                  cpu: 100m
                  memory: 256Mi
                limits:
                  cpu: 1000m
                  memory: 1Gi
              volumeMounts:
                - name: backup-storage
                  mountPath: /backups
          volumes:
            - name: backup-storage
              persistentVolumeClaim:
                claimName: {{ cookiecutter.project_slug }}-backup-pvc
```

### 2. Backup PersistentVolumeClaim (`k8s/base/backup-pvc.yaml`)

```yaml
# {{ cookiecutter.project_name }} Backup Storage
# Persistent volume for database backups
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {{ cookiecutter.project_slug }}-backup-pvc
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backup
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi  # Adjust based on database size
  # storageClassName: standard  # Uncomment and set for specific storage class
```

### 3. Backup ConfigMap (`k8s/base/backup-configmap.yaml`)

```yaml
# {{ cookiecutter.project_name }} Backup Configuration
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ cookiecutter.project_slug }}-backup-config
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backup
data:
  POSTGRES_HOST: "{{ cookiecutter.project_slug }}-postgres"
  POSTGRES_PORT: "5432"
  POSTGRES_DB: "{{ cookiecutter.postgres_db }}"
  # Retention settings (for reference - implemented in CronJob script)
  BACKUP_RETENTION_DAILY: "7"
  BACKUP_RETENTION_WEEKLY: "4"
  BACKUP_RETENTION_MONTHLY: "12"
```

### 4. Backup ServiceAccount (`k8s/base/backup-serviceaccount.yaml`)

```yaml
# {{ cookiecutter.project_name }} Backup ServiceAccount
# Minimal permissions for backup jobs
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ cookiecutter.project_slug }}-backup
  labels:
    app.kubernetes.io/name: {{ cookiecutter.project_slug }}
    app.kubernetes.io/component: backup
automountServiceAccountToken: false
```

### 5. Kustomization Update (`k8s/base/kustomization.yaml`)

Add to existing kustomization.yaml:

```yaml
resources:
  # ... existing resources ...
  - backup-cronjob.yaml
  - backup-pvc.yaml
  - backup-configmap.yaml
  - backup-serviceaccount.yaml
```

## Success Criteria

### Functional Requirements
- [ ] CronJobs are created with correct schedules (daily, weekly, monthly)
- [ ] Jobs execute pg_dump and create compressed backups
- [ ] Backups are stored in persistent volume
- [ ] Old backups are cleaned up according to retention policy
- [ ] Jobs respect resource limits

### Verification Steps
1. **Deploy CronJobs:**
   ```bash
   kubectl apply -k k8s/base/
   kubectl get cronjobs
   # Expected: Three cronjobs listed (daily, weekly, monthly)
   ```

2. **Manual Job Trigger:**
   ```bash
   # Create a job from the cronjob for testing
   kubectl create job --from=cronjob/{{ cookiecutter.project_slug }}-backup-daily test-backup

   # Watch job progress
   kubectl get pods -l backup-type=daily --watch

   # Check logs
   kubectl logs job/test-backup
   ```

3. **Verify Backup Created:**
   ```bash
   # Access PVC to check backups
   kubectl run -it --rm debug --image=busybox --restart=Never -- ls -la /backups
   # (Mount PVC to debug pod)
   ```

4. **Check Job History:**
   ```bash
   kubectl get jobs -l app.kubernetes.io/component=backup
   # Expected: Completed jobs with appropriate age
   ```

### Quality Gates
- [ ] CronJobs pass Kubernetes validation
- [ ] Jobs complete within activeDeadlineSeconds
- [ ] Backups are created with correct naming convention
- [ ] Cleanup removes old backups correctly
- [ ] SecurityContext enforces non-root execution

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P3-05 | Backup file format and naming | CronJob creates same format as db-backup.sh |
| P4-01 | K8s manifest patterns | Follows base manifest conventions |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P4-02 | Kustomize staging overlay | May customize schedule or retention |
| P4-03 | Kustomize production overlay | May increase resources or storage |

### Integration Contract
```yaml
# Contract: Backup CronJob outputs

# Backup files:
# - Location: /backups/ in PVC
# - Naming: ${POSTGRES_DB}_${type}_${timestamp}.sql.gz
# - Checksum: ${backup_file}.sha256

# Job labels:
# - app.kubernetes.io/component: backup
# - backup-type: daily|weekly|monthly

# Required secrets:
# - {{ cookiecutter.project_slug }}-db-credentials (username, password keys)
```

## Monitoring and Observability

### Job Status Monitoring
```bash
# Check cronjob status
kubectl get cronjobs

# Check recent job completions
kubectl get jobs -l app.kubernetes.io/component=backup --sort-by=.metadata.creationTimestamp

# Check failed jobs
kubectl get jobs -l app.kubernetes.io/component=backup --field-selector=status.successful=0
```

### Prometheus Metrics
Kubernetes exposes job metrics via kube-state-metrics:
- `kube_cronjob_status_last_schedule_time`
- `kube_job_complete`
- `kube_job_failed`

### Alerting
Consider adding Prometheus alerts for:
- Backup job failures
- Backup storage running low
- Backup job taking too long

Example alert (for P3-01):
```yaml
- alert: BackupJobFailed
  expr: kube_job_status_failed{job_name=~".*backup.*"} > 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Database backup job failed"
```

## Infrastructure Needs

### Storage Requirements
- PVC with ReadWriteOnce access
- Storage class supporting dynamic provisioning (recommended)
- Sufficient capacity for retention policy (estimate: DB size * 1.5 * (7 + 4 + 12))

### Network Requirements
- CronJob pods must reach PostgreSQL service
- No external network access required for basic operation

### Resource Estimates
| Backup Type | CPU Request | Memory Request | Duration |
|-------------|-------------|----------------|----------|
| Daily | 100m | 256Mi | 5-30 min |
| Weekly | 100m | 256Mi | 5-30 min |
| Monthly | 100m | 256Mi | 10-60 min |

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Follows established K8s patterns
- Straightforward CronJob configuration
- Reuses backup script logic inline
- Minimal custom code required

## Notes

### Design Decisions

**1. Inline Script vs. ConfigMap:**
The backup script is inline in the CronJob rather than mounted from ConfigMap for:
- Simpler deployment (fewer resources)
- Easier debugging (script visible in manifest)
- Atomic updates (script changes with CronJob)

**2. Separate CronJobs per Schedule:**
Three separate CronJobs instead of one with multiple schedules:
- Clearer job history per backup type
- Independent failure handling
- Easier resource customization

**3. PostgreSQL Alpine Image:**
Uses official postgres image for:
- Built-in pg_dump with version matching
- Minimal container size
- Regular security updates

**4. Concurrency Policy: Forbid:**
Prevents overlapping backups which could:
- Cause database contention
- Fill storage unexpectedly
- Create inconsistent backup sets

### Production Considerations

**Storage Class:**
For production, specify a storage class with:
- Appropriate performance (SSD for faster backups)
- Snapshot support (for additional backup layer)
- Retention policies (storage-level backup)

**S3 Integration:**
For S3 backup storage, modify the script to use AWS CLI:
```bash
# Add to container command
aws s3 cp "${BACKUP_PATH}" "s3://${BACKUP_S3_BUCKET}/${BACKUP_S3_PREFIX}${BACKUP_TYPE}/"
```

**Cross-Region Replication:**
Consider S3 cross-region replication or multi-region PV for disaster recovery.

### Related Requirements
- FR-OPS-011: Database backup script using pg_dump shall be included
- FR-OPS-012: Backup script shall support configurable retention policy
- US-3.3: Cron job configuration for scheduled backups
