# Yatzy E2E Tests

Full-stack smoke tests using Playwright. Tests run against a live stack (frontend + backend + auth) via a single Nginx entry point.

## Running

From the repo root:

```bash
make e2e
```

This starts all services, runs the tests, and shuts them down.

## Development

Run from `e2e/` (or `make -C e2e <target>` from the repo root).

```bash
make lint      # check formatting and lint
make format    # auto-fix formatting and lint issues
```

Tests run in Chromium only. `BASE_URL` defaults to `http://localhost:80`.
