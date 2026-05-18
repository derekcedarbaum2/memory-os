#!/usr/bin/env python3
"""
Dormancy decay — marks vault _learnings.md files as `status:dormant` when no touch in 90 days.
Idempotent. Adds a one-line log entry per change.

Threshold: 90 days no mtime touch on the _learnings.md file itself.

Outputs:
- Updates frontmatter `tags:` on dormant files: adds `status:dormant`, keeps everything else.
- Updates frontmatter `status:` field to `archived` if present (Obsidian-visible).
- Appends a line per change to Vault/log.md.

This script does NOT touch MEMORY.md or INDEX.md — active-venture-refresh handles pinboard moves.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

HOME = Path.home()
VAULT_ROOT = HOME / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"
LOG_FILE = VAULT_ROOT / "log.md"
THRESHOLD_DAYS = 90

EXCLUDE = (
    "_archive/",
    "_attachments/",
    ".git/",
    ".obsidian/",
    "Reading/",
    "Voice Memos/",
    "Monologue/",
    "Personal/",  # personal _learnings stays out of dormancy automation
)


def parse_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    if not m:
        return None, "", text
    return m.group(1), m.group(0), text[m.end():]


def parse_tags(raw: str) -> list[str]:
    m = re.search(r"^tags:\s*\[(.*?)\]\s*$", raw, re.MULTILINE)
    if not m:
        return []
    inner = m.group(1).strip()
    if not inner:
        return []
    return [t.strip() for t in inner.split(",") if t.strip()]


def has_dormant_tag(tags: list[str]) -> bool:
    return any(t.startswith("status:dormant") for t in tags)


def update_tags_to_dormant(raw_fm: str) -> str:
    if re.search(r"^tags:", raw_fm, re.MULTILINE):
        def repl(m):
            inner = m.group(1).strip()
            tags = [t.strip() for t in inner.split(",")] if inner else []
            tags = [t for t in tags if not t.startswith("status:")]
            tags.append("status:dormant")
            return "tags: [" + ", ".join(tags) + "]"
        return re.sub(r"^tags:\s*\[(.*?)\]\s*$", repl, raw_fm, count=1, flags=re.MULTILINE)
    return raw_fm + "\ntags: [status:dormant]"


def update_status_field(raw_fm: str) -> str:
    if re.search(r"^status:", raw_fm, re.MULTILINE):
        return re.sub(r"^status:\s*\S+", "status: archived", raw_fm, count=1, flags=re.MULTILINE)
    return raw_fm


def main():
    cutoff = dt.datetime.now() - dt.timedelta(days=THRESHOLD_DAYS)
    cutoff_ts = cutoff.timestamp()
    now_iso = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    changes = []

    for f in VAULT_ROOT.rglob("_learnings.md"):
        rel = str(f.relative_to(VAULT_ROOT))
        if any(rel.startswith(p) for p in EXCLUDE):
            continue
        mtime = f.stat().st_mtime
        if mtime > cutoff_ts:
            continue  # touched recently, still active
        text = f.read_text(encoding="utf-8")
        raw_fm, raw_block, body = parse_frontmatter(text)
        if raw_fm is None:
            continue
        tags = parse_tags(raw_fm)
        if has_dormant_tag(tags):
            continue  # already dormant, skip
        new_fm = update_tags_to_dormant(raw_fm)
        new_fm = update_status_field(new_fm)
        new_text = "---\n" + new_fm + "\n---\n" + body
        f.write_text(new_text, encoding="utf-8")
        days_stale = int((dt.datetime.now().timestamp() - mtime) / 86400)
        changes.append((rel, days_stale))
        print(f"  dormant: {rel} ({days_stale}d stale)")

    if changes:
        with LOG_FILE.open("a", encoding="utf-8") as logf:
            for rel, days in changes:
                logf.write(f"{now_iso} | dormancy-decay | mark dormant | {rel} | {days}d stale\n")

    print(f"\nDormancy pass complete. {len(changes)} _learnings.md marked dormant.")


if __name__ == "__main__":
    main()
