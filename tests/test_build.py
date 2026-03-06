"""Tests for marketplace building."""

from __future__ import annotations

import json
from pathlib import Path

from guild._build import build_and_write, build_marketplace, build_readme
from guild._scaffold import add_plugin, init_marketplace


class TestBuildMarketplace:
    def test_empty_marketplace(self, tmp_path: Path):
        init_marketplace(tmp_path / "mp", name="mp", owner="J")
        data = build_marketplace(tmp_path / "mp")
        assert data["name"] == "mp"
        assert data["owner"] == {"name": "J"}
        assert data["plugins"] == []

    def test_with_local_plugin(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        add_plugin(ws, "review", description="Code review")

        data = build_marketplace(ws)
        assert len(data["plugins"]) == 1
        assert data["plugins"][0]["name"] == "review"
        assert data["plugins"][0]["source"] == "./plugins/review"
        assert data["plugins"][0]["description"] == "Code review"

    def test_with_external(self, tmp_path: Path):
        ws = tmp_path / "mp"
        ws.mkdir(parents=True)
        (ws / "plugins").mkdir()
        (ws / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n'
            '[external.helper]\nsource = "github"\nrepo = "acme/helper"\n'
        )

        data = build_marketplace(ws)
        assert len(data["plugins"]) == 1
        assert data["plugins"][0]["name"] == "helper"
        assert data["plugins"][0]["source"] == {
            "source": "github",
            "repo": "acme/helper",
        }

    def test_local_and_external_combined(self, tmp_path: Path):
        ws = tmp_path / "mp"
        ws.mkdir(parents=True)
        (ws / "plugins").mkdir()
        (ws / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n'
            '[external.helper]\nsource = "github"\nrepo = "a/b"\n'
        )
        add_plugin(ws, "local-tool", description="A local tool")

        data = build_marketplace(ws)
        assert len(data["plugins"]) == 2
        names = [p["name"] for p in data["plugins"]]
        assert "local-tool" in names
        assert "helper" in names

    def test_owner_email(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J", email="j@example.com")
        data = build_marketplace(ws)
        assert data["owner"]["email"] == "j@example.com"

    def test_description_in_metadata(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J", description="Tools")
        data = build_marketplace(ws)
        assert data["metadata"]["description"] == "Tools"


class TestBuildReadme:
    def test_empty(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        readme = build_readme(ws)
        assert "# mp" in readme
        assert "No plugins yet" in readme

    def test_with_plugins(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        add_plugin(ws, "review", description="Review code")

        readme = build_readme(ws)
        assert "review" in readme
        assert "## Plugins" in readme
        assert "## Usage" in readme

    def test_includes_external(self, tmp_path: Path):
        ws = tmp_path / "mp"
        ws.mkdir(parents=True)
        (ws / "plugins").mkdir()
        (ws / "guild.toml").write_text(
            '[marketplace]\nname = "mp"\nowner = "J"\n\n'
            '[external.helper]\nsource = "github"\nrepo = "acme/helper"\n'
        )
        readme = build_readme(ws)
        assert "helper" in readme
        assert "acme/helper" in readme


class TestBuildAndWrite:
    def test_writes_both_files(self, tmp_path: Path):
        ws = tmp_path / "mp"
        init_marketplace(ws, name="mp", owner="J")
        add_plugin(ws, "review")

        mp_path, readme_path = build_and_write(ws)

        assert mp_path.exists()
        assert readme_path.exists()
        data = json.loads(mp_path.read_text())
        assert len(data["plugins"]) == 1
