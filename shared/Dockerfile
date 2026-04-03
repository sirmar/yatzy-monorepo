FROM python:3.14-slim AS base
WORKDIR /shared
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml ./

FROM base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev
COPY yatzy_rules/ yatzy_rules/
COPY tests/ tests/
