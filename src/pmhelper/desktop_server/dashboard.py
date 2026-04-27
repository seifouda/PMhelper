"""
Server Status Dashboard

Advanced dashboard for monitoring server performance, statistics,
and active analysis jobs with real-time updates.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from typing import Optional
from datetime import datetime, timedelta
from collections import deque

from ..server.config import config


class ServerDashboard:
    """Advanced server monitoring dashboard."""

    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Statistics storage
        self.request_counts = deque(maxlen=60)  # Last 60 minutes
        self.response_times = deque(maxlen=100)  # Last 100 requests
        self.active_jobs = {}
        self.completed_jobs_count = 0
        self.failed_jobs_count = 0
        self.total_requests = 0

        # Create GUI components
        self.create_widgets()

        # Start monitoring if server is available
        self.start_monitoring()

    def create_widgets(self):
        """Create the dashboard GUI widgets."""
        # Main container with padding
        main_frame = ttk.Frame(self.parent_frame, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="Server Performance Dashboard", font=(
                'TkDefaultFont', 12, 'bold'))
        title_label.grid(
            row=0, column=0, columnspan=2, pady=(
                0, 20), sticky=tk.W)

        # Statistics Overview Section
        stats_frame = ttk.LabelFrame(
            main_frame, text="Statistics Overview", padding="10")
        stats_frame.grid(
            row=1, column=0, columnspan=2, sticky=(
                tk.W, tk.E), pady=(
                0, 10))
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)

        # Request statistics
        ttk.Label(
            stats_frame,
            text="Total Requests:").grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                10))
        self.total_requests_label = ttk.Label(stats_frame, text="0")
        self.total_requests_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(stats_frame, text="Requests/Min:").grid(row=0,
                                                          column=2, sticky=tk.W, padx=(20, 10))
        self.requests_per_min_label = ttk.Label(stats_frame, text="0")
        self.requests_per_min_label.grid(row=0, column=3, sticky=tk.W)

        ttk.Label(
            stats_frame, text="Avg Response Time:").grid(
            row=1, column=0, sticky=tk.W, padx=(
                0, 10), pady=(
                5, 0))
        self.avg_response_time_label = ttk.Label(stats_frame, text="0 ms")
        self.avg_response_time_label.grid(
            row=1, column=1, sticky=tk.W, pady=(5, 0))

        ttk.Label(
            stats_frame, text="Server Uptime:").grid(
            row=1, column=2, sticky=tk.W, padx=(
                20, 10), pady=(
                5, 0))
        self.uptime_label = ttk.Label(stats_frame, text="0:00:00")
        self.uptime_label.grid(row=1, column=3, sticky=tk.W, pady=(5, 0))

        # Analysis Jobs Section
        jobs_frame = ttk.LabelFrame(
            main_frame, text="Analysis Jobs", padding="10")
        jobs_frame.grid(
            row=2, column=0, columnspan=2, sticky=(
                tk.W, tk.E), pady=(
                0, 10))
        jobs_frame.columnconfigure(1, weight=1)
        jobs_frame.columnconfigure(3, weight=1)

        ttk.Label(
            jobs_frame,
            text="Active Jobs:").grid(
            row=0,
            column=0,
            sticky=tk.W,
            padx=(
                0,
                10))
        self.active_jobs_label = ttk.Label(jobs_frame, text="0")
        self.active_jobs_label.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(
            jobs_frame,
            text="Completed Jobs:").grid(
            row=0,
            column=2,
            sticky=tk.W,
            padx=(
                20,
                10))
        self.completed_jobs_label = ttk.Label(jobs_frame, text="0")
        self.completed_jobs_label.grid(row=0, column=3, sticky=tk.W)

        ttk.Label(
            jobs_frame, text="Failed Jobs:").grid(
            row=1, column=0, sticky=tk.W, padx=(
                0, 10), pady=(
                5, 0))
        self.failed_jobs_label = ttk.Label(jobs_frame, text="0")
        self.failed_jobs_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))

        ttk.Label(
            jobs_frame, text="Success Rate:").grid(
            row=1, column=2, sticky=tk.W, padx=(
                20, 10), pady=(
                5, 0))
        self.success_rate_label = ttk.Label(jobs_frame, text="100%")
        self.success_rate_label.grid(row=1, column=3, sticky=tk.W, pady=(5, 0))

        # Active Jobs List Section
        active_jobs_frame = ttk.LabelFrame(
            main_frame, text="Active Analysis Jobs", padding="10")
        active_jobs_frame.grid(
            row=3, column=0, columnspan=2, sticky=(
                tk.W, tk.E, tk.N, tk.S), pady=(
                0, 10))
        active_jobs_frame.columnconfigure(0, weight=1)
        active_jobs_frame.rowconfigure(0, weight=1)

        # Jobs treeview
        columns = ("Job ID", "Type", "Status", "Progress", "Started")
        self.jobs_tree = ttk.Treeview(
            active_jobs_frame,
            columns=columns,
            show="headings",
            height=8)

        # Define headings
        for col in columns:
            self.jobs_tree.heading(col, text=col)
            if col == "Job ID":
                self.jobs_tree.column(col, width=200)
            elif col in ["Type", "Status"]:
                self.jobs_tree.column(col, width=100)
            elif col == "Progress":
                self.jobs_tree.column(col, width=80)
            else:
                self.jobs_tree.column(col, width=120)

        # Add scrollbar for jobs tree
        jobs_scrollbar = ttk.Scrollbar(
            active_jobs_frame,
            orient=tk.VERTICAL,
            command=self.jobs_tree.yview)
        self.jobs_tree.configure(yscrollcommand=jobs_scrollbar.set)

        self.jobs_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        jobs_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Performance Graph Section (placeholder for now)
        graph_frame = ttk.LabelFrame(
            main_frame, text="Performance Metrics", padding="10")
        graph_frame.grid(
            row=4, column=0, columnspan=2, sticky=(
                tk.W, tk.E), pady=(
                0, 10))

        # Simple text-based performance display
        self.performance_text = tk.Text(
            graph_frame, height=6, width=80, state=tk.DISABLED)
        self.performance_text.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Control buttons
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky=tk.W,
            pady=(
                10,
                0))

        ttk.Button(
            controls_frame,
            text="Refresh Dashboard",
            command=self.refresh_dashboard).grid(
            row=0,
            column=0,
            padx=(
                0,
                10))
        ttk.Button(
            controls_frame,
            text="Clear Statistics",
            command=self.clear_statistics).grid(
            row=0,
            column=1,
            padx=(
                0,
                10))

        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            controls_frame,
            text="Auto-refresh (5s)",
            variable=self.auto_refresh_var).grid(
            row=0,
            column=2,
            padx=(
                20,
                0))

        # Configure grid weights for main frame
        main_frame.rowconfigure(3, weight=1)

        # Store start time for uptime calculation
        self.start_time = time.time()

    def start_monitoring(self):
        """Start the monitoring thread."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.is_monitoring = False

    def _monitoring_loop(self):
        """Main monitoring loop running in background thread."""
        while self.is_monitoring:
            try:
                # Simulate collecting server metrics
                # In a real implementation, this would query the actual server
                self.collect_server_metrics()

                # Update GUI in main thread
                self.parent_frame.after(0, self.update_dashboard)

                # Wait for next update
                time.sleep(5 if self.auto_refresh_var.get() else 10)

            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)

    def collect_server_metrics(self):
        """Collect server performance metrics."""
        # Simulate metrics collection
        # In real implementation, this would:
        # 1. Query server health endpoint
        # 2. Check database for job statistics
        # 3. Monitor system resources

        current_time = time.time()

        # Simulate request rate
        import random
        requests_this_minute = random.randint(0, 20)
        self.request_counts.append((current_time, requests_this_minute))
        self.total_requests += requests_this_minute

        # Simulate response times
        if requests_this_minute > 0:
            avg_response = random.uniform(50, 500)  # 50-500ms
            self.response_times.append(avg_response)

        # Simulate job updates
        self.update_job_statistics()

    def update_job_statistics(self):
        """Update job-related statistics."""
        # Simulate job completion
        import random

        # Randomly complete some jobs
        completed_jobs = []
        for job_id, job_info in list(self.active_jobs.items()):
            if random.random() < 0.1:  # 10% chance to complete per cycle
                completed_jobs.append(job_id)
                if random.random() < 0.9:  # 90% success rate
                    self.completed_jobs_count += 1
                else:
                    self.failed_jobs_count += 1

        for job_id in completed_jobs:
            del self.active_jobs[job_id]

        # Occasionally add new jobs
        if random.random() < 0.05:  # 5% chance to add new job
            job_id = f"job_{random.randint(1000, 9999)}"
            job_type = random.choice(["CPM", "PERT", "RCPS"])
            self.active_jobs[job_id] = {
                "type": job_type,
                "status": "running",
                "progress": f"{random.randint(10, 90)}%",
                "started": datetime.now().strftime("%H:%M:%S")
            }

    def update_dashboard(self):
        """Update dashboard display (called from main thread)."""
        # Update statistics
        self.total_requests_label.config(text=str(self.total_requests))

        # Calculate requests per minute
        current_time = time.time()
        recent_requests = [count for timestamp, count in self.request_counts
                           if current_time - timestamp <= 60]
        requests_per_min = sum(recent_requests)
        self.requests_per_min_label.config(text=str(requests_per_min))

        # Calculate average response time
        if self.response_times:
            avg_response = sum(self.response_times) / len(self.response_times)
            self.avg_response_time_label.config(text=f"{avg_response:.1f} ms")

        # Update uptime
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = str(timedelta(seconds=uptime_seconds))
        self.uptime_label.config(text=uptime_str)

        # Update job statistics
        self.active_jobs_label.config(text=str(len(self.active_jobs)))
        self.completed_jobs_label.config(text=str(self.completed_jobs_count))
        self.failed_jobs_label.config(text=str(self.failed_jobs_count))

        # Calculate success rate
        total_finished = self.completed_jobs_count + self.failed_jobs_count
        if total_finished > 0:
            success_rate = (self.completed_jobs_count / total_finished) * 100
            self.success_rate_label.config(text=f"{success_rate:.1f}%")

        # Update active jobs tree
        self.update_jobs_tree()

        # Update performance metrics display
        self.update_performance_display()

    def update_jobs_tree(self):
        """Update the active jobs tree view."""
        # Clear existing items
        for item in self.jobs_tree.get_children():
            self.jobs_tree.delete(item)

        # Add current active jobs
        for job_id, job_info in self.active_jobs.items():
            self.jobs_tree.insert("", "end", values=(
                job_id,
                job_info["type"],
                job_info["status"],
                job_info["progress"],
                job_info["started"]
            ))

    def update_performance_display(self):
        """Update the performance metrics text display."""
        self.performance_text.config(state=tk.NORMAL)
        self.performance_text.delete(1.0, tk.END)

        # Create simple performance summary
        performance_text = []
        performance_text.append("=== Performance Summary ===")

        # Request rate trend
        if len(self.request_counts) >= 2:
            recent_avg = sum(count for _,
                             count in list(self.request_counts)[-5:]) / min(5,
                                                                            len(self.request_counts))
            performance_text.append(
                f"Recent request rate: {
                    recent_avg:.1f} requests/min")

        # Response time trend
        if len(self.response_times) >= 2:
            recent_responses = list(self.response_times)[-10:]
            min_time = min(recent_responses)
            max_time = max(recent_responses)
            performance_text.append(
                f"Response time range: {min_time:.1f} - {max_time:.1f} ms")

        # System status
        performance_text.append("")
        performance_text.append("=== System Status ===")
        performance_text.append(f"Server host: {config.HOST}:{config.PORT}")
        performance_text.append(
            f"Debug mode: {
                'Enabled' if config.DEBUG else 'Disabled'}")
        performance_text.append(
            f"Network access: {
                'Enabled' if config.is_network_mode() else 'Localhost only'}")

        # Resource usage (simulated)
        import random
        cpu_usage = random.uniform(10, 40)
        memory_usage = random.uniform(20, 60)
        performance_text.append(f"CPU usage: {cpu_usage:.1f}%")
        performance_text.append(f"Memory usage: {memory_usage:.1f}%")

        self.performance_text.insert(1.0, "\n".join(performance_text))
        self.performance_text.config(state=tk.DISABLED)

    def refresh_dashboard(self):
        """Manually refresh the dashboard."""
        self.collect_server_metrics()
        self.update_dashboard()

    def clear_statistics(self):
        """Clear all collected statistics."""
        self.request_counts.clear()
        self.response_times.clear()
        self.active_jobs.clear()
        self.completed_jobs_count = 0
        self.failed_jobs_count = 0
        self.total_requests = 0
        self.start_time = time.time()

        self.update_dashboard()

    def add_job(self, job_id: str, job_type: str, status: str = "pending"):
        """Add a new job to the monitoring."""
        self.active_jobs[job_id] = {
            "type": job_type,
            "status": status,
            "progress": "0%",
            "started": datetime.now().strftime("%H:%M:%S")
        }

    def update_job_progress(
            self,
            job_id: str,
            progress: str,
            status: str = None):
        """Update job progress."""
        if job_id in self.active_jobs:
            self.active_jobs[job_id]["progress"] = progress
            if status:
                self.active_jobs[job_id]["status"] = status

    def complete_job(self, job_id: str, success: bool = True):
        """Mark a job as completed."""
        if job_id in self.active_jobs:
            del self.active_jobs[job_id]
            if success:
                self.completed_jobs_count += 1
            else:
                self.failed_jobs_count += 1

    def cleanup(self):
        """Cleanup resources when the dashboard is destroyed."""
        self.stop_monitoring()


__all__ = ["ServerDashboard"]
