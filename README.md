# Yatzy

A Swedish Maxi Yatzy game built with FastAPI + React.

> The purpose of this project is to practice AI-assisted development. All code, infrastructure and commits are done with an AI tool.

## Structure

- [`backend/`](backend/) — REST API (Python / FastAPI / MySQL)
- [`auth/`](auth/) — Authentication service (Python / FastAPI / MySQL)
- [`frontend/`](frontend/) — Web client (TypeScript / React / Vite)
- [`cli/`](cli/) — Interactive terminal client (Python)
- [`bot/`](bot/) — AI bot service (Python / FastAPI)
- [`e2e/`](e2e/) — Full-stack Playwright smoke tests

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (includes Docker Compose)

## Getting started

```bash
mdev up                  # start full stack with hot reload
mdev db-migrate          # first time only: run database migrations
sh auth/scripts/seed.sh  # first time only: create a verified dev account (dev@example.com / devpassword123)
```

To play via the terminal client (after the stack is running):

```bash
cd cli && dev run
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Auth: http://localhost:8001
- Bot: http://localhost:8002
- Swagger docs: http://localhost:8000/docs

## Development

Run `mdev` commands from the repo root, `dev` commands from within a package directory.

```bash
mdev up       # start full stack with hot reload
mdev down     # stop all services
mdev check    # lint + types + tests for all packages
dev e2e       # run full-stack Playwright tests (from e2e/)
```

### Bot

Offline evaluation (from `bot/`):

```bash
dev exec evaluate -- --bot <maxi|yatzy|maxi-sequential|yatzy-sequential>
```

### CLI

```bash
cd cli && dev run   # launch the interactive terminal client (requires stack running)
```

## Deployment

Production uses Docker Compose with images pulled from GHCR. All commands run locally via a Docker context pointing at the server.

### One-time server setup

Copy `docker-compose.prod.yml` and `.env.prod.example` to the server, rename the example to `.env.prod` and fill in the secrets.

### One-time local setup

```bash
docker context create prod --docker "host=ssh://user@yourserver"
```

### Deploy

```bash
docker context use prod
mdev db-migrate   # run on first deploy and after schema changes
mdev up           # pull latest images and start/recreate services
docker context use default
```

### Other prod commands

```bash
docker context use prod
mdev down
docker context use default
```
