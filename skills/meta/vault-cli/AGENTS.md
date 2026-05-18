# AGENTS.md — `vault-cli`

Operating protocol for agents using or installing this CLI.

## What this repo provides

A Node.js CLI binary (`vault`) that exposes deterministic primitives every Claude Code skill in this ecosystem can call. Skills do *judgment*; the CLI does *glue, math, and file I/O*.

## Inspiration

Architecturally inspired by [Garry Tan's `gbrain`](https://github.com/garrytan/gbrain) — specifically the "thin harness, fat skills" ethos, the skillify pipeline pattern, the `AGENTS.md` + `llms.txt` convention, and JSON-on-non-TTY output. Independent code (pure Node.js vs. gbrain's TS+Bun+PGLite+graph stack), different scope (vault primitives vs. general agent brain). See README's Credits section.

## Read order

1. `README.md` — full architecture, install, what v0.1 ships vs. what v0.2+ will add, migration plan.
2. `package.json` — entrypoint and Node version requirement.
3. `src/cli.js` — top-level dispatcher.
4. `src/commands/*.js` — one file per command group (distill, resurface, session, voice-memo, router, frontmatter, learnings, skill, state).
5. `src/lib/config.js` — operator-specific path resolution (env vars).

## Trust boundary

- The CLI assumes the [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) memory layout (MEMORY.md as index, individual memory files, `_learnings.md` per venture/engagement folder).
- The CLI assumes the [`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions) frontmatter schema.
- The CLI assumes hook scripts at `~/.claude/hooks/{auto-distill-readwise,learnings-resurface,archive-session}.sh` — `vault distill run`, `vault resurface run`, `vault session archive` wrap them. If those scripts are absent, those wrapped commands fail; native commands (`router`, `frontmatter`, `learnings`, `skill`, `state`) work regardless.
- **Append-only is enforced** for `vault learnings *` commands. The CLI never rewrites or deletes existing entries in `_learnings.md`. Do not bypass this.
- **Atomic state writes** — state-file mutations write to a temp file and rename. Don't manually edit a state file while the CLI might be running.

## Install

```bash
git clone https://github.com/derekcedarbaum2/vault-cli.git
cd vault-cli
npm link
vault --version
```

If the operator's vault path differs from the default:

```bash
export VAULT_PATH=/path/to/operator/vault
export VAULT_MEMORY_DIR=/path/to/operator/.claude/projects/<id>/memory
```

## Adaptation checklist

- [ ] Operator has Node.js 22+ installed.
- [ ] Operator's `VAULT_PATH` is set or the default applies.
- [ ] Operator has `MEMORY.md` at the resolved path (run `vault router list` to verify).
- [ ] Operator's existing hook scripts (`auto-distill-readwise.sh`, etc.) are at `~/.claude/hooks/` — required only for the wrapped commands.
- [ ] First write commands run with `--dry-run` where supported.

## Common tasks

| Task | Command |
|---|---|
| Validate Knowledge Router pointers | `vault router check` |
| Find a `_learnings.md` for a topic | `vault router lookup "<topic>"` |
| Audit frontmatter across the vault | `vault frontmatter audit` |
| Backfill frontmatter on one file | `vault frontmatter add <path>` |
| Append a learning to a venture | `vault learnings append "Ideas/Bastion" "Detector for X..."` |
| Scaffold a new skill | `vault skill new <name> --description "..."` |
| Check a skill against the conformance standard | `vault skill check <name>` |
| List installed skills | `vault skill list` |
| Inspect a state file | `vault state get <name>` |
| Run the daily distill cycle | `vault distill run` |
| Run a resurface dry-run | `vault resurface run --dry-run --window 30` |
| Read current ephemeral state (Today.md) | `vault today read` |
| Check if Today.md is stale | `vault today stale --max 6` |
| Regenerate Today.md | `vault today regenerate` |

## Output convention

- Most commands emit JSON when `--json` is passed OR when stdout is non-TTY (gh CLI convention). This means agents calling `vault X` from a subagent get clean parseable output without setting any flag.
- Human-friendly output is short, grep-friendly, no tables.
- Errors go to stderr prefixed with `[vault] ERROR:`. Exit codes: 0 = success, 1 = error or validation failure.

## Calling the CLI from a skill

Within a SKILL.md, prefer:

```bash
vault skill new my-new-skill --description "..."
```

Over:

```bash
mkdir ~/.claude/skills/my-new-skill && \
mkdir -p ~/.claude/skills/my-new-skill/{examples/good,examples/bad,prompts,reference,templates} && \
echo "---..." > ~/.claude/skills/my-new-skill/SKILL.md && ...
```

The CLI version is one line, atomically scaffolds the conformant structure, and always uses the standard. The bash version is repetitive and drift-prone.

## Related repos

- [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system)
- [`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions)
- [`learnings-resurface`](https://github.com/derekcedarbaum2/learnings-resurface)
- [`note-highlight-indexer`](https://github.com/derekcedarbaum2/note-highlight-indexer)
- [`agentic-architecture-map`](https://github.com/derekcedarbaum2/agentic-architecture-map)
