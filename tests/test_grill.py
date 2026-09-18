from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from aor_cli.cli import main
from aor_cli.grill.approval import load_approval, sha256_file
from aor_cli.grill.session import load_session
from aor_cli.grill.stages import GrillError, mark_discovery_complete, request_architecture_change


BRIEF = """
Product name: **WidgetBoard**

Build WidgetBoard for local inventory on one laptop.
Operators track stock through a local HTTP API.
Payments are out of scope for v1.
"""


def _run_to_specs_gate(tmp_path: Path, runner: CliRunner | None = None) -> CliRunner:
    runner = runner or CliRunner()
    assert (
        runner.invoke(
            main, ["grill", "run", "--stub", "--root", str(tmp_path), BRIEF], catch_exceptions=False
        ).exit_code
        == 0
    )
    assert (
        runner.invoke(
            main,
            ["grill", "approve", "prd", "--actor", "tester", "--root", str(tmp_path)],
            catch_exceptions=False,
        ).exit_code
        == 0
    )
    assert (
        runner.invoke(
            main,
            ["grill", "approve", "architecture", "--actor", "tester", "--root", str(tmp_path)],
            catch_exceptions=False,
        ).exit_code
        == 0
    )
    return runner


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
        ["grill", "approve", "prd", "--actor", "iman", "--root", str(tmp_path)],
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
        ["grill", "approve", "architecture", "--actor", "iman", "--root", str(tmp_path)],
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


def test_request_prd_change_preserves_human_edits(tmp_path: Path) -> None:
    runner = CliRunner()
    runner.invoke(main, ["grill", "run", "--stub", "--root", str(tmp_path), BRIEF], catch_exceptions=False)
    prd = tmp_path / "product" / "prd.md"
    marker = "HUMAN_EDIT_KEEP_ME_UNIQUE_12345"
    prd.write_text(prd.read_text(encoding="utf-8") + f"\n\n## Human note\n\n{marker}\n", encoding="utf-8")
    runner.invoke(
        main,
        ["grill", "approve", "prd", "--actor", "tester", "--root", str(tmp_path)],
        catch_exceptions=False,
    )
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
    body = prd.read_text(encoding="utf-8")
    assert marker in body
    assert "DRAFT" in body
    assert "missing multi-warehouse scope" in body


def test_request_architecture_change_preserves_human_edits(tmp_path: Path) -> None:
    runner = _run_to_specs_gate(tmp_path)
    arch = tmp_path / "ARCHITECTURE.md"
    marker = "HUMAN_ARCH_EDIT_KEEP_98765"
    arch.write_text(arch.read_text(encoding="utf-8") + f"\n\n## Human note\n\n{marker}\n", encoding="utf-8")
    session = load_session(tmp_path)
    session = request_architecture_change(tmp_path, session, "need edge deploy")
    assert session.stage == "GATE_ARCHITECTURE_APPROVE"
    assert session.architecture_approved is False
    assert session.prd_approved is True
    body = arch.read_text(encoding="utf-8")
    assert marker in body
    assert "DRAFT" in body
    assert "need edge deploy" in body


def test_approval_evidence_has_actor_timestamp_sha(tmp_path: Path) -> None:
    _run_to_specs_gate(tmp_path)
    session = load_session(tmp_path)
    prd_ev = load_approval(tmp_path, session, "prd")
    arch_ev = load_approval(tmp_path, session, "architecture")
    assert prd_ev is not None
    assert arch_ev is not None
    assert prd_ev["actor"] == "tester"
    assert arch_ev["actor"] == "tester"
    assert prd_ev["timestamp"]
    assert arch_ev["timestamp"]
    assert len(prd_ev["artifact_sha256"]) == 64
    assert prd_ev["artifact_sha256"] == sha256_file(tmp_path / "product" / "prd.md")
    assert arch_ev["artifact_sha256"] == sha256_file(tmp_path / "ARCHITECTURE.md")
    # evidence files on disk
    assert (tmp_path / ".aor" / "grill" / session.session_id / "approvals" / "prd.json").is_file()


def test_complete_requires_specs_approved(tmp_path: Path) -> None:
    runner = _run_to_specs_gate(tmp_path)
    session = load_session(tmp_path)
    assert session.stage == "GATE_SPECS_APPROVE"
    try:
        mark_discovery_complete(tmp_path, session)
        raise AssertionError("expected GrillError")
    except GrillError as exc:
        assert "APPROVED" in str(exc) or "approve specs" in str(exc)

    r_fail = runner.invoke(
        main, ["grill", "complete", "--root", str(tmp_path)], catch_exceptions=False
    )
    assert r_fail.exit_code != 0

    r_ok = runner.invoke(
        main,
        ["grill", "approve", "specs", "--actor", "tester", "--root", str(tmp_path)],
        catch_exceptions=False,
    )
    assert r_ok.exit_code == 0, r_ok.output
    session = load_session(tmp_path)
    specs_ev = load_approval(tmp_path, session, "specs")
    assert specs_ev is not None
    assert specs_ev["actor"] == "tester"
    assert specs_ev["artifact_kind"] == "tree"

    r_complete = runner.invoke(
        main, ["grill", "complete", "--root", str(tmp_path)], catch_exceptions=False
    )
    assert r_complete.exit_code == 0, r_complete.output
    session = load_session(tmp_path)
    assert session.stage == "DISCOVERY_COMPLETE"


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
