"""Selection tab — stub placeholder for feat--sel-risk-da-co implementation."""

import tkinter as tk
from tkinter import ttk


class SelectionTab(ttk.Frame):
    """Project selection / portfolio prioritisation tab.

    This is a stub that keeps the app importable while the full feature
    is being implemented in the feat--sel-risk-da-co branch.
    """

    def __init__(self, parent, main_window=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.main_window = main_window
        ttk.Label(
            self,
            text="Project Selection — Coming Soon",
            font=("Segoe UI", 12),
        ).pack(expand=True)

    # ------------------------------------------------------------------ #
    # Common tab interface methods expected by main_window               #
    # ------------------------------------------------------------------ #

    def update_results(self, results_data=None):
        pass

    def set_mode(self, mode: str):
        pass

    def on_tab_selected(self):
        pass
