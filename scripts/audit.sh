#!/usr/bin/env bash
# The audit board. See AGENTS.md: this output is the project's only progress signal.
#
# Usage: ./scripts/audit.sh [--datasheets DIR_WITH_PDFS]
# The datasheet PDFs are not stored here; with them the quote layer runs, without
# them it reports "skipped" and every other layer still decides the exit status.
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PARTSPEC_PYTHON:-}"
if [ -z "$PYTHON" ]; then
  if [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
  else
    PYTHON="python3"
  fi
fi

exec "$PYTHON" scripts/audit.py "$@"
