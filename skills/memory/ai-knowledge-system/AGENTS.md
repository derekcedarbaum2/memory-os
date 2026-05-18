# AGENTS.md — `ai-knowledge-system`

Operating protocol for agents installing this for an operator.

## What this repo provides

A three-tier persistent-memory pattern for AI agents (Claude Code or Codex CLI). Two skills (`/archive-session` and `/distill`) keep the knowledge base current.

- **Tier 1** — Global rules (every call): role, work style, hard rules.
- **Tier 2** — Operational memory (every call): tool gotchas, API field IDs, vendor quirks, current initiatives.
- **Tier 3** — Domain (on demand): cross-session learnings, decisions, open threads per product / methodology / research area.

## Read order

1. `README.md` — human overview, what goes where, who this is for.
2. `INSTALL-PROMPT.md` — the install-via-agent prompt. Paste this verbatim into the agent (Claude Code or Codex) and it interviews the operator for vault location, products, tools, conventions, then writes customized files.
3. `setup-claude-code.md` — manual 15-min setup for Claude Code operators.
4. `setup-codex.md` — manual 30-min setup for Codex CLI operators.
5. `skills/archive-session/SKILL.md` — end-of-session capture skill.
6. `skills/distill/SKILL.md` — cross-session reconciliation skill.
7. `templates/MEMORY.template.md` — starter Tier 2 index.
8. `templates/_learnings.template.md` — starter Tier 3 domain file.
9. `examples/example-MEMORY.md` and `examples/example-_learnings.md` — sanitized real examples.

## Trust boundary

- The two `SKILL.md` files were authored for Claude Code's skill loader. Codex users treat them as design references and rewire per `setup-codex.md`.
- Templates and examples are platform-neutral.
- The "what goes where" rule of thumb in `README.md` is load-bearing — preserve when adapting.

## Install

**Recommended (agent-driven):**

Paste the contents of `INSTALL-PROMPT.md` into the agent. It interviews the operator and writes files. ~15–30 minutes.

**Manual:**

Follow `setup-claude-code.md` (Claude Code) or `setup-codex.md` (Codex CLI). 

## Adaptation checklist

- [ ] Operator's vault / knowledge-base location identified.
- [ ] Operator's main products / projects / engagements listed (for Tier 3 file scaffolding).
- [ ] Operator's tools / APIs identified (for Tier 2 gotcha capture).
- [ ] Tier 1 (global rules) reflects operator's role, work style, voice preferences.
- [ ] Tier 2 (`MEMORY.md`) starts with at least 3 entries (tool gotchas observed during the install conversation count).
- [ ] Tier 3 — at least one `_learnings.md` per active product / engagement.

## Common tasks for ongoing operation

| Task | Skill |
|---|---|
| End a meaningful chat — capture decisions / learnings | `/archive-session` |
| Periodic reconciliation across past sessions | `/distill` (every 2–4 weeks) |
| Find which `_learnings.md` to load for a task | Knowledge Router pointers in MEMORY.md |

## Related repos

- [`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions) — frontmatter discipline + hygiene tooling that pairs with this memory system.
- [`learnings-resurface`](https://github.com/derekcedarbaum2/learnings-resurface) — weekly reconciliation across accumulated interaction memory.
- [`vault-lint`](https://github.com/derekcedarbaum2/vault-lint) — vault hygiene scanner.
