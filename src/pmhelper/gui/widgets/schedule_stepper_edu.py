"""
PMhelper Edu — Schedule Process Stepper Widget.

Horizontal progress bar showing the 5 PMBOK scheduling steps.
Each badge auto-detects completion from live project state and
is clickable to navigate to the relevant tab/column.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    pass  # avoid circular imports


# ── Step definitions ────────────────────────────────────────────────

_STEPS = [
    {
        "num": 1,
        "label": "Define Activities",
        "tooltip_pending": "Enter your project activities in the table below, "
                           "or load data from a CSV file.",
        "tooltip_done": "Activities defined — proceed to sequencing.",
    },
    {
        "num": 2,
        "label": "Sequence Activities",
        "tooltip_pending": "Set the Predecessors column to define task "
                           "dependencies (e.g., 'A, B'). The first activity "
                           "has no predecessors.",
        "tooltip_done": "Activity sequencing complete.",
    },
    {
        "num": 3,
        "label": "Estimate Resources",
        "tooltip_pending": "Optional: Set Resource Demand per activity to "
                           "enable resource-constrained scheduling.",
        "tooltip_done": "Resource estimates entered.",
        "optional": True,
    },
    {
        "num": 4,
        "label": "Estimate Durations",
        "tooltip_pending": "Enter a Duration for each activity (CPM) or "
                           "Optimistic/Most-Likely/Pessimistic estimates (PERT).",
        "tooltip_done": "All durations estimated.",
    },
    {
        "num": 5,
        "label": "Develop Schedule",
        "tooltip_pending": "Click ▶ Analyze to calculate the critical path, "
                           "float values, and project duration.",
        "tooltip_done": "Schedule developed — view Gantt and Results tabs.",
    },
]

# Colours
_GREEN = "#27ae60"
_GREEN_BG = "#e8f8f0"
_GREY = "#95a5a6"
_GREY_BG = "#f0f0f0"
_ARROW_GREY = "#bdc3c7"


class ScheduleStepperWidget(ttk.Frame):
    """Horizontal 5-step progress bar for the PMBOK scheduling process."""

    def __init__(self, parent, main_window=None):
        super().__init__(parent)
        self._main_window = main_window
        self._badges: List[dict] = []
        self._tooltip_window: Optional[tk.Toplevel] = None
        self._build_badges()

    # ──────────────────────────────────────────────────────────────
    #  Build
    # ──────────────────────────────────────────────────────────────

    def _build_badges(self):
        """Create the 5 badge frames with arrows between them."""
        for i, step in enumerate(_STEPS):
            if i > 0:
                # Arrow connector
                arrow = tk.Label(self, text="►", fg=_ARROW_GREY,
                                 font=("TkDefaultFont", 8))
                arrow.pack(side=tk.LEFT, padx=1)

            badge_frame = tk.Frame(
                self, bd=1, relief=tk.RIDGE, padx=6, pady=2,
                cursor="hand2")
            badge_frame.pack(side=tk.LEFT, padx=2)

            icon_lbl = tk.Label(badge_frame, text=str(step["num"]),
                                fg="white", bg=_GREY,
                                font=("TkDefaultFont", 8, "bold"),
                                width=2, anchor=tk.CENTER)
            icon_lbl.pack(side=tk.LEFT, padx=(0, 4))

            text_lbl = tk.Label(badge_frame, text=step["label"],
                                font=("TkDefaultFont", 8),
                                fg="#2c3e50")
            text_lbl.pack(side=tk.LEFT)

            badge_info = {
                "frame": badge_frame,
                "icon": icon_lbl,
                "text": text_lbl,
                "step": step,
                "state": "pending",
            }
            self._badges.append(badge_info)

            # Bind click + hover on all sub-widgets
            num = step["num"]
            for widget in (badge_frame, icon_lbl, text_lbl):
                widget.bind("<Button-1>", lambda e, n=num: self._on_click(n))
                widget.bind("<Enter>", lambda e, b=badge_info: self._show_tooltip(e, b))
                widget.bind("<Leave>", lambda e: self._hide_tooltip())

    # ──────────────────────────────────────────────────────────────
    #  Refresh (called by InputTabEdu + main_window)
    # ──────────────────────────────────────────────────────────────

    def refresh(self):
        """Re-detect completion of all 5 steps and update badges."""
        states = self._detect_steps()
        for badge in self._badges:
            num = badge["step"]["num"]
            new_state = states.get(num, "pending")
            badge["state"] = new_state
            self._apply_badge_style(badge, new_state)

    def _detect_steps(self) -> Dict[int, str]:
        """Return {step_num: "complete"|"pending"|"optional"} for all 5 steps."""
        activities = self._get_activities()
        results_data = self._get_results_data()
        mode = self._get_input_mode()

        states: Dict[int, str] = {}

        # Step 1 — Define Activities
        has_activities = len(activities) >= 1
        # PG: also accept WBS tree with children
        if not has_activities and self._has_wbs_children():
            has_activities = True
        states[1] = "complete" if has_activities else "pending"

        # Step 2 — Sequence Activities
        if len(activities) <= 1:
            # Single or zero activities — sequencing is trivially done
            states[2] = "complete" if has_activities else "pending"
        else:
            has_preds = any(
                str(a.get("predecessors", "")).strip()
                for a in activities
            )
            states[2] = "complete" if has_preds else "pending"

        # Step 3 — Estimate Resources (optional)
        has_resources = any(
            self._to_float(a.get("resource_demand", 0)) > 0
            for a in activities
        )
        states[3] = "complete" if has_resources else "optional"

        # Step 4 — Estimate Durations
        if not activities:
            states[4] = "pending"
        elif mode == "probabilistic":
            states[4] = "complete" if all(
                self._to_float(a.get("optimistic", 0)) > 0
                for a in activities
            ) else "pending"
        else:
            states[4] = "complete" if all(
                self._to_float(a.get("duration", 0)) > 0
                for a in activities
            ) else "pending"

        # Step 5 — Develop Schedule
        states[5] = "complete" if results_data is not None else "pending"

        return states

    # ──────────────────────────────────────────────────────────────
    #  Data access helpers (read-only from existing state)
    # ──────────────────────────────────────────────────────────────

    def _get_activities(self) -> list:
        """Get activities data from the input tab."""
        if self._main_window and hasattr(self._main_window, '_input_tab_edu'):
            tab = self._main_window._input_tab_edu
            if hasattr(tab, 'get_activities_data'):
                return tab.get_activities_data()
        return []

    def _get_results_data(self):
        """Check if analysis has been run."""
        if self._main_window and hasattr(self._main_window, 'results_data'):
            return self._main_window.results_data
        return None

    def _get_input_mode(self) -> str:
        """Get current input mode (deterministic/probabilistic)."""
        if self._main_window and hasattr(self._main_window, '_input_tab_edu'):
            return getattr(self._main_window._input_tab_edu, 'current_mode',
                           'deterministic') or 'deterministic'
        return "deterministic"

    def _has_wbs_children(self) -> bool:
        """Check if WBS tree has at least one child node (PG mode)."""
        if not self._main_window:
            return False
        state = getattr(self._main_window, 'state', None)
        if not state:
            return False
        wbs = getattr(state, 'wbs_tree', None)
        if wbs is None:
            return False
        roots = wbs.get_roots()
        if not roots:
            return False
        # Root exists — check if it has children
        return len(wbs.get_children(roots[0].id)) > 0

    @staticmethod
    def _to_float(val) -> float:
        """Safely convert a value to float."""
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    # ──────────────────────────────────────────────────────────────
    #  Badge styling
    # ──────────────────────────────────────────────────────────────

    def _apply_badge_style(self, badge: dict, state: str):
        """Update badge visual appearance based on state."""
        frame = badge["frame"]
        icon = badge["icon"]
        text_lbl = badge["text"]

        if state == "complete":
            frame.configure(bg=_GREEN_BG)
            icon.configure(text="✓", bg=_GREEN, fg="white")
            text_lbl.configure(fg=_GREEN, bg=_GREEN_BG)
        elif state == "optional":
            frame.configure(bg=_GREY_BG)
            icon.configure(text="○", bg=_GREY_BG, fg=_GREY)
            text_lbl.configure(fg=_GREY, bg=_GREY_BG)
        else:  # pending
            frame.configure(bg=_GREY_BG)
            icon.configure(text=str(badge["step"]["num"]),
                           bg=_GREY, fg="white")
            text_lbl.configure(fg="#2c3e50", bg=_GREY_BG)

    # ──────────────────────────────────────────────────────────────
    #  Click → tab navigation
    # ──────────────────────────────────────────────────────────────

    def _on_click(self, step_num: int):
        """Navigate to the relevant tab or column when a badge is clicked."""
        mw = self._main_window
        if not mw:
            return

        if step_num == 1:
            # Already on Input Activities — no-op
            pass
        elif step_num == 2:
            # Flash Predecessors column header
            self._flash_column("Predecessors")
        elif step_num == 3:
            # Flash Resource Demand column
            self._flash_column("Resource Demand")
        elif step_num == 4:
            # Flash Duration column (or Optimistic for PERT)
            mode = self._get_input_mode()
            col = "Optimistic" if mode == "probabilistic" else "Duration"
            self._flash_column(col)
        elif step_num == 5:
            # Click the Analyze button if data exists
            if hasattr(mw, '_input_tab_edu'):
                btn = getattr(mw._input_tab_edu, '_analyze_btn', None)
                if btn:
                    self._flash_widget(btn)

    def _flash_column(self, col_name: str):
        """Briefly highlight a column header in the treeview."""
        if not self._main_window:
            return
        tab = getattr(self._main_window, '_input_tab_edu', None)
        if not tab or not hasattr(tab, 'tree'):
            return
        tree = tab.tree
        # We can't directly colour treeview headers in ttk,
        # so flash the analyze button area as a visual cue instead.
        # Still useful: the column name appears in a brief label.
        self._show_flash_hint(f"→ {col_name}")

    def _flash_widget(self, widget):
        """Briefly flash a widget with yellow background."""
        try:
            orig = widget.cget("style") if isinstance(widget, ttk.Button) else None
            # Use a simple after-based flash
            widget.configure(style="Accent.TButton") if isinstance(widget, ttk.Button) else None
            self.after(500, lambda: None)  # brief pause
        except Exception:
            pass

    def _show_flash_hint(self, text: str):
        """Show a brief floating hint near the stepper."""
        hint = tk.Label(self, text=text, bg="#ffffcc", fg="#2c3e50",
                        font=("TkDefaultFont", 9, "bold"),
                        padx=8, pady=2, relief=tk.SOLID, bd=1)
        hint.place(relx=0.5, rely=1.0, anchor=tk.N)
        self.after(1200, hint.destroy)

    # ──────────────────────────────────────────────────────────────
    #  Tooltips
    # ──────────────────────────────────────────────────────────────

    def _show_tooltip(self, event, badge: dict):
        """Show a tooltip below the hovered badge."""
        self._hide_tooltip()
        step = badge["step"]
        state = badge["state"]
        if state == "complete":
            text = step["tooltip_done"]
        elif state == "optional":
            text = step["tooltip_pending"]
        else:
            text = step["tooltip_pending"]

        # Position tooltip below the badge
        x = event.widget.winfo_rootx()
        y = event.widget.winfo_rooty() + event.widget.winfo_height() + 4

        self._tooltip_window = tw = tk.Toplevel(self)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.configure(bg="#333")
        label = tk.Label(tw, text=text, bg="#333", fg="white",
                         font=("TkDefaultFont", 8),
                         wraplength=260, justify=tk.LEFT,
                         padx=6, pady=4)
        label.pack()

    def _hide_tooltip(self):
        """Destroy the tooltip window if it exists."""
        if self._tooltip_window:
            self._tooltip_window.destroy()
            self._tooltip_window = None
