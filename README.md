# Yatzy

A Swedish Maxi Yatzy game built with FastAPI + React.

> The purpose of this project is to practice AI-assisted development. All code, infrastructure and commits are done with an AI tool.

## Structure

- [`backend/`](backend/) — REST API (Python / FastAPI / MySQL)
- [`frontend/`](frontend/) — Web client (TypeScript / React / Vite)

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (includes Docker Compose)

## Getting started

```bash
make dev
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

## Development

All commands run from the repo root.

```bash
make dev              # start full stack with hot reload
make stop             # stop all services
make clean            # stop and remove containers and volumes

make backend/check    # lint + types + security + all tests
make frontend/check   # lint + types + unit tests + e2e
make check            # both

make backend/shell    # open a shell in the backend container
make backend/db       # open a MySQL shell
```

See [`backend/README.md`](backend/README.md) and [`frontend/README.md`](frontend/README.md) for package-specific details.
