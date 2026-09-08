from __future__ import annotations

import asyncio
from pathlib import Path

from click.testing import CliRunner

from aor_cli.bootstrap.layout import scaffold_control_plane
from aor_cli.cli import main
from aor_cli.project import ProjectMeta
from aor_cli.tui.actions import human_approve, new_spec, plan_and_message, run_and_message, snapshot
from aor_cli.tui.app import AorApp


def test_bare_aor_non_tty_prints_help() -> None:
    result = CliRunner().invoke(main, [])
    assert result.exit_code == 0
    assert "tui" in result.output.lower()
    assert "Agent On Rails" in result.output


def test_tui_help() -> None:
    result = CliRunner().invoke(main, ["tui", "--help"])
    assert result.exit_code == 0
    assert "terminal UI" in result.output.lower() or "mouse" in result.output.lower()


def test_snapshot_and_actions(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    scaffold_control_plane(root, "Demo")
    ProjectMeta.from_name("Demo").save(root)
    data = snapshot(root)
    assert data["root"] == root
    ok, msg = new_spec(root, "Checkout totals", "demo-app")
    assert ok, msg
    assert "DEMO-001" in msg
    blocked, _ = plan_and_message(root, "DEMO-001")
    assert not blocked
    ok, _ = human_approve(root, "DEMO-001")
    assert ok
    ok, msg = run_and_message(root, "DEMO-001")
    assert ok, msg
    assert "Packaged" in msg
    snap = snapshot(root)
    assert any(s.id == "DEMO-001" for s in snap["specs"])
    assert snap["tasks"]


def test_tui_composes(tmp_path: Path) -> None:
    root = tmp_path / "demo"
    scaffold_control_plane(root, "Demo")
    ProjectMeta.from_name("Demo").save(root)
    new_spec(root, "Checkout totals", "demo-app")

    async def _run() -> None:
        app = AorApp(start=root)
        async with app.run_test() as pilot:
            await pilot.pause()
            specs = app.query_one("#specs")
            assert specs.row_count == 1
            log = str(app.query_one("#log").lines)
            assert "harness" in log.lower() or "Agent On Rails" in log
            await pilot.press("q")

    asyncio.run(_run())
