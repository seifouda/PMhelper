"""Collapsible section widget for forms."""

import tkinter as tk
from tkinter import ttk


class CollapsibleSection(ttk.Frame):
    """
    A collapsible section widget with expandable/collapsible header.
    
    Features:
    - Expandable/collapsible header
    - Visual indicators (▼/▶)
    - Required field indicator (*)
    - Content frame for child widgets
    """
    
    def __init__(self, parent, title: str, required: bool = False, expanded: bool = True):
        """
        Initialize the collapsible section.
        
        Args:
            parent: Parent widget
            title: Section title
            required: Whether section contains required fields
            expanded: Initial expanded state
        """
        super().__init__(parent)
        
        self.title = title
        self.required = required
        self.expanded = expanded
        
        # Configure grid
        self.columnconfigure(0, weight=1)
        
        # Create header
        self._create_header()
        
        # Create content frame
        self._create_content_frame()
        
        # Set initial state
        if not expanded:
            self.collapse()
    
    def _create_header(self):
        """Create the header with title and toggle button."""
        # Header frame
        self.header_frame = ttk.Frame(self, relief="raised", borderwidth=1)
        self.header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        self.header_frame.columnconfigure(1, weight=1)
        
        # Toggle button with arrow
        self.arrow_label = ttk.Label(
            self.header_frame,
            text="▼" if self.expanded else "▶",
            font=("Arial", 10),
            width=2
        )
        self.arrow_label.grid(row=0, column=0, padx=(5, 0), pady=5)
        
        # Title label
        title_text = self.title
        if self.required:
            title_text += " *"
        
        self.title_label = ttk.Label(
            self.header_frame,
            text=title_text,
            font=("Arial", 11, "bold"),
            foreground="#333333"
        )
        self.title_label.grid(row=0, column=1, sticky="w", padx=(5, 10), pady=5)
        
        # Make header clickable
        self.header_frame.bind("<Button-1>", lambda e: self.toggle())
        self.arrow_label.bind("<Button-1>", lambda e: self.toggle())
        self.title_label.bind("<Button-1>", lambda e: self.toggle())
        
        # Change cursor on hover
        self.header_frame.bind("<Enter>", lambda e: self._on_hover(True))
        self.header_frame.bind("<Leave>", lambda e: self._on_hover(False))
    
    def _create_content_frame(self):
        """Create the content frame for child widgets."""
        self.content_frame = ttk.Frame(self, relief="flat", borderwidth=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 0), pady=(0, 10))
        self.content_frame.columnconfigure(0, weight=1)
    
    def _on_hover(self, entering: bool):
        """Handle mouse hover effect."""
        if entering:
            self.header_frame.configure(relief="raised")
        else:
            self.header_frame.configure(relief="raised")
    
    def toggle(self):
        """Toggle the section expanded/collapsed state."""
        if self.expanded:
            self.collapse()
        else:
            self.expand()
    
    def expand(self):
        """Expand the section."""
        self.expanded = True
        self.arrow_label.configure(text="▼")
        self.content_frame.grid()
    
    def collapse(self):
        """Collapse the section."""
        self.expanded = False
        self.arrow_label.configure(text="▶")
        self.content_frame.grid_remove()
    
    def get_content_frame(self) -> ttk.Frame:
        """Get the content frame where child widgets should be added."""
        return self.content_frame
