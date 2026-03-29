.PHONY: lint format check

IMAGE := e2e-dev

lint:
	docker build --target dev -t $(IMAGE) . -q
	docker run --rm -v $(CURDIR):/app -v /app/node_modules $(IMAGE) npx biome check .

format:
	docker build --target dev -t $(IMAGE) . -q
	docker run --rm -v $(CURDIR):/app -v /app/node_modules $(IMAGE) npx biome check --fix .

check: lint
