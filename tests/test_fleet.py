import json
import pytest
from pathlib import Path
from run.cao_fleet import FleetConductor


def test_fleet_conductor_list_projects(tmp_path):
    p1 = tmp_path / "proj1"
    p1.mkdir()
    (p1 / "wcao" / "plans").mkdir(parents=True)
    (p1 / "wcao" / "plans" / "now.md").write_text("- [ ] **Task 1** do something\n- [x] **Task 2** done\n")

    registry = {"proj1": str(p1)}
    conductor = FleetConductor(registry=registry)
    projects = conductor.list_projects()

    assert len(projects) == 1
    assert projects[0]["name"] == "proj1"
    assert projects[0]["tasks_progress"] == "1/2"
    assert projects[0]["status"] == "detached"


def test_fleet_conductor_dispatch_task(tmp_path):
    p1 = tmp_path / "proj1"
    p1.mkdir()
    (p1 / "wcao" / "plans").mkdir(parents=True)
    (p1 / "wcao" / "plans" / "now.md").write_text("# now.md\n## 🔥 Prioritized Task Queue\n")

    registry = {"proj1": str(p1)}
    conductor = FleetConductor(registry=registry)

    res = conductor.dispatch_task(
        task_text="Refactor domain architecture boundaries",
        project_name_or_path="proj1",
    )

    assert res["project"] == "proj1"
    assert res["routed_worker"] == "claude_worker"
    assert res["enqueued_now_md"] is True

    # Verify content in now.md
    now_content = (p1 / "wcao" / "plans" / "now.md").read_text()
    assert "Refactor domain architecture boundaries" in now_content
    assert "claude_worker" in now_content


def test_fleet_conductor_register_unregister(tmp_path):
    conductor = FleetConductor(registry={})
    p = tmp_path / "custom_app"
    p.mkdir()

    conductor.register_project("custom_app", str(p))
    assert "custom_app" in conductor.registry

    ok = conductor.unregister_project("custom_app")
    assert ok is True
    assert "custom_app" not in conductor.registry
