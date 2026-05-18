#!/usr/bin/env python3
"""
Prune-memory dry-run — headless audit, no fixes. Appends summary to Vault/log.md.

Checks (subset of /prune-memory skill, mechanical only):
1. MEMORY.md line count vs 80-line cap.
2. INDEX.md line count vs 200-line soft cap.
3. Memory file subfolder/filename consistency.
4. Tag-vocabulary compliance (every file has kind: and decay: namespaces).
5. project_*.md files in memory dir (should be zero post-reorg).

Stale check (#3 in the skill) requires judgment and is skipped in the cron.
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

HOME = Path.home()
MEMORY_DIR = HOME / ".claude/projects/-Users-derekcedarbaum/memory"
MEMORY_MD = MEMORY_DIR / "MEMORY.md"
INDEX_MD = MEMORY_DIR / "INDEX.md"
VAULT_ROOT = HOME / "Library/Mobile Documents/iCloud~md~obsidian/Documents/Vault"
LOG_FILE = VAULT_ROOT / "log.md"

SUBFOLDERS = ("user", "feedback", "principle", "location", "pipeline")


def count_lines(p: Path) -> int:
    return len(p.read_text(encoding="utf-8").splitlines())


def parse_tags(text: str) -> list[str]:
    m = re.search(r"^tags:\s*\[(.*?)\]\s*$", text, re.MULTILINE)
    if not m or not m.group(1).strip():
        return []
    return [t.strip() for t in m.group(1).split(",") if t.strip()]


def main():
    now_iso = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    findings = []
    severity = {"critical": 0, "warning": 0, "info": 0}

    # 1. MEMORY.md size
    mem_lines = count_lines(MEMORY_MD)
    if mem_lines > 80:
        findings.append(("critical", f"MEMORY.md {mem_lines} lines > 80 cap"))
        severity["critical"] += 1
    elif mem_lines > 70:
        findings.append(("warning", f"MEMORY.md {mem_lines} lines (approaching 80 cap)"))
        severity["warning"] += 1
    else:
        findings.append(("info", f"MEMORY.md {mem_lines} lines (under cap)"))
        severity["info"] += 1

    # 2. INDEX.md size
    if INDEX_MD.exists():
        idx_lines = count_lines(INDEX_MD)
        if idx_lines > 200:
            findings.append(("warning", f"INDEX.md {idx_lines} lines (cold rot risk)"))
            severity["warning"] += 1

    # 3. Subfolder/filename consistency + 4. tag compliance
    for sub in SUBFOLDERS:
        sub_path = MEMORY_DIR / sub
        if not sub_path.exists():
            findings.append(("critical", f"Subfolder missing: {sub}/"))
            severity["critical"] += 1
            continue
        for f in sorted(sub_path.glob("*.md")):
            # filename prefix
            if not f.name.startswith(f"{sub}_"):
                findings.append(("warning", f"{sub}/{f.name}: filename does not start with {sub}_"))
                severity["warning"] += 1
            text = f.read_text(encoding="utf-8")
            tags = parse_tags(text)
            has_kind = any(t.startswith("kind:") for t in tags)
            has_decay = any(t.startswith("decay:") for t in tags)
            if not has_kind:
                findings.append(("warning", f"{sub}/{f.name}: missing kind: tag"))
                severity["warning"] += 1
            if not has_decay:
                findings.append(("warning", f"{sub}/{f.name}: missing decay: tag"))
                severity["warning"] += 1

    # 5. project_*.md anywhere in memory dir
    for f in MEMORY_DIR.rglob("project_*.md"):
        findings.append(("critical", f"DEPRECATED project_*.md in memory: {f.relative_to(MEMORY_DIR)} — should be in vault _learnings.md"))
        severity["critical"] += 1

    # Print to stdout (cron log)
    print(f"Prune-memory dry-run @ {now_iso}")
    print(f"  Findings: critical={severity['critical']} warning={severity['warning']} info={severity['info']}")
    for sev, msg in findings:
        print(f"  [{sev}] {msg}")

    # Append summary to vault log.md
    with LOG_FILE.open("a", encoding="utf-8") as logf:
        logf.write(
            f"{now_iso} | prune-memory-dryrun | summary | "
            f"critical={severity['critical']} warning={severity['warning']} info={severity['info']} | "
            f"MEMORY.md={mem_lines}/80\n"
        )
        if severity["critical"] > 0:
            for sev, msg in findings:
                if sev == "critical":
                    logf.write(f"{now_iso} | prune-memory-dryrun | critical | {msg}\n")


if __name__ == "__main__":
    main()
