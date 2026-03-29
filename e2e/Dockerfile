FROM node:22-slim AS base
WORKDIR /app
COPY package.json ./
RUN npm install

FROM base AS dev

FROM base AS e2e
RUN npx playwright install chromium --with-deps
COPY . .
