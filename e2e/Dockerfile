FROM ghcr.io/sirmar/dev-typescript:v0.0.4 AS base

FROM base AS lock
WORKDIR /workspace
COPY package.json pnpm-lock.yaml ./
ENTRYPOINT ["/usr/local/bin/lock-entrypoint.sh"]

FROM base AS deps
WORKDIR /workspace
COPY package.json pnpm-lock.yaml biome.json tsconfig.json playwright.config.ts ./
RUN pnpm install --frozen-lockfile

FROM deps AS lint
ENTRYPOINT ["/usr/local/bin/lint-entrypoint.sh"]

FROM deps AS format
ENTRYPOINT ["/usr/local/bin/format-entrypoint.sh"]

FROM deps AS types
ENTRYPOINT ["/usr/local/bin/types-entrypoint.sh"]

FROM deps AS security
ENTRYPOINT ["/usr/local/bin/security-entrypoint.sh"]

FROM deps AS prod
RUN npx playwright install chromium --with-deps
COPY src ./src
