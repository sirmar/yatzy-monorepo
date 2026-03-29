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

Run from `frontend/` (or `make -C frontend <target>` from the repo root).

```bash
make format     # auto-fix formatting and lint issues
make lint       # check formatting and lint
make types      # type check
make unit       # unit tests
make check      # lint + types + unit

make schema     # regenerate API client from backend OpenAPI schema (requires backend on port 8000)
make auth-schema  # regenerate auth client (requires auth on port 8001)
```
