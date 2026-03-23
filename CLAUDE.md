**Monorepo structure**
- `backend/` — REST API (Python / FastAPI / MySQL). See `backend/CLAUDE.md`.
- `frontend/` — Web client (TypeScript / React / Vite). See `frontend/CLAUDE.md`.

**Docker and make**
- Single `docker-compose.yml` at the repo root with all services.
- Single `Makefile` at the repo root with all targets, namespaced by package: `make backend/dev`, `make frontend/check`, `make backend/e2e`, etc.
- Top-level targets: `dev` (full stack foreground), `start` (detached), `stop`, `logs`, `ps`, `clean` (down), `build`, `rebuild`, `check` (all quality checks), `release-patch/minor/major`.
- Always run `make` from the repo root.

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
- Regenerate the frontend API client after backend changes: `make frontend/schema` (starts the backend automatically if not running)
