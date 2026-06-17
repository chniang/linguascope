#!/usr/bin/env bash
# push-hf.sh — Sync text-only changes from main to the HF Space remote.
#
# Usage: bash scripts/push-hf.sh
#
# HF rejects binary files (Xet policy); screenshots live on GitHub raw.
# This script builds a binary-free commit on top of HF's history and pushes it.

set -euo pipefail

REMOTE="hf"
DEPLOY_BRANCH="hf-deploy"
BINARY_EXT='\.(png|jpg|jpeg|gif|webp|ico|pdf|zip|tar\.gz|woff2?|ttf|eot)$'

echo "→ Fetching $REMOTE…"
git fetch "$REMOTE" --quiet

# Detect text-only changes between HF tip and local main
TEXT_CHANGED=$(git diff --name-only --diff-filter=ACMR "$REMOTE/main" main \
  | grep -vE "$BINARY_EXT" || true)

TEXT_DELETED=$(git diff --name-only --diff-filter=D "$REMOTE/main" main \
  | grep -vE "$BINARY_EXT" || true)

if [ -z "$TEXT_CHANGED" ] && [ -z "$TEXT_DELETED" ]; then
  echo "✅  Nothing to sync — HF is already up to date."
  exit 0
fi

# Commit count and log (best-effort; histories may diverge)
COMMIT_COUNT=$(git rev-list --count "$REMOTE/main..main" 2>/dev/null || echo "?")
COMMIT_LOG=$(git log --oneline "$REMOTE/main..main" 2>/dev/null | head -10 \
  || echo "(divergent history — see origin/main)")

echo "→ Syncing ~${COMMIT_COUNT} commit(s)…"
[ -n "$TEXT_CHANGED" ] && echo "$TEXT_CHANGED" | sed 's/^/   + /'
[ -n "$TEXT_DELETED" ] && echo "$TEXT_DELETED" | sed 's/^/   - /'

# Build on top of HF's current tip (keeps HF history binary-free)
git checkout -b "$DEPLOY_BRANCH" "$REMOTE/main"

if [ -n "$TEXT_CHANGED" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] && git checkout main -- "$f"
  done <<< "$TEXT_CHANGED"
fi

if [ -n "$TEXT_DELETED" ]; then
  while IFS= read -r f; do
    [ -n "$f" ] && git rm --quiet -f -- "$f"
  done <<< "$TEXT_DELETED"
fi

# Guard: nothing staged after filtering (e.g. only binary changes)
if git diff --cached --quiet; then
  echo "✅  Nothing to commit after binary filtering — HF already has these changes."
  git checkout main
  git branch -D "$DEPLOY_BRANCH"
  exit 0
fi

COMMIT_MSG="chore: sync ${COMMIT_COUNT} commit(s) from main (text-only, binaries excluded)

${COMMIT_LOG}"

git commit -m "$COMMIT_MSG"
git push "$REMOTE" "${DEPLOY_BRANCH}:main"

git checkout main
git branch -D "$DEPLOY_BRANCH"

echo "✅  Pushed to HF — ${COMMIT_COUNT} commit(s) synced, binaries excluded."
