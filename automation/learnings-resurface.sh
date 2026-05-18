#!/bin/bash
# learnings-resurface.sh (v2.0 — two-phase)
#
# Weekly runner for the learnings-resurface skill.
# Decomposes the work into bounded phases, persisted via state files.
#
#   1. Enumerate (bash)              → state/runs/<run-id>/enumerate.json
#   2. Phase A: cluster + classify   → state/runs/<run-id>/clusters.json
#   3. Pre-route guard (bash)        → state/runs/<run-id>/clusters_filtered.json
#   4. Phase B: route + log          → state/runs/<run-id>/routed.json + actual writes
#   5. Finalize (bash)               → state/index.json updates + Vault/log.md
#
# Each claude phase is bounded by `timeout 1800` (30 min wall clock) and
# `--max-turns 80`. If either bound is hit, the phase fails cleanly and the
# run can be resumed by re-invoking with --resume <run-id> --from-phase <A|B>.
#
# Usage:
#   learnings-resurface.sh                                 # weekly (90d, live)
#   learnings-resurface.sh --dry-run                       # preview only
#   learnings-resurface.sh --window N                      # custom lookback days
#   learnings-resurface.sh --resume <id> --from-phase B    # resume failed run

set -euo pipefail

# ---------- config ----------
VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"
STATE_ROOT="$HOME/.claude/state/learnings-resurface"
STATE_INDEX="$STATE_ROOT/index.json"
LOG_DIR="$HOME/.claude/logs"
LOG_FILE="$LOG_DIR/learnings-resurface-$(date +%Y-%m-%d).log"
CLAUDE_BIN="$HOME/.local/bin/claude"

DEFAULT_WINDOW=90
PHASE_TIMEOUT=1800   # 30 min wall clock per phase
MAX_TURNS=80

# ---------- args ----------
MODE="live"
WINDOW="$DEFAULT_WINDOW"
RESUME_RUN_ID=""
FROM_PHASE=""
SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-0}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) MODE="dry-run"; shift ;;
    --window) WINDOW="$2"; shift 2 ;;
    --resume) RESUME_RUN_ID="$2"; shift 2 ;;
    --from-phase) FROM_PHASE="$2"; shift 2 ;;
    --skip-preflight) SKIP_PREFLIGHT="1"; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# ---------- env-var overrides for portability ----------
# Allow operators to point at non-default vault / claude binary without editing the script.
[[ -n "${VAULT_PATH:-}" ]] && VAULT="$VAULT_PATH"
[[ -n "${CLAUDE_BIN_OVERRIDE:-}" ]] && CLAUDE_BIN="$CLAUDE_BIN_OVERRIDE"

# ---------- concurrency lock ----------
LOCK_DIR="/tmp/learnings-resurface.lock.d"
if [[ -d "$LOCK_DIR" ]]; then
  LOCK_AGE=$(( $(date +%s) - $(stat -f %m "$LOCK_DIR" 2>/dev/null || echo 0) ))
  [[ $LOCK_AGE -gt 7200 ]] && { rmdir "$LOCK_DIR" 2>/dev/null || rm -rf "$LOCK_DIR"; }
fi
if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] another learnings-resurface instance is running (lock $LOCK_DIR); exiting" >&2
  exit 0
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT

# ---------- pre-flight: directory + state setup ----------
mkdir -p "$LOG_DIR"
mkdir -p "$STATE_ROOT/runs"
[[ -f "$STATE_INDEX" ]] || echo '{"runs": {}, "cluster_fingerprints": {}}' > "$STATE_INDEX"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

# ---------- pre-flight: install / dependency checks ----------
# Verifies the runner's environment before any work. Hard-fails when a missing
# piece would cause silent zero-output. Soft-warns when a missing piece reduces
# functionality but doesn't break the run.
#
# Skip with --skip-preflight (e.g., on a machine you've already verified).

