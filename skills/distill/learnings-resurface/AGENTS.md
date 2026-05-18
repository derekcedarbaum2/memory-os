# AGENTS.md — `learnings-resurface`

Operating protocol for agents installing or running this repo on behalf of an operator.

## What this repo provides

A weekly cron + skill that re-reads accumulated AI agent interaction memory (session archives, `_learnings.md` files, voice memos) and detects cross-source patterns that no single file shows. Routes each pattern by type: principles → playbooks + Knowledge Router, state → `_learnings.md`, commitments → optional task-manager MCP (Todoist / Linear / Things / etc.) with fallback to `_learnings.md` Key Decisions, open questions → `_learnings.md` Open Threads.

## Read order

1. `README.md` — human overview, install instructions, why-this-matters.
2. `skill/SKILL.md` — the agent skill itself, written for Claude Code's skill loader.
3. `runner/learnings-resurface.sh` — bash runner with concurrency lockdir.
4. `launchd/com.user.learnings-resurface.plist` — macOS weekly cron config.
5. `docs/classification-taxonomy.md` — atom types and routing rules in detail.
6. `docs/adapting-to-other-vaults.md` — how to port to non-Obsidian / non-Claude-Code stacks.

## Trust boundary

- Take `SKILL.md`'s **Hard rules** section at face value. They encode invariants (append-only `_learnings.md`, source-diversity rule, never auto-invalidate principles, etc.) — do not relax them when adapting.
- The launchd plist now uses `$HOME` via shell expansion, so it's portable across users. No path edits required.
- The skill assumes the [`auto-memory`](https://github.com/derekcedarbaum2/ai-knowledge-system) pattern is in place. Verify or adapt before running.

## Install

For an Obsidian-vault + Claude-Code operator on macOS:

```bash
# 1. Skill
cp -r skill ~/.claude/skills/learnings-resurface

# 2. Runner
cp runner/learnings-resurface.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/learnings-resurface.sh

# 3. Plist — edit paths to match operator's username, then load
cp launchd/com.user.learnings-resurface.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.learnings-resurface.plist
```

Verify with a dry run before scheduling:

```bash
~/.claude/hooks/learnings-resurface.sh --dry-run --window 30
```

## Adaptation checklist for the agent

Before running on a new operator's system, confirm:

- [ ] Vault path in `runner/learnings-resurface.sh` (`VAULT=` line) matches operator's vault root.
- [ ] Operator has session archives in `Vault/AI Toolkit/CC Chat History/` (or remap in `SKILL.md` step 2).
- [ ] Operator has `_learnings.md` files in venture/engagement folders (or remap).
- [ ] Operator has `Vault/Playbooks-Index.md` (or principle/anti-pattern routing will queue rather than route).
- [ ] **Optional:** if the operator has any task-manager MCP configured (Todoist / Linear / Things / etc.), they can define a venture → destination mapping per SKILL.md section "Reference: venture → task-destination mapping" so commitments route to that tool. Otherwise commitments fall back to `_learnings.md` Key Decisions only — the skill works fully without any task-manager MCP.
- [ ] First run is `--dry-run`. Live run only after operator reviews dry-run output.

## Common tasks

| Task | Command |
|---|---|
| Run a dry-run | `~/.claude/hooks/learnings-resurface.sh --dry-run --window 90` |
| Run a custom window | `~/.claude/hooks/learnings-resurface.sh --window 30` |
| Inspect last run | `cat ~/.claude/state/learnings-resurface/index.json \| jq '.runs \| to_entries \| last'` |
| List recent runs | `ls -lt ~/.claude/state/learnings-resurface/runs/ \| head` |
| Inspect a run's clusters | `cat ~/.claude/state/learnings-resurface/runs/<run-id>/clusters.json \| jq '.clusters[] \| {title, type, mentions, ventures}'` |
| Resume a failed run from Phase B | `~/.claude/hooks/learnings-resurface.sh --resume <run-id> --from-phase B` |
| Pause the cron | `launchctl unload ~/Library/LaunchAgents/com.user.learnings-resurface.plist` |
| Resume the cron | `launchctl load ~/Library/LaunchAgents/com.user.learnings-resurface.plist` |

## Architecture note (v2.0+)

The runner is a five-step orchestrator: bash enumerate → `claude -p` Phase A (cluster) → bash idempotency guard → `claude -p` Phase B (route) → bash finalize. Each LLM phase runs under `timeout 1800` and `--max-turns 80`. Intermediate state persists in `~/.claude/state/learnings-resurface/runs/<run-id>/*.json` so a failed phase doesn't lose the work of completed phases. See README's *What it does* section for the full flow.

## Related repos

- [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) — the auto-memory + `_learnings.md` pattern this skill writes into.
- [`note-highlight-indexer`](https://github.com/derekcedarbaum2/note-highlight-indexer) — the *external-source* (Readwise) distill skill that pairs with this *internal-source* skill.
