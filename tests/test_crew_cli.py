"""Unit tests for the Unified CAO-Crew CLI (crew / cao-crew)."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = REPO_ROOT / "run"
if str(RUN_DIR) not in sys.path:
    sys.path.insert(0, str(RUN_DIR))

import pytest
from cao_crew_cli import main, show_unified_status


def test_crew_cli_help(capsys):
    crew_bin = RUN_DIR / "crew"
    res = subprocess.run([sys.executable, str(crew_bin), "--help"], capture_output=True, text=True)
    assert res.returncode == 0
    assert "🛸 cao-crew (`crew`)" in res.stdout
    assert "status" in res.stdout
    assert "fleet" in res.stdout
    assert "repair" in res.stdout
    assert "evolve" in res.stdout


def test_crew_status_dashboard(capsys):
    ret = show_unified_status([])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Unified Workstation & Fleet Dashboard" in out
    assert "Workstation Projects" in out
    assert "Provider Quotas & Utilization" in out


def test_crew_alias_resolution():
    cao_crew = RUN_DIR / "cao-crew"
    crew = RUN_DIR / "crew"
    assert cao_crew.exists()
    assert crew.exists()
    assert cao_crew.resolve() == crew.resolve()


def test_crew_auto_goal_routing(capsys, monkeypatch):
    """Ensure natural language strings automatically route to cao-auto without explicit 'auto' verb."""
    import cao_crew_cli
    routed = []

    def mock_forward(script_name, args):
        routed.append((script_name, args))
        return 0

    monkeypatch.setattr(cao_crew_cli, "forward_to_script", mock_forward)
    monkeypatch.setattr(sys, "argv", ["crew", "Build", "a", "secure", "REST", "API"])

    with pytest.raises(SystemExit) as exc:
        cao_crew_cli.main()

    assert exc.value.code == 0
    assert len(routed) == 1
    assert routed[0][0] == "cao-auto"
    assert routed[0][1] == ["Build a secure REST API"]
