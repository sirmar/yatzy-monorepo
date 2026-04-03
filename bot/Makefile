.PHONY: dev build rebuild format lint types test coverage check fast-check

IMAGE := yatzy-bot-bot

DC := docker compose --progress quiet

dev:
	$(DC) up bot

build:
	$(DC) build bot

rebuild:
	$(DC) build --no-cache bot

format:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		sh -c 'uv run --quiet ruff format app/ sim/ && uv run --quiet ruff check --fix app/ sim/'

lint:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		sh -c 'uv run --quiet ruff check app/ sim/ && uv run --quiet ruff format --check app/ sim/'

types:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		uv run --quiet ty check app/ sim/

test:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/

coverage:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/ --cov=app --cov=sim

fast-check: check

check: lint types test
