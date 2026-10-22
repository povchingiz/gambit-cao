# Playwright Autonomous QA & UI/UX Ergonomics Report

- **Target:** `/home/user/Desktop/Chingiz/dycom-demo/web/ru.html` (`file:///home/user/Desktop/Chingiz/dycom-demo/web/ru.html`)
- **Page Title:** Сегментация КЛКТ — автоматическая разметка челюстей, зубов и каналов — 2 снимка, совпадение с totalsegmentator · 0.8056
- **Status:** **WARN** (Health Score: **80/100**)
- **Browser Engine:** `/usr/bin/google-chrome`
- **Audit Duration:** `25.71s`
- **Timestamp:** `2026-10-22T19:21:16.024021+00:00`

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
| Mobile Horizontal Overflow (`390x844`) | `YES` |
| Destructive Actions Safely Skipped | `0` |
| Forms Smartly Auto-filled | `0` |
| Dialog / Modal Exploration Cycles | `0` |
| Visual Issue Screenshots Saved | `0` |
| Secret & Token Leaks Detected | `0` |
| Insecure CORS Configurations | `0` |

## 2. Full-Stack Telemetry & Broken Interactions

No console errors, uncaught JS exceptions, HTTP 4xx/5xx responses, or backend log errors triggered by UI clicks.
## 3. Redundant Controls (Duplicate Functionality)

No redundant buttons or duplicate action controls detected.

## 4. Silent Dead Clicks

- **`label` (Итог):** Zero DOM delta, zero network calls, zero URL/console effect.

## 5. Ergonomics, Hit Targets & Viewport Overflow

- **Viewport Overflow (mobile `390px`):** Scroll width is `418px` (+`28px` overflow). Offenders: div.tools (right=418px), button#theme-toggle (right=418px)

## 6. Security, Secrets & CORS Audit

No sensitive credentials, API keys, or insecure wildcard CORS configurations detected in DOM, console, or network traces.

## 7. Actionable UX Simplification & Remediation Plan

1. Control 'Итог' (label) produced zero DOM, network, URL, or state change when clicked. Wire up its handler or remove it.
2. Fix mobile horizontal overflow (+28px beyond 390px viewport; offenders: div.tools (right=418px), button#theme-toggle (right=418px)).
