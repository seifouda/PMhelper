"""Z-Score Table Widget — scrollable highlighted grid (Phase 10)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from pmhelper.core.ztable_loader import ZTableData, ZLookupResult


# Colour palette
_CLR_HEADER_BG = "#2c3e50"
_CLR_HEADER_FG = "#ecf0f1"
_CLR_CELL_BG = "#ffffff"
_CLR_CELL_FG = "#2c3e50"
_CLR_HIGHLIGHT = "#27ae60"
_CLR_HIGHLIGHT_FG = "#ffffff"
_CLR_ROW_HIGHLIGHT = "#d5f5e3"
_CLR_COL_HIGHLIGHT = "#d5f5e3"
_CLR_ALT_ROW = "#f8f9fa"


class ZScoreTableWidget(ttk.Frame):
    """Scrollable Z-score table with forward/reverse highlighting.

    Parameters
    ----------
    parent : tk.Widget
    table : ZTableData
        Pre-loaded Z-table data.
    """

    def __init__(self, parent: tk.Widget, table: ZTableData, **kw):
        super().__init__(parent, **kw)
        self._table = table
        self._view_var = tk.StringVar(value="Positive")
        self._labels: dict[tuple[int, int], tk.Label] = {}
        self._row_header_labels: dict[int, tk.Label] = {}
        self._col_header_labels: dict[int, tk.Label] = {}

        self._build_ui()
        self._populate("Positive")

    # ────────────────────────────────────────────────────────────────
    #  UI construction
    # ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Toggle bar
        toggle = ttk.Frame(self)
        toggle.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(toggle, text="View:").pack(side=tk.LEFT, padx=(0, 4))
        ttk.Radiobutton(toggle, text="Positive (0 → +3.9)",
                        variable=self._view_var, value="Positive",
                        command=self._on_toggle).pack(side=tk.LEFT, padx=2)
        ttk.Radiobutton(toggle, text="Negative (−3.9 → 0)",
                        variable=self._view_var, value="Negative",
                        command=self._on_toggle).pack(side=tk.LEFT, padx=2)

        # Scrollable canvas
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(container, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient=tk.VERTICAL,
                            command=self._canvas.yview)
        hsb = ttk.Scrollbar(container, orient=tk.HORIZONTAL,
                            command=self._canvas.xview)
        self._canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._grid_frame = tk.Frame(self._canvas, bg=_CLR_CELL_BG)
        self._win_id = self._canvas.create_window(
            (0, 0), window=self._grid_frame, anchor=tk.NW)
        self._grid_frame.bind("<Configure>", self._on_grid_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse-wheel scrolling
        self._canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self._canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())

    def _bind_mousewheel(self):
        self._canvas.bind_all(
            "<MouseWheel>", lambda e: self._canvas.yview_scroll(-int(e.delta / 120), "units"))

    def _unbind_mousewheel(self):
        self._canvas.unbind_all("<MouseWheel>")

    def _on_grid_configure(self, _event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Let the grid be at least as wide as the canvas
        self._canvas.itemconfig(self._win_id, width=max(
            event.width, self._grid_frame.winfo_reqwidth()))

    # ────────────────────────────────────────────────────────────────
    #  Populate grid labels
    # ────────────────────────────────────────────────────────────────

    def _on_toggle(self):
        self._populate(self._view_var.get())

    def _populate(self, view: str):
        """Rebuild the grid for the selected view (Positive / Negative)."""
        # Destroy old labels
        for w in self._grid_frame.winfo_children():
            w.destroy()
        self._labels.clear()
        self._row_header_labels.clear()
        self._col_header_labels.clear()

        rows = (self._table.positive_rows if view == "Positive"
                else self._table.negative_rows)
        cols = self._table.col_labels

        cell_w = 7
        hdr_font = ("TkDefaultFont", 8, "bold")
        cell_font = ("TkDefaultFont", 8)

        # Top-left corner
        tk.Label(
            self._grid_frame,
            text="Z",
            width=5,
            bg=_CLR_HEADER_BG,
            fg=_CLR_HEADER_FG,
            font=hdr_font,
            relief="flat").grid(
            row=0,
            column=0,
            sticky="nsew")

        # Column headers
        for ci, col in enumerate(cols):
            lbl = tk.Label(self._grid_frame, text=col, width=cell_w,
                           bg=_CLR_HEADER_BG, fg=_CLR_HEADER_FG,
                           font=hdr_font, relief="flat")
            lbl.grid(row=0, column=ci + 1, sticky="nsew")
            self._col_header_labels[ci] = lbl

        # Rows
        for ri, row_label in enumerate(rows):
            bg = _CLR_CELL_BG if ri % 2 == 0 else _CLR_ALT_ROW
            # Row header
            rh = tk.Label(self._grid_frame, text=row_label, width=5,
                          bg=_CLR_HEADER_BG, fg=_CLR_HEADER_FG,
                          font=hdr_font, relief="flat")
            rh.grid(row=ri + 1, column=0, sticky="nsew")
            self._row_header_labels[ri] = rh

            for ci, col in enumerate(cols):
                val = self._table.cells.get((row_label, col))
                txt = f"{val:.4f}" if val is not None else ""
                lbl = tk.Label(self._grid_frame, text=txt, width=cell_w,
                               bg=bg, fg=_CLR_CELL_FG,
                               font=cell_font, relief="flat",
                               anchor=tk.CENTER)
                lbl.grid(row=ri + 1, column=ci + 1, sticky="nsew")
                self._labels[(ri, ci)] = lbl

        self._on_grid_configure()

    # ────────────────────────────────────────────────────────────────
    #  Highlighting API
    # ────────────────────────────────────────────────────────────────

    def clear_highlights(self):
        """Reset all cells to default colours."""
        rows = (self._table.positive_rows if self._view_var.get() == "Positive"
                else self._table.negative_rows)
        for ri in range(len(rows)):
            bg = _CLR_CELL_BG if ri % 2 == 0 else _CLR_ALT_ROW
            # Row header back to normal
            rh = self._row_header_labels.get(ri)
            if rh:
                rh.configure(bg=_CLR_HEADER_BG, fg=_CLR_HEADER_FG)
            for ci in range(len(self._table.col_labels)):
                lbl = self._labels.get((ri, ci))
                if lbl:
                    lbl.configure(bg=bg, fg=_CLR_CELL_FG)
        for ci, lbl in self._col_header_labels.items():
            lbl.configure(bg=_CLR_HEADER_BG, fg=_CLR_HEADER_FG)

    def highlight_forward(self, lookup: ZLookupResult) -> bool:
        """Highlight the row, column, and intersection cell for a forward lookup.

        Returns True if the cell was found in the current view.
        """
        self.clear_highlights()

        # Auto-switch view if needed
        z_is_negative = lookup.z_value < 0 or (
            lookup.z_value == 0 and lookup.row_label.startswith("-"))
        needed_view = "Negative" if z_is_negative else "Positive"
        if self._view_var.get() != needed_view:
            self._view_var.set(needed_view)
            self._populate(needed_view)

        rows = (self._table.positive_rows if self._view_var.get() == "Positive"
                else self._table.negative_rows)
        cols = self._table.col_labels

        try:
            ri = rows.index(lookup.row_label)
            ci = cols.index(lookup.col_label)
        except ValueError:
            return False

        # Highlight entire row (light)
        for c in range(len(cols)):
            lbl = self._labels.get((ri, c))
            if lbl:
                lbl.configure(bg=_CLR_ROW_HIGHLIGHT)

        # Highlight entire column (light)
        for r in range(len(rows)):
            lbl = self._labels.get((r, ci))
            if lbl:
                lbl.configure(bg=_CLR_COL_HIGHLIGHT)

        # Intersection cell (strong)
        cell = self._labels.get((ri, ci))
        if cell:
            cell.configure(bg=_CLR_HIGHLIGHT, fg=_CLR_HIGHLIGHT_FG)

        # Header highlights
        rh = self._row_header_labels.get(ri)
        if rh:
            rh.configure(bg=_CLR_HIGHLIGHT, fg=_CLR_HIGHLIGHT_FG)
        ch = self._col_header_labels.get(ci)
        if ch:
            ch.configure(bg=_CLR_HIGHLIGHT, fg=_CLR_HIGHLIGHT_FG)

        # Scroll to the cell
        self._scroll_to_row(ri, len(rows))
        return True

    def highlight_reverse(self, lookup: ZLookupResult) -> bool:
        """Highlight the cell found by reverse lookup (same visual as forward)."""
        return self.highlight_forward(lookup)

    def _scroll_to_row(self, ri: int, total_rows: int):
        """Scroll the canvas so that row *ri* is visible."""
        if total_rows <= 0:
            return
        frac = max(0.0, (ri - 2) / total_rows)
        self._canvas.yview_moveto(frac)
