from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from aor_cli.cli import main
from aor_cli.specs.store import get_spec, set_spec_status
from aor_cli.tasks.store import list_tasks


def _runner() -> CliRunner:
    return CliRunner()


def _init(tmp_path: Path) -> Path:
    root = tmp_path / "demo"
    result = _runner().invoke(main, ["init", str(root), "--name", "Demo"])
    assert result.exit_code == 0, result.output
    return root


def test_init_and_status(tmp_path: Path) -> None:
    root = _init(tmp_path)
    assert (root / "AGENTS.md").is_file()
    assert (root / "product" / "proposition.md").is_file()
    assert (root / ".aor" / "project.yaml").is_file()
    result = _runner().invoke(main, ["status", "--path", str(root)])
    assert result.exit_code == 0, result.output
    assert "prefix: DEMO" in (root / ".aor" / "project.yaml").read_text(encoding="utf-8")


def test_guide_names_the_product() -> None:
    result = _runner().invoke(main, ["guide"])
    assert result.exit_code == 0, result.output
    assert "Agent On Rails" in result.output
    assert "aor spec approve" in result.output


def test_spec_new_plan_blocked_until_approved(tmp_path: Path) -> None:
    root = _init(tmp_path)
    created = _runner().invoke(
        main,
        ["spec", "new", "Checkout totals", "--path", str(root), "--repo", "demo-app"],
    )
    assert created.exit_code == 0, created.output
    assert "DEMO-001" in created.output

    spec = get_spec(root, "DEMO-001")
    assert spec is not None
    assert spec.status == "draft"
    assert (spec.path.parent / "acceptance.md").is_file()

    blocked = _runner().invoke(main, ["plan", "DEMO-001", "--path", str(root)])
    assert blocked.exit_code == 2
    assert "Blocked" in blocked.output

    run_blocked = _runner().invoke(main, ["run", "DEMO-001", "--path", str(root)])
    assert run_blocked.exit_code == 2
    assert "approve" in run_blocked.output.lower()


def test_approve_plan_run_review(tmp_path: Path) -> None:
    root = _init(tmp_path)
    _runner().invoke(main, ["spec", "new", "Checkout totals", "--path", str(root), "--repo", "demo-app"])

    approved = _runner().invoke(main, ["spec", "approve", "DEMO-001", "--path", str(root)])
    assert approved.exit_code == 0, approved.output
    assert get_spec(root, "DEMO-001").status == "approved"  # type: ignore[union-attr]

    planned = _runner().invoke(main, ["plan", "DEMO-001", "--path", str(root)])
    assert planned.exit_code == 0, planned.output
    tasks = list_tasks(root)
    assert len(tasks) == 1
    assert tasks[0].id == "TASK-001"
    assert get_spec(root, "DEMO-001").status == "ready"  # type: ignore[union-attr]

    ran = _runner().invoke(main, ["run", "DEMO-001", "--path", str(root)])
    assert ran.exit_code == 0, ran.output
    context = root / ".aor" / "packages" / "TASK-001" / "CONTEXT.md"
    assert context.is_file()
    text = context.read_text(encoding="utf-8")
    assert "DEMO-001" in text
    assert "CURRENT TASK" in text
    assert list_tasks(root)[0].status == "running"

    reviewed = _runner().invoke(
        main,
        ["review", "TASK-001", "--path", str(root), "--approve", "--notes", "ok"],
    )
    assert reviewed.exit_code == 0, reviewed.output
    assert (root / ".aor" / "reviews" / "TASK-001.json").is_file()
    assert get_spec(root, "DEMO-001").status == "final_review"  # type: ignore[union-attr]
    assert list_tasks(root)[0].status == "done"


def test_cannot_approve_from_ready(tmp_path: Path) -> None:
    root = _init(tmp_path)
    _runner().invoke(main, ["spec", "new", "Thing", "--path", str(root)])
    set_spec_status(root, "DEMO-001", "ready")
    result = _runner().invoke(main, ["spec", "approve", "DEMO-001", "--path", str(root)])
    assert result.exit_code == 2
