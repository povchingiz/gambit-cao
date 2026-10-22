# now.md — wcao · active focus

> **Branch:** `1000x`
> **Active Plan:** 1000x Workstation Fleet Conductor & Laya Routing Engine
> **Rule:** NEVER run `git push` without explicit user confirmation.

---

## ✅ What's Done (Milestone 1000x: Fleet Conductor & Sandboxes)

- **Workstation Fleet Conductor (`cao-fleet`)**: Live multi-project status tracking, task inspection, and cross-project dispatching across `llmaas`, `3DAang`, `nowait-study`, `dycom-demo`, and `cao-crew` (`run/cao_fleet.py`, `run/cao-fleet`, `tests/test_fleet.py`).
- **Laya System-1 Intent & Risk Router (`cao-laya`)**: Zero-overhead rule-based intent router mapping tasks to optimal worker engines (`claude_worker`, `coder_worker`, `codex_worker`, `antigravity_worker`, `analyst_worker`) and anti-babysitting reflex gate (`run/cao_laya_router.py`, `run/cao-laya`, `tests/test_laya.py`).
- **Autonomous Laya Binding in `cao-auto`**: Dynamic worker and model binding in headless DAG execution (`run/cao_auto.py`).
- **Git Worktree Isolation Sandboxes (`cao-sandbox`)**: Ephemeral speculative execution in `wcao/sandboxes/<worker>` with automated squash-merge upon test verification (Milestone P6.3 complete: `run/cao_worktree.py`, `run/cao-sandbox`, `tests/test_worktree.py`).
- **Cross-Project Workstation Memory**: Shared episodic knowledge layer in `~/.cao/fleet_memory.sqlite` accessible via `cao-memory --fleet` and auto-recalled in `cao-auto`.
- **Milestone 6 Production Resilience (`P6.1`, `P6.3`, `P6.4`, `P6.6`)**:
  - `P6.1` Watchdog (900s wall-clock) & stdout stagnation (180s) detection with fallback self-healing in `run/cao_auto.py`.
  - `P6.4` Port 9889 stale/zombie daemon self-healing (`heal_stale_daemon` in `run/cao_lib.py` & wired into `run/cao-run`).
  - `P6.6` Episodic memory pruning & FTS5 optimization (`prune_memories`, `vacuum_memory` in `run/cao_memory.py` & `run/cao-memory`).
- [x] **Playwright Autonomous Full-Stack QA & UI/UX Auditor (`cao-qa`)**: Comprehensive Playwright auditing engine (`run/cao_qa.py`, `run/cao-qa`, `tests/test_cao_qa.py`, `wcao/skills/playwright-qa-ux-auditor.md`) featuring full-stack log correlation, destructive action safety guards, smart form auto-filling, 2-hop modal exploration, visual error screenshots with high-contrast outlines, dual-viewport testing (Desktop & Mobile), and direct `cao-fleet` remediation dispatch.
- **77/77 test suite passing**: Full unit & integration coverage across all modules.

---

## ✅ What's Done (Milestones 1–5)

All shipped — see [`archive/`](archive/) for historical specs.

- Core provisioner, prompt renderer, MCP inheritance, tmux lifecycle
- `cao-auto` autonomous DAG dispatcher + Telegram telemetry
- Universal 429 fallback / TokenMaster quota routing
- `cao-limits` CLI — live quota inspector (visual utilization bars)
- Repo root detection, scoped tmux sessions, `cao-stop --project`
- Context compactor (Hermes 50% rule) — `cao_compactor.py`
- Procedural memory (`wcao/skills/`) + SQLite FTS5 episodic memory
- `hermes_worker` engine integration + conformance test suite
- `cao-plan` goal decomposer → cycle-free DAG in `wcao/tasks.json`
- Anti-test-tampering gate (`cao_tamper.py`)
- `cao-run` fix: early symlink resolution prevents `$HERE: unbound variable` crash ([`wcao/plans/2026-09-22-cao-run-fix.md`](2026-09-22-cao-run-fix.md))
- Shorthand supervisor flag: `--sv <engine>` (`agy`, `codex`, `claude`, `opencode`, `hermes`) in `run/cao-run`
- `code_supervisor.md` prompt streamlined to strict orchestration-only mandate
- Configured bulk models for OpenCode (`Kimi-K3`, `GLM-5.3`, `DeepSeek-V4-Pro`)
- 58/58 test suite passing (`tests/test_cao_run_flags.py`)
- Orca ADE architecture comparison & backlog mapped

---

## 🔥 Prioritized Task Queue

- [x] **[antigravity_worker]** Implement cao-qa Playwright Autonomous QA, Full-Stack Log Correlator & UI/UX Redundancy Auditor CLI and Skill (wcao/plans/2026-10-22-playwright-qa-ux-auditor.md) *(Model: gemini-3.8-flash-high)* — Milestone 6: Production Resilience

- [x] **P6.1 Watchdog & Stagnation Detection** — max 900s wall-clock + 180s stdout stagnation in [`run/cao_auto.py`](../../run/cao_auto.py)
- [x] **P6.2 CLI Prompt Deadlock Prevention** — non-interactive flags (`CI=1`, `DEBIAN_FRONTEND=noninteractive`, `GIT_TERMINAL_PROMPT=0`) in [`run/cao-run`](../../run/cao-run) + prompt deadlock detector in [`run/cao_auto.py`](../../run/cao_auto.py)
- [x] **P6.4 Port 9889 Self-Healing** — health-check probe + zombie daemon cleanup in [`run/cao-run`](../../run/cao-run)
- [x] **P6.5 Setup Wizard `cao-init`** — 1-click auto-detect CLIs, generate tailored `cao.config.toml`, compile via `apply.sh` ([`run/cao_init.py`](../../run/cao_init.py))
- [x] **P6.6 Memory Pruning** — `cao-memory prune` / `vacuum` subcommands to prevent memory dilution
- [x] **P6.3 Git Worktree Isolation** — `WorktreeManager` in [`run/cao_worktree.py`](../../run/cao_worktree.py) for parallel workers
- [x] **1000x Autonomous Closed-Loop Self-Healing (`cao-repair`)** — End-to-end bug discovery, sandbox worktree isolation, surgical remediation, re-audit verification & auto-squash merge ([`run/cao_repair.py`](../../run/cao_repair.py), [`run/cao-repair`](../../run/cao-repair))

---

## 🚀 80/80 Test Suite Passing
Full unit & integration test coverage across the entire system.

---

## 🔮 Backlog: Orca (`stablyai/orca`) Feature Adoptions

- [ ] **Automated Worktree Lifecycle** — Task-level worktree provision (`git worktree add`), branch isolation, and auto-squash merge upon passing verification.
- [ ] **UI Context Capture ("Design Mode")** — Lightweight CLI/browser hook extracting live DOM element, CSS styles, and viewport screenshot directly into `codex_worker` prompt.
- [ ] **TokenMaster Multi-Account Rotation** — Hot-swap API keys/profiles across multiple accounts of the same provider on 429 before cross-tier downgrade.
- [ ] **Remote SSH Worktree Workers** — Run heavy workers (e.g. local vLLM / Hermes) on remote GPU machines over SSH worktrees while managing locally.

