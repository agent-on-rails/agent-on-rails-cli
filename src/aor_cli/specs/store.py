"""Read and write spec bundles under specs/<PREFIX>-NNN-slug/."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aor_cli.specs.frontmatter import dump_frontmatter, split_frontmatter

SPEC_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]{3}$")
DIR_RE = re.compile(r"^([A-Z][A-Z0-9]*-[0-9]{3})(?:-(.+))?$")

IMPLEMENTABLE = frozenset(
    {
        "approved",
        "planned",
        "ready",
        "in_progress",
        "verifying",
        "final_review",
        "retry",
        "escalate",
    }
)


@dataclass(frozen=True)
class SpecRecord:
    id: str
    title: str
    status: str
    intent: str
    path: Path
    frontmatter: dict[str, Any]
    repositories: list[str]

    @property
    def implementable(self) -> bool:
        return self.status.lower() in IMPLEMENTABLE


def list_specs(root: Path) -> list[SpecRecord]:
    specs_dir = root / "specs"
    if not specs_dir.is_dir():
        return []
    records: list[SpecRecord] = []
    for child in sorted(specs_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        spec_md = child / "spec.md"
        if not spec_md.is_file():
            continue
        parsed = _parse_spec_file(spec_md)
        if parsed is not None:
            records.append(parsed)
    return records


def get_spec(root: Path, spec_id: str) -> SpecRecord | None:
    wanted = spec_id.strip().upper()
    for record in list_specs(root):
        if record.id.upper() == wanted:
            return record
    return None


def create_spec(
    root: Path,
    *,
    title: str,
    prefix: str,
    repositories: list[str],
    intent: str | None = None,
) -> SpecRecord:
    prefix = prefix.upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9]*", prefix):
        raise ValueError(f"invalid spec prefix: {prefix}")
    next_id = _next_spec_id(root, prefix)
    slug = _slugify(title)
    bundle = root / "specs" / f"{next_id}-{slug}"
    bundle.mkdir(parents=True, exist_ok=False)

    intent_text = intent or f"{title} — draft contract (replace with the real intent)."
    repos = repositories or ["app"]
    frontmatter: dict[str, Any] = {
        "id": next_id,
        "title": title,
        "status": "draft",
        "intent": intent_text,
        "implementation": {"repositories": repos},
        "verification": {"tests": ["unit"]},
        "evidence_required": ["implementation-pr", "test-results", "execution-log"],
    }
    spec_body = (
        f"# {next_id} — {title}\n\n"
        "## Summary\n\n"
        f"{intent_text}\n\n"
        "## Behavior\n\n"
        "1. Describe the required behavior.\n"
        "2. Name the sibling repository that may change.\n\n"
        "## Out of scope\n\n"
        "- Work not covered by this contract\n"
    )
    (bundle / "spec.md").write_text(dump_frontmatter(frontmatter, spec_body), encoding="utf-8")
    (bundle / "acceptance.md").write_text(
        f"# Acceptance — {next_id} {title}\n\n"
        "- [ ] Happy path is described and testable\n"
        "- [ ] Failure / blocked path is described\n"
        "- [ ] No production application code is written into the control-plane repository\n",
        encoding="utf-8",
    )
    (bundle / "evidence.md").write_text(
        f"# Evidence — {next_id} {title}\n\n"
        "## Required\n\n"
        "| Artifact | Description |\n"
        "| --- | --- |\n"
        "| `implementation-pr` | PR in the named implementation repository |\n"
        "| `test-results` | Unit (and other listed) test results |\n"
        "| `execution-log` | Log of the Agent On Rails run |\n\n"
        "## Done when\n\n"
        "Evidence exists, independent review has passed, and a human has completed final review.\n",
        encoding="utf-8",
    )
    record = get_spec(root, next_id)
    if record is None:
        raise RuntimeError(f"failed to read newly created spec {next_id}")
    return record


def approve_spec(root: Path, spec_id: str) -> SpecRecord:
    record = get_spec(root, spec_id)
    if record is None:
        raise FileNotFoundError(f"spec not found: {spec_id}")
    status = record.status.lower()
    if status not in {"draft", "review"}:
        raise ValueError(f"{record.id} cannot be approved from status {record.status}")
    return set_spec_status(root, record.id, "approved")


def set_spec_status(root: Path, spec_id: str, status: str) -> SpecRecord:
    record = get_spec(root, spec_id)
    if record is None:
        raise FileNotFoundError(f"spec not found: {spec_id}")
    data = dict(record.frontmatter)
    data["status"] = status.lower()
    text = record.path.read_text(encoding="utf-8")
    _, body = split_frontmatter(text)
    record.path.write_text(dump_frontmatter(data, body), encoding="utf-8")
    updated = get_spec(root, spec_id)
    if updated is None:
        raise RuntimeError(f"failed to re-read spec {spec_id}")
    return updated


def _parse_spec_file(path: Path) -> SpecRecord | None:
    text = path.read_text(encoding="utf-8")
    data, _body = split_frontmatter(text)
    spec_id = str(data.get("id") or "").strip().upper()
    if not spec_id:
        match = DIR_RE.match(path.parent.name)
        spec_id = match.group(1) if match else ""
    if not spec_id or not SPEC_ID_RE.match(spec_id):
        return None
    impl = data.get("implementation") or {}
    repos = []
    if isinstance(impl, dict):
        raw_repos = impl.get("repositories") or []
        if isinstance(raw_repos, list):
            repos = [str(r) for r in raw_repos]
    return SpecRecord(
        id=spec_id,
        title=str(data.get("title") or path.parent.name),
        status=str(data.get("status") or "draft").lower(),
        intent=str(data.get("intent") or "").strip(),
        path=path,
        frontmatter=data,
        repositories=repos,
    )


def _next_spec_id(root: Path, prefix: str) -> str:
    used = [s.id for s in list_specs(root) if s.id.startswith(f"{prefix}-")]
    numbers = []
    for spec_id in used:
        _, _, num = spec_id.partition("-")
        if num.isdigit():
            numbers.append(int(num))
    nxt = (max(numbers) + 1) if numbers else 1
    return f"{prefix}-{nxt:03d}"


def _slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "spec"
