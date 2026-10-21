"""Unit tests for Milestone 6 Production Resilience (P6.1, P6.4, P6.6)."""
import hashlib
import json
import socket
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

from run.cao_auto import AutonomousRunner
from run.cao_lib import heal_stale_daemon, is_port_open, probe_daemon_health
from run.cao_memory import (
    get_connection,
    list_memories,
    prune_memories,
    store_memory,
    vacuum_memory,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parent


class DummyClient:
    def __init__(self, status: str = "RUNNING", output: str = ""):
        self.status = status
        self.output = output
        self.deleted_terminals = []
        self.launched = []

    def launch_session(self, agent_profile, initial_message, model=None, working_directory=None):
        term_id = f"term-{len(self.launched) + 1}"
        self.launched.append((agent_profile, model, term_id))
        return {"terminal_id": term_id}

    def get_terminal(self, terminal_id: str) -> dict:
        return {"terminal_id": terminal_id, "status": self.status}

    def get_terminal_output(self, terminal_id: str) -> str:
        return self.output

    def delete_terminal(self, terminal_id: str) -> bool:
        self.deleted_terminals.append(terminal_id)
        return True


def test_p6_1_watchdog_defaults_and_output_tracking(tmp_path):
    tasks_file = tmp_path / "tasks.json"
    tasks = [{"id": "t1", "title": "Implement feature", "detail": "Write code", "status": "pending", "engine": "claude_worker"}]
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")

    client = DummyClient(status="RUNNING", output="initial output")
    runner = AutonomousRunner(tasks_file=tasks_file, client=client)

    assert runner.wall_clock_timeout == 900.0
    assert runner.stagnation_timeout == 180.0

    runner._dispatch_task(tasks[0], tasks)
    assert "t1" in runner.active_workers
    meta = runner.active_workers["t1"]
    assert "last_output_hash" in meta
    assert "last_output_change_monotonic" in meta
    initial_hash = meta["last_output_hash"]
    initial_change_ts = meta["last_output_change_monotonic"]

    # Poll with changed stdout -> hash and timestamp update
    time.sleep(0.01)
    runner._poll_active_terminals(tasks)
    assert meta["last_output_hash"] != initial_hash
    assert meta["last_output_change_monotonic"] > initial_change_ts


def test_p6_1_watchdog_wall_clock_timeout(tmp_path):
    tasks_file = tmp_path / "tasks.json"
    tasks = [{"id": "t1", "title": "Long running task", "detail": "Hang", "status": "running", "engine": "claude_worker"}]
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")

    client = DummyClient(status="RUNNING", output="still working...")
    runner = AutonomousRunner(
        tasks_file=tasks_file,
        client=client,
        wall_clock_timeout=5.0,
        stagnation_timeout=180.0,
        self_heal=True,
    )

    now = time.monotonic()
    runner.active_workers["t1"] = {
        "terminal_id": "term-watchdog",
        "engine": "claude_worker",
        "started": now - 10.0,
        "last_output_hash": hashlib.sha256(b"still working...").hexdigest(),
        "last_output_change_monotonic": now - 1.0,
    }

    runner._poll_active_terminals(tasks)

    assert "term-watchdog" in client.deleted_terminals
    assert "t1" not in runner.active_workers
    assert tasks[0]["failure_reason"] == "watchdog_timeout"
    assert tasks[0]["status"] == "pending"
    assert tasks[0]["engine"] == "coder_worker"


def test_p6_1_stdout_stagnation_timeout(tmp_path):
    tasks_file = tmp_path / "tasks.json"
    tasks = [{"id": "t2", "title": "Stagnant task", "detail": "Frozen stdout", "status": "running", "engine": "claude_worker"}]
    tasks_file.write_text(json.dumps(tasks), encoding="utf-8")

    client = DummyClient(status="RUNNING", output="frozen line")
    runner = AutonomousRunner(
        tasks_file=tasks_file,
        client=client,
        wall_clock_timeout=900.0,
        stagnation_timeout=5.0,
        self_heal=False,
    )

    now = time.monotonic()
    runner.active_workers["t2"] = {
        "terminal_id": "term-stagnant",
        "engine": "claude_worker",
        "started": now - 10.0,
        "last_output_hash": hashlib.sha256(b"frozen line").hexdigest(),
        "last_output_change_monotonic": now - 10.0,
    }

    runner._poll_active_terminals(tasks)

    assert "term-stagnant" in client.deleted_terminals
    assert "t2" not in runner.active_workers
    assert tasks[0]["failure_reason"] == "stdout_stagnation"
    assert tasks[0]["status"] == "failed"


def test_p6_4_heal_stale_daemon():
    # 1. Port not open -> returns False
    with patch("run.cao_lib.is_port_open", return_value=False):
        assert heal_stale_daemon(port=9889) is False

    # 2. Port open and daemon healthy -> returns False without killing anything
    with (
        patch("run.cao_lib.is_port_open", return_value=True),
        patch("run.cao_lib.probe_daemon_health", return_value=True),
        patch("run.cao_lib.find_pids_on_port") as mock_find,
    ):
        assert heal_stale_daemon(port=9889) is False
        mock_find.assert_not_called()

    # 3. Port open but daemon unresponsive -> finds and terminates stale PIDs, returns True
    with (
        patch("run.cao_lib.is_port_open", return_value=True),
        patch("run.cao_lib.probe_daemon_health", return_value=False),
        patch("run.cao_lib.find_pids_on_port", return_value=[42424]) as mock_find,
        patch("run.cao_lib.terminate_stale_pids", return_value=[42424]) as mock_term,
    ):
        assert heal_stale_daemon(port=9889) is True
        mock_find.assert_called_once_with(port=9889)
        mock_term.assert_called_once_with([42424])

    # 4. Real ephemeral socket test for is_port_open and probe_daemon_health
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        ephemeral_port = srv.getsockname()[1]
        assert is_port_open(port=ephemeral_port, timeout=0.5) is True
        assert probe_daemon_health(port=ephemeral_port, timeout=0.2) is False


def test_p6_6_memory_pruning_and_vacuum(tmp_path):
    db_path = tmp_path / "memory.sqlite"
    conn = get_connection(db_path=db_path)

    now = datetime.now(timezone.utc)
    old_ts = (now - timedelta(days=45)).isoformat()
    recent_ts = (now - timedelta(days=5)).isoformat()

    # Insert 5 old memories and 3 recent memories (total 8)
    with conn:
        for i in range(5):
            conn.execute(
                "INSERT INTO session_memory(session_id, category, summary, details, file_paths, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("s_old", "bug_fix", f"Old memory {i}", "details", "", old_ts),
            )
        for i in range(3):
            conn.execute(
                "INSERT INTO session_memory(session_id, category, summary, details, file_paths, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ("s_new", "architecture", f"Recent memory {i}", "details", "", recent_ts),
            )
    conn.close()

    # If keep_min=10, nothing should be pruned even though 5 entries are 45 days old
    pruned_none = prune_memories(max_age_days=30, keep_min=10, db_path=db_path)
    assert pruned_none == 0
    assert len(list_memories(limit=20, db_path=db_path)) == 8

    # If keep_min=5, we have 8 entries: newest 5 are kept (3 recent + 2 old), and 3 old entries are pruned
    pruned_three = prune_memories(max_age_days=30, keep_min=5, db_path=db_path)
    assert pruned_three == 3
    remaining = list_memories(limit=20, db_path=db_path)
    assert len(remaining) == 5

    # Vacuum should succeed cleanly
    vacuum_memory(db_path=db_path)
    assert len(list_memories(limit=20, db_path=db_path)) == 5


def test_p6_6_cao_memory_cli_subcommands():
    cao_mem = REPO / "run" / "cao-memory"
    res_help = subprocess.run([sys.executable, str(cao_mem), "--help"], capture_output=True, text=True, check=True)
    assert "prune" in res_help.stdout
    assert "vacuum" in res_help.stdout
