.PHONY: dev start stop logs ps clean build rebuild check \
	backend/build backend/rebuild backend/dev backend/shell backend/db backend/migrate \
	backend/format backend/lint backend/types backend/security \
	backend/unit backend/unit-cov backend/e2e backend/e2e-cov backend/test backend/coverage backend/check \
	release-major release-minor release-patch \
	frontend/build frontend/rebuild frontend/schema \
	frontend/format frontend/lint frontend/types frontend/unit frontend/coverage frontend/test frontend/e2e frontend/check \
	frontend/security \
	auth/build auth/rebuild auth/dev auth/shell \
	auth/format auth/lint auth/types auth/security \
	auth/unit auth/unit-cov auth/e2e auth/e2e-cov auth/test auth/coverage auth/check

SHARD_ID ?= 0
NUM_SHARDS ?= 1
DC_RUN := docker compose --progress quiet run --rm --quiet-pull
DC_BUILD := docker compose --progress quiet build
DC_UP_TEST := docker compose --progress quiet up db-test -d --wait --quiet-pull
DC_UP_AUTH_TEST := docker compose --progress quiet up auth-db-test -d --wait --quiet-pull
DC_UP_BACKEND := docker compose --progress quiet up db migrate backend -d --wait --quiet-pull
DC_UP_FULL := docker compose --progress quiet up db migrate backend auth-db auth-migrate auth frontend -d --wait --quiet-pull

# Full stack

dev:
	docker compose --progress quiet up db migrate backend auth-db auth-migrate auth frontend --quiet-pull

start:
	$(DC_UP_FULL)

stop:
	docker compose stop

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	docker compose down --volumes

build:
	$(DC_BUILD)

rebuild:
	$(DC_UP_FULL) --build

backend/build:
	$(DC_BUILD) backend backend-dev

backend/rebuild:
	$(DC_UP_BACKEND) --build

frontend/build:
	$(DC_BUILD) frontend frontend-app frontend-dev e2e

frontend/rebuild:
	$(DC_UP_FULL) --build

# Backend

backend/dev:
	docker compose --progress quiet up db migrate backend --quiet-pull

backend/shell:
	$(DC_RUN) backend-dev sh

backend/db:
	docker compose exec db mysql -uroot -proot yatzy

backend/migrate:
	$(DC_RUN) migrate

backend/format:
	$(DC_RUN) backend-dev sh -c 'uv run --quiet ruff format app/ && uv run --quiet ruff check --fix app/'

backend/lint:
	$(DC_RUN) backend-dev sh -c 'uv run --quiet ruff check app/ && uv run --quiet ruff format --check app/'

backend/types:
	$(DC_RUN) backend-dev uv run --quiet ty check app/

backend/security:
	$(DC_RUN) backend-dev uv run --quiet bandit -q -r app/ -c pyproject.toml

backend/unit:
	$(DC_RUN) backend-dev uv run --quiet pytest -q tests/unit/

backend/unit-cov:
	$(DC_RUN) backend-dev uv run --quiet pytest -q tests/unit/ --cov=app

backend/e2e:
	$(DC_UP_TEST)
	$(DC_RUN) backend-dev uv run --quiet pytest -q tests/e2e/ \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); docker compose stop db-test

backend/e2e-cov:
	$(DC_UP_TEST)
	$(DC_RUN) backend-dev uv run --quiet pytest -q tests/e2e/ --cov=app \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); docker compose stop db-test

backend/test: backend/unit backend/e2e

backend/coverage:
	$(DC_UP_TEST)
	$(DC_RUN) backend-dev uv run --quiet pytest -q tests/ --cov=app; docker compose stop db-test

backend/check: backend/lint backend/types backend/security backend/test

# Frontend

frontend/schema:
	$(DC_UP_BACKEND)
	$(DC_RUN) frontend-dev pnpm dlx openapi-typescript http://backend:8000/openapi.json -o src/api/schema.ts

frontend/security:
	$(DC_RUN) frontend-dev pnpm audit --audit-level=moderate

frontend/format:
	$(DC_RUN) frontend-dev pnpm biome check --fix .

