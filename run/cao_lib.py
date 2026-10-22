"""cao_lib — shared helpers for cao-tokens, cao-limits, and future tools.
Extracted from cao-tokens to avoid duplication."""
import json
import os
import re
import signal
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.request
from glob import glob
from pathlib import Path
from typing import List

HOME = Path.home()

CAO_MARKERS = ("cao-mcp-server", "cao_", '"assign"')


def cutoff_ts(since):
    if not since:
        return 0.0
    n, unit = float(since[:-1]), since[-1]
    mult = {"h": 3600, "d": 86400, "w": 604800}.get(unit)
    if not mult:
        sys.exit(f"bad --since '{since}': use e.g. 24h, 7d, 2w")
    return time.time() - n * mult


def _iter_claude_files(cutoff):
    root = HOME / ".claude" / "projects"
    if not root.exists():
        return
    for f in glob(str(root / "**" / "*.jsonl"), recursive=True):
        if cutoff and os.path.getmtime(f) < cutoff:
            continue
        yield f


def _file_is_cao(path):
    """True if this session loaded cao's MCP server / used its assign tool."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if any(m in line for m in CAO_MARKERS):
                    return True
    except OSError:
        return False
    return False


def _q(db, sql):
    if not Path(db).exists():
        return None
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        out = con.execute(sql).fetchall()
        con.close()
        return out
    except sqlite3.Error:
        return None


def hn(n):
    """Human-compact number: 1234 -> 1.2k, 2_500_000 -> 2.5M, 0 -> 0."""
    n = int(n)
    if n == 0:
        return "0"
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}k"
    return str(n)


def is_port_open(port: int = 9889, host: str = "127.0.0.1", timeout: float = 1.0) -> bool:
    """Return True if a TCP socket is listening on host:port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def probe_daemon_health(port: int = 9889, host: str = "127.0.0.1", timeout: float = 2.0) -> bool:
    """Return True if the daemon on host:port responds HTTP 2xx to /health or /sessions."""
    for endpoint in ("/health", "/sessions"):
        url = f"http://{host}:{port}{endpoint}"
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                if 200 <= getattr(resp, "status", 200) < 300:
                    return True
        except Exception:
            continue
    return False


