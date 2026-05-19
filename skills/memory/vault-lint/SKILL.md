---
name: vault-lint
description: Vault hygiene scan — flags broken wikilinks, missing/invalid frontmatter, orphans, oversized files, stale `_learnings.md`, stale bullets, contradictions, knowledge gaps, cross-layer drift, duplicate concepts. Severity-tagged report (Critical / Warning / Info). Optional --fix mode for safe categories. Read-only by default. Writes a report to `Lint Reports/` for user review. Activate when user says "lint the vault", "vault health check", "audit the vault", "scan for drift", or invokes `/vault-lint`. Also fires on weekly launchd schedule.
version: 1.0.0
model: sonnet
effort: medium
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, Agent]
---

# Vault Lint — Hygiene Scan

Scans a markdown knowledge vault for staleness, contradictions, orphans, knowledge gaps, and structural issues. Writes a single severity-tagged report the user can read and act on. Read-only by default; `--fix` mode available for safe categories with per-category opt-in.

---

## Configuration (edit before first run)

This skill assumes a single vault root and a memory layer. Replace the placeholders below with your own paths before invoking:

| Placeholder | What to set it to |
|---|---|
| `{{VAULT_ROOT}}` | Absolute path to your vault folder (the parent of your `_learnings.md` files and session-archive folder) |
| `{{MEMORY_PATH}}` | Absolute path to your auto-memory `MEMORY.md` (typically `~/.claude/projects/<project>/memory/MEMORY.md`) |
| `{{CLAUDE_MD}}` | Absolute path to your global `CLAUDE.md` (typically `~/.claude/CLAUDE.md`) |
| `{{SESSION_ARCHIVE_DIR}}` | Path inside the vault where session archives live (typically `CC Chat History/` or `AI Toolkit/CC Chat History/`) |

The skill expects these conventions in your vault:

- One or more `_learnings.md` files, one per domain (e.g., `Products/X/_learnings.md`)
- Optional session archives folder — files there are excluded from orphan and most semantic checks (one-way writes by design)
- YAML frontmatter on each `.md` file with required fields: `title`, `type`, `status`, `classification`, `created`, `updated`. Plus `last_reviewed: YYYY-MM-DD` on `_learnings.md` files for staleness tracking.
- Wikilink syntax (`[[target]]`) for inter-page references

If your vault uses different conventions, see the "Adapting to Your Vault" section at the bottom.

---

## Always-excluded paths

These directories are skipped on every run. Some are unreadable (system); others are externally regenerated and would pollute every report:

- `_archive/` — inactive / completed work
- `_attachments/` — media files
- `.git/` — git metadata
- `.obsidian/` — Obsidian app state
- **`Reading/Books/`, `Reading/Articles/`, `Reading/Tweets/`** — Readwise-generated. Any frontmatter or links you "fix" here will be overwritten on next sync. **If you use the Note Highlight Indexer or any Readwise-to-Obsidian integration, leaving these in scope would flag 200+ files every run.**
- `{{SESSION_ARCHIVE_DIR}}` — included from inventory but excluded from orphan checks and most semantic checks (session archives are intentionally terminal leaf nodes)

Apply these exclusions at the glob/find step. Never produce findings for files under these paths.

---

## Invocation

- `/vault-lint` — full audit
- `/vault-lint --folder=<vault-relative-path>` — scope to one folder (cheap targeted run, e.g., `--folder=Products/Alpha/`)
- `/vault-lint --fix` — pre-approve auto-fixes for safe categories (frontmatter backfill only); never auto-deletes; per-category yes/no confirmation

---

## When to Use This Skill

Activate when user:
- Says "lint vault", "lint the vault", "check the vault", "vault hygiene", "vault health check", "audit the vault", "scan for drift"
- Invokes `/vault-lint` (with or without options)
- Is triggered by a scheduled launchd job (the plist passes `/vault-lint` to `claude -p`)

Do NOT activate for:
- Day-to-day vault edits — those are the user's responsibility
- Memory pruning (use a separate `/prune-memory` skill if you have one)
- Session archiving (use a separate `/archive-session` skill if you have one)
- Single-file content quality review (use `/qa-loop` instead)

---

## Severity tagging

Every finding gets one of three severities:

