#!/usr/bin/env python3
"""gambit_cli.py — GAMBIT (Powered by CAO Architecture): Autonomous Multi-Agent Engineering Fleet.

Chess Taxonomy:
  ♔ Grandmaster  - You (Strategic Vision & Approvals)
  ♜ The Rook     - Master Fleet Conductor (One Terminal to Rule Them All)
  ♞ The Knights  - Project Supervisors (Stationed per repository in tmux)
  ♝ The Bishops  - Architectural & Analytical Specialists (Claude / AGY)
  ♙ The Pawns    - High-throughput Implementation Workers (OpenCode / DeepSeek)

Usage:
  gambit                          - Talk to The Rook (auto-attaches or launches)
  gambit "<goal>"                 - Natural language cross-project mission dispatch
  gambit fleet                    - Chessboard status: Knights, Bishops, Pawns & Quotas
  gambit test <url|path>          - 5-Vector QA-UIX suite + Closed-Loop Auto-Repair
  gambit run [--provider <p>]     - Launch The Rook master session in tmux
  gambit stop                     - Clean shutdown of all Knights and Daemons
  gambit doctor                   - Pre-flight diagnostic across tools & logins
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
        print(f"Error: Internal engine script not found: {script_path}", file=sys.stderr)
        return 1

    cmd = [str(script_path)] + args
    try:
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


def show_chessboard_status(args: List[str]) -> int:
    """Display the active GAMBIT Chessboard status: Knights, Bishops, Pawns, and Provider Quotas."""
    print("♜ GAMBIT — Autonomous Engineering Fleet (Powered by CAO Architecture)")
    print("═" * 88)

    # 1. Stationed Knights (Projects Overview)
    try:
        from cao_fleet import FleetConductor
        conductor = FleetConductor()
        projects = conductor.list_projects()
        print("♞ Stationed Knights (Active Projects):")
        print(f"   {'PROJECT':18s} | {'BRANCH':12s} | {'KNIGHT STATUS':14s} | {'TASKS':6s} | ACTIVE MISSION")
        print("   " + "─" * 82)
        for p in projects:
            branch = p.get("git", {}).get("branch", "detached")
            tasks_str = p.get("tasks_progress", "0/0")
            status_str = p.get("status", "idle").upper()
            active_str = (p.get("active_task") or "Standing by")[:32]
            print(f"   {p['name']:18s} | {branch:12s} | {status_str:14s} | {tasks_str:6s} | {active_str}")
    except Exception as exc:
        print(f"   Knight inspection notice: {exc}")

    print("─" * 88)

    # 2. Token & Provider Quotas (Bishops & Pawns)
    try:
        from run.cao_limits import get_limits
        lr = get_limits()
        print("⚡ Engine Quotas & Readiness (Bishops & Pawns):")
        # Claude (Bishop)
        if lr.claude:
            c_status = "BLOCKED" if lr.claude.is_blocked() else ("WARN" if lr.claude.is_near_limit() else "HEALTHY")
            windows_info = ", ".join(f"{w.name}: {w.utilization * 100:.0f}%" for w in lr.claude.windows if w.utilization is not None)
            print(f"   • ♝ Bishop Claude:   {c_status:10s} | {windows_info or 'Available'}")
        else:
            print("   • ♝ Bishop Claude:   READY      | Flat-rate subscription available")
        # Codex (Bishop)
        if lr.codex:
            cx_status = "BLOCKED" if lr.codex.is_blocked() else "READY"
            print(f"   • ♝ Bishop Codex:    {cx_status:10s} | Available")
        else:
            print("   • ♝ Bishop Codex:    READY      | Available")
        # OpenCode / DeepSeek / GLM (Pawns)
        if lr.opencode:
            cost_str = f"${lr.opencode.cost:.2f}" if lr.opencode.cost else "Free/Local"
            print(f"   • ♙ Pawns (Bulk):    READY      | Spend: {cost_str} ({lr.opencode.tokens_in + lr.opencode.tokens_out} tokens)")
        else:
            print("   • ♙ Pawns (Bulk):    READY      | Available")
    except Exception as exc:
        print(f"   Engine quota inspection notice: {exc}")

    print("─" * 88)

    # 3. The Rook Session State
    try:
        tmux_res = subprocess.run(["tmux", "list-sessions"], capture_output=True, text=True)
        sessions = [line.split(":")[0] for line in tmux_res.stdout.splitlines() if line.strip()]
        rook_active = any("supervisor" in s or "rook" in s for s in sessions)
        rook_badge = "ONLINE (attached via 'gambit')" if rook_active else "OFFLINE (launch via 'gambit run')"
        print(f"♜ The Rook (Master Conductor): {rook_badge}")
        cao_sessions = [s for s in sessions if "cao" in s or "gambit" in s or "crew" in s]
        print(f"🖥️  Active Background Panes:   {len(cao_sessions)} sessions ({', '.join(cao_sessions) or 'None'})")
    except Exception:
        print("♜ The Rook: tmux not running")

    print("═" * 88)
    print("💡 Grandmaster Orders: gambit | gambit \"<mission>\" | gambit test <url> | gambit fleet")
    return 0


def attach_or_launch_rook() -> int:
    """Connect Grandmaster directly to The Rook session."""
    session_name = "cao-supervisor"
    try:
        check = subprocess.run(["tmux", "has-session", "-t", session_name], capture_output=True)
        if check.returncode == 0:
            print("♜ Connecting Grandmaster to The Rook (Master Conductor)...")
            os.execvp("tmux", ["tmux", "attach", "-t", session_name])
        else:
            print("♜ The Rook is not currently active.")
            print("Launching new master session with pre-flight check...")
            return forward_to_script("cao-run", [])
    except Exception as exc:
        print(f"Error connecting to The Rook: {exc}", file=sys.stderr)
        return 1


def print_help():
    help_text = """
