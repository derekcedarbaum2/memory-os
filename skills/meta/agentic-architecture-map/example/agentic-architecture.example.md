---
title: "Agentic Architecture — Internal Map and Evolution Log"
type: reference
status: active
classification: internal
created: 2026-02-15
updated: 2026-05-06
author: "[Sanitized example — based on a real PM's setup]"
tags: [architecture, claude-code, vault, agentic, internal]
---

# Agentic Architecture — Internal Map (sanitized example)

> **This is a sanitized example.** It illustrates the snapshot + evolution log format with real-shaped content (counts, layer detail, evolution entries with actual reasoning). Names, paths, clients, and employers have been genericized. Use this as a reference when filling out your own.

---

## Layer 1 — The always-loaded prompt context

Three files always load into every Claude Code session:

| File | Role |
|---|---|
| `~/.claude/CLAUDE.md` | Global instructions — voice, autonomy, knowledge routing protocol, memory overrides, cron windows |
| `Vault/CLAUDE.md` | Vault folder map + "everything lives in its venture folder" rule + YAML frontmatter schema |
| `~/.claude/projects/<project-id>/memory/MEMORY.md` | Auto-memory index — pointers to individual memory files (≤200 lines after which truncation kicks in) |

---

## Layer 2 — Auto-memory

**Location:** `~/.claude/projects/<project-id>/memory/`

**Pattern:** MEMORY.md as index, one .md per memory entry. Each entry has frontmatter (`name`, `description`, `type` ∈ `user | feedback | project | reference`). Pointer line in MEMORY.md follows `- [Title](file.md) — one-line hook` format.

**Current entries (count by type, as of 2026-05-03):**
- 5 feedback (writing voice, permissions, IP boundary, PDF default, etc.)
- 8 project (active ventures and engagements)
- 12 reference (Knowledge Router, Playbooks Index, Voice memo pipeline, Auto-distill pipeline, MCP gotchas, etc.)
- 1 user (personal context)

**Important policy:** the structured `Rule / **Why:** / **How to apply:**` format is **recommended, not required**. One-liners are valid when the rule speaks for itself. This was loosened on 2026-05-03 after the Letta benchmark / Anthropic managed-agents post showed structure constrains weaker models but isn't load-bearing for stronger ones.

---

## Layer 3 — Knowledge Router + domain learnings

**Router:** `~/.claude/projects/<project-id>/memory/reference_knowledge_router.md`
- Maps task patterns → vault `_learnings.md` files.
- **As of 2026-05-03 framing change:** Router is a starting hint, not a directive. After the routed file loads, grep across siblings + voice memos + session archives. Iterate until enough context surfaces. (Letta finding: filesystem+grep > specialized retrieval.)

**Domain knowledge files** (per vault folder):
- `_learnings.md` — append-only running context (Learnings / Key Decisions / Open Threads / Related Sessions)
- `_strategy.md` — durable anchor (target problem, approach, persona, key metrics, tracks). Currently exists for: 4 ventures.

**Routing systems in active use:**
- Knowledge Router (task → `_learnings.md`)
- `Vault/Playbooks-Index.md` (10 cross-vault domains; auto-distill cron routes here)
- `Vault/Company Building/README.md` (folder index + agent routing for company-building methods)
- `~/.claude/reference/brand/README.md` (loading order for brand tokens by output surface)

---

## Layer 4 — Skills

**Location:** `~/.claude/skills/` (60 directories as of 2026-05-03, plus `_shared/`)

**Categorized inventory:**

*Writing & artifact production:*
write-tweets, write-prd, scqa, sense-of-style, brief, one-pager, presentation, podcast-notes, meeting-summary, sme-debrief, transcript-prep, uat-debrief, slack-digest, roi, worksheet-pack, word-of-the-day

*Research & discovery:*
analyze-research, synthesize-interviews, user-discovery, hypothesis, x-research, autoresearch, distill, playbook-distill, auto-playbook-distill

*Sales & outreach:*
linkedin-outreach, linkedin-optimize, cold-outreach, sales-qa

*Quality / review:*
qa-loop, prd-review, design-standards-check, pressure-test, skill-critique, compliance-gap-check-generic, vault-lint, prune-memory, prd-sync

*Workflow / system:*
archive-session, morning-briefing, voice-memo-process, execute-prd, jpd, role-intake, learnings-resurface

*Web/data integration (Firecrawl family):*
firecrawl, firecrawl-search, firecrawl-scrape, firecrawl-map, firecrawl-crawl, firecrawl-agent, firecrawl-interact, firecrawl-download, firecrawl-build-onboarding, firecrawl-build-search, firecrawl-build-scrape, firecrawl-build-interact

