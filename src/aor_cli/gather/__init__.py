"""Natural-language → SurveyDesk-shaped specs (AOR-010)."""

from aor_cli.gather.extract import extract_outline, stub_extract
from aor_cli.gather.models import SpecOutline
from aor_cli.gather.writer import write_surveydesk_specs

__all__ = [
    "SpecOutline",
    "extract_outline",
    "stub_extract",
    "write_surveydesk_specs",
]
