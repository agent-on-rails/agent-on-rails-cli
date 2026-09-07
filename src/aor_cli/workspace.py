"""Locate an Agent On Rails project (control-plane contract on disk)."""

from __future__ import annotations

from pathlib import Path

MARKERS = ("AGENTS.md", "specs", "product")
AOR_DIRNAME = ".aor"


def find_control_plane(start: Path) -> Path | None:
    """Walk *start* and parents for a control-plane contract."""
    current = start.resolve()
    candidates = [current, *current.parents]
    for path in candidates:
        if (path / "AGENTS.md").is_file() and (path / "specs").is_dir() and (path / "product").is_dir():
            return path
    return None


def require_control_plane(start: Path) -> Path:
    found = find_control_plane(start)
    if found is None:
        raise SystemExit(
            "No Agent On Rails project found. Run `aor init` in an empty directory, "
            "or `cd` into a project that already has AGENTS.md, product/, and specs/."
        )
    return found


def aor_dir(root: Path) -> Path:
    path = root / AOR_DIRNAME
    path.mkdir(parents=True, exist_ok=True)
    return path
