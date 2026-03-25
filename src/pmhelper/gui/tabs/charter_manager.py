"""Charter Manager tab for listing and managing saved charters."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from ..models import CharterStatus
from ..services.storage_service import StorageService


class CharterManager(ttk.Frame):
    """Charter manager tab for viewing and managing saved charters."""
    
    def __init__(self, parent, on_open_callback=None, on_duplicate_callback=None):
        """Initialize the charter manager.
        
        Args:
            parent: Parent widget
            on_open_callback: Function to call when opening a charter (receives filepath)
            on_duplicate_callback: Function to call when duplicating a charter (receives filepath)
        """
        super().__init__(parent)
        
        self.storage_service = StorageService()
        self.on_open_callback = on_open_callback
        self.on_duplicate_callback = on_duplicate_callback
        self.charters: List[Dict] = []
        self.selected_charter: Optional[Dict] = None
        
        self._setup_ui()
        self._load_charters()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Create toolbar
        self._create_toolbar()
        
        # Create charter list
        self._create_charter_list()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_toolbar(self):
        """Create the toolbar with search and action buttons."""
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        # Search section
        search_frame = ttk.Frame(toolbar_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._on_search_change)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        
        # Sort options
        ttk.Label(search_frame, text="Sort by:").pack(side="left", padx=(20, 5))
        
        self.sort_var = tk.StringVar(value="modified_desc")
        sort_combo = ttk.Combobox(
            search_frame,
            textvariable=self.sort_var,
            values=[
                "Modified Date (Newest)",
                "Modified Date (Oldest)",
                "Title (A-Z)",
                "Title (Z-A)",
                "Status"
            ],
            state="readonly",
            width=25
        )
        sort_combo.pack(side="left", padx=5)
        sort_combo.bind('<<ComboboxSelected>>', self._on_sort_change)
        
        # Map display values to sort keys
        self.sort_map = {
            "Modified Date (Newest)": "modified_desc",
            "Modified Date (Oldest)": "modified_asc",
            "Title (A-Z)": "title_asc",
            "Title (Z-A)": "title_desc",
            "Status": "status"
        }
        
        # Action buttons
        action_frame = ttk.Frame(toolbar_frame)
        action_frame.pack(side="right")
        
        self.open_btn = ttk.Button(
            action_frame,
            text="Open",
            command=self._on_open_charter,
            width=12,
            state="disabled"
        )
        self.open_btn.pack(side="left", padx=5)
        
        self.duplicate_btn = ttk.Button(
            action_frame,
            text="Duplicate",
            command=self._on_duplicate_charter,
            width=12,
            state="disabled"
        )
        self.duplicate_btn.pack(side="left", padx=5)
        
        self.delete_btn = ttk.Button(
            action_frame,
            text="Delete",
            command=self._on_delete_charter,
            width=12,
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        self.refresh_btn = ttk.Button(
            action_frame,
            text="Refresh",
            command=self._load_charters,
            width=12
        )
        self.refresh_btn.pack(side="left", padx=5)
    
    def _create_charter_list(self):
        """Create the charter list view."""
        # Create container frame with scrollbar
        container = ttk.Frame(self)
        container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)
        
        # Create treeview
        columns = ('title', 'status', 'modified', 'completion')
        self.tree = ttk.Treeview(
            container,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        # Configure columns
        self.tree.heading('title', text='Project Title', command=lambda: self._sort_by('title'))
        self.tree.heading('status', text='Status', command=lambda: self._sort_by('status'))
        self.tree.heading('modified', text='Last Modified', command=lambda: self._sort_by('modified'))
        self.tree.heading('completion', text='Completion', command=lambda: self._sort_by('completion'))
        
        self.tree.column('title', width=300, minwidth=200)
        self.tree.column('status', width=100, minwidth=80)
        self.tree.column('modified', width=150, minwidth=120)
        self.tree.column('completion', width=100, minwidth=80)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)  # Right-click context menu
    
    def _create_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side="left")
        
        self.count_label = ttk.Label(status_frame, text="0 charters")
        self.count_label.pack(side="right")
    
    def _load_charters(self):
        """Load all charters from storage."""
        try:
            self.charters = self.storage_service.list_charters()
            self._update_charter_list()
            self._update_status(f"Loaded {len(self.charters)} charter(s)")
        except Exception as e:
            self._update_status(f"Error loading charters: {str(e)}")
            messagebox.showerror("Error", f"Failed to load charters: {str(e)}")
    
    def _update_charter_list(self):
        """Update the charter list view with current data."""
        # Get current sort key from display value
        display_value = self.sort_var.get()
        sort_key = self.sort_map.get(display_value, "modified_desc")
        self._update_charter_list_with_sort(sort_key)
    
    def _update_charter_list_with_sort(self, sort_key: str):
        """Update the charter list view with specific sort key.
        
        Args:
            sort_key: Sort key (modified_desc, modified_asc, title_asc, title_desc, status)
        """
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Filter charters based on search
        search_text = self.search_var.get().lower()
        filtered_charters = self.charters
        
        if search_text:
            filtered_charters = [
                c for c in self.charters
                if search_text in c.get('title', '').lower() or
                   search_text in c.get('status', '').lower()
            ]
        
        # Sort charters
        sort_key = self.sort_var.get()
        if sort_key == 'modified_desc':
            filtered_charters.sort(key=lambda c: c.get('modified_date', ''), reverse=True)
        elif sort_key == 'modified_asc':
            filtered_charters.sort(key=lambda c: c.get('modified_date', ''))
        elif sort_key == 'title_asc':
            filtered_charters.sort(key=lambda c: c.get('title', '').lower())
        elif sort_key == 'title_desc':
            filtered_charters.sort(key=lambda c: c.get('title', '').lower(), reverse=True)
        elif sort_key == 'status':
            filtered_charters.sort(key=lambda c: c.get('status', ''))
        
        # Add items to tree
        for charter in filtered_charters:
            # Format modified date
            modified_str = charter.get('modified_date', '')
            if modified_str:
                try:
                    modified_dt = datetime.fromisoformat(modified_str)
                    modified_str = modified_dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            # Format completion percentage
            completion = charter.get('completion', 0)
            completion_str = f"{completion:.0f}%"
            
            # Insert item
            self.tree.insert(
                '',
                'end',
                values=(
                    charter.get('title', 'Untitled'),
                    charter.get('status', 'unknown').upper(),
                    modified_str,
                    completion_str
                ),
                tags=(charter.get('filepath', ''),)
            )
        
        # Update count
        self.count_label.configure(text=f"{len(filtered_charters)} charter(s)")
    
    def _on_search_change(self, *args):
        """Handle search text change."""
        self._update_charter_list()
    
    def _on_sort_change(self, event):
        """Handle sort option change."""
        # Convert display value to sort key
        display_value = self.sort_var.get()
        sort_key = self.sort_map.get(display_value, "modified_desc")
        self._update_charter_list_with_sort(sort_key)
    
    def _sort_by(self, column: str):
        """Sort by the given column."""
        # Map column names to sort keys
        sort_map = {
            'title': 'title_asc',
            'status': 'status',
            'modified': 'modified_desc',
            'completion': 'completion'
        }
        
        if column in sort_map:
            self.sort_var.set(sort_map[column])
            self._update_charter_list()
    
    def _on_select(self, event):
        """Handle charter selection."""
        selection = self.tree.selection()
        if selection:
            # Get selected charter filepath from tags
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if tags:
                filepath = tags[0]
                # Find charter in list
                self.selected_charter = next(
                    (c for c in self.charters if c.get('filepath') == filepath),
                    None
                )
                
                # Enable action buttons
                self.open_btn.configure(state="normal")
                self.duplicate_btn.configure(state="normal")
                self.delete_btn.configure(state="normal")
        else:
            self.selected_charter = None
            self.open_btn.configure(state="disabled")
            self.duplicate_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
    
    def _on_double_click(self, event):
        """Handle double-click to open charter."""
        if self.selected_charter:
            self._on_open_charter()
    
    def _on_right_click(self, event):
        """Handle right-click to show context menu."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._show_context_menu(event)
    
    def _show_context_menu(self, event):
        """Show context menu."""
        if not self.selected_charter:
            return
        
        # Create context menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Open", command=self._on_open_charter)
        menu.add_command(label="Duplicate", command=self._on_duplicate_charter)
        menu.add_separator()
        menu.add_command(label="Delete", command=self._on_delete_charter)
        
        # Show menu
        menu.tk_popup(event.x_root, event.y_root)
    
    def _on_open_charter(self):
        """Handle open charter action."""
        if not self.selected_charter:
            return
        
        filepath = self.selected_charter.get('filepath')
        if filepath and self.on_open_callback:
            self.on_open_callback(filepath)
    
    def _on_duplicate_charter(self):
        """Handle duplicate charter action."""
        if not self.selected_charter:
            return
        
        filepath = self.selected_charter.get('filepath')
        if not filepath:
            return
        
        try:
            # Duplicate charter
            new_filepath = self.storage_service.duplicate_charter(filepath)
            if new_filepath:
                self._update_status(f"Charter duplicated: {Path(new_filepath).name}")
                self._load_charters()
                
                # Open duplicated charter if callback provided
                if self.on_duplicate_callback:
                    self.on_duplicate_callback(new_filepath)
            else:
                messagebox.showerror("Error", "Failed to duplicate charter.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to duplicate charter: {str(e)}")
    
    def _on_delete_charter(self):
        """Handle delete charter action."""
        if not self.selected_charter:
            return
        
        filepath = self.selected_charter.get('filepath')
        title = self.selected_charter.get('title', 'this charter')
        
        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{title}'?\n\nThis action cannot be undone."
        )
        
        if not response:
            return
        
        try:
            # Delete charter
            if self.storage_service.delete_charter(filepath):
                self._update_status(f"Deleted: {title}")
                self._load_charters()
            else:
                messagebox.showerror("Error", "Failed to delete charter.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete charter: {str(e)}")
    
    def _update_status(self, message: str):
        """Update status bar message."""
        self.status_label.configure(text=message)
    
    def refresh(self):
        """Refresh the charter list."""
        self._load_charters()
