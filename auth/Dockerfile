FROM python:3.14-slim AS base
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY --from=ghcr.io/amacneil/dbmate /usr/local/bin/dbmate /usr/local/bin/dbmate
COPY pyproject.toml uv.lock ./

FROM base AS dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev

FROM base AS prod
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev
COPY app/ app/
COPY migrations/ migrations/
EXPOSE 8001
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
