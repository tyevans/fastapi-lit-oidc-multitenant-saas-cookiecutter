# P5-02: Create k6 Load Testing Scripts

## Task Identifier
**ID:** P5-02
**Phase:** 5 - Developer Experience
**Domain:** DevOps
**Complexity:** M (Medium)

## Dependencies

| Dependency | Type | Status | Notes |
|------------|------|--------|-------|
| None | - | - | Can be developed independently |

## Scope

### In Scope
- Create k6 load testing script structure and configuration
- Implement health check endpoint load test as baseline
- Implement API endpoint load tests (authenticated and unauthenticated)
- Create configurable test scenarios (smoke, load, stress, soak)
- Create `scripts/load-test.sh` wrapper script
- Document k6 installation and usage
- Create test results output configuration (JSON, HTML summary)
- Add npm scripts for running load tests

### Out of Scope
- Authentication flow testing (covered in P5-03)
- CI integration for automated load testing (can be added later)
- Distributed load testing (k6 Cloud integration)
- Performance regression detection automation
- Grafana k6 dashboard integration

## Relevant Code Areas

### Files to Create
```
template/{{cookiecutter.project_slug}}/tests/load/
  k6.config.js                    # k6 configuration file
  scenarios/
    smoke.js                      # Quick validation (1 VU, 1 minute)
    load.js                       # Normal load (50 VUs, 5 minutes)
    stress.js                     # Beyond normal (100+ VUs, ramp up/down)
    soak.js                       # Extended duration (20 VUs, 30+ minutes)
  scripts/
    health.js                     # Health endpoint tests
    api-public.js                 # Public API endpoint tests
    api-authenticated.js          # Authenticated API tests (imports from P5-03)
  lib/
    config.js                     # Shared configuration (base URL, thresholds)
    helpers.js                    # Utility functions
    checks.js                     # Common check patterns
  README.md                       # Load testing documentation

template/{{cookiecutter.project_slug}}/scripts/
  load-test.sh                    # Wrapper script for running tests
```

### Reference Files
```
template/{{cookiecutter.project_slug}}/backend/app/api/routers/health.py    # Health endpoint
template/{{cookiecutter.project_slug}}/backend/app/main.py                  # API routes
template/{{cookiecutter.project_slug}}/scripts/docker-dev.sh                # Script pattern reference
```

## Implementation Details

### 1. k6 Configuration (`tests/load/k6.config.js`)

```javascript
// k6 Configuration for {{ cookiecutter.project_name }}
//
// This file defines shared configuration for all load test scenarios.
// Override via environment variables or command-line options.

export const config = {
  // Base URL for API requests
  baseUrl: __ENV.BASE_URL || 'http://localhost:{{ cookiecutter.backend_port }}',

  // API prefix
  apiPrefix: '{{ cookiecutter.backend_api_prefix }}',

  // Default thresholds (can be overridden per scenario)
  thresholds: {
    // 95% of requests should complete under 500ms
    http_req_duration: ['p(95)<500'],
    // Less than 1% error rate
    http_req_failed: ['rate<0.01'],
    // Specific endpoint thresholds
    'http_req_duration{name:health}': ['p(95)<100'],
    'http_req_duration{name:api}': ['p(95)<500'],
  },

  // Tags for grouping metrics
  tags: {
    project: '{{ cookiecutter.project_slug }}',
    environment: __ENV.ENVIRONMENT || 'local',
  },
};

// Scenario presets
export const scenarios = {
  smoke: {
    executor: 'constant-vus',
    vus: 1,
    duration: '1m',
  },
  load: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '2m', target: 50 },   // Ramp up to 50 VUs
      { duration: '5m', target: 50 },   // Stay at 50 VUs
      { duration: '2m', target: 0 },    // Ramp down to 0
    ],
  },
  stress: {
    executor: 'ramping-vus',
    startVUs: 0,
    stages: [
      { duration: '2m', target: 50 },   // Ramp up
      { duration: '5m', target: 50 },   // Normal load
      { duration: '2m', target: 100 },  // Push to stress
      { duration: '5m', target: 100 },  // Hold at stress
      { duration: '2m', target: 150 },  // Breaking point
      { duration: '5m', target: 150 },  // Hold at breaking
      { duration: '5m', target: 0 },    // Recovery
    ],
  },
  soak: {
    executor: 'constant-vus',
    vus: 20,
    duration: '30m',
  },
};
```

### 2. Shared Library (`tests/load/lib/config.js`)

