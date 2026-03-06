"""Command-line interface for guild."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from guild._build import build_and_write
from guild._config import discover_local_plugins, is_kebab_case, load_guild_config
from guild._install import install_plugin
from guild._scaffold import add_plugin, init_marketplace, remove_plugin
from guild._validate import validate


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``guild`` CLI."""
    parser = argparse.ArgumentParser(
        prog="guild",
        description="Scaffold and manage Claude Code plugin marketplaces.",
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit.")
    sub = parser.add_subparsers(dest="command")

    # -- init --
    p_init = sub.add_parser("init", help="Scaffold a new marketplace.")
    p_init.add_argument("path", nargs="?", default=".", help="Directory to create.")
    p_init.add_argument("--name", help="Marketplace name (default: directory name).")
    p_init.add_argument("--owner", default="", help="Marketplace owner name.")
    p_init.add_argument("--email", default=None, help="Owner contact email.")
    p_init.add_argument("--description", default=None, help="Marketplace description.")

    # -- add --
    p_add = sub.add_parser("add", help="Add a new local plugin.")
    p_add.add_argument("name", help="Plugin name (kebab-case).")
    p_add.add_argument("--description", default="", help="Plugin description.")

    # -- remove --
    p_rm = sub.add_parser("remove", help="Remove a local plugin.")
    p_rm.add_argument("name", help="Plugin name to remove.")

    # -- build --
    sub.add_parser("build", help="Regenerate marketplace.json and README.md.")

    # -- validate --
    sub.add_parser("validate", help="Validate marketplace structure.")

    # -- list --
    sub.add_parser("list", help="List all plugins.")

    # -- version (subcommand) --
    p_ver = sub.add_parser("version", help="Set a plugin's version.")
    p_ver.add_argument("plugin_name", help="Plugin name.")
    p_ver.add_argument("new_version", help="New version string.")

    # -- setup-plugin --
    p_setup = sub.add_parser(
        "setup-plugin",
        help="Install guild's own skills plugin into a directory.",
    )
    p_setup.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Target directory (default: plugins/ in current marketplace, or .claude/plugins/).",
    )

    args = parser.parse_args(argv)

    if args.version:
        from guild.__about__ import __version__

        print(f"guild {__version__}")
        return 0

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "init":
        return _cmd_init(args)
    if args.command == "add":
        return _cmd_add(args)
    if args.command == "remove":
        return _cmd_remove(args)
    if args.command == "build":
        return _cmd_build()
    if args.command == "validate":
        return _cmd_validate()
    if args.command == "list":
        return _cmd_list()
    if args.command == "version":
        return _cmd_version(args)
    if args.command == "setup-plugin":
        return _cmd_setup_plugin(args)

    parser.print_help()
    return 1


# ------------------------------------------------------------------
# Command implementations
# ------------------------------------------------------------------


def _cmd_init(args: argparse.Namespace) -> int:
    path = Path(args.path).resolve()
    name = args.name or path.name
    if not is_kebab_case(name):
        print(f"Error: marketplace name '{name}' must be kebab-case.", file=sys.stderr)
        return 1

    try:
        result = init_marketplace(
            path,
            name=name,
            owner=args.owner,
            email=args.email,
            description=args.description,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Marketplace '{name}' created at {result}")
    return 0


def _cmd_add(args: argparse.Namespace) -> int:
    if not is_kebab_case(args.name):
        print(f"Error: plugin name '{args.name}' must be kebab-case.", file=sys.stderr)
        return 1

    workspace = _find_workspace()
    if workspace is None:
        return 1

    try:
        plugin_dir = add_plugin(workspace, args.name, description=args.description)
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    # Rebuild after adding
    build_and_write(workspace)
    print(f"Plugin '{args.name}' created at {plugin_dir}")
    return 0


def _cmd_remove(args: argparse.Namespace) -> int:
    workspace = _find_workspace()
    if workspace is None:
        return 1

    # Check if it's an external
    try:
        config = load_guild_config(workspace)
        external_names = {ext.name for ext in config.externals}
    except Exception:
        external_names = set()

    if args.name in external_names:
        print(
            f"'{args.name}' is an external plugin. "
            f"Remove the [external.{args.name}] section from guild.toml "
            f"and run `guild build`.",
            file=sys.stderr,
        )
        return 1

    if not remove_plugin(workspace, args.name):
        print(f"Error: plugin '{args.name}' not found.", file=sys.stderr)
        return 1

    # Rebuild after removal
    build_and_write(workspace)
    print(f"Plugin '{args.name}' removed.")
    return 0


def _cmd_build() -> int:
    workspace = _find_workspace()
    if workspace is None:
        return 1

    try:
        mp_path, readme_path = build_and_write(workspace)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Built {mp_path.name} and {readme_path.name}")
    return 0


def _cmd_validate() -> int:
    workspace = _find_workspace()
    if workspace is None:
        return 1

    report = validate(workspace)

    for msg in report.messages:
        print(msg)

    print()
    print(report.summary())
    return 0 if report.ok else 1


def _cmd_list() -> int:
    workspace = _find_workspace()
    if workspace is None:
        return 1

    try:
        config = load_guild_config(workspace)
        local = discover_local_plugins(workspace)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not local and not config.externals:
        print("No plugins found.")
        return 0

    if local:
        print("Local plugins:")
        for _dir, meta in local:
            desc = f" — {meta.description}" if meta.description else ""
            print(f"  {meta.name} ({meta.version}){desc}")

    if config.externals:
        if local:
            print()
        print("External plugins:")
        for ext in config.externals:
            label = ext.fields.get("repo") or ext.fields.get("package") or ext.fields.get("url", "")
            print(f"  {ext.name} [{ext.source_type}] {label}")

    return 0


def _cmd_version(args: argparse.Namespace) -> int:
    workspace = _find_workspace()
    if workspace is None:
        return 1

    plugin_dir = workspace / "plugins" / args.plugin_name
    toml_path = plugin_dir / "plugin.toml"

    if not toml_path.exists():
        print(f"Error: plugin '{args.plugin_name}' not found.", file=sys.stderr)
        return 1

    content = toml_path.read_text()
    new_content = re.sub(
        r'version\s*=\s*"[^"]*"',
        f'version = "{args.new_version}"',
        content,
        count=1,
    )

    if new_content == content:
        print("Error: could not find version field in plugin.toml.", file=sys.stderr)
        return 1

    toml_path.write_text(new_content)

    # Rebuild
    build_and_write(workspace)
    print(f"Plugin '{args.plugin_name}' version set to {args.new_version}")
    return 0


def _cmd_setup_plugin(args: argparse.Namespace) -> int:
    if args.target is not None:
        target = Path(args.target).resolve()
    else:
        # Prefer plugins/ in current marketplace, fall back to .claude/plugins/
        workspace = _find_workspace(quiet=True)
        if workspace is not None:
            target = workspace / "plugins"
        else:
            target = Path.cwd().resolve() / ".claude" / "plugins"

    target.mkdir(parents=True, exist_ok=True)

    try:
        dest = install_plugin(target)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Installed guild-skills plugin at {dest}")
    return 0


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _find_workspace(*, quiet: bool = False) -> Path | None:
    """Walk up from cwd to find a directory containing ``guild.toml``."""
    current = Path.cwd().resolve()
    while True:
        if (current / "guild.toml").exists():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent

    if not quiet:
        print("Error: guild.toml not found (searched from cwd upward).", file=sys.stderr)
    return None
