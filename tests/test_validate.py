"""Tests for marketplace validation."""

from __future__ import annotations

from pathlib import Path

from guild._scaffold import add_plugin, init_marketplace
from guild._validate import validate


class TestValidateHappy:
    def test_valid_empty_marketplace(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        report = validate(ws)
        assert report.ok

    def test_valid_with_plugin(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        add_plugin(ws, "review", description="Review code")
        (ws / "plugins" / "review" / "skills" / "review.md").write_text("# Review")

        # Rebuild so marketplace.json is fresh
        from guild._build import build_and_write

        build_and_write(ws)

        report = validate(ws)
        assert report.ok, [str(m) for m in report.messages]


class TestValidateGuildToml:
    def test_missing_guild_toml(self, tmp_path: Path):
        report = validate(tmp_path)
        assert not report.ok
        assert any("guild.toml" in m.path and "not found" in m.message for m in report.errors)

    def test_invalid_toml(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text("not valid toml {{{{")
        report = validate(tmp_path)
        assert not report.ok

    def test_non_kebab_name(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text('[marketplace]\nname = "MyTools"\nowner = "J"\n')
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        assert not report.ok
        assert any("kebab-case" in m.message for m in report.errors)

    def test_missing_owner(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text('[marketplace]\nname = "tools"\nowner = ""\n')
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        assert not report.ok
        assert any("owner" in m.message for m in report.errors)


class TestValidatePlugins:
    def test_dir_without_toml(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        (ws / "plugins" / "orphan").mkdir()

        report = validate(ws)
        assert any("missing plugin.toml" in m.message.lower() for m in report.errors)

    def test_file_in_plugins_dir(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        (ws / "plugins" / "stray.txt").write_text("oops")

        report = validate(ws)
        assert any("Unexpected file" in m.message for m in report.warnings)

    def test_name_mismatch(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        plugin_dir = ws / "plugins" / "review"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "plugin.toml").write_text('[plugin]\nname = "wrong-name"\nversion = "1.0"\n')
        (plugin_dir / "CLAUDE.md").write_text("# Wrong")

        report = validate(ws)
        assert any("does not match" in m.message for m in report.errors)

    def test_non_kebab_plugin_name(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        plugin_dir = ws / "plugins" / "BadName"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "plugin.toml").write_text('[plugin]\nname = "BadName"\nversion = "1.0"\n')
        (plugin_dir / "CLAUDE.md").write_text("# Bad")

        report = validate(ws)
        assert any("kebab-case" in m.message for m in report.errors)

    def test_missing_claude_md(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        plugin_dir = ws / "plugins" / "review"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "plugin.toml").write_text('[plugin]\nname = "review"\nversion = "1.0"\n')

        report = validate(ws)
        assert any("CLAUDE.md" in m.message for m in report.errors)

    def test_non_md_skill_file(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        add_plugin(ws, "review")
        (ws / "plugins" / "review" / "skills" / "bad.py").write_text("x")

        report = validate(ws)
        assert any(".md" in m.message for m in report.errors)

    def test_skill_subdirectory(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        add_plugin(ws, "review")
        (ws / "plugins" / "review" / "skills" / "nested").mkdir()

        report = validate(ws)
        assert any("Subdirectories" in m.message for m in report.errors)


class TestValidateExternals:
    def test_invalid_source_type(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n[external.bad]\nsource = "ftp"\n'
        )
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        assert any("Unknown source type" in m.message for m in report.errors)

    def test_github_missing_repo(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n[external.helper]\nsource = "github"\n'
        )
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        assert any("repo" in m.message for m in report.errors)

    def test_npm_missing_package(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n[external.linter]\nsource = "npm"\n'
        )
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        assert any("package" in m.message for m in report.errors)

    def test_git_subdir_missing_fields(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n[external.mono]\nsource = "git-subdir"\n'
        )
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        errors = [m.message for m in report.errors]
        assert any("url" in e for e in errors)
        assert any("path" in e for e in errors)

    def test_non_kebab_external_name(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n'
            '[external.BadName]\nsource = "github"\nrepo = "a/b"\n'
        )
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        assert any("kebab-case" in m.message for m in report.errors)

    def test_valid_external(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n'
            '[external.helper]\nsource = "github"\nrepo = "acme/helper"\n'
        )
        (tmp_path / "plugins").mkdir()
        (tmp_path / "marketplace.json").write_text("{}")
        report = validate(tmp_path)
        assert report.ok


class TestValidateMarketplaceJson:
    def test_missing_marketplace_json(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text('[marketplace]\nname = "mp"\nowner = "J"\n')
        (tmp_path / "plugins").mkdir()
        report = validate(tmp_path)
        assert any("marketplace.json" in m.path for m in report.warnings)
