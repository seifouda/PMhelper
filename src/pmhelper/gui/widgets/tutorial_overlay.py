"""
PMhelper Edu - Interactive Tutorial Overlay.

Arrow-connected tooltip tutorial.  Every overlay widget is placed
*inside* the root window with place(), so they move, resize,
and minimise together with the application.

Components per step:
  4 thin Frame strips  - blue highlight border around the target
  1 Frame              - tooltip card with built-in pointer nub
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, List, Optional

_ACCENT = "#42a5f5"
_POINTER_COLOR = "#e53935"
_BORDER = 3
_PAD = 4
_TIP_W = 330
_POINTER_SIZE = 14            # triangle pointer height
_TOOLTIP_GAP = 6              # gap between highlight border and tooltip


@dataclass
class TutorialStep:
    """One step in the guided tutorial."""
    widget_fn: Callable[[], Optional[tk.Widget]]
    title: str
    description: str
    placement: str = "auto"
    group: str = ""
    on_enter: Optional[Callable[[], None]] = None


class TutorialOverlay:
    """Highlights one widget at a time with a border + arrow + tooltip.

    Everything is a child of *root* positioned with place() so it
    stays inside the application window at all times.
    """

    def __init__(self, root: tk.Tk, steps: List[TutorialStep]):
        self._root = root
        self._all_steps = steps
        self._steps: List[TutorialStep] = []
        self._index = -1

        self._borders: List[tk.Frame] = []
        self._pointer: Optional[tk.Canvas] = None   # small triangle nub
        self._tooltip: Optional[tk.Frame] = None
        self._reposition_id: Optional[str] = None
        self._cfg_bind_id: Optional[str] = None

    # -- Public API --

    def start(self, filter_fn=None):
        self._steps = [
            s for s in self._all_steps
            if filter_fn is None or filter_fn(s)
        ]
        if not self._steps:
            return
        self._index = 0
        self._create_widgets()
        self._show_step()

    def close(self):
        for w in self._borders:
            try:
                w.place_forget()
                w.destroy()
            except tk.TclError:
                pass
        self._borders.clear()
        for w in (self._pointer, self._tooltip):
            if w is not None:
                try:
                    w.place_forget()
                    w.destroy()
                except tk.TclError:
                    pass
        self._pointer = self._tooltip = None
        self._index = -1
        if self._reposition_id is not None:
            try:
                self._root.after_cancel(self._reposition_id)
            except (tk.TclError, ValueError):
                pass
            self._reposition_id = None
        if self._cfg_bind_id is not None:
            try:
                self._root.unbind("<Configure>", self._cfg_bind_id)
            except (tk.TclError, AttributeError):
                pass
            self._cfg_bind_id = None
        try:
            self._root.unbind("<Escape>")
            self._root.unbind("<Right>")
            self._root.unbind("<Left>")
        except tk.TclError:
            pass
        self._root.focus_force()

    @property
    def is_active(self):
        return self._index >= 0

    # -- Navigation --

    def next(self):
        if self._index + 1 >= len(self._steps):
            self.close()
            return
        self._index += 1
        self._show_step()

    def back(self):
        if self._index <= 0:
            return
        self._index -= 1
        self._show_step()

    # -- Widget creation --

    def _create_widgets(self):
        for _ in range(4):
            f = tk.Frame(self._root, bg=_ACCENT)
            self._borders.append(f)

        # Small triangle pointer (placed between highlight and tooltip)
        self._pointer = tk.Canvas(
            self._root, highlightthickness=0, bd=0,
            width=_POINTER_SIZE * 2, height=_POINTER_SIZE)

        self._tooltip = tk.Frame(
            self._root, bg="white", bd=0,
            highlightbackground="#bbdefb", highlightthickness=2)
        self._build_tooltip()

        self._root.bind("<Escape>", self._on_escape)
        self._root.bind("<Right>", self._on_right)
        self._root.bind("<Left>", self._on_left)
        self._cfg_bind_id = self._root.bind("<Configure>", self._on_configure)

    def _build_tooltip(self):
        tip = self._tooltip

        header = tk.Frame(tip, bg="white")
        header.pack(fill=tk.X, padx=12, pady=(10, 2))

        self._badge = tk.Label(
            header, text="1/1", bg="#1565c0", fg="white",
            font=("Segoe UI", 9, "bold"), padx=6, pady=1)
        self._badge.pack(side=tk.LEFT)

        self._title_lbl = tk.Label(
            header, text="", bg="white", fg="#1e293b",
            font=("Segoe UI", 11, "bold"), anchor="w")
        self._title_lbl.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)

        close_btn = tk.Button(
            header, text="✕", bg="white", fg="#90a4ae",
            font=("Segoe UI", 10), bd=0, cursor="hand2",
            activebackground="#eee", command=self.close)
        close_btn.pack(side=tk.RIGHT)

        self._desc = tk.Label(
            tip, text="", bg="white", fg="#546e7a",
            font=("Segoe UI", 10), anchor="nw", justify=tk.LEFT,
            wraplength=_TIP_W - 40)
        self._desc.pack(fill=tk.X, padx=12, pady=(0, 6))

        btn_frame = tk.Frame(tip, bg="white")
        btn_frame.pack(fill=tk.X, padx=12, pady=(0, 10))

        self._back_btn = ttk.Button(
            btn_frame, text="← Back", command=self.back)
        self._back_btn.pack(side=tk.LEFT, padx=(0, 4))

        self._next_btn = ttk.Button(
            btn_frame, text="Next →", command=self.next)
        self._next_btn.pack(side=tk.RIGHT)

    # -- Coordinate helper --

    def _root_rel(self, widget):
        """(x, y, w, h) of widget relative to root content area."""
        return (
            widget.winfo_rootx() - self._root.winfo_rootx(),
            widget.winfo_rooty() - self._root.winfo_rooty(),
            widget.winfo_width(),
            widget.winfo_height(),
        )

    # -- Step rendering --

    def _show_step(self):
        if self._index < 0 or self._index >= len(self._steps):
            self.close()
            return

        step = self._steps[self._index]

        # Run pre-step hook (e.g. switch to the correct tab)
        if step.on_enter is not None:
            try:
                step.on_enter()
                self._root.update_idletasks()
            except Exception:
                pass

        widget = step.widget_fn()

        if widget is None:
            if self._index + 1 < len(self._steps):
                self._index += 1
                self._show_step()
            else:
                self.close()
            return

        self._root.update_idletasks()

        try:
            wx, wy, ww, wh = self._root_rel(widget)
        except tk.TclError:
            self.next()
            return

        rw = self._root.winfo_width()
        rh = self._root.winfo_height()

        # -- Highlight border --
        pad = _PAD
        b = _BORDER
        bx = wx - pad
        by = wy - pad
        bw = ww + pad * 2
        bh = wh + pad * 2

        self._borders[0].place(x=bx - b, y=by - b,
                               width=bw + 2 * b, height=b)       # top
        self._borders[1].place(x=bx - b, y=by + bh,
                               width=bw + 2 * b, height=b)       # bottom
        self._borders[2].place(x=bx - b, y=by, width=b, height=bh)  # left
        self._borders[3].place(x=bx + bw, y=by, width=b, height=bh)  # right
        for f in self._borders:
            f.lift()

        # -- Update tooltip content --
        total = len(self._steps)
        self._badge.config(text=f"{self._index + 1} / {total}")
        self._title_lbl.config(text=step.title)
        self._desc.config(text=step.description)
        self._back_btn.config(
            state=tk.DISABLED if self._index == 0 else tk.NORMAL)
        self._next_btn.config(
            text="Finish ✓" if self._index >= total - 1
            else "Next →")

        # -- Position tooltip --
        self._tooltip.update_idletasks()
        tip_w = max(self._tooltip.winfo_reqwidth(), _TIP_W)
        tip_h = self._tooltip.winfo_reqheight()

        gap = _TOOLTIP_GAP + _POINTER_SIZE
        side, tx, ty = self._pick_side(
            bx, by, bw, bh, tip_w, tip_h, rw, rh, step.placement, gap)

        tx = max(4, min(tx, rw - tip_w - 4))
        ty = max(4, min(ty, rh - tip_h - 4))

        self._tooltip.place(x=tx, y=ty, width=tip_w)
        self._tooltip.lift()

        # -- Draw pointer triangle --
        self._draw_pointer(side, bx, by, bw, bh, tx, ty, tip_w, tip_h)
        self._tooltip.focus_force()

    # -- Side picking --

    @staticmethod
    def _pick_side(bx, by, bw, bh, tip_w, tip_h, rw, rh, preferred, gap):
        br = bx + bw
        bb = by + bh

        candidates = {
            "right": (rw - br, lambda: (br + gap, by)),
            "left": (bx, lambda: (bx - tip_w - gap, by)),
            "bottom": (rh - bb, lambda: (bx, bb + gap)),
            "top": (by, lambda: (bx, by - tip_h - gap)),
        }
        needed = {
            "right": tip_w + gap, "left": tip_w + gap,
            "bottom": tip_h + gap, "top": tip_h + gap,
        }

        if preferred != "auto" and preferred in candidates:
            avail, fn = candidates[preferred]
            if avail >= needed[preferred]:
                return preferred, *fn()

        order = sorted(candidates, key=lambda s: candidates[s][0],
                       reverse=True)
        for side in order:
            avail, fn = candidates[side]
            if avail >= needed[side]:
                return side, *fn()

        _, fn = candidates[order[0]]
        return order[0], *fn()

    # -- Pointer triangle --

    def _draw_pointer(self, side, bx, by, bw, bh, tx, ty, tw, th):
        """Draw a small red triangle between the highlight and tooltip."""
        s = _POINTER_SIZE
        root_bg = self._root.cget("bg")
        self._pointer.config(bg=root_bg)
        self._pointer.delete("all")

        if side == "right":
            # Triangle points LEFT toward the highlight
            px = tx - s
            py = ty + th // 2 - s
            self._pointer.place(x=px, y=py, width=s, height=s * 2)
            self._pointer.create_polygon(
                0, s, s, 0, s, s * 2,
                fill=_POINTER_COLOR, outline=_POINTER_COLOR)
        elif side == "left":
            # Triangle points RIGHT toward the highlight
            px = tx + tw
            py = ty + th // 2 - s
            self._pointer.place(x=px, y=py, width=s, height=s * 2)
            self._pointer.create_polygon(
                s, s, 0, 0, 0, s * 2,
                fill=_POINTER_COLOR, outline=_POINTER_COLOR)
        elif side == "bottom":
            # Triangle points UP toward the highlight
            px = tx + tw // 2 - s
            py = ty - s
            self._pointer.place(x=px, y=py, width=s * 2, height=s)
            self._pointer.create_polygon(
                s, 0, 0, s, s * 2, s,
                fill=_POINTER_COLOR, outline=_POINTER_COLOR)
        else:  # top
            # Triangle points DOWN toward the highlight
            px = tx + tw // 2 - s
            py = ty + th
            self._pointer.place(x=px, y=py, width=s * 2, height=s)
            self._pointer.create_polygon(
                s, s, 0, 0, s * 2, 0,
                fill=_POINTER_COLOR, outline=_POINTER_COLOR)

        self._pointer.lift()

    # -- Event handlers --

    def _on_configure(self, event):
        if not self.is_active or event.widget is not self._root:
            return
        if self._reposition_id is not None:
            try:
                self._root.after_cancel(self._reposition_id)
            except (tk.TclError, ValueError):
                pass
        self._reposition_id = self._root.after(50, self._reposition)

    def _reposition(self):
        self._reposition_id = None
        if self.is_active:
            self._show_step()

    def _on_escape(self, event):
        if self.is_active:
            self.close()

    def _on_right(self, event):
        if self.is_active:
            self.next()

    def _on_left(self, event):
        if self.is_active:
            self.back()
