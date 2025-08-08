"""Chat window for individual personas."""

from __future__ import annotations

import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from typing import Dict, List, Tuple

from ..ai import AIClient
from ..chat import ChatSession
from ..personas import Persona

ROLE_COLORS = {"Ambassador": "green", "Other": "purple"}
# Shorten the pause before the AI responds so conversations feel snappier.
REPLY_DELAY = 1

GREETING_TEMPLATE = (
    Path(__file__).resolve().parent.parent.joinpath("greeting_template.txt").read_text().strip()
)


def make_greeting(name: str) -> str:
    return GREETING_TEMPLATE.format(name=name)


class ChatBox(tk.Toplevel):
    """A window showing conversation with a single persona."""

    def __init__(self, master: tk.Misc, persona: Persona, session: ChatSession):
        super().__init__(master)
        self.persona = persona
        self.session = session
        self.persona_ai = AIClient()
        self.client_name = persona.name

        # When this window is restored, raise all windows so they stay grouped.
        self.bind("<Map>", lambda event: self.master.bring_all_to_front())

        self.title(persona.name)
        # Increase the window height to give the matches list more space.
        self.geometry("300x600")

        tk.Label(self, text=persona.name, font=("Helvetica", 10, "bold")).pack()
        self.chat_area = scrolledtext.ScrolledText(
            self, state="disabled", width=40, font=("Helvetica", 10), wrap=tk.WORD
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self, font=("Helvetica", 10))
        self.entry.pack(fill=tk.X, padx=5, pady=5)
        self.entry.bind("<Return>", lambda event: self.send_message())

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=(0, 5))
        tk.Button(btn_frame, text="Send", command=self.send_message).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="AI", command=self.next_message).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Show Profile", command=self.show_profile).pack(
            side=tk.LEFT, padx=5
        )

        # Provide a bit more room for the matches list.
        self.match_area = tk.Text(
            self, state="disabled", height=8, font=("Helvetica", 9), wrap=tk.WORD
        )
        self.match_area.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        if len(self.session.messages) > 1:
            for msg in self.session.messages[1:]:
                role = persona.name if msg["role"] == "user" else self.ambassador_name()
                self.display_message(role, msg["content"])
        else:
            greeting = make_greeting(persona.name)
            self.display_message(self.ambassador_name(), greeting)
            self.session.messages.append({"role": "assistant", "content": greeting})
            self.session.save_history()

    def ambassador_name(self) -> str:
        if self.session.matched_persona:
            return f"Ambassador ({self.session.matched_persona})"
        return "Ambassador"

    def display_message(self, role: str, content: str) -> None:
        self.chat_area.configure(state="normal")
        tag_role = role.replace(" ", "_").replace("(", "").replace(")", "")
        name_tag = f"{tag_role}_name"
        if name_tag not in self.chat_area.tag_names():
            base_role = role.split(" (", 1)[0]
            color = ROLE_COLORS.get(base_role, "purple")
            self.chat_area.tag_config(tag_role, foreground=color)
            self.chat_area.tag_config(
                name_tag, foreground=color, font=("Helvetica", 10, "bold")
            )
        self.chat_area.insert(tk.END, f"{role}: ", name_tag)
        self.chat_area.insert(tk.END, f"{content}\n\n", tag_role)
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(tk.END)

    def send_message(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.display_message(self.persona.name, text)

        def run() -> None:
            time.sleep(REPLY_DELAY)
            reply = self.session.send_client_message(self.persona.name, text)
            self.after(0, lambda: self.display_message(self.ambassador_name(), reply))

        threading.Thread(target=run, daemon=True).start()

    def next_message(self) -> None:
        def worker() -> None:
            context = [{"role": "system", "content": self.persona.system_prompt}]
            context.extend(self.session.messages[1:])
            persona_msg = self.persona_ai.get_response(context)
            self.after(0, lambda: self.display_message(self.persona.name, persona_msg))

            def reply_worker() -> None:
                time.sleep(REPLY_DELAY)
                reply = self.session.send_client_message(self.persona.name, persona_msg)
                self.after(0, lambda: self.display_message(self.ambassador_name(), reply))

            threading.Thread(target=reply_worker, daemon=True).start()

        threading.Thread(target=worker, daemon=True).start()

    def show_profile(self) -> None:
        data = self.session.profile_store.read(self.persona.name)
        popup = tk.Toplevel(self)
        popup.title(f"{self.persona.name} profile")
        tk.Message(popup, text=data or "No data yet.", width=300).pack(padx=10, pady=10)

    def update_match_display(
        self,
        matches: List[Tuple[str, float]],
        message_counts: Dict[Tuple[str, str], int] | None = None,
    ) -> None:
        self.match_area.configure(state="normal")
        self.match_area.delete("1.0", tk.END)
        for name, score in matches:
            count = 0
            if message_counts:
                key = tuple(sorted([self.client_name, name]))
                count = message_counts.get(key, 0)
            self.match_area.insert(tk.END, f"{name}: {score:.2f} ({count} msgs)\n")
        self.match_area.configure(state="disabled")
