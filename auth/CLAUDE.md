**Monorepo**
This is the `auth/` package in the Yatzy monorepo.

**Goal**
A dedicated authentication service. Issues JWTs for email/password login. Isolated from the game backend.

**Tools**
- Language: Python 3.14
- Packages: FastAPI (with Pydantic and aiomysql), PyJWT, passlib[bcrypt]. No ORM.
- Dev packages: Ruff for lint and code formatting. Ty for static type checking.
- Always build and run using Docker via `make` targets — never raw `docker compose` or `uvicorn` commands. Run from `auth/` or using `make -C auth <target>` from the repo root. Key targets: `dev`, `shell`, `migrate`, `build`, `rebuild`, `format`, `lint`, `types`, `security`, `unit`, `unit-cov`, `e2e`, `e2e-cov`, `test`, `coverage`, `check`.
- Compose files: `docker-compose.yml` (base/prod), `docker-compose.dev.yml` (dev overrides), `docker-compose.test.yml` (test environment).
- Use uv for package management.
- Configure project using pyproject.toml.

**Design rules**
- Same patterns as `backend/`: factory-function routers, dependency injection, repository pattern, raw SQL.
- Soft deletes on the `users` table (`deleted_at`).
- Refresh tokens stored hashed (SHA-256) in the database for server-side revocation.
- Token rotation: each refresh issues a new pair and revokes the old token.

**Code Style**
- Two space indent
- Single quotes
