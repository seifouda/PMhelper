"""Date picker widget for forms."""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import calendar


class DatePicker(ttk.Frame):
    """
    A date picker widget with calendar popup.
    
    Features:
    - Text entry with date validation
    - Calendar popup for date selection
    - Format: YYYY-MM-DD
    - Clear button
    """
    
    def __init__(self, parent, callback=None):
        """
        Initialize the date picker.
        
        Args:
            parent: Parent widget
            callback: Callback function when date changes
        """
        super().__init__(parent)
        
        self.callback = callback
        self.calendar_window = None
        
        # Create entry and button
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the entry and calendar button."""
        # Date entry
        self.entry_var = tk.StringVar()
        self.entry_var.trace('w', self._on_entry_change)
        
        self.entry = ttk.Entry(self, textvariable=self.entry_var, width=12)
        self.entry.pack(side="left", padx=(0, 5))
        
        # Calendar button
        self.calendar_btn = ttk.Button(
            self,
            text="📅",
            width=3,
            command=self._show_calendar
        )
        self.calendar_btn.pack(side="left", padx=(0, 5))
        
        # Clear button
        self.clear_btn = ttk.Button(
            self,
            text="✕",
            width=3,
            command=self._clear_date
        )
        self.clear_btn.pack(side="left")
    
    def _on_entry_change(self, *args):
        """Handle entry value change."""
        if self.callback:
            self.callback(self.get_date())
    
    def _show_calendar(self):
        """Show calendar popup."""
        if self.calendar_window and self.calendar_window.winfo_exists():
            return
        
        # Create popup window
        self.calendar_window = tk.Toplevel(self)
        self.calendar_window.title("Select Date")
        self.calendar_window.transient(self)
        self.calendar_window.grab_set()
        
        # Get current date or today
        current_date = self._parse_date(self.entry_var.get()) or datetime.now()
        self.selected_year = current_date.year
        self.selected_month = current_date.month
        
        # Create calendar
        self._create_calendar()
        
        # Position window near button
        x = self.calendar_btn.winfo_rootx()
        y = self.calendar_btn.winfo_rooty() + self.calendar_btn.winfo_height()
        self.calendar_window.geometry(f"+{x}+{y}")
    
    def _create_calendar(self):
        """Create calendar widget."""
        # Navigation frame
        nav_frame = ttk.Frame(self.calendar_window)
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        # Previous month button
        ttk.Button(nav_frame, text="◀", width=3, 
                  command=self._prev_month).pack(side="left")
        
        # Month/Year label
        self.month_label = ttk.Label(
            nav_frame,
            text=f"{calendar.month_name[self.selected_month]} {self.selected_year}",
            font=("Arial", 10, "bold")
        )
        self.month_label.pack(side="left", expand=True)
        
        # Next month button
        ttk.Button(nav_frame, text="▶", width=3,
                  command=self._next_month).pack(side="right")
        
        # Calendar frame
        self.cal_frame = ttk.Frame(self.calendar_window)
        self.cal_frame.pack(padx=5, pady=5)
        
        self._draw_calendar()
        
        # Buttons frame
        btn_frame = ttk.Frame(self.calendar_window)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Today", 
                  command=self._select_today).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel",
                  command=self.calendar_window.destroy).pack(side="right", padx=5)
    
    def _draw_calendar(self):
        """Draw the calendar grid."""
        # Clear existing calendar
        for widget in self.cal_frame.winfo_children():
            widget.destroy()
        
        # Day headers
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for col, day in enumerate(days):
            label = ttk.Label(self.cal_frame, text=day, font=("Arial", 9, "bold"),
                            width=4, anchor="center")
            label.grid(row=0, column=col, padx=1, pady=1)
        
        # Get calendar for month
        cal = calendar.monthcalendar(self.selected_year, self.selected_month)
        
        # Draw days
        for row, week in enumerate(cal, start=1):
            for col, day in enumerate(week):
                if day == 0:
                    # Empty cell
                    ttk.Label(self.cal_frame, text="", width=4).grid(
                        row=row, column=col, padx=1, pady=1)
                else:
                    # Day button
                    btn = tk.Button(
                        self.cal_frame,
                        text=str(day),
                        width=3,
                        command=lambda d=day: self._select_day(d)
                    )
                    btn.grid(row=row, column=col, padx=1, pady=1)
                    
                    # Highlight today
                    today = datetime.now()
                    if (day == today.day and self.selected_month == today.month 
                        and self.selected_year == today.year):
                        btn.configure(background="#e3f2fd")
    
    def _prev_month(self):
        """Go to previous month."""
        if self.selected_month == 1:
            self.selected_month = 12
            self.selected_year -= 1
        else:
            self.selected_month -= 1
        
        self.month_label.configure(
            text=f"{calendar.month_name[self.selected_month]} {self.selected_year}"
        )
        self._draw_calendar()
    
    def _next_month(self):
        """Go to next month."""
        if self.selected_month == 12:
            self.selected_month = 1
            self.selected_year += 1
        else:
            self.selected_month += 1
        
        self.month_label.configure(
            text=f"{calendar.month_name[self.selected_month]} {self.selected_year}"
        )
        self._draw_calendar()
    
    def _select_day(self, day: int):
        """Select a specific day."""
        date_str = f"{self.selected_year:04d}-{self.selected_month:02d}-{day:02d}"
        self.set_date(date_str)
        self.calendar_window.destroy()
    
    def _select_today(self):
        """Select today's date."""
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        self.set_date(date_str)
        self.calendar_window.destroy()
    
    def _clear_date(self):
        """Clear the date."""
        self.entry_var.set("")
    
    def _parse_date(self, date_str: str):
        """Parse date string to datetime."""
        if not date_str or not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str.strip(), "%Y-%m-%d")
        except ValueError:
            return None
    
    def get_date(self) -> str:
        """Get the current date value."""
        return self.entry_var.get().strip()
    
    def set_date(self, date_str: str):
        """Set the date value."""
        self.entry_var.set(date_str)
