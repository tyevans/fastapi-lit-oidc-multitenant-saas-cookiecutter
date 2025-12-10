# P5-05: Document Performance Baselines

## Task Identifier
**ID:** P5-05
**Phase:** 5 - Developer Experience
**Domain:** Documentation
**Complexity:** S (Small)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| P5-02 | Informational | Recommended first | Uses k6 test output format for baselines |

## Scope

### In Scope
- Document performance baseline methodology
- Define key performance indicators (KPIs) and thresholds
- Create performance baseline template
- Document expected performance characteristics
- Provide guidance on establishing project-specific baselines
- Create performance regression detection guidelines
- Document capacity planning considerations

### Out of Scope
- Actual performance measurements (project-specific)
- Automated performance regression detection in CI
- Detailed capacity planning calculations
- Infrastructure sizing recommendations
- APM tool integration (New Relic, Datadog)

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/docs/
  performance-baselines.md         # Main performance baselines document
  performance-testing-guide.md     # How to run and interpret tests
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/tests/load/README.md            # k6 documentation (P5-02)
template/{{cookiecutter.project_slug}}/tests/load/scenarios/*.js       # Test scenarios
template/{{cookiecutter.project_slug}}/docs/api-versioning.md          # Related docs (P5-04)
```

## Implementation Details

### 1. Performance Baselines Document (`docs/performance-baselines.md`)

```markdown
# Performance Baselines

This document defines performance expectations and baseline measurements for {{ cookiecutter.project_name }}.

## Overview

Performance baselines establish expected behavior under normal conditions. They enable:

- **Regression Detection**: Identify when changes degrade performance
- **Capacity Planning**: Understand system limits and scaling needs
- **SLA Definition**: Set realistic performance targets
- **Incident Response**: Know what "normal" looks like

## Key Performance Indicators (KPIs)

### Response Time Metrics

| Metric | Target | Critical | Description |
|--------|--------|----------|-------------|
| **P50 Latency** | < 100ms | < 200ms | Median response time |
| **P95 Latency** | < 300ms | < 500ms | 95th percentile response time |
| **P99 Latency** | < 500ms | < 1000ms | 99th percentile response time |
| **Max Latency** | < 2000ms | < 5000ms | Maximum observed response time |

### Throughput Metrics

| Metric | Target | Critical | Description |
|--------|--------|----------|-------------|
| **Requests/Second** | > 100 | > 50 | Sustained request rate |
| **Peak RPS** | > 500 | > 200 | Maximum burst capacity |
| **Concurrent Users** | > 100 | > 50 | Simultaneous active sessions |

### Reliability Metrics

| Metric | Target | Critical | Description |
|--------|--------|----------|-------------|
| **Error Rate** | < 0.1% | < 1% | Percentage of failed requests |
| **Availability** | > 99.9% | > 99% | Uptime percentage |
| **Success Rate** | > 99.9% | > 99% | Successful transaction rate |

### Resource Utilization

| Resource | Normal | Warning | Critical |
|----------|--------|---------|----------|
| **CPU** | < 50% | < 70% | < 85% |
| **Memory** | < 60% | < 75% | < 90% |
| **DB Connections** | < 50% | < 70% | < 85% |
| **Redis Connections** | < 50% | < 70% | < 85% |

## Endpoint-Specific Baselines

### Health Endpoints

| Endpoint | P50 | P95 | P99 | Target RPS |
|----------|-----|-----|-----|------------|
| `GET /api/v1/health` | < 10ms | < 25ms | < 50ms | 1000+ |
| `GET /api/v1/health/ready` | < 20ms | < 50ms | < 100ms | 500+ |
| `GET /api/v1/health/live` | < 5ms | < 15ms | < 30ms | 1000+ |

### Authentication Endpoints

| Endpoint | P50 | P95 | P99 | Target RPS |
|----------|-----|-----|-----|------------|
| `POST /api/v1/auth/token` | < 100ms | < 200ms | < 400ms | 50+ |
| `POST /api/v1/auth/refresh` | < 50ms | < 100ms | < 200ms | 100+ |
| `GET /api/v1/auth/me` | < 30ms | < 75ms | < 150ms | 200+ |

### API Endpoints

| Endpoint | P50 | P95 | P99 | Target RPS |
|----------|-----|-----|-----|------------|
| `GET /api/v1/todos` | < 50ms | < 100ms | < 200ms | 200+ |
| `POST /api/v1/todos` | < 75ms | < 150ms | < 300ms | 100+ |
| `GET /api/v1/todos/{id}` | < 30ms | < 75ms | < 150ms | 300+ |

## Baseline Measurement Methodology

### Test Environment

Performance baselines should be measured in a consistent environment:

```yaml
# Recommended baseline environment
Environment: Staging (production-equivalent)
Database: PostgreSQL 15+ (dedicated, not shared)
Redis: Redis 7+ (dedicated)
Containers:
  Backend: 2 CPU, 2GB RAM
  Frontend: 0.5 CPU, 512MB RAM
Network: Low latency (< 10ms to database)
```

### Test Scenarios

Run these scenarios to establish baselines:

1. **Smoke Test**: Verify system is functional
   ```bash
   ./scripts/load-test.sh smoke
   ```

2. **Baseline Load Test**: Normal expected traffic
   ```bash
   ./scripts/load-test.sh load --vus 50 --duration 10m
   ```

3. **Stress Test**: Find breaking points
   ```bash
   ./scripts/load-test.sh stress
   ```

4. **Soak Test**: Extended reliability
   ```bash
   ./scripts/load-test.sh soak
   ```

### Recording Baselines

After each test, record the results:

```json
{
  "test_date": "2024-01-15T10:30:00Z",
  "environment": "staging",
  "git_commit": "abc123",
  "scenario": "load",
  "configuration": {
    "vus": 50,
    "duration": "10m"
  },
  "results": {
    "http_reqs": 45000,
    "http_req_duration": {
      "avg": 85.3,
      "p50": 72.1,
      "p95": 156.8,
      "p99": 289.4,
      "max": 1245.6
    },
    "http_req_failed": 0.02,
    "checks_passed": 99.8
  },
  "resources": {
    "cpu_avg": 45,
    "memory_avg": 58,
    "db_connections_peak": 25
  }
}
```

## Establishing Your Baselines

### Step 1: Initial Measurement

1. Deploy to a consistent environment (staging)
2. Ensure no other load on the system
3. Run baseline load test:
   ```bash
   ./scripts/load-test.sh load --output baseline-$(date +%Y%m%d).json
   ```

4. Record results in `docs/baselines/` directory

### Step 2: Multiple Runs

Run the baseline test at least 3 times:

```bash
for i in 1 2 3; do
  ./scripts/load-test.sh load --output baseline-run-$i.json
  sleep 60  # Cool down between runs
done
```

### Step 3: Calculate Thresholds

From multiple runs, calculate:

- **Target**: Average of P95 values
- **Critical**: Max of P99 values + 20% buffer

Example calculation:
```
Run 1 P95: 145ms
Run 2 P95: 152ms
Run 3 P95: 148ms

Target P95 = avg(145, 152, 148) = 148ms
Round up to: 150ms

Run 1 P99: 285ms
Run 2 P99: 312ms
Run 3 P99: 298ms

Critical P99 = max(285, 312, 298) * 1.2 = 374ms
Round up to: 400ms
```

### Step 4: Document Baselines

Update this document with your measured values:

```markdown
## Project-Specific Baselines

**Baseline Date**: 2024-01-15
**Git Commit**: abc123def
**Environment**: Staging (AWS t3.medium)

| Endpoint | P50 | P95 | P99 | Notes |
|----------|-----|-----|-----|-------|
| GET /api/v1/health | 8ms | 22ms | 45ms | |
| GET /api/v1/todos | 42ms | 98ms | 187ms | With 1000 todos |
```

## Performance Regression Detection

### Manual Detection

Compare new results against baseline:

```bash
# Run current performance test
./scripts/load-test.sh load --output current.json

# Compare key metrics
# P95 should not exceed baseline P95 by more than 10%
# Error rate should not exceed baseline error rate
```

### Threshold Violations

If thresholds are violated:

1. **Investigate**: Check recent commits for changes
2. **Profile**: Use profiling tools to identify bottlenecks
3. **Fix or Accept**: Either fix the regression or update baselines with justification

### Baseline Update Policy

Update baselines when:

- New features fundamentally change performance characteristics
- Infrastructure changes affect baseline (more/less resources)
- After optimizations (new, better baselines)

Do NOT update baselines to hide regressions.

## Capacity Planning

### Scaling Factors

Based on load testing, estimate scaling needs:

| User Count | Expected RPS | Recommended Replicas |
|------------|--------------|----------------------|
| 100 | 10-50 | 1 |
| 1,000 | 50-200 | 2 |
| 10,000 | 200-500 | 3-5 |
| 100,000 | 500-2000 | 5-10+ |

### Bottleneck Analysis

Common bottlenecks and solutions:

| Bottleneck | Symptoms | Solutions |
|------------|----------|-----------|
| **Database** | High query time, connection exhaustion | Read replicas, connection pooling, query optimization |
| **Redis** | High latency, connection errors | Larger instance, clustering |
| **CPU** | High CPU, slow responses | Horizontal scaling, code optimization |
| **Memory** | OOM errors, swap usage | Increase limits, fix memory leaks |
| **Network** | Timeout errors, high latency | CDN, regional deployment |

### Load Testing for Capacity

To determine capacity limits:

```bash
# Find breaking point
./scripts/load-test.sh stress

# Note the VU count where:
# - Error rate exceeds 1%
# - P95 latency exceeds SLA
# - Resource utilization exceeds 85%
```

## Alerting Thresholds

Based on baselines, configure alerts:

### Response Time Alerts

```yaml
# prometheus/alerts.yml
groups:
  - name: performance
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency above 500ms"

      - alert: CriticalLatency
        expr: histogram_quantile(0.99, http_request_duration_seconds_bucket) > 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "P99 latency above 1s"
```

### Error Rate Alerts

```yaml
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Error rate above 1%"
```

## Baseline History

Track baseline evolution over time:

| Date | Git Commit | P95 Latency | RPS | Notes |
|------|------------|-------------|-----|-------|
| 2024-01-01 | abc123 | 150ms | 200 | Initial baseline |
| 2024-02-01 | def456 | 145ms | 220 | After query optimization |
| 2024-03-01 | ghi789 | 160ms | 250 | Added new feature X |

## Related Documentation

- [Performance Testing Guide](./performance-testing-guide.md)
- [Load Testing README](../tests/load/README.md)
- [Prometheus Alerting Rules](../observability/prometheus/alerts.yml)
```

### 2. Performance Testing Guide (`docs/performance-testing-guide.md`)

```markdown
# Performance Testing Guide

This guide explains how to run performance tests and interpret results for {{ cookiecutter.project_name }}.

## Prerequisites

### Install k6

```bash
# macOS
brew install k6

# Ubuntu/Debian
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
    sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

### Start the Application

```bash
# Development
./scripts/docker-dev.sh up

# Or staging/production-like
docker compose -f compose.production.yml up
```

## Running Tests

### Quick Validation (Smoke Test)

```bash
./scripts/load-test.sh smoke
```

**Expected Output:**
```
     checks.........................: 100.00%
     http_req_duration..............: avg=45ms  p(95)=89ms
     http_req_failed................: 0.00%
```

**Pass Criteria:**
- All checks pass (100%)
- No failed requests (0%)
- P95 latency under 500ms

### Normal Load Test

```bash
./scripts/load-test.sh load
```

**Expected Output:**
```
     checks.........................: 98.50%
     http_req_duration..............: avg=85ms  p(95)=156ms  p(99)=289ms
     http_req_failed................: 0.02%
     vus............................: 50      min=0     max=50
```

**Pass Criteria:**
- Checks > 95%
- Error rate < 1%
- P95 latency under 500ms

### Stress Test

```bash
./scripts/load-test.sh stress
```

**Purpose:** Find breaking points and observe recovery

**What to Watch:**
- At what VU count does error rate spike?
- At what VU count does latency exceed SLA?
- Does the system recover after load decreases?

### Soak Test

```bash
./scripts/load-test.sh soak
```

**Purpose:** Find memory leaks and long-term issues

**Duration:** 30+ minutes recommended

**What to Watch:**
- Memory growth over time
- Response time degradation
- Connection pool exhaustion

## Interpreting Results

### Understanding k6 Output

```
     data_received..................: 15 MB  254 kB/s
     data_sent......................: 2.1 MB 35 kB/s
     http_req_blocked...............: avg=1.2ms   min=0s      med=0s      max=98ms    p(90)=1ms    p(95)=5ms
     http_req_connecting............: avg=0.8ms   min=0s      med=0s      max=45ms    p(90)=0s     p(95)=2ms
     http_req_duration..............: avg=85.3ms  min=12ms    med=72ms    max=1245ms  p(90)=145ms  p(95)=156ms
       { expected_response:true }...: avg=84.1ms  min=12ms    med=71ms    max=1102ms  p(90)=142ms  p(95)=153ms
     http_req_failed................: 0.02%  1 out of 45000
     http_req_receiving.............: avg=0.5ms   min=0s      med=0s      max=45ms    p(90)=1ms    p(95)=2ms
     http_req_sending...............: avg=0.1ms   min=0s      med=0s      max=12ms    p(90)=0s     p(95)=0s
     http_req_tls_handshaking.......: avg=0s      min=0s      med=0s      max=0s      p(90)=0s     p(95)=0s
     http_req_waiting...............: avg=84.7ms  min=11ms    med=71ms    max=1200ms  p(90)=143ms  p(95)=154ms
     http_reqs......................: 45000   750/s
     iteration_duration.............: avg=2.1s    min=1.5s    med=2s      max=5.2s    p(90)=2.8s   p(95)=3.1s
     iterations.....................: 22500   375/s
     vus............................: 50      min=0       max=50
     vus_max........................: 50      min=50      max=50
```

### Key Metrics Explained

| Metric | Description | Good Value |
|--------|-------------|------------|
| `http_req_duration` | Total request time | P95 < 500ms |
| `http_req_failed` | Error percentage | < 1% |
| `http_reqs` | Requests per second | > 100 |
| `http_req_blocked` | Time waiting for connection | < 10ms avg |
| `http_req_waiting` | Server processing time | Close to `http_req_duration` |
| `checks` | Assertion pass rate | > 95% |

### Identifying Issues

**High Latency (P95 > 500ms):**
- Check database query performance
- Look for N+1 query patterns
- Check external service calls
- Review connection pool settings

**High Error Rate (> 1%):**
- Check application logs for errors
- Review rate limiting settings
- Check database connection limits
- Look for resource exhaustion

**Low Throughput (< expected RPS):**
- Check if VUs are waiting (think time)
- Review connection limits
- Check for synchronous bottlenecks

## Custom Tests

### Testing Specific Endpoints

```javascript
// tests/load/scripts/custom.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '1m',
};

export default function() {
  const response = http.get('http://localhost:8000/api/v1/your-endpoint');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
  });
  sleep(1);
}
```

Run with:
```bash
k6 run tests/load/scripts/custom.js
```

### Testing with Authentication

```bash
# Set test user credentials
export TEST_USERS="testuser:testpass"
export TOKEN_URL="http://localhost:8080/realms/myapp/protocol/openid-connect/token"

# Run authenticated tests
k6 run tests/load/scripts/api-authenticated.js
```

## Saving and Comparing Results

### Save Results

```bash
./scripts/load-test.sh load --output results-$(date +%Y%m%d).json
```

### Compare Results

```bash
# Manual comparison
diff results-before.json results-after.json

# Or use jq for specific metrics
jq '.metrics.http_req_duration.values["p(95)"]' results-*.json
```

## Troubleshooting

### "Connection refused" errors

```bash
# Check if backend is running
curl http://localhost:8000/api/v1/health

# Check Docker containers
docker compose ps
```

### High error rate from the start

```bash
# Check backend logs
docker compose logs backend

# Check database connectivity
docker compose exec backend python -c "from app.core.database import engine; print(engine.url)"
```

### Results vary significantly between runs

- Ensure no other processes are using resources
- Run tests from a consistent environment
- Use longer durations for more stable results
- Check for garbage collection pauses

## Next Steps

After completing performance testing:

1. Record results in [Performance Baselines](./performance-baselines.md)
2. Configure [Prometheus alerts](../observability/prometheus/alerts.yml)
3. Set up automated regression testing in CI (future)
```

## Success Criteria

### Functional Requirements
- [ ] FR-DX-007: Performance baseline documentation included
- [ ] KPIs defined with target and critical thresholds
- [ ] Endpoint-specific baselines provided
- [ ] Methodology for establishing baselines documented
- [ ] Capacity planning guidance included

### Verification Steps
1. **Document Review:**
   - KPIs are clearly defined
   - Thresholds are reasonable
   - Methodology is actionable

2. **Template Validation:**
   - Baseline recording template is complete
   - Can be filled in after running tests

3. **Consistency Check:**
   - References to k6 commands match P5-02
   - Metrics align with k6 output format

### Quality Gates
- [ ] Documents use clear, professional language
- [ ] KPIs have both target and critical thresholds
- [ ] Methodology is step-by-step and reproducible
- [ ] Capacity planning guidance is practical
- [ ] Integration with alerting is shown
- [ ] Troubleshooting section is helpful

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P5-02 | k6 output format | Baselines use k6 metrics format |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P6-01 | CLAUDE.md | References baseline docs |
| P3-01 | Prometheus alerts | Alert thresholds from baselines |

### Integration Contract
```yaml
# Contract: Performance Baselines Documentation

# Documentation files
docs/performance-baselines.md      # Main baselines document
docs/performance-testing-guide.md  # How to run tests

# Key definitions
kpis:
  - p50_latency: < 100ms target
  - p95_latency: < 300ms target
  - p99_latency: < 500ms target
  - error_rate: < 0.1% target
  - throughput: > 100 rps target

# Baseline format
baseline_record:
  test_date: ISO8601
  environment: string
  git_commit: string
  scenario: string
  results: object
  resources: object

# Update policy
update_baselines_when:
  - new_features_change_characteristics
  - infrastructure_changes
  - after_optimizations
```

## Monitoring and Observability

### Baseline Tracking
- Store baselines in version control
- Track baseline history over time
- Alert when new results deviate significantly

### Dashboard Integration
If using Grafana:
- Display current vs baseline metrics
- Show trend over time
- Highlight regressions

## Infrastructure Needs

No infrastructure requirements - pure documentation task.

## Estimated Effort

**Size:** S (Small)
**Time:** 0.5-1 day
**Justification:**
- Documentation-only task
- Templates adapted from industry standards
- No code implementation required
- Builds on k6 foundation from P5-02

## Notes

### Design Decisions

**1. Percentile-Based Thresholds:**
- P95 for normal operations
- P99 for edge cases
- More meaningful than averages

**2. Separate Target vs Critical:**
- Target: What we aim for
- Critical: When to alert/investigate
- Allows for normal variation

**3. Methodology Focus:**
- Reproducible process
- Multiple runs for accuracy
- Clear update policy

### Future Considerations

**Automated Regression Detection:**
- Compare CI test results to baselines
- Fail builds on significant regression
- Store historical trends

**Dashboard Integration:**
- Grafana panel for baseline comparison
- Trend visualization
- Automatic alerting

### Related Requirements
- FR-DX-007: Performance baseline documentation included
- US-5.2: Performance baseline documented
- US-3.2: Alerting rules (use baselines for thresholds)
