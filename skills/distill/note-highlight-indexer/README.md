# note-highlight-indexer · Distill what you read into operational rules

> **Want to install the whole 12-repo ecosystem?** Paste [this prompt](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/INSTALL-PROMPT.md) into your Claude Code or Codex session — it interviews you, installs in phases, runs smoke tests, and pauses for confirmation between phases. Or browse the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) first.


**Paste anything you've read worth keeping into your coding agent, run `/playbook-distill`, and it becomes operational rules** — scorecards, decision triggers, anti-pattern detectors, fillable templates — inside a domain-specific "playbook" file your AI loads at the right moment. Plain Markdown + grep, no vector DB. The reading half of the [writing-layer-over-retrieval-layer thesis](https://github.com/derekcedarbaum2/claude-code-setup#the-thesis-writing-layer-over-retrieval-layer): turn passive reading into rules an agent applies on your behalf.

> **New to Claude Code?** [Claude Code](https://docs.anthropic.com/claude/code) is Anthropic's command-line AI agent. [Codex CLI](https://github.com/openai/codex) is OpenAI's equivalent. This repo works with either one. See the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) for the full system overview + onboarding sequence. Vocabulary used here (skill, vault, playbook, etc.) is defined in the [glossary](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/GLOSSARY.md).

## The problem

For years on and off, I read articles and books, highlighted notes in the book or put something into an Evernote note — and then it disappeared into the ether, rarely to be used and even less frequently to be integrated. Business stuff, history books, health books. 10–15 years of notes and highlights, created and mostly lost to the sands of time.

If you read a lot and have ever felt that gap — between *encountering* an idea and *being able to retrieve it when you need it* — this is built for that.

The fix isn't another note-taking app. It's a script that reads what you've already highlighted and converts each insight into operational form (a scorecard row, a decision trigger, an anti-pattern detector) inside a topic-specific playbook the AI agent reads at the right moment. Information you were deferential to becomes information the agent applies on your behalf.

## What it does

**Paste anything you've read worth keeping into your coding agent (Claude Code, Codex CLI, Codex web — works in any of them), run the `playbook-distill` prompt, and it gets distilled into operational rules** — scorecards, decision triggers, anti-pattern detectors, fillable templates — inside a domain-specific "playbook" file (Startup, Tech, Health, Writing, Personal OS, Investing, Parenting, Philosophy, Politics+Economics, Leadership). Next time you're working on a project, the AI loads the relevant playbook and applies what you've already read instead of generic web knowledge or vague memory.

Plain markdown + grep, no vector DB, no proprietary index. There's an optional Readwise auto-processing mode if you want it to also pick up your highlights overnight.

## Works with

- **Claude Code** — installable as a slash command (`/playbook-distill`). See `skills/`.
- **Codex CLI / Codex web / other agents** — paste the prompt or load it as a custom prompt file. See `prompts/`.

The prompt logic is identical between modes; only the install convention differs.

## How it might fit your work

Useful anywhere you read documents and lose the takeaways:

- **Highlights from RFPs** — store the *rules*, not the document. Agents find the rules without context-rotting on the full PDF.
- **Notes from research papers** — distill the methodology rules into the relevant playbook, source-tagged.
- **Tactical lessons from internal docs** — feed forward into your existing skills and projects via per-domain playbooks tied to your `MEMORY.md` / `CLAUDE.md` / `_learnings.md` files.

The data gets properly stored and indexed, tied to your existing skills and projects.

## Two modes

### Mode 1 — Manual paste-in (most users use this)

Open your coding agent in your vault. Paste an article, an essay, a transcript excerpt, a slide quote, a book passage, anything operational. Then signal intent — any of these work:

- **Casual:** "store this", "save this", "capture this", "keep this", "file this", "make a note of this"
- **Playbook-specific:** "add this to the playbook", "distill this", "operationalize this", "playbook this"
- **Explicit:** type `/playbook-distill` (Claude Code) or invoke the `prompts/playbook-distill.md` prompt (Codex CLI / web)

The agent classifies the content into one of 10 domains, picks the right playbook, distills the content into operational format, source-tags every claim, and merges into the existing topic file (or scaffolds a new playbook if it's a domain you haven't seeded yet).

In Claude Code, casual triggers work out of the box (the skill's auto-activation reads natural phrases). In Codex / other agents, add the trigger block from `prompts/playbook-distill.md` to your system prompt for the same behavior, or invoke the prompt explicitly.

**No Readwise required. No cron required. Just the prompt.**

### Mode 2 — Readwise auto-processing (optional)

If you use Readwise to capture article and book highlights into your Obsidian vault, there's a daily cron that processes new files through the same playbook system at 7:30 AM. Skip this entirely if you don't use Readwise.

## What's in this repo

```
note-highlight-indexer/
├── README.md                       ← this file
├── LICENSE                         ← MIT
├── architecture.md                 ← visual flow + components
├── setup-guide.md                  ← install (Claude Code + Codex paths)
├── prompts/                        ← TOOL-AGNOSTIC PROMPT BODIES (paste into any agent)
│   ├── playbook-distill.md         ← primary prompt: paste content → distill into playbook
│   └── auto-playbook-distill.md    ← headless variant for cron use
├── skills/                         ← Claude Code installable form (YAML frontmatter)
│   ├── playbook-distill.md         ← copy to ~/.claude/skills/playbook-distill/SKILL.md
│   └── auto-playbook-distill.md    ← copy to ~/.claude/skills/auto-playbook-distill/SKILL.md
├── cron/                           ← optional: Readwise auto-processing
│   ├── auto-distill-readwise.sh    ← supports any CLI agent (CLI_BIN configurable)
│   └── com.user.auto-distill.plist
├── vault-templates/
│   ├── Playbooks-Index.md          ← the 10-domain routing table (drop in vault root)
│   └── playbook-readme-template.md ← structure for each playbook's README
└── examples/
    ├── example-paste-in.md             ← primary example: full paste-in session
    ├── example-routing-decision.md     ← step-by-step walkthrough of internals
    ├── example-input-article.md        ← (Readwise mode) raw highlights file
    └── example-output-playbook.md      ← what the distiller produces
```

## Why this works

Three load-bearing claims:

1. **Notes are useless until operationalized.** A quote isn't a rule. The distill step is what makes the corpus actionable.
2. **One synthesized knowledge per dimension beats 50 separate notes.** The skill enforces "merge into existing topic, don't append a new file." After 6 months you have crystallized rules per domain instead of a graveyard.
3. **Filesystem + grep beats specialized memory tools.** Plain Markdown files. No vector store. No graph DB. Any agent can read it. ([Letta's 2026 benchmark](https://www.letta.com/blog/benchmarking-ai-agent-memory) and [Anthropic's managed-agents post](https://www.anthropic.com/engineering/managed-agents) both confirmed this is the right architecture for AI memory.)

## Read next

- **[setup-guide.md](setup-guide.md)** — install instructions, organized into 4 install layers (manual + routing index → optional headless skill → optional cron). **If you're an agent installing on a user's behalf, read the "Pre-flight checklist" section first** — it lists the questions you should ask before making vault-shaping decisions.
- **[architecture.md](architecture.md)** — diagrams and component table
- **[examples/example-paste-in.md](examples/example-paste-in.md)** — full end-to-end paste-in session
- **[examples/example-routing-decision.md](examples/example-routing-decision.md)** — step-by-step skill internals

## Prerequisites

**Manual mode (most people):**
- A coding agent that accepts markdown prompts — [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Codex CLI](https://github.com/openai/codex), Codex web, Cursor, Aider, etc.
- A folder of markdown files you treat as your "second brain" (Obsidian vault, plain folder, anything)

**Optional Readwise mode (additional):**
- Readwise account with the "Sync Highlights to Obsidian" integration
- macOS (for launchd; Linux: substitute systemd or cron)
- Python 3 (ships with macOS)
- A headless-capable agent (Claude Code, Codex CLI, etc.)

## Status

Single-user system. Running in production on a personal machine since early May 2026. Plain Markdown files; no remote storage; no auth; no multi-tenant. That's the point.

Issues, ideas, or improvements: open a GitHub issue or PR.

## License

MIT — see [LICENSE](LICENSE). Use it, fork it, modify it. Attribution appreciated but not required.
