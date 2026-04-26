#!/usr/bin/env bash
# Retry git push with backoff when the remote is flaky (e.g. GitHub 443 timeouts).
# Usage: ./scripts/git_push_retry.sh [remote] [ref ...]
# Env:   GIT_PUSH_RETRY_MAX (default 5)  GIT_PUSH_RETRY_DELAY base seconds (default 3, nth wait = base * n)
set -euo pipefail
max="${GIT_PUSH_RETRY_MAX:-5}"
base_delay="${GIT_PUSH_RETRY_DELAY:-3}"
remote="${1:-origin}"
if [ "$#" -ge 1 ]; then shift; fi
if [ "$#" -eq 0 ]; then
  set -- main
fi

n=0
while [ "$n" -lt "$max" ]; do
  n=$((n + 1))
  echo "=== git push $remote $* (attempt $n/$max) ===" >&2
  if git push "$remote" "$@"; then
    echo "OK" >&2
    exit 0
  fi
  if [ "$n" -lt "$max" ]; then
    s=$(( base_delay * n ))
    echo "failed, sleep ${s}s ..." >&2
    sleep "$s"
  fi
done
echo "all attempts failed" >&2
exit 1
