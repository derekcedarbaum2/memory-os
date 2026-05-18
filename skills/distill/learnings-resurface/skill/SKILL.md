---
name: learnings-resurface
description: Headless cluster + classify + route across vault interaction memory (session archives, _learnings.md, voice memos). Detects recurring principles, anti-patterns, state observations, commitments, and open questions across ventures. Routes principles/anti-patterns into playbooks via auto-playbook-distill, promotes high-recurrence principles to the MEMORY.md Knowledge Router, optionally creates tasks in the operator's task manager via MCP (or falls back to `_learnings.md` Key Decisions), and notes contradictions for review. Invoked weekly via cron (Sunday 10pm PT) in two phases (cluster, then route) with persisted intermediate state.
version: 2.0.0
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash]
---

> **MCP-agnostic by design.** This skill does not bind to any specific task-manager MCP server. If the operator has a task-manager MCP available (Todoist, Linear, Things, OmniFocus, etc. — anything exposing a task-creation tool like `mcp__<provider>__create_task`), Phase B can route commitment-type clusters there. If no task-manager MCP is available, commitments fall back to `_learnings.md` Key Decisions only. The fallback path is the default; MCP integration is opt-in.

# Learnings Resurface

Cross-vault interaction-memory pattern detector. The third leg of the auto-distill family:
- `auto-playbook-distill` — distills *external* sources (Readwise) into playbooks
- `voice-memo-process` — processes *single* voice-memo transcripts
- `learnings-resurface` — distills *accumulated internal* interaction memory across the whole vault

**v2.0 architecture:** the workflow is split into two phases, each invoked as a separate `claude -p` call by the runner. This bounds each invocation under the API stream's idle-timeout tolerance and provides resumability — phase A's clustering is preserved if phase B fails. Eats the dogfood of `Tech Playbook/working-with-coding-agents.md` *Architecture: deterministic vs. judgment work* (manifest + idempotent fetcher pattern).

## Phases

| Phase | Run by | Cost | Output |
|---|---|---|---|
| **Enumerate** | bash (no LLM) | <1s | `state/runs/<run-id>/enumerate.json` |
| **A — Cluster + Classify** | `claude -p` | ~10–15 min | `state/runs/<run-id>/clusters.json` |
| **Pre-route guard** | bash (no LLM) | <1s | `state/runs/<run-id>/clusters_filtered.json` |
| **B — Route + Log** | `claude -p` | ~10–15 min | `state/runs/<run-id>/routed.json` + actual writes |
| **Finalize** | bash (no LLM) | <1s | updated `state/index.json` + Vault/log.md |

## Input

The user message names which phase to run, plus the run id and mode. Format:

```
Phase: <A | B>
Run id: <YYYYMMDD-HHMMSS-PID>
Mode: <dry-run | live>
Window: <N>            # only used by Phase A
```

The runner ensures the phase contract: Phase A only runs when `enumerate.json` exists; Phase B only runs when `clusters_filtered.json` exists.

## Hard rules (enforced in both phases)

