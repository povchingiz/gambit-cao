"""Unit tests for GAMBIT workspace resolution and auto-migration patch (wcao <-> wgambit)."""
import os
import tempfile
from pathlib import Path

from run.cao_lib import patch_workspace_migration, resolve_workspace_dir
from run.gambit_migrate import migrate_project_workspace


def test_resolve_fresh_project_creates_wgambit():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        ws = resolve_workspace_dir(root, create=True, auto_patch=True)
        assert ws.name == "wgambit"
        assert ws.exists()
        assert (root / "wcao").exists()
        assert (root / "wcao").is_symlink()
        assert os.readlink(root / "wcao") == "wgambit"


def test_migration_patch_upgrades_wcao_to_wgambit():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        wcao = root / "wcao"
        wcao.mkdir()
        (wcao / "plans").mkdir()
        (wcao / "plans" / "now.md").write_text("# Active Plan\n- [ ] Task 1")
        (wcao / "design").mkdir()
        (wcao / "design" / "architecture.mmd").write_text("sequenceDiagram\n  A->>B: ping")

        # Run migration patch
        canonical = patch_workspace_migration(root)
        assert canonical.name == "wgambit"
        assert (root / "wgambit").exists()
        assert not (root / "wgambit").is_symlink()
        assert (root / "wcao").is_symlink()
        assert os.readlink(root / "wcao") == "wgambit"

        # Verify content accessibility from both paths
        assert (root / "wgambit" / "design" / "architecture.mmd").read_text() == "sequenceDiagram\n  A->>B: ping"
        assert (root / "wcao" / "design" / "architecture.mmd").read_text() == "sequenceDiagram\n  A->>B: ping"
        assert "- [ ] Task 1" in (root / "wcao" / "plans" / "now.md").read_text()


def test_migrate_project_workspace_summary():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        wcao = root / "wcao"
        wcao.mkdir()
        (wcao / "design").mkdir()
        (wcao / "design" / "seq.mmd").write_text("sequenceDiagram")

        summary = migrate_project_workspace(root)
        assert summary["status"] == "migrated (wcao -> wgambit + symlink)"
        assert summary["workspace"] == "wgambit"
        assert summary["diagrams_count"] == "1"