```javascript
// Shared configuration and utilities for k6 tests
import { config } from '../k6.config.js';

export const BASE_URL = config.baseUrl;
export const API_PREFIX = config.apiPrefix;
export const API_URL = `${BASE_URL}${API_PREFIX}`;

// Default request options
export const defaultOptions = {
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  timeout: '30s',
};

// Authenticated request options (token injected at runtime)
export function authHeaders(token) {
  return {
    ...defaultOptions.headers,
    'Authorization': `Bearer ${token}`,
  };
}

// Standard thresholds for different endpoint types
export const standardThresholds = {
  health: {
    http_req_duration: ['p(95)<100', 'p(99)<200'],
    http_req_failed: ['rate<0.001'],
  },
  api_read: {
    http_req_duration: ['p(95)<300', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
  api_write: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};
```

### 3. Helper Functions (`tests/load/lib/helpers.js`)

```javascript
// Utility functions for k6 tests
import { sleep } from 'k6';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

// Random think time between requests (simulates real user behavior)
export function thinkTime(minSeconds = 1, maxSeconds = 3) {
  sleep(randomIntBetween(minSeconds, maxSeconds));
}

// Format bytes for logging
export function formatBytes(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(2) + ' KB';
  return (bytes / 1048576).toFixed(2) + ' MB';
}

// Generate unique test data
export function generateTestId() {
  return `test-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Parse JSON response safely
export function parseJsonResponse(response) {
  try {
    return JSON.parse(response.body);
  } catch (e) {
    console.error(`Failed to parse JSON: ${e.message}`);
    return null;
  }
}

// Log response details for debugging
export function logResponse(response, name = 'response') {
  console.log(`[${name}] Status: ${response.status}, Duration: ${response.timings.duration}ms`);
}
```

### 4. Common Checks (`tests/load/lib/checks.js`)

```javascript
// Common check patterns for k6 tests
import { check } from 'k6';

// Check HTTP 200 response
export function checkOk(response, name = 'request') {
  return check(response, {
    [`${name} status is 200`]: (r) => r.status === 200,
  });
}

// Check HTTP 2xx response
export function check2xx(response, name = 'request') {
  return check(response, {
    [`${name} status is 2xx`]: (r) => r.status >= 200 && r.status < 300,
  });
}

// Check response time under threshold
export function checkDuration(response, maxMs, name = 'request') {
  return check(response, {
    [`${name} duration < ${maxMs}ms`]: (r) => r.timings.duration < maxMs,
  });
}

// Check JSON response structure
export function checkJsonBody(response, expectedFields, name = 'response') {
  const checks = {};
  checks[`${name} has valid JSON`] = (r) => {
    try {
      JSON.parse(r.body);
      return true;
    } catch {
      return false;
    }
  };

  if (expectedFields && expectedFields.length > 0) {
    checks[`${name} has required fields`] = (r) => {
      const body = JSON.parse(r.body);
      return expectedFields.every(field => field in body);
    };
  }

  return check(response, checks);
}

// Check health endpoint response
export function checkHealthResponse(response) {
  return check(response, {
    'health status is 200': (r) => r.status === 200,
    'health has status field': (r) => {
      const body = JSON.parse(r.body);
      return body.status === 'healthy' || body.status === 'ok';
    },
    'health response time < 100ms': (r) => r.timings.duration < 100,
  });
}
```

### 5. Health Endpoint Tests (`tests/load/scripts/health.js`)

```javascript
// Health Endpoint Load Tests
//
// Tests the /health endpoint to establish baseline performance.
// This is typically the fastest endpoint and serves as a sanity check.
//
// Usage:
//   k6 run tests/load/scripts/health.js
//   k6 run --env BASE_URL=https://api.example.com tests/load/scripts/health.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { BASE_URL, API_PREFIX } from '../lib/config.js';
import { checkHealthResponse } from '../lib/checks.js';

// Custom metrics
const healthCheckErrors = new Rate('health_check_errors');
const healthCheckDuration = new Trend('health_check_duration');

// Test configuration
export const options = {
  scenarios: {
    health_check: {
      executor: 'constant-vus',
      vus: __ENV.VUS ? parseInt(__ENV.VUS) : 10,
      duration: __ENV.DURATION || '1m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<100', 'p(99)<200'],
    http_req_failed: ['rate<0.001'],
    health_check_errors: ['rate<0.001'],
    health_check_duration: ['p(95)<100'],
  },
  tags: {
    test_type: 'health',
  },
};

