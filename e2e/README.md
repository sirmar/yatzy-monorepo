# Yatzy E2E Tests

Full-stack smoke tests using Playwright. Tests run against a live stack (frontend + backend + auth) via a single Nginx entry point.

## Running

From `e2e/`:

```bash
dev e2e
```

This starts all services, runs the tests, and shuts them down.

Tests run in Chromium only. `BASE_URL` defaults to `http://localhost:80`.
