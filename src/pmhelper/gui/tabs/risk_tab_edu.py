"""
PMhelper Edu — Risk Analysis Tab.
Sub-tab A: Risk Register (Treeview with CRUD, sorted by exposure).
Sub-tab B: Risk Matrix (5×5 Matplotlib heat map).
"""

import tkinter as tk
from tkinter import ttk, messagebox
import uuid

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.colors as mcolors
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.risk_register_edu import Risk, RiskCategory, RiskRegister
from pmhelper.utils.risk_io_edu import export_to_csv, import_from_csv


class RiskTabEdu:
    """Risk Analysis tab with Risk Register and Risk Matrix sub-tabs."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)
        self._selected_risk_id = None

        # Ensure state has a risk_register
        if self.state.risk_register is None:
            self.state.risk_register = RiskRegister(bac=self.state.evm_project.bac)

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

    # ------------------------------------------------------------------
    # Sub-tab A: Risk Register
    # ------------------------------------------------------------------

    def _build_register_tab(self):
        # Toolbar
        toolbar = ttk.Frame(self._register_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Button(toolbar, text="Add Risk", command=self._add_risk).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Edit Risk", command=self._edit_risk).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Risk", command=self._delete_risk).pack(side=tk.LEFT, padx=2)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Import CSV", command=self._import_csv).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=2)

        # Treeview
        cols = ("id", "name", "category", "probability", "impact", "exposure", "flag")
        self._tree = ttk.Treeview(self._register_frame, columns=cols,
                                  show="headings", selectmode="browse")
        self._tree.heading("id", text="ID")
        self._tree.heading("name", text="Name")
        self._tree.heading("category", text="Category")
        self._tree.heading("probability", text="Probability")
        self._tree.heading("impact", text="Impact ($)")
        self._tree.heading("exposure", text="Exposure ($)")
        self._tree.heading("flag", text="\u26a0")

        self._tree.column("id", width=60, anchor=tk.CENTER)
        self._tree.column("name", width=180)
        self._tree.column("category", width=90, anchor=tk.CENTER)
        self._tree.column("probability", width=80, anchor=tk.CENTER)
        self._tree.column("impact", width=100, anchor=tk.E)
        self._tree.column("exposure", width=100, anchor=tk.E)
        self._tree.column("flag", width=40, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(self._register_frame, orient=tk.VERTICAL,
                                  command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)
        self._tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Footer
        self._footer_var = tk.StringVar(value="Total Exposure: $0  |  Contingency Reserve: $0  |  Flagged risks: 0")
        ttk.Label(self._register_frame, textvariable=self._footer_var,
                  font=("TkDefaultFont", 9, "italic")).pack(fill=tk.X, padx=5, pady=(0, 5))

    def _refresh_register_tree(self):
        """Refresh the treeview with current register data."""
        reg = self.state.risk_register
        if reg is None:
            return
        reg.recompute_exposures()
        flagged_ids = {r.id for r in reg.flag_high_exposure()}
        sorted_risks = reg.risks_by_exposure()

        self._tree.delete(*self._tree.get_children())
        for r in sorted_risks:
            flag_text = "\u25b2" if r.id in flagged_ids else ""
            self._tree.insert("", tk.END, iid=r.id, values=(
                r.id, r.name, r.category.value,
                f"{r.probability:.2f}",
                f"{r.impact:,.2f}",
                f"{r.exposure:,.2f}",
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
        dlg.geometry("400x350")
        dlg.transient(self.frame)
        dlg.grab_set()

        row = 0
        ttk.Label(dlg, text="ID:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=4)
        id_var = tk.StringVar(value=risk.id if editing else f"R{len(self.state.risk_register.risks)+1:03d}")
        id_entry = ttk.Entry(dlg, textvariable=id_var, width=30)
        id_entry.grid(row=row, column=1, padx=10, pady=4)
        if editing:
            id_entry.configure(state="readonly")

        row += 1
        ttk.Label(dlg, text="Name:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=4)
        name_var = tk.StringVar(value=risk.name if editing else "")
        ttk.Entry(dlg, textvariable=name_var, width=30).grid(row=row, column=1, padx=10, pady=4)

        row += 1
        ttk.Label(dlg, text="Description:").grid(row=row, column=0, sticky=tk.NW, padx=10, pady=4)
        desc_text = tk.Text(dlg, width=30, height=3)
        desc_text.grid(row=row, column=1, padx=10, pady=4)
        if editing:
            desc_text.insert("1.0", risk.description)

        row += 1
        ttk.Label(dlg, text="Category:").grid(row=row, column=0, sticky=tk.W, padx=10, pady=4)
        cat_var = tk.StringVar(value=risk.category.value if editing else RiskCategory.OTHER.value)
        cat_combo = ttk.Combobox(dlg, textvariable=cat_var, width=27,
                                 values=[c.value for c in RiskCategory], state="readonly")
        cat_combo.grid(row=row, column=1, padx=10, pady=4)

        row += 1
        ttk.Label(dlg, text="Probability (0-1):").grid(row=row, column=0, sticky=tk.W, padx=10, pady=4)
        prob_var = tk.StringVar(value=f"{risk.probability:.2f}" if editing else "0.00")
        ttk.Entry(dlg, textvariable=prob_var, width=30).grid(row=row, column=1, padx=10, pady=4)

        row += 1
        ttk.Label(dlg, text="Impact ($):").grid(row=row, column=0, sticky=tk.W, padx=10, pady=4)
        imp_var = tk.StringVar(value=f"{risk.impact:.2f}" if editing else "0.00")
        ttk.Entry(dlg, textvariable=imp_var, width=30).grid(row=row, column=1, padx=10, pady=4)

        def _save():
            try:
                prob = float(prob_var.get())
                impact = float(imp_var.get())
                cat = RiskCategory(cat_var.get())
                name = name_var.get().strip()
                desc = desc_text.get("1.0", tk.END).strip()
                rid = id_var.get().strip()
                if not name:
                    messagebox.showerror("Validation", "Name is required.")
                    return
                if not rid:
                    messagebox.showerror("Validation", "ID is required.")
                    return
                if editing:
                    self.state.risk_register.update_risk(
                        risk.id, name=name, description=desc,
                        probability=prob, impact=impact, category=cat)
                else:
                    new_risk = Risk(id=rid, name=name, description=desc,
                                    probability=prob, impact=impact, category=cat)
                    self.state.risk_register.add_risk(new_risk)
                self.state.mark_dirty()
                self._refresh_register_tree()
                dlg.destroy()
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))

        row += 1
        btn_frame = ttk.Frame(dlg)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Save", command=_save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dlg.destroy).pack(side=tk.LEFT, padx=5)

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
            messagebox.showinfo("Import", f"Imported {len(imported.risks)} risks.")
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

    # ------------------------------------------------------------------
    # Sub-tab B: Risk Matrix (5×5 Heat Map)
    # ------------------------------------------------------------------

    def _build_matrix_tab(self):
        if not HAS_MATPLOTLIB:
            ttk.Label(self._matrix_frame,
                      text="Matplotlib not installed — Risk Matrix unavailable.").pack(
                expand=True)
            return

        # Top toolbar
        toolbar = ttk.Frame(self._matrix_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Button(toolbar, text="Refresh", command=self._draw_matrix).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export PNG", command=lambda: self._export_matrix("png")).pack(
            side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export PDF", command=lambda: self._export_matrix("pdf")).pack(
            side=tk.LEFT, padx=2)

        # Matplotlib canvas
        self._fig = Figure(figsize=(6, 5), dpi=100)
        self._ax = self._fig.add_subplot(111)
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._matrix_frame)
        self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Detail panel
        self._detail_var = tk.StringVar(value="Click a risk on the matrix for details.")
        ttk.Label(self._matrix_frame, textvariable=self._detail_var,
                  font=("TkDefaultFont", 9)).pack(fill=tk.X, padx=5, pady=(0, 5))

        # Empty-state label (shown/hidden as needed)
        self._empty_label = ttk.Label(self._matrix_frame,
                                      text="Add risks in the Risk Register tab to populate this matrix.")

        # Click handler
        self._canvas.mpl_connect("button_press_event", self._on_matrix_click)

    def _draw_matrix(self):
        """Draw the 5×5 risk heat map."""
        if not HAS_MATPLOTLIB:
            return
        ax = self._ax
        ax.clear()

        reg = self.state.risk_register
        if reg is None or not reg.risks:
            ax.text(0.5, 0.5, "No risks to display.\nAdd risks in the Risk Register tab.",
                    ha="center", va="center", fontsize=12, color="grey",
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
            ax.plot(x, y, "o", color="white", markersize=18, markeredgecolor="black",
                    markeredgewidth=1.2)
            ax.text(x, y, str(idx), ha="center", va="center", fontsize=8,
                    fontweight="bold", color="black")
            self._risk_positions.append((x, y, r))

        ax.set_xlabel("Impact ($)", fontsize=10)
        ax.set_ylabel("Probability", fontsize=10)
        ax.set_title("Risk Matrix (5\u00d75 Heat Map)", fontsize=11, fontweight="bold")
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
            flagged = best.id in {r.id for r in self.state.risk_register.flag_high_exposure()}
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
    # Public interface
    # ------------------------------------------------------------------

    def set_mode(self, mode: str):
        """Adjust UI for UG/PG mode."""
        self._mode = mode
        # Aggregate exposure section only in PG
        # (Risk register and matrix always visible)

    def get_figures(self):
        """Return list of (name, Figure) for batch export."""
        figs = []
        if HAS_MATPLOTLIB and hasattr(self, "_fig"):
            figs.append(("risk_matrix", self._fig))
        return figs

    def on_tab_selected(self):
        """Called when this tab is selected — refresh data."""
        self._refresh_register_tree()
        if HAS_MATPLOTLIB:
            self._draw_matrix()
