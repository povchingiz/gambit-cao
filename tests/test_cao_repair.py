"""Tests for 1000x Autonomous Closed-Loop Self-Healing Engine (cao_repair.py)."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = REPO_ROOT / "run"
if str(RUN_DIR) not in sys.path:
    sys.path.insert(0, str(RUN_DIR))

import pytest
from cao_repair import AutoRepairEngine, RepairFinding


@pytest.fixture
def test_git_repo(tmp_path):
    """Set up an isolated git repo with a flawed HTML page."""
    repo = tmp_path / "sandbox_repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "TestUser"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)

    html_file = repo / "index.html"
    html_file.write_text(
        """<!DOCTYPE html>
<html>
<head>
  <title>Flawed Page</title>
</head>
<body>
  <div style="width: 700px; height: 20px; background: #eee;">Wide Banner</div>
  <button id="btn-dead-action">Unwired Button</button>
</body>
</html>
""",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True)
    return repo, html_file


def test_auto_repair_engine_detects_and_fixes_defects_in_worktree(test_git_repo):
    repo, html_file = test_git_repo

    engine = AutoRepairEngine(
        target=str(html_file),
        project_root=str(repo),
        max_cycles=2,
        auto_merge=True,
    )
    result = engine.run_repair_loop()

    # 1. Verification of defect discovery
    assert result.initial_score < 100
    assert len(result.findings) >= 1

    # 2. Score must improve after autonomous repair
    assert result.final_score > result.initial_score
    assert result.merged is True
    assert result.cycles_run >= 1

    # 3. Target file inside the main repo now has the repairs applied via squash-merge
    updated_content = html_file.read_text(encoding="utf-8")
    assert "cao-qa responsive overflow guard" in updated_content
    assert "btn-dead-action" in updated_content

    # 4. Git log in repo must reflect the automated commit
    log_res = subprocess.run(["git", "log", "-n", "1", "--oneline"], cwd=repo, capture_output=True, text=True)
    assert "fix(ui-ux): autonomous repair via cao-repair" in log_res.stdout
