FROM python:3.12-slim AS base
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

FROM base AS dev
COPY requirements.txt requirements-dev.txt ./
RUN uv pip install --system -r requirements-dev.txt

FROM base AS prod
COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt
COPY yatzy/ yatzy/
COPY main.py ./
CMD ["python", "main.py"]
