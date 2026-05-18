# AGENTS.md — `vault-lint`

Operating protocol for agents installing this for an operator.

## What this repo provides

A weekly vault hygiene scan for Markdown knowledge bases. Audits for broken wikilinks, missing/malformed frontmatter, orphan pages, stale `_learnings.md` files, duplicate concepts, and contradictions between domain files. Produces a severity-tagged report. Read-only by default. Plain Markdown, no DB.

## Read order

1. `README.md` — what gets audited, what severity tags mean, how to interpret the report.
2. `SKILL.md` — the skill itself.
3. `launchd/` — periodic cron config (macOS).
4. `examples/` — sanitized example reports.

## Trust boundary

- Read-only by default. The skill audits and reports; it does not auto-fix.
- Severity tags: `critical` (broken wikilinks, contradictions), `high` (missing frontmatter on active files), `medium` (orphans, stale `_learnings.md`), `low` (style nits). Trust the tags; review the underlying findings before action.
- Auto-fix mode (when implemented) requires explicit operator authorization per finding.

## Install

```bash
# 1. Skill
cp -r SKILL.md ~/.claude/skills/vault-lint/

# 2. Periodic cron (macOS launchd)
cp launchd/com.user.vault-lint.plist ~/Library/LaunchAgents/
# edit operator's username inside the plist first
launchctl load ~/Library/LaunchAgents/com.user.vault-lint.plist
```

## Adaptation checklist

- [ ] Vault path in skill / plist matches operator's vault root.
- [ ] Operator's frontmatter schema matches what `vault-lint` expects (defaults to the schema in [`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions)).
- [ ] First run is read-only; review report before configuring any auto-fix.

## Common tasks

| Task | Command |
|---|---|
| On-demand audit | `/vault-lint` |
| View last report | `cat ~/.claude/state/vault-lint-report-latest.md` (path may vary per skill version) |
| Pause periodic audit | `launchctl unload ~/Library/LaunchAgents/com.user.vault-lint.plist` |

## Related repos

- [`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions) — the conventions `vault-lint` audits against.
- [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) — the memory pattern these conventions support.
