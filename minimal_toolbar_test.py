#!/usr/bin/env python3
"""
Minimal test to understand matplotlib toolbar visibility requirements
"""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

def test_minimal_toolbar():
    print("🧪 MINIMAL MATPLOTLIB TOOLBAR TEST")
    print("=" * 40)
    
    # Create window
    root = tk.Tk()
    root.title("Minimal Toolbar Test")
    root.geometry("800x600")
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Method 1: Pack toolbar FIRST (PERT style)
    print("📊 Testing Method 1: Toolbar First (PERT style)")
    frame1 = ttk.LabelFrame(main_frame, text="Method 1: Toolbar First", padding="5")
    frame1.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Pack toolbar frame first at bottom
    toolbar_frame1 = ttk.Frame(frame1)
    toolbar_frame1.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Pack canvas frame second at top
    canvas_frame1 = ttk.Frame(frame1)
    canvas_frame1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Create figure and canvas
    fig1 = Figure(figsize=(6, 3), dpi=100)
    fig1.patch.set_facecolor('white')
    ax1 = fig1.add_subplot(111)
    ax1.plot([1, 2, 3, 4], [1, 4, 2, 3])
    ax1.set_title("Toolbar First Method")
    
    canvas1 = FigureCanvasTkAgg(fig1, canvas_frame1)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Create toolbar
    toolbar1 = NavigationToolbar2Tk(canvas1, toolbar_frame1)
    toolbar1.update()
    
    # Add debug info
    def check_toolbar1():
        height = toolbar_frame1.winfo_height()
        geometry = toolbar_frame1.winfo_geometry()
        print(f"  Method 1 - Height: {height}, Geometry: {geometry}")
    
    root.after(500, check_toolbar1)
    
    # Method 2: Pack canvas FIRST (original Network style)
    print("🌐 Testing Method 2: Canvas First (original Network style)")
    frame2 = ttk.LabelFrame(main_frame, text="Method 2: Canvas First", padding="5")
    frame2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Pack canvas frame first at top
    canvas_frame2 = ttk.Frame(frame2)
    canvas_frame2.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Pack toolbar frame second at bottom
    toolbar_frame2 = ttk.Frame(frame2)
    toolbar_frame2.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Create figure and canvas
    fig2 = Figure(figsize=(6, 3), dpi=100)
    fig2.patch.set_facecolor('white')
    ax2 = fig2.add_subplot(111)
    ax2.plot([4, 3, 2, 1], [1, 4, 2, 3])
    ax2.set_title("Canvas First Method")
    
    canvas2 = FigureCanvasTkAgg(fig2, canvas_frame2)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Create toolbar
    toolbar2 = NavigationToolbar2Tk(canvas2, toolbar_frame2)
    toolbar2.update()
    
    # Add debug info
    def check_toolbar2():
        height = toolbar_frame2.winfo_height()
        geometry = toolbar_frame2.winfo_geometry()
        print(f"  Method 2 - Height: {height}, Geometry: {geometry}")
    
    root.after(500, check_toolbar2)
    
    # Final check
    def final_check():
        print("\n🔍 FINAL COMPARISON:")
        print(f"  Method 1 (Toolbar First): {toolbar_frame1.winfo_height()}px")
        print(f"  Method 2 (Canvas First): {toolbar_frame2.winfo_height()}px")
        
        if toolbar_frame1.winfo_height() > toolbar_frame2.winfo_height():
            print("✅ Method 1 (Toolbar First) wins!")
        elif toolbar_frame2.winfo_height() > toolbar_frame1.winfo_height():
            print("✅ Method 2 (Canvas First) wins!")
        else:
            print("🤔 Both methods have same height")
    
    root.after(1000, final_check)
    
    print("👀 Visual inspection: Check which toolbar is actually visible in the GUI")
    root.mainloop()

if __name__ == "__main__":
    test_minimal_toolbar()
