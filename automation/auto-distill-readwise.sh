#!/bin/bash
# auto-distill-readwise.sh
# Daily/backfill runner for the auto-playbook-distill skill.
#
# Iterates over Reading/Articles, Reading/Books, Reading/Tweets.
# For each unprocessed file (per state file), invokes headless claude with the
# auto-playbook-distill skill, passing the source path.
# Skips files whose hash already exists in the state file (idempotency).
#
# Usage:
#   auto-distill-readwise.sh                      # daily mode (cap 5 files per run)
#   auto-distill-readwise.sh --backfill           # full backfill (cap 25 per run; relaunch to continue)
#   auto-distill-readwise.sh --backfill --limit N # custom cap
#   auto-distill-readwise.sh --file <path>        # single-file run (smoke test)
#
# Exit codes:
#   0 — completed (may have processed 0+ files)
#   1 — fatal error (state corruption, missing claude, etc.)

set -euo pipefail

# ---------- config ----------
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"
READING="$VAULT/Reading"
STATE_FILE="$HOME/.claude/state/distilled-readwise.json"
LOG_DIR="$HOME/.claude/logs"
LOG_FILE="$LOG_DIR/auto-distill-$(date +%Y-%m-%d).log"
CLAUDE_BIN="$HOME/.local/bin/claude"

DEFAULT_LIMIT_DAILY=5
DEFAULT_LIMIT_BACKFILL=25

# ---------- args ----------
MODE="daily"
LIMIT=""
SINGLE_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backfill) MODE="backfill"; shift ;;
    --limit) LIMIT="$2"; shift 2 ;;
    --file) SINGLE_FILE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

[[ -z "$LIMIT" ]] && {
  if [[ "$MODE" == "backfill" ]]; then LIMIT="$DEFAULT_LIMIT_BACKFILL"; else LIMIT="$DEFAULT_LIMIT_DAILY"; fi
}

# ---------- concurrency lock ----------
# Prevent self-overlap (e.g. backfill still running when daily fires).
# mkdir is atomic on POSIX; trap releases on any exit.
LOCK_DIR="/tmp/auto-distill-readwise.lock.d"
if [[ -d "$LOCK_DIR" ]]; then
  LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0) ))
  # Stale-clean if older than 2h (a normal run caps far below this).
  [[ $LOCK_AGE -gt 7200 ]] && { rmdir "$LOCK_DIR" 2>/dev/null || rm -rf "$LOCK_DIR"; }
fi
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] another auto-distill instance is running (lock $LOCK_DIR); exiting" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

# ---------- pre-flight ----------
mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$STATE_FILE")"

# Initialize state file if missing
[[ -f "$STATE_FILE" ]] || echo '{}' > "$STATE_FILE"

# Verify claude binary
[[ -x "$CLAUDE_BIN" ]] || { echo "claude not found at $CLAUDE_BIN" >&2; exit 1; }

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "=== auto-distill-readwise mode=$MODE limit=$LIMIT ==="

# ---------- helper: check if file needs processing ----------
needs_processing() {
  local src_path="$1"
  python3 - <<EOF
import json, hashlib, sys
state_path = "$STATE_FILE"
src_path = "$src_path"
try:
  with open(state_path) as f: state = json.load(f)
except Exception:
  state = {}
try:
  with open(src_path, 'rb') as f: h = hashlib.sha256(f.read()).hexdigest()
except Exception as e:
  print('ERROR', e, file=sys.stderr); sys.exit(2)
entry = state.get(src_path)
if entry and entry.get('hash') == h:
  sys.exit(1)  # skip
sys.exit(0)  # process
EOF
}

# ---------- helper: process one file via headless claude ----------
process_file() {
  local src_path="$1"
  local run_id="$(date +%Y%m%d-%H%M%S)-$$"
  local basename="$(basename "$src_path")"

  log "PROCESSING: $basename"

  # Construct the prompt for the skill
  local prompt="Source file: $src_path
Strictness: loose
Run id: $run_id

Use the auto-playbook-distill skill to process this file."

  # Invoke claude headless. --print = single-shot, --skill loads the skill.
  # Capture stdout to log; let the skill itself update state file + log.md.
  local out
  if out=$("$CLAUDE_BIN" -p "$prompt" 2>&1); then
    echo "$out" | tee -a "$LOG_FILE"
    log "DONE: $basename"
    return 0
  else
    log "FAILED: $basename — $out"
    return 1
  fi
}

# ---------- single-file mode (smoke test) ----------
if [[ -n "$SINGLE_FILE" ]]; then
  [[ -f "$SINGLE_FILE" ]] || { log "Single file not found: $SINGLE_FILE"; exit 1; }
  process_file "$SINGLE_FILE"
  log "=== single-file run complete ==="
  exit 0
fi

# ---------- enumerate candidates ----------
log "scanning $READING/Articles, $READING/Books, $READING/Tweets..."

CANDIDATES=()
while IFS= read -r -d '' f; do
  CANDIDATES+=("$f")
done < <(find "$READING/Articles" "$READING/Books" "$READING/Tweets" \
          -type f -name "*.md" \
          ! -name ".*" \
          -print0 2>/dev/null)

log "found ${#CANDIDATES[@]} total source files"

# ---------- filter to unprocessed ----------
TO_PROCESS=()
for f in "${CANDIDATES[@]}"; do
  if needs_processing "$f"; then
    TO_PROCESS+=("$f")
    [[ ${#TO_PROCESS[@]} -ge "$LIMIT" ]] && break
  fi
done

log "${#TO_PROCESS[@]} files to process this run (cap $LIMIT)"

if [[ ${#TO_PROCESS[@]} -eq 0 ]]; then
  log "nothing to do — all current files already distilled"
  log "=== run complete (no-op) ==="
  exit 0
fi

# ---------- process ----------
PROCESSED=0
FAILED=0
for f in "${TO_PROCESS[@]}"; do
  if process_file "$f"; then
    PROCESSED=$((PROCESSED+1))
  else
    FAILED=$((FAILED+1))
  fi
done

log "=== run complete: $PROCESSED processed, $FAILED failed ==="

# Append a roll-up line to vault log.md (the skill itself logs per-file detail)
VAULT_LOG="$VAULT/log.md"
if [[ -f "$VAULT_LOG" ]]; then
  echo "" >> "$VAULT_LOG"
  echo "$(date '+%Y-%m-%d %H:%M') | auto-distill | run-summary | mode=$MODE | $PROCESSED processed, $FAILED failed (cap $LIMIT)" >> "$VAULT_LOG"
fi

exit 0
