# Master Plan: Frontier Expansion Across GAMBIT Knights

> **Date:** 2026-10-23  
> **Status:** Active Execution (Autonomous Multi-Track)  
> **Rule:** STRICT GIT PUSH POLICY — Never push without explicit Grandmaster confirmation. All feature branches committed locally.

---

## 1. Executive Vision & Strategic Reorientation

Based on Grandmaster feedback, we have refined the trajectory across the 4 stationed Knights:

1. **♘ Knight 1 (`dycom-demo`) $\rightarrow$ Smart Diagnostic Annotator & Hazard Radar:**
   - Shift focus from automated surgery to **super-assistant and diagnostic annotator**.
   - Zero-install 100% in-browser WebGL visualization.
   - Interactive 3D progressive loading: futuristic laser-scan wireframe hologram + progressive 96³ voxel LOD.
   - Hazard Radar: neon red 2.0 mm nerve safety tube, yellow thin bone (<1.2 mm), orange soft bone (D4/D5), purple periapical radiolucencies.
   - Interactive 3D point-to-point laser ruler tool & X-Ray opacity slider.
   - Universal format cleaner (DICOM, NIfTI, MHA, NRRD, STL).

2. **♘ Knight 2 (`3DAang`) $\rightarrow$ Universal Photo/Video-to-Avatar & 3s Voice Cloning:**
   - Any single photo or video clip converts into an optimized 52 ARKit blendshapes avatar (.glb < 1.5 MB).
   - 3-second zero-shot voice cloning extracting speaker acoustic embeddings.
   - Lightweight, real-time 60 FPS WebGL client viewer with < 100 ms voice-to-lip latency.

3. **♘ Knight 3 (`llmaas`) $\rightarrow$ Real-Time Call Assistant & LLM-CLI Video Editor:**
   - **Real-Time Call Co-pilot (`src/copilot/`):** LiveKit/WebRTC streaming audio, sub-150 ms STT, turn-taking/backchanneling filter, sub-200 ms objection detection & battlecard RAG.
   - **LLM-CLI Video Editor (`src/video_editor/`):** Whisper word-level timestamps, silence/filler word remover (jump-cuts via FFmpeg), auto-reframe 16:9 $\rightarrow$ 9:16 Shorts, natural language director CLI.

4. **♜ The Rook (`gambit`) $\rightarrow$ Meta-Orchestrator:**
   - Coordinates separate git feature branches.
   - Maintains `wgambit/` workspace standard with backwards-compatible `wcao/` symlinks.
   - Prepares groundwork for future Grand Synergy.

---

## 2. Independent Feature Branches Roster

| Project | Base Branch | New Feature Branch | Mission |
|---|---|---|---|
| `dycom-demo` | `feat/e2e-clinical-pipeline` | `feat/3d-progressive-hazard-radar` | 3D progressive laser loading, hazard radar, 3D ruler, X-Ray mode |
| `3DAang` | `feat/arkit-avatar-webgl` | `feat/universal-avatar-voice-clone` | Universal photo/video-to-avatar, 3s voice cloner, WebGL controls |
| `llmaas` | `feat/speech-frontier-lab` | `feat/call-copilot-and-video-cli` | Real-time call co-pilot engine & LLM-CLI video editing pipeline |
| `gambit` | `1000x` | `1000x` (Master) | Fleet conductor tracking, test verification, frontier documentation |
