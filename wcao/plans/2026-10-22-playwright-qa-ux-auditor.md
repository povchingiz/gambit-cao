# Plan: Playwright Autonomous QA, Full-Stack Telemetry & UI/UX Ergonomics Auditor (`cao-qa`)

> **Date:** 2026-10-22  
> **Branch:** `1000x`  
> **Routed Worker:** `codex_worker` / `antigravity_worker`  
> **Deliverables:** `run/cao_qa.py`, `run/cao-qa`, `wcao/skills/playwright-qa-ux-auditor.md`, `tests/test_cao_qa.py`

---

## 1. Problem Statement

Unit tests verify isolated functions, but real-world regressions hide in the **seam between UI interactions, frontend state, and backend APIs**, as well as in **UI/UX friction**:
- Buttons that silently do nothing (`dead clicks`) or throw uncaught JS/console errors.
- Clicks that trigger backend `4xx/5xx` responses, CORS errors, or backend log exceptions.
- **Redundant Controls:** Multiple buttons/links on the same view performing identical actions (same event target, same API call, or identical DOM delta).
- **UX Friction & Ergonomics:** Tiny hit targets (`< 24x24 px`), overlapping/occluded controls, missing accessible labels, horizontal layout overflow on mobile/desktop viewports, and multi-step flows that could be 1-click actions.

---

## 2. Architecture & Capabilities of `cao-qa`

### A. Interactive Explorer & Click Harness (`run/cao_qa.py`)
- Uses Playwright (`sync_playwright`) backed by `/usr/bin/google-chrome` (zero extra browser binary download required).
- Accepts any target URL (`http://127.0.0.1:9877`, `http://localhost:3000`) or local HTML file (`file:///.../dycom-demo/web/index.html`).
- Discovers all visible interactive elements: `button`, `a[href]`, `[role="button"]`, `input[type="submit"]`, `select`, tabs, and toggles.
- For each interactive element:
  1. Records bounding box (`x, y, width, height`), label/text, ARIA attributes, and DOM fingerprint before interaction.
  2. Clicks/triggers the element safely.
  3. Captures:
     - **DOM Delta:** What changed in the DOM (`innerHTML` hash delta, modal opened, tab switched, attribute toggled).
     - **Network Telemetry:** All `fetch`/`XHR`/document requests fired during the interaction, status codes (`200`, `4xx`, `5xx`), and latency (ms).
     - **Console & Page Errors:** `console.error`, `console.warn`, and uncaught `pageerror` exceptions.
     - **Backend Log Correlation (`--backend-log <path>`):** Tails the backend server log file during the click window to link a specific UI button click directly to a backend stack trace or warning.

### B. UI/UX & Redundancy Heuristics Engine
1. **Redundant Button / Duplicate Action Detector:**
   - Groups interactive elements by their **effect signature**: `(target_url_or_api, dom_delta_signature, onclick_handler)`.
   - Flags controls that produce identical effects on the same screen (*"Buttons 'Apply' and 'Save Config' trigger the exact same POST /api/save and DOM mutation — consider consolidating"*).
2. **Silent Dead-Click Detector:**
   - Flags enabled buttons that, when clicked, produce zero DOM mutation, zero URL navigation, zero network requests, and zero console/state feedback.
3. **Ergonomics & Simplification Analyzer:**
   - **Hit-Target Sizing:** Flags interactive elements smaller than `24x24 px` (WCAG 2.2 AA target size).
   - **Unlabeled Controls:** Flags icon-only buttons lacking `aria-label`, `title`, or visible text.
   - **Viewport Overflow Check:** Tests both Desktop (`1440x900`) and Mobile (`390x844`) viewports for unintended horizontal scroll (`document.documentElement.scrollWidth > window.innerWidth`).
   - **Flow Simplification Hints:** Flags deeply nested interactions or forms without default values / keyboard Enter submission.

### C. Output & Fleet Integration
- Generates `wcao/audit/qa_ux_report.md` and `wcao/audit/qa_ux_report.json`.
- Can auto-dispatch discovered bugs directly into a project's task queue via `cao-fleet dispatch --project <name>`.
- Bundled as a reusable procedural skill in `wcao/skills/playwright-qa-ux-auditor.md`.
