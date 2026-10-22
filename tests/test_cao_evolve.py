"""Tests for Protected Prompt Self-Evolution Loop (cao_evolve.py)."""
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = REPO_ROOT / "run"
if str(RUN_DIR) not in sys.path:
    sys.path.insert(0, str(RUN_DIR))

import pytest
from cao_evolve import EvolutionGateVerdict, PromptEvolutionEngine


def test_classify_failure_taxonomies():
    engine = PromptEvolutionEngine()

    assert engine.classify_failure("Error: unrecognized argument: --invalid-flag") == "tool_usage_error"
    assert engine.classify_failure("pytest AssertionError: expected True got False") == "reasoning_mistake"
    assert engine.classify_failure("Terminal halted due to watchdog_timeout (stalled)") == "planning_premature_stop"
    assert engine.classify_failure("Test tampering detected: assertion removed") == "scope_format_error"
    assert engine.classify_failure("Something totally unknown happened") == "one_off_edge_case"


def test_performance_gate_anti_bloat_protection():
    engine = PromptEvolutionEngine()

    original = "---\nname: test_worker\nprovider: test\n---\n# System Prompt\nClean instructions."
    
    # 1. Concise, high-signal addition (<15% growth) passes
    small_cand = original + "\n- Verify inputs."
    verdict_pass = engine.evaluate_performance_gate(original, small_cand)
    assert verdict_pass.passed is True
    assert "Token budget respected" in verdict_pass.details

    # 2. Bloated reactive paragraph (>15% growth) fails Gate 2
    bloated = original + "\n" + ("DO NOT DO THIS AND NEVER DO THAT BECAUSE IT BROKE BEFORE. " * 30)
    verdict_bloat = engine.evaluate_performance_gate(original, bloated)
    assert verdict_bloat.passed is False
    assert "violates anti-bloat gate" in verdict_bloat.details

    # 3. Corrupted frontmatter fails Gate 2
    corrupt_fm = "No frontmatter at all here."
    verdict_corrupt = engine.evaluate_performance_gate(original, corrupt_fm)
    assert verdict_corrupt.passed is False
    assert "frontmatter" in verdict_corrupt.details.lower()


def test_evolve_worker_dual_gate_in_sandbox(tmp_path):
    """Test full evolution cycle in an isolated git repository."""
    repo = tmp_path / "mock_repo"
    repo.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "AgentTest"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "agent@test.local"], cwd=repo, check=True)

    # Set up prompt structure
    prompts_dir = repo / "setup" / "2_configure" / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = prompts_dir / "coder_worker.md"
    prompt_file.write_text(
        "---\nname: coder_worker\nprovider: opencode\nrole: developer\n---\n\n# System Prompt\n## Execution rules\n- Write code cleanly.\n",
        encoding="utf-8",
    )

    # Set up passing test suite
    tests_dir = repo / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "test_sample.py").write_text("def test_ok():\n    assert True\n", encoding="utf-8")

    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=repo, check=True)

    engine = PromptEvolutionEngine(repo_root=repo)

    # Run evolution with a reasoning mistake trace
    trace = "AssertionError: expected status ok but got error"
    res = engine.evolve_worker(worker_name="coder_worker", failure_trace=trace, auto_merge=True)

    assert res.accepted is True
    assert res.root_cause == "reasoning_mistake"
    assert res.quality_gate.passed is True
    assert res.performance_gate.passed is True
    assert res.commit_sha is not None

    # Check updated prompt in repo
    updated = prompt_file.read_text(encoding="utf-8")
    assert "Verify assumptions against ground-truth contracts" in updated
