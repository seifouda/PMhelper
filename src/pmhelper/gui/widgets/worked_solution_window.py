"""
PMhelper Edu — Worked Solution Window.

A scrollable Toplevel window that renders a list of Step objects as
expandable / collapsible cards with colour-coded RAG badges.

Provides "Copy as Text" and "Export PDF" actions.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from pmhelper.core.step_generators_edu import Step


# RAG badge colours
_RAG = {
    "green": "#27ae60",
    "amber": "#f39c12",
    "red":   "#e74c3c",
    "grey":  "#95a5a6",
}


class WorkedSolutionWindow(tk.Toplevel):
    """Pop-up window showing worked-solution steps."""

    def __init__(self, parent, title: str, steps: List["Step"]):
        super().__init__(parent)
        self.title(title)
        self.geometry("720x600")
        self.minsize(500, 350)
        self._steps = steps

        # ── Toolbar ──────────────────────────────────────────────
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, padx=6, pady=(6, 2))

        ttk.Button(toolbar, text="Copy as Text",
                   command=self._copy_text).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="Export PDF",
                   command=self._export_pdf).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="Expand All",
                   command=self._expand_all).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(toolbar, text="Collapse All",
                   command=self._collapse_all).pack(side=tk.RIGHT)

        # ── Scrollable area ──────────────────────────────────────
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self._canvas = tk.Canvas(container, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient=tk.VERTICAL,
                             command=self._canvas.yview)
        self._inner = ttk.Frame(self._canvas)

        self._inner.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))
        self._canvas.create_window((0, 0), window=self._inner, anchor="nw")
        self._canvas.configure(yscrollcommand=vsb.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse-wheel scrolling
        self._canvas.bind_all("<MouseWheel>",
                              lambda e: self._canvas.yview_scroll(
                                  int(-1 * (e.delta / 120)), "units"))
        self.bind("<Destroy>", self._on_destroy)

        # ── Render cards ─────────────────────────────────────────
        self._child_frames: List[dict] = []
        for step in steps:
            self._render_step(self._inner, step, depth=0)

    # ----------------------------------------------------------------
    #  Rendering helpers
    # ----------------------------------------------------------------

    def _render_step(self, parent, step: "Step", depth: int):
        """Render one step as a LabelFrame card, recursing into children."""
        pad_x = 10 + depth * 16

        # Card frame
        lf = ttk.LabelFrame(parent, text=step.title, padding=6)
        lf.pack(fill=tk.X, padx=(pad_x, 6), pady=3)

        # RAG colour stripe
        if step.rag and step.rag in _RAG:
            stripe = tk.Frame(lf, bg=_RAG[step.rag], width=6)
            stripe.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 6))

        body = ttk.Frame(lf)
        body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if step.formula:
            ttk.Label(body, text=step.formula,
                      font=("Consolas", 10)).pack(anchor="w")
        if step.substitution:
            for line in step.substitution.split("\n"):
                ttk.Label(body, text=line,
                          font=("Consolas", 10),
                          foreground="#2c3e50").pack(anchor="w")
        if step.result:
            ttk.Label(body, text=step.result,
                      font=("Consolas", 10, "bold"),
                      foreground="#1a5276").pack(anchor="w")
        if step.interpretation:
            ttk.Label(body, text=step.interpretation,
                      font=("Arial", 9, "italic"),
                      foreground="grey",
                      wraplength=580).pack(anchor="w", pady=(2, 0))

        # ── Children (collapsible) ────────────────────────────
        if step.children:
            child_container = ttk.Frame(parent)
            child_container.pack(fill=tk.X)

            toggle_var = tk.BooleanVar(value=False)
            entry = {"container": child_container,
                     "toggle": toggle_var,
                     "btn": None}

            def _toggle(cv=child_container, tv=toggle_var):
                if tv.get():
                    cv.pack_forget()
                    tv.set(False)
                else:
                    cv.pack(fill=tk.X)
                    tv.set(True)
                # Force scroll-region update
                self._inner.update_idletasks()
                self._canvas.configure(scrollregion=self._canvas.bbox("all"))

            btn = ttk.Button(lf, text=f"▶ Show {len(step.children)} sub-steps",
                             command=_toggle)
            btn.pack(anchor="w", pady=(2, 0))
            entry["btn"] = btn

            # Initially collapsed
            child_container.pack_forget()

            # Render children inside container
            for child in step.children:
                self._render_step(child_container, child, depth + 1)

            self._child_frames.append(entry)

    # ----------------------------------------------------------------
    #  Actions
    # ----------------------------------------------------------------

    def _copy_text(self):
        """Copy all steps as plain text to clipboard."""
        text = "\n\n".join(s.to_text() for s in self._steps)
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "Worked solution copied to clipboard.",
                            parent=self)

    def _export_pdf(self):
        """Export steps to a PDF file (requires reportlab)."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            from reportlab.pdfgen import canvas as pdf_canvas
        except ImportError:
            messagebox.showwarning(
                "Missing dependency",
                "Install reportlab to export PDF:\n  pip install reportlab",
                parent=self)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            parent=self)
        if not path:
            return

        c = pdf_canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 30 * mm
        margin = 20 * mm
        line_h = 14

        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, self.title())
        y -= line_h * 2

        def _write(text: str, font="Helvetica", size=10, indent=0):
            nonlocal y
            if y < 30 * mm:
                c.showPage()
                y = height - 20 * mm
            c.setFont(font, size)
            c.drawString(margin + indent, y, text)
            y -= line_h

        def _render_pdf(step, depth=0):
            indent = depth * 15
            _write(step.title, "Helvetica-Bold", 10, indent)
            if step.formula:
                _write(f"  Formula:        {step.formula}", "Courier", 9, indent)
            if step.substitution:
                for line in step.substitution.split("\n"):
                    _write(f"  Substitution:   {line}", "Courier", 9, indent)
            if step.result:
                _write(f"  Result:         {step.result}", "Courier", 9, indent)
            if step.interpretation:
                _write(f"  {step.interpretation}", "Helvetica-Oblique", 9, indent)
            for child in step.children:
                _render_pdf(child, depth + 1)

        for step in self._steps:
            _render_pdf(step)
            y -= line_h  # gap between top-level steps

        c.save()
        messagebox.showinfo("Exported", f"PDF saved to:\n{path}", parent=self)

    def _expand_all(self):
        for entry in self._child_frames:
            if not entry["toggle"].get():
                entry["container"].pack(fill=tk.X)
                entry["toggle"].set(True)
        self._inner.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _collapse_all(self):
        for entry in self._child_frames:
            if entry["toggle"].get():
                entry["container"].pack_forget()
                entry["toggle"].set(False)
        self._inner.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_destroy(self, event):
        """Unbind mouse-wheel when window is destroyed."""
        if event.widget is self:
            try:
                self._canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass
