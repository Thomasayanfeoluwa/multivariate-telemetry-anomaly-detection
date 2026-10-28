"""
Audit project structure: report meaningful files, stubs, empty placeholders.

Run from the project root:
    python scripts/audit_project.py

Or write a Markdown report (useful for README appendix or cleanup planning):
    python scripts/audit_project.py --markdown reports/project_audit.md

Classification:
    empty        0 bytes
    stub         1 – 100 bytes      (likely untouched placeholder)
    small        101 – 1,000 bytes  (suspicious — worth checking)
    meaningful   > 1,000 bytes      (real content)

Excluded from enumeration:
    .git, node_modules, cats/, venv, __pycache__, .pytest_cache,
    dist/, build/, .vite, .ipynb_checkpoints
    data/raw/, data/processed/, data/parquet/ (large, private)
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path


EXCLUDE_DIRS = {
    ".git", "node_modules", "cats", "venv", ".venv", "env",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "dist", "build", ".vite", ".ipynb_checkpoints", ".next",
    "site-packages", ".cache",
}

LARGE_DATA_DIRS = {"data/raw", "data/processed", "data/parquet"}


def categorize(size: int) -> str:
    if size == 0:
        return "empty"
    if size <= 100:
        return "stub"
    if size <= 1000:
        return "small"
    return "meaningful"


def audit(root: Path):
    files_by_dir: dict[str, list[tuple[str, int, str]]] = defaultdict(list)
    empty_dirs: list[str] = []
    total_files = 0

    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root)
        if any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        rel_str = str(rel).replace("\\", "/")
        if any(rel_str == d or rel_str.startswith(d + "/") for d in LARGE_DATA_DIRS):
            continue

        if path.is_file():
            size = path.stat().st_size
            parent = str(rel.parent).replace("\\", "/")
            files_by_dir[parent].append((rel.name, size, categorize(size)))
            total_files += 1
        elif path.is_dir():
            try:
                has_files = any(
                    p.is_file()
                    and not any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts)
                    for p in path.rglob("*")
                )
            except (PermissionError, OSError):
                has_files = False
            if not has_files:
                empty_dirs.append(rel_str)

    return files_by_dir, empty_dirs, total_files


def print_report(files_by_dir, empty_dirs, total_files, root: Path) -> None:
    print(f"# Project audit — {root}\n")

    counts = defaultdict(int)
    for dir_files in files_by_dir.values():
        for _, _, cat in dir_files:
            counts[cat] += 1

    print("## Summary")
    print(f"  Total files audited:    {total_files}")
    print(f"    meaningful (>1 KB):   {counts['meaningful']}")
    print(f"    small (100 B – 1 KB): {counts['small']}")
    print(f"    stub (1 – 100 B):     {counts['stub']}")
    print(f"    empty (0 B):          {counts['empty']}")
    print(f"  Empty folders:          {len(empty_dirs)}")
    print()

    print("## Empty and stub files — candidates for cleanup")
    any_stub = False
    for dir_path in sorted(files_by_dir):
        stubs = [f for f in files_by_dir[dir_path] if f[2] in ("empty", "stub")]
        if not stubs:
            continue
        any_stub = True
        print(f"  {dir_path}/")
        for name, size, cat in stubs:
            print(f"    [{cat:6s}] {size:>5,} B  {name}")
    if not any_stub:
        print("  (none — all files have content)")
    print()

    if empty_dirs:
        print("## Empty folders")
        for d in sorted(empty_dirs):
            print(f"  {d}/")
        print()

    print("## Meaningful files (kept)")
    for dir_path in sorted(files_by_dir):
        meaningful = [f for f in files_by_dir[dir_path] if f[2] == "meaningful"]
        if not meaningful:
            continue
        print(f"  {dir_path}/")
        for name, size, _ in meaningful:
            print(f"    {size:>10,} B  {name}")
        print()


def write_markdown(path: Path, files_by_dir, empty_dirs, total_files, root: Path) -> None:
    lines: list[str] = [f"# Project audit\n\nGenerated from `{root}`.\n"]

    counts = defaultdict(int)
    for dir_files in files_by_dir.values():
        for _, _, cat in dir_files:
            counts[cat] += 1

    lines.append("## Summary\n")
    lines.append("| Category | Count |")
    lines.append("|---|---:|")
    lines.append(f"| Total files | {total_files} |")
    lines.append(f"| Meaningful (>1 KB) | {counts['meaningful']} |")
    lines.append(f"| Small (100 B – 1 KB) | {counts['small']} |")
    lines.append(f"| Stub (1 – 100 B) | {counts['stub']} |")
    lines.append(f"| Empty (0 B) | {counts['empty']} |")
    lines.append(f"| Empty folders | {len(empty_dirs)} |")
    lines.append("")

    stubs_any = any(f[2] in ("empty", "stub") for fs in files_by_dir.values() for f in fs)
    if stubs_any:
        lines.append("## Empty and stub files\n")
        lines.append("| Directory | File | Size | Category |")
        lines.append("|---|---|---:|---|")
        for dir_path in sorted(files_by_dir):
            for name, size, cat in files_by_dir[dir_path]:
                if cat in ("empty", "stub"):
                    lines.append(f"| `{dir_path}/` | `{name}` | {size:,} B | {cat} |")
        lines.append("")

    if empty_dirs:
        lines.append("## Empty folders\n")
        for d in sorted(empty_dirs):
            lines.append(f"- `{d}/`")
        lines.append("")

    lines.append("## Meaningful files\n")
    for dir_path in sorted(files_by_dir):
        meaningful = [f for f in files_by_dir[dir_path] if f[2] == "meaningful"]
        if not meaningful:
            continue
        lines.append(f"### `{dir_path}/`\n")
        for name, size, _ in meaningful:
            lines.append(f"- `{name}` — {size:,} B")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit project structure.")
    parser.add_argument("--root", default=".", help="Project root (default: cwd)")
    parser.add_argument(
        "--markdown", default=None, help="Write Markdown report to this path"
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory.")
        return 1

    files_by_dir, empty_dirs, total = audit(root)
    print_report(files_by_dir, empty_dirs, total, root)

    if args.markdown:
        out = Path(args.markdown)
        out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(out, files_by_dir, empty_dirs, total, root)
        print(f"\nMarkdown report written to: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())