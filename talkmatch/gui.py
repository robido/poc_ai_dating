"""Tkinter GUI for the TalkMatch demo with separate chat windows."""
from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path
from typing import Dict, List, Tuple

from .chat import ChatSession
from .ai import AIClient
from .matcher import Matcher
from .personas import PERSONAS, Persona
from .persistent import Persistent

ROLE_COLORS = {"Ambassador": "green", "Other": "purple"}
# Shorten the pause before the AI responds so conversations feel snappier.
REPLY_DELAY = 1

GREETING_TEMPLATE = Path(__file__).with_name("greeting_template.txt").read_text().strip()


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
                role = persona.name if msg["role"] == "user" else "Ambassador"
                self.display_message(role, msg["content"])
        else:
            greeting = make_greeting(persona.name)
            self.display_message("Ambassador", greeting)
            self.session.messages.append({"role": "assistant", "content": greeting})
            self.session.save_history()

    def display_message(self, role: str, content: str) -> None:
        self.chat_area.configure(state="normal")
        tag_role = role.replace(" ", "_")
        name_tag = f"{tag_role}_name"
        if name_tag not in self.chat_area.tag_names():
            color = ROLE_COLORS.get(role, "purple")
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
            role = self.session.matched_persona or "Ambassador"
            self.after(0, lambda: self.display_message(role, reply))

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
                self.after(0, lambda: self.display_message("Ambassador", reply))

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
