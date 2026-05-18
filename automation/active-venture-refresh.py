#!/usr/bin/env python3
"""
Active-venture refresh — keeps MEMORY.md hot pinboard in sync with reality.

Logic (purely additive + demotive — does NOT auto-add new ventures):
1. Read MEMORY.md `## Active ventures (kind:state)` section.
2. For each pinboard entry, find the linked vault _learnings.md.
3. Check mtime:
   - >90 days no touch  → DEMOTE: remove from pinboard, append to INDEX.md "Dormant ventures" section.
   - 30-90 days         → keep, but flag in log report
   - <30 days           → keep (active)
4. Scan all vault _learnings.md NOT currently on pinboard with mtime <14 days → log as
   "promotion candidates" — do NOT auto-promote (judgment call).

Outputs:
- Updated MEMORY.md (demotions only)
- Updated INDEX.md (added dormant entries)
- Vault/log.md (one line per demotion + a summary of candidates)
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

HOME = Path.home()
MEMORY_DIR = HOME / ".claude/projects/-Users-derekcedarbaum/memory"
MEMORY_MD = MEMORY_DIR / "MEMORY.md"
INDEX_MD = MEMORY_DIR / "INDEX.md"
VAULT_ROOT = HOME / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"
LOG_FILE = VAULT_ROOT / "log.md"

DORMANT_DAYS = 90
WARN_DAYS = 30
CANDIDATE_DAYS = 14

EXCLUDE = ("_archive/", "Personal/", "Reading/")


def extract_section(md: str, header: str) -> tuple[str | None, int, int]:
    """Returns (section_body, start_idx_of_header, end_idx). End is start of next ## header or EOF."""
    pat = re.compile(rf"^{re.escape(header)}\s*$", re.MULTILINE)
    m = pat.search(md)
    if not m:
        return None, -1, -1
    start = m.end()
    next_h = re.search(r"^## ", md[start:], re.MULTILINE)
    end = start + next_h.start() if next_h else len(md)
    return md[start:end], m.start(), end


def parse_pinboard_entries(section: str):
    """Parse lines like '- **Bastion** — desc → `Vault/path/_learnings.md`'."""
    entries = []
    for line in section.splitlines():
        # Tolerate optional " (parenthetical)" between **Name** and the em-dash.
        m = re.match(
            r"^- \*\*(.+?)\*\*(?:\s*\([^)]*\))?\s*—\s*(.+?)\s*→\s*`(.+?_learnings\.md)`",
            line,
        )
        if m:
            entries.append({
                "name": m.group(1),
                "desc": m.group(2),
                "path": m.group(3),
                "raw_line": line,
            })
    return entries


def main():
    if not MEMORY_MD.exists():
        print(f"FATAL: {MEMORY_MD} not found", file=sys.stderr)
        return 1
    memory_text = MEMORY_MD.read_text(encoding="utf-8")
    pin_section, pin_start, pin_end = extract_section(memory_text, "## Active ventures (kind:state) — read the linked `_learnings.md` first for any task on this venture")
    if pin_section is None:
        print("WARN: Active ventures section not found in MEMORY.md", file=sys.stderr)
        return 1
    entries = parse_pinboard_entries(pin_section)

    now = dt.datetime.now()
    now_iso = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    today = now.strftime("%Y-%m-%d")
    demotions = []
    warnings_ = []
    pinboard_paths = set()

    for e in entries:
        vault_rel = e["path"]
        # MEMORY.md uses "Vault/..." prefix; convert to absolute
        if vault_rel.startswith("Vault/"):
            abs_path = VAULT_ROOT / vault_rel[len("Vault/"):]
        else:
            abs_path = VAULT_ROOT / vault_rel
        pinboard_paths.add(str(abs_path))
        if not abs_path.exists():
            warnings_.append((e["name"], "missing-file", vault_rel))
            continue
        mtime = abs_path.stat().st_mtime
        days = int((now.timestamp() - mtime) / 86400)
        if days >= DORMANT_DAYS:
            demotions.append((e, days))
        elif days >= WARN_DAYS:
            warnings_.append((e["name"], f"{days}d stale", vault_rel))

    # Find promotion candidates (vault _learnings.md not on pinboard, touched <14d)
    candidates = []
    cutoff_candidate = (now - dt.timedelta(days=CANDIDATE_DAYS)).timestamp()
    for f in VAULT_ROOT.rglob("_learnings.md"):
        rel = str(f.relative_to(VAULT_ROOT))
        if any(rel.startswith(p) for p in EXCLUDE):
            continue
        if str(f) in pinboard_paths:
            continue
        if f.stat().st_mtime >= cutoff_candidate:
            days_ago = int((now.timestamp() - f.stat().st_mtime) / 86400)
            candidates.append((rel, days_ago))

    # Apply demotions: remove from pinboard section, append to INDEX.md
    if demotions:
        new_pin_section = pin_section
        for e, days in demotions:
            # remove the line (and any trailing newline if it leaves a double-blank)
            new_pin_section = new_pin_section.replace(e["raw_line"] + "\n", "")
            new_pin_section = new_pin_section.replace(e["raw_line"], "")
        # rebuild MEMORY.md
        new_memory = memory_text[:pin_start] + memory_text[pin_start:pin_end].replace(pin_section, new_pin_section) + memory_text[pin_end:]
        MEMORY_MD.write_text(new_memory, encoding="utf-8")

        # append to INDEX.md dormant section
        index_text = INDEX_MD.read_text(encoding="utf-8")
        dormant_marker = "## Dormant ventures (status:dormant)"
        if dormant_marker in index_text:
            insert_at = index_text.index(dormant_marker) + len(dormant_marker)
            # find end of that section header line
            insert_at = index_text.index("\n", insert_at) + 1
            additions = ""
            for e, days in demotions:
                additions += f"- **{e['name']}** — {e['desc']} → `{e['path']}` *(auto-demoted {today}, {days}d no touch)*\n"
            new_index = index_text[:insert_at] + additions + index_text[insert_at:]
            INDEX_MD.write_text(new_index, encoding="utf-8")
        else:
            with INDEX_MD.open("a", encoding="utf-8") as f:
                f.write(f"\n## Dormant ventures (auto-demoted)\n\n")
                for e, days in demotions:
                    f.write(f"- **{e['name']}** — {e['desc']} → `{e['path']}` *(auto-demoted {today}, {days}d no touch)*\n")

    # Append to vault log.md
    with LOG_FILE.open("a", encoding="utf-8") as logf:
        logf.write(f"{now_iso} | active-venture-refresh | summary | pinboard_active={len(entries)-len(demotions)} demoted={len(demotions)} warn={len(warnings_)} candidates={len(candidates)}\n")
        for e, days in demotions:
            logf.write(f"{now_iso} | active-venture-refresh | demote | {e['name']} | {days}d no touch | {e['path']}\n")
        for name, reason, vault_rel in warnings_:
            logf.write(f"{now_iso} | active-venture-refresh | warn | {name} | {reason} | {vault_rel}\n")
        for rel, days_ago in candidates:
            logf.write(f"{now_iso} | active-venture-refresh | promotion-candidate | {rel} | touched {days_ago}d ago\n")

    print(f"Demoted: {len(demotions)}")
    print(f"Warnings (30-90d stale): {len(warnings_)}")
    print(f"Promotion candidates (touched <14d, not on pinboard): {len(candidates)}")
    for rel, days in candidates:
        print(f"  - {rel} ({days}d)")


if __name__ == "__main__":
    sys.exit(main() or 0)
