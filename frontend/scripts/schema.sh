#!/bin/sh
pnpm dlx openapi-typescript http://backend:8000/openapi.json -o src/api/schema.ts
