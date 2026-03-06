"""Tests for data models."""

from __future__ import annotations

from guild._models import (
    ExternalSource,
    GuildConfig,
    PluginMeta,
    ValidationMessage,
    ValidationReport,
)


class TestPluginMeta:
    def test_basic(self):
        m = PluginMeta(name="review", version="1.0.0", description="Code review")
        assert m.name == "review"
        assert m.version == "1.0.0"
        assert m.description == "Code review"

    def test_default_description(self):
        m = PluginMeta(name="x", version="0.1.0")
        assert m.description == ""


class TestExternalSource:
    def test_github_to_marketplace(self):
        ext = ExternalSource(
            name="helper",
            source_type="github",
            fields={"repo": "acme/helper", "ref": "v1.0"},
        )
        d = ext.to_marketplace_source()
        assert d == {"source": "github", "repo": "acme/helper", "ref": "v1.0"}

    def test_npm_to_marketplace(self):
        ext = ExternalSource(
            name="linter",
            source_type="npm",
            fields={"package": "@acme/linter"},
        )
        d = ext.to_marketplace_source()
        assert d == {"source": "npm", "package": "@acme/linter"}


class TestGuildConfig:
    def test_minimal(self):
        c = GuildConfig(name="my-tools", owner="James")
        assert c.name == "my-tools"
        assert c.owner == "James"
        assert c.externals == ()
        assert c.owner_email is None
        assert c.description is None

    def test_full(self):
        ext = ExternalSource(name="x", source_type="github", fields={"repo": "a/b"})
        c = GuildConfig(
            name="tools",
            owner="J",
            owner_email="j@example.com",
            description="Dev tools",
            externals=(ext,),
        )
        assert c.owner_email == "j@example.com"
        assert len(c.externals) == 1


class TestValidationMessage:
    def test_str(self):
        msg = ValidationMessage("error", "guild.toml", "Missing name.")
        assert str(msg) == "[ERROR] guild.toml: Missing name."


class TestValidationReport:
    def test_empty_is_ok(self):
        r = ValidationReport()
        assert r.ok
        assert r.errors == ()
        assert r.warnings == ()
        assert "No issues" in r.summary()

    def test_warnings_only_is_ok(self):
        r = ValidationReport(messages=(ValidationMessage("warning", "x", "minor"),))
        assert r.ok
        assert len(r.warnings) == 1

    def test_errors_not_ok(self):
        r = ValidationReport(
            messages=(
                ValidationMessage("error", "a", "bad"),
                ValidationMessage("warning", "b", "meh"),
            )
        )
        assert not r.ok
        assert len(r.errors) == 1
        assert len(r.warnings) == 1
        assert "1 error" in r.summary()
        assert "1 warning" in r.summary()

    def test_summary_plurals(self):
        r = ValidationReport(
            messages=(
                ValidationMessage("error", "a", "x"),
                ValidationMessage("error", "b", "y"),
            )
        )
        assert "2 errors" in r.summary()
