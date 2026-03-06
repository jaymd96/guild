"""Install guild's bundled plugin into a project."""

from __future__ import annotations

import importlib.resources
import shutil
from pathlib import Path


def _bundled_plugin_root() -> Path:
    """Return the path to the bundled guild-skills plugin directory."""
    # The plugin ships inside the package at guild/_plugin/guild-skills/
    ref = importlib.resources.files("guild") / "_plugin" / "guild-skills"
    # resources.files returns a Traversable; for a real filesystem package
    # this is already a Path
    return Path(str(ref))


def install_plugin(target: Path) -> Path:
    """Copy the bundled guild-skills plugin into *target*.

    *target* is typically a ``.claude/plugins/`` or ``plugins/`` directory.
    Creates ``guild-skills/`` inside *target* with CLAUDE.md, plugin.toml,
    and skills/.

    Returns the path to the installed plugin directory.
    """
    src = _bundled_plugin_root()
    if not src.is_dir():
        msg = f"Bundled plugin not found at {src}"
        raise FileNotFoundError(msg)

    dest = target / "guild-skills"
    if dest.exists():
        shutil.rmtree(dest)

    shutil.copytree(src, dest)
    return dest
