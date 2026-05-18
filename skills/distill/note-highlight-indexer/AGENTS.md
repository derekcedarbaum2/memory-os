# AGENTS.md — `note-highlight-indexer`

Operating protocol for agents installing this for an operator.

## What this repo provides

A daily cron + skill that reads Readwise-synced highlights (articles, books, tweets) and distills them into operational format inside cross-vault playbook files (scorecards, decision triggers, anti-pattern detectors, fillable templates). Sources are routed across a 10-domain playbook taxonomy. Plain Markdown, no vector DB.

## Read order

1. `README.md` — human overview, value proposition, what this is not.
2. `architecture.md` — the 10-domain playbook taxonomy, the routing logic, the merge format.
3. `setup-guide.md` — step-by-step install for Obsidian + Claude Code on macOS.
4. `skills/auto-playbook-distill/SKILL.md` — the headless / cron-driven skill.
5. `skills/playbook-distill/SKILL.md` — the interactive variant.
6. `cron/auto-distill-readwise.sh` — bash runner with concurrency lockdir.
7. `vault-templates/` — starter playbook structure (Playbooks-Index.md + topic file format).
8. `prompts/` — supporting prompts.
9. `examples/` — sanitized examples of distilled output.

## Trust boundary

- Source quotes must be preserved verbatim or as tight paraphrases (per the two-column merge format). Drift in the source column defeats the audit purpose.
- Never create more than one new playbook in a single run. If a source spans multiple new domains, route to the dominant one and queue the secondary.
- Source-tag every claim inline.
- The 10-domain taxonomy is the routing baseline. Don't add an 11th playbook silently — queue to `_unrouted-distill-queue.md` instead.

## Install

For an Obsidian-vault + Claude-Code operator on macOS with Readwise sync:

```bash
# 1. Skill (both variants — headless cron + interactive)
cp -r skills/auto-playbook-distill ~/.claude/skills/
cp -r skills/playbook-distill ~/.claude/skills/

# 2. Cron runner
cp cron/auto-distill-readwise.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/auto-distill-readwise.sh

# 3. Vault scaffolding (if operator doesn't have a Playbooks-Index.md yet)
cp vault-templates/Playbooks-Index.md <operator-vault>/

# 4. Schedule the cron (see setup-guide.md for launchd plist)
```

## Adaptation checklist

- [ ] Operator has Readwise sync writing to `Vault/Reading/{Articles,Books,Tweets}/` (or remap).
- [ ] Operator has `Vault/Playbooks-Index.md` (or copy from `vault-templates/`).
- [ ] State file location at `~/.claude/state/distilled-readwise.json` is writable.
- [ ] Cron runs at 7:30 AM PT (or operator's preferred quiet window).
- [ ] First run is `--backfill --dry-run` to see what would be distilled.

## Common tasks

| Task | Command |
|---|---|
| Daily auto-distill (cron-driven) | runs automatically at 7:30 AM PT |
| Manual backfill | `~/.claude/hooks/auto-distill-readwise.sh --backfill` |
| Dry-run | `~/.claude/hooks/auto-distill-readwise.sh --dry-run` |
| Manual interactive distill (paste content) | invoke `/playbook-distill` skill |

## Related repos

- [`learnings-resurface`](https://github.com/derekcedarbaum2/learnings-resurface) — the *internal-source* counterpart (cross-vault interaction memory). Together they form the distill triad.
- [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) — the memory pattern this skill writes into (Knowledge Router promotion).
- [`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions) — frontmatter and vault structure conventions.
