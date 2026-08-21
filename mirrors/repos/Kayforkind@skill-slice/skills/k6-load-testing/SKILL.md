---
name: k6-load-testing
version: 1.1.1
description: "Writes and runs k6 load tests for HTTP APIs, WebSockets, and browser scenarios, covering smoke/load/stress/spike/soak profiles, thresholds, and CI regression. Use when validating SLA budgets or comparing release behavior under synthetic load. Not for WebGL frame-budget tuning (webgl-performance-tuning), Monte Carlo warehouse-query diagnosis, or unit/property tests (fast-check)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# k6 Load Testing

## Overview

k6 is a developer-centric load testing tool for HTTP APIs, WebSocket endpoints, and browser scenarios. This skill covers writing realistic load tests, configuring test scenarios (smoke, load, stress, spike, soak), setting thresholds, analyzing results, and integrating with CI/CD pipelines.

Primary environment: **Windows host with PowerShell**. Commands below are PowerShell-compatible where relevant. Linux/macOS equivalents are noted where they differ.

## When to Use

- Load test HTTP APIs, WebSocket endpoints, or browser scenarios
- Set up performance regression tests in CI/CD pipelines
- Analyze system behavior under various load conditions (smoke, load, stress, spike, soak)
- Compare performance between code changes or releases
- Validate SLA requirements and performance budgets
- Identify bottlenecks and breaking points before deployment

## Prerequisites

1. Install k6 on the Windows host:

```powershell
choco install k6
```

Alternative platforms:

```bash
# macOS
brew install k6

# Linux (Debian/Ubuntu)
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

2. Verify installation:

```powershell
k6 version
```

3. For browser testing, install Chromium support:

```powershell
k6 install chromium
```

4. Never hardcode API keys or passwords in test scripts. Use environment variables:

```powershell
$env:API_TOKEN = "YOUR_KEY"
k6 run --env API_TOKEN=$env:API_TOKEN load-test.js
```

## Procedure

### 1. Create a Basic Test Script

Create `simple-test.js`:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const res = http.get('https://httpbin.test.k6.io/get');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

Run:

```powershell
k6 run simple-test.js
```

### 2. Configure Test Scenarios

Choose the test type based on your goal:

| Type | Use Case | Configuration |
|------|----------|---------------|
| Smoke | Verify basic functionality | 1-5 VUs, short duration |
| Load | Normal expected load | Target VUs based on traffic |
| Stress | Find breaking point | Ramp beyond capacity |
| Spike | Sudden traffic spikes | Rapid increase/decrease |
| Soak | Long-term stability | Extended duration (hours) |

Ramp-up/ramp-down with stages:

```javascript
export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up
    { duration: '1m', target: 100 },   // Stay at 100
    { duration: '30s', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};
```

### 3. Write HTTP API Tests

Basic GET and POST with checks:

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export default function () {
  const getRes = http.get('https://api.example.com/users');

  check(getRes, {
    'GET succeeded': (r) => r.status === 200,
    'has users': (r) => r.json('data.length') > 0,
  });

  const postRes = http.post('https://api.example.com/users',
    JSON.stringify({ name: 'Test User', email: 'test@example.com' }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + __ENV.API_TOKEN,
      },
    }
  );

  check(postRes, {
    'POST succeeded': (r) => r.status === 201,
    'user created': (r) => r.json('id') !== undefined,
  });

  sleep(1);
}
```

Request chaining (login then use token):

```javascript
import http from 'k6/http';
import { check } from 'k6';

export default function () {
  const loginRes = http.post('https://api.example.com/login',
    JSON.stringify({ email: 'test@example.com', password: 'password123' })
  );

  const token = loginRes.json('access_token');

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  const profileRes = http.get('https://api.example.com/profile', { headers });

  check(profileRes, {
    'profile loaded': (r) => r.status === 200,
  });
}
```

### 4. Parameterize with Shared Data

CSV data source:

```javascript
import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';

const users = new SharedArray('users', function () {
  return open('./users.csv').split('\n').slice(1).map(line => {
    const [email, password] = line.split(',');
    return { email, password };
  });
});

export default function () {
  const user = users[__VU % users.length];

  const res = http.post('https://api.example.com/login',
    JSON.stringify({ email: user.email, password: user.password })
  );

  check(res, { 'login successful': (r) => r.status === 200 });
}
```

