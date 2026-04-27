"""
PMhelper Edu — Tab Group Notebook.

A two-level navigation widget: a left-side group selector
(Schedule, Cost, Risk, Strategic, Dashboard) controlling which
inner ``ttk.Notebook`` is visible.  Each group holds its own
set of tabs.

Design constraints
------------------
* Individual tabs must be reachable by widget reference (for ``notebook.tab(widget, state=...)``).
* ``on_tab_selected()`` must fire when any inner tab gains focus.
* PG-only show/hide must still work per-tab.
* Existing tab objects (Edu + real) are unchanged — they still receive
  their parent notebook as first arg and can be added via ``.add()``.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Callable, Dict, List, Optional


class TabGroupNotebook(ttk.Frame):
    """Two-level tab navigator: group buttons on the left, inner notebooks on the right."""

    def __init__(self, parent: tk.Widget, **kw):
        super().__init__(parent, **kw)

        # ── Layout: left sidebar + right content area ───────────
        self._sidebar = ttk.Frame(self, width=140)
        self._sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        self._sidebar.pack_propagate(False)

        self._content = ttk.Frame(self)
        self._content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Group bookkeeping
        self._groups: Dict[str, _Group] = {}       # name → _Group
        self._group_order: List[str] = []           # insertion order
        self._active_group: Optional[str] = None

        # Callback fired on any inner tab change
        self._tab_changed_callback: Optional[Callable] = None

    # ── public API ──────────────────────────────────────────────

    def add_group(self, name: str, *, icon: str = "📁") -> ttk.Notebook:
        """Create a new group and return its inner ``ttk.Notebook``.

        Parameters
        ----------
        name : str
            Human-readable group label (e.g. "Schedule").
        icon : str
            A short prefix shown on the sidebar button.

        Returns
        -------
        ttk.Notebook
            The notebook that tab widgets should be added to via
            ``notebook.add(widget, text=...)``.
        """
        nb = ttk.Notebook(self._content)

        btn = ttk.Button(
            self._sidebar,
            text=f"{icon} {name}",
            command=lambda n=name: self._select_group(n),
        )
        btn.pack(fill=tk.X, padx=4, pady=2)

        grp = _Group(name=name, notebook=nb, button=btn)
        self._groups[name] = grp
        self._group_order.append(name)

        # Forward inner tab-change events
        nb.bind("<<NotebookTabChanged>>", self._on_inner_tab_changed)

        # Auto-select first group
        if self._active_group is None:
            self._select_group(name)

        return nb

    def add_tab(
            self,
            group_name: str,
            widget: Any,
            *,
            text: str,
            **kw) -> None:
        """Convenience: add *widget* to the named group's notebook."""
        grp = self._groups[group_name]
        grp.notebook.add(widget, text=text, **kw)

    def select_tab(self, widget: Any) -> None:
        """Programmatically switch to the group + tab that contains *widget*."""
        for gname in self._group_order:
            nb = self._groups[gname].notebook
            try:
                nb.select(widget)
                self._select_group(gname)
                return
            except tk.TclError:
                continue

    def tab(self, widget: Any, **kw):
        """Proxy for ``ttk.Notebook.tab()`` — searches all inner notebooks."""
        for gname in self._group_order:
            nb = self._groups[gname].notebook
            try:
                return nb.tab(widget, **kw)
            except tk.TclError:
                continue
        raise tk.TclError("widget not managed by TabGroupNotebook")

    def index(self, what) -> int:
        """Return the flat index of the currently selected inner tab."""
        if self._active_group is None:
            return 0
        grp = self._groups[self._active_group]
        try:
            return grp.notebook.index(grp.notebook.select())
        except tk.TclError:
            return 0

    def select(self, tab_index_or_widget=None):
        """Select a tab by flat index (int) or widget reference."""
        if tab_index_or_widget is None:
            # Return currently selected widget
            if self._active_group is None:
                return None
            grp = self._groups[self._active_group]
            return grp.notebook.select()

        if isinstance(tab_index_or_widget, int):
            # Flat index across all groups
            idx = tab_index_or_widget
            for gname in self._group_order:
                grp = self._groups[gname]
                n = grp.notebook.index("end")
                if idx < n:
                    self._select_group(gname)
                    grp.notebook.select(idx)
                    return
                idx -= n
        else:
            self.select_tab(tab_index_or_widget)

    def get_all_notebooks(self) -> List[ttk.Notebook]:
        """Return inner notebooks in group order."""
        return [self._groups[g].notebook for g in self._group_order]

    def get_group_notebook(self, group_name: str) -> ttk.Notebook:
        """Return the inner notebook for a specific group."""
        return self._groups[group_name].notebook

    def bind_tab_changed(self, callback: Callable) -> None:
        """Register a callback ``callback(event)`` for any inner tab switch."""
        self._tab_changed_callback = callback

    # ── private ─────────────────────────────────────────────────

    def _select_group(self, name: str) -> None:
        if name == self._active_group:
            return
        # Hide current
        if self._active_group is not None:
            old = self._groups[self._active_group]
            old.notebook.pack_forget()
            old.button.state(["!pressed"])
        # Show new
        grp = self._groups[name]
        grp.notebook.pack(fill=tk.BOTH, expand=True)
        grp.button.state(["pressed"])
        self._active_group = name
        # Fire callback for newly visible tab
        self._on_inner_tab_changed(None)

    def _on_inner_tab_changed(self, event) -> None:
        if self._tab_changed_callback is not None:
            self._tab_changed_callback(event)


class _Group:
    """Internal bookkeeping for one tab group."""
    __slots__ = ("name", "notebook", "button")

    def __init__(self, name: str, notebook: ttk.Notebook, button: ttk.Button):
        self.name = name
        self.notebook = notebook
        self.button = button
