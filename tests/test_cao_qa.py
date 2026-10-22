"""Tests for Playwright Autonomous QA, Full-Stack Telemetry & UI/UX Ergonomics Auditor (cao_qa.py)."""
import http.server
import json
import socketserver
import sys
import threading
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_DIR = REPO_ROOT / "run"
if str(RUN_DIR) not in sys.path:
    sys.path.insert(0, str(RUN_DIR))

from cao_qa import PlaywrightQAAuditor, find_browser_executable, normalize_target_url


FIXTURE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CAO-QA Full-Stack Test Fixture</title>
  <style>
    body { margin: 0; font-family: sans-serif; }
    .btn { padding: 10px 18px; font-size: 14px; cursor: pointer; }
    #tiny-icon-btn {
      width: 14px;
      height: 14px;
      padding: 0;
      border: 1px solid #333;
      background: #eee;
    }
    .wide-banner {
      width: 650px;
      height: 30px;
      background: #f0f0f0;
    }
  </style>
</head>
<body>
  <h1>Dashboard Under Audit</h1>
  <div id="status-box">Ready</div>
  <div class="wide-banner">Wide banner causing mobile overflow on 390px screen</div>

  <!-- 1. Two redundant buttons performing the exact same API call & DOM update -->
  <button id="btn-save-top" class="btn" onclick="saveConfig()">Save Config</button>
  <button id="btn-save-bottom" class="btn" onclick="saveConfig()">Apply Config</button>

  <!-- 2. Silent dead button that does nothing at all -->
  <button id="btn-dead" class="btn">Export CSV (Unwired)</button>

  <!-- 3. Broken button that logs console.error and hits a 500 endpoint -->
  <button id="btn-broken" class="btn" onclick="triggerCrash()">Sync Cloud</button>

  <!-- 4. Tiny (<24x24px) unlabeled button -->
  <button id="tiny-icon-btn" onclick="toggleHint()"></button>

  <script>
    async function saveConfig() {
      const res = await fetch('/api/save', { method: 'POST' });
      const data = await res.json();
      document.getElementById('status-box').innerText = 'Saved: ' + data.status;
    }

    async function triggerCrash() {
      console.error('UncaughtSyncError: Cloud token missing in state');
      await fetch('/api/crash', { method: 'POST' });
    }

    function toggleHint() {
      document.getElementById('status-box').innerText = 'Hint toggled';
    }
  </script>
</body>
</html>
"""


@pytest.fixture
def qa_test_server(tmp_path):
    """Spin up a lightweight local HTTP server with backend logging for full-stack correlation tests."""
    backend_log = tmp_path / "backend.log"
    backend_log.write_text("", encoding="utf-8")

    class Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            body = FIXTURE_HTML.encode("utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            if self.path == "/api/save":
                with open(backend_log, "a", encoding="utf-8") as f:
                    f.write("INFO [api.save] Configuration saved successfully\n")
                payload = json.dumps({"status": "ok"}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            elif self.path == "/api/crash":
                with open(backend_log, "a", encoding="utf-8") as f:
                    f.write("ERROR [api.crash] Traceback: DatabaseConnectionError on /api/crash (HTTP 500)\n")
                payload = json.dumps({"error": "Internal Server Error"}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_response(404)
                self.end_headers()

    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True

    server = ThreadedTCPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}", backend_log
    server.shutdown()
    server.server_close()


def test_normalize_target_url_and_browser_detection(tmp_path):
    html_file = tmp_path / "sample.html"
    html_file.write_text("<html></html>", encoding="utf-8")
    assert normalize_target_url(str(html_file)).startswith("file://")
    assert normalize_target_url("http://127.0.0.1:8000") == "http://127.0.0.1:8000"
    assert normalize_target_url("localhost:3000") == "http://localhost:3000"
    # Browser binary detection returns either valid executable path or None
    exe = find_browser_executable()
    assert exe is None or Path(exe).exists()


def test_playwright_qa_auditor_catches_all_ux_and_fullstack_defects(qa_test_server, tmp_path):
    url, backend_log = qa_test_server
    auditor = PlaywrightQAAuditor(
        target=url,
        backend_log_path=str(backend_log),
        max_elements=25,
        click_wait_ms=120,
    )
    report = auditor.run_audit()

    assert report["status"] == "FAIL"
    assert report["summary"]["total_interactive_elements"] == 5
    assert report["summary"]["clicked_elements"] == 5

    heuristics = report["heuristics"]

    # 1. Redundant controls: #btn-save-top and #btn-save-bottom share POST:/api/save + DOM mutation
    redundant = heuristics["redundant_controls"]
    assert len(redundant) == 1
    assert set(redundant[0]["selectors"]) == {"button#btn-save-top", "button#btn-save-bottom"}
    assert "api=POST:/api/save" in redundant[0]["action_signature"]

    # 2. Silent dead click: #btn-dead
    dead = heuristics["dead_clicks"]
    assert len(dead) == 1
    assert dead[0]["selector"] == "button#btn-dead"

    # 3. Broken interaction: #btn-broken triggers console.error + HTTP 500 + backend log error
    broken = heuristics["broken_interactions"]
    assert len(broken) == 1
    b0 = broken[0]
    assert b0["selector"] == "button#btn-broken"
    assert any("UncaughtSyncError" in msg for msg in b0["console_errors"])
    assert any(net["status"] == 500 and "/api/crash" in net["url"] for net in b0["failed_network"])
    assert any("DatabaseConnectionError" in line for line in b0["backend_errors"])

    # 4. Small target (<24x24px) & Unlabeled control: #tiny-icon-btn
    small = heuristics["small_targets"]
    assert any(st["selector"] == "button#tiny-icon-btn" for st in small)
    unlabeled = heuristics["unlabeled_controls"]
    assert any(uc["selector"] == "button#tiny-icon-btn" for uc in unlabeled)

    # 5. Viewport overflow: 650px banner fits 1440px desktop, overflows 390px mobile
    vp = heuristics["viewport_overflow"]
    assert vp["desktop"]["has_overflow"] is False
    assert vp["mobile"]["has_overflow"] is True
    assert vp["mobile"]["overflow_px"] > 200

    # 6. Save Markdown & JSON reports
    out_md = tmp_path / "qa_ux_report.md"
    out_json = tmp_path / "qa_ux_report.json"
    auditor.save_reports(report, out_md=out_md, out_json=out_json)
    assert out_md.exists()
    assert out_json.exists()
    md_text = out_md.read_text(encoding="utf-8")
    assert "Redundant Controls" in md_text
    assert "Silent Dead Clicks" in md_text
    assert "DatabaseConnectionError" in md_text
