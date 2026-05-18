---
title: Tag vocabulary
type: reference
status: active
classification: internal
created: 2026-05-17
updated: 2026-05-17
author: "Derek Cedarbaum"
tags: [kind:pipeline, domain:claude-code, decay:low]
---

# Tag vocabulary

Controlled vocabulary for YAML `tags:` across the memory dir and vault. Tags are how agents grep-filter at retrieval time. **Never leave `tags: []`.** Pick from below. If nothing fits, add a new term here first, then use it — don't invent ad-hoc tags inline.

Format: `tags: [namespace:value, namespace:value, ...]`

## Namespaces

### `kind:` — what the entry IS (required, exactly one)

| Tag | Used for |
|---|---|
| `kind:identity` | Facts about Derek, family, immutable personal context |
| `kind:preference` | Communication/behavior rules ("how to work with Derek") |
| `kind:feedback` | Specific corrections or confirmations from Derek |
| `kind:state` | Current status snapshot of a venture/project/engagement |
| `kind:principle` | Operating heuristic that should fire at decision time |
| `kind:location` | Pointer to where something canonical lives |
| `kind:pipeline` | System / protocol / cron / MCP / hook documentation |
| `kind:gotcha` | Known footgun, API quirk, version-specific bug |

### `venture:` — which venture (when applicable, one)

| Tag | Maps to |
|---|---|
| `venture:bastion` | `Vault/Ideas/Bastion/` |
| `venture:unlikely-labs` | `Vault/Work/Unlikely Labs/` |
| `venture:inversion-space` | `Vault/Work/Inversion Space/` |
| `venture:neros` | `Vault/Work/Neros/` |
| `venture:estivon` | `Vault/Ideas/Estivon Agentic Real Estate/` |
| `venture:tribal-datacenter` | `Vault/Ideas/Nick Financing/Tribal Datacenter/` |
| `venture:ai-build-partners` | `Vault/Work/AI Build Partners/` |
| `venture:red6` | Current employer (NOT a venture — use this for AI-adoption work and IP-boundary topics) |
| `venture:capitalgrid` | `Vault/Work/CapitalGrid/` |

### `domain:` — non-venture topical bucket (when applicable, one or more)

| Tag | Used for |
|---|---|
| `domain:health` | Family health, nutrition, Noa PT, supplements, dog feeding |
| `domain:family` | Spouse, kids, family-day, kids learning |
| `domain:personal-brand` | Public-facing: LinkedIn, GitHub, talks, essays |
| `domain:writing` | Voice, style, essay craft |
| `domain:claude-code` | CC setup, skills, hooks, MCP, memory system, vault architecture |
| `domain:design` | Decks, charts, diagrams, branded artifacts |
| `domain:sales` | Outreach, pitches, prospecting |
| `domain:hiring` | Interview prep (when not engagement-specific) |

### `decay:` — how fast does this rot (required, one)

| Tag | Meaning |
|---|---|
| `decay:low` | Durable — identity, hard preferences, foundational principles. Re-verify yearly. |
| `decay:medium` | Quarter-scale — locations, positioning, pipelines. Re-verify quarterly. |
| `decay:high` | Week-scale — project state, active engagements. Re-verify on each touch. |

### `status:` — lifecycle (optional; default `status:active`)

| Tag | Meaning |
|---|---|
| `status:active` | Live, in scope this quarter |
| `status:dormant` | Idle but not killed; ignore unless explicitly invoked |
| `status:archived` | Done. Keep for history; do not surface in routing |

## Example combinations

```yaml
# Bastion status doc in the vault
tags: [venture:bastion, kind:state, decay:high]

# A feedback memory in ~/.claude/memory/feedback/
tags: [kind:feedback, decay:medium]

# A principle (operating heuristic)
tags: [kind:principle, domain:sales, decay:low]

# A pipeline doc
tags: [kind:pipeline, domain:claude-code, decay:medium]

# A location pointer
tags: [kind:location, venture:neros, decay:medium]

# A dormant idea folder
tags: [venture:luma, kind:state, decay:low, status:dormant]
```

## Grep recipes

```bash
# Find every Bastion artifact
grep -lrE "tags:.*venture:bastion" ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/Vault/

# Find principles (decision-time heuristics)
grep -lrE "tags:.*kind:principle" ~/.claude/projects/-Users-derekcedarbaum/memory/

# Find everything tagged sales — across vault + memory
grep -lrE "tags:.*domain:sales" ~/.claude/projects/-Users-derekcedarbaum/memory/ ~/Library/Mobile\ Documents/iCloud~md~obsidian/Documents/Vault/

# Find dormant ventures (skip on default routing)
grep -lrE "tags:.*status:dormant" ~/.claude/projects/-Users-derekcedarbaum/memory/
```

## Enforcement

- **All new `.md` files in the vault or memory dir must include valid tags.** No empty `tags: []`.
- When editing an old file that uses `tags: [learnings, domain-knowledge]` or similar legacy free-text tags, replace with controlled vocab.
- If you need a tag that doesn't exist here, add it to this file *first*, then use it.
- This file is the ground truth — when in doubt, grep here.
