"""
PMhelper Edu — Educational Calculator Tab (abstract base).

Provides the common skeleton for all V2 calculator tabs:

* **Standalone input panel** — students type textbook problems directly.
* **"Load from Project" button** — pulls data from the active ``.pmproj``.
* **Results frame** — subclass fills with charts / tables.
* **Worked Solution panel** — step-by-step expandable section.
* **"Try It Yourself" toggle** — hides answers until the student submits.

Subclasses override the ``_build_*`` hooks and the calculation methods.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, List

from pmhelper.gui.widgets.worked_solution_window import WorkedSolutionWindow

if TYPE_CHECKING:
    from pmhelper.core.step_generators_edu import Step


class EducationalCalculatorTab:
    """Abstract base for V2 educational calculator tabs."""

    # Subclass should set a human-readable title
    TAB_TITLE: str = "Calculator"

    def __init__(self, parent: ttk.Notebook, state, *, main_window=None):
        self.parent = parent
        self.state = state
        self.main_window = main_window
        self._mode = "UG"

        self.frame = ttk.Frame(parent)

        # ── Master paned window: top = input/results, bottom = educational ──
        self._paned = ttk.PanedWindow(self.frame, orient=tk.VERTICAL)
        self._paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ── Top section ──
        top = ttk.Frame(self._paned)
        self._paned.add(top, weight=3)

        # Toolbar: Load from Project + Calculate
        self._toolbar = ttk.Frame(top)
        self._toolbar.pack(fill=tk.X, pady=(0, 4))

        self._load_btn = ttk.Button(
            self._toolbar, text="📂 Load from Project",
            command=self._on_load_from_project)
        self._load_btn.pack(side=tk.LEFT, padx=(0, 6))

        self._calc_btn = ttk.Button(
            self._toolbar, text="▶ Calculate",
            command=self._on_calculate)
        self._calc_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Try It Yourself toggle
        self._try_var = tk.BooleanVar(value=False)
        self._try_cb = ttk.Checkbutton(
            self._toolbar, text="🎓 Try It Yourself",
            variable=self._try_var,
            command=self._on_try_toggle)
        self._try_cb.pack(side=tk.RIGHT, padx=(6, 0))

        # Input area (subclass populates)
        self._input_frame = ttk.LabelFrame(top, text="Input")
        self._input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        self._build_input_panel(self._input_frame)

        # Results area (subclass populates)
        self._results_frame = ttk.LabelFrame(top, text="Results")
        self._results_frame.pack(fill=tk.BOTH, expand=True)
        self._build_results_panel(self._results_frame)

        # ── Bottom section: educational ──
        bottom = ttk.Frame(self._paned)
        self._paned.add(bottom, weight=1)

        edu_toolbar = ttk.Frame(bottom)
        edu_toolbar.pack(fill=tk.X, pady=(0, 4))

        self._worked_btn = ttk.Button(
            edu_toolbar, text="📖 Show Worked Solution",
            command=self._show_worked_solution)
        self._worked_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Practice frame (shown only in Try It Yourself mode)
        self._practice_frame = ttk.LabelFrame(bottom, text="Your Answers")
        self._practice_frame.pack(fill=tk.BOTH, expand=True)
        self._build_practice_panel(self._practice_frame)
        self._practice_frame.pack_forget()  # hidden by default

        # State
        self._last_steps: List["Step"] = []

    # ── Hooks for subclasses ────────────────────────────────────

    def _build_input_panel(self, parent: ttk.Frame) -> None:
        """Override: populate the standalone input area."""

    def _build_results_panel(self, parent: ttk.Frame) -> None:
        """Override: populate the results display area."""

    def _build_practice_panel(self, parent: ttk.Frame) -> None:
        """Override: populate the 'Try It Yourself' answer area."""

    def load_from_project(self) -> None:
        """Override: pull relevant data from ``self.state`` into the input panel."""

    def calculate(self) -> None:
        """Override: run the calculation, update the results panel.

        Should also populate ``self._last_steps`` with worked-solution Steps.
        """

    def check_answers(self) -> None:
        """Override: compare student answers in the practice panel to computed results."""

    # ── Standard interface (called by MainWindowEdu) ────────────

    def set_mode(self, mode: str) -> None:
        self._mode = mode.upper()

    def on_tab_selected(self) -> None:
        """Called when this tab becomes visible."""

    def update_results(self, *args, **kwargs) -> None:
        """Optional: update from external results (e.g. CPM analysis)."""

    def get_figures(self) -> list:
        """Return matplotlib Figure objects for chart export."""
        return []

    # ── Private handlers ────────────────────────────────────────

    def _on_load_from_project(self) -> None:
        self.load_from_project()

    def _on_calculate(self) -> None:
        self.calculate()
        # If in TIY mode, hide results
        if self._try_var.get():
            self._results_frame.pack_forget()

    def _on_try_toggle(self) -> None:
        if self._try_var.get():
            # Hide results, show practice
            self._results_frame.pack_forget()
            self._practice_frame.pack(fill=tk.BOTH, expand=True)
        else:
            # Show results, hide practice
            self._practice_frame.pack_forget()
            self._results_frame.pack(fill=tk.BOTH, expand=True)

    def _show_worked_solution(self) -> None:
        if not self._last_steps:
            from tkinter import messagebox
            messagebox.showinfo(
                "Worked Solution",
                "Run a calculation first to generate the worked solution.")
            return
        WorkedSolutionWindow(
            self.frame, f"{
                self.TAB_TITLE} — Worked Solution", self._last_steps)
