# skills/ — the judgment layer

The conventions in [`../vault/`](../vault/) say what *should* be in the vault. The automation in [`../automation/`](../automation/) enforces what *can* be enforced mechanically. The skills in this folder do the judgment work in between.

Each skill is a Markdown specification that a Claude Code-class agent reads and executes. They are not code. They are instructions, gated examples, and decision rules — the kind of thing that used to live in a long system prompt and rotted within a month. Pulled out into individual files, versioned, and grouped by purpose, they compose into a working agent without becoming an unreadable monolith.

## The four buckets

### [`memory/`](memory/) — three-tier memory pattern, frontmatter discipline, weekly audit

The skills that maintain the memory architecture itself. Distilled from three repos:

- **[`ai-knowledge-system/`](memory/ai-knowledge-system/)** — the three-tier memory pattern (global / operational / domain-routed) with append-only `_learnings.md`. The foundation everything else builds on.
- **[`vault-conventions/`](memory/vault-conventions/)** — folder structure, frontmatter discipline, concurrency lock pattern, and the `/prune-memory` skill that keeps `MEMORY.md` tight.
- **[`vault-lint/`](memory/vault-lint/)** — weekly health check that catches orphan pages, broken wiki-links, missing frontmatter, stale `_learnings.md` files, and contradictions between domain files. Read-only by default.

### [`quality/`](quality/) — adversarial trio, Pinker-grounded prose review

The skills that prevent garbage from going out the door. Distilled from three repos:

- **[`qa-loop/`](quality/qa-loop/)** — adversarial trio (Finder, Disprover, Referee) with competing economic incentives. Three context-isolated subagents find every issue, challenge every issue, and arbitrate. Rewrites only what survives.
- **[`sense-of-style/`](quality/sense-of-style/)** — prose review grounded in Steven Pinker's *Sense of Style*. Scores 8 dimensions, flags line-level problems (nominalizations, passive voice, hedges, broken topic chains), and rewrites preserving voice.
- **[`adversarial-agent-pattern/`](quality/adversarial-agent-pattern/)** — the structural anti-sycophancy mechanism documented as a reusable pattern. Five design rules + a template for new family members (qa-loop, prd-review, pressure-test, sales-qa).

### [`distill/`](distill/) — Readwise → playbook, cross-corpus reconciliation

The skills that turn raw input into operational rules. Distilled from two repos:

- **[`note-highlight-indexer/`](distill/note-highlight-indexer/)** — `/playbook-distill` and `/auto-playbook-distill`. Paste anything you've read (article, book highlights, transcript) and it becomes operational rules in the right domain playbook. Source-tagged, anti-sprawl, no vector DB.
- **[`learnings-resurface/`](distill/learnings-resurface/)** — weekly cron that rereads every session archive, `_learnings.md`, and voice memo, clusters patterns, classifies them (principle / state / commitment / question), and routes them. Source-diversity rule. Contradictions surface for review, never auto-overwrite.

### [`meta/`](meta/) — living architecture map, deterministic CLI primitives

The skills that document the system and offload deterministic work to scripts. Distilled from two repos:

- **[`agentic-architecture-map/`](meta/agentic-architecture-map/)** — a snapshot + append-only evolution log of how the whole system is wired. Updated on every structural change. Prevents setup drift before it starts.
- **[`vault-cli/`](meta/vault-cli/)** — deterministic Node.js CLI primitives for the boring mechanical work (file ops, frontmatter audits, router lookups, skill scaffolding). Skills call the CLI for deterministic work; the LLM does only judgment.

## Installing a skill into your Claude Code

Each skill folder contains a `SKILL.md` (the canonical spec) plus any supporting examples. To install:

```bash
# Copy the SKILL.md into your Claude Code skills dir
cp memory-os/skills/quality/qa-loop/SKILL.md ~/.claude/skills/qa-loop/SKILL.md

# If the skill folder has examples/ or scripts/ subdirs, copy those too
cp -r memory-os/skills/quality/qa-loop/examples ~/.claude/skills/qa-loop/

# Claude Code picks up the skill on the next session
```

The skills are intentionally not packaged as an installer. Each one is small enough to read in five minutes; you should *read* it before installing it, decide whether the conventions match yours, and adjust before saving.

## What "skill" means here

A skill in this context is a discrete, named capability that an agent loads on demand. Anthropic shipped Skills as a first-class concept in Claude Code in mid-2026; the format matches what they ship. Each skill has:

- A **trigger** (when to activate)
- A **workflow** (what to do)
- A set of **rules** (what not to do)
- **Examples** (what good output looks like, what bad output looks like)

If you're not on Claude Code, the same patterns work as system-prompt sections or as Cursor Rules — but the discrete-file structure prevents the monolithic-prompt failure mode where everything degrades together.

## How the four buckets interact

```
        ┌──────────────────────┐
        │  meta/ (architecture │
        │   map, vault-cli)    │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  memory/ (the storage│
        │  + retrieval surface)│
        └──────────┬───────────┘
                   │
       ┌───────────┴───────────┐
       ▼                       ▼
┌─────────────┐         ┌──────────────┐
│  distill/   │         │  quality/    │
│  (input →   │         │ (output      │
│   memory)   │         │  refinement) │
└─────────────┘         └──────────────┘
```

- **memory/** is the substrate. The other three operate against it.
- **distill/** writes *into* the memory substrate from external sources (read material) and internal sources (accumulated session archives).
- **quality/** operates on artifacts the agent produces — running adversarial loops before something gets shipped.
- **meta/** documents the system itself and provides primitives the other skills call when they need deterministic work done.

## A note on size

Each skill SKILL.md is generally 100–500 lines. That's an enforced ceiling. If a skill grows past ~500 lines, it's probably doing two things and should be split into two skills.

The exception is `claude-code-setup` (the umbrella reference), which is documentation, not a runnable skill — and which is being absorbed and condensed into the present repo. The original README of `claude-code-setup` is preserved in [`memory/ai-knowledge-system/`](memory/ai-knowledge-system/) for reference.
