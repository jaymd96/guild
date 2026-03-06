"""Data models for guild configuration and validation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PluginMeta:
    """Metadata parsed from a plugin's ``plugin.toml``."""

    name: str
    version: str
    description: str = ""


@dataclass(frozen=True)
class ExternalSource:
    """An external plugin source declared in ``guild.toml``."""

    name: str
    source_type: str
    fields: dict[str, str] = field(default_factory=dict)

    def to_marketplace_source(self) -> dict[str, str]:
        d: dict[str, str] = {"source": self.source_type, **self.fields}
        return d


@dataclass(frozen=True)
class GuildConfig:
    """Parsed ``guild.toml`` configuration."""

    name: str
    owner: str
    owner_email: str | None = None
    description: str | None = None
    externals: tuple[ExternalSource, ...] = ()


@dataclass(frozen=True)
class ValidationMessage:
    """A single validation finding."""

    level: str  # "error" or "warning"
    path: str
    message: str

    def __str__(self) -> str:
        return f"[{self.level.upper()}] {self.path}: {self.message}"


@dataclass(frozen=True)
class ValidationReport:
    """Result of running ``guild validate``."""

    messages: tuple[ValidationMessage, ...] = ()

    @property
    def ok(self) -> bool:
        return not any(m.level == "error" for m in self.messages)

    @property
    def errors(self) -> tuple[ValidationMessage, ...]:
        return tuple(m for m in self.messages if m.level == "error")

    @property
    def warnings(self) -> tuple[ValidationMessage, ...]:
        return tuple(m for m in self.messages if m.level == "warning")

    def summary(self) -> str:
        errs = len(self.errors)
        warns = len(self.warnings)
        if self.ok and warns == 0:
            return "Valid. No issues found."
        parts: list[str] = []
        if errs:
            parts.append(f"{errs} error{'s' if errs != 1 else ''}")
        if warns:
            parts.append(f"{warns} warning{'s' if warns != 1 else ''}")
        return ", ".join(parts) + "."