**Plugin skills:** `frontend-design` (via Claude plugins, enabled in settings.json).

**Custom commands:** `~/.claude/commands/pressure-test.md` (one custom slash command).

---

## Layer 5 — Hooks

**Location:** `~/.claude/hooks/`

| Script | Trigger | What it does |
|---|---|---|
| `archive-session.sh` | SessionEnd | Reads transcript JSON from stdin, writes raw archive to `Vault/AI Toolkit/CC Chat History/{date}-{shortid}.md`. Skips short sessions (<3 user turns) and skips if `/archive-session` already wrote a rich archive. |
| `auto-distill-readwise.sh` | launchd cron 7:30 AM PT (also `--backfill` mode manual) | Iterates over Reading/Articles, Reading/Books, Reading/Tweets. For each unprocessed file, invokes headless `claude -p` with the auto-playbook-distill skill. Daily cap 5; backfill cap 25. **Has lockdir guard `/tmp/auto-distill-readwise.lock.d`** (added 2026-05-03). |
| `learnings-resurface.sh` | launchd cron Sunday 10pm PT | Cross-vault interaction-memory pattern detector. Lockdir `/tmp/learnings-resurface.lock.d`. |

Hook config lives in `~/.claude/settings.json`.

---

## Layer 6 — Crons (launchd plists)

**Location:** `~/Library/LaunchAgents/`

| Plist | Schedule | Runs |
|---|---|---|
| `com.user.monologue-sync.plist` | 7:00 AM | Pulls voice memos, writes to `Vault/Voice Memos/`, then invokes `/voice-memo-process` per memo via headless claude. **Lockdir `/tmp/monologue-sync.lock.d`**. Hard bans: Edit, Bash, Gmail, deletes. |
| `com.user.auto-distill.plist` | 7:30 AM | Calls `~/.claude/hooks/auto-distill-readwise.sh` |
| `com.user.learnings-resurface.plist` | Sundays 10 PM PT | Calls `~/.claude/hooks/learnings-resurface.sh` |
| `com.user.family-day.plist` | Thursdays 5 PM PT | Generates a personal weekend planning artifact |
| `com.user.vault-lint.plist` | TBD verify | Periodic vault health audit |

**Cron windows for shared-file write awareness:** 7:00–8:00 AM PT is the active window. Both morning crons hold mkdir-based lockdirs (stale-cleaned at 2h). Interactive sessions don't lock — coordinate writes during this window.

---

## Layer 7 — MCP servers

**Config:** `~/.claude/mcp.json` and additional MCPs configured via the Claude.ai integration layer.

**MCP servers in active use:**
- **Productivity:** Linear, Gmail, Google Calendar, Google Drive, Slack, Todoist
- **Research / web:** Firecrawl, Exa
- **Personal data:** Monarch Money, Anki, Monologue
- **Visual:** drawio

**Notable gotchas:**
- Todoist MCP must use `todoist-mcp` package with env `API_KEY`, NOT older v2 packages (deprecated → 410).
- Firecrawl + Exa are both installed at user scope and should be used proactively before writing any research deliverable.

---

## Layer 8 — Settings

| File | Role |
|---|---|
| `~/.claude/settings.json` | Model (`opus[1m]`), permissions (defaultMode `auto`, allow list of common Bash/MCP tools), SessionEnd hook config, plugin enables, theme, `effortLevel: high` |
| `~/.claude/settings.local.json` | Local overrides (large file — ~26KB, not exhaustively documented here yet) |

---

## Layer 9 — Brand system

**Location:** `~/.claude/reference/brand/` (22 files, canonical)

**Loading pattern:** start with `README.md` (loads-by-surface), pick tokens for the medium (deck / one-pager / PRD / meeting summary / proposal / email), apply.

**Important:** branded PDFs default to **Light Mode tokens (white background)** regardless of brand-README routing. Dark mode only on explicit request.

---

## Cross-cutting flows

**1. Voice memo flow:**
Voice memo (mobile) → 7:00 AM cron → `monologue-sync.sh` → `Vault/Voice Memos/{ts}-{slug}.md` → headless claude per memo → `/voice-memo-process` skill → actions taken (Todoist tasks, vault notes, scheduled agents) → `.actions.md` sibling file.

**2. Reading distill flow:**
Readwise sync → `Vault/Reading/{Articles,Books,Tweets}/*.md` → 7:30 AM cron → `auto-distill-readwise.sh` → headless claude per file → `auto-playbook-distill` skill → matching playbook → state file update.

