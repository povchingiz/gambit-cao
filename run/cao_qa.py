"""cao_qa.py — Playwright Autonomous QA, Full-Stack Telemetry & UI/UX Ergonomics Auditor.

Explores a live URL or local HTML file using headless Chrome/Playwright:
1. Discovers and clicks interactive elements (buttons, links, role=button, submits, tabs).
2. Correlates every UI click with:
   - DOM state delta (before/after structural & text fingerprint)
   - Network telemetry (XHR/fetch URLs, HTTP 4xx/5xx status codes, latency in ms)
   - Browser console errors/warnings & uncaught JS pageerror exceptions
   - Backend server log lines (--backend-log) emitted during that exact click window
3. Evaluates UI/UX & Ergonomics heuristics:
   - Redundant controls (duplicate buttons/links with identical action/API/DOM effect signature)
   - Silent dead clicks (enabled buttons producing zero DOM, network, URL, or console effect)
   - Small hit targets (< 24x24px WCAG 2.2 AA minimum)
   - Unlabeled controls (missing visible text, aria-label, and title)
   - Viewport horizontal overflow across Desktop (1440x900) and Mobile (390x844)
   - Actionable UX simplification & flow consolidation recommendations
"""
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


CHROME_CANDIDATES = [
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium-browser",
    "/usr/bin/chromium",
    "/snap/bin/chromium",
]

DESTRUCTIVE_PATTERN = re.compile(
    r"\b(delete|drop|wipe|purge|destroy|truncate|reset\s*all|remove\s*account|clear\s*all|format|terminate|kill)\b",
    re.IGNORECASE,
)

