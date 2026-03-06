"""Tests for the CLI interface."""

from __future__ import annotations

import json
import os
from pathlib import Path

from guild._cli import main


class TestCliInit:
    def test_init_creates_marketplace(self, tmp_path: Path):
        target = tmp_path / "my-tools"
        rc = main(["init", str(target), "--owner", "James"])
        assert rc == 0
        assert (target / "guild.toml").exists()
        assert (target / "marketplace.json").exists()

    def test_init_with_all_options(self, tmp_path: Path):
        target = tmp_path / "tools"
        rc = main(
            [
                "init",
                str(target),
                "--name",
                "tools",
                "--owner",
                "J",
                "--email",
                "j@example.com",
                "--description",
                "Dev tools",
            ]
        )
        assert rc == 0
        data = json.loads((target / "marketplace.json").read_text())
        assert data["owner"]["email"] == "j@example.com"

    def test_init_rejects_non_kebab(self, tmp_path: Path):
        target = tmp_path / "BadName"
        rc = main(["init", str(target), "--name", "BadName"])
        assert rc == 1


class TestCliAdd:
    def test_add_plugin(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["add", "review", "--description", "Code review"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0
        assert (ws / "plugins" / "review" / "plugin.toml").exists()

    def test_add_rejects_non_kebab(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["add", "BadName"])
        finally:
            os.chdir(old_cwd)

        assert rc == 1

    def test_add_rebuilds_marketplace(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            main(["add", "review"])
        finally:
            os.chdir(old_cwd)

        data = json.loads((ws / "marketplace.json").read_text())
        assert len(data["plugins"]) == 1


class TestCliRemove:
    def test_remove_plugin(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            main(["add", "review"])
            assert (ws / "plugins" / "review").exists()
            rc = main(["remove", "review"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0
        assert not (ws / "plugins" / "review").exists()

    def test_remove_nonexistent(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["remove", "ghost"])
        finally:
            os.chdir(old_cwd)

        assert rc == 1


class TestCliBuild:
    def test_build(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            main(["add", "review"])
            # Delete marketplace.json to prove build regenerates it
            (ws / "marketplace.json").unlink()
            rc = main(["build"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0
        assert (ws / "marketplace.json").exists()


class TestCliValidate:
    def test_valid_marketplace(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["validate"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0

    def test_invalid_marketplace(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])
        (ws / "plugins" / "orphan").mkdir()

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["validate"])
        finally:
            os.chdir(old_cwd)

        assert rc == 1


class TestCliList:
    def test_list_empty(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["list"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0

    def test_list_with_plugins(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            main(["add", "review"])
            rc = main(["list"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0


class TestCliVersion:
    def test_version_bump(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            main(["add", "review"])
            rc = main(["version", "review", "2.0.0"])
        finally:
            os.chdir(old_cwd)

        assert rc == 0
        content = (ws / "plugins" / "review" / "plugin.toml").read_text()
        assert 'version = "2.0.0"' in content

        # marketplace.json should also reflect new version
        data = json.loads((ws / "marketplace.json").read_text())
        assert data["plugins"][0]["version"] == "2.0.0"

    def test_version_nonexistent_plugin(self, tmp_path: Path):
        ws = tmp_path / "mp"
        main(["init", str(ws), "--owner", "J"])

        old_cwd = os.getcwd()
        try:
            os.chdir(ws)
            rc = main(["version", "ghost", "1.0.0"])
        finally:
            os.chdir(old_cwd)

        assert rc == 1


class TestCliMisc:
    def test_no_command_shows_help(self):
        rc = main([])
        assert rc == 0

    def test_version_flag(self):
        rc = main(["--version"])
        assert rc == 0
