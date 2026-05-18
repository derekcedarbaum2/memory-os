---
name: archive-session
description: Archive the current session to your vault with AI-extracted metadata — decisions, insights, open threads, and a condensed transcript. Use when the user says "archive this", "save this session", "log this chat", or invokes /archive-session.
version: 3.0.0
model: sonnet
effort: high
disable-model-invocation: true
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent]
---

# Archive Session — Conversation Knowledge Extraction

> **Note for Codex users:** this file is the workflow definition in Claude Code skill format. Codex users treat it as a design reference and rewire per [setup-codex.md](../../setup-codex.md) (Option A/B/C). The workflow logic is the same; the invocation surface differs.

Extracts decisions, insights, open threads, and context from a session and writes a structured, queryable markdown file to the user's vault. Maintains running domain `_learnings.md` files so the agent can efficiently load past context in future sessions.

## When to Use This Skill

Activate when user:
- Says "archive this", "save this session", "log this chat"
- Invokes `/archive-session`
- Invokes `/archive-session [path-to-existing-raw-archive.md]` (retroactive enrichment mode)

Do NOT activate for:
- Exporting raw transcripts (a SessionEnd hook should handle that, if configured)
- Summarizing someone else's conversation or document

## Core Philosophy

> Every archived session should answer: **What happened? What was decided? What did I learn? What's still open?**

Most sessions don't have all four. That's fine — leave fields empty rather than force-fill garbage.

---

## Vault Configuration

- **Output directory:** `<VAULT_ROOT>/CC Chat History/` (replace `<VAULT_ROOT>` during install — see setup guides)
- **Filename format:** `YYYY-MM-DD-[topic-slug].md` where the topic slug is a 3–5 word kebab-case summary of the session topic (e.g., `2026-02-18-vendor-eval-decision.md`). Derive from the session title. Keep it short and scannable.
- If a file already exists at that path (e.g., from a SessionEnd hook), overwrite it — the skill output is strictly superior.

---

## Workflow

### Step 0: Cost Check

Before doing any work, estimate whether the full archive is worth running at the current context size. Find the transcript `.jsonl`, check file size. If the conversation is over ~50K tokens, ask the user before proceeding — extraction at high context is expensive and a shorter session may not need the full pipeline.

### Step 1: Locate the Transcript

**Normal mode (during or at end of active session):**
1. Find the current session's transcript. The session ID is available from the conversation context.
2. Look for the `.jsonl` file at: `~/.claude/projects/-<your-username>/[session-id].jsonl` (Claude Code) or your tool's equivalent transcript path.
3. If the exact path isn't clear, glob for recent `.jsonl` files and pick the one matching the current session or the most recently modified.

**Retroactive enrichment mode (`/archive-session [path]`):**
1. Read the provided file path (a raw archive markdown file from a hook).
2. Extract the `session_id` from its frontmatter.
3. Locate the original `.jsonl` transcript using that session ID.
4. If the `.jsonl` no longer exists, work from the raw archive content instead.

### Step 2: Parse the Transcript

Read the `.jsonl` file. Each line is a JSON object. For Claude Code's schema, key fields:

- `type`: `"user"` or `"assistant"` — these are conversation turns
- `message.role`: `"user"` or `"assistant"`
- `message.content`: String or array of content blocks
  - Text blocks: `{"type": "text", "text": "..."}`
  - Tool use blocks: `{"type": "tool_use", "name": "ToolName", "input": {...}}`
  - Tool result blocks: `{"type": "tool_result", "content": "..."}`
- `timestamp`: ISO timestamp
- `sessionId`: Session identifier
- `cwd`: Working directory

(Codex users: rewrite this step to match your transcript schema. Downstream steps are schema-agnostic.)

**Extraction rules:**
- Collect all user text messages verbatim
- Collect all assistant text responses
- For tool uses: log as one-line summary — `"[ToolName] — [brief description]"` (e.g., "Read — ~/.claude/settings.json", "Bash — ran npm test, 3 passed")
- For tool results: DO NOT include raw output. Only note success/failure and key result in the tool use summary above.
- Skip `file-history-snapshot` entries entirely
- Skip system messages

### Step 3: Extract Metadata

Analyze the full conversation to extract metadata fields. Extraction heuristics:

