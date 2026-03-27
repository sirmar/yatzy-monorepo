#!/bin/sh
set -e

BASE=http://localhost:8001
EMAIL=dev@example.com
PASSWORD=devpassword123

STATUS=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE/register" \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

if [ "$STATUS" = "409" ]; then
  echo "User already exists, skipping registration"
elif [ "$STATUS" = "201" ]; then
  TOKEN=$(curl -sf "$BASE/dev/verification-token?email=$EMAIL" \
    | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
  curl -sf -X POST "$BASE/verify-email" \
    -H 'Content-Type: application/json' \
    -d "{\"token\":\"$TOKEN\"}" > /dev/null
  echo "Registered and verified: $EMAIL"
else
  echo "Unexpected status $STATUS from /register" >&2
  exit 1
fi

echo "Seed complete — $EMAIL / $PASSWORD"
