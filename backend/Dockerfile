FROM ghcr.io/sirmar/dev-python:v0.0.3 AS base

FROM base AS base-deps
WORKDIR /workspace
COPY backend/pyproject.toml backend/uv.lock ./
COPY shared/ /shared/

FROM base-deps AS deps
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev

FROM deps AS app
ENTRYPOINT ["uv", "run"]

FROM deps AS lint
ENTRYPOINT ["/usr/local/bin/lint-entrypoint.sh"]

FROM deps AS format
ENTRYPOINT ["/usr/local/bin/format-entrypoint.sh"]

FROM deps AS unit
ENTRYPOINT ["/usr/local/bin/unit-entrypoint.sh"]

FROM deps AS types
ENTRYPOINT ["/usr/local/bin/types-entrypoint.sh"]

FROM deps AS security
ENTRYPOINT ["/usr/local/bin/security-entrypoint.sh"]

FROM deps AS watch
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/watch-entrypoint.sh"]

FROM deps AS test-base
RUN apt-get update && apt-get install -y --no-install-recommends curl=8.14.1-2+deb13u2 \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL -o /usr/local/bin/dbmate https://github.com/amacneil/dbmate/releases/latest/download/dbmate-linux-amd64 \
    && chmod +x /usr/local/bin/dbmate
WORKDIR /workspace/backend

FROM test-base AS e2e
ENTRYPOINT ["/usr/local/bin/e2e-entrypoint.sh"]

FROM test-base AS coverage
ENTRYPOINT ["/usr/local/bin/coverage-entrypoint.sh"]

FROM base-deps AS prod
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev
COPY backend/src/app/ src/app/
COPY backend/migrations/ migrations/
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
