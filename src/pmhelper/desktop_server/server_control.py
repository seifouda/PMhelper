"""
Desktop Server Control GUI

GUI interface for controlling the PMHelper server from within the desktop application.
Provides server start/stop functionality, status monitoring, and configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import asyncio
import logging
import webbrowser
from typing import Optional, Callable

# Graceful import handling for server components
try:
    import uvicorn
    from ..server.config import config
    from ..server.main import app
    SERVER_AVAILABLE = True
except ImportError as e:
    SERVER_AVAILABLE = False
    SERVER_IMPORT_ERROR = str(e)

    # Create mock config for GUI functionality
    class MockConfig:
        PORT = 8000
        DEBUG = False
        HOST = "127.0.0.1"

        def get_server_url(self):
            return f"http://{self.HOST}:{self.PORT}"

        def get_docs_url(self):
            return f"http://{self.HOST}:{self.PORT}/docs"

        def is_network_mode(self):
            return self.HOST != "127.0.0.1"

        def enable_network_access(self):
            self.HOST = "0.0.0.0"

        def disable_network_access(self):
            self.HOST = "127.0.0.1"

    config = MockConfig()
    app = None


class ServerControlPanel:
    """GUI panel for controlling the PMHelper server."""

    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame
        self.server_thread: Optional[threading.Thread] = None
        self.server_task: Optional[asyncio.Task] = None
        self.is_server_running = False
        self.status_callback: Optional[Callable] = None

        # Setup logging capture
        self.log_messages = []
        self.setup_logging()

        # Create GUI components
        self.create_widgets()

        # Update status initially
        self.update_status_display()

    def setup_logging(self):
        """Setup logging to capture server messages."""
        # Create custom log handler to capture server logs
        class GUILogHandler(logging.Handler):
            def __init__(self, control_panel):
                super().__init__()
                self.control_panel = control_panel

            def emit(self, record):
                log_entry = self.format(record)
                self.control_panel.add_log_message(log_entry)

        # Add our handler to relevant loggers
        self.gui_handler = GUILogHandler(self)
        self.gui_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        # Add to FastAPI and uvicorn loggers
        logging.getLogger("pmhelper.server").addHandler(self.gui_handler)
        logging.getLogger("uvicorn").addHandler(self.gui_handler)
        logging.getLogger("fastapi").addHandler(self.gui_handler)

    def create_widgets(self):
        """Create the GUI widgets for server control."""
        # Main container with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsiveness
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="PMHelper Server Control",
                                font=('TkDefaultFont', 12, 'bold'))
        title_label.grid(
            row=0, column=0, columnspan=3, pady=(
                0, 20), sticky=tk.W)

        # Server Status Section
        status_frame = ttk.LabelFrame(
            main_frame, text="Server Status", padding="10")
        status_frame.grid(
            row=1, column=0, columnspan=3, sticky=(
                tk.W, tk.E), pady=(
                0, 10))
        status_frame.columnconfigure(1, weight=1)

        # Status indicator
        ttk.Label(
            status_frame,
            text="Status:").grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                10))
        self.status_label = ttk.Label(
            status_frame, text="Stopped", foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W)

        # Server URL
        ttk.Label(
            status_frame,
            text="URL:").grid(
            row=1,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                10),
            pady=(
                5,
                0))
        self.url_label = ttk.Label(
            status_frame,
            text=config.get_server_url(),
            foreground="blue",
            cursor="hand2")
        self.url_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        self.url_label.bind("<Button-1>", self.open_server_url)

        # API Documentation URL
        ttk.Label(
            status_frame,
            text="API Docs:").grid(
            row=2,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                10),
            pady=(
                5,
                0))
        self.docs_label = ttk.Label(
            status_frame,
            text=config.get_docs_url(),
            foreground="blue",
            cursor="hand2")
        self.docs_label.grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        self.docs_label.bind("<Button-1>", self.open_docs_url)

        # Control Buttons Section
        control_frame = ttk.LabelFrame(
            main_frame, text="Server Controls", padding="10")
        control_frame.grid(
            row=2, column=0, columnspan=3, sticky=(
                tk.W, tk.E), pady=(
                0, 10))

        # Start/Stop buttons
        self.start_button = ttk.Button(
            control_frame,
            text="Start Server",
            command=self.start_server)
        self.start_button.grid(row=0, column=0, padx=(0, 10))

        self.stop_button = ttk.Button(
            control_frame,
            text="Stop Server",
            command=self.stop_server,
            state="disabled")
        self.stop_button.grid(row=0, column=1, padx=(0, 20))

        # Network access toggle
        self.network_var = tk.BooleanVar(value=config.is_network_mode())
        self.network_checkbox = ttk.Checkbutton(
            control_frame,
            text="Allow network access (other computers)",
            variable=self.network_var,
            command=self.toggle_network_access
        )
        self.network_checkbox.grid(row=0, column=2, padx=(20, 0))

        # Configuration Section
        config_frame = ttk.LabelFrame(
            main_frame, text="Configuration", padding="10")
        config_frame.grid(
            row=3, column=0, columnspan=3, sticky=(
                tk.W, tk.E), pady=(
                0, 10))
        config_frame.columnconfigure(1, weight=1)

        # Port configuration
        ttk.Label(
            config_frame,
            text="Port:").grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                10))
        self.port_var = tk.StringVar(value=str(config.PORT))
        self.port_entry = ttk.Entry(
            config_frame, textvariable=self.port_var, width=10)
        self.port_entry.grid(row=0, column=1, sticky=tk.W)
        self.port_entry.bind('<FocusOut>', self.update_port)

        # Debug mode toggle
        self.debug_var = tk.BooleanVar(value=config.DEBUG)
        debug_checkbox = ttk.Checkbutton(
            config_frame,
            text="Debug mode",
            variable=self.debug_var,
            command=self.toggle_debug_mode
        )
        debug_checkbox.grid(row=0, column=2, padx=(20, 0))

        # Server Log Section
        log_frame = ttk.LabelFrame(
            main_frame, text="Server Logs", padding="10")
        log_frame.grid(
            row=4, column=0, columnspan=3, sticky=(
                tk.W, tk.E, tk.N, tk.S), pady=(
                0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Log display with scrollbar
        self.log_display = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=80,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Log control buttons
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))

        ttk.Button(
            log_controls,
            text="Clear Logs",
            command=self.clear_logs).grid(
            row=0,
            column=0,
            padx=(
                0,
                10))
        ttk.Button(
            log_controls,
            text="Refresh",
            command=self.refresh_logs).grid(
            row=0,
            column=1)

        # Configure grid weights for the main frame
        main_frame.rowconfigure(4, weight=1)

    def start_server(self):
        """Start the PMHelper server."""
        if not SERVER_AVAILABLE:
            messagebox.showerror(
                "Server Unavailable",
                f"Server components are not available.\n\nError: {SERVER_IMPORT_ERROR}\n\n"
                "Please install server dependencies:\npip install fastapi uvicorn sqlalchemy pydantic aiosqlite"
            )
            return

        try:
            if self.is_server_running:
                messagebox.showinfo(
                    "Server Status", "Server is already running.")
                return

            # Update configuration based on GUI settings
            config.PORT = int(self.port_var.get())
            config.DEBUG = self.debug_var.get()

            # Start server in background thread
            self.server_thread = threading.Thread(
                target=self._run_server, daemon=True)
            self.server_thread.start()

            # Update UI
            self.is_server_running = True
            self.update_status_display()
            self.add_log_message("Starting PMHelper server...")

        except ValueError:
            messagebox.showerror(
                "Configuration Error",
                "Invalid port number. Please enter a valid port.")
        except Exception as e:
            messagebox.showerror(
                "Server Error",
                f"Failed to start server: {
                    str(e)}")
            self.add_log_message(f"Error starting server: {str(e)}")

    def stop_server(self):
        """Stop the PMHelper server."""
        try:
            if not self.is_server_running:
                messagebox.showinfo("Server Status", "Server is not running.")
                return

            # Signal server to stop
            self.is_server_running = False

            # Update UI immediately
            self.update_status_display()
            self.add_log_message("Stopping PMHelper server...")

            # Note: uvicorn server will be stopped by the thread cleanup

        except Exception as e:
            messagebox.showerror(
                "Server Error",
                f"Failed to stop server: {
                    str(e)}")
            self.add_log_message(f"Error stopping server: {str(e)}")

    def _run_server(self):
        """Run the FastAPI server in a background thread."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Configure uvicorn
            server_config = uvicorn.Config(
                app,
                host=config.HOST,
                port=config.PORT,
                log_level="info" if config.DEBUG else "warning",
                reload=False,  # Disable reload in GUI mode
                access_log=config.DEBUG
            )

            server = uvicorn.Server(server_config)

            # Run server until stopped
            loop.run_until_complete(server.serve())

        except Exception as e:
            self.add_log_message(f"Server thread error: {str(e)}")
        finally:
            # Cleanup
            self.is_server_running = False
            # Update UI in main thread
            self.parent_frame.after(0, self.update_status_display)
            self.add_log_message("Server stopped.")

    def toggle_network_access(self):
        """Toggle network access mode."""
        if self.network_var.get():
            config.enable_network_access()
            self.add_log_message(
                "Network access enabled - server accessible from other computers")
        else:
            config.disable_network_access()
            self.add_log_message(
                "Network access disabled - server accessible from localhost only")

        # Update URL displays
        self.url_label.config(text=config.get_server_url())
        self.docs_label.config(text=config.get_docs_url())

    def toggle_debug_mode(self):
        """Toggle debug mode."""
        config.DEBUG = self.debug_var.get()
        mode = "enabled" if config.DEBUG else "disabled"
        self.add_log_message(f"Debug mode {mode}")

    def update_port(self, event=None):
        """Update port configuration."""
        try:
            new_port = int(self.port_var.get())
            if new_port != config.PORT:
                config.PORT = new_port
                # Update URL displays
                self.url_label.config(text=config.get_server_url())
                self.docs_label.config(text=config.get_docs_url())
                self.add_log_message(f"Port updated to {new_port}")
        except ValueError:
            # Reset to current config if invalid
            self.port_var.set(str(config.PORT))
            messagebox.showerror(
                "Invalid Port",
                "Please enter a valid port number.")

    def update_status_display(self):
        """Update the status display elements."""
        if self.is_server_running:
            self.status_label.config(text="Running", foreground="green")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
        else:
            self.status_label.config(text="Stopped", foreground="red")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

        # Update URLs
        self.url_label.config(text=config.get_server_url())
        self.docs_label.config(text=config.get_docs_url())

        # Call status callback if set
        if self.status_callback:
            self.status_callback(self.is_server_running)

    def add_log_message(self, message: str):
        """Add a message to the log display."""
        # Add to internal log
        self.log_messages.append(message)

        # Keep only last 1000 messages to prevent memory issues
        if len(self.log_messages) > 1000:
            self.log_messages = self.log_messages[-1000:]

        # Update GUI in main thread
        self.parent_frame.after(0, self._update_log_display, message)

    def _update_log_display(self, message: str):
        """Update the log display widget (must be called from main thread)."""
        # Safety check: ensure log_display exists before updating
        if not hasattr(self, 'log_display') or self.log_display is None:
            return

        try:
            self.log_display.config(state=tk.NORMAL)
            self.log_display.insert(tk.END, message + "\n")
            self.log_display.see(tk.END)  # Auto-scroll to bottom
            self.log_display.config(state=tk.DISABLED)
        except tk.TclError:
            # Widget might have been destroyed
            pass

    def clear_logs(self):
        """Clear the log display."""
        if not hasattr(self, 'log_display') or self.log_display is None:
            return

        try:
            self.log_display.config(state=tk.NORMAL)
            self.log_display.delete(1.0, tk.END)
            self.log_display.config(state=tk.DISABLED)
            self.log_messages.clear()
            self.add_log_message("Logs cleared.")
        except tk.TclError:
            pass

    def refresh_logs(self):
        """Refresh the log display."""
        if not hasattr(self, 'log_display') or self.log_display is None:
            return

        try:
            self.log_display.config(state=tk.NORMAL)
            self.log_display.delete(1.0, tk.END)
            for message in self.log_messages:
                self.log_display.insert(tk.END, message + "\n")
            self.log_display.see(tk.END)
            self.log_display.config(state=tk.DISABLED)
        except tk.TclError:
            pass

    def open_server_url(self, event=None):
        """Open the server URL in the default browser."""
        if self.is_server_running:
            webbrowser.open(config.get_server_url())
        else:
            messagebox.showinfo(
                "Server Not Running",
                "Please start the server first.")

    def open_docs_url(self, event=None):
        """Open the API documentation URL in the default browser."""
        if self.is_server_running:
            webbrowser.open(config.get_docs_url())
        else:
            messagebox.showinfo(
                "Server Not Running",
                "Please start the server first.")

    def set_status_callback(self, callback: Callable[[bool], None]):
        """Set a callback function to be called when server status changes."""
        self.status_callback = callback

    def cleanup(self):
        """Cleanup resources when the panel is destroyed."""
        if self.is_server_running:
            self.stop_server()

        # Remove log handler
        if hasattr(self, 'gui_handler'):
            logging.getLogger("pmhelper.server").removeHandler(
                self.gui_handler)
            logging.getLogger("uvicorn").removeHandler(self.gui_handler)
            logging.getLogger("fastapi").removeHandler(self.gui_handler)


__all__ = ["ServerControlPanel"]
