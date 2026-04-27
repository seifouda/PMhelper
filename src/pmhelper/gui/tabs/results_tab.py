#!/usr/bin/env python3
"""
Results Tab Module

Displays analysis results including critical path, project statistics,
and activity details in a user-friendly format.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path

from pmhelper.gui.widgets.sortable_treeview import enhance_treeview

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class ResultsTab:
    """Results tab for displaying analysis results"""

    def __init__(self, notebook, main_window):
        self.notebook = notebook
        self.main_window = main_window
        self.results_data = None
        self.analysis_mode = None

        self.create_tab()

    def create_tab(self):
        """Create the results tab"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="Results")

        # Create header frame with help button
        header_frame = ttk.Frame(self.results_frame)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 0))

        # Help button
        ttk.Button(
            header_frame,
            text="? Help",
            command=self.main_window.show_results_tab_help).pack(
            side=tk.RIGHT)

        # Create main layout with paned window
        self.paned_window = ttk.PanedWindow(
            self.results_frame, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create frames
        self.create_summary_frame()
        self.create_activities_frame()
        self.create_critical_path_frame()

    def create_summary_frame(self):
        """Create project summary frame"""
        summary_frame = ttk.LabelFrame(
            self.paned_window,
            text="Project Summary",
            padding="10")
        self.paned_window.add(summary_frame, weight=1)

        # Create two columns for summary
        left_frame = ttk.Frame(summary_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(summary_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left column labels
        self.project_duration_label = ttk.Label(
            left_frame,
            text="Project Duration: --",
            font=(
                "Arial",
                10,
                "bold"))
        self.project_duration_label.pack(anchor="w", pady=2)

        self.total_activities_label = ttk.Label(
            left_frame, text="Total Activities: --")
        self.total_activities_label.pack(anchor="w", pady=2)

        self.critical_activities_label = ttk.Label(
            left_frame, text="Critical Activities: --")
        self.critical_activities_label.pack(anchor="w", pady=2)

        # Right column labels (for PERT mode)
        self.probability_frame = ttk.Frame(right_frame)
        self.probability_frame.pack(anchor="w", fill=tk.X)

        self.expected_duration_label = ttk.Label(
            self.probability_frame, text="Expected Duration: --")
        self.expected_duration_label.pack(anchor="w", pady=2)

        self.variance_label = ttk.Label(
            self.probability_frame,
            text="Project Variance: --")
        self.variance_label.pack(anchor="w", pady=2)

        self.std_deviation_label = ttk.Label(
            self.probability_frame, text="Standard Deviation: --")
        self.std_deviation_label.pack(anchor="w", pady=2)

        # Initially hide probability frame
        self.probability_frame.pack_forget()

    def create_activities_frame(self):
        """Create activities details frame"""
        activities_frame = ttk.LabelFrame(
            self.paned_window, text="Activity Details", padding="5")
        self.paned_window.add(activities_frame, weight=2)

        # Create treeview for activities
        self.activities_tree = ttk.Treeview(activities_frame, height=12)

        # Add only vertical scrollbar
        v_scrollbar = ttk.Scrollbar(activities_frame, orient=tk.VERTICAL,
                                    command=self.activities_tree.yview)
        self.activities_tree.configure(yscrollcommand=v_scrollbar.set)

        # Pack treeview and vertical scrollbar
        self.activities_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure treeview for CPM mode by default
        self.setup_cpm_activities_tree()

    def create_critical_path_frame(self):
        """Create critical path display frame"""
        cp_frame = ttk.LabelFrame(
            self.paned_window,
            text="Critical Path",
            padding="10")
        self.paned_window.add(cp_frame, weight=1)

        # Critical path text display
        self.critical_path_text = tk.Text(cp_frame, height=6, wrap=tk.WORD)
        cp_scrollbar = ttk.Scrollbar(cp_frame, orient=tk.VERTICAL,
                                     command=self.critical_path_text.yview)
        self.critical_path_text.configure(yscrollcommand=cp_scrollbar.set)

        self.critical_path_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cp_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def setup_cmp_activities_tree(self):
        """Setup activities treeview for CPM mode"""
        # Clear existing columns
        self.activities_tree.delete(*self.activities_tree.get_children())

        # CPM columns
        columns = (
            "ID",
            "Activity",
            "Duration",
            "ES",
            "EF",
            "LS",
            "LF",
            "Float",
            "Critical")
        self.activities_tree.config(columns=columns, show='headings')

        # Configure column headings and widths
        for col in columns:
            self.activities_tree.heading(col, text=col)
            if col in ["ID"]:
                self.activities_tree.column(col, width=50, minwidth=40)
            elif col in ["Duration", "ES", "EF", "LS", "LF", "Float"]:
                self.activities_tree.column(col, width=70, minwidth=60)
            elif col in ["Critical"]:
                self.activities_tree.column(col, width=80, minwidth=70)
            else:
                self.activities_tree.column(col, width=150, minwidth=120)
        enhance_treeview(self.activities_tree)

    def setup_cpm_activities_tree(self):
        """Setup activities treeview for CPM mode"""
        self.setup_cmp_activities_tree()  # Same as CPM

    def setup_pert_activities_tree(self):
        """Setup activities treeview for PERT mode"""
        # Clear existing columns
        self.activities_tree.delete(*self.activities_tree.get_children())

        # PERT columns
        columns = (
            "ID",
            "Activity",
            "Optimistic",
            "Most Likely",
            "Pessimistic",
            "Expected",
            "Variance",
            "ES",
            "EF",
            "LS",
            "LF",
            "Float",
            "Critical")
        self.activities_tree.config(columns=columns, show='headings')

        # Configure column headings and widths
        for col in columns:
            self.activities_tree.heading(col, text=col)
            if col in ["ID"]:
                self.activities_tree.column(col, width=50, minwidth=40)
            elif col in ["Optimistic", "Most Likely", "Pessimistic", "Expected",
                         "Variance", "ES", "EF", "LS", "LF", "Float"]:
                self.activities_tree.column(col, width=70, minwidth=60)
            elif col in ["Critical"]:
                self.activities_tree.column(col, width=80, minwidth=70)
            else:
                self.activities_tree.column(col, width=120, minwidth=100)
        enhance_treeview(self.activities_tree)

    def update_results(self, results_data, analysis_mode):
        """Update the results display with new data"""
        self.results_data = results_data
        self.analysis_mode = analysis_mode

        if not results_data:
            self.clear_results()
            return

        # Setup appropriate tree view
        if analysis_mode == 'probabilistic':
            self.setup_pert_activities_tree()
            self.probability_frame.pack(anchor="w", fill=tk.X)
        else:
            self.setup_cpm_activities_tree()
            self.probability_frame.pack_forget()

        # Update summary
        self.update_summary()

        # Update activities
        self.update_activities()

        # Update critical path
        self.update_critical_path()

    def update_summary(self):
        """Update project summary information"""
        if not self.results_data:
            return

        # Basic project information
        project_duration = self.results_data.get('project_duration', '--')
        self.project_duration_label.config(
            text=f"Project Duration: {project_duration}")

        activities = self.results_data.get('activities', [])
        total_activities = len(activities)
        critical_activities = len(
            [a for a in activities if a.get('critical', False)])

        self.total_activities_label.config(
            text=f"Total Activities: {total_activities}")
        self.critical_activities_label.config(
            text=f"Critical Activities: {critical_activities}")

        # PERT-specific information
        if self.analysis_mode == 'probabilistic':
            expected_duration = self.results_data.get(
                'expected_duration', '--')
            variance = self.results_data.get('project_variance', '--')
            std_deviation = self.results_data.get('standard_deviation', '--')

            # Format with proper precision
            if expected_duration != '--':
                expected_duration = f"{expected_duration:.2f}"
            if variance != '--':
                variance = f"{variance:.3f}"
            if std_deviation != '--':
                std_deviation = f"{std_deviation:.3f}"

            self.expected_duration_label.config(
                text=f"Expected Duration: {expected_duration}")
            self.variance_label.config(text=f"Project Variance: {variance}")
            self.std_deviation_label.config(
                text=f"Standard Deviation: {std_deviation}")

    # def update_activities(self):
    #     """Update activities details"""
    #     # Clear existing data
    #     for item in self.activities_tree.get_children():
    #         self.activities_tree.delete(item)

    #     if not self.results_data:
    #         return

    #     activities = self.results_data.get('activities', [])

    #     for activity in activities:
    #         if self.analysis_mode == 'probabilistic':
    #             values = (
    #                 activity.get('id', ''),
    #                 activity.get('name', ''),
    #                 activity.get('optimistic', ''),
    #                 activity.get('most_likely', ''),
    #                 activity.get('pessimistic', ''),
    #                 f"{activity.get('expected_duration', 0):.2f}",
    #                 f"{activity.get('variance', 0):.3f}",
    #                 activity.get('earliest_start', ''),
    #                 activity.get('earliest_finish', ''),
    #                 activity.get('latest_start', ''),
    #                 activity.get('latest_finish', ''),
    #                 f"{activity.get('total_float', 0):.2f}",
    #                 "Yes" if activity.get('critical', False) else "No"
    #             )
    #         else:
    #             values = (
    #                 activity.get('id', ''),
    #                 activity.get('name', ''),
    #                 activity.get('duration', ''),
    #                 activity.get('earliest_start', ''),
    #                 activity.get('earliest_finish', ''),
    #                 activity.get('latest_start', ''),
    #                 activity.get('latest_finish', ''),
    #                 f"{activity.get('total_float', 0):.2f}",
    #                 "Yes" if activity.get('critical', False) else "No"
    #             )

    #         # Color critical activities
    #         item = self.activities_tree.insert("", tk.END, values=values)
    #         if activity.get('critical', False):
    #             self.activities_tree.set(item, "Critical", "Yes")
    #             # Try to tag for coloring (may not work on all systems)
    #             try:
    #                 self.activities_tree.item(item, tags=('critical',))
    #             except:
    #                 pass

    #     # Configure tags for critical activities
    #     try:
    #         self.activities_tree.tag_configure('critical', background='#ffdddd')
    #     except:
    #         pass

    # def update_critical_path(self):
    #     """Update critical path display"""
    #     self.critical_path_text.delete(1.0, tk.END)

    #     if not self.results_data:
    #         return

    #     critical_path = self.results_data.get('critical_path', [])

    #     if critical_path:
    #         path_text = "Critical Path:\n"
    #         path_text += " → ".join(critical_path) + "\n\n"

    #         # Add critical activities details
    #         path_text += "Critical Activities:\n"
    #         activities = self.results_data.get('activities', [])
    #         critical_activities = [a for a in activities if a.get('critical', False)]

    #         for activity in critical_activities:
    #             if self.analysis_mode == 'probabilistic':
    #                 duration = f"{activity.get('expected_duration', 0):.2f}"
    #             else:
    #                 duration = str(activity.get('duration', ''))

    #             path_text += f"• {activity.get('id', '')} - {activity.get('name', '')} (Duration: {duration})\n"

    #         # Add project statistics
    #         path_text += f"\nProject Duration: {self.results_data.get('project_duration', '--')}\n"

    #         if self.analysis_mode == 'probabilistic':
    #             path_text += f"Expected Duration: {self.results_data.get('expected_duration', '--')}\n"
    #             path_text += f"Standard Deviation: {self.results_data.get('standard_deviation', '--')}\n"
    #     else:
    #         path_text = "No critical path found. Please run analysis first."

    #     self.critical_path_text.insert(1.0, path_text)
    #     self.critical_path_text.see(1.0)

    def clear_results(self):
        """Clear all results displays"""
        # Clear summary
        self.project_duration_label.config(text="Project Duration: --")
        self.total_activities_label.config(text="Total Activities: --")
        self.critical_activities_label.config(text="Critical Activities: --")

        # Clear PERT-specific
        self.expected_duration_label.config(text="Expected Duration: --")
        self.variance_label.config(text="Project Variance: --")
        self.std_deviation_label.config(text="Standard Deviation: --")

        # Clear activities tree
        for item in self.activities_tree.get_children():
            self.activities_tree.delete(item)

        # Clear critical path
        self.critical_path_text.delete(1.0, tk.END)

        # Hide probability frame
        self.probability_frame.pack_forget()

    def export_results(self):
        """Export results to file"""
        if not self.results_data:
            messagebox.showwarning(
                "Warning", "No results to export. Please run analysis first.")
            return

        from tkinter import filedialog

        filename = filedialog.asksaveasfilename(
            title="Export Results", defaultextension=".csv", filetypes=[
                ("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")])

        if filename:
            try:
                self._export_to_file(filename)
                messagebox.showinfo(
                    "Success", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error",
                                     f"Failed to export results: {str(e)}")

    # def _export_to_file(self, filename):
    #     """Export results data to specified file"""
    #     import csv

    #     with open(filename, 'w', newline='', encoding='utf-8') as file:
    #         if filename.lower().endswith('.csv'):
    #             writer = csv.writer(file)

    #             # Write summary
    #             writer.writerow(["Project Summary"])
    #             writer.writerow(["Project Duration", self.results_data.get('project_duration', '')])
    #             writer.writerow(["Critical Path", " → ".join(self.results_data.get('critical_path', []))])

    #             if self.analysis_mode == 'probabilistic':
    #                 writer.writerow(["Expected Duration", self.results_data.get('expected_duration', '')])
    #                 writer.writerow(["Project Variance", self.results_data.get('project_variance', '')])
    #                 writer.writerow(["Standard Deviation", self.results_data.get('standard_deviation', '')])

    #             writer.writerow([])  # Empty row

    #             # Write activities header
    #             if self.analysis_mode == 'probabilistic':
    #                 writer.writerow(["ID", "Activity", "Optimistic", "Most Likely", "Pessimistic",
    #                                "Expected", "Variance", "ES", "EF", "LS", "LF", "Float", "Critical"])
    #             else:
    #                 writer.writerow(["ID", "Activity", "Duration", "ES", "EF", "LS", "LF", "Float", "Critical"])

    #             # Write activities data
    #             activities = self.results_data.get('activities', [])
    #             for activity in activities:
    #                 if self.analysis_mode == 'probabilistic':
    #                     row = [
    #                         activity.get('id', ''),
    #                         activity.get('name', ''),
    #                         activity.get('optimistic', ''),
    #                         activity.get('most_likely', ''),
    #                         activity.get('pessimistic', ''),
    #                         f"{activity.get('expected_duration', 0):.2f}",
    #                         f"{activity.get('variance', 0):.3f}",
    #                         activity.get('earliest_start', ''),
    #                         activity.get('earliest_finish', ''),
    #                         activity.get('latest_start', ''),
    #                         activity.get('latest_finish', ''),
    #                         f"{activity.get('total_float', 0):.2f}",
    #                         "Yes" if activity.get('critical', False) else "No"
    #                     ]
    #                 else:
    #                     row = [
    #                         activity.get('id', ''),
    #                         activity.get('name', ''),
    #                         activity.get('duration', ''),
    #                         activity.get('earliest_start', ''),
    #                         activity.get('earliest_finish', ''),
    #                         activity.get('latest_start', ''),
    #                         activity.get('latest_finish', ''),
    #                         f"{activity.get('total_float', 0):.2f}",
    #                         "Yes" if activity.get('critical', False) else "No"
    #                     ]
    #                 writer.writerow(row)
    #         else:
    #             # Text format
    #             file.write("Project Analysis Results\n")
    #             file.write("=" * 50 + "\n\n")

    #             file.write(f"Project Duration: {self.results_data.get('project_duration', '')}\n")
    #             file.write(f"Critical Path: {' → '.join(self.results_data.get('critical_path', []))}\n")

    #             if self.analysis_mode == 'probabilistic':
    #                 file.write(f"Expected Duration: {self.results_data.get('expected_duration', '')}\n")
    #                 file.write(f"Project Variance: {self.results_data.get('project_variance', '')}\n")
    #                 file.write(f"Standard Deviation: {self.results_data.get('standard_deviation', '')}\n")

    #             file.write("\nActivity Details:\n")
    #             file.write("-" * 30 + "\n")

    #             activities = self.results_data.get('activities', [])
    #             for activity in activities:
    #                 file.write(f"\nActivity: {activity.get('id', '')} - {activity.get('name', '')}\n")
    #                 if self.analysis_mode == 'probabilistic':
    #                     file.write(f"  Optimistic: {activity.get('optimistic', '')}\n")
    #                     file.write(f"  Most Likely: {activity.get('most_likely', '')}\n")
    #                     file.write(f"  Pessimistic: {activity.get('pessimistic', '')}\n")
    #                     file.write(f"  Expected Duration: {activity.get('expected_duration', 0):.2f}\n")
    #                     file.write(f"  Variance: {activity.get('variance', 0):.3f}\n")
    #                 else:
    #                     file.write(f"  Duration: {activity.get('duration', '')}\n")

    #                 file.write(f"  Earliest Start: {activity.get('earliest_start', '')}\n")
    #                 file.write(f"  Earliest Finish: {activity.get('earliest_finish', '')}\n")
    #                 file.write(f"  Latest Start: {activity.get('latest_start', '')}\n")
    #                 file.write(f"  Latest Finish: {activity.get('latest_finish', '')}\n")
    #                 file.write(f"  Total Float: {activity.get('total_float', 0):.2f}\n")
    #                 file.write(f"  Critical: {'Yes' if activity.get('critical', False) else 'No'}\n")

    def update_activities(self):
        """Update activities details"""
        # Clear existing data
        for item in self.activities_tree.get_children():
            self.activities_tree.delete(item)

        if not self.results_data:
            return

        activities = self.results_data.get('activities', [])

        for activity in activities:
            if self.analysis_mode == 'probabilistic':
                values = (
                    activity.get('id', ''),
                    activity.get('name', ''),
                    activity.get('optimistic', ''),
                    activity.get('most_likely', ''),
                    activity.get('pessimistic', ''),
                    # Show integer expected duration for scheduling
                    str(activity.get('expected', activity.get('duration', 0))),
                    f"{activity.get('variance', 0):.3f}",
                    activity.get('ES', ''),
                    activity.get('EF', ''),
                    activity.get('LS', ''),
                    activity.get('LF', ''),
                    str(activity.get('float', 0)),  # Show integer float
                    "Yes" if activity.get('critical', False) else "No"
                )
            else:
                values = (
                    activity.get('id', ''),
                    activity.get('name', ''),
                    activity.get('duration', ''),
                    activity.get('ES', ''),
                    activity.get('EF', ''),
                    activity.get('LS', ''),
                    activity.get('LF', ''),
                    str(activity.get('float', 0)),  # Show integer float
                    "Yes" if activity.get('critical', False) else "No"
                )

            # Color critical activities
            item = self.activities_tree.insert("", tk.END, values=values)
            if activity.get('critical', False):
                self.activities_tree.set(item, "Critical", "Yes")
                # Try to tag for coloring (may not work on all systems)
                try:
                    self.activities_tree.item(item, tags=('critical',))
                except BaseException:
                    pass

        # Configure tags for critical activities
        try:
            self.activities_tree.tag_configure(
                'critical', background='#ffdddd')
        except BaseException:
            pass

    def update_critical_path(self):
        """Update critical path display"""
        self.critical_path_text.delete(1.0, tk.END)

        if not self.results_data:
            return

        critical_path = self.results_data.get('critical_path', [])

        if critical_path:
            path_text = "Critical Path:\n"
            path_text += " → ".join(critical_path) + "\n\n"

            # Add critical activities details
            path_text += "Critical Activities:\n"
            activities = self.results_data.get('activities', [])
            critical_activities = [
                a for a in activities if a.get(
                    'critical', False)]

            for activity in critical_activities:
                if self.analysis_mode == 'probabilistic':
                    duration = f"{activity.get('expected_duration', 0):.2f}"
                else:
                    duration = str(activity.get('duration', ''))

                # FIXED: Show float value for each critical activity (should be
                # 0)
                float_val = activity.get('float', 0)
                path_text += f"• {activity.get('id',
                                               '')} - {activity.get('name',
                                                                    '')} (Duration: {duration}, Float: {float_val})\n"

            # Add project statistics
            path_text += f"\nProject Duration: {
                self.results_data.get(
                    'project_duration', '--')}\n"

            if self.analysis_mode == 'probabilistic':
                path_text += f"Expected Duration: {
                    self.results_data.get(
                        'expected_duration', '--')}\n"
                path_text += f"Standard Deviation: {
                    self.results_data.get(
                        'standard_deviation', '--')}\n"
        else:
            path_text = "No critical path found. Please run analysis first."

        self.critical_path_text.insert(1.0, path_text)
        self.critical_path_text.see(1.0)

    def _export_to_file(self, filename):
        """Export results data to specified file"""
        import csv

        with open(filename, 'w', newline='', encoding='utf-8') as file:
            if filename.lower().endswith('.csv'):
                writer = csv.writer(file)

                # Write summary
                writer.writerow(["Project Summary"])
                writer.writerow(
                    ["Project Duration", self.results_data.get('project_duration', '')])
                writer.writerow(["Critical Path", " → ".join(
                    self.results_data.get('critical_path', []))])

                if self.analysis_mode == 'probabilistic':
                    writer.writerow(
                        ["Expected Duration", self.results_data.get('expected_duration', '')])
                    writer.writerow(
                        ["Project Variance", self.results_data.get('project_variance', '')])
                    writer.writerow(
                        ["Standard Deviation", self.results_data.get('standard_deviation', '')])

                writer.writerow([])  # Empty row

                # Write activities header
                if self.analysis_mode == 'probabilistic':
                    writer.writerow(["ID",
                                     "Activity",
                                     "Optimistic",
                                     "Most Likely",
                                     "Pessimistic",
                                     "Expected",
                                     "Variance",
                                     "ES",
                                     "EF",
                                     "LS",
                                     "LF",
                                     "Float",
                                     "Critical"])
                else:
                    writer.writerow(
                        ["ID", "Activity", "Duration", "ES", "EF", "LS", "LF", "Float", "Critical"])

                # Write activities data
                activities = self.results_data.get('activities', [])
                for activity in activities:
                    if self.analysis_mode == 'probabilistic':
                        row = [
                            activity.get('id', ''),
                            activity.get('name', ''),
                            activity.get('optimistic', ''),
                            activity.get('most_likely', ''),
                            activity.get('pessimistic', ''),
                            f"{activity.get('expected_duration', 0):.2f}",
                            f"{activity.get('variance', 0):.3f}",
                            activity.get('ES', ''),  # FIXED: Use 'ES'
                            activity.get('EF', ''),  # FIXED: Use 'EF'
                            activity.get('LS', ''),  # FIXED: Use 'LS'
                            activity.get('LF', ''),  # FIXED: Use 'LF'
                            # FIXED: Use 'float'
                            f"{activity.get('float', 0):.2f}",
                            "Yes" if activity.get('critical', False) else "No"
                        ]
                    else:
                        row = [
                            activity.get('id', ''),
                            activity.get('name', ''),
                            activity.get('duration', ''),
                            activity.get('ES', ''),  # FIXED: Use 'ES'
                            activity.get('EF', ''),  # FIXED: Use 'EF'
                            activity.get('LS', ''),  # FIXED: Use 'LS'
                            activity.get('LF', ''),  # FIXED: Use 'LF'
                            # FIXED: Use 'float'
                            f"{activity.get('float', 0):.2f}",
                            "Yes" if activity.get('critical', False) else "No"
                        ]
                    writer.writerow(row)
            else:
                # Text format
                file.write("Project Analysis Results\n")
                file.write("=" * 50 + "\n\n")

                file.write(
                    f"Project Duration: {
                        self.results_data.get(
                            'project_duration',
                            '')}\n")
                file.write(
                    f"Critical Path: {
                        ' → '.join(
                            self.results_data.get(
                                'critical_path',
                                []))}\n")

                if self.analysis_mode == 'probabilistic':
                    file.write(
                        f"Expected Duration: {
                            self.results_data.get(
                                'expected_duration',
                                '')}\n")
                    file.write(
                        f"Project Variance: {
                            self.results_data.get(
                                'project_variance',
                                '')}\n")
                    file.write(
                        f"Standard Deviation: {
                            self.results_data.get(
                                'standard_deviation',
                                '')}\n")

                file.write("\nActivity Details:\n")
                file.write("-" * 30 + "\n")

                activities = self.results_data.get('activities', [])
                for activity in activities:
                    file.write(
                        f"\nActivity: {activity.get('id', '')} - {activity.get('name', '')}\n")
                    if self.analysis_mode == 'probabilistic':
                        file.write(
                            f"  Optimistic: {
                                activity.get(
                                    'optimistic',
                                    '')}\n")
                        file.write(
                            f"  Most Likely: {
                                activity.get(
                                    'most_likely',
                                    '')}\n")
                        file.write(
                            f"  Pessimistic: {
                                activity.get(
                                    'pessimistic',
                                    '')}\n")
                        file.write(
                            f"  Expected Duration: {
                                activity.get(
                                    'expected_duration',
                                    0):.2f}\n")
                        file.write(
                            f"  Variance: {
                                activity.get(
                                    'variance',
                                    0):.3f}\n")
                    else:
                        file.write(
                            f"  Duration: {
                                activity.get(
                                    'duration',
                                    '')}\n")

                    file.write(
                        f"  Earliest Start: {
                            activity.get(
                                'ES', '')}\n")  # FIXED
                    file.write(
                        f"  Earliest Finish: {
                            activity.get(
                                'EF', '')}\n")  # FIXED
                    file.write(
                        f"  Latest Start: {
                            activity.get(
                                'LS', '')}\n")  # FIXED
                    file.write(
                        f"  Latest Finish: {
                            activity.get(
                                'LF', '')}\n")  # FIXED
                    file.write(
                        f"  Total Float: {
                            activity.get(
                                'float',
                                0):.2f}\n")  # FIXED
                    file.write(
                        f"  Critical: {
                            'Yes' if activity.get(
                                'critical',
                                False) else 'No'}\n")
