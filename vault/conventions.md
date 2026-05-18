# Vault conventions

A `memory-os` vault is an Obsidian-style Markdown folder tree organized around one mental model: **everything lives inside the venture or engagement folder it came from.**

## The single rule

When you create or file something, ask: what venture/engagement does this belong to? File it inside that folder. Meeting notes, research, deliverables, learnings — all of it lives nested under the venture, not in a cross-cutting top-level folder.

If it doesn't belong to a single venture, it belongs in one of the cross-cutting folders (Writing, Personal, Reading, Toolkit, Company Building) — and those are smaller, personal domains, not generic catch-alls.

## Reference top-level structure

This is the structure I run. Adapt the venture names; preserve the shape.

```
Vault/
├── Work/                       Professional engagements, clients
│   ├── <client-or-engagement>/
│   │   ├── _learnings.md       Append-only per-venture state
│   │   ├── _strategy.md        Optional — durable strategic anchor
│   │   ├── Meetings/           Dated meeting notes
│   │   ├── Research/           Venture-specific research
│   │   └── Deliverables/       Artifacts shipped to stakeholders
│   └── ...
│
├── Ideas/                      Pre-engagement ventures and concepts
│   └── <venture-name>/         Each gets its own folder
│       └── _learnings.md
│
├── Personal/                   Family, health, philosophy, recipes
├── Writing/                    Essays, books, articles
├── Reading/                    Synced from a read-it-later service
├── Professional Development/   Cross-employer skills
├── Company Building/           Cross-venture methods
├── AI Toolkit/                 Skills, prompts, session archives
│   └── CC Chat History/        Session transcripts (auto-saved)
│
├── _archive/                   Done or inactive
├── _attachments/               Images and media
├── raw-sources/                Inbox for unprocessed inputs
│
├── CLAUDE.md                   Agent instructions for the vault
├── log.md                      Append-only operation log
└── Today.md                    Regenerated ephemeral working artifact
```

## What each top-level folder is for

- **`Work/`** — Anything where someone is paying you, or where you're trading time for a contractual relationship. Each client/engagement gets its own folder with a `_learnings.md` at minimum.
- **`Ideas/`** — Ventures that don't yet have revenue or a contract. Folders here can graduate to `Work/` when they earn it.
- **`Personal/`** — Family, health, recipes, personal-finance. Strictly excluded from cross-venture clustering by automation.
- **`Writing/`** — Long-form output for public consumption. Different folder because the *audience* and *voice* are different.
- **`Reading/`** — Input from read-it-later services (Readwise, Pocket). Generally excluded from edits because external sync will overwrite them.
- **`Professional Development/`** — Cross-employer skill-building. Generic AI adoption learnings; interview prep; certifications.
- **`Company Building/`** — Methods (Startup Playbook, Strategy Method) and cross-venture notes (Operations, Pricing, Hiring).
- **`AI Toolkit/`** — Skills, prompts, the architecture map. `CC Chat History/` is where session transcripts auto-save.

## Inside each venture/engagement folder

A well-formed venture folder looks like:

```
Ideas/<venture>/
├── _learnings.md            Append-only per-venture state
├── <hypothesis>.md          Core thesis document
├── Meetings/                Dated meeting notes (when they happen)
├── Research/                Venture-specific research
└── Deliverables/            Artifacts shipped to stakeholders
```

Not every venture needs every subfolder on day one. `_learnings.md` is the minimum. The rest accrete as work happens.

## Core working rules

1. **Orient first.** Scan the relevant venture folder before making changes.
2. **File inside the venture.** Don't create cross-cutting folders for things that belong to a single venture.
3. **Maintain confidentiality.** Tag with the right `classification:` in frontmatter; treat `confidential` as load-bearing.
4. **Be precise.** Exact names, dates, figures.
5. **Preserve voice.** Match the tone of the folder (Work professional, Writing raw, Ideas exploratory, Personal private).
6. **Track decisions.** Note who decided what, why, when, in the venture's `_learnings.md` under Key Decisions.
7. **Date everything.** Include dates on meetings, deliverables, decisions.
8. **Update, don't duplicate.** If information exists, update it rather than creating a new page.
9. **Depth over breadth.** Develop ideas fully rather than collecting shallow notes.
10. **Frontmatter first.** Add YAML frontmatter when creating any new `.md`. Backfill when editing old files.

## Connections and linking

Use `[[wikilinks]]` for internal vault links. Wiki-link liberally — a `[[name]]` that doesn't yet match an existing file is fine; it marks intent.

When processing new content, suggest connections to existing notes. Add links with context — explain *why* notes relate to each other.

## Operation log

`log.md` at the vault root is append-only. Crons append automatically; interactive sessions append on substantive structural changes (new folder, new `_learnings.md`, large reorg).

## Why this shape

The shape is opinionated because the alternative — flat, by-type, or organized by my-recent-feeling — does not survive contact with two years of accumulated notes. The venture-first organization works because (a) most of what a knowledge worker does *is* organized around active engagements, and (b) the few cross-cutting things are small in number and stable in identity (writing, personal, reading).

Adapt the folder names. Don't dilute the rule.
