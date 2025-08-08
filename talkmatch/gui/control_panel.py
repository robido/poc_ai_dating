"""Control panel for managing chat sessions."""

from __future__ import annotations

import tkinter as tk
from typing import Dict

from ..ai import AIClient
from ..chat import ChatSession
from ..matcher import Matcher
from ..personas import PERSONAS
from ..persistent import Persistent

from .chat_box import ChatBox


class ControlPanel(tk.Tk):
    """Main control panel that spawns chat windows and manages matches."""

    def __init__(self) -> None:
        super().__init__()
        self.title("TalkMatch Control Panel")
        # Position the control panel and chat windows so they do not overlap.
        self.geometry("300x200+20+50")
        self.persistent = Persistent()
        self.profile_store = self.persistent.profile_store()
        ChatSession.message_counts = self.persistent.load_message_counts()

        self.personas = PERSONAS
        self.sessions: Dict[str, ChatSession] = {}
        self.windows: Dict[str, ChatBox] = {}

        for idx, persona in enumerate(self.personas):
            session = ChatSession(
                AIClient(),
                profile_store=self.profile_store,
                history_path=self.persistent.chat_history_path(persona.name),
                persistent=self.persistent,
            )
            self.sessions[persona.name] = session
            win = ChatBox(self, persona, session)
            # Arrange chat windows horizontally with a small gap.
            win.geometry(f"+{350 + idx * 320}+50")
            self.windows[persona.name] = win

        # When any window is restored, keep the whole set of windows on top.
        self.bind("<Map>", lambda event: self.bring_all_to_front())

        self.matcher = Matcher(
            [p.name for p in self.personas], path=self.persistent.match_matrix_path()
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
        ChatSession.message_counts.clear()
        self.persistent.save_message_counts({})
        self.refresh_matches()

    def refresh_matches(self) -> None:
        msg_counts = ChatSession.message_counts
        for name, win in self.windows.items():
            win.update_match_display(
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
