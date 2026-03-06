"""Tests for plugin installation."""

from __future__ import annotations

import os
from pathlib import Path

from guild._cli import main
from guild._install import install_plugin


class TestInstallPlugin:
    def test_copies_plugin(self, tmp_path: Path):
        dest = install_plugin(tmp_path)
        assert dest == tmp_path / "guild-skills"
        assert (dest / "plugin.toml").exists()
        assert (dest / "CLAUDE.md").exists()
        assert (dest / "skills").is_dir()
        assert (dest / "skills" / "guild-oracle.md").exists()
        assert (dest / "skills" / "create-plugin.md").exists()
        assert (dest / "skills" / "write-skill.md").exists()
        assert (dest / "skills" / "update-plugin.md").exists()
        assert (dest / "skills" / "review-marketplace.md").exists()

    def test_overwrites_existing(self, tmp_path: Path):
        dest = install_plugin(tmp_path)
        # Write a marker to prove overwrite
        (dest / "marker.txt").write_text("old")
        dest2 = install_plugin(tmp_path)
        assert dest2 == dest
        assert not (dest2 / "marker.txt").exists()

    def test_creates_target_dir(self, tmp_path: Path):
        target = tmp_path / "nested" / "deep"
        target.mkdir(parents=True)
        dest = install_plugin(target)
        assert dest.is_dir()


class TestCliSetupPlugin:
    def test_explicit_target(self, tmp_path: Path):
        target = tmp_path / "my-plugins"
        target.mkdir()
        rc = main(["setup-plugin", str(target)])
        assert rc == 0
        assert (target / "guild-skills" / "CLAUDE.md").exists()

    def test_defaults_to_marketplace_plugins(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["setup-plugin"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0
        assert (ws / "plugins" / "guild-skills" / "CLAUDE.md").exists()

    def test_defaults_to_dot_claude_outside_marketplace(self, tmp_path: Path):
        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            rc = main(["setup-plugin"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0
        assert (tmp_path / ".claude" / "plugins" / "guild-skills" / "CLAUDE.md").exists()
