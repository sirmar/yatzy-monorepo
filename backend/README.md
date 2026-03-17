# Purpose
The purpose of this project is not to write another yatzy service but to practice using AI-assisted
  development. All code, infrastructure and commits will be done with the AI tool. The only thing written directly by me is this paragraph as well as the CLAUDE.md file.

# Yatzy Backend

REST API backend for a Yatzy game. Tracks players, games, dice rolls and scores. Implements Swedish Maxi Yatzy rules (6 dice, up to 3 rolls per turn, unused rolls can be saved).

Built with FastAPI + MySQL (no ORM), Python 3.14, Docker.

## Running the service

```bash
cp .env.example .env
docker compose up
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## Running tests

E2e tests require the test database:

```bash
docker compose up db-test -d
```

```bash
# Unit tests
uv run pytest tests/unit/ -v

# E2e tests
uv run pytest tests/e2e/ -v

# All tests with coverage
uv run pytest tests/ -v --cov=app
uv run coverage report --show-missing
```

## Lint and type checking

```bash
uv run ruff check app/     # lint
uv run ruff format app/    # format
uv run ty check app/       # type check
```

## Development setup

Requires Python 3.14 and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --extra dev
```
