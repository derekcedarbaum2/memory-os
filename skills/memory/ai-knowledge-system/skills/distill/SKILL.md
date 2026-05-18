---
name: distill
description: Batch-process session archives and route learnings, decisions, open threads into the domain `_learnings.md` files via the Knowledge Router. Use to dedupe, reconcile, or rebuild domain knowledge across sessions.
version: 2.0.0
model: sonnet
effort: high
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion]
---

# Distill — Batch Domain Learnings Processing

> **Note for Codex users:** this file is the workflow definition in Claude Code skill format. Codex users treat it as a design reference and rewire per [setup-codex.md](../../setup-codex.md). The workflow logic is the same; the invocation surface differs.

Reads all session archives and distills them into the domain `_learnings.md` files defined by the Knowledge Router (in `MEMORY.md` for Claude Code, in `AGENTS.md` for Codex). This is the batch counterpart to `/archive-session`'s inline domain-file updates.

## When to Use This Skill

Activate when user:
- Says "distill", "process my archives", "rebuild learnings"
- Invokes `/distill`
- Wants a cross-session pass to dedupe, reconcile, and resolve open threads across domain files
- Has accumulated many sessions and wants to rebuild domain knowledge from scratch
- Invokes `/distill --rebuild` to rewrite all domain files from session archives

Do NOT activate for:
- Archiving a single session (use `/archive-session`)
- Reading or querying a single domain file (just read it)

## Core Philosophy

> `/archive-session` captures one session at a time. `/distill` sees all sessions at once.

The archive skill updates one domain file per session. It can't see patterns across many sessions, can't detect when two sessions independently validated the same learning, and can't notice that an old open thread was silently resolved in a later session. `/distill` reads everything and reconciles the domain files with full context.

---

## Target Files (Knowledge Router)

The Knowledge Router is a table in `MEMORY.md` (Claude Code) or `AGENTS.md` (Codex) that maps task patterns to domain files. This skill reads that table and operates on every domain file it lists.

