# Yatzy Backend

REST API for a Yatzy game. Tracks players, games, dice rolls and scores. Implements Swedish Maxi Yatzy rules (6 dice, up to 3 rolls per turn, unused rolls can be saved).

Built with FastAPI + MySQL (no ORM), Python 3.14, Docker.

## Getting started

From the repo root:

```bash
make backend/dev
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## Development

All commands run from the repo root.

```bash
make backend/format     # auto-fix formatting and lint issues
make backend/lint       # check formatting and lint
make backend/types      # type check
make backend/security   # security scan
make backend/unit       # unit tests
make backend/e2e        # e2e tests (starts and stops db-test automatically)
make backend/check      # lint + types + security + all tests

make backend/shell      # open a shell in the backend container
make backend/db         # open a MySQL shell
make backend/migrate    # run database migrations
```
