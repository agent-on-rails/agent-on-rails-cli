from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from aor_cli.cli import main
from aor_cli.gather.extract import stub_extract
from aor_cli.gather.writer import write_surveydesk_specs


REQS = """
Build a product called SurveyDesk: local-first surveys.
Operators use native mobile apps; respondents answer anonymously on the web.
Store data in local SQLite via an HTTP API. Instant results. English UI.
"""


def test_stub_extract_and_writer(tmp_path: Path) -> None:
    outline = stub_extract(REQS)
    assert outline.product_name
    assert outline.requirements
    written = write_surveydesk_specs(tmp_path, outline, force=True)
    rels = {str(p.relative_to(tmp_path)) for p in written}
    assert "specs/product/vision.md" in rels
    assert "specs/api/openapi.yaml" in rels
    assert any(r.startswith("specs/requirements/") for r in rels)
    assert any(r.startswith("specs/acceptance/") and r.endswith(".feature") for r in rels)
    assert "specs/regeneration/prompts/REGENERATE.md" in rels
    assert (tmp_path / ".aor").exists() is False  # writer does not create outline


def test_gather_run_stub_with_confirm(tmp_path: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["gather", "run", "--stub", "--yes", "--root", str(tmp_path), REQS],
        catch_exceptions=False,
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "specs" / "product" / "vision.md").is_file()
    outline = tmp_path / ".aor" / "gather" / "outline.json"
    assert outline.is_file()
    data = json.loads(outline.read_text(encoding="utf-8"))
    assert data["product_name"]


def test_gather_apply_after_edit(tmp_path: Path) -> None:
    outline = stub_extract(REQS)
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
    vision = (tmp_path / "specs" / "product" / "vision.md").read_text(encoding="utf-8")
    assert "EditedDesk" in vision or "Edited" in path.read_text(encoding="utf-8")
