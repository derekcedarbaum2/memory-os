# CLAUDE.md trigger

Add this section to your `~/.claude/CLAUDE.md` (the global instructions Claude Code reads on every call). Adjust the path to match where you placed your `agentic-architecture.md` file.

---

## Agentic architecture map (always update on structural change)

The internal map of how the full system is wired (skills, hooks, crons, MCP servers, memory, vault routing, brand) lives at `[path]/agentic-architecture.md`. It includes a snapshot section (rewrite in place) and an append-only **Evolution log**.

**Whenever you make or observe a structural change** to:
- a skill in `~/.claude/skills/` (added, removed, materially rewritten),
- a hook in `~/.claude/hooks/`,
- a launchd plist in `~/Library/LaunchAgents/` (or your cron / systemd equivalent),
- a memory schema or routing protocol (Knowledge Router, MEMORY.md, auto-memory format),
- `~/.claude/settings.json` / `settings.local.json` permissions or hook config,
- an MCP server (added, removed, reconfigured),
- vault routing (new venture folder, new `_learnings.md`, new playbook domain in `[path]/Playbooks-Index.md`, new `_strategy.md`),

→ **append a dated entry to the Evolution log section of `[path]/agentic-architecture.md`** using the template at the bottom of the file. If the snapshot section above the log has gone stale because of the change, also update the relevant snapshot subsection in place.

This is how we track architecture drift and surface optimization opportunities over time. Don't skip it for "small" structural changes — those are exactly the ones that compound and get lost.
