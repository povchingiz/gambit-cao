import subprocess
import sys
from run.cao_laya_router import LayaRouter


def test_laya_route_architecture():
    res = LayaRouter.route_task("Design DDD aggregate roots and service contracts")
    assert res["worker"] == "claude_worker"
    assert res["provider"] == "claude_code"
    assert "claude" in res["model"]
    assert res["confidence"] >= 0.70


def test_laya_route_frontend():
    res = LayaRouter.route_task("Build responsive React Tailwind navigation bar")
    assert res["worker"] == "codex_worker"
    assert res["provider"] == "codex"
    assert "gpt" in res["model"]


def test_laya_route_tests_qa():
    res = LayaRouter.route_task("Write comprehensive pytest suite and verify coverage")
    assert res["worker"] == "antigravity_worker"
    assert res["provider"] == "antigravity_cli"
    assert "gemini" in res["model"]


def test_laya_route_boilerplate():
    res = LayaRouter.route_task("Generate CRUD database migration schema and repetitive helpers")
    assert res["worker"] == "coder_worker"
    assert res["provider"] == "opencode_cli"


def test_laya_evaluate_risk():
    # Critical risk
    r_crit = LayaRouter.evaluate_risk("bash", "rm -rf /")
    assert r_crit["decision"] == "ESCALATE_TO_HUMAN"
    assert r_crit["risk_tier"] == "CRITICAL"
    assert not r_crit["auto_approved"]

    # Safe read
    r_safe = LayaRouter.evaluate_risk("git", "status")
    assert r_safe["decision"] == "AUTO_APPROVE"
    assert r_safe["risk_tier"] == "SAFE"
    assert r_safe["auto_approved"]

    # Standard edit
    r_std = LayaRouter.evaluate_risk("edit_file", "path/to/file.py")
    assert r_std["risk_tier"] == "STANDARD"
    assert r_std["auto_approved"]


def test_laya_cli_route(tmp_path):
    cmd = [sys.executable, "run/cao-laya", "route", "design abstract protocol", "--json"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "claude_worker" in proc.stdout
