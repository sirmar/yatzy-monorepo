.PHONY: dev shell db migrate format lint types security \
	unit unit-cov e2e e2e-cov test coverage check build rebuild

SHARD_ID  ?= 0
NUM_SHARDS ?= 1

IMAGE := backend-dev

DC_DEV  := docker compose --progress quiet -f docker-compose.yml -f docker-compose.dev.yml
DC_TEST := docker compose --progress quiet -f docker-compose.test.yml

DBMATE_TEST := docker run --rm \
	--network yatzy-backend-test \
	-v $(CURDIR)/migrations:/db/migrations \
	-e DATABASE_URL=mysql://root:test@yatzy-db-test:3306/yatzy_test \
	ghcr.io/amacneil/dbmate --no-dump-schema

dev:
	$(DC_DEV) up --quiet-pull

shell:
	docker run --rm -it -v $(CURDIR):/app -v /app/.venv $(IMAGE) sh

db:
	$(DC_DEV) exec yatzy-db mysql -uroot -proot yatzy

migrate:
	docker run --rm \
		--network yatzy-backend \
		-v $(CURDIR)/migrations:/db/migrations \
		--env-file .env \
		ghcr.io/amacneil/dbmate --no-dump-schema up

build:
	$(DC_DEV) build backend

rebuild:
	$(DC_DEV) build --no-cache backend

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
	$(DC_TEST) up -d --wait yatzy-db-test --quiet-pull
	$(DBMATE_TEST) up
	$(DC_TEST) run --rm --no-deps backend-test uv run --quiet pytest -q tests/e2e/ \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); \
	$(DC_TEST) stop yatzy-db-test

e2e-cov:
	$(DC_TEST) up -d --wait yatzy-db-test --quiet-pull
	$(DBMATE_TEST) up
	$(DC_TEST) run --rm --no-deps backend-test uv run --quiet pytest -q tests/e2e/ --cov=app \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); \
	$(DC_TEST) stop yatzy-db-test

test: unit e2e

coverage:
	$(DC_TEST) up -d --wait yatzy-db-test --quiet-pull
	$(DBMATE_TEST) up
	$(DC_TEST) run --rm --no-deps backend-test uv run --quiet pytest -q tests/ --cov=app; \
	$(DC_TEST) stop yatzy-db-test

check: lint types security test
