"""
PMhelper Edu — Main Window.
This is a COPY of main_window.py, modified for the Edu edition.
The original main_window.py is NEVER touched.
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os
import math
import time as _time

from pmhelper.gui.edu_state import EduProjectState, AppConfig
from pmhelper.utils.project_io_edu import (
    save_full_project, load_full_project, make_empty_project,
)
from pmhelper.utils.chart_export_edu import export_all_charts_dialog
from pmhelper.core.cpm_analyzer import CPMAnalyzer
from pmhelper.gui.widgets.tutorial_overlay import TutorialOverlay, TutorialStep

try:
    from pmhelper.core.pert_analyzer import PERTAnalyzer
    HAS_PERT = True
except ImportError:
    HAS_PERT = False


# PG-only tabs — hidden in UG mode.
# Tabs removed from PG-only (now UG-visible): probability, charter, wbs, rcps
_PG_ONLY_TABS = {
    "rcps_crashing",
    "charter_mgr",
    "dpci",
    "swot",
    "pestel",
    "raci"}

# File extension for project files
_PROJ_EXT = ".pmproj"


class MainWindowEdu:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.state = EduProjectState()
        self.config = AppConfig.load()

        # CPM/PERT analysis state (facade for real tabs)
        self.cpm_analyzer = CPMAnalyzer()
        self.pert_analyzer = None
        if HAS_PERT:
            self.pert_analyzer = PERTAnalyzer()
        self.current_analyzer = self.cpm_analyzer
        self.base_analyzer = self.cpm_analyzer
        self.analysis_mode = 'deterministic'
        self.results_data = None
        self.last_analysis_results = None
        self.current_data = None

        # Ensure an empty project exists on startup
        if self.state.evm_project is None:
            proj, reg = make_empty_project()
            self.state.evm_project = proj
            self.state.risk_register = reg

        # Subscribe to dirty state for window title
        self.state.subscribe(self._on_state_change)

        # Unsaved-changes warning on close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Keyboard shortcuts
        self.root.bind_all("<Control-s>", lambda e: self._save_project())
        self.root.bind_all("<Control-S>", lambda e: self._save_project_as())

        self._build_menu()
        self._build_tabs()
        self._apply_mode(self.config.mode)

    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project", command=self._new_project)
        file_menu.add_command(
            label="Open Project...",
            command=self._open_project)
        file_menu.add_command(label="Save Project", command=self._save_project,
                              accelerator="Ctrl+S")
        file_menu.add_command(label="Save Project As...",
                              command=self._save_project_as,
                              accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        demo_menu = tk.Menu(file_menu, tearoff=0)
        demo_menu.add_command(
            label="UG Demo — Small (15 tasks)",
            command=lambda: self._load_demo("ug", "small"))
        demo_menu.add_command(
            label="UG Demo — Medium (150 tasks)",
            command=lambda: self._load_demo("ug", "medium"))
        demo_menu.add_command(
            label="UG Demo — Large (600 tasks)",
            command=lambda: self._load_demo("ug", "large"))
        demo_menu.add_separator()
        demo_menu.add_command(
            label="PG Demo — Small (13 tasks)",
            command=lambda: self._load_demo("pg", "small"))
        demo_menu.add_command(
            label="PG Demo — Medium (150 tasks)",
            command=lambda: self._load_demo("pg", "medium"))
        demo_menu.add_command(
            label="PG Demo — Large (600 tasks)",
            command=lambda: self._load_demo("pg", "large"))
        file_menu.add_cascade(label="Load Demo", menu=demo_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Export All Charts...",
                              command=self._export_all_charts)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        menubar.add_cascade(label="File", menu=file_menu)

        self._file_menu = file_menu
        self._rebuild_recent_menu()

        mode_menu = tk.Menu(menubar, tearoff=0)
        self._mode_var = tk.StringVar(value=self.config.mode)
        mode_menu.add_radiobutton(
            label="Undergraduate", variable=self._mode_var,
            value="UG", command=lambda: self._apply_mode("UG"))
        mode_menu.add_radiobutton(
            label="Postgraduate", variable=self._mode_var,
            value="PG", command=lambda: self._apply_mode("PG"))
        menubar.add_cascade(label="Mode", menu=mode_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Start Tutorial",
                              command=self._start_tutorial,
                              accelerator="F1")
        menubar.add_cascade(label="Help", menu=help_menu)
        self.root.bind_all("<F1>", lambda e: self._start_tutorial())

    def _rebuild_recent_menu(self):
        """Rebuild the Recent Files submenu from config."""
        menu = self._file_menu
        # Remove old Recent submenu if present
        if hasattr(self, "_recent_menu"):
            try:
                menu.delete("Recent Projects")
            except Exception:
                pass
        recent = self.config.recent_files
        if not recent:
            return
        self._recent_menu = tk.Menu(menu, tearoff=0)
        for path in recent:
            label = os.path.basename(path)
            self._recent_menu.add_command(
                label=label,
                command=lambda p=path: self._open_recent(p))
        # Insert before the last separator + Exit
        menu.insert_cascade(menu.index("Exit"), label="Recent Projects",
                            menu=self._recent_menu)

    def _open_recent(self, filepath: str):
        """Open a file from the Recent Projects list."""
        if not os.path.exists(filepath):
            messagebox.showwarning("File Not Found",
                                   f"File no longer exists:\n{filepath}")
            self.config.recent_files = [
                f for f in self.config.recent_files
                if os.path.normpath(f) != os.path.normpath(filepath)
            ]
            self.config.save()
            self._rebuild_recent_menu()
            return
        # Delegate to _open_project logic by setting the file directly
        if self.state.is_dirty():
            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save current project before opening another?")
            if answer is None:
                return
            if answer:
                self._save_project()
        try:
            data = load_full_project(filepath)
        except (FileNotFoundError, ValueError) as exc:
            messagebox.showerror("Open Error", str(exc))
            return
        self.state.evm_project = data["evm_project"] or make_empty_project()[0]
        self.state.risk_register = data["risk_register"]
        self.state.mc_results = data["mc_results"]
        self.state.swot_analysis = data.get("swot_analysis")
        self.state.pestel_analysis = data.get("pestel_analysis")
        self.state.wbs_tree = data.get("wbs_tree")
        self.state.raci_task = data.get("raci_task")
        self.state.raci_deliv = data.get("raci_deliv")
        self.state.current_file_path = filepath
        self.state.mark_clean()
        saved_mode = data.get("app_config", {}).get("mode", self.config.mode)
        self._apply_mode(saved_mode)
        cpm_activities = data.get("cpm_activities", [])
        cpm_mode = data.get("cpm_mode", "deterministic")
        if cpm_activities:
            self._input_tab_edu.load_activities(cpm_activities, cpm_mode)
        self.config.last_project_path = filepath
        self.config.add_recent_file(filepath)
        self.config.save()
        self._rebuild_recent_menu()
        self._refresh_all_edu_tabs()

    # ----------------------------------------------------------------
    #  Dual-notebook tab building
    #  UG mode  → self.notebook    (lecture sequence L1–L10)
    #  PG mode  → self.notebook_pg (topic groups: Schedule / Cost /
    #                                Risk / Strategic / Dashboard)
    # ----------------------------------------------------------------

    @property
    def _active_nb(self):
        """The TabGroupNotebook currently on-screen."""
        return self.notebook if self.config.mode == "UG" else self.notebook_pg

    def _build_tabs(self):
        self._build_tabs_ug()
        self._build_tabs_pg()
        # Both notebooks are built; _apply_mode (called from __init__)
        # will show the correct one and swap attribute references.

    def _build_tabs_ug(self):
        from pmhelper.gui.widgets.tab_group_notebook import TabGroupNotebook

        self.notebook = TabGroupNotebook(self.root)
        # Do NOT pack yet — _apply_mode decides which notebook is visible.

        # ── Lecture-sequenced sidebar groups (UG follows L1→L10) ──
        l1_nb = self.notebook.add_group("L1 · Foundations", icon="📖")
        l2_nb = self.notebook.add_group("L2 · Selection", icon="🎯")
        l3_nb = self.notebook.add_group("L3 · PM Role", icon="👔")
        l4_nb = self.notebook.add_group("L4 · Planning", icon="📋")
        l5_nb = self.notebook.add_group("L5 · CPM", icon="🔵")
        l6_nb = self.notebook.add_group("L6 · PERT", icon="📐")
        l7_nb = self.notebook.add_group("L7 · Cost Est.", icon="💲")
        l8_nb = self.notebook.add_group("L8 · Resources", icon="🔧")
        l9_nb = self.notebook.add_group("L9 · Crashing", icon="⚡")
        l10_nb = self.notebook.add_group("L10 · EVM", icon="📈")
        dash_nb = self.notebook.add_group("Dashboard", icon="📊")

        # Import new Edu-only reference tabs
        from pmhelper.gui.tabs.foundations_tab_edu import FoundationsTabEdu
        from pmhelper.gui.tabs.org_tab_edu import OrgTabEdu

        # Import Edu tab modules
        from pmhelper.gui.tabs.input_tab_edu import InputTabEdu
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        from pmhelper.gui.tabs.three_point_tab_edu import ThreePointTabEdu
        from pmhelper.gui.tabs.evm_tab_edu import EVMTabEdu
        from pmhelper.gui.tabs.financial_tab_edu import FinancialTabEdu
        from pmhelper.gui.tabs.risk_tab_edu import RiskTabEdu
        from pmhelper.gui.tabs.probability_tab_edu import ProbabilityTabEdu
        from pmhelper.gui.tabs.rcps_tab_edu import RCPSTabEdu
        from pmhelper.gui.tabs.dashboard_tab_edu import DashboardTabEdu
        from pmhelper.gui.tabs.cost_estimation_tab_edu import CostEstimationTabEdu

        # Import real PMhelper tab modules (unchanged originals)
        from pmhelper.gui.tabs.results_tab import ResultsTab
        from pmhelper.gui.tabs.network_tab import NetworkTab
        from pmhelper.gui.tabs.pert_diagram_tab import PertDiagramTab
        from pmhelper.gui.tabs.crashing_tab import CrashingTab
        from pmhelper.gui.tabs.rcps_crashing_tab import RCPSCrashingTab
        from pmhelper.gui.tabs.charter_tab import CharterTab
        from pmhelper.gui.tabs.charter_manager import CharterManager
        from pmhelper.gui.tabs.dpci_tab import DPCITab
        from pmhelper.gui.tabs.swot_tab_edu import SWOTTabEdu
        from pmhelper.gui.tabs.pestel_tab_edu import PESTELTabEdu
        from pmhelper.gui.tabs.wbs_tab_edu import WBSTabEdu
        from pmhelper.gui.tabs.raci_tab_edu import RACITabEdu

        # ══════════════════════════════════════════════════════════
        #  L1 · Foundations
        # ══════════════════════════════════════════════════════════
        self._foundations_tab = FoundationsTabEdu(l1_nb, self.state)
        l1_nb.add(self._foundations_tab.frame, text="Foundations")

        # ══════════════════════════════════════════════════════════
        #  L2 · Selection  (Financial Analysis covers UG needs)
        # ══════════════════════════════════════════════════════════
        self._financial_tab = FinancialTabEdu(
            l2_nb, self.state, main_window=self)
        l2_nb.add(self._financial_tab.frame, text="Financial Analysis")

        # ══════════════════════════════════════════════════════════
        #  L3 · PM Role & Organisation
        # ══════════════════════════════════════════════════════════
        self._org_tab = OrgTabEdu(l3_nb, self.state)
        l3_nb.add(self._org_tab.frame, text="PM Role & Org")

        # ══════════════════════════════════════════════════════════
        #  L4 · Planning  (Charter + WBS are UG; RACI/SWOT/PESTEL/DPCI PG-only)
        # ══════════════════════════════════════════════════════════
        self._charter_tab = CharterTab(l4_nb, self)
        l4_nb.add(self._charter_tab, text="Charter")

        self._wbs_tab = WBSTabEdu(l4_nb, self.state)
        l4_nb.add(self._wbs_tab.frame, text="WBS")

        self._risk_tab = RiskTabEdu(l4_nb, self.state)
        l4_nb.add(self._risk_tab.frame, text="Risk Analysis")

        # PG-only planning tabs
        self._raci_tab = RACITabEdu(l4_nb, self.state, main_window=self)
        l4_nb.add(self._raci_tab.frame, text="Responsibility Matrix")

        self.charter_manager = CharterManager(
            l4_nb,
            on_open_callback=self._charter_tab.load_charter_from_file,
            on_duplicate_callback=self._charter_tab.load_charter_from_file,
        )
        l4_nb.add(self.charter_manager, text="Charter Mgr")

        self._dpci_tab = DPCITab(l4_nb)
        l4_nb.add(self._dpci_tab, text="DPCI")

        self._swot_tab = SWOTTabEdu(l4_nb, self.state)
        l4_nb.add(self._swot_tab.frame, text="SWOT")

        self._pestel_tab = PESTELTabEdu(l4_nb, self.state)
        l4_nb.add(self._pestel_tab.frame, text="PESTEL")

        # ══════════════════════════════════════════════════════════
        #  L5 · CPM  (Input → Results → Network → PERT Diagram → Gantt)
        # ══════════════════════════════════════════════════════════
        self._input_tab_edu = InputTabEdu(l5_nb, self.state, main_window=self)
        self.input_tab = self._input_tab_edu
        l5_nb.add(self._input_tab_edu.frame, text="Input Activities")

        self.results_tab = ResultsTab(l5_nb, self)
        self.network_tab = NetworkTab(l5_nb, self)
        self.pert_diagram_tab = PertDiagramTab(l5_nb, self)

        self._gantt_tab_edu = GanttTabEdu(l5_nb, self.state, main_window=self)
        self.gantt_tab = self._gantt_tab_edu
        l5_nb.add(self._gantt_tab_edu.frame, text="Gantt Chart")

        # ══════════════════════════════════════════════════════════
        #  L6 · PERT  (Three-Point Estimates + Probability)
        # ══════════════════════════════════════════════════════════
        self._three_point_tab = ThreePointTabEdu(
            l6_nb, self.state, main_window=self)
        l6_nb.add(self._three_point_tab.frame, text="Three-Point Est.")

        self._probability_tab = ProbabilityTabEdu(
            l6_nb, self.state, main_window=self)
        l6_nb.add(self._probability_tab.frame, text="Probability")

        # ══════════════════════════════════════════════════════════
        #  L7 · Cost Estimation
        # ══════════════════════════════════════════════════════════
        self._cost_est_tab = CostEstimationTabEdu(
            l7_nb, self.state, main_window=self)
        l7_nb.add(self._cost_est_tab.frame, text="Cost Estimation")

        # ══════════════════════════════════════════════════════════
        #  L8 · Resources  (RCPS is UG; RCPS Crashing is PG-only)
        # ══════════════════════════════════════════════════════════
        self._rcps_tab = RCPSTabEdu(l8_nb, self.state, main_window=self)
        l8_nb.add(self._rcps_tab.frame, text="Resources")

        self._rcps_crashing_tab = RCPSCrashingTab(l8_nb, self)
        l8_nb.add(self._rcps_crashing_tab, text="RCPS Crash")

        # ══════════════════════════════════════════════════════════
        #  L9 · Crashing
        # ══════════════════════════════════════════════════════════
        self.crashing_tab = CrashingTab(l9_nb, self)
        l9_nb.add(self.crashing_tab, text="Crashing")

        # ══════════════════════════════════════════════════════════
        #  L10 · EVM
        # ══════════════════════════════════════════════════════════
        self._evm_tab = EVMTabEdu(l10_nb, self.state)
        l10_nb.add(self._evm_tab.frame, text="EVM Dashboard")

        # ══════════════════════════════════════════════════════════
        #  Dashboard (capstone)
        # ══════════════════════════════════════════════════════════
        self._dashboard_tab = DashboardTabEdu(dash_nb, self.state)
        dash_nb.add(self._dashboard_tab.frame, text="Dashboard")

        # ── Cross-tab wiring ──────────────────────────────────────
        self._rcps_crashing_tab.set_rcps_tab_reference(self._rcps_tab)

        # ── Widget → tab-object reverse map (for on_tab_changed) ──
        self._widget_to_tab = {
            id(self._foundations_tab.frame): self._foundations_tab,
            id(self._financial_tab.frame): self._financial_tab,
            id(self._org_tab.frame): self._org_tab,
            id(self._charter_tab): self._charter_tab,
            id(self._wbs_tab.frame): self._wbs_tab,
            id(self._risk_tab.frame): self._risk_tab,
            id(self._raci_tab.frame): self._raci_tab,
            id(self.charter_manager): self.charter_manager,
            id(self._dpci_tab): self._dpci_tab,
            id(self._swot_tab.frame): self._swot_tab,
            id(self._pestel_tab.frame): self._pestel_tab,
            id(self._input_tab_edu.frame): self._input_tab_edu,
            id(self.results_tab.results_frame): self.results_tab,
            id(self.network_tab.network_frame): self.network_tab,
            id(self.pert_diagram_tab.main_frame): self.pert_diagram_tab,
            id(self._gantt_tab_edu.frame): self._gantt_tab_edu,
            id(self._three_point_tab.frame): self._three_point_tab,
            id(self._probability_tab.frame): self._probability_tab,
            id(self._cost_est_tab.frame): self._cost_est_tab,
            id(self._rcps_tab.frame): self._rcps_tab,
            id(self._rcps_crashing_tab): self._rcps_crashing_tab,
            id(self.crashing_tab): self.crashing_tab,
            id(self._evm_tab.frame): self._evm_tab,
            id(self._dashboard_tab.frame): self._dashboard_tab,
        }

        # Edu tabs dict for set_mode / on_tab_selected / get_figures
        self.tabs = {
            "foundations": self._foundations_tab,
            "financial": self._financial_tab,
            "org": self._org_tab,
            "charter": self._charter_tab,
            "wbs": self._wbs_tab,
            "risk": self._risk_tab,
            "raci": self._raci_tab,
            "charter_mgr": self.charter_manager,
            "dpci": self._dpci_tab,
            "swot": self._swot_tab,
            "pestel": self._pestel_tab,
            "input": self._input_tab_edu,
            "gantt": self._gantt_tab_edu,
            "three_point": self._three_point_tab,
            "probability": self._probability_tab,
            "cost_estimation": self._cost_est_tab,
            "rcps": self._rcps_tab,
            "rcps_crashing": self._rcps_crashing_tab,
            "evm": self._evm_tab,
            "dashboard": self._dashboard_tab,
        }

        # PG-only tab widget references for show/hide
        # (probability, charter, wbs, rcps are now UG-visible)
        self._pg_only_widgets = [
            self._rcps_crashing_tab,        # RCPS Crash
            self.charter_manager,           # Charter Mgr
            self._dpci_tab,                 # DPCI
            self._swot_tab.frame,           # SWOT
            self._pestel_tab.frame,         # PESTEL
            self._raci_tab.frame,           # Responsibility Matrix
        ]

        # Auto-recalculate on tab switch (any group)
        self.notebook.bind_tab_changed(self._on_tab_changed)

        # ── Tutorial system ────────────────────────────────────
        self._tutorial = TutorialOverlay(
            self.root, self._build_tutorial_steps())

        # ── Save UG store for attribute-swapping in _apply_mode ──
        self._ug_store = {
            "attrs": {
                "_foundations_tab": self._foundations_tab,
                "_financial_tab": self._financial_tab,
                "_org_tab": self._org_tab,
                "_charter_tab": self._charter_tab,
                "_wbs_tab": self._wbs_tab,
                "_risk_tab": self._risk_tab,
                "_raci_tab": self._raci_tab,
                "charter_manager": self.charter_manager,
                "_dpci_tab": self._dpci_tab,
                "_swot_tab": self._swot_tab,
                "_pestel_tab": self._pestel_tab,
                "_input_tab_edu": self._input_tab_edu,
                "input_tab": self.input_tab,
                "results_tab": self.results_tab,
                "network_tab": self.network_tab,
                "pert_diagram_tab": self.pert_diagram_tab,
                "_gantt_tab_edu": self._gantt_tab_edu,
                "gantt_tab": self.gantt_tab,
                "_three_point_tab": self._three_point_tab,
                "_probability_tab": self._probability_tab,
                "_cost_est_tab": self._cost_est_tab,
                "_rcps_tab": self._rcps_tab,
                "_rcps_crashing_tab": self._rcps_crashing_tab,
                "crashing_tab": self.crashing_tab,
                "_evm_tab": self._evm_tab,
                "_dashboard_tab": self._dashboard_tab,
            },
            "tabs": self.tabs,
            "widget_to_tab": self._widget_to_tab,
            "pg_only_widgets": self._pg_only_widgets,
        }

    # ----------------------------------------------------------------
    def _build_tabs_pg(self):
        """Build the PG-mode TabGroupNotebook (topic groups, not lectures)."""
        from pmhelper.gui.widgets.tab_group_notebook import TabGroupNotebook

        # Import all tab classes (same set as UG)
        from pmhelper.gui.tabs.foundations_tab_edu import FoundationsTabEdu
        from pmhelper.gui.tabs.org_tab_edu import OrgTabEdu
        from pmhelper.gui.tabs.input_tab_edu import InputTabEdu
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        from pmhelper.gui.tabs.three_point_tab_edu import ThreePointTabEdu
        from pmhelper.gui.tabs.evm_tab_edu import EVMTabEdu
        from pmhelper.gui.tabs.financial_tab_edu import FinancialTabEdu
        from pmhelper.gui.tabs.risk_tab_edu import RiskTabEdu
        from pmhelper.gui.tabs.probability_tab_edu import ProbabilityTabEdu
        from pmhelper.gui.tabs.rcps_tab_edu import RCPSTabEdu
        from pmhelper.gui.tabs.dashboard_tab_edu import DashboardTabEdu
        from pmhelper.gui.tabs.cost_estimation_tab_edu import CostEstimationTabEdu
        from pmhelper.gui.tabs.results_tab import ResultsTab
        from pmhelper.gui.tabs.network_tab import NetworkTab
        from pmhelper.gui.tabs.pert_diagram_tab import PertDiagramTab
        from pmhelper.gui.tabs.crashing_tab import CrashingTab
        from pmhelper.gui.tabs.rcps_crashing_tab import RCPSCrashingTab
        from pmhelper.gui.tabs.charter_tab import CharterTab
        from pmhelper.gui.tabs.charter_manager import CharterManager
        from pmhelper.gui.tabs.dpci_tab import DPCITab
        from pmhelper.gui.tabs.swot_tab_edu import SWOTTabEdu
        from pmhelper.gui.tabs.pestel_tab_edu import PESTELTabEdu
        from pmhelper.gui.tabs.wbs_tab_edu import WBSTabEdu
        from pmhelper.gui.tabs.raci_tab_edu import RACITabEdu

        pg = TabGroupNotebook(self.root)
        self.notebook_pg = pg
        # Not packed yet — _apply_mode controls visibility.

        sched_nb = pg.add_group("Schedule", icon="📅")
        cost_nb = pg.add_group("Cost", icon="💰")
        risk_nb = pg.add_group("Risk", icon="⚠")
        strat_nb = pg.add_group("Strategic", icon="📌")
        dash_nb = pg.add_group("Dashboard", icon="📊")

        # ── Schedule ──────────────────────────────────────────────
        p_input = InputTabEdu(sched_nb, self.state, main_window=self)
        sched_nb.add(p_input.frame, text="Input Activities")
        p_results = ResultsTab(sched_nb, self)
        p_network = NetworkTab(sched_nb, self)
        p_pert_diag = PertDiagramTab(sched_nb, self)
        p_gantt = GanttTabEdu(sched_nb, self.state, main_window=self)
        sched_nb.add(p_gantt.frame, text="Gantt Chart")
        p_three_point = ThreePointTabEdu(
            sched_nb, self.state, main_window=self)
        sched_nb.add(p_three_point.frame, text="Three-Point Est.")
        p_crashing = CrashingTab(sched_nb, self)
        sched_nb.add(p_crashing, text="Crashing")

        # ── Cost ──────────────────────────────────────────────────
        p_evm = EVMTabEdu(cost_nb, self.state)
        cost_nb.add(p_evm.frame, text="EVM Dashboard")
        p_financial = FinancialTabEdu(cost_nb, self.state, main_window=self)
        cost_nb.add(p_financial.frame, text="Financial Analysis")
        p_cost_est = CostEstimationTabEdu(
            cost_nb, self.state, main_window=self)
        cost_nb.add(p_cost_est.frame, text="Cost Estimation")
        p_rcps = RCPSTabEdu(cost_nb, self.state, main_window=self)
        cost_nb.add(p_rcps.frame, text="Resources")
        p_rcps_crash = RCPSCrashingTab(cost_nb, self)
        cost_nb.add(p_rcps_crash, text="RCPS Crash")

        # ── Risk ──────────────────────────────────────────────────
        p_risk = RiskTabEdu(risk_nb, self.state)
        risk_nb.add(p_risk.frame, text="Risk Analysis")
        p_prob = ProbabilityTabEdu(risk_nb, self.state, main_window=self)
        risk_nb.add(p_prob.frame, text="Probability")

        # ── Strategic ─────────────────────────────────────────────
        p_found = FoundationsTabEdu(strat_nb, self.state)
        strat_nb.add(p_found.frame, text="Foundations")
        p_org = OrgTabEdu(strat_nb, self.state)
        strat_nb.add(p_org.frame, text="PM Role & Org")
        p_charter = CharterTab(strat_nb, self)
        strat_nb.add(p_charter, text="Charter")
        p_wbs = WBSTabEdu(strat_nb, self.state)
        strat_nb.add(p_wbs.frame, text="WBS")
        p_raci = RACITabEdu(strat_nb, self.state, main_window=self)
        strat_nb.add(p_raci.frame, text="Responsibility Matrix")
        p_charter_mgr = CharterManager(
            strat_nb,
            on_open_callback=p_charter.load_charter_from_file,
            on_duplicate_callback=p_charter.load_charter_from_file,
        )
        strat_nb.add(p_charter_mgr, text="Charter Mgr")
        p_dpci = DPCITab(strat_nb)
        strat_nb.add(p_dpci, text="DPCI")
        p_swot = SWOTTabEdu(strat_nb, self.state)
        strat_nb.add(p_swot.frame, text="SWOT")
        p_pestel = PESTELTabEdu(strat_nb, self.state)
        strat_nb.add(p_pestel.frame, text="PESTEL")

        # ── Dashboard ─────────────────────────────────────────────
        p_dash = DashboardTabEdu(dash_nb, self.state)
        dash_nb.add(p_dash.frame, text="Dashboard")

        # Cross-tab wiring
        p_rcps_crash.set_rcps_tab_reference(p_rcps)

        # Widget → tab reverse map
        pg_widget_to_tab = {
            id(p_found.frame): p_found,
            id(p_financial.frame): p_financial,
            id(p_org.frame): p_org,
            id(p_charter): p_charter,
            id(p_wbs.frame): p_wbs,
            id(p_risk.frame): p_risk,
            id(p_raci.frame): p_raci,
            id(p_charter_mgr): p_charter_mgr,
            id(p_dpci): p_dpci,
            id(p_swot.frame): p_swot,
            id(p_pestel.frame): p_pestel,
            id(p_input.frame): p_input,
            id(p_results.results_frame): p_results,
            id(p_network.network_frame): p_network,
            id(p_pert_diag.main_frame): p_pert_diag,
            id(p_gantt.frame): p_gantt,
            id(p_three_point.frame): p_three_point,
            id(p_prob.frame): p_prob,
            id(p_cost_est.frame): p_cost_est,
            id(p_rcps.frame): p_rcps,
            id(p_rcps_crash): p_rcps_crash,
            id(p_crashing): p_crashing,
            id(p_evm.frame): p_evm,
            id(p_dash.frame): p_dash,
        }

        pg_tabs = {
            "foundations": p_found,
            "financial": p_financial,
            "org": p_org,
            "charter": p_charter,
            "wbs": p_wbs,
            "risk": p_risk,
            "raci": p_raci,
            "charter_mgr": p_charter_mgr,
            "dpci": p_dpci,
            "swot": p_swot,
            "pestel": p_pestel,
            "input": p_input,
            "gantt": p_gantt,
            "three_point": p_three_point,
            "probability": p_prob,
            "cost_estimation": p_cost_est,
            "rcps": p_rcps,
            "rcps_crashing": p_rcps_crash,
            "evm": p_evm,
            "dashboard": p_dash,
        }

        pg.bind_tab_changed(self._on_tab_changed)

        # Save PG store (all tabs visible in PG, so pg_only_widgets is empty)
        self._pg_store = {
            "attrs": {
                "_foundations_tab": p_found,
                "_financial_tab": p_financial,
                "_org_tab": p_org,
                "_charter_tab": p_charter,
                "_wbs_tab": p_wbs,
                "_risk_tab": p_risk,
                "_raci_tab": p_raci,
                "charter_manager": p_charter_mgr,
                "_dpci_tab": p_dpci,
                "_swot_tab": p_swot,
                "_pestel_tab": p_pestel,
                "_input_tab_edu": p_input,
                "input_tab": p_input,
                "results_tab": p_results,
                "network_tab": p_network,
                "pert_diagram_tab": p_pert_diag,
                "_gantt_tab_edu": p_gantt,
                "gantt_tab": p_gantt,
                "_three_point_tab": p_three_point,
                "_probability_tab": p_prob,
                "_cost_est_tab": p_cost_est,
                "_rcps_tab": p_rcps,
                "_rcps_crashing_tab": p_rcps_crash,
                "crashing_tab": p_crashing,
                "_evm_tab": p_evm,
                "_dashboard_tab": p_dash,
            },
            "tabs": pg_tabs,
            "widget_to_tab": pg_widget_to_tab,
            "pg_only_widgets": [],   # All tabs shown in PG mode
        }

    def _build_tutorial_steps(self) -> list:
        """Return the list of TutorialStep objects for the guided tour."""
        nb = self.notebook

        def _sidebar_btn(group_name):
            grp = nb._groups.get(group_name)
            return grp.button if grp else None

        # Invisible proxy frame — repositioned over each tab label.
        # It is lowered below the tab bar so it never visually covers anything,
        # but its geometry is used by the overlay to position the highlight.
        self._tab_proxy = tk.Frame(self.root, width=1, height=1)
        _TAB_BAR_H = 28          # typical ttk tab-bar height (px)

        def _tab_label_widget(group_name, tab_frame):
            """Place a proxy Frame over the tab label for *tab_frame*.

            Uses pixel-scanning with notebook.index('@x,y') to find exact
            tab label boundaries — independent of font or theme padding.
            """
            grp = nb._groups.get(group_name)
            if grp is None:
                return None
            inner_nb = grp.notebook
            self.root.update_idletasks()

            # Find which index this frame is
            target_idx = None
            for i, tab_id in enumerate(inner_nb.tabs()):
                try:
                    if inner_nb.nametowidget(tab_id) is tab_frame:
                        target_idx = i
                        break
                except Exception:
                    continue
            if target_idx is None:
                return inner_nb

            # Scan the top row of the notebook to find the pixel boundaries
            # of the target tab using identify / index('@x,y')
            nb_w = inner_nb.winfo_width()
            y_probe = 8  # middle of the tab-bar height
            x_start = None
            x_end = None
            step = 2  # scan in 2px steps for speed

            for x in range(0, nb_w, step):
                try:
                    idx = inner_nb.index(f"@{x},{y_probe}")
                except (tk.TclError, ValueError):
                    continue
                if idx == target_idx:
                    if x_start is None:
                        # Refine: go back to find exact start
                        x_start = x
                        for rx in range(x, max(x - step - 1, -1), -1):
                            try:
                                if inner_nb.index(
                                        f"@{rx},{y_probe}") == target_idx:
                                    x_start = rx
                                else:
                                    break
                            except (tk.TclError, ValueError):
                                break
                    x_end = x
                elif x_start is not None:
                    # We've passed the target tab — done
                    break

            if x_start is None:
                return inner_nb

            # Refine x_end forward
            for rx in range(x_end, min(x_end + step + 1, nb_w)):
                try:
                    if inner_nb.index(f"@{rx},{y_probe}") == target_idx:
                        x_end = rx
                    else:
                        break
                except (tk.TclError, ValueError):
                    break

            label_w = x_end - x_start + 1
            nbx = inner_nb.winfo_rootx() - self.root.winfo_rootx()
            nby = inner_nb.winfo_rooty() - self.root.winfo_rooty()

            self._tab_proxy.place(
                x=nbx + x_start, y=nby,
                width=label_w, height=_TAB_BAR_H)
            self._tab_proxy.update_idletasks()
            # Lower the proxy behind everything so it doesn't cover the tab
            # text
            self._tab_proxy.lower()
            return self._tab_proxy

        def _switch_to(tab_frame):
            """Return a callable that auto-switches to the tab containing tab_frame."""
            def _do():
                nb.select_tab(tab_frame)
            return _do

        steps = [
            # ── Layout ──────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: nb._sidebar,
                title="Navigation Sidebar",
                description=(
                    "The sidebar is organised by lecture (L1–L10) so you can "
                    "work through course topics in sequence. "
                    "Click any lecture group to open its tools."
                ),
            ),

            # ── L1 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L1 \u00b7 Foundations"),
                title="L1 · Foundations",
                description=(
                    "Start here: project definition, the triple constraint "
                    "(scope/time/cost), lifecycle phases, and the difference "
                    "between projects and operations."
                ),
                on_enter=lambda: nb._select_group("L1 \u00b7 Foundations"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L1 \u00b7 Foundations", self._foundations_tab.frame),
                title="Foundations Reference Card",
                description=(
                    "A scrollable reference card covering the L1 theory. "
                    "Use it alongside lecture notes to reinforce key definitions."
                ),
                on_enter=_switch_to(self._foundations_tab.frame),
            ),

            # ── L2 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L2 \u00b7 Selection"),
                title="L2 · Project Selection",
                description=(
                    "Evaluate and compare projects financially using "
                    "NPV, IRR, payback period, and benefit-cost ratio."
                ),
                on_enter=lambda: nb._select_group("L2 \u00b7 Selection"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L2 \u00b7 Selection", self._financial_tab.frame),
                title="Financial Analysis",
                description=(
                    "Calculate NPV, IRR, payback period, "
                    "and benefit-cost ratio for your project\u2019s "
                    "financial viability."
                ),
                on_enter=_switch_to(self._financial_tab.frame),
            ),

            # ── L3 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L3 \u00b7 PM Role"),
                title="L3 · PM Role & Organisation",
                description=(
                    "Understand the PM's responsibilities, the PMI Talent Triangle, "
                    "and the three organisational structures: functional, "
                    "projectised, and matrix."
                ),
                on_enter=lambda: nb._select_group("L3 \u00b7 PM Role"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L3 \u00b7 PM Role", self._org_tab.frame),
                title="PM Role & Org Reference Card",
                description=(
                    "A scrollable reference card covering L3 theory on "
                    "organisational structures and stakeholder management."
                ),
                on_enter=_switch_to(self._org_tab.frame),
            ),

            # ── L4 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L4 \u00b7 Planning"),
                title="L4 · Planning",
                description=(
                    "Draft the Project Charter, build the WBS, "
                    "and identify risks. RACI, SWOT, PESTEL, and DPCI "
                    "are also here (PG unlocks those)."
                ),
                on_enter=lambda: nb._select_group("L4 \u00b7 Planning"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L4 \u00b7 Planning", self._charter_tab),
                title="Charter",
                description=(
                    "Draft the project charter with objectives, "
                    "scope, stakeholders, milestones, "
                    "and high-level budget."
                ),
                on_enter=_switch_to(self._charter_tab),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L4 \u00b7 Planning", self._wbs_tab.frame),
                title="WBS",
                description=(
                    "Build a Work Breakdown Structure \u2014 "
                    "decompose project scope into manageable "
                    "deliverables and work packages."
                ),
                on_enter=_switch_to(self._wbs_tab.frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L4 \u00b7 Planning", self._risk_tab.frame),
                title="Risk Analysis",
                description=(
                    "Build a risk register, assign probability and "
                    "impact scores, view the risk heat map, "
                    "and plan responses."
                ),
                on_enter=_switch_to(self._risk_tab.frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L4 \u00b7 Planning", self._raci_tab.frame),
                title="Responsibility Matrix (PG)",
                description=(
                    "Assign Responsible, Accountable, Consulted, "
                    "and Informed roles for each activity "
                    "using the RACI matrix."
                ),
                on_enter=_switch_to(self._raci_tab.frame),
                group="pg",
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L4 \u00b7 Planning", self._swot_tab.frame),
                title="SWOT Analysis (PG)",
                description=(
                    "Identify Strengths, Weaknesses, Opportunities, "
                    "and Threats to inform strategic project decisions."
                ),
                on_enter=_switch_to(self._swot_tab.frame),
                group="pg",
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L4 \u00b7 Planning", self._pestel_tab.frame),
                title="PESTEL Analysis (PG)",
                description=(
                    "Analyse Political, Economic, Social, "
                    "Technological, Environmental, and Legal "
                    "factors affecting the project."
                ),
                on_enter=_switch_to(self._pestel_tab.frame),
                group="pg",
            ),

            # ── L5 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L5 \u00b7 CPM"),
                title="L5 · Critical Path Method",
                description=(
                    "Enter activities, run CPM, and view results, "
                    "network diagram, PERT diagram, and Gantt chart "
                    "all in one lecture group."
                ),
                on_enter=lambda: nb._select_group("L5 \u00b7 CPM"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L5 \u00b7 CPM", self._input_tab_edu.frame),
                title="Input Activities",
                description=(
                    "Enter your project activities here with their "
                    "durations, predecessors, and resource data. "
                    "This is where every project starts. "
                    "Click \u2018Analyse\u2019 to run CPM."
                ),
                on_enter=_switch_to(self._input_tab_edu.frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L5 \u00b7 CPM", self.results_tab.results_frame),
                title="CPM Results",
                description=(
                    "After running analysis, view the full CPM results "
                    "table with ES, EF, LS, LF, and float values. "
                    "Critical activities are highlighted."
                ),
                on_enter=_switch_to(self.results_tab.results_frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L5 \u00b7 CPM", self.network_tab.network_frame),
                title="Network Diagram",
                description=(
                    "Visualise the activity-on-node (AoN) network. "
                    "Nodes show ES, EF, LS, LF, and float. "
                    "Critical path is highlighted in red."
                ),
                on_enter=_switch_to(self.network_tab.network_frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L5 \u00b7 CPM", self.pert_diagram_tab.main_frame),
                title="PERT Diagram",
                description=(
                    "View the PERT network layout with optimistic, "
                    "most likely, and pessimistic duration estimates "
                    "and expected completion probabilities."
                ),
                on_enter=_switch_to(self.pert_diagram_tab.main_frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L5 \u00b7 CPM", self._gantt_tab_edu.frame),
                title="Gantt Chart",
                description=(
                    "Visualise the project schedule as a Gantt chart. "
                    "Critical path bars are shown in red, "
                    "float bars in light blue."
                ),
                on_enter=_switch_to(self._gantt_tab_edu.frame),
            ),

            # ── L6 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L6 \u00b7 PERT"),
                title="L6 · PERT & Probability",
                description=(
                    "Enter three-point duration estimates (O/M/P), "
                    "compute PERT expected values, and analyse "
                    "completion probability."
                ),
                on_enter=lambda: nb._select_group("L6 \u00b7 PERT"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L6 \u00b7 PERT", self._three_point_tab.frame),
                title="Three-Point Estimates",
                description=(
                    "Enter optimistic, most likely, and pessimistic "
                    "durations to compute PERT expected values "
                    "and standard deviations."
                ),
                on_enter=_switch_to(self._three_point_tab.frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L6 \u00b7 PERT", self._probability_tab.frame),
                title="Probability / Monte Carlo",
                description=(
                    "Run Monte Carlo simulations to estimate "
                    "project completion probability and "
                    "confidence intervals."
                ),
                on_enter=_switch_to(self._probability_tab.frame),
            ),

            # ── L7 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L7 \u00b7 Cost Est."),
                title="L7 · Cost Estimation",
                description=(
                    "Apply analogous, parametric, and bottom-up "
                    "estimation techniques to build accurate "
                    "project cost estimates."
                ),
                on_enter=lambda: nb._select_group("L7 \u00b7 Cost Est."),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L7 \u00b7 Cost Est.", self._cost_est_tab.frame),
                title="Cost Estimation",
                description=(
                    "Use analogous, parametric, and bottom-up "
                    "estimation techniques to build accurate "
                    "project cost estimates."
                ),
                on_enter=_switch_to(self._cost_est_tab.frame),
            ),

            # ── L8 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L8 \u00b7 Resources"),
                title="L8 · Resource-Constrained Scheduling",
                description=(
                    "Level resource usage, view histograms, "
                    "and resolve over-allocation using RCPS. "
                    "RCPS Crashing is PG-only."
                ),
                on_enter=lambda: nb._select_group("L8 \u00b7 Resources"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L8 \u00b7 Resources", self._rcps_tab.frame),
                title="Resources (RCPS)",
                description=(
                    "Resource-constrained project scheduling \u2014 "
                    "level resource usage, view histograms, "
                    "and resolve over-allocation."
                ),
                on_enter=_switch_to(self._rcps_tab.frame),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L8 \u00b7 Resources", self._rcps_crashing_tab),
                title="RCPS Crashing (PG)",
                description=(
                    "Combine resource-constrained scheduling with "
                    "activity crashing to find the best "
                    "time\u2013cost\u2013resource trade-off."
                ),
                on_enter=_switch_to(self._rcps_crashing_tab),
                group="pg",
            ),

            # ── L9 ──────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L9 \u00b7 Crashing"),
                title="L9 · Time–Cost Trade-off (Crashing)",
                description=(
                    "Crash activities to shorten the project duration. "
                    "Set crash costs and durations, then optimise "
                    "the trade-off between time and cost."
                ),
                on_enter=lambda: nb._select_group("L9 \u00b7 Crashing"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L9 \u00b7 Crashing", self.crashing_tab),
                title="Crashing",
                description=(
                    "Crash activities to shorten the project duration. "
                    "Set crash costs and durations, then optimise "
                    "the trade-off between time and cost."
                ),
                on_enter=_switch_to(self.crashing_tab),
            ),

            # ── L10 ─────────────────────────────────────────────────
            TutorialStep(
                widget_fn=lambda: _sidebar_btn("L10 \u00b7 EVM"),
                title="L10 · Earned Value Management",
                description=(
                    "Track project performance using EVM KPIs: "
                    "CPI, SPI, EAC, ETC, VAC, TCPI, and S-curve."
                ),
                on_enter=lambda: nb._select_group("L10 \u00b7 EVM"),
            ),
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "L10 \u00b7 EVM", self._evm_tab.frame),
                title="EVM Dashboard",
                description=(
                    "Earned Value Management \u2014 track cost and schedule "
                    "performance with CPI, SPI, EAC, ETC, "
                    "and variance analysis."
                ),
                on_enter=_switch_to(self._evm_tab.frame),
            ),

            # ══ DASHBOARD ══════════════════════════════════════════
            TutorialStep(
                widget_fn=lambda: _tab_label_widget(
                    "Dashboard", self._dashboard_tab.frame),
                title="Dashboard",
                description=(
                    "View a summary dashboard with KPIs, "
                    "critical path overview, cost/schedule "
                    "status, and project alerts."
                ),
                on_enter=_switch_to(self._dashboard_tab.frame),
            ),

            # ══ Wrap up ═══════════════════════════════════════════
            TutorialStep(
                widget_fn=lambda: nb._sidebar,
                title="File & Mode Menus",
                description=(
                    "Use the File menu to open/save projects \u2003"
                    "and load demo data.\n\n"
                    "Use the Mode menu to switch between "
                    "Undergraduate (UG) and Postgraduate (PG). "
                    "PG unlocks RACI, SWOT, PESTEL, DPCI, "
                    "Charter Mgr, and RCPS Crashing."
                ),
                on_enter=lambda: nb._select_group("L1 \u00b7 Foundations"),
            ),
            TutorialStep(
                widget_fn=lambda: nb._sidebar,
                title="That's It!",
                description=(
                    "You're ready to go! Work through the sidebar from "
                    "L1 to L10 as you progress through the course, "
                    "or load a demo from File > Load Demo.\n\n"
                    "Press F1 at any time to replay this tutorial."
                ),
            ),
        ]
        return steps

    def _start_tutorial(self) -> None:
        """Launch the interactive tutorial overlay (UG mode only)."""
        if self.config.mode == "PG":
            messagebox.showinfo(
                "Tutorial",
                "The tutorial is designed for UG mode.\n"
                "Switch to Mode → Undergraduate to use it.")
            return
        is_pg = self.config.mode == "PG"
        self._tutorial = TutorialOverlay(
            self.root, self._build_tutorial_steps())
        self._tutorial.start(
            filter_fn=lambda s: s.group != "pg" or is_pg
        )

    def _apply_mode(self, mode: str):
        """Swap UG ↔ PG notebooks and update all tab-instance references."""
        mode = mode.upper()
        self.config.mode = mode
        self.config.save()
        self._mode_var.set(mode)

        # ── Select the correct store and show its notebook ───────
        if mode == "UG":
            store = self._ug_store
            if hasattr(self, "notebook_pg"):
                self.notebook_pg.pack_forget()
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            store = self._pg_store
            self.notebook.pack_forget()
            self.notebook_pg.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Swap tab-instance attributes ─────────────────────────
        for attr, obj in store["attrs"].items():
            setattr(self, attr, obj)
        self.tabs = store["tabs"]
        self._widget_to_tab = store["widget_to_tab"]
        self._pg_only_widgets = store["pg_only_widgets"]

        # ── In UG mode hide PG-only tabs in the UG notebook ──────
        if mode == "UG":
            for widget in self._pg_only_widgets:
                try:
                    self.notebook.tab(widget, state="hidden")
                except Exception:
                    pass

        # ── Notify active tabs ────────────────────────────────────
        for tab in self.tabs.values():
            if hasattr(tab, "set_mode"):
                tab.set_mode(mode)

        suffix = "[UG]" if mode == "UG" else "[PG]"
        dirty = " [unsaved]" if self.state.is_dirty() else ""
        self.root.title(f"PMhelper Edu {suffix}{dirty}")

    def _on_state_change(self):
        mode = self.config.mode
        suffix = "[UG]" if mode == "UG" else "[PG]"
        self.root.title(f"PMhelper Edu {suffix} [unsaved]")

    def _on_tab_changed(self, event):
        """Handle tab change in any group — call on_tab_selected."""
        nb = self._active_nb
        if nb._active_group is None:
            return
        grp = nb._groups[nb._active_group]
        try:
            sel = grp.notebook.select()
            if not sel:
                return
            widget = grp.notebook.nametowidget(sel)
            tab = self._widget_to_tab.get(id(widget))
            if tab is not None and hasattr(tab, "on_tab_selected"):
                tab.on_tab_selected()
        except Exception:
            pass

    def _on_closing(self):
        if self.state.is_dirty():
            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Save before closing?")
            if answer is None:  # Cancel
                return
            if answer:  # Yes
                self._save_project()
        self.root.destroy()

    def _new_project(self):
        """Reset to a fresh empty project."""
        if self.state.is_dirty():
            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save current project before creating a new one?")
            if answer is None:
                return
            if answer:
                self._save_project()

        proj, reg = make_empty_project()
        self.state.evm_project = proj
        self.state.risk_register = reg
        self.state.mc_results = None
        self.state.current_file_path = None
        self.state.mark_clean()
        # Reset analysis state
        self.results_data = None
        self.last_analysis_results = None
        self.current_data = None
        # Clear CPM Input table
        self._input_tab_edu.clear_all_without_confirmation()
        # Clear Gantt analysis data so it shows empty state
        if hasattr(self._gantt_tab_edu, '_results_data'):
            self._gantt_tab_edu._results_data = None
        self._apply_mode(self.config.mode)
        # Refresh ALL edu tabs so every panel resets
        self._refresh_all_edu_tabs()
        # Reset schedule stepper
        if hasattr(self._input_tab_edu, '_stepper'):
            self._input_tab_edu._stepper.refresh()

    def _open_project(self):
        """Open a .pmproj file."""
        if self.state.is_dirty():
            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save current project before opening another?")
            if answer is None:
                return
            if answer:
                self._save_project()

        filepath = filedialog.askopenfilename(
            title="Open Project",
            defaultextension=_PROJ_EXT,
            filetypes=[("PMhelper Project", f"*{_PROJ_EXT}"),
                       ("JSON files", "*.json"),
                       ("All files", "*.*")])
        if not filepath:
            return

        try:
            data = load_full_project(filepath)
        except (FileNotFoundError, ValueError) as exc:
            messagebox.showerror("Open Error", str(exc))
            return

        self.state.evm_project = data["evm_project"] or make_empty_project()[0]
        self.state.risk_register = data["risk_register"]
        self.state.mc_results = data["mc_results"]
        self.state.swot_analysis = data.get("swot_analysis")
        self.state.pestel_analysis = data.get("pestel_analysis")
        self.state.wbs_tree = data.get("wbs_tree")
        self.state.raci_task = data.get("raci_task")
        self.state.raci_deliv = data.get("raci_deliv")
        self.state.current_file_path = filepath
        self.state.mark_clean()

        # Restore mode from file if present
        saved_mode = data.get("app_config", {}).get("mode", self.config.mode)
        self._apply_mode(saved_mode)

        # Re-populate CPM/PERT Input table
        cpm_activities = data.get("cpm_activities", [])
        cpm_mode = data.get("cpm_mode", "deterministic")
        if cpm_activities:
            self._input_tab_edu.load_activities(cpm_activities, cpm_mode)

        # Update config
        self.config.last_project_path = filepath
        self.config.add_recent_file(filepath)
        self.config.save()
        self._rebuild_recent_menu()

        self._refresh_all_edu_tabs()

    def _save_project(self):
        """Save project to current path, or prompt for a path."""
        if self.state.current_file_path:
            self._do_save(self.state.current_file_path)
        else:
            self._save_project_as()

    def _save_project_as(self):
        """Prompt for a file path, then save."""
        filepath = filedialog.asksaveasfilename(
            title="Save Project As",
            defaultextension=_PROJ_EXT,
            filetypes=[("PMhelper Project", f"*{_PROJ_EXT}"),
                       ("JSON files", "*.json"),
                       ("All files", "*.*")])
        if filepath:
            self._do_save(filepath)

    def _do_save(self, filepath: str):
        """Perform the actual save operation."""
        try:
            # Store current mode + CPM activities in state for serialisation
            self.state._mode = self.config.mode
            self.state._cpm_activities = self._input_tab_edu.get_activities_data()
            self.state._cpm_mode = getattr(self._input_tab_edu, 'current_mode',
                                           'deterministic')
            # Sync RACI grid → state before serialising
            if hasattr(self, '_raci_tab'):
                self._raci_tab.sync_to_state()
            save_full_project(self.state, filepath)
            self.state.current_file_path = filepath
            self.state.mark_clean()
            self.config.last_project_path = filepath
            self.config.save()
            self._apply_mode(self.config.mode)  # refresh title
            self.config.add_recent_file(filepath)
            self.config.save()
            self._rebuild_recent_menu()
        except Exception as exc:
            messagebox.showerror("Save Error", str(exc))

    _DEMO_FILES = {
        ("ug", "small"): "office_renovation_ug.pmproj",
        ("ug", "medium"): "hospital_construction_ug_medium.pmproj",
        ("ug", "large"): "campus_construction_ug_large.pmproj",
        ("pg", "small"): "software_development_pg.pmproj",
        ("pg", "medium"): "digital_transformation_pg_medium.pmproj",
        ("pg", "large"): "erp_implementation_pg_large.pmproj",
    }

    def _load_demo(self, level: str, size: str = "small"):
        """Load a built-in demo dataset."""
        if self.state.is_dirty():
            answer = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save current project before loading demo data?")
            if answer is None:
                return
            if answer:
                self._save_project()

        # Look for demo files in the demos directory
        demo_dir = os.path.join(os.path.dirname(__file__), "..", "demos_edu")
        filename = self._DEMO_FILES.get((level.lower(), size.lower()))
        if not filename:
            messagebox.showerror("Demo Error", f"Unknown demo: {level}/{size}")
            return
        demo_file = os.path.join(demo_dir, filename)

        if not os.path.exists(demo_file):
            messagebox.showinfo(
                "Demo Data",
                f"Demo file not found:\n{demo_file}\n\n"
                "Demo datasets will be created shortly.")
            return

        try:
            data = load_full_project(demo_file)
        except Exception as exc:
            messagebox.showerror("Demo Load Error", str(exc))
            return

        self.state.evm_project = data["evm_project"] or make_empty_project()[0]
        self.state.risk_register = data["risk_register"]
        self.state.mc_results = data["mc_results"]
        self.state.swot_analysis = data.get("swot_analysis")
        self.state.pestel_analysis = data.get("pestel_analysis")
        self.state.wbs_tree = data.get("wbs_tree")
        self.state.raci_task = data.get("raci_task")
        self.state.raci_deliv = data.get("raci_deliv")
        self.state.current_file_path = None  # demos are not saved
        self.state.mark_clean()

        # Re-populate CPM/PERT Input table from demo data
        cpm_activities = data.get("cpm_activities", [])
        cpm_mode = data.get("cpm_mode", "deterministic")
        if cpm_activities:
            self._input_tab_edu.load_activities(cpm_activities, cpm_mode)

        target_mode = "UG" if level.lower() == "ug" else "PG"
        self._apply_mode(target_mode)
        self._refresh_all_edu_tabs()

    def _export_all_charts(self):
        """Export all chart figures from all tabs."""
        export_all_charts_dialog(self.tabs, parent=self.root)

    def _refresh_current_tab(self):
        """Trigger on_tab_selected for the currently visible tab."""
        try:
            self._on_tab_changed(None)
        except Exception:
            pass

    def _refresh_all_edu_tabs(self):
        """Refresh every edu tab so loaded/reset data is reflected."""
        for tab in self.tabs.values():
            try:
                if hasattr(tab, "on_tab_selected"):
                    tab.on_tab_selected()
            except Exception:
                pass

    # ================================================================
    #  CPM / PERT Analysis
    # ================================================================

    def analyze_project(self):
        """Run CPM/PERT analysis on the activities data."""
        # Determine mode from input tab
        input_mode = getattr(
            self._input_tab_edu,
            'current_mode',
            'deterministic')
        if input_mode == 'probabilistic' and self.pert_analyzer:
            self.current_analyzer = self.pert_analyzer
            self.analysis_mode = 'probabilistic'
        else:
            self.current_analyzer = self.cpm_analyzer
            self.analysis_mode = 'deterministic'

        _t0 = _time.time()

        activities_data = self._input_tab_edu.get_activities_data()
        if not activities_data:
            messagebox.showwarning(
                "Analysis",
                "No activity data to analyze.\n"
                "Please enter or load activities first.")
            return

        print(
            f"[analyze_project {
                _time.time() -
                _t0:.3f}s] activities data loaded ({
                len(activities_data)} activities)")

        try:
            G, critical_paths, critical_activities = \
                self.current_analyzer.analyze(activities_data)
        except Exception as exc:
            messagebox.showerror("Analysis Error",
                                 f"Analysis failed:\n{exc}")
            return

        print(
            f"[analyze_project {
                _time.time() -
                _t0:.3f}s] analyze() complete")

        # Store analyzer reference
        if self.analysis_mode == 'probabilistic':
            self.pert_analyzer = self.current_analyzer
        else:
            self.cpm_analyzer = self.current_analyzer

        # Project duration = max EF across all real nodes
        project_duration = 0
        for node in G.nodes():
            if node not in ('START', 'END') and 'EF' in G.nodes[node]:
                ef = G.nodes[node]['EF']
                if ef > project_duration:
                    project_duration = ef

        critical_path = critical_paths[0] if critical_paths else []

        # Build enriched activities list
        activities_for_display = []
        for node in G.nodes():
            if node in ('START', 'END'):
                continue
            nd = G.nodes[node]
            preds = [p for p in G.predecessors(node) if p != 'START']
            activity = {
                'id': node,
                'name': nd.get('activity', node),
                'duration': nd.get('duration', 0),
                'ES': nd.get('ES', 0),
                'EF': nd.get('EF', 0),
                'LS': nd.get('LS', 0),
                'LF': nd.get('LF', 0),
                'float': nd.get('float', 0),
                'critical': node in critical_activities,
                'predecessors': ', '.join(preds),
                'resource': nd.get('resource_demand', 0),
            }
            if self.analysis_mode == 'probabilistic':
                exp = nd.get('expected_duration',
                             nd.get('duration', 0))
                activity.update({
                    'optimistic': nd.get('optimistic', 0),
                    'most_likely': nd.get('most_likely', 0),
                    'pessimistic': nd.get('pessimistic', 0),
                    'expected_duration': exp,
                    'expected': math.ceil(exp) if isinstance(exp, float) else exp,
                    'variance': round(nd.get('variance', 0), 3),
                })
            activities_for_display.append(activity)

        # Build results dict
        self.results_data = {
            'graph': G,
            'critical_paths': critical_paths,
            'critical_path': critical_path,
            'critical_activities': critical_activities,
            'activities_data': activities_data,
            'activities': activities_for_display,
            'project_duration': project_duration,
        }

        # PERT-specific results
        if self.analysis_mode == 'probabilistic' and self.pert_analyzer:
            self.results_data.update({
                'expected_duration': getattr(
                    self.pert_analyzer, 'expected_duration',
                    project_duration),
                'project_variance': getattr(
                    self.pert_analyzer, 'project_variance', 0),
                'standard_deviation': getattr(
                    self.pert_analyzer, 'project_std', 0),
            })

        self.last_analysis_results = self.results_data

        # Store on shared state for dashboard access
        self.state.results_data = self.results_data

        # Build DataFrame for RCPS compatibility
        try:
            import pandas as pd
            rows = []
            for act in activities_for_display:
                rows.append({
                    'id': act['id'],
                    'activity': act['name'],
                    'early_start': act['ES'],
                    'early_finish': act['EF'],
                    'late_start': act['LS'],
                    'late_finish': act['LF'],
                    'float': act['float'],
                    'duration': act['duration'],
                    'resource': act.get('resource', 0),
                    'predecessors': act.get('predecessors', ''),
                    'critical': act['critical'],
                })
            self.current_data = pd.DataFrame(rows)
        except ImportError:
            self.current_data = None

        print(
            f"[analyze_project {
                _time.time() -
                _t0:.3f}s] results dict + DataFrame built")

        # ---- Update tabs with results ----
        # Critical tabs updated immediately (user is switching to Results).
        try:
            self.results_tab.update_results(
                self.results_data, self.analysis_mode)
        except Exception:
            pass
        print(
            f"[analyze_project {
                _time.time() -
                _t0:.3f}s] results_tab updated")

        # Remaining tabs are deferred via after(0) so the event-loop
        # stays responsive between each heavy redraw.  Each step
        # schedules the next, forming a lightweight chain.
        _rd = self.results_data
        _am = self.analysis_mode

        def _step_network():
            try:
                self.network_tab.update_network(_rd, _am)
            except Exception:
                pass
            print(
                f"[analyze_project {
                    _time.time() -
                    _t0:.3f}s] network_tab updated")
            self.root.after(0, _step_pert_diagram)

        def _step_pert_diagram():
            try:
                self.pert_diagram_tab.update_network(_rd, _am)
            except Exception:
                pass
            print(
                f"[analyze_project {
                    _time.time() -
                    _t0:.3f}s] pert_diagram_tab updated")
            self.root.after(0, _step_gantt)

        def _step_gantt():
            if hasattr(self._gantt_tab_edu, 'update_from_analysis'):
                try:
                    self._gantt_tab_edu.update_from_analysis(_rd, _am)
                except Exception:
                    pass
            print(
                f"[analyze_project {
                    _time.time() -
                    _t0:.3f}s] gantt_tab updated")
            self.root.after(0, _step_secondary)

        def _step_secondary():
            try:
                self._evm_tab.on_tab_selected()
            except Exception:
                pass
            print(
                f"[analyze_project {
                    _time.time() -
                    _t0:.3f}s] evm_tab updated")
            try:
                self._dashboard_tab.on_tab_selected()
            except Exception:
                pass
            print(
                f"[analyze_project {
                    _time.time() -
                    _t0:.3f}s] dashboard_tab updated")
            if _am == 'probabilistic':
                try:
                    if hasattr(self._probability_tab, 'update_from_analysis'):
                        self._probability_tab.update_from_analysis(_rd, _am)
                    else:
                        self._probability_tab.on_tab_selected()
                except Exception:
                    pass
                print(
                    f"[analyze_project {
                        _time.time() -
                        _t0:.3f}s] probability_tab updated")
            print(
                f"[analyze_project {
                    _time.time() -
                    _t0:.3f}s] DONE (deferred)")
            # Refresh schedule stepper (Step 5 -> green)
            if hasattr(self._input_tab_edu, '_stepper'):
                self._input_tab_edu._stepper.refresh()
            # Show completion dialog after all tabs are updated
            messagebox.showinfo(
                "Analysis Complete",
                f"Analysis completed successfully!\n\n"
                f"Mode: {_am.title()}\n"
                f"Project Duration: {project_duration}\n"
                f"Critical Activities: {len(critical_activities)}\n"
                f"Critical Path: {' \u2192 '.join(str(n) for n in critical_path)}")

        self.root.after(0, _step_network)

        # Switch to Results tab immediately — deferred updates happen
        # in the background between event-loop ticks.
        try:
            self._active_nb.select_tab(self.results_tab.results_frame)
        except Exception:
            pass

    def update_gantt_chart_after_analysis(self, results_data):
        """Called by original flow \u2014 delegate to edu Gantt."""
        if hasattr(self._gantt_tab_edu, 'update_from_analysis'):
            self._gantt_tab_edu.update_from_analysis(
                results_data, self.analysis_mode)

    # ================================================================
    #  Facade methods for real tab compatibility
    # ================================================================

    def get_activities_data(self):
        """Delegate to input tab."""
        return self._input_tab_edu.get_activities_data()

    def set_analysis_mode(self, mode):
        """Set the analysis mode (deterministic/probabilistic)."""
        if mode == 'probabilistic' and self.pert_analyzer:
            self.current_analyzer = self.pert_analyzer
        else:
            self.current_analyzer = self.cpm_analyzer
        self.analysis_mode = mode

    def run_cpm_analysis(self):
        """Run CPM analysis (deterministic)."""
        self.set_analysis_mode('deterministic')
        self.analyze_project()

    def set_status(self, msg):
        """Status bar update \u2014 no-op in edu edition."""

    def show_network_tab_help(self):
        """Help dialog for Network Diagram tab."""
        messagebox.showinfo(
            "Network Diagram Help",
            "The Network Diagram shows the project network with "
            "activities as nodes and dependencies as edges.\n\n"
            "Critical path activities are highlighted in red.\n"
            "Use the checkboxes to toggle display of times, float, "
            "and critical path.")

    def show_results_tab_help(self):
        """Help dialog for Results tab."""
        messagebox.showinfo(
            "Results Help",
            "The Results tab shows the CPM/PERT analysis output:\n\n"
            "\u2022 Project summary (duration, critical path)\n"
            "\u2022 Activity details (ES, EF, LS, LF, float)\n"
            "\u2022 Critical path sequence")

    def show_gantt_tab_help(self):
        """Help dialog for Gantt Chart tab."""
        messagebox.showinfo(
            "Gantt Chart Help",
            "The Gantt Chart shows activities as horizontal bars.\n\n"
            "\u2022 Red bars = Critical path activities\n"
            "\u2022 Blue bars = Non-critical activities\n"
            "\u2022 Grey extensions = Available float/slack")

    def show_crashing_tab_help(self):
        """Help dialog for Crashing tab."""
        messagebox.showinfo(
            "Crashing Help",
            "Crashing analysis finds the optimal way to reduce "
            "project duration by allocating additional resources.\n\n"
            "Run CPM analysis first, then use this tab to "
            "crash activities.")

    def show_probability_tab_help(self):
        """Help dialog for Probability tab."""
        messagebox.showinfo(
            "Probability Help",
            "The Probability tab provides:\n\n"
            "\u2022 PERT Analysis — completion probability, risk metrics, "
            "distribution / cumulative / sensitivity charts\n"
            "\u2022 Monte Carlo — simulation-based duration & cost "
            "distributions with P50/P80/P90 lines")

    def show_charter_tab_help(self):
        """Help dialog for Charter tab."""
        messagebox.showinfo(
            "Charter Help",
            "The Charter tab lets you create, edit, and export "
            "project charters.\n\n"
            "\u2022 Use templates for quick start\n"
            "\u2022 Fill in scope, objectives, stakeholders, etc.\n"
            "\u2022 Export to PDF\n\n"
            "The Charter Manager lists saved charters for "
            "quick access.")
