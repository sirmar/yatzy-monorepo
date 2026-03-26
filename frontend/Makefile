.PHONY: dev shell schema format lint types unit coverage security test check build rebuild

IMAGE := frontend-dev

DC_DEV := docker compose --progress quiet -f docker-compose.yml -f docker-compose.dev.yml

dev:
	$(DC_DEV) up --quiet-pull

shell:
	docker run --rm -it -v $(CURDIR):/app -v /app/node_modules $(IMAGE) sh

schema:
	docker run --rm \
		--add-host host.docker.internal:host-gateway \
		-v $(CURDIR):/app \
		$(IMAGE) \
		pnpm dlx openapi-typescript http://host.docker.internal:8000/openapi.json -o src/api/schema.ts

build:
	$(DC_DEV) build frontend

rebuild:
	$(DC_DEV) build --no-cache frontend

format:
	docker run --rm -v $(CURDIR):/app -v /app/node_modules $(IMAGE) pnpm biome check --fix .

lint:
	docker run --rm -v $(CURDIR):/app -v /app/node_modules $(IMAGE) pnpm biome check .

types:
	docker run --rm -v $(CURDIR):/app -v /app/node_modules $(IMAGE) pnpm tsc --noEmit

unit:
	docker run --rm -e CI=true -v $(CURDIR):/app -v /app/node_modules $(IMAGE) pnpm vitest run --reporter=dot

coverage:
	docker run --rm -e CI=true -v $(CURDIR):/app -v /app/node_modules $(IMAGE) pnpm vitest run --coverage --reporter=dot

security:
	docker run --rm -v $(CURDIR):/app -v /app/node_modules $(IMAGE) pnpm audit --audit-level=moderate

test: unit

check: lint types security test