**3. Session archive flow:**
Session end → `archive-session.sh` SessionEnd hook → raw archive in `Vault/AI Toolkit/CC Chat History/{date}-{shortid}.md` → optional `/archive-session` enrichment.

**4. Learnings resurface flow (weekly):**
Sundays 10pm → `learnings-resurface.sh` → headless claude → cluster + classify across session archives + `_learnings.md` + voice memos → route per type → state file + log update.

**5. Knowledge retrieval flow (search-first, post-2026-05-03):**
Task arrives → check Knowledge Router → load routed `_learnings.md` (+ `_strategy.md` if exists) → if thin or task spans concerns, grep across vault → iterate.

---

## Portability notes

**Portable:** skills directory, hooks (paths inside scripts may need repointing), brand reference, vault structure as a pattern, cron-script lockdir pattern.

**Machine-specific:** vault path (iCloud-specific), launchd plists (macOS-specific), MCP credentials/OAuth tokens, MCP config paths.

**Worth abstracting:** the cron-runner pattern (lockdir + headless claude + skill invocation + state file) is generic enough to template into a portable framework.

---

## Open optimization questions

1. **MEMORY.md will hit the 200-line cap soon.** Need a pruning protocol. `/prune-memory` skill exists — schedule it?
2. **`settings.local.json` is 26KB and undocumented here.** Worth a one-time audit + summary.
3. **The CC Chat History flow has two writers** — SessionEnd hook (raw) + `/archive-session` skill (rich). Race possible if both fire on the same path within a short window — low probability but worth noting.
4. **Concurrency on read-modify-write of playbook topic files** — auto-distill skill merges into existing files. Cron-script-level lock prevents self-collision but not user-vs-cron. Acceptable for now (window is small).

---

## Evolution log (append-only, dated entries)

### 2026-05-06 — First live `/learnings-resurface` run: stream-timeout failure + manual recovery + identified runner architecture gap

**Trigger:** First live execution of `learnings-resurface` (post-patch) on 2026-05-05 06:05 PT against the full 90-day window. Headless `claude -p` hit API stream idle timeout at 10:19 PT (~4h13m wall clock). The skill committed 5 Router promotions (memory files + MEMORY.md index) in the first ~10 minutes, then got stuck on the playbook-distill phase — read+merge cycles for each cluster against existing topic files. The connection went stale before completion.

**State at failure (audited 2026-05-06):**
- ✅ Wrote: 5 memory files in `~/.claude/projects/<project-id>/memory/` + 5 MEMORY.md index lines.
- ❌ Did not write: playbook distills, new playbook scaffold, state file run record, `Vault/log.md` lines, Todoist tasks.

**Manual recovery executed 2026-05-06:**
1. Updated 4 playbook topic files with the principles that should have been distilled.
2. Scaffolded one new topic file (`image-generation-craft.md`) for a domain the cron failed to write.
3. Updated playbook README + `Vault/Playbooks-Index.md` (file count, last-source-added date).
4. Wrote run record + cluster fingerprints to `~/.claude/state/learnings-resurface.json` so next Sunday's cron has idempotency reference.
5. Appended log lines to `Vault/log.md` per skill spec format.

**Identified runner architecture gap (action item):**
The runner script invokes `claude -p` with no max-turns cap, no per-phase decomposition, and no wall-clock timeout. A 4-hour single-shot is too long for the API stream's idle tolerance. **Three candidate fixes**, in escalating intrusiveness:
- (a) Add `timeout 1800 claude -p ...` (30-min wall clock) and `--max-turns 60`. Quick patch.
- (b) Decompose the skill into phases (extract → cluster → classify → route → log) with the runner invoking `claude -p` once per phase against persisted intermediate state. **Recommended.**
- (c) Switch the routing/distill phase to a deterministic script-driven mechanism, with the LLM only on per-cluster judgment. Most robust.

Until the runner is fixed, Sunday's cron remains a stream-timeout risk.

**Files touched:**
- 4 playbook topic files (updated)
- 1 playbook topic file (new)
- 1 playbook README, `Vault/Playbooks-Index.md`
- `~/.claude/state/learnings-resurface.json`
- `Vault/log.md`
- This file (log entry)

**Source:** session 2026-05-06 — recovery from 2026-05-05 live-run stream-timeout failure.

---

### 2026-05-05 — `/learnings-resurface` skill patched: artifact-type / optimization-target check before clustering and contradiction flagging

