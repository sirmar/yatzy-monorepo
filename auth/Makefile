.PHONY: dev shell migrate seed format lint types security \
	unit unit-cov e2e e2e-cov test coverage check build rebuild

SHARD_ID  ?= 0
NUM_SHARDS ?= 1

IMAGE := auth-dev

DC_DEV  := docker compose --progress quiet -f docker-compose.yml -f docker-compose.dev.yml
DC_TEST := docker compose --progress quiet -f docker-compose.test.yml

DBMATE_TEST := docker run --rm \
	--network yatzy-auth-test \
	-v $(CURDIR)/migrations:/db/migrations \
	-e DATABASE_URL=mysql://root:test@auth-db-test:3306/yatzy_auth_test \
	ghcr.io/amacneil/dbmate --no-dump-schema

dev:
	$(DC_DEV) up --quiet-pull

shell:
	docker run --rm -it -v $(CURDIR):/app -v /app/.venv $(IMAGE) sh

migrate:
	docker run --rm \
		--network yatzy-auth \
		-v $(CURDIR)/migrations:/db/migrations \
		--env-file .env \
		ghcr.io/amacneil/dbmate --no-dump-schema up

seed:
	sh scripts/seed.sh

build:
	$(DC_DEV) build auth

rebuild:
	$(DC_DEV) build --no-cache auth

format:
	docker run --rm -v $(CURDIR):/app -v /app/.venv $(IMAGE) \
		sh -c 'uv run --quiet ruff format app/ && uv run --quiet ruff check --fix app/'

lint:
	docker run --rm -v $(CURDIR):/app -v /app/.venv $(IMAGE) \
		sh -c 'uv run --quiet ruff check app/ && uv run --quiet ruff format --check app/'

types:
	docker run --rm -v $(CURDIR):/app -v /app/.venv $(IMAGE) \
		uv run --quiet ty check app/

security:
	docker run --rm -v $(CURDIR):/app -v /app/.venv $(IMAGE) \
		uv run --quiet bandit -q -r app/ -c pyproject.toml

unit:
	docker run --rm -v $(CURDIR):/app -v /app/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/unit/

unit-cov:
	docker run --rm -v $(CURDIR):/app -v /app/.venv $(IMAGE) \
		uv run --quiet pytest -q tests/unit/ --cov=app

e2e:
	$(DC_TEST) up -d --wait auth-db-test --quiet-pull
	$(DBMATE_TEST) up
	$(DC_TEST) run --rm --no-deps auth-test uv run --quiet pytest -q tests/e2e/ \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); \
	$(DC_TEST) stop auth-db-test

e2e-cov:
	$(DC_TEST) up -d --wait auth-db-test --quiet-pull
	$(DBMATE_TEST) up
	$(DC_TEST) run --rm --no-deps auth-test uv run --quiet pytest -q tests/e2e/ --cov=app \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); \
	$(DC_TEST) stop auth-db-test

test: unit e2e

coverage:
	$(DC_TEST) up -d --wait auth-db-test --quiet-pull
	$(DBMATE_TEST) up
	$(DC_TEST) run --rm --no-deps auth-test uv run --quiet pytest -q tests/ --cov=app; \
	$(DC_TEST) stop auth-db-test

check: lint types security test
