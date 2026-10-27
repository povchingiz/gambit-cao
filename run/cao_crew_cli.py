#!/usr/bin/env python3
"""cao_crew_cli.py — The Unified Single-Entrypoint CLI for cao-crew (`crew` / `cao-crew`).

Consolidates all 17 loose commands into 1 intuitive binary with clean subcommands:
  crew status     - Single unified dashboard: fleet, active workers, tokens, quotas
  crew fleet      - Cross-project workstation conductor (status, dispatch, inspect)
  crew test       - Playwright autonomous QA, full-stack telemetry & UX auditor (cao-qa)
  crew repair     - Closed-loop self-repair in ephemeral git worktree sandbox (cao-repair)
  crew run        - Interactive supervisor in tmux (cao-run)
  crew auto       - Autonomous headless DAG execution (cao-auto)
  crew stop       - Clean shutdown of workers & daemon (cao-stop)
  crew sandbox    - Git worktree sandbox manager (cao-sandbox)
  crew evolve     - Protected prompt self-evolution loop (cao-evolve)
  crew doctor     - Pre-flight diagnostic & 1-click wizard (cao-doctor / cao-init)
  crew terminal   - Attach to the interactive crew fleet supervisor session
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


def forward_to_script(script_name: str, args: List[str]) -> int:
    script_path = HERE / script_name
    if not script_path.exists():
        print(f"Error: Internal script not found: {script_path}", file=sys.stderr)
        return 1

    cmd = [str(script_path)] + args
    try:
        # Check if Python script or shell script
        first_line = script_path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
        if "python" in first_line:
            cmd = [sys.executable, str(script_path)] + args
        elif "bash" in first_line or "sh" in first_line:
            cmd = ["bash", str(script_path)] + args

        res = subprocess.run(cmd)
        return res.returncode
    except KeyboardInterrupt:
        return 130
    except Exception as exc:
        print(f"Error executing {script_name}: {exc}", file=sys.stderr)
        return 1


def show_unified_status(args: List[str]) -> int:
    """Unified workstation dashboard combining Fleet, Tokens, Quotas, and Tmux sessions."""
    print("🛸 CAO-CREW — Unified Workstation & Fleet Dashboard")
    print("=" * 88)

    # 1. Fleet Projects Overview
    try:
        from cao_fleet import FleetConductor
        conductor = FleetConductor()
        projects = conductor.list_projects()
        print("📁 Workstation Projects:")
        print(f"   {'PROJECT':16s} | {'BRANCH':12s} | {'STATUS':10s} | {'TASKS':6s} | ACTIVE GOAL")
        print("   " + "-" * 82)
        for p in projects:
            branch = p.get("git", {}).get("branch", "detached")
            tasks_str = p.get("tasks_progress", "0/0")
            status_str = p.get("status", "idle").upper()
            active_str = (p.get("active_task") or "None")[:34]
            print(f"   {p['name']:16s} | {branch:12s} | {status_str:10s} | {tasks_str:6s} | {active_str}")
    except Exception as exc:
        print(f"   Fleet inspection unavailable: {exc}")

    print("-" * 88)

    # 2. Token & Provider Quotas
    try:
        from run.cao_limits import get_limits
        lr = get_limits()
        print("⚡ Provider Quotas & Utilization:")
        # Claude
        if lr.claude:
            c_status = "BLOCKED" if lr.claude.is_blocked() else ("WARN" if lr.claude.is_near_limit() else "HEALTHY")
            windows_info = ", ".join(f"{w.name}: {w.utilization * 100:.0f}%" for w in lr.claude.windows if w.utilization is not None)
            print(f"   • Anthropic (Claude): {c_status:10s} | {windows_info or 'Available'}")
        else:
            print("   • Anthropic (Claude): READY      | No rate limit events")
        # Codex
        if lr.codex:
            cx_status = "BLOCKED" if lr.codex.is_blocked() else "READY"
            print(f"   • OpenAI (Codex):     {cx_status:10s} | Available")
        else:
            print("   • OpenAI (Codex):     READY      | Available")
        # OpenCode
        if lr.opencode:
            cost_str = f"${lr.opencode.cost:.2f}" if lr.opencode.cost else "Free/Local"
            print(f"   • OpenCode (Bulk):    READY      | Spend: {cost_str} ({lr.opencode.tokens_in + lr.opencode.tokens_out} tokens)")
        else:
            print("   • OpenCode (Bulk):    READY      | Available")
    except Exception as exc:
        print(f"   Quota inspection unavailable: {exc}")

    print("-" * 88)

    # 3. Active Background Sessions
    try:
        tmux_res = subprocess.run(["tmux", "list-sessions"], capture_output=True, text=True)
        sessions = [line.split(":")[0] for line in tmux_res.stdout.splitlines() if line.strip()]
        cao_sessions = [s for s in sessions if "cao" in s or "crew" in s]
        print(f"🖥️  Active Background Panes: {len(cao_sessions)} sessions ({', '.join(cao_sessions) or 'None'})")
    except Exception:
        print("🖥️  Active Background Panes: tmux not running")

    print("=" * 88)
    print("💡 Quick actions: crew fleet | crew test <url> | crew repair <target> | crew run")
    return 0


def attach_terminal() -> int:
    """Attach to the interactive conversational fleet supervisor session."""
    session_name = "cao-supervisor"
    # Check if session exists
    try:
        check = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
        if check.returncode == 0:
            os.execvp("tmux", ["tmux", "attach", "-t", session_name])
        else:
            print(f"Session '{session_name}' is not currently running.")
            print("Launching new interactive supervisor via 'crew run'...")
            return forward_to_script("cao-run", [])
    except Exception as exc:
        print(f"Error attaching to session: {exc}", file=sys.stderr)
        return 1


def print_help():
    help_text = """
