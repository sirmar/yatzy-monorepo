FROM ghcr.io/sirmar/dev-python:v0.0.3 AS base
WORKDIR /workspace

FROM base AS base-deps
COPY bot/pyproject.toml bot/uv.lock ./
COPY yatzy_rules/ /yatzy_rules/

FROM base-deps AS deps
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev

FROM deps AS lint
ENTRYPOINT ["/usr/local/bin/lint-entrypoint.sh"]

FROM deps AS format
ENTRYPOINT ["/usr/local/bin/format-entrypoint.sh"]

FROM deps AS unit
ENTRYPOINT ["/usr/local/bin/unit-entrypoint.sh"]

FROM deps AS types
ENTRYPOINT ["/usr/local/bin/types-entrypoint.sh"]

FROM deps AS coverage
ENTRYPOINT ["/usr/local/bin/coverage-entrypoint.sh"]

FROM deps AS watch
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/watch-entrypoint.sh"]

FROM deps AS scripts
ENTRYPOINT ["uv", "run", "python"]

FROM base-deps AS prod
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev
COPY bot/src/app/ src/app/
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
