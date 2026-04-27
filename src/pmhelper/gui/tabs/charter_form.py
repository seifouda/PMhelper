"""Dynamic form builder for charter creation."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Dict, Any, Callable, Optional

from ..models import Charter
from ..models.template_model import Template, TemplateSection, TemplateField
from ..widgets import CollapsibleSection, DatePicker, TableEditor, ListEditor
from ..utils import FieldValidator, show_validation_error, clear_validation_error


class CharterForm(ttk.Frame):
    """
    Dynamic form builder that generates form from template.

    Features:
    - Generate form from template JSON
    - Create sections with fields
    - Support multiple field types
    - Data binding (widget ↔ model)
    - Change tracking and callbacks
    """

    # Currency code to symbol mapping
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CAD': 'C$',
        'AUD': 'A$',
        'CNY': '¥',
        'INR': '₹',
        'CHF': 'CHF',
        'Other': ''
    }

    def __init__(
            self,
            parent,
            charter: Charter,
            template: Template,
            on_change: Optional[Callable] = None):
        """
        Initialize the charter form.

        Args:
            parent: Parent widget
            charter: Charter data model
            template: Template definition
            on_change: Callback when form data changes
        """
        super().__init__(parent)

        self.charter = charter
        self.template = template
        self.on_change = on_change

        # Field widgets registry
        self.field_widgets: Dict[str, Dict[str, Any]] = {}

        # Validation errors
        self.validation_errors: Dict[str, str] = {}

        # Currency fields that need to be updated when currency changes
        self.currency_fields: Dict[str, ttk.Entry] = {}

        # Create scrollable form
        self._create_scrollable_form()

        # Generate form from template
        self._generate_form()

        # Load existing data
        self._load_data()

    def _create_scrollable_form(self):
        """Create scrollable canvas for form."""
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Bind mousewheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Configure grid
        self.scrollable_frame.columnconfigure(0, weight=1)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _generate_form(self):
        """Generate form from template."""
        for section in self.template.sections:
            self._create_section(section)

    def _create_section(self, section: TemplateSection):
        """Create a collapsible section with fields."""
        # Create collapsible section
        section_widget = CollapsibleSection(
            self.scrollable_frame,
            title=section.section_title,
            required=section.required,
            expanded=True
        )
        section_widget.pack(fill="x", padx=10, pady=5)

        # Get content frame
        content = section_widget.get_content_frame()
        content.columnconfigure(1, weight=1)

        # Create fields
        row = 0
        for field_def in section.fields:
            self._create_field(
                content,
                section.section_id,
                field_def,
                row,
                section_widget)
            row += 1

    def _create_field(
            self,
            parent: ttk.Frame,
            section_id: str,
            field_def: TemplateField,
            row: int,
            section_widget=None):
        """Create a single form field.

        Args:
            parent: Parent frame
            section_id: Section identifier
            field_def: Field definition
            row: Row number in grid
            section_widget: The CollapsibleSection widget containing this field
        """
        # Label
        label_text = field_def.field_label
        if field_def.required:
            label_text += " *"

        label = ttk.Label(parent, text=label_text, anchor="w")
        label.grid(row=row, column=0, sticky="nw", padx=(5, 10), pady=8)

        # Create a wrapper frame for the widget (for error highlighting)
        wrapper_frame = tk.Frame(
            parent,
            bg='SystemButtonFace',
            highlightthickness=0)
        wrapper_frame.grid(
            row=row,
            column=1,
            sticky="ew",
            padx=(
                0,
                10),
            pady=5)
        wrapper_frame.columnconfigure(0, weight=1)

        # Field widget based on type
        if field_def.field_type == "text":
            widget = self._create_text_field(wrapper_frame, field_def)
        elif field_def.field_type == "textarea":
            widget = self._create_textarea_field(wrapper_frame, field_def)
        elif field_def.field_type == "list":
            widget = self._create_list_field(wrapper_frame, field_def)
        elif field_def.field_type == "date":
            widget = self._create_date_field(wrapper_frame, field_def)
        elif field_def.field_type == "currency":
            widget = self._create_currency_field(wrapper_frame, field_def)
        elif field_def.field_type == "number":
            widget = self._create_number_field(wrapper_frame, field_def)
        elif field_def.field_type == "dropdown":
            widget = self._create_dropdown_field(wrapper_frame, field_def)
        elif field_def.field_type == "table":
            widget = self._create_table_field(wrapper_frame, field_def)
        else:
            widget = self._create_text_field(
                wrapper_frame, field_def)  # Default to text

        widget.pack(fill="both", expand=True)

        # Help text
        if field_def.help_text:
            help_label = ttk.Label(parent, text=field_def.help_text,
                                   foreground="gray", font=("Arial", 9))
            help_label.grid(
                row=row, column=2, sticky="w", padx=(
                    5, 10), pady=5)

        # Store widget reference AND wrapper frame for error highlighting
        self.field_widgets[f"{section_id}.{field_def.field_id}"] = {
            'widget': widget,
            'wrapper': wrapper_frame,
            'field_def': field_def,
            'section_id': section_id,
            'section_widget': section_widget
        }

    def _create_text_field(
            self,
            parent,
            field_def: TemplateField) -> ttk.Entry:
        """Create a text entry field."""
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, width=40)

        # Store the field_def in the widget for later reference
        entry._field_def = field_def

        if field_def.placeholder:
            entry.insert(0, field_def.placeholder)
            entry.config(foreground='gray')

            def on_focus_in(e):
                if entry.get() == field_def.placeholder:
                    entry.delete(0, tk.END)
                    entry.config(foreground='black')

            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, field_def.placeholder)
                    entry.config(foreground='gray')
                # Trigger change when losing focus
                self._on_field_change(entry, field_def)

            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)

        # Bind change event with multiple methods to ensure it fires
        var.trace('w', lambda *args: self._on_field_change(entry, field_def))
        entry.bind(
            '<KeyRelease>',
            lambda e: self._on_field_change(
                entry,
                field_def))
        entry.bind(
            '<FocusOut>',
            lambda e: self._on_field_change(
                entry,
                field_def))

        return entry

    def _create_textarea_field(
            self,
            parent,
            field_def: TemplateField) -> scrolledtext.ScrolledText:
        """Create a textarea field."""
        rows = field_def.rows or 4
        textarea = scrolledtext.ScrolledText(
            parent, height=rows, width=50, wrap=tk.WORD)

        # Track if we're programmatically setting text to avoid triggering
        # change events
        textarea._loading = False

        if field_def.placeholder:
            textarea._loading = True
            textarea.insert('1.0', field_def.placeholder)
            textarea.config(foreground='gray')
            textarea._loading = False

            def on_focus_in(e):
                if textarea.get('1.0',
                                tk.END).strip() == field_def.placeholder:
                    textarea._loading = True
                    textarea.delete('1.0', tk.END)
                    textarea.config(foreground='black')
                    textarea._loading = False

            def on_focus_out(e):
                if not textarea.get('1.0', tk.END).strip():
                    textarea._loading = True
                    textarea.insert('1.0', field_def.placeholder)
                    textarea.config(foreground='gray')
                    textarea._loading = False
                else:
                    # Trigger change when losing focus with actual content
                    self._on_field_change(textarea, field_def)

            textarea.bind('<FocusIn>', on_focus_in)
            textarea.bind('<FocusOut>', on_focus_out)

        # Bind change events
        def on_text_change(event):
            # Only trigger if not loading and modified flag is set
            if not getattr(
                textarea,
                '_loading',
                    False) and textarea.edit_modified():
                self._on_field_change(textarea, field_def)
                textarea.edit_modified(False)  # Reset the modified flag

        textarea.bind('<<Modified>>', on_text_change)
        textarea.bind(
            '<FocusOut>',
            lambda e: self._on_field_change(
                textarea,
                field_def))

        return textarea

    def _create_date_field(
            self,
            parent,
            field_def: TemplateField) -> DatePicker:
        """Create a date picker field."""
        date_picker = DatePicker(
            parent, callback=lambda v: self._on_field_change(
                date_picker, field_def))
        return date_picker

    def _create_currency_field(
            self,
            parent,
            field_def: TemplateField) -> ttk.Entry:
        """Create a currency field."""
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, width=20)

        # Store reference to this currency field
        # We'll use the section_id to link it with the currency dropdown
        entry._field_def = field_def

        # Format on focus out
        def on_focus_out(e):
            # Get the current currency symbol
            currency_symbol = self._get_currency_symbol()

            # Remove any existing currency symbols (longest first to handle
            # multi-char symbols)
            value = var.get().strip()
            sorted_symbols = sorted(
                self.CURRENCY_SYMBOLS.values(), key=len, reverse=True)
            for symbol in sorted_symbols:
                if symbol:
                    value = value.replace(symbol, '')
            value = value.replace(',', '').replace(' ', '').strip()

            if value:
                try:
                    num = float(value)
                    var.set(f"{currency_symbol}{num:,.2f}")
                except ValueError:
                    pass

        entry.bind('<FocusOut>', on_focus_out)
        var.trace('w', lambda *args: self._on_field_change(entry, field_def))

        # Store reference for later updates
        self.currency_fields[field_def.field_id] = entry

        return entry

    def _get_currency_symbol(self) -> str:
        """Get the current currency symbol based on the currency dropdown selection."""
        # Try to get the currency value from the charter data
        currency_code = self.charter.get_field_value('budget', 'currency')
        if currency_code and currency_code in self.CURRENCY_SYMBOLS:
            return self.CURRENCY_SYMBOLS[currency_code]
        return '$'  # Default to USD

    def _update_currency_fields(self):
        """Update all currency fields with the new currency symbol."""
        for field_id, entry in self.currency_fields.items():
            current_value = entry.get().strip()
            if not current_value:
                continue

            # Remove old currency symbols - sort by length (longest first) to
            # handle multi-char symbols
            value = current_value
            sorted_symbols = sorted(
                self.CURRENCY_SYMBOLS.values(), key=len, reverse=True)
            for symbol in sorted_symbols:
                if symbol:
                    value = value.replace(symbol, '')
            # Also remove common separators
            value = value.replace(',', '').replace(' ', '').strip()

            if value:
                try:
                    num = float(value)
                    currency_symbol = self._get_currency_symbol()
                    entry.delete(0, tk.END)
                    entry.insert(0, f"{currency_symbol}{num:,.2f}")
                except ValueError:
                    pass

    def _create_number_field(
            self,
            parent,
            field_def: TemplateField) -> ttk.Entry:
        """Create a number field."""
        var = tk.StringVar()
        entry = ttk.Entry(parent, textvariable=var, width=20)

        var.trace('w', lambda *args: self._on_field_change(entry, field_def))

        return entry

    def _create_dropdown_field(
            self,
            parent,
            field_def: TemplateField) -> ttk.Combobox:
        """Create a dropdown field."""
        var = tk.StringVar()
        options = field_def.options or []

        combo = ttk.Combobox(parent, textvariable=var, values=options,
                             state="readonly", width=37)

        if field_def.default and field_def.default in options:
            combo.set(field_def.default)

        # Special handling for currency dropdown
        def on_dropdown_change(e):
            self._on_field_change(combo, field_def)
            # If this is the currency dropdown, update all currency fields
            if field_def.field_id == 'currency':
                self._update_currency_fields()

        combo.bind('<<ComboboxSelected>>', on_dropdown_change)

        return combo

    def _create_list_field(
            self,
            parent,
            field_def: TemplateField) -> ListEditor:
        """Create a list editor field."""
        placeholder = field_def.placeholder or "Add item..."
        list_editor = ListEditor(
            parent,
            placeholder=placeholder,
            on_change=lambda: self._on_field_change(list_editor, field_def)
        )
        return list_editor

    def _create_table_field(
            self,
            parent,
            field_def: TemplateField) -> TableEditor:
        """Create a table editor field."""
        columns = field_def.columns or []
        table = TableEditor(
            parent,
            columns,
            callback=lambda data: self._on_field_change(
                table,
                field_def))
        return table

    def _on_field_change(self, widget, field_def: TemplateField):
        """Handle field value change."""
        # Get the field key
        field_key = None
        wrapper = None
        for key, info in self.field_widgets.items():
            if info['widget'] == widget:
                field_key = key
                section_id = info['section_id']
                wrapper = info.get('wrapper')
                break

        if not field_key:
            return

        # Get value from widget
        value = self._get_widget_value(widget, field_def.field_type)

        # Update charter data
        self.charter.set_field_value(section_id, field_def.field_id, value)

        # Clear validation error from wrapper frame
        if wrapper:
            clear_validation_error(wrapper)
        else:
            clear_validation_error(widget)
        if field_key in self.validation_errors:
            del self.validation_errors[field_key]

        # Call change callback
        if self.on_change:
            self.on_change()

    def _get_widget_value(self, widget, field_type: str) -> Any:
        """Get value from widget based on field type."""
        if field_type == "textarea":
            value = widget.get('1.0', tk.END).strip()
            # Check if it's a placeholder (gray text)
            if hasattr(widget, 'cget') and widget.cget('foreground') == 'gray':
                return None
            return value if value else None
        elif field_type == "list":
            items = widget.get_data()
            return items if items else None
        elif field_type == "date":
            return widget.get_date() or None
        elif field_type == "table":
            return widget.get_data()
        elif field_type == "dropdown":
            value = widget.get()
            return value if value else None
        elif field_type == "currency":
            # Strip all currency symbols before saving (longest first to handle
            # multi-char symbols)
            value = widget.get().strip()
            sorted_symbols = sorted(
                self.CURRENCY_SYMBOLS.values(), key=len, reverse=True)
            for symbol in sorted_symbols:
                if symbol:
                    value = value.replace(symbol, '')
            value = value.replace(',', '').replace(' ', '').strip()
            return value if value else None
        else:  # text, number
            value = widget.get().strip()
            # Check if it's a placeholder (gray text)
            if hasattr(widget, 'cget'):
                try:
                    if widget.cget('foreground') == 'gray':
                        return None
                except BaseException:
                    pass
            return value if value else None

    def _load_data(self):
        """Load existing charter data into form."""
        loaded_count = 0
        for field_key, info in self.field_widgets.items():
            widget = info['widget']
            field_def = info['field_def']
            section_id = info['section_id']

            # Get value from charter
            value = self.charter.get_field_value(
                section_id, field_def.field_id)

            if value:
                self._set_widget_value(widget, field_def.field_type, value)
                loaded_count += 1

    def _set_widget_value(self, widget, field_type: str, value: Any):
        """Set widget value based on field type."""
        try:
            if field_type == "textarea":
                widget._loading = True  # Prevent change event during load
                widget.delete('1.0', tk.END)
                widget.insert('1.0', value)
                widget.config(foreground='black')  # Clear placeholder styling
                widget.edit_modified(False)  # Reset modified flag
                widget._loading = False
            elif field_type == "list":
                if isinstance(value, list):
                    widget.set_data(value)
                elif isinstance(value, str):
                    # Handle old data format - convert string to list
                    items = [item.strip()
                             for item in value.split('\n') if item.strip()]
                    widget.set_data(items)
            elif field_type == "date":
                widget.set_date(value)
            elif field_type == "table":
                widget.set_data(value)
            elif field_type == "dropdown":
                widget.set(value)
            elif field_type == "currency":
                # Format currency with appropriate symbol
                try:
                    num = float(str(value).replace(',', ''))
                    currency_symbol = self._get_currency_symbol()
                    widget.delete(0, tk.END)
                    widget.insert(0, f"{currency_symbol}{num:,.2f}")
                except ValueError:
                    widget.delete(0, tk.END)
                    widget.insert(0, value)
                widget.config(foreground='black')
            else:  # text, number
                widget.delete(0, tk.END)
                widget.insert(0, value)
                widget.config(foreground='black')  # Clear placeholder styling
        except Exception as e:
            print(f"Error setting widget value: {e}")
            print(f"Error setting widget value: {e}")

    def validate(self) -> bool:
        """Validate all form fields and highlight errors."""
        # Clear previous validation errors
        self.validation_errors.clear()
        self._clear_all_validation_highlights()

        is_valid = True
        first_error_widget = None
        first_error_section = None

        for field_key, info in self.field_widgets.items():
            widget = info['widget']
            wrapper = info.get('wrapper')  # Get the wrapper frame
            field_def = info['field_def']
            section_id = info['section_id']
            section_widget = info.get('section_widget')

            # Get current value
            value = self.charter.get_field_value(
                section_id, field_def.field_id)

            # Validate required
            if field_def.required:
                valid, error = FieldValidator.validate_required(
                    value, field_def.field_label)
                if not valid:
                    self.validation_errors[field_key] = error
                    # Highlight the wrapper frame instead of the widget
                    if wrapper:
                        show_validation_error(wrapper, error)
                    else:
                        show_validation_error(widget, error)
                    is_valid = False
                    if first_error_widget is None:
                        first_error_widget = widget
                        first_error_section = section_widget
                    continue

            # Type-specific validation
            if value:
                if field_def.field_type == "date":
                    valid, error = FieldValidator.validate_date(
                        value, field_def.field_label)
                    if not valid:
                        self.validation_errors[field_key] = error
                        if wrapper:
                            show_validation_error(wrapper, error)
                        else:
                            show_validation_error(widget, error)
                        is_valid = False
                        if first_error_widget is None:
                            first_error_widget = widget
                            first_error_section = section_widget
                elif field_def.field_type == "currency":
                    valid, error = FieldValidator.validate_currency(
                        value, field_def.field_label)
                    if not valid:
                        self.validation_errors[field_key] = error
                        if wrapper:
                            show_validation_error(wrapper, error)
                        else:
                            show_validation_error(widget, error)
                        is_valid = False
                        if first_error_widget is None:
                            first_error_widget = widget
                            first_error_section = section_widget
                elif field_def.field_type == "number":
                    valid, error = FieldValidator.validate_number(
                        value, field_def.field_label)
                    if not valid:
                        self.validation_errors[field_key] = error
                        if wrapper:
                            show_validation_error(wrapper, error)
                        else:
                            show_validation_error(widget, error)
                        is_valid = False
                        if first_error_widget is None:
                            first_error_widget = widget
                            first_error_section = section_widget

                # Max length validation
                if field_def.max_length and field_def.field_type in [
                        "text", "textarea"]:
                    valid, error = FieldValidator.validate_max_length(
                        value, field_def.max_length, field_def.field_label)
                    if not valid:
                        self.validation_errors[field_key] = error
                        if wrapper:
                            show_validation_error(wrapper, error)
                        else:
                            show_validation_error(widget, error)
                        is_valid = False
                        if first_error_widget is None:
                            first_error_widget = widget
                            first_error_section = section_widget

        # If there are errors, expand the section with first error and scroll
        # to it
        if not is_valid and first_error_widget and first_error_section:
            self._scroll_to_error(first_error_widget, first_error_section)

        return is_valid

    def get_validation_errors(self) -> Dict[str, str]:
        """Get all validation errors."""
        return self.validation_errors.copy()

    def _clear_all_validation_highlights(self):
        """Clear validation error highlights from all fields."""
        for field_key, info in self.field_widgets.items():
            wrapper = info.get('wrapper')
            widget = info['widget']
            # Clear the wrapper frame highlight
            if wrapper:
                clear_validation_error(wrapper)
            else:
                clear_validation_error(widget)

    def _scroll_to_error(self, error_widget, section_widget):
        """Scroll to the first error field and expand its section.

        Args:
            error_widget: The widget with the validation error
            section_widget: The CollapsibleSection containing the widget
        """
        # Expand the section if it's collapsed
        if section_widget and hasattr(section_widget, 'expand'):
            section_widget.expand()

        # Wait for section to expand, then scroll
        self.after(100, lambda: self._do_scroll(error_widget))

    def _do_scroll(self, widget):
        """Perform the actual scroll operation.

        Args:
            widget: Widget to scroll to
        """
        try:
            # Update idle tasks to ensure layout is complete
            self.canvas.update_idletasks()

            # Get widget position relative to canvas
            widget.update_idletasks()

            # Find the widget's y position in the scrollable frame
            y_pos = widget.winfo_y()

            # Get the scrollable frame and canvas heights
            frame_height = self.scrollable_frame.winfo_height()
            canvas_height = self.canvas.winfo_height()

            if frame_height > canvas_height:
                # Calculate scroll position (center the error widget)
                scroll_pos = (y_pos - canvas_height // 2) / frame_height
                # Clamp between 0 and 1
                scroll_pos = max(0.0, min(1.0, scroll_pos))

                # Scroll to position
                self.canvas.yview_moveto(scroll_pos)

            # Flash the widget to draw attention
            self._flash_widget(widget)
        except Exception as e:
            print(f"Error scrolling to widget: {e}")

    def _flash_widget(self, widget):
        """Flash the widget background to draw attention.

        Args:
            widget: Widget to flash
        """
        try:
            # Get current background color
            current_bg = widget.cget('background')

            # Flash sequence: normal -> red -> normal
            def flash_step(count):
                if count > 0:
                    # Red flash
                    if isinstance(widget, (ttk.Entry, ttk.Combobox)):
                        # For ttk widgets, we can't easily change background
                        # Just ensure the red border is visible
                        pass
                    else:
                        widget.configure(
                            background='#ffcccc' if count %
                            2 == 1 else current_bg)
                    self.after(200, lambda: flash_step(count - 1))

            flash_step(3)  # Flash 3 times
        except Exception as e:
            print(f"Error flashing widget: {e}")
