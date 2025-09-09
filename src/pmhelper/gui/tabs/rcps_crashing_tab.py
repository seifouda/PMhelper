#!/usr/bin/env python3
"""
RCPS Crashing Tab Module

Provides project crashing functionality specifically for RCPS (Resource-Constrained Project Scheduling) data.
This tab applies the same crashing logic and visualization as the regular Crashing tab,
but operates on resource-constrained schedule data from the RCPS tab.
"""

import tkinter as tk
from tkinter import ttk
from .project_crashing_core import RCPSProjectCrashing, CrashingStrategy, OptimizationObjective, CrashingResult, compare_crashing_results, generate_crashing_report
from .rcps_crashing_tab_gui import RCPSCrashingTabGUIManager


class RCPSCrashingTab(ttk.Frame):
    """
    RCPS Crashing tab for Project Crashing analysis using RCPS data.
    Integrates all logic and GUI components for resource-constrained crashing.
    """
    def __init__(self, master, main_window):
        super().__init__(master)
        self.main_window = main_window
        self.rcps_tab = None  # Reference to RCPS tab for data access
        
        # Initialize the GUI manager for this tab
        # All controls, analysis, and visualization are handled by RCPSCrashingTabGUIManager
        self.gui_manager = RCPSCrashingTabGUIManager(self, main_window)
    
    def set_rcps_tab_reference(self, rcps_tab):
        """Set reference to RCPS tab for data access"""
        self.rcps_tab = rcps_tab
        self.gui_manager.rcps_tab = rcps_tab
        # Establish bidirectional link
        self.rcps_tab.set_rcps_crashing_tab(self)
        print("[DEBUG] RCPS Crashing tab linked to RCPS tab")

    def get_rcps_analyzer(self):
        """Get RCPS analyzer (same pattern as normal crashing gets base_analyzer)"""
        if not self.rcps_tab:
            return None
        return self.rcps_tab.get_rcps_analyzer()

    def get_resource_limit(self):
        """Return the current resource limit from RCPS tab"""
        if self.rcps_tab:
            return self.rcps_tab.get_resource_limit()
        return 5  # Default fallback
