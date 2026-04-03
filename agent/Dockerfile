FROM python:3.14-slim AS base
WORKDIR /agent
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY agent/pyproject.toml agent/uv.lock* ./
COPY shared/ /shared/

FROM base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev

ENV PYTHONPATH=/agent

FROM base AS prod
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev
COPY agent/agent/ agent/
ENV PYTHONPATH=/agent