// Test setup (runs once per VU)
export function setup() {
  console.log(`Testing health endpoint at: ${BASE_URL}${API_PREFIX}/health`);

  // Verify endpoint is accessible
  const response = http.get(`${BASE_URL}${API_PREFIX}/health`);
  if (response.status !== 200) {
    throw new Error(`Health endpoint not accessible: ${response.status}`);
  }

  return { startTime: new Date().toISOString() };
}

// Main test function (runs repeatedly)
export default function() {
  const response = http.get(`${BASE_URL}${API_PREFIX}/health`, {
    tags: { name: 'health' },
  });

  // Record custom metrics
  healthCheckDuration.add(response.timings.duration);
  healthCheckErrors.add(response.status !== 200);

  // Run checks
  checkHealthResponse(response);

  // Small pause between requests
  sleep(0.1);
}

// Teardown (runs once at end)
export function teardown(data) {
  console.log(`Test completed. Started at: ${data.startTime}`);
}
```

### 6. Public API Tests (`tests/load/scripts/api-public.js`)

```javascript
// Public API Endpoint Load Tests
//
// Tests unauthenticated API endpoints.
// Focuses on publicly accessible endpoints like health, OpenAPI schema.
//
// Usage:
//   k6 run tests/load/scripts/api-public.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { BASE_URL, API_PREFIX, defaultOptions } from '../lib/config.js';
import { checkOk, checkJsonBody, checkDuration } from '../lib/checks.js';
import { thinkTime } from '../lib/helpers.js';

// Custom metrics
const apiErrors = new Rate('api_errors');
const requestCount = new Counter('request_count');

// Test configuration
export const options = {
  scenarios: {
    public_api: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 10 },  // Warm up
        { duration: '2m', target: 30 },   // Normal load
        { duration: '30s', target: 0 },   // Cool down
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    api_errors: ['rate<0.01'],
  },
  tags: {
    test_type: 'api_public',
  },
};

export function setup() {
  console.log(`Testing public API at: ${BASE_URL}${API_PREFIX}`);
  return { baseUrl: BASE_URL, apiPrefix: API_PREFIX };
}

export default function(data) {
  // Test health endpoint
  group('health', function() {
    const response = http.get(`${BASE_URL}${API_PREFIX}/health`, {
      ...defaultOptions,
      tags: { name: 'health', endpoint: 'health' },
    });

    requestCount.add(1);
    apiErrors.add(response.status !== 200);

    check(response, {
      'health: status 200': (r) => r.status === 200,
      'health: has status field': (r) => {
        const body = JSON.parse(r.body);
        return 'status' in body;
      },
    });
  });

  thinkTime(0.5, 1);

  // Test OpenAPI schema endpoint
  group('openapi', function() {
    const response = http.get(`${BASE_URL}/openapi.json`, {
      ...defaultOptions,
      tags: { name: 'openapi', endpoint: 'openapi' },
    });

    requestCount.add(1);
    apiErrors.add(response.status !== 200);

    check(response, {
      'openapi: status 200': (r) => r.status === 200,
      'openapi: valid JSON': (r) => {
        try {
          JSON.parse(r.body);
          return true;
        } catch {
          return false;
        }
      },
      'openapi: has paths': (r) => {
        const body = JSON.parse(r.body);
        return 'paths' in body;
      },
    });
  });

  thinkTime(0.5, 1);

  // Test root endpoint (if exists)
  group('root', function() {
    const response = http.get(`${BASE_URL}/`, {
      ...defaultOptions,
      tags: { name: 'root', endpoint: 'root' },
    });

    requestCount.add(1);
    // Root may redirect or return various codes, so we're lenient
    apiErrors.add(response.status >= 500);

    check(response, {
      'root: not server error': (r) => r.status < 500,
    });
  });

  thinkTime(1, 2);
}

export function teardown(data) {
  console.log('Public API test completed');
}
```

### 7. Smoke Test Scenario (`tests/load/scenarios/smoke.js`)

```javascript
// Smoke Test Scenario
//
// Quick validation test to ensure the application is working.
// Run before more intensive tests to catch obvious issues.
//
// Usage:
//   k6 run tests/load/scenarios/smoke.js
//   ./scripts/load-test.sh smoke

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, API_PREFIX } from '../lib/config.js';
import { scenarios } from '../k6.config.js';

export const options = {
  ...scenarios.smoke,
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
    checks: ['rate>0.99'],  // 99% of checks must pass
  },
  tags: {
    test_type: 'smoke',
    scenario: 'smoke',
  },
};

