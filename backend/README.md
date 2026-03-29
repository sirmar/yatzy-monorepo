# Yatzy Backend

REST API for a Yatzy game. Tracks players, games, dice rolls and scores. Implements Swedish Maxi Yatzy rules (6 dice, up to 3 rolls per turn, unused rolls can be saved).

Built with FastAPI + MySQL (no ORM), Python 3.14, Docker.

## Getting started

From `backend/`:

```bash
make dev
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## Development

Run from `backend/` (or `make -C backend <target>` from the repo root).

```bash
make format     # auto-fix formatting and lint issues
make lint       # check formatting and lint
make types      # type check
make security   # security scan
make unit       # unit tests
make e2e        # e2e tests (starts and stops db-test automatically)
make check      # lint + types + security + all tests

make shell      # open a shell in the backend container
make db         # open a MySQL shell
make migrate    # run database migrations
```
