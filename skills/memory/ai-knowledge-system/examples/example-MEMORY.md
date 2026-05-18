# Memory

> Sanitized example from a working installation. Project keys, vault paths, field IDs, and people names are illustrative — replace with your own.

## Active Initiatives
- [Q2 PRD Refresh](project_q2_prd.md) — rewriting Product A PRD after stakeholder review
- [Vendor Eval](project_vendor_eval.md) — comparing three options through end of May
- [Onboarding Doc](project_onboarding.md) — capturing tribal knowledge for a new hire

## Vault Navigation
- **Vault root:** `~/Documents/work-vault/`
- Session archives live in `CC Chat History/`
- When pointed at a new vault area, update `vault-map.md` incrementally

## People & Callsigns
- "Mac" → MacKenzie Reyes (PM peer); not "Mack"
- "GH" → Glenn Halverson (engineering lead)

## Tool & API Gotchas
- Jira v2 `/rest/api/3/search` is removed — use `/rest/api/3/search/jql`
- Jira PUT returns 204 — don't parse response body as JSON
- Confluence `wiki` representation mangles markdown — must use `storage` with HTML
- Confluence `update_page` orphans inline comments if the page has any — run `get_comments` first; use storage-format surgical replacement on pages with `"location": "inline"` markers
- Project keys: PROJ1 (Planning workstream), PROJ2 (Execution), PROJ3 (Bug intake)
- Custom field IDs: Severity=10067, Test Type=10320, Planned Date=11534

## Cost & Performance
- Cached tokens read at $0.50/MTok vs $5/MTok fresh — ~10× savings (Claude Code)
- Tier-1 (CLAUDE.md/AGENTS.md) + tier-2 (MEMORY.md) load into every call. Trim impact compounds.
- For 100+ Jira ops on Claude Code: delegate to a cheaper-model subagent — typical 50–60% savings vs. running everything on the top-tier model

## Workflow Patterns
- Claude Code: `claude -c -p "/skill-name"` continues last session non-interactively
- Plan mode propagates to subagents — finish ExitPlanMode before delegating
- Codex: keep `AGENTS.md` under ~10K tokens; split rarely-used sections into companion files

## Knowledge Router
When starting deep work, read the `_learnings.md` in the matching vault folder. The **Reviewed** column shows last human-affirmed accuracy — re-review if older than 60 days.

| Task pattern | File (relative to vault root) | Reviewed |
|---|---|---|
| Product A (PRD, scenarios, board) | `Products/Product A/_learnings.md` | 2026-04-21 |
| Product B (rendering, networking) | `Products/Product B/_learnings.md` | 2026-04-21 |
| Agent toolkit, Jira API, automation | `Toolkit/_learnings.md` | 2026-04-21 |
| PM methodology, QA loops, ROI | `Toolkit/PM Methodology/_learnings.md` | 2026-04-21 |
| Market and competitor research | `Research/_learnings.md` | 2026-04-21 |
