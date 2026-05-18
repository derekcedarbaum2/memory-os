# Setup — Codex CLI (manual)

30-minute manual setup for Codex CLI users. For the conceptual overview, see [README.md](README.md). For agent-driven install, see [INSTALL-PROMPT.md](INSTALL-PROMPT.md).

> **Honest framing.** This system was built on Claude Code first and ports to Codex with one-time wiring. The three-tier model and the two-operation loop (archive + distill) port directly. Some plumbing — context loading, skill invocation, transcript storage — differs and this guide handles each gap explicitly.

---

## What's different on Codex

| Concern | Claude Code | Codex CLI |
|---------|-------------|-----------|
| Project context auto-load | `~/.claude/CLAUDE.md` (global) + per-project `CLAUDE.md` | `AGENTS.md` at project root (no global equivalent) |
| Auto-memory directory | `~/.claude/projects/-<dir>/memory/MEMORY.md` | None native — fold into `AGENTS.md` or a pre-prompt |
| Skill loader | `~/.claude/skills/<name>/SKILL.md` with frontmatter | None — use prompt templates, shell wrappers, or in-session paste |
| Slash commands | `/archive-session`, `/distill` | None native — invoke via wrapper script or pasted prompt |
| Session transcript | `~/.claude/projects/-<dir>/<session-id>.jsonl` | Codex-specific path; schema differs |
| Hook surface (SessionEnd, etc.) | Native | Different mechanism |

The `_learnings.md` files, the four-section structure, and the Knowledge Router table are all platform-neutral and work as-is.

---

## 1. Decide where global rules live

Codex auto-loads `AGENTS.md` from the project root. There is no global equivalent of `~/.claude/CLAUDE.md`. Two viable patterns:

- **Per-project `AGENTS.md`** — duplicate global rules into each project. Simple, but drifts.
- **Symlinked `AGENTS.md`** — keep the canonical file at `~/.codex/AGENTS-global.md` and symlink it from each project root. Single source of truth.

For most users, the symlink pattern is worth the 5 minutes of setup. Add to your shell profile:

```bash
codex-init() {
  ln -s ~/.codex/AGENTS-global.md ./AGENTS.md
}
```

## 2. Pick a vault location

Same as Claude Code. You need a folder for session archives and domain `_learnings.md` files. Any synced markdown folder works — OneDrive, Dropbox, git repo, Obsidian vault.

Recommended structure:

```
YourVault/
├── Codex Chat History/       ← session archives land here
└── <Domain folders>/
    └── _learnings.md
```

## 3. Define your Knowledge Router

Identical to Claude Code. Build a small table mapping work topics to domain files. Drop it into your `AGENTS.md` (the file Codex auto-loads).

```markdown
## Knowledge Router

| Task pattern | File (relative to vault) |
|---|---|
| Product A | Products/Product A/_learnings.md |
| Methodology | Methodology/_learnings.md |
| Toolkit | Toolkit/_learnings.md |
```

## 4. Seed the templates

- Copy `templates/MEMORY.template.md` content directly into your `AGENTS.md` under a "Memory" heading. (Codex has no auto-memory loader, so the tier-2 content rides along with tier 1.)
- For each domain in your Router, copy `templates/_learnings.template.md` to the matching vault path.

If your `AGENTS.md` grows past ~500 lines, split rarely-used sections into companion files (e.g., `AGENTS-jira-fields.md`) and reference them by path so Codex pulls them on demand instead of every call.

## 5. Port the two skills

The `SKILL.md` files in `skills/` were authored for Claude Code's skill loader. Codex doesn't have an equivalent. Three port options, in order of effort:

### Option A — Pasted prompt (fastest, ~10 min)

Convert each `SKILL.md` body into a single prompt template. Save as `~/.codex/prompts/archive-session.md` and `~/.codex/prompts/distill.md`. To invoke, paste the file content into a Codex session at the right moment.

```bash
alias codex-archive='cat ~/.codex/prompts/archive-session.md | pbcopy && echo "Prompt copied — paste into Codex"'
```

Trade-off: manual paste each time. No automation.

### Option B — Wrapper script (medium, ~1 hr per skill)

Write a shell script that:
1. Locates the current Codex session transcript
2. Builds the right prompt with the transcript inlined
3. Pipes it back into `codex` as a follow-up turn

```bash
#!/bin/bash
# ~/.codex/bin/codex-archive
TRANSCRIPT=$(find ~/.codex -name "*.jsonl" -type f | sort -r | head -1)
PROMPT=$(cat ~/.codex/prompts/archive-session.md)
echo "$PROMPT" | codex --resume --transcript "$TRANSCRIPT"
```

You'll need to discover Codex's actual transcript path and JSON schema first — these can change between Codex versions. Run a session, then `find ~ -name "*.jsonl" -newer /tmp/marker -type f` to locate the active transcript.

Trade-off: real automation, but version-fragile.

### Option C — Native Codex tool (longest, ~half day per skill)

If your Codex version supports custom tools or extensions, register `archive-session` and `distill` as proper tools. Best long-term answer; only worth the time if you'll run this for many months.

## 6. Wire the transcript reader

`archive-session` Step 2 reads the session transcript as `.jsonl` and parses Claude Code's specific schema. For Codex:

1. Find Codex's transcript directory (varies by Codex version — check `~/.codex/`, `~/Library/Application Support/codex/`, or wherever your Codex install logs sessions).
2. Open one transcript and document its schema. Look for: turn boundaries, role markers, tool-use blocks, timestamps.
3. Rewrite Step 2 of `archive-session` to match. The downstream metadata extraction (Steps 3–5) is schema-agnostic and ports as-is.

If Codex doesn't persist transcripts in a readable format, fall back to "manual archive" mode — paste the conversation into the prompt and let Codex extract from what's in context.

## 7. Test it

Start a Codex session in a project that has `AGENTS.md` wired up. Make a decision or learn a tool quirk. Invoke your archive prompt (Option A/B/C from Step 5). The output should be a markdown file matching the four-section structure, ready to drop into the right `_learnings.md`.

After a few sessions, invoke distill the same way.

---

## Day-to-day usage

Identical to Claude Code, with platform-specific invocation:

| Trigger | Operation | Claude Code | Codex |
|---------|-----------|-------------|-------|
| End of a meaningful session | Archive | `/archive-session` | Pasted prompt or `codex-archive` script |
| Every 2–4 weeks | Distill | `/distill` | Pasted prompt or `codex-distill` script |
| Anytime | Read context | Auto from `CLAUDE.md` + `MEMORY.md` | Auto from `AGENTS.md` |

---

## What you give up vs. Claude Code

- **No automatic transcript capture.** Claude Code's `SessionEnd` hook can write a raw archive even if the user forgets to run the skill. On Codex you depend on user discipline or a custom hook equivalent.
- **No auto-memory tier.** Tier 2 collapses into tier 1 (`AGENTS.md`). Watch the file size — past ~10K tokens you're paying for the same context every call.
- **Slash command UX.** Pasting a prompt or running a script is more friction than typing `/distill`. Worth investing in Option C (native tool) once you're sure you'll keep using the system.

---

## What you keep

The whole conceptual loop. Per-domain `_learnings.md` files, the four-section structure, the Knowledge Router, the dedupe and open-thread-resolution logic, the per-session frontmatter — all platform-neutral. The Claude-Code-authored `SKILL.md` files in this package serve as design references; the Codex implementation is whatever wrapper or script you build around the same logic.
