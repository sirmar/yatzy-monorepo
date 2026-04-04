#!/usr/bin/env bash
set -euo pipefail

f=$(jq -r .tool_input.file_path)
root=$(git -C "$(dirname "$f")" rev-parse --show-toplevel 2>/dev/null) || exit 0
rel=$(python3 -c "import os,sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$f" "$root")
mod=$(echo "$rel" | cut -d/ -f1)

case "$mod" in
  auth|backend|frontend|bot|cli|shared) ;;
  *) exit 0 ;;
esac

tmp=/tmp/claude-touched-modules.txt
[ -f "$tmp" ] || echo "$root" > "$tmp"
echo "$mod" >> "$tmp"
