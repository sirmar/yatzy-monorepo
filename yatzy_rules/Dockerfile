FROM ghcr.io/sirmar/dev-python:v0.0.4 AS base
WORKDIR /workspace

FROM base AS deps
ENV PYTHONPATH=/workspace/src
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev

FROM deps AS lint
ENTRYPOINT ["/usr/local/bin/lint-entrypoint.sh"]

FROM deps AS format
ENTRYPOINT ["/usr/local/bin/format-entrypoint.sh"]

FROM deps AS unit
COPY src/ src/
ENTRYPOINT ["uv", "run", "pytest", "-q", "src/tests/"]

FROM deps AS coverage
COPY src/ src/
ENTRYPOINT ["/usr/local/bin/coverage-entrypoint.sh"]

FROM deps AS types
COPY src/yatzy_rules/ src/yatzy_rules/
ENTRYPOINT ["uv", "run", "ty", "check", "src/yatzy_rules/"]

FROM deps AS security
COPY src/yatzy_rules/ src/yatzy_rules/
ENTRYPOINT ["uv", "run", "bandit", "-q", "-r", "src/yatzy_rules/", "-c", "pyproject.toml"]

