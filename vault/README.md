# vault/ — the conventions

This folder is the canonical specification of how a `memory-os` vault is structured. Every file in this folder is small, declarative, and self-contained.

If you adopt memory-os, you are adopting these conventions. Adjust them to your work, but adjust them *deliberately* — the value of the system comes from the conventions being consistent enough that `grep` and the cron jobs do useful work without thinking.

## Files in this folder

- [`conventions.md`](conventions.md) — folder structure and the "one mental model" rule (everything lives inside the venture/engagement folder it came from).
- [`frontmatter-schema.md`](frontmatter-schema.md) — the YAML frontmatter every `.md` file declares.
- [`tag-vocabulary.md`](tag-vocabulary.md) — the controlled tag vocabulary (`kind:`, `decay:`, `venture:`, `domain:`, `status:`). **`tags: []` is an enforced error.**
- [`memory-protocol.md`](memory-protocol.md) — the hot-pinboard / cold-index / per-venture-state pattern.
- [`learnings-template.md`](learnings-template.md) — the append-only `_learnings.md` template.
- [`operations.md`](operations.md) — the full operating manual (cron windows, brand routing, agentic-architecture-map enforcement). Loaded on demand by agents.
- [`examples/`](examples/) — sanitized worked examples.

## The single rule

When you create or file something, ask: what venture/engagement does this belong to? File it inside that folder. Meeting notes, research, deliverables, learnings — all of it lives nested under the venture, not in a cross-cutting top-level folder.

If it doesn't belong to a single venture, it belongs in one of the cross-cutting folders (Writing, Personal, Reading, Toolkit, Company Building) — and those are smaller, personal domains, not generic catch-alls.

## The three retrieval layers

The conventions encode three layers, each with one job:

1. **Hot pinboard** (`MEMORY.md`) — always loaded. ≤80 lines. User identity, sticky preferences, active venture pointers, decision-time principles inlined. The thing the agent reads on turn one of every session.

2. **Cold index** (`INDEX.md`) — read on demand. Locations, pipelines, dormant ventures, less-frequent feedback. The thing the agent reads when the hot pinboard doesn't answer the question.

3. **Per-venture state** (`_learnings.md`) — one file per active venture or engagement, inside that venture's folder. Append-only. Decisions, key facts, open threads, related sessions. The thing the agent reads when it knows the task is venture-scoped.

These three layers are the entire retrieval model. `grep` walks between them. The tag vocabulary makes the grep useful.

## Why this matters

Without the conventions, an agent given filesystem access becomes either passive (only reads what you tell it) or recklessly noisy (reads everything every time). With the conventions, the agent has a *policy* for what to read when — and that policy is encoded in folder paths and tag namespaces, not in a 4,000-token system prompt that nobody can audit.

Read the files in this order if you're starting fresh:

1. [`conventions.md`](conventions.md) — the folder map.
2. [`frontmatter-schema.md`](frontmatter-schema.md) — the file header.
3. [`tag-vocabulary.md`](tag-vocabulary.md) — the controlled vocab.
4. [`memory-protocol.md`](memory-protocol.md) — the three-tier pattern.
5. [`learnings-template.md`](learnings-template.md) — the per-venture file template.
6. [`operations.md`](operations.md) — the rest of the operating manual.
