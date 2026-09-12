from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aor_cli.cli import main
from aor_cli.gather.extract import stub_extract
from aor_cli.gather.writer import TEMPLATE_ROOT, write_surveydesk_specs


REQS = """
Build a product called SurveyDesk: local-first surveys.
Operators use native mobile apps; respondents answer anonymously on the web.
Store data in local SQLite via an HTTP API. Instant results. English UI.
"""

GENERIC = """
Build a product called WidgetBoard for local inventory on one laptop.
Operators track stock counts through a local HTTP API.
"""

REFERENCE_FILES = [
    "specs/requirements/SD-001-product-surfaces.md",
    "specs/requirements/SD-012-acceptance.md",
    "specs/domain/form-spec.md",
    "specs/domain/survey.md",
    "specs/api/openapi.yaml",
    "specs/adr/ADR-001-monorepo.md",
    "specs/adr/ADR-009-android-build-speed.md",
    "specs/acceptance/lifecycle.feature",
    "specs/regeneration/prompts/REGENERATE.md",
    "specs/regeneration/prompts/parallel/P1-api.md",
    "specs/regeneration/prompts/parallel/P6-tests.md",
    "specs/regeneration/contracts/theme.css.txt",
]


def test_template_pack_is_complete() -> None:
    specs = TEMPLATE_ROOT / "specs"
    assert specs.is_dir()
    for rel in REFERENCE_FILES:
        assert (TEMPLATE_ROOT / rel).is_file(), rel


def test_stub_extract_and_writer(tmp_path: Path) -> None:
    outline = stub_extract(REQS)
    assert outline.product_name == "SurveyDesk"
    assert [r.id for r in outline.requirements] == [f"SD-{i:03d}" for i in range(1, 13)]
    assert outline.requirements[0].title == "Product surfaces"
    assert outline.domains[0].name == "survey"
    assert any(d.name == "form-spec" for d in outline.domains)
    written = write_surveydesk_specs(tmp_path, outline, force=True)
    rels = {str(p.relative_to(tmp_path)) for p in written}
    for rel in REFERENCE_FILES:
        assert rel in rels
    assert "AGENTS.md" in rels
    assert "specs/regeneration/source-requirements.md" in rels
    vision = (tmp_path / "specs" / "product" / "vision.md").read_text(encoding="utf-8")
    assert "SurveyDesk" in vision
    openapi = (tmp_path / "specs" / "api" / "openapi.yaml").read_text(encoding="utf-8")
    assert "/v1/surveys" in openapi
    assert (tmp_path / ".aor").exists() is False  # writer does not create outline


def test_reference_pack_force_replaces_stub_files(tmp_path: Path) -> None:
    stale = tmp_path / "specs" / "requirements" / "SD-001-build-a-product-called-surveydesk-a.md"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale stub\n", encoding="utf-8")
    write_surveydesk_specs(tmp_path, stub_extract(REQS), force=True)
    assert not stale.exists()
    assert (tmp_path / "specs" / "requirements" / "SD-001-product-surfaces.md").is_file()


def test_generic_product_does_not_copy_surveydesk_files(tmp_path: Path) -> None:
    outline = stub_extract(GENERIC)
    assert outline.product_name == "WidgetBoard"
    assert outline.requirements[0].title != "Product surfaces"
    write_surveydesk_specs(tmp_path, outline, force=True)
    assert not (tmp_path / "specs" / "requirements" / "SD-001-product-surfaces.md").exists()
    assert not (tmp_path / "specs" / "regeneration" / "prompts" / "parallel" / "P1-api.md").exists()
    assert (tmp_path / "specs" / "product" / "vision.md").is_file()
    assert "WidgetBoard" in (tmp_path / "specs" / "product" / "vision.md").read_text(encoding="utf-8")


def test_gather_run_stub_with_confirm(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["gather", "run", "--stub", "--yes", "--root", str(tmp_path), REQS],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "specs" / "product" / "vision.md").is_file()
    assert (tmp_path / "specs" / "requirements" / "SD-001-product-surfaces.md").is_file()
    outline = tmp_path / ".aor" / "gather" / "outline.json"
    assert outline.is_file()
    data = json.loads(outline.read_text(encoding="utf-8"))
    assert data["product_name"] == "SurveyDesk"
    assert data["requirements"][0]["title"] == "Product surfaces"


def test_gather_run_outline_only_does_not_write_specs(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "gather",
            "run",
            "--stub",
            "--outline-only",
            "--json",
            "--root",
            str(tmp_path),
            REQS,
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    outline = tmp_path / ".aor" / "gather" / "outline.json"
    assert outline.is_file()
    assert not (tmp_path / "specs" / "product" / "vision.md").exists()
    data = json.loads(result.output)
    assert data["product_name"] == "SurveyDesk"
    assert data["requirements"][0]["title"] == "Product surfaces"


def test_gather_apply_surveydesk_writes_reference_pack(tmp_path: Path) -> None:
    outline = stub_extract(REQS)
    path = tmp_path / ".aor" / "gather" / "outline.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(outline.to_dict()), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["gather", "apply", "--yes", "--force", "--root", str(tmp_path)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "specs" / "requirements" / "SD-001-product-surfaces.md").is_file()
    assert (tmp_path / "specs" / "regeneration" / "prompts" / "parallel" / "P1-api.md").is_file()


def test_gather_apply_after_edit(tmp_path: Path) -> None:
    outline = stub_extract(GENERIC)
    outline.product_name = "EditedDesk"
    path = tmp_path / ".aor" / "gather" / "outline.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(outline.to_dict()), encoding="utf-8")
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["gather", "apply", "--yes", "--force", "--root", str(tmp_path)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    brand = (tmp_path / "specs" / "product" / "brand.md").read_text(encoding="utf-8")
    assert "EditedDesk" in brand
    assert not (tmp_path / "specs" / "requirements" / "SD-001-product-surfaces.md").exists()