JSON data source:

```javascript
import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';

const products = new SharedArray('products', function () {
  return JSON.parse(open('./products.json'));
});

export default function () {
  const product = products[Math.floor(Math.random() * products.length)];

  const res = http.get(`https://api.example.com/products/${product.id}`);

  check(res, { 'product found': (r) => r.status === 200 });
}
```

### 5. Write WebSocket Tests

```javascript
import ws from 'k6/ws';
import { check } from 'k6';

export default function () {
  const url = 'wss://echo.websocket.org';

  ws.connect(url, {}, function (socket) {
    socket.on('open', () => {
      console.log('WebSocket connected');
      socket.send('Hello WebSocket');
    });

    socket.on('message', (data) => {
      console.log(`Received: ${data}`);
      check(data, {
        'echo received': (d) => d.includes('Hello'),
      });
    });

    socket.on('close', () => {
      console.log('WebSocket closed');
    });

    socket.setInterval(function () {
      socket.send('ping');
    }, 1000);

    socket.setTimeout(function () {
      socket.close();
    }, 5000);
  });
}
```

### 6. Write Browser Tests (k6 Browser)

Requires `k6 install chromium` first.

```javascript
import { browser } from 'k6/browser';

export const options = {
  scenarios: {
    browser_test: {
      executor: 'constant-vus',
      vus: 5,
      duration: '30s',
      browser: {
        type: 'chromium',
      },
    },
  },
};

export default async function () {
  const page = await browser.newPage();

  try {
    await page.goto('https://example.com');

    const title = await page.title();
    console.log(`Page title: ${title}`);

    await page.click('button[data-testid="submit"]');
    await page.waitForSelector('.success-message');
  } finally {
    await page.close();
  }
}
```

### 7. Set Thresholds and SLA

```javascript
export const options = {
  vus: 50,
  duration: '2m',
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.01'],
    http_reqs: ['rate>100'],
  },
};
```

Advanced thresholds with tagged metrics:

```javascript
export const options = {
  thresholds: {
    http_req_duration: [
      'p(90)<300',
      'p(95)<500',
      'p(99)<1000',
      'avg<200',
    ],
    'http_req_duration{method:GET}': ['p(95)<300'],
  },
};
```

### 8. Add Custom Metrics

```javascript
import http from 'k6/http';
import { Counter, Trend, Rate, Gauge } from 'k6/metrics';

const myCounter = new Counter('api_calls_total');
const responseTime = new Trend('response_time');
const errorRate = new Rate('error_rate');
const activeUsers = new Gauge('active_users');

export default function () {
  const res = http.get('https://api.example.com/data');

  myCounter.add(1);
  responseTime.add(res.timings.duration);
  errorRate.add(res.status !== 200);
  activeUsers.add(__VU);

  http.get('https://api.example.com/users', {
    tags: { endpoint: 'users', env: 'prod' },
  });
}
```

### 9. Run Tests and Collect Output

```powershell
# Text summary (default)
k6 run load-test.js

# JSON output for parsing
k6 run --out json=results.json load-test.js

# InfluxDB output
k6 run --out influxdb=http://localhost:8086/k6 load-test.js

# Prometheus remote write
k6 run --out prometheus=localhost:9090/k6 load-test.js

# Cloud results
k6 run --out cloud load-test.js
```

### 10. Integrate with CI/CD

GitHub Actions (`.github/workflows/load-test.yml`):

```yaml
name: Load Tests

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup k6
        uses: grafana/k6-action@v0.2.0

      - name: Run load test
        env:
          API_TOKEN: ${{ secrets.API_TOKEN }}
        run: k6 run --out json=results.json load-test.js

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: k6-results
          path: results.json

      - name: Check thresholds
        if: failure()
        run: |
          echo "Load test failed thresholds!"
          exit 1
```

GitLab CI (`.gitlab-ci.yml`):

```yaml
load_test:
  image: grafana/k6:latest
  script:
    - k6 run load-test.js
  artifacts:
    when: always
    paths:
      - results.json
    reports:
      junit: results.xml
