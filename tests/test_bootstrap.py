from __future__ import annotations

from pathlib import Path

from aor_cli.bootstrap.layout import scaffold_control_plane, validate_control_plane


def test_scaffold_and_validate(tmp_path: Path) -> None:
    root = tmp_path / "demo-control-plane"
    written = scaffold_control_plane(root, "Demo")
    assert written
    assert not validate_control_plane(root)


def test_validate_missing(tmp_path: Path) -> None:
    root = tmp_path / "empty"
    root.mkdir()
    issues = validate_control_plane(root)
    assert any(i.path == "AGENTS.md" for i in issues)
    assert any(i.path == "product/" for i in issues)


def test_incomplete_spec_bundle(tmp_path: Path) -> None:
    root = tmp_path / "cp"
    scaffold_control_plane(root, "Demo")
    bad = root / "specs" / "DEMO-001-thing"
    bad.mkdir()
    (bad / "spec.md").write_text("# x\n", encoding="utf-8")
    issues = validate_control_plane(root)
    assert any("acceptance.md" in i.path for i in issues)


def test_surveydesk_layout_dirs_are_not_spec_bundles(tmp_path: Path) -> None:
    root = tmp_path / "cp"
    scaffold_control_plane(root, "SurveyDesk")
    for name in (
        "product",
        "requirements",
        "domain",
        "api",
        "adr",
        "acceptance",
        "regeneration",
    ):
        (root / "specs" / name).mkdir()
    assert not validate_control_plane(root)
