"""Marketplace validation rules."""

from __future__ import annotations

from pathlib import Path

from guild._config import is_kebab_case, load_guild_config, load_plugin_meta
from guild._models import ExternalSource, ValidationMessage, ValidationReport


def validate(workspace: Path) -> ValidationReport:
    """Run all validation checks against the marketplace at *workspace*.

    Returns a :class:`ValidationReport` with errors and warnings.
    """
    messages: list[ValidationMessage] = []
    messages.extend(_check_guild_toml(workspace))

    # If guild.toml doesn't parse, remaining checks are meaningless
    if any(m.level == "error" for m in messages):
        return ValidationReport(messages=tuple(messages))

    config = load_guild_config(workspace)
    messages.extend(_check_plugins_dir(workspace))
    messages.extend(_check_local_plugins(workspace, config.name))
    messages.extend(_check_externals(config.externals))
    messages.extend(_check_marketplace_json(workspace))

    return ValidationReport(messages=tuple(messages))


# ------------------------------------------------------------------
# Individual checks
# ------------------------------------------------------------------


def _check_guild_toml(workspace: Path) -> list[ValidationMessage]:
    msgs: list[ValidationMessage] = []
    path = workspace / "guild.toml"

    if not path.exists():
        msgs.append(ValidationMessage("error", "guild.toml", "File not found."))
        return msgs

    try:
        config = load_guild_config(workspace)
    except Exception as exc:
        msgs.append(ValidationMessage("error", "guild.toml", f"Failed to parse: {exc}"))
        return msgs

    if not config.name:
        msgs.append(ValidationMessage("error", "guild.toml", "marketplace.name is required."))
    elif not is_kebab_case(config.name):
        msgs.append(
            ValidationMessage(
                "error",
                "guild.toml",
                f"marketplace.name '{config.name}' must be kebab-case.",
            )
        )

    if not config.owner:
        msgs.append(ValidationMessage("error", "guild.toml", "marketplace.owner is required."))

    return msgs


def _check_plugins_dir(workspace: Path) -> list[ValidationMessage]:
    msgs: list[ValidationMessage] = []
    plugins_dir = workspace / "plugins"

    if not plugins_dir.is_dir():
        msgs.append(
            ValidationMessage("warning", "plugins/", "Directory not found. No local plugins.")
        )
        return msgs

    for entry in sorted(plugins_dir.iterdir()):
        if entry.is_file():
            msgs.append(
                ValidationMessage(
                    "warning",
                    f"plugins/{entry.name}",
                    "Unexpected file in plugins directory (expected directories only).",
                )
            )
        elif entry.is_dir() and not (entry / "plugin.toml").exists():
            msgs.append(
                ValidationMessage(
                    "error",
                    f"plugins/{entry.name}/",
                    "Directory missing plugin.toml.",
                )
            )

    return msgs


def _check_local_plugins(workspace: Path, marketplace_name: str) -> list[ValidationMessage]:
    msgs: list[ValidationMessage] = []
    plugins_dir = workspace / "plugins"

    if not plugins_dir.is_dir():
        return msgs

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir() or not (plugin_dir / "plugin.toml").exists():
            continue

        rel = f"plugins/{plugin_dir.name}"

        # Parse plugin.toml
        try:
            meta = load_plugin_meta(plugin_dir)
        except Exception as exc:
            msgs.append(ValidationMessage("error", f"{rel}/plugin.toml", f"Failed to parse: {exc}"))
            continue

        # Name must be kebab-case
        if not is_kebab_case(meta.name):
            msgs.append(
                ValidationMessage(
                    "error",
                    f"{rel}/plugin.toml",
                    f"Plugin name '{meta.name}' must be kebab-case.",
                )
            )

        # Directory name must match plugin name
        if plugin_dir.name != meta.name:
            msgs.append(
                ValidationMessage(
                    "error",
                    f"{rel}/plugin.toml",
                    f"Directory name '{plugin_dir.name}' does not match plugin name '{meta.name}'.",
                )
            )

        # Version required
        if not meta.version:
            msgs.append(
                ValidationMessage("error", f"{rel}/plugin.toml", "Plugin version is required.")
            )

        # CLAUDE.md mandatory
        if not (plugin_dir / "CLAUDE.md").exists():
            msgs.append(
                ValidationMessage(
                    "error", f"{rel}/", "Missing CLAUDE.md (required for every plugin)."
                )
            )

        # Skills directory checks
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            for item in sorted(skills_dir.iterdir()):
                if item.is_dir():
                    msgs.append(
                        ValidationMessage(
                            "error",
                            f"{rel}/skills/{item.name}/",
                            "Subdirectories not allowed in skills/.",
                        )
                    )
                elif item.suffix != ".md":
                    msgs.append(
                        ValidationMessage(
                            "error",
                            f"{rel}/skills/{item.name}",
                            f"Skill files must be .md (found {item.suffix}).",
                        )
                    )

    return msgs


def _check_externals(externals: tuple[ExternalSource, ...]) -> list[ValidationMessage]:
    msgs: list[ValidationMessage] = []
    valid_sources = {"github", "url", "git-subdir", "npm", "pip"}

    for ext in externals:
        loc = f"guild.toml [external.{ext.name}]"

        if not is_kebab_case(ext.name):
            msgs.append(
                ValidationMessage("error", loc, f"External name '{ext.name}' must be kebab-case.")
            )

        if ext.source_type not in valid_sources:
            msgs.append(
                ValidationMessage(
                    "error",
                    loc,
                    f"Unknown source type '{ext.source_type}'. "
                    f"Valid: {', '.join(sorted(valid_sources))}.",
                )
            )
            continue

        # Source-specific required fields
        if ext.source_type == "github" and "repo" not in ext.fields:
            msgs.append(ValidationMessage("error", loc, "GitHub source requires 'repo' field."))
        elif ext.source_type == "url" and "url" not in ext.fields:
            msgs.append(ValidationMessage("error", loc, "URL source requires 'url' field."))
        elif ext.source_type == "git-subdir":
            if "url" not in ext.fields:
                msgs.append(
                    ValidationMessage("error", loc, "git-subdir source requires 'url' field.")
                )
            if "path" not in ext.fields:
                msgs.append(
                    ValidationMessage("error", loc, "git-subdir source requires 'path' field.")
                )
        elif ext.source_type in ("npm", "pip") and "package" not in ext.fields:
            msgs.append(
                ValidationMessage(
                    "error",
                    loc,
                    f"{ext.source_type} source requires 'package' field.",
                )
            )

    return msgs


def _check_marketplace_json(workspace: Path) -> list[ValidationMessage]:
    msgs: list[ValidationMessage] = []
    mp_path = workspace / "marketplace.json"

    if not mp_path.exists():
        msgs.append(
            ValidationMessage(
                "warning",
                "marketplace.json",
                "Not found. Run `guild build` to generate it.",
            )
        )

    return msgs
