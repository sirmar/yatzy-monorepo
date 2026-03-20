.PHONY: format lint types security unit e2e test check network start

network:
	docker network inspect yatzy >/dev/null 2>&1 || docker network create yatzy

start: network
	docker compose up app db -d --wait

format:
	docker compose run --rm dev sh -c 'uv run ruff format app/ && uv run ruff check --fix app/'

lint:
	docker compose run --rm dev sh -c 'uv run ruff check app/ && uv run ruff format --check app/'

types:
	docker compose run --rm dev uv run ty check app/

security:
	docker compose run --rm dev uv run bandit -r app/ -c pyproject.toml

unit:
	docker compose run --rm dev uv run pytest tests/unit/ -v --cov=app

e2e:
	docker compose up db-test -d --wait
	docker compose run --rm dev uv run pytest tests/e2e/ -v --cov=app; docker compose stop db-test

test:
	docker compose up db-test -d --wait
	docker compose run --rm dev uv run pytest tests/ --cov=app; docker compose stop db-test

check: lint types security test
