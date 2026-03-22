# Yatzy Frontend

Web client for the Yatzy game. Allows players to create and join games, roll dice, fill in scorecards and see results.

Built with React + Vite + TypeScript, served via Nginx in production.

## Getting started

From the repo root (requires the backend to be running):

```bash
make dev
```

- Frontend: http://localhost:5173

## Development

All commands run from the repo root.

```bash
make frontend/format    # auto-fix formatting and lint issues
make frontend/lint      # check formatting and lint
make frontend/types     # type check
make frontend/unit      # unit tests
make frontend/e2e       # smoke tests against the production build
make frontend/check     # lint + types + unit + e2e

make frontend/schema    # regenerate API client from backend OpenAPI schema
```
