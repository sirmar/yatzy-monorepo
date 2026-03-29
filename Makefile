.PHONY: dev start stop logs ps clean migrate build e2e check \
	prod-up prod-down prod-migrate \
	release-major release-minor release-patch

DC := docker compose --progress quiet

DBMATE_BACKEND := docker run --rm \
	--network yatzy_default \
	-v $(PWD)/backend/migrations:/db/migrations \
	--env-file backend/.env \
	ghcr.io/amacneil/dbmate --no-dump-schema

DBMATE_AUTH := docker run --rm \
	--network yatzy_default \
	-v $(PWD)/auth/migrations:/db/migrations \
	--env-file auth/.env \
	ghcr.io/amacneil/dbmate --no-dump-schema

DC_E2E  := docker compose --progress quiet -f e2e/docker-compose.yml
DC_PROD := docker compose --progress quiet --context prod -f docker-compose.prod.yml --env-file .env.prod

dev:
	$(DC) up --quiet-pull

start:
	$(DC) up -d --wait --quiet-pull

stop:
	$(DC) stop

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	$(DC) down --volumes

migrate:
	$(DBMATE_BACKEND) up
	$(DBMATE_AUTH) up

build:
	$(DC) build

e2e:
	$(DC_E2E) up -d --wait yatzy-db auth-db --quiet-pull
	docker run --rm --network yatzy-e2e \
		-v $(PWD)/backend/migrations:/db/migrations \
		-e DATABASE_URL=mysql://root:test@yatzy-db:3306/yatzy \
		ghcr.io/amacneil/dbmate --no-dump-schema up
	docker run --rm --network yatzy-e2e \
		-v $(PWD)/auth/migrations:/db/migrations \
		-e DATABASE_URL=mysql://root:test@auth-db:3306/yatzy_auth \
		ghcr.io/amacneil/dbmate --no-dump-schema up
	$(DC_E2E) up -d --wait --build backend auth frontend
	$(DC_E2E) run --rm --no-deps --build e2e; \
	$(DC_E2E) down

prod-up:
	$(DC_PROD) up -d --wait --quiet-pull

prod-down:
	$(DC_PROD) down

prod-migrate:
	$(DC_PROD) up -d --wait yatzy-db auth-db --quiet-pull
	$(DC_PROD) run --rm --no-deps backend dbmate --migrations-dir migrations --no-dump-schema up
	$(DC_PROD) run --rm --no-deps auth dbmate --migrations-dir migrations --no-dump-schema up

check:
	$(MAKE) -C backend check
	$(MAKE) -C auth check
	$(MAKE) -C frontend check
	$(MAKE) -C e2e check
	$(MAKE) e2e

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
