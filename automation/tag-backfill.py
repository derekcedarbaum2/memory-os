#!/usr/bin/env python3
"""
Tag backfill — idempotent. Walks memory dir + vault and populates `tags:` frontmatter
with controlled-vocab values inferred from path. Re-runnable.

Conventions encoded:
- ~/.claude/projects/-Users-derekcedarbaum/memory/<kind-subfolder>/<file>.md
    → tags: [kind:<inferred>, decay:<default>]
- Vault/<top>/<venture-or-domain>/_learnings.md
    → tags: [venture:<slug>|domain:<slug>, kind:state, decay:high]
- Vault/<...>/<other>.md  → leaves existing tags alone if non-empty controlled vocab.
                            If `tags: []` or missing, infers kind:reference + decay:medium as safe default.

The script never removes existing controlled-vocab tags. It merges in missing namespaces.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HOME = Path.home()
MEMORY_DIR = HOME / ".claude/projects/-Users-derekcedarbaum/memory"
VAULT_ROOT = HOME / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"

MEMORY_SUBFOLDER_TO_TAGS = {
    "user":      ("kind:identity",  "decay:low"),
    "feedback":  ("kind:feedback",  "decay:medium"),
    "principle": ("kind:principle", "decay:low"),
    "location":  ("kind:location",  "decay:medium"),
    "pipeline":  ("kind:pipeline",  "decay:medium"),
}

# Vault folder → tag inference
# (top-level path segment that the file lives under)  →  (tag_namespace, slug)
VAULT_VENTURE_MAP = {
    "Ideas/Bastion":                              ("venture", "bastion"),
    "Work/Unlikely Labs":                         ("venture", "unlikely-labs"),
    "Work/Inversion Space":                       ("venture", "inversion-space"),
    "Work/Neros":                                 ("venture", "neros"),
    "Work/AI Build Partners":                     ("venture", "ai-build-partners"),
    "Work/CapitalGrid":                           ("venture", "capitalgrid"),
    "Work/Vanguard Foundry Podcast":              ("venture", "vanguard-foundry"),
    "Ideas/Estivon Agentic Real Estate":          ("venture", "estivon"),
    "Ideas/Nick Financing/Tribal Datacenter":     ("venture", "tribal-datacenter"),
    "Ideas/Aristotle's World":                    ("venture", "aristotles-world"),
    "Ideas/Biographer":                           ("venture", "biographer"),
    "Ideas/Lian Fashion Game":                    ("venture", "lian-fashion-game"),
    "Ideas/Litmus":                               ("venture", "litmus"),
    "Ideas/Luma":                                 ("venture", "luma"),
    "Ideas/Marathon":                             ("venture", "marathon"),
    "Professional Development/AI":                ("venture", "red6"),
    "Personal Brand":                             ("domain",  "personal-brand"),
    "Personal/Health & Wellness":                 ("domain",  "health"),
    "Personal/Family":                            ("domain",  "family"),
    "Writing":                                    ("domain",  "writing"),
    "AI Toolkit":                                 ("domain",  "claude-code"),
    "Design":                                     ("domain",  "design"),
    "Company Building":                           ("domain",  "company-building"),
}

EXCLUDE_VAULT_PATHS = (
    "_archive/",
    "_attachments/",
    ".git/",
    ".obsidian/",
    "Reading/Books/",
    "Reading/Articles/",
)


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
    """Returns (parsed_fields, raw_frontmatter_block, body)."""
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not m:
        return {}, "", text
    raw = m.group(1)
    body = text[m.end():]
    fields = {}
    for line in raw.splitlines():
        if ": " in line:
            k, _, v = line.partition(": ")
            fields[k.strip()] = v.strip()
    return fields, raw, body


def parse_tags(raw_value: str) -> list[str]:
    """Parse a tags: value into a list. Handles 'tags: []', 'tags: [a, b]', 'tags: [a:b, c:d]'."""
    if not raw_value:
        return []
    s = raw_value.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1].strip()
        if not s:
            return []
        return [t.strip() for t in s.split(",") if t.strip()]
    return []


def merge_tags(existing: list[str], required: list[str]) -> list[str]:
    """Merge: keep existing controlled-vocab tags, add missing namespaces from required."""
    legacy_drop = {"learnings", "domain-knowledge"}  # legacy free-text tags to discard
    cleaned = [t for t in existing if t not in legacy_drop and ":" in t]
    existing_namespaces = {t.split(":", 1)[0] for t in cleaned}
    for req in required:
        ns = req.split(":", 1)[0]
        if ns not in existing_namespaces:
            cleaned.append(req)
    # Stable order: kind first, venture second, domain third, decay fourth, status fifth, others last
    order = {"kind": 0, "venture": 1, "domain": 2, "decay": 3, "status": 4}
    cleaned.sort(key=lambda t: (order.get(t.split(":", 1)[0], 99), t))
    return cleaned


def infer_memory_tags(path: Path) -> list[str]:
    rel = path.relative_to(MEMORY_DIR)
    parts = rel.parts
    if len(parts) < 2:
        return ["kind:reference", "decay:medium"]  # MEMORY.md / INDEX.md fall here but we skip those
    subfolder = parts[0]
    if subfolder in MEMORY_SUBFOLDER_TO_TAGS:
        return list(MEMORY_SUBFOLDER_TO_TAGS[subfolder])
    return ["kind:reference", "decay:medium"]


def infer_vault_tags(path: Path) -> list[str]:
    rel = str(path.relative_to(VAULT_ROOT))
    # match the longest VAULT_VENTURE_MAP prefix
    best = None
    for prefix, _ in VAULT_VENTURE_MAP.items():
        if rel.startswith(prefix + "/") or rel.startswith(prefix):
            if best is None or len(prefix) > len(best):
                best = prefix
    tags: list[str] = []
    if best:
        ns, slug = VAULT_VENTURE_MAP[best]
        tags.append(f"{ns}:{slug}")
    is_learnings = path.name == "_learnings.md"
    if is_learnings:
        tags.append("kind:state")
        tags.append("decay:high")
    else:
        tags.append("kind:reference")
        tags.append("decay:medium")
    return tags


def update_file(path: Path, infer_fn) -> tuple[bool, str]:
    """Returns (changed, reason)."""
    text = path.read_text(encoding="utf-8")
    fields, raw, body = parse_frontmatter(text)
    if not raw:
        return False, "no frontmatter"
    required = infer_fn(path)
    existing = parse_tags(fields.get("tags", ""))
    merged = merge_tags(existing, required)
    if merged == existing:
        return False, "already compliant"
    # Rebuild frontmatter block, replacing or adding tags line
    new_lines = []
    saw_tags = False
    for line in raw.splitlines():
        if line.startswith("tags:"):
            new_lines.append("tags: [" + ", ".join(merged) + "]")
            saw_tags = True
        else:
            new_lines.append(line)
    if not saw_tags:
        new_lines.append("tags: [" + ", ".join(merged) + "]")
    new_raw = "\n".join(new_lines)
    new_text = "---\n" + new_raw + "\n---\n" + body
    path.write_text(new_text, encoding="utf-8")
    return True, f"merged → [{', '.join(merged)}]"


def walk_memory():
    changes = []
    for subfolder in MEMORY_SUBFOLDER_TO_TAGS:
        for f in sorted((MEMORY_DIR / subfolder).glob("*.md")):
            changed, reason = update_file(f, infer_memory_tags)
            changes.append((f, changed, reason))
    return changes


def walk_vault():
    changes = []
    for f in sorted(VAULT_ROOT.rglob("*.md")):
        rel = str(f.relative_to(VAULT_ROOT))
        if any(rel.startswith(p) for p in EXCLUDE_VAULT_PATHS):
            continue
        if rel.startswith("Voice Memos/") or rel.startswith("Monologue/"):
            continue  # ephemeral
        # Only touch _learnings.md and files with tags: [] or missing tags
        text = f.read_text(encoding="utf-8", errors="ignore")
        fields, _, _ = parse_frontmatter(text)
        if not fields:
            continue
        existing = parse_tags(fields.get("tags", ""))
        # Skip files with already-compliant tags (have kind: namespace)
        if any(t.startswith("kind:") for t in existing) and any(t.startswith("decay:") for t in existing):
            continue
        # Only backfill _learnings.md aggressively. For other files, only fix if tags: is empty/missing.
        is_learnings = f.name == "_learnings.md"
        if not is_learnings and existing:
            continue  # don't disturb non-learnings files that have any tags
        changed, reason = update_file(f, infer_vault_tags)
        changes.append((f, changed, reason))
    return changes


def main():
    print(f"Memory dir: {MEMORY_DIR}", flush=True)
    mem_changes = walk_memory()
    mem_updated = sum(1 for _, c, _ in mem_changes if c)
    print(f"  scanned {len(mem_changes)} files, updated {mem_updated}", flush=True)
    for f, c, r in mem_changes:
        if c:
            print(f"    {f.relative_to(MEMORY_DIR)}: {r}", flush=True)

    print(f"\nVault: {VAULT_ROOT}", flush=True)
    vault_changes = walk_vault()
    vault_updated = sum(1 for _, c, _ in vault_changes if c)
    print(f"  scanned {len(vault_changes)} files, updated {vault_updated}", flush=True)
    for f, c, r in vault_changes:
        if c:
            print(f"    {f.relative_to(VAULT_ROOT)}: {r}", flush=True)

    print(f"\nDone. Memory updated: {mem_updated}. Vault updated: {vault_updated}.")


if __name__ == "__main__":
    main()
