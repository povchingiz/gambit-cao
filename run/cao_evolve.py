#!/usr/bin/env python3
"""cao_evolve.py — Protected Prompt Self-Evolution Loop (The Self-Evolving Agent Harness).

Implements the Self-Evolving Agent Harness architecture:
1. Precise Error Signals & Root-Cause Clustering:
   Classifies failure traces into 4 systematic failure patterns:
   - Tool Usage Errors
   - Reasoning Mistakes
   - Planning / Premature Stop
   - Scope & Format Compliance
2. Anti-Bloat Prompt Refinement:
   Addresses the shared failure mode without reactive "DO NOT" prompt bloat.
3. Protected Competence (Dual Gate):
   - Gate 1: Quality Gate (100% test pass rate + AST anti-tampering verification).
   - Gate 2: Performance Gate (Strict token budget: <= +15% token growth).
4. Isolated Worktree Execution:
   Proposes and tests mutations inside an ephemeral git sandbox before squash-merging.
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "run") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "run"))

from cao_tamper import detect_test_tampering
from cao_worktree import WorktreeManager

logger = logging.getLogger("cao_evolve")

# 4 Systematic Root-Cause Failure Taxonomies (from Self-Evolving Agent Harness)
FAILURE_TAXONOMIES = {
    "tool_usage_error": re.compile(
        r"(command not found|unrecognized argument|flag|syntaxerror|invalid option|exit code [1-9]|stderr:|missing parameter)",
        re.IGNORECASE,
    ),
    "reasoning_mistake": re.compile(
        r"(assertionerror|test failed|expected .* but got|typeerror|indexerror|keyerror|logic error|incorrect value)",
        re.IGNORECASE,
    ),
    "planning_premature_stop": re.compile(
        r"(watchdog_timeout|stdout_stagnation|prompt_deadlock|timeout|stalled|incomplete|unresolved|hanging)",
        re.IGNORECASE,
    ),
    "scope_format_error": re.compile(
        r"(tamper|out of scope|unauthorized file|jsondecodeerror|preamble|formatting violation)",
        re.IGNORECASE,
    ),
}

# Generalizable, anti-bloat directives for each taxonomy
GENERALIZABLE_DIRECTIVES = {
    "tool_usage_error": "- Validate all tool arguments, CLI flags, and file paths for existence prior to execution.",
    "reasoning_mistake": "- Verify assumptions against ground-truth contracts; verify intermediate logic step-by-step.",
    "planning_premature_stop": "- Verify that execution has fully completed and relevant unit tests pass before declaring completion.",
    "scope_format_error": "- Strictly confine edits to explicitly assigned files without conversational preamble.",
}


@dataclass
class EvolutionGateVerdict:
    gate_name: str
    passed: bool
    details: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvolutionResult:
    worker_name: str
    root_cause: str
    original_tokens: int
    candidate_tokens: int
    quality_gate: EvolutionGateVerdict
    performance_gate: EvolutionGateVerdict
    accepted: bool
    commit_sha: Optional[str] = None
    rejection_reason: Optional[str] = None
    diff: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PromptEvolutionEngine:
    """Manages the Protected Prompt Self-Evolution Loop."""

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or REPO_ROOT
        self.prompts_dir = self.repo_root / "setup" / "2_configure" / "prompts"
        self.audit_dir = self.repo_root / "wcao" / "audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.audit_dir / "evolution_log.jsonl"
        self.wt_mgr = WorktreeManager(repo_root=self.repo_root)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count (~4 characters per token)."""
        return max(1, len(text) // 4)

    def classify_failure(self, failure_trace: str) -> str:
        """Classify failure trace into one of the 4 systematic root-cause patterns."""
        for taxonomy, pattern in FAILURE_TAXONOMIES.items():
            if pattern.search(failure_trace):
                return taxonomy
        return "one_off_edge_case"

    def synthesize_candidate_prompt(
        self,
        current_prompt: str,
        root_cause: str,
        custom_directive: Optional[str] = None,
    ) -> str:
        """Apply a generalizable directive to the prompt without reactive bloat."""
        directive = custom_directive or GENERALIZABLE_DIRECTIVES.get(root_cause)
        if not directive:
            return current_prompt

        # Check if directive or very similar rule is already present
        if directive.strip().lower() in current_prompt.lower():
            return current_prompt

        # Inject into "Execution rules" or append under "# System Prompt"
        if "## Execution rules" in current_prompt:
            parts = current_prompt.split("## Execution rules", 1)
            return f"{parts[0]}## Execution rules\n{directive}{parts[1]}"
        elif "Execution rules:" in current_prompt:
            parts = current_prompt.split("Execution rules:", 1)
            return f"{parts[0]}Execution rules:\n{directive}{parts[1]}"
        elif "# System Prompt" in current_prompt:
            parts = current_prompt.split("# System Prompt", 1)
            return f"{parts[0]}# System Prompt\n\nExecution rules:\n{directive}{parts[1]}"
        else:
            return f"{current_prompt.rstrip()}\n\nExecution rules:\n{directive}\n"

    def evaluate_quality_gate(self, sandbox_path: Path) -> EvolutionGateVerdict:
        """Gate 1: Verify zero test regressions and AST anti-tampering."""
        # 1. AST Anti-Tampering Gate
        is_tampered, tamper_msg, _ = detect_test_tampering(sandbox_path)
        if is_tampered:
            return EvolutionGateVerdict(
                gate_name="QualityGate (Anti-Tampering)",
                passed=False,
                details=f"Test tampering detected in candidate harness: {tamper_msg}",
            )

        # 2. Run test suite inside sandbox
        cmd = ["uv", "run", "--with", "pytest", "pytest", "tests/", "-q"]
        try:
            res = subprocess.run(
                cmd,
                cwd=sandbox_path,
                capture_output=True,
                text=True,
                timeout=120,
            )
            passed = res.returncode == 0
            details = "All test assertions passed cleanly (100% pass rate)." if passed else (res.stderr or res.stdout)[-300:]
            return EvolutionGateVerdict(
                gate_name="QualityGate (Test Suite)",
                passed=passed,
                details=details.strip(),
                metrics={"returncode": res.returncode},
            )
        except Exception as exc:
            return EvolutionGateVerdict(
                gate_name="QualityGate (Execution Error)",
                passed=False,
                details=f"Quality gate test run failed with error: {exc}",
            )

    def evaluate_performance_gate(
        self,
        original_prompt: str,
        candidate_prompt: str,
        max_growth_ratio: float = 0.15,
        max_absolute_delta_tokens: int = 40,
    ) -> EvolutionGateVerdict:
        """Gate 2: Enforce strict token budget and frontmatter integrity (Anti-Bloat)."""
        orig_tokens = self.estimate_tokens(original_prompt)
        cand_tokens = self.estimate_tokens(candidate_prompt)
        delta_tokens = cand_tokens - orig_tokens
        growth_ratio = delta_tokens / orig_tokens if orig_tokens > 0 else 0.0

        # Frontmatter validation
        if not candidate_prompt.startswith("---\n") or "\n---\n" not in candidate_prompt:
            return EvolutionGateVerdict(
                gate_name="PerformanceGate (Frontmatter Integrity)",
                passed=False,
                details="Candidate prompt corrupted YAML frontmatter header.",
                metrics={"orig_tokens": orig_tokens, "cand_tokens": cand_tokens},
            )

        # Anti-bloat token threshold check: must not exceed both ratio and absolute delta
        if growth_ratio > max_growth_ratio and delta_tokens > max_absolute_delta_tokens:
            return EvolutionGateVerdict(
                gate_name="PerformanceGate (Token Budget Exceeded)",
                passed=False,
                details=(
                    f"Candidate violates anti-bloat gate: token count grew by {growth_ratio:.1%} "
                    f"(+{delta_tokens} tokens: {orig_tokens} -> {cand_tokens}), exceeding {max_growth_ratio:.0%} limit "
                    f"and {max_absolute_delta_tokens} token threshold."
                ),
                metrics={"orig_tokens": orig_tokens, "cand_tokens": cand_tokens, "growth_ratio": growth_ratio},
            )

        return EvolutionGateVerdict(
            gate_name="PerformanceGate (Anti-Bloat Budget)",
            passed=True,
            details=f"Token budget respected: {orig_tokens} -> {cand_tokens} tokens (+{delta_tokens} tokens, {growth_ratio:.1%}).",
            metrics={"orig_tokens": orig_tokens, "cand_tokens": cand_tokens, "growth_ratio": growth_ratio},
        )

    def evolve_worker(
        self,
        worker_name: str,
        failure_trace: str,
        custom_directive: Optional[str] = None,
        auto_merge: bool = True,
    ) -> EvolutionResult:
        """Execute the full evolution cycle in an isolated worktree."""
        prompt_file = self.prompts_dir / f"{worker_name}.md"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Worker prompt file not found: {prompt_file}")

        orig_prompt = prompt_file.read_text(encoding="utf-8")
        orig_tokens = self.estimate_tokens(orig_prompt)
        root_cause = self.classify_failure(failure_trace)

        # Synthesize candidate refinement
        candidate_prompt = self.synthesize_candidate_prompt(
            current_prompt=orig_prompt,
            root_cause=root_cause,
            custom_directive=custom_directive,
        )
        cand_tokens = self.estimate_tokens(candidate_prompt)

        # Evaluate Gate 2 (Performance / Anti-Bloat) first before spinning up heavy worktree
        perf_verdict = self.evaluate_performance_gate(orig_prompt, candidate_prompt)
        if not perf_verdict.passed:
            res = EvolutionResult(
                worker_name=worker_name,
                root_cause=root_cause,
                original_tokens=orig_tokens,
                candidate_tokens=cand_tokens,
                quality_gate=EvolutionGateVerdict("QualityGate (Skipped)", False, "Skipped due to performance gate failure"),
                performance_gate=perf_verdict,
                accepted=False,
                rejection_reason=perf_verdict.details,
            )
            self._log_result(res)
            return res

        # Spin up ephemeral worktree sandbox for Gate 1 (Quality Gate)
        worker_id = f"evolve_{worker_name}_{int(time.time() * 1000) % 100000}"
        sandbox_dir = self.wt_mgr.create_sandbox(worker_name=worker_id)
        sandbox_prompt = sandbox_dir / "setup" / "2_configure" / "prompts" / f"{worker_name}.md"

        try:
            # Apply mutation in sandbox
            sandbox_prompt.write_text(candidate_prompt, encoding="utf-8")

            # Run Quality Gate in sandbox
            qual_verdict = self.evaluate_quality_gate(sandbox_dir)

            if qual_verdict.passed and perf_verdict.passed:
                # Merge if auto_merge is True
                commit_sha = None
                if auto_merge:
                    commit_msg = (
                        f"evolve({worker_name}): refine prompt for {root_cause}\n\n"
                        f"- Quality Gate: PASS (100% test pass rate)\n"
                        f"- Performance Gate: PASS ({orig_tokens} -> {cand_tokens} tokens)\n"
                        f"- Root Cause: {root_cause}"
                    )
                    self.wt_mgr.merge_sandbox(worker_name=worker_id, squash=True, commit_message=commit_msg)
                    try:
                        commit_sha = subprocess.check_output(
                            ["git", "-C", str(self.repo_root), "rev-parse", "HEAD"], text=True
                        ).strip()
                    except Exception:
                        commit_sha = "head"

                self.wt_mgr.remove_sandbox(worker_name=worker_id)

                res = EvolutionResult(
                    worker_name=worker_name,
                    root_cause=root_cause,
                    original_tokens=orig_tokens,
                    candidate_tokens=cand_tokens,
                    quality_gate=qual_verdict,
                    performance_gate=perf_verdict,
                    accepted=True,
                    commit_sha=commit_sha,
                )
            else:
                # Rejection
                self.wt_mgr.remove_sandbox(worker_name=worker_id)
                res = EvolutionResult(
                    worker_name=worker_name,
                    root_cause=root_cause,
                    original_tokens=orig_tokens,
                    candidate_tokens=cand_tokens,
                    quality_gate=qual_verdict,
                    performance_gate=perf_verdict,
                    accepted=False,
                    rejection_reason=qual_verdict.details,
                )

        except Exception as exc:
            self.wt_mgr.remove_sandbox(worker_name=worker_id)
            res = EvolutionResult(
                worker_name=worker_name,
                root_cause=root_cause,
                original_tokens=orig_tokens,
                candidate_tokens=cand_tokens,
                quality_gate=EvolutionGateVerdict("QualityGate (Crash)", False, str(exc)),
                performance_gate=perf_verdict,
                accepted=False,
                rejection_reason=f"Evolution cycle crashed: {exc}",
            )

        self._log_result(res)
        return res

    def _log_result(self, result: EvolutionResult) -> None:
        """Record the evolution event in the audit ledger."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(result)) + "\n")
