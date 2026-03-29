# Yatzy

A Swedish Maxi Yatzy game built with FastAPI + React.

> The purpose of this project is to practice AI-assisted development. All code, infrastructure and commits are done with an AI tool.

## Structure

- [`backend/`](backend/) — REST API (Python / FastAPI / MySQL)
- [`auth/`](auth/) — Authentication service (Python / FastAPI / MySQL)
- [`frontend/`](frontend/) — Web client (TypeScript / React / Vite)
- [`e2e/`](e2e/) — Full-stack Playwright smoke tests

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (includes Docker Compose)

## Getting started

```bash
make dev
make migrate                # first time only: run database migrations
make -C auth seed           # first time only: create a verified dev account (dev@example.com / devpassword123)
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Auth: http://localhost:8001
- Swagger docs: http://localhost:8000/docs

## Development

Run commands from the repo root or from within a package directory.

```bash
make dev          # start full stack with hot reload
make stop         # stop all services
make clean        # stop and remove containers and volumes
make migrate      # run database migrations (explicit — not run automatically)
make check        # lint + types + security + tests for all packages + e2e
make e2e          # run full-stack Playwright tests only
```

Per-package commands (run from package directory or repo root with `make -C <pkg>`):

```bash
make lint         # lint
make types        # type check
make unit         # unit tests
make e2e          # integration tests against test database
make check        # all of the above
make shell        # open a shell in the container
make build        # build dev image
```

Backend only:
```bash
make -C backend db       # open a MySQL shell
make -C backend migrate  # run backend migrations only
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
make prod-migrate   # run on first deploy and after schema changes
make prod-up        # pull latest images and start/recreate services
```

### Other prod commands

```bash
make prod-down      # stop and remove prod containers
```
