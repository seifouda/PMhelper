"""Table editor widget for forms."""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Callable, Optional

from pmhelper.gui.widgets.sortable_treeview import enhance_treeview


class TableEditor(ttk.Frame):
    """
    Editable table widget for form data.

    Features:
    - Editable rows using Treeview
    - Add/remove rows
    - Column headers from template
    - Support for text, number, and date columns
    - Data as list of dictionaries
    """

    def __init__(self,
                 parent,
                 columns: List[Dict[str,
                                    Any]],
                 callback: Optional[Callable] = None):
        """
        Initialize the table editor.

        Args:
            parent: Parent widget
            columns: List of column definitions from template
            callback: Callback function when data changes
        """
        super().__init__(parent)

        self.columns = columns
        self.callback = callback
        self.data: List[Dict[str, Any]] = []

        # Create widgets
        self._create_widgets()

    def _create_widgets(self):
        """Create the table and buttons."""
        # Toolbar frame
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", pady=(0, 5))

        # Add row button
        self.add_btn = ttk.Button(
            toolbar,
            text="➕ Add Row",
            command=self._add_row
        )
        self.add_btn.pack(side="left", padx=(0, 5))

        # Remove row button
        self.remove_btn = ttk.Button(
            toolbar,
            text="➖ Remove Row",
            command=self._remove_row,
            state="disabled"
        )
        self.remove_btn.pack(side="left")

        # Table frame with scrollbar
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True)

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical")
        vsb.pack(side="right", fill="y")

        hsb = ttk.Scrollbar(table_frame, orient="horizontal")
        hsb.pack(side="bottom", fill="x")

        # Create treeview
        column_ids = [col['id'] for col in self.columns]
        self.tree = ttk.Treeview(
            table_frame,
            columns=column_ids,
            show="headings",
            height=6,
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        self.tree.pack(fill="both", expand=True)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

        # Configure columns
        for col in self.columns:
            col_id = col['id']
            col_label = col['label']
            col_width = col.get('width', 150)

            self.tree.heading(col_id, text=col_label)
            self.tree.column(col_id, width=col_width, minwidth=50)

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)
        enhance_treeview(self.tree)

    def _on_select(self, event):
        """Handle row selection."""
        selection = self.tree.selection()
        if selection:
            self.remove_btn.configure(state="normal")
        else:
            self.remove_btn.configure(state="disabled")

    def _on_double_click(self, event):
        """Handle double-click to edit cell."""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        # Get selected item and column
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)

        if not item or not column:
            return

        # Get column index
        col_index = int(column.replace('#', '')) - 1
        if col_index < 0 or col_index >= len(self.columns):
            return

        col_id = self.columns[col_index]['id']

        # Get current value
        values = self.tree.item(item, 'values')
        current_value = values[col_index] if col_index < len(values) else ""

        # Create edit entry
        self._edit_cell(
            item,
            col_id,
            col_index,
            current_value,
            event.x,
            event.y)

    def _edit_cell(self, item, col_id, col_index, current_value, x, y):
        """Create entry widget to edit cell."""
        # Get cell coordinates
        bbox = self.tree.bbox(item, col_index)
        if not bbox:
            return

        # Create entry
        entry = ttk.Entry(self.tree)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()

        # Place entry over cell
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

        def save_edit(event=None):
            """Save the edited value."""
            new_value = entry.get()

            # Get row data
            row_index = self.tree.index(item)
            if row_index < len(self.data):
                self.data[row_index][col_id] = new_value

                # Update treeview
                values = list(self.tree.item(item, 'values'))
                values[col_index] = new_value
                self.tree.item(item, values=values)

                # Call callback
                if self.callback:
                    self.callback(self.data)

            entry.destroy()

        def cancel_edit(event=None):
            """Cancel editing."""
            entry.destroy()

        # Bind events
        entry.bind('<Return>', save_edit)
        entry.bind('<FocusOut>', save_edit)
        entry.bind('<Escape>', cancel_edit)

    def _add_row(self):
        """Add a new empty row."""
        # Create empty row data
        row_data = {col['id']: '' for col in self.columns}
        self.data.append(row_data)

        # Add to treeview
        values = [row_data[col['id']] for col in self.columns]
        self.tree.insert('', 'end', values=values)

        # Call callback
        if self.callback:
            self.callback(self.data)

    def _remove_row(self):
        """Remove selected row."""
        selection = self.tree.selection()
        if not selection:
            return

        for item in selection:
            # Get row index
            row_index = self.tree.index(item)

            # Remove from data
            if row_index < len(self.data):
                del self.data[row_index]

            # Remove from treeview
            self.tree.delete(item)

        # Call callback
        if self.callback:
            self.callback(self.data)

        # Update remove button state
        self.remove_btn.configure(state="disabled")

    def get_data(self) -> List[Dict[str, Any]]:
        """Get the table data."""
        return self.data

    def set_data(self, data: List[Dict[str, Any]]):
        """Set the table data."""
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        self.data = []

        # Add new data
        for row_data in data:
            self.data.append(row_data.copy())
            values = [row_data.get(col['id'], '') for col in self.columns]
            self.tree.insert('', 'end', values=values)

        # Call callback
        if self.callback:
            self.callback(self.data)
