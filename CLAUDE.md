**Packages:** `backend/` (FastAPI/MySQL), `auth/` (FastAPI/MySQL, issues JWTs), `frontend/` (React/Vite), `bot/` (FastAPI, plays autonomously), `cli/` (terminal client, `dev run` to play). Each has its own `CLAUDE.md`.

**Dev:** Always use `dev <command>` from inside the package dir — never raw `docker compose` or `uvicorn`. Migrations: `dev db-migrate` (never automatic). E2E (Playwright) tests in `e2e/` at repo root.

**Deploy:** `docker-compose.prod.yml` via a local Docker context pointing at the server. Run migrations then `dev up` against the prod context.

**Domain:** Multiple Yatzy variants (Maxi, standard, etc.) — dice-based, turn-based, 1–6 players. See each variant's rules for scoring details. Creator starts the game after others join.

**Cross-package:** After backend changes run `dev exec schema` from `frontend/`. After auth changes run `dev exec auth-schema` from `frontend/` (requires the respective service on the yatzy network).

**Code:** No comments. No auto-generated READMEs.
