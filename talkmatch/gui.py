"""Tkinter GUI for the TalkMatch Phase 0 prototype."""
from __future__ import annotations

import tkinter as tk
from tkinter import scrolledtext

from .chat import ChatSession, FakeUser
from .ai import AIClient


class ChatWindow(tk.Toplevel):
    """User chat interface."""

    def __init__(self, master: tk.Misc, session: ChatSession):
        super().__init__(master)
        self.session = session
        self.title("TalkMatch Chat")
        self.geometry("400x500")

        self.chat_area = scrolledtext.ScrolledText(self, state="disabled")
        self.chat_area.pack(fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(self)
        self.entry.pack(fill=tk.X, padx=5, pady=5)
        self.entry.bind("<Return>", lambda event: self.send_message())

        send_btn = tk.Button(self, text="Send", command=self.send_message)
        send_btn.pack(pady=(0, 5))

    def display_message(self, role: str, content: str) -> None:
        self.chat_area.configure(state="normal")
        self.chat_area.insert(tk.END, f"{role}: {content}\n")
        self.chat_area.configure(state="disabled")
        self.chat_area.yview(tk.END)

    def send_message(self) -> None:
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self.display_message("You", text)
        reply = self.session.send_user_message(text)
        self.display_message("Other", reply)


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
        root.title("TalkMatch")
        root.geometry("300x150")

        tk.Button(root, text="User Login", command=self.open_chat).pack(pady=10)
        tk.Button(root, text="Admin Login", command=self.open_admin).pack(pady=10)

    def open_chat(self) -> None:
        ChatWindow(self.root, self.session)

    def open_admin(self) -> None:
        AdminWindow(self.root, self.session)


def run_app() -> None:
    """Entry point to run the GUI application."""
    root = tk.Tk()
    session = ChatSession(AIClient())
    LoginWindow(root, session)
    root.mainloop()
