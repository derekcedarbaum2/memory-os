#!/bin/bash
# Weekly memory maintenance — fires Sun 11pm PT, after learnings-resurface 10pm.
#
# Runs three jobs in order:
#   1. dormancy-decay.py        — marks vault _learnings.md as status:dormant if 90d no touch
#   2. active-venture-refresh.py — demotes stale MEMORY.md pinboard entries, surfaces candidates
#   3. prune-memory-dryrun.py    — headless audit of memory dir, logs summary
#
# All output → ~/.claude/logs/weekly-memory-maintenance.log
# All structural events → Vault/log.md (each script appends its own lines)

set -euo pipefail

LOCK_DIR="/tmp/weekly-memory-maintenance.lock"
LOG_DIR="$HOME/.claude/logs"
mkdir -p "$LOG_DIR"

# stale-lock cleanup (>2h)
if [ -d "$LOCK_DIR" ]; then
    age_min=$(( ($(date +%s) - $(stat -f%m "$LOCK_DIR")) / 60 ))
    if [ "$age_min" -gt 120 ]; then
        rm -rf "$LOCK_DIR"
    fi
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "[$(date)] another weekly-memory-maintenance run in progress — exiting" >&2
    exit 0
fi
trap 'rm -rf "$LOCK_DIR"' EXIT

cd "$HOME"

echo "=== weekly-memory-maintenance $(date) ==="
echo ""

echo "--- 1. dormancy-decay (90d threshold) ---"
python3 "$HOME/.claude/hooks/dormancy-decay.py" || echo "dormancy-decay failed: $?"
echo ""

echo "--- 2. active-venture-refresh ---"
python3 "$HOME/.claude/hooks/active-venture-refresh.py" || echo "active-venture-refresh failed: $?"
echo ""

echo "--- 3. prune-memory dry-run ---"
python3 "$HOME/.claude/hooks/prune-memory-dryrun.py" || echo "prune-memory-dryrun failed: $?"
echo ""

echo "=== weekly-memory-maintenance done $(date) ==="
