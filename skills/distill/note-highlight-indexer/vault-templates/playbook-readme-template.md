---
title: <Playbook Name> — Index
type: reference
status: active
classification: internal
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "<your-name>"
tags: [playbook, <domain-tag>]
---

# <Playbook Name>

<One-paragraph description of the playbook's purpose. What domain does it cover? Who/what consumes it (which skills, which tasks)?>

Each file is structured for an AI agent to *use*, not just read: scorecards, decision triggers, anti-patterns, fillable templates. Source attribution is inline so claims are traceable.

## Files

<As topic files accumulate, list them here with one-line descriptions. Group by purpose if the playbook has natural sub-categories. Example structure:>

**Generative (use to *create* candidates):**
- [[topic-1]] — short description

**Evaluative (use to *score / kill / sharpen* candidates):**
- [[topic-2]] — short description
- [[topic-3]] — short description

## Task routing for agents

<Map common tasks to the file(s) that should be loaded. The auto-distiller does NOT fill this in — the user wires it up as the playbook matures. Example:>

| Task | Files to load (in order) |
|------|--------------------------|
| **<Task A>** | `topic-1` → `topic-2` |
| **<Task B>** | `topic-3` → `topic-1` |

**Default for ambiguous tasks:** <name the 1–2 files that are usually load-bearing>.

## How to use

**When applying to a project:** load only the task-routed subset above plus the project's `_learnings.md`. Don't load every file in the playbook unless the task warrants it.

**When capturing new content:** use `/playbook-distill` (interactive) or let the auto-distill cron handle Readwise files automatically. The distiller decides where new insights merge.

## Conventions

- Every insight is source-tagged inline: `[<source title>, <date>]`.
- New articles get distilled *into* existing topic files, not appended as new files. The synthesis cost is the feature.
- Topic files split when one exceeds ~400 lines or covers two clearly distinct dimensions. Don't pre-split.
- Examples and named entities stay — they make the patterns sticky.

## Sources captured

<Append-only audit trail of what's been distilled into this playbook. The auto-distiller appends to this list on every merge.>

- <First source title> [YYYY-MM-DD] — <which topic file(s) it merged into; what was net-new>
- <Second source title> [YYYY-MM-DD] — <merge summary>
