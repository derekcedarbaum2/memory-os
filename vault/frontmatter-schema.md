# Frontmatter schema

Every `.md` file in the vault opens with a YAML frontmatter block. The block is the agent's primary signal for what the file IS, how to retrieve it, and how fresh it is.

## The block

```yaml
---
title: [document title]
type: [prd | reference | meeting | cta | research | concept | session | essay | idea | ephemeral]
status: [draft | active | approved | archived]
classification: [public | internal | confidential | unclassified]
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "Derek Cedarbaum"
tags: [<controlled vocab — see tag-vocabulary.md>]
---
```

## Required fields

- **`title`** — The human-readable title. Often matches the H1; doesn't have to.
- **`type`** — The kind of document. Controlled set, see below.
- **`status`** — Document lifecycle. Controlled set, see below.
- **`classification`** — Sensitivity. `public` / `internal` / `confidential` / `unclassified`. Treat `confidential` as load-bearing — agents must not surface confidential content outside its envelope.
- **`created`** — Creation date in `YYYY-MM-DD`. Backfill from `git log` or file `ctime` if unknown.
- **`updated`** — Last meaningful update. Bumped on substantive edits, not whitespace.
- **`author`** — The human author. `"Derek Cedarbaum"` for the canonical case.
- **`tags`** — Controlled-vocabulary tags. **`tags: []` is forbidden.** See [`tag-vocabulary.md`](tag-vocabulary.md). The vault-lint cron flags empty tag arrays as warnings.

## Optional fields

Use when applicable:

- **`product`** — When the file is tied to a specific product or feature.
- **`program`** — When the file is tied to a customer program or contract.
- **`related: [[wiki-links]]`** — Explicit related-file pointers.
- **`source`** — For derivative documents — link to the source.
- **`owner`** — When the owner is not the author.
- **`due`** — Date a task or decision is due.

## Controlled `type` values

| Value | Used for |
|---|---|
| `prd` | Product Requirements Document |
| `reference` | Long-lived reference material (most common) |
| `meeting` | Meeting notes |
| `cta` | Call-to-action / next-action list |
| `research` | Research notes — primary or secondary |
| `concept` | A distilled concept (e.g., from a knowledge graph build) |
| `session` | A Claude Code session archive |
| `essay` | Long-form writing intended for publication |
| `idea` | Early-stage venture or product idea |
| `ephemeral` | Regenerated artifacts (Today.md, dashboards) |

If a real document doesn't fit any value, add the new value to this file *first*, then use it.

## Controlled `status` values

| Value | Meaning |
|---|---|
| `draft` | Work in progress, not safe to act on |
| `active` | Live and load-bearing |
| `approved` | Cleared for stakeholder use |
| `archived` | Historical, do not act on without verification |

## Controlled `classification` values

| Value | Meaning |
|---|---|
| `public` | OK to share externally |
| `internal` | Inside-the-vault only |
| `confidential` | Client / employer sensitive — never paste into chat with third parties |
| `unclassified` | Default catch-all when sensitivity is unknown |

Agents must respect `confidential` — that means no copy-paste into shared docs, public READMEs, or external chats without explicit human approval.

## Why this is enforced

Frontmatter is the only retrieval signal in a Markdown vault. Without it, `grep` returns nothing structured; agents must read every file in full to know what it is; the tag-based filtering doesn't work; the cron jobs cannot prioritize.

The cost of consistent frontmatter is roughly 10 seconds per file at write time. The benefit is every retrieval, every filter, every audit forever. The tradeoff is obvious.

## Auto-fixing missing frontmatter

The vault-lint skill ([`skills/memory/vault-lint/`](../skills/memory/vault-lint/)) detects missing or invalid frontmatter and offers to backfill with reasonable defaults:

```yaml
created: (file mtime or today)
updated: today
type: reference
status: active
classification: internal
author: "Derek Cedarbaum"
tags: [kind:reference, decay:medium]  # plus venture/domain if inferable from path
```

This is safe: it adds fields without removing content. Run it on a folder with `vault-lint --fix <folder>`.

## Backfill protocol

When editing an old file that lacks frontmatter:

1. Add the block at the top of the file.
2. Set `created:` from `git log --follow` or file mtime, whichever is older.
3. Set `updated:` to today.
4. Set `type:` from content inspection.
5. Set `classification:` to `internal` if you can't tell.
6. Set `tags:` from the controlled vocab — at minimum a `kind:` and a `decay:`.
7. Save.

The tag-backfill script ([`automation/tag-backfill.py`](../automation/tag-backfill.py)) handles the mechanical part across a whole vault in one pass.
