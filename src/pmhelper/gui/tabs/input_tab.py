#!/usr/bin/env python3
"""
Input Tab Module

Handles the activity input interface for both CPM and PERT data entry.
Supports dynamic column switching between deterministic and probabilistic modes.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
from pathlib import Path
import csv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from pmhelper.utils.file_handlers import FileHandler


class InputTab:
    """Input tab for activity data entry"""
    
    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.current_mode = None
        
        self.create_tab()
    
    def create_tab(self):
        """Create the input tab"""
        self.input_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.input_frame, text="Input Activities")
        
        # Create button frame
        self.create_button_frame()
        
        # Create mode indicator
        self.mode_label = ttk.Label(self.input_frame, text="Mode: None", 
                                font=("Arial", 10, "bold"))
        self.mode_label.pack(anchor="w", pady=(0, 5))
        
        # Create tree frame (will contain the treeview)
        self.tree_frame = ttk.Frame(self.input_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Start with deterministic layout
        self.setup_deterministic_tree()
    
    def create_button_frame(self):
        """Create the button frame with all control buttons"""
        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # File loading buttons
        ttk.Button(button_frame, text="Load CPM Data", 
                command=self.load_deterministic_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Load PERT Data", 
                command=self.load_probabilistic_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Auto-Detect CSV", 
                command=self.load_csv_auto_detect).pack(side=tk.LEFT, padx=(0, 10))
        
        # Row manipulation buttons
        ttk.Button(button_frame, text="Add Row", 
                  command=self.add_row).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Delete Row", 
                  command=self.delete_row).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        
        # Sample data buttons
        ttk.Button(button_frame, text="Load Sample CPM", 
                  command=self.load_sample_cpm).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Load Sample PERT", 
                  command=self.load_sample_pert).pack(side=tk.LEFT, padx=(0, 10))
        
        # Analysis button
        ttk.Button(button_frame, text="Analyze Project", 
                  command=self.main_window.analyze_project).pack(side=tk.RIGHT)
    
    def setup_deterministic_tree(self):
        """Setup treeview for deterministic (CPM) data"""
        self.clear_tree_frame()
        
        # CPM columns
        columns = ("ID", "Activity", "Duration", "Predecessors", "Min Duration", 
                  "Crash Cost", "Resource Demand", "Normal Cost")
        
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ["ID"]:
                self.tree.column(col, width=50, minwidth=50)
            elif col in ["Duration", "Min Duration", "Resource Demand"]:
                self.tree.column(col, width=80, minwidth=70)
            elif col in ["Crash Cost", "Normal Cost"]:
                self.tree.column(col, width=100, minwidth=80)
            elif col == "Predecessors":
                self.tree.column(col, width=120, minwidth=100)
            else:
                self.tree.column(col, width=150, minwidth=120)
        # Add only vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind double-click for editing
        self.tree.bind('<Double-1>', self.edit_item)
        
        self.current_mode = 'deterministic'
    
    def setup_probabilistic_tree(self):
        """Setup treeview for probabilistic (PERT) data"""
        self.clear_tree_frame()
        
        # PERT columns (add normal_cost)
        columns = ("ID", "Activity", "Optimistic", "Most Likely", "Pessimistic", "Predecessors", "Min Duration", "Crash Cost", "Resource Demand", "Normal Cost")
        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings', height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            if col in ["ID"]:
                self.tree.column(col, width=50, minwidth=50)
            elif col in ["Optimistic", "Most Likely", "Pessimistic", "Min Duration", "Resource Demand"]:
                self.tree.column(col, width=80, minwidth=70)
            elif col in ["Crash Cost", "Normal Cost"]:
                self.tree.column(col, width=100, minwidth=80)
            elif col == "Predecessors":
                self.tree.column(col, width=120, minwidth=100)
            else:
                self.tree.column(col, width=150, minwidth=120)
        
        self.tree.bind('<Double-1>', self.edit_item)
        self.current_mode = 'probabilistic'
    
    def clear_tree_frame(self):
        """Clear the tree frame of all widgets"""
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
    
    def set_mode(self, mode):
        """Set the input mode and reconfigure the interface"""
        # Always update the interface layout even if mode appears the same
        # This ensures visual consistency and proper synchronization
        
        if mode == 'deterministic':
            # Only recreate tree if mode actually changed to avoid unnecessary work
            if mode != self.current_mode:
                self.setup_deterministic_tree()
            self.mode_label.config(text="Mode: CPM (Deterministic)")
            # Don't call main_window.set_analysis_mode here to avoid circular calls
        elif mode == 'probabilistic':
            # Add only vertical scrollbar
            v_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
            self.tree.configure(yscrollcommand=v_scrollbar.set)
            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.mode_label.config(text="Mode: None")
            if mode != self.current_mode:
                # Clear the tree for unknown mode
                self.clear_tree_frame()
    
    def load_deterministic_data(self):
        """Load deterministic (CPM) data from file with validation"""
        filename = filedialog.askopenfilename(
            title="Load CPM Data",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            # Validate that the file contains CPM data before loading
            if self.validate_file_format(filename, 'deterministic'):
                self.load_file(filename, 'deterministic')
            else:
                messagebox.showerror(
                    "Invalid Data Format", 
                    "This file appears to contain PERT data (with optimistic, most_likely, pessimistic columns).\n\n"
                    "To load CPM data, please select a file with a 'duration' column.\n"
                    "To load this PERT file, use the 'Load PERT Data' button instead."
                )
    
    def auto_detect_mode(self, csv_headers):
        """
        Automatically detect analysis mode based on CSV column headers
        
        Args:
            csv_headers (list): List of column headers from CSV
            
        Returns:
            str: 'deterministic' for CPM mode, 'probabilistic' for PERT mode
        """
        # Convert headers to lowercase for case-insensitive comparison
        headers_lower = [header.lower().strip() for header in csv_headers]
        
        # Check for PERT-specific columns (optimistic, pessimistic, most_likely)
        pert_indicators = ['optimistic', 'pessimistic', 'most_likely']
        has_pert_columns = any(indicator in headers_lower for indicator in pert_indicators)
        
        # Check for CPM-specific column (duration)
        has_duration = 'duration' in headers_lower
        
        # Decision logic
        if has_pert_columns:
            detected_mode = 'probabilistic'
        elif has_duration:
            detected_mode = 'deterministic'
        else:
            # Default to deterministic if ambiguous
            detected_mode = 'deterministic'
        
        return detected_mode
    
    def validate_file_format(self, filename, expected_mode):
        """
        Validate that the file format matches the expected mode
        
        Args:
            filename (str): Path to the file to validate
            expected_mode (str): Expected mode ('deterministic' or 'probabilistic')
            
        Returns:
            bool: True if file format matches expected mode, False otherwise
        """
        try:
            # Read just the headers to check format
            if filename.lower().endswith('.xlsx'):
                import pandas as pd
                df = pd.read_excel(filename, nrows=0)  # Read only headers
                headers = df.columns.tolist()
            else:
                import csv
                with open(filename, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    headers = next(reader, [])
            
            if not headers:
                # Empty file, allow loading (will show appropriate error later)
                return True
            
            # Auto-detect the actual mode of the file
            detected_mode = self.auto_detect_mode(headers)
            
            # Check if detected mode matches expected mode
            return detected_mode == expected_mode
            
        except Exception:
            # If we can't read the file, let the regular loading process handle the error
            return True
    
    def load_csv_auto_detect(self):
        """Load CSV with automatic mode detection based on column headers"""
        filename = filedialog.askopenfilename(
            title="Select CSV file (Auto-detect mode)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Read CSV headers to detect mode
                with open(filename, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    headers = reader.fieldnames
                    
                    if not headers:
                        messagebox.showerror("Error", "CSV file appears to be empty or invalid.")
                        return
                    
                    # Auto-detect mode based on headers
                    detected_mode = self.auto_detect_mode(headers)
                    
                    # Clear existing data
                    self.clear_all_without_confirmation()
                    
                    # Set the detected mode (this will update the UI layout)
                    self.set_mode(detected_mode)
                    
                    # Load the data
                    activities_data = []
                    file.seek(0)  # Reset file pointer
                    reader = csv.DictReader(file)
                    
                    for row in reader:
                        if detected_mode == 'probabilistic':
                            # PERT data structure
                            activity_dict = {
                                'id': row.get('id', ''),
                                'activity': row.get('activity', ''),
                                'optimistic': row.get('optimistic', ''),
                                'most_likely': row.get('most_likely', ''),
                                'pessimistic': row.get('pessimistic', ''),
                                'predecessors': row.get('predecessors', ''),
                                'min_duration': row.get('min_duration', ''),
                                'crash_cost': row.get('crash_cost', ''),
                                'resource_demand': row.get('resource_demand', ''),
                                'normal_cost': row.get('normal_cost', '')
                            }
                        else:
                            # CPM data structure  
                            activity_dict = {
                                'id': row.get('id', ''),
                                'activity': row.get('activity', ''),
                                'duration': row.get('duration', ''),
                                'predecessors': row.get('predecessors', ''),
                                'min_duration': row.get('min_duration', ''),
                                'crash_cost': row.get('crash_cost', ''),
                                'resource_demand': row.get('resource_demand', ''),
                                'normal_cost': row.get('normal_cost', '')
                            }
                        activities_data.append(activity_dict)
                    
                    # Populate the tree with the loaded data
                    self.populate_tree(activities_data)
                    
                    # Update main window analysis mode (this will sync the main window)
                    self.main_window.set_analysis_mode(detected_mode)
                    
                    messagebox.showinfo("Success", 
                                      f"CSV file loaded successfully!\n"
                                      f"Mode: {detected_mode.title()} (Auto-detected)\n"
                                      f"Activities loaded: {len(activities_data)}")
                    
                    self.main_window.set_status(f"Loaded {len(activities_data)} activities with auto-detected {detected_mode} mode")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")
    
    def clear_all_without_confirmation(self):
        """Clear all data without asking for confirmation (for internal use)"""
        for item in self.tree.get_children():
            self.tree.delete(item)
    
    def load_probabilistic_data(self):
        """Load probabilistic (PERT) data from file with validation"""
        filename = filedialog.askopenfilename(
            title="Load PERT Data",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        if filename:
            # Validate that the file contains PERT data before loading
            if self.validate_file_format(filename, 'probabilistic'):
                self.load_file(filename, 'probabilistic')
            else:
                messagebox.showerror(
                    "Invalid Data Format", 
                    "This file appears to contain CPM data (with duration column only).\n\n"
                    "To load PERT data, please select a file with 'optimistic', 'most_likely', and 'pessimistic' columns.\n"
                    "To load this CPM file, use the 'Load CPM Data' button instead."
                )
    
    def load_file(self, filename, mode):
        """Load data from file with format validation"""
        try:
            # Validate file format before loading
            if not self.validate_file_format(filename, mode):
                return  # validation_file_format already shows the error message
            
            # Load data based on file type
            if filename.lower().endswith('.xlsx'):
                activities_data = FileHandler.load_excel(filename)
            else:
                activities_data = FileHandler.load_csv(filename)
            
            # Set mode and populate data
            self.set_mode(mode)
            self.populate_tree(activities_data)
            
            # Update main window analysis mode
            self.main_window.set_analysis_mode(mode)
            
            self.main_window.set_status(f"Loaded {len(activities_data)} activities from {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")
    
    def populate_tree(self, activities_data):
        """Populate the treeview with data"""
        # Always recreate the treeview before populating
        if self.current_mode == 'deterministic':
            self.setup_deterministic_tree()
        else:
            self.setup_probabilistic_tree()
        # Add new data
        for activity in activities_data:
            if self.current_mode == 'deterministic':
                values = (
                    activity.get('id', ''),
                    activity.get('activity', ''),
                    activity.get('duration', ''),
                    activity.get('predecessors', ''),
                    activity.get('min_duration', ''),
                    activity.get('crash_cost', ''),
                    activity.get('resource_demand', ''),
                    activity.get('normal_cost', '')
                )
            else:  # probabilistic
                values = (
                    activity.get('id', ''),
                    activity.get('activity', ''),
                    activity.get('optimistic', ''),
                    activity.get('most_likely', ''),
                    activity.get('pessimistic', ''),
                    activity.get('predecessors', ''),
                    activity.get('min_duration', ''),
                    activity.get('crash_cost', ''),
                    activity.get('resource_demand', ''),
                    activity.get('normal_cost', '')
                )
            self.tree.insert("", tk.END, values=values)
    
    def add_row(self):
        """Add a new empty row"""
        if self.current_mode == 'deterministic':
            values = ("", "", "", "", "", "", "", "")
        else:  # probabilistic
            values = ("", "", "", "", "", "", "", "", "", "")
        self.tree.insert("", tk.END, values=values)
    
    def delete_row(self):
        """Delete selected row"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a row to delete.")
            return
        
        for item in selected_items:
            self.tree.delete(item)
    
    def clear_all(self):
        """Clear all data"""
        result = messagebox.askyesno("Clear All", "Are you sure you want to clear all data?")
        if result:
            try:
                if self.tree and self.tree.winfo_exists():
                    for item in self.tree.get_children():
                        self.tree.delete(item)
            except Exception as e:
                print(f"Warning: Tried to clear tree but it was not valid. Error: {e}")
    
    def edit_item(self, event):
        """Handle double-click editing"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        column = self.tree.identify_column(event.x)
        if not column:
            return
        
        # Get column index (column returns '#1', '#2', etc.)
        col_index = int(column.replace('#', '')) - 1
        
        # Get current value
        current_values = list(self.tree.item(item, 'values'))
        current_value = current_values[col_index] if col_index < len(current_values) else ""
        
        # Create entry widget for editing
        self.edit_entry = tk.Entry(self.tree)
        self.edit_entry.insert(0, current_value)
        
        # Position the entry widget
        bbox = self.tree.bbox(item, column)
        if bbox:
            self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            self.edit_entry.focus()
            self.edit_entry.select_range(0, tk.END)
            
            # Bind events
            self.edit_entry.bind('<Return>', lambda e: self.save_edit(item, col_index))
            self.edit_entry.bind('<Escape>', lambda e: self.cancel_edit())
            self.edit_entry.bind('<FocusOut>', lambda e: self.save_edit(item, col_index))
    
    def save_edit(self, item, col_index):
        """Save the edited value"""
        if hasattr(self, 'edit_entry'):
            new_value = self.edit_entry.get()
            current_values = list(self.tree.item(item, 'values'))
            
            # Ensure we have enough values
            while len(current_values) <= col_index:
                current_values.append('')
            
            current_values[col_index] = new_value
            self.tree.item(item, values=current_values)
            self.cancel_edit()
    
    def cancel_edit(self):
        """Cancel editing"""
        if hasattr(self, 'edit_entry'):
            self.edit_entry.destroy()
            delattr(self, 'edit_entry')
    
    def load_sample_cpm(self):
        """Load sample CPM data"""
        sample_data = FileHandler.get_sample_cpm_data()
        self.set_mode('deterministic')
        self.populate_tree(sample_data)
        # Update main window analysis mode (single call, no duplicate)
        self.main_window.set_analysis_mode('deterministic')
        self.main_window.set_status("Loaded sample CPM data")
    
    def load_sample_pert(self):
        """Load sample PERT data and display in the treeview"""
        self.clear_tree_frame()  # Destroy old widgets
        self.setup_probabilistic_tree()  # Recreate treeview for PERT columns
        sample_data = FileHandler.get_sample_pert_data()
        self.populate_tree(sample_data)  # Now safe to populate
        self.main_window.set_analysis_mode('probabilistic')
        self.main_window.set_status("Loaded sample PERT data")
    
    def load_sample_data(self):
        """Load default sample data (CPM)"""
        self.load_sample_cpm()
    
    def get_activities_data(self):
        """Get activities data from the treeview"""
        activities_data = []
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if not values or not values[0].strip():  # Skip empty rows
                continue
            if self.current_mode == 'deterministic':
                activity_dict = {
                    'id': values[0] if len(values) > 0 else '',
                    'activity': values[1] if len(values) > 1 else '',
                    'duration': values[2] if len(values) > 2 else '',
                    'predecessors': values[3] if len(values) > 3 else '',
                    'min_duration': values[4] if len(values) > 4 else '',
                    'crash_cost': values[5] if len(values) > 5 else '',
                    'resource_demand': values[6] if len(values) > 6 else '',
                    'normal_cost': values[7] if len(values) > 7 else ''
                }
            else:  # probabilistic
                activity_dict = {
                    'id': values[0] if len(values) > 0 else '',
                    'activity': values[1] if len(values) > 1 else '',
                    'optimistic': values[2] if len(values) > 2 else '',
                    'most_likely': values[3] if len(values) > 3 else '',
                    'pessimistic': values[4] if len(values) > 4 else '',
                    'predecessors': values[5] if len(values) > 5 else '',
                    'min_duration': values[6] if len(values) > 6 else '',
                    'crash_cost': values[7] if len(values) > 7 else '',
                    'resource_demand': values[8] if len(values) > 8 else '',
                    'normal_cost': values[9] if len(values) > 9 else ''
                }
            activities_data.append(activity_dict)
        return activities_data

    def load_csv_auto_detect(self):
        """Load CSV with automatic mode detection based on column headers"""
        filename = filedialog.askopenfilename(
            title="Select CSV file (Auto-detect mode)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    headers = reader.fieldnames
                    if not headers:
                        messagebox.showerror("Error", "CSV file appears to be empty or invalid.")
                        return
                    detected_mode = self.auto_detect_mode(headers)
                    self.clear_tree_frame()
                    if detected_mode == 'probabilistic':
                        self.setup_probabilistic_tree()
                    else:
                        self.setup_deterministic_tree()
                    activities_data = []
                    file.seek(0)
                    reader = csv.DictReader(file)
                    for row in reader:
                        if detected_mode == 'probabilistic':
                            activity_dict = {
                                'id': row.get('id', ''),
                                'activity': row.get('activity', ''),
                                'optimistic': row.get('optimistic', ''),
                                'most_likely': row.get('most_likely', ''),
                                'pessimistic': row.get('pessimistic', ''),
                                'predecessors': row.get('predecessors', ''),
                                'min_duration': row.get('min_duration', ''),
                                'crash_cost': row.get('crash_cost', ''),
                                'resource_demand': row.get('resource_demand', ''),
                                'normal_cost': row.get('normal_cost', '')
                            }
                        else:
                            activity_dict = {
                                'id': row.get('id', ''),
                                'activity': row.get('activity', ''),
                                'duration': row.get('duration', ''),
                                'predecessors': row.get('predecessors', ''),
                                'min_duration': row.get('min_duration', ''),
                                'crash_cost': row.get('crash_cost', ''),
                                'resource_demand': row.get('resource_demand', ''),
                                'normal_cost': row.get('normal_cost', '')
                            }
                        activities_data.append(activity_dict)
                    self.populate_tree(activities_data)
                    self.main_window.set_analysis_mode(detected_mode)
                    messagebox.showinfo("Success", 
                                        f"CSV file loaded successfully!\n"
                                        f"Mode: {detected_mode.title()} (Auto-detected)\n"
                                        f"Activities loaded: {len(activities_data)}")
                    self.main_window.set_status(f"Loaded {len(activities_data)} activities with auto-detected {detected_mode} mode")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")