```

### 11. Interpret Results

| Metric | Description | Good | Warning | Bad |
|--------|-------------|------|---------|-----|
| http_req_duration (p95) | 95th percentile response time | < 300ms | 300-500ms | > 500ms |
| http_req_failed | Error rate | < 0.1% | 0.1-1% | > 1% |
| http_reqs | Requests/sec | Meeting target | Near limit | At limit |
| vus | Virtual users | Stable | Gradual increase | Unexpected spike |

## Examples

### Example 1: Basic API Load Test

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50,
  duration: '2m',
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get('https://api.example.com/users');

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(1);
}
```

### Example 2: Authenticated Test with Data Parameterization

```javascript
import http from 'k6/http';
import { check } from 'k6';
import { SharedArray } from 'k6/data';

const users = new SharedArray('users', function () {
  return JSON.parse(open('./users.json'));
});

export default function () {
  const user = users[__VU % users.length];

  const loginRes = http.post('https://api.example.com/login',
    JSON.stringify({ email: user.email, password: user.password })
  );

  const token = loginRes.json('access_token');

  const headers = { 'Authorization': `Bearer ${token}` };
  const res = http.get('https://api.example.com/profile', { headers });

  check(res, { 'profile loaded': (r) => r.status === 200 });
}
```

## Pitfalls

- **Starting with high VUs**: Always run a smoke test (1-5 VUs) before scaling up. High VUs on an unverified script can produce misleading results or overwhelm the target.
- **Hardcoding secrets**: Never embed API keys, tokens, or passwords in test scripts. Use `__ENV` and pass via `--env` or CI secrets. Example: `Bearer ${__ENV.API_TOKEN}`.
- **Ignoring thresholds**: Thresholds are how k6 signals pass/fail. Without them, a test run always "succeeds" even if performance is unacceptable.
- **No ramp-up**: Sudden full-load VUs can cause artificial failures. Use `stages` to ramp up gradually.
- **Unrealistic data**: Using the same single user for all VUs may hit caches or rate limits. Parameterize with `SharedArray` and real data distributions.
- **Unmonitored tests**: Running load tests without monitoring the target system gives incomplete pictures. Monitor downstream services, databases, and infrastructure simultaneously.
- **Deprecated APIs**: k6 evolves. Check the [k6 documentation](https://k6.io/docs/) for current APIs. The `k6/browser` module import path and browser scenario configuration must match your installed k6 version.
- **Browser tests without Chromium**: `k6 install chromium` must be run before browser tests. Missing this causes a clear startup error.
- **Ignoring `check` failures vs threshold failures**: `check` failures are reported but do not fail the test by default. Threshold failures cause a non-zero exit code. Use both intentionally.
- **Long soak tests without cleanup**: Soak tests can accumulate data in target systems. Ensure test data cleanup or use ephemeral environments.

## Verification

1. Verify k6 is installed:

```powershell
k6 version
```

Expected: prints k6 version and build info.

2. Run a minimal smoke test:

```powershell
k6 run simple-test.js
```

Expected: test completes, prints summary with `http_req_duration`, `http_req_failed`, and check pass rates.

3. Verify thresholds are enforced:

```powershell
k6 run --out json=results.json load-test.js
echo $LASTEXITCODE
```

Expected: exit code `0` if all thresholds pass, non-zero if any threshold fails.

4. Verify CI/CD integration triggers on push or schedule and uploads artifacts.

5. Verify browser support:

```powershell
k6 install chromium
k6 run browser-test.js
```

Expected: Chromium launches, test completes with page interaction logs.

6. Review test scripts for deprecated features and insecure practices before merging.

## Related Skills

- `performance-engineer` — broader performance optimization
- `api-testing-observability-api-mock` — API mocking during testing
- `application-performance-performance-optimization` — performance optimization

## Additional Resources

- [k6 Documentation](https://k6.io/docs/)
- [k6 Examples](https://github.com/grafana/k6/tree/master/examples)
- [k6 Load Testing Guides](https://k6.io/guides/)
- [k6 Cloud](https://k6.io/cloud/)

## Limitations

- Use this skill only when the task clearly matches load/performance testing scope.
- Do not treat output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.
