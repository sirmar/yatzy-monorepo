.PHONY: format lint types security unit e2e test check

format:
	docker compose run --rm dev uv run ruff format app/
	docker compose run --rm dev uv run ruff check --fix app/

lint:
	docker compose run --rm dev uv run ruff check app/
	docker compose run --rm dev uv run ruff format --check app/

types:
	docker compose run --rm dev uv run ty check app/

security:
	docker compose run --rm dev uv run bandit -r app/ -c pyproject.toml

unit:
	docker compose run --rm dev uv run pytest tests/unit/ -v

e2e:
	docker compose up db-test -d --wait
	docker compose run --rm dev uv run pytest tests/e2e/ -v; docker compose stop db-test

test:
	docker compose up db-test -d --wait
	docker compose run --rm dev uv run pytest tests/ --cov=app; docker compose stop db-test

check: lint types security test
