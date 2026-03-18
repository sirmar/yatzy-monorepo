.PHONY: format lint types security unit e2e test check

format:
	uv run ruff format app/
	uv run ruff check --fix app/

lint:
	uv run ruff check app/
	uv run ruff format --check app/

types:
	uv run ty check app/

security:
	uv run bandit -r app/ -c pyproject.toml

unit:
	uv run pytest tests/unit/ -v

e2e:
	docker compose up db-test -d
	uv run pytest tests/e2e/ -v; docker compose stop db-test

test:
	docker compose up db-test -d
	uv run pytest tests/ --cov=app; docker compose stop db-test

check: lint types security test