frontend/lint:
	$(DC_RUN) frontend-dev pnpm biome check .

frontend/types:
	$(DC_RUN) frontend-dev pnpm tsc --noEmit

frontend/unit:
	$(DC_RUN) -e CI=true frontend-dev pnpm vitest run --reporter=dot

frontend/coverage:
	$(DC_RUN) -e CI=true frontend-dev pnpm vitest run --coverage --reporter=dot

frontend/test: frontend/unit frontend/e2e

frontend/e2e:
	$(DC_BUILD) frontend-app e2e
	docker compose --progress quiet up db-test auth-db --force-recreate -V -d --wait --quiet-pull
	$(DC_RUN) auth-migrate
	docker compose --progress quiet up auth --no-deps -d --wait --quiet-pull
	$(DC_RUN) e2e; docker compose stop db-test auth auth-db

frontend/check: frontend/lint frontend/types frontend/security frontend/test

# Auth

auth/build:
	$(DC_BUILD) auth auth-dev

auth/rebuild:
	$(DC_BUILD) auth auth-dev --no-cache

auth/dev:
	docker compose --progress quiet up auth-db auth-migrate auth --quiet-pull

auth/shell:
	$(DC_RUN) auth-dev sh

auth/format:
	$(DC_RUN) auth-dev sh -c 'uv run --quiet ruff format app/ && uv run --quiet ruff check --fix app/'

auth/lint:
	$(DC_RUN) auth-dev sh -c 'uv run --quiet ruff check app/ && uv run --quiet ruff format --check app/'

auth/types:
	$(DC_RUN) auth-dev uv run --quiet ty check app/

auth/security:
	$(DC_RUN) auth-dev uv run --quiet bandit -q -r app/ -c pyproject.toml

auth/unit:
	$(DC_RUN) auth-dev uv run --quiet pytest -q tests/unit/

auth/unit-cov:
	$(DC_RUN) auth-dev uv run --quiet pytest -q tests/unit/ --cov=app

auth/e2e:
	$(DC_UP_AUTH_TEST)
	$(DC_RUN) auth-dev uv run --quiet pytest -q tests/e2e/ \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); docker compose stop auth-db-test

auth/e2e-cov:
	$(DC_UP_AUTH_TEST)
	$(DC_RUN) auth-dev uv run --quiet pytest -q tests/e2e/ --cov=app \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); docker compose stop auth-db-test

auth/test: auth/unit auth/e2e

auth/coverage:
	$(DC_UP_AUTH_TEST)
	$(DC_RUN) auth-dev uv run --quiet pytest -q tests/ --cov=app; docker compose stop auth-db-test

auth/check: auth/lint auth/types auth/security auth/test

# Aggregate

check: backend/check frontend/check auth/check

# Release

release-major:
	@git diff --exit-code && git diff --cached --exit-code
	@latest=$$(git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'); \
	 major=$$(echo $$latest | cut -d. -f1 | tr -d v); \
	 minor=$$(echo $$latest | cut -d. -f2); \
	 patch=$$(echo $$latest | cut -d. -f3); \
	 new="v$$(( major + 1 )).0.0"; \
	 echo "Tagging $$new"; git tag $$new && git push origin $$new

release-minor:
	@git diff --exit-code && git diff --cached --exit-code
	@latest=$$(git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'); \
	 major=$$(echo $$latest | cut -d. -f1 | tr -d v); \
	 minor=$$(echo $$latest | cut -d. -f2); \
	 patch=$$(echo $$latest | cut -d. -f3); \
	 new="v$$major.$$(( minor + 1 )).0"; \
	 echo "Tagging $$new"; git tag $$new && git push origin $$new

release-patch:
	@git diff --exit-code && git diff --cached --exit-code
	@latest=$$(git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'); \
	 major=$$(echo $$latest | cut -d. -f1 | tr -d v); \
	 minor=$$(echo $$latest | cut -d. -f2); \
	 patch=$$(echo $$latest | cut -d. -f3); \
	 new="v$$major.$$minor.$$(( patch + 1 ))"; \
	 echo "Tagging $$new"; git tag $$new && git push origin $$new
