#!/usr/bin/env python3
"""
Critical Path Method (CPM) and PERT Analysis Desktop Application

A comprehensive desktop application with GUI for analyzing project networks using
both deterministic CPM and probabilistic PERT methods.
Users can input activities via a table interface or load from CSV.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
import matplotlib.patches as mpatches
from tabulate import tabulate
import csv
import io
import sys
from collections import defaultdict
import numpy as np
import matplotlib.backends.backend_agg as agg
from PIL import Image, ImageTk
import textwrap
import pandas as pd
from matplotlib.colors import ListedColormap
import math
from scipy.stats import norm

# Import PERT analyzer
from pert_analyzer import PERTAnalyzer


class CPMAnalyzer:
    """Core CPM analysis functionality"""

    def __init__(self):
        self.G = None
        self.critical_paths = []
        self.critical_activities = []

    def load_activities_from_data(self, activities_data):
        """Load activities from list of dictionaries"""
        activities = []

        for row in activities_data:
            # Convert duration to integer
            try:
                duration = int(row['duration'])
            except (ValueError, KeyError):
                raise ValueError(
                    f"Duration for activity {
                        row.get(
                            'id',
                            'Unknown')} must be a number")

            # Handle crash duration and cost
            try:
                # Default to normal duration
                min_duration = int(row.get('min_duration', duration))
                if min_duration > duration:
                    min_duration = duration  # Ensure min_duration <= duration
            except (ValueError, TypeError):
                min_duration = duration

            try:
                crash_cost = float(row.get('crash_cost', 0))
            except (ValueError, TypeError):
                crash_cost = 0

            # Process predecessors (comma-separated list)
            predecessors = []
            if row.get('predecessors') and str(row['predecessors']).strip():
                predecessors = [
                    p.strip() for p in str(
                        row['predecessors']).split(',') if p.strip()]

            # Get activity name
            activity_name = row.get('activity', '').strip()

            # Handle resource demand
            try:
                resource_demand = int(row.get('resource_demand', 0))
            except (ValueError, TypeError):
                resource_demand = 0

            # Handle normal cost
            try:
                normal_cost = float(row.get('normal_cost', 0))
            except (ValueError, TypeError):
                normal_cost = 0

            activities.append({
                'id': row['id'],
                'activity': activity_name,
                'min_duration': min_duration,
                'crash_cost': crash_cost,
                'duration': duration,
                'predecessors': predecessors,
                'resource_demand': resource_demand,
                'normal_cost': normal_cost
            })

        return activities

    def build_network(self, activities):
        """Build a directed graph network from activity data"""
        # Create directed graph
        G = nx.DiGraph()

        # Add all activities as nodes with duration attribute
        for activity in activities:
            G.add_node(
                activity['id'],
                duration=activity['duration'],
                min_duration=activity.get(
                    'min_duration', activity['duration']),  # NEW
                crash_cost=activity.get(
                    'crash_cost', 0),                         # NEW
                activity=activity.get('activity', ''),
                resource_demand=activity.get('resource_demand', 0),
                normal_cost=activity.get(
                    'normal_cost', 0)                        # NEW
            )

        # Add edges based on predecessor relationships
        for activity in activities:
            if 'predecessors' in activity and activity['predecessors']:
                for predecessor in activity['predecessors']:
                    if predecessor in G:
                        G.add_edge(predecessor, activity['id'])

        # Add START node and connect it to nodes with no predecessors
        start_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
        if start_nodes:
            G.add_node('START', duration=0, activity='Start')
            for node in start_nodes:
                G.add_edge('START', node)

        # Add END node and connect nodes with no successors to it
        end_nodes = [node for node in G.nodes() if G.out_degree(node)
                     == 0 and node != 'START']
        if end_nodes:
            G.add_node('END', duration=0, activity='End')
            for node in end_nodes:
                G.add_edge(node, 'END')

        return G

    def forward_pass(self, G):
        """Perform forward pass to calculate Early Start (ES) and Early Finish (EF)"""
        start_activities = [
            node for node in G.nodes() if G.in_degree(node) == 0]

        nx.set_node_attributes(G, 0, 'ES')
        nx.set_node_attributes(G, 0, 'EF')

        for node in nx.topological_sort(G):
            duration = G.nodes[node]['duration']

            if node in start_activities:
                G.nodes[node]['ES'] = 0
            else:
                pred_ef = [G.nodes[pred]['EF']
                           for pred in G.predecessors(node)]
                G.nodes[node]['ES'] = max(pred_ef) if pred_ef else 0

            G.nodes[node]['EF'] = G.nodes[node]['ES'] + duration

        return G

    def backward_pass(self, G):
        """Perform backward pass to calculate Late Start (LS) and Late Finish (LF)"""
        end_activities = [
            node for node in G.nodes() if G.out_degree(node) == 0]

        project_duration = max([G.nodes[node]['EF'] for node in G.nodes()])
        nx.set_node_attributes(G, project_duration, 'LF')
        nx.set_node_attributes(G, project_duration, 'LS')

        for node in reversed(list(nx.topological_sort(G))):
            duration = G.nodes[node]['duration']

            if node in end_activities:
                G.nodes[node]['LF'] = project_duration
            else:
                succ_ls = [G.nodes[succ]['LS'] for succ in G.successors(node)]
                G.nodes[node]['LF'] = min(
                    succ_ls) if succ_ls else project_duration

            G.nodes[node]['LS'] = G.nodes[node]['LF'] - duration

        return G

    def calculate_float(self, G):
        """Calculate float (slack) for each activity"""
        for node in G.nodes():
            G.nodes[node]['float'] = G.nodes[node]['LS'] - G.nodes[node]['ES']
        return G

    def identify_critical_path(self, G):
        """Identify the critical path (activities with zero float)"""
        critical_activities = [
            node for node in G.nodes() if G.nodes[node]['float'] == 0]
        critical_subgraph = G.subgraph(critical_activities)

        start_nodes = [node for node in critical_subgraph.nodes(
        ) if critical_subgraph.in_degree(node) == 0]
        end_nodes = [node for node in critical_subgraph.nodes(
        ) if critical_subgraph.out_degree(node) == 0]

        longest_path = []
        max_length = 0

        for start in start_nodes:
            for end in end_nodes:
                try:
                    paths = list(
                        nx.all_simple_paths(
                            critical_subgraph, start, end))
                    for path in paths:
                        if len(path) > max_length:
                            max_length = len(path)
                            longest_path = path
                except nx.NetworkXNoPath:
                    pass

        return [longest_path] if longest_path else [
            critical_activities], critical_activities

    def calculate_additional_metrics(self, G, activities_data):
        """Calculate additional metrics for each activity"""
        # Create a mapping of activity data for resource information
        activity_map = {act['id']: act for act in activities_data}

        for node in G.nodes():
            if node not in ['START', 'END']:
                # Number of predecessors
                G.nodes[node]['num_predecessors'] = G.in_degree(node)

                # Number of immediate successors
                G.nodes[node]['num_immediate_successors'] = G.out_degree(node)

                # Number of total successors (all activities after this one)
                total_successors = set()

                def get_all_successors(current_node):
                    for successor in G.successors(current_node):
                        if successor not in [
                                'START', 'END'] and successor not in total_successors:
                            total_successors.add(successor)
                            get_all_successors(successor)

                get_all_successors(node)
                G.nodes[node]['num_total_successors'] = len(total_successors)

                # Resource demand (from input data if available)
                activity_data = activity_map.get(node, {})
                resource_demand = activity_data.get('resource_demand', 0)
                try:
                    G.nodes[node]['resource_demand'] = int(
                        resource_demand) if resource_demand else 0
                except (ValueError, TypeError):
                    G.nodes[node]['resource_demand'] = 0

                # Cumulative demand (resource_demand * duration)
                G.nodes[node]['cumulative_demand'] = G.nodes[node]['resource_demand'] * \
                    G.nodes[node]['duration']

                # GRPW (Greatest Rank Positional Weight) = duration + sum of
                # durations of all successors
                grpw = G.nodes[node]['duration']
                for successor in total_successors:
                    grpw += G.nodes[successor]['duration']
                G.nodes[node]['grpw'] = grpw
            else:
                # Set default values for START and END nodes
                G.nodes[node]['num_predecessors'] = 0
                G.nodes[node]['num_immediate_successors'] = 0
                G.nodes[node]['num_total_successors'] = 0
                G.nodes[node]['resource_demand'] = 0
                G.nodes[node]['cumulative_demand'] = 0
                G.nodes[node]['grpw'] = 0

        return G

    def analyze(self, activities_data):
        """Perform complete CPM analysis"""
        activities = self.load_activities_from_data(activities_data)
        self.G = self.build_network(activities)
        self.G = self.forward_pass(self.G)
        self.G = self.backward_pass(self.G)
        self.G = self.calculate_float(self.G)
        self.critical_paths, self.critical_activities = self.identify_critical_path(
            self.G)
        self.G = self.calculate_additional_metrics(self.G, activities_data)
        self.critical_paths, self.critical_activities = self.identify_critical_path(
            self.G)

        return self.G, self.critical_paths, self.critical_activities

    ##########################################################################

    def build_cpm_schedule_table(self, df_gantt, resource_limit):
        """
        Build the initial CPM-based schedule table.
        Returns: DataFrame (table), list of time units, dict of critical activities
        """
        print(
            f"[DEBUG] rcps_heuristic_schedule_table: type(df_gantt)={
                type(df_gantt)}, value={
                repr(df_gantt)[
                    :200]}")
        df = df_gantt.copy()
        # Ensure correct columns
        required = [
            'id',
            'duration',
            'resource',
            'early_start',
            'late_finish',
            'float',
            'predecessors']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        df['critical'] = df['float'] == 0
        # Time units: from 1 to max LF
        max_time = int(df['late_finish'].max())
        time_cols = list(range(1, max_time + 1))
        # Build table
        print(
            f"[DEBUG] build_cpm_schedule_table: type(df)={
                type(df)}, value={
                repr(df)[
                    :200]}")
        table = df[['id', 'duration', 'resource',
                    'early_start', 'late_finish', 'float']].copy()
        for t in time_cols:
            table[t] = ''
        # Fill schedule cells
        for idx, row in table.iterrows():
            es = int(row['early_start'])
            dur = int(row['duration'])
            for t in range(es + 1, es + dur + 1):  # time units are 1-based
                if t in time_cols:
                    table.at[idx, t] = 'S'
        # Add resource rows
        resource_available = [resource_limit] * len(time_cols)
        resource_scheduled = []
        for t in time_cols:
            resource_scheduled.append(
                table[table[t] == 'S']['resource'].sum()
            )
        # Append resource rows
        resource_row = pd.Series(
            ['RA', '', resource_limit, '', '', ''] + resource_available, index=table.columns)
        scheduled_row = pd.Series(
            ['RS', '', '', '', '', ''] + resource_scheduled, index=table.columns)
        table = pd.concat([table, pd.DataFrame(
            [resource_row, scheduled_row])], ignore_index=True)
        return table, time_cols, set(df[df['critical']]['id'])

    def rcps_heuristic_schedule_table(
            self,
            df_gantt,
            resource_limit,
            priority_rule='minimum_slack'):
        """
        Apply RCPS heuristic and build the actual schedule table.
        Returns: DataFrame (table), dict of actual start times, dict of critical activities
        """
        if df_gantt is None:
            raise ValueError(
                "No project data available. Please run analysis before running RCPS scheduling.")
        df = df_gantt.copy()
        df['critical'] = df['float'] == 0

        # Prepare schedule tracking
        tasks = df.set_index('id')
        tasks['scheduled'] = False
        tasks['actual_start'] = None
        tasks['actual_finish'] = None
        current_time = 0
        resource_usage = {}
        unscheduled = set(tasks.index)
        pred_map = {tid: [p for p in str(tasks.at[tid, 'predecessors']).split(
            ',') if p and p != 'nan'] for tid in tasks.index}

        # Scheduling loop
        while unscheduled:
            # Find ready tasks
            ready = []
            for tid in unscheduled:
                preds = pred_map[tid]
                if all(tasks.at[p, 'scheduled'] and tasks.at[p,
                       'actual_finish'] <= current_time for p in preds):
                    if tasks.at[tid, 'early_start'] <= current_time:
                        ready.append(tid)

            # Sort ready tasks by selected priority rule
            if priority_rule == 'minimum_slack':
                ready.sort(key=lambda tid: (
                    tasks.at[tid, 'float'],
                    tasks.at[tid, 'duration'],
                    tid
                ))
            elif priority_rule == 'shortest_duration':
                ready.sort(key=lambda tid: (
                    tasks.at[tid, 'duration'],
                    tasks.at[tid, 'float'],
                    tid
                ))
            elif priority_rule == 'earliest_start':
                ready.sort(key=lambda tid: (
                    tasks.at[tid, 'early_start'],
                    tasks.at[tid, 'float'],
                    tid
                ))
            else:
                ready.sort(key=lambda tid: tid)  # Default: by ID

            # Try to schedule the first ready task
            scheduled_this_step = False
            for tid in ready:
                dur = int(tasks.at[tid, 'duration'])
                res = int(tasks.at[tid, 'resource'])
                # Check resource availability
                can_schedule = True
                for t in range(current_time + 1, current_time + dur + 1):
                    if resource_usage.get(t, 0) + res > resource_limit:
                        can_schedule = False
                        break
                if can_schedule:
                    tasks.at[tid, 'actual_start'] = current_time
                    tasks.at[tid, 'actual_finish'] = current_time + dur
                    tasks.at[tid, 'scheduled'] = True
                    for t in range(current_time + 1, current_time + dur + 1):
                        resource_usage[t] = resource_usage.get(t, 0) + res
                    unscheduled.remove(tid)
                    scheduled_this_step = True
                    break
            if not scheduled_this_step:
                current_time += 1

        # After scheduling, get the actual RCPS project duration
        actual_project_duration = max(
            [tasks.at[tid, 'actual_finish'] for tid in tasks.index])

        # Build time columns based on actual RCPS duration
        time_cols = list(range(1, actual_project_duration + 1))

        # Build table
        table = tasks.reset_index()[['id',
                                     'duration',
                                     'resource',
                                     'early_start',
                                     'late_finish',
                                     'float',
                                     'actual_start']].copy()

        # Ensure all time columns are initialized
        for t in time_cols:
            table[t] = ''
            if t not in resource_usage:
                resource_usage[t] = 0

        # Fill schedule cells for all activities FIRST
        for idx, row in table.iterrows():
            if row['id'] in ['RA', 'RS']:
                continue
            start = int(row['actual_start'])
            dur = int(row['duration'])
            resource_demand = int(row['resource'])

            # Fill schedule cells with resource demand
            for t in range(start + 1, start + dur + 1):
                if t in time_cols:
                    table.at[idx, t] = int(resource_demand)

        # MOVED: Calculate resource_scheduled AFTER all activities are filled
        resource_scheduled = []
        for t in time_cols:
            # Sum all resource demands that are active in time period t
            total_resources = 0
            for idx, row in table.iterrows():
                if row['id'] not in ['RA', 'RS']:
                    if isinstance(row.get(t, ''), int) and row[t] > 0:
                        total_resources += row[t]
            resource_scheduled.append(total_resources)

        # Add resource rows
        resource_available = [resource_limit] * len(time_cols)
        resource_row = pd.Series(
            ['RA', '', '', '', '', '', ''] + resource_available, index=table.columns)
        scheduled_row = pd.Series(
            ['RS', '', '', '', '', '', ''] + resource_scheduled, index=table.columns)
        table = pd.concat([table, pd.DataFrame(
            [resource_row, scheduled_row])], ignore_index=True)

        # Build actual start dict for highlighting
        actual_starts = {
            row['id']: row['actual_start'] for _,
            row in table.iterrows() if row['id'] not in [
                'RA',
                'RS']}
        # Replace all nan and "nan" with empty string
        table = table.replace({np.nan: '', 'nan': ''})

        return table, actual_starts, set(df[df['critical']]['id'])

    def get_scheduled_critical_path(self, scheduled_activities):
        """
        Find the path with the longest finish time in the scheduled activities.
        Returns a list of activity IDs on the critical path.
        """
        # Build a graph from scheduled_activities using their dependencies
        import networkx as nx
        G = nx.DiGraph()
        for act_id, data in scheduled_activities.items():
            G.add_node(act_id, **data)
        # Add edges based on predecessors (if available in data)
        for act_id, data in scheduled_activities.items():
            preds = data.get('predecessors', [])
            if isinstance(preds, str):
                preds = [p.strip() for p in preds.split(',') if p.strip()]
            for pred in preds:
                if pred in G:
                    G.add_edge(pred, act_id)

        # # Debug output
        # print("DEBUG: Edges in scheduled graph:", list(G.edges()))

        # Find all paths from sources to sinks
        sources = [n for n in G.nodes if G.in_degree(n) == 0]
        sinks = [n for n in G.nodes if G.out_degree(n) == 0]
        max_path = []
        max_duration = -1
        for s in sources:
            for t in sinks:
                for path in nx.all_simple_paths(G, s, t):
                    finish = scheduled_activities[path[-1]]['scheduled_finish']
                    start = scheduled_activities[path[0]]['scheduled_start']
                    duration = finish - start
                    if duration > max_duration:
                        max_duration = duration
                        max_path = path

        # # Debug output critical path
        # print("DEBUG: Critical path found:", max_path)

        return set(max_path)

    ##### TRIAAL###

    def recalculate_with_rcps_constraints(self, G, rcps_start_times):
        """
        Recalculate network with RCPS start time constraints preserved.
        Only allows activities to start earlier if their duration was reduced.
        """
        G_new = G.copy()

        # For each node, calculate new finish time based on:
        # 1. RCPS start time (preserved)
        # 2. New (potentially crashed) duration
        for node in G_new.nodes():
            if node in rcps_start_times:
                # Preserve RCPS start time
                G_new.nodes[node]['ES'] = rcps_start_times[node]
                # Calculate new finish time with (possibly crashed) duration
                G_new.nodes[node]['EF'] = rcps_start_times[node] + \
                    G_new.nodes[node]['duration']

        # Calculate project duration
        project_duration = max([G_new.nodes[node]['EF']
                               for node in G_new.nodes()])

        # Calculate Late Start and Late Finish times
        for node in G_new.nodes():
            G_new.nodes[node]['LF'] = project_duration
            G_new.nodes[node]['LS'] = project_duration

        # Backward pass for LS/LF calculation
        for node in reversed(list(nx.topological_sort(G_new))):
            if node not in ['START', 'END']:
                duration = G_new.nodes[node]['duration']

                # Calculate LF based on successors' LS
                successors = list(G_new.successors(node))
                if successors:
                    min_succ_ls = min([G_new.nodes[succ]['LS']
                                      for succ in successors])
                    G_new.nodes[node]['LF'] = min_succ_ls
                else:
                    G_new.nodes[node]['LF'] = project_duration

                # Calculate LS
                G_new.nodes[node]['LS'] = G_new.nodes[node]['LF'] - duration

                # Calculate float
                G_new.nodes[node]['float'] = G_new.nodes[node]['LS'] - \
                    G_new.nodes[node]['ES']

        return G_new

    def crash_project_with_rcps(
            self,
            target_duration,
            resource_limit,
            priority_rule='minimum_slack',
            max_iterations=300,
            max_budget=None):
        """
        Crash the project to achieve target duration while respecting resource constraints.

        This function integrates Resource-Constrained Project Scheduling (RCPS) into the crashing process,
        ensuring that the crashing decisions respect both resource limitations and the chronological
        progression of the project. Activities that have already completed cannot be crashed.

        Args:
            target_duration (float): The desired project duration after crashing
            resource_limit (int): Maximum resource availability per time period
            priority_rule (str): Scheduling rule for resource allocation ('minimum_slack', 'shortest_duration', or 'earliest_start')
            max_iterations (int): Maximum number of crashing iterations to prevent infinite loops
            max_budget (float, optional): Maximum budget available for crashing activities

        Returns:
            tuple: (crashed_graph, total_crash_cost, crash_log)
        """
        if not self.G:
            raise ValueError("No network graph available. Run analysis first.")

        # Store original durations BEFORE any modifications
        original_durations = {
            node: self.G.nodes[node]['duration'] for node in self.G.nodes()}

        # Create a copy of the graph to modify
        crashed_G = self.G.copy()
        total_crash_cost = 0
        crash_log = []

        # Track how many times each activity has been crashed
        crash_counts = {node: 0 for node in crashed_G.nodes()}

        # Get max_crash_steps for each activity (default: unlimited)
        max_crash_steps = {}
        for node in crashed_G.nodes():
            max_crash_steps[node] = crashed_G.nodes[node].get(
                'max_crash_steps', None)

        iteration = 0

        # Initialize simulation time and completed activities tracker
        current_time = 0
        completed_activities = set()

        print(
            f"Starting RCPS-integrated crash optimization: Target = {target_duration}")

        while iteration < max_iterations:

            # Budget check before any crash
            if max_budget is not None and total_crash_cost >= max_budget:
                print(
                    f"Crash budget reached: {total_crash_cost} >= {max_budget}")
                break

            iteration += 1

            # Debug: Print current activity durations
            for node in crashed_G.nodes():
                if node not in ['START', 'END']:
                    print(f"  {node}: {crashed_G.nodes[node]['duration']}")

            # Generate RCPS schedule for current graph state
            # This creates a resource-feasible schedule considering resource
            # constraints
            current_schedule = self.generate_rcps_schedule_for_graph(
                crashed_G, resource_limit, priority_rule)
            current_duration = current_schedule['project_duration']

            # Update completed activities based on current simulation time
            for activity_id, activity_data in current_schedule['activities'].items(
            ):
                # If activity finishes before or at current simulation time,
                # mark as completed
                if activity_data['actual_finish'] <= current_time:
                    completed_activities.add(activity_id)
                    print(
                        f"DEBUG: Activity {activity_id} completed at time {
                            activity_data['actual_finish']} (current_time: {current_time})")

            # Print current state information
            print(
                f"Iteration {iteration}: RCPS duration = {current_duration}, Target = {target_duration}, Current time = {current_time}")
            print(
                f"Completed activities: {
                    sorted(
                        list(completed_activities))}")

            # Check if target is achieved
            if current_duration <= target_duration:
                print(
                    f"Target duration {target_duration} achieved! Final duration: {current_duration}")
                break

            # Find critical activities using zero float approach (same as CPM)
            crashed_G_temp = self.forward_pass(crashed_G.copy())
            crashed_G_temp = self.backward_pass(crashed_G_temp)
            crashed_G_temp = self.calculate_float(crashed_G_temp)

            # Get critical activities (activities with zero float)
            critical_activities = [node for node in crashed_G_temp.nodes(
            ) if crashed_G_temp.nodes[node]['float'] == 0 and node not in ['START', 'END']]

            print(
                f"Critical activities (zero float): {
                    ' -> '.join(critical_activities)}")

            if not critical_activities:
                print("No critical activities found. Breaking.")
                break

            # Test crash impact for each critical activity that hasn't finished
            # yet
            crash_options = []
            for activity in critical_activities:
                # Skip if activity is already completed
                if activity in completed_activities:
                    print(f"  Not crashable: {activity} (already completed)")
                    continue

                # Get current activity data
                current_dur = crashed_G.nodes[activity]['duration']
                min_dur = crashed_G.nodes[activity]['min_duration']
                crash_cost = crashed_G.nodes[activity]['crash_cost']
                max_steps = max_crash_steps.get(activity, None)
                crashed_so_far = crash_counts.get(activity, 0)

                # Get activity schedule data from RCPS
                activity_data = current_schedule['activities'].get(
                    activity, {})
                actual_start = activity_data.get('actual_start', 0)
                actual_finish = activity_data.get('actual_finish', 0)

                # Check if activity is in progress or hasn't started yet
                # Only in-progress activities or future activities can be
                # crashed
                will_finish_soon = (
                    actual_start <= current_time) and (
                    actual_finish > current_time)
                is_future = actual_start > current_time

                # Only allow if:
                # - Under max_crash_steps (or unlimited if None)
                # - Not finished
                # - Has not reached minimum duration
                # - Has a positive crash cost
                can_crash = (current_dur > min_dur and
                             crash_cost > 0 and
                             (max_steps is None or crashed_so_far < max_steps))

                if can_crash:
                    # Test the impact of crashing this activity by simulating
                    # the crash
                    temp_G = crashed_G.copy()
                    temp_G.nodes[activity]['duration'] -= 1

                    # Generate a new RCPS schedule with the crashed activity
                    temp_schedule = self.generate_rcps_schedule_for_graph(
                        temp_G, resource_limit, priority_rule)
                    temp_duration = temp_schedule['project_duration']

                    # Calculate the reduction in project duration this crash
                    # would achieve
                    duration_reduction = current_duration - temp_duration

                    # Store this crash option for evaluation
                    crash_options.append({
                        'id': activity,
                        'crash_cost': crash_cost,
                        'current_duration': current_dur,
                        'min_duration': min_dur,
                        'duration_reduction': duration_reduction,
                        'resulting_duration': temp_duration,
                        'efficiency': duration_reduction / crash_cost if crash_cost > 0 else 0,
                        'actual_start': actual_start,
                        'actual_finish': actual_finish - 1,  # Reduced by 1 due to crash
                        'is_in_progress': will_finish_soon
                    })

                    print(f"  Crashable: {activity} (dur={current_dur}, min={min_dur}, cost={crash_cost}, "
                          f"reduction={duration_reduction}, new_duration={temp_duration})")
                else:
                    print(
                        f"  Not crashable: {activity} (dur={current_dur}, min={min_dur}, already at min or max steps reached)")

            if not crash_options:
                print("No more activities can be crashed. Breaking.")
                break

            # Select activity with lowest crash cost (same logic as in
            # crash_project)
            cheapest_activity = min(
                crash_options, key=lambda x: x['crash_cost'])
            activity_id = cheapest_activity['id']

            # Add logging for clarity about selection
            if cheapest_activity['is_in_progress']:
                print(
                    f"  Selected activity {activity_id} (in progress) with lowest cost {
                        cheapest_activity['crash_cost']}")
            else:
                print(
                    f"  Selected activity {activity_id} (future) with lowest cost {
                        cheapest_activity['crash_cost']}")

            # Budget check before this specific crash
            if max_budget is not None and total_crash_cost + \
                    cheapest_activity['crash_cost'] > max_budget:
                print(
                    f"Next crash would exceed budget: {total_crash_cost} + {
                        cheapest_activity['crash_cost']} > {max_budget}")
                break

            # Crash the selected activity
            crashed_G.nodes[activity_id]['duration'] -= 1
            total_crash_cost += cheapest_activity['crash_cost']
            crash_counts[activity_id] += 1

            print(
                f"  Crashing {activity_id}: {
                    cheapest_activity['current_duration']} → {
                    crashed_G.nodes[activity_id]['duration']} (Cost: {
                    cheapest_activity['crash_cost']})")

            # Record this crash in the log
            crash_log.append({
                'iteration': iteration,
                'activity': activity_id,
                'crash_cost': cheapest_activity['crash_cost'],
                'new_duration': crashed_G.nodes[activity_id]['duration'],
                'original_duration': original_durations[activity_id],
                'project_duration_reduction': cheapest_activity['duration_reduction'],
                'resulting_project_duration': cheapest_activity['resulting_duration']
            })

            print(
                f"  New RCPS project duration: {current_duration} → {
                    cheapest_activity['resulting_duration']}")

            # CRITICAL FIX: Uniformly advance time by 1 unit
            current_time += 1
            print(f"  Advanced time to {current_time}")

        # Generate final RCPS schedule for the crashed graph
        final_schedule = self.generate_rcps_schedule_for_graph(
            crashed_G, resource_limit, priority_rule)
        final_duration = final_schedule['project_duration']

        # Update the crashed graph with final RCPS times
        # This ensures that the graph reflects the resource-feasible schedule
        for activity_id, activity_data in final_schedule['activities'].items():
            if activity_id in crashed_G.nodes:
                crashed_G.nodes[activity_id]['ES'] = activity_data['actual_start']
                crashed_G.nodes[activity_id]['EF'] = activity_data['actual_finish']

        # Calculate LS, LF, and float based on RCPS schedule
        # Set all LF to project duration initially
        for node in crashed_G.nodes():
            crashed_G.nodes[node]['LF'] = final_duration
            crashed_G.nodes[node]['LS'] = final_duration

        # Backward pass for LS/LF calculation only
        for node in reversed(list(nx.topological_sort(crashed_G))):
            if node not in ['START', 'END']:
                duration = crashed_G.nodes[node]['duration']

                # Calculate LF based on successors' LS
                successors = list(crashed_G.successors(node))
                if successors:
                    min_succ_ls = min([crashed_G.nodes[succ]['LS']
                                      for succ in successors])
                    crashed_G.nodes[node]['LF'] = min_succ_ls
                else:
                    crashed_G.nodes[node]['LF'] = final_duration

                # Calculate LS
                crashed_G.nodes[node]['LS'] = crashed_G.nodes[node]['LF'] - duration

                # Calculate float based on RCPS times
                crashed_G.nodes[node]['float'] = crashed_G.nodes[node]['LS'] - \
                    crashed_G.nodes[node]['ES']

        print(
            f"RCPS-integrated crash optimization complete. Final duration: {final_duration}, Total cost: {total_crash_cost}")

        return crashed_G, total_crash_cost, crash_log

    def crash_project(
            self,
            target_duration,
            max_iterations=300,
            max_budget=None):
        """
        Crash the project to achieve target duration with enhanced logging and proper simulation time tracking.

        This function implements a time-based project crashing approach that respects the chronological
        progression of the project. Activities that have already completed cannot be crashed.

        Args:
            target_duration (float): The desired project duration after crashing
            max_iterations (int): Maximum number of crashing iterations to prevent infinite loops
            max_budget (float, optional): Maximum budget available for crashing activities

        Returns:
            tuple: (crashed_graph, total_crash_cost, crash_log)
        """
        if not self.G:
            raise ValueError("No network graph available. Run analysis first.")

        # Store original durations BEFORE any modifications
        original_durations = {
            node: self.G.nodes[node]['duration'] for node in self.G.nodes()}

        # Create a copy of the graph to modify
        crashed_G = self.G.copy()
        total_crash_cost = 0
        crash_log = []

        # Track how many times each activity has been crashed
        crash_counts = {node: 0 for node in crashed_G.nodes()}

        # Get max_crash_steps for each activity (default: unlimited)
        max_crash_steps = {}
        for node in crashed_G.nodes():
            max_crash_steps[node] = crashed_G.nodes[node].get(
                'max_crash_steps', None)

        # Get initial project duration
        current_duration = max([crashed_G.nodes[node]['EF']
                               for node in crashed_G.nodes()])
        iteration = 0

        # Initialize simulation time - starts at 0 (beginning of project)
        current_time = 0
        # Initialize set to track completed activities
        completed_activities = set()

        print(
            f"Starting crash optimization: Initial duration = {current_duration}, Target = {target_duration}")

        while current_duration > target_duration and iteration < max_iterations:
            # Budget check before any crash
            if max_budget is not None and total_crash_cost >= max_budget:
                print(
                    f"Crash budget reached: {total_crash_cost} >= {max_budget}")
                break

            iteration += 1

            # Recalculate CPM on current graph
            crashed_G = self.forward_pass(crashed_G)
            crashed_G = self.backward_pass(crashed_G)
            crashed_G = self.calculate_float(crashed_G)

            # Find critical activities
            critical_activities = [node for node in crashed_G.nodes(
            ) if crashed_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]

            print(
                f"Iteration {iteration}: Critical path = {
                    ' -> '.join(critical_activities)}")
            print(f"Current simulation time = {current_time}")
            print(
                f"Completed activities: {
                    sorted(
                        list(completed_activities))}")

            if not critical_activities:
                print("No critical activities found. Breaking.")
                break

            # Update completed activities based on current simulation time
            for node in crashed_G.nodes():
                if node not in [
                    'START',
                        'END'] and crashed_G.nodes[node]['EF'] <= current_time:
                    completed_activities.add(node)

            # Find crashable activities on critical path that haven't finished
            # yet
            crashable_activities = []
            for activity in critical_activities:
                current_dur = crashed_G.nodes[activity]['duration']
                min_dur = crashed_G.nodes[activity]['min_duration']
                crash_cost = crashed_G.nodes[activity]['crash_cost']
                max_steps = max_crash_steps.get(activity, None)
                crashed_so_far = crash_counts.get(activity, 0)
                es = crashed_G.nodes[activity]['ES']
                ef = crashed_G.nodes[activity]['EF']

                # CRITICAL: An activity is eligible for crashing if:
                # 1. It has not yet completed (EF > current_time)
                # 2. It meets all the other crashing criteria
                not_finished = ef > current_time

                # For clearer logic, check if activity is in progress
                is_in_progress = es <= current_time and ef > current_time

                # Only allow if:
                # - Under max_crash_steps (or unlimited if None)
                # - Not finished
                # - Has not reached minimum duration
                # - Has a positive crash cost
                can_crash = (current_dur > min_dur and
                             crash_cost > 0 and
                             (max_steps is None or crashed_so_far < max_steps) and
                             not_finished)

                if can_crash:
                    crashable_activities.append({
                        'id': activity,
                        'crash_cost': crash_cost,
                        'current_duration': current_dur,
                        'min_duration': min_dur,
                        'es': es,
                        'ef': ef,
                        'is_in_progress': is_in_progress
                    })
                    print(
                        f"  Crashable: {activity} (dur={current_dur}, min={min_dur}, cost={crash_cost}, ES={es}, EF={ef})")
                elif not not_finished:
                    print(
                        f"  Not crashable: {activity} (already finished, EF={ef} <= current_time={current_time})")
                else:
                    print(
                        f"  Not crashable: {activity} (dur={current_dur}, min={min_dur}, already at min or max steps reached)")

            if not crashable_activities:
                print("No more activities can be crashed. Breaking.")
                break  # No more activities can be crashed

            # Select activity with lowest crash cost
            # Prioritize in-progress activities over future activities
            cheapest_activity = min(
                crashable_activities,
                key=lambda x: x['crash_cost'])
            activity_id = cheapest_activity['id']

            # Add logging for clarity about selection
            if cheapest_activity['is_in_progress']:
                print(
                    f"  Selected activity {activity_id} (in progress) with lowest cost {
                        cheapest_activity['crash_cost']}")
            else:
                print(
                    f"  Selected activity {activity_id} (future) with lowest cost {
                        cheapest_activity['crash_cost']}")

            activity_id = cheapest_activity['id']

            # Budget check before this crash
            if max_budget is not None and total_crash_cost + \
                    cheapest_activity['crash_cost'] > max_budget:
                print(
                    f"Next crash would exceed budget: {total_crash_cost} + {
                        cheapest_activity['crash_cost']} > {max_budget}")
                break

            # Crash the selected activity
            crashed_G.nodes[activity_id]['duration'] -= 1
            total_crash_cost += cheapest_activity['crash_cost']
            crash_counts[activity_id] += 1  # Track this crash

            print(
                f"  Crashing {activity_id}: {
                    cheapest_activity['current_duration']} → {
                    crashed_G.nodes[activity_id]['duration']} (Cost: {
                    cheapest_activity['crash_cost']})")

            crash_log.append({
                'iteration': iteration,
                'activity': activity_id,
                'crash_cost': cheapest_activity['crash_cost'],
                'new_duration': crashed_G.nodes[activity_id]['duration'],
                'original_duration': original_durations[activity_id]
            })

            # Update project duration
            crashed_G = self.forward_pass(crashed_G)
            new_duration = max([crashed_G.nodes[node]['EF']
                               for node in crashed_G.nodes()])
            print(
                f"  New project duration: {current_duration} → {new_duration}")
            current_duration = new_duration

            # CRITICAL FIX: Uniformly advance time by 1 unit
            current_time += 1
            print(f"  Advanced time to {current_time}")

            if current_duration <= target_duration:
                print(f"Target duration {target_duration} achieved!")
                break

        # Final CPM calculation
        crashed_G = self.forward_pass(crashed_G)
        crashed_G = self.backward_pass(crashed_G)
        crashed_G = self.calculate_float(crashed_G)

        print(
            f"Crash optimization complete. Final duration: {current_duration}, Total cost: {total_crash_cost}")

        return crashed_G, total_crash_cost, crash_log

    def generate_rcps_schedule_for_graph(
            self, G, resource_limit, priority_rule='minimum_slack'):
        """
        Generate RCPS schedule for a given graph state and return schedule data.

        This method should perform FULL RCPS scheduling, not just CPM calculations.

        Returns:
            dict: {
                'project_duration': int,
                'activities': dict,  # activity_id -> {actual_start, actual_finish, ...}
                'critical_activities': list
            }
        """
        # Convert graph to DataFrame format for RCPS scheduling
        activities_data = []
        for node in G.nodes():
            if node not in ['START', 'END']:
                # Get predecessors (excluding START)
                predecessors = [
                    pred for pred in G.predecessors(node) if pred != 'START']
                predecessors_str = ','.join(
                    predecessors) if predecessors else ''

                # Use current durations from the graph (which may be crashed)
                current_duration = G.nodes[node]['duration']

                activities_data.append({
                    'id': node,
                    # Use current (possibly crashed) duration
                    'duration': current_duration,
                    'resource': G.nodes[node].get('resource_demand', 0),
                    'early_start': 0,  # Reset for RCPS calculation
                    'late_finish': 0,  # Reset for RCPS calculation
                    'float': 0,  # Reset for RCPS calculation
                    'predecessors': predecessors_str
                })

        df_gantt = pd.DataFrame(activities_data)

        # CRITICAL: Run FULL CPM analysis first (to get ES, LF, float for RCPS)
        temp_G = self.build_network_for_rcps(activities_data)
        temp_G = self.forward_pass(temp_G)
        temp_G = self.backward_pass(temp_G)
        temp_G = self.calculate_float(temp_G)

        # Update DataFrame with CPM results for RCPS input
        for idx, row in df_gantt.iterrows():
            activity_id = row['id']
            if activity_id in temp_G.nodes:
                df_gantt.at[idx,
                            'early_start'] = temp_G.nodes[activity_id]['ES']
                df_gantt.at[idx,
                            'late_finish'] = temp_G.nodes[activity_id]['LF']
                df_gantt.at[idx, 'float'] = temp_G.nodes[activity_id]['float']

        # Run RCPS scheduling with proper inputs
        rcps_table, actual_starts, critical_ids = self.rcps_heuristic_schedule_table(
            df_gantt, resource_limit, priority_rule)

        # Extract schedule data
        activities = {}
        project_duration = 0

        for idx, row in rcps_table.iterrows():
            if row['id'] not in ['RA', 'RS']:
                activity_id = row['id']
                actual_start = int(
                    row['actual_start']) if not pd.isna(
                    row['actual_start']) else 0
                duration = int(row['duration'])
                actual_finish = actual_start + duration

                activities[activity_id] = {
                    'actual_start': actual_start,
                    'actual_finish': actual_finish,
                    'duration': duration
                }

                project_duration = max(project_duration, actual_finish)

        # Use critical activities from zero float calculation (same as CPM)
        critical_activities = [node for node in temp_G.nodes(
        ) if temp_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]

        return {
            'project_duration': project_duration,
            'activities': activities,
            'critical_activities': critical_activities
        }

    def build_network_for_rcps(self, activities):
        """
        Build a directed graph network from activity data.
        This is a simplified version for internal use during RCPS scheduling.
        """
        # Create directed graph
        G = nx.DiGraph()

        # Add all activities as nodes with duration attribute
        for activity in activities:
            predecessors = activity.get('predecessors', [])
            if isinstance(predecessors, str):
                predecessors = [p.strip()
                                for p in predecessors.split(',') if p.strip()]

            G.add_node(
                activity['id'], duration=activity['duration'], min_duration=activity.get(
                    'min_duration', activity['duration']), crash_cost=activity.get(
                    'crash_cost', 0), activity=activity.get(
                    'activity', ''), resource_demand=activity.get(
                    'resource_demand', 0), normal_cost=activity.get(
                        'normal_cost', 0))

        # Add edges based on predecessor relationships
        for activity in activities:
            predecessors = activity.get('predecessors', [])
            if isinstance(predecessors, str):
                predecessors = [p.strip()
                                for p in predecessors.split(',') if p.strip()]

            for predecessor in predecessors:
                if predecessor and predecessor in G:
                    G.add_edge(predecessor, activity['id'])

        # Add START node and connect it to nodes with no predecessors
        start_nodes = [node for node in G.nodes() if G.in_degree(node) == 0]
        if start_nodes:
            G.add_node('START', duration=0, activity='Start')
            for node in start_nodes:
                G.add_edge('START', node)

        # Add END node and connect nodes with no successors to it
        end_nodes = [node for node in G.nodes() if G.out_degree(node)
                     == 0 and node != 'START']
        if end_nodes:
            G.add_node('END', duration=0, activity='End')
            for node in end_nodes:
                G.add_edge(node, 'END')

        return G

    #################
    def debug_crash_process(self, crashed_G, crash_log, target_duration):
        """
        Generate a detailed debug report of the crashing process execution.
        Shows step-by-step decision making and reasoning.

        Args:
            crashed_G: Final crashed graph
            crash_log: Log of all crashing operations
            target_duration: The target project duration
        """
        debug_text = "DETAILED CRASHING PROCESS EXECUTION\n"
        debug_text += "=" * 60 + "\n\n"

        # Get original graph for initial state
        original_G = self.G.copy()
        current_G = original_G.copy()

        # Initial state
        initial_duration = max([original_G.nodes[node]['EF']
                               for node in original_G.nodes()])
        debug_text += f"INITIAL STATE (Time Unit 0):\n"
        debug_text += f"  Project Duration: {initial_duration}\n"
        debug_text += f"  Target Duration: {target_duration}\n"

        # Find initial critical path
        critical_activities = [node for node in original_G.nodes(
        ) if original_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]
        debug_text += f"  Critical Path: {' -> '.join(critical_activities)}\n"
        debug_text += f"  Activities on Critical Path:\n"

        # Show all critical activities and their crashing potential
        for activity in critical_activities:
            current_dur = original_G.nodes[activity]['duration']
            min_dur = original_G.nodes[activity]['min_duration']
            crash_cost = original_G.nodes[activity]['crash_cost']
            crash_potential = current_dur - min_dur

            debug_text += f"    - {activity}: Duration={current_dur}, Min={min_dur}, "
            debug_text += f"Cost={crash_cost}, Potential={crash_potential}\n"

        debug_text += "\n" + "-" * 60 + "\n\n"

        # Simulate each step
        current_time = 0
        completed_activities = set()

        for i, entry in enumerate(crash_log):
            step_num = entry['iteration']
            activity_id = entry['activity']
            crash_cost = entry['crash_cost']
            new_duration = entry['new_duration']

            # Update current graph to simulate this step
            current_G.nodes[activity_id]['duration'] = new_duration
            current_G = self.forward_pass(current_G)
            current_G = self.backward_pass(current_G)
            current_G = self.calculate_float(current_G)

            # Get project duration after this crash
            new_project_duration = max(
                [current_G.nodes[node]['EF'] for node in current_G.nodes()])

            # Update simulation time to match the time in the actual algorithm
            # In a real implementation, this would come from the actual simulation time
            # Here we're approximating for the debug output
            if i < len(crash_log) - 1:
                next_entry = crash_log[i + 1]
                # Simulate time advancement based on activity finish events
                for node in current_G.nodes():
                    if node not in ['START',
                                    'END'] and node not in completed_activities:
                        ef = current_G.nodes[node]['EF']
                        if ef > current_time and ef <= current_G.nodes[next_entry['activity']]['ES']:
                            current_time = ef
                            completed_activities.add(node)

            # Get current critical path
            critical_activities = [node for node in current_G.nodes(
            ) if current_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]

            # Get crashable activities at this point
            crashable_activities = []
            for act in critical_activities:
                if (act not in completed_activities and
                    current_G.nodes[act]['duration'] > current_G.nodes[act]['min_duration'] and
                        current_G.nodes[act]['crash_cost'] > 0):

                    # Determine if in progress or future
                    es = current_G.nodes[act]['ES']
                    ef = current_G.nodes[act]['EF']
                    is_in_progress = es <= current_time and ef > current_time

                    crashable_activities.append({
                        'id': act,
                        'crash_cost': current_G.nodes[act]['crash_cost'],
                        'duration': current_G.nodes[act]['duration'],
                        'min_duration': current_G.nodes[act]['min_duration'],
                        'is_in_progress': is_in_progress
                    })

            # Sort by priority (in-progress first, then by cost)
            in_progress = [
                a for a in crashable_activities if a['is_in_progress']]
            future = [
                a for a in crashable_activities if not a['is_in_progress']]

            in_progress.sort(key=lambda x: x['crash_cost'])
            future.sort(key=lambda x: x['crash_cost'])

            # Debug output for this step
            debug_text += f"STEP {step_num} (Time Unit {current_time}):\n"
            debug_text += f"  Current Project Duration: {new_project_duration}\n"
            debug_text += f"  Critical Path: {
                ' -> '.join(critical_activities)}\n"

            debug_text += f"  Completed Activities: {
                sorted(
                    list(completed_activities))}\n"
            debug_text += f"  Crashable Activities on Critical Path:\n"

            # In-progress activities
            if in_progress:
                debug_text += f"    In-Progress Activities:\n"
                for act in in_progress:
                    debug_text += f"      - {
                        act['id']}: Cost={
                        act['crash_cost']}, "
                    debug_text += f"Duration={
                        act['duration']}, Min={
                        act['min_duration']}\n"

            # Future activities
            if future:
                debug_text += f"    Future Activities:\n"
                for act in future:
                    debug_text += f"      - {
                        act['id']}: Cost={
                        act['crash_cost']}, "
                    debug_text += f"Duration={
                        act['duration']}, Min={
                        act['min_duration']}\n"

            # Decision reasoning
            debug_text += f"\n  DECISION: Crash activity {activity_id}\n"
            debug_text += f"  REASONING:\n"

            if activity_id in [a['id'] for a in in_progress]:
                debug_text += f"    - Activity {activity_id} is in progress\n"
                debug_text += f"    - It has the lowest crash cost ({crash_cost}) among in-progress activities\n"
            else:
                debug_text += f"    - No in-progress activities on critical path\n"
                debug_text += f"    - Activity {activity_id} has the lowest crash cost ({crash_cost}) among future activities\n"

            debug_text += f"    - New duration: {new_duration}\n"

            duration_change = new_project_duration - initial_duration
            debug_text += f"    - Project duration changed from {initial_duration} to {new_project_duration} "
            debug_text += f"(reduction of {-duration_change if duration_change < 0 else 0})\n"

            debug_text += "\n" + "-" * 60 + "\n\n"

        # Final state
        final_duration = max([crashed_G.nodes[node]['EF']
                             for node in crashed_G.nodes()])
        debug_text += f"FINAL STATE:\n"
        debug_text += f"  Project Duration: {final_duration} (Target: {target_duration})\n"
        debug_text += f"  Total Reduction: {
            initial_duration - final_duration}\n"
        debug_text += f"  Total Crash Cost: {
            sum(
                entry['crash_cost'] for entry in crash_log)}\n"

        # Was target achieved?
        if final_duration <= target_duration:
            debug_text += f"  TARGET ACHIEVED \n"
        else:
            debug_text += f"  TARGET NOT ACHIEVED\n"
            debug_text += f"  Reason: {
                self._get_termination_reason(
                    crashed_G, crash_log, target_duration)}\n"

        return debug_text

    def _get_termination_reason(self, crashed_G, crash_log, target_duration):
        """Determine why crashing stopped before reaching target"""
        # Find all critical activities
        critical_activities = [node for node in crashed_G.nodes(
        ) if crashed_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]

        # Check if any critical activity can still be crashed
        can_crash_more = False
        for act in critical_activities:
            if (crashed_G.nodes[act]['duration'] > crashed_G.nodes[act]
                [ 'min_duration'] and crashed_G.nodes[act]['crash_cost'] > 0):
                can_crash_more = True
                break

        if not can_crash_more:
            return "All critical activities at minimum duration or have zero crash cost"

        # If we have a crash log, check the last entry
        if crash_log:
            last_entry = crash_log[-1]
            if 'project_duration_reduction' in last_entry and last_entry[
                    'project_duration_reduction'] == 0:
                return "No further reduction in project duration possible due to parallel critical paths"

        return "Unknown reason - possibly reached max iterations or budget constraint"

    def debug_rcps_crash_process(
            self,
            crashed_G,
            crash_log,
            target_duration,
            resource_limit,
            priority_rule):
        """
        Generate a detailed debug report of the RCPS crashing process execution.
        Shows step-by-step decision making and reasoning including resource constraints.

        Args:
            crashed_G: Final crashed graph
            crash_log: Log of all crashing operations
            target_duration: The target project duration
            resource_limit: Resource limit used in RCPS
            priority_rule: Priority rule used in resource scheduling
        """
        debug_text = "DETAILED RCPS CRASHING PROCESS EXECUTION\n"
        debug_text += "=" * 70 + "\n\n"

        # Get original graph for initial state
        original_G = self.G.copy()
        current_G = original_G.copy()

        # Generate initial RCPS schedule
        initial_schedule = self.generate_rcps_schedule_for_graph(
            original_G, resource_limit, priority_rule)
        initial_duration = initial_schedule['project_duration']

        debug_text += f"Starting crash optimization: Initial duration = {initial_duration}, Target = {target_duration}\n"

        # Track crash counts
        crash_counts = {node: 0 for node in crashed_G.nodes()}
        for entry in crash_log:
            if 'activity' in entry:
                activity_id = entry['activity']
                if activity_id in crash_counts:
                    crash_counts[activity_id] += 1

        # Simulate each step
        current_time = 0
        completed_activities = set()

        for i, entry in enumerate(crash_log):
            step_num = entry['iteration']
            activity_id = entry['activity']
            crash_cost = entry['crash_cost']
            new_duration = entry['new_duration']
            original_duration = entry.get('original_duration', 0)

            # Update current graph to simulate this step
            current_G.nodes[activity_id]['duration'] = new_duration

            # Generate RCPS schedule for current state
            current_schedule = self.generate_rcps_schedule_for_graph(
                current_G, resource_limit, priority_rule)
            current_duration = current_schedule['project_duration']

            # Update completed activities based on current time
            for act_id, act_data in current_schedule['activities'].items():
                if act_data['actual_finish'] <= current_time:
                    completed_activities.add(act_id)

            # Get current critical path from RCPS
            critical_activities = current_schedule['critical_activities']

            # Debug output for this step
            debug_text += f"Iteration {step_num}: Critical path = {
                ' -> '.join(critical_activities)}\n"
            debug_text += f"Current simulation time = {current_time}\n"
            debug_text += f"Completed activities: {
                sorted(
                    list(completed_activities))}\n"

            # Get max_crash_steps for each activity (default: unlimited)
            max_crash_steps = {}
            for node in crashed_G.nodes():
                max_crash_steps[node] = crashed_G.nodes[node].get(
                    'max_crash_steps', None)

            # Analyze and show crash options
            for activity in critical_activities:
                if activity not in ['START', 'END']:
                    # Skip if already completed
                    if activity in completed_activities:
                        debug_text += f"  Not crashable: {activity} (already finished, "
                        debug_text += f"EF={
                            current_schedule['activities'][activity]['actual_finish']} <= current_time={current_time})\n"
                        continue

                    # Get activity data
                    current_dur = current_G.nodes[activity]['duration']
                    min_dur = current_G.nodes[activity]['min_duration']
                    act_crash_cost = current_G.nodes[activity]['crash_cost']
                    max_steps = max_crash_steps.get(activity, None)
                    crashed_so_far = crash_counts.get(activity, 0)

                    # Get RCPS timing
                    act_data = current_schedule['activities'].get(activity, {})
                    actual_start = act_data.get('actual_start', 0)
                    actual_finish = act_data.get('actual_finish', 0)

                    # Check if in progress or future
                    is_in_progress = actual_start <= current_time and actual_finish > current_time

                    # Determine if it can be crashed
                    can_crash = (
                        current_dur > min_dur and act_crash_cost > 0 and (
                            max_steps is None or crashed_so_far < max_steps))

                    if can_crash:
                        debug_text += f"  Crashable: {activity} (dur={current_dur}, min={min_dur}, "
                        debug_text += f"cost={act_crash_cost}, ES={actual_start}, EF={actual_finish})\n"
                    else:
                        reason = ""
                        if current_dur <= min_dur:
                            reason = "already at min or max steps reached"
                        elif act_crash_cost <= 0:
                            reason = "zero crash cost"
                        elif max_steps is not None and crashed_so_far >= max_steps:
                            reason = "reached maximum crash steps"

                        debug_text += f"  Not crashable: {activity} (dur={current_dur}, min={min_dur}, {reason})\n"

            # Record selection reasoning
            if is_in_progress:
                debug_text += f"  Selected activity {activity_id} (in progress) with lowest cost {crash_cost}\n"
            else:
                debug_text += f"  Selected activity {activity_id} (future) with lowest cost {crash_cost}\n"

            # Get original duration from entry or from the graph before the
            # current iteration
            orig_duration = entry.get(
                'original_duration',
                current_G.nodes[activity_id]['duration'] + 1)
            debug_text += f"  Crashing {activity_id}: {orig_duration} -> {new_duration} (Cost: {crash_cost})\n"

            # Get resulting duration after crashing
            resulting_duration = entry.get(
                'resulting_project_duration', current_duration)
            debug_text += f"  New project duration: {current_duration} -> {resulting_duration}\n"

            # Advance time consistently by 1 unit per iteration
            current_time += 1
            debug_text += f"  Advanced time to {current_time}\n"

        # Final state
        final_schedule = self.generate_rcps_schedule_for_graph(
            crashed_G, resource_limit, priority_rule)
        final_duration = final_schedule['project_duration']

        # Check if no more activities can be crashed
        if len(crash_log) > 0:
            debug_text += "No more activities can be crashed. Breaking.\n"

        debug_text += f"Crash optimization complete. Final duration: {final_duration}, Total cost: {
            sum(
                entry['crash_cost'] for entry in crash_log)}\n"

        return debug_text

    def _calculate_resource_usage(self, schedule, G):
        """Calculate resource usage at each time period from RCPS schedule"""
        resource_usage = {}

        # Initialize time periods
        max_time = 0
        for act_id, act_data in schedule['activities'].items():
            finish_time = act_data.get('actual_finish', 0)
            if finish_time > max_time:
                max_time = finish_time

        for t in range(1, max_time + 1):
            resource_usage[t] = 0

        # Calculate resource usage for each time period
        for act_id, act_data in schedule['activities'].items():
            if act_id in G.nodes():
                start = act_data.get('actual_start', 0)
                finish = act_data.get('actual_finish', 0)
                resource = G.nodes[act_id].get('resource_demand', 0)

                for t in range(start + 1, finish + 1):
                    if t in resource_usage:
                        resource_usage[t] += resource

        return resource_usage

    def _get_rcps_termination_reason(
            self,
            crashed_G,
            crash_log,
            target_duration,
            resource_limit,
            priority_rule):
        """Determine why RCPS crashing stopped before reaching target"""
        # Generate final RCPS schedule
        final_schedule = self.generate_rcps_schedule_for_graph(
            crashed_G, resource_limit, priority_rule)
        critical_activities = final_schedule['critical_activities']

        # Check if any critical activity can still be crashed
        can_crash_more = False
        for act in critical_activities:
            if (crashed_G.nodes[act]['duration'] > crashed_G.nodes[act]
                [ 'min_duration'] and crashed_G.nodes[act]['crash_cost'] > 0):
                can_crash_more = True
                break

        if not can_crash_more:
            return "All critical activities at minimum duration or have zero crash cost"

        # Check for resource bottlenecks
        resource_usage = self._calculate_resource_usage(
            final_schedule, crashed_G)
        resource_bottlenecks = []
        for t, usage in resource_usage.items():
            if usage == resource_limit:
                resource_bottlenecks.append(t)

        if resource_bottlenecks:
            return f"Resource bottlenecks at time periods: {resource_bottlenecks}"

        # If we have a crash log, check the last entry
        if crash_log:
            last_entry = crash_log[-1]
            if 'project_duration_reduction' in last_entry and last_entry[
                    'project_duration_reduction'] == 0:
                return "No further reduction in project duration possible with RCPS constraints"

        return "Unknown reason - possibly reached max iterations or budget constraint"


class CPMDesktopApp:
    """Main desktop application class supporting both CPM and PERT analysis"""

    def __init__(self, root):
        self.root = root
        self.root.title("CPM and PERT Analysis Tool")
        self.root.geometry("1200x800")

        # Initialize analyzers
        self.cpm_analyzer = CPMAnalyzer()
        self.pert_analyzer = PERTAnalyzer()

        # Analysis mode: 'deterministic' or 'probabilistic'
        self.analysis_mode = None
        self.current_analyzer = None

        # Create GUI
        self.create_widgets()

        # Initialize with sample data
        self.load_sample_data()

    @property
    def analyzer(self):
        """Backward compatibility property for self.current_analyzer"""
        return self.current_analyzer

    def create_widgets(self):
        """Create the main GUI widgets"""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Existing tabs
        self.create_input_tab()
        self.create_results_tab()
        self.create_network_tab()
        self.create_critical_path_tab()
        self.create_gantt_tab()
        self.create_probability_analysis_tab()  # NEW: Add probability analysis tab
        self.create_rcps_tab()
        self.create_crashing_tab()
        self.create_rcps_crashing_tab()

    def create_input_tab(self):
        """Create the input tab for activity data"""
        input_frame = ttk.Frame(self.notebook)
        self.notebook.add(input_frame, text="Input Activities")

        # Buttons frame
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # Data loading buttons
        ttk.Button(
            button_frame,
            text="Load CPM Data",
            command=self.load_csv_auto_detect).pack(
            side=tk.LEFT,
            padx=(
                0,
                10))
        ttk.Button(
            button_frame,
            text="Load Deterministic Data",
            command=self.load_deterministic_csv).pack(
            side=tk.LEFT,
            padx=(
                0,
                10))
        ttk.Button(
            button_frame,
            text="Load Probabilistic Data",
            command=self.load_probabilistic_csv).pack(
            side=tk.LEFT,
            padx=(
                0,
                10))

        # Row manipulation buttons
        self.add_row_btn = ttk.Button(
            button_frame, text="Add Row", command=self.add_row)
        self.add_row_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.delete_row_btn = ttk.Button(
            button_frame, text="Delete Row", command=self.delete_row)
        self.delete_row_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Clear All",
            command=self.clear_all).pack(
            side=tk.LEFT,
            padx=(
                0,
                10))

        # Sample CSV download buttons
        ttk.Button(
            button_frame,
            text="Download Sample Deterministic CSV",
            command=self.download_sample_deterministic_csv).pack(
            side=tk.LEFT,
            padx=(
                0,
                10))
        ttk.Button(
            button_frame,
            text="Download Sample Probabilistic CSV",
            command=self.download_sample_probabilistic_csv).pack(
            side=tk.LEFT,
            padx=(
                0,
                10))

        # Analysis button
        ttk.Button(
            button_frame,
            text="Analyze",
            command=self.analyze_project).pack(
            side=tk.RIGHT)

        # Mode indicator label
        self.mode_label = ttk.Label(
            input_frame, text="Mode: None", font=(
                "Arial", 10, "bold"))
        self.mode_label.pack(anchor="w", pady=(0, 5))

        # Create treeview for activity input (will be dynamically configured)
        self.tree_frame = ttk.Frame(input_frame)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        self.setup_deterministic_tree()  # Start with deterministic layout

    def create_results_tab(self):
        """Create the results tab for displaying analysis results"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="Analysis Results")

        # Add button frame for Save CSV button
        button_frame = ttk.Frame(results_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(
            button_frame,
            text="Save CSV",
            command=self.save_results_csv).pack(
            side=tk.LEFT)

        # Create text widget for results
        self.results_text = scrolledtext.ScrolledText(
            results_frame, font=("Courier", 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def create_network_tab(self):
        """Create the network diagram tab"""
        network_frame = ttk.Frame(self.notebook)
        self.notebook.add(network_frame, text="Network Diagram")

        # Create matplotlib figure
        self.fig_network = plt.Figure(figsize=(12, 8))
        self.canvas_network = FigureCanvasTkAgg(
            self.fig_network, network_frame)
        self.canvas_network.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_critical_path_tab(self):
        """Create the critical path analysis tab"""
        critical_path_frame = ttk.Frame(self.notebook)
        self.notebook.add(critical_path_frame, text="Critical Path Analysis")

        # Create matplotlib figure for critical path visualization
        self.fig_critical_path = plt.Figure(figsize=(18, 12))
        self.canvas_critical_path = FigureCanvasTkAgg(
            self.fig_critical_path, critical_path_frame)
        self.canvas_critical_path.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_gantt_tab(self):
        """Create the Gantt chart tab"""
        gantt_frame = ttk.Frame(self.notebook)
        self.notebook.add(gantt_frame, text="Gantt Chart")

        # Create matplotlib figure
        self.fig_gantt = plt.Figure(figsize=(18, 12))
        self.canvas_gantt = FigureCanvasTkAgg(self.fig_gantt, gantt_frame)
        self.canvas_gantt.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_probability_analysis_tab(self):
        """Create the probability analysis tab for PERT"""
        prob_frame = ttk.Frame(self.notebook)
        self.notebook.add(prob_frame, text="Probability Analysis")

        # Create main container with scrollable frame
        canvas = tk.Canvas(prob_frame)
        scrollbar = ttk.Scrollbar(
            prob_frame,
            orient="vertical",
            command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Title and status
        title_frame = ttk.Frame(scrollable_frame)
        title_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(
            title_frame,
            text="PERT Probability Analysis",
            font=(
                "Arial",
                14,
                "bold")).pack(
            side=tk.LEFT)
        self.prob_status_label = ttk.Label(
            title_frame, text="Status: Disabled (Load probabilistic data first)", font=(
                "Arial", 10), foreground="red")
        self.prob_status_label.pack(side=tk.RIGHT)

        # Project statistics frame
        stats_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Project Statistics",
            padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stats_text = tk.Text(
            stats_frame,
            height=8,
            state=tk.DISABLED,
            wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)

        # Analysis controls frame
        controls_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Probability Calculations",
            padding=10)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)

        # Completion probability calculation
        comp_frame = ttk.Frame(controls_frame)
        comp_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            comp_frame,
            text="1. Project Completion Probability:",
            font=(
                "Arial",
                11,
                "bold")).pack(
            anchor="w")

        comp_input_frame = ttk.Frame(comp_frame)
        comp_input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(comp_input_frame, text="Target Duration:").pack(side=tk.LEFT)
        self.prob_target_duration_var = tk.StringVar()
        self.target_duration_entry = ttk.Entry(
            comp_input_frame, textvariable=self.prob_target_duration_var, width=10)
        self.target_duration_entry.pack(side=tk.LEFT, padx=(5, 10))

        self.calc_prob_btn = ttk.Button(
            comp_input_frame,
            text="Calculate Probability",
            command=self.calculate_completion_probability,
            state=tk.DISABLED)
        self.calc_prob_btn.pack(side=tk.LEFT, padx=5)

        self.prob_result_label = ttk.Label(
            comp_input_frame, text="", font=(
                "Arial", 10, "bold"))
        self.prob_result_label.pack(side=tk.LEFT, padx=(10, 0))

        # Duration for probability calculation
        dur_frame = ttk.Frame(controls_frame)
        dur_frame.pack(fill=tk.X, pady=5)

        ttk.Label(
            dur_frame,
            text="2. Required Duration for Given Probability:",
            font=(
                "Arial",
                11,
                "bold")).pack(
            anchor="w")

        dur_input_frame = ttk.Frame(dur_frame)
        dur_input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dur_input_frame,
                  text="Target Probability (0-1):").pack(side=tk.LEFT)
        self.target_probability_var = tk.StringVar()
        self.target_probability_entry = ttk.Entry(
            dur_input_frame, textvariable=self.target_probability_var, width=10)
        self.target_probability_entry.pack(side=tk.LEFT, padx=(5, 10))

        self.calc_duration_btn = ttk.Button(
            dur_input_frame,
            text="Calculate Duration",
            command=self.calculate_required_duration,
            state=tk.DISABLED)
        self.calc_duration_btn.pack(side=tk.LEFT, padx=5)

        self.duration_result_label = ttk.Label(
            dur_input_frame, text="", font=(
                "Arial", 10, "bold"))
        self.duration_result_label.pack(side=tk.LEFT, padx=(10, 0))

        # Visualization frame
        viz_frame = ttk.LabelFrame(
            scrollable_frame,
            text="Normal Distribution Visualization",
            padding=10)
        viz_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.fig_probability = plt.Figure(figsize=(12, 6))
        self.canvas_probability = FigureCanvasTkAgg(
            self.fig_probability, viz_frame)
        self.canvas_probability.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Initially disable the tab
        self.probability_tab_enabled = False

    def setup_deterministic_tree(self):
        """Setup tree view for deterministic (CPM) data"""
        # Clear existing tree if any
        for widget in self.tree_frame.winfo_children():
            widget.destroy()

        # Create treeview for deterministic input
        columns = (
            "ID",
            "Activity Name",
            "Duration",
            "Predecessors",
            "Min Duration",
            "Crash Cost",
            "Resource Demand",
            "Normal Cost")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            height=15)

        # Define column headings and widths
        column_widths = {
            "ID": 80,
            "Activity Name": 150,
            "Duration": 80,
            "Min Duration": 90,
            "Crash Cost": 90,
            "Predecessors": 120,
            "Resource Demand": 120,
            "Normal Cost": 90
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(
            self.tree_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(
            self.tree_frame,
            orient=tk.HORIZONTAL,
            command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Enable editing for deterministic mode
        self.tree.bind("<Double-1>", self.edit_item)

        # Enable row manipulation buttons
        self.add_row_btn.config(state=tk.NORMAL)
        self.delete_row_btn.config(state=tk.NORMAL)

    # def setup_probabilistic_tree(self):
    #     """Setup tree view for probabilistic (PERT) data"""
    #     # Clear existing tree if any
    #     for widget in self.tree_frame.winfo_children():
    #         widget.destroy()

    #     # Create treeview for probabilistic input
    #     columns = ("ID", "Predecessors", "Optimistic", "Most Likely", "Pessimistic", "Expected Time", "Variance")
    #     self.tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=15)

    #     # Define column headings and widths
    #     column_widths = {
    #         "ID": 80,
    #         "Predecessors": 120,
    #         "Optimistic": 90,
    #         "Most Likely": 90,
    #         "Pessimistic": 90,
    #         "Expected Time": 100,
    #         "Variance": 80
    #     }

    #     for col in columns:
    #         self.tree.heading(col, text=col)
    #         self.tree.column(col, width=column_widths.get(col, 100))

    #     # Add scrollbars
    #     v_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
    #     h_scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
    #     self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    #     # Pack treeview and scrollbars
    #     self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    #     v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    #     h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    #     # Enable editing for probabilistic mode (allow editing like deterministic)
    #     self.tree.bind("<Double-1>", self.edit_item)

    #     # Enable row manipulation buttons
    #     self.add_row_btn.config(state=tk.NORMAL)
    #     self.delete_row_btn.config(state=tk.NORMAL)

    def setup_probabilistic_tree(self):
        """Setup tree view for probabilistic (PERT) data"""
        # Clear existing tree if any
        for widget in self.tree_frame.winfo_children():
            widget.destroy()

        # Create treeview for probabilistic input - UPDATED with all fields
        columns = (
            "ID",
            "Predecessors",
            "Optimistic",
            "Most Likely",
            "Pessimistic",
            "Expected Time",
            "Variance",
            "Min Duration",
            "Crash Cost",
            "Resource Demand",
            "Normal Cost")
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=columns,
            show="headings",
            height=15)

        # Define column headings and widths
        column_widths = {
            "ID": 60,
            "Predecessors": 100,
            "Optimistic": 80,
            "Most Likely": 80,
            "Pessimistic": 80,
            "Expected Time": 90,
            "Variance": 70,
            "Min Duration": 80,
            "Crash Cost": 80,
            "Resource Demand": 100,
            "Normal Cost": 80
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 80))

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(
            self.tree_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(
            self.tree_frame,
            orient=tk.HORIZONTAL,
            command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set)

        # Pack treeview and scrollbars
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Enable editing for probabilistic mode (allow editing like
        # deterministic)
        self.tree.bind("<Double-1>", self.edit_item)

        # Enable row manipulation buttons
        self.add_row_btn.config(state=tk.NORMAL)
        self.delete_row_btn.config(state=tk.NORMAL)

    def load_sample_data(self):
        """Load sample deterministic project data"""
        # Set deterministic mode and setup tree
        self.analysis_mode = 'deterministic'
        self.current_analyzer = self.cpm_analyzer
        self.setup_deterministic_tree()
        self.mode_label.config(text="Mode: CPM", foreground="blue")

        sample_data = [
            ("A", "Design Phase", "5", "", "1", "300", "2", "100"),
            ("B", "Requirements Analysis", "3", "", "2", "500", "1", "150"),
            ("C", "Architecture Design", "7", "A, B", "5", "600", "3", "200"),
            ("D", "Database Design", "5", "C", "4", "400", "1", "120"),
            ("E", "Frontend Development", "6", "C", "3", "300", "4", "180"),
            ("F", "Backend Development", "8", "C", "5", "200", "5", "250"),
            ("G", "Testing", "3", "D", "3", "800", "2", "90"),
            ("H", "Deployment", "4", "E, F", "2", "1000", "1", "110"),
            ("I", "Documentation", "3", "G, H", "2", "250", "2", "80"),
            ("J", "User Training", "4", "I", "2", "250", "1", "100"),
            ("K", "Post-Deployment Review", "2", "J", "1", "500", "1", "75"),
        ]

        for item in sample_data:
            self.tree.insert("", tk.END, values=item)

    def auto_detect_mode(self, csv_headers):
        """
        Automatically detect analysis mode based on CSV column headers

        Args:
            csv_headers (list): List of column headers from CSV

        Returns:
            str: 'deterministic' for CPM mode, 'probabilistic' for PERT mode
        """
        # Convert headers to lowercase for case-insensitive comparison
        headers_lower = [header.lower().strip() for header in csv_headers]

        # Check for PERT-specific columns (optimistic, pessimistic,
        # most_likely)
        pert_indicators = ['optimistic', 'pessimistic', 'most_likely']
        has_pert_columns = any(
            indicator in headers_lower for indicator in pert_indicators)

        # Check for CPM-specific column (duration)
        has_duration = 'duration' in headers_lower

        # Decision logic
        if has_pert_columns:
            return 'probabilistic'
        elif has_duration:
            return 'deterministic'
        else:
            # Default to deterministic if ambiguous
            return 'deterministic'

    def load_csv_auto_detect(self):
        """Load CSV with automatic mode detection based on column headers"""
        file_path = filedialog.askopenfilename(
            title="Select CSV file (Auto-detect mode)",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Read CSV headers to detect mode
                with open(file_path, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    headers = reader.fieldnames

                    if not headers:
                        messagebox.showerror(
                            "Error", "CSV file appears to be empty or invalid.")
                        return

                    # Auto-detect mode based on headers
                    detected_mode = self.auto_detect_mode(headers)

                    # Clear existing data but don't reset mode yet
                    self.clear_all(reset_mode=False)

                    if detected_mode == 'probabilistic':
                        # Set PERT mode
                        self.analysis_mode = 'probabilistic'
                        self.current_analyzer = self.pert_analyzer
                        self.setup_probabilistic_tree()
                        self.mode_label.config(
                            text="Mode: PERT (Auto-detected)", foreground="green")

                        # Load PERT data
                        activities_data = []
                        file.seek(0)  # Reset file pointer
                        reader = csv.DictReader(file)
                        for row in reader:
                            pert_data = {
                                'id': row['id'],
                                'predecessors': row.get('predecessors', '').strip(),
                                'optimistic': int(float(row['optimistic'])),
                                'most_likely': int(float(row['most_likely'])),
                                'pessimistic': int(float(row['pessimistic'])),
                                'min_duration': self._safe_float_to_int(row.get('min_duration', 1)),
                                'crash_cost': self._safe_float_to_int(row.get('crash_cost', 0)),
                                'resource_demand': self._safe_float_to_int(row.get('resource_demand', 0)),
                                'normal_cost': self._safe_float_to_int(row.get('normal_cost', 0))
                            }
                            activities_data.append(pert_data)

                        # Process through PERT analyzer
                        processed_activities = self.pert_analyzer.load_activities_from_pert_data(
                            activities_data)

                        # Display in tree
                        for activity in processed_activities:
                            self.tree.insert(
                                "", tk.END, values=(
                                    activity['id'], ', '.join(
                                        activity['predecessors']) if activity['predecessors'] else '', str(
                                        activity['optimistic']), str(
                                        activity['most_likely']), str(
                                        activity['pessimistic']), str(
                                        activity['expected_time_ceil']), f"{
                                        activity['variance']:.3f}", str(
                                        activity['min_duration']), str(
                                        activity['crash_cost']), str(
                                            activity['resource_demand']), str(
                                                activity['normal_cost'])))

                        # Enable probability analysis
                        self.enable_probability_analysis()

                    else:  # deterministic mode
                        # Set CPM mode
                        self.analysis_mode = 'deterministic'
                        self.current_analyzer = self.cpm_analyzer
                        self.setup_deterministic_tree()
                        self.mode_label.config(
                            text="Mode: CPM (Auto-detected)", foreground="blue")

                        # Load CPM data
                        file.seek(0)  # Reset file pointer
                        reader = csv.DictReader(file)
                        for row in reader:
                            activity_name = row.get('activity', '').strip()
                            predecessors = row.get('predecessors', '').strip()
                            min_duration = row.get('min_duration', '').strip()
                            crash_cost = row.get('crash_cost', '0').strip()
                            resource_demand = row.get(
                                'resource_demand', '0').strip()
                            normal_cost = row.get('normal_cost', '0').strip()

                            self.tree.insert("", tk.END, values=(
                                row['id'],
                                activity_name,
                                row['duration'],
                                predecessors,
                                min_duration,
                                crash_cost,
                                resource_demand,
                                normal_cost
                            ))

                messagebox.showinfo(
                    "Success", f"CSV file loaded successfully!\nMode: {
                        detected_mode.title()}")

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to load CSV file: {
                        str(e)}")

    def load_deterministic_csv(self):
        """Load activities from deterministic CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select Deterministic CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Clear existing data but preserve mode, then set deterministic
                # mode
                self.clear_all(reset_mode=False)
                self.analysis_mode = 'deterministic'
                self.current_analyzer = self.cpm_analyzer
                self.setup_deterministic_tree()
                self.mode_label.config(text="Mode: CPM", foreground="blue")

                # Load CSV data
                with open(file_path, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        activity_name = row.get('activity', '').strip()
                        predecessors = row.get('predecessors', '').strip()
                        min_duration = row.get('min_duration', '').strip()
                        crash_cost = row.get('crash_cost', '0').strip()
                        resource_demand = row.get(
                            'resource_demand', '0').strip()
                        normal_cost = row.get('normal_cost', '0').strip()

                        self.tree.insert("", tk.END, values=(
                            row['id'],
                            activity_name,
                            row['duration'],
                            predecessors,
                            min_duration,
                            crash_cost,
                            resource_demand,
                            normal_cost
                        ))

                messagebox.showinfo(
                    "Success", "Deterministic CSV file loaded successfully!")

            except Exception as e:
                messagebox.showerror(
                    "Error", f"Failed to load CSV file: {
                        str(e)}")

    # def load_probabilistic_csv(self):
    #     """Load activities from probabilistic PERT CSV file"""
    #     file_path = filedialog.askopenfilename(
    #         title="Select Probabilistic (PERT) CSV file",
    #         filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    #     )

    #     if file_path:
    #         try:
    #             # Clear existing data and set probabilistic mode
    #             self.clear_all()
    #             self.analysis_mode = 'probabilistic'
    #             self.current_analyzer = self.pert_analyzer
    #             self.setup_probabilistic_tree()
    #             self.mode_label.config(text="Mode: Probabilistic (PERT)", foreground="green")

    #             # Load CSV data
    #             activities_data = []
    #             with open(file_path, 'r', newline='') as file:
    #                 reader = csv.DictReader(file)
    #                 for row in reader:
    #                     # Extract only required PERT columns, ignore extra columns
    #                     pert_data = {
    #                         'id': row['id'],
    #                         'predecessors': row.get('predecessors', '').strip(),
    #                         'optimistic': int(float(row['optimistic'])),  # Convert to int
    #                         'most_likely': int(float(row['most_likely'])),  # Convert to int
    #                         'pessimistic': int(float(row['pessimistic']))  # Convert to int
    #                     }
    #                     activities_data.append(pert_data)

    #             # Process through PERT analyzer to get calculated values
    #             processed_activities = self.pert_analyzer.load_activities_from_pert_data(activities_data)

    #             # Display in tree
    #             for activity in processed_activities:
    #                 self.tree.insert("", tk.END, values=(
    #                     activity['id'],
    #                     ', '.join(activity['predecessors']) if activity['predecessors'] else '',
    #                     str(activity['optimistic']),  # Display as integer
    #                     str(activity['most_likely']),  # Display as integer
    #                     str(activity['pessimistic']),  # Display as integer
    #                     str(activity['expected_time_ceil']),  # Ceiling value
    #                     f"{activity['variance']:.3f}"
    #                 ))

    #             # Enable probability analysis tab
    #             self.enable_probability_analysis()

    #             messagebox.showinfo("Success", "Probabilistic CSV file loaded successfully!")

    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to load probabilistic CSV file: {str(e)}")

    def load_probabilistic_csv(self):
        """Load activities from probabilistic PERT CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select Probabilistic (PERT) CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Clear existing data but preserve mode, then set probabilistic
                # mode
                self.clear_all(reset_mode=False)
                self.analysis_mode = 'probabilistic'
                self.current_analyzer = self.pert_analyzer
                self.setup_probabilistic_tree()
                self.mode_label.config(text="Mode: PERT", foreground="green")

                # Load CSV data
                activities_data = []
                with open(file_path, 'r', newline='') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        try:
                            pert_data = {
                                'id': row['id'],
                                'predecessors': row.get('predecessors', '').strip(),
                                'optimistic': int(float(row['optimistic'])),
                                'most_likely': int(float(row['most_likely'])),
                                'pessimistic': int(float(row['pessimistic'])),
                                'min_duration': self._safe_float_to_int(row.get('min_duration', 1)),
                                'crash_cost': self._safe_float_to_int(row.get('crash_cost', 0)),
                                'resource_demand': self._safe_float_to_int(row.get('resource_demand', 0)),
                                'normal_cost': self._safe_float_to_int(row.get('normal_cost', 0))
                            }
                            activities_data.append(pert_data)
                        except Exception as row_e:
                            print(f"Skipping row due to error: {row_e}")

                # Process through PERT analyzer to get calculated values
                processed_activities = self.pert_analyzer.load_activities_from_pert_data(
                    activities_data)

                # Optionally display in tree or enable probability analysis tab here
                # self.enable_probability_analysis()
                # messagebox.showinfo("Success", "Probabilistic CSV file loaded successfully!")

            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Failed to load probabilistic CSV file: {
                        str(e)}")

    def _safe_float_to_int(self, value):
        """Safely convert float string to integer, handling various formats"""

        """Safely convert float string to integer, handling various formats"""
        try:
            if value is None or value == '':
                return 0
            # Convert to float first, then to int to handle strings like "3.0"
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return 0

    def download_sample_deterministic_csv(self):
        """Save and download a sample deterministic CSV file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Sample Deterministic CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # Define sample deterministic data
                sample_data = [
                    [
                        "id", "activity", "duration", "predecessors", "min_duration", "crash_cost", "resource_demand", "normal_cost"], [
                        "A", "Design Phase", "5", "", "1", "300", "2", "100"], [
                        "B", "Requirements Analysis", "3", "", "2", "500", "1", "150"], [
                        "C", "Architecture Design", "7", "A,B", "5", "600", "3", "200"], [
                        "D", "Database Design", "5", "C", "4", "400", "1", "120"], [
                            "E", "Frontend Development", "6", "C", "3", "300", "4", "180"], [
                                "F", "Backend Development", "8", "C", "5", "200", "5", "250"], [
                                    "G", "Testing", "3", "D", "3", "800", "2", "90"], [
                                        "H", "Deployment", "4", "E,F", "2", "1000", "1", "110"], ]

                # Write to CSV file
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(sample_data)

                messagebox.showinfo(
                    "Success", f"Sample deterministic CSV saved to:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Error",
                                     f"Failed to save sample CSV: {str(e)}")

    # def download_sample_probabilistic_csv(self):
    #     """Save and download a sample probabilistic CSV file"""
    #     file_path = filedialog.asksaveasfilename(
    #         title="Save Sample Probabilistic CSV",
    #         defaultextension=".csv",
    #         filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    #     )

    #     if file_path:
    #         try:
    #             # Define sample probabilistic data (only required PERT columns)
    #             sample_data = [
    #                 ["id", "predecessors", "optimistic", "most_likely", "pessimistic"],
    #                 ["A", "", "3", "4", "7"],
    #                 ["B", "", "7", "9", "12"],
    #                 ["C", "A,B", "4", "5", "9"],
    #                 ["D", "A,B", "10", "11", "16"],
    #                 ["E", "C,D", "18", "20", "22"],
    #                 ["F", "E", "12", "16", "17"],
    #                 ["G", "E", "7", "8", "12"],
    #                 ["H", "F,G", "11", "15", "17"],
    #                 ["I", "H", "6", "8", "10"],
    #                 ["J", "I", "6", "7", "9"]
    #             ]

    #             # Write to CSV file
    #             with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
    #                 writer = csv.writer(csvfile)
    #                 writer.writerows(sample_data)

    #             messagebox.showinfo("Success", f"Sample probabilistic CSV saved to:\n{file_path}")

    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to save sample CSV: {str(e)}")

    def download_sample_probabilistic_csv(self):
        """Save and download a sample probabilistic CSV file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Sample Probabilistic CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # UPDATED: Define sample probabilistic data with ALL fields
                sample_data = [
                    ["id", "predecessors", "optimistic", "most_likely", "pessimistic",
                     "min_duration", "crash_cost", "resource_demand", "normal_cost"],
                    ["A", "", "3", "4", "7", "1", "300", "2", "100"],
                    ["B", "", "7", "9", "12", "2", "500", "1", "150"],
                    ["C", "A,B", "4", "5", "9", "2", "600", "3", "200"],
                    ["D", "A,B", "10", "11", "16", "3", "400", "1", "120"],
                    ["E", "C,D", "18", "20", "22", "5", "300", "4", "180"],
                    ["F", "E", "12", "16", "17", "3", "200", "5", "160"],
                    ["G", "E", "7", "8", "12", "2", "800", "2", "140"],
                    ["H", "F,G", "11", "15", "17", "4", "1000", "1", "250"],
                    ["I", "H", "6", "8", "10", "2", "250", "2", "80"],
                    ["J", "I", "6", "7", "9", "1", "250", "1", "90"]
                ]

                # Write to CSV file
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerows(sample_data)

                messagebox.showinfo(
                    "Success", f"Sample probabilistic CSV saved to:\n{file_path}")

            except Exception as e:
                messagebox.showerror("Error",
                                     f"Failed to save sample CSV: {str(e)}")

    def add_row(self):
        """Add a new empty row"""
        if self.analysis_mode == 'probabilistic':
            # Add row with correct number of columns for PERT
            self.tree.insert(
                "",
                tk.END,
                values=(
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""))
        else:
            # Add row for deterministic mode (8 columns including Normal Cost)
            self.tree.insert(
                "", tk.END, values=(
                    "", "", "", "", "", "", "", ""))

    def delete_row(self):
        """Delete selected row"""
        selected = self.tree.selection()
        if selected:
            for item in selected:
                self.tree.delete(item)
        else:
            messagebox.showwarning("Warning", "Please select a row to delete.")

    def clear_all(self, reset_mode=True):
        """Clear all data from input table and all tabs"""
        # Clear the input table
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Reset analysis mode only if requested
        if reset_mode:
            self.analysis_mode = None
            self.current_analyzer = None
            self.mode_label.config(text="Mode: None", foreground="black")

        # Reset to deterministic tree layout
        self.setup_deterministic_tree()

        # Clear analyzer data
        if hasattr(self, 'cpm_analyzer'):
            self.cpm_analyzer.G = None
            self.cpm_analyzer.critical_paths = []
            self.cpm_analyzer.critical_activities = []

        if hasattr(self, 'pert_analyzer'):
            self.pert_analyzer.G = None
            self.pert_analyzer.critical_paths = []
            self.pert_analyzer.critical_activities = []

        # Disable probability analysis tab
        self.disable_probability_analysis()

        # Clear results tab
        if hasattr(self, 'results_text'):
            self.results_text.delete(1.0, tk.END)

        # Clear network diagram
        if hasattr(self, 'fig_network'):
            self.fig_network.clear()
            self.canvas_network.draw()

        # Clear critical path diagram
        if hasattr(self, 'fig_critical_path'):
            self.fig_critical_path.clear()
            self.canvas_critical_path.draw()

        # Clear Gantt chart
        if hasattr(self, 'fig_gantt'):
            self.fig_gantt.clear()
            self.canvas_gantt.draw()

        # Clear probability chart
        if hasattr(self, 'fig_probability'):
            self.fig_probability.clear()
            self.canvas_probability.draw()

        # Clear RCPS tables
        if hasattr(self, 'fig_rcps_tables'):
            self.fig_rcps_tables.clear()
            self.canvas_rcps_tables.draw()

        # Clear RCPS stored data
        if hasattr(self, 'last_rcps_table'):
            self.last_rcps_table = None

        # Clear crashing tab
        if hasattr(self, 'crash_results_text'):
            self.crash_results_text.delete(1.0, tk.END)

        # Clear crash step diagrams
        if hasattr(self, 'crash_steps_frame'):
            for widget in self.crash_steps_frame.winfo_children():
                widget.destroy()

        if hasattr(self, 'crash_step_images'):
            self.crash_step_images = []

        # Clear RCPS crashing tab
        if hasattr(self, 'rcps_crash_results_text'):
            self.rcps_crash_results_text.delete(1.0, tk.END)

        # if hasattr(self, 'fig_rcps_crashed'):
        #     self.fig_rcps_crashed.clear()
        #     self.canvas_rcps_crashed.draw()

        # Clear RCPS crash step diagrams
        if hasattr(self, 'rcps_crash_steps_frame'):
            for widget in self.rcps_crash_steps_frame.winfo_children():
                widget.destroy()

        if hasattr(self, 'rcps_crash_step_images'):
            self.rcps_crash_step_images = []

        # Reset input field values to defaults
        if hasattr(self, 'resource_limit_var'):
            self.resource_limit_var.set("5")

        if hasattr(self, 'priority_rule_var'):
            self.priority_rule_var.set("minimum_slack")

        if hasattr(self, 'target_duration_var'):
            self.target_duration_var.set("10")

        if hasattr(self, 'crash_budget_var'):
            self.crash_budget_var.set("")

        if hasattr(self, 'rcps_target_duration_var'):
            self.rcps_target_duration_var.set("10")

        if hasattr(self, 'rcps_crash_budget_var'):
            self.rcps_crash_budget_var.set("")

        # Optional: Show a message to confirm clearing
        messagebox.showinfo(
            "Cleared",
            "All data has been cleared from all tabs.")

    def edit_item(self, event):
        """Edit selected item in place"""
        item = self.tree.selection()[0]
        column = self.tree.identify_column(event.x)

        # Get column index
        col_index = int(column.replace('#', '')) - 1
        col_names = ["ID", "Activity Name", "Duration", "Predecessors"]

        # Get current value
        current_values = list(self.tree.item(item, 'values'))
        current_value = current_values[col_index] if col_index < len(
            current_values) else ""

        # Create entry widget for editing
        bbox = self.tree.bbox(item, column)
        if bbox:
            entry = tk.Entry(self.tree)
            entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            entry.insert(0, current_value)
            entry.select_range(0, tk.END)
            entry.focus()

            def save_edit(event=None):
                new_value = entry.get()
                current_values[col_index] = new_value
                self.tree.item(item, values=current_values)
                entry.destroy()

            def cancel_edit(event=None):
                entry.destroy()

            entry.bind("<Return>", save_edit)
            entry.bind("<Escape>", cancel_edit)
            entry.bind("<FocusOut>", save_edit)

    # def get_activities_data(self):
    #     """Get activities data from the treeview based on current mode"""
    #     activities_data = []

    #     if self.analysis_mode == 'deterministic':
    #         # Deterministic format: ID, Activity Name, Duration, Predecessors, Min Duration, Crash Cost, Resource Demand
    #         for item in self.tree.get_children():
    #             values = self.tree.item(item, 'values')
    #             if values and values[0]:  # Must have an ID
    #                 activities_data.append({
    #                     'id': values[0],
    #                     'activity': values[1] if len(values) > 1 else '',
    #                     'duration': values[2] if len(values) > 2 else '0',
    #                     'predecessors': values[3] if len(values) > 3 else '',
    #                     'min_duration': values[4] if len(values) > 4 else values[2] if len(values) > 2 else '0',
    #                     'crash_cost': values[5] if len(values) > 5 else '0',
    #                     'resource_demand': values[6] if len(values) > 6 else '0'
    #                 })

    #     elif self.analysis_mode == 'probabilistic':
    #         # Probabilistic format: ID, Predecessors, Optimistic, Most Likely, Pessimistic, Expected Time, Variance, Min Duration, Crash Cost, Resource Demand, Normal Cost
    #         for item in self.tree.get_children():
    #             values = self.tree.item(item, 'values')
    #             if values and values[0]:  # Must have an ID
    #                 activities_data.append({
    #                     'id': values[0],
    #                     'predecessors': values[1] if len(values) > 1 else '',
    #                     'optimistic': self._safe_float_to_int(values[2]) if len(values) > 2 else 0,
    #                     'most_likely': self._safe_float_to_int(values[3]) if len(values) > 3 else 0,
    #                     'pessimistic': self._safe_float_to_int(values[4]) if len(values) > 4 else 0,
    #                     'min_duration': self._safe_float_to_int(values[7]) if len(values) > 7 else 1,
    #                     'crash_cost': self._safe_float_to_int(values[8]) if len(values) > 8 else 0,
    #                     'resource_demand': self._safe_float_to_int(values[9]) if len(values) > 9 else 0,
    #                     'normal_cost': self._safe_float_to_int(values[10]) if len(values) > 10 else 0
    #                 })

    #     return activities_data

    def get_activities_data(self):
        """Get activities data from the treeview based on current mode"""
        activities_data = []

        if self.analysis_mode == 'deterministic':
            # Deterministic format: ID, Activity Name, Duration, Predecessors,
            # Min Duration, Crash Cost, Resource Demand, Normal Cost
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                if values and values[0]:  # Must have an ID
                    activities_data.append({
                        'id': values[0],
                        'activity': values[1] if len(values) > 1 else '',
                        'duration': values[2] if len(values) > 2 else '0',
                        'predecessors': values[3] if len(values) > 3 else '',
                        'min_duration': values[4] if len(values) > 4 else values[2] if len(values) > 2 else '0',
                        'crash_cost': values[5] if len(values) > 5 else '0',
                        'resource_demand': values[6] if len(values) > 6 else '0',
                        'normal_cost': values[7] if len(values) > 7 else '0'
                    })

        elif self.analysis_mode == 'probabilistic':
            # UPDATED: Probabilistic format with ALL fields
            for item in self.tree.get_children():
                values = self.tree.item(item, 'values')
                if values and values[0]:  # Must have an ID
                    activities_data.append({
                        'id': values[0],
                        'predecessors': values[1] if len(values) > 1 else '',
                        'optimistic': self._safe_float_to_int(values[2]) if len(values) > 2 else 0,
                        'most_likely': self._safe_float_to_int(values[3]) if len(values) > 3 else 0,
                        'pessimistic': self._safe_float_to_int(values[4]) if len(values) > 4 else 0,
                        # Skip expected_time (index 5) and variance (index 6)
                        # as they're calculated
                        'min_duration': self._safe_float_to_int(values[7]) if len(values) > 7 else 1,
                        'crash_cost': self._safe_float_to_int(values[8]) if len(values) > 8 else 0,
                        'resource_demand': self._safe_float_to_int(values[9]) if len(values) > 9 else 0,
                        'normal_cost': self._safe_float_to_int(values[10]) if len(values) > 10 else 0
                    })

        return activities_data

    def analyze_project(self):
        """Analyze the project using CPM or PERT based on current mode"""
        try:
            if not self.analysis_mode:
                messagebox.showwarning(
                    "Warning", "Please load data first (deterministic or probabilistic).")
                return

            activities_data = self.get_activities_data()

            if not activities_data:
                messagebox.showwarning(
                    "Warning", "Please enter some activities to analyze.")
                return

            # Perform analysis based on mode
            if self.analysis_mode == 'deterministic':
                G, critical_paths, critical_activities = self.cpm_analyzer.analyze(
                    activities_data)
                analysis_type = "CPM"
            else:  # probabilistic
                G, critical_paths, critical_activities = self.pert_analyzer.analyze(
                    activities_data)
                analysis_type = "PERT"

            # Display results
            self.display_results(G, critical_paths, analysis_type)

            # Generate network diagram
            self.generate_network_diagram(G, critical_activities)

            # Generate critical path visualization
            self.visualize_critical_path_network(G, critical_activities)

            # Generate Gantt chart
            self.generate_gantt_chart(G, critical_activities)

            # Update probability analysis if in PERT mode
            if self.analysis_mode == 'probabilistic':
                self.update_probability_analysis()

            # Switch to results tab
            self.notebook.select(1)

            messagebox.showinfo(
                "Success", f"{analysis_type} analysis completed successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")

    def save_results_csv(self):
        """Save analysis results to CSV file"""
        try:
            # Check if analysis has been performed
            if not self.current_analyzer or not hasattr(
                    self.current_analyzer, 'G') or self.current_analyzer.G is None:
                messagebox.showwarning(
                    "Warning", "Please run the analysis first before saving results.")
                return

            # Get file path for saving
            file_path = filedialog.asksaveasfilename(
                title="Save Analysis Results as CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if not file_path:
                return  # User cancelled

            G = self.current_analyzer.G

            # Prepare data for CSV
            csv_data = []
            headers = [
                "Activity",
                "Duration",
                "ES",
                "EF",
                "LS",
                "LF",
                "Float",
                "Critical",
                "Predecessors",
                "Immediate_Successors",
                "Total_Successors",
                "Resource_Demand",
                "Cumulative_Demand",
                "GRPW"]

            for node in G.nodes():
                if node not in ['START', 'END']:  # Skip START and END nodes
                    # Get predecessors and successors as comma-separated
                    # strings
                    predecessors = ', '.join(
                        [pred for pred in G.predecessors(node) if pred != 'START'])
                    immediate_successors = ', '.join(
                        [succ for succ in G.successors(node) if succ != 'END'])

                    row = [
                        node,  # Activity ID
                        G.nodes[node]['duration'],
                        G.nodes[node]['ES'],
                        G.nodes[node]['EF'],
                        G.nodes[node]['LS'],
                        G.nodes[node]['LF'],
                        G.nodes[node]['float'],
                        "Yes" if G.nodes[node]['float'] == 0 else "No",
                        predecessors,
                        immediate_successors,
                        G.nodes[node]['num_total_successors'],
                        G.nodes[node]['resource_demand'],
                        G.nodes[node]['cumulative_demand'],
                        G.nodes[node]['grpw']
                    ]
                    csv_data.append(row)

            # Write to CSV file
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)  # Write header row
                writer.writerows(csv_data)  # Write data rows

            messagebox.showinfo(
                "Success",
                f"Analysis results saved successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV file: {str(e)}")

    def display_results(self, G, critical_paths, analysis_type="CPM"):
        """Display analysis results in the results tab"""
        # Clear previous results
        self.results_text.delete(1.0, tk.END)

        # Prepare data for tabulation
        table_data = []

        if analysis_type == "PERT":
            # PERT-specific headers and data
            for node in G.nodes():
                if node not in ['START', 'END']:  # Skip START and END nodes
                    table_data.append([
                        node,
                        # Expected time (original)
                        f"{G.nodes[node]['expected_time']:.2f}",
                        G.nodes[node]['duration'],  # Expected time (ceil)
                        f"{G.nodes[node]['variance']:.3f}",  # Variance
                        G.nodes[node]['ES'],
                        G.nodes[node]['EF'],
                        G.nodes[node]['LS'],
                        G.nodes[node]['LF'],
                        G.nodes[node]['float'],
                        "Yes" if G.nodes[node]['float'] == 0 else "No"
                    ])

            headers = [
                "Activity",
                "Expected Time",
                "Duration (Ceil)",
                "Variance",
                "ES",
                "EF",
                "LS",
                "LF",
                "Float",
                "Critical"]

        else:
            # CPM-specific headers and data
            for node in G.nodes():
                if node not in ['START', 'END']:  # Skip START and END nodes
                    table_data.append([
                        node,
                        G.nodes[node]['duration'],
                        G.nodes[node]['ES'],
                        G.nodes[node]['EF'],
                        G.nodes[node]['LS'],
                        G.nodes[node]['LF'],
                        G.nodes[node]['float'],
                        "Yes" if G.nodes[node]['float'] == 0 else "No",
                        G.nodes[node].get('num_predecessors', 0),
                        G.nodes[node].get('num_immediate_successors', 0),
                        G.nodes[node].get('num_total_successors', 0),
                        G.nodes[node].get('resource_demand', 0),
                        G.nodes[node].get('cumulative_demand', 0),
                        G.nodes[node].get('grpw', 0)
                    ])

            headers = [
                "Activity",
                "Duration",
                "ES",
                "EF",
                "LS",
                "LF",
                "Float",
                "Critical",
                "# Pred",
                "# Imm Succ",
                "# Total Succ",
                "Resource",
                "Cum Demand",
                "GRPW"]

        # Sort by early start time
        table_data.sort(
            key=lambda x: int(
                x[4] if analysis_type == "PERT" else x[2]))

        results_table = tabulate(table_data, headers=headers, tablefmt="grid")

        # Display results
        results_text = f"{analysis_type} ANALYSIS RESULTS\n"
        results_text += "=" * 50 + "\n\n"
        results_text += results_table + "\n\n"

        # Display critical path(s)
        results_text += "CRITICAL PATH(S):\n"
        results_text += "-" * 20 + "\n"
        for i, path in enumerate(critical_paths):
            # Filter out START and END from path display
            display_path = [
                node for node in path if node not in [
                    'START', 'END']]
            results_text += f"Path {i + 1}: {' -> '.join(display_path)}\n"

        # Calculate project duration
        project_duration = max([G.nodes[node]['EF'] for node in G.nodes()])
        results_text += f"\nPROJECT DURATION: {project_duration} time units\n"

        # Add PERT-specific information
        if analysis_type == "PERT" and hasattr(self, 'pert_analyzer'):
            results_text += f"PROJECT VARIANCE: {
                self.pert_analyzer.project_variance}\n"
            results_text += f"PROJECT STANDARD DEVIATION: {
                self.pert_analyzer.project_std}\n"

        self.results_text.insert(1.0, results_text)

    def generate_network_diagram(self, G, critical_activities):
        """Generate network diagram"""
        self.fig_network.clear()
        ax = self.fig_network.add_subplot(111)

        # Create hierarchical layout
        pos = {}
        generations = list(nx.topological_generations(G))

        for i, gen in enumerate(generations):
            sorted_gen = sorted(gen)
            for j, node in enumerate(sorted_gen):
                y_pos = (j - len(sorted_gen) / 2 + 0.5) * 4
                pos[node] = (i * 3, y_pos)

        # Node parameters
        node_radius = 0.6

        # Draw edges
        for u, v in G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]

            dx = x2 - x1
            dy = y2 - y1
            distance = (dx ** 2 + dy ** 2) ** 0.5

            if distance > 0:
                dx_norm = dx / distance
                dy_norm = dy / distance

                start_x = x1 + node_radius * dx_norm
                start_y = y1 + node_radius * dy_norm
                end_x = x2 - node_radius * dx_norm
                end_y = y2 - node_radius * dy_norm

                ax.annotate(
                    "", xy=(
                        end_x, end_y), xytext=(
                        start_x, start_y), arrowprops=dict(
                        arrowstyle="->", color="black", lw=1.5))

        # Draw nodes
        for node in G.nodes():
            x, y = pos[node]

            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'
            elif node in critical_activities:
                color = 'red'
            else:
                color = 'lightblue'

            circle = plt.Circle(
                (x,
                 y),
                node_radius,
                fill=True,
                color=color,
                alpha=0.7,
                edgecolor='black',
                linewidth=1.5)
            ax.add_patch(circle)

            if node in ['START', 'END']:
                display_text = 'Start' if node == 'START' else 'End'
                ax.text(x, y, display_text, ha='center', va='center',
                        fontsize=10, fontweight='bold')
            else:
                ax.plot([x - node_radius, x + node_radius], [y, y],
                        color='black', linewidth=1.2)
                ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                        fontsize=10, fontweight='bold')
                ax.text(x, y - node_radius / 2, str(G.nodes[node]['duration']),
                        ha='center', va='center', fontsize=9)

        # Create legend for critical path
        legend_elements = [
            mpatches.Patch(
                color='red',
                alpha=0.7,
                label='Critical Path'),
            mpatches.Patch(
                color='lightblue',
                alpha=0.7,
                label='Normal Activity')]
        ax.legend(handles=legend_elements, loc='lower right')

        ax.set_title("Project Network Diagram")
        ax.axis('equal')
        ax.axis('off')

        self.canvas_network.draw()

    def generate_gantt_chart(self, G, critical_activities):
        """Generate Gantt chart"""
        self.fig_gantt.clear()
        ax = self.fig_gantt.add_subplot(111)

        # Extract activity data
        activities = []
        for node in G.nodes():
            if node not in ['START', 'END']:
                node_data = G.nodes[node]
                activities.append({
                    'id': node,
                    'duration': node_data.get('duration', 0),
                    'early_start': node_data.get('ES', 0),
                    'early_finish': node_data.get('EF', 0),
                    'late_start': node_data.get('LS', 0),
                    'late_finish': node_data.get('LF', 0),
                    'float': node_data.get('float', 0),
                    'critical': node in critical_activities,
                    'resource': node_data.get('resource_demand', 0),
                    'predecessors': ','.join([p for p in G.predecessors(node) if p not in ['START', 'END']])
                })

        # Convert to DataFrame for further use
        df_gantt = pd.DataFrame(activities)

        # Sort activities by early start time
        activities.sort(key=lambda x: (x['early_start'], x['id']))

        # Colors
        critical_color = 'red'
        normal_color = 'lightblue'
        slack_color = 'lightgrey'

        # Calculate project duration
        project_duration = max([activity['late_finish']
                               for activity in activities])

        # Y positions
        y_pos = np.arange(len(activities))
        y_pos = y_pos[::-1]

        # Create bars
        activity_labels = []
        for i, activity in enumerate(activities):
            activity_id = activity['id']
            early_start = activity['early_start']
            early_finish = activity['early_finish']
            duration = activity['duration']
            float_time = activity['float']

            is_critical = activity_id in critical_activities
            bar_color = critical_color if is_critical else normal_color

            # Main activity bar
            ax.barh(y_pos[i], duration, left=early_start,
                    color=bar_color, alpha=0.7, height=0.6,
                    edgecolor='black', linewidth=0.8)

            # Slack bar
            if float_time > 0:
                ax.barh(y_pos[i], float_time, left=early_finish,
                        color=slack_color, alpha=0.5, height=0.6,
                        edgecolor='gray', linewidth=0.5, linestyle='--')

            activity_labels.append(activity_id)

            # Add text
            bar_center_x = early_start + duration / 2
            ax.text(bar_center_x, y_pos[i], activity_id,
                    ha='center', va='center', fontweight='bold', fontsize=10)

            # Early start/finish times
            ax.text(
                early_start - 0.1,
                y_pos[i],
                f"{early_start}",
                ha='right',
                va='center',
                fontsize=9,
                color='darkgreen',
                fontweight='bold')
            ax.text(
                early_finish + 0.1,
                y_pos[i],
                f"{early_finish}",
                ha='left',
                va='center',
                fontsize=9,
                color='darkgreen',
                fontweight='bold')

        # Customize chart
        ax.set_yticks(y_pos)
        ax.set_yticklabels(activity_labels)
        ax.set_xlabel('Time Units')
        ax.set_ylabel('Activities')
        ax.set_title('Project Gantt Chart')
        ax.set_xlim(-0.5, project_duration + 0.5)
        ax.grid(True, axis='x', alpha=0.3)

        # Legend
        legend_elements = [
            mpatches.Patch(
                color=critical_color,
                alpha=0.7,
                label='Critical Activities'),
            mpatches.Patch(
                color=normal_color,
                alpha=0.7,
                label='Non-Critical Activities'),
            mpatches.Patch(
                color=slack_color,
                alpha=0.5,
                label='Available Slack/Float')]
        ax.legend(handles=legend_elements, loc='lower left')

        self.canvas_gantt.draw()

        # Return the DataFrame for further use
        return df_gantt

    def visualize_critical_path_network(self, G, critical_activities=None):
        """
        Visualize the project network with critical path highlighted and detailed node information.
        Nodes have a semicircle on the left side attached to a square, similar to the provided image.

        Args:
            G: NetworkX DiGraph
            critical_activities: List of activities on the critical path
        """
        if critical_activities is None:
            critical_activities = []

        # Clear the figure
        self.fig_critical_path.clear()
        ax = self.fig_critical_path.add_subplot(111)

        # Create a custom positioning
        pos = {}

        # Get topological generations (layers of nodes)
        generations = list(nx.topological_generations(G))

        # Set x-coordinates by generation and y-coordinates to spread nodes
        # vertically
        for i, gen in enumerate(generations):
            # Sort nodes within generation to make visualization more
            # predictable
            sorted_gen = sorted(gen)

            # Calculate vertical positions
            for j, node in enumerate(sorted_gen):
                y_pos = (j - len(sorted_gen) / 2 + 0.5) * \
                    2  # Center nodes vertically
                # Increase spacing between generations
                pos[node] = (i * 3, y_pos)

        # Node size parameters
        # The left third will be a semicircle, the right two-thirds will be a
        # square
        width = 1.2
        height = width * 2 / 3
        semicircle_width = width / 3
        square_width = width * 2 / 3
        node_radius = 0.3

        # Draw edges with proper arrowheads
        for u, v in G.edges():
            # Get node positions
            x1, y1 = pos[u]
            x2, y2 = pos[v]

            # Calculate starting and ending points based on node type
            if u in ['START', 'END']:
                # For START/END nodes (circles), start from edge of circle
                dx = x2 - x1
                dy = y2 - y1
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > 0:
                    dx_norm = dx / distance
                    dy_norm = dy / distance
                    start_x = x1 + node_radius * dx_norm
                    start_y = y1 + node_radius * dy_norm
                else:
                    start_x = x1
                    start_y = y1
            else:
                # For regular nodes, start from far right
                start_x = x1 + width / 2 - semicircle_width / 2
                start_y = y1

            if v in ['START', 'END']:
                # For START/END nodes (circles), end at edge of circle
                dx = x2 - x1
                dy = y2 - y1
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance > 0:
                    dx_norm = dx / distance
                    dy_norm = dy / distance
                    end_x = x2 - node_radius * dx_norm
                    end_y = y2 - node_radius * dy_norm
                else:
                    end_x = x2
                    end_y = y2
            else:
                # For regular nodes, end at far left
                end_x = x2 - square_width / 2 - semicircle_width
                end_y = y2

            # Draw straight arrow
            ax.annotate(
                "", xy=(
                    end_x, end_y), xycoords='data', xytext=(
                    start_x, start_y), textcoords='data', arrowprops=dict(
                    arrowstyle="->", color="black", lw=1.5))

        # Draw nodes with semicircle on left side and square on right side
        for node in G.nodes():
            x, y = pos[node]
            is_critical = node in critical_activities
            color = 'red' if is_critical else 'lightblue'

            # Special colors for START and END nodes
            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'

            # Special handling for START and END nodes
            if node in ['START', 'END']:
                # Draw simple circle for START/END nodes
                circle = plt.Circle((x, y), node_radius,
                                    fill=True, color=color, alpha=0.7,
                                    edgecolor='black', linewidth=1.5, zorder=3)
                ax.add_patch(circle)

                # Add only the text "Start" or "End"
                display_text = 'Start' if node == 'START' else 'End'
                ax.text(
                    x,
                    y,
                    display_text,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=9,
                    fontweight='bold',
                    zorder=5)
            else:
                # Draw semicircle on left side
                semicircle = mpatches.Wedge(
                    (x - square_width / 2, y),
                    semicircle_width,  # radius
                    90, 270,  # angles for left-facing semicircle
                    fill=True,
                    color=color,
                    alpha=0.7,
                    edgecolor='black',
                    linewidth=1.4,
                    zorder=3  # Ensure nodes appear above arrows
                )
                ax.add_patch(semicircle)

                # Draw square on right side
                square = plt.Rectangle(
                    # Position square to connect with semicircle
                    (x - square_width / 2, y - height / 2),
                    square_width,
                    height,
                    fill=True,
                    color=color,
                    alpha=0.7,
                    edgecolor='black',
                    linewidth=1.5,
                    zorder=3  # Ensure nodes appear above arrows
                )
                ax.add_patch(square)

                # Draw horizontal and vertical grid lines for the cells
                # Draw horizontal divider across entire shape
                ax.plot([x -
                         square_width /
                         2 -
                         semicircle_width, x +
                         square_width /
                         2], [y, y], color='black', linewidth=0.8, zorder=4)

                # Draw vertical divider between semicircle and square
                ax.plot([x -
                         square_width /
                         2, x -
                         square_width /
                         2], [y -
                              height /
                              2, y +
                              height /
                              2], color='black', linewidth=0.8, zorder=5)

                # Draw vertical divider in square section
                ax.plot([x, x], [y - height / 2, y + height / 2],
                        color='black', linewidth=0.8, zorder=4)

                # Add text in each cell
                # Top row
                ax.text(
                    x - square_width / 2 - semicircle_width / 2,
                    y + height / 4,
                    node,
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=7,
                    zorder=5)
                ax.text(x - square_width / 4,
                        y + height / 4,
                        str(G.nodes[node]['ES']),
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=7,
                        zorder=5)
                ax.text(x + square_width / 4,
                        y + height / 4,
                        str(G.nodes[node]['EF']),
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=7,
                        zorder=5)

                # Bottom row
                ax.text(x - square_width / 2 - semicircle_width / 2,
                        y - height / 4,
                        str(G.nodes[node]['duration']),
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=7,
                        zorder=5)
                ax.text(x - square_width / 4,
                        y - height / 4,
                        str(G.nodes[node]['LS']),
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=7,
                        zorder=5)
                ax.text(x + square_width / 4,
                        y - height / 4,
                        str(G.nodes[node]['LF']),
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=7,
                        zorder=5)

                # Add slack below node
                ax.text(
                    x,
                    y - height / 2 - 0.05,
                    f"Slack: {
                        G.nodes[node]['float']}",
                    horizontalalignment='center',
                    verticalalignment='top',
                    fontsize=8,
                    color='darkblue' if G.nodes[node]['float'] > 0 else 'darkred',
                    zorder=5)

                # Add activity name above node
                def wrap_text(text, width=12):
                    # Only wrap at spaces, don't split long words
                    return "\n".join(
                        textwrap.wrap(
                            text,
                            width=width,
                            break_long_words=False,
                            break_on_hyphens=False))

                activity_name = G.nodes[node].get('activity', '')
                if activity_name and activity_name not in ['Start', 'End']:
                    wrapped_name = wrap_text(
                        activity_name, width=12)  # Adjust width as needed
                    ax.text(
                        x,
                        y + height / 2 + 0.1,
                        wrapped_name,
                        horizontalalignment='center',
                        verticalalignment='bottom',
                        fontsize=8,
                        color='purple',
                        fontweight='bold',
                        zorder=5)

        # Create legend for critical path
        legend_elements = [
            mpatches.Patch(
                color='red',
                alpha=0.7,
                label='Critical Path'),
            mpatches.Patch(
                color='lightblue',
                alpha=0.7,
                label='Normal Activity')]
        ax.legend(handles=legend_elements, loc='lower right')

        # Add legend for node format
        self.fig_critical_path.text(0.01, 0.01, "Node Format:", fontsize=9)
        self.fig_critical_path.text(
            0.12, 0.01, "ID | ES | EF\nDur | LS | LF", fontsize=9)

        ax.set_title("Critical Path Network Diagram")
        ax.axis('off')

        # Draw the canvas
        self.canvas_critical_path.draw()

    ########################################################################
    def create_rcps_tab(self):
        """Create the Resource-Constrained Project Scheduling tab"""
        rcps_frame = ttk.Frame(self.notebook)
        self.notebook.add(rcps_frame, text="RCPS Scheduling")

        # Control frame
        control_frame = ttk.Frame(rcps_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Resource limit input
        ttk.Label(
            control_frame,
            text="Resource Limit:").pack(
            side=tk.LEFT,
            padx=(
                0,
                5))
        self.resource_limit_var = tk.StringVar(value="5")
        resource_entry = ttk.Entry(
            control_frame,
            textvariable=self.resource_limit_var,
            width=10)
        resource_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Priority rule selection
        ttk.Label(
            control_frame,
            text="Priority Rule:").pack(
            side=tk.LEFT,
            padx=(
                0,
                5))
        self.priority_rule_var = tk.StringVar(value="minimum_slack")
        priority_combo = ttk.Combobox(
            control_frame,
            textvariable=self.priority_rule_var,
            width=15)
        priority_combo['values'] = (
            'minimum_slack',
            'shortest_duration',
            'earliest_start')
        priority_combo.pack(side=tk.LEFT, padx=(0, 20))

        # Generate button
        # ttk.Button(control_frame, text="Generate RCPS Schedule",
        #         command=self.generate_rcps_schedule).pack(side=tk.LEFT)
        ttk.Button(control_frame, text="Generate RCPS Schedule",
                   command=self.run_rcps_tables).pack(side=tk.LEFT)

        # Results frame
        results_frame = ttk.Frame(rcps_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Create matplotlib figure for RCPS tables
        self.fig_rcps_tables = plt.Figure(figsize=(18, 10))
        self.canvas_rcps_tables = FigureCanvasTkAgg(
            self.fig_rcps_tables, results_frame)
        self.canvas_rcps_tables.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_rcps_tables(self):
        """Run CPM Analyzer logic and plot schedule tables in RCPS tab."""
        try:
            # Check if analysis has been performed
            if not self.current_analyzer or not hasattr(
                    self.current_analyzer, 'G') or self.current_analyzer.G is None:
                messagebox.showwarning(
                    "Warning", "Please run the analysis first.")
                return

            # Check if current analyzer supports RCPS (support both CPM and PERT)
            # For PERT mode, we'll use expected_time as duration
            # if self.analysis_mode != 'deterministic':
            #     messagebox.showwarning("Warning", "RCPS analysis is only available for deterministic (CPM) data.")
            #     return

            # Get resource limit from user input
            try:
                resource_limit = int(self.resource_limit_var.get())
            except Exception:
                messagebox.showerror("Error", "Invalid resource limit.")
                return

            # --- Data validation: resource limit must be >= max resource demand ---
            max_resource_demand = self._validate_resource_limit(resource_limit)
            if max_resource_demand is None:
                return  # Validation failed, error already shown
            # --- End validation ---

            # Generate CPM Gantt DataFrame
            df_gantt = self.generate_gantt_chart(
                self.current_analyzer.G,
                self.current_analyzer.critical_activities)

            # Calculate RCPS schedule and display tables
            self._calculate_and_display_rcps_tables(df_gantt, resource_limit)

            # Prepare RCPS data for crashing optimization
            self._prepare_rcps_data_for_crashing(df_gantt, resource_limit)

            print("RCPS scheduling completed successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"RCPS scheduling failed: {str(e)}")
            import traceback
            print(traceback.format_exc())

    def _validate_resource_limit(self, resource_limit):
        """
        Validate that resource limit is sufficient for all activities.
        Returns max_resource_demand if valid, None if invalid.
        """
        max_resource_demand = 0
        for node in self.current_analyzer.G.nodes():
            if node not in ['START', 'END']:
                demand = self.current_analyzer.G.nodes[node].get(
                    'resource_demand', 0)
                try:
                    demand = int(demand)
                except Exception:
                    demand = 0
                if demand > max_resource_demand:
                    max_resource_demand = demand

        if resource_limit < max_resource_demand:
            messagebox.showwarning(
                "Resource Limit Too Low",
                f"Resource limit ({resource_limit}) is less than the maximum resource demand ({max_resource_demand}) of any activity.\n"
                "Please enter a resource limit greater than or equal to the largest resource demand."
            )
            return None

        return max_resource_demand

    def _calculate_and_display_rcps_tables(self, df_gantt, resource_limit):
        """
        Calculate RCPS schedule and display the comparison tables.

        Args:
            df_gantt: DataFrame with original CPM schedule data
            resource_limit: Maximum available resources per time period
        """
        # print("DEBUG: Calculating RCPS tables for display...")

        # Get priority rule
        priority_rule = self.priority_rule_var.get()

        # Build CPM and RCPS tables for display
        cpm_table, time_cols, critical_ids = self.current_analyzer.build_cpm_schedule_table(
            df_gantt, resource_limit)
        rcps_table, actual_starts, critical_ids2 = self.current_analyzer.rcps_heuristic_schedule_table(
            df_gantt, resource_limit, priority_rule)

        # Pad CPM table columns if RCPS has more time periods
        cpm_table_updated, time_cols_updated = self._pad_cpm_table_columns(
            cpm_table, rcps_table, time_cols)

        # Plot the comparison tables
        self.plot_schedule_tables(
            cpm_table_updated,
            rcps_table,
            time_cols_updated,
            critical_ids,
            actual_starts,
            df_gantt)

        # print(f"DEBUG: RCPS tables calculated and displayed. Time cols: {len(time_cols_updated)}")

    def _pad_cpm_table_columns(self, cmp_table, rcps_table, time_cols):
        """
        Ensure CPM table has same time columns as RCPS table for proper comparison.

        Args:
            cmp_table: DataFrame with CPM schedule
            rcps_table: DataFrame with RCPS schedule
            time_cols: List of time column identifiers

        Returns:
            Tuple of (updated_cmp_table, updated_time_cols)
        """
        cmp_time_cols = [
            col for col in cmp_table.columns if isinstance(
                col, int)]
        rcps_time_cols = [
            col for col in rcps_table.columns if isinstance(
                col, int)]
        max_time_rcps = max(rcps_time_cols) if rcps_time_cols else 0
        max_time_cmp = max(cmp_time_cols) if cmp_time_cols else 0

        if max_time_rcps > max_time_cmp:
            # Add extra columns to CPM table
            for t in range(max_time_cmp + 1, max_time_rcps + 1):
                cmp_table[t] = ''
            # Ensure columns are in correct order
            non_time_cols = [
                col for col in cmp_table.columns if not isinstance(
                    col, int)]
            all_time_cols = list(range(1, max_time_rcps + 1))
            cmp_table = cmp_table[non_time_cols + all_time_cols]
            time_cols = all_time_cols  # Update time_cols for plotting

        return cmp_table, time_cols

    def _prepare_rcps_data_for_crashing(self, df_gantt, resource_limit):
        """
        Prepare RCPS data in the format required by the crashing optimization.

        This function creates a DataFrame that matches the format expected by
        load_activities_from_data() method for proper crashing optimization.

        Expected format for crashing:
        - id: Activity identifier
        - activity: Activity name/description
        - duration: Current duration from RCPS schedule
        - predecessors: List of predecessor activity IDs
        - min_duration: Minimum crashable duration
        - crash_cost: Cost per unit time reduction
        - resource_demand: Resource requirement per time period

        Args:
            df_gantt: DataFrame with original CPM schedule data
            resource_limit: Maximum available resources per time period
        """
        print("DEBUG: Preparing RCPS data for crashing optimization...")

        # Get priority rule and recalculate RCPS for data extraction
        priority_rule = self.priority_rule_var.get()

        # Run RCPS scheduling to get actual start times and schedule data
        rcps_table, actual_starts, _ = self.current_analyzer.rcps_heuristic_schedule_table(
            df_gantt, resource_limit, priority_rule)

        # Create activities list in the format expected by crashing
        # optimization
        activities_list = []

        # print(f"DEBUG: Processing {len(rcps_table)} rows from RCPS table...")

        for idx, row in rcps_table.iterrows():
            activity_id = row['id']

            # Skip resource tracking rows
            if activity_id in ['RA', 'RS']:
                continue

            # print(f"DEBUG: Processing activity {activity_id}")

            # Get original activity data from analyzer's graph for reference
            original_data = {}
            if activity_id in self.current_analyzer.G.nodes:
                original_data = self.current_analyzer.G.nodes[activity_id]
            else:
                print(
                    f"WARNING: Activity {activity_id} not found in analyzer graph")
                continue

            # Extract duration from RCPS table (this is the scheduled duration)
            try:
                duration = int(row['duration'])
            except (ValueError, TypeError):
                print(
                    f"WARNING: Invalid duration for activity {activity_id}, using original")
                duration = original_data.get('duration', 0)

            # Get activity name
            activity_name = original_data.get('activity', '')

            # Get predecessors from original graph (maintain dependency
            # structure)
            predecessors = []
            if activity_id in self.current_analyzer.G.nodes:
                for pred in self.current_analyzer.G.predecessors(activity_id):
                    if pred not in ['START']:
                        predecessors.append(pred)

            # Get crashing parameters from original graph
            min_duration = original_data.get('min_duration', duration)
            crash_cost = original_data.get('crash_cost', 0)

            # Get resource demand from RCPS table or original graph
            try:
                resource_demand = int(row['resource'])
            except (ValueError, TypeError):
                resource_demand = original_data.get('resource_demand', 0)

            # Get actual start time from RCPS scheduling
            actual_start = row.get('actual_start', 0)
            try:
                actual_start = int(actual_start) if not pd.isna(
                    actual_start) else 0
            except (ValueError, TypeError):
                actual_start = 0

            # Get normal cost from original graph data
            normal_cost = original_data.get('normal_cost', 0)

            # Create activity dictionary in the format expected by
            # load_activities_from_data
            activity_dict = {
                'id': activity_id,
                'activity': activity_name,
                'duration': duration,  # Current RCPS scheduled duration
                'predecessors': predecessors,  # List format for internal use
                'min_duration': min_duration,
                'crash_cost': crash_cost,
                'resource_demand': resource_demand,
                'normal_cost': normal_cost,
                'actual_start': actual_start,
                'ES': actual_start,  # Early Start = Actual Start in RCPS
                'EF': actual_start + duration,  # Early Finish = Actual Start + Duration
            }

            activities_list.append(activity_dict)
            # print(f"DEBUG: Added activity {activity_id}: duration={duration}, actual_start={actual_start}")

        # Store the activities list for RCPS Crashing tab
        self.last_rcps_table = pd.DataFrame(activities_list)

        # print(f"DEBUG: RCPS data prepared for crashing. {len(activities_list)} activities processed.")
        # print(f"DEBUG: Fields in last_rcps_table: {list(self.last_rcps_table.columns)}")

        # Debug: Print complete table of prepared data
        if not self.last_rcps_table.empty:
            print("\nDEBUG: Complete RCPS Activity Data:")
            print("+" + "-" * 78 + "+")
            print(
                f"| {
                    'ID':<4} | {
                    'Duration':<8} | {
                    'Min Dur':<8} | {
                    'Crash $':<8} | {
                        'Resource':<8} | {
                            'Start':<8} | {
                                'Normal $':<8} |")
            print("+" + "-" * 78 + "+")

            for idx, row in self.last_rcps_table.iterrows():
                normal_cost = row.get('normal_cost', 0)
                print(
                    f"| {
                        row['id']:<4} | {
                        row['duration']:<8} | {
                        row['min_duration']:<8} | " f"{
                        row['crash_cost']:<8.0f} | {
                        row['resource_demand']:<8} | " f"{
                            row['actual_start']:<8} | {
                                normal_cost:<8.0f} |")

            print("+" + "-" * 78 + "+")
            print(f"Total Activities: {len(self.last_rcps_table)}")
            print()

        print("RCPS scheduling completed successfully.")

    def plot_schedule_tables(
            self,
            cpm_table,
            rcps_table,
            time_cols,
            critical_ids,
            actual_starts,
            df_gantt):
        """
        Plot the CPM and RCPS schedule tables side by side with highlights in the RCPS tab.
        """
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.colors import Normalize
        from matplotlib.cm import YlOrRd  # Yellow to Red colormap

        self.fig_rcps_tables.clear()
        fig = self.fig_rcps_tables

        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        # Function to create heatmap colors
        def get_heatmap_color(value, min_val, max_val, colormap=YlOrRd):
            """Convert a value to a color using a heatmap scale."""
            if pd.isna(value) or not isinstance(value, (int, float)):
                return 'white'
            norm = Normalize(vmin=min_val, vmax=max_val)
            return colormap(norm(value))

        def get_cell_colors(
                table_data,
                table_type,
                scheduled_activities,
                delayed_activities):
            colors = []

            # Get min and max values only for duration columns in RCPS
            # resource_scheduled row
            time_values = []
            if table_type == 'rcps':
                resource_scheduled_row = table_data[table_data['id'] == 'RS']
                if not resource_scheduled_row.empty:
                    for col in time_cols:
                        val = resource_scheduled_row[col].iloc[0]
                        if isinstance(val, (int, float)) and val > 0:
                            time_values.append(val)

            min_val = min(time_values) if time_values else 0
            max_val = max(time_values) if time_values else 1

            for i, (idx, row) in enumerate(table_data.iterrows()):
                row_colors = []
                for j, col in enumerate(table_data.columns):
                    val = row[col]
                    if j == 0 and row['id'] in critical_ids:
                        row_colors.append('#ffcccc')
                    elif col in time_cols:
                        # EXPLICIT HEATMAP: Apply heatmap ONLY to RS row in
                        # RCPS table
                        if table_type == 'rcps' and row['id'] == 'RS':
                            if isinstance(val, (int, float)) and val > 0:
                                row_colors.append(
                                    get_heatmap_color(
                                        val, min_val, max_val))
                            else:
                                row_colors.append('white')
                        # RESOURCE ROWS: Both RA and RS get gray background in
                        # time columns
                        elif row['id'] in ['RA', 'RS']:
                            row_colors.append('#e0e0e0')
                        # REGULAR ACTIVITIES: Only non-resource rows get
                        # activity coloring
                        else:
                            if table_type == 'cpm':
                                if str(val) == 'S' or (isinstance(
                                        val, (int, float)) and int(val) > 0):
                                    row_colors.append('#b6fcb6')
                                else:
                                    row_colors.append('white')
                            elif table_type == 'rcps':
                                if isinstance(
                                        val, (int, float)) and int(val) > 0:
                                    if row['id'] in delayed_activities:
                                        row_colors.append('#ffd580')
                                    elif row['id'] in scheduled_activities:
                                        row_colors.append('#b6fcb6')
                                    else:
                                        row_colors.append('white')
                                else:
                                    row_colors.append('white')
                    elif row['id'] in ['RA', 'RS']:
                        row_colors.append('#e0e0e0')
                    else:
                        row_colors.append('white')
                colors.append(row_colors)
            return colors

        pretty_names = {
            'id': 'ID',
            'duration': 'D',
            'resource': 'R',
            'early_start': 'ES',
            'late_finish': 'LF',
            'float': 'F',
            'actual_start': 'AS',
        }

        def get_headers(df):
            return [pretty_names.get(col, str(col)) for col in df.columns]

        # Identify scheduled and delayed activities
        scheduled_activities = set()
        delayed_activities = set()
        for idx, row in rcps_table.iterrows():
            if row['id'] not in ['RA', 'RS']:
                if row['actual_start'] == row['early_start']:
                    scheduled_activities.add(row['id'])
                else:
                    delayed_activities.add(row['id'])

        cpm_time_cols = [
            col for col in cpm_table.columns if isinstance(
                col, int)]
        rcps_time_cols = [
            col for col in rcps_table.columns if isinstance(
                col, int)]

        for ax, table_data, table_type, title, tcols in zip(
            [ax1, ax2], [cpm_table, rcps_table], ['cpm', 'rcps'],
            ['Initial CPM-based Plan', 'Resource-Constrained Schedule (RCPS)'],
            [cpm_time_cols, rcps_time_cols]
        ):
            ax.clear()
            ax.axis('off')

            # Prepare cell text and colors
            cell_text = []
            for _, row in table_data.iterrows():
                # Convert float values to integers in display
                formatted_row = []
                # Handle CPM table cell values
                if table_type == 'cpm':
                    for col, val in row.items():
                        if col in time_cols and str(val) == 'S':
                            # Replace 'S' with resource demand
                            formatted_row.append(str(int(row['resource'])))
                        elif isinstance(val, float) and val.is_integer():
                            formatted_row.append(str(int(val)))
                        else:
                            formatted_row.append(str(val))
                else:
                    # Original handling for RCPS table
                    for val in row.values:
                        if isinstance(val, float) and val.is_integer():
                            formatted_row.append(str(int(val)))
                        else:
                            formatted_row.append(str(val))

                # Special handling for resource rows
                if row['id'] in ['RA', 'RS']:
                    formatted_row[1] = ''  # Empty duration
                    formatted_row[2] = ''  # Empty resource

                cell_text.append(formatted_row)

            cell_colors = get_cell_colors(
                table_data,
                table_type,
                scheduled_activities,
                delayed_activities)
            header_colors = ['#cccccc'] * len(table_data.columns)
            custom_headers = get_headers(table_data)
            table = ax.table(
                cellText=cell_text,
                colLabels=custom_headers,
                cellColours=cell_colors,
                colColours=header_colors,
                cellLoc='center',
                loc='center',
                bbox=[0, 0, 1, 1]
            )

            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 2)

            for (i, j), cell in table.get_celld().items():
                cell.set_text_props(weight='normal', size=12)
                if i == -1:
                    cell.set_text_props(weight='bold', size=14)
                    cell.set_height(0.08)
                else:
                    cell.set_height(0.08)

            ax.set_title(title, fontsize=20, fontweight='bold', pad=20)

        fig.tight_layout()
        fig.subplots_adjust(hspace=0.4)
        self.canvas_rcps_tables.draw()

    def update_cpm_graph_with_rcps(self):
        """
        Create a temporary CPM graph updated with RCPS schedule data for crashing optimization.
        This does NOT modify the original analyzer graph.

        Returns: Updated graph copy for RCPS crashing, or None if failed
        """
        if not self.current_analyzer or not hasattr(
                self.current_analyzer,
                'G') or self.current_analyzer.G is None:
            print("ERROR: No CPM graph available for updating")
            return None

        if not hasattr(
                self,
                'last_rcps_table') or self.last_rcps_table is None:
            print("ERROR: No RCPS table available for updating CPM graph")
            return None

        # CRITICAL FIX: Create a copy instead of modifying the original
        updated_G = self.current_analyzer.G.copy()

        rcps_df = self.last_rcps_table

        # Track field transfers for debugging
        fields_transferred = {
            'duration': 0,
            'ES': 0,
            'EF': 0,
            'activity': 0,
            'min_duration': 0,
            'crash_cost': 0,
            'resource_demand': 0
        }

        # Update the COPY with RCPS data
        for idx, row in rcps_df.iterrows():
            act_id = row['id']
            if act_id in updated_G.nodes and act_id not in ['RA', 'RS']:
                try:
                    # Update duration (most critical for crashing)
                    if 'duration' in row and not pd.isna(row['duration']):
                        new_duration = int(row['duration'])
                        updated_G.nodes[act_id]['duration'] = new_duration
                        fields_transferred['duration'] += 1

                    # Use RCPS actual_start times
                    if 'actual_start' in row and not pd.isna(
                            row['actual_start']):
                        actual_start = int(row['actual_start'])
                        duration = int(row['duration'])

                        # Set ES and EF to RCPS actual times
                        updated_G.nodes[act_id]['ES'] = actual_start
                        updated_G.nodes[act_id]['EF'] = actual_start + duration
                        fields_transferred['ES'] += 1
                        fields_transferred['EF'] += 1

                    # Transfer other attributes
                    if 'activity' in row and row['activity'] and not pd.isna(
                            row['activity']):
                        updated_G.nodes[act_id]['activity'] = row['activity']
                        fields_transferred['activity'] += 1

                    if 'min_duration' in row and not pd.isna(
                            row['min_duration']):
                        updated_G.nodes[act_id]['min_duration'] = int(
                            row['min_duration'])
                        fields_transferred['min_duration'] += 1

                    if 'crash_cost' in row and not pd.isna(row['crash_cost']):
                        updated_G.nodes[act_id]['crash_cost'] = float(
                            row['crash_cost'])
                        fields_transferred['crash_cost'] += 1

                    if 'resource_demand' in row and not pd.isna(
                            row['resource_demand']):
                        updated_G.nodes[act_id]['resource_demand'] = int(
                            row['resource_demand'])
                        fields_transferred['resource_demand'] += 1

                except Exception as e:
                    print(f"ERROR: Failed to update node {act_id}: {str(e)}")

        # Calculate project duration and timing for the copy
        project_duration = max([updated_G.nodes[node]['EF']
                               for node in updated_G.nodes()])

        # Calculate Late Start and Late Finish times for the copy
        for node in updated_G.nodes():
            updated_G.nodes[node]['LF'] = project_duration
            updated_G.nodes[node]['LS'] = project_duration

        # Backward pass for LS/LF calculation only
        for node in reversed(list(nx.topological_sort(updated_G))):
            if node not in ['START', 'END']:
                duration = updated_G.nodes[node]['duration']

                successors = list(updated_G.successors(node))
                if successors:
                    min_succ_ls = min([updated_G.nodes[succ]['LS']
                                      for succ in successors])
                    updated_G.nodes[node]['LF'] = min_succ_ls
                else:
                    updated_G.nodes[node]['LF'] = project_duration

                updated_G.nodes[node]['LS'] = updated_G.nodes[node]['LF'] - duration
                updated_G.nodes[node]['float'] = updated_G.nodes[node]['LS'] - \
                    updated_G.nodes[node]['ES']

        print(
            f"Created temporary graph with RCPS data for crashing (original graph preserved)")
        return updated_G

    ##########################################################################
    def create_crashing_tab(self):
        """Create the Crashing Optimization tab with navigation controls always at the bottom."""
        crashing_frame = ttk.Frame(self.notebook)
        crashing_frame.pack(fill=tk.BOTH, expand=True)
        self.notebook.add(crashing_frame, text="Crashing Optimization")

        # Control frame (top)
        control_frame = ttk.Frame(crashing_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            control_frame,
            text="Target Duration:").pack(
            side=tk.LEFT,
            padx=(
                0,
                5))
        self.target_duration_var = tk.StringVar(value="10")
        target_entry = ttk.Entry(
            control_frame,
            textvariable=self.target_duration_var,
            width=10)
        target_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Button(control_frame, text="Run Crashing Optimization",
                   command=self.run_crashing_optimization).pack(side=tk.LEFT)

        # ttk.Label(control_frame, text="Crash Budget:").pack(side=tk.LEFT, padx=(0, 5))
        self.crash_budget_var = tk.StringVar(value="")
        budget_entry = ttk.Entry(
            control_frame,
            textvariable=self.crash_budget_var,
            width=10)
        budget_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Results frame (middle, fills most of the space)
        results_frame = ttk.Frame(crashing_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Text output for crash log/results
        self.crash_results_text = scrolledtext.ScrolledText(
            results_frame, font=("Courier", 10), height=8)
        self.crash_results_text.pack(fill=tk.X, padx=2, pady=2)

        # # Matplotlib figure for crashed network
        # self.fig_crashed = plt.Figure(figsize=(12, 3))
        # self.canvas_crashed = FigureCanvasTkAgg(self.fig_crashed, results_frame)
        # self.canvas_crashed.get_tk_widget().pack(fill=tk.X, padx=2, pady=2)

        # # Step display area (this expands and fills the rest)
        # self.step_display_frame = ttk.Frame(results_frame)
        # self.step_display_frame.pack(fill=tk.BOTH, expand=True)
        # self.step_display_frame.config(style="StepDisplay.TFrame")
        # style = ttk.Style()
        # style.configure("StepDisplay.TFrame", background="lightyellow")

        # Step display area (this expands and fills the rest)
        self.step_display_frame = ttk.Frame(
            results_frame, width=1610, height=500)
        self.step_display_frame.pack_propagate(
            False)  # Prevent resizing to fit children
        self.step_display_frame.pack(padx=2, pady=2)
        self.step_display_frame.config(style="StepDisplay.TFrame")
        style = ttk.Style()
        style.configure("StepDisplay.TFrame", background="lightyellow")

        # Step navigation frame (BOTTOM, always visible)
        step_nav_frame = ttk.Frame(
            crashing_frame,
            borderwidth=2,
            relief="solid",
            height=40)
        # Prevent shrinking to fit children
        step_nav_frame.pack_propagate(False)
        step_nav_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Navigation controls
        ttk.Button(
            step_nav_frame,
            text="◀◀ First",
            command=self.show_first_step).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            step_nav_frame,
            text="◀ Previous",
            command=self.show_previous_step).pack(
            side=tk.LEFT,
            padx=2)
        # tk.Label(step_nav_frame, text="DEBUG NAVIGATION BAR", bg="yellow", fg="black", font=("Arial", 16)).pack(fill=tk.BOTH, expand=True)

        self.step_info_label = ttk.Label(step_nav_frame, text="Step 0 of 0")
        self.step_info_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            step_nav_frame,
            text="Next ▶",
            command=self.show_next_step).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            step_nav_frame,
            text="Last ▶▶",
            command=self.show_last_step).pack(
            side=tk.LEFT,
            padx=2)

        # Step selection
        ttk.Label(
            step_nav_frame,
            text="Go to step:").pack(
            side=tk.LEFT,
            padx=(
                20,
                5))
        self.step_select_var = tk.StringVar(value="0")
        self.step_select_spinbox = ttk.Spinbox(
            step_nav_frame,
            from_=0,
            to=0,
            width=5,
            textvariable=self.step_select_var,
            command=self.show_selected_step)
        self.step_select_spinbox.pack(side=tk.LEFT, padx=2)

        # Go to step controls - FIX THE IMPLEMENTATION
        step_frame = ttk.Frame(control_frame)
        step_frame.pack(fill=tk.X, pady=5)

        ttk.Label(step_frame, text="Go to Step:").pack(side=tk.LEFT)
        self.goto_step_var = tk.StringVar()
        self.goto_step_entry = ttk.Entry(
            step_frame, textvariable=self.goto_step_var, width=10)
        self.goto_step_entry.pack(side=tk.LEFT, padx=5)

        # Bind Enter key to go to step function
        self.goto_step_entry.bind(
            '<Return>', lambda event: self.goto_crash_step())

        self.goto_step_btn = ttk.Button(
            step_frame, text="Go", command=self.goto_crash_step)
        self.goto_step_btn.pack(side=tk.LEFT, padx=5)

        # Show all steps button
        ttk.Button(
            step_nav_frame,
            text="Show All Steps",
            command=self.show_all_steps_grid).pack(
            side=tk.RIGHT,
            padx=2)

        # Initialize step tracking
        self.current_step = 0
        self.total_steps = 0

    def goto_crash_step(self):
        """Navigate to specific step in crash optimization"""
        try:
            target_step = int(self.goto_step_var.get())

            # Check if we have crash log data
            if not hasattr(self, 'crash_log') or not self.crash_log:
                messagebox.showerror(
                    "Error", "No crash optimization results available. Run optimization first.")
                return

            # Validate step number
            max_step = len(self.crash_log)
            if target_step < 0 or target_step > max_step:
                messagebox.showerror(
                    "Error", f"Step must be between 0 and {max_step}")
                return

            # Update the step slider to the target step
            if hasattr(self, 'crash_step_var'):
                self.crash_step_var.set(target_step)

            # Update the display for the target step
            self.show_crash_step(target_step)

            # Update step display
            if hasattr(self, 'crash_step_label'):
                self.crash_step_label.config(
                    text=f"Step: {target_step}/{max_step}")

            messagebox.showinfo("Success", f"Navigated to step {target_step}")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid step number")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to navigate to step: {
                    str(e)}")

    def run_crashing_optimization(self, max_budget=None):
        """Run project crashing optimization"""
        try:
            # Clear previous results
            self.crash_results_text.delete(1.0, tk.END)
            # self.fig_crashed.clear()

            # Clear previous crash steps
            for widget in self.step_display_frame.winfo_children():
                widget.destroy()

            # #  Force update navigation controls
            # if hasattr(self, 'step_info_label'):
            #     self.step_info_label.update()
            #     print(f"DEBUG: step_info_label visible: {self.step_info_label.winfo_viewable()}")
            #     print(f"DEBUG: step_info_label size: {self.step_info_label.winfo_width()}x{self.step_info_label.winfo_height()}")

            # Check if analysis has been performed
            if not self.current_analyzer or not hasattr(
                    self.current_analyzer, 'G') or self.current_analyzer.G is None:
                messagebox.showwarning(
                    "Warning", "Please run the analysis first.")
                return

            # Check if current analyzer supports crashing (support both CPM and PERT)
            # For PERT mode, we'll use expected_time as duration
            # if self.analysis_mode != 'deterministic':
            #     messagebox.showwarning("Warning", "Crashing analysis is only available for deterministic (CPM) data.")
            #     return

            # Get target duration
            try:
                target_duration = float(self.target_duration_var.get())
            except ValueError:
                messagebox.showerror(
                    "Error", "Target duration must be a number.")
                return

            # # DEBUG: tab information
            # print("DEBUG: Notebook tabs:")
            for i, tab_id in enumerate(self.notebook.tabs()):
                tab_text = self.notebook.tab(tab_id, "text")
                print(f"  Tab {i}: {tab_text}")

            # Find crashing tab by name instead of index
            for i, tab_id in enumerate(self.notebook.tabs()):
                if self.notebook.tab(
                        tab_id, "text") == "Crashing Optimization":
                    # # DEBUG: Switch to crashing tab
                    # print(f"DEBUG: Switching to crashing tab at index {i}")
                    self.notebook.select(i)
                    break

            # Get current project duration
            current_duration = max([self.current_analyzer.G.nodes[node]['EF']
                                   for node in self.current_analyzer.G.nodes()])

            if target_duration >= current_duration:
                messagebox.showinfo("Info", f"Target duration ({target_duration}) is already achieved or exceeded. "
                                    f"Current project duration is {current_duration}.")
                return

            # Get crash budget
            try:
                crash_budget = self.crash_budget_var.get()
                max_budget = float(
                    crash_budget) if crash_budget.strip() else None
            except ValueError:
                messagebox.showerror("Error", "Crash budget must be a number.")
                return

            # Run crashing optimization
            crashed_G, total_crash_cost, crash_log = self.current_analyzer.crash_project(
                target_duration, max_budget=max_budget)

            # Display crash results
            self.display_crash_results(
                crashed_G, total_crash_cost, crash_log, target_duration)

            # # Generate crashed network diagram
            # self.generate_crashed_network_diagram(crashed_G, crash_log)

            # Show crashing steps diagrams
            self.show_crashing_steps_diagrams(crashed_G, crash_log)

            messagebox.showinfo(
                "Success", "Project crashing completed successfully!")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Crashing optimization failed: {
                    str(e)}")

    def _get_normal_cost(self, activity_id):
        """Helper function to extract normal cost for an activity"""
        try:
            # First check if normal_cost exists in the graph nodes
            if (hasattr(self, 'current_analyzer') and
                hasattr(self.current_analyzer, 'G') and
                self.current_analyzer.G and
                    activity_id in self.current_analyzer.G.nodes):
                return float(
                    self.current_analyzer.G.nodes[activity_id].get(
                        'normal_cost', 0))
            return 0.0
        except (ValueError, TypeError, KeyError):
            return 0.0

    def display_crash_results(
            self,
            crashed_G,
            total_crash_cost,
            crash_log,
            target_duration):
        """Display crash log and summary in the crashing tab with comprehensive cost tracking"""
        self.crash_results_text.delete(1.0, tk.END)
        lines = []
        lines.append("CRASHING OPTIMIZATION LOG\n" + "=" * 40)

        # Show initial project duration
        initial_duration = max([self.current_analyzer.G.nodes[node]['EF']
                               for node in self.current_analyzer.G.nodes()])
        lines.append(f"Initial Project Duration: {initial_duration}")
        lines.append(f"Target Duration: {target_duration}")
        lines.append("-" * 40)

        # Enhanced cost tracking
        cumulative_crash_cost = 0.0
        cumulative_step_cost = 0.0
        total_normal_cost = 0.0

        # Show each crash step with comprehensive cost breakdown
        for entry in crash_log:
            activity_id = entry['activity']
            crash_cost = float(entry['crash_cost'])
            normal_cost = self._get_normal_cost(activity_id)
            step_cost = crash_cost + normal_cost

            # Update cumulative costs BEFORE displaying
            cumulative_crash_cost += crash_cost
            cumulative_step_cost += step_cost
            total_normal_cost += normal_cost

            # Enhanced step display
            lines.append(
                f"Step {
                    entry['iteration']}: Activity {activity_id} crashed to duration {
                    entry['new_duration']}")
            lines.append(f"  - Crash Cost: ${crash_cost:,.2f}")
            lines.append(f"  - Normal Cost: ${normal_cost:,.2f}")
            lines.append(f"  - Step Cost: ${step_cost:,.2f}")
            lines.append(
                f"  - Cumulative Crash: ${cumulative_crash_cost:,.2f}")
            lines.append(f"  - Cumulative Step: ${cumulative_step_cost:,.2f}")
            lines.append("")

        lines.append("-" * 40)
        lines.append("-" * 40)

        # Enhanced cost summary
        total_step_cost = cumulative_step_cost
        crash_percentage = (
            total_crash_cost /
            total_step_cost *
            100) if total_step_cost > 0 else 0
        normal_percentage = (
            total_normal_cost /
            total_step_cost *
            100) if total_step_cost > 0 else 0

        lines.append("COST BREAKDOWN SUMMARY:")
        lines.append(f"Total Crash Cost: ${total_crash_cost:,.2f}")
        lines.append(f"Total Normal Cost: ${total_normal_cost:,.2f}")
        lines.append(f"Total Step Cost: ${total_step_cost:,.2f}")
        lines.append(
            f"Cost Composition: {
                crash_percentage:.1f}% Crash, {
                normal_percentage:.1f}% Normal")
        lines.append("")

        # Calculate final project duration
        new_duration = max([crashed_G.nodes[node]['EF']
                           for node in crashed_G.nodes()])
        lines.append(f"Final Project Duration: {new_duration}")
        lines.append(
            f"Duration Reduction: {
                initial_duration -
                new_duration} units")

        # Cost efficiency metrics
        duration_reduction = initial_duration - new_duration
        if duration_reduction > 0:
            cost_per_unit_reduction = total_crash_cost / duration_reduction
            step_cost_per_unit_reduction = total_step_cost / duration_reduction
            lines.append(
                f"Crash Cost per Unit Reduction: ${
                    cost_per_unit_reduction:,.2f}")
            lines.append(
                f"Total Cost per Unit Reduction: ${
                    step_cost_per_unit_reduction:,.2f}")

        lines.append("")

        # Show success/failure status
        if new_duration <= target_duration:
            lines.append(f"✓ Target duration achieved!")
        else:
            lines.append(
                f"✗ Target duration not achieved (stopped at {new_duration})")

        # Show new critical path
        critical_activities = [node for node in crashed_G.nodes(
        ) if crashed_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]
        lines.append(
            f"Final Critical Path: {
                ' -> '.join(critical_activities)}")

        # Enhanced crashed activities summary with cost details
        crashed_activities = {}
        for entry in crash_log:
            activity = entry['activity']
            if activity not in crashed_activities:
                crashed_activities[activity] = {
                    'original_duration': entry.get(
                        'original_duration',
                        self.current_analyzer.G.nodes[activity]['duration']),
                    'final_duration': entry['new_duration'],
                    'total_crash_cost': 0,
                    'total_normal_cost': 0,
                    'total_step_cost': 0,
                    'crash_count': 0}
            crashed_activities[activity]['final_duration'] = entry['new_duration']
            crashed_activities[activity]['total_crash_cost'] += entry['crash_cost']
            crashed_activities[activity]['total_normal_cost'] += self._get_normal_cost(
                activity)
            crashed_activities[activity]['total_step_cost'] += (
                entry['crash_cost'] + self._get_normal_cost(activity))
            crashed_activities[activity]['crash_count'] += 1

        if crashed_activities:
            lines.append("\nCRASHED ACTIVITIES SUMMARY:")
            lines.append("-" * 50)
            for activity, info in crashed_activities.items():
                reduction = info['original_duration'] - info['final_duration']
                lines.append(f"Activity {activity}: {info['original_duration']} → {info['final_duration']} "
                             f"({reduction} units, {info['crash_count']} steps)")
                lines.append(
                    f"  - Crash Cost: ${info['total_crash_cost']:,.2f}")
                lines.append(
                    f"  - Normal Cost: ${info['total_normal_cost']:,.2f}")
                lines.append(
                    f"  - Total Cost: ${info['total_step_cost']:,.2f}")
                lines.append("")

        self.crash_results_text.insert(1.0, "\n".join(lines))

    def show_crashing_steps_diagrams(self, crashed_G, crash_log):
        """Prepare step diagrams for navigation display."""
        # Clear previous step data
        self.step_graphs = []
        self.current_step = 0

        # Prepare all step graphs
        G = self.current_analyzer.G.copy()  # Start with original graph

        # Add initial state (before any crashing)
        G_initial = self.current_analyzer.forward_pass(G.copy())
        G_initial = self.current_analyzer.backward_pass(G_initial)
        G_initial = self.current_analyzer.calculate_float(G_initial)
        self.step_graphs.append((0, "Initial", None, G_initial))

        # Apply crashes incrementally
        for i, entry in enumerate(crash_log):
            # Apply this crash to the current graph
            G.nodes[entry['activity']]['duration'] = entry['new_duration']
            G = self.current_analyzer.forward_pass(G)
            G = self.current_analyzer.backward_pass(G)
            G = self.current_analyzer.calculate_float(G)
            self.step_graphs.append(
                (i + 1, entry['activity'], entry['new_duration'], G.copy()))

        self.total_steps = len(self.step_graphs)

        # # DEBUG output to verify steps
        # print(f"DEBUG: Total step graphs created: {self.total_steps}")
        # print(f"DEBUG: Crash log length: {len(crash_log)}")

        # Update spinbox range
        self.step_select_spinbox.config(to=self.total_steps - 1)

        # Show initial step
        self.show_step(0)

    def show_crash_step(self, step_value):
        """Show specific crash optimization step"""
        try:
            step = int(step_value)

            if not hasattr(self, 'crash_log') or not self.crash_log:
                return

            # Clear current display
            for widget in self.crash_results_frame.winfo_children():
                widget.destroy()

            # Create main container
            main_frame = ttk.Frame(self.crash_results_frame)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            if step == 0:
                # Show initial state (before any crashing)
                ttk.Label(main_frame, text="Initial Project State (Step 0)",
                          font=('Arial', 12, 'bold')).pack(pady=5)

                # Show original project info
                if hasattr(self, 'G') and self.G:
                    original_duration = max(
                        [self.G.nodes[node]['EF'] for node in self.G.nodes()])
                    ttk.Label(
                        main_frame,
                        text=f"Original Duration: {original_duration}").pack()
                    ttk.Label(main_frame,
                              text="No activities crashed yet").pack()
            else:
                # Show specific crash step
                if step <= len(self.crash_log):
                    crash_entry = self.crash_log[step - 1]

                    ttk.Label(main_frame, text=f"Crash Step {step}",
                              font=('Arial', 12, 'bold')).pack(pady=5)

                    # Show crash details
                    info_frame = ttk.LabelFrame(
                        main_frame, text="Crash Details")
                    info_frame.pack(fill=tk.X, pady=5)

                    ttk.Label(
                        info_frame, text=f"Activity Crashed: {
                            crash_entry['activity']}").pack(
                        anchor=tk.W)
                    ttk.Label(
                        info_frame, text=f"Crash Cost: ${
                            crash_entry['crash_cost']:,.2f}").pack(
                        anchor=tk.W)
                    ttk.Label(
                        info_frame, text=f"New Duration: {
                            crash_entry['new_duration']}").pack(
                        anchor=tk.W)
                    ttk.Label(
                        info_frame, text=f"Original Duration: {
                            crash_entry['original_duration']}").pack(
                        anchor=tk.W)

                    # Calculate cumulative cost up to this step
                    cumulative_cost = sum([entry['crash_cost']
                                          for entry in self.crash_log[:step]])
                    ttk.Label(
                        info_frame,
                        text=f"Cumulative Cost: ${
                            cumulative_cost:,.2f}").pack(
                        anchor=tk.W)

            # Update step counter
            max_steps = len(self.crash_log)
            if hasattr(self, 'crash_step_label'):
                self.crash_step_label.config(text=f"Step: {step}/{max_steps}")

        except Exception as e:
            print(f"Error showing crash step: {e}")

    def show_rcps_crash_step(self, step_value):
        """Show specific RCPS crash optimization step"""
        try:
            step = int(step_value)

            if not hasattr(self, 'rcps_crash_log') or not self.rcps_crash_log:
                return

            # Clear current display
            for widget in self.rcps_crash_results_frame.winfo_children():
                widget.destroy()

            # Create main container
            main_frame = ttk.Frame(self.rcps_crash_results_frame)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            if step == 0:
                # Show initial state (before any crashing)
                ttk.Label(
                    main_frame,
                    text="Initial RCPS Project State (Step 0)",
                    font=(
                        'Arial',
                        12,
                        'bold')).pack(
                    pady=5)

                ttk.Label(main_frame, text="No activities crashed yet").pack()
            else:
                # Show specific crash step
                if step <= len(self.rcps_crash_log):
                    crash_entry = self.rcps_crash_log[step - 1]

                    ttk.Label(main_frame, text=f"RCPS Crash Step {step}",
                              font=('Arial', 12, 'bold')).pack(pady=5)

                    # Show crash details
                    info_frame = ttk.LabelFrame(
                        main_frame, text="RCPS Crash Details")
                    info_frame.pack(fill=tk.X, pady=5)

                    ttk.Label(
                        info_frame, text=f"Activity Crashed: {
                            crash_entry['activity']}").pack(
                        anchor=tk.W)
                    ttk.Label(
                        info_frame, text=f"Crash Cost: ${
                            crash_entry['crash_cost']:,.2f}").pack(
                        anchor=tk.W)
                    ttk.Label(
                        info_frame, text=f"New Duration: {
                            crash_entry['new_duration']}").pack(
                        anchor=tk.W)
                    ttk.Label(
                        info_frame, text=f"Original Duration: {
                            crash_entry['original_duration']}").pack(
                        anchor=tk.W)

                    # Show RCPS-specific info if available
                    if 'project_duration_reduction' in crash_entry:
                        ttk.Label(
                            info_frame, text=f"Project Duration Reduction: {
                                crash_entry['project_duration_reduction']}").pack(
                            anchor=tk.W)
                    if 'resulting_project_duration' in crash_entry:
                        ttk.Label(
                            info_frame, text=f"Resulting Project Duration: {
                                crash_entry['resulting_project_duration']}").pack(
                            anchor=tk.W)

                    # Calculate cumulative cost up to this step
                    cumulative_cost = sum([entry['crash_cost']
                                          for entry in self.rcps_crash_log[:step]])
                    ttk.Label(
                        info_frame,
                        text=f"Cumulative Cost: ${
                            cumulative_cost:,.2f}").pack(
                        anchor=tk.W)

            # Update step counter
            max_steps = len(self.rcps_crash_log)
            if hasattr(self, 'rcps_crash_step_label'):
                self.rcps_crash_step_label.config(
                    text=f"Step: {step}/{max_steps}")

        except Exception as e:
            print(f"Error showing RCPS crash step: {e}")

    def _draw_network_diagram_on_ax(self, ax, G):
        """Draw a CPM network diagram on the given matplotlib axis."""
        pos = {}
        generations = list(nx.topological_generations(G))
        for i, gen in enumerate(generations):
            sorted_gen = sorted(gen)
            for j, node in enumerate(sorted_gen):
                y_pos = (j - len(sorted_gen) / 2 + 0.5) * 4
                pos[node] = (i * 3, y_pos)

        node_radius = 0.4

        # Draw edges
        for u, v in G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx = x2 - x1
            dy = y2 - y1
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
                start_x = x1 + node_radius * dx_norm
                start_y = y1 + node_radius * dy_norm
                end_x = x2 - node_radius * dx_norm
                end_y = y2 - node_radius * dy_norm
                ax.annotate(
                    "", xy=(
                        end_x, end_y), xytext=(
                        start_x, start_y), arrowprops=dict(
                        arrowstyle="->", color="black", lw=1.5))

        # Draw nodes
        critical_activities = [
            node for node in G.nodes() if G.nodes[node]['float'] == 0 and node not in [
                'START', 'END']]
        for node in G.nodes():
            x, y = pos[node]
            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'
            elif node in critical_activities:
                color = 'red'
            else:
                color = 'lightblue'
            circle = plt.Circle(
                (x,
                 y),
                node_radius,
                fill=True,
                color=color,
                alpha=0.7,
                edgecolor='black',
                linewidth=1.5)
            ax.add_patch(circle)
            if node in ['START', 'END']:
                display_text = 'Start' if node == 'START' else 'End'
                ax.text(x, y, display_text, ha='center', va='center',
                        fontsize=10, fontweight='bold')
            else:
                ax.plot([x - node_radius, x + node_radius], [y, y],
                        color='black', linewidth=1.2)
                ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                        fontsize=10, fontweight='bold')
                ax.text(x, y - node_radius / 2, str(G.nodes[node]['duration']),
                        ha='center', va='center', fontsize=9)

        ax.set_axis_off()
        ax.set_aspect('equal')

    def _draw_network_diagram_on_ax_small(self, ax, G):
        """Draw a smaller CPM network diagram on the given matplotlib axis."""
        pos = {}
        generations = list(nx.topological_generations(G))
        for i, gen in enumerate(generations):
            sorted_gen = sorted(gen)
            for j, node in enumerate(sorted_gen):
                y_pos = (j - len(sorted_gen) / 2 + 0.5) * 2  # Reduced spacing
                pos[node] = (i * 2, y_pos)  # Reduced spacing

        node_radius = 0.3  # Smaller radius

        # Draw edges
        for u, v in G.edges():
            x1, y1 = pos[u]
            x2, y2 = pos[v]
            dx = x2 - x1
            dy = y2 - y1
            distance = (dx ** 2 + dy ** 2) ** 0.5
            if distance > 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
                start_x = x1 + node_radius * dx_norm
                start_y = y1 + node_radius * dy_norm
                end_x = x2 - node_radius * dx_norm
                end_y = y2 - node_radius * dy_norm
                ax.annotate(
                    "", xy=(
                        end_x, end_y), xytext=(
                        start_x, start_y), arrowprops=dict(
                        arrowstyle="->", color="black", lw=1))

        # Draw nodes
        critical_activities = [
            node for node in G.nodes() if G.nodes[node]['float'] == 0 and node not in [
                'START', 'END']]
        for node in G.nodes():
            x, y = pos[node]
            if node == 'START':
                color = 'lightgreen'
            elif node == 'END':
                color = 'orange'
            elif node in critical_activities:
                color = 'red'
            else:
                color = 'lightblue'
            circle = plt.Circle(
                (x,
                 y),
                node_radius,
                fill=True,
                color=color,
                alpha=0.7,
                edgecolor='black',
                linewidth=1)
            ax.add_patch(circle)
            if node in ['START', 'END']:
                display_text = 'Start' if node == 'START' else 'End'
                ax.text(x, y, display_text, ha='center', va='center',
                        fontsize=7, fontweight='bold')
            else:
                ax.plot([x - node_radius, x + node_radius], [y, y],
                        color='black', linewidth=0.8)
                ax.text(x, y + node_radius / 2, node, ha='center', va='center',
                        fontsize=7, fontweight='bold')
                ax.text(x, y - node_radius / 2, str(G.nodes[node]['duration']),
                        ha='center', va='center', fontsize=6)

        ax.set_axis_off()
        ax.set_aspect('equal')

    def show_step(self, step_index):
        """Display a specific step diagram."""
        if 0 <= step_index < len(self.step_graphs):
            self.current_step = step_index
            step_num, activity, new_duration, G_step = self.step_graphs[step_index]

            # # DEBUG: Check graph integrity
            # print(f"DEBUG: Showing step {step_index}")
            # print(f"DEBUG: Graph has {len(G_step.nodes())} nodes and {len(G_step.edges())} edges")
            # print(f"DEBUG: Edges: {list(G_step.edges())}")

            # Clear previous display
            for widget in self.step_display_frame.winfo_children():
                widget.destroy()

            # Create matplotlib figure for this step
            fig = plt.Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)

            self._draw_network_diagram_on_ax(ax, G_step)

            # Set title
            if step_num == 0:
                ax.set_title("Initial Network", fontsize=14, fontweight='bold')
            else:
                ax.set_title(
                    f"Step {step_num}: Activity {activity} crashed to {new_duration}",
                    fontsize=14,
                    fontweight='bold')

            # Display the figure
            canvas = FigureCanvasTkAgg(fig, self.step_display_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()

            # Update step info
            self.step_info_label.config(
                text=f"Step {step_index} of {
                    self.total_steps - 1}")
            self.step_select_var.set(str(step_index))

            # # Debug info to verify step data
            # print(f"DEBUG: Updated step info - Current: {step_index}, Total steps: {self.total_steps}")

    def show_first_step(self):
        """Show the first step."""
        self.show_step(0)

    def show_previous_step(self):
        """Show the previous step."""
        if self.current_step > 0:
            self.show_step(self.current_step - 1)

    def show_next_step(self):
        """Show the next step."""
        if self.current_step < self.total_steps - 1:
            self.show_step(self.current_step + 1)

    def show_last_step(self):
        """Show the last step."""
        if self.total_steps > 0:
            self.show_step(self.total_steps - 1)

    def show_selected_step(self):
        """Show the step selected in the spinbox."""
        try:
            step_index = int(self.step_select_var.get())
            self.show_step(step_index)
        except ValueError:
            pass

    def show_all_steps_grid(self):
        """Show all steps in a grid layout in a new window."""
        if not self.step_graphs:
            messagebox.showwarning("Warning", "No steps to display.")
            return

        # Create a new window for the grid view
        grid_window = tk.Toplevel(self.root)
        grid_window.title("All Crashing Steps")
        grid_window.geometry("1200x800")

        # Create scrollable frame
        canvas = tk.Canvas(grid_window)
        scrollbar = ttk.Scrollbar(
            grid_window,
            orient="vertical",
            command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create grid of step diagrams
        cols = 3  # 3 diagrams per row
        step_images = []

        for idx, (step_num, activity, new_duration,
                  G_step) in enumerate(self.step_graphs):
            fig = plt.Figure(figsize=(4, 3))
            ax = fig.add_subplot(111)

            self._draw_network_diagram_on_ax_small(ax, G_step)

            if step_num == 0:
                ax.set_title("Initial Network", fontsize=10, fontweight='bold')
            else:
                ax.set_title(f"Step {step_num}: {activity} → {new_duration}",
                             fontsize=10, fontweight='bold')

            # Convert to image
            canvas_agg = agg.FigureCanvasAgg(fig)
            canvas_agg.draw()
            buf = canvas_agg.buffer_rgba()
            img = Image.frombuffer(
                "RGBA",
                canvas_agg.get_width_height(),
                buf,
                "raw",
                "RGBA",
                0,
                1)
            tk_img = ImageTk.PhotoImage(img)
            step_images.append(tk_img)

            # Place in grid
            row = idx // cols
            col = idx % cols
            lbl = tk.Label(scrollable_frame, image=tk_img)
            lbl.grid(row=row, column=col, padx=5, pady=5)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store images to prevent garbage collection
        grid_window.step_images = step_images

    ##########################################################################

    def create_rcps_crashing_tab(self):
        """Create the RCPS Crashing Optimization tab with navigation controls."""
        rcps_crashing_frame = ttk.Frame(self.notebook)
        self.notebook.add(rcps_crashing_frame, text="RCPS Crashing")

        # Control frame
        control_frame = ttk.Frame(rcps_crashing_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            control_frame,
            text="Target Duration:").pack(
            side=tk.LEFT,
            padx=(
                0,
                5))
        self.rcps_target_duration_var = tk.StringVar(value="10")
        target_entry = ttk.Entry(
            control_frame,
            textvariable=self.rcps_target_duration_var,
            width=10)
        target_entry.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Button(
            control_frame,
            text="Run RCPS Crashing",
            command=self.run_rcps_crashing_optimization).pack(
            side=tk.LEFT)

        ttk.Label(
            control_frame,
            text="Crash Budget:").pack(
            side=tk.LEFT,
            padx=(
                0,
                5))
        self.rcps_crash_budget_var = tk.StringVar(value="")
        budget_entry = ttk.Entry(
            control_frame,
            textvariable=self.rcps_crash_budget_var,
            width=10)
        budget_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Results frame
        results_frame = ttk.Frame(rcps_crashing_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        # Text output for crash log/results
        self.rcps_crash_results_text = scrolledtext.ScrolledText(
            results_frame, font=("Courier", 10), height=8)
        self.rcps_crash_results_text.pack(fill=tk.BOTH, expand=True)

        # # Matplotlib figure for crashed network
        # self.fig_rcps_crashed = plt.Figure(figsize=(12, 6))
        # self.canvas_rcps_crashed = FigureCanvasTkAgg(self.fig_rcps_crashed, results_frame)
        # self.canvas_rcps_crashed.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Step navigation frame (same as regular crashing tab)
        rcps_step_nav_frame = ttk.Frame(results_frame)
        rcps_step_nav_frame.pack(fill=tk.X, pady=(5, 0))

        # Navigation controls
        ttk.Button(
            rcps_step_nav_frame,
            text="◀◀ First",
            command=self.show_rcps_first_step).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            rcps_step_nav_frame,
            text="◀ Previous",
            command=self.show_rcps_previous_step).pack(
            side=tk.LEFT,
            padx=2)

        self.rcps_step_info_label = ttk.Label(
            rcps_step_nav_frame, text="Step 0 of 0")
        self.rcps_step_info_label.pack(side=tk.LEFT, padx=10)

        ttk.Button(
            rcps_step_nav_frame,
            text="Next ▶",
            command=self.show_rcps_next_step).pack(
            side=tk.LEFT,
            padx=2)
        ttk.Button(
            rcps_step_nav_frame,
            text="Last ▶▶",
            command=self.show_rcps_last_step).pack(
            side=tk.LEFT,
            padx=2)

        # Step selection
        ttk.Label(
            rcps_step_nav_frame,
            text="Go to step:").pack(
            side=tk.LEFT,
            padx=(
                20,
                5))
        self.rcps_step_select_var = tk.StringVar(value="0")
        self.rcps_step_select_spinbox = ttk.Spinbox(
            rcps_step_nav_frame,
            from_=0,
            to=0,
            width=5,
            textvariable=self.rcps_step_select_var,
            command=self.show_rcps_selected_step)
        self.rcps_step_select_spinbox.pack(side=tk.LEFT, padx=2)

        # Go to step controls - FIX THE IMPLEMENTATION
        step_frame = ttk.Frame(control_frame)
        step_frame.pack(fill=tk.X, pady=5)

        ttk.Label(step_frame, text="Go to Step:").pack(side=tk.LEFT)
        self.rcps_goto_step_var = tk.StringVar()
        self.rcps_goto_step_entry = ttk.Entry(
            step_frame, textvariable=self.rcps_goto_step_var, width=10)
        self.rcps_goto_step_entry.pack(side=tk.LEFT, padx=5)

        # Bind Enter key to go to step function
        self.rcps_goto_step_entry.bind(
            '<Return>', lambda event: self.goto_rcps_crash_step())

        self.rcps_goto_step_btn = ttk.Button(
            step_frame, text="Go", command=self.goto_rcps_crash_step)
        self.rcps_goto_step_btn.pack(side=tk.LEFT, padx=5)

        # Show all steps button
        ttk.Button(
            rcps_step_nav_frame,
            text="Show All Steps",
            command=self.show_rcps_all_steps_grid).pack(
            side=tk.RIGHT,
            padx=2)

        # Step display area
        self.rcps_step_display_frame = ttk.Frame(results_frame)
        self.rcps_step_display_frame.pack(fill=tk.BOTH, expand=True)

        # Initialize step tracking for RCPS
        self.rcps_current_step = 0
        self.rcps_total_steps = 0
        self.rcps_step_graphs = []

    def goto_rcps_crash_step(self):
        """Navigate to specific step in RCPS crash optimization"""
        try:
            target_step = int(self.rcps_goto_step_var.get())

            # Check if we have RCPS crash log data
            if not hasattr(self, 'rcps_crash_log') or not self.rcps_crash_log:
                messagebox.showerror(
                    "Error",
                    "No RCPS crash optimization results available. Run optimization first.")
                return

            # Validate step number
            max_step = len(self.rcps_crash_log)
            if target_step < 0 or target_step > max_step:
                messagebox.showerror(
                    "Error", f"Step must be between 0 and {max_step}")
                return

            # Update the step slider to the target step
            if hasattr(self, 'rcps_crash_step_var'):
                self.rcps_crash_step_var.set(target_step)

            # Update the display for the target step
            self.show_rcps_crash_step(target_step)

            # Update step display
            if hasattr(self, 'rcps_crash_step_label'):
                self.rcps_crash_step_label.config(
                    text=f"Step: {target_step}/{max_step}")

            messagebox.showinfo("Success", f"Navigated to step {target_step}")

        except ValueError:
            messagebox.showerror("Error", "Please enter a valid step number")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to navigate to step: {
                    str(e)}")

    # without debugging points

    def run_rcps_crashing_optimization(self):
        """
        Run crashing optimization using RCPS scheduling integrated into the optimization loop.
        """
        try:
            # Clear previous results
            self.rcps_crash_results_text.delete(1.0, tk.END)

            for widget in self.rcps_step_display_frame.winfo_children():
                widget.destroy()

            # Check if RCPS analysis has been performed first
            if not hasattr(
                    self,
                    'last_rcps_table') or self.last_rcps_table is None:
                messagebox.showwarning(
                    "Warning", "Please run the RCPS scheduling first in the RCPS tab.")
                return

            # Check if CPM analysis has been performed
            if not hasattr(
                    self.current_analyzer,
                    'G') or self.current_analyzer.G is None:
                messagebox.showwarning(
                    "Warning", "Please run the CPM analysis first.")
                return

            # Get target duration and validate
            try:
                target_duration = float(self.rcps_target_duration_var.get())
            except ValueError:
                messagebox.showerror(
                    "Error", "Target duration must be a number.")
                return

            # Get crash budget
            try:
                crash_budget = self.rcps_crash_budget_var.get()
                max_budget = float(
                    crash_budget) if crash_budget.strip() else None
            except ValueError:
                messagebox.showerror("Error", "Crash budget must be a number.")
                return

            # Get resource limit and priority rule from RCPS tab
            try:
                resource_limit = int(self.resource_limit_var.get())
            except ValueError:
                messagebox.showerror(
                    "Error", "Please set a valid resource limit in the RCPS tab first.")
                return

            priority_rule = self.priority_rule_var.get()

            # Create temporary graph with RCPS data, don't modify original
            rcps_updated_graph = self.update_cpm_graph_with_rcps()

            if rcps_updated_graph is None:
                messagebox.showerror(
                    "Error", "Failed to create RCPS-updated graph.")
                return

            # Get RCPS duration after update
            rcps_duration = max([rcps_updated_graph.nodes[node]['EF']
                                for node in rcps_updated_graph.nodes()])

            # Validate target duration against RCPS duration (not CPM duration)
            if target_duration >= rcps_duration:
                messagebox.showinfo("Info",
                                    f"Target duration ({target_duration}) is already achieved or exceeded.\n"
                                    f"Current RCPS project duration is {rcps_duration}.\n"
                                    f"Please set a target duration less than {rcps_duration}.")
                return

            # Use temporary graph for RCPS crashing, preserve original
            original_analyzer_graph = self.current_analyzer.G  # Store original
            self.current_analyzer.G = rcps_updated_graph      # Temporarily use RCPS graph

            try:
                # Run RCPS-integrated crashing optimization
                crashed_G, total_crash_cost, crash_log = self.current_analyzer.crash_project_with_rcps(
                    target_duration, resource_limit, priority_rule, max_budget=max_budget)

                # Display results and step diagrams
                self.display_rcps_crashing_results(
                    crashed_G, total_crash_cost, crash_log, target_duration)
                self.show_rcps_crashing_steps_diagrams(
                    rcps_updated_graph, crash_log)  # Use RCPS base graph

            finally:
                # Always restore the original graph
                self.current_analyzer.G = original_analyzer_graph

            # Switch to RCPS Crashing tab
            for i, tab_id in enumerate(self.notebook.tabs()):
                if self.notebook.tab(tab_id, "text") == "RCPS Crashing":
                    self.notebook.select(i)
                    break

            messagebox.showinfo(
                "Success", "RCPS Crashing completed successfully!")

        except Exception as e:
            # Make sure to restore original graph even if there's an error
            if 'original_analyzer_graph' in locals():
                self.current_analyzer.G = original_analyzer_graph
            messagebox.showerror("Error", f"RCPS Crashing failed: {str(e)}")
            import traceback
            traceback.print_exc()

    def display_rcps_crashing_results(
            self,
            crashed_G,
            total_crash_cost,
            crash_log,
            target_duration):
        """Display crash log and summary in the RCPS Crashing tab with enhanced cost tracking."""
        self.rcps_crash_results_text.delete(1.0, tk.END)
        lines = []
        lines.append("RCPS CRASHING OPTIMIZATION LOG")
        lines.append("=" * 40)

        # CRITICAL FIX: Get initial duration from RCPS (first crash log entry
        # or current graph)
        if crash_log and 'resulting_project_duration' in crash_log[0]:
            # Get initial duration from first crash log entry
            # The initial duration should be the "before" state of the first
            # crash
            first_entry = crash_log[0]
            if 'project_duration_reduction' in first_entry and 'resulting_project_duration' in first_entry:
                initial_duration = first_entry['resulting_project_duration'] + \
                    first_entry['project_duration_reduction']
            else:
                # Fallback: calculate from RCPS data
                initial_duration = max([self.current_analyzer.G.nodes[node]['EF']
                                       for node in self.current_analyzer.G.nodes()])
        else:
            # Fallback: get from current graph state
            initial_duration = max([self.current_analyzer.G.nodes[node]['EF']
                                   for node in self.current_analyzer.G.nodes()])

        lines.append(f"Initial Project Duration: {initial_duration}")
        lines.append(f"Target Duration: {target_duration}")
        lines.append("-" * 40)

        # Enhanced step-by-step cost tracking
        cumulative_crash_cost = 0
        cumulative_step_cost = 0
        total_normal_cost = 0
        total_crash_cost = 0

        for i, entry in enumerate(crash_log, 1):
            crash_cost = entry['crash_cost']
            normal_cost = self._get_normal_cost(entry['activity'])
            step_cost = crash_cost + normal_cost

            # Update cumulative costs
            cumulative_crash_cost += crash_cost
            cumulative_step_cost += step_cost
            total_crash_cost += crash_cost
            total_normal_cost += normal_cost

            lines.append(
                f"Step {i}: Activity {
                    entry['activity']} crashed to duration {
                    entry['new_duration']}")
            lines.append(f"  - Crash Cost: ${crash_cost:,.2f}")
            lines.append(f"  - Normal Cost: ${normal_cost:,.2f}")
            lines.append(f"  - Step Cost: ${step_cost:,.2f}")
            lines.append(
                f"  - Cumulative Crash: ${cumulative_crash_cost:,.2f}")
            lines.append(f"  - Cumulative Step: ${cumulative_step_cost:,.2f}")
            lines.append("")

        lines.append("-" * 40)

        # Enhanced cost summary
        total_step_cost = cumulative_step_cost
        crash_percentage = (
            total_crash_cost /
            total_step_cost *
            100) if total_step_cost > 0 else 0
        normal_percentage = (
            total_normal_cost /
            total_step_cost *
            100) if total_step_cost > 0 else 0

        lines.append("COST BREAKDOWN SUMMARY:")
        lines.append(f"Total Crash Cost: ${total_crash_cost:,.2f}")
        lines.append(f"Total Normal Cost: ${total_normal_cost:,.2f}")
        lines.append(f"Total Step Cost: ${total_step_cost:,.2f}")
        lines.append(
            f"Cost Composition: {
                crash_percentage:.1f}% Crash, {
                normal_percentage:.1f}% Normal")
        lines.append("")

        # Calculate final project duration
        new_duration = max([crashed_G.nodes[node]['EF']
                           for node in crashed_G.nodes()])
        lines.append(f"Final Project Duration: {new_duration}")

        # CRITICAL FIX: Calculate duration reduction correctly
        duration_reduction = initial_duration - new_duration
        lines.append(f"Duration Reduction: {duration_reduction} units")

        # Cost efficiency metrics
        if duration_reduction > 0:
            cost_per_unit_reduction = total_crash_cost / duration_reduction
            step_cost_per_unit_reduction = total_step_cost / duration_reduction
            lines.append(
                f"Crash Cost per Unit Reduction: ${
                    cost_per_unit_reduction:,.2f}")
            lines.append(
                f"Total Cost per Unit Reduction: ${
                    step_cost_per_unit_reduction:,.2f}")

        lines.append("")

        # Show success/failure status
        if new_duration <= target_duration:
            lines.append(f"✓ Target duration achieved!")
        else:
            lines.append(
                f"✗ Target duration not achieved (stopped at {new_duration})")

        # CRITICAL FIX: Show RCPS critical path, not CPM critical path
        try:
            # Get resource limit and priority rule for final RCPS calculation
            resource_limit = int(self.resource_limit_var.get())
            priority_rule = self.priority_rule_var.get()

            # Generate final RCPS schedule to get correct critical path
            final_schedule = self.current_analyzer.generate_rcps_schedule_for_graph(
                crashed_G, resource_limit, priority_rule)
            rcps_critical_activities = final_schedule['critical_activities']

            if rcps_critical_activities:
                lines.append(
                    f"Final Critical Path: {
                        ' -> '.join(rcps_critical_activities)}")
            else:
                # Fallback to CPM critical path if RCPS calculation fails
                critical_activities = [node for node in crashed_G.nodes(
                ) if crashed_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]
                lines.append(
                    f"Final Critical Path: {
                        ' -> '.join(critical_activities)}")
        except Exception as e:
            print(f"DEBUG: Error calculating RCPS critical path: {e}")
            # Fallback to CPM critical path
            critical_activities = [node for node in crashed_G.nodes(
            ) if crashed_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]
            lines.append(
                f"Final Critical Path: {
                    ' -> '.join(critical_activities)}")

        # Enhanced crashed activities summary with cost details
        crashed_activities = {}
        for entry in crash_log:
            activity = entry['activity']
            if activity not in crashed_activities:
                crashed_activities[activity] = {
                    'original_duration': entry.get(
                        'original_duration',
                        self.current_analyzer.G.nodes[activity]['duration']),
                    'final_duration': entry['new_duration'],
                    'total_crash_cost': 0,
                    'total_normal_cost': 0,
                    'total_step_cost': 0,
                    'crash_count': 0}
            crashed_activities[activity]['final_duration'] = entry['new_duration']
            crashed_activities[activity]['total_crash_cost'] += entry['crash_cost']
            crashed_activities[activity]['total_normal_cost'] += self._get_normal_cost(
                activity)
            crashed_activities[activity]['total_step_cost'] += (
                entry['crash_cost'] + self._get_normal_cost(activity))
            crashed_activities[activity]['crash_count'] += 1

        if crashed_activities:
            lines.append("\nCRASHED ACTIVITIES SUMMARY:")
            lines.append("-" * 50)
            for activity, info in crashed_activities.items():
                reduction = info['original_duration'] - info['final_duration']
                lines.append(f"Activity {activity}: {info['original_duration']} → {info['final_duration']} "
                             f"({reduction} units, {info['crash_count']} steps)")
                lines.append(
                    f"  - Crash Cost: ${info['total_crash_cost']:,.2f}")
                lines.append(
                    f"  - Normal Cost: ${info['total_normal_cost']:,.2f}")
                lines.append(
                    f"  - Total Cost: ${info['total_step_cost']:,.2f}")
                lines.append("")

        self.rcps_crash_results_text.insert(1.0, "\n".join(lines))

    def show_rcps_crashing_steps_diagrams(self, base_G, crash_log):
        """Prepare step diagrams for RCPS navigation display."""

        # # DEBUG: Print input data information
        # print("\n==== DEBUG: RCPS Crashing Steps Input Data ====")
        # print(f"base_G type: {type(base_G)}")
        # print(f"base_G node count: {len(base_G.nodes())}")
        # print(f"base_G nodes: {list(base_G.nodes())}")
        # print(f"base_G edge count: {len(base_G.edges())}")
        # print(f"crash_log length: {len(crash_log)}")

        # if crash_log:
        #     print("First crash log entry:")
        #     for key, value in crash_log[0].items():
        #         print(f"  {key}: {value}")

        #     print("Sample node attributes from base_G:")
        #     sample_node = list(base_G.nodes())[0] if base_G.nodes() else None
        #     if sample_node:
        #         print(f"Node {sample_node} attributes:")
        #         for key, value in base_G.nodes[sample_node].items():
        #             print(f"  {key}: {value}")
        # print("===============================================\n")

        # Clear previous step data
        self.rcps_step_graphs = []
        self.rcps_current_step = 0

        # Prepare all step graphs
        G = base_G.copy()  # Start from the graph passed in

        # Add initial state (before any crashing)
        G_initial = self.current_analyzer.forward_pass(G.copy())
        G_initial = self.current_analyzer.backward_pass(G_initial)
        G_initial = self.current_analyzer.calculate_float(G_initial)
        self.rcps_step_graphs.append((0, "Initial", None, G_initial))

        # Apply crashes incrementally
        for i, entry in enumerate(crash_log):
            G = G.copy()
            G.nodes[entry['activity']]['duration'] = entry['new_duration']
            G = self.current_analyzer.forward_pass(G)
            G = self.current_analyzer.backward_pass(G)
            G = self.current_analyzer.calculate_float(G)
            self.rcps_step_graphs.append(
                (i + 1, entry['activity'], entry['new_duration'], G))

        self.rcps_total_steps = len(self.rcps_step_graphs)

        print(
            f"DEBUG: RCPS Total step graphs created: {
                self.rcps_total_steps}")
        print(f"DEBUG: RCPS Crash log length: {len(crash_log)}")

        # Update spinbox range
        self.rcps_step_select_spinbox.config(to=self.rcps_total_steps - 1)

        # Show initial step
        self.show_rcps_step(0)

    def show_rcps_step(self, step_index):
        """Display a specific RCPS step diagram."""
        if 0 <= step_index < len(self.rcps_step_graphs):
            self.rcps_current_step = step_index
            step_num, activity, new_duration, G_step = self.rcps_step_graphs[step_index]

            # Clear previous display
            for widget in self.rcps_step_display_frame.winfo_children():
                widget.destroy()

            # Create matplotlib figure for this step
            fig = plt.Figure(figsize=(10, 6))
            ax = fig.add_subplot(111)

            self._draw_network_diagram_on_ax(ax, G_step)

            # Set title
            if step_num == 0:
                ax.set_title(
                    "Initial RCPS Network",
                    fontsize=14,
                    fontweight='bold')
            else:
                ax.set_title(
                    f"RCPS Step {step_num}: Activity {activity} crashed to {new_duration}",
                    fontsize=14,
                    fontweight='bold')

            # Display the figure
            canvas = FigureCanvasTkAgg(fig, self.rcps_step_display_frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            canvas.draw()

            # Update step info
            self.rcps_step_info_label.config(
                text=f"Step {step_index} of {
                    self.rcps_total_steps - 1}")
            self.rcps_step_select_var.set(str(step_index))

    def show_rcps_first_step(self):
        """Show the first RCPS step."""
        self.show_rcps_step(0)

    def show_rcps_previous_step(self):
        """Show the previous RCPS step."""
        if self.rcps_current_step > 0:
            self.show_rcps_step(self.rcps_current_step - 1)

    def show_rcps_next_step(self):
        """Show the next RCPS step."""
        if self.rcps_current_step < self.rcps_total_steps - 1:
            self.show_rcps_step(self.rcps_current_step + 1)

    def show_rcps_last_step(self):
        """Show the last RCPS step."""
        if self.rcps_total_steps > 0:
            self.show_rcps_step(self.rcps_total_steps - 1)

    def show_rcps_selected_step(self):
        """Show the RCPS step selected in the spinbox."""
        try:
            step_index = int(self.rcps_step_select_var.get())
            self.show_rcps_step(step_index)
        except ValueError:
            pass

    def show_rcps_all_steps_grid(self):
        """Show all RCPS steps in a grid layout in a new window."""
        if not self.rcps_step_graphs:
            messagebox.showwarning("Warning", "No RCPS steps to display.")
            return

        # Create a new window for the grid view
        grid_window = tk.Toplevel(self.root)
        grid_window.title("All RCPS Crashing Steps")
        grid_window.geometry("1200x800")

        # Create scrollable frame
        canvas = tk.Canvas(grid_window)
        scrollbar = ttk.Scrollbar(
            grid_window,
            orient="vertical",
            command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create grid of step diagrams
        cols = 3  # 3 diagrams per row
        step_images = []

        for idx, (step_num, activity, new_duration,
                  G_step) in enumerate(self.rcps_step_graphs):
            fig = plt.Figure(figsize=(4, 3))
            ax = fig.add_subplot(111)

            self._draw_network_diagram_on_ax_small(ax, G_step)

            if step_num == 0:
                ax.set_title(
                    "Initial RCPS Network",
                    fontsize=10,
                    fontweight='bold')
            else:
                ax.set_title(
                    f"RCPS Step {step_num}: {activity} → {new_duration}",
                    fontsize=10,
                    fontweight='bold')

            # Convert to image
            canvas_agg = agg.FigureCanvasAgg(fig)
            canvas_agg.draw()
            buf = canvas_agg.buffer_rgba()
            img = Image.frombuffer(
                "RGBA",
                canvas_agg.get_width_height(),
                buf,
                "raw",
                "RGBA",
                0,
                1)
            tk_img = ImageTk.PhotoImage(img)
            step_images.append(tk_img)

            # Place in grid
            row = idx // cols
            col = idx % cols
            lbl = tk.Label(scrollable_frame, image=tk_img)
            lbl.grid(row=row, column=col, padx=5, pady=5)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Store images to prevent garbage collection
        grid_window.step_images = step_images

    # ======= PROBABILITY ANALYSIS METHODS =======

    def enable_probability_analysis(self):
        """Enable the probability analysis tab and controls"""
        self.probability_tab_enabled = True
        self.prob_status_label.config(
            text="Status: Enabled (Probabilistic data loaded)",
            foreground="green")
        self.calc_prob_btn.config(state=tk.NORMAL)
        self.calc_duration_btn.config(state=tk.NORMAL)
        self.target_duration_entry.config(state=tk.NORMAL)
        self.target_probability_entry.config(state=tk.NORMAL)

    def disable_probability_analysis(self):
        """Disable the probability analysis tab and controls"""
        self.probability_tab_enabled = False
        self.prob_status_label.config(
            text="Status: Disabled (Load probabilistic data first)",
            foreground="red")
        self.calc_prob_btn.config(state=tk.DISABLED)
        self.calc_duration_btn.config(state=tk.DISABLED)
        self.target_duration_entry.config(state=tk.DISABLED)
        self.target_probability_entry.config(state=tk.DISABLED)

        # Clear results
        self.prob_result_label.config(text="")
        self.duration_result_label.config(text="")

        # Clear plot
        if hasattr(self, 'fig_probability'):
            self.fig_probability.clear()
            self.canvas_probability.draw()

        # Clear statistics
        if hasattr(self, 'stats_text'):
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.config(state=tk.DISABLED)

    def update_probability_analysis(self):
        """Update probability analysis display with current PERT results"""
        if not self.probability_tab_enabled or self.analysis_mode != 'probabilistic':
            return

        # Get project statistics
        stats = self.pert_analyzer.get_project_statistics()
        if not stats:
            return

        # Update statistics display
        stats_text = f"Project Expected Duration: {
            stats['expected_duration']:.1f} time units\n"
        stats_text += f"Project Variance: {stats['variance']:.3f}\n"
        stats_text += f"Project Standard Deviation: {
            stats['std_deviation']:.3f}\n\n"

        stats_text += f"Critical Path: {' -> '.join(stats['critical_path'])}\n\n"

        stats_text += "Critical Activities Variance Breakdown:\n"
        stats_text += "-" * 40 + "\n"
        for activity_info in stats['critical_activities_variance']:
            stats_text += f"{
                activity_info['id']}: Variance = {
                activity_info['variance']:.3f}, "
            stats_text += f"Expected Time = {activity_info['expected_time']}\n"

        # Update display
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
        self.stats_text.config(state=tk.DISABLED)

        # Generate initial probability distribution plot
        self.plot_probability_distribution()

    def calculate_completion_probability(self):
        """Calculate probability of completing project within target duration"""
        try:
            target_duration = float(self.prob_target_duration_var.get())

            # Check if PERT analyzer exists and has data
            if not hasattr(self, 'pert_analyzer') or not self.pert_analyzer:
                raise ValueError("PERT analyzer not initialized")

            if not self.pert_analyzer.G:
                raise ValueError("No PERT analysis has been performed")

            probability = self.pert_analyzer.calculate_completion_probability(
                target_duration)

            result_text = f"Probability: {
                probability:.4f} ({
                probability * 100:.2f}%)"
            self.prob_result_label.config(text=result_text, foreground="blue")

            # Update plot with this calculation
            self.plot_probability_distribution(
                target_duration=target_duration,
                highlight_prob=probability)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid target duration: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def calculate_required_duration(self):
        """Calculate duration required for given probability"""
        try:
            target_probability = float(self.target_probability_var.get())

            if not (0 <= target_probability <= 1):
                raise ValueError("Probability must be between 0 and 1")

            duration = self.pert_analyzer.calculate_duration_for_probability(
                target_probability)

            result_text = f"Required Duration: {duration:.2f} time units"
            self.duration_result_label.config(
                text=result_text, foreground="blue")

            # Update plot with this calculation
            self.plot_probability_distribution(
                target_probability=target_probability,
                highlight_duration=duration)

        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Invalid probability value: {
                    str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Calculation failed: {str(e)}")

    def plot_probability_distribution(
            self,
            target_duration=None,
            highlight_prob=None,
            target_probability=None,
            highlight_duration=None):
        """Plot the normal distribution for project completion time"""
        if not self.probability_tab_enabled or self.analysis_mode != 'probabilistic':
            return

        try:
            # Clear previous plot
            self.fig_probability.clear()
            ax = self.fig_probability.add_subplot(111)

            # Get project statistics
            stats = self.pert_analyzer.get_project_statistics()
            if not stats:
                return

            expected_duration = stats['expected_duration']
            std_dev = stats['std_deviation']

            if std_dev == 0:
                # No variance - display message
                ax.text(
                    0.5,
                    0.5,
                    f"No variance in critical path.\nProject duration is exactly {expected_duration} time units.",
                    ha='center',
                    va='center',
                    transform=ax.transAxes,
                    fontsize=12)
                self.canvas_probability.draw()
                return

            # Create range for x-axis (±4 standard deviations)
            x_min = expected_duration - 4 * std_dev
            x_max = expected_duration + 4 * std_dev
            x = np.linspace(x_min, x_max, 1000)

            # Calculate normal distribution
            y = norm.pdf(x, expected_duration, std_dev)

            # Plot the distribution
            ax.plot(
                x,
                y,
                'b-',
                linewidth=2,
                label='Project Duration Distribution')
            ax.fill_between(x, y, alpha=0.3, color='lightblue')

            # Mark expected duration
            ax.axvline(
                expected_duration,
                color='red',
                linestyle='--',
                linewidth=2,
                label=f'Expected Duration ({
                    expected_duration:.1f})')

            # Highlight specific calculations
            if target_duration is not None and highlight_prob is not None:
                # Shade area for probability calculation
                x_shade = x[x <= target_duration]
                y_shade = norm.pdf(x_shade, expected_duration, std_dev)
                ax.fill_between(
                    x_shade,
                    y_shade,
                    alpha=0.6,
                    color='green',
                    label=f'P(T ≤ {target_duration}) = {
                        highlight_prob:.4f}')
                ax.axvline(
                    target_duration,
                    color='green',
                    linestyle='-',
                    linewidth=2)

            if target_probability is not None and highlight_duration is not None:
                # Mark duration for probability calculation
                ax.axvline(
                    highlight_duration,
                    color='orange',
                    linestyle='-',
                    linewidth=2,
                    label=f'Duration for P = {
                        target_probability:.3f}: {
                        highlight_duration:.2f}')

                # Shade area
                x_shade = x[x <= highlight_duration]
                y_shade = norm.pdf(x_shade, expected_duration, std_dev)
                ax.fill_between(x_shade, y_shade, alpha=0.6, color='orange')

            # Formatting
            ax.set_xlabel('Project Duration (time units)', fontsize=10)
            ax.set_ylabel('Probability Density', fontsize=10)
            ax.set_title(
                'Project Completion Time Distribution (Normal)',
                fontsize=12,
                fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)

            # Add statistics text
            stats_text = f'μ = {
                expected_duration:.2f}, σ = {
                std_dev:.3f}, σ² = {
                stats["variance"]:.3f}'
            ax.text(
                0.02,
                0.98,
                stats_text,
                transform=ax.transAxes,
                fontsize=9,
                verticalalignment='top',
                bbox=dict(
                    boxstyle='round',
                    facecolor='wheat',
                    alpha=0.8))

            self.fig_probability.tight_layout()
            self.canvas_probability.draw()

        except Exception as e:
            print(f"Error plotting probability distribution: {str(e)}")


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CPMDesktopApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