export default function() {
  // Test 1: Health check
  const healthRes = http.get(`${BASE_URL}${API_PREFIX}/health`);
  check(healthRes, {
    'health endpoint accessible': (r) => r.status === 200,
    'health returns healthy status': (r) => {
      const body = JSON.parse(r.body);
      return body.status === 'healthy' || body.status === 'ok';
    },
  });

  sleep(1);

  // Test 2: OpenAPI spec accessible
  const openApiRes = http.get(`${BASE_URL}/openapi.json`);
  check(openApiRes, {
    'openapi accessible': (r) => r.status === 200,
    'openapi valid JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch {
        return false;
      }
    },
  });

  sleep(1);
}

export function handleSummary(data) {
  console.log('\n=== Smoke Test Summary ===');
  console.log(`Total Requests: ${data.metrics.http_reqs.values.count}`);
  console.log(`Failed Requests: ${data.metrics.http_req_failed.values.rate * 100}%`);
  console.log(`Avg Duration: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms`);
  console.log(`P95 Duration: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms`);

  const passed = data.metrics.checks.values.rate >= 0.99;
  console.log(`\nStatus: ${passed ? 'PASSED' : 'FAILED'}`);

  return {
    'stdout': '',  // Already logged above
  };
}
```

### 8. Load Test Scenario (`tests/load/scenarios/load.js`)

```javascript
// Load Test Scenario
//
// Normal expected load test to validate performance under typical conditions.
// Ramps up to target VUs, holds steady, then ramps down.
//
// Usage:
//   k6 run tests/load/scenarios/load.js
//   k6 run --env VUS=100 --env DURATION=10m tests/load/scenarios/load.js
//   ./scripts/load-test.sh load

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';
import { BASE_URL, API_PREFIX, defaultOptions } from '../lib/config.js';
import { scenarios } from '../k6.config.js';
import { thinkTime } from '../lib/helpers.js';

// Custom metrics for detailed analysis
const errorRate = new Rate('error_rate');
const healthDuration = new Trend('health_duration', true);
const apiDuration = new Trend('api_duration', true);

// Allow VU count override via environment
const targetVUs = __ENV.VUS ? parseInt(__ENV.VUS) : 50;

export const options = {
  scenarios: {
    load_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: targetVUs },     // Ramp up
        { duration: __ENV.DURATION || '5m', target: targetVUs },  // Steady state
        { duration: '2m', target: 0 },             // Ramp down
      ],
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    error_rate: ['rate<0.01'],
    health_duration: ['p(95)<100'],
    api_duration: ['p(95)<500'],
    checks: ['rate>0.95'],
  },
  tags: {
    test_type: 'load',
    scenario: 'load',
    target_vus: String(targetVUs),
  },
};

