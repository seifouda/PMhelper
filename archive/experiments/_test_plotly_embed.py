"""Quick test: embed Plotly network in Tkinter via PlotlyChartFrame (WebView2)."""
import sys
sys.path.insert(0, "src")

import tkinter as tk
from tkinter import ttk
from pmhelper.gui.widgets.plotly_chart_frame import PlotlyChartFrame

# Load the pre-generated HTML
html_path = r"C:\Users\seifk\AppData\Local\Temp\pmhelper_plotly_test.html"

root = tk.Tk()
root.title("Plotly Embed Test - 600 Activity Network")
root.geometry("1200x800")

frame = PlotlyChartFrame(root)
frame.pack(fill=tk.BOTH, expand=True)

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()
frame.load_html(html)

root.mainloop()
