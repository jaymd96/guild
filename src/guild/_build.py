"""Build marketplace.json and README from source files."""

from __future__ import annotations

import json
from pathlib import Path

from guild._config import discover_local_plugins, load_guild_config


def build_marketplace(workspace: Path) -> dict:
    """Generate the marketplace dict from ``guild.toml`` and local plugins.

    Returns a dict matching the Claude Code marketplace.json schema.
    """
    config = load_guild_config(workspace)
    plugins: list[dict] = []

    # Local plugins
    for _plugin_dir, meta in discover_local_plugins(workspace):
        entry: dict = {
            "name": meta.name,
            "source": f"./plugins/{meta.name}",
        }
        if meta.description:
            entry["description"] = meta.description
        if meta.version:
            entry["version"] = meta.version
        plugins.append(entry)

    # External plugins
    for ext in config.externals:
        entry = {
            "name": ext.name,
            "source": ext.to_marketplace_source(),
        }
        plugins.append(entry)

    result: dict = {
        "name": config.name,
        "owner": {"name": config.owner},
        "plugins": plugins,
    }
    if config.owner_email:
        result["owner"]["email"] = config.owner_email
    if config.description:
        result.setdefault("metadata", {})["description"] = config.description

    return result


def build_readme(workspace: Path) -> str:
    """Generate a README.md catalogue from the marketplace sources."""
    config = load_guild_config(workspace)
    local = discover_local_plugins(workspace)

    lines = [
        f"# {config.name}",
        "",
    ]
    if config.description:
        lines.append(config.description)
        lines.append("")

    lines.append(f"A Claude Code plugin marketplace maintained by **{config.owner}**.")
    lines.append("")

    if local or config.externals:
        lines.append("## Plugins")
        lines.append("")
        lines.append("| Plugin | Version | Source | Description |")
        lines.append("|--------|---------|--------|-------------|")

        for _dir, meta in local:
            lines.append(f"| {meta.name} | {meta.version} | local | {meta.description} |")

        for ext in config.externals:
            source_label = ext.source_type
            if ext.source_type == "github":
                source_label = ext.fields.get("repo", "github")
            elif ext.source_type == "npm":
                source_label = ext.fields.get("package", "npm")
            elif ext.source_type == "pip":
                source_label = ext.fields.get("package", "pip")
            lines.append(f"| {ext.name} | — | {source_label} | — |")

        lines.append("")
    else:
        lines.append("No plugins yet. Run `guild add <name>` to create one.")
        lines.append("")

    lines.append("## Usage")
    lines.append("")
    lines.append("```python")
    lines.append("from psclaude import PsClaude")
    lines.append("")
    lines.append("client = PsClaude(")
    lines.append(f'    marketplaces=["<owner>/{config.name}"],')
    if local:
        first = local[0][1].name
        lines.append(f'    install=["{first}@{config.name}"],')
    lines.append(")")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


def build_and_write(workspace: Path) -> tuple[Path, Path]:
    """Build and write both ``marketplace.json`` and ``README.md``.

    Returns paths to both written files.
    """
    mp_data = build_marketplace(workspace)
    mp_path = workspace / "marketplace.json"
    mp_path.write_text(json.dumps(mp_data, indent=2) + "\n")

    readme_text = build_readme(workspace)
    readme_path = workspace / "README.md"
    readme_path.write_text(readme_text)

    return mp_path, readme_path
