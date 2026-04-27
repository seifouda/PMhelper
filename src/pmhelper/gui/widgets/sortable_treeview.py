"""
Reusable Sortable & Filterable Treeview widget.

Provides two usage patterns:

1. **SortableTreeview** — drop-in replacement for ``ttk.Treeview`` with
   column sorting & quick-filter bar (use for *new* tables).
2. **enhance_treeview()** — utility to patch sorting & optional filter bar
   onto an *existing* ``ttk.Treeview`` (use for retrofit).
"""

from __future__ import annotations

import csv
import tkinter as tk
from tkinter import ttk, filedialog
from typing import List, Optional, Tuple


class SortableTreeview(ttk.Frame):
    """Treeview with built-in column sorting and optional text filter.

    Parameters
    ----------
    parent : tk.Widget
        Parent container.
    columns : list[str]
        Column identifiers.
    headings : list[str] | None
        Display headings (defaults to *columns*).
    widths : dict[str, int] | None
        ``{col_id: pixel_width}`` overrides.
    show_filter : bool
        If *True* (default), show the filter/search bar.
    show_export : bool
        If *True*, show an "Export CSV" button on the filter bar.
    anchor_map : dict[str, str] | None
        ``{col_id: tk anchor}`` overrides (default ``tk.W``).
    height : int
        Treeview row count hint.
    show : str
        Treeview *show* option (``"headings"`` by default).
    """

    def __init__(
        self,
        parent,
        columns: List[str],
        *,
        headings: Optional[List[str]] = None,
        widths: Optional[dict] = None,
        show_filter: bool = True,
        show_export: bool = False,
        anchor_map: Optional[dict] = None,
        height: int = 12,
        show: str = "headings",
        **kw,
    ):
        super().__init__(parent, **kw)
        self._columns = list(columns)
        self._headings = headings or list(columns)
        self._widths = widths or {}
        self._anchor_map = anchor_map or {}
        self._sort_col: Optional[str] = None
        self._sort_reverse = False
        self._all_items: List[Tuple] = []  # master list: (values, tags)
        self._filter_var = tk.StringVar()

        # ── Filter bar ──────────────────────────────────────────
        if show_filter:
            fbar = ttk.Frame(self)
            fbar.pack(fill=tk.X, pady=(0, 2))
            ttk.Label(fbar, text="🔍").pack(side=tk.LEFT, padx=(0, 3))
            fentry = ttk.Entry(fbar, textvariable=self._filter_var, width=28)
            fentry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self._filter_var.trace_add(
                "write", lambda *_: self._apply_filter())
            ttk.Button(fbar, text="✕", width=3,
                       command=self._clear_filter).pack(side=tk.LEFT, padx=2)
            if show_export:
                ttk.Button(
                    fbar,
                    text="Export CSV",
                    command=self._export_csv).pack(
                    side=tk.RIGHT,
                    padx=4)

        # ── Treeview + scrollbars ───────────────────────────────
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(container, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb = ttk.Scrollbar(container, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(
            container,
            columns=self._columns,
            show=show,
            height=height,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
        )
        self.tree.pack(fill=tk.BOTH, expand=True)
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure headings + columns
        for cid, heading in zip(self._columns, self._headings):
            self.tree.heading(
                cid, text=heading,
                command=lambda c=cid: self._on_heading_click(c),
            )
            w = self._widths.get(cid, 100)
            anchor = self._anchor_map.get(cid, tk.W)
            self.tree.column(cid, width=w, minwidth=40, anchor=anchor)

    # ── Public API ──────────────────────────────────────────────

    def insert(self, values, tags=(), **kw):
        """Insert a row and track it for sorting/filtering."""
        self._all_items.append((tuple(values), tags))
        self.tree.insert("", tk.END, values=values, tags=tags, **kw)

    def clear(self):
        """Remove all rows."""
        self.tree.delete(*self.tree.get_children())
        self._all_items.clear()

    def set_data(self, rows: List[Tuple], tags_list: Optional[List] = None):
        """Bulk-replace all rows.

        *rows* is a list of value-tuples.  *tags_list* (optional) is a
        parallel list of tag tuples/strings.
        """
        self.tree.delete(*self.tree.get_children())
        self._all_items.clear()
        tags_list = tags_list or [() for _ in rows]
        for values, tags in zip(rows, tags_list):
            self._all_items.append((tuple(values), tags))
            self.tree.insert("", tk.END, values=values, tags=tags)

    def get_selected_values(self):
        """Return the values tuple for the first selected row."""
        sel = self.tree.selection()
        if sel:
            return self.tree.item(sel[0], "values")
        return None

    def get_all_values(self):
        """Return list of all value-tuples (unfiltered master list)."""
        return [v for v, _ in self._all_items]

    # Expose common Treeview methods so callers don't reach into .tree
    def selection(self):
        return self.tree.selection()

    def item(self, *a, **kw):
        return self.tree.item(*a, **kw)

    def tag_configure(self, *a, **kw):
        return self.tree.tag_configure(*a, **kw)

    def bind(self, *a, **kw):
        return self.tree.bind(*a, **kw)

    def heading(self, *a, **kw):
        return self.tree.heading(*a, **kw)

    def column(self, *a, **kw):
        return self.tree.column(*a, **kw)

    def get_children(self):
        return self.tree.get_children()

    def delete(self, *items):
        return self.tree.delete(*items)

    def configure(self, **kw):
        return self.tree.configure(**kw)

    config = configure

    # ── Sorting ─────────────────────────────────────────────────

    def _on_heading_click(self, col: str):
        if self._sort_col == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col
            self._sort_reverse = False
        self._sort_and_display()
        # Update heading arrows
        for cid, heading in zip(self._columns, self._headings):
            arrow = ""
            if cid == col:
                arrow = " ▼" if self._sort_reverse else " ▲"
            self.tree.heading(cid, text=heading + arrow)

    def _sort_key(self, values: tuple, col_idx: int):
        """Return a sort key that handles numeric strings."""
        val = values[col_idx] if col_idx < len(values) else ""
        # Try numeric sort
        try:
            return (
                0,
                float(
                    str(val).replace(
                        ",",
                        "").replace(
                        "$",
                        "").replace(
                        "%",
                        "")))
        except (ValueError, TypeError):
            return (1, str(val).lower())

    def _sort_and_display(self):
        if self._sort_col is None:
            return
        try:
            col_idx = self._columns.index(self._sort_col)
        except ValueError:
            return

        self._all_items.sort(
            key=lambda item: self._sort_key(item[0], col_idx),
            reverse=self._sort_reverse,
        )
        self._apply_filter()

    # ── Filtering ───────────────────────────────────────────────

    def _apply_filter(self):
        self.tree.delete(*self.tree.get_children())
        query = self._filter_var.get().strip().lower()
        for values, tags in self._all_items:
            if query:
                text = " ".join(str(v) for v in values).lower()
                if query not in text:
                    continue
            self.tree.insert("", tk.END, values=values, tags=tags)

    def _clear_filter(self):
        self._filter_var.set("")

    # ── Export ──────────────────────────────────────────────────

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Export Table to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self._headings)
            for values, _ in self._all_items:
                writer.writerow(values)


# ════════════════════════════════════════════════════════════════
#  Utility: enhance an existing Treeview in-place
# ════════════════════════════════════════════════════════════════

def _sort_key(value: str):
    """Return a sort key that handles numeric strings."""
    try:
        return (
            0,
            float(
                str(value).replace(
                    ",",
                    "").replace(
                    "$",
                    "").replace(
                    "%",
                    "")))
    except (ValueError, TypeError):
        return (1, str(value).lower())


def _sort_treeview(tree: ttk.Treeview, col: str, reverse: bool):
    """Sort an existing Treeview's visible items by *col*."""
    items = [(tree.set(iid, col), iid) for iid in tree.get_children("")]
    items.sort(key=lambda x: _sort_key(x[0]), reverse=reverse)
    for idx, (_, iid) in enumerate(items):
        tree.move(iid, "", idx)


class _SortState:
    """Lightweight state holder attached to a Treeview for sorting."""

    def __init__(self, tree: ttk.Treeview):
        self.tree = tree
        self.col: Optional[str] = None
        self.reverse = False
        self._original_headings: dict = {}

    def on_click(self, col: str):
        if self.col == col:
            self.reverse = not self.reverse
        else:
            self.col = col
            self.reverse = False
        _sort_treeview(self.tree, col, self.reverse)
        # Update arrows
        for c in self.tree["columns"]:
            orig = self._original_headings.get(c, c)
            arrow = ""
            if c == col:
                arrow = " ▼" if self.reverse else " ▲"
            self.tree.heading(c, text=orig + arrow)


class _FilterState:
    """Filter bar controller for an existing Treeview."""

    def __init__(self, tree: ttk.Treeview, filter_var: tk.StringVar):
        self.tree = tree
        self._var = filter_var
        self._detached: List[Tuple[str, str, int]] = []  # (iid, parent, index)

    def apply(self, *_args):
        # Reattach all first
        for iid, parent, idx in self._detached:
            try:
                self.tree.reattach(iid, parent, idx)
            except tk.TclError:
                pass
        self._detached.clear()

        query = self._var.get().strip().lower()
        if not query:
            return

        for iid in list(self.tree.get_children("")):
            values = self.tree.item(iid, "values")
            text = " ".join(str(v) for v in values).lower()
            if query not in text:
                idx = self.tree.index(iid)
                self._detached.append((iid, "", idx))
                self.tree.detach(iid)


def enhance_treeview(tree: ttk.Treeview,
                     filter_frame: Optional[ttk.Frame] = None):
    """Add column-click sorting (and optional filter bar) to an existing Treeview.

    Parameters
    ----------
    tree : ttk.Treeview
        The treeview to enhance.
    filter_frame : ttk.Frame | None
        If supplied, a filter entry is packed into this frame **above** the tree.
        Pass the parent container *before* the tree is packed, or a dedicated
        frame above the tree.

    Returns
    -------
    _SortState
        The sort state object (handy for re-calling after a tree rebuild).
    """
    state = _SortState(tree)
    # Capture original heading text
    for col in tree["columns"]:
        state._original_headings[col] = tree.heading(col, "text")
    # Bind headings
    for col in tree["columns"]:
        tree.heading(col, command=lambda c=col: state.on_click(c))

    # Optional filter bar
    if filter_frame is not None:
        fvar = tk.StringVar()
        fbar = ttk.Frame(filter_frame)
        fbar.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(fbar, text="🔍").pack(side=tk.LEFT, padx=(0, 3))
        fentry = ttk.Entry(fbar, textvariable=fvar, width=28)
        fentry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        fs = _FilterState(tree, fvar)
        fvar.trace_add("write", fs.apply)
        ttk.Button(fbar, text="✕", width=3,
                   command=lambda: fvar.set("")).pack(side=tk.LEFT, padx=2)

    return state
