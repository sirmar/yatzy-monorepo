FROM ghcr.io/sirmar/dev-python:v0.0.4 AS base
WORKDIR /workspace
ENV PYTHONPATH=/workspace/src
COPY pyproject.toml uv.lock ./
RUN uv sync --extra dev

FROM base AS lock
ENTRYPOINT ["/usr/local/bin/lock-entrypoint.sh"]

FROM base AS lint
ENTRYPOINT ["/usr/local/bin/lint-entrypoint.sh"]

FROM base AS format
ENTRYPOINT ["/usr/local/bin/format-entrypoint.sh"]

FROM base AS unit
COPY src/ src/
ENTRYPOINT ["uv", "run", "pytest", "-q", "src/tests/"]

FROM base AS coverage
COPY src/ src/
ENTRYPOINT ["/usr/local/bin/coverage-entrypoint.sh"]

FROM base AS types
COPY src/yatzy_rules/ src/yatzy_rules/
ENTRYPOINT ["uv", "run", "ty", "check", "src/yatzy_rules/"]

FROM base AS security
COPY src/yatzy_rules/ src/yatzy_rules/
ENTRYPOINT ["uv", "run", "bandit", "-q", "-r", "src/yatzy_rules/", "-c", "pyproject.toml"]
