---
title: Playbooks Index
type: reference
status: active
classification: internal
created: 2026-05-04
updated: 2026-05-04
author: "<your-name>"
tags: [playbooks, routing, index, meta]
---

# Playbooks Index

> **⚠ BEFORE FIRST USE — adapt the `Playbook Path` column below.**
>
> The default paths (`Company Building/`, `Personal/`, `Writing/`, `Professional Development/`, etc.) assume a particular personal-vault layout. If your vault top-level folders don't match, pick one:
>
> - **(a) Adapt to existing folders** — change each path to a folder that already exists in your vault (e.g., `Tech → Toolkit/Tech Playbook/`). Best when you want playbooks to live alongside existing content.
> - **(b) Scaffold new top-level folders** — leave the defaults; the skill will create them on first hit. Best when you want clean separation between the playbook system and the rest of your vault.
>
> If you're an agent installing this on a user's behalf, **ask the user before making this choice** — it shapes their vault layout long-term.

Cross-cutting compaction layer for the vault. Each playbook is a folder of operationalized topic files (scorecards, decision triggers, anti-patterns, fillable templates) sourced from books, articles, podcasts, and lived experience. Used by the auto-distill pipeline (`~/.claude/skills/auto-playbook-distill/`) and by skills that need domain context.

> **Rule:** every playbook follows the same pattern — `README.md` (with task router) + topic files + inline source tags. New playbooks scaffold automatically when the auto-distiller encounters a new domain. Topic files split when one exceeds ~400 lines.

## The 10 Playbook Domains

| # | Domain | Playbook Path (vault-relative) | Status | What feeds it |
|---|--------|---------------|--------|----------------|
| 1 | **Startup / Business Building** | `Company Building/Startup Playbook/` | not yet scaffolded | YC analyses, founder essays, GTM frameworks, pitch teardowns |
| 2 | **Investing / Markets / Finance** | `Company Building/Investing Playbook/` | not yet scaffolded | Investor biographies, market histories, valuation frameworks |
| 3 | **Health / Body / Nutrition / Biomechanics** | `Personal/Health & Wellness/Health Playbook/` | not yet scaffolded | Nutrition books, exercise science, sleep, longevity, biomechanics |
| 4 | **Parenting / Kids / Education** | `Personal/Family/Parenting Playbook/` | not yet scaffolded | Doman, Montessori, Waldorf, child development, education research |
| 5 | **Writing / Communication / Voice** | `Writing/Writing Playbook/` | not yet scaffolded | Style, voice, rhetoric, copywriting, narrative theory |
| 6 | **Philosophy / Mental Models** | `Personal/Philosophy/Philosophy Playbook/` | not yet scaffolded | Decision theory, epistemology, ethics, schools of thought |
| 7 | **Politics + Economics / Public Policy** | `Personal/Politics/Politics-Economics Playbook/` | not yet scaffolded | Monetary theory, market design, policy critique |
| 8 | **Leadership + Operating Discipline** | `Company Building/Leadership Playbook/` | not yet scaffolded | Command, coaching, executive cadence, debrief, operating discipline |
| 9 | **Personal OS / Productivity / Life Systems** | `Personal/Personal Development/Personal OS Playbook/` | not yet scaffolded | Time management, attention, habits, knowledge management |
| 10 | **Tech / AI / Software / Engineering** | `Professional Development/AI/Tech Playbook/` | not yet scaffolded | AI/ML, software architecture, agent design, dev tooling |

## Routing Rules (For The Auto-Distiller)

When a Readwise file lands, the distiller picks **one primary playbook** based on the dominant content:

1. **Strong match (single domain)** → merge into that playbook only.
2. **Spanning two domains** → primary merge in the dominant one, cross-reference link in the secondary's relevant topic file (no duplicate paragraphs).
3. **Spanning 3+ domains** → likely a broad / structural insight; route to the most operational domain (where the rule actually applies). Cross-reference others.
4. **No clear match in the 10** → DO NOT create an 11th playbook silently. Append to `raw-sources/_unrouted-distill-queue.md` with file path + reason. User decides whether to add a domain.

## Domains That Are NOT Playbooks (And Why)

- **History / Biography** — source domain. A Bezos biography feeds Startup. A Buffett biography feeds Investing. A Lincoln biography feeds Politics. No standalone playbook unless volume exceptional.
- **Random / Memoir / General Non-Fiction** — content gets routed to the operational domain it informs, not its own playbook.
- **Recipes / How-To / Reference Material** — these are reference docs, not operational rules. Stay raw in their existing folders.

## Per-Playbook Conventions

Every playbook MUST have:

1. **`README.md`** — frontmatter, file index, task router (which files to load for which task), conventions, sources captured.
2. **Topic files** — operational format only (scorecards, decision triggers, anti-patterns, fillable templates). No narrative archives.
3. **Source tags inline** — every claim ends with `[source name, date]` so attribution is traceable.
4. **Update, don't append** — new content merges into existing topic files unless creating a clearly new dimension (then a new topic file, with README updated).

The auto-distiller enforces all four when scaffolding new playbooks.

## How To Use

**For agents needing domain context:** load this file first, route to the relevant playbook, load that playbook's `README.md` for its task router. Don't load all 10 playbooks.

**For skills:** wire each skill to load the relevant playbook(s). E.g., `/write-tweets` → Writing Playbook + Startup Playbook (gtm voice). `/baby-learning-coach` → Parenting Playbook. `/sense-of-style` → Writing Playbook.

**For new content arriving:** the auto-distill pipeline runs daily at 7:30am via launchd. Manual invocation: `/playbook-distill` (interactive) or `~/.claude/hooks/auto-distill-readwise.sh` (batch).

## Playbook Lifecycle

| Stage | What happens |
|-------|--------------|
| **Scaffold** | Auto-distiller hits first source for a domain. Creates folder + `README.md` + first topic file. Adds source tag. Logs to `Vault/log.md`. |
| **Grow** | Each new source merges into existing topic files OR (if dimension is new) creates a new topic file and updates README. |
| **Split** | When a topic file exceeds ~400 lines OR covers two clearly distinct dimensions, split. Don't pre-split. |
| **Cross-link** | When an insight spans two playbooks, primary merge in one + `[[wiki-link]]` cross-reference in the other. Never duplicate. |
| **Prune** | If a topic file gets stale (no new sources in 12 months) AND its rules haven't been applied, flag for human review. (Future automation.) |

## Active Playbook Status

| Playbook | Files | Last Source Added |
|----------|-------|-------------------|
| Startup | — | not yet scaffolded |
| Investing | — | not yet scaffolded |
| Health | — | not yet scaffolded |
| Parenting | — | not yet scaffolded |
| Writing | — | not yet scaffolded |
| Philosophy | — | not yet scaffolded |
| Politics+Economics | — | not yet scaffolded |
| Leadership | — | not yet scaffolded |
| Personal OS | — | not yet scaffolded |
| Tech | — | not yet scaffolded |

(Updated automatically by the auto-distill pipeline.)
