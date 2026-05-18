# Memory

> Tier-2 operational memory. Loaded on every agent call (Claude Code: auto-loaded from `~/.claude/projects/-<dir>/memory/MEMORY.md`; Codex: paste contents into the `## Memory` section of `AGENTS.md`).

## Active Initiatives
- [Initiative name](project_initiative_slug.md) — one-line description of what's in flight

## Vault Navigation
- **Vault root:** `<VAULT_ROOT>` (absolute path to your vault)
- Session archives live in `CC Chat History/`
- Per-domain `_learnings.md` files routed via the Knowledge Router below

## People & Callsigns
- Add nicknames, callsign shortenings, or naming preferences the agent should use

## Tool & API Gotchas
- Add operational rules that break tools if violated. Examples:
  - "Tool X v3 endpoint /foo is deprecated — use /bar"
  - "API field 11534 is Planned UAT Date (custom field)"
  - "Project keys: PROJ1 (X workstream), PROJ2 (Y workstream)"

## Cost & Performance
- Pricing notes, cache behavior, model routing rules

## Workflow Patterns
- Cross-cutting "how I work" notes that don't fit other sections

## Knowledge Router
When starting deep work, read the `_learnings.md` in the matching vault folder.

| Task pattern | File (relative to vault root) | Reviewed |
|---|---|---|
| <Domain 1 — describe scope> | <path/to/_learnings.md> | YYYY-MM-DD |
| <Domain 2 — describe scope> | <path/to/_learnings.md> | YYYY-MM-DD |
| <Domain 3 — describe scope> | <path/to/_learnings.md> | YYYY-MM-DD |

---

## Notes for users

- **Claude Code: keep this file under 200 lines** — content past line 200 gets truncated by the loader.
- **Codex: keep the combined `AGENTS.md` under ~10K tokens** — beyond that, you're paying for the same context every call.
- Section headings are flexible. Add/remove to match your work.
- The **Knowledge Router** table is required and is read by `/distill` and `/archive-session`.
- Per-fact memory files (e.g., `feedback_x.md`, `project_y.md`) live alongside this file (Claude Code) and are referenced by `[Title](file.md)` links above.
