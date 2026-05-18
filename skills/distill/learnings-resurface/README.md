# Learnings Resurface

> **Want to install the whole 12-repo ecosystem?** Paste [this prompt](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/INSTALL-PROMPT.md) into your Claude Code or Codex session — it interviews you, installs in phases, runs smoke tests, and pauses for confirmation between phases. Or browse the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) first.


**A weekly job that rereads everything your AI agent has captured and surfaces the patterns no single file shows.**

> **New to Claude Code?** [Claude Code](https://docs.anthropic.com/claude/code) is Anthropic's command-line AI agent. The patterns in this repo assume you're running it (or [Codex CLI](https://github.com/openai/codex)) plus a Markdown knowledge base (Obsidian or similar). See the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md) — full system overview + onboarding sequence — or [`claude-code-setup`](https://github.com/derekcedarbaum2/claude-code-setup) for the umbrella reference doc. Vocabulary used here (skill, vault, `_learnings.md`, etc.) is defined in the [glossary](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/GLOSSARY.md).

---

## The problem

Most AI agent setups capture a lot of stuff. Session transcripts get auto-saved. You write notes after meetings. You record voice memos. The AI dutifully drops them into the right folder.

**Then nobody — including the AI — ever reads them again.**

So patterns that recur three times across two ventures stay invisible. A principle you've stated in four voice memos never gets promoted to durable memory. A commitment you made in a session three weeks ago is forgotten until the deadline hits. The system has the information; it just isn't *connected*.

The fix is a weekly job that *rereads* everything the agent has captured — session transcripts, per-project running notes, voice memos — and looks for patterns across them. When the same idea shows up in multiple places from multiple sources, it gets promoted into something durable. When a one-off observation shows up, it stays where it is. When two ideas contradict, you find out.

---

## How it fits with related repos

This skill is the **third tier-3 maintenance operation** in the [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) memory pattern, alongside two manual ones:

| When | Operation | Trigger |
|---|---|---|
| End of every meaningful chat | `/archive-session` (in `ai-knowledge-system`) — per-session capture | Manual |
| Every 2–4 weeks | `/distill` (in `ai-knowledge-system`) — periodic cross-session reconciliation on a recent window | Manual |
| **Weekly (Sunday 10pm)** | **`learnings-resurface` (this repo)** — cluster + classify across the *whole accumulated corpus*, route per type | **Automated cron** |

The first two run on individual sessions / recent windows. This one runs on the **full corpus the first two build up** — so it adds value only once you've been running them for a few weeks. Without an active `/archive-session` habit, this skill has nothing to chew on.

> ⚠️ **Don't install this first.** The dependency is real. Get [`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) in place, run `/archive-session` after every meaningful chat for ~6 weeks of active use, and *then* install this. The pre-flight check will refuse to run if the corpus is empty.

It's also the third of three "distillation" loops across the broader ecosystem. Each rereads a different kind of input:

| Skill / Repo | Rereads | Source |
|---|---|---|
| [`note-highlight-indexer`](https://github.com/derekcedarbaum2/note-highlight-indexer) | *External* content | Articles, books, tweets you've read (via Readwise) |
| `voice-memo-process` (in `claude-code-setup`) | *Single* voice memos | Daily mobile capture |
| **`learnings-resurface` (this repo)** | *Accumulated internal* interaction memory | Session archives + `_learnings.md` + voice memos, across your whole knowledge base |

---

## What it does (technical detail)

Once a week (Sunday 10pm PT), a launchd cron fires `learnings-resurface.sh`. The runner is a **five-step orchestrator** that decomposes the work into bounded phases — most steps are deterministic bash; only two are LLM calls. Each LLM call runs under `timeout 1800` (30 min wall clock) and `--max-turns 80`, so neither can drag past the API stream's idle tolerance:

```
[bash] enumerate corpus                           → state/runs/<run-id>/enumerate.json
[claude -p, ~10–15 min] Phase A: cluster + classify
                                                    → state/runs/<run-id>/clusters.json
[bash] pre-route guard (idempotency)              → state/runs/<run-id>/clusters_filtered.json
[claude -p, ~10–15 min] Phase B: route + log
                                                    → state/runs/<run-id>/routed.json + actual writes
[bash] finalize: merge run record + fingerprints  → state/index.json + Vault/log.md
```

If Phase A or Phase B fails, intermediate state is preserved on disk and the run can be resumed: `learnings-resurface.sh --resume <run-id> --from-phase <A|B>`. Re-runs of completed phases are skipped via file-presence checks.

### What each step does

1. **Enumerate** *(bash, no LLM)* — finds interaction-memory across the last N days (default 90):
   - Session archives (`Vault/AI Toolkit/CC Chat History/`)
   - All `_learnings.md` files (excluding `Personal/` and employer scope)
   - Voice memos (`Vault/Voice Memos/`)
   - Skips files <500 B (empty scaffolding).

2. **Phase A — Cluster + Classify** *(claude -p)* — extracts atoms (short attributable signal units; each carries source file, date, venture context, speaker/origin, type guess), clusters by semantic similarity, applies the threshold guards:
   - Drop clusters with <3 mentions.
   - Drop clusters with <2 distinct human sources (the **source-diversity rule** — three of your own voice memos saying the same thing is one source, not three).
   - Drop clusters where all sources are within the same week (echo, not pattern).
   - Score by **time-decay weighted recency**: each atom contributes `1 / (1 + days_old / 30)`.
   - **Artifact-type / optimization-target check:** atoms only cluster together if they operate on the *same artifact type* AND the *same optimization target*. Two atoms about "multi-pass QA loops" do not belong in one cluster if one targets marketing copy (optimize for voice/authenticity) and the other targets skill logic (optimize for soundness/gap-detection). Surface similarity is not the bar. When in doubt, split.

   Phase A also detects contradictions for principle/anti-pattern clusters — searches existing memory + corpus for opposing statements. Surfaces contested clusters for review; **never auto-invalidates**. Output is `clusters.json` with each cluster's `fingerprint` (sha256 of normalized title + sorted source paths) and `proposed_destinations` resolved upfront.

3. **Pre-route guard** *(bash, no LLM)* — Python check that drops clusters whose proposed memory file already exists OR whose fingerprint is already in `index.json`'s `cluster_fingerprints` from a prior run (unless mention count grew past a threshold). This is the **destination-as-fingerprint idempotency** that survives Opus non-determinism between dry-runs and live runs. Output is `clusters_filtered.json`.

4. **Phase B — Route + Log** *(claude -p)* — applies the 5-cap, queues surplus to `Vault/raw-sources/_resurface-queue.md`, then routes each cluster by type:

   | Type | Destination |
   |---|---|
   | Principle / Anti-pattern | Distilled into the matching playbook (via `auto-playbook-distill` domain logic). Promoted to the auto-memory Knowledge Router if `mentions ≥3` AND surfaced across `≥2 ventures`. |
   | State | Appended to the relevant venture's `_learnings.md` Learnings section. Not promoted. |
   | Commitment | If the operator has a task-manager MCP configured (Todoist / Linear / Things / etc.) AND a venture → destination mapping defined, a task is created there. Otherwise (and always), a row is appended to the venture's `_learnings.md` Key Decisions table. The skill works fully without any task-manager integration. |
   | Open question | Appended to the venture's `_learnings.md` Open Threads section. |

   Per-cluster + roll-up lines go to `Vault/log.md`. Output is `routed.json`.

5. **Finalize** *(bash, no LLM)* — Python merges the run record and new cluster fingerprints into `index.json`, writes a runner-level marker line to `Vault/log.md`. Closes the run.

### State directory layout

```
~/.claude/state/learnings-resurface/
├── index.json                          ← global state: last_run, runs, cluster_fingerprints
└── runs/
    └── <run-id>/
        ├── enumerate.json              ← bash output
        ├── clusters.json               ← Phase A output
        ├── clusters_filtered.json      ← bash guard output
        └── routed.json                 ← Phase B output
```

This is the *manifest + idempotent fetcher* pattern — the runner is a worked example of the deterministic-vs-judgment architecture rule the skill itself distills (see `working-with-coding-agents.md` *Architecture* section in any vault running this skill).

---

## Why most "memory" systems miss this

Capture is the easy half. Most setups have a hook that writes session transcripts to disk and call it done. That gives you a corpus, not a memory.

The hard half is **reconciliation across the corpus**. Three properties matter:

1. **Cross-source aggregation** — a principle that's appeared once in three different sessions across two ventures is more durable than one stated firmly in a single voice memo. You can't see that without rereading everything.

2. **Source diversity** — your own thinking restated four times is one signal. An LLM watching a single human's voice memos will inflate confidence on whatever that human says repeatedly. The diversity rule is the corrective.

3. **Type-specific routing** — a principle, a state observation, a commitment, and an open question all need different homes. Conflating them is what makes most "second brain" systems collapse into a single undifferentiated bucket.

This skill encodes all three, plus contradiction detection that respects category boundaries.

---

## Hard rules (enforced by the skill)

1. **Never rewrite or delete** content in `_learnings.md` files. Append-only is a vault invariant.
2. **Never edit** `Vault/Reading/` (Readwise overwrites it).
3. **Never edit** `Vault/Personal/`. Personal scope is excluded.
4. **Never include employer source materials** in cross-venture clustering.
5. **Never auto-invalidate a principle.** Contradictions surface for review only.
6. **Never fabricate clusters.** Source-diversity rule applies (≥2 distinct human sources).
7. **Never fabricate quotes.** Reproduce verbatim if quoting.
8. **Never promote silently.** Router promotion requires `mentions ≥3` AND `cross_venture: true`.
9. **Cap: 5 new patterns per run.** Excess queues.
10. **Use absolute paths** for all writes.

---

## What's in this repo

```
learnings-resurface/
├── README.md
├── LICENSE
├── skill/
│   └── SKILL.md                 ← The agent skill (Claude Code format)
├── runner/
│   └── learnings-resurface.sh   ← Bash runner with concurrency lockdir
├── launchd/
│   └── com.user.learnings-resurface.plist  ← macOS weekly cron config
└── docs/
    ├── classification-taxonomy.md  ← Atom types + routing rules in detail
    └── adapting-to-other-vaults.md ← Notes for other knowledge-base layouts
```

---

## Prerequisites

> **If you got here directly:** this skill is **step 11** in a multi-skill setup, not a one-shot install. It's a *cross-source pattern detector* that runs on top of an established system. Without the system underneath, it has nothing to read and nowhere to write. **Start at the [ECOSYSTEM map](https://github.com/derekcedarbaum2/claude-code-setup/blob/main/ECOSYSTEM.md)** and follow the install sequence — come back to this repo when ECOSYSTEM tells you to.

The runner's pre-flight check verifies all of the below before doing any work and prints actionable errors when something is missing. Skip the check with `--skip-preflight` if you know your setup.

### Required (hard fail without these)

- **Claude Code** installed and on `$PATH` (or set `CLAUDE_BIN_OVERRIDE` env var).
- **A Markdown vault** (Obsidian or similar). The runner auto-discovers `$HOME/Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault/` (Obsidian default on macOS) but any path works — set `VAULT_PATH` env var to override.
- **`python3`** on `$PATH`. The runner uses Python 3 for the deterministic enumerate / pre-route guard / finalize phases (no LLM calls — just fast file ops + JSON manipulation). Already installed on every modern macOS and Linux distribution.
- **[`ai-knowledge-system`](https://github.com/derekcedarbaum2/ai-knowledge-system) installed** — provides the auto-memory + Knowledge Router pattern. The skill writes Router promotions to `~/.claude/projects/<slug>/memory/MEMORY.md`; if that file doesn't exist anywhere, principle promotion silently fails.
- **[`vault-conventions`](https://github.com/derekcedarbaum2/vault-conventions) installed** — provides the `_learnings.md` schema (`## Learnings / ## Key Decisions / ## Open Threads`) and the `Vault/CLAUDE.md` folder map this skill reads. Without it, appends land in unexpected places or fail.
- **Accumulated content.** This skill clusters across `_learnings.md` + session archives + voice memos. If you have none of those (e.g., fresh Obsidian vault), the corpus is empty and the skill has nothing to do. **Plan on ~6+ weeks of active Claude Code use first.** Pre-flight will hard-fail if no `_learnings.md` files exist anywhere in the vault.

### Recommended (soft warnings without these — runs but with reduced functionality)

- **[`note-highlight-indexer`](https://github.com/derekcedarbaum2/note-highlight-indexer) installed** — provides the `auto-playbook-distill` skill that this skill calls for principle/anti-pattern routing into playbooks. Also provides `Vault/Playbooks-Index.md` (the routing table). Without it, principle clusters route to `_resurface-queue.md` instead of distilling into a playbook topic file.
- **`archive-session.sh` SessionEnd hook** (from `vault-conventions`) — populates session archives at `Vault/AI Toolkit/CC Chat History/`. Without it, the primary corpus tier (session archives) is empty; the skill works on `_learnings.md` content alone, which is much sparser.

### Optional

- **Any task-manager MCP** (Todoist, Linear, Things, OmniFocus, etc.) — used for commitment-type clusters. If you have one configured AND have defined a venture → destination mapping (see SKILL.md "Reference: venture → task-destination mapping"), commitments will create tasks there. If you don't have one, commitments fall back to `_learnings.md` Key Decisions only. **The skill works fully without any task-manager MCP.**
- **`Vault/Voice Memos/` directory** — only relevant if you have a voice-memo capture pipeline (e.g., the Monologue cron in `claude-code-setup`). Empty / missing folder is fine.

### Configuration overrides

Without editing the script:

```bash
export VAULT_PATH="/path/to/your/vault"           # if your vault isn't at the iCloud-Obsidian default
export CLAUDE_BIN_OVERRIDE="/usr/local/bin/claude" # if claude isn't at $HOME/.local/bin/claude
```

---

## Install (macOS)

```bash
# 1. Install the skill
cp -r skill ~/.claude/skills/learnings-resurface

# 2. Install the runner
cp runner/learnings-resurface.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/learnings-resurface.sh

# 3. Edit the plist's path to your username, then install
cp launchd/com.user.learnings-resurface.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.learnings-resurface.plist
```

Verify with a dry run:

```bash
~/.claude/hooks/learnings-resurface.sh --dry-run --window 30
```

This prints what would be routed without writing anything.

---

## Tuning

| Knob | Where | Default | When to change |
|---|---|---|---|
| Window (lookback days) | `--window N` | 90 | Shorter (30) for active periods; longer (180) on a sparse vault |
| Pattern cap per run | `SKILL.md` Hard rule 9 | 5 | Raise if your vault is high-volume; cap exists to prevent noise floods |
| Mentions threshold | `SKILL.md` Phase A.4 | 3 | Lower (2) when you want more recall; higher (5) when you want more precision |
| Source-diversity threshold | `SKILL.md` Phase A.4 | 2 distinct human sources | Almost never change — this is the anti-echo guard |
| Promotion threshold | `SKILL.md` Phase B.3 | `mentions ≥3` AND `cross_venture: true` | Tighten if your Router is getting noisy |
| Per-phase wall clock | `runner/learnings-resurface.sh` `PHASE_TIMEOUT` | 1800s (30 min) | Raise only if your corpus is very large; below 900s starts cutting Phase B short |
| Per-phase max turns | `runner/learnings-resurface.sh` `MAX_TURNS` | 80 | Raise if Phase B truncates with surplus pending |

## Resuming a failed run

If a phase fails (network blip, timeout, transient error), nothing is lost — Phase A's clusters and Phase B's routing decisions are persisted to disk before the next phase starts. Resume from the last incomplete phase:

```bash
# List recent runs
ls -lt ~/.claude/state/learnings-resurface/runs/ | head

# Resume a specific run from Phase B (Phase A's clusters.json is preserved)
~/.claude/hooks/learnings-resurface.sh --resume 20260512-220015-12345 --from-phase B
```

File-presence checks ensure completed steps aren't re-run. If a run completed successfully, re-invoking the runner with the same run-id is a no-op.

---

## What this is not

- **Not a chat-based "ask my notes" tool.** It's a write-back reconciliation pass. Output goes to playbooks, memory, `_learnings.md`, and (optionally) your task manager — not a conversational answer.
- **Not real-time.** Weekly cron is the right cadence for the patterns it's catching. Faster runs miss recurrence and over-route noise.
- **Not generic.** It assumes a venture-folder vault with `_learnings.md` per folder, an auto-memory Knowledge Router, and an `auto-playbook-distill` skill for the playbook side. Adapt the routing layer if your stack differs.

---

## License

MIT.
