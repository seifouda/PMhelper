"""
PMhelper Edu — Network Diagram Tab.
Wraps or copies the original network_tab.py.
"""

from tkinter import ttk


class NetworkTabEdu:
    """Stub — may import original or be customised later."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Network Diagram — Coming Soon").pack(
            expand=True)

    def set_mode(self, mode: str):
        pass

    def on_tab_selected(self):
        pass
