"""PMhelper Edu — L3: PM Role & Organisation Tab.

Reference card covering the concepts from Lecture 3:
the project manager's role, key competencies, and organisational structures
(functional, projectised, matrix).
"""

import tkinter as tk
from tkinter import ttk


# ── Lecture 3 content ───────────────────────────────────────────────────

_SECTIONS = [
    ("The Project Manager's Role",
     ("The PM is responsible for leading the project team to achieve the project "
      "objectives within the agreed constraints.\n\n"
      "Core responsibilities:\n"
      "  • Define and communicate the project vision and goals\n"
      "  • Develop and maintain the project management plan\n"
      "  • Identify, track, and resolve issues and risks\n"
      "  • Manage stakeholder expectations and communications\n"
      "  • Monitor and control progress; manage change requests\n"
      "  • Close the project and hand over deliverables"),
     ),
    ("Key PM Competencies (PMI Talent Triangle)",
     ("PMI defines three domains of PM competency:\n\n"
      "  1. Technical PM Skills — scheduling, budgeting, risk, quality\n"
      "  2. Leadership Skills  — communication, motivation, conflict resolution, "
      "negotiation\n"
      "  3. Strategic & Business Management — understanding organisational context, "
      "aligning projects to strategy, benefits realisation\n\n"
      "Effective PMs balance all three domains."),
     ),
    ("Functional Organisation",
     ("The organisation is divided by business function (e.g., Engineering, "
      "Marketing, Finance).\n\n"
      "  ✔  Deep technical expertise within each department\n"
      "  ✔  Clear career paths and resource pooling\n"
      "  ✘  PM has little authority — resources report to functional managers\n"
      "  ✘  Poor cross-functional coordination; projects often deprioritised\n\n"
      "Best for: routine, functional work where projects are secondary."),
     ),
    ("Projectised (Project-Based) Organisation",
     ("Teams are organised around projects rather than functions.  The PM has "
      "full authority over the team and budget.\n\n"
      "  ✔  Strong PM authority; clear accountability\n"
      "  ✔  Team loyalty to the project; fast decision-making\n"
      "  ✘  Resource duplication — each project carries its own specialists\n"
      "  ✘  Team members face uncertainty when the project ends\n\n"
      "Best for: large, complex, long-duration projects (construction, defence)."),
     ),
    ("Matrix Organisation",
     ("A hybrid: functional departments exist, but PMs draw resources from them "
      "for specific projects.  Three sub-types:\n\n"
      "  Weak Matrix   — PM has limited authority; closer to functional\n"
      "  Balanced Matrix — shared authority between PM and functional manager\n"
      "  Strong Matrix  — PM has significant authority; closer to projectised\n\n"
      "  ✔  Efficient resource sharing across projects\n"
      "  ✔  Flexibility and specialist expertise available\n"
      "  ✘  Dual reporting creates ambiguity (PM vs. functional manager)\n"
      "  ✘  Potential for conflict over resource priorities\n\n"
      "Best for: organisations running multiple simultaneous projects."),
     ),
    ("Stakeholder Management Overview",
     ("Stakeholders are individuals or groups who may affect or be affected by "
      "the project.\n\n"
      "Key steps:\n"
      "  1. Identify — who has an interest or influence?\n"
      "  2. Analyse  — assess their power, interest, and attitude\n"
      "  3. Plan     — define engagement strategies\n"
      "  4. Engage   — communicate, consult, and manage expectations throughout\n\n"
      "The stakeholder register documents all identified stakeholders and "
      "their characteristics."),
     ),
]


class OrgTabEdu:
    """L3: PM Role & Organisation reference card."""

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
            text="L3 · The PM Role & Organisational Structures",
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
