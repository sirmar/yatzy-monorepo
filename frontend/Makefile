.PHONY: format lint types unit check

format:
	docker compose run --rm dev pnpm biome check --fix .

lint:
	docker compose run --rm dev pnpm biome check .

types:
	docker compose run --rm dev pnpm tsc --noEmit

unit:
	docker compose run --rm dev pnpm vitest run --coverage --passWithNoTests

check: lint types unit
