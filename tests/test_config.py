"""Tests for configuration loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from guild._config import discover_local_plugins, is_kebab_case, load_guild_config, load_plugin_meta


class TestIsKebabCase:
    def test_valid(self):
        assert is_kebab_case("review")
        assert is_kebab_case("code-review")
        assert is_kebab_case("my-cool-plugin")
        assert is_kebab_case("a1")
        assert is_kebab_case("plugin-v2")

    def test_invalid(self):
        assert not is_kebab_case("CamelCase")
        assert not is_kebab_case("snake_case")
        assert not is_kebab_case("UPPER")
        assert not is_kebab_case("-leading-dash")
        assert not is_kebab_case("trailing-dash-")
        assert not is_kebab_case("double--dash")
        assert not is_kebab_case("")
        assert not is_kebab_case("123")


class TestLoadGuildConfig:
    def test_minimal(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text('[marketplace]\nname = "my-tools"\nowner = "James"\n')
        config = load_guild_config(tmp_path)
        assert config.name == "my-tools"
        assert config.owner == "James"
        assert config.externals == ()

    def test_full(self, tmp_path: Path):
        (tmp_path / "guild.toml").write_text(
            "[marketplace]\n"
            'name = "tools"\n'
            'owner = "J"\n'
            'owner_email = "j@example.com"\n'
            'description = "Dev tools"\n'
            "\n"
            "[external.helper]\n"
            'source = "github"\n'
            'repo = "acme/helper"\n'
            'ref = "v1.0"\n'
            "\n"
            "[external.linter]\n"
            'source = "npm"\n'
            'package = "@acme/linter"\n'
        )
        config = load_guild_config(tmp_path)
        assert config.owner_email == "j@example.com"
        assert config.description == "Dev tools"
        assert len(config.externals) == 2
        assert config.externals[0].name == "helper"
        assert config.externals[0].source_type == "github"
        assert config.externals[0].fields["repo"] == "acme/helper"
        assert config.externals[1].name == "linter"

    def test_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_guild_config(tmp_path)


class TestLoadPluginMeta:
    def test_basic(self, tmp_path: Path):
        (tmp_path / "plugin.toml").write_text(
            '[plugin]\nname = "review"\nversion = "1.0.0"\ndescription = "Code review"\n'
        )
        meta = load_plugin_meta(tmp_path)
        assert meta.name == "review"
        assert meta.version == "1.0.0"
        assert meta.description == "Code review"

    def test_missing_description(self, tmp_path: Path):
        (tmp_path / "plugin.toml").write_text('[plugin]\nname = "x"\nversion = "0.1.0"\n')
        meta = load_plugin_meta(tmp_path)
        assert meta.description == ""


class TestDiscoverLocalPlugins:
    def test_finds_plugins(self, tmp_path: Path):
        plugins = tmp_path / "plugins"
        p1 = plugins / "alpha"
        p2 = plugins / "beta"
        p1.mkdir(parents=True)
        p2.mkdir(parents=True)
        (p1 / "plugin.toml").write_text('[plugin]\nname = "alpha"\nversion = "1.0"\n')
        (p2 / "plugin.toml").write_text('[plugin]\nname = "beta"\nversion = "2.0"\n')

        result = discover_local_plugins(tmp_path)
        assert len(result) == 2
        assert result[0][1].name == "alpha"
        assert result[1][1].name == "beta"

    def test_skips_dirs_without_toml(self, tmp_path: Path):
        plugins = tmp_path / "plugins"
        (plugins / "valid").mkdir(parents=True)
        (plugins / "invalid").mkdir(parents=True)
        (plugins / "valid" / "plugin.toml").write_text(
            '[plugin]\nname = "valid"\nversion = "1.0"\n'
        )

        result = discover_local_plugins(tmp_path)
        assert len(result) == 1

    def test_empty(self, tmp_path: Path):
        assert discover_local_plugins(tmp_path) == []
