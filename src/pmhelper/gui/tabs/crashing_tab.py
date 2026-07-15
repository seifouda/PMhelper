from tkinter import ttk
# Import the refactored core logic and GUI manager
from .crashing_tab_gui import CrashingTabGUIManager


class CrashingTab(ttk.Frame):
    """
    Main tab for Project Crashing analysis and visualization.
    Integrates all logic and GUI components.
    """

    def __init__(self, master, main_window):
        super().__init__(master)
        self.main_window = main_window
        # Initialize the GUI manager for this tab
        # All controls, analysis, and visualization are handled by
        # CrashingTabGUIManager
        self.gui_manager = CrashingTabGUIManager(self, main_window)

    def set_mode(self, mode):
        self.gui_manager.set_mode(mode)