🛸 cao-crew (`crew`) — The Autonomous AI Engineering Fleet CLI

The entire fleet compressed into 3 primary autonomous actions:

1. THE FLEET OVERVIEW & INTERACTIVE TECH LEAD:
   crew                     Attach to live supervisor in tmux (or show fleet status)
   crew fleet               Inspect workstation projects, spend & provider quotas

2. AUTONOMOUS HEADLESS EXECUTION (SANDBOX + SELF-HEALING):
   crew "<goal>"            Autonomously plan, isolate in sandbox, build, and verify
   crew auto "<goal>"       (Explicit headless DAG alias)

3. 5-VECTOR FULL-STACK QA-UIX + IMMEDIATE AUTO-REPAIR:
   crew test <url|path>     Playwright UI/UX audit + IMMEDIATE closed-loop auto-repair
   crew test --audit-only   Audit only (skips repair sandbox)

Lifecycle & Management:
   crew harness <cmd>       Kernel-secured Linux Landlock sandbox execution & secret stripping
   crew stop                Cleanly terminate background workers, panes and daemon
   crew doctor              Pre-flight diagnostics and configuration wizard
   crew evolve <worker>     Protected prompt self-evolution loop

Examples:
   crew                     # Attach to supervisor pane or view fleet dashboard
   crew "Add auth tokens"   # Headless autonomous task execution
   crew test http://127.0.0.1:3000   # QA crawl + instant repair of any defect found
   crew stop                # Clean shutdown of all background sessions
"""
    print(help_text.strip())


def main():
    args = sys.argv[1:]
    if not args:
        # Check if supervisor session exists; if so, attach; otherwise show unified status
        try:
            check = subprocess.run(["tmux", "has-session", "-t", "cao-supervisor"], capture_output=True)
            if check.returncode == 0:
                print("🛸 Attaching to active fleet supervisor session (cao-supervisor)...")
                os.execvp("tmux", ["tmux", "attach", "-t", "cao-supervisor"])
            else:
                sys.exit(show_unified_status([]))
        except Exception:
            sys.exit(show_unified_status([]))

    if args[0] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    cmd = args[0]
    rest = args[1:]

    # Command Router
    if cmd == "status":
        sys.exit(show_unified_status(rest))

    elif cmd == "fleet":
        sys.exit(forward_to_script("cao-fleet", rest))

    elif cmd == "run":
        sys.exit(forward_to_script("cao-run", rest))

    elif cmd == "auto":
        sys.exit(forward_to_script("cao-auto", rest))

    elif cmd == "stop":
        sys.exit(forward_to_script("cao-stop", rest))

    elif cmd in ("test", "qa"):
        sys.exit(forward_to_script("cao-qa", rest))

    elif cmd in ("repair", "fix"):
        sys.exit(forward_to_script("cao-repair", rest))

    elif cmd in ("harness", "jail"):
        sys.exit(forward_to_script("gambit-harness", rest))

    elif cmd == "sandbox":
        sys.exit(forward_to_script("cao-sandbox", rest))

    elif cmd == "evolve":
        sys.exit(forward_to_script("cao-evolve", rest))

    elif cmd == "memory":
        sys.exit(forward_to_script("cao-memory", rest))

    elif cmd in ("doctor", "check"):
        if "--init" in rest or "-i" in rest:
            rest.remove("--init") if "--init" in rest else rest.remove("-i")
            sys.exit(forward_to_script("cao-init", rest))
        elif "--update" in rest or "-u" in rest:
            rest.remove("--update") if "--update" in rest else rest.remove("-u")
            sys.exit(forward_to_script("cao-update", rest))
        else:
            sys.exit(forward_to_script("cao-doctor", rest))

    elif cmd == "init":
        sys.exit(forward_to_script("cao-init", rest))

    elif cmd == "update":
        sys.exit(forward_to_script("cao-update", rest))

    elif cmd in ("terminal", "attach", "chat"):
        sys.exit(attach_terminal())

    else:
        # If the argument is not a known command verb, treat as an autonomous goal string
        full_goal = " ".join(args)
        print(f"🛸 Routing autonomous goal to headless DAG pipeline: \"{full_goal}\"")
        sys.exit(forward_to_script("cao-auto", [full_goal]))


if __name__ == "__main__":
    main()
