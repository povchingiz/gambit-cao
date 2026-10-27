# Playwright Autonomous QA & UI/UX Ergonomics Report

- **Target:** `/home/user/Desktop/Maksat/3DAang/web_viewer/index.html` (`file:///home/user/Desktop/Maksat/3DAang/web_viewer/index.html`)
- **Page Title:** 3DAang - GAMBIT Universal 52 ARKit Avatar & Voice Cloner
- **Status:** **FAIL** (Health Score: **54/100**)
- **Browser Engine:** `/usr/bin/google-chrome`
- **Audit Duration:** `10.49s`
- **Timestamp:** `2026-10-23T07:19:52.182842+00:00`

## 1. Executive Summary

| Metric | Count / Status |
|---|---|
| Interactive Controls Discovered | `22` (Clicked: `22`) |
| Broken Interactions (JS / HTTP 4xx-5xx / Backend Errors) | `1` |
| Silent Dead Clicks (Zero Effect) | `1` |
| Redundant / Duplicate Control Groups | `1` |
| Small Hit Targets (`< 24x24 px`) | `0` |
| Unlabeled Controls (Missing A11y Name) | `0` |
| Desktop Horizontal Overflow (`1440x900`) | `NO` |
| Mobile Horizontal Overflow (`390x844`) | `YES` |
| Destructive Actions Safely Skipped | `0` |
| Forms Smartly Auto-filled | `0` |
| Dialog / Modal Exploration Cycles | `0` |
| Visual Issue Screenshots Saved | `0` |
| Secret & Token Leaks Detected | `0` |
| Insecure CORS Configurations | `0` |

## 2. Full-Stack Telemetry & Broken Interactions

### `button#btn-ws-connect` — **Connect WS** (Index #6)
- **Console Error:** `WebSocket connection to 'ws://127.0.0.1:8000/ws/speech' failed: Error in connection establishment: net::ERR_CONNECTION_REFUSED`

## 3. Redundant Controls (Duplicate Functionality)

- **2 Duplicate Controls (`► Stream Visemes & Audio`, `EE`):** Selectors `button#btn-stream-speak`, `button.vowel-btn` share identical effect signature `dom=b49178fd2ae1d1d0`.

## 4. Silent Dead Clicks

- **`button#btn-ws-disconnect` (Disconnect):** Zero DOM delta, zero network calls, zero URL/console effect.

## 5. Ergonomics, Hit Targets & Viewport Overflow

- **Viewport Overflow (mobile `390px`):** Scroll width is `709px` (+`319px` overflow). Offenders: div.metrics-bar (right=709px), div.metric-pill (right=458px), span#ws-status-text (right=445px), div.metric-pill (right=551px), span (right=515px)

## 6. Security, Secrets & CORS Audit

No sensitive credentials, API keys, or insecure wildcard CORS configurations detected in DOM, console, or network traces.

## 7. Actionable UX Simplification & Remediation Plan

1. Consolidate 2 duplicate controls ('► Stream Visemes & Audio', 'EE') that trigger the exact same action signature `dom=b49178fd2ae1d1d0`.
2. Control 'Disconnect' (button#btn-ws-disconnect) produced zero DOM, network, URL, or state change when clicked. Wire up its handler or remove it.
3. Fix broken interaction on 'Connect WS' (button#btn-ws-connect): JS error (WebSocket connection to 'ws://127.0.0.1:8000/ws/speech' failed: Error in connect).
4. Fix mobile horizontal overflow (+319px beyond 390px viewport; offenders: div.metrics-bar (right=709px), div.metric-pill (right=458px), span#ws-status-text (right=445px)).
