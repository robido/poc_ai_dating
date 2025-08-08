"""Chat window for individual personas."""

from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext

from ..chat import ChatSession
from ..personas import Persona
from ..prompts import GREETING_TEMPLATE
from .persona_controller import PersonaChatController

ROLE_COLORS = {"Ambassador": "green", "Other": "purple"}

def make_greeting(name: str) -> str:
    return GREETING_TEMPLATE.format(name=name)


class ChatBox(tk.Toplevel):
    """A window showing conversation with a single persona."""

    def __init__(self, master: tk.Misc, persona: Persona, session: ChatSession):
        super().__init__(master)
        self.persona = persona
        self.session = session
        self.controller: PersonaChatController = PersonaChatController(
            self, persona, session
        )

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
                role = (
                    persona.name
                    if msg["role"] == "user"
                    else self.controller.ambassador_name()
                )
                self.display_message(role, msg["content"])
        else:
            greeting = make_greeting(persona.name)
            self.display_message(self.controller.ambassador_name(), greeting)
            self.session.messages.append({"role": "assistant", "content": greeting})
            self.session.save_history()

    def display_message(self, role: str, content: str) -> None:
        if not content.strip():
            content = "Empty response"
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
        self.controller.send_message(text)

    def next_message(self) -> None:
        self.controller.next_message()

    def show_profile(self) -> None:
        data = self.session.profile_store.read(self.persona.name)
        popup = tk.Toplevel(self)
        popup.title(f"{self.persona.name} profile")
        tk.Message(popup, text=data or "No data yet.", width=300).pack(padx=10, pady=10)

    def update_match_display(self, matches, message_counts=None) -> None:
        self.controller.update_match_display(matches, message_counts)
