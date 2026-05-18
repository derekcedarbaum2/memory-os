# Agentic Architecture Map

> **Want to install the whole 12-repo ecosystem?** Paste [this prompt](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/INSTALL-PROMPT.md) into your Claude Code or Codex session — it interviews you, installs in phases, runs smoke tests, and pauses for confirmation between phases. Or browse the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) first.


**A single document that tracks how your AI agent setup is wired — and a log of every change so you can see how it got that way.**

> **New to Claude Code?** [Claude Code](https://docs.anthropic.com/claude/code) is Anthropic's command-line AI agent. Once you start adding skills, hooks, and crons, the setup becomes a system you can lose track of. See the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) — full system overview + onboarding sequence — or [`claude-code-setup`](https://github.com/derekcedarbaum2/claude-code-setup) for the umbrella reference doc. Vocabulary used here (skill, hook, MCP, cron, etc.) is defined in the [glossary](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/GLOSSARY.md).

---

## The problem

If you've been using Claude Code (or any AI agent setup) seriously for more than a few months, you have the same problem:

- A skill broke last Tuesday and you can't remember which hook triggered it.
- You added an MCP server six weeks ago and now you're not sure why.
- A teammate asks "how does your setup work?" and you write a fresh explanation that's already drifted by next week.
- You're considering retiring something but don't remember the original purpose.

The fix is not another README. The fix is a **single internal file** that documents the wiring as-it-is plus a **dated, append-only log** of every structural change. The README drifts; the log doesn't lie.

This repo is the pattern: one file, one trigger, one rule.

---

## The pattern

You maintain **one file** in your knowledge base — `agentic-architecture.md` — with two halves:

```
┌─ Snapshot (rewritten in place) ─────────────────────┐
│ Layer 1 — Always-loaded prompt context              │
│ Layer 2 — Auto-memory                               │
│ Layer 3 — Knowledge Router + domain learnings       │
│ Layer 4 — Skills                                    │
│ Layer 5 — Hooks                                     │
│ Layer 6 — Crons                                     │
│ Layer 7 — MCP servers                               │
│ Layer 8 — Settings                                  │
│ Layer 9 — Brand / reference                         │
│ Layer 10 — Vault structure                          │
│ Cross-cutting flows                                 │
│ Portability notes                                   │
│ Open optimization questions                         │
├─ Evolution log (append-only, dated entries) ────────┤
│ ### 2026-05-06 — entry                              │
│ ### 2026-05-04 — entry                              │
│ ### 2026-05-03 — entry                              │
│ ...                                                  │
└─────────────────────────────────────────────────────┘
```

You add **one trigger** to your global agent instructions (`CLAUDE.md` for Claude Code, equivalent for other harnesses):

> Whenever you make or observe a structural change to a skill, hook, cron, MCP server, memory schema, or routing — **append a dated entry to the Evolution log section of `[path]/agentic-architecture.md`** using the template at the bottom of the file. If the snapshot section above the log has gone stale because of the change, also update the relevant snapshot subsection in place.

You enforce **one rule:**

> Don't skip the log for "small" structural changes. Those are exactly the ones that compound and get lost.

That's the whole pattern.

---

## Why this works

**Snapshot rewriting + append-only log is the durable shape.** Two single failures motivate it:

1. **README-only setups drift silently.** You update the README the first three times you change something. By month four, the README is wrong and nobody trusts it. Without an append-only log, you can't even tell *when* it went wrong.

2. **Log-only setups are unreadable.** A pure changelog is great for forensics but terrible for "what does my system look like right now?" You need both.

The snapshot answers *what is true*. The log answers *how did we get here, and why*.

The trigger in `CLAUDE.md` makes maintenance free — every structural change you ask Claude to make also gets logged, automatically, because you instructed it to. You don't have to remember to update the doc.

---

## What gets logged

A structural change is anything that affects how the system is wired:

- A skill is added, removed, or materially rewritten
- A hook is added, removed, or its trigger changes
- A launchd plist / cron / systemd timer is added, removed, or rescheduled
- The memory schema or routing protocol changes (e.g., Knowledge Router rule shift)
- `settings.json` permissions or hook config changes
- An MCP server is added, removed, or reconfigured
- Vault routing changes (new venture folder, new `_learnings.md`, new playbook domain, new `_strategy.md`)

A non-structural change is a one-off content edit — adding a learning to an existing `_learnings.md`, fixing a typo in a skill, drafting a doc. Don't log those.

The line is: **does this change how the system processes future tasks?** If yes, log it.

---

## What's in this repo

```
agentic-architecture-map/
├── README.md
├── LICENSE
├── template/
│   ├── agentic-architecture.template.md   ← Starter file with all 10 layers
│   └── claude-md-trigger.md                ← The CLAUDE.md instruction to add
└── example/
    └── agentic-architecture.example.md     ← Sanitized real example with ~20 evolution log entries
```

---

## Quick start

1. **Pick a path** — somewhere in your knowledge base. Author's choice: `Vault/AI Toolkit/agentic-architecture.md`. Anything stable will do.

2. **Copy the template** to that path:
   ```bash
   cp template/agentic-architecture.template.md ~/path/to/agentic-architecture.md
   ```

3. **Fill in the snapshot** — walk through your current setup once and document each layer. This is the only manual part. ~30 minutes for a mature setup.

4. **Add the trigger** to your global `CLAUDE.md` — copy the contents of `template/claude-md-trigger.md` (one paragraph) into your CLAUDE.md, adjusting the path to match step 1.

5. **Stop maintaining it manually.** From here, every time you ask Claude to add a skill / change a hook / install an MCP, the trigger fires and the evolution log gets a new entry. Re-read the file once a month to catch drift.

---

## Why the snapshot has those 10 layers

The snapshot taxonomy is opinionated. The layers cover every place a structural change can hide:

| Layer | Catches |
|---|---|
| 1 — Always-loaded context | What loads on every API call (CLAUDE.md, MEMORY.md, vault CLAUDE.md). The most cost-sensitive layer. |
| 2 — Auto-memory | Persistent memory schema and current contents (count by type). |
| 3 — Knowledge Router + domain learnings | The retrieval layer — how task → relevant context. |
| 4 — Skills | Slash commands. The visible surface. |
| 5 — Hooks | Event-triggered scripts (SessionEnd, UserPromptSubmit). The invisible surface. |
| 6 — Crons | Scheduled runs. The "things that fire when you're not looking" layer. |
| 7 — MCP servers | External tool access. The integration layer. |
| 8 — Settings | Model choice, permissions, hook config. The harness config. |
| 9 — Brand / reference | Static reference docs the agent can read on demand. |
| 10 — Vault structure | The knowledge base layout itself. |

Plus three cross-cutting sections:
- **Cross-cutting flows** — narrated end-to-end pipelines (e.g., "voice memo → cron → skill → action"). The "how do I trace what happens when X" section.
- **Portability notes** — what would survive a machine migration vs. what's environment-locked.
- **Open optimization questions** — the running list of "we should probably address this someday" items.

Drop or rename layers to fit your stack. The point is *cover every structural surface*; the specific taxonomy is adjustable.

---

## Why "evolution log" not "changelog"

A changelog is for shipped versions of software. This is for an internal system that nobody else uses, and that doesn't have versions. The relevant unit is *the change itself* — when, what, why, what files touched, what's now true that wasn't before.

The example in this repo shows the format. Each entry has:

- **Date** (heading)
- **Trigger** — what prompted the change
- **What changed** — concrete files / configs / scripts
- **Why** — the reasoning, including evidence or external sources that justified it
- **Files touched** — paths
- (Optional) **Identified gaps / follow-ups** — what this change implied for next time

Keep entries dense. Future-you will thank you for "Why" lines that explain reasoning, not just record what was done.

---

## What this is not

- **Not a generic project changelog.** This is for *your* agent setup, not a public-facing software project. Don't conflate them — your `claude-code-setup.md` (or equivalent) is the public face; this is the internal forensic record.
- **Not a substitute for git history.** Git tells you when files changed. This tells you why the *system* changed.
- **Not a substitute for `CLAUDE.md`.** `CLAUDE.md` is what the agent reads on every call. This file is reference material loaded on demand when discussing the system itself.

---

## License

MIT.
