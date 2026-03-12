"""
PMhelper Edu — SWOT Analysis Tab (PG-only).
2x2 quadrant grid with auto-extract and manual CRUD.
Exports to PNG, PDF, and CSV.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
import os

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.swot_models_edu import (
    SWOTFactor, SWOTCategory, SWOTSource, SWOTAnalysis,
)
from pmhelper.utils.swot_extractor_edu import SWOTExtractor

# Quadrant colours (light backgrounds for treeview tags)
_QUADRANT_COLOURS = {
    SWOTCategory.STRENGTH:    "#d4edda",   # green
    SWOTCategory.WEAKNESS:    "#f8d7da",   # red
    SWOTCategory.OPPORTUNITY: "#cce5ff",   # blue
    SWOTCategory.THREAT:      "#fff3cd",   # amber
}

_QUADRANT_LABELS = {
    SWOTCategory.STRENGTH:    "Strengths (Internal +)",
    SWOTCategory.WEAKNESS:    "Weaknesses (Internal −)",
    SWOTCategory.OPPORTUNITY: "Opportunities (External +)",
    SWOTCategory.THREAT:      "Threats (External −)",
}


class SWOTTabEdu:
    """SWOT Analysis tab with 2×2 grid, auto-extract, CRUD, and export."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)

        # Ensure state has a swot_analysis
        if not hasattr(self.state, 'swot_analysis') or self.state.swot_analysis is None:
            self.state.swot_analysis = SWOTAnalysis()

        self._trees: dict[SWOTCategory, ttk.Treeview] = {}
        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Label(toolbar, text="SWOT Analysis", font=("TkDefaultFont", 11, "bold")).pack(side=tk.LEFT)

        # Auto-extract buttons
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Auto-Extract All", command=self._auto_extract_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="From Charter", command=self._extract_charter).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="From Risks", command=self._extract_risks).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="From EVM", command=self._extract_evm).pack(side=tk.LEFT, padx=2)

        # Manual CRUD
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Add Factor", command=self._add_manual).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Delete Selected", command=self._delete_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Clear All", command=self._clear_all).pack(side=tk.LEFT, padx=2)

        # Export
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=8, fill=tk.Y)
        ttk.Button(toolbar, text="Export PNG", command=self._export_png).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=2)

        # 2×2 quadrant grid
        grid = ttk.Frame(self.frame)
        grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        layout = [
            (SWOTCategory.STRENGTH, 0, 0),
            (SWOTCategory.WEAKNESS, 0, 1),
            (SWOTCategory.OPPORTUNITY, 1, 0),
            (SWOTCategory.THREAT, 1, 1),
        ]

        for cat, row, col in layout:
            self._build_quadrant(grid, cat, row, col)

        # Footer
        self._footer_var = tk.StringVar(value="Factors: 0")
        ttk.Label(self.frame, textvariable=self._footer_var,
                  font=("TkDefaultFont", 9, "italic")).pack(fill=tk.X, padx=5, pady=(0, 5))

    def _build_quadrant(self, parent, category: SWOTCategory, row: int, col: int):
        """Build one quadrant with label + treeview."""
        lf = ttk.LabelFrame(parent, text=_QUADRANT_LABELS[category])
        lf.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)

        cols = ("text", "source", "weight")
        tree = ttk.Treeview(lf, columns=cols, show="headings",
                            selectmode="browse", height=6)
        tree.heading("text", text="Factor")
        tree.heading("source", text="Source")
        tree.heading("weight", text="Weight")
        tree.column("text", width=280)
        tree.column("source", width=80, anchor=tk.CENTER)
        tree.column("weight", width=50, anchor=tk.CENTER)

        sb = ttk.Scrollbar(lf, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(3, 0), pady=3)
        sb.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 3), pady=3)

        # Store reference
        self._trees[category] = tree

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def on_tab_selected(self):
        """Called when this tab becomes visible."""
        self._refresh_all()

    _CAT_PROP = {
        SWOTCategory.STRENGTH: "strengths",
        SWOTCategory.WEAKNESS: "weaknesses",
        SWOTCategory.OPPORTUNITY: "opportunities",
        SWOTCategory.THREAT: "threats",
    }

    def _refresh_all(self):
        analysis = self.state.swot_analysis
        if analysis is None:
            analysis = SWOTAnalysis()
            self.state.swot_analysis = analysis

        for cat, tree in self._trees.items():
            tree.delete(*tree.get_children())
            prop = self._CAT_PROP.get(cat, "")
            factors = getattr(analysis, prop, []) if prop else []
            for f in factors:
                tree.insert("", tk.END, values=(f.text, f.source.value, f"{f.weight:.1f}"))

        total = analysis.factor_count()
        s = len(analysis.strengths)
        w = len(analysis.weaknesses)
        o = len(analysis.opportunities)
        t = len(analysis.threats)
        self._footer_var.set(f"Factors: {total}  (S:{s} W:{w} O:{o} T:{t})")

    # ------------------------------------------------------------------
    # Auto-Extract
    # ------------------------------------------------------------------

    def _auto_extract_all(self):
        """Extract from all available sources."""
        charter_data = self._get_charter_data()
        kpis = self._get_evm_kpis()
        bac = self._get_bac()

        analysis = SWOTExtractor.extract_all(
            charter_data=charter_data,
            risk_register=self.state.risk_register,
            kpis=kpis,
            bac=bac,
        )
        # Merge with existing manual factors
        existing = self.state.swot_analysis or SWOTAnalysis()
        manual_factors = [f for f in existing.factors if f.source == SWOTSource.MANUAL]
        for f in manual_factors:
            analysis.add_factor(f)

        self.state.swot_analysis = analysis
        self.state.mark_dirty()
        self._refresh_all()
        messagebox.showinfo("SWOT", f"Extracted {analysis.factor_count() - len(manual_factors)} factors from project data.")

    def _extract_charter(self):
        charter_data = self._get_charter_data()
        if not charter_data:
            messagebox.showinfo("SWOT", "No Charter data available.")
            return
        factors = SWOTExtractor.from_charter(charter_data)
        self._merge_factors(factors, "Charter")

    def _extract_risks(self):
        if self.state.risk_register is None:
            messagebox.showinfo("SWOT", "No Risk Register data available.")
            return
        bac = self._get_bac()
        factors = SWOTExtractor.from_risk_register(self.state.risk_register, bac)
        self._merge_factors(factors, "Risk Register")

    def _extract_evm(self):
        kpis = self._get_evm_kpis()
        if not kpis:
            messagebox.showinfo("SWOT", "No EVM data available.")
            return
        bac = self._get_bac()
        factors = SWOTExtractor.from_evm(kpis, bac)
        self._merge_factors(factors, "EVM")

    def _merge_factors(self, new_factors, source_name):
        """Add new factors while avoiding duplicates."""
        analysis = self.state.swot_analysis or SWOTAnalysis()
        existing_texts = {f.text for f in analysis.factors}
        added = 0
        for f in new_factors:
            if f.text not in existing_texts:
                analysis.add_factor(f)
                added += 1
        self.state.swot_analysis = analysis
        self.state.mark_dirty()
        self._refresh_all()
        messagebox.showinfo("SWOT", f"Added {added} factors from {source_name}.")

    # ------------------------------------------------------------------
    # Manual CRUD
    # ------------------------------------------------------------------

    def _add_manual(self):
        """Open a dialog to add a manual SWOT factor."""
        dialog = _SWOTFactorDialog(self.frame, "Add SWOT Factor")
        if dialog.result:
            analysis = self.state.swot_analysis or SWOTAnalysis()
            analysis.add_factor(dialog.result)
            self.state.swot_analysis = analysis
            self.state.mark_dirty()
            self._refresh_all()

    def _delete_selected(self):
        """Delete the selected factor from any quadrant."""
        for cat, tree in self._trees.items():
            sel = tree.selection()
            if sel:
                idx = tree.index(sel[0])
                analysis = self.state.swot_analysis
                factors = getattr(analysis, cat.value.lower() + "s", [])
                if 0 <= idx < len(factors):
                    factor = factors[idx]
                    analysis.remove_factor(factor)
                    self.state.mark_dirty()
                    self._refresh_all()
                return
        messagebox.showinfo("SWOT", "No factor selected.")

    def _clear_all(self):
        """Clear all SWOT factors."""
        if messagebox.askyesno("SWOT", "Clear all SWOT factors?"):
            self.state.swot_analysis = SWOTAnalysis()
            self.state.mark_dirty()
            self._refresh_all()

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _export_png(self):
        """Export SWOT matrix as PNG (or PDF)."""
        if not HAS_MATPLOTLIB:
            messagebox.showerror("Export", "Matplotlib is required for image export.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")],
            title="Export SWOT Matrix",
        )
        if not path:
            return

        analysis = self.state.swot_analysis or SWOTAnalysis()
        fig = self._render_swot_figure(analysis)
        fig.savefig(path, dpi=150, bbox_inches="tight")
        messagebox.showinfo("Export", f"SWOT matrix saved to {os.path.basename(path)}")

    def _export_csv(self):
        """Export all factors to CSV."""
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Export SWOT Factors",
        )
        if not path:
            return

        analysis = self.state.swot_analysis or SWOTAnalysis()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category", "Factor", "Source", "Weight", "Linked To"])
            for factor in analysis.factors:
                writer.writerow([
                    factor.category.value,
                    factor.text,
                    factor.source.value,
                    f"{factor.weight:.2f}",
                    factor.linked_to,
                ])
        messagebox.showinfo("Export", f"SWOT factors saved to {os.path.basename(path)}")

    def _render_swot_figure(self, analysis: SWOTAnalysis) -> "Figure":
        """Render a 2×2 SWOT matrix figure."""
        fig = Figure(figsize=(10, 8))
        fig.suptitle("SWOT Analysis", fontsize=14, fontweight="bold")

        quadrants = [
            (SWOTCategory.STRENGTH, "Strengths", "#d4edda", 1),
            (SWOTCategory.WEAKNESS, "Weaknesses", "#f8d7da", 2),
            (SWOTCategory.OPPORTUNITY, "Opportunities", "#cce5ff", 3),
            (SWOTCategory.THREAT, "Threats", "#fff3cd", 4),
        ]

        for cat, label, colour, pos in quadrants:
            ax = fig.add_subplot(2, 2, pos)
            ax.set_facecolor(colour)
            ax.set_title(label, fontweight="bold", fontsize=11)
            ax.set_xlim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])

            factors = getattr(analysis, cat.value.lower() + "s", [])
            if factors:
                y_start = 0.92
                for i, f in enumerate(factors[:8]):  # 8 max per quadrant in chart
                    ax.text(0.05, y_start - i * 0.11, f"• {f.text[:50]}",
                            fontsize=8, va="top", wrap=True)
                ax.set_ylim(0, 1)
            else:
                ax.text(0.5, 0.5, "(none)", ha="center", va="center",
                        fontsize=10, color="gray")
                ax.set_ylim(0, 1)

        fig.tight_layout(rect=[0, 0, 1, 0.95])
        return fig

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _get_charter_data(self) -> dict:
        """Try to retrieve Charter data from state."""
        if hasattr(self.state, 'charter_data') and self.state.charter_data:
            return self.state.charter_data
        return {}

    def _get_evm_kpis(self) -> dict:
        """Try to compute EVM KPIs from state."""
        if self.state.evm_project is None:
            return {}
        try:
            proj = self.state.evm_project
            # Gather latest period KPIs
            kpis = {}
            if hasattr(proj, 'cpi') and proj.cpi is not None:
                kpis['cpi'] = proj.cpi
            if hasattr(proj, 'spi') and proj.spi is not None:
                kpis['spi'] = proj.spi
            if hasattr(proj, 'cv') and proj.cv is not None:
                kpis['cv'] = proj.cv
            if hasattr(proj, 'sv') and proj.sv is not None:
                kpis['sv'] = proj.sv
            if hasattr(proj, 'eac1') and proj.eac1 is not None:
                kpis['eac1'] = proj.eac1
            # Try compute_kpis if available
            if not kpis and hasattr(proj, 'compute_kpis'):
                kpis = proj.compute_kpis()
            return kpis
        except Exception:
            return {}

    def _get_bac(self) -> float:
        """Get BAC from EVM project."""
        if self.state.evm_project and hasattr(self.state.evm_project, 'bac'):
            return self.state.evm_project.bac
        return 0.0


