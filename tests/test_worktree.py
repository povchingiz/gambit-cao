import subprocess
import pytest
from pathlib import Path
from run.cao_worktree import WorktreeManager


def test_worktree_lifecycle(tmp_path):
    # Initialize a git repo
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "master"], cwd=str(repo), check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=str(repo), check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(repo), check=True)

    # Initial commit
    (repo / "README.md").write_text("# Test Repo")
    subprocess.run(["git", "add", "README.md"], cwd=str(repo), check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=str(repo), check=True)

    mgr = WorktreeManager(repo_root=repo)

    # 1. Create sandbox
    sb_path = mgr.create_sandbox("coder_worker", base_branch="master")
    assert sb_path.exists()
    assert (sb_path / "README.md").exists()

    # 2. List sandboxes
    boxes = mgr.list_sandboxes()
    assert len(boxes) == 1
    assert boxes[0]["worker"] == "coder_worker"

    # 3. Modify inside sandbox and merge
    (sb_path / "feature.py").write_text("print('hello sandbox')")
    mgr.merge_sandbox("coder_worker", target_branch="master", squash=True)

    # Verify merged file exists in main repo
    assert (repo / "feature.py").exists()

    # 4. Remove sandbox
    mgr.remove_sandbox("coder_worker")
    assert not sb_path.exists()
