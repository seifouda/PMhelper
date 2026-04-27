"""PMhelper Edu — L1: Foundations Tab.

Introductory reference card covering the core concepts from Lecture 1:
project definition, the triple constraint, lifecycle phases, and the
difference between projects and operations.
"""

import tkinter as tk
from tkinter import ttk


# ── Lecture 1 content ───────────────────────────────────────────────────

_SECTIONS = [
    ("What is a Project?",
     ("A project is a temporary endeavour undertaken to create a unique product, "
      "service, or result.  It has a defined beginning and end, distinct from ongoing "
      "operations.\n\n"
      "Key characteristics:\n"
      "  • Temporary — has a definite start and finish\n"
      "  • Unique — produces a one-of-a-kind deliverable\n"
      "  • Progressive elaboration — details refined as the project evolves"),
     ),
    ("The Triple Constraint",
     ("Every project is constrained by three competing dimensions:\n\n"
      "  ⏱  Scope  — what must be delivered\n"
      "  ⏱  Time   — when it must be delivered\n"
      "  ⏱  Cost   — budget available\n\n"
      "Quality is often added as a fourth dimension at the centre of the triangle.  "
      "Changing any one constraint forces a trade-off with the others."),
     ),
    ("Project Lifecycle Phases",
     ("Projects move through a sequence of phases:\n\n"
      "  1. Initiation   — define the project, obtain authorisation (Project Charter)\n"
      "  2. Planning     — develop the management plan, schedule, budget, risk register\n"
      "  3. Execution    — carry out the work, manage the team and stakeholders\n"
      "  4. Monitoring & Control — track performance, manage change\n"
      "  5. Closure      — finalise deliverables, release resources, lessons learned"),
     ),
    ("Projects vs. Operations",
     ("Projects are temporary and unique; operations are ongoing and repetitive.\n\n"
      "  Projects:    build a new hospital wing, launch a software product\n"
      "  Operations:  run the hospital, maintain the software\n\n"
      "Projects often transition into operations once the deliverable is handed over."),
     ),
    ("Project Success Criteria",
     ("A project is successful when it:\n\n"
      "  ✔  Delivers the agreed scope\n"
      "  ✔  Finishes within the approved schedule\n"
      "  ✔  Stays within the approved budget\n"
      "  ✔  Meets the required quality standards\n"
      "  ✔  Satisfies stakeholder expectations\n\n"
      "Modern PM frameworks also consider benefits realisation and strategic alignment."),
     ),
]


class FoundationsTabEdu:
    """L1: Foundations reference card."""

    def __init__(self, parent: tk.Widget, state=None, main_window=None):
        self.frame = ttk.Frame(parent)
        self._build_ui()

    # ── UI ──────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Header
        hdr = ttk.Frame(self.frame)
        hdr.pack(fill=tk.X, padx=12, pady=(10, 4))
        ttk.Label(
            hdr,
            text="L1 · Foundations of Project Management",
            font=("Segoe UI", 14, "bold"),
        ).pack(side=tk.LEFT)

        ttk.Separator(self.frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, padx=12, pady=(0, 8)
        )

        # Scrollable content area
        canvas = tk.Canvas(self.frame, highlightthickness=0)
        sb = ttk.Scrollbar(
            self.frame,
            orient=tk.VERTICAL,
            command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=4)

        inner = ttk.Frame(canvas)
        canvas_win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_resize(event):
            canvas.itemconfigure(canvas_win, width=event.width)

        inner.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_canvas_resize)

        # Bind mouse-wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Render sections
        for title, body in _SECTIONS:
            sec = ttk.LabelFrame(inner, text=title, padding=10)
            sec.pack(fill=tk.X, pady=6, padx=4)
            lbl = tk.Text(
                sec,
                wrap=tk.WORD,
                font=("Segoe UI", 10),
                relief=tk.FLAT,
                state=tk.DISABLED,
                background="#f5f5f5",
                height=1,
                cursor="arrow",
            )
            lbl.configure(state=tk.NORMAL)
            lbl.insert(tk.END, body)
            lbl.configure(state=tk.DISABLED)
            # Auto-size height to content
            lines = body.count("\n") + 3
            lbl.configure(height=lines)
            lbl.pack(fill=tk.X)

    # ── Common tab interface ────────────────────────────────────────────────

    def update_results(self, results_data=None):
        pass

    def set_mode(self, mode: str):
        pass

    def on_tab_selected(self):
        pass