| Field | Heuristic |
|---|---|
| `decisions` | Statements where the user committed to a path ("we'll use X", "going with Y", "decided to skip Z"). Include rationale if stated. |
| `insights` | Non-obvious learnings — tool quirks, API gotchas, mental-model corrections. Things future-you will be glad past-you wrote down. |
| `open_threads` | Unresolved questions, blocked decisions, "we'll come back to this" statements. |
| `follow_up` | Concrete CTAs the user committed to outside this session (send email, create ticket, run command). |
| `artifacts_created` / `artifacts_modified` | Files the assistant wrote or edited. Pull from tool use entries. |
| `stack` | Tools, APIs, libraries, services discussed. Auto-detect from tool names and content. |
| `tags` | 3–6 keyword tags, lowercased, hyphenated. |

**If a field has no matches, set it to an empty list `[]`. Never fabricate.**

### Step 4: Build the Condensed Transcript

From the parsed conversation:
1. Include all user text messages verbatim
2. Include all assistant text responses
3. Replace tool use/result sequences with one-line summaries
4. For sessions under 50 raw content lines: include everything
5. For longer sessions: use judgment to compress — collapse repetitive exchanges, summarize long tool-heavy sequences, but preserve the narrative arc. Target ~300 lines max.

Format as:

```
**User:** [message]

**Assistant:** [response]

> [Tool] — [one-line summary]

**User:** [next message]
...
```

### Step 5: Assemble

Build the full archive document with this structure:

```markdown
---
title: "<short title from session topic>"
type: session
status: archived
classification: internal
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "<user name>"
tags: [<tags>]
date: YYYY-MM-DD
session_id: <id>
session_type: <build|research|debug|writing|planning|brainstorm>
project: <primary project>
summary: "<one-sentence summary>"
confidence: <high|medium|low>
decisions: [...]
artifacts_created: [...]
artifacts_modified: [...]
open_threads: [...]
insights: [...]
follow_up: [...]
stack: [...]
turns: <N>
---

# Session: YYYY-MM-DD — <title>

## Summary
<2–4 sentences>

## Decisions
- <decision> — <rationale>

## Insights
- <insight>

## Open Threads
- <thread>

## CTAs
- #cta <action> @<owner if known> — due <date if known>

## Condensed Transcript
<from Step 4>
```

**Rules for the body sections:**
- If a section has no items, omit it from the body. Frontmatter still gets `[]`.
- Body sections can have slightly more context than frontmatter versions — a sentence of explanation is fine.

### Step 5b: CTA Sweep

Scan the conversation for commitments, action items, and follow-ups. Emit `#cta` tasks in the `## CTAs` section. Format: `#cta <action verb> <thing>` plus optional `@owner` and `due <date>`.

Examples:
- `#cta send proposal to vendor X — due Friday`
- `#cta @MacKenzie — review draft PRD by next Tuesday`

Do not invent CTAs. Only emit what was explicitly committed to in the session.

### Step 6: Show and Confirm

**Display the assembled archive to the user.** Do NOT auto-save.

Then ask (Claude Code uses `AskUserQuestion`; Codex agents emit a plain question):

```
Archive looks good? I'll save to <VAULT_ROOT>/CC Chat History/.

Options:
  - Save as-is
  - Let me edit first
```

### Step 7: Save and Update Knowledge Graph

**Cost optimization (Claude Code only):** Steps 7+ are mechanical file operations that don't need the full conversation context. Late in a session, the accumulated context can be 2M+ tokens, making every read/edit expensive. To avoid this, delegate the remaining work to a **cheaper model subagent** (e.g., Sonnet) using the Agent tool.

**How to delegate (Claude Code):**

1. Assemble a single prompt for the subagent containing:
   - The complete archive markdown document (from Step 5)
   - The target file path: `<VAULT_ROOT>/CC Chat History/YYYY-MM-DD-[topic-slug].md`
   - The project name
   - Lists of: decisions, insights, open_threads, follow_up
   - The session date

2. Launch the subagent with `model: "sonnet"` and instruct it to perform Steps 7a–11 below.

**Codex users:** skip subagent delegation; perform Steps 7a–11 inline. Higher per-call cost, simpler flow.

**Steps 7a–11 (whether direct or via subagent):**

7a. **Save the archive** to `<VAULT_ROOT>/CC Chat History/<filename>.md`.

8. **Update the project index** at `<VAULT_ROOT>/<project>/_index.md` (if maintained) — add a row pointing to the new archive.

9. **Update the relevant `_learnings.md`** — see Step 12b below for the distillation flow.

10. **(Optional)** Extract concept nodes if your vault uses a knowledge-graph layer.

11. **(Optional)** Update MOCs (Maps of Content) if your vault uses them.

### Step 12: Offer Tier-1 Integration

