"""Validation utilities for form fields."""

import re
from datetime import datetime
from typing import Any, Optional, Tuple


class FieldValidator:
    """Validator for form fields."""

    @staticmethod
    def validate_required(
            value: Any, field_label: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a required field is not empty.

        Args:
            value: Field value to validate
            field_label: Label of the field for error message

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"{field_label} is required"

        if isinstance(value, list) and len(value) == 0:
            return False, f"{field_label} requires at least one entry"

        return True, None

    @staticmethod
    def validate_max_length(value: str, max_length: int,
                            field_label: str) -> Tuple[bool, Optional[str]]:
        """
        Validate maximum length constraint.

        Args:
            value: String value to validate
            max_length: Maximum allowed length
            field_label: Label of the field for error message

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value and len(value) > max_length:
            return False, f"{field_label} cannot exceed {max_length} characters (currently {
                len(value)})"
        return True, None

    @staticmethod
    def validate_date(value: str,
                      field_label: str) -> Tuple[bool,
                                                 Optional[str]]:
        """
        Validate date format (YYYY-MM-DD).

        Args:
            value: Date string to validate
            field_label: Label of the field for error message

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Empty is okay for non-required

        try:
            datetime.strptime(value.strip(), "%Y-%m-%d")
            return True, None
        except ValueError:
            return False, f"{field_label} must be in format YYYY-MM-DD"

    @staticmethod
    def validate_number(value: str,
                        field_label: str,
                        min_value: Optional[float] = None,
                        max_value: Optional[float] = None) -> Tuple[bool,
                                                                    Optional[str]]:
        """
        Validate numeric value.

        Args:
            value: String value to validate
            field_label: Label of the field for error message
            min_value: Minimum allowed value (optional)
            max_value: Maximum allowed value (optional)

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Empty is okay for non-required

        try:
            num = float(value.strip().replace(',', ''))

            if min_value is not None and num < min_value:
                return False, f"{field_label} must be at least {min_value}"

            if max_value is not None and num > max_value:
                return False, f"{field_label} must not exceed {max_value}"

            return True, None
        except ValueError:
            return False, f"{field_label} must be a valid number"

    @staticmethod
    def validate_currency(
            value: str, field_label: str) -> Tuple[bool, Optional[str]]:
        """
        Validate currency value.

        Args:
            value: Currency string to validate
            field_label: Label of the field for error message

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Empty is okay for non-required

        # Remove currency symbols and commas
        cleaned = value.strip().replace(
            '$',
            '').replace(
            ',',
            '').replace(
            ' ',
            '')

        try:
            num = float(cleaned)
            if num < 0:
                return False, f"{field_label} cannot be negative"
            return True, None
        except ValueError:
            return False, f"{field_label} must be a valid currency amount"

    @staticmethod
    def validate_email(
            value: str, field_label: str) -> Tuple[bool, Optional[str]]:
        """
        Validate email format.

        Args:
            value: Email string to validate
            field_label: Label of the field for error message

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not value or not value.strip():
            return True, None  # Empty is okay for non-required

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value.strip()):
            return False, f"{field_label} must be a valid email address"

        return True, None


def show_validation_error(widget, error_message: str):
    """
    Show validation error on a widget by adding a red border.

    Args:
        widget: Tkinter widget (usually a Frame wrapper) to highlight
        error_message: Error message to display
    """

    # Store error message
    widget._validation_error = error_message

    try:
        # Set red border on the frame/widget
        widget.configure(
            highlightbackground='red',
            highlightcolor='red',
            highlightthickness=2,
            bg='#ffe6e6'  # Light red background
        )
    except Exception as e:
        print(f"Error highlighting widget: {e}")


def clear_validation_error(widget):
    """
    Clear validation error from a widget.

    Args:
        widget: Tkinter widget to clear
    """
    # Clear error message
    if hasattr(widget, '_validation_error'):
        delattr(widget, '_validation_error')

    try:
        # Try to get current config keys to see what's supported
        config_keys = widget.keys() if hasattr(widget, 'keys') else []

        # Reset to default styling based on what the widget supports
        if 'highlightthickness' in config_keys:
            widget.configure(highlightthickness=0)
        if 'bg' in config_keys:
            widget.configure(bg='SystemButtonFace')
    except Exception as e:
        # Silently ignore - widget may have been destroyed
        pass
