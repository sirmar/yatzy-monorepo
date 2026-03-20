.PHONY: format lint types unit check network start schema

network:
	docker network inspect yatzy >/dev/null 2>&1 || docker network create yatzy

start: network
	docker compose up app -d

schema:
	docker run --rm --network yatzy -v .:/app -w /app frontend-dev pnpm dlx openapi-typescript http://backend:8000/openapi.json -o src/api/schema.ts

format:
	docker compose run --rm dev pnpm biome check --fix .

lint:
	docker compose run --rm dev pnpm biome check .

types:
	docker compose run --rm dev pnpm tsc --noEmit

unit:
	docker compose run --rm dev pnpm vitest run --coverage --passWithNoTests

check: lint types unit