export function setup() {
  console.log(`\n=== Load Test Configuration ===`);
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Target VUs: ${targetVUs}`);
  console.log(`Duration: ${__ENV.DURATION || '5m'} (steady state)`);

  // Verify system is ready
  const healthCheck = http.get(`${BASE_URL}${API_PREFIX}/health`);
  if (healthCheck.status !== 200) {
    throw new Error(`System not ready: health check returned ${healthCheck.status}`);
  }

  return {
    startTime: new Date().toISOString(),
    targetVUs: targetVUs,
  };
}

export default function() {
  // Health check (lightweight, frequent)
  group('health', function() {
    const response = http.get(`${BASE_URL}${API_PREFIX}/health`, {
      tags: { name: 'health' },
    });

    healthDuration.add(response.timings.duration);
    errorRate.add(response.status !== 200);

    check(response, {
      'health: status 200': (r) => r.status === 200,
    });
  });

  thinkTime(1, 2);

  // API endpoint (heavier, less frequent)
  group('api', function() {
    const response = http.get(`${BASE_URL}/openapi.json`, {
      ...defaultOptions,
      tags: { name: 'openapi' },
    });

    apiDuration.add(response.timings.duration);
    errorRate.add(response.status !== 200);

    check(response, {
      'openapi: status 200': (r) => r.status === 200,
    });
  });

  thinkTime(2, 4);
}

export function teardown(data) {
  console.log(`\n=== Load Test Complete ===`);
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
}

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    scenario: 'load',
    targetVUs: data.options?.scenarios?.load_test?.stages?.[1]?.target || 'unknown',
    metrics: {
      requests: data.metrics.http_reqs?.values?.count || 0,
      errorRate: (data.metrics.http_req_failed?.values?.rate || 0) * 100,
      duration: {
        avg: data.metrics.http_req_duration?.values?.avg || 0,
        p95: data.metrics.http_req_duration?.values?.['p(95)'] || 0,
        p99: data.metrics.http_req_duration?.values?.['p(99)'] || 0,
      },
    },
    passed: data.metrics.checks?.values?.rate >= 0.95,
  };

  return {
    'results/load-test-summary.json': JSON.stringify(summary, null, 2),
  };
}
```

### 9. Stress Test Scenario (`tests/load/scenarios/stress.js`)

```javascript
// Stress Test Scenario
//
// Tests system behavior beyond normal load to find breaking points.
// Progressively increases load to identify capacity limits.
//
// Usage:
//   k6 run tests/load/scenarios/stress.js
//   ./scripts/load-test.sh stress

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { BASE_URL, API_PREFIX, defaultOptions } from '../lib/config.js';
import { thinkTime } from '../lib/helpers.js';

// Custom metrics
const errorRate = new Rate('error_rate');
const requestDuration = new Trend('request_duration', true);
const errorCount = new Counter('error_count');

export const options = {
  scenarios: {
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },   // Ramp to normal load
        { duration: '3m', target: 50 },   // Hold normal
        { duration: '2m', target: 100 },  // Ramp to high load
        { duration: '3m', target: 100 },  // Hold high
        { duration: '2m', target: 150 },  // Ramp to stress
        { duration: '3m', target: 150 },  // Hold stress
        { duration: '2m', target: 200 },  // Ramp to breaking point
        { duration: '3m', target: 200 },  // Hold breaking point
        { duration: '5m', target: 0 },    // Recovery
      ],
    },
  },
  thresholds: {
    // More lenient thresholds for stress testing
    http_req_duration: ['p(95)<2000'],  // Allow up to 2s under stress
    http_req_failed: ['rate<0.10'],     // Allow up to 10% errors under stress
    checks: ['rate>0.80'],              // 80% checks must pass
  },
  tags: {
    test_type: 'stress',
    scenario: 'stress',
  },
};

export function setup() {
  console.log(`\n=== Stress Test Configuration ===`);
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Peak VUs: 200`);
  console.log(`Total Duration: ~25 minutes`);
  console.log(`Purpose: Find breaking points and observe recovery\n`);

  return { startTime: new Date().toISOString() };
}

export default function() {
  const response = http.get(`${BASE_URL}${API_PREFIX}/health`, {
    tags: { name: 'health' },
    timeout: '10s',  // Longer timeout for stress conditions
  });

  requestDuration.add(response.timings.duration);
  errorRate.add(response.status !== 200);

  if (response.status !== 200) {
    errorCount.add(1);
    console.log(`Error: ${response.status} at VU ${__VU}, iteration ${__ITER}`);
  }

  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });

  // Minimal think time during stress testing
  sleep(0.5);
}

export function teardown(data) {
  console.log(`\n=== Stress Test Complete ===`);
  console.log(`Started: ${data.startTime}`);
  console.log(`Ended: ${new Date().toISOString()}`);
}

export function handleSummary(data) {
  const summary = {
    timestamp: new Date().toISOString(),
    scenario: 'stress',
    peakVUs: 200,
    metrics: {
      requests: data.metrics.http_reqs?.values?.count || 0,
      errors: data.metrics.error_count?.values?.count || 0,
      errorRate: (data.metrics.http_req_failed?.values?.rate || 0) * 100,
      duration: {
        avg: data.metrics.http_req_duration?.values?.avg || 0,
        p95: data.metrics.http_req_duration?.values?.['p(95)'] || 0,
        p99: data.metrics.http_req_duration?.values?.['p(99)'] || 0,
        max: data.metrics.http_req_duration?.values?.max || 0,
      },
    },
  };

  return {
    'results/stress-test-summary.json': JSON.stringify(summary, null, 2),
  };
}
```

### 10. Wrapper Script (`scripts/load-test.sh`)

```bash
#!/bin/bash
set -euo pipefail

