"""Agent On Rails TUI — mouse-friendly harness (OpenCode / Claude-style)."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Log, Markdown, Static

from aor_cli import __version__
from aor_cli.tui.actions import (
    human_approve,
    init_project,
    new_spec,
    plan_and_message,
    review_and_message,
    run_and_message,
    snapshot,
)
from aor_cli.tui.screens import ConfirmModal, InitModal, NewSpecModal
from aor_cli.workspace import find_control_plane

GUIDE_MD = """\
# Agent On Rails

A **terminal harness** for coding agents — not a coding agent itself.

Docs define intent. Specs define the contract. Agents implement.
Evidence proves completion. Humans own approve + merge.

## Loop

1. **Init** — contract folder (`product/`, `specs/`, `adr/`)
2. **New spec** — `spec.md` + acceptance + evidence
3. **Approve** — human gate (agents cannot skip)
4. **Plan / Run** — bounded task + context package
5. Open `prompt.md` in Cursor, Claude, Codex, Gemini, …
6. **Review** — human final review

Click a spec, then use the buttons (mouse works) or keys below.
"""

EMPTY_MD = """\
# No project in this directory

Press **Init** (or `i`) to create an Agent On Rails contract here.

This TUI does not talk to a model. It packages work for whatever
headless agent you already use.
"""


class AorApp(App[None]):
    """Harness UI: specs, human gates, packaged tasks."""

    TITLE = "Agent On Rails"
    SUB_TITLE = f"v{__version__}  ·  mouse-friendly harness"
    CSS = """
    Screen { background: #0b1f3a; color: #e8f4ff; }
    Header { background: #0a2a4a; color: #2eb6ff; }
    Footer { background: #0a2a4a; }
    #pathbar {
        height: 1;
        color: #8eb4d4;
        padding: 0 1;
        background: #071628;
    }
    #body { height: 1fr; }
    #left { width: 3fr; }
    #right { width: 2fr; border-left: solid #1a4a6e; }
    .pane-title { color: #2eb6ff; text-style: bold; padding: 0 1; height: 1; }
    DataTable { height: 1fr; }
    #actions { height: auto; padding: 0 1 1 1; }
    #actions Button { margin-right: 1; }
    #log { height: 8; border-top: solid #1a4a6e; }
    Markdown { padding: 0 1; }
    """
    BINDINGS: ClassVar[list[Binding | tuple[str, str, str]]] = [
        Binding("q", "quit", "Quit"),
        Binding("i", "init", "Init"),
        Binding("n", "new_spec", "New spec"),
        Binding("a", "approve", "Approve"),
        Binding("p", "plan", "Plan"),
        Binding("r", "run_task", "Run"),
        Binding("v", "review", "Review"),
        Binding("x", "reject", "Reject"),
        Binding("g", "toggle_guide", "Guide"),
        Binding("f5", "refresh", "Refresh"),
    ]

    def __init__(self, start: Path, engine_url: str | None = None) -> None:
        super().__init__()
        self.start = start.resolve()
        self.engine_url = engine_url
        self.show_guide = True
        self._selected_spec: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("", id="pathbar")
        with Horizontal(id="body"):
            with Vertical(id="left"):
                yield Static("Specs", classes="pane-title")
                yield DataTable(id="specs", cursor_type="row")
                yield Static("Tasks", classes="pane-title")
                yield DataTable(id="tasks", cursor_type="row")
                with Horizontal(id="actions"):
                    yield Button("Init", id="btn-init", variant="primary")
                    yield Button("New spec", id="btn-new")
                    yield Button("Approve", id="btn-approve")
                    yield Button("Plan", id="btn-plan")
                    yield Button("Run", id="btn-run")
                    yield Button("Review", id="btn-review")
            with Vertical(id="right"):
                yield Markdown(GUIDE_MD, id="detail")
        yield Log(id="log", highlight=True, max_lines=400)
        yield Footer()

    def on_mount(self) -> None:
        specs = self.query_one("#specs", DataTable)
        specs.add_columns("ID", "Status", "Title", "Repos")
        tasks = self.query_one("#tasks", DataTable)
        tasks.add_columns("ID", "Spec", "Status", "Title")
        self.refresh_state()
        self._log("Agent On Rails TUI — click rows and buttons, or use the keys in the footer.")
        self._log("This is a harness. It does not run a model; your coding agent does.")

    def _log(self, message: str) -> None:
        self.query_one("#log", Log).write_line(message)

    def _root(self) -> Path | None:
        return find_control_plane(self.start)

    def _need_spec(self) -> str | None:
        if self._selected_spec:
            return self._selected_spec
        self._log("Select a spec first (click a row).")
        return None

    def refresh_state(self) -> None:
        data = snapshot(self.start)
        root = data["root"]
        pathbar = self.query_one("#pathbar", Static)
        if root is None:
            pathbar.update(f"no project  ·  {self.start}  ·  press Init")
        else:
            meta = data.get("meta")
            name = meta.name if meta else root.name
            pathbar.update(f"{name}  ·  {root}")

        specs_table = self.query_one("#specs", DataTable)
        specs_table.clear()
        for spec in data["specs"]:
            specs_table.add_row(
                spec.id,
                spec.status.upper(),
                spec.title,
                ", ".join(spec.repositories) or "—",
                key=spec.id,
            )
        tasks_table = self.query_one("#tasks", DataTable)
        tasks_table.clear()
        for task in data["tasks"]:
            tasks_table.add_row(task.id, task.spec_id, task.status.upper(), task.title, key=task.id)

        detail = self.query_one("#detail", Markdown)
        if self.show_guide or root is None:
            detail.update(EMPTY_MD if root is None else GUIDE_MD)
        elif self._selected_spec:
            spec = next((s for s in data["specs"] if s.id == self._selected_spec), None)
            if spec:
                detail.update(
                    f"# {spec.id} — {spec.title}\n\n"
                    f"**Status:** {spec.status.upper()}  \n"
                    f"**Repos:** {', '.join(spec.repositories) or '—'}  \n"
                    f"**Path:** `{spec.path}`\n\n"
                    f"{spec.intent or '_No intent yet._'}\n\n"
                    "Approve (human) → Plan → Run → open prompt.md in your agent → Review."
                )

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        key = str(event.row_key.value)
        if event.data_table.id == "specs":
            self._selected_spec = key
            self.show_guide = False
            self.refresh_state()
        elif event.data_table.id == "tasks":
            data = snapshot(self.start)
            task = next((t for t in data["tasks"] if t.id == key), None)
            if task:
                self._selected_spec = task.spec_id
                self.show_guide = False
                self.refresh_state()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping = {
            "btn-init": self.action_init,
            "btn-new": self.action_new_spec,
            "btn-approve": self.action_approve,
            "btn-plan": self.action_plan,
            "btn-run": self.action_run_task,
            "btn-review": self.action_review,
        }
        action = mapping.get(event.button.id or "")
        if action:
            action()

    def action_toggle_guide(self) -> None:
        self.show_guide = not self.show_guide
        self.refresh_state()

    def action_refresh(self) -> None:
        self.refresh_state()
        self._log("Refreshed.")

    def action_init(self) -> None:
        default_name = self.start.name.removesuffix("-control-plane") or "my-product"

        def done(result: tuple[str, str] | None) -> None:
            if not result:
                return
            path_s, name = result
            ok, message, root = init_project(Path(path_s), name)
            self._log(message)
            if ok:
                self.start = root
                self.refresh_state()

        self.push_screen(InitModal(str(self.start), default_name), done)

    def action_new_spec(self) -> None:
        root = self._root()
        if root is None:
            self._log("Init a project first.")
            return

        def done(result: tuple[str, str] | None) -> None:
            if not result:
                return
            title, repo = result
            ok, message = new_spec(root, title, repo)
            self._log(message)
            if ok:
                self.refresh_state()

        self.push_screen(NewSpecModal(), done)

    def action_approve(self) -> None:
        spec_id = self._need_spec()
        root = self._root()
        if not spec_id or root is None:
            return

        def done(ok: bool) -> None:
            if not ok:
                return
            success, message = human_approve(root, spec_id)
            self._log(message)
            if success:
                self.refresh_state()

        self.push_screen(
            ConfirmModal(
                f"Approve [b]{spec_id}[/b]?\n\nThis is a human gate. Agents cannot skip it.",
                yes="Approve",
            ),
            done,
        )

    def action_plan(self) -> None:
        spec_id = self._need_spec()
        root = self._root()
        if not spec_id or root is None:
            return
        ok, message = plan_and_message(root, spec_id)
        self._log(message)
        if ok:
            self.refresh_state()

    def action_run_task(self) -> None:
        spec_id = self._need_spec()
        root = self._root()
        if not spec_id or root is None:
            return
        ok, message = run_and_message(root, spec_id)
        self._log(message)
        if ok:
            self.refresh_state()

    def action_review(self) -> None:
        spec_id = self._need_spec()
        root = self._root()
        if not spec_id or root is None:
            return

        def done(ok: bool) -> None:
            if not ok:
                return
            success, message = review_and_message(root, spec_id, approve=True)
            self._log(message)
            if success:
                self.refresh_state()

        self.push_screen(
            ConfirmModal(
                f"Human final review of [b]{spec_id}[/b] — approve?\n\n"
                "Only do this after evidence (PR, tests) exists.",
                yes="Approve",
            ),
            done,
        )

    def action_reject(self) -> None:
        spec_id = self._need_spec()
        root = self._root()
        if not spec_id or root is None:
            return

        def done(ok: bool) -> None:
            if not ok:
                return
            success, message = review_and_message(root, spec_id, approve=False)
            self._log(message)
            if success:
                self.refresh_state()

        self.push_screen(
            ConfirmModal(f"Reject [b]{spec_id}[/b] and send it to RETRY?", yes="Reject"),
            done,
        )


def run_app(*, start: Path | None = None, engine_url: str | None = None) -> int:
    AorApp(start=start or Path.cwd(), engine_url=engine_url).run()
    return 0
