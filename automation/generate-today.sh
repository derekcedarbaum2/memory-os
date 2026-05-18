#!/bin/bash
# generate-today.sh
# Regenerates Vault/Today.md by invoking the `today` skill via headless claude.
# Mirrors the auto-distill-readwise.sh pattern.
#
# Usage:
#   generate-today.sh              # cron mode
#   generate-today.sh --verbose    # echo the prompt + skill output
#
# Exit codes:
#   0 — completed (file written)
#   1 — fatal error (claude not found, lock contention, etc.)

set -euo pipefail

# ---------- config ----------
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"
TODAY_FILE="$VAULT/Today.md"
LOG_DIR="$HOME/.claude/logs"
LOG_FILE="$LOG_DIR/today-$(date +%Y-%m-%d).log"
CLAUDE_BIN="$HOME/.local/bin/claude"

# ---------- args ----------
VERBOSE=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --verbose) VERBOSE=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# ---------- concurrency lock ----------
LOCK_DIR="/tmp/generate-today.lock.d"
if [[ -d "$LOCK_DIR" ]]; then
  LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0) ))
  # Stale-clean if older than 30min — today regen should be fast.
  [[ $LOCK_AGE -gt 1800 ]] && { rmdir "$LOCK_DIR" 2>/dev/null || rm -rf "$LOCK_DIR"; }
fi
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] another generate-today instance is running; exiting" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

# ---------- pre-flight ----------
mkdir -p "$LOG_DIR"
[[ -x "$CLAUDE_BIN" ]] || { echo "claude not found at $CLAUDE_BIN" >&2; exit 1; }
[[ -d "$VAULT" ]] || { echo "vault not found at $VAULT" >&2; exit 1; }

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "=== generate-today start ==="

# ---------- invoke skill ----------
PROMPT="Use the today skill to regenerate Vault/Today.md now. Today is $(date '+%Y-%m-%d (%A)'). Current time: $(date '+%H:%M %Z'). Pull from all sources listed in the skill spec. Write the file and append the log line. Report total lines written."

if [[ "$VERBOSE" -eq 1 ]]; then
  log "PROMPT: $PROMPT"
fi

if out=$("$CLAUDE_BIN" -p "$PROMPT" 2>&1); then
  if [[ "$VERBOSE" -eq 1 ]]; then
    echo "$out" | tee -a "$LOG_FILE"
  else
    echo "$out" >> "$LOG_FILE"
  fi

  # Sanity check — file must exist and be non-trivial
  if [[ -f "$TODAY_FILE" ]]; then
    SIZE=$(wc -l < "$TODAY_FILE" | tr -d ' ')
    log "DONE: Today.md ($SIZE lines)"
  else
    log "WARNING: Today.md not written despite skill returning success"
    exit 1
  fi
else
  log "FAILED: $out"
  exit 1
fi

log "=== generate-today complete ==="
exit 0
