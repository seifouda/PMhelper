"""
PMhelper Edu — Educational Edition Entry Point.

Launch with: python -m pmhelper.edu_main
This is completely independent from the main app (__main__.py).
"""

import tkinter as tk
from pmhelper.gui.main_window_edu import MainWindowEdu

# Pre-initialize COM as STA before Tkinter creates its window.
# Required for the embedded WebView2 (Plotly) chart renderer.
try:
    from pmhelper.gui.widgets.plotly_chart_frame import ensure_com_sta
    ensure_com_sta()
except Exception:
    pass


def main():
    root = tk.Tk()
    root.title("PMhelper Edu")
    root.geometry("1400x900")
    root.minsize(1200, 700)
    app = MainWindowEdu(root)
    root.mainloop()


if __name__ == "__main__":
    main()
