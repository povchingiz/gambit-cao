# now.md — GAMBIT · Active Operations

> **Fleet Status:** ♜ The Rook Orchestrator active | 3 Knights deployed in parallel
> **Branch:** `1000x` (Synchronized with `origin`: `https://github.com/povchingiz/gambit-cao.git`)
> **Rule:** NEVER run `git push` without explicit user confirmation.

---

## ♜ GAMBIT Architecture & Chess Taxonomy

- **The Grandmaster (User):** Defines strategic objectives, holds final safety confirmation gate.
- **The Rook (`gambit` / `cao-crew`):** Master fleet orchestrator, autonomous DAG pipeline, sandbox isolation, self-repair.
- **The Knights (Specialized Projects):**
  - ♘ **Knight 1 (`dycom-demo`):** Dental AI & 3D CBCT Segmentation (ToothFairy2, E2E Clinical Calculations).
  - ♘ **Knight 2 (`llmaas`):** SOTA LLM/GPU Inference & Real-Time Low-Latency Streaming Speech Lab.
  - ♘ **Knight 3 (`3DAang`):** 3D Avatar Generation (Photo-to-ARKit 52 Blendshapes) & Real-Time Three.js WebGL.
- **The Bishops (Specialized Engines):** Claude (Architecture), Codex/OpenCode (Implementation), Antigravity/Gemini (Codebase & Multimodal Analysis), Hermes (Local Reasoning).
- **The Pawns:** Atomic execution steps, AST anti-tampering guards, telemetry probes.

---

## ⚡ Active Parallel Missions (Launched via Subagents)

### 1. ♘ Knight 1: `dycom-demo` — E2E Clinical Pipeline & Safety Buffer
- **Directory:** `/home/user/Desktop/Chingiz/dycom-demo` (`feat/e2e-clinical-pipeline`)
- **Objectives:**
  - 2mm Mandibular Alveolar Canal safety buffer tube and 3D collision detection (`nerve_buffer.py`).
  - Misch Bone Density HU Profiler (D1–D5) for implant bed site analysis (`bone_density.py`).
  - Metal Artifact Reduction (MAR) streak filter (`mar_filter.py`).
  - Full E2E pipeline integration (`pipeline.py`) exporting clinical JSON reports + STL geometries.
  - Competitor benchmark & killer features document (`docs/COMPETITORS_AND_KILLER_FEATURES.md`).
  - 100% test pass rate in `tests/`.

### 2. ♘ Knight 2: `llmaas` — Speech Streaming Lab & Frontier Research
- **Directory:** `/home/user/Desktop/Chingiz/llmaas` (`feat/speech-frontier-lab`)
- **Objectives:**
  - Ultra-low latency streaming STT engine (`src/speech/stt_streamer.py`).
  - Ultra-fast streaming TTS engine with Kokoro-82M / Piper architecture (`src/speech/tts_kokoro.py`).
  - 52 ARKit blendshape viseme mapper & 60 FPS timestamped stream (`src/speech/viseme_streamer.py`).
  - Full-duplex WebSocket speech server (`src/speech/ws_server.py`).
  - Frontier optimization benchmarks & deep dive (`experiments/frontier/`, `docs/FRONTIER_OPTIMIZATION.md`).
  - Unit test suite in `tests/speech/`.

### 3. ♘ Knight 3: `3DAang` — Modernized Photo-to-3D Avatar & WebGL Engine
- **Directory:** `/home/user/Desktop/Maksat/3DAang` (`feat/arkit-avatar-webgl`)
- **Objectives:**
  - Git repository initialization and clean hygiene (`.gitignore`, legacy isolation).
  - Photo-to-3D-head builder with 52 ARKit blendshapes (`avatar_engine/avatar_builder.py`, `blendshape_rig.py`).
  - Real-time Three.js WebGL canvas client (`web_viewer/`) with lifelike blinking, breathing, and zero-lag (< 100ms) viseme-to-mouth synchronization.
  - Eliminating the slow legacy 10-15s Wav2Lip video generation bottleneck (`docs/AVATAR_ARCHITECTURE.md`).
  - Unit tests in `tests/`.

---

## ✅ Completed Milestones

- **92/92 Unit & Integration Tests Passing** in `tests/`.
- **Unified `gambit` CLI**: Space syntax (`gambit status`, `gambit fleet`, `gambit test`) and dash syntax (`gambit-status`, etc.).
- **Natural Language Mission Dispatch**: `gambit "diagnose and fix"` automatically executes via Laya routing.
- **Grandmaster Confirmation Gate**: Playwright QA-UIX auditor verifies with the user `[y/N]` before launching heavy browser runs.
- **GitHub Remote Synchronized**: `main` and `1000x` cleanly pushed to `https://github.com/povchingiz/gambit-cao.git`.
- **Consolidation of `llmaas`**: Absorbed `nowait-study` and `token-audit` with 382 passing tests.
- **Client-Side WebWorker DICOM Loader**: Built in `dycom-demo` with progressive 96³ LOD and binary STL exporter.


