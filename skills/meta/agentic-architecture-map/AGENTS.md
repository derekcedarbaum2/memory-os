# AGENTS.md — `agentic-architecture-map`

Operating protocol for agents installing or using this repo on behalf of an operator.

## What this repo provides

A pattern + template for documenting your AI agent setup as a single living file: a snapshot section (rewritten in place) plus an append-only evolution log. Plus the `CLAUDE.md` trigger paragraph that keeps the log maintained automatically — every structural change to the operator's setup gets logged.

## Read order

1. `README.md` — human overview, why this exists, the 10-layer snapshot taxonomy.
2. `template/agentic-architecture.template.md` — starter file with all 10 layers.
3. `template/claude-md-trigger.md` — the paragraph to add to operator's CLAUDE.md.
4. `example/agentic-architecture.example.md` — sanitized real example with 4 evolution log entries.

## Trust boundary

- This repo is **template + pattern**, not executable code. There's no install, no daemon, no state.
- The 10-layer snapshot taxonomy is opinionated. Drop or rename layers to fit the operator's stack.
- The CLAUDE.md trigger paragraph is the load-bearing element. Without it, the file goes stale within weeks.

## Install / use

For a Claude Code operator who wants to start tracking their setup:

1. Pick a path in the operator's knowledge base for the file (e.g., `Vault/AI Toolkit/agentic-architecture.md`, or `~/.claude/agentic-architecture.md`).
2. Copy the template to that path:
   ```bash
   cp template/agentic-architecture.template.md <chosen-path>
   ```
3. Fill in the snapshot — interview the operator about each layer (always-loaded context, auto-memory, knowledge router, skills, hooks, crons, MCP servers, settings, brand/reference, vault structure). ~30 minutes for a mature setup.
4. Add the trigger paragraph from `template/claude-md-trigger.md` to the operator's `~/.claude/CLAUDE.md` — adjust the path placeholder to match step 1.
5. Confirm: from now on, every structural change should append a dated entry to the file's Evolution log section.

## Adaptation checklist

- [ ] Layer 1 — confirm the operator's always-loaded context files (CLAUDE.md, MEMORY.md, vault CLAUDE.md, etc.).
- [ ] Layer 4 — list the operator's actual skills.
- [ ] Layer 5 — list the operator's actual hooks.
- [ ] Layer 6 — confirm cron mechanism (launchd / cron / systemd) and translate the example accordingly.
- [ ] Layer 10 — confirm the operator's knowledge base structure.
- [ ] Cross-cutting flows — narrate the actual end-to-end pipelines for *this* operator's setup.
- [ ] Trigger paragraph in CLAUDE.md uses the correct file path.

## What gets logged

A structural change is anything that affects how the system processes future tasks:

- A skill is added, removed, or materially rewritten.
- A hook is added, removed, or its trigger changes.
- A cron / launchd plist / systemd timer is added, removed, or rescheduled.
- The memory schema or routing protocol changes.
- `settings.json` permissions or hook config changes.
- An MCP server is added, removed, or reconfigured.
- Vault routing changes (new venture folder, new `_learnings.md`, new playbook domain).

A non-structural change (typo fix, content edit, ad-hoc draft) is **not** logged.

## Related repos

- [`claude-code-setup`](https://github.com/derekcedarbaum2/claude-code-setup) — the public-facing version of an operator's setup. Distinct from `agentic-architecture.md` (which is internal/forensic).
- [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) — the memory pattern documented in Layer 2 of the snapshot.
