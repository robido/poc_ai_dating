"""Controller for persona-specific chat logic."""
from __future__ import annotations

import threading
import time
import tkinter as tk
from typing import TYPE_CHECKING, List, Tuple

from ..ai import AIClient
from ..chat import ChatSession
from ..personas import Persona

REPLY_DELAY = 1

if TYPE_CHECKING:
    from .chat_box import ChatBox


class PersonaChatController:
    """Handle AI interactions for a single persona chat."""

    def __init__(self, chat_box: ChatBox, persona: Persona, session: ChatSession) -> None:
        self.chat_box = chat_box
        self.persona = persona
        self.session = session
        self.persona_ai = AIClient()
        self.client_name = persona.name

    def ambassador_label(self) -> str:
        return self.session.ambassador_label()

    def send_message(self, text: str) -> None:
        self.chat_box.display_message(self.persona.name, text)

        def run() -> None:
            time.sleep(REPLY_DELAY)
            reply = self.session.send_client_message(self.persona.name, text)
            self.chat_box.after(
                0, lambda: self.chat_box.display_message(self.ambassador_label(), reply)
            )

        threading.Thread(target=run, daemon=True).start()

    def next_message(self) -> None:
        def worker() -> None:
            context = [{"role": "system", "content": self.persona.system_prompt}]
            context.extend(self.session.messages[1:])
            persona_msg = self.persona_ai.get_response(context)
            self.chat_box.after(
                0, lambda: self.chat_box.display_message(self.persona.name, persona_msg)
            )

            def reply_worker() -> None:
                time.sleep(REPLY_DELAY)
                reply = self.session.send_client_message(self.persona.name, persona_msg)
                self.chat_box.after(
                    0,
                    lambda: self.chat_box.display_message(
                        self.ambassador_label(), reply
                    ),
                )

            threading.Thread(target=reply_worker, daemon=True).start()

        threading.Thread(target=worker, daemon=True).start()

    def update_match_display(
        self, matches: List[Tuple[str, float]]
    ) -> None:
        match_area = self.chat_box.match_area
        match_area.configure(state="normal")
        match_area.delete("1.0", tk.END)
        for name, score in matches:
            match_area.insert(tk.END, f"{name}: {score:.2f}\n")
        match_area.configure(state="disabled")
