.PHONY: build rebuild train imitate evaluate tensorboard format lint

IMAGE := yatzy-agent-dev
DC    := docker compose --progress quiet

build:
	$(DC) build agent

rebuild:
	$(DC) build --no-cache agent

train:
	$(DC) run --rm agent uv run python -m agent.train.train $(ARGS)

imitate:
	$(DC) run --rm agent uv run python -m agent.train.imitate $(ARGS)

evaluate:
	$(DC) run --rm agent uv run python -m agent.train.evaluate --model $(MODEL) $(ARGS)

tensorboard:
	$(DC) up tensorboard

format:
	$(DC) run --rm agent sh -c 'uv run ruff format agent/ && uv run ruff check --fix agent/'

lint:
	$(DC) run --rm agent sh -c 'uv run ruff check agent/ && uv run ruff format --check agent/'
