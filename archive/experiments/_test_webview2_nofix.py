"""Test: WebView2 embed without COM pre-init (testing if pywebview 4.4.1 works natively)."""
import sys
sys.path.insert(0, "src")

import tkinter as tk
from tkwebview2.tkwebview2 import WebView2

html_path = r"C:\Users\seifk\AppData\Local\Temp\pmhelper_plotly_test.html"

root = tk.Tk()
root.title("WebView2 Embed Test (no COM fix)")
root.geometry("1200x800")

frame = WebView2(root, 1200, 800, url=html_path)
frame.pack(fill=tk.BOTH, expand=True)

root.mainloop()
