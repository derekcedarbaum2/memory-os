# Adapting to Other Knowledge Bases

The skill is shaped for an Obsidian vault with venture/engagement folders, each containing a `_learnings.md`, plus session archives in `Vault/AI Toolkit/CC Chat History/`. If your knowledge base is structured differently, here's what to change.

---

## Inputs (what the skill reads)

The skill expects three input streams. Map yours:

| Stream | Default location | What it provides |
|---|---|---|
| Session archives | `Vault/AI Toolkit/CC Chat History/*.md` | Actual interaction history — most weight |
| Curated learnings | `_learnings.md` files across folders | Pre-distilled context per domain |
| Voice memos | `Vault/Voice Memos/*.md` | Inbound thoughts |

**To remap:** edit `SKILL.md` step 2 ("Enumerate interaction-memory corpus") and the corresponding `Glob` paths.

If you don't have a session-archive equivalent, you can run on `_learnings.md` alone — but expect lower recall (curated learnings have already filtered out a lot of pattern signal).

---

## Outputs (what the skill writes)

| Output | Default destination | Required? |
|---|---|---|
| Principle/anti-pattern routing | Playbook topic files via `auto-playbook-distill` skill | Optional — without it, principles queue for manual review |
| Router promotion | `MEMORY.md` index + memory file in `~/.claude/projects/<id>/memory/` | Required if you want cross-session recall |
| State / open questions | `_learnings.md` per venture | Required (this is the per-venture knowledge home) |
| Commitments | Tasks via any task-manager MCP (Todoist, Linear, Things, etc.) | Optional — falls back to `_learnings.md` Key Decisions only if no MCP is available |
| Run log | `Vault/log.md` | Optional — for auditability |
| State directory | `~/.claude/state/learnings-resurface/` (v2.0+) | Required for idempotency. `index.json` at root holds global run history + cluster fingerprints; `runs/<run-id>/` subdirs hold per-run intermediate state (`enumerate.json`, `clusters.json`, `clusters_filtered.json`, `routed.json`) for phase resumability. |

---

## Vault-structure assumptions you can drop

- **Venture folders:** the skill uses parent folder under `Work/`, `Ideas/`, `Professional Development/`, `Company Building/` as the venture context. If your folder taxonomy differs, edit the venture-detection logic in step 3.
- **Knowledge Router:** if you don't have one, drop the Router-promotion step entirely. Principles still distill into playbooks.
- **Playbook domains:** if you don't have a `Playbooks-Index.md`, principles will queue rather than route. You can add `auto-playbook-distill` later — it's a strict superset of the routing this skill needs.

---

## Linux / non-launchd

Replace the launchd plist with cron or systemd:

```cron
# Sundays at 22:00
0 22 * * 0 /home/USER/.claude/hooks/learnings-resurface.sh
```

Or systemd timer:

```
[Timer]
OnCalendar=Sun 22:00
```

The runner script (`runner/learnings-resurface.sh`) is bash and works on Linux. Two paths to update:
- `VAULT="$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"` — point to your vault root
- `CLAUDE_BIN="$HOME/.local/bin/claude"` — confirm your `claude` binary path

---

## Without Claude Code

The skill is written for Claude Code's skill loader (`SKILL.md` with frontmatter, `claude -p` invocation). To port to another agent runner:

1. Treat `SKILL.md` as the system prompt.
2. The runner shells out to `claude -p "<task description>"` — replace with your CLI's equivalent.
3. The skill expects tool access to: `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Bash`. Optional: any task-manager MCP (skill auto-detects whether the relevant MCP tool is in the agent's allowed-tools at runtime; falls back to `_learnings.md` if not).
4. The auto-memory Router and `_learnings.md` patterns are platform-neutral markdown — those don't need to change.

The skill design (taxonomy, source-diversity rule, artifact-type check, contradiction detection) is portable; the runner glue is the only platform-specific layer.
