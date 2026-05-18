# Install Prompt — Agent-Driven Setup

Paste the prompt below into your agent (Claude Code or Codex) from the root of this repo. The agent will interview you, then write the customized files into the right places. Faster than manual find/replace, and the result is shaped to your actual infrastructure.

The prompt assumes the agent has tools to:
- Read this repo's files
- Ask the user clarifying questions interactively (Claude Code: `AskUserQuestion`; Codex: standard interactive prompts; any agent: emit one question at a time and wait for a reply)
- Write files to the user's filesystem

If your agent lacks any of these, fall back to the manual setup ([setup-claude-code.md](setup-claude-code.md) or [setup-codex.md](setup-codex.md)).

---

## Paste this into your agent

> You are installing the **AI Knowledge System** for the user. The repo is in your current working directory. Read these files first to understand the system you're installing:
>
> - `README.md` (overview + tier model)
> - `setup-claude-code.md` and `setup-codex.md` (platform wiring)
> - `templates/MEMORY.template.md` and `templates/_learnings.template.md` (the files you'll customize)
> - `examples/example-MEMORY.md` and `examples/example-_learnings.md` (what good looks like)
>
> Then drive the install **interactively** using your question tool. Ask one question (or one tight batch) at a time and wait for the user's answer before continuing. Do not write any files until Step 6 below.
>
> ### Step 1 — Detect platform
>
> Determine whether you are Claude Code or Codex. If you're Claude Code, look for `~/.claude/` and confirm it exists. If you're Codex, look for `~/.codex/` and confirm. If unclear, ask the user which agent they're running you in.
>
> ### Step 2 — Ask the user for their setup
>
> Use your question tool to gather the following. Use multi-select where the answer space is bounded; otherwise free-text. Batch related questions when natural.
>
> 1. **Vault location.** Where do they want session archives and `_learnings.md` files to live? (Common answers: an Obsidian vault, a OneDrive/Dropbox folder, a plain git repo, a synced iCloud folder.) Get an absolute path.
> 2. **Role.** PM, PM Ops, Technical PM, Product Analyst, Solutions PM, other.
> 3. **Primary products / initiatives** they're working on. 2–5 of them. These become tier-3 domain files.
> 4. **Cross-cutting domains** (methodology, research, toolkit/automation). These also become tier-3 domain files. Optional — skip if user has none.
> 5. **Primary work tools** — multi-select from Jira, Linear, Asana, Notion, Confluence, GitHub Issues, Shortcut, Productboard, other. This determines what tier-2 gotchas to seed.
> 6. **Project keys / workspace IDs** for those tools, if known. (e.g., for Jira: project keys; for Linear: team identifiers; for Notion: workspace name.) Optional — they can fill in later.
> 7. **Naming conventions** — anything the agent should always do or never do (e.g., "always use the callsign 'Mac' for MacKenzie Reyes", "never auto-commit", "always confirm before sending Slack messages"). Optional.
> 8. **Active initiatives** — 1–3 in-flight projects with one-line descriptions. These go into `## Active Initiatives` in `MEMORY.md`.
>
> ### Step 3 — Confirm the Knowledge Router
>
> Based on Step 2, draft the Knowledge Router table — a row per domain file. Show the draft to the user and ask: *"Does this routing match how you think about your work?"* Iterate until they say yes.
>
> Each row maps a task pattern (free-text matcher the agent uses to detect topic) to a `_learnings.md` path inside the vault. Default folder names: `Products/<product>/`, `Methodology/`, `Research/`, `Toolkit/` — but use the user's actual vocabulary from Step 2.
>
> ### Step 4 — Detect target paths
>
> Compute the install paths based on the platform detected in Step 1.
>
> **Claude Code:**
> - Global rules: `~/.claude/CLAUDE.md` (modify in place — append the Knowledge System pointer block, do not overwrite existing content)
> - Auto-memory: `~/.claude/projects/-<sanitized-cwd-or-username>/memory/MEMORY.md` (create from `templates/MEMORY.template.md`)
> - Skills: `~/.claude/skills/archive-session/SKILL.md` and `~/.claude/skills/distill/SKILL.md` (copy from this repo)
> - Vault path: from Step 2
>
> **Codex:**
> - Global rules: `~/.codex/AGENTS-global.md` plus a symlink `./AGENTS.md` from each project root, OR a per-project `AGENTS.md` (ask the user which pattern they prefer per `setup-codex.md`)
> - Tier-2 content: appended into `AGENTS.md` under a `## Memory` heading (Codex has no auto-memory loader)
> - Skills: skipped — Codex doesn't have a skill loader. Save `archive-session/SKILL.md` and `distill/SKILL.md` as design references at `~/.codex/prompts/archive-session.md` and `~/.codex/prompts/distill.md` per `setup-codex.md` Option A.
> - Vault path: from Step 2
>
> ### Step 5 — Substitute placeholders
>
> In all files about to be written, replace these placeholders with values from Steps 2–4:
>
> - `<VAULT_ROOT>` → absolute vault path from Step 2
> - `<USER_ROLE>` → role from Step 2
> - `<DOMAIN_FILES>` → Knowledge Router rows from Step 3
> - `<ACTIVE_INITIATIVES>` → from Step 2
> - `<PEOPLE_AND_CALLSIGNS>` → from Step 2 (or empty section if user gave none)
> - `<TOOL_GOTCHAS>` → seed entries based on tools selected in Step 2 (use examples from `examples/example-MEMORY.md` as starters; flag them as "<verify before relying on>" so the user knows to confirm against their actual environment)
>
> The `SKILL.md` files contain `<VAULT_ROOT>` and a few path placeholders — substitute and confirm.
>
> ### Step 6 — Show before writing
>
> Show the user the full contents of every file you're about to create (or every block you're about to append). Use diffs or compact summaries for files over 100 lines.
>
> Ask: *"Write all of this to disk?"* with options Yes / Edit first / Cancel. Do not write until they confirm.
>
> ### Step 7 — Write
>
> Create all files. For files that exist (`~/.claude/CLAUDE.md` typically does), append the new content under a clearly delimited section like:
>
> ```
> <!-- AI Knowledge System — installed YYYY-MM-DD -->
> ## Knowledge System
> ...content...
> <!-- /AI Knowledge System -->
> ```
>
> So the user can find and remove it cleanly later.
>
> ### Step 8 — Verify
>
> After writing, do a quick sanity pass:
> - Read each created file and confirm placeholders are gone (search for `<VAULT_ROOT>`, `<` in general)
> - Confirm the Knowledge Router in `MEMORY.md` references files at paths that exist (or that you just created stubs for)
> - Confirm the skills in `~/.claude/skills/` are loadable (Claude Code only — check frontmatter is intact)
>
> Report any issues. Don't pretend success.
>
> ### Step 9 — Hand off
>
> Tell the user:
>
> - Their tier-1 file (CLAUDE.md or AGENTS.md) location and what was added
> - Their tier-2 MEMORY location
> - Their tier-3 stub `_learnings.md` files (paths, one per domain in the Router)
> - How to invoke `/archive-session` and `/distill` on their platform
> - The "First Two Weeks" advice: actively capture every correction the user makes. After two weeks, the system runs on momentum.
>
> Do NOT auto-commit anything to git. Do NOT push anything. Do NOT send any messages. Setup ends at "files written + sanity-checked."

---

## What the agent should NOT do

- Do not assume defaults for vault path, products, or role. **Always ask.**
- Do not skip Step 6 (show before writing). The user wants to see the customization before it lands on disk.
- Do not invent tool gotchas you can't ground in the user's actual stack. If they didn't pick Jira, don't seed Jira gotchas.
- Do not promote anything from `examples/` verbatim. Examples are illustrative, not user-specific.

---

## When to fall back to manual setup

Use the manual guides ([setup-claude-code.md](setup-claude-code.md), [setup-codex.md](setup-codex.md)) if:

- Your agent doesn't have a question tool
- You want to read the system end-to-end before installing
- You're customizing heavily and the interview flow gets in the way
- You're installing across many projects and want to template the install yourself
