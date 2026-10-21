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
- **74/74 test suite passing**: Full unit & integration coverage including `tests/test_resilience_m6.py`.

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

## 🔥 Prioritized Task Queue — Milestone 6: Production Resilience

- [x] **P6.1 Watchdog & Stagnation Detection** — max 900s wall-clock + 180s stdout stagnation in [`run/cao_auto.py`](../../run/cao_auto.py)
- [ ] **P6.2 CLI Prompt Deadlock Prevention** — non-interactive flags + `[y/N]` auto-responder in worker profiles
- [x] **P6.4 Port 9889 Self-Healing** — health-check probe + zombie daemon cleanup in [`run/cao-run`](../../run/cao-run)
- [ ] **P6.5 Setup Wizard `cao-init`** — auto-detect CLIs, generate tailored `cao.config.toml`, 1-click compile
- [x] **P6.6 Memory Pruning** — `cao-memory prune` / `vacuum` subcommands to prevent memory dilution
- [x] **P6.3 Git Worktree Isolation** — `WorktreeManager` in [`run/cao_worktree.py`](../../run/cao_worktree.py) for parallel workers *(most complex, last)*

---

## 🔮 Backlog: Orca (`stablyai/orca`) Feature Adoptions

- [ ] **Automated Worktree Lifecycle** — Task-level worktree provision (`git worktree add`), branch isolation, and auto-squash merge upon passing verification.
- [ ] **UI Context Capture ("Design Mode")** — Lightweight CLI/browser hook extracting live DOM element, CSS styles, and viewport screenshot directly into `codex_worker` prompt.
- [ ] **TokenMaster Multi-Account Rotation** — Hot-swap API keys/profiles across multiple accounts of the same provider on 429 before cross-tier downgrade.
- [ ] **Remote SSH Worktree Workers** — Run heavy workers (e.g. local vLLM / Hermes) on remote GPU machines over SSH worktrees while managing locally.

