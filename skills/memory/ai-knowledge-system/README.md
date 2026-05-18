# AI Knowledge System

> **Want to install the whole 12-repo ecosystem?** Paste [this prompt](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/INSTALL-PROMPT.md) into your Claude Code or Codex session — it interviews you, installs in phases, runs smoke tests, and pauses for confirmation between phases. Or browse the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) first.


**Stop re-explaining context to your AI agent.**

> **New to Claude Code?** [Claude Code](https://docs.anthropic.com/claude/code) is Anthropic's command-line AI agent. [Codex CLI](https://github.com/openai/codex) is OpenAI's equivalent. This repo works with either one. See the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) for the full system overview + onboarding sequence. Vocabulary used here (skill, vault, `_learnings.md`, etc.) is defined in the [glossary](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/GLOSSARY.md).

---

## The problem

If you use an AI agent for serious work, you've probably noticed it has amnesia.

Every new session starts cold. You re-explain who you are and what you're working on. You re-tell it about the Jira field that broke last week and how you worked around it. You correct the same mistakes the same way for the third time. You answer "which file holds the X notes?" again, by paste, because the agent doesn't know.

Over weeks this adds up to two costs:

1. **Time you keep paying.** Same setup explanation, same corrections, same context paste — every session.
2. **Quality you keep losing.** A decision you made three weeks ago doesn't show up when you need it. A trap you've already hit catches you again. The agent's blind spots are the same blind spots, every session.

The fix is structured persistent memory: a tiered system where the agent reads the right context at the right moment without you typing it.

This repo is one such system. Three tiers, two skills to keep them current, and an installer prompt to set it up by interview.

After roughly two weeks of active use, the rate of agent mistakes drops and sessions get measurably cheaper. Cached context reads at about 10× lower cost than fresh.

---

## How it works

| Tier | Holds | When loaded |
|------|-------|-------------|
| **1 — Global** | Role, work style, preferences, hard rules | Every call |
| **2 — Operational memory** | Tool gotchas, API field IDs, vendor quirks, current initiatives | Every call |
| **3 — Domain** | Cross-session learnings, decisions, open threads per product/methodology/research area | On demand |

### Memory vs. regenerated artifacts (the boundary)

The three tiers are all **memory** — facts that persist. Memory is one of two ways an agent reads context. The other is **regenerated artifacts**: derived views the agent reads but never edits, written by a script or skill on a schedule.

| Form | Persistence | Source of truth | Examples |
|---|---|---|---|
| Memory (tiers 1–3) | Persists | The file itself (append-only at tier 3) | `CLAUDE.md`, `MEMORY.md`, `_learnings.md` |
| Regenerated artifact | Whole-file overwritten on each regen | An external source (calendar, MCPs, other vault files) | `Today.md` (working state), `Playbooks-Index.md` (domain map) |

Regenerated artifacts answer questions memory cannot — *what's true right now*, *what's the current index of all playbooks* — without polluting memory with state that decays in hours. They are marked with `type: ephemeral` in frontmatter so lint, archive, and backup tools handle them correctly.

**This repo ships the memory tiers.** Regenerated artifacts are domain-specific (`Today.md` ships in [`vault-cli`](https://github.com/derekcedarbaum2/vault-cli) + a `today` skill; `Playbooks-Index.md` ships in [`note-highlight-indexer`](https://github.com/derekcedarbaum2/note-highlight-indexer)) — but they belong in the same mental model.

**Three operations keep tier 3 current.** Two are in this repo; the third is a separate repo for users who want cron-driven cross-corpus pattern detection later.

| When | Operation | Where it lives | Trigger |
|---|---|---|---|
| End of every meaningful chat | **`/archive-session`** — capture decisions, learnings, open threads from the session and route to the right domain file | This repo | **Manual** — you invoke it |
| Every 2–4 weeks | **`/distill`** — dedupe across recent sessions, resolve stale open threads, promote recurring operational rules to tier 2 | This repo | **Manual** — you invoke it |
| Weekly (Sunday 10pm), once corpus has accumulated | **`learnings-resurface`** — cluster + classify across the whole accumulated corpus (session archives + `_learnings.md` + voice memos), detect cross-source patterns, route principles → playbooks/Router, state → `_learnings.md`, commitments → optional task-manager MCP, contradictions → review | [`learnings-resurface`](https://github.com/derekcedarbaum2/learnings-resurface) (separate repo) | **Automated** — launchd/cron |

The first two are foundational and run on individual sessions / recent windows. The third runs on the *full corpus they build up* — so it only adds value once you've been using the first two for a few weeks.

> ⚠️ **The first two skills don't fire themselves. Until Claude Code adds an automatic session-end skill trigger, you have to invoke them manually.** If you don't run `/archive-session` regularly, the corpus stops accumulating, decisions are lost between sessions, and `learnings-resurface` (when you eventually install it) has nothing to chew on. **Build the habit before you build the rest.**

---

## Quick start

1. **Clone this repo** (or download the zip).
2. **Paste [INSTALL-PROMPT.md](INSTALL-PROMPT.md) into your agent** (Claude Code or Codex). It interviews you for vault location, products, tools, and naming conventions, then writes customized files. Faster than manual find/replace.
3. **Run `/archive-session` at the end of every meaningful chat.** Form the habit now. Skipping this is the #1 way the system decays.
4. **Run `/distill` every 2–4 weeks.** Calendar it. Sunday afternoons work well.
5. (Optional, for later) Once you've been running #3 and #4 for ~6 weeks of active use, install [`learnings-resurface`](https://github.com/derekcedarbaum2/learnings-resurface) for the automated weekly cross-corpus pass.

Prefer manual setup? See [setup-claude-code.md](setup-claude-code.md) (15 min) or [setup-codex.md](setup-codex.md) (30 min).

---

## Who this is for

**Anyone running an AI agent (Claude Code, Codex CLI) for serious daily work where context compounds.** The pattern was originally built and battle-tested for product management in 2026 Q1–Q2, but the structure of the problem — *"I keep re-explaining context to my AI agent every session"* — is domain-agnostic.

It applies to:

- **Product managers** writing PRDs, grooming tickets, doing vendor research, prepping for board ops
- **Engineers** maintaining context on a large codebase, recurring debugging patterns, architectural decisions across many sessions
- **Founders** who keep needing to re-explain their company, ICP, current priorities, deal pipeline
- **Researchers** with running threads across many interview sessions, literature reviews, hypotheses
- **Consultants** managing context across multiple client engagements without bleed-through
- **Lawyers / analysts / writers / solo operators** — anyone who hits the same recurring corrections session after session, has decisions scattered across past chats they can't find, or wants their next session to know what last session decided

The skills shipped in this repo (`/archive-session`, `/distill`) are PM-flavored in their default trigger phrases and example outputs because the author is a PM. **Adapt them to your domain — that's the install path.** The patterns underneath (three-tier memory, append-only `_learnings.md`, Knowledge Router, periodic reconciliation) work for any kind of recurring knowledge work where you'd rather the AI remembered what you taught it last time.

If you're not yet running an AI agent daily, this is overkill. Come back when you're hitting "I keep telling the AI the same things" friction more than once a week.

---

## What's in this repo

```
ai-knowledge-system/
├── README.md                       ← this file
├── INSTALL-PROMPT.md               ← paste into your agent for guided setup
├── setup-claude-code.md            ← 15-min manual setup for Claude Code
├── setup-codex.md                  ← 30-min manual setup for Codex CLI
├── skills/
│   ├── archive-session/SKILL.md    ← end-of-session capture (Claude Code skill format; design ref for Codex)
│   └── distill/SKILL.md            ← cross-session reconciliation
├── templates/
│   ├── MEMORY.template.md          ← starter tier-2 index (platform-neutral)
│   └── _learnings.template.md      ← starter tier-3 domain file (platform-neutral)
└── examples/
    ├── example-MEMORY.md           ← sanitized real example
    └── example-_learnings.md       ← sanitized real example
```

The two `SKILL.md` files were authored for Claude Code's skill loader. Codex users treat them as design references and rewire per [setup-codex.md](setup-codex.md). Templates and examples are platform-neutral and used as-is.

---

## Value in concrete terms

- **No re-explaining.** Project keys, API field IDs, vendor quirks, who owns what — written once, recalled forever.
- **Mistakes don't repeat.** Every correction becomes a memory entry. The Confluence-orphan-comment bug gets fixed once; no future session re-hits it.
- **Cross-session synthesis.** The distill pass resolves stale "open threads" from past sessions when later work answers them. You don't have to remember the question existed.
- **Cheaper sessions over time.** Cached context reads at ~10× lower cost than fresh on Claude Code (Codex caching varies by version). Tight tier-2 + targeted tier-3 loads beat dumping the whole vault into context.

---

## What goes where (the rule of thumb)

| Type of fact | Goes in |
|--------------|---------|
| "I'm a [your role] at $COMPANY working on $PROJECT_OR_DOMAIN" | Tier 1 (global rules) |
| "Jira project key is PROJ1, custom field 11534 is Planned UAT Date" | Tier 2 (operational, breaks tools if wrong) |
| "We decided JTBD format for PRDs after the QA loop on V1.4" | Tier 3 (domain `_learnings.md`) |
| "What we discussed in last Tuesday's session" | Session archive |

If you find yourself writing the same correction twice, it belongs in tier 2.

---

## What this is not

- Not a replacement for documentation. It's the agent's memory, not your team's.
- Not a substitute for git history or Jira tickets. Those are authoritative for code and work tracking.
- Not zero-effort. The first 2 weeks need active capture. After that the loop runs on momentum.

---

## License

MIT. Fork it, modify it, ship it. If you build something useful on top, an issue or PR is appreciated but not required.
