"""Tests for marketplace and plugin scaffolding."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from guild._scaffold import add_plugin, init_marketplace, remove_plugin


class TestInitMarketplace:
    def test_creates_structure(self, tmp_path: Path):
        mp = tmp_path / "my-tools"
        init_marketplace(mp, name="my-tools", owner="James")

        assert (mp / "guild.toml").exists()
        assert (mp / "plugins").is_dir()
        assert (mp / "README.md").exists()
        assert (mp / ".gitignore").exists()
        assert (mp / ".github" / "workflows" / "validate.yml").exists()
        assert (mp / ".github" / "workflows" / "release.yml").exists()
        assert (mp / "marketplace.json").exists()

    def test_guild_toml_content(self, tmp_path: Path):
        mp = tmp_path / "test-mp"
        init_marketplace(mp, name="test-mp", owner="Test", email="t@example.com")

        content = (mp / "guild.toml").read_text()
        assert 'name = "test-mp"' in content
        assert 'owner = "Test"' in content
        assert 'owner_email = "t@example.com"' in content

    def test_marketplace_json_valid(self, tmp_path: Path):
        mp = tmp_path / "tools"
        init_marketplace(mp, name="tools", owner="J")

        data = json.loads((mp / "marketplace.json").read_text())
        assert data["name"] == "tools"
        assert data["owner"]["name"] == "J"
        assert data["plugins"] == []

    def test_name_defaults_to_dirname(self, tmp_path: Path):
        mp = tmp_path / "my-cool-marketplace"
        init_marketplace(mp, owner="J")

        data = json.loads((mp / "marketplace.json").read_text())
        assert data["name"] == "my-cool-marketplace"

    def test_description_in_output(self, tmp_path: Path):
        mp = tmp_path / "tools"
        init_marketplace(mp, name="tools", owner="J", description="Dev tools")

        data = json.loads((mp / "marketplace.json").read_text())
        assert data["metadata"]["description"] == "Dev tools"

    def test_idempotent_on_existing_dir(self, tmp_path: Path):
        mp = tmp_path / "tools"
        mp.mkdir()
        init_marketplace(mp, name="tools", owner="J")
        assert (mp / "guild.toml").exists()


class TestAddPlugin:
    def test_creates_structure(self, tmp_path: Path):
        init_marketplace(tmp_path / "mp", name="mp", owner="J")
        ws = tmp_path / "mp"

        plugin_dir = add_plugin(ws, "code-review", description="Review code")

        assert plugin_dir == ws / "plugins" / "code-review"
        assert (plugin_dir / "plugin.toml").exists()
        assert (plugin_dir / "CLAUDE.md").exists()
        assert (plugin_dir / "skills").is_dir()

    def test_plugin_toml_content(self, tmp_path: Path):
        init_marketplace(tmp_path / "mp", name="mp", owner="J")
        ws = tmp_path / "mp"
        add_plugin(ws, "review", description="Review code")

        content = (ws / "plugins" / "review" / "plugin.toml").read_text()
        assert 'name = "review"' in content
        assert 'version = "0.1.0"' in content
        assert 'description = "Review code"' in content

    def test_raises_on_duplicate(self, tmp_path: Path):
        init_marketplace(tmp_path / "mp", name="mp", owner="J")
        ws = tmp_path / "mp"
        add_plugin(ws, "review")

        with pytest.raises(FileExistsError):
            add_plugin(ws, "review")


class TestRemovePlugin:
    def test_removes_directory(self, tmp_path: Path):
        init_marketplace(tmp_path / "mp", name="mp", owner="J")
        ws = tmp_path / "mp"
        add_plugin(ws, "review")
        assert (ws / "plugins" / "review").exists()

        assert remove_plugin(ws, "review") is True
        assert not (ws / "plugins" / "review").exists()

    def test_returns_false_if_missing(self, tmp_path: Path):
        init_marketplace(tmp_path / "mp", name="mp", owner="J")
        assert remove_plugin(tmp_path / "mp", "nonexistent") is False
