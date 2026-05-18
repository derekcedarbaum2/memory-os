# Setup — Claude Code (manual)

15-minute manual setup for Claude Code users. For the conceptual overview, see [README.md](README.md). For agent-driven install, see [INSTALL-PROMPT.md](INSTALL-PROMPT.md).

---

## 1. Confirm Claude Code is installed

You need Claude Code with skills enabled (any version supporting `~/.claude/skills/`). If `~/.claude/` doesn't exist yet, run any Claude Code session once to generate it.

## 2. Install the two skills

Copy each skill folder to `~/.claude/skills/`:

```bash
cp -r skills/distill ~/.claude/skills/
cp -r skills/archive-session ~/.claude/skills/
```

Open both `SKILL.md` files and replace `<VAULT_ROOT>` with the absolute path to your vault. The placeholder appears in:
- `archive-session/SKILL.md` — Vault Configuration section
- `distill/SKILL.md` — Target Files section

## 3. Pick a vault location

You need a folder for session archives and domain `_learnings.md` files. Obsidian works well but isn't required — any synced markdown folder is fine (OneDrive, Dropbox, plain git repo).

Recommended structure:

```
YourVault/
├── CC Chat History/          ← session archives land here
└── <Domain folders>/
    └── _learnings.md         ← one per domain you care about
```

## 4. Define your Knowledge Router

The Router is a small table in `MEMORY.md` that maps work topics to domain files. Start with 2–4 domains — you can always add more.

Example for a PM working on two products plus methodology:

```markdown
| Task pattern | File (relative to vault) |
|---|---|
| Product A (PRD, scenarios, board) | Products/Product A/_learnings.md |
| Product B (any work) | Products/Product B/_learnings.md |
| PM methodology, QA loops, ROI | Methodology/_learnings.md |
| API/automation/tooling gotchas | Toolkit/_learnings.md |
```

Both skills read this Router from `MEMORY.md` to decide where new content goes.

## 5. Seed the templates

Copy `templates/MEMORY.template.md` to `~/.claude/projects/-<your-username>/memory/MEMORY.md`. Fill in your Knowledge Router, your tooling gotchas, your active initiatives.

For each domain in your Router, copy `templates/_learnings.template.md` to the matching vault path. The skills will populate them as you work.

## 6. Add tier-1 pointers in `~/.claude/CLAUDE.md`

Add a short section so Claude knows to consult the system:

```markdown
## Knowledge System
- **Tier 1 (always loaded):** this file + MEMORY.md
- **Tier 2 (on demand):** _learnings.md per domain — see Knowledge Router in MEMORY.md
- **Vault path:** <YOUR_VAULT_PATH>
```

## 7. Test it

Start a session. Make a decision or learn something non-obvious about a tool. At the end, type `/archive-session`. The skill captures the conversation, routes the learnings, and asks before writing.

After a few sessions, run `/distill` to dedupe and reconcile across them.

---

## Day-to-day usage

| Trigger | Skill | What it does |
|---------|-------|--------------|
| End of a meaningful session | `/archive-session` | Saves transcript + extracts decisions, insights, open threads. Routes new items to the right `_learnings.md`. |
| Every 2–4 weeks, or after a sprint | `/distill` | Rereads all archives. Dedupes, resolves stale open threads, promotes operational rules to `MEMORY.md`. |
| Anytime | (just chat) | Claude reads `CLAUDE.md` + `MEMORY.md` automatically. Pull the relevant `_learnings.md` into context when starting deep work in a domain. |

---

## File locations reference

| File | Path |
|------|------|
| Global rules (tier 1) | `~/.claude/CLAUDE.md` |
| Auto-memory index (tier 2) | `~/.claude/projects/-<dir>/memory/MEMORY.md` |
| Per-fact memory files (tier 2) | `~/.claude/projects/-<dir>/memory/<slug>.md` |
| Domain learnings (tier 3) | `<vault>/<domain>/_learnings.md` |
| Session archives | `<vault>/CC Chat History/<YYYY-MM-DD-slug>.md` |
| Skills | `~/.claude/skills/<skill-name>/SKILL.md` |
| Session transcripts (raw) | `~/.claude/projects/-<dir>/<session-id>.jsonl` |
