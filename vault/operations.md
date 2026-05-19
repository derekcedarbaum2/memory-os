---
title: Operations — process docs separated from CLAUDE.md
type: reference
status: active
classification: internal
created: 2026-05-17
updated: 2026-05-17
author: "Derek Cedarbaum"
tags: [kind:pipeline, domain:claude-code, decay:medium]
---

# Operations

Process docs that used to live in `~/.claude/CLAUDE.md`. Pulled out 2026-05-17 because they decay faster than the identity/preference layer in CLAUDE.md. Load on demand — when working on a vault file, hook, cron, skill, MCP server, or memory entry.

## YAML frontmatter (all vault `.md` and memory `.md`)

Every markdown file in the vault or memory dir should open with:

```yaml
---
title: [document title]
type: [prd | reference | meeting | cta | research | concept | session | essay | idea | ephemeral]
status: [draft | active | approved | archived]
classification: [public | internal | confidential | unclassified]
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "Derek Cedarbaum"
tags: [<controlled vocab — see ~/.claude/reference/tag-vocabulary.md>]
---
```

Optional fields as applicable: `product`, `program`, `related: [[wiki-links]]`, `source`, `owner`, `due`.

**Tags are required and use the controlled vocabulary** at `~/.claude/reference/tag-vocabulary.md`. Never `tags: []`. If no controlled tag fits, add the new term to the vocabulary file *first*.

Backfill frontmatter (including tags) when editing an old file without it.

## Citations on every claim (`_learnings.md` and `_strategy.md`)

Every bullet under `## Learnings`, `## Anti-patterns`, `## Principles`, `## Decisions`, or any claim-shaped section in a venture's `_learnings.md` or `_strategy.md` should end with a source link in one of these forms:

- `[[session-archive-name]]` — the chat that produced the insight
- `[[voice-memo-name]]` — voice memo source
- `[[document-name]]` — vault doc that documents the underlying event
- `(YYYY-MM-DD)` — inline date for in-conversation observations with no archived source

Open Threads bullets are exempt (they describe state, not claims).

**Why:** Unsourced claims rot silently and lose provenance — when a claim is later questioned or contradicted, the source is unrecoverable. GBrain-style self-citation is the cheap counter; the vault grows graph-shaped instead of pile-shaped.

**Backfill rule:** When editing an existing `_learnings.md`, add citations to the bullets you touch; don't backfill the whole file. `vault-lint` check 2f flags unsourced claim bullets as Warning.

## Cron windows (shared-file write awareness)

Three crons fire and write to shared vault files:

- **7:00 AM PT (daily)** — `monologue-sync.sh` writes to `Vault/Voice Memos/`, may invoke `/voice-memo-process` which can update memos and add Todoist tasks.
- **7:15 AM, 11:00 AM, 2:00 PM, 5:00 PM PT (daily)** — `generate-today.sh` regenerates `Vault/Today.md` (whole-file overwrite). Appends a one-line entry to `Vault/log.md`.
- **7:30 AM PT (daily)** — `auto-distill-readwise.sh` writes to playbook topic files in `Vault/Company Building/Startup Playbook/` (and other domain playbooks), `Vault/Playbooks-Index.md`, `~/.claude/state/distilled-readwise.json`, and appends to `Vault/log.md`.

Both scripts use `mkdir`-based lockdirs in `/tmp/` to prevent self-overlap (stale-cleaned after 2h). Interactive sessions don't lock. **If editing shared files between 7:00–8:00 AM PT, expect possible conflicts — prefer to wait or coordinate.**

## Memory writing protocol

Auto-memory at `~/.claude/projects/-Users-derekcedarbaum/memory/`. Subfolder structure (2026-05-17 reorg):

```
memory/
  MEMORY.md          # Hot pinboard — always loaded, ≤80 lines
  INDEX.md           # Cold pointers — read on demand
  user/              # kind:identity (Derek, family, body)
  feedback/          # kind:feedback (corrections, confirmations, preferences)
  principle/         # kind:principle (operating heuristics that fire at decision time)
  location/          # kind:location (pointers to canonical files outside memory)
  pipeline/          # kind:pipeline (system docs — crons, MCPs, hooks, routing)
```

