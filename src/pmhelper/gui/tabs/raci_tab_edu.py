"""
PMhelper Edu — RACI Responsibility Matrix Tab (V2 Phase 4).

Two inner sub-tabs:

1. **Task × Role RACI** — project activities (rows) vs team roles/people (cols).
   Populated from Input Activities tab or entered free-form.
2. **Deliverables × Department** — WBS deliverables vs organisational departments.
   Free-form only (or can be pre-populated from WBS if available).

Each sub-tab features:
* Editable colour-coded cell grid (click a cell to cycle R → A → C → I → "")
* Add/remove rows and columns
* "Load Rows from Project" (activities or WBS deliverables)
* Real-time validation panel (PM rule enforcement)
* "📖 Worked Solution" — pops a :class:`WorkedSolutionWindow`
* "🎓 Try It Yourself" — blank grid + scenario description + Check button
* Persistence: RACI data saved/loaded via ``.pmproj`` project files
"""

from __future__ import annotations

import json
import os
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Optional, Tuple

from pmhelper.core.raci_model import RACIMatrix, CELL_COLORS


# ════════════════════════════════════════════════════════════════════
#  Outer container
# ════════════════════════════════════════════════════════════════════

class RACITabEdu:
    """RACI Responsibility Matrix educational tab."""

    def __init__(self, parent, state, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self._mode = "UG"

        self.frame = ttk.Frame(parent)
        self._nb = ttk.Notebook(self.frame)
        self._nb.pack(fill=tk.BOTH, expand=True)

        # Ensure state has RACI matrices
        if not hasattr(state, "raci_task") or state.raci_task is None:
            state.raci_task = RACIMatrix()
        if not hasattr(state, "raci_deliv") or state.raci_deliv is None:
            state.raci_deliv = RACIMatrix()

        # Track matrix identity so on_tab_selected can reload only when changed
        self._last_task_id = id(state.raci_task)
        self._last_deliv_id = id(state.raci_deliv)
        self._task_sub = _RACISubTab(
            self._nb, state, matrix_attr="raci_task",
            row_label="Activity", col_label="Role",
            main_window=main_window,
            load_rows_label="📂 Load Activities from Project",
            load_rows_callback=self._load_activities,
        )
        self._deliv_sub = _RACISubTab(
            self._nb, state, matrix_attr="raci_deliv",
            row_label="Deliverable", col_label="Department",
            main_window=main_window,
            load_rows_label="📂 Load Deliverables from WBS",
            load_rows_callback=self._load_deliverables,
        )

        self._nb.add(self._task_sub.frame, text="Task × Role")
        self._nb.add(self._deliv_sub.frame, text="Deliverables × Dept")

    # ── Load callbacks ───────────────────────────────────────────

    def _load_activities(self) -> List[str]:
        """Return activity names from the Input Activities tab."""
        if self.main_window is None:
            return []
        if not hasattr(self.main_window, "_input_tab_edu"):
            return []
        raw = self.main_window._input_tab_edu.get_activities_data()
        names = []
        for act in raw:
            n = (act.get("activity") or act.get("name")
                 or act.get("id", "")).strip()
            if n:
                names.append(n)
        return names

    def _load_deliverables(self) -> List[str]:
        """Return WBS work-package names if available."""
        if self.main_window is None:
            return []
        try:
            wbs = getattr(self.state, "wbs_tree", None)
            if wbs is None:
                return []
            # Extract leaf-node names from WBS
            nodes = getattr(wbs, "nodes", [])
            return [n.get("name", "") for n in nodes
                    if n.get("name") and not n.get("children")]
        except Exception:
            return []

    # ── Public interface ─────────────────────────────────────────

    def set_mode(self, mode: str):
        self._mode = mode.upper()
        for sub in (self._task_sub, self._deliv_sub):
            sub.set_mode(self._mode)

    def on_tab_selected(self):
        """Reload grid from state when a new matrix object has been assigned."""
        task_m = getattr(self.state, "raci_task", None)
        deliv_m = getattr(self.state, "raci_deliv", None)
        if task_m is not None and id(task_m) != self._last_task_id:
            self._last_task_id = id(task_m)
            self._task_sub.load_matrix(task_m)
        if deliv_m is not None and id(deliv_m) != self._last_deliv_id:
            self._last_deliv_id = id(deliv_m)
            self._deliv_sub.load_matrix(deliv_m)

    def sync_to_state(self) -> None:
        """Sync current grid state back to ``self.state`` before a project save."""
        self.state.raci_task = self._task_sub.get_matrix()
        self.state.raci_deliv = self._deliv_sub.get_matrix()
        self._last_task_id = id(self.state.raci_task)
        self._last_deliv_id = id(self.state.raci_deliv)

    def get_figures(self) -> list:
        return []

    def get_raci_data(self) -> tuple:
        """Return ``(RACIMatrix, RACIMatrix)`` for task×role and deliverables×dept."""
        return self._task_sub.get_matrix(), self._deliv_sub.get_matrix()

    def load_raci_data(self, task_matrix: Optional[RACIMatrix],
                       deliv_matrix: Optional[RACIMatrix]) -> None:
        """Restore RACI matrices (accepts ``RACIMatrix`` objects)."""
        if task_matrix:
            self.state.raci_task = task_matrix
            self._last_task_id = id(task_matrix)
            self._task_sub.load_matrix(task_matrix)
        if deliv_matrix:
            self.state.raci_deliv = deliv_matrix
            self._last_deliv_id = id(deliv_matrix)
            self._deliv_sub.load_matrix(deliv_matrix)


# ════════════════════════════════════════════════════════════════════
#  Inner sub-tab
# ════════════════════════════════════════════════════════════════════

class _RACISubTab:
    """One RACI sub-tab (Task×Role or Deliverables×Dept)."""

    def __init__(
        self, parent, state, *,
        matrix_attr: str,
        row_label: str,
        col_label: str,
        main_window,
        load_rows_label: str,
        load_rows_callback,
    ):
        self.parent = parent
        self.state = state
        self.matrix_attr = matrix_attr
        self.row_label = row_label
        self.col_label = col_label
        self.main_window = main_window
        self._load_cb = load_rows_callback
        self._try_mode = False
        self._practice_answers: Dict[Tuple[int, int], str] = {}

        self.frame = ttk.Frame(parent)
        self._build_ui()

    # ── Current matrix property ──────────────────────────────────

    def get_matrix(self) -> RACIMatrix:
        """Read cell values from the grid and return a RACIMatrix."""
        rows = [v.get().strip()
                for v in self._row_name_vars if v.get().strip()]
        cols = [v.get().strip()
                for v in self._col_name_vars if v.get().strip()]
        m = RACIMatrix(rows=rows, cols=cols)
        for (r_idx, c_idx), var in self._cell_vars.items():
            v = var.get()
            if v:
                m.set_cell(r_idx, c_idx, v)
        return m

    def set_mode(self, mode: str) -> None:
        """Show the all-calculations button only in UG mode."""
        if getattr(self, "_worked_btn", None) is None:
            return
        if mode.upper() == "UG":
            self._worked_btn.pack(side=tk.LEFT)
        else:
            self._worked_btn.pack_forget()

    def load_matrix(self, matrix: RACIMatrix) -> None:
        """Rebuild the grid to display *matrix*."""
        self._rebuild_grid(matrix.rows, matrix.cols)
        for (key, val) in matrix.cells.items():
            try:
                r_idx, c_idx = (int(x) for x in key.split(","))
                if (r_idx, c_idx) in self._cell_vars:
                    self._cell_vars[(r_idx, c_idx)].set(val)
            except (ValueError, KeyError):
                pass
        self._run_validation()

    # ── UI Construction ──────────────────────────────────────────

    def _build_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill=tk.X, padx=6, pady=(5, 2))

        ttk.Button(toolbar, text=self._load_rows_label_text(),
                   command=self._load_rows_from_project).pack(
            side=tk.LEFT, padx=(0, 6))

        ttk.Button(toolbar, text=f"+ Add {self.row_label}",
                   command=self._add_row).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(toolbar, text=f"+ Add {self.col_label}",
                   command=self._add_col).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(
            toolbar,
            text="🔍 Validate",
            command=self._run_validation).pack(
            side=tk.LEFT,
            padx=(
                0,
                4))
        ttk.Button(toolbar, text="Load Demo",
                   command=self._load_demo).pack(side=tk.LEFT, padx=(0, 12))

        self._try_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            toolbar, text="🎓 Try It Yourself",
            variable=self._try_var, command=self._toggle_practice,
        ).pack(side=tk.RIGHT)

        # Legend row
        legend = ttk.Frame(self.frame)
        legend.pack(fill=tk.X, padx=6, pady=(0, 2))
        ttk.Label(
            legend,
            text="Legend:",
            font=(
                "TkDefaultFont",
                9,
                "bold")).pack(
            side=tk.LEFT,
            padx=(
                0,
                6))
        for code, color in CELL_COLORS.items():
            if code == "":
                continue
            tk.Label(legend, text=f"  {code} ", bg=color,
                     relief="ridge", width=3).pack(side=tk.LEFT, padx=2)
            ttk.Label(legend, text={
                "R": "Responsible", "A": "Accountable",
                "C": "Consulted", "I": "Informed",
            }[code], foreground="grey", font=("TkDefaultFont", 8)).pack(
                side=tk.LEFT, padx=(0, 6))

        # Click-to-cycle hint
        ttk.Label(
            legend,
            text="← click cell to assign",
            foreground="#6b7280",
            font=(
                "TkDefaultFont",
                8,
                "italic")).pack(
            side=tk.LEFT,
            padx=(
                6,
                0))

        # Scrollable container for main area + practice frame
        _scroll_outer = ttk.Frame(self.frame)
        _scroll_outer.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        _vsb = ttk.Scrollbar(_scroll_outer, orient=tk.VERTICAL)
        _vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._tiy_canvas = tk.Canvas(_scroll_outer, yscrollcommand=_vsb.set,
                                     highlightthickness=0)
        self._tiy_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        _vsb.config(command=self._tiy_canvas.yview)
        self._inner_frame = ttk.Frame(self._tiy_canvas)
        self._tiy_win = self._tiy_canvas.create_window(
            (0, 0), window=self._inner_frame, anchor='nw')
        self._inner_frame.bind('<Configure>',
                               lambda e: self._tiy_canvas.configure(
                                   scrollregion=self._tiy_canvas.bbox('all')))
        self._tiy_canvas.bind(
            '<Configure>',
            lambda e: self._tiy_canvas.itemconfig(
                self._tiy_win,
                width=e.width))
        _scroll_outer.bind('<Enter>', lambda e: self._tiy_canvas.bind_all(
            '<MouseWheel>', lambda ev: self._tiy_canvas.yview_scroll(int(-1 * (ev.delta / 120)), 'units')))
        _scroll_outer.bind(
            '<Leave>',
            lambda e: self._tiy_canvas.unbind_all('<MouseWheel>'))

        # Main area: grid (left) + validation (right)
        main_pane = ttk.PanedWindow(self._inner_frame, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=6, pady=2)

        # Grid panel
        self._grid_lf = ttk.LabelFrame(main_pane, text="RACI Grid")
        main_pane.add(self._grid_lf, weight=4)
        self._build_grid_panel(self._grid_lf)

        # Validation panel
        val_lf = ttk.LabelFrame(main_pane, text="Validation")
        main_pane.add(val_lf, weight=1)
        self._build_validation_panel(val_lf)

        # Edu bar
        edu_bar = ttk.Frame(self._inner_frame)
        edu_bar.pack(fill=tk.X, padx=6, pady=(2, 2))
        self._worked_btn = ttk.Button(edu_bar, text="📊 Show All Calculations",
                                      command=self._show_worked_solution)
        self._worked_btn.pack(side=tk.LEFT)

        # Summary stats
        self._summary_var = tk.StringVar()
        ttk.Label(edu_bar, textvariable=self._summary_var,
                  foreground="grey", font=("TkDefaultFont", 8)).pack(
            side=tk.LEFT, padx=(12, 0))

        # Practice frame (below content, inside scrollable inner_frame)
        self._practice_frame = ttk.LabelFrame(
            self._inner_frame, text="🎓 Try It Yourself")
        self._build_practice_panel()

        # Seed default empty grid (3 rows × 3 cols)
        default_rows = [f"{self.row_label} {i + 1}" for i in range(3)]
        default_cols = [f"{self.col_label} {i + 1}" for i in range(3)]
        self._rebuild_grid(default_rows, default_cols)

    def _load_rows_label_text(self):
        return f"📂 Load {self.row_label}s"

    # ── Grid panel ────────────────────────────────────────────────

    def _build_grid_panel(self, parent: ttk.Frame):
        """Build the scrollable canvas that will host the cell grid."""
        self._grid_canvas = tk.Canvas(parent, highlightthickness=0)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL,
                                    command=self._grid_canvas.xview)
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL,
                                    command=self._grid_canvas.yview)
        self._grid_canvas.configure(
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self._grid_canvas.pack(fill=tk.BOTH, expand=True)

        self._grid_inner = ttk.Frame(self._grid_canvas)
        self._grid_window = self._grid_canvas.create_window(
            (0, 0), window=self._grid_inner, anchor=tk.NW)

        self._grid_inner.bind("<Configure>", self._on_grid_resize)
        self._grid_canvas.bind("<Configure>", self._on_canvas_resize)

        # Storage
        self._row_name_vars: List[tk.StringVar] = []
        self._col_name_vars: List[tk.StringVar] = []
        self._cell_vars: Dict[Tuple[int, int], tk.StringVar] = {}
        self._cell_frames: Dict[Tuple[int, int], tk.Frame] = {}
        self._cell_labels: Dict[Tuple[int, int], tk.Label] = {}

    def _on_grid_resize(self, event):
        self._grid_canvas.configure(
            scrollregion=self._grid_canvas.bbox("all"))

    def _on_canvas_resize(self, event):
        self._grid_canvas.itemconfig(self._grid_window, width=event.width)

    def _rebuild_grid(self, row_names: List[str], col_names: List[str],
                      preserve_values: bool = False):
        """Destroy existing grid and rebuild with new row/col sets."""
        # Capture current values for preservation
        old_vars = dict(self._cell_vars) if preserve_values else {}
        old_row_names = [v.get() for v in self._row_name_vars]
        old_col_names = [v.get() for v in self._col_name_vars]

        for w in self._grid_inner.winfo_children():
            w.destroy()
        self._row_name_vars.clear()
        self._col_name_vars.clear()
        self._cell_vars.clear()
        self._cell_frames.clear()
        self._cell_labels.clear()

        n_rows = len(row_names)
        n_cols = len(col_names)

        # ── Header row (col names, editable) ──
        # Top-left corner: blank
        tk.Label(
            self._grid_inner,
            text="",
            width=18,
            relief="groove",
            bg="#e5e7eb").grid(
            row=0,
            column=0,
            padx=1,
            pady=1,
            sticky="nsew")

        for c_idx, cname in enumerate(col_names):
            v = tk.StringVar(value=cname)
            self._col_name_vars.append(v)
            e = ttk.Entry(self._grid_inner, textvariable=v, width=14,
                          justify=tk.CENTER)
            e.grid(row=0, column=c_idx + 1, padx=1, pady=1)

        # Remove column button row
        tk.Label(self._grid_inner, text="", width=18, relief="flat",
                 bg="#ffffff").grid(row=1, column=0, padx=1, pady=1)
        for c_idx in range(n_cols):
            ttk.Button(
                self._grid_inner, text="−", width=2,
                command=lambda c=c_idx: self._remove_col(c),
            ).grid(row=1, column=c_idx + 1, padx=1, pady=1)

        # ── Data rows ──
        for r_idx, rname in enumerate(row_names):
            grid_row = r_idx + 2

            # Row label (editable)
            rv = tk.StringVar(value=rname)
            self._row_name_vars.append(rv)
            row_frame = ttk.Frame(self._grid_inner)
            row_frame.grid(row=grid_row, column=0, padx=1, pady=1, sticky="w")
            ttk.Entry(row_frame, textvariable=rv, width=16).pack(side=tk.LEFT)
            ttk.Button(
                row_frame, text="−", width=2,
                command=lambda r=r_idx: self._remove_row(r),
            ).pack(side=tk.LEFT, padx=1)

            # Cell widgets
            for c_idx in range(n_cols):
                # Attempt to preserve old value
                old_val = ""
                if preserve_values:
                    try:
                        old_r = old_row_names.index(
                            rname) if rname in old_row_names else -1
                        old_c = old_col_names.index(
                            col_names[c_idx]) if col_names[c_idx] in old_col_names else -1
                        if old_r >= 0 and old_c >= 0:
                            old_sv = old_vars.get((old_r, old_c))
                            if old_sv:
                                old_val = old_sv.get()
                    except Exception:
                        old_val = ""

                cell_var = tk.StringVar(value=old_val)
                color = CELL_COLORS.get(old_val, CELL_COLORS[""])

                cell_f = tk.Frame(self._grid_inner, bd=1, relief="solid",
                                  bg=color, cursor="hand2")
                cell_f.grid(row=grid_row, column=c_idx + 1,
                            padx=1, pady=1, sticky="nsew")
                cell_lbl = tk.Label(cell_f, textvariable=cell_var,
                                    width=4, bg=color,
                                    font=("TkDefaultFont", 10, "bold"),
                                    cursor="hand2")
                cell_lbl.pack(padx=4, pady=3)

                self._cell_vars[(r_idx, c_idx)] = cell_var
                self._cell_frames[(r_idx, c_idx)] = cell_f
                self._cell_labels[(r_idx, c_idx)] = cell_lbl

                # Bind click to cycle handler
                for widget in (cell_f, cell_lbl):
                    widget.bind("<Button-1>", lambda e, r=r_idx,
                                c=c_idx: self._cycle_cell(r, c))

                # Watch for external var changes (e.g. load)
                cell_var.trace_add(
                    "write",
                    lambda *a,
                    r=r_idx,
                    c=c_idx: self._refresh_cell_color(
                        r,
                        c))

        self._on_grid_resize(None)

    # ── Cell interaction ─────────────────────────────────────────

    def _cycle_cell(self, r_idx: int, c_idx: int):
        """Cycle the cell value: "" → R → A → C → I → ""."""
        if self._try_mode:
            return  # practice grid is separate
        var = self._cell_vars.get((r_idx, c_idx))
        if var is None:
            return
        cycle = ["", "R", "A", "C", "I"]
        cur = var.get() if var.get() in cycle else ""
        var.set(cycle[(cycle.index(cur) + 1) % len(cycle)])
        self._run_validation()

    def _refresh_cell_color(self, r_idx: int, c_idx: int):
        """Update cell background colour after var change."""
        var = self._cell_vars.get((r_idx, c_idx))
        cell_f = self._cell_frames.get((r_idx, c_idx))
        cell_l = self._cell_labels.get((r_idx, c_idx))
        if var is None or cell_f is None:
            return
        color = CELL_COLORS.get(var.get(), CELL_COLORS[""])
        cell_f.configure(bg=color)
        if cell_l:
            cell_l.configure(bg=color)

    # ── Row/Col management ────────────────────────────────────────

    def _add_row(self):
        rows = [v.get().strip() for v in self._row_name_vars]
        cols = [v.get().strip() for v in self._col_name_vars]
        rows.append(f"{self.row_label} {len(rows) + 1}")
        self._rebuild_grid(rows, cols, preserve_values=True)

    def _add_col(self):
        rows = [v.get().strip() for v in self._row_name_vars]
        cols = [v.get().strip() for v in self._col_name_vars]
        cols.append(f"{self.col_label} {len(cols) + 1}")
        self._rebuild_grid(rows, cols, preserve_values=True)

    def _remove_row(self, row_idx: int):
        rows = [v.get().strip() for v in self._row_name_vars]
        cols = [v.get().strip() for v in self._col_name_vars]
        current_matrix = self.get_matrix()
        if len(rows) <= 1:
            messagebox.showinfo("Remove Row", "Cannot remove the last row.")
            return
        rows.pop(row_idx)
        new_matrix = RACIMatrix(rows=rows, cols=cols)
        # Re-index remaining rows (shift rows after deleted one)
        new_r = 0
        for old_r in range(len(rows) + 1):
            if old_r == row_idx:
                continue
            for c in range(len(cols)):
                val = current_matrix.get_cell(old_r, c)
                if val:
                    new_matrix.set_cell(new_r, c, val)
            new_r += 1
        self.load_matrix(new_matrix)

    def _remove_col(self, col_idx: int):
        rows = [v.get().strip() for v in self._row_name_vars]
        cols = [v.get().strip() for v in self._col_name_vars]
        if len(cols) <= 1:
            messagebox.showinfo(
                "Remove Column",
                "Cannot remove the last column.")
            return
        current_matrix = self.get_matrix()
        cols.pop(col_idx)
        new_matrix = RACIMatrix(rows=rows, cols=cols)
        for r in range(len(rows)):
            new_c = 0
            for old_c in range(len(cols) + 1):
                if old_c == col_idx:
                    continue
                val = current_matrix.get_cell(r, old_c)
                if val:
                    new_matrix.set_cell(r, new_c, val)
                new_c += 1
        self.load_matrix(new_matrix)

    # ── Validation panel ─────────────────────────────────────────

    def _build_validation_panel(self, parent: ttk.Frame):
        self._val_text = tk.Text(parent, width=28, height=12,
                                 state=tk.DISABLED, wrap=tk.WORD,
                                 font=("TkDefaultFont", 8),
                                 relief="flat")
        vsb = ttk.Scrollbar(parent, orient=tk.VERTICAL,
                            command=self._val_text.yview)
        self._val_text.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._val_text.pack(fill=tk.BOTH, expand=True)

        self._val_text.tag_config("error", foreground="#b91c1c")
        self._val_text.tag_config("warning", foreground="#b45309")
        self._val_text.tag_config("ok", foreground="#15803d")
        self._val_text.tag_config("header", font=("TkDefaultFont", 9, "bold"))

    def _run_validation(self):
        """Run RACI validation and update the validation text widget."""
        m = self.get_matrix()
        issues = m.validate()
        counts = m.count_by_type()

        self._val_text.config(state=tk.NORMAL)
        self._val_text.delete("1.0", tk.END)

        if not m.rows:
            self._val_text.insert(
                tk.END,
                "Add activities and roles to validate.\n",
                "warning")
            self._val_text.config(state=tk.DISABLED)
            return

        if not issues:
            self._val_text.insert(tk.END, "✓ Matrix is valid!\n", "ok")
        else:
            errors = [i for i in issues if i.level == "error"]
            warnings = [i for i in issues if i.level == "warning"]
            if errors:
                self._val_text.insert(
                    tk.END, f"✗ {
                        len(errors)} error(s):\n", "header")
                for iss in errors:
                    self._val_text.insert(
                        tk.END, f"• {iss.message}\n", "error")
            if warnings:
                self._val_text.insert(
                    tk.END, f"\n⚠ {
                        len(warnings)} warning(s):\n", "header")
                for iss in warnings:
                    self._val_text.insert(
                        tk.END, f"• {iss.message}\n", "warning")

        self._val_text.insert(tk.END, "\nSummary:\n", "header")
        for k in ("R", "A", "C", "I"):
            self._val_text.insert(tk.END, f"  {k}: {counts.get(k, 0)}\n")

        self._val_text.config(state=tk.DISABLED)

        # Update summary label
        self._summary_var.set(m.summary_text())

    # ── Load from project ─────────────────────────────────────────

    def _load_rows_from_project(self):
        names = self._load_cb()
        if not names:
            messagebox.showinfo(
                "Load", "No items found. Run the project analysis first.")
            return
        cols = [v.get().strip() for v in self._col_name_vars] or [
            f"{self.col_label} 1", f"{self.col_label} 2"]
        self._rebuild_grid(names, cols, preserve_values=False)
        messagebox.showinfo("Load", f"Loaded {len(names)} {self.row_label}s.")

    # ── Demo load ─────────────────────────────────────────────────

    def _load_demo(self):
        demo_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "..", "..", "data", "demos", "v2", "raci_demo.json")
        demo_path = os.path.normpath(demo_path)

        if not os.path.exists(demo_path):
            here = os.path.dirname(os.path.abspath(__file__))
            for _ in range(6):
                candidate = os.path.join(
                    here, "data", "demos", "v2", "raci_demo.json")
                if os.path.exists(candidate):
                    demo_path = candidate
                    break
                here = os.path.dirname(here)

        if not os.path.exists(demo_path):
            messagebox.showerror("Load Demo",
                                 f"Demo file not found:\n{demo_path}")
            return

        with open(demo_path, encoding="utf-8") as fh:
            demo = json.load(fh)

        data_key = "task_role" if self.matrix_attr == "raci_task" else "deliv_dept"
        raw = demo.get("data", {}).get(data_key)
        if not raw:
            messagebox.showinfo(
                "Load Demo",
                f"No '{data_key}' data in demo file.")
            return

        m = RACIMatrix.from_dict(raw)
        self.load_matrix(m)
        self._run_validation()
        messagebox.showinfo(
            "Load Demo",
            f"Loaded demo: {demo.get('name', 'RACI Demo')}\n\n"
            f"{demo.get('description', '')}")

    # ── Worked solution ───────────────────────────────────────────

    def _show_worked_solution(self):
        from pmhelper.core.raci_step_generator import (
            raci_matrix_steps, raci_theory_steps)
        from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow

        m = self.get_matrix()
        if not m.rows or not m.cols:
            steps = raci_theory_steps()
            title = "RACI — Theory & Rules"
        else:
            steps = raci_matrix_steps(
                m, matrix_title=(
                    "Task × Role RACI"
                    if self.matrix_attr == "raci_task"
                    else "Deliverables × Department"
                )
            )
            title = (
                "Task × Role RACI — Worked Solution"
                if self.matrix_attr == "raci_task"
                else "Deliverables × Dept — Worked Solution"
            )

        WorkedSolutionWindow(self.frame, title, steps)

    # ── Try It Yourself ───────────────────────────────────────────

    def _build_practice_panel(self):
        inner = ttk.Frame(self._practice_frame)
        inner.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        ttk.Label(
            inner,
            text=(
                "Fill the RACI assignments in the grid above using the correct "
                "designations (R/A/C/I) for each activity and role.\n"
                "Use 'Validate' to check your answers against PM rules."),
            foreground="navy",
            wraplength=700,
        ).pack(
            anchor=tk.W,
            pady=(
                0,
                4))

        self._prac_scenario = tk.StringVar(value="")
        ttk.Label(inner, textvariable=self._prac_scenario,
                  foreground="#6b7280", wraplength=700,
                  font=("TkDefaultFont", 8, "italic")).pack(
            anchor=tk.W, pady=(0, 4))

        btn_row = ttk.Frame(inner)
        btn_row.pack(anchor=tk.W, pady=(4, 0))
        ttk.Button(btn_row, text="✓ Check My RACI",
                   command=self._check_raci).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Show Answer",
                   command=self._reveal_answer).pack(side=tk.LEFT)

        self._prac_result_var = tk.StringVar()
        ttk.Label(inner, textvariable=self._prac_result_var,
                  foreground="teal").pack(anchor=tk.W, pady=(4, 0))

    def _toggle_practice(self):
        self._try_mode = self._try_var.get()
        if self._try_mode:
            self._practice_frame.pack(fill=tk.X, padx=6, pady=(2, 6))
            self._prac_scenario.set(self._get_scenario_text())
            self._inner_frame.update_idletasks()
            self._tiy_canvas.yview_moveto(1.0)
        else:
            self._practice_frame.pack_forget()

    def _get_scenario_text(self) -> str:
        if self.matrix_attr == "raci_task":
            return (
                "Scenario: Your team is developing a software product. "
                "Fill in the RACI grid ensuring each activity has exactly "
                "one Accountable and at least one Responsible."
            )
        return (
            "Scenario: Your organisation is implementing an ERP system. "
            "Assign RACI roles to each deliverable across departments."
        )

    def _check_raci(self):
        m = self.get_matrix()
        issues = m.validate()
        errors = [i for i in issues if i.level == "error"]
        if not errors:
            self._prac_result_var.set(
                "✓ Valid RACI! No rule violations found — well done! 🎉")
        else:
            self._prac_result_var.set(
                f"✗ {len(errors)} rule violation(s) found. Click 'Validate' for details.")

    def _reveal_answer(self):
        m = self.get_matrix()
        issues = m.validate()
        if not issues:
            self._prac_result_var.set("Your RACI is already valid!")
        else:
            self._run_validation()
            self._prac_result_var.set(
                "Validation panel updated — review errors and fix each activity row.")
