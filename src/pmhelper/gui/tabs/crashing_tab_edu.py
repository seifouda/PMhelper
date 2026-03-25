"""
PMhelper Edu — Crashing Tab.
Wraps or copies the original crashing_tab.py.
"""

from tkinter import ttk


class CrashingTabEdu:
    """Stub — may import original or be customised later."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Crashing — Coming Soon").pack(
            expand=True)

    def set_mode(self, mode: str):
        pass

    def on_tab_selected(self):
        pass