# {{ cookiecutter.project_name }} - Load Testing Script
#
# Wrapper script for running k6 load tests.
#
# Usage:
#   ./scripts/load-test.sh [scenario] [options]
#
# Scenarios:
#   smoke   - Quick validation (1 VU, 1 minute)
#   load    - Normal load test (50 VUs, 5 minutes)
#   stress  - Stress test to find breaking points
#   soak    - Extended duration test (20 VUs, 30 minutes)
#   health  - Health endpoint specific test
#   api     - Public API endpoint test
#
# Options:
#   --vus N        Override virtual users count
#   --duration T   Override duration (e.g., 5m, 1h)
#   --base-url U   Override base URL
#   --output F     Output results to file
#   --help         Show this help message
#
# Examples:
#   ./scripts/load-test.sh smoke
#   ./scripts/load-test.sh load --vus 100 --duration 10m
#   ./scripts/load-test.sh stress --base-url https://staging.example.com

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TESTS_DIR="$PROJECT_ROOT/tests/load"
RESULTS_DIR="$PROJECT_ROOT/tests/load/results"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Default values
SCENARIO="${1:-smoke}"
BASE_URL="${BASE_URL:-http://localhost:{{ cookiecutter.backend_port }}}"
VUS=""
DURATION=""
OUTPUT_FILE=""

# Parse arguments
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --vus)
            VUS="$2"
            shift 2
            ;;
        --duration)
            DURATION="$2"
            shift 2
            ;;
        --base-url)
            BASE_URL="$2"
            shift 2
            ;;
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --help)
            head -40 "$0" | tail -35
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Check k6 is installed
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}Error: k6 is not installed${NC}"
    echo ""
    echo "Install k6:"
    echo "  macOS:   brew install k6"
    echo "  Ubuntu:  sudo gpg -k && sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69"
    echo "           echo 'deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main' | sudo tee /etc/apt/sources.list.d/k6.list"
    echo "           sudo apt-get update && sudo apt-get install k6"
    echo "  Docker:  docker run --rm -i grafana/k6 run -"
    exit 1
fi

# Create results directory
mkdir -p "$RESULTS_DIR"

# Determine test file
case $SCENARIO in
    smoke)
        TEST_FILE="$TESTS_DIR/scenarios/smoke.js"
        ;;
    load)
        TEST_FILE="$TESTS_DIR/scenarios/load.js"
        ;;
    stress)
        TEST_FILE="$TESTS_DIR/scenarios/stress.js"
        ;;
    soak)
        TEST_FILE="$TESTS_DIR/scenarios/soak.js"
        ;;
    health)
        TEST_FILE="$TESTS_DIR/scripts/health.js"
        ;;
    api)
        TEST_FILE="$TESTS_DIR/scripts/api-public.js"
        ;;
    *)
        # Allow direct file path
        if [[ -f "$SCENARIO" ]]; then
            TEST_FILE="$SCENARIO"
        elif [[ -f "$TESTS_DIR/$SCENARIO" ]]; then
            TEST_FILE="$TESTS_DIR/$SCENARIO"
        else
            echo -e "${RED}Unknown scenario: $SCENARIO${NC}"
            echo "Available scenarios: smoke, load, stress, soak, health, api"
            exit 1
        fi
        ;;
esac

if [[ ! -f "$TEST_FILE" ]]; then
    echo -e "${RED}Test file not found: $TEST_FILE${NC}"
    exit 1
fi

# Build k6 command
K6_CMD="k6 run"
K6_ENV=""

# Add environment variables
K6_ENV="$K6_ENV --env BASE_URL=$BASE_URL"
[[ -n "$VUS" ]] && K6_ENV="$K6_ENV --env VUS=$VUS"
[[ -n "$DURATION" ]] && K6_ENV="$K6_ENV --env DURATION=$DURATION"

# Add output options
if [[ -n "$OUTPUT_FILE" ]]; then
    K6_CMD="$K6_CMD --out json=$RESULTS_DIR/$OUTPUT_FILE"
fi

echo -e "${BLUE}=== {{ cookiecutter.project_name }} Load Testing ===${NC}"
echo ""
echo -e "${YELLOW}Scenario:${NC}  $SCENARIO"
echo -e "${YELLOW}Test File:${NC} $TEST_FILE"
echo -e "${YELLOW}Base URL:${NC}  $BASE_URL"
[[ -n "$VUS" ]] && echo -e "${YELLOW}VUs:${NC}       $VUS"
[[ -n "$DURATION" ]] && echo -e "${YELLOW}Duration:${NC}  $DURATION"
echo ""

# Run the test
echo -e "${GREEN}Starting test...${NC}"
echo ""

$K6_CMD $K6_ENV "$TEST_FILE"

echo ""
echo -e "${GREEN}Test complete.${NC}"