- **Critical** — blocks daily work or surfaces a wrong fact in always-loaded context (e.g., wrong production date in a project's `CLAUDE.md`, contradiction between MEMORY.md and an authoritative source)
- **Warning** — quality issue (broken link, oversized file, stale bullet, contradiction not yet biting)
- **Info** — FYI, often intentional (orphans, dormant `_learnings.md`, duplicate concepts that may be expected)

The report leads with Critical findings. The summary table tracks counts per severity.

---

## Paths

- **Vault root:** `{{VAULT_ROOT}}`
- **MEMORY.md:** `{{MEMORY_PATH}}`
- **Global CLAUDE.md:** `{{CLAUDE_MD}}`
- **Session archive dir:** `{{SESSION_ARCHIVE_DIR}}`
- **Output:** `{{VAULT_ROOT}}/Lint Reports/lint-YYYY-MM-DD.md`
- **Log:** `{{VAULT_ROOT}}/log.md` (append entry after writing report)
- **Style reference:** `~/.claude/skills/vault-lint/examples/` — read 1–2 files here before writing the report (see Step 4)

---

## Cost Discipline

This runs weekly unattended. Keep it bounded:

- Model is **sonnet**, not opus. Do not upgrade without user approval.
- Do NOT read every file in the vault. Read only: `MEMORY.md`, `CLAUDE.md`, all `_learnings.md` files, and recent session archives (last 14 days).
- Use Grep/Glob/Bash for structural checks (broken wikilinks, file sizes, frontmatter parsing) — cheap.
- Reserve AI-level reasoning for the things it's uniquely good at: contradictions, staleness, gap detection, cross-layer drift.
- Run cross-file analytic checks (contradictions, drift, duplicate concepts) via subagent (Agent tool, `subagent_type: "Explore"`) for context isolation.
- Target total skill runtime cost: **under $5 per invocation** (typical: $0.20–$0.75).

If the vault has grown substantially (>100 `_learnings.md` bullets in any one file, or >500 markdown files total), flag this in the report's summary — the scope of lint may need to be re-scoped.

---

## Workflow

### Step 1: Inventory (shell-only, cheap)

```bash
# Count vault markdown files (excluding always-excluded paths)
find "{{VAULT_ROOT}}" -name "*.md" \
  -not -path "*/_archive/*" \
  -not -path "*/_attachments/*" \
  -not -path "*/.git/*" \
  -not -path "*/.obsidian/*" \
  -not -path "*/Reading/Books/*" \
  -not -path "*/Reading/Articles/*" \
  -not -path "*/Reading/Tweets/*" \
  -not -path "*/{{SESSION_ARCHIVE_DIR}}/*" \
  -not -path "*/Lint Reports/*" \
  | wc -l

# Skip ephemeral files (regenerated derived views — Today.md and similar) for
# orphan/staleness checks. Detect via `type: ephemeral` in frontmatter.

# List all _learnings.md files
find "{{VAULT_ROOT}}" -name "_learnings.md"

# List recent session archives (last 14 days)
find "{{VAULT_ROOT}}/{{SESSION_ARCHIVE_DIR}}" -maxdepth 1 -name "*.md" -mtime -14
```

Record: total file count, `_learnings.md` paths + sizes, recent session archive count.

If a `--folder=<path>` flag was passed, scope all subsequent checks to that subtree.

### Step 2: Structural Checks (shell + Grep, cheap)

**2a. Broken wikilinks**

```bash
grep -rhoE '\[\[[^\]]+\]\]' "{{VAULT_ROOT}}" --include="*.md" \
  | sed -E 's/\[\[([^|\]]+)(\|[^]]+)?\]\]/\1/' \
  | sort -u > /tmp/lint-wikilink-targets.txt
```

For each target, check if a file with that basename exists in the vault. Flag targets that resolve to zero files. **Severity: Warning.**

**2b. Missing or invalid YAML frontmatter**

Every `.md` file (excluding the always-excluded paths above and session archives) must have a frontmatter block:

- Block starts with `---` on line 1, contains required fields, ends with `---`
- Required fields: `title`, `type`, `status`, `classification`, `created`, `updated`
- Field value enums:
  - `type` ∈ {`prd`, `reference`, `meeting`, `cta`, `research`, `concept`, `session`, `essay`, `idea`, `ephemeral`}
  - `status` ∈ {`draft`, `active`, `approved`, `archived`}
  - `classification` ∈ {`public`, `internal`, `confidential`, `unclassified`}
- Dates must match `YYYY-MM-DD` format

Missing block, missing required field, or value outside the enum = **Warning**.

**2c. Oversized `_learnings.md`**

Any over 30KB gets flagged as a prune candidate. **Severity: Warning** (Med).

**2d. Orphaned pages**

A page is orphaned if (a) no other vault page links to it AND (b) it has no outbound links. Only check files outside `{{SESSION_ARCHIVE_DIR}}` and the always-excluded paths — session archives are expected to be terminal.

**Skip files with `type: ephemeral`** in frontmatter (e.g., `Today.md`, regenerated dashboards). They are regenerated derived views, not first-class content; orphan-ness is a non-issue by design. Note "ephemeral files excluded" in Skipped Checks.

**Severity: Info** (orphans aren't always bad — they might be inbox items or standalone deliverables).

Skip this check if the vault uses path-style wikilinks (`[[Folder/file]]`) heavily — those resolve in Obsidian but trip strict checkers. Note in the report's "Skipped Checks" section if so.

**2d-bis. Premature entity scaffold (entity-evidence threshold)**

For any folder under `People/`, `Organizations/`, or any user-declared typed-entity directory, flag folders that contain only a single stub file (frontmatter + ≤3 body lines) and have no inbound wikilinks from other vault content. These are entity files created ahead of evidence.

The entity-evidence rule (see [vault-conventions](https://github.com/derekcedarbaum2/vault-conventions)): don't create an entity file until ≥2 distinct independent signals justify it. The lint check infers signal absence from the file's own thinness + lack of inbound references.

**Severity: Info** (premature scaffold is messy, not broken).

Skip if the vault doesn't use typed-entity folders — note in Skipped Checks.

**2e. MEMORY.md size**

Warn if MEMORY.md is over 200 lines (truncation risk). **Severity: Warning.**

**2f. Unsourced claims in `_learnings.md` / `_strategy.md`**

For every `_learnings.md` and `_strategy.md`, parse bullets under any claim-shaped section: `## Learnings`, `## Anti-patterns`, `## Principles`, `## Decisions`. A bullet is **sourced** if it ends with `[[wiki-link]]` OR an inline date `(YYYY-MM-DD)`. Bullets under `## Open Threads`, `## Current state`, `## Backlog`, `## Status snapshot`, or `## Related Sessions` are **exempt** (state, not claims).

Report grouped by file — count + top 3 example bullets per file. **Severity: Warning.** Backfilling the whole vault is not the goal — the rule applies on edits going forward and surfaces drift in active files.

**2g. Trajectory regression — active ventures untouched ≥30 days**

For each active venture pointer in `MEMORY.md`, locate its `_learnings.md` and read filesystem mtime. Compute days since last edit.

- ≥30 days → **Warning** ("stale active venture — touch or move to backlog")
- ≥60 days → **Critical** ("dormant — consider demoting from active or archiving")

Active ventures that no longer get edits are silent decay. The 30-day threshold is the early flag; the 60-day threshold is the hard demotion prompt. Report: venture name, days since mtime, recommended action.

### Step 3: Semantic Checks (AI; use carefully)

Run via subagent (Agent tool, `subagent_type: "Explore"`) for context isolation. Reserve main-context reasoning for the report write-up.

**3a. Contradictions across `_learnings.md` files**

Read every `_learnings.md` file. Look for bullets that contradict each other — different field IDs for the same field, conflicting dates or priorities, "X is P0" vs "X is P2".

For each contradiction, record: the two conflicting bullets, the files, and the likely authoritative source. **Severity: Warning** (or **Critical** if the contradiction is in always-loaded context).

**3b. Stale bullets**

Flag bullets that reference:
- **Ticket IDs** (Jira, Linear, Plane, etc.) — quick-sample 10 random IDs; if any are gone, flag the learning. (Skip if MCP unavailable; note in Skipped Checks.)
- **File paths** — if the path no longer exists, flag the bullet.
- **Function/API names** — if mentioned as "current" but reference material says otherwise.
- **Version numbers** — if a bullet references "PRD V1.3" but MEMORY.md says current is V1.4.
- **Dates** — "upcoming" or "next week" with a date over 60 days in the past.

Do not try to be exhaustive. Spot-check aggressively. **Severity: Warning** (or Critical for expired-today deadlines).

**3c. Knowledge gaps (topics in recent sessions but not distilled)**

Read filenames (not contents) of session archives from the last 14 days. For topics that appear 3+ times but have not been added to any `_learnings.md` file, flag as a gap. **Severity: Warning.**

**3d. Cross-layer drift (same fact in MEMORY.md + CLAUDE.md + `_learnings.md`)**

The same fact appearing in 2+ auto-loaded files is duplication. Pick one source of truth per layer:

- **Operational rule / gotcha** → MEMORY.md only
- **Product fact** → product-scoped `.claude/CLAUDE.md` only
- **Detailed synthesis** → `_learnings.md` only
- **User preference / style** → global `CLAUDE.md` only

Check by:
1. Read MEMORY.md, global CLAUDE.md, all product `.claude/CLAUDE.md` files, all `_learnings.md`.
2. Normalize each non-heading line (lowercase, strip markdown, compress whitespace).
3. For any two normalized lines with token-overlap ratio > 0.7 across different files, flag as drift.
4. Report each duplication with: the shared fact, the files, and a proposed source-of-truth.

Do not flag headings, frontmatter, or routing-table entries. **Severity: Warning** (or **Critical** if the duplicated fact is wrong in one of the copies).

**3e. Stale `_learnings.md` via `last_reviewed` frontmatter**

Flag any `_learnings.md` where:
- `last_reviewed` is missing
- `last_reviewed` is more than 60 days in the past
- `updated` is more than 30 days newer than `last_reviewed` (accumulated changes without review)

**Severity: Info** (stale isn't always wrong — some domains are dormant).

**3f. Duplicate concepts**

Two or more files describe the same concept (same title, or >70% content overlap on body). Suggests consolidation target. Run via subagent for context isolation. **Severity: Info.**

### Step 4: Produce Report

**Before writing**, read 1–2 files in `~/.claude/skills/vault-lint/examples/` to pattern-match tone and structure. The examples are real prior reports — match the heading style, severity calls, and "Next Steps for User" prioritization pattern.

Write to `{{VAULT_ROOT}}/Lint Reports/lint-YYYY-MM-DD.md` with this structure:

```markdown
---
title: "Vault Lint Report — YYYY-MM-DD"
type: reference
status: draft
classification: unclassified
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "Claude Code (vault-lint skill)"
tags: [lint, vault-hygiene, automated]
---

# Vault Lint Report — YYYY-MM-DD

**Generated by:** `/vault-lint` ({manual | scheduled} | {full audit | --folder=<path> | --fix})
**Vault scope:** {N} markdown files (excl. always-excluded), {M} `_learnings.md` files, {K} session archives in last 14 days
**Runtime cost:** ${estimated-cost}

## Summary

{2-3 sentence executive summary. Lead with the most important finding (Critical first).}

| Check | Count | Severity |
|---|---|---|
| Broken wikilinks | {N} | Warning |
| Missing/invalid frontmatter | {N} | Warning |
| Orphaned pages | {N} | Info |
| Oversized `_learnings.md` | {N} | Warning |
| MEMORY.md size | {ok / warn} | Warning |
| Unsourced claims | {N} | Warning |
| Trajectory regression (stale active ventures) | {N} | {Warning / Critical} |
| Contradictions | {N} | {Critical/Warning} |
| Stale bullets | {N} | Warning |
| Knowledge gaps | {N} | Warning |
| Cross-layer drift | {N} | {Critical/Warning} |
| `last_reviewed` overdue | {N} | Info |
| Duplicate concepts | {N} | Info |

## Critical ({N})
{Lead with the findings the user should act on today. If none, "No Critical findings."}

## 1. Broken Wikilinks
{list with file paths and broken targets, or "None found"}

## 2. Missing or Invalid Frontmatter
{Grouped — missing block; missing field; invalid enum value. Per file: path, issue, suggested fix.}

## 3. Orphaned Pages
{list with paths, or "None found / skipped (vault uses path-style wikilinks)"}

## 4. Oversized Files
{list files over 30KB with current size and prune recommendation}

## 5. Contradictions
For each:
- **Claim A:** {bullet} — *source: {file}*
- **Claim B:** {bullet} — *source: {file}*
- **Likely authority:** {which to trust and why}
- **Recommended fix:** {specific action}

## 6. Stale Bullets
For each:
- **File:** {path}:{line}
- **Bullet:** {text}
- **Stale because:** {reason}
- **Recommended fix:** {update / remove / verify}

## 7. Knowledge Gaps
For each:
- **Topic:** {topic}
- **Appears in:** {N} recent sessions
- **Not captured in:** any `_learnings.md`
- **Recommended action:** {distill into which file}

## 8. Cross-Layer Drift
For each cluster:
- **Shared fact:** {text}
- **Files:** {paths and line numbers}
- **Proposed source of truth:** {which layer wins}
- **Recommended fix:** {remove from which file(s)}

## 9. Duplicate Concepts
{Groups of duplicates with consolidation suggestion}

## 10. Unsourced Claims
For each file with violations:
- **File:** {path}
- **Unsourced bullets:** {N}
- **Examples:**
  - `{bullet text without trailing citation}`
  - …
- **Recommended fix:** add `[[session-id]]`, `[[voice-memo]]`, `[[document]]`, or `(YYYY-MM-DD)` to each.

## 11. Trajectory Regression — Stale Active Ventures
For each:
- **Venture:** {name}
- **`_learnings.md`:** {path}
- **Last touched:** {N days ago}
- **Severity:** {Warning ≥30 days / Critical ≥60 days}
- **Recommended action:** {touch / demote from active list / archive}

## 12. Skipped Checks
{Checks that could not run — e.g., "Jira MCP unavailable; ticket-staleness skipped." "Orphan check skipped — vault uses path-style wikilinks."}

## 11. Next Steps for User
{Prioritized list. Critical first; then high-traffic stale bullets and contradictions; then gaps; then housekeeping (orphans, dormant files).}
```

### Step 5: --fix mode (only if `--fix` flag passed)

Auto-fix is opt-in per category and limited to safe operations. Never auto-deletes. Never auto-edits content beyond frontmatter.

For each safe category, ask the user yes/no before applying:

- **Frontmatter backfill** (safe, opt-in) — adds minimum required fields with reasonable defaults: `created: <file mtime or today>`, `updated: <today>`, `type: reference`, `status: active`, `classification: internal`. The user reviews the diff per file or per batch.
- **Broken-link fixes** (suggestive only — never auto-applied) — propose the most likely correct target; print the diff; user copy-pastes to apply.
- **Contradictions** — never auto-reconciled. Flag for human review.
- **Cross-layer drift** — never auto-removed. The "remove from which file" decision is the user's.
- **Oversized files** — never auto-pruned. Recommend split target only.

If `--fix` was not passed, skip this step entirely.

### Step 6: Append to `log.md`

```
YYYY-MM-DD HH:MM | vault-lint | {full | folder | fix} | Lint Reports/lint-YYYY-MM-DD.md | {N critical, M warnings, K info}{; auto-fixed: <categories>}
```

### Step 7: No further action — terminate

The user reads the report and decides. Do NOT delete, rename, or rewrite any vault content beyond what `--fix` explicitly enabled and the user confirmed per category.

---

## Failure Modes

- **MCP / external tool unavailable** (Jira, Linear, etc.): Skip dependent checks. Note in the report's Skipped Checks section.
- **Vault path inaccessible (cloud sync issue):** Halt, write a minimal report noting the failure to `Lint Reports/lint-FAILED-YYYY-MM-DD.md`, log to `log.md`.
- **Report file already exists for today:** Overwrite (lint may be re-run same day).
- **No issues found:** Still produce a report. Summary should say "clean run, no issues found".
- **Vault uses path-style wikilinks heavily:** Skip the orphan check; note it in Skipped Checks.

---

## Output Expectations

A good lint report:
- Leads with the finding the user will act on first (Critical, then top-priority Warnings).
- Gives specific paths and line numbers, not generic advice.
- Separates structural findings (broken links, sizes, frontmatter) from semantic findings (contradictions, drift, gaps).
- Respects intentional patterns the user has noted in MEMORY.md or CLAUDE.md.

A bad lint report:
- Lists every minor thing with equal weight.
- Recommends exhaustive wikilinking or aggressive refactoring.
- Flags intentional patterns as problems (e.g., session archives have no inbound links — that's by design).
- Re-flags Readwise files (those should be in always-excluded; if you see them, your exclusion list is wrong).

---

## Manual vs Scheduled Invocation

When the user types `/vault-lint`:
1. Run the full workflow.
2. At the end: "Report written to {path}. Open it?"

When triggered by launchd:
1. Run the full workflow.
2. Do NOT offer to open the report — the user isn't at the terminal.
3. The report sits in `Lint Reports/` for the next session start.

---

## Adapting to Your Vault

If your vault doesn't follow the conventions above, here's what to change:

| Convention | If you don't use it |
|---|---|
| `_learnings.md` per domain | Replace `_learnings.md` references with whatever filename you use for your distilled knowledge layer |
| Session archive folder | Update `{{SESSION_ARCHIVE_DIR}}` to your folder; if you don't have one, skip Step 3c (gap detection) |
| Wikilink `[[target]]` syntax | If you use markdown links instead, swap the regex in Step 2a for `\[([^\]]+)\]\(([^)]+\.md)\)` |
| YAML frontmatter | If you don't use frontmatter, skip Steps 2b and 3e |
| `last_reviewed` frontmatter | If you don't track review dates, skip Step 3e |
| MEMORY.md / global CLAUDE.md auto-load | If you only have one knowledge layer, skip the cross-layer drift check (Step 3d) |
| Readwise / external sync into Reading/ | If you don't sync external content, you can remove the `Reading/Books/`, `Reading/Articles/`, `Reading/Tweets/` exclusions |

The structural checks (Steps 1, 2) work on any markdown vault. The semantic checks (Step 3) assume the multi-layer pattern described above.
