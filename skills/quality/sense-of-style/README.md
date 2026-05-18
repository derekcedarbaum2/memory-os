# Sense of Style

**Diagnose and rewrite prose using Steven Pinker's *Sense of Style* principles.**

Scores writing on 8 style dimensions, flags specific line-level problems (nominalizations, passive voice, hedges, broken topic chains, clichés), and produces a rewrite that **preserves voice while killing the things that make writing soft.**

For PRDs, stakeholder updates, posts, emails, essays — any prose where the content is right but the writing is bloated, academic, or hedged.

---

## Pairs with [`qa-loop`](https://github.com/derekcedarbaum2/qa-loop)

| qa-loop | sense-of-style |
|---------|----------------|
| Scores **argument**, evidence, structure | Scores **prose** quality |
| Fixes "this claim is unsupported" | Fixes "this sentence is a nominalization swamp" |
| Asks "is this true?" | Asks "does this read well?" |
| Works on PM artifacts | Works on any prose |

Run them in sequence on high-stakes writing: `qa-loop` first (fix the thinking), `sense-of-style` second (fix the writing).

---

## The 8 dimensions

The skill scores each dimension 0–10 and flags line-level violations:

1. **Classic style** — does the prose treat the reader as an equal looking at the same world the writer is looking at?
2. **Nominalizations** — verbs disguised as nouns ("conduct an analysis" vs. "analyze")
3. **Passive voice** — used deliberately or by default?
4. **Topic chain coherence** — do sentences flow from given → new info?
5. **Hedge density** — "perhaps," "somewhat," "might be argued" — earned or reflexive?
6. **Cliché load** — dead metaphors that no longer make the reader see anything
7. **Curse of knowledge** — assuming the reader knows what you know
8. **Tree-then-string** — does the syntax tree reach the reader as a clean string?

A document scoring ≥ 72/80 gets "no rewrite needed." The skill won't manufacture changes to justify itself.

---

## Voice file (optional but recommended)

Style serves voice. If you have an opinionated personal writing voice — direct, first-principles, occasionally profane, whatever — write it down once and the skill will enforce Pinker's principles **on top of** your voice rather than against it.

Two ways to set up:

**Option A — use the template.** Copy `examples/voice.template.md` to `~/.claude/skills/_shared/voice.md` (Claude Code) or wherever your agent looks for shared context. Fill in the sections.

**Option B — see a real example.** `examples/voice-example-derek.md` is a real, in-production voice file from this repo's author. Read it for shape, then write your own.

If no voice file is configured, the skill falls back to Pinker-only enforcement. Still useful — just less personalized.

---

## Install

### Claude Code

```bash
mkdir -p ~/.claude/skills/sense-of-style
cp SKILL.md ~/.claude/skills/sense-of-style/SKILL.md

# Optional: voice file
mkdir -p ~/.claude/skills/_shared
cp examples/voice.template.md ~/.claude/skills/_shared/voice.md
# then edit ~/.claude/skills/_shared/voice.md to describe your voice
```

Invoke with `/sense-of-style` or `/sense-of-style /path/to/document.md`.

### Codex CLI

Codex doesn't have a skill loader, so use the `SKILL.md` as a prompt template:

```bash
mkdir -p ~/.codex/prompts
cp SKILL.md ~/.codex/prompts/sense-of-style.md
```

Invoke by pasting the file contents into a Codex session, or wrap in a shell alias. The voice file is the same — just point the skill at wherever you keep it.

---

## Usage

```
/sense-of-style /path/to/document.md     # full file path
/sense-of-style                          # operates on the last generated document in context
```

Output: scoring report + line-level flags + rewrite (only when overall score < 72/80).

---

## License

MIT. Fork it. Pinker's principles are public; this is just one operationalization.

*Based on Steven Pinker, The Sense of Style (2014).*
