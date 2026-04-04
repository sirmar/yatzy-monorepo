.PHONY: dev build rebuild format lint types test coverage check fast-check evaluate evaluate-maxi evaluate-yatzy evaluate-maxi-sequential evaluate-yatzy-sequential

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
		sh -c 'uv run --quiet ruff format app/ && uv run --quiet ruff check --fix app/'

lint:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		sh -c 'uv run --quiet ruff check app/ && uv run --quiet ruff format --check app/'

types:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		uv run --quiet ty check app/

test:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/

coverage:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/ --cov=app

evaluate: evaluate-maxi

evaluate-maxi:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv -e PYTHONPATH=/bot -e UV_LINK_MODE=copy $(IMAGE) \
		uv run python scripts/evaluate.py --bot maxi $(ARGS)

evaluate-yatzy:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv -e PYTHONPATH=/bot -e UV_LINK_MODE=copy $(IMAGE) \
		uv run python scripts/evaluate.py --bot yatzy $(ARGS)

evaluate-maxi-sequential:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv -e PYTHONPATH=/bot -e UV_LINK_MODE=copy $(IMAGE) \
		uv run python scripts/evaluate.py --bot maxi-sequential $(ARGS)

evaluate-yatzy-sequential:
	docker run --rm -v $(CURDIR):/bot -v /bot/.venv -e PYTHONPATH=/bot -e UV_LINK_MODE=copy $(IMAGE) \
		uv run python scripts/evaluate.py --bot yatzy-sequential $(ARGS)

fast-check: check

check: lint types test
