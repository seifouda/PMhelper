"""Test: fix COM threading by initializing STA before clr import."""
import ctypes
# Force STA apartment model before anything else touches COM
ctypes.windll.ole32.CoInitializeEx(None, 2)  # COINIT_APARTMENTTHREADED

import sys
sys.path.insert(0, "src")

import tkinter as tk
from tkinter import ttk
from tkwebview2.tkwebview2 import WebView2

html_path = r"C:\Users\seifk\AppData\Local\Temp\pmhelper_plotly_test.html"

root = tk.Tk()
root.title("WebView2 Embed Test")
root.geometry("1200x800")

frame = WebView2(root, 1200, 800, url=html_path)
frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
