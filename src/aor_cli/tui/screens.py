"""Modal screens for the Agent On Rails TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class InitModal(ModalScreen[tuple[str, str] | None]):
    """Ask for a project path and product name."""

    CSS = """
    InitModal { align: center middle; }
    #init-dialog {
        width: 72;
        height: auto;
        border: tall #2eb6ff;
        background: #0a2a4a;
        padding: 1 2;
    }
    #init-dialog Label { margin-bottom: 1; }
    #init-dialog Input { margin-bottom: 1; }
    #init-actions { height: auto; align: right middle; }
    """

    def __init__(self, default_path: str, default_name: str) -> None:
        super().__init__()
        self.default_path = default_path
        self.default_name = default_name

    def compose(self) -> ComposeResult:
        with Vertical(id="init-dialog"):
            yield Static("[b]Init project[/b] — docs + specs contract, no app code")
            yield Label("Path")
            yield Input(self.default_path, id="path")
            yield Label("Product name")
            yield Input(self.default_name, id="name")
            with Horizontal(id="init-actions"):
                yield Button("Create", id="ok", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            path = self.query_one("#path", Input).value.strip()
            name = self.query_one("#name", Input).value.strip()
            self.dismiss((path, name) if path else None)
        else:
            self.dismiss(None)

    def on_input_submitted(self) -> None:
        self.query_one("#ok", Button).press()


class NewSpecModal(ModalScreen[tuple[str, str] | None]):
    """Ask for a spec title and implementation repo."""

    CSS = """
    NewSpecModal { align: center middle; }
    #spec-dialog {
        width: 72;
        height: auto;
        border: tall #2eb6ff;
        background: #0a2a4a;
        padding: 1 2;
    }
    #spec-dialog Label { margin-bottom: 1; }
    #spec-dialog Input { margin-bottom: 1; }
    #spec-actions { height: auto; align: right middle; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="spec-dialog"):
            yield Static("[b]New spec[/b] — draft contract (human must approve later)")
            yield Label("Title")
            yield Input(placeholder="Checkout totals", id="title")
            yield Label("Implementation repo")
            yield Input("app", id="repo")
            with Horizontal(id="spec-actions"):
                yield Button("Create", id="ok", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            title = self.query_one("#title", Input).value.strip()
            repo = self.query_one("#repo", Input).value.strip() or "app"
            self.dismiss((title, repo) if title else None)
        else:
            self.dismiss(None)

    def on_input_submitted(self) -> None:
        self.query_one("#ok", Button).press()


class ConfirmModal(ModalScreen[bool]):
    """Yes / no human gate."""

    CSS = """
    ConfirmModal { align: center middle; }
    #confirm-dialog {
        width: 64;
        height: auto;
        border: tall #2eb6ff;
        background: #0a2a4a;
        padding: 1 2;
    }
    #confirm-actions { height: auto; align: right middle; margin-top: 1; }
    """

    def __init__(self, question: str, *, yes: str = "Yes", no: str = "Cancel") -> None:
        super().__init__()
        self.question = question
        self.yes_label = yes
        self.no_label = no

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static(self.question)
            with Horizontal(id="confirm-actions"):
                yield Button(self.yes_label, id="yes", variant="primary")
                yield Button(self.no_label, id="no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")
