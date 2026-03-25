"""List Editor Widget - For managing bullet-point list fields."""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional


class ListEditor(ttk.Frame):
    """
    Widget for editing list items with add/remove/reorder functionality.
    
    Features:
    - Add new items
    - Remove selected items
    - Move items up/down
    - Visual list display
    - Get/set data methods
    """
    
    def __init__(self, parent, placeholder: str = "Add item...", on_change: Optional[Callable] = None):
        """
        Initialize the list editor.
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text for entry field
            on_change: Callback when list changes
        """
        super().__init__(parent)
        
        self.placeholder = placeholder
        self.on_change = on_change
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Main frame layout
        self.columnconfigure(0, weight=1)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox
        self.listbox = tk.Listbox(
            list_frame,
            height=6,
            selectmode=tk.SINGLE,
            font=("Arial", 10),
            bg="white",
            fg="black"
        )
        self.listbox.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # Entry field for new items
        entry_frame = ttk.Frame(self)
        entry_frame.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        entry_frame.columnconfigure(0, weight=1)
        
        self.entry = ttk.Entry(entry_frame, font=("Arial", 10))
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.entry.insert(0, self.placeholder)
        self.entry.config(foreground='gray')
        
        # Placeholder handling
        self.entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.entry.bind('<FocusOut>', self._on_entry_focus_out)
        self.entry.bind('<Return>', lambda e: self.add_item())
        
        # Button frame
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, sticky="ew")
        
        # Add button
        self.add_btn = ttk.Button(
            btn_frame,
            text="Add",
            command=self.add_item,
            width=8
        )
        self.add_btn.pack(side="left", padx=(0, 5))
        
        # Remove button
        self.remove_btn = ttk.Button(
            btn_frame,
            text="Remove",
            command=self.remove_item,
            width=8
        )
        self.remove_btn.pack(side="left", padx=(0, 5))
        
        # Move up button
        self.up_btn = ttk.Button(
            btn_frame,
            text="↑",
            command=self.move_up,
            width=3
        )
        self.up_btn.pack(side="left", padx=(0, 2))
        
        # Move down button
        self.down_btn = ttk.Button(
            btn_frame,
            text="↓",
            command=self.move_down,
            width=3
        )
        self.down_btn.pack(side="left")
        
        # Clear button
        self.clear_btn = ttk.Button(
            btn_frame,
            text="Clear All",
            command=self.clear_all,
            width=10
        )
        self.clear_btn.pack(side="right")
    
    def _on_entry_focus_in(self, event):
        """Handle entry field focus in."""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(foreground='black')
    
    def _on_entry_focus_out(self, event):
        """Handle entry field focus out."""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(foreground='gray')
    
    def add_item(self):
        """Add new item to list."""
        text = self.entry.get().strip()
        
        # Don't add placeholder or empty text
        if not text or text == self.placeholder:
            return
        
        # Add to listbox with bullet point
        self.listbox.insert(tk.END, f"• {text}")
        
        # Clear entry
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(foreground='gray')
        
        # Trigger change callback
        if self.on_change:
            self.on_change()
    
    def remove_item(self):
        """Remove selected item from list."""
        selection = self.listbox.curselection()
        if selection:
            self.listbox.delete(selection[0])
            
            # Trigger change callback
            if self.on_change:
                self.on_change()
    
    def move_up(self):
        """Move selected item up."""
        selection = self.listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        idx = selection[0]
        text = self.listbox.get(idx)
        
        self.listbox.delete(idx)
        self.listbox.insert(idx - 1, text)
        self.listbox.selection_set(idx - 1)
        
        # Trigger change callback
        if self.on_change:
            self.on_change()
    
    def move_down(self):
        """Move selected item down."""
        selection = self.listbox.curselection()
        if not selection or selection[0] == self.listbox.size() - 1:
            return
        
        idx = selection[0]
        text = self.listbox.get(idx)
        
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, text)
        self.listbox.selection_set(idx + 1)
        
        # Trigger change callback
        if self.on_change:
            self.on_change()
    
    def clear_all(self):
        """Clear all items from list."""
        if self.listbox.size() > 0:
            self.listbox.delete(0, tk.END)
            
            # Trigger change callback
            if self.on_change:
                self.on_change()
    
    def get_data(self) -> List[str]:
        """
        Get list of items without bullet points.
        
        Returns:
            List of item strings
        """
        items = []
        for i in range(self.listbox.size()):
            text = self.listbox.get(i)
            # Remove bullet point if present
            if text.startswith("• "):
                text = text[2:]
            items.append(text)
        return items
    
    def set_data(self, items: List[str]):
        """
        Set list items.
        
        Args:
            items: List of item strings
        """
        self.listbox.delete(0, tk.END)
        for item in items:
            if item:  # Skip empty items
                # Add bullet if not present
                if not item.startswith("• "):
                    item = f"• {item}"
                self.listbox.insert(tk.END, item)
