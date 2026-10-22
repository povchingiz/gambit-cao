# Playwright Autonomous QA & UI/UX Ergonomics Report

- **Target:** `/home/user/Desktop/Chingiz/dycom-demo/web/index.html` (`file:///home/user/Desktop/Chingiz/dycom-demo/web/index.html`)
- **Page Title:** CBCT segmentation — automatic mapping of jaws, teeth and nerve canals — 2 scans, agreement with totalsegmentator · 0.8056
- **Status:** **WARN** (Health Score: **90/100**)
- **Browser Engine:** `/usr/bin/google-chrome`
- **Audit Duration:** `20.89s`
- **Timestamp:** `2026-10-22T13:04:21.960965+00:00`

## 1. Executive Summary

| Metric | Count / Status |
|---|---|
| Interactive Controls Discovered | `8` (Clicked: `7`) |
| Broken Interactions (JS / HTTP 4xx-5xx / Backend Errors) | `0` |
| Silent Dead Clicks (Zero Effect) | `1` |
| Redundant / Duplicate Control Groups | `0` |
| Small Hit Targets (`< 24x24 px`) | `0` |
| Unlabeled Controls (Missing A11y Name) | `0` |
| Desktop Horizontal Overflow (`1440x900`) | `NO` |
| Mobile Horizontal Overflow (`390x844`) | `NO` |

## 2. Full-Stack Telemetry & Broken Interactions

No console errors, uncaught JS exceptions, HTTP 4xx/5xx responses, or backend log errors triggered by UI clicks.
## 3. Redundant Controls (Duplicate Functionality)

No redundant buttons or duplicate action controls detected.

## 4. Silent Dead Clicks

- **`label` (Summary):** Zero DOM delta, zero network calls, zero URL/console effect.

## 5. Ergonomics, Hit Targets & Viewport Overflow

All controls meet minimum 24x24px target sizing, have accessible labels, and fit both desktop and mobile viewports.

## 6. Actionable UX Simplification & Remediation Plan

1. Control 'Summary' (label) produced zero DOM, network, URL, or state change when clicked. Wire up its handler or remove it.
