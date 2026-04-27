"""Project Charter tab for PMHelper GUI."""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional
from datetime import datetime
import uuid
import threading

from ..models import Charter, CharterMetadata, CharterStatus
from ..models.template_model import Template
from ..services.template_service import TemplateService
from ..services.storage_service import StorageService
from ..services.pdf_generator import PDFGenerator
from ..dialogs import show_charter_help
from .charter_form import CharterForm


class CharterTab(ttk.Frame):
    """Tab for creating and managing project charters."""

    def __init__(self, parent, main_window):
        """Initialize the charter tab."""
        super().__init__(parent)

        self.main_window = main_window
        self.current_charter: Optional[Charter] = None
        self.current_template: Optional[Template] = None
        self.current_form: Optional[CharterForm] = None
        self.current_filepath: Optional[str] = None
        self.template_service = TemplateService()
        self.storage_service = StorageService()
        self.pdf_generator = PDFGenerator()
        self.auto_save_timer: Optional[threading.Timer] = None
        self.last_saved_time: Optional[datetime] = None

        self._setup_ui()
        self._setup_keyboard_shortcuts()

        # Start auto-save timer
        self._start_auto_save_timer()

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        # Ctrl+N: New charter
        self.bind_all('<Control-n>', lambda e: self._on_new_charter())

        # Ctrl+O: Open charter
        self.bind_all('<Control-o>', lambda e: self._on_open_charter())

        # Ctrl+S: Save charter
        self.bind_all('<Control-s>', lambda e: self._on_save_charter())

        # Ctrl+E: Export PDF
        self.bind_all('<Control-e>', lambda e: self._on_export_pdf())

        # F1: Help
        self.bind_all('<F1>', lambda e: self._on_help())

    def _setup_ui(self):
        """Setup the user interface."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Create toolbar
        self._create_toolbar()

        # Create content area
        self._create_content_area()

        # Create status bar
        self._create_status_bar()

    def _create_toolbar(self):
        """Create the toolbar with buttons."""
        toolbar_frame = ttk.Frame(self)
        toolbar_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # New button
        self.new_btn = ttk.Button(
            toolbar_frame,
            text="New Charter",
            command=self._on_new_charter,
            width=15
        )
        self.new_btn.pack(side="left", padx=5)
        self._create_tooltip(self.new_btn,
                             "Create a new project charter (Ctrl+N)")

        # Open button
        self.open_btn = ttk.Button(
            toolbar_frame,
            text="Open",
            command=self._on_open_charter,
            width=12
        )
        self.open_btn.pack(side="left", padx=5)
        self._create_tooltip(
            self.open_btn,
            "Open an existing charter (Ctrl+O)")

        # Save button
        self.save_btn = ttk.Button(
            toolbar_frame,
            text="Save",
            command=self._on_save_charter,
            width=12,
            state="disabled"
        )
        self.save_btn.pack(side="left", padx=5)
        self._create_tooltip(self.save_btn, "Save current charter (Ctrl+S)")

        # Export button
        self.export_btn = ttk.Button(
            toolbar_frame,
            text="Export PDF",
            command=self._on_export_pdf,
            width=15,
            state="disabled"
        )
        self.export_btn.pack(side="left", padx=5)
        self._create_tooltip(self.export_btn, "Export charter to PDF (Ctrl+E)")

        # Help button
        self.help_btn = ttk.Button(
            toolbar_frame,
            text="Help",
            command=self._on_help,
            width=12
        )
        self.help_btn.pack(side="right", padx=5)
        self._create_tooltip(self.help_btn,
                             "Show help and keyboard shortcuts (F1)")

    def _create_content_area(self):
        """Create the main content area."""
        # Content frame with border
        self.content_frame = ttk.Frame(self, relief="sunken", borderwidth=2)
        self.content_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(
                0,
                10))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Welcome message (shown when no charter is loaded)
        self.welcome_label = ttk.Label(
            self.content_frame,
            text="Welcome to Project Charter\n\nClick 'New Charter' to begin or 'Open' to load an existing charter.",
            font=(
                "Arial",
                14),
            foreground="gray")
        self.welcome_label.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=20,
            pady=20)

    def _create_status_bar(self):
        """Create the status bar."""
        status_frame = ttk.Frame(self)
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))

        # Status label
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10)

        # Progress info
        self.progress_label = ttk.Label(
            status_frame,
            text="",
            anchor="e"
        )
        self.progress_label.pack(side="right", padx=10)

    def _on_new_charter(self):
        """Handle new charter button click."""
        print("New Charter clicked - TODO: Show template selection dialog")
        self._update_status(
            "TODO: Implement template selection and charter creation")

        # For now, create a simple charter with default template
        self._create_new_charter("standard_charter_v1")

    def _create_new_charter(self, template_id: str):
        """Create a new charter with the given template."""
        # Clear template cache to ensure we get the latest version
        self.template_service.clear_cache()

        # Load template
        template = self.template_service.load_template(template_id)
        if not template:
            self._update_status(
                f"Error: Could not load template '{template_id}'")
            return

        # Create charter metadata
        charter_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        metadata = CharterMetadata(
            charter_id=charter_id,
            created_date=now,
            modified_date=now,
            status=CharterStatus.DRAFT.value,
            template_id=template.template_id,
            template_version=template.template_version
        )

        # Create charter
        self.current_charter = Charter(metadata=metadata)
        self.current_template = template
        self.current_filepath = None  # New charter has no file path yet
        self.last_saved_time = None  # New charter hasn't been saved yet

        # Update UI
        self._update_status(f"New charter created: {template.template_name}")
        self._enable_buttons()
        self._show_charter_form()

        # Start auto-save timer
        self._start_auto_save_timer()

    def _show_charter_form(self):
        """Show the charter form."""
        # Hide welcome message if visible
        try:
            self.welcome_label.grid_forget()
        except BaseException:
            pass

        # Clear any existing form
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create charter form
        self.current_form = CharterForm(
            self.content_frame,
            self.current_charter,
            self.current_template,
            on_change=self._on_form_change
        )
        self.current_form.pack(fill="both", expand=True)

        self._update_progress()
        self._update_status(f"Editing: {self.current_template.template_name}")

    def _on_form_change(self):
        """Handle form data change."""
        self._update_progress()
        self._update_status("Charter modified (unsaved)")
        self._update_last_saved_display()

    def _on_open_charter(self):
        """Handle open charter button click."""
        # Check for unsaved changes
        if self.current_charter and self._has_unsaved_changes():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save changes to current charter before opening another?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes, save
                if not self._save_charter_with_dialog():
                    return

        # Show file open dialog
        filepath = filedialog.askopenfilename(
            title="Open Charter",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.storage_service.base_dir
        )

        if not filepath:
            return

        # Load charter
        charter = self.storage_service.load_charter(filepath)
        if not charter:
            messagebox.showerror("Error", "Failed to load charter file.")
            return

        # Load template
        template = self.template_service.load_template(
            charter.metadata.template_id)
        if not template:
            messagebox.showerror(
                "Error",
                f"Template '{charter.metadata.template_id}' not found."
            )
            return

        # Set current charter and show form
        self.current_charter = charter
        self.current_template = template
        self.current_filepath = filepath
        self.last_saved_time = datetime.now()

        self._show_charter_form()
        self._enable_buttons()
        self._update_status(f"Loaded: {filepath}")
        self._update_last_saved_display()

        # Start auto-save timer
        self._start_auto_save_timer()

    def load_charter_from_file(self, filepath: str):
        """Load a charter from a file path (called from charter manager).

        Args:
            filepath: Path to the charter file to load
        """
        # Check for unsaved changes
        if self.current_charter and self._has_unsaved_changes():
            response = messagebox.askyesnocancel(
                "Unsaved Changes",
                "Save changes to current charter before opening another?"
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes, save
                if not self._save_charter_with_dialog():
                    return

        # Load charter
        charter = self.storage_service.load_charter(filepath)
        if not charter:
            messagebox.showerror("Error", "Failed to load charter file.")
            return

        # Load template
        template = self.template_service.load_template(
            charter.metadata.template_id)
        if not template:
            messagebox.showerror(
                "Error",
                f"Template '{charter.metadata.template_id}' not found."
            )
            return

        # Set current charter and show form
        self.current_charter = charter
        self.current_template = template
        self.current_filepath = filepath
        self.last_saved_time = datetime.now()

        self._show_charter_form()
        self._enable_buttons()
        self._update_status(f"Loaded: {filepath}")
        self._update_last_saved_display()

        # Start auto-save timer
        self._start_auto_save_timer()

    def _on_save_charter(self):
        """Handle save charter button click."""
        if not self.current_charter or not self.current_form:
            return

        # Validate form - show warning but allow saving
        if not self.current_form.validate():
            errors = self.current_form.get_validation_errors()

            # Build detailed error message
            error_list = "\n".join([f"• {error}" for error in errors.values()])

            response = messagebox.askyesno(
                "Validation Warnings",
                f"Found {len(errors)} validation issue(s):\n\n{error_list}\n\n"
                f"The missing fields have been highlighted in red.\n\n"
                f"Do you want to save anyway?",
                icon='warning'
            )
            if not response:
                return  # User chose not to save

        # Save charter
        if self.current_filepath:
            # Save to existing file
            if self.storage_service.save_charter(
                    self.current_charter, self.current_filepath):
                self.last_saved_time = datetime.now()
                self._update_status(f"Saved: {self.current_filepath}")
                self._update_last_saved_display()
                messagebox.showinfo("Success", "Charter saved successfully!")

                # Refresh Charter Manager to show updated data
                self._refresh_charter_manager()
            else:
                messagebox.showerror("Error", "Failed to save charter.")
        else:
            # Save As dialog
            self._save_charter_with_dialog()

    def _save_charter_with_dialog(self) -> bool:
        """Show Save As dialog and save charter. Returns True if saved."""
        if not self.current_charter:
            return False

        # Get suggested filename
        project_name = self.current_charter.get_field_value(
            'identification', 'project_name')
        if project_name:
            clean_name = "".join(
                c for c in project_name if c.isalnum() or c in (
                    ' ', '-', '_'))
            suggested_name = f"{clean_name.replace(' ', '_')}.json"
        else:
            suggested_name = "charter.json"

        # Show save dialog
        filepath = filedialog.asksaveasfilename(
            title="Save Charter",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=self.storage_service.base_dir,
            initialfile=suggested_name
        )

        if not filepath:
            return False

        # Save charter
        if self.storage_service.save_charter(self.current_charter, filepath):
            self.current_filepath = filepath
            self.last_saved_time = datetime.now()
            self._update_status(f"Saved: {filepath}")
            self._update_last_saved_display()
            messagebox.showinfo("Success", "Charter saved successfully!")

            # Refresh Charter Manager to show updated data
            self._refresh_charter_manager()
            return True
        else:
            messagebox.showerror("Error", "Failed to save charter.")
            return False

    def _on_export_pdf(self):
        """Handle export PDF button click."""
        if not self.current_charter or not self.current_form:
            return

        # Validate form first
        if not self.current_form.validate():
            errors = self.current_form.get_validation_errors()
            response = messagebox.askyesno(
                "Validation Errors", f"Charter has {
                    len(errors)} validation error(s).\n\nExport anyway?")
            if not response:
                return

        # Get suggested filename
        project_name = self.current_charter.get_field_value(
            'identification', 'project_name')
        if project_name:
            clean_name = "".join(
                c for c in project_name if c.isalnum() or c in (
                    ' ', '-', '_'))
            suggested_name = f"{clean_name.replace(' ', '_')}_Charter.pdf"
        else:
            suggested_name = "Project_Charter.pdf"

        # Show save dialog
        filepath = filedialog.asksaveasfilename(
            title="Export Charter to PDF",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialdir=self.storage_service.get_export_dir(),
            initialfile=suggested_name
        )

        if not filepath:
            return

        try:
            # Show progress
            self._update_status("Generating PDF...")
            self.update_idletasks()  # Force UI update

            # Generate PDF
            success = self.pdf_generator.generate_pdf(
                self.current_charter,
                self.current_template,
                filepath
            )

            if success:
                self._update_status(f"PDF exported: {filepath}")
                messagebox.showinfo(
                    "Export Successful",
                    f"Charter exported to PDF:\n\n{filepath}"
                )
            else:
                self._update_status("PDF export failed")
                messagebox.showerror(
                    "Export Failed",
                    "Failed to generate PDF. Check console for details."
                )
        except Exception as e:
            self._update_status(f"PDF export error: {str(e)}")
            messagebox.showerror(
                "Export Error",
                f"An error occurred while exporting:\n\n{str(e)}"
            )

    def _on_help(self):
        """Handle help button click."""
        show_charter_help(self.winfo_toplevel())

    def _update_status(self, message: str):
        """Update the status label."""
        self.status_label.configure(text=message)

    def _update_progress(self):
        """Update the progress label."""
        if self.current_charter and self.current_template:
            completion = self.current_charter.get_completion_percentage(
                self.current_template)
            self.progress_label.configure(
                text=f"Completion: {completion:.0f}%")
        else:
            self.progress_label.configure(text="")

    def _enable_buttons(self):
        """Enable buttons when a charter is loaded."""
        self.save_btn.configure(state="normal")
        self.export_btn.configure(state="normal")

    def _disable_buttons(self):
        """Disable buttons when no charter is loaded."""
        self.save_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")

    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes."""
        if not self.current_charter:
            return False

        # If never saved, has changes
        if not self.last_saved_time:
            return True

        # Check if modified after last save
        modified_time = datetime.fromisoformat(
            self.current_charter.metadata.modified_date)
        return modified_time > self.last_saved_time

    def _start_auto_save_timer(self):
        """Start the auto-save timer (5 minutes)."""
        if self.auto_save_timer:
            self.auto_save_timer.cancel()

        # Auto-save every 5 minutes (300 seconds)
        self.auto_save_timer = threading.Timer(300.0, self._auto_save)
        self.auto_save_timer.daemon = True
        self.auto_save_timer.start()

    def _auto_save(self):
        """Perform auto-save."""
        try:
            if self.current_charter and self.current_form:
                # Save to draft folder
                draft_path = self.storage_service.get_draft_filepath(
                    self.current_charter.metadata.charter_id
                )

                if self.storage_service.save_charter(
                        self.current_charter, draft_path):
                    self.last_saved_time = datetime.now()
                    # Update status in main thread
                    self.after(
                        0, lambda: self._update_status("Auto-saved to drafts"))
                    self.after(0, self._update_last_saved_display)
        except Exception as e:
            print(f"Auto-save error: {e}")
        finally:
            # Restart timer
            self._start_auto_save_timer()

    def _update_last_saved_display(self):
        """Update the last saved time display."""
        if self.last_saved_time:
            time_str = self.last_saved_time.strftime("%H:%M:%S")
            self.progress_label.configure(
                text=f"Completion: {
                    self._get_completion():.0f}% | Last saved: {time_str}")
        else:
            self.progress_label.configure(
                text=f"Completion: {self._get_completion():.0f}% | Not saved"
            )

    def _get_completion(self) -> float:
        """Get current completion percentage."""
        if self.current_charter and self.current_template:
            return self.current_charter.get_completion_percentage(
                self.current_template)
        return 0.0

    def _create_tooltip(self, widget, text: str):
        """Create a tooltip for a widget.

        Args:
            widget: Widget to attach tooltip to
            text: Tooltip text
        """
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief="solid",
                borderwidth=1,
                font=("Arial", 9)
            )
            label.pack()

            widget._tooltip = tooltip

        def on_leave(event):
            if hasattr(widget, '_tooltip'):
                widget._tooltip.destroy()
                del widget._tooltip

        widget.bind('<Enter>', on_enter)
        widget.bind('<Leave>', on_leave)

    def _refresh_charter_manager(self):
        """Refresh the Charter Manager tab to show updated charter data."""
        try:
            # Access the charter manager through main_window
            if hasattr(self.main_window, 'charter_manager'):
                self.main_window.charter_manager.refresh()
        except Exception as e:
            # Silently fail if charter manager is not available
            print(f"Warning: Could not refresh Charter Manager: {e}")

    def destroy(self):
        """Clean up when tab is destroyed."""
        # Cancel auto-save timer
        if self.auto_save_timer:
            self.auto_save_timer.cancel()
        super().destroy()
