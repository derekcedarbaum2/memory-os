# `_learnings.md` template

Every venture or engagement folder gets one `_learnings.md`. Append-only. Never rewrite. This is the canonical per-venture state file.

## Template

```markdown
---
title: <Venture> — Learnings
type: reference
status: active
classification: internal
created: YYYY-MM-DD
updated: YYYY-MM-DD
author: "Derek Cedarbaum"
tags: [venture:<slug>, kind:state, decay:high]
---

# <Venture> — Learnings

Domain knowledge accumulated across sessions. Append only. Never rewrite.

## Status snapshot

<One paragraph: what this venture is, where it stands, who's involved, what's
load-bearing right now. Update by rewriting this section in place — it's the
only part of the file that isn't append-only.>

## Learnings

<!-- Append new insights with source citation: "- Insight text *(from [[session-id]])*" -->

## Key Decisions

| Date | Decision | Why | Session |
|---|---|---|---|

## Open Threads

<!-- Unresolved work items with parent session reference. Move to Learnings or
     Key Decisions when resolved. -->

## Related Sessions

| Date | Session | Summary |
|---|---|---|

## Related

<!-- [[wiki-links]] to related principles, locations, other ventures.
     Link liberally; agents walk the graph at retrieval time. -->
```

## How to fill each section

### Status snapshot

The only section that can be rewritten in place. One paragraph or one bulleted list, no more. What's the venture's current state? Who's involved? What's the immediate next decision? Don't repeat content that lives in Learnings or Key Decisions below.

If you find yourself writing more than ~150 words here, split: the durable thesis goes into a `_strategy.md` next to this file; the snapshot stays terse.

### Learnings

Append-only insights, one per line. Each line ends with a source citation in the form `*(from [[session-id]])*` where session-id matches a file in `AI Toolkit/CC Chat History/`.

Sample:

```markdown
- The fractional CAIO category is a feature, not a category — every firm in the
  field sells "fractional CAIO" the way 2018 firms sold "Digital Transformation"
  *(from [[2026-04-26-cheney-research-session]])*
```

Never reword an existing learning. If you've changed your mind, append a new learning that contradicts the old one and let both stand.

### Key Decisions

Table format. One row per decision. Each row has a date, a one-line decision, a one-line rationale, and a session link.

```markdown
| 2026-04-17 | Filed venture separate from Bastion | Different ICP and thesis | [[2026-04-17-...]] |
```

A decision is something with a binary resolution that downstream work depends on. "We picked LLC over C-corp." "We will not pursue defense customers in Year 1." Not vibes.

### Open Threads

Bulleted list of unresolved items. Each item with a session reference.

```markdown
- Pick geography + vertical for specialization *(surfaced [[2026-04-26-...]])*
- Renewal mechanic at month 9 — what's the upgrade path? *(surfaced [[2026-04-26-...]])*
```

When an open thread resolves, move it to Learnings or Key Decisions with a resolution note. Don't just delete it; the resolution is more valuable than the question.

### Related Sessions

Table format. One row per session that touched this venture. Each row has a date, a session link, and a one-line summary.

```markdown
| 2026-04-26 | [[2026-04-26-cheney-research]] | Competitive landscape research, 6 dossiers |
```

This section is mostly maintained by the `/archive-session` skill — it appends an entry every time a session is archived and tagged to this venture.

### Related

Wiki-links to related principles, locations, or other ventures. Link liberally. Cross-references compound: a stranger reading this file should be able to walk to the connected files.

```markdown
- [[principle_one_wedge_per_pitch]] — applies when shaping outreach for this venture
- [[venture:unlikely-labs]] — sibling engagement
```

## What NOT to put in `_learnings.md`

- **Deliverables.** Those go in `Deliverables/`.
- **Meeting notes.** Those go in `Meetings/`.
- **Research dossiers.** Those go in `Research/`.
- **The thesis or strategic anchor.** That goes in `_strategy.md` (optional sibling file).

`_learnings.md` is *learnings about the venture* — facts I've earned that need to inform every future session — not the venture's working files.

## Hygiene rules

1. **Append only.** Never rewrite a Learning. If you change your mind, append a contradicting Learning and let both stand.
2. **Cite sources.** Every Learning ends with a `[[session-id]]`. If you can't cite, you're not sure enough to commit.
3. **Move resolved threads.** Open Thread → resolved? Move it to Learnings or Key Decisions with a resolution note.
4. **Update the snapshot in place.** That's the only section that's not append-only. Keep it short.
5. **Cross-reference.** Wiki-link to principles, sibling ventures, and locations. The graph is your indexer.

## When to retire

When a venture goes dormant for 90+ days, the dormancy-decay cron adds `status:dormant` to this file's frontmatter and the active-venture-refresh cron moves the venture's pinboard pointer from `MEMORY.md` to `INDEX.md`'s Dormant section. The file itself stays — it's history, not deletable.

If the venture is truly dead (entity dissolved, project killed), set `status: archived` and move the folder to `Vault/_archive/<venture-name>/`. Don't delete; the learnings still apply to future ventures of the same shape.
