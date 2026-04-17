FROM ghcr.io/sirmar/dev-typescript:v0.0.4 AS base

FROM base AS deps
WORKDIR /workspace
COPY package.json pnpm-lock.yaml biome.json tsconfig.json tsconfig.node.json vite.config.ts index.html ./
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

FROM deps AS lint
ENTRYPOINT ["/usr/local/bin/lint-entrypoint.sh"]

FROM deps AS format
ENTRYPOINT ["/usr/local/bin/format-entrypoint.sh"]

FROM deps AS unit
ENV CI=true
ENTRYPOINT ["/usr/local/bin/unit-entrypoint.sh"]

FROM deps AS coverage
ENV CI=true
ENTRYPOINT ["/usr/local/bin/coverage-entrypoint.sh"]

FROM deps AS types
ENTRYPOINT ["/usr/local/bin/types-entrypoint.sh"]

FROM deps AS security
ENTRYPOINT ["/usr/local/bin/security-entrypoint.sh"]

FROM deps AS watch
EXPOSE 5173
ENTRYPOINT ["/usr/local/bin/watch-entrypoint.sh"]

FROM deps AS scripts
ENTRYPOINT ["sh"]

FROM deps AS builder
COPY . .
RUN pnpm build

FROM ghcr.io/sirmar/dev-nginx:v0.0.4 AS prod
COPY --from=builder /workspace/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf.template
EXPOSE 80
ENTRYPOINT ["/usr/local/bin/serve-entrypoint.sh"]
