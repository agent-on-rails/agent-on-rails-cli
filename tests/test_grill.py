from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from aor_cli.cli import main
from aor_cli.grill.session import load_session
from aor_cli.grill.stages import GrillError, request_architecture_change


BRIEF = """
Product name: **WidgetBoard**

Build WidgetBoard for local inventory on one laptop.
Operators track stock through a local HTTP API.
Payments are out of scope for v1.
"""


def test_grill_end_to_end_stub(tmp_path: Path) -> None:
    runner = CliRunner()
    r1 = runner.invoke(
        main,
        ["grill", "run", "--stub", "--root", str(tmp_path), BRIEF],
        catch_exceptions=False,
    )
    assert r1.exit_code == 0, r1.output
    assert (tmp_path / "product" / "prd.md").is_file()
    assert not (tmp_path / "ARCHITECTURE.md").is_file()
    session = load_session(tmp_path)
    assert session.stage == "GATE_PRD_APPROVE"
    assert session.architect_questions

    r2 = runner.invoke(
        main,
        ["grill", "approve", "prd", "--root", str(tmp_path)],
        catch_exceptions=False,
    )
    assert r2.exit_code == 0, r2.output
    assert (tmp_path / "ARCHITECTURE.md").is_file()
    prd = (tmp_path / "product" / "prd.md").read_text(encoding="utf-8")
    assert "APPROVED" in prd
    session = load_session(tmp_path)
    assert session.stage == "GATE_ARCHITECTURE_APPROVE"
    assert session.prd_approved

    r3 = runner.invoke(
        main,
        ["grill", "approve", "architecture", "--root", str(tmp_path)],
        catch_exceptions=False,
    )
    assert r3.exit_code == 0, r3.output
    assert (tmp_path / "specs").is_dir()
    assert (tmp_path / "specs" / "requirements").is_dir()
    session = load_session(tmp_path)
    assert session.stage == "GATE_SPECS_APPROVE"
    assert session.architecture_approved

    r4 = runner.invoke(
        main,
        ["grill", "resume", "--root", str(tmp_path)],
        catch_exceptions=False,
    )
    assert r4.exit_code == 0, r4.output
    assert session.session_id in r4.output


def test_architect_cannot_author_before_prd_approved(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(
        main,
        ["grill", "run", "--stub", "--root", str(tmp_path), BRIEF],
        catch_exceptions=False,
    )
    session = load_session(tmp_path)
    session.stage = "STAGE_ARCHITECTURE"
    session.prd_approved = False
    try:
        from aor_cli.grill.stages import author_architecture

        author_architecture(tmp_path, session)
        raise AssertionError("expected GrillError")
    except GrillError as exc:
        assert "before PRD APPROVED" in str(exc)


def test_request_prd_change_returns_to_prd_gate(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["grill", "run", "--stub", "--root", str(tmp_path), BRIEF], catch_exceptions=False)
    runner.invoke(main, ["grill", "approve", "prd", "--root", str(tmp_path)], catch_exceptions=False)
    r = runner.invoke(
        main,
        [
            "grill",
            "request",
            "prd-change",
            "-m",
            "missing multi-warehouse scope",
            "--root",
            str(tmp_path),
        ],
        catch_exceptions=False,
    )
    assert r.exit_code == 0, r.output
    session = load_session(tmp_path)
    assert session.stage == "GATE_PRD_APPROVE"
    assert session.prd_approved is False


def test_request_architecture_change(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["grill", "run", "--stub", "--root", str(tmp_path), BRIEF], catch_exceptions=False)
    runner.invoke(main, ["grill", "approve", "prd", "--root", str(tmp_path)], catch_exceptions=False)
    runner.invoke(
        main, ["grill", "approve", "architecture", "--root", str(tmp_path)], catch_exceptions=False
    )
    session = load_session(tmp_path)
    assert session.stage == "GATE_SPECS_APPROVE"
    session = request_architecture_change(tmp_path, session, "need edge deploy")
    assert session.stage == "GATE_ARCHITECTURE_APPROVE"
    assert session.architecture_approved is False
    assert session.prd_approved is True


def test_discover_alias(tmp_path: Path) -> None:
    runner = CliRunner()
    r = runner.invoke(
        main,
        ["discover", "run", "--stub", "--root", str(tmp_path), BRIEF],
        catch_exceptions=False,
    )
    assert r.exit_code == 0, r.output
    assert (tmp_path / "product" / "prd.md").is_file()


def test_cloudflare_template(tmp_path: Path) -> None:
    runner = CliRunner()
    r = runner.invoke(
        main,
        [
            "grill",
            "run",
            "--stub",
            "--architect-template",
            "cloudflare-web-payments",
            "--root",
            str(tmp_path),
            "Product name: Store\nBuild a store with Midtrans checkout on Cloudflare.",
        ],
        catch_exceptions=False,
    )
    assert r.exit_code == 0, r.output
    session = load_session(tmp_path)
    assert session.architect_template == "cloudflare-web-payments"
    assert any("payment" in q.lower() or "webhook" in q.lower() for q in session.architect_questions)
