"""Scrollable Matplotlib canvas with optional NavigationToolbar.

Used by NetworkTab, PertDiagramTab, and GanttTabEdu to support large
projects (600+ activities) where the figure exceeds the visible viewport.

Two modes:
- **auto-fit** (default): figure resizes to fill the viewport — identical
  to the previous behaviour for small projects.  Scrollbars are inactive.
- **fixed-size**: figure stays at the caller-specified size.  Scrollbars
  appear when the figure is larger than the viewport.
"""

import sys
import tkinter as tk
from tkinter import ttk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class ScrollableMatplotlibFrame(ttk.Frame):
    """A frame embedding a matplotlib canvas inside a scrollable viewport.

    Attributes
    ----------
    figure : matplotlib.figure.Figure
    canvas : FigureCanvasTkAgg
    toolbar : NavigationToolbar2Tk | None
    """

    def __init__(self, parent, figsize=(12, 8), dpi=100, toolbar=True, **kw):
        super().__init__(parent, **kw)

        # ----- toolbar at bottom -----
        if toolbar:
            self._toolbar_frame = ttk.Frame(self)
            self._toolbar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self._toolbar_frame = None

        # ----- scrollable viewport -----
        scroll_container = ttk.Frame(self)
        scroll_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._v_sb = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL)
        self._h_sb = ttk.Scrollbar(scroll_container, orient=tk.HORIZONTAL)
        self._viewport = tk.Canvas(
            scroll_container,
            yscrollcommand=self._v_sb.set,
            xscrollcommand=self._h_sb.set,
            highlightthickness=0,
        )
        self._v_sb.config(command=self._viewport.yview)
        self._h_sb.config(command=self._viewport.xview)

        self._viewport.grid(row=0, column=0, sticky="nsew")
        self._v_sb.grid(row=0, column=1, sticky="ns")
        self._h_sb.grid(row=1, column=0, sticky="ew")
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)

        # ----- matplotlib figure + canvas -----
        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.figure.patch.set_facecolor("white")
        self.canvas = FigureCanvasTkAgg(self.figure, master=self._viewport)
        self._mpl_widget = self.canvas.get_tk_widget()

        # Place mpl widget inside the viewport via create_window
        self._win_id = self._viewport.create_window(
            (0, 0), window=self._mpl_widget, anchor="nw"
        )

        # Keep scroll region in sync with the mpl widget size
        self._mpl_widget.bind("<Configure>", self._update_scrollregion)
        self._viewport.bind("<Configure>", self._on_viewport_resize)

        # Mouse-wheel scrolling (vertical default, shift+wheel horizontal)
        for w in (self._viewport, self._mpl_widget):
            w.bind("<MouseWheel>", self._on_mousewheel)
            w.bind("<Shift-MouseWheel>", self._on_h_mousewheel)

        # ----- toolbar -----
        if toolbar:
            self.toolbar = NavigationToolbar2Tk(self.canvas, self._toolbar_frame)
            self.toolbar.update()
        else:
            self.toolbar = None

        self._auto_fit = True  # True → resize figure to fill viewport

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_figure_size(self, width_in, height_in):
        """Set figure to a fixed size (inches).  Scrollbars appear if needed."""
        self._auto_fit = False
        dpi = self.figure.dpi
        w_px = int(width_in * dpi)
        h_px = int(height_in * dpi)
        self.figure.set_size_inches(width_in, height_in, forward=True)
        # Explicitly resize the tk widget and scroll region so the viewport
        # knows the new content size immediately (avoids Tk idle-scheduling lag).
        self._mpl_widget.configure(width=w_px, height=h_px)
        self._viewport.configure(scrollregion=(0, 0, w_px, h_px))
        self.canvas.draw_idle()

    def fit_to_viewport(self):
        """Reset to auto-fit mode (figure fills the viewport, no scrollbars)."""
        self._auto_fit = True
        self._resize_to_viewport()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _update_scrollregion(self, _event=None):
        self._viewport.configure(scrollregion=self._viewport.bbox("all"))

    def _on_viewport_resize(self, event):
        if self._auto_fit:
            w, h = event.width, event.height
            if w > 10 and h > 10:
                dpi = self.figure.dpi
                self.figure.set_size_inches(w / dpi, h / dpi, forward=True)
                self.canvas.draw_idle()

    def _resize_to_viewport(self):
        w = self._viewport.winfo_width()
        h = self._viewport.winfo_height()
        if w > 10 and h > 10:
            dpi = self.figure.dpi
            self.figure.set_size_inches(w / dpi, h / dpi, forward=True)
            self.canvas.draw_idle()

    def _on_mousewheel(self, event):
        if not self._auto_fit:
            self._viewport.yview_scroll(-1 * (event.delta // 120), "units")

    def _on_h_mousewheel(self, event):
        if not self._auto_fit:
            self._viewport.xview_scroll(-1 * (event.delta // 120), "units")
