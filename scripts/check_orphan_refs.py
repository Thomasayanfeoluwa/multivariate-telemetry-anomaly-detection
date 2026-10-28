"""
Verify that specific deleted/planned files are not referenced anywhere in
the project source tree.

Run from the project root:
    python scripts/check_orphan_refs.py

Exits with code 0 if no references found (safe to commit deletions).
Exits with code 1 if any references found (fix them first).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# Files whose absence is being verified.
TARGETS = [
    "DEPLOYMENT_PLAN.md",
    "PROJECT_SPEC.md",
    "PROJECT_STATE.md",
]

# Directories to skip during the scan.
EXCLUDE_DIRS = {
    ".git", "node_modules", "cats", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", ".vite", ".ipynb_checkpoints", ".next",
    "site-packages", ".cache",
}

# File extensions to scan.
SCAN_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".md", ".ipynb", ".json", ".txt", ".yaml", ".yml",
    ".toml", ".cfg", ".ini", ".env", ".sh", ".ps1",
    ".html", ".css", ".sql",
}

# Case-insensitive whole-word-ish patterns. We use word boundaries to
# avoid false positives in strings like "MYDEPLOYMENT_PLAN_BACKUP".
PATTERNS = [
    re.compile(rf"(?<![\w-]){re.escape(target)}(?![\w-])", re.IGNORECASE)
    for target in TARGETS
]


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Return [(line_number, line_text)] for every line matching any target."""
    hits: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except (OSError, UnicodeDecodeError):
        return hits

    for lineno, line in enumerate(text.splitlines(), start=1):
        for pat in PATTERNS:
            if pat.search(line):
                hits.append((lineno, line.strip()))
                break
    return hits


def main() -> int:
    root = Path.cwd()
    print(f"# Scanning for references to deleted files")
    print(f"# Root: {root}")
    print(f"# Targets: {', '.join(TARGETS)}")
    print()

    total_hits = 0
    files_scanned = 0
    files_with_hits = 0

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        # Skip this audit script itself — it must contain the target
        # filenames to know what to search for.
        if path.name == "check_orphan_refs.py":
            continue

        files_scanned += 1
        hits = scan_file(path)
        if hits:
            files_with_hits += 1
            rel_str = str(rel).replace("\\", "/")
            print(f"  {rel_str}")
            for lineno, line in hits:
                snippet = line if len(line) <= 120 else line[:117] + "..."
                print(f"    line {lineno}: {snippet}")
            print()
            total_hits += len(hits)

    print("=" * 72)
    print(f"Files scanned:  {files_scanned}")
    print(f"Files with hits: {files_with_hits}")
    print(f"Total matches:   {total_hits}")
    print("=" * 72)

    if total_hits == 0:
        print()
        print("PASS — no references found. Safe to commit the deletions.")
        return 0
    else:
        print()
        print("FAIL — broken references detected. Fix the lines above before")
        print("committing the deletions, or the deployment README will point")
        print("at files that don't exist.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())