**Example router** (placeholder — replace with the user's actual one during install):

| Domain | File (relative to vault) | Route when content is about |
|---|---|---|
| Product A | `Products/Product A/_learnings.md` | PRD, scenarios, board, planning, requirements |
| Product B | `Products/Product B/_learnings.md` | Any work on Product B |
| Methodology | `Methodology/_learnings.md` | QA loops, personas, ROI, requirements analysis, discovery |
| Toolkit | `Toolkit/_learnings.md` | Agent tooling, API gotchas, automation, hooks, cost |
| Research | `Research/_learnings.md` | Market context, competitive landscape, buyer personas |

**Vault root:** `<VAULT_ROOT>` (set during install).

**Session archives source:** `<VAULT_ROOT>/CC Chat History/*.md` (Claude Code) or your equivalent (Codex). Ignore subdirectories like `Indexes/`, `Concepts/`, or any legacy artifacts.

A single session can route to multiple domains. Individual learnings within one session can also route to different domains (e.g., a session that both debugs an MCP server and decides a PRD policy).

---

## Domain File Structure

Every `_learnings.md` file has the same four sections. Preserve this structure exactly — `/archive-session` and `/distill` both append to it, and drift breaks cross-session linking.

```markdown
---
title: "[Domain] Knowledge Base"
type: reference
status: active
classification: unclassified
created: YYYY-MM-DD
updated: YYYY-MM-DD
last_reviewed: YYYY-MM-DD
author: "<your name>"
tags: [...]
---

# [Domain] — Knowledge Base

[1-2 sentence description of domain scope.]

## Learnings

### [Sub-topic heading]

- [learning sentence] *(source: [[YYYY-MM-DD-topic-slug]])*

## Key Decisions

| Date | Decision | Session |
|------|----------|---------|
| YYYY-MM-DD | [decision] | [[YYYY-MM-DD-topic-slug]] |

## Open Threads

- [thread] *(from [[YYYY-MM-DD-topic-slug]])*

## Related Sessions

| Date | Type | Summary | Link |
|------|------|---------|------|
| YYYY-MM-DD | [type] | [summary] | [[YYYY-MM-DD-topic-slug]] |
```

---

## Workflow

### Step 1: Inventory

1. Glob session archives (`<VAULT_ROOT>/CC Chat History/*.md`, not subdirectories).
2. Read YAML frontmatter of each — collect: `date`, `project`, `session_type`, `summary`, `decisions`, `insights`, `open_threads`, `follow_up`, `tags`, `related_sessions`, `topic_slug` (filename).
3. Report inventory:

```
Found [N] session archives:
- [N] build, [N] research, [N] debug, [N] writing, [N] planning, [N] brainstorm
- Projects touched: [list]
- Total insights: [N], Total decisions: [N], Total open threads: [N]
```

### Step 2: Route Each Session to Domain(s)

For each session, decide which domain file(s) it contributes to. A session can contribute to multiple domains. Use this routing logic:

1. **Project + tags first.** If `project` or `tags` clearly match a domain (per the Router's "Route when content is about" column), route there.
2. **Topic/summary fallback.** If project/tags are ambiguous, read the `summary` field. Use the Router's task-pattern descriptions to decide.
3. **Per-item routing for mixed sessions.** If a session's decisions/insights/threads span domains (common with tooling-heavy product work), split them: each individual item routes independently. Track item→domain mapping, not just session→domain.
4. **When genuinely unclear:** route to the most generic catch-all domain (typically Toolkit or Methodology) by default and flag in the preview for user override.

**Also route the session's Related Sessions table entry** to every domain it contributed to — so someone reading `Products/Product A/_learnings.md` can see every session that touched that domain.

### Step 3: Read Existing Domain Files

For each domain file in the Router:
1. Read the full file.
2. Parse the four sections (Learnings, Key Decisions, Open Threads, Related Sessions).
3. Build an index of existing entries (by session link + content) for deduplication.

If a domain file doesn't exist, note it — will create in Step 6 using the header template above.

### Step 4: Reconcile — Dedupe, Resolve, Classify

For each domain file, compare the routed new items against existing entries:

1. **Dedupe learnings.** If a new insight is substantially similar to an existing one (same principle, same mechanism), skip it. If the new wording is clearer, replace the old one and merge source links.
2. **Dedupe decisions.** Match by date + decision text. Don't add the same decision twice.
3. **Dedupe session rows.** Match by session link. Don't re-add a session that's already in the Related Sessions table.
4. **Resolve open threads.** For each existing open thread, check whether a later session's decision or explicit statement resolves it. If yes: remove the thread and note the resolution in the decision log entry (`"Resolved: [thread text] → [decision]"`). Match by semantic similarity, not string equality. **This is the single most valuable part of distill** — stale open threads destroy trust in the domain files.
5. **Classify learnings into sub-topics.** Each domain file organizes learnings under `### Sub-topic` headings. Place new learnings under the best-fitting existing heading, or propose a new one if >2 new learnings share a theme with no home.

### Step 5: Preview Plan to User

Show a summary of proposed changes per domain file. Loop over every domain in the Router (do not assume a fixed count):

```
=== <Domain Name> (_learnings.md) ===
+ N new learnings (under <sub-topic>, ...)
+ N new decisions
+ N new sessions in Related Sessions
~ N open threads resolved (moved to decision log)
- N duplicate learnings skipped (already covered)
```

Then confirm:

```
Ready to write changes to the domain files?

Options:
  - Apply all changes
  - Show me item-level detail first
  - Full rebuild instead (rewrite all domain files from scratch)
```

### Step 6: Apply Changes

For each domain file in the Router:
1. If the file exists: use Edit to insert new items into each section. Preserve frontmatter except `updated:` → today's date.
2. If the file doesn't exist: Write the full file with the standard four-section template.
3. Ensure sub-topic headings are ordered consistently (match existing order; append new sub-topics at the end of the Learnings section).

**After applying:** read each modified file once to confirm the four sections are intact and well-formed. Report any malformed tables or broken wiki-links.

### Step 7: Tier-2 Maintenance Pass

Perform a maintenance pass on the user's tier-2 memory file (`MEMORY.md` for Claude Code, the `## Memory` section of `AGENTS.md` for Codex):

1. **Tier-2 promotion.** Scan newly added learnings across all domain files. A learning belongs in tier 2 if it's an operational rule that prevents tool failures, wrong API responses, or cost errors (e.g., API field IDs, endpoint changes, pricing corrections, core product constraints). Strategic/methodological learnings stay in domain files only.
   - For each tier-2 candidate not already in the memory file, propose it for addition under the right section (Tool Gotchas, Cost & Performance, Workflow Patterns, etc.).
2. **Deduplication check.** Scan the memory file for entries that duplicate tier-1 (CLAUDE.md/AGENTS.md) content. Flag duplicates — tier 2 owns the detail; tier 1 should have at most a one-liner pointer.
3. **Staleness check.** Flag entries that may be outdated (version-specific rules for tools that have been updated, pricing that may have changed, project state that's moved on).
4. **Growth check.** Report line count. **For Claude Code, the hard cap on `MEMORY.md` is 200 lines** (lines after 200 get truncated by the loader). If over 150, suggest entries to archive or consolidate. For Codex, watch the `AGENTS.md` total — past ~10K tokens you're paying for the same context every call.
5. **Output.** Present a "Tier-2 maintenance" section in the final summary with: current line count, proposed additions, flagged duplicates/staleness. **Never auto-edit the memory file — always ask the user to approve each change.**

### Step 8: Summary

Report a per-domain summary. Loop over every domain in the Router; do not hardcode a count:

```
Distill complete:
- Sessions processed: N
- Domain files updated: N of M
  For each domain in the Router:
    - <Domain Name>: +L learnings, +D decisions, +S sessions, R threads resolved
- Cross-domain sessions: N (routed to 2+ domains)
- Tier-2 maintenance: N tier-2 promotions proposed, N duplicates flagged
```

---

## Modes

### Default: Incremental

Process only sessions that are newer than the most recent `updated:` date across the domain files. Everything else is assumed already reconciled. Fast and cheap.

### `--rebuild`: Full Rebuild

Rewrite all domain files from scratch, using the full set of session archives. Useful when the files have drifted, sub-topic organization has gone sideways, or routing rules have changed.

**Before overwriting, confirm:**

```
Full rebuild will overwrite all domain `_learnings.md` files with freshly reconciled content from session archives. Session archives are NOT touched.

Options:
  - Yes, rebuild
  - Cancel (run incremental instead)
```

In rebuild mode, skip Step 3's "read existing" — you're regenerating. Still run Step 7's tier-2 maintenance pass.

---

## Edge Cases

- **No session archives exist:** Tell the user. Nothing to distill.
- **Session with no insights or decisions:** Still add it to the Related Sessions table of whichever domain(s) its project/tags indicate. Skip it for Learnings and Key Decisions.
- **Session with ambiguous domain:** If tags/project/summary don't clearly route to a domain, default to the most generic domain (Toolkit or Methodology) and flag in the Step 5 preview so the user can override.
- **Open thread with no matching resolution:** Leave it. Don't force-resolve threads just because time has passed.
- **Session that contributes to 3+ domains:** Fine. Route per-item and add the session row to each relevant domain's Related Sessions table.
- **Domain file doesn't exist yet:** Create it with the standard four-section template in Step 6.

---

## Relationship to /archive-session

| | /archive-session | /distill |
|---|---|---|
| **When** | During/after one session | Periodically, across all sessions |
| **Scope** | One session's output | Every session ever archived |
| **Strength** | Captures in the moment | Sees cross-session patterns, resolves stale open threads |
| **Routing** | Single-session routing | Multi-session routing + dedupe + cross-domain reconciliation |
| **Domain files** | Appends new items | Dedupes, reorganizes, resolves threads |
| **Tier 2** | Routes tier-2 candidates inline | Full maintenance pass (promotion, dedupe, staleness, growth) |

Use both. `/archive-session` keeps the domain files current. `/distill` keeps them clean.
