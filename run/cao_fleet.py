"""cao_fleet.py — Fleet Conductor Core for Workstation Projects.

Orchestrates multi-repo visibility, intelligent Laya routing, and task dispatching
across projects on this workstation (llmaas, 3DAang, nowait-study, dycom-demo, cao-crew, etc.).
"""
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
if str(HERE) not in os.sys.path:
    os.sys.path.insert(0, str(HERE))

from cao_laya_router import LayaRouter
from cao_lib import resolve_workspace_dir

# Projects are registered per machine in ~/.cao/fleet_projects.json.
DEFAULT_PROJECTS: Dict[str, Path] = {}


def get_fleet_config_path() -> Path:
    cao_home = Path.home() / ".cao"
    cao_home.mkdir(parents=True, exist_ok=True)
    return cao_home / "fleet_projects.json"


def load_fleet_registry() -> Dict[str, str]:
    cfg = get_fleet_config_path()
    registry: Dict[str, str] = {k: str(v) for k, v in DEFAULT_PROJECTS.items()}
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                registry.update({k: str(v) for k, v in data.items()})
        except Exception:
            pass
    return registry


def save_fleet_registry(registry: Dict[str, str]) -> None:
    cfg = get_fleet_config_path()
    cfg.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


class FleetConductor:
    """Master Meta-Agent Orchestrator for the Workstation Fleet."""

    def __init__(self, registry: Optional[Dict[str, str]] = None):
        self.registry = registry or load_fleet_registry()

    def list_projects(self) -> List[Dict[str, Any]]:
        """Inspect and return health/status information for all fleet projects."""
        results = []
        tmux_sessions = self._get_tmux_sessions()

        for name, path_str in sorted(self.registry.items()):
            p = Path(path_str)
            exists = p.exists() and p.is_dir()
            info: Dict[str, Any] = {
                "name": name,
                "path": str(p),
                "exists": exists,
                "git": {},
                "supervisor": "none",
                "active_task": "None",
                "tasks_progress": "0/0",
                "status": "idle",
            }

            if not exists:
                info["status"] = "missing"
                results.append(info)
                continue

            # 1. Inspect Git
            info["git"] = self._inspect_git(p)

            # 2. Inspect Supervisor / tmux sessions
            info["supervisor"], info["session_name"] = self._inspect_supervisor(name, p, tmux_sessions)

            # 3. Inspect Tasks / Plans
            tasks_info = self._inspect_tasks_and_plan(p)
            info["tasks_progress"] = tasks_info["progress"]
            info["active_task"] = tasks_info["active_task"]
            info["tasks_total"] = tasks_info["total"]
            info["tasks_done"] = tasks_info["done"]

            if info["supervisor"] != "none":
                info["status"] = "running"
            elif tasks_info["total"] > 0 and tasks_info["done"] < tasks_info["total"]:
                info["status"] = "detached"
            elif tasks_info["total"] > 0 and tasks_info["done"] == tasks_info["total"]:
                info["status"] = "completed"
            else:
                info["status"] = "idle"

            results.append(info)

        return results

    def inspect_project(self, project_name_or_path: str) -> Dict[str, Any]:
        """Deep inspection of a specific fleet project."""
        target_path = self._resolve_project_path(project_name_or_path)
        if not target_path or not target_path.exists():
            raise FileNotFoundError(f"Project '{project_name_or_path}' not found.")

        name = self._resolve_project_name(target_path)
        tmux_sessions = self._get_tmux_sessions()

        info: Dict[str, Any] = {
            "name": name,
            "path": str(target_path),
            "git": self._inspect_git(target_path, detailed=True),
            "tasks": self._inspect_tasks_and_plan(target_path, detailed=True),
        }
        info["supervisor"], info["session_name"] = self._inspect_supervisor(name, target_path, tmux_sessions)
        return info

    def dispatch_task(
        self,
        task_text: str,
        project_name_or_path: Optional[str] = None,
        preferred_engine: Optional[str] = None,
        auto_run: bool = False,
    ) -> Dict[str, Any]:
        """Intelligently route and dispatch a task into the target project's queue."""
        if not project_name_or_path:
            # Infer from current directory or default to cao-crew
            cwd = Path.cwd()
            project_name_or_path = self._resolve_project_name(cwd) or "cao-crew"

        target_path = self._resolve_project_path(project_name_or_path)
        if not target_path or not target_path.exists():
            raise FileNotFoundError(f"Cannot dispatch task: project '{project_name_or_path}' directory not found.")

        project_name = self._resolve_project_name(target_path)

        # 1. Laya Route to select optimal worker profile & model
        laya_decision = LayaRouter.route_task(task_text, project_context=f"Project: {project_name}")
        worker = preferred_engine or laya_decision["worker"]
        model = laya_decision["model"]

        # 2. Append/Enqueue task in target project's now.md or tasks.json
        wcao_dir = resolve_workspace_dir(target_path, create=True, auto_patch=True)
        plans_dir = wcao_dir / "plans"
        now_md = plans_dir / "now.md"
        plans_dir.mkdir(parents=True, exist_ok=True)

        # Append to now.md task queue if exists
        task_entry = f"- [ ] **[{worker}]** {task_text} *(Model: {model})*"
        if now_md.exists():
            content = now_md.read_text(encoding="utf-8")
            if "## 🔥 Prioritized Task Queue" in content:
                content = content.replace(
                    "## 🔥 Prioritized Task Queue",
                    f"## 🔥 Prioritized Task Queue\n\n{task_entry}",
                )
            else:
                content += f"\n\n## 🔥 Prioritized Task Queue\n\n{task_entry}\n"
            now_md.write_text(content, encoding="utf-8")
        else:
            now_md.write_text(
                f"# now.md — {project_name} active focus\n\n## 🔥 Prioritized Task Queue\n\n{task_entry}\n",
                encoding="utf-8",
            )

        # Append to session tasks.json if an active session exists
        session_task_added = False
        sessions_dir = wcao_dir / "sessions"
        if sessions_dir.exists():
            sessions = sorted([d for d in sessions_dir.iterdir() if d.is_dir()], key=lambda d: d.name)
            if sessions:
                latest_session = sessions[-1]
                tasks_json = latest_session / "tasks.json"
                if tasks_json.exists():
                    try:
                        tasks = json.loads(tasks_json.read_text(encoding="utf-8"))
                        if isinstance(tasks, list):
                            new_id = f"task_{len(tasks) + 1}"
                            tasks.append({
                                "id": new_id,
                                "title": task_text,
                                "engine": worker,
                                "model": model,
                                "status": "pending",
                                "depends_on": [],
                                "detail": f"Dispatched by Fleet Conductor. Optimal model: {model}",
                            })
                            tasks_json.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
                            session_task_added = True
                    except Exception:
                        pass

        result = {
            "project": project_name,
            "path": str(target_path),
            "task": task_text,
            "routed_worker": worker,
            "routed_model": model,
            "category": laya_decision["category"],
            "confidence": laya_decision["confidence"],
            "enqueued_now_md": True,
            "enqueued_session_tasks": session_task_added,
            "auto_run_triggered": False,
        }

        # 3. Optional: Trigger background autonomous runner
        if auto_run:
            cmd = ["cao-auto", task_text]
            subprocess.Popen(
                cmd,
                cwd=str(target_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            result["auto_run_triggered"] = True

        return result

    def register_project(self, name: str, path: str) -> None:
        p = Path(path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Path does not exist: {p}")
        self.registry[name] = str(p)
        save_fleet_registry(self.registry)

    def unregister_project(self, name: str) -> bool:
        if name in self.registry:
            del self.registry[name]
            save_fleet_registry(self.registry)
            return True
        return False

    def _resolve_project_path(self, query: str) -> Optional[Path]:
        if query in self.registry:
            return Path(self.registry[query])
        # Try path directly
        p = Path(query).resolve()
        if p.exists():
            return p
        # Partial match on name
        for k, v in self.registry.items():
            if query.lower() in k.lower():
                return Path(v)
        return None

    def _resolve_project_name(self, path: Path) -> str:
        resolved = path.resolve()
        for k, v in self.registry.items():
            if Path(v).resolve() == resolved:
                return k
        return resolved.name

    def _get_tmux_sessions(self) -> List[str]:
        try:
            res = subprocess.run(
                ["tmux", "list-sessions", "-F", "#{session_name}"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if res.returncode == 0:
                return [s.strip() for s in res.stdout.splitlines() if s.strip()]
        except Exception:
            pass
        return []

    def _inspect_git(self, project_path: Path, detailed: bool = False) -> Dict[str, Any]:
        git_dir = project_path / ".git"
        if not git_dir.exists():
            return {"is_git": False}

        try:
            branch = subprocess.check_output(
                ["git", "-C", str(project_path), "rev-parse", "--abbrev-ref", "HEAD"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            commit = subprocess.check_output(
                ["git", "-C", str(project_path), "log", "-1", "--format=%h %s"],
                text=True,
                stderr=subprocess.DEVNULL,
            ).strip()
            status_out = subprocess.check_output(
                ["git", "-C", str(project_path), "status", "--porcelain"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            dirty = len(status_out.strip().splitlines()) if status_out.strip() else 0

            res: Dict[str, Any] = {
                "is_git": True,
                "branch": branch,
                "head_commit": commit,
                "dirty_files": dirty,
            }
            if detailed:
                diff_stat = subprocess.check_output(
                    ["git", "-C", str(project_path), "diff", "--stat"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                res["diff_stat"] = diff_stat.strip()
            return res
        except Exception as e:
            return {"is_git": True, "error": str(e)}

    def _inspect_supervisor(self, name: str, path: Path, tmux_sessions: List[str]) -> Tuple[str, Optional[str]]:
        # Match against running tmux sessions
        matched_session = None
        for s in tmux_sessions:
            if s == f"cao-{name}" or s == f"cao-supervisor" or name in s:
                matched_session = s
                break

        # Check hint or active supervisor
        hint_file = Path.home() / ".cao" / "supervisor.hint"
        supervisor_engine = "none"
        if matched_session:
            supervisor_engine = "active"
            if hint_file.exists():
                try:
                    supervisor_engine = hint_file.read_text(encoding="utf-8").strip() or "active"
                except Exception:
                    pass
        return supervisor_engine, matched_session

    def _inspect_tasks_and_plan(self, project_path: Path, detailed: bool = False) -> Dict[str, Any]:
        wcao = resolve_workspace_dir(project_path, create=False, auto_patch=False)
        sessions_dir = wcao / "sessions"
        total_tasks = 0
        done_tasks = 0
        active_task_title = "None"
        tasks_list = []

        if sessions_dir.exists():
            sessions = sorted([d for d in sessions_dir.iterdir() if d.is_dir()], key=lambda d: d.name)
            if sessions:
                latest = sessions[-1]
                tasks_file = latest / "tasks.json"
                if tasks_file.exists():
                    try:
                        tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
                        if isinstance(tasks, list):
                            total_tasks = len(tasks)
                            done_tasks = sum(1 for t in tasks if t.get("status") in ("done", "completed"))
                            tasks_list = tasks
                            for t in tasks:
                                if t.get("status") in ("running", "in_progress", "pending"):
                                    active_task_title = t.get("title", "Active Task")
                                    break
                    except Exception:
                        pass

        # Fallback to now.md
        now_md = wcao / "plans" / "now.md"
        plan_content = ""
        if now_md.exists():
            try:
                plan_content = now_md.read_text(encoding="utf-8")
                if total_tasks == 0:
                    checkboxes = re.findall(r"- \[( |x|X)\]", plan_content)
                    if checkboxes:
                        total_tasks = len(checkboxes)
                        done_tasks = sum(1 for c in checkboxes if c.lower() == "x")
                        # Find first unchecked
                        m = re.search(r"- \[ \] \*\*?(.*?)\*\*? (.*)", plan_content)
                        if m:
                            active_task_title = f"{m.group(1)} {m.group(2)}"[:60]
            except Exception:
                pass

        res = {
            "total": total_tasks,
            "done": done_tasks,
            "progress": f"{done_tasks}/{total_tasks}",
            "active_task": active_task_title if active_task_title != "None" else ("No active tasks" if total_tasks == 0 or done_tasks == total_tasks else "In progress"),
        }
        if detailed:
            res["plan_markdown"] = plan_content
            res["tasks_list"] = tasks_list
        return res