Note: `project_*.md` files **do not live in memory anymore.** Venture/engagement state lives in the vault `_learnings.md` for that venture. Memory dir is for cross-session patterns (feedback, principles, locations, pipelines, identity), not project state.

### When to save a memory

- **user/identity** — facts about Derek, family, personal context. Save immediately on first mention.
- **feedback** — when Derek corrects or confirms an approach (both directions). Save with brief Why.
- **principle** — when an insight is decision-time-load-bearing across multiple future tasks (not a one-off observation). Should fire on every relevant task without being re-derived.
- **location** — when learning a canonical path or external resource. Pure pointer.
- **pipeline** — when a system / cron / MCP / hook is added or reconfigured. Documents the protocol, not the content.

### How to save

1. Write a file in the right subfolder (`user/`, `feedback/`, `principle/`, `location/`, `pipeline/`) with the controlled-vocab frontmatter.
2. Add a pointer line to either `MEMORY.md` (if hot — pinboard tier) or `INDEX.md` (if cold). Default cold; promote to MEMORY.md only if the entry should fire on every relevant task.

### Format flexibility

Use the `Rule / **Why:** / **How to apply:**` structure when the *why* or *application context* is non-obvious. Otherwise a clean one-liner is fine. What matters is recoverable info, not template adherence. **Frontmatter is required; structured-body is optional.**

### Cross-references

Link related memories with `[[name]]` (kebab-case slug from the file's `name:` field). Links to not-yet-written entries are fine — they mark intent. Wiki-link liberally; agents walk the graph at retrieval time.

## Agentic architecture map

The full map of how skills + hooks + crons + MCP + memory + vault routing + brand wire together lives at `Vault/AI Toolkit/agentic-architecture.md`. It has a snapshot section (rewrite in place) and an append-only **Evolution log**.

**Whenever you make or observe a structural change** to:
- a skill in `~/.claude/skills/` (added, removed, materially rewritten),
- a hook in `~/.claude/hooks/`,
- a launchd plist in `~/Library/LaunchAgents/`,
- a memory schema or routing protocol (subfolder layout, MEMORY.md/INDEX.md split, tag vocabulary),
- `~/.claude/settings.json` / `settings.local.json` permissions or hook config,
- an MCP server (added, removed, reconfigured),
- vault routing (new venture folder, new `_learnings.md`, new playbook domain in `Vault/Playbooks-Index.md`, new `_strategy.md`),

→ **append a dated entry to the Evolution log section of `Vault/AI Toolkit/agentic-architecture.md`** using the template at the bottom of the file. If the snapshot section above the log has gone stale because of the change, also update the relevant snapshot subsection in place.

This is how we track architecture drift and surface optimization opportunities over time. Don't skip it for "small" structural changes — those are the ones that compound and get lost.

## Brand routing

Derek's house brand at `~/.claude/reference/brand/` **auto-applies to every artifact** (deck, PDF, one-pager, PRD, brief, meeting summary) without being asked. Start with `README.md` there for loading order by surface.

**Exception:** UL-positioning *content* files (`boilerplate.md`, `messaging.md`, the UL Marketing section of `voice-and-tone.md`, and the UL framing in `identity.md`) carry Unlikely Labs company copy and should only be loaded when the artifact is for Unlikely Labs itself. For any other venture (Bastion, AI Build Partners, Tribal Datacenter, Estivon, etc.), use the visual system from this folder and substitute the positioning content with the venture's own copy — or, if no venture copy exists, write neutral placeholder positioning and surface that gap once at the end of the response (not as a blocking question).

For PDFs specifically: **default to Light Mode tokens (white background)** regardless of brand-README routing; dark mode only when explicitly requested.

Bastion has its own brand content profile at `~/.claude/reference/brand-bastion/` (auto-loads with the Derek visual system).

## Vault operation log

`Vault/log.md` is append-only — record major vault-modifying operations there as you make them. Crons append automatically; interactive sessions should append on substantive structural changes (new folder, new `_learnings.md`, large reorg).
