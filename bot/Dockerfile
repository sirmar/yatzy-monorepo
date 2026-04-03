FROM python:3.14-slim AS base
WORKDIR /bot
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY bot/pyproject.toml ./
COPY shared/ /shared/

FROM base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev

FROM base AS prod
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev
COPY bot/sim/ sim/
COPY bot/app/ app/
EXPOSE 8002
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
