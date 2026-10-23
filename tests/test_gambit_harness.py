"""Tests for GAMBIT-HARNESS — Kernel-Secured AI Agent Isolation & Zero-Secret Runtime."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from run.gambit_harness import GambitHarness, HarnessAuditRecord


def test_landlock_abi_detection():
    harness = GambitHarness()
    # On Linux 6.8+, Landlock ABI should be >= 1 (detected v4)
    abi = harness.get_landlock_abi_version()
    assert isinstance(abi, int)
    assert abi >= 0


def test_sanitize_environment_strips_sensitive_keys():
    harness = GambitHarness()
    raw_env = {
        "PATH": "/usr/bin:/bin",
        "USER": "testuser",
        "ANTHROPIC_API_KEY": "sk-ant-test-secret-12345",
        "OPENAI_API_KEY": "sk-openai-test-secret-98765",
        "GITHUB_TOKEN": "ghp_realtoken123",
        "LOCAL_API_KEY": "cao-secret-key-456",
        "AWS_SECRET_ACCESS_KEY": "aws-secret-key-789",
        "SAFE_CUSTOM_VAR": "my_public_setting",
    }

    clean, stripped = harness.sanitize_environment(raw_env)

    # Sensitive keys must be stripped from the returned dictionary
    assert "GITHUB_TOKEN" not in clean
    assert "AWS_SECRET_ACCESS_KEY" not in clean

    # Masked / proxy tokens should be present
    assert clean["ANTHROPIC_API_KEY"] == "gambit-harness-isolated-token"
    assert clean["OPENAI_API_KEY"] == "gambit-harness-isolated-token"
    assert clean["LOCAL_API_KEY"] == "gambit-harness-isolated-token"
    assert clean["GAMBIT_HARNESS_ACTIVE"] == "1"

    # Safe vars must be preserved
    assert clean["PATH"] == "/usr/bin:/bin"
    assert clean["USER"] == "testuser"
    assert clean["SAFE_CUSTOM_VAR"] == "my_public_setting"

    # Stripped keys list must contain all stripped sensitive vars
    assert "GITHUB_TOKEN" in stripped
    assert "AWS_SECRET_ACCESS_KEY" in stripped


def test_build_path_rules():
    harness = GambitHarness()
    ro, rw = harness.build_path_rules(extra_ro=["/etc"], extra_rw=["/tmp"])

    assert "/usr" in ro
    assert "/bin" in ro or "/usr/bin" in ro
    assert str(harness.workspace) in rw
    assert "/tmp" in rw


def test_harness_execution_inside_workspace(tmp_path):
    harness = GambitHarness(workspace=tmp_path, audit_dir=tmp_path / "audit")
    code, out, err, audit = harness.run("echo 'hello from harness'")

    assert code == 0
    assert "hello from harness" in out
    assert audit.status == "PASS"
    assert audit.duration_s >= 0.0


def test_harness_blocks_unauthorized_paths(tmp_path):
    """Verify that Landlock blocks access to unauthorized paths outside workspace and sys."""
    harness = GambitHarness(workspace=tmp_path, audit_dir=tmp_path / "audit")
    if not harness.is_supported():
        pytest.skip("Landlock LSM not supported in this environment")

    # Command tries to read a non-allowed host file (~/.git-credentials)
    test_script = (
        'python3 -c "'
        'import os; '
        'target = os.path.expanduser(\'~/.git-credentials\'); '
        'open(target, \'r\')"'
    )

    code, out, err, audit = harness.run(test_script)

    # Must fail with PermissionError / EACCES
    assert code != 0
    assert "PermissionError" in err or "Permission denied" in err


def test_harness_audit_logging(tmp_path):
    audit_dir = tmp_path / "audit"
    harness = GambitHarness(workspace=tmp_path, audit_dir=audit_dir)

    code, out, err, audit = harness.run("echo 'audit test'")
    assert code == 0

    log_file = audit_dir / "harness_audit.json"
    assert log_file.exists()

    data = json.loads(log_file.read_text(encoding="utf-8"))
    assert isinstance(data, list)
    assert len(data) >= 1
    last = data[-1]
    assert last["status"] == "PASS"
    assert "echo 'audit test'" in " ".join(last["command"])
    assert last["landlock_abi"] == harness.landlock_abi
