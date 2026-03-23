.PHONY: dev start stop logs ps clean build rebuild check \
	backend/build backend/rebuild backend/dev backend/shell backend/db backend/migrate \
	backend/format backend/lint backend/types backend/security \
	backend/unit backend/e2e backend/test backend/check \
	release-major release-minor release-patch \
	frontend/build frontend/rebuild frontend/schema \
	frontend/format frontend/lint frontend/types frontend/unit frontend/e2e frontend/check \
	frontend/security \
	backend/image-audit frontend/image-audit

SHARD_ID ?= 0
NUM_SHARDS ?= 1

# Full stack

dev:
	docker compose up db migrate backend frontend

start:
	docker compose up db migrate backend frontend -d --wait

stop:
	docker compose stop

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	docker compose down

build:
	docker compose build

rebuild:
	docker compose up -d --wait --build

backend/build:
	docker compose build backend backend-dev

backend/rebuild:
	docker compose up db migrate backend -d --wait --build

frontend/build:
	docker compose build frontend frontend-app frontend-dev e2e

frontend/rebuild:
	docker compose up db migrate backend frontend -d --wait --build

# Backend

backend/dev:
	docker compose up db migrate backend

backend/shell:
	docker compose run --rm backend-dev sh

backend/db:
	docker compose exec db mysql -uroot -proot yatzy

backend/migrate:
	docker compose run --rm migrate

backend/format:
	docker compose run --rm backend-dev sh -c 'uv run ruff format app/ && uv run ruff check --fix app/'

backend/lint:
	docker compose run --rm backend-dev sh -c 'uv run ruff check app/ && uv run ruff format --check app/'

backend/types:
	docker compose run --rm backend-dev uv run ty check app/

backend/security:
	docker compose run --rm backend-dev uv run bandit -r app/ -c pyproject.toml

backend/image-audit:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v $(PWD)/.trivyignore:/.trivyignore aquasec/trivy image --severity HIGH,CRITICAL --ignorefile /.trivyignore backend-dev

backend/unit:
	docker compose run --rm backend-dev uv run pytest tests/unit/ -v --cov=app

backend/e2e:
	docker compose up db-test -d --wait
	docker compose run --rm backend-dev uv run pytest tests/e2e/ -v --cov=app \
		--shard-id=$(SHARD_ID) --num-shards=$(NUM_SHARDS); docker compose stop db-test

backend/test:
	docker compose up db-test -d --wait
	docker compose run --rm backend-dev uv run pytest tests/ --cov=app; docker compose stop db-test

backend/check: backend/lint backend/types backend/security backend/test

# Frontend

frontend/schema:
	docker compose up db migrate backend -d --wait
	docker compose run --rm frontend-dev pnpm dlx openapi-typescript http://backend:8000/openapi.json -o src/api/schema.ts

frontend/security:
	docker compose run --rm frontend-dev pnpm audit --audit-level=moderate

frontend/image-audit:
	docker run --rm -v /var/run/docker.sock:/var/run/docker.sock -v $(PWD)/.trivyignore:/.trivyignore aquasec/trivy image --severity HIGH,CRITICAL --ignorefile /.trivyignore frontend-app

frontend/format:
	docker compose run --rm frontend-dev pnpm biome check --fix .

frontend/lint:
	docker compose run --rm frontend-dev pnpm biome check .

frontend/types:
	docker compose run --rm frontend-dev pnpm tsc --noEmit

frontend/unit:
	docker compose run --rm frontend-dev pnpm vitest run --coverage --passWithNoTests

frontend/e2e:
	docker compose run --rm e2e

frontend/check: frontend/lint frontend/types frontend/security frontend/unit frontend/e2e

# Aggregate

check: backend/check frontend/check

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
