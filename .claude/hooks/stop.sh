#!/usr/bin/env bash
set -uo pipefail

tmp=/tmp/claude-touched-modules.txt
[ -f "$tmp" ] || exit 0

root=$(head -1 "$tmp")
failed=""

while read -r mod; do
  out=$(make -C "$root/$mod" fast-check 2>&1)
  rc=$?
  [ $rc -ne 0 ] && failed="$failed\n=== $mod ===\n$(echo "$out" | tail -n 20)"
done < <(tail -n +2 "$tmp" | sort -u)

rm -f "$tmp"

[ -n "$failed" ] && { printf "%b" "$failed" >&2; exit 2; }
exit 0