def find_pids_on_port(port: int = 9889) -> List[int]:
    """Find PIDs bound to the given TCP port."""
    pids: List[int] = []
    my_pid = os.getpid()

    # Try lsof first
    try:
        res = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if res.returncode == 0 and res.stdout.strip():
            for line in res.stdout.splitlines():
                line = line.strip()
                if line.isdigit():
                    pid = int(line)
                    if pid != my_pid and pid not in pids:
                        pids.append(pid)
    except Exception:
        pass

    # Fallback to ss if lsof returned nothing
    if not pids:
        try:
            res = subprocess.run(
                ["ss", "-lptn", f"sport = :{port}"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if res.returncode == 0 and res.stdout:
                for match in re.findall(r"pid=(\d+)", res.stdout):
                    pid = int(match)
                    if pid != my_pid and pid not in pids:
                        pids.append(pid)
        except Exception:
            pass

    return pids


def terminate_stale_pids(pids: List[int], sigterm_wait: float = 1.0) -> List[int]:
    """Send SIGTERM (then SIGKILL if needed) to stale daemon PIDs."""
    terminated: List[int] = []
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            terminated.append(pid)
        except ProcessLookupError:
            continue
        except PermissionError:
            continue

    if terminated and sigterm_wait > 0:
        deadline = time.monotonic() + sigterm_wait
        while time.monotonic() < deadline:
            still_alive = []
            for pid in terminated:
                try:
                    os.kill(pid, 0)
                    still_alive.append(pid)
                except OSError:
                    pass
            if not still_alive:
                break
            time.sleep(0.05)

        for pid in terminated:
            try:
                os.kill(pid, 0)
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

    return terminated


def heal_stale_daemon(port: int = 9889, timeout: float = 2.0) -> bool:
    """Probe http://127.0.0.1:<port>/health (or /sessions); if the port is bound
    by an unresponsive/zombie process that fails HTTP health checks, terminate
    the stale process so a new daemon can bind cleanly.

    Returns True if a stale daemon was detected and cleaned up, False otherwise.
    """
    if not is_port_open(port=port, timeout=min(1.0, timeout)):
        return False

    if probe_daemon_health(port=port, timeout=timeout):
        return False

    pids = find_pids_on_port(port=port)
    terminate_stale_pids(pids)
    return True


# ==============================================================================
# GAMBIT Workspace Resolution & Auto-Migration Patch (wcao <-> wgambit)
# ==============================================================================

def patch_workspace_migration(repo_root: Path) -> Path:
    """Detects legacy wcao/ in repo_root and migrates/links it to wgambit/.
    
    Ensures complete preservation of sequence diagrams, schemas, plans,
    memory, and audit trails while establishing wgambit as the canonical workspace.
    
    If wcao/ exists and wgambit/ does not:
      1. Renames wcao -> wgambit
      2. Creates a relative symlink wcao -> wgambit for 100% backwards compatibility
         with legacy tools, scripts, and tests.
    
    If wgambit/ exists and wcao/ does not:
      Creates a relative symlink wcao -> wgambit for backwards compatibility.
      
    Returns:
      Canonical Path to wgambit/.
    """
    repo_root = Path(repo_root).resolve()
    wcao_dir = repo_root / "wcao"
    wgambit_dir = repo_root / "wgambit"

    # Case 1: wcao exists, wgambit does not exist
    if wcao_dir.exists() and not wgambit_dir.exists():
        if wcao_dir.is_symlink():
            # If wcao is already a symlink pointing to wgambit (broken target), fix it
            target = os.readlink(wcao_dir)
            if target == "wgambit":
                wgambit_dir.mkdir(parents=True, exist_ok=True)
                return wgambit_dir
        # Rename physical directory wcao -> wgambit
        wcao_dir.rename(wgambit_dir)
        # Create backward-compatibility symlink: wcao -> wgambit
        try:
            os.symlink("wgambit", wcao_dir)
        except OSError:
            pass
        return wgambit_dir

    # Case 2: wgambit exists, wcao does not exist
    elif wgambit_dir.exists() and not wcao_dir.exists():
        try:
            os.symlink("wgambit", wcao_dir)
        except OSError:
            pass
        return wgambit_dir

    # Case 3: Both exist
    elif wgambit_dir.exists() and wcao_dir.exists():
        return wgambit_dir

    # Case 4: Neither exists -> default to wgambit
    return wgambit_dir


def resolve_workspace_dir(repo_root: Path, create: bool = True, auto_patch: bool = True) -> Path:
    """Resolve the active GAMBIT workspace directory (wgambit/ or wcao/).
    
    Parameters:
      repo_root: Path to repository or project root.
      create: If True, creates wgambit/ (and symlink wcao -> wgambit) if neither exists.
      auto_patch: If True, automatically patches and migrates legacy wcao/ -> wgambit/.
      
    Returns:
      Resolved Path object pointing to the workspace directory.
    """
    repo_root = Path(repo_root).resolve()
    wcao_dir = repo_root / "wcao"
    wgambit_dir = repo_root / "wgambit"

    if auto_patch:
        if wcao_dir.exists() and not wgambit_dir.exists():
            return patch_workspace_migration(repo_root)
        if wgambit_dir.exists() and not wcao_dir.exists():
            return patch_workspace_migration(repo_root)

    if wgambit_dir.exists():
        return wgambit_dir

    if wcao_dir.exists():
        return wcao_dir

    if create:
        wgambit_dir.mkdir(parents=True, exist_ok=True)
        try:
            if not wcao_dir.exists():
                os.symlink("wgambit", wcao_dir)
        except OSError:
            pass
        return wgambit_dir

    return wgambit_dir

