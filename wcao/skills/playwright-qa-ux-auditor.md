---
name: playwright-qa-ux-auditor
description: Autonomous Playwright QA, Full-Stack Telemetry & UI/UX Ergonomics Auditor (cao-qa). Clicks every interactive control on a web app or HTML page, correlates UI actions with DOM deltas, HTTP 4xx/5xx responses, console/JS exceptions, and backend log stack traces, and flags redundant duplicate buttons, silent dead clicks, small targets (<24x24px), unlabeled controls, and viewport overflow.
---

# Skill: Playwright Autonomous QA & UI/UX Ergonomics Auditor (`cao-qa`)

## When to Activate
Use this skill whenever:
1. A frontend UI, dashboard, landing page, or full-stack web feature has been created or modified.
2. You want to verify that every button, link, tab, and form control actually works and produces a meaningful state change.
3. You need to correlate a frontend button click with backend server logs (`--backend-log`) or API 4xx/5xx responses.
4. You want to audit UI/UX ergonomics: redundant buttons sharing the same action, silent dead clicks, tiny hit targets (`< 24x24px`), missing `aria-label` accessibility names, or horizontal scroll overflow on Desktop (`1440x900`) and Mobile (`390x844`).

---

## Quick Usage

### 1. Audit a Live Web App or Local HTML File
```bash
# Audit a running local server
cao-qa http://127.0.0.1:3000

# Audit a static/local HTML file directly
cao-qa /home/user/Desktop/Chingiz/dycom-demo/web/index.html
```

### 2. Full-Stack Click-to-Backend-Log Correlation
Pass `--backend-log <path>` to tail the backend log file before and after each UI click. Any `ERROR`, `Exception`, `Traceback`, or `500` emitted during the click window is automatically attributed to the exact button selector that triggered it:
```bash
cao-qa http://127.0.0.1:8000 --backend-log /tmp/backend.log
```

### 3. Auto-Dispatch Discovered Bugs to `cao-fleet`
Automatically enqueue remediation tasks into any registered fleet project (`llmaas`, `3DAang`, `nowait-study`, `dycom-demo`, `cao-crew`):
```bash
cao-qa http://127.0.0.1:8080 --dispatch-project dycom-demo
```

---

## What `cao-qa` Inspects & Reports

| Dimension | Heuristic / Check |
|---|---|
| **Broken Interactions** | Captures `console.error`, uncaught `pageerror`, failed `fetch`/`XHR` requests, HTTP `4xx`/`5xx` status codes with latency (ms), and correlated `--backend-log` errors per click. |
| **Redundant Controls** | Computes an effect signature `(api_endpoints, dom_delta_hash, nav_or_handler)` per control and flags multiple buttons/links on the same screen that perform the exact same action. |
| **Silent Dead Clicks** | Flags enabled buttons/controls that produce zero DOM mutation, zero network call, zero URL change, and zero console/log activity when clicked. |
| **Hit Target Ergonomics** | Flags interactive elements smaller than `24x24 px` (WCAG 2.2 AA target size minimum). |
| **Accessibility Labels** | Flags icon-only or empty buttons/links missing visible text, `aria-label`, and `title`. |
| **Responsive Overflow** | Tests both Desktop (`1440x900`) and Mobile (`390x844`) viewports for unintended horizontal scroll (`scrollWidth > innerWidth`) and lists offending selectors. |

---

## Artifacts Produced
- `wcao/audit/qa_ux_report.md` — Human-readable executive summary, per-button error attribution, redundancy table, and prioritized UX simplification plan.
- `wcao/audit/qa_ux_report.json` — Machine-readable telemetry report with bounding boxes, DOM hashes, and network traces for every interactive element.
