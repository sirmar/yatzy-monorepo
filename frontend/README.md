# Yatzy Frontend

Web client for the Yatzy game. Allows players to create and join games, roll dice, fill in scorecards and see results.

Built with React + Vite + TypeScript, served via Nginx in production.

- Frontend: http://localhost:5173

## Schema generation

Run from `frontend/` after the respective service is running:

```bash
dev exec schema       # regenerate API client from backend OpenAPI schema (requires backend on port 8000)
dev exec auth-schema  # regenerate auth client (requires auth on port 8001)
```
