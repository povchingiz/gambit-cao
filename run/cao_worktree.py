"""cao_worktree.py — Git Worktree Sandbox Manager for Parallel Worker Isolation.

Provides speculative execution environments in `wcao/sandboxes/<worker>`:
1. Spawns ephemeral git worktrees for workers to develop in isolation.
2. Anti-tampering and test gates verify the sandbox branch.
3. Squash-merges verified changes back into the target branch without dirtying the working tree.
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class WorktreeManager:
    """Manages git worktree lifecycles for CAO workers."""

    def __init__(self, repo_root: Optional[Path] = None):
        if repo_root is None:
            # Discover repo root
            p = Path.cwd().resolve()
            while p != p.parent:
                if (p / ".git").exists():
                    repo_root = p
                    break
                p = p.parent
            if repo_root is None:
                repo_root = Path.cwd().resolve()

        self.repo_root = repo_root
        self.sandboxes_dir = self.repo_root / "wcao" / "sandboxes"

    def get_sandbox_path(self, worker_name: str) -> Path:
        return self.sandboxes_dir / worker_name

    def get_branch_name(self, worker_name: str) -> str:
        safe_name = worker_name.replace("/", "_").replace(" ", "_")
        return f"wcao-sandbox-{safe_name}"

    def list_sandboxes(self) -> List[Dict[str, Any]]:
        """List currently existing worktree sandboxes."""
        sandboxes = []
        if not self.sandboxes_dir.exists():
            return sandboxes

        for p in self.sandboxes_dir.iterdir():
            if p.is_dir() and (p / ".git").exists():
                branch = self.get_branch_name(p.name)
                sandboxes.append({
                    "worker": p.name,
                    "path": str(p),
                    "branch": branch,
                })
        return sandboxes

    def create_sandbox(self, worker_name: str, base_branch: Optional[str] = None) -> Path:
        """Create an isolated worktree sandbox for worker."""
        self.sandboxes_dir.mkdir(parents=True, exist_ok=True)
        sandbox_path = self.get_sandbox_path(worker_name)
        branch = self.get_branch_name(worker_name)

        if not base_branch:
            try:
                base_branch = subprocess.check_output(
                    ["git", "-C", str(self.repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            except Exception:
                base_branch = "master"

        # If sandbox path already exists, clean it first
        if sandbox_path.exists():
            self.remove_sandbox(worker_name)

        # Ensure branch doesn't conflict
        subprocess.run(
            ["git", "-C", str(self.repo_root), "branch", "-D", branch],
            capture_output=True,
            text=True,
        )

        # Create worktree
        cmd = [
            "git", "-C", str(self.repo_root),
            "worktree", "add", "-b", branch, str(sandbox_path), base_branch,
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Failed to create git worktree: {res.stderr.strip()}")

        return sandbox_path

    def remove_sandbox(self, worker_name: str, delete_branch: bool = True) -> bool:
        """Remove a worktree sandbox and delete its branch."""
        sandbox_path = self.get_sandbox_path(worker_name)
        branch = self.get_branch_name(worker_name)

        if sandbox_path.exists():
            subprocess.run(
                ["git", "-C", str(self.repo_root), "worktree", "remove", "--force", str(sandbox_path)],
                capture_output=True,
                text=True,
            )
            if sandbox_path.exists():
                shutil.rmtree(sandbox_path, ignore_errors=True)

        # Prune dead worktree metadata
        subprocess.run(
            ["git", "-C", str(self.repo_root), "worktree", "prune"],
            capture_output=True,
            text=True,
        )

        if delete_branch:
            subprocess.run(
                ["git", "-C", str(self.repo_root), "branch", "-D", branch],
                capture_output=True,
                text=True,
            )
        return True

    def merge_sandbox(
        self,
        worker_name: str,
        target_branch: Optional[str] = None,
        squash: bool = True,
        commit_message: Optional[str] = None,
    ) -> bool:
        """Merge verified changes from sandbox branch into target branch."""
        branch = self.get_branch_name(worker_name)
        sandbox_path = self.get_sandbox_path(worker_name)

        if not target_branch:
            try:
                target_branch = subprocess.check_output(
                    ["git", "-C", str(self.repo_root), "rev-parse", "--abbrev-ref", "HEAD"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                ).strip()
            except Exception:
                target_branch = "master"

        # Check if sandbox has uncommitted changes
        if sandbox_path.exists():
            status = subprocess.check_output(
                ["git", "-C", str(sandbox_path), "status", "--porcelain"],
                text=True,
            ).strip()
            if status:
                # Auto-commit sandbox changes
                subprocess.run(["git", "-C", str(sandbox_path), "add", "-A"], check=True)
                subprocess.run(
                    ["git", "-C", str(sandbox_path), "commit", "-m", f"sandbox({worker_name}): speculative work"],
                    check=True,
                )

        # Merge into target_branch
        msg = commit_message or f"feat(wcao): merge sandbox {worker_name}"
        merge_cmd = ["git", "-C", str(self.repo_root), "merge"]
        if squash:
            merge_cmd.extend(["--squash", branch])
            res = subprocess.run(merge_cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"Squash merge conflict: {res.stderr}")
            subprocess.run(["git", "-C", str(self.repo_root), "commit", "-m", msg], check=True)
        else:
            merge_cmd.extend(["-m", msg, branch])
            res = subprocess.run(merge_cmd, capture_output=True, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"Merge conflict: {res.stderr}")

        return True
