# Purpose
The purpose of this project is not to write another yatzy service but to practice using AI-assisted
  development. All code, infrastructure and commits will be done with the AI tool. The only thing written directly by me is this paragraph as well as the CLAUDE.md file.

# Yatzy Backend

REST API backend for a Yatzy game. Tracks players, games, dice rolls and scores. Implements Swedish Maxi Yatzy rules (6 dice, up to 3 rolls per turn, unused rolls can be saved).

Built with FastAPI + MySQL (no ORM), Python 3.14, Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (includes Docker Compose)

## Running the service

```bash
cp .env.example .env
docker compose up
```

- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## Development

```bash
make format     # auto-fix formatting and lint issues
make lint       # check formatting and lint
make types      # type check
make security   # security scan
make unit       # unit tests
make e2e        # e2e tests (starts and stops db-test automatically)
make check      # lint + types + security + all tests
```