preflight_check() {
  local hard_fail=0
  local soft_warn=0
  local fail_messages=()

  log "pre-flight: checking environment..."

  # Hard: claude binary executable
  if [[ -x "$CLAUDE_BIN" ]]; then
    log "  ✓ claude binary: $CLAUDE_BIN"
  else
    fail_messages+=("claude binary not executable at $CLAUDE_BIN — install Claude Code or set CLAUDE_BIN_OVERRIDE")
    hard_fail=1
  fi

  # Hard: vault path exists
  if [[ -d "$VAULT" ]]; then
    log "  ✓ vault path: $VAULT"
  else
    fail_messages+=("vault directory not found: $VAULT — set VAULT_PATH env var or edit runner config")
    hard_fail=1
  fi

  # Hard: vault has CLAUDE.md (folder map convention required by skill)
  if [[ -f "$VAULT/CLAUDE.md" ]]; then
    log "  ✓ vault has CLAUDE.md (folder map)"
  else
    fail_messages+=("missing $VAULT/CLAUDE.md — install vault-conventions: https://github.com/derekcedarbaum2/vault-conventions")
    hard_fail=1
  fi

  # Hard: at least one _learnings.md exists somewhere
  local learnings_count
  learnings_count=$(find "$VAULT" -name "_learnings.md" -not -path "*/Personal/*" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$learnings_count" -gt 0 ]]; then
    log "  ✓ found $learnings_count _learnings.md files"
  else
    fail_messages+=("no _learnings.md files found in $VAULT (excluding Personal/) — this skill needs accumulated content. Install vault-conventions, then use Claude Code for ~6+ weeks before running this skill. See ECOSYSTEM.md step 11.")
    hard_fail=1
  fi

  # Hard: at least one MEMORY.md exists under ~/.claude/projects/*/memory/
  # (Path slug depends on cwd; check for ANY existing memory dir.)
  local memory_count
  memory_count=$(find "$HOME/.claude/projects" -mindepth 3 -maxdepth 3 -name "MEMORY.md" -path "*/memory/*" 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$memory_count" -gt 0 ]]; then
    log "  ✓ found $memory_count MEMORY.md auto-memory file(s)"
  else
    fail_messages+=("no MEMORY.md auto-memory file found under ~/.claude/projects/*/memory/ — install ai-knowledge-system: https://github.com/derekcedarbaum2/ai-knowledge-system")
    hard_fail=1
  fi

  # Soft warn: session archives directory
  if [[ -d "$VAULT/AI Toolkit/CC Chat History" ]]; then
    local archive_count
    archive_count=$(find "$VAULT/AI Toolkit/CC Chat History" -maxdepth 1 -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
    log "  ✓ session archives: $archive_count files"
  else
    log "  ⚠ no session archives at $VAULT/AI Toolkit/CC Chat History/ — install the SessionEnd archive-session.sh hook from vault-conventions for richer corpus"
    soft_warn=$((soft_warn + 1))
  fi

  # Soft warn: Playbooks-Index.md (principle routing falls back to queue without it)
  if [[ -f "$VAULT/Playbooks-Index.md" ]]; then
    log "  ✓ Playbooks-Index.md found (principle routing enabled)"
  else
    log "  ⚠ no $VAULT/Playbooks-Index.md — principle/anti-pattern routing will queue. Install note-highlight-indexer for the playbook system: https://github.com/derekcedarbaum2/note-highlight-indexer"
    soft_warn=$((soft_warn + 1))
  fi

  # Soft warn: voice memos
  if [[ -d "$VAULT/Voice Memos" ]]; then
    log "  ✓ voice memos directory exists"
  else
    log "  ⚠ no $VAULT/Voice Memos/ — voice-memo tier of corpus will be empty (this is fine if you don't use voice memos)"
  fi

  # Hard fail summary
  if [[ "$hard_fail" -gt 0 ]]; then
    log ""
    log "pre-flight: ✗ FAILED ($hard_fail blocker(s), $soft_warn warning(s))"
    log ""
    log "Required pieces missing:"
    for msg in "${fail_messages[@]}"; do
      log "  - $msg"
    done
    log ""
    log "This skill runs on top of an established system. To set it up from scratch,"
    log "follow the install sequence in claude-code-setup ECOSYSTEM.md (step 11):"
    log "  https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md"
    log ""
    log "Override with --skip-preflight if you know what you're doing."
    exit 1
  fi

  log "pre-flight: ✓ ready ($soft_warn warning(s))"
}

if [[ "$SKIP_PREFLIGHT" != "1" ]]; then
  preflight_check
else
  log "pre-flight: SKIPPED (--skip-preflight)"
fi

# ---------- run id ----------
if [[ -n "$RESUME_RUN_ID" ]]; then
  RUN_ID="$RESUME_RUN_ID"
  log "=== learnings-resurface RESUME run-id=$RUN_ID from-phase=$FROM_PHASE mode=$MODE ==="
else
  RUN_ID="$(date +%Y%m%d-%H%M%S)-$$"
  log "=== learnings-resurface mode=$MODE window=${WINDOW}d run-id=$RUN_ID ==="
fi

RUN_DIR="$STATE_ROOT/runs/$RUN_ID"
mkdir -p "$RUN_DIR"

# ============================================================
# Step 1 — Enumerate (bash, no LLM)
# ============================================================
enumerate_corpus() {
  local enum_file="$RUN_DIR/enumerate.json"
  if [[ -f "$enum_file" ]]; then
    log "enumerate.json already exists, skipping enumerate step"
    return 0
  fi

  log "enumerating corpus (window=${WINDOW}d)..."

  python3 - <<EOF > "$enum_file"
import os, json, time, fnmatch

VAULT = "$VAULT"
WINDOW_DAYS = $WINDOW
NOW = time.time()
CUTOFF = NOW - (WINDOW_DAYS * 86400)
MIN_BYTES = 500

def collect(roots, exclude_patterns=None):
    out = []
    exclude_patterns = exclude_patterns or []
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            # prune excluded subdirs in-place
            dirnames[:] = [d for d in dirnames if not any(fnmatch.fnmatch(os.path.join(dirpath, d), p) for p in exclude_patterns)]
            for fn in filenames:
                if not fn.endswith('.md'): continue
                fp = os.path.join(dirpath, fn)
                try:
                    st = os.stat(fp)
                except OSError:
                    continue
                if st.st_mtime < CUTOFF: continue
                if st.st_size < MIN_BYTES: continue
                out.append({
                    "path": fp,
                    "size": st.st_size,
                    "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime)),
                })
    return out

# Primary: session archives (top-level only — exclude Concepts/ and Indexes/)
primary = collect(
    [os.path.join(VAULT, "AI Toolkit/CC Chat History")],
    exclude_patterns=["*/Concepts", "*/Indexes"],
)

# Secondary: _learnings.md files across vault, excluding Personal/
def find_learnings():
    out = []
    for dirpath, dirnames, filenames in os.walk(VAULT):
        # exclude Personal subtree
        if "/Personal" in dirpath or dirpath.endswith("/Personal"):
            dirnames[:] = []
            continue
        if "_learnings.md" in filenames:
            fp = os.path.join(dirpath, "_learnings.md")
            try:
                st = os.stat(fp)
            except OSError:
                continue
            if st.st_size < MIN_BYTES: continue
            out.append({
                "path": fp,
                "size": st.st_size,
                "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(st.st_mtime)),
            })
    return out
secondary = find_learnings()

# Tertiary: voice memos
tertiary = collect([os.path.join(VAULT, "Voice Memos")])

result = {
    "window_days": WINDOW_DAYS,
    "enumerated_at": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(NOW)),
    "primary_session_archives": primary,
    "secondary_learnings": secondary,
    "tertiary_voice_memos": tertiary,
    "counts": {
        "primary": len(primary),
        "secondary": len(secondary),
        "tertiary": len(tertiary),
    }
}
print(json.dumps(result, indent=2))
EOF

  local pcount scount tcount
  pcount=$(python3 -c "import json; print(json.load(open('$enum_file'))['counts']['primary'])")
  scount=$(python3 -c "import json; print(json.load(open('$enum_file'))['counts']['secondary'])")
  tcount=$(python3 -c "import json; print(json.load(open('$enum_file'))['counts']['tertiary'])")
  log "enumerate complete: primary=$pcount secondary=$scount tertiary=$tcount"
}

# ============================================================
# Step 2 — Phase A: cluster + classify (claude -p)
# ============================================================
run_phase_a() {
  local clusters_file="$RUN_DIR/clusters.json"
  if [[ -f "$clusters_file" ]]; then
    log "clusters.json already exists for $RUN_ID, skipping Phase A"
    return 0
  fi

  log "Phase A: invoking claude (timeout=${PHASE_TIMEOUT}s, max-turns=${MAX_TURNS})..."

  local prompt="Phase: A
Run id: $RUN_ID
Mode: $MODE
Window: $WINDOW

Use the learnings-resurface skill, Phase A workflow.

Inputs:
- Corpus enumeration: $RUN_DIR/enumerate.json
- Global state: $STATE_INDEX
- Read MEMORY.md, Vault/Playbooks-Index.md, Vault/CLAUDE.md as the skill instructs

Output: write Phase A's clusters.json to $RUN_DIR/clusters.json per the schema in SKILL.md section A.6. Then exit. Do NOT route, do NOT update memory, do NOT touch playbooks or _learnings.md — that is Phase B's job. End your turn after writing clusters.json."

  if timeout "$PHASE_TIMEOUT" "$CLAUDE_BIN" -p --max-turns "$MAX_TURNS" "$prompt" 2>&1 | tee -a "$LOG_FILE"; then
    if [[ -f "$clusters_file" ]]; then
      local count
      count=$(python3 -c "import json; print(len(json.load(open('$clusters_file')).get('clusters', [])))")
      log "Phase A complete: $count clusters written to $clusters_file"
      return 0
    else
      log "Phase A returned 0 but did not write clusters.json"
      return 1
    fi
  else
    local ec=$?
    log "Phase A FAILED (exit $ec)"
    return $ec
  fi
}

# ============================================================
# Step 3 — Pre-route guard (bash, no LLM)
# ============================================================
preroute_guard() {
  local clusters_file="$RUN_DIR/clusters.json"
  local filtered_file="$RUN_DIR/clusters_filtered.json"

  [[ -f "$clusters_file" ]] || { log "no clusters.json — cannot pre-route"; return 1; }
  if [[ -f "$filtered_file" ]]; then
    log "clusters_filtered.json already exists, skipping pre-route guard"
    return 0
  fi

  log "pre-route guard: filtering by destination existence + fingerprint..."

  python3 - <<EOF
import json, os

clusters_path = "$clusters_file"
filtered_path = "$filtered_file"
index_path = "$STATE_INDEX"
memory_dir = os.path.expanduser("~/.claude/projects/-Users-derekcedarbaum/memory")

with open(clusters_path) as f:
    data = json.load(f)
with open(index_path) as f:
    idx = json.load(f)

prior_fps = idx.get("cluster_fingerprints", {})
clusters = data.get("clusters", [])

kept = []
skipped = []
for c in clusters:
    fp = c.get("fingerprint", "")
    title = c.get("title", "")
    proposed = c.get("proposed_destinations") or {}
    mem_file = proposed.get("memory_file")

    # Skip if memory file already exists (durable destination already populated)
    if mem_file:
        full = os.path.join(memory_dir, mem_file)
        if os.path.exists(full):
            skipped.append({"reason": "memory_file_exists", "title": title, "memory_file": mem_file})
            continue

    # Skip if fingerprint already routed in a prior run AND mentions count hasn't grown enough
    if fp in prior_fps:
        prior = prior_fps[fp]
        prior_mentions = prior.get("mentions", 0)
        new_mentions = c.get("mentions", 0)
        # Only re-route if mentions grew AND it's now Router-eligible (and wasn't before)
        if new_mentions <= prior_mentions:
            skipped.append({"reason": "fingerprint_already_routed", "title": title, "prior_mentions": prior_mentions})
            continue

    kept.append(c)

out = {
    "run_id": data.get("run_id"),
    "phase": "filtered",
    "kept": kept,
    "skipped": skipped,
    "kept_count": len(kept),
    "skipped_count": len(skipped),
}
with open(filtered_path, "w") as f:
    json.dump(out, f, indent=2)
print(f"[preroute] kept={len(kept)} skipped={len(skipped)}")
EOF
}

# ============================================================
# Step 4 — Phase B: route + log (claude -p)
# ============================================================
run_phase_b() {
  local filtered_file="$RUN_DIR/clusters_filtered.json"
  local routed_file="$RUN_DIR/routed.json"

  [[ -f "$filtered_file" ]] || { log "no clusters_filtered.json — cannot route"; return 1; }
  if [[ -f "$routed_file" ]]; then
    log "routed.json already exists for $RUN_ID, skipping Phase B"
    return 0
  fi

  # Short-circuit: nothing to route
  local kept
  kept=$(python3 -c "import json; print(json.load(open('$filtered_file')).get('kept_count', 0))")
  if [[ "$kept" -eq 0 ]]; then
    log "Phase B: no clusters to route (0 kept after pre-route guard)"
    echo '{"run_id": "'"$RUN_ID"'", "phase": "B", "clusters_routed": 0, "clusters_queued": 0, "router_promotions": [], "playbook_distills": [], "learnings_appends": [], "todoist_tasks_created": [], "contested": []}' > "$routed_file"
    return 0
  fi

  log "Phase B: invoking claude (timeout=${PHASE_TIMEOUT}s, max-turns=${MAX_TURNS}, kept=$kept)..."

  local prompt="Phase: B
Run id: $RUN_ID
Mode: $MODE

Use the learnings-resurface skill, Phase B workflow.

Inputs:
- Filtered clusters: $RUN_DIR/clusters_filtered.json
- Global state: $STATE_INDEX

Output: execute the route + log workflow per SKILL.md section B. Apply 5-cap. Write each cluster to its proposed destinations (memory file, MEMORY.md index line, playbook distill, _learnings.md append, Todoist task — only what type+rules require). Append per-cluster + roll-up lines to Vault/log.md. Write Phase B's routed.json to $RUN_DIR/routed.json per the schema in SKILL.md section B.6. End your turn after writing routed.json."

  if timeout "$PHASE_TIMEOUT" "$CLAUDE_BIN" -p --max-turns "$MAX_TURNS" "$prompt" 2>&1 | tee -a "$LOG_FILE"; then
    if [[ -f "$routed_file" ]]; then
      log "Phase B complete: routed.json written"
      return 0
    else
      log "Phase B returned 0 but did not write routed.json"
      return 1
    fi
  else
    local ec=$?
    log "Phase B FAILED (exit $ec)"
    return $ec
  fi
}

# ============================================================
# Step 5 — Finalize (bash, no LLM)
# ============================================================
finalize() {
  local routed_file="$RUN_DIR/routed.json"
  local clusters_file="$RUN_DIR/clusters.json"

  [[ -f "$routed_file" ]] || { log "no routed.json — cannot finalize"; return 1; }

  log "finalizing: updating index.json..."

  python3 - <<EOF
import json, time, os

index_path = "$STATE_INDEX"
routed_path = "$routed_file"
clusters_path = "$clusters_file"
run_id = "$RUN_ID"
mode = "$MODE"
window = $WINDOW

with open(index_path) as f:
    idx = json.load(f)
with open(routed_path) as f:
    routed = json.load(f)
with open(clusters_path) as f:
    clusters = json.load(f)

now = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())
idx["last_run"] = now

idx.setdefault("runs", {})[run_id] = {
    "completed_at": now,
    "mode": mode,
    "window_days": window,
    "atoms_extracted": clusters.get("atoms_extracted"),
    "clusters_formed": clusters.get("clusters_formed"),
    "clusters_routed": routed.get("clusters_routed"),
    "clusters_queued": routed.get("clusters_queued"),
    "router_promotions": routed.get("router_promotions", []),
    "playbook_distills": routed.get("playbook_distills", []),
    "learnings_appends": routed.get("learnings_appends", []),
    "todoist_tasks_created": routed.get("todoist_tasks_created", []),
    "contested": routed.get("contested", []),
}

# Merge new fingerprints from this run
fps = idx.setdefault("cluster_fingerprints", {})
for c in clusters.get("clusters", []):
    fp = c.get("fingerprint")
    if not fp: continue
    fps[fp] = {
        "first_seen": fps.get(fp, {}).get("first_seen", now),
        "last_seen": now,
        "title": c.get("title"),
        "type": c.get("type"),
        "mentions": c.get("mentions"),
        "ventures": c.get("ventures", []),
        "memory_file": (c.get("proposed_destinations") or {}).get("memory_file"),
        "playbook_file": (c.get("proposed_destinations") or {}).get("playbook_file"),
    }

with open(index_path, "w") as f:
    json.dump(idx, f, indent=2)
print(f"[finalize] index updated: run={run_id} routed={routed.get('clusters_routed', 0)}")
EOF

  log "finalize complete"
}

# ============================================================
# Orchestration
# ============================================================
START_PHASE="${FROM_PHASE:-}"

if [[ -z "$START_PHASE" ]] || [[ "$START_PHASE" == "enumerate" ]]; then
  enumerate_corpus
  START_PHASE="A"
fi

if [[ "$START_PHASE" == "A" ]]; then
  run_phase_a || exit 1
  START_PHASE="preroute"
fi

if [[ "$START_PHASE" == "preroute" ]]; then
  preroute_guard
  START_PHASE="B"
fi

if [[ "$START_PHASE" == "B" ]]; then
  run_phase_b || exit 1
  START_PHASE="finalize"
fi

if [[ "$START_PHASE" == "finalize" ]]; then
  finalize
fi

# ---------- final stdout summary ----------
ROUTED=$(python3 -c "import json; print(json.load(open('$RUN_DIR/routed.json'))['clusters_routed'])" 2>/dev/null || echo "?")
log "=== run complete: routed=$ROUTED ==="

# Append a roll-up line to vault log.md if live mode and Phase B fully ran
if [[ "$MODE" == "live" ]] && [[ -f "$RUN_DIR/routed.json" ]]; then
  VAULT_LOG="$VAULT/log.md"
  if [[ -f "$VAULT_LOG" ]]; then
    # The skill itself already wrote per-cluster lines in Phase B; this is the runner-level marker
    {
      echo ""
      echo "$(date '+%Y-%m-%d %H:%M') | learnings-resurface | runner | mode=$MODE window=${WINDOW}d run-id=$RUN_ID routed=$ROUTED"
    } >> "$VAULT_LOG"
  fi
fi

exit 0
