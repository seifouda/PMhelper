"""
PMhelper Edu — Main Window.
This is a COPY of main_window.py, modified for the Edu edition.
The original main_window.py is NEVER touched.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import math

from pmhelper.gui.edu_state import EduProjectState, AppConfig
from pmhelper.utils.project_io_edu import (
    save_full_project, load_full_project, make_empty_project,
)
from pmhelper.utils.chart_export_edu import export_all_charts_dialog
from pmhelper.core.cpm_analyzer import CPMAnalyzer

try:
    from pmhelper.core.pert_analyzer import PERTAnalyzer
    HAS_PERT = True
except ImportError:
    HAS_PERT = False


# PG-only tabs — hidden in UG mode
_PG_ONLY_TABS = {"probability", "rcps", "rcps_crashing", "charter", "charter_mgr", "dpci",
                  "swot", "pestel", "wbs"}

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
        file_menu.add_command(label="Open Project...", command=self._open_project)
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
            label="UG Demo — Large (600 tasks)",
            command=lambda: self._load_demo("ug", "large"))
        demo_menu.add_separator()
        demo_menu.add_command(
            label="PG Demo — Small (12 tasks)",
            command=lambda: self._load_demo("pg", "small"))
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

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Import Edu tab modules
        from pmhelper.gui.tabs.input_tab_edu import InputTabEdu
        from pmhelper.gui.tabs.gantt_tab_edu import GanttTabEdu
        from pmhelper.gui.tabs.evm_tab_edu import EVMTabEdu
        from pmhelper.gui.tabs.risk_tab_edu import RiskTabEdu
        from pmhelper.gui.tabs.probability_tab_edu import ProbabilityTabEdu
        from pmhelper.gui.tabs.rcps_tab_edu import RCPSTabEdu
        from pmhelper.gui.tabs.dashboard_tab_edu import DashboardTabEdu

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

        # ----------------------------------------------------------
        # Create tabs in display order.
        # Real tabs add themselves to the notebook during construction.
        # Edu tabs are added manually afterwards.
        # ----------------------------------------------------------

        # 1. Input Activities (edu) — manually add
        self._input_tab_edu = InputTabEdu(
            self.notebook, self.state, main_window=self)
        self.input_tab = self._input_tab_edu          # alias for real-tab compat
        self.notebook.add(self._input_tab_edu.frame, text="Input Activities")

        # 2. Results (real) — adds itself as "Results"
        self.results_tab = ResultsTab(self.notebook, self)

        # 3. Network Diagram (real) — adds itself as "Network Diagram"
        self.network_tab = NetworkTab(self.notebook, self)

        # 4. PERT Diagram (real) — adds itself as "PERT Diagram"
        self.pert_diagram_tab = PertDiagramTab(self.notebook, self)

        # 5. Gantt Chart (edu, enhanced with CPM rendering) — manually add
        self._gantt_tab_edu = GanttTabEdu(self.notebook, self.state,
                                          main_window=self)
        self.gantt_tab = self._gantt_tab_edu
        self.notebook.add(self._gantt_tab_edu.frame, text="Gantt Chart")

        # 6. EVM Dashboard (edu) — manually add
        self._evm_tab = EVMTabEdu(self.notebook, self.state)
        self.notebook.add(self._evm_tab.frame, text="EVM Dashboard")

        # 7. Risk Analysis (edu) — manually add
        self._risk_tab = RiskTabEdu(self.notebook, self.state)
        self.notebook.add(self._risk_tab.frame, text="Risk Analysis")

        # 8. Probability / Monte Carlo (edu, PG-only) — manually add
        self._probability_tab = ProbabilityTabEdu(self.notebook, self.state,
                                                   main_window=self)
        self.notebook.add(self._probability_tab.frame, text="Probability")

        # 9. Crashing (real) — ttk.Frame, add externally
        self.crashing_tab = CrashingTab(self.notebook, self)
        self.notebook.add(self.crashing_tab, text="Crashing")

        # 10. Resources / Cost Histograms (edu, PG-only) — manually add
        self._rcps_tab = RCPSTabEdu(self.notebook, self.state, main_window=self)
        self.notebook.add(self._rcps_tab.frame, text="Resources")

        # 11. RCPS Crashing (real, PG-only) — ttk.Frame, add externally
        self._rcps_crashing_tab = RCPSCrashingTab(self.notebook, self)
        self.notebook.add(self._rcps_crashing_tab, text="RCPS Crash")

        # 12. Dashboard (edu) — manually add
        self._dashboard_tab = DashboardTabEdu(self.notebook, self.state)
        self.notebook.add(self._dashboard_tab.frame, text="Dashboard")

        # 13. Charter (real, PG-only) — ttk.Frame, add externally
        self._charter_tab = CharterTab(self.notebook, self)
        self.notebook.add(self._charter_tab, text="Charter")

        # 14. Charter Manager (real, PG-only) — ttk.Frame, add externally
        self.charter_manager = CharterManager(
            self.notebook,
            on_open_callback=self._charter_tab.load_charter_from_file,
            on_duplicate_callback=self._charter_tab.load_charter_from_file,
        )
        self.notebook.add(self.charter_manager, text="Charter Mgr")

        # 15. DPCI Assessment (real, PG-only) — ttk.Frame, add externally
        self._dpci_tab = DPCITab(self.notebook)
        self.notebook.add(self._dpci_tab, text="DPCI")

        # 16. SWOT Analysis (edu, PG-only) — manually add
        self._swot_tab = SWOTTabEdu(self.notebook, self.state)
        self.notebook.add(self._swot_tab.frame, text="SWOT")

        # 17. PESTEL Analysis (edu, PG-only) — manually add
        self._pestel_tab = PESTELTabEdu(self.notebook, self.state)
        self.notebook.add(self._pestel_tab.frame, text="PESTEL")

        # 18. WBS Diagram (edu, PG-only) — manually add
        self._wbs_tab = WBSTabEdu(self.notebook, self.state)
        self.notebook.add(self._wbs_tab.frame, text="WBS")

        # Wire RCPS Crashing ↔ RCPS bidirectional link
        self._rcps_crashing_tab.set_rcps_tab_reference(self._rcps_tab)

        # Ordered list of ALL tab objects (matches notebook tab indices)
        self._all_tabs_ordered = [
            self._input_tab_edu,      # 0  Input Activities
            self.results_tab,         # 1  Results
            self.network_tab,         # 2  Network Diagram
            self.pert_diagram_tab,    # 3  PERT Diagram
            self._gantt_tab_edu,      # 4  Gantt Chart
            self._evm_tab,            # 5  EVM Dashboard
            self._risk_tab,           # 6  Risk Analysis
            self._probability_tab,    # 7  Probability
            self.crashing_tab,        # 8  Crashing
            self._rcps_tab,           # 9  Resources
            self._rcps_crashing_tab,  # 10 RCPS Crash
            self._dashboard_tab,      # 11 Dashboard
            self._charter_tab,        # 12 Charter
            self.charter_manager,     # 13 Charter Mgr
            self._dpci_tab,           # 14 DPCI
            self._swot_tab,           # 15 SWOT
            self._pestel_tab,         # 16 PESTEL
            self._wbs_tab,            # 17 WBS
        ]

        # Edu tabs dict for set_mode / on_tab_selected / get_figures
        self.tabs = {
            "input":          self._input_tab_edu,
            "gantt":          self._gantt_tab_edu,
            "evm":            self._evm_tab,
            "risk":           self._risk_tab,
            "probability":    self._probability_tab,
            "rcps":           self._rcps_tab,
            "rcps_crashing":  self._rcps_crashing_tab,
            "dashboard":      self._dashboard_tab,
            "charter":        self._charter_tab,
            "charter_mgr":    self.charter_manager,
            "dpci":           self._dpci_tab,
            "swot":           self._swot_tab,
            "pestel":         self._pestel_tab,
            "wbs":            self._wbs_tab,
        }

        # PG-only tab widget references for show/hide
        self._pg_only_widgets = [
            self._probability_tab.frame,   # Probability
            self._rcps_tab.frame,          # Resources
            self._rcps_crashing_tab,        # RCPS Crash
            self._charter_tab,             # Charter
            self.charter_manager,          # Charter Mgr
            self._dpci_tab,                # DPCI
            self._swot_tab.frame,          # SWOT
            self._pestel_tab.frame,        # PESTEL
            self._wbs_tab.frame,           # WBS
        ]

        # Auto-recalculate on tab switch
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _apply_mode(self, mode: str):
        """Show/hide PG-only features across all tabs."""
        mode = mode.upper()
        self.config.mode = mode
        self.config.save()
        self._mode_var.set(mode)

        # Notify edu tabs that support set_mode
        for tab in self.tabs.values():
            if hasattr(tab, "set_mode"):
                tab.set_mode(mode)

        # Show/hide PG-only tabs in the notebook
        for widget in self._pg_only_widgets:
            try:
                if mode == "PG":
                    self.notebook.tab(widget, state="normal")
                else:
                    self.notebook.tab(widget, state="hidden")
            except Exception:
                pass

        suffix = "[UG]" if mode == "UG" else "[PG]"
        dirty = " [unsaved]" if self.state.is_dirty() else ""
        self.root.title(f"PMhelper Edu {suffix}{dirty}")

    def _on_state_change(self):
        mode = self.config.mode
        suffix = "[UG]" if mode == "UG" else "[PG]"
        self.root.title(f"PMhelper Edu {suffix} [unsaved]")

    def _on_tab_changed(self, event):
        selected = self.notebook.index(self.notebook.select())
        if selected < len(self._all_tabs_ordered):
            tab = self._all_tabs_ordered[selected]
            if hasattr(tab, "on_tab_selected"):
                tab.on_tab_selected()

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
        ("ug", "large"): "campus_construction_ug_large.pmproj",
        ("pg", "small"): "software_development_pg.pmproj",
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
            selected = self.notebook.index(self.notebook.select())
            if selected < len(self._all_tabs_ordered):
                tab = self._all_tabs_ordered[selected]
                if hasattr(tab, "on_tab_selected"):
                    tab.on_tab_selected()
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
        input_mode = getattr(self._input_tab_edu, 'current_mode', 'deterministic')
        if input_mode == 'probabilistic' and self.pert_analyzer:
            self.current_analyzer = self.pert_analyzer
            self.analysis_mode = 'probabilistic'
        else:
            self.current_analyzer = self.cpm_analyzer
            self.analysis_mode = 'deterministic'

        activities_data = self._input_tab_edu.get_activities_data()
        if not activities_data:
            messagebox.showwarning(
                "Analysis",
                "No activity data to analyze.\n"
                "Please enter or load activities first.")
            return

        try:
            G, critical_paths, critical_activities = \
                self.current_analyzer.analyze(activities_data)
        except Exception as exc:
            messagebox.showerror("Analysis Error",
                                 f"Analysis failed:\n{exc}")
            return

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

        # ---- Update all tabs with results ----
        try:
            self.results_tab.update_results(
                self.results_data, self.analysis_mode)
        except Exception:
            pass

        try:
            self.network_tab.update_network(
                self.results_data, self.analysis_mode)
        except Exception:
            pass

        try:
            self.pert_diagram_tab.update_network(
                self.results_data, self.analysis_mode)
        except Exception:
            pass

        # Update Gantt (edu) with CPM data
        if hasattr(self._gantt_tab_edu, 'update_from_analysis'):
            try:
                self._gantt_tab_edu.update_from_analysis(
                    self.results_data, self.analysis_mode)
            except Exception:
                pass

        # Refresh EVM tab (KPI values may now reflect CPM-synced tasks)
        try:
            self._evm_tab.on_tab_selected()
        except Exception:
            pass

        # Refresh Dashboard tab
        try:
            self._dashboard_tab.on_tab_selected()
        except Exception:
            pass

        # For PERT mode, update probability tab
        if self.analysis_mode == 'probabilistic':
            try:
                if hasattr(self._probability_tab, 'update_from_analysis'):
                    self._probability_tab.update_from_analysis(
                        self.results_data, self.analysis_mode)
                else:
                    self._probability_tab.on_tab_selected()
            except Exception:
                pass

        # Switch to Results tab (index 1)
        try:
            self.notebook.select(1)
        except Exception:
            pass

        messagebox.showinfo(
            "Analysis Complete",
            f"Analysis completed successfully!\n\n"
            f"Mode: {self.analysis_mode.title()}\n"
            f"Project Duration: {project_duration}\n"
            f"Critical Activities: {len(critical_activities)}\n"
            f"Critical Path: {' \u2192 '.join(str(n) for n in critical_path)}")

        # Refresh schedule stepper (Step 5 → green)
        if hasattr(self._input_tab_edu, '_stepper'):
            self._input_tab_edu._stepper.refresh()

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
        pass

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
