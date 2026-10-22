"""Unit tests for GAMBIT CLI (run/gambit and run/gambit_cli.py)."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = REPO_ROOT / "run"
if str(RUN_DIR) not in sys.path:
    sys.path.insert(0, str(RUN_DIR))

import pytest
import gambit_cli


def test_gambit_help_displays_chess_taxonomy(capsys):
    gambit_bin = RUN_DIR / "gambit"
    res = subprocess.run([sys.executable, str(gambit_bin), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "GAMBIT" in res.stdout
    assert "Grandmaster" in res.stdout
    assert "The Rook" in res.stdout
    assert "The Knights" in res.stdout
    assert "The Bishops" in res.stdout
    assert "The Pawns" in res.stdout


def test_gambit_chessboard_status(capsys):
    ret = gambit_cli.show_chessboard_status([])
    assert ret == 0
    out = capsys.readouterr().out
    assert "GAMBIT — Autonomous Engineering Fleet" in out
    assert "Stationed Knights" in out
    assert "Engine Quotas & Readiness" in out
    assert "The Rook" in out


def test_gambit_natural_language_mission_routing(monkeypatch):
    routed = []

    def mock_forward(script_name, args):
        routed.append((script_name, args))
        return 0

    monkeypatch.setattr(gambit_cli, "forward_to_script", mock_forward)
    monkeypatch.setattr(sys, "argv", ["gambit", "In", "backend", "add", "auth,", "in", "frontend", "wire", "login"])

    with pytest.raises(SystemExit) as exc:
        gambit_cli.main()

    assert exc.value.code == 0
    assert len(routed) == 1
    assert routed[0][0] == "cao-auto"
    assert routed[0][1] == ["In backend add auth, in frontend wire login"]


def test_gambit_dash_command_aliasing(monkeypatch):
    routed = []

    def mock_forward(script_name, args):
        routed.append((script_name, args))
        return 0

    monkeypatch.setattr(gambit_cli, "forward_to_script", mock_forward)
    monkeypatch.setattr(sys, "argv", ["gambit-test", "http://localhost:3000"])

    with pytest.raises(SystemExit) as exc:
        gambit_cli.main()

    assert exc.value.code == 0
    assert len(routed) == 1
    assert routed[0][0] == "cao-qa"
    assert routed[0][1] == ["http://localhost:3000"]
