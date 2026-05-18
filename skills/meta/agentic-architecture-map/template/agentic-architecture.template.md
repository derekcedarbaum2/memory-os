---
title: "Agentic Architecture — Internal Map and Evolution Log"
type: reference
status: active
classification: internal
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "[Your Name]"
tags: [architecture, claude-code, vault, agentic, internal]
---

# Agentic Architecture — Internal Map

The full agentic system you run across `~/.claude/` and your knowledge base. This file is the **internal, comprehensive, append-only-tracked** map.

**Purpose**
1. Single source of truth for how the system is wired right now.
2. Append-only evolution log so we can see how it changed and why.
3. Surface optimization opportunities and portability notes that current state implies.

**How this file gets maintained**
- A trigger in `~/.claude/CLAUDE.md` tells Claude to append a dated entry whenever a structural change happens to: skills, hooks, MCP servers, crons, memory schema, settings, vault routing, or the Knowledge Router.
- The "Snapshot" section is rewritten in place when components change. The "Evolution log" is append-only.
- This file is `classification: internal` — do **not** mirror to public docs.

---

## Layer 1 — The always-loaded prompt context

[Files that always load into every session. Cost-sensitive. Document each.]

| File | Role |
|---|---|
| `~/.claude/CLAUDE.md` | Global instructions |
| `[path]/CLAUDE.md` | Knowledge-base folder map and conventions |
| `~/.claude/projects/<project-id>/memory/MEMORY.md` | Auto-memory index |

---

## Layer 2 — Auto-memory

**Location:** `~/.claude/projects/<project-id>/memory/`

**Pattern:** [describe — e.g., MEMORY.md as index, one .md per entry, frontmatter with name/description/type, etc.]

**Current entries (count by type, as of YYYY-MM-DD):**
- N feedback
- N project
- N reference
- N user

**Important policy:** [any deviations from the default protocol]

---

## Layer 3 — Knowledge Router + domain learnings

**Router:** `[path to router file]`

**Domain knowledge files** (per knowledge-base folder):
- `_learnings.md` — append-only running context
- `_strategy.md` (optional) — durable anchor

**Routing systems in active use:**
- [list each routing system and its scope]

---

## Layer 4 — Skills

**Location:** `~/.claude/skills/` (N directories as of YYYY-MM-DD)

**Categorized inventory:**

*Writing & artifact production:* [list]

*Research & discovery:* [list]

*Sales & outreach:* [list]

*Quality / review:* [list]

*Workflow / system:* [list]

*[Other categories as relevant]*

**Plugin skills:** [if any]

**Custom commands:** [if any]

---

## Layer 5 — Hooks

**Location:** `~/.claude/hooks/`

| Script | Trigger | What it does |
|---|---|---|
| `[script.sh]` | [SessionEnd / UserPromptSubmit / etc.] | [description, including any concurrency guards] |

Hook config lives in `~/.claude/settings.json`.

---

## Layer 6 — Crons (launchd plists / cron / systemd)

**Location:** `~/Library/LaunchAgents/` (or `crontab -l`, or `systemd/user/`)

| Plist / job | Schedule | Runs |
|---|---|---|
| `[name]` | [cron expression / human readable] | [what it invokes] |

**Cron windows for shared-file write awareness:** [if multiple crons write to overlapping files, document the windows and any lockdir patterns]

---

## Layer 7 — MCP servers

**Config:** `~/.claude/mcp.json` (and any harness-level integrations)

**MCP servers in active use:**
- **Productivity:** [list]
- **Research / web:** [list]
- **Personal data:** [list]
- **[Other categories]:** [list]

**Notable gotchas:** [any setup tricks worth documenting]

---

## Layer 8 — Settings

| File | Role |
|---|---|
| `~/.claude/settings.json` | [model, permissions, hooks, plugins] |
| `~/.claude/settings.local.json` | [local overrides] |

---

## Layer 9 — Brand / reference

**Location:** `~/.claude/reference/` (and any equivalents)

**Loading pattern:** [describe how reference docs get loaded — e.g., README router by output surface, regex hook injection, etc.]

---

## Layer 10 — Knowledge-base structure (summary)

[Top-level folders and their roles. Full map lives in your knowledge base's CLAUDE.md.]

---

## Cross-cutting flows

**1. [Flow name, e.g., Voice memo flow]:**
[Source] → [trigger] → [script] → [skill] → [destination]

**2. [Flow name, e.g., Reading distill flow]:**
[Source] → [trigger] → [script] → [skill] → [destination]

**3. [Flow name, e.g., Session archive flow]:**
[Source] → [trigger] → [script] → [destination]

**4. [Flow name, e.g., Knowledge retrieval flow]:**
[Trigger] → [steps]

---

## Portability notes (what would move to another machine vs. not)

**Portable / reusable across machines:**
- [list]

**Machine-specific:**
- [list]

**Worth abstracting:** [generic patterns worth templating into a portable framework]

---

## Open optimization questions

1. [Question / known issue / TBD verification]
2. [Question / known issue / TBD verification]

---

## Evolution log (append-only, dated entries)

<!--
Template for new entries (newest at top of this section):

### YYYY-MM-DD — [short title]

**Trigger:** [what prompted the change]

**What changed:**
- [concrete file / config / script changes]

**Why:**
[reasoning, including any evidence / external sources that justified it]

**Files touched:**
- [path]
- [path]

**Identified gaps / follow-ups (optional):**
- [item]
-->

### YYYY-MM-DD — Initial setup

**Trigger:** First documentation of the system.

**What changed:**
- Created `agentic-architecture.md` snapshot covering all 10 layers.
- Added trigger paragraph to `~/.claude/CLAUDE.md`.

**Why:**
System had grown to N skills, N hooks, N crons. Drift was already visible. Needed a single internal source of truth for the wiring, plus an append-only log so future structural changes wouldn't get lost.

**Files touched:**
- `[path]/agentic-architecture.md` (created)
- `~/.claude/CLAUDE.md` (added trigger)
