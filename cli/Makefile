.PHONY: play build rebuild lint types security format unit unit-cov \
	integration integration-cov test coverage check

IMAGE := yatzy-cli-dev

DC_TEST := docker compose --progress quiet -f docker-compose.test.yml

DBMATE_BACKEND := docker run --rm \
	--network yatzy-cli-test \
	-v $(CURDIR)/../backend/migrations:/db/migrations \
	-e DATABASE_URL=mysql://root:test@yatzy-db:3306/yatzy \
	ghcr.io/amacneil/dbmate --no-dump-schema

DBMATE_AUTH := docker run --rm \
	--network yatzy-cli-test \
	-v $(CURDIR)/../auth/migrations:/db/migrations \
	-e DATABASE_URL=mysql://root:test@auth-db:3306/yatzy_auth \
	ghcr.io/amacneil/dbmate --no-dump-schema

build:
	docker compose build cli

rebuild:
	docker compose build --no-cache cli

play:
	docker compose run --rm cli

dev:
	docker compose run --rm cli-dev

format:
	docker run --rm -v $(CURDIR):/app $(IMAGE) \
		sh -c 'ruff format yatzy/ main.py && ruff check --fix yatzy/ main.py'

lint:
	docker run --rm -v $(CURDIR):/app $(IMAGE) \
		sh -c 'ruff check yatzy/ main.py && ruff format --check yatzy/ main.py'

types:
	docker run --rm -v $(CURDIR):/app $(IMAGE) \
		ty check yatzy/ main.py

security:
	docker run --rm -v $(CURDIR):/app $(IMAGE) \
		bandit -q -r yatzy/ main.py -c pyproject.toml

unit:
	docker run --rm -v $(CURDIR):/app $(IMAGE) \
		pytest -q tests/unit/

unit-cov:
	docker run --rm -v $(CURDIR):/app $(IMAGE) \
		pytest -q tests/unit/ --cov=yatzy

integration:
	docker run --rm -v $(CURDIR):/app \
		--network yatzy_default \
		-e AUTH_URL=http://auth:8001 \
		-e BACKEND_URL=http://backend:8000 \
		$(IMAGE) \
		pytest -q -m integration tests/

integration-cov:
	$(DC_TEST) up -d --wait auth-db yatzy-db --quiet-pull
	$(DBMATE_BACKEND) up
	$(DBMATE_AUTH) up
	$(DC_TEST) up -d --wait --quiet-pull backend auth
	$(DC_TEST) run --rm --no-deps cli-test \
		pytest -q -m integration tests/ --cov=yatzy; \
	$(DC_TEST) stop backend auth auth-db yatzy-db

test: unit integration-cov

coverage:
	$(DC_TEST) up -d --wait auth-db yatzy-db --quiet-pull
	$(DBMATE_BACKEND) up
	$(DBMATE_AUTH) up
	$(DC_TEST) up -d --wait --quiet-pull backend auth
	$(DC_TEST) run --rm --no-deps cli-test \
		pytest -q tests/ --cov=yatzy; \
	$(DC_TEST) stop backend auth auth-db yatzy-db

check: lint types security unit integration-cov
