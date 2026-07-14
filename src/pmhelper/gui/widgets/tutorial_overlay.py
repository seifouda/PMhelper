"""
PMhelper Edu – Interactive Tutorial Overlay  (v2)

Components per step
───────────────────
  4 tk.Frame   – accent-colour highlight border
  1 tk.Canvas  – pointer triangle
  1 tk.Frame   – tooltip card

New in v2
─────────
  • Progress bar        — thin coloured bar across the tooltip header
  • Keyboard-hint strip — ← → Esc F1 reminder at tooltip bottom
  • Welcome screen      — modal chapter overview before step 1
  • Smooth animation    — ease-out cubic interpolation on tooltip move
  • Finish celebration  — full-window card, auto-dismisses after 2.2 s
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from typing import Callable, List, Optional

# ── Design tokens ────────────────────────────────────────────
_ACCENT       = "#42a5f5"
_ACCENT_DARK  = "#1565c0"
_BORDER       = 2            # highlight border thickness (px)
_PAD          = 8            # spotlight padding around the target widget
_TIP_W        = 340          # tooltip card minimum width
_POINTER_SZ   = 12           # triangle pointer height (px)
_TIP_GAP      = 8            # gap between spotlight border and tooltip
_ANIM_STEPS   = 8            # frames per tooltip slide animation
_ANIM_MS      = 12           # ms between animation frames


@dataclass
class TutorialStep:
    """One step in the guided tutorial."""
    widget_fn: Callable[[], Optional[tk.Widget]]
    title: str
    description: str
    placement: str = "right"
    group: str = ""
    on_enter: Optional[Callable[[], None]] = None


class TutorialOverlay:
    """Highlights one widget at a time with a border + arrow + tooltip.

    Everything is a child of *root* positioned with place() so it
    stays inside the application window at all times.
    """

    def __init__(self, root: tk.Tk, steps: List[TutorialStep]):
        self._root      = root
        self._all_steps = steps
        self._steps:    List[TutorialStep] = []
        self._index     = -1

        self._borders:   List[tk.Frame]      = []   # 4 accent highlight strips
        self._pointer:   Optional[tk.Canvas] = None
        self._tooltip:   Optional[tk.Frame]  = None

        # Animation
        self._anim_id:    Optional[str]   = None
        self._anim_frame: int             = 0
        self._anim_src:   tuple[int, int] = (0, 0)
        self._anim_dst:   tuple[int, int] = (0, 0)
        self._anim_tip_w: int             = _TIP_W
        self._tip_placed: bool            = False   # snaps on first show

        self._reposition_id: Optional[str] = None
        self._cfg_bind_id:   Optional[str] = None

    # -- Public API --

    def start(self, filter_fn=None) -> None:
        self._steps = [
            s for s in self._all_steps
            if filter_fn is None or filter_fn(s)
        ]
        if not self._steps:
            return
        self._index      = 0
        self._tip_placed = False
        self._create_widgets()
        self._show_welcome()

    def close(self) -> None:
        self._cancel_anim()
        for w in self._borders:
            try:
                w.place_forget()
            except tk.TclError:
                pass
            try:
                w.destroy()
            except tk.TclError:
                pass
        self._borders.clear()
        for w in (self._pointer, self._tooltip):
            if w is not None:
                try:
                    w.place_forget()
                except tk.TclError:
                    pass
                try:
                    w.destroy()
                except tk.TclError:
                    pass
        self._pointer    = None
        self._tooltip    = None
        self._index      = -1
        self._tip_placed = False

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

        for seq in ("<Escape>", "<Right>", "<Left>"):
            try:
                self._root.unbind(seq)
            except tk.TclError:
                pass
        self._root.focus_force()

    @property
    def is_active(self):
        return self._index >= 0

    # -- Navigation --

    def next(self) -> None:
        if self._index + 1 >= len(self._steps):
            self._show_finish()
            return
        self._index += 1
        self._show_step()

    def back(self):
        if self._index <= 0:
            return
        self._index -= 1
        self._show_step()

    # -- Widget creation --

    def _create_widgets(self) -> None:
        # 4 thin accent highlight strips
        for _ in range(4):
            self._borders.append(tk.Frame(self._root, bg=_ACCENT))

        # Pointer triangle
        self._pointer = tk.Canvas(
            self._root, highlightthickness=0, bd=0,
            width=_POINTER_SZ * 2, height=_POINTER_SZ)

        # Tooltip card
        self._tooltip = tk.Frame(
            self._root, bg="white", bd=0,
            highlightbackground=_ACCENT_DARK, highlightthickness=1)
        self._build_tooltip()

        self._root.bind("<Escape>", self._on_escape)
        self._root.bind("<Right>",  self._on_right)
        self._root.bind("<Left>",   self._on_left)
        self._cfg_bind_id = self._root.bind("<Configure>", self._on_configure)

    def _build_tooltip(self) -> None:
        tip = self._tooltip

        # ── Dark header bar ──────────────────────────────────────────
        hdr = tk.Frame(tip, bg=_ACCENT_DARK)
        hdr.pack(fill=tk.X)

        self._badge = tk.Label(
            hdr, text="1 / 1", bg=_ACCENT, fg="white",
            font=("Segoe UI", 9, "bold"), padx=8, pady=5)
        self._badge.pack(side=tk.LEFT)

        self._title_lbl = tk.Label(
            hdr, text="", bg=_ACCENT_DARK, fg="white",
            font=("Segoe UI", 11, "bold"), anchor="w", pady=5)
        self._title_lbl.pack(side=tk.LEFT, padx=(10, 4), fill=tk.X, expand=True)

        tk.Button(
            hdr, text="✕", bg=_ACCENT_DARK, fg="#bbdefb",
            font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2",
            relief=tk.FLAT, activebackground="#1e3a5f",
            activeforeground="white", command=self.close,
            padx=8, pady=5,
        ).pack(side=tk.RIGHT)

        # ── Progress bar ──────────────────────────────────────────────
        prog_track = tk.Frame(tip, bg="#bbdefb", height=4)
        prog_track.pack(fill=tk.X)
        prog_track.pack_propagate(False)
        self._prog_bar = tk.Frame(prog_track, bg=_ACCENT, height=4)
        self._prog_bar.place(x=0, y=0, relheight=1, relwidth=0)

        # ── Description ───────────────────────────────────────────────
        self._desc = tk.Label(
            tip, text="", bg="white", fg="#37474f",
            font=("Segoe UI", 10), anchor="nw", justify=tk.LEFT,
            wraplength=_TIP_W - 32, padx=14, pady=10)
        self._desc.pack(fill=tk.X)

        # ── Navigation buttons ────────────────────────────────────────
        nav = tk.Frame(tip, bg="white")
        nav.pack(fill=tk.X, padx=12, pady=(0, 8))

        self._back_btn = ttk.Button(nav, text="← Back", command=self.back)
        self._back_btn.pack(side=tk.LEFT)

        self._next_btn = ttk.Button(nav, text="Next →", command=self.next)
        self._next_btn.pack(side=tk.RIGHT)

        # ── Keyboard hint strip ───────────────────────────────────────
        tk.Label(
            tip,
            text="← →  arrows   ·   Esc  close   ·   F1  replay",
            bg="#eceff1", fg="#90a4ae",
            font=("Segoe UI", 8), anchor="center", pady=4,
        ).pack(fill=tk.X)

    # ── Welcome screen ───────────────────────────────────────────────────────

    def _show_welcome(self) -> None:
        """Modal chapter-overview dialog shown before the first step."""
        dlg = tk.Toplevel(self._root)
        dlg.title("Tutorial Overview")
        dlg.resizable(False, False)
        dlg.transient(self._root)
        dlg.grab_set()
        dlg.configure(bg="white")

        def _on_cancel():
            dlg.destroy()
            self.close()

        def _on_start():
            dlg.destroy()
            self._root.after(60, self._show_step)

        dlg.protocol("WM_DELETE_WINDOW", _on_cancel)

        tk.Frame(dlg, bg=_ACCENT_DARK, height=4).pack(fill=tk.X)

        hdr = tk.Frame(dlg, bg=_ACCENT_DARK)
        hdr.pack(fill=tk.X)
        tk.Label(
            hdr, text="\U0001f393  Interactive Tutorial",
            bg=_ACCENT_DARK, fg="white",
            font=("Segoe UI", 14, "bold"), padx=18, pady=12,
        ).pack(side=tk.LEFT)
        tk.Label(
            hdr, text=f"{len(self._steps)} steps",
            bg=_ACCENT, fg="white",
            font=("Segoe UI", 9, "bold"), padx=8, pady=4,
        ).pack(side=tk.RIGHT, padx=12)

        body = tk.Frame(dlg, bg="white", padx=18, pady=14)
        body.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            body, text="Topics covered in this tutorial:",
            bg="white", fg="#607d8b",
            font=("Segoe UI", 10, "italic"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        seen: dict[str, int] = {}
        for s in self._steps:
            key = s.group or "General"
            seen[key] = seen.get(key, 0) + 1

        for i, (grp, cnt) in enumerate(seen.items()):
            row = (i // 2) + 1
            col = (i % 2) * 2
            tk.Frame(body, bg=_ACCENT, width=10, height=10).grid(
                row=row, column=col, padx=(0, 8), pady=4, sticky="w")
            tk.Label(
                body, text=f"{grp}  ({cnt})",
                bg="white", fg="#263238",
                font=("Segoe UI", 9, "bold"),
            ).grid(row=row, column=col + 1, sticky="w", padx=(0, 24))

        tk.Frame(dlg, bg="#e3f2fd", height=1).pack(fill=tk.X)
        foot = tk.Frame(dlg, bg="#fafafa", padx=16, pady=10)
        foot.pack(fill=tk.X)
        ttk.Button(foot, text="Cancel", command=_on_cancel).pack(side=tk.LEFT)
        ttk.Button(
            foot, text="Start Tutorial  \u2192", command=_on_start,
        ).pack(side=tk.RIGHT)

        dlg.update_idletasks()
        rx = self._root.winfo_rootx() + self._root.winfo_width()  // 2
        ry = self._root.winfo_rooty() + self._root.winfo_height() // 2
        dlg.geometry(
            f"+{rx - dlg.winfo_width() // 2}"
            f"+{ry - dlg.winfo_height() // 2}")

    # ── Finish celebration ────────────────────────────────────────────────────

    def _show_finish(self) -> None:
        """Tutorial complete — close the overlay immediately."""
        self.close()

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

    def _show_step(self) -> None:
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
                self._show_finish()
            return

        self._root.update_idletasks()

        try:
            wx, wy, ww, wh = self._root_rel(widget)
        except tk.TclError:
            self.next()
            return

        rw = self._root.winfo_width()
        rh = self._root.winfo_height()

        bx = wx - _PAD
        by = wy - _PAD
        bw = ww + _PAD * 2
        bh = wh + _PAD * 2

        # ── Highlight border ──────────────────────────────────────────────────
        b = _BORDER
        self._borders[0].place(x=bx - b, y=by - b,  width=bw + 2*b, height=b)   # top
        self._borders[1].place(x=bx - b, y=by + bh, width=bw + 2*b, height=b)   # bottom
        self._borders[2].place(x=bx - b, y=by,      width=b,         height=bh)  # left
        self._borders[3].place(x=bx + bw, y=by,     width=b,         height=bh)  # right
        for f in self._borders:
            f.lift()

        # ── Tooltip content ───────────────────────────────────────────
        total = len(self._steps)
        frac  = (self._index + 1) / total
        self._badge.config(text=f"{self._index + 1}  /  {total}")
        self._title_lbl.config(text=step.title)
        self._desc.config(text=step.description)
        self._back_btn.config(
            state=tk.DISABLED if self._index == 0 else tk.NORMAL)
        self._next_btn.config(
            text="Finish  \u2713" if self._index >= total - 1 else "Next  \u2192")
        self._prog_bar.place(x=0, y=0, relheight=1, relwidth=frac)

        # ── Position tooltip ──────────────────────────────────────────
        self._tooltip.update_idletasks()
        tip_w = max(self._tooltip.winfo_reqwidth(), _TIP_W)
        tip_h = self._tooltip.winfo_reqheight()

        gap  = _TIP_GAP + _POINTER_SZ
        side, tx, ty = self._pick_side(
            bx, by, bw, bh, tip_w, tip_h, rw, rh, step.placement, gap)

        tx = max(4, min(tx, rw - tip_w - 4))
        ty = max(4, min(ty, rh - tip_h - 4))

        self._animate_to(tx, ty, tip_w)
        self._draw_pointer(side, bx, by, bw, bh, tx, ty, tip_w, tip_h)
        self._tooltip.focus_force()

    # ── Smooth animation ──────────────────────────────────────────────────────

    def _cancel_anim(self) -> None:
        if self._anim_id is not None:
            try:
                self._root.after_cancel(self._anim_id)
            except (tk.TclError, ValueError):
                pass
            self._anim_id = None

    def _animate_to(self, tx: int, ty: int, tip_w: int) -> None:
        self._cancel_anim()
        self._anim_tip_w = tip_w

        if not self._tip_placed:
            # First appearance — snap immediately, no animation
            self._tooltip.place(x=tx, y=ty, width=tip_w)
            self._tooltip.lift()
            self._tip_placed = True
            return

        cur_x = self._tooltip.winfo_x()
        cur_y = self._tooltip.winfo_y()

        if abs(tx - cur_x) < 2 and abs(ty - cur_y) < 2:
            self._tooltip.place(x=tx, y=ty, width=tip_w)
            self._tooltip.lift()
            return

        self._anim_src   = (cur_x, cur_y)
        self._anim_dst   = (tx,    ty)
        self._anim_frame = 0

        def _tick() -> None:
            self._anim_frame += 1
            t    = self._anim_frame / _ANIM_STEPS
            ease = 1 - (1 - t) ** 3   # ease-out cubic
            sx, sy = self._anim_src
            ex, ey = self._anim_dst
            ix = int(sx + (ex - sx) * ease)
            iy = int(sy + (ey - sy) * ease)
            try:
                self._tooltip.place(x=ix, y=iy, width=self._anim_tip_w)
                self._tooltip.lift()
            except tk.TclError:
                return
            if self._anim_frame < _ANIM_STEPS:
                self._anim_id = self._root.after(_ANIM_MS, _tick)
            else:
                self._anim_id = None

        self._anim_id = self._root.after(_ANIM_MS, _tick)

    # -- Side picking --

    @staticmethod
    def _pick_side(bx, by, bw, bh, tip_w, tip_h, rw, rh, preferred, gap):
        br = bx + bw
        bb = by + bh

        candidates = {
            "right":  (rw - br, lambda: (br + gap, by)),
            "left":   (bx,      lambda: (bx - tip_w - gap, by)),
            "bottom": (rh - bb, lambda: (bx, bb + gap)),
            "top":    (by,      lambda: (bx, by - tip_h - gap)),
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
        """Draw a small triangle nub between the highlight and tooltip."""
        s = _POINTER_SZ
        root_bg = self._root.cget("bg")
        self._pointer.config(bg=root_bg)
        self._pointer.delete("all")

        if side == "right":
            # Triangle points LEFT toward the highlight
            px = tx - s
            py = ty + th // 2 - s
            self._pointer.place(x=px, y=py, width=s, height=s * 2)
            self._pointer.create_polygon(
                0, s,  s, 0,  s, s * 2,
                fill=_ACCENT, outline=_ACCENT)
        elif side == "left":
            # Triangle points RIGHT toward the highlight
            px = tx + tw
            py = ty + th // 2 - s
            self._pointer.place(x=px, y=py, width=s, height=s * 2)
            self._pointer.create_polygon(
                s, s,  0, 0,  0, s * 2,
                fill=_ACCENT, outline=_ACCENT)
        elif side == "bottom":
            # Triangle points UP toward the highlight
            px = tx + tw // 2 - s
            py = ty - s
            self._pointer.place(x=px, y=py, width=s * 2, height=s)
            self._pointer.create_polygon(
                s, 0,  0, s,  s * 2, s,
                fill=_ACCENT, outline=_ACCENT)
        else:  # top
            # Triangle points DOWN toward the highlight
            px = tx + tw // 2 - s
            py = ty + th
            self._pointer.place(x=px, y=py, width=s * 2, height=s)
            self._pointer.create_polygon(
                s, s,  0, 0,  s * 2, 0,
                fill=_ACCENT, outline=_ACCENT)

        tk.Misc.lift(self._pointer)

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
