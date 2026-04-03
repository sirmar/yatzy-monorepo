.PHONY: build format lint types test coverage check fast-check

IMAGE := yatzy-shared-shared

DC := docker compose --progress quiet

build:
	$(DC) build shared

format:
	docker run --rm -v $(CURDIR):/shared -v /shared/.venv $(IMAGE) \
		sh -c 'uv run --quiet ruff format yatzy_rules/ && uv run --quiet ruff check --fix yatzy_rules/'

lint:
	docker run --rm -v $(CURDIR):/shared -v /shared/.venv $(IMAGE) \
		sh -c 'uv run --quiet ruff check yatzy_rules/ && uv run --quiet ruff format --check yatzy_rules/'

types:
	docker run --rm -v $(CURDIR):/shared -v /shared/.venv $(IMAGE) \
		uv run --quiet ty check yatzy_rules/

test:
	docker run --rm -v $(CURDIR):/shared -v /shared/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/

coverage:
	docker run --rm -v $(CURDIR):/shared -v /shared/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/ --cov=yatzy_rules

fast-check: check

check: lint types test
