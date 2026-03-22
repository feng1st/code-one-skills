#!/usr/bin/env python3
"""Install / uninstall Code One Skills."""

import argparse
import json
import shutil
import sys
from pathlib import Path

PACKAGE_NAME = "code-one-skills"
MANIFEST_FILE = f".{PACKAGE_NAME}.json"

# Entries to install, relative to the repository root.
# Each entry can be a directory (e.g. "skills/topic-open") or a single file
# (e.g. "commands/foo.md").  The same relative path is used at the destination.
ENTRIES = [
    "skills/topic-open",
    "skills/topic-save",
]

# ── target definitions ────────────────────────────────────────────────


def _home() -> Path:
    return Path.home()


TARGETS = {
    "claude": {
        "dir": lambda: _home() / ".claude",
        "desc": "Claude Code, Cursor, OpenCode",
    },
    "codex": {
        "dir": lambda: _home() / ".codex",
        "desc": "Codex, Cursor",
    },
    "cursor": {
        "dir": lambda: _home() / ".cursor",
        "desc": "Cursor",
    },
    "opencode": {
        "dir": lambda: _home() / ".config" / "opencode",
        "desc": "OpenCode",
    },
}

# ── helpers ───────────────────────────────────────────────────────────


def repo_root() -> Path:
    return Path(__file__).resolve().parent


def abort(msg: str) -> None:
    print(f"Error: {msg}")
    sys.exit(1)


def copy_entry(src: Path, dst: Path) -> Path | None:
    """Copy a file or directory from *src* to *dst*."""
    if src.is_dir():
        if dst.exists():
            print(f"  Removing existing: {dst}")
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    elif src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            print(f"  Removing existing: {dst}")
            dst.unlink()
        shutil.copy2(src, dst)
    else:
        print(f"  WARN: source not found, skipping: {src}")
        return None
    return dst


def remove_entry(p: Path) -> None:
    """Remove a file or directory."""
    if not p.exists():
        print(f"  Already gone: {p}")
        return
    print(f"  Removing: {p}")
    if p.is_dir():
        shutil.rmtree(p)
    else:
        p.unlink()


# ── install ───────────────────────────────────────────────────────────


def install(target: str) -> None:
    cfg = TARGETS[target]
    tool_dir: Path = cfg["dir"]()

    print(f"Installing to: {tool_dir}")

    # Check the tool directory exists (not a sub-path — the tool itself)
    if not tool_dir.exists():
        abort(
            f"{tool_dir} does not exist.\n"
            f"  Please install the target tool first ({cfg['desc']})."
        )

    # Clean previous installation based on manifest to avoid stale files
    manifest = tool_dir / MANIFEST_FILE
    if manifest.exists():
        old_data = json.loads(manifest.read_text(encoding="utf-8"))
        for rel in old_data.get("files", []):
            remove_entry(tool_dir / rel)
        manifest.unlink()

    root = repo_root()
    installed: list[str] = []

    for entry in ENTRIES:
        src = root / entry
        dst = tool_dir / entry
        result = copy_entry(src, dst)
        if result is not None:
            print(f"  Copied: {entry} -> {dst}")
            installed.append(entry)

    # Write manifest
    manifest = tool_dir / MANIFEST_FILE
    manifest_data = {
        "name": PACKAGE_NAME,
        "files": installed,
    }
    manifest.write_text(json.dumps(manifest_data, indent=2) + "\n", encoding="utf-8")
    print(f"  Manifest: {manifest}")
    print("Done.")


# ── uninstall ─────────────────────────────────────────────────────────


def uninstall(target: str) -> None:
    cfg = TARGETS[target]
    tool_dir: Path = cfg["dir"]()
    manifest = tool_dir / MANIFEST_FILE

    print(f"Uninstalling from: {tool_dir}")

    if not manifest.exists():
        abort(f"Manifest not found: {manifest}\n  Nothing to uninstall.")

    data = json.loads(manifest.read_text(encoding="utf-8"))
    files: list[str] = data.get("files", [])

    for rel in files:
        remove_entry(tool_dir / rel)

    manifest.unlink()
    print(f"  Removed manifest: {manifest}")
    print("Done.")


# ── CLI ───────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    target_lines = "\n".join(
        f"  {name:<12} {cfg['dir']()}/    {cfg['desc']}"
        for name, cfg in TARGETS.items()
    )

    epilog = (
        "targets:\n"
        f"{target_lines}\n"
        "\n"
        "examples:\n"
        "  python install.py            Install to ~/.claude/ (default)\n"
        "  python install.py -i codex   Install to ~/.codex/\n"
        "  python install.py -r claude  Uninstall from ~/.claude/"
    )

    parser = argparse.ArgumentParser(
        description="Install / uninstall Code One Skills.",
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="claude",
        choices=TARGETS.keys(),
        help="target tool (default: claude)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-i",
        "--install",
        action="store_true",
        default=True,
        help="install skills to the target (default action)",
    )
    group.add_argument(
        "-r",
        "--remove",
        action="store_true",
        help="uninstall skills from the target",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.remove:
        uninstall(args.target)
    else:
        install(args.target)


if __name__ == "__main__":
    main()