♜ GAMBIT — Autonomous Engineering Fleet (Powered by CAO Architecture)

Chess Taxonomy:
  ♔ Grandmaster  - You (Strategic Vision & Approvals)
  ♜ The Rook     - Master Fleet Conductor (One Terminal to Rule Them All)
  ♞ The Knights  - Project Supervisors (Stationed per repository)
  ♝ The Bishops  - Architectural & Analytical Specialists (Claude / AGY)
  ♙ The Pawns    - High-throughput Implementation Workers (OpenCode / DeepSeek)

Commands (both space 'gambit <cmd>' and dash 'gambit-<cmd>' supported):

1. MASTER CONDUCTOR & FLEET BOARD:
   gambit                     Talk to The Rook (attaches if active, launches if idle)
   gambit fleet               Chessboard status: Knights, Bishops, Pawns & Quotas
   gambit run [--provider P]  Launch The Rook in tmux (providers: claude, agy, codex)

2. NATURAL LANGUAGE MISSIONS:
   gambit "<mission>"         Natural language cross-project mission dispatch
   gambit auto "<goal>"       Headless DAG autonomous execution

3. FULL-STACK QA-UIX + AUTO-REPAIR:
   gambit test <url|path>     5-Vector QA-UIX crawl + Closed-Loop Auto-Repair
   gambit test --audit-only   Audit only without launching repair sandbox
   gambit test -y             Bypass safety confirmation gate

4. FLEET LIFECYCLE:
   gambit stop                Cleanly terminate all Knights, Daemons and Rook panes
   gambit doctor              Pre-flight diagnostic across tools, ports & logins
   gambit evolve <worker>     Protected prompt self-evolution loop

Examples:
   gambit                                # Enter master terminal with The Rook
   gambit "In backend add JWT, in mobile add login"  # Cross-project mission
   gambit test http://localhost:3000     # Full QA-UIX audit with safety confirmation
   gambit fleet                          # Inspect projects, spend & provider quotas
"""
    print(help_text.strip())


def main():
    prog_name = Path(sys.argv[0]).name
    if prog_name.startswith("gambit-") and prog_name != "gambit-cli":
        sub = prog_name.replace("gambit-", "")
        args = [sub] + sys.argv[1:]
    else:
        args = sys.argv[1:]

    if not args:
        # Check if The Rook is already active
        try:
            check = subprocess.run(["tmux", "has-session", "-t", "cao-supervisor"], capture_output=True)
            if check.returncode == 0:
                print("♜ Attaching to active Rook master session...")
                os.execvp("tmux", ["tmux", "attach", "-t", "cao-supervisor"])
            else:
                sys.exit(show_chessboard_status([]))
        except Exception:
            sys.exit(show_chessboard_status([]))

    first = args[0]
    rest = args[1:]

    if first in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    # Allow dash aliases if user typed gambit-fleet, gambit-test, etc.
    cmd = first.replace("gambit-", "") if first.startswith("gambit-") else first

    # Command Router
    if cmd in ("status", "fleet", "board"):
        sys.exit(show_chessboard_status(rest))

    elif cmd in ("run", "rook"):
        sys.exit(forward_to_script("cao-run", rest))

    elif cmd in ("auto", "mission"):
        sys.exit(forward_to_script("cao-auto", rest))

    elif cmd == "stop":
        sys.exit(forward_to_script("cao-stop", rest))

    elif cmd in ("test", "qa"):
        sys.exit(forward_to_script("cao-qa", rest))

    elif cmd in ("repair", "fix"):
        sys.exit(forward_to_script("cao-repair", rest))

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

    elif cmd in ("terminal", "attach", "chat"):
        sys.exit(attach_or_launch_rook())

    else:
        # Natural Language Mission: Route directly to autonomous pipeline
        full_mission = " ".join(args)
        print(f"♜ The Rook is routing mission to Knights: \"{full_mission}\"")
        sys.exit(forward_to_script("cao-auto", [full_mission]))


if __name__ == "__main__":
    main()
