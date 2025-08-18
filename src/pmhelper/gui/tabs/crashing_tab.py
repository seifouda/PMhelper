import tkinter as tk
from tkinter import ttk
# Import the refactored core logic and GUI manager
from .project_crashing_core import ProjectCrashing, RCPSProjectCrashing, CrashingStrategy, OptimizationObjective, CrashingResult, compare_crashing_results, generate_crashing_report
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
        # All controls, analysis, and visualization are handled by CrashingTabGUIManager
        self.gui_manager = CrashingTabGUIManager(self, main_window)
