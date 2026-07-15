"""
PMhelper Edu — Risk Analysis Tab.
Sub-tab A: Risk Register (Treeview with CRUD, sorted by exposure).
Sub-tab B: Risk Matrix (5×5 Matplotlib heat map).
Sub-tab C: Assessment Matrix (5×5 discrete grid, Phase 6).
Sub-tab D: Response Planning (per-risk response form, Phase 6).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

from pmhelper.gui.widgets.sortable_treeview import enhance_treeview

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.colors as mcolors
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.risk_register_edu import (
    Risk, RiskCategory, RiskRegister,
    ResponseStrategy, risk_zone, zone_color,
)
from pmhelper.utils.risk_io_edu import export_to_csv, import_from_csv

# Plotly embed
try:
    from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame, WEBVIEW2_AVAILABLE
    from pmhelper.utils.plotly_charts import plotly_risk_matrix as _plotly_risk, PLOTLY_AVAILABLE as _PLT_AVAIL
    _PLOTLY_EMBED = WEBVIEW2_AVAILABLE and _PLT_AVAIL
except ImportError:
    _PLOTLY_EMBED = False


class RiskTabEdu:
    """Risk Analysis tab with Risk Register, Risk Matrix, Assessment Matrix,
    and Response Planning sub-tabs."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)
        self._selected_risk_id = None
        self._selected_response_risk_id = None
        self._render_mode_var = tk.StringVar(value="matplotlib")

        # Ensure state has a risk_register
        if self.state.risk_register is None:
            self.state.risk_register = RiskRegister(
                bac=self.state.evm_project.bac)

        # Inner Notebook for sub-tabs
        self._notebook = ttk.Notebook(self.frame)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sub-tab A: Risk Register
        self._register_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._register_frame, text="Risk Register")
        self._build_register_tab()

        # Sub-tab B: Risk Matrix
        self._matrix_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._matrix_frame, text="Risk Matrix")
        self._build_matrix_tab()

        # Sub-tab C: Assessment Matrix (Phase 6)
        self._assessment_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._assessment_frame, text="🟥 Assessment Matrix")
        self._build_assessment_tab()

        # Sub-tab D: Response Planning (Phase 6)
        self._response_frame = ttk.Frame(self._notebook)
        self._notebook.add(self._response_frame, text="🛡️ Response Planning")
        self._build_response_tab()

        # B1.1: refresh assessment canvas when its sub-tab is selected
        self._notebook.bind("<<NotebookTabChanged>>", self._on_subtab_changed)

    def _on_subtab_changed(self, _event=None):
        """Refresh the Assessment Matrix canvas when that sub-tab becomes visible."""
        idx = self._notebook.index("current")
        if idx == 2:  # Assessment Matrix is the 3rd tab (index 2)
            self.frame.update_idletasks()
            self._refresh_assessment_grid()
        elif idx == 3:  # Response Planning
            self._refresh_response_list()
            self._refresh_effectiveness()

    # ------------------------------------------------------------------
    # Sub-tab A: Risk Register
    # ------------------------------------------------------------------

    def _build_register_tab(self):
        # Toolbar
        toolbar = ttk.Frame(self._register_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Button(
            toolbar,
            text="Add Risk",
            command=self._add_risk).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Edit Risk",
            command=self._edit_risk).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Delete Risk",
            command=self._delete_risk).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="Import CSV",
            command=self._import_csv).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Export CSV",
            command=self._export_csv).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(toolbar, text="� Load Demo",
                   command=self._load_demo).pack(side=tk.LEFT, padx=2)
        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(toolbar, text="📖 Theory",
                   command=self._show_theory).pack(side=tk.LEFT, padx=2)
        self._worked_btn = ttk.Button(
            toolbar,
            text="📊 Show All Calculations",
            command=self._show_worked_solution)
        self._worked_btn.pack(side=tk.LEFT, padx=2)

        # Treeview with horizontal scrollbar
        tree_frame = ttk.Frame(self._register_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

        cols = ("id", "name", "category", "probability", "impact", "exposure",
                "score", "rank", "response", "flag")
        self._tree = ttk.Treeview(tree_frame, columns=cols,
                                  show="headings", selectmode="browse")
        self._tree.heading("id", text="ID")
        self._tree.heading("name", text="Name")
        self._tree.heading("category", text="Category")
        self._tree.heading("probability", text="Probability")
        self._tree.heading("impact", text="Impact ($)")
        self._tree.heading("exposure", text="Exposure ($)")
        self._tree.heading("score", text="Score",
                           command=lambda: self._sort_register("score"))
        self._tree.heading("rank", text="Rank")
        self._tree.heading("response", text="Response")
        self._tree.heading("flag", text="\u26a0")

        self._tree.column("id", width=60, anchor=tk.CENTER)
        self._tree.column("name", width=160)
        self._tree.column("category", width=80, anchor=tk.CENTER)
        self._tree.column("probability", width=80, anchor=tk.CENTER)
        self._tree.column("impact", width=90, anchor=tk.E)
        self._tree.column("exposure", width=90, anchor=tk.E)
        self._tree.column("score", width=55, anchor=tk.CENTER)
        self._tree.column("rank", width=40, anchor=tk.CENTER)
        self._tree.column("response", width=90, anchor=tk.CENTER)
        self._tree.column("flag", width=35, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(
            tree_frame,
            orient=tk.VERTICAL,
            command=self._tree.yview)
        hsb = ttk.Scrollbar(
            tree_frame,
            orient=tk.HORIZONTAL,
            command=self._tree.xview)
        self._tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._tree.pack(fill=tk.BOTH, expand=True)
        enhance_treeview(self._tree)

        # Footer
        self._footer_var = tk.StringVar(
            value="Total Exposure: $0  |  Contingency Reserve: $0  |  Flagged risks: 0")
        ttk.Label(
            self._register_frame,
            textvariable=self._footer_var,
            font=(
                "TkDefaultFont",
                9,
                "italic")).pack(
            fill=tk.X,
            padx=5,
            pady=(
                0,
                5))

    def _refresh_register_tree(self):
        """Refresh the treeview with current register data."""
        reg = self.state.risk_register
        if reg is None:
            return
        reg.recompute_exposures()
        reg.recompute_scores()
        reg.update_ranks()
        flagged_ids = {r.id for r in reg.flag_high_exposure()}
        sorted_risks = reg.risks_by_score()

        self._tree.delete(*self._tree.get_children())
        for r in sorted_risks:
            flag_text = "\u25b2" if r.id in flagged_ids else ""
            strat = r.response_strategy.value if r.response_strategy else ""
            self._tree.insert("", tk.END, iid=r.id, values=(
                r.id, r.name, r.category.value,
                f"{r.probability:.2f}",
                f"{r.impact:,.2f}",
                f"{r.exposure:,.2f}",
                f"{r.risk_score:.0f}",
                r.risk_rank,
                strat,
                flag_text,
            ))

        total = reg.total_exposure()
        contingency = reg.contingency_reserve()
        n_flagged = len(flagged_ids)
        self._footer_var.set(
            f"Total Exposure: ${total:,.2f}  |  "
            f"Contingency Reserve: ${contingency:,.2f}  |  "
            f"Flagged risks: {n_flagged}"
        )

    def _sort_register(self, col: str):
        """Sort register treeview by Score column."""
        reg = self.state.risk_register
        if reg is None:
            return
        reg.recompute_scores()
        reg.update_ranks()
        self._refresh_register_tree()

    def _show_theory(self):
        from pmhelper.core.risk_step_generator import risk_assessment_theory_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        WorkedSolutionWindow(
            self.frame,
            "Risk Assessment — Theory & Overview",
            risk_assessment_theory_steps(),
        )

    def _show_worked_solution(self):
        reg = self.state.risk_register
        if not reg or not reg.risks:
            messagebox.showinfo("Worked Solution", "Add risks first.")
            return
        from pmhelper.core.risk_step_generator import full_register_steps
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow
        WorkedSolutionWindow(
            self.frame,
            "Risk Register — Worked Solution",
            full_register_steps(reg),
        )

    def _add_risk(self):
        """Open dialog to add a new risk."""
        self._open_risk_dialog(None)

    def _edit_risk(self):
        """Open dialog to edit selected risk."""
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Edit Risk", "Select a risk to edit.")
            return
        risk_id = sel[0]
        risk = self.state.risk_register.get_risk(risk_id)
        if risk:
            self._open_risk_dialog(risk)

    def _delete_risk(self):
        """Delete the selected risk."""
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Delete Risk", "Select a risk to delete.")
            return
        risk_id = sel[0]
        if messagebox.askyesno("Delete Risk", f"Delete risk '{risk_id}'?"):
            self.state.risk_register.remove_risk(risk_id)
            self.state.mark_dirty()
            self._refresh_register_tree()

    def _open_risk_dialog(self, risk=None):
        """Open a Toplevel dialog for adding / editing a risk."""
        editing = risk is not None
        dlg = tk.Toplevel(self.frame)
        dlg.title("Edit Risk" if editing else "Add Risk")
        dlg.geometry("440x480")
        dlg.transient(self.frame)
        dlg.grab_set()

        row = 0
        ttk.Label(
            dlg,
            text="ID:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=10,
            pady=4)
        id_var = tk.StringVar(
            value=risk.id if editing else f"R{len(self.state.risk_register.risks) + 1:03d}")
        id_entry = ttk.Entry(dlg, textvariable=id_var, width=30)
        id_entry.grid(row=row, column=1, padx=10, pady=4)
        if editing:
            id_entry.configure(state="readonly")

        row += 1
        ttk.Label(
            dlg,
            text="Name:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=10,
            pady=4)
        name_var = tk.StringVar(value=risk.name if editing else "")
        ttk.Entry(
            dlg,
            textvariable=name_var,
            width=30).grid(
            row=row,
            column=1,
            padx=10,
            pady=4)

        row += 1
        ttk.Label(
            dlg,
            text="Description:").grid(
            row=row,
            column=0,
            sticky=tk.NW,
            padx=10,
            pady=4)
        desc_text = tk.Text(dlg, width=30, height=3)
        desc_text.grid(row=row, column=1, padx=10, pady=4)
        if editing:
            desc_text.insert("1.0", risk.description)

        row += 1
        ttk.Label(
            dlg,
            text="Category:").grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=10,
            pady=4)
        cat_var = tk.StringVar(
            value=risk.category.value if editing else RiskCategory.OTHER.value)
        cat_combo = ttk.Combobox(
            dlg, textvariable=cat_var, width=27, values=[
                c.value for c in RiskCategory], state="readonly")
        cat_combo.grid(row=row, column=1, padx=10, pady=4)

        row += 1
        ttk.Label(dlg, text="Probability (0-1):").grid(row=row,
                                                       column=0, sticky=tk.W, padx=10, pady=4)
        prob_var = tk.StringVar(
            value=f"{
                risk.probability:.2f}" if editing else "0.00")
        ttk.Entry(
            dlg,
            textvariable=prob_var,
            width=30).grid(
            row=row,
            column=1,
            padx=10,
            pady=4)

        row += 1
        ttk.Label(
            dlg,
            text="Impact ($):").grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=10,
            pady=4)
        imp_var = tk.StringVar(
            value=f"{
                risk.impact:.2f}" if editing else "0.00")
        ttk.Entry(
            dlg,
            textvariable=imp_var,
            width=30).grid(
            row=row,
            column=1,
            padx=10,
            pady=4)

        # Phase 6: 1-5 score fields
        ttk.Separator(dlg, orient=tk.HORIZONTAL).grid(
            row=row + 1, column=0, columnspan=2, sticky=tk.EW, padx=10, pady=6)
        row += 2
        ttk.Label(
            dlg,
            text="Prob. Score (1-5):",
            foreground="darkblue").grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=10,
            pady=4)
        ps_var = tk.StringVar(value=str(risk.prob_score if editing else 3))
        ttk.Combobox(
            dlg,
            textvariable=ps_var,
            width=5,
            values=[
                "1",
                "2",
                "3",
                "4",
                "5"],
            state="readonly").grid(
            row=row,
            column=1,
            sticky=tk.W,
            padx=10)

        row += 1
        ttk.Label(
            dlg,
            text="Impact Score (1-5):",
            foreground="darkblue").grid(
            row=row,
            column=0,
            sticky=tk.W,
            padx=10,
            pady=4)
        is_var = tk.StringVar(value=str(risk.impact_score if editing else 3))
        ttk.Combobox(
            dlg,
            textvariable=is_var,
            width=5,
            values=[
                "1",
                "2",
                "3",
                "4",
                "5"],
            state="readonly").grid(
            row=row,
            column=1,
            sticky=tk.W,
            padx=10)

        row += 1
        score_lbl = ttk.Label(dlg, text="", foreground="darkblue",
                              font=("TkDefaultFont", 9, "bold"))
        score_lbl.grid(row=row, column=0, columnspan=2, padx=10)

        def _update_score_preview(*_):
            try:
                s = int(ps_var.get()) * int(is_var.get())
                zone = risk_zone(s)
                score_lbl.config(text=f"Risk Score = {s}  ({zone})")
            except Exception:
                pass

        ps_var.trace_add("write", _update_score_preview)
        is_var.trace_add("write", _update_score_preview)
        _update_score_preview()

        def _save():
            try:
                prob = float(prob_var.get())
                impa = float(imp_var.get())
                cat = RiskCategory(cat_var.get())
                name = name_var.get().strip()
                desc = desc_text.get("1.0", tk.END).strip()
                rid = id_var.get().strip()
                psc = int(ps_var.get())
                isc = int(is_var.get())
                if not name:
                    messagebox.showerror("Validation", "Name is required.",
                                         parent=dlg)
                    return
                if not rid:
                    messagebox.showerror("Validation", "ID is required.",
                                         parent=dlg)
                    return
                if editing:
                    self.state.risk_register.update_risk(
                        risk.id, name=name, description=desc,
                        probability=prob, impact=impa, category=cat,
                        prob_score=psc, impact_score=isc)
                else:
                    new_risk = Risk(
                        id=rid,
                        name=name,
                        description=desc,
                        probability=prob,
                        impact=impa,
                        category=cat,
                        prob_score=psc,
                        impact_score=isc)
                    self.state.risk_register.add_risk(new_risk)
                self.state.mark_dirty()
                self._refresh_register_tree()
                dlg.destroy()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e), parent=dlg)

        row += 1
        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(
            btn_frame,
            text="Save",
            command=_save).pack(
            side=tk.LEFT,
            padx=5)
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=dlg.destroy).pack(
            side=tk.LEFT,
            padx=5)

    def _import_csv(self):
        """Import risks from CSV file."""
        from tkinter import filedialog
        filepath = filedialog.askopenfilename(
            title="Import Risk Register CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not filepath:
            return
        try:
            imported = import_from_csv(filepath)
            reg = self.state.risk_register
            for r in imported.risks:
                if not reg.get_risk(r.id):
                    reg.risks.append(r)
            reg.recompute_exposures()
            self.state.mark_dirty()
            self._refresh_register_tree()
            messagebox.showinfo("Import",
                                f"Imported {len(imported.risks)} risks.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _export_csv(self):
        """Export risks to CSV file."""
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            title="Export Risk Register CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not filepath:
            return
        try:
            export_to_csv(self.state.risk_register, filepath)
            messagebox.showinfo("Export", f"Exported to {filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def _load_demo(self):
        """Load the risk_assessment_demo.json into the Risk Register."""
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "data",
            "demos",
            "v2",
            "risk_assessment_demo.json")
        demo_path = os.path.normpath(demo_path)

        if not os.path.exists(demo_path):
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(
                    here, "data", "demos", "v2", "risk_assessment_demo.json")
                if os.path.exists(candidate):
                    demo_path = candidate
                    break
                here = os.path.dirname(here)

        if not os.path.exists(demo_path):
            messagebox.showerror(
                "Load Demo", f"Demo file not found:\n{demo_path}")
            return

        with open(demo_path, encoding="utf-8") as fh:
            demo = json.load(fh)

        rr_data = demo.get("risk_register", {})
        if not rr_data.get("risks"):
            messagebox.showinfo("Load Demo", "No risks in demo file.")
            return

        new_reg = RiskRegister.from_dict(rr_data)
        new_reg.recompute_exposures()
        new_reg.recompute_scores()
        new_reg.update_ranks()

        self.state.risk_register = new_reg
        self.state.mark_dirty()
        self.on_tab_selected()
        messagebox.showinfo(
            "Load Demo",
            f"Loaded {len(new_reg.risks)} risks with response plans.\n\n"
            "Check all 4 sub-tabs:\n"
            "• Risk Register — sorted risk list\n"
            "• Risk Matrix — 5×5 heat map\n"
            "• Assessment Matrix — zone grid\n"
            "• Response Planning — per-risk responses")

    # ------------------------------------------------------------------
    # Sub-tab B: Risk Matrix (5×5 Heat Map)
    # ------------------------------------------------------------------

    def _build_matrix_tab(self):
        if not HAS_MATPLOTLIB:
            ttk.Label(
                self._matrix_frame,
                text="Matplotlib not installed — Risk Matrix unavailable.").pack(
                expand=True)
            return

        # Top toolbar
        toolbar = ttk.Frame(self._matrix_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self._draw_matrix).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Export PNG",
            command=lambda: self._export_matrix("png")).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Export PDF",
            command=lambda: self._export_matrix("pdf")).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="\U0001f50d Open Interactive",
            command=self._open_matrix_interactive).pack(
            side=tk.LEFT,
            padx=6)

        # Renderer toggle
        if _PLOTLY_EMBED:
            rf = ttk.LabelFrame(toolbar, text="Renderer", padding="3")
            rf.pack(side=tk.LEFT, padx=(10, 0))
            ttk.Radiobutton(
                rf,
                text="Classic",
                value="matplotlib",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)
            ttk.Radiobutton(
                rf,
                text="\U0001f4ca Plotly",
                value="plotly",
                variable=self._render_mode_var,
                command=self._switch_renderer).pack(
                side=tk.LEFT,
                padx=4)

        # Matplotlib canvas
        self._mpl_matrix_frame = ttk.Frame(self._matrix_frame)
        self._mpl_matrix_frame.pack(fill=tk.BOTH, expand=True)
        self._fig = Figure(figsize=(6, 5), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(
            self._fig, master=self._mpl_matrix_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Plotly frame (hidden)
        self._plotly_frame = None
        if _PLOTLY_EMBED:
            self._plotly_frame = PlotlyChartFrame(self._matrix_frame)

        # Detail panel
        self._detail_var = tk.StringVar(
            value="Click a risk on the matrix for details.")
        ttk.Label(
            self._matrix_frame,
            textvariable=self._detail_var,
            font=(
                "TkDefaultFont",
                9)).pack(
            fill=tk.X,
            padx=5,
            pady=(
                0,
                5))

        # Empty-state label (shown/hidden as needed)
        self._empty_label = ttk.Label(
            self._matrix_frame,
            text="Add risks in the Risk Register tab to populate this matrix.")

        # Click handler
        self._canvas.mpl_connect("button_press_event", self._on_matrix_click)

    def _open_matrix_interactive(self):
        risks = self.state.risk_register.risks if self.state.risk_register else []
        if not risks:
            messagebox.showinfo("Interactive", "Add risks first.")
            return
        from pmhelper.utils.interactive_charts import open_chart_in_browser
        fig = _plotly_risk(risks)
        open_chart_in_browser(fig, "Risk Matrix")

    def _draw_matrix(self):
        """Draw the 5×5 risk heat map."""
        if self._render_mode_var.get() == "plotly" and getattr(self, '_plotly_frame', None):
            self._update_plotly_matrix()
            return
        if not HAS_MATPLOTLIB:
            return
        ax = self._ax
        ax.clear()

        reg = self.state.risk_register
        if reg is None or not reg.risks:
            ax.text(
                0.5,
                0.5,
                "No risks to display.\nAdd risks in the Risk Register tab.",
                ha="center",
                va="center",
                fontsize=12,
                color="grey",
                transform=ax.transAxes)
            self._canvas.draw()
            return

        reg.recompute_exposures()
        risks = reg.risks

        # Define grid bands
        prob_bands = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]  # 5 bands
        max_impact = max(r.impact for r in risks) if risks else 1.0
        if max_impact <= 0:
            max_impact = 1.0
        max_impact *= 1.1  # 10% headroom
        impact_step = max_impact / 5
        impact_bands = [i * impact_step for i in range(6)]

        # Build 5×5 score grid (probability_midpoint × impact_midpoint)
        score_grid = np.zeros((5, 5))
        for pi in range(5):
            p_mid = (prob_bands[pi] + prob_bands[pi + 1]) / 2
            for ii in range(5):
                i_mid = (impact_bands[ii] + impact_bands[ii + 1]) / 2
                score_grid[pi, ii] = p_mid * i_mid

        # Normalise scores for colour mapping
        max_score = score_grid.max() if score_grid.max() > 0 else 1.0
        normalised = score_grid / max_score

        # Custom colourmap: green → yellow → orange → red
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "risk", ["#27ae60", "#f1c40f", "#e67e22", "#e74c3c"])

        ax.pcolormesh(impact_bands, prob_bands, normalised, cmap=cmap,
                      edgecolors="white", linewidth=1.5, shading="flat")

        # Plot each risk as a numbered circle
        self._risk_positions = []  # store for click detection
        for idx, r in enumerate(risks, 1):
            x = min(r.impact, max_impact * 0.98)
            y = min(r.probability, 0.98)
            ax.plot(
                x,
                y,
                "o",
                color="white",
                markersize=18,
                markeredgecolor="black",
                markeredgewidth=1.2)
            ax.text(x, y, str(idx), ha="center", va="center", fontsize=8,
                    fontweight="bold", color="black")
            self._risk_positions.append((x, y, r))

        ax.set_xlabel("Impact ($)", fontsize=10)
        ax.set_ylabel("Probability", fontsize=10)
        ax.set_title(
            "Risk Matrix (5\u00d75 Heat Map)",
            fontsize=11,
            fontweight="bold")
        ax.set_xlim(0, max_impact)
        ax.set_ylim(0, 1.0)

        self._fig.tight_layout()
        self._canvas.draw()

    def _on_matrix_click(self, event):
        """Handle click on risk dot in matrix."""
        if event.xdata is None or event.ydata is None:
            return
        if not hasattr(self, "_risk_positions"):
            return
        # Find nearest risk
        best = None
        best_dist = float("inf")
        for (x, y, risk) in self._risk_positions:
            # Normalise distance (impact range vs probability range)
            dx = (event.xdata - x)
            dy = (event.ydata - y) * 100  # scale to comparable range
            d = (dx ** 2 + dy ** 2) ** 0.5
            if d < best_dist:
                best_dist = d
                best = risk
        if best is not None:
            flagged = best.id in {
                r.id for r in self.state.risk_register.flag_high_exposure()}
            flag_text = " [FLAGGED \u26a0]" if flagged else ""
            self._detail_var.set(
                f"{best.id}: {best.name}  |  Category: {best.category.value}  |  "
                f"Exposure: ${best.exposure:,.2f}{flag_text}"
            )

    def _export_matrix(self, fmt):
        """Export the risk matrix figure as PNG or PDF."""
        from tkinter import filedialog
        ext = f".{fmt}"
        filepath = filedialog.asksaveasfilename(
            title=f"Export Risk Matrix as {fmt.upper()}",
            defaultextension=ext,
            filetypes=[(f"{fmt.upper()} files", f"*{ext}"), ("All files", "*.*")])
        if filepath:
            self._fig.savefig(filepath, dpi=150, bbox_inches="tight")
            messagebox.showinfo("Export", f"Saved to {filepath}")

    # ------------------------------------------------------------------
    # Sub-tab C: Assessment Matrix (5×5 discrete grid)
    # ------------------------------------------------------------------

    # Zone colours and labels
    _ZONE_PALETTE = {
        "Critical": "#e74c3c",
        "High": "#e67e22",
        "Medium": "#f1c40f",
        "Low": "#27ae60",
    }

    def _build_assessment_tab(self):
        """Build the 5x5 discrete assessment matrix sub-tab."""
        # Top toolbar
        toolbar = ttk.Frame(self._assessment_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Button(toolbar, text="📖 Theory",
                   command=self._show_theory).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            toolbar,
            text="Refresh",
            command=self._refresh_assessment_grid).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(toolbar, text="Try It Yourself",
                   command=self._toggle_try_it).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🗺 Walkthrough",
                   command=self._toggle_walkthrough).pack(side=tk.LEFT, padx=2)

        # B8.1: Collapsible instruction strip
        self._instr_visible = True
        self._instr_toggle_btn = ttk.Button(
            toolbar, text="▲ Instructions",
            command=self._toggle_instructions)
        self._instr_toggle_btn.pack(side=tk.RIGHT, padx=2)

        self._instr_strip = ttk.Frame(self._assessment_frame,
                                      relief=tk.GROOVE, padding=4)
        self._instr_strip.pack(fill=tk.X, padx=5, pady=(0, 3))
        ttk.Label(
            self._instr_strip, text=(
                "The 5×5 Risk Assessment Matrix plots each risk by its Probability score (1–5, vertical) "
                "and Impact score (1–5, horizontal). The cell colour indicates the zone: "
                "Critical (red) = score ≥ 15, High (orange) = 10–14, Medium (yellow) = 5–9, Low (green) ≤ 4. "
                "Click any cell to list the risks it contains."), wraplength=700, justify=tk.LEFT, font=(
                "TkDefaultFont", 9, "italic"), ).pack(
            anchor=tk.W)

        # Main PanedWindow: matrix canvas | cell details
        pane = ttk.PanedWindow(self._assessment_frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: canvas + labels
        left = ttk.Frame(pane, width=440)
        pane.add(left, weight=3)

        # Zone legend strip
        leg = ttk.Frame(left)
        leg.pack(fill=tk.X, padx=5, pady=(2, 0))
        for zone, color in self._ZONE_PALETTE.items():
            f = tk.Frame(leg, bg=color, width=14, height=14)
            f.pack(side=tk.LEFT, padx=(0, 1))
            ttk.Label(leg, text=zone).pack(side=tk.LEFT, padx=(0, 8))

        # Y-axis label (rotated via Label trick)
        canvas_frame = ttk.Frame(left)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        y_label = ttk.Label(canvas_frame, text="← Probability Score →",
                            font=("TkDefaultFont", 9))
        y_label.pack(side=tk.LEFT, padx=(4, 0))

        # Canvas
        self._grid_canvas = tk.Canvas(canvas_frame, width=360, height=320,
                                      bg="#f5f5f5", highlightthickness=1,
                                      highlightbackground="#aaa")
        self._grid_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._grid_canvas.bind("<Button-1>", self._on_canvas_click)

        # X-axis label
        x_label = ttk.Label(left, text="← Impact Score →",
                            font=("TkDefaultFont", 9))
        x_label.pack(pady=(0, 4))

        # Right: details panel
        right = ttk.Frame(pane)
        pane.add(right, weight=2)

        # Zone summary
        zone_lf = ttk.LabelFrame(right, text="Zone Summary")
        zone_lf.pack(fill=tk.X, padx=5, pady=5)
        self._zone_vars = {}
        for zone in ("Critical", "High", "Medium", "Low"):
            row_f = ttk.Frame(zone_lf)
            row_f.pack(fill=tk.X, padx=5, pady=2)
            tk.Frame(row_f, bg=self._ZONE_PALETTE[zone],
                     width=14, height=14).pack(side=tk.LEFT, padx=(0, 4))
            ttk.Label(row_f, text=f"{zone}:").pack(side=tk.LEFT)
            var = tk.StringVar(value="0")
            ttk.Label(
                row_f, textvariable=var, font=(
                    "TkDefaultFont", 9, "bold")).pack(
                side=tk.LEFT, padx=4)
            self._zone_vars[zone] = var

        # Selected cell risks
        cell_lf = ttk.LabelFrame(right, text="Risks in Selected Cell")
        cell_lf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._cell_label_var = tk.StringVar(
            value="Click a cell to see its risks.")
        ttk.Label(
            cell_lf,
            textvariable=self._cell_label_var,
            font=(
                "TkDefaultFont",
                9,
                "italic")).pack(
            anchor=tk.W,
            padx=5,
            pady=2)

        cell_cols = ("id", "name", "score")
        self._cell_tree = ttk.Treeview(cell_lf, columns=cell_cols,
                                       show="headings", height=8)
        self._cell_tree.heading("id", text="ID")
        self._cell_tree.heading("name", text="Risk Name")
        self._cell_tree.heading("score", text="Score")
        self._cell_tree.column("id", width=50, anchor=tk.CENTER)
        self._cell_tree.column("name", width=150)
        self._cell_tree.column("score", width=50, anchor=tk.CENTER)
        self._cell_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        enhance_treeview(self._cell_tree)

        # "Try It Yourself" practice panel (hidden by default)
        self._try_it_visible = False
        self._try_it_frame = ttk.LabelFrame(self._assessment_frame,
                                            text="Try It Yourself")
        self._build_try_it_assessment()

        # B8.5: Narrated walkthrough panel (hidden by default)
        self._walkthrough_visible = False
        self._walkthrough_frame = ttk.LabelFrame(
            self._assessment_frame, text="🗺 Step-by-Step Walkthrough", padding=6)
        self._build_assessment_walkthrough()

    def _build_try_it_assessment(self):
        """Build the practice panel for assessment tab."""
        scenarios = [
            ("A critical vendor unexpectedly closes operations, impacting delivery.",
             4, 5, "Critical"),
            ("Minor scope ambiguity may cause rework on a non-critical module.",
             2, 2, "Low"),
            ("A key architect resigns mid-project, delaying design decisions.",
             3, 4, "High"),
        ]
        self._try_scenarios = scenarios
        self._try_idx = 0

        txt = ttk.Label(self._try_it_frame,
                        text="Rate the following risk and identify its zone:",
                        wraplength=600, justify=tk.LEFT)
        txt.pack(anchor=tk.W, padx=10, pady=4)

        self._try_scenario_var = tk.StringVar()
        ttk.Label(self._try_it_frame, textvariable=self._try_scenario_var,
                  wraplength=600, justify=tk.LEFT,
                  font=("TkDefaultFont", 10, "italic")).pack(
                      anchor=tk.W, padx=10, pady=(0, 6))

        ctrl = ttk.Frame(self._try_it_frame)
        ctrl.pack(anchor=tk.W, padx=10)
        ttk.Label(ctrl, text="Prob Score (1-5):").grid(row=0,
                                                       column=0, sticky=tk.W, padx=4)
        self._try_ps = tk.StringVar(value="3")
        ttk.Combobox(ctrl, textvariable=self._try_ps, width=4,
                     values=["1", "2", "3", "4", "5"],
                     state="readonly").grid(row=0, column=1, padx=4)
        ttk.Label(ctrl,
                  text="Impact Score (1-5):").grid(row=0,
                                                   column=2,
                                                   padx=12)
        self._try_is = tk.StringVar(value="3")
        ttk.Combobox(ctrl, textvariable=self._try_is, width=4,
                     values=["1", "2", "3", "4", "5"],
                     state="readonly").grid(row=0, column=3, padx=4)
        ttk.Button(
            ctrl,
            text="Check",
            command=self._check_try_it_assessment).grid(
            row=0,
            column=4,
            padx=12)
        ttk.Button(
            ctrl,
            text="Next",
            command=self._next_try_scenario).grid(
            row=0,
            column=5,
            padx=4)

        self._try_result_var = tk.StringVar()
        ttk.Label(
            self._try_it_frame,
            textvariable=self._try_result_var,
            font=(
                "TkDefaultFont",
                9,
                "bold")).pack(
            anchor=tk.W,
            padx=10,
            pady=4)
        self._load_try_scenario()

    def _load_try_scenario(self):
        s = self._try_scenarios[self._try_idx % len(self._try_scenarios)]
        self._try_scenario_var.set(s[0])
        self._try_result_var.set("")

    def _next_try_scenario(self):
        self._try_idx += 1
        self._load_try_scenario()

    def _check_try_it_assessment(self):
        _, exp_p, exp_i, exp_zone = self._try_scenarios[
            self._try_idx % len(self._try_scenarios)]
        try:
            ps = int(self._try_ps.get())
            is_ = int(self._try_is.get())
            score = ps * is_
            actual_zone = risk_zone(score)
            correct = (ps == exp_p and is_ == exp_i)
            if correct:
                msg = f"✅ Correct! Score = {score}, Zone = {actual_zone}"
            else:
                exp_score = exp_p * exp_i
                msg = (f"❌ Expected P={exp_p}, I={exp_i} → Score={exp_score} "
                       f"({exp_zone}). You got P={ps}, I={is_} → {score} ({actual_zone}).")
            self._try_result_var.set(msg)
        except Exception:
            self._try_result_var.set("Enter valid scores 1-5.")

    def _toggle_try_it(self):
        self._try_it_visible = not self._try_it_visible
        if self._try_it_visible:
            self._try_it_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        else:
            self._try_it_frame.pack_forget()

    # ── B8.1: Collapsible instructions ────────────────────────────

    def _toggle_instructions(self):
        self._instr_visible = not self._instr_visible
        if self._instr_visible:
            self._instr_strip.pack(fill=tk.X, padx=5, pady=(0, 3))
            self._instr_toggle_btn.configure(text="▲ Instructions")
        else:
            self._instr_strip.pack_forget()
            self._instr_toggle_btn.configure(text="▼ Instructions")

    # ── B8.5: Narrated walkthrough ────────────────────────────────

    def _toggle_walkthrough(self):
        self._walkthrough_visible = not self._walkthrough_visible
        if self._walkthrough_visible:
            self._walkthrough_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
            self._wk_step_idx = 0
            self._wk_show_step()
        else:
            self._walkthrough_frame.pack_forget()

    def _build_assessment_walkthrough(self):
        """Build the narrated walkthrough panel for the Assessment Matrix."""
        self._wk_steps = [
            ("Step 1 — Identify Risks",
             "For each risk in your register, assign a Probability score (1 = very unlikely, "
             "5 = very likely) and an Impact score (1 = negligible, 5 = catastrophic)."),
            ("Step 2 — Compute Risk Score",
             "Multiply Probability × Impact to get the Risk Score (1–25). "
             "Example: P=4, I=3 → Score = 12."),
            ("Step 3 — Determine Zone",
             "Map the score to a zone:\n"
             "  Critical: score ≥ 15  (P×I ≥ 15)\n"
             "  High:     score 10–14\n"
             "  Medium:   score  5–9\n"
             "  Low:      score ≤  4"),
            ("Step 4 — Plot on Matrix",
             "Place the risk at column = Impact, row = Probability. "
             "The grid cell is coloured by zone. Multiple risks may share a cell."),
            ("Step 5 — Prioritise Responses",
             "Focus immediate attention on Critical and High-zone risks. "
             "Schedule mitigation plans; monitor Medium risks; "
             "accept Low risks with periodic review."),
        ]
        self._wk_step_idx = 0

        nav = ttk.Frame(self._walkthrough_frame)
        nav.pack(fill=tk.X)

        ttk.Button(nav, text="◀ Prev",
                   command=self._wk_prev).pack(side=tk.LEFT, padx=4)
        self._wk_step_label_var = tk.StringVar(value="Step 1 of 5")
        ttk.Label(nav, textvariable=self._wk_step_label_var,
                  font=("TkDefaultFont", 9, "bold")).pack(side=tk.LEFT, padx=8)
        ttk.Button(nav, text="Next ▶",
                   command=self._wk_next).pack(side=tk.LEFT, padx=4)

        self._wk_title_var = tk.StringVar()
        ttk.Label(
            self._walkthrough_frame,
            textvariable=self._wk_title_var,
            font=(
                "TkDefaultFont",
                10,
                "bold")).pack(
            anchor=tk.W,
            pady=(
                6,
                2))

        self._wk_body_var = tk.StringVar()
        ttk.Label(self._walkthrough_frame, textvariable=self._wk_body_var,
                  wraplength=700, justify=tk.LEFT,
                  font=("TkDefaultFont", 9)).pack(anchor=tk.W, padx=4)

    def _wk_show_step(self):
        n = len(self._wk_steps)
        idx = self._wk_step_idx % n
        title, body = self._wk_steps[idx]
        self._wk_step_label_var.set(f"Step {idx + 1} of {n}")
        self._wk_title_var.set(title)
        self._wk_body_var.set(body)

    def _wk_prev(self):
        self._wk_step_idx = (self._wk_step_idx - 1) % len(self._wk_steps)
        self._wk_show_step()

    def _wk_next(self):
        self._wk_step_idx = (self._wk_step_idx + 1) % len(self._wk_steps)
        self._wk_show_step()

    def _refresh_assessment_grid(self):
        """Redraw the 5×5 assessment canvas grid."""
        c = self._grid_canvas
        c.delete("all")
        reg = self.state.risk_register
        if reg is None:
            return

        reg.recompute_scores()

        MARGIN_L = 28
        MARGIN_B = 20
        MARGIN_T = 10
        MARGIN_R = 8
        canvas_w = int(c.winfo_width()) or 360
        canvas_h = int(c.winfo_height()) or 320
        usable_w = canvas_w - MARGIN_L - MARGIN_R
        usable_h = canvas_h - MARGIN_B - MARGIN_T
        cw = usable_w / 5
        ch = usable_h / 5

        def cell_x(i_score):   # i_score 1-5
            return MARGIN_L + (i_score - 1) * cw

        def cell_y(p_score):   # p_score 1-5, 5 at top
            return MARGIN_T + (5 - p_score) * ch

        # Draw cells
        for p in range(1, 6):
            for i in range(1, 6):
                score = p * i
                col = zone_color(score)
                x0 = cell_x(i)
                y0 = cell_y(p)
                x1, y1 = x0 + cw, y0 + ch
                c.create_rectangle(x0, y0, x1, y1, fill=col, outline="white",
                                   width=2, tags=f"cell_{p}_{i}")
                # Risk count in cell
                risks_here = reg.risks_in_cell(p, i)
                n = len(risks_here)
                if n > 0:
                    c.create_text(x0 + cw / 2, y0 + ch / 2 - 6,
                                  text=str(n), fill="black",
                                  font=("TkDefaultFont", 12, "bold"))
                    ids = " ".join(r.id for r in risks_here[:3])
                    if len(risks_here) > 3:
                        ids += "…"
                    c.create_text(x0 + cw / 2, y0 + ch / 2 + 10,
                                  text=ids, fill="#333",
                                  font=("TkDefaultFont", 7))

        # Axis labels — probability (left, top-to-bottom: 5→1)
        for p in range(1, 6):
            y = cell_y(p) + ch / 2
            c.create_text(MARGIN_L / 2, y, text=str(p),
                          font=("TkDefaultFont", 8, "bold"), fill="#555")

        # Impact labels (bottom, left-to-right: 1→5)
        for i in range(1, 6):
            x = cell_x(i) + cw / 2
            c.create_text(x, canvas_h - MARGIN_B / 2, text=str(i),
                          font=("TkDefaultFont", 8, "bold"), fill="#555")

        # Zone counts
        counts = reg.zone_counts()
        mapping = {"Critical": "Critical", "High": "High",
                   "Medium": "Medium", "Low": "Low"}
        for zone, k in mapping.items():
            self._zone_vars[zone].set(str(counts.get(k.lower(), 0)))

    def _on_canvas_click(self, event):
        """Map canvas click to a (p,i) cell and show its risks."""
        c = self._grid_canvas
        canvas_w = int(c.winfo_width()) or 360
        canvas_h = int(c.winfo_height()) or 320
        MARGIN_L = 28
        MARGIN_B = 20
        MARGIN_T = 10
        MARGIN_R = 8
        usable_w = canvas_w - MARGIN_L - MARGIN_R
        usable_h = canvas_h - MARGIN_B - MARGIN_T
        cw = usable_w / 5
        ch = usable_h / 5
        col_idx = int((event.x - MARGIN_L) / cw)   # 0-4
        row_idx = int((event.y - MARGIN_T) / ch)   # 0-4, 0=top
        if not (0 <= col_idx <= 4 and 0 <= row_idx <= 4):
            return
        i_score = col_idx + 1
        p_score = 5 - row_idx
        self._show_cell_risks(p_score, i_score)

    def _show_cell_risks(self, p_score: int, i_score: int):
        """Populate the cell-detail treeview for the given cell."""
        reg = self.state.risk_register
        if reg is None:
            return
        zone = risk_zone(p_score * i_score)
        self._cell_label_var.set(
            f"P={p_score}, I={i_score}  →  Score={
                p_score * i_score}  ({zone})")
        self._cell_tree.delete(*self._cell_tree.get_children())
        for r in reg.risks_in_cell(p_score, i_score):
            self._cell_tree.insert(
                "", tk.END, values=(
                    r.id, r.name, r.risk_score))

    # ------------------------------------------------------------------
    # Sub-tab D: Response Planning
    # ------------------------------------------------------------------

    def _build_response_tab(self):
        """Build the response planning sub-tab."""
        # PanedWindow: risk list | form
        main_pane = ttk.PanedWindow(self._response_frame, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: risk list sorted by score
        left_lf = ttk.LabelFrame(main_pane, text="Risks by Score")
        main_pane.add(left_lf, weight=2)

        self._resp_list_tree = ttk.Treeview(
            left_lf,
            columns=("id", "name", "score", "zone", "response"),
            show="headings", selectmode="browse", height=18,
        )
        for col, hdr, w in [
            ("id", "ID", 50),
            ("name", "Name", 130),
            ("score", "Score", 45),
            ("zone", "Zone", 65),
            ("response", "Strategy", 75),
        ]:
            self._resp_list_tree.heading(col, text=hdr)
            self._resp_list_tree.column(col, width=w, anchor=tk.CENTER)
        self._resp_list_tree.column("name", anchor=tk.W)
        vsb2 = ttk.Scrollbar(left_lf, orient=tk.VERTICAL,
                             command=self._resp_list_tree.yview)
        self._resp_list_tree.configure(yscrollcommand=vsb2.set)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)
        self._resp_list_tree.pack(fill=tk.BOTH, expand=True)
        enhance_treeview(self._resp_list_tree)
        self._resp_list_tree.bind("<<TreeviewSelect>>", self._on_resp_select)

        ttk.Button(left_lf, text="Apply Accept to All Unplanned",
                   command=self._apply_default_response).pack(
                       fill=tk.X, padx=5, pady=5)

        # Right: scrollable form
        right_outer = ttk.Frame(main_pane)
        main_pane.add(right_outer, weight=3)

        form_lf = ttk.LabelFrame(right_outer, text="Response Details")
        form_lf.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollable canvas for the form
        form_canvas = tk.Canvas(form_lf, highlightthickness=0)
        form_vsb = ttk.Scrollbar(form_lf, orient=tk.VERTICAL,
                                 command=form_canvas.yview)
        form_canvas.configure(yscrollcommand=form_vsb.set)
        form_vsb.pack(side=tk.RIGHT, fill=tk.Y)
        form_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        form_inner = ttk.Frame(form_canvas)
        form_win = form_canvas.create_window(
            (0, 0), window=form_inner, anchor="nw")
        form_inner.bind("<Configure>",
                        lambda e: form_canvas.configure(
                            scrollregion=form_canvas.bbox("all")))
        form_canvas.bind("<Configure>",
                         lambda e: form_canvas.itemconfig(
                             form_win, width=e.width))

        R = 0
        ttk.Label(form_inner, text="Selected Risk:").grid(
            row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_selected_var = tk.StringVar(value="(none selected)")
        ttk.Label(form_inner, textvariable=self._resp_selected_var,
                  font=("TkDefaultFont", 9, "bold")).grid(
                      row=R, column=1, sticky=tk.W, padx=8)

        R += 1
        ttk.Separator(form_inner, orient=tk.HORIZONTAL).grid(
            row=R, column=0, columnspan=2, sticky=tk.EW, padx=8, pady=4)

        R += 1
        ttk.Label(form_inner, text="Strategy:").grid(
            row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_strategy_var = tk.StringVar()
        ttk.Combobox(
            form_inner,
            textvariable=self._resp_strategy_var,
            width=18,
            values=[
                s.value for s in ResponseStrategy],
            state="readonly").grid(
            row=R,
            column=1,
            sticky=tk.W,
            padx=8)

        R += 1
        ttk.Label(form_inner, text="Description:").grid(
            row=R, column=0, sticky=tk.NW, padx=8, pady=4)
        self._resp_desc_text = tk.Text(form_inner, width=28, height=3)
        self._resp_desc_text.grid(row=R, column=1, padx=8, pady=4)

        R += 1
        ttk.Label(form_inner, text="Owner:").grid(
            row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_owner_var = tk.StringVar()
        ttk.Entry(
            form_inner,
            textvariable=self._resp_owner_var,
            width=20).grid(
            row=R,
            column=1,
            sticky=tk.W,
            padx=8)

        R += 1
        ttk.Label(form_inner, text="Stakeholder Owner:").grid(
            row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_stakeholder_var = tk.StringVar()
        ttk.Entry(
            form_inner,
            textvariable=self._resp_stakeholder_var,
            width=20).grid(
            row=R,
            column=1,
            sticky=tk.W,
            padx=8)

        R += 1
        ttk.Label(form_inner, text="Response Cost ($):").grid(
            row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_cost_var = tk.StringVar(value="0.00")
        ttk.Entry(form_inner, textvariable=self._resp_cost_var, width=14).grid(
            row=R, column=1, sticky=tk.W, padx=8)

        R += 1
        ttk.Label(form_inner, text="Budget Impact ($):").grid(
            row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_budget_var = tk.StringVar(value="0.00")
        ttk.Entry(
            form_inner,
            textvariable=self._resp_budget_var,
            width=14).grid(
            row=R,
            column=1,
            sticky=tk.W,
            padx=8)

        R += 1
        ttk.Separator(form_inner, orient=tk.HORIZONTAL).grid(
            row=R, column=0, columnspan=2, sticky=tk.EW, padx=8, pady=4)

        R += 1
        ttk.Label(form_inner, text="Residual Prob. Score (1-5):",
                  foreground="darkblue").grid(
                      row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_res_p_var = tk.StringVar(value="3")
        rp_box = ttk.Combobox(
            form_inner,
            textvariable=self._resp_res_p_var,
            width=5,
            values=[
                "1",
                "2",
                "3",
                "4",
                "5"],
            state="readonly")
        rp_box.grid(row=R, column=1, sticky=tk.W, padx=8)

        R += 1
        ttk.Label(form_inner, text="Residual Impact Score (1-5):",
                  foreground="darkblue").grid(
                      row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_res_i_var = tk.StringVar(value="3")
        ri_box = ttk.Combobox(
            form_inner,
            textvariable=self._resp_res_i_var,
            width=5,
            values=[
                "1",
                "2",
                "3",
                "4",
                "5"],
            state="readonly")
        ri_box.grid(row=R, column=1, sticky=tk.W, padx=8)

        R += 1
        ttk.Label(form_inner, text="Residual Score:",
                  foreground="darkblue").grid(
                      row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_res_score_var = tk.StringVar(value="—")
        ttk.Label(form_inner, textvariable=self._resp_res_score_var,
                  font=("TkDefaultFont", 9, "bold"),
                  foreground="darkblue").grid(
                      row=R, column=1, sticky=tk.W, padx=8)

        R += 1
        ttk.Label(form_inner, text="Residual Reduction %:",
                  foreground="darkblue").grid(
                      row=R, column=0, sticky=tk.W, padx=8, pady=4)
        self._resp_reduction_var = tk.StringVar(value="—")
        ttk.Label(form_inner, textvariable=self._resp_reduction_var,
                  font=("TkDefaultFont", 9, "bold"),
                  foreground="#27ae60").grid(
                      row=R, column=1, sticky=tk.W, padx=8)

        def _update_residual_score(*_):
            try:
                s = int(self._resp_res_p_var.get()) * \
                    int(self._resp_res_i_var.get())
                self._resp_res_score_var.set(f"{s}  ({risk_zone(s)})")
                # Residual reduction: compare against original score of
                # selected risk
                rid = self._selected_response_risk_id
                reg = self.state.risk_register
                orig_score = reg.get_risk(
                    rid).risk_score if (reg and rid) else 0
                if orig_score > 0:
                    pct = (orig_score - s) / orig_score * 100
                    self._resp_reduction_var.set(f"{pct:.0f}%")
                else:
                    self._resp_reduction_var.set("—")
            except Exception:
                pass

        self._resp_res_p_var.trace_add("write", _update_residual_score)
        self._resp_res_i_var.trace_add("write", _update_residual_score)

        R += 1
        ttk.Separator(form_inner, orient=tk.HORIZONTAL).grid(
            row=R, column=0, columnspan=2, sticky=tk.EW, padx=8, pady=4)

        R += 1
        ttk.Label(form_inner, text="Trigger Conditions:").grid(
            row=R, column=0, sticky=tk.NW, padx=8, pady=4)
        self._resp_trigger_text = tk.Text(form_inner, width=28, height=3)
        self._resp_trigger_text.grid(row=R, column=1, padx=8, pady=4)

        R += 1
        ttk.Label(form_inner, text="Contingency Plan:").grid(
            row=R, column=0, sticky=tk.NW, padx=8, pady=4)
        self._resp_contingency_text = tk.Text(form_inner, width=28, height=3)
        self._resp_contingency_text.grid(row=R, column=1, padx=8, pady=4)

        R += 1
        ttk.Button(form_inner, text="💾 Save Response",
                   command=self._save_response).grid(
                       row=R, column=0, columnspan=2, pady=10)

        # Bottom: Effectiveness summary
        eff_lf = ttk.LabelFrame(right_outer, text="Effectiveness Summary")
        eff_lf.pack(fill=tk.X, padx=5, pady=(0, 5))

        eff_cols = ("id", "name", "orig", "resid", "pct")
        self._eff_tree = ttk.Treeview(eff_lf, columns=eff_cols,
                                      show="headings", height=5)
        for col, hdr, w in [
            ("id", "ID", 50),
            ("name", "Risk", 140),
            ("orig", "Original", 60),
            ("resid", "Residual", 60),
            ("pct", "% Red.", 55),
        ]:
            self._eff_tree.heading(col, text=hdr)
            self._eff_tree.column(col, width=w, anchor=tk.CENTER)
        self._eff_tree.column("name", anchor=tk.W)
        self._eff_tree.pack(fill=tk.X, padx=5, pady=(0, 5))
        enhance_treeview(self._eff_tree)

    def _refresh_response_list(self):
        """Reload the left-side risk list sorted by risk score."""
        reg = self.state.risk_register
        if reg is None:
            return
        reg.recompute_scores()
        reg.update_ranks()
        self._resp_list_tree.delete(*self._resp_list_tree.get_children())
        for r in reg.risks_by_score():
            strat = r.response_strategy.value if r.response_strategy else ""
            self._resp_list_tree.insert("", tk.END, iid=r.id, values=(
                r.id, r.name, f"{r.risk_score:.0f}",
                risk_zone(r.risk_score), strat,
            ))

    def _on_resp_select(self, _event=None):
        """Load the form when a risk is selected in the left list."""
        sel = self._resp_list_tree.selection()
        if not sel:
            return
        self._selected_response_risk_id = sel[0]
        self._load_response_form(sel[0])

    def _load_response_form(self, risk_id: str):
        """Populate the response form for the given risk."""
        reg = self.state.risk_register
        r = reg.get_risk(risk_id) if reg else None
        if r is None:
            return
        self._resp_selected_var.set(
            f"[{r.id}] {r.name}  (Score: {r.risk_score:.0f})")
        self._resp_strategy_var.set(
            r.response_strategy.value if r.response_strategy else "")
        self._resp_desc_text.delete("1.0", tk.END)
        self._resp_desc_text.insert("1.0", r.response_description)
        self._resp_owner_var.set(r.response_owner)
        self._resp_stakeholder_var.set(getattr(r, "stakeholder_owner", ""))
        self._resp_cost_var.set(f"{r.response_cost:.2f}")
        self._resp_budget_var.set(f"{getattr(r, 'budget_impact', 0.0):.2f}")
        self._resp_res_p_var.set(str(int(r.residual_probability)))
        self._resp_res_i_var.set(str(int(r.residual_impact)))
        self._resp_trigger_text.delete("1.0", tk.END)
        self._resp_trigger_text.insert("1.0", r.trigger_conditions)
        self._resp_contingency_text.delete("1.0", tk.END)
        self._resp_contingency_text.insert("1.0", r.contingency_plan)

    def _save_response(self):
        """Read form fields and save the response plan for the selected risk."""
        region = self.state.risk_register
        rid = self._selected_response_risk_id
        if region is None or rid is None:
            messagebox.showinfo("Info", "Select a risk first.")
            return
        try:
            strategy_str = self._resp_strategy_var.get().strip()
            strategy = ResponseStrategy(strategy_str) if strategy_str else None
            desc = self._resp_desc_text.get("1.0", tk.END).strip()
            owner = self._resp_owner_var.get().strip()
            stakeholder = self._resp_stakeholder_var.get().strip()
            cost = float(self._resp_cost_var.get())
            budget = float(self._resp_budget_var.get())
            res_p = float(self._resp_res_p_var.get())
            res_i = float(self._resp_res_i_var.get())
            trigger = self._resp_trigger_text.get("1.0", tk.END).strip()
            cont = self._resp_contingency_text.get("1.0", tk.END).strip()
            if cost < 0:
                raise ValueError("Response cost cannot be negative.")
            if budget < 0:
                raise ValueError("Budget impact cannot be negative.")
            region.update_risk(
                rid,
                response_strategy=strategy,
                response_description=desc,
                response_owner=owner,
                stakeholder_owner=stakeholder,
                response_cost=cost,
                budget_impact=budget,
                residual_probability=res_p,
                residual_impact=res_i,
                trigger_conditions=trigger,
                contingency_plan=cont,
            )
            self.state.mark_dirty()
            self._refresh_response_list()
            self._refresh_effectiveness()
            self._refresh_register_tree()
            messagebox.showinfo("Saved", "Response plan saved.")
        except ValueError as exc:
            messagebox.showerror("Validation Error", str(exc))

    def _apply_default_response(self):
        """Set 'Accept' strategy for all risks that have no strategy set."""
        reg = self.state.risk_register
        if reg is None:
            return
        count = 0
        for r in reg.risks:
            if r.response_strategy is None:
                reg.update_risk(
                    r.id, response_strategy=ResponseStrategy.ACCEPT)
                count += 1
        self.state.mark_dirty()
        self._refresh_response_list()
        self._refresh_effectiveness()
        self._refresh_register_tree()
        messagebox.showinfo(
            "Done", f"Applied 'Accept' to {count} unplanned risk(s).")

    def _refresh_effectiveness(self):
        """Populate the effectiveness summary treeview."""
        reg = self.state.risk_register
        if reg is None:
            return
        reg.recompute_scores()
        self._eff_tree.delete(*self._eff_tree.get_children())
        for r in reg.risks_by_score():
            orig = r.risk_score
            resid = r.residual_score
            pct = (orig - resid) / orig * 100 if orig > 0 else 0.0
            self._eff_tree.insert("", tk.END, values=(
                r.id, r.name,
                f"{orig:.0f}", f"{resid:.0f}", f"{pct:.0f}%",
            ))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set_mode(self, mode: str):
        """Adjust UI for UG/PG mode."""
        self._mode = mode
        # Show all-calculations button only in UG mode
        if getattr(self, "_worked_btn", None) is not None:
            if mode.upper() == "UG":
                self._worked_btn.pack(side=tk.LEFT, padx=2)
            else:
                self._worked_btn.pack_forget()

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB and hasattr(self, "_fig"):
            figs.append(("risk_matrix", self._fig))
        return figs

    def on_tab_selected(self):
        """Called when this tab is selected — refresh all sub-tabs."""
        self._refresh_register_tree()
        if HAS_MATPLOTLIB:
            self._draw_matrix()
        self._refresh_assessment_grid()
        self._refresh_response_list()
        self._refresh_effectiveness()

    # ── Plotly embedded renderer ──────────────────────────────────

    def _switch_renderer(self):
        mode = self._render_mode_var.get()
        if mode == "plotly" and getattr(self, '_plotly_frame', None):
            self._mpl_matrix_frame.pack_forget()
            self._plotly_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            if getattr(self, '_plotly_frame', None):
                self._plotly_frame.pack_forget()
            self._mpl_matrix_frame.pack(fill=tk.BOTH, expand=True)
        self._draw_matrix()

    def _update_plotly_matrix(self):
        if not self._plotly_frame:
            return
        risks = self.state.risk_register.risks if self.state.risk_register else []
        try:
            fig = _plotly_risk(risks)
            if fig:
                self._plotly_frame.update_chart(fig)
            else:
                self._plotly_frame.load_html(
                    "<html><body style='font-family:sans-serif;padding:40px'>"
                    "<h3>No risks to display</h3></body></html>")
        except Exception as e:
            self._plotly_frame.load_html(
                f"<html><body style='font-family:sans-serif;padding:40px'>"
                f"<h3>Error</h3><pre>{e}</pre></body></html>")