SECRET_LEAK_PATTERNS = [
    ("OpenAI API Key", re.compile(r"\b(sk-[a-zA-Z0-9_\-]{20,})\b")),
    ("Anthropic API Key", re.compile(r"\b(sk-ant-[a-zA-Z0-9_\-]{20,})\b")),
    ("AWS Access Key ID", re.compile(r"\b(AKIA[0-9A-Z]{16})\b")),
    ("Private Key Header", re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----")),
    ("Bearer / JWT Token", re.compile(r"\b(ey[a-zA-Z0-9_-]{15,}\.ey[a-zA-Z0-9_-]{15,})\b")),
    ("Database URI with Password", re.compile(r"\b((?:postgres|mongodb|mysql|redis)://[^:\s]+:[^@\s]+@[^\s/]+)\b")),
    (".env Variable Leak", re.compile(r"\b(API_KEY|SECRET_KEY|DATABASE_PASSWORD|AWS_SECRET_ACCESS_KEY)\s*=\s*['\"]?([^'\"\s\n]{8,})['\"]?", re.IGNORECASE)),
]


def scan_secrets(text: str, source_label: str) -> List[Dict[str, str]]:
    """Scan text for credentials and secrets, redacting sensitive content."""
    findings = []
    if not text or len(text) < 8:
        return findings
    for label, pat in SECRET_LEAK_PATTERNS:
        for match in pat.finditer(text):
            val = match.group(0)
            redacted = val[:7] + "..." + val[-3:] if len(val) > 12 else val[:3] + "..."
            findings.append({
                "kind": label,
                "source": source_label,
                "preview": redacted,
                "recommendation": f"Remove sensitive credential ({label}) exposed in {source_label}.",
            })
    return findings


def find_browser_executable() -> Optional[str]:
    """Return the first available system Chrome/Chromium binary, or None to use Playwright's default."""
    env_bin = os.environ.get("CAO_QA_BROWSER_BIN")
    if env_bin and os.path.exists(env_bin):
        return env_bin
    for path in CHROME_CANDIDATES:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return None


def normalize_target_url(target: str) -> str:
    """Convert a file path or URL string into a valid navigable URL."""
    target = target.strip()
    if target.startswith(("http://", "https://", "file://")):
        return target
    p = Path(target).expanduser().resolve()
    if p.exists():
        return p.as_uri()
    if ":" in target and not target.startswith("/"):
        return f"http://{target}"
    return p.as_uri()


@dataclass
class NetworkEvent:
    method: str
    url: str
    status: Optional[int]
    latency_ms: float
    failed: bool = False
    failure_text: str = ""


@dataclass
class ElementAuditRecord:
    index: int
    tag: str
    element_id: str
    classes: str
    selector: str
    label: str
    aria_label: str
    title: str
    href: str
    onclick: str
    bbox: Dict[str, float]
    disabled: bool
    clicked: bool = False
    dom_changed: bool = False
    dom_delta_hash: str = ""
    text_delta_preview: str = ""
    url_changed: bool = False
    navigated_to: str = ""
    network_events: List[Dict[str, Any]] = field(default_factory=list)
    console_errors: List[str] = field(default_factory=list)
    console_warnings: List[str] = field(default_factory=list)
    console_logs: List[str] = field(default_factory=list)
    page_errors: List[str] = field(default_factory=list)
    backend_log_lines: List[str] = field(default_factory=list)
    backend_errors: List[str] = field(default_factory=list)
    action_signature: str = ""
    safety_skipped: bool = False
    form_autofilled: int = 0
    modal_opened: bool = False
    screenshot_path: str = ""


class PlaywrightQAAuditor:
    """Full-Stack Interactive QA & UI/UX Ergonomics Auditor powered by Playwright."""

    def __init__(
        self,
        target: str,
        backend_log_path: Optional[str] = None,
        max_elements: int = 60,
        click_wait_ms: int = 180,
        headless: bool = True,
        allow_destructive: bool = False,
        autofill_forms: bool = True,
        explore_modals: bool = True,
        screenshots_dir: Optional[str] = None,
        viewport_mode: str = "desktop",
    ):
        self.raw_target = target
        self.target_url = normalize_target_url(target)
        self.backend_log_path = Path(backend_log_path).expanduser().resolve() if backend_log_path else None
        self.max_elements = max_elements
        self.click_wait_ms = click_wait_ms
        self.headless = headless
        self.allow_destructive = allow_destructive
        self.autofill_forms = autofill_forms
        self.explore_modals = explore_modals
        self.screenshots_dir = Path(screenshots_dir).expanduser().resolve() if screenshots_dir else None
        self.viewport_mode = viewport_mode

    def _read_backend_log_offset(self) -> int:
        if not self.backend_log_path or not self.backend_log_path.exists():
            return 0
        try:
            return self.backend_log_path.stat().st_size
        except OSError:
            return 0

    def _read_backend_log_delta(self, start_offset: int) -> Tuple[List[str], List[str]]:
        if not self.backend_log_path or not self.backend_log_path.exists():
            return [], []
        try:
            with open(self.backend_log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(start_offset)
                new_text = f.read()
        except OSError:
            return [], []

        if not new_text.strip():
            return [], []

        lines = [line.strip() for line in new_text.splitlines() if line.strip()]
        err_pattern = re.compile(r"\b(ERROR|Exception|Traceback|CRITICAL|FATAL|500|Internal Server Error)\b", re.IGNORECASE)
        errors = [line for line in lines if err_pattern.search(line)]
        return lines, errors

    @staticmethod
    def _compute_dom_snapshot(page) -> Tuple[str, str]:
        """Return (structural_hash, visible_text_snapshot) of the current document body."""
        try:
            snapshot_data = page.evaluate(
                """() => {
                    if (!document.body) return { text: "", struct: "" };
                    const text = (document.body.innerText || "").replace(/\\s+/g, " ").trim();
                    const clone = document.body.cloneNode(true);
                    clone.querySelectorAll('script, style').forEach(el => el.remove());
                    clone.querySelectorAll('[data-cao-qa-idx]').forEach(el => el.removeAttribute('data-cao-qa-idx'));
                    const inputs = Array.from(document.querySelectorAll('input, select, textarea, details')).map(
                        el => `${el.id || el.name}:${el.value}:${el.checked}:${el.open}`
                    ).join('|');
                    const struct = clone.innerHTML.replace(/\\s+/g, " ").trim() + "||" + inputs;
                    return { text, struct };
                }"""
            )
            struct_str = snapshot_data.get("struct", "")
            text_str = snapshot_data.get("text", "")
            h = hashlib.sha256(struct_str.encode("utf-8", errors="ignore")).hexdigest()[:16]
            return h, text_str
        except Exception:
            return "error", ""

    @staticmethod
    def _compute_text_delta(before_text: str, after_text: str) -> str:
        if before_text == after_text:
            return ""
        before_words = before_text.split()
        after_words = after_text.split()
        # Find new substring or difference preview
        if len(after_text) >= len(before_text) and before_text in after_text:
            added = after_text.replace(before_text, "", 1).strip()
            return f"+{added[:120]}"
        # Otherwise find first differing token window
        for i, (bw, aw) in enumerate(zip(before_words, after_words)):
            if bw != aw:
                snippet = " ".join(after_words[max(0, i - 1) : i + 12])
                return f"~{snippet[:120]}"
        if len(after_words) > len(before_words):
            snippet = " ".join(after_words[len(before_words) : len(before_words) + 12])
            return f"+{snippet[:120]}"
        return "DOM mutated"

    def run_audit(self) -> Dict[str, Any]:
        """Execute full Playwright interactive QA and UX audit and return structured report."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            import shutil
            import subprocess

            uv_bin = shutil.which("uv")
            if not uv_bin:
                raise RuntimeError("playwright is not installed and 'uv' was not found on PATH")
            code = (
                "import json, sys; "
                f"sys.path.insert(0, {repr(str(Path(__file__).resolve().parent))}); "
                "from cao_qa import PlaywrightQAAuditor; "
                f"a = PlaywrightQAAuditor(target={repr(self.raw_target)}, "
                f"backend_log_path={repr(str(self.backend_log_path) if self.backend_log_path else None)}, "
                f"max_elements={self.max_elements}, click_wait_ms={self.click_wait_ms}, headless={self.headless}, "
                f"allow_destructive={self.allow_destructive}, autofill_forms={self.autofill_forms}, "
                f"explore_modals={self.explore_modals}, screenshots_dir={repr(str(self.screenshots_dir) if self.screenshots_dir else None)}, "
                f"viewport_mode={repr(self.viewport_mode)}); "
                "print(json.dumps(a.run_audit()))"
            )
            res = subprocess.run(
                [uv_bin, "run", "--with", "playwright", "python3", "-c", code],
                capture_output=True,
                text=True,
                check=True,
            )
            return json.loads(res.stdout.strip().splitlines()[-1])

        started_at = time.time()
        executable_path = find_browser_executable()
        initial_console_errors: List[str] = []
        initial_page_errors: List[str] = []
        initial_network_failures: List[Dict[str, Any]] = []

        with sync_playwright() as p:
            launch_kwargs: Dict[str, Any] = {
                "headless": self.headless,
                "args": ["--no-sandbox", "--disable-dev-shm-usage"],
            }
            if executable_path:
                launch_kwargs["executable_path"] = executable_path

            browser = p.chromium.launch(**launch_kwargs)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            # Automatically dismiss blocking alert/confirm/prompt dialogs while logging them
            dialog_messages: List[str] = []

            def _on_dialog(dialog):
                dialog_messages.append(f"{dialog.type}: {dialog.message}")
                try:
                    dialog.dismiss()
                except Exception:
                    pass

            page.on("dialog", _on_dialog)

            # Active collectors that switch between initial page load and per-element clicks
            active_console_errors: List[str] = initial_console_errors
            active_console_warnings: List[str] = []
            active_console_logs: List[str] = []
            active_page_errors: List[str] = initial_page_errors
            active_network_events: List[NetworkEvent] = []
            req_start_times: Dict[int, float] = {}
            secret_leaks: List[Dict[str, Any]] = []
            cors_issues: List[Dict[str, Any]] = []

            def _on_console(msg):
                mtype = msg.type
                text = msg.text
                if mtype == "error":
                    active_console_errors.append(text)
                elif mtype == "warning":
                    active_console_warnings.append(text)
                else:
                    active_console_logs.append(text)
                # QA-UIX Security: Scan console messages for leaked credentials
                leaks = scan_secrets(text, f"console.{mtype}")
                if leaks:
                    secret_leaks.extend(leaks)

            def _on_pageerror(exc):
                active_page_errors.append(str(exc))

            def _on_request(req):
                req_start_times[id(req)] = time.time()

            def _on_response(resp):
                req = resp.request
                t0 = req_start_times.pop(id(req), time.time())
                latency = round((time.time() - t0) * 1000.0, 1)
                active_network_events.append(
                    NetworkEvent(
                        method=req.method,
                        url=resp.url,
                        status=resp.status,
                        latency_ms=latency,
                        failed=resp.status >= 400,
                    )
                )

                # QA-UIX Security: CORS inspection
                headers = resp.headers
                allow_origin = headers.get("access-control-allow-origin", "")
                allow_creds = headers.get("access-control-allow-credentials", "").lower()
                if allow_origin == "*" and allow_creds == "true":
                    cors_issues.append({
                        "url": resp.url,
                        "issue": "Wildcard Origin with Credentials",
                        "detail": "Access-Control-Allow-Origin: * combined with Access-Control-Allow-Credentials: true permits cross-origin credential theft.",
                        "recommendation": f"Configure backend route {urlparse(resp.url).path} to restrict origins to explicit trusted domains.",
                    })

                # QA-UIX Security: Scan URL for leaked tokens/secrets
                url_leaks = scan_secrets(resp.url, f"API URL: {resp.url}")
                if url_leaks:
                    secret_leaks.extend(url_leaks)

            def _on_requestfailed(req):
                t0 = req_start_times.pop(id(req), time.time())
                latency = round((time.time() - t0) * 1000.0, 1)
                failure = req.failure or "request_failed"
                if isinstance(failure, dict):
                    failure_str = failure.get("errorText", str(failure))
                else:
                    failure_str = str(failure)
                active_network_events.append(
                    NetworkEvent(
                        method=req.method,
                        url=req.url,
                        status=None,
                        latency_ms=latency,
                        failed=True,
                        failure_text=failure_str,
                    )
                )

            page.on("console", _on_console)
            page.on("pageerror", _on_pageerror)
            page.on("request", _on_request)
            page.on("response", _on_response)
            page.on("requestfailed", _on_requestfailed)

            # 1. Navigate to target URL
            page.goto(self.target_url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(200)

            # QA-UIX Security: Scan initial DOM content for exposed API keys, tokens, and .env leaks
            try:
                dom_source = page.content()
                dom_leaks = scan_secrets(dom_source, "DOM source / inline scripts")
                if dom_leaks:
                    secret_leaks.extend(dom_leaks)
            except Exception:
                pass

            page_title = page.title()
            base_url = page.url
            base_parsed = urlparse(base_url)

            for ev in active_network_events:
                if ev.failed:
                    initial_network_failures.append(asdict(ev))

            # 2. Check Desktop & Mobile Viewport Overflow before mutating state
            viewport_overflow = self._check_viewport_overflow(page)

            # 3. Discover Interactive Elements on Desktop (1440x900)
            page.set_viewport_size({"width": 1440, "height": 900})
            page.wait_for_timeout(100)

            raw_elements = page.evaluate(
                """(maxElements) => {
                    const selector = 'button, a[href], [role="button"], input[type="submit"], input[type="button"], input[type="checkbox"], input[type="radio"], input[type="range"], label[for], label:has(input), select, summary, [role="tab"], [role="switch"], [onclick]';
                    const nodes = Array.from(document.querySelectorAll(selector));
                    const results = [];
                    nodes.forEach((el, idx) => {
                        if (results.length >= maxElements) return;
                        const rect = el.getBoundingClientRect();
                        const style = window.getComputedStyle(el);
                        if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) {
                            return;
                        }
                        if (rect.width === 0 && rect.height === 0) {
                            return;
                        }
                        el.setAttribute('data-cao-qa-idx', String(idx));
                        const tag = el.tagName.toLowerCase();
                        const id = el.id || '';
                        const classes = typeof el.className === 'string' ? el.className.trim() : '';
                        let labelText = (el.innerText || el.value || '').replace(/\\s+/g, ' ').trim();
                        if (!labelText && el.labels && el.labels.length > 0) {
                            labelText = (el.labels[0].innerText || '').replace(/\\s+/g, ' ').trim();
                        }
                        if (!labelText && el.closest('label')) {
                            labelText = (el.closest('label').innerText || '').replace(/\\s+/g, ' ').trim();
                        }
                        const text = labelText;
                        const ariaLabel = el.getAttribute('aria-label') || '';
                        const title = el.getAttribute('title') || '';
                        const href = el.getAttribute('href') || '';
                        const onclick = el.getAttribute('onclick') || '';
                        const disabled = Boolean(el.disabled || el.getAttribute('aria-disabled') === 'true');
                        let cssSelector = tag;
                        if (id) cssSelector += `#${id}`;
                        else if (classes) cssSelector += `.${classes.split(/\\s+/)[0]}`;
                        results.append ? results.append({}) : results.push({
                            index: idx,
                            tag,
                            element_id: id,
                            classes,
                            selector: cssSelector,
                            label: text.slice(0, 80),
                            aria_label: ariaLabel,
                            title,
                            href,
                            onclick,
                            bbox: {
                                x: Math.round(rect.x * 10) / 10,
                                y: Math.round(rect.y * 10) / 10,
                                width: Math.round(rect.width * 10) / 10,
                                height: Math.round(rect.height * 10) / 10
                            },
                            disabled
                        });
                    });
                    return results;
                }""",
                self.max_elements,
            )

            records: List[ElementAuditRecord] = [ElementAuditRecord(**item) for item in raw_elements]

            # 4. Interact with each discovered element and collect telemetry
            for rec in records:
                if rec.disabled:
                    continue

                # 1. Destructive Safety Guard: skip destructive actions unless allow_destructive is True
                ident_text = f"{rec.label} {rec.element_id} {rec.classes} {rec.title} {rec.aria_label} {rec.onclick}".lower()
                if not self.allow_destructive and DESTRUCTIVE_PATTERN.search(ident_text):
                    rec.safety_skipped = True
                    continue

                # Re-ensure data-cao-qa-idx exists if we reloaded page after a navigation
                loc = page.locator(f'[data-cao-qa-idx="{rec.index}"]').first
                if loc.count() == 0 and rec.element_id:
                    loc = page.locator(f"#{rec.element_id}").first

                if loc.count() == 0:
                    continue

                # 2. Smart Form Auto-Fill: inject realistic data into parent/associated form before submit
                if self.autofill_forms and (rec.tag == "button" or rec.tag == "input" or "submit" in rec.classes):
                    try:
                        filled_cnt = loc.evaluate("""(el) => {
                            const form = el.closest('form') || el.closest('[data-form]') || el.form;
                            if (!form) return 0;
                            const inputs = form.querySelectorAll('input:not([type="hidden"]):not([disabled]), textarea, select');
                            let count = 0;
                            inputs.forEach(inp => {
                                if (inp.value && String(inp.value).trim() !== '') return;
                                const type = (inp.type || '').toLowerCase();
                                const name = (inp.name || inp.id || '').toLowerCase();
                                if (type === 'email' || name.includes('email')) inp.value = 'qa.test@example.com';
                                else if (type === 'password' || name.includes('pass')) inp.value = 'QaP@ssw0rd!123';
                                else if (type === 'number' || name.includes('num') || name.includes('count') || name.includes('age')) inp.value = '42';
                                else if (type === 'tel' || name.includes('phone')) inp.value = '+1234567890';
                                else if (type === 'url') inp.value = 'https://example.com';
                                else if (type === 'checkbox' || type === 'radio') inp.checked = true;
                                else if (inp.tagName.toLowerCase() === 'select') {
                                    if (inp.options && inp.options.length > 1) inp.selectedIndex = 1;
                                } else {
                                    inp.value = name.includes('search') ? 'QA test query' : 'Test value';
                                }
                                inp.dispatchEvent(new Event('input', { bubbles: true }));
                                inp.dispatchEvent(new Event('change', { bubbles: true }));
                                count++;
                            });
                            return count;
                        }""")
                        rec.form_autofilled = filled_cnt or 0
                    except Exception:
                        pass

                # Reset per-click collectors
                click_console_errors: List[str] = []
                click_console_warnings: List[str] = []
                click_console_logs: List[str] = []
                click_page_errors: List[str] = []
                click_network_events: List[NetworkEvent] = []
                dialog_messages.clear()

                active_console_errors = click_console_errors
                active_console_warnings = click_console_warnings
                active_console_logs = click_console_logs
                active_page_errors = click_page_errors
                active_network_events = click_network_events

                before_hash, before_text = self._compute_dom_snapshot(page)
                before_url = page.url
                log_offset = self._read_backend_log_offset()

                # Check if link is an external URL so we don't leave the local audit target forever
                is_external_link = False
                if rec.tag == "a" and rec.href:
                    parsed_href = urlparse(rec.href)
                    if parsed_href.scheme in ("http", "https") and parsed_href.netloc and parsed_href.netloc != base_parsed.netloc:
                        is_external_link = True

                try:
                    if is_external_link:
                        # Don't navigate away to external internet sites during local UI audit;
                        # record the external href as its navigation target.
                        rec.clicked = True
                        rec.url_changed = True
                        rec.navigated_to = rec.href
                    else:
                        loc.scroll_into_view_if_needed(timeout=1500)
                        loc.click(timeout=2000)
                        rec.clicked = True
                        page.wait_for_timeout(self.click_wait_ms)
                except Exception:
                    # Try force click if obscured/animated
                    try:
                        loc.click(force=True, timeout=1500)
                        rec.clicked = True
                        page.wait_for_timeout(self.click_wait_ms)
                    except Exception:
                        rec.clicked = False

                after_url = page.url
                if not is_external_link and after_url != before_url:
                    rec.url_changed = True
                    rec.navigated_to = after_url

                after_hash, after_text = self._compute_dom_snapshot(page)
                if after_hash != before_hash or bool(dialog_messages):
                    rec.dom_changed = True
                    if dialog_messages:
                        rec.text_delta_preview = f"Dialog: {'; '.join(dialog_messages)}"
                        rec.dom_delta_hash = hashlib.sha256(rec.text_delta_preview.encode()).hexdigest()[:12]
                    else:
                        rec.text_delta_preview = self._compute_text_delta(before_text, after_text)
                        rec.dom_delta_hash = after_hash

                # 3. 2-Hop Modal / Dialog Exploration: if a modal opened, explore child actions then dismiss
                if self.explore_modals and rec.dom_changed:
                    try:
                        modal_loc = page.locator('dialog[open], [role="dialog"], .modal.show, .modal.active, .modal[style*="display: block"]').first
                        if modal_loc.count() > 0 and modal_loc.is_visible():
                            rec.modal_opened = True
                            child_btns = modal_loc.locator('button:not([disabled]), [role="button"]:not([aria-disabled="true"]), input[type="submit"]:not([disabled])').all()
                            for cb in child_btns[:3]:
                                try:
                                    if cb.is_visible():
                                        cb_text = (cb.inner_text() or cb.get_attribute("aria-label") or "").strip().lower()
                                        if cb_text not in ("close", "cancel", "x", "✕", "dismiss"):
                                            cb.click(timeout=1000)
                                            page.wait_for_timeout(self.click_wait_ms)
                                except Exception:
                                    pass
                            try:
                                page.keyboard.press("Escape")
                                page.wait_for_timeout(60)
                            except Exception:
                                pass
                    except Exception:
                        pass

                rec.network_events = [asdict(ev) for ev in click_network_events]
                rec.console_errors = list(click_console_errors)
                rec.console_warnings = list(click_console_warnings)
                rec.console_logs = list(click_console_logs)
                rec.page_errors = list(click_page_errors)

                backend_lines, backend_errs = self._read_backend_log_delta(log_offset)
                rec.backend_log_lines = backend_lines
                rec.backend_errors = backend_errs

                # 4. Visual Evidence Capture: snapshot element with red outline if issue detected
                has_issues = bool(rec.console_errors or rec.page_errors or [ev for ev in click_network_events if ev.failed] or rec.backend_errors)
                if self.screenshots_dir and has_issues:
                    try:
                        shot_name = f"issue_{rec.index}_{rec.tag}_{int(time.time() * 1000) % 100000}.png"
                        shot_path = self.screenshots_dir / shot_name
                        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
                        loc.evaluate("(el) => { el.style.outline = '3px solid red'; el.style.boxShadow = '0 0 10px rgba(255,0,0,0.8)'; }")
                        page.screenshot(path=str(shot_path))
                        rec.screenshot_path = str(shot_path)
                    except Exception:
                        pass

                # Build deterministic action signature for redundancy detection
                api_sig = ",".join(
                    sorted(f"{ev.method}:{urlparse(ev.url).path}" for ev in click_network_events)
                )
                handler_sig = (rec.onclick or rec.href or "").strip()
                rec.action_signature = self._build_action_signature(
                    api_sig=api_sig,
                    dom_delta_hash=rec.dom_delta_hash,
                    text_delta=rec.text_delta_preview,
                    handler_sig=handler_sig,
                    console_logs=rec.console_logs,
                    navigated_to=rec.navigated_to,
                )

                # Restore clean page state if the click mutated the DOM or navigated away
                if (rec.dom_changed or rec.url_changed) and not is_external_link:
                    try:
                        page.goto(self.target_url, wait_until="domcontentloaded", timeout=10000)
                        page.wait_for_timeout(60)
                        page.evaluate(
                            """(maxElements) => {
                                const selector = 'button, a[href], [role="button"], input[type="submit"], input[type="button"], input[type="checkbox"], input[type="radio"], input[type="range"], label[for], label:has(input), select, summary, [role="tab"], [role="switch"], [onclick]';
                                const nodes = Array.from(document.querySelectorAll(selector));
                                let count = 0;
                                nodes.forEach((el, idx) => {
                                    if (count >= maxElements) return;
                                    const rect = el.getBoundingClientRect();
                                    const style = window.getComputedStyle(el);
                                    if (style.display === 'none' || style.visibility === 'hidden' || parseFloat(style.opacity) === 0) return;
                                    if (rect.width === 0 && rect.height === 0) return;
                                    el.setAttribute('data-cao-qa-idx', String(idx));
                                    count++;
                                });
                            }""",
                            self.max_elements,
                        )
                    except Exception:
                        pass

            browser.close()

        duration_s = round(time.time() - started_at, 2)
        return self._analyze_findings(
            page_title=page_title,
            records=records,
            viewport_overflow=viewport_overflow,
            initial_console_errors=initial_console_errors,
            initial_page_errors=initial_page_errors,
            initial_network_failures=initial_network_failures,
            browser_executable=executable_path or "playwright-chromium",
            duration_s=duration_s,
            secret_leaks=secret_leaks,
            cors_issues=cors_issues,
        )

    @staticmethod
    def _build_action_signature(
        api_sig: str,
        dom_delta_hash: str,
        text_delta: str,
        handler_sig: str,
        console_logs: List[str],
        navigated_to: str = "",
    ) -> str:
        """Create a normalized effect signature to detect duplicate/redundant buttons."""
        if not api_sig and not dom_delta_hash and not handler_sig and not console_logs and not navigated_to:
            return ""
        parts = []
        if api_sig:
            parts.append(f"api={api_sig}")
        if dom_delta_hash:
            parts.append(f"dom={dom_delta_hash}")
        if navigated_to:
            parts.append(f"nav={navigated_to}")
        if not parts and handler_sig:
            parts.append(f"handler={handler_sig}")
        if not parts and console_logs:
            parts.append(f"log={console_logs[0][:60]}")
        return "|".join(parts)

    def _check_viewport_overflow(self, page) -> Dict[str, Any]:
        """Test both Desktop (1440x900) and Mobile (390x844) viewports for horizontal overflow."""
        viewports = {
            "desktop": {"width": 1440, "height": 900},
            "mobile": {"width": 390, "height": 844},
        }
        results: Dict[str, Any] = {}
        for name, vp in viewports.items():
            page.set_viewport_size(vp)
            page.wait_for_timeout(80)
            info = page.evaluate(
                """() => {
                    const docWidth = document.documentElement.scrollWidth;
                    const winWidth = window.innerWidth;
                    const hasOverflow = docWidth > winWidth + 2;
                    const overflowing = [];
                    if (hasOverflow) {
                        document.querySelectorAll('*').forEach(el => {
                            const r = el.getBoundingClientRect();
                            if (r.right > winWidth + 4 && overflowing.length < 5) {
                                const tag = el.tagName.toLowerCase();
                                const id = el.id ? `#${el.id}` : '';
                                const cls = (typeof el.className === 'string' && el.className.trim())
                                    ? `.${el.className.trim().split(/\\s+/)[0]}` : '';
                                overflowing.push(`${tag}${id}${cls} (right=${Math.round(r.right)}px)`);
                            }
                        });
                    }
                    return {
                        viewport_width: winWidth,
                        scroll_width: docWidth,
                        overflow_px: Math.max(0, docWidth - winWidth),
                        has_overflow: hasOverflow,
                        offending_elements: overflowing
                    };
                }"""
            )
            results[name] = info
        return results

    def _analyze_findings(
        self,
        page_title: str,
        records: List[ElementAuditRecord],
        viewport_overflow: Dict[str, Any],
        initial_console_errors: List[str],
        initial_page_errors: List[str],
        initial_network_failures: List[Dict[str, Any]],
        browser_executable: str,
        duration_s: float,
        secret_leaks: Optional[List[Dict[str, Any]]] = None,
        cors_issues: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        secret_leaks = secret_leaks or []
        cors_issues = cors_issues or []
        redundant_controls: List[Dict[str, Any]] = []
        dead_clicks: List[Dict[str, Any]] = []
        broken_interactions: List[Dict[str, Any]] = []
        small_targets: List[Dict[str, Any]] = []
        unlabeled_controls: List[Dict[str, Any]] = []

        # Group by action_signature to detect redundant buttons/links
        sig_groups: Dict[str, List[ElementAuditRecord]] = {}

        for rec in records:
            display_name = rec.label or rec.aria_label or rec.title or rec.selector

            # 1. Small Hit Target (< 24x24px WCAG 2.2 AA)
            w = rec.bbox.get("width", 0)
            h = rec.bbox.get("height", 0)
            if 0 < w < 24 or 0 < h < 24:
                small_targets.append(
                    {
                        "index": rec.index,
                        "selector": rec.selector,
                        "label": display_name,
                        "width": w,
                        "height": h,
                        "recommendation": f"Increase target size of '{display_name}' ({w}x{h}px) to at least 24x24px (WCAG 2.2 AA).",
                    }
                )

            # 2. Unlabeled Control
            if not rec.label.strip() and not rec.aria_label.strip() and not rec.title.strip():
                unlabeled_controls.append(
                    {
                        "index": rec.index,
                        "selector": rec.selector,
                        "tag": rec.tag,
                        "recommendation": f"Add visible text or an accessible `aria-label` to `{rec.selector}`.",
                    }
                )

            if not rec.clicked:
                continue

            # 3. Broken Interactions (JS errors, HTTP 4xx/5xx, failed requests, or backend log errors)
            failed_net = [ev for ev in rec.network_events if ev.get("failed") or (ev.get("status") or 0) >= 400]
            if rec.console_errors or rec.page_errors or failed_net or rec.backend_errors:
                broken_interactions.append(
                    {
                        "index": rec.index,
                        "selector": rec.selector,
                        "label": display_name,
                        "console_errors": rec.console_errors,
                        "page_errors": rec.page_errors,
                        "failed_network": failed_net,
                        "backend_errors": rec.backend_errors,
                    }
                )

            # 4. Silent Dead Clicks
            has_any_effect = (
                rec.dom_changed
                or rec.url_changed
                or bool(rec.network_events)
                or bool(rec.console_errors)
                or bool(rec.console_warnings)
                or bool(rec.console_logs)
                or bool(rec.page_errors)
                or bool(rec.backend_log_lines)
                or rec.tag == "select"
            )
            if not has_any_effect:
                dead_clicks.append(
                    {
                        "index": rec.index,
                        "selector": rec.selector,
                        "label": display_name,
                        "tag": rec.tag,
                        "recommendation": f"Control '{display_name}' ({rec.selector}) produced zero DOM, network, URL, or state change when clicked. Wire up its handler or remove it.",
                    }
                )

            # 5. Collect for Redundant Controls
            if rec.action_signature:
                sig_groups.setdefault(rec.action_signature, []).append(rec)

        for sig, group in sig_groups.items():
            if len(group) > 1:
                labels = [g.label or g.aria_label or g.selector for g in group]
                selectors = [g.selector for g in group]
                redundant_controls.append(
                    {
                        "action_signature": sig,
                        "count": len(group),
                        "labels": labels,
                        "selectors": selectors,
                        "indices": [g.index for g in group],
                        "recommendation": (
                            f"Consolidate {len(group)} duplicate controls ({', '.join(repr(l) for l in labels)}) "
                            f"that trigger the exact same action signature `{sig}`."
                        ),
                    }
                )

        # 6. Synthesize Concrete UX Simplification Hints
        safety_skipped = [
            {
                "index": rec.index,
                "selector": rec.selector,
                "label": rec.label or rec.aria_label or rec.title or rec.selector,
                "recommendation": f"Destructive action '{rec.label or rec.selector}' was safely skipped (pass --allow-destructive to test).",
            }
            for rec in records
            if rec.safety_skipped
        ]
        forms_autofilled_count = sum(1 for rec in records if rec.form_autofilled > 0)
        modals_opened_count = sum(1 for rec in records if rec.modal_opened)
        screenshots_saved = [rec.screenshot_path for rec in records if rec.screenshot_path]

        ux_simplification_hints: List[str] = []
        for leak in secret_leaks:
            ux_simplification_hints.append(
                f"CRITICAL SECURITY: {leak['kind']} exposed in {leak['source']} ({leak['preview']}). {leak['recommendation']}"
            )
        for c in cors_issues:
            ux_simplification_hints.append(
                f"CORS VULNERABILITY: {c['issue']} on {c['url']}. {c['recommendation']}"
            )
        for rc in redundant_controls:
            ux_simplification_hints.append(rc["recommendation"])
        for dc in dead_clicks:
            ux_simplification_hints.append(dc["recommendation"])
        for bi in broken_interactions:
            err_summary = []
            if bi["console_errors"] or bi["page_errors"]:
                err_summary.append(f"JS error ({(bi['console_errors'] + bi['page_errors'])[0][:80]})")
            if bi["failed_network"]:
                net0 = bi["failed_network"][0]
                err_summary.append(f"HTTP {net0.get('status') or 'ERR'} on {net0.get('method')} {net0.get('url')}")
            if bi["backend_errors"]:
                err_summary.append(f"Backend error ({bi['backend_errors'][0][:80]})")
            ux_simplification_hints.append(
                f"Fix broken interaction on '{bi['label']}' ({bi['selector']}): {', '.join(err_summary)}."
            )
        for st in small_targets:
            ux_simplification_hints.append(st["recommendation"])
        for uc in unlabeled_controls:
            ux_simplification_hints.append(uc["recommendation"])
        for vp_name, vp_data in viewport_overflow.items():
            if vp_data.get("has_overflow"):
                ux_simplification_hints.append(
                    f"Fix {vp_name} horizontal overflow (+{vp_data['overflow_px']}px beyond {vp_data['viewport_width']}px viewport; "
                    f"offenders: {', '.join(vp_data.get('offending_elements', [])[:3]) or 'root container'})."
                )
        if len(records) > 25:
            ux_simplification_hints.append(
                f"High control density ({len(records)} interactive controls on a single screen). "
                "Consider progressive disclosure (grouping secondary actions into a collapsible drawer or menu)."
            )

        # Calculate QA & UX Health Score (0-100)
        deductions = (
            len(broken_interactions) * 18
            + len(dead_clicks) * 10
            + len(redundant_controls) * 8
            + len(small_targets) * 5
            + len(unlabeled_controls) * 5
            + len(secret_leaks) * 35
            + len(cors_issues) * 20
            + sum(10 for vp in viewport_overflow.values() if vp.get("has_overflow"))
        )
        score = max(0, 100 - deductions)
        if broken_interactions or secret_leaks or cors_issues:
            status = "FAIL"
        elif dead_clicks or redundant_controls or small_targets or unlabeled_controls or any(
            vp.get("has_overflow") for vp in viewport_overflow.values()
        ):
            status = "WARN"
        else:
            status = "PASS"

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target": self.raw_target,
            "target_url": self.target_url,
            "page_title": page_title,
            "browser_executable": browser_executable,
            "duration_seconds": duration_s,
            "status": status,
            "health_score": score,
            "summary": {
                "total_interactive_elements": len(records),
                "clicked_elements": sum(1 for r in records if r.clicked),
                "broken_interactions_count": len(broken_interactions),
                "dead_clicks_count": len(dead_clicks),
                "redundant_control_groups_count": len(redundant_controls),
                "small_targets_count": len(small_targets),
                "unlabeled_controls_count": len(unlabeled_controls),
                "safety_skipped_count": len(safety_skipped),
                "forms_autofilled_count": forms_autofilled_count,
                "modals_opened_count": modals_opened_count,
                "screenshots_count": len(screenshots_saved),
                "secret_leaks_count": len(secret_leaks),
                "cors_issues_count": len(cors_issues),
                "desktop_overflow": viewport_overflow.get("desktop", {}).get("has_overflow", False),
                "mobile_overflow": viewport_overflow.get("mobile", {}).get("has_overflow", False),
            },
            "initial_load_errors": {
                "console_errors": initial_console_errors,
                "page_errors": initial_page_errors,
                "network_failures": initial_network_failures,
            },
            "heuristics": {
                "broken_interactions": broken_interactions,
                "redundant_controls": redundant_controls,
                "dead_clicks": dead_clicks,
                "small_targets": small_targets,
                "unlabeled_controls": unlabeled_controls,
                "safety_skipped_controls": safety_skipped,
                "screenshots": screenshots_saved,
                "secret_leaks": secret_leaks,
                "cors_issues": cors_issues,
                "viewport_overflow": viewport_overflow,
                "ux_simplification_hints": ux_simplification_hints,
            },
            "elements": [asdict(r) for r in records],
        }

    @staticmethod
    def render_markdown(report: Dict[str, Any]) -> str:
        """Render a rich Markdown QA & UX Ergonomics Audit Report."""
        s = report["summary"]
        h = report["heuristics"]
        lines = [
            f"# Playwright Autonomous QA & UI/UX Ergonomics Report",
            "",
            f"- **Target:** `{report['target']}` (`{report['target_url']}`)",
            f"- **Page Title:** {report.get('page_title') or '(untitled)'}",
            f"- **Status:** **{report['status']}** (Health Score: **{report['health_score']}/100**)",
            f"- **Browser Engine:** `{report['browser_executable']}`",
            f"- **Audit Duration:** `{report['duration_seconds']}s`",
            f"- **Timestamp:** `{report['timestamp']}`",
            "",
            "## 1. Executive Summary",
            "",
            "| Metric | Count / Status |",
            "|---|---|",
            f"| Interactive Controls Discovered | `{s['total_interactive_elements']}` (Clicked: `{s['clicked_elements']}`) |",
            f"| Broken Interactions (JS / HTTP 4xx-5xx / Backend Errors) | `{s['broken_interactions_count']}` |",
            f"| Silent Dead Clicks (Zero Effect) | `{s['dead_clicks_count']}` |",
            f"| Redundant / Duplicate Control Groups | `{s['redundant_control_groups_count']}` |",
            f"| Small Hit Targets (`< 24x24 px`) | `{s['small_targets_count']}` |",
            f"| Unlabeled Controls (Missing A11y Name) | `{s['unlabeled_controls_count']}` |",
            f"| Desktop Horizontal Overflow (`1440x900`) | `{'YES' if s['desktop_overflow'] else 'NO'}` |",
            f"| Mobile Horizontal Overflow (`390x844`) | `{'YES' if s['mobile_overflow'] else 'NO'}` |",
            f"| Destructive Actions Safely Skipped | `{s.get('safety_skipped_count', 0)}` |",
            f"| Forms Smartly Auto-filled | `{s.get('forms_autofilled_count', 0)}` |",
            f"| Dialog / Modal Exploration Cycles | `{s.get('modals_opened_count', 0)}` |",
            f"| Visual Issue Screenshots Saved | `{s.get('screenshots_count', 0)}` |",
            f"| Secret & Token Leaks Detected | `{s.get('secret_leaks_count', 0)}` |",
            f"| Insecure CORS Configurations | `{s.get('cors_issues_count', 0)}` |",
            "",
        ]

        # Broken interactions
        lines.append("## 2. Full-Stack Telemetry & Broken Interactions")
        lines.append("")
        if not h["broken_interactions"]:
            lines.append("No console errors, uncaught JS exceptions, HTTP 4xx/5xx responses, or backend log errors triggered by UI clicks.")
        else:
            for item in h["broken_interactions"]:
                lines.append(f"### `{item['selector']}` — **{item['label']}** (Index #{item['index']})")
                for ce in item["console_errors"]:
                    lines.append(f"- **Console Error:** `{ce}`")
                for pe in item["page_errors"]:
                    lines.append(f"- **Uncaught PageError:** `{pe}`")
                for net in item["failed_network"]:
                    lines.append(
                        f"- **Network Failure:** `{net.get('method')} {net.get('url')}` -> "
                        f"Status `{net.get('status') or net.get('failure_text')}` ({net.get('latency_ms')} ms)"
                    )
                for be in item["backend_errors"]:
                    lines.append(f"- **Correlated Backend Log Error:** `{be}`")
                lines.append("")

        # Redundant controls
        lines.append("## 3. Redundant Controls (Duplicate Functionality)")
        lines.append("")
        if not h["redundant_controls"]:
            lines.append("No redundant buttons or duplicate action controls detected.")
        else:
            for rc in h["redundant_controls"]:
                labels_str = ", ".join(f"`{l}`" for l in rc["labels"])
                sels_str = ", ".join(f"`{sel}`" for sel in rc["selectors"])
                lines.append(
                    f"- **{rc['count']} Duplicate Controls ({labels_str}):** Selectors {sels_str} share identical effect signature `{rc['action_signature']}`."
                )
        lines.append("")

        # Dead clicks
        lines.append("## 4. Silent Dead Clicks")
        lines.append("")
        if not h["dead_clicks"]:
            lines.append("All clicked interactive controls produced observable DOM, URL, network, or state feedback.")
        else:
            for dc in h["dead_clicks"]:
                lines.append(f"- **`{dc['selector']}` ({dc['label']}):** Zero DOM delta, zero network calls, zero URL/console effect.")
        lines.append("")

        # Ergonomics & Accessibility
        lines.append("## 5. Ergonomics, Hit Targets & Viewport Overflow")
        lines.append("")
        if not h["small_targets"] and not h["unlabeled_controls"] and not s["desktop_overflow"] and not s["mobile_overflow"]:
            lines.append("All controls meet minimum 24x24px target sizing, have accessible labels, and fit both desktop and mobile viewports.")
        else:
            for st in h["small_targets"]:
                lines.append(f"- **Small Target:** `{st['selector']}` (`{st['label']}`) is `{st['width']}x{st['height']}px` (< 24x24px).")
            for uc in h["unlabeled_controls"]:
                lines.append(f"- **Unlabeled Control:** `{uc['selector']}` (`<{uc['tag']}>`) has no visible text, `aria-label`, or `title`.")
            for vp_name, vp in h["viewport_overflow"].items():
                if vp.get("has_overflow"):
                    lines.append(
                        f"- **Viewport Overflow ({vp_name} `{vp['viewport_width']}px`):** "
                        f"Scroll width is `{vp['scroll_width']}px` (+`{vp['overflow_px']}px` overflow). "
                        f"Offenders: {', '.join(vp.get('offending_elements', [])) or 'root'}"
                    )
        lines.append("")

        # Security, Secrets & CORS
        lines.append("## 6. Security, Secrets & CORS Audit")
        lines.append("")
        if not h.get("secret_leaks") and not h.get("cors_issues"):
            lines.append("No sensitive credentials, API keys, or insecure wildcard CORS configurations detected in DOM, console, or network traces.")
        else:
            for leak in h.get("secret_leaks", []):
                lines.append(f"- 🚨 **Secret Exposed ({leak['kind']}):** Found in `{leak['source']}` (`{leak['preview']}`). {leak['recommendation']}")
            for c in h.get("cors_issues", []):
                lines.append(f"- 🌐 **CORS Issue ({c['issue']}):** `{c['url']}`. {c['detail']} {c['recommendation']}")
        lines.append("")

        # UX Simplification Hints
        lines.append("## 7. Actionable UX Simplification & Remediation Plan")
        lines.append("")
        if not h["ux_simplification_hints"]:
            lines.append("- UI is clean, responsive, and free of redundant or dead controls.")
        else:
            for idx, hint in enumerate(h["ux_simplification_hints"], 1):
                lines.append(f"{idx}. {hint}")
        lines.append("")

        return "\n".join(lines)

    def save_reports(
        self,
        report: Dict[str, Any],
        out_md: Optional[Path] = None,
        out_json: Optional[Path] = None,
    ) -> Tuple[Path, Path]:
        repo_root = Path(__file__).resolve().parent.parent
        audit_dir = repo_root / "wcao" / "audit"
        audit_dir.mkdir(parents=True, exist_ok=True)

        md_path = out_md or (audit_dir / "qa_ux_report.md")
        json_path = out_json or (audit_dir / "qa_ux_report.json")
        md_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.parent.mkdir(parents=True, exist_ok=True)

        md_path.write_text(self.render_markdown(report), encoding="utf-8")
        json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return md_path, json_path