# Show results location if output was specified
if [[ -n "$OUTPUT_FILE" ]]; then
    echo -e "Results saved to: ${BLUE}$RESULTS_DIR/$OUTPUT_FILE${NC}"
fi
```

### 11. Load Testing README (`tests/load/README.md`)

```markdown
# Load Testing

This directory contains k6 load testing scripts for {{ cookiecutter.project_name }}.

## Prerequisites

### Install k6

**macOS:**
```bash
brew install k6
```

**Ubuntu/Debian:**
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
    sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update && sudo apt-get install k6
```

**Docker:**
```bash
docker run --rm -i grafana/k6 run -
```

## Quick Start

```bash
# Run smoke test (quick validation)
./scripts/load-test.sh smoke

# Run load test (normal traffic)
./scripts/load-test.sh load

# Run with custom options
./scripts/load-test.sh load --vus 100 --duration 10m

# Test against staging
./scripts/load-test.sh smoke --base-url https://staging.example.com
```

## Test Scenarios

| Scenario | Description | VUs | Duration |
|----------|-------------|-----|----------|
| `smoke` | Quick validation | 1 | 1 minute |
| `load` | Normal expected load | 50 | 5 minutes |
| `stress` | Find breaking points | Up to 200 | 25 minutes |
| `soak` | Extended reliability | 20 | 30 minutes |

### Smoke Test
Minimal test to verify the system is responding. Run before other tests.

```bash
./scripts/load-test.sh smoke
```

### Load Test
Simulates normal expected traffic patterns. Use to validate performance meets SLAs.

```bash
./scripts/load-test.sh load
./scripts/load-test.sh load --vus 100  # Higher load
```

### Stress Test
Progressively increases load to find system limits and breaking points.

```bash
./scripts/load-test.sh stress
```

### Soak Test
Extended duration test to find memory leaks and resource exhaustion issues.

```bash
./scripts/load-test.sh soak
```

## Directory Structure

```
tests/load/
  k6.config.js           # Shared configuration
  scenarios/             # Test scenarios
    smoke.js             # Quick validation
    load.js              # Normal load
    stress.js            # Breaking points
    soak.js              # Extended duration
  scripts/               # Endpoint-specific tests
    health.js            # Health endpoint
    api-public.js        # Public API endpoints
    api-authenticated.js # Authenticated endpoints
  lib/                   # Shared utilities
    config.js            # Configuration
    helpers.js           # Helper functions
    checks.js            # Common checks
  results/               # Test output (gitignored)
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | API base URL | `http://localhost:{{ cookiecutter.backend_port }}` |
| `VUS` | Virtual users count | Scenario-specific |
| `DURATION` | Test duration | Scenario-specific |
| `ENVIRONMENT` | Environment tag | `local` |

### Command Line Options

```bash
./scripts/load-test.sh <scenario> [options]

Options:
  --vus N        Override virtual users
  --duration T   Override duration (e.g., 5m, 1h)
  --base-url U   Override base URL
  --output F     Save results to file
  --help         Show help
```

## Thresholds

Default performance thresholds:

| Metric | Threshold | Description |
|--------|-----------|-------------|
| `http_req_duration` | p95 < 500ms | 95th percentile response time |
| `http_req_failed` | rate < 1% | Error rate |
| `checks` | rate > 95% | Check pass rate |

## Viewing Results

### Console Output
k6 outputs summary statistics after each run.

### JSON Output
Save detailed results for analysis:
```bash
./scripts/load-test.sh load --output results.json
```

### Grafana Dashboard (Optional)
With the observability stack enabled, stream results to Grafana:
```bash
k6 run --out influxdb=http://localhost:8086/k6 tests/load/scenarios/load.js
```

## Writing Custom Tests

Create new test files in `scripts/` or `scenarios/`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, API_PREFIX } from '../lib/config.js';

export const options = {
  vus: 10,
  duration: '5m',
  thresholds: {
    http_req_duration: ['p(95)<500'],
  },
};

export default function() {
  const response = http.get(`${BASE_URL}${API_PREFIX}/your-endpoint`);
  check(response, {
    'status is 200': (r) => r.status === 200,
  });
  sleep(1);
}
```

## Troubleshooting

### Connection Refused
Ensure the backend is running:
```bash
./scripts/docker-dev.sh up
```

### High Error Rate
- Check backend logs: `docker compose logs backend`
- Reduce VU count: `--vus 10`
- Check resource limits: `docker stats`

### Slow Response Times
- Check database connections: `docker compose exec postgres pg_stat_activity`
- Monitor Redis: `docker compose exec redis redis-cli info`
- Check for N+1 queries in logs

## Related Documentation

- [k6 Documentation](https://k6.io/docs/)
- [Performance Baselines](../../docs/performance-baselines.md)
- [ADR-XXX: Load Testing Strategy](../../docs/adr/)
```

