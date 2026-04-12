FROM node:22-slim AS base
WORKDIR /workspace
COPY package.json biome.json playwright.config.ts tsconfig.json ./
RUN npm install

FROM base AS lint
ENTRYPOINT ["npx", "biome", "check", "."]

FROM base AS format
ENTRYPOINT ["npx", "biome", "check", "--fix", "."]

FROM base AS types
ENTRYPOINT ["npx", "tsc", "--noEmit"]

FROM base AS security
ENTRYPOINT ["npm", "audit", "--audit-level=moderate"]

FROM base AS prod
RUN npx playwright install chromium --with-deps
COPY src ./src
