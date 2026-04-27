"""
Server Tab

Tab component for server control and monitoring within the PMHelper main GUI.
Provides server management interface integrated with the existing tab system.
"""

import tkinter as tk
from tkinter import ttk
from ...desktop_server.server_control import ServerControlPanel
from ...desktop_server.dashboard import ServerDashboard


class ServerTab:
    """Server control and monitoring tab for the main PMHelper GUI."""

    def __init__(self, notebook, main_window):
        """Initialize the server tab."""
        self.notebook = notebook
        self.main_window = main_window

        # Create tab frame
        self.server_frame = ttk.Frame(notebook)
        self.notebook.add(self.server_frame, text="Server")

        # Create sub-notebook for server control and dashboard
        self.server_notebook = ttk.Notebook(self.server_frame)
        self.server_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create control panel tab
        self.control_frame = ttk.Frame(self.server_notebook)
        self.server_notebook.add(self.control_frame, text="Control Panel")

        # Create dashboard tab
        self.dashboard_frame = ttk.Frame(self.server_notebook)
        self.server_notebook.add(self.dashboard_frame, text="Dashboard")

        # Initialize control panel and dashboard
        self.control_panel = ServerControlPanel(self.control_frame)
        self.dashboard = ServerDashboard(self.dashboard_frame)

        # Set up communication between control panel and dashboard
        self.control_panel.set_status_callback(self.on_server_status_changed)

        # Add server info section
        self.create_info_section()

    def create_info_section(self):
        """Create an information section about server mode."""
        # Add info frame at the top of server frame
        info_frame = ttk.LabelFrame(
            self.server_frame,
            text="Server Mode Information",
            padding="10")
        info_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        info_text = """
PMHelper Server Mode allows you to run PMHelper as a local web server, providing REST API access
to all analysis functions (CPM, PERT, RCPS). This enables:

• Web-based access from browsers and other applications
• Integration with external tools and scripts
• Remote analysis capabilities (when network access is enabled)
• API documentation at /docs when server is running

Use the Control Panel to start/stop the server and configure settings.
Monitor server performance and active jobs using the Dashboard.
        """.strip()

        info_label = ttk.Label(
            info_frame,
            text=info_text,
            wraplength=800,
            justify=tk.LEFT)
        info_label.pack(anchor=tk.W)

    def on_server_status_changed(self, is_running: bool):
        """Handle server status changes."""
        # Update main window status
        if hasattr(self.main_window, 'set_status'):
            status = "Server running" if is_running else "Server stopped"
            self.main_window.set_status(f"PMHelper {status}")

        # Update dashboard monitoring
        if is_running:
            self.dashboard.start_monitoring()
        else:
            self.dashboard.stop_monitoring()

    def is_server_running(self) -> bool:
        """Check if server is currently running."""
        return self.control_panel.is_server_running if self.control_panel else False

    def get_server_url(self) -> str:
        """Get the current server URL."""
        from ...server.config import config
        return config.get_server_url()

    def get_server_status_info(self) -> dict:
        """Get comprehensive server status information."""
        return {
            "running": self.is_server_running(),
            "url": self.get_server_url(),
            "docs_url": f"{
                self.get_server_url()}/docs" if self.is_server_running() else None,
            "active_jobs": len(
                self.dashboard.active_jobs) if self.dashboard else 0,
            "completed_jobs": self.dashboard.completed_jobs_count if self.dashboard else 0,
            "failed_jobs": self.dashboard.failed_jobs_count if self.dashboard else 0}

    def cleanup(self):
        """Cleanup resources when tab is destroyed."""
        if self.control_panel:
            self.control_panel.cleanup()
        if self.dashboard:
            self.dashboard.cleanup()


__all__ = ["ServerTab"]
