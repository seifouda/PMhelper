"""
PlotlyChartFrame — Embeds Plotly HTML inside a Tkinter frame via tkwebview2
(Edge WebView2 with full JavaScript support).

Requires: pip install tkwebview2 "pywebview==4.4.1"
Note: COM must be initialized as STA *before* Tkinter starts.
      Call ``ensure_com_sta()`` early in the app entry point.

Usage:
    from pmhelper.gui.widgets.plotly_chart_frame import ensure_com_sta
    ensure_com_sta()          # call ONCE, before Tk() is created

    frame = PlotlyChartFrame(parent)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.update_chart(plotly_fig)
"""

import ctypes
import tkinter as tk
from tkinter import ttk
import tempfile
import os

_com_initialized = False


def ensure_com_sta():
    """Pre-initialize COM as Single-Threaded Apartment.

    Must be called *before* tk.Tk() is created, otherwise WebView2
    fails with ``RPC_E_CHANGED_MODE``.  Safe to call multiple times.
    """
    global _com_initialized
    if _com_initialized:
        return
    try:
        COINIT_APARTMENTTHREADED = 0x2
        ctypes.windll.ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)
    except OSError:
        pass  # already initialized — that's fine
    _com_initialized = True


try:
    from tkwebview2.tkwebview2 import WebView2
    WEBVIEW2_AVAILABLE = True
except ImportError:
    WEBVIEW2_AVAILABLE = False

try:
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class PlotlyChartFrame(ttk.Frame):
    """A reusable Tkinter frame that renders Plotly figures via Edge WebView2."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._tmp_file = None

        if not WEBVIEW2_AVAILABLE:
            lbl = ttk.Label(
                self,
                text="tkwebview2 is required.\npip install tkwebview2",
                anchor="center")
            lbl.pack(fill=tk.BOTH, expand=True)
            return

        self._webview = WebView2(self, width=800, height=600)
        self._webview.pack(fill=tk.BOTH, expand=True)

    # ── public API ───────────────────────────────────────────────────

    def update_chart(self, fig):
        """Render a Plotly Figure inside the embedded browser.

        Parameters
        ----------
        fig : plotly.graph_objects.Figure
        """
        html = fig.to_html(include_plotlyjs="cdn", full_html=True,
                           config={"scrollZoom": True, "displayModeBar": True})
        self.load_html(html)

    def load_html(self, html_string: str):
        """Load arbitrary HTML content into the embedded WebView2."""
        if not WEBVIEW2_AVAILABLE:
            return
        # Write to a temp file — WebView2 loads from file:// URL
        self._cleanup_tmp()
        fd, path = tempfile.mkstemp(suffix=".html", prefix="pmhelper_plotly_")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(html_string)
        self._tmp_file = path
        file_url = "file:///" + path.replace(os.sep, "/")
        self._webview.load_url(file_url)

    def clear(self):
        """Clear the chart, showing a blank page."""
        if WEBVIEW2_AVAILABLE:
            self._webview.load_html("<html><body></body></html>")
        self._cleanup_tmp()

    def destroy(self):
        self._cleanup_tmp()
        super().destroy()

    # ── internals ────────────────────────────────────────────────────

    def _cleanup_tmp(self):
        if self._tmp_file and os.path.exists(self._tmp_file):
            try:
                os.unlink(self._tmp_file)
            except OSError:
                pass
            self._tmp_file = None