**Trigger:** 90-day dry-run produced one contested cluster that, on inspection, was a category error rather than a real contradiction. The system grouped two atoms by surface semantics ("multi-pass QA loops") but the atoms operated on different artifact types: one on skill logic / analysis / backend automation (where adversarial passes are unambiguously good), the other on marketing copy / voice-driven prose (where same-prompt polish loops over-refine).

**Changes implemented:**
1. Added mandatory artifact-type / optimization-target check during clustering. Atoms with similar surface semantics but different artifact types must split into separate clusters.
2. Added `domain` field to cluster schema capturing the artifact type / optimization target each cluster applies to.
3. Added pre-flight check to contradiction detection: confirm contradiction holds *within a single artifact type and optimization target* before marking `status: contested`.

**Why this matters:** without the check, the live run would have written a `[CONTESTED]` memory file for what is actually two clean principles (one Router-eligible, one belonging in a different playbook). Patch was applied before any live writes touched MEMORY.md or the playbooks.

**Files touched:**
- `~/.claude/skills/learnings-resurface/SKILL.md`
- This file (log entry)

---

### 2026-05-04 — New `/learnings-resurface` skill + weekly cron: cross-venture interaction-memory pattern detector

**Trigger:** Reading "Company Brain, Part 3: Interaction Memory" raised the question of whether vault `_learnings.md` files (append-only, never re-read) miss compounding cross-venture signal. Pressure-test concluded yes — but full ontology-drift design was over-engineered for one-person volume. Stripped to the two compounding pieces (Router auto-promotion, inward distill into playbooks) + classification taxonomy to handle timeless-vs-temporal patterns correctly.

**Changes implemented:**
1. New skill `~/.claude/skills/learnings-resurface/SKILL.md`.
2. New runner `~/.claude/hooks/learnings-resurface.sh` — lockdir, mirrors `auto-distill-readwise.sh` pattern; supports `--dry-run` and `--window N`.
3. New plist `~/Library/LaunchAgents/com.user.learnings-resurface.plist` — Sunday 10pm PT.
4. New state file at `~/.claude/state/learnings-resurface.json` — tracks run history + cluster fingerprints for idempotency.
5. MEMORY.md updated — added `reference_learnings_resurface.md` pointer.

**Design notes:**
- No `Vault/_patterns/` folder — would violate vault's "everything in venture folder OR cross-cutting domain folder" rule. Patterns instead route to existing infrastructure (Router for principles, playbooks for distilled wisdom, Todoist for commitments, `_learnings.md` Open Threads for questions).
- Type taxonomy distinguishes durable patterns (no decay; invalidate on contradiction) from temporal state (decays by recency). Without this, the system would erode the most valuable signals over time.

**Files touched:**
- 4 new files in `~/.claude/skills/learnings-resurface/`, `~/.claude/hooks/`, `~/Library/LaunchAgents/`, `~/.claude/projects/<project-id>/memory/`
- This file (log entry)

---

### 2026-05-03 — Initial snapshot + concurrency + Router framing change

**Trigger:** Letta benchmark + Anthropic managed-agents post review revealed three weaknesses in the current setup.

**Changes implemented:**
1. **Concurrency lockdirs** added to `auto-distill-readwise.sh` and `monologue-sync.sh`. Pattern: `mkdir`-based atomic lock at `/tmp/{name}.lock.d`, stale-cleaned after 2h, released via `trap` on EXIT. Prevents self-overlap when previous run hasn't finished.
2. **Knowledge Router reframed as starting hint, not directive.** Updated Router file and the "Loading protocol" section to add explicit grep-iteration step. Cited the Letta finding inline.
3. **Memory writing structure loosened to recommended-not-required.** New section in `~/.claude/CLAUDE.md` "Memory writing — overrides to default protocol." Frontmatter remains required.
4. **Path drift fix:** `~/.claude/CLAUDE.md` referenced wrong path for the session archive folder. Updated to actual hook write location.
5. **New section: Cron windows.** Added 7:00–8:00 AM PT awareness to `~/.claude/CLAUDE.md`.

**Files touched:**
- `~/.claude/CLAUDE.md`
- `~/.claude/projects/<project-id>/memory/MEMORY.md`
- `~/.claude/projects/<project-id>/memory/reference_knowledge_router.md`
- `~/.claude/hooks/auto-distill-readwise.sh`
- `~/scripts/monologue-sync.sh`

---

## Append-only entry template

```
### YYYY-MM-DD — [Short title of change]

**Trigger:** what motivated the change

**Changes implemented:** numbered list

**Why:** the reasoning, including any evidence or external sources that justified it

**Files touched:** absolute paths

**Source:** session reference, link, or tweet (optional)
```
