#!/usr/bin/env python3
"""
Quick test to verify GUI variable naming
"""

import tkinter as tk
from tkinter import ttk

def test_variable_conflict():
    """Test that different target_duration variables don't conflict"""
    
    root = tk.Tk()
    root.title("Variable Test")
    
    # Create variables like in the app
    prob_target_duration_var = tk.StringVar()  # For probability analysis
    target_duration_var = tk.StringVar(value="10")  # For crashing
    
    # Create entries
    frame = ttk.Frame(root)
    frame.pack(padx=20, pady=20)
    
    ttk.Label(frame, text="Probability Target:").grid(row=0, column=0)
    prob_entry = ttk.Entry(frame, textvariable=prob_target_duration_var)
    prob_entry.grid(row=0, column=1, padx=5)
    
    ttk.Label(frame, text="Crashing Target:").grid(row=1, column=0)
    crash_entry = ttk.Entry(frame, textvariable=target_duration_var)
    crash_entry.grid(row=1, column=1, padx=5)
    
    def check_values():
        prob_val = prob_target_duration_var.get()
        crash_val = target_duration_var.get()
        result_label.config(text=f"Prob: '{prob_val}', Crash: '{crash_val}'")
    
    ttk.Button(frame, text="Check Values", command=check_values).grid(row=2, column=0, columnspan=2, pady=10)
    
    result_label = ttk.Label(frame, text="")
    result_label.grid(row=3, column=0, columnspan=2)
    
    # Test setting values
    prob_target_duration_var.set("90")
    target_duration_var.set("10")
    
    check_values()
    
    print("Variables set successfully:")
    print(f"prob_target_duration_var: {prob_target_duration_var.get()}")
    print(f"target_duration_var: {target_duration_var.get()}")
    
    root.destroy()

if __name__ == "__main__":
    test_variable_conflict()
