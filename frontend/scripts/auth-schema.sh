#!/bin/sh
pnpm dlx openapi-typescript http://auth:8000/openapi.json -o src/auth/schema.ts