## Success Criteria

### Functional Requirements
- [ ] FR-DX-004: k6 load testing scripts included for key endpoints
- [ ] FR-DX-006: Scripts are configurable for virtual users and duration
- [ ] Smoke test completes successfully against running backend
- [ ] Load test can run with configurable VU count
- [ ] Stress test identifies system limits

### Verification Steps
1. **Installation Check:**
   ```bash
   # Verify k6 is installed
   k6 version
   ```

2. **Smoke Test:**
   ```bash
   # Start backend
   ./scripts/docker-dev.sh up

   # Run smoke test
   ./scripts/load-test.sh smoke
   # Should complete with 0 errors
   ```

3. **Load Test with Custom Config:**
   ```bash
   ./scripts/load-test.sh load --vus 20 --duration 2m
   # Should complete and show metrics
   ```

4. **Configuration Validation:**
   ```bash
   # Check thresholds are enforced
   k6 run tests/load/scenarios/smoke.js
   # Should show pass/fail for each threshold
   ```

### Quality Gates
- [ ] All test files have valid JavaScript syntax
- [ ] Wrapper script has proper error handling
- [ ] README documents installation and usage
- [ ] Configurable via environment variables
- [ ] Results can be saved to file
- [ ] Thresholds are defined for each scenario

## Integration Points

### Upstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| None | - | Independent task |

### Downstream Dependencies
| Task | Contract | Notes |
|------|----------|-------|
| P5-03 | k6 structure | Auth tests extend this foundation |
| P5-05 | Test results | Baselines use k6 output format |
| P6-01 | Commands | CLAUDE.md documents load test commands |

### Integration Contract
```yaml
# Contract: k6 Load Testing Structure

# Test directory structure
tests/load/
  k6.config.js              # Shared configuration
  scenarios/                # Scenario presets
  scripts/                  # Endpoint tests
  lib/                      # Shared utilities
  results/                  # Output (gitignored)

# Wrapper script
./scripts/load-test.sh <scenario> [options]

# Available scenarios
- smoke: Quick validation (1 VU, 1 min)
- load: Normal load (50 VUs, 5 min)
- stress: Breaking points (200 VUs peak)
- soak: Extended (20 VUs, 30 min)

# Environment variables
BASE_URL: API base URL
VUS: Override virtual users
DURATION: Override duration

# Output format
JSON summary with metrics and thresholds
```

## Monitoring and Observability

### Test Metrics
- Request count and rate
- Response time percentiles (p50, p95, p99)
- Error rate and error types
- Virtual user count over time

### Integration with Observability Stack
When `include_observability: yes`:
- Stream results to InfluxDB for Grafana visualization
- Correlate load test with application metrics
- Monitor backend resource usage during tests

## Infrastructure Needs

### Development Requirements
- k6 installed locally (or via Docker)
- Backend running (for test target)
- 4GB+ RAM for stress tests

### CI Requirements (Future Enhancement)
- k6 available in CI environment
- Backend service running
- Results storage for comparison

## Estimated Effort

**Size:** M (Medium)
**Time:** 1-2 days
**Justification:**
- k6 configuration is straightforward
- Multiple scenario files needed
- Wrapper script with options
- Documentation requirements
- Testing across scenarios

## Notes

### Design Decisions

**1. k6 Over Alternatives:**
- JavaScript-based (familiar to frontend devs)
- Low resource consumption (Go-based)
- Built-in thresholds and checks
- Good documentation and community

**2. Scenario-Based Structure:**
- Clear separation of test types
- Easy to run specific scenarios
- Consistent configuration

**3. Shared Library:**
- Reduces code duplication
- Centralized configuration
- Easier maintenance

### Alternatives Considered

| Tool | Pros | Cons |
|------|------|------|
| k6 | JavaScript, lightweight | No GUI |
| Locust | Python, distributed | More complex setup |
| Artillery | YAML config | Less flexible |
| JMeter | Full-featured | Java, resource heavy |

### Related Requirements
- FR-DX-004: k6 load testing scripts for key endpoints
- FR-DX-006: Configurable virtual users and duration
- US-5.2: Load testing scripts for performance validation
