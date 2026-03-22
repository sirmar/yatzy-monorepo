.PHONY: format lint types security unit e2e test check network start dev build rebuild stop logs ps clean db shell release-major release-minor release-patch

network:
	docker network inspect yatzy >/dev/null 2>&1 || docker network create yatzy

build: network
	docker compose build app

rebuild: network
	docker compose up app db -d --wait --build

start: network
	docker compose up app db -d --wait

dev: network
	docker compose up app-dev db

stop:
	docker compose stop app db

logs:
	docker compose logs app -f

ps:
	docker compose ps

clean:
	docker compose down

db:
	docker compose exec db mysql -uroot -proot yatzy

shell:
	docker compose run --rm dev sh

release-major:
	@git diff --exit-code && git diff --cached --exit-code
	@latest=$$(git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'); \
	 major=$$(echo $$latest | sed 's/v\([0-9]*\)\..*/\1/'); \
	 new="v$$(( major + 1 )).0.0"; \
	 echo "Tagging $$new"; git tag $$new && git push origin $$new

release-minor:
	@git diff --exit-code && git diff --cached --exit-code
	@latest=$$(git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'); \
	 minor=$$(echo $$latest | sed 's/v[0-9]*\.\([0-9]*\)\..*/\1/'); \
	 prefix=$$(echo $$latest | sed 's/\(v[0-9]*\)\..*/\1/'); \
	 new="$$prefix.$$(( minor + 1 )).0"; \
	 echo "Tagging $$new"; git tag $$new && git push origin $$new

release-patch:
	@git diff --exit-code && git diff --cached --exit-code
	@latest=$$(git describe --tags --abbrev=0 2>/dev/null || echo 'v0.0.0'); \
	 patch=$$(echo $$latest | sed 's/v[0-9]*\.[0-9]*\.\([0-9]*\)/\1/'); \
	 prefix=$$(echo $$latest | sed 's/\(v[0-9]*\.[0-9]*\)\.[0-9]*/\1/'); \
	 new="$$prefix.$$(( patch + 1 ))"; \
	 echo "Tagging $$new"; git tag $$new && git push origin $$new

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
