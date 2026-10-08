#!/usr/bin/env python3
"""Install this Agent Skill into supported global skill directories."""

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
NAME = "design-resource-workflow"
FILES = ("SKILL.md", "references/catalog.md")
MARKER = ".design-resource-workflow-install.json"
TOOL_DIRS = {
    "master": ".skills",
    "hermes": ".hermes/skills",
    "codex": ".codex/skills",
    "claude": ".claude/skills",
    "cursor": ".cursor/skills",
    "gemini-antigravity": ".gemini/skills",
    "opencode": ".config/opencode/skills",
    "opencode-legacy": ".opencode/skills",
    "openclaude": ".openclaude/skills",
    "grok": ".grok/skills",
    "zcode": ".zcode/skills",
    "agents": ".agents/skills",
}


def hashes(root):
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in FILES}


def has_linked_content(root, include_marker=False):
    paths = [root / name for name in FILES]
    paths.extend(root / Path(name).parts[0] for name in FILES if len(Path(name).parts) > 1)
    if include_marker:
        paths.append(root / MARKER)
    return any(path.is_symlink() for path in paths)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tools", default="all", help="Comma-separated names or 'all' (default)")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Home directory (also useful for tests)")
    parser.add_argument("--mode", choices=("auto", "link", "copy"), default="auto")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    parser.add_argument("--verify", action="store_true", help="Check installed skill files without writing")
    args = parser.parse_args(argv)
    names = list(TOOL_DIRS) if args.tools == "all" else list(dict.fromkeys(args.tools.split(",")))
    unknown = [name for name in names if name not in TOOL_DIRS]
    if unknown:
        parser.error("unknown tool(s): " + ", ".join(unknown) + "; choose from " + ", ".join(TOOL_DIRS))
    if any(not (SOURCE / name).is_file() for name in FILES) or has_linked_content(SOURCE):
        parser.error("SKILL.md or references/catalog.md is missing or symlinked in this checkout")

    expected = hashes(SOURCE)
    home = args.home.expanduser().resolve()
    mode = ("copy" if os.name == "nt" else "link") if args.mode == "auto" else args.mode
    problems = 0
    for tool in names:
        dest = home / TOOL_DIRS[tool] / NAME
        if dest == SOURCE or (dest.exists() and dest.resolve() == SOURCE):
            print(f"OK {tool}: {dest} (source or linked)")
            continue
        if dest.is_symlink():
            print(f"CONFLICT {tool}: {dest} points elsewhere; left untouched")
            problems += 1
            continue
        if dest.exists():
            marker = dest / MARKER
            if has_linked_content(dest, include_marker=True):
                print(f"CONFLICT {tool}: {dest} contains symlinks; left untouched")
                problems += 1
                continue
            try:
                saved = json.loads(marker.read_text(encoding="utf-8"))
                if not dest.is_dir() or saved.get("files") != hashes(dest):
                    raise ValueError("installed files changed")
            except (OSError, ValueError, TypeError, KeyError):
                print(f"CONFLICT {tool}: {dest} is not an unchanged managed copy; left untouched")
                problems += 1
                continue
            if args.verify:
                print(f"{'OK' if hashes(dest) == expected else 'STALE'} {tool}: {dest} (managed copy)")
                problems += hashes(dest) != expected
                continue
            if args.dry_run:
                print(f"WOULD UPDATE {tool}: {dest} (managed copy)")
                continue
            for name in FILES:
                target = dest / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SOURCE / name, target)
            marker.write_text(json.dumps({"files": expected}, indent=2) + "\n", encoding="utf-8")
            print(f"UPDATED {tool}: {dest}")
            continue
        if args.verify:
            print(f"MISSING {tool}: {dest}")
            problems += 1
            continue
        if args.dry_run:
            print(f"WOULD {mode.upper()} {tool}: {dest}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if mode == "link":
            dest.symlink_to(SOURCE, target_is_directory=True)
        else:
            dest.mkdir()
            for name in FILES:
                target = dest / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(SOURCE / name, target)
            (dest / MARKER).write_text(json.dumps({"files": expected}, indent=2) + "\n", encoding="utf-8")
        print(f"INSTALLED {tool}: {dest} ({mode})")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
