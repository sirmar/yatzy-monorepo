.PHONY: dev build rebuild format lint test

DC := docker compose --progress quiet

dev:
	$(DC) up bot

build:
	$(DC) build bot

rebuild:
	$(DC) build --no-cache bot



format:
	$(DC) run --rm bot sh -c 'uv run ruff format app/ && uv run ruff check --fix app/'

lint:
	$(DC) run --rm bot sh -c 'uv run ruff check app/ && uv run ruff format --check app/'

test:
	$(DC) run --rm bot uv run pytest tests/ -v
