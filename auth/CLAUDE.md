**Monorepo**
This is the `auth/` package in the Yatzy monorepo.

**Goal**
A dedicated authentication service. Issues JWTs for email/password login. Isolated from the game backend.

**Tools**
- Language: Python 3.14
- Packages: FastAPI (with Pydantic and aiomysql), PyJWT, passlib[bcrypt]. No ORM.
- Dev packages: Ruff for lint and code formatting. Ty for static type checking.
- Always build and run using Docker via `make` targets — from the repo root or from `auth/` directly. Never raw `docker compose` or `uvicorn` commands. Key targets: `auth/dev`, `auth/shell`, `auth/build`, `auth/rebuild`, `auth/format`, `auth/lint`, `auth/types`, `auth/security`, `auth/unit`, `auth/unit-cov`, `auth/e2e`, `auth/e2e-cov`, `auth/test`, `auth/coverage`, `auth/check`.
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
