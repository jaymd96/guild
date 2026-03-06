"""guild — scaffold and manage Claude Code plugin marketplaces."""

from guild.__about__ import __version__
from guild._build import build_and_write, build_marketplace, build_readme
from guild._config import discover_local_plugins, load_guild_config, load_plugin_meta
from guild._install import install_plugin
from guild._models import (
    ExternalSource,
    GuildConfig,
    PluginMeta,
    ValidationMessage,
    ValidationReport,
)
from guild._scaffold import add_plugin, init_marketplace, remove_plugin
from guild._validate import validate

__all__ = [
    "ExternalSource",
    "GuildConfig",
    "PluginMeta",
    "ValidationMessage",
    "ValidationReport",
    "__version__",
    "add_plugin",
    "build_and_write",
    "build_marketplace",
    "build_readme",
    "discover_local_plugins",
    "init_marketplace",
    "install_plugin",
    "load_guild_config",
    "load_plugin_meta",
    "remove_plugin",
    "validate",
]
