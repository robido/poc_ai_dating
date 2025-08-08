"""Control panel for managing chat sessions."""
from __future__ import annotations

import tkinter as tk
from typing import Dict

from ..session_manager import SessionManager
from .chat_box import ChatBox
from ..ai import AIClient


class ControlPanel(tk.Tk):
    """Main control panel that spawns chat windows and delegates logic."""

    def __init__(self, manager: SessionManager | None = None) -> None:
        super().__init__()
        self.title("TalkMatch Control Panel")
        # Position the control panel and chat windows so they do not overlap.
        self.geometry("300x200+20+50")

        self.session_manager = manager or SessionManager()
        self.windows: Dict[str, ChatBox] = {}

        for idx, persona in enumerate(self.session_manager.personas):
            session = self.session_manager.sessions[persona.name]
            win = ChatBox(self, persona, session)
            # Arrange chat windows horizontally with a small gap.
            win.geometry(f"+{350 + idx * 320}+50")
            self.windows[persona.name] = win

        # When any window is restored, keep the whole set of windows on top.
        self.bind("<Map>", lambda event: self.bring_all_to_front())

        self.session_manager.update_callback = self.update_match_display

        tk.Button(self, text="Calculate matches", command=self.calculate).pack(
            padx=10, pady=5
        )
        tk.Button(self, text="Clear matches", command=self.clear).pack(padx=10, pady=5)

        self.refresh_matches()

    def calculate(self) -> None:
        self.session_manager.calculate()

    def clear(self) -> None:
        self.session_manager.clear()

    def refresh_matches(self) -> None:
        self.session_manager.refresh_matches()

    def update_match_display(self, matches) -> None:
        for name, win in self.windows.items():
            win.controller.update_match_display(
                matches.get(name, [])
            )

    def bring_all_to_front(self) -> None:
        """Raise all application windows above others."""
        windows = [self, *self.windows.values()]
        for win in windows:
            win.lift()
            win.attributes("-topmost", True)
        # Allow other apps to come to the foreground afterwards.
        self.after(0, lambda: [w.attributes("-topmost", False) for w in windows])


def run_app(openai_client=None) -> None:
    """Launch the control panel with optional preconfigured OpenAI client."""
    factory = (lambda: AIClient(openai_client=openai_client)) if openai_client else AIClient
    manager = SessionManager(ai_client_factory=factory)
    ControlPanel(manager).mainloop()
