#!/usr/bin/env bash
# Drive audit rounds with a headless agent. The loop understands one thing only:
# the board printed by scripts/audit.sh. See AGENTS.md.
#
#   AGENT_CMD="claude -p" MAX_ROUNDS=20 STALL_LIMIT=3 ./scripts/loop.sh
#
# Per round: a throwaway branch, one work cycle (scripts/prompts/round.md), the
# audit, a commit of whatever the round left, and a stop check. Stops when the
# board is green (未通过: [] and no 退步), when no round has improved the passing
# count for STALL_LIMIT rounds, or at MAX_ROUNDS. Every AUDIT_EVERY rounds the
# independent audit prompt is run read-only into .audit/reports/.
set -euo pipefail

cd "$(dirname "$0")/.."

AGENT_CMD="${AGENT_CMD:-claude -p}"
MAX_ROUNDS="${MAX_ROUNDS:-20}"
STALL_LIMIT="${STALL_LIMIT:-3}"
AUDIT_EVERY="${AUDIT_EVERY:-5}"
BRANCH_PREFIX="${BRANCH_PREFIX:-audit/round}"
REPORTS=".audit/reports"
BOARD=".audit/last_audit.txt"

read -r -a AGENT <<<"$AGENT_CMD"
if [ "${#AGENT[@]}" -eq 0 ]; then
  echo "AGENT_CMD is empty" >&2
  exit 2
fi

if [ -n "$(git status --porcelain)" ] && [ "${ALLOW_DIRTY:-0}" != "1" ]; then
  echo "working tree is dirty; commit or stash first (or ALLOW_DIRTY=1)" >&2
  exit 2
fi

mkdir -p "$REPORTS"
board_field() { sed -n "s/^$1: *//p" "$BOARD"; }

best=0
stalled=0
round=1
while [ "$round" -le "$MAX_ROUNDS" ]; do
  git checkout -q -B "$BRANCH_PREFIX-$round"
  echo "=== round $round on $BRANCH_PREFIX-$round ==="

  "${AGENT[@]}" "$(cat scripts/prompts/round.md)"

  # A failing board exits 1; that is the round's outcome, not a script error.
  if ! ./scripts/audit.sh | tee "$BOARD"; then
    echo "board is not green after round $round"
  fi

  failing=$(board_field 未通过)
  regressed=$(board_field 退步)
  passed=$(board_field 通过)
  total=$(board_field 规则总数)

  if [ -n "$(git status --porcelain)" ]; then
    git add -A
    git commit -q -m "[audit] round $round: $passed/$total passing; 未通过: $failing; 退步: $regressed"
  fi

  if [ "$failing" = "[]" ] && [ "$regressed" = "[]" ]; then
    echo "board green: $passed/$total"
    break
  fi

  if [ "$passed" -gt "$best" ]; then
    best=$passed
    stalled=0
  else
    stalled=$((stalled + 1))
    echo "no progress for $stalled round(s) (best $best)"
    if [ "$stalled" -ge "$STALL_LIMIT" ]; then
      echo "stalled at $passed/$total; stopping for a human"
      break
    fi
  fi

  if [ $((round % AUDIT_EVERY)) -eq 0 ]; then
    "${AGENT[@]}" "$(cat scripts/prompts/independent_audit.md)" >"$REPORTS/round-$round.audit.md"
    echo "independent audit report: $REPORTS/round-$round.audit.md"
  fi

  round=$((round + 1))
done

git checkout -q - 2>/dev/null || true
