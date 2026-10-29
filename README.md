# ♜ GAMBIT — Autonomous Multi-Agent Engineering Fleet

> **Orchestrate your frontier AI coding CLI engines into an autonomous, self-evolving engineering fleet — powered by CAO Architecture.**

[![Interactive Deck](https://img.shields.io/badge/Presentation%20Deck-16%20Slides-6366f1?style=flat-square&logo=googleslides&logoColor=white)](https://povchingiz.github.io/gambit-cao/)
[![Sequence Diagram](https://img.shields.io/badge/Architecture-Sequence%20Diagram-06b6d4?style=flat-square&logo=diagramsdotnet&logoColor=white)](https://povchingiz.github.io/gambit-cao/#16)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-104%20Passing-emerald)](tests/)

---

## The Chess Taxonomy

GAMBIT organizes multi-agent coding like a grandmaster orchestrating the board:

```
                    ♔ GRANDMASTER (You)
                 Strategic Intent & Approvals
                             │
                             ▼
                    ♜ THE ROOK (Master Conductor)
                 One Terminal to Rule Them All.
                 Controls the ranks and files across all projects.
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
  ♞ KNIGHT: Project A                     ♞ KNIGHT: Project B
  Stationed Project Supervisor            Stationed Project Supervisor
  (Local repo & wgambit/ context)         (Local repo & wgambit/)
         │                                       │
    ┌────┴────┐                             ┌────┴────┐
    ▼         ▼                             ▼         ▼
 ♝ BISHOP   ♙ PAWN                       ♝ BISHOP   ♙ PAWN
 Specialist  Bulk Worker                 Specialist  Bulk Worker
  (Claude)   (OpenCode)                   (Codex)    (DeepSeek)
```

- ♔ **Grandmaster (You):** Gives natural language goals, answers bubble-up questions, and confirms heavy operations.
- ♜ **The Rook (Master Conductor):** The overarching terminal coordinating all projects across your workstation.
- ♞ **The Knights (Project Supervisors):** Stationed in each project repository in background tmux sessions (`gambit run`).
- ♝ **The Bishops (Specialists):** Deep reasoning engines (Claude for architecture/contracts, AGY for whole-repo analysis).
- ♙ **The Pawns (Bulk Workers):** High-throughput workers (OpenCode, DeepSeek, GLM) typing boilerplate, schemas, and tests.

---

## TL;DR

> **`gambit` turns your fragmented terminal AI tools (`claude`, `codex`, `agy`, `opencode`, `copilot`, `hermes`) into a unified, self-repairing engineering fleet managed inside background `tmux` sessions.**

* ♜ **One Terminal to Rule Them All:** Talk to **The Rook** via `gambit`. The Rook coordinates Stationed Knights across all repos on your machine.
* 🗣️ **Natural Language Cross-Project Missions:** Just type `gambit "In backend add JWT auth, in mobile add login view"` — no awkward flags needed.
* 🛡️ **Safety Confirmation Gate:** Heavy QA-UIX browser crawls and worktree repairs prompt for Grandmaster confirmation (`[y/N]`) so you never trigger them by accident (pass `-y` or `--yolo` for autonomous runs).
* 🧪 **5-Vector Full-Stack QA-UIX (`gambit test`):** Playwright crawler checking DOM ergonomics, JS telemetry, backend payloads, CORS transport, and credential/secret leaks.
* 🔄 **Closed-Loop Auto-Repair:** Discovered regressions automatically spawn an isolated git worktree sandbox, implement fixes, re-audit to verify 100/100 score, and squash-merge.
* ⚡ **Space & Dash Commands:** Both `gambit <command>` and `gambit-<command>` are first-class CLI citizens.
* 🏛️ **CAO Heritage Preserved:** Built proudly on the rock-solid AWS Labs `cli-agent-orchestrator` foundation with zero subscription markups.

```bash
git clone https://github.com/povchingiz/gambit-cao.git ~/gambit-cao && cd ~/gambit-cao
./install.sh
```

---

### Quick Navigation
* ⚡ **[TL;DR](#tldr)** — 30-second summary: architecture, chess taxonomy, and quickstart
* 🎮 **[Gambit Command Cheatsheet](#gambit-command-cheatsheet)** — unified space and dash commands to rule the board
* 🧪 **[5-Vector Full-Stack QA-UIX (`gambit test`)](#5-vector-full-stack-qa-uix-engine-gambit-test)** — DOM ergonomics, console telemetry, payloads, CORS & secrets
* 🔄 **[Closed-Loop Self-Repair (`gambit repair`)](#autonomous-closed-loop-self-repair-gambit-repair)** — isolated worktree sandboxes, automated diagnosis & merge
* 🎬 **[Frontier 3D Avatar & Video Rendering (`gambit render`)](#frontier-3d-avatar--video-rendering-gambit-render)** — HunyuanVideo-Avatar 13B MM-DiT + Voicebox neural voice sync
* 🛡️ **[Kernel-Secured AI Agent Isolation (`gambit harness`)](#kernel-secured-ai-agent-isolation--zero-secret-runtime-gambit-harness)** — Linux Landlock LSM jail & zero-secret environment
* 🔌 **[Cross-Engine Skills & Everything Claude Code (`gambit plugins`)](#cross-engine-skills-mcp--everything-claude-code-ecc-integration-gambit-plugins)** — broadcast skills & ECC to all engines
* 🧬 **[Protected Prompt Self-Evolution (`gambit evolve`)](#protected-prompt-self-evolution-gambit-evolve)** — Dual-Gate prompt optimization & regression protection
* 🤖 **[AI Assistant Onboarding](#-first-time-let-your-ai-assistant-guide-you)** — ask your AI agent to set up gambit automatically (`AGENTS.md` standard)
* 🌐 **[Interactive Slides](https://povchingiz.github.io/gambit-cao/)** — 16 bilingual slides (RU/EN), dark/light mode, and rival benchmarks
* 🔄 **[Execution Sequence Diagram](https://povchingiz.github.io/gambit-cao/#16)** — native visual trace from North Star goal to verified commit
* ⚠️ **[The Problem](#the-problem)** — 6 fatal flaws of single-agent and uncoordinated coding
* 🧩 **[The Solution](#the-solution-a-unified-engineering-squad)** — specialist workforce, economic asymmetry, and DAG execution
* 🚀 **[Installation & Setup](#1-install-once)** — 5-minute bootstrap and configuration
* 🧠 **[Hermes Learning & Memory (`gambit memory`)](#hermes-learning--memory-system)** — SQLite FTS5 episodic storage and now.md checkpoints
* 🛡️ **[Autonomous Self-Healing (`gambit auto`)](#autonomous-execution--self-healing-gambit-auto)** — AST anti-tampering, 5-vector audit gate, and L2 escalation

---

## Gambit Command Cheatsheet

All commands support both **space syntax** (`gambit <cmd>`) and **dash syntax** (`gambit-<cmd>`).
> 💡 **Backwards Compatibility:** All legacy `crew <cmd>` and `cao-*` commands remain 100% functional as direct aliases.

| Space Command | Dash Command | Legacy Alias | Description & Typical Usage |
|---|---|---|---|
| `gambit` | `gambit` | `cao-supervisor` | **The Rook Master Terminal:** attaches directly to the active Rook supervisor in tmux, or displays the active Chessboard if idle. |
| `gambit fleet` | `gambit-fleet` | `crew fleet` / `cao-fleet` | **Chessboard & Fleet Conductor:** live status of Stationed Knights (projects), active missions, token spend, and provider quotas. |
| `gambit "<mission>"` | `gambit auto "<m>"` | `crew auto` / `gambit auto` | **Natural Language Cross-Project Mission:** parses goals, plans tasks in DAGs, enforces file locks, watches quotas, and self-heals regressions. |
| `gambit brief "<idea>"` | `gambit brief` | — | **Tripartite Brief Sparring (Phase 1):** triggers adversarial sparring between The Rook and Bishop Architect to freeze 12-factor contracts before coding. |
| `gambit contracts` | `gambit-contracts` | — | **Locked Architecture Contracts:** displays and validates all frozen interface schemas and briefs in `wgambit/contracts/`. |
| `gambit test <target>` | `gambit-test` | `crew test` / `cao-qa` | **5-Vector Full-Stack QA-UIX Engine:** Playwright crawler testing DOM ergonomics, JS console telemetry, backend payloads, CORS headers, and secret leaks. |
| `gambit repair <target>` | `gambit-repair` | `crew repair` / `cao-repair` | **1000x Autonomous Closed-Loop Self-Repair:** spins up an isolated git worktree sandbox (`.git/worktrees/`), diagnoses failure, implements patch, verifies, and squash-merges. |
| `gambit render <prompt>` | `gambit-render` | `cao-render` | **Frontier 3D Avatar & Video Rendering:** Tencent HunyuanVideo-Avatar (13B MM-DiT) batch rendering + Jamie Pine's Voicebox / Kokoro neural voice sync + ARKit 52 visemes + FFmpeg packaging. |
| `gambit harness <cmd>` | `gambit-harness` | — | **Kernel-Secured AI Agent Isolation & Zero-Secret Runtime:** Linux Landlock LSM sandbox jail restricting agent filesystem access + automatic API key stripping from environment. |
| `gambit plugins` | `gambit-plugins` | `cao-plugins` | **Cross-Engine Skills & MCP Broadcaster:** distributes Claude plugins, MCP servers, and **Everything Claude Code (ECC)** skills to all engines (`codex`, `agy`, `opencode`, `copilot`). |
| `gambit sandbox <action>` | `gambit-sandbox` | `crew sandbox` / `cao-sandbox` | **Ephemeral Git Sandboxes:** manages isolated git worktrees (`create`, `test`, `merge`, `list`, `destroy`) for zero-risk multi-agent coding. |
| `gambit evolve <worker>` | `gambit-evolve` | `crew evolve` / `cao-evolve` | **Protected Prompt Self-Evolution Loop:** benchmarks mutated prompts with Dual-Gate (Quality + Anti-Bloat) harness and automatic golden rollback. |
| `gambit memory <cmd>` | `gambit-memory` | `gambit memory` | **Hermes Continuous Learning System:** SQLite BM25 FTS5 episodic storage (`store`, `recall`, `list`) injected before worker dispatch. |
| `gambit run` | `gambit-run` | `crew run` / `gambit run` | **Launch The Rook:** boots the master conversational supervisor pane in tmux (`--provider agy/claude/codex`). |
| `gambit terminal` | — | `tmux attach` | **Supervisor Terminal:** attaches directly to the active interactive supervisor session (`tmux attach -t cao-supervisor`). |
| `gambit stop` | `gambit-stop` | `crew stop` / `gambit stop` | **Clean Board Termination:** halts all background Knights, Daemons, and Rook sessions cleanly (`--keep-server` to keep daemon running). |
| `gambit doctor` | `gambit-doctor` | `crew doctor` / `gambit doctor` | **Pre-Flight Diagnostics:** validates binaries, daemon ports, CLI logins, and API endpoints (`--init` for setup wizard, `--update` for updater). |
| `gambit tokens` | `gambit-tokens` | `gambit tokens` | **TokenMaster Efficiency Scraper:** extracts token spend and cost per engine across local JSONL/SQLite stores. |
| `gambit migrate` | `gambit-migrate` | — | **Workspace Migration:** automatically checks and migrates legacy `wcao/` workspaces to canonical `wgambit/` with backward-compatible symlinks. |

---

### 🤖 First Time? Let Your AI Assistant Guide You

If you are using **Cursor, Claude Code, OpenAI Codex, Windsurf, GitHub Copilot, or Google Antigravity**, you don't need to configure everything manually. This repository includes universal cross-agent instructions in [`AGENTS.md`](AGENTS.md), [`CLAUDE.md`](CLAUDE.md), and [`.cursorrules`](.cursorrules).

Just open this repository in your IDE or terminal and prompt your AI assistant:
> *"Help me set up gambit-cao and check my environment"*

Your AI assistant will automatically:
1. Run `run/gambit doctor` to test your local tools, daemon port, and existing CLI logins.
2. If any CLI is unauthenticated, give you the exact terminal command (`claude /login`, `codex login`, etc.).
3. Explain how to launch either an interactive Tech Lead team (`run/gambit run`) or autonomous DAG tasks (`run/gambit auto`).

> [!NOTE]
> **Origins & Lineage:** This project originated as an automated setup and configuration harness for AWS Labs' open-source [`cli-agent-orchestrator`](https://github.com/awslabs/cli-agent-orchestrator) (CAO). It has since expanded significantly beyond the original launcher into an autonomous multi-engine platform—adding the **`wcao/` project standard**, **Hermes episodic & procedural memory**, **proactive TokenMaster quota intelligence**, **headless DAG execution (`cao_auto`)**, and **anti-tamper self-healing audit gates**.

---

### The Problem
* **Siloed CLI Agents:** Claude Code, Codex, Antigravity/Gemini, OpenCode, and Hermes each live in isolated terminal windows with no shared memory, contracts, or task delegation.
* **Token & Quota Burn:** Using expensive frontier models for mundane boilerplate, migrations, or whole-repo reading exhausts rate limits and quotas rapidly.
* **Context Decay & Amnesia:** As agent sessions grow, token context degrades, leading to hallucinated edits, broken syntax, and forgotten lessons across sessions.
* **Race Conditions in Multi-Agent Coding:** Running multiple autonomous agents simultaneously on the same codebase leads to file collisions and overwritten code.
* **Premature Completion without Verification:** Most agent setups stop as soon as code is written—without running tests, verifying AST syntax, or fixing their own regressions.

---

### The Solution: A Unified Engineering Squad
**CAO (CLI Agent Orchestrator)** turns individual CLI tools into an autonomous, fault-tolerant software engineering system:

* **Tech Lead Supervisor (Claude / AGY):** Plans architecture, decomposes requirements into Directed Acyclic Graphs (DAGs), and delegates.
* **Specialist Workforce:** Routes tasks to the best-fit engine—Claude for hard domain logic, high-throughput models (DeepSeek/OpenCode) for bulk typing, Gemini/AGY for massive-context codebase analysis, Codex for UI, and Hermes for open-source reasoning.
* **Deterministic Execution & Safety Locks:** A headless execution engine (`cao_auto`) schedules tasks, enforces file-level disjointness locks, and prevents parallel collision.
* **Autonomous Closed-Loop Quality:** An aggressive postflight audit gate tests and scans code before marking any task complete, with an automatic self-healing loop that fixes failures without human intervention.
* **Hermes Cross-Engine Memory:** Context compactor (Hermes 50% rule) prevents token blowout, while SQLite FTS5 episodic memory stores lessons learned so future workers never repeat past mistakes.

---

### Core Capabilities at a Glance

| Capability | How CAO Delivers It |
|---|---|
| **Multi-Engine Swarm** | Unifies Claude, Codex, OpenCode, Antigravity, Copilot, and Hermes into one orchestrated pipeline. |
| **Token-Aware Efficiency** | Proactive TokenMaster quota monitoring, automatic high-utilization model swaps, context-size advisories, and 50% window compaction. |
| **Zero-Collision Concurrency** | Task DAG scheduler evaluates dependencies and locks files dynamically across parallel workers. |
| **Autonomous Self-Healing** | Postflight AST checks, security audits, and test suites trigger automatic remediation loops when regressions occur. |
| **Persistent Project Brain (`wgambit/`)** | Single source of truth for architectural diagrams (`design/*.mmd`), active plans (`now.md`), and reusable skills (`skills/`). Backward-compatible `wcao/` alias maintained. |
| **Quota Resilience** | Real-time detection of 429 rate limits with automatic fallback to secondary engines and supervisor failover. |

---

```
gambit run  →  The Rook (Claude / AGY Master Supervisor)  →  assign  →
    ┌ ♝ Bishop Architect   claude       architecture, contracts, hard logic
    ├ ♙ Pawn Coder         opencode     implementation, schemas, CRUD (cheap model)
    ├ ♝ Bishop Analyst     gemini/agy   whole-repo maps, long docs, multimodal (huge context)
    ├ ♝ Bishop Codex       codex        frontend / UI
    ├ ♝ Bishop Antigravity gemini/agy   QA, tests, security review
    ├ ♙ Pawn Copilot       copilot      GitHub PRs, CI/CD deploy
    └ ♙ Pawn Hermes        hermes       open-source reasoning, autonomous fallback
```

**Why it saves tokens:** the expensive model (Claude) is spent only on design,
contracts, and coordination. Reading a big repo goes to the huge-context analyst;
the bulk of the typing goes to a cheap coding model against Claude's blueprint.
`gambit tokens` shows you exactly where the tokens went (per day, or cao-only).

**Fault-tolerant by default:** if Claude's quota or login is down, the supervisor
falls back to another engine automatically — `gambit run` never dead-ends (see
*Supervisor fallback*).

Roles above are the **defaults** — every one is editable (see *Configure*).

> **Windows:** not supported natively (CAO needs tmux + POSIX ptys). Use WSL2 —
> see [WINDOWS.md](wgambit/docs/WINDOWS.md). Inside WSL these steps apply unchanged, if the
> repo lives in your WSL home (not `/mnt/c`).

## Repo layout — by lifecycle phase

```
setup/                                                     ← install & configure, in order
  1_install/    bootstrap.sh · bootstrap.ps1 · patch_*.py      ← run once
  2_configure/  cao.config.toml · prompts/*.md                 ← edit these
  3_apply/      apply.sh · render_config.py · inherit_*.py     ← push edits · share MCP
run/            gambit · gambit-fleet · gambit-test · gambit-repair · gambit-harness · gambit-render · …
                (executable verbs symlinked to ca-* / gambit_* engines)
tests/          pytest suite (103 unit & integration tests)
wgambit/        plans/ · design/ · audit/ · docs/ · tasks.json ← project state, contracts, memory (wcao/ alias)
index.html      the deck (served by GitHub Pages)
.generated/     settings.json · opencode.json                  ← auto-written locally (gitignored)
```

Edit only in `setup/2_configure/`. Everything else is machinery. Never edit the live
files under `~/.aws` or `~/.config` directly — they are generated.

> [!TIP]
> **Complete Command Cheatsheet:** See the [Master Gambit Cheatsheet](#gambit-command-cheatsheet) above for all 16 unified verbs.

---

## 5-Vector Full-Stack QA-UIX Engine (`gambit test`)

`gambit test` (or `crew test` / `cao-qa`) is an autonomous QA, telemetry, and ergonomics auditor powered by Playwright. It crawls local web applications, SPAs, and server endpoints to assess overall product health before shipping:

```bash
# Run headless QA-UIX audit against local dev server
gambit test http://localhost:3000

# Run headed with automated click exploration and custom output
gambit test http://localhost:8080 --headed --explore --output wgambit/audit/qa-report.md
```

### The 5 Verification Vectors:
1. **Vector 1: UI/UX Ergonomics & Accessibility:**
   - Detects viewport clipping and horizontal page overflow.
   - Identifies dead buttons (unclickable, disabled without tooltip, or zero visual response).
   - Flags duplicate button labels or misleading text that induces user friction.
2. **Vector 2: Frontend JS Telemetry & Console Health:**
   - Captures uncaught JavaScript runtime exceptions (`pageerror`).
   - Surfaces all `console.error` and `console.warn` occurrences with stack traces.
3. **Vector 3: Backend & Network Payloads:**
   - Intercepts all XHR/Fetch network traffic.
   - Alerts on HTTP 4xx client errors and 5xx backend server crashes.
   - Measures API latency to flag slow or hung payload responses.
4. **Vector 4: CORS & Transport Security:**
   - Verifies cross-origin resource sharing headers.
   - Detects dangerous wildcard CORS configurations with credentials allowed (`Access-Control-Allow-Origin: *` with credentials).
5. **Vector 5: Secret & Credential Leak Scanner:**
   - High-entropy and pattern scanner continuously inspecting DOM HTML, console logs, and outgoing API request URLs.
   - Catches accidentally leaked OpenAI API keys (`sk-...`), Anthropic keys (`sk-ant-...`), AWS credentials (`AKIA...`), Bearer/JWT tokens, and raw database connection strings.

Any critical failure deducts health score points and generates an actionable remediation plan ready for `gambit repair`.

---

## Autonomous Closed-Loop Self-Repair (`gambit repair`)

When tests fail or `gambit test` uncovers security or UI/UX regressions, `gambit repair` closes the loop completely autonomously:

```bash
# Automatically repair issues found in the latest QA audit
gambit repair wgambit/audit/qa-report.md

# Repair a specific project test failure
gambit repair tests/test_auth.py
```

```
[Trigger: QA Failure / Test Break]
                │
                ▼
  [1. Isolated Git Worktree Sandbox] (via `gambit sandbox`)
                │
                ▼
  [2. Architect Escalation] (Claude / AGY diagnose root cause)
                │
                ▼
  [3. Worker Patch Implementation] (High-throughput coding model)
                │
                ▼
  [4. AST Anti-Tampering & Verification Gate] (Ensures tests weren't weakened)
                │
                ▼
  [5. Clean Squash-Merge & Report] (Merged back into main branch)
```

1. **Isolation:** Runs entirely within an ephemeral Git worktree sandbox (`.git/worktrees/...`). Production branches remain completely untouched.
2. **Anti-Tampering:** Ensures the worker does not simply delete failing assertions or insert bypasses (`assert True`).
3. **Squash-Merge:** Once all tests pass and postflight audits succeed, the fix is squash-merged into the working branch with an audit trail in `wgambit/audit/`.

---

## Frontier 3D Avatar & Video Rendering (`gambit render`)

`gambit render` connects the GAMBIT fleet orchestrator directly to state-of-the-art generative video and neural speech engines:

```bash
# Render full clinical case video with Tencent HunyuanVideo-Avatar & Voicebox
gambit render "Explain CBCT mandibular canal proximity and 3D bone density" --engine hunyuan --voicebox

# Generate real-time lightweight WebGL avatar audio-viseme package (zero VRAM requirement)
gambit render "Autonomous agent task completed successfully" --engine webgl --voicebox --output build/avatar.mp4
```

### Studio Architecture Capabilities:
1. **Tencent HunyuanVideo-Avatar (13B MM-DiT):**
   - Studio batch diffusion pipeline supporting high-fidelity 720p/1080p full-body avatar generation.
   - VRAM Hardware Probe: automatically detects local GPU VRAM (>24GB for local inference, or seamlessly routes to cloud inference endpoints).
2. **Jamie Pine's Voicebox / Kokoro-82M Neural Speech:**
   - Ultra-realistic, emotion-conditioned voice synthesis paired with our procedural CPU formant fallback (`voice_cloner.py`).
   - Extracts Audio-Emotion Motion priors (AEM) to control facial micro-expressions.
3. **Apple ARKit 52 Blendshape Viseme Synchronization:**
   - 60 FPS deterministic viseme curve extraction (`jawOpen`, `mouthFunnel`, `browInnerUp`) synchronized directly with audio waveform frequencies.
4. **Automated FFmpeg Cinema Packaging:**
   - Packages synchronized audio, video frames, and viseme sidecar JSON into production-ready web and mobile video containers.

---

## Kernel-Secured AI Agent Isolation & Zero-Secret Runtime (`gambit harness`)

Autonomous coding agents executing shell commands represent an inherent security risk if left unconfined. `gambit harness` provides **kernel-enforced Landlock LSM (Linux 5.13+) sandboxing and automated credential stripping**:

```bash
# Run untrusted agent worker or test harness in strict Landlock jail
gambit harness run/cao-worker --role coder_worker

# Strict isolation: read-only root, read/write project workspace only, zero home-directory access
gambit harness --strict bash -c "uv run pytest tests/"
```

### Kernel Guardrails:
* 🔒 **Landlock LSM Filesystem Confinement:** At the Linux kernel syscall level, worker processes are barred from reading outside their designated repository and Python virtualenv. Access to `~/.ssh`, `~/.aws`, `~/.gnupg`, and user home configurations returns hard `EACCES` permission denied errors.
* 🛡️ **Zero-Secret Memory Runtime:** Strips dangerous API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `LOCAL_API_KEY`, AWS credentials) from the child environment. Workers authenticate exclusively through the orchestrator daemon's unix domain socket.
* 📜 **Tamper-Proof Audit Logging:** All jailed syscall attempts and command outputs are recorded in `wgambit/audit/harness.log`.

---

## Protected Prompt Self-Evolution (`gambit evolve`)

Worker system prompts (e.g. `coder_worker`, `analyst_worker`) are living code. `gambit evolve` runs an automated optimization harness to refine system instructions based on past execution history and benchmark test suites:

```bash
# Evolve coder_worker prompt against local benchmark harness
gambit evolve coder_worker --task-dir benchmarks/coder --iterations 3

# Dry run to preview candidate mutations without writing to disk
gambit evolve coder_worker --dry-run
```

### The Dual-Gate Harness:
* 🛡️ **Quality Gate:** The mutated prompt must achieve 100% test pass rate on all canonical regression tasks. Any regression triggers an immediate, zero-latency rollback to the golden prompt checkpoint.
* 📏 **Anti-Bloat Gate:** Prompt mutations that introduce unnecessary fluff, repetitive tokens, or excessive prompt bloat are penalized and rejected, keeping agent system prompts razor-sharp and token-efficient.
* 💾 **Golden Checkpoints:** All validated improvements are saved with atomic versioning under `wgambit/evolve/history/` and compiled to the live store via `apply.sh`.

Environment knobs (all optional): `CAO_SUPERVISOR_PROVIDER` forces the supervisor
engine · `CAO_FALLBACK_PROVIDER` sets the auto-retry engine · `LOCAL_API_KEY`
(in `.env`) authenticates the coding-worker endpoint.

## 1. Install (once)

```sh
git clone https://github.com/povchingiz/gambit-cao.git ~/gambit-cao && cd ~/gambit-cao
cp .env.example .env               # set LOCAL_API_KEY (bulk-worker endpoint key)
./install.sh                       # recommended one-command setup
# or, step by step:
./setup/1_install/bootstrap.sh
```

`./install.sh` is the **recommended one-command installer**: it runs the bootstrap
installer, walks you through the interactive onboarding and native CLI logins
(`claude`, `codex`, `agy`, `gh auth login`), and finishes with the pre-flight
`gambit doctor` check — everything from the section above in a single step.

Flags: `--inherit-mcp` (give your existing Claude MCP servers to the workers),
`--with-kodeks` (dev standard — read its section first), `--with-guard-hook`.

Prerequisites: macOS needs [Homebrew](https://brew.sh); Linux needs `sudo` (for
`apt`). Scripts clone executable — no `chmod` needed.

### Upgrades & Existing Tenant Updates

Already have gambit-cao installed? Update with one command:

```sh
gambit doctor --update              # or: ./update.sh
```

`gambit doctor --update` (a thin wrapper around `./update.sh` → `run/gambit doctor --update`) keeps an
existing install current:

1. **Pulls the latest code** (`git pull --ff-only`; skips safely if you have local changes).
2. **Re-applies site-packages patches** that `cao update` silently wipes (e.g. the `wait_for_shell` pyte patch).
3. **Refreshes the `~/.local/bin` symlinks** so all `cao-*` helpers point at the new code.
4. **Re-renders configs and re-registers worker profiles** (`./setup/3_apply/apply.sh`), then restarts the daemon.
5. **Runs the pre-flight `gambit doctor` check** to verify health.

Every step is idempotent — safe to re-run at any time. Flags:
- `--full` — also update the worker CLIs (claude, codex, opencode) via npm.
- `--npm` — only update the worker CLIs via npm, skip everything else.
- `-y` — auto-confirm prompts (non-interactive).

After running `cao update` (the upstream AWS CLI's own updater), re-run
`gambit doctor --update` — it restores the patches that upstream update erases.

### Native CLI Authentication (Pre-Flight Terminal Logins)

> **Zero Credential Sharing:** CAO never asks for your web account passwords or proxies your session keys. You authenticate once natively in your terminal using the official vendor CLIs. CAO simply connects to these pre-authenticated CLI sessions inside background `tmux` panes:

```sh
claude          # Anthropic subscription (/login on first prompt)
codex login     # OpenAI subscription (ChatGPT / API sign-in)
agy             # Google Antigravity / Gemini sign-in
gh auth login   # GitHub Copilot CLI subscription (if using copilot_worker)
```

## 2. Configure — one file

Edit `setup/2_configure/cao.config.toml`, then `./setup/3_apply/apply.sh`. That's the loop.

| Section | Controls |
|---------|----------|
| `[orchestrator]` | supervisor, default provider, port, max workers, worktree isolation |
| `[endpoint]` | bulk-worker `base_url`, `models`, `default_model` |
| `[workers.*]` | each worker's `provider` and `model` |
| `[profiles]` | which profiles register, in what order |

`apply.sh` renders the toml into `~/.config/cao/settings.json`,
`~/.aws/opencode/opencode.json`, and each worker's frontmatter, re-registers
them, and offers to restart the server. Renaming a worker is safe: `apply.sh`
prunes the old profile from every store cao uses, so no ghost is left behind.

**Coding worker model.** The coding role (`coder_worker`) runs the cheap,
high-volume half of the work through `opencode` against any OpenAI-compatible
endpoint — set `[endpoint]` `base_url` to OpenRouter or another gateway and pick
a low-cost model. If you'd rather not run a separate cheap endpoint, set
`workers.coder_worker.provider` to `claude_code`, `codex`, or `antigravity_cli`
and the coding role runs on that engine instead — no external key needed.

## 3. Roles — who does what, from one place

Every role lives in `[workers.*]` in `cao.config.toml`:

```toml
[workers.codex_worker]
provider = "codex"                       # which engine
model    = "..."                         # optional (opencode only)
aliases  = ["codex", "frontend", "ui"]   # how the supervisor routes to it
focus    = "React/Vue/Svelte, CSS, UI"   # what it does
```

`apply.sh` writes `provider`/`model` into the worker's frontmatter **and
regenerates the supervisor's routing table** from `aliases` + `focus` — so this
one block controls engine, model, and responsibility. Change `focus`/`aliases`
to reassign work; change `provider` to move a role onto another engine.

Only the **detailed prompt** (execution rules) lives separately, in
`setup/2_configure/prompts/<worker>.md` below the frontmatter — edit it there for
fine behavior. `apply.sh` never touches that text; it only regenerates the
supervisor's routing table (between the `AUTO-MAPPING` markers).

After any edit: `./setup/3_apply/apply.sh`.

## 4. Run

```sh
gambit run
```

First it runs a **pre-flight health check** (`gambit doctor`) — verifies the
toolchain, worker binaries, logins, and that the bulk endpoint answers, so a
worker can't fail silently mid-task. A missing binary aborts the launch;
warnings (e.g. an unconfigured endpoint) don't. Run it any time with
`gambit doctor`, or skip the gate with `gambit run --skip-check`.

Then it launches the daemon if needed and attaches you to the supervisor (tmux
session `cao-supervisor`). Delegate by talking to it. You can detach (`Ctrl-b
d`) and the workers keep running — the `cao-server` daemon owns them, not your
terminal. Reattach with `tmux attach -t cao-supervisor`.

> **Run it in a real terminal, not an IDE-embedded one.** Some IDE integrations
> (e.g. Zed) strip the supervisor's file-edit tools; it then can't delegate and
> falls back to hand-holding you through manual edits. A plain terminal keeps
> full tools. (Workers run in the daemon and are unaffected either way.)

### Supervisor fallback (when Claude's quota runs out)

The supervisor defaults to `claude_code`. If your Claude quota is exhausted or
your login expires, `gambit run` no longer dead-ends — it picks the supervisor
engine in this priority:

1. **`CAO_SUPERVISOR_PROVIDER`** env var — explicit override, always wins:
   ```sh
   CAO_SUPERVISOR_PROVIDER=antigravity_cli gambit run
   ```
2. **Fallback hint** — `gambit doctor` writes `~/.cao/supervisor_provider` when it
   sees Claude logged out, and clears it when Claude works again.
3. **`claude_code`** default.

On top of that, when the primary is `claude_code`, `gambit run` **auto-retries once
on a fallback engine if the launch itself fails** — this catches a burned quota,
which isn't visible any earlier (`claude auth status` reports login, not quota).
Fallback order: `CAO_FALLBACK_PROVIDER` env > `antigravity_cli` (if `agy`
present) > `codex`. Any registered worker engine works as the value.

**Stop when done.** Nothing auto-stops — workers survive detach by design, so
you shut down explicitly:

```sh
gambit stop              # kill all cao- tmux sessions + the daemon (end of day)
gambit stop --workers    # kill workers only, keep the supervisor + daemon up
gambit stop --keep-server / -k   # kill the sessions, leave the daemon running
```

**Check usage.** `gambit tokens` scrapes each CLI's local store (`~/.claude` jsonl,
`~/.codex` + opencode sqlite) — no billing API. By **default it shows a claude
heatmap plus a per-day table across all engines, last 7 days, cao-only** — one
column per engine, each cell `input/output` (compact: `2.2k/670.5k`):

```
date          claude(in/out)   ~codex  ~opencode(in/out)      $
2026-09-17       2.2k/670.5k     2.1M         2.8M/26.6k   0.00
```

- **cao-only is the default.** For claude it counts only sessions that loaded
  cao's MCP server (a reliable marker). codex and opencode keep no such marker
  locally, so their columns are marked `~` and show *all* of that engine's use —
  in practice you rarely run them outside cao. A precise per-engine split would
  need request tracing (e.g. langfuse). `--all-sessions` drops the claude filter.
- `output` is real generation — the number that matters. `codex` reports one
  combined total (no in/out split). `$` shows only for opencode (metered); claude
  and codex are flat-rate. `agy`/gemini keeps no local log (Google server-side).

```sh
gambit tokens                # DEFAULT: heatmap + per-day, all engines, 7 days, cao-only
gambit tokens --since 2w     # widen the window (24h / 7d / 2w / 3d ...)
gambit tokens --lifetime     # lifetime per-engine table (all history)
gambit tokens --day 2026-09-17   # one specific date (YYYY-MM-DD)
gambit tokens --claude       # per-day CLAUDE only (input/output/cache detail)
gambit tokens --heatmap      # claude output heatmap only
gambit tokens -x             # extended: heatmap + claude daily + lifetime table
gambit tokens --all-sessions # include non-cao claude sessions too
gambit tokens --json         # machine-readable form of the selected view
```

**Design first for big work.** For a new project or a large feature the
supervisor acts as architect: it discusses the system with you, writes a Mermaid
sequence/flow diagram to `wgambit/design/`, and gets your approval before
any code is delegated — the diagram is the contract the workers build against.
Small changes skip this and go straight to delegation. The diagram is a living
document: it's referenced and edited across sessions, not redrawn each time.

**Single Source of Truth (`wgambit/`).** All project-level plans, contracts, and knowledge live in `wcao/`:
- `wgambit/plans/now.md` — Active plan, North Star objective, and latest checkpoint.
- `wgambit/tasks.json` — Directed Acyclic Graph (DAG) of tasks with dependencies and file locks.
- `wgambit/design/*.mmd` — Architecture and sequence diagrams.
- `wgambit/skills/*.md` — Procedural memory (rules, workflows, tool gotchas).
- `wgambit/audit/` — Postflight audit reports (`aggressive-audit.md`), threat analysis (`weaknesses.md`), and executable load/stress harness (`stress-test.sh`).
- `wgambit/memory.sqlite` — Local episodic memory database with BM25 FTS5 full-text search (gitignored).

## Autonomous Execution & Self-Healing (`gambit auto`)

`cao_auto` provides fully headless, autonomous execution of task graphs:

```sh
gambit auto --tasks wgambit/tasks.json --max-workers 4
```

1. **Autonomous Planning (`gambit plan`)**: Decomposes a high-level goal into an acyclic DAG (`wgambit/tasks.json`) with TokenMaster model routing and contract specification.
2. **DAG Scheduling & File Locks**: Evaluates `depends_on` relationships and prevents concurrent workers from touching overlapping `files`, ensuring zero merge conflicts or race conditions.
3. **Proactive TokenMaster Quota Control**: Reads live quota utilization via `cao_limits`. If quota exceeds the 80% watermark or is blocked, it proactively reassigns tasks to `hermes_worker` or `coder_worker` before hitting rate limits.
4. **Anti-Test-Tampering Gate (`cao_tamper.py`)**: During postflight audit, inspects git diffs to ensure workers have not weakened assertions, inserted bypasses (`assert True`), or deleted test functions. Automatically reverts tampered tests and forces fixes in production code.
5. **Architect Escalation Protocol**: If a bulk implementation worker fails to fix an audit blocker on attempt 1, self-healing automatically escalates attempt 2+ to an Architect/Reasoning engine (`hermes_worker` or `claude_worker`) for root-cause diagnosis.
6. **5-Vector Audit & Auto-Generated Stress Testing (`cao-aggressive`)**: Runs AST compilation across all files, high-entropy secrets scanning, and test suites. Automatically generates an executable load/stress test harness (`wgambit/audit/stress-test.sh`) to stress concurrency bursts, CLI arguments, and process stability (see [Audit & Stress-Testing Docs](wgambit/docs/AUDIT_AND_STRESS_TESTING.md)).

## Hermes Learning & Memory System

CAO incorporates the **Hermes Continuous Learning** architecture across all engines:

1. **Episodic Memory (`gambit memory`)**:
   Powered by SQLite with FTS5 and BM25 ranking. Stores context, past solutions, and debugging outcomes.
   - `gambit memory store <category> <summary> [details]`
   - `gambit memory recall <query> [-n 5]`
   - `gambit memory list [--category <cat>]`
   Before any task is dispatched, `cao_auto` automatically searches episodic memory and injects relevant historical lessons directly into the worker's prompt.
2. **Procedural Memory (`wgambit/skills/`)**:
   Reusable behavioral and debugging recipes saved as Markdown files in `wgambit/skills/`, shared across all worker engines.
3. **Hermes 50% Compaction Rule**:
   To prevent context saturation, the `ContextCompactor` automatically triggers every 5 turns or when context fills. It condenses verbose conversation histories into structured summaries, extracts new lessons, and writes progress checkpoints directly to `wgambit/plans/now.md`.
4. **Retrospective Storage**:
   Whenever a self-healing loop resolves a failure, the root cause and fix are automatically indexed into `memory.sqlite` and `wgambit/skills/` so future workers never repeat the mistake.

## Share your MCP servers with every engine

MCP is a cross-engine protocol — codex, opencode, antigravity (agy), and copilot
each have their own `mcp add`, so an MCP tool you use in Claude (lean-ctx,
symdex, …) can reach all of them. Two scripts, two levels:

```sh
# 1. Into cao WORKER PROFILES (cao writes them into each engine's config at install):
python3 setup/3_apply/inherit_mcp.py --list      # what you have
python3 setup/3_apply/inherit_mcp.py             # add to all worker profiles
./setup/3_apply/apply.sh                         # push live

# 2. Directly into every ENGINE's own CLI config (works outside cao too):
python3 setup/3_apply/inherit_all.py --list      # per-engine plan
python3 setup/3_apply/inherit_all.py --dry-run   # print the mcp-add commands
python3 setup/3_apply/inherit_all.py             # register with codex/opencode/agy/copilot
```

Both read `~/.claude.json` global `mcpServers` (skipping cao's own server). A
server carrying a token in its `env` is copied verbatim — the scripts warn so you
can review. `bootstrap.sh --inherit-mcp` runs both automatically.

### Cross-Engine Skills, MCP & "Everything Claude Code" (ECC) Integration (`gambit plugins`)

`gambit plugins` allows you to take any plugin, skill pack, or MCP server installed in Claude Code—including the industry-standard **[Everything Claude Code (ECC)](https://github.com/affaan-m/ECC)** toolkit—and broadcast it across your entire multi-agent workforce:

```sh
gambit plugins list                     # Inspect what each engine currently has
gambit plugins broadcast --dry-run      # Preview broadcast plan without making changes
gambit plugins broadcast                # Push all Claude MCP + plugins + ECC skills everywhere
gambit plugins broadcast --mcp          # Synchronize MCP servers only
gambit plugins broadcast --plugins      # Synchronize plugins/skills only
gambit plugins broadcast --only=caveman # Synchronize a specific plugin
gambit plugins broadcast --to=codex,agy # Target specific worker engines
```

#### Why broadcasting "Everything Claude Code" (ECC) makes strategic sense:
* **The Synergy:** ECC provides state-of-the-art prompts, subagents, and test-driven design workflows (TDD, security reviews, architecture spikes). GAMBIT provides the **orchestration, economic asymmetry, kernel Landlock sandboxing, and multi-process tmux coordination**.
* **Zero Token Waste:** Running ECC on vanilla Claude Code burns expensive flat-rate/API tokens for every small edit. When broadcast through GAMBIT, Claude acts as **The Rook / Tech Lead** using ECC's architecture skills, while high-throughput Pawns (`opencode`, `hermes`) implement the boilerplate inside Landlock-secured git worktrees.
* **How each engine receives broadcasted skills & ECC:**

| Engine | Role in Fleet | Plugin / Skill Reception Mechanism |
|--------|---------------|-----------------------------------|
| **Claude** | ♜ The Rook / ♝ Bishop Architect | Native installation (`claude plugin add ecc@ecc` or `npx ecc-universal`). Full access to subagents and prompts. |
| **Codex** | ♝ Bishop Frontend & UI | `plugin marketplace add owner/repo` + `plugin add p@mp` (git-based plugin registry). |
| **AGY / Gemini** | ♝ Bishop Massive Context & QA | `plugin install <plugin-dir>` (native directory extension). |
| **Copilot** | ♙ Pawn PR & CI/CD | `skill add <plugin-dir>`; natively parses `.claude/skills` manifests. |
| **OpenCode** | ♙ Pawn Bulk Implementation | Receives a **compact Markdown skill index** appended to `~/.config/opencode/AGENTS.md`. Gives the cheap model high-level guidelines without bloating context tokens. |

So MCP and real plugins reach claude/codex/agy/copilot; opencode gets the skills
as a lightweight text index (one line per skill, not full bodies — to avoid
bloating every opencode run). Nothing is ever uninstalled.

### Don't have any yet? Context MCP servers worth adding

`inherit_mcp.py` only copies servers you **already** have. If your `--list` is
empty, these two give the workers a big context/token win before you inherit —
they let a worker read, search, and map the repo compactly instead of pulling
whole files into its context:

- **lean-ctx** — cached, compressed file reads + git/grep output. Cuts the tokens
  a worker spends just to look at code.
- **symdex** — symbol index: "who calls X", file/repo outlines, dependency maps.
  This is exactly what `analyst_worker` leans on.

Add them to your **own** Claude first (they live in `~/.claude.json` global
`mcpServers`), confirm with `python3 setup/3_apply/inherit_mcp.py --list`, then run the
inherit + apply steps above to push them to every worker. They're independent,
optional tools — CAO works without them; they only make each worker cheaper.

Skills like **superpowers** (brainstorming, systematic-debugging) are Claude
Code-only and can't reach codex/opencode/antigravity workers. Install them in
your own Claude if you want them on the **supervisor** (which runs on Claude);
the non-Claude workers won't see them either way.

## Secrets

`LOCAL_API_KEY` is the only secret — in `.env` (gitignored), copied to
`~/.config/cao/cao.env` (chmod 600), never in a tracked file (configs reference
it as `{env:LOCAL_API_KEY}`). Endpoint URL and model ids are not secret.

## After `cao update`

Re-run `gambit doctor --update` (or `./update.sh`, or `./setup/1_install/bootstrap.sh`) — it
re-applies the pyte patch (which lives in the CAO venv and is lost on
reinstall). Idempotent.

## dev-kodeks (optional development standard)

`--with-kodeks` installs [dev-kodeks](https://github.com/povchingiz/dev-kodeks):
global Claude Code rules + skills for repo/code/change discipline. A **quality
layer**, not part of CAO — it runs fine without it.

⚠️ **It's global**: it symlinks into `~/.claude/`, so it affects *every* Claude
session on the machine, including the CAO workers that run through `claude`, and
changes Claude's default behavior (planning discipline, when it pauses). Enable
deliberately. `--with-guard-hook` also activates its `guard-env` hook, which
blocks `git push/pull/reset`, `systemctl`, `shutdown` … — for the workers too.
Both are off unless you pass the flag.

---

### For Claude: "set it all up for me"

If a user hands you this repo and says *connect everything*, do this in order —
stop at each 🔸 (needs a human):

1. Confirm OS is macOS/Linux (Windows → tell them WSL2 per `wgambit/docs/WINDOWS.md`, stop).
2. 🔸 Ask for `LOCAL_API_KEY`; `cp .env.example .env` and write it. Never print
   or commit it.
3. Check `[endpoint]` in `setup/2_configure/cao.config.toml` matches their endpoint.
4. Run `./setup/1_install/bootstrap.sh` (add `--inherit-mcp` / `--with-kodeks` only if
   they ask).
5. 🔸 Tell them to run the logins themselves: `claude` → `/login`, `codex
   login`, `agy`. You cannot.
6. Verify: `gambit run`, delegate a trivial task to each worker, confirm replies.
7. Point them at `gambit run` from any project. Edits go through `setup/2_configure/` +
   `./setup/3_apply/apply.sh`, never the live files.
