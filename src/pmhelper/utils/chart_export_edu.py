"""
PMhelper Edu — Chart Export Utilities.
Reusable ExportButton widget + batch export for all tab figures.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from matplotlib.figure import Figure
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class ExportButton(ttk.Button):
    """
    Reusable button that exports a Matplotlib Figure to PNG or PDF.

    Usage:
        ExportButton(parent, figure=self._fig, default_name="s_curve")
    """

    def __init__(self, parent, figure: "Figure", default_name: str = "chart",
                 fmt: str = "png", text: Optional[str] = None, **kw):
        self._figure = figure
        self._default_name = default_name
        self._fmt = fmt.lower()
        display_text = text or f"Export {self._fmt.upper()}"
        super().__init__(parent, text=display_text,
                         command=self._export, **kw)

    def _export(self):
        if self._figure is None:
            messagebox.showwarning("Export", "No chart to export.")
            return
        ext = self._fmt
        filepath = filedialog.asksaveasfilename(
            defaultextension=f".{ext}",
            initialfile=f"{self._default_name}.{ext}",
            filetypes=[(f"{ext.upper()} files", f"*.{ext}"),
                       ("All files", "*.*")])
        if filepath:
            try:
                self._figure.savefig(filepath, format=ext, dpi=150,
                                     bbox_inches="tight")
                messagebox.showinfo("Export", f"Chart saved to:\n{filepath}")
            except Exception as exc:
                messagebox.showerror("Export Error", str(exc))


def export_all_charts(tabs: dict, output_dir: str, fmt: str = "png") -> List[str]:
    """
    Iterate all tabs, call get_figures() where available,
    and save each figure to output_dir.

    Args:
        tabs: dict of {name: tab_object} from MainWindowEdu.tabs
        output_dir: directory to save all chart files
        fmt: "png" or "pdf"

    Returns:
        List of saved file paths.
    """
    if not HAS_MATPLOTLIB:
        return []

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved: List[str] = []

    for tab_name, tab in tabs.items():
        if not hasattr(tab, "get_figures"):
            continue
        figures: List[Tuple[str, "Figure"]] = tab.get_figures()
        for chart_name, fig in figures:
            filename = f"{tab_name}_{chart_name}.{fmt}"
            filepath = out / filename
            try:
                fig.savefig(str(filepath), format=fmt, dpi=150,
                            bbox_inches="tight")
                saved.append(str(filepath))
            except Exception:
                pass  # skip broken figures silently

    return saved


def export_all_charts_dialog(tabs: dict, parent: tk.Widget = None,
                              fmt: str = "png") -> None:
    """
    Show a directory picker, then export all charts.
    Reports a summary messagebox.
    """
    output_dir = filedialog.askdirectory(title="Select folder for chart export",
                                          parent=parent)
    if not output_dir:
        return

    saved = export_all_charts(tabs, output_dir, fmt)

    if saved:
        messagebox.showinfo(
            "Export All Charts",
            f"Exported {len(saved)} chart(s) to:\n{output_dir}",
            parent=parent)
    else:
        messagebox.showinfo(
            "Export All Charts",
            "No charts to export. Open some tabs with data first.",
            parent=parent)
