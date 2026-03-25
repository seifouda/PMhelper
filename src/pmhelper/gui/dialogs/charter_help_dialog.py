"""Help dialog for Project Charter feature."""

import tkinter as tk
from tkinter import ttk


class CharterHelpDialog:
    """Help dialog showing charter feature documentation."""
    
    def __init__(self, parent):
        """Initialize help dialog.
        
        Args:
            parent: Parent window
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Project Charter Help")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_ui()
        
        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _create_ui(self):
        """Create the help UI."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Overview tab
        overview_frame = ttk.Frame(notebook)
        notebook.add(overview_frame, text="Overview")
        self._create_overview_tab(overview_frame)
        
        # Keyboard shortcuts tab
        shortcuts_frame = ttk.Frame(notebook)
        notebook.add(shortcuts_frame, text="Keyboard Shortcuts")
        self._create_shortcuts_tab(shortcuts_frame)
        
        # Fields tab
        fields_frame = ttk.Frame(notebook)
        notebook.add(fields_frame, text="Field Types")
        self._create_fields_tab(fields_frame)
        
        # Close button
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(side="bottom", pady=(0, 10))
        
        close_btn = ttk.Button(
            btn_frame,
            text="Close",
            command=self.dialog.destroy,
            width=15
        )
        close_btn.pack()
    
    def _create_overview_tab(self, parent):
        """Create overview content."""
        # Create scrollable text
        text = tk.Text(
            parent,
            wrap="word",
            padx=10,
            pady=10,
            font=("Arial", 10)
        )
        text.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)
        
        # Add content
        content = """PROJECT CHARTER FEATURE

The Project Charter feature helps you create professional project documentation following PMI standards.

GETTING STARTED:

1. New Charter
   Click "New Charter" or press Ctrl+N to create a new project charter from the standard template.

2. Fill Out the Form
   Complete all sections of the charter. Required fields are marked with an asterisk (*).
   The completion percentage is shown at the bottom.

3. Save Your Work
   Click "Save" or press Ctrl+S to save your charter. Charters are auto-saved every 5 minutes to prevent data loss.

4. Export to PDF
   Click "Export PDF" or press Ctrl+E to generate a professional PDF document.

CHARTER SECTIONS:

1. Project Identification
   Basic project information including name, sponsor, and dates.

2. Objectives & Business Case
   Define business objectives, success criteria, and expected benefits.

3. Scope
   Document what's included and excluded from the project.

4. Budget
   Define financial resources and cost breakdown.

5. Schedule
   Set project timeline with start and end dates.

6. Project Team
   List team members and their roles.

7. Stakeholders
   Identify key stakeholders and their interests.

8. Risks & Constraints
   Document potential risks and project constraints.

9. Approval & Sign-off
   Record approvals and authorization details.

CHARTER MANAGER:

Use the "Charter Manager" tab to:
- View all saved charters
- Search and sort charters
- Open, duplicate, or delete charters
- See completion status at a glance

AUTO-SAVE:

Your work is automatically saved to the drafts folder every 5 minutes. You can always manually save with Ctrl+S.

VALIDATION:

The system validates your input to ensure data quality:
- Required fields must be filled
- Dates must be in valid format
- Currency values must be numbers
- Email addresses must be valid

TIPS:

• Use Tab to navigate between fields
• Expand/collapse sections to focus on specific areas
• The progress indicator shows how much of the charter is complete
• Save frequently to avoid data loss
• Export to PDF only when the charter is complete
"""
        
        text.insert("1.0", content)
        text.configure(state="disabled")
    
    def _create_shortcuts_tab(self, parent):
        """Create keyboard shortcuts content."""
        # Create frame for shortcuts
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ttk.Label(
            frame,
            text="Keyboard Shortcuts",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=(0, 20))
        
        # Shortcuts list
        shortcuts = [
            ("Ctrl+N", "Create new charter"),
            ("Ctrl+O", "Open existing charter"),
            ("Ctrl+S", "Save current charter"),
            ("Ctrl+E", "Export charter to PDF"),
            ("F1", "Show this help dialog"),
            ("Tab", "Navigate to next field"),
            ("Shift+Tab", "Navigate to previous field"),
            ("Enter", "Expand/collapse section (when focused)"),
        ]
        
        # Create table
        for shortcut, description in shortcuts:
            row_frame = ttk.Frame(frame)
            row_frame.pack(fill="x", pady=5)
            
            shortcut_label = ttk.Label(
                row_frame,
                text=shortcut,
                font=("Courier New", 10, "bold"),
                width=15
            )
            shortcut_label.pack(side="left")
            
            desc_label = ttk.Label(
                row_frame,
                text=description,
                font=("Arial", 10)
            )
            desc_label.pack(side="left", padx=10)
    
    def _create_fields_tab(self, parent):
        """Create field types content."""
        # Create scrollable text
        text = tk.Text(
            parent,
            wrap="word",
            padx=10,
            pady=10,
            font=("Arial", 10)
        )
        text.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(parent, command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)
        
        # Add content
        content = """FIELD TYPES

The charter form supports various field types to capture different kinds of information:

TEXT FIELD
Single-line text entry for short information.
Examples: Project name, sponsor name, project code

TEXTAREA
Multi-line text entry for longer descriptions.
Examples: Project description, business case, objectives
Use this for detailed information that spans multiple lines.

DATE FIELD
Date picker for selecting dates.
Click the calendar icon to choose a date visually.
Format: YYYY-MM-DD
Examples: Start date, end date, approval date

CURRENCY FIELD
Numeric input for monetary values.
Automatically formats with $ symbol in exports.
Examples: Budget amount, cost estimates
Enter numbers only (decimals allowed).

NUMBER FIELD
Numeric input for quantities or percentages.
Examples: Team size, success percentage
Enter numbers only (decimals allowed).

DROPDOWN
Selection from predefined options.
Click to see available choices.
Examples: Priority level, project type, status

TABLE FIELD
Editable table for structured data with multiple entries.
Features:
- Add Row: Click "+" to add new rows
- Remove Row: Select row and click "-"
- Edit Cell: Double-click cell to edit
- Column Headers: Defined by template

Examples:
- Stakeholders: Name, Role, Contact
- Team Members: Name, Role, Allocation
- Risks: Description, Impact, Mitigation
- Budget Breakdown: Category, Amount, Notes

VALIDATION

Each field type has specific validation rules:
- Required fields must be filled before saving
- Dates must be valid calendar dates
- Currency and number fields must contain numeric values
- Email fields must be valid email addresses
- Maximum length restrictions apply to text fields

HELP TEXT

Hover over field labels to see help text and requirements for specific fields.
"""
        
        text.insert("1.0", content)
        text.configure(state="disabled")


def show_charter_help(parent):
    """Show the charter help dialog.
    
    Args:
        parent: Parent window
    """
    CharterHelpDialog(parent)
