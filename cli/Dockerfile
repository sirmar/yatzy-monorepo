FROM ghcr.io/sirmar/dev-python:v0.0.4 AS base
WORKDIR /workspace

FROM base AS deps
ENV PYTHONPATH=/workspace/src
COPY pyproject.toml uv.lock ./
RUN uv sync --extra dev

FROM deps AS lint
ENTRYPOINT ["/usr/local/bin/lint-entrypoint.sh"]

FROM deps AS format
ENTRYPOINT ["/usr/local/bin/format-entrypoint.sh"]

FROM deps AS unit
ENTRYPOINT ["pytest", "-q", "src/tests/unit/"]

FROM deps AS types
ENTRYPOINT ["ty", "check", "src/yatzy/", "src/main.py"]

FROM deps AS security
ENTRYPOINT ["bandit", "-q", "-r", "src/yatzy/", "src/main.py", "-c", "pyproject.toml"]

FROM deps AS coverage
ENTRYPOINT ["pytest", "-q", "--cov=src/yatzy", "src/tests/"]

FROM base AS prod
ENV PYTHONPATH=/workspace/src
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev
COPY src/yatzy/ src/yatzy/
COPY src/main.py src/main.py
CMD ["python", "src/main.py"]
