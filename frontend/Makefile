.PHONY: format lint types unit check network start

network:
	docker network inspect yatzy >/dev/null 2>&1 || docker network create yatzy

start: network
	docker compose up app -d

format:
	docker compose run --rm dev pnpm biome check --fix .

lint:
	docker compose run --rm dev pnpm biome check .

types:
	docker compose run --rm dev pnpm tsc --noEmit

unit:
	docker compose run --rm dev pnpm vitest run --coverage --passWithNoTests

check: lint types unit
