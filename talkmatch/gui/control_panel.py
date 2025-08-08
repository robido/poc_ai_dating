"""Control panel for managing chat sessions."""
from __future__ import annotations

import tkinter as tk
from typing import Dict

from ..ai import AIClient
from ..chat import ChatSession
from ..storage import (
    ChatStore,
    MessageCountStore,
    ProfileStore,
    BASE_DIR,
)
from ..matcher import Matcher
from ..personas import PERSONAS

from .chat_box import ChatBox


class ControlPanel(tk.Tk):
    """Main control panel that spawns chat windows and manages matches."""

    def __init__(self) -> None:
        super().__init__()
        self.title("TalkMatch Control Panel")
        # Position the control panel and chat windows so they do not overlap.
        self.geometry("300x200+20+50")
        self.profile_store = ProfileStore()
        self.message_counts = MessageCountStore()

        self.personas = PERSONAS
        self.sessions: Dict[str, ChatSession] = {}
        self.windows: Dict[str, ChatBox] = {}

        for idx, persona in enumerate(self.personas):
            history = ChatStore(path=BASE_DIR / "chats" / f"{persona.name}.json")
            session = ChatSession(
                AIClient(),
                profile_store=self.profile_store,
                chat_store=history,
                message_counts=self.message_counts,
            )
            self.sessions[persona.name] = session
            win = ChatBox(self, persona, session)
            # Arrange chat windows horizontally with a small gap.
            win.geometry(f"+{350 + idx * 320}+50")
            self.windows[persona.name] = win

        # When any window is restored, keep the whole set of windows on top.
        self.bind("<Map>", lambda event: self.bring_all_to_front())

        self.matcher = Matcher(
            [p.name for p in self.personas], path=BASE_DIR / "match_matrix.json"
        )

        for session in self.sessions.values():
            session.update_callback = self.refresh_matches

        tk.Button(self, text="Calculate matches", command=self.calculate).pack(
            padx=10, pady=5
        )
        tk.Button(self, text="Clear matches", command=self.clear).pack(padx=10, pady=5)

        self.refresh_matches()

    def calculate(self) -> None:
        self.matcher.calculate(AIClient(), profile_store=self.profile_store)
        for persona in self.personas:
            top = self.matcher.top_matches(persona.name, 1)
            if top and top[0][1] > 0:
                self.sessions[persona.name].set_persona(top[0][0])
            else:
                self.sessions[persona.name].set_persona(None)
        self.refresh_matches()

    def clear(self) -> None:
        self.matcher.clear()
        for session in self.sessions.values():
            session.set_persona(None)
        self.message_counts.clear()
        self.refresh_matches()

    def refresh_matches(self) -> None:
        msg_counts = self.message_counts.counts
        for name, win in self.windows.items():
            win.controller.update_match_display(
                self.matcher.top_matches(name), message_counts=msg_counts
            )

    def bring_all_to_front(self) -> None:
        """Raise all application windows above others."""
        windows = [self, *self.windows.values()]
        for win in windows:
            win.lift()
            win.attributes("-topmost", True)
        # Allow other apps to come to the foreground afterwards.
        self.after(0, lambda: [w.attributes("-topmost", False) for w in windows])


def run_app() -> None:
    ControlPanel().mainloop()
