"""
PMhelper Edu — PERT Diagram Tab.
Wraps or copies the original pert_diagram_tab.py.
"""

from tkinter import ttk


class PertTabEdu:
    """Stub — may import original or be customised later."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="PERT Diagram — Coming Soon").pack(
            expand=True)

    def set_mode(self, mode: str):
        pass

    def on_tab_selected(self):
        pass
