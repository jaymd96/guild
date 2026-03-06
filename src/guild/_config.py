"""Guild and plugin configuration loading."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from guild._models import ExternalSource, GuildConfig, PluginMeta

_KEBAB_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def is_kebab_case(name: str) -> bool:
    return _KEBAB_RE.match(name) is not None


def load_guild_config(workspace: Path) -> GuildConfig:
    """Parse ``guild.toml`` from *workspace*."""
    path = workspace / "guild.toml"
    with open(path, "rb") as f:
        data = tomllib.load(f)

    mp = data.get("marketplace", {})

    externals: list[ExternalSource] = []
    for name, ext_data in data.get("external", {}).items():
        ext_data = dict(ext_data)  # copy so we can pop
        source_type = ext_data.pop("source")
        externals.append(ExternalSource(name=name, source_type=source_type, fields=ext_data))

    return GuildConfig(
        name=mp["name"],
        owner=mp["owner"],
        owner_email=mp.get("owner_email"),
        description=mp.get("description"),
        externals=tuple(externals),
    )


def load_plugin_meta(plugin_dir: Path) -> PluginMeta:
    """Parse ``plugin.toml`` from a plugin directory."""
    path = plugin_dir / "plugin.toml"
    with open(path, "rb") as f:
        data = tomllib.load(f)

    p = data["plugin"]
    return PluginMeta(
        name=p["name"],
        version=p["version"],
        description=p.get("description", ""),
    )


def discover_local_plugins(workspace: Path) -> list[tuple[Path, PluginMeta]]:
    """Find all local plugins under ``plugins/`` with valid ``plugin.toml``."""
    plugins_dir = workspace / "plugins"
    if not plugins_dir.is_dir():
        return []

    results: list[tuple[Path, PluginMeta]] = []
    for d in sorted(plugins_dir.iterdir()):
        if d.is_dir() and (d / "plugin.toml").exists():
            meta = load_plugin_meta(d)
            results.append((d, meta))
    return results
