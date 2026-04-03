# Yatzy Auth Service

Dedicated authentication service for the Yatzy monorepo. Issues JWTs for email/password login, isolated from the game backend.

**Stack:** Python 3.14, FastAPI, MySQL (aiomysql), PyJWT, passlib[bcrypt]

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/register` | Register user, sends verification email |
| POST | `/verify-email` | Verify email, returns token pair |
| POST | `/login` | Login, returns token pair |
| POST | `/refresh` | Rotate refresh token, returns new token pair |
| POST | `/logout` | Revoke refresh token |
| POST | `/forgot-password` | Send password reset email |
| POST | `/reset-password` | Reset password, revokes all refresh tokens |
| PUT | `/password` | Change password (authenticated) |
| GET | `/me` | Get current user (authenticated) |
| DELETE | `/me` | Delete account (authenticated) |

Runs on port **8001**. Interactive docs at `http://localhost:8001/docs`.

## Token design

- **Access token** — short-lived JWT (15 min), verified by consumers via shared `JWT_SECRET`
- **Refresh token** — opaque token stored as SHA-256 hash in DB, rotated on each use (30 days)
- Email verification and password reset tokens are also stored hashed with expiry

## Dev setup

```bash
make dev        # start service + DB with hot reload
make migrate    # run pending migrations
make shell      # bash shell inside app container
```

## Testing

```bash
make unit         # unit tests
make e2e          # end-to-end tests (spins up test DB)
make test         # unit + e2e
make fast-check   # lint + types + security + unit (no e2e)
make check        # fast-check + e2e
```

## Configuration

Environment variables (`.env` file or Docker env):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `mysql://root:root@auth-db:3306/yatzy_auth` | MySQL connection string |
| `JWT_SECRET` | *(change in prod)* | Signing secret for JWTs |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token TTL |
| `EMAIL_VERIFICATION_EXPIRE_MINUTES` | `60` | Email verification token TTL |
| `PASSWORD_RESET_EXPIRE_MINUTES` | `30` | Password reset token TTL |
| `APP_ENV` | `dev` | Environment (`dev`/`test`/`prod`) |

In `dev`/`test`, a `/dev/*` router is mounted with test helpers (e.g. creating verified users directly).