class _SWOTFactorDialog(tk.Toplevel):
    """Simple dialog for adding a SWOT factor."""

    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.title(title)
        self.result: SWOTFactor | None = None
        self.resizable(False, False)
        self.grab_set()

        # Category
        ttk.Label(self, text="Category:").grid(row=0, column=0, padx=8, pady=4, sticky=tk.W)
        self._cat_var = tk.StringVar(value="STRENGTH")
        cat_combo = ttk.Combobox(self, textvariable=self._cat_var,
                                 values=[c.value for c in SWOTCategory],
                                 state="readonly", width=20)
        cat_combo.grid(row=0, column=1, padx=8, pady=4)

        # Text
        ttk.Label(self, text="Factor:").grid(row=1, column=0, padx=8, pady=4, sticky=tk.W)
        self._text_var = tk.StringVar()
        ttk.Entry(self, textvariable=self._text_var, width=40).grid(row=1, column=1, padx=8, pady=4)

        # Weight
        ttk.Label(self, text="Weight (0-1):").grid(row=2, column=0, padx=8, pady=4, sticky=tk.W)
        self._weight_var = tk.StringVar(value="0.5")
        ttk.Entry(self, textvariable=self._weight_var, width=10).grid(row=2, column=1, padx=8, pady=4, sticky=tk.W)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=8)
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=4)

        self.wait_window()

    def _on_ok(self):
        text = self._text_var.get().strip()
        if not text:
            messagebox.showerror("Error", "Factor text is required.", parent=self)
            return
        try:
            weight = float(self._weight_var.get())
            if not 0 <= weight <= 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Weight must be a number between 0 and 1.", parent=self)
            return

        self.result = SWOTFactor(
            text=text,
            category=SWOTCategory(self._cat_var.get()),
            source=SWOTSource.MANUAL,
            weight=weight,
        )
        self.destroy()
