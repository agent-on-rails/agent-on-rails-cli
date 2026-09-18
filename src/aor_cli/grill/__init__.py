"""aor_cli.grill — Discovery AI Team (AOR-011)."""

from aor_cli.grill.personas import list_templates
from aor_cli.grill.session import GrillSession, load_session, save_session
from aor_cli.grill.stages import (
    GrillError,
    approve_architecture,
    approve_prd,
    approve_specs,
    emit_control_plane,
    request_architecture_change,
    request_prd_change,
    start_prd_stage,
)

__all__ = [
    "GrillError",
    "GrillSession",
    "approve_architecture",
    "approve_prd",
    "approve_specs",
    "emit_control_plane",
    "list_templates",
    "load_session",
    "request_architecture_change",
    "request_prd_change",
    "save_session",
    "start_prd_stage",
]
