"""Tkinter GUI for the TalkMatch Phase 0 prototype."""
from __future__ import annotations

import random
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext

from .chat import ChatSession, FakeUser
from .ai import AIClient
from .personas import PERSONAS, Persona


USER_NAME = "Dominic"
ROLE_COLORS = {USER_NAME: "blue", "Ambassador": "green", "Other": "purple"}

# Load the greeting template from a text file and format it with the desired name.
GREETING_TEMPLATE = Path(__file__).with_name("greeting_template.txt").read_text().strip()


def make_greeting(name: str) -> str:
    return GREETING_TEMPLATE.format(name=name)


class ChatWindow(tk.Toplevel):
    """User chat interface."""

    def __init__(self, master: tk.Misc, session: ChatSession, on_close=None):
        super().__init__(master)
        self.session = session
        self._on_close = on_close
        self.title("TalkMatch Chat")
        self.geometry("400x500")

        tk.Label(self, text=USER_NAME, font=("Helvetica", 12, "bold")).pack()
        self.chat_area = scrolledtext.ScrolledText(self, state="disabled", font=("Helvetica", 12))
        self.chat_area.tag_config(USER_NAME, foreground=ROLE_COLORS[USER_NAME])
        self.chat_area.tag_config("Ambassador", foreground=ROLE_COLORS["Ambassador"])
        self.chat_area.tag_config("Other", foreground=ROLE_COLORS["Other"])
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self, font=("Helvetica", 12))
        self.entry.pack(fill=tk.X, padx=5, pady=5)
        self.entry.bind("<Return>", lambda event: self.send_message())

        send_btn = tk.Button(self, text="Send", command=self.send_message)
        send_btn.pack(pady=(0, 5))

        tk.Button(self, text="Show Profile", command=self.show_profile).pack(pady=(0, 5))

        greeting = make_greeting(USER_NAME)
        self.display_message("Ambassador", greeting)
        self.session.messages.append({"role": "assistant", "content": greeting})
        self.protocol("WM_DELETE_WINDOW", self.close)

    def display_message(self, role: str, content: str) -> None:
        self.chat_area.configure(state="normal")
        name_tag = f"{role}_name"
        if name_tag not in self.chat_area.tag_names():
            color = ROLE_COLORS.get(role, "purple")
            self.chat_area.tag_config(role, foreground=color)
            self.chat_area.tag_config(name_tag, foreground=color, font=("Helvetica", 12, "bold"))
        self.chat_area.insert(tk.END, f"{role}: ", name_tag)
        self.chat_area.insert(tk.END, f"{content}\n\n", role)
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(tk.END)

    def send_message(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.display_message(USER_NAME, text)

        def run() -> None:
            delay = random.randint(5, 10)
            time.sleep(delay)
            reply = self.session.send_client_message(USER_NAME, text)
            self.after(0, lambda: self.display_message("Other", reply))

        threading.Thread(target=run, daemon=True).start()

    def show_profile(self) -> None:
        data = self.session.profile_store.read(USER_NAME)
        popup = tk.Toplevel(self)
        popup.title("Known about you")
        tk.Message(popup, text=data or "No data yet.", width=300).pack(padx=10, pady=10)

    def close(self) -> None:
        if self._on_close:
            self._on_close()
        self.destroy()


class AdminWindow(tk.Toplevel):
    """Simple admin panel to trigger fake user responses."""

    def __init__(self, master: tk.Misc, session: ChatSession):
        super().__init__(master)
        self.session = session
        self.title("Admin Panel")
        self.geometry("300x200")

        tk.Label(self, text="Admin Controls").pack(pady=10)
        tk.Button(
            self,
            text="Switch to Fake User",
            command=self.trigger_fake_user,
        ).pack(pady=5)

    def trigger_fake_user(self) -> None:
        fake = FakeUser([
            "Hi! I'm the fake match.",
            "What do you like to do for fun?",
        ])
        self.session.switch_to_fake_user(fake)


class LoginWindow:
    """Starting point with simple login buttons."""

    def __init__(self, root: tk.Tk, session: ChatSession):
        self.root = root
        self.session = session
        self.chat_window = None
        root.title("TalkMatch")
        root.geometry("300x150")

        tk.Button(root, text="User Login", command=self.open_chat).pack(pady=10)
        tk.Button(root, text="Admin Login", command=self.open_admin).pack(pady=10)

    def open_chat(self) -> None:
        if self.chat_window and self.chat_window.winfo_exists():
            self.chat_window.lift()
            return
        self.chat_window = ChatWindow(self.root, self.session, on_close=self._chat_closed)

    def open_admin(self) -> None:
        AdminWindow(self.root, self.session)

    def _chat_closed(self) -> None:
        self.chat_window = None


class ChatPane(tk.Frame):
    """Base frame for displaying a single chat conversation."""

    def __init__(self, master: tk.Misc, session: ChatSession, title: str):
        super().__init__(master)
        self.session = session
        self.client_name = title
        tk.Label(self, text=title, font=("Helvetica", 12, "bold")).pack()
        self.chat_area = scrolledtext.ScrolledText(self, state="disabled", width=50, height=20, font=("Helvetica", 12))
        self.chat_area.pack(fill=tk.BOTH, expand=True)

    def add_profile_button(self) -> None:
        tk.Button(self, text="Show Profile", command=self.show_profile).pack(pady=(0, 5))

    def show_profile(self) -> None:
        data = self.session.profile_store.read(self.client_name)
        popup = tk.Toplevel(self)
        popup.title(f"{self.client_name} profile")
        tk.Message(popup, text=data or "No data yet.", width=300).pack(padx=10, pady=10)

    def display_message(self, role: str, content: str) -> None:
        self.chat_area.configure(state="normal")
        name_tag = f"{role}_name"
        if name_tag not in self.chat_area.tag_names():
            color = ROLE_COLORS.get(role, "purple")
            self.chat_area.tag_config(role, foreground=color)
            self.chat_area.tag_config(name_tag, foreground=color, font=("Helvetica", 12, "bold"))
        self.chat_area.insert(tk.END, f"{role}: ", name_tag)
        self.chat_area.insert(tk.END, f"{content}\n\n", role)
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(tk.END)


class UserChatPane(ChatPane):
    """Chat pane for the real user with text input."""

    def __init__(self, master: tk.Misc):
        session = ChatSession(AIClient())
        super().__init__(master, session, USER_NAME)
        self.entry = tk.Entry(self, font=("Helvetica", 12))
        self.entry.pack(fill=tk.X, padx=5, pady=5)
        self.entry.bind("<Return>", lambda event: self.send())
        tk.Button(self, text="Send", command=self.send).pack(pady=(0, 5))
        self.add_profile_button()

        greeting = make_greeting(USER_NAME)
        self.display_message("Ambassador", greeting)
        self.session.messages.append({"role": "assistant", "content": greeting})

    def send(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.display_message(USER_NAME, text)

        def run() -> None:
            delay = random.randint(5, 10)
            time.sleep(delay)
            reply = self.session.send_client_message(USER_NAME, text)
            self.after(0, lambda: self.display_message("Ambassador", reply))

        threading.Thread(target=run, daemon=True).start()


class PersonaChatPane(ChatPane):
    """Chat pane representing an AI persona chatting with the assistant."""

    def __init__(self, master: tk.Misc, persona: Persona):
        session = ChatSession(AIClient())
        super().__init__(master, session, persona.name)
        self.persona = persona
        self.persona_ai = AIClient()
        tk.Button(self, text="Next", command=self.next_message).pack(pady=(0, 5))
        self.add_profile_button()

        greeting = make_greeting(persona.name)
        self.display_message("Ambassador", greeting)
        self.session.messages.append({"role": "assistant", "content": greeting})

    def next_message(self) -> None:
        def worker() -> None:
            context = [{"role": "system", "content": self.persona.system_prompt}]
            context.extend(self.session.messages[1:])
            persona_msg = self.persona_ai.get_response(context)
            self.after(0, lambda: self.display_message(self.persona.name, persona_msg))

            def reply_worker() -> None:
                delay = random.randint(5, 10)
                time.sleep(delay)
                reply = self.session.send_client_message(self.persona.name, persona_msg)
                self.after(0, lambda: self.display_message("Ambassador", reply))

            threading.Thread(target=reply_worker, daemon=True).start()

        threading.Thread(target=worker, daemon=True).start()


def run_app() -> None:
    """Display the user and persona chats side-by-side."""
    root = tk.Tk()
    root.title("TalkMatch")

    user_pane = UserChatPane(root)
    user_pane.grid(row=0, column=0, padx=5, pady=5)

    for idx, persona in enumerate(PERSONAS, start=1):
        pane = PersonaChatPane(root, persona)
        pane.grid(row=0, column=idx, padx=5, pady=5)

    root.mainloop()
