**Monorepo structure**
- `backend/` — REST API (Python / FastAPI / MySQL). See `backend/CLAUDE.md`.
- `auth/` — Authentication service (Python / FastAPI / MySQL). Issues JWTs for email/password login. See `auth/CLAUDE.md`.
- `frontend/` — Web client (TypeScript / React / Vite). See `frontend/CLAUDE.md`.

**Docker and make**
- Each package (`backend/`, `auth/`, `frontend/`) has its own `docker-compose.yml` and `Makefile`.
- Root `docker-compose.yml` is for full-stack dev only (no test/prod services).
- Root `Makefile` has aggregate targets only: `dev`, `start`, `stop`, `logs`, `ps`, `clean`, `migrate`, `build`, `e2e`, `check`, `prod-up`, `prod-down`, `prod-migrate`, `release-patch/minor/major`.
- Sub-repo Makefiles are self-contained — run `make <target>` from inside the package directory, or `make -C <pkg> <target>` from the root.
- Migrations are explicit: `make migrate` at root (dev) or `make prod-migrate` (prod). Never automatic.
- Always run with Docker — never raw `docker compose` or `uvicorn` commands directly.
- E2E (Playwright) tests live in `e2e/` at the repo root.

**Deployment**
- Production uses `docker-compose.prod.yml` with images pulled from GHCR. All commands run locally via a Docker context pointing at the server.
- One-time server setup: copy `docker-compose.prod.yml` and `.env.prod.example` to the server, rename to `.env.prod` and fill in secrets.
- One-time local setup: `docker context create prod --docker "host=ssh://user@yourserver"`
- Deploy: `make prod-migrate` (first deploy and after schema changes), then `make prod-up`
- `DC_PROD` in the Makefile hardcodes `--context prod`, so all prod targets automatically target the remote server.

**Git**
- Always commit and push using the `/commit` skill — never raw `git commit`/`git push`
- Never run `/commit` automatically — only commit when explicitly asked

**Documentation**
- Avoid comments in code
- Write tests first
- README.md with repository purpose and developer focused information

**Domain**
- Swedish Maxi Yatzy: 6 dice, up to 3 rolls per turn, unused rolls can be saved for later. Bonus is 100 points at 84 or more in the upper section. Yatzy is worth 100.
- Categories: standard Swedish Maxi Yatzy scoring categories
- 1 to 6 players per game, turn-based
- A player creates a game. Other players list and join. When enough have joined, the creator starts the game.

**Cross-package**
- Regenerate the frontend API client after backend changes: `make schema` from `frontend/` (requires backend running on port 8000).
- Regenerate the frontend auth client after auth service changes: `make auth-schema` from `frontend/` (requires auth running on port 8001).