If this session produced decisions or insights that would be valuable as **persistent context for all future sessions**, offer to add them to the user's tier-1 file:
- Claude Code: `~/.claude/CLAUDE.md`
- Codex: `~/.codex/AGENTS-global.md` or per-project `AGENTS.md`

```
This session produced context that could help future sessions. Add key items to your global rules file?

Options:
  - Yes, show me what you'd add
  - No, just the archive
```

**If yes:**
1. Read the current tier-1 file.
2. Draft additions — only high-value, durable context. Not session-specific details. Think: "Would the agent need to know this in 3 months?"
3. Show the draft to the user. Do NOT write without approval.
4. If approved, append to the appropriate section.

**What belongs in tier 1:**
- Architectural decisions that affect how the agent should work ("Always use flat YAML, never nested objects")
- Project conventions ("we use freemium pricing — never quote enterprise tiers without explicit go-ahead")
- Learned preferences ("user prefers terse responses, no trailing summaries")

**What does NOT belong:**
- Session-specific details
- Temporary states ("currently debugging X")
- Anything already in the project index or `_learnings.md`

### Step 12b: Distill to `_learnings.md`

After the archive is saved and tier-1 integration is handled, close the synthesis loop by proposing additions to the domain `_learnings.md`. This is the step that keeps the tier-3 knowledge layer current without relying on the user's memory.

**Route to the right `_learnings.md`** using the Knowledge Router in `MEMORY.md`. If the session spans domains, offer the user a choice.

**Workflow:**

1. **Read the target `_learnings.md`** (the one matched by the Router, or user-selected).
2. **From the archive's decisions + insights + open_threads,** draft candidate additions grouped by section:
   - New **Learning** bullets (with source wikilink to the session archive).
   - New **Key Decision** rows (date | decision | session link).
   - New **Open Thread** bullets.
3. **De-duplicate** against the existing `_learnings.md` — if a candidate is already captured (exact or near-paraphrase), skip it.
4. **Present the draft to the user:**

```
Add these {N} items to {_learnings.md basename}?

Options (multi-select):
  - All learnings ({N})
  - All decisions ({M})
  - All open threads ({K})
  - Review per-item first
```

5. **If "Review per-item first":** loop through candidates one at a time, offering Keep / Edit / Skip per item. Batch by section if there are many.

6. **Before writing:** set `updated` in frontmatter to today and `last_reviewed` to today.

7. **Apply approved additions** with Edit. Do NOT overwrite existing content — append only, to the correct section.

8. **Never auto-write.** This is the highest-risk synthesis step — always confirm per category before touching the file.

**Rules:**
- Source citations are mandatory: every new learning bullet ends with `*(source: [[YYYY-MM-DD-{topic-slug}]])*`.
- No bullet should be over two sentences. If the insight is longer, it's a Concepts/ note (or just a separate doc), not a learning.
- If the session produced zero new learnings worth adding, skip this step entirely — tell the user "no new distillations worth adding" and move on.
- If the `_learnings.md` has no `last_reviewed` field, add it. Update it only if the user approved additions — a skipped distillation pass is NOT a review.

### Step 13: Summary Output

After all steps complete, output a brief summary:

```
Archive saved: [filename]
Project index: [updated/created]
_learnings.md distillation: [N learnings, M decisions, K open threads added to {file} | skipped]
Tier-1 (CLAUDE.md/AGENTS.md): [updated/skipped]
```

---

## Edge Cases

- **Very short sessions (< 5 turns):** Still archive, but expect most metadata fields to be empty. Set confidence to `medium` or `low`.
- **Multiple projects in one session:** Use the primary project (most discussed). Add secondary project as a tag.
- **No clear decisions/insights:** That's fine. A research or brainstorm session might have none. Don't force-fill.
- **Session transcript not found:** Tell the user. Offer to create a manual archive based on the conversation context visible to you.
- **Retroactive enrichment of raw archive:** Read the raw archive, extract what you can, supplement by reading the original `.jsonl` if available.

---

## Notes for Implementers

This SKILL.md is the **shipped, self-contained version** of the skill. The original author runs an extended version with companion files for progressive disclosure:

- `prompts/subagent-instructions.md` — extracted subagent prompt for Steps 7a–11
- `reference/metadata-field-definitions.md` — full extraction heuristics
- `reference/cta-sweep-rules.md` — CTA formatting rules
- `reference/cost-estimation.md` — cost-tier confirmation prompts
- `templates/archive-structure-template.md` — externalized output template

These are optimizations, not requirements. The skill works fine inline. Add them later if your sessions get long enough that progressive context loading saves real money.