1. **NEVER rewrite or delete content in `_learnings.md` files.** Append-only is a vault invariant.
2. **NEVER edit `Vault/Reading/`.** Readwise wipes it on sync.
3. **NEVER edit `Vault/Personal/`.** Personal scope is excluded from cross-venture clustering.
4. **NEVER include employer source materials in cross-venture clustering.** Employer IP boundary (per memory `feedback_employer_ip_boundary.md`).
5. **NEVER auto-invalidate a principle.** Contradictions get flagged for Derek's review only.
6. **NEVER fabricate clusters.** Every cluster needs ≥2 distinct human sources (not 3 of Derek's own voice memos saying the same thing).
7. **NEVER fabricate quotes.** If quoting a learning entry or session archive line, reproduce verbatim.
8. **NEVER promote to MEMORY.md Router silently.** Only principles with ≥3 sources across ≥2 ventures qualify, and the entry must include a Why line.
9. **Cap: max 5 new patterns routed per run.** Noise control. Excess gets queued to `Vault/raw-sources/_resurface-queue.md` in Phase B.
10. **Use absolute paths** for all writes and `mkdir -p`.

---

# Phase A — Cluster + Classify

## Phase A inputs

When invoked with `Phase: A`:
- `~/.claude/state/learnings-resurface/runs/<run-id>/enumerate.json` — file paths to scan, with mtimes (produced by the bash enumerate step)
- `~/.claude/state/learnings-resurface/index.json` — global state, including `cluster_fingerprints` from prior runs (for cross-run idempotency)
- `~/.claude/projects/<active-project-id>/memory/MEMORY.md` (current Router state — to know what's already promoted)
- `Vault/Playbooks-Index.md` (10 playbook domains for routing principles)
- `Vault/CLAUDE.md` (folder map — to know venture boundaries)

> **Resolving `<active-project-id>`:** the project ID is the kebab-case form of the absolute path Claude Code was invoked from. To find it at runtime, list `~/.claude/projects/` and pick the one with a `memory/MEMORY.md`. If multiple, pick the most recently modified. The `VAULT_MEMORY_DIR` env var overrides this lookup.

## Phase A workflow

### A.1 Read context

Read MEMORY.md, Playbooks-Index.md, CLAUDE.md, and the existing `index.json`. Note which `cluster_fingerprints` are already routed.

### A.2 Read the enumerated corpus

`enumerate.json` lists files in three tiers:
- Primary: session archives in `Vault/AI Toolkit/CC Chat History/` (excluding `Concepts/` and `Indexes/` subfolders)
- Secondary: `_learnings.md` files across vault, EXCEPT under `Vault/Personal/`
- Tertiary: `Vault/Voice Memos/` if present

Skip files <500 bytes (empty scaffolding).

### A.3 Extract candidate signals (atoms)

For each file, extract atoms — short, attributable signal units. An atom has:
- **Source file** (path)
- **Source date** (frontmatter `created` or filename date)
- **Venture context** (parent folder under `Work/`, `Ideas/`, `Professional Development/`, `Company Building/`, etc. — the venture/engagement boundary)
- **Speaker / origin** (Derek's own thinking vs. cited 3rd party — best-effort detection from quotes / "X said")
- **Atom text** (the signal itself, ≤200 chars)
- **Atom type guess** (principle / anti-pattern / state / commitment / open-question)
- **Domain guess** (artifact type / optimization target — see clustering check below)

Atom-types definitions:
- **Principle**: durable truth about a domain. Test: would this still be true in 12 months absent contrary evidence? ("Regulated SMBs require air-gap")
- **Anti-pattern**: durable truth about what doesn't work. ("Hourly billing undersells AI work")
- **State**: current world state, snapshot. ("Acme is in active eval")
- **Commitment**: promise / decision with a binary resolution. ("Promised SSO to Acme by Q3")
- **Open question**: unresolved. ("Do credit unions buy on-prem differently?")

### A.4 Cluster atoms across files

Group atoms by semantic similarity. Within each cluster:
- Drop the cluster if **<3 mentions total** (threshold).
- Drop the cluster if **<2 distinct human sources** (source-diversity rule). 3 mentions all from Derek's own voice memos = noise.
- Drop the cluster if **all sources are within the same week** (likely echo, not pattern).
- Score by **weighted recency**: each atom's contribution = `1 / (1 + days_old / 30)`. Sum across atoms.

**Artifact-type / optimization-target check (mandatory):** atoms only cluster together if they operate on the **same artifact type** AND the **same optimization target**. Two atoms about "multi-pass QA loops" do NOT belong in one cluster if one targets *marketing copy* (optimize for voice/authenticity) and the other targets *skill logic / backend automation* (optimize for soundness/gap-detection). Surface semantic similarity is not enough — same artifact, same optimization target is the bar. When in doubt, split into two clusters and let routing send them to different destinations.

Common artifact-type / optimization-target pairs to keep separate:
- Marketing copy / decks / one-pagers — optimize for voice, first-principles framing, authenticity
- Skill logic / analysis output / backend automation — optimize for soundness, gap detection, contradiction catching
- Pricing / packaging / offer design — optimize for buyer clarity, dollarized counterfactual
- Visual design / brand identity — optimize for differentiation, restraint
- Product positioning / wedge — optimize for ICP-buyer specificity, defensibility

### A.5 Detect contradictions (principles + anti-patterns only)

For each `principle` or `anti-pattern` cluster:
- Search MEMORY.md Router and existing playbook topic files for an opposing statement.
- Search the corpus itself for atoms that contradict the cluster.
- **Before flagging contested, confirm the apparent contradiction is real.** A real contradiction holds *within the same artifact type and optimization target*. If the "contradicting" atoms apply to a different artifact type or optimize for a different target, that's a category boundary — NOT a contradiction. Resolution: the two clusters were misclustered in A.4; split them and route each to its own destination. Re-run A.4's artifact-type/optimization-target check on any contested cluster before marking it contested.
- If contradiction found AND it holds within a single artifact type / optimization target, mark the cluster `status: contested` and note the contradicting source(s). Do NOT auto-invalidate. Surface for Derek's review.

### A.6 Write `clusters.json`

Output schema:

```json
{
  "run_id": "<id>",
  "phase": "A",
  "completed_at": "<ISO 8601>",
  "window_days": <N>,
  "atoms_extracted": <int>,
  "clusters_formed": <int>,
  "clusters": [
    {
      "fingerprint": "<sha256 of normalized title + sorted source paths>",
      "title": "<≤80 chars>",
      "type": "principle | anti-pattern | state | commitment | open-question",
      "domain": "<artifact type / optimization target>",
      "mentions": <int>,
      "ventures": ["<venture>", ...],
      "cross_venture": <bool>,
      "recency_score": <float>,
      "status": "active | contested",
      "contradicting_sources": [...] | null,
      "source_atoms": [
        { "file": "<path>", "date": "YYYY-MM-DD", "atom": "<text>" }
      ],
      "proposed_destinations": {
        "memory_file": "reference_<slug>.md" | null,
        "playbook_file": "<absolute path>" | null,
        "router_eligible": <bool>,
        "task_destination": { "mcp_tool": "<tool_name>", "project_or_list": "<id>" } | null,
        "learnings_file": "<absolute path>" | null
      }
    }
  ]
}
```

Phase A writes ONLY this file. No other writes. No file modifications outside `~/.claude/state/learnings-resurface/runs/<run-id>/`.

### A.7 Stdout (for the runner)

```
[learnings-resurface][phase-A] atoms=<A> clusters=<C> ready_for_route
```

---

# Phase B — Route + Log

## Phase B inputs

When invoked with `Phase: B`:
- `~/.claude/state/learnings-resurface/runs/<run-id>/clusters_filtered.json` — clusters that survived the bash idempotency pre-guard
- `~/.claude/state/learnings-resurface/index.json` — global state
- The full vault (read access) for merging into existing playbook topic files

## Phase B workflow

### B.1 Read clusters

Read `clusters_filtered.json`. Each cluster has full fingerprint + proposed_destinations. Bash already filtered out clusters whose destinations exist (idempotency guard).

### B.2 Apply 5-cap

Sort surviving clusters by `recency_score` descending. Take top 5. Surplus → write each as one line to `Vault/raw-sources/_resurface-queue.md` (create file if absent).

### B.3 Route each cluster per type

#### Principle / Anti-pattern (durable)
- **Distill into the playbook** at `cluster.proposed_destinations.playbook_file`. Format as scorecard / decision-trigger / anti-pattern detector / fillable template — NOT narrative. Source-tag inline. Merge into existing topic file when a section fits; create a new topic file only if no section fits AND the dimension is genuinely new.
- **If `router_eligible: true`** AND `status: active`:
  - Write `~/.claude/projects/<active-project-id>/memory/<memory_file>` with the standard memory file frontmatter (`name`, `description`, `type: reference`).
  - Append `- [Title](<memory_file>) — one-line hook` to MEMORY.md.
- **If `status: contested`**: write the memory file with `**Status:** contested` + a "Contradicting evidence:" section. Skip Router promotion.

#### State (decaying)
- Append a Learning entry to `cluster.proposed_destinations.learnings_file` under `## Learnings`. Format: `- [pattern] *(resurfaced YYYY-MM-DD from N atoms across [sources])*`.
- If multiple ventures contributed, append to each venture's `_learnings.md` with a cross-venture note.

#### Commitment (track to resolution)
- **If `cluster.proposed_destinations.task_destination` is not null AND a matching MCP task-creation tool is available** in the agent's allowed-tools at runtime: invoke that tool to create a task. Title: `[Commitment] <text>`. Description includes contributing source paths. Priority: medium / P2 (or whatever the operator's task-manager-MCP convention dictates — read the operator's `MEMORY.md` or `CLAUDE.md` for any priority-mapping convention; if none, use the MCP's default).
- **If `task_destination` is null OR the MCP tool is unavailable**: skip task creation. Append to `_learnings.md` Key Decisions only.
- **Always** append a row to the venture's `_learnings.md` Key Decisions table regardless of whether a task was created.

#### Open question (active until answered)
- Append to `cluster.proposed_destinations.learnings_file` `## Open Threads` section. Format: `- [question] — surfaced YYYY-MM-DD from [sources]`.

### B.4 Update routing artifacts

- If a new playbook topic file was created, update its playbook README and `Vault/Playbooks-Index.md` "Active Playbook Status" table.
- If a Router promotion occurred, MEMORY.md is already updated in B.3.

### B.5 Append to `Vault/log.md`

One roll-up line + one line per routed cluster. See "Logging format" below.

### B.6 Write `routed.json`

Output schema:

```json
{
  "run_id": "<id>",
  "phase": "B",
  "completed_at": "<ISO 8601>",
  "clusters_routed": <int>,
  "clusters_queued": <int>,
  "router_promotions": ["<memory-file>", ...],
  "playbook_distills": ["<absolute path>", ...],
  "learnings_appends": ["<absolute path>", ...],
  "tasks_created": [{ "mcp_tool": "<name>", "task_id": "<id>", "title": "<text>" }, ...],
  "contested": ["<memory-file>", ...]
}
```

### B.7 Stdout (for the runner)

```
[learnings-resurface][phase-B] routed=<R> queued=<Q> promotions=<P> distills=<D> contested=<X>
```

## Logging format

For `Vault/log.md`:

```
YYYY-MM-DD HH:MM | learnings-resurface | run-summary | window=Nd | <atoms> atoms → <clusters> clusters → <routed> routed (<P> principle / <S> state / <C> commitment / <Q> question / <X> contested), <queued> queued
YYYY-MM-DD HH:MM | learnings-resurface | <type> | <title> | mentions=<N> ventures=[<list>] | routed → <destination>
```

Match existing pipe-separated, grep-friendly style.

## Dry-run mode

For both phases, `Mode: dry-run` means: read everything, produce the same JSON output, but **do not write to anything outside `~/.claude/state/learnings-resurface/runs/<run-id>/`**. No MEMORY.md edits, no playbook edits, no `_learnings.md` edits, no MCP task creation, no Vault/log.md append. Stdout prefix every action line with `[DRY-RUN] would: `.

## Anti-patterns (avoid these)

- **Treating Derek's own thinking as multi-source signal.** A cluster of "Derek mentioned X in 4 voice memos" is one source, not four. The diversity rule guards against this.
- **Promoting state observations to the Router.** The Router is for timeless principles only. State is venture-local.
- **Auto-invalidating principles.** Contradictions surface for review; Derek decides.
- **Creating new playbook domains.** Stay within the 10 in `Playbooks-Index.md`. If a pattern doesn't fit, queue it.
- **Routing to a task-manager destination that doesn't exist or whose MCP isn't configured.** If `task_destination` is null or the corresponding MCP tool isn't in the agent's allowed-tools, skip task creation and write to `_learnings.md` Key Decisions only. Do not error.
- **Logging in a chatty / narrative tone.** Match the existing `Vault/log.md` style — one line, pipe-separated, grep-friendly.
- **Cross-phase work.** Phase A does not write to MEMORY.md or playbooks; Phase B does not re-cluster. The contract is the JSON files in `state/runs/<run-id>/`.

## Edge cases

- **Empty corpus** (no files in window) → Phase A writes `clusters: []`, Phase B no-ops.
- **All clusters fail diversity rule** → same as empty.
- **Cluster fingerprint matches an entry in `index.json`'s `cluster_fingerprints`** → bash pre-guard removes it from `clusters_filtered.json` before Phase B runs (skip silently). EXCEPTION: if `mentions` count grew past a threshold (e.g., previously 3, now 5 → eligible for Router promotion), bash keeps it in for Phase B.
- **No matching playbook for a principle** → set `proposed_destinations.playbook_file: null`. Phase B queues it.
- **No task-manager MCP available, or no matching destination for the venture** → `proposed_destinations.task_destination: null`. Phase B writes to `_learnings.md` Key Decisions only.
- **`Vault/Voice Memos/` is empty or missing** → enumeration skips silently.
- **A `_learnings.md` file is just scaffolding (no real entries under `## Learnings`)** → Phase A still scans for entries; expect none, don't error.

## Reference: venture → task-destination mapping (operator-specific)

If the operator has a task-manager MCP configured and wants commitments routed there, they should define a venture → destination mapping in their `MEMORY.md` or in a `learnings-resurface.config.md` file the agent reads at runtime. The mapping has the shape:

```
- <venture folder name>: { mcp_tool: "<tool_name>", project_or_list: "<id-or-name>" }
```

Example (the operator's specifics, not prescriptive):

```
- Inbox: { mcp_tool: "mcp__todoist__create_tasks", project_or_list: "<their-todoist-inbox-id>" }
- Engineering: { mcp_tool: "mcp__linear__create_issue", project_or_list: "<their-linear-team-id>" }
```

If no mapping exists for a venture or no task-manager MCP is configured at all, set `proposed_destinations.task_destination: null` and route the commitment to `_learnings.md` Key Decisions only. The skill works fully without any task-manager integration — MCP routing is opt-in.
