"""
PMhelper Edu — PESTEL Analysis Tab (PG-only).
Six-dimension table with impact scoring, radar chart, and risk-register bridge.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from pmhelper.core.pestel_models_edu import (
    PESTELFactor, PESTELCategory, PESTELAnalysis, PESTEL_COLOURS,
)


class PESTELTabEdu:
    """PESTEL Analysis tab with factor table, radar chart, and risk bridge."""

    def __init__(self, parent, state):
        self.parent = parent
        self.state = state
        self.frame = ttk.Frame(parent)

        if not hasattr(
                self.state,
                'pestel_analysis') or self.state.pestel_analysis is None:
            self.state.pestel_analysis = PESTELAnalysis()

        self._build_ui()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Top toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Label(
            toolbar,
            text="PESTEL Analysis",
            font=(
                "TkDefaultFont",
                11,
                "bold")).pack(
            side=tk.LEFT)
        ttk.Separator(
            toolbar,
            orient=tk.VERTICAL).pack(
            side=tk.LEFT,
            padx=8,
            fill=tk.Y)
        ttk.Button(
            toolbar,
            text="📂 Load Demo",
            command=self._load_demo).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Add Factor",
            command=self._add_factor).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Edit Factor",
            command=self._edit_factor).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Delete Factor",
            command=self._delete_factor).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Clear All",
            command=self._clear_all).pack(
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
            text="Send to Risk Register",
            command=self._send_to_risks).pack(
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
            text="Export PNG",
            command=self._export_png).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            toolbar,
            text="Export CSV",
            command=self._export_csv).pack(
            side=tk.LEFT,
            padx=2)

        # Category filter buttons
        cat_bar = ttk.Frame(self.frame)
        cat_bar.pack(fill=tk.X, padx=5, pady=(2, 0))
        ttk.Label(cat_bar, text="Filter:").pack(side=tk.LEFT, padx=(0, 4))
        self._cat_filter = tk.StringVar(value="All")
        ttk.Radiobutton(
            cat_bar,
            text="All",
            variable=self._cat_filter,
            value="All",
            command=self._refresh_all).pack(
            side=tk.LEFT,
            padx=2)
        for cat in PESTELCategory:
            ttk.Radiobutton(
                cat_bar,
                text=cat.value,
                variable=self._cat_filter,
                value=cat.value,
                command=self._refresh_all).pack(
                side=tk.LEFT,
                padx=2)

        # Main pane: table on left, radar chart on right
        pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left: Treeview table
        left = ttk.Frame(pane)
        pane.add(left, weight=3)

        cols = (
            "category",
            "description",
            "impact",
            "probability",
            "exposure",
            "timeframe",
            "mitigation")
        self._tree = ttk.Treeview(
            left,
            columns=cols,
            show="headings",
            selectmode="browse")
        self._tree.heading("category", text="Category")
        self._tree.heading("description", text="Description")
        self._tree.heading("impact", text="Impact")
        self._tree.heading("probability", text="Prob.")
        self._tree.heading("exposure", text="Exposure")
        self._tree.heading("timeframe", text="Timeframe")
        self._tree.heading("mitigation", text="Mitigation")

        self._tree.column("category", width=90, anchor=tk.CENTER)
        self._tree.column("description", width=200)
        self._tree.column("impact", width=60, anchor=tk.CENTER)
        self._tree.column("probability", width=50, anchor=tk.CENTER)
        self._tree.column("exposure", width=60, anchor=tk.CENTER)
        self._tree.column("timeframe", width=80, anchor=tk.CENTER)
        self._tree.column("mitigation", width=150)

        sb = ttk.Scrollbar(left, orient=tk.VERTICAL, command=self._tree.yview)
        self._tree.configure(yscrollcommand=sb.set)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        from pmhelper.gui.widgets.sortable_treeview import enhance_treeview
        enhance_treeview(self._tree)

        # Right: Radar chart
        right = ttk.Frame(pane)
        pane.add(right, weight=2)
        self._chart_frame = right

        # Chart toolbar: bubble overlay toggle
        chart_tb = ttk.Frame(right)
        chart_tb.pack(fill=tk.X, padx=2, pady=(2, 0))
        self._show_bubbles_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(chart_tb, text="Show Bubbles",
                        variable=self._show_bubbles_var,
                        command=self._refresh_all).pack(side=tk.LEFT, padx=4)

        self._radar_annotation = None
        self._radar_angles = []  # angles for click-to-filter

        if HAS_MATPLOTLIB:
            self._fig = Figure(figsize=(4, 4))
            self._canvas = FigureCanvasTkAgg(self._fig, master=right)
            self._canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self._canvas.mpl_connect(
                "motion_notify_event", self._on_radar_hover)
            self._canvas.mpl_connect(
                "button_press_event", self._on_radar_click)
        else:
            ttk.Label(
                right,
                text="Matplotlib required for radar chart.").pack(
                padx=20,
                pady=20)

        # Footer
        self._footer_var = tk.StringVar(
            value="Factors: 0 | Total exposure: 0.00")
        ttk.Label(
            self.frame,
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

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def on_tab_selected(self):
        self._refresh_all()

    def _refresh_all(self):
        analysis = self.state.pestel_analysis
        if analysis is None:
            analysis = PESTELAnalysis()
            self.state.pestel_analysis = analysis

        # Filter
        cat_filter = self._cat_filter.get()

        self._tree.delete(*self._tree.get_children())
        if cat_filter == "All":
            display = analysis.factors
        else:
            cat = PESTELCategory(cat_filter)
            display = analysis.by_category(cat)

        for f in display:
            sign = "+" if f.impact_score >= 0 else ""
            self._tree.insert("", tk.END, values=(
                f.category.value,
                f.description[:60],
                f"{sign}{f.impact_score:.1f}",
                f"{f.probability:.2f}",
                f"{f.exposure:.2f}",
                f.timeframe,
                f.mitigation[:40],
            ))

        total = analysis.factor_count()
        exp = analysis.total_exposure()
        self._footer_var.set(f"Factors: {total} | Total exposure: {exp:.2f}")

        # Refresh radar
        if HAS_MATPLOTLIB:
            self._draw_radar(analysis)

    def _draw_radar(self, analysis: PESTELAnalysis):
        """Draw a radar / spider chart of PESTEL dimensions with optional bubble overlay."""
        self._fig.clear()
        categories = list(PESTELCategory)
        labels = [c.value for c in categories]
        values = []
        cat_data = {}  # store per-category stats for hover
        for c in categories:
            factors = analysis.by_category(c)
            avg_exp = sum(f.exposure for f in factors) / max(len(factors), 1)
            values.append(avg_exp)
            cat_data[c] = {"count": len(factors), "avg_exposure": avg_exp}

        N = len(categories)
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        self._radar_angles = list(zip(angles, categories))
        values_plot = values + [values[0]]
        angles_plot = angles + [angles[0]]

        ax = self._fig.add_subplot(111, polar=True)
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(labels, fontsize=9)
        ax.plot(angles_plot, values_plot, 'o-', linewidth=2, color="#4e79a7")
        ax.fill(angles_plot, values_plot, alpha=0.25, color="#4e79a7")
        ax.set_title(
            "PESTEL Exposure Radar",
            fontsize=10,
            fontweight="bold",
            pad=15)

        # Bubble overlay (Task 9.7) — filtered by selected category (9C.9)
        if self._show_bubbles_var.get():
            cat_filter = self._cat_filter.get()
            for i, c in enumerate(categories):
                if cat_filter != "All" and c.value != cat_filter:
                    continue
                factors = analysis.by_category(c)
                for f in factors:
                    angle = angles[i]
                    # distance from centre = impact magnitude
                    r = abs(f.impact_score)
                    size = f.exposure * 80 + 20  # bubble size proportional to exposure
                    colour = PESTEL_COLOURS[c]
                    ax.scatter(angle, r, s=size, c=colour, alpha=0.6,
                               edgecolors="#333", linewidths=0.5, zorder=4)

        self._radar_cat_data = cat_data
        self._radar_annotation = None
        self._canvas.draw()

    # ------------------------------------------------------------------
    # Radar Interactivity (Tasks 9.6–9.7)
    # ------------------------------------------------------------------

    def _on_radar_hover(self, event):
        """Show tooltip with factor count + avg exposure when hovering near a radar axis."""
        if event.inaxes is None or not hasattr(self, '_radar_cat_data'):
            if self._radar_annotation is not None:
                self._radar_annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        # Find nearest axis
        closest_cat = self._find_nearest_axis(event)
        if closest_cat is None:
            if self._radar_annotation is not None:
                self._radar_annotation.set_visible(False)
                self._canvas.draw_idle()
            return

        data = self._radar_cat_data[closest_cat]
        tip = f"{
            closest_cat.value}\nFactors: {
            data['count']}\nAvg Exposure: {
            data['avg_exposure']:.2f}"

        if self._radar_annotation is None:
            self._radar_annotation = event.inaxes.annotate(
                tip, xy=(event.xdata, event.ydata), xytext=(15, 15),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.4", fc="#ffffcc", alpha=0.95),
                fontsize=8, zorder=10,
            )
        else:
            self._radar_annotation.xy = (event.xdata, event.ydata)
            self._radar_annotation.set_text(tip)
            self._radar_annotation.set_visible(True)
        self._canvas.draw_idle()

    def _on_radar_click(self, event):
        """Click on a radar axis to filter the table by that category."""
        if event.inaxes is None:
            return
        closest_cat = self._find_nearest_axis(event)
        if closest_cat is not None:
            self._cat_filter.set(closest_cat.value)
            self._refresh_all()

    def _find_nearest_axis(self, event) -> "PESTELCategory | None":
        """Find the nearest PESTEL category axis to the mouse event."""
        if not self._radar_angles or event.xdata is None:
            return None
        mouse_angle = event.xdata % (2 * np.pi)
        best_cat = None
        best_dist = float("inf")
        for angle, cat in self._radar_angles:
            # Angular distance
            diff = abs(mouse_angle - angle)
            diff = min(diff, 2 * np.pi - diff)
            if diff < best_dist:
                best_dist = diff
                best_cat = cat
        # Only trigger if within ~30° of an axis
        if best_dist < np.pi / 6:
            return best_cat
        return None

    # ------------------------------------------------------------------
    # Demo loader
    # ------------------------------------------------------------------

    def _load_demo(self):
        """Load demo PESTEL factors from pestel_demo.json."""
        import json as _json
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..", "data", "demos", "v2", "pestel_demo.json")
        demo_path = os.path.normpath(demo_path)

        if not os.path.exists(demo_path):
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(
                    here, "data", "demos", "v2", "pestel_demo.json")
                if os.path.exists(candidate):
                    demo_path = candidate
                    break
                here = os.path.dirname(here)

        if not os.path.exists(demo_path):
            messagebox.showerror("Load Demo",
                                 f"Demo file not found:\n{demo_path}")
            return

        with open(demo_path, encoding="utf-8") as fh:
            demo = _json.load(fh)

        factors_raw = demo.get("data", {}).get("factors", [])
        if not factors_raw:
            messagebox.showinfo("Load Demo", "No factors in demo file.")
            return

        analysis = PESTELAnalysis()
        for f in factors_raw:
            try:
                cat = PESTELCategory(f["category"])
            except (KeyError, ValueError):
                continue
            factor = PESTELFactor(
                category=cat,
                description=f.get("description", ""),
                impact_score=float(f.get("impact_score", 0)),
                probability=float(f.get("probability", 0)),
                timeframe=f.get("timeframe", "Medium-term"),
                mitigation=f.get("mitigation", ""),
                linked_to=f.get("linked_to", ""),
            )
            analysis.add_factor(factor)

        self.state.pestel_analysis = analysis
        self.state.mark_dirty()
        self._refresh_all()

        messagebox.showinfo("Load Demo",
                            f"Loaded {len(analysis.factors)} PESTEL factors.")

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def _add_factor(self):
        dialog = _PESTELFactorDialog(self.frame, "Add PESTEL Factor")
        if dialog.result:
            analysis = self.state.pestel_analysis or PESTELAnalysis()
            analysis.add_factor(dialog.result)
            self.state.pestel_analysis = analysis
            self.state.mark_dirty()
            self._refresh_all()

    def _edit_factor(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("PESTEL", "No factor selected.")
            return
        idx = self._tree.index(sel[0])
        analysis = self.state.pestel_analysis
        cat_filter = self._cat_filter.get()
        if cat_filter == "All":
            factors = analysis.factors
        else:
            factors = analysis.by_category(PESTELCategory(cat_filter))
        if idx >= len(factors):
            return
        old = factors[idx]
        dialog = _PESTELFactorDialog(self.frame, "Edit PESTEL Factor", old)
        if dialog.result:
            # Replace old with new
            try:
                real_idx = analysis.factors.index(old)
                analysis.factors[real_idx] = dialog.result
            except ValueError:
                analysis.add_factor(dialog.result)
            self.state.mark_dirty()
            self._refresh_all()

    def _delete_factor(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("PESTEL", "No factor selected.")
            return
        idx = self._tree.index(sel[0])
        analysis = self.state.pestel_analysis
        cat_filter = self._cat_filter.get()
        if cat_filter == "All":
            factors = analysis.factors
        else:
            factors = analysis.by_category(PESTELCategory(cat_filter))
        if idx < len(factors):
            analysis.remove_factor(factors[idx])
            self.state.mark_dirty()
            self._refresh_all()

    def _clear_all(self):
        if messagebox.askyesno("PESTEL", "Clear all PESTEL factors?"):
            self.state.pestel_analysis = PESTELAnalysis()
            self.state.mark_dirty()
            self._refresh_all()

    # ------------------------------------------------------------------
    # Risk Register Bridge
    # ------------------------------------------------------------------

    def _send_to_risks(self):
        """Send negative-impact factors to Risk Register."""
        analysis = self.state.pestel_analysis
        if not analysis or not analysis.factors:
            messagebox.showinfo("PESTEL", "No PESTEL factors to send.")
            return

        risk_data = analysis.factors_for_risk_register()
        if not risk_data:
            messagebox.showinfo(
                "PESTEL", "No negative-impact factors with mitigations to send.")
            return

        if self.state.risk_register is None:
            messagebox.showinfo("PESTEL", "Risk Register not initialized.")
            return

        from pmhelper.core.risk_register_edu import Risk, RiskCategory
        added = 0
        for rd in risk_data:
            risk = Risk(
                name=rd["name"],
                category=RiskCategory.EXTERNAL,
                probability=rd["probability"],
                impact=rd["impact"],
            )
            self.state.risk_register.add_risk(risk)
            added += 1

        self.state.mark_dirty()
        messagebox.showinfo("PESTEL", f"Added {added} risks to Risk Register.")

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def _export_png(self):
        if not HAS_MATPLOTLIB:
            messagebox.showerror("Export", "Matplotlib required.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")],
            title="Export PESTEL Chart",
        )
        if not path:
            return

        analysis = self.state.pestel_analysis or PESTELAnalysis()
        # Render a full-size figure
        fig = Figure(figsize=(10, 6))
        ax = fig.add_subplot(121, polar=True)

        categories = list(PESTELCategory)
        labels = [c.value for c in categories]
        values = []
        for c in categories:
            factors = analysis.by_category(c)
            avg_exp = sum(f.exposure for f in factors) / max(len(factors), 1)
            values.append(avg_exp)

        N = len(categories)
        angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
        values_plot = values + [values[0]]
        angles_plot = angles + [angles[0]]

        ax.set_theta_offset(3.14159 / 2)
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(labels, fontsize=9)
        ax.plot(angles_plot, values_plot, 'o-', linewidth=2, color="#4e79a7")
        ax.fill(angles_plot, values_plot, alpha=0.25, color="#4e79a7")
        ax.set_title("PESTEL Exposure Radar", fontsize=11, fontweight="bold")

        # Summary bar on right
        ax2 = fig.add_subplot(122)
        colors = [PESTEL_COLOURS[c] for c in categories]
        counts = [len(analysis.by_category(c)) for c in categories]
        ax2.barh(labels, counts, color=colors)
        ax2.set_xlabel("Factor Count")
        ax2.set_title("Factors by Category", fontsize=11, fontweight="bold")

        fig.suptitle("PESTEL Analysis", fontsize=14, fontweight="bold")
        fig.tight_layout(rect=[0, 0, 1, 0.95])
        fig.savefig(path, dpi=150, bbox_inches="tight")
        messagebox.showinfo("Export", f"Saved to {os.path.basename(path)}")

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Export PESTEL Factors",
        )
        if not path:
            return

        analysis = self.state.pestel_analysis or PESTELAnalysis()
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Category",
                             "Description",
                             "Impact Score",
                             "Probability",
                             "Exposure",
                             "Timeframe",
                             "Mitigation"])
            for factor in analysis.factors:
                writer.writerow([
                    factor.category.value,
                    factor.description,
                    f"{factor.impact_score:.1f}",
                    f"{factor.probability:.2f}",
                    f"{factor.exposure:.2f}",
                    factor.timeframe,
                    factor.mitigation,
                ])
        messagebox.showinfo("Export", f"Saved to {os.path.basename(path)}")


class _PESTELFactorDialog(tk.Toplevel):
    """Dialog for adding/editing a PESTEL factor."""

    def __init__(
            self,
            parent,
            title: str,
            existing: PESTELFactor | None = None):
        super().__init__(parent)
        self.title(title)
        self.result: PESTELFactor | None = None
        self.resizable(False, False)
        self.grab_set()

        row = 0

        # Category
        ttk.Label(
            self,
            text="Category:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._cat_var = tk.StringVar(
            value=existing.category.value if existing else "Political")
        ttk.Combobox(
            self,
            textvariable=self._cat_var,
            values=[
                c.value for c in PESTELCategory],
            state="readonly",
            width=20).grid(
            row=row,
            column=1,
            padx=8,
            pady=4)
        row += 1

        # Description
        ttk.Label(
            self,
            text="Description:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._desc_var = tk.StringVar(
            value=existing.description if existing else "")
        ttk.Entry(
            self,
            textvariable=self._desc_var,
            width=40).grid(
            row=row,
            column=1,
            padx=8,
            pady=4)
        row += 1

        # Impact Score
        ttk.Label(self, text="Impact (-5 to +5):").grid(row=row,
                                                        column=0, padx=8, pady=4, sticky=tk.W)
        self._impact_var = tk.StringVar(
            value=str(existing.impact_score) if existing else "0")
        ttk.Entry(
            self,
            textvariable=self._impact_var,
            width=10).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Probability
        ttk.Label(self, text="Probability (0-1):").grid(row=row,
                                                        column=0, padx=8, pady=4, sticky=tk.W)
        self._prob_var = tk.StringVar(
            value=str(existing.probability) if existing else "0.5")
        ttk.Entry(
            self,
            textvariable=self._prob_var,
            width=10).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Timeframe
        ttk.Label(
            self,
            text="Timeframe:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._tf_var = tk.StringVar(
            value=existing.timeframe if existing else "Medium-term")
        ttk.Combobox(
            self,
            textvariable=self._tf_var,
            values=[
                "Short-term",
                "Medium-term",
                "Long-term"],
            state="readonly",
            width=15).grid(
            row=row,
            column=1,
            padx=8,
            pady=4,
            sticky=tk.W)
        row += 1

        # Mitigation
        ttk.Label(
            self,
            text="Mitigation:").grid(
            row=row,
            column=0,
            padx=8,
            pady=4,
            sticky=tk.W)
        self._mit_var = tk.StringVar(
            value=existing.mitigation if existing else "")
        ttk.Entry(
            self,
            textvariable=self._mit_var,
            width=40).grid(
            row=row,
            column=1,
            padx=8,
            pady=4)
        row += 1

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=8)
        ttk.Button(
            btn_frame,
            text="OK",
            command=self._on_ok).pack(
            side=tk.LEFT,
            padx=4)
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy).pack(
            side=tk.LEFT,
            padx=4)

        self.wait_window()

    def _on_ok(self):
        desc = self._desc_var.get().strip()
        if not desc:
            messagebox.showerror(
                "Error",
                "Description is required.",
                parent=self)
            return
        try:
            impact = float(self._impact_var.get())
            if not -5 <= impact <= 5:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error",
                "Impact must be between -5 and +5.",
                parent=self)
            return
        try:
            prob = float(self._prob_var.get())
            if not 0 <= prob <= 1:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Error",
                "Probability must be between 0 and 1.",
                parent=self)
            return

        self.result = PESTELFactor(
            category=PESTELCategory(self._cat_var.get()),
            description=desc,
            impact_score=impact,
            probability=prob,
            timeframe=self._tf_var.get(),
            mitigation=self._mit_var.get().strip(),
        )
        self.destroy()